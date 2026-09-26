"""Hash test for PLAN-EXPAND2 3.10(1): the v0, closure and order Lean sources
and the existing `Main.lean` subcommands are unchanged by the route.

Usage (from lean/): python3 VE/Route/frozen.py        exits 0 iff unchanged.
`frozen-sources.sha256` lists every Lean source file of the base commit that
P0-Lean did not edit (the v0, closure, order, bridge and surface files, among
others). The files P0-Lean edits are exactly: VE/ClaimGraph.lean (the label
field), VE/GraphChecks.lean and VE/TableauChecks.lean (structure-instance
syntax for the labelled Claim), VE/Audit.lean and VE.lean (imports and audit
entries), Main.lean (one import and the `route` dispatch line), and VE/Route/*.
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


def main():
    bad = []
    for line in (HERE / "frozen-sources.sha256").read_text().splitlines():
        expected, name = line.split(maxsplit=1)
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != expected:
            bad.append(name)
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
    sys.exit(main())
