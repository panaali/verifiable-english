"""The statement gate for spec 5.4 (SC-2): each proved theorem is the reviewed text, whitespace aside (sc-2c, sc-2d).

The five effect statements take `(hw : JsonWF o)` after `hN` (before `h₁` in `commute_applies`), as the DRI signed
(reviews/dri-decisions-20261031-sc-2c.md item 1); their binders are pinned here as well, so a statement without `hw`, or
with any other premise, fails even if the spec text were changed with it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools.check_readings_defaults_statements import proof_cut

ROOT = Path(__file__).resolve().parents[1]
EFFECTS = {
    "reguard_applies": "D u c o o' N N' G' h hN hw hN' hG S ρ",
    "restrict_applies": "D u C o o' C' N N' hC hC' h hN hw hN' S ρ",
    "carveOut_applies": "D u c o o' N N' C h hN hw hN' hC S ρ",
    "applyEffect_typed": "D u e o o' N N' E Γ hN hw h hN' hT hc",
    "commute_applies": "D u e₁ e₂ hc o o₁ o₂ N₁ N₂ hw h₁ h₂ hN₁ hN₂ S ρ",
}
PROVED = ("own_congr", "order_refused", "listName_run", *EFFECTS)


def statement(text: str, name: str) -> str | None:
    """The statement of `name`: from `theorem name ` to the `:=` that starts the proof (`proof_cut`: a `:=` inside the
    statement, `{ L with scope := s }`, is kept) or the next blank line, whitespace normalised."""
    start = text.find(f"theorem {name} ")
    if start < 0:
        return None
    rest = text[start:]
    rest = rest[:rest.find("\n\n")] if "\n\n" in rest else rest
    return " ".join(rest[:proof_cut(rest)].split())


def binders(stmt: str) -> str:
    """The names each explicit binder `(x y : T)` of a statement introduces, in order."""
    return " ".join(m.group(1) for m in re.finditer(r"\(([\w']+(?: [\w']+)*) :", stmt))


def spec_5_4() -> str:
    spec = (ROOT / "docs/spec/scope.md").read_text()
    start = spec.index("### 5.4 SC-2")
    return spec[start:spec.index("### 5.5", start)]


def lean() -> str:
    return (ROOT / "lean/VE/Scope/Theorems.lean").read_text()


@pytest.mark.parametrize("name", PROVED)
def test_the_proved_statements_are_spec_5_4s_text(name):
    assert statement(spec_5_4(), name) is not None, name
    assert statement(lean(), name) == statement(spec_5_4(), name), name


@pytest.mark.parametrize("name", EFFECTS)
def test_an_effect_statement_takes_exactly_the_signed_premises(name):
    for text in (lean(), spec_5_4()):
        stmt = statement(text, name)
        assert stmt.count("(hw : JsonWF o)") == 1, name
        assert binders(stmt) == EFFECTS[name], name


@pytest.mark.parametrize("name", [n for n in PROVED if " with " in (statement(lean(), n) or "")])
def test_the_statement_runs_past_a_record_update(name):
    """Review sc-6 F1: a `:=` inside `{ N with f := v }` is part of the statement, so the text after it is compared,
    and a change there is a different statement."""
    text, proved = lean(), statement(lean(), name)
    assert ":=" in proved and proved.rsplit(":=", 1)[1].strip(), name
    inner = text.index(":=", text.index(f"theorem {name} "))
    changed = text[:inner] + ":= changed" + text[inner + 2:]
    assert statement(changed, name) != statement(spec_5_4(), name), name


def test_the_check_tells_a_changed_statement():
    """The comparison is not vacuous: a dropped or added premise, or a weakened conclusion, is a different statement."""
    for name, old, new in (("own_congr", "(hs : ownSafe depthLimit c = true) ", ""),
                           ("order_refused", '"ScopeOrder"', '"Scope"'),
                           *((n, "(hw : JsonWF o) ", "") for n in EFFECTS),
                           *((n, "(hw : JsonWF o) ", "(hw : JsonWF o) (hx : True) ") for n in EFFECTS)):
        proved = statement(lean(), name)
        assert old in proved, name
        changed = proved.replace(old, new, 1)
        assert changed != statement(spec_5_4(), name), name
        if name in EFFECTS:
            assert binders(changed) != EFFECTS[name], name
