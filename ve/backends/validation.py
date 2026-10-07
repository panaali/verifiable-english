"""Lean decides environment and model validity; Python builds accepted containers.

A constructor failure after Lean acceptance is an operational checker failure,
never a second diagnostic. Accepted verdicts are cached by canonical input.
"""
from __future__ import annotations

import hashlib
from typing import Callable

from ..errors import CheckerUnavailable, VEError
from ..wire import canonical_json
from ..profiles import STATEMENT_LAYERS
from .diagnostics import backend_rejection

_ACCEPTED: dict[tuple, bool] = {}
_LIMIT = 1 << 14
_LAYERED = STATEMENT_LAYERS


def nary_core_definitions(profiles, predicates) -> bool:
    """A core-family vocabulary with an n-ary defined predicate: Lean's core
    layer glue projects unary and binary predicates only (a recorded gap)."""
    if not {"closure@0", "nary@0"} <= set(profiles):
        return False
    return any(type(entry) is dict and "defined" in entry and type(entry.get("arguments")) is list
               and len(entry["arguments"]) > 2 for entry in predicates)


# The frozen pre-route envelopes, which Lean's standalone modes decode with
# their frozen decoders (Standalone.decodeLegacy).
LEGACY_LANGUAGES = frozenset({"ve.core@0", "ve.core@0.1"})


def legacy_language(data: dict) -> bool:
    """Whether `data` names a frozen envelope's language; any JSON value may
    stand there before the decoder runs."""
    language = data.get("language")
    return type(language) is str and language in LEGACY_LANGUAGES


def model_in_scope(env) -> bool:
    """Whether Lean's `model` mode validates models over `env`."""
    if env.language in LEGACY_LANGUAGES:
        return True
    return (env.language == "ve.core@0.2" and env.unit_schema is None and env.alternatives is None
            and not _LAYERED & set(env.profiles)
            and not ({"closure@0", "nary@0"} <= set(env.profiles) and any(
                decl.defined is not None and len(decl.arguments) > 2 for decl in env.predicates.values())))


def family_in_scope(env) -> bool:
    """Whether Lean's `graph` and `readings` modes take a ve.core@0.2 envelope of
    any family: no statement layer and no n-ary definition on the core family
    (deferred in Lean)."""
    if env.language != "ve.core@0.2" or env.unit_schema is not None or env.alternatives is not None:
        return False
    if STATEMENT_LAYERS & set(env.profiles):
        return False
    if nary_core_definitions(env.profiles, [{"defined": True, "arguments": list(decl.arguments)}
                                            for decl in env.predicates.values() if decl.defined is not None]):
        return False
    return True


def key(*parts) -> tuple:
    return tuple(hashlib.sha256(canonical_json(part)).hexdigest() for part in parts)


def _remember(key: tuple) -> None:
    if len(_ACCEPTED) >= _LIMIT:
        _ACCEPTED.clear()
    _ACCEPTED[key] = True


def decided(decode: Callable[[], object], cache: tuple | None, ask: Callable[[], dict],
             identity: Callable[[object, dict], bool], what: str):
    """Legacy adapter for bundle and definitions, pending their owner migration."""
    try:
        built, error = decode(), None
    except VEError as exc:
        built, error = None, exc
    if cache is None:
        if error is not None:
            raise error
        raise CheckerUnavailable(f"CheckerUnavailable: {what} cannot be sent to the checker")
    if error is None and cache in _ACCEPTED:
        return built
    try:
        row = ask()
    except VEError as rejected:
        raise (backend_rejection(error) if error is not None else rejected) from None
    if error is not None:
        raise CheckerUnavailable(f"CheckerUnavailable: Lean accepts {what} that the Python decoder "
                                 f"rejects ({error.code}: {error.message.removeprefix(error.code + ': ')})")
    if not identity(built, row):
        raise CheckerUnavailable(f"CheckerUnavailable: Lean and Python {what} identities differ")
    _remember(cache)
    return built


def construct_after_lean(decode: Callable[[], object], cache: tuple | None,
                         ask: Callable[[], dict], identity: Callable[[object, dict], bool], what: str):
    """Ask Lean first, then construct only the accepted environment or model."""
    row = None
    if cache is None or cache not in _ACCEPTED:
        row = ask()
    try:
        built = decode()
    except Exception as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: Python could not construct a Lean-accepted {what}") from exc
    if row is None:
        return built
    if not identity(built, row):
        raise CheckerUnavailable(f"CheckerUnavailable: Lean and Python {what} identities differ")
    if cache is not None:
        _remember(cache)
    return built


def validated_environment(env, data, decode: Callable[[], object]):
    """`decode()` builds `env` from `data`; Lean decides its validity."""
    from .relay import decide
    # Restricted JSON is a wire primitive. Check the environment value itself
    # before wrapping it in a service case, so an offset names the same bytes
    # at every public entry point.
    canonical_json(data)
    try:
        cache = key("environment", data)
    except (VEError, TypeError, ValueError, RecursionError):
        cache = None
    return construct_after_lean(decode, cache,
                    lambda: decide("environment", [{"id": "environment", "environment": data}])[0],
                    lambda built, row: row.get("environment_id") == built.environment_id,
                    "environment")


def validated_model(env, wire, decode: Callable[[], object], *, claimed: dict | None = None):
    """`decode()` builds a model of `env` from `wire`; Lean decides its validity
    and, for a `claimed` identity pair, whether each claimed identity is the
    recomputed one."""
    from .relay import decide
    request = {"id": "model", "environment": env.to_dict(), "model": wire,
               **({"claimed": claimed} if claimed is not None else {})}
    try:
        cache = key("model", env.environment_id, wire, *(() if claimed is None else (claimed,)))
    except (VEError, TypeError, ValueError, RecursionError):
        cache = None
    return construct_after_lean(decode, cache,
                    lambda: decide("model", [request])[0],
                    lambda built, row: row.get("valid") is True and row.get("model_id") == built.model_id,
                    "model")
