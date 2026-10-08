"""Batch 15a: Lean's metered evaluator and non-vacuity search filter."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from tests.subprocesses import HANG_TIMEOUT
from tests.probe_matrix import model_wire, raw_environment
from ve import Environment, FiniteModel
from ve.ast import (And, Atom, Binary, Body, Bottom, Const, Document, Eq, Exists,
                    Forall, Implies, Le, Lt, Named, Not, Num, Or, Reach, Top,
                    Unary, Var, formula_to_data)
from ve.evaluate import evaluate
from ve.search import _nonvacuous


EXE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_metered"
FAMILIES = ((), ("closure@0",), ("closure@0", "nary@0"), ("order@0",))


def run(cases):
    answer = subprocess.run([str(EXE)], input=json.dumps(cases), text=True,
                            capture_output=True, check=True, timeout=HANG_TIMEOUT)
    return json.loads(answer.stdout)


def fixture(profiles):
    raw = raw_environment(profiles)
    env = Environment(raw)
    model = FiniteModel.from_dict(env, model_wire(env))
    return raw, env, model


def formulas(profiles):
    common = [Top(), Bottom(), Not(Bottom()), And(Top(), Bottom()),
              Or(Top(), Bottom()), Implies(Bottom(), Top()),
              Unary("base", Const("x")), Eq(Const("x"), Const("x")),
              Forall("item", Unary("base", Var(0))),
              Exists("item", Not(Unary("base", Var(0)))),
              Forall("item", Implies(Unary("base", Var(0)), Top()))]
    if "closure@0" in profiles:
        common += [Binary("step", Const("x"), Const("x")),
                   Reach("plus", Named("step"), Const("x"), Const("x")),
                   Reach("star", Body("item", Binary("step", Var(1), Var(0))),
                         Const("x"), Const("x"))]
    if "nary@0" in profiles:
        common.append(Atom("triple", (Const("x"), Const("y"), Const("x"))))
    if "order@0" in profiles:
        common += [Lt(Num(0), Num(1)), Le(Num(1), Num(1))]
    return common


@pytest.mark.skipif(not EXE.exists(), reason="ve_metered has not been built")
@pytest.mark.parametrize("profiles", FAMILIES)
def test_budgeted_values_counts_and_traces_match_python(profiles):
    raw, env, model = fixture(profiles)
    cases, expected = [], []
    for formula in formulas(profiles):
        for budget, trace_budget, trace in ((0, 4, False), (1, 4, True),
                                            (2, 1, True), (4, 4, True), (20, 20, True)):
            cases.append({"id": str(len(cases)), "kind": "evaluate-budgeted",
                          "environment": raw, "model": model.to_dict(),
                          "ast": [formula_to_data(env, formula)],
                          "max_evaluations": budget, "max_trace_nodes": trace_budget,
                          "trace": trace})
            expected.append(evaluate(env, formula, model, max_evaluations=budget,
                                     max_trace_nodes=trace_budget, trace=trace).to_dict())
    rows = run(cases)
    assert len(rows) == len(cases)
    for case, row, answer in zip(cases, rows, expected, strict=True):
        assert row["status"] == "ok", (case, row)
        assert row["evaluation"] == answer, (case, row["evaluation"], answer)


@pytest.mark.skipif(not EXE.exists(), reason="ve_metered has not been built")
@pytest.mark.parametrize("profiles", FAMILIES)
def test_document_budget_is_shared_and_stops_at_first_violation(profiles):
    raw, env, model = fixture(profiles)
    documents = (Document((Top(), Bottom(), Top())), Document((Top(), Top())))
    cases, expected = [], []
    for document in documents:
        for budget in (0, 1, 2, 3, 4):
            cases.append({"id": str(len(cases)), "kind": "evaluate-budgeted",
                          "environment": raw, "model": model.to_dict(),
                          "ast": [formula_to_data(env, f) for f in document.formulas],
                          "max_evaluations": budget, "trace": True})
            expected.append(evaluate(env, document, model, max_evaluations=budget,
                                     trace=True).to_dict())
    for row, answer in zip(run(cases), expected, strict=True):
        assert row["evaluation"] == answer


@pytest.mark.skipif(not EXE.exists(), reason="ve_metered has not been built")
@pytest.mark.parametrize("profiles", FAMILIES)
def test_nonvacuity_charge_exhaustion_and_semantic_guards_match_python(profiles):
    raw, env, model = fixture(profiles)
    candidates = (Top(), Forall("item", Implies(Unary("base", Var(0)), Top())),
                  Forall("item", Implies(Bottom(), Top())),
                  Forall("item", Or(Not(Unary("base", Var(0))), Bottom())))
    cases, expected = [], []
    for formula in candidates:
        for semantic in (False, True):
            for budget in (0, 1, 3, 20):
                cases.append({"id": str(len(cases)), "kind": "non-vacuity",
                              "environment": raw, "model": model.to_dict(),
                              "formula": formula_to_data(env, formula),
                              "max_evaluations": budget, "semantic_nonvacuity": semantic})
                expected.append(_nonvacuous(env, formula, model, budget, semantic=semantic))
    for row, answer in zip(run(cases), expected, strict=True):
        assert row["status"] == "ok", row
        assert (row["suitable"], row["evaluations"], row["exhausted"]) == answer


@pytest.mark.skipif(not EXE.exists(), reason="ve_metered has not been built")
def test_bad_budget_types_are_bounded_errors():
    raw, env, model = fixture(())
    cases = [{"id": str(i), "kind": "evaluate-budgeted", "environment": raw,
              "model": model.to_dict(), "ast": [["top"]], "max_evaluations": value}
             for i, value in enumerate((True, None, [], {}, "3", -1))]
    for case in cases:
        completed = subprocess.run([str(EXE)], input=json.dumps([case]), text=True,
                                   capture_output=True, timeout=HANG_TIMEOUT)
        if completed.returncode == 0:
            assert json.loads(completed.stdout)[0]["status"] == "error"
        else:
            assert completed.returncode == 2
            assert "expected restricted JSON value" in completed.stderr


@pytest.mark.skipif(not EXE.exists(), reason="ve_metered has not been built")
@pytest.mark.parametrize("profiles", FAMILIES)
def test_empty_quantifier_domains_match_python(profiles):
    raw, _, _ = fixture(profiles)
    raw["vocabulary"]["sorts"]["empty"] = {"description": "empty"}
    env = Environment(raw)
    wire = model_wire(env)
    wire["domains"]["empty"] = []
    model = FiniteModel.from_dict(env, wire)
    formulas_ = (Forall("empty", Top()), Exists("empty", Top()))
    cases = [{"id": str(i), "kind": "evaluate-budgeted", "environment": raw,
              "model": model.to_dict(), "ast": [formula_to_data(env, f)], "trace": True,
              "max_evaluations": budget}
             for i, (f, budget) in enumerate((f, b) for f in formulas_ for b in (0, 1, 2))]
    expected = [evaluate(env, f, model, trace=True, max_evaluations=budget).to_dict()
                for f in formulas_ for budget in (0, 1, 2)]
    for row, answer in zip(run(cases), expected, strict=True):
        assert row["evaluation"] == answer
    nv = [{"id": str(i), "kind": "non-vacuity", "environment": raw,
           "model": model.to_dict(), "formula": formula_to_data(env, f)}
          for i, f in enumerate(formulas_)]
    assert [row["suitable"] for row in run(nv)] == [False, False]
