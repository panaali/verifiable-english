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
# Python raises these errors without the code in the message; the Lean
# runners prefix it only to carry the code.
_UNPREFIXED = frozenset({"UnknownSymbol", "TypeMismatch", "UnboundVariable", "UnsupportedProfile"})
# Other ResourceLimit messages carry their prefix in Python too; `_Checker`'s
# budget messages (ve/ast.py) do not.
_UNPREFIXED_LIMITS = frozenset({"AST exceeds 10,000 nodes", "Formula exceeds 64 nesting levels",
                                "Arithmetic term exceeds 64 nesting levels"})


def checker_error(message: str, *, code: str | None = None,
                  span: dict | None = None, generator: str | None = None) -> VEError:
    """Make the existing VEError class from a Lean or Rust error record."""
    match = re.match(r"^InvalidModel\(([^)]*)\)", message)
    if match:
        code, generator = "InvalidModel", generator or match.group(1)
    elif code is None:
        head, sep, rest = message.partition(":")
        code = head if head in _CODES else "InvalidInput"
        if message.startswith("Definition "):
            code = "InvalidInput"
        if sep and (code in _UNPREFIXED or
                    (code == "ResourceLimit" and rest.lstrip() in _UNPREFIXED_LIMITS)):
            message = rest.lstrip()
    cls = _CODES.get(code, VEError)
    if cls is None:
        from ..admission import AdmissionError
        cls = AdmissionError
    location = Span(**span) if span is not None else None
    if cls is InvalidModel:
        return cls(message, generator=generator, span=location)
    return cls(message, span=location)


def backend_rejection(error: VEError) -> VEError:
    """Mark `error` as naming a rejection a Lean or Rust checker returned.

    The mark is provenance only: the Gate 2 parity tool counts a rejection
    cell as backend-decided when the error the operation raised carries it."""
    error.backend_rejection = True
    return error


def require_ok(record: dict) -> dict:
    """Return a successful runner record or raise its classified diagnostic."""
    if record.get("status") == "error":
        error = record.get("error", "checker rejected request")
        if isinstance(error, dict):
            raise backend_rejection(checker_error(
                error.get("message", "checker rejected request"), code=error.get("code"),
                span=error.get("span"), generator=record.get("generator")))
        raise backend_rejection(checker_error(str(error), generator=record.get("generator")))
    return record
