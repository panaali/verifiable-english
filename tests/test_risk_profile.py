"""Risk declaration identity, gates, and fail-closed dispatch."""
from copy import deepcopy

import pytest

from ve.environment import Environment
from ve.english import parse_english_with_metadata
from ve.norm_english import parse_english as parse_norm_english
from ve.errors import CheckerUnavailable, VEError
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.risk import run_case
from ve.surface.registry import by_tag, enabled
from ve.surface.risk import gap_lines, legend_lines, parse_wording


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
    raw["unit_schema"] = "ve-units@1"
    raw["units"] = {"gb": {"scale": "10", "display": {"kind": "decimal", "label": "GB"}}}
    raw["risk"]["quantity_kinds"] = {"memory": "gb"}
    env = Environment(raw)
    assert env.to_dict() == raw


def test_risk_quantity_environment_rejects_order_checker():
    raw = risk_source()
    raw["profiles"] += ["order@0", "time@0"]
    raw["profiles"].sort()
    raw["unit_schema"] = "ve-units@1"
    raw["units"] = {"gb": {"scale": "10", "display": {"kind": "decimal", "label": "GB"}}}
    with pytest.raises(VEError, match="risk norms route admits FOL documents only"):
        Environment(raw)


@pytest.mark.parametrize("edit,diagnostic", [
    (lambda r: r["risk"].update(bands=[]), "stage B or C not enabled"),
    (lambda r: r["risk"].update(unknown=True), "InvalidInput: risk.unknown"),
    (lambda r: r["risk"]["severity"].update(sort="harm"), "RiskSeverityNotFresh"),
    (lambda r: r["risk"]["severity"].update(classes=["minor", "minor"]), "risk class minor"),
    (lambda r: r["risk"]["severity"].update(classes=["avoidable"]), "RiskReserved"),
    (lambda r: r["risk"]["severity"].update(more_severe=[["severe", "minor"], ["minor", "severe"]]), "DependencyCycle"),
    (lambda r: r["risk"]["severity"].update(unranked=[["minor", "severe"]]), "RiskUnrankedAgainstOrder"),
    (lambda r: r["risk"].update(harm_classes=[]), "HarmUnclassified"),
    (lambda r: r["vocabulary"]["predicates"].update(alias={"arguments": ["action", "harm"],
                                                          "description": "alias",
                                                          "verbalisation": "{0} might lead to {1}"}),
     "RiskReserved: wording"),
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
    case["kind"] = []
    with pytest.raises(VEError, match="risk route case"):
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
                    "Running leads to outage if memory exceeds 5.", "Running prevents outage.",
                    "Running might not lead to outage."):
        with pytest.raises(VEError):
            parse(wording, "record" if "might not" in wording else "guard")
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
        ("run certainly leads to outage.", "Use 'leads to'"),
        ("run could lead to outage.", "Use 'might lead to'"),
    ):
        with pytest.raises(VEError, match=rewrite):
            parse_english_with_metadata(env, sentence)


def test_risk_word_in_norm_guard_has_one_reading():
    raw = risk_source()
    raw["vocabulary"]["predicates"]["permitted"] = {
        "arguments": ["action"], "description": "permission",
        "regulated": {"role": "permission", "default": "deny", "act": "{0} be done"},
    }
    env = Environment(raw)
    text = ("Rule 1. Every action may be done, if there is a harm such that both "
            "that harm is severe and that action might lead to that harm.")
    document = parse_norm_english(env, text)
    assert document.document_hash


def test_legend_tracks_declared_order_and_pending_condition():
    env = Environment(risk_source())
    lines = legend_lines(env, used_words=("risk__less_worst", "avoidable"),
                         condition_forms=("necessary", "sufficient"))
    assert lines[0].startswith('"<action> might lead to <harm>"')
    assert any("Severity, from most to least severe: severe, minor" in line for line in lines)
    assert any(line == "outage is severe." for line in lines)
    assert any("(wording pending)" in line for line in lines)
    assert any("might not lead to the harm" in line for line in lines)


def test_gap_renderer_keeps_distinct_report_categories():
    lines = gap_lines({
        "unexamined_possible": [{"action": "run", "harm": "outage"}],
        "assumed_ruled_out": [{"action": "wait", "harm": "outage", "decider": "team"}],
        "unranked_severities": [{"left": "serious", "right": "minor"}],
        "point_estimates": [{"id": "E1", "result": "run cannot lead to outage"}],
        "default_decided": ["wait"],
        "dilemmas": ["no clear action"],
    })
    assert lines == (
        "Unexamined possible: run might lead to outage.",
        "Assumed ruled out by team: wait cannot lead to outage.",
        "Unranked severities: serious and minor are not ranked.",
        "Point estimate E1: run cannot lead to outage.",
        "Default decided: wait.",
        "Dilemma: no clear action.",
    )
