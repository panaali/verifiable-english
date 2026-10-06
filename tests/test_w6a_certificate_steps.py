"""Certificate replay steps: Python's 10,000-step budget, in Lean too.

Python replays a certificate one step per trace node and stops with
`ResourceLimit` after `max_steps = 10,000`; the frozen Lean checkers bound only
the trace's depth, so Lean accepted valid certificates Python refuses. A
certificate that splits n disjunctions before closing every branch has
2ⁿ − 1 + 2ⁿ⁺¹ nodes: 6,143 for n = 11 (accepted by both) and 12,287 for
n = 12 (refused by both), at depth n + 2.
"""
from __future__ import annotations

import json

import pytest
from ve.errors import ResourceLimit

from tests import lean_routes

from conformance.p0 import _raw_certificate, envelope
from tests.test_units_lean_w6a import LEAN as QUANTITY, lean as lean_quantity, quantity
from tests.test_w6a_review_regressions import raw_environment
from tests.test_w6a_route_limits import LEAN, lean
from ve import Environment
from ve.ast import formula_from_data
from ve.entailment import check_entailment_certificate, prove_entailment
from ve.units import check_quantity_certificate, prove_quantity

pytestmark = pytest.mark.skipif(not (LEAN.exists() and lean_routes.SERVICE.exists()),
                                reason="build the Lean runners first")
STEP_LIMIT = "ResourceLimit: certificate replay exceeds 10,000 steps"


def predicates(n, sort="s"):
    out = {f"a{i}": {"arguments": [sort], "description": "a"} for i in range(n)}
    out.update({f"b{i}": {"arguments": [sort], "description": "b"} for i in range(n)})
    return out


def formulas(n):
    """(aᵢ(c) ∨ bᵢ(c)) for i < n, then ¬aₙ₋₁(c) and ¬bₙ₋₁(c); they entail ⊥."""
    c = ["const", "c"]
    return ([["or", ["unary", f"a{i}", c], ["unary", f"b{i}", c]] for i in range(n)]
            + [["not", ["unary", f"a{n - 1}", c]], ["not", ["unary", f"b{n - 1}", c]]])


def bushy(n):
    """Split every disjunction, in order, before closing any branch."""
    def tree(i):
        if i == n - 1:
            return {"rule": "expand", "at": i, "children": [
                {"rule": "expand", "at": n, "children": [{"rule": "close"}]},
                {"rule": "expand", "at": n + 1, "children": [{"rule": "close"}]}]}
        return {"rule": "expand", "at": i, "children": [tree(i + 1), tree(i + 1)]}
    return tree(0)


def fol_env(n, profiles=("relational-fol@0",)):
    return envelope({"sorts": {"s": {"description": "s"}},
                     "constants": {"c": {"sort": "s", "description": "c"}},
                     "predicates": predicates(n)}, profiles)


@pytest.mark.parametrize("profiles", [("relational-fol@0",), ("order@0", "relational-fol@0")])
@pytest.mark.parametrize("n,fits", [(11, True), (12, False)])
def test_route_certificates_share_the_step_budget(profiles, n, fits):
    env = fol_env(n, profiles)
    e = Environment(env)
    ps = [formula_from_data(e, p) for p in formulas(n)]
    bottom = formula_from_data(e, ["bottom"])
    certificate = {**prove_entailment(e, ps, bottom).certificate, "trace": bushy(n)}
    assert check_entailment_certificate(e, ps, bottom, certificate, max_steps=100_000).valid
    checked = check_entailment_certificate(e, ps, bottom, certificate)
    [got] = lean([{"id": "c", "kind": "certificate", "environment": env, "premises": formulas(n),
                   "conclusion": ["bottom"], "certificate": certificate}])
    if fits:
        assert checked.valid
        assert got["status"] == "ok" and got["valid"] is True, got
    else:
        assert (checked.valid, checked.status) == (False, "ResourceLimit")
        assert got["status"] == "error" and got["error"] == STEP_LIMIT and got["valid"] is False, got


def w6_env(n):
    return raw_environment({}, sorts={"item": {"description": "item"}},
                           constants={"c": {"sort": "item", "description": "c"}},
                           predicates=predicates(n, "item"))


def w6_certificate(n, raw):
    premises = [quantity(f) for f in formulas(n)]
    small = prove_quantity(Environment(raw), premises, quantity(["bottom"]))
    return premises, {**small, "core": {**small["core"], "trace": bushy(n)}}


