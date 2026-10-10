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
    _, declared = audit.declarations(audit.ROOT)
    actual = set(declared)
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
    monkeypatch.setattr(audit, 'check_hashes', lambda *args: None)
    monkeypatch.setattr(audit, 'generated_manifests', lambda _: {
        name: (audit.ROOT / name).read_text() for name in audit.MANIFESTS})
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
        audit.main(['--unknown'])


def test_scratch_theorem_requires_regeneration_then_checks(tmp_path, monkeypatch):
    root = tmp_path / 'lean'
    (root / 'VE').mkdir(parents=True)
    (root / 'ResponseShape').mkdir()
    source = root / 'VE/Scratch.lean'
    source.write_text('theorem VE.Scratch.fresh : True := by trivial\n')
    import hashlib
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    declarations = root / 'declarations.txt'
    for manifest in audit.MANIFESTS:
        (root / manifest).write_text('')
    def refresh_hashes():
        declarations.write_text(f'module VE.Scratch {digest}\n'
                                '1:0-1:50 theorem VE.Scratch.fresh@VE.Scratch\n'
                                f'module VE.Audit {hashlib.sha256((root / "VE/Audit.lean").read_bytes()).hexdigest()}\n'
                                f'module ResponseShape.Audit {hashlib.sha256((root / "ResponseShape/Audit.lean").read_bytes()).hexdigest()}\n')
    refresh_hashes()
    monkeypatch.setattr(audit, 'ROOT', root)
    monkeypatch.setattr(audit, 'RECORD', root / 'axioms.txt')
    def lean(command, **kwargs):
        manifest = root / command[-1]
        names = [line.removeprefix('#print axioms ') for line in manifest.read_text().splitlines()
                 if line.startswith('#print axioms ')]
        return SimpleNamespace(stdout=''.join(f"'{name}' does not depend on any axioms\n" for name in names))
    monkeypatch.setattr(subprocess, 'run', lean)
    # The initial manifest is stale; the source hash is correct.
    with pytest.raises(AssertionError, match='stale'):
        audit.main(['--check'])
    audit.main(['--write'])
    assert '#print axioms VE.Scratch.fresh\n' in (root / 'VE/Audit.lean').read_text()
    refresh_hashes()
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


def test_audit_refuses_bare_admit(tmp_path):
    (tmp_path / 'Hole.lean').write_text('def hole : True := by admit\n')
    with pytest.raises(AssertionError, match='forbidden admit tactic'):
        audit.scan_sources(tmp_path)


def test_audit_allows_the_admission_function_as_a_name_and_application(tmp_path):
    (tmp_path / 'Admission.lean').write_text(
        'def admit (n : Nat) : Nat := n\n'
        'def use (n : Nat) : Nat := admit n\n'
        'theorem keeps_name : admit 0 = 0 := by\n  unfold admit\n  rfl\n')
    assert [p.name for p in audit.scan_sources(tmp_path)] == ['Admission.lean']


def test_manifest_generation_uses_compiled_ranges_and_declaring_modules(tmp_path):
    (tmp_path / 'declarations.txt').write_text(
        'module VE.Scratch ' + '0' * 64 + '\n'
        '1:0-1:20 theorem VE.Scratch.new_result@VE.Scratch\n'
        'generated theorem VE.Scratch.unranged@VE.Scratch\n'
        'module ResponseShape.Scratch ' + '1' * 64 + '\n'
        '2:0-2:30 theorem ResponseShape.Scratch.result@ResponseShape.Scratch\n')
    _, names = audit.declarations(tmp_path)
    manifests = audit.generated_manifests(names)
    assert 'import VE.Scratch\n' in manifests['VE/Audit.lean']
    assert '#print axioms VE.Scratch.new_result\n' in manifests['VE/Audit.lean']
    assert 'unranged' not in manifests['VE/Audit.lean']
    assert 'import ResponseShape.Scratch\n' in manifests['ResponseShape/Audit.lean']
    assert '#print axioms ResponseShape.Scratch.result\n' in manifests['ResponseShape/Audit.lean']


def test_audit_rejects_stale_module_hash(tmp_path):
    source = tmp_path / 'VE/Scratch.lean'
    source.parent.mkdir()
    source.write_text('theorem fresh : True := by trivial\n')
    with pytest.raises(AssertionError, match='source hash mismatch'):
        audit.check_hashes(tmp_path, {'VE.Scratch': '0' * 64}, audit.scan_sources(tmp_path))
