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
  make_snapshots.sh -s [TARGET]    Make HTML snapshots (uses current outputs)
  make_snapshots.sh -c [TARGET]    Clear outputs in-place (prepare for commit)
  make_snapshots.sh -s -c [TARGET] Do both

TARGET (optional):
  - Omit to process: notebooks/FDB and notebooks/Polytope
  - Directory path: process all *.ipynb under it (recursively)
  - Single file: path/to/notebook.ipynb

Examples:
  ./make_snapshots.sh -s
  ./make_snapshots.sh -c notebooks/Polytope
  ./make_snapshots.sh -s notebooks/Polytope/feature_time_series.ipynb
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

# Determine script directory
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Default notebooks
default_dirs=("$script_dir/notebooks/FDB" "$script_dir/notebooks/Polytope")

target="${1:-}"
declare -a notebooks=()

collect_from_dir() {
  local d="$1"
  [ -d "$d" ] || return 0
  while IFS= read -r f; do
    notebooks+=("$f")
  done < <(find "$d" -type f -name "*.ipynb")
}

if [[ -z "$target" ]]; then
  for d in "${default_dirs[@]}"; do collect_from_dir "$d"; done
else
  if [[ -d "$target" ]]; then
    collect_from_dir "$target"
  elif [[ -f "$target" && "$target" == *.ipynb ]]; then
    notebooks+=("$target")
  else
    echo "TARGET not found or not a .ipynb: $target"
    exit 1
  fi
fi

if [[ ${#notebooks[@]} -eq 0 ]]; then
  echo "No notebooks found."
  exit 0
fi

# Choose jupyter runner (prefer Poetry if available)
jup="jupyter"
if command -v poetry >/dev/null 2>&1; then
  jup="poetry run jupyter"
fi

# Actions
if $make_snapshots; then
  snap_dir="$script_dir/notebooks/snapshots"
  mkdir -p "$snap_dir"
  echo "Making HTML snapshots into: $snap_dir"
  for nb in "${notebooks[@]}"; do
    if grep -E -q 'EmailKey|Bearer' "$nb"; then
      echo "Secret-like token found in: $nb"
      echo "Aborting snapshots. Clear/obfuscate secrets first."
      exit 1
    fi
    echo "  - $nb"
    $jup nbconvert "$nb" --to html --output-dir "$snap_dir" >/dev/null
  done
fi

if $clear_outputs; then
  echo "Clearing outputs in-place"
  for nb in "${notebooks[@]}"; do
    echo "  - $nb"
    $jup nbconvert --to notebook --ClearOutputPreprocessor.enabled=True --inplace "$nb" >/dev/null
  done
fi

echo "Done."
