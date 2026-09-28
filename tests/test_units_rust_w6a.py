"""Python/Rust regeneration parity for the admitted W6a ground family."""
import json
from pathlib import Path
import subprocess

import pytest

from ve.ast import formula_from_data
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.units import elaborate_quantity, erased_environment, quantity_meaning_id

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
