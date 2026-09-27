"""Python entry point for the proved soft-norm admission route."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

from .ast import formula_to_data
from .errors import VEError
from .softnorms import SoftEnvironment, SoftNormDocument

LEAN_ROUTE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_soft_norms_route"


def _run(case):
    try:
        completed = subprocess.run(
            [str(LEAN_ROUTE), "-"], input=json.dumps([case], ensure_ascii=False),
            text=True, capture_output=True, timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VEError(f"soft route unavailable: {exc}") from exc
    try:
        rows = json.loads(completed.stdout)
        if type(rows) is not list or len(rows) != 1 or type(rows[0]) is not dict:
            raise ValueError("invalid result shape")
    except ValueError as exc:
        raise VEError(f"soft route returned invalid JSON: {completed.stderr.strip()}") from exc
    row = rows[0]
    if row.get("status") == "error":
        raise VEError(row.get("error", "soft route rejected input"))
    if completed.returncode != 0 or row.get("status") != "ok":
        raise VEError(f"soft route failed: {completed.stderr.strip()}")
    return row


def admit_soft_document(environment, document, *, soft_document=None):
    """Check Python regeneration, then return Lean's admission verdict.

    Both calls use the original source environment and norm objects. Lean
    independently regenerates E′ and T′; no Python-generated premise is sent
    as an authority for admission.
    """
    env = environment if isinstance(environment, SoftEnvironment) else SoftEnvironment(environment)
    if soft_document is None:
        active = [u["content"] for u in document["units"]
                  if u["kind"] == "norm" and type(u.get("content")) is dict
                  and "norm" in u["content"]]
        soft_document = SoftNormDocument(env, active)
    norms = [rule.to_dict() for rule in soft_document.rules]
    elaborated = _run({"id": "soft-elaborate", "kind": "soft-elaborate",
                       "environment": env.to_dict(), "norms": norms})
    if soft_document.extended_env.to_dict() != elaborated["environment_prime"]:
        raise VEError("soft route regeneration mismatch: extended environment")
    decisions = {item["name"] for item in elaborated["decisions"]}
    if decisions != soft_document.extended_env.decision_names:
        raise VEError("soft route regeneration mismatch: decision predicates")
    py_layers = {label: formula_to_data(soft_document.extended_env, formula, _generated=True)
                 for label, formula in soft_document.elaborated.premises()}
    lean_layers = {item["label"]: item["ast"] for item in elaborated["premises"]}
    if py_layers != lean_layers:
        raise VEError("soft route regeneration mismatch: norm layers")
    py_soft = [(label, formula_to_data(soft_document.extended_env, formula, _generated=True))
               for label, formula in soft_document.extended_env.soft_premises]
    lean_soft = [(item["label"], item["ast"]) for item in elaborated["background"]
                 if item.get("generator") == "soft"]
    if py_soft != lean_soft:
        raise VEError("soft route regeneration mismatch: soft background")
    # The restricted Lean JSON input has no null literal. The wire's null
    # inherited-decider spelling is canonicalized to the equivalent omission.
    normalized_units = []
    for unit in document["units"]:
        content = unit.get("content")
        if type(content) is dict and "norm" in content:
            raw = content["norm"]
            if type(raw.get("exception")) is dict:
                exception = {k: v for k, v in raw["exception"].items()
                             if k != "decided_by" or v is not None}
                unit = {**unit, "content": {"norm": {**raw, "exception": exception}}}
        normalized_units.append(unit)
    document = {**document, "units": normalized_units}
    row = _run({"id": "admission", "kind": "admission", "environment": env.to_dict(),
                "document": document})
    return {key: value for key, value in row.items() if key not in ("id", "status")}
