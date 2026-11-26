#!/bin/sh
# Tour stop 7 (tour/README.md). Run: sh tour/stops/07-company-policy.sh
. "$(dirname "$0")/common.sh"
on_after_release
show_run uv run --frozen python -m ve ask usecases/gitlab_relocation "Does Ivo meet the policy’s requirement to reside in their primary location in 2028?" --case R009
show_run uv run --frozen python -m ve ask usecases/gitlab_relocation "May Ivo live and work outside their primary location for the stays described in 2028?" --case R009
