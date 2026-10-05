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
import os
from pathlib import Path

import pytest

from conformance.p0 import envelope
from subprocesses import run_cpu_bounded
from ve import Environment, FiniteModel, evaluate
from ve.ast import document_from_data, formula_from_data
from ve.errors import ResourceLimit
from ve.search import check_countermodel

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_conformance"
QUANTITY = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_quantity"
RUST = Path(os.environ.get("VE_RUST_BINARY", str(ROOT / "rust" / "target" / "release" / "ve")))
pytestmark = pytest.mark.skipif(not (LEAN.exists() and RUST.exists()),
                                reason="build ve_conformance (lake build) and the Rust release binary")
# CPU seconds for one batch of limit-busting cases, per backend (tests/subprocesses.py:
# CPU time, unlike elapsed time, does not grow with machine load).
CPU = 30


def run(command, cases):
    # The kernel stops a batch that spends CPU seconds past the limit (a runaway guard: it
    # then exits by a signal, which fails here). What each batch spends is a benchmark
    # against a stored baseline (tools/bench/test_perf.py), not a test criterion.
    completed, cpu = run_cpu_bounded(command, json.dumps(cases), CPU)
    assert completed.returncode in (0, 1), (command[0], completed.returncode, cpu, completed.stderr[:500])
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


# --- Static model limits first; tables of every allowed size -------------------

def order_env():
    return fol(("order@0", "relational-fol@0"), p=["s"], e=["s", "s"])


def limit_cases():
    """Each breaks a static model limit and something checked after it."""
    bad_ids = {"complete": True, "domains": {"s": ["X"] + [f"e{i}" for i in range(1000)]},
               "constants": {}, "relations": {"p": [], "e": []}}
    rows = [["a", "a"]] * 100_001
    dup_domain = {"complete": True, "domains": {"s": ["a", "a"]}, "constants": {},
                  "relations": {"p": [], "e": rows}}
    return [bad_ids, dup_domain]


@pytest.mark.parametrize("profiles", [("relational-fol@0",), ("order@0", "relational-fol@0")])
def test_model_limits_precede_entity_checks_three_ways(profiles):
    """A 1,001-entity domain with an invalid identifier, and 100,001 rows beside
    a duplicate entity: the limit is reported first in every backend."""
    env = fol(profiles, p=["s"], e=["s", "s"])
    for data in limit_cases():
        with pytest.raises(ResourceLimit):
            FiniteModel.from_dict(Environment(env), data)
        case = {"id": "l", "environment": env, "model": data, "ast": [["top"]]}
        [got] = lean([{**case, "kind": "evaluate"}])
        lean_limit(got)
        [other] = rust([case])
        rust_limit(other)


def test_quantity_model_limits_precede_entity_checks_three_ways():
    from tests.test_units_lean_w6a import lean as lean_quantity, quantity
    from tests.test_w6a_review_regressions import raw_environment
    from ve.units import quantity_countermodel
    raw = raw_environment({}, sorts={"s": {"description": "s"}},
                          predicates={"p": {"arguments": ["s"], "description": "p"},
                                      "e": {"arguments": ["s", "s"], "description": "e"}})
    for data in limit_cases():
        with pytest.raises(ResourceLimit):
            quantity_countermodel(Environment(raw), [], quantity(["bottom"]), data)
        case = {"environment": raw, "premises": [], "conclusion": quantity(["bottom"]), "model": data}
        [got] = lean_quantity([{"id": "q", "kind": "countermodel", **case}])
        lean_limit(got)
        [other] = rust([{"id": "q", "kind": "quantity", "mode": "countermodel", **case}])
        rust_limit(other)


