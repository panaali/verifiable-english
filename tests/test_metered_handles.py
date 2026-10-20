"""The decoded environment the service keeps with each handle (lean-first batch 18, DRI note F7; the
unbuilt half of LEAN-FIRST-PLAN F2).

`VE.Service.Entry` keeps what the `metered` mode decodes from a registered environment alone
(`VE.Route.MeteredRun.prepare`) beside it in the handle table, so it is replaced or dropped exactly with its
handle (`caseResult_cached`: the answer is the answer to the case with its environment re-sent). The client
keeps the decoded environments its response checks read the same way (`LeanService._decoded_environment`).
"""
from __future__ import annotations

import json

import pytest

from tests.lean_build import lean_build
from tests.probe_matrix import model_wire, raw_environment
from ve import Environment, FiniteModel
from ve.ast import And, Bottom, Exists, Forall, Implies, Not, Top, Unary, Var, Const
from ve.backends.lean_runner import encoded_formula, encoded_model, metered_environment
from ve.backends.lean_service import HANDLE_KEY, MAX_HANDLES, LeanService, case_digest
from ve.backends.service_schema import same_json

pytestmark = pytest.mark.live_service

# Every family's vocabulary decoder (`Prepared.route`, `.order`, `.core`) and the layered core one (`.layered`).
PROFILES = ((), ("closure@0",), ("closure@0", "nary@0"), ("order@0",), ("definitions@0",))
FORMULAS = (Top(), Bottom(), Unary("base", Const("x")), Forall("item", Unary("base", Var(0))),
            Exists("item", Not(Unary("base", Var(0)))), And(Top(), Implies(Bottom(), Top())))


@pytest.fixture(scope="module")
def executable():
    return lean_build("ve_service") / "ve_service"


def _cases(profiles, relations=None, extra=False) -> list[dict]:
    raw = raw_environment(profiles)
    if extra:
        raw["vocabulary"]["predicates"]["extra"] = {"arguments": ["item"], "description": "extra"}
    env = Environment(raw)
    wire = model_wire(env)
    if relations is not None:
        wire["relations"] = {**wire["relations"], **relations}
    model = FiniteModel.from_dict(env, wire)
    environment = metered_environment(env)
    cases = []
    for n, formula in enumerate(FORMULAS):
        kind = "non-vacuity" if n % 3 == 2 else "evaluate-budgeted"
        case = {"id": f"{'-'.join(profiles) or 'fol'}-{n}", "kind": kind, "environment": environment,
                "model": encoded_model(model)}
        if kind == "non-vacuity":
            case.update(formula=encoded_formula(formula), max_evaluations=1000)
        else:
            case.update(ast=[encoded_formula(formula)], max_evaluations=1000, max_trace_nodes=1000,
                        trace=n % 2 == 0)
        cases.append(case)
    return cases


def _answers(entries: list) -> list:
    return [entry["result"] for entry in entries]


def _interleaved() -> list[dict]:
    """One case of each environment in turn, two environments of one family among them whose answers
    differ: the second declares one more predicate, which its model gives, and `base` holds of nothing
    in it, so its cases neither decode nor answer alike under the first's vocabulary."""
    groups = [_cases(profiles) for profiles in PROFILES] + [_cases((), relations={"base": []}, extra=True)]
    return [case for row in zip(*groups) for case in row]


def _text(environment) -> str:
    return environment.text if hasattr(environment, "text") else json.dumps(
        environment, ensure_ascii=False, separators=(",", ":"))


