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


def rights_document_file(tmp_path, contents, *, meanings=None, statuses=None, env=None):
    source = "".join(f"Unit {index}.\n" for index in range(len(contents)))
    units = []
    start = 0
    for index, content in enumerate(contents):
        end = start + len(f"Unit {index}.\n")
        units.append({"id": f"u{index}", "span": [start, end], "kind": next(iter(content)),
                      "meaning": (meanings or {}).get(index, "specified"), "support": "none",
                      "content": content,
                      **({"status": statuses[index]} if statuses and index in statuses else {})})
        start = end
    path = tmp_path / "rights.ve.md"
    path.write_text("---\n" + json.dumps({"format": "ve-document@1",
                                          "environment": env or rights_env(),
                                          "units": units}) + "\n---\n" + source)
    return path


def life_limitation():
    return {"limitation": {"name": "l29", "scope": ["life"], "kinds": ["claim"],
                           "decided_by": "unstated", "conditions": [
                               {"name": "law", "role": "necessary", "decided_by": None,
                                "verbalisation": "determined by law"}], "factors": []}}


def test_generated_condition_opens_unscoped_right_and_accepts_open_meaning(tmp_path):
    health = right([claim("health-protect")])
    health["right"]["name"] = "health"
    health["right"]["lines"][0]["norm"]["guard"] = [
        "binary", "rights__cond__1", ["var", 1], ["var", 0]]
    contents = [right(), health, life_limitation()]
    path = rights_document_file(tmp_path, contents)
    doc = load_document(path)
    assert [u["status"] for u in doc["units"]] == ["OPEN", "OPEN", "OPEN"]
    path = rights_document_file(tmp_path, contents,
                                meanings={1: {"open": ["rights__cond__1"]}},
                                statuses={1: "OPEN"})
    assert load_document(path)["units"][1]["status"] == "OPEN"
    path = rights_document_file(tmp_path, contents,
                                meanings={1: {"open": ["rights__cond__2"]}})
    with pytest.raises(VEError, match="invalid meaning status"):
        load_document(path)


@pytest.mark.parametrize("generated", ["rights__lim__1", "rights__cond__1"])
def test_generated_limitation_names_open_outside_norms(tmp_path, generated):
    outside = {"norm": {"name": "outside", "predicate": "protect_required", "sign": True,
                        "guard": ["binary", generated, ["var", 1], ["var", 0]],
                        "unless": [], "over": []}}
    path = rights_document_file(tmp_path, [right(), life_limitation(), outside],
                                statuses={2: "OPEN"})
    assert load_document(path)["units"][2]["status"] == "OPEN"


def test_generated_bar_name_opens_outside_norm(tmp_path):
    liberty = {"kind": "liberty", "holder_slot": None, "cites": {},
               "norm": {"name": "may-act", "predicate": "person_may_act", "sign": True,
                        "guard": ["top"], "unless": [], "over": []}}
    bar = {"bar": {"name": "b30", "reading": "rule", "decided_by": "unstated"}}
    outside = {"norm": {"name": "outside", "predicate": "person_may_act", "sign": True,
                        "guard": ["unary", "rights__bar__1", ["var", 0]],
                        "unless": [], "over": []}}
    path = rights_document_file(tmp_path, [right([liberty]), bar, outside],
                                meanings={2: {"open": ["rights__bar__1"]}},
                                statuses={2: "OPEN"})
    assert [u["status"] for u in load_document(path)["units"]] == ["OPEN", "OPEN", "OPEN"]


def test_holder_guard_opens_correlated_incident(tmp_path):
    raw = rights_env()
    raw["vocabulary"]["predicates"]["eligibility"] = {
        "arguments": ["person"], "description": "eligibility"}
    guarded = right(guard=["unary", "eligibility", ["var", 0]])
    # A declared open term in the right's guard was absent from the source line.
    # Keep the declaration in document metadata, as required by the W2 contract.
    path = rights_document_file(tmp_path, [guarded], env=raw)
    meta, source = path.read_text().split("\n---\n", 1)
    metadata = json.loads(meta.removeprefix("---\n"))
    metadata["open_terms"] = [{"name": "eligibility", "arguments": ["person"],
                                "decided_by": "author", "necessary": [], "sufficient": [],
                                "factors": [], "precedents": [], "jurisdiction": "general",
                                "version": 1}]
    path.write_text("---\n" + json.dumps(metadata) + "\n---\n" + source)
    assert load_document(path)["units"][0]["status"] == "OPEN"


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


