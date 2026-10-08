"""W6a limits directive, item 3: a differential limit-busting generator.

Seeded families of inputs that break a limit: doubling conjunctions (a
statement's nodes, the premises-plus-conclusion aggregate), deep binder stacks
(the depth limit, and stacks within it whose evaluation exceeds the budget),
and large domains (the domain limit, and full domains under nested binders),
across the quantity runner and every route family, with both reproducers from
the W6a loop review. Python, Lean and Rust must each report `ResourceLimit`,
and the work each spends is bounded by measures that do not grow with machine
load: Python's own evaluation units, and a kernel limit on the CPU seconds of
each Lean and Rust batch (neither reports its units), which stops a runaway.
What each batch spends is benchmarked by tools/bench/test_perf.py. The same cases also go through the public
API under the Lean authority, which must report `ResourceLimit` without any
operation falling back to Python.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import random
import time

import pytest

from tests import lean_routes

from conformance.p0 import envelope
from subprocesses import HANG_TIMEOUT, run_cpu_bounded
from conformance.three_way import rust_evaluations
from ve import Environment, FiniteModel, evaluate
from ve.ast import document_from_data, formula_from_data
from ve.backends import dispatch, rust_jsonl
from ve.backends.lean_service import LeanService
from ve.errors import ResourceLimit
from ve.evaluate import _Evaluator
from ve.limits import MAX_EVALUATIONS
from ve.search import check_countermodel
from ve.units import elaborate_quantity, erased_environment, quantity_countermodel

ROOT = Path(__file__).resolve().parents[1]
QUANTITY = "ve_quantity"  # its service mode, through tests/lean_routes.py
ROUTE = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_conformance"
SERVICE = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_service"
RUST = Path(os.environ.get("VE_RUST_BINARY", str(ROOT / "rust" / "target" / "release" / "ve")))
pytestmark = pytest.mark.skipif(not (lean_routes.SERVICE.exists() and ROUTE.exists() and RUST.exists()),
                                reason="build the Lean runners and the Rust release binary")
SEEDS = range(3)
CPU = 60  # the runaway guard: CPU seconds per backend per batch; each spends under 10 alone
# Every generated case stops at its first exhausted budget: at most MAX_EVALUATIONS
# charged units and the one refused charge that reports the limit.
CASE_UNITS = MAX_EVALUATIONS + 1


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
    """(name, python verdict thunk, Lean runner, Lean case, Rust case or None). Quantity cases
    have no Rust case: Lean-first batch 9 deleted Rust's quantity route."""
    rng = random.Random(seed)
    cases = []

    def quantity_value(name, formula, data):
        raw = w6_env()
        cases.append((name, lambda: py_quantity_value(raw, formula, data), "quantity",
                      {"id": name, "environment": raw, "quantity": q(formula), "model": data},
                      None))

    def quantity_countermodel_case(name, premises, conclusion, data):
        raw = w6_env()
        body = {"environment": raw, "premises": [q(p) for p in premises], "conclusion": q(conclusion),
                "model": data}
        cases.append((name, lambda: py_quantity_countermodel(raw, premises, conclusion, data), "quantity",
                      {"id": name, "kind": "countermodel", **body},
                      None))

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


class Overrun(BaseException):
    """Python charged past a budget; a BaseException, so no handler in `ve` absorbs it."""


