"""Translate checker diagnostics at the backend boundary.

The runner's text is retained on the exception.  Its leading code is only a
classification; an unrecognised message is InvalidInput, never a verdict.
"""
from __future__ import annotations

import re

from ..errors import (DuplicateDeclaration, InvalidModel, ResourceLimit, Span,
                      SyntaxError, TypeMismatch, UnboundVariable, UnknownSymbol,
                      UnsupportedProfile, VEError)
from .lean_service import CheckerUnavailable

_CODES = {
    cls.code: cls for cls in (DuplicateDeclaration, InvalidModel, ResourceLimit,
                              SyntaxError, TypeMismatch, UnboundVariable,
                              UnknownSymbol, UnsupportedProfile, CheckerUnavailable)
}
_CODES["AdmissionError"] = None  # imported lazily to avoid a package cycle
_CODES["DependencyCycle"] = VEError


def checker_error(message: str, *, code: str | None = None,
                  span: dict | None = None, generator: str | None = None) -> VEError:
    """Make the existing VEError class from a Lean or Rust error record."""
    match = re.match(r"^InvalidModel\(([^)]*)\)", message)
    if match:
        code, generator = "InvalidModel", generator or match.group(1)
    elif code is None:
        head = message.split(":", 1)[0]
        code = head if head in _CODES else "InvalidInput"
        if message.startswith("Definition "):
            code = "InvalidInput"
    cls = _CODES.get(code, VEError)
    if cls is None:
        from ..admission import AdmissionError
        cls = AdmissionError
    location = Span(**span) if span is not None else None
    if cls is InvalidModel:
        return cls(message, generator=generator, span=location)
    return cls(message, span=location)


def require_ok(record: dict) -> dict:
    """Return a successful runner record or raise its classified diagnostic."""
    if record.get("status") == "error":
        error = record.get("error", "checker rejected request")
        if isinstance(error, dict):
            raise checker_error(error.get("message", "checker rejected request"),
                                code=error.get("code"), span=error.get("span"),
                                generator=record.get("generator"))
        raise checker_error(str(error), generator=record.get("generator"))
    return record
