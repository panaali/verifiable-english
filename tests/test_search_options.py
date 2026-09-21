"""Request budgets and non-degenerate witnesses at public API boundaries."""
import pytest

from ve import (And, Bottom, Environment, Eq, Exists, FiniteModel, Forall, Implies,
                Not, Or, Top, Unary, Var, check, check_countermodel, evaluate,
                find_countermodel, find_distinguishing_model)
from ve.errors import InvalidModel


ENV = Environment({
    "language": "ve.core@0", "profile": "relational-fol@0",
    "spec_revision": "ve-v0-draft-2026-09-20",
    "vocabulary": {"sorts": {"item": {"description": "Item"}},
                   "predicates": {"active": {"arguments": ["item"], "description": "Active"}},
                   "constants": {}},
})


def test_no_trace_success_at_exactly_one_million_and_failure_one_short():
    wire = ENV.to_dict()
    wire["vocabulary"]["sorts"]["other"] = {"description": "Other"}
    env = Environment(wire)
    model = FiniteModel.from_dict(env, {
        "complete": True, "domains": {"item": [f"e{i}" for i in range(999)],
                                        "other": [f"e{i}" for i in range(1000)]},
        "constants": {}, "relations": {"active": []}})
    formula = Forall("item", Forall("other", Top()))
    result = evaluate(env, formula, model, trace=False)
    assert (result.status, result.evaluations) == ("Satisfied", 1_000_000)
    limited = evaluate(env, formula, model, max_evaluations=999_999, trace=False)
    assert (limited.status, limited.value, limited.evaluations) == ("ResourceLimit", None, 999_999)


def test_distinguishing_preserves_allowed_ast_depth():
    a, b = Top(), Bottom()
    for _ in range(63):
        a, b = Not(a), Not(b)
    result = find_distinguishing_model(ENV, a, b, max_domain_size=0, max_evaluations=128)
    assert result.status == "Found" and result.evaluations == 128
    assert evaluate(ENV, a, result.model).value != evaluate(ENV, b, result.model).value


def test_distinguishing_preserves_aggregate_size_without_synthetic_duplication():
    # 4095 nodes per tree, 8190 in the pair. An equivalence wrapper would exceed
    # the 10k AST envelope even though the two submitted claims are admissible.
    a, b = Top(), Bottom()
    for _ in range(11):
        a, b = And(a, a), Or(b, b)
    result = find_distinguishing_model(ENV, a, b, max_domain_size=0, max_evaluations=8190)
    assert result.status == "Found" and result.evaluations == 8190


def test_evaluation_budget_is_shared_across_premises_and_conclusion():
    model = FiniteModel.from_dict(ENV, {
        "complete": True, "domains": {"item": []}, "constants": {}, "relations": {"active": []}})
    limited = check_countermodel(ENV, (Top(), Top()), Bottom(), model, max_evaluations=2)
    assert limited.status == "ResourceLimit" and limited.conclusion_value is None
    assert limited.evaluations == 2 and not limited.valid
    assert check_countermodel(ENV, (Top(), Top()), Bottom(), model, max_evaluations=3).valid
    source = "true.\nfalse.\n"
    assert check(ENV, source, model, max_evaluations=1, trace=False)["evaluation"]["status"] == "ResourceLimit"
    assert check(ENV, source, model, max_evaluations=2, trace=False)["evaluation"]["status"] == "Violated"


@pytest.mark.parametrize("operation", ["countermodel", "distinguishing"])
def test_nonvacuity_inspection_shares_the_search_budget(operation):
    def run(limit):
        options = dict(max_domain_size=0, nonvacuous_for=Top(), max_evaluations=limit)
        return (find_countermodel(ENV, (), Bottom(), **options) if operation == "countermodel"
                else find_distinguishing_model(ENV, Top(), Bottom(), **options))
    needed = 2 if operation == "countermodel" else 3
    limited = run(needed - 1)
    assert limited.status == "ResourceLimit" and limited.evaluations == needed - 1
    found = run(needed)
    assert found.status == "Found" and found.evaluations == needed
    assert found.to_dict()["max_evaluations"] == needed
    assert len(found.to_dict()["nonvacuous_for_meaning_id"]) == 64


def test_nonvacuity_quantifiers_are_required_even_when_hidden_by_true_disjunction():
    formula = Or(Top(), Exists("item", Top()))
    result = find_distinguishing_model(ENV, Top(), Bottom(), max_domain_size=0,
                                      nonvacuous_for=formula)
    assert result.status == "NotFound"


def test_nonvacuity_is_per_occurrence_even_when_the_ast_node_is_shared():
    data = ENV.to_dict()
    data["vocabulary"]["sorts"]["other"] = {"description": "Other"}
    env = Environment(data)
    # A shared equality expression is well typed under either sort. With two
    # items but one other, its antecedent is possible in exactly one occurrence.
    shared = Implies(Not(Eq(Var(0), Var(1))), Top())
    formula = Or(Forall("item", Forall("item", shared)),
                 Forall("other", Forall("other", shared)))
    premises = (Exists("item", Exists("item", Not(Eq(Var(0), Var(1))))),
                Forall("other", Forall("other", Eq(Var(0), Var(1)))))
    options = dict(min_domain_size=1, max_domain_size=2)
    assert find_countermodel(env, premises, Bottom(), **options).status == "Found"
    result = find_countermodel(env, premises, Bottom(), nonvacuous_for=formula, **options)
    assert result.status == "NotFound"


@pytest.mark.parametrize("options", [
    {"min_domain_size": -1}, {"min_domain_size": True},
    {"min_domain_size": 2, "max_domain_size": 1}, {"nonempty_domains": 1},
    {"max_models": -1}, {"max_evaluations": -1}, {"max_evaluations": True},
])
def test_search_option_validation_consistent(options):
    with pytest.raises(ValueError):
        find_countermodel(ENV, (), Bottom(), **options)
    with pytest.raises(ValueError):
        find_distinguishing_model(ENV, Top(), Bottom(), **options)


def test_public_countermodel_check_always_revalidates_forged_model_identity():
    forged = FiniteModel({"item": ()}, {}, {"active": frozenset()}, ENV.environment_id, "0" * 64)
    with pytest.raises(InvalidModel):
        check_countermodel(ENV, (), Bottom(), forged)
