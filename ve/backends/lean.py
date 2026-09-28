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
case `id`; an `id` or `case_index` present on any row names that case. Each
caller adds the fields its interpretation reads from an `ok` row (`fields`).
"""
from __future__ import annotations

import subprocess
import sys

from ..assurance import require_lean_binding, require_lean_call_site
from ..errors import CheckerUnavailable, VEError
from ..wire import canonical_json, loads_json


def _has_type(value, expected) -> bool:
    # bool is not an int here, and an int is not a bool.
    types = expected if type(expected) is tuple else (expected,)
    return any(type(value) is t for t in types)


def row_problem(case: dict, row, index: int, fields: dict) -> str | None:
    """Why `row` is not a well-formed answer to `case`, or None."""
    if type(row) is not dict:
        return "a result row is not an object"
    status = row.get("status")
    if status not in ("ok", "error"):
        return "a result row has no status ok or error"
    if "case_index" in row and row["case_index"] != index:
        return "result case indices do not match the submitted cases"
    if "id" in row and row["id"] != case.get("id"):
        return "result ids do not match the submitted cases"
    if status == "error":
        return None if type(row.get("error")) is str else "an error row has no error message"
    if "id" in case and row.get("id") != case["id"]:
        return "an ok row does not name its case id"
    for name, expected in fields.items():
        if name not in row or not _has_type(row[name], expected):
            return f"an ok row has no well-formed {name!r}"
    return None


def run(operation: str, executable, cases: list[dict], *, runner: str, mode: str = "",
        timeout: float, fields: dict | None = None) -> list[dict]:
    """Submit `cases` to the Lean `runner` executable at path `executable`.

    `fields` maps each field the caller reads from an `ok` row to its type
    (or a tuple of types); a missing or ill-typed field is `CheckerUnavailable`.
    """
    kinds = {case["kind"] for case in cases if type(case.get("kind")) is str}
    require_lean_binding(operation, runner, mode, kinds)
    require_lean_call_site(operation, sys._getframe(1))
    fields = dict(fields or {})

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
        problem = row_problem(case, row, index, fields)
        if problem:
            raise unavailable(problem)
    rejected = any(row["status"] == "error" for row in rows)
    if rejected != (proc.returncode == 1):
        raise unavailable("exit status disagrees with its result rows")
    return rows
