#!/bin/bash

# Pull the fdb uenv image
uenv image pull --build fdb/5.16:1907126596

root_dir=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)

kernel_dir="$HOME/.local/share/jupyter/kernels/"
if [ ! -d "$kernel_dir" ]; then
    mkdir -p "$kernel_dir"
fi
cd "$kernel_dir"

mkdir -p polytope-demo

sed "s|\"WRAPPER\"|\"$root_dir/uenv-wrapper.sh\"|" ${root_dir}/kernel.json > polytope-demo/kernel.json
