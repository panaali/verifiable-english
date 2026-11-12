#!/bin/bash
# sc-admit-cpu (DRI amendment 2026-11-11, adv1118 item 2): main's and HEAD's answers of the three keyed corpora and of
# every soft-default readings document, all concurrently, then the comparison (docs/rd-9/sc-admit-cpu/cpu.md).
# Usage: run_corpora.sh <worktree> <main-tree> <out-dir>. <main-tree> is `git archive main` with main's built
# lean/.lake/build/bin/ve_service and the (unchanged) Rust release binary linked in; both sides run with the worktree's
# .venv Python and PYTHONPATH=<tree>. Writes only <out-dir>/{main,head}.
WT=$1; MAIN=$2; OUT=$3; PY=$WT/.venv/bin/python; S=$WT/docs/rd-9/sc-admit-cpu/corpora_answers.py
mkdir -p $OUT/main $OUT/head
echo "start $(date -u +%FT%TZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
echo "machine: $(lscpu | sed -n 's/^Model name: *//p'), $(nproc) vCPU"
pids=()
for side in main head; do
  if [ $side = main ]; then T=$MAIN; else T=$WT; fi
  (cd $T && PYTHONPATH=$T $PY $S documents $T $OUT/$side > $OUT/$side/documents.log 2>&1; echo "$side documents rc=$?") & pids+=($!)
  for c in anthropic-rsp openai-preparedness safety-framework; do
    (cd $T && PYTHONPATH=$T /usr/bin/time -f "$side $c %e s wall %U s user %M KB" $PY $S corpus $T $OUT/$side $c > $OUT/$side/$c.log 2>&1; echo "$side $c rc=$? $(tail -1 $OUT/$side/$c.log)") & pids+=($!)
  done
done
wait "${pids[@]}"
echo "end $(date -u +%FT%TZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
python3 -I $S compare $OUT/main $OUT/head; echo "compare rc=$?"
