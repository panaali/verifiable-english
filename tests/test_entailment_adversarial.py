"""Adversarial checks for the small trusted tableau replayer."""

import copy
from itertools import product

import pytest
from hypothesis import given, settings, strategies as st

from ve.ast import (And, Binary, Bottom, Const, Eq, Exists, Forall, Implies,
                    Not, Or, Top, Unary, Var)
from ve.entailment import check_entailment_certificate, prove_entailment
from ve.environment import Environment
from ve.errors import TypeMismatch


def environment(*, constants=True):
    return Environment.from_dict({
        "language": "ve.core@0",
        "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {"left": {"description": "Left."},
                      "right": {"description": "Right."}},
            "predicates": {
                "marked": {"arguments": ["left"], "description": "Marked."},
                "rel": {"arguments": ["left", "right"], "description": "Related."},
            },
            "constants": ({"a": {"sort": "left", "description": "A."},
                           "b": {"sort": "left", "description": "B."},
                           "r": {"sort": "right", "description": "R."}}
                          if constants else {}),
        },
    })


def test_dependent_witness_is_not_reused_as_a_uniform_witness():
    env = environment(constants=False)
    pointwise = Forall("left", Exists(
        "right", Binary("rel", Var(1), Var(0))))
    uniform = Exists("right", Forall(
        "left", Binary("rel", Var(0), Var(1))))
    # Two left objects may require two different right witnesses.
    assert prove_entailment(env, [pointwise], uniform, max_steps=2_000).status == "NotFound"


def test_quantifier_alternation_with_a_fixed_parameter_certifies():
    env = environment()
    premise = Forall("left", Exists(
        "right", Binary("rel", Var(1), Var(0))))
    conclusion = Exists("right", Binary("rel", Const("a"), Var(0)))
    result = prove_entailment(env, [premise], conclusion, max_steps=2_000)
    assert result.status == "Found"
    assert check_entailment_certificate(
        env, [premise], conclusion, result.certificate, max_steps=2_000
    ).valid


def test_aliases_substitute_but_unique_names_are_not_assumed():
    env = environment()
    marked_a = Unary("marked", Const("a"))
    marked_b = Unary("marked", Const("b"))
    result = prove_entailment(env, [Eq(Const("a"), Const("b")), marked_a], marked_b)
    assert result.status == "Found"
    assert prove_entailment(env, [], Not(Eq(Const("a"), Const("b")))).status == "NotFound"


def test_cross_sort_equality_is_rejected_before_certificate_replay():
    env = environment()
    with pytest.raises(TypeMismatch):
        prove_entailment(env, [], Eq(Const("a"), Const("r")))


@pytest.mark.parametrize("bad_trace", [
    None,
    [],
    {"rule": "close", "extra": None},
    {"rule": "expand", "at": False, "children": []},
    {"rule": "expand", "at": 0, "parameter": [], "children": []},
    {"rule": "expand", "at": 0, "children": "not-a-list"},
])
def test_hostile_builtin_trace_shapes_are_total(bad_trace):
    env = environment()
    premise = Unary("marked", Const("a"))
    result = prove_entailment(env, [premise], premise)
    certificate = copy.deepcopy(result.certificate)
    certificate["trace"] = bad_trace
    checked = check_entailment_certificate(env, [premise], premise, certificate)
    assert not checked.valid
    assert checked.status == "InvalidCertificate"


def test_zero_replay_budget_never_accepts_even_immediate_closure():
    env = environment()
    formula = Unary("marked", Const("a"))
    result = prove_entailment(env, [formula], formula)
    checked = check_entailment_certificate(
        env, [formula], formula, result.certificate, max_steps=0)
    assert not checked.valid and checked.status == "ResourceLimit"


def test_certificate_metadata_cannot_invoke_attacker_comparison_code():
    env = environment()
    result = prove_entailment(env, [], Top())

    class Bomb:
        def __eq__(self, other):
            raise RuntimeError("hostile equality ran")

        def __ne__(self, other):
            raise RuntimeError("hostile inequality ran")

    certificate = dict(result.certificate)
    certificate["environment_id"] = Bomb()
    checked = check_entailment_certificate(env, [], Top(), certificate)
    assert not checked.valid and checked.status == "InvalidCertificate"


TWO_SORT_ENV = environment()


