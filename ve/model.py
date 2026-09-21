"""Validated finite structures for the relational v0 profile."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping
import re

from .errors import InvalidModel, ResourceLimit
from .limits import MAX_ENTITIES, MAX_IDENTIFIER_BYTES, MAX_PACKAGE_BYTES, MAX_TUPLES

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


@dataclass(frozen=True, slots=True)
class FiniteModel:
    """A defensively copied, validated finite model."""

    domains: Mapping[str, tuple[str, ...]]
    constants: Mapping[str, str]
    relations: Mapping[str, frozenset[tuple[str, ...]]]
    environment_id: str
    model_id: str

    @classmethod
    def from_json(cls, env: Any, data: str | bytes) -> "FiniteModel":
        from .wire import loads_json
        return cls.from_dict(env, loads_json(data))

    @classmethod
    def from_dict(cls, env: Any, wire: Any) -> "FiniteModel":
        _keys(wire, {"complete", "domains", "constants", "relations"}, "")
        if wire["complete"] is not True:
            _fail("complete must be the Boolean true", "/complete")
        for field in ("domains", "constants", "relations"):
            if not isinstance(wire[field], dict):
                _fail("expected an object", f"/{field}")

        sort_names = set(env.sorts)
        predicate_names = set(env.predicates)
        constant_names = set(env.constants)
        if set(wire["domains"]) != sort_names:
            _fail("domains must contain exactly the declared sorts", "/domains")
        if set(wire["constants"]) != constant_names:
            _fail("constants must contain exactly the declared constants", "/constants")
        if set(wire["relations"]) != predicate_names:
            _fail("relations must contain exactly the declared predicates", "/relations")

        domains: dict[str, tuple[str, ...]] = {}
        for sort in sorted(sort_names):
            raw = wire["domains"][sort]
            if not isinstance(raw, list):
                _fail("domain must be an array", f"/domains/{sort}")
            if len(raw) > MAX_ENTITIES:
                raise ResourceLimit("domain exceeds entity limit", path=f"/domains/{sort}")
            values = tuple(_local_id(x, f"/domains/{sort}/{i}") for i, x in enumerate(raw))
            if len(set(values)) != len(values):
                _fail("duplicate domain entity", f"/domains/{sort}")
            domains[sort] = tuple(sorted(values))

        constants: dict[str, str] = {}
        for name in sorted(constant_names):
            value = _local_id(wire["constants"][name], f"/constants/{name}")
            sort = env.constants[name].sort
            if value not in domains[sort]:
                _fail("constant denotes an entity outside its sort", f"/constants/{name}")
            constants[name] = value

        if sum(len(raw) for raw in wire["relations"].values() if isinstance(raw, list)) > MAX_TUPLES:
            raise ResourceLimit("model exceeds total relation tuple limit", path="/relations")
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
                row = tuple(_local_id(x, f"/relations/{name}/{i}/{j}") for j, x in enumerate(item))
                for j, (value, sort) in enumerate(zip(row, signature, strict=True)):
                    if value not in domains[sort]:
                        _fail("relation tuple contains a dangling or wrong-sort entity", f"/relations/{name}/{i}/{j}")
                tuples.append(row)
            if len(set(tuples)) != len(tuples):
                _fail("duplicate relation tuple", f"/relations/{name}")
            tuple_count += len(tuples)
            if tuple_count > MAX_TUPLES:
                raise ResourceLimit("model exceeds total relation tuple limit", path="/relations")
            relations[name] = frozenset(tuples)

        normalized = {
            "complete": True,
            "domains": {k: list(domains[k]) for k in sorted(domains)},
            "constants": {k: constants[k] for k in sorted(constants)},
            "relations": {k: [list(x) for x in sorted(relations[k])] for k in sorted(relations)},
        }
        from .wire import digest
        environment_id = env.environment_id
        model_id = digest(f"ve-model-{env.identity_version}\n", {"environment_id": environment_id, "model": normalized})
        return cls(MappingProxyType(domains), MappingProxyType(constants), MappingProxyType(relations), environment_id, model_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "complete": True,
            "domains": {k: list(self.domains[k]) for k in sorted(self.domains)},
            "constants": {k: self.constants[k] for k in sorted(self.constants)},
            "relations": {k: [list(x) for x in sorted(self.relations[k])] for k in sorted(self.relations)},
        }
