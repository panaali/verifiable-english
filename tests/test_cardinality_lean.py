"""The `cardinality@0` route through its relay and `ve document` (quantities QT-A4): both sides of each check. Lean's
answers and diagnostics reach the caller verbatim (`ve.cardinality`, `Service.Document`), and a route case's answer is
the one recorded."""
from __future__ import annotations

import json

import pytest

from tests.lean_service_corpus import cardinality_cases, recorded
from ve import cardinality
from ve.document import check_document, load_document, main, render_document
from ve.document.report import coverage
from ve.errors import CheckerUnavailable, ResourceLimit, UnsupportedProfile, VEError

CASES = {case["id"]: case for case in cardinality_cases() if type(case) is dict and "id" in case}
FA1, FA1B, GRAPH = CASES["fa1"], CASES["fa1b"], CASES["document-fa1"]
ENV = GRAPH["environment"]
W6A = ["cardinality@0", "order@0", "relational-fol@0", "time@0"]
# The constitution pilot's list (backlog dr-qt-cardinality-doc): the gate fact it needs is qt-a4b's first row.
FOUR = ["cardinality@0", "norm-defaults@0", "norms@0", "readings@1"]
NEEDS_GATE = "UnsupportedProfile: Missing profile relational-fol@0"
TOP = {"format": "ve-cardinality@1", "formula": ["quantity", ["top"]]}


def text(nodes, environment=ENV, graph=True, **front) -> bytes:
    """A part document with one unit per claim graph node, holding the node's statement (`content` when it is given)."""
    body, units, cursor = b"", [], 0
    for position, node in enumerate(nodes):
        line = f"Sentence {position} about the count.\n".encode()
        units.append({"id": node["name"], "span": [cursor, cursor + len(line)], "kind": "asserted", "meaning": "specified",
                      "support": "testimony", "content": node.get("content", {"cardinality": node["statement"]}),
                      **({"meaning_id": node["meaning_id"]} if "meaning_id" in node else {})})
        body, cursor = body + line, cursor + len(line)
    root = nodes[-1]["name"]
    meta = {"format": "ve-document@1", "environment": environment, "units": units, **front}
    if graph:
        meta["graph"] = {"root": root, "nodes": [{k: v for k, v in n.items() if k not in ("content", "meaning_id")} for n in nodes]}
    return b"---\n" + json.dumps(meta).encode() + b"\n---\n" + body


def written(tmp_path, *args, **front):
    path = tmp_path / "part.ve.md"
    path.write_bytes(text(*args, **front))
    return path


def test_a_found_certificate_is_lean_s_and_an_open_problem_has_none():
    """The search runs on Lean's regenerated problem and Lean replays what it found; FA1b, whose conclusion a two-object
    model refutes, has no certificate and is refuted by Lean's countermodel, FA1's is not."""
    certificate = cardinality.prove(FA1["environment"], FA1["premises"], FA1["conclusion"])
    assert cardinality.check_certificate(FA1["environment"], FA1["premises"], FA1["conclusion"], certificate) is True
    assert cardinality.prove(FA1B["environment"], FA1B["premises"], FA1B["conclusion"]) is None
    forged = CASES["fa1b-certificate"]
    assert cardinality.check_certificate(forged["environment"], forged["premises"], forged["conclusion"],
                                         forged["certificate"]) is False
    other = FA1B["premises"][:-1]
    with pytest.raises(VEError, match="stale or bound to different statements"):
        cardinality.check_certificate(FA1["environment"], other, FA1["conclusion"], certificate)
    model = CASES["fa1b-countermodel"]
    assert cardinality.countermodel(model["environment"], model["premises"], model["conclusion"], model["model"])["refutes"]
    fa1 = CASES["fa1-countermodel"]
    assert not cardinality.countermodel(fa1["environment"], fa1["premises"], fa1["conclusion"], fa1["model"])["refutes"]


def test_a_zero_budget_search_finds_nothing_and_claims_nothing():
    """Exhaustion is inconclusive: no certificate, never a refutation."""
    assert cardinality.prove(FA1["environment"], FA1["premises"], FA1["conclusion"], max_steps=0) is None


