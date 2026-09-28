"""W6a admission regression cases: identity, exact grid, dates, and counting."""
from datetime import date, timedelta

import pytest

from ve import ast
from ve.environment import Environment
from ve.errors import UnsupportedProfile, VEError
from ve.surface.count import at_least, exactly, n_of_m
from ve.units import day_number, elaborate_quantity, erased_environment, quantity_meaning_id, render_coordinate


def environment():
    return {
        "language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {
            "sorts": {"item": {"description": "an item"}},
            "predicates": {"reported": {"arguments": ["$int"], "argument_units": {"0": "bp"},
                                        "description": "reported percentage"}},
            "constants": {"rate": {"sort": "$int", "unit": "bp", "description": "reported rate"},
                          "event": {"sort": "item", "description": "event"}},
        },
        "unit_schema": "ve-units@1", "units": {
            "bp": {"scale": "100", "display": {"kind": "percent"}},
            "usd_cent": {"scale": "100", "display": {"kind": "money", "currency": "USD", "input_symbol": "$"}},
            "day": {"scale": "1", "display": {"kind": "iso_date"}},
            "elapsed_day": {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
        },
    }


def quantity(formula, **more):
    return {"format": "ve-quantity@1", "formula": formula, **more}


def test_exact_decimal_and_identity_binds_tags():
    source_environment = environment()
    env = Environment(source_environment)
    original_id = env.environment_id
    source_environment["units"]["bp"]["scale"] = "1000"
    assert env.environment_id == original_id
    with pytest.raises(TypeError):
        env.units["bp"]["display"]["kind"] = "decimal"
    canonical, core = elaborate_quantity(env, quantity(["lt", ["decimal", "bp", "3.75"],
                                                         ["decimal", "bp", "4.00"]]))
    assert canonical["formula"] == ["lt", ["num", "bp", "375"], ["num", "bp", "400"]]
    assert core == ["lt", ["num", "375"], ["num", "400"]]
    target = erased_environment(env)
    assert target.unit_schema is None and target.environment_id != env.environment_id
    assert ast.formula_from_data(target, core) == ast.Lt(ast.Num(375), ast.Num(400))
    assert render_coordinate("bp", 370, env) == "3.70%"
    assert render_coordinate("usd_cent", 375, env) == "USD 3.75"
    assert quantity_meaning_id(env, quantity(["eq", ["decimal", "bp", "3.700"],
                                             ["num", "bp", "370"]])) == quantity_meaning_id(
        env, quantity(["eq", ["decimal", "bp", "3.70"], ["num", "bp", "370"]]))
    assert quantity_meaning_id(env, quantity(["eq", ["num", "bp", "375"],
                                             ["num", "bp", "375"]])) != quantity_meaning_id(
        env, quantity(["eq", ["num", "usd_cent", "375"], ["num", "usd_cent", "375"]]))
    with pytest.raises(VEError, match=r"UnitMismatch\(usd_cent,bp\)"):
        elaborate_quantity(env, quantity(["eq", ["num", "usd_cent", "375"],
                                          ["decimal", "bp", "3.75"]]))
    with pytest.raises(VEError, match="UnitPrecision"):
        elaborate_quantity(env, quantity(["eq", ["decimal", "bp", "3.755"],
                                          ["num", "bp", "375"]]))
    with pytest.raises(VEError, match="Q differs"):
        elaborate_quantity(env, quantity(["eq", ["decimal", "bp", "3.75"],
                                          ["num", "bp", "375"]],
                                         Q=["eq", ["num", "bp", "376"], ["num", "bp", "375"]]))
    implicit, _ = elaborate_quantity(env, quantity(["eq", ["num", "375"], ["num", "375"]]))
    explicit, _ = elaborate_quantity(env, quantity(["eq", ["num", "dimensionless", "375"],
                                                    ["num", "dimensionless", "375"]]))
    assert implicit == explicit
    changed = environment()
    changed["units"]["unused"] = {"scale": "1", "display": {"kind": "decimal", "label": "unused"}}
    assert Environment(changed).environment_id != env.environment_id


def test_declaration_rejections_and_slot_tags():
    for replacement in ({"scale": "3", "display": {"kind": "percent"}},
                        {"scale": "100", "display": {"kind": "decimal", "label": "days"}}):
        raw = environment()
        raw["units"]["bp"] = replacement
        with pytest.raises(VEError):
            Environment(raw)
    raw = environment()
    raw["units"]["other"] = {"scale": "100", "display": {"kind": "percent"}}
    with pytest.raises(VEError, match="DisplayCollision"):
        Environment(raw)
    raw = environment()
    raw["units"]["label"] = {"scale": "100", "display": {"kind": "decimal", "label": "USD",
                                                               "placement": "prefix"}}
    with pytest.raises(VEError, match="DisplayCollision"):
        Environment(raw)
    env = Environment(environment())
    bare = environment()
    bare["vocabulary"] = {"sorts": {}, "predicates": {}, "constants": {}}
    bare["units"] = {}
    empty_extension = Environment(bare)
    no_extension = dict(bare)
    no_extension.pop("unit_schema")
    no_extension.pop("units")
    assert empty_extension.environment_id != Environment(no_extension).environment_id
    with pytest.raises(UnsupportedProfile, match="annotated admission"):
        ast.formula_from_data(env, ["lt", ["num", "375"], ["num", "400"]])
    with pytest.raises(VEError, match="UnitMismatch"):
        elaborate_quantity(env, quantity(["unary", "reported", ["num", "usd_cent", "375"]]))
    with pytest.raises(VEError, match="UnitMismatch"):
        elaborate_quantity(env, quantity(["eq", ["const", "usd_cent", "rate"],
                                          ["num", "usd_cent", "375"]]))
    with pytest.raises(UnsupportedProfile, match="numbers2"):
        elaborate_quantity(env, quantity(["forall_date", ["top"]]))


