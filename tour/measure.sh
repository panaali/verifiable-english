#!/bin/sh
# Measure the tour from a clean copy, as a newcomer would run it, and check every stop's output against
# tour/expected/. Usage:  sh tour/measure.sh REPOSITORY BRANCH WORKDIR [--fresh-home] [--from-source]
#   REPOSITORY: a URL or path to clone; BRANCH: the branch with the tour; WORKDIR: a new, empty directory.
#   --fresh-home: HOME=WORKDIR/home, so uv, Lean and Rust are downloaded as on a machine that never had them
#   (system packages such as git and a C compiler must already be there).
#   --from-source: time `sh tour/install.sh --from-source` (the builds) instead of the prebuilt programs.
#   VE_TOUR_PREBUILT (environment): where the install fetches the prebuilt archive from (its default: the published URL).
# Prints the seconds of: the clone, the install, the first answer (clone start to the end of stop 1), all ten stops,
# and the total; then one line per stop: its seconds and "same" or "DIFFERS" against tour/expected/<stop>.txt.
set -eu
REPO=$1; BRANCH=$2; WORK=$3; shift 3
FRESH=""; ROUTE=""
for opt in "$@"; do
    case $opt in --fresh-home) FRESH=$opt ;; --from-source) ROUTE=$opt ;; *) echo "unknown option $opt" >&2; exit 2 ;; esac
done
mkdir "$WORK"
WORK=$(CDPATH= cd -- "$WORK" && pwd)
if [ "$FRESH" = --fresh-home ]; then
    export HOME="$WORK/home"; mkdir "$HOME"
    PATH=$(printf '%s' "$PATH" | tr ':' '\n' | grep -v -e '/\.local/bin$' -e '/\.elan/bin$' -e '/\.cargo/bin$' | paste -sd: -)
    export PATH
    unset CARGO_HOME RUSTUP_HOME ELAN_HOME UV_CACHE_DIR || true
fi
now() { date +%s; }
START=$(now)
git clone -q --branch "$BRANCH" "$REPO" "$WORK/verifiable-english"
CLONED=$(now)
cd "$WORK/verifiable-english"
sh tour/install.sh $ROUTE > "$WORK/install.log" 2>&1 || { tail -n 30 "$WORK/install.log"; echo "install failed" >&2; exit 1; }
INSTALLED=$(now)
mkdir "$WORK/out"
first=""
results=""
for script in tour/stops/[0-9]*.sh; do
    stop=$(basename "$script" .sh)
    t0=$(now)
    sh "$script" 2>&1 | grep -v -E '^ *((Building|Built) [A-Za-z0-9_.-]+ @ file://[^ ]+$|(Uninstalled|Installed|Resolved|Prepared|Audited) [0-9]+ packages? in [0-9.]+m?s$|Using CPython [^ ]+ interpreter at: [^ ]+$)' \
        > "$WORK/out/$stop.txt" || true
    t1=$(now)
    [ -n "$first" ] || first=$t1
    if cmp -s "$WORK/out/$stop.txt" "tour/expected/$stop.txt"; then same=same; else same=DIFFERS; fi
    results="$results$stop $((t1 - t0)) s $same
"
done
END=$(now)
echo "route: ${ROUTE:-prebuilt}${VE_TOUR_PREBUILT:+ (archive from $VE_TOUR_PREBUILT)}"
echo "clone: $((CLONED - START)) s"
echo "install: $((INSTALLED - CLONED)) s"
echo "first answer (from the start of the clone): $((first - START)) s"
echo "all ten stops: $((END - INSTALLED)) s"
echo "total: $((END - START)) s"
printf '%s' "$results"
echo "commit: $(git rev-parse --short=10 HEAD); after-release: $(git -C .tour-after-release rev-parse --short=10 HEAD)"
grep -E '==> .*done in|still running' "$WORK/install.log" || true
