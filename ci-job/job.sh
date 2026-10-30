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
# 2026-10-30 dri-arm-lean-cache (flag ARM_LEAN_CACHE, backlog arm-lean-cache): when the dispatcher (gha-arm-gate.sh,
# gha-arm-shard.sh) appends ve-cache.sh after a line #VE-CACHE-SH-BEGIN (after gate-wrap.py), step cache_restore restores
# the aarch64 Lean build before `lake build`: ve-cache.sh restore lean-build of the EXACT key only (an asset of this lean/
# tree; none: cold build; no seed from another tree), with every restore's checks (sha256, member names, platform and
# toolchain seal; any failure leaves lean/.lake untouched and the build is cold). Report ve-cache.json,
# log cache_restore.log; the dispatcher's guard (gha/arm-cache-guard.sh -> ve-cache-guard.sh) reads them.
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
awk 'f && /^#VE-CACHE-SH-BEGIN$/ {exit} f; /^#GATE-WRAP-BEGIN$/ {f=1}' "$0" > "$RUNNER_TEMP/gate-wrap.py"; [ -s "$RUNNER_TEMP/gate-wrap.py" ] || fail gate-wrap
# the account's elan paths, as on the VM and the Mac (R18: test_lake_outputs looks in ~/.elan/bin)
tc=$(cat lean/lean-toolchain); tc=${tc//\//--}; mkdir -p ~/.elan/toolchains ~/.elan/bin
ln -sfn /opt/lean ~/.elan/toolchains/${tc//:/---}; for t in lean lake; do [ -e ~/.elan/bin/$t ] || ln -sfn /opt/lean/bin/$t ~/.elan/bin/$t; done  # lake: dri-maclight (gha-elan-lake)
step rust_toolchain rustup toolchain install "$(sed -nE 's/^channel *= *"([^"]+)".*/\1/p' rust-toolchain.toml)" --profile minimal || fail rust-toolchain
step python_env uv sync -q --locked --group dev || fail sync
CARGO_HOME=$R/.cargo-home step cargo_fetch cargo fetch --locked --manifest-path rust/Cargo.toml || fail cargo-fetch
if grep -q -x '#VE-CACHE-SH-BEGIN' "$0"; then
  sed -n '/^#VE-CACHE-SH-BEGIN$/,$p' "$0" | tail -n +2 > "$RUNNER_TEMP/ve-cache.sh"
  export VE_CACHE_DIR=$RUNNER_TEMP/ve-cache
  # exact key only (a gate leg decides merges; lean_share restores exact keys only too): the public manifest cut down to
  # this lean/ tree's assets, so ve-cache.sh restores the exact build or none (cold: "no lean-build asset")
  if curl -sSfL --retry 2 --max-time 60 -o "$RUNNER_TEMP/ve-cache-all.json" https://github.com/panaali/verifiable-english/releases/download/ve-cache/ve-cache-manifest.json \
     && python3 -I -c 'import json,sys; m=json.load(open(sys.argv[1])); m["assets"]=[a for a in m.get("assets",[]) if a.get("key")==sys.argv[3]]; json.dump(m,open(sys.argv[2],"w"))' \
          "$RUNNER_TEMP/ve-cache-all.json" "$RUNNER_TEMP/ve-cache-exact.json" "$(git rev-parse HEAD:lean)"; then
    step cache_restore bash "$RUNNER_TEMP/ve-cache.sh" restore lean-build --repo "$R" --manifest "$RUNNER_TEMP/ve-cache-exact.json" --report "$O/ve-cache.json"
    tail -n 1 "$O/cache_restore.log" >> "$O/machine.txt"
  else echo "ve-cache: the public manifest did not download: cold build" >> "$O/machine.txt"; fi
fi
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
#VE-CACHE-SH-BEGIN
#!/bin/bash
# ve-cache.sh: the ONE restore script for VE's shared caches, the same file in every place VE work runs (the VM, the Mac
# runner, Claude cloud ve-runner, Codex Cloud ve-runner-codex, GitHub Actions). 2026-10-28 dri-sharedcache,
# reviews/shared-cache-20261028.md. Portable bash (no bash-4-only features), needs curl, python3, zstd, tar, sha256sum or shasum.
# usage: ve-cache.sh restore lean-build [--repo DIR] [--base SHA] [--url URL --sha256 HEX] [--manifest FILE|URL] [--report FILE]
#        ve-cache.sh prefetch lean-build [--manifest FILE|URL]     (setup phase: download + verify into the store only)
#        ve-cache.sh list [--manifest FILE|URL]
#        ve-cache.sh bundle <job script> <out>   (VM: <job script>, a marker line #VE-CACHE-SH-BEGIN, then this file;
#          a job script that finds the marker in "$0" extracts this file and restores through it: one file to ship)
# Assets are content-addressed: kind lean-build = main's checked Lean build (lean_share entry: lake/ + pins.json), keyed
# by the git tree id of lean/ (`git rev-parse HEAD:lean`), published by lean-cache-publish.sh and listed with
# platform and toolchain in the public manifest (ve-cache-publish.sh: release ve-cache, ve-cache-manifest.json).
# restore picks, among manifest entries of this platform and this checkout's lean/lean-toolchain: the entry whose key is
# HEAD:lean ("exact"), else the one built at --base (VM or exported sha), else the nearest one at an ancestor of HEAD,
# else the newest ("seed": Lake's own traces rebuild whatever differs; the caller's `lake build` always runs after).
# --url/--sha256 pin one asset instead (the VM dispatcher's choice). Every use is checked, never silent:
#   the sha256 of the file (a local copy is used only when its sha256 matches; downloads land as .part, then verified);
#   member names (no absolute or .. paths; lake/build/ and pins.json present);
#   the seal (pins.json): its platform is this machine's, its toolchain.lean is `lean --version` here (when lean runs).
# Any failure: lean/.lake untouched, one line saying why (the caller builds cold). Exit 0: restored, one line
# `ve-cache: lean-build <exact|seed> ...`; --report FILE gets the same facts as JSON (kind, status restored, match, key,
# asset, sha256, source local|download, seconds). 2026-10-28 dri-advfix5 (ADV-20261028T0336-1): failures are classed,
# and --report gets {status, class, reason, asset, sha256, platform, lean} for each, so the VM's guard (ve-cache-guard.sh)
# can tell a correct refusal from a broken mechanism:
#   exit 3 status cold: nothing wrong with any asset (no asset named or none for this platform/toolchain; class
#     "download" when the download failed: one is cold, repeated ones are a mechanism failure for the guard);
#   exit 4 status refused: VALIDATION refused the asset (asset name, sha256, member names, platform or toolchain seal):
#     the guard quarantines the asset and keeps SHARED_CACHE on;
#   exit 5 status error: the mechanism itself (a tool missing, no store or temp dir, manifest unreadable or the pick
#     failed, extraction or the move failed): the guard removes SHARED_CACHE. Exit 2: usage (also a mechanism failure).
# Quarantined assets (the manifest's "quarantined" list, or an entry marked "quarantined") are never picked.
# 2026-10-28 dri-tmshard (backlog cache-manifest-404): a pinned --url that GitHub no longer serves (HTTP 404/410; file://:
# absent) is said ("pinned asset X is gone") and replaced by the manifest's pick (exact, base, ancestor, newest; never
# the gone one), same checks; none: exit 3 status cold class gone. The report then carries pinned_gone: X.
# The store: $VE_CACHE_DIR, else the first writable of /opt/ve-cache,
# /workspace/.tools/ve-cache, ${XDG_CACHE_HOME:-~/.cache}/ve-cache; read-only search also in ~/.cache/ve-cloud-cache (the
# VM's packs). Tests only: VE_CACHE_SEARCH (extra dirs, colon-separated), VE_CACHE_LEAN (the lean to ask for --version).
set -u
DEFAULT_MANIFEST=https://github.com/panaali/verifiable-english/releases/download/ve-cache/ve-cache-manifest.json
say(){ echo "ve-cache: $*" >&2; }
report=""; name=""; want_sha=""; LEANV=""
rep(){ [ -n "$report" ] && python3 -I -c 'import json,sys; k=["kind","status","class","reason","asset","sha256","platform","lean"]
json.dump(dict(zip(k, sys.argv[2:])), open(sys.argv[1], "w"))' "$report" lean-build "$1" "$2" "$3" "$name" "$want_sha" "$platform" "$LEANV" 2> /dev/null; }
die(){ say "$1"; [ "${2:-3}" = 3 ] && rep cold "${3:-none}" "$1"; exit "${2:-3}"; }   # exit 3: cold, no asset at fault
refuse(){ say "$1"; rep refused "$2" "$1"; exit 4; }   # validation refused this asset: quarantine it
broken(){ say "$1"; rep error mechanism "$1"; exit 5; }   # the mechanism failed: the guard removes SHARED_CACHE
sha(){ if command -v sha256sum > /dev/null; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }
now(){ python3 -c 'import time; print("%.1f" % time.time())'; }
platform="$(uname -s)-$(uname -m)"
cmd=${1:-}; shift || true
if [ "$cmd" = bundle ]; then [ $# = 2 ] && [ -f "$1" ] || die "usage: ve-cache.sh bundle <job script> <out>" 2
  grep -q -x '#VE-CACHE-SH-BEGIN' "$1" && die "$1 already carries a bundle" 2
  { cat "$1"; echo '#VE-CACHE-SH-BEGIN'; cat "$0"; } > "$2.part" && mv "$2.part" "$2" || die "cannot write $2" 2; exit 0; fi
kind=""; case $cmd in restore|prefetch) kind=${1:-}; shift || true;; list) ;; *) die "usage: ve-cache.sh restore|prefetch lean-build [...] | list" 2;; esac
[ -z "$kind" ] && [ "$cmd" != list ] && die "usage: ve-cache.sh $cmd lean-build [...]" 2
[ -n "$kind" ] && [ "$kind" != lean-build ] && die "unknown kind $kind (known: lean-build)" 2
R=$PWD; base=""; url=""; want_sha=""; man=${VE_CACHE_MANIFEST:-$DEFAULT_MANIFEST}; report=""
while [ $# -gt 0 ]; do case $1 in
  --repo) R=$2; shift 2;; --base) base=$2; shift 2;; --url) url=$2; shift 2;; --sha256) want_sha=$2; shift 2;;
  --manifest) man=$2; shift 2;; --report) report=$2; shift 2;; *) die "unknown option $1" 2;; esac; done
