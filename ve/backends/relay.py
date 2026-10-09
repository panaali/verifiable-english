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
them before batch 1).

Both check every case before it is sent (`ve.environment_wire.wire_checked`, shared with the
Rust transport): a value `json` cannot send as itself (a lone surrogate, a set, bytes, a tuple, a
non-string key, a non-finite float, a cycle) raises the wire's `VEError`, never a `TypeError` or
`UnicodeEncodeError` from the encoder and never a silent conversion. That check is Python's and
is not a verdict; whether a JSON value is on the restricted subset stays Lean's to say.

Every statement-layer route is a service mode, so this module and `lean.run` (the
manifest-bound calls, whose `canonical_json` is the same wire check) are the only ways `ve`
reaches Lean.
"""
from __future__ import annotations

import atexit
import json
import os
from pathlib import Path
import threading
import weakref

from ..errors import (CheckerUnavailable, DuplicateDeclaration, InvalidModel, ResourceLimit, ShadowedVariable, Span, SyntaxError,
                      TypeMismatch, UnboundVariable, UnknownSymbol, UnsupportedProfile, VEError)
from ..environment_wire import wire_checked
from .lean_service import DEFAULT_EXECUTABLE, LeanServicePool

# The pool of the default service (`VE_LEAN_SERVICE`, else the lake build), and one pool per
# other service executable a caller names.
_pool: LeanServicePool | None = None
_pools: dict[Path, LeanServicePool] = {}
_lock = threading.Lock()
# `decide_once`'s answers, per pool: a pool runs one pinned build, so its answer to a request is
# the answer to every copy of that request; another pool (another build) starts empty.
_answers: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
ANSWERS_LIMIT = 256


def _admission_error():
    from ..admission import AdmissionError  # ve.admission imports this package
    return AdmissionError


# One class per code of the service's handshake (`codes`); `None` is resolved lazily.
CLASSES: dict[str, type | None] = {
    "InvalidInput": VEError, "SyntaxError": SyntaxError, "UnknownSymbol": UnknownSymbol,
    "DuplicateDeclaration": DuplicateDeclaration, "UnboundVariable": UnboundVariable,
    "ShadowedVariable": ShadowedVariable,
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
        if type(row.get("span")) is dict:
            error.span = Span(**row["span"])
        if type(row.get("code")) is str:
            error.code = row["code"]
        if row.get("dual_guard_cycle") is True:
            error.dual_guard_cycle = True
        # Provenance only: the Gate 2 parity tool counts a rejection cell as
        # backend-decided when the error the operation raised carries this mark.
        error.backend_rejection = True
    return error


def rows(mode: str, cases: list[dict], *, timeout: float | None = None,
         executable: str | os.PathLike | None = None) -> list[dict]:
    """Lean's rows for `cases`, in order, rejection rows included. `timeout` replaces the
    mode's deadline with a wall-clock limit (`lean_service.DEADLINES`)."""
    return [entry["result"] for entry in
            _pool_for(executable).run_bound(mode, wire_checked(cases), timeout=timeout)]


def decide(mode: str, cases: list[dict], *, timeout: float | None = None,
           executable: str | os.PathLike | None = None) -> list[dict]:
    """Lean's rows for `cases`, in order; the first rejection row raises its diagnostic."""
    entries = _pool_for(executable).run_bound(mode, wire_checked(cases), timeout=timeout)
    for entry in entries:
        if entry["result"].get("status") == "error":
            raise _raised(entry)
    return [entry["result"] for entry in entries]


def answer(mode: str, case: dict) -> tuple[dict, BaseException | None]:
    """Lean's row for one case and, for a rejection row, the error `decide` would raise for it, returned rather
    than raised: for a caller that keeps its own path for the rows Lean marks as undecided (`CheckerUnavailable`,
    `ResourceLimit`). A failure of the service itself is raised, as by `decide`."""
    [entry] = _pool_for(None).run_bound(mode, wire_checked([case]))
    return entry["result"], (_raised(entry) if entry["result"].get("status") == "error" else None)


def decide_once(mode: str, case: dict) -> dict:
    """`decide(mode, [case])[0]`, asked of the default service once per request (docs/LEAN-FIRST-PLAN.md,
    F3, batch 2). A service request is a pure function of its text, so a request that is the same JSON
    value as one the same pool answered gets that answer without a call: the agent-policy harness asked
    for the same few environments' Background 12,199 times. A rejection is raised each time and kept
    nowhere. At most `ANSWERS_LIMIT` answers are kept per pool."""
    pool = _pool_for(None)
    key = (mode, json.dumps(case, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    with _lock:
        row = _answers.setdefault(pool, {}).get(key)
    if row is None:
        row = decide(mode, [case])[0]
        with _lock:
            answers = _answers.setdefault(pool, {})
            if len(answers) >= ANSWERS_LIMIT:
                answers.clear()
            answers[key] = row
    return row
