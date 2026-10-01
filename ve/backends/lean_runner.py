"""Lazy shared Lean service client for public adapters."""
from __future__ import annotations

import atexit
import threading

from .diagnostics import require_ok
from .lean_service import LeanServicePool

_pool: LeanServicePool | None = None
_lock = threading.Lock()


def _close() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


atexit.register(_close)


def route_mode(env) -> str:
    """The service mode for a plain route case over a ve.core@0.2 `env`.

    The route decoders reject the `regulated` extension; the norms route
    validates it and answers background, evaluate and countermodel cases.
    """
    return "norms" if any(d.regulated is not None for d in env.predicates.values()) else "route"


def lean_mode(env) -> str:
    """The service mode for evaluate and countermodel cases over `env`.

    ve.core@0.2 envelopes use the route (or the norms route); the frozen
    ve.core@0.1 order envelope uses the order runner; v0 and v0.1 closure
    envelopes use the legacy evaluation runner.
    """
    if env.language == "ve.core@0.2":
        return route_mode(env)
    return "order" if env.order else "evaluate"


def route_environment(env) -> dict:
    """The environment of a route case whose answer carries no environment identity.

    The route gate refuses reports@0, soft-norms@0, speech-acts@0 and rights@0. No Background generator,
    evaluation or countermodel check reads the reports block or the soft
    declarations, so such cases take the vocabulary without them (for reports,
    the one the Lean attribution decoder hands the route decoder,
    lean/VE/Attribution/Wire.lean decodeEnvironment).
    """
    data = env.to_dict()
    if "reports@0" in env.profiles:
        vocabulary = {key: value for key, value in data["vocabulary"].items() if key != "reports"}
        vocabulary["constants"] = {name: {k: v for k, v in entry.items() if k != "verbalisation"}
                                   for name, entry in vocabulary["constants"].items()}
        data = {**data, "vocabulary": vocabulary,
                "profiles": [p for p in data["profiles"] if p != "reports@0"]}
    if "speech-acts@0" in env.profiles:
        # The speech-act scope names addressees and definites; no generator,
        # evaluation or countermodel check reads it (the speech route does).
        data = {**{key: value for key, value in data.items() if key != "speech_acts"},
                "profiles": [p for p in data["profiles"] if p != "speech-acts@0"]}
    if "rights@0" in env.profiles:
        # The rights block declares rights over ordinary vocabulary; its
        # limitation premises are installed by `correlate`, never read from it,
        # and the rights route regenerates them.
        data = {**data, "vocabulary": {key: value for key, value in data["vocabulary"].items()
                                       if key != "rights"},
                "profiles": [p for p in data["profiles"] if p != "rights@0"]}
    if "soft-norms@0" in env.profiles:
        # The soft block and instruction_of name parties and ranks; the soft
        # premises a validated soft document adds are not environment data.
        vocabulary = {key: value for key, value in data["vocabulary"].items() if key != "soft"}
        vocabulary["predicates"] = {name: {k: v for k, v in entry.items() if k != "instruction_of"}
                                    for name, entry in vocabulary["predicates"].items()}
        data = {**data, "vocabulary": vocabulary,
                "profiles": [p for p in data["profiles"] if p != "soft-norms@0"]}
    return data


def evaluation_case(env, case_id: str, ast: list, model: dict) -> tuple[str, dict]:
    """(mode, case) for evaluating the formulas `ast` on `model`; rows carry `values`."""
    case = {"id": case_id, "environment": route_environment(env), "model": model, "ast": ast}
    mode = lean_mode(env)
    # The legacy evaluation runner takes a kind-less case; the others name it.
    return mode, case if mode == "evaluate" else {**case, "kind": "evaluate"}


def run(mode: str, cases: list[dict], *, timeout: float | None = None) -> list[dict]:
    """Send a batch and classify each case diagnostic."""
    global _pool
    with _lock:
        if _pool is None:
            _pool = LeanServicePool()
        pool = _pool
    return [require_ok(row) for row in pool.run(mode, cases, timeout=timeout)]
