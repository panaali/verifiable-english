"""The committed axiom audit record `lean/axioms.txt` names every theorem, and the audit refuses a stale one.

Review regression (english-lean, 2026-10-04): 134 new theorems were audited locally but the record was
not regenerated, and no test read it against the theorem inventory.

The audit manifests are generated from `lean/declarations.txt` (architecture plan AR-1): a scratch tree
compiled by Lean shows that a new theorem needs `--write`, that a `sorry` proof fails the audit, and that a
declaration list older than the sources fails it.
"""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('ve_lean_audit_record', ROOT / 'lean/audit.py')
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)
sys.path.insert(0, str(ROOT / 'tools'))
import lean_statements  # noqa: E402


def test_record_names_every_theorem_once():
    theorems = audit.declared_theorems(audit.ROOT, audit.scan_sources(audit.ROOT))
    actual = {name for names in theorems.values() for name in names}
    names = audit.recorded_names(audit.RECORD.read_text())
    assert len(names) == len(set(names))
    assert set(names) == actual, {'unrecorded': sorted(actual - set(names))[:10],
                                  'obsolete': sorted(set(names) - actual)[:10]}


def test_committed_manifests_are_the_generated_ones():
    """Both manifests are exactly what `--write` generates from the committed declaration list, whose every
    theorem is in one of them: a Prop-class instance that Lean compiles as a theorem included."""
    theorems = audit.declared_theorems(audit.ROOT, audit.scan_sources(audit.ROOT))
    for manifest in audit.MANIFESTS:
        assert (audit.ROOT / manifest).read_text() == audit.manifest_text(manifest, theorems[manifest]), manifest
    declared, _ = lean_statements.declaration_list()
    compiled = {d.name for constants in declared.values() for d in constants if d.kind == 'theorem' and d.start}
    assert compiled == {name for names in theorems.values() for name in names}
    assert set(theorems[audit.MANIFESTS[1]].values()) == {m for m in declared if m.startswith('ResponseShape.')
                                                          and any(d.kind == 'theorem' and d.start
                                                                  for d in declared[m])}


@pytest.fixture
def fake_lean(monkeypatch, tmp_path):
    """The audit with the committed record as Lean's output and a temporary record file."""
    output = audit.RECORD.read_text()
    # The whole record is the first manifest's output; the others (and the build) print nothing.
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


def test_audit_check_is_the_default(fake_lean, capsys):
    output, record = fake_lean
    record.write_text(output)
    audit.main(['--check'])
    assert 'PASS:' in capsys.readouterr().out


@pytest.mark.parametrize('argv', [['--writ'], ['--check', '--write'], ['--write', 'extra']])
def test_audit_refuses_unknown_arguments(fake_lean, argv):
    with pytest.raises(SystemExit):
        audit.main(argv)


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
    assert audit.scan_sources(tmp_path) == [tmp_path / 'Admission.lean']


# A scratch tree: a VE module, a ResponseShape module and a Prop-class instance (compiled as a theorem).
SCRATCH = {
    'lakefile.toml': ('name = "scratch"\nversion = "0.1.0"\ndefaultTargets = ["VE"]\n[[lean_lib]]\nname = "VE"\n'
                      '[[lean_lib]]\nname = "ResponseShape"\nglobs = ["ResponseShape.*"]\n'),
    'VE.lean': 'import VE.Scratch\n',
    'VE/Scratch.lean': ('namespace VE.Scratch\ninductive Two where\n  | a | b\ninstance : Nonempty Two := ⟨.a⟩\n'
                        'theorem kept : True := trivial\n@[simp] theorem Nested.result : (1 : Nat) + 0 = 1 := rfl\n'
                        'theorem _root_.root_result : True := trivial\nend VE.Scratch\n'),
    'ResponseShape/Shape.lean': 'theorem ResponseShape.shape_ok : 1 = 1 := rfl\n',
    'VE/Audit.lean': '-- empty until the first --write\n',
    'ResponseShape/Audit.lean': '-- empty until the first --write\n',
}


@pytest.fixture
def scratch(tmp_path, monkeypatch):
    """A compiled scratch tree with its declaration list, the audit pointed at it; returns the dump step."""
    if shutil.which('lake') is None:
        pytest.skip('lake is not on PATH')
    lean = tmp_path / 'lean'
    for name, text in SCRATCH.items():
        (lean / name).parent.mkdir(parents=True, exist_ok=True)
        (lean / name).write_text(text)
    shutil.copy(ROOT / 'lean/lean-toolchain', lean / 'lean-toolchain')
    monkeypatch.setattr(audit, 'ROOT', lean)
    monkeypatch.setattr(audit, 'RECORD', lean / 'axioms.txt')

    def dump():
        statements, _, declarations = lean_statements.dump_all(tmp_path)
        (lean / 'declarations.txt').write_text(declarations)
        (lean / 'statements.txt').write_text(statements)
    dump()
    return lean, dump


