"""The ties pass of jt-crossplan-fixes: the statement it proposes for `PolicyCtx.of` is the one Lean checks."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DELTA = ROOT / "docs/jt-crossplan-fixes/DELTA.md"
EXAMPLES = ROOT / "lean/VE/EnglishGrammar/E2Examples.lean"


def _row(name):
    rows = [line for line in DELTA.read_text().splitlines() if line.startswith(f"| `{name}` |")]
    assert len(rows) == 1, name
    return rows[0]


def test_policy_ctx_tie_does_not_claim_the_false_converse():
    """Review F1 of ties-jt-crossplan: a wording that passes both lints need not claim its head (`allow` in
    `Fpermits`), so the proposed tie states conjuncts, not an "iff"."""
    text = DELTA.read_text()
    assert "holds iff" not in text
    for name in ["VE.EnglishGrammar.PolicyCtx.of", "VE.EnglishGrammar.PolicyCtx"]:
        assert not re.search(r"\biff\b(?!\")", _row(name)), name


def test_policy_ctx_tie_is_the_statement_the_lean_guards_check():
    """The proposed statement names the `#guard`s that check it, and those guards check (a)-(c), the counterexample
    and that a context keeping too many heads or none fails them."""
    row = _row("VE.EnglishGrammar.PolicyCtx.of")
    assert "fixedPointTie" in row and "Fpermits" in row
    lean = EXAMPLES.read_text()
    assert "def fixedPointTieOf (of : Env → Overlay → PolicyCtx)" in lean
    assert "def fixedPointTie (E : Env) (O : Overlay := {}) : Bool := fixedPointTieOf PolicyCtx.of E O" in lean
    guards = [g for g in re.split(r"\n(?=#guard )", lean) if g.startswith("#guard ")]
    assert "#guard policyEnvs.all fun (E, O) => fixedPointTie E O\n" in lean
    assert re.search(r"\(Fpermits, noOverlay\)", lean.split("def policyEnvs", 1)[1].split("\n\n", 1)[0])
    assert any('lintCodesIn c "allow"' in g and '!c.lintHeads.any (·.2 == "allow")' in g for g in guards)
    assert any("!fixedPointTieOf oneRoundOf Fpermits" in g and "!fixedPointTieOf (fun E O => PolicyCtx.ofHeads E O [])"
               in g for g in guards)
