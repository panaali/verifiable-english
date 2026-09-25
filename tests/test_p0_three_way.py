"""Three-way P0 conformance: Python, Rust and the Lean `route` subcommand give
identical verdicts on every shipped case of the P0 families (PLAN-EXPAND2 3.10(2)).

Rust scope (plan 3.7): envelopes, Background, model validity, evaluation and
search, plus the label grammar and the dependency order. Rust has no certificate
checker, so on a certificate or inconsistency case its verdict is that bounded
search finds no model; admission is Python and Lean only; the order family is
evaluation only in Rust (numbers2 scope).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from conformance.p0 import FAMILIES, lean_case

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_conformance"
KNOWN = ("UnsupportedProfile", "InvalidModel", "ResourceLimit", "DuplicateDeclaration",
         "AdmissionError", "DependencyCycle")


def fixture(name):
    return json.loads((ROOT / f"conformance/{name}.json").read_text())


def active(name):
    return [case for case in fixture(name) if "pending" not in case]


def diagnostic(code, message):
    return message if re.match(r"[A-Z][A-Za-z]+(: |\()", message) else f"{code}: {message}"


def error_verdict(code, message, generator=None):
    text = diagnostic(code, message)
    if text.startswith("InvalidModel"):
        code = "InvalidModel"
    else:
        head = text.split(":", 1)[0]
        code = head if head in KNOWN else code if code in KNOWN else "rejected"
    out = {"status": "error", "code": code, "error": text}
    if generator is not None:
        out["generator"] = generator
    return out


def agrees(expected, verdict):
    return all(verdict.get(key) == value for key, value in expected.items())


# ---------------------------------------------------------------- Python

def python_verdict(case):
    from ve import Environment, FiniteModel, evaluate
    from ve.admission import admit_document, parse_label, validate_label
    from ve.ast import Bottom, document_from_data, formula_from_data
    from ve.background import background, dependency_order_nodes
    from ve.entailment import check_entailment_certificate
    from ve.errors import InvalidModel, VEError
    from ve.search import check_countermodel, find_countermodel
    from ve.vacuity import premise_status
    kind = case["kind"]
    try:
        if kind == "label":
            validate_label(case["label"])
            Environment(case["environment"])
            return {"status": "ok", "label": parse_label(case["label"]).render()}
        env = Environment(case["environment"])
        if kind == "dependency-order":
            return {"status": "ok", "order": list(dependency_order_nodes(case["nodes"]))}
        if kind == "admission":
            return {"status": "ok", **admit_document(env, case["document"])}
        if kind == "evaluate":
            model = FiniteModel.from_dict(env, case["model"])
            doc = document_from_data(env, case["ast"])
            return {"status": "ok", "values": [evaluate(env, f, model, trace=False).value
                                               for f in doc.formulas]}
        premises = [formula_from_data(env, p) for p in case["premises"]]
        if kind == "vacuity":
            if "model" in case:
                witness = check_countermodel(env, premises, Bottom(),
                                             FiniteModel.from_dict(env, case["model"])).valid
            else:
                witness = check_entailment_certificate(env, premises, Bottom(), case["certificate"]).valid
            assert witness, case["id"]
            return {"status": "ok", "premises": premise_status(env, premises)["status"]}
        conclusion = formula_from_data(env, case["conclusion"])
        if kind == "countermodel":
            model = FiniteModel.from_dict(env, case["model"])
            return {"status": "ok", "refutes": check_countermodel(env, premises, conclusion, model).valid}
        if kind == "search":
            found = find_countermodel(env, premises, conclusion, max_domain_size=case["max_domain_size"])
            return {"status": "ok", "found": found.status == "Found",
                    "model": found.model.to_dict() if found.model else None}
        assert kind == "certificate"
        checked = check_entailment_certificate(env, premises, conclusion, case["certificate"])
        return {"status": "ok", "valid": checked.valid, "background": len(background(env))}
    except InvalidModel as exc:
        return error_verdict(exc.code, exc.message, exc.generator)
    except VEError as exc:
        return error_verdict(exc.code, exc.message)


# ---------------------------------------------------------------- Rust

def rust_request(case):
    """The Rust conformance input for a case, or None outside Rust scope."""
    kind, env = case["kind"], case["environment"]
    order = "order@0" in env.get("profiles", [])
    base = {"id": case["id"], "environment": env}
    if kind in ("label", "dependency-order"):
        return {**case}
    if kind == "evaluate":
        return {**base, "model": case["model"], "ast": case["ast"]}
    if kind == "admission" or order:
        return None
    if kind == "countermodel":
        return {**base, "model": case["model"], "premises": case["premises"], "conclusion": case["conclusion"]}
    if kind == "search":
        return {**base, "premises": case["premises"], "conclusion": case["conclusion"],
                "max_domain_size": case["max_domain_size"]}
    if kind == "vacuity":
        return {**base, "premises": case["premises"], "conclusion": ["bottom"], "max_domain_size": 2}
    if kind == "certificate" and case["expected"].get("valid"):
        return {**base, "premises": case["premises"], "conclusion": case["conclusion"], "max_domain_size": 2}
    return None


def rust_verdict(case, result):
    kind = case["kind"]
    if result.get("status") == "error":
        error = result["error"]
        generator = "literals" if error["message"].endswith("(literals)") else None
        return error_verdict(error["code"], error["message"], generator)
    if kind == "label":
        return {"status": "ok", "label": result["label"]}
    if kind == "dependency-order":
        return {"status": "ok", "order": result["order"]}
    if kind == "evaluate":
        return {"status": "ok", "values": result["values"]}
    if kind == "countermodel":
        return {"status": "ok", "refutes": result["valid"]}
    if kind == "search":
        return {"status": "ok", "found": result["status"] == "Found", "model": result.get("model")}
    if kind == "vacuity":
        return {"status": "ok", "premises": "model" if result["status"] == "Found" else "no model found"}
    assert kind == "certificate"
    return {"status": "ok", "valid": result["status"] != "Found"}


# ---------------------------------------------------------------- Lean

def lean_verdict(case, result):
    kind = case["kind"]
    if result.get("status") == "error":
        verdict = error_verdict("rejected", result["error"], result.get("generator"))
        if kind == "certificate" and verdict["code"] not in ("UnsupportedProfile", "ResourceLimit"):
            return {"status": "ok", "valid": False}
        return verdict
    if kind == "search":
        return {"status": "ok", "found": result["refutes"]}
    if kind == "vacuity":
        if "model" in case:
            return {"status": "ok", "premises": "model" if result["refutes"] else "unwitnessed"}
        return {"status": "ok", "premises": "INCONSISTENT" if result["valid"] else "unwitnessed"}
    return result


def run(command, cases):
    completed = subprocess.run(command, input=json.dumps(cases), text=True, capture_output=True, timeout=600)
    assert completed.returncode in (0, 1), completed.stderr
    results = json.loads(completed.stdout)
    assert len(results) == len(cases)
    return results


@pytest.fixture(scope="module")
def lean_executable():
    if not LEAN.exists():
        pytest.skip("lean route runner is not built (lake build)")
    return LEAN


@pytest.fixture(scope="module")
def rust_executable():
    cargo = shutil.which("cargo")
    if not cargo:
        pytest.skip("cargo is not available")
    env = {**os.environ, "CARGO_HOME": str(ROOT / ".cargo-home"), "CARGO_TARGET_DIR": str(ROOT / "rust/target")}
    built = subprocess.run([cargo, "build", "-j", "2", "--locked", "--release", "--manifest-path",
                            str(ROOT / "rust/Cargo.toml")], cwd=ROOT, env=env, capture_output=True,
                           text=True, timeout=600)
    assert built.returncode == 0, built.stdout + built.stderr
    return ROOT / "rust/target/release/ve"


def test_fixtures_are_generated():
    for name, build in FAMILIES.items():
        assert fixture(name) == json.loads(json.dumps(build())), name


@pytest.mark.parametrize("family", list(FAMILIES))
def test_python_matches_expected(family):
    for case in active(family):
        verdict = python_verdict(case)
        assert agrees(case["expected"], verdict), (case["id"], case["expected"], verdict)


@pytest.mark.parametrize("family", list(FAMILIES))
def test_lean_matches_expected(family, lean_executable):
    cases = active(family)
    results = run([str(lean_executable), "route", "-"], [lean_case(c) for c in cases])
    for case, result in zip(cases, results, strict=True):
        verdict = lean_verdict(case, result)
        assert agrees(case["expected"], verdict), (case["id"], case["expected"], result)


@pytest.mark.parametrize("family", list(FAMILIES))
def test_rust_matches_expected(family, rust_executable):
    requests = [(case, rust_request(case)) for case in active(family)]
    requests = [(case, request) for case, request in requests if request is not None]
    if not requests:
        pytest.skip(f"{family} is outside Rust scope")
    results = run([str(rust_executable), "conformance"], [r for _, r in requests])
    for (case, _), result in zip(requests, results, strict=True):
        verdict = rust_verdict(case, result)
        expected = dict(case["expected"])
        if case["kind"] == "vacuity" and expected["premises"] == "INCONSISTENT":
            expected["premises"] = "no model found"  # Rust never certifies inconsistency
        if case["kind"] == "certificate":
            expected = {"status": "ok", "valid": True}  # no countermodel within the bound
        assert agrees(expected, verdict), (case["id"], expected, result)


def test_rust_and_python_share_identities_and_models(rust_executable):
    """Beyond verdicts: the same environment, meaning and model ids, and the
    same model from bounded search."""
    from ve import Environment, FiniteModel
    from ve.ast import document_from_data
    from ve.identity import meaning_id
    cases = [c for c in active("elaborated-document") if c["kind"] in ("evaluate", "search")
             and c["expected"]["status"] == "ok"]
    results = run([str(rust_executable), "conformance"], [rust_request(c) for c in cases])
    for case, result in zip(cases, results, strict=True):
        env = Environment(case["environment"])
        if case["kind"] == "search":
            assert result["model"] == python_verdict(case)["model"], case["id"]
            continue
        doc = document_from_data(env, case["ast"])
        assert result["environment_id"] == env.environment_id, case["id"]
        assert result["meaning_id"] == meaning_id(env, doc), case["id"]
        assert result["model_id"] == FiniteModel.from_dict(env, case["model"]).model_id, case["id"]


def test_lean_seed_cases_are_the_shared_families():
    """lean/VE/Route/examples/route-cases.json is generated from these families."""
    seeds = json.loads((ROOT / "lean/VE/Route/examples/route-cases.json").read_text())
    expected = [lean_case(c) for name in FAMILIES for c in active(name)]
    assert seeds == json.loads(json.dumps(expected))


def test_python_claim_labels_follow_the_route_grammar():
    from conformance.p0 import environment
    from ve import Environment
    from ve.admission import AdmissionError
    from ve.argument import Claim
    env = Environment(environment())
    assert Claim.create(env, "c", "true.\n", label="background:literals").label == "background:literals"
    for label in ("background:strings", "readings:s@01:0", "free text"):
        with pytest.raises(AdmissionError, match="invalid label"):
            Claim.create(env, "c", "true.\n", label=label)


def test_python_certificates_always_bind_background_first():
    """A premise list that already starts with the Background premise is not
    merged with it: the checked list is Background ++ premises, as in Lean."""
    from conformance.p0 import DISTINCT, FIN_A, SAME, VOCAB, envelope
    from ve import Environment
    from ve.ast import formula_from_data
    from ve.entailment import prove_entailment
    from ve.identity import meaning_id
    env = Environment(envelope(VOCAB))
    premises = [formula_from_data(env, p) for p in (DISTINCT, ["or", SAME, FIN_A])]
    proof = prove_entailment(env, premises, formula_from_data(env, FIN_A))
    distinct = meaning_id(env, premises[0])
    assert proof.certificate["premise_meaning_ids"][:2] == [distinct, distinct]
    assert len(proof.certificate["premise_meaning_ids"]) == 3
