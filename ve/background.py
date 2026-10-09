"""Environment-derived premises and finite-model validity hooks.

The wire never supplies this list. Workstreams register generators here when
their declaration schemas land; a declaration without its generator is not
silently given semantics.
"""
from __future__ import annotations

from typing import Callable, NamedTuple

from .assurance import semantic_entry
from .ast import Const, Eq, Formula, Not
from .errors import InvalidModel, ResourceLimit


class Premise(NamedTuple):
    formula: Formula
    generator: str


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


def _valid_profile(env, model):
    for required, permitted in _profile_pairs(env):
        if not model.relations[required] <= model.relations[permitted]:
            raise InvalidModel(f"required relation {required} exceeds permission {permitted}", generator="profile")


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


def _valid_fill(env, model):
    if not getattr(env, "fill_premises", ()):
        return
    from .evaluate import _evaluate_validated
    from .limits import MAX_EVALUATIONS
    for label, formula in env.fill_premises:
        result = _evaluate_validated((formula,), model, max_evaluations=MAX_EVALUATIONS)
        if result.value is None:
            raise ResourceLimit(f"Fill background evaluation budget exhausted: {label}")
        if result.value is not True:
            raise InvalidModel(f"fill premise {label} is false", generator="norm-defaults")


# The Background generators and their model-validity checkers. Lean regenerates the premises
# (`background`, lean-first batch 13b); the checkers validate a search candidate that has no
# identity yet (`validate_background`), whose witness Lean checks again when it is reported.
HOOKS: dict[str, Callable] = {
    "flags": _valid_flags,
    "definitions": _valid_definitions,
    "literals": _valid_literals,
    "profile": _valid_profile,
}


def _background_hooks(env):
    yield from HOOKS.items()
    if getattr(env, "soft_premises", ()):
        yield "soft", _valid_soft
    if getattr(env, "rights_premises", ()):
        yield "rights", _valid_rights
    if getattr(env, "fill_premises", ()):
        yield "norm-defaults", _valid_fill


@semantic_entry("definitions.elaborate")
def background(env) -> tuple[Premise, ...]:
    """Environment premises regenerated by Lean under every authority (lean-first batch 13b), with the
    legacy type."""
    from .backends.dispatch import owned
    from .backends.lean_runner import cached_route_environment, route_mode
    from .backends.relay import decide_once
    from .ast import formula_from_data

    case = {"id": "background", "kind": "background", "environment": env.to_dict()}

    def lean():
        if env.language != "ve.core@0.2":
            # The frozen v0 and v0.1 envelopes have no generated Background: their
            # Lean certificate runners bind the case premises alone.
            return ()
        # The same Background request is asked once (lean-first batch 2, F3).
        row = decide_once(route_mode(env), {**case, "environment": cached_route_environment(env)})
        if len(row["premises"]) != len(row["generators"]):
            from .backends.lean_service import CheckerUnavailable
            raise CheckerUnavailable("CheckerUnavailable: malformed Lean Background result")
        base = tuple(Premise(formula_from_data(env, wire, _generated=True), generator)
                     for wire, generator in zip(row["premises"], row["generators"], strict=True))
        # Trusted composition: soft premises belong to a validated soft
        # document, and rights premises to a correlated rights document, not to
        # the environment JSON. Lean regenerates them in the soft and rights
        # routes, and soft_route.check_regenerated and
        # The rights route supplies them as part of its Lean elaboration.
        return (base + tuple(Premise(formula, "soft") for formula in _soft_premises(env))
                + tuple(Premise(formula, "rights") for formula in _rights_premises(env)))

    return owned("background", lean)


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
    for generator, validate in _background_hooks(env):
        try:
            validate(env, model)
        except InvalidModel as exc:
            if exc.generator is None:
                raise InvalidModel(exc.message, generator=generator, path=exc.path) from exc
            raise


_DEPENDENCY_ENVIRONMENT = {
    "language": "ve.core@0.2", "profiles": ["relational-fol@0"],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}},
}


@semantic_entry("definitions.elaborate")
def dependency_order(dependencies: dict[str, set[str] | tuple[str, ...]]) -> tuple[str, ...]:
    """Dependencies precede dependents in one DAG over defined and regulated symbols."""
    from .backends.dispatch import owned
    from .backends.relay import decide
    from .backends.lean_service import CheckerUnavailable
    from .errors import ResourceLimit

    if len(dependencies) > 256:
        raise ResourceLimit("dependency graph size")
    case = {"id": "dependency-order", "kind": "dependency-order",
            "environment": _DEPENDENCY_ENVIRONMENT,
            "nodes": [{"name": name, "mentions": sorted(dependencies[name])}
                      for name in sorted(dependencies)]}

    def lean():
        order = decide("route", [case])[0]["order"]
        if (type(order) is not list or len(order) != len(dependencies)
                or set(order) != set(dependencies)):
            raise CheckerUnavailable("CheckerUnavailable: malformed Lean dependency order")
        return tuple(order)

    return owned("dependency_order", lean)


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
