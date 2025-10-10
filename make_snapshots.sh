#!/usr/bin/env bash
# Simple notebook helper
# -s  Make HTML snapshots from current outputs
# -c  Clear outputs in-place (prepare for commit)
# TARGET (optional): a folder or a single .ipynb file
# Defaults to notebooks/FDB and notebooks/Polytope if no TARGET is given.

set -euo pipefail

clear_outputs=false
make_snapshots=false

usage() {
  cat <<'EOF'
Usage:
  notebooks.sh -s [TARGET]    Make HTML snapshots (uses current outputs in the notebooks)
  notebooks.sh -c [TARGET]    Clear outputs in-place (prepare for commit)
  notebooks.sh -s -c [TARGET] Do both

TARGET (optional):
  - Omit to process: notebooks/FDB and notebooks/Polytope
  - Directory path: process all *.ipynb under it (recursively)
  - Single file: path/to/notebook.ipynb

Examples:
  notebooks.sh -s
  notebooks.sh -c notebooks/Polytope
  notebooks.sh -s notebooks/Polytope/feature_time_series.ipynb
EOF
}

# Parse flags
while getopts ":csh" opt; do
  case "$opt" in
    c) clear_outputs=true ;;
    s) make_snapshots=true ;;
    h) usage; exit 0 ;;
    \?) echo "Unknown option: -$OPTARG"; usage; exit 1 ;;
  esac
done
shift $((OPTIND-1))

# Resolve target(s)
ROOT_DIR="$(pwd)"
DEFAULT_DIRS=("notebooks/FDB" "notebooks/Polytope")

TARGET="${1:-}"
declare -a NOTEBOOKS

collect_from_dir() {
  local d="$1"
  [ -d "$d" ] || return 0
  # shellcheck disable=SC2044
  for f in $(find "$d" -type f -name "*.ipynb"); do
    NOTEBOOKS+=("$f")
  done
}

if [[ -z "$TARGET" ]]; then
  for d in "${DEFAULT_DIRS[@]}"; do collect_from_dir "$d"; done
else
  if [[ -d "$TARGET" ]]; then
    collect_from_dir "$TARGET"
  elif [[ -f "$TARGET" && "$TARGET" == *.ipynb ]]; then
    NOTEBOOKS+=("$TARGET")
  else
    echo "TARGET not found or not a .ipynb: $TARGET"
    exit 1
  fi
fi

if [[ ${#NOTEBOOKS[@]} -eq 0 ]]; then
  echo "No notebooks found."
  exit 0
fi

# Choose jupyter runner (prefer Poetry if available)
JUP="jupyter"
if command -v poetry >/dev/null 2>&1; then
  JUP="poetry run jupyter"
fi

# Actions
if $make_snapshots; then
  SNAP_DIR="notebooks/snapshots"
  mkdir -p "$SNAP_DIR"
  echo "Making HTML snapshots into: $SNAP_DIR"
  for nb in "${NOTEBOOKS[@]}"; do
    # Basic secret check
    if grep -E -q 'EmailKey|Bearer' "$nb"; then
      echo "Secret-like token found in: $nb"
      echo "Aborting snapshots. Clear/obfuscate secrets first."
      exit 1
    fi
    echo "  - $nb"
    # NOTE: this uses current outputs; it does NOT execute the notebook.
    # If you need to execute, add: --execute
    $JUP nbconvert "$nb" --to html --output-dir "$SNAP_DIR" >/dev/null
  done
fi

if $clear_outputs; then
  echo "Clearing outputs in-place"
  for nb in "${NOTEBOOKS[@]}"; do
    echo "  - $nb"
    $JUP nbconvert --to notebook --ClearOutputPreprocessor.enabled=True --inplace "$nb" >/dev/null
  done
fi

echo "Done."
