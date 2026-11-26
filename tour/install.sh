#!/bin/sh
# The tour's one install command, from the repository root:  sh tour/install.sh
#
# 1. Everything the main branch needs: usecases/eligibility/demo/install.sh (the prerequisites, each only if missing,
#    then uv sync, the Lean build and the Rust build; the first Lean build takes 20 to 40 minutes).
# 2. A second checkout of branch after-release in .tour-after-release/, for the stops whose feature is not on main
#    yet (stops 4, 5, 7, 9 and 10). Its Lean build starts from a copy of the first one, so only the Lean files that
#    differ are rebuilt; its Rust checker is copied when the Rust sources are the same, else built.
# Safe to run again. Prints each step's time in seconds and the total.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
export PATH="$HOME/.local/bin:$HOME/.elan/bin:$HOME/.cargo/bin:$PATH"
START=$(date +%s)
SIDE="$ROOT/.tour-after-release"

sh usecases/eligibility/demo/install.sh

echo "==> the after-release checkout (.tour-after-release/)"
t0=$(date +%s)
if [ ! -d "$SIDE" ]; then
    if git rev-parse -q --verify after-release^{commit} >/dev/null; then ref=after-release
    elif git rev-parse -q --verify origin/after-release^{commit} >/dev/null; then ref=origin/after-release
    else git fetch -q origin after-release && ref=FETCH_HEAD; fi
    git worktree add -q --detach "$SIDE" "$ref"
fi
if [ ! -x "$SIDE/lean/.lake/build/bin/ve_service" ]; then
    mkdir -p "$SIDE/lean"
    cp -a lean/.lake "$SIDE/lean/"
fi
log=$(mktemp "${TMPDIR:-/tmp}/ve-tour-lake.XXXXXX")
if (cd "$SIDE/lean" && lake build) >"$log" 2>&1; then tail -n 1 "$log"; rm -f "$log"
else tail -n 40 "$log"; echo "lake build failed in $SIDE; full log: $log" >&2; exit 1; fi
if [ "$(git rev-parse HEAD:rust)" = "$(git -C "$SIDE" rev-parse HEAD:rust)" ] && [ -x rust/target/release/ve ]; then
    mkdir -p "$SIDE/rust/target/release"
    cp -p rust/target/release/ve "$SIDE/rust/target/release/ve"
else
    (cd "$SIDE" && uv run --frozen python tools/rust_build.py)
fi
(cd "$SIDE" && uv sync --locked --inexact)
echo "==> the after-release checkout: done in $(( $(date +%s) - t0 )) s"
echo "==> tour install: all done in $(( $(date +%s) - START )) s"
echo "Next: sh tour/stops/01-yes.sh"
