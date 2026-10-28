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
: > "$O/steps.rc"
for spec in "$@"; do name=${spec%%=*}; cmd=${spec#*=}
  [[ $name =~ ^[A-Za-z0-9_-]+$ ]] || { echo "$spec: bad step name" >> "$O/machine.txt"; continue; }
  step "$name" bash -c "$cmd"; echo "$name $?" >> "$O/steps.rc"; done
finish 0
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
