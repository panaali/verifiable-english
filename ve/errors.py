"""Stable diagnostics shared by all experimental checking boundaries."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Span:
    start: int
    end: int
    line: int
    column: int


class VEError(ValueError):
    code = "InvalidInput"

    def __init__(self, message: str, *, span: Span | None = None, path: str = "",
                 diagnostic: dict | None = None):
        super().__init__(message)
        self.message, self.span, self.path = message, span, path
        self.diagnostic = diagnostic

    def to_dict(self) -> dict:
        result = {"code": self.code, "message": self.message}
        if self.path:
            result["path"] = self.path
        if self.span is not None:
            result["span"] = {k: getattr(self.span, k) for k in ("start", "end", "line", "column")}
        if self.diagnostic is not None:
            result["diagnostic"] = self.diagnostic
        return result


class SyntaxError(VEError):
    code = "SyntaxError"


class AmbiguousDerivation(SyntaxError):
    """A distinct exception type while preserving the public SyntaxError code."""


class UnknownSymbol(VEError):
    code = "UnknownSymbol"


class DuplicateDeclaration(VEError):
    code = "DuplicateDeclaration"


class UnboundVariable(VEError):
    code = "UnboundVariable"


class ShadowedVariable(VEError):
    code = "ShadowedVariable"


class TypeMismatch(VEError):
    code = "TypeMismatch"


class InvalidModel(VEError):
    code = "InvalidModel"

    def __init__(self, message: str, *, generator: str | None = None,
                 span: Span | None = None, path: str = ""):
        super().__init__(message, span=span, path=path)
        self.generator = generator

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.generator is not None:
            result["generator"] = self.generator
        return result


class UnsupportedProfile(VEError):
    code = "UnsupportedProfile"


class CheckerUnavailable(VEError):
    code = "CheckerUnavailable"


class ResourceLimit(VEError):
    code = "ResourceLimit"


class CheckerUnavailable(RuntimeError):
    """An operational failure: no verdict was obtained, so none is reported.

    A missing or mismatched backend, a crash, a timeout, malformed backend
    output, or an operation whose verdict authority cannot run on this path.
    Deliberately not a `VEError` (nor a `ValueError`): no handler that turns
    input errors into `InvalidInput`, or exhausted budgets into `UNKNOWN` or
    `ResourceLimit`, can absorb it. See docs/spec/assurance-manifest.md.
    """
    code = "CheckerUnavailable"

    def __init__(self, message: str, *, operation: str = "", backend: str = ""):
        super().__init__(message)
        self.message, self.operation, self.backend = message, operation, backend

    def to_dict(self) -> dict:
        result = {"code": self.code, "message": self.message}
        if self.operation:
            result["operation"] = self.operation
        if self.backend:
            result["backend"] = self.backend
        return result


class AuthorityViolation(CheckerUnavailable):
    """A migrated operation reached a non-authoritative implementation."""
