#!/usr/bin/env python3
"""Notebook validation script for CI."""
import logging
import os
import sys
from pathlib import Path

import nbformat
import yaml
from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor

logger = logging.getLogger(__name__)

KERNEL_NAME = "polytope-env"
ROOT_DIR = Path(__file__).resolve().parent.parent
POLYTOPE_DIR = ROOT_DIR / "examples" / "Polytope"

# In this notebook, blank the first cell that touches ECMWF config and every cell
# after it — CI has no ECMWF credentials.
SKIP_FROM_NOTEBOOK = "feature_time_series.ipynb"
SKIP_FROM_PATTERN = 'config["ecmwf"]'


def create_config_file(config_path: Path) -> None:
    """Create config.yml from environment variables."""
    config = {
        "meteoswiss": {
            "key": os.environ.get("POLYTOPE_USER_KEY", ""),
        },
        "ecmwf": {
            "user_email": "",  # Intentionally empty - ECMWF cells skipped
            "key": "",
        },
    }
    with open(config_path, "w") as f:
        yaml.dump(config, f)


def run_notebook(notebook_path: Path) -> bool:
    """Execute a notebook; return True if successful."""
    logger.info(f"Running: {notebook_path.name}")

    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)

    skip_remaining = False
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        if notebook_path.name == SKIP_FROM_NOTEBOOK and SKIP_FROM_PATTERN in cell.source:
            skip_remaining = True
        if skip_remaining:
            cell.source = "# SKIPPED BY CI\npass"

    ep = ExecutePreprocessor(timeout=600, kernel_name=KERNEL_NAME)
    try:
        ep.preprocess(nb, {"metadata": {"path": notebook_path.parent}})
        logger.info(f"PASS: {notebook_path.name}")
        return True
    except CellExecutionError:
        logger.exception(f"FAIL: {notebook_path.name}")
        return False


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    if not os.environ.get("POLYTOPE_USER_KEY"):
        logger.error("Missing required env var: POLYTOPE_USER_KEY")
        return 1

    notebooks = sorted(POLYTOPE_DIR.glob("*.ipynb"))
    logger.info(f"Found {len(notebooks)} notebooks")

    # The notebooks read config.yml from their own directory; provide it once.
    config_path = POLYTOPE_DIR / "config.yml"
    created_config = not config_path.exists()
    if created_config:
        create_config_file(config_path)

    try:
        failed = [nb for nb in notebooks if not run_notebook(nb)]
    finally:
        if created_config:
            config_path.unlink(missing_ok=True)

    if failed:
        logger.error(f"{len(failed)} notebook(s) failed: {[f.name for f in failed]}")
        return 1

    logger.info("All notebooks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