[ -n "$url" ] && [ -z "$want_sha" ] && die "--url needs --sha256" 2
[ "$url" = - ] && die "no asset named (-): cold build"
for t in curl python3 zstd tar git; do command -v $t > /dev/null || broken "missing tool: $t"; done
store=${VE_CACHE_DIR:-}
if [ -z "$store" ]; then for d in /opt/ve-cache /workspace/.tools/ve-cache "${XDG_CACHE_HOME:-$HOME/.cache}/ve-cache"; do
  if mkdir -p "$d/lean-build" 2> /dev/null && [ -w "$d/lean-build" ]; then store=$d; break; fi; done; fi
[ -n "$store" ] || broken "no writable store directory"
mkdir -p "$store/lean-build" || broken "cannot create $store/lean-build"
search="$store/lean-build:/opt/ve-cache/lean-build:/workspace/.tools/ve-cache/lean-build:${XDG_CACHE_HOME:-$HOME/.cache}/ve-cache/lean-build:$HOME/.cache/ve-cloud-cache:${VE_CACHE_SEARCH:-}"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/ve-cache.XXXXXX") || broken "no temp dir"; trap 'rm -rf "$tmp"' EXIT
t0=$(now)

getman(){ # the manifest into $tmp/manifest.json
  case $man in
    http://*|https://*) curl -sSfL --retry 2 --max-time 60 -o "$tmp/manifest.json" "$man" || return 1;;
    *) cp "$man" "$tmp/manifest.json" 2> /dev/null || return 1;; esac
  python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d.get("format")==1 and isinstance(d.get("assets"),list)' "$tmp/manifest.json" 2> /dev/null; }
