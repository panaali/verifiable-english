"""Structural checks for B2 shadow-evidence binding, using synthetic gate data."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("b2_shadow", ROOT / "docs/test-speed-b2/shadow.py")
assert spec and spec.loader
shadow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shadow)


@pytest.fixture
def shadow_record(tmp_path, monkeypatch):
    """Ten paired records, including one failed gate whose failure is selected."""
    monkeypatch.setattr(shadow, "ROOT", tmp_path)
    monkeypatch.setattr(shadow, "MAP", tmp_path / "map.json")
    monkeypatch.setattr(shadow, "FIRST_GATE", "first.json")
    monkeypatch.setattr(shadow, "digest", lambda path: f"digest:{path.name}")
    monkeypatch.setattr(shadow.test_map, "load", lambda path: {
        "commit": "map-commit", "tests": ["tests/test_fail.py", "tests/test_other.py"]})
    monkeypatch.setattr(shadow, "git", lambda *args: "")
    (tmp_path / "first.json").write_text(json.dumps({
        "status": "failed", "failures": [{"nodeid": "tests/test_fail.py::test_case"}]}))
    rows = []
    for index in range(10):
        gate_name = f"gate-{index}.json"
        (tmp_path / gate_name).write_text(json.dumps({
            "status": "passed", "commit_sha": f"commit-{index}",
            "counts": {"collected": 2}, "failures": []}))
        selected = (["tests/test_fail.py", "tests/test_other.py"] if index == 0
                    else ["tests/test_other.py"])
        rows.append({"item": "eff-tests" if index == 0 else f"item-{index}",
                     "merge": f"merge-{index}", "paths": [], "gate": gate_name,
                     "gate_sha256": f"digest:{gate_name}", "gate_commit": f"commit-{index}",
                     "full_collected": 2, "selected": selected,
                     "selected_count": len(selected), "full_count": 2,
                     "full_failures": [], "failures_outside_selection": []})
    return {"schema": 1, "map_sha256": "digest:map.json", "map_commit": "map-commit",
            "merges": rows,
            "first_gate_probe": {"gate": "first.json", "sha256": "digest:first.json",
                                 "status": "failed", "failed_files": ["tests/test_fail.py"],
                                 "outside_selection": []}}


def test_failed_gate_probe_is_bound_to_selected_files(shadow_record):
    shadow.check(shadow_record)
    changed = copy.deepcopy(shadow_record)
    row = next(row for row in changed["merges"] if row["item"] == "eff-tests")
    row["selected"].remove("tests/test_fail.py")
    row["selected_count"] = len(row["selected"])
    with pytest.raises(AssertionError):
        shadow.check(changed)


def test_shadow_merge_failure_exclusion_is_recomputed(shadow_record):
    changed = copy.deepcopy(shadow_record)
    row = next(row for row in changed["merges"] if row["item"] == "eff-tests")
    row["failures_outside_selection"].append("tests/test_fail.py")
    with pytest.raises(AssertionError):
        shadow.check(changed)
