import pytest

from ve.ast import (And, Binary, Bottom, Const, Document, Eq, Exists, Forall,
                    Implies, Not, Or, Top, Unary, Var)
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.entailment import check_entailment_certificate
from ve.equivalence import (Budgets, DIFFERENT, EQUIVALENT, UNKNOWN, compare,
                            in_two_variable_fragment, is_stronger, is_weaker,
                            validate_reference, witness_quality)
from ve.errors import VEError
from ve.evaluate import evaluate
from ve.parser import parse


ENV = Environment.from_dict({
    'language': LANGUAGE, 'profile': PROFILE, 'spec_revision': SPEC_REVISION,
    'vocabulary': {'sorts': {'item': {'description': 'An item.'}},
                   'predicates': {p: {'arguments': ['item'], 'description': p} for p in ('p', 'q')},
                   'constants': {}},
})
P, Q = Unary('p', Var(0)), Unary('q', Var(0))
F = Forall('item', Implies(P, Q))


def test_alpha_identity_and_logical_equivalence_return_two_bound_certificates():
    renamed = parse(ENV, 'for every item renamed, (if (renamed is p), then (renamed is q)).\n').formulas[0]
    for other in (renamed, Not(Not(F)), Forall('item', Or(Not(P), Q))):
        result = compare(ENV, F, other)
        assert result.status == EQUIVALENT and result.relation == 'equivalent'
        assert len(result.certificates) == 2 and not result.models
        assert check_entailment_certificate(ENV, (F,), other, result.certificates['a_implies_b']).valid
        assert check_entailment_certificate(ENV, (other,), F, result.certificates['b_implies_a']).valid
        assert not is_weaker(ENV, other, F) and not is_stronger(ENV, other, F)


def test_strict_direction_and_incomparability():
    a, b = Exists('item', And(P, Q)), Exists('item', P)
    result = compare(ENV, a, b)
    assert (result.status, result.relation) == (DIFFERENT, 'weaker')
    assert result.failed_directions == ('b_not_implies_a',)
    assert is_weaker(ENV, b, a) is True
    assert is_stronger(ENV, a, b) is True
    assert compare(ENV, b, a).relation == 'stronger'
    result = compare(ENV, Exists('item', P), Exists('item', Q))
    assert result.relation == 'incomparable'
    assert len(result.models) == 2
    for direction, model in result.models.items():
        assert evaluate(ENV, Exists('item', P), model).value == (direction == 'a_not_implies_b')
        assert evaluate(ENV, Exists('item', Q), model).value == (direction == 'b_not_implies_a')


def test_empty_sorts_are_part_of_comparison_semantics():
    result = compare(ENV, Forall('item', P), Exists('item', P))
    assert result.relation == 'incomparable'
    assert not result.a_implies_b.model.domains['item']
    assert len(result.b_implies_a.model.domains['item']) == 2


def test_bounded_exhaustion_is_never_equivalence():
    # Every four objects include an equal pair: true on <=3, false at size 4.
    pairs = [Eq(Var(i), Var(j)) for i in range(4) for j in range(i)]
    at_most_three = pairs[0]
    for pair in pairs[1:]:
        at_most_three = Or(at_most_three, pair)
    for _ in range(4):
        at_most_three = Forall('item', at_most_three)
    assert not in_two_variable_fragment(at_most_three)
    result = compare(ENV, at_most_three, Top(), Budgets(max_domain_size=3))
    assert result.status == UNKNOWN
    assert result.a_implies_b.status == 'ENTAILED'
    assert result.b_implies_a.status == UNKNOWN and result.reason
    assert result.b_implies_a.attempts[-1]['status'] == 'NotFound'
    assert compare(ENV, at_most_three, Top(), Budgets(max_domain_size=4)).relation == 'weaker'


def test_difference_does_not_guess_the_other_implication():
    budgets = Budgets(max_proof_steps=0)
    a = Exists('item', P)
    result = compare(ENV, a, Top(), budgets)
    assert result.status == DIFFERENT and result.relation == 'unknown'
    assert result.failed_directions == ('b_not_implies_a',)
    assert is_weaker(ENV, Top(), a, budgets) is None
    zero = Budgets(0, 0, 0, 0)
    assert compare(ENV, a, a, zero).status == UNKNOWN


