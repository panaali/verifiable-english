"""Backend integration on the public evaluation and Background signatures."""
from __future__ import annotations

from pathlib import Path

import pytest

from conformance.p0 import environment
from ve import Environment, FiniteModel
from ve.ast import And, Bottom, Top
from ve.background import background
from ve.evaluate import evaluate
from ve.search import check_countermodel

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_service"
RUST = ROOT / "rust/target/release/ve"


@pytest.fixture
def fixture():
    env = Environment(environment())
    model = FiniteModel.from_dict(env, {"complete": True,
                                      "domains": {"$string": ["a", "b"]},
                                      "constants": {"alpha": "a", "beta": "b"},
                                      "relations": {}})
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
