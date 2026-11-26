#!/bin/sh
# Install the Winter Fuel Payment demo on a fresh Ubuntu machine (the steps of usecases/eligibility/DEMO.md).
#
# Run from the repository root:  sh usecases/eligibility/demo/install.sh
#
# First the prerequisites, each only if it is missing: a C toolchain, curl and git (apt-get, with sudo when not
# root), uv (Python and its packages), elan (Lean) and rustup (Rust). Then the three build commands of the VE
# README: uv sync --locked, (cd lean && lake build), uv run python tools/rust_build.py. Safe to run again: present
# tools are kept and the builds only redo what changed. Prints each step's time in seconds, and a line every minute
# while a build runs. VE_NO_SUDO=1 (set by tour/install.sh): never sudo; a missing system package stops the install
# with the apt-get command to run.
# The Lean and Rust versions come from lean/lean-toolchain and rust-toolchain.toml; Python packages from uv.lock.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
cd "$ROOT"
[ -f lean/lean-toolchain ] && [ -f uv.lock ] || { echo "install.sh: $ROOT is not the VE repository root" >&2; exit 1; }

export PATH="$HOME/.local/bin:$HOME/.elan/bin:$HOME/.cargo/bin:$PATH"
START=$(date +%s)
step() {  # step <name> <command...>: run it, print its time
    name=$1; shift
    echo "==> $name"
    t0=$(date +%s)
    "$@"
    echo "==> $name: done in $(( $(date +%s) - t0 )) s"
}
have() { command -v "$1" >/dev/null 2>&1; }
# newlog <name>: a new, private log file for one step (a fresh name each run, so another user's log in the same
# temporary directory is never in the way); removed when the step succeeds, its path printed when it fails
newlog() { mktemp "${TMPDIR:-/tmp}/ve-demo-$1.XXXXXX"; }

system_packages() {
    missing=""
    have cc || missing="$missing build-essential"
    have curl || missing="$missing curl"
    have git || missing="$missing git"
    if [ -z "$missing" ]; then echo "C toolchain, curl and git present"; return; fi
    have apt-get || { echo "install.sh: missing$missing and no apt-get; install them and run again" >&2; exit 1; }
    if [ "${VE_NO_SUDO:-}" = 1 ]; then
        echo "Missing system packages:$missing. Install them, then run this again:" >&2
        echo "    sudo apt-get update && sudo apt-get install -y$missing ca-certificates" >&2
        exit 1
    fi
    SUDO=""; [ "$(id -u)" = 0 ] || SUDO=sudo
    $SUDO apt-get update -q
    # shellcheck disable=SC2086
    DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y -q $missing ca-certificates
}

install_uv() {
    if have uv; then uv --version; return; fi
    curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
    uv --version
}

install_elan() {
    if have elan; then elan --version; return; fi
    curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
        | sh -s -- -y --no-modify-path --default-toolchain none
    elan --version
}

install_rustup() {  # rustup's installer ends by asking you to put Cargo's bin directory in PATH: this script and
    # the demo do not need that, so its output goes to a log (shown only if it fails)
    if have rustup; then rustup --version 2>/dev/null; return; fi
    log=$(newlog rustup-install)
    # a failed download leaves sh an empty script (exit 0), so success also needs rustup to be there afterwards
    if curl -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path --profile minimal --default-toolchain none >"$log" 2>&1 \
        && have rustup
    then rm -f "$log"; echo "rustup installed (nothing to add to your PATH for the demo)"
    else tail -n 20 "$log"; echo "rustup install failed; full log: $log" >&2; exit 1; fi
    rustup --version 2>/dev/null
}

rust_toolchain() {  # the toolchain rust-toolchain.toml pins (newer rustup no longer installs it on first use)
    rustup toolchain install 2>/dev/null || rustup show active-toolchain
}

# with_progress <label> <log> <command...>: run a long build with its output in <log>, print a line every minute while
# it runs (Lean's "[done/total]" count when its log has one), then the log's last line; on failure show its end
with_progress() {
    label=$1; log=$2; shift 2
    "$@" >"$log" 2>&1 &
    pid=$!
    t0=$(date +%s); every=${VE_PROGRESS_SECONDS:-60}; next=$every
    while kill -0 "$pid" 2>/dev/null; do
        sleep 1
        elapsed=$(( $(date +%s) - t0 ))
        if [ "$elapsed" -ge "$next" ]; then
            count=$(grep -o '\[[0-9]*/[0-9]*\]' "$log" 2>/dev/null | tail -n 1 || true)
            echo "    $label: still running, $(( elapsed / 60 )) min so far${count:+, $count files}"
            next=$(( next + every ))
        fi
    done
    if wait "$pid"; then tail -n 1 "$log"; rm -f "$log"; else tail -n 40 "$log"; echo "$label failed; full log: $log" >&2; exit 1; fi
}

lake_build() {  # Lean prints a line per checked example; keep them in a log and show the end
    echo "The first Lean build takes 20 to 40 minutes (a line every minute while it runs); a later run takes seconds."
    with_progress "lake build" "$(newlog lake-build)" sh -c 'cd lean && lake build'
}

rust_build() {
    with_progress "rust build" "$(newlog rust-build)" uv run python tools/rust_build.py
}

step "system packages (C toolchain, curl, git)" system_packages
step "uv" install_uv
step "elan (Lean)" install_elan
step "rustup (Rust)" install_rustup
step "rust toolchain (rust-toolchain.toml)" rust_toolchain
# --inexact: keep packages already in .venv (a developer's dev group), so running this again never removes them
step "uv sync --locked" uv sync --locked --inexact
step "lake build (Lean; the first build is the long one)" lake_build
step "rust build" rust_build

echo "==> all steps done in $(( $(date +%s) - START )) s"
echo "Next (DEMO.md step 4): uv run python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json"
echo "If uv is not found in a new shell, run first: export PATH=\"\$HOME/.local/bin:\$PATH\""
