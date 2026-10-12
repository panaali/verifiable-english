"""Pure elaboration of acyclic predicate definitions.

The environment decoder stores identity-bound ``defined`` entries. The
background generator calls this elaborator in dependency order.
"""
from __future__ import annotations

from dataclasses import dataclass

from .assurance import semantic_entry
from . import ast
from .background import dependency_order
from .environment import Environment
from .errors import UnsupportedProfile, VEError
from .wire import digest


@dataclass(frozen=True, slots=True)
class Definition:
    name: str
    arguments: tuple[str, ...]
    body: ast.Formula


def _mentions(formula: ast.Formula) -> set[str]:
    # The decoder keeps a name of any JSON kind; one that is not a string names
    # no symbol, and the body's typing check rejects it.
    match formula:
        case ast.Unary(predicate, _) | ast.Binary(predicate, _, _) | ast.Atom(predicate, _):
            return {predicate} if type(predicate) is str else set()
        case ast.Not(body) | ast.Forall(_, body) | ast.Exists(_, body):
            return _mentions(body)
        case ast.And(left, right) | ast.Or(left, right) | ast.Implies(left, right):
            return _mentions(left) | _mentions(right)
        case ast.Reach(_, ast.Named(relation), _, _):
            return {relation} if type(relation) is str else set()
        case ast.Reach(_, ast.Body(_, body), _, _):
            return _mentions(body)
        case _:
            return set()


def _has_reach(formula: ast.Formula) -> bool:
    match formula:
        case ast.Reach():
            return True
        case ast.Not(body) | ast.Forall(_, body) | ast.Exists(_, body):
            return _has_reach(body)
        case ast.And(left, right) | ast.Or(left, right) | ast.Implies(left, right):
            return _has_reach(left) or _has_reach(right)
        case _:
            return False


def _atom(name: str, arity: int) -> ast.Formula:
    if arity == 1:
        return ast.Unary(name, ast.Var(0))
    if arity == 2:
        return ast.Binary(name, ast.Var(1), ast.Var(0))
    if 3 <= arity <= 6:
        return ast.Atom(name, tuple(ast.Var(arity - index - 1) for index in range(arity)))
    raise VEError("Definition must have one to six arguments")


def premise(definition: Definition) -> ast.Formula:
    """The closed biconditional, with binders in declared argument order."""
    head = _atom(definition.name, len(definition.arguments))
    result = ast.And(ast.Implies(head, definition.body),
                     ast.Implies(definition.body, head))
    for sort in reversed(definition.arguments):
        result = ast.Forall(sort, result)
    return result


def _restricted(env: Environment, allowed: set[str]) -> Environment:
    """The signatures below a definition. Bodies of the kept definitions are
    dropped: typing a body needs only signatures, and keeping them would
    re-elaborate every lower definition."""
    raw = env.to_dict()
    raw["vocabulary"]["predicates"] = {
        name: {key: value for key, value in declaration.items() if key != "defined"}
        for name, declaration in raw["vocabulary"]["predicates"].items()
        if name in allowed
    }
    return Environment(raw)


# environment_id binds every definition body and version, so elaboration is a
# function of it; bounded so hostile inputs cannot grow the cache.
_COMPILED: dict[tuple[str, str], tuple[Definition, ...]] = {}


@semantic_entry("definitions.elaborate")
def compile_definitions(env: Environment, entries: dict[str, dict], *,
                        version: str) -> tuple[Definition, ...]:
    """Check declared bodies and order them below their dependents.

    ``entries`` contains identity-bound body payloads from the vocabulary.
    Lean validates and orders them under every authority (`_compile_lean`,
    lean-first batch 13b). Environments outside Lean's model scope keep the
    retained Python elaborator, a recorded scope gap.
    """
    from .backends.dispatch import owned
    from .backends.validation import model_in_scope

    def python():
        return _compile_python(env, entries, version=version)

    if not model_in_scope(env):
        return python()
    return owned("definitions_elaboration", lambda: _compile_lean(env, entries, version, python))


def _wire_entries(env: Environment, entries) -> dict | None:
    """`entries` embedded as `defined` fields of `env`'s declarations, or None
    when they cannot be (then only Python's structural decoder reads them)."""
    if type(entries) is not dict:
        return None
    raw = env.to_dict()
    predicates = raw["vocabulary"]["predicates"]
    for declaration in predicates.values():
        declaration.pop("defined", None)
    for name, entry in entries.items():
        if name not in predicates or type(entry) is not dict or set(entry) != {"arguments", "body"}:
            return None
        body = entry["body"]
        predicates[name]["defined"] = {"arguments": entry["arguments"],
                                       "body": body if type(body) is list else ast._to_data(body)}
    return raw


