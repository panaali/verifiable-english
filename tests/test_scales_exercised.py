"""Every trusted definition of `lean/VE/Scales/` is stated about by a theorem (standing ruling R16).

R16 signs qt-b1's S +78 only when every new trusted definition is exercised by a check that can fail.
This reads the compiled `-- uses` lines of `lean/statements.txt` through `tools/trust_map.py`'s own
trust rule, for every file of the directory, so a trusted definition added there (qt-b1b's `Fresh` and
`StrictLinear`) fails here until a theorem states something about it. The cases themselves
are pinned by the theorems and #guards of `lean/VE/Scales/Examples.lean`;
`docs/quantities/qt-b1/mutants.json` and `docs/quantities/qt-b1b/mutants.json` plant a bug in each
trusted definition."""

from pathlib import Path

from tools import trust_map

ROOT = Path(__file__).resolve().parents[1]
STATEMENTS = ROOT / "lean/statements.txt"


def scales_modules() -> list[str]:
    return sorted(trust_map.module_key(p, ROOT) for p in (ROOT / "lean/VE/Scales").glob("*.lean"))


def test_the_scales_files_are_classified():
    table = trust_map.load_table()
    modules = scales_modules()
    assert {"VE/Scales/Syntax.lean", "VE/Scales/Premises.lean", "VE/Scales/Intended.lean",
            "VE/Scales/Degrees.lean"} <= set(modules)
    assert all(module in table for module in modules)


def test_every_trusted_scales_definition_is_used_by_a_theorem():
    proved = trust_map.statements(STATEMENTS)
    assert proved, "lean/statements.txt is missing or empty; run tools/lean_statements.py"
    assert trust_map.unexercised(trust_map.load_table(), proved, scales_modules()) == []


def test_a_definition_no_theorem_uses_is_reported():
    """The check can fail: drop every theorem that states something about `Intended` and it names
    exactly that definition and `Direction`, which only `intended_iff_and` states something about."""
    proved = trust_map.statements(STATEMENTS)
    intended = ("VE.Scales.Intended", "VE.Scales.Intended")
    without = {theorem: found for theorem, found in proved.items() if not found or intended not in found}
    assert trust_map.unexercised(trust_map.load_table(), without, scales_modules()) == [
        "VE/Scales/Intended.lean: VE.Scales.Intended", "VE/Scales/Syntax.lean: VE.Scales.Direction"]


def test_fresh_is_stated_about_by_scales_conservative():
    """`Fresh` is exercised by the theorem that needs it: drop `scales_conservative` and every theorem
    that states something about `Fresh` with it, and `Fresh` alone is named."""
    proved = trust_map.statements(STATEMENTS)
    fresh = ("VE.Scales.Intended", "VE.Scales.Fresh")
    assert fresh in proved["VE.Scales.scales_conservative"]
    without = {theorem: found for theorem, found in proved.items() if not found or fresh not in found}
    assert trust_map.unexercised(trust_map.load_table(), without, scales_modules()) == [
        "VE/Scales/Intended.lean: VE.Scales.Fresh"]
