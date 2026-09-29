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


# --- 1. Definition premises -----------------------------------------------------

def defined(definitions):
    """definitions: name -> (arguments, body)."""
    predicates = {"p": {"arguments": ["s"], "description": "p"}}
    for name, (args, body) in definitions.items():
        predicates[name] = {"arguments": list(args), "description": name,
                            "defined": {"arguments": list(args), "body": body}}
    return envelope({"sorts": {"s": {"description": "items"}}, "constants": {},
                     "predicates": predicates}, ("definitions@0", "relational-fol@0"))


def definition_outcome(env, data):
    """Python's exception (None when accepted), Lean's and Rust's results for ⊤."""
    try:
        FiniteModel.from_dict(Environment(env), data)
        python = None
    except VEError as exc:
        python = exc
    case = {"id": "d", "environment": env, "model": data, "ast": [["top"]]}
    [got] = lean([{**case, "kind": "evaluate"}])
    [other] = rust([case])
    return python, got, other


def assert_limited(env, data=None):
    python, got, other = definition_outcome(env, data or model(["a"], p=[]))
    assert isinstance(python, ResourceLimit), python
    lean_limit(got)
    rust_limit(other)


def assert_accepted(env, data=None):
    python, got, other = definition_outcome(env, data or model(["a"], p=[]))
    assert python is None, python
    assert got["status"] == "ok" and got["values"] == [True], got
    assert other["status"] == "ok", other


def test_reviewer_premise_node_reproducer_three_ways():
    """Body F₁₂ (8,191 nodes): the premise has 16,390 nodes."""
    assert_limited(defined({"d": (["s"], doubling(12))}))


def test_reviewer_premise_depth_reproducer_three_ways():
    assert_limited(defined({"d": (["s"], nest(62))}))


@pytest.mark.parametrize("args", [["s"], ["s", "s"]])
def test_premise_node_boundary_three_ways(args):
    """Premise nodes: one binder per argument, ∧, two →, two heads (1 + arity
    nodes each) and the body twice."""
    fixed = len(args) + 3 + 2 * (1 + len(args))
    largest = (10_000 - fixed) // 2
    assert_accepted(defined({"d": (args, sized(largest))}))
    assert_limited(defined({"d": (args, sized(largest + 1))}))


@pytest.mark.parametrize("args", [["s"], ["s", "s"]])
def test_premise_depth_boundary_three_ways(args):
    """The body sits under the binders, ∧ and →; a leaf is one level."""
    largest = 64 - len(args) - 2 - 1
    assert_accepted(defined({"d": (args, nest(largest))}))
    assert_limited(defined({"d": (args, nest(largest + 1))}))


def test_premise_limit_is_checked_in_dependency_order_three_ways():
    """Python checks each body, then its premise, one definition at a time: an
    oversized premise below an ill-typed body is the limit, and an ill-typed
    body below an oversized premise is the typing error."""
    big = doubling(12)
    bad = ["and", ["unary", "a", VAR0], ["unary", "p", ["var", 7]]]
    assert_limited(defined({"a": (["s"], big), "b": (["s"], bad)}))
    python, got, other = definition_outcome(
        defined({"a": (["s"], ["unary", "p", ["var", 7]]), "b": (["s"], ["and", ["unary", "a", VAR0], big])}),
        model(["a"], p=[]))
    assert python is not None and not isinstance(python, ResourceLimit), python
    not_limit(got)
    rust_not_limit(other)


def test_body_limits_precede_its_typing_three_ways():
    """A body is decoded, within its own limits, before it is typed."""
    assert_limited(defined({"d": (["s"], ["and", ["unary", "p", ["var", 5]], doubling(13)])}))


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


# --- 3. Node limits before typing ----------------------------------------------

def families():
    base = {"sorts": {"s": {"description": "items"}}, "constants": {},
            "predicates": {"p": {"arguments": ["s"], "description": "p"}}}
    nary = {**base, "predicates": {**base["predicates"],
                                   "r": {"arguments": ["s", "s", "s"], "description": "r"}}}
    return {"fol": envelope(base, ("relational-fol@0",)),
            "data": envelope(base, ("data@0", "relational-fol@0")),
            "closure": envelope(base, ("closure@0", "relational-fol@0")),
            "nary": envelope(nary, ("closure@0", "nary@0", "relational-fol@0")),
            "order": envelope(base, ("order@0", "relational-fol@0"))}


