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
    "$@" || status=$?
    [ "$status" = 0 ] || echo "[exit code $status]"
}

# on_after_release: move into the after-release checkout (this stop's feature is not on main yet)
on_after_release() {
    [ -d "$AFTER_RELEASE" ] || { echo "This stop needs the after-release checkout: run sh tour/install.sh first." >&2; exit 1; }
    cd "$AFTER_RELEASE"
    echo "(this stop runs from branch after-release, in .tour-after-release/)"
}
