"""Cached transport text for an immutable, identity-bound environment.

Adapters use these private dict values only to build checker cases. Public `to_dict()`
continues to return a fresh object. A cache entry is bound by the environment digest and
projection name, so a second Environment with the same identity shares one encoding.
`wire_checked` is the check every transport runs on a batch before encoding it.
"""
from __future__ import annotations

import copy
import json
import math
import threading


class _FrozenList(list):
    def __init__(self, values):
        super().__init__(_freeze(value) for value in values)

    def __deepcopy__(self, memo):
        return [copy.deepcopy(value, memo) for value in self]

    def _blocked(self, *args, **kwargs):
        raise TypeError("cached checker environment is immutable")

    __setitem__ = __delitem__ = append = clear = extend = insert = pop = remove = reverse = sort = _blocked
    __iadd__ = __imul__ = _blocked


class _FrozenDict(dict):
    def __init__(self, values):
        super().__init__((key, _freeze(value)) for key, value in values.items())

    def __deepcopy__(self, memo):
        return {key: copy.deepcopy(value, memo) for key, value in self.items()}

    def _blocked(self, *args, **kwargs):
        raise TypeError("cached checker environment is immutable")

    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = __ior__ = _blocked


def _freeze(value):
    if type(value) is dict:
        return _FrozenDict(value)
    if type(value) is list:
        return _FrozenList(value)
    return value


class EncodedEnvironment(_FrozenDict):
    """A JSON object with the exact compact text the transports send."""

    __slots__ = ("_text",)

    def __init__(self, data: dict):
        super().__init__(data)
        object.__setattr__(self, "_text", json.dumps(self, ensure_ascii=False, separators=(",", ":")))

    @property
    def text(self) -> str:
        return self._text

    def __setattr__(self, name, value):
        raise TypeError("cached checker environment is immutable")


_cache: dict[tuple[str, str], EncodedEnvironment] = {}
_lock = threading.Lock()
_LIMIT = 256


def encoded_environment(env, projection: str, build) -> EncodedEnvironment:
    key = (env.environment_id, projection)
    with _lock:
        cached = _cache.get(key)
    if cached is not None:
        return cached
    fresh = EncodedEnvironment(build())
    with _lock:
        if len(_cache) >= _LIMIT:
            _cache.clear()
        return _cache.setdefault(key, fresh)


# Container levels a transport encodes. `json`'s C encoder overflows its stack near 50,000 nested
# objects on this host; every checker's own reader stops far below this (Lean's at 256).
TRANSPORT_DEPTH = 10_000


def wire_checked(cases: list) -> list:
    """`cases`, once each is a JSON value `json` sends as itself; else the wire's `VEError`.

    Every checker transport (the Lean relay, the Rust JSONL adapter) sends only what this admits.
    `json` raises `TypeError` on a set or bytes, `UnicodeEncodeError` on a lone surrogate and
    `ValueError` on a cycle, writes `NaN` (no JSON) for a non-finite float, and quietly sends a
    tuple as a list and an integer key as a string: no checker can read any of these as the
    caller's value, so Python rejects them with the texts of `ve.wire`, as the decoders the
    checkers replaced did. What is JSON (null, a float, any integer, any depth) is sent as it is:
    whether it is on the restricted subset is the checker's decision, in the checker's words
    (rule R9 of batch 9: wording row W9.3 is Lean's depth limit). Only a value nested past
    `TRANSPORT_DEPTH`, which the encoder's C stack may not write, is the wire's runtime limit;
    the walk itself is iterative, so no depth raises `RecursionError`. A cached `EncodedEnvironment` was encoded from an
    environment the wire check already admitted, so it is not walked again."""
    from .errors import ResourceLimit, VEError
    from .wire import validate_json
    if type(cases) is not list:
        raise VEError("Expected a JSON array of cases")
    unsupported = "Unsupported JSON value; null and floating-point numbers are not in v0"
    runtime_limit = "JSON nesting exceeds runtime limit"
    path: set[int] = set()  # the containers above the value being walked
    pending: list = [(False, case, 0) for case in cases]
    while pending:
        leaving, value, depth = pending.pop()
        if leaving:
            path.discard(id(value))
            continue
        kind = type(value)
        if kind is str:
            validate_json(value)  # a lone surrogate
        elif value is None or kind is bool or kind is int:
            pass
        elif kind is float:
            if not math.isfinite(value):
                raise VEError(unsupported)
        elif isinstance(value, EncodedEnvironment):
            pass
        elif kind in (dict, _FrozenDict, list, _FrozenList):
            if depth >= TRANSPORT_DEPTH or id(value) in path:  # a cycle never ends
                raise ResourceLimit(runtime_limit)
            path.add(id(value))
            pending.append((True, value, depth))
            if kind in (dict, _FrozenDict):
                for key in value:
                    if type(key) is not str:
                        raise VEError("JSON object keys must be strings")
                    validate_json(key)
                pending.extend((False, item, depth + 1) for item in value.values())
            else:
                pending.extend((False, item, depth + 1) for item in value)
        else:
            raise VEError(unsupported)
    return cases
