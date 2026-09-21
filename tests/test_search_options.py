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


def review_search_environment(predicate_count=7):
    data = ENV.to_dict()
    data['vocabulary'] = {
        'sorts': {'service': {'description': 'Service'}, 'person': {'description': 'Person'}},
        'predicates': {
            name: {'arguments': args, 'description': name}
            for name, args in list({
                'owns': ['person', 'service'], 'audits': ['person', 'service'],
                'links': ['service', 'service'], 'serves': ['person', 'service'],
                'dep': ['service'], 'rev': ['service'], 'ready': ['person'],
            }.items())[:predicate_count]
        },
        'constants': {},
    }
    return Environment(data)


@pytest.mark.parametrize('predicate_count', [5, 7])
def test_review_quantifier_swap_found_with_default_budgets(predicate_count):
    from ve import Binary
    env = review_search_environment(predicate_count)
    a = Forall('service', Exists('person', Binary('owns', Var(0), Var(1))))
    b = Exists('person', Forall('service', Binary('owns', Var(1), Var(0))))
    # Exclude the trivial empty-sort witness: this must find the real dependency
    # counterexample with two services and two different owners.
    result = find_distinguishing_model(env, a, b, nonvacuous_for=a)
    assert result.status == 'Found', result
    assert result.models_checked < 100 and result.evaluations < 10_000
    assert evaluate(env, a, result.model).value is True
    assert evaluate(env, b, result.model).value is False
    assert all(len(domain) == 2 for domain in result.model.domains.values())
    assert len(result.model.relations['owns']) == 2
    assert all(not rows for name, rows in result.model.relations.items() if name != 'owns')


def test_unused_predicates_do_not_multiply_models_or_trigger_atom_limit(monkeypatch):
    import ve.search as search
    env = review_search_environment()
    # Unused declarations must not even consume the possible-atom space cap.
    monkeypatch.setattr(search, 'MAX_TUPLES', 1)
    result = find_distinguishing_model(env, Top(), Top(), min_domain_size=1)
    assert result.status == 'NotFound' and result.models_checked == 4
    assert find_countermodel(env, (), Top(), min_domain_size=1).models_checked == 4


def test_enumeration_small_domains_and_globally_sparse_relations_first():
    from itertools import product
    from ve.search import _domain_sizes, _models, _relation_assignments, _subsets
    vectors = list(_domain_sizes([0, 1, 0], 2))
    assert len(vectors) == len(set(vectors)) == 18
    assert vectors == sorted(product(range(3), range(1, 3), range(3)), key=lambda v: (sum(v), v))
    assert list(_domain_sizes([], 2)) == [()]
    assert list(_domain_sizes([1], 0)) == []
    env = review_search_environment()
    domains = {'service': ['e0', 'e1'], 'person': ['e0']}
    assignments = list(_relation_assignments(env, domains, frozenset({'owns', 'dep'})))
    assert len(assignments) == 16  # Four used atoms, each interpretation exactly once.
    assert len({repr(rows) for rows in assignments}) == 16
    counts = [sum(map(len, rows.values())) for rows in assignments]
    assert counts == sorted(counts)
    assert all(not rows['audits'] and not rows['rev'] for rows in assignments)
    subsets = list(_subsets(domains, ('service',)))
    assert [len(s) for s in subsets] == [0, 1, 1, 2]
    models = list(_models(env, 1, 2, frozenset({'dep'})))
    totals = [sum(map(len, model.domains.values())) for model in models]
    assert totals == sorted(totals)


@pytest.mark.parametrize('operation', ['countermodel', 'distinguishing'])
def test_used_predicates_include_every_formula_and_nonvacuity_filter(operation):
    env = review_search_environment()
    a = Exists('service', Unary('dep', Var(0)))
    b = Forall('service', Not(Unary('rev', Var(0))))
    guard = Forall('person', Implies(Unary('ready', Var(0)), Top()))
    options = dict(nonempty_domains=True, max_domain_size=1, nonvacuous_for=guard)
    result = (find_countermodel(env, (a,), b, **options) if operation == 'countermodel'
              else find_distinguishing_model(env, And(a, Not(b)), Bottom(), **options))
    assert result.status == 'Found'
    assert all(result.model.relations[name] for name in ('dep', 'rev', 'ready'))
    assert all(not result.model.relations[name] for name in ('owns', 'audits', 'links', 'serves'))


