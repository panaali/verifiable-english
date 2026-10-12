"""AR-4 F5: malformed saved scope is a report problem, never an exception."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPORT = Path(__file__).resolve().parents[1] / "docs/arch/AR-4/report.py"


@pytest.mark.parametrize("change", [
    lambda scope: scope.update(files=[1]),  # PROBE F5
    lambda scope: scope.update(files=None),
    lambda scope: scope.update(files={}),
    lambda scope: scope.update(commits=[7]),
    lambda scope: scope.update(commits=None),
    lambda scope: scope.update(base=7),
    lambda scope: scope.clear(),
], ids=["review-f5-probe", "null-files", "object-files", "bad-commit", "null-commits",
        "numeric-base", "empty-scope"])
def test_malformed_scope_is_a_report_problem(monkeypatch, capsys, change):
    spec = importlib.util.spec_from_file_location("ar4_report", REPORT)
    assert spec and spec.loader
    report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(report)
    scope = json.loads((report.EVIDENCE / "scope.json").read_text())
    change(scope)
    original = Path.read_text

    def read_text(path, *args, **kwargs):
        return json.dumps(scope) if path.name == "scope.json" else original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)
    assert any("scope" in problem for problem in report.problems())
    assert report.main(["--check"]) == 1
    assert "scope" in capsys.readouterr().err
