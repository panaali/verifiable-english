#!/bin/sh
# Tour stop 1 (tour/README.md). Run: sh tour/stops/01-yes.sh
. "$(dirname "$0")/common.sh"
show_run uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Ann eligible?"
