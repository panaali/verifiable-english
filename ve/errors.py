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

    def __init__(self, message: str, *, span: Span | None = None, path: str = ""):
        super().__init__(message)
        self.message, self.span, self.path = message, span, path

    def to_dict(self) -> dict:
        result = {"code": self.code, "message": self.message}
        if self.path:
            result["path"] = self.path
        if self.span is not None:
            result["span"] = {k: getattr(self.span, k) for k in ("start", "end", "line", "column")}
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


class ResourceLimit(VEError):
    code = "ResourceLimit"
