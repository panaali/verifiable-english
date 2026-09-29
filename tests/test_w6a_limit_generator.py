"""W6a limits directive, item 3: a differential limit-busting generator.

Seeded families of inputs that break a limit: doubling conjunctions (a
statement's nodes, the premises-plus-conclusion aggregate), deep binder stacks
(the depth limit, and stacks within it whose evaluation exceeds the budget),
and large domains (the domain limit, and full domains under nested binders),
across the quantity runner and every route family, with both reproducers from
the W6a loop review. Python, Lean and Rust must each report `ResourceLimit`,
and each backend must finish its batch within a wall-time bound.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import random
import subprocess
import time

import pytest

from conformance.p0 import envelope
from ve import Environment, FiniteModel, evaluate
from ve.ast import document_from_data, formula_from_data
from ve.errors import ResourceLimit
from ve.search import check_countermodel
from ve.units import elaborate_quantity, erased_environment, quantity_countermodel

ROOT = Path(__file__).resolve().parents[1]
QUANTITY = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_quantity"
ROUTE = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_conformance"
RUST = Path(os.environ.get("VE_RUST_BINARY", str(ROOT / "rust" / "target" / "release" / "ve")))
pytestmark = pytest.mark.skipif(not (QUANTITY.exists() and ROUTE.exists() and RUST.exists()),
                                reason="build the Lean runners and the Rust release binary")
SEEDS = range(3)
WALL = 60  # seconds per backend per batch


def doubling(n):
    f = ["top"]
    for _ in range(n):
        f = ["and", f, f]
    return f


def nest(depth, sort, body=None, quantifier="forall"):
    body = body or ["top"]
    for _ in range(depth):
        body = [quantifier, sort, body]
    return body


def entities(n, prefix="e"):
    return [f"{prefix}{i:04d}" for i in range(n)]


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def w6_env():
    return {"language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "an item"}}, "constants": {},
                           "predicates": {"p": {"arguments": ["item"], "description": "p"},
                                          "r": {"arguments": ["item", "item"], "description": "r"}}},
            "unit_schema": "ve-units@1", "units": {}}


def w6_model(domain, p=(), r=()):
    return {"complete": True, "domains": {"item": list(domain)}, "constants": {},
            "relations": {"p": [[x] for x in p], "r": [list(x) for x in r]}}


def route_env(profiles, extra=None):
    predicates = {"p": {"arguments": ["s"], "description": "p"},
                  "e": {"arguments": ["s", "s"], "description": "e"}}
    predicates.update(extra or {})
    constants = {"a": {"sort": "s", "description": "a"}, "b": {"sort": "s", "description": "b"}}
    return envelope({"sorts": {"s": {"description": "s"}}, "constants": constants,
                     "predicates": predicates}, profiles)


def route_model(domain, p=(), e=()):
    domain = list(domain)
    return {"complete": True, "domains": {"s": domain}, "constants": {"a": domain[0], "b": domain[-1]},
            "relations": {"p": [[x] for x in p], "e": [list(x) for x in e]}}


# --- Python oracles: True when Python reports ResourceLimit -------------------

def py_quantity_value(raw, formula, data):
    try:
        env = Environment(raw)
        _, core = elaborate_quantity(env, q(formula))
        target = erased_environment(env)
        result = evaluate(target, formula_from_data(target, core), FiniteModel.from_dict(target, data),
                          trace=False)
    except ResourceLimit:
        return True
    return result.value is None


def py_quantity_countermodel(raw, premises, conclusion, data):
    try:
        quantity_countermodel(Environment(raw), [q(p) for p in premises], q(conclusion), data)
    except ResourceLimit:
        return True
    return False


def py_route_evaluate(env, ast, data):
    try:
        e = Environment(env)
        doc = document_from_data(e, ast)
        m = FiniteModel.from_dict(e, data)
        return any(evaluate(e, f, m, trace=False).value is None for f in doc.formulas)
    except ResourceLimit:
        return True


def py_route_countermodel(env, premises, conclusion, data):
    try:
        e = Environment(env)
        checked = check_countermodel(e, [formula_from_data(e, p) for p in premises],
                                     formula_from_data(e, conclusion), FiniteModel.from_dict(e, data))
    except ResourceLimit:
        return True
    return checked.status == "ResourceLimit"


# --- Generated cases ------------------------------------------------------------

def generate(seed):
    """(name, python verdict thunk, Lean runner, Lean case, Rust case)."""
    rng = random.Random(seed)
    cases = []

    def quantity_value(name, formula, data):
        raw = w6_env()
        cases.append((name, lambda: py_quantity_value(raw, formula, data), "quantity",
                      {"id": name, "environment": raw, "quantity": q(formula), "model": data},
                      {"id": name, "kind": "quantity", "environment": raw, "quantity": q(formula),
                       "model": data}))

    def quantity_countermodel_case(name, premises, conclusion, data):
        raw = w6_env()
        body = {"environment": raw, "premises": [q(p) for p in premises], "conclusion": q(conclusion),
                "model": data}
        cases.append((name, lambda: py_quantity_countermodel(raw, premises, conclusion, data), "quantity",
                      {"id": name, "kind": "countermodel", **body},
                      {"id": name, "kind": "quantity", "mode": "countermodel", **body}))

    def route_evaluate(name, env, ast, data):
        cases.append((name, lambda: py_route_evaluate(env, ast, data), "route",
                      {"id": name, "kind": "evaluate", "environment": env, "model": data, "ast": ast},
                      {"id": name, "environment": env, "model": data, "ast": ast}))

    def route_countermodel(name, env, premises, conclusion, data):
        order = "order@0" in env["profiles"]
        body = {"environment": env, "model": data, "premises": premises, "conclusion": conclusion}
        cases.append((name, lambda: py_route_countermodel(env, premises, conclusion, data), "route",
                      {"id": name, "kind": "countermodel", **body},
                      {"id": name, **({"kind": "countermodel"} if order else {}), **body}))

    small = entities(2)
    # Doubling conjunctions: one statement over 10,000 nodes, or an aggregate.
    n = rng.choice([13, 14])
    quantity_value(f"q-nodes-{n}", doubling(n), w6_model(small))
    a, b = rng.choice([(12, 12), (13, 1), (12, 11)])
    if 2 ** (a + 1) + 2 ** (b + 1) - 1 > 10000:
        quantity_countermodel_case(f"q-aggregate-{a}-{b}", [doubling(a), doubling(b)], ["bottom"],
                                   w6_model(small))
    quantity_countermodel_case("reproducer-1", [doubling(12), doubling(12)], ["bottom"], w6_model(small))
    for profiles in (("relational-fol@0",), ("order@0", "relational-fol@0"),
                     ("closure@0", "relational-fol@0"), ("closure@0", "nary@0", "relational-fol@0")):
        tag = "-".join(p.split("@")[0] for p in profiles)
        env = route_env(profiles)
        route_evaluate(f"r-nodes-{tag}", env, [doubling(n)], route_model(small))
        route_countermodel(f"r-aggregate-{tag}", env, [doubling(12)], doubling(12), route_model(small))
        # Deep binder stacks: past the depth limit, and within it past the budget.
        depth = rng.randint(65, 80)
        route_evaluate(f"r-depth-{depth}-{tag}", env, [nest(depth, "s")], route_model(small))
        k = rng.randint(20, 24)
        route_evaluate(f"r-binders-{k}-{tag}", env, [nest(k, "s")], route_model(small))
        route_countermodel(f"r-binders-cm-{k}-{tag}", env, [], ["not", nest(k, "s")], route_model(small))
        # Large domains: past the domain limit, and full under nested binders.
        big = rng.randint(1001, 1100)
        route_evaluate(f"r-domain-{big}-{tag}", env, [["top"]], route_model(entities(big)))
        full = nest(2, "s", ["or", ["binary", "e", ["var", 1], ["var", 0]], ["top"]])
        route_evaluate(f"r-full-domain-{tag}", env, [full], route_model(entities(1000)))
    depth = rng.randint(65, 80)
    quantity_value(f"q-depth-{depth}", nest(depth, "item"), w6_model(small))
    k = rng.randint(20, 24)
    quantity_value(f"q-binders-{k}", nest(k, "item"), w6_model(small))
    quantity_countermodel_case(f"q-binders-cm-{k}", [], ["not", nest(k, "item")], w6_model(small))
    quantity_value(f"q-domain-{rng.randint(1001, 1100)}", ["top"], w6_model(entities(1001)))
    quantity_value("q-full-domain",
                   nest(2, "item", ["or", ["binary", "r", ["var", 1], ["var", 0]], ["top"]]),
                   w6_model(entities(1000)))
    # Order-sensitive budget (loop fix 3) in both orders.
    body = ["or", ["unary", "p", ["var", 0]], nest(19, "item")]
    for domain in (["b", "a"], ["a", "b"]):
        quantity_value(f"q-order-{''.join(domain)}", ["exists", "item", body], w6_model(domain, p=["b"]))
    # Reproducer 2: a defined table of 30 binders over two entities.
    defined = route_env(("definitions@0", "relational-fol@0"),
                        {"d": {"arguments": ["s"], "description": "d",
                               "defined": {"arguments": ["s"], "body": nest(30, "s")}}})
    for domain in (["b", "a"], ["a", "b"]):
        route_evaluate(f"reproducer-2-{''.join(domain)}", defined, [["top"]],
                       route_model(domain, p=["b"]))
    # Loop recheck (round 2): a definition's generated biconditional past the
    # node or depth limit, Reach bodies in the aggregate, limits before typing.
    for name, body in ((f"premise-nodes-{n - 1}", doubling(n - 1)),
                       (f"premise-depth-{(k := rng.randint(61, 63))}", nest(k, "s"))):
        env = route_env(("definitions@0", "relational-fol@0"),
                        {"d": {"arguments": ["s"], "description": "d",
                               "defined": {"arguments": ["s"], "body": body}}})
        route_evaluate(name, env, [["top"]], route_model(small))
    reach = ["exists", "s", ["reach", "plus", ["body", "s", doubling(11)], ["var", 0], ["var", 0]]]
    for profiles in (("closure@0", "relational-fol@0"), ("closure@0", "nary@0", "relational-fol@0")):
        route_countermodel(f"reach-aggregate-{len(profiles)}", route_env(profiles), [reach] * 3, ["bottom"],
                           route_model(small))
    unbound = ["eq", ["var", 0], ["var", 0]]
    for profiles in (("relational-fol@0",), ("order@0", "relational-fol@0"),
                     ("closure@0", "relational-fol@0"), ("closure@0", "nary@0", "relational-fol@0")):
        tag = "-".join(p.split("@")[0] for p in profiles)
        route_evaluate(f"typed-after-limit-{tag}", route_env(profiles), [["and", unbound, doubling(n)]],
                       route_model(small))
    # A named closure one entity past its budget.
    chain = entities(817)
    closure = route_env(("closure@0", "relational-fol@0"))
    route_evaluate("r-closure-817", closure,
                   [["reach", "plus", ["named", "e"], ["const", "a"], ["const", "b"]]],
                   route_model(chain, e=zip(chain, chain[1:])))
    return cases


def run(command, cases):
    start = time.monotonic()
    completed = subprocess.run(command, input=json.dumps(cases), text=True, capture_output=True,
                               timeout=WALL * 4)
    elapsed = time.monotonic() - start
    assert completed.returncode in (0, 1), completed.stderr[:500]
    results = json.loads(completed.stdout)
    assert len(results) == len(cases)
    return results, elapsed


@pytest.mark.parametrize("seed", SEEDS)
def test_every_backend_reports_resource_limit_in_bounded_time(seed):
    cases = generate(seed)
    assert len({c[0] for c in cases}) == len(cases)
    start = time.monotonic()
    python = {name: verdict() for name, verdict, _, _, _ in cases}
    assert time.monotonic() - start < WALL * 2
    assert all(python.values()), [n for n, v in python.items() if not v]
    quantity, q_time = run([str(QUANTITY), "-"], [c[3] for c in cases if c[2] == "quantity"])
    route, r_time = run([str(ROUTE), "route", "-"], [c[3] for c in cases if c[2] == "route"])
    assert q_time < WALL and r_time < WALL, (q_time, r_time)
    for got in quantity + route:
        assert got["status"] == "error" and got["error"].startswith("ResourceLimit"), got
    rust, rust_time = run([str(RUST), "conformance"], [c[4] for c in cases])
    assert rust_time < WALL, rust_time
    for got in rust:
        limited = (got.get("status") == "error" and got["error"]["code"] == "ResourceLimit") or \
            got.get("status") == "ResourceLimit"
        assert limited, got
