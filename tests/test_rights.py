"""Rights holder-side elaboration regressions."""
from __future__ import annotations

import pytest
import json

from tests.test_norms import environment, obligation, permission
from ve.document import check_document, load_document, render_document
from ve.soft_route import elaborate_soft_document
from ve.softnorms import SoftEnvironment
from ve.background import background
from ve.model import FiniteModel
from ve.surface.rights import parse_line, render_line, render_unit
from ve.errors import VEError
from ve.rights import RightsEnvironment, correlate
from ve.readings import plan_choices, rights_meaning_id, validate_couplings, validate_reading_sets


def rights_env():
    raw = environment({
        "protect_required": obligation("deny", "protect_permitted",
                                        act="{0} protect {1}", args=("state", "person")),
        "protect_permitted": permission("allow", act="{0} protect {1}",
                                         args=("state", "person")),
        "person_may_act": permission("allow", act="{0} act", args=("person",)),
    }, sorts=("state", "person")).to_dict()
    raw["profiles"] = sorted({"relational-fol@0", "norms@0", "soft-norms@0", "rights@0"})
    raw["vocabulary"]["rights"] = {"holders": ["person"], "bearers": ["state"],
                                    "protected": [], "alters": {}}
    return raw


def claim(name="protect"):
    return {"kind": "claim", "holder_slot": None, "cites": {},
            "norm": {"name": name, "predicate": "protect_required", "sign": True,
                     "guard": ["top"], "unless": [], "over": []}}


def right(lines=None, guard=None):
    return {"right": {"name": "life", "holder": "person", "guard": guard or ["top"],
                      "lines": [claim()] if lines is None else lines}}


def test_profile_and_identity_bound_rights_block():
    raw = rights_env()
    env = RightsEnvironment(raw)
    assert env.to_dict() == raw
    changed = rights_env()
    changed["vocabulary"]["rights"]["bearers"].append("person")
    assert RightsEnvironment(changed).environment_id != env.environment_id
    raw["profiles"].remove("soft-norms@0")
    with pytest.raises(VEError, match="rights@0 requires soft-norms@0"):
        RightsEnvironment(raw)


def test_claim_is_one_soft_rule_and_limitation_is_one_pack():
    units = [right(), {"limitation": {"name": "l29", "scope": "all", "kinds": ["claim"],
                                    "decided_by": "unstated", "conditions": [
                                        {"name": "law", "role": "necessary", "decided_by": None,
                                         "verbalisation": "determined by law"}], "factors": []}}]
    doc = correlate(rights_env(), units)
    assert [rule.core.name for rule in doc.soft_document.rules] == ["protect"]
    assert doc.limitation_names == {("l29", "protect_permitted"): "rights__lim__1"}
    assert doc.condition_names == {("l29", "protect_permitted", "law"): "rights__cond__1"}
    assert len(doc.soft_document.rules[0].core.unless) == 1
    assert [label for label, _ in doc.limitation_premises] == [
        "rights:limitation:l29:protect_permitted:necessary:law"]
    assert sum(p.generator == "rights" for p in background(doc.soft_document.extended_env)) == 1
    extended = doc.soft_document.extended_env
    model = {"complete": True, "domains": {"state": ["s"], "person": ["p"]},
             "constants": {}, "relations": {name: [] for name in extended.predicates}}
    model["relations"]["rights__lim__1"] = [["s", "p"]]
    with pytest.raises(VEError, match="rights premise"):
        FiniteModel.from_dict(extended, model)


def test_right_requires_incident_and_claim_shape():
    with pytest.raises(VEError, match="RightWithoutIncident: life"):
        correlate(rights_env(), [right([])])
    invalid = claim()
    invalid["norm"]["predicate"] = "person_may_act"
    with pytest.raises(VEError, match="IncidentShape"):
        correlate(rights_env(), [right([invalid])])


def test_document_check_uses_correlated_soft_route(tmp_path):
    source = "Every person has a right to protection.\n"
    meta = {"format": "ve-document@1", "environment": rights_env(),
            "units": [{"id": "u1", "span": [0, len(source)], "kind": "right",
                       "meaning": "specified", "support": "none", "content": right()}]}
    path = tmp_path / "rights.ve.md"
    path.write_text("---\n" + json.dumps(meta) + "\n---\n" + source)
    result = check_document(path)
    assert result["rights"]["environment_id"]
    report = result["rights"]["report"]
    assert report["conflict"]["verdict"] in ("UNKNOWN", "CONFLICT-FREE")
    assert report["unlicensed_limitations"] == []
    assert report["distinction"][0]["independent"] is True
    assert report["bar"] == []
    assert result["soft"]["soft_document_hash"]
    assert "Claim of right life" in render_document(path)
    assert load_document(path)["units"][0]["meaning_id"]


