#!/usr/bin/env python3
"""Execute the example notebooks.

Run this directly to execute every notebook locally and write the fresh outputs
back in place — e.g. to refresh them before making HTML snapshots:

    python ci/run_notebooks.py && ./make_snapshots.sh -s

It needs no arguments and uses your existing examples/Polytope/config.yml for
credentials. check_notebooks.py imports from here to run the same notebooks in
CI with write_back=False (validate only, don't touch the working tree).
"""
import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import nbformat
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


@dataclass
class NotebookResult:
    name: str
    passed: bool
    category: str = ""  # only set on failure
    detail: str = ""    # concise, human-readable cause


def configure_logging() -> None:
    # Set LOG_LEVEL=DEBUG to also print full tracebacks for failed notebooks.
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s")


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


def run_notebook(notebook_path: Path, write_back: bool) -> NotebookResult:
    """Execute a notebook and return a classified result.

    When write_back is True the executed notebook (with fresh outputs) is saved
    in place; CI passes False to validate without touching the working tree.
    """
    name = notebook_path.name
    logger.info(f"Running: {name}")

    with open(notebook_path) as f:
        # Read as nbformat v4 (the current schema) whatever version is on disk.
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=600, kernel_name=KERNEL_NAME)
    try:
        # Run in the notebook's own directory so its relative reads (config.yml) work.
        ep.preprocess(nb, {"metadata": {"path": notebook_path.parent}})
        if write_back:
            with open(notebook_path, "w") as f:
                nbformat.write(nb, f)
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


def run_all(write_back: bool) -> list[NotebookResult]:
    """Execute every Polytope notebook and return their results."""
    notebooks = sorted(POLYTOPE_DIR.glob("*.ipynb"))
    logger.info(f"Found {len(notebooks)} notebooks")
    return [run_notebook(nb, write_back) for nb in notebooks]


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


def main() -> int:
    """Execute all notebooks locally, writing fresh outputs back in place."""
    configure_logging()
    results = run_all(write_back=True)
    failed = [r for r in results if not r.passed]
    log_summary(results, failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
