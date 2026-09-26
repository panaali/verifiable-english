"""Indexed syntax and its extrinsic type/scope checker.

Constructors are raw immutable nodes for convenient FOL adapters. A node is a
typed claim only after checking under its environment. Every public semantic
consumer checks its inputs; Python type annotations are not validation evidence.
"""
from dataclasses import dataclass
import re
from typing import TypeAlias

from .environment import Environment
from .errors import ResourceLimit, SyntaxError, TypeMismatch, UnboundVariable, UnknownSymbol, UnsupportedProfile, VEError
from .limits import MAX_DEPTH, MAX_INDEX, MAX_NODES
from .wire import loads_json


@dataclass(frozen=True, slots=True)
class Var:
    index: int


@dataclass(frozen=True, slots=True)
class Const:
    name: str


@dataclass(frozen=True, slots=True)
class Num:
    """An integer numeral (order@0). Wire form: canonical decimal string."""
    value: int


@dataclass(frozen=True, slots=True)
class Add:
    left: "Term"
    right: "Term"


@dataclass(frozen=True, slots=True)
class Scale:
    """Multiplication by a literal integer; `-t` is Scale(-1, t), `t - u` is Add(t, Scale(-1, u))."""
    coefficient: int
    term: "Term"


Term: TypeAlias = Var | Const | Num | Add | Scale


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


@dataclass(frozen=True, slots=True)
class Named:
    relation: str


@dataclass(frozen=True, slots=True)
class Body:
    sort: str
    formula: "Formula"


Edge: TypeAlias = Named | Body


@dataclass(frozen=True, slots=True)
class Reach:
    kind: str  # exactly "plus" or "star"
    edge: Edge
    left: Term
    right: Term


@dataclass(frozen=True, slots=True)
class Lt:
    left: Term
    right: Term


@dataclass(frozen=True, slots=True)
class Le:
    left: Term
    right: Term


Formula: TypeAlias = Top | Bottom | Unary | Binary | Eq | Not | And | Or | Implies | Forall | Exists | Reach | Lt | Le

INT_SORT = "$int"
MAX_NUMERAL_CHARS = 40
_DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)\Z", re.ASCII)


def integer_value(value) -> int:
    """Validate a Python integer used as a numeral or coefficient (not Boolean)."""
    if type(value) is not int:
        raise TypeMismatch("Integer literals must be Python int values (not Boolean)")
    if len(str(value)) > MAX_NUMERAL_CHARS:
        raise ResourceLimit(f"Integer literal exceeds {MAX_NUMERAL_CHARS} characters")
    return value


def decimal_from_wire(text) -> int:
    """Canonical decimal string: optional minus, no leading zeros, no -0."""
    if type(text) is not str:
        raise SyntaxError("Integer wire values must be canonical decimal strings")
    if len(text) > MAX_NUMERAL_CHARS:
        raise ResourceLimit(f"Integer literal exceeds {MAX_NUMERAL_CHARS} characters")
    if not _DECIMAL.match(text) or text == "-0":
        raise SyntaxError(f"Non-canonical integer literal {text!r}")
    return int(text)


def decimal_to_wire(value: int) -> str:
    return str(integer_value(value))


@dataclass(frozen=True, slots=True)
class Document:
    formulas: tuple[Formula, ...]

    def __post_init__(self):
        if type(self.formulas) not in (tuple, list):
            raise VEError("Document formulas must be a tuple or list")
        object.__setattr__(self, "formulas", tuple(self.formulas))


