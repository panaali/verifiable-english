"""Reject new outward Lean imports and stale, exact legacy exceptions."""
from __future__ import annotations

import json
import re
import sys

from layer_policy import ROOT, lean_layer

LEDGER = ROOT / "tools/lean-layer-exceptions.json"
# Lean reads `import` as a keyword token anywhere in the header: after `prelude`
# or a modifier on the same line (`public import`), with its module on a later
# line, or directly before a «quoted» name. Only a preceding or following
# identifier character (or a `.` before it) makes the word part of a name.
IMPORT = re.compile(r"(?<![\w.'!?«»])import(?![\w'!?])\s*(.+)$", re.MULTILINE)
QUOTED_IDENT = re.compile(r"«([^»]+)»")
IMPORT_NAME = re.compile(r"(?:«[^»]*»|[^\s«»])+")
OPENER = re.compile(r'--|/-|"')
BLOCK = re.compile(r"/-|-/")
STRING_END = re.compile(r'\\[\s\S]?|"')
NOT_NEWLINE = re.compile(r"[^\n]")


def imports(source: str) -> list[str]:
    """Read import commands after erasing nested Lean comments and strings.

    Erased text becomes spaces (newlines kept); the scan jumps between comment
    and string delimiters, so whole files are cheap to read.
    """
    clean = []
    index = 0
    while (opener := OPENER.search(source, index)):
        clean.append(source[index:opener.start()])
        if opener[0] == "--":
            end = source.find("\n", opener.start())
            end = len(source) if end < 0 else end
        elif opener[0] == "/-":
            depth, end = 1, opener.end()
            while depth and (mark := BLOCK.search(source, end)):
                depth += 1 if mark[0] == "/-" else -1
                end = mark.end()
            end = end if not depth else len(source)
        else:
            end = opener.end()
            while (mark := STRING_END.search(source, end)):
                end = mark.end()
                if mark[0] == '"':
                    break
            else:
                end = len(source)
        clean.append(NOT_NEWLINE.sub(" ", source[opener.start():end]))
        index = end
    clean.append(source[index:])
    return [QUOTED_IDENT.sub(r"\1", name)
            for group in IMPORT.findall("".join(clean))
            for name in IMPORT_NAME.findall(group)]


def main() -> int:
    paths = {".".join(path.relative_to(ROOT / "lean").with_suffix("").parts): path
             for path in (ROOT / "lean").rglob("*.lean") if ".lake" not in path.parts}
    unmapped = sorted(module for module in paths if lean_layer(module) is None)
    edges = set()
    unknown = set()
    for importer, path in paths.items():
        for imported in imports(path.read_text()):
            if imported not in paths:
                if imported.startswith("VE.") or imported in {"VE", "Iceberg"}:
                    unknown.add(f"{importer} -> {imported}")
                continue  # Lean and Std library imports
            importer_layer = lean_layer(importer)
            imported_layer = lean_layer(imported)
            if importer_layer is not None and imported_layer is not None and importer_layer < imported_layer:
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