def test_phi_null_recognition_is_the_absent_field():
    # fixture phi: an alters entry with recognition null could not be built at all, since
    # canonical JSON has no null; it is the absent field, as on the Lean wire
    raw = rights_env()
    raw["vocabulary"]["predicates"]["deprive_permitted"] = permission(
        "allow", act="{0} deprive {1} of nationality", args=("state", "person"))
    raw["vocabulary"]["predicates"]["has_nationality"] = {"arguments": ["person"], "description": "n"}
    raw["vocabulary"]["rights"]["alters"] = {"deprive_permitted": {
        "holder_slot": 1, "status": "has_nationality", "recognition": None}}
    absent = json.loads(json.dumps(raw))
    del absent["vocabulary"]["rights"]["alters"]["deprive_permitted"]["recognition"]
    assert RightsEnvironment(raw).environment_id == RightsEnvironment(absent).environment_id
    immunity = {"kind": "immunity", "cites": {},
                "norm": {"name": "no-deprive", "predicate": "deprive_permitted", "sign": False,
                         "guard": ["top"], "unless": [], "over": []}}
    assert correlate(raw, [right([immunity])]).instances[0]["holder_slot"] == 1
    power = {"kind": "power", "cites": {},
             "liberty": {**immunity["norm"], "name": "may-deprive", "sign": True},
             "recognition": {**immunity["norm"], "name": "recognise", "sign": True}}
    with pytest.raises(VEError, match="IncidentShape"):
        correlate(raw, [right([power])])


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
    assert "Claim of right 1. Every state must protect each person." in render_document(path)
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
    with pytest.raises(VEError, match="UnknownSymbol: unit nonexistent-source-unit"):
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


def test_rights_coverage_counts_open_limitation_terms_and_findings(tmp_path):
    from ve.document import coverage
    # strict lines only, but a limitation's lim and cond terms are open: never soft CHECKED
    path = rights_document_file(tmp_path, [right(), life_limitation()])
    result = check_document(path)
    residual = result["coverage"]["residual"]
    assert residual["limitation_terms"] == 2
    assert result["coverage"]["soft_status"] == "OPEN"
    assert residual["unlicensed_limitations"] == 0 and residual["distinction_hits"] == 0
    # an uncited default exception under the limitation is a finding counted in the total
    line = claim()
    line["norm"].update(mode="default", exception={"decided_by": "unstated",
                         "sufficient": [], "necessary": [], "factors": []})
    path = rights_document_file(tmp_path, [right([line]), life_limitation()])
    result = check_document(path)
    residual = result["coverage"]["residual"]
    assert residual["unlicensed_limitations"] == 1
    assert result["coverage"]["residual_total"] == sum(residual.values())
    assert result["coverage"]["rights_report"]["unlicensed_limitations"] == [
        "UnlicensedLimitation: exception of rule protect on right life"]
    assert coverage(load_document(path))["residual"] == residual
    # a bar's aimed terms are open too
    liberty = {"kind": "liberty", "holder_slot": None, "cites": {},
               "norm": {"name": "may-act", "predicate": "person_may_act", "sign": True,
                        "guard": ["top"], "unless": [], "over": []}}
    bar = {"bar": {"name": "b30", "reading": "query", "decided_by": "unstated"}}
    covered = check_document(rights_document_file(tmp_path, [right([liberty]), bar]))["coverage"]
    assert covered["residual"]["bar_terms"] == 1 and covered["soft_status"] == "OPEN"
    # with no liberty there is no aimed term to count
    assert check_document(rights_document_file(tmp_path, [right(), bar]))["coverage"]["residual"]["bar_terms"] == 0


