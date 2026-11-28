# Shared by the tour's stop scripts (sourced, not run). Every stop runs from the repository root, whatever the
# directory you call it from; a stop that needs branch after-release runs in the checkout tour/install.sh made.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
AFTER_RELEASE="$ROOT/.tour-after-release"
export PATH="$HOME/.local/bin:$HOME/.elan/bin:$HOME/.cargo/bin:$PATH"
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

# show_status STOP COMMAND...: show_run COMMAND, with the line from tour/TEXTS.md after each Lean line of its output
# (tour/stops/status.py reads that line from the table "The line after each Lean line")
# (unbuffered, so a long stop prints as it goes and its stderr stays in place); an output with no Lean line stops it
show_status() {
    stop=$1; shift
    export PYTHONUNBUFFERED=1
    if [ -n "${VE_TOUR_PYTHON:-}" ]; then
        show_run "$@" 2>&1 | "$VE_TOUR_PYTHON" "$ROOT/tour/stops/status.py" "$stop"
    else
        show_run "$@" 2>&1 | uv run --frozen python "$ROOT/tour/stops/status.py" "$stop"
    fi
}

# on_after_release: move into the after-release checkout (this stop's feature is not on main yet)
on_after_release() {
    [ -d "$AFTER_RELEASE" ] || { echo "This stop needs the after-release checkout: run sh tour/install.sh first." >&2; exit 1; }
    cd "$AFTER_RELEASE"
    [ -z "${VE_TOUR_PYTHON:-}" ] || VE_TOUR_PYTHON="$AFTER_RELEASE/.venv/bin/python"
    echo "(this stop runs from branch after-release, in .tour-after-release/)"
}
