#!/bin/sh
# The tour's longer example (tour/README.md, after stop 10). Run: sh tour/stops/11-longer-example.sh
. "$(dirname "$0")/common.sh"
show_run uv run --frozen python -m ve ask usecases/question-answering/udhr-part07.ve.md "May every person form as well as join trade unions to protect their interests?"
