#!/usr/bin/env python3
"""
Minimal benchmarking script for Polytope timeseries feature extraction.

Uses earthkit-data for data retrieval and the polytope client to access
request IDs for correlating client-side timings with gribjump-server logs.
"""

import json
import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import cartopy.crs as ccrs
import earthkit.data as ekd
import yaml
from polytope import api as polytope_api

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
    os.environ["POLYTOPE_USERNAME"] = config["access"]["user"]
    os.environ["POLYTOPE_PASSWORD"] = config["access"]["password"]
    os.environ["POLYTOPE_ADDRESS"] = config["access"]["endpoint"]


def get_latest_forecast_time(
    model: str,
) -> tuple[str, str]:
    """Get a valid forecast date/time (FDB holds only the latest day)."""
    now = datetime.now()
    past_time = now - timedelta(hours=12)
    # ICON-CH2-EPS runs every 6 hours, ICON-CH1-EPS every 3 hours
    cycle_hours = 6 if model == "ICON_CH2_EPS" else 3
    rounded_hour = (past_time.hour // cycle_hours) * cycle_hours
    rounded_time = past_time.replace(
        hour=rounded_hour, minute=0, second=0, microsecond=0
    )
    return rounded_time.strftime("%Y%m%d"), rounded_time.strftime("%H%M")


def rotate_points(latlon: list[tuple[float, float]]) -> list[list[float]]:
    """
    Transform WGS84 coordinates to MeteoSwiss rotated grid.

    The data source accessed by Polytope is stored on a rotated grid.
    It is necessary to provide Polytope with coordinates in rotated form,
    using a South Pole rotation with a reference of longitude 10° and
    latitude -43°.
    """
    geo_crs = ccrs.PlateCarree()
    rotated_crs = ccrs.RotatedPole(pole_longitude=190, pole_latitude=43)
    rotated_points = [
        rotated_crs.transform_point(lon, lat, geo_crs) for lon, lat in latlon
    ]
    # polytope serializes the request to YAML, which can't handle np.float
    return [[float(rot_lon), float(rot_lat)] for rot_lon, rot_lat in rotated_points]


def build_request(
    config: dict,
) -> dict:
    """Build a Polytope request dict for feature extraction."""

    points = config["benchmark"]["feature"]["points"]
    feature_type = config["benchmark"]["feature"]["type"]
    model = config["benchmark"]["model"]
    forecast_type = config["benchmark"]["forecast_type"]
    steps = config["benchmark"]["feature"]["range"]
    num_members = config["benchmark"]["num_members"]
    parameter = config["benchmark"]["param"]
    levtype = config["benchmark"]["levtype"]

    rotated_points = rotate_points(points)
    date, time_str = get_latest_forecast_time(model)

    if feature_type == "timeseries":
        feature = {
            "type": "timeseries",
            "points": rotated_points,
            "time_axis": "step",
            "axes": ["longitude", "latitude"],
        }
    elif feature_type == "boundingbox":
        feature = {
            "type": "boundingbox",
            "points": rotated_points,
            "axes": ["longitude", "latitude"],
        }
    else:
        raise ValueError(f"Unsupported feature type: {feature_type}")

    request = {
        "class": "od",
        "stream": "enfo",
        "expver": "0001",
        "type": forecast_type,
        "date": date,
        "time": time_str,
        "param": parameter,
        "levtype": levtype,
        "model": model.lower().replace("_", "-"),
        "step": f"{steps[0]}/to/{steps[1]}",
        "feature": feature,
    }

    if forecast_type == "pf":
        request["number"] = f"1/to/{num_members}"

    if (
        "levelist" in config["benchmark"]
        and config["benchmark"]["levelist"] is not None
    ):
        request["levelist"] = config["benchmark"]["levelist"]

    return request


def get_request_ids(client: polytope_api.Client, collection: str) -> set:
    """Get current request IDs for the collection."""
    try:
        requests = client.list_requests(collection)
        return set(requests) if requests else set()
    except (OSError, ValueError, RuntimeError):
        return set()


def run_polytope_request(
    client: polytope_api.Client, collection: str, request: dict
) -> tuple[float, str | None, ekd.FieldList]:
    """
    Execute the Polytope request using earthkit-data and measure client-side time.

    Returns:
        Tuple of (elapsed_seconds, request_id, earthkit_data)
    """
    # Get request IDs before
    before_ids = get_request_ids(client, collection)

    # Run request using earthkit-data
    start = time.perf_counter()
    data = ekd.from_source(
        "polytope",
        collection,
        request,
        stream=False,
    )
    elapsed = time.perf_counter() - start

    # Get request IDs after
    after_ids = get_request_ids(client, collection)
    new_ids = after_ids - before_ids
    request_id = new_ids.pop() if new_ids else None

    return elapsed, request_id, data


def extract_gribjump_timings(
    gribjump_log_path: str, request_id: str | None = None
) -> dict:
    """
    Extract timing information from gribjump-server logs.

    Parses JSON log lines to find entries matching the request ID.

    Args:
        request_id: Request identifier (UUID) for log correlation

    Returns:
        Dictionary with timing metrics
    """

    if request_id is None:
        print("  Warning: No request ID available for log correlation")
        return {}

    log_path = Path(gribjump_log_path)
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


def run(config: dict) -> dict:
    """
    Run the Polytope benchmark with the given config.

    Returns:
        Dictionary with results: client_time, request_id, num_fields, server_timings
    """
    setup_polytope_env(config)
    client = polytope_api.Client(quiet=True)

    request = build_request(config)
    client_time, request_id, data = run_polytope_request(
        client, config["benchmark"]["collection"], request
    )

    num_fields = len(data)

    # Save to temp file to get output size
    with tempfile.NamedTemporaryFile(suffix=".grib", delete=False) as f:
        temp_path = Path(f.name)
    data.save(temp_path)
    output_size_kb = temp_path.stat().st_size / 1024
    temp_path.unlink()

    server_timings = {}
    log_path = config["benchmark"].get("gribjump_log_path")
    if log_path:
        server_timings = extract_gribjump_timings(log_path, request_id)

    return {
        "request": request,
        "client_time": client_time,
        "request_id": request_id,
        "num_fields": num_fields,
        "output_size_kb": output_size_kb,
        "server_timings": server_timings,
    }


def main():
    """Run the Polytope benchmark and print results."""
    config = load_config()
    result = run(config)

    print("Request:")
    print(result["request"])
    print(f"""
Results:
  Client-side time: {result["client_time"]:.2f}s
  Request ID: {result["request_id"]}
  Number of fields: {result["num_fields"]}
  Output size: {result["output_size_kb"]:.1f} KB""")

    if result["server_timings"]:
        print(f"  Server timings: {result['server_timings']}")


if __name__ == "__main__":
    main()
