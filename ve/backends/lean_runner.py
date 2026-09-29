"""Lazy shared Lean service client for public adapters."""
from __future__ import annotations

import atexit
import threading

from .diagnostics import require_ok
from .lean_service import LeanServicePool

_pool: LeanServicePool | None = None
_lock = threading.Lock()


def _close() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


atexit.register(_close)


def route_mode(env) -> str:
    """The service mode for a plain route case over a ve.core@0.2 `env`.

    The route decoders reject the `regulated` extension; the norms route
    validates it and answers background, evaluate and countermodel cases.
    """
    return "norms" if any(d.regulated is not None for d in env.predicates.values()) else "route"


def run(mode: str, cases: list[dict], *, timeout: float | None = None) -> list[dict]:
    """Send a batch and classify each case diagnostic."""
    global _pool
    with _lock:
        if _pool is None:
            _pool = LeanServicePool()
        pool = _pool
    return [require_ok(row) for row in pool.run(mode, cases, timeout=timeout)]
