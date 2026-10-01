"""Spec §8 scenarios: Lean's inlined formula evaluated by three implementations."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from conformance.alternatives import base_environment, cases, environment as fixture_environment, rules
from tools import rust_build
from ve.alternatives import run_case
from ve.admission import AdmissionError, admit_document
from ve.norm_admission import admit_norm_document
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
    if os.environ.get("VE_RUST_PREBUILT"):
        binary = Path(os.environ["VE_RUST_BINARY"])
        assert binary.is_file(), f"gate Rust build missing: {binary}"
        return binary
    cargo = shutil.which("cargo")
    if cargo is None:
        pytest.skip("cargo is unavailable")
    env = rust_build.cargo_env()
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
    env_id = Environment(source["environment"]).environment_id
    assert scenario["environment_id"] == env_id
    assert scenario["document_hash"] == digest(
        f"ve-alternatives-{Environment(source['environment']).identity_version}\n",
        {"environment_id": env_id, "norms": source["norms"], "units": source.get("units", [])})

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


def test_mapped_violation_requires_a_taken_action_and_failed_fulfilment(rust_binary):
    case = deepcopy(next(c for c in cases() if c["id"] == "f1"))
    case.pop("expected_clear")
    taken = case["scenario"]["model"]["relations"]["taken"]
    base = base_environment(case["environment"])
    env = Environment(base)
    failed_fulfilment = ["exists", "action", ["and", ["unary", "taken", ["var", 0]],
                          ["not", case["environment"]["alternatives"]["fulfilments"][1]["body"]]]]
    for action, expected in (("refuse", True), ("refer", False), (None, False)):
        taken[:] = [[action]] if action else []
        report = run_case(case | {"kind": "alt-validate"})["choosers"][0]
        assert report["violations"] == ([{"obligation": "respond_required", "arguments": ["r"]}]
                                         if expected else [])
        model_data = case["scenario"]["model"]
        model = FiniteModel.from_dict(env, model_data)
        assert evaluate(env, formula_from_data(env, failed_fulfilment), model, trace=False).value == expected
        rust = subprocess.run([str(rust_binary), "conformance"],
                              input=json.dumps([{"id": "mapped", "kind": "evaluate",
                                                 "environment": base, "ast": [failed_fulfilment],
                                                 "model": model_data}]),
                              capture_output=True, text=True, timeout=120)
        assert rust.returncode == 0, rust.stdout + rust.stderr
        assert json.loads(rust.stdout)[0]["values"] == [expected]


def test_scenario_document_binding_changes_with_rules_and_units():
    case = deepcopy(next(c for c in cases() if c["id"] == "a"))
    case.pop("expected_clear")
    initial = run_case(case | {"kind": "alt-validate"})
    without_rule = deepcopy(case)
    without_rule["norms"] = []
    changed = run_case(without_rule | {"kind": "alt-validate"})
    assert initial["model_id"] == changed["model_id"]
    assert initial["document_hash"] != changed["document_hash"]
    assert initial["choosers"][0]["clear"] != changed["choosers"][0]["clear"]
    with_unit = deepcopy(case)
    with_unit["units"] = [{"label": "fact", "ast": ["top"]}]
    assert run_case(with_unit | {"kind": "alt-validate"})["document_hash"] != initial["document_hash"]


def test_w2_admission_uses_regenerated_alternatives_leaves():
    case = deepcopy(next(c for c in cases() if c["id"] == "a"))
    env = Environment(case["environment"])
    elaborated = run_case({"id": "source", "kind": "alt-elaborate",
                           "environment": case["environment"], "norms": []})
    premise = next(p for p in elaborated["alternatives"] if p["label"] == "alternatives:own")
    document = {"units": [], "graph": {"root": "slot", "nodes": [
        {"name": "slot", "label": premise["label"], "ast": premise["ast"]}]}}
    result = admit_document(env, document)
    assert admit_norm_document(env, document) == result
    assert result["admitted"] is True
    assert result["report"]["assumptions"][0]["label"] == "alternatives:own"
    assert len(result["report_id"]) == 64
    stale = deepcopy(document)
    stale["graph"]["nodes"][0]["ast"] = ["top"]
    with pytest.raises(AdmissionError):
        admit_document(env, stale)
    changed = deepcopy(case["environment"])
    changed["alternatives"]["decided_by"] = "another decider"
    assert admit_document(Environment(changed), document)["report_id"] != result["report_id"]


@pytest.mark.parametrize("word,first,second", [
    ("avoidable", "h", "r"),
    ("unavoidable", "h", "r"),
    ("allows", "pull", "h"),
    ("prevents", "pull", "h"),
])
@pytest.mark.parametrize("source_kind", ["asserted", "quoted", "reading", "lemma"])
def test_w2_admission_profile_words_in_units_and_roots(word, first, second, source_kind):
    raw = fixture_environment()
    raw["vocabulary"]["constants"] = {
        "pull": {"sort": "action", "description": "pull"},
        "r": {"sort": "robot", "description": "r"},
        "h": {"sort": "harm", "description": "h"},
    }
    atom = ["binary", word, ["const", first], ["const", second]]
    unit = {"id": "profile", "span": [0, 1], "kind": "asserted", "content": atom}
    node = {"name": "root", "ast": atom, "unit": "profile"}
    document = {"units": [unit], "graph": {"root": "root", "nodes": [node]}}
    if source_kind == "quoted":
        unit["kind"] = ["attributed", "author", "says", "asserted"]
        node.pop("unit")
        node["label"] = "bridge:accepts(author,profile)"
    elif source_kind == "reading":
        document["units"] = []
        document["reading_sets"] = [{"id": "profile", "version": 1,
                                      "readings": [atom]}]
        node.pop("unit")
        node["label"] = "readings:profile@1:0"
    elif source_kind == "lemma":
        document["units"] = []
        document["lemmas"] = [{"name": "bundle/profile", "conclusion": atom,
                               "leaves": []}]
        node.pop("unit")
        node["label"] = "cite:bundle/profile"
    result = admit_document(Environment(raw), document)
    assert result["admitted"]
    assert result["report"]["root"]["ast"] == atom


def test_w2_admission_regenerates_profile_definition_leaf():
    raw = fixture_environment()
    atom = ["binary", "avoidable", ["var", 1], ["var", 0]]
    body = ["exists", "action", ["and",
            ["binary", "available", ["var", 0], ["var", 1]],
            ["not", ["binary", "leads_to", ["var", 0], ["var", 2]]]]]
    definition = ["forall", "harm", ["forall", "robot", ["and",
                  ["implies", atom, body], ["implies", body, atom]]]]
    document = {"units": [], "graph": {"root": "definition", "nodes": [
        {"name": "definition", "label": "alternatives:profile:avoidable",
         "ast": definition}]}}
    assert admit_document(Environment(raw), document)["admitted"]
    stale = deepcopy(document)
    stale["graph"]["nodes"][0]["ast"] = ["top"]
    with pytest.raises(AdmissionError):
        admit_document(Environment(raw), stale)


def test_w2_admission_regenerates_norm_layer_and_table_completion():
    env_data = deepcopy(next(c for c in cases() if c["id"] == "a")["environment"])
    env_data["alternatives"]["outcomes"] = {"complete_by": "annotator"}
    env_data["vocabulary"]["constants"] = {
        "nothing": {"sort": "action", "description": "nothing"},
        "h": {"sort": "harm", "description": "h"}}
    norm = deepcopy(rules()["7"])
    cell = ["binary", "leads_to", ["const", "nothing"], ["const", "h"]]
    source = {"id": "generated", "kind": "alt-elaborate", "environment": env_data,
              "norms": [norm], "units": [{"label": "unit:cell", "ast": cell}]}
    elaborated = run_case(source)
    assert elaborated["status"] == "ok"
    layer = next(p for p in elaborated["premises"] if p["label"] == "layer:norms:permitted")
    completion = next(p for p in elaborated["base_premises"]
                      if p["label"] == "alternatives:table_complete")
    document = {"units": [
        {"id": "rule", "span": [0, 1], "kind": "norm", "content": norm},
        {"id": "cell", "span": [1, 2], "kind": "asserted", "content": cell}],
        "graph": {"root": "layer", "nodes": [
            {"name": "layer", "label": layer["label"], "ast": layer["ast"]},
            {"name": "completion", "label": completion["label"], "ast": completion["ast"]}]}}
    admitted = admit_document(Environment(env_data), document)
    assert admitted["admitted"]
    assert admitted["kinds"] == ["norm", "asserted"]
    assert "alternatives:table_complete" in admitted["conditional_on"]
    document["graph"]["root"] = "completion"
    assert admit_document(Environment(env_data), document)["report"]["root"]["label"] == "alternatives:table_complete"
    stale = deepcopy(document)
    stale["units"][1]["content"] = ["not", cell]
    with pytest.raises(AdmissionError):
        admit_document(Environment(env_data), stale)


def test_w2_quoted_norm_does_not_activate_a_layer():
    env_data = deepcopy(next(c for c in cases() if c["id"] == "a")["environment"])
    norm = deepcopy(rules()["7"])
    source = run_case({"id": "empty", "kind": "alt-elaborate",
                       "environment": env_data, "norms": []})
    premise = next(p for p in source["alternatives"] if p["label"] == "alternatives:own")
    document = {"units": [{"id": "quote", "span": [0, 1],
                           "kind": ["attributed", "alice", "says", "norm"],
                           "content": norm}],
                "graph": {"root": "slot", "nodes": [
                    {"name": "slot", "label": premise["label"], "ast": premise["ast"]}]}}
    env = Environment(env_data)
    assert admit_document(env, document)["kinds"] == [["attributed", "alice", "says", "norm"]]
    layer = next(p for p in run_case({"id": "active", "kind": "alt-elaborate",
                                     "environment": env_data, "norms": [norm]})["premises"]
                 if p["label"] == "layer:norms:permitted")
    document["graph"] = {"root": "layer", "nodes": [
        {"name": "layer", "label": layer["label"], "ast": layer["ast"]}]}
    with pytest.raises(AdmissionError):
        admit_document(env, document)


def test_legend_uses_act_words_without_template_slots():
    case = next(c for c in cases() if c["id"] == "t")
    elaborated = run_case({"id": "legend", "kind": "alt-elaborate",
                           "environment": case["environment"], "norms": case["norms"]})
    lines = elaborated["legend"]
    assert any('fulfils "prevent"' in line for line in lines)
    assert any('duties do not bear on the choice: "file a report"' in line for line in lines)
    assert all("{0}" not in line and "{1}" not in line for line in lines)


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


@pytest.mark.parametrize("with_rule_five", [False, True], ids=["A-minus", "A-minus-5"])
def test_spec_bprime_unrelated_permission_conflict_three_way(with_rule_five, rust_binary):
    case = deepcopy(next(c for c in cases() if c["id"] == "bprime-A"))
    case.pop("expected_clear")
    case["id"] = "bprime-Aminus5" if with_rule_five else "bprime-Aminus"
    selected = ("3", "5", "7", "9m") if with_rule_five else ("3", "7", "9m")
    case["norms"] = [deepcopy(rules()[name]) for name in selected]
    case["scenario"]["model"]["relations"]["injures_human"] = [["nothing"], ["pull"]]
    elaborated = run_case({k: v for k, v in case.items() if k != "scenario"} |
                          {"kind": "alt-elaborate"})
    scenario = run_case(case | {"kind": "alt-validate"})
    assert (scenario["verdict"], scenario["target"], scenario["tuple"]) == (
        "CONFLICT", "permitted", ["nothing"])
    target = next(item for item in elaborated["conflict_targets"]
                  if item["target"] == "permitted")
    formula = ["exists", "action", target["ast"]]
    base = base_environment(case["environment"])
    model_data = case["scenario"]["model"]
    env = Environment(base)
    model = FiniteModel.from_dict(env, model_data)
    assert evaluate(env, formula_from_data(env, formula), model, trace=False).value
    rust = subprocess.run([str(rust_binary), "conformance"],
                          input=json.dumps([{"id": case["id"], "kind": "evaluate", "environment": base,
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
