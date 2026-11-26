#!/bin/sh
# The tour's one install command, from the repository root:
#   sh tour/install.sh                 fetch the prebuilt checker programs (a few minutes)
#   sh tour/install.sh --from-source   build them from source instead (about an hour)
#
# Both ways: uv (Python and its packages), then a second checkout of branch after-release, at the commit in
# tour/AFTER_RELEASE_COMMIT, in .tour-after-release/ (stops 4, 5, 7, 9 and 10 run there until their features reach main).
# The fast way then fetches one archive with the two checker programs of both checkouts (Lean's ve_service and the
# Rust ve; tour/prebuilt.py checks it against tour/prebuilt.json before unpacking anything). VE_TOUR_PREBUILT=<URL or
# path> fetches it from elsewhere (a copy on your own disk, say). When the checkout's Lean or Rust sources are not the
# ones the programs were built from, the fast way says so and builds from source.
# --from-source runs usecases/eligibility/demo/install.sh (Lean and Rust toolchains, then the builds), then builds the
# after-release checkout's Lean programs, starting from a copy of the first build.
# Never runs sudo: a missing system package (git, curl, or for --from-source a C compiler) stops the install with the
# apt-get command to run. Safe to run again. Prints each step's time and, during a build, a line every minute.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
export PATH="$HOME/.local/bin:$HOME/.elan/bin:$HOME/.cargo/bin:$PATH"
export VE_NO_SUDO=1
START=$(date +%s)
SIDE="$ROOT/.tour-after-release"
PIN=$(cat tour/AFTER_RELEASE_COMMIT)
MODE=prebuilt
case "${1:-}" in
    "") ;;
    --from-source) MODE=source ;;
    *) echo "usage: sh tour/install.sh [--from-source]" >&2; exit 2 ;;
esac

step() {  # step <name> <command...>: run it, print its time
    name=$1; shift
    echo "==> $name"
    t0=$(date +%s)
    "$@"
    echo "==> $name: done in $(( $(date +%s) - t0 )) s"
}
have() { command -v "$1" >/dev/null 2>&1; }

# with_progress <label> <log> <command...>: run a long command with its output in <log>, and print a line every minute
# while it runs (Lean's "[done/total]" count when its log has one); on failure show the log's end
with_progress() {
    label=$1; log=$2; shift 2
    "$@" >"$log" 2>&1 &
    pid=$!
    t0=$(date +%s); every=${VE_PROGRESS_INTERVAL:-60}; next=$every
    while kill -0 "$pid" 2>/dev/null; do
        sleep 1
        elapsed=$(( $(date +%s) - t0 ))
        if [ "$elapsed" -ge "$next" ]; then
            count=$(grep -o '\[[0-9]*/[0-9]*\]' "$log" 2>/dev/null | tail -n 1 || true)
            echo "    $label: still running, $(( elapsed / 60 )) min so far${count:+, $count files}"
            next=$(( next + every ))
        fi
    done
    if wait "$pid"; then tail -n 1 "$log"; rm -f "$log"
    else tail -n 40 "$log"; echo "$label failed; full log: $log" >&2; exit 1; fi
}

need_system() {  # need_system <command...>: stop with the apt-get line when one is missing (never sudo here)
    missing=""
    for tool in "$@"; do
        case $tool in cc) pkg=build-essential ;; *) pkg=$tool ;; esac
        have "$tool" || missing="$missing $pkg"
    done
    [ -z "$missing" ] && { echo "present: $*"; return; }
    echo "Missing system packages:$missing. Install them, then run this again:" >&2
    echo "    sudo apt-get update && sudo apt-get install -y$missing ca-certificates" >&2
    exit 1
}

install_uv() {
    if have uv; then uv --version; return; fi
    curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
    uv --version
}

side_checkout() {  # the after-release checkout at the pinned commit
    if ! git cat-file -e "$PIN^{commit}" 2>/dev/null; then
        git fetch -q origin after-release || true
        git cat-file -e "$PIN^{commit}" 2>/dev/null \
            || { echo "the after-release commit $PIN is not in this repository (fetch branch after-release)" >&2; exit 1; }
    fi
    if [ ! -d "$SIDE" ]; then
        git worktree add -q --detach "$SIDE" "$PIN"
    elif [ "$(git -C "$SIDE" rev-parse HEAD)" != "$(git rev-parse "$PIN^{commit}")" ]; then
        git -C "$SIDE" checkout -q --detach "$PIN"
    fi
    git -C "$SIDE" log -1 --format='after-release checkout at %h (%cd)' --date=short
}

side_lean_build() {
    if [ ! -x "$SIDE/lean/.lake/build/bin/ve_service" ]; then
        mkdir -p "$SIDE/lean"
        cp -a lean/.lake "$SIDE/lean/"
    fi
    with_progress "after-release Lean build" "$(mktemp "${TMPDIR:-/tmp}/ve-tour-lake.XXXXXX")" \
        sh -c 'cd "$1/lean" && lake build' sh "$SIDE"
    if [ "$(git rev-parse HEAD:rust)" = "$(git -C "$SIDE" rev-parse HEAD:rust)" ] && [ -x rust/target/release/ve ]; then
        mkdir -p "$SIDE/rust/target/release"
        cp -p rust/target/release/ve "$SIDE/rust/target/release/ve"
    else
        with_progress "after-release Rust build" "$(mktemp "${TMPDIR:-/tmp}/ve-tour-rust.XXXXXX")" \
            sh -c 'cd "$1" && uv run --frozen python tools/rust_build.py' sh "$SIDE"
    fi
}

prebuilt() {  # rc 3 from prebuilt.py: this commit's sources have no prebuilt programs
    source=${VE_TOUR_PREBUILT:-$(uv run --frozen python tour/prebuilt.py url)}
    status=0
    uv run --frozen python tour/prebuilt.py install "$source" || status=$?
    if [ "$status" = 3 ]; then
        echo "No prebuilt programs for this commit: building from source instead (about an hour)."
        MODE=source
    elif [ "$status" != 0 ]; then
        exit "$status"
    elif [ "$(git rev-parse HEAD:rust)" = "$(git -C "$SIDE" rev-parse HEAD:rust)" ]; then
        mkdir -p "$SIDE/rust/target/release"
        cp -p rust/target/release/ve "$SIDE/rust/target/release/ve"
    fi
}

if [ "$MODE" = prebuilt ]; then
    step "system packages (git, curl)" need_system git curl
    step "uv" install_uv
    step "uv sync --locked" uv sync --locked --inexact
    step "the after-release checkout (.tour-after-release/)" side_checkout
    step "uv sync --locked (after-release)" sh -c 'cd "$1" && uv sync --locked --inexact' sh "$SIDE"
    step "prebuilt checker programs" prebuilt
fi
if [ "$MODE" = source ]; then
    sh usecases/eligibility/demo/install.sh
    step "the after-release checkout (.tour-after-release/)" side_checkout
    step "after-release builds" side_lean_build
    step "uv sync --locked (after-release)" sh -c 'cd "$1" && uv sync --locked --inexact' sh "$SIDE"
fi
echo "==> tour install: all done in $(( $(date +%s) - START )) s"
echo "Next: sh tour/stops/01-yes.sh"
