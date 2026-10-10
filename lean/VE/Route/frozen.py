"""Hash test for the reviewed trusted Lean source inventory.

Usage (from lean/): python3 VE/Route/frozen.py        exits 0 iff unchanged.
                    python3 VE/Route/frozen.py --write rehashes every `VE/**/*.lean` module into
                    the inventory (after a reviewed edit or a merge of reviewed branches;
                    tools/regen_generated.py runs it); `Main.lean` is still only checked.
`frozen-sources.sha256` lists every reviewed `VE/*.lean` module,
including the audit manifest, service protocol and generated English runner
copy. New modules must be added to the manifest before this check passes.
`Main.lean` with those two lines removed must hash to the base file.
"""
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MAIN_BASE = "1bd244f8ff087d3f81e7302a0938ceab9d107e9efd609d97e41b23c0eb36c26d"
ROUTE_LINES = ("import VE.Route.Run\n",
               '  if let "route" :: rest := args then return ← VE.Route.Run.main rest\n')


def inventory_text():
    """The inventory of the tree as it is: one `<sha256>  <path>` line per `VE/**/*.lean`, by path."""
    names = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "VE").rglob("*.lean"))
    return "".join(f"{hashlib.sha256((ROOT / name).read_bytes()).hexdigest()}  {name}\n" for name in names)


def main(argv=()):
    if list(argv) == ["--write"]:
        (HERE / "frozen-sources.sha256").write_text(inventory_text())
    elif list(argv):
        raise SystemExit("usage: python3 VE/Route/frozen.py [--write]")
    bad = []
    recorded = set()
    for line in (HERE / "frozen-sources.sha256").read_text().splitlines():
        expected, name = line.split(maxsplit=1)
        recorded.add(name)
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != expected:
            bad.append(name)
    trusted = {str(path.relative_to(ROOT)) for path in (ROOT / "VE").rglob("*.lean")}
    for name in sorted(trusted - recorded):
        bad.append(f"unlisted trusted module: {name}")
    for name in sorted(recorded - trusted):
        bad.append(f"obsolete trusted module: {name}")
    text = (ROOT / "Main.lean").read_text()
    for route_line in ROUTE_LINES:
        if text.count(route_line) != 1:
            bad.append(f"Main.lean: expected exactly one {route_line.strip()!r}")
        text = text.replace(route_line, "")
    if hashlib.sha256(text.encode()).hexdigest() != MAIN_BASE:
        bad.append("Main.lean: existing subcommands changed")
    if bad:
        print("CHANGED:", *bad, sep="\n  ")
        return 1
    print("PASS: frozen Lean sources and Main.lean subcommands unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
