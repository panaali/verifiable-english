"""Baseline route rejects integer-quantifier W6b syntax before evidence."""
import json
import os
from pathlib import Path
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from ve.environment import Environment
from ve.errors import UnsupportedProfile
from ve.units import elaborate_quantity

ROOT = Path(__file__).resolve().parents[1]
RUST = Path(os.environ.get("VE_RUST_BINARY", str(ROOT / "rust" / "target" / "release" / "ve")))
FIXTURE = ROOT / "usecases" / "news-article" / "w6a-quantity-fixtures.json"


@pytest.mark.parametrize("formula", [
    ["sunday", ["date", "2026-09-20"]],
    ["excluded_sundays", ["date", "2026-10-01"], ["date", "2026-09-20"], "10"],
    ["forall_date", ["top"]],
    ["exists_date", ["top"]],
    ["trace_all", "review_window", ["top"]],
    ["trace_some", "review_window", ["top"]],
    ["forall", "$int", "dimensionless", ["top"]],
])
def test_integer_quantifier_forms_are_gated(formula):
    raw = json.loads(FIXTURE.read_text())["environment"]
    payload = {"format": "ve-quantity@1", "formula": formula}
    with pytest.raises(UnsupportedProfile, match="numbers2"):
        elaborate_quantity(Environment(raw), payload)
    if RUST.exists():
        case = {"id": "gate", "kind": "quantity", "environment": raw, "quantity": payload}
        process = subprocess.run([str(RUST), "conformance", "-"], input=json.dumps(case),
                                 capture_output=True, text=True, timeout=HANG_TIMEOUT)
        result = json.loads(process.stdout)[0]
        assert result["status"] == "error" and "numbers2" in result["error"]["message"]
