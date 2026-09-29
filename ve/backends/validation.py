"""Lean validation adapters for the `Environment` and `FiniteModel` constructors.

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

_ACCEPTED: dict[tuple, bool] = {}
_LIMIT = 1 << 14
# Statement layers whose validity Lean's environment and model modes refuse
# (their own routes validate them).
_LAYERED = frozenset({"soft-norms@0", "reports@0"})


def _nary_definitions(profiles, predicates) -> bool:
    """A core-family vocabulary with an n-ary defined predicate: Lean's core
    layer glue projects unary and binary predicates only (a recorded gap)."""
    if not {"closure@0", "nary@0"} <= set(profiles):
        return False
    return any(type(entry) is dict and "defined" in entry and type(entry.get("arguments")) is list
               and len(entry["arguments"]) > 2 for entry in predicates)


def environment_in_scope(data) -> bool:
    """Whether Lean's `environment` mode validates this environment input."""
    if type(data) is not dict or data.get("language") != "ve.core@0.2":
        return False
    if {"unit_schema", "units", "alternatives"} & set(data):
        return False
    profiles = data.get("profiles")
    if type(profiles) is not list:
        return True
    profiles = {p for p in profiles if type(p) is str}
    vocabulary = data.get("vocabulary")
    predicates = vocabulary.get("predicates") if type(vocabulary) is dict else None
    return not (_LAYERED & profiles) and not (
        type(predicates) is dict and _nary_definitions(profiles, predicates.values()))


def model_in_scope(env) -> bool:
    """Whether Lean's `model` mode validates models over `env`."""
    return (env.language == "ve.core@0.2" and env.unit_schema is None and env.alternatives is None
            and not _LAYERED & set(env.profiles)
            and not ({"closure@0", "nary@0"} <= set(env.profiles) and any(
                decl.defined is not None and len(decl.arguments) > 2 for decl in env.predicates.values())))


def _key(*parts) -> tuple:
    return tuple(hashlib.sha256(canonical_json(part)).hexdigest() for part in parts)


def _remember(key: tuple) -> None:
    if len(_ACCEPTED) >= _LIMIT:
        _ACCEPTED.clear()
    _ACCEPTED[key] = True


def _decided(decode: Callable[[], object], key: tuple | None, ask: Callable[[], dict],
             identity: Callable[[object, dict], bool], what: str):
    """Run the structural decoder, then apply Lean's verdict to its outcome."""
    try:
        built, error = decode(), None
    except VEError as exc:
        built, error = None, exc
    if key is None:
        # The input is not JSON on the restricted wire subset, so no checker
        # can read it; the wire check is Python's and is not a verdict.
        raise error
    if error is None and key in _ACCEPTED:
        return built
    try:
        row = ask()
    except VEError as rejected:
        raise (error if error is not None else rejected) from None
    if error is not None:
        raise CheckerUnavailable(f"CheckerUnavailable: Lean accepts {what} that the Python decoder "
                                 f"rejects ({error.code}: {error.message})")
    if not identity(built, row):
        raise CheckerUnavailable(f"CheckerUnavailable: Lean and Python {what} identities differ")
    _remember(key)
    return built


def validated_environment(env, data, decode: Callable[[], object]):
    """`decode()` builds `env` from `data`; Lean decides its validity."""
    from .lean_runner import run
    try:
        key = _key("environment", data)
    except (VEError, TypeError, ValueError, RecursionError):
        key = None
    return _decided(decode, key,
                    lambda: run("environment", [{"id": "environment", "environment": data}])[0],
                    lambda built, row: row.get("environment_id") == built.environment_id,
                    "an environment")


def validated_model(env, wire, decode: Callable[[], object]):
    """`decode()` builds a model of `env` from `wire`; Lean decides its validity."""
    from .lean_runner import run
    try:
        key = _key("model", env.environment_id, wire)
    except (VEError, TypeError, ValueError, RecursionError):
        key = None
    return _decided(decode, key,
                    lambda: run("model", [{"id": "model", "environment": env.to_dict(), "model": wire}])[0],
                    lambda built, row: row.get("valid") is True and row.get("model_id") == built.model_id,
                    "a model")