def full_table():
    """1,000 entities and 100,000 rows: the largest tables the limits allow."""
    domain = [f"e{i:03d}" for i in range(1000)]
    return {"complete": True, "domains": {"s": domain}, "constants": {},
            "relations": {"p": [], "e": [[domain[k // 1000], domain[k % 1000]] for k in range(100_000)]}}


def test_largest_tables_reach_the_budget_quickly_three_ways():
    """Every atom reads a 100,000-row table in constant time, so the budget, not
    the table, bounds the work (Lean used to scan the rows for each atom)."""
    data = full_table()
    formula = ["forall", "s", ["forall", "s", ["or", ["binary", "e", ["var", 1], ["var", 0]], ["top"]]]]
    exists = ["exists", "s", ["binary", "e", ["var", 0], ["var", 0]]]
    for env in (fol(p=["s"], e=["s", "s"]), order_env()):
        assert python_values(env, [formula, exists], data) == [None, True]
        case = {"id": "t", "environment": env, "model": data, "ast": [exists]}
        [got] = lean([{**case, "kind": "evaluate"}])
        [other] = rust([case])
        assert got["values"] == [True] and other["values"] == [True], (got, other)
        case = {**case, "ast": [formula]}
        [got] = lean([{**case, "kind": "evaluate"}])
        lean_limit(got, "MAX_EVALUATIONS")
        [other] = rust([case])
        rust_limit(other)


def test_largest_tables_on_the_quantity_route_three_ways():
    from tests.test_units_lean_w6a import quantity
    from tests.test_w6a_review_regressions import raw_environment
    from ve.units import quantity_countermodel
    raw = raw_environment({}, sorts={"s": {"description": "s"}},
                          predicates={"p": {"arguments": ["s"], "description": "p"},
                                      "e": {"arguments": ["s", "s"], "description": "e"}})
    conclusion = quantity(["not", ["forall", "s", ["forall", "s",
                                                   ["or", ["binary", "e", ["var", 1], ["var", 0]],
                                                    ["top"]]]]])
    data = full_table()
    with pytest.raises(ResourceLimit, match="MAX_EVALUATIONS"):
        quantity_countermodel(Environment(raw), [], conclusion, data)
    case = {"environment": raw, "premises": [], "conclusion": conclusion, "model": data}
    [got] = run([str(QUANTITY), "-"], [{"id": "q", "kind": "countermodel", **case}])
    lean_limit(got, "MAX_EVALUATIONS")
    [other] = rust([{"id": "q", "kind": "quantity", "mode": "countermodel", **case}])
    rust_limit(other)


# --- Background of a model --------------------------------------------------------

@pytest.mark.parametrize("n,fits", [(447, True), (448, False)])
def test_definition_background_is_metered_at_the_same_size_three_ways(n, fits):
    """Each definition's biconditional is evaluated under its own budget (Python
    `_valid_definitions`): 447 × 447 rows of ⊥ cost 999,493 units, 448 × 448
    cost 1,003,969. Rust skipped this check and Lean ran it unmetered."""
    env = defined(["bottom"], ("s", "s"))
    data = model([f"e{i:03d}" for i in range(n)], p=[])
    case = {"id": "b", "environment": env, "model": data, "ast": [["top"]]}
    [got] = lean([{**case, "kind": "evaluate"}])
    [other] = rust([case])
    if fits:
        assert FiniteModel.from_dict(Environment(env), data).relations["d"] == frozenset()
        assert got["values"] == [True] and other["values"] == [True], (got, other)
    else:
        with pytest.raises(ResourceLimit, match="Definition background evaluation budget"):
            FiniteModel.from_dict(Environment(env), data)
        lean_limit(got, "Definition background evaluation budget")
        rust_limit(other)
        assert "Definition background evaluation budget" in other["error"]["message"]


def test_definitions_share_one_construction_budget_three_ways():
    """Three unary definitions, each ∀y:t ⊤ over 496 entities of t: each fits its
    own Background budget (999,001), two tables cost 994,000 together, and the
    third exhausts the shared construction budget."""
    def env(names):
        body = ["forall", "t", ["top"]]
        predicates = {name: {"arguments": ["s"], "description": name,
                             "defined": {"arguments": ["s"], "body": body}} for name in names}
        return envelope({"sorts": {"s": {"description": "s"}, "t": {"description": "t"}},
                         "constants": {}, "predicates": predicates},
                        ("definitions@0", "relational-fol@0"))
    data = {"complete": True, "domains": {"s": [f"e{i:03d}" for i in range(1000)],
                                          "t": [f"t{i:03d}" for i in range(496)]},
            "constants": {}, "relations": {}}
    two, three = env(["d1", "d2"]), env(["d1", "d2", "d3"])
    FiniteModel.from_dict(Environment(two), data)
    [got] = lean([{"id": "two", "kind": "evaluate", "environment": two, "model": data, "ast": [["top"]]}])
    [other] = rust([{"id": "two", "environment": two, "model": data, "ast": [["top"]]}])
    assert got["values"] == [True] and other["values"] == [True], (got, other)
    got, other = defined_three_ways(three, data, "Definition model evaluation budget")
    lean_limit(got, "Definition model evaluation budget")
    rust_limit(other)


def test_supplied_tuples_count_toward_the_defined_tuple_limit_three_ways():
    """The limit is shared with the supplied tables: 314 × 314 rows of ⊤ fit
    beside 10 supplied rows, 317 × 317 do not."""
    for size, fits in ((314, True), (317, False)):
        domain = [f"e{i:03d}" for i in range(size)]
        data = model(domain, p=[[e] for e in domain[:10]])
        env = defined(["top"], ("s", "s"))
        case = {"id": "d", "environment": env, "model": data, "ast": [["top"]]}
        [got] = lean([{**case, "kind": "evaluate"}])
        [other] = rust([case])
        if fits:
            FiniteModel.from_dict(Environment(env), data)
            assert got["status"] == "ok" and got["values"] == [True], got
            assert other["status"] == "ok" and other["values"] == [True], other
        else:
            with pytest.raises(ResourceLimit, match="tuple limit"):
                FiniteModel.from_dict(Environment(env), data)
            lean_limit(got, "tuple count")
            rust_limit(other)


def flags_env():
    return envelope({"sorts": {"s": {"description": "s"}, "t": {"description": "t"}}, "constants": {},
                     "predicates": {"f": {"arguments": ["s", "t"], "description": "f",
                                          "functional": True, "total": True}}},
                    ("data@0", "relational-fol@0"))


def test_flags_are_checked_in_one_pass_three_ways():
    """A functional, total table over 1,000 × 1,000 entities (Lean evaluated the
    generated premise, three nested quantifiers, for each flagged table)."""
    from ve.errors import InvalidModel
    s = [f"s{i:03d}" for i in range(1000)]
    t = [f"t{i:03d}" for i in range(1000)]
    rows = [[s[i], t[(7 * i) % 1000]] for i in range(1000)]
    good = {"complete": True, "domains": {"s": s, "t": t}, "constants": {}, "relations": {"f": rows}}
    two = {**good, "relations": {"f": rows + [[s[0], t[1]]]}}
    partial = {**good, "relations": {"f": rows[1:]}}
    env = flags_env()
    FiniteModel.from_dict(Environment(env), good)
    [got] = lean([{"id": "g", "kind": "evaluate", "environment": env, "model": good, "ast": [["top"]]}])
    [other] = rust([{"id": "g", "environment": env, "model": good, "ast": [["top"]]}])
    assert got["values"] == [True] and other["values"] == [True], (got, other)
    for data in (two, partial):
        with pytest.raises(InvalidModel) as exc:
            FiniteModel.from_dict(Environment(env), data)
        assert exc.value.generator == "flags"
        [got] = lean([{"id": "b", "kind": "evaluate", "environment": env, "model": data, "ast": [["top"]]}])
        assert got["status"] == "error" and got["error"].startswith("InvalidModel(flags)"), got
        [other] = rust([{"id": "b", "environment": env, "model": data, "ast": [["top"]]}])
        assert other["error"]["code"] == "InvalidModel" and "flags" in other["error"]["message"], other


# --- Closure families ----------------------------------------------------------

CLOSURE = ("closure@0", "relational-fol@0")
NARY = ("closure@0", "nary@0", "relational-fol@0")


def closure_env(profiles):
    return envelope({"sorts": {"s": {"description": "items"}},
                     "predicates": {"e": {"arguments": ["s", "s"], "description": "e"}},
                     "constants": {"a": {"sort": "s", "description": "a"},
                                   "b": {"sort": "s", "description": "b"}}}, profiles)


def chain(n, reverse=False):
    names = [f"n{i:04d}" for i in range(n)]
    domain = names[::-1] if reverse else names
    return {"complete": True, "domains": {"s": domain}, "constants": {"a": names[0], "b": names[-1]},
            "relations": {"e": [[names[i], names[i + 1]] for i in range(n - 1)]}}


NAMED = ["reach", "plus", ["named", "e"], ["const", "a"], ["const", "b"]]
BODY = ["reach", "plus", ["body", "s", ["binary", "e", ["var", 1], ["var", 0]]],
        ["const", "a"], ["const", "b"]]


def python_status(env, formula, data):
    e = Environment(env)
    result = evaluate(e, formula_from_data(e, formula), FiniteModel.from_dict(e, data), trace=False)
    return result.value, result.evaluations


def closure_agrees(env, formula, data):
    value, work = python_status(env, formula, data)
    case = {"id": "r", "environment": env, "model": data, "ast": [formula]}
    [got] = lean([{**case, "kind": "evaluate"}])
    [other] = rust([case])
    if value is None:
        lean_limit(got, "MAX_EVALUATIONS")
        rust_limit(other)
    else:
        assert got["status"] == "ok" and got["values"] == [value], got
        assert other["status"] == "ok" and other["values"] == [value], other
    return value, work


@pytest.mark.parametrize("profiles", [CLOSURE, NARY])
def test_named_closure_charges_meet_the_budget_at_the_same_chain_length(profiles):
    """A named chain costs 1 + (n − 1) rows + n² pivot visits + the
    incoming × outgoing pairs: 816 entities fit the budget, 817 do not."""
    env = closure_env(profiles)
    assert closure_agrees(env, NAMED, chain(816)) == (True, 998377)
    assert closure_agrees(env, NAMED, chain(817))[0] is None
    # Domain order does not change the charges: named pivots are sorted endpoints.
    assert closure_agrees(env, NAMED, chain(816, reverse=True)) == (True, 998377)


@pytest.mark.parametrize("profiles", [CLOSURE, NARY])
def test_body_closure_charges_meet_the_budget_at_the_same_domain_size(profiles):
    env = closure_env(profiles)
    fits = [n for n in (600, 610, 620, 630, 640) if python_status(env, BODY, chain(n))[0] is not None]
    boundary = max(fits)
    assert boundary < 640
    assert closure_agrees(env, BODY, chain(boundary))[0] is True
    assert closure_agrees(env, BODY, chain(boundary + 10))[0] is None
    # Body pivots are the whole sort, in sorted order, however the domain is sent.
    assert closure_agrees(env, BODY, chain(boundary, reverse=True))[0] is True


@pytest.mark.parametrize("profiles", [CLOSURE, NARY])
def test_closure_cache_is_charged_once_per_edge_and_bindings(profiles):
    """A repeated closure under the same bindings is charged once; under a
    binder its key includes the binding, so it is charged per entity."""
    env = closure_env(profiles)
    data = chain(700)
    value, work = closure_agrees(env, ["and", NAMED, NAMED], data)
    assert value is True and work == 734651 + 2
    assert closure_agrees(env, ["exists", "s", ["not", NAMED]], data)[0] is None


@pytest.mark.parametrize("profiles", [CLOSURE, NARY])
def test_closure_countermodel_budget_three_ways(profiles):
    env = closure_env(profiles)
    data = chain(817)
    e = Environment(env)
    checked = check_countermodel(e, [], formula_from_data(e, ["not", NAMED]), FiniteModel.from_dict(e, data))
    assert checked.status == "ResourceLimit"
    case = {"id": "m", "environment": env, "model": data, "premises": [], "conclusion": ["not", NAMED]}
    [got] = lean([{**case, "kind": "countermodel"}])
    lean_limit(got, "MAX_EVALUATIONS")
    [other] = rust([case])
    assert other["status"] == "ResourceLimit" and other["valid"] is False, other
    # On 816 entities the closure fits (1 + 998,377 units) and refutes ¬reach.
    fitting = {**case, "model": chain(816)}
    e816 = FiniteModel.from_dict(e, chain(816))
    assert check_countermodel(e, [], formula_from_data(e, ["not", NAMED]), e816).status == "Valid"
    [got] = lean([{**fitting, "kind": "countermodel"}])
    [other] = rust([fitting])
    assert got["refutes"] is True and other["valid"] is True and other["status"] == "Valid", (got, other)
