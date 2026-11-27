#!/bin/sh
# Tour stop 2 (tour/README.md). Run: sh tour/stops/02-not-necessarily.sh
. "$(dirname "$0")/common.sh"
show_run uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Bo eligible?"