def test_scratch_theorem_needs_write_and_check_passes_after(scratch, capsys):
    lean, dump = scratch
    instance = 'VE.Scratch.instNonemptyTwo'
    with pytest.raises(AssertionError, match=r'VE/Audit.lean is stale: missing \[.*VE.Scratch.kept'):
        audit.main(['--check'])
    audit.main(['--write'])
    text = (lean / 'VE/Audit.lean').read_text()
    assert text == (f'{audit.HEADER}-- The `#print axioms` audit of {audit.SCOPE["VE/Audit.lean"]}.\n'
                    f'import VE.Scratch\n\n#print axioms VE.Scratch.Nested.result\n#print axioms {instance}\n'
                    '#print axioms VE.Scratch.kept\n#print axioms root_result\n')
    assert (lean / 'ResponseShape/Audit.lean').read_text().endswith(
        'import ResponseShape.Shape\n\n#print axioms ResponseShape.shape_ok\n')
    assert audit.recorded_names((lean / 'axioms.txt').read_text()) == [
        'VE.Scratch.Nested.result', instance, 'VE.Scratch.kept', 'root_result', 'ResponseShape.shape_ok']
    audit.main(['--check'])
    # The statement dump lists the generated manifest's theorems, and the declaration list records the
    # manifest's hash: one dump after the write leaves every list current.
    dump()
    assert lean_statements.audited_names(lean.parent) == ['VE.Scratch.Nested.result', instance, 'VE.Scratch.kept',
                                                           'root_result']
    assert lean_statements.declaration_list(lean / 'declarations.txt')[1]['VE.Audit'] == \
        lean_statements.source_hash(lean / 'VE/Audit.lean')
    # A new module with a new theorem: stale until the dump, then missing from the manifest until --write.
    (lean / 'VE/Extra.lean').write_text('theorem VE.extra : 2 = 2 := rfl\n')
    (lean / 'VE.lean').write_text('import VE.Scratch\nimport VE.Extra\n')
    with pytest.raises(AssertionError, match=r'declarations.txt is stale: 2 modules .*\(VE, VE.Extra\)'):
        audit.main(['--check'])
    dump()
    with pytest.raises(AssertionError, match=r"missing \['VE.extra'\]"):
        audit.main(['--check'])
    audit.main(['--write'])
    assert '#print axioms VE.extra\n' in (lean / 'VE/Audit.lean').read_text()
    audit.main(['--check'])
    capsys.readouterr()


def test_scratch_stale_declarations_fail_check_and_write(scratch):
    """A module edited after the dump: neither --check nor --write passes, and --write writes nothing."""
    lean, _ = scratch
    audit.main(['--write'])
    before = {m: (lean / m).read_text() for m in audit.MANIFESTS}
    source = lean / 'VE/Scratch.lean'
    source.write_text(source.read_text().replace('end VE.Scratch', 'theorem later : True := trivial\nend VE.Scratch'))
    for argv in (['--check'], ['--write']):
        with pytest.raises(AssertionError, match=r'declarations.txt is stale: 1 modules .*\(VE.Scratch\)'):
            audit.main(argv)
    assert {m: (lean / m).read_text() for m in audit.MANIFESTS} == before
    # A module the list does not record at all (or records but the tree lacks) is stale too.
    declarations = (lean / 'declarations.txt').read_text()
    (lean / 'declarations.txt').write_text(declarations + f'module VE.Gone {"0" * 64}\n')
    with pytest.raises(AssertionError, match=r'declarations.txt is stale: 2 modules .*VE.Gone'):
        audit.main(['--check'])


def test_scratch_sorry_proof_fails_the_audit(scratch, monkeypatch):
    """A `sorry` proof fails the word scan; with the word scan blind to it, the `#print axioms` check."""
    lean, dump = scratch
    (lean / 'VE/Hole.lean').write_text('theorem VE.hole : 1 = 2 := by sorry\n')
    (lean / 'VE.lean').write_text('import VE.Scratch\nimport VE.Hole\n')
    with pytest.raises(AssertionError, match='VE/Hole.lean:1: forbidden sorry'):
        audit.main(['--write'])
    monkeypatch.setattr(audit, 'FORBIDDEN', audit.re.compile(r'\b(axiom|unsafe)\b'))
    dump()
    with pytest.raises(AssertionError, match=r"\('VE.hole', \{'sorryAx'\}\)"):
        audit.main(['--write'])
