"""Explicit adapters from formal first-order AST data to typed VE.

No sort, declaration, quantifier, or premise is inferred by this module.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from . import ast
from .errors import ResourceLimit, SyntaxError
from .limits import MAX_DEPTH, MAX_INDEX, MAX_NODES
from .printer import NaturalView, natural_document, print_document


def _fail(message: str, path: str) -> None:
    raise SyntaxError(message, path=path)


def _array(value: Any, length: int, path: str) -> list[Any]:
    if not isinstance(value, list) or len(value) != length:
        _fail(f"expected tagged array of length {length}", path)
    return value


def term_from_indexed_json(value: Any, *, path: str = "", depth: int = 0):
    if depth > MAX_DEPTH: _fail("term nesting limit exceeded", path)
    if not isinstance(value, list) or not value or not isinstance(value[0], str):
        _fail("expected tagged term array", path)
    if value[0] == "var":
        _array(value, 2, path)
        if isinstance(value[1], bool) or not isinstance(value[1], int) or not 0 <= value[1] <= MAX_INDEX:
            _fail("variable index must be a bounded nonnegative integer", path + "/1")
        return ast.Var(value[1])
    if value[0] == "const":
        _array(value, 2, path)
        if not isinstance(value[1], str): _fail("constant id must be a string", path + "/1")
        return ast.Const(value[1])
    _fail(f"unknown term tag {value[0]!r}", path + "/0")


def formula_from_indexed_json(value: Any, *, path: str = "", depth: int = 0,
                              _count: list[int] | None = None):
    if depth > MAX_DEPTH: raise ResourceLimit("formula nesting limit exceeded", path=path)
    count = [0] if _count is None else _count
    count[0] += 1
    if count[0] > MAX_NODES: raise ResourceLimit("AST node limit exceeded", path=path)
    if not isinstance(value, list) or not value or not isinstance(value[0], str):
        _fail("expected tagged formula array", path)
    tag = value[0]
    if tag in ("top", "bottom"):
        _array(value, 1, path); return ast.Top() if tag == "top" else ast.Bottom()
    if tag == "unary":
        _array(value, 3, path); return ast.Unary(value[1], term_from_indexed_json(value[2], path=path+"/2"))
    if tag == "binary":
        _array(value, 4, path); return ast.Binary(value[1], term_from_indexed_json(value[2], path=path+"/2"), term_from_indexed_json(value[3], path=path+"/3"))
    if tag == "eq":
        _array(value, 3, path); return ast.Eq(term_from_indexed_json(value[1], path=path+"/1"), term_from_indexed_json(value[2], path=path+"/2"))
    if tag == "not":
        _array(value, 2, path); return ast.Not(formula_from_indexed_json(value[1], path=path+"/1", depth=depth+1, _count=count))
    binary = {"and": ast.And, "or": ast.Or, "implies": ast.Implies}
    if tag in binary:
        _array(value, 3, path)
        return binary[tag](formula_from_indexed_json(value[1], path=path+"/1", depth=depth+1, _count=count), formula_from_indexed_json(value[2], path=path+"/2", depth=depth+1, _count=count))
    binders = {"forall": ast.Forall, "exists": ast.Exists}
    if tag in binders:
        _array(value, 3, path)
        if not isinstance(value[1], str): _fail("binder sort must be a string", path+"/1")
        return binders[tag](value[1], formula_from_indexed_json(value[2], path=path+"/2", depth=depth+1, _count=count))
    _fail(f"unknown formula tag {tag!r}", path + "/0")


def document_from_indexed_json(env: Any, value: Any) -> ast.Document:
    """Decode the specified indexed wire AST and validate it against *env*."""
    # The core decoder is the one trusted implementation of indexed wire data.
    return ast.document_from_data(env, value)


def document_from_named_fol(env: Any, value: Mapping[str, Any]) -> ast.Document:
    """Import a practical named FOL object with explicit variable sorts.

    Shape: ``{"formulas": [...]} ``. Formula objects have ``op`` and operands;
    binders require ``sort``, ``variable``, and ``body``. Terms are
    ``{"var": name}`` or ``{"const": id}``.
    """
    if not isinstance(value, Mapping) or set(value) != {"formulas"} or not isinstance(value["formulas"], list) or not value["formulas"]:
        _fail("named FOL document requires only a nonempty 'formulas' array", "")
    count = [0]
    def term(raw, scope, path):
        if not isinstance(raw, Mapping) or len(raw) != 1: _fail("invalid named term", path)
        if "const" in raw and isinstance(raw["const"], str): return ast.Const(raw["const"])
        if "var" in raw and isinstance(raw["var"], str):
            try: return ast.Var(list(reversed(scope)).index(raw["var"]))
            except ValueError: _fail(f"unbound variable {raw['var']!r}", path)
        _fail("term requires string 'var' or 'const'", path)
    def formula(raw, scope, path, depth=0):
        if depth > MAX_DEPTH: raise ResourceLimit("formula nesting limit exceeded", path=path)
        count[0] += 1
        if count[0] > MAX_NODES: raise ResourceLimit("AST node limit exceeded", path=path)
        if not isinstance(raw, Mapping) or not isinstance(raw.get("op"), str): _fail("formula requires string 'op'", path)
        op = raw["op"]
        expected = {
            "top":{"op"}, "bottom":{"op"}, "unary":{"op","predicate","term"},
            "binary":{"op","predicate","left","right"}, "eq":{"op","left","right"},
            "not":{"op","body"}, "and":{"op","left","right"}, "or":{"op","left","right"},
            "implies":{"op","left","right"}, "forall":{"op","sort","variable","body"},
            "exists":{"op","sort","variable","body"}}
        if op not in expected or set(raw) != expected[op]: _fail(f"invalid fields for operation {op!r}", path)
        if op == "top": return ast.Top()
        if op == "bottom": return ast.Bottom()
        if op == "unary": return ast.Unary(raw["predicate"], term(raw["term"],scope,path+"/term"))
        if op == "binary": return ast.Binary(raw["predicate"],term(raw["left"],scope,path+"/left"),term(raw["right"],scope,path+"/right"))
        if op == "eq": return ast.Eq(term(raw["left"],scope,path+"/left"),term(raw["right"],scope,path+"/right"))
        if op == "not": return ast.Not(formula(raw["body"],scope,path+"/body",depth+1))
        if op in ("and","or","implies"):
            cls={"and":ast.And,"or":ast.Or,"implies":ast.Implies}[op]
            return cls(formula(raw["left"],scope,path+"/left",depth+1),formula(raw["right"],scope,path+"/right",depth+1))
        if not isinstance(raw["sort"],str) or not isinstance(raw["variable"],str): _fail("binder sort and variable must be strings",path)
        cls=ast.Forall if op=="forall" else ast.Exists
        return cls(raw["sort"],formula(raw["body"],[*scope,raw["variable"]],path+"/body",depth+1))
    document=ast.Document(tuple(formula(v,[],f"/formulas/{i}") for i,v in enumerate(value["formulas"])))
    return ast.check_document(env,document)


def render_fol(env: Any, value: ast.Document | list[Any] | Mapping[str, Any], *, view: str = "canonical") -> str | NaturalView:
    """Validate and render an internal, indexed-wire, or named FOL document."""
    if isinstance(value, ast.Document):
        document=value
        ast.check_document(env,document)
    elif isinstance(value,list): document=document_from_indexed_json(env,value)
    else: document=document_from_named_fol(env,value)
    if view == "canonical": return print_document(env,document)
    if view == "natural": return natural_document(env,document)
    raise ValueError("view must be 'canonical' or 'natural'")
