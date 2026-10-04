"""One-shot Lean runner calls with operational failures kept out of verdicts.

`run` returns one result row per submitted case. A row with `status: error` is
Lean's own rejection of that case, a semantic outcome the caller interprets.
Everything else that prevents a well-formed answer (the binary is missing or
cannot start, a timeout, a signal or unexpected exit status, output that is not
one JSON row per case, a row that does not match the response schema, or an
exit status inconsistent with the rows) raises `CheckerUnavailable`. No Python
result is ever substituted, and a malformed row is never read as a rejection.

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
import json
import sys

from ..assurance import require_lean_binding, require_lean_call_site
from ..errors import CheckerUnavailable, VEError
from ..wire import canonical_json, loads_json
from .lean_service import _decode_json


def run_soft_case(executable, case):
    """Transport one soft route case through the shared Lean process boundary."""
    try:
        completed = subprocess.run(
            [str(executable), "-"], input=json.dumps([case], ensure_ascii=False),
            text=True, capture_output=True, timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VEError(f"soft route unavailable: {exc}") from exc
    try:
        rows = _decode_json(completed.stdout)
        if type(rows) is not list or len(rows) != 1 or type(rows[0]) is not dict:
            raise ValueError("invalid result shape")
    except ValueError as exc:
        raise VEError(f"soft route returned invalid JSON: {completed.stderr.strip()}") from exc
    row = rows[0]
    if row.get("status") == "error":
        problem = soft_error_problem(row)
        if problem:
            raise CheckerUnavailable(f"Lean soft route: {problem}", operation="soft-route", backend="lean")
        error = VEError(row.get("error", "soft route rejected input"))
        error.code = row.get("code", error.code)
        raise error
    if completed.returncode != 0 or row.get("status") != "ok":
        raise VEError(f"soft route failed: {completed.stderr.strip()}")
    return row


def soft_error_problem(row: dict) -> str | None:
    """Why a soft route error row is not a rejection, or None: its message is text, and so is the code it
    names, when it names one (`SoftNorms/Run.lean` `runCaseReported`). Without a code, the rejection keeps
    VEError's. Which codes the route may name is the soft-norms@0 contract's table, a diagnostic module
    that stays off this verdict path (tests/test_softnorms_contract.py); tools/difffuzz.py checks it. A row
    that names its case by position (`case_index`) is the error of a case the route could not read: the
    route never ran it, so the row names no code."""
    if "error" in row and type(row["error"]) is not str:
        return "an error row's message is not text"
    if "id" not in row and "code" in row:
        return "a row for a case the route could not read names a code"
    if "code" in row and (type(row["code"]) is not str or not row["code"]):
        return "an error row's code is not text"
    return None


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


def run_alternatives_case(executable, case: dict, *, timeout: float) -> dict:
    """Transport a raw alternatives case to its dedicated Lean runner."""
    try:
        proc = subprocess.run([str(executable), "-"], input=canonical_json([case]),
                              capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckerUnavailable("ve_alternatives_route is unavailable") from exc
    if proc.returncode not in (0, 1):
        raise CheckerUnavailable("ve_alternatives_route failed")
    try:
        rows = loads_json(proc.stdout)
    except VEError as exc:
        raise CheckerUnavailable("ve_alternatives_route returned invalid JSON") from exc
    if (type(rows) is not list or len(rows) != 1 or type(rows[0]) is not dict
            or not _same(rows[0].get("id"), case.get("id"))
            or rows[0].get("status") not in ("ok", "error")
            or (rows[0]["status"] == "error" and type(rows[0].get("error")) is not str)
            or (proc.returncode == 1) != (rows[0]["status"] == "error")):
        raise CheckerUnavailable("ve_alternatives_route returned an invalid response")
    return rows[0]


def run_discourse_case(executable, case: dict, *, timeout: float):
    """Transport one discourse case to `ve_discourse_route`: its exit status, stdout and stderr
    bytes. The caller (`ve/discourse.py` `lean_admission`) checks the answer; a route that cannot
    start or does not answer in time is `CheckerUnavailable`."""
    try:
        proc = subprocess.run([str(executable), "-"], input=json.dumps([case], ensure_ascii=False).encode(),
                              capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: the Lean discourse route did not answer ({exc})") from None
    return proc.returncode, proc.stdout, proc.stderr


def run_reports_case(executable, case: dict, *, timeout: float) -> dict:
    """Transport one reports case through the shared Lean process boundary."""
    try:
        proc = subprocess.run([str(executable), "-"], input=canonical_json([case]),
                              capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckerUnavailable("ve_reports_route is unavailable") from exc
    if proc.returncode not in (0, 1):
        raise CheckerUnavailable("ve_reports_route failed")
    try:
        rows = loads_json(proc.stdout)
    except VEError as exc:
        raise CheckerUnavailable("ve_reports_route returned invalid JSON") from exc
    if (type(rows) is not list or len(rows) != 1 or type(rows[0]) is not dict
            or not _same(rows[0].get("id"), case.get("id"))
            or rows[0].get("status") not in ("ok", "error")
            or (rows[0]["status"] == "error" and type(rows[0].get("error")) is not str)
            or (proc.returncode == 1) != (rows[0]["status"] == "error")):
        raise CheckerUnavailable("ve_reports_route returned an invalid response")
    return rows[0]


def run_norm_defaults_cases(executable, cases: list[dict], *, timeout: float = 120) -> list[dict]:
    """Transport cases to `ve_norm_defaults_route`: one row per case, in order. A row with
    `status: error` is Lean's rejection of that case; a route that cannot start, does not
    answer in time or answers with the wrong shape is `CheckerUnavailable`."""
    try:
        completed = subprocess.run([str(executable), "-"], input=json.dumps(cases, ensure_ascii=False),
                                   text=True, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckerUnavailable("ve_norm_defaults_route is unavailable") from exc
    try:
        rows = _decode_json(completed.stdout)
    except ValueError as exc:
        raise CheckerUnavailable("ve_norm_defaults_route returned invalid JSON") from exc
    if (type(rows) is not list or len(rows) != len(cases) or not all(type(r) is dict for r in rows)
            or any(r.get("status") not in ("ok", "error") for r in rows)):
        raise CheckerUnavailable("ve_norm_defaults_route returned an invalid response")
    return rows


def run_readings_cases(executable, cases: list[dict], *, timeout: float = 120) -> list[dict]:
    """Transport cases to `ve_readings_route` (composition-s1.md 8.4): one row per case, in order.

    A row with `status: error` is Lean's rejection of that case. A route that cannot start, does
    not answer in time, or answers with the wrong shape or an exit status that disagrees with its
    rows is `CheckerUnavailable`, never a rejection."""
    try:
        completed = subprocess.run([str(executable), "-"], input=json.dumps(cases, ensure_ascii=False),
                                   text=True, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckerUnavailable("ve_readings_route is unavailable") from exc
    if completed.returncode not in (0, 1):
        raise CheckerUnavailable("ve_readings_route failed")
    try:
        rows = _decode_json(completed.stdout)
    except ValueError as exc:
        raise CheckerUnavailable("ve_readings_route returned invalid JSON") from exc
    if (type(rows) is not list or len(rows) != len(cases) or not all(type(r) is dict for r in rows)
            or any(r.get("status") not in ("ok", "error") for r in rows)
            or any(r["status"] == "error" and type(r.get("error")) is not str for r in rows)
            or any(r["status"] == "ok" and not _same(r.get("id"), c.get("id")) for r, c in zip(rows, cases))
            or (completed.returncode == 1) != any(r["status"] == "error" for r in rows)):
        raise CheckerUnavailable("ve_readings_route returned an invalid response")
    return rows
