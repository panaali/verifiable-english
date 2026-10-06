"""W6a limits directive: static limits before any work, metered constructions.

Every static limit of a problem is checked on the decoded input before a model
is decoded, a certificate is read or anything is evaluated, in one shared stage
per wire mode and in the same order in Python, Lean and Rust. Each reproducer
from the W6a loop review is pinned here, with the rest of its class.
"""
from __future__ import annotations

import pytest

from tests import lean_routes

from tests.test_units_lean_w6a import LEAN, lean, quantity, rust
from tests.test_w6a_looprecheck2 import model, raw
from ve.environment import Environment
from ve.errors import ResourceLimit
from ve.units import (AGGREGATE_LIMIT, check_quantity_certificate, elaborate_quantity,
                      prove_quantity, quantity_countermodel)

pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="build the Lean service first")


def doubling(n):
    """F₀ = ⊤, Fₙ₊₁ = Fₙ ∧ Fₙ: 2ⁿ⁺¹ − 1 nodes."""
    f = ["top"]
    for _ in range(n):
        f = ["and", f, f]
    return f


def lean_error(got, text="ResourceLimit"):
    assert got["status"] == "error" and got["error"].startswith("ResourceLimit") \
        and text in got["error"], got


def rust_error(got):
    assert got["status"] == "error" and got["error"]["code"] == "ResourceLimit", got


# --- Aggregate nodes across premises and conclusion (loop review P2) ---------

def test_countermodel_aggregate_reproducer_three_ways():
    """[F₁₂, F₁₂] ⊢ ⊥ has 16,383 core nodes, each statement under 10,000.
    Lean used to answer `refutes=true`; all three now stop before the model."""
    premises, conclusion = [quantity(doubling(12))] * 2, quantity(["bottom"])
    env = Environment(raw())
    for p in premises:
        elaborate_quantity(env, p)  # each statement is within its own limits
    case = {"environment": raw(), "premises": premises, "conclusion": conclusion,
            "model": model(["b", "a"])}
    with pytest.raises(ResourceLimit, match=AGGREGATE_LIMIT):
        quantity_countermodel(env, premises, conclusion, case["model"])
    [got] = lean([{"id": "m", "kind": "countermodel", **case}])
    lean_error(got, AGGREGATE_LIMIT)
    [other] = rust([{"id": "m", "kind": "quantity", "mode": "countermodel", **case}])
    rust_error(other)


def test_aggregate_is_checked_before_the_model_three_ways():
    """An invalid model is never read when the problem is already too large."""
    premises, conclusion = [quantity(doubling(12))] * 2, quantity(["bottom"])
    bad = {"complete": True, "domains": {"item": ["a", "a"]}, "constants": {}, "relations": {"p": []}}
    with pytest.raises(ResourceLimit, match=AGGREGATE_LIMIT):
        quantity_countermodel(Environment(raw()), premises, conclusion, bad)
    case = {"environment": raw(), "premises": premises, "conclusion": conclusion, "model": bad}
    [got] = lean([{"id": "m", "kind": "countermodel", **case}])
    lean_error(got, AGGREGATE_LIMIT)
    [other] = rust([{"id": "m", "kind": "quantity", "mode": "countermodel", **case}])
    rust_error(other)


@pytest.mark.parametrize("split", [(12, 11, 11), (13, 0, 0), (11, 11, 11)])
def test_aggregate_boundary_three_ways(split):
    """10,000 is allowed and 10,001 is not, however the nodes are split."""
    a, b, c = (doubling(n) for n in split)
    total = sum(2 ** (n + 1) - 1 for n in split)
    premises, conclusion = [quantity(a), quantity(b)], quantity(c)
    case = {"environment": raw(), "premises": premises, "conclusion": conclusion,
            "model": model(["a", "b"])}
    [got] = lean([{"id": "m", "kind": "countermodel", **case}])
    [other] = rust([{"id": "m", "kind": "quantity", "mode": "countermodel", **case}])
    env = Environment(raw())
    if total > 10000:
        with pytest.raises(ResourceLimit):
            quantity_countermodel(env, premises, conclusion, case["model"])
        lean_error(got)
        rust_error(other)
    else:
        assert quantity_countermodel(env, premises, conclusion, case["model"]) is False
        assert got["status"] == "ok" and got["refutes"] is False, got
        assert other["status"] == "ok" and other["refutes"] is False, other


def rebind(small, admissions, premises):
    """A certificate for the small problem [⊤, ⊤] ⊢ ⊤, rebound to the
    identities Lean regenerates for a problem with the same shape."""
    *ps, c = admissions
    core = {**small["core"], "environment_id": c["target_environment_id"],
            "premise_meaning_ids": [p["core_meaning_id"] for p in ps],
            "conclusion_meaning_id": c["core_meaning_id"]}
    return {**small, "environment_id": c["environment_id"],
            "premise_meaning_ids": [p["meaning_id"] for p in ps],
            "conclusion_meaning_id": c["meaning_id"], "core": core}


