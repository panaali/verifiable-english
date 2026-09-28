"""Authored age reading and negative controls; no source-fidelity claim."""
import pytest

from ve.ast import formula_from_data
from ve.environment import Environment
from ve.errors import VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.surface.count import at_least
from ve.units import elaborate_quantity, erased_environment, render_coordinate
from ve import ast


def test_authored_completed_years_boundary_only():
    env = Environment({"language": "ve.core@0.2",
        "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {}, "predicates": {},
                       "constants": {"user_age": {"sort": "$int", "unit": "age_year",
                                                  "description": "authored completed-years reading of the user's age"}}},
        "unit_schema": "ve-units@1",
        "units": {"age_year": {"scale": "1", "display": {"kind": "decimal",
                    "label": "completed years of age"}}}})
    payload = {"format": "ve-quantity@1",
               "formula": ["lt", ["num", "age_year", "18"], ["const", "age_year", "user_age"]]}
    _, core = elaborate_quantity(env, payload)
    target = erased_environment(env)
    formula = formula_from_data(target, core)
    def at(age):
        model = FiniteModel.from_dict(target, {"complete": True, "domains": {},
                                               "constants": {"user_age": str(age)}, "relations": {}})
        return evaluate(target, formula, model, trace=False).value
    assert at(18) is False and at(19) is True
    assert render_coordinate("age_year", 18, env) == "18 completed years of age"


def test_thousand_distinct_users_exceeds_bounded_sugar():
    env = Environment({"language": "ve.core@0.2", "profiles": ["relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"user": {"description": "user"}},
                       "predicates": {"sent": {"arguments": ["user"], "description": "sent"}},
                       "constants": {}}})
    with pytest.raises(VEError, match="CountingBound"):
        at_least(env, "user", 1000, ast.Unary("sent", ast.Var(0)))
