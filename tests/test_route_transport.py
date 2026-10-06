"""Every route transport contains every answer that is not Lean's answer to the request (lf-3 looprecheck1 B1
and B2, build checklist 4 and 5), on the transports lean-first batch 1 leaves.

Batch 1 made every statement-layer route a mode of the Lean service: its client binds each result to its case
(position and digest) and checks every row against its mode's schema (`ve/backends/lean_service.py`,
`lean_service_schema/`), and the one-shot transports of `ve/backends/lean.py` were deleted. `read_rows` remains
the one reader of a one-shot runner's output (`lean.run`, for `ve_conformance`): the output is read as bytes
inside the containment, and every row, an error row included, is bound to its case. Each output below must be
no answer to it (B2: a checker writing the byte 0xff made `validate` raise `UnicodeDecodeError`). B1, a genuine
Lean error replayed against valid K1 with its `id` changed, emptied or omitted, used to reject the document; it
is replayed here through the service's client, which must refuse it. Genuine error rows of every route mode
stay rejections. The Rust JSON-lines transport gets the same treatment for its error records.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

import ve.backends.lean as lean_backend
import ve.readings_route as route
from subprocesses import HANG_TIMEOUT
from tests import lean_routes
from tests.test_readings_route_fuzz import units_of
from tests.test_readings_s1_lean import env_k, k1_document
from ve.backends import relay, rust_jsonl
from ve.backends.lean_service import LeanServicePool
from ve.errors import CheckerUnavailable, VEError

ROOT = Path(__file__).resolve().parents[1]
CASE = {"id": "c", "kind": "k"}


def checker(tmp_path, stdout: bytes, returncode: int = 0) -> Path:
    """A temporary checker: it consumes the request, writes `stdout` and exits with `returncode`."""
    answer = tmp_path / "answer"
    answer.write_bytes(stdout)
    script = tmp_path / "checker"
    script.write_text(f"#!/bin/sh\ncat > /dev/null\ncat '{answer}'\nexit {returncode}\n")
    script.chmod(0o755)
    return script


def _rows(*rows) -> bytes:
    return json.dumps(list(rows)).encode()


ERROR = {"id": "c", "status": "error", "error": "InvalidInput: x"}
OK = {"id": "c", "status": "ok"}

# (stdout, exit status) that is no answer to CASE: each must be `CheckerUnavailable`.
MALFORMED = {
    # B2 and its kin: bytes that are not UTF-8 JSON
    "byte 0xff": (b"\xff", 0),
    "0xff inside a string": (b'[{"id": "c", "status": "error", "error": "\xff"}]', 1),
    "UTF-16 JSON": (_rows(ERROR).decode().encode("utf-16"), 1),
    "UTF-32 JSON": (_rows(OK).decode().encode("utf-32-le"), 0),
    "lone surrogate bytes": (b'[{"id": "c", "status": "error", "error": "\xed\xa0\x80"}]', 1),
    "empty output": (b"", 0),
    "truncated": (b'[{"id": "c", "status": "ok"}', 0),
    "nested past the runtime limit": (b"[" * 100_000 + b"]" * 100_000, 0),
    "repeated member": (b'[{"id": "c", "status": "error", "status": "error", "error": "x"}]', 1),
    "NaN": (b'[{"id": "c", "status": "ok", "value": NaN}]', 0),
    "not an array": (json.dumps(OK).encode(), 0),
    "no row": (_rows(), 0),
    "two rows": (_rows(OK, OK), 0),
    "row not an object": (_rows("ok"), 0),
    "no status": (_rows({"id": "c"}), 0),
    "status a list": (_rows({"id": "c", "status": ["ok"]}), 0),
    # B1 and its kin: an error row not bound to the case
    "error id another case": (_rows({**ERROR, "id": "another-case"}), 1),
    "error id a list": (_rows({**ERROR, "id": []}), 1),
    "error id omitted": (_rows({k: v for k, v in ERROR.items() if k != "id"}), 1),
    "error id null": (_rows({**ERROR, "id": None}), 1),
    "error id a number": (_rows({**ERROR, "id": 7}), 1),
    "error id and case_index": (_rows({**ERROR, "case_index": 0}), 1),
    "error case_index another case": (_rows({"status": "error", "case_index": 1, "error": "x"}), 1),
    "error case_index false": (_rows({"status": "error", "case_index": False, "error": "x"}), 1),
    "error message dropped": (_rows({"id": "c", "status": "error"}), 1),
    "error message an object": (_rows({**ERROR, "error": {"message": "x"}}), 1),
    "error message null": (_rows({**ERROR, "error": None}), 1),
    "error with an extra member": (_rows({**ERROR, "admitted": True}), 1),
    "error code a number": (_rows({**ERROR, "code": 7}), 1),
    "error valid true": (_rows({**ERROR, "valid": True}), 1),
    "error generator a list": (_rows({**ERROR, "generator": []}), 1),
    # an ok row not bound to the case, and exit statuses that disagree with the rows
    "ok id another case": (_rows({**OK, "id": "another-case"}), 0),
    "ok id omitted": (_rows({"status": "ok"}), 0),
    "ok case_index another case": (_rows({**OK, "case_index": 1}), 0),
    "error row, exit 0": (_rows(ERROR), 0),
    "ok row, exit 1": (_rows(OK), 1),
    "exit 2": (_rows(ERROR), 2),
    "killed": (_rows(OK), 137),
}


@pytest.mark.parametrize("coded", [False, True])
@pytest.mark.parametrize("output", MALFORMED)
def test_no_answer_to_the_case_is_no_answer_to_the_one_shot_reader(output, coded):
    stdout, returncode = MALFORMED[output]
    with pytest.raises(lean_backend.NoAnswer):
        lean_backend.read_rows(returncode, stdout, [CASE], coded=coded)


# Error rows in the shapes Lean writes: each is Lean's rejection of the case. Only a coded route's rows name a
# code (`read_rows(coded=True)`); on any other a code is no answer (`tests/test_relay.py`).
GENUINE_ERRORS = {
    "id echoed": ERROR,
    "soft route's code": {**ERROR, "code": "InvalidInput"},
    "route's generator": {**ERROR, "error": "InvalidModel(soft): x", "generator": "soft"},
    "certificate's valid false": {**ERROR, "valid": False},
    "case its reader rejected": {"status": "error", "case_index": 0, "error": "ResourceLimit: JSON depth exceeds 256"},
}


@pytest.mark.parametrize("coded", [False, True])
@pytest.mark.parametrize("shape", GENUINE_ERRORS)
def test_an_error_row_in_leans_shape_is_a_rejection(shape, coded):
    stdout = _rows(GENUINE_ERRORS[shape])
    if "code" in GENUINE_ERRORS[shape] and not coded:
        with pytest.raises(lean_backend.NoAnswer):
            lean_backend.read_rows(1, stdout, [CASE], coded=coded)
        return
    [row] = lean_backend.read_rows(1, stdout, [CASE], coded=coded)
    assert row["status"] == "error" and row["error"] == GENUINE_ERRORS[shape]["error"]


def test_a_missing_executable_is_unavailable(tmp_path):
    with pytest.raises(CheckerUnavailable):
        relay.rows("soft-norms", [CASE], executable=tmp_path / "absent")


# -- every route mode's genuine error rows pass the client's checks (the schemas cover Lean's encoders)

ROUTE_MODES = ("soft-norms", "rights", "alternatives", "risk", "reports", "discourse", "norm-defaults",
               "readings-route")


@pytest.mark.parametrize("mode", ROUTE_MODES)
def test_every_route_mode_answers_its_genuine_errors(mode):
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service is not built")
    for case in ({"id": "c", "kind": "no-such-kind", "environment": {}, "document": "x"},
                 {"id": "c", "kind": "admission"}):
        [row] = lean_routes.rows(mode, [case])
        assert row["status"] == "error" and type(row["error"]) is str, (mode, case, row)


# -- the reviewer's repros, through `ve.readings_route.validate` on valid K1 and the service's client

@pytest.fixture(scope="module")
def k1():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service is not built")
    raw = env_k()
    document, _ = k1_document(raw)
    return raw, document


def _request(document, raw):
    return {"id": "readings-s1", "kind": "readings-validate", "environment": raw,
            "document": route.document_wire(units_of(document), document["reading_sets"])}


@pytest.fixture(scope="module")
def genuine_error(k1):
    """Lean's own error row for a K1 request it rejects (its situation's recorded value flipped), with the
    code the service sets beside it."""
    raw, document = k1
    broken = copy.deepcopy(document)
    for situation in broken["reading_sets"][0]["situations"].values():
        situation["value"] = not situation["value"]
    with LeanServicePool(size=1) as pool:
        [entry] = pool.run_bound("readings-route", route.wire([_request(broken, raw)]))
    row = entry["result"]
    assert row["status"] == "error" and row["id"] == "readings-s1", row
    return row, entry["code"]


@pytest.fixture
def answering(tmp_path, monkeypatch):
    """`validate` against a scripted service that answers each request with the row given (bound to the
    request's case by position and digest, as the service binds it), with `code` beside a rejection."""
    from tests.test_lean_service import fake
    pool = LeanServicePool(size=1, executable=fake(tmp_path, "scripted"), allow_unlisted_build=True)
    monkeypatch.setattr(relay, "_pool_for", lambda executable: pool)
    marker = tmp_path / "marker"

    def answer(row, code):
        marker.write_text(json.dumps({
            "__bound__": True, "id": "__nonce__", "status": "ok", "mode": "readings-route",
            "results": [{"index": 0, "digest": {"$digest": 0}, "result": row, **({"code": code} if code else {})}],
            "counts": {"cases": 1, "bytes": "__bytes__", "errors": int(row.get("status") == "error")}}))
    yield answer
    pool.close()


def _validate(k1):
    raw, document = k1
    return route.validate(raw, units_of(document), document["reading_sets"])


def test_the_genuine_error_replayed_is_still_a_rejection(k1, genuine_error, answering):
    row, code = genuine_error
    answering(row, code)
    with pytest.raises(VEError) as caught:
        _validate(k1)
    assert str(caught.value) == row["error"] and not isinstance(caught.value, CheckerUnavailable)


@pytest.mark.parametrize("identity", ["another-case", [], None, 7, False, "omitted", "case_index 1", "both"])
def test_a_replayed_error_not_naming_the_request_is_unavailable(k1, genuine_error, answering, identity):
    """lf-3 looprecheck1 B1: these raised `VEError`, rejecting a valid document on an answer to another case."""
    row, code = copy.deepcopy(genuine_error[0]), genuine_error[1]
    if identity == "omitted":
        del row["id"]
    elif identity == "case_index 1":
        del row["id"]
        row["case_index"] = 1
    elif identity == "both":
        row["case_index"] = 0
    else:
        row["id"] = identity
    answering(row, code)
    with pytest.raises(CheckerUnavailable):
        _validate(k1)


# -- the Rust JSON-lines transport: the same containment for its error records

def _rust(monkeypatch, tmp_path, stdout: bytes, returncode: int):
    binary = checker(tmp_path, stdout, returncode)
    monkeypatch.setenv("VE_RUST_JSONL", str(binary))
    monkeypatch.setenv("VE_RUST_SHA256", hashlib.sha256(binary.read_bytes()).hexdigest())
    return rust_jsonl.run({"id": "c", "kind": "evaluate"}, timeout=HANG_TIMEOUT)


RUST_ERROR = {"id": "c", "status": "error", "error": {"code": "InvalidInput", "message": "InvalidInput: x"}}
RUST_MALFORMED = {
    "byte 0xff": b"\xff\n",
    "nested past the runtime limit": b"[" * 100_000 + b"]" * 100_000 + b"\n",
    "UTF-16": json.dumps(RUST_ERROR).encode("utf-16") + b"\n",
    "error a string": json.dumps({**RUST_ERROR, "error": "InvalidInput: x"}).encode() + b"\n",
    "error dropped": json.dumps({"id": "c", "status": "error"}).encode() + b"\n",
    "error message a number": json.dumps({**RUST_ERROR, "error": {"code": "InvalidInput", "message": 7}}).encode() + b"\n",
    "error code dropped": json.dumps({**RUST_ERROR, "error": {"message": "x"}}).encode() + b"\n",
    "error with an extra member": json.dumps({**RUST_ERROR, "error": {**RUST_ERROR["error"], "x": 1}}).encode() + b"\n",
    "span of another shape": json.dumps({**RUST_ERROR, "error": {**RUST_ERROR["error"], "span": {"start": 0}}}).encode() + b"\n",
    "span field negative": json.dumps({**RUST_ERROR, "error": {**RUST_ERROR["error"], "span": {
        "start": -1, "end": 0, "line": 1, "column": 1}}}).encode() + b"\n",
    "span field a bool": json.dumps({**RUST_ERROR, "error": {**RUST_ERROR["error"], "span": {
        "start": True, "end": 0, "line": 1, "column": 1}}}).encode() + b"\n",
    "record with an extra member": json.dumps({**RUST_ERROR, "admitted": True}).encode() + b"\n",
    "id omitted": json.dumps({k: v for k, v in RUST_ERROR.items() if k != "id"}).encode() + b"\n",
    "id another case": json.dumps({**RUST_ERROR, "id": "another-case"}).encode() + b"\n",
}


@pytest.mark.parametrize("output", RUST_MALFORMED)
def test_a_rust_record_that_is_no_answer_is_unavailable(monkeypatch, tmp_path, output):
    with pytest.raises(CheckerUnavailable):
        _rust(monkeypatch, tmp_path, RUST_MALFORMED[output], 1)


@pytest.mark.parametrize("span", [None, {"start": 0, "end": 3, "line": 1, "column": 1}])
def test_a_rust_error_record_in_its_shape_is_a_rejection(monkeypatch, tmp_path, span):
    record = copy.deepcopy(RUST_ERROR)
    if span is not None:
        record["error"]["span"] = span
    with pytest.raises(VEError) as caught:
        _rust(monkeypatch, tmp_path, json.dumps(record).encode() + b"\n", 1)
    assert str(caught.value) == "InvalidInput: x"
