"""premise-scale: Lean's premise-check budget, its per-sort domain bounds, the ground-fact route, and the
Rust wall-clock limit (DRI decisions QT2, ME1, ME2, ET1).

A premise set that forces more entities of one sort than the shared domain bound ("exactly three principal
types") gets a model at that size, Lean-checked; stated quantities give their own model with no search; a
Rust search that times out is no witness, and the premise check's answer is then Lean's alone. Nothing a
budget does is a verdict: every model is Lean-checked, and a spent or zero budget stays UNKNOWN.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT
from tests.premise_scale_fixtures import (exactly_chain, exactly_constants, distinct, quantity_environment,
                                          relational_environment, stated_quantities, conjunction)
from ve.ast import Bottom, formula_from_data
from ve.backends import rust_jsonl
from ve.environment import Environment
from ve.errors import CheckerUnavailable
from ve.search import GROUND_NOT_FOUND, check_countermodel, find_countermodel, premise_budget
from ve.vacuity import premise_status

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "tests/data/premise-scale/qt0p-companion.ve.md"


def formulas(env, asts):
    return [formula_from_data(env, ast) for ast in asts]


@pytest.fixture(scope="module")
def principals():
    return Environment(relational_environment())


# --- Lean's budget -------------------------------------------------------------------------------------

def test_lean_raises_only_the_sort_the_premises_force(principals):
    budget = premise_budget(principals, formulas(principals, [exactly_constants()]))
    assert (budget.max_proof_steps, budget.max_domain_size, budget.max_models, budget.max_evaluations) == (
        10_000, 2, 10_000, 100_000)
    assert budget.sort_bounds == {"principal_type": (3, 3)}


def test_an_existential_chain_raises_its_sort(principals):
    assert premise_budget(principals, formulas(principals, [exactly_chain()])).sort_bounds == {
        "principal_type": (3, 3)}
    assert premise_budget(principals, formulas(principals, [exactly_chain(4)])).sort_bounds == {
        "principal_type": (4, 4)}


def test_no_sort_is_raised_within_the_shared_bound_or_past_the_cap(principals):
    two = conjunction(distinct(["anthropic", "users"]))
    assert premise_budget(principals, formulas(principals, [two])).sort_bounds == {}
    nine = [f"t{i}" for i in range(9)]
    capped = Environment(relational_environment(dict.fromkeys(nine, "principal_type")))
    assert premise_budget(capped, formulas(capped, [conjunction(distinct(nine))])).sort_bounds == {}
    eight = Environment(relational_environment(dict.fromkeys(nine[:8], "principal_type")))
    assert premise_budget(eight, formulas(eight, [conjunction(distinct(nine[:8]))])).sort_bounds == {
        "principal_type": (8, 8)}


def test_a_negated_or_disjoined_inequality_forces_nothing(principals):
    # Only top-level conjuncts are facts: a disjunction of inequalities, or one under a negation, forces no
    # entity, so the sort stays at the shared bound.
    pairs = distinct(["anthropic", "operators", "users"])
    either = ["or", conjunction(pairs), ["top"]]
    assert premise_budget(principals, formulas(principals, [either])).sort_bounds == {}


# --- the premise check ---------------------------------------------------------------------------------

def test_exactly_three_principal_types_has_a_lean_checked_model_at_size_three(principals):
    premises = formulas(principals, [exactly_constants()])
    status = premise_status(principals, premises)
    assert status["status"] == "model"
    # The model the check reports is the search's at Lean's bounds, which Lean checks: three principal types.
    found = find_countermodel(principals, premises, Bottom(), sort_bounds={"principal_type": (3, 3)})
    assert found.status == "Found" and found.model.model_id == status["model_id"]
    assert len(found.model.domains["principal_type"]) == 3
    assert check_countermodel(principals, premises, Bottom(), found.model).valid
    # The same check with the caller's own budget (no Lean budget) stays UNKNOWN, as before premise-scale.
    before = premise_status(principals, premises, max_proof_steps=10_000, max_domain_size=2,
                            max_models=10_000, max_evaluations=100_000)
    assert before["status"] == "UNKNOWN" and "sort_bounds" not in before["budget"]


def test_the_chain_form_has_a_model_too(principals):
    assert premise_status(principals, formulas(principals, [exactly_chain()]))["status"] == "model"


def test_a_model_the_shared_bound_finds_is_unchanged(principals):
    """Today's search runs first with today's bounds: where it finds a model, that model is the answer."""
    premises = formulas(principals, [conjunction([["unary", "principal", ["const", "users"]],
                                                  *distinct(["anthropic", "users"])])])
    plain = find_countermodel(principals, premises, Bottom(), max_domain_size=2, max_models=10_000,
                              max_evaluations=100_000)
    assert plain.status == "Found"
    assert premise_status(principals, premises) == {"status": "model", "model_id": plain.model.model_id}


def test_raised_bounds_stay_in_the_unknown_budget():
    nine = [f"t{i}" for i in range(9)]
    env = Environment(relational_environment(dict.fromkeys(nine[:3], "principal_type")))
    premises = formulas(env, [exactly_constants(nine[:3])])
    status = premise_status(env, premises, max_models=0)
    assert status == {"status": "UNKNOWN", "budget": {
        "max_proof_steps": 10_000, "max_domain_size": 2, "max_models": 0, "max_evaluations": 100_000,
        "sort_bounds": {"principal_type": [3, 3]}}}


def test_document_mode_premise_check_of_qt0p_content():
    from ve.document import check_document
    assert check_document(COMPANION)["premises"]["status"] == "model"


# --- the ground-fact route -----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def quantities():
    return Environment(quantity_environment(80))


def test_stated_quantities_give_their_own_model(quantities):
    premises = formulas(quantities, stated_quantities(80))
    searched = find_countermodel(quantities, premises, Bottom(), max_models=100)
    assert searched.status == "ResourceLimit"
    ground = find_countermodel(quantities, premises, Bottom(), ground_only=True)
    assert (ground.status, ground.models_checked) == ("Found", 1)
    assert ground.model.constants["q079"] == 4000 + 7 * 79
    assert premise_status(quantities, premises) == {"status": "model", "model_id": ground.model.model_id}


def test_contradictory_stated_quantities_stay_inconsistent(quantities):
    facts = stated_quantities(80) + [["eq", ["const", "q000"], ["num", "1"]]]
    premises = formulas(quantities, facts)
    assert find_countermodel(quantities, premises, Bottom(), ground_only=True).detail == GROUND_NOT_FOUND
    assert premise_status(quantities, premises)["status"] == "INCONSISTENT"


def test_a_zero_model_budget_stays_unknown(quantities):
    """R5: no model may be tried, so the ground route finds none either."""
    premises = formulas(quantities, stated_quantities(80))
    assert find_countermodel(quantities, premises, Bottom(), ground_only=True, max_models=0).status == "ResourceLimit"
    status = premise_status(quantities, premises, max_models=0)
    assert status["status"] == "UNKNOWN" and status["budget"]["max_models"] == 0
    assert premise_status(quantities, premises)["status"] == "model"


# --- the search options --------------------------------------------------------------------------------

def test_search_options_are_checked(principals):
    premises = formulas(principals, [exactly_constants()])
    for bounds in ({"ghost": (1, 1)}, {"principal_type": (3, 2)}, {"principal_type": (True, 3)},
                   {"principal_type": (3,)}, [("principal_type", (3, 3))]):
        with pytest.raises(ValueError):
            find_countermodel(principals, premises, Bottom(), sort_bounds=bounds)
    with pytest.raises(ValueError):
        find_countermodel(principals, premises, Bottom(), ground_only=1)


@pytest.mark.parametrize("field,value,code", [
    ("sort_bounds", {"ghost": [1, 1]}, "InvalidInput"), ("sort_bounds", {"principal_type": [3, 2]}, "ResourceLimit"),
    ("sort_bounds", {"principal_type": [3]}, "InvalidInput"), ("sort_bounds", {"principal_type": [3, True]}, "InvalidInput"),
    ("sort_bounds", [], "InvalidInput"), ("ground_only", 1, "InvalidInput")])
def test_rust_refuses_malformed_search_options(principals, field, value, code):
    from ve.ast import _to_data
    case = {"id": "search", "environment": rust_jsonl.cached_rust_environment(principals),
            "premises": [exactly_constants()], "conclusion": _to_data(Bottom()), "max_models": 10, field: value}
    with pytest.raises(Exception) as caught:
        rust_jsonl.run(case)
    assert getattr(caught.value, "code", None) == code, caught.value


# --- the Rust wall-clock limit (ME1) -------------------------------------------------------------------

def test_a_rust_timeout_is_no_witness(principals, monkeypatch):
    """The search's Rust call times out: the premise check goes on to Lean's contradiction proof and answers
    UNKNOWN or INCONSISTENT, never CheckerUnavailable."""
    import ve.vacuity

    def timed_out(*args, **kwargs):
        raise rust_jsonl.RustTimeout("CheckerUnavailable: Rust checker failed: timed out")
    monkeypatch.setattr(ve.vacuity, "find_countermodel", timed_out)
    premises = formulas(principals, [exactly_constants()])
    assert premise_status(principals, premises)["status"] == "UNKNOWN"
    contradiction = formulas(principals, [conjunction([["unary", "principal", ["const", "users"]],
                                                       ["not", ["unary", "principal", ["const", "users"]]]])])
    assert premise_status(principals, contradiction)["status"] == "INCONSISTENT"


def test_another_rust_failure_is_still_unavailable(principals, monkeypatch):
    import ve.vacuity

    def failed(*args, **kwargs):
        raise CheckerUnavailable("CheckerUnavailable: Rust protocol failure")
    monkeypatch.setattr(ve.vacuity, "find_countermodel", failed)
    with pytest.raises(CheckerUnavailable):
        premise_status(principals, formulas(principals, [exactly_constants()]))


def test_a_timed_out_process_raises_rust_timeout(principals, monkeypatch):
    def hung(argv, *, input, timeout):
        raise subprocess.TimeoutExpired(argv, timeout)
    monkeypatch.setattr(rust_jsonl, "_run_checker", hung)
    with pytest.raises(rust_jsonl.RustTimeout) as caught:
        find_countermodel(principals, formulas(principals, [exactly_constants()]), Bottom())
    assert isinstance(caught.value, CheckerUnavailable)
    assert str(caught.value).startswith("CheckerUnavailable: Rust checker failed: Command")


def test_the_default_limit_grows_with_the_case(monkeypatch):
    """Without VE_RUST_TIMEOUT a call waits the scaled limit of its case: 5 s at least, more for a case
    with more constants (H's 217 constants: about 25 s)."""
    def limit(n):
        return rust_jsonl.scaled_timeout(
            {"environment": {"vocabulary": {"constants": {f"c{i}": {} for i in range(n)}}}})
    limits = [limit(n) for n in (0, 5, 62, 217, 800)]
    assert all(x >= rust_jsonl.DEFAULT_TIMEOUT for x in limits)
    assert limits == sorted(limits) and limits[-1] > 100 and 20 < limits[3] < 30
    assert rust_jsonl.scaled_timeout({}) == limit(0)
    seen = []

    def checker(argv, *, input, timeout):
        seen.append(timeout)
        raise subprocess.TimeoutExpired(argv, timeout)
    monkeypatch.setattr(rust_jsonl, "_run_checker", checker)
    case = {"id": "search", "environment": quantity_environment(217), "premises": stated_quantities(217),
            "conclusion": ["bottom"]}
    monkeypatch.delenv("VE_RUST_TIMEOUT", raising=False)
    with pytest.raises(rust_jsonl.RustTimeout):
        rust_jsonl.run(case)  # no child starts: the stand-in records the limit the call waits
    assert seen == [limit(217)]
    monkeypatch.setenv("VE_RUST_TIMEOUT", str(HANG_TIMEOUT))
    with pytest.raises(rust_jsonl.RustTimeout):
        rust_jsonl.run(case)
    assert seen[-1] == float(HANG_TIMEOUT)
