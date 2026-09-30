"""Environment-derived premises and finite-model validity hooks.

The wire never supplies this list. Workstreams register generators here when
their declaration schemas land; a declaration without its generator is not
silently given semantics.
"""
from __future__ import annotations

from typing import Callable, NamedTuple

from .assurance import semantic_entry
from .ast import And, Binary, Const, Eq, Exists, Forall, Formula, Implies, Not, Unary, Var
from .errors import InvalidModel, ResourceLimit


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


def _profile_pairs(env):
    return tuple((name, decl.regulated.permission) for name, decl in sorted(env.predicates.items())
                 if decl.regulated is not None and decl.regulated.permission is not None)


def _profile_premises(env):
    result = []
    for required, permitted in _profile_pairs(env):
        sorts = env.predicates[required].arguments
        terms = tuple(Var(len(sorts) - 1 - i) for i in range(len(sorts)))
        atom = lambda name: Unary(name, terms[0]) if len(terms) == 1 else Binary(name, *terms)
        formula = Implies(atom(required), atom(permitted))
        for sort in reversed(sorts):
            formula = Forall(sort, formula)
        result.append(formula)
    return tuple(result)


def _valid_profile(env, model):
    for required, permitted in _profile_pairs(env):
        if not model.relations[required] <= model.relations[permitted]:
            raise InvalidModel(f"required relation {required} exceeds permission {permitted}", generator="profile")


# Each entry is (premise generator, validity checker). The three empty slots
# are deliberately explicit extension points for W5, W3 and W1.
def _flag_premises(env):
    result = []
    for name, decl in sorted(env.predicates.items()):
        if decl.functional:
            result.append(Forall(decl.arguments[0], Forall(decl.arguments[1],
                Forall(decl.arguments[1], Implies(
                    And(Binary(name, Var(2), Var(1)), Binary(name, Var(2), Var(0))),
                    Eq(Var(1), Var(0)))))))
        if decl.total:
            result.append(Forall(decl.arguments[0], Exists(decl.arguments[1],
                Binary(name, Var(1), Var(0)))))
    return tuple(result)


def _valid_flags(env, model):
    for name, decl in env.predicates.items():
        if not (decl.functional or decl.total):
            continue
        values = {}
        for source, target in model.relations[name]:
            if decl.functional and source in values and values[source] != target:
                raise InvalidModel(f"{name!r} has two values for {source!r}", generator="flags")
            values[source] = target
        if decl.total:
            missing = set(model.domains[decl.arguments[0]]) - values.keys()
            if missing:
                raise InvalidModel(f"{name!r} has no value for {min(missing)!r}", generator="flags")

def _definition_premises(env):
    if not env.definition_entries:
        return ()
    from .definitions import compile_definitions, expand
    return expand(compile_definitions(env, env.definition_entries, version=env.environment_id))


def _valid_definitions(env, model):
    if not env.definition_entries:
        return
    from .evaluate import _evaluate_validated
    from .limits import MAX_EVALUATIONS
    for formula in _definition_premises(env):
        result = _evaluate_validated((formula,), model, max_evaluations=MAX_EVALUATIONS)
        if result.value is None:
            raise ResourceLimit("Definition background evaluation budget exhausted")
        if result.value is not True:
            raise InvalidModel("defined predicate table disagrees with its body",
                               generator="definitions")


def _soft_premises(env):
    # Populated only by a validated soft document. Neither wire premises nor
    # unvalidated environment metadata may supply this slot.
    return tuple(formula for _, formula in getattr(env, "soft_premises", ()))


def _valid_soft(env, model):
    if not getattr(env, "soft_premises", ()):
        return
    from .evaluate import _evaluate_validated
    from .limits import MAX_EVALUATIONS
    for label, formula in env.soft_premises:
        result = _evaluate_validated((formula,), model, max_evaluations=MAX_EVALUATIONS)
        if result.value is None:
            raise ResourceLimit(f"Soft background evaluation budget exhausted: {label}")
        if result.value is not True:
            raise InvalidModel(f"soft premise {label} is false", generator="soft")


def _rights_premises(env):
    # Installed only by correlate, never accepted from authored wire fields.
    return tuple(formula for _, formula in getattr(env, "rights_premises", ()))


def _valid_rights(env, model):
    if not getattr(env, "rights_premises", ()):
        return
    from .evaluate import _evaluate_validated
    from .limits import MAX_EVALUATIONS
    for label, formula in env.rights_premises:
        result = _evaluate_validated((formula,), model, max_evaluations=MAX_EVALUATIONS)
        if result.value is None:
            raise ResourceLimit(f"Rights background evaluation budget exhausted: {label}")
        if result.value is not True:
            raise InvalidModel(f"rights premise {label} is false", generator="rights")


# Each entry is (premise generator, validity checker).
HOOKS: dict[str, tuple[Callable, Callable]] = {
    "flags": (_flag_premises, _valid_flags),
    "definitions": (_definition_premises, _valid_definitions),
    "literals": (_literal_premises, _valid_literals),
    "profile": (_profile_premises, _valid_profile),
}


