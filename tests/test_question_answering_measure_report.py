"""F4: published numbers must agree with captured measurements and fixtures."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("question_answering_report", ROOT / "tools/question_answering_report.py")
REPORT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REPORT)


def test_q2_measurement_report_is_generated_from_saved_evidence():
    assert REPORT.DESTINATION.read_text() == REPORT.render()
    fixtures = json.loads((REPORT.EVIDENCE / "fixtures.json").read_text())["fixtures"]
    agreement = json.loads((REPORT.EVIDENCE / "agreement.json").read_text())["rows"]
    assert {row["fixture"] for row in agreement} == {row["id"] for row in fixtures}
    assert any(row["status"] == "compared" for row in agreement)