def test_interleaved_handles_answer_each_case_as_its_own_environment_does(executable):
    """Requests on six handles with different environments, alternating one case per request: every
    answer is the answer with the environment re-sent, and every case after an environment's first is
    answered by its handle (so by the decoding kept with it)."""
    cases = _interleaved()
    with LeanService(executable, handles=True) as handled, LeanService(executable, handles=False) as inline:
        with_handles = [_answers(handled.run_bound("metered", [case]))[0] for case in cases]
        resent = [_answers(inline.run_bound("metered", [case]))[0] for case in cases]
        stats = dict(handled.stats)
    assert same_json(with_handles, resent)
    assert all(row["status"] == "ok" for row in resent), [row for row in resent if row["status"] != "ok"]
    # The two environments of one family answer some case differently: a decoding answered for the
    # wrong handle could not pass.
    first, last = [row for row in resent if row["id"] == "fol-3"]
    assert first != last
    assert stats["registered"] == len(PROFILES) + 1 and stats["handle_resends"] == 0


def _line_case(digest: str, case: dict) -> str:
    rest = {key: value for key, value in case.items() if key != "environment"}
    return json.dumps({**rest, HANDLE_KEY: digest}, ensure_ascii=False, separators=(",", ":"))


def _row(service: LeanService, case: dict, environments: dict | None = None) -> dict:
    digest = case_digest(_text(case["environment"]))
    _, response = service.exchange("metered", "[" + _line_case(digest, case) + "]", 1,
                                   environments=environments)
    return response


def test_a_dropped_or_refused_handle_never_answers_from_its_old_decoding(executable):
    """Close a handle (the table is emptied once more than `MAX_HANDLES` environments are registered) and
    try to replace one (register another text under its digest), then name the handle again: the dropped
    handle is a miss, never an answer from the decoding it held, and the refused replacement leaves the
    handle answering with its own environment."""
    case = _cases(())[3]
    other = _cases(("order@0",))[3]
    text = _text(case["environment"])
    digest = case_digest(text)
    with LeanService(executable, handles=False) as inline:
        expected = _answers(inline.run_bound("metered", [case]))[0]
    with LeanService(executable) as service:
        response = _row(service, case, {digest: text})
        assert response["status"] == "ok" and same_json(response["results"][0]["result"], expected)
        # Replace: the order environment's text under this digest is refused, and changes no handle.
        service._registered.pop(digest)  # so that the client sends the registration at all
        response = _row(service, case, {digest: _text(other["environment"])})
        assert response["status"] == "error" and response["code"] == "InvalidInput"
        response = _row(service, case)
        assert response["status"] == "ok" and same_json(response["results"][0]["result"], expected)
        # Close: registering MAX_HANDLES more environments empties the table, this handle first.
        for n in range(MAX_HANDLES):
            filler = json.dumps({**raw_environment(()), "spec_revision": f"r{n}"}, separators=(",", ":"))
            service.exchange("environment", '[{"id":"e","%s":"%s"}]' % (HANDLE_KEY, case_digest(filler)), 1,
                             environments={case_digest(filler): filler})
        response = _row(service, case)
        assert response["status"] == "error" and response["code"] == "CheckerUnavailable"
        assert response["error"] == f"CheckerUnavailable: environment handle {digest} is not registered"
        # Reusing the id registers it again, and it answers as before.
        response = _row(service, case, {digest: text})
        assert response["status"] == "ok" and same_json(response["results"][0]["result"], expected)


def test_the_client_keeps_one_decoding_per_environment_text():
    """The client's decoded environments are keyed by the digest of their text, are each that text's
    decoding, and are bounded by `MAX_HANDLES` (the oldest dropped first)."""
    service = LeanService(handles=True)
    texts = [json.dumps({**raw_environment(()), "spec_revision": f"r{n}"}, separators=(",", ":"))
             for n in range(MAX_HANDLES + 2)]
    for _ in range(2):
        for text in texts[:3]:
            assert service._decoded_environment(case_digest(text), text) == json.loads(text)
    assert service._decoded_environment(case_digest(texts[0]), texts[0]) is \
        service._decoded_environment(case_digest(texts[0]), texts[0])
    for text in texts:
        assert service._decoded_environment(case_digest(text), text) == json.loads(text)
    assert len(service._decoded) == MAX_HANDLES
    assert case_digest(texts[0]) not in service._decoded and case_digest(texts[-1]) in service._decoded
