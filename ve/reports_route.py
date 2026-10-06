"""Checked reports route."""
from __future__ import annotations

from .backends.relay import decide


def _without_null(value):
    # The frozen Lean JSON parser has no null; the reports wire uses absent
    # optional fields for literal, reference_time and package content.
    if type(value) is dict:
        return {k: _without_null(v) for k, v in value.items() if v is not None}
    if type(value) is list:
        return [_without_null(v) for v in value]
    return value


def run_case(kind, environment, document, **extra):
    """Lean's reports route row (service mode `reports`); a rejection raises Lean's diagnostic."""
    case = _without_null({"id": "document", "kind": kind,
                          "environment": environment, "document": document, **extra})
    return decide("reports", [case])[0]
