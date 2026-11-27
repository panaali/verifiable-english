#!/bin/sh
# Tour stop 8 (tour/README.md). Run: sh tour/stops/08-outside-the-text.sh
. "$(dirname "$0")/common.sh"
show_run uv run --frozen python -m ve ask tour/texts/club.ve.md "Is Ann retired?"
