"""Defined-value translation for Cedar-style attribute and context lookups.

The Boolean in `Value` is definedness. A missing path never becomes an
ordinary false value, so `has` and comparisons preserve missing-attribute
behavior when a later policy layer consumes them.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..errors import VEError


@dataclass(frozen=True, slots=True)
class Value:
    defined: bool
    value: object = None


def attribute(record: dict, path: tuple[str, ...]) -> Value:
    if type(record) is not dict or type(path) is not tuple or not path or any(
            type(part) is not str or not part for part in path):
        raise VEError("Attribute lookup requires an object and a nonempty string path")
    current = record
    for part in path:
        if type(current) is not dict or part not in current:
            return Value(False)
        current = current[part]
    return Value(True, current)


def has(record: dict, path: tuple[str, ...]) -> bool:
    return attribute(record, path).defined


def compare(record: dict, path: tuple[str, ...], expected: object, operator: str = "==") -> Value:
    """A missing operand leaves either comparison undefined."""
    found = attribute(record, path)
    if not found.defined:
        return Value(False)
    if operator == "==":
        return Value(True, found.value == expected)
    if operator == "!=":
        return Value(True, found.value != expected)
    raise VEError(f"Unsupported attribute comparison {operator!r}")
