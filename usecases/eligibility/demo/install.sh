#!/bin/sh
# Install the Winter Fuel Payment demo on a fresh Ubuntu machine (release B, checklist item 5; DEMO.md).
#
# Run from the repository root:  sh usecases/eligibility/demo/install.sh
#
# First the prerequisites, each only if it is missing: a C toolchain, curl and git (apt-get, with sudo when not
# root), uv (Python and its packages), elan (Lean) and rustup (Rust). Then the three build commands of the VE
# README: uv sync --locked, (cd lean && lake build), uv run python tools/rust_build.py. Safe to run again: present
# tools are kept and the builds only redo what changed. Prints each step's time in seconds.
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

system_packages() {
    missing=""
    have cc || missing="$missing build-essential"
    have curl || missing="$missing curl"
    have git || missing="$missing git"
    if [ -z "$missing" ]; then echo "C toolchain, curl and git present"; return; fi
    have apt-get || { echo "install.sh: missing$missing and no apt-get; install them and run again" >&2; exit 1; }
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

install_rustup() {
    if have rustup; then rustup --version 2>/dev/null; return; fi
    curl -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path --profile minimal --default-toolchain none
    rustup --version 2>/dev/null
}

rust_toolchain() {  # the toolchain rust-toolchain.toml pins (newer rustup no longer installs it on first use)
    rustup toolchain install 2>/dev/null || rustup show active-toolchain
}

lake_build() {  # Lean prints a line per checked example; keep them in a log and show the end
    log="${TMPDIR:-/tmp}/ve-demo-lake-build.log"
    if (cd lean && lake build) >"$log" 2>&1; then tail -n 1 "$log"; else tail -n 40 "$log"; echo "lake build failed; full log: $log" >&2; exit 1; fi
}

step "system packages (C toolchain, curl, git)" system_packages
step "uv" install_uv
step "elan (Lean)" install_elan
step "rustup (Rust)" install_rustup
step "rust toolchain (rust-toolchain.toml)" rust_toolchain
# --inexact: keep packages already in .venv (a developer's dev group), so running this again never removes them
step "uv sync --locked" uv sync --locked --inexact
step "lake build (Lean; the first build is the long one)" lake_build
step "rust build" uv run python tools/rust_build.py

echo "==> all steps done in $(( $(date +%s) - START )) s"
echo "Next (DEMO.md step 4): uv run python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json"
echo "If uv is not found in a new shell, run first: export PATH=\"\$HOME/.local/bin:\$PATH\""
