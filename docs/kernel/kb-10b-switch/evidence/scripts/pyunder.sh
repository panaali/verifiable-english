#!/bin/zsh
# usage: pyunder.sh <worktree> <tag>: py_under.py on the three safety-framework harnesses, --check
W=$1; T=$2; HARNESSES=(${=3})
export VE_LEAN_SERVICE=/home/seyran/code/ve-kb-10b-switch/lean/.lake/build/bin/ve_service
PY=/home/seyran/code/ve-kb-10b-switch/.venv/bin/python
cd $W
for h in ${HARNESSES[@]:-anthropic-rsp safety-framework openai-preparedness}; do
  s=$(date +%s)
  $PY /home/seyran/code/manage-agents/fable-team/architect/experiments/py_under.py /tmp/kb10bs/pyunder-$T-$h.json usecases/$h/run.py --check > /tmp/kb10bs/pyunder-$T-$h.log 2>&1
  echo "$h rc=$? $(( $(date +%s) - s ))s"
done
