#!/usr/bin/env python3
"""Notebook validation script for CI."""
import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import nbformat
import yaml
from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor

logger = logging.getLogger(__name__)

KERNEL_NAME = "polytope-env"
ROOT_DIR = Path(__file__).resolve().parent.parent
POLYTOPE_DIR = ROOT_DIR / "examples" / "Polytope"

# Failure categories. DATA_UNAVAILABLE is environmental (forecast not yet in FDB)
# and typically warrants a retry rather than a code fix; the others point at a
# real regression.
CAT_DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
CAT_AUTH = "AUTH"
CAT_NOTEBOOK_ERROR = "NOTEBOOK_ERROR"

# Matches ANSI colour escapes (e.g. "\x1b[31m") that Jupyter embeds in tracebacks.
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
# Captures the two counts from gribjump's "Matched 0 fields but 121 were requested".
FIELDS_RE = re.compile(r"Matched (\d+) fields but (\d+) were requested")

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


@dataclass
class NotebookResult:
    name: str
    passed: bool
    category: str = ""  # only set on failure
    detail: str = ""    # concise, human-readable cause


def strip_ansi(text: str) -> str:
    """Remove ANSI colour escapes that Jupyter embeds in captured tracebacks."""
    return ANSI_RE.sub("", text)


def classify_failure(ename: str, evalue: str) -> str:
    """Bucket a cell error so a red build tells us whether to retry or investigate."""
    text = evalue.lower()
    if "datanotfound" in text or "no data retrieved" in text:
        return CAT_DATA_UNAVAILABLE
    if "expiredcredentials" in ename.lower() or "expired" in text or "unauthorized" in text:
        return CAT_AUTH
    return CAT_NOTEBOOK_ERROR


def summarize_error(evalue: str) -> str:
    """Extract the one line worth reading from a (possibly huge) error value.

    Assumes the caller has already run the value through strip_ansi.
    """
    text = evalue.strip()
    m = FIELDS_RE.search(text)
    if m:
        return f"{m.group(1)}/{m.group(2)} fields matched"
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines:
        if "Error in function" in ln or "GribJumpException" in ln or "No data retrieved" in ln:
            return ln
    return lines[-1] if lines else text


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


def run_notebook(notebook_path: Path) -> NotebookResult:
    """Execute a notebook and return a classified result."""
    name = notebook_path.name
    logger.info(f"Running: {name}")

    with open(notebook_path) as f:
        # Read as nbformat v4 (the current schema) whatever version is on disk.
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=600, kernel_name=KERNEL_NAME)
    try:
        # Run in the notebook's own directory so its relative reads (config.yml) work.
        ep.preprocess(nb, {"metadata": {"path": notebook_path.parent}})
        logger.info(f"PASS: {name}")
        return NotebookResult(name, passed=True)
    except CellExecutionError as e:
        # ename is the error's class name (e.g. "HTTPResponseError"),
        # evalue its message text.
        ename = strip_ansi(getattr(e, "ename", ""))
        evalue = strip_ansi(getattr(e, "evalue", "") or str(e))
        category = classify_failure(ename, evalue)
        detail = summarize_error(evalue)
        # One actionable line at INFO/ERROR; the full traceback only when debugging.
        logger.error("FAIL: %s — %s: %s — %s", name, category, ename or "error", detail)
        logger.debug("Full traceback for %s", name, exc_info=True)
        return NotebookResult(name, passed=False, category=category, detail=detail)


def main() -> int:
    # Set LOG_LEVEL=DEBUG to also print full tracebacks for failed notebooks.
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s")

    missing = [var for var in REQUIRED_ENV if not os.environ.get(var)]
    if missing:
        logger.error("Missing required env var(s): %s", ", ".join(missing))
        return 1

    notebooks = sorted(POLYTOPE_DIR.glob("*.ipynb"))
    logger.info(f"Found {len(notebooks)} notebooks")

    # The notebooks read config.yml from their own directory. Create it only if
    # missing (and remove only what we created) so a local config.yml is kept.
    config_path = POLYTOPE_DIR / "config.yml"
    do_create_config = not config_path.exists()
    if do_create_config:
        create_config_file(config_path)

    try:
        results = [run_notebook(nb) for nb in notebooks]
    finally:
        if do_create_config:
            config_path.unlink(missing_ok=True)

    failed = [r for r in results if not r.passed]
    log_summary(results, failed)
    return report_status(failed)


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


def log_summary(results: list[NotebookResult], failed: list[NotebookResult]) -> None:
    """Emit a one-glance table keyed by failure cause."""
    name_width = max((len(r.name) for r in results), default=0)

    logger.info("=== Notebook validation summary ===")
    for r in results:
        if r.passed:
            logger.info("%s  PASS", r.name.ljust(name_width))
        else:
            logger.error("%s  FAIL  %-16s  %s", r.name.ljust(name_width), r.category, r.detail)

    tally = f"{len(failed)} failed, {len(results) - len(failed)} passed"
    categories = {r.category for r in failed}
    if len(categories) == 1:
        # All failures share a cause — call it out so triage is instant.
        tally += f" — all {next(iter(categories))}"
    (logger.error if failed else logger.info)(tally)


if __name__ == "__main__":
    sys.exit(main())
