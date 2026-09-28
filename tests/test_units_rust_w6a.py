"""Python/Rust regeneration parity for the admitted W6a ground family."""
import json
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
RUST = ROOT / "rust" / "target" / "release" / "ve"
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
    values = {"decision_date": "20712", "new_target_lower": "375", "new_target_upper": "400",
              "pce_september_estimate": "370", "pce_june_estimate": "360", "target_rate": "200",
              "first_projected_target_year": "2029", "growth_old_projection": "220",
              "growth_new_projection": "230", "unemployment_old_projection": "430",
              "unemployment_new_projection": "410"}
    model_data = {"complete": True, "domains": {}, "constants": values, "relations": {}}
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
