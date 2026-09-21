import json

import pytest

from ve.ast import Binary, Bottom, Const, Eq, Exists, Forall, Implies, Not, Top, Unary, Var
from ve.environment import Environment
from ve.errors import InvalidModel, ResourceLimit, VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.search import _subsets, check_countermodel, find_countermodel


@pytest.fixture
def env():
    return Environment.from_dict({
        "language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {"item": {"description": "An item."}},
            "predicates": {
                "marked": {"arguments": ["item"], "description": "Marked."},
                "edge": {"arguments": ["item", "item"], "description": "An edge."},
            },
            "constants": {"origin": {"sort": "item", "description": "The origin."}},
        },
    })


def model(env, *, domain=("a",), marked=(), edge=(), origin="a"):
    return FiniteModel.from_dict(env, {"complete": True, "domains": {"item": list(domain)},
        "constants": {"origin": origin}, "relations": {"marked": [[x] for x in marked],
                                                           "edge": [list(x) for x in edge]}})


def test_model_is_canonical_immutable_and_identity_bearing(env):
    wire = {"complete": True, "domains": {"item": ["b", "a"]}, "constants": {"origin": "a"},
            "relations": {"marked": [["b"]], "edge": [["b", "a"]]}}
    finite = FiniteModel.from_dict(env, wire)
    wire["domains"]["item"].append("later")
    assert finite.domains["item"] == ("a", "b")
    assert finite.to_dict()["relations"]["edge"] == [["b", "a"]]
    assert len(finite.model_id) == 64
    with pytest.raises(TypeError):
        finite.constants["origin"] = "b"


@pytest.mark.parametrize("mutation", [
    lambda w: w.update(complete=1),
    lambda w: w["domains"]["item"].append("a"),
    lambda w: w["relations"]["marked"].append(["missing"]),
    lambda w: w["relations"].pop("edge"),
])
def test_model_rejects_nonliteral_complete_duplicates_dangling_and_missing(env, mutation):
    wire = {"complete": True, "domains": {"item": ["a"]}, "constants": {"origin": "a"},
            "relations": {"marked": [], "edge": []}}
    mutation(wire)
    with pytest.raises(InvalidModel): FiniteModel.from_dict(env, wire)


def test_json_duplicate_model_key_rejected(env):
    raw = '{"complete":true,"complete":true,"domains":{"item":["a"]},"constants":{"origin":"a"},"relations":{"marked":[],"edge":[]}}'
    with pytest.raises(Exception): FiniteModel.from_json(env, raw)


def test_explanations_surface_empty_domain_and_false_antecedent():
    empty_env = Environment.from_dict({"language":"ve.core@0","profile":"relational-fol@0",
        "spec_revision":"ve-v0-draft-2026-09-20","vocabulary":{"sorts":{"item":{"description":"Item."}},
        "predicates":{},"constants":{}}})
    finite = FiniteModel.from_dict(empty_env, {"complete":True,"domains":{"item":[]},"constants":{},"relations":{}})
    universal = evaluate(empty_env, Forall("item", Bottom()), finite)
    implication = evaluate(empty_env, Implies(Exists("item", Top()), Bottom()), finite)
    existential = evaluate(empty_env, Exists("item", Top()), finite)
    assert universal.value is True and "empty" in universal.explanation.children[0].detail
    assert implication.value is True and "antecedent" in implication.explanation.children[0].detail
    assert existential.value is False and "empty" in existential.explanation.children[0].detail


def test_nested_binding_is_nearest_first(env):
    finite = model(env, domain=("a", "b"), edge=(("a", "b"),))
    formula = Exists("item", Exists("item", Binary("edge", Var(1), Var(0))))
    result = evaluate(env, formula, finite)
    assert result.value is True
    assert "witness" in result.explanation.children[0].detail


def test_evaluation_resource_limit_is_not_false(env):
    result = evaluate(env, Forall("item", Unary("marked", Var(0))), model(env), max_evaluations=1)
    assert (result.status, result.value, result.evaluations) == ("ResourceLimit", None, 1)


def test_trace_budget_is_a_resource_limit(env):
    result = evaluate(env, Forall("item", Unary("marked", Var(0))), model(env),
                      max_evaluations=100, max_trace_nodes=1)
    assert result.status == "ResourceLimit" and result.value is None


def test_model_runtime_limits_have_resource_classification(env):
    with pytest.raises(ResourceLimit):
        model(env, domain=tuple(f"e{i}" for i in range(1001)), origin="e0")
    with pytest.raises(ResourceLimit):
        model(env, domain=("a" * 65,), origin="a" * 65)


def test_search_finds_empty_domain_countermodel_and_checks_it():
    empty_env = Environment.from_dict({"language":"ve.core@0","profile":"relational-fol@0",
        "spec_revision":"ve-v0-draft-2026-09-20","vocabulary":{"sorts":{"item":{"description":"Item."}},
        "predicates":{},"constants":{}}})
    result = find_countermodel(empty_env, [Forall("item", Top())], Exists("item", Top()), max_domain_size=1)
    assert result.status == "Found"
    assert result.model.domains["item"] == ()
    checked = check_countermodel(empty_env, [Forall("item", Top())], Exists("item", Top()), result.model)
    assert checked.valid and checked.premise_values == (True,) and checked.conclusion_value is False


def test_relation_subset_enumerator_is_exhaustive():
    subsets = list(_subsets({"item": ["a", "b"]}, ("item",)))
    assert len(subsets) == 4
    assert {tuple(tuple(row) for row in subset) for subset in subsets} == {
        (), (("a",),), (("b",),), (("a",), ("b",))}


def test_search_allows_aliasing_constants_and_distinguishes_not_found(env):
    conclusion = Eq(Const("origin"), Const("origin"))
    result = find_countermodel(env, (), conclusion, max_domain_size=1, max_models=100)
    assert result.status == "NotFound"


def test_search_model_budget_is_explicit_resource_limit(env):
    result = find_countermodel(env, (), Top(), max_domain_size=2, max_models=0)
    assert result.status == "ResourceLimit" and result.models_checked == 0


def test_distinct_constant_names_do_not_assert_distinct_entities(env):
    data = env.to_dict()
    data["vocabulary"]["constants"]["other"] = {"sort": "item", "description": "Another constant."}
    two = Environment.from_dict(data)
    result = find_countermodel(two, (), Not(Eq(Const("origin"), Const("other"))), max_domain_size=1)
    assert result.status == "Found"
    assert result.model.constants["origin"] == result.model.constants["other"]


def test_search_reaches_two_entity_full_unary_relation(env):
    premises = [Exists("item", Exists("item", Not(Eq(Var(0), Var(1))))),
                Forall("item", Unary("marked", Var(0)))]
    result = find_countermodel(env, premises, Bottom(), max_domain_size=2, max_models=1000)
    assert result.status == "Found"
    assert len(result.model.domains["item"]) == len(result.model.relations["marked"]) == 2
    assert check_countermodel(env, premises, Bottom(), result.model).valid


def test_consumable_premises_cannot_silently_become_empty(env):
    with pytest.raises(VEError, match="sequence"):
        check_countermodel(env, iter([Bottom()]), Bottom(), model(env))


def test_revalidation_preserves_resource_error_class(env):
    forged = FiniteModel({"item": tuple(f"e{i}" for i in range(1001))}, {"origin": "e0"},
                         {"edge": frozenset(), "marked": frozenset()}, env.environment_id, "0" * 64)
    with pytest.raises(ResourceLimit):
        evaluate(env, Top(), forged)
