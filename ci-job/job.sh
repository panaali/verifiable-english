#!/bin/bash
# GitHub Actions command job (2026-10-28 dri-gha, reviews/gha-pilot-20261028.md); the workflow runs it as ci-job/job.sh.
# usage: cmd-job.sh run <checkout> <out dir> <job> <head> <base> <asset url|-> <asset sha256|-> <name>=<command>...
# Same setup as cloud-tm-job.sh (HEAD check, history for <base>, tools, main's Lean build from the cache asset (sha256,
# member names and seal checked), else a cold build, `uv sync --frozen`, the branch's incremental `lake build`), then each <command> in order with
# `bash -c` in the checkout (BASE=<base> in its environment), log <name>.log. Writes timings.tsv (step, rc, seconds),
# machine.txt, steps.rc (name rc per command) and DONE (this script's exit code).
set -u
mode=$1; R=$2; O=$3; JOB=$4; HEAD_SHA=$5; BASE=$6; URL=$7; SUM=$8; shift 8
[ "$mode" = run ] || exit 2
T=${CLOUD_TM_TMP:-/tmp}; export PATH=/usr/local/bin:/opt/lean/bin:$HOME/.local/bin:$PATH BASE
mkdir -p "$O"; P=$O/timings.tsv; printf 'step\trc\tseconds\n' > "$P"
now(){ date +%s.%N; }
step(){ local name=$1; shift; local t0; t0=$(now); "$@" > "$O/$name.log" 2>&1; local rc=$?
  printf '%s\t%s\t%s\n' "$name" "$rc" "$(awk -v a="$t0" -v b="$(now)" 'BEGIN{printf "%.1f", b-a}')" >> "$P"; return $rc; }
