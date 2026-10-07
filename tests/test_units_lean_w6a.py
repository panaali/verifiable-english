"""W6a conformance: Lean `ve_quantity` admission, and Python's relay of it.

Lean owns admission, typing, erasure, identities and certificate binding; Python
relays Lean's answers and generates certificates (Lean-first batch 9, which
deleted Rust's quantity route and Python's elaborator).
"""
import copy
from datetime import date, timedelta
import json
from pathlib import Path
import subprocess

import pytest

from tests import lean_routes

from tests.subprocesses import HANG_TIMEOUT
from tests.test_w6a_review_regressions import (COLLIDING_UNITS, IDENTITY_VARIANTS, label, money,
                                               raw_environment)
from ve import ast
from ve.environment import Environment
from ve.errors import VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.surface.count import at_least, at_most, exactly, n_of_m
from ve.units import (check_quantity_certificate, day_number, decimal_exact, elaborate_quantity,
                      erased_environment, iso_date, prove_quantity, quantity_countermodel,
                      quantity_meaning_id, render_coordinate)

ROOT = Path(__file__).resolve().parents[1]
LEAN = "ve_quantity"  # its service mode, through tests/lean_routes.py
FIXTURE = ROOT / "usecases" / "news-article" / "w6a-quantity-fixtures.json"
pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="build the Lean ve_quantity runner first")


def lean(cases):
    process = lean_routes.completed(LEAN, cases)
    assert process.returncode in (0, 1), process.stderr[:500]
    results = json.loads(process.stdout)
    assert len(results) == len(cases)
    return results


def quantity(formula, **more):
    return {"format": "ve-quantity@1", "formula": formula, **more}


def news():
    return json.loads(FIXTURE.read_text())


def news_model(raw):
    """The fixture's non-vacuity model."""
    return copy.deepcopy(news()["model"])


# --- Admission, regeneration and identities --------------------------------

def test_news_admission_agrees_with_the_relay():
    fixture = news()
    raw = fixture["environment"]
    env = Environment(raw)
    target = erased_environment(env)
    model_data = news_model(raw)
    model = FiniteModel.from_dict(target, model_data)
    cases = [{"id": item["id"], "environment": raw, "quantity": quantity(item["formula"]),
              "model": model_data} for item in fixture["cases"]]
    lean_results = lean(cases)
    for item, got in zip(fixture["cases"], lean_results, strict=True):
        canonical, core = elaborate_quantity(env, quantity(item["formula"]))
        assert got["status"] == "ok", got
        assert got["assurance"] == "lean-admitted"
        assert got["Q"] == canonical["formula"]
        assert got["core"] == core
        assert got["environment_id"] == env.environment_id
        assert got["target_environment_id"] == target.environment_id
        assert got["meaning_id"] == quantity_meaning_id(env, quantity(item["formula"]))
        value = evaluate(target, ast.formula_from_data(target, core), model, trace=False).value
        assert got["value"] is value is True


