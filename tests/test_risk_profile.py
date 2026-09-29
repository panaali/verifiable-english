"""Risk declaration identity, gates, and fail-closed dispatch."""
from copy import deepcopy

import pytest

from ve.environment import Environment
from ve.english import parse_english_with_metadata
from ve.errors import CheckerUnavailable, VEError
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.risk import run_case
from ve.surface.registry import by_tag, enabled
from ve.surface.risk import parse_wording


def risk_source():
    raw = {"language": LANGUAGE, "spec_revision": SPEC_REVISION,
           "profiles": ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"],
           "vocabulary": {
               "sorts": {name: {"description": name} for name in ("chooser", "action", "harm")},
               "predicates": {
                   "available": {"arguments": ["action", "chooser"], "description": "available",
                                 "verbalisation": "{0} is available to {1}"},
                   "leads_to": {"arguments": ["action", "harm"], "description": "leads",
                                "verbalisation": "{0} leads to {1}"},
                   "prevent_required": {"arguments": ["chooser", "harm"], "description": "prevent",
                                        "regulated": {"role": "obligation", "default": "deny",
                                                      "act": "{0} prevent {1}"}},
               },
               "constants": {"outage": {"sort": "harm", "description": "outage"}},
           },
           "alternatives": {"chooser": "chooser", "action": "action", "harm": "harm",
                            "available": "available", "leads_to": "leads_to", "outcomes": "signed"}}
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


def test_risk_block_with_w6_quantity_kind_round_trips():
    raw = risk_source()
    raw["profiles"] += ["order@0", "time@0"]
    raw["profiles"].sort()
    raw["unit_schema"] = "ve-units@1"
    raw["units"] = {"gb": {"scale": "10", "display": {"kind": "decimal", "label": "GB"}}}
    raw["risk"]["quantity_kinds"] = {"memory": "gb"}
    env = Environment(raw)
    assert env.to_dict() == raw


@pytest.mark.parametrize("edit,diagnostic", [
    (lambda r: r["risk"].update(bands=[]), "stage B or C not enabled"),
    (lambda r: r["risk"].update(unknown=True), "InvalidInput: risk.unknown"),
    (lambda r: r["risk"]["severity"].update(sort="harm"), "RiskSeverityNotFresh"),
    (lambda r: r["risk"]["severity"].update(classes=["minor", "minor"]), "risk class minor"),
    (lambda r: r["risk"]["severity"].update(classes=["avoidable"]), "RiskReserved"),
    (lambda r: r["risk"]["severity"].update(more_severe=[["severe", "minor"], ["minor", "severe"]]), "DependencyCycle"),
    (lambda r: r["risk"]["severity"].update(unranked=[["minor", "severe"]]), "RiskUnrankedAgainstOrder"),
    (lambda r: r["risk"].update(harm_classes=[]), "HarmUnclassified"),
    (lambda r: r["risk"].update(harm_classes=[["outage", "severe"]] * 2), "HarmTwoClasses"),
    (lambda r: r["alternatives"].update(outcomes={"complete_by": "team"}), "RiskOutcomes"),
    (lambda r: r["profiles"].remove("alternatives@0"), "risk@0 requires alternatives@0"),
    (lambda r: r["risk"].update(required_alternatives=[{"when": [], "require": []}]), "risk.required_alternatives"),
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


def test_decision_envelope_shape_precedes_dispatch(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    case = {"id": "one", "kind": "risk-decision", "environment": risk_source(),
            "decision": {"kind": "decision", "content": {"format": "ve-risk-decision@0"}},
            "entries": []}
    with pytest.raises(VEError, match="risk-decision.id"):
        run_case(case)
    record = case["decision"]["content"]
    record.update(id="17", chooser="agent", chooser_label="agent",
                  policy={"environment_id": "e", "document_hash": "d"},
                  alternatives=[{"name": "run", "label": "running"}], quantities=[], cites=[], facts=[])
    case["decision"].update(seq=4, day="2026-09-29", id="D17", prev="", hash="h")
    case["entries"] = [{"kind": "estimate", "id": "E1", "content": {}, "prev": "", "hash": "h"}]
    with pytest.raises(VEError, match="EstimateProvenance: E1 recorded"):
        run_case(case)
    case["entries"][0].update(seq=1, day="2026-09-29")
    with pytest.raises(CheckerUnavailable, match="Lean checker"):
        run_case(case)


def test_frozen_wordings_and_pending_sufficient_form():
    env = Environment(risk_source())
    actions = {"Running": "run", "Waiting": "wait"}
    harms = {"outage": "outage"}
    classes = {"severe": "severe"}
    parse = lambda s, context="guard": parse_wording(
        s, env, actions=actions, harms=harms, classes=classes, context=context)
    assert parse("Running might lead to outage.")["form"] == "might"
    assert parse("Running cannot lead to outage.")["form"] == "cannot"
    assert parse("Running leads to outage.")["form"] == "leads"
    assert parse("Running might not lead to outage.")["form"] == "might-not"
    assert parse("outage is severe.")["form"] == "class"
    assert parse("outage is severe or worse.")["form"] == "or-worse"
    assert parse("Waiting has a less severe worst case than Running.")["form"] == "less-worst"
    assert parse("Running cannot lead to outage unless memory is at most 5.", "record") == {
        "form": "necessary", "action": "run", "harm": "outage",
        "condition_text": "memory is at most 5"}
    assert parse("Running leads to outage exactly when memory exceeds 5.", "record")["form"] == "exact"
    for wording in ("Running may lead to outage.", "Running does not lead to outage.",
                    "Running leads to outage if memory exceeds 5.", "Running prevents outage."):
        with pytest.raises(VEError):
            parse(wording)
    for word in ("might", "cannot", "leads", "might-not", "class", "or-worse", "less-worst",
                 "necessary", "exact"):
        assert enabled(by_tag("risk-" + word), env)


def test_policy_english_uses_risk_readings():
    raw = risk_source()
    raw["vocabulary"]["constants"].update({
        "run": {"sort": "action", "description": "run"},
        "wait": {"sort": "action", "description": "wait"},
    })
    env = Environment(raw)
    readings = {
        "run might lead to outage.": "risk__might_lead_to",
        "run cannot lead to outage.": "risk__might_lead_to",
        "run might not lead to outage.": "leads_to",
        "outage is severe.": "risk__class",
        "outage is severe or worse.": "risk__or_worse",
        "wait has a less severe worst case than run.": "risk__less_worst",
        "run might prevent outage.": "prevents",
    }
    for sentence, predicate in readings.items():
        parsed = parse_english_with_metadata(env, sentence)
        assert predicate in str(parsed.document.formulas[0])
    for sentence, rewrite in (
        ("run does not lead to outage.", "Choose 'cannot lead to'"),
        ("run prevents outage.", "Use 'might prevent'"),
        ("run may lead to outage.", "Use 'might lead to'"),
        ("wait is safer than run.", "less severe worst case"),
    ):
        with pytest.raises(VEError, match=rewrite):
            parse_english_with_metadata(env, sentence)
