"""Lean-only alternatives route transport.

No causal or followability verdict is computed in Python. The route consumes
the original case so Lean can regenerate every premise and binding itself.
"""
from __future__ import annotations

from .backends.relay import rows

def run_case(case: dict, *, timeout: float | None = None) -> dict:
    """Dispatch one raw case to the Lean alternatives route (service mode `alternatives`); its row,
    a rejection included. Never substitute a Python semantic implementation."""
    return rows("alternatives", [case], timeout=timeout)[0]
