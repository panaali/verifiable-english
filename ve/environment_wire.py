"""Cached transport text for an immutable, identity-bound environment.

Adapters use these private dict values only to build checker cases. Public `to_dict()`
continues to return a fresh object. A cache entry is bound by the environment digest and
projection name, so a second Environment with the same identity shares one encoding.
"""
from __future__ import annotations

import json
import threading
import copy


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
