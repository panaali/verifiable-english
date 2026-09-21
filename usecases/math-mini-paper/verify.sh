#!/bin/sh
# Re-run every check in the mini-paper from scratch, then regenerate paper.md.
#
#   cd usecases/math-mini-paper && ./verify.sh
#
# Prerequisite (once): cd lean && lake build
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
export UV_CACHE_DIR="${UV_CACHE_DIR:-/private/tmp/ve-uv-cache-uc}"

if [ ! -x "$ROOT/lean/.lake/build/bin/ve_conformance" ]; then
  echo "note: Lean executable missing; run 'cd $ROOT/lean && lake build'." >&2
  echo "      Lean columns will report n/a." >&2
fi

cd "$ROOT"
rm -rf "$HERE/theorems" "$HERE/countermodels"
mkdir -p "$HERE/theorems" "$HERE/countermodels"

uv run python "$HERE/verify.py"
uv run python "$HERE/make_paper.py"

echo
echo "--- Task B boundary probe (see boundary.md) ---"
uv run python "$HERE/boundary/probe.py" > "$HERE/boundary/probe-output.txt"
echo "wrote boundary/results.json and boundary/probe-output.txt"
