"""The P0 route adapters shared by the three-way tests and the differential fuzzer.

Each adapter runs one P0 case (`conformance/p0.py`) on one implementation and
reduces its answer to a verdict: Python in process (`python_verdict`), Rust
through `ve conformance` (`rust_request`, `rust_verdict`) and Lean through
`ve_conformance route` (`lean_verdict`). Errors are reduced by `error_verdict`
to the P0 contract's codes (`KNOWN`), whose texts the contract fixes; every
other rejection is `rejected`. The reduction is the three-way test's contract
only: each error verdict also keeps the implementation's own diagnostic code
(`diagnostic_code`: Python's `VEError.code`, Rust's error code, and for Lean the
code `checker_error` gives its text, as the Lean backend raises it), which the
differential fuzzer compares. Used by tests/test_p0_three_way.py and
tools/difffuzz.py.
"""
from __future__ import annotations

import json
import re
import subprocess

from tests.subprocesses import HANG_TIMEOUT

KNOWN = ("UnsupportedProfile", "InvalidModel", "ResourceLimit", "DuplicateDeclaration",
         "AdmissionError", "DependencyCycle")


def diagnostic(code, message):
    return message if message.startswith("Definition ") or re.match(r"[A-Z][A-Za-z]+(: |\()", message) else f"{code}: {message}"


def error_verdict(code, message, generator=None):
    """`code` is the implementation's own code, or None for a Lean error text (classified by
    `checker_error`, the Lean backend's reading of it)."""
    if code is None:
        from ve.backends.diagnostics import checker_error
        code, actual = "rejected", checker_error(message).code
    else:
        actual = code
    text = diagnostic(code, message)
    if text.startswith("InvalidModel"):
        code = "InvalidModel"
    else:
        head = text.split(":", 1)[0]
        code = head if head in KNOWN else code if code in KNOWN else "rejected"
    out = {"status": "error", "code": code, "diagnostic_code": actual, "error": text}
    if generator is not None:
        out["generator"] = generator
    return out


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
        # The envelope is decoded and gated before anything else (the route contract, `runCase`).
        env = Environment(case["environment"])
        if kind == "label":
            validate_label(case["label"])
            return {"status": "ok", "label": parse_label(case["label"]).render()}
        if kind == "dependency-order":
            return {"status": "ok", "order": list(dependency_order_nodes(case["nodes"]))}
        if kind == "admission":
            return {"status": "ok", **admit_document(env, case["document"])}
        if kind == "background":
            from ve.ast import _to_data
            items = background(env)
            return {"status": "ok", "background": [_to_data(p.formula) for p in items],
                    "generators": [p.generator for p in items]}
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
    if kind == "background":
        return None
    if kind == "evaluate":
        return {**base, "model": case["model"], "ast": case["ast"]}
    if kind == "admission" or (order and kind != "countermodel"):
        return None
    if kind == "countermodel":
        return {**base, **({"kind": kind} if order else {}), "model": case["model"],
                "premises": case["premises"], "conclusion": case["conclusion"]}
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
        message = error["message"]
        generator = ("literals" if message.startswith("literals:") or message.endswith("(literals)")
                     else "flags" if message.startswith("flags:") or message.endswith("(flags)")
                     else None)
        suffix = re.search(r"\((literals|definitions|flags|profile)\)$", error["message"])
        generator = generator or (suffix[1] if suffix else None)
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
        verdict = error_verdict(None, result["error"], result.get("generator"))
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
    """The rows of a batch runner (`ve_conformance route -`, `ve conformance`), one per case."""
    completed = subprocess.run(command, input=json.dumps(cases), text=True, capture_output=True,
                               timeout=HANG_TIMEOUT)
    assert completed.returncode in (0, 1), completed.stderr
    results = json.loads(completed.stdout)
    assert len(results) == len(cases)
    return results
