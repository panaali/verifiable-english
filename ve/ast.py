"""Indexed syntax and its extrinsic type/scope checker.

Constructors are raw immutable nodes for convenient FOL adapters. A node is a
typed claim only after checking under its environment. Every public semantic
consumer checks its inputs; Python type annotations are not validation evidence.
"""
from dataclasses import dataclass
from typing import TypeAlias

from .environment import Environment
from .errors import ResourceLimit, SyntaxError, TypeMismatch, UnboundVariable, UnknownSymbol, VEError
from .limits import MAX_DEPTH, MAX_INDEX, MAX_NODES
from .wire import loads_json


@dataclass(frozen=True, slots=True)
class Var:
    index: int


@dataclass(frozen=True, slots=True)
class Const:
    name: str


Term: TypeAlias = Var | Const


@dataclass(frozen=True, slots=True)
class Top:
    pass


@dataclass(frozen=True, slots=True)
class Bottom:
    pass


@dataclass(frozen=True, slots=True)
class Unary:
    predicate: str
    term: Term


@dataclass(frozen=True, slots=True)
class Binary:
    predicate: str
    left: Term
    right: Term


@dataclass(frozen=True, slots=True)
class Eq:
    left: Term
    right: Term


@dataclass(frozen=True, slots=True)
class Not:
    body: "Formula"


@dataclass(frozen=True, slots=True)
class And:
    left: "Formula"
    right: "Formula"


@dataclass(frozen=True, slots=True)
class Or:
    left: "Formula"
    right: "Formula"


@dataclass(frozen=True, slots=True)
class Implies:
    left: "Formula"
    right: "Formula"


@dataclass(frozen=True, slots=True)
class Forall:
    sort: str
    body: "Formula"


@dataclass(frozen=True, slots=True)
class Exists:
    sort: str
    body: "Formula"


Formula: TypeAlias = Top | Bottom | Unary | Binary | Eq | Not | And | Or | Implies | Forall | Exists


@dataclass(frozen=True, slots=True)
class Document:
    formulas: tuple[Formula, ...]

    def __post_init__(self):
        if type(self.formulas) not in (tuple, list):
            raise VEError("Document formulas must be a tuple or list")
        object.__setattr__(self, "formulas", tuple(self.formulas))


class _Checker:
    def __init__(self, env):
        if not isinstance(env, Environment):
            raise VEError("Expected a validated Environment")
        self.env, self.nodes = env, 0

    def tick(self):
        self.nodes += 1
        if self.nodes > MAX_NODES:
            raise ResourceLimit("AST exceeds 10,000 nodes")

    def term(self, node, context):
        self.tick()
        if type(node) is Var:
            if type(node.index) is not int or not 0 <= node.index <= MAX_INDEX:
                raise UnboundVariable("Variable index must be a bounded nonnegative integer (not Boolean)")
            if node.index >= len(context):
                raise UnboundVariable(f"Variable index {node.index} is outside its scope")
            return context[node.index]
        if type(node) is Const:
            if type(node.name) is not str or node.name not in self.env.constants:
                raise UnknownSymbol(f"Unknown constant {node.name!r}")
            return self.env.constants[node.name].sort
        raise TypeMismatch("Expected a variable or constant term")

    def formula(self, node, context=(), depth=1):
        self.tick()
        if depth > MAX_DEPTH:
            raise ResourceLimit("Formula exceeds 64 nesting levels")
        kind = type(node)
        if kind in (Top, Bottom):
            return
        if kind in (Unary, Binary):
            p = node.predicate
            if type(p) is not str or p not in self.env.predicates:
                raise UnknownSymbol(f"Unknown predicate {p!r}")
            terms = (node.term,) if kind is Unary else (node.left, node.right)
            signature = self.env.predicates[p].arguments
            if len(signature) != len(terms):
                raise TypeMismatch(f"Predicate {p!r} has arity {len(signature)}, not {len(terms)}")
            actual = tuple(self.term(t, context) for t in terms)
            if actual != signature:
                raise TypeMismatch(f"Predicate {p!r} expects {signature}, received {actual}")
        elif kind is Eq:
            left, right = self.term(node.left, context), self.term(node.right, context)
            if left != right:
                raise TypeMismatch(f"Equality requires one sort, received {left!r} and {right!r}")
        elif kind is Not:
            self.formula(node.body, context, depth + 1)
        elif kind in (And, Or, Implies):
            self.formula(node.left, context, depth + 1)
            self.formula(node.right, context, depth + 1)
        elif kind in (Forall, Exists):
            if type(node.sort) is not str or node.sort not in self.env.sorts:
                raise UnknownSymbol(f"Unknown binder sort {node.sort!r}")
            self.formula(node.body, (node.sort,) + context, depth + 1)
        else:
            raise TypeMismatch("Unknown formula constructor")