def test_rule_bar_elaborates_over_right_liberty():
    liberty = {"kind": "liberty", "holder_slot": None, "cites": {},
               "norm": {"name": "may-act", "predicate": "person_may_act", "sign": True,
                        "guard": ["top"], "unless": [], "over": []}}
    doc = correlate(rights_env(), [right([liberty]),
                                   {"bar": {"name": "b30", "reading": "rule",
                                            "decided_by": "unstated"}}])
    assert doc.bar_names == {"person_may_act": "rights__bar__1"}
    assert [r.core.name for r in doc.soft_document.rules] == ["may-act", "rights-bar-1"]
    assert doc.soft_document.rules[-1].core.over == ("may-act",)
    assert elaborate_soft_document(doc.soft_document)["status"] == "ok"


def test_liberty_without_bar_does_not_declare_aimed_vocabulary():
    liberty = {"kind": "liberty", "holder_slot": None, "cites": {},
               "norm": {"name": "may-act", "predicate": "person_may_act", "sign": True,
                        "guard": ["top"], "unless": [], "over": []}}
    doc = correlate(rights_env(), [right([liberty])])
    assert doc.bar_names == {}
    assert not any(name.startswith("rights__bar__") for name in doc.environment.predicates)


def test_document_rejects_citation_to_nonexistent_source_unit(tmp_path):
    source = "Right.\nLimitation.\n"
    line = claim()
    line["norm"].update(mode="default", exception={"decided_by": "unstated",
                         "sufficient": [], "necessary": [], "factors": []})
    line["cites"] = {"exception": ["nonexistent-source-unit"]}
    units = [right([line]), {"limitation": {
        "name": "l29", "scope": "all", "kinds": ["claim"], "decided_by": "unstated",
        "conditions": [], "factors": []}}]
    meta = {"format": "ve-document@1", "environment": rights_env(), "units": [
        {"id": "u1", "span": [0, 7], "kind": "right", "meaning": "specified",
         "support": "none", "content": units[0]},
        {"id": "u2", "span": [7, len(source)], "kind": "limitation", "meaning": "specified",
         "support": "none", "content": units[1]}]}
    path = tmp_path / "citation.ve.md"
    path.write_text("---\n" + json.dumps(meta) + "\n---\n" + source)
    with pytest.raises(VEError, match="citation target is not a source unit"):
        load_document(path)
    meta["units"][0]["content"]["right"]["lines"][0]["cites"]["exception"] = ["u2"]
    path.write_text("---\n" + json.dumps(meta) + "\n---\n" + source)
    doc = load_document(path)
    assert doc["units"][0]["status"] == "OPEN"
    assert doc["units"][1]["status"] == "OPEN"
    assert doc["rights_document"].instances[0]["cites"]["exception"] == ["u2"]
    meta["units"][0]["content"]["right"]["lines"][0]["cites"] = {}
    path.write_text("---\n" + json.dumps(meta) + "\n---\n" + source)
    result = check_document(path)
    assert result["coverage"]["bytes_by_status"] == {"OPEN": len(source)}
    assert any("exception" in finding for finding in
               result["rights"]["report"]["unlicensed_limitations"])


def test_rights_english_preserves_default_holder_guard_and_generated_conditions():
    raw = rights_env()
    raw["vocabulary"]["predicates"]["adult"] = {"arguments": ["person"],
                                                   "description": "adult"}
    line = claim()
    line["norm"].update(mode="default", exception={"decided_by": "unstated",
                         "sufficient": [], "necessary": [], "factors": []},
                        guard=["binary", "rights__cond__1", ["var", 1], ["var", 0]])
    units = [right([line], guard=["unary", "adult", ["var", 0]]),
             {"limitation": {"name": "l29", "scope": "all", "kinds": ["claim"],
                             "decided_by": "unstated", "conditions": [
                                 {"name": "law", "role": "necessary", "decided_by": None,
                                  "verbalisation": "determined by law"}], "factors": []}}]
    document = correlate(raw, units)
    text = render_unit(document, units[0])
    assert "should protect" in text
    assert "must protect" not in text
    assert "adult" in text and "rights__cond__1" in text and "rights__lim__1" in text
    assert "claim lines" in render_unit(document, units[1])


