"""Per-operation authority selection and zero-tolerance shadow recording.

Python remains the default through stage 3.  A shadow call always returns the
Python result; checker failures and differences are recorded in JSONL.  A
selected Lean or Rust authority never falls back to Python.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import json
import os
from pathlib import Path
import threading
import time
from dataclasses import asdict, is_dataclass
from typing import Callable, Iterator, TypeVar

from .lean_service import CheckerUnavailable

T = TypeVar("T")
_AUTHORITIES = frozenset({"python", "shadow", "lean", "rust-experimental"})
_log_lock = threading.Lock()
# Callables told (op, authority) on every dispatched call; the Gate 2 parity
# tool uses them to tell adapter-routed cells from Python-only ones.
observers: list[Callable[[str, str], None]] = []


# The authority of every call inside an adapter that composes other operations
# (`pinned`); None outside one.
_pin: ContextVar[str | None] = ContextVar("ve_authority_pin", default=None)


@contextmanager
def pinned(authority: str) -> Iterator[None]:
    """Run a composing adapter's constituents on `authority`, whatever the
    per-operation selection: the adapter's verdict then rests on that backend's
    checks only, never on a constituent another override sent to Python."""
    if authority not in _AUTHORITIES - {"shadow"}:
        raise ValueError(f"invalid pinned authority {authority!r}")
    token = _pin.set(authority)
    try:
        yield
    finally:
        _pin.reset(token)


def composed(authority: str, run: Callable[[], T]) -> Callable[[], T]:
    """`run` with its constituents pinned to `authority` (an adapter for `execute`)."""
    def adapter() -> T:
        with pinned(authority):
            return run()
    return adapter


def _overrides() -> dict[str, str]:
    """The per-operation selections of VE_AUTHORITY_OVERRIDES (the last entry for an operation wins)."""
    selected = {}
    for entry in filter(None, os.environ.get("VE_AUTHORITY_OVERRIDES", "").split(",")):
        name, sep, authority = entry.partition("=")
        if not sep or not name or authority not in _AUTHORITIES:
            raise ValueError(f"invalid VE_AUTHORITY_OVERRIDES entry {entry!r}")
        selected[name] = authority
    return selected


def overridden(op: str) -> bool:
    """Whether VE_AUTHORITY_OVERRIDES selects an authority for `op` by name. An operation whose Lean side
    is not built yet joins the dispatch only then, never through VE_AUTHORITY or a pin."""
    return op in _overrides()


# Operations with a temporary Python-authority shadow policy.
SHADOW_ONLY = frozenset({"english.admission"})


def shadowed(op: str, payload: dict, python: Callable[[], T], candidate: Callable[[], T],
             shadow: Callable[[object, object], dict | None]) -> T:
    """Python's result for a shadow-only operation. By default the candidate is also run and
    compared; `op=python` disables that comparison. Another backend cannot become authoritative."""
    if op not in SHADOW_ONLY:
        raise ValueError(f"{op} is not a shadow-only operation")
    selected = _overrides().get(op, "shadow")
    if selected not in ("python", "shadow"):
        raise CheckerUnavailable(f"CheckerUnavailable: {op} accepts only the python or shadow authority; "
                                 f"{selected!r} would make the candidate reader the authority")
    for observe in observers:
        observe(op, selected)
    if selected == "python":
        return python()
    return _shadow(op, payload, python, candidate, None, shadow)


def authority_for(op: str) -> str:
    pin = _pin.get()
    if pin is not None:
        return pin
    selected = _overrides().get(op, os.environ.get("VE_AUTHORITY", "python"))
    if selected not in _AUTHORITIES:
        raise ValueError(f"invalid VE_AUTHORITY {selected!r}")
    return selected


def _record(value):
    if hasattr(value, "to_dict"):
        return _record(value.to_dict())
    if is_dataclass(value):
        return _record(asdict(value))
    if isinstance(value, dict):
        return {key: _record(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_record(item) for item in value]
    return value


def _classes(left, right) -> list[str]:
    left, right = _record(left), _record(right)
    classes: set[str] = set()
    identities = {"environment_id", "source_id", "meaning_id", "model_id",
                  "claim_id", "edge_id", "graph_id"}
    composition = {"composition", "assumptions", "assumption_claim_ids",
                   "supporting_edge_ids", "unresolved_obligations"}

    def shape(path: tuple[str, ...]) -> None:
        classes.add("schema")
        if "explanation" in path or "trace" in path:
            classes.add("explanation")
        if any(part in composition for part in path):
            classes.add("composition")

    def visit(a, b, path: tuple[str, ...] = ()) -> None:
        if type(a) is not type(b):
            shape(path)
            return
        if isinstance(a, dict):
            if a.keys() != b.keys():
                shape(path)
            for key in a.keys() & b.keys():
                visit(a[key], b[key], (*path, key))
            return
        if isinstance(a, list):
            if len(a) != len(b):
                shape(path)
            for x, y in zip(a, b):
                visit(x, y, path)
            return
        if a == b:
            return
        key = path[-1] if path else ""
        if "explanation" in path or "trace" in path:
            classes.add("explanation")
        elif any(part in composition for part in path):
            classes.add("composition")
        elif key == "status":
            classes.update(("verdict", "budget-outcome"))
        elif key in {"valid", "value", "values", "refutes", "composed", "verdict"}:
            classes.add("verdict")
        elif key in identities:
            classes.add("identity")
        elif key in {"evaluations", "steps", "models_checked"}:
            classes.add("count-value")
        elif key in {"code", "generator"}:
            classes.add("diagnostic-code")
        elif key in {"message", "detail"}:
            classes.add("diagnostic-message")
        else:
            classes.add("schema")

    visit(left, right)
    return sorted(classes)


def _append(record: dict) -> None:
    path = Path(os.environ.get("VE_SHADOW_LOG", "ve-shadow.jsonl"))
    line = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
    with _log_lock:
        with path.open("a", encoding="utf-8") as stream:
            stream.write(line)


# Operations with ONE implementation under every authority, and the engine it runs (lean-first batch 15b:
# Rust keeps search; Python has none). There is nothing to shadow, and differential harnesses must not
# compare a "Python" answer of these operations with that engine's own (`conformance.three_way`,
# `tools/difffuzz.py`): they compare it with recorded answers or with another engine's check instead.
SINGLE_OWNER = {"countermodel_search": "rust", "distinguishing_model": "rust"}


def owned(op: str, run: Callable[[], T]) -> T:
    """Run a single-owner operation (SINGLE_OWNER) under whatever authority is selected; observers
    still see the selection, which the operation's constituents (its witness checks) follow."""
    if op not in SINGLE_OWNER:
        raise ValueError(f"{op} is not a single-owner operation")
    authority = authority_for(op)
    for observe in observers:
        observe(op, authority)
    return run()


