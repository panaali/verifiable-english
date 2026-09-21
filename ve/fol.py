"""Explicit adapters from formal first-order AST data to typed VE.

No sort, declaration, quantifier, or premise is inferred by this module.
"""
from __future__ import annotations

from typing import Any, Mapping

from . import ast
from .errors import ResourceLimit, SyntaxError
from .limits import MAX_DEPTH, MAX_NODES
from .wire import canonical_json
from .printer import NaturalView, natural_document, print_document


def _fail(message: str, path: str) -> None:
    raise SyntaxError(message, path=path)



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
    canonical_json(value)  # Validate the complete wire package before discarding source names.
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
