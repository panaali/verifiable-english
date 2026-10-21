"""scope@0's Lean core (sc-1a, sc-3a, sc-1ab, sc-1ac, sc-1ad): the layout's list runs, label reaches and anchors, the
effects on a rule's JSON object, and `govern` with the block's admission, the graph step and the run path.

The fixtures themselves are Lean: `lean/VE/Scope/Examples.lean` holds the spec's 7.1 fixtures as kernel theorems
(`decide`) and `#guard`s, checked by every `lake build`. This file checks what standing ruling R16 asks of the
trusted lines the item adds: every trusted definition of `lean/VE/Layout/` and `lean/VE/Scope/` is stated about by
some theorem (the compiled `-- uses` lines of `lean/statements.txt`, read through `tools/trust_map.py`'s own trust
rule), and each tie the side table records names a theorem about it."""

from pathlib import Path

import pytest

from tools import trust_map

ROOT = Path(__file__).resolve().parents[1]
STATEMENTS = ROOT / "lean/statements.txt"


def scope_modules() -> list[str]:
    files = [*(ROOT / "lean/VE/Layout").glob("*.lean"), *(ROOT / "lean/VE/Scope").glob("*.lean")]
    return sorted(trust_map.module_key(p, ROOT) for p in files)


def test_the_scope_files_are_classified():
    table = trust_map.load_table()
    modules = scope_modules()
    assert {"VE/Layout/Anchors.lean", "VE/Layout/Discourse.lean", "VE/Layout/List.lean", "VE/Scope/Effects.lean",
            "VE/Scope/Examples.lean", "VE/Scope/Govern.lean", "VE/Scope/Theorems.lean"} <= set(modules)
    assert all(module in table for module in modules)


def test_every_trusted_scope_definition_is_used_by_a_theorem():
    proved = trust_map.statements(STATEMENTS)
    assert proved, "lean/statements.txt is missing or empty; run tools/lean_statements.py"
    assert trust_map.unexercised(trust_map.load_table(), proved, scope_modules()) == []


TIES = {
    "VE/Layout/List.lean": {"VE.Layout.continues", "VE.Layout.indexOf", "VE.Layout.listRun", "VE.Layout.runFrom",
                            "VE.Layout.itemFrom", "VE.Layout.itemRun"},
    "VE/Layout/Anchors.lean": {"VE.Layout.anchorReach", "VE.Layout.anchorUnits"},
    "VE/Scope/Govern.lean": {"VE.Scope.coversU", "VE.Scope.governorsOf", "VE.Scope.itemRule", "VE.Scope.ruleTable",
                             "VE.Scope.edgesFor", "VE.Scope.governFast", "VE.Scope.fastReads", "VE.Scope.frameOnF",
                             "VE.Scope.baseObjF", "VE.Scope.coveredBy", "VE.Scope.governorsOfF", "VE.Scope.composedF",
                             "VE.Scope.edgesOfF", "VE.Scope.governBody"},
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
    # governorsOf's meaning is `covered` and `unary`; itemRule's is `mergeParts` and the chain's decoder (spec 5.1)
    assert ("VE.Scope.Govern", "VE.Scope.covered") in proved["VE.Scope.governorsOf_iff"]
    assert ("VE.Scope.Effects", "VE.Scope.mergeParts") in proved["VE.Scope.itemRule_decoder"]
    # the run path's meaning is `govern` (spec 5.1), each of its steps `govern`'s step (sc-1ad)
    assert ("VE.Scope.Govern", "VE.Scope.govern") in proved["VE.Scope.governFast_eq"]
    assert ("VE.Scope.Govern", "VE.Scope.govern") in proved["VE.Scope.governBody_slow"]


def unexercised_without(module: str, name: str) -> list[str]:
    """The unexercised definitions once every theorem that uses `name` of `module` is dropped."""
    proved = trust_map.statements(STATEMENTS)
    without = {theorem: found for theorem, found in proved.items() if not found or (module, name) not in found}
    return trust_map.unexercised(trust_map.load_table(), without, scope_modules())


def test_a_definition_no_theorem_uses_is_reported():
    """The check can fail: drop every theorem that uses `ofSource` and it names exactly that definition."""
    assert unexercised_without("VE.Layout.List", "VE.Layout.ofSource") == ["VE/Layout/List.lean: VE.Layout.ofSource"]


@pytest.mark.parametrize("name", ["VE.Scope.mergeParts", "VE.Scope.narrowing", "VE.Scope.ownSafe"])
def test_an_effects_definition_no_theorem_uses_is_reported(name):
    """The same for the effects (sc-1ab): each named definition is reported once its theorems are dropped."""
    assert unexercised_without("VE.Scope.Effects", name) == [f"VE/Scope/Effects.lean: {name}"]


@pytest.mark.parametrize("name", ["VE.Scope.baseObj", "VE.Scope.ordered", "VE.Scope.govern", "VE.Scope.applyEffect",
                                  "VE.Scope.addOver", "VE.Scope.edgesInto", "VE.Scope.memo"])
def test_a_govern_definition_no_theorem_uses_is_reported(name):
    """The same for `govern` (sc-1ac, sc-1ad): each named definition is reported once its theorems are dropped."""
    assert f"VE/Scope/Govern.lean: {name}" in unexercised_without("VE.Scope.Govern", name)
