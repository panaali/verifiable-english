#!/bin/sh
# Tour: stop 12, write your own rules (tour/README.md, after the longer example).
# Run: sh tour/stops/12-write-your-own.sh
. "$(dirname "$0")/common.sh"
show_status 12 uv run --frozen python -m ve read tour/texts/own-rules.txt
show_run uv run --frozen python -m ve read tour/texts/own-rules-new-word.txt
show_status 12 uv run --frozen python -m ve read tour/texts/own-rules-new-word-fixed.txt
