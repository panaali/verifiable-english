#!/bin/bash
# Cloud runner job for trust_mutants (2026-10-27 cloud plumbing; from the pilot's tm-job.sh). cloud-dispatch.sh embeds
# this file verbatim in the routine's prompt; the session writes it to /tmp/cloud-tm-job.sh and runs it detached.
# usage: cloud-tm-job.sh run <checkout> <out dir> <job> <head> <base> <asset url|-> <asset sha256|-> [trust_mutants args...]
#        cloud-tm-job.sh publish <checkout> <out dir> <job> <branch>
# run: checks HEAD = <head>, fetches history if <base> is missing, needs lean, lake, zstd and uv (exit 127 if one is
#   missing: without lake the Lean tests would skip silently), restores main's Lean build from the release asset (sha256,
#   member names and the platform/toolchain seal checked; any failure: cold build, logged, ve-cache.json says why), `uv sync --frozen`, the branch's incremental `lake build`, then
#   VE_LEAN_SHARE=off uv run --frozen python tools/trust_mutants.py --base <base> <args> --json <out>/trust-mutants.json.
#   Writes <out>/timings.tsv (step, rc, seconds), machine.txt, tm.rc (trust_mutants' exit code) and DONE (this script's).
# publish: copies the results (json, timings, machine, tm.rc, last 200 lines of each log) to cloud-results/<job>/,
#   commits ONLY that directory on top of <head> and pushes it to <branch> (no --force; one retry after 30 s).
# 2026-10-31 eff-tm-partial: a `--budget S` among the trust_mutants args (tm-shard.sh, flag TM_PART_DEADLINE) counts
#   from this script's start, not the tool's (the cache restore, uv sync and the branch's lake build come first): it is
#   passed as `--deadline <start + S>` (unix seconds). The tool then writes a partial record (exit 4) before the job limit.
# Tests only: CLOUD_TM_LEAN_BIN (a dir prepended to PATH), CLOUD_TM_TMP (default /tmp), CLOUD_TM_START (the start time).
set -u
T0=${CLOUD_TM_START:-$(date +%s)}
mode=$1; R=$2; O=$3; JOB=$4; shift 4
T=${CLOUD_TM_TMP:-/tmp}; export PATH=/usr/local/bin:/opt/lean/bin:$HOME/.local/bin:$PATH
[ -n "${CLOUD_TM_LEAN_BIN:-}" ] && export PATH=$CLOUD_TM_LEAN_BIN:$PATH
mkdir -p "$O"
if [ "$mode" = publish ]; then
  BR=$1; D=cloud-results/$JOB; cd "$R" || exit 2
  rm -rf "$D"; mkdir -p "$D"
  for f in trust-mutants.json timings.tsv machine.txt tm.rc DONE ve-cache.json; do [ -f "$O/$f" ] && cp "$O/$f" "$D/"; done
  for f in "$O"/*.log; do [ -f "$f" ] && tail -n 200 "$f" > "$D/$(basename "$f").tail"; done
  git add -- "$D" && git -c user.name="VE cloud runner" -c user.email=noreply@anthropic.com commit -q -m "cloud-tm $JOB: trust_mutants result" -- "$D" || exit 3
  git push -q origin "HEAD:refs/heads/$BR" || { sleep 30; git push -q origin "HEAD:refs/heads/$BR"; } || exit 4
  git rev-parse HEAD; exit 0
fi
HEAD_SHA=$1; BASE=$2; URL=$3; SUM=$4; shift 4
P=$O/timings.tsv; printf 'step\trc\tseconds\n' > "$P"
now(){ date +%s.%N; }
step(){ local name=$1; shift; local t0; t0=$(now); "$@" > "$O/$name.log" 2>&1; local rc=$?
  printf '%s\t%s\t%s\n' "$name" "$rc" "$(awk -v a="$t0" -v b="$(now)" 'BEGIN{printf "%.1f", b-a}')" >> "$P"; return $rc; }
finish(){ echo "$1" > "$O/DONE"; exit "$1"; }
{ echo "job=$JOB nproc=$(nproc) host=$(hostname) date=$(date -u +%FT%TZ)"; free -g | sed -n 2p; df -h / | tail -1; uptime; } > "$O/machine.txt"
cd "$R" || finish 2
[ "$(git rev-parse HEAD)" = "$HEAD_SHA" ] || { echo "HEAD is not $HEAD_SHA" >> "$O/machine.txt"; finish 2; }
git cat-file -e "$BASE^{commit}" 2>/dev/null || step fetch_history git fetch -q --unshallow origin || step fetch_history2 git fetch -q origin
git cat-file -e "$BASE^{commit}" 2>/dev/null || { echo "base $BASE missing" >> "$O/machine.txt"; finish 2; }
for t in lean lake zstd uv; do command -v $t > /dev/null || { echo "missing tool: $t" >> "$O/machine.txt"; printf 'tools\t127\t0\n' >> "$P"; finish 127; }; done
lean --version >> "$O/machine.txt" 2>&1
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
export VE_LEAN_SHARE=off
# 2026-10-28 dri-offload2 (backlog cloud-rescore-ship): `--rescore ci-job/rescore.json` names the previous record the VM
# shipped inside this job's ci-job/job.json (next to this script: "rescore", sha256 "rescore_sha256"): written to
# <checkout>/ci-job/rescore.json first; missing or another sha256 -> no run (DONE 2: the VM runs it).
case " $* " in *" --rescore ci-job/rescore.json "*)
  step rescore_input python3 -I -c 'import hashlib, json, os, sys
d = json.load(open(sys.argv[1])); raw = d["rescore"].encode("utf-8")
if hashlib.sha256(raw).hexdigest() != d["rescore_sha256"]:
    sys.exit("the shipped --rescore record does not match its sha256")
os.makedirs(os.path.dirname(sys.argv[2]), exist_ok=True); open(sys.argv[2], "wb").write(raw)' "$(dirname "$0")/job.json" "$R/ci-job/rescore.json" || finish 2;;
esac
targs=()  # eff-tm-partial (header): --budget S -> --deadline T0 + S
while [ $# -gt 0 ]; do
  if [ "$1" = --budget ] && [ $# -ge 2 ] && [[ $2 =~ ^[0-9]+$ ]]; then targs+=(--deadline $(( T0 + $2 ))); shift 2
  else targs+=("$1"); shift; fi; done
step trust_mutants uv run --frozen python tools/trust_mutants.py --base "$BASE" ${targs[@]+"${targs[@]}"} --json "$O/trust-mutants.json"
echo $? > "$O/tm.rc"
finish 0