def test_citations_name_declared_source_units_on_lines_and_outside_norms():
    raw = rights_env()
    line = claim()
    line["cites"] = {"guard": ["u057"]}
    outside = {"norm": {"name": "may-protect", "predicate": "protect_permitted", "sign": True,
                        "guard": ["top"], "unless": [], "over": []},
               "cites": {"narrows:protect": ["u082"]}}
    source = [{"source_units": ["u057", "u082"]}, right([line]), outside]
    rights = correlate(raw, source)
    assert rights.instances[0]["cites"] == {"guard": ["u057"]}
    assert [rule.core.name for rule in rights.soft_document.rules] == ["protect", "may-protect"]
    # a citation to a unit the source does not have is rejected, never a licence
    with pytest.raises(VEError, match="UnknownSymbol: unit u082"):
        correlate(raw, [{"source_units": ["u057"]}, right([line]), outside])
    with pytest.raises(VEError, match="UnknownSymbol: unit u057"):
        correlate(raw, [right([line])])
    with pytest.raises(VEError, match="InvalidInput: cites guard must list unit ids"):
        correlate(raw, [{"source_units": []}, right([{**line, "cites": {"guard": []}}])])
    from ve.rights_route import report_rights
    assert report_rights(rights.env, source, rights)["unlicensed_limitations"] == []


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
    # the holder guard is in the header and in every line; generated predicates are worded,
    # never printed by name (2.1)
    assert "Every line of this right applies only where that person is adult." in text
    assert ("Claim of right 1. Every state should protect each person, if both determined by law "
            "where that state protects that person and that person is adult, unless limitation 1 "
            "holds where that state protects that person.") in text
    assert "rights__" not in text
    limitation = render_unit(document, units[1])
    assert limitation == (
        "Limitation 1 (on the claims of every right). A right in this document is limited in a "
        "situation only where limitation 1 holds. Limitation 1 holds only where determined by law. "
        "The source names no decider of limitation 1.")


def test_python_applies_the_lean_carve_out_and_count_limits():
    from ve.rights_route import run_rights_case
    raw = rights_env()
    raw["vocabulary"]["predicates"]["q"] = {"arguments": ["state", "person"], "description": "q"}
    env = RightsEnvironment(raw)
    seven = claim("seven")
    seven["norm"]["unless"] = [["binary", "q", ["var", 1], ["var", 0]]] * 7
    six = claim("six")
    six["norm"]["unless"] = [["binary", "q", ["var", 1], ["var", 0]]] * 6
    many_rights = [{"right": {"name": f"r{i}", "holder": "person", "guard": ["top"],
                              "lines": [claim(f"c{i}")]}} for i in range(129)]
    limit = life_limitation()["limitation"]
    many_limits = [right(), *({"limitation": {**limit, "name": f"l{i}"}} for i in range(17))]
    many_conditions = [right(), {"limitation": {**limit, "conditions": [
        {"name": f"c{i}", "role": "necessary", "decided_by": None, "verbalisation": "v"}
        for i in range(9)]}}]
    cases = [([right([seven])], "carve-outs of rule seven"),  # no limitation covers the line
             (many_rights, "rights"), (many_limits, "limitations"), (many_conditions, "conditions")]
    for units, message in cases:
        with pytest.raises(VEError, match=message):
            correlate(raw, units)
        with pytest.raises(VEError, match=f"ResourceLimit: {message}"):
            run_rights_case(env, units, "rights-elaborate")
    correlate(raw, [right([six])])
    assert run_rights_case(env, [right([six])], "rights-elaborate")["lines"]


def test_generated_declarations_are_the_same_bytes_in_python_and_lean(monkeypatch):
    from ve import rights_route
    raw = rights_env()
    liberty = {"kind": "liberty", "holder_slot": None, "cites": {},
               "norm": {"name": "may-act", "predicate": "person_may_act", "sign": True,
                        "guard": ["top"], "unless": [], "over": []}}
    units = [right([claim(), liberty]), life_limitation(),
             {"bar": {"name": "b30", "reading": "rule", "decided_by": "unstated"}}]
    rights = correlate(raw, units)
    row = rights_route.run_rights_case(rights.env, units, "rights-elaborate")
    predicates = row["environment_prime"]["vocabulary"]["predicates"]
    assert predicates["rights__lim__1"] == {
        "arguments": ["state", "person"], "description": "limitation l29 of protect_permitted",
        "verbalisation": "limitation 1 holds where {0} protect {1}"}
    assert predicates["rights__cond__1"]["verbalisation"] == "determined by law where {0} protect {1}"
    assert predicates["rights__bar__1"]["verbalisation"] == "{0} act aimed at the destruction of a right"
    assert row["environment_prime"] == rights_route.expected_environment_prime(rights)
    rights_route.report_rights(rights.env, units, rights)
    original = rights_route.run_rights_case

    def drifted(environment, source, kind, **extra):
        result = original(environment, source, kind, **extra)
        if kind == "rights-elaborate":
            generated = result["environment_prime"]["vocabulary"]["predicates"]["rights__lim__1"]
            generated["description"] = "rights-generated open predicate"
        return result

    monkeypatch.setattr(rights_route, "run_rights_case", drifted)
    with pytest.raises(VEError, match="regeneration mismatch: environment"):
        rights_route.report_rights(rights.env, units, rights)


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


