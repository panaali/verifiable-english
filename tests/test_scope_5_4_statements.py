"""The statement gate for spec 5.4 (SC-2): each proved theorem is the reviewed text, whitespace aside (sc-2c).

The five effect statements are not proved: on a raw rule tree they are false (docs/scope/sc-2c/REPORT.md), so they are
absent from the Lean source until a decided statement is proved; none may appear under its name with other text.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROVED = ("own_congr", "order_refused", "listName_run")
UNPROVED = ("reguard_applies", "restrict_applies", "carveOut_applies", "applyEffect_typed", "commute_applies")


def statement(text: str, name: str) -> str | None:
    """The statement of `name`: from `theorem name ` to `:=` or the next blank line, whitespace normalised."""
    start = text.find(f"theorem {name} ")
    if start < 0:
        return None
    rest = text[start:]
    return " ".join(rest[:min(i for i in (rest.find(":="), rest.find("\n\n")) if i >= 0)].split())


def spec_5_4() -> str:
    spec = (ROOT / "docs/spec/scope.md").read_text()
    start = spec.index("### 5.4 SC-2")
    return spec[start:spec.index("### 5.5", start)]


@pytest.mark.parametrize("name", PROVED)
def test_the_proved_statements_are_spec_5_4s_text(name):
    lean = (ROOT / "lean/VE/Scope/Theorems.lean").read_text()
    assert statement(spec_5_4(), name) is not None, name
    assert statement(lean, name) == statement(spec_5_4(), name), name


@pytest.mark.parametrize("name", UNPROVED)
def test_an_unproved_statement_is_not_stated_under_its_name(name):
    lean = (ROOT / "lean/VE/Scope/Theorems.lean").read_text()
    assert statement(spec_5_4(), name) is not None, name
    assert statement(lean, name) is None, name


def test_the_check_tells_a_changed_statement():
    """The comparison is not vacuous: a dropped premise or a weakened conclusion is a different statement."""
    lean = (ROOT / "lean/VE/Scope/Theorems.lean").read_text()
    for name, old, new in (("own_congr", "(hs : ownSafe depthLimit c = true) ", ""),
                           ("order_refused", '"ScopeOrder"', '"Scope"')):
        proved = statement(lean, name)
        assert old in proved
        assert proved.replace(old, new, 1) != statement(spec_5_4(), name), name
