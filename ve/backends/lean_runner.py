"""The cases public adapters send to the Lean service; `relay.decide` sends them."""
from __future__ import annotations

from pathlib import Path

# Lean's metered evaluator and non-vacuity check (batch 15a), a one-shot runner: the owner of every
# reported evaluation count, trace and `ResourceLimit`, and of the non-vacuity of a search witness.
METERED_EXECUTABLE = Path(__file__).resolve().parents[2] / "lean/.lake/build/bin/ve_metered"


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
    lean/VE/Attribution/Wire.lean decodeEnvironment; for soft-norms, without the
    soft block and `instruction_of`; for speech-acts and rights, without their
    scope and block).
    """
    from ..profiles import STATEMENT_LAYERS, model_environment
    # The statement layers' rows of the one model-reduction table; display text stays.
    return model_environment(env.to_dict(), layers=STATEMENT_LAYERS, display=False)


def cached_route_environment(env) -> dict:
    """The same projection, encoded once for repeated route/evaluation cases."""
    from ..environment_wire import encoded_environment
    return encoded_environment(env, "lean-route", lambda: route_environment(env))


def background_environment(env) -> dict:
    """The environment of a Background case, encoded once: the model environment (`profiles.model_environment`,
    the projection the metered evaluator and Rust's search read, which keeps every Background source), with the
    W6 annotations erased (`units.erased_data`) where no profile row removes them. Lean's route and norms modes
    regenerate Background over it for every registered profile (lean-first batch 13b)."""
    from ..environment_wire import encoded_environment
    from ..profiles import model_environment

    def build():
        data = model_environment(env.to_dict(), display=False)
        if type(data) is dict and "unit_schema" in data:
            from ..units import erased_data
            data = erased_data(data)
        return data
    return encoded_environment(env, "lean-background", build)


def metered_environment(env) -> dict:
    """The environment of a `ve_metered` case (evaluation and non-vacuity answer
    no environment identity): the model environment Rust's search reads too
    (`profiles.model_environment`)."""
    from ..profiles import model_environment
    return model_environment(env.to_dict())


def evaluation_case(env, case_id: str, ast: list, model: dict) -> tuple[str, dict]:
    """(mode, case) for evaluating the formulas `ast` on `model`; rows carry `values`."""
    case = {"id": case_id, "environment": cached_route_environment(env), "model": model, "ast": ast}
    mode = lean_mode(env)
    # The legacy evaluation runner takes a kind-less case; the others name it.
    return mode, case if mode == "evaluate" else {**case, "kind": "evaluate"}


def _metered_timeout() -> float:
    from .lean import ROUTE_TIMEOUT, configured_timeout
    return configured_timeout(ROUTE_TIMEOUT)


def metered_evaluation(case: dict) -> dict:
    """One `evaluate-budgeted` case through `ve_metered`: its row (value, count, trace)."""
    from . import lean
    return lean.run("evaluate", METERED_EXECUTABLE, [case], runner="ve_metered", timeout=_metered_timeout())[0]


def metered_nonvacuity(case: dict) -> dict:
    """One `non-vacuity` case through `ve_metered`: its row (suitable, evaluations, exhausted)."""
    from . import lean
    return lean.run("countermodel.search", METERED_EXECUTABLE, [case], runner="ve_metered",
                    timeout=_metered_timeout())[0]
