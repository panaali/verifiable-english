#!/bin/bash
# GitHub Actions aarch64 gate job (2026-10-28 dri-cloudcpu, reviews/cloud-cpu-20261028.md); run as ci-job/job.sh by the
# staged workflow gha/ve-job-arm.yml (ubuntu-24.04-arm). Shadow pilot of the train's aarch64 gate leg: the same steps as
# the Mac runner's mac-gate-job.sh `work` for a merge candidate (MAC_GATE_ONE_AUDIT on: no pre-gate audit), on GitHub's
# Linux arm64 runner instead of the ve-mac-1 Linux arm64 guest:
#   main = <base> (the candidate's first parent: origin/main when its Mac leg ran), pilot/* and codex/e0-rater branches
#   from the exported remote, `uv sync --locked --group dev`, rustup toolchain from rust-toolchain.toml, `cargo fetch
#   --locked` into the checkout's .cargo-home, `lake build` (one retry of a crashed build, as lakebuild()), this runner's
#   checker pins (regen_generated.py --only checker-pins, assume-unchanged, runner-local), a clean-tree check, then
#   `gate-wrap.py --workers <n>` (mac-gate-wrap.py, appended to this file after #GATE-WRAP-BEGIN by gha-arm-gate.sh).
# usage: gate-job.sh run <checkout> <out dir> <job> <head> <base> <asset|-> <sha256|-> <workers> [<shard K/N|->]
# 2026-10-29 dri-actions-gate-arm (gha-arm-shard.sh): a 10th argument K/N runs `gate.py --shard K/N` (main's deterministic share;
# shard 1 also audit, Rust build, cargo test); its record (mode shard) is gate-record.json; gha-arm-shard.sh merges the N.
# Writes timings.tsv (step, rc, seconds), machine.txt, gate.log, lake.log, gate-record.json (the record), done.txt
# ("GATE <rc> lake=<rc>" or "SETUP-FAIL <step>") and DONE (0 = a gate ran, its verdict is in done.txt; 2 = setup failed).
set -u
mode=$1; R=$2; O=$3; JOB=$4; HEAD_SHA=$5; BASE=$6; N=${9:-4}; SHARD=${10:--}
[ "$mode" = run ] || exit 2
sharg=(); if [ "$SHARD" != - ]; then [[ $SHARD =~ ^[1-9][0-9]*/[1-9][0-9]*$ ]] || exit 2; sharg=(--shard "$SHARD"); fi
export PATH=/usr/local/bin:/opt/lean/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH
mkdir -p "$O"; P=$O/timings.tsv; printf 'step\trc\tseconds\n' > "$P"
now(){ date +%s.%N; }
step(){ local name=$1; shift; local t0; t0=$(now); "$@" > "$O/$name.log" 2>&1; local rc=$?
  printf '%s\t%s\t%s\n' "$name" "$rc" "$(awk -v a="$t0" -v b="$(now)" 'BEGIN{printf "%.1f", b-a}')" >> "$P"; return $rc; }
fail(){ echo "SETUP-FAIL $1" > "$O/done.txt"; echo 2 > "$O/DONE"; exit 2; }
{ echo "job=$JOB shard=$SHARD nproc=$(nproc) arch=$(uname -m) host=$(hostname) date=$(date -u +%FT%TZ) ulimit_s=$(ulimit -s)"; free -g | sed -n 2p; df -h / | tail -1; uptime; } > "$O/machine.txt"
cd "$R" || fail cd
[ "$(git rev-parse HEAD)" = "$HEAD_SHA" ] || { echo "HEAD is not $HEAD_SHA" >> "$O/machine.txt"; fail head; }
git cat-file -e "$BASE^{commit}" 2>/dev/null || fail base
git branch -f main "$BASE" > /dev/null 2>> "$O/machine.txt" || fail main
for b in $(git for-each-ref --format='%(refname:lstrip=3)' refs/remotes/origin/pilot/ refs/remotes/origin/codex/e0-rater); do
  git branch -f "$b" "origin/$b" > /dev/null 2>&1; done