def _lean_definition(env: Environment, premise_wire) -> Definition:
    """A definition read back from its regenerated premise
    `∀x̄. (head(x̄) → body) ∧ (body → head(x̄))`."""
    node = premise_wire
    sorts = []
    while type(node) is list and node and node[0] == "forall":
        sorts.append(node[1])
        node = node[2]
    if (type(node) is not list or node[:1] != ["and"] or type(node[1]) is not list
            or node[1][:1] != ["implies"] or type(node[1][1]) is not list or len(node[1][1]) < 2):
        from .errors import CheckerUnavailable
        raise CheckerUnavailable("CheckerUnavailable: malformed Lean definition premise")
    return Definition(node[1][1][1], tuple(sorts), ast._Decoder().decode(node[1][2]))


def _compile_lean(env: Environment, entries, version, python) -> tuple[Definition, ...]:
    """Lean's route Background decides the definitions and their order; the
    definitions are read back from its regenerated premises. Entries that
    cannot be embedded in the environment (only a direct caller passes them)
    and n-ary definitions on the core family keep the retained Python."""
    from .backends.lean_runner import route_mode
    from .backends.relay import decide_once
    from .backends.validation import nary_core_definitions
    raw = _wire_entries(env, entries)
    if raw is None or type(version) is not str or not version:
        return python()
    if nary_core_definitions(env.profiles, raw["vocabulary"]["predicates"].values()):
        return python()  # outside Lean's core layer glue (stage-2c gap, batch 14c)
    row = decide_once(route_mode(env), {"id": "definitions", "kind": "background", "environment": raw})
    if len(row["premises"]) != len(row["generators"]):
        from .errors import CheckerUnavailable
        raise CheckerUnavailable("CheckerUnavailable: malformed Lean Background result")
    return tuple(_lean_definition(env, premise) for premise, generator
                 in zip(row["premises"], row["generators"], strict=True) if generator == "definitions")


def _compile_python(env: Environment, entries: dict[str, dict], *,
                    version: str) -> tuple[Definition, ...]:
    if "definitions@0" not in env.profiles:
        raise VEError("Definitions require definitions@0")
    key = (env.environment_id, version)
    if entries == env.definition_entries and key in _COMPILED:
        return _COMPILED[key]
    if type(version) is not str or not version:
        raise VEError("Definition version must be a nonempty string")
    if type(entries) is not dict:
        raise VEError("Definitions must be an object")
    if env.order:
        raise UnsupportedProfile("definitions on the order family require an order definition layer")
    result = {}
    for name, entry in entries.items():
        if name not in env.predicates:
            raise VEError(f"Undefined predicate declaration {name!r}")
        if type(entry) is not dict or set(entry) != {"arguments", "body"}:
            raise VEError(f"Definition {name!r} needs arguments and body")
        arguments = entry["arguments"]
        if type(arguments) is not list or tuple(arguments) != env.predicates[name].arguments:
            raise VEError(f"Definition {name!r} arguments differ from its declaration")
        if "$int" in arguments:
            raise UnsupportedProfile("Definitions over $int arguments require an order definition layer")
        body = entry["body"]
        if type(body) is list:
            body = ast._Decoder().decode(body)
        if _has_reach(body):
            raise UnsupportedProfile(
                "definition bodies with reachability require a closure definition layer")
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
            raise VEError(f"Definition {name}: the body is not a typed formula over the symbols below it")
        lower_env = _restricted(env, allowed)
        try:
            ast._Checker(lower_env).formula(definition.body, tuple(reversed(definition.arguments)))
        except VEError as exc:
            raise VEError(f"Definition {name}: the body is not a typed formula over the symbols below it") from exc
        ast.check_formula(env, premise(definition))
        ordered.append(definition)
        allowed.add(name)
    if entries == env.definition_entries:
        if len(_COMPILED) >= 256:
            _COMPILED.clear()
        _COMPILED[key] = tuple(ordered)
    return tuple(ordered)


@semantic_entry("definitions.elaborate")
def expand(definitions: tuple[Definition, ...]) -> tuple[ast.Formula, ...]:
    """Executable statement-layer elaboration in dependency order."""
    return tuple(premise(definition) for definition in definitions)


def definitions_id(env: Environment, definitions: tuple[Definition, ...], *,
                   version: str) -> str:
    """A content digest for standalone elaboration; public identity is on env."""
    from .ast import _to_data
    return digest("ve-definitions-v0.2\n", {
        "environment_id": env.environment_id,
        "version": version,
        "definitions": [{"name": d.name, "arguments": list(d.arguments),
                         "body": _to_data(d.body)} for d in definitions],
    })