def test_lean_s_diagnostics_reach_the_caller_verbatim():
    with pytest.raises(UnsupportedProfile, match="cardinality@0 requires order@0, relational-fol@0 and time@0"):
        cardinality.admission({**FA1["environment"], "profiles": ["cardinality@0", "time@0"]}, [], TOP)
    with pytest.raises(VEError, match="Unknown cardinality operator nope"):
        cardinality.paraphrase(FA1["environment"], {"format": "ve-cardinality@1", "formula": ["nope"]})
    with pytest.raises(ResourceLimit, match="At most 1000 claim graph nodes"):
        cardinality.document(ENV, {"root": "n0", "nodes": [{"name": f"n{i}", "statement": TOP} for i in range(1001)]})


def test_a_part_document_is_admitted_with_lean_s_report(tmp_path, capsys):
    path = written(tmp_path, GRAPH["document"]["nodes"])
    answer = check_document(path)
    relayed = cardinality.document(ENV, GRAPH["document"])
    assert answer["cardinality"]["report"] == relayed["report"]
    assert [leaf["name"] for leaf in answer["cardinality"]["report"]["leaves"]] == ["total", "increase", "stay", "exclusive"]
    assert answer["coverage"]["bytes_by_status"] == {"CHECKED": answer["coverage"]["source_bytes"]}
    # Nothing here decides the premise set: that line says so.
    assert answer["premises"]["status"] == "UNKNOWN"
    assert main(["check", str(path)]) == 0 and json.loads(capsys.readouterr().out) == answer
    assert "is exactly 18." in render_document(path) and coverage(load_document(path))["coverage_percent"] == 100
    assert load_document(path)["cardinality"] is None  # the report is `check`'s: loading asks for no claim graph


def test_a_document_without_a_graph_has_no_report_and_needs_no_document_layer(tmp_path):
    nodes = [{"name": "only", "statement": TOP}]
    answer = check_document(written(tmp_path, nodes, {**ENV, "profiles": W6A}, graph=False))
    assert "cardinality" not in answer and answer["coverage"]["coverage_percent"] == 100
    with pytest.raises(UnsupportedProfile, match="cardinality documents require documents@1"):
        check_document(written(tmp_path, nodes, {**ENV, "profiles": W6A}))


@pytest.mark.parametrize("profiles, message", [
    (FOUR, NEEDS_GATE),
    (["cardinality@0", "documents@1", "norm-defaults@0", "norms@0", "order@0", "readings@1", "relational-fol@0", "time@0"],
     "cardinality@0 with norm-defaults@0"),
    (["cardinality@0", "norms@0", "order@0", "relational-fol@0", "time@0"], "cardinality@0 with norms@0"),
    (["cardinality@0", "order@0", "readings@1", "relational-fol@0", "time@0"], "cardinality@0 with readings@1"),
    (["cardinality@0", "order@0", "relational-fol@0"], "cardinality@0 requires time@0")])
def test_the_gate_refuses_a_list_cardinality_does_not_compose_with(tmp_path, profiles, message):
    with pytest.raises(UnsupportedProfile, match=message):
        check_document(written(tmp_path, [{"name": "only", "statement": TOP}], {**ENV, "profiles": profiles}))


def test_the_route_cases_answer_as_recorded():
    from ve.backends.relay import rows
    cases = recorded("document")
    answers = rows("document", cases)
    assert [case["id"] for case in cases] == ["cardinality-part", "cardinality-four-profiles"]
    assert answers[0]["status"] == "ok" and answers[0]["cardinality"]["report"]["root"]["name"] == "root"
    assert answers[1]["error"] == NEEDS_GATE


@pytest.mark.parametrize("change, message", [
    (lambda n: {**n, "content": {"ast": ["top"]}}, "a cardinality@0 unit's content is a cardinality statement"),
    (lambda n: {**n, "content": {"norm": {}}}, "a cardinality@0 unit's content is a cardinality statement"),
    (lambda n: {**n, "content": {"cardinality": {"format": "ve-cardinality@1", "formula": ["count", "user", [], "eq", "1"]}}},
     r"CardinalityNotFinite\(user\)"),
    (lambda n: {**n, "content": {"cardinality": {"format": "nope", "formula": ["quantity", ["top"]]}}},
     "Unsupported cardinality format")])
