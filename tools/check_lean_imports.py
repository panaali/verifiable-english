"""Reject new outward Lean imports and stale, exact legacy exceptions."""
from __future__ import annotations

import json
import re
import sys

from layer_policy import ROOT, lean_layer

LEDGER = ROOT / "tools/lean-layer-exceptions.json"
IMPORT = re.compile(r"^\s*import\s+(.+)$", re.MULTILINE)


def main() -> int:
    paths = {".".join(path.relative_to(ROOT / "lean").with_suffix("").parts): path
             for path in (ROOT / "lean").rglob("*.lean") if ".lake" not in path.parts}
    unmapped = sorted(module for module in paths if lean_layer(module) is None)
    edges = set()
    unknown = set()
    for importer, path in paths.items():
        for group in IMPORT.findall(path.read_text()):
            for imported in group.split("--", 1)[0].split():
                if imported not in paths:
                    if imported.startswith("VE.") or imported in {"VE", "Iceberg"}:
                        unknown.add(f"{importer} -> {imported}")
                    continue  # Lean and Std library imports
                if lean_layer(importer) < lean_layer(imported):
                    edges.add(f"{importer} -> {imported}")
    expected = json.loads(LEDGER.read_text())
    for message in (f"unmapped Lean module: {x}" for x in unmapped):
        print(message, file=sys.stderr)
    for message in (f"missing local Lean import: {x}" for x in sorted(unknown)):
        print(message, file=sys.stderr)
    for edge in sorted(edges - expected.keys()):
        print(f"new outward Lean import: {edge}", file=sys.stderr)
    for edge in sorted(expected.keys() - edges):
        print(f"stale Lean exception: {edge}", file=sys.stderr)
    if unmapped or unknown or edges != expected.keys():
        return 1
    print(f"Lean layer graph kept ({len(paths)} modules, {len(edges)} reviewed legacy edges)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