def test_fan_out_source_name_is_an_author_rule_name():
    # found by the differential: Python renamed fan-out instances without checking the source
    # line's own name, which Lean rejects when reserved or duplicated (1.6)
    raw = rights_env()
    raw["vocabulary"]["rights"]["bearers"] = ["state", "person"]
    raw["vocabulary"]["predicates"]["person_protect_permitted"] = permission(
        "allow", act="{0} protect {1}", args=("person", "person"))
    fan = {"kind": "claim", "cites": {}, "holder_slot": 1,
           "fan_out": {"state": "protect_permitted", "person": "person_protect_permitted"},
           "norm": {"name": "rights-x", "predicate": None, "sign": False,
                    "guard": ["top"], "unless": [], "over": []}}
    with pytest.raises(VEError, match="name rights-x begins with rights-"):
        correlate(raw, [right([fan])])
    fan["norm"]["name"] = "protect"
    with pytest.raises(VEError, match="rule protect"):
        correlate(raw, [right([claim("protect"), fan])])


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


def test_at_most_eight_couplings():
    sets = [{"id": name, "version": 1, "unit": name, "status": "open",
             "readings": [{"id": f"{name}-{value}", "labels": {"force": value}}
                          for value in ("strict", "default")]}
            for name in ("a", "b")]
    couplings = [{"id": f"c{i}", "axis": "force",
                  "sets": [{"set": name, "version": 1} for name in ("a", "b")],
                  "by": "translator", "reason_spans": ["preamble"]} for i in range(9)]
    env = RightsEnvironment(rights_env())
    with pytest.raises(VEError, match="ResourceLimit: couplings"):
        validate_couplings(env, couplings, sets, {"a", "b", "preamble"})
    validate_couplings(env, couplings[:8], sets, {"a", "b", "preamble"})


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


def _labelled_sets(contents):
    return [{"id": name, "version": 1, "unit": f"u-{name}", "status": "open",
             "readings": [{"id": f"{name}-{i}", "kind": "asserted", "content": content,
                           "labels": {"force": force}, "original_index": i}
                          for i, (force, content) in enumerate(pairs)]}
            for name, pairs in contents.items()]


FORCE = [{"id": "same-force", "axis": "force",
          "sets": [{"set": "a", "version": 1}, {"set": "b", "version": 1}],
          "by": "translator", "reason_spans": ["preamble"]}]


def test_coupled_readings_never_turn_zero_choices_into_all():
    from tests.test_document import VOCAB, envelope
    from ve.environment import Environment
    from ve.readings import check_readings
    env = Environment(envelope(VOCAB))
    p = ["unary", "senior", ["const", "alice"]]
    # a narrowing that keeps a strict candidate of a and a default one of b leaves no
    # coupled choice; before, zero choices of which zero failed were reported ALL
    narrowed = _labelled_sets({"a": [("strict", p)], "b": [("default", p)]})
    with pytest.raises(VEError, match="CouplingUnsatisfiable: same-force"):
        check_readings(env, narrowed, ["top"], couplings=FORCE)
    with pytest.raises(VEError, match="CouplingUnsatisfiable: same-force"):
        plan_choices(narrowed, couplings=FORCE)