# 2026-10-28 dri-advfix5: an entry is usable unless quarantined (marked, or its name + sha256 in the "quarantined" list)

if [ "$cmd" = list ]; then getman || broken "manifest $man unreadable"
  python3 -I -c 'import json,sys
for a in json.load(open(sys.argv[1]))["assets"]:
    print(a["kind"], a["key"][:12], a["name"], a["bytes"], a["platform"], a["toolchain"], a.get("main","")[:9], a.get("packed_at",""))' "$tmp/manifest.json"; exit 0; fi

# --- choose the asset: name, url, sha256, key, match
want_tree=""; toolchain=""
if [ "$cmd" = restore ]; then
  [ -d "$R/lean" ] || die "$R has no lean/ directory" 2
  want_tree=$(git -C "$R" rev-parse -q --verify HEAD:lean 2> /dev/null) || die "no HEAD:lean in $R" 2
  toolchain=$(tr -d '[:space:]' < "$R/lean/lean-toolchain" 2> /dev/null)
fi
pinned_gone=""
choose(){ # the manifest's pick into name, url, want_sha, key, match; $1: a gone asset name never to pick
  if ! getman; then [ -n "${1:-}" ] && die "pinned asset $1 is gone and the manifest $man is unreadable: cold build" 3 gone
    broken "manifest $man unreadable: cold build"; fi
  pick=$(python3 -I - "$tmp/manifest.json" "$platform" "$toolchain" "$want_tree" "$base" "$R" "$cmd" "${1:-}" <<'PY'
import json, subprocess, sys
path, platform, toolchain, tree, base, repo, cmd, skip = sys.argv[1:9]
m = json.load(open(path))
q = {(x.get("name"), x.get("sha256")) for x in m.get("quarantined", []) if isinstance(x, dict)}
a = [x for x in m["assets"] if x.get("kind") == "lean-build" and x.get("url") and not x.get("quarantined")
     and (x.get("name"), x.get("sha256")) not in q and x.get("name") != skip
     and x.get("platform") == platform and (not toolchain or x.get("toolchain") == toolchain)]
def anc(c):
    return bool(c) and subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", c, "HEAD"],
                                      capture_output=True).returncode == 0
def dist(c):
    r = subprocess.run(["git", "-C", repo, "rev-list", "--count", c + "..HEAD"], capture_output=True, text=True)
    return int(r.stdout) if r.returncode == 0 else 10**9
hit, match = None, None
if cmd == "restore":
    hit = next((x for x in a if tree and x["key"] == tree), None); match = "exact"
    if hit is None and base:
        hit = next((x for x in a if base in (x.get("main"), x.get("main_export"))), None); match = "seed-base"
    if hit is None:
        c = [(dist(m), x) for x in a for m in (x.get("main"), x.get("main_export")) if anc(m)]
        hit = min(c, key=lambda t: t[0])[1] if c else None; match = "seed-ancestor"
if hit is None and a:
    hit, match = a[0], ("seed-newest" if cmd == "restore" else "newest")
if hit:
    print("\t".join([hit["name"], hit["url"], hit["sha256"], hit["key"], match]))
PY
) || broken "manifest pick failed"
  [ -n "$pick" ] || { [ -n "$pinned_gone" ] && die "pinned asset $pinned_gone is gone and the manifest has no other lean-build asset for $platform ${toolchain:-?}: cold build" 3 gone
    die "no lean-build asset for $platform ${toolchain:-?} in the manifest: cold build"; }
  IFS=$'\t' read -r name url want_sha key match <<< "$pick"; }
