"""Lean validation adapters for the `Environment` and `FiniteModel` constructors
(and, through `decided`, for `definitions.compile_definitions`).

Lean's `environment` and `model` service modes decide whether an environment or
a model is valid and recompute its identity. The Python constructor stays the
structural decoder that builds the container (SEMANTICS-MIGRATION-PLAN.md
section 1.1, "kept"); under a backend authority its own validation is never
the verdict:

* Lean rejects: the call raises. When Python's decoder also rejects, its
  diagnostic names the rejection (code and wording are Python's, as the
  typing diagnostics are); otherwise Lean's diagnostic is raised.
* Lean accepts: the container Python built is returned if its identity equals
  the one Lean recomputed. If Python's decoder rejects what Lean accepts, or
  the identities differ, no container exists that Lean vouches for, and the
  call is CheckerUnavailable, never Python's rejection.

Lean's accepted verdicts are cached by the digest of the canonical input.
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


def validated_statement_block(data: dict, kind: str) -> None:
    """Ask the owning statement-layer route before Python materialises its container."""
    from .relay import decide
    case = {"id": "environment", "environment": data}
    if kind == "risk":
        case.update(kind="risk-elaborate", document={"norms": [], "units": []})
    else:
        case.update(kind="alt-elaborate", norms=[])
    decide(kind, [case])


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


def environment_in_scope(data) -> bool:
    """Whether Lean's `environment` mode validates this environment input."""
    if type(data) is dict and legacy_language(data):
        return True
    if type(data) is not dict or data.get("language") != "ve.core@0.2":
        return False
    if {"unit_schema", "units", "alternatives", "speech_acts"} & set(data):
        return False
    profiles = data.get("profiles")
    if type(profiles) is not list:
        return True
    profiles = {p for p in profiles if type(p) is str}
    vocabulary = data.get("vocabulary")
    predicates = vocabulary.get("predicates") if type(vocabulary) is dict else None
    return not (_LAYERED & profiles) and not (
        type(predicates) is dict and nary_core_definitions(profiles, predicates.values()))


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
    """Run the structural decoder, then apply Lean's verdict to its outcome.

    `cache` keys Lean's acceptance (None: the input cannot be sent)."""
    try:
        built, error = decode(), None
    except VEError as exc:
        built, error = None, exc
    if cache is None:
        # The input is not JSON on the restricted wire subset, so no checker
        # can read it; the wire check is Python's and is not a verdict.
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


def validated_environment(env, data, decode: Callable[[], object]):
    """`decode()` builds `env` from `data`; Lean decides its validity."""
    from .relay import decide
    try:
        cache = key("environment", data)
    except (VEError, TypeError, ValueError, RecursionError):
        cache = None
    return decided(decode, cache,
                    lambda: decide("environment", [{"id": "environment", "environment": data}])[0],
                    lambda built, row: row.get("environment_id") == built.environment_id,
                    "an environment")


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
    return decided(decode, cache,
                    lambda: decide("model", [request])[0],
                    lambda built, row: row.get("valid") is True and row.get("model_id") == built.model_id,
                    "a model")
