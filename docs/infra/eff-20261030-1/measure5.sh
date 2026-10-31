#!/bin/zsh
# Step 5 of eff-20261030-1 on the Mac test runner: each chunkable file whole (--bench-chunk 1/1) and then each of its
# chunks alone, one serial pytest process each, with every node's outcome and seconds and the process's peak RSS
# (tools/bench/chunk_probe.py: it sets the chunk the suite's own hook keeps, as a selected run does).
#   zsh docs/infra/eff-20261030-1/measure5.sh <out dir>
# k per file: the chunk count tools/select_tests.py chunk_counts gives on the 2026-10-30 map (432763b06d).
out=$1
mkdir -p $out
for spec in tests/test_acts_vocab_mutants.py:2 tests/test_readings_rd6b_differential.py:4 tests/test_english_evidence.py:4 \
            tests/test_trust_mutants.py:4 tests/test_speech_polar_lean.py:4; do
  f=${spec%:*}; k=${spec#*:}; stem=${${f:t}:r}
  for c in 1/1 $(seq -f "%g/$k" 1 $k); do
    t0=$(date +%s)
    zsh /home/seyran/code/manage-agents/mac-pytest.sh -- -n 0 -v -p no:cacheprovider -p tools.bench.chunk_probe \
        --bench-chunk $c --durations=0 --durations-min=0 $f > $out/$stem.${c/\//of}.log 2>&1
    print -r -- "$f	$c	$?	$(( $(date +%s) - t0 ))" >> $out/runs.tsv
  done
done
