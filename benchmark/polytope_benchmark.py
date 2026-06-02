#!/usr/bin/env python3
"""
Minimal benchmarking script for Polytope timeseries feature extraction.

Uses earthkit-data for data retrieval and queries CloudWatch Logs for
server-side timing breakdown (GribJump setup, Polytope, CovJSON phases).
"""

import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path

import boto3
import earthkit.data as ekd
import yaml
from polytope import api as polytope_api


def load_config() -> dict:
    """Load Polytope credentials from config.yml."""
    path = Path(__file__).parent / "config.yml"
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

    date, time_str = get_latest_forecast_time(model)

    if feature_type == "timeseries":
        feature = {
            "type": "timeseries",
            "points": points,
            "time_axis": "step",
            "axes": ["longitude", "latitude"],
        }
    elif feature_type == "boundingbox":
        feature = {
            "type": "boundingbox",
            "points": points,
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
        "timespan": "none"
    }

    if forecast_type == "pf":
        request["number"] = f"1/to/{num_members}"

    if (
        "levelist" in config["benchmark"]
        and config["benchmark"]["levelist"] is not None
    ):
        request["levelist"] = config["benchmark"]["levelist"]

    return request


def run_polytope_request(
    client: polytope_api.Client, collection: str, request: dict
) -> tuple[float, str | None, int]:
    """
    Execute the Polytope request and measure client-side time.

    Uses polytope client directly to get the request ID from the result filename,
    then loads data with earthkit-data for xarray conversion.

    Returns:
        Tuple of (elapsed_seconds, request_id, num_values)
    """
    print(f"running request: {request}")

    # Convert request dict to YAML string for polytope client
    request_str = yaml.dump(request)

    # Run request using polytope client directly (returns list of file paths)
    start = time.perf_counter()
    result_files = client.retrieve(collection, request_str)
    elapsed = time.perf_counter() - start

    # Extract request ID from filename (e.g., "d77b7629-6fbe-43e8-b1b8-e3cb65d42166.covjson")
    request_id = None
    if result_files:
        filename = Path(result_files[0]).stem
        # Validate it looks like a UUID (36 chars with 4 dashes)
        if len(filename) == 36 and filename.count("-") == 4:
            request_id = filename

    # Load data using earthkit-data (handles CovJSON format)
    num_vals = 0
    if result_files:
        ds = ekd.from_source("file", result_files[0]).to_xarray()
        num_vals = no_values(ds)

    # Clean up downloaded files
    for f in result_files:
        Path(f).unlink(missing_ok=True)

    return elapsed, request_id, num_vals

def no_values(ds) -> int:
    if isinstance(ds, list):
        return sum(var.size for d in ds for var in d.data_vars.values())
    return sum(var.size for var in ds.data_vars.values())


def extract_cloudwatch_timings(
    request_id: str,
    aws_profile: str,
    aws_region: str = "eu-central-2",
    log_group: str = "polytope-server-logs",
    max_wait_seconds: int = 30,
) -> dict:
    """
    Query CloudWatch Logs for polytope-server timing.

    Args:
        request_id: Request identifier (UUID) for log correlation
        aws_profile: AWS SSO profile name
        aws_region: AWS region
        log_group: CloudWatch log group name
        max_wait_seconds: Max time to wait for logs to appear

    Returns:
        Dict with keys: gribjump_setup, polytope, covjson (floats in seconds)
    """
    session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
    client = session.client("logs")

    patterns = {
        "gribjump_setup": re.compile(r"Gribjump/setup time taken: ([0-9.]+)"),
        "polytope": re.compile(r"Polytope time taken: ([0-9.]+)"),
        "covjson": re.compile(r"Covjsonkit time taken: ([0-9.]+)"),
    }
    timings = {}

    start_time = int((time.time() - 300) * 1000)  # last 5 minutes
    wait_interval = 2
    elapsed = 0

    while elapsed < max_wait_seconds:
        response = client.filter_log_events(
            logGroupName=log_group,
            startTime=start_time,
            filterPattern=f'"{request_id}"',
        )

        for event in response.get("events", []):
            message = event.get("message", "")
            try:
                log_entry = json.loads(message)
                body = log_entry.get("body", "")
            except (json.JSONDecodeError, TypeError):
                body = message

            for key, pattern in patterns.items():
                if key not in timings:
                    match = pattern.search(body)
                    if match:
                        timings[key] = float(match.group(1))

        if len(timings) == len(patterns):
            return timings

        time.sleep(wait_interval)
        elapsed += wait_interval

    if not timings:
        print(f"  Warning: No CloudWatch logs found for request {request_id}")

    return timings


def run(config: dict) -> dict:
    """
    Run the Polytope benchmark with the given config.

    Returns:
        Dictionary with results: client_time, request_id, num_fields, server_timings
    """
    setup_polytope_env(config)
    client = polytope_api.Client(quiet=True)

    request = build_request(config)
    client_time, request_id, no_values = run_polytope_request(
        client, config["benchmark"]["collection"], request
    )

    server_timings = {}
    aws_profile = config["benchmark"].get("aws_profile")
    if aws_profile and request_id:
        server_timings = extract_cloudwatch_timings(
            request_id,
            aws_profile=aws_profile,
            aws_region=config["benchmark"].get("aws_region", "eu-central-2"),
        )

    return {
        "request": request,
        "client_time": client_time,
        "request_id": request_id,
        "no_values": no_values,
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
  Output size: {result["no_values"]} data points""")

    if result["server_timings"]:
        st = result["server_timings"]
        print(f"  GribJump setup: {st.get('gribjump_setup', 0):.2f}s")
        print(f"  Polytope:       {st.get('polytope', 0):.2f}s")
        print(f"  CovJSON:        {st.get('covjson', 0):.2f}s")


if __name__ == "__main__":
    main()
