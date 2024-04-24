#!/bin/bash

root_dir=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)

kernel_dir="$HOME/.local/share/jupyter/kernels/"
if [ ! -d "$kernel_dir" ]; then
    mkdir -p "$kernel_dir"
fi
cd "$kernel_dir"

mkdir -p polytope-demo

cp ${root_dir}/kernel.json polytope-demo/
