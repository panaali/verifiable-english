#!/bin/bash
# Run 20261019T1800Z: premise-check variants of the PS-6r upgrades. usage: ps6r_variants.sh <tag> <comma list of unit ids without .presupposition, may be empty>
# Builds a scratch copy of the run directory (deleted afterwards by the caller), applies the repair with only the listed upgrades, runs nd.py all, keeps readings/nd-all-result.json.
set -u
export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
RUNDIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$RUNDIR/../../.." && pwd)
TAG=$1; ONLY=$2; EXTRA=${3:-}
S=$ROOT/usecases/claude-constitution-pilot/scratch-$TAG
rm -rf "$S"; mkdir "$S"
rsync -a --exclude __pycache__ --exclude evidence --exclude probes --exclude prev --exclude readings --exclude '*.json' --exclude '*.md' "$RUNDIR/" "$S/"
mkdir -p "$S/readings" "$S/evidence"
cp "$RUNDIR/prev/translation-without-content.ve.md" "$S/translation-without-content.ve.md"
cp "$RUNDIR"/readings/all-strict*.ve.md "$S/readings/" 2>/dev/null
cp -r "$RUNDIR/probes" "$S/probes"
mkdir -p "$S/prev"; cp "$RUNDIR/prev/"* "$S/prev/" 2>/dev/null
cd "$ROOT"
uv run python "$S/repair_20261019T1800Z.py" --only="$ONLY" $EXTRA > "$S/repair.out" 2>&1
uv run python "$S/nd.py" all > "$S/readings/nd-all.out" 2>&1
python3 - "$S" "$TAG" "$ONLY" <<'P'
import json, sys
s, tag, only = sys.argv[1:]
r = json.load(open(f"{s}/readings/nd-all-result.json"))
from collections import Counter
print(json.dumps({"variant": tag, "added": only, "premises": r["premises"]["status"], "route": r["premises"]["route"], "candidates": dict(Counter(c["status"] for c in r["premises"]["candidates"])),
                  "bytes_by_status": r["bytes_by_status"]}))
P
