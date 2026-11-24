#!/bin/bash
# relb-clean-run: run-demo.sh <out-dir> <id>: run one line of commands.txt (DEMO.md's commands, verbatim) in the
# shell state the previous line left (working directory and PATH), as if every line were typed into one terminal.
# stdout -> <out>/step-<id>.out, stderr -> <out>/step-<id>.err, both appended to <out>/demo.log; one row in
# <out>/steps.tsv (id, rc, wall seconds, UTC start, command). Exits with the command's own code.
set -u
OUT=$1; ID=$2; export OUT
HERE=$(cd "$(dirname "$0")" && pwd)
CMD=$(awk -F'\t' -v id="$ID" '$1==id { sub(/^[^\t]*\t/, ""); print; exit }' "$HERE/commands.txt")
[ -n "$CMD" ] || { echo "run-demo.sh: no command $ID in commands.txt" >&2; exit 2; }
[ -f "$OUT/steps.tsv" ] || printf 'id\trc\tseconds\tstart_utc\tcommand\n' > "$OUT/steps.tsv"
if [ -f "$OUT/state.pwd" ]; then cd "$(cat "$OUT/state.pwd")" || exit 2; PATH=$(cat "$OUT/state.path"); export PATH
else cd "$HOME" || exit 2; fi
start=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{ echo "### STEP $ID at $start in $PWD"; echo "\$ $CMD"; } | tee -a "$OUT/demo.log"
t0=$(date +%s)
eval "$CMD" > "$OUT/step-$ID.out" 2> "$OUT/step-$ID.err" < /dev/null
rc=$?
secs=$(( $(date +%s) - t0 ))
{ cat "$OUT/step-$ID.out"
  [ -s "$OUT/step-$ID.err" ] && { echo "--- stderr ---"; cat "$OUT/step-$ID.err"; }
  echo "### STEP $ID: rc=$rc in ${secs} s"; echo; } | tee -a "$OUT/demo.log"
printf '%s\t%s\t%s\t%s\t%s\n' "$ID" "$rc" "$secs" "$start" "$CMD" >> "$OUT/steps.tsv"
pwd > "$OUT/state.pwd"; printf '%s' "$PATH" > "$OUT/state.path"
lb=${TMPDIR:-/tmp}/ve-demo-lake-build.log
[ -f "$lb" ] && cp "$lb" "$OUT/lake-build-$ID.log"
exit $rc
