#!/bin/bash
# Cloud runner job for trust_mutants (2026-10-27 cloud plumbing; from the pilot's tm-job.sh). cloud-dispatch.sh embeds
# this file verbatim in the routine's prompt; the session writes it to /tmp/cloud-tm-job.sh and runs it detached.
# usage: cloud-tm-job.sh run <checkout> <out dir> <job> <head> <base> <asset url|-> <asset sha256|-> [trust_mutants args...]
#        cloud-tm-job.sh publish <checkout> <out dir> <job> <branch>
# run: checks HEAD = <head>, fetches history if <base> is missing, needs lean, lake, zstd and uv (exit 127 if one is
#   missing: without lake the Lean tests would skip silently), restores main's Lean build from the release asset (sha256
#   checked; any failure: cold build, logged), `uv sync --frozen`, the branch's incremental `lake build`, then
#   VE_LEAN_SHARE=off uv run --frozen python tools/trust_mutants.py --base <base> <args> --json <out>/trust-mutants.json.
#   Writes <out>/timings.tsv (step, rc, seconds), machine.txt, tm.rc (trust_mutants' exit code) and DONE (this script's).
# publish: copies the results (json, timings, machine, tm.rc, last 200 lines of each log) to cloud-results/<job>/,
#   commits ONLY that directory on top of <head> and pushes it to <branch> (no --force; one retry after 30 s).
# Tests only: CLOUD_TM_LEAN_BIN (a dir prepended to PATH), CLOUD_TM_TMP (default /tmp).
set -u
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
restored=""
# 2026-10-28 dri-sharedcache (flag SHARED_CACHE): a job script shipped with ve-cache.sh appended after its last line
# (ve-cache.sh bundle, by cloud-dispatch.sh / gha-job.sh) restores through it: key, sha256, member names and the seal
# (platform, lean --version) checked, exact/seed said, ve-cache.json written; any refusal = cold build. Else as before.
if [ "$URL" != - ] && grep -q -x '#VE-CACHE-SH-BEGIN' "$0" 2>/dev/null; then
  sed -n '/^#VE-CACHE-SH-BEGIN$/,$p' "$0" | tail -n +2 > "$T/ve-cache.sh"
  step cache_restore bash "$T/ve-cache.sh" restore lean-build --repo "$PWD" --url "$URL" --sha256 "$SUM" --report "$O/ve-cache.json" && restored=1
elif [ "$URL" != - ]; then
  if step cache_download curl -sSfL --retry 2 -o "$T/lean-cache.tar.zst" "$URL" \
     && step cache_sha256 bash -c "echo '$SUM  $T/lean-cache.tar.zst' | sha256sum -c -" \
     && step cache_restore bash -c "rm -rf '$T/lc' && mkdir -p '$T/lc' && zstd -dc '$T/lean-cache.tar.zst' | tar -x -C '$T/lc' && chmod -R u+w '$T/lc' && rm -rf lean/.lake/build && mkdir -p lean/.lake && mv '$T/lc/lake/build' lean/.lake/build"; then
    restored=1; fi
  rm -f "$T/lean-cache.tar.zst"
fi
[ -n "$restored" ] || echo "no cache restored: cold build" >> "$O/machine.txt"
step python_env uv sync --frozen || finish 2
(cd lean && step branch_lake_build lake build)
export VE_LEAN_SHARE=off
step trust_mutants uv run --frozen python tools/trust_mutants.py --base "$BASE" "$@" --json "$O/trust-mutants.json"
echo $? > "$O/tm.rc"
finish 0
#VE-CACHE-SH-BEGIN
#!/bin/bash
# ve-cache.sh: the ONE restore script for VE's shared caches, the same file in every place VE work runs (the VM, the Mac
# runner, Claude cloud ve-runner, Codex Cloud ve-runner-codex, GitHub Actions). 2026-10-28 dri-sharedcache,
# reviews/shared-cache-20261028.md. Portable bash (3.2 on the Mac), needs curl, python3, zstd, tar, sha256sum or shasum.
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
# Any failure: exit 3, lean/.lake untouched, one line saying why (the caller builds cold). Exit 0: restored, one line
# `ve-cache: lean-build <exact|seed> ...`; --report FILE gets the same facts as JSON (kind, match, key, asset, sha256,
# source local|download, seconds). The store: $VE_CACHE_DIR, else the first writable of /opt/ve-cache,
# /workspace/.tools/ve-cache, ${XDG_CACHE_HOME:-~/.cache}/ve-cache; read-only search also in ~/.cache/ve-cloud-cache (the
# VM's packs). Tests only: VE_CACHE_SEARCH (extra dirs, colon-separated), VE_CACHE_LEAN (the lean to ask for --version).
set -u
DEFAULT_MANIFEST=https://github.com/panaali/verifiable-english/releases/download/ve-cache/ve-cache-manifest.json
say(){ echo "ve-cache: $*" >&2; }
die(){ say "$1"; exit "${2:-3}"; }
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
store=${VE_CACHE_DIR:-}
if [ -z "$store" ]; then for d in /opt/ve-cache /workspace/.tools/ve-cache "${XDG_CACHE_HOME:-$HOME/.cache}/ve-cache"; do
  if mkdir -p "$d/lean-build" 2> /dev/null && [ -w "$d/lean-build" ]; then store=$d; break; fi; done; fi
[ -n "$store" ] || die "no writable store directory"
mkdir -p "$store/lean-build" || die "cannot create $store/lean-build"
search="$store/lean-build:/opt/ve-cache/lean-build:/workspace/.tools/ve-cache/lean-build:${XDG_CACHE_HOME:-$HOME/.cache}/ve-cache/lean-build:$HOME/.cache/ve-cloud-cache:${VE_CACHE_SEARCH:-}"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/ve-cache.XXXXXX") || die "no temp dir"; trap 'rm -rf "$tmp"' EXIT
t0=$(now)

