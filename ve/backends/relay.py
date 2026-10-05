"""The one Python entry to Lean's decisions (docs/LEAN-FIRST-PLAN.md, rule 2, batches 0 and 1).

`decide(mode, cases)` sends a batch to the persistent Lean service and returns Lean's
rows in case order. A rejection row raises the `VEError` subclass of the `code` the service
sets beside it with Lean's text verbatim: no rewording, no prefix stripping and no
classification here, since the service derives every code (`lean/VE/Service/Protocol.lean`,
`rejectionCode` and `coding`). A route row that carries its own contract code (the soft-norms@0
table's, `SoftNorms.Run.reportedCode`) keeps it as the error's `code`. Python raises its own
error only for operational failures: `CheckerUnavailable` when the service cannot answer, or
answers with a code this client has no class for.

`rows(mode, cases)` returns every row, rejections included, for the callers that read a
route's rejection rows themselves (one row per case, as the one-shot route executables printed
them before batch 1). Every statement-layer route is a service mode, so this module and
`lean.run` (the manifest-bound calls) are the only ways `ve` reaches Lean.
"""
from __future__ import annotations

import atexit
import os
from pathlib import Path
import threading

from ..errors import (CheckerUnavailable, DuplicateDeclaration, InvalidModel, ResourceLimit, SyntaxError,
                      TypeMismatch, UnboundVariable, UnknownSymbol, UnsupportedProfile, VEError)
from .lean_service import DEFAULT_EXECUTABLE, LeanServicePool

# The pool of the default service (`VE_LEAN_SERVICE`, else the lake build), and one pool per
# other service executable a caller names.
_pool: LeanServicePool | None = None
_pools: dict[Path, LeanServicePool] = {}
_lock = threading.Lock()


def _admission_error():
    from ..admission import AdmissionError  # ve.admission imports this package
    return AdmissionError


# One class per code of the service's handshake (`codes`); `None` is resolved lazily.
CLASSES: dict[str, type | None] = {
    "InvalidInput": VEError, "SyntaxError": SyntaxError, "UnknownSymbol": UnknownSymbol,
    "DuplicateDeclaration": DuplicateDeclaration, "UnboundVariable": UnboundVariable,
    "TypeMismatch": TypeMismatch, "InvalidModel": InvalidModel, "UnsupportedProfile": UnsupportedProfile,
    "ResourceLimit": ResourceLimit, "AdmissionError": None, "CheckerUnavailable": CheckerUnavailable,
}


def _close() -> None:
    global _pool
    with _lock:
        pools = [pool for pool in (_pool, *_pools.values()) if pool is not None]
        _pool = None
        _pools.clear()
    for pool in pools:
        pool.close()


atexit.register(_close)


def _pool_for(executable: str | os.PathLike | None) -> LeanServicePool:
    """The pool of services running `executable`; the default pool when it is None or the
    default service."""
    global _pool
    default = Path(os.environ.get("VE_LEAN_SERVICE") or DEFAULT_EXECUTABLE)
    path = None if executable is None or Path(executable).resolve() == default.resolve() else Path(executable)
    with _lock:
        if path is None:
            if _pool is None:
                _pool = LeanServicePool()
            return _pool
        if path not in _pools:
            _pools[path] = LeanServicePool(executable=path)
        return _pools[path]


def rejection(code: str, message: str, *, generator: str | None = None) -> BaseException:
    """Lean's rejection as the exception of its code, with Lean's text."""
    if code not in CLASSES:
        return CheckerUnavailable(f"CheckerUnavailable: the Lean service answered with an unknown code {code!r}")
    cls = CLASSES[code] or _admission_error()
    if cls is CheckerUnavailable:
        return CheckerUnavailable(message)
    return InvalidModel(message, generator=generator) if cls is InvalidModel else cls(message)


def _raised(entry: dict) -> BaseException:
    """The error a bound rejection entry raises (`rejection`), marked as the backend's."""
    row = entry["result"]
    error = rejection(entry["code"], row["error"], generator=entry.get("generator"))
    if isinstance(error, VEError):
        if type(row.get("code")) is str:
            error.code = row["code"]
        # Provenance only: the Gate 2 parity tool counts a rejection cell as
        # backend-decided when the error the operation raised carries this mark.
        error.backend_rejection = True
    return error


def rows(mode: str, cases: list[dict], *, timeout: float | None = None,
         executable: str | os.PathLike | None = None) -> list[dict]:
    """Lean's rows for `cases`, in order, rejection rows included. `timeout` replaces the
    mode's deadline with a wall-clock limit (`lean_service.DEADLINES`)."""
    return [entry["result"] for entry in _pool_for(executable).run_bound(mode, cases, timeout=timeout)]


def decide(mode: str, cases: list[dict], *, timeout: float | None = None,
           executable: str | os.PathLike | None = None) -> list[dict]:
    """Lean's rows for `cases`, in order; the first rejection row raises its diagnostic."""
    entries = _pool_for(executable).run_bound(mode, cases, timeout=timeout)
    for entry in entries:
        if entry["result"].get("status") == "error":
            raise _raised(entry)
    return [entry["result"] for entry in entries]
