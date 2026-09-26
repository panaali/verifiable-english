"""Active norm units and regenerated layer leaves in W2 FOL documents."""
from copy import deepcopy

import pytest

from ve.admission import AdmissionError, admit_document
from ve.ast import formula_to_data
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
