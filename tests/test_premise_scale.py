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


def test_the_readings_budget_is_leans(monkeypatch):
    """The readings routes' BUDGET holds no numbers of its own: each value is Lean's `search-budget` answer, and
    a key a test sets stands in for Lean's only until it is deleted."""
    from ve import readings_verdicts, search
    from ve.backends import relay
    # monkeypatch.setitem in another test restores a key by setting Lean's value back: start with none set.
    monkeypatch.setattr(readings_verdicts.BUDGET, "_set", {})
    lean = search.lean_budget()
    assert dict(readings_verdicts.BUDGET) == {"max_steps": lean.max_proof_steps, "max_domain_size": lean.max_domain_size,
                                              "max_models": lean.max_models, "max_evaluations": lean.max_evaluations}
    real = relay.decide

    def other(mode, cases, *args, **kwargs):
        [row] = real(mode, cases, *args, **kwargs)
        return [{**row, "max_models": 7, "max_proof_steps": 9}] if mode == "search-budget" else [row]
    search.lean_budget.cache_clear()
    monkeypatch.setattr(relay, "decide", other)
    try:
        assert readings_verdicts.BUDGET["max_models"] == 7 and readings_verdicts.BUDGET["max_steps"] == 9
        readings_verdicts.BUDGET["max_models"] = 0
        assert readings_verdicts.BUDGET["max_models"] == 0
        del readings_verdicts.BUDGET["max_models"]
        assert readings_verdicts.BUDGET["max_models"] == 7
        with pytest.raises(KeyError):
            readings_verdicts.BUDGET["max_nodes"] = 1
    finally:
        search.lean_budget.cache_clear()


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
    """Without VE_RUST_TIMEOUT a model search waits the scaled limit of its case: 5 s at least, more for a longer case
    line and for more constants (H's search, 50 kB and 217 constants: about a minute; a constitution search,
    60 kB and 5 constants: about half a minute)."""
    def limit(n, size=0):
        return rust_jsonl.scaled_timeout(
            {"max_models": 10_000, "environment": {"vocabulary": {"constants": {f"c{i}": {} for i in range(n)}}}}, size)
    by_constants = [limit(n) for n in (0, 5, 62, 217, 800)]
    assert all(x >= rust_jsonl.DEFAULT_TIMEOUT for x in by_constants)
    assert by_constants == sorted(by_constants) and by_constants[-1] > 500
    by_size = [limit(5, size) for size in (0, 10_000, 60_000, 1_000_000)]
    assert by_size == sorted(by_size) and by_size[0] < by_size[1] and 20 < by_size[2] < 40
    assert 50 < limit(217, 50_000) < 80
    assert limit(0) == rust_jsonl.TIMEOUT_FACTOR * rust_jsonl.SEARCH_SECONDS[0]
    # A case that is not a model search keeps the 5 s default, whatever its size.
    assert rust_jsonl.scaled_timeout({"kind": "check", "environment": {}}, 1_000_000) == rust_jsonl.DEFAULT_TIMEOUT
    seen = []

    def checker(argv, *, input, timeout):
        seen.append((len(input), timeout))
        raise subprocess.TimeoutExpired(argv, timeout)
    monkeypatch.setattr(rust_jsonl, "_run_checker", checker)
    case = {"id": "search", "environment": quantity_environment(217), "premises": stated_quantities(217),
            "conclusion": ["bottom"], "max_domain_size": 2, "max_models": 10_000, "max_evaluations": 100_000}
    monkeypatch.delenv("VE_RUST_TIMEOUT", raising=False)
    with pytest.raises(rust_jsonl.RustTimeout):
        rust_jsonl.run(case)  # no child starts: the stand-in records the limit the call waits
    [(size, waited)] = seen
    assert size > 10_000 and waited == limit(217, size)
    monkeypatch.setenv("VE_RUST_TIMEOUT", str(HANG_TIMEOUT))
    with pytest.raises(rust_jsonl.RustTimeout):
        rust_jsonl.run(case)
    assert seen[-1][1] == float(HANG_TIMEOUT)
    monkeypatch.setenv("VE_RUST_TIMEOUT", "soon")
    with pytest.raises(CheckerUnavailable):
        rust_jsonl.run(case, executable="/nonexistent/ve")  # the setting is refused before the executable


# --- the readings route's premise check (review F1, F2) ----------------------------------------------------
# premise-scale's searches and its timeout rule serve the premise check alone (no Γ, no conclusion): `premises()`
# and `candidate_premises()`. An entailment's countermodel search is as before premise-scale.

def _readings_document(tmp_path, fixed):
    """A superposed document: the open set {strict, default} of no-deception, help-x fixed, and `fixed`, over
    env K with three agent constants."""
    from tests.test_readings_s1_lean import env_k
    from tests.test_readings_s2_document import DF, HELP_X, S, s2_document
    raw = env_k()
    for name in ("a1", "a2", "a3"):
        raw["vocabulary"]["constants"][name] = {"sort": "agent", "description": name}
    return s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X), ("fixed", "u2", fixed)],
                       raw=raw)