HOSTILE = [
    (["eq", ["decimal", "bp", "3.755"], ["num", "bp", "375"]], "UnitPrecision(bp, scale=100)"),
    (["eq", ["num", "bp", "375"], ["num", "calendar_year", "375"]], "UnitMismatch(bp,calendar_year)"),
    (["eq", ["num", "bp", "0"], ["num", "0"]], "UnitMismatch(bp,dimensionless)"),
    (["eq", ["add", "bp", ["num", "bp", "1"], ["num", "calendar_year", "1"]], ["num", "bp", "2"]],
     "UnitMismatch(bp,calendar_year)"),
    (["eq", ["const", "calendar_year", "new_target_lower"], ["num", "calendar_year", "1"]],
     "UnitMismatch(calendar_year,bp)"),
    (["eq", ["const", "new_target_lower"], ["num", "375"]], "UnitMismatch(dimensionless,bp)"),
    (["eq", ["date", "1969-12-31"], ["num", "day", "0"]], "DateRange"),
    (["eq", ["date", "2100-02-29"], ["num", "day", "0"]], "InvalidDate"),
    (["eq", ["date", "09/10/2026"], ["num", "day", "0"]], "InvalidDate"),
    (["date_on", ["const", "day", "decision_date"], ["num", "bp", "375"]], "UnitMismatch(bp,day)"),
    (["date_on", ["add", "day", ["date", "2026-09-16"], ["num", "day", "1"]], ["date", "2026-09-16"]],
     "Calendar dates cannot be added"),
    (["eq", ["scale", "day", "2", ["date", "2026-09-16"]], ["num", "day", "1"]],
     "Calendar dates cannot be scaled"),
    (["lt", ["num", "undeclared", "1"], ["num", "undeclared", "2"]], "UnknownUnit(undeclared)"),
    (["shift_days", ["date", "2026-09-17"], ["date", "2026-09-16"], "-1"], "nonnegative"),
    (["within_days", ["date", "2026-09-17"], ["date", "2026-09-16"]], "Invalid within_days node"),
    (["sunday", ["date", "2026-09-20"]], "numbers2"),
    (["forall", "$int", ["top"]], "numbers2"),
    (["forall", "$int", "bp", ["top"]], "numbers2"),
    (["exists_date", ["top"]], "numbers2"),
    (["trace_some", "w", ["top"]], "numbers2"),
    (["atom", "p", []], "n-ary"),
    (["eq", ["var", "bp", 0], ["num", "bp", "0"]], "numbers2"),
    (["eq", ["decimal", "bp", "1" * 41], ["num", "bp", "0"]], "40 digits"),
    (["eq", ["decimal", "bp", "-1." + "0" * 40], ["num", "bp", "0"]], "40 digits"),
]


@pytest.mark.parametrize("formula,message", HOSTILE)
def test_hostile_statements_reject_in_lean_and_the_relay(formula, message):
    raw = news()["environment"]
    with pytest.raises(VEError, match=message.replace("(", r"\(").replace(")", r"\)")):
        elaborate_quantity(Environment(raw), quantity(formula))
    [got] = lean([{"id": "h", "environment": raw, "quantity": quantity(formula)}])
    assert got["status"] == "error" and message in got["error"], got


def test_claimed_q_is_regenerated_not_trusted():
    raw = news()["environment"]
    forged = quantity(["eq", ["decimal", "bp", "3.75"], ["num", "bp", "375"]],
                      Q=["eq", ["num", "bp", "376"], ["num", "bp", "375"]])
    honest = quantity(forged["formula"], Q=["eq", ["num", "bp", "375"], ["num", "bp", "375"]])
    bad_index = quantity(["top"], Q=["top", False])
    results = lean([{"id": "f", "environment": raw, "quantity": forged},
                    {"id": "h", "environment": raw, "quantity": honest},
                    {"id": "b", "environment": raw, "quantity": bad_index}])
    assert results[0]["status"] == "error" and "Q differs" in results[0]["error"]
    assert results[1]["status"] == "ok"
    assert results[2]["status"] == "error" and "Q differs" in results[2]["error"]


def test_same_erased_ast_under_two_tags_has_two_meanings():
    raw = raw_environment({"bp": {"scale": "100", "display": {"kind": "percent"}},
                           "usd_cent": money("USD", "$")})
    env = Environment(raw)
    cases = [{"id": tag, "environment": raw,
              "quantity": quantity(["lt", ["num", tag, "375"], ["num", tag, "400"]])}
             for tag in ("bp", "usd_cent")]
    first, second = lean(cases)
    assert first["core"] == second["core"]
    assert first["core_meaning_id"] == second["core_meaning_id"]
    assert first["meaning_id"] != second["meaning_id"]
    for got, case in zip((first, second), cases):
        assert got["meaning_id"] == quantity_meaning_id(env, case["quantity"])


# --- Environment admission: every review class in Lean too -----------------

def test_lean_rejects_every_display_collision_class():
    cases = [{"id": str(i), "environment": raw_environment(units), "quantity": quantity(["top"])}
             for i, units in enumerate(COLLIDING_UNITS)]
    for got in lean(cases):
        assert got["status"] == "error" and "DisplayCollision" in got["error"], got


def test_lean_display_strings_follow_python_whitespace_rule():
    texts = ["", " $", "$  ", "U\tS", "US $", "a  b", "US $", "US\x1c$"]
    cases = [{"id": repr(t), "environment": raw_environment({"usd": money("USD", t)}),
              "quantity": quantity(["top"])} for t in texts]
    cases += [{"id": "trailing", "environment": raw_environment({"usd": money("USD", "US$ ")}),
               "quantity": quantity(["top"])},
              {"id": "label", "environment": raw_environment({"n": label("items ")}),
               "quantity": quantity(["top"])}]
    results = lean(cases)
    assert all(r["status"] == "error" for r in results[:len(texts)]), results
    assert results[-2]["status"] == "ok" and results[-1]["status"] == "error"


