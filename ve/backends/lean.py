"""One-shot Lean runner calls with operational failures kept out of verdicts.

`run` returns one result row per submitted case. A row with `status: error` is
Lean's own rejection of that case, a semantic outcome the caller interprets.
Everything else that prevents a well-formed answer (the binary is missing or
cannot start, a timeout, a signal or unexpected exit status, output that is not
one JSON row per case, a row that does not match the response schema, or an
exit status inconsistent with the rows) raises `CheckerUnavailable`. No Python
result is ever substituted, and a malformed row is never read as a rejection.

The response schema every runner row satisfies: `status` is `ok` or `error`;
an `error` row carries a string `error`, names its case by exactly one of `id`
and `case_index`, and has no member but those of `ERROR_EXTRAS`; an `ok` row
carries the submitted case `id`; an `id` or `case_index` present on any row
names that case, with its JSON type (a string id, an integer index: `false` is
not case 0). The per-route transports (`route_rows`) check the same rows. Each
binding's manifest `response` gives every field an `ok` row of the operation
must carry with its type (`bool`, `nat`, `string`, `object`, `json`, or
`array<T>` with every element of type `T`), and its `counts` the fields whose
size (an array's length, a `nat`'s value) must equal the length of a case
array (`case.NAME`) or of another response array (`row.NAME`). Nothing reads
an `ok` row that fails its schema.
"""
from __future__ import annotations

import subprocess
import json
import sys
from pathlib import Path

from ..assurance import require_lean_binding, require_lean_call_site
from ..errors import CheckerUnavailable, VEError
from ..wire import canonical_json, loads_json
from .lean_service import _decode_json


def run_soft_case(executable, case):
    """Transport one soft route case through the shared Lean process boundary (`route_rows`).

    Lean's error row raises its message (and code) as a `VEError`; a route that cannot answer this
    case is `CheckerUnavailable`."""
    row = route_rows(executable, [case], timeout=120,
                     payload=json.dumps([case], ensure_ascii=False).encode())[0]
    if row["status"] == "error":
        error = VEError(row["error"])
        error.code = row.get("code", error.code)
        raise error
    return row


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


# The members an error row of a Lean runner may carry besides its identity, `status` and `error`
# (`runCaseReported` in VE/*/Run.lean, VE/Route/Run.lean, VE/CertificateWire.lean, VE/Order/*.lean,
# VE/Time/Wire.lean; `caseError` in VE/Service/Protocol.lean): the soft route's `code`, the route's
# `generator` of an `InvalidModel(g)` message, and `valid: false` on certificate and order cases.
ERROR_EXTRAS = {
    "code": _SCALARS["string"],
    "generator": _SCALARS["string"],
    "valid": lambda value: value is False,
}


def error_row_problem(case: dict, row: dict, index: int) -> str | None:
    """Why the error row `row` is not Lean's rejection of `case`, submitted at `index`, or None.

    A Lean runner writes an error row in one of two shapes: `runCaseReported` echoes the case's
    `id` (JSON null when the case has none), and `main` names a case its JSON reader rejected on its
    own (JSON depth) by `case_index`. A row naming neither, both, or another case, or carrying a
    member no runner writes, rejects nothing: it is not Lean's answer to this request."""
    if type(row.get("error")) is not str:
        return "an error row has no error message"
    if ("id" in row) == ("case_index" in row):
        return "an error row does not name its case by exactly one of id and case_index"
    if "id" in row and not _same(row["id"], case.get("id")):
        return "result ids do not match the submitted cases"
    if "case_index" in row and not _same(row["case_index"], index):
        return "result case indices do not match the submitted cases"
    for name in row.keys() - {"id", "case_index", "status", "error"}:
        if name not in ERROR_EXTRAS or not ERROR_EXTRAS[name](row[name]):
            return f"an error row has an unexpected {name!r}"
    return None


def row_problem(case: dict, row, index: int, response: dict, counts: dict | None = None) -> str | None:
    """Why `row` is not a well-formed answer to `case`, or None.

    `response` and `counts` are the binding's manifest schema for `ok` rows.
    """
    if type(row) is not dict:
        return "a result row is not an object"
    status = row.get("status")
    if type(status) is not str or status not in ("ok", "error"):
        return "a result row has no status ok or error"
    if status == "error":
        return error_row_problem(case, row, index)
    # Identity fields are compared with their types: Python's `False == 0` is not
    # a JSON equality, so a Boolean never names case 0 (nor a float case 1).
    if "case_index" in row and not _same(row["case_index"], index):
        return "result case indices do not match the submitted cases"
    if "id" in row and not _same(row["id"], case.get("id")):
        return "result ids do not match the submitted cases"
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
        timeout: float) -> list[dict]:
    """Submit `cases` to the Lean `runner` executable at path `executable`.

    Every `ok` row must satisfy the binding's declared `response` types and
    `counts`; a row that does not is `CheckerUnavailable`.
    """
    kinds = {case["kind"] for case in cases if type(case.get("kind")) is str}
    binding = require_lean_binding(operation, runner, mode, kinds)
    require_lean_call_site(operation, sys._getframe(1))

    def unavailable(message):
        return CheckerUnavailable(f"Lean {runner}: {message}", operation=operation, backend="lean")

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


