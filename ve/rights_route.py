"""Replay rights reporting through the Lean rights route on source units."""
from __future__ import annotations

from pathlib import Path

from .backends.lean import run_soft_case
from .errors import VEError

LEAN_ROUTE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_rights_route"


def _wire(value):
    # The restricted Lean JSON input represents optional null fields by omission.
    if type(value) is dict:
        return {key: _wire(item) for key, item in value.items() if item is not None}
    if type(value) is list:
        return [_wire(item) for item in value]
    return value


def run_rights_case(environment, units, kind, **extra):
    case = {"id": kind, "kind": kind, "environment": _wire(environment.to_dict()),
            "document": _wire(units), **extra}
    return run_soft_case(LEAN_ROUTE, case)


def report_rights(environment, units, rights):
    """Return the checked five-question rows available without submitted certificates."""
    elaborated = run_rights_case(environment, units, "rights-elaborate")
    expected = (set(rights.limitation_names.values()) |
                set(rights.condition_names.values()) |
                (set(rights.bar_names.values()) if rights.bar is not None else set()))
    actual = {item["name"] for item in elaborated["generated"]}
    if actual != expected:
        raise VEError("rights route regeneration mismatch: generated predicates")
    labels = [item["label"] for item in elaborated["limitations"]]
    if labels != [label for label, _ in rights.limitation_premises]:
        raise VEError("rights route regeneration mismatch: limitation premises")
    scope = run_rights_case(environment, units, "rights-scope", certificates={})
    bar = run_rights_case(environment, units, "rights-bar", certificates={})
    conflict = run_rights_case(environment, units, "rights-conflict", packages={})
    return {
        "conflict": {key: conflict[key] for key in ("verdict", "status_text", "targets", "conditional_on")},
        "narrowings": scope["narrowings"],
        "unlicensed_limitations": scope["findings"],
        "distinction": elaborated["distinction"],
        "distinction_hits": elaborated["findings"],
        "bar": bar["bars"],
        "limitation_premises_used": conflict["conditional_on"],
        "decider_note": "No claim is made about the deciders of open terms.",
    }
