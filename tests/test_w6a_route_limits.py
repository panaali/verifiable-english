"""W6a limits directive on the `route` subcommand: nothing runs unmetered.

Python and Rust stop with `ResourceLimit` when a model's defined tables or an
evaluation exceed `MAX_EVALUATIONS`; Lean used to build defined tables and
evaluate route formulas without a budget, so it answered, or ran on, where they
stopped. Lean now builds defined tables one candidate row at a time under the
shared budget and tuple limit, evaluates every family (relational, order,
closure, closure with n-ary atoms) under the Python/Rust charges, and checks
each case's formula limits before it decodes the model.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import time

import pytest

from conformance.p0 import envelope
from ve import Environment, FiniteModel, evaluate
from ve.ast import document_from_data, formula_from_data
from ve.errors import ResourceLimit
from ve.search import check_countermodel

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_conformance"
RUST = ROOT / "rust" / "target" / "release" / "ve"
pytestmark = pytest.mark.skipif(not (LEAN.exists() and RUST.exists()),
                                reason="build ve_conformance (lake build) and the Rust release binary")
WALL = 30  # seconds for one batch of limit-busting cases, per backend


def run(command, cases):
    start = time.monotonic()
    completed = subprocess.run(command, input=json.dumps(cases), text=True, capture_output=True,
                               timeout=WALL * 4)
    elapsed = time.monotonic() - start
    assert completed.returncode in (0, 1), completed.stderr[:500]
    assert elapsed < WALL, (command[0], elapsed)
    results = json.loads(completed.stdout)
    assert len(results) == len(cases)
    return results


def lean(cases):
    return run([str(LEAN), "route", "-"], cases)


def rust(cases):
    return run([str(RUST), "conformance"], cases)


def lean_limit(got, text=""):
    assert got["status"] == "error" and got["error"].startswith("ResourceLimit") \
        and text in got["error"], got


def rust_limit(got):
    assert got["status"] == "error" and got["error"]["code"] == "ResourceLimit", got


def nest(depth, quantifier="forall", sort="s", body=None):
    body = body or ["top"]
    for _ in range(depth):
        body = [quantifier, sort, body]
    return body


def doubling(n):
    f = ["top"]
    for _ in range(n):
        f = ["and", f, f]
    return f


def vocabulary(**predicates):
    return {"sorts": {"s": {"description": "items"}}, "constants": {},
            "predicates": {name: {"arguments": args, "description": name}
                           for name, args in predicates.items()}}


def fol(profiles=("relational-fol@0",), **predicates):
    return envelope(vocabulary(**(predicates or {"p": ["s"]})), profiles)


def model(domain, **relations):
    return {"complete": True, "domains": {"s": list(domain)}, "constants": {},
            "relations": {name: [list(r) for r in rows] for name, rows in relations.items()}}


def python_values(env, ast, data):
    """Python route evaluation: the document is checked before the model is read."""
    e = Environment(env)
    doc = document_from_data(e, ast)
    m = FiniteModel.from_dict(e, data)
    return [evaluate(e, f, m, trace=False).value for f in doc.formulas]


# --- Defined tables (loop review P2) -------------------------------------------

def defined(body, args=("s",), extra=None):
    predicates = {"p": {"arguments": ["s"], "description": "p"},
                  "d": {"arguments": list(args), "description": "d",
                        "defined": {"arguments": list(args), "body": body}}}
    predicates.update(extra or {})
    return envelope({"sorts": {"s": {"description": "items"}}, "constants": {},
                     "predicates": predicates}, ("definitions@0", "relational-fol@0"))


def defined_three_ways(env, data, python_match):
    with pytest.raises(ResourceLimit, match=python_match):
        FiniteModel.from_dict(Environment(env), data)
    case = {"id": "d", "environment": env, "model": data, "ast": [["top"]]}
    [got] = lean([{**case, "kind": "evaluate"}])
    [other] = rust([case])
    return got, other


def test_defined_table_reproducer_stops_under_the_budget_three_ways():
    """The review's body: 30 universal binders over s = ["b", "a"], ending in ⊤.
    Lean exceeded 15 seconds; it now stops with the budget, in either order."""
    for domain in (["b", "a"], ["a", "b"]):
        got, other = defined_three_ways(defined(nest(30)), model(domain, p=[["b"]]),
                                        "Definition model evaluation budget")
        lean_limit(got, "Definition model evaluation budget")
        rust_limit(other)


def test_defined_table_candidates_are_enumerated_one_at_a_time_three_ways():
    """A million candidate rows are never materialized: ¬⊤ (two units a row)
    stops at the budget, ⊤ at the 100,000-tuple limit, as each row is evaluated."""
    domain = [f"e{i:03d}" for i in range(1000)]
    args = ("s", "s")
    got, other = defined_three_ways(defined(["not", ["top"]], args), model(domain, p=[]),
                                    "Definition model evaluation budget")
    lean_limit(got, "Definition model evaluation budget")
    rust_limit(other)
    got, other = defined_three_ways(defined(["top"], args), model(domain, p=[]), "tuple limit")
    lean_limit(got, "tuple count")
    rust_limit(other)


# --- Relational evaluation and countermodels ---------------------------------

def reviewer_body(depth):
    return ["exists", "s", ["or", ["unary", "p", ["var", 0]], nest(depth)]]


def test_fol_evaluation_budget_three_ways():
    env = fol()
    cases = [(nest(20), None), (nest(18), True), (reviewer_body(19), None)]
    for domain in (["b", "a"], ["a", "b"]):
        data = model(domain, p=[["b"]])
        for formula, expected in cases:
            assert python_values(env, [formula], data) == [expected]
            case = {"id": "e", "environment": env, "model": data, "ast": [formula]}
            [got] = lean([{**case, "kind": "evaluate"}])
            [other] = rust([case])
            if expected is None:
                lean_limit(got, "MAX_EVALUATIONS")
                rust_limit(other)
            else:
                assert got["values"] == [expected] and other["values"] == [expected], (got, other)


def test_fol_countermodel_budget_three_ways():
    env = fol()
    data = model(["b", "a"], p=[["b"]])
    e = Environment(env)
    conclusion = ["not", nest(20)]
    checked = check_countermodel(e, [], formula_from_data(e, conclusion), FiniteModel.from_dict(e, data))
    assert checked.status == "ResourceLimit" and checked.valid is False
    case = {"id": "m", "environment": env, "model": data, "premises": [], "conclusion": conclusion}
    [got] = lean([{**case, "kind": "countermodel"}])
    lean_limit(got, "MAX_EVALUATIONS")
    [other] = rust([case])
    assert other["status"] == "ResourceLimit" and other["valid"] is False, other
    # A false premise stops the check first, in every backend.
    stopped = {**case, "premises": [["bottom"]]}
    [got] = lean([{**stopped, "kind": "countermodel"}])
    [other] = rust([stopped])
    assert got["refutes"] is False and other["valid"] is False and other["status"] == "NotCountermodel"


def test_fol_countermodel_aggregate_covers_the_conclusion_three_ways():
    """Premises [F₁₂] and conclusion F₁₂: 16,382 nodes. Lean counted only the
    premises on the relational route; the conclusion now counts too."""
    env = fol()
    e = Environment(env)
    data = model(["a"], p=[])
    premises, conclusion = [doubling(12)], doubling(12)
    with pytest.raises(ResourceLimit):
        check_countermodel(e, [formula_from_data(e, p) for p in premises],
                           formula_from_data(e, conclusion), FiniteModel.from_dict(e, data))
    case = {"id": "m", "environment": env, "model": data, "premises": premises, "conclusion": conclusion}
    [got] = lean([{**case, "kind": "countermodel"}])
    lean_limit(got, "AST node count")
    [other] = rust([case])
    rust_limit(other)
    [cert] = lean([{"id": "c", "kind": "certificate", "environment": env, "premises": premises,
                    "conclusion": conclusion, "certificate": {}}])
    lean_limit(cert, "AST node count")


def test_formula_limits_precede_the_model_in_every_family():
    """An oversized document with an invalid model is a node-limit error, in
    every route family (Lean used to decode the model first)."""
    bad = {"complete": True, "domains": {"s": ["a", "a"]}, "constants": {}, "relations": {}}
    families = [fol(p=["s"]), fol(("closure@0", "relational-fol@0"), p=["s"]),
                fol(("closure@0", "nary@0", "relational-fol@0"), p=["s"]),
                fol(("order@0", "relational-fol@0"), p=["s"])]
    for env in families:
        bad["relations"] = {"p": []}
        ast = [doubling(13)]
        with pytest.raises(ResourceLimit):
            python_values(env, ast, bad)
        case = {"id": "e", "environment": env, "model": bad, "ast": ast}
        [got] = lean([{**case, "kind": "evaluate"}])
        lean_limit(got)
        [other] = rust([case])
        rust_limit(other)


# --- Order family ------------------------------------------------------------

def test_order_family_evaluation_budget_in_both_domain_orders_three_ways():
    env = fol(("order@0", "relational-fol@0"))
    for domain in (["b", "a"], ["a", "b"]):
        data = model(domain, p=[["b"]])
        for formula, expected in ((reviewer_body(19), None), (nest(18), True)):
            assert python_values(env, [formula], data) == [expected]
            case = {"id": "o", "environment": env, "model": data, "ast": [formula]}
            [got] = lean([{**case, "kind": "evaluate"}])
            [other] = rust([case])
            if expected is None:
                lean_limit(got, "MAX_EVALUATIONS")
                rust_limit(other)
            else:
                assert got["values"] == [True] and other["values"] == [True], (got, other)
        conclusion = ["not", reviewer_body(19)]
        e = Environment(env)
        checked = check_countermodel(e, [], formula_from_data(e, conclusion),
                                     FiniteModel.from_dict(e, data))
        assert checked.status == "ResourceLimit"
        case = {"id": "m", "environment": env, "model": data, "premises": [], "conclusion": conclusion}
        [got] = lean([{**case, "kind": "countermodel"}])
        lean_limit(got, "MAX_EVALUATIONS")
        [other] = rust([{**case, "kind": "countermodel"}])
        rust_limit(other)


def test_nary_family_sorts_domains_before_the_budget():
    """The n-ary family presented domains in input order; the reviewer-style
    formula is UNKNOWN in both orders, as in Python and Rust."""
    env = fol(("closure@0", "nary@0", "relational-fol@0"))
    for domain in (["b", "a"], ["a", "b"]):
        data = model(domain, p=[["b"]])
        assert python_values(env, [reviewer_body(19)], data) == [None]
        case = {"id": "n", "environment": env, "model": data, "ast": [reviewer_body(19)]}
        [got] = lean([{**case, "kind": "evaluate"}])
        lean_limit(got, "MAX_EVALUATIONS")
        [other] = rust([case])
        rust_limit(other)