def test_reporting_rejects_swapped_lean_lines_even_when_names_match(monkeypatch):
    from ve import rights_route
    raw = rights_env()
    first = right([claim("first")])
    second_line = claim("second")
    second_line["norm"]["guard"] = ["not", ["top"]]
    later = {"right_lines": {"right": "life", "lines": [second_line]}}
    units = [first, later]
    rights = correlate(raw, units)
    original = rights_route.run_rights_case

    def swapped(environment, source, kind, **extra):
        row = original(environment, source, kind, **extra)
        if kind == "rights-elaborate":
            row["lines"][0]["node"], row["lines"][1]["node"] = (
                row["lines"][1]["node"], row["lines"][0]["node"])
        return row

    monkeypatch.setattr(rights_route, "run_rights_case", swapped)
    with pytest.raises(VEError, match="regeneration mismatch: lines"):
        rights_route.report_rights(rights.env, units, rights)


def test_document_graph_admits_exact_regenerated_rights_layer(tmp_path):
    from ve.rights_route import run_rights_case
    raw = rights_env()
    unit = right()
    rights = correlate(raw, [unit])
    row = run_rights_case(rights.env, [unit], "rights-elaborate")
    premise = next(p for p in row["premises"]
                   if p["label"] == "layer:norms:protect_required")
    source = "Right.\n"
    meta = {"format": "ve-document@1", "environment": raw,
            "units": [{"id": "u1", "span": [0, len(source)], "kind": "right",
                       "meaning": "specified", "support": "none", "content": unit}],
            "graph": {"root": "leaf", "nodes": [
                {"name": "leaf", "ast": premise["ast"], "label": premise["label"]}]}}
    path = tmp_path / "admission.ve.md"
    path.write_text("---\n" + json.dumps(meta) + "\n---\n" + source)
    result = check_document(path)
    assert result["admission"]["admitted"] is True
    assert result["admission"]["report"]["assumptions"][0]["label"] == premise["label"]


def test_couplings_keep_only_shared_axis_choices():
    sets = [{"id": name, "version": 1, "unit": name, "status": "open",
             "readings": [{"id": f"{name}-{value}", "labels": {"force": value}}
                          for value in ("strict", "default")]}
            for name in ("a", "b")]
    couplings = [{"id": "same-force", "axis": "force",
                  "sets": [{"set": name, "version": 1} for name in ("a", "b")],
                  "by": "translator", "reason_spans": ["preamble"]}]
    validate_couplings(RightsEnvironment(rights_env()), couplings, sets,
                       {"a", "b", "preamble"})
    plan = plan_choices(sets, couplings=couplings)
    assert plan["route"] == "enumerate"
    assert plan["choices"] == [{"a": 0, "b": 0}, {"a": 1, "b": 1}]
    assert plan["conditional_on"] == ["coupling:same-force"]
    sets[1]["readings"] = [sets[1]["readings"][0]]
    assert plan_choices(sets, couplings=couplings)["choices"] == [{"a": 0, "b": 0}]
    sets[1]["readings"] = [{"id": "b-other", "labels": {"force": "other"}}]
    with pytest.raises(VEError, match="CouplingLabelMissing"):
        validate_couplings(RightsEnvironment(rights_env()), couplings, sets,
                           {"a", "b", "preamble"})


def test_right_readings_need_a_checked_separating_situation():
    from ve.readings import _right_situation
    raw = rights_env()
    raw["vocabulary"]["predicates"]["q"] = {"arguments": ["state", "person"], "description": "q"}
    env = RightsEnvironment(raw)
    positive = right()
    positive["right"]["lines"][0]["norm"]["guard"] = ["binary", "q", ["var", 1], ["var", 0]]
    negative = right()
    negative["right"]["lines"][0]["norm"]["guard"] = ["not", positive["right"]["lines"][0]["norm"]["guard"]]
    situation = {"complete": True, "domains": {"state": ["s"], "person": ["p"]},
                 "constants": {}, "relations": {"q": [["s", "p"]]}}
    model_id = _right_situation(env, positive, situation)[0]
    choices = [positive, negative]
    readings = [{"id": str(i), "kind": "right", "content": content,
                 "meaning_id": rights_meaning_id(env, content),
                 "admission": {"who": "translator", "why": "the source leaves the guard open",
                               "distinguishing_models": {str(1 - i): model_id}}}
                for i, content in enumerate(choices)]
    reading_set = {"id": "r", "unit": "u", "version": 1, "status": "open",
                   "readings": readings, "models": {model_id: situation}}
    validate_reading_sets(env, [reading_set], {"u"})
    reading_set["readings"][1]["content"] = positive
    reading_set["readings"][1]["meaning_id"] = rights_meaning_id(env, positive)
    with pytest.raises(VEError, match="does not separate"):
        validate_reading_sets(env, [reading_set], {"u"})


