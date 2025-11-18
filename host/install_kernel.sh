#!/bin/bash

# Set the FDB image name
fdb_image="fdb/5.18:v1"

# Pull the fdb uenv image
uenv image pull "$fdb_image"

root_dir=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)

# Save image name for wrapper
echo "$fdb_image" > "$root_dir/.fdb_image"


kernel_dir="$HOME/.local/share/jupyter/kernels/"
if [ ! -d "$kernel_dir" ]; then
    mkdir -p "$kernel_dir"
fi
cd "$kernel_dir"

mkdir -p polytope-demo

sed "s|\"WRAPPER\"|\"$root_dir/uenv-wrapper.sh\"|" ${root_dir}/kernel.json > polytope-demo/kernel.json

echo "'polytope demo' kernel has been installed successfully at: $kernel_dir"
