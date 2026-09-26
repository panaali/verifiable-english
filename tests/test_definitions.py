"""W3 definition elaboration and the identity-bound declaration hook."""
from copy import deepcopy
import pytest

from ve import ast
from ve.definitions import compile_definitions, definitions_id, expand
from ve.environment import Environment
from ve.errors import VEError
from ve.errors import InvalidModel
from ve.background import background
from ve.model import FiniteModel
from ve.profiles import SPEC_REVISION


def environment():
    return Environment({
        "language": "ve.core@0.2",
        "profiles": ["definitions@0", "relational-fol@0"],
        "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {"point": {"description": "point"}},
            "predicates": {
                name: {"arguments": ["point"], "description": name}
                for name in ("base", "middle", "upper")
            },
            "constants": {},
        },
    })


def test_order_and_closed_biconditionals():
    env = environment()
    entries = {
        "upper": {"arguments": ["point"], "body": ["unary", "middle", ["var", 0]]},
        "middle": {"arguments": ["point"], "body": ["unary", "base", ["var", 0]]},
    }
    definitions = compile_definitions(env, entries, version="one")
    assert [d.name for d in definitions] == ["middle", "upper"]
    assert all(ast.check_formula(env, f) == f for f in expand(definitions))
    assert definitions_id(env, definitions, version="one") != definitions_id(
        env, definitions, version="two")
    altered = dict(entries)
    altered["middle"] = {"arguments": ["point"], "body": ["top"]}
    assert definitions_id(env, compile_definitions(env, altered, version="one"), version="one") != (
        definitions_id(env, definitions, version="one"))


@pytest.mark.parametrize("body, diagnostic", [
    (["unary", "upper", ["var", 0]], "DependencyCycle"),
    (["unary", "base", ["var", 1]], "Variable index"),
])
def test_reject_recursive_and_free(body, diagnostic):
    with pytest.raises(VEError, match=diagnostic):
        compile_definitions(environment(), {
            "upper": {"arguments": ["point"], "body": body},
        }, version="one")


def test_reject_mutual_cycle():
    with pytest.raises(VEError, match="DependencyCycle"):
        compile_definitions(environment(), {
            "upper": {"arguments": ["point"], "body": ["unary", "middle", ["var", 0]]},
            "middle": {"arguments": ["point"], "body": ["unary", "upper", ["var", 0]]},
        }, version="one")


def test_bound_definition_changes_identity_and_validates_model():
    raw = environment().to_dict()
    raw["vocabulary"]["predicates"]["middle"]["defined"] = {
        "arguments": ["point"], "body": ["unary", "base", ["var", 0]],
    }
    env = Environment(raw)
    assert env.to_dict() == raw
    assert [p.generator for p in background(env)] == ["definitions"]
    altered = deepcopy(raw)
    altered["vocabulary"]["predicates"]["middle"]["defined"]["body"] = ["top"]
    assert Environment(altered).environment_id != env.environment_id
    model = {"complete": True, "domains": {"point": ["p"]}, "constants": {},
             "relations": {"base": [["p"]], "middle": [["p"]], "upper": []}}
    FiniteModel.from_dict(env, model)
    model["relations"]["middle"] = []
    with pytest.raises(InvalidModel, match="defined predicate") as exc:
        FiniteModel.from_dict(env, model)
    assert exc.value.generator == "definitions"


def test_bound_definition_rejects_cycle_and_free_variable():
    raw = environment().to_dict()
    entry = raw["vocabulary"]["predicates"]["middle"]
    entry["defined"] = {"arguments": ["point"], "body": ["unary", "middle", ["var", 0]]}
    with pytest.raises(VEError, match="DependencyCycle"):
        Environment(raw)
    entry["defined"]["body"] = ["unary", "base", ["var", 1]]
    with pytest.raises(VEError, match="Variable index"):
        Environment(raw)
