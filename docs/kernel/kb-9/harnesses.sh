#!/bin/bash
# usage: harnesses.sh <phase>   runs the three harnesses --check under tools/kernel_trace.py
cd /home/seyran/code/ve-kb-9
phase=$1
for h in anthropic-rsp openai-preparedness safety-framework; do
  s=$(date +%s.%N)
  uv run python tools/kernel_trace.py /tmp/kb9m/$phase-$h.json usecases/$h/run.py --check > /tmp/kb9m/$phase-$h.log 2>&1
  rc=$?
  e=$(date +%s.%N)
  echo "$phase $h rc=$rc wall=$(echo "$e - $s" | bc) at $(date -Is)" | tee -a /tmp/kb9m/times.txt
done
git status --short | tee /tmp/kb9m/$phase-status.txt
