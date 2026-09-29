"""Python/Rust regeneration parity for the admitted W6a ground family."""
import json
import os
from datetime import date, timedelta
from pathlib import Path
import subprocess

import pytest

from ve.ast import formula_from_data
from ve import ast
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.units import elaborate_quantity, erased_environment, quantity_meaning_id
from ve.surface.count import at_least

ROOT = Path(__file__).resolve().parents[1]
RUST = Path(os.environ.get("VE_RUST_BINARY", str(ROOT / "rust" / "target" / "release" / "ve")))
FIXTURE = ROOT / "usecases" / "news-article" / "w6a-quantity-fixtures.json"
pytestmark = pytest.mark.skipif(not RUST.exists(), reason="build Rust release runner first")


def rust(case):
    process = subprocess.run([str(RUST), "conformance", "-"], input=json.dumps(case),
                             text=True, capture_output=True, timeout=30)
    assert process.returncode in (0, 1), process.stderr
    return json.loads(process.stdout)[0]


def test_news_regeneration_ids_and_evaluation_agree():
    fixture = json.loads(FIXTURE.read_text())
    env = Environment(fixture["environment"])
    target = erased_environment(env)
    model_data = fixture["model"]
    model = FiniteModel.from_dict(target, model_data)
    for item in fixture["cases"]:
        payload = {"format": "ve-quantity@1", "formula": item["formula"]}
        canonical, core = elaborate_quantity(env, payload)
        result = rust({"id": item["id"], "kind": "quantity", "environment": fixture["environment"],
                       "quantity": payload, "model": model_data})
        assert result["status"] == "ok", result
        assert result["Q"] == canonical["formula"]
        assert result["core"] == core
        assert result["environment_id"] == env.environment_id
        assert result["target_environment_id"] == target.environment_id
        assert result["meaning_id"] == quantity_meaning_id(env, payload)
        assert result["value"] is True
        assert evaluate(target, formula_from_data(target, core), model, trace=False).value is True


def test_hostile_literal_and_tag_changes_reject_in_both():
    fixture = json.loads(FIXTURE.read_text())
    env = Environment(fixture["environment"])
    cases = [
        (["eq", ["decimal", "bp", "3.755"], ["num", "bp", "375"]], "UnitPrecision"),
        (["eq", ["num", "bp", "375"], ["num", "calendar_year", "375"]], "UnitMismatch"),
        (["eq", ["num", "bp", "0"], ["num", "0"]], "UnitMismatch"),
        (["eq", ["add", "bp", ["num", "bp", "1"], ["num", "calendar_year", "1"]],
          ["num", "bp", "2"]], "UnitMismatch"),
        (["eq", ["date", "1969-12-31"], ["num", "day", "0"]], "DateRange"),
    ]
    for formula, message in cases:
        payload = {"format": "ve-quantity@1", "formula": formula}
        with pytest.raises(Exception, match=message):
            elaborate_quantity(env, payload)
        result = rust({"id": message, "kind": "quantity", "environment": fixture["environment"],
                       "quantity": payload})
        assert result["status"] == "error" and message in result["error"]["message"]
    payload = {"format": "ve-quantity@1", "formula": ["eq", ["decimal", "bp", "3.75"],
                                                        ["num", "bp", "375"]],
               "Q": ["eq", ["num", "bp", "376"], ["num", "bp", "375"]]}
    with pytest.raises(Exception, match="Q differs"):
        elaborate_quantity(env, payload)
    result = rust({"id": "forged-Q", "kind": "quantity", "environment": fixture["environment"],
                   "quantity": payload})
    assert result["status"] == "error" and "Q differs" in result["error"]["message"]


def test_user_sort_counting_expansion_agrees_on_a_finite_model():
    raw = {"language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
           "spec_revision": "ve-v0.2-expand2-2026-09-25",
           "vocabulary": {"sorts": {"item": {"description": "item"}},
                          "predicates": {"p": {"arguments": ["item"], "description": "P"}},
                          "constants": {}}, "unit_schema": "ve-units@1", "units": {}}
    env = Environment(raw)
    expanded = at_least(env, "item", 2, ast.Unary("p", ast.Var(0)))
    payload = {"format": "ve-quantity@1", "formula": ast._to_data(expanded)}
    canonical, core = elaborate_quantity(env, payload)
    target = erased_environment(env)
    model_data = {"complete": True, "domains": {"item": ["e1", "e2"]},
                  "constants": {}, "relations": {"p": [["e1"], ["e2"]]}}
    model = FiniteModel.from_dict(target, model_data)
    result = rust({"id": "two", "kind": "quantity", "environment": raw,
                   "quantity": payload, "model": model_data})
    assert result["status"] == "ok" and result["value"] is True
    assert result["Q"] == canonical["formula"] and result["core"] == core
    assert evaluate(target, formula_from_data(target, core), model, trace=False).value is True


