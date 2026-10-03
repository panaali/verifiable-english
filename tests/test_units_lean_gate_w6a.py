"""No W6 proof claim may pass the frozen Lean route by erasing tags first."""
import json
from pathlib import Path
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT

ROOT =Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_conformance"
FIXTURE = ROOT / "usecases" / "news-article" / "w6a-quantity-fixtures.json"
pytestmark = pytest.mark.skipif(not LEAN.exists(), reason="build Lean route runner first")


def test_extended_environment_is_not_raw_order_evidence():
    environment = json.loads(FIXTURE.read_text())["environment"]
    forged = {"id": "tag-erasure-bypass", "kind": "evaluate", "environment": environment,
              "ast": [["lt", ["num", "375"], ["num", "400"]]]}
    process = subprocess.run([str(LEAN), "route", "-"], input=json.dumps([forged]),
                             text=True, capture_output=True, timeout=HANG_TIMEOUT)
    result = json.loads(process.stdout)[0]
    assert process.returncode == 1
    assert result["status"] == "error" and "unit_schema" in result["error"]
