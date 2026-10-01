"""The authored BlueDot reading keeps source bytes and modalities separate."""
from __future__ import annotations

import importlib
import json
from collections import Counter
from hashlib import sha256
from pathlib import Path

from ve.document import check_document, load_document

ROOT = Path(__file__).resolve().parents[1] / "usecases/bluedot-grant"
SOURCE_HASH = "a9fa225acce6a684af7519c9c6fa82a20fc3a7e685a04b7e1a4bac88a0d6ed22"
choices = importlib.import_module("usecases.bluedot-grant.author_choices")
features = importlib.import_module("usecases.bluedot-grant.feature_readings")


def test_source_partition_and_author_decisions():
    source = (ROOT / "source.md").read_bytes()
    assert sha256(source).hexdigest() == SOURCE_HASH
    assert len(source) == 7619
    doc = load_document(ROOT / "document.ve.md")
    assert doc["source"] == source
    assert len(doc["units"]) == 93
    assert [u["id"] for u in doc["units"]] == [f"u{i:03d}" for i in range(1, 94)]
    cursor = 0
    for unit in doc["units"]:
        assert unit["span"][0] == cursor
        cursor = unit["span"][1]
        assert unit["source"].encode() == source[slice(*unit["span"])]
    assert cursor == len(source)
    assert set(choices.CHOICES) == {"matched_cost", "real_artefact", "affordable_proof",
                                    "misleading_formalisation", "catastrophic_risk"}
    for name, choice in choices.CHOICES.items():
        assert choice["signature"] == "grant-author" and choice["why"] and choice["rule"]
        defined = doc["environment"].to_dict()["vocabulary"]["predicates"][name]["defined"]
        assert defined["body"] and defined["arguments"] == ["artifact"]
    assert Counter(u["status"] for u in doc["units"]) == {
        "CHECKED": 67, "LABELLED": 25, "UNFORMALISED": 1}
    assert all(u["status"] != "OPEN" for u in doc["units"])
    assert doc["units"][32]["status"] == "LABELLED"  # predictive "should help"
    assert doc["units"][68]["meaning"] == {"unformalised": "vague_comparison"}


def test_operational_boundaries_do_not_supply_world_facts():
    costs = {k: 0 for k in ("authoring", "formalisation", "proof", "compute", "review")}
    record = {"same_task": True, "budget_record_id": "pre-1",
              "arms": {"proof": {**costs, "proof": 100},
                       "cross_examination": {**costs, "review": 95}}}
    assert choices.decide("matched_cost", record)
    record["arms"]["cross_examination"]["review"] = 94
    assert not choices.decide("matched_cost", record)
    assert not choices.decide("matched_cost", {})
    artefact = {"provenance_sha256": "a" * 64, "created_on": "2026-08-01",
                "selected_on": "2026-09-01", "independent_task": True,
                "evaluator_seeded_flaw": False}
    assert choices.decide("real_artefact", artefact)
    assert not choices.decide("real_artefact", {**artefact, "created_on": "2026-09-02"})
    proof = {"certificate_checked": True, "formalisation_cost_recorded": True,
             "total_cost": "100", "preregistered_budget": "100",
             "elapsed_hours": "2", "preregistered_deadline_hours": "2"}
    assert choices.decide("affordable_proof", proof)
    assert not choices.decide("affordable_proof", {**proof, "total_cost": "100.01"})
    fidelity = {"source_sha256": "a" * 64, "formula_sha256": "b" * 64,
                "counterexample_id": "case-1", "answer_changes": True,
                "blind_reviewers": ["r1", "r2"]}
    assert choices.decide("misleading_formalisation", fidelity)
    assert not choices.decide("misleading_formalisation", {**fidelity, "blind_reviewers": ["r1", "r1"]})
    risk = {"pathway_record_id": "path-1", "evidence_record_id": "evidence-1",
            "projected_deaths": 1_000_000}
    assert choices.decide("catastrophic_risk", risk)
    assert not choices.decide("catastrophic_risk", {**risk, "projected_deaths": 999_999})


def test_feature_readings_are_checked_on_their_own_routes():
    artifact = json.loads((ROOT / "feature-readings.json").read_text())
    assert artifact["source_sha256"] == SOURCE_HASH
    assert artifact["signature"] == "grant-author"
    actual = {"speech_acts": features.check_commands(), "reports": features.check_reports(),
              "risk_possibility": features.check_risk(), "time": features.check_dates()}
    assert actual == artifact["readings"]
    assert set(actual["speech_acts"]) == set(features.COMMANDS)
    assert set(actual["risk_possibility"]) == set(features.RISK_WORDINGS)


def test_document_coverage_and_premise_limit():
    result = check_document(ROOT / "document.ve.md")
    coverage = result["coverage"]
    assert coverage["source_bytes"] == coverage["accounted_bytes"] == 7619
    assert coverage["coverage_percent"] == 100
    assert coverage["bytes_by_status"] == {
        "CHECKED": 6709, "LABELLED": 853, "UNFORMALISED": 57}
    assert coverage["unformalised_reasons"] == {"vague_comparison": 1}
    assert coverage["residual"]["open_terms"] == 0
    assert result["premises"]["status"] in {"UNKNOWN", "model", "inconsistent"}
