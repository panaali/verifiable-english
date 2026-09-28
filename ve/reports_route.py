"""Checked reports route and independent Python/Lean elaboration comparison."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

from .errors import UnsupportedProfile, VEError

EXECUTABLE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_reports_route"
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
    if not EXECUTABLE.is_file():
        raise UnsupportedProfile("reports@0 needs the built ve_reports_route executable")
    case = _without_null({"id": "document", "kind": kind,
                          "environment": environment, "document": document})
    try:
        proc = subprocess.run([str(EXECUTABLE), "-"], input=json.dumps([case], ensure_ascii=False),
                              capture_output=True, text=True, timeout=60, check=False)
        [result] = json.loads(proc.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        raise VEError("reports Lean route failed") from exc
    if result.get("status") != "ok":
        raise VEError(result.get("error", proc.stderr or "reports Lean route rejected document"))
    return result


def checked_elaboration(reports, environment, document):
    result = run_case("reports-elaborate", environment, document)
    python = reports.elaborated()
    for field in FIELDS:
        if python[field] != result.get(field):
            raise VEError(f"ReportsConformance: Python and Lean differ at {field}")
    return result