class _Checker:
    def __init__(self, env, *, generated=False):
        if not isinstance(env, Environment):
            raise VEError("Expected a validated Environment")
        self.env, self.nodes, self.generated = env, 0, generated

    def tick(self):
        self.nodes += 1
        if self.nodes > MAX_NODES:
            raise ResourceLimit("AST exceeds 10,000 nodes")

    def term(self, node, context, depth=1):
        self.tick()
        if depth > MAX_DEPTH:
            raise ResourceLimit("Arithmetic term exceeds 64 nesting levels")
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
        if type(node) in (Num, Add, Scale):
            if not getattr(self.env, "order", False):
                raise UnsupportedProfile("Integer arithmetic requires order@0")
            if type(node) is Num:
                integer_value(node.value)
                return INT_SORT
            if type(node) is Scale:
                integer_value(node.coefficient)
                parts = (node.term,)
            else:
                parts = (node.left, node.right)
            for part in parts:
                if self.term(part, context, depth + 1) != INT_SORT:
                    raise TypeMismatch("Arithmetic requires integer operands")
            return INT_SORT
        raise TypeMismatch("Expected a variable or constant term")

    def formula(self, node, context=(), depth=1):
        self.tick()
        if depth > MAX_DEPTH:
            raise ResourceLimit("Formula exceeds 64 nesting levels")
        kind = type(node)
        from .surface.registry import by_node
        record = by_node(node)
        if record is not None and record.typecheck_hook is not None:
            record.typecheck_hook(self, node, context, depth)
            return
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
        elif kind is Reach:
            if not self.env.closure:
                raise UnsupportedProfile("Reach requires closure@0")
            if type(node.kind) is not str or node.kind not in ("plus", "star"):
                raise TypeMismatch("Reach kind must be plus or star")
            if type(node.edge) is Named:
                p = node.edge.relation
                if type(p) is not str or p not in self.env.predicates:
                    raise UnknownSymbol(f"Unknown closure relation {p!r}")
                args = self.env.predicates[p].arguments
                if len(args) != 2 or args[0] != args[1]:
                    raise TypeMismatch("Named closure requires a homogeneous binary relation")
                sort = args[0]
            elif type(node.edge) is Body:
                sort = node.edge.sort
                if type(sort) is not str or sort not in self.env.sorts:
                    raise UnknownSymbol(f"Unknown closure sort {sort!r}")
                self.formula(node.edge.formula, (sort, sort) + context, depth + 1)
            else:
                raise TypeMismatch("Unknown closure edge variant")
            if self.term(node.left, context) != sort or self.term(node.right, context) != sort:
                raise TypeMismatch("Closure endpoints must have the edge sort in the outer context")
        elif kind in (Lt, Le):
            if not getattr(self.env, "order", False):
                raise UnsupportedProfile("Comparisons require order@0")
            if self.term(node.left, context) != INT_SORT or self.term(node.right, context) != INT_SORT:
                raise TypeMismatch("Comparisons require integer terms")
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
            if type(node.sort) is not str or (node.sort not in self.env.sorts
                    and not (self.generated and node.sort == "$string" and "data@0" in self.env.profiles)):
                if node.sort == "$string" and "data@0" in self.env.profiles:
                    raise UnsupportedProfile("$string quantification requires data stage 2")
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
    from .surface.registry import by_node
    record = by_node(node)
    if record is not None and record.wire_encoder is not None:
        return record.wire_encoder(node, _to_data)
    if kind is Var:
        return ["var", node.index]
    if kind is Const:
        return ["const", node.name]
    if kind is Num:
        return ["num", decimal_to_wire(node.value)]
    if kind is Add:
        return ["add", _to_data(node.left), _to_data(node.right)]
    if kind is Scale:
        return ["scale", decimal_to_wire(node.coefficient), _to_data(node.term)]
    if kind in (Lt, Le):
        return ["lt" if kind is Lt else "le", _to_data(node.left), _to_data(node.right)]
    if kind in (Top, Bottom):
        return ["top" if kind is Top else "bottom"]
    if kind is Unary:
        return ["unary", node.predicate, _to_data(node.term)]
    if kind is Binary:
        return ["binary", node.predicate, _to_data(node.left), _to_data(node.right)]
    if kind is Reach:
        edge = (["named", node.edge.relation] if type(node.edge) is Named else
                ["body", node.edge.sort, _to_data(node.edge.formula)])
        return ["reach", node.kind, edge, _to_data(node.left), _to_data(node.right)]
    if kind is Eq:
        return ["eq", _to_data(node.left), _to_data(node.right)]
    if kind is Not:
        return ["not", _to_data(node.body)]
    if kind in (And, Or, Implies):
        return [record.wire_tag, _to_data(node.left), _to_data(node.right)]
    return [record.wire_tag, node.sort, _to_data(node.body)]


