"""The small soft-chain document has the pilot probe's profiles, a soft rule and a claim graph."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ve.document import check_document, load_document
from ve.errors import CheckerUnavailable, VEError
from ve.admission import admit_document
from ve.ast import formula_to_data
from ve.norm_defaults_route import admit_norm_defaults_document
from ve.norms import NormDocument
from ve.softnorms import SoftEnvironment, check_soft_source


FIXTURE = Path(__file__).parent / "data/rd9-docroute.ve.md"
THROUGH_FILL = "UnsupportedProfile: norm-defaults@0 documents are checked through fill (ve.norm_defaults)"
NEEDS_PROFILE = "UnsupportedProfile: unspecified completion requires norm-defaults@0"


def _front():
    raw = FIXTURE.read_bytes()
    head, body = raw[4:].split(b"\n---\n", 1)
    return json.loads(head), body


def _without_profile(tmp_path):
    front, body = _front()
    front["environment"]["profiles"].remove("norm-defaults@0")
    path = tmp_path / "without-defaults.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + body)
    return path


def _direct_case():
    front, _ = _front()
    lower = deepcopy(front["environment"])
    lower["profiles"].remove("readings@1")
    document = {
        "units": [
            {"id": "u1", "span": front["units"][0]["span"], "kind": "norm",
             "content": front["units"][0]["content"]},
            {"id": "u2", "span": front["units"][1]["span"], "kind": "asserted",
             "content": ["top"]},
        ],
        "graph": front["graph"], "lemmas": [], "open_terms": [], "reading_sets": [], "narrowings": [],
    }
    return SoftEnvironment(lower), document


def test_soft_chain_document_checks_the_filled_route():
    loaded = load_document(FIXTURE)
    assert loaded["norm_defaults"] is None  # The soft chain owns its fill.
    report = check_document(FIXTURE)
    env, document = _direct_case()
    admitted = admit_norm_defaults_document(env, document)
    assert report["admission"]["admitted"] is True
    assert report["admission"]["report"] == admitted["report"]
    assert report["admission"]["core_report_id"] == admitted["report_id"]


def test_filled_soft_layer_matches_ordinary_w1():
    # The frozen oracle proposes the ordinary W1 tree. Both answers are Lean's.
    from conformance import frozen_norm_defaults as oracle
    env, source = _direct_case()
    filled = oracle.UnspecifiedSoftDocument(env, [source["units"][0]["content"]])
    label, formula = next((name, ast) for name, ast in filled.filled.premises()
                          if name == "layer:norms:x_permitted")
    ast = formula_to_data(filled.filled.env, formula)
    assert "unsaid__x_permitted" in json.dumps(ast)
    source["graph"] = {"root": "layer", "nodes": [{"name": "layer", "ast": ast, "label": label}]}
    routed = admit_norm_defaults_document(env, source)
    ordinary_env = deepcopy(filled.filled.env.to_dict())
    ordinary_env["profiles"].remove("soft-norms@0")
    ordinary = deepcopy(source)
    ordinary["units"][0]["content"] = filled.filled.rules[0].to_dict()
    end = ordinary["units"][-1]["span"][1]
    ordinary["units"].append({"id": "generated", "span": [end, end + 1], "kind": "norm",
                              "content": filled.filled.rules[1].to_dict()})
    checked_w1 = admit_document(ordinary_env, ordinary)
    assert routed["admitted"] is checked_w1["admitted"] is True
    assert routed["report"] == checked_w1["report"]


def test_soft_admission_conditions_are_bound_to_the_source(monkeypatch):
    from ve import norm_defaults_route as route
    env, document = _direct_case()
    original = route.run_case
    for labels in (["soft:coherence:absent,absent"],
                   ["soft:coherence:absent,absent", "soft:coherence:absent,absent"]):
        def changed(case):
            row = original(case)
            if case["kind"] == "admission":
                row = {**row, "conditional_on": labels}
            return row
        monkeypatch.setattr(route, "run_case", changed)
        with pytest.raises(CheckerUnavailable, match="unbound condition"):
            admit_norm_defaults_document(env, document)
        monkeypatch.setattr(route, "run_case", original)

    def missing(case):
        row = original(case)
        if case["kind"] == "admission":
            row = {key: value for key, value in row.items() if key != "conditional_on"}
        return row
    monkeypatch.setattr(route, "run_case", missing)
    with pytest.raises(CheckerUnavailable, match="another filled route"):
        admit_norm_defaults_document(env, document)


def test_soft_admission_row_fields_are_typed():
    from ve import norm_defaults_route as route
    from ve.backends.service_schema import Invalid, check_row
    env, document = _direct_case()
    case = {"id": "admission", "kind": "admission", "environment": env.to_dict(), "document": document}
    row = route.run_case(case)
    check_row("norm-defaults", row, case, 0)
    for field in row:
        missing = {key: value for key, value in row.items() if key != field}
        wrong_type = {**row, field: 7}
        if field != "conditional_on":
            with pytest.raises(Invalid):
                check_row("norm-defaults", missing, case, 0)
        with pytest.raises(Invalid):
            check_row("norm-defaults", wrong_type, case, 0)


def test_soft_admission_elaborates_fill_once(monkeypatch):
    from ve import norm_defaults_route as route
    env, document = _direct_case()
    original = route.run_case
    called = []

    def counted(case):
        called.append(case["kind"])
        return original(case)

    monkeypatch.setattr(route, "run_case", counted)
    assert route.admit_norm_defaults_document(env, document)["admitted"] is True
    assert called == ["admission", "norm-defaults-elaborate"]


def test_unspecified_without_profile_keeps_its_own_refusal(tmp_path):
    with pytest.raises(VEError, match="^" + NEEDS_PROFILE + "$"):
        check_document(_without_profile(tmp_path))


def test_plain_soft_document_keeps_its_admission_route(tmp_path):
    front, body = _front()
    front["environment"]["profiles"].remove("norm-defaults@0")
    front["environment"]["vocabulary"]["predicates"]["x_permitted"]["regulated"]["default"] = "deny"
    path = tmp_path / "plain-soft.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + body)
    assert check_document(path)["admission"]["admitted"] is True


def test_direct_soft_check_of_unfilled_tree_still_refuses():
    front, _ = _front()
    with pytest.raises(VEError, match="^" + THROUGH_FILL.replace("(", r"\(").replace(")", r"\)") + "$"):
        check_soft_source(front["environment"], [front["units"][0]["content"]])


def test_direct_w1_outcome_of_unfilled_soft_tree_still_refuses():
    front, _ = _front()
    document = NormDocument(SoftEnvironment(front["environment"]), [])
    with pytest.raises(VEError, match="^" + THROUGH_FILL.replace("(", r"\(").replace(")", r"\)") + "$"):
        document.outcome("x_required")
