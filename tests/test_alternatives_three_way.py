"""Spec §8 scenarios: Lean's inlined formula evaluated by three implementations."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from conformance.alternatives import base_environment, cases, rules
from ve.alternatives import run_case
from ve.ast import formula_from_data
from ve.ast import _Decoder, Not
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.norms import _bind
from ve.wire import digest


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
    probes = elaborated["profile_exists"]
    names = ("avoidable", "unavoidable", "allows", "prevents")
    formulas = [elaborated["followable"]["ast"], *(probes[name] for name in names)]
    python_values = [evaluate(env, formula_from_data(env, formula), model, trace=False).value
                     for formula in formulas]

    rust = subprocess.run([str(rust_binary), "conformance"],
                          input=json.dumps([{"id": case["id"], "kind": "evaluate",
                                             "environment": base, "ast": formulas,
                                             "model": model_data}]),
                          capture_output=True, text=True, timeout=120)
    assert rust.returncode == 0, rust.stdout + rust.stderr
    rust_values = json.loads(rust.stdout)[0]["values"]
    expected = [bool(report["clear"]), *(bool(report[name]) for name in names)]
    assert python_values == rust_values == expected, case["id"]


def test_spec_s2_conflict_three_way(rust_binary):
    case = next(c for c in cases() if c["id"] == "a")
    source = {k: v for k, v in case.items() if k != "expected_clear"}
    source["norms"] = [*source["norms"], rules()["X"]]
    source["id"] = "s2"
    elaborated = run_case({k: v for k, v in source.items() if k != "scenario"} |
                          {"kind": "alt-elaborate"})
    scenario = run_case(source | {"kind": "alt-validate"})
    assert (scenario["verdict"], scenario["target"], scenario["tuple"]) == (
        "CONFLICT", "permitted", ["nothing"])
    target = next(t for t in elaborated["conflict_targets"] if t["target"] == "permitted")
    formula = ["exists", "action", target["ast"]]
    base = base_environment(source["environment"])
    model_data = source["scenario"]["model"]
    env = Environment(base)
    model = FiniteModel.from_dict(env, model_data)
    assert evaluate(env, formula_from_data(env, formula), model, trace=False).value
    rust = subprocess.run([str(rust_binary), "conformance"],
                          input=json.dumps([{"id": "s2", "kind": "evaluate", "environment": base,
                                             "ast": [formula], "model": model_data}]),
                          capture_output=True, text=True, timeout=120)
    assert rust.returncode == 0, rust.stdout + rust.stderr
    assert json.loads(rust.stdout)[0]["values"] == [True]


def test_spec_p_outcome_completion_and_document_binding_three_way(rust_binary):
    source = deepcopy(next(c for c in cases() if c["id"] == "a"))
    source.pop("expected_clear")
    source["id"] = "p1"
    source["scenario"]["outcomes"] = [row for row in source["scenario"]["outcomes"]
                                      if row["action"] != "pull"]
    assert run_case(source | {"kind": "alt-validate"})["error"] == (
        "InvalidModel(alternatives): outcome of pull for h1 unstated")

    source["id"] = "p2"
    source["environment"]["alternatives"]["outcomes"] = {
        "complete_by": "Asimov case annotator"}
    source["environment"]["vocabulary"]["constants"] = {
        "nothing": {"sort": "action", "description": "nothing"},
        "h1": {"sort": "harm", "description": "h1"}}
    source["scenario"]["model"]["constants"] = {"nothing": "nothing", "h1": "h1"}
    source["units"] = [{"label": "cell:nothing/h1", "ast":
                        ["binary", "leads_to", ["const", "nothing"], ["const", "h1"]]}]
    elaborated = run_case({k: v for k, v in source.items() if k != "scenario"} |
                          {"kind": "alt-elaborate"})
    scenario = run_case(source | {"kind": "alt-validate"})
    assert scenario["status"] == "ok"
    assert scenario["choosers"][0]["clear"] == ["pull"]
    assert scenario["assumed_harm_free"] == ["pull/h1 (Asimov case annotator)"]
    assert scenario["conditional_on"] == ["alternatives:table_complete"]
    formulas = [elaborated["followable"]["ast"],
                elaborated["profile_exists"]["avoidable"],
                elaborated["profile_exists"]["allows"]]
    base = base_environment(source["environment"])
    model_data = source["scenario"]["model"]
    env = Environment(base)
    model = FiniteModel.from_dict(env, model_data)
    python_values = [evaluate(env, formula_from_data(env, formula), model, trace=False).value
                     for formula in formulas]
    rust = subprocess.run([str(rust_binary), "conformance"],
                          input=json.dumps([{"id": "p2", "kind": "evaluate", "environment": base,
                                             "ast": formulas, "model": model_data}]),
                          capture_output=True, text=True, timeout=120)
    assert rust.returncode == 0, rust.stdout + rust.stderr
    assert python_values == json.loads(rust.stdout)[0]["values"] == [True, True, True]

    changed = deepcopy(source)
    changed["id"] = "p6"
    changed["scenario"]["outcomes"].append(
        {"action": "pull", "harm": "h1", "leads_to": True, "support": "testimony"})
    changed["scenario"]["model"]["relations"]["leads_to"].append(["pull", "h1"])
    assert run_case(changed | {"kind": "alt-validate"})["error"] == (
        "InvalidModel(alternatives): premise alternatives:table_complete fails")


def test_spec_h3_proximate_claim_requires_leading_to_harm(rust_binary):
    source = deepcopy(next(c for c in cases() if c["id"] == "h-7"))
    source.pop("expected_clear")
    source["id"] = "h3"
    source["scenario"]["model"]["relations"]["causes"] = [["operate", "hd"]]
    elaborated = run_case({k: v for k, v in source.items() if k != "scenario"} |
                          {"kind": "alt-elaborate"})
    scenario = run_case(source | {"kind": "alt-validate"})
    assert scenario["error"] == (
        "InvalidModel(alternatives): operate causes hd but does not lead to it")
    proximate = next(item["ast"] for item in elaborated["alternatives"]
                     if item["label"] == "alternatives:proximate")
    base = base_environment(source["environment"])
    model_data = source["scenario"]["model"]
    env = Environment(base)
    model = FiniteModel.from_dict(env, model_data)
    assert not evaluate(env, formula_from_data(env, proximate), model, trace=False).value
    rust = subprocess.run([str(rust_binary), "conformance"],
                          input=json.dumps([{"id": "h3", "kind": "evaluate", "environment": base,
                                             "ast": [proximate], "model": model_data}]),
                          capture_output=True, text=True, timeout=120)
    assert rust.returncode == 0, rust.stdout + rust.stderr
    assert json.loads(rust.stdout)[0]["values"] == [False]


def _source_and_conflict_packages(case):
    source = {k: v for k, v in case.items() if k not in ("scenario", "expected_clear")}
    env = Environment(source["environment"])
    base = Environment(base_environment(source["environment"]))
    elaborated = run_case(source | {"kind": "alt-elaborate"})
    document_hash = digest(f"ve-alternatives-{env.identity_version}\n", {
        "environment_id": env.environment_id, "norms": source["norms"], "units": []})
    packages = {}
    for target in elaborated["conflict_targets"]:
        conclusion = _bind(Not(_Decoder().decode(target["ast"])), target["sorts"])
        proof = prove_entailment(base, (), conclusion, max_steps=10000)
        assert proof.status == "Found", (case["id"], target["target"], proof.status)
        packages[target["target"]] = {
            "environment_id": env.environment_id, "document_hash": document_hash,
            "target": target["target"], "certificate": proof.certificate}
    return source, base, elaborated, document_hash, packages


@pytest.mark.parametrize("name,diagnosis", [
    ("b-A1", "NONE-PERMITTED"),
    ("b-B", "JOINTLY-UNDISCHARGEABLE"),
    ("j", "OVER-REQUIRED"),
])
def test_spec_conflict_certificates_and_dilemma_witness_replay(name, diagnosis):
    case = next(c for c in cases() if c["id"] == name)
    source, _, _, _, packages = _source_and_conflict_packages(case)
    assert run_case(source | {"kind": "alt-conflict", "packages": packages})["verdict"] == "CONFLICT-FREE"
    result = run_case(source | {"kind": "alt-followable", "packages": packages,
                                "witness": {**case["scenario"], "chooser": "r"}})
    assert result["verdict"] == "DILEMMA"
    assert result["diagnosis"].startswith(diagnosis)
    changed = deepcopy(source)
    changed["environment"]["alternatives"]["decided_by"] = "another annotator"
    assert run_case(changed | {"kind": "alt-conflict", "packages": packages})["verdict"] == "UNKNOWN"


def test_rule_free_followable_certificate_replay():
    case = {"id": "rule-free", "environment": next(cases())["environment"], "norms": []}
    source, base, elaborated, document_hash, packages = _source_and_conflict_packages(case)
    premises = [formula_from_data(base, item["ast"]) for item in elaborated["alternatives"]]
    conclusion = formula_from_data(base, elaborated["followable"]["ast"])
    proof = prove_entailment(base, premises, conclusion, max_steps=10000)
    assert proof.status == "Found"
    package = {"environment_id": Environment(source["environment"]).environment_id,
               "document_hash": document_hash, "target": "followable",
               "certificate": proof.certificate}
    result = run_case(source | {"kind": "alt-followable", "packages": packages,
                                "package": package})
    assert result["verdict"] == "FOLLOWABLE"
    assert result["conditional_on"] == []