def formula_to_data(env: Environment, formula: Formula, *, _generated=False):
    _Checker(env, generated=_generated).formula(formula)
    return _to_data(formula)


def document_to_data(env: Environment, document: Document):
    check_document(env, document)
    return [_to_data(f) for f in document.formulas]


class _Decoder:
    def __init__(self):
        self.nodes = 0

    def decode(self, data, depth=1, term=False):
        # Formula depth and term depth are separate budgets, matching the type
        # checker (_Checker.term restarts at depth 1 under each atom) and the
        # Lean order decoder; every AST the checker accepts round-trips.
        self.nodes += 1
        if self.nodes > MAX_NODES or depth > MAX_DEPTH:
            raise ResourceLimit("AST exceeds depth or node budget")
        if type(data) is not list or not data or type(data[0]) is not str:
            raise SyntaxError("AST nodes must be nonempty tagged JSON arrays")
        tag = data[0]
        from .surface.registry import by_tag
        from .wire import formula_tag_arity
        arity = ({"var": 2, "const": 2, "num": 2, "add": 3, "scale": 3}.get(tag)
                 if term else formula_tag_arity(tag))
        if arity is None or len(data) != arity:
            raise SyntaxError(f"Unknown AST tag or incorrect arity: {tag!r}")
        record = by_tag(tag)
        if record is not None and record.wire_decoder is not None:
            return record.wire_decoder(data, self.decode, depth)
        if tag == "var":
            if type(data[1]) is not int or not 0 <= data[1] <= MAX_INDEX:
                raise UnboundVariable("Invalid variable index")
            return Var(data[1])
        if tag == "const":
            return Const(data[1])
        if tag == "num":
            return Num(decimal_from_wire(data[1]))
        if tag == "add":
            return Add(self.decode(data[1], depth + 1, True), self.decode(data[2], depth + 1, True))
        if tag == "scale":
            return Scale(decimal_from_wire(data[1]), self.decode(data[2], depth + 1, True))
        if tag in ("lt", "le"):
            return (Lt if tag == "lt" else Le)(self.decode(data[1], 1, True),
                                               self.decode(data[2], 1, True))
        if tag in ("top", "bottom"):
            return Top() if tag == "top" else Bottom()
        if tag == "unary":
            return Unary(data[1], self.decode(data[2], 1, True))
        if tag == "binary":
            return Binary(data[1], self.decode(data[2], 1, True), self.decode(data[3], 1, True))
        if tag == "eq":
            return Eq(self.decode(data[1], 1, True), self.decode(data[2], 1, True))
        if tag == "reach":
            edge = data[2]
            if type(edge) is not list or not edge or type(edge[0]) is not str:
                raise SyntaxError("Reach edge must be a tagged array")
            if edge[0] == "named" and len(edge) == 2:
                edge = Named(edge[1])
            elif edge[0] == "body" and len(edge) == 3:
                edge = Body(edge[1], self.decode(edge[2], depth + 1))
            else:
                raise SyntaxError("Unknown Reach edge tag or incorrect arity")
            return Reach(data[1], edge, self.decode(data[3], 1, True),
                         self.decode(data[4], 1, True))
        if tag == "not":
            return Not(self.decode(data[1], depth + 1))
        if tag in ("and", "or", "implies"):
            return record.node_type(
                self.decode(data[1], depth + 1), self.decode(data[2], depth + 1))
        return record.node_type(data[1], self.decode(data[2], depth + 1))


def formula_from_data(env: Environment, data) -> Formula:
    return check_formula(env, _Decoder().decode(data))


def document_from_data(env: Environment, data) -> Document:
    if type(data) is not list or not data:
        raise SyntaxError("A document AST must be a nonempty array of formulas")
    decoder = _Decoder()
    return check_document(env, Document(tuple(decoder.decode(f) for f in data)))


def doc_from_json(env: Environment, data: str | bytes) -> Document:
    return document_from_data(env, loads_json(data))
