"""Every trusted definition of `lean/VE/Cardinality/` is stated about by a theorem (standing ruling R16).

R16 signs qt-a1's S +137 only when every new trusted definition is exercised by a check that can fail.
Review F1 of qt-a1: nine trusted definitions (`Cmp`, `CountAtom`, `Rel`, `Body.holds`, `CEntails`,
`CountAtom.holds`, `Counts`, `Proportion.holds`, `Rel.holds`) were exercised only by `example`s or by
nothing, and fifteen planted bugs in their cases left the build passing. This reads the compiled
`-- uses` lines of `lean/statements.txt` through `tools/trust_map.py`'s own trust rule, for every file
of the directory, so a trusted definition a later item adds there (QT-A2's ratios, QT-A3's decoder)
fails here until a theorem states something about it. The cases themselves are pinned by the theorems
of `lean/VE/Cardinality/Examples.lean`; `docs/quantities/qt-a1/mutants.json` plants one bug per case."""

from pathlib import Path

from tools import trust_map

ROOT = Path(__file__).resolve().parents[1]
STATEMENTS = ROOT / "lean/statements.txt"
SYNTAX, SEMANTICS = "VE.Cardinality.Syntax", "VE.Cardinality.Semantics"


def cardinality_modules() -> list[str]:
    return sorted(trust_map.module_key(p, ROOT) for p in (ROOT / "lean/VE/Cardinality").glob("*.lean"))


def test_the_cardinality_files_are_classified():
    table = trust_map.load_table()
    modules = cardinality_modules()
    assert "VE/Cardinality/Syntax.lean" in modules and "VE/Cardinality/Semantics.lean" in modules
    assert all(module in table for module in modules)


def test_every_trusted_cardinality_definition_is_used_by_a_theorem():
    proved = trust_map.statements(STATEMENTS)
    assert proved, "lean/statements.txt is missing or empty; run tools/lean_statements.py"
    assert trust_map.unexercised(trust_map.load_table(), proved, cardinality_modules()) == []


# The qt-a1 F1 instances: each definition the review listed, with a theorem that states its cases.
F1 = {
    (SYNTAX, "VE.Cardinality.Rel"): "VE.Cardinality.Examples.everyone_two",
    (SEMANTICS, "VE.Cardinality.Rel.holds"): "VE.Cardinality.Examples.everyone_two",
    (SYNTAX, "VE.Cardinality.Cmp"): "VE.Cardinality.Examples.share_two",
    (SEMANTICS, "VE.Cardinality.Proportion.holds"): "VE.Cardinality.Examples.share_two",
    (SYNTAX, "VE.Cardinality.CountAtom"): "VE.Cardinality.Examples.counts_unique",
    (SEMANTICS, "VE.Cardinality.Counts"): "VE.Cardinality.Examples.counts_two",
    (SEMANTICS, "VE.Cardinality.CountAtom.holds"): "VE.Cardinality.Examples.everyone_two",
    (SEMANTICS, "VE.Cardinality.Body.holds"): "VE.Cardinality.Examples.body_cases",
    (SEMANTICS, "VE.Cardinality.CEntails"): "VE.Cardinality.Examples.entails_cases",
}


def test_each_f1_definition_is_stated_about_by_its_theorem():
    proved = trust_map.statements(STATEMENTS)
    for definition, theorem in F1.items():
        assert definition in (proved.get(theorem) or set()), (definition, theorem)


def test_a_definition_no_theorem_uses_is_reported():
    """The check can fail: drop every theorem that states something about `Body.holds` and it names
    exactly that definition."""
    table = trust_map.load_table()
    proved = trust_map.statements(STATEMENTS)
    body = (SEMANTICS, "VE.Cardinality.Body.holds")
    without = {theorem: found for theorem, found in proved.items() if not found or body not in found}
    assert trust_map.unexercised(table, without, cardinality_modules()) == [
        "VE/Cardinality/Semantics.lean: VE.Cardinality.Body.holds"]
