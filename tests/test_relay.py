"""`ve/backends/relay.py`, the one Python entry to Lean's decisions (docs/LEAN-FIRST-PLAN.md,
rule 2, batch 0): Lean's code chooses the exception class and Lean's text is raised verbatim;
only operational failures are Python's own (`CheckerUnavailable`)."""
from __future__ import annotations

import ast as ast_module
import json
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT
from tests.probe_matrix import raw_environment
from ve import Environment
from ve.admission import AdmissionError
from ve.ast import Const, Unary, formula_to_data
from ve.backends import lean as lean_backend, relay
from ve.backends.service_schema import DIRECTORY as SCHEMAS
from ve.errors import (CheckerUnavailable, InvalidModel, ResourceLimit, UnknownSymbol, UnsupportedProfile,
                       VEError)

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
needs_service = pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
HANDSHAKE_CODES = json.loads((SCHEMAS / "envelope.json").read_text())["handshake"]["properties"]["codes"]["const"]
ROW_CODES = json.loads((SCHEMAS / "common.json").read_text())["$defs"]["code"]["enum"]


def test_one_class_per_code_of_the_service():
    """The class table, the handshake the client requires and the rows' code domain are one list."""
    assert list(relay.CLASSES) == HANDSHAKE_CODES == ROW_CODES


@needs_service
def test_the_service_states_the_code_list_the_client_requires():
    from ve.backends.lean_service import LeanService
    with LeanService(SERVICE) as service:
        assert service.handshake["codes"] == HANDSHAKE_CODES


class _Pool:
    """A pool whose service answers `rows`, each bound with the code beside it (`coding`)."""

    def __init__(self, rows):
        self.rows, self.calls = rows, []

    def run_bound(self, mode, cases, *, timeout=None):
        self.calls.append((mode, cases, timeout))
        return [{"index": i, "digest": "0" * 64,
                 "result": {k: v for k, v in row.items() if k not in ("code", "generator")},
                 **{k: row[k] for k in ("code", "generator") if k in row}} for i, row in enumerate(self.rows)]

    def close(self):
        pass


@pytest.mark.parametrize("code, cls", [(code, cls) for code, cls in relay.CLASSES.items()
                                       if code != "CheckerUnavailable"])
def test_each_code_raises_its_class_with_the_text_verbatim(monkeypatch, code, cls):
    text = f"{code}: Lean's own words, kept: as sent"
    monkeypatch.setattr(relay, "_pool", _Pool([{"id": "a", "status": "ok"},
                                               {"id": "b", "status": "error", "error": text, "code": code}]))
    with pytest.raises(VEError) as caught:
        relay.decide("check", [{"id": "a"}, {"id": "b"}])
    expected = cls or AdmissionError
    assert type(caught.value) is expected and caught.value.code == expected.code
    assert caught.value.message == text and str(caught.value) == text
    assert caught.value.backend_rejection is True


def test_a_rejection_does_not_lose_its_generator(monkeypatch):
    row = {"id": "a", "status": "error", "error": "InvalidModel(literals): x", "code": "InvalidModel",
           "generator": "literals"}
    monkeypatch.setattr(relay, "_pool", _Pool([row]))
    with pytest.raises(InvalidModel) as caught:
        relay.decide("route", [{"id": "a"}])
    assert caught.value.to_dict() == {"code": "InvalidModel", "message": "InvalidModel(literals): x",
                                      "generator": "literals"}


@pytest.mark.parametrize("code", ["DependencyCycle", "", "unknownsymbol", "InvalidInput "])
def test_an_unknown_code_is_operational(monkeypatch, code):
    monkeypatch.setattr(relay, "_pool", _Pool([{"id": "a", "status": "error", "error": "x", "code": code}]))
    with pytest.raises(CheckerUnavailable, match="unknown code"):
        relay.decide("check", [{"id": "a"}])


def test_lean_checker_unavailable_is_operational(monkeypatch):
    row = {"id": "a", "status": "error", "error": "CheckerUnavailable: x", "code": "CheckerUnavailable"}
    monkeypatch.setattr(relay, "_pool", _Pool([row]))
    with pytest.raises(CheckerUnavailable, match="^CheckerUnavailable: x$"):
        relay.decide("check", [{"id": "a"}])


def test_rows_are_returned_in_order_and_unchanged(monkeypatch):
    rows = [{"id": str(i), "status": "ok", "value": i} for i in range(3)]
    pool = _Pool(rows)
    monkeypatch.setattr(relay, "_pool", pool)
    assert relay.decide("evaluate", [{"id": "0"}], timeout=7.0) == rows
    assert pool.calls == [("evaluate", [{"id": "0"}], 7.0)]