@pytest.mark.parametrize("n,fits", [(11, True), (12, False)])
def test_quantity_certificates_share_the_step_budget(n, fits):
    raw = w6_env(n)
    premises, certificate = w6_certificate(n, raw)
    env = Environment(raw)
    assert check_quantity_certificate(env, premises, quantity(["bottom"]), certificate,
                                      max_steps=100_000)
    if fits:
        python = check_quantity_certificate(env, premises, quantity(["bottom"]), certificate)
    else:
        with pytest.raises(ResourceLimit, match="certificate replay exceeds"):
            check_quantity_certificate(env, premises, quantity(["bottom"]), certificate)
    [got] = lean_quantity([{"id": "c", "kind": "certificate", "environment": raw,
                            "premises": premises, "conclusion": quantity(["bottom"]),
                            "certificate": certificate}])
    if fits:
        assert python is True
        assert got["status"] == "ok" and got["valid"] is True, got
    else:
        assert got["status"] == "error" and got["error"] == STEP_LIMIT and got["valid"] is False, got


def test_document_lemma_over_the_step_budget_is_not_established():
    from ve.errors import VEError
    from ve.admission import admit_document
    raw = w6_env(12)
    raw["profiles"] = sorted({*raw["profiles"], "documents@1"})
    premises, certificate = w6_certificate(12, raw)
    document = {"units": [], "open_terms": ["t"],
                "lemmas": [{"name": "b/l", "conclusion": quantity(["bottom"]),
                            "leaves": [{"quantity": p, "label": "open:t"} for p in premises],
                            "certificate": certificate}],
                "graph": {"root": "r", "nodes": [{"name": "r", "quantity": quantity(["bottom"]),
                                                  "label": "cite:b/l"}]}}
    message = "AdmissionError: lemma b/l is not established by its certificate"
    with pytest.raises(VEError, match=message):
        admit_document(Environment(raw), document)
    [got] = lean_quantity([{"id": "d", "kind": "document", "environment": raw, "document": document}])
    assert got["status"] == "error" and got["error"] == message, got


@pytest.mark.parametrize("n,fits", [(11, True), (12, False)])
def test_admission_edges_share_the_step_budget(n, fits):
    """An admission edge whose certificate needs more than 10,000 steps is not
    verified, so the graph is rejected as for an invalid certificate."""
    from ve.admission import admit_document
    from ve.errors import VEError
    env = fol_env(n)
    premises = formulas(n)
    certificate = {**_raw_certificate(env, premises, ["bottom"]), "trace": bushy(n)}
    nodes = [{"name": f"p{i}", "ast": p, "label": "open:t"} for i, p in enumerate(premises)]
    nodes.append({"name": "root", "ast": ["bottom"], "premises": [f"p{i}" for i in range(len(premises))],
                  "certificate": certificate})
    document = {"units": [], "open_terms": ["t"], "graph": {"root": "root", "nodes": nodes}}
    [got] = lean([{"id": "a", "kind": "admission", "environment": env, "document": document}])
    if fits:
        admitted = admit_document(Environment(env), document)
        assert got["status"] == "ok" and got["report_id"] == admitted["report_id"], got
    else:
        with pytest.raises(VEError):
            admit_document(Environment(env), document)
        assert got["status"] == "error" and got["error"].startswith("graph rejected"), got


@pytest.mark.parametrize("n,fits", [(11, True), (12, False)])
def test_bundle_lemmas_share_the_step_budget(n, fits):
    from ve.bundle import check_bundle, lean_bundle_verdict
    from ve.errors import VEError
    from ve.identity import meaning_id
    env_json = fol_env(n, ("definitions@0", "relational-fol@0"))
    e = Environment(env_json)
    ps = [formula_from_data(e, p) for p in formulas(n)]
    bottom = formula_from_data(e, ["bottom"])
    certificate = {**prove_entailment(e, ps, bottom).certificate, "trace": bushy(n)}
    leaves = [{"label": "open:t", "ast": p} for p in formulas(n)]
    lemma = {"name": "l", "environment_id": e.environment_id, "premises": leaves, "cites": [],
             "conclusion": ["bottom"], "meaning_id": meaning_id(e, bottom), "reading_choices": {},
             "transitive_leaves": leaves, "certificate": certificate}
    data = {"version": "ve-bundle@0", "environment": e.to_dict(), "lemmas": [lemma]}
    verdict = lean_bundle_verdict(LEAN, data["environment"], data["lemmas"])
    if fits:
        assert check_bundle(data)["status"] == "Checked"
        assert verdict["status"] == "ok", verdict
    else:
        with pytest.raises(VEError):
            check_bundle(data)
        assert verdict["status"] == "error" and verdict["error"] == "Lemma l certificate failed", verdict
