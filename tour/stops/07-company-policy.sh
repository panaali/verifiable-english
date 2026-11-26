#!/bin/sh
# Tour stop 7 (tour/README.md). Run: sh tour/stops/07-company-policy.sh
. "$(dirname "$0")/common.sh"
on_after_release
show_run uv run --frozen python -m ve ask usecases/gitlab_relocation "Does Ana meet the policy’s requirement to reside in their primary location in 2027?" --case R001
show_run uv run --frozen python -m ve ask usecases/gitlab_relocation "Does Ivo meet the policy’s requirement to reside in their primary location in 2028?" --case R009
