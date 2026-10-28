#!/bin/bash
# Codex Cloud runner for one VE job (2026-10-28 dri-tmshardon; backlog codex-cloud-pool, reviews/tmshard-on-20261028.md;
# flag CODEX_CLOUD_POOL). The same job commit as the GitHub Actions pool (gha-job.sh: ONE commit on the job's exported
# head adding only ci-job/job.json, ci-job/job.sh, the workflow file and this file), pushed as cx-job/<job> (ve-job.yml
# runs on ci-job/** only: no Actions run). The Codex task is checked out at that commit; its agent starts this file under
# setsid and waits for $T/cx-out/END (cloud-codex-prompt.py). Nothing is transcribed by the agent: on Oct 28 Codex agents
# rewrote a pasted job script (dropping the cache restore) or skipped files, so the script now travels in the commit.
#   checks the commit's shape (parent = job.json "head", no merge, only those files), adds a detached worktree at head
#   ($T/cx-wt; the task's checkout stays at the job commit), runs
#   bash job.sh run <worktree> <out> <job.json "argv"...>   (the cloud runner's contract, as on Actions)
#   then copies the results into the TASK's checkout as cloud-results/<job>/ and makes ONE local commit of that directory
#   only (a Codex task returns only committed changes, as its diff; never pushed). Ends by writing $T/cx-out/END:
#   "COMMITTED <sha> job_rc=<n>" or "FAILED <why>" (a FAILED end still commits what exists, for the log tails).
# usage: cx-run.sh <job> <job commit>      (from the task's VE checkout, whose HEAD is the job commit)
# Tests only: CX_RUN_TMP (default /tmp).
set -u
JOB=$1; JC=$2; R=$PWD; T=${CX_RUN_TMP:-/tmp}; O=$T/cx-out; WT=$T/cx-wt; C=$T/cx-job
export PATH=/usr/local/bin:/opt/lean/bin:$HOME/.local/bin:$PATH
mkdir -p "$O" "$C"; t0=$(date +%s)
commit(){ cd "$R" || return 1; local D=cloud-results/$JOB; rm -rf "$D"; mkdir -p "$D"
  for f in "$O"/*; do [ -f "$f" ] || continue; case $f in */END|*/END.tmp) continue;; *.log) tail -n 200 "$f" > "$D/$(basename "$f").tail";; *) cp "$f" "$D/";; esac; done
  git add -- "$D" && git -c user.name="VE codex runner" -c user.email=noreply@anthropic.com commit -q -m "cx-job $JOB: result (local, never pushed)" -- "$D" && git rev-parse HEAD; }
end(){ echo "$1" > "$O/END.tmp" && mv "$O/END.tmp" "$O/END"; echo "cx-run: $1"; exit 0; }
fail(){ echo "$1" >> "$O/cx-run.log"; commit > /dev/null 2>&1; end "FAILED $1"; }
[[ $JOB =~ ^[A-Za-z0-9._-]+$ && $JC =~ ^[0-9a-f]{40}$ ]] || end "FAILED usage"
[ "$(git -C "$R" rev-parse HEAD)" = "$JC" ] || fail "the checkout is not at the job commit $JC"
# --- the job commit's shape (as ve-job.yml's "job commit" step)
git -C "$R" show "$JC:ci-job/job.json" > "$C/job.json" && git -C "$R" show "$JC:ci-job/job.sh" > "$C/job.sh" || fail "no ci-job files"
head=$(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["job"]==sys.argv[2]; print(d["head"])' "$C/job.json" "$JOB") || fail "job.json is not $JOB"
[ "$(git -C "$R" rev-parse "$JC~1")" = "$head" ] && ! git -C "$R" rev-parse -q --verify "$JC^2" > /dev/null || fail "the job commit's parent is not $head"
extra=$(git -C "$R" diff --name-only "$JC~1" "$JC" | grep -v -x -E 'ci-job/job\.json|ci-job/job\.sh|ci-job/cx-run\.sh|\.github/workflows/ve-job\.yml' || true)
[ -z "$extra" ] || fail "the job commit changes other files: $extra"
# --- worktree at head, machine facts
rm -rf "$WT"; git -C "$R" worktree prune 2>/dev/null
git -C "$R" worktree add -q --detach "$WT" "$head" 2>> "$O/cx-run.log" || fail "worktree at $head"
{ echo "job=$JOB job_commit=$JC nproc=$(nproc)"; free -m | awk '/Mem:/{print "mem_total_mb="$2" mem_avail_mb="$7}'
  df -h "$T" | awk 'NR==2{print "tmp_free="$4}'; lean --version 2>&1 | head -1; uv --version 2>&1; } > "$O/cx.txt"
# --- run (same contract as the Actions workflow's job step)
mapfile -t argv < <(python3 -I -c 'import json, sys; print("\n".join(json.load(open(sys.argv[1]))["argv"]))' "$C/job.json")
bash "$C/job.sh" run "$WT" "$O" "${argv[@]}" >> "$O/cx-run.log" 2>&1; jrc=$?
echo "job_rc=$jrc job_s=$(( $(date +%s) - t0 ))" >> "$O/cx.txt"
rc=$(commit) || end "FAILED result commit"
end "COMMITTED $rc job_rc=$jrc"