def test_reference_validation_requires_non_vacuous_satisfaction_and_nonvalidity():
    result = validate_reference(ENV, F)
    assert result.valid and result.status == 'VALID'
    assert evaluate(ENV, F, result.satisfying_model).value is True
    assert witness_quality(ENV, result.satisfying_model, F)['non_vacuous'] is True
    assert evaluate(ENV, F, result.falsifying_model).value is False
    for f, reason in ((Top(), 'valid'), (Bottom(), 'unsatisfiable'),
                      (Forall('item', Eq(Var(0), Var(0))), 'valid')):
        result = validate_reference(ENV, f)
        assert result.status == 'INVALID' and result.reason == reason
        assert result.certificates
    # This is satisfiable and non-valid, but every p->q instance is vacuous.
    result = validate_reference(ENV, And(Forall('item', Not(P)), F))
    assert result.status == 'INVALID' and result.reason == 'no_non_vacuous_model'
    # A satisfiable sentence restricted to empty domains cannot be a reference.
    assert validate_reference(ENV, Not(Exists('item', Top()))).status == 'INVALID'
    assert validate_reference(ENV, F, Budgets(0, 0, 0, 0)).status == UNKNOWN


def test_fragment_counts_live_names_not_quantifier_depth_or_index():
    assert in_two_variable_fragment(F)
    assert in_two_variable_fragment(Document((F, Exists('item', Eq(Var(0), Var(0))))))
    # Three nested binders, with the middle name reusable by the inner binder.
    reusable = Forall('item', Exists('item', Forall('item', Eq(Var(2), Var(0)))))
    assert in_two_variable_fragment(reusable)
    # Across two conjuncts, all three are live simultaneously.
    three = Forall('item', Forall('item', Exists('item',
        And(Eq(Var(2), Var(1)), Eq(Var(1), Var(0))))))
    assert not in_two_variable_fragment(three)
    # Even an unused binder must not capture either outer variable.
    assert not in_two_variable_fragment(Forall('item', Forall('item',
        Exists('item', Eq(Var(2), Var(1))))))
    assert in_two_variable_fragment(And(Exists('item', P), Exists('item', Q)))
    assert not in_two_variable_fragment(Eq(Var(0), Var(0)))
    assert not in_two_variable_fragment(Exists('item', Eq(Var(True), Var(0))))
    assert not in_two_variable_fragment(object())
    assert not in_two_variable_fragment(Forall([], Top()))
    assert not in_two_variable_fragment(Unary(123, Const('a')))
    assert not in_two_variable_fragment(Unary('p', Const('Not an identifier')))


def test_nonvacuity_tracks_outer_binders_for_nested_antecedents():
    f = Forall('item', Exists('item', Implies(Unary('p', Var(1)), Q)))
    result = validate_reference(ENV, f)
    assert result.valid
    assert witness_quality(ENV, result.satisfying_model, f)['non_vacuous'] is True


def test_invalid_inputs_are_not_unknown_logic():
    with pytest.raises(VEError):
        compare(ENV, Unary('missing', Const('missing')), Top())
    for kwargs in ({'max_models': -1}, {'max_proof_steps': True}, {'max_evaluations': 1_000_001}):
        with pytest.raises(ValueError):
            Budgets(**kwargs)


def test_proof_and_model_outputs_are_independently_replayed(monkeypatch):
    from ve.entailment import EntailmentResult
    from ve.search import CountermodelResult
    import ve.equivalence as oracle
    a = Exists('item', P)
    certificate = compare(ENV, Top(), Top()).a_implies_b.certificate
    monkeypatch.setattr(oracle, 'prove_entailment', lambda *args, **kwargs:
                        EntailmentResult('Found', certificate, 1))
    assert compare(ENV, a, Top()).status == DIFFERENT
    assert compare(ENV, a, Top()).relation == 'unknown'
    wrong_model = validate_reference(ENV, a).falsifying_model
    monkeypatch.setattr(oracle, 'find_countermodel', lambda *args, **kwargs:
                        CountermodelResult('Found', wrong_model, 1, 1, 2, 100))
    # Use formulas unlike the stolen proof and a model satisfying both sides.
    result = compare(ENV, Not(a), Not(a))
    assert result.status == UNKNOWN


