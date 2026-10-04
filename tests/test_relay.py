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
from ve.backends.service_schema import DIRECTORY as SCHEMAS, same_json
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
RESTRICTED = {"run", "alternatives", "reports"}  # `read_rows(restricted=True)`: `ve.wire.loads_json`


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
    restricted = {node.name for node in tree.body if isinstance(node, ast_module.FunctionDef)
                  and any(isinstance(k, ast_module.keyword) and k.arg == "restricted"
                          and getattr(k.value, "value", None) is True for k in ast_module.walk(node))}
    assert restricted == {names[key] for key in RESTRICTED}


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
    # lf-0 looprecheck1 B3: a number no float holds is no answer, never infinity or zero.
    "float-overflow": (b'[{"id":"0","status":"ok","value":1e999}]', 0),
    "float-overflow-negative": (b'[{"id":"0","status":"ok","value":-1.5E+400}]', 0),
    "float-underflow": (b'[{"id":"0","status":"ok","value":1e-999}]', 0),
    "float-overflow-in-error": (b'[{"id":"0","status":"error","error":"x","value":[2e308]}]', 1),
    "too-deep": (b'[{"id":"0","status":"ok","value":' + b"[" * 100_000 + b"]" * 100_000 + b"}]", 0),
    "two-rows": (json.dumps([{"id": "0", "status": "ok"}] * 2).encode(), 0),
    "exit-2": (_row(status="ok"), 2),
    "ok-exit-1": (_row(status="ok"), 1),
    "error-exit-0": (_row(status="error", error="x"), 0),
}


# The identities a submitted case can have: the runners echo the `id` field, `null` for a case
# without one (lf-0 looprecheck1 B2: a row without the field matched a case without one).
CASES = {"string-id": CASE, "no-id": {"kind": "bundle"}}


def _mutants(case):
    """Genuine rows for `case` with one field dropped, retyped or duplicated, or a foreign identity
    added: none is an answer to `case` (checklist line 4)."""
    ident = case.get("id")
    genuine = {"ok": ({"id": ident, "status": "ok"}, 0), "error": ({"id": ident, "status": "error", "error": "x"}, 1)}
    for kind, (row, status) in genuine.items():
        for name in row:
            yield f"{kind}-drop-{name}", {k: v for k, v in row.items() if k != name}, status
            # Every retyping, and for the identity and status fields a near-miss of the same type.
            near = {"id": (0, "0 ", "", False, "null"), "status": ("OK", "")}.get(name, ())
            for bad in (7, True, None, [], {}, "\ud800", *near):
                if not same_json(bad, row[name]):
                    yield f"{kind}-{name}-{bad!r}", {**row, name: bad}, status
        yield f"{kind}-case-index", {**row, "case_index": 0}, status
        yield f"{kind}-false-case-index", {**row, "case_index": False}, status
    yield "ok-code", {"id": ident, "status": "ok", "code": "InvalidInput"}, 0
    yield "ok-error", {"id": ident, "status": "ok", "error": ""}, 0
    # The soft route's coded rejection, naming no case (the looprecheck1 B2 reproducer).
    yield "coded-error-no-id", {"status": "error", "error": "InvalidInput: invalid vocabulary",
                                "code": "SOFT_UNKNOWN_RANK"}, 1


# fault -> (stdout, exit status, the submitted case); the mutants of a case without an id are `no-id-*`.
FAULTS = {name: (stdout, status, CASE) for name, (stdout, status) in NO_ANSWER.items()} | {
    ("" if identity == "string-id" else f"{identity}-") + name: (json.dumps([row]).encode(), status, case)
    for identity, case in CASES.items() for name, row, status in _mutants(case)}


