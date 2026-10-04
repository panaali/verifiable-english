"""Risk declaration identity, gates, and fail-closed dispatch."""
from copy import deepcopy
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT
from ve.environment import Environment
from ve.english import parse_english_with_metadata
from ve.norm_english import parse_english as parse_norm_english
from ve.errors import CheckerUnavailable, VEError
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.risk import run_case
from ve.surface.registry import by_tag, enabled
from ve.surface.risk import gap_lines, parse_wording


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


W6_FROZEN = ("UnsupportedProfile: ve-units@1 requires exactly order@0, relational-fol@0 and time@0, "
             "optionally with documents@1")


@pytest.mark.parametrize("profiles", [
    ["relational-fol@0"], ["order@0", "relational-fol@0"], ["relational-fol@0", "time@0"],
    ["documents@1", "relational-fol@0", "time@0"],
])
def test_w6_profile_diagnostic_is_unchanged_without_risk(profiles):
    """Review A1/B2: risk@0 adds a profile tuple only; the shared W6 text stays frozen."""
    raw = {"language": LANGUAGE, "profiles": profiles, "spec_revision": SPEC_REVISION,
           "vocabulary": {"sorts": {"item": {"description": "an item"}}, "constants": {},
                          "predicates": {"p": {"arguments": ["item"], "description": "p"}}},
           "unit_schema": "ve-units@1", "units": {}}
    with pytest.raises(VEError) as caught:
        Environment(raw)
    assert f"{type(caught.value).__name__}: {caught.value}" == W6_FROZEN
    root = Path(__file__).resolve().parents[1]
    text = W6_FROZEN.removeprefix("UnsupportedProfile: ")
    assert f'"UnsupportedProfile: {text}"' in (root / "lean/VE/Time/Wire.lean").read_text()
    [units] = root.glob("rust/*/src/units.rs")  # exactly one, whichever crate holds it
    assert f'"{text}"' in units.read_text()
    from ve.units import validate_extension
    with pytest.raises(VEError) as caught:
        validate_extension(profiles, {}, {}, {})
    assert f"{type(caught.value).__name__}: {caught.value}" == W6_FROZEN


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
    (lambda r: r["risk"]["severity"].update(classes=["avoidable"]), "AlternativesReserved: avoidable"),
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


def _decision_cases():
    """Malformed records whose first diagnostic Python used to decide (review A3, B1)."""
    base = {"format": "ve-risk-decision@0", "id": "17", "chooser": "agent", "chooser_label": "agent",
            "policy": {"environment_id": "e", "document_hash": "d"},
            "alternatives": [{"name": "run", "label": "running"}], "quantities": [], "cites": [], "facts": []}
    entry = {"seq": 4, "day": "2026-09-29", "id": "D17", "kind": "decision", "prev": "", "hash": "h"}
    unrecorded = {"kind": "estimate", "id": "E1", "content": {}, "prev": "", "hash": "h"}
    no_facts = {k: v for k, v in base.items() if k != "facts"}
    cases = {
        # A1: supplied entries decode (EstimateProvenance … recorded) before the record does
        "facts-missing-and-unrecorded": ({**entry, "content": no_facts}, [unrecorded]),
        # Lean's record decoder accepts empty strings; the answer is its next check
        "empty-id": ({**entry, "content": {**base, "id": "", "chooser_label": ""}}, []),
        "empty-alternative-label": ({**entry, "content": {**base, "alternatives": [{"name": "run", "label": ""}]}}, []),
        # one text per field: Lean's `InvalidInput: risk-decision.record`, not `.fields`
        "extra-field": ({**entry, "content": {**base, "note": "x"}}, []),
        "cite-seq-type": ({**entry, "content": {**base, "cites": [{"id": "E1", "seq": "1", "hash": "h"}]}}, []),
    }
    from conformance.risk import entry_hash
    for decision, _ in cases.values():
        decision["hash"] = entry_hash(decision)
    return {name: {"id": name, "kind": "risk-decision", "environment": risk_source(),
                   "document": {"norms": []}, "decision": decision, "entries": entries}
            for name, (decision, entries) in cases.items()}


