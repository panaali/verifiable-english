#!/bin/sh
# Tour stop 6 (tour/README.md). Run: sh tour/stops/06-checker.sh
. "$(dirname "$0")/common.sh"
show_status 6 uv run --frozen python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json
