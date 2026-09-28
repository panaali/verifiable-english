"""Authority boundaries: fail closed, preserve Python in shadow, classify drift."""
from __future__ import annotations

import json

import pytest

from ve.backends.diagnostics import checker_error
from ve.backends.dispatch import authority_for, execute
from ve.backends.lean_service import CheckerUnavailable
from ve.errors import InvalidModel, ResourceLimit, VEError


def test_authority_override_and_rejection(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "evaluate=python,background=shadow")
    assert authority_for("evaluate") == "python"
    assert authority_for("background") == "shadow"
    assert authority_for("check") == "lean"
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "broken")
    with pytest.raises(ValueError):
        authority_for("evaluate")


def test_selected_authority_never_falls_back(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    with pytest.raises(CheckerUnavailable):
        execute("missing", {}, lambda: pytest.fail("Python executed"))


def test_shadow_returns_python_and_logs_drift(monkeypatch, tmp_path):
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    result = execute("evaluate", {"ast": ["top"]},
                     lambda: {"status": "Satisfied", "evaluations": 1},
                     lean=lambda: {"status": "Violated", "evaluations": 2})
    assert result == {"status": "Satisfied", "evaluations": 1}
    row = json.loads(log.read_text())
    assert row["class"] == ["count-value", "verdict"]
    assert row["op"] == "evaluate" and len(row["input_digest"]) == 64


def test_shadow_records_unavailable_checker(monkeypatch, tmp_path):
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    assert execute("check", {}, lambda: {"status": "ok"},
                   lean=lambda: (_ for _ in ()).throw(CheckerUnavailable("gone"))) == {"status": "ok"}
    assert json.loads(log.read_text())["lean"]["code"] == "CheckerUnavailable"


def test_checker_diagnostics_keep_code_and_generator():
    error = checker_error("InvalidModel(flags): mismatched relation")
    assert isinstance(error, InvalidModel) and error.generator == "flags"
    assert isinstance(checker_error("ResourceLimit: exhausted"), ResourceLimit)
    assert type(checker_error("unexpected decoder text")) is VEError
