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
from ve.evaluate import _evaluate_validated, _explanation
from tests import nonvacuity_oracle


EXE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_metered"
FAMILIES = ((), ("closure@0",), ("closure@0", "nary@0"), ("order@0",))


def python(formulas, model, **options):
    """The retained Python evaluator's answer (`evaluate` itself is Lean's since lean-first batch 18)."""
    return _evaluate_validated(tuple(formulas), model, **options).to_dict()


def lean(row):
    """A metered row's evaluation, its explanation rows rebuilt into the public tree (`_explanation`)."""
    evaluation = row["evaluation"]
    rows = evaluation["explanation"]
    return {**evaluation, "explanation": None if rows is None else _explanation(rows).to_dict()}


def run(cases):
    answer = subprocess.run([str(EXE)], input=json.dumps(cases), text=True,
                            capture_output=True, check=False, timeout=HANG_TIMEOUT)
    rows = json.loads(answer.stdout)
    # Exit 1 exactly when a case is rejected (batch 15b), as every one-shot runner.
    assert answer.returncode == int(any(row.get("status") == "error" for row in rows)), answer
    return rows


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
            expected.append(python((formula,), model, max_evaluations=budget,
                                   max_trace_nodes=trace_budget, trace=trace))
    rows = run(cases)
    assert len(rows) == len(cases)
    for case, row, answer in zip(cases, rows, expected, strict=True):
        assert row["status"] == "ok", (case, row)
        assert lean(row) == answer, (case, row["evaluation"], answer)


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
            expected.append(python(document.formulas, model, max_evaluations=budget, trace=True))
    for row, answer in zip(run(cases), expected, strict=True):
        assert lean(row) == answer


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
                item = formula_to_data(env, formula)
                cases.append({"id": str(len(cases)), "kind": "non-vacuity",
                              "environment": raw, "model": model.to_dict(),
                              "formula": item,
                              "max_evaluations": budget, "semantic_nonvacuity": semantic})
                expected.append(nonvacuity_oracle.answer(raw, model.to_dict(), item, budget, semantic,
                                                         env=env, formula=formula, model=model))
    for row, answer in zip(run(cases), expected, strict=True):
        assert row["status"] == "ok", row
        assert [row["suitable"], row["evaluations"], row["exhausted"]] == answer


@pytest.mark.skipif(not EXE.exists(), reason="ve_metered has not been built")
def test_bad_budget_types_are_bounded_errors():
    raw, env, model = fixture(())
    cases = [{"id": str(i), "kind": "evaluate-budgeted", "environment": raw,
              "model": model.to_dict(), "ast": [["top"]], "max_evaluations": value}
             for i, value in enumerate((True, None, [], {}, "3", -1))]
    for case in cases:
        completed = subprocess.run([str(EXE)], input=json.dumps([case]), text=True,
                                   capture_output=True, timeout=HANG_TIMEOUT)
        if completed.returncode == 1:  # a rejected case (exit 1 since batch 15b)
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
    expected = [python((f,), model, trace=True, max_evaluations=budget)
                for f in formulas_ for budget in (0, 1, 2)]
    for row, answer in zip(run(cases), expected, strict=True):
        assert lean(row) == answer
    nv = [{"id": str(i), "kind": "non-vacuity", "environment": raw,
           "model": model.to_dict(), "formula": formula_to_data(env, f)}
          for i, f in enumerate(formulas_)]
    assert [row["suitable"] for row in run(nv)] == [False, False]


ROW = {"kind": "top", "value": True, "bindings": [], "detail": "", "children": 0}


@pytest.mark.parametrize("rows", [
    [],                                                                 # no tree
    [{**ROW, "kind": "document", "children": 2}, ROW],                  # a count past the end
    [{**ROW, "kind": "document", "children": 1}, ROW, ROW],             # a row outside the tree
    [ROW, ROW],                                                         # two roots
    [{**ROW, "children": -1}],                                          # a negative count
    [{**ROW, "children": True}],                                        # a Boolean count
    [{**ROW, "bindings": [{"debruijn_index": 1, "sort": "s", "local_id": "x"}]}],   # a shifted index
    [{k: v for k, v in ROW.items() if k != "detail"}],                  # a missing member
    "rows",                                                             # not a list
])
def test_explanation_rows_must_be_exactly_one_tree(rows):
    """Lean-first batch 18: the service writes an explanation as preorder rows (`MeteredTrace.Trace.json`); rows
    that are not exactly one tree in preorder are no answer."""
    from ve.errors import CheckerUnavailable
    with pytest.raises(CheckerUnavailable):
        _explanation(rows)


def test_explanation_rows_rebuild_the_tree():
    rows = [{**ROW, "kind": "document", "detail": "all statements satisfied", "children": 2},
            {**ROW, "kind": "and", "children": 1}, ROW, ROW]
    tree = _explanation(rows).to_dict()
    assert [child["kind"] for child in tree["children"]] == ["and", "top"]
    assert [child["kind"] for child in tree["children"][0]["children"]] == ["top"]


@pytest.mark.parametrize("kind, answer", [
    ("evaluate-budgeted", {"id": "c", "status": "ok", "suitable": True, "evaluations": 1, "exhausted": False}),
    ("non-vacuity", {"id": "c", "status": "ok", "evaluation": {"status": "Satisfied", "value": True,
                                                                "evaluations": 1, "explanation": None}}),
])
def test_a_metered_answer_of_the_other_kind_is_no_answer(monkeypatch, kind, answer):
    """The `metered` row is one of two alternatives (`metered.json`); the client binds it to the kind it sent."""
    from ve.backends import lean_runner, relay
    from ve.errors import CheckerUnavailable
    monkeypatch.setattr(relay, "rows", lambda mode, cases, **_: [answer])
    call = lean_runner.metered_evaluation if kind == "evaluate-budgeted" else lean_runner.metered_nonvacuity
    with pytest.raises(CheckerUnavailable, match="of another kind"):
        call({"id": "c"})
