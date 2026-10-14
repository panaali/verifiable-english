#!/usr/bin/env bash
# JT-0p end to end (3 to 10 min, by load): copies of the pinned UDHR run, the u010/u060 encoding, the check of the four
# parts before and after, bar part A, then the instrument, the integrity scan, the admission forecast and P2-P9.
# Run from the repository root with the pinned checkers at lean/.lake/build/bin/ve_service and rust/target/release/ve
# (their hashes are recorded in docs/research/evidence/judgment-terms/jt0p-inputs.json). Every VE run has a 6 GiB
# address-space limit; the wall-clock limits are raised for a loaded machine (a call that runs out is
# CheckerUnavailable, never an answer).
set -euo pipefail
export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
export VE_RUST_TIMEOUT=${VE_RUST_TIMEOUT:-600} VE_LEAN_TIMEOUT=${VE_LEAN_TIMEOUT:-1800} \
       VE_LEAN_SERVICE_TIMEOUT=${VE_LEAN_SERVICE_TIMEOUT:-1800}
LIMIT="prlimit --as=6442450944"
J=research/judgment-terms
uv run python $J/jt0p.py copy
uv run python $J/jt0p.py apply
$LIMIT uv run python $J/jt0p.py check run-baseline
$LIMIT uv run python $J/jt0p.py check run-jt0p
uv run python $J/jt0p.py compare
python3 $J/measure.py reproduce
python3 $J/measure.py instrument
python3 $J/measure.py forecast
python3 $J/measure.py scan
python3 $J/measure.py integrity
echo "JT-0p: done; evidence in docs/research/evidence/judgment-terms/"