def test_display_collision_rejects_on_both_decoders():
    fixture = json.loads(FIXTURE.read_text())
    raw = fixture["environment"]
    raw["units"]["other_percent"] = {"scale": "100", "display": {"kind": "percent"}}
    with pytest.raises(Exception, match="DisplayCollision"):
        Environment(raw)
    result = rust({"id": "collision", "kind": "quantity", "environment": raw,
                   "quantity": {"format": "ve-quantity@1", "formula": ["top"]}})
    assert result["status"] == "error" and "DisplayCollision" in result["error"]["message"]


def test_integer_predicate_slot_is_checked_before_erasure():
    raw = json.loads(FIXTURE.read_text())["environment"]
    raw["vocabulary"]["predicates"]["reported"] = {
        "arguments": ["$int"], "argument_units": {"0": "bp"}, "description": "reported rate"}
    env = Environment(raw)
    good = {"format": "ve-quantity@1", "formula": ["unary", "reported", ["num", "bp", "375"]]}
    canonical, core = elaborate_quantity(env, good)
    model = {"complete": True, "domains": {},
             "constants": {k: "0" for k in raw["vocabulary"]["constants"]},
             "relations": {"reported": [["375"]]}}
    result = rust({"id": "slot", "kind": "quantity", "environment": raw,
                   "quantity": good, "model": model})
    assert result["status"] == "ok" and result["Q"] == canonical["formula"]
    assert result["core"] == core and result["value"] is True
    bad = {"format": "ve-quantity@1", "formula": ["unary", "reported", ["num", "calendar_year", "375"]]}
    with pytest.raises(Exception, match="UnitMismatch"):
        elaborate_quantity(env, bad)
    rejected = rust({"id": "slot-bad", "kind": "quantity", "environment": raw, "quantity": bad})
    assert rejected["status"] == "error" and "UnitMismatch" in rejected["error"]["message"]