@needs_service
def test_genuine_typing_rejection_is_leans(monkeypatch):
    """Lean's code and text, unstripped: `UnknownSymbol: ...` (wording list W1 of DELTA.md)."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    env = Environment(raw_environment(()))
    ast = json.loads(json.dumps(formula_to_data(env, Unary("base", Const("x")))).replace('"base"', '"missing"'))
    case = {"id": "c", "environment": env.to_dict(), "ast": ast}
    with pytest.raises(UnknownSymbol) as caught:
        relay.decide("check", [case])
    assert caught.value.message.startswith("UnknownSymbol: ")


@needs_service
def test_genuine_request_error_carries_leans_code():
    from ve.backends.lean_service import LeanService
    with LeanService(SERVICE) as service:
        _, response = service.exchange("evaluate", "[{},{}]", 2, budget={"cases": 1, "bytes": 1 << 20})
    assert response["status"] == "error" and response["code"] == "ResourceLimit"
    error = relay.rejection(response["code"], response["error"])
    assert type(error) is ResourceLimit and error.message == "ResourceLimit: batch has 2 cases; budget is 1"


@needs_service
def test_genuine_profile_rejection_is_leans(monkeypatch):
    raw = raw_environment(())
    raw["profiles"] = 7
    with pytest.raises(UnsupportedProfile, match="^UnsupportedProfile: "):
        relay.decide("environment", [{"id": "e", "environment": raw}])


# The one-shot runner transports (`ve/backends/lean.py`): every one reads its runner's output with
# `read_rows`, so output that is no answer is `CheckerUnavailable` on every path, never a rejection
# (lf-0 review B1 and B2; reproducers from the difffuzz looprecheck3 review).

CASE = {"id": "0", "kind": "bundle"}


def _runner(tmp_path, stdout: bytes, status: int):
    """A runner that reads its cases and answers `stdout` with exit status `status`."""
    out = tmp_path / "out.bin"
    out.write_bytes(stdout)
    path = tmp_path / "runner"
    path.write_text(f"#!/bin/sh\ncat >/dev/null\ncat '{out}'\nexit {status}\n")
    path.chmod(0o755)
    return path


def _soft(exe, case):
    return lean_backend.run_soft_case(exe, case, timeout=HANG_TIMEOUT)


TRANSPORTS = {
    "run": lambda exe, case: lean_backend.run("bundle.check", exe, [case], runner="ve_conformance",
                                              mode="route", timeout=HANG_TIMEOUT)[0],
    "soft": _soft,
    "alternatives": lambda exe, case: lean_backend.run_alternatives_case(exe, case, timeout=HANG_TIMEOUT),
    "discourse": lambda exe, case: lean_backend.run_discourse_case(exe, case, timeout=HANG_TIMEOUT),
    "reports": lambda exe, case: lean_backend.run_reports_case(exe, case, timeout=HANG_TIMEOUT),
    "norm-defaults": lambda exe, case: lean_backend.run_norm_defaults_cases(exe, [case], timeout=HANG_TIMEOUT)[0],
    "readings": lambda exe, case: lean_backend.run_readings_cases(exe, [case], timeout=HANG_TIMEOUT)[0],
}
CODED = {"soft"}


def test_every_runner_transport_is_listed():
    """Every function of `ve/backends/lean.py` that starts a runner reads its output with
    `read_rows` (through `_route_rows` or directly), and is in TRANSPORTS; nothing else in the
    module decodes runner output."""
    tree = ast_module.parse((ROOT / "ve/backends/lean.py").read_text())
    starts, decodes = set(), set()
    for node in tree.body:
        if isinstance(node, ast_module.FunctionDef):
            calls = {(c.func.attr if isinstance(c.func, ast_module.Attribute) else getattr(c.func, "id", None))
                     for c in ast_module.walk(node) if isinstance(c, ast_module.Call)}
            if "run" in calls and any(isinstance(c, ast_module.Attribute) and c.attr == "run"
                                      and getattr(c.value, "id", None) == "subprocess"
                                      for c in ast_module.walk(node)):
                starts.add(node.name)
                assert calls & {"read_rows", "_route_rows"}, node.name
            if calls & {"loads", "loads_json", "_decode_json"}:
                decodes.add(node.name)
    assert decodes == {"read_rows"}
    public = {name for name in starts if not name.startswith("_")} | {
        node.name for node in tree.body if isinstance(node, ast_module.FunctionDef)
        and any(getattr(c.func, "id", None) == "_route_rows" for c in ast_module.walk(node)
                if isinstance(c, ast_module.Call))}
    names = {"run": "run", "soft": "run_soft_case", "alternatives": "run_alternatives_case",
             "discourse": "run_discourse_case", "reports": "run_reports_case",
             "norm-defaults": "run_norm_defaults_cases", "readings": "run_readings_cases"}
    assert public == {names[key] for key in TRANSPORTS}


def _row(**fields):
    return json.dumps([{"id": "0", **fields}]).encode()


# Output that is no answer to CASE on any transport: (stdout, exit status).
NO_ANSWER = {
    # B1: text that is not Unicode (a lone surrogate) or not UTF-8.
    "surrogate-error": (_row(status="error", error="\ud800"), 1),
    "surrogate-success": (_row(status="ok", value="\ud800"), 0),
    "surrogate-key": (b'[{"id":"0","status":"ok","\\udc00":1}]', 0),
    "surrogate-pair-split": (_row(status="ok", value="\udbff\u0041"), 0),
    "not-utf8": (b'[{"id":"0","status":"ok","value":"\xff"}]', 0),
    # B2: mixed identity, or a code or error beside a success.
    "mixed-identity-error": (json.dumps([{"id": "0", "case_index": 0, "status": "error",
                                          "error": "InvalidInput: invalid vocabulary",
                                          "code": "SOFT_UNKNOWN_RANK"}]).encode(), 1),
    "mixed-identity-plain": (json.dumps([{"id": "0", "case_index": 0, "status": "error",
                                          "error": "x"}]).encode(), 1),
    "mixed-identity-success": (json.dumps([{"id": "0", "case_index": 0, "status": "ok"}]).encode(), 0),
    "position-row-with-code": (json.dumps([{"case_index": 0, "status": "error", "error": "x",
                                            "code": "SOFT_UNKNOWN_RANK"}]).encode(), 1),
    "position-row-with-field": (json.dumps([{"case_index": 0, "status": "error", "error": "x",
                                             "generator": "flags"}]).encode(), 1),
    "position-row-valid-true": (json.dumps([{"case_index": 0, "status": "error", "error": "x",
                                             "valid": True}]).encode(), 1),
    "code-beside-success": (_row(status="ok", code="SOFT_UNKNOWN_RANK"), 0),
    "error-beside-success": (_row(status="ok", error="x"), 0),
    "empty-code": (_row(status="error", error="x", code=""), 1),
    "non-text-code": (_row(status="error", error="x", code=7), 1),
    "no-error-text": (_row(status="error"), 1),
    "duplicate-field": (b'[{"id":"0","id":"0","status":"ok"}]', 0),
    "non-finite": (b'[{"id":"0","status":"ok","value":NaN}]', 0),
    "too-deep": (b'[{"id":"0","status":"ok","value":' + b"[" * 100_000 + b"]" * 100_000 + b"}]", 0),
    "two-rows": (json.dumps([{"id": "0", "status": "ok"}] * 2).encode(), 0),
    "exit-2": (_row(status="ok"), 2),
    "ok-exit-1": (_row(status="ok"), 1),
    "error-exit-0": (_row(status="error", error="x"), 0),
}


def _mutants():
    """Genuine rows with one field dropped, retyped or duplicated, or a foreign identity added:
    none is an answer to CASE (checklist line 4)."""
    genuine = {"ok": ({"id": "0", "status": "ok"}, 0), "error": ({"id": "0", "status": "error", "error": "x"}, 1)}
    for kind, (row, status) in genuine.items():
        for name in row:
            yield f"{kind}-drop-{name}", {k: v for k, v in row.items() if k != name}, status
            # Every retyping, and for the identity and status fields a near-miss of the same type.
            near = {"id": (0, "0 "), "status": ("OK", "")}.get(name, ())
            for bad in (7, True, None, [], {}, "\ud800", *near):
                yield f"{kind}-{name}-{bad!r}", {**row, name: bad}, status
        yield f"{kind}-case-index", {**row, "case_index": 0}, status
        yield f"{kind}-false-case-index", {**row, "case_index": False}, status
    yield "ok-code", {"id": "0", "status": "ok", "code": "InvalidInput"}, 0
    yield "ok-error", {"id": "0", "status": "ok", "error": ""}, 0


MUTANTS = {name: (json.dumps([row]).encode(), status) for name, row, status in _mutants()}


@pytest.mark.parametrize("transport", TRANSPORTS)
@pytest.mark.parametrize("fault", [*NO_ANSWER, *MUTANTS])
def test_output_that_is_no_answer_is_checker_unavailable(tmp_path, transport, fault):
    stdout, status = NO_ANSWER.get(fault) or MUTANTS[fault]
    with pytest.raises(CheckerUnavailable):
        TRANSPORTS[transport](_runner(tmp_path, stdout, status), CASE)


@pytest.mark.parametrize("transport", sorted(set(TRANSPORTS) - CODED))
def test_a_code_on_a_route_without_codes_is_no_answer(tmp_path, transport):
    exe = _runner(tmp_path, _row(status="error", error="x", code="InvalidInput"), 1)
    with pytest.raises(CheckerUnavailable):
        TRANSPORTS[transport](exe, CASE)


def test_the_soft_routes_coded_rejection_keeps_its_code(tmp_path):
    """The control of the reproducer: the same row without `case_index` is the route's rejection."""
    exe = _runner(tmp_path, _row(status="error", error="InvalidInput: invalid vocabulary",
                                 code="SOFT_UNKNOWN_RANK"), 1)
    with pytest.raises(VEError) as caught:
        _soft(exe, CASE)
    assert caught.value.code == "SOFT_UNKNOWN_RANK" and caught.value.message == "InvalidInput: invalid vocabulary"