def check_formula(env: Environment, formula: Formula) -> Formula:
    """Check a closed formula. Open formulas are never accepted as claims."""
    _Checker(env).formula(formula)
    return formula


def check_document(env: Environment, document: Document) -> Document:
    if type(document) is not Document or not document.formulas:
        raise SyntaxError("A document must contain at least one formula")
    checker = _Checker(env)
    for formula in document.formulas:
        checker.formula(formula)
    return document


def _to_data(node):
    kind = type(node)
    if kind is Var:
        return ["var", node.index]
    if kind is Const:
        return ["const", node.name]
    if kind in (Top, Bottom):
        return ["top" if kind is Top else "bottom"]
    if kind is Unary:
        return ["unary", node.predicate, _to_data(node.term)]
    if kind is Binary:
        return ["binary", node.predicate, _to_data(node.left), _to_data(node.right)]
    if kind is Eq:
        return ["eq", _to_data(node.left), _to_data(node.right)]
    if kind is Not:
        return ["not", _to_data(node.body)]
    if kind in (And, Or, Implies):
        return [{And: "and", Or: "or", Implies: "implies"}[kind], _to_data(node.left), _to_data(node.right)]
    return ["forall" if kind is Forall else "exists", node.sort, _to_data(node.body)]


def formula_to_data(env: Environment, formula: Formula):
    check_formula(env, formula)
    return _to_data(formula)


def document_to_data(env: Environment, document: Document):
    check_document(env, document)
    return [_to_data(f) for f in document.formulas]


class _Decoder:
    def __init__(self):
        self.nodes = 0

    def decode(self, data, depth=1, term=False):
        self.nodes += 1
        if self.nodes > MAX_NODES or depth > MAX_DEPTH + (1 if term else 0):
            raise ResourceLimit("AST exceeds depth or node budget")
        if type(data) is not list or not data or type(data[0]) is not str:
            raise SyntaxError("AST nodes must be nonempty tagged JSON arrays")
        tag = data[0]
        arities = {"var": 2, "const": 2} if term else {"top": 1, "bottom": 1, "unary": 3,
                   "binary": 4, "eq": 3, "not": 2, "and": 3, "or": 3, "implies": 3,
                   "forall": 3, "exists": 3}
        if tag not in arities or len(data) != arities[tag]:
            raise SyntaxError(f"Unknown AST tag or incorrect arity: {tag!r}")
        if tag == "var":
            if type(data[1]) is not int or not 0 <= data[1] <= MAX_INDEX:
                raise UnboundVariable("Invalid variable index")
            return Var(data[1])
        if tag == "const":
            return Const(data[1])
        if tag in ("top", "bottom"):
            return Top() if tag == "top" else Bottom()
        if tag == "unary":
            return Unary(data[1], self.decode(data[2], depth + 1, True))
        if tag == "binary":
            return Binary(data[1], self.decode(data[2], depth + 1, True), self.decode(data[3], depth + 1, True))
        if tag == "eq":
            return Eq(self.decode(data[1], depth + 1, True), self.decode(data[2], depth + 1, True))
        if tag == "not":
            return Not(self.decode(data[1], depth + 1))
        if tag in ("and", "or", "implies"):
            return {"and": And, "or": Or, "implies": Implies}[tag](
                self.decode(data[1], depth + 1), self.decode(data[2], depth + 1))
        return (Forall if tag == "forall" else Exists)(data[1], self.decode(data[2], depth + 1))


def formula_from_data(env: Environment, data) -> Formula:
    return check_formula(env, _Decoder().decode(data))


def document_from_data(env: Environment, data) -> Document:
    if type(data) is not list or not data:
        raise SyntaxError("A document AST must be a nonempty array of formulas")
    decoder = _Decoder()
    return check_document(env, Document(tuple(decoder.decode(f) for f in data)))


def doc_from_json(env: Environment, data: str | bytes) -> Document:
    return document_from_data(env, loads_json(data))
