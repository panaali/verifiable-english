"""Portable JSON differential tests. No files under ve/ are modified by Lean."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from ve import Environment, FiniteModel, evaluate, parse, print_document
from ve.ast import document_from_data
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "conformance/evaluation.json").read_text())


@pytest.fixture(scope="session")
def lean_executable():
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    build = subprocess.run([lake, "build"], cwd=ROOT / "lean", capture_output=True, text=True, timeout=180)
    assert build.returncode == 0, build.stdout + build.stderr
    return ROOT / "lean/.lake/build/bin/ve_conformance"


def invoke(executable, cases, expected_code=0):
    result = subprocess.run([str(executable)], input=json.dumps(cases), capture_output=True, text=True, timeout=60)
    assert result.returncode == expected_code, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_shared_fixture_python_golden_values():
    for case in CASES:
        env = Environment.from_dict(case["environment"])
        model = FiniteModel.from_dict(env, case["model"])
        doc = document_from_data(env, case["ast"])
        assert parse(env, case["source"]) == doc, case["id"]
        assert print_document(env, doc) == case["source"], case["id"]
        assert [evaluate(env, f, model).value for f in doc.formulas] == case["expected"], case["id"]


def test_lean_agrees_on_every_shared_case(lean_executable):
    results = invoke(lean_executable, CASES)
    assert len(results) == len(CASES)
    for case, result in zip(CASES, results, strict=True):
        env = Environment.from_dict(case["environment"])
        doc = document_from_data(env, case["ast"])
        model = FiniteModel.from_dict(env, case["model"])
        expected = [evaluate(env, f, model).value for f in doc.formulas]
        assert result == {"id": case["id"], "status": "ok", "values": expected, "value": all(expected), "canonical": case["source"]}


def malformed_cases():
    base = CASES[0]
    mutations = [
        lambda c: c["environment"].update(language="unknown"),
        lambda c: c["environment"].update(extra="unknown"),
        lambda c: c["environment"]["vocabulary"]["sorts"]["person"].update(description=""),
        lambda c: c["environment"]["vocabulary"]["predicates"]["owns"].update(arguments=["unknown", "service"]),
        lambda c: c["environment"]["vocabulary"]["predicates"]["owns"].update(arguments=[]),
        lambda c: c["model"].update(complete=False),
        lambda c: c["model"].update(complete=1),
        lambda c: c["model"].update(extra=[]),
        lambda c: c["model"]["relations"].pop("owns"),
        lambda c: c["model"]["domains"].pop("person"),
        lambda c: c["model"]["domains"]["person"].append("alice"),
        lambda c: c["model"]["domains"]["person"].append("Bad"),
        lambda c: c["model"]["relations"]["owns"].append(["alice", "api"]),
        lambda c: c["model"]["relations"].update(owns=[["missing", "api"]]),
        lambda c: c["model"]["relations"].update(owns=[["api", "alice"]]),
        lambda c: c["model"]["relations"].update(owns=[["alice"]]),
        lambda c: c.update(ast=[]),
        lambda c: c.update(ast=[["top", "extra"]]),
        lambda c: c.update(ast=[["unknown"]]),
        lambda c: c.update(ast=[["eq", ["var", 0], ["var", 0]]]),
        lambda c: c.update(ast=[["forall", "missing", ["top"]]]),
        lambda c: c.update(ast=[["forall", "person", ["unary", "deployed", ["var", 0]]]]),
        lambda c: c.update(ast=[["forall", "person", ["unary", "owns", ["var", 0]]]]),
        lambda c: c.update(ast=[["forall", "person", ["eq", ["var", True], ["var", 0]]]]),
        lambda c: c.update(ast=[["forall", "person", ["eq", ["var", -1], ["var", 0]]]]),
        lambda c: c.update(ast=[["forall", "person", ["exists", "service", ["eq", ["var", 0], ["var", 1]]]]]),
    ]
    cases = []
    for i, mutate in enumerate(mutations):
        case = copy.deepcopy(base)
        mutate(case)
        case["id"] = f"invalid_{i}"
        cases.append(case)
    return cases


def test_both_decoders_reject_malformed_cases(lean_executable):
    for case in malformed_cases():
        with pytest.raises(VEError):
            env = Environment.from_dict(case["environment"])
            model = FiniteModel.from_dict(env, case["model"])
            doc = document_from_data(env, case["ast"])
            evaluate(env, doc, model)
        result = subprocess.run([str(lean_executable)], input=json.dumps(case), capture_output=True, text=True, timeout=10)
        assert result.returncode != 0, case["id"]


@pytest.mark.parametrize("raw", [
    '{"a":1,"a":2}', '{"a":1,"\\u0061":2}', '{"a":{"b":1,"b":2}}',
    '{"a":"\\ud800"}', '{"a":"\\udfff"}', '{"a":"\\ud800x"}',
    '{"a":null}', '{"a":1.0}', '{"a":1e0}', '{"a":-1}', '{"a":9007199254740992}',
])
def test_lean_rejects_invalid_raw_json(lean_executable, raw):
    result = subprocess.run([str(lean_executable)], input=raw, capture_output=True, text=True, timeout=10)
    assert result.returncode == 2, result.stdout + result.stderr


def test_lean_source_resolution_and_canonical_binder_order(lean_executable):
    cases = []
    for original in CASES[:3] + CASES[-12:]:
        case = copy.deepcopy(original)
        case["source"] = case["source"].replace("x0", "trueish").replace("x1", "falsehood")
        case["source"] = case["source"].replace("x2", "notable").replace("x3", "therefore")
        cases.append(case)
    sibling = copy.deepcopy(CASES[0])
    sibling["id"] = "sibling_scopes"
    sibling["source"] = "(for every service s, (s is deployed)) and (for every service s, (s is reviewed)).\n"
    env = Environment.from_dict(sibling["environment"])
    doc = parse(env, sibling["source"])
    from ve.ast import document_to_data
    sibling["ast"] = document_to_data(env, doc)
    cases.append(sibling)
    results = invoke(lean_executable, cases)
    for case, result in zip(cases, results, strict=True):
        env = Environment.from_dict(case["environment"])
        doc = parse(env, case["source"])
        assert result["canonical"] == print_document(env, doc), case["id"]


@pytest.mark.parametrize("source", [
    "true.", "true.\r\n", "true.\n\n", " true.\n", "true .\n", "(true).\n",
    "true and false.\n", "True.\n", "true.\n#comment\n", "true.\t\n",
    "for every service s, (for every service s, (true)).\n",
    "for every service person, (true).\n", "for every service not, (true).\n",
    "for every service s, (s is deployed).\nthere exists service t, (s is reviewed).\n",
])
def test_lean_rejects_non_strict_or_unbound_source(lean_executable, source):
    case = copy.deepcopy(CASES[0])
    case["source"] = source
    env = Environment.from_dict(case["environment"])
    with pytest.raises(VEError):
        parse(env, source)
    assert invoke(lean_executable, case, 1)[0]["status"] == "error"


def test_lean_rejects_individually_valid_source_ast_substitution(lean_executable):
    case = copy.deepcopy(CASES[0])
    case["source"] = "true.\n"
    assert invoke(lean_executable, case, 1)[0]["error"] == "source/AST mismatch"


def test_lean_json_accepts_unicode_descriptions(lean_executable):
    case = copy.deepcopy(CASES[0])
    case["environment"]["vocabulary"]["sorts"]["person"]["description"] = "Person \U0001f600 \u20ac"
    for escaped in (True, False):
        result = subprocess.run([str(lean_executable)], input=json.dumps(case, ensure_ascii=escaped),
                                capture_output=True, text=True, timeout=10)
        assert result.returncode == 0, result.stderr + result.stdout


def test_lean_and_python_accept_identity_bound_display_metadata(lean_executable):
    case = copy.deepcopy(CASES[0])
    vocab = case["environment"]["vocabulary"]
    vocab["sorts"]["person"]["verbalisation"] = {"singular": "person", "plural": "people"}
    vocab["predicates"]["owns"].update(verbalisation="{0} owns {1}",
                                        negative_verbalisation="{0} does not own {1}")
    env = Environment(case["environment"])
    doc = document_from_data(env, case["ast"])
    model = FiniteModel.from_dict(env, case["model"])
    assert invoke(lean_executable, case)[0]["values"] == [evaluate(env, f, model).value for f in doc.formulas]
    # Rejected display templates remain inert data in both semantic decoders.
    vocab["predicates"]["owns"]["negative_verbalisation"] = "{0} owns {1}"
    Environment(case["environment"])
    assert invoke(lean_executable, case)[0]["values"] == case["expected"]


@pytest.mark.parametrize("field,bad", [
    ("verbalisation", []), ("verbalisation", ""), ("verbalisation", "x" * 257),
    ("negative_verbalisation", {}), ("negative_verbalisation", ""),
    ("negative_verbalisation", "x" * 257), ("unknown_verbalisation", "word"),
])
def test_lean_and_python_reject_malformed_display_metadata(lean_executable, field, bad):
    case = copy.deepcopy(CASES[0])
    case["environment"]["vocabulary"]["predicates"]["owns"][field] = bad
    with pytest.raises(VEError):
        Environment(case["environment"])
    assert invoke(lean_executable, case, 1)[0]["status"] == "error"


def test_lean_transitive_axiom_allowlist(lean_executable):
    import sys
    result = subprocess.run([sys.executable, str(ROOT / "lean/audit.py")], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS:" in result.stdout
