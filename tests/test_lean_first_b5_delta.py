"""Batch 5's direct-entry changes are visible beside the recorded A/B corpus."""
import json
from pathlib import Path


B5 = Path(__file__).resolve().parents[1] / "docs/lean-first/b5"


def test_direct_entry_changes_are_recorded_with_dri_disposition():
    delta = json.loads((B5 / "delta.json").read_text())
    entries = delta["outside_corpus"]
    assert {(entry["test"], entry["class"]) for entry in entries} == {
        ("tests/test_asimov_laws.py::test_permission_default_stays_allow_until_norm_defaults_combines_with_alternatives", "wording"),
        ("tests/test_lean_first_triage.py::test_df12_risk_route_rejects_an_nbsp_act_phrase", "verdict"),
    }
    for entry in entries:
        path, test = entry["test"].split("::")
        assert f"def {test}(" in (B5.parents[2] / path).read_text()
        assert entry["base"] != entry["head"]
        assert entry["dri"]["owner"] == "DRI"
        assert entry["dri"]["status"] == "pending"
        assert entry["dri"]["reason"]
    assert {"base": entries[0]["base"]["message"],
            "head": entries[0]["head"]["message"]} in delta["wording"]
    assert delta["verdict"] == []  # the direct route is outside the A/B recorder's corpora
