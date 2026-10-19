"""scope@0's Lean core (sc-1a, sc-3a): the layout's list runs, label reaches and anchors.

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
    assert {"VE/Layout/Anchors.lean", "VE/Layout/Discourse.lean", "VE/Layout/List.lean",
            "VE/Scope/Examples.lean"} <= set(modules)
    assert all(module in table for module in modules)


def test_every_trusted_scope_definition_is_used_by_a_theorem():
    proved = trust_map.statements(STATEMENTS)
    assert proved, "lean/statements.txt is missing or empty; run tools/lean_statements.py"
    assert trust_map.unexercised(trust_map.load_table(), proved, scope_modules()) == []


TIES = {
    "VE/Layout/List.lean": {"VE.Layout.continues", "VE.Layout.indexOf", "VE.Layout.listRun", "VE.Layout.runFrom",
                            "VE.Layout.itemFrom", "VE.Layout.itemRun"},
    "VE/Layout/Anchors.lean": {"VE.Layout.anchorReach", "VE.Layout.anchorUnits"},
    # discourse's containment and anchor checks are one-line calls of the moved bodies (sc-3a)
    "VE/Discourse/Access.lean": {"VE.Discourse.within", "VE.Discourse.innermostAnchor"},
    "VE/Discourse/WellFormed.lean": {"VE.Discourse.anchorsOk"},
}


def test_each_tie_names_a_theorem_about_its_definition():
    proved = trust_map.statements(STATEMENTS)
    table = trust_map.load_table()
    for module, expected in TIES.items():
        entries = table[module]
        ties = {name: entry["tied"] for name, entry in entries.items() if isinstance(entry, dict)}
        assert expected <= set(ties), module
        source = module.removesuffix(".lean").replace("/", ".")
        for name in expected:
            for theorem in ties[name]:
                assert (source, name) in proved[theorem], (name, theorem)
    # listRun's and itemRun's meanings are the independent statements GovernedItem and ItemUnit (spec 5.1, 5.5)
    assert ("VE.Layout.List", "VE.Layout.GovernedItem") in proved["VE.Layout.listRun_iff"]
    assert ("VE.Layout.List", "VE.Layout.ItemUnit") in proved["VE.Layout.itemRun_iff"]
    # anchorReach's meaning is the moved containment body `within` (spec 5.5), which discourse calls
    assert ("VE.Layout.Anchors", "VE.Layout.within") in proved["VE.Layout.anchorReach_iff"]
    assert ("VE.Layout.Anchors", "VE.Layout.within") in proved["VE.Layout.discourse_within_unchanged"]
    assert ("VE.Layout.Anchors", "VE.Layout.anchorsOk") in proved["VE.Layout.discourse_anchorsOk_unchanged"]


def test_a_definition_no_theorem_uses_is_reported():
    """The check can fail: drop every theorem that uses `ofSource` and it names exactly that definition."""
    table = trust_map.load_table()
    proved = trust_map.statements(STATEMENTS)
    source = ("VE.Layout.List", "VE.Layout.ofSource")
    without = {theorem: found for theorem, found in proved.items() if not found or source not in found}
    assert trust_map.unexercised(table, without, scope_modules()) == ["VE/Layout/List.lean: VE.Layout.ofSource"]
