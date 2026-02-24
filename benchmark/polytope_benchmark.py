#!/usr/bin/env python3
"""
Minimal benchmarking script for Polytope timeseries feature extraction.
Uses the polytope client directly to capture request IDs.
"""

import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from polytope import api as polytope_api
from pyproj import CRS, Transformer


# =============================================================================
# BENCHMARK CONFIGURATION
# Modify these values to change what is being measured
# =============================================================================

# Polytope collection
COLLECTION = "mchgj"  # "mchgj" for feature extraction, "mch" for full field

# Request parameters
PARAM = "T_2M"  # Parameter (e.g., T_2M, U_10M, V_10M, TOT_PREC)
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

# =============================================================================


def load_config(path: Path = None) -> dict:
    """Load Polytope credentials from config.yml."""
    if path is None:
        path = Path(__file__).parent.parent / "examples" / "Polytope" / "config.yml"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Create one based on config_example.yml"
        )
    with open(path) as f:
        return yaml.safe_load(f)


def setup_polytope_env(config: dict) -> None:
    """Set environment variables for MeteoSwiss Polytope access."""
    # HTTP proxy for outbound connections (MeteoSwiss lab network)
    if "HTTP_PROXY" not in os.environ:
        os.environ["HTTP_PROXY"] = "http://127.0.0.1:8874"
    if "HTTPS_PROXY" not in os.environ:
        os.environ["HTTPS_PROXY"] = "http://127.0.0.1:8874"

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
    """Transform WGS84 coordinates to MeteoSwiss rotated grid."""
    # Rotated pole: lon=190, lat=43 (equivalent to south pole at lon=10, lat=-43)
    wgs84 = CRS.from_epsg(4326)
    rotated = CRS.from_proj4(
        "+proj=ob_tran +o_proj=longlat +o_lon_p=0 +o_lat_p=43 +lon_0=10 +datum=WGS84"
    )
    transformer = Transformer.from_crs(wgs84, rotated, always_xy=True)
    return transformer.transform(lon, lat)


def build_request(date: str, time: str, rotated_point: tuple[float, float]) -> dict:
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
        "time": time,
        "param": PARAM,
        "levtype": LEVTYPE,
        "model": MODEL.lower().replace("_", "-"),
        "feature": feature,
    }

    if FORECAST_TYPE == "pf":
        request["number"] = "/".join(str(m) for m in range(1, NUM_MEMBERS + 1))

    return request


def get_request_ids(client: polytope_api.Client, collection: str) -> set:
    """Get current request IDs for the collection."""
    try:
        requests = client.list_requests(collection)
        return set(requests) if requests else set()
    except Exception:
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

    TODO: Implement log parsing to extract server-side timings.
    This requires access to gribjump-server logs at CSCS.

    Expected metrics from JSON log line:
    - run_time: total server-side time
    - elapsed_build_filemap: time to build file map
    - elapsed_tasks: time for extraction tasks
    - elapsed_execute: total execution time
    - elapsed_reply: time to send response

    Args:
        request_id: Request identifier for log correlation

    Returns:
        Dictionary with timing metrics
    """
    # TODO: Implement gribjump-server log extraction
    return {}


def main():
    # Setup
    config = load_config()
    setup_polytope_env(config)

    # Create client
    client = polytope_api.Client()

    # Prepare request
    rotated_point = rotate_point(POINT_LON, POINT_LAT)
    date, time_str = get_latest_forecast_time()

    print("Benchmark Configuration:")
    print(f"  Collection: {COLLECTION}")
    print(f"  Model: {MODEL}")
    print(f"  Param: {PARAM}")
    print(f"  Level type: {LEVTYPE}")
    print(f"  Forecast type: {FORECAST_TYPE}")
    print(f"  Date/Time: {date} {time_str}")
    print(
        f"  Point: ({POINT_LON}, {POINT_LAT}) -> ({rotated_point[0]:.4f}, {rotated_point[1]:.4f})"
    )
    print(f"  Steps: {STEP_START}-{STEP_END}")
    if FORECAST_TYPE == "pf":
        print(f"  Members: 1-{NUM_MEMBERS}")
    print()

    # Build and run request
    request = build_request(date, time_str, rotated_point)

    print("Running Polytope request...")
    client_time, request_id, output_path = run_polytope_request(client, request)

    print()
    print("Results:")
    print(f"  Client-side time: {client_time:.2f}s")
    print(f"  Request ID: {request_id}")
    print(f"  Output file: {output_path}")
    print(f"  Output size: {output_path.stat().st_size / 1024:.1f} KB")

    # Server-side timings (placeholder)
    server_timings = extract_gribjump_timings(request_id)
    if server_timings:
        print(f"  Server timings: {server_timings}")

    # Cleanup
    if output_path.exists():
        output_path.unlink()
        print()
        print("  (Cleaned up temp file)")


if __name__ == "__main__":
    main()
