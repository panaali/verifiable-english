"""Regression checks for the CI-3b review: StepsProofs' comments claim no more than its theorems prove."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOFS = ROOT / "lean/VE/Commands/StepsProofs.lean"
ONE_SHAPE = "shapes s = [.preposed c x]"
# A comment that says the preposed `<x>` is one piece of the split at `, ` or cannot reach the condition-scope refusal.
CLAIM = re.compile(
    r"refusal never fires|never has the condition-scope refusal|holds no `, then `|takes `<x>` from|`<x>` is one piece"
)


def doc_comments(text: str) -> list[str]:
    """The `/-! ... -/` and `/-- ... -/` comments of a Lean file (they do not nest in StepsProofs)."""
    return re.findall(r"/-[-!](.*?)-/", text, flags=re.S)


def test_every_no_condition_scope_claim_names_the_one_shape_hypothesis() -> None:
    # F1: "`<x>` holds no `, then ` and the condition-scope refusal never fires" holds only when the `If` shape is
    # the wording's only shape; with two shapes `<x>` joins pieces and ConditionScope fires.
    claims = [c for c in doc_comments(PROOFS.read_text()) if CLAIM.search(c)]
    assert len(claims) >= 3, claims  # the module comment, shapes_preposed and hasThen_preposed
    for comment in claims:
        assert ONE_SHAPE in " ".join(comment.split()), comment


def test_the_two_shape_counterexample_is_a_checked_guard() -> None:
    # The comment's boundary is held by a `#guard` that `lake build` checks: two shapes, `<x>` holds `, then `,
    # and the step is ConditionScope.
    text = PROOFS.read_text()
    guard = text[text.index("-- `h` is needed (one shape)") :]
    assert '#guard let p := "If draft is approved, click Check rule conflict, then click Ask."' in guard
    assert '.preposed "draft is approved" "click Check rule conflict, then click Ask"' in guard
    assert 'hasThen ("click Check rule conflict, then click Ask" ++ ".") &&' in guard
    assert '.refused "ConditionScope" StepsExamples.conditionScopeText' in guard
