"""AP-2's Lean declarations against the Lean block of docs/spec/act-phrases.md 5.6 (build checklist 17), and the check's
ability to fail: a missing theorem (ap-2bc review F1, `read_normal`) and a changed statement."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _checker(monkeypatch):
    # The checker imports `check_pc3_statements` from tools/, as when run; the path is restored after the test.
    monkeypatch.syspath_prepend(str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("check_ap56", ROOT / "tools/check_ap56_statements.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ap56_statements_equal_the_spec(monkeypatch):
    checker = _checker(monkeypatch)
    assert checker.main() == 0
    names = {name for _, name in checker.approved()}
    assert {"read_normal", "read_unique", "read_none", "read_many", "readings_exact", "readings_nodup",
            "readings_limit", "listing_ok", "grammar_wf", "analyse_one", "Derived"} == names


def test_a_missing_or_changed_statement_fails(tmp_path, capsys, monkeypatch):
    checker = _checker(monkeypatch)
    unique = ROOT / "lean/VE/Acts/NormalUnique.lean"
    others = [p for p in checker.SOURCES if p != unique]
    text = unique.read_text()
    cases = {
        # the theorem cut from the batch (review F1): no Lean declaration of that name
        "missing": text.replace("theorem read_normal (V", "theorem read_normal_cut (V"),
        # a weaker conclusion
        "weaker": text.replace("= .ok (.one a.canon) :=\n  NormalProofs", "≠ .none :=\n  NormalProofs"),
    }
    for name, changed in cases.items():
        assert changed != text, name
        path = tmp_path / f"{name}.lean"
        path.write_text(changed)
        assert checker.main([*others, path]) == 1, name
    out = capsys.readouterr().out
    assert "read_normal: theorem missing" in out
    assert "read_normal: theorem differs" in out


def test_a_header_naming_an_unproved_theorem_fails(tmp_path, capsys, monkeypatch):
    # ap-2bc review F2: NormalProofs' first sentence said `read_normal` holds while no theorem of that name existed
    checker = _checker(monkeypatch)
    unique = ROOT / "lean/VE/Acts/NormalUnique.lean"
    proofs = ROOT / "lean/VE/Acts/NormalProofs.lean"
    others = [p for p in checker.SOURCES if p not in (unique, proofs)]
    header = proofs.read_text().replace(
        "/-! The existence and bounds halves of `read_normal`",
        "/-! `read_normal`: the normal form of a `normalOk` atom reads back as its canonical atom. The halves of it", 1)
    assert header != proofs.read_text()
    cut = unique.read_text().replace("theorem read_normal (V", "theorem read_normal_cut (V")
    (tmp_path / "NormalProofs.lean").write_text(header)
    (tmp_path / "NormalUnique.lean").write_text(cut)
    assert checker.main([*others, tmp_path / "NormalProofs.lean", tmp_path / "NormalUnique.lean"]) == 1
    assert "NormalProofs.lean: its first sentence names `read_normal`, which Lean does not declare" in \
        capsys.readouterr().out
    # the same header with the theorem declared passes
    assert checker.main([*others, tmp_path / "NormalProofs.lean", unique]) == 0