gone(){ local c; case $1 in  # the asset is no longer served (not a passing network error)
  file://*) [ ! -e "${1#file://}" ];;
  http://*|https://*) c=$(curl -sIL --max-time 30 -o /dev/null -w '%{http_code}' "$1" 2> /dev/null); [ "$c" = 404 ] || [ "$c" = 410 ];;
  *) return 1;; esac; }
fetch(){ # a verified local copy, else a download into .part (verified below); 1: the download failed
  case $name in lean-build-*.tar.zst) ;; *) refuse "unexpected asset name $name: refused, cold build" name;; esac
  file=""; src=local; IFS=: read -r -a dirs <<< "$search"
  for d in "${dirs[@]}"; do [ -n "$d" ] && [ -s "$d/$name" ] || continue
    [ "$(sha "$d/$name")" = "$want_sha" ] && { file=$d/$name; return 0; }
    say "local $d/$name has another sha256: ignored"; done
  src=download; curl -sSfL --retry 2 -o "$store/lean-build/$name.part" "$url" || { rm -f "$store/lean-build/$name.part"; return 1; }; }
if [ -n "$url" ]; then name=$(basename "$url"); key=""; match=pinned; else choose; fi

# --- a verified local copy, else a verified download
if ! fetch; then
  if [ "$match" = pinned ] && gone "$url"; then pinned_gone=$name
    say "pinned asset $name is gone (no longer served at $url): taking the manifest's pick instead"
    choose "$pinned_gone"; fetch || die "download of $name failed: cold build" 3 download
  else die "download of $name failed: cold build" 3 download; fi
