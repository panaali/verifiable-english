#!/bin/bash
# GitHub Actions command job (2026-10-28 dri-gha, reviews/gha-pilot-20261028.md); the workflow runs it as ci-job/job.sh.
# usage: cmd-job.sh run <checkout> <out dir> <job> <head> <base> <asset url|-> <asset sha256|-> <name>=<command>...
# Same setup as cloud-tm-job.sh (HEAD check, history for <base>, tools, main's Lean build from the sha256-checked cache
# asset, else a cold build, `uv sync --frozen`, the branch's incremental `lake build`), then each <command> in order with
# `bash -c` in the checkout (BASE=<base> in its environment), log <name>.log. Writes timings.tsv (step, rc, seconds),
# machine.txt, steps.rc (name rc per command) and DONE (this script's exit code).
set -u
mode=$1; R=$2; O=$3; JOB=$4; HEAD_SHA=$5; BASE=$6; URL=$7; SUM=$8; shift 8
[ "$mode" = run ] || exit 2
T=${CLOUD_TM_TMP:-/tmp}; export PATH=/usr/local/bin:/opt/lean/bin:$HOME/.local/bin:$PATH BASE
mkdir -p "$O"; P=$O/timings.tsv; printf 'step\trc\tseconds\n' > "$P"
now(){ date +%s.%N; }
step(){ local name=$1; shift; local t0; t0=$(now); "$@" > "$O/$name.log" 2>&1; local rc=$?
  printf '%s\t%s\t%s\n' "$name" "$rc" "$(awk -v a="$t0" -v b="$(now)" 'BEGIN{printf "%.1f", b-a}')" >> "$P"; return $rc; }
finish(){ echo "$1" > "$O/DONE"; exit "$1"; }
{ echo "job=$JOB nproc=$(nproc) host=$(hostname) date=$(date -u +%FT%TZ)"; free -g | sed -n 2p; df -h / | tail -1; uptime; } > "$O/machine.txt"
cd "$R" || finish 2
[ "$(git rev-parse HEAD)" = "$HEAD_SHA" ] || { echo "HEAD is not $HEAD_SHA" >> "$O/machine.txt"; finish 2; }
git cat-file -e "$BASE^{commit}" 2>/dev/null || step fetch_history git fetch -q origin
git cat-file -e "$BASE^{commit}" 2>/dev/null || { echo "base $BASE missing" >> "$O/machine.txt"; finish 2; }
for t in lean lake zstd uv; do command -v $t > /dev/null || { echo "missing tool: $t" >> "$O/machine.txt"; printf 'tools\t127\t0\n' >> "$P"; finish 127; }; done
lean --version >> "$O/machine.txt" 2>&1
restored=""
if [ "$URL" != - ]; then
  if step cache_download curl -sSfL --retry 2 -o "$T/lean-cache.tar.zst" "$URL" \
     && step cache_sha256 bash -c "echo '$SUM  $T/lean-cache.tar.zst' | sha256sum -c -" \
     && step cache_restore bash -c "rm -rf '$T/lc' && mkdir -p '$T/lc' && zstd -dc '$T/lean-cache.tar.zst' | tar -x -C '$T/lc' && chmod -R u+w '$T/lc' && rm -rf lean/.lake/build && mkdir -p lean/.lake && mv '$T/lc/lake/build' lean/.lake/build"; then
    restored=1; fi
  rm -f "$T/lean-cache.tar.zst"
fi
[ -n "$restored" ] || echo "no cache restored: cold build" >> "$O/machine.txt"
step python_env uv sync --frozen || finish 2
(cd lean && step branch_lake_build lake build)
export VE_LEAN_SHARE=off
: > "$O/steps.rc"
for spec in "$@"; do name=${spec%%=*}; cmd=${spec#*=}
  [[ $name =~ ^[A-Za-z0-9_-]+$ ]] || { echo "$spec: bad step name" >> "$O/machine.txt"; continue; }
  step "$name" bash -c "$cmd"; echo "$name $?" >> "$O/steps.rc"; done
finish 0
