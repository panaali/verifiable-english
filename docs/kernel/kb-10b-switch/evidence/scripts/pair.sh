#!/bin/zsh
# usage: pair.sh <harness> <tag>: `--check` wall time of the base and head worktrees, run concurrently (same load)
h=$1; t=$2
export VE_LEAN_SERVICE=/home/seyran/code/ve-kb-10b-switch/lean/.lake/build/bin/ve_service
PY=/home/seyran/code/ve-kb-10b-switch/.venv/bin/python
run() { local w=$1 side=$2; cd $w; local s=$(date +%s.%N)
  zsh /home/seyran/code/manage-agents/iso.sh kb10bs-time-$side 8G -- $PY usecases/$h/run.py --check > /tmp/kb10bs/time-$t-$h-$side.log 2>&1
  local rc=$?; echo "$h $side rc=$rc wall=$(printf %.1f $(( $(date +%s.%N) - s )))s $(git -C $w rev-parse --short HEAD) $(date -u +%H:%MZ)"; }
echo "start $(date -u +%Y-%m-%dT%H:%MZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
run /home/seyran/code/ve-kb-10b-switch-base before &
run /home/seyran/code/ve-kb-10b-switch after &
wait
echo "end $(date -u +%Y-%m-%dT%H:%MZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
