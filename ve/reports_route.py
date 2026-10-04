"""Checked reports route and independent Python/Lean elaboration comparison."""
from __future__ import annotations

from .backends.relay import decide
from .errors import VEError
FIELDS = ("environment_reports_id", "keys", "premises", "open_terms",
          "bridge_formulas", "content_ids", "envelope", "warnings")


def _without_null(value):
    # The frozen Lean JSON parser has no null; the reports wire uses absent
    # optional fields for literal, reference_time and package content.
    if type(value) is dict:
        return {k: _without_null(v) for k, v in value.items() if v is not None}
    if type(value) is list:
        return [_without_null(v) for v in value]
    return value


def run_case(kind, environment, document):
    """Lean's reports route row (service mode `reports`); a rejection raises Lean's diagnostic."""
    case = _without_null({"id": "document", "kind": kind,
                          "environment": environment, "document": document})
    return decide("reports", [case])[0]


def checked_elaboration(reports, environment, document):
    result = run_case("reports-elaborate", environment, document)
    python = reports.elaborated()
    for field in FIELDS:
        if python[field] != result.get(field):
            raise VEError(f"ReportsConformance: Python and Lean differ at {field}")
    return result
