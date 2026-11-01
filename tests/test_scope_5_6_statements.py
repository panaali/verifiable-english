"""The statement gate for spec 5.6 (SC-4): each proved theorem and each definition the statements read is the reviewed
text, whitespace aside (sc-4).

`precedes_edges` and `yields_edges` are false as written on a raw unit tree (F-raw-edges, `FarExamples.lean`); the
DRI's decision of 2026-11-01 (reviews/dri-decisions-20261101-sc-4-edges.md) adds `JsonWF D.doc`, proved in sc-4b, so
until then neither is stated under its name.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.test_scope_5_4_statements import statement

ROOT = Path(__file__).resolve().parents[1]
PROVED = ("no_effect_refused", "forward_exception_sound", "forward_exception_complete")
DEFINED = ("laterUnitsIn", "forwardCheck")
UNPROVED = ("precedes_edges", "yields_edges")


def spec_5_6() -> str:
    spec = (ROOT / "docs/spec/scope.md").read_text()
    start = spec.index("### 5.6 SC-4")
    return spec[start:spec.index("### 5.7", start)]


def definition(text: str, name: str) -> str | None:
    """The definition of `name`, to the next blank line or the end of a fence, whitespace normalised."""
    start = text.find(f"def {name} ")
    if start < 0:
        return None
    rest = text[start:]
    return " ".join(rest[:min(i for i in (rest.find("\n\n"), rest.find("\n```")) if i >= 0)].split())


@pytest.mark.parametrize("name", PROVED)
def test_the_proved_statements_are_spec_5_6s_text(name):
    lean = (ROOT / "lean/VE/Scope/FarTheorems.lean").read_text()
    assert statement(spec_5_6(), name) is not None, name
    assert statement(lean, name) == statement(spec_5_6(), name), name


@pytest.mark.parametrize("name", DEFINED)
def test_the_definitions_are_spec_5_6s_text(name):
    lean = (ROOT / "lean/VE/Scope/Govern.lean").read_text()
    assert definition(spec_5_6(), name) is not None, name
    assert definition(lean, name) == definition(spec_5_6(), name), name


@pytest.mark.parametrize("name", UNPROVED)
def test_a_statement_waiting_for_sc_4b_is_not_stated_under_its_name(name):
    assert statement(spec_5_6(), name) is not None, name
    for path in (ROOT / "lean/VE/Scope").glob("*.lean"):
        assert statement(path.read_text(), name) is None, (name, path.name)


def test_the_check_tells_a_changed_statement():
    """The comparison is not vacuous: a dropped premise or another refusal is a different statement."""
    lean = (ROOT / "lean/VE/Scope/FarTheorems.lean").read_text()
    for name, old, new in (("no_effect_refused", "(hgr : graph g.effect = true) ", ""),
                           ("forward_exception_sound", "r ∈ N.over", "True"),
                           ("no_effect_refused", '"ScopeNoEffect"', '"Scope"')):
        proved = statement(lean, name)
        assert old in proved
        assert proved.replace(old, new, 1) != statement(spec_5_6(), name), name
    govern = (ROOT / "lean/VE/Scope/Govern.lean").read_text()
    assert definition(govern, "laterUnitsIn").replace(".drop 1", "", 1) != definition(spec_5_6(), "laterUnitsIn")
