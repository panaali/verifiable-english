#!/bin/sh
# Tour stop 5 (tour/README.md). Run: sh tour/stops/05-sum.sh
. "$(dirname "$0")/common.sh"
on_after_release
show_run uv run --frozen python ../tour/stops/sums.py