def test_coupled_positive_choices_carry_their_premise_status():
    from tests.test_document import VOCAB, envelope
    from ve.environment import Environment
    from ve.readings import check_readings
    env = Environment(envelope(VOCAB))
    p = ["unary", "senior", ["const", "alice"]]
    sets = _labelled_sets({"a": [("strict", p), ("default", ["top"])],
                           "b": [("strict", ["not", p]), ("default", ["top"])]})
    result = check_readings(env, sets, ["bottom"], couplings=FORCE)
    # the only choice that proves the conclusion is inconsistent: shown vacuous, not as support
    assert result["verdict"] == "SOME"
    positive = [row for row in result["choices"] if "certificate" in row]
    assert len(positive) == 1 and positive[0]["vacuous"] is True
    assert positive[0]["premises"]["status"] == "INCONSISTENT"
    assert result["vacuous"] is True
    consistent = check_readings(env, sets, ["top"], couplings=FORCE)
    assert consistent["verdict"] == "ALL"
    assert [row["vacuous"] for row in consistent["choices"]] == [True, False]


def test_unknown_past_the_budget_names_the_open_units():
    # iota, scaled: coupled sets resolved to one candidate per joint value, plus uncoupled
    # binary sets; past 64 choices the verdict names only the units still open
    def labelled(name, pairs):
        return {"id": name, "version": 1, "unit": f"u-{name}", "status": "open",
                "readings": [{"id": f"{name}-{i}", "kind": "right", "content": None,
                              "labels": labels} for i, labels in enumerate(pairs)]}
    four = [{"bearer": b, "polarity": p} for b in ("state", "person") for p in ("negative", "positive")]
    coupled = [labelled(f"c{i}", four) for i in range(3)]
    loose = [labelled(f"f{i}", [{"force": "strict"}, {"force": "default"}]) for i in range(5)]
    couplings = [{"id": f"c-{axis}", "axis": axis, "sets": [{"set": s["id"], "version": 1} for s in coupled],
                  "by": "translator", "reason_spans": ["preamble"]} for axis in ("bearer", "polarity")]
    plan = plan_choices(coupled + loose, couplings=couplings)
    assert plan["route"] == "UNKNOWN"
    assert plan["units"] == [f"u-f{i}" for i in range(5)]
    assert plan_choices(coupled + loose[:4], couplings=couplings)["route"] == "enumerate"
    assert len(plan_choices(coupled + loose[:4], couplings=couplings)["choices"]) == 64
    uncoupled = plan_choices(coupled + loose)
    assert uncoupled["route"] == "UNKNOWN"
    assert uncoupled["units"] == [s["unit"] for s in coupled + loose]


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


def test_rights_english_uses_display_numbers_scopes_kinds_deciders_and_shadows():
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
    marriage = {"right": {"name": "r16", "holder": "person", "guard": ["top"], "lines": [power]}}
    limitation = {"limitation": {"name": "l29b", "scope": ["life", "r16"], "kinds": ["claim", "power"],
                                 "decided_by": "the courts", "conditions": [
                                     {"name": "purpose", "role": "sufficient", "decided_by": "a tribunal",
                                      "verbalisation": "the exercise defeats the purpose"}],
                                 "factors": ["public order", "morality"]}}
    units = [right(), marriage, limitation,
             {"bar": {"name": "b30", "reading": "query", "decided_by": "the courts"}}]
    document = correlate(raw, units)
    assert render_unit(document, marriage).startswith(
        "Right 2. Every person has the right described by its incident lines")
    assert "Power of right 2. Every person may marry, unless limitation 1 holds where that person marries." in (
        render_unit(document, marriage))
    assert render_unit(document, marriage).endswith("Recognition required; later effects not modelled.")
    assert render_unit(document, limitation) == (
        "Limitation 1 (on the claims and powers of rights 1 and 2). A right in this document is limited "
        "in a situation only where limitation 1 holds. Limitation 1 holds where the exercise defeats the "
        "purpose. Limitation 1 takes account of public order and morality. Limitation 1 is decided by the "
        "courts. Whether the exercise defeats the purpose is decided by a tribunal.")
    assert render_unit(document, units[3]) == (
        "Whether any right in this document permits an act aimed at the destruction of a right is "
        "checked, not ruled. Whether an act is so aimed is decided by the courts.")


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
