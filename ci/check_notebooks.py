#!/usr/bin/env python3
"""Notebook validation script for CI."""
import logging
import os
import sys
import tempfile
from pathlib import Path

import nbformat
import yaml
from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor

logger = logging.getLogger(__name__)

KERNEL_NAME = "polytope-env"
ROOT_DIR = Path(__file__).resolve().parent.parent
POLYTOPE_DIR = ROOT_DIR / "examples" / "Polytope"

SKIP_NOTEBOOKS = {"data_retrieve_from_FDB.ipynb"}  # Requires CSCS uenv

# Cells to skip in specific notebooks (by cell source substring)
SKIP_CELLS = {
    "feature_time_series.ipynb": [
        'config["ecmwf"]',  # Skip all ECMWF-related cells
    ]
}


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


def should_skip_cell(notebook_name: str, cell_source: str) -> bool:
    """Check if a cell should be skipped based on SKIP_CELLS config."""
    if notebook_name not in SKIP_CELLS:
        return False
    return any(pattern in cell_source for pattern in SKIP_CELLS[notebook_name])


def run_notebook(notebook_path: Path, config_dir: Path) -> bool:
    """Execute a notebook; return True if successful."""
    logger.info(f"Running: {notebook_path.name}")

    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)

    # Mark cells to skip (ECMWF cells in time_series)
    skip_remaining = False
    for cell in nb.cells:
        if cell.cell_type == "code":
            if should_skip_cell(notebook_path.name, cell.source):
                skip_remaining = True  # Skip this and all following cells
            if skip_remaining:
                cell.source = "# SKIPPED BY CI\npass"
                logger.info(f"  Skipping cell (ECMWF)")

    ep = ExecutePreprocessor(timeout=600, kernel_name=KERNEL_NAME)

    # Symlink config into notebook directory
    config_link = notebook_path.parent / "config.yml"
    created_link = False
    if not config_link.exists():
        config_link.symlink_to(config_dir / "config.yml")
        created_link = True

    try:
        ep.preprocess(nb, {"metadata": {"path": notebook_path.parent}})
        logger.info(f"PASS: {notebook_path.name}")
        return True
    except CellExecutionError:
        logger.exception(f"FAIL: {notebook_path.name}")
        return False
    finally:
        if created_link and config_link.is_symlink():
            config_link.unlink()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    if not os.environ.get("POLYTOPE_USER_KEY"):
        logger.error("Missing required env var: POLYTOPE_USER_KEY")
        return 1

    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        create_config_file(config_dir / "config.yml")

        notebooks = sorted(
            p for p in POLYTOPE_DIR.glob("*.ipynb")
            if p.name not in SKIP_NOTEBOOKS
        )
        logger.info(f"Found {len(notebooks)} notebooks")

        failed = [nb for nb in notebooks if not run_notebook(nb, config_dir)]

        if failed:
            logger.error(f"{len(failed)} notebook(s) failed: {[f.name for f in failed]}")
            return 1

        logger.info("All notebooks passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
