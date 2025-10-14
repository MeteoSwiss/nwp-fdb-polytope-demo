#!/bin/bash
image=$(cat "$(dirname "$0")/.fdb_image")

uenv run --view=realtime "$image" -- /user-environment/venvs/fdb/bin/python3.11 "$@"


