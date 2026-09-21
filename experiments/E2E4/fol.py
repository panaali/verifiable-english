"""Small deterministic renderer for VE's indexed wire AST.

This is an experiment display adapter, not a parser or semantic checker. Input
must be the tagged arrays produced by ``ve.ast.formula_to_data``.
"""
from __future__ import annotations
from typing import Any
from ve import ast


class FOLRenderError(ValueError):
    pass


def render_formula(data: Any) -> str:
    """Render a VE ``Formula`` or ``formula_to_data`` value as ASCII FOL."""
    if isinstance(data, (ast.Top, ast.Bottom, ast.Unary, ast.Binary, ast.Eq, ast.Not,
                         ast.And, ast.Or, ast.Implies, ast.Forall, ast.Exists)):
        return _ast_formula(data, ())
    return _formula(data, ())


def render_sequent(premises: list[Any] | tuple[Any, ...], conclusion: Any) -> str:
    left = ", ".join(render_formula(p) for p in premises)
    return f"{left} |- {render_formula(conclusion)}" if left else f"|- {render_formula(conclusion)}"


def _node(data: Any, tag: str, arity: int) -> None:
    if type(data) is not list or len(data) != arity or data[0] != tag:
        raise FOLRenderError(f"malformed {tag} node")


def _term(data: Any, scope: tuple[str, ...]) -> str:
    if type(data) is not list or not data or type(data[0]) is not str:
        raise FOLRenderError("malformed term")
    if data[0] == "const":
        _node(data, "const", 2)
        if type(data[1]) is not str: raise FOLRenderError("constant name must be text")
        return data[1]
    if data[0] == "var":
        _node(data, "var", 2)
        index = data[1]
        if type(index) is not int or index < 0 or index >= len(scope):
            raise FOLRenderError("variable index is outside renderer scope")
        return scope[index]
    raise FOLRenderError(f"unknown term tag: {data[0]!r}")


def _ast_term(term: ast.Term, scope: tuple[str, ...]) -> str:
    if isinstance(term, ast.Const): return term.name
    if isinstance(term, ast.Var) and type(term.index) is int and 0 <= term.index < len(scope):
        return scope[term.index]
    raise FOLRenderError("invalid or out-of-scope AST term")


def _ast_formula(node: ast.Formula, scope: tuple[str, ...]) -> str:
    if isinstance(node, ast.Top): return "true"
    if isinstance(node, ast.Bottom): return "false"
    if isinstance(node, ast.Unary): return f"{node.predicate}({_ast_term(node.term, scope)})"
    if isinstance(node, ast.Binary):
        return f"{node.predicate}({_ast_term(node.left, scope)}, {_ast_term(node.right, scope)})"
    if isinstance(node, ast.Eq): return f"({_ast_term(node.left, scope)} = {_ast_term(node.right, scope)})"
    if isinstance(node, ast.Not): return f"not ({_ast_formula(node.body, scope)})"
    if isinstance(node, (ast.And, ast.Or, ast.Implies)):
        op = {ast.And: "and", ast.Or: "or", ast.Implies: "->"}[type(node)]
        return f"({_ast_formula(node.left, scope)} {op} {_ast_formula(node.right, scope)})"
    if isinstance(node, (ast.Forall, ast.Exists)):
        variable=f"x{len(scope)}"; quantifier="forall" if isinstance(node, ast.Forall) else "exists"
        return f"({quantifier} {variable}:{node.sort}. {_ast_formula(node.body, (variable,) + scope)})"
    raise FOLRenderError(f"unknown AST formula: {type(node).__name__}")


def _formula(data: Any, scope: tuple[str, ...]) -> str:
    if type(data) is not list or not data or type(data[0]) is not str:
        raise FOLRenderError("malformed formula")
    tag = data[0]
    if tag in {"top", "bottom"}:
        _node(data, tag, 1); return "true" if tag == "top" else "false"
    if tag == "unary":
        _node(data, tag, 3); return f"{data[1]}({_term(data[2], scope)})"
    if tag == "binary":
        _node(data, tag, 4); return f"{data[1]}({_term(data[2], scope)}, {_term(data[3], scope)})"
    if tag == "eq":
        _node(data, tag, 3); return f"({_term(data[1], scope)} = {_term(data[2], scope)})"
    if tag == "not":
        _node(data, tag, 2); return f"not ({_formula(data[1], scope)})"
    if tag in {"and", "or", "implies"}:
        _node(data, tag, 3)
        op = {"and": "and", "or": "or", "implies": "->"}[tag]
        return f"({_formula(data[1], scope)} {op} {_formula(data[2], scope)})"
    if tag in {"forall", "exists"}:
        _node(data, tag, 3)
        if type(data[1]) is not str: raise FOLRenderError("quantifier sort must be text")
        variable = f"x{len(scope)}"
        quantifier = "forall" if tag == "forall" else "exists"
        return f"({quantifier} {variable}:{data[1]}. {_formula(data[2], (variable,) + scope)})"
    raise FOLRenderError(f"unknown formula tag: {tag!r}")