def execute(op: str, payload: dict, python: Callable[[], T], *,
            lean: Callable[[], T] | None = None,
            rust: Callable[[], T] | None = None,
            shadow: Callable[[object, object], dict | None] | None = None) -> T:
    """Run the selected implementation, or compare both while returning Python.

    The caller passes independent implementations with the same public result
    type.  No class-A result may be inferred from the Python result in `lean`.
    Under shadow, `shadow(python_result, backend_result)` (either may be the
    exception raised instead) replaces the default record: it returns the
    fields of the record to append, or None for no record.
    """
    if op in SHADOW_ONLY:
        raise ValueError(f"{op} is shadow-only: dispatch it through `shadowed`")
    if op in SINGLE_OWNER or python is lean or python is rust:
        # A shadow (or a differential test) of one implementation against itself compares nothing.
        raise ValueError(f"{op} has one implementation: dispatch it through `owned`")
    authority = authority_for(op)
    for observe in observers:
        observe(op, authority)
    if authority == "python":
        return python()
    if authority == "lean":
        if lean is None:
            raise CheckerUnavailable(f"CheckerUnavailable: Lean adapter for {op} is not available")
        return lean()
    if authority == "rust-experimental":
        if rust is None:
            raise CheckerUnavailable(f"CheckerUnavailable: Rust adapter for {op} is not available")
        return rust()
    return _shadow(op, payload, python, lean, rust, shadow)


def _shadow(op: str, payload: dict, python: Callable[[], T], lean: Callable[[], T] | None,
            rust: Callable[[], T] | None, shadow: Callable[[object, object], dict | None] | None) -> T:
    """Run Python and the backend, record their difference, and return Python's result."""
    started = time.monotonic()
    try:
        original = python()
        # A comparing `shadow` reads the results itself: Python's result is never lost to a record.
        left = _record(original) if shadow is None else None
    except Exception as exc:
        original, left = exc, {"code": getattr(exc, "code", type(exc).__name__),
                               "message": str(exc)}
    python_ms = (time.monotonic() - started) * 1000
    candidate = lean or rust
    started = time.monotonic()
    if candidate is None:
        value = CheckerUnavailable(f"CheckerUnavailable: no adapter for {op}")
        right = {"code": "CheckerUnavailable", "message": f"no adapter for {op}"}
    else:
        try:
            value = candidate()
            right = _record(value) if shadow is None else None
        except Exception as exc:
            value, right = exc, {"code": getattr(exc, "code", type(exc).__name__),
                                 "message": str(exc)}
    backend_ms = (time.monotonic() - started) * 1000
    if shadow is not None:
        record = shadow(original, value)
    else:
        classes = _classes(left, right)
        record = {"python": left, "lean": right if lean else None, "rust": right if not lean else None,
                  "class": classes} if classes else None
    if record is not None:
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                           separators=(",", ":")).encode()).hexdigest()
        _append({"op": op, "input_digest": digest, **record, "python_ms": python_ms, "backend_ms": backend_ms})
    if isinstance(original, Exception):
        raise original
    return original
