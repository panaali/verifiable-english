"""Regression checks for the B2 activation evidence."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/test-speed-b2/evidence"
spec = importlib.util.spec_from_file_location("b2_shadow", ROOT / "docs/test-speed-b2/shadow.py")
assert spec and spec.loader
shadow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shadow)


def test_failed_gate_probe_is_bound_to_selected_files():
    data = json.loads((EVIDENCE / "shadow.json").read_text())
    shadow.check(data)
    changed = copy.deepcopy(data)
    row = next(row for row in changed["merges"] if row["item"] == "eff-tests")
    row["selected"].remove("tests/test_run_cache.py")
    row["selected_count"] = len(row["selected"])
    with pytest.raises(AssertionError):
        shadow.check(changed)


def test_each_saved_shadow_failure_exclusion_is_recomputed():
    data = json.loads((EVIDENCE / "shadow.json").read_text())
    changed = copy.deepcopy(data)
    row = next(row for row in changed["merges"] if row["item"] == "eff-tests")
    row["failures_outside_selection"].append("tests/test_run_cache.py")
    with pytest.raises(AssertionError):
        shadow.check(changed)
