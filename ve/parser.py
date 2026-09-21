"""Strict, non-normalizing parser for the VE v0 surface language."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from . import ast
from .errors import (ResourceLimit, ShadowedVariable, Span, SyntaxError, VEError,
                     UnboundVariable, UnknownSymbol)
from .limits import MAX_DEPTH, MAX_IDENTIFIER_BYTES, MAX_NODES, MAX_SOURCE_BYTES

_IDENT = re.compile(r"[a-z][a-z0-9_]*", re.ASCII)
_IDENT_CONT = re.compile(r"[a-z0-9_]", re.ASCII)


@dataclass(frozen=True, slots=True)
class SourceMetadata:
    """Non-semantic source details in parser node-completion order."""

    source: str
    spans: tuple[Span, ...]
    source_names: tuple[str | None, ...]


@dataclass(frozen=True, slots=True)
class ParseResult:
    document: ast.Document
    metadata: SourceMetadata


class _Parser:
    def __init__(self, env: Any, source: str):
        self.env, self.s, self.i = env, source, 0
        self.binders: list[tuple[str, str]] = []  # outermost first
        self.spans: list[Span] = []
        self.names: list[str | None] = []
        self.nodes = 0

    def span(self, start: int, end: int | None = None) -> Span:
        end = self.i if end is None else end
        return Span(start, end, self.s.count("\n", 0, start) + 1,
                    start - self.s.rfind("\n", 0, start))

    def error(self, message: str, start: int | None = None, cls=SyntaxError):
        p = self.i if start is None else start
        raise cls(message, span=self.span(p, min(len(self.s), max(p + 1, self.i))))

    def literal(self, value: str) -> None:
        if not self.s.startswith(value, self.i):
            self.error(f"expected {value!r}")
        self.i += len(value)

    def identifier(self, role: str) -> tuple[str, int]:
        start = self.i
        match = _IDENT.match(self.s, self.i)
        if match is None:
            self.error(f"expected {role}")
        name = match.group()
        self.i = match.end()
        if len(name) > MAX_IDENTIFIER_BYTES:
            self.error(f"{role} exceeds {MAX_IDENTIFIER_BYTES} ASCII bytes", start,
                       ResourceLimit)
        return name, start

    def node(self, start: int, value: Any, name: str | None = None):
        self.nodes += 1
        if self.nodes > MAX_NODES:
            self.error(f"document exceeds {MAX_NODES} AST nodes", start, ResourceLimit)
        # Preorder is useful to diagnostics even though nodes complete postorder.
        self.spans.append(self.span(start))
        self.names.append(name)
        return value

    def term(self):
        start = self.i
        if self.s.startswith("@", self.i):
            self.i += 1
            name, pos = self.identifier("constant identifier")
            if name not in self.env.constants:
                self.error(f"unknown constant {name!r}", pos, UnknownSymbol)
            return ast.Const(name)
        name, pos = self.identifier("term")
        from .environment import RESERVED
        if name in RESERVED:
            self.error(f"reserved word {name!r} cannot be a term", pos)
        for index, (active, _sort) in enumerate(reversed(self.binders)):
            if active == name:
                return ast.Var(index)
        self.error(f"unbound variable {name!r}", pos, UnboundVariable)

    def formula(self, depth: int = 1):
        if depth > MAX_DEPTH:
            self.error(f"formula exceeds nesting limit {MAX_DEPTH}", cls=ResourceLimit)
        start = self.i
        if self.s.startswith("true", self.i) and not _IDENT_CONT.match(self.s, self.i + 4):
            self.i += 4
            return self.node(start, ast.Top())
        if self.s.startswith("false", self.i) and not _IDENT_CONT.match(self.s, self.i + 5):
            self.i += 5
            return self.node(start, ast.Bottom())
        if self.s.startswith("not (", self.i):
            self.i += 5; body = self.formula(depth + 1); self.literal(")")
            return self.node(start, ast.Not(body))
        if self.s.startswith("if (", self.i):
            self.i += 4; left = self.formula(depth + 1); self.literal("), then (")
            right = self.formula(depth + 1); self.literal(")")
            return self.node(start, ast.Implies(left, right))
        for prefix, constructor in (("for every ", ast.Forall),
                                    ("there exists ", ast.Exists)):
            if self.s.startswith(prefix, self.i):
                self.i += len(prefix)
                sort, sort_pos = self.identifier("sort identifier")
                if sort not in self.env.sorts:
                    self.error(f"unknown sort {sort!r}", sort_pos, UnknownSymbol)
                self.literal(" ")
                name, name_pos = self.identifier("binder name")
                reserved = getattr(self.env, "RESERVED", None)
                if reserved is None:
                    try:
                        from .environment import RESERVED
                        reserved = RESERVED
                    except ImportError:
                        reserved = frozenset()
                schema = set(self.env.sorts) | set(self.env.predicates) | set(self.env.constants)
                # x<digits> is reserved for generated binders, but canonical VE
                # must itself parse, so the restriction applies to schema names.
                if name in reserved or name in schema:
                    self.error(f"invalid binder name {name!r}", name_pos)
                if any(active == name for active, _ in self.binders):
                    self.error(f"binder {name!r} shadows an active binder", name_pos,
                               ShadowedVariable)
                self.literal(", (")
                self.binders.append((name, sort))
                body = self.formula(depth + 1)
                self.binders.pop()
                self.literal(")")
                return self.node(start, constructor(sort, body), name)
        if self.s.startswith("(", self.i):
            self.i += 1; left = self.formula(depth + 1)
            if self.s.startswith(") and (", self.i):
                self.i += 7; constructor = ast.And
            elif self.s.startswith(") or (", self.i):
                self.i += 6; constructor = ast.Or
            else:
                self.error("expected ') and (' or ') or ('")
            right = self.formula(depth + 1); self.literal(")")
            return self.node(start, constructor(left, right))

        left = self.term()
        if self.s.startswith(" is ", self.i):
            self.i += 4; pred, pos = self.identifier("unary predicate")
            decl = self.env.predicates.get(pred)
            if decl is None or len(decl.arguments) != 1:
                self.error(f"unknown unary predicate {pred!r}", pos, UnknownSymbol)
            return self.node(start, ast.Unary(pred, left))
        if self.s.startswith(" equals ", self.i):
            self.i += 8
            return self.node(start, ast.Eq(left, self.term()))
        self.literal(" ")
        pred, pos = self.identifier("binary predicate")
        decl = self.env.predicates.get(pred)
        if decl is None or len(decl.arguments) != 2:
            self.error(f"unknown binary predicate {pred!r}", pos, UnknownSymbol)
        self.literal(" ")
        return self.node(start, ast.Binary(pred, left, self.term()))

    def document(self) -> ast.Document:
        formulas = []
        if not self.s:
            self.error("document must contain at least one statement", 0)
        while self.i < len(self.s):
            formulas.append(self.formula())
            self.literal(".\n")
        return ast.Document(tuple(formulas))


def parse_with_metadata(env: Any, source: str | bytes) -> ParseResult:
    if isinstance(source, bytes):
        if len(source) > MAX_SOURCE_BYTES:
            raise ResourceLimit(f"source exceeds {MAX_SOURCE_BYTES} bytes")
        try:
            source = source.decode("ascii")
        except UnicodeDecodeError as exc:
            raise SyntaxError("VE semantic syntax must be ASCII",
                              span=Span(exc.start, exc.end, 1, exc.start + 1)) from exc
    elif not isinstance(source, str):
        raise TypeError("source must be str or bytes")
    else:
        try:
            encoded = source.encode("ascii")
        except UnicodeEncodeError as exc:
            raise SyntaxError("VE semantic syntax must be ASCII",
                              span=Span(exc.start, exc.end, source.count("\n", 0, exc.start)+1,
                                        exc.start-source.rfind("\n", 0, exc.start))) from exc
        if len(encoded) > MAX_SOURCE_BYTES:
            raise ResourceLimit(f"source exceeds {MAX_SOURCE_BYTES} bytes")
    parser = _Parser(env, source)
    document = parser.document()
    # Checking is intentionally after name resolution: malformed raw AST never escapes.
    try:
        ast.check_document(env, document)
    except VEError as exc:
        if exc.span is None:
            exc.span = Span(0, len(source), 1, 1)
        raise
    return ParseResult(document, SourceMetadata(source, tuple(parser.spans), tuple(parser.names)))


def parse(env: Any, source: str | bytes) -> ast.Document:
    return parse_with_metadata(env, source).document


def canonicalize(env: Any, source: str | bytes) -> str:
    from .printer import print_document
    return print_document(env, parse(env, source))


def is_canonical(env: Any, source: str | bytes) -> bool:
    try:
        text = source.decode("ascii") if isinstance(source, bytes) else source
        return canonicalize(env, source) == text
    except (UnicodeError, ValueError):
        return False