@pytest.fixture(scope="module")
def three_agents(tmp_path_factory):
    """The premises force three agents, one more than the shared domain bound."""
    return _readings_document(tmp_path_factory.mktemp("three-agents"), conjunction(distinct(["a1", "a2", "a3"])))


@pytest.fixture(scope="module")
def m4(tmp_path_factory):
    from tests.test_readings_s2_document import DF, HELP_X, S, s2_document
    return s2_document(tmp_path_factory.mktemp("m4"), [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X)])


def _route(path):
    from ve.document import load_document
    from ve.readings_verdicts import context
    return context(load_document(path))


@pytest.fixture
def searches(monkeypatch):
    """Every model search and Lean budget request the readings route makes: (ground_only, raised, status)."""
    import ve.search
    real_search, real_budget, seen = ve.search.find_countermodel, ve.search.premise_budget, []

    def search(*args, **kwargs):
        found = real_search(*args, **kwargs)
        seen.append((kwargs.get("ground_only", False), bool(kwargs.get("sort_bounds")), found.status))
        return found

    def budget(*args, **kwargs):
        seen.append("search-budget")
        return real_budget(*args, **kwargs)
    monkeypatch.setattr(ve.search, "find_countermodel", search)
    monkeypatch.setattr(ve.search, "premise_budget", budget)
    return seen


def _timing_out(monkeypatch):
    import ve.search

    def timed_out(*args, **kwargs):
        raise rust_jsonl.RustTimeout("CheckerUnavailable: Rust checker failed: timed out")
    monkeypatch.setattr(ve.search, "find_countermodel", timed_out)


def test_readings_premise_check_searches_the_sort_lean_raises(three_agents, searches):
    """The raised branch: the shared bound finds no model, the search at Lean's raised bound does, and Lean
    checks it (`readings-model`)."""
    result = _route(three_agents).premises()
    assert result["status"] == "model" and result["evidence"] == "model", result
    assert len(result["model"]["domains"]["agent"]) == 3
    assert [c["status"] for c in result["candidates"]] == ["model", "model"]
    assert (False, True, "Found") in searches
    assert not any(entry[2] == "Found" for entry in searches if entry != "search-budget" and not entry[1])


def test_readings_premise_check_takes_the_ground_route(three_agents, searches, monkeypatch):
    """The ground branch: with one model attempt the raised search finds nothing, and the premises' stated facts
    are their own model, Lean-checked. With no attempt at all (R5) the answer stays UNKNOWN."""
    from ve import readings_verdicts
    monkeypatch.setattr(readings_verdicts.BUDGET, "_set", {"max_models": 1})
    result = _route(three_agents).premises()
    assert result["status"] == "model" and len(result["model"]["domains"]["agent"]) == 3, result
    assert (False, True, "ResourceLimit") in searches and (True, True, "Found") in searches
    assert not any(entry[2] == "Found" for entry in searches if entry != "search-budget" and not entry[0])
    monkeypatch.setattr(readings_verdicts.BUDGET, "_set", {"max_models": 0})
    assert _route(three_agents).premises()["status"] == "UNKNOWN"


def test_readings_premise_check_timeout_is_no_witness(three_agents, m4, monkeypatch):
    """The timeout branch: every Rust search times out, the lifted choices' searches included; the premise check
    answers without Rust's witness (DELTA row 4), never CheckerUnavailable."""
    _timing_out(monkeypatch)
    for path in (three_agents, m4):
        result = _route(path).premises()
        assert result["status"] == "UNKNOWN" and result["budget"], result
        assert [c["status"] for c in result["candidates"]] == ["UNKNOWN", "UNKNOWN"]


@pytest.mark.parametrize("assumed", [[("rs1", 1)], None])
def test_readings_entailment_timeout_is_still_unavailable(m4, monkeypatch, assumed):
    """Review F1: outside the premise check a Rust timeout is CheckerUnavailable, as before premise-scale, in the
    lifted choices' searches and in the search on `sup D` alike (named readings, and the fold over the choices)."""
    from tests.test_readings_s2_document import every
    from ve.readings_verdicts import Superposed
    _timing_out(monkeypatch)
    with pytest.raises(CheckerUnavailable):
        _route(m4).entailment(every("avoid_required"), assumed=assumed)
    monkeypatch.setattr(Superposed, "_lifted", lambda *args: None)
    with pytest.raises(CheckerUnavailable):
        _route(m4).entailment(every("avoid_required"), assumed=assumed)


@pytest.mark.parametrize("assumed", [[("rs1", 1)], None])
def test_readings_entailment_takes_no_scaled_search(three_agents, searches, assumed):
    """Review F1: an entailment's countermodel search keeps the shared bound. Its countermodel needs three agents,
    so it stays UNKNOWN: no raised or ground search runs, and Lean's budget is not asked for."""
    from tests.test_readings_s2_document import every
    route = _route(three_agents)
    assert route.conflict(())["status"] == "CONFLICT-FREE"
    searches.clear()
    result = route.entailment(every("avoid_required"), assumed=assumed)
    assert result["verdict"] == "UNKNOWN", result
    assert searches and "search-budget" not in searches
    assert not any(ground or raised for ground, raised, _ in searches), searches
