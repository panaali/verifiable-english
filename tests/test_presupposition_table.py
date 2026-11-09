"""ps-2a: `lean/VE/Presupposition/Table.lean` is PS-E1's candidate table (presupposition spec section 6), generated."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _generator():
    spec = importlib.util.spec_from_file_location("presupposition_table_tool", ROOT / "tools/presupposition_table.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_lean_table_is_the_e1_table():
    """The file is the rendering of the JSON, one arm per non-empty cell, and the Lean build reads it."""
    gen = _generator()
    text = gen.TARGET.read_text()
    assert text == gen.render()
    rows = json.loads(gen.SOURCE.read_text())
    assert [r["row"] for r in rows] == ["definite", "plural", "generic"]
    for row in rows:
        for name, cands in row["cells"].items():
            arm = f'  | "{row["row"]}", .{gen.CLASSES[name]} => ['
            assert (arm in text) == bool(cands)
    assert '  | "generic", .consequent => [.assumed, .unconditional]\n' in text
    assert "import VE.Presupposition.Table" in (ROOT / "lean/VE.lean").read_text().splitlines()


def test_a_changed_table_changes_the_rendering():
    """The other direction: the rendering follows the JSON (order kept, in place spelled `.inPlace`)."""
    gen = _generator()
    rows = json.loads(gen.SOURCE.read_text())
    changed = copy.deepcopy(rows)
    changed[0]["cells"]["negated"] = ["conditioned", "in_place"]
    text = gen.render(changed)
    assert text != gen.render(rows)
    assert '  | "definite", .negated => [.conditioned, .inPlace]\n' in text


@pytest.mark.parametrize("edit", ["unknown candidate", "missing class", "extra class", "repeated row"])
def test_names_outside_the_spec_are_refused(edit):
    gen = _generator()
    rows = json.loads(gen.SOURCE.read_text())
    if edit == "unknown candidate":
        rows[0]["cells"]["top"] = ["presumed"]
    elif edit == "missing class":
        del rows[0]["cells"]["disjunct"]
    elif edit == "extra class":
        rows[0]["cells"]["heading"] = []
    else:
        rows.append(copy.deepcopy(rows[0]))
    with pytest.raises((KeyError, ValueError)):
        gen.render(rows)
