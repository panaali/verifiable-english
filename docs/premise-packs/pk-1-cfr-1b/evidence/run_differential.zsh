#!/bin/zsh
# Writes the differential record: header, the 33 case sessions, the tool's full output, its exit status.
set -u
B=/home/seyran/code/ve-pk-1-cfr-1b-base; H=/home/seyran/code/ve-pk-1-cfr-1b-head
E=/home/seyran/code/ve-pk-1-cfr-1b/docs/premise-packs/pk-1-cfr-1b/evidence
OUT=$E/ab_route_cases_valid.txt; REC=/tmp/pk1cfr1b/recorded
export PATH=$HOME/.elan/bin:$PATH
cd $H
rm -rf $REC
{
  print "pk-1 route-case differential, rebuilt base vs head (pk-1-cfr-1b)"
  print "base $(git -C $B rev-parse HEAD) (main before pk-1: first parent of pk-1's merge)"
  print "head $(git -C $H rev-parse HEAD) (pk-1's merge on main, cb033316a7)"
  print "base lean/ clean: $(git -C $B status --porcelain -- lean | grep -vc '/.lake/') changes; head lean/ clean: $(git -C $H status --porcelain -- lean | grep -vc '/.lake/') changes"
  print "baseline manifest: $(python3 -c "import json;m=json.load(open('$B/lean/.lake/ve-output-baseline/manifest.json'));print(m['commit'])")"
  print "cases: docs/premise-packs/pk-1-cfr-1b/evidence/route_cases_norm_defaults.jsonl sha256 $(sha256sum $E/route_cases_norm_defaults.jsonl | cut -c1-64) (the 33 [\"norm-defaults\", case] lines of tests/data/route-cases.jsonl at head)"
  print "command 1 (in head): uv run python docs/premise-packs/pk-1-cfr-1b/evidence/route_case_sessions.py route_cases_norm_defaults.jsonl $REC"
  uv run python $E/route_case_sessions.py $E/route_cases_norm_defaults.jsonl $REC 2>&1
  print "invocation plan (in head): $(uv run python -c "
import tempfile
from pathlib import Path
from tools.lean_output_diff import static_invocations, recorded_invocations
s = static_invocations()
with tempfile.TemporaryDirectory() as d:
    r = recorded_invocations(Path('$REC'), Path(d))
print(f'static ve_service {sum(i.exe == \"ve_service\" for i in s)}, static ve_speech_acts_route {sum(i.exe == \"ve_speech_acts_route\" for i in s)}, recorded route-case ve_service sessions {len(r)} ({len({i.label for i in r})} distinct)')
")"
  print "command 2 (in head): uv run python tools/lean_output_diff.py --baseline $B/lean/.lake/ve-output-baseline --recorded $REC --jobs 8"
  uv run python tools/lean_output_diff.py --baseline $B/lean/.lake/ve-output-baseline --recorded $REC --jobs 8 2>&1
  rc=$?
  print "exit $rc"
} > $OUT
exit ${rc:-99}
