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


def has(record: dict, path: tuple[str, ...]) -> Value:
    """A missing parent is undefined; a missing final field is false."""
    if type(record) is not dict or type(path) is not tuple or not path or any(
            type(part) is not str or not part for part in path):
        raise VEError("Attribute lookup requires an object and a nonempty string path")
    if len(path) == 1:
        return Value(True, path[0] in record)
    parent = attribute(record, path[:-1])
    if not parent.defined or type(parent.value) is not dict:
        return Value(False)
    return Value(True, path[-1] in parent.value)


def _cedar_equal(left: object, right: object) -> bool:
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(
            _cedar_equal(left[key], right[key]) for key in left)
    if type(left) is list:
        # Cedar sets ignore order and duplicate members.
        return (all(any(_cedar_equal(a, b) for b in right) for a in left)
                and all(any(_cedar_equal(b, a) for a in left) for b in right))
    return left == right


def compare(record: dict, path: tuple[str, ...], expected: object, operator: str = "==") -> Value:
    """A missing operand leaves either comparison undefined."""
    found = attribute(record, path)
    if not found.defined:
        return Value(False)
    if operator == "==":
        return Value(True, _cedar_equal(found.value, expected))
    if operator == "!=":
        return Value(True, not _cedar_equal(found.value, expected))
    raise VEError(f"Unsupported attribute comparison {operator!r}")
