#!/bin/zsh
# kb-2a-b acceptance: the five frozen keys' harnesses (docs/kernel/frozen-keys-20261111.md), each in its check mode,
# on this tree; each exit code and whether the tree is unchanged after it. Usage: zsh docs/kernel/kb-2a-b/frozen_keys.sh OUT
out=${1:?out}
cd ${0:A:h}/../../..
print -r -- "{" > $out
first=1
for key cmd in \
  rsp "usecases/anthropic-rsp/run.py --check" \
  preparedness "usecases/openai-preparedness/run.py --check --base-only" \
  fsf "usecases/safety-framework/run.py --check" \
  agent-policy "usecases/agent-policy/check.py base" \
  eligibility "usecases/eligibility/run.py --no-write --no-mutants"; do
  start=$(date +%s)
  uv run python ${=cmd} > /tmp/kb2ab/key-$key.log 2>&1
  rc=$?
  changed=$(git status --porcelain | grep -v '^?? \|docs/kernel/kb-2a-b/' | wc -l)
  [ $first = 1 ] || print -r -- "," >> $out
  first=0
  print -rn -- "\"$key\": {\"command\": \"$cmd\", \"exit\": $rc, \"seconds\": $(( $(date +%s) - start )), \"tree_changed_files\": $changed}" >> $out
done
print -r -- "}" >> $out
