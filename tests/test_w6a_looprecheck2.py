"""W6a loop recheck 2 regressions: budgeted checks see one domain order.

Python and Rust sort every submitted domain when they load a model, and a
budgeted evaluator short-circuits quantifiers, so its work (and whether it
exhausts `MAX_EVALUATIONS`) depends on entity order. Lean now sorts after
the frozen decoders, in the quantity runner (`admission` and `countermodel`)
and in the relational route (the defined-table budget). Each check runs in
more than one domain order, three ways.
"""
from __future__ import annotations

from itertools import permutations
import json
import subprocess

import pytest

from tests.test_units_lean_w6a import LEAN, ROOT, lean, quantity, rust
from tests.test_w6a_review_regressions import raw_environment
from ve import ast
from ve.environment import Environment
from ve.errors import ResourceLimit
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.units import erased_environment, quantity_countermodel

pytestmark = pytest.mark.skipif(not LEAN.exists(), reason="build the Lean ve_quantity runner first")
CONFORMANCE = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_conformance"


def wide(depth):
    """p(x) ∨ ∀y₁…∀y_depth.⊤, the reviewer's reproducer body (x is index 0)."""
    body = ["top"]
    for _ in range(depth):
        body = ["forall", "item", body]
    return ["or", ["unary", "p", ["var", 0]], body]


def raw():
    return raw_environment({}, sorts={"item": {"description": "an item"}},
                           predicates={"p": {"arguments": ["item"], "description": "p"}})


def model(domain, holds=("b",)):
    return {"complete": True, "domains": {"item": list(domain)}, "constants": {},
            "relations": {"p": [[e] for e in holds]}}


def python_value(formula, data):
    target = erased_environment(Environment(raw()))
    result = evaluate(target, ast.formula_from_data(target, formula),
                      FiniteModel.from_dict(target, data), trace=False)
    # An exhausted budget is UNKNOWN: no value and no reported count.
    return (None, None) if result.value is None else (result.value, result.evaluations)


def test_reviewer_reproducer_is_unknown_in_every_order_three_ways():
    formula = ["exists", "item", wide(19)]
    for domain in (["b", "a"], ["a", "b"]):
        data = model(domain)
        assert python_value(formula, data) == (None, None)
        [got] = lean([{"id": "r", "environment": raw(), "quantity": quantity(formula), "model": data}])
        assert got["status"] == "error" and "MAX_EVALUATIONS" in got["error"], (domain, got)
        [other] = rust([{"id": "r", "kind": "quantity", "environment": raw(),
                         "quantity": quantity(formula), "model": data}])
        assert other["status"] == "error" and other["error"]["code"] == "ResourceLimit", other


def test_countermodel_route_is_unknown_in_every_order_three_ways():
    env = Environment(raw())
    conclusion = quantity(["not", ["exists", "item", wide(19)]])
    for domain in (["b", "a"], ["a", "b"]):
        data = model(domain)
        with pytest.raises(ResourceLimit, match="MAX_EVALUATIONS"):
            quantity_countermodel(env, [], conclusion, data)
        case = {"environment": raw(), "premises": [], "conclusion": conclusion, "model": data}
        [got] = lean([{"id": "m", "kind": "countermodel", **case}])
        assert got["status"] == "error" and "MAX_EVALUATIONS" in got["error"], (domain, got)
        [other] = rust([{"id": "m", "kind": "quantity", "mode": "countermodel", **case}])
        assert other["status"] == "error" and other["error"]["code"] == "ResourceLimit", other


def test_evaluation_counts_agree_on_every_permutation():
    """Below the budget the value never depended on order, but the reported
    work did: Lean now reports Python's count on every permutation."""
    formulas = [["exists", "item", wide(3)], ["forall", "item", wide(2)],
                ["exists", "item", ["and", ["not", ["unary", "p", ["var", 0]]], wide(1)]]]
    cases, expected = [], []
    for domain in permutations(["c", "a", "b", "aa"]):
        for index, formula in enumerate(formulas):
            data = model(domain, holds=("b", "aa"))
            cases.append({"id": f"{index}:{','.join(domain)}", "environment": raw(),
                          "quantity": quantity(formula), "model": data})
            expected.append(python_value(formula, data))
    for got, (value, work) in zip(lean(cases), expected, strict=True):
        assert got["status"] == "ok" and (got["value"], got["evaluations"]) == (value, work), got
    for other, (value, _) in zip(rust([{**c, "kind": "quantity"} for c in cases]), expected, strict=True):
        assert other["status"] == "ok" and other["value"] is value, other