def oversized_certificate():
    env = Environment(raw())
    small = prove_quantity(env, [quantity(["top"])] * 2, quantity(["top"]))
    premises, conclusion = [quantity(doubling(12))] * 2, quantity(["top"])
    admitted = lean([{"id": str(i), "environment": raw(), "quantity": q}
                     for i, q in enumerate([*premises, conclusion])])
    assert all(a["status"] == "ok" for a in admitted)
    return premises, conclusion, rebind(small, admitted, premises)


def test_certificate_aggregate_is_checked_before_replay():
    """A replayable certificate for an oversized problem is not evidence:
    Lean rejects it before reading the certificate, as Python does."""
    premises, conclusion, certificate = oversized_certificate()
    with pytest.raises(ResourceLimit, match=AGGREGATE_LIMIT):
        check_quantity_certificate(Environment(raw()), premises, conclusion, certificate)
    [got] = lean([{"id": "c", "kind": "certificate", "environment": raw(), "premises": premises,
                   "conclusion": conclusion, "certificate": certificate}])
    lean_error(got, AGGREGATE_LIMIT)
    assert got["valid"] is False
    [garbage] = lean([{"id": "c", "kind": "certificate", "environment": raw(), "premises": premises,
                       "conclusion": conclusion, "certificate": {"format": "nothing"}}])
    lean_error(garbage, AGGREGATE_LIMIT)
    # The same shape within the limit replays in both.
    small = [quantity(doubling(11))] * 2
    admitted = lean([{"id": str(i), "environment": raw(), "quantity": q}
                     for i, q in enumerate([*small, conclusion])])
    fitting = rebind(certificate, admitted, small)
    assert check_quantity_certificate(Environment(raw()), small, conclusion, fitting)
    [ok] = lean([{"id": "c", "kind": "certificate", "environment": raw(), "premises": small,
                  "conclusion": conclusion, "certificate": fitting}])
    assert ok["status"] == "ok" and ok["valid"] is True, ok


def test_document_lemma_over_the_aggregate_is_not_established():
    """Documents check lemmas through the same stage: an oversized lemma is
    'not established' in Lean and Python alike."""
    from ve.admission import admit_document
    from ve.errors import VEError
    premises, conclusion, certificate = oversized_certificate()
    data = raw()
    data["profiles"] = sorted({*data["profiles"], "documents@1"})
    # Documents bind to their own environment identity; rebind to it.
    admitted = lean([{"id": str(i), "environment": data, "quantity": q}
                     for i, q in enumerate([*premises, conclusion])])
    certificate = rebind(certificate, admitted, premises)
    document = {"units": [], "lemmas": [{"name": "b/l", "conclusion": conclusion,
                                         "leaves": [{"quantity": p, "label": "open:t"}
                                                    for p in premises],
                                         "certificate": certificate}],
                "open_terms": ["t"],
                "graph": {"root": "r", "nodes": [{"name": "r", "quantity": conclusion,
                                                  "label": "cite:b/l"}]}}
    message = "AdmissionError: lemma b/l is not established by its certificate"
    with pytest.raises(VEError, match=message):
        admit_document(Environment(data), document)
    [got] = lean([{"id": "d", "kind": "document", "environment": data, "document": document}])
    assert got["status"] == "error" and got["error"] == message, got


# --- Per-statement node count before elaboration ------------------------------

def test_statement_node_count_precedes_type_errors_three_ways():
    """An ill-typed node ahead of 10,001 nodes: every backend reports the node
    limit, which is checked before elaboration, not where elaboration stops."""
    ill = ["eq", ["var", 0], ["var", 0]]  # unbound: an elaboration error
    formula = ["and", ill, doubling(13)]
    with pytest.raises(ResourceLimit, match="node or depth limit"):
        elaborate_quantity(Environment(raw()), quantity(formula))
    [got] = lean([{"id": "q", "environment": raw(), "quantity": quantity(formula)}])
    lean_error(got, "node or depth limit")
    [other] = rust([{"id": "q", "kind": "quantity", "environment": raw(),
                     "quantity": quantity(formula)}])
    rust_error(other)


def test_statement_node_count_includes_the_operator_position_three_ways():
    """Arrays in the operator position count too (Rust used to skip them)."""
    formula = [doubling(13)]
    with pytest.raises(ResourceLimit, match="node or depth limit"):
        elaborate_quantity(Environment(raw()), quantity(formula))
    [got] = lean([{"id": "q", "environment": raw(), "quantity": quantity(formula)}])
    lean_error(got, "node or depth limit")
    [other] = rust([{"id": "q", "kind": "quantity", "environment": raw(),
                     "quantity": quantity(formula)}])
    rust_error(other)
