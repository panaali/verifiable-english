#!/bin/zsh
# usage: pair5.sh <tag>: one paired round of the five frozen keys' commands (docs/kernel/frozen-keys-20261111.md; the
# Preparedness key with its full `--check`, which compares results.json). Each key runs in the base worktree (main) and
# the head worktree at the same time (same machine, same load). The Preparedness pair runs beside the other four pairs,
# which run one after another. (Round r1 ran with a bare `wait` in `pair`, which also waited for the Preparedness pair,
# so its other four pairs ran after it; each pair was still concurrent.) One line per run: harness, side, exit code, wall seconds, commit, UTC end time.
T=$1
B=/home/seyran/code/ve-kb-10b-switch-base; H=/home/seyran/code/ve-kb-10b-switch
export VE_LEAN_SERVICE=$H/lean/.lake/build/bin/ve_service   # no Lean change on the branch: one binary for both sides
PY=$H/.venv/bin/python
mkdir -p /tmp/kb10bs
typeset -A CMD
CMD=(anthropic-rsp "usecases/anthropic-rsp/run.py --check"
     safety-framework "usecases/safety-framework/run.py --check"
     openai-preparedness "usecases/openai-preparedness/run.py --check"
     agent-policy "usecases/agent-policy/check.py base"
     eligibility "usecases/eligibility/run.py --no-write --no-mutants")
run() { local w=$1 side=$2 h=$3; cd $w; local s=$(date +%s.%N)
  zsh /home/seyran/code/manage-agents/iso.sh kb10bs-$T-$h-$side 8G -- $PY ${=CMD[$h]} > /tmp/kb10bs/time-$T-$h-$side.log 2>&1
  local rc=$?; echo "$h $side rc=$rc wall=$(printf %.1f $(( $(date +%s.%N) - s )))s $(git -C $w rev-parse --short=10 HEAD) $(date -u +%H:%MZ)"; }
pair() { local a b; run $B before $1 & a=$!; run $H after $1 & b=$!; wait $a $b; }  # its own two runs only
echo "start $T $(date -u +%Y-%m-%dT%H:%MZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
pair openai-preparedness & P=$!
for h in anthropic-rsp safety-framework agent-policy eligibility; do pair $h; done
wait $P
echo "end $T $(date -u +%Y-%m-%dT%H:%MZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
for w in $B $H; do echo "$w status: $(git -C $w status --short | wc -l) changed"; done
