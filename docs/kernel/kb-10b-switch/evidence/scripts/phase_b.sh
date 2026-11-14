#!/bin/zsh
# The restart round's other evidence runs (after the paired timings, which ran alone), all at once, each under iso.sh:
#  split.py on the three safety-framework harnesses (head): Lean wall and CPU of each soft-selected call (R4's budgets);
#  py_funcs.py on the three, base and head: the ve functions that run (task item (4));
#  f8_pairs.py on FSF (head): the switch's calls against step (1)'s pairs (review F8);
#  measure_keyed_paths.py --write (head): docs/usecases/keyed-answers.json on the rebased code;
#  the per-answer ownership trace of every RSP item (head), as ownership/run_all.sh.
# py_funcs runs with PYTHONPATH=<its worktree> (see pair5.sh): the first run lacked it, so Preparedness "before"
# imported the head's `ve` and recorded nothing under the base's ve/; it was rerun alone (pyfuncs_prep_before.sh).
H=/home/seyran/code/ve-kb-10b-switch; B=$H-base; PY=$H/.venv/bin/python; S=$H/docs/kernel/kb-10b-switch/evidence/scripts
ISO=/home/seyran/code/manage-agents/iso.sh; O=/tmp/kb10bs
export VE_LEAN_SERVICE=$H/lean/.lake/build/bin/ve_service
mkdir -p $O/own/items
echo "start $(date -u +%Y-%m-%dT%H:%MZ) load $(cut -d' ' -f1-3 /proc/loadavg) head $(git -C $H rev-parse --short=10 HEAD) base $(git -C $B rev-parse --short=10 HEAD)"
for h in anthropic-rsp safety-framework openai-preparedness; do
  (cd $H && zsh $ISO kb10bs-split-$h 8G -- $PY $S/split.py $H $h > $O/split-$h.log 2>&1; echo "split $h rc=$?") &
  for side in before after; do
    w=$H; [[ $side == before ]] && w=$B
    (cd $w && PYTHONPATH=$w zsh $ISO kb10bs-pf-$side-$h 8G -- $PY $S/py_funcs.py $O/pyfuncs-$side-$h.json usecases/$h/run.py --check \
       > $O/pyfuncs-$side-$h.log 2>&1; echo "py_funcs $side $h rc=$?") &
  done
done
(cd $H && zsh $ISO kb10bs-f8 8G -- $PY $S/f8_pairs.py safety-framework $O/f8-safety-framework.json > $O/f8.log 2>&1; echo "f8 rc=$?") &
(cd $H && zsh $ISO kb10bs-keyed 8G -- $PY usecases/measure_keyed_paths.py --write > $O/keyed.log 2>&1; echo "keyed rc=$?") &
(cp $H/docs/kernel/kb-10b-switch/ownership/trace_item_callers.py $O/own/ \
   && zsh $ISO kb10bs-ownership 16G -- zsh $H/docs/kernel/kb-10b-switch/ownership/run_all.sh > $O/own/run.log 2>&1; echo "ownership rc=$?") &
wait
echo "end $(date -u +%Y-%m-%dT%H:%MZ)"
