"""Lean risk route transport. Risk block decisions live in VE.Risk.Wire."""
from __future__ import annotations

import os

from .errors import CheckerUnavailable


def run_case(case: dict, *, timeout: float | None = None) -> dict:
    """Send a raw case to the Lean risk route (service mode `risk`) unchanged and return its row,
    a rejection included; an unavailable route is never a verdict.

    Python decodes nothing of the environment, record or log first, so every
    diagnostic, including its order, is the route's (risk.md 6, 7.3).
    """
    if os.environ.get("VE_AUTHORITY") == "python":
        raise CheckerUnavailable("risk@0 requires the Lean checker")
    from .backends.relay import rows
    return rows("risk", [case], timeout=timeout)[0]
