#!/bin/sh
# Tour stop 4 (tour/README.md). Run: sh tour/stops/04-date.sh
. "$(dirname "$0")/common.sh"
on_after_release
show_run uv run --frozen python ../tour/stops/dates.py
