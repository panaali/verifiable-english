"""The RD-1 declarations against the approved text of docs/spec/readings-defaults.md 6.2."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _checker():
    spec = importlib.util.spec_from_file_location("check_rd", ROOT / "tools/check_readings_defaults_statements.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _approved_names():
    return sorted(_checker().approved())


def test_rd1_statements_match_the_approved_text(capsys):
    checker = _checker()
    assert checker.main() == 0
    out = capsys.readouterr().out
    assert "checked 31 approved RD-1 declarations (10 theorems)" in out
    # Review B2: the DRI approved `attached_fillDoc`'s added hypothesis; 6.2 states it, so nothing is pending.
    assert checker.PENDING == {}
    assert "0 pending" in out


def test_the_definitions_are_compared_too():
    """Review B2: the 6.2 definitions, not only the theorems, are read from the spec block and compared."""
    names = {name for kind, name in _checker().approved() if kind == "def"}
    assert {"AchievesU", "fillDoc", "fillNamesFree", "normsShaped", "WellFormedND"} <= names


def _mutate(source, kind, name, checker):
    """`source` with the Lean declaration `kind name` changed at the end of its compared text."""
    import re
    start = re.search(rf"^{kind} {re.escape(name)}\b", source, re.M)
    line_end = source.find("\n", start.end())
    stop = checker.STOP.search(source, line_end + 1)
    text = source[start.start():stop.start()]
    if kind == "theorem":
        head, proof = text.split(":=", 1)
        changed = head.rstrip() + " ∧ True :=" + proof
    else:
        changed = text.rstrip() + " ∧ True\n"
    return source[:start.start()] + changed + source[stop.start():]


@pytest.mark.parametrize("kind, name", _approved_names(), ids=lambda v: str(v))
def test_rd1_checker_fails_on_every_changed_declaration(tmp_path, capsys, kind, name):
    """Each declaration of the spec block, changed in Lean, fails the check by name (checklist 13: the check can
    fail on every item it lists)."""
    checker = _checker()
    path = tmp_path / "Unspecified.lean"
    path.write_text(_mutate(checker.SOURCE.read_text(), kind, name, checker))
    checker.SOURCE = path
    assert checker.main() == 1
    assert f"{name}: {kind} differs" in capsys.readouterr().out


def test_rd1_checker_fails_on_a_dropped_hypothesis(tmp_path, capsys):
    checker = _checker()
    source = checker.SOURCE.read_text()
    mutated = source.replace("(hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (s : String) (i : Nat) :",
                             "(hf : fillNamesFree N = true) (s : String) (i : Nat) :", 1)
    assert mutated != source
    path = tmp_path / "Unspecified.lean"
    path.write_text(mutated)
    checker.SOURCE = path
    assert checker.main() == 1
    assert "fillDoc_one: theorem differs" in capsys.readouterr().out


def test_rd1_checker_fails_on_the_first_approved_attached_statement(tmp_path, capsys):
    """Review B2: the statement without `singlyAttached` (false, F-ND11) is no longer accepted as pending."""
    checker = _checker()
    source = checker.SOURCE.read_text()
    restored = source.replace("(hs : singlyAttached N.D = true) (u : String)", "(u : String)", 1)
    assert restored != source
    path = tmp_path / "Unspecified.lean"
    path.write_text(restored)
    checker.SOURCE = path
    assert checker.main() == 1
    assert "attached_fillDoc: theorem differs" in capsys.readouterr().out


def test_rd1_checker_fails_when_a_pending_entry_is_stale(capsys):
    checker = _checker()
    checker.PENDING = {"attached_fillDoc": "seeded"}
    assert checker.main() == 1
    assert "attached_fillDoc: listed as pending but matches the approved text" in capsys.readouterr().out


def test_rd1_checker_fails_on_a_missing_declaration(tmp_path, capsys):
    checker = _checker()
    path = tmp_path / "Unspecified.lean"
    path.write_text(checker.SOURCE.read_text().replace("def fillHolds ", "private def fillHolds ", 1))
    checker.SOURCE = path
    assert checker.main() == 1
    assert "fillHolds: expected one Lean def, found 0" in capsys.readouterr().out
