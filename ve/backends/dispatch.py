"""Per-operation authority selection and zero-tolerance shadow recording.

Python remains the default through stage 3.  A shadow call always returns the
Python result; checker failures and differences are recorded in JSONL.  A
selected Lean or Rust authority never falls back to Python.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import threading
import time
from dataclasses import asdict, is_dataclass
from typing import Callable, TypeVar

from .lean_service import CheckerUnavailable

T = TypeVar("T")
_AUTHORITIES = frozenset({"python", "shadow", "lean", "rust-experimental"})
_log_lock = threading.Lock()


def authority_for(op: str) -> str:
    selected = os.environ.get("VE_AUTHORITY", "python")
    for entry in filter(None, os.environ.get("VE_AUTHORITY_OVERRIDES", "").split(",")):
        name, sep, authority = entry.partition("=")
        if not sep or not name or authority not in _AUTHORITIES:
            raise ValueError(f"invalid VE_AUTHORITY_OVERRIDES entry {entry!r}")
        if name == op:
            selected = authority
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
    if type(left) is not type(right):
        return ["schema"]
    if isinstance(left, dict):
        if left.keys() != right.keys():
            return ["schema"]
        classes = set()
        for key in left:
            if left[key] == right[key]:
                continue
            if key in {"status", "valid", "value", "values", "refutes", "composed", "verdict"}:
                classes.add("verdict")
            elif key in {"environment_id", "source_id", "meaning_id", "model_id", "claim_id", "edge_id"}:
                classes.add("identity")
            elif key in {"evaluations", "steps", "models_checked"}:
                classes.add("count-value")
            elif key in {"explanation", "trace"}:
                classes.add("explanation")
            elif key in {"composition", "assumptions", "assumption_claim_ids", "supporting_edge_ids"}:
                classes.add("composition")
            elif key in {"code", "generator"}:
                classes.add("diagnostic-code")
            elif key in {"message", "detail"}:
                classes.add("diagnostic-message")
            else:
                classes.add("schema")
        return sorted(classes)
    return [] if left == right else ["verdict"]


def _append(record: dict) -> None:
    path = Path(os.environ.get("VE_SHADOW_LOG", "ve-shadow.jsonl"))
    line = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
    with _log_lock:
        with path.open("a", encoding="utf-8") as stream:
            stream.write(line)


def execute(op: str, payload: dict, python: Callable[[], T], *,
            lean: Callable[[], T] | None = None,
            rust: Callable[[], T] | None = None) -> T:
    """Run the selected implementation, or compare both while returning Python.

    The caller passes independent implementations with the same public result
    type.  No class-A result may be inferred from the Python result in `lean`.
    """
    authority = authority_for(op)
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

    started = time.monotonic()
    try:
        original = python()
        left = _record(original)
    except Exception as exc:
        original, left = exc, {"code": getattr(exc, "code", type(exc).__name__),
                               "message": str(exc)}
    python_ms = (time.monotonic() - started) * 1000
    candidate = lean or rust
    started = time.monotonic()
    if candidate is None:
        right = {"code": "CheckerUnavailable", "message": f"no adapter for {op}"}
    else:
        try:
            right = _record(candidate())
        except Exception as exc:
            right = {"code": getattr(exc, "code", type(exc).__name__),
                     "message": str(exc)}
    backend_ms = (time.monotonic() - started) * 1000
    classes = _classes(left, right)
    if classes:
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                           separators=(",", ":")).encode()).hexdigest()
        _append({"op": op, "input_digest": digest, "python": left,
                 "lean": right if lean else None, "rust": right if not lean else None,
                 "class": classes, "python_ms": python_ms, "backend_ms": backend_ms})
    if isinstance(original, Exception):
        raise original
    return original
