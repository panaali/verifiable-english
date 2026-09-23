"""Explicit adapters from formal first-order AST data to typed VE.

No sort, declaration, quantifier, or premise is inferred by this module.
"""
from __future__ import annotations

from typing import Any, Mapping

from . import ast
from .environment import RESERVED, valid_identifier
from .errors import ResourceLimit, ShadowedVariable, SyntaxError, UnboundVariable
from .limits import MAX_DEPTH, MAX_IDENTIFIER_BYTES, MAX_NODES
from .wire import canonical_json
from .printer import NaturalView, natural_document, print_document


def _fail(message: str, path: str) -> None:
    raise SyntaxError(message, path=path)


def _variable_name(env: Any, value: Any, path: str) -> str:
    """Validate a source-level variable name at the named-FOL boundary."""
    if type(value) is str and len(value) > MAX_IDENTIFIER_BYTES:
        raise ResourceLimit(
            f"variable name exceeds {MAX_IDENTIFIER_BYTES} ASCII bytes", path=path
        )
    if not valid_identifier(value):
        _fail(f"invalid variable name {value!r}", path)
    schema = set(env.sorts) | set(env.predicates) | set(env.constants)
    if value in RESERVED or value in schema:
        _fail(f"invalid variable name {value!r}", path)
    return value



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
    if getattr(env, "order", False):
        from .errors import UnsupportedProfile
        raise UnsupportedProfile("The named FOL adapter does not yet cover order@0 integer terms")
    canonical_json(value)  # Validate the complete wire package before discarding source names.
    if not isinstance(value, Mapping) or set(value) != {"formulas"} or not isinstance(value["formulas"], list) or not value["formulas"]:
        _fail("named FOL document requires only a nonempty 'formulas' array", "")
    count = [0]
    def term(raw, scope, path):
        if not isinstance(raw, Mapping) or len(raw) != 1: _fail("invalid named term", path)
        if "const" in raw and isinstance(raw["const"], str): return ast.Const(raw["const"])
        if "var" in raw:
            name = _variable_name(env, raw["var"], path + "/var")
            try: return ast.Var(list(reversed(scope)).index(name))
            except ValueError:
                raise UnboundVariable(f"unbound variable {name!r}", path=path + "/var")
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
            "exists":{"op","sort","variable","body"},
            "reach":{"op","kind","edge","left","right"}}
        if op not in expected or set(raw) != expected[op]: _fail(f"invalid fields for operation {op!r}", path)
        if op == "top": return ast.Top()
        if op == "bottom": return ast.Bottom()
        if op == "unary": return ast.Unary(raw["predicate"], term(raw["term"],scope,path+"/term"))
        if op == "binary": return ast.Binary(raw["predicate"],term(raw["left"],scope,path+"/left"),term(raw["right"],scope,path+"/right"))
        if op == "eq": return ast.Eq(term(raw["left"],scope,path+"/left"),term(raw["right"],scope,path+"/right"))
        if op == "reach":
            edge = raw["edge"]
            if not isinstance(edge, Mapping): _fail("invalid reach edge", path + "/edge")
            if set(edge) == {"named"}:
                edge = ast.Named(edge["named"])
            elif set(edge) == {"sort", "source", "destination", "body"}:
                src = _variable_name(env, edge["source"], path + "/edge/source")
                dst = _variable_name(env, edge["destination"], path + "/edge/destination")
                if src == dst or src in scope or dst in scope:
                    raise ShadowedVariable("closure locals shadow a binder", path=path + "/edge")
                edge = ast.Body(edge["sort"], formula(edge["body"], [*scope, src, dst], path + "/edge/body", depth + 1))
            else: _fail("invalid reach edge fields", path + "/edge")
            return ast.Reach(raw["kind"], edge, term(raw["left"], scope, path + "/left"),
                             term(raw["right"], scope, path + "/right"))
        if op == "not": return ast.Not(formula(raw["body"],scope,path+"/body",depth+1))
        if op in ("and","or","implies"):
            cls={"and":ast.And,"or":ast.Or,"implies":ast.Implies}[op]
            return cls(formula(raw["left"],scope,path+"/left",depth+1),formula(raw["right"],scope,path+"/right",depth+1))
        if not isinstance(raw["sort"],str): _fail("binder sort must be a string",path + "/sort")
        name = _variable_name(env, raw["variable"], path + "/variable")
        if name in scope:
            raise ShadowedVariable(
                f"binder {name!r} shadows an active binder", path=path + "/variable"
            )
        cls=ast.Forall if op=="forall" else ast.Exists
        return cls(raw["sort"],formula(raw["body"],[*scope,name],path+"/body",depth+1))
    document=ast.Document(tuple(formula(v,[],f"/formulas/{i}") for i,v in enumerate(value["formulas"])))
    return ast.check_document(env,document)


