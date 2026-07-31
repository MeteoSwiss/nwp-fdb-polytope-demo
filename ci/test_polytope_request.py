import multiprocessing
import os
import sys
import time

import requests


REQUEST = {
    "param": "500011",
    "date": "20260731",
    "time": "0000",
    "expver": "0001",
    "step": 0,
    "class": "od",
    "levtype": "sfc",
    "model": "icon-ch1-eps",
    "stream": "enfo",
    "type": "cf",
    "feature": {
        "type": "boundingbox",
        "points": [[5.8, 47.81], [10.5, 45.81]],
        "axes": ["longitude", "latitude"],
    },
    "timespan": "none",
}


def run_polytope_request() -> None:
    import earthkit.data as ekd

    started = time.monotonic()

    print("Calling ekd.from_source(...)", flush=True)

    source = ekd.from_source(
        "polytope",
        "mchgj",
        REQUEST,
        stream=False,
    )

    print(
        f"from_source completed after "
        f"{time.monotonic() - started:.1f}s",
        flush=True,
    )

    dataset = source.to_xarray()

    print(
        f"to_xarray completed after "
        f"{time.monotonic() - started:.1f}s",
        flush=True,
    )
    print(dataset, flush=True)


def main() -> int:
    address = os.environ["POLYTOPE_ADDRESS"].rstrip("/")

    print(f"Polytope address: {address}", flush=True)
    print(f"Request: {REQUEST}", flush=True)

    health_url = f"{address}/api/v1/test"
    print(f"Testing health endpoint: {health_url}", flush=True)

    try:
        started = time.monotonic()
        response = requests.get(
            health_url,
            timeout=(5, 20),
            allow_redirects=False,
        )

        print(
            f"Health response: status={response.status_code}, "
            f"time={time.monotonic() - started:.1f}s, "
            f"body={response.text[:300]!r}",
            flush=True,
        )
        response.raise_for_status()

    except Exception as exc:
        print(
            f"Health check failed: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )
        return 1

    process = multiprocessing.Process(
        target=run_polytope_request,
    )
    process.start()

    request_timeout = 600
    process.join(timeout=request_timeout)

    if process.is_alive():
        print(
            f"ERROR: Polytope request still running after "
            f"{request_timeout} seconds.",
            flush=True,
        )
        process.terminate()
        process.join(timeout=10)
        return 2

    if process.exitcode != 0:
        print(
            f"ERROR: Request process exited with code "
            f"{process.exitcode}.",
            flush=True,
        )
        return 3

    print("Polytope request completed successfully.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())