def test_lean_identity_is_the_submitted_declaration():
    cases = []
    for variant in IDENTITY_VARIANTS:
        raw = raw_environment(variant.get("units"), variant.get("constants"),
                              predicates=variant.get("predicates"))
        cases.append({"id": "v", "environment": raw, "quantity": quantity(["top"])})
    for case, got in zip(cases, lean(cases)):
        env = Environment(copy.deepcopy(case["environment"]))
        assert got["status"] == "ok", got
        assert got["environment_id"] == env.environment_id
        assert got["target_environment_id"] == erased_environment(env).environment_id
        assert got["meaning_id"] == quantity_meaning_id(env, case["quantity"])


def test_lean_gates_unsupported_combinations_like_python():
    trace = {"name": "w", "tick_tag": "dimensionless", "origin": "e", "horizon": "1"}
    with_event = raw_environment(sorts={"item": {"description": "i"}},
                                 constants={"e": {"sort": "item", "description": "e"}})
    rejected = [(raw_environment(sorts={"bp": {"description": "s"}}), quantity(["top"]), "collides"),
                (raw_environment(sorts={"dimensionless": {"description": "s"}}), quantity(["top"]),
                 "collides"),
                (raw_environment(constants={"s": {"sort": "$string"}}), quantity(["top"]), "$string"),
                (raw_environment(constants={"c": {"sort": "$int", "description": "c",
                                                  "verbalisation": ""}}), quantity(["top"]),
                 "Verbalisation"),
                (raw_environment({}), quantity(["date_on", ["date", "2026-09-16"],
                                                ["date", "2026-09-16"]]), "UnknownUnit(day)"),
                (with_event, quantity(["top"], traces=[trace]), "numbers2")]
    for profiles in (["data@0", "order@0", "relational-fol@0", "time@0"],
                     ["definitions@0", "order@0", "relational-fol@0", "time@0"],
                     ["order@0", "relational-fol@0"]):
        raw = raw_environment()
        raw["profiles"] = profiles
        rejected.append((raw, quantity(["top"]), "UnsupportedProfile"))
    results = lean([{"id": str(i), "environment": raw, "quantity": q}
                    for i, (raw, q, _) in enumerate(rejected)])
    for (raw, q, message), got in zip(rejected, results):
        with pytest.raises(VEError):
            elaborate_quantity(Environment(raw), q)
        assert got["status"] == "error" and message in got["error"], (message, got)


def test_lean_budgets_formula_and_term_depth_like_python():
    raw = raw_environment()
    env = Environment(raw)
    term = ["num", "bp", "1"]
    for _ in range(60):
        term = ["add", "bp", term, ["num", "bp", "1"]]
    formula = ["eq", term, term]
    for _ in range(60):
        formula = ["not", formula]
    deep = ["not", ["top"]]
    for _ in range(64):
        deep = ["not", deep]
    canonical, core = elaborate_quantity(env, quantity(formula))
    ok, rejected = lean([{"id": "ok", "environment": raw, "quantity": quantity(formula)},
                         {"id": "deep", "environment": raw, "quantity": quantity(deep)}])
    assert ok["status"] == "ok" and ok["Q"] == canonical["formula"] and ok["core"] == core
    assert rejected["status"] == "error" and "depth" in rejected["error"]


# --- Exact conversions ------------------------------------------------------

