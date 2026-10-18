"""Every trusted definition of the judgment-terms files is stated about by a theorem (standing ruling R16).

R16 signs a small trusted-line growth only when every new trusted definition is exercised by a check
that can fail. Review F1 of jt-1: `VE.Judgments.names` (S) was counted in the +54 and named as
exercised, but no `#guard`, theorem or test used it. This reads the compiled `-- uses` lines of
`lean/statements.txt` and the classes of `tools/trust-classes.json` through `tools/trust_map.py`'s own
trust rule, so a trusted definition of `lean/VE/Judgments/` that no theorem states anything about
fails here, whichever item adds it."""

from pathlib import Path

from tools import trust_map

ROOT = Path(__file__).resolve().parents[1]
STATEMENTS = ROOT / "lean/statements.txt"


def judgment_modules() -> list[str]:
    return sorted(trust_map.module_key(p, ROOT) for p in (ROOT / "lean/VE/Judgments").glob("*.lean"))


def test_the_judgment_files_are_classified():
    table = trust_map.load_table()
    modules = judgment_modules()
    assert "VE/Judgments/Decl.lean" in modules and "VE/Judgments/Scan.lean" in modules
    assert all(module in table for module in modules)


def test_every_trusted_judgment_definition_is_used_by_a_theorem():
    proved = trust_map.statements(STATEMENTS)
    assert proved, "lean/statements.txt is missing or empty; run tools/lean_statements.py"
    assert trust_map.unexercised(trust_map.load_table(), proved, judgment_modules()) == []


def test_names_is_exercised_by_its_own_theorem():
    # the jt-1 F1 instance: `names` is stated about by `names_omega`, on J-ω's two admitted records
    uses = trust_map.statements(STATEMENTS)["VE.Judgments.Examples.names_omega"]
    assert ("VE.Judgments.Decl", "VE.Judgments.names") in uses


def test_a_definition_no_theorem_uses_is_reported():
    """The check can fail: drop every theorem that uses `names` and it names exactly that definition;
    a tied [V] definition, or a P or T one, is not trusted and is never reported."""
    table = trust_map.load_table()
    proved = trust_map.statements(STATEMENTS)
    names = ("VE.Judgments.Decl", "VE.Judgments.names")
    without = {theorem: found for theorem, found in proved.items() if not found or names not in found}
    assert trust_map.unexercised(table, without, judgment_modules()) == ["VE/Judgments/Decl.lean: VE.Judgments.names"]
    toy = {"VE/Toy.lean": {"a": "S", "b": {"class": "D[V]", "tied": ["t"]}, "c": "P", "d": "T", "e": "G[V]",
                           "f": "D[R]", "g": "K"}}
    assert trust_map.unexercised(toy, {}, ["VE/Toy.lean"]) == ["VE/Toy.lean: a", "VE/Toy.lean: e", "VE/Toy.lean: g"]
    assert trust_map.unexercised(toy, {"t": {("VE.Toy", "a"), ("VE.Toy", "e"), ("VE.Toy", "g")}}, ["VE/Toy.lean"]) == []