def _terms(sort, context):
    constants = ([Const("a"), Const("b")] if sort == "left" else [Const("r")])
    variables = [Var(index) for index, bound_sort in enumerate(context)
                 if bound_sort == sort]
    return constants + variables


@st.composite
def two_sort_formula(draw, depth=2, context=()):
    left = _terms("left", context)
    right = _terms("right", context)
    leaves = [st.just(Top()), st.just(Bottom()),
              st.sampled_from(left).map(lambda term: Unary("marked", term)),
              st.tuples(st.sampled_from(left), st.sampled_from(right)).map(
                  lambda terms: Binary("rel", *terms)),
              st.tuples(st.sampled_from(left), st.sampled_from(left)).map(
                  lambda terms: Eq(*terms)),
              st.tuples(st.sampled_from(right), st.sampled_from(right)).map(
                  lambda terms: Eq(*terms))]
    if depth == 0:
        return draw(st.one_of(leaves))
    child = two_sort_formula(depth - 1, context)
    left_bound = two_sort_formula(depth - 1, ("left",) + context)
    right_bound = two_sort_formula(depth - 1, ("right",) + context)
    return draw(st.one_of(*(leaves + [
        child.map(Not),
        st.tuples(child, child).map(lambda values: And(*values)),
        st.tuples(child, child).map(lambda values: Or(*values)),
        st.tuples(child, child).map(lambda values: Implies(*values)),
        left_bound.map(lambda body: Forall("left", body)),
        left_bound.map(lambda body: Exists("left", body)),
        right_bound.map(lambda body: Forall("right", body)),
        right_bound.map(lambda body: Exists("right", body)),
    ])))


def _denote_term(term, constants, bindings):
    return constants[term.name] if type(term) is Const else bindings[term.index]


def _denote(formula, domains, constants, marked, relation, bindings=()):
    kind = type(formula)
    if kind is Top:
        return True
    if kind is Bottom:
        return False
    if kind is Unary:
        return _denote_term(formula.term, constants, bindings) in marked
    if kind is Binary:
        return (_denote_term(formula.left, constants, bindings),
                _denote_term(formula.right, constants, bindings)) in relation
    if kind is Eq:
        return (_denote_term(formula.left, constants, bindings)
                == _denote_term(formula.right, constants, bindings))
    if kind is Not:
        return not _denote(formula.body, domains, constants, marked, relation, bindings)
    if kind is And:
        return (_denote(formula.left, domains, constants, marked, relation, bindings)
                and _denote(formula.right, domains, constants, marked, relation, bindings))
    if kind is Or:
        return (_denote(formula.left, domains, constants, marked, relation, bindings)
                or _denote(formula.right, domains, constants, marked, relation, bindings))
    if kind is Implies:
        return (not _denote(formula.left, domains, constants, marked, relation, bindings)
                or _denote(formula.right, domains, constants, marked, relation, bindings))
    values = domains[formula.sort]
    results = (_denote(formula.body, domains, constants, marked, relation,
                       (value,) + bindings) for value in values)
    return all(results) if kind is Forall else any(results)


def _subsets(values):
    values = tuple(values)
    for mask in range(1 << len(values)):
        yield {value for index, value in enumerate(values) if mask & (1 << index)}


def _small_two_sort_models():
    for left_size, right_size in product((1, 2), repeat=2):
        left = tuple(f"l{i}" for i in range(left_size))
        right = tuple(f"r{i}" for i in range(right_size))
        domains = {"left": left, "right": right}
        atoms = tuple(product(left, right))
        for a, b, r in product(left, left, right):
            constants = {"a": a, "b": b, "r": r}
            for marked, relation in product(_subsets(left), _subsets(atoms)):
                yield domains, constants, marked, relation


@given(st.lists(two_sort_formula(), max_size=1), two_sort_formula())
@settings(max_examples=35, deadline=None)
def test_two_sort_certificates_have_no_small_countermodel(premises, conclusion):
    result = prove_entailment(TWO_SORT_ENV, premises, conclusion, max_steps=2_000)
    if result.status != "Found":
        return
    assert check_entailment_certificate(
        TWO_SORT_ENV, premises, conclusion, result.certificate, max_steps=2_000
    ).valid
    for domains, constants, marked, relation in _small_two_sort_models():
        assert not (
            all(_denote(p, domains, constants, marked, relation) for p in premises)
            and not _denote(conclusion, domains, constants, marked, relation)
        )
