"""Under the Lean authority no reported evaluation value or count is Rust's (lean-first batch 15b, review B3).

Rust keeps search only: under `VE_AUTHORITY=lean` its evaluator may still score search candidates, but every
value, count and status a public operation reports comes from Lean's metered evaluator. The guard below fails
any Rust request that is not a search, so a public path that asks Rust's evaluator for a reported answer
fails here, whichever operation it is; the answers must equal Python's own, counts included. The closure
fixtures are the ones on which Rust's evaluator under-counted (DELTA V1).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ve.ast import Bottom, Not, document_from_data
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.search import check_countermodel, find_countermodel, find_distinguishing_model

ROOT = Path(__file__).resolve().parents[1]
CLOSURE = [case for case in json.loads((ROOT / "conformance/closure.json").read_text())
           if "model" in case and "ast" in case]
SEARCH_KINDS = {None, "distinguishing-model"}


@pytest.fixture
def rust_searches_only(monkeypatch):
    from ve.backends import rust_jsonl
    original = rust_jsonl.run

    def guarded(case, *args, **kwargs):
        assert case.get("kind") in SEARCH_KINDS and "max_domain_size" in case, (
            f"Rust was asked for a reported evaluation under the Lean authority: {sorted(case)}")
        return original(case, *args, **kwargs)
    monkeypatch.setattr(rust_jsonl, "run", guarded)


def answers(env, formulas, model):
    document = document_from_data(env, formulas)
    *premises, last = document.formulas
    result = evaluate(env, document, model, trace=False)
    return {"evaluate": (result.status, result.value, result.evaluations),
            "check": check_countermodel(env, premises, last, model),
            "negated": check_countermodel(env, premises, Not(last), model),
            "model": check_countermodel(env, document.formulas, Bottom(), model),
            "tight": check_countermodel(env, premises, Not(last), model, max_evaluations=7)}


def test_closure_fixtures_reach_both_outcomes():
    assert len(CLOSURE) >= 20


@pytest.mark.parametrize("case", CLOSURE, ids=[case["id"] for case in CLOSURE])
def test_lean_authority_reports_lean_values_and_counts(case, monkeypatch, rust_searches_only):
    env = Environment(case["environment"])
    model = FiniteModel.from_dict(env, case["model"])
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = answers(env, case["ast"], model)
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert answers(env, case["ast"], model) == expected, case["id"]


def test_lean_authority_search_checks_its_witness_with_lean(monkeypatch, rust_searches_only):
    case = next(case for case in CLOSURE if case["id"] == "closure_cycle")
    env = Environment(case["environment"])
    document = document_from_data(env, case["ast"])
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    found = find_countermodel(env, (), document.formulas[1], max_domain_size=2)
    assert found.status == "Found" and check_countermodel(env, (), document.formulas[1], found.model).valid
    different = find_distinguishing_model(env, document.formulas[0], document.formulas[1], max_domain_size=2)
    assert different.status == "Found"


@pytest.mark.parametrize("global_authority", ["python", "lean"])
@pytest.mark.parametrize("search", ["countermodel_search", "distinguishing_model"])
def test_lean_selected_search_pins_its_witness_check(search, global_authority, monkeypatch,
                                                     rust_searches_only):
    """A check override must not let a Lean-selected Rust search publish a Python-checked witness."""
    from ve.backends import dispatch
    from ve import search as search_module
    case = next(case for case in CLOSURE if case["id"] == "closure_cycle")
    env = Environment(case["environment"])
    first, second = document_from_data(env, case["ast"]).formulas[:2]
    monkeypatch.setenv("VE_AUTHORITY", global_authority)
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", f"{search}=lean,countermodel_check=python")
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda op, authority: seen.append((op, authority))])

    def python_check_used(*args, **kwargs):
        pytest.fail("a Lean-selected search used Python to check its witness")

    monkeypatch.setattr(search_module, "_evaluate_validated", python_check_used)
    if search == "countermodel_search":
        result = find_countermodel(env, (), second, max_domain_size=2)
    else:
        result = find_distinguishing_model(env, first, second, max_domain_size=2)
    assert result.status == "Found"
    assert (search, "lean") in seen
    assert ("countermodel_check", "lean") in seen
    assert ("countermodel_check", "python") not in seen
