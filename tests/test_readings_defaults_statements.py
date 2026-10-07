"""The RD-1 theorem statements against the approved text of docs/spec/readings-defaults.md 6.2."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _checker():
    spec = importlib.util.spec_from_file_location("check_rd", ROOT / "tools/check_readings_defaults_statements.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rd1_statements_match_the_approved_text(capsys):
    checker = _checker()
    assert checker.main() == 0
    out = capsys.readouterr().out
    assert "checked 10 approved RD-1 statements" in out
    assert set(checker.PENDING) == {"attached_fillDoc"}


def test_rd1_checker_fails_on_a_changed_statement(tmp_path, capsys):
    checker = _checker()
    source = checker.SOURCE.read_text()
    mutated = source.replace("(hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (s : String) (i : Nat) :",
                             "(hf : fillNamesFree N = true) (s : String) (i : Nat) :", 1)
    assert mutated != source
    path = tmp_path / "Unspecified.lean"
    path.write_text(mutated)
    checker.SOURCE = path
    assert checker.main() == 1
    assert "fillDoc_one: statement differs" in capsys.readouterr().out


def test_rd1_checker_fails_when_a_pending_entry_is_stale(tmp_path):
    checker = _checker()
    source = checker.SOURCE.read_text()
    restored = source.replace("(hs : singlyAttached N.D = true) (u : String)", "(u : String)", 1)
    assert restored != source
    path = tmp_path / "Unspecified.lean"
    path.write_text(restored)
    checker.SOURCE = path
    assert checker.main() == 1
