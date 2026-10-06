"""Relay rights decisions and reports from the Lean rights route."""
from __future__ import annotations

from .backends.relay import decide

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
    return decide("rights", [case])[0]


def expected_environment_prime(rights):
    """The full environment identity preimage supplied by the Lean owner."""
    return rights.elaborated["environment_prime"]


def report_rights(environment, units, rights=None):
    """Return the five-question rows available without submitted certificates."""
    elaborated = run_rights_case(environment, units, "rights-elaborate")
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


def admit_rights_document(environment, document, rights=None):
    """Replay W2 admission on the Lean-validated rights source."""
    source = [{"source_units": [unit["id"] for unit in document["units"]]}] + [
        unit["content"] for unit in document["units"]
        if unit.get("kind") in ("right", "right_lines", "limitation", "bar", "norm")
        and type(unit.get("content")) is dict]
    report_rights(environment, source, rights)
    case = {"id": "admission", "kind": "admission", "environment": environment.to_dict(),
            "document": document}
    row = decide("rights", [_wire(case)])[0]
    return {key: value for key, value in row.items() if key not in ("id", "status")}