getman(){ # the manifest into $tmp/manifest.json
  case $man in
    http://*|https://*) curl -sSfL --retry 2 --max-time 60 -o "$tmp/manifest.json" "$man" || return 1;;
    *) cp "$man" "$tmp/manifest.json" 2> /dev/null || return 1;; esac
  python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d.get("format")==1 and isinstance(d.get("assets"),list)' "$tmp/manifest.json" 2> /dev/null; }

if [ "$cmd" = list ]; then getman || die "manifest $man unreadable"
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
if [ -n "$url" ]; then name=$(basename "$url"); key=""; match=pinned
else
  getman || die "manifest $man unreadable: cold build"
  pick=$(python3 -I - "$tmp/manifest.json" "$platform" "$toolchain" "$want_tree" "$base" "$R" "$cmd" <<'PY'
import json, subprocess, sys
path, platform, toolchain, tree, base, repo, cmd = sys.argv[1:8]
a = [x for x in json.load(open(path))["assets"] if x.get("kind") == "lean-build" and x.get("url")
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
) || die "manifest pick failed"
  [ -n "$pick" ] || die "no lean-build asset for $platform ${toolchain:-?} in the manifest: cold build"
  IFS=$'\t' read -r name url want_sha key match <<< "$pick"
fi
case $name in lean-build-*.tar.zst) ;; *) die "unexpected asset name $name";; esac

# --- a verified local copy, else a verified download
file=""; src=local; IFS=: read -r -a dirs <<< "$search"
for d in "${dirs[@]}"; do [ -n "$d" ] && [ -s "$d/$name" ] || continue
  [ "$(sha "$d/$name")" = "$want_sha" ] && { file=$d/$name; break; }
  say "local $d/$name has another sha256: ignored"; done
if [ -z "$file" ]; then src=download
  curl -sSfL --retry 2 -o "$store/lean-build/$name.part" "$url" || { rm -f "$store/lean-build/$name.part"; die "download of $name failed: cold build"; }
  got=$(sha "$store/lean-build/$name.part")
  [ "$got" = "$want_sha" ] || { rm -f "$store/lean-build/$name.part"; die "sha256 of the downloaded $name is ${got:0:12}, not ${want_sha:0:12}: refused, cold build"; }
  mv "$store/lean-build/$name.part" "$store/lean-build/$name"; file=$store/lean-build/$name
  for old in $(ls -t "$store"/lean-build/lean-build-*.tar.zst 2> /dev/null | tail -n +3); do rm -f "$old"; done
fi
if [ "$cmd" = prefetch ]; then say "prefetched $name (sha256 ${want_sha:0:12} ok, $src) into ${file%/*}"; exit 0; fi

# --- member names, then extraction, then the seal
zstd -dc "$file" | tar -t > "$tmp/list" 2> /dev/null || die "$name does not list: refused"
grep -q -E '^/|(^|/)\.\.(/|$)' "$tmp/list" && die "$name has an absolute or .. member: refused"
grep -q -x 'pins.json' "$tmp/list" && grep -q '^lake/build/' "$tmp/list" || die "$name lacks pins.json or lake/build/: refused"
L=$R/lean/.cache/ve-cache-restore; rm -rf "$L"; mkdir -p "$L" || die "cannot create $L"
zstd -dc "$file" | tar -x -C "$L" 2> "$tmp/x.err" || { rm -rf "$L"; die "extracting $name failed: $(head -c 200 "$tmp/x.err")"; }
LEANV=$("${VE_CACHE_LEAN:-lean}" --version 2> /dev/null | head -1)
if ! seal=$(python3 -I - "$L/pins.json" "$(uname -s)" "$(uname -m)" "$LEANV" <<'PY'
import json, sys
k = json.load(open(sys.argv[1]))["key"]; system, machine, leanv = sys.argv[2:5]
p = k.get("platform", {})
if (p.get("system"), p.get("machine")) != (system, machine):
    sys.exit("seal platform %s-%s is not %s-%s" % (p.get("system"), p.get("machine"), system, machine))
if leanv and k.get("toolchain", {}).get("lean") != leanv:
    sys.exit("seal toolchain %r is not this lean %r" % (k.get("toolchain", {}).get("lean"), leanv))
print("seal ok" if leanv else "seal platform ok (no lean here to compare)")
PY
); then rm -rf "$L"; die "$name refused: $seal" ; fi
chmod -R u+w "$L" && rm -rf "$R/lean/.lake/build" && mkdir -p "$R/lean/.lake" && mv "$L/lake/build" "$R/lean/.lake/build" \
  || { rm -rf "$L"; die "moving the build into $R/lean/.lake failed"; }
rm -rf "$L"
secs=$(python3 -c "import sys; print('%.1f' % (float(sys.argv[2]) - float(sys.argv[1])))" "$t0" "$(now)")
[ "$match" = pinned ] && { [ "${name#lean-build-}" = "${want_tree:0:12}.tar.zst" ] && match=exact || match=seed-pinned; }
say "lean-build $match key ${want_tree:0:12} asset $name sha256 ${want_sha:0:12} ok, $seal, from $src, ${secs} s"
if [ -n "$report" ]; then python3 -I -c 'import json,sys; k=["kind","match","key","asset","sha256","source","seconds","platform"]
json.dump(dict(zip(k, sys.argv[2:])), open(sys.argv[1], "w"))' "$report" lean-build "$match" "$want_tree" "$name" "$want_sha" "$src" "$secs" "$platform"; fi
exit 0
