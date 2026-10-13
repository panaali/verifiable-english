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


def test_the_budgets_are_met_and_the_corpus_agreement_is_recorded():
    """F4 (qa-q2 recheck): the saved measurements meet the plan's pass gates (`ask` Lean CPU at most 2 s, U3 `ve ask`
    wall at most 60 s), and the agreement of the corpora's queries is recorded with no lead that contradicts the
    existing route (`tools/question_answering_agreement.py`)."""
    measurements = json.loads((REPORT.EVIDENCE / "measurements.json").read_text())["fixtures"]
    assert all(row["ask"]["cpu_s"] <= 2 for row in measurements.values())
    assert measurements["U3"]["ve ask"]["wall_s"] <= 60
    saved = json.loads((REPORT.EVIDENCE / "agreement.json").read_text())
    assert not any(row["status"].startswith("requires review") for row in saved["rows"])
    corpus = saved["corpus"]
    assert corpus["queries"] == len(corpus["rows"]) > 0
    # A comparison that needs review is reviewed in the evidence and is a row of DELTA.md (D15), never silent.
    delta = (ROOT / "docs/spec/question-answering-q2/DELTA.md").read_text()
    assert corpus["requires_review"] == [r for r in corpus["rows"] if r["status"].startswith("requires review")]
    for row in corpus["requires_review"]:
        assert row["review"].startswith("reviewed (DELTA D") and row["review"][16:19].rstrip(")") in delta, row
    assert {"readings", "norm-defaults"} <= set(corpus["counts"])
    assert sum(counts.get("agrees", 0) for counts in corpus["counts"].values()) > 0
    for row in corpus["rows"]:
        if row["status"] == "agrees":
            assert row["question"].startswith("Is it the case that ") and row["leads"]