@pytest.mark.parametrize("transport", TRANSPORTS)
def test_genuine_rows_are_answers(tmp_path, transport):
    """Controls: a case rejection, a position row and (but for `run`, whose binding requires
    fields) a success are rows on every transport; the soft route raises its rejections."""
    for stdout, status in ((_row(status="error", error="E: x"), 1),
                           (json.dumps([{"case_index": 0, "status": "error", "error": "E: x"}]).encode(), 1),
                           (_row(status="ok", value="é ok"), 0)):
        if transport == "run" and status == 0:
            continue
        exe = _runner(tmp_path, stdout, status)
        if transport == "soft" and status == 1:
            with pytest.raises(VEError, match="^E: x$"):
                _soft(exe, CASE)
        else:
            assert TRANSPORTS[transport](exe, CASE) == json.loads(stdout)[0]


def test_the_rust_checker_output_is_read_by_the_same_decoder(tmp_path):
    import hashlib
    from ve.backends import rust_jsonl
    exe = tmp_path / "rust"
    out = tmp_path / "out.bin"
    out.write_bytes(b'{"id":"0","status":"error","error":"\\ud800"}\n')
    exe.write_text(f"#!/bin/sh\ncat >/dev/null\ncat '{out}'\nexit 1\n")
    exe.chmod(0o755)
    with pytest.raises(CheckerUnavailable, match="malformed"):
        rust_jsonl.run({"id": "0"}, executable=exe, timeout=HANG_TIMEOUT,
                       expected_sha256=hashlib.sha256(exe.read_bytes()).hexdigest())


