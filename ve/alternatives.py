"""Lean-only alternatives route transport.

No causal or followability verdict is computed in Python. The route consumes
the original case so Lean can regenerate every premise and binding itself.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess

from .errors import CheckerUnavailable, UnsupportedProfile, VEError
from .wire import canonical_json, loads_json

_KINDS = frozenset({"alt-elaborate", "alt-validate", "alt-conflict", "alt-followable",
                    "alt-certificate", "admission"})
_BINARY = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_alternatives_route"


def run_case(case: dict, *, binary: Path | None = None, timeout: int = 180) -> dict:
    """Dispatch one raw case; never substitute a Python semantic implementation."""
    if type(case) is not dict or case.get("kind") not in _KINDS or type(case.get("environment")) is not dict:
        raise VEError("InvalidInput: alternatives route case")
    from .environment import Environment
    env = Environment(case["environment"])
    if "alternatives@0" not in env.profiles:
        raise UnsupportedProfile("alternatives@0 is required")
    if os.environ.get("VE_AUTHORITY") == "python":
        raise CheckerUnavailable("alternatives@0 requires the Lean checker")
    executable = _BINARY if binary is None else Path(binary)
    if not executable.is_file():
        raise CheckerUnavailable("ve_alternatives_route is unavailable")
    raw = canonical_json([case])
    try:
        completed = subprocess.run([str(executable), "-"], input=raw, capture_output=True,
                                   timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckerUnavailable("ve_alternatives_route is unavailable") from exc
    if completed.returncode not in (0, 1):
        raise CheckerUnavailable("ve_alternatives_route failed")
    try:
        answer = loads_json(completed.stdout)
    except VEError as exc:
        raise CheckerUnavailable("ve_alternatives_route returned invalid JSON") from exc
    if type(answer) is not list or len(answer) != 1 or type(answer[0]) is not dict or answer[0].get("id") != case.get("id"):
        raise CheckerUnavailable("ve_alternatives_route returned an invalid response")
    return answer[0]
