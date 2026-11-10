"""Spec section 5 of docs/spec/premise-packs.md against the stub's checked plan (pk-1s-cfr-1).

Every file in section 5's file table is in the stub's `planFiles`, or both its row and the stub's section-5 comment
say it is "not in the checked plan" (and such a row's imports are the built file's); every `planFiles` entry is a row;
and no import the table plans points outward under tools/layer_policy.py (check_lean_imports' rule, ledger aside).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_lean_imports import imports as lean_imports  # noqa: E402
from layer_policy import lean_layer  # noqa: E402

SPEC = ROOT / "docs/spec/premise-packs.md"
STUB = ROOT / "docs/spec/premise-packs/SpecStubs_pk1.lean"
MARK = "not in the checked plan"
TOKEN = r"`([^`\s]+)`(?!'s)"  # a backticked name, not a possessive ("`Layered.lean`'s own imports")


def file_rows() -> list[list[str]]:
    """Section 5's file table, as cells."""
    lines = SPEC.read_text().split("## 5. ", 1)[1].splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("| File, in import order"))
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def key(cell: str) -> str:
    """A file cell's `lean/...` path, or its text in lower case (the first provider)."""
    path = re.search(r"`?(lean/[^`\s]+\.lean)", cell)
    return path.group(1) if path else re.sub(r"\s+", " ", cell).lower()


def plan_section() -> tuple[str, list[str]]:
    """The stub's section-5 comment (one line) and the `file` of every `planFiles` entry."""
    section = STUB.read_text().split("/-! ## 5 ", 1)[1]
    body = section.split("def planFiles", 1)[1].split("\n\n", 1)[0]
    return " ".join(section.split("-/", 1)[0].split()), re.findall(r'⟨"([^"]+)"', body)


def module(token: str, row_file: str) -> str | None:
    """The existing Lean module a token names: dotted, a path under lean/VE/, or a file in the row's directory."""
    if token.startswith(("VE.", "ResponseShape.")) and not token.endswith(".lean"):
        base = token.replace(".", "/")
    elif re.fullmatch(r"[A-Z][\w/]*", name := token.removesuffix(".lean")):
        base = "VE/" + name if "/" in name else str(Path(row_file).parent.relative_to("lean")) + "/" + name
    else:
        return None
    return base.replace("/", ".") if (ROOT / "lean" / f"{base}.lean").exists() else None


def test_every_table_file_is_planned_or_marked():
    comment, planned = plan_section()
    planned_keys = {key(f) for f in planned}
    for row in file_rows():
        path, marked = key(row[0]), MARK in " ".join(row)
        assert marked != (path in planned_keys), f"spec 5's row {row[0]}: in planFiles exactly when not '{MARK}'"
        if marked:
            assert f"`{Path(path).name}` is {MARK}" in comment, \
                f"the stub's section-5 comment does not say that {Path(path).name} is {MARK}"
            built = [module(t, path) for t in re.findall(TOKEN, row[1])]
            assert built == lean_imports((ROOT / path).read_text()), f"{row[0]}: imports not as built"


def test_every_plan_file_is_a_table_row():
    _, planned = plan_section()
    rows = {key(row[0]) for row in file_rows()}
    assert len(planned) >= 5 and len(rows) >= 6
    assert [f for f in planned if key(f) not in rows] == []


def test_planned_imports_respect_layers():
    bad = []
    for row in file_rows():
        path = key(row[0])
        if not path.startswith("lean/"):
            continue
        own = path.removeprefix("lean/").removesuffix(".lean").replace("/", ".")
        ims, importers = ([module(t, path) for t in re.findall(TOKEN, cell)] for cell in row[1:3])
        bad += [f"{row[0]}: a name is no module" for m in ims + importers if m is None]
        bad += [f"{a} (layer {lean_layer(a)}) imports {b} (layer {lean_layer(b)})"
                for a, b in [(own, m) for m in ims if m] + [(m, own) for m in importers if m]
                if lean_layer(a) < lean_layer(b)]
    assert not bad, "spec 5 plans imports the layer policy refuses:\n" + "\n".join(bad)
