from copy import deepcopy

import pytest

from tests.test_data_flags import environment
from ve.ast import And, Binary, Const, Exists, Forall, Unary, Var
from ve.environment import Environment
from ve.errors import TypeMismatch
from ve.english import parse_english, render_english
from ve.surface.data import attribute_equals, attribute_property, member_of


def test_attribute_sugar_requires_functional_total_relation():
    env = environment()
    assert attribute_equals(env, "department", Const("alice"), Const("finance")) == Binary(
        "department", Const("alice"), Const("finance"))
    with pytest.raises(TypeMismatch, match="functional and total"):
        attribute_equals(environment(total=False), "department", Const("alice"), Const("finance"))


def test_member_convention_is_an_ordinary_declared_relation():
    data = deepcopy(environment().to_dict())
    data["vocabulary"]["sorts"]["group"] = {"description": "Group"}
    data["vocabulary"]["constants"]["staff"] = {"sort": "group", "description": "Staff"}
    data["vocabulary"]["predicates"]["member"] = {
        "arguments": ["person", "group"], "description": "Set membership"}
    env = Environment(data)
    assert member_of(env, Const("alice"), Const("staff")) == Binary(
        "member", Const("alice"), Const("staff"))


def test_writable_attribute_description_and_non_total_refusal():
    env = environment()
    atom = Binary("department", Const("alice"), Const("finance"))
    text = render_english(atom, env) + "."
    assert text == "The department of alice is finance."
    assert parse_english(env, text).formulas == (atom,)
    with pytest.raises(Exception, match="functional and total"):
        parse_english(environment(total=False), text)


def test_1000_attribute_english_round_trips():
    data = deepcopy(environment().to_dict())
    data["vocabulary"]["constants"] = {
        **{f"p{i}": {"sort": "person", "description": f"Person {i}"} for i in range(32)},
        **{f"s{i}": {"sort": "$string"} for i in range(32)}}
    env = Environment(data)
    for index in range(1000):
        atom = Binary("department", Const(f"p{index // 32}"), Const(f"s{index % 32}"))
        text = render_english(atom, env) + "."
        assert parse_english(env, text).formulas == (atom,)


def test_general_definite_attribute_property_and_scoped_source():
    data = deepcopy(environment().to_dict())
    data["vocabulary"]["sorts"]["department_sort"] = {"description": "Department"}
    data["vocabulary"]["predicates"]["department"]["arguments"] = ["person", "department_sort"]
    data["vocabulary"]["predicates"]["active"] = {
        "arguments": ["department_sort"], "description": "Active department"}
    env = Environment(data)
    atom = attribute_property(env, "department", Const("alice"), "active")
    assert atom == Exists("department_sort", And(
        Binary("department", Const("alice"), Var(0)), Unary("active", Var(0))))
    assert parse_english(env, render_english(atom, env) + ".").formulas == (atom,)
    scoped = Forall("person", Exists("department_sort", And(
        Binary("department", Var(1), Var(0)), Unary("active", Var(0)))))
    assert parse_english(env, render_english(scoped, env) + ".").formulas == (scoped,)
