"""Source checks of `plain_wellFormed` (docs/spec/right-clauses.md 8.3; cmp-s3a-cfr-1).

The statement in Lean must be the approved text of 8.3 exactly, up to whitespace, and the theorem and its
corollaries must be in the audit record with standard axioms only (no `sorryAx`).
"""
from __future__ import annotations

from pathlib import Path
import re

from tools.lean_statements import inventory_path  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'docs/spec/right-clauses.md'
LEAN = ROOT / 'lean/VE/RightClauses/PlainWellFormed.lean'
PROOF_DIR = ROOT / 'lean/VE/RightClauses/PlainWellFormed'
AXIOMS = inventory_path('lean/axioms.txt')
STANDARD = {'propext', 'Classical.choice', 'Quot.sound'}
COROLLARIES = ('plain_wellFormedRights', 'clauseSlot_labelled_of_doc', 'clause_fails_not_selected_of_doc',
               'relation_some_bearer_of_doc')


def _flat(text: str) -> str:
    return ' '.join(text.split())


def spec_statement() -> str:
    """The statement of `plain_wellFormed` in 8.3, after its name."""
    text = SPEC.read_text()
    section = text[text.index('### 8.3 `Plain.lean`'):text.index('### 8.4')]
    match = re.search(r'^theorem plain_wellFormed (.*?)\nend VE\.RightClauses', section, flags=re.M | re.S)
    assert match, 'no plain_wellFormed in 8.3'
    return _flat(match[1])


def lean_statement(path: Path = LEAN) -> str | None:
    """The statement of `plain_wellFormed` in Lean, after its name and up to `:=`."""
    if not path.exists():
        return None
    match = re.search(r'^theorem plain_wellFormed (.*?)\s:=\s*by\b', path.read_text(), flags=re.M | re.S)
    return _flat(match[1]) if match else None


def audited_axioms(name: str) -> list[str] | None:
    match = re.search(rf"^'VE\.RightClauses\.{re.escape(name)}' (.*)$", AXIOMS.read_text(), flags=re.M)
    return re.findall(r'[\w.]+', match[1].partition('[')[2]) if match else None


def test_right_clauses_required_plain_wellformed_theorem():
    assert lean_statement() == spec_statement()
    for name in ('plain_wellFormed',) + COROLLARIES:
        axioms = audited_axioms(name)
        assert axioms is not None, f'{name} is not in the audit record'
        assert set(axioms) <= STANDARD, (name, axioms)
    for path in [LEAN, *sorted(PROOF_DIR.glob('*.lean'))]:
        assert not re.search(r'\bsorry\b|\badmit\b', path.read_text()), path


def test_statement_check_catches_a_restatement(tmp_path):
    """The comparison is not vacuous: a weakened or renamed statement differs from the approved text."""
    text = LEAN.read_text()
    weakened = tmp_path / 'weakened.lean'
    weakened.write_text(text.replace('(h0 : WellFormedRights D.doc = true) :',
                                     '(h0 : WellFormedRights D.doc = true) (hx : True) :', 1))
    assert lean_statement(weakened) != spec_statement()
    renamed = tmp_path / 'renamed.lean'
    renamed.write_text(text.replace('theorem plain_wellFormed ', 'theorem plain_wellFormed2 ', 1))
    assert lean_statement(renamed) is None
