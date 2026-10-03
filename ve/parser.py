"""Strict, non-normalizing parser for the VE v0 surface language."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from .assurance import semantic_entry
from . import ast
from .errors import (ResourceLimit, ShadowedVariable, Span, SyntaxError, VEError,
                     UnboundVariable, UnknownSymbol)
from .limits import MAX_DEPTH, MAX_IDENTIFIER_BYTES, MAX_NODES, MAX_SOURCE_BYTES

_IDENT = re.compile(r"[a-z][a-z0-9_]*", re.ASCII)
_IDENT_CONT = re.compile(r"[a-z0-9_]", re.ASCII)
_NUMERAL = re.compile(r"-?(?:0|[1-9][0-9]*)", re.ASCII)


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
        # Whether a definitions@0 sugar production was read (`no`, `every ...
        # that is`, `iff`, `define`); no Lean surface parser has them.
        self.sugar = False

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
        # Metadata follows node-completion order; semantic nodes carry no spans.
        self.spans.append(self.span(start))
        self.names.append(name)
        return value

    def numeral(self):
        start = self.i
        match = _NUMERAL.match(self.s, self.i)
        if match is None:
            self.error("expected an integer numeral")
        text = match.group()
        if len(text) > ast.MAX_NUMERAL_CHARS:
            self.error(f"numeral exceeds {ast.MAX_NUMERAL_CHARS} characters", start, ResourceLimit)
        if text == "-0" or (self.i + len(text) < len(self.s) and self.s[self.i + len(text)].isdigit()):
            self.error("non-canonical integer numeral", start)
        self.i = match.end()
        return int(text)

    def term(self, depth: int = 1):
        start = self.i
        if getattr(self.env, "order", False):
            if depth > MAX_DEPTH:
                self.error(f"term exceeds nesting limit {MAX_DEPTH}", cls=ResourceLimit)
            char = self.s[self.i:self.i + 1]
            nxt = self.s[self.i + 1:self.i + 2]
            if char.isdigit() or (char == "-" and nxt.isdigit()):
                return ast.Num(self.numeral())
            if char == "-":
                self.i += 1
                return ast.Scale(-1, self.term(depth + 1))
            if char == "[":
                self.i += 1
                left = self.term(depth + 1)
                if self.s.startswith(" * ", self.i):
                    if type(left) is not ast.Num:
                        self.error("a scaling coefficient must be an integer numeral", start)
                    self.i += 3
                    right = self.term(depth + 1)
                    self.literal("]")
                    return ast.Scale(left.value, right)
                if self.s.startswith(" + ", self.i):
                    self.i += 3
                    right = self.term(depth + 1)
                    self.literal("]")
                    return ast.Add(left, right)
                if self.s.startswith(" - ", self.i):
                    self.i += 3
                    right = self.term(depth + 1)
                    self.literal("]")
                    return ast.Add(left, ast.Scale(-1, right))
                self.error("expected ' + ', ' - ' or ' * '")
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

    def closure_binder(self, sort):
        from .environment import RESERVED
        name, pos = self.identifier("closure binder")
        if name in RESERVED or name in self.env.sorts or name in self.env.predicates or name in self.env.constants:
            self.error(f"invalid binder name {name!r}", pos)
        if any(active == name for active, _ in self.binders):
            self.error(f"binder {name!r} shadows an active binder", pos, ShadowedVariable)
        self.binders.append((name, sort))
        return name

    def formula(self, depth: int = 1):
        if depth > MAX_DEPTH:
            self.error(f"formula exceeds nesting limit {MAX_DEPTH}", cls=ResourceLimit)
        start = self.i
        definitions = "definitions@0" in self.env.profiles
        from .surface.registry import strict_dispatch
        matched = strict_dispatch(self.s[self.i:], self.env)
        if matched is not None:
            return matched[1].strict_parser_hook(self, depth)
        if self.s.startswith(("tc[", "rtc["), self.i):
            kind = "star" if self.s.startswith("rtc[", self.i) else "plus"
            self.i += 4 if kind == "star" else 3
            symbol, pos = self.identifier("closure relation or sort")
            if self.s.startswith("]", self.i):
                edge = ast.Named(symbol)
            else:
                if symbol not in self.env.sorts:
                    self.error(f"unknown sort {symbol!r}", pos, UnknownSymbol)
                self.literal(" ")
                self.closure_binder(symbol)
                self.literal(", ")
                self.closure_binder(symbol)
                self.literal(" | (")
                body = self.formula(depth + 1)
                self.literal(")")
                del self.binders[-2:]
                edge = ast.Body(symbol, body)
            self.literal("](")
            left = self.term()
            self.literal(", ")
            right = self.term()
            self.literal(")")
            return self.node(start, ast.Reach(kind, edge, left, right))
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
        if definitions and self.s.startswith("no ", self.i):
            self.sugar = True
            self.i += 3
            sort, pos = self.identifier("sort identifier")
            if sort not in self.env.sorts:
                self.error(f"unknown sort {sort!r}", pos, UnknownSymbol)
            self.literal(" is ")
            predicate, pos = self.identifier("unary predicate")
            decl = self.env.predicates.get(predicate)
            if decl is None or decl.arguments != (sort,):
                self.error(f"unknown unary predicate {predicate!r}", pos, UnknownSymbol)
            return self.node(start, ast.Forall(sort, ast.Not(ast.Unary(predicate, ast.Var(0)))))
        if definitions and self.s.startswith("every ", self.i):
            from .environment import RESERVED
            self.sugar = True
            self.i += 6
            sort, pos = self.identifier("sort identifier")
            if sort not in self.env.sorts:
                self.error(f"unknown sort {sort!r}", pos, UnknownSymbol)
            self.literal(" ")
            name, pos = self.identifier("binder name")
            if name in RESERVED or name in self.env.sorts or name in self.env.predicates or name in self.env.constants or any(
                    active == name for active, _ in self.binders):
                self.error(f"invalid binder name {name!r}", pos)
            self.literal(" that is ")
            predicate, pos = self.identifier("unary predicate")
            decl = self.env.predicates.get(predicate)
            if decl is None or decl.arguments != (sort,):
                self.error(f"unknown unary predicate {predicate!r}", pos, UnknownSymbol)
            self.literal(", (")
            self.binders.append((name, sort))
            body = self.formula(depth + 1)
            self.binders.pop()
            self.literal(")")
            guard = ast.Unary(predicate, ast.Var(0))
            return self.node(start, ast.Forall(sort, ast.Implies(guard, body)), name)
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
            elif definitions and self.s.startswith(") iff (", self.i):
                self.sugar = True
                self.i += 7; constructor = None
            else:
                self.error("expected ') and (' or ') or ('")
            right = self.formula(depth + 1); self.literal(")")
            return self.node(start, constructor(left, right) if constructor is not None else
                             ast.And(ast.Implies(left, right), ast.Implies(right, left)))

        if "nary@0" in self.env.profiles:
            match = _IDENT.match(self.s, self.i)
            if match is not None and self.s.startswith("(", match.end()):
                predicate, position = self.identifier("n-ary predicate")
                declaration = self.env.predicates.get(predicate)
                if declaration is None or not 3 <= len(declaration.arguments) <= 6:
                    self.error(f"unknown n-ary predicate {predicate!r}", position, UnknownSymbol)
                self.literal("(")
                terms = [self.term()]
                while self.s.startswith(", ", self.i):
                    self.i += 2
                    terms.append(self.term())
                    if len(terms) > 6:
                        self.error("n-ary atom exceeds six arguments", start)
                self.literal(")")
                return self.node(start, ast.Atom(predicate, tuple(terms)))

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
        if getattr(self.env, "order", False):
            for operator, constructor in ((" <= ", ast.Le), (" < ", ast.Lt)):
                if self.s.startswith(operator, self.i):
                    self.i += len(operator)
                    return self.node(start, constructor(left, self.term()))
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
            if "definitions@0" in self.env.profiles and self.s.startswith("define ", self.i):
                from .environment import RESERVED
                from .definitions import Definition, premise
                self.sugar = True
                self.i += 7
                predicate, pos = self.identifier("defined predicate")
                if predicate not in self.env.definition_entries:
                    self.error(f"unknown defined predicate {predicate!r}", pos, UnknownSymbol)
                sorts = self.env.predicates[predicate].arguments
                self.literal("(")
                names = []
                for index, sort in enumerate(sorts):
                    if index:
                        self.literal(", ")
                    name, pos = self.identifier("definition argument")
                    if name in RESERVED or name in self.env.sorts or name in self.env.predicates or name in self.env.constants or name in names:
                        self.error(f"repeated definition argument {name!r}", pos)
                    names.append(name)
                    self.binders.append((name, sort))
                self.literal(") as (")
                body = self.formula()
                self.literal(")")
                del self.binders[-len(sorts):]
                from . import ast as formula_ast
                expected = formula_ast._Decoder().decode(self.env.definition_entries[predicate]["body"])
                if body != expected:
                    self.error("definition body differs from identity-bound declaration")
                formulas.append(premise(Definition(predicate, sorts, body)))
            else:
                formulas.append(self.formula())
            self.literal(".\n")
        return ast.Document(tuple(formulas))


def _lean_parse_scope(env: Any) -> bool:
    """Whether Lean's `parse` mode takes sources over `env`: the frozen v0 and
    v0.1 envelopes, and ve.core@0.2 without statement layers."""
    from .profiles import STATEMENT_LAYERS
    if getattr(env, "language", None) in ("ve.core@0", "ve.core@0.1"):
        return True
    return (getattr(env, "language", None) == "ve.core@0.2"
            and env.unit_schema is None
            and env.alternatives is None and not STATEMENT_LAYERS & set(env.profiles))


@semantic_entry("parse")
def parse_with_metadata(env: Any, source: str | bytes) -> ParseResult:
    """Parse and type a source under the selected authority.

    Under a backend authority Lean's surface parser for the envelope's family
    decides acceptance; the Python parser reads the document and its source
    metadata, names a rejection both make, and its document must be Lean's
    (the same AST and, where Lean prints, the same canonical text).
    """
    from .backends.dispatch import authority_for, execute, note_uncompared

    def python():
        return _parse_python(env, source)

    if authority_for("parse") in ("python", "rust-experimental") or not _lean_parse_scope(env):
        note_uncompared("parse", "parse-scope")
        return python()
    return execute("parse", {"environment": env, "source": source}, python,
                   lean=lambda: _parse_lean(env, source, python))


def _parse_lean(env: Any, source: str | bytes, python) -> ParseResult:
    from .backends.lean_runner import run
    from .backends.validation import decided, key
    if "definitions@0" in env.profiles:
        # The definitions@0 surface sugar (`no`, `every ... that is`, `iff`,
        # `define`) is in no Lean surface parser: a source the Python reader
        # accepts through it keeps Python's reading (a recorded scope gap).
        # Every other source over the environment is Lean's to accept.
        try:
            result, sugar = _parse_python_marked(env, source)
        except VEError:
            sugar = False
        if sugar:
            return result
    try:
        text = source if isinstance(source, str) else source.decode("ascii")
        cache = key("parse", env.environment_id, text)
    except (UnicodeError, VEError, TypeError, ValueError, AttributeError):
        text, cache = None, None

    def same(result: ParseResult, row: dict) -> bool:
        from .printer import print_document
        if row.get("ast") != [ast._to_data(f) for f in result.document.formulas]:
            return False
        return "canonical" not in row or row["canonical"] == print_document(env, result.document)

    return decided(python, cache,
                   lambda: run("parse", [{"id": "parse", "environment": env.to_dict(), "source": text}])[0],
                   same, "a source")


def _parse_python(env: Any, source: str | bytes) -> ParseResult:
    return _parse_python_marked(env, source)[0]


def _parse_python_marked(env: Any, source: str | bytes) -> tuple[ParseResult, bool]:
    """The Python reading, and whether it read a definitions@0 sugar production."""
    if isinstance(source, bytes):
        if len(source) > MAX_SOURCE_BYTES:
            raise ResourceLimit(f"source exceeds {MAX_SOURCE_BYTES} bytes")
        try:
            source = source.decode("ascii")
        except UnicodeDecodeError as exc:
            raise SyntaxError("VE semantic syntax must be ASCII",
                              span=Span(exc.start, exc.end, source.count(b"\n", 0, exc.start) + 1,
                                        exc.start - source.rfind(b"\n", 0, exc.start))) from exc
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
    return (ParseResult(document, SourceMetadata(source, tuple(parser.spans), tuple(parser.names))),
            parser.sugar)


@semantic_entry("parse")
def parse(env: Any, source: str | bytes) -> ast.Document:
    return parse_with_metadata(env, source).document


@semantic_entry("parse")
def canonicalize(env: Any, source: str | bytes) -> str:
    from .printer import print_document
    return print_document(env, parse(env, source))


@semantic_entry("parse")
def is_canonical(env: Any, source: str | bytes) -> bool:
    try:
        text = source.decode("ascii") if isinstance(source, bytes) else source
        return canonicalize(env, source) == text
    except (UnicodeError, ValueError):
        return False
