#!/bin/bash
# GitHub Actions aarch64 Lean build cache job (2026-10-30 dri-arm-lean-cache, backlog arm-lean-cache; reviews/arm-lean-cache-20261029.md);
# run as ci-job/job.sh by the staged workflow gha/ve-job-arm.yml (ubuntu-24.04-arm), dispatched by lean-cache-arm.sh on the VM.
# Builds main's lean/ tree once (`lake build`, one retry of a crashed build, as gha/gate-job.sh), stores it with VE's own
# tools/lean_share.py publish (the seal pins.json: key = lean tree, toolchain, platform Linux-aarch64; every file's SHA-256;
# pins runner-local:gha-arm) and packs that entry like lean-cache-publish.sh packs the x86 one (lake/ + pins.json, tar |
# zstd -6) as <out>/pack/lean-build-<lean tree 12>-linux-aarch64.tar.zst. The pack is in a SUBDIRECTORY: the workflow's
# artifact "out" carries it, its publish job (files of <out> only) leaves it out of the ci-result commit; <out>/pack.json
# (name, sha256, bytes, members, entry, lean tree, lean --version) goes in the commit. The VM fetches the artifact,
# checks it (sha256, size cap, member names, content scan, seal, every file's SHA-256) and publishes it; nothing is
# trusted from here. No secrets, no token; the job only reads the public checkout.
# usage: lean-cache-arm-job.sh run <checkout> <out dir> <job> <head> <lean tree (git rev-parse HEAD:lean)>
# Writes timings.tsv, machine.txt, lake.log, publish.log, pack.json, done.txt ("LEANCACHE 0" or "SETUP-FAIL <step>"), DONE.
set -u
mode=$1; R=$2; O=$3; JOB=$4; HEAD_SHA=$5; LT=$6; CAP=2000000000
[ "$mode" = run ] || exit 2
export PATH=/usr/local/bin:/opt/lean/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH
mkdir -p "$O/pack"; P=$O/timings.tsv; printf 'step\trc\tseconds\n' > "$P"
now(){ date +%s.%N; }
step(){ local name=$1; shift; local t0; t0=$(now); "$@" > "$O/$name.log" 2>&1; local rc=$?
  printf '%s\t%s\t%s\n' "$name" "$rc" "$(awk -v a="$t0" -v b="$(now)" 'BEGIN{printf "%.1f", b-a}')" >> "$P"; return $rc; }
fail(){ echo "SETUP-FAIL $1" > "$O/done.txt"; echo 2 > "$O/DONE"; exit 2; }
{ echo "job=$JOB nproc=$(nproc) arch=$(uname -m) host=$(hostname) date=$(date -u +%FT%TZ)"; free -g | sed -n 2p; df -h / | tail -1; } > "$O/machine.txt"
cd "$R" || fail cd
[ "$(git rev-parse HEAD)" = "$HEAD_SHA" ] || fail head
[ "$(git rev-parse HEAD:lean)" = "$LT" ] || fail lean-tree
tc=$(cat lean/lean-toolchain); tc=${tc//\//--}; mkdir -p ~/.elan/toolchains ~/.elan/bin
ln -sfn /opt/lean ~/.elan/toolchains/${tc//:/---}; for t in lean lake; do [ -e ~/.elan/bin/$t ] || ln -sfn /opt/lean/bin/$t ~/.elan/bin/$t; done
step python_env uv sync -q --locked --group dev || fail sync
lb(){ ( cd lean && lake build ); }
step lake lb; lk=$?
if [ $lk -ne 0 ] && ! grep -qE '^error: [^ ]+\.lean:[0-9]+:[0-9]+:|deep recursion was detected' "$O/lake.log"; then
  for m in $(sed -nE "s/.*Building ([A-Za-z0-9_.']+):c\.o.*/\1/p" "$O/lake.log" | sort -u); do rm -f lean/.lake/build/ir/${m//.//}.c.o*; done
  mv "$O/lake.log" "$O/lake-first.log"; step lake lb; lk=$?; fi
[ $lk -eq 0 ] || fail lake
git status --porcelain --untracked-files=all > "$O/dirty.txt"; [ -s "$O/dirty.txt" ] && fail dirty-after-build
S=$RUNNER_TEMP/lean-share
step publish uv run python tools/lean_share.py publish --store "$S" --pins runner-local:gha-arm --copy || fail publish
entry=$(ls "$S/v1"); [[ $entry =~ ^[0-9a-f]{64}$ ]] || fail entry
name=lean-build-${LT:0:12}-linux-aarch64.tar.zst; A=$O/pack/$name
pk(){ tar -C "$S/v1/$entry" -cf - lake pins.json | zstd -6 -T0 -q -o "$A"; }
step pack pk || fail pack
zstd -dc "$A" | tar -t > "$RUNNER_TEMP/pack.list" || fail pack-list
[ "$(stat -c %s "$A")" -le $CAP ] || fail size-cap
python3 -I - "$O/pack.json" "$A" "$RUNNER_TEMP/pack.list" "$JOB" "$HEAD_SHA" "$LT" "$entry" "$(lean --version | head -1)" "$(uname -s)-$(uname -m)" <<'PY' || fail pack-json
import hashlib, json, os, sys
out, a, lst, job, head, lt, entry, leanv, plat = sys.argv[1:10]
h = hashlib.sha256()
with open(a, "rb") as f:
    for b in iter(lambda: f.read(1 << 20), b""):
        h.update(b)
json.dump({"job": job, "head": head, "lean_tree": lt, "entry": entry, "name": os.path.basename(a), "sha256": h.hexdigest(),
           "bytes": os.path.getsize(a), "members": sum(1 for l in open(lst) if l.strip()), "lean": leanv, "platform": plat},
          open(out, "w"), indent=1)
PY
echo "LEANCACHE 0 lake=$lk" > "$O/done.txt"; echo 0 > "$O/DONE"; exit 0
