#!/usr/bin/env python3
"""
Minimal benchmarking script for Polytope timeseries feature extraction.

Uses the polytope client directly (instead of earthkit-data) to access
request IDs for correlating client-side timings with gribjump-server logs.
"""

import json
import logging
import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import cartopy.crs as ccrs
import yaml
from polytope import api as polytope_api


# =============================================================================
# BENCHMARK CONFIGURATION
# Modify these values to change what is being measured
# =============================================================================

# Polytope collection
COLLECTION = "mchgj"  # "mchgj" for feature extraction, "mch" for full field

# Request parameters
PARAM = 500011  # Parameter (e.g., T_2M, U_10M, V_10M, TOT_PREC)
MODEL = "ICON_CH2_EPS"  # ICON_CH1_EPS or ICON_CH2_EPS
LEVTYPE = "sfc"  # sfc, ml (model level), pl (pressure level)
FORECAST_TYPE = "pf"  # "pf" (perturbed/ensemble) or "cf" (control)

# Point location (WGS84 coordinates)
POINT_LON = 8.565074  # Zurich Airport longitude
POINT_LAT = 47.453928  # Zurich Airport latitude

# Timeseries range
STEP_START = 0  # First forecast step
STEP_END = 120  # Last forecast step (120 for CH2, 33 for CH1)

# Ensemble members (ignored if FORECAST_TYPE == "cf")
NUM_MEMBERS = 20  # 20 for CH2, 10 for CH1

# Gribjump server log file path (local)
GRIBJUMP_LOG_PATH = "/oprusers/trajond/gribjump-server/logs/log.out"  # e.g., "/var/log/gribjump/server.log"

# Timing metrics to extract from gribjump logs
TIMING_KEYS = [
    "run_time",
    "elapsed_build_filemap",
    "elapsed_tasks",
    "elapsed_execute",
    "elapsed_reply",
    "elapsed_receive",
    "count_tasks",
]

# =============================================================================


def load_config() -> dict:
    """Load Polytope credentials from config.yml."""
    path = Path("config.yml")
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Create one based on config_example.yml"
        )
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_polytope_env(config: dict) -> None:
    """Set environment variables for MeteoSwiss Polytope access."""
    # ICON-CSCS Polytope credentials
    os.environ["POLYTOPE_USERNAME"] = config["meteoswiss"]["user"]
    os.environ["POLYTOPE_PASSWORD"] = config["meteoswiss"]["password"]
    os.environ["POLYTOPE_ADDRESS"] = config["meteoswiss"]["endpoint"]


