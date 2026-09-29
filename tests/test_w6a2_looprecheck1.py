"""W6a loop recheck (round 2, recheck 1) regressions: static limits, three ways.

1. A definition's generated biconditional has the AST limits of any formula.
   Python checks `premise(definition)` after each body, in dependency order;
   Lean and Rust checked only the body, so a body of 8,191 nodes (a premise of
   16,390) or of 61 binders (a premise 65 levels deep) was accepted there.
2. Python's aggregate premises-plus-conclusion count skipped Reach body edges,
   so three 4,099-node closure premises counted as 13 nodes.
3. Node limits come before typing. Python's decoder counts nodes in preorder
   before any node is typed; Lean typed first (and did not count admission
   claims or definition bodies at all), and Rust's order route typed while it
   counted, so an unbound variable ahead of 16,383 nodes was ill-typed there.
"""
from __future__ import annotations

import pytest

from conformance.p0 import envelope
from tests.test_w6a_route_limits import LEAN, RUST, doubling, lean, lean_limit, nest, rust, rust_limit
from ve import Environment, FiniteModel
from ve.ast import _Checker, document_from_data, formula_from_data
from ve.errors import ResourceLimit, VEError
from ve.search import _node_count, check_countermodel, find_countermodel, find_distinguishing_model

pytestmark = pytest.mark.skipif(not (LEAN.exists() and RUST.exists()),
                                reason="build ve_conformance (lake build) and the Rust release binary")

VAR0 = ["var", 0]
UNBOUND = ["eq", VAR0, VAR0]


def sized(n):
    """A formula of exactly n nodes and logarithmic depth."""
    if n == 1:
        return ["top"]
    if n == 2:
        return ["not", ["top"]]
    left = (n - 1) // 2
    return ["and", sized(left), sized(n - 1 - left)]


def model(domain, **relations):
    return {"complete": True, "domains": {"s": list(domain)}, "constants": {},
            "relations": {name: [list(r) for r in rows] for name, rows in relations.items()}}


def not_limit(got):
    assert got["status"] == "error" and not got["error"].startswith("ResourceLimit"), got


def rust_not_limit(got):
    assert got["status"] == "error" and got["error"]["code"] != "ResourceLimit", got


# --- 2. Python's aggregate count covers Reach bodies ----------------------------

def closure_env(profiles):
    predicates = {"p": {"arguments": ["s"], "description": "p"}}
    if "nary@0" in profiles:
        predicates["r"] = {"arguments": ["s", "s", "s"], "description": "r"}
    return envelope({"sorts": {"s": {"description": "items"}}, "constants": {},
                     "predicates": predicates}, profiles)


CLOSURE_PROFILES = [("closure@0", "relational-fol@0"), ("closure@0", "nary@0", "relational-fol@0")]


def reach_premise(n=11):
    return ["exists", "s", ["reach", "plus", ["body", "s", doubling(n)], VAR0, VAR0]]


@pytest.mark.parametrize("profiles", CLOSURE_PROFILES)
def test_reviewer_reach_aggregate_reproducer_three_ways(profiles):
    """[P, P, P] ⊢ ⊥ with P = ∃s. reach⁺(body F₁₁)(x, x): 12,298 nodes."""
    env = closure_env(profiles)
    e = Environment(env)
    data = model(["a"], p=[], **({"r": []} if "nary@0" in profiles else {}))
    premises = [reach_premise()] * 3
    ps = [formula_from_data(e, p) for p in premises]
    bottom = formula_from_data(e, ["bottom"])
    assert sum(_node_count(f) for f in (*ps, bottom)) > 10_000
    with pytest.raises(ResourceLimit, match="aggregate"):
        check_countermodel(e, ps, bottom, FiniteModel.from_dict(e, data))
    with pytest.raises(ResourceLimit, match="aggregate"):
        find_countermodel(e, ps, bottom, max_domain_size=1)
    with pytest.raises(ResourceLimit, match="aggregate"):
        find_distinguishing_model(e, ps[0], formula_from_data(e, ["and", premises[0], premises[0]]))
    case = {"id": "m", "environment": env, "model": data, "premises": premises, "conclusion": ["bottom"]}
    [got] = lean([{**case, "kind": "countermodel"}])
    lean_limit(got)
    [other] = rust([case])
    rust_limit(other)
    # Two of them fit (8,199 nodes): each premise holds and ⊥ fails, everywhere.
    fits = {**case, "premises": premises[:2]}
    assert check_countermodel(e, ps[:2], bottom, FiniteModel.from_dict(e, data)).status == "Valid"
    [got] = lean([{**fits, "kind": "countermodel"}])
    assert got["status"] == "ok" and got["refutes"] is True, got
    [other] = rust([fits])
    assert other["status"] == "Valid", other


@pytest.mark.parametrize("profiles", CLOSURE_PROFILES + [("order@0", "relational-fol@0")])
def test_node_count_is_the_checkers_count(profiles):
    """The search counter and the type checker count the same nodes, for every
    constructor, including nested Reach bodies, n-ary atoms and arithmetic."""
    env = Environment(closure_env(profiles) if "order@0" not in profiles else envelope(
        {"sorts": {"s": {"description": "items"}},
         "constants": {"k": {"sort": "$int", "description": "k"}},
         "predicates": {"p": {"arguments": ["s"], "description": "p"},
                        "q": {"arguments": ["s", "s"], "description": "q"}}}, profiles))
    if "order@0" in profiles:
        term = ["add", ["scale", "2", ["const", "k"]], ["num", "3"]]
        formulas = [["lt", term, ["num", "-1"]],
                    ["forall", "s", ["or", ["le", ["const", "k"], term], ["unary", "p", VAR0]]],
                    ["exists", "s", ["exists", "s", ["binary", "q", VAR0, ["var", 1]]]]]
    else:
        inner = ["reach", "star", ["body", "s", ["unary", "p", VAR0]], VAR0, ["var", 1]]
        formulas = [reach_premise(3),
                    ["forall", "s", ["reach", "plus", ["body", "s", ["and", inner, ["not", ["top"]]]],
                                     VAR0, VAR0]],
                    ["exists", "s", ["reach", "plus", ["body", "s", ["eq", VAR0, ["var", 1]]],
                                     VAR0, VAR0]]]
        if "nary@0" in profiles:
            formulas.append(["forall", "s", ["atom", "r", [VAR0, VAR0, VAR0]]])
    for data in formulas:
        formula = formula_from_data(env, data)
        checker = _Checker(env)
        checker.formula(formula)
        assert _node_count(formula) == checker.nodes, data