def test_a_unit_s_content_is_a_statement_lean_admits(tmp_path, change, message):
    node = {"name": "only", "statement": TOP}
    with pytest.raises(VEError, match=message):
        check_document(written(tmp_path, [change(node)], graph=False))
    check_document(written(tmp_path, [node], graph=False))


def test_cardinality_content_needs_the_profile(tmp_path):
    environment = {k: v for k, v in ENV.items() if k not in ("cardinality", "cardinality_schema", "unit_schema", "units")}
    plain = {**environment, "profiles": ["relational-fol@0"], "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}}}
    with pytest.raises(UnsupportedProfile, match="cardinality content requires cardinality@0"):
        check_document(written(tmp_path, [{"name": "only", "statement": TOP}], plain, graph=False))


@pytest.mark.parametrize("member, value", [("open_terms", []), ("reading_sets", []), ("narrowings", [])])
def test_what_the_chain_does_not_compose_is_refused_by_name(tmp_path, member, value):
    with pytest.raises(UnsupportedProfile, match=f"{member} beside cardinality@0 is not composed"):
        check_document(written(tmp_path, [{"name": "only", "statement": TOP}], graph=False, **{member: value}))


def test_every_graph_node_is_a_unit_holding_its_statement(tmp_path):
    nodes = GRAPH["document"]["nodes"]
    # Each leaf is bound: another unit name, or another statement under its name, is refused; the same statement passes.
    renamed = text(nodes).replace(b'"id": "total"', b'"id": "other"')
    path = tmp_path / "renamed.ve.md"
    path.write_bytes(renamed)
    with pytest.raises(VEError, match="claim graph node total is not a unit holding its statement"):
        check_document(path)
    other = [{**nodes[0], "content": {"cardinality": TOP}}, *nodes[1:]]
    with pytest.raises(VEError, match="claim graph node total is not a unit holding its statement"):
        check_document(written(tmp_path, other))
    assert check_document(written(tmp_path, [{**n, "content": {"cardinality": n["statement"]}} for n in nodes]))


def test_a_stale_meaning_id_and_an_unproved_root_are_refused(tmp_path):
    node = {"name": "only", "statement": TOP}
    mid = load_document(written(tmp_path, [node], graph=False))["units"][0]["meaning_id"]
    assert check_document(written(tmp_path, [{**node, "meaning_id": mid}], graph=False))
    with pytest.raises(VEError, match="unit meaning id does not match content"):
        check_document(written(tmp_path, [{**node, "meaning_id": "0" * 64}], graph=False))
    with pytest.raises(VEError, match="graph rejected"):
        check_document(written(tmp_path, CASES["document-unproved"]["document"]["nodes"]))


def test_a_large_well_formed_graph_ends_within_its_limit(tmp_path):
    """Every statement is read once and its size charged: at the limit the document is answered, one past it refused."""
    nodes = [{"name": f"n{i}", "statement": TOP} for i in range(1000)]
    answer = check_document(written(tmp_path, nodes))
    assert answer["cardinality"]["report"]["root"]["name"] == "n999"
    with pytest.raises(ResourceLimit, match="At most 1000 claim graph nodes"):
        check_document(written(tmp_path, [*nodes, {"name": "n1000", "statement": TOP}]))


def test_lean_answering_unavailable_is_no_python_verdict(tmp_path, monkeypatch):
    """A `cardinality@0` document has no Python path: Lean's `CheckerUnavailable` is raised, not read by Python's."""
    from ve.backends import relay
    path = written(tmp_path, [{"name": "only", "statement": TOP}], graph=False)
    monkeypatch.setattr(relay, "answer", lambda mode, case: (
        {"id": case["id"], "status": "error", "error": "CheckerUnavailable: no"}, CheckerUnavailable("no")))
    with pytest.raises(CheckerUnavailable, match="no"):
        check_document(path)
