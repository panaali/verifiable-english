"""The Stage 0 baseline in shadow: fixtures L9 and Z3 of docs/spec/mig3.md (8.3, 8.5).

The whole probe matrix runs through ``tools/shadow_baseline.py``, with the
classes of ``tools/stage2_parity.py --authority lean`` for its cells that have
neither a compared nor an uncompared call.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from subprocesses import HANG_TIMEOUT
from tools import shadow_baseline

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "conformance/baseline-2026-09/python.json"


def _environment() -> dict:
    # Each tool chooses its own authorities; nothing of the caller's shadow run reaches it.
    return {name: value for name, value in os.environ.items()
            if not name.startswith(("VE_AUTHORITY", "VE_SHADOW"))}


def _tool(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=ROOT, env=_environment(), capture_output=True,
                          text=True, timeout=HANG_TIMEOUT)


def test_l9_z3_every_probe_cell_in_shadow(tmp_path):
    parity, summary = tmp_path / "parity.json", tmp_path / "shadow.json"
    done = _tool("tools/stage2_parity.py", "--authority", "lean", "--json", str(parity))
    assert done.returncode == 0, done.stdout[-2000:] + done.stderr[-2000:]
    done = _tool("tools/shadow_baseline.py", "--parity", str(parity), "--json", str(summary))
    result = json.loads(summary.read_text())
    assert done.returncode == 0, result
    cells = len(json.loads(BASELINE.read_text())["cells"])
    # L9: every cell has a compared call, an uncompared call, or is "same, python".
    assert result["cells"] == cells
    assert result["compared"] + result["uncompared"] + result["neither"] == cells
    assert result["compared"] > 0
    assert set(result["neither_parity_classes"]) <= {"same, python"}
    assert sum(result["neither_parity_classes"].values()) == result["neither"]
    # V1: the shadow call's result is today's Python result on every cell.
    assert result["shadow_differs_count"] == 0, result["shadow_differs_from_python"]
    # Z3 (V4): the candidate never changed the object Python returned.
    assert result["v4_count"] == 0, result["v4_violations"]


def test_z3_a_candidate_that_changes_pythons_object_is_reported(monkeypatch):
    """The V4 check can fail: a candidate that edits the object Python returned."""
    monkeypatch.setattr(shadow_baseline, "_v4", [])
    value = {"status": "Satisfied"}

    def run(op, payload, python, lean):
        returned = python()
        lean()
        return returned

    def candidate():
        value["status"] = "Violated"
        return dict(value)

    assert shadow_baseline._checked_shadow(run)("evaluate", {}, lambda: value, candidate) is value
    assert shadow_baseline._v4 == ["evaluate: the candidate changed Python's returned object"]
    monkeypatch.setattr(shadow_baseline, "_v4", [])
    assert shadow_baseline._checked_shadow(run)("evaluate", {}, lambda: {"status": "ok"},
                                                lambda: {"status": "ok"}) == {"status": "ok"}
    assert shadow_baseline._v4 == []