def test_lean_day_numbers_match_datetime_on_10000_dates():
    epoch = date(1970, 1, 1)
    indices = sorted({i * 2932896 // 9999 for i in range(10000)} |
                     {day_number(s) for s in ("2000-02-28", "2000-02-29", "2000-03-01",
                                              "2100-02-28", "2100-03-01", "1999-12-31",
                                              "2000-01-01", "9999-12-31")})
    assert indices[0] == 0 and indices[-1] == 2932896 and len(indices) >= 10000
    dates = [(epoch + timedelta(days=i)).isoformat() for i in indices]
    forward = lean([{"id": str(i), "kind": "day", "date": d} for i, d in zip(indices, dates)])
    backward = lean([{"id": str(i), "kind": "civil", "day": i} for i in indices])
    for i, d, f, b in zip(indices, dates, forward, backward):
        assert f["day"] == i == day_number(d)
        assert b["date"] == d == iso_date(i)
    rejected = lean([{"id": s, "kind": "day", "date": s} for s in
                     ("1969-12-31", "2100-02-29", "2026-13-01", "0000-01-01", "2026-9-16")] +
                    [{"id": "past", "kind": "civil", "day": 2932897}])
    assert [r["error"].split("(")[0] for r in rejected] == \
        ["DateRange", "InvalidDate", "InvalidDate", "InvalidDate", "InvalidDate", "DateRange"]


def deterministic_decimals():
    seeds = ["0", "-0", "1", "-1", "3.75", "3.7", "3.700", "3.755", "-0.25", "0.0001", "12.30",
             "9" * 38, "-" + "9" * 38, "1." + "0" * 38, "0." + "0" * 37 + "1", "1" * 40]
    value = 7
    for _ in range(300):
        value = (value * 1103515245 + 12345) % (2 ** 31)
        whole = str(value % 100000)
        frac = str(value // 7 % 10000).zfill(value % 5) if value % 5 else ""
        text = ("-" if value % 3 == 0 else "") + whole + ("." + frac if frac else "")
        seeds.append(text)
    return seeds


def test_decimal_lowering_and_rendering_agree_three_ways():
    raw = raw_environment({"bp": {"scale": "100", "display": {"kind": "percent"}},
                           "fine": label("fine", "prefix") | {"scale": "10000"},
                           "whole": label("items")})
    raw["units"]["fine"]["scale"] = "10000"
    env = Environment(raw)
    places = {"bp": 2, "fine": 4, "whole": 0}
    lean_cases, expected = [], []
    for text in deterministic_decimals():
        for tag, k in places.items():
            try:
                coordinate = decimal_exact(text, tag, env)
            except VEError as exc:
                coordinate = type(exc).__name__
            lean_cases.append({"id": f"{tag}:{text}", "kind": "lower", "decimal": text, "places": k})
            expected.append(coordinate)
    results = lean(lean_cases)
    for case, got, want in zip(lean_cases, results, expected):
        if isinstance(want, int):
            assert got["status"] == "ok" and got["coordinate"] == str(want), (case, got)
        else:
            assert got["status"] == "error", (case, got)
    renders = [(tag, want) for case, want in zip(lean_cases, expected) if isinstance(want, int)
               for tag in [case["id"].split(":")[0]]]
    rendered = lean([{"id": str(i), "kind": "render", "coordinate": str(q), "places": places[tag]}
                     for i, (tag, q) in enumerate(renders)])
    for (tag, q), got in zip(renders, rendered):
        display = render_coordinate(tag, q, env)
        amount = display.removesuffix("%").removeprefix("fine ").removesuffix(" items")
        assert got["amount"] == amount


# --- Counting expansion ------------------------------------------------------

def counting_env():
    return raw_environment({}, sorts={"item": {"description": "item"}}, predicates={
        "p": {"arguments": ["item"], "description": "P"},
        "s": {"arguments": ["item"], "description": "S"},
        "r": {"arguments": ["item", "item"], "description": "R"}})


def test_counting_expansion_is_canonical_in_lean():
    raw = counting_env()
    env = Environment(raw)
    bodies = [ast.Unary("p", ast.Var(0)),
              ast.Exists("item", ast.Binary("r", ast.Var(1), ast.Var(0))),
              ast.And(ast.Unary("s", ast.Var(0)), ast.Forall("item", ast.Binary("r", ast.Var(0), ast.Var(1))))]
    cases, expected = [], []
    for body in bodies:
        data = ast._to_data(body)
        for n in range(0, 9):
            cases.append({"mode": "at_least", "n": n, "body": data})
            expected.append(at_least(env, "item", n, body))
        for n in range(0, 8):
            cases.append({"mode": "exactly", "n": n, "body": data})
            expected.append(exactly(env, "item", n, body))
            cases.append({"mode": "at_most", "n": n, "body": data})
            expected.append(at_most(env, "item", n, body))
    for n, m in ((2, 1), (0, 0), (6, 7), (7, 7)):
        cases.append({"mode": "n_of_m", "n": n, "m": m, "selected": ast._to_data(bodies[0]),
                      "property": ast._to_data(bodies[2])})
        expected.append(n_of_m(env, "item", n, m, bodies[0], bodies[2]))
    results = lean([{"id": str(i), "kind": "count", "environment": raw, "sort": "item", **case}
                    for i, case in enumerate(cases)])
    for case, got, want in zip(cases, results, expected):
        assert got["status"] == "ok", (case, got)
        assert got["expansion"] == ast._to_data(want), case
    bounds = [({"mode": "at_least", "n": 9}, "at least 8"), ({"mode": "exactly", "n": 8}, "exactly 7"),
              ({"mode": "at_most", "n": 8}, "at most 7"),
              ({"mode": "n_of_m", "n": 16, "m": 18}, "n of m"), ({"mode": "n_of_m", "n": 1, "m": 8}, "n of m")]
    body = ast._to_data(bodies[0])
    rejected = lean([{"id": "b", "kind": "count", "environment": raw, "sort": "item", "body": body,
                      "selected": body, "property": body, **case} for case, _ in bounds])
    for (_, message), got in zip(bounds, rejected):
        assert got["status"] == "error" and message in got["error"]
    [int_sort] = lean([{"id": "i", "kind": "count", "environment": raw, "sort": "$int", "mode": "at_least",
                        "n": 1, "body": body}])
    assert "numbers2" in int_sort["error"]


# --- Certified consequences and the outer binding ----------------------------

def certified(env, raw, premises, conclusion):
    certificate = prove_quantity(env, premises, conclusion)
    assert certificate is not None
    assert check_quantity_certificate(env, premises, conclusion, certificate)
    return certificate


def lean_certificate(raw, premises, conclusion, certificate, case_id="c"):
    [got] = lean([{"id": case_id, "kind": "certificate", "environment": raw, "premises": premises,
                   "conclusion": conclusion, "certificate": certificate}])
    return got


NEWS_CONSEQUENCES = [
    ("N07", ["new_target_lower", "3.75"], ["new_target_upper", "4.00"],
     ["lt", ["const", "bp", "new_target_lower"], ["const", "bp", "new_target_upper"]]),
    ("N21", ["pce_june_estimate", "3.60"], ["pce_september_estimate", "3.70"],
     ["eq", ["add", "bp", ["const", "bp", "pce_september_estimate"],
             ["scale", "bp", "-1", ["const", "bp", "pce_june_estimate"]]], ["num", "bp", "10"]]),
    ("N21-order", ["pce_june_estimate", "3.60"], ["pce_september_estimate", "3.70"],
     ["lt", ["const", "bp", "pce_june_estimate"], ["const", "bp", "pce_september_estimate"]]),
    ("N23-growth", ["growth_old_projection", "2.20"], ["growth_new_projection", "2.30"],
     ["eq", ["add", "bp", ["const", "bp", "growth_new_projection"],
             ["scale", "bp", "-1", ["const", "bp", "growth_old_projection"]]], ["num", "bp", "10"]]),
    ("N23-unemployment", ["unemployment_old_projection", "4.30"], ["unemployment_new_projection", "4.10"],
     ["eq", ["add", "bp", ["const", "bp", "unemployment_old_projection"],
             ["scale", "bp", "-1", ["const", "bp", "unemployment_new_projection"]]], ["num", "bp", "20"]]),
]


@pytest.mark.parametrize("name,first,second,claim", NEWS_CONSEQUENCES)
def test_news_consequences_are_certified_by_lean(name, first, second, claim):
    raw = news()["environment"]
    env = Environment(raw)
    premises = [quantity(["eq", ["const", "bp", c], ["decimal", "bp", v]]) for c, v in (first, second)]
    conclusion = quantity(claim)
    certificate = certified(env, raw, premises, conclusion)
    got = lean_certificate(raw, premises, conclusion, certificate, name)
    assert got["status"] == "ok" and got["valid"] is True, got
    assert got["premise_meaning_ids"] == certificate["premise_meaning_ids"]
    assert got["conclusion_meaning_id"] == certificate["conclusion_meaning_id"]


def test_relabelled_or_raw_evidence_never_certifies():
    raw = raw_environment({"bp": {"scale": "100", "display": {"kind": "percent"}},
                           "usd_cent": money("USD", "$")},
                          {"low": {"sort": "$int", "unit": "bp", "description": "low"},
                           "high": {"sort": "$int", "unit": "bp", "description": "high"},
                           "cost": {"sort": "$int", "unit": "usd_cent", "description": "cost"},
                           "price": {"sort": "$int", "unit": "usd_cent", "description": "price"}})
    env = Environment(raw)
    premises = [quantity(["eq", ["const", "bp", "low"], ["decimal", "bp", "3.75"]]),
                quantity(["eq", ["const", "bp", "high"], ["decimal", "bp", "4.00"]])]
    conclusion = quantity(["lt", ["num", "bp", "375"], ["const", "bp", "high"]])
    certificate = certified(env, raw, premises, conclusion)
    assert lean_certificate(raw, premises, conclusion, certificate)["valid"] is True
    # Percent to money: the same integer proof, different annotated statements.
    money_premises = [quantity(["eq", ["const", "usd_cent", "cost"], ["decimal", "usd_cent", "3.75"]]),
                      quantity(["eq", ["const", "usd_cent", "price"], ["decimal", "usd_cent", "4.00"]])]
    money_conclusion = quantity(["lt", ["num", "usd_cent", "375"], ["const", "usd_cent", "price"]])
    relabelled = lean_certificate(raw, money_premises, money_conclusion, certificate)
    assert relabelled["status"] == "error" and "stale" in relabelled["error"]
    with pytest.raises(VEError, match="stale"):
        check_quantity_certificate(env, money_premises, money_conclusion, certificate)
    # The unwrapped order certificate is not W6 evidence.
    raw_core = lean_certificate(raw, premises, conclusion, certificate["core"])
    assert raw_core["status"] == "error" and raw_core["valid"] is False
    # Any mutated binding or trace fails.
    for key, value in (("environment_id", "0" * 64), ("conclusion_meaning_id", "0" * 64),
                       ("premise_meaning_ids", certificate["premise_meaning_ids"][::-1])):
        mutated = {**certificate, key: value}
        assert lean_certificate(raw, premises, conclusion, mutated)["valid"] is False
    inner = {**certificate, "core": {**certificate["core"], "environment_id": "0" * 64}}
    assert lean_certificate(raw, premises, conclusion, inner)["valid"] is False
    closed = {**certificate, "core": {**certificate["core"], "trace": {"rule": "close"}}}
    got = lean_certificate(raw, premises, conclusion, closed)
    assert got["status"] == "ok" and got["valid"] is False


def test_countermodels_agree_with_the_relay():
    raw = news()["environment"]
    env = Environment(raw)
    premises = [quantity(["eq", ["const", "bp", "new_target_lower"], ["decimal", "bp", "3.75"]])]
    for claim, lower, refutes in ((["lt", ["const", "bp", "new_target_lower"], ["decimal", "bp", "3.70"]], "375", True),
                                  (["le", ["decimal", "bp", "3.75"], ["const", "bp", "new_target_lower"]], "375", False)):
        model = news_model(raw)
        model["constants"]["new_target_lower"] = lower
        conclusion = quantity(claim)
        assert quantity_countermodel(env, premises, conclusion, model) is refutes
        [got] = lean([{"id": "m", "kind": "countermodel", "environment": raw, "premises": premises,
                       "conclusion": conclusion, "model": model}])
        assert got["refutes"] is refutes
        assert got["premise_meaning_ids"] == [quantity_meaning_id(env, p) for p in premises]
        assert got["conclusion_meaning_id"] == quantity_meaning_id(env, conclusion)
        assert got["environment_id"] == env.environment_id


def test_generic_route_still_rejects_extended_environments():
    """Raw erased evidence cannot pass the order route by dropping tags."""
    conformance = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_conformance"
    raw = news()["environment"]
    process = subprocess.run([str(conformance), "route", "-"], text=True, capture_output=True,
                             input=json.dumps([{"id": "bypass", "kind": "evaluate", "environment": raw,
                                                "ast": [["lt", ["num", "375"], ["num", "400"]]]}]),
                             timeout=HANG_TIMEOUT)
    [result] = json.loads(process.stdout)
    assert result["status"] == "error" and "unit_schema" in result["error"]
