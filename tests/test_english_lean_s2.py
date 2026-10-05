"""Source checks of the English instance in Lean (docs/spec/english-lean-s2.md 5.6 and 5.7).

The statements of spec 5.6 are the approved text: each Lean theorem must state exactly that text, up to
whitespace, and be in the audit record with standard axioms only. Two properties of the action library are
checked on the source, as spec 5.7 prescribes: no action constructs `Reject.internal`, and the fixed
actions read neither the environment nor the lexicon.
"""
from __future__ import annotations

from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'docs/spec/english-lean-s2.md'
LEAN = ROOT / 'lean/VE/EnglishGrammar'
AXIOMS = ROOT / 'lean/axioms.txt'
STANDARD = {'propext', 'Classical.choice', 'Quot.sound'}


def _flat(text: str) -> str:
    return ' '.join(text.split())


def spec_statements() -> dict[str, str]:
    """The theorems of spec 5.6, name to statement."""
    text = SPEC.read_text()
    section = text[text.index('### 5.6 The exact statements'):text.index('### 5.7')]
    block = section[section.index('```lean') + len('```lean'):section.index('```', section.index('```lean') + 7)]
    parts = re.split(r'^theorem ', block, flags=re.M)[1:]
    out = {}
    for part in parts:
        name, _, statement = part.partition(' : ')
        out[name.strip()] = _flat(statement)
    return out


def lean_statement(name: str) -> str | None:
    """The statement of a Lean theorem of the English instance, up to `:=`."""
    for path in sorted(LEAN.rglob('*.lean')):
        text = path.read_text()
        match = re.search(rf'^theorem {re.escape(name)} : (.*?)\s:=\s*(?:by\b|fun\b|rfl\b|\n)', text,
                          flags=re.M | re.S)
        if match:
            return _flat(match[1])
    return None


SPEC_NAMES = sorted(spec_statements())


def test_spec_lists_the_statements_of_5_5():
    assert set(SPEC_NAMES) == {
        'read_ok', 'read_complete_english', 'read_stopped', 'english_reading_unique', 'start_sentence',
        'meaning_total', 'checked_rendering', 'checked_rendering_exact', 'translate_exact',
        'translate_one_sentence', 'grammar_rules', 'lexRules_terminatorFree', 'valid_iff_no_failure',
        'grammar_extension'}


@pytest.mark.parametrize('name', SPEC_NAMES)
def test_statement_equals_the_approved_text(name):
    assert lean_statement(name) == spec_statements()[name]


@pytest.mark.parametrize('name', SPEC_NAMES)
def test_statement_is_audited_with_standard_axioms(name):
    record = AXIOMS.read_text()
    match = re.search(rf"^'VE\.EnglishGrammar\.{re.escape(name)}' (.*)$", record, flags=re.M)
    assert match, name
    axioms = re.findall(r'[\w.]+', match[1].partition('[')[2])
    assert set(axioms) <= STANDARD, (name, axioms)


def test_statement_diff_catches_a_change(tmp_path, monkeypatch):
    """The comparison is not vacuous: a weakened statement differs from the approved text."""
    copy = tmp_path / 'VE/EnglishGrammar'
    copy.mkdir(parents=True)
    for path in LEAN.glob('*.lean'):
        (copy / path.name).write_text(path.read_text())
    read = copy / 'Read.lean'
    read.write_text(read.read_text().replace('rs2 = rs :=', 'True :=', 1))
    monkeypatch.setattr(__import__(__name__), 'LEAN', copy)
    assert lean_statement('english_reading_unique') != spec_statements()['english_reading_unique']


def _definition(path: Path, head: str) -> str:
    """The text of the top-level definition that starts with `head`, up to the next top-level item."""
    text = path.read_text()
    start = text.index(head)
    following = re.search(r'^(?:def |theorem |/--|/-!|end )', text[start + len(head):], flags=re.M)
    return text[start:start + len(head) + following.start()] if following else text[start:]


def test_no_action_constructs_internal():
    source = (LEAN / 'Actions.lean').read_text()
    assert not re.search(r'\binternal\b', re.sub(r'--.*', '', source)), 'an action names Reject.internal'
    # `meaning` alone has the fallback (spec 5.3)
    assert '.error .internal' in (LEAN / 'Read.lean').read_text()


@pytest.mark.parametrize('head', ['def FixedAct.action ', 'def fixedActs ', 'def runCoordSubjects ',
                                  'def runCoordAdjectives ', 'def runReachBody '])
def test_fixed_actions_read_neither_environment_nor_lexicon(head):
    body = _definition(LEAN / 'Actions.lean', head)
    assert not re.search(r'\b(?:Env|Lexicon|E|L|lexRows|lexActs|acts)\b', body), head


def test_the_four_codes_have_their_public_names():
    source = (LEAN / '../EnglishGrammar/Syntax.lean').read_text()
    for code in ('CoordinationRepeated', 'CoordinationForm', 'NaturalScoped', 'RelativeForm'):
        lean = code[0].lower() + code[1:]
        assert f'| .{lean} => "{code}"' in source


def test_fixed_table_has_88_rows_with_distinct_tags():
    rows = re.findall(r'\{ tag := "([^"]+)"', (LEAN / 'Fixed/RelationalFol.lean').read_text())
    assert len(rows) == 88 and len(set(rows)) == 88


@pytest.mark.parametrize('wording, arity, ok', [
    ('{0} is deployed', 1, True),
    ('{0} is v1.2 compliant', 1, False),       # l4: two sentences
    ('{0} is {x} compliant', 1, False),        # a brace the lexer refuses
    ('{0} has the recorded relation "owns" to {1}', 2, True),
])
def test_reference_v3_requires_one_sentence(wording, arity, ok):
    """The Python reference of `Lexicon.valid` keeps the V3 condition of `shapeOk` (spec 2.6, Q6)."""
    from conformance.english_lean_lexicon import _shape_ok
    assert _shape_ok(wording, arity) is ok
