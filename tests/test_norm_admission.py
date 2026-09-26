"""Active norm units and regenerated layer leaves in W2 FOL documents."""
from copy import deepcopy

import pytest

from ve.admission import AdmissionError, admit_document
from ve.ast import And, Top, formula_to_data
from ve.entailment import prove_entailment
from ve.errors import VEError
from ve.identity import meaning_id
from tests.test_norms import environment, permission, rule
from ve.norms import NormDocument


def source():
    env = environment({"permitted": permission()})
    norms = NormDocument(env, [rule("allow", "permitted", True)])
    premise = formula_to_data(env, norms.elaborate("permitted"))
    document = {"units": [{"id": "u1", "span": [0, 20], "kind": "norm",
                           "content": norms.rules[0].to_dict()}],
                "graph": {"root": "layer", "nodes": [
                    {"name": "layer", "ast": premise, "label": "layer:norms:permitted"}]}}
    return env, document


def test_active_norm_unit_admits_only_its_regenerated_layer():
    env, document = source()
    admitted = admit_document(env, document)
    assert admitted["admitted"]
    assert admitted["kinds"] == ["norm"]
    assert admitted["report"]["assumptions"][0]["label"] == "layer:norms:permitted"
    assert len(admitted["report_id"]) == 64
    changed = deepcopy(document)
    changed["units"][0]["content"]["norm"]["sign"] = False
    with pytest.raises(AdmissionError):
        admit_document(env, changed)
    changed = deepcopy(document)
    changed["graph"]["nodes"][0]["label"] = "layer:norms:other"
    with pytest.raises(AdmissionError):
        admit_document(env, changed)


def test_quoted_norm_does_not_activate_a_layer():
    env, document = source()
    document["units"][0]["kind"] = ["attributed", "alice", "says", "norm"]
    document["units"].append({"id": "u2", "span": [20, 40], "kind": "norm",
                              "content": rule("silent", "permitted", False).to_dict()})
    with pytest.raises(AdmissionError):
        admit_document(env, document)


def test_quoted_only_norm_content_uses_norm_decoder_and_keeps_provenance():
    env, document = source()
    document["units"][0]["kind"] = ["attributed", "alice", "says", "norm"]
    document["units"].append({"id": "u2", "span": [20, 30], "kind": "asserted",
                               "content": ["top"]})
    document["graph"] = {"root": "asserted", "nodes": [
        {"name": "asserted", "ast": ["top"], "unit": "u2"}]}
    result = admit_document(env, document)
    assert result["admitted"]
    assert result["kinds"] == [["attributed", "alice", "says", "norm"], "asserted"]


def test_norm_layer_and_asserted_unit_replay_in_w2_graph():
    env, document = source()
    premise = NormDocument(env, [rule("allow", "permitted", True)]).elaborate("permitted")
    conclusion = And(premise, Top())
    proof = prove_entailment(env, (premise, Top()), conclusion)
    assert proof.status == "Found"
    document["units"].append({"id": "u2", "span": [20, 30], "kind": "asserted",
                              "content": ["top"]})
    document["graph"]["nodes"].extend([
        {"name": "asserted", "ast": ["top"], "unit": "u2"},
        {"name": "joined", "ast": formula_to_data(env, conclusion),
         "premises": ["layer", "asserted"], "certificate": proof.certificate}])
    document["graph"]["root"] = "joined"
    admitted = admit_document(env, document)
    assert [a["name"] for a in admitted["report"]["assumptions"]] == ["layer", "asserted"]
    stale = deepcopy(document)
    stale["graph"]["nodes"][-1]["certificate"]["premise_meaning_ids"] = [meaning_id(env, Top())]
    with pytest.raises(VEError, match="stale"):
        admit_document(env, stale)


def inactive_norm_mutants():
    """Norm content under a kind that does not activate it, with the graph leaf
    set to the empty-document layer (what silently dropping the content admits)."""
    env, document = source()
    empty = formula_to_data(env, NormDocument(env, []).elaborate("permitted"))
    for kind in ("asserted", "question", "definition", "instruction", "example", "meta",
                 ["causal", "because", "norm", "norm"], ["unformalised", "vague"]):
        changed = deepcopy(document)
        changed["units"][0]["kind"] = kind
        changed["graph"]["nodes"][0]["ast"] = empty
        yield f"kind {kind}", changed
    quoted = deepcopy(document)
    quoted["units"][0]["kind"] = ["hedged", "likely", "norm"]
    quoted["units"].append({"id": "u2", "span": [20, 30], "kind": "asserted",
                            "content": ["top"]})
    quoted["graph"] = {"root": "asserted", "nodes": [
        {"name": "asserted", "ast": ["top"], "unit": "u2"}]}
    edits = {"unknown predicate": ("predicate", "undeclared"),
             "predicate type": ("predicate", 7),
             "sign type": ("sign", "yes"),
             "rule name": ("name", "Bad Name"),
             "guard typing": ("guard", ["unary", "permitted", ["const", "nobody"]]),
             "guard shape": ("guard", ["nonsense"]),
             "unless shape": ("unless", "top"),
             "carve-out count": ("unless", [["top"]] * 9),
             "edge type": ("over", [{}])}
    for label, (field, value) in edits.items():
        changed = deepcopy(quoted)
        changed["units"][0]["content"]["norm"][field] = value
        yield f"quoted {label}", changed
    changed = deepcopy(quoted)
    changed["units"][0]["content"]["norm"]["extra"] = True
    yield "quoted extra field", changed
    changed = deepcopy(quoted)
    changed["units"][0]["content"] = {"norm": 5}
    yield "quoted non-object", changed


@pytest.mark.parametrize("label", [label for label, _ in inactive_norm_mutants()])
def test_inactive_norm_content_is_rejected_not_discarded(label):
    env, _ = source()
    document = dict(inactive_norm_mutants())[label]
    with pytest.raises(VEError):
        admit_document(env, document)


def test_quoted_norm_edges_name_the_quoted_source():
    env, document = source()
    document["units"][0]["kind"] = ["attributed", "alice", "says", "norm"]
    document["units"][0]["content"]["norm"]["over"] = ["alices-other-rule"]
    document["units"].append({"id": "u2", "span": [20, 30], "kind": "asserted",
                              "content": ["top"]})
    document["graph"] = {"root": "asserted", "nodes": [
        {"name": "asserted", "ast": ["top"], "unit": "u2"}]}
    assert admit_document(env, document)["admitted"]


@pytest.mark.parametrize("field,value", [("over", [{}]), ("over", [3]), ("predicate", {})])
def test_non_string_rule_fields_are_diagnosed(field, value):
    env, document = source()
    content = document["units"][0]["content"]
    content["norm"][field] = value
    with pytest.raises(VEError, match="must be strings"):
        NormDocument(env, [content])
