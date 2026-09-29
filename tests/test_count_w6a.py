"""Pinned W6 counting expansion and finite evaluation envelope."""
import pytest

from ve import ast
from ve.environment import Environment
from ve.errors import UnsupportedProfile, VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.surface.count import at_least, at_most, exactly, n_of_m


def fixture(n):
    env = Environment({"language": "ve.core@0.2", "profiles": ["relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"item": {"description": "an item"}},
                       "predicates": {name: {"arguments": ["item"], "description": name}
                                      for name in ("p", "s")}, "constants": {}}})
    entities = [f"e{i}" for i in range(1, n + 1)]
    model = FiniteModel.from_dict(env, {"complete": True, "domains": {"item": entities},
        "constants": {}, "relations": {name: [[e] for e in entities] for name in ("p", "s")}})
    p, s = ast.Unary("p", ast.Var(0)), ast.Unary("s", ast.Var(0))
    return env, model, p, s


@pytest.mark.parametrize("n,name,expected,work", [
    (8, "at least 8", "Satisfied", 359),
    (6, "exactly 6", "Satisfied", 120536),
    (6, "6 of 6", "Satisfied", 244997),
    (7, "exactly 7", "ResourceLimit", 1000000),
    (7, "7 of 7", "ResourceLimit", 1000000),
    (7, "at least 8", "ResourceLimit", 1000000),
])
def test_pinned_evaluation(n, name, expected, work):
    env, model, p, s = fixture(n)
    f = {"at least 8": lambda: at_least(env, "item", 8, p),
         "exactly 6": lambda: exactly(env, "item", 6, p),
         "6 of 6": lambda: n_of_m(env, "item", 6, 6, s, p),
         "exactly 7": lambda: exactly(env, "item", 7, p),
         "7 of 7": lambda: n_of_m(env, "item", 7, 7, s, p)}[name]()
    result = evaluate(env, f, model, trace=False)
    assert (result.status, result.evaluations) == (expected, work)
    assert result.value is (True if expected == "Satisfied" else None)


def test_canonical_scope_order_and_bounds():
    env, _, p, s = fixture(2)
    assert ast._to_data(at_least(env, "item", 2, p)) == [
        "exists", "item", ["and", ["unary", "p", ["var", 0]],
        ["exists", "item", ["and", ["not", ["eq", ["var", 0], ["var", 1]]],
        ["unary", "p", ["var", 0]]]]]]
    assert ast._to_data(at_least(env, "item", 0, p)) == ["top"]
    assert ast._to_data(at_most(env, "item", 0, p))[0] == "not"
    assert ast._to_data(n_of_m(env, "item", 2, 1, s, p))[0] == "and"
    for call in (lambda: at_least(env, "item", 9, p),
                 lambda: exactly(env, "item", 8, p),
                 lambda: at_most(env, "item", 8, p),
                 lambda: n_of_m(env, "item", 16, 18, s, p)):
        with pytest.raises(VEError, match="CountingBound"):
            call()
    with pytest.raises(UnsupportedProfile, match="numbers2"):
        at_least(env, "$int", 1, p)


def test_outer_reference_is_shifted_and_nested_binder_is_preserved():
    env, _, _, _ = fixture(2)
    # Source body sees counted x0 and surrounding x1. At the second witness,
    # x1 moves to x2; a nested binder still owns its x0.
    body = ast.Exists("item", ast.Eq(ast.Var(0), ast.Var(2)))
    expansion = ast._to_data(at_least(env, "item", 2, body))
    second_body = expansion[2][2][2][2]
    assert second_body == ["exists", "item", ["eq", ["var", 0], ["var", 3]]]
