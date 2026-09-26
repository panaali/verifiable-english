"""Pure elaboration of acyclic predicate definitions.

This module does not install a declaration hook.  The P0 environment decoder
must attach identity-bound ``defined`` entries before these premises can be
used as Background in the public checking route.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import ast
from .background import dependency_order
from .environment import Environment
from .errors import VEError
from .wire import digest


@dataclass(frozen=True, slots=True)
class Definition:
    name: str
    arguments: tuple[str, ...]
    body: ast.Formula


def _mentions(formula: ast.Formula) -> set[str]:
    match formula:
        case ast.Unary(predicate, _) | ast.Binary(predicate, _, _):
            return {predicate}
        case ast.Not(body) | ast.Forall(_, body) | ast.Exists(_, body):
            return _mentions(body)
        case ast.And(left, right) | ast.Or(left, right) | ast.Implies(left, right):
            return _mentions(left) | _mentions(right)
        case ast.Reach(_, ast.Named(relation), _, _):
            return {relation}
        case ast.Reach(_, ast.Body(_, body), _, _):
            return _mentions(body)
        case _:
            return set()


def _atom(name: str, arity: int) -> ast.Formula:
    if arity == 1:
        return ast.Unary(name, ast.Var(0))
    if arity == 2:
        return ast.Binary(name, ast.Var(1), ast.Var(0))
    raise VEError("Definition must have one or two arguments")


def premise(definition: Definition) -> ast.Formula:
    """The closed biconditional, with binders in declared argument order."""
    head = _atom(definition.name, len(definition.arguments))
    result = ast.And(ast.Implies(head, definition.body),
                     ast.Implies(definition.body, head))
    for sort in reversed(definition.arguments):
        result = ast.Forall(sort, result)
    return result


def _restricted(env: Environment, allowed: set[str]) -> Environment:
    raw = env.to_dict()
    raw["vocabulary"]["predicates"] = {
        name: declaration for name, declaration in raw["vocabulary"]["predicates"].items()
        if name in allowed
    }
    return Environment(raw)


def compile_definitions(env: Environment, entries: dict[str, dict], *,
                        version: str) -> tuple[Definition, ...]:
    """Check declared bodies and order them below their dependents.

    ``entries`` contains the identity-bound body payload supplied by the
    future declaration hook.  The predicates must already be in ``env``.
    """
    if "definitions@0" not in env.profiles:
        raise VEError("Definitions require definitions@0")
    if type(version) is not str or not version:
        raise VEError("Definition version must be a nonempty string")
    if type(entries) is not dict:
        raise VEError("Definitions must be an object")
    result = {}
    for name, entry in entries.items():
        if name not in env.predicates:
            raise VEError(f"Undefined predicate declaration {name!r}")
        if type(entry) is not dict or set(entry) != {"arguments", "body"}:
            raise VEError(f"Definition {name!r} needs arguments and body")
        arguments = entry["arguments"]
        if type(arguments) is not list or tuple(arguments) != env.predicates[name].arguments:
            raise VEError(f"Definition {name!r} arguments differ from its declaration")
        body = entry["body"]
        if type(body) is list:
            body = ast._Decoder().decode(body)
        result[name] = Definition(name, tuple(arguments), body)
    mentions = {name: _mentions(definition.body) for name, definition in result.items()}
    order = dependency_order(mentions)
    allowed = set(env.predicates) - set(result)
    ordered = []
    for name in order:
        definition = result[name]
        if name in mentions[name]:
            raise VEError(f"DependencyCycle: {name}")
        missing = mentions[name] - allowed
        if missing:
            raise VEError(f"Definition {name!r} mentions a symbol not below it: {sorted(missing)[0]}")
        lower_env = _restricted(env, allowed)
        try:
            ast._Checker(lower_env).formula(definition.body, tuple(reversed(definition.arguments)))
        except VEError as exc:
            raise VEError(f"Definition {name!r}: {exc}") from exc
        ast.check_formula(env, premise(definition))
        ordered.append(definition)
        allowed.add(name)
    return tuple(ordered)


def expand(definitions: tuple[Definition, ...]) -> tuple[ast.Formula, ...]:
    """Executable statement-layer elaboration in dependency order."""
    return tuple(premise(definition) for definition in definitions)


def definitions_id(env: Environment, definitions: tuple[Definition, ...], *,
                   version: str) -> str:
    """A provisional content digest for tests; public environment identity awaits P0."""
    from .ast import _to_data
    return digest("ve-definitions-v0.2\n", {
        "environment_id": env.environment_id,
        "version": version,
        "definitions": [{"name": d.name, "arguments": list(d.arguments),
                         "body": _to_data(d.body)} for d in definitions],
    })
