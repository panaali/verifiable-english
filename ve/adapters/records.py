"""Recomputable glob, prefix and regex tables with complete error rows.

The record is an assumption source. A verified row may be cited with its label;
the checker does not interpret the host language's string operations.
"""
from __future__ import annotations

import fnmatch
import hashlib
from pathlib import Path
import re
import sys

from ..errors import ResourceLimit, VEError
from ..wire import digest, require_fields

FUNCTIONS = frozenset(("glob@1", "prefix@1", "regex@1"))
MAX_DOMAIN = 10000
MAX_PATTERN = 256
MAX_TEXT = 4096


def _request(function, parameters, domain):
    if function not in FUNCTIONS:
        raise VEError(f"Unsupported adapter function {function!r}")
    require_fields(parameters, {"pattern"}, path="/parameters")
    pattern = parameters["pattern"]
    if type(pattern) is not str or len(pattern) > MAX_PATTERN:
        raise ResourceLimit("Adapter pattern must be a string of at most 256 characters")
    if type(domain) is not list or len(domain) > MAX_DOMAIN:
        raise ResourceLimit("Adapter domain must be a list of at most 10000 strings")
    if any(type(value) is not str or len(value) > MAX_TEXT for value in domain):
        raise VEError("Adapter domain values must be strings of at most 4096 characters")
    if len(set(domain)) != len(domain):
        raise VEError("Adapter domain contains duplicate inputs")
    return pattern


def _calculate(function, pattern, value):
    try:
        if function == "prefix@1":
            return {"input": value, "status": "ok", "value": value.startswith(pattern)}
        if function == "glob@1":
            return {"input": value, "status": "ok", "value": fnmatch.fnmatchcase(value, pattern)}
        return {"input": value, "status": "ok", "value": re.fullmatch(pattern, value) is not None}
    except re.error as exc:
        return {"input": value, "status": "error", "error": "invalid regex: " + str(exc)}


def run(function: str, parameters: dict, domain: list[str]) -> dict:
    """Generate a total table over the caller's explicitly listed domain."""
    pattern = _request(function, parameters, domain)
    rows = [_calculate(function, pattern, value) for value in domain]
    input_hashes = [digest("ve-adapter-input-v1\n", value) for value in domain]
    table_hash = digest("ve-adapter-table-v1\n", rows)
    return {"function": function, "parameters": {"pattern": pattern},
            "implementation": f"python-stdlib-{sys.version_info.major}.{sys.version_info.minor}",
            "implementation_hash": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "domain": list(domain), "input_hashes": input_hashes,
            "rows": rows, "table_hash": table_hash,
            "label": "adapter:" + function}


def verify(record: dict) -> dict:
    """Reject changed inputs, domain, rows, hashes, and unlisted functions."""
    require_fields(record, {"function", "parameters", "implementation", "implementation_hash",
                            "domain", "input_hashes",
                            "rows", "table_hash", "label"}, path="/adapter")
    expected = run(record["function"], record["parameters"], record["domain"])
    if record != expected:
        raise VEError("Adapter record does not match recomputed inputs and output table")
    return expected


def lookup(record: dict | None, value: str) -> bool | None:
    """Return UNKNOWN without a table; reject values outside a verified domain."""
    if record is None:
        return None
    checked = verify(record)
    try:
        index = checked["domain"].index(value)
    except ValueError as exc:
        raise VEError("Adapter input is outside the recorded domain") from exc
    row = checked["rows"][index]
    if row["status"] == "error":
        raise VEError(row["error"])
    return row["value"]
