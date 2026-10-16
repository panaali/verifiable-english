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

Every one-shot transport here reads the runner's output with `read_rows`, the
one row contract of every runner: `status` is `ok` or `error`; a row naming its
case by position (`case_index`) carries only that position and an `error`; any
other row has an `id` field naming the submitted case, with its JSON type (a
string id, an integer index: `false` is not case 0), and `null` for a case
without one (a row without the field names no case); an `error` row carries a non-empty string `error`
and, on a coded route only, a string `code`; an `ok` row carries neither. Output
that is no Unicode text (a `\\ud800` escape) is no answer. Each
binding's manifest `response` gives every field an `ok` row of the operation
must carry with its type (`bool`, `nat`, `string`, `object`, `json`, or
`array<T>` with every element of type `T`), and its `counts` the fields whose
size (an array's length, a `nat`'s value) must equal the length of a case
array (`case.NAME`) or of another response array (`row.NAME`). Nothing reads
an `ok` row that fails its schema.

Each caller's wall-clock timeout is a guard against a hung runner, not a work
limit: `VE_LEAN_TIMEOUT` replaces every caller's default (`configured_timeout`;
the test suite raises it to its hang guard, so machine load cannot fail a test).
"""
from __future__ import annotations

import subprocess
import sys

from ..assurance import require_lean_binding, require_lean_call_site
from ..errors import CheckerUnavailable, VEError
from ..wire import canonical_json, loads_json
from .lean_service import _decode_json, configured_seconds
from .process_limits import run_limited
# JSON equality with types kept apart: `false` is not `0`, `1.0` is not `1`.
from .service_schema import same_json as _same

SOFT_TIMEOUT = 120.0
ROUTE_TIMEOUT = 120.0
# A one-shot runner's address-space limit (`process_limits`): a runaway runner fails its own
# allocation and gives no answer (CheckerUnavailable) instead of exhausting the machine.
ADDRESS_SPACE = 8 << 30


def configured_timeout(default: float) -> float:
    """The wall-clock timeout of one one-shot Lean runner call whose caller's default is
    `default`: `VE_LEAN_TIMEOUT` when set, else `default`. A value that is not a positive
    finite number of seconds is `CheckerUnavailable` before the runner starts."""
    return configured_seconds("VE_LEAN_TIMEOUT", default)


class NoAnswer(Exception):
    """Why a one-shot runner's output is no answer to the submitted cases (`read_rows`). Each
    transport raises it as its own `CheckerUnavailable`: it is never a rejection."""


# The members an error row of a Lean runner may carry besides its identity, `status`, `error` and a coded
# route's `code` (`runCaseReported` in VE/*/Run.lean, VE/Route/Run.lean, VE/CertificateWire.lean,
# VE/Order/*.lean, VE/Time/Wire.lean; `caseError` in VE/Service/Protocol.lean): the route's `generator` of an
# `InvalidModel(g)` message, and `valid: false` on certificate and order cases.
ERROR_EXTRAS = {
    "generator": lambda value: type(value) is str,
    "valid": lambda value: value is False,
}


def identity_problem(case: dict, row, index: int, *, coded: bool = False) -> str | None:
    """Why `row` is not a result row for `case`, the `index`-th submitted case, or None.

    The row contract every one-shot runner's `main` writes (`lean/VE/*/Run.lean`): a case the
    runner could not read is answered by its position alone (`status: error`, `case_index`,
    `error` and, from the certificate and order runners, `valid: false`); every other row names the case's `id` (null when the case has none)
    and no position. An `error` row carries a non-empty string `error` and, only on a route whose rows name
    codes (`coded`), a non-empty string `code`, and no member outside `ERROR_EXTRAS`; an `ok` row carries
    neither."""
    if type(row) is not dict:
        return "a result row is not an object"
    status = row.get("status")
    if status not in ("ok", "error"):
        return "a result row has no status ok or error"
    # Identity fields are compared with their types: Python's `False == 0` is not
    # a JSON equality, so a Boolean never names case 0 (nor a float case 1).
    if "case_index" in row:
        if not _same(row["case_index"], index):
            return "result case indices do not match the submitted cases"
        # `valid: false` beside it on the certificate and order runners (`lean/Main.lean`).
        if status != "error" or row.keys() - {"valid"} != {"status", "case_index", "error"} \
                or row.get("valid", False) is not False:
            return "a row naming its case by position carries more than its position and an error"
    # The id field is required: the runners write it, `null` for a case without one
    # (`j.getObjValD "id"`), so a row that omits it names no case at all.
    elif "id" not in row or not _same(row["id"], case.get("id")):
        return "result ids do not match the submitted cases"
    if status == "error":
        # Lean's texts are never empty (`lean_service_schema/common.json` `text`, the same rows).
        if type(row.get("error")) is not str or not row["error"]:
            return "an error row has no error message"
        if "code" in row and not (coded and type(row["code"]) is str and row["code"]):
            return "an error row names a code its route does not give"
        for name in row.keys() - {"id", "case_index", "status", "error", "code"}:
            if name not in ERROR_EXTRAS or not ERROR_EXTRAS[name](row[name]):
                return f"an error row has an unexpected {name!r}"
    elif "error" in row or "code" in row:
        return "an ok row carries an error or a code"
    return None


def read_rows(returncode: int, stdout: bytes, cases: list, *, coded: bool = False,
              restricted: bool = False) -> list[dict]:
    """The result rows of a one-shot runner's answer to `cases`, or `NoAnswer`.

    The one reader of every one-shot runner's output. The runners exit 0 (every case ok) or 1
    (some case rejected); 2 is a usage or JSON framing error, and anything else is a crash.
    The output must be one JSON array (`_decode_json`, or VE's restricted JSON when
    `restricted`: no lone surrogate, duplicate field or non-finite number) of one row per case
    satisfying `identity_problem`, with an exit status that agrees with its rows."""
    if returncode not in (0, 1):
        raise NoAnswer(f"exited with status {returncode}")
    try:
        rows = loads_json(stdout) if restricted else _decode_json(stdout)
    except (VEError, ValueError, RecursionError):
        raise NoAnswer("output is not a JSON result array") from None
    if type(rows) is not list or len(rows) != len(cases):
        raise NoAnswer("output does not hold one result object per case")
    for index, (case, row) in enumerate(zip(cases, rows)):
        problem = identity_problem(case, row, index, coded=coded)
        if problem:
            raise NoAnswer(problem)
    if any(row["status"] == "error" for row in rows) != (returncode == 1):
        raise NoAnswer("exit status disagrees with its result rows")
    return rows


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


def row_problem(case: dict, row, index: int, response: dict, counts: dict | None = None, *,
                coded: bool = False) -> str | None:
    """Why `row` is not a well-formed answer to `case`, or None.

    `response` and `counts` are the binding's manifest schema for `ok` rows; `coded` is
    `identity_problem`'s (a route whose error rows name codes).
    """
    problem = identity_problem(case, row, index, coded=coded)
    if problem or row["status"] == "error":
        return problem
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
        proc = run_limited([str(executable), *([mode] if mode else [])], input=canonical_json(cases),
                           timeout=timeout, address_space=ADDRESS_SPACE)
    except subprocess.TimeoutExpired:
        raise unavailable(f"no answer within {timeout} s") from None
    except OSError as exc:
        raise unavailable(f"cannot start {executable}: {exc.strerror or exc}") from None
    try:
        rows = (read_rows(proc.returncode, proc.stdout, cases, restricted=True) if runner != "ve_metered" else
                # `ve_metered`'s rows carry JSON null (an exhausted value, an absent trace), as the
                # service's do; they are read as the service's are.
                read_rows(proc.returncode, proc.stdout, cases))
    except NoAnswer as exc:
        raise unavailable(str(exc)) from None
    for index, (case, row) in enumerate(zip(cases, rows)):
        problem = row_problem(case, row, index, binding["response"], binding.get("counts"))
        if problem:
            raise unavailable(problem)
    return rows



def run_route_cases(executable, mode: str, cases: list[dict], *, coded: bool = False,
                    timeout: float | None = None, route_name: str = "Lean route") -> list[dict]:
    """One-shot route transport; every caller shares the bound row reader."""
    if timeout is None:
        timeout = configured_timeout(ROUTE_TIMEOUT)
    try:
        proc = run_limited([str(executable), mode], input=canonical_json(cases), timeout=timeout,
                           address_space=ADDRESS_SPACE)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: {route_name} {mode} is unavailable") from exc
    try:
        return read_rows(proc.returncode, proc.stdout, cases, coded=coded, restricted=True)
    except NoAnswer as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: {route_name} {mode} returned an invalid response "
                                 f"({exc})") from None


def run_english_cases(executable, mode: str, cases: list[dict], *, timeout: float | None = None) -> list[dict]:
    """Transport English cases using the shared one-shot route reader."""
    return run_route_cases(executable, mode, cases, timeout=timeout, route_name="ve_english_route")
