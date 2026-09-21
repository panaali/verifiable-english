"""Independent bounded semantic check of every generated positive certificate."""
from itertools import product

from hypothesis import given, settings, strategies as st

from ve.ast import (And, Bottom, Eq, Exists, Forall, Implies, Not, Or, Top,
                    Unary, Var)
from ve.entailment import check_entailment_certificate, prove_entailment
from ve.environment import Environment


ENV = Environment.from_dict({
    "language": "ve.core@0", "profile": "relational-fol@0",
    "spec_revision": "ve-v0-draft-2026-09-20",
    "vocabulary": {
        "sorts": {"item": {"description": "Item."}},
        "predicates": {"p": {"arguments": ["item"], "description": "P."}},
        "constants": {},
    },
})


@st.composite
def formula(draw, depth=3, binders=0):
    leaves = [st.just(Top()), st.just(Bottom())]
    if binders:
        index = st.integers(0, binders - 1)
        leaves += [index.map(lambda i: Unary("p", Var(i))),
                   st.tuples(index, index).map(lambda x: Eq(Var(x[0]), Var(x[1])))]
    if depth == 0:
        return draw(st.one_of(leaves))
    child = formula(depth - 1, binders)
    bound = formula(depth - 1, binders + 1)
    return draw(st.one_of(*(leaves + [child.map(Not),
        st.tuples(child, child).map(lambda x: And(*x)),
        st.tuples(child, child).map(lambda x: Or(*x)),
        st.tuples(child, child).map(lambda x: Implies(*x)),
        bound.map(lambda x: Forall("item", x)),
        bound.map(lambda x: Exists("item", x))])))


def denote(f, domain, relation, bindings=()):
    kind = type(f)
    if kind is Top: return True
    if kind is Bottom: return False
    if kind is Unary: return bindings[f.term.index] in relation
    if kind is Eq: return bindings[f.left.index] == bindings[f.right.index]
    if kind is Not: return not denote(f.body, domain, relation, bindings)
    if kind is And: return denote(f.left, domain, relation, bindings) and denote(f.right, domain, relation, bindings)
    if kind is Or: return denote(f.left, domain, relation, bindings) or denote(f.right, domain, relation, bindings)
    if kind is Implies: return not denote(f.left, domain, relation, bindings) or denote(f.right, domain, relation, bindings)
    if kind is Forall: return all(denote(f.body, domain, relation, (x,) + bindings) for x in domain)
    if kind is Exists: return any(denote(f.body, domain, relation, (x,) + bindings) for x in domain)
    raise AssertionError(kind)


def small_models():
    for size in range(3):
        domain = tuple(range(size))
        for bits in range(1 << size):
            yield domain, {x for x in domain if bits & (1 << x)}


@given(st.lists(formula(), max_size=2), formula())
@settings(max_examples=180, deadline=None)
def test_every_certificate_has_no_small_finite_countermodel(premises, conclusion):
    result = prove_entailment(ENV, premises, conclusion, max_steps=3000)
    if result.status != "Found":
        return
    assert check_entailment_certificate(ENV, premises, conclusion, result.certificate,
                                        max_steps=3000).valid
    for domain, relation in small_models():
        assert not (all(denote(p, domain, relation) for p in premises)
                    and not denote(conclusion, domain, relation))

