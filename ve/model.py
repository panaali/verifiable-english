"""Validated finite structures for the relational v0 profile."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping
import re
from itertools import product

from .assurance import semantic_entry
from .errors import InvalidModel, ResourceLimit
from .limits import MAX_ENTITIES, MAX_IDENTIFIER_BYTES, MAX_PACKAGE_BYTES, MAX_TUPLES

INT_SORT = "$int"

_ID = re.compile(r"^[a-z][a-z0-9_]*$")


def _fail(message: str, path: str = "") -> None:
    raise InvalidModel(message, path=path)


def _keys(value: Any, expected: set[str], path: str) -> None:
    if not isinstance(value, dict):
        _fail("expected an object", path)
    if set(value) != expected:
        missing = sorted(expected - set(value))
        extra = sorted(set(value) - expected)
        _fail(f"fields do not match (missing={missing}, unknown={extra})", path)


def _local_id(value: Any, path: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        _fail("local ID must match [a-z][a-z0-9_]*", path)
    if len(value.encode("ascii")) > MAX_IDENTIFIER_BYTES:
        raise ResourceLimit("local ID exceeds 64 ASCII bytes", path=path)
    return value


def _model_limits(wire: Any, sort_names: set[str]) -> None:
    """The static limits of a submitted model, after its shape and before any
    entity is read: each domain has at most MAX_ENTITIES entries, then all
    supplied tables at most MAX_TUPLES rows together (Lean `modelLimits`, Rust
    `model_limits`). Entries that are not arrays are left to the decoder."""
    for sort in sorted(sort_names):
        raw = wire["domains"][sort]
        if isinstance(raw, list) and len(raw) > MAX_ENTITIES:
            raise ResourceLimit("domain exceeds entity limit", path=f"/domains/{sort}")
    if sum(len(raw) for raw in wire["relations"].values() if isinstance(raw, list)) > MAX_TUPLES:
        raise ResourceLimit("model exceeds total relation tuple limit", path="/relations")


@dataclass(frozen=True, slots=True)
class FiniteModel:
    """A defensively copied, validated finite model."""

    domains: Mapping[str, tuple[str, ...]]
    constants: Mapping[str, str]
    relations: Mapping[str, frozenset[tuple[str, ...]]]
    environment_id: str
    model_id: str
    defined_predicates: tuple[str, ...] = ()

    @classmethod
    def from_json(cls, env: Any, data: str | bytes) -> "FiniteModel":
        from .wire import loads_json
        return cls.from_dict(env, loads_json(data))

    @classmethod
    @semantic_entry("model")
    def from_dict(cls, env: Any, wire: Any, *, _defer_model_id: bool = False,
                  _claimed: dict | None = None) -> "FiniteModel":
        """Decode and validate a model under the selected authority.

        `_defer_model_id` marks a search generator's candidate: it is never
        reported before `countermodel.check` checks it, so it keeps Python's
        structural decoder. `_claimed` holds the `environment_id` and
        `model_id` an existing `FiniteModel` claims; each must be the
        recomputed identity.
        """
        from .backends.dispatch import authority_for, execute

        def python():
            if _claimed is not None and _claimed["environment_id"] != env.environment_id:
                raise InvalidModel("model belongs to a different environment")
            built = cls._decode(env, wire, _defer_model_id=_defer_model_id)
            if _claimed is not None and built.model_id != _claimed["model_id"]:
                raise InvalidModel("model identity does not match its contents")
            return built

        # rust-experimental covers evaluation and search only; its witnesses
        # keep the Python decoder, as before any adapter existed.
        if _defer_model_id or authority_for("model_validation") in ("python", "rust-experimental"):
            return python()
        from .backends.validation import model_in_scope, validated_model
        if not model_in_scope(env):
            return python()
        return execute("model_validation", {"kind": "model"}, python,
                       lean=lambda: validated_model(env, wire, python, claimed=_claimed))

    @classmethod
    def _decode(cls, env: Any, wire: Any, *, _defer_model_id: bool = False) -> "FiniteModel":
        _keys(wire, {"complete", "domains", "constants", "relations"}, "")
        if wire["complete"] is not True:
            _fail("complete must be the Boolean true", "/complete")
        for field in ("domains", "constants", "relations"):
            if not isinstance(wire[field], dict):
                _fail("expected an object", f"/{field}")

        sort_names = set(env.model_sorts)
        defined_names = set(env.definition_entries)
        predicate_names = set(env.predicates) - defined_names
        constant_names = set(env.constants)
        if set(wire["domains"]) != sort_names:
            _fail("domains must contain exactly the declared sorts", "/domains")
        if set(wire["constants"]) != constant_names:
            _fail("constants must contain exactly the declared constants", "/constants")
        if defined_names.intersection(wire["relations"]):
            raise InvalidModel("supplied table for defined predicate", generator="definitions",
                               path="/relations")
        if set(wire["relations"]) != predicate_names:
            _fail("relations must contain exactly the base predicates; defined tables are computed", "/relations")
        _model_limits(wire, sort_names)

        domains: dict[str, tuple[str, ...]] = {}
        for sort in sorted(sort_names):
            raw = wire["domains"][sort]
            if not isinstance(raw, list):
                _fail("domain must be an array", f"/domains/{sort}")
            values = tuple(_local_id(x, f"/domains/{sort}/{i}") for i, x in enumerate(raw))
            if len(set(values)) != len(values):
                _fail("duplicate domain entity", f"/domains/{sort}")
            domains[sort] = tuple(sorted(values))

        order = getattr(env, "order", False)

        def integer(raw, path):
            from .ast import decimal_from_wire
            from .errors import VEError
            try:
                return decimal_from_wire(raw)
            except ResourceLimit:
                raise
            except VEError as exc:
                _fail("integer values must be canonical decimal strings", path)

        constants: dict[str, str | int] = {}
        for name in sorted(constant_names):
            sort = env.constants[name].sort
            if order and sort == INT_SORT:
                constants[name] = integer(wire["constants"][name], f"/constants/{name}")
                continue
            value = _local_id(wire["constants"][name], f"/constants/{name}")
            if value not in domains[sort]:
                _fail("constant denotes an entity outside its sort", f"/constants/{name}")
            constants[name] = value

        relations: dict[str, frozenset[tuple[str, ...]]] = {}
        tuple_count = 0
        for name in sorted(predicate_names):
            raw = wire["relations"][name]
            if not isinstance(raw, list):
                _fail("relation must be an array", f"/relations/{name}")
            signature = tuple(env.predicates[name].arguments)
            tuples: list[tuple[str, ...]] = []
            for i, item in enumerate(raw):
                if not isinstance(item, list) or len(item) != len(signature):
                    _fail("relation tuple has wrong arity", f"/relations/{name}/{i}")
                row = tuple(integer(x, f"/relations/{name}/{i}/{j}") if order and sort == INT_SORT
                            else _local_id(x, f"/relations/{name}/{i}/{j}")
                            for j, (x, sort) in enumerate(zip(item, signature, strict=True)))
                for j, (value, sort) in enumerate(zip(row, signature, strict=True)):
                    if not (order and sort == INT_SORT) and value not in domains[sort]:
                        _fail("relation tuple contains a dangling or wrong-sort entity", f"/relations/{name}/{i}/{j}")
                tuples.append(row)
            if len(set(tuples)) != len(tuples):
                _fail("duplicate relation tuple", f"/relations/{name}")
            tuple_count += len(tuples)
            if tuple_count > MAX_TUPLES:
                raise ResourceLimit("model exceeds total relation tuple limit", path="/relations")
            relations[name] = frozenset(tuples)

        if defined_names:
            from .definitions import compile_definitions
            from .evaluate import _Evaluator, _Exhausted
            from .limits import MAX_EVALUATIONS
            work_remaining = MAX_EVALUATIONS
            for definition in compile_definitions(env, env.definition_entries, version=env.environment_id):
                table = set()
                temporary = cls(MappingProxyType(domains), MappingProxyType(constants),
                                MappingProxyType(relations), env.environment_id, "")
                evaluator = _Evaluator(env, temporary, work_remaining, trace=False)
                try:
                    for row in product(*(domains[s] for s in definition.arguments)):
                        bindings = tuple(reversed(tuple(zip(definition.arguments, row))))
                        if evaluator.formula(definition.body, bindings)[0]:
                            table.add(row)
                            if tuple_count + len(table) > MAX_TUPLES:
                                raise ResourceLimit("model exceeds total relation tuple limit", path="/relations")
                except _Exhausted as exc:
                    raise ResourceLimit("Definition model evaluation budget exhausted") from exc
                work_remaining -= evaluator.work
                tuple_count += len(table)
                relations[definition.name] = frozenset(table)

        environment_id = env.environment_id
        model_id = ""
        if not _defer_model_id:
            normalized = _normalized(domains, constants, relations, defined_names)
            from .wire import digest
            model_id = digest(f"ve-model-{env.identity_version}\n", {"environment_id": environment_id, "model": normalized})
        model = cls(MappingProxyType(domains), MappingProxyType(constants), MappingProxyType(relations),
                    environment_id, model_id, tuple(sorted(defined_names)))
        from .background import _validate_background_python
        _validate_background_python(env, model)
        return model

    def to_dict(self) -> dict[str, Any]:
        return _normalized(self.domains, self.constants, self.relations, set(self.defined_predicates))


def _cell(value):
    # Integers (order@0 only) travel as canonical decimal strings.
    return str(value) if type(value) is int else value


def _normalized(domains, constants, relations, excluded=frozenset()) -> dict[str, Any]:
    return {
        "complete": True,
        "domains": {k: list(domains[k]) for k in sorted(domains)},
        "constants": {k: _cell(constants[k]) for k in sorted(constants)},
        "relations": {k: [[_cell(c) for c in x] for x in sorted(relations[k])]
                      for k in sorted(relations) if k not in excluded},
    }