def document_to_named_fol(env: Any, document: ast.Document) -> dict[str, list[dict[str, Any]]]:
    """Export *document* with deterministic preorder names and explicit sorts."""
    if getattr(env, "order", False):
        from .errors import UnsupportedProfile
        raise UnsupportedProfile("The named FOL adapter does not yet cover order@0 integer terms")
    ast.check_document(env, document)

    def term(value: ast.Term, scope: list[str]) -> dict[str, str]:
        if type(value) is ast.Var:
            return {"var": scope[value.index]}
        return {"const": value.name}

    def export_formula(value: ast.Formula, scope: list[str], counter: list[int]) -> dict[str, Any]:
        kind = type(value)
        if kind is ast.Top: return {"op": "top"}
        if kind is ast.Bottom: return {"op": "bottom"}
        if kind is ast.Unary:
            return {"op": "unary", "predicate": value.predicate,
                    "term": term(value.term, scope)}
        if kind is ast.Binary:
            return {"op": "binary", "predicate": value.predicate,
                    "left": term(value.left, scope), "right": term(value.right, scope)}
        if kind is ast.Eq:
            return {"op": "eq", "left": term(value.left, scope),
                    "right": term(value.right, scope)}
        if kind is ast.Reach:
            if type(value.edge) is ast.Named:
                edge = {"named": value.edge.relation}
            else:
                src, dst = f"x{counter[0]}", f"x{counter[0] + 1}"
                counter[0] += 2
                edge = {"sort": value.edge.sort, "source": src, "destination": dst,
                        "body": export_formula(value.edge.formula, [dst, src, *scope], counter)}
            return {"op": "reach", "kind": value.kind, "edge": edge,
                    "left": term(value.left, scope), "right": term(value.right, scope)}
        if kind is ast.Not:
            return {"op": "not", "body": export_formula(value.body, scope, counter)}
        if kind in (ast.And, ast.Or, ast.Implies):
            op = {ast.And: "and", ast.Or: "or", ast.Implies: "implies"}[kind]
            return {"op": op, "left": export_formula(value.left, scope, counter),
                    "right": export_formula(value.right, scope, counter)}
        name = f"x{counter[0]}"
        counter[0] += 1
        return {"op": "forall" if kind is ast.Forall else "exists",
                "sort": value.sort, "variable": name,
                "body": export_formula(value.body, [name, *scope], counter)}

    return {"formulas": [export_formula(formula, [], [0])
                          for formula in document.formulas]}


def render_fol(env: Any, value: ast.Document | list[Any] | Mapping[str, Any], *, view: str = "canonical") -> str | NaturalView:
    """Validate and render an internal, indexed-wire, or named FOL document."""
    if isinstance(value, ast.Document):
        document=value
        ast.check_document(env,document)
    elif isinstance(value,list): document=document_from_indexed_json(env,value)
    else: document=document_from_named_fol(env,value)
    if view == "canonical": return print_document(env,document)
    if view == "natural": return natural_document(env,document)
    from .printer import VIEWS, render
    if view in VIEWS:
        return render(document, env, view)
    raise ValueError("unknown rendering view")