@pytest.mark.parametrize('operation', ['countermodel', 'distinguishing'])
def test_review_clause_nonvacuity_excludes_empty_guard_relation(operation):
    env = review_search_environment()
    clause = Forall('service', Or(Not(Unary('dep', Var(0))), Unary('rev', Var(0))))
    no_deployed = Forall('service', Not(Unary('dep', Var(0))))
    def run(semantic):
        options = dict(nonvacuous_for=clause, semantic_nonvacuity=semantic)
        return (find_countermodel(env, (no_deployed,), Bottom(), **options)
                if operation == 'countermodel' else
                find_distinguishing_model(env, no_deployed, Bottom(), **options))
    assert run(False).status == 'Found'  # Legacy syntactic behavior is explicit.
    assert run(True).status == 'NotFound'
    found = find_countermodel(env, (clause,), Bottom(), nonvacuous_for=clause,
                              semantic_nonvacuity=True)
    assert found.status == 'Found'
    assert found.model.relations['dep'] and found.model.relations['rev']
    assert found.to_dict()['semantic_nonvacuity'] is True


def test_semantic_guard_matches_implication_across_all_small_interpretations():
    from ve.search import _models, _nonvacuous
    env = review_search_environment()
    p, q = Unary('dep', Var(0)), Unary('rev', Var(0))
    implication = Forall('service', Implies(p, q))
    clauses = [Forall('service', Or(Not(p), q)), Forall('service', Or(q, Not(p)))]
    for model in _models(env, 0, 2, frozenset({'dep', 'rev'})):
        expected, _, exhausted = _nonvacuous(env, implication, model, 10_000, semantic=True)
        assert not exhausted
        for clause in clauses:
            actual, _, exhausted = _nonvacuous(env, clause, model, 10_000, semantic=True)
            assert actual == expected and not exhausted


def test_semantic_clause_guard_is_joint_per_occurrence_and_checks_hidden_branches():
    from ve.search import _nonvacuous
    env = review_search_environment()
    p, q = Unary('dep', Var(0)), Unary('rev', Var(0))
    # Individually possible but never simultaneous: dep={a}, rev={b}.
    model = FiniteModel.from_dict(env, {
        'complete': True, 'domains': {'service': ['a', 'b'], 'person': ['p']}, 'constants': {},
        'relations': {name: ([['a']] if name == 'dep' else [['b']] if name == 'rev' else [])
                      for name in env.predicates}})
    for body in (Or(Not(p), Or(Top(), Not(q))), Or(Or(Not(q), Top()), Not(p))):
        hidden = Or(Top(), Forall('service', body))
        assert _nonvacuous(env, hidden, model, 1000, semantic=True)[0] is False
    # A hit at one disjunction must not satisfy a separate impossible guard.
    separate = Forall('service', And(Or(Not(p), Top()), Or(Not(And(p, q)), Top())))
    assert _nonvacuous(env, separate, model, 1000, semantic=True)[0] is False
    # No universal binder: clause checking is deliberately not applied.
    existential = Exists('service', Or(Not(And(p, q)), Top()))
    assert _nonvacuous(env, existential, model, 1000, semantic=True)[0] is True


def test_semantic_nonvacuity_budget_is_shared_and_exhaustion_is_not_notfound():
    env = review_search_environment()
    clause = Forall('service', Or(Not(Unary('dep', Var(0))), Top()))
    options = dict(min_domain_size=1, max_domain_size=1, nonvacuous_for=clause,
                   semantic_nonvacuity=True)
    found = find_distinguishing_model(env, Top(), Bottom(), **options)
    assert found.status == 'Found'
    limit = found.evaluations - 1
    result = find_distinguishing_model(env, Top(), Bottom(), max_evaluations=limit, **options)
    assert (result.status, result.evaluations) == ('ResourceLimit', limit)
    assert not result.model


@pytest.mark.parametrize('options', [
    {'semantic_nonvacuity': True}, {'semantic_nonvacuity': 1},
    {'max_domain_size': True}, {'max_models': True}, {'max_domain_size': -1},
])
def test_new_and_boolean_option_validation_is_shared(options):
    with pytest.raises(ValueError):
        find_countermodel(ENV, (), Bottom(), **options)
    with pytest.raises(ValueError):
        find_distinguishing_model(ENV, Top(), Bottom(), **options)
