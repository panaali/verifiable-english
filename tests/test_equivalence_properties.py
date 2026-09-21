"""Independent truth tables and finite semantics, not the production evaluator."""
from itertools import product

from hypothesis import given, settings, strategies as st

from ve.ast import (And, Binary, Bottom, Const, Eq, Exists, Forall, Implies,
                    Not, Or, Top, Unary, Var)
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.equivalence import Budgets, compare, validate_reference
from ve.attacks import validate_attack


ENV = Environment.from_dict({
    'language': LANGUAGE, 'profile': PROFILE, 'spec_revision': SPEC_REVISION,
    'vocabulary': {'sorts': {'item': {'description': 'Item.'}},
        'predicates': {'p': {'arguments': ['item'], 'description': 'P.'},
                       'r': {'arguments': ['item', 'item'], 'description': 'R.'}},
        'constants': {'a': {'sort': 'item', 'description': 'A.'}}},
})


def denote(f, domain, p, r, a, bindings=()):
    def term(t):
        return a if type(t) is Const else bindings[t.index]
    def visit(child):
        return denote(child, domain, p, r, a, bindings)
    kind = type(f)
    if kind is Top: return True
    if kind is Bottom: return False
    if kind is Unary: return term(f.term) in p
    if kind is Binary: return (term(f.left), term(f.right)) in r
    if kind is Eq: return term(f.left) == term(f.right)
    if kind is Not: return not visit(f.body)
    if kind is And: return visit(f.left) and visit(f.right)
    if kind is Or: return visit(f.left) or visit(f.right)
    if kind is Implies: return not visit(f.left) or visit(f.right)
    values = (denote(f.body, domain, p, r, a, (x,) + bindings) for x in domain)
    if kind is Forall: return all(values)
    if kind is Exists: return any(values)
    raise AssertionError(kind)


def models(max_size=2):
    # Constants need inhabitants; enumerate every constant denotation, too.
    for size in range(1, max_size + 1):
        domain = tuple(f'e{i}' for i in range(size))
        pairs = tuple(product(domain, repeat=2))
        for a in domain:
            for p_bits in range(1 << size):
                p = {x for i, x in enumerate(domain) if p_bits & (1 << i)}
                for r_bits in range(1 << len(pairs)):
                    r = {x for i, x in enumerate(pairs) if r_bits & (1 << i)}
                    yield domain, p, r, a


def denote_model(f, model):
    return denote(f, model.domains['item'], {row[0] for row in model.relations['p']},
                  model.relations['r'], model.constants['a'])


GROUND = st.recursive(st.sampled_from([Top(), Bottom(), Unary('p', Const('a')),
                                     Binary('r', Const('a'), Const('a'))]),
    lambda child: st.one_of(child.map(Not), st.tuples(child, child).map(lambda x: And(*x)),
        st.tuples(child, child).map(lambda x: Or(*x)),
        st.tuples(child, child).map(lambda x: Implies(*x))), max_leaves=6)


@given(GROUND, GROUND)
@settings(max_examples=160, deadline=None, derandomize=True)
def test_ground_oracle_and_attack_classification_equal_exhaustive_truth_tables(a, b):
    values = [(denote(a, *m), denote(b, *m)) for m in models(1)]
    ab = any(x and not y for x, y in values)
    ba = any(y and not x for x, y in values)
    result = compare(ENV, a, b)
    assert result.status == ('DIFFERENT' if ab or ba else 'EQUIVALENT')
    relation = {(False, False): 'equivalent', (False, True): 'weaker',
                (True, False): 'stronger', (True, True): 'incomparable'}[ab, ba]
    assert result.relation == relation
    attack = validate_attack(ENV, a, b)
    assert attack.status == ('VALID' if ab or ba else 'REJECTED')
    for witness in attack.witnesses:
        from ve.model import FiniteModel
        model = FiniteModel.from_dict(ENV, witness['model'])
        assert denote_model(a, model) != denote_model(b, model)


@st.composite
def formulas(draw, depth=3, binders=0):
    terms = [Const('a')] + [Var(i) for i in range(binders)]
    atoms = [Top(), Bottom()]
    atoms += [Unary('p', t) for t in terms]
    atoms += [ctor(x, y) if ctor is Eq else Binary('r', x, y)
              for x in terms for y in terms for ctor in (Eq, Binary)]
    if depth == 0:
        return draw(st.sampled_from(atoms))
    child = formulas(depth - 1, binders)
    bound = formulas(depth - 1, binders + 1)
    return draw(st.one_of(st.sampled_from(atoms), child.map(Not),
        st.tuples(child, child).map(lambda x: And(*x)),
        st.tuples(child, child).map(lambda x: Or(*x)),
        st.tuples(child, child).map(lambda x: Implies(*x)),
        bound.map(lambda f: Forall('item', f)), bound.map(lambda f: Exists('item', f))))


@given(formulas(), formulas())
@settings(max_examples=150, deadline=None, derandomize=True)
def test_quantified_findings_are_sound_against_brute_force(a, b):
    result = compare(ENV, a, b, Budgets(max_proof_steps=1500))
    values = [(denote(a, *m), denote(b, *m)) for m in models()]
    for left, right, direction in ((a, b, result.a_implies_b), (b, a, result.b_implies_a)):
        if direction.status == 'ENTAILED':
            assert all(not denote(left, *m) or denote(right, *m) for m in models())
        if direction.model is not None:
            assert denote_model(left, direction.model)
            assert not denote_model(right, direction.model)
    if result.status == 'EQUIVALENT':
        assert all(x == y for x, y in values)
    # The entire <=2 domain search fits these budgets. Every bounded difference
    # must be found, while lack of a bounded difference proves nothing globally.
    if any(x != y for x, y in values):
        assert result.status == 'DIFFERENT'


@given(formulas(depth=2))
@settings(max_examples=60, deadline=None, derandomize=True)
def test_reference_witnesses_are_sound_against_independent_semantics(f):
    result = validate_reference(ENV, f, Budgets(max_proof_steps=1500))
    if result.valid:
        assert denote_model(f, result.satisfying_model)
        assert not denote_model(f, result.falsifying_model)
    if result.reason == 'valid':
        assert all(denote(f, *m) for m in models())
    if result.reason == 'unsatisfiable':
        assert not any(denote(f, *m) for m in models())
