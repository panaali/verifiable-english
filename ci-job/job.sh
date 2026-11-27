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
# usage: gate-job.sh run <checkout> <out dir> <job> <head> <base> <asset|-> <sha256|-> <workers> [<shard K/N|-> [authority]]
# 2026-10-31 dri-nightly-x86-actions (backlog nightly-x86-actions, DRI ruling E-b, reviews/escalations-20261031.md 07:04Z): an
# 11th argument `authority` (gha-arm-shard.sh --x86, ubuntu-24.04: the nightly x86 pin authority) runs the gate as the VM
# nightly does: NO runner pins (the committed lean/checkers.lock must list this runner's x86 builds: no regen, no
# assume-unchanged; mac-gate-wrap.py VE_GATE_NO_RUNNER_PINS=1), VE_RUN_CACHE=off in the gate's own environment
# (VE_GATE_RUN_CACHE_OFF=1), `python -I`, --no-quarantine. Without it the job is exactly as before.
# 2026-10-31 dri-nightly-x86-actions (validation run 1: shards 2..8 all "needs the pinned Rust binary"): on x86_64 nothing
# rewrites the pins, so nothing builds rust/target/release/ve before the gate, and gate.py --shard K/N with K >= 2 needs
# it pinned (only shard 1 builds Rust). So every x86_64 shard K >= 2 (authority or not) first runs step rust_pin,
# `tools/rust_build.py --check`: VE's reproducible release build (remapped paths) that fails unless lean/checkers.lock pins
# its hash (SETUP-FAIL rust-pin: a missing shard, never a pass). Shard 1 and unsharded jobs build and check it in the gate.
# 2026-10-29 dri-actions-gate-arm (gha-arm-shard.sh): a 10th argument K/N runs `gate.py --shard K/N` (main's deterministic share;
# shard 1 also audit, Rust build, cargo test); its record (mode shard) is gate-record.json; gha-arm-shard.sh merges the N.
# 2026-10-30 dri-arm-lean-cache (flag ARM_LEAN_CACHE, backlog arm-lean-cache): when the dispatcher (gha-arm-gate.sh,
# gha-arm-shard.sh) appends ve-cache.sh after a line #VE-CACHE-SH-BEGIN (after gate-wrap.py), step cache_restore restores
# the aarch64 Lean build before `lake build`: ve-cache.sh restore lean-build of the EXACT key only (an asset of this lean/
# tree; none: cold build; no seed from another tree), with every restore's checks (sha256, member names, platform and
# toolchain seal; any failure leaves lean/.lake untouched and the build is cold). Report ve-cache.json,
# log cache_restore.log; the dispatcher's guard (gha/arm-cache-guard.sh -> ve-cache-guard.sh) reads them.
# 2026-10-31 actions-gate-x86 (gha-arm-shard.sh --x86, VE ve-job.yml v3: the Lean build once per sharded gate):
# (a) when the workflow hands over $VE_LEAN_FROM (the pack of the dispatch's own build-once job; the workflow already
# checked its name and sha256), step lean_from restores it before `lake build`: its seal must name this HEAD:lean, then
# ve-cache.sh restore --url file://<pack> --sha256 $VE_LEAN_FROM_SHA256 with an EMPTY manifest (sha256, member names,
# platform and toolchain seal; never a seed from elsewhere), report lean-from.json; only match exact counts, anything else
# leaves lean/.lake/build absent (cold build). The manifest restore below is then skipped. (b) On x86_64 the checker pins
# are never rewritten (with or without `authority`): x86 is the pins authority, so every x86 gate checks the committed
# lean/checkers.lock, as the VM's x86 leg does.
# 2026-11-09 dri-trainfix-seed (train bottleneck fix 3, backlog train-arm-seed-lean, flag ARM_GATE_SEED read by the
# dispatcher gha-arm-shard.sh). TRUST: DRI ruling 2026-11-09 at the end of reviews/train-bottleneck-20261109.md, item 3
# (SIGNED trial to 2026-11-16T16:00Z): "the aarch64 shards reuse the nearest main Lean build; guard = a cold-build comparison
# on 1 leg in 5". That ruling replaces, for the train's candidate gate legs only, the "exact key only" rule above. The mode
# comes from the LAST line of this job file when it is exactly a line VE-GATE-SEED=<mode> preceded by '#' (the dispatcher
# appends it; none = "-": everything exactly as before; never with `authority`):
#   seed     the restore takes ve-cache.sh's own pick order over the public manifest cut down to the assets of this lean/
#            tree or of a main commit that is an ANCESTOR of HEAD (exact, seed-base = --base <the candidate's main base>,
#            seed-ancestor); a pick of any other kind (seed-newest: a non-ancestor build) is removed again (cold). Every
#            restore check stays (sha256, member names, platform + toolchain seal: ve-cache.sh). Then build artifacts of
#            modules whose .lean source is not in this checkout are removed (lib/lean, ir: a deleted module's stale .olean
#            must not satisfy an import), and `lake build` as before rebuilds what differs (Lake's traces).
#            machine.txt says "seed: match=exact|seed-base|seed-ancestor|cold ..." and "seed: lake <s> s"; seed.json holds
#            {seed, match, asset, pruned, lake_rc, lake_s, seed_commit, rebuilt, stale}. The stale-build check (after
#            `lake build`): every module the candidate adds or changes against the seed's main commit must have a new Lake
#            .trace; one that kept the seed's is stale: the seed is removed and the build redone cold (see below).
#   seed-fp  seed, and the LAST shard (K = N) also writes the Lean fingerprint fp.json right after `lake build` (below).
#   cold-fp  the cold shadow (the guard): no restore at all, `lake build`, the fingerprint, then done.txt "SHADOW lake=<rc>"
#            and exit 0 before any gate (no pins, no tests; it never decides a leg).
# The fingerprint (fp.json, fp-oleans.txt): lake rc; sha256 of every .olean (fp-oleans.txt) and of the .olean of each module
# the candidate changes against <base>; then tools/lean_statements.py and lean/audit.py --write (VE_RUN_CACHE=off) as
# regenerated: their rc and the sha256 of lean/statements.txt, predicates.txt, declarations.txt, axioms.txt, VE/Audit.lean,
# ResponseShapeAudit.lean; then the checkout is put back (those files from HEAD, new untracked files removed) so the
# clean-tree check below sees what it saw before. tools-local/trainfix-seed.py compare reads both fingerprints.
# Writes timings.tsv (step, rc, seconds), machine.txt, gate.log, lake.log, gate-record.json (the record), done.txt
# ("GATE <rc> lake=<rc>" or "SETUP-FAIL <step>") and DONE (0 = a gate ran, its verdict is in done.txt; 2 = setup failed).
set -u
mode=$1; R=$2; O=$3; JOB=$4; HEAD_SHA=$5; BASE=$6; N=${9:-4}; SHARD=${10:--}; AUTH=${11:--}
[ "$AUTH" = - ] || [ "$AUTH" = authority ] || exit 2
SEED=$(tail -n 1 "$0" | sed -n -E 's/^#VE-GATE-SEED=(seed|seed-fp|cold-fp)$/\1/p'); SEED=${SEED:--}
[ "$AUTH" = authority ] && SEED=-
FP=""; [ "$SEED" = cold-fp ] && FP=1
[ "$SEED" = seed-fp ] && [ "$SHARD" != - ] && [ "${SHARD%%/*}" = "${SHARD##*/}" ] && FP=1
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
lean_from_seal(){ local t; t=$(git rev-parse -q --verify HEAD:lean) || { echo "no HEAD:lean"; return 1; }
  zstd -dc "$VE_LEAN_FROM" 2> /dev/null | tar -xO pins.json 2> /dev/null | python3 -I -c 'import json, sys
try:
    k = json.load(sys.stdin)["key"]
except (ValueError, KeyError, TypeError):
    sys.exit("the pack has no readable seal")
if not isinstance(k, dict) or k.get("git_lean_tree") != sys.argv[1]:
    sys.exit("the seal names lean tree %.12s, not %.12s" % (str(k.get("git_lean_tree") if isinstance(k, dict) else None), sys.argv[1]))' "$t" 2>&1; }
lf=""
if [ -n "${VE_LEAN_FROM:-}" ]; then
  if ! grep -q -x '#VE-CACHE-SH-BEGIN' "$0"; then echo "lean-from: job.sh carries no ve-cache.sh: not restored, cold build" >> "$O/machine.txt"
  elif ! why=$(lean_from_seal); then echo "lean-from: ${why:0:200}: not restored, cold build" >> "$O/machine.txt"
  else
    sed -n '/^#VE-CACHE-SH-BEGIN$/,$p' "$0" | tail -n +2 > "$RUNNER_TEMP/ve-cache.sh"
    echo '{"format": 1, "assets": []}' > "$RUNNER_TEMP/ve-cache-none.json"
    VE_CACHE_DIR=$RUNNER_TEMP/ve-cache step lean_from bash "$RUNNER_TEMP/ve-cache.sh" restore lean-build --repo "$R" \
      --url "file://$VE_LEAN_FROM" --sha256 "${VE_LEAN_FROM_SHA256:-}" --manifest "$RUNNER_TEMP/ve-cache-none.json" --report "$O/lean-from.json"
    if python3 -I -c 'import json, sys; r = json.load(open(sys.argv[1])); sys.exit(not (r.get("status") == "restored" and r.get("match") == "exact"))' "$O/lean-from.json" 2> /dev/null
    then lf=1; else rm -rf lean/.lake/build; fi
    echo "lean-from: $([ -n "$lf" ] && echo restored || echo "not restored, cold build"): $(tail -n 1 "$O/lean_from.log" | head -c 200)" >> "$O/machine.txt"
  fi
fi
smatch=cold; sasset=-; spruned=0; seedc=""; sstale=""; srebuilt=-
# traces <out.json>: {module: sha256 of its Lake .trace} over lean/.lake/build/lib/lean (the build's input record per module)
traces(){ python3 -I -c 'import hashlib, json, os, sys
d, out = "lean/.lake/build/lib/lean", {}
for dp, _, fs in os.walk(d):
    for f in fs:
        if f.endswith(".trace"):
            p = os.path.join(dp, f); out[os.path.relpath(p, d)[:-len(".trace")]] = hashlib.sha256(open(p, "rb").read()).hexdigest()
json.dump(out, open(sys.argv[1], "w"))' "$1" 2> /dev/null; }
if [ -z "$lf" ] && [ "$SEED" != cold-fp ] && grep -q -x '#VE-CACHE-SH-BEGIN' "$0"; then
  sed -n '/^#VE-CACHE-SH-BEGIN$/,$p' "$0" | tail -n +2 > "$RUNNER_TEMP/ve-cache.sh"
  export VE_CACHE_DIR=$RUNNER_TEMP/ve-cache
  # exact key only (a gate leg decides merges; lean_share restores exact keys only too): the public manifest cut down to
  # this lean/ tree's assets, so ve-cache.sh restores the exact build or none (cold: "no lean-build asset")
  # 2026-11-09 dri-trainfix-seed: with a seed mode (DRI ruling 2026-11-09 item 3, header) the cut keeps this tree's assets
  # AND those built at a main commit that is an ancestor of HEAD, and ve-cache.sh gets --base: its pick order then gives
  # exact, seed-base or seed-ancestor only (an ancestor is always nearer than "newest"); any other pick is undone below
  if [ "$SEED" = - ]; then mcut(){ python3 -I -c 'import json,sys; m=json.load(open(sys.argv[1])); m["assets"]=[a for a in m.get("assets",[]) if a.get("key")==sys.argv[3]]; json.dump(m,open(sys.argv[2],"w"))' "$@"; }
  else mcut(){ python3 -I -c 'import json, subprocess, sys
m = json.load(open(sys.argv[1])); tree = sys.argv[3]
anc = lambda c: bool(c) and subprocess.run(["git", "merge-base", "--is-ancestor", c, "HEAD"], capture_output=True).returncode == 0
m["assets"] = [a for a in m.get("assets", []) if a.get("key") == tree or any(anc(a.get(f)) for f in ("main_export", "main"))]
json.dump(m, open(sys.argv[2], "w"))' "$@"; }; fi
  if curl -sSfL --retry 2 --max-time 60 -o "$RUNNER_TEMP/ve-cache-all.json" ${VE_GATE_MANIFEST_URL:-https://github.com/panaali/verifiable-english/releases/download/ve-cache/ve-cache-manifest.json} \
     && mcut "$RUNNER_TEMP/ve-cache-all.json" "$RUNNER_TEMP/ve-cache-exact.json" "$(git rev-parse HEAD:lean)"; then
    if [ "$SEED" = - ]; then
      step cache_restore bash "$RUNNER_TEMP/ve-cache.sh" restore lean-build --repo "$R" --manifest "$RUNNER_TEMP/ve-cache-exact.json" --report "$O/ve-cache.json"
    else step cache_restore bash "$RUNNER_TEMP/ve-cache.sh" restore lean-build --repo "$R" --base "$BASE" --manifest "$RUNNER_TEMP/ve-cache-exact.json" --report "$O/ve-cache.json"
      read -r smatch sasset < <(python3 -I -c 'import json, sys
try:
    r = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    r = {}
print(r.get("match") if r.get("status") == "restored" else "cold", r.get("asset") or "-")' "$O/ve-cache.json" 2> /dev/null)
      case ${smatch:-cold} in
        exact|seed-base|seed-ancestor) ;;
        cold) ;;
        *) echo "seed: ve-cache.sh picked ${smatch} ($sasset), not exact/seed-base/seed-ancestor: removed, cold build" >> "$O/machine.txt"
           rm -rf lean/.lake/build; smatch=cold;;
      esac
      # a module the checkout no longer has (deleted or renamed by the candidate) keeps no artifact from the seed
      if [ "$smatch" != cold ] && [ "$smatch" != exact ]; then
        spruned=$(python3 -I -c 'import os, sys
n = 0
for sub in ("lean/.lake/build/lib/lean", "lean/.lake/build/ir"):
    for dp, _, fs in os.walk(sub):
        for f in fs:
            rel = os.path.relpath(os.path.join(dp, f), sub)
            d, b = os.path.split(rel)
            if not os.path.exists(os.path.join("lean", d, b.split(".", 1)[0] + ".lean")):
                os.remove(os.path.join(dp, f)); n += 1
print(n)' 2> /dev/null) || { echo "seed: the prune failed: removed, cold build" >> "$O/machine.txt"; rm -rf lean/.lake/build; smatch=cold; spruned=0; }
      fi
      # the stale-build check (below, after lake build): the seed's main commit and every module's .trace before the build
      if [ "$smatch" = seed-base ] || [ "$smatch" = seed-ancestor ]; then
        seedc=$(python3 -I -c 'import json, sys; m = json.load(open(sys.argv[1]))
print(next((a.get("main_export") or a.get("main") or "" for a in m.get("assets", []) if a.get("name") == sys.argv[2]), ""))' "$RUNNER_TEMP/ve-cache-exact.json" "$sasset" 2> /dev/null)
        traces "$RUNNER_TEMP/traces-before.json"
      fi
    fi
    tail -n 1 "$O/cache_restore.log" >> "$O/machine.txt"
  else echo "ve-cache: the public manifest did not download: cold build" >> "$O/machine.txt"; fi
fi
[ "$SEED" != - ] && echo "seed: mode=$SEED match=${smatch:-cold} asset=$sasset pruned=${spruned:-0} base=${BASE:0:12}" >> "$O/machine.txt"
lb(){ ( cd lean && lake build ); }
step lake lb; lk=$?
if [ $lk -ne 0 ] && ! grep -qE '^error: [^ ]+\.lean:[0-9]+:[0-9]+:|deep recursion was detected' "$O/lake.log"; then
  for m in $(sed -nE "s/.*Building ([A-Za-z0-9_.']+):c\.o.*/\1/p" "$O/lake.log" | sort -u); do rm -f lean/.lake/build/ir/${m//.//}.c.o*; done
  mv "$O/lake.log" "$O/lake-first.log"; step lake lb; lk=$?; fi
# 2026-11-09 dri-trainfix-seed, the stale-build check (every seed-base/seed-ancestor shard): a module whose .lean differs
# from the seed's main commit (added or modified) and that the seed had built must have a NEW .trace after `lake build`
# (Lake records its inputs there and rewrites it when it rebuilds). One that kept the seed's trace was not rebuilt: the seed
# is thrown away, the build is redone cold (this shard's verdict is a cold build's), seed.json lists it under "stale" and
# the dispatcher turns ARM_GATE_SEED off (trainfix-seed.py leg-summary). No seed commit in this checkout: cold as well.
if [ -s "$RUNNER_TEMP/traces-before.json" ] && [ $lk -eq 0 ]; then
  traces "$RUNNER_TEMP/traces-after.json"
  read -r srebuilt sstale < <(python3 -I -c 'import json, subprocess, sys
b, a = (json.load(open(p)) for p in sys.argv[1:3]); seedc = sys.argv[3]
r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AMR", seedc, "HEAD", "--", "lean"], capture_output=True, text=True)
if not seedc or r.returncode != 0:
    print(-1); sys.exit()
mods = [l[len("lean/"):-len(".lean")] for l in r.stdout.splitlines() if l.endswith(".lean")]
stale = [m for m in mods if m in b and a.get(m) == b[m]]
print(sum(1 for m in a if a[m] != b.get(m)), ",".join(stale))' "$RUNNER_TEMP/traces-before.json" "$RUNNER_TEMP/traces-after.json" "$seedc" 2> /dev/null)
  if [ "$srebuilt" = -1 ] || [ -z "$srebuilt" ]; then
    echo "seed: the stale-build check could not read the seed's commit (${seedc:-none}): the seed removed, cold rebuild" >> "$O/machine.txt"
    rm -rf lean/.lake/build; mv "$O/lake.log" "$O/lake-seeded.log"; step lake lb; lk=$?; smatch=cold; sstale=""; srebuilt=-
  elif [ -n "$sstale" ]; then
    echo "seed: STALE after lake build (${sstale:0:300}): the seed removed, cold rebuild" >> "$O/machine.txt"
    rm -rf lean/.lake/build; mv "$O/lake.log" "$O/lake-seeded.log"; step lake lb; lk=$?; smatch=cold
  else echo "seed: $srebuilt modules rebuilt over the seed (traces), none stale" >> "$O/machine.txt"; fi
fi
if [ "$SEED" != - ]; then
  lks=$(awk -F'\t' '$1 == "lake" {s += $3} END {printf "%.1f", s}' "$P")
  echo "seed: lake $lks s (rc $lk, match ${smatch:-cold})" >> "$O/machine.txt"
  python3 -I -c 'import json, sys; k = ["seed", "match", "asset", "pruned", "lake_rc", "lake_s", "shard", "base", "seed_commit", "rebuilt", "stale"]; d = dict(zip(k, sys.argv[2:]))
d["pruned"], d["lake_rc"], d["lake_s"], d["rebuilt"] = int(d["pruned"] or 0), int(d["lake_rc"]), float(d["lake_s"]), int(d["rebuilt"]) if d["rebuilt"].lstrip("-").isdigit() else None
d["stale"] = [m for m in d["stale"].split(",") if m]; json.dump(d, open(sys.argv[1], "w"))' \
    "$O/seed.json" "$SEED" "${smatch:-cold}" "$sasset" "${spruned:-0}" "$lk" "$lks" "$SHARD" "$BASE" "${seedc:--}" "$srebuilt" "$sstale" 2>> "$O/machine.txt"
fi
# the Lean fingerprint (seed-fp on shard N, cold-fp): see the header; never fails the job, says what it could not read
if [ -n "$FP" ]; then
  # its own timings file: timings.tsv rows other than lake/gate are the shard's setup (gha-arm-shard.sh's H, shard-overhead.tsv)
  fpstep(){ local name=$1; shift; local t0; t0=$(now); "$@" > "$O/$name.log" 2>&1; local rc=$?
    printf '%s\t%s\t%s\n' "$name" "$rc" "$(awk -v a="$t0" -v b="$(now)" 'BEGIN{printf "%.1f", b-a}')" >> "$O/fp-timings.tsv"; return $rc; }
  fp_t0=$(now); fpfiles=(lean/statements.txt lean/predicates.txt lean/declarations.txt lean/axioms.txt lean/VE/Audit.lean lean/ResponseShapeAudit.lean)
  git status --porcelain --untracked-files=all > "$RUNNER_TEMP/fp-before.txt"; fpinv=""; [ -e lean/.lake/ve-inventory ] && fpinv=1
  ( cd lean/.lake/build/lib/lean 2> /dev/null && find . -name '*.olean' -type f | LC_ALL=C sort | xargs -r sha256sum ) > "$O/fp-oleans.txt" 2> /dev/null
  git diff --name-only "$BASE" HEAD -- lean | grep '\.lean$' > "$RUNNER_TEMP/fp-changed.txt"
  fst=-; fau=-
  if [ $lk -eq 0 ]; then
    VE_RUN_CACHE=off fpstep fp_statements timeout 2400 uv run python tools/lean_statements.py; fst=$?
    VE_RUN_CACHE=off fpstep fp_audit timeout 2400 uv run python lean/audit.py --write; fau=$?
  fi
  python3 -I - "$O/fp.json" "$SEED" "$lk" "$fst" "$fau" "$O/fp-oleans.txt" "$RUNNER_TEMP/fp-changed.txt" "$HEAD_SHA" "$BASE" "${fpfiles[@]}" <<'PY' 2>> "$O/machine.txt"
import hashlib, json, os, sys
out, seed, lk, fst, fau, oleans, changed, head, base = sys.argv[1:10]
files = sys.argv[10:]
def h(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except OSError:
        return None
ol = {}
for line in open(oleans).read().splitlines():
    s, _, p = line.partition("  ")
    ol[p[2:] if p.startswith("./") else p] = s
mods = [l[len("lean/"):-len(".lean")] for l in open(changed).read().splitlines() if l.startswith("lean/") and l.endswith(".lean")]
d = {"seed": seed, "head": head, "base": base, "lake_rc": int(lk), "statements_rc": None if fst == "-" else int(fst),
     "audit_rc": None if fau == "-" else int(fau), "files": {f: h(f) for f in files} if fst != "-" else {},
     "changed_modules": mods, "changed_oleans": {m: ol.get(m + ".olean") for m in mods},
     "oleans_n": len(ol), "oleans_sha256": hashlib.sha256(open(oleans, "rb").read()).hexdigest()}
json.dump(d, open(out, "w"), indent=1, sort_keys=True)
PY
  # put the checkout back: the regenerated files from HEAD (or removed when HEAD has none), new untracked files removed
  for f in "${fpfiles[@]}"; do if git cat-file -e "HEAD:$f" 2> /dev/null; then git checkout -q HEAD -- "$f"; else rm -f "$f"; fi; done
  git status --porcelain --untracked-files=all | while IFS= read -r l; do grep -qxF -- "$l" "$RUNNER_TEMP/fp-before.txt" && continue
    case $l in '?? '*) rm -f -- "${l#?? }";; *) git checkout -q HEAD -- "${l#???}" 2> /dev/null;; esac; done
  [ -n "$fpinv" ] || rm -rf lean/.lake/ve-inventory
  echo "seed: fingerprint fp.json (lake rc $lk, statements rc $fst, audit rc $fau, $(awk -v a="$fp_t0" -v b="$(now)" 'BEGIN{printf "%.0f", b-a}') s)" >> "$O/machine.txt"
fi
if [ "$SEED" = cold-fp ]; then echo "SHADOW lake=$lk" > "$O/done.txt"; echo 0 > "$O/DONE"; exit 0; fi
if [ $lk -eq 0 ] && [ "$(uname -m)" = x86_64 ]; then
  echo "pins: the committed lean/checkers.lock (x86_64 is the pins authority: not rewritten)" >> "$O/machine.txt"
  if [ "$SHARD" != - ] && [ "${SHARD%%/*}" != 1 ]; then step rust_pin uv run python tools/rust_build.py --check || fail rust-pin; fi
elif [ $lk -eq 0 ] && [ "$AUTH" != authority ]; then
  step pins uv run python tools/regen_generated.py --write --only checker-pins || fail pins
  git update-index --assume-unchanged lean/checkers.lock
fi
# 2026-11-01 actions-gate-x86-switch (backlog nightly-x86-tokenizer; the Mac's seed rule L100): the VM's gate worktrees and
# the Mac's seed ~/p1-tokenizers-seed hold exactly one pinned P1 tokenizer (.cache/p1-tokenizers/<git blob sha1>.json, the
# Qwen one), so tests/test_p1_native_counter.py [replication-19] runs there and is skipped on a fresh checkout (R18: an added
# skip = DIFFERENT). Every job fetches THAT set (P1_TOK_SEED) from the source pinned in experiments/P1-deference/
# tokenizers/sources.json (repo, revision) and keeps a file only if its git blob sha1 is the pinned one; never the others
# ([weak-21] stays skipped, as on the VM and the Mac). Any failure: nothing written, the test skips, the job goes on (gate-compare
# then says DIFFERENT and the leg goes back to the VM). VE_P1_TOK_BASE: tests only (a file:// mirror).
# 2026-11-01 arm-shard-p1-tok: on every architecture, not only x86_64. With the fetch on x86_64 only, an aarch64 shard had the
# file only when an earlier test in its own checkout downloaded it, so the shard split decided [replication-19] (the sharded
# arm shadow of e63bae65 skipped it in shard 2: DIFFERENT).
P1_TOK_SEED=443909a61d429dff23010e5bddd28ff530edda00
step p1_tokenizer python3 -I -c 'import hashlib, json, os, sys, tempfile, urllib.request
base, want = sys.argv[1], sys.argv[2:]
blob = lambda b: hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()
try:
    src = json.load(open("experiments/P1-deference/tokenizers/sources.json"))
except (OSError, ValueError):
    print("no readable sources.json: none fetched"); sys.exit(0)
cache, said = ".cache/p1-tokenizers", {}
for spec in src.values() if isinstance(src, dict) else ():
    f = (spec.get("files") or {}).get("tokenizer.json") if isinstance(spec, dict) else None
    sha = f.get("git_blob_sha1") if isinstance(f, dict) else None
    if sha not in want or sha in said:
        continue
    path = os.path.join(cache, sha + ".json")
    try:
        if os.path.exists(path) and blob(open(path, "rb").read()) == sha:
            said[sha] = "cached"; continue
        data = urllib.request.urlopen("%s/%s/resolve/%s/tokenizer.json" % (base, f["repo"], f["revision"]), timeout=120).read()
        if blob(data) != sha:
            said[sha] = "REFUSED (blob sha1 %s)" % blob(data)[:12]; continue
        os.makedirs(cache, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=cache)
        with os.fdopen(fd, "wb") as h:
            h.write(data)
        os.replace(tmp, path); said[sha] = "fetched"
    except Exception as e:
        said[sha] = "failed (%s)" % type(e).__name__
print("; ".join("%s %s" % (s[:12], said.get(s, "not in sources.json")) for s in want))' "${VE_P1_TOK_BASE:-https://huggingface.co}" $P1_TOK_SEED
echo "p1-tokenizers: $(tail -n 1 "$O/p1_tokenizer.log" | head -c 200)" >> "$O/machine.txt"
git status --porcelain --untracked-files=all > "$O/dirty.txt"; [ -s "$O/dirty.txt" ] && fail dirty-after-setup
ulimit -s 8192
if [ "$AUTH" = authority ]; then
  VE_GATE_RUN_CACHE_OFF=1 VE_GATE_NO_RUNNER_PINS=1 step gate timeout 19000 uv run python -I "$RUNNER_TEMP/gate-wrap.py" --no-quarantine --workers "$N" "${sharg[@]}"; gt=$?
else step gate timeout 19000 uv run python "$RUNNER_TEMP/gate-wrap.py" --workers "$N" "${sharg[@]}"; gt=$?; fi
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
# 2026-11-03 (arm-mac-first-pins-regen, ADV-20261103T0711-1): the base worktree's pins build ran tools/rust_build.py with
# CARGO_HOME = <base worktree>/.cargo-home, which a fresh `git worktree add` does not have, and without offline mode, so
# cargo tried to download the crates.io index; the runner guest has had no DNS since Oct 22 (Tailscale MagicDNS, no upstream:
# L100), and every collected base failed "unlisted build" at collection (cand-sc-6/pc-9/sn-b6b: EARLY, the train's Mac-first
# legs fell back to Actions). Now the base worktree gets a copy of the job checkout's own .cargo-home/registry (filled by
# mac-gate-job.sh's cargofetch from ~/cargo-seed; gitignored, never committed) and the pins step runs with
# CARGO_NET_OFFLINE=true; build_rust (gate_collection) has already copied the job checkout's rust/target into the tree, so
# the release build is incremental. A pins failure is logged as "checker-pins: <cause>" and the cause is written to
# <job dir>/base-pins.cause (outside the checkout), which mac-gate.sh puts into the record (runner.base_pins) and its log.
import os
import runpy
import subprocess
import sys
from pathlib import Path

PIN = "lean/checkers.lock"


def say(text):
    print(f"[gate-wrap] {text}", file=sys.stderr, flush=True)


CAUSE = "base-pins.cause"  # in the job dir (the checkout's parent), read by mac-gate.sh


def seed_cargo_home(root, tree):
    """The job checkout's cargo registry for the base worktree (rust_build.py's CARGO_HOME is <tree>/.cargo-home)."""
    src, dst = root / ".cargo-home" / "registry", tree / ".cargo-home" / "registry"
    if dst.is_dir():
        return "base worktree has its own .cargo-home"
    if not src.is_dir():
        return f"no {src} to copy"
    import shutil
    shutil.copytree(src, dst, symlinks=True)
    return f"registry copied from {src}"


def pins_cause(out, seeded):
    """One line naming why the base worktree's checker-pins step failed."""
    import re
    host = re.search(r"Could not resolve host: ([^\s)]+)", out)
    if host:
        return (f"the base worktree's Rust release build needed the network and the runner cannot resolve {host.group(1)} "
                f"(cargo registry: {seeded})")
    if re.search(r"--offline was specified|failed to download|no matching package named|failed to load source", out):
        return f"a crate of the base's Cargo.lock is not in the runner's cargo registry (offline build; {seeded})"
    lines = [x.strip() for x in out.splitlines() if x.strip()]
    named = [x for x in lines if x.startswith(("checker-pins:", "error:"))]
    last = (named or lines or ["no output"])[-1]
    return last[len("checker-pins: "):] if last.startswith("checker-pins: ") else last


def install_base_pins(root):
    """Runner pins for a base worktree gate.py collects (2026-10-14)."""
    from tools import gate_collection

    original = gate_collection.collect

    def collect(tree, *args, **kwargs):
        tree = Path(tree)
        seeded = seed_cargo_home(root, tree)
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        env["CARGO_NET_OFFLINE"] = "true"
        done = subprocess.run([sys.executable, str(tree / "tools/regen_generated.py"), "--write", "--only", "checker-pins"],
                              cwd=tree, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        say(f"runner-local checker pins for the base worktree {tree}: exit {done.returncode} ({seeded}, offline)")
        if done.returncode:
            print(done.stdout[-3000:], file=sys.stderr, flush=True)
            cause = pins_cause(done.stdout, seeded)
            say(f"checker-pins: {cause}")
            try:
                (root.parent / CAUSE).write_text(cause + "\n")
            except OSError as exc:
                say(f"{CAUSE} not written: {exc!r}")
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
