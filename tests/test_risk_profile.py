"""Risk declaration identity, gates, and fail-closed dispatch."""
from copy import deepcopy

import pytest

from tests.test_alternatives_profile import source
from ve.environment import Environment
from ve.errors import CheckerUnavailable, VEError
from ve.risk import run_case


def risk_source():
    raw = source()
    raw["profiles"].append("risk@0")
    raw["profiles"].sort()
    raw["vocabulary"]["constants"]["outage"] = {"sort": "harm", "description": "outage"}
    raw["risk"] = {
        "severity": {"sort": "severity", "classes": ["severe", "minor"],
                     "more_severe": [["severe", "minor"]], "unranked": [], "decided_by": "team"},
        "harm_classes": [["outage", "severe"]], "unexamined": "possible",
    }
    return raw


def test_block_round_trip_and_identity():
    raw = risk_source()
    env = Environment(raw)
    assert env.to_dict() == raw
    assert Environment(env.to_dict()).environment_id == env.environment_id
    changed = deepcopy(raw)
    changed["risk"]["unexamined"] = {"ruled_out_by": "team"}
    assert Environment(changed).environment_id != env.environment_id


@pytest.mark.parametrize("edit,diagnostic", [
    (lambda r: r["risk"].update(bands=[]), "stage B or C not enabled"),
    (lambda r: r["risk"].update(unknown=True), "InvalidInput: risk.unknown"),
    (lambda r: r["risk"]["severity"].update(sort="harm"), "RiskSeverityNotFresh"),
    (lambda r: r["risk"]["severity"].update(classes=["minor", "minor"]), "risk class minor"),
    (lambda r: r["risk"]["severity"].update(more_severe=[["severe", "minor"], ["minor", "severe"]]), "DependencyCycle"),
    (lambda r: r["risk"]["severity"].update(unranked=[["minor", "severe"]]), "RiskUnrankedAgainstOrder"),
    (lambda r: r["risk"].update(harm_classes=[]), "HarmUnclassified"),
    (lambda r: r["risk"].update(harm_classes=[["outage", "severe"]] * 2), "HarmTwoClasses"),
    (lambda r: r["alternatives"].update(outcomes={"complete_by": "team"}), "RiskOutcomes"),
    (lambda r: r["profiles"].remove("alternatives@0"), "risk@0 requires alternatives@0"),
])
def test_block_rejections(edit, diagnostic):
    raw = risk_source()
    edit(raw)
    with pytest.raises(VEError, match=diagnostic):
        Environment(raw)


def test_excludes_and_route_unavailable(monkeypatch, tmp_path):
    raw = risk_source()
    raw["alternatives"]["fulfilments"] = [{"obligation": "prevent_required", "body": "excludes"}]
    Environment(raw)
    case = {"id": "one", "kind": "risk-elaborate", "environment": raw, "norms": []}
    monkeypatch.setenv("VE_AUTHORITY", "python")
    with pytest.raises(CheckerUnavailable, match="Lean checker"):
        run_case(case)
    monkeypatch.delenv("VE_AUTHORITY")
    with pytest.raises(CheckerUnavailable, match="unavailable"):
        run_case(case, binary=tmp_path / "absent")
