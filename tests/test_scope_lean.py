"""scope@0's Lean core (sc-1a): the layout's list runs and the effects on a rule's JSON object.

The fixtures themselves are Lean: `lean/VE/Scope/Examples.lean` holds the spec's 7.1 fixtures as kernel theorems
(`decide`) and `#guard`s, checked by every `lake build`. This file checks what standing ruling R16 asks of the
trusted lines the item adds: every trusted definition of `lean/VE/Layout/` and `lean/VE/Scope/` is stated about by
some theorem (the compiled `-- uses` lines of `lean/statements.txt`, read through `tools/trust_map.py`'s own trust
rule), and each tie the side table records names a theorem about it."""

from pathlib import Path

from tools import trust_map

ROOT = Path(__file__).resolve().parents[1]
STATEMENTS = ROOT / "lean/statements.txt"


def scope_modules() -> list[str]:
    files = [*(ROOT / "lean/VE/Layout").glob("*.lean"), *(ROOT / "lean/VE/Scope").glob("*.lean")]
    return sorted(trust_map.module_key(p, ROOT) for p in files)


def test_the_scope_files_are_classified():
    table = trust_map.load_table()
    modules = scope_modules()
    assert {"VE/Layout/List.lean", "VE/Scope/Effects.lean", "VE/Scope/Examples.lean"} <= set(modules)
    assert all(module in table for module in modules if module != "VE/Scope/Theorems.lean")


def test_every_trusted_scope_definition_is_used_by_a_theorem():
    proved = trust_map.statements(STATEMENTS)
    assert proved, "lean/statements.txt is missing or empty; run tools/lean_statements.py"
    assert trust_map.unexercised(trust_map.load_table(), proved, scope_modules()) == []


def test_each_tie_names_a_theorem_about_its_definition():
    proved = trust_map.statements(STATEMENTS)
    entries = trust_map.load_table()["VE/Layout/List.lean"]
    ties = {name: entry["tied"] for name, entry in entries.items() if isinstance(entry, dict)}
    assert set(ties) == {"VE.Layout.continues", "VE.Layout.indexOf", "VE.Layout.listRun", "VE.Layout.runFrom"}
    for name, theorems in ties.items():
        for theorem in theorems:
            assert ("VE.Layout.List", name) in proved[theorem], (name, theorem)
    # listRun's meaning is the independent statement GovernedItem (spec 5.1)
    assert ("VE.Layout.List", "VE.Layout.GovernedItem") in proved["VE.Layout.listRun_iff"]


def test_a_definition_no_theorem_uses_is_reported():
    """The check can fail: drop every theorem that uses `mergeParts` and it names exactly that definition."""
    table = trust_map.load_table()
    proved = trust_map.statements(STATEMENTS)
    merge = ("VE.Scope.Effects", "VE.Scope.mergeParts")
    without = {theorem: found for theorem, found in proved.items() if not found or merge not in found}
    assert trust_map.unexercised(table, without, scope_modules()) == ["VE/Scope/Effects.lean: VE.Scope.mergeParts"]
