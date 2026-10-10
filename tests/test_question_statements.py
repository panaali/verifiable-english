"""The Q2 declarations (`lean/VE/Ask`, `lean/VE/Words`) against the approved text of docs/spec/question-answering.md
5.2 (build checklist 17), by `tools/question_statements.py --q2`: the text, then Lean elaborating every approved
statement and signature against the implementation."""
from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _checker():
    spec = importlib.util.spec_from_file_location("question_statements", ROOT / "tools/question_statements.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_q2_statements_match_the_approved_text(capsys):
    checker = _checker()
    assert checker.q2(lean=True) == 0
    out = capsys.readouterr().out
    assert "Q2 statements: 27 of 27 implemented; 0 missing; 0 differ in text" in out
    assert "32 equal to the approved text, 0 changed" in out and "0 absent" in out
    assert "Q2 Lean check: 41 approved statements and signatures elaborated against the implementation; PASS" in out
    # The one listed difference is a DRI item of the batch's DELTA.md.
    assert set(checker.DIFFERENCES) == {"Asked"}
    assert "changed Asked: `hnames` uses `NameReadsBackSame`" in out


def _copy_with(tmp_path, file, old, new):
    sources = []
    for source in _checker().Q2_SOURCES:
        target = tmp_path / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        text = source.read_text()
        if source.name == file:
            assert old in text
            text = text.replace(old, new, 1)
        target.write_text(text)
        sources.append(target)
    return sources


def test_a_changed_statement_or_definition_fails(tmp_path, monkeypatch, capsys):
    checker = _checker()
    mutants = [
        ("Sound.lean", "theorem lead_sound :", "theorem lead_sound' :"),           # a statement missing
        ("Basic.lean", "else if r.split then .notSettled", "else if r.split then .notNecessarily"),  # a body changed
        ("Render.lean", "theorem render_asked :", "theorem render_asked' :"),
        ("Binding.lean", "∀ k ∈ boundKeys,", "∀ k ∈ boundKeys.tail,"),          # an approved predicate changed
        # The same statement up to a bound name: Lean accepts it; the text check does not.
        ("Render.lean", "theorem render_asked : ∀ (ctx : Context) (a : Answer), (render ctx a).head?",
         "theorem render_asked : ∀ (c : Context) (a : Answer), (render c a).head?"),
    ]
    for i, (file, old, new) in enumerate(mutants):
        sources = _copy_with(tmp_path / str(i), file, old, new)
        monkeypatch.setattr(checker, "Q2_SOURCES", sources)
        assert checker.q2(lean=False) == 1, (file, old)
    capsys.readouterr()


def test_lean_refuses_a_statement_the_implementation_does_not_prove(tmp_path, monkeypatch, capsys):
    """The Lean oracle is not vacuous: an approved statement with a changed conclusion does not elaborate against
    the implemented theorem, though the text is read from the spec."""
    checker = _checker()
    spec = tmp_path / "spec.md"
    text = checker.SPEC.read_text()
    old = "→ (renderGroup ctx a g).filterMap (·.source) = g.cited"
    assert old in text
    spec.write_text(text.replace(old, "→ (renderGroup ctx a g).filterMap (·.source) = g.cited.reverse", 1))
    monkeypatch.setattr(checker, "SPEC", spec)
    assert shutil.which("lake")
    assert checker.q2(lean=True) == 1
    assert "Q2 Lean check: 41 approved statements and signatures elaborated against the implementation; FAIL" in \
        capsys.readouterr().out