@pytest.mark.parametrize('a,b', [
    (Forall('item', Exists('item', Unary('q', Var(1)))),
     Forall('item', Exists('item', Not(Not(Unary('q', Var(1))))))),
    (Exists('item', Forall('item', P)), Exists('item', Not(Exists('item', Not(P))))),
])
def test_reviewer_quantifier_starvation_regressions(a, b):
    result = compare(ENV, a, b)
    assert result.status == EQUIVALENT
    for left, right, certificate in ((a, b, result.a_implies_b.certificate),
                                     (b, a, result.b_implies_a.certificate)):
        assert check_entailment_certificate(ENV, (left,), right, certificate).valid


def test_empty_only_detail_needs_checked_models_and_conditional_proofs():
    from ve.search import check_countermodel
    a, b = Forall('item', Bottom()), Bottom()
    result = compare(ENV, a, b)
    assert result.status == DIFFERENT
    assert result.relation_detail == 'differs_only_on_empty_sorts'
    assert result.relation == 'stronger'
    assert result.nonempty_sorts == ('item',)
    assert not result.a_implies_b.model.domains['item']
    assert check_countermodel(ENV, (a,), b, result.a_implies_b.model).valid
    for label, left, right in [('a_implies_b', a, b), ('b_implies_a', b, a)]:
        assert check_entailment_certificate(ENV, (left, Exists('item', Top())), right,
                                           result.nonempty_certificates[label]).valid
        assert not check_entailment_certificate(ENV, (left,), right,
                                               result.nonempty_certificates[label]).valid
    assert result.to_dict()['nonempty_equivalence']['sorts'] == ['item']
    # An empty witness by itself is not an empty-only certificate.
    assert compare(ENV, a, b, Budgets(max_proof_steps=0)).relation_detail is None
    assert compare(ENV, Forall('item', P), Exists('item', P)).relation_detail is None


def test_strict_strength_is_refuted_even_when_other_direction_unknown():
    budgets = Budgets(max_proof_steps=0)
    a = Exists('item', P)
    assert is_weaker(ENV, a, Top(), budgets) is False
    assert is_stronger(ENV, Top(), a, budgets) is False
    assert is_weaker(ENV, Top(), a, budgets) is None
    assert is_stronger(ENV, a, Top(), budgets) is None


def test_empty_only_certificate_covers_multiple_sorts():
    from test_entailment_adversarial import environment
    env = environment(constants=False)
    a = Forall('left', Exists('right', Top()))
    b = Exists('right', Forall('left', Top()))
    result = compare(env, a, b)
    assert result.relation_detail == 'differs_only_on_empty_sorts'
    conditions = tuple(Exists(sort, Top()) for sort in result.nonempty_sorts)
    assert result.nonempty_sorts == ('left', 'right')
    for label, left, right in [('a_implies_b', a, b), ('b_implies_a', b, a)]:
        assert check_entailment_certificate(env, (left, *conditions), right,
                                           result.nonempty_certificates[label]).valid


def test_infinite_witness_chain_does_not_starve_countermodel_search():
    data = ENV.to_dict()
    data['vocabulary']['predicates']['r'] = {'arguments': ['item', 'item'], 'description': 'R.'}
    env = Environment.from_dict(data)
    a = And(Exists('item', Top()), Forall('item', Exists('item', Binary('r', Var(1), Var(0)))))
    b = Forall('item', Forall('item', Binary('r', Var(1), Var(0))))
    result = compare(env, a, b)
    assert result.status == DIFFERENT and result.a_implies_b.model is not None
    attempts = result.a_implies_b.attempts
    assert attempts[0]['kind'] == 'proof' and attempts[0]['status'] == 'ResourceLimit'
    assert attempts[1]['kind'] == 'search' and attempts[1]['status'] == 'Found'
    assert attempts[0]['steps'] < Budgets().max_proof_steps
