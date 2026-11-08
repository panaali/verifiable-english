"""SC-7: scope's authoring wordings (docs/spec/scope.md 2.2, 5.8, 7.8). Lean decides (`Pinned.parseGovernor`,
`Pinned.renderGovernor`, `Pinned.paraphrase`, `lean/VE/Scope/Authoring.lean`); each row of 2.2, F5a and the refused
variants are `#guard`s in `lean/VE/Scope/AuthoringExamples.lean`, checked by every `lake build`. No Python reads a
wording: the IDE wiring through the relay is sc-7b. These tests tie the Lean text to the spec's."""
from __future__ import annotations

import re
from pathlib import Path

from tests.test_scope_5_4_statements import statement

ROOT = Path(__file__).resolve().parents[1]
AUTHORING = ROOT / "lean/VE/Scope/Authoring.lean"
EXAMPLES = ROOT / "lean/VE/Scope/AuthoringExamples.lean"
SPEC = ROOT / "docs/spec/scope.md"


def spec_5_8() -> str:
    spec = SPEC.read_text()
    start = spec.index("### 5.8 SC-6")
    return spec[start:spec.index("### 6.", start)]


def test_the_round_trip_statements_are_spec_5_8s_text():
    for name in ("scope_parseRender", "scope_renderParse"):
        want = statement(spec_5_8(), name)
        assert want is not None, name
        assert statement(AUTHORING.read_text(), name) == want, name


def test_the_statement_gate_sees_a_changed_conclusion():
    changed = AUTHORING.read_text().replace("Pinned.renderGovernor b = w", "Pinned.renderGovernor b = w ++ \"\"", 1)
    assert statement(changed, "scope_parseRender") != statement(spec_5_8(), "scope_parseRender")


def test_f5a_guards_u0170_s01s_wording_as_the_spec_quotes_it():
    """F5a (7.8): the wording the Lean fixture parses to no governor is 2.1's quotation of u0170.s01, byte for byte."""
    quoted = re.search(r'\(u0170\.s01, "([^"]+)"\)', " ".join(SPEC.read_text().split()))
    assert quoted is not None
    examples = EXAMPLES.read_text()
    assert f'def u0170s01 := "{quoted.group(1)}"' in examples
    assert "#guard parseGovernor u0170s01 == none" in examples


def test_each_row_of_2_2_has_a_round_trip_and_a_paraphrase_guard():
    examples = EXAMPLES.read_text()
    for row in ("wFrame", "wNamed", "wNarrow", "wInPlace", "wCarve", "wPrecedes", "wWhen", "wTitle", "wFrontier"):
        assert f"#guard trip {row} " in examples, row
        assert f"#guard para {row} " in examples, row
