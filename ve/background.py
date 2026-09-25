"""Environment-derived premises and finite-model validity hooks.

The wire never supplies this list. Workstreams register generators here when
their declaration schemas land; a declaration without its generator is not
silently given semantics.
"""
from __future__ import annotations

from typing import Callable, NamedTuple

from .ast import Const, Eq, Formula, Not
from .errors import InvalidModel


class Premise(NamedTuple):
    formula: Formula
    generator: str


def _empty(_env):
    return ()


def _valid(_env, _model):
    return None


def _literal_premises(env):
    literals = sorted(name for name, decl in env.constants.items() if decl.sort == "$string")
    return tuple(Not(Eq(Const(left), Const(right)))
                 for index, left in enumerate(literals) for right in literals[index + 1:])


def _valid_literals(env, model):
    denotations = {}
    for name, decl in env.constants.items():
        if decl.sort != "$string":
            continue
        value = model.constants[name]
        if value in denotations:
            raise InvalidModel(f"$string literals {denotations[value]!r} and {name!r} alias",
                               generator="literals")
        denotations[value] = name


# Each entry is (premise generator, validity checker). The three empty slots
# are deliberately explicit extension points for W5, W3 and W1.
HOOKS: dict[str, tuple[Callable, Callable]] = {
    "flags": (_empty, _valid),
    "definitions": (_empty, _valid),
    "literals": (_literal_premises, _valid_literals),
    "profile": (_empty, _valid),
}


def background(env) -> tuple[Premise, ...]:
    # Every checking site consults Background, so the gate on checker families
    # that have not landed sits here and in validate_background.
    from .profiles import require_checker
    require_checker(env)
    return tuple(Premise(formula, generator)
                 for generator, (make, _) in HOOKS.items() for formula in make(env))


def checked_premises(env, layer_premises, case_premises):
    """The certificate order: Background ++ composed layer premises ++ Γ.

    Layer premises are in composition order. P0 has no executable layers, so
    current callers pass an empty layer list. Keep this order when they land.
    """
    return (tuple(item.formula for item in background(env)) +
            tuple(layer_premises) + tuple(case_premises))


def validate_background(env, model) -> None:
    from .profiles import require_checker
    require_checker(env)
    for generator, (_, validate) in HOOKS.items():
        try:
            validate(env, model)
        except InvalidModel as exc:
            if exc.generator is None:
                raise InvalidModel(exc.message, generator=generator, path=exc.path) from exc
            raise


def dependency_order(dependencies: dict[str, set[str] | tuple[str, ...]]) -> tuple[str, ...]:
    """Dependencies precede dependents in one DAG over defined and regulated symbols."""
    from .errors import ResourceLimit, VEError
    if len(dependencies) > 256:
        raise ResourceLimit("dependency graph size")
    names = set(dependencies)
    remaining = {name: set(mentions) & names for name, mentions in dependencies.items()}
    ordered = []
    while remaining:
        ready = next((name for name in sorted(remaining) if not remaining[name]), None)
        if ready is None:
            raise VEError("DependencyCycle: " + ", ".join(sorted(remaining)))
        ordered.append(ready)
        del remaining[ready]
        for mentions in remaining.values():
            mentions.discard(ready)
    return tuple(ordered)


def dependency_order_nodes(nodes) -> tuple[str, ...]:
    """The wire form shared with the Lean route and Rust: `[{"name", "mentions"}]`.

    Duplicate names are rejected (the first name, in list order, that occurs
    twice); mentions of symbols that are not nodes carry no edge."""
    from .errors import DuplicateDeclaration, ResourceLimit, VEError
    from .wire import require_fields
    if type(nodes) is not list:
        raise VEError("dependency nodes must be an array")
    if len(nodes) > 256:
        raise ResourceLimit("dependency graph size")
    parsed = []
    for node in nodes:
        require_fields(node, {"name", "mentions"})
        name, mentions = node["name"], node["mentions"]
        if type(name) is not str or type(mentions) is not list or any(type(m) is not str for m in mentions):
            raise VEError("dependency nodes are {name: string, mentions: [string]}")
        parsed.append((name, tuple(mentions)))
    names = [name for name, _ in parsed]
    duplicate = next((name for name in names if names.count(name) > 1), None)
    if duplicate is not None:
        raise DuplicateDeclaration(f"dependency node {duplicate}")
    return dependency_order(dict(parsed))