def test_premise_order_short_circuit_still_matches_across_domain_orders():
    """A false premise stops the countermodel check before the conclusion, in any order."""
    env = Environment(raw())
    premise = quantity(["forall", "item", ["unary", "p", ["var", 0]]])
    conclusion = quantity(["not", ["exists", "item", wide(19)]])
    for domain in (["b", "a"], ["a", "b"]):
        data = model(domain)
        assert quantity_countermodel(env, [premise], conclusion, data) is False
        case = {"environment": raw(), "premises": [premise], "conclusion": conclusion, "model": data}
        [got] = lean([{"id": "m", "kind": "countermodel", **case}])
        assert got["status"] == "ok" and got["refutes"] is False, got
        [other] = rust([{"id": "m", "kind": "quantity", "mode": "countermodel", **case}])
        assert other["status"] == "ok" and other["refutes"] is False, other


# --- The same class on the relational route: the defined-table budget --------

def defined_env():
    body = ["top"]
    for _ in range(19):
        body = ["forall", "s", body]
    body = ["exists", "s", ["or", ["unary", "p", ["var", 0]], body]]
    return {"language": LANGUAGE, "profiles": ["definitions@0", "relational-fol@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {"s": {"description": "items"}}, "constants": {},
                           "predicates": {
                               "p": {"arguments": ["s"], "description": "p"},
                               "d": {"arguments": ["s"], "description": "d",
                                     "defined": {"arguments": ["s"], "body": body}}}}}


def run(command, cases):
    completed = subprocess.run(command, input=json.dumps(cases), text=True, capture_output=True,
                               timeout=600)
    assert completed.returncode in (0, 1), completed.stderr[:500]
    return json.loads(completed.stdout)


@pytest.mark.skipif(not CONFORMANCE.exists(), reason="build the Lean ve_conformance runner first")
def test_defined_table_budget_is_order_independent_three_ways():
    for domain in (["b", "a"], ["a", "b"]):
        data = {"complete": True, "domains": {"s": domain}, "constants": {},
                "relations": {"p": [["b"]]}}
        with pytest.raises(ResourceLimit, match="Definition model evaluation budget"):
            FiniteModel.from_dict(Environment(defined_env()), data)
        case = {"id": "d", "environment": defined_env(), "model": data, "ast": [["top"]]}
        [got] = run([str(CONFORMANCE), "route", "-"], [{**case, "kind": "evaluate"}])
        assert got["status"] == "error" and "Definition model evaluation budget" in got["error"], \
            (domain, got)
        [other] = run([str(ROOT / "rust" / "target" / "release" / "ve"), "conformance"], [case])
        assert other["status"] == "error" and other["error"]["code"] == "ResourceLimit", other


def test_lean_runners_sort_domains_and_audit_the_bridge():
    """The frozen decoders keep input order; the runners sort after decoding."""
    time = (ROOT / "lean" / "VE" / "Time" / "Wire.lean").read_text()
    route = (ROOT / "lean" / "VE" / "Route" / "Wire.lean").read_text()
    assert time.count("(sortDomains d).toModel maxEvaluations") == 2
    assert "evalB d.toModel" not in time and "refutesB d.toModel" not in time
    assert "let data₀ := sortModelData (← VE.Bridge.decodeModelData" in route
    audit = (ROOT / "lean" / "VE" / "Audit.lean").read_text()
    for name in ("VE.Time.eval_domains_perm", "VE.Time.countermodelCheck_domains_perm",
                 "VE.Time.Wire.sortDomains_perm", "VE.Time.Wire.evalB_sorted_sound",
                 "VE.Time.Wire.refutesB_sorted_sound"):
        assert f"#print axioms {name}\n" in audit