def test_python_authority_gives_no_record_verdict(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    for case in _decision_cases().values():
        with pytest.raises(CheckerUnavailable, match="Lean checker"):
            run_case(case)
    with pytest.raises(VEError, match="risk route case"):
        run_case({"id": "x", "kind": [], "environment": {}})


@pytest.mark.skipif(not (Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_risk_route").exists(),
                    reason="ve_risk_route is not built")
def test_record_diagnostics_are_the_routes():
    """risk.md 6: record diagnostics come from the Lean route; Python only dispatches."""
    import json
    import subprocess
    binary = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_risk_route"
    cases = _decision_cases()
    direct = json.loads(subprocess.run([str(binary), "-"], input=json.dumps(list(cases.values())), text=True,
                                       capture_output=True, timeout=HANG_TIMEOUT).stdout)
    for (name, case), expected in zip(cases.items(), direct):
        assert run_case(case) == expected, name
    errors = {name: row["error"] for name, row in zip(cases, direct)}
    assert errors["facts-missing-and-unrecorded"] == "EstimateProvenance: E1 recorded"
    assert errors["extra-field"] == "InvalidInput: risk-decision.record"
    assert errors["cite-seq-type"] == "InvalidInput: risk-decision.cites"
    # the empty strings decode; binding to the loaded policy is the first failure
    assert errors["empty-id"] == errors["empty-alternative-label"] == "RiskBinding: policy"


def test_frozen_wordings_and_sufficient_form():
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
    assert parse("If memory exceeds 5, Running leads to outage.", "record") == {
        "form": "sufficient", "action": "run", "harm": "outage", "condition_text": "memory exceeds 5"}
    for wording in ("Running may lead to outage.", "Running does not lead to outage.",
                    "Running leads to outage if memory exceeds 5.", "Running prevents outage.",
                    "Running might not lead to outage."):
        with pytest.raises(VEError):
            parse(wording, "record" if "might not" in wording else "guard")
    for word in ("might", "cannot", "leads", "might-not", "class", "or-worse", "less-worst",
                 "necessary", "exact", "sufficient"):
        assert enabled(by_tag("risk-" + word), env)


def test_policy_english_uses_risk_readings():
    raw = risk_source()
    raw["vocabulary"]["constants"].update({
        "run": {"sort": "action", "description": "run"},
        "wait": {"sort": "action", "description": "wait"},
    })
    env = Environment(raw)
    from ve.ast import Binary, Const, Not
    atom = lambda p, x, y: Binary(p, Const(x), Const(y))
    readings = {
        "run might lead to outage.": atom("risk__might_lead_to", "run", "outage"),
        "run cannot lead to outage.": Not(atom("risk__might_lead_to", "run", "outage")),
        "run leads to outage.": atom("leads_to", "run", "outage"),
        "run might not lead to outage.": Not(atom("leads_to", "run", "outage")),
        "outage is severe.": atom("risk__class", "outage", "severe"),
        "outage is severe or worse.": atom("risk__or_worse", "outage", "severe"),
        "wait has a less severe worst case than run.": atom("risk__less_worst", "wait", "run"),
        "run might prevent outage.": atom("prevents", "run", "outage"),
    }
    for sentence, formula in readings.items():
        # the whole formula, so "cannot" (¬might) and "might" are told apart (review B8)
        assert parse_english_with_metadata(env, sentence).document.formulas == (formula,)
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
    guard = parse_norm_english(env, text).rules[0].guard
    from ve.ast import formula_to_data, Forall
    assert formula_to_data(env, Forall("action", guard)) == ["forall", "action", [
        "exists", "harm", ["and", ["binary", "risk__class", ["var", 0], ["const", "severe"]],
                           ["binary", "risk__might_lead_to", ["var", 1], ["var", 0]]]]]


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
