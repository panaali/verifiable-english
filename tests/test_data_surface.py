from copy import deepcopy

import pytest

from tests.test_data_flags import environment
from ve.ast import Binary, Const
from ve.environment import Environment
from ve.errors import TypeMismatch
from ve.surface.data import attribute_equals, member_of


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