def route_answer(route: str, cases: list[dict], returncode: int, stdout: bytes, stderr: bytes = b"") -> list[dict]:
    """The rows of a one-shot route's answer to `cases`, each bound to its case, or `CheckerUnavailable`.

    The one check of every route transport below: the exit status is 0 or 1; stdout is UTF-8 JSON
    (`_decode_json`: no repeated member, no non-JSON number, nesting within the runtime limit); it
    holds one object per case; every row, an error row included, satisfies `row_problem` (an `ok`
    row names its case's `id`, an error row is Lean's encoder shape naming its case); and the exit
    status is 1 exactly when some row is an error. The content of an `ok` row is the caller's to
    check. Nothing here raises anything but `CheckerUnavailable`."""
    def invalid(problem):
        return CheckerUnavailable(f"CheckerUnavailable: {route} returned an invalid response: {problem}")

    if returncode not in (0, 1):
        detail = stderr.decode("utf-8", "replace").strip()[-300:]
        raise CheckerUnavailable(f"CheckerUnavailable: {route} failed" + (f" ({detail})" if detail else ""))
    try:
        rows = _decode_json(stdout)
    except ValueError as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: {route} returned invalid JSON") from exc
    if type(rows) is not list or len(rows) != len(cases):
        raise invalid("not one result object per case")
    for index, (case, row) in enumerate(zip(cases, rows)):
        problem = row_problem(case, row, index, {})
        if problem:
            raise invalid(problem)
    if (returncode == 1) != any(row["status"] == "error" for row in rows):
        raise invalid("exit status disagrees with its rows")
    return rows


def route_rows(executable, cases: list[dict], *, timeout: float, payload: bytes | None = None) -> list[dict]:
    """Submit `cases` (as `payload`, canonical JSON by default) to the one-shot Lean route at path
    `executable` and return `route_answer`'s rows. A route that cannot start or does not answer
    in time is `CheckerUnavailable`. The output is read as bytes: decoding is the reader's, inside
    the containment, never `subprocess`'s."""
    route = Path(str(executable)).name
    try:
        proc = subprocess.run([str(executable), "-"], input=canonical_json(cases) if payload is None else payload,
                              capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: {route} is unavailable") from exc
    return route_answer(route, cases, proc.returncode, proc.stdout, proc.stderr)


def run_alternatives_case(executable, case: dict, *, timeout: float) -> dict:
    """Transport a raw alternatives (or risk) case to its dedicated Lean runner."""
    return route_rows(executable, [case], timeout=timeout)[0]


def run_discourse_case(executable, case: dict, *, timeout: float) -> dict:
    """Transport one discourse case to `ve_discourse_route` (`route_rows`); the caller
    (`ve/discourse.py` `lean_admission`) checks the content of an `ok` row."""
    return route_rows(executable, [case], timeout=timeout,
                      payload=json.dumps([case], ensure_ascii=False).encode())[0]


def run_reports_case(executable, case: dict, *, timeout: float) -> dict:
    """Transport one reports case through the shared Lean process boundary."""
    return route_rows(executable, [case], timeout=timeout)[0]


def run_norm_defaults_cases(executable, cases: list[dict], *, timeout: float = 120) -> list[dict]:
    """Transport cases to `ve_norm_defaults_route`: one row per case, in order. A row with
    `status: error` is Lean's rejection of that case; anything else that is not an answer bound to
    the request is `CheckerUnavailable` (`route_rows`)."""
    return route_rows(executable, cases, timeout=timeout, payload=json.dumps(cases, ensure_ascii=False).encode())


def run_readings_cases(executable, cases: list[dict], *, timeout: float = 120) -> list[dict]:
    """Transport cases to `ve_readings_route` (composition-s1.md 8.4): one row per case, in order.

    A row with `status: error` is Lean's rejection of that case. A route that cannot start, does
    not answer in time, or answers anything but rows bound to the request with a consistent exit
    status (`route_rows`) is `CheckerUnavailable`, never a rejection."""
    return route_rows(executable, cases, timeout=timeout, payload=json.dumps(cases, ensure_ascii=False).encode())
