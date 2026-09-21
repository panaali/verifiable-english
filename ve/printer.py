"""Canonical and explanatory read-only renderers for typed VE ASTs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import ast
from .errors import ResourceLimit
from .limits import MAX_SOURCE_BYTES

NATURAL_RENDERER = "ve.ace-explicit"
NATURAL_RENDERER_VERSION = "0"


def _checker():
    return ast.check_document, ast.check_formula


class _Canonical:
    def __init__(self):
        self.next_name = 0

    def term(self, value: Any, scope: list[str]) -> str:
        if isinstance(value, ast.Var):
            if value.index < 0 or value.index >= len(scope):
                raise ValueError(f"invalid bound-variable index {value.index}")
            return scope[value.index]
        if isinstance(value, ast.Const):
            return "@" + value.name
        raise TypeError(f"unsupported term {type(value).__name__}")

    def formula(self, value: Any, scope: list[str]) -> str:
        if isinstance(value, ast.Top): return "true"
        if isinstance(value, ast.Bottom): return "false"
        if isinstance(value, ast.Unary):
            return f"{self.term(value.term, scope)} is {value.predicate}"
        if isinstance(value, ast.Binary):
            return f"{self.term(value.left, scope)} {value.predicate} {self.term(value.right, scope)}"
        if isinstance(value, ast.Eq):
            return f"{self.term(value.left, scope)} equals {self.term(value.right, scope)}"
        if isinstance(value, ast.Not): return f"not ({self.formula(value.body, scope)})"
        if isinstance(value, ast.And):
            return f"({self.formula(value.left, scope)}) and ({self.formula(value.right, scope)})"
        if isinstance(value, ast.Or):
            return f"({self.formula(value.left, scope)}) or ({self.formula(value.right, scope)})"
        if isinstance(value, ast.Implies):
            return f"if ({self.formula(value.left, scope)}), then ({self.formula(value.right, scope)})"
        if isinstance(value, (ast.Forall, ast.Exists)):
            name = f"x{self.next_name}"; self.next_name += 1
            keyword = "for every" if isinstance(value, ast.Forall) else "there exists"
            return f"{keyword} {value.sort} {name}, ({self.formula(value.body, [name, *scope])})"
        raise TypeError(f"unsupported formula {type(value).__name__}")


def print_formula(env: Any, formula: Any) -> str:
    """Print one closed formula without statement punctuation."""
    _checker()[1](env, formula)
    text = _Canonical().formula(formula, [])
    if len(text) + 2 > MAX_SOURCE_BYTES:
        raise ResourceLimit("Canonical statement exceeds 64 KiB of VE text")
    return text


def print_document(env: Any, document: ast.Document) -> str:
    """Return the sole canonical VE v0 serialization of *document*."""
    _checker()[0](env, document)
    lines = []
    for formula in document.formulas:
        # The naming counter resets at each statement.
        lines.append(_Canonical().formula(formula, []) + ".\n")
    text = "".join(lines)
    if len(text) > MAX_SOURCE_BYTES:
        raise ResourceLimit("Canonical document exceeds 64 KiB of VE text")
    return text


@dataclass(frozen=True, slots=True)
class NaturalView:
    text: str
    environment_id: str
    meaning_id: str
    renderer: str = NATURAL_RENDERER
    version: str = NATURAL_RENDERER_VERSION

    def to_dict(self) -> dict[str, str]:
        return {"text": self.text, "environment_id": self.environment_id,
                "meaning_id": self.meaning_id, "renderer": self.renderer,
                "version": self.version}


class _Natural(_Canonical):
    """Deliberately explicit templates; fluency never hides logical structure."""
    def formula(self, value: Any, scope: list[str]) -> str:
        if isinstance(value, ast.Top): return "the condition is true"
        if isinstance(value, ast.Bottom): return "the condition is false"
        if isinstance(value, ast.Unary):
            return f"{self.term(value.term, scope)} satisfies {value.predicate}"
        if isinstance(value, ast.Binary):
            return f"{self.term(value.left, scope)} stands in relation {value.predicate} to {self.term(value.right, scope)}"
        if isinstance(value, ast.Eq):
            return f"{self.term(value.left, scope)} is equal to {self.term(value.right, scope)}"
        if isinstance(value, ast.Not):
            return f"it is not the case that ({self.formula(value.body, scope)})"
        if isinstance(value, ast.And):
            return f"both ({self.formula(value.left, scope)}) and ({self.formula(value.right, scope)})"
        if isinstance(value, ast.Or):
            return f"either ({self.formula(value.left, scope)}) or ({self.formula(value.right, scope)}), or both"
        if isinstance(value, ast.Implies):
            return f"if ({self.formula(value.left, scope)}), then ({self.formula(value.right, scope)})"
        if isinstance(value, (ast.Forall, ast.Exists)):
            name = f"x{self.next_name}"; self.next_name += 1
            body = self.formula(value.body, [name, *scope])
            if isinstance(value, ast.Forall):
                return f"for every {value.sort} {name}, ({body})"
            return f"there exists at least one {value.sort} {name} such that ({body})"
        raise TypeError(f"unsupported formula {type(value).__name__}")


def natural_document(env: Any, document: ast.Document) -> NaturalView:
    """Render a validated read-only view with explicit scope and dependencies."""
    _checker()[0](env, document)
    lines = []
    for n, formula in enumerate(document.formulas, 1):
        lines.append(f"Statement {n}: {_Natural().formula(formula, [])}.")
    from .identity import meaning_id
    return NaturalView("\n".join(lines), env.environment_id, meaning_id(env, document))


def natural_formula(env: Any, formula: Any) -> NaturalView:
    _checker()[1](env, formula)
    from .identity import meaning_id
    return NaturalView(_Natural().formula(formula, []) + ".", env.environment_id,
                       meaning_id(env, formula))