@pytest.mark.parametrize("transport", TRANSPORTS)
@pytest.mark.parametrize("fault", FAULTS)
def test_output_that_is_no_answer_is_checker_unavailable(tmp_path, transport, fault):
    stdout, status, case = FAULTS[fault]
    with pytest.raises(CheckerUnavailable):
        TRANSPORTS[transport](_runner(tmp_path, stdout, status), case)


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
@pytest.mark.parametrize("identity", CASES)
def test_genuine_rows_are_answers(tmp_path, transport, identity):
    """Controls: a case rejection, a position row and (but for `run`, whose binding requires
    fields) a success are rows on every transport, for a case with an id and one without (whose
    rows carry `"id": null`); the soft route raises its rejections. Numbers a float holds are
    read as such, zero included. The transports reading VE's restricted JSON, which has neither
    null nor fractions, refuse rows holding them."""
    case = CASES[identity]

    def row(**fields):
        return json.dumps([{"id": case.get("id"), **fields}]).encode()

    for stdout, status in ((row(status="error", error="E: x"), 1),
                           (json.dumps([{"case_index": 0, "status": "error", "error": "E: x"}]).encode(), 1),
                           (row(status="ok", value="é ok"), 0),
                           (row(status="ok", value=[1.5, -0.0, 1.7976931348623157e308, 5e-324]), 0)):
        if transport == "run" and status == 0:
            continue
        exe = _runner(tmp_path, stdout, status)
        if transport in RESTRICTED and (b"null" in stdout or b"." in stdout):
            with pytest.raises(CheckerUnavailable, match="not a JSON result array"):
                TRANSPORTS[transport](exe, case)
        elif transport == "soft" and status == 1:
            with pytest.raises(VEError, match="^E: x$"):
                _soft(exe, case)
        else:
            assert TRANSPORTS[transport](exe, case) == json.loads(stdout)[0]


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


@pytest.mark.parametrize("number", [b"1e999", b"-1e999", b"1E+309", b"2e308", b"1e-999", b"-0.1e-400", b"1.0e-330"])
def test_the_checker_output_decoder_refuses_numbers_no_float_holds(number):
    """lf-0 looprecheck1 B3: `json` reads them as infinity or zero without `parse_constant`."""
    from ve.backends.lean_service import _decode_json
    with pytest.raises(ValueError, match="outside the float range"):
        _decode_json(b'{"value":' + number + b"}")


@pytest.mark.parametrize("number, value", [(b"0e999", 0.0), (b"-0.0e-999", 0.0), (b"0.000", 0.0), (b"1.5", 1.5),
                                           (b"5e-324", 5e-324), (b"1.7976931348623157e308", 1.7976931348623157e308),
                                           (b"1" + b"0" * 400, 10 ** 400)],
                         ids=["0e999", "-0.0e-999", "0.000", "1.5", "5e-324", "float-max", "integer-1e400"])
def test_the_checker_output_decoder_keeps_numbers_a_float_or_int_holds(number, value):
    from ve.backends.lean_service import _decode_json
    assert _decode_json(b"[" + number + b"]") == [value]


def test_the_rust_checker_output_must_name_its_case(tmp_path):
    """lf-0 looprecheck1 B2 on the Rust reader: a record without `id` (or `false` for case 0) is
    no answer, also to a case without an id; Rust echoes `""` for that case."""
    import hashlib
    from ve.backends import rust_jsonl
    exe, out = tmp_path / "rust", tmp_path / "out.bin"
    exe.write_text(f"#!/bin/sh\ncat >/dev/null\ncat '{out}'\nexit 1\n")
    exe.chmod(0o755)
    run = lambda case: rust_jsonl.run(case, executable=exe, timeout=HANG_TIMEOUT,  # noqa: E731
                                      expected_sha256=hashlib.sha256(exe.read_bytes()).hexdigest())
    for record, case in (({}, {"kind": "evaluate"}), ({"id": False}, {"id": 0}), ({"id": 0}, {"id": False}),
                         ({"id": None}, {"kind": "evaluate"}), ({"id": "0"}, {"id": 0})):
        out.write_text(json.dumps({**record, "status": "error", "error": "UnknownSymbol: x"}) + "\n")
        with pytest.raises(CheckerUnavailable, match="mismatched Rust response id"):
            run(case)
    out.write_text(json.dumps({"id": "", "status": "error", "error": "UnknownSymbol: x"}) + "\n")
    with pytest.raises(UnknownSymbol):
        run({"kind": "evaluate"})


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
