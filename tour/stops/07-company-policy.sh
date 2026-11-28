#!/bin/sh
# Tour stop 7 (tour/README.md). Run: sh tour/stops/07-company-policy.sh
. "$(dirname "$0")/common.sh"
MAIN_PYTHON=${VE_TOUR_PYTHON:-}
on_after_release
show_run uv run --frozen python -m ve ask usecases/gitlab_relocation "Does Ivo meet the policy’s requirement to reside in their primary location in 2028?" --case R009
show_run uv run --frozen python -m ve ask usecases/gitlab_relocation "May Ivo live and work outside their primary location for the stays described in 2028?" --case R009
# The answers' provenance: this checkout's `ve provenance` reads the after-release checkout that gave them (its commit,
# its Lean build, the translation's hash and freeze commit, and who translated, checked and signed off the text).
cd "$ROOT"
VE_TOUR_PYTHON=$MAIN_PYTHON
echo "(back in the main checkout: the provenance of the two answers above)"
show_run uv run --frozen python -m ve provenance .tour-after-release/usecases/gitlab_relocation
