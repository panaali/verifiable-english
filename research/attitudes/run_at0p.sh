#!/usr/bin/env bash
# AT-0p end to end (5 to 20 min, by load): fresh copies of the pilot run, reproduction of its recorded translation,
# probe and rendering, the rewrite, the rebuild, the probe, the measurements and the render diff. Run from the
# repository root after `lake build` in lean/ and `python3 tools/rust_build.py`. Every VE run has a 6 GiB
# address-space limit.
set -euo pipefail
export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
# wall-clock limits only (a call that runs out is CheckerUnavailable, never an answer): the 5 s Rust default fails on a
# loaded machine (load 84 on 32 cores, 2026-10-13)
export VE_RUST_TIMEOUT=${VE_RUST_TIMEOUT:-600} VE_LEAN_TIMEOUT=${VE_LEAN_TIMEOUT:-1800} \
       VE_LEAN_SERVICE_TIMEOUT=${VE_LEAN_SERVICE_TIMEOUT:-1800}
LIMIT="prlimit --as=6442450944"
PILOT=/home/seyran/code/manage-agents/pilots/claude-constitution/run-20261012T1800Z
B=research/attitudes/run-baseline
W=research/attitudes/run-at0p
uv run python research/attitudes/at0p.py copy
$LIMIT uv run python $B/nd.py all > $B/nd-all.repro.out 2>&1
cmp $B/readings/nd-all.ve.md $PILOT/translation.ve.md
$LIMIT uv run python $B/probe_unspecified.py > $B/probe-unspecified.repro.out 2>&1
cmp $B/probes/unspecified-probe.json $PILOT/probes/unspecified-probe.json
$LIMIT uv run python -m ve document render $B/readings/nd-all.ve.md > $B/rendered-raw.md
cmp $B/rendered-raw.md $PILOT/rendered-raw.md
$LIMIT uv run python research/attitudes/at0p.py apply
$LIMIT uv run python $W/nd.py all > $W/nd-all.at0p.out 2>&1
mv $W/readings/nd-all.ve.md $W/translation.ve.md
$LIMIT uv run python research/attitudes/at0p.py probe > $W/probe.out
$LIMIT uv run python research/attitudes/at0p.py measure > $W/measure.out
$LIMIT uv run python -m ve document render $W/translation.ve.md > $W/rendered-raw.md
uv run python research/attitudes/at0p.py render
test ! -e $PILOT/__pycache__
echo "AT-0p: done; evidence in docs/research/evidence/attitudes/"
