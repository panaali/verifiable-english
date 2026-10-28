#!/bin/bash
# Cloud runner job for trust_mutants (2026-10-27 cloud plumbing; from the pilot's tm-job.sh). cloud-dispatch.sh embeds
# this file verbatim in the routine's prompt; the session writes it to /tmp/cloud-tm-job.sh and runs it detached.
# usage: cloud-tm-job.sh run <checkout> <out dir> <job> <head> <base> <asset url|-> <asset sha256|-> [trust_mutants args...]
#        cloud-tm-job.sh publish <checkout> <out dir> <job> <branch>
# run: checks HEAD = <head>, fetches history if <base> is missing, needs lean, lake, zstd and uv (exit 127 if one is
#   missing: without lake the Lean tests would skip silently), restores main's Lean build from the release asset (sha256
#   checked; any failure: cold build, logged), `uv sync --frozen`, the branch's incremental `lake build`, then
#   VE_LEAN_SHARE=off uv run --frozen python tools/trust_mutants.py --base <base> <args> --json <out>/trust-mutants.json.
#   Writes <out>/timings.tsv (step, rc, seconds), machine.txt, tm.rc (trust_mutants' exit code) and DONE (this script's).
# publish: copies the results (json, timings, machine, tm.rc, last 200 lines of each log) to cloud-results/<job>/,
#   commits ONLY that directory on top of <head> and pushes it to <branch> (no --force; one retry after 30 s).
# Tests only: CLOUD_TM_LEAN_BIN (a dir prepended to PATH), CLOUD_TM_TMP (default /tmp).
set -u
mode=$1; R=$2; O=$3; JOB=$4; shift 4
T=${CLOUD_TM_TMP:-/tmp}; export PATH=/usr/local/bin:/opt/lean/bin:$HOME/.local/bin:$PATH
[ -n "${CLOUD_TM_LEAN_BIN:-}" ] && export PATH=$CLOUD_TM_LEAN_BIN:$PATH
mkdir -p "$O"
if [ "$mode" = publish ]; then
  BR=$1; D=cloud-results/$JOB; cd "$R" || exit 2
  rm -rf "$D"; mkdir -p "$D"
  for f in trust-mutants.json timings.tsv machine.txt tm.rc DONE; do [ -f "$O/$f" ] && cp "$O/$f" "$D/"; done
  for f in "$O"/*.log; do [ -f "$f" ] && tail -n 200 "$f" > "$D/$(basename "$f").tail"; done
  git add -- "$D" && git -c user.name="VE cloud runner" -c user.email=noreply@anthropic.com commit -q -m "cloud-tm $JOB: trust_mutants result" -- "$D" || exit 3
  git push -q origin "HEAD:refs/heads/$BR" || { sleep 30; git push -q origin "HEAD:refs/heads/$BR"; } || exit 4
  git rev-parse HEAD; exit 0
fi
HEAD_SHA=$1; BASE=$2; URL=$3; SUM=$4; shift 4
P=$O/timings.tsv; printf 'step\trc\tseconds\n' > "$P"
now(){ date +%s.%N; }
step(){ local name=$1; shift; local t0; t0=$(now); "$@" > "$O/$name.log" 2>&1; local rc=$?
  printf '%s\t%s\t%s\n' "$name" "$rc" "$(awk -v a="$t0" -v b="$(now)" 'BEGIN{printf "%.1f", b-a}')" >> "$P"; return $rc; }
finish(){ echo "$1" > "$O/DONE"; exit "$1"; }
{ echo "job=$JOB nproc=$(nproc) host=$(hostname) date=$(date -u +%FT%TZ)"; free -g | sed -n 2p; df -h / | tail -1; uptime; } > "$O/machine.txt"
cd "$R" || finish 2
[ "$(git rev-parse HEAD)" = "$HEAD_SHA" ] || { echo "HEAD is not $HEAD_SHA" >> "$O/machine.txt"; finish 2; }
git cat-file -e "$BASE^{commit}" 2>/dev/null || step fetch_history git fetch -q --unshallow origin || step fetch_history2 git fetch -q origin
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
step trust_mutants uv run --frozen python tools/trust_mutants.py --base "$BASE" "$@" --json "$O/trust-mutants.json"
echo $? > "$O/tm.rc"
finish 0
