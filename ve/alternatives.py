"""Lean-only alternatives route transport.

No causal or followability verdict is computed in Python. The route consumes
the original case so Lean can regenerate every premise and binding itself.
"""
from __future__ import annotations

import os

from .backends.relay import rows
from .errors import CheckerUnavailable

def run_case(case: dict, *, timeout: float | None = None) -> dict:
    """Dispatch one raw case to the Lean alternatives route (service mode `alternatives`); its row,
    a rejection included. Never substitute a Python semantic implementation."""
    if os.environ.get("VE_AUTHORITY") == "python":
        raise CheckerUnavailable("alternatives@0 requires the Lean checker")
    return rows("alternatives", [case], timeout=timeout)[0]