def python_document(env, formulas):
    """Python's wire reading: one shared decoder, then typing (conformance fixtures
    decode premises and conclusion as one document)."""
    try:
        document_from_data(Environment(env), formulas)
    except VEError as exc:
        return exc
    return None


def route_model(env):
    domains = {"s": ["a"]}
    relations = {name: [] for name in env["vocabulary"]["predicates"]}
    return {"complete": True, "domains": domains, "constants": {}, "relations": relations}


# Ill-typed (or unsupported) formulas that come first in preorder.
FIRST = {"unbound": UNBOUND, "unknown": ["unary", "nope", ["var", 0]],
         "binder": ["forall", "nope", ["top"]], "string": ["forall", "$string", ["top"]],
         "comparison": ["lt", ["num", "1"], ["num", "2"]]}


@pytest.mark.parametrize("family", ["fol", "data", "closure", "nary", "order"])
@pytest.mark.parametrize("first", sorted(FIRST))
def test_node_limit_precedes_typing_in_documents_three_ways(family, first):
    env = families()[family]
    document = [["and", FIRST[first], doubling(13)]]
    assert isinstance(python_document(env, document), ResourceLimit)
    case = {"id": "e", "environment": env, "model": route_model(env), "ast": document}
    [got] = lean([{**case, "kind": "evaluate"}])
    lean_limit(got, "AST node count")
    [other] = rust([case])
    rust_limit(other)


@pytest.mark.parametrize("family", ["fol", "data", "closure", "nary", "order"])
def test_aggregate_limit_precedes_typing_in_countermodels_three_ways(family):
    """An ill-typed first premise; F₁₂ as a premise and as the conclusion."""
    env = families()[family]
    premises, conclusion = [UNBOUND, doubling(12)], doubling(12)
    assert isinstance(python_document(env, [*premises, conclusion]), ResourceLimit)
    case = {"id": "m", "environment": env, "model": route_model(env), "premises": premises,
            "conclusion": conclusion}
    [got] = lean([{**case, "kind": "countermodel"}])
    lean_limit(got, "AST node count")
    [other] = rust([{**case, "kind": "countermodel"} if family == "order" else case])
    rust_limit(other)
    if family != "order":
        [cert] = lean([{**case, "kind": "certificate", "certificate": {}}])
        lean_limit(cert, "AST node count")


@pytest.mark.parametrize("family", ["fol", "closure", "nary", "order"])
def test_limit_and_syntax_errors_keep_preorder_three_ways(family):
    """A malformed node reached before the limit is the syntax error; one
    reached after it is the limit."""
    env = families()[family]
    after = [["and", doubling(13), ["bad"]]]
    before = [["and", ["bad"], doubling(13)]]
    assert isinstance(python_document(env, after), ResourceLimit)
    python = python_document(env, before)
    assert python is not None and not isinstance(python, ResourceLimit), python
    for document, limited in ((after, True), (before, False)):
        case = {"id": "e", "environment": env, "model": route_model(env), "ast": document}
        [got] = lean([{**case, "kind": "evaluate"}])
        [other] = rust([case])
        if limited:
            lean_limit(got, "AST node count")
            rust_limit(other)
        else:
            not_limit(got)
            rust_not_limit(other)


def test_depth_limit_precedes_typing_three_ways():
    env = families()["fol"]
    document = [["and", UNBOUND, nest(70)]]
    assert isinstance(python_document(env, document), ResourceLimit)
    case = {"id": "e", "environment": env, "model": route_model(env), "ast": document}
    [got] = lean([{**case, "kind": "evaluate"}])
    lean_limit(got)
    [other] = rust([case])
    rust_limit(other)


@pytest.mark.parametrize("formula", [["and", UNBOUND, doubling(13)], doubling(14)])
def test_admission_claims_have_their_own_limits(formula):
    """Each claim is decoded within its own limits before it is typed; Lean did
    not count claims at all, so a well-typed 32,767-node claim was accepted."""
    from ve.admission import admit_document
    env = families()["fol"]
    document = {"units": [], "open_terms": ["t"],
                "graph": {"root": "root", "nodes": [{"name": "root", "ast": formula, "label": "open:t"}]}}
    with pytest.raises(ResourceLimit):
        admit_document(Environment(env), document)
    [got] = lean([{"id": "a", "kind": "admission", "environment": env, "document": document}])
    lean_limit(got)
