#!/bin/zsh
# Step 1 (and step 5) measurement of eff-20261030-1: run each heavy test file alone on the Mac test runner, one serial
# pytest process (-n 0, as tools/select_tests.py runs a unit), with every node's setup/call/teardown seconds.
#   zsh docs/infra/eff-20261030-1/measure.sh <out dir> [extra pytest args...]
# Each file's output goes to <out dir>/<file stem>.log; <out dir>/runs.tsv gets one line per run: file, exit, wall s.
# docs/infra/eff-20261030-1/chunk_table.py reads them.
out=$1; shift
mkdir -p $out
files=(tests/test_consolidation_tools.py tests/test_acts_vocab_mutants.py tests/test_readings_rd6b_differential.py
       tests/test_english_evidence.py tests/test_trust_mutants.py tests/test_defaults_checks.py
       tests/test_speech_polar_lean.py tests/test_lean_conformance.py)
for f in $files; do
  stem=${${f:t}:r}
  t0=$(date +%s)
  zsh /home/seyran/code/manage-agents/mac-pytest.sh -- -n 0 -v -p no:cacheprovider --durations=0 --durations-min=0 \
      "$@" $f > $out/$stem.log 2>&1
  rc=$?
  print -r -- "$f	$rc	$(( $(date +%s) - t0 ))" >> $out/runs.tsv
done
