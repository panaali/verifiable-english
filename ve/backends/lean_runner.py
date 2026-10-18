"""The cases public adapters send to the Lean service; `relay.decide` sends them."""
from __future__ import annotations

from ..errors import CheckerUnavailable


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


def metered_environment(env):
    """The environment of a `metered` case (evaluation and non-vacuity answer no environment
    identity), encoded once: the model environment Rust's search reads too
    (`profiles.model_environment`)."""
    from ..environment_wire import encoded_environment
    from ..profiles import model_environment
    return encoded_environment(env, "lean-metered", lambda: model_environment(env.to_dict()))


def evaluation_case(env, case_id: str, ast: list, model: dict) -> tuple[str, dict]:
    """(mode, case) for evaluating the formulas `ast` on `model`; rows carry `values`."""
    case = {"id": case_id, "environment": cached_route_environment(env), "model": model, "ast": ast}
    mode = lean_mode(env)
    # The legacy evaluation runner takes a kind-less case; the others name it.
    return mode, case if mode == "evaluate" else {**case, "kind": "evaluate"}


# The fields of each `metered` answer, by the kind of the case it answers (`metered.json`: the row is
# one of the two alternatives, and the client binds it to the kind it sent).
METERED_FIELDS = {"evaluate-budgeted": {"id", "status", "evaluation"},
                  "non-vacuity": {"id", "status", "suitable", "evaluations", "exhausted"}}


def _metered(case: dict) -> dict:
    """One case of Lean's metered evaluator and non-vacuity check (lean-first batch 15a, the service's
    `metered` mode since batch 18): the owner of every reported evaluation count, trace and
    `ResourceLimit`, and of the non-vacuity of a search witness. Its row, a rejection included; an
    answer of the other kind is no answer."""
    from .relay import rows
    row = rows("metered", [case])[0]
    if row["status"] == "ok" and set(row) != METERED_FIELDS[case["kind"]]:
        raise CheckerUnavailable(f"CheckerUnavailable: the Lean metered answer to a {case['kind']} case "
                                 "is of another kind")
    return row


def metered_evaluation(case: dict) -> dict:
    """One `evaluate-budgeted` case: its row (value, count, trace)."""
    return _metered({**case, "kind": "evaluate-budgeted"})


def metered_nonvacuity(case: dict) -> dict:
    """One `non-vacuity` case: its row (suitable, evaluations, exhausted)."""
    return _metered({**case, "kind": "non-vacuity"})
