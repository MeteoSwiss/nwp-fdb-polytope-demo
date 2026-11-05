#!/usr/bin/env python3
"""Validate the example notebooks in CI.

Wraps run_notebooks.py: checks the Vault-injected credentials are present, runs
every notebook without writing results back, and records a build outcome
(SUCCESS / UNSTABLE / FAILURE) that the Jenkinsfile reads from validation_status.txt.
"""
import logging
import os
import sys
from pathlib import Path

import yaml

from run_notebooks import (
    CAT_DATA_UNAVAILABLE,
    POLYTOPE_DIR,
    ROOT_DIR,
    NotebookResult,
    configure_logging,
    log_summary,
    run_all,
)

logger = logging.getLogger(__name__)

# Overall build outcomes. UNSTABLE means the only failures were environmental
# (forecast not yet in FDB) — an orange pipeline, not a red one.
STATUS_SUCCESS = "SUCCESS"
STATUS_UNSTABLE = "UNSTABLE"
STATUS_FAILURE = "FAILURE"

# Local exit codes. Jenkins ignores these (mchbuild collapses every non-zero
# exit to 1); it reads STATUS_FILE instead. They still make local runs legible.
EXIT_CODE = {STATUS_SUCCESS: 0, STATUS_FAILURE: 1, STATUS_UNSTABLE: 2}

# Written to the workspace root so the Jenkinsfile can map the run onto
# SUCCESS / UNSTABLE / FAILURE regardless of the mchbuild exit code.
STATUS_FILE = ROOT_DIR / "validation_status.txt"

# Env vars the notebooks need, injected from Vault by the pipeline. The ECMWF
# credentials let feature_time_series.ipynb reach the IFS data on polytope.ecmwf.int.
REQUIRED_ENV = ["POLYTOPE_USER_KEY", "POLYTOPE_ADDRESS", "ECMWF_USER_EMAIL", "ECMWF_KEY"]


def create_config_file(config_path: Path) -> None:
    """Create config.yml from environment variables."""
    config = {
        "meteoswiss": {
            "key": os.environ.get("POLYTOPE_USER_KEY", ""),
            "address": os.environ.get("POLYTOPE_ADDRESS", ""),
        },
        "ecmwf": {
            "user_email": os.environ.get("ECMWF_USER_EMAIL", ""),
            "key": os.environ.get("ECMWF_KEY", ""),
        },
    }
    with open(config_path, "w") as f:
        yaml.dump(config, f)


def report_status(failed: list[NotebookResult]) -> int:
    """Decide the overall outcome, persist it for Jenkins, and return an exit code."""
    hard = [r for r in failed if r.category != CAT_DATA_UNAVAILABLE]

    if hard:
        status = STATUS_FAILURE
    elif failed:
        status = STATUS_UNSTABLE
    else:
        status = STATUS_SUCCESS

    STATUS_FILE.write_text(status + "\n")

    if status == STATUS_UNSTABLE:
        logger.warning(
            "Only data-availability failures (forecast not yet in FDB); "
            "marking build UNSTABLE rather than FAILURE"
        )
    return EXIT_CODE[status]


def main() -> int:
    configure_logging()

    missing = [var for var in REQUIRED_ENV if not os.environ.get(var)]
    if missing:
        logger.error("Missing required env var(s): %s", ", ".join(missing))
        return 1

    # The notebooks read config.yml from their own directory. Create it only if
    # missing (and remove only what we created) so a local config.yml is kept.
    config_path = POLYTOPE_DIR / "config.yml"
    do_create_config = not config_path.exists()
    if do_create_config:
        create_config_file(config_path)

    try:
        results = run_all(write_back=False)
    finally:
        if do_create_config:
            config_path.unlink(missing_ok=True)

    failed = [r for r in results if not r.passed]
    log_summary(results, failed)
    return report_status(failed)


if __name__ == "__main__":
    sys.exit(main())
