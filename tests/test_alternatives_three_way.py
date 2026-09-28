"""Spec §8 scenarios: Lean's inlined formula evaluated by three implementations."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from conformance.alternatives import base_environment, cases
from ve.alternatives import run_case
from ve.ast import formula_from_data
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_alternatives_route"


@pytest.fixture(scope="module")
def rust_binary():
    if not LEAN.is_file():
        pytest.skip("build ve_alternatives_route with lake build")
    cargo = shutil.which("cargo")
    if cargo is None:
        pytest.skip("cargo is unavailable")
    env = {**os.environ, "CARGO_HOME": str(ROOT / ".cargo-home"),
           "CARGO_TARGET_DIR": str(ROOT / "rust/target")}
    built = subprocess.run([cargo, "build", "-j", "2", "--locked", "--release",
                            "--manifest-path", str(ROOT / "rust/Cargo.toml")],
                           env=env, capture_output=True, text=True, timeout=600)
    assert built.returncode == 0, built.stdout + built.stderr
    return ROOT / "rust/target/release/ve"


@pytest.mark.parametrize("case", list(cases()), ids=lambda c: c["id"])
def test_spec_scenario_followability_three_way(case, rust_binary):
    source = {k: v for k, v in case.items() if k != "expected_clear"}
    elaborated = run_case({k: v for k, v in source.items() if k != "scenario"} |
                          {"kind": "alt-elaborate"})
    scenario = run_case(source | {"kind": "alt-validate"})
    assert scenario["status"] == "ok", case["id"]
    report = scenario["choosers"][0]
    assert report["clear"] == case["expected_clear"]

    base = base_environment(case["environment"])
    model_data = case["scenario"]["model"]
    env = Environment(base)
    model = FiniteModel.from_dict(env, model_data)
    formula = elaborated["followable"]["ast"]
    python_value = evaluate(env, formula_from_data(env, formula), model, trace=False).value

    rust = subprocess.run([str(rust_binary), "conformance"],
                          input=json.dumps([{"id": case["id"], "kind": "evaluate",
                                             "environment": base, "ast": [formula],
                                             "model": model_data}]),
                          capture_output=True, text=True, timeout=120)
    assert rust.returncode == 0, rust.stdout + rust.stderr
    rust_value = json.loads(rust.stdout)[0]["value"]
    expected = bool(case["expected_clear"])
    assert python_value == rust_value == expected == bool(report["clear"]), case["id"]
