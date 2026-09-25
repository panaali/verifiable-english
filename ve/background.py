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
    return tuple(Premise(formula, generator)
                 for generator, (make, _) in HOOKS.items() for formula in make(env))


def validate_background(env, model) -> None:
    for generator, (_, validate) in HOOKS.items():
        try:
            validate(env, model)
        except InvalidModel as exc:
            if exc.generator is None:
                raise InvalidModel(exc.message, generator=generator, path=exc.path) from exc
            raise


def dependency_order(dependencies: dict[str, set[str] | tuple[str, ...]]) -> tuple[str, ...]:
    """Dependencies precede dependents in one DAG over defined and regulated symbols."""
    ordered, active, done = [], set(), set()

    def visit(name):
        if name in active:
            from .errors import VEError
            raise VEError("Dependency cycle in definitions and regulated predicates")
        if name in done:
            return
        active.add(name)
        for dependency in sorted(dependencies.get(name, ())):
            if dependency in dependencies:
                visit(dependency)
        active.remove(name)
        done.add(name)
        ordered.append(name)

    for symbol in sorted(dependencies):
        visit(symbol)
    return tuple(ordered)