def get_latest_forecast_time() -> tuple[str, str]:
    """Get a valid forecast date/time (FDB holds only the latest day)."""
    now = datetime.now()
    past_time = now - timedelta(hours=12)
    # ICON-CH2-EPS runs every 6 hours, ICON-CH1-EPS every 3 hours
    cycle_hours = 6 if MODEL == "ICON_CH2_EPS" else 3
    rounded_hour = (past_time.hour // cycle_hours) * cycle_hours
    rounded_time = past_time.replace(
        hour=rounded_hour, minute=0, second=0, microsecond=0
    )
    return rounded_time.strftime("%Y%m%d"), rounded_time.strftime("%H%M")


def rotate_point(lon: float, lat: float) -> tuple[float, float]:
    """
    Transform WGS84 coordinates to MeteoSwiss rotated grid.

    The data source accessed by Polytope is stored on a rotated grid.
    It is necessary to provide Polytope with coordinates in rotated form,
    using a South Pole rotation with a reference of longitude 10° and
    latitude -43°.
    """
    geo_crs = ccrs.PlateCarree()
    rotated_crs = ccrs.RotatedPole(pole_longitude=190, pole_latitude=43)
    rot_lon, rot_lat = rotated_crs.transform_point(lon, lat, geo_crs)
    # polytope serializes the request to YAML, which can't handle np.float
    return float(rot_lon), float(rot_lat)


def build_request(date: str, time_str: str, rotated_point: tuple[float, float]) -> dict:
    """Build a Polytope request dict for timeseries feature extraction."""
    feature = {
        "type": "timeseries",
        "points": [list(rotated_point)],
        "time_axis": "step",
        "range": {"start": STEP_START, "end": STEP_END},
        "axes": ["longitude", "latitude"],
    }

    request = {
        "class": "od",
        "stream": "enfo",
        "expver": "0001",
        "type": FORECAST_TYPE,
        "date": date,
        "time": time_str,
        "param": PARAM,
        "levtype": LEVTYPE,
        "model": MODEL.lower().replace("_", "-"),
        "feature": feature,
    }

    if FORECAST_TYPE == "pf":
        request["number"] = f"1/to/{NUM_MEMBERS}"

    return request


def get_request_ids(client: polytope_api.Client, collection: str) -> set:
    """Get current request IDs for the collection."""
    try:
        requests = client.list_requests(collection)
        return set(requests) if requests else set()
    except (OSError, ValueError, RuntimeError):
        return set()


def run_polytope_request(
    client: polytope_api.Client, request: dict
) -> tuple[float, str | None, Path]:
    """
    Execute the Polytope request and measure client-side time.

    Returns:
        Tuple of (elapsed_seconds, request_id, output_path)
    """
    # Get request IDs before
    before_ids = get_request_ids(client, COLLECTION)

    # Create temp file for output
    output_file = Path(tempfile.mktemp(suffix=".grib"))

    # Run request
    start = time.perf_counter()
    client.retrieve(
        COLLECTION,
        request,
        output_file=str(output_file),
        pointer=False,
        asynchronous=False,
    )
    elapsed = time.perf_counter() - start

    # Get request IDs after
    after_ids = get_request_ids(client, COLLECTION)
    new_ids = after_ids - before_ids
    request_id = new_ids.pop() if new_ids else None

    return elapsed, request_id, output_file


def extract_gribjump_timings(request_id: str | None = None) -> dict:
    """
    Extract timing information from gribjump-server logs.

    Parses JSON log lines to find entries matching the request ID.

    Args:
        request_id: Request identifier (UUID) for log correlation

    Returns:
        Dictionary with timing metrics
    """
    if GRIBJUMP_LOG_PATH is None:
        return {}

    if request_id is None:
        print("  Warning: No request ID available for log correlation")
        return {}

    log_path = Path(GRIBJUMP_LOG_PATH)
    if not log_path.exists():
        print(f"  Warning: Log file not found: {log_path}")
        return {}

    # Read file and parse JSON lines in reverse (most recent first)
    with open(log_path, encoding="utf-8") as f:
        lines = f.readlines()

    for line in reversed(lines):
        line = line.strip()
        if not line.startswith("{"):
            continue

        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Check if this entry matches our request
        context_str = entry.get("context", "{}")
        try:
            context = json.loads(context_str)
        except json.JSONDecodeError:
            context = {}

        if context.get("id") == request_id:
            return {key: entry.get(key) for key in TIMING_KEYS}

    print(f"  Warning: No log entry found for request ID {request_id}")
    return {}


def main():
    """Run the Polytope benchmark and print results."""
    setup_polytope_env(load_config())
    client = polytope_api.Client(quiet=True) # Suppress client logs for cleaner output

    rotated_point = rotate_point(POINT_LON, POINT_LAT)
    date, time_str = get_latest_forecast_time()

    members_info = f"\n  Members: 1-{NUM_MEMBERS}" if FORECAST_TYPE == "pf" else ""
    print(f"""Benchmark Configuration:
  Collection: {COLLECTION}
  Model: {MODEL}
  Param: {PARAM}
  Level type: {LEVTYPE}
  Forecast type: {FORECAST_TYPE}
  Date/Time: {date} {time_str}
  Point: ({POINT_LON}, {POINT_LAT}) -> ({rotated_point[0]:.4f}, {rotated_point[1]:.4f})
  Steps: {STEP_START}-{STEP_END}{members_info}
""")

    request = build_request(date, time_str, rotated_point)

    print("Running Polytope request...")
    client_time, request_id, output_path = run_polytope_request(client, request)

    output_size = output_path.stat().st_size / 1024
    print(f"""
Results:
  Client-side time: {client_time:.2f}s
  Request ID: {request_id}
  Output file: {output_path}
  Output size: {output_size:.1f} KB""")

    server_timings = extract_gribjump_timings(request_id)
    if server_timings:
        print(f"  Server timings: {server_timings}")

    output_path.unlink(missing_ok=True)
    print(f"\nCleaned up temp file {output_path}")


if __name__ == "__main__":
    main()