def test_fan_out_generates_one_rule_per_bearer_sort():
    raw = rights_env()
    raw["vocabulary"]["rights"]["bearers"] = ["state", "person"]
    raw["vocabulary"]["predicates"]["person_protect_permitted"] = permission(
        "allow", act="{0} protect {1}", args=("person", "person"))
    fan = {"kind": "claim", "cites": {}, "holder_slot": 1,
           "fan_out": {"state": "protect_permitted", "person": "person_protect_permitted"},
           "norm": {"name": "no-protect", "predicate": None, "sign": False,
                    "guard": ["top"], "unless": [], "over": []}}
    doc = correlate(raw, [right([fan])])
    assert [(i["bearer"], i["rule"].core.name) for i in doc.instances] == [
        ("person", "rights-fan-1"), ("state", "rights-fan-2")]
    assert elaborate_soft_document(doc.soft_document)["status"] == "ok"


def test_joint_couplings_reject_empty_complete_choice_space():
    sets = [{"id": "a", "version": 1, "unit": "a", "readings": [
        {"labels": {"force": "strict", "polarity": "positive"}},
        {"labels": {"force": "default", "polarity": "negative"}}]},
        {"id": "b", "version": 1, "unit": "b", "readings": [
            {"labels": {"force": "strict", "polarity": "negative"}},
            {"labels": {"force": "default", "polarity": "positive"}}]}]
    couplings = [{"id": axis, "axis": axis,
                  "sets": [{"set": name, "version": 1} for name in ("a", "b")],
                  "by": "translator", "reason_spans": ["preamble"]}
                 for axis in ("force", "polarity")]
    with pytest.raises(VEError, match="CouplingUnsatisfiable"):
        validate_couplings(RightsEnvironment(rights_env()), couplings, sets,
                           {"a", "b", "preamble"})


def test_power_splits_into_liberty_and_recognition():
    raw = rights_env()
    predicates = raw["vocabulary"]["predicates"]
    predicates["marry_permitted"] = permission("allow", act="{0} marry", args=("person",))
    predicates["recognise_required"] = obligation(
        "deny", None, act="{0} recognise {1}", args=("state", "person"))
    predicates["married"] = {"arguments": ["person"], "description": "married"}
    raw["vocabulary"]["rights"]["alters"] = {
        "marry_permitted": {"holder_slot": 0, "status": "married",
                            "recognition": "recognise_required"}}
    power = {"kind": "power", "cites": {},
             "liberty": {"name": "may-marry", "predicate": "marry_permitted", "sign": True,
                         "guard": ["top"], "unless": [], "over": []},
             "recognition": {"name": "recognise-marriage", "predicate": "recognise_required",
                             "sign": True, "guard": ["top"], "unless": [], "over": []}}
    doc = correlate(raw, [right([power])])
    assert [i["kind"] for i in doc.instances] == ["powerLiberty", "powerRecognition"]
    assert [r.core.name for r in doc.soft_document.rules] == ["may-marry", "recognise-marriage"]
    assert elaborate_soft_document(doc.soft_document)["status"] == "ok"


def test_rights_soft_regeneration_conformance():
    from conformance.rights import run
    assert run(8) == 8


def test_incident_english_has_one_soft_rule_reading():
    env = RightsEnvironment(rights_env())
    source = render_line(env, "life", "claim", claim()["norm"])
    assert source == "Claim of right life. Every state must protect each person."
    parsed = parse_line(env, source, name="protect")
    assert parsed["right"] == "life"
    assert parsed["norm"] == claim()["norm"]
    default = claim("protect-default")["norm"]
    default.update({"mode": "default", "exception": {
        "decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}})
    soft_source = render_line(env, "life", "claim", default)
    assert "should protect" in soft_source
    assert parse_line(env, soft_source, name="protect-default")["norm"] == default
    with pytest.raises(VEError, match="rights@0 is required"):
        render_line(SoftEnvironment(rights_env_without_profile()), "life", "claim", claim()["norm"])


def rights_env_without_profile():
    raw = rights_env()
    raw["profiles"].remove("rights@0")
    raw["vocabulary"].pop("rights")
    return raw
