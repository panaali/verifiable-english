from hypothesis import given, settings, strategies as st

from ve.ast import (
    And,
    Bottom,
    Document,
    Eq,
    Exists,
    Forall,
    Implies,
    Not,
    Or,
    Top,
    Unary,
    Var,
    document_from_data,
    document_to_data,
)
from ve.environment import Environment
from ve.identity import meaning_id
from ve.model import FiniteModel
from ve.evaluate import evaluate
from ve.parser import canonicalize, parse
from ve.printer import print_document


ENV = Environment.from_dict(
    {
        "language": "ve.core@0",
        "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {"item": {"description": "An item."}},
            "predicates": {
                "marked": {"arguments": ["item"], "description": "Is marked."}
            },
            "constants": {},
        },
    }
)


@st.composite
def closed_formula(draw, max_depth=4):
    def at(depth, binders):
        leaves = [st.just(Top()), st.just(Bottom())]
        if binders:
            index = st.integers(min_value=0, max_value=binders - 1)
            leaves += [
                index.map(lambda i: Unary("marked", Var(i))),
                st.tuples(index, index).map(lambda pair: Eq(Var(pair[0]), Var(pair[1]))),
            ]
        if depth <= 0:
            return st.one_of(leaves)
        child = at(depth - 1, binders)
        under_binder = at(depth - 1, binders + 1)
        return st.one_of(
            leaves
            + [
                child.map(Not),
                st.tuples(child, child).map(lambda pair: And(*pair)),
                st.tuples(child, child).map(lambda pair: Or(*pair)),
                st.tuples(child, child).map(lambda pair: Implies(*pair)),
                under_binder.map(lambda body: Forall("item", body)),
                under_binder.map(lambda body: Exists("item", body)),
            ]
        )

    return draw(at(max_depth, 0))


def plain_denote(formula, domain, marked, bindings=()):
    if isinstance(formula, Top):
        return True
    if isinstance(formula, Bottom):
        return False
    if isinstance(formula, Unary):
        return bindings[formula.term.index] in marked
    if isinstance(formula, Eq):
        return bindings[formula.left.index] == bindings[formula.right.index]
    if isinstance(formula, Not):
        return not plain_denote(formula.body, domain, marked, bindings)
    if isinstance(formula, And):
        return plain_denote(formula.left, domain, marked, bindings) and plain_denote(formula.right, domain, marked, bindings)
    if isinstance(formula, Or):
        return plain_denote(formula.left, domain, marked, bindings) or plain_denote(formula.right, domain, marked, bindings)
    if isinstance(formula, Implies):
        return (not plain_denote(formula.left, domain, marked, bindings)) or plain_denote(formula.right, domain, marked, bindings)
    if isinstance(formula, Forall):
        return all(plain_denote(formula.body, domain, marked, (value,) + bindings) for value in domain)
    if isinstance(formula, Exists):
        return any(plain_denote(formula.body, domain, marked, (value,) + bindings) for value in domain)
    raise AssertionError(f"unhandled generated formula: {formula!r}")


@given(closed_formula())
@settings(max_examples=150, deadline=None)
def test_canonical_print_parse_roundtrip_and_idempotence(formula):
    document = Document((formula,))
    text = print_document(ENV, document)
    assert parse(ENV, text) == document
    assert canonicalize(ENV, text) == text


@given(closed_formula())
@settings(max_examples=150, deadline=None)
def test_ast_json_data_roundtrip_preserves_identity(formula):
    document = Document((formula,))
    recovered = document_from_data(ENV, document_to_data(ENV, document))
    assert recovered == document
    assert meaning_id(ENV, recovered) == meaning_id(ENV, document)


@given(
    formula=closed_formula(),
    domain=st.lists(st.sampled_from(["a", "b"]), unique=True),
    marked=st.sets(st.sampled_from(["a", "b"])),
)
@settings(max_examples=250, deadline=None)
def test_evaluator_matches_independent_denotation(formula, domain, marked):
    marked_in_domain = marked.intersection(domain)
    model = FiniteModel.from_dict(
        ENV,
        {
            "complete": True,
            "domains": {"item": domain},
            "constants": {},
            "relations": {"marked": [[item] for item in sorted(marked_in_domain)]},
        },
    )
    expected = plain_denote(formula, domain, marked_in_domain)
    result = evaluate(ENV, formula, model)
    assert result.value is expected
    assert result.status == ("Satisfied" if expected else "Violated")


def test_empty_domain_and_material_implication_corner_cases():
    model = FiniteModel.from_dict(
        ENV,
        {
            "complete": True,
            "domains": {"item": []},
            "constants": {},
            "relations": {"marked": []},
        },
    )
    formulas = (
        Forall("item", Unary("marked", Var(0))),
        Exists("item", Top()),
        Exists("item", Forall("item", Bottom())),
        Implies(Exists("item", Top()), Bottom()),
    )
    assert [evaluate(ENV, f, model).value for f in formulas] == [True, False, False, True]