finish(){ echo "$1" > "$O/DONE"; exit "$1"; }
{ echo "job=$JOB nproc=$(nproc) host=$(hostname) date=$(date -u +%FT%TZ)"; free -g | sed -n 2p; df -h / | tail -1; uptime; } > "$O/machine.txt"
cd "$R" || finish 2
[ "$(git rev-parse HEAD)" = "$HEAD_SHA" ] || { echo "HEAD is not $HEAD_SHA" >> "$O/machine.txt"; finish 2; }
git cat-file -e "$BASE^{commit}" 2>/dev/null || step fetch_history git fetch -q origin
git cat-file -e "$BASE^{commit}" 2>/dev/null || { echo "base $BASE missing" >> "$O/machine.txt"; finish 2; }
git branch -f main "$BASE" 2>> "$O/machine.txt"  # as on the VM, where main is the branch's merge base (regen --check trust-tables)
for t in lean lake zstd uv; do command -v $t > /dev/null || { echo "missing tool: $t" >> "$O/machine.txt"; printf 'tools\t127\t0\n' >> "$P"; finish 127; }; done
lean --version >> "$O/machine.txt" 2>&1
# 2026-10-28 dri-elanbin (R18, gha-elan-bin): the account's elan lean, as on the VM and the Mac (test_lake_outputs looks there)
# 2026-10-29 dri-maclight (gha-elan-lake): lake too (en-sw tests/test_source_words.py calls ~/.elan/bin/lake)
for t in lean lake; do [ -e "$HOME/.elan/bin/$t" ] || [ ! -x /opt/lean/bin/$t ] || { mkdir -p "$HOME/.elan/bin" && ln -sfn /opt/lean/bin/$t "$HOME/.elan/bin/$t"; } 2>> "$O/machine.txt"; done
# 2026-10-28 dri-advfix5 (ADV-20261028T0336-1): the fallback without the bundle (SHARED_CACHE off) is no weaker path: the
# same checks as ve-cache.sh (asset name, sha256, member names, the seal: platform and lean --version), the same exit
# classes (3 cold, 4 refused, 5 error) and the same ve-cache.json report (path inline), for the VM's ve-cache-guard.sh.
inline_restore(){ local u=$1 s=$2 n f=$T/lean-cache.tar.zst got seal lv; n=$(basename "$u"); lv=$(lean --version 2>/dev/null | head -1)
  vrep(){ python3 -I -c 'import json,sys; k=["kind","status","class","reason","asset","sha256","platform","lean","path"]
json.dump(dict(zip(k, sys.argv[2:])), open(sys.argv[1], "w"))' "$O/ve-cache.json" lean-build "$1" "$2" "$3" "$n" "$s" "$(uname -s)-$(uname -m)" "$lv" inline
    echo "ve-cache (inline): $1 ($2): $3"; rm -f "$f"; rm -rf "$T/lc"; case $1 in restored) return 0;; cold) return 3;; refused) return 4;; *) return 5;; esac; }
  case $n in lean-build-*.tar.zst) ;; *) vrep refused name "unexpected asset name $n"; return;; esac
  # 2026-10-28 dri-tmshard (cache-manifest-404): an asset GitHub no longer serves is class gone (said; not a download error)
  curl -sSfL --retry 2 -o "$f" "$u" || { case $(case $u in file://*) [ -e "${u#file://}" ] && echo 200 || echo 404;; *) curl -sIL --max-time 30 -o /dev/null -w '%{http_code}' "$u" 2>/dev/null;; esac) in
    404|410) vrep cold gone "pinned asset $n is gone (no longer served): cold build";; *) vrep cold download "download of $n failed";; esac; return; }
  got=$(sha256sum "$f" | cut -d' ' -f1); [ "$got" = "$s" ] || { vrep refused sha256 "sha256 of $n is ${got:0:12}, not ${s:0:12}"; return; }
  zstd -dc "$f" | tar -t > "$T/lc.list" 2>/dev/null || { vrep refused members "$n does not list"; return; }
  grep -q -E '^/|(^|/)\.\.(/|$)' "$T/lc.list" && { vrep refused members "$n has an absolute or .. member"; return; }
  grep -q -x 'pins.json' "$T/lc.list" && grep -q '^lake/build/' "$T/lc.list" || { vrep refused members "$n lacks pins.json or lake/build/"; return; }
  rm -rf "$T/lc" && mkdir -p "$T/lc" && zstd -dc "$f" | tar -x -C "$T/lc" || { vrep error mechanism "extracting $n failed"; return; }
  seal=$(python3 -I -c 'import json, sys
k = json.load(open(sys.argv[1]))["key"]; system, machine, leanv = sys.argv[2:5]; p = k.get("platform", {})
if (p.get("system"), p.get("machine")) != (system, machine):
    sys.exit("seal platform %s-%s is not %s-%s" % (p.get("system"), p.get("machine"), system, machine))
if leanv and k.get("toolchain", {}).get("lean") != leanv:
    sys.exit("seal toolchain %r is not this lean %r" % (k.get("toolchain", {}).get("lean"), leanv))' "$T/lc/pins.json" "$(uname -s)" "$(uname -m)" "$lv" 2>&1) \
    || { vrep refused seal "$n refused: $(printf %s "$seal" | tail -n 1 | head -c 200)"; return; }
  chmod -R u+w "$T/lc" && rm -rf lean/.lake/build && mkdir -p lean/.lake && mv "$T/lc/lake/build" lean/.lake/build || { vrep error mechanism "moving the build into lean/.lake failed"; return; }
  vrep restored inline "$n sha256 ${s:0:12} ok, seal ok"; }
restored=""
# 2026-10-28 dri-sharedcache (flag SHARED_CACHE): a job script shipped with ve-cache.sh appended after its last line
# (ve-cache.sh bundle, by cloud-dispatch.sh / gha-job.sh) restores through it: key, sha256, member names and the seal
# (platform, lean --version) checked, exact/seed said, ve-cache.json written; any refusal = cold build. Else as before.
if [ "$URL" != - ] && grep -q -x '#VE-CACHE-SH-BEGIN' "$0" 2>/dev/null; then
  sed -n '/^#VE-CACHE-SH-BEGIN$/,$p' "$0" | tail -n +2 > "$T/ve-cache.sh"
  step cache_restore bash "$T/ve-cache.sh" restore lean-build --repo "$PWD" --url "$URL" --sha256 "$SUM" --report "$O/ve-cache.json" && restored=1
