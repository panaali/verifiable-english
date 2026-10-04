"""The one Python entry to Lean's decisions (docs/LEAN-FIRST-PLAN.md, rule 2, batch 0).

`decide(mode, cases)` sends a batch to the persistent Lean service and returns Lean's
rows in case order. A rejection row raises the `VEError` subclass of Lean's `code` with
Lean's text verbatim: no rewording, no prefix stripping and no classification here, since
the service derives every code (`lean/VE/Service/Protocol.lean`, `rejectionCode`). Python
raises its own error only for operational failures: `CheckerUnavailable` when the service
cannot answer, or answers with a code this client has no class for.
"""
from __future__ import annotations

import atexit
import threading

from ..errors import (CheckerUnavailable, DuplicateDeclaration, InvalidModel, ResourceLimit, SyntaxError,
                      TypeMismatch, UnboundVariable, UnknownSymbol, UnsupportedProfile, VEError)
from .lean_service import LeanServicePool

_pool: LeanServicePool | None = None
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
    if _pool is not None:
        _pool.close()
        _pool = None


atexit.register(_close)


def rejection(code: str, message: str, *, generator: str | None = None) -> BaseException:
    """Lean's rejection as the exception of its code, with Lean's text."""
    if code not in CLASSES:
        return CheckerUnavailable(f"CheckerUnavailable: the Lean service answered with an unknown code {code!r}")
    cls = CLASSES[code] or _admission_error()
    if cls is CheckerUnavailable:
        return CheckerUnavailable(message)
    return InvalidModel(message, generator=generator) if cls is InvalidModel else cls(message)


def decide(mode: str, cases: list[dict], *, timeout: float | None = None) -> list[dict]:
    """Lean's rows for `cases`, in order; the first rejection row raises its diagnostic."""
    global _pool
    with _lock:
        if _pool is None:
            _pool = LeanServicePool()
        pool = _pool
    rows = pool.run(mode, cases, timeout=timeout)
    for row in rows:
        if row.get("status") == "error":
            error = rejection(row["code"], row["error"], generator=row.get("generator"))
            if isinstance(error, VEError):
                # Provenance only: the Gate 2 parity tool counts a rejection cell as
                # backend-decided when the error the operation raised carries this mark.
                error.backend_rejection = True
            raise error
    return rows
