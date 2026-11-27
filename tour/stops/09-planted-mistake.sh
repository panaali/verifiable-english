#!/bin/sh
# Tour stop 9 (tour/README.md). Run: sh tour/stops/09-planted-mistake.sh
. "$(dirname "$0")/common.sh"
on_after_release
show_run uv run --frozen python ../tour/stops/planted.py
