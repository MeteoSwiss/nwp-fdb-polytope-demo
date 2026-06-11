#!/usr/bin/env python3
"""
Minimal benchmarking script for Polytope timeseries feature extraction.

Uses earthkit-data for data retrieval and queries CloudWatch Logs for
server-side timing breakdown (GribJump setup, Polytope, CovJSON phases).
"""

import gc
import json
import os
import re
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import boto3
import earthkit.data as ekd
import yaml


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
        "timespan": "none",
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
    collection: str, request: dict
) -> tuple[float, str | None, int]:
    """
    Execute the Polytope request and measure client-side time.

    Uses polytope client directly to get the request ID from the result filename,
    then loads data with earthkit-data for xarray conversion.

    Returns:
        Tuple of (elapsed_seconds, request_id, num_values)
    """
    ekd.settings.set("cache-policy", "off")
    _, log_file = tempfile.mkstemp(suffix=".log")

    # Run request using earthkit-data
    start = time.perf_counter()
    ds = ekd.from_source(
        "polytope",
        collection,
        request,
        stream=False,
        log_file=log_file,
        log_level="INFO",
        # quiet=True
    ).to_xarray()
    elapsed = time.perf_counter() - start

    def find_first_poll_id(file_path):
        """Return the captured ID from the first matching line, or None."""
        pattern = re.compile(r"Please poll .*/([a-f0-9-]+) for status")
        with open(file_path) as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    return match.group(1)
        return None

    request_id = find_first_poll_id(log_file)

    values = no_values(ds)

    # Cleanup
    del ds
    gc.collect()

    return elapsed, request_id, values


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
    filter_pattern = f'"{request_id}"'

    while elapsed < max_wait_seconds:
        # Paginate through results (CloudWatch may return empty pages)
        events = []
        next_token = None
        for _ in range(20):  # max pages per retry
            kwargs = {
                "logGroupName": log_group,
                "startTime": start_time,
                "filterPattern": filter_pattern,
            }
            if next_token:
                kwargs["nextToken"] = next_token

            response = client.filter_log_events(**kwargs)
            events.extend(response.get("events", []))
            next_token = response.get("nextToken")

            if not next_token or events:
                break

        for event in events:
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


def trace_request(
    request_id: str,
    aws_profile: str,
    aws_region: str = "eu-central-2",
    log_group: str = "polytope-server-logs",
) -> None:
    """
    Print detailed timeline for a request, similar to trace_request.sh.

    Args:
        request_id: Request identifier (UUID) for log correlation
        aws_profile: AWS SSO profile name
        aws_region: AWS region
        log_group: CloudWatch log group name
    """
    from datetime import datetime as dt

    session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
    client = session.client("logs")

    start_time = int((time.time() - 86400) * 1000)  # last 24 hours
    filter_pattern = f'"{request_id}"'

    # Paginate through results (CloudWatch may return empty pages before finding matches)
    events = []
    next_token = None
    max_pages = 50

    for _ in range(max_pages):
        kwargs = {
            "logGroupName": log_group,
            "startTime": start_time,
            "filterPattern": filter_pattern,
        }
        if next_token:
            kwargs["nextToken"] = next_token

        response = client.filter_log_events(**kwargs)
        events.extend(response.get("events", []))
        next_token = response.get("nextToken")

        if not next_token or events:
            break
    if not events:
        print(f"No logs found for request {request_id}")
        return

    # Header
    print(f"\n=== REQUEST LIFECYCLE FOR {request_id} ===\n")
    print(f"{'TIME':<15} | {'SERVICE':<10} | {'TRACE_ID':<14} | MESSAGE")
    print("-" * 15 + "-+-" + "-" * 10 + "-+-" + "-" * 14 + "-+-" + "-" * 40)

    # Parse and display events
    timings = {}
    patterns = {
        "gribjump_setup": re.compile(r"Gribjump/setup time taken: ([0-9.]+)"),
        "polytope": re.compile(r"Polytope time taken: ([0-9.]+)"),
        "covjson": re.compile(r"Covjsonkit time taken: ([0-9.]+)"),
    }

    for event in sorted(events, key=lambda e: e["timestamp"]):
        ts = event["timestamp"]
        msg = event.get("message", "")
        time_str = dt.fromtimestamp(ts / 1000).strftime("%H:%M:%S.%f")[:-3]

        try:
            log_entry = json.loads(msg)
            service = log_entry.get("resource", {}).get("service.name", "unknown")
            body = log_entry.get("body", "")
            trace_id = log_entry.get("trace_id", "null")
        except (json.JSONDecodeError, TypeError):
            service = "unknown"
            body = msg
            trace_id = "null"

        # Truncate body for display
        body_display = body[:60] + "..." if len(body) > 60 else body
        print(f"{time_str:<15} | {service:<10} | {trace_id[:12]:<14} | {body_display}")

        # Extract timings
        for key, pattern in patterns.items():
            if key not in timings:
                match = pattern.search(body)
                if match:
                    timings[key] = float(match.group(1))

    # Print timing summary
    if timings:
        print("\n=== TIMING BREAKDOWN ===")
        if "gribjump_setup" in timings:
            print(f"GribJump setup: {timings['gribjump_setup']:.2f}s")
        if "polytope" in timings:
            print(f"Polytope:       {timings['polytope']:.2f}s")
        if "covjson" in timings:
            print(f"CovJSON:        {timings['covjson']:.2f}s")


def run(config: dict) -> dict:
    """
    Run the Polytope benchmark with the given config.

    Returns:
        Dictionary with results: client_time, request_id, num_fields, server_timings
    """
    setup_polytope_env(config)

    request = build_request(config)
    client_time, request_id, no_values = run_polytope_request(
        config["benchmark"]["collection"], request
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
    import argparse

    parser = argparse.ArgumentParser(description="Polytope benchmark and request tracing")
    parser.add_argument(
        "--trace",
        metavar="REQUEST_ID",
        help="Trace a specific request ID (show detailed CloudWatch timeline)",
    )
    args = parser.parse_args()

    config = load_config()

    if args.trace:
        aws_profile = config["benchmark"].get("aws_profile")
        if not aws_profile:
            print("Error: aws_profile must be set in config.yml to trace requests")
            return
        trace_request(
            args.trace,
            aws_profile=aws_profile,
            aws_region=config["benchmark"].get("aws_region", "eu-central-2"),
        )
        return

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