elif [ "$URL" != - ]; then
  step cache_restore inline_restore "$URL" "$SUM" && restored=1
fi
[ -n "$restored" ] || echo "no cache restored: cold build" >> "$O/machine.txt"
step python_env uv sync --frozen || finish 2
(cd lean && step branch_lake_build lake build)
# 2026-10-31 gha-wf2 (backlog gha-wf2; VE .github/workflows/ve-job.yml v2): when the workflow sets VE_LEAN_ASSET_DIR (job.json
# "lean_asset": true: the VM dispatcher's choice for one shard, flag BRANCH_LEAN_CACHE), the build just made is packed there
# as lean-build-<HEAD:lean, 12>.tar.zst (lake/build/ and a seal pins.json: git lean tree, platform, lean --version), right
# after the lake build and before any command runs; not when the build failed or the restore was already that exact tree.
# The workflow's publish job checks it and uploads it to the release lean-branch-cache; nothing here holds a token.
pack_branch(){ local d=$VE_LEAN_ASSET_DIR tr n b
  tr=$(git rev-parse -q --verify HEAD:lean) || return 1; n=lean-build-${tr:0:12}.tar.zst
  rm -rf "$d" "$T/lbseal" && mkdir -p "$d" "$T/lbseal" || return 1
  python3 -I -c 'import json, platform, sys
p, tree, leanv, job, head = sys.argv[1:6]
json.dump({"format": 1, "key": {"git_lean_tree": tree, "platform": {"system": platform.system(), "machine": platform.machine()},
           "toolchain": {"lean": leanv}}, "origin": {"kind": "gha-branch", "job": job, "head": head}}, open(p, "w"), indent=1)' \
    "$T/lbseal/pins.json" "$tr" "$(lean --version 2>/dev/null | head -1)" "$JOB" "$HEAD_SHA" || return 1
  tar -c -C "$T/lbseal" pins.json -C "$PWD/lean" --hard-dereference --transform 's,^\.lake/build,lake/build,' .lake/build \
    | zstd -q -6 -T0 -o "$d/$n.part" || { rm -rf "$d"; return 1; }
  b=$(stat -c %s "$d/$n.part"); [ "$b" -le 2000000000 ] || { echo "$n is $b bytes, over 2,000,000,000: not sent"; rm -rf "$d"; return 1; }
  mv "$d/$n.part" "$d/$n" && echo "packed $n ($b bytes)"; }
exact_restore(){ local tr; tr=$(git rev-parse -q --verify HEAD:lean) || return 1
  python3 -I -c 'import json, sys; sys.exit(0 if json.load(open(sys.argv[1])).get("match") == "exact" else 1)' "$O/ve-cache.json" 2>/dev/null \
    || { [ -n "$restored" ] && [ "$(basename "$URL")" = "lean-build-${tr:0:12}.tar.zst" ]; }; }
if [ -n "${VE_LEAN_ASSET_DIR:-}" ]; then
  if [ "$(awk -F'\t' '$1 == "branch_lake_build" {r = $2} END {print r}' "$P")" != 0 ]; then echo "lean asset: the lake build failed: nothing packed" >> "$O/machine.txt"
  elif exact_restore; then echo "lean asset: the restore was this exact lean tree: nothing packed" >> "$O/machine.txt"
  else step lean_asset pack_branch || echo "lean asset: packing failed (lean_asset.log): nothing sent" >> "$O/machine.txt"; fi; fi
export VE_LEAN_SHARE=off
: > "$O/steps.rc"
for spec in "$@"; do name=${spec%%=*}; cmd=${spec#*=}
  [[ $name =~ ^[A-Za-z0-9_-]+$ ]] || { echo "$spec: bad step name" >> "$O/machine.txt"; continue; }
  step "$name" bash -c "$cmd"; echo "$name $?" >> "$O/steps.rc"; done
finish 0
