#!/bin/sh
# Tour stop 3 (tour/README.md). Run: sh tour/stops/03-two-readings.sh
. "$(dirname "$0")/common.sh"
show_run uv run --frozen python -m ve ask usecases/question-answering/udhr-part07.ve.md "May every person form as well as join trade unions to protect their interests?"
