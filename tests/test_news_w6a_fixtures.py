"""Pinned news numeric inputs: source-scoped cases, certified consequences, residuals.

Every case must have tagged admission, a controlled wording that round-trips,
a regenerated core, and a jointly satisfying model; every claimed consequence
must carry Lean-checked evidence over the cases it cites (units-schema §7).
"""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from ve import ast
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.surface.time import parse_quantity_sentence, render_quantity_sentence
from ve.units import (check_quantity_certificate, elaborate_quantity, erased_environment,
                      prove_quantity, render_coordinate)

ROOT = Path(__file__).resolve().parents[1]
NEWS = ROOT / "usecases" / "news-article"
LEAN = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_quantity"


def fixture():
    return json.loads((NEWS / "w6a-quantity-fixtures.json").read_text())


def quantity(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def test_news_quantity_fixtures():
    data = fixture()
    assert sha256((NEWS / "source.md").read_bytes()).hexdigest() == data["source_sha256"]
    env = Environment(data["environment"])
    coordinates = {}
    for case in data["cases"]:
        canonical, core = elaborate_quantity(env, quantity(case["formula"]))
        assert canonical["formula"] and core
        coordinates[case["id"]] = core
    assert coordinates["N07-lower"] == ["eq", ["const", "new_target_lower"], ["num", "375"]]
    assert coordinates["N07-upper"] == ["eq", ["const", "new_target_upper"], ["num", "400"]]
    assert [coordinates[x][-1] for x in ("N13-lower", "N13-upper", "N13-reach-year",
                                            "N13-remain-year")] == [
        ["num", "400"], ["num", "425"], ["num", "2026"], ["num", "2027"]]
    assert coordinates["N15-goal"][-1] == coordinates["N24-goal"][-1] == ["num", "200"]
    assert coordinates["N21-september"][-1] == ["num", "370"]
    assert coordinates["N21-june"][-1] == ["num", "360"]
    assert coordinates["N22-year"][-1] == ["num", "2029"]
    assert [coordinates[x][-1] for x in ("N23-growth-old", "N23-growth-new",
                                            "N23-unemployment-old", "N23-unemployment-new")] == [
                                                ["num", "220"], ["num", "230"],
                                                ["num", "430"], ["num", "410"]]
    assert render_coordinate("bp", 375, env) == "3.75%"
    assert render_coordinate("calendar_year", 2029, env) == "calendar year 2029"
    assert {r["id"]: r["status"] for r in data["residuals"]} == {
        "N07b": "NO", "N08": "REIFIED", "N13-projection": "OPEN", "N15-timelier": "OPEN",
        "N22b": "NO", "N23-slightly": "OPEN", "N24-clearly-speed": "OPEN"}
    # Spec §7.1 rows with a numeric payload all have cases; N07b/N22b stay NO.
    assert {c["row"] for c in data["cases"]} == {"1", "7", "13", "15", "21", "22", "23", "24"}


def test_every_case_and_consequence_wording_round_trips():
    data = fixture()
    env = Environment(data["environment"])
    for item in data["cases"] + data["consequences"]:
        canonical, _ = elaborate_quantity(env, quantity(item["formula"]))
        assert parse_quantity_sentence(env, item["wording"]) == canonical, item["id"]
        assert render_quantity_sentence(env, canonical) == item["wording"], item["id"]


def test_model_satisfies_every_case_and_consequence():
    data = fixture()
    env = Environment(data["environment"])
    target = erased_environment(env)
    model = FiniteModel.from_dict(target, data["model"])
    for item in data["cases"] + data["consequences"]:
        _, core = elaborate_quantity(env, quantity(item["formula"]))
        assert evaluate(target, ast.formula_from_data(target, core), model, trace=False).value is True


def test_consequences_are_certified_from_cited_cases():
    data = fixture()
    env = Environment(data["environment"])
    cases = {c["id"]: c for c in data["cases"]}
    lean_cases = []
    for item in data["consequences"]:
        premises = [quantity(cases[c]["formula"]) for c in item["from"]]
        conclusion = quantity(item["formula"])
        certificate = prove_quantity(env, premises, conclusion)
        assert certificate is not None, item["id"]
        assert check_quantity_certificate(env, premises, conclusion, certificate)
        lean_cases.append({"id": item["id"], "kind": "certificate", "environment": data["environment"],
                           "premises": premises, "conclusion": conclusion, "certificate": certificate})
    if not LEAN.exists():
        pytest.skip("build the Lean ve_quantity runner first")
    process = subprocess.run([str(LEAN), "-"], input=json.dumps(lean_cases), text=True,
                             capture_output=True, timeout=HANG_TIMEOUT)
    results = json.loads(process.stdout)
    assert [r["id"] for r in results] == [c["id"] for c in data["consequences"]]
    assert all(r["status"] == "ok" and r["valid"] is True for r in results), results


def test_lean_admits_every_case_with_the_model():
    if not LEAN.exists():
        pytest.skip("build the Lean ve_quantity runner first")
    data = fixture()
    cases = [{"id": item["id"], "environment": data["environment"],
              "quantity": quantity(item["formula"]), "model": data["model"]}
             for item in data["cases"] + data["consequences"]]
    process = subprocess.run([str(LEAN), "-"], input=json.dumps(cases), text=True,
                             capture_output=True, timeout=HANG_TIMEOUT)
    results = json.loads(process.stdout)
    assert all(r["status"] == "ok" and r["value"] is True for r in results), results
