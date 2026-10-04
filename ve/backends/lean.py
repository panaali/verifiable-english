"""Manifest-bound Lean calls with operational failures kept out of verdicts.

`run` returns one result row per submitted case for an operation the assurance manifest
binds to a runner (`lean.bindings`). A binding to `ve_service` goes through the persistent
service (`relay.decide`): a rejection raises Lean's diagnostic with Lean's code, and the rows
returned are Lean's answers. A binding to the one-shot `ve_conformance` runs that executable,
and a row with `status: error` is Lean's own rejection of that case, a semantic outcome the
caller interprets. Everything else that prevents a well-formed answer (the binary is missing or
cannot start, a timeout, a signal or unexpected exit status, output that is not one JSON row per
case, a row that does not match the response schema, or an exit status inconsistent with the
rows) raises `CheckerUnavailable`. No Python result is ever substituted, and a malformed row is
never read as a rejection.

The response schema every runner row satisfies: `status` is `ok` or `error`;
an `error` row carries a string `error`; an `ok` row carries the submitted
case `id`; an `id` or `case_index` present on any row names that case, with its
JSON type (a string id, an integer index: `false` is not case 0). Each
binding's manifest `response` gives every field an `ok` row of the operation
must carry with its type (`bool`, `nat`, `string`, `object`, `json`, or
`array<T>` with every element of type `T`), and its `counts` the fields whose
size (an array's length, a `nat`'s value) must equal the length of a case
array (`case.NAME`) or of another response array (`row.NAME`). Nothing reads
an `ok` row that fails its schema.
"""
from __future__ import annotations

import subprocess
import sys

from ..assurance import require_lean_binding, require_lean_call_site
from ..errors import CheckerUnavailable, VEError
from ..wire import canonical_json, loads_json


_SCALARS = {
    "bool": lambda value: type(value) is bool,
    # bool is not an int here.
    "nat": lambda value: type(value) is int and value >= 0,
    "string": lambda value: type(value) is str,
    "object": lambda value: type(value) is dict,
    # Any JSON value; the caller compares its content.
    "json": lambda value: True,
}


def valid_type(spec) -> bool:
    """Whether `spec` is a response type of the manifest schema."""
    if type(spec) is not str:
        return False
    if spec.startswith("array<") and spec.endswith(">"):
        return valid_type(spec[len("array<"):-1])
    return spec in _SCALARS


def conforms(value, spec: str) -> bool:
    """Whether `value` has the response type `spec`."""
    if spec.startswith("array<"):
        element = spec[len("array<"):-1]
        return type(value) is list and all(conforms(item, element) for item in value)
    return _SCALARS[spec](value)


def _size(value) -> int:
    return value if type(value) is int else len(value)


def _same(value, expected) -> bool:
    """JSON equality with types kept apart: `false` is not `0`, `1.0` is not `1`."""
    if type(value) is not type(expected):
        return False
    if type(value) is list:
        return len(value) == len(expected) and all(map(_same, value, expected))
    if type(value) is dict:
        return value.keys() == expected.keys() and all(_same(value[k], expected[k]) for k in value)
    return value == expected


def row_problem(case: dict, row, index: int, response: dict, counts: dict | None = None) -> str | None:
    """Why `row` is not a well-formed answer to `case`, or None.

    `response` and `counts` are the binding's manifest schema for `ok` rows.
    """
    if type(row) is not dict:
        return "a result row is not an object"
    status = row.get("status")
    if status not in ("ok", "error"):
        return "a result row has no status ok or error"
    # Identity fields are compared with their types: Python's `False == 0` is not
    # a JSON equality, so a Boolean never names case 0 (nor a float case 1).
    if "case_index" in row and not _same(row["case_index"], index):
        return "result case indices do not match the submitted cases"
    if "id" in row and not _same(row["id"], case.get("id")):
        return "result ids do not match the submitted cases"
    if status == "error":
        return None if type(row.get("error")) is str else "an error row has no error message"
    if "id" in case and not _same(row.get("id"), case["id"]):
        return "an ok row does not name its case id"
    for name, spec in response.items():
        if name not in row or not conforms(row[name], spec):
            return f"an ok row has no well-formed {name!r} ({spec})"
    for name, reference in (counts or {}).items():
        source, _, field = reference.partition(".")
        counted = (case if source == "case" else row).get(field)
        if type(counted) is not list or _size(row[name]) != len(counted):
            return f"an ok row's {name!r} does not count {reference}"
    return None


def run(operation: str, executable, cases: list[dict], *, runner: str, mode: str = "",
        timeout: float | None = None) -> list[dict]:
    """Submit `cases` to the Lean `runner` executable at path `executable`.

    Every `ok` row must satisfy the binding's declared `response` types and
    `counts`; a row that does not is `CheckerUnavailable`. For `ve_service` the
    service mode is `mode`, `timeout` (if any) replaces its deadline, and a
    rejection raises Lean's diagnostic.
    """
    kinds = {case["kind"] for case in cases if type(case.get("kind")) is str}
    binding = require_lean_binding(operation, runner, mode, kinds)
    require_lean_call_site(operation, sys._getframe(1))

    def unavailable(message):
        return CheckerUnavailable(f"Lean {runner}: {message}", operation=operation, backend="lean")

    if runner == "ve_service":
        from .relay import decide
        rows = decide(mode, cases, timeout=timeout, executable=executable)
        for index, (case, row) in enumerate(zip(cases, rows, strict=True)):
            problem = row_problem(case, row, index, binding["response"], binding.get("counts"))
            if problem:
                raise unavailable(problem)
        return rows
    if timeout is None:
        raise TypeError(f"a one-shot {runner} call needs a timeout")
    try:
        proc = subprocess.run([str(executable), *([mode] if mode else [])], input=canonical_json(cases),
                              capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise unavailable(f"no answer within {timeout} s") from None
    except OSError as exc:
        raise unavailable(f"cannot start {executable}: {exc.strerror or exc}") from None
    # The one-shot runners exit 0 (every case ok) or 1 (some case rejected);
    # 2 is a usage or JSON framing error, and anything else is a crash.
    if proc.returncode not in (0, 1):
        raise unavailable(f"exited with status {proc.returncode}")
    try:
        rows = loads_json(proc.stdout)
    except VEError:
        raise unavailable("output is not a JSON result array") from None
    if type(rows) is not list or len(rows) != len(cases):
        raise unavailable("output does not hold one result object per case")
    for index, (case, row) in enumerate(zip(cases, rows)):
        problem = row_problem(case, row, index, binding["response"], binding.get("counts"))
        if problem:
            raise unavailable(problem)
    rejected = any(row["status"] == "error" for row in rows)
    if rejected != (proc.returncode == 1):
        raise unavailable("exit status disagrees with its result rows")
    return rows
