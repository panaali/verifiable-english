"""The x86 essentials leg audits Lean candidates even when the Mac gate is unavailable.

This file matches x86-essentials.py's test_lean_service*.py selector. The full
gate already runs lean/audit.py as its own stage; x86 essentials needs this run.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest

from tests.subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]


def test_x86_essentials_runs_lean_audit():
    collection = os.environ.get("VE_GATE_PYTEST_RESULT", "")
    if Path(collection).parent.name.startswith("ve-x86e-"):
        result = subprocess.run([sys.executable, "lean/audit.py"], cwd=ROOT, text=True,
                                capture_output=True, timeout=HANG_TIMEOUT, check=False)
        assert result.returncode == 0, result.stderr[-2000:] + result.stdout[-2000:]
    else:
        # In the full gate the audit is a stage rather than an essentials test.
        source = (ROOT / "tools/gate.py").read_text()
        assert 'stage="Lean audit"' in source
        assert 'result["stages"].append("lean_audit")' in source


def test_x86_audit_refuses_failure_and_accepts_success(monkeypatch):
    monkeypatch.setenv("VE_GATE_PYTEST_RESULT", "/tmp/ve-x86e-fixture/pytest-collection.json")
    calls = []

    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="audit failed")

    monkeypatch.setattr(subprocess, "run", run)
    with pytest.raises(AssertionError, match="audit failed"):
        test_x86_essentials_runs_lean_audit()
    assert calls and calls[0][0][-1] == "lean/audit.py"

    def succeeds(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", succeeds)
    test_x86_essentials_runs_lean_audit()
