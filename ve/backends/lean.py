"""One-shot Lean runner calls with operational failures kept out of verdicts.

`run` returns one result row per submitted case. A row with `status: error` is
Lean's own rejection of that case, a semantic outcome the caller interprets.
Everything else that prevents a well-formed answer (the binary is missing or
cannot start, a timeout, a signal or unexpected exit status, output that is not
one JSON row per case, or an exit status inconsistent with the rows) raises
`CheckerUnavailable`. No Python result is ever substituted.
"""
from __future__ import annotations

import subprocess

from ..assurance import require_lean_binding
from ..errors import CheckerUnavailable, VEError
from ..wire import canonical_json, loads_json


def run(operation: str, executable, cases: list[dict], *, runner: str, mode: str = "",
        timeout: float) -> list[dict]:
    """Submit `cases` to the Lean `runner` executable at path `executable`."""
    kinds = {case["kind"] for case in cases if type(case.get("kind")) is str}
    require_lean_binding(operation, runner, mode, kinds)

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
    if type(rows) is not list or len(rows) != len(cases) or any(type(row) is not dict for row in rows):
        raise unavailable("output does not hold one result object per case")
    for case, row in zip(cases, rows):
        if "id" in row and row["id"] != case.get("id"):
            raise unavailable("result ids do not match the submitted cases")
    rejected = any(row.get("status") == "error" for row in rows)
    if rejected != (proc.returncode == 1):
        raise unavailable("exit status disagrees with its result rows")
    return rows
