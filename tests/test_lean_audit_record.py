"""The committed axiom audit record `lean/axioms.txt` names every theorem, and the audit refuses a stale one.

Review regression (english-lean, 2026-10-04): 134 new theorems were audited locally but the record was
not regenerated, and no test read it against the theorem inventory.
"""
import importlib.util
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('ve_lean_audit_record', ROOT / 'lean/audit.py')
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)


def test_record_names_every_theorem_once():
    actual, _ = audit.scan_sources(audit.ROOT)
    names = audit.recorded_names(audit.RECORD.read_text())
    assert len(names) == len(set(names))
    assert set(names) == actual, {'unrecorded': sorted(actual - set(names))[:10],
                                  'obsolete': sorted(set(names) - actual)[:10]}


@pytest.fixture
def fake_lean(monkeypatch, tmp_path):
    """The audit with the committed record as Lean's output and a temporary record file."""
    output = audit.RECORD.read_text()
    # The whole record is the first manifest's output; the others print nothing.
    monkeypatch.setattr(subprocess, 'run', lambda command, **k: SimpleNamespace(
        stdout=output if command[-1] == audit.MANIFESTS[0] else '', returncode=0))
    record = tmp_path / 'axioms.txt'
    monkeypatch.setattr(audit, 'RECORD', record)
    return output, record


def test_audit_refuses_a_stale_record_and_write_regenerates_it(fake_lean, capsys):
    output, record = fake_lean
    record.write_text(''.join(output.splitlines(keepends=True)[:-1]))
    with pytest.raises(AssertionError, match='stale'):
        audit.main([])
    audit.main(['--write'])
    assert record.read_text() == output
    audit.main([])
    capsys.readouterr()


def test_audit_refuses_unknown_arguments(fake_lean):
    with pytest.raises(SystemExit):
        audit.main(['--check'])


@pytest.mark.parametrize('body', [
    'by admit', 'by\n  · admit', 'by\n  case zero => admit',
    'by\n  exact True.intro <;> admit', 'decreasing_by admit',
    'by\n  admit; trivial',
])
def test_audit_refuses_admit_tactic_in_executable_definitions(tmp_path, body):
    source = tmp_path / 'Hole.lean'
    source.write_text(f'def hole : True := {body}\n')
    with pytest.raises(AssertionError, match='forbidden admit tactic'):
        audit.scan_sources(tmp_path)


def test_audit_allows_the_admission_function_as_a_name_and_application(tmp_path):
    (tmp_path / 'Admission.lean').write_text(
        'def admit (n : Nat) : Nat := n\n'
        'def use (n : Nat) : Nat := admit n\n'
        'theorem keeps_name : admit 0 = 0 := by\n  unfold admit\n  rfl\n')
    actual, _ = audit.scan_sources(tmp_path)
    assert actual == {'keeps_name'}
