"""Validated finite structures for the relational v0 profile."""
from __future__ import annotations

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Any, Mapping
from itertools import product

from .assurance import semantic_entry
from .errors import InvalidModel, ResourceLimit
from .limits import MAX_TUPLES

INT_SORT = "$int"

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
        """Build a model after Lean's validation.

        `_defer_model_id` marks a search generator's candidate: it is never
        reported before `countermodel.check` checks it, so it keeps Python's
        structural decoder. `_claimed` holds the `environment_id` and
        `model_id` an existing `FiniteModel` claims; each must be the
        recomputed identity.
        """
        def python():
            return cls._decode(env, wire, _defer_model_id=_defer_model_id)

        # Search candidates are unreported until a Lean witness check.
        if _defer_model_id:
            return python()
        # A soft/rights document adds generated relations and private premises
        # to a search environment. It is not an authored envelope the service
        # can register. Its candidate evaluator remains the generator-internal
        # duplicate tracked for batch 15; witnesses are replayed by Lean.
        if (any(getattr(env, slot, ()) for slot in
                ("soft_premises", "rights_premises", "fill_premises")) or
                any(name.startswith(("soft__", "rights__", "reports__")) for name in env.predicates)):
            built = cls._decode(env, wire, _defer_model_id=True)
            from .wire import digest
            model_id = digest(f"ve-model-{env.identity_version}\n", {
                "environment_id": env.environment_id, "model": built.to_dict()})
            if _claimed is not None:
                if _claimed["environment_id"] != env.environment_id:
                    raise InvalidModel("model belongs to a different environment")
                if _claimed["model_id"] != model_id:
                    raise InvalidModel("model identity does not match its contents")
            return replace(built, model_id=model_id)
        from .backends.validation import validated_model
        return validated_model(env, wire, python, claimed=_claimed)

    @classmethod
    def _decode(cls, env: Any, wire: Any, *, _defer_model_id: bool = False) -> "FiniteModel":
        """Materialise a model after Lean accepted it, or a search candidate.

        Search candidates are untrusted and gain no identity until a Lean
        witness check. Any unexpected shape in an accepted model is an
        operational construction failure at the public adapter.
        """
        sort_names = set(env.model_sorts)
        defined_names = set(env.definition_entries)
        predicate_names = set(env.predicates) - defined_names
        order = getattr(env, "order", False)
        domains = {sort: tuple(sorted(wire["domains"][sort])) for sort in sorted(sort_names)}
        constants = {}
        for name in sorted(env.constants):
            raw = wire["constants"][name]
            constants[name] = int(raw) if order and env.constants[name].sort == INT_SORT else raw
        relations = {}
        for name in sorted(predicate_names):
            signature = env.predicates[name].arguments
            relations[name] = frozenset(tuple(int(cell) if order and sort == INT_SORT else cell
                                              for cell, sort in zip(row, signature, strict=True))
                                        for row in wire["relations"][name])
        tuple_count = sum(map(len, relations.values()))

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

        model = cls(MappingProxyType(domains), MappingProxyType(constants), MappingProxyType(relations),
                    env.environment_id, "", tuple(sorted(defined_names)))
        if _defer_model_id:
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
