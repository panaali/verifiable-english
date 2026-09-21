"""Bounded, provider-independent assisted authoring for VE documents.

The proposer is deliberately injected.  This module neither calls a model nor
interprets prose: it only gives a proposer bounded opportunities to repair text
against the ordinary VE parser and checker boundary.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .ast import Document
from .environment import Environment
from .errors import Span, VEError
from .parser import parse
from .printer import print_document


_REPAIR_HINTS = {
    "SyntaxError": "Use exact VE syntax, including canonical spacing and a final '.\\n'.",
    "UnknownSymbol": "Use only sorts, predicates, and constants declared in the environment.",
    "UnboundVariable": "Bind the variable before use and keep every use inside its binder.",
    "ShadowedVariable": "Give each simultaneously active binder a distinct variable name.",
    "TypeMismatch": "Use terms with the sorts and predicate arities declared in the environment.",
    "ResourceLimit": "Shorten the proposal so it fits the VE source, depth, and node limits.",
}
_DEFAULT_REPAIR_HINT = "Revise the proposal to satisfy the VE parser and checker diagnostic."


@dataclass(frozen=True, slots=True)
class AuthoringDiagnostic:
    """Stable, located feedback suitable for a repair prompt or audit log."""

    code: str
    message: str
    span: Span
    repair_hint: str
    path: str = ""

    def to_dict(self) -> dict:
        result = {
            "code": self.code,
            "message": self.message,
            "span": {key: getattr(self.span, key)
                     for key in ("start", "end", "line", "column")},
            "repair_hint": self.repair_hint,
        }
        if self.path:
            result["path"] = self.path
        return result


@dataclass(frozen=True, slots=True)
class AuthoringRequest:
    """Input to a proposer; rounds are one-based."""

    round: int
    previous_text: str | None
    diagnostic: AuthoringDiagnostic | None


@dataclass(frozen=True, slots=True)
class AuthoringRound:
    round: int
    text: str
    accepted: bool
    diagnostic: AuthoringDiagnostic | None

    def to_dict(self) -> dict:
        result = {"round": self.round, "text": self.text, "accepted": self.accepted}
        if self.diagnostic is not None:
            result["diagnostic"] = self.diagnostic.to_dict()
        return result


@dataclass(frozen=True, slots=True)
class AuthoringResult:
    """Final outcome, including every raw proposal and its acceptance decision."""

    accepted: bool
    text: str
    document: Document | None
    canonical_text: str | None
    rounds: tuple[AuthoringRound, ...]

    @property
    def acceptance_rate(self) -> float:
        return sum(item.accepted for item in self.rounds) / len(self.rounds)

    def to_dict(self) -> dict:
        return {
            "accepted": self.accepted,
            "text": self.text,
            "canonical_text": self.canonical_text,
            "rounds": [item.to_dict() for item in self.rounds],
            "acceptance_rate": self.acceptance_rate,
        }


Proposer = Callable[[AuthoringRequest], str]


def _diagnostic(error: VEError) -> AuthoringDiagnostic:
    # Some boundary errors (notably source-size limits) occur before a parser
    # cursor exists.  Point those at the start rather than returning unlocated
    # feedback, so every authoring rejection has the same usable shape.
    span = error.span if error.span is not None else Span(0, 0, 1, 1)
    return AuthoringDiagnostic(
        code=error.code,
        message=error.message,
        span=span,
        repair_hint=_REPAIR_HINTS.get(error.code, _DEFAULT_REPAIR_HINT),
        path=error.path,
    )


def gatekeep(env, propose: Proposer, *, max_rounds: int = 3) -> AuthoringResult:
    """Run a bounded propose/parse/check repair loop.

    ``propose`` is called once per round with the previous raw text and
    diagnostic.  It must return ``str``; provider failures and programming
    errors propagate rather than being mislabeled as invalid VE.  The first
    proposal with a usable canonical rendering stops the loop.  An exhausted
    result retains the final proposal and the complete per-round audit trail.
    """
    if not isinstance(env, Environment):
        raise TypeError("env must be a validated Environment")
    if type(max_rounds) is not int or max_rounds < 1:
        raise ValueError("max_rounds must be a positive integer")
    if not callable(propose):
        raise TypeError("propose must be callable")

    previous_text = None
    diagnostic = None
    records: list[AuthoringRound] = []
    for round_number in range(1, max_rounds + 1):
        request = AuthoringRequest(round_number, previous_text, diagnostic)
        text = propose(request)
        if type(text) is not str:
            raise TypeError("propose must return str")
        try:
            document = parse(env, text)
            canonical_text = print_document(env, document)
        except VEError as error:
            diagnostic = _diagnostic(error)
            records.append(AuthoringRound(round_number, text, False, diagnostic))
            previous_text = text
            continue
        records.append(AuthoringRound(round_number, text, True, None))
        return AuthoringResult(True, text, document, canonical_text, tuple(records))

    return AuthoringResult(False, previous_text, None, None, tuple(records))
