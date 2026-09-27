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


def _regex_issue(pattern: str) -> str | None:
    """Keep regex@1 in a deterministic fragment with bounded backtracking.

    A single repetition of one atom is linear in the input length. Grouped
    repetition, alternation with repetition, and lookaround are excluded.
    """
    repetitions, alternate, grouped_repeat = 0, False, False
    in_class, escaped, previous = False, False, ""
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if escaped:
            if char.isdigit():
                return "regex backreferences are outside the bounded stage-1 fragment"
            escaped = False
            previous = "atom"
        elif char == "\\":
            escaped = True
        elif in_class:
            if char == "]":
                in_class = False
                previous = "atom"
        elif char == "[":
            in_class = True
        elif char == "(" and pattern[i:i + 2] == "(" + "?":
            return "regex lookaround and special groups are outside the bounded stage-1 fragment"
        elif char == "|":
            alternate = True
            previous = ""
        elif char in "*+?":
            repetitions += 1
            grouped_repeat |= previous == ")"
            previous = "quantifier"
        elif char == "{":
            match = re.match(r"\{(\d+)(?:,(\d*))?\}", pattern[i:])
            if match:
                repetitions += 1
                grouped_repeat |= previous == ")"
                upper = match[2] or match[1]
                if int(upper) > MAX_TEXT:
                    return "regex repetition exceeds the bounded stage-1 limit"
                i += len(match[0]) - 1
                previous = "quantifier"
            else:
                previous = "atom"
        else:
            previous = ")" if char == ")" else "atom"
        i += 1
    if grouped_repeat or repetitions > 1 or (alternate and repetitions):
        return "regex pattern is outside the bounded stage-1 fragment"
    return None


def _calculate(function, pattern, value, compiled=None):
    try:
        if function == "prefix@1":
            return {"input": value, "status": "ok", "value": value.startswith(pattern)}
        if function == "glob@1":
            return {"input": value, "status": "ok", "value": fnmatch.fnmatchcase(value, pattern)}
        return {"input": value, "status": "ok", "value": compiled.fullmatch(value) is not None}
    except re.error as exc:
        return {"input": value, "status": "error", "error": "invalid regex: " + str(exc)}


def run(function: str, parameters: dict, domain: list[str]) -> dict:
    """Generate a total table over the caller's explicitly listed domain."""
    pattern = _request(function, parameters, domain)
    issue = _regex_issue(pattern) if function == "regex@1" else None
    compiled = None
    if function == "regex@1" and issue is None:
        try:
            compiled = re.compile(pattern)
        except re.error as exc:
            issue = "invalid regex: " + str(exc)
    rows = ([{"input": value, "status": "error", "error": issue} for value in domain]
            if issue else [_calculate(function, pattern, value, compiled) for value in domain])
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
    if record["implementation"] != expected["implementation"]:
        raise VEError("Adapter Python version does not match the recorded implementation")
    if record["implementation_hash"] != expected["implementation_hash"]:
        raise VEError("Adapter implementation hash does not match the running code")
    if record != expected:
        raise VEError("Adapter record does not match recomputed inputs and output table")
    return expected


def _lookup_verified(checked: dict, value: str) -> bool:
    """Internal lookup after exactly one full record verification."""
    try:
        index = checked["domain"].index(value)
    except ValueError as exc:
        raise VEError("Adapter input is outside the recorded domain") from exc
    row = checked["rows"][index]
    if row["status"] == "error":
        raise VEError(row["error"])
    return row["value"]


def lookup(record: dict | None, value: str) -> bool | None:
    """Return UNKNOWN without a table; reject values outside a verified domain."""
    if record is None:
        return None
    return _lookup_verified(verify(record), value)