def meter_python(monkeypatch):
    """Count the evaluation units Python charges (`_Evaluator.tick`, the only gate
    of the budget), per case, and stop at the first charge past a budget: an
    evaluator whose own check was skipped or widened, or a case that goes on
    charging after its budget is spent, fails here instead of running on.

    The meter reads Python's evaluator, so the metered cases run on the Python
    authority whatever VE_AUTHORITY selects."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    units = [0]
    charge = _Evaluator.tick

    def tick(self):
        units[0] += 1
        if self.work > MAX_EVALUATIONS or units[0] > CASE_UNITS:
            raise Overrun(f"{units[0]} units charged, evaluator at {self.work}")
        charge(self)
    monkeypatch.setattr(_Evaluator, "tick", tick)
    return units


def run(command, cases):
    # The kernel stops a batch that spends CPU seconds past the limit (a runaway guard: it
    # then exits by a signal, which fails here); the service stops a request past its mode's CPU
    # deadline (`lean_service.DEADLINES`). What each batch spends is a benchmark against a stored
    # baseline (tools/bench/test_perf.py), not a test criterion.
    if command[0] == str(QUANTITY):
        results = lean_routes.rows(QUANTITY, cases)
        assert len(results) == len(cases)
        return results
    completed, cpu = run_cpu_bounded(command, json.dumps(cases), CPU)
    assert completed.returncode in (0, 1), (command[0], completed.returncode, cpu, completed.stderr[:500])
    results = json.loads(completed.stdout)
    assert len(results) == len(cases)
    return results


@pytest.mark.parametrize("seed", SEEDS)
def test_every_backend_reports_resource_limit_in_bounded_time(seed, monkeypatch):
    cases = generate(seed)
    assert len({c[0] for c in cases}) == len(cases)
    units = meter_python(monkeypatch)
    python = {}
    for name, verdict, _, _, _ in cases:
        units[0] = 0
        try:
            python[name] = verdict()
        except Overrun as exc:
            pytest.fail(f"{name}: Python evaluation ran past its budget: {exc}")
    assert all(python.values()), [n for n, v in python.items() if not v]
    quantity = run([str(QUANTITY), "-"], [c[3] for c in cases if c[2] == "quantity"])
    route = run([str(ROUTE), "route", "-"], [c[3] for c in cases if c[2] == "route"])
    for got in quantity + route:
        assert got["status"] == "error" and got["error"].startswith("ResourceLimit"), got
    rust = rust_evaluations(lambda batch: run([str(RUST), "conformance"], batch),
                            [c[4] for c in cases if c[4] is not None])
    for got in rust:
        limited = (got.get("status") == "error" and got["error"]["code"] == "ResourceLimit") or \
            got.get("status") == "ResourceLimit"
        assert limited, got


# The operations that decide the work-budget and domain cases once the
# structural caps of `limits.py` (checked before any backend is called) pass.
BUDGET_OPERATIONS = {"evaluate", "countermodel_check", "model_validation", "definitions_elaboration"}


@pytest.mark.skipif(not SERVICE.exists(), reason="build the Lean service")
@pytest.mark.parametrize("seed", SEEDS)
def test_lean_authority_reports_resource_limit_on_every_generated_case(seed, monkeypatch):
    """The Lean-authority counterpart of the metered test above: the same
    generated cases, through the same public calls under VE_AUTHORITY=lean, each
    report `ResourceLimit`, and every operation they dispatch runs on Lean (no
    Python fallback). It counts no Python units: the verdicts are the backends'.

    Lean-authority evaluation asks Rust first. Under load (a 2 h 14 min suite)
    one such call outlasted the Rust client's 5-second default; every Rust call
    and Lean service request here must wait the suite's hang guard instead
    (`VE_RUST_TIMEOUT`, `VE_LEAN_SERVICE_TIMEOUT`: a request's wall-clock cap beside
    its mode's CPU deadline, lean-first batch 1)."""
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    monkeypatch.delenv("VE_AUTHORITY_OVERRIDES", raising=False)
    calls = []
    monkeypatch.setattr(dispatch, "observers", [*dispatch.observers, lambda op, a: calls.append((op, a))])
    waits, lean_waits = [], []
    checker, deadline = rust_jsonl._run_checker, LeanService._deadline

    def recorded(argv, *, input, timeout):
        waits.append(timeout)
        return checker(argv, input=input, timeout=timeout)

    def lean_recorded(self, mode, size, cases, timeout):
        start = time.monotonic()
        result = deadline(self, mode, size, cases, timeout)
        lean_waits.append(round(result.wall - start))
        return result
    monkeypatch.setattr(rust_jsonl, "_run_checker", recorded)
    monkeypatch.setattr(LeanService, "_deadline", lean_recorded)
    dispatched = set()
    for name, verdict, _, _, _ in generate(seed):
        calls.clear()
        assert verdict(), f"{name}: no ResourceLimit under the Lean authority"
        assert all(authority == "lean" for _, authority in calls), (name, calls)
        dispatched.update(op for op, _ in calls)
    assert BUDGET_OPERATIONS <= dispatched, BUDGET_OPERATIONS - dispatched
    assert waits and set(waits) == {HANG_TIMEOUT}, sorted(set(waits))
    assert lean_waits and set(lean_waits) == {HANG_TIMEOUT}, sorted(set(lean_waits))


# --- The Python meter keeps the regression power of the old wall-clock bound ---

@pytest.mark.parametrize("prefix", ["r-binders-", "reproducer-2-"])
def test_python_meter_stops_an_evaluator_that_skips_its_budget(prefix, monkeypatch):
    """An evaluator whose budget check is skipped would answer after 2^k units
    (2^30 for the defined table); the meter stops it one charge past the budget,
    and the case fails whatever the machine load."""
    def unchecked(self):
        self.work += 1
    monkeypatch.setattr(_Evaluator, "tick", unchecked)
    units = meter_python(monkeypatch)
    verdict = next(c[1] for c in generate(0) if c[0].startswith(prefix))
    with pytest.raises(Overrun):
        verdict()
    assert units[0] == MAX_EVALUATIONS + 2


def test_python_meter_stops_a_case_that_charges_past_its_first_budget(monkeypatch):
    """A case that starts a second budget after the first is spent (a retry, or a
    budget per statement instead of per case) is stopped at its first new charge."""
    units = meter_python(monkeypatch)
    verdict = next(c[1] for c in generate(0) if c[0].startswith("r-full-domain-"))
    assert verdict()
    assert units[0] == CASE_UNITS
    with pytest.raises(Overrun):
        verdict()
    assert units[0] == CASE_UNITS + 1
