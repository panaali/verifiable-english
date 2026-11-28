# Shared by the tour's stop scripts (sourced, not run). Every stop runs from the repository root, whatever the
# directory you call it from; a stop that needs branch after-release runs in the checkout tour/install.sh made.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
AFTER_RELEASE="$ROOT/.tour-after-release"
export PATH="$HOME/.local/bin:$HOME/.elan/bin:$HOME/.cargo/bin:$PATH"
# `ve read` offers its AI reader once, on its first run on a machine: no stop shows that offer, so the stops count it
# as made (stop 12 then prints what this page shows; your own `ve read` of your own file still makes the offer)
export VE_READER_OFFER=off
cd "$ROOT"

# show_run COMMAND...: print the command (as you would type it), run it, and print its exit code when it is not 0
# (a refusal is an expected outcome on some stops, so the stop goes on)
show_run() {
    printf '$'
    for word in "$@"; do
        case $word in
            *[!A-Za-z0-9_./:=-]*) printf ' "%s"' "$word" ;;
            *) printf ' %s' "$word" ;;
        esac
    done
    printf '\n'
    status=0
    # VE_TOUR_PYTHON (set by the tour's test, tests/test_tour.py): run "uv run --frozen python ..." with that Python
    if [ -n "${VE_TOUR_PYTHON:-}" ] && [ "$1 $2 $3 $4" = "uv run --frozen python" ]; then
        shift 4
        set -- "$VE_TOUR_PYTHON" "$@"
    fi
    "$@" || status=$?
    [ "$status" = 0 ] || echo "[exit code $status]"
}

# on_after_release: move into the after-release checkout (this stop's feature is not on main yet)
on_after_release() {
    [ -d "$AFTER_RELEASE" ] || { echo "This stop needs the after-release checkout: run sh tour/install.sh first." >&2; exit 1; }
    cd "$AFTER_RELEASE"
    [ -z "${VE_TOUR_PYTHON:-}" ] || VE_TOUR_PYTHON="$AFTER_RELEASE/.venv/bin/python"
    echo "(this stop runs from branch after-release, in .tour-after-release/)"
}