echo "pilot/codex branches: $(git for-each-ref --format='%(refname:short)' refs/heads/pilot/ refs/heads/codex/ | wc -l)" >> "$O/machine.txt"
sed -n '/^#GATE-WRAP-BEGIN$/,$p' "$0" | tail -n +2 > "$RUNNER_TEMP/gate-wrap.py"; [ -s "$RUNNER_TEMP/gate-wrap.py" ] || fail gate-wrap
# the account's elan paths, as on the VM and the Mac (R18: test_lake_outputs looks in ~/.elan/bin)
tc=$(cat lean/lean-toolchain); tc=${tc//\//--}; mkdir -p ~/.elan/toolchains ~/.elan/bin
ln -sfn /opt/lean ~/.elan/toolchains/${tc//:/---}; for t in lean lake; do [ -e ~/.elan/bin/$t ] || ln -sfn /opt/lean/bin/$t ~/.elan/bin/$t; done  # lake: dri-maclight (gha-elan-lake)
step rust_toolchain rustup toolchain install "$(sed -nE 's/^channel *= *"([^"]+)".*/\1/p' rust-toolchain.toml)" --profile minimal || fail rust-toolchain
step python_env uv sync -q --locked --group dev || fail sync
CARGO_HOME=$R/.cargo-home step cargo_fetch cargo fetch --locked --manifest-path rust/Cargo.toml || fail cargo-fetch
lb(){ ( cd lean && lake build ); }
step lake lb; lk=$?
if [ $lk -ne 0 ] && ! grep -qE '^error: [^ ]+\.lean:[0-9]+:[0-9]+:|deep recursion was detected' "$O/lake.log"; then
  for m in $(sed -nE "s/.*Building ([A-Za-z0-9_.']+):c\.o.*/\1/p" "$O/lake.log" | sort -u); do rm -f lean/.lake/build/ir/${m//.//}.c.o*; done
  mv "$O/lake.log" "$O/lake-first.log"; step lake lb; lk=$?; fi
if [ $lk -eq 0 ]; then
  step pins uv run python tools/regen_generated.py --write --only checker-pins || fail pins
  git update-index --assume-unchanged lean/checkers.lock
fi
git status --porcelain --untracked-files=all > "$O/dirty.txt"; [ -s "$O/dirty.txt" ] && fail dirty-after-setup
ulimit -s 8192
step gate timeout 19000 uv run python "$RUNNER_TEMP/gate-wrap.py" --workers "$N" "${sharg[@]}"; gt=$?
[ -f gate-result.json ] && cp gate-result.json "$O/gate-record.json"  # not gate-result.json: VE's .gitignore drops that name from the publish commit
grep -E '^\[gate\] (passed|failed|rerun-passed):' "$O/gate.log" | tail -1 >> "$O/machine.txt"
echo "GATE $gt lake=$lk" > "$O/done.txt"; echo 0 > "$O/DONE"; exit 0
#GATE-WRAP-BEGIN
# 2026-10-14 DRI: runner-local wrapper for tools/gate.py on the Mac runner (copied to ve-mac-1:gate-wrap.py by mac-gate.sh;
# run by mac-gate-job.sh as `uv run python ~/gate-wrap.py <gate args>` in the job checkout). It runs the checkout's own
# tools/gate.py unchanged as __main__, with one runner-local addition: when gate.py collects the merge base in a scratch
# worktree (tools/gate_collection.collect_commit -> collect(tree, ...)), that scratch tree first gets THIS runner's
# aarch64 checker pins (tools/regen_generated.py --write --only checker-pins in the tree, as mac-gate-job.sh does for the
# job checkout), because the base's committed lean/checkers.lock lists only the VM's x86 builds (2026-10-14: fix-abbrev
# and fix-subtick gates failed at collection: base-worktree ve_service "has unlisted build"). The scratch tree is
# removed by gate.py afterwards; nothing is committed or pushed. Normally the base's record comes from the VM's
# refs/notes/ve-gate-result (pushed by mac-gate.sh) and no base is collected at all. If the patch cannot be applied the
# gate runs exactly as before.
# 2026-10-14 DRI (pipeline-r2-1014, R3: the nightlies run gate.py without quarantine and with VE_RUN_CACHE=off):
#  - VE_GATE_RUN_CACHE_OFF=1: gate.py builds every stage's environment from nothing (gate_environment, ALLOWED_ENVIRONMENT),
#    so VE_RUN_CACHE cannot be passed from outside and the run cache (tools/run_cache.py: the git common directory's
#    ve-run-cache, shared by the checkout's worktrees) would serve test_wire_gate_corpus's nested run. With the variable
#    the wrapper adds VE_RUN_CACHE=off to gate_environment's result and the name to ALLOWED_ENVIRONMENT (the record's
#    "environment" then shows VE_RUN_CACHE=off). Arguments are passed as given (the nightly adds --no-quarantine).
#  - VE_GATE_NO_RUNNER_PINS=1 (the VM nightly, $M/mac-gate-wrap.py run with `python -I`): no runner-pin hooks.
# 2026-10-15 (fix-fsmonitor-gate F1, DRI signature pending): gate.py's source_identity now checks a clean tree again on a
# fresh index read from the commit, so mac-gate-job.sh's assume-unchanged no longer hides the runner's pins in
# lean/checkers.lock and every Mac gate would stop "worktree is dirty at gate start". When the job checkout marks
# lean/checkers.lock assume-unchanged (mac-gate-job.sh, after writing the pins), the wrapper hashes the file once, at its
# start, and accepts exactly that file with exactly that content: in the stage "worktree content" (the fresh-index status)
# it drops the one line " M lean/checkers.lock" when the file still hashes to the blob taken at the start. Any other line
# (an edit, an untracked file, a staged change) still makes the tree dirty, and so does any later change to the pin file
# itself (gate start and gate end both check it). Adding the blob to the fresh index (update-index --cacheinfo) is not
# enough: status then reports "M  lean/checkers.lock" as staged against HEAD. On a gate.py without that stage the hook
# never fires. The gate is imported as a module (as the nightly path did) so its `command` can be wrapped; if the import
# fails it runs by runpy as before.
import os
import runpy
import subprocess
import sys
from pathlib import Path

PIN = "lean/checkers.lock"


def say(text):
    print(f"[gate-wrap] {text}", file=sys.stderr, flush=True)


def install_base_pins(root):
    """Runner pins for a base worktree gate.py collects (2026-10-14)."""
    from tools import gate_collection

    original = gate_collection.collect

    def collect(tree, *args, **kwargs):
        tree = Path(tree)
        done = subprocess.run([sys.executable, str(tree / "tools/regen_generated.py"), "--write", "--only", "checker-pins"],
                              cwd=tree, env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        say(f"runner-local checker pins for the base worktree {tree}: exit {done.returncode}")
        if done.returncode:
            print(done.stdout[-3000:], file=sys.stderr, flush=True)
        return original(tree, *args, **kwargs)

    gate_collection.collect = collect


def git(root, *args):
    return subprocess.run(["git", "--no-optional-locks", *args], cwd=root, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def pinned_blob(root):
    """The pin file's blob when the checkout hides it (assume-unchanged: tag 'h'), else None."""
    tags = git(root, "ls-files", "-v", "--", PIN).split()
    if tags[:1] != ["h"]:
        return None
    return git(root, "hash-object", "--", PIN).strip()


def install_pin_content(gate_module, root):
    """Accept exactly the pin file, with the content it had at the wrapper's start, in the fresh-index status."""
    blob = pinned_blob(root)
    if blob is None:
        return None
    original = gate_module.command
    # gate.command returns the output stripped, so a first line " M <pin>" arrives as "M <pin>"; no other porcelain
    # line strips to it ("M  <pin>" is staged, "MM <pin>" is staged and edited).
    line = f"M {PIN}"

    def command(args, *, env, stage, **kwargs):
        out = original(args, env=env, stage=stage, **kwargs)
        if stage != "worktree content":
            return out
        now = subprocess.run(["git", "hash-object", "--", PIN], cwd=kwargs.get("cwd", root), env=env, text=True,
                             stdout=subprocess.PIPE).stdout.strip()
        if now != blob:  # even back to the commit's content: the gate ran with other pins
            say(f"{PIN} changed since the wrapper started ({blob} -> {now or 'unreadable'}): dirty")
            return out or f"{PIN} changed since the wrapper started"
        lines = out.splitlines()
        if line not in [x.strip() for x in lines]:
            return out
        say(f"{PIN} differs from the commit by this runner's pins only (blob {blob}, taken at the wrapper's start)")
        return "\n".join(x for x in lines if x.strip() != line).strip()

    gate_module.command = command
    say(f"{PIN} is this runner's (assume-unchanged); the gate accepts it only as blob {blob}")
    return blob


def run_cache_off(gate_module):
    base_environment = gate_module.gate_environment

    def gate_environment(scratch):
        env = base_environment(scratch)
        env["VE_RUN_CACHE"] = "off"
        return env

    gate_module.gate_environment = gate_environment
    gate_module.ALLOWED_ENVIRONMENT = (*gate_module.ALLOWED_ENVIRONMENT, "VE_RUN_CACHE")
    say("VE_RUN_CACHE=off in the gate's own environment (nightly)")


def main():
    root = Path.cwd().resolve()
    gate = root / "tools" / "gate.py"
    sys.path.insert(0, str(root))
    sys.argv = [str(gate), *sys.argv[1:]]
    runner_pins = os.environ.get("VE_GATE_NO_RUNNER_PINS") != "1"
    if runner_pins:
        try:
            install_base_pins(root)
        except Exception as exc:  # the gate itself decides; the wrapper never blocks it
            say(f"base-worktree pin hook not installed: {exc!r}")
    try:
        from tools import gate as gate_module
    except Exception as exc:
        if os.environ.get("VE_GATE_RUN_CACHE_OFF") == "1":
            raise
        say(f"tools.gate not importable ({exc!r}); running it by runpy, without the pin-content hook")
        runpy.run_path(str(gate), run_name="__main__")
        return 0
    if runner_pins:
        try:
            install_pin_content(gate_module, root)
        except Exception as exc:  # without the hook the gate refuses the runner's pins: a runner failure, not a pass
            say(f"pin-content hook not installed: {exc!r}")
    if os.environ.get("VE_GATE_RUN_CACHE_OFF") == "1":
        run_cache_off(gate_module)
    return gate_module.main()


if __name__ == "__main__":
    raise SystemExit(main())
