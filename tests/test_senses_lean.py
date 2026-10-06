"""Source checks of the senses layer in Lean (docs/spec/senses.md 5.2 and 5.3).

The statements of spec 5.3 are the approved text. A statement the build proves is a Lean theorem that states exactly
that text, up to whitespace, and is in the audit record with standard axioms only. A statement the build does not prove
(DEFERRED, each with its reason in docs/spec/senses-lean-report.md) is a `def ... : Prop` with exactly that text, so a
later proof states it unchanged. The lists the senses layer shares with Python (the reserved words of D13, the schema
names of W4, the limits of W3, W4 and 2.5) are read from the compiled Lean definitions, never from the source text, and
compared with Python's.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'docs/spec/senses.md'
LEAN = ROOT / 'lean/VE/Senses'
AXIOMS = ROOT / 'lean/axioms.txt'
STANDARD = {'propext', 'Classical.choice', 'Quot.sound'}
DEFERRED = {'glossed_negative', 'lines_read', 'project_total', 'senseMap_ids'}


def _flat(text: str) -> str:
    return ' '.join(text.split())


def spec_statements() -> dict[str, str]:
    """The theorems of spec 5.3, name to statement."""
    text = SPEC.read_text()
    section = text[text.index('### 5.3 The exact statements'):text.index('### 5.4')]
    start = section.index('```lean') + len('```lean')
    block = section[start:section.index('```', start)]
    out = {}
    for part in re.split(r'^theorem ', block, flags=re.M)[1:]:
        name, _, statement = part.partition(' : ')
        out[name.strip()] = _flat(statement)
    return out


def lean_statement(name: str, root: Path = LEAN) -> tuple[str, str] | None:
    """How the senses modules state `name`: ('theorem', text) up to `:=`, or ('def', text) of a `Prop` definition."""
    for path in sorted(root.glob('*.lean')):
        text = path.read_text()
        match = re.search(rf'^theorem {re.escape(name)} : (.*?)\s:=\s*(?:by\b|fun\b|rfl\b|\n)', text,
                          flags=re.M | re.S)
        if match:
            return 'theorem', _flat(match[1])
        match = re.search(rf'^def {re.escape(name)} : Prop :=\s(.*?)(?=\n\n|\nend |\Z)', text, flags=re.M | re.S)
        if match:
            return 'def', _flat(match[1])
    return None


SPEC_NAMES = sorted(spec_statements())


def test_spec_lists_the_thirteen_statements():
    assert set(SPEC_NAMES) == {
        'wf_iff_no_failure', 'glossed_negative', 'preamble_unique', 'lines_read', 'project_valid', 'project_total',
        'project_extends', 'senses_resolved_one_reading', 'senses_unit_sound', 'senses_candidate_sound',
        'candidates_complete', 'mixed_exact', 'senseMap_ids'}
    assert DEFERRED < set(SPEC_NAMES)


@pytest.mark.parametrize('name', SPEC_NAMES)
def test_statement_equals_the_approved_text(name):
    kind = 'def' if name in DEFERRED else 'theorem'
    assert lean_statement(name) == (kind, spec_statements()[name])


@pytest.mark.parametrize('name', sorted(set(SPEC_NAMES) - DEFERRED))
def test_proved_statement_is_audited_with_standard_axioms(name):
    record = AXIOMS.read_text()
    match = re.search(rf"^'VE\.Senses\.{re.escape(name)}' (.*)$", record, flags=re.M)
    assert match, name
    axioms = re.findall(r'[\w.]+', match[1].partition('[')[2])
    assert set(axioms) <= STANDARD, (name, axioms)


@pytest.mark.parametrize('name', sorted(DEFERRED))
def test_deferred_statement_is_no_theorem(name):
    """A deferred statement is not in the audit record under its name: nothing claims it is proved."""
    assert not re.search(rf"^'VE\.Senses\.{re.escape(name)}' ", AXIOMS.read_text(), flags=re.M)


@pytest.mark.parametrize('name, old, new', [
    ('mixed_exact', '2 ≤ ids.length := by', '1 ≤ ids.length := by'),
    ('project_total', 'E.forms.aliases = [] →', ''),
])
def test_statement_diff_catches_a_change(tmp_path, name, old, new):
    """The comparison is not vacuous: a weakened statement, proved or deferred, differs from the approved text."""
    for path in LEAN.glob('*.lean'):
        (tmp_path / path.name).write_text(path.read_text())
    for path in tmp_path.glob('*.lean'):
        text = path.read_text()
        if old in text:
            path.write_text(text.replace(old, new, 1))
    assert lean_statement(name, tmp_path) != lean_statement(name)
    assert lean_statement(name) == ('def' if name in DEFERRED else 'theorem', spec_statements()[name])


PROBE = '''import VE.Senses.Read
open Lean
#eval IO.println (toJson VE.Senses.reservedWords).compress
#eval IO.println (toJson VE.Senses.schemaReserved).compress
#eval IO.println (toJson [VE.Senses.maxSorts, VE.Senses.maxPredicates, VE.Senses.maxNameChars,
  VE.Senses.maxFormChars, VE.Senses.candidateCap]).compress
'''


@pytest.fixture(scope='module')
def lean_values(tmp_path_factory):
    """The shared lists and limits as the compiled Lean definitions give them."""
    lake = shutil.which('lake')
    if lake is None:
        pytest.skip('lake is required to read the compiled senses definitions')
    probe = tmp_path_factory.mktemp('senses') / 'Probe.lean'
    probe.write_text(PROBE)
    built = subprocess.run([lake, 'build', 'VE.Senses.Read'], cwd=ROOT / 'lean', capture_output=True, text=True,
                           timeout=HANG_TIMEOUT)
    assert built.returncode == 0, built.stdout + built.stderr
    run = subprocess.run([lake, 'env', 'lean', str(probe)], cwd=ROOT / 'lean', capture_output=True, text=True,
                         timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout + run.stderr
    lines = run.stdout.splitlines()
    assert len(lines) == 3, run.stdout
    return [json.loads(line) for line in lines]


def test_reserved_words_are_python_reserved_and_the_three_of_d13(lean_values):
    from ve.english import _RESERVED
    words = lean_values[0]
    assert len(words) == len(set(words))
    assert set(words) == set(_RESERVED) | {'means', 'meaning', 'document'}


def test_schema_names_are_python_reserved(lean_values):
    from ve.environment import RESERVED
    names = lean_values[1]
    assert len(names) == len(set(names)) and set(names) == set(RESERVED)


def test_limits_are_python_limits(lean_values):
    from ve.environment import _verbalisation
    from ve.errors import ResourceLimit
    from ve.limits import MAX_IDENTIFIER_BYTES, MAX_PREDICATES, MAX_SORTS
    max_sorts, max_predicates, max_name, max_form, cap = lean_values[2]
    assert (max_sorts, max_predicates, max_name) == (MAX_SORTS, MAX_PREDICATES, MAX_IDENTIFIER_BYTES)
    _verbalisation('a' * max_form)
    with pytest.raises(ResourceLimit):
        _verbalisation('a' * (max_form + 1))
    from ve.backends.senses import CANDIDATE_CAP
    assert cap == CANDIDATE_CAP == 8  # spec 2.6, candidateCap; the response check's bound
