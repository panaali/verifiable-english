import pytest

from ve import ast
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.errors import ResourceLimit, ShadowedVariable, SyntaxError, UnboundVariable
from ve.fol import document_from_named_fol, document_to_named_fol


@pytest.fixture
def env():
    return Environment({
        "language": LANGUAGE,
        "profile": PROFILE,
        "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {"service": {"description": "a service"},
                      "person": {"description": "a person"}},
            "predicates": {
                "deployed": {"arguments": ["service"], "description": "is deployed"},
                "owns": {"arguments": ["person", "service"], "description": "owns"},
            },
            "constants": {"api": {"sort": "service", "description": "the API"}},
        },
    })


def quantified(name, body=None, *, op="forall", sort="service"):
    return {"op": op, "sort": sort, "variable": name, "body": body or {"op": "top"}}


@pytest.mark.parametrize("name", ["Bad", "_bad", "bad-name", "naïve", ""])
def test_named_fol_rejects_non_identifier_binder_names(env, name):
    with pytest.raises(SyntaxError) as caught:
        document_from_named_fol(env, {"formulas": [quantified(name)]})
    assert caught.value.path == "/formulas/0/variable"


def test_named_fol_applies_identifier_length_limit_to_binders_and_references(env):
    too_long = "a" * 65
    with pytest.raises(ResourceLimit) as caught:
        document_from_named_fol(env, {"formulas": [quantified(too_long)]})
    assert caught.value.path == "/formulas/0/variable"

    value = {"formulas": [quantified("ok", {
        "op": "unary", "predicate": "deployed", "term": {"var": too_long}
    })]}
    with pytest.raises(ResourceLimit) as caught:
        document_from_named_fol(env, value)
    assert caught.value.path.endswith("/term/var")


@pytest.mark.parametrize("name", ["true", "there", "no", "service", "deployed", "api"])
def test_named_fol_rejects_reserved_and_schema_colliding_variables(env, name):
    with pytest.raises(SyntaxError):
        document_from_named_fol(env, {"formulas": [quantified(name)]})

    value = {"formulas": [quantified("s", {
        "op": "unary", "predicate": "deployed", "term": {"var": name}
    })]}
    with pytest.raises(SyntaxError):
        document_from_named_fol(env, value)


def test_named_fol_rejects_shadowing_but_allows_sibling_reuse(env):
    nested = quantified("a", quantified("a", op="exists", sort="person"))
    with pytest.raises(ShadowedVariable) as caught:
        document_from_named_fol(env, {"formulas": [nested]})
    assert caught.value.path == "/formulas/0/body/variable"

    siblings = {"op": "and", "left": quantified("a"), "right": quantified("a")}
    document_from_named_fol(env, {"formulas": [siblings]})


def test_named_fol_validates_variable_references_before_resolution(env):
    invalid = quantified("s", {
        "op": "unary", "predicate": "deployed", "term": {"var": 7}
    })
    with pytest.raises(SyntaxError) as caught:
        document_from_named_fol(env, {"formulas": [invalid]})
    assert caught.value.path.endswith("/term/var")

    free = {"op": "unary", "predicate": "deployed", "term": {"var": "s"}}
    with pytest.raises(UnboundVariable) as caught:
        document_from_named_fol(env, {"formulas": [free]})
    assert caught.value.path == "/formulas/0/term/var"


def test_generated_x_names_are_valid_and_resolve_to_the_nearest_binder(env):
    named = {"formulas": [quantified("x0", {
        "op": "exists", "sort": "person", "variable": "x1", "body": {
            "op": "binary", "predicate": "owns",
            "left": {"var": "x1"}, "right": {"var": "x0"},
        }
    })]}
    assert document_from_named_fol(env, named) == ast.Document((
        ast.Forall("service", ast.Exists("person", ast.Binary(
            "owns", ast.Var(0), ast.Var(1)
        ))),
    ))


def test_named_export_uses_preorder_names_resets_and_round_trips(env):
    document = ast.Document((
        ast.And(
            ast.Exists("service", ast.Unary("deployed", ast.Var(0))),
            ast.Forall("service", ast.Exists("person", ast.Binary(
                "owns", ast.Var(0), ast.Var(1)
            ))),
        ),
        ast.Exists("service", ast.Eq(ast.Var(0), ast.Const("api"))),
    ))
    named = document_to_named_fol(env, document)
    left, right = named["formulas"][0]["left"], named["formulas"][0]["right"]
    assert left["variable"] == "x0"
    assert right["variable"] == "x1"
    assert right["body"]["variable"] == "x2"
    assert named["formulas"][1]["variable"] == "x0"
    assert document_from_named_fol(env, named) == document