def test_dates_and_duration_are_distinct():
    env = Environment(environment())
    assert day_number("2026-09-16") == 20712
    assert render_coordinate("day", 20712, env) == "2026-09-16"
    start = date(1970, 1, 1)
    for i in range(0, 2932897, 293):
        d = start + timedelta(days=i)
        assert day_number(d.isoformat()) == i
    for spelling in ("1970-01-01", "2000-02-29", "2000-12-31", "2099-12-31",
                     "2100-03-01", "9999-12-31"):
        assert render_coordinate("day", day_number(spelling), env) == spelling
    _, core = elaborate_quantity(env, quantity(["shift_days", ["date", "2026-09-17"],
                                                ["date", "2026-09-16"], "1"]))
    assert core[-1] == ["eq", ["num", "20713"], ["add", ["num", "20712"], ["num", "1"]]]
    _, core = elaborate_quantity(env, quantity(["elapsed_days", ["date", "2026-09-17"],
                                                ["date", "2026-09-16"],
                                                ["num", "elapsed_day", "-1"]]))
    assert core[-1] == ["eq", ["num", "-1"],
                        ["add", ["num", "20712"], ["scale", "-1", ["num", "20713"]]]]
    with pytest.raises(VEError, match="UnitMismatch"):
        elaborate_quantity(env, quantity(["eq", ["date", "2026-09-16"],
                                          ["num", "elapsed_day", "20712"]]))
    with pytest.raises(VEError, match="DateRange"):
        day_number("1969-12-31")
    with pytest.raises(VEError, match="InvalidDate"):
        day_number("2100-02-29")


def test_trace_declarations_are_identity_bound_before_trace_route_exists():
    raw = environment()
    raw["vocabulary"]["constants"]["other_event"] = {"sort": "item", "description": "other event"}
    env = Environment(raw)
    trace = {"name": "review_window", "tick_tag": "elapsed_day", "origin": "event", "horizon": "10"}
    first = quantity(["top"], traces=[trace])
    second = quantity(["top"], traces=[{**trace, "origin": "other_event"}])
    assert elaborate_quantity(env, first)[1] == elaborate_quantity(env, second)[1]
    assert quantity_meaning_id(env, first) != quantity_meaning_id(env, second)
    with pytest.raises(VEError, match="Duplicate"):
        elaborate_quantity(env, quantity(["top"], traces=[trace, trace]))
    with pytest.raises(VEError, match="origin"):
        elaborate_quantity(env, quantity(["top"], traces=[{**trace, "origin": "missing"}]))
    with pytest.raises(UnsupportedProfile, match="numbers2"):
        elaborate_quantity(env, quantity(["trace_all", "review_window", ["top"]], traces=[trace]))


def test_fine_percent_uses_a_separate_environment_without_conversion():
    coarse = Environment(environment())
    with pytest.raises(VEError, match="UnitPrecision"):
        elaborate_quantity(coarse, quantity(["eq", ["decimal", "bp", "0.0001"],
                                             ["num", "bp", "0"]]))
    raw = environment()
    raw["vocabulary"] = {"sorts": {}, "predicates": {}, "constants": {}}
    raw["units"] = {"fine_percent": {"scale": "1000000", "display": {"kind": "percent"}}}
    fine = Environment(raw)
    canonical, _ = elaborate_quantity(fine, quantity(["eq", ["decimal", "fine_percent", "0.0001"],
                                                     ["num", "fine_percent", "100"]]))
    assert canonical["formula"][1] == ["num", "fine_percent", "100"]
    assert render_coordinate("fine_percent", 100, fine) == "0.000100%"
    assert fine.environment_id != coarse.environment_id


def test_counting_nested_scope_and_bounds():
    raw = environment()
    raw["vocabulary"]["predicates"]["p"] = {"arguments": ["item"], "description": "P"}
    env = Environment(raw)
    body = ast.Unary("p", ast.Var(0))
    expanded = at_least(env, "item", 2, body)
    assert ast._to_data(expanded) == ["exists", "item", ["and", ["unary", "p", ["var", 0]],
        ["exists", "item", ["and", ["not", ["eq", ["var", 0], ["var", 1]]],
                              ["unary", "p", ["var", 0]]]]]]
    with pytest.raises(VEError, match="at least 8"):
        at_least(env, "item", 9, body)
    with pytest.raises(VEError, match="exactly 7"):
        exactly(env, "item", 8, body)
    with pytest.raises(VEError, match="n of m"):
        n_of_m(env, "item", 16, 18, body, body)
    with pytest.raises(UnsupportedProfile, match="numbers2"):
        at_least(env, "$int", 1, body)
