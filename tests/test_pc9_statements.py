"""PC-9's Lean declarations against the approved blocks of docs/spec/profile-composition.md 1.8 and 1.9 (build
checklist 17), and the check's ability to fail."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _checker(monkeypatch):
    # The checker imports `check_pc3_statements` from tools/, as when run; the path is restored after the test, so a
    # later test's `import question_fixtures` still finds tests/question_fixtures.py, not tools/'s generator.
    monkeypatch.syspath_prepend(str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("check_pc9", ROOT / "tools/check_pc9_statements.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pc9_statements_equal_the_approved_text(monkeypatch):
    checker = _checker(monkeypatch)
    assert checker.main() == 0
    names = {name for _, name in checker.approved()}
    assert {"precedence_apart", "dfltUniform_legacy", "ConditionsExact", "dfltUniform_sound", "providerConditions",
            "providerRefusal", "dfltUniformOf"} <= names


def test_a_changed_statement_fails(tmp_path, capsys, monkeypatch):
    checker = _checker(monkeypatch)
    text = checker.SOURCES[0].read_text()
    cases = {
        "legacy": text.replace("(h : ∀ p ∈ qs, p.conditions = []) :\n    dfltUniformLabelled",
                               ":\n    dfltUniformLabelled"),
        "sound": text.replace("(hD : WellFormedSoft D = true) (qs : List Pack) (hex : ConditionsExact.{u} U D qs) (B",
                              "(qs : List Pack) (hex : ConditionsExact.{u} U D qs) (B", 1),
        "guard": text.replace("qs.any (!·.conditions.isEmpty)", 'qs.any (fun p => p.id == "weighing")'),
        "least": text.replace("(B : VE.Structure.{u}) : String → List B.Carrier → Prop :=",
                              "(B : VE.Structure.{u}) : String → List B.Carrier → Bool :="),
    }
    for name, changed in cases.items():
        assert changed != text, name
        path = tmp_path / f"{name}.lean"
        path.write_text(changed)
        assert checker.main([path]) == 1, name
    out = capsys.readouterr().out
    for name in ("dfltUniform_legacy: theorem", "dfltUniform_sound: theorem", "providerConditions: def",
                 "leastUniform: def"):
        assert f"{name} differs" in out, name
