#!/bin/bash
image=$(cat "$(dirname "$0")/.fdb_image")

# disable core dumps
ulimit -c 0

exec uenv run --view=realtime "$image" -- /user-environment/venvs/fdb/bin/python3.11 "$@"
