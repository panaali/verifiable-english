"""Spec section 5 of docs/spec/premise-packs.md against the stub's checked plan (pk-1s-cfr-1).

Every file in section 5's file table is in the stub's `planFiles`, or both the table row and the stub's section-5
comment say it is "not in the checked plan"; and no import the table plans (its Imports and Imported by columns)
points from a lower layer to a higher one under tools/layer_policy.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from layer_policy import lean_layer  # noqa: E402

SPEC = ROOT / "docs/spec/premise-packs.md"
STUB = ROOT / "docs/spec/premise-packs/SpecStubs_pk1.lean"
MARK = "not in the checked plan"
TOKEN = r"`([^`\s]+)`(?!'s)"  # a backticked name, not a possessive ("`Layered.lean`'s own imports")


def file_rows() -> list[list[str]]:
    """Section 5's file table: the rows after its `| File, in import order |` header, as cells."""
    lines = SPEC.read_text().split("## 5. ", 1)[1].splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("| File, in import order"))
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def key(cell: str) -> str:
    """A file cell's path (its first backticked `lean/...` path), or its text in lower case (the first provider)."""
    path = re.search(r"`?(lean/[^`\s]+\.lean)", cell)
    return path.group(1) if path else re.sub(r"\s+", " ", cell).lower()


def plan_section() -> tuple[str, list[str]]:
    """The stub's section-5 comment and the `file` of every `planFiles` entry."""
    text = STUB.read_text()
    section = text.split("/-! ## 5 ", 1)[1]
    comment = section.split("-/", 1)[0]
    body = section.split("def planFiles", 1)[1].split("\n\n", 1)[0]
    return comment, re.findall(r'⟨"([^"]+)"', body)


def module(token: str, row_file: str) -> str | None:
    """The Lean module a backticked token of a row names: a dotted `VE.`/`ResponseShape.` name, a path under
    lean/VE/, or a bare file name in the row's own directory."""
    if token.startswith(("VE.", "ResponseShape.")) and not token.endswith(".lean"):
        return token
    name = token.removesuffix(".lean")
    if not re.fullmatch(r"[A-Z][\w/]*", name):
        return None
    base = "VE/" + name if "/" in name else str(Path(row_file).parent.relative_to("lean")) + "/" + name
    return base.replace("/", ".") if (ROOT / "lean" / f"{base}.lean").exists() else None


def test_every_table_file_is_planned_or_marked():
    comment, planned = plan_section()
    planned_keys = {key(f) for f in planned}
    unplanned = [row for row in file_rows() if key(row[0]) not in planned_keys]
    for row in unplanned:
        name = Path(key(row[0])).name
        assert MARK in " ".join(row), f"spec 5's row {row[0]} is not in planFiles and does not say '{MARK}'"
        assert name in comment and MARK in comment, \
            f"the stub's section-5 comment does not say that {name} is {MARK}"


def test_planned_imports_respect_layers():
    bad = []
    for row in file_rows():
        path = key(row[0])
        if not path.startswith("lean/"):
            continue
        own = path.removeprefix("lean/").removesuffix(".lean").replace("/", ".")
        imports, importers = ([module(t, path) for t in re.findall(TOKEN, cell)] for cell in row[1:3])
        bad += [f"{row[0]}: an import or importer names no module" for m in imports + importers if m is None]
        edges = [(own, m) for m in imports if m] + [(m, own) for m in importers if m]
        bad += [f"{a} (layer {lean_layer(a)}) imports {b} (layer {lean_layer(b)})"
                for a, b in edges if lean_layer(a) < lean_layer(b)]
    assert not bad, "spec 5 plans imports the layer policy refuses:\n" + "\n".join(bad)
