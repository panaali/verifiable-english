"""Backend integration on the public evaluation and Background signatures."""
from __future__ import annotations

from pathlib import Path

import pytest

from conformance.p0 import environment
from ve import Environment, FiniteModel
from ve.ast import And, Binary, Bottom, Const, Eq, Exists, Forall, Implies, Not, Or, Top, Unary, Var
from ve.background import background
from ve.evaluate import evaluate
from ve.search import check_countermodel

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_service"
RUST = ROOT / "rust/target/release/ve"


@pytest.fixture
def fixture():
    wire = environment()
    wire["vocabulary"]["sorts"]["person"] = {"description": "A person."}
    for item in wire["vocabulary"]["constants"].values():
        item["sort"] = "person"
        item["description"] = "A named person."
    wire["vocabulary"]["predicates"]["ready"] = {
        "arguments": ["person"], "description": "A ready person."}
    wire["vocabulary"]["predicates"]["knows"] = {
        "arguments": ["person", "person"], "description": "One person knows another."}
    env = Environment(wire)
    model = FiniteModel.from_dict(env, {"complete": True,
                                      "domains": {"person": ["a", "b"]},
                                      "constants": {"alpha": "a", "beta": "b"},
                                      "relations": {"ready": [["a"]], "knows": [["a", "b"]]}})
    return env, model


@pytest.mark.skipif(not LEAN.exists(), reason="Lean service has not been built")
def test_lean_background_preserves_named_premises(monkeypatch, fixture):
    env, _ = fixture
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = background(env)
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert background(env) == expected


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("formula,budget", [(Top(), 1), (Bottom(), 1),
                                           (And(Top(), Top()), 2), (Top(), 0)])
def test_budgeted_evaluation_matches_python(monkeypatch, fixture, formula, budget):
    env, model = fixture
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = evaluate(env, formula, model, trace=False, max_evaluations=budget)
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        assert evaluate(env, formula, model, trace=False,
                        max_evaluations=budget).to_dict() == expected.to_dict()


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
def test_shadow_evaluation_has_no_divergence(monkeypatch, fixture, tmp_path):
    env, model = fixture
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    assert evaluate(env, Top(), model, trace=False).value is True
    assert not log.exists()


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("formula,budget,trace_budget", [
    (Top(), 1, 1), (Top(), 0, 10), (And(Top(), Bottom()), 3, 3),
    (And(Bottom(), Top()), 2, 2), (Or(Top(), Bottom()), 2, 2),
    (Implies(Bottom(), Top()), 2, 2), (Not(Top()), 2, 2),
    (Eq(Const("alpha"), Const("beta")), 1, 1),
    (Unary("ready", Const("alpha")), 1, 1),
    (Binary("knows", Const("alpha"), Const("beta")), 1, 1),
    (Forall("person", Eq(Var(0), Const("alpha"))), 3, 3),
    (Exists("person", Eq(Var(0), Const("beta"))), 3, 3),
    (Exists("person", Top()), 4, 1),
])
def test_traced_evaluation_matches_python(monkeypatch, fixture, formula, budget, trace_budget):
    env, model = fixture
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = evaluate(env, formula, model, trace=True,
                        max_evaluations=budget, max_trace_nodes=trace_budget)
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        actual = evaluate(env, formula, model, trace=True,
                          max_evaluations=budget, max_trace_nodes=trace_budget)
        assert actual.to_dict() == expected.to_dict()


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("premises,conclusion,budget", [
    ((Top(),), Bottom(), 2), ((Bottom(),), Top(), 2),
    ((Top(),), Bottom(), 1),
])
def test_countermodel_schema_identity_and_budget(monkeypatch, fixture, premises, conclusion, budget):
    env, model = fixture
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = check_countermodel(env, premises, conclusion, model, max_evaluations=budget)
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        assert check_countermodel(env, premises, conclusion, model,
                                  max_evaluations=budget) == expected