@pytest.mark.parametrize("text", [b'["\\ud800"]', b'{"\\udfff":1}', b'[["\\ud83d"]]', b'["\xff"]'])
def test_the_checker_output_decoder_refuses_text_that_is_not_unicode(text):
    from ve.backends.lean_service import _decode_json
    with pytest.raises(ValueError):
        _decode_json(text)
    assert _decode_json(b'["\\ud83d\\ude00"]') == ["\U0001F600"]


# The relay itself, over a scripted service (the persistent path): the same answers are
# operational there too.

@pytest.mark.parametrize("result, coding", [
    ({"id": "c", "status": "error", "error": "\ud800"}, {"code": "InvalidInput"}),
    ({"id": "c", "case_index": 0, "status": "error", "error": "InvalidInput: invalid vocabulary"},
     {"code": "InvalidInput"}),
    ({"id": "c", "status": "error", "error": "rejected", "code": "InvalidInput"}, {"code": "InvalidInput"}),
    ({"id": "c", "status": "ok", "kind": "source", "identity_id": "0" * 64}, {"code": "InvalidInput"}),
    ({"id": "c", "status": "ok", "kind": "source", "identity_id": "0" * 64, "code": "InvalidInput"}, {}),
])
def test_the_relay_turns_malformed_service_answers_into_checker_unavailable(tmp_path, monkeypatch, result, coding):
    from tests.test_lean_service import fake
    from ve.backends.lean_service import LeanServicePool
    answer = {"__bound__": True, "id": "__nonce__", "status": "ok", "mode": "identity",
              "results": [{"index": 0, "digest": {"$digest": 0}, "result": result, **coding}],
              "counts": {"cases": 1, "bytes": "__bytes__", "errors": int(result["status"] == "error")}}
    (tmp_path / "marker").write_text(json.dumps(answer))
    pool = LeanServicePool(1, executable=fake(tmp_path, "scripted"), allow_unlisted_build=True)
    monkeypatch.setattr(relay, "_pool", pool)
    try:
        with pytest.raises(CheckerUnavailable):
            relay.decide("identity", [{"id": "c", "kind": "source", "source": "x"}])
    finally:
        pool.close()