def _background_hooks(env):
    yield from HOOKS.items()
    if getattr(env, "soft_premises", ()):
        yield "soft", (_soft_premises, _valid_soft)
    if getattr(env, "rights_premises", ()):
        yield "rights", (_rights_premises, _valid_rights)


def _background_python(env) -> tuple[Premise, ...]:
    # Every checking site consults Background, so the gate on checker families
    # that have not landed sits here and in validate_background.
    from .profiles import require_checker
    require_checker(env)
    return tuple(Premise(formula, generator)
                 for generator, (make, _) in _background_hooks(env) for formula in make(env))


@semantic_entry("definitions.elaborate")
def background(env) -> tuple[Premise, ...]:
    """Environment premises from the selected authority, with the legacy type."""
    from .backends.dispatch import execute
    from .backends.lean_runner import route_environment, route_mode, run
    from .ast import formula_from_data

    case = {"id": "background", "kind": "background", "environment": env.to_dict()}

    def lean():
        if env.language != "ve.core@0.2":
            # The frozen v0 and v0.1 envelopes have no generated Background: their
            # Lean certificate runners bind the case premises alone.
            return ()
        request = {**case, "environment": route_environment(env)}
        row = run(route_mode(env), [request])[0]
        if len(row["premises"]) != len(row["generators"]):
            from .backends.lean_service import CheckerUnavailable
            raise CheckerUnavailable("CheckerUnavailable: malformed Lean Background result")
        base = tuple(Premise(formula_from_data(env, wire, _generated=True), generator)
                     for wire, generator in zip(row["premises"], row["generators"], strict=True))
        # Trusted composition: soft premises belong to a validated soft
        # document, not to the environment JSON. Lean regenerates them in the
        # soft route, and soft_route.check_regenerated compares them there.
        return base + tuple(Premise(formula, "soft") for formula in _soft_premises(env))

    return execute("background", case, lambda: _background_python(env), lean=lean)


def checked_premises(env, layer_premises, case_premises):
    """The certificate order: Background ++ composed layer premises ++ Γ.

    Layer premises are in composition order after the regenerated Background.
    """
    return (tuple(item.formula for item in background(env)) +
            tuple(layer_premises) + tuple(case_premises))


@semantic_entry("definitions.elaborate")
def validate_background(env, model) -> None:
    """Background validity of a model under the selected authority.

    Under a backend authority Lean's model mode decides (it checks the flags,
    definitions, literals and profile generators); the Python checks name a
    rejection both make (`backends.validation.decided`). A search candidate
    without an identity (`_defer_model_id`) and environments outside Lean's
    model mode keep the Python checks.
    """
    from .backends.dispatch import authority_for, execute
    from .backends.validation import model_in_scope, validated_model
    if (authority_for("model_validation") in ("python", "rust-experimental") or not model_in_scope(env)
            or getattr(env, "soft_premises", ()) or not getattr(model, "model_id", "")):
        return _validate_background_python(env, model)

    def python():
        _validate_background_python(env, model)
        return model

    execute("model_validation", {"kind": "model"}, python,
            lean=lambda: validated_model(env, model.to_dict(), python))


def _validate_background_python(env, model) -> None:
    from .profiles import require_checker
    require_checker(env)
    for generator, (_, validate) in _background_hooks(env):
        try:
            validate(env, model)
        except InvalidModel as exc:
            if exc.generator is None:
                raise InvalidModel(exc.message, generator=generator, path=exc.path) from exc
            raise


def _dependency_order_python(dependencies: dict[str, set[str] | tuple[str, ...]]) -> tuple[str, ...]:
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


_DEPENDENCY_ENVIRONMENT = {
    "language": "ve.core@0.2", "profiles": ["relational-fol@0"],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}},
}


@semantic_entry("definitions.elaborate")
def dependency_order(dependencies: dict[str, set[str] | tuple[str, ...]]) -> tuple[str, ...]:
    """Dependencies precede dependents in one DAG over defined and regulated symbols."""
    from .backends.dispatch import authority_for, execute
    from .backends.lean_runner import run
    from .backends.lean_service import CheckerUnavailable
    from .errors import ResourceLimit

    if authority_for("dependency_order") == "python":
        return _dependency_order_python(dependencies)
    if len(dependencies) > 256:
        raise ResourceLimit("dependency graph size")
    case = {"id": "dependency-order", "kind": "dependency-order",
            "environment": _DEPENDENCY_ENVIRONMENT,
            "nodes": [{"name": name, "mentions": sorted(dependencies[name])}
                      for name in sorted(dependencies)]}

    def lean():
        order = run("route", [case])[0]["order"]
        if (type(order) is not list or len(order) != len(dependencies)
                or set(order) != set(dependencies)):
            raise CheckerUnavailable("CheckerUnavailable: malformed Lean dependency order")
        return tuple(order)

    return execute("dependency_order", case,
                   lambda: _dependency_order_python(dependencies), lean=lean)


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
