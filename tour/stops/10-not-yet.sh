#!/bin/sh
# Tour stop 10 (tour/README.md). Run: sh tour/stops/10-not-yet.sh
. "$(dirname "$0")/common.sh"
on_after_release
show_run uv run --frozen python ../tour/stops/not_yet.py