def test_rust_day_numbers_match_datetime_on_10000_dates():
    raw = {"language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
           "spec_revision": "ve-v0.2-expand2-2026-09-25",
           "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}},
           "unit_schema": "ve-units@1", "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}}}}
    epoch = date(1970, 1, 1)
    indices = [i * 2932896 // 9999 for i in range(10000)]
    assert len(set(indices)) == 10000 and indices[0] == 0 and indices[-1] == 2932896
    cases = [{"id": str(i), "kind": "quantity", "environment": raw,
              "quantity": {"format": "ve-quantity@1", "formula": ["eq", ["date", (epoch + timedelta(days=i)).isoformat()],
                                                                 ["num", "day", str(i)]]}}
             for i in indices]
    process = subprocess.run([str(RUST), "conformance", "-"], input=json.dumps(cases),
                             text=True, capture_output=True, timeout=120)
    assert process.returncode == 0, process.stderr[:500]
    results = json.loads(process.stdout)
    assert len(results) == 10000
    assert all(result["status"] == "ok" and result["Q"][1] == ["num", "day", result["id"]]
               for result in results)


# --- Review regressions: Rust decides every class exactly as Python ---------

from tests.test_w6a_review_regressions import (COLLIDING_UNITS, IDENTITY_VARIANTS, money,
                                               raw_environment)
from ve.errors import VEError


def _rust_quantity(raw, formula=("top",), **more):
    return rust({"id": "review", "kind": "quantity", "environment": raw,
                 "quantity": {"format": "ve-quantity@1", "formula": list(formula), **more}})


def test_rust_rejects_every_display_collision_class():
    for units in COLLIDING_UNITS:
        result = _rust_quantity(raw_environment(units))
        assert result["status"] == "error", units
        assert "DisplayCollision" in result["error"]["message"], (units, result)


def test_rust_rejects_non_normalized_display_strings():
    for text in ["", " $", "$  ", "U\tS", "US $", "a  b", "US $", "US\x1c$"]:
        with pytest.raises(VEError):
            Environment(raw_environment({"usd": money("USD", text)}))
        assert _rust_quantity(raw_environment({"usd": money("USD", text)}))["status"] == "error", text
    assert _rust_quantity(raw_environment({"usd": money("USD", "US$ ")}))["status"] == "ok"


def test_rust_rejects_the_undeclared_date_tag_like_python():
    for formula in (["date_on", ["date", "2026-09-16"], ["date", "2026-09-16"]],
                    ["eq", ["date", "2026-09-16"], ["date", "2026-09-16"]]):
        with pytest.raises(VEError, match=r"UnknownUnit\(day\)"):
            elaborate_quantity(Environment(raw_environment({})),
                               {"format": "ve-quantity@1", "formula": formula})
        result = _rust_quantity(raw_environment({}), formula)
        assert result["status"] == "error" and "UnknownUnit(day)" in result["error"]["message"]


def test_rust_and_python_identities_agree_on_every_spelling():
    for variant in IDENTITY_VARIANTS:
        raw = raw_environment(variant.get("units"), variant.get("constants"),
                              predicates=variant.get("predicates"))
        env = Environment(raw)
        payload = {"format": "ve-quantity@1", "formula": ["top"]}
        result = _rust_quantity(raw)
        assert result["status"] == "ok", result
        assert result["environment_id"] == env.environment_id
        assert result["meaning_id"] == quantity_meaning_id(env, payload)
        assert result["target_environment_id"] == erased_environment(env).environment_id


def test_rust_gates_traces_sorts_profiles_and_literals_like_python():
    trace = {"name": "w", "tick_tag": "dimensionless", "origin": "e", "horizon": "1"}
    raw = raw_environment(sorts={"item": {"description": "i"}},
                          constants={"e": {"sort": "item", "description": "e"}})
    with pytest.raises(VEError, match="numbers2"):
        elaborate_quantity(Environment(raw), {"format": "ve-quantity@1", "formula": ["top"],
                                              "traces": [trace]})
    assert "numbers2" in _rust_quantity(raw, traces=[trace])["error"]["message"]
    rejected = []
    for sort in ("bp", "dimensionless"):
        rejected.append(raw_environment(sorts={sort: {"description": "s"}}))
    for profiles in (["data@0", "order@0", "relational-fol@0", "time@0"],
                     ["definitions@0", "order@0", "relational-fol@0", "time@0"]):
        changed = raw_environment()
        changed["profiles"] = profiles
        rejected.append(changed)
    rejected.append(raw_environment(constants={"s": {"sort": "$string"}}))
    rejected.append(raw_environment(constants={"c": {"sort": "$int", "description": "c",
                                                     "verbalisation": 3}}))
    for raw in rejected:
        with pytest.raises(VEError):
            Environment(raw)
        assert _rust_quantity(raw)["status"] == "error", raw
    documents = raw_environment()
    documents["profiles"] = ["documents@1", "order@0", "relational-fol@0", "time@0"]
    assert _rust_quantity(documents)["status"] == "ok"
    assert Environment(documents).environment_id == _rust_quantity(documents)["environment_id"]


def test_rust_orders_invalid_date_before_date_range_like_python():
    raw = raw_environment({"day": {"scale": "1", "display": {"kind": "iso_date"}}})
    env = Environment(raw)
    for spelling, message in (("1969-13-45", "InvalidDate"), ("0000-01-01", "InvalidDate"),
                              ("1969-12-31", "DateRange"), ("2100-02-29", "InvalidDate"),
                              ("2000-02-29", None)):
        formula = ["date_on", ["date", spelling], ["date", spelling]]
        result = _rust_quantity(raw, formula)
        if message is None:
            elaborate_quantity(env, {"format": "ve-quantity@1", "formula": formula})
            assert result["status"] == "ok"
            continue
        with pytest.raises(VEError, match=message):
            elaborate_quantity(env, {"format": "ve-quantity@1", "formula": formula})
        assert message in result["error"]["message"], result


def test_rust_budgets_formula_and_term_depth_separately_like_python():
    raw = raw_environment()
    env = Environment(raw)
    term = ["num", "bp", "1"]
    for _ in range(60):
        term = ["add", "bp", term, ["num", "bp", "1"]]
    formula = ["eq", term, term]
    for _ in range(60):
        formula = ["not", formula]
    payload = {"format": "ve-quantity@1", "formula": formula}
    canonical, _ = elaborate_quantity(env, payload)
    result = _rust_quantity(raw, formula)
    assert result["status"] == "ok" and result["Q"] == canonical["formula"]
    deep = ["not", ["top"]]
    for _ in range(64):
        deep = ["not", deep]
    with pytest.raises(VEError, match="depth"):
        elaborate_quantity(env, {"format": "ve-quantity@1", "formula": deep})
    assert "depth" in _rust_quantity(raw, deep)["error"]["message"]