fi
if [ -z "$file" ]; then
  got=$(sha "$store/lean-build/$name.part")
  [ "$got" = "$want_sha" ] || { rm -f "$store/lean-build/$name.part"; refuse "sha256 of the downloaded $name is ${got:0:12}, not ${want_sha:0:12}: refused, cold build" sha256; }
  mv "$store/lean-build/$name.part" "$store/lean-build/$name"; file=$store/lean-build/$name
  for old in $(ls -t "$store"/lean-build/lean-build-*.tar.zst 2> /dev/null | tail -n +3); do rm -f "$old"; done
fi
if [ "$cmd" = prefetch ]; then say "prefetched $name (sha256 ${want_sha:0:12} ok, $src) into ${file%/*}"; exit 0; fi

# --- member names, then extraction, then the seal
zstd -dc "$file" | tar -t > "$tmp/list" 2> /dev/null || refuse "$name does not list: refused, cold build" members
grep -q -E '^/|(^|/)\.\.(/|$)' "$tmp/list" && refuse "$name has an absolute or .. member: refused, cold build" members
grep -q -x 'pins.json' "$tmp/list" && grep -q '^lake/build/' "$tmp/list" || refuse "$name lacks pins.json or lake/build/: refused, cold build" members
L=$R/lean/.cache/ve-cache-restore; rm -rf "$L"; mkdir -p "$L" || broken "cannot create $L"
zstd -dc "$file" | tar -x -C "$L" 2> "$tmp/x.err" || { rm -rf "$L"; broken "extracting $name failed: $(head -c 200 "$tmp/x.err")"; }
LEANV=$("${VE_CACHE_LEAN:-lean}" --version 2> /dev/null | head -1)
if ! seal=$(python3 -I - "$L/pins.json" "$(uname -s)" "$(uname -m)" "$LEANV" 2>&1 <<'PY'
import json, sys
k = json.load(open(sys.argv[1]))["key"]; system, machine, leanv = sys.argv[2:5]
p = k.get("platform", {})
if (p.get("system"), p.get("machine")) != (system, machine):
    sys.exit("seal platform %s-%s is not %s-%s" % (p.get("system"), p.get("machine"), system, machine))
if leanv and k.get("toolchain", {}).get("lean") != leanv:
    sys.exit("seal toolchain %r is not this lean %r" % (k.get("toolchain", {}).get("lean"), leanv))
print("seal ok" if leanv else "seal platform ok (no lean here to compare)")
PY
); then rm -rf "$L"; refuse "$name refused: $(printf %s "$seal" | tail -n 1 | head -c 200), cold build" seal; fi
chmod -R u+w "$L" && rm -rf "$R/lean/.lake/build" && mkdir -p "$R/lean/.lake" && mv "$L/lake/build" "$R/lean/.lake/build" \
  || { rm -rf "$L"; broken "moving the build into $R/lean/.lake failed"; }
rm -rf "$L"
secs=$(python3 -c "import sys; print('%.1f' % (float(sys.argv[2]) - float(sys.argv[1])))" "$t0" "$(now)")
[ "$match" = pinned ] && { [ "${name#lean-build-}" = "${want_tree:0:12}.tar.zst" ] && match=exact || match=seed-pinned; }
say "lean-build $match key ${want_tree:0:12} asset $name sha256 ${want_sha:0:12} ok, $seal, from $src, ${secs} s${pinned_gone:+ (pinned $pinned_gone was gone: manifest pick)}"
if [ -n "$report" ]; then python3 -I -c 'import json,sys; k=["kind","status","match","key","asset","sha256","source","seconds","platform","pinned_gone"]
json.dump(dict(zip(k, sys.argv[2:])), open(sys.argv[1], "w"))' "$report" lean-build restored "$match" "$want_tree" "$name" "$want_sha" "$src" "$secs" "$platform" "$pinned_gone"; fi
exit 0
