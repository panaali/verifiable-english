"""Stage 1 Lean service: protocol, byte identity with the one-shot runners, faults.

The full-fixture parity, soak and latency runs are `tools/lean_service_parity.py`,
`tools/lean_service_soak.py` and `tools/lean_service_latency.py`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import types
from types import SimpleNamespace

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from subprocesses import BUSY_PHASES, HANG_TIMEOUT, busy_cpu
from tests.lean_build import lean_build
from ve.backends.lean_service import (HANDLE_KEY, MAX_CASES, MAX_HANDLE_BYTES, MAX_HANDLES, MAX_LINE_BYTES,
                                      CheckerUnavailable, LeanService,
                                      LeanServicePool, MODES, case_digest, case_texts,
                                      executable_sha256)
from ve.backends.service_schema import DIRECTORY as SCHEMAS

from ve.errors import ResourceLimit, VEError

# The service's code list, as its handshake states it (envelope.json).
CODES = json.loads((SCHEMAS / "envelope.json").read_text())["handshake"]["properties"]["codes"]["const"]

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin"
CASES = json.loads((ROOT / "conformance/evaluation.json").read_text())


# The statement-layer route modes of lean-first batch 1 (their rows: `<mode>.json`).
ROUTE_MODES = ("soft-norms", "rights", "speech-acts", "reports", "alternatives", "risk", "quantity",
                    "norm-defaults", "discourse", "readings-route")


@pytest.fixture(scope="session")
def service_executable():
    return lean_build("ve_service", "ve_conformance", "ve_english_run") / "ve_service"


def raw_session(executable, lines: bytes, timeout=HANG_TIMEOUT):
    proc = subprocess.run([str(executable)], input=lines, capture_output=True, timeout=timeout)
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout.split(b"\n")
    assert out[-1] == b""
    return [json.loads(line) for line in out[1:-1]], out[1:-1]


def test_complete_lean_response_obeys_size_cap(tmp_path, monkeypatch):
    """F4: a complete, genuine response above the cap is unavailable."""
    from ve.backends import lean_service

    with LeanService(fake(tmp_path, "ok"), allow_unlisted_build=True, retries=0) as service:
        monkeypatch.setattr(lean_service, "MAX_RESPONSE_BYTES", 64)
        original = LeanService._write_all

        def send_and_buffer(self, data, deadline):
            original(self, data, deadline)
            with monkeypatch.context() as whole:
                whole.setattr(lean_service, "MAX_RESPONSE_BYTES", 1 << 30)
                line = LeanService._read_line(self, deadline)
            assert len(line) > lean_service.MAX_RESPONSE_BYTES
            self._buffer[:] = line + b"\n"

        monkeypatch.setattr(LeanService, "_write_all", send_and_buffer)
        with pytest.raises(CheckerUnavailable, match="size limit"):
            service.run("evaluate", [{"id": "a", "ast": [["top"]]}])


def test_english_mode_is_the_generated_copy_of_the_english_runner():
    result = subprocess.run([sys.executable, "VE/Service/english_copy.py", "--check"], cwd=ROOT / "lean",
                            capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stdout + result.stderr


def _lean_strings(path, start, end="\n\n"):
    text = (ROOT / "lean" / path).read_text()
    return re.findall(r'"([^"]+)"', text.split(start, 1)[1].split(end, 1)[0])


def test_response_schemas_follow_lean_sources():
    """Every mode has one schema file, and the schema enumerations are the Lean ones."""
    protocol = (ROOT / "lean/VE/Service/Protocol.lean").read_text()
    names = re.findall(r'^  \| \.(\w+) => "([^"]+)"$', protocol, re.M)
    dispatch = re.findall(r'^  \| \.(\w+), j => ', protocol, re.M)
    files = {p.stem for p in SCHEMAS.glob("*.json")} - {"common", "envelope"}
    assert {name for _, name in names} == set(MODES) == files
    assert {constructor for constructor, _ in names} == set(dispatch)
    common = json.loads((SCHEMAS / "common.json").read_text())["$defs"]
    admission = "VE/Route/Admission.lean"
    assert common["act"]["enum"] == _lean_strings(admission, "def acts : List String :=", "\n")
    assert common["modality"]["enum"] == _lean_strings(admission, "def modalities : List String :=", "\n")
    assert common["relation"]["enum"] == _lean_strings(admission, "def relations : List String :=", "\n")
    atomic = re.findall(r'^  \| "(\w+)" => some', (ROOT / "lean" / admission).read_text(), re.M)
    assert common["atomic_kind"]["enum"] == atomic
    assert common["generator"]["enum"] == _lean_strings("VE/Route/Background.lean",
                                                        "def generators : List String :=", "\n")
    kind = common["kind"]["anyOf"][1]["x-tagged"]
    rendered = re.findall(r'Json.arr #\[\.str "(\w+)"', (ROOT / "lean" / admission).read_text())
    assert set(kind) == set(rendered)
    envelope = json.loads((SCHEMAS / "envelope.json").read_text())
    request_error = protocol.split("def requestError", 1)[1].split("\n\n", 1)[0]
    assert set(re.findall(r'\("(\w+)",', request_error)) == set(envelope["$defs"]["error"]["required"])
    handshake = envelope["handshake"]["properties"]
    assert [c["contains"]["const"] for c in handshake["modes"]["allOf"]] == list(MODES)
    limits = {k: v["minimum"] for k, v in handshake["limits"]["properties"].items()}
    assert limits == {"max_line_bytes": MAX_LINE_BYTES, "max_cases": MAX_CASES, "json_depth": 256}
    assert re.search(r"def maxLineBytes : Nat := (\d+)", protocol)[1] == str(MAX_LINE_BYTES)
    assert re.search(r"def maxCases : Nat := (\d+)", protocol)[1] == str(MAX_CASES)
    assert re.search(r"def maxHandles : Nat := (\d+)", protocol)[1] == str(MAX_HANDLES)
    assert re.search(r"def maxHandleBytes : Nat := (\d+)", protocol)[1] == str(MAX_HANDLE_BYTES)
    assert re.search(r'def handleKey : String := "(\w+)"', protocol)[1] == HANDLE_KEY
    runner = (ROOT / "lean/VE/Service/EnglishRun.lean").read_text()
    terms = runner.split("def encodeTerm :", 1)[1].split("def encodeFormula :", 1)[0]
    formulas = runner.split("def encodeFormula :", 1)[1].split("/-- Decide", 1)[0]
    assert set(re.findall(r'\.str "([^"]+)"', terms)) == set(common["fol_term"]["x-tagged"])
    for name in ("fol_formula", "generated_formula"):
        assert set(re.findall(r'\.str "([^"]+)"', formulas)) == set(common[name]["x-tagged"])
    order = (ROOT / "lean/VE/Order/Wire.lean").read_text()
    order_terms = order.split("def decodeTerm :", 1)[1].split("def decodeFormula :", 1)[0]
    order_formulas = order.split("def decodeFormula :", 1)[1].split("def termNodes", 1)[0]
    assert set(re.findall(r'\[\.str "(\w+)"', order_terms)) == set(common["order_term"]["x-tagged"])
    assert set(re.findall(r'\[\.str "(\w+)"', order_formulas)) == set(common["order_formula"]["x-tagged"])


def _random_value(rng, depth=0):
    options = [lambda: 1, lambda: 'a\\"b,]}\\\\' * rng.randrange(3), lambda: "é,[{ü"]
    if depth < 4:
        options += [lambda: [_random_value(rng, depth + 1) for _ in range(rng.randrange(3))],
                    lambda: {f'k{i},"[': _random_value(rng, depth + 1) for i in range(rng.randrange(3))}]
    return rng.choice(options)()


def test_client_case_digests_are_the_services(service_executable):
    """`case_texts` mirrors `VE.JsonInput.caseTexts` and the service digests each case
    in one byte pass (`VE.Service.caseDigests`): on random batches with escaped quotes,
    backslashes, delimiters inside strings, non-ASCII text and JSON whitespace between
    cases, the client's digests are the service's (a mismatch would fail closed)."""
    import random
    rng = random.Random(20260928)
    with LeanService(service_executable) as service:
        for _ in range(60):
            cases = [{"id": str(k), "x": _random_value(rng)} for k in range(rng.randrange(1, 6))]
            texts = [json.dumps(c, ensure_ascii=False, separators=(",", rng.choice([":", " : "])))
                     for c in cases]
            text = rng.choice(["", " ", "\t"]) + "[" + rng.choice(["", " "]) + \
                rng.choice([",", " ,\t", "\r, "]).join(texts) + rng.choice(["", "\r"]) + "] "
            assert case_texts(text) == texts
            _, response = service.exchange("evaluate", text, len(cases))
            assert [b["digest"] for b in response["results"]] == [case_digest(t) for t in texts]
        assert service.stats["retries"] == 0


def test_handshake(service_executable):
    with LeanService(service_executable) as service:
        assert service.handshake["service"] == "ve-lean@1"
        assert tuple(service.handshake["modes"]) == MODES
        assert service.handshake["limits"] == {"max_line_bytes": 16777216, "max_cases": 4096,
                                               "json_depth": 256}
        # The handle table the client mirrors (lean-first b2): the service states it, the schema pins it.
        assert service.handshake["handles"] == {"member": HANDLE_KEY, "max": MAX_HANDLES,
                                                "max_bytes": MAX_HANDLE_BYTES}
        assert len(service.build) == 64


def results(response):
    """The runner results of a response, without their bindings."""
    return [bound["result"] for bound in response["results"]]


def test_results_are_the_one_shot_bytes(service_executable):
    """Result i is the one-shot runner's bytes for case i, bound to its position and to
    the SHA-256 of the case's text as sent."""
    cases = CASES[:40]
    text = json.dumps(cases)
    one_shot = subprocess.run([str(BIN / "ve_conformance")], input=text.encode(),
                              capture_output=True, timeout=HANG_TIMEOUT)
    with LeanService(service_executable) as service:
        raw, response = service.exchange("evaluate", text, len(cases))
    assert response["status"] == "ok"
    rows = case_texts(one_shot.stdout.decode())
    digests = [case_digest(t) for t in case_texts(text)]
    bound = ",".join(f'{{"digest":"{d}","index":{i},"result":{row}}}'
                     for i, (d, row) in enumerate(zip(digests, rows, strict=True)))
    start = raw.index(b'"results":') + len(b'"results":')
    assert raw[start:] == ("[" + bound + '],"status":"ok"}').encode()


def test_results_are_bound_to_the_case_texts_as_sent(service_executable):
    """The digest is over each case's text as the client sent it, whitespace trimmed, so
    two spellings of one case have different digests and equal results."""
    text = ' [ {"id":"a","ast":[]} ,\t{ "ast" : [], "id":"a"}\r,{"id":"a","ast":[]}]'
    with LeanService(service_executable) as service:
        _, response = service.exchange("evaluate", text, 3)
        assert service.stats["retries"] == 0
    texts = ['{"id":"a","ast":[]}', '{ "ast" : [], "id":"a"}', '{"id":"a","ast":[]}']
    assert case_texts(text) == texts
    assert [b["index"] for b in response["results"]] == [0, 1, 2]
    assert [b["digest"] for b in response["results"]] == [case_digest(t) for t in texts]
    assert results(response)[0] == results(response)[1] == results(response)[2]


def test_protocol_errors_answer_one_line_and_continue(service_executable):
    good = json.dumps({"id": "ok", "mode": "evaluate", "cases": CASES[:1]}).encode()
    lines = [
        b"not json",
        b"\xff\xfe",
        b'{"id":"a","mode":"evaluate"}',
        b'{"id":"b","mode":"missing","cases":[]}',
        b'{"id":"c","mode":"evaluate","cases":{}}',
        b'{"id":"d","mode":"evaluate","cases":[],"cases":[]}',
        b'{"id":"e","mode":"evaluate","cases":[],"extra":1}',
        b'{"id":"f","mode":"evaluate","cases":[{"id":1,}]}',
        b'{"id":"g","mode":"evaluate","budget":{"cases":1},"cases":[{},{}]}',
        b'{"id":"h","mode":"evaluate","budget":{"bytes":3},"cases":[{},{}]}',
        b'{"id":"j","mode":"evaluate","budget":{"steps":3},"cases":[{}, {"id":2}]}',
        b"",
        b'{"id":"i","mode":"evaluate","cases":[' + good[:40],
        b"{" + b" " * (16 * 1024 * 1024 + 8) + b"}",
        good,
    ]
    rows, _ = raw_session(service_executable, b"\n".join(lines) + b"\n")
    ids = [row["id"] for row in rows]
    assert ids == [None, None, "a", "b", "c", "d", "e", "f", "g", "h", "j", None, None, "ok"]
    assert all(row["status"] == "error" for row in rows[:-1])
    assert rows[8]["error"] == "ResourceLimit: batch has 2 cases; budget is 1"
    assert rows[9]["error"].startswith("ResourceLimit: cases are 7 bytes")
    assert rows[10]["error"] == "unknown budget field steps"
    assert rows[12]["error"].startswith("ResourceLimit: request line exceeds")
    # A decoded request's error is bound like a response: its mode and the digests of its
    # case texts as split (null when the cases text does not split into cases). Only a line
    # whose envelope does not decode gets the unbound error, which answers no request.
    bound = {"c": None, "f": [case_digest('{"id":1,}')], "g": [case_digest("{}")] * 2,
             "h": [case_digest("{}")] * 2, "j": [case_digest("{}"), case_digest('{"id":2}')]}
    for row in rows[:-1]:
        if row["id"] in bound:
            assert set(row) == {"id", "status", "mode", "digests", "error", "code"}
            assert row["mode"] == "evaluate" and row["digests"] == bound[row["id"]]
            assert row["code"] == ("ResourceLimit" if row["error"].startswith("ResourceLimit:") else "InvalidInput")
        else:
            assert set(row) == {"id", "status", "error"}
    assert rows[-1]["status"] == "ok" and rows[-1]["counts"] == {"cases": 1, "errors": 0,
                                                                 "bytes": len(json.dumps(CASES[:1]))}


def test_truncated_final_line_is_an_error_record(service_executable):
    rows, _ = raw_session(service_executable, b'{"id":"t","mode":"evaluate","cases":[{"id"')
    assert rows == [{"id": None, "error": "request must be a JSON object", "status": "error"}]


def test_budget_rejection_is_deterministic_and_keeps_the_process(service_executable):
    with LeanService(service_executable, batch_cases=2) as service:
        pid = service.pid
        _, response = service.exchange("evaluate", json.dumps(CASES[:3]), 3,
                                       budget={"cases": 2, "bytes": 1 << 20})
        assert response == {"id": response["id"], "status": "error", "mode": "evaluate",
                            "digests": [case_digest(t) for t in case_texts(json.dumps(CASES[:3]))],
                            "error": "ResourceLimit: batch has 3 cases; budget is 2", "code": "ResourceLimit"}
        assert service.run("evaluate", CASES[:5]) == service.run("evaluate", CASES[:5])
        assert service.pid == pid and service.stats["restarts"] == 0
        with pytest.raises(ResourceLimit):
            service.run("evaluate", [{"x": "y" * (17 * 1024 * 1024)}])


def test_batch_decode_rejection_is_a_ve_error(service_executable):
    with LeanService(service_executable) as service:
        with pytest.raises(VEError):
            service.run("evaluate", [{"id": None}])  # null is outside the restricted JSON
        assert service.stats["restarts"] == 0


@pytest.mark.parametrize("suffix", [',"ignored":null}', ',"ignored":1.5}',
                                    ',"ignored":1e2}', ',"ignored":1,"ignored":2}'])
def test_english_accepts_one_shot_json(service_executable, suffix):
    payload = {"environment": {"sorts": [], "predicates": {}, "constants": {}},
               "lexicon": {"sorts": {}, "predicates": {}, "constants": {}}, "cases": []}
    raw_case = json.dumps(payload, separators=(",", ":"))[:-1] + suffix
    proc = subprocess.run([str(BIN / "ve_english_run")], input=raw_case.encode(),
                          capture_output=True, timeout=HANG_TIMEOUT)
    assert proc.returncode == 0, proc.stderr
    with LeanService(service_executable) as service:
        _, response = service.exchange("english", "[" + raw_case + "]", 1)
    assert results(response) == [json.loads(proc.stdout)]


@pytest.mark.parametrize("number,place", [
    ("0.0", "formula"), ("0e0", "formula"), ("1e0", "formula"),
    ("0.0", "token"), ("0.0", "slot"),
])
def test_english_consumed_number_keeps_one_shot_decoding(service_executable, number, place):
    payload = {"environment": {"sorts": ["thing"], "predicates": {}, "constants": {}},
               "lexicon": {"sorts": {"thing": {"noun": ["thing"], "letter": "x"}},
                           "predicates": {}, "constants": {}},
               "cases": [{"tokens": [], "formulas": [["forall", "thing",
                                                     ["eq", ["var", 0], ["var", 0]]]]}]}
    if place == "slot":
        payload["lexicon"]["predicates"] = {"p": [0]}
    raw = json.dumps(payload, separators=(",", ":"))
    if place == "formula":
        raw = raw.replace('["var",0]', f'["var",{number}]', 1)
    elif place == "token":
        raw = raw.replace('"tokens":[]', f'"tokens":[["x",{number}]]')
    else:
        raw = raw.replace('"p":[0]', f'"p":[{number}]')
    one_shot = subprocess.run([str(BIN / "ve_english_run")], input=raw.encode(),
                              capture_output=True, timeout=HANG_TIMEOUT)
    assert one_shot.returncode in (0, 2)
    with LeanService(service_executable) as service:
        _, response = service.exchange("english", "[" + raw + "]", 1)
    expected = (json.loads(one_shot.stdout) if one_shot.returncode == 0 else
                {"status": "error", "error": one_shot.stderr.decode().strip()})
    assert results(response) == [expected]
    # Beside a rejection the service sets its code (Service.Protocol.coding); the row is the runner's.
    [entry] = response["results"]
    assert ("code" in entry) == (expected.get("status") == "error") and entry.get("code", "InvalidInput") in CODES


def test_english_ignored_large_integer_matches_one_shot(service_executable):
    payload = {"environment": {"sorts": ["thing"], "predicates": {}, "constants": {}},
               "lexicon": {"sorts": {"thing": {"noun": ["thing"], "letter": "x"}},
                           "predicates": {}, "constants": {}},
               "cases": [{"tokens": [], "formulas": [["top"]]}]}
    raw = json.dumps(payload, separators=(",", ":"))
    raw = raw[:-1] + ',"ignored":' + "9" * 4500 + "}"
    one_shot = subprocess.run([str(BIN / "ve_english_run")], input=raw.encode(),
                              capture_output=True, timeout=HANG_TIMEOUT)
    assert one_shot.returncode == 0, one_shot.stderr
    with LeanService(service_executable) as service:
        _, response = service.exchange("english", "[" + raw + "]", 1)
        assert service.stats["retries"] == 0
    assert results(response) == [json.loads(one_shot.stdout)]


@pytest.mark.parametrize("mode,case", [
    ("evaluate", CASES[0]),
    ("english", {"environment": {"sorts": [], "predicates": {}, "constants": {}},
                 "lexicon": {"sorts": {}, "predicates": {}, "constants": {}}, "cases": []}),
])
def test_whitespace_around_cases_matches_one_shot(service_executable, mode, case):
    text = " \t[" + json.dumps(case, separators=(",", ":")) + "] \r"
    with LeanService(service_executable) as service:
        _, response = service.exchange(mode, text, 1)
        assert service.stats["retries"] == 0
    assert response["counts"]["bytes"] == len(text.strip().encode())
    assert response["status"] == "ok"


def test_whitespace_empty_batch_has_trimmed_count(service_executable):
    with LeanService(service_executable) as service:
        _, response = service.exchange("evaluate", " [] ", 0)
        assert service.stats["retries"] == 0
    assert response["counts"] == {"cases": 0, "bytes": 2, "errors": 0}


def test_killed_process_is_replaced_between_requests(service_executable):
    with LeanService(service_executable) as service:
        first = service.pid
        os.kill(first, 9)
        service._proc.wait()  # reaped: the client sees it dead before the next request
        assert service.run("evaluate", CASES[:2])[0]["status"] == "ok"
        assert service.pid != first


def test_kill_during_a_batch_retries_once_on_a_fresh_process(service_executable, monkeypatch):
    with LeanService(service_executable, timeout=HANG_TIMEOUT, batch_cases=4096,
                     batch_bytes=16 << 20) as service:
        first = service.pid
        write = service._write_all
        killed = False

        def kill_before_write(line, deadline):
            nonlocal killed
            if not killed:
                os.kill(first, 9)
                killed = True
            return write(line, deadline)

        monkeypatch.setattr(service, "_write_all", kill_before_write)
        results = service.run("evaluate", CASES * 5)
        assert len(results) == 5 * len(CASES) and service.pid != first
        assert service.stats["retries"] == 1


def test_recycling_after_max_requests(service_executable):
    with LeanService(service_executable, max_requests=2) as service:
        pids = []
        for _ in range(5):
            service.run("evaluate", CASES[:1])
            pids.append(service.pid)
        assert pids[0] == pids[1] != pids[2] == pids[3] != pids[4]
        assert service.stats["recycles"] == 2 and service.stats["restarts"] == 0


def test_chunks_fit_their_byte_budget(service_executable):
    service = LeanService(service_executable, batch_bytes=3000)
    texts = [json.dumps(case, separators=(",", ":")) for case in CASES[:40]]
    chunks = list(service._chunks(texts))
    assert [t for chunk in chunks for t in chunk] == texts
    assert all(len(("[" + ",".join(chunk) + "]").encode()) <= 3000 for chunk in chunks if len(chunk) > 1)
    # Cases go with environment handles (lean-first b2): their requests are the chunks of the texts sent.
    sent = list(service._chunks(service._sent("evaluate", CASES[:40])))
    assert all(len(("[" + ",".join(item.text for item in chunk) + "]").encode()) <= 3000
               for chunk in sent if len(chunk) > 1)
    with service:
        assert [r["id"] for r in service.run("evaluate", CASES[:40])] == [c["id"] for c in CASES[:40]]
        assert service.stats["requests"] == len(sent) and service.stats["restarts"] == 0
        assert service.stats["handle_resends"] == 0


def test_build_mismatch_is_refused(service_executable):
    assert len(executable_sha256(service_executable)) == 64
    with pytest.raises(CheckerUnavailable, match="expected 0000"):
        LeanService(service_executable, expected_sha256="0" * 64).start()


def test_missing_executable_is_unavailable(tmp_path):
    with pytest.raises(CheckerUnavailable, match="missing"):
        LeanService(tmp_path / "absent").start()


def test_pool_serves_concurrent_callers(service_executable):
    with LeanServicePool(2, executable=service_executable) as pool:
        out = [None] * 6
        def call(i):
            out[i] = pool.run("evaluate", CASES[i:i + 3])
        threads = [threading.Thread(target=call, args=(i,)) for i in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert [[r["id"] for r in rows] for rows in out] == [[c["id"] for c in CASES[i:i + 3]]
                                                             for i in range(6)]


# Supervisor faults, driven by a scripted stand-in for the service.

FAKE = r'''
import hashlib, json, os, sys, time
behaviour, marker = sys.argv[1], sys.argv[2]


def bind(rows, line):
    """Result i bound to case i as the service binds it: position and SHA-256 of the case text."""
    body = line.split(',"cases":', 1)[1].rstrip()[:-1].strip()
    texts = [json.dumps(c, ensure_ascii=False, separators=(",", ":")) for c in json.loads(body)]
    return [{"index": i, "digest": hashlib.sha256(texts[i].encode()).hexdigest() if i < len(texts) else "0" * 64,
             "result": row, **({"code": "InvalidInput"} if isinstance(row, dict) and row.get("status") == "error"
                               and isinstance(row.get("error"), str) else {})} for i, row in enumerate(rows)]


def placeholders(value, line):
    """{"$digest": k} is the digest of case k."""
    if isinstance(value, dict) and set(value) == {"$digest"}:
        return bind([None] * (value["$digest"] + 1), line)[value["$digest"]]["digest"]
    if isinstance(value, dict):
        return {k: placeholders(v, line) for k, v in value.items()}
    if isinstance(value, list):
        return [placeholders(v, line) for v in value]
    return value


hello = {"service": "ve-lean@1", "protocol": 2,
         "modes": __MODES__,
         "codes": __CODES__,
         "limits": {"max_line_bytes": 16777216, "max_cases": 4096, "json_depth": 256},
         "handles": {"member": "environment_handle", "max": 64, "max_bytes": 67108864}}
if behaviour == "handshake":
    hello["service"] = "other"
if behaviour == "null-modes":
    hello["modes"] = None
if behaviour == "small-limits":
    hello["limits"]["max_cases"] = 1
if behaviour == "bad-protocol":
    hello["protocol"] = 1
if behaviour == "startup-eof":
    open(marker, "a").write("s")
    sys.exit(3)
if behaviour == "silent":
    time.sleep(60)
# A flaky service hangs on every request of its first process only. The process,
# not the request, decides: a client that gives up before the first process read
# its request still meets a hanging process first.
started = marker + "-started"
first_process = not os.path.exists(started)
open(started, "a").close()
print(json.dumps(hello), flush=True)
for line in sys.stdin:
    request = json.loads(line)
    open(marker, "a").close()
    if behaviour == "hang" or (behaviour == "flaky" and first_process):
        time.sleep(60)
    if behaviour == "spin":
        while True:
            pass
    if behaviour == "crash":
        sys.exit(3)
    if behaviour == "garbage":
        print("\x00garbage", flush=True); continue
    if behaviour == "truncated":
        sys.stdout.write('{"id":"'); sys.stdout.flush(); sys.exit(0)
    if behaviour == "wrong-id":
        request["id"] = "other"
    if behaviour == "short":
        print(json.dumps({"id": request["id"], "status": "ok", "results": []}), flush=True); continue
    if behaviour == "wrong-mode":
        print(json.dumps({"id": request["id"], "status": "ok", "mode": "order", "results": bind([True], line),
                          "counts": {"cases": 1, "bytes": len(json.dumps(request["cases"])), "errors": 0}}), flush=True); continue
    if behaviour == "missing-error":
        print(json.dumps({"id": request["id"], "status": "error"}), flush=True); continue
    if behaviour == "boolean-result":
        print(json.dumps({"id": request["id"], "status": "ok", "mode": request["mode"],
                          "results": bind([True], line), "counts": {"cases": 1, "bytes": 4, "errors": 0}}), flush=True); continue
    if behaviour == "empty-result":
        print(json.dumps({"id": request["id"], "status": "ok", "mode": request["mode"],
                          "results": bind([{"status": "ok"}], line), "counts": {"cases": 1, "bytes": 4, "errors": 0}}), flush=True); continue
    if behaviour == "duplicate-response":
        print('{"id":' + json.dumps(request["id"]) + ',"id":' + json.dumps(request["id"]) +
              ',"status":"error","error":"forged"}', flush=True); continue
    if behaviour == "nan-result":
        print('{"id":' + json.dumps(request["id"]) + ',"status":"ok","mode":"evaluate",'
              '"results":[{"status":"ok","value":NaN}],'
              '"counts":{"cases":1,"bytes":4,"errors":0}}', flush=True); continue
    if behaviour == "scripted":
        answer = json.load(open(marker))
        if answer.pop("__bound__", False):
            answer = placeholders(answer, line)
        elif isinstance(answer.get("results"), list):
            answer["results"] = bind(answer["results"], line)
        if answer.get("id") == "__nonce__":
            answer["id"] = request["id"]
        if isinstance(answer.get("counts"), dict) and answer["counts"].get("bytes") == "__bytes__":
            answer["counts"]["bytes"] = len(line.split(',"cases":', 1)[1].rstrip()[:-1].strip().encode())
        print(json.dumps(answer), flush=True); continue
    n = len(request["cases"])
    if behaviour in ("missing-valid", "string-valid", "wrong-case-id", "english-nested-bool"):
        if request["mode"] == "english":
            row = {"admissible": True, "covers": True,
                   "results": [True] if behaviour == "english-nested-bool" else []}
        else:
            row = {"id": request["cases"][0].get("id"), "status": "ok", "valid": True}
            if behaviour == "missing-valid": del row["valid"]
            if behaviour == "string-valid": row["valid"] = "false"
            if behaviour == "wrong-case-id": row["id"] = "other"
        print(json.dumps({"id": request["id"], "status": "ok", "mode": request["mode"],
                          "results": bind([row], line), "counts": {"cases": 1,
                          "bytes": len(json.dumps(request["cases"], separators=(",", ":"))),
                          "errors": 0}}), flush=True); continue
    malformed = {
        "route-string-values": {"id": "c", "status": "ok", "values": ["false"]},
        "route-extra-field": {"id": "c", "status": "ok", "values": [False], "extra": 1},
        "order-bad-surface": {"id": "c", "status": "ok", "ast": [["garbage"]]},
        "admission-no-report": {"id": "c", "status": "ok", "admitted": True},
        "norms-bad-verdict": {"id": "c", "status": "ok", "verdict": "garbage", "targets": []},
        "english-bad-formula": {"admissible": True, "covers": True,
                                "results": [{"parsed": [["garbage"]], "checked": False,
                                             "rendered": None, "roundtrip": False}]},
        "english-negative-label": {"admissible": True, "covers": True,
                                   "results": [{"parsed": None, "checked": True,
                                                "rendered": [["x", -1]], "roundtrip": False}]},
    }
    if behaviour in malformed:
        print(json.dumps({"id": request["id"], "status": "ok", "mode": request["mode"],
                          "results": bind([malformed[behaviour]], line), "counts": {"cases": 1,
                          "bytes": len(json.dumps(request["cases"], separators=(",", ":"))),
                          "errors": 0}}), flush=True); continue
    if behaviour in ("english-order-atom", "english-checked-no-render", "english-deep-formula",
                     "english-deep-parse", "background-boolean-premise"):
        if behaviour == "background-boolean-premise":
            row = {"id": request["cases"][0]["id"], "status": "ok",
                   "background": [["eq", ["var", 0], ["var", 0]]],
                   "premises": [["eq", ["var", False], ["var", 0]]],
                   "generators": ["g"]}
        else:
            parsed = [["lt", ["num", "0"], ["num", "1"]]] if behaviour == "english-order-atom" else None
            row = {"admissible": True, "covers": True,
                   "results": [{"parsed": parsed, "checked": behaviour == "english-checked-no-render",
                                "rendered": None, "roundtrip": behaviour == "english-checked-no-render"}]}
        prefix = json.dumps({"id": request["id"], "status": "ok", "mode": request["mode"]})[:-1]
        counts = json.dumps({"cases": 1, "bytes": len(json.dumps(request["cases"], separators=(",", ":"))),
                             "errors": 0})
        if behaviour in ("english-deep-formula", "english-deep-parse"):
            leaf = '["top"]' if behaviour == "english-deep-parse" else '["nope"]'
            deep = '["not",' * 5000 + leaf + ']' * 5000
            result = '{"admissible":true,"covers":true,"results":[{"parsed":[' + deep + \
                     '],"checked":false,"rendered":null,"roundtrip":false}]}'
        else:
            result = json.dumps(row, separators=(",", ":"))
        binding = json.dumps(bind([None], line)[0], separators=(",", ":"))[:-len('null}')]
        print(prefix + ',"results":[' + binding + result + '}],"counts":' + counts + '}', flush=True)
        continue
    print(json.dumps({"id": request["id"], "status": "ok", "mode": request["mode"],
                      "results": bind([{"id": case.get("id"), "status": "ok", "values": [True],
                                        "value": True, "canonical": ""} for case in request["cases"]], line),
                      "counts": {"cases": n, "bytes": len(json.dumps(request["cases"], separators=(",", ":"))), "errors": 0}}), flush=True)
'''


ALL = range(1 << 30)


@pytest.fixture
def expired(monkeypatch):
    """An injected clock for the client's waits, so that no test waits out a deadline
    against a fake that never answers: the response wait of each request attempt in
    `expired.requests` (numbered from 0 over the test's attempts) and, with
    `expired.handshakes`, every handshake wait, elapses on the injected clock as soon as
    it starts. Every other wait is the configured one (HANG_TIMEOUT in the suite).

    The client computes its deadlines itself, from the clock; what is recorded is the
    deadline that reaches each wait, less the clock reading its attempt started at:
    `expired.waits` for every request attempt (its write and its read must share one
    deadline, else the entry records both), `expired.starts` for every handshake. A
    client that miscomputes a deadline therefore records the wrong wait."""
    return expire_service_waits(monkeypatch)


def expire_service_waits(monkeypatch):
    from ve.backends import lean_service
    state = SimpleNamespace(requests=set(), handshakes=False, frozen=False, waits=[], starts=[])
    roundtrip, spawn = LeanService._roundtrip, LeanService._spawn
    write_all, read_line = LeanService._write_all, LeanService._read_line
    phase = threading.local()

    def clock():
        """The real clock, plus the time each injected expiry skipped on this thread;
        with `state.frozen` it moves only by those skips."""
        if not hasattr(phase, "skew"):
            phase.skew, phase.origin = 0.0, time.monotonic()
        now = (phase.origin if state.frozen else time.monotonic()) + phase.skew
        if getattr(phase, "start", None) is None and getattr(phase, "kind", None) is not None:
            phase.start = now  # the attempt's first reading: the one its deadline is computed from
        return now

    def within(kind, expires, call):
        saved = tuple(getattr(phase, name, None) for name in ("kind", "expires", "start", "write"))
        phase.kind, phase.expires, phase.start, phase.write = kind, expires, None, None
        try:
            return call()
        finally:
            phase.kind, phase.expires, phase.start, phase.write = saved

    def wait_of(deadline):
        return None if phase.start is None else round(deadline.wall - phase.start, 6)

    def recorded_roundtrip(self, *arguments):
        return within("request", len(state.waits) in state.requests, lambda: roundtrip(self, *arguments))

    def handshake(self):
        return within("start", state.handshakes, lambda: spawn(self))

    def write(self, data, deadline):
        phase.write = wait_of(deadline)
        return write_all(self, data, deadline)

    def read(self, deadline):
        wait = wait_of(deadline)
        if phase.kind == "start":
            state.starts.append(wait)
        else:
            state.waits.append(wait if phase.write == wait else {"write": phase.write, "read": wait})
        if phase.expires:  # the whole wait (and a second, so no rounding leaves a remainder)
            phase.skew += max(0.0, deadline.wall - clock()) + 1  # elapses on the injected clock
        return read_line(self, deadline)
    monkeypatch.setattr(lean_service, "time", SimpleNamespace(monotonic=clock))
    monkeypatch.setattr(LeanService, "_roundtrip", recorded_roundtrip)
    monkeypatch.setattr(LeanService, "_spawn", handshake)
    monkeypatch.setattr(LeanService, "_write_all", write)
    monkeypatch.setattr(LeanService, "_read_line", read)
    return state


LATER = "_Deadline(deadline.wall + 1, deadline.cpu, deadline.start, deadline.mode)"
DEADLINE_MUTANTS = {
    "request wait ignores the setting": ("_deadline", "_Deadline(now + cap, cpu, start, mode)",
                                         "_Deadline(now + 999999, cpu, start, mode)"),
    "request read past its deadline": ("_roundtrip", "raw = self._read_line(deadline)",
                                       f"raw = self._read_line({LATER})"),
    "request write past its deadline": ("_roundtrip", "self._write_all(line, deadline)",
                                        f"self._write_all(line, {LATER})"),
    "start wait ignores the setting": ("_spawn", "self._read_line(_Deadline(time.monotonic() + startup))",
                                       "self._read_line(_Deadline(time.monotonic() + 999999))"),
}


@pytest.mark.parametrize("mutant", sorted(DEADLINE_MUTANTS))
def test_the_injected_clock_records_a_miscomputed_deadline(tmp_path, monkeypatch, mutant):
    """Mutation smoke for the `expired` clock (review: injecting the expired deadline in
    place of the computed one passed a request wait of 999,999 s): each seeded deadline
    mutant of the client records a wait other than the setting."""
    import inspect
    import textwrap
    name, old, new = DEADLINE_MUTANTS[mutant]
    original = getattr(LeanService, name)
    source = textwrap.dedent(inspect.getsource(original))
    assert source.count(old) == 1
    namespace = dict(original.__globals__)
    exec(compile(source.replace(old, new), inspect.getsourcefile(original), "exec"), namespace)
    # The mutant reads the module's globals, so it sees the injected clock.
    monkeypatch.setattr(LeanService, name, types.FunctionType(
        namespace[name].__code__, original.__globals__, name, original.__defaults__))
    monkeypatch.setenv("VE_LEAN_SERVICE_TIMEOUT", "1234.5")
    monkeypatch.setenv("VE_LEAN_SERVICE_STARTUP_TIMEOUT", "1234.5")
    expired = expire_service_waits(monkeypatch)
    expired.requests = {0}
    with LeanService(fake(tmp_path, "flaky"), allow_unlisted_build=True) as service:
        service.run("evaluate", [{"id": "a", "ast": [["top"]]}])
    assert (expired.waits, expired.starts) != ([1234.5] * 2, [1234.5] * 2)


def fake(tmp_path, behaviour):
    script = tmp_path / "fake.py"
    script.write_text(FAKE.replace("__CODES__", json.dumps(CODES)).replace("__MODES__", json.dumps(list(MODES))))
    wrapper = tmp_path / f"fake-{behaviour}"
    wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {script} {behaviour} {tmp_path / 'marker'}\n")
    wrapper.chmod(0o755)
    return wrapper


@pytest.mark.parametrize("behaviour", ["hang", "crash", "garbage", "truncated", "wrong-id", "short",
                                       "wrong-mode", "missing-error", "boolean-result", "empty-result",
                                       "duplicate-response", "nan-result"])
def test_operational_faults_fail_closed(tmp_path, expired, behaviour):
    if behaviour == "hang":
        expired.requests = ALL
    service = LeanService(fake(tmp_path, behaviour), allow_unlisted_build=True)
    try:
        with pytest.raises(CheckerUnavailable) as caught:
            service.run("evaluate", [{}])
        assert caught.value.code == "CheckerUnavailable"
        assert not isinstance(caught.value, ResourceLimit)
        assert service.stats["starts"] == 2 and service.stats["retries"] == 1
        assert expired.waits == [HANG_TIMEOUT] * 2
    finally:
        service.close()


@pytest.mark.skipif(not Path("/proc/self/stat").exists(), reason="process CPU time is read from /proc")
def test_a_request_past_its_cpu_deadline_names_its_mode_and_is_not_retried(tmp_path, monkeypatch):
    """F4: a request that needs more CPU than its operation's deadline is `CheckerUnavailable` naming the
    mode, at once: the same request needs the same work, so it is not retried."""
    from ve.backends import lean_service
    monkeypatch.setitem(lean_service.DEADLINES, "evaluate", (0.3, 0.0))
    with LeanService(fake(tmp_path, "spin"), allow_unlisted_build=True) as service:
        with pytest.raises(CheckerUnavailable, match="mode evaluate used more than its deadline of 0.3 s of CPU") \
                as caught:
            service.run("evaluate", [{}])
        assert caught.value.operation == "evaluate" and not isinstance(caught.value, ResourceLimit)
        assert service.stats["starts"] == 1 and service.stats["retries"] == 0 and service.pid is None


@pytest.mark.parametrize("phase", ["write", "response"])
def test_request_transfer_checks_cpu_after_its_final_system_call(tmp_path, monkeypatch, phase):
    """F2: CPU exhaustion during the last write or the read containing the newline cannot
    escape because the transfer loop has no further select after that system call."""
    from ve.backends import lean_service
    from ve.backends.lean_service import _Deadline

    clock = SimpleNamespace(seconds=0.0, transferred=False)
    monkeypatch.setattr(lean_service, "_cpu_seconds", lambda pid: clock.seconds)
    monkeypatch.setitem(lean_service.DEADLINES, "evaluate", (0.3, 0.0))
    with LeanService(fake(tmp_path, "ok"), allow_unlisted_build=True) as service:
        native = os.write if phase == "write" else os.read
        stream = service._proc.stdin if phase == "write" else service._proc.stdout

        def transfer(fd, data):
            result = native(fd, data)
            content = bytes(data) if phase == "write" else result
            if fd == stream.fileno() and b"\n" in content and (
                    phase == "write" or b'"results"' in bytes(service._buffer) + content):
                clock.seconds, clock.transferred = 1.0, True
            return result

        monkeypatch.setattr(lean_service, "os", SimpleNamespace(**vars(os)))
        setattr(lean_service.os, "write" if phase == "write" else "read", transfer)
        with pytest.raises(CheckerUnavailable, match="mode evaluate used more than its deadline") as caught:
            if phase == "write":
                service._write_all(b"{}\n", _Deadline(time.monotonic() + HANG_TIMEOUT, 0.3, 0.0, "evaluate"))
            else:
                service.run("evaluate", [{"id": "a", "ast": [["top"]]}])
        assert clock.transferred and caught.value.operation == "evaluate"
        assert service.stats["retries"] == 0 and service.pid is None


def _without_cpu(method):
    """`method` (`_write_all` or `_read_line`) of a client that does not check the CPU deadline in that phase."""
    from ve.backends.lean_service import _Deadline
    return lambda self, *arguments: method(self, *arguments[:-1],
                                           _Deadline(arguments[-1].wall, mode=arguments[-1].mode))


@pytest.mark.skipif(not Path("/proc/self/stat").exists(), reason="process CPU time is read from /proc")
@pytest.mark.parametrize("unchecked", [None, "write", "response"], ids=["checked", "write unchecked",
                                                                        "response unchecked"])
@pytest.mark.parametrize("phase", ["write", "response"])
def test_each_phase_of_a_request_is_bounded_by_its_cpu_deadline(tmp_path, monkeypatch, phase, unchecked):
    """Review runner-portability F1: a CPU clock that moved from its first reading found a sub-tick deadline
    passed while the request was still being written, so the deadline tests passed with a client that never
    checks the CPU while waiting for the response. With the service busy in one phase only, the deadline is
    found passed in that phase, naming the mode; a client that drops the check in that phase (the mutant,
    `unchecked`) answers instead, so each phase's check is one a test needs."""
    from ve.backends import lean_service
    if unchecked:
        name = BUSY_PHASES[unchecked]
        monkeypatch.setattr(LeanService, name, _without_cpu(getattr(LeanService, name)))
    monkeypatch.setitem(lean_service.DEADLINES, "evaluate", (1e-6, 0.0))
    clock = busy_cpu(monkeypatch, lean_service, phases=(phase,))
    with LeanService(fake(tmp_path, "ok"), allow_unlisted_build=True) as service:
        if unchecked == phase:
            assert len(service.run("evaluate", [{"id": "a", "ast": [["top"]]}])) == 1
            assert clock.fired == []
            return
        with pytest.raises(CheckerUnavailable, match="mode evaluate used more than its deadline") as caught:
            service.run("evaluate", [{"id": "a", "ast": [["top"]]}])
        assert caught.value.operation == "evaluate" and not isinstance(caught.value, ResourceLimit)
        assert clock.fired == [phase] and service.stats["retries"] == 0


# The tests that set a mode's CPU deadline below one /proc tick and claim it bounds the service's work.
SUB_TICK_DEADLINE_TESTS = (
    "tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline",
    "tests/test_lean_document_wrapper.py::test_a_document_past_its_cpu_deadline_is_unavailable_never_ok",
)
# Loaded into a nested run: a machine that answers within one tick (its service's CPU always reads 0), and,
# with VE_UNCHECKED_RESPONSE, a client that does not check the CPU deadline while waiting for the response.
FAST_MACHINE = '''import os
from ve.backends import lean_service

lean_service._cpu_seconds = lambda pid: 0.0
if os.environ.get("VE_UNCHECKED_RESPONSE"):
    read = lean_service.LeanService._read_line
    lean_service.LeanService._read_line = lambda self, deadline: read(
        self, lean_service._Deadline(deadline.wall, mode=deadline.mode))
'''


@pytest.mark.skipif(not Path("/proc/self/stat").exists(), reason="process CPU time is read from /proc")
@pytest.mark.parametrize("unchecked", [False, True], ids=["checked", "response unchecked"])
def test_the_sub_tick_deadline_tests_hold_on_a_fast_machine_and_need_the_response_check(tmp_path, unchecked):
    """The ARM runner's failure and review runner-portability F1's probe: on a machine that answers within one
    tick the sub-tick deadline tests pass, and with the response wait's CPU check dropped each of them fails."""
    from tools import nested_pytest
    (tmp_path / "ve_fast_machine.py").write_text(FAST_MACHINE)
    settings = {"PYTHONPATH": os.pathsep.join(filter(None, [str(tmp_path), os.environ.get("PYTHONPATH")])),
                "VE_ENGLISH_COMPARATOR": "0", "PYTHONDONTWRITEBYTECODE": "1"}
    if unchecked:
        settings["VE_UNCHECKED_RESPONSE"] = "1"
    run = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", "-p", "ve_fast_machine",
                                                f"--basetemp={tmp_path / 'run'}", *SUB_TICK_DEADLINE_TESTS]),
                         cwd=Path(__file__).resolve().parents[1], env=nested_pytest.environment(os.environ, **settings),
                         capture_output=True, text=True, timeout=HANG_TIMEOUT)
    if not unchecked:
        assert run.returncode == 0 and "2 passed" in run.stdout, run.stdout[-4000:] + run.stderr[-4000:]
    else:
        assert run.returncode == pytest.ExitCode.TESTS_FAILED, run.stdout[-4000:] + run.stderr[-4000:]
        assert "2 failed" in run.stdout and run.stdout.count("DID NOT RAISE CheckerUnavailable") == 2, \
            run.stdout[-4000:]


def test_a_request_that_gets_no_cpu_meets_the_wall_cap(tmp_path, monkeypatch, expired):
    """A process that stops being scheduled (here, sleeping) uses no CPU; the wall-clock cap still
    ends the request, which is retried once. The cap is `WALL_FACTOR` times the CPU deadline
    (`test_users_keep_the_mode_deadlines`); in the suite it is the setting, HANG_TIMEOUT, and each
    attempt's wait is injected as expired."""
    from ve.backends import lean_service
    monkeypatch.setitem(lean_service.DEADLINES, "evaluate", (0.05, 0.0))
    expired.requests = ALL
    with LeanService(fake(tmp_path, "hang"), allow_unlisted_build=True) as service:
        with pytest.raises(CheckerUnavailable, match=r"timeout waiting for the response \(mode evaluate\)"):
            service.run("evaluate", [{}])
        assert service.stats["starts"] == 2 and service.stats["retries"] == 1
    assert expired.waits == [HANG_TIMEOUT] * 2


def test_every_mode_has_a_deadline_that_grows_with_its_input():
    from ve.backends.lean_service import DEADLINES, deadline
    assert set(DEADLINES) == set(MODES)
    for mode, (base, per_mib) in DEADLINES.items():
        assert base > 0 and per_mib > 0, mode
        assert deadline(mode, 0) == base and deadline(mode, 1 << 20) == base + per_mib, mode
        assert deadline(mode, 1 << 20, 3) == 3 * base + per_mib, mode
    # The readings route keeps the UDHR call (about 2,300 s of CPU per MiB) unavailable until F5.
    assert deadline("readings-route", 500_000) < 2300 * 500_000 / (1 << 20)


def test_the_executable_digest_is_reused_across_processes_until_the_file_changes(tmp_path, monkeypatch):
    """The client's SHA-256 of the service binary is cached beside it by the file's identity, so a new
    process does not read the binary again; a write to the binary or a sidecar for another identity is
    a miss, and the digest is the file's."""
    import hashlib
    from ve.backends import lean_service
    binary = tmp_path / "service"
    binary.write_bytes(b"first build")
    monkeypatch.setattr(lean_service, "_hashes", {})
    assert lean_service.executable_sha256(binary) == hashlib.sha256(b"first build").hexdigest()
    sidecar = tmp_path / "service.sha256-cache"
    assert json.loads(sidecar.read_text())["sha256"] == hashlib.sha256(b"first build").hexdigest()
    monkeypatch.setattr(lean_service, "_hashes", {})  # a new process
    real_open = Path.open
    monkeypatch.setattr(Path, "open", lambda path, *a, **k: (_ for _ in ()).throw(AssertionError("read"))
                        if path == binary else real_open(path, *a, **k))
    assert lean_service.executable_sha256(binary) == hashlib.sha256(b"first build").hexdigest()
    monkeypatch.setattr(Path, "open", real_open)
    binary.write_bytes(b"second build")
    monkeypatch.setattr(lean_service, "_hashes", {})
    assert lean_service.executable_sha256(binary) == hashlib.sha256(b"second build").hexdigest()
    forged = json.loads(sidecar.read_text())
    sidecar.write_text(json.dumps({"key": [*forged["key"][:-1], 0], "sha256": "0" * 64}))
    monkeypatch.setattr(lean_service, "_hashes", {})
    assert lean_service.executable_sha256(binary) == hashlib.sha256(b"second build").hexdigest()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["service", "service.sha256-cache"]


@pytest.mark.parametrize("mode", [*ROUTE_MODES, "diagnose", "risk-eval"])
def test_a_route_rejection_without_its_text_fails_closed(tmp_path, mode):
    """A statement-layer route's rejection row without a text `error` is no rejection, and the batch is
    CheckerUnavailable (common.json route_path_error and each mode's error rows)."""
    case = {"id": "c", "kind": "k", "unit": "soft-norms@0"}
    row = {"status": "error", "error": "InvalidInput: x", **({} if mode == "risk-eval" else {"id": "c"})}

    def answer(result, coded):
        # Beside a rejection the service sets its code; beside anything else, none (`Protocol.coding`), so a
        # broken row is refused by the row schema, not by the envelope's coding rule.
        return {"__bound__": True, "id": "__nonce__", "status": "ok", "mode": mode,
                "results": [{"index": 0, "digest": {"$digest": 0}, "result": result,
                             **({"code": "InvalidInput"} if coded else {})}],
                "counts": {"cases": 1, "bytes": "__bytes__", "errors": 1}}
    marker = tmp_path / "marker"
    marker.write_text(json.dumps(answer(row, True)))
    with LeanService(fake(tmp_path, "scripted"), allow_unlisted_build=True) as service:
        assert service.run(mode, [case]) == [row]
        for broken in ({k: v for k, v in row.items() if k != "error"}, {**row, "error": 7}):
            marker.write_text(json.dumps(answer(broken, False)))
            with pytest.raises(CheckerUnavailable, match="malformed response"):
                service.run(mode, [case])


def test_one_retry_recovers_a_hung_batch(tmp_path, expired):
    """The first attempt's deadline is injected (it has expired against a process that
    never answers); the retry waits HANG_TIMEOUT and its fresh process answers."""
    expired.requests = {0}
    with LeanService(fake(tmp_path, "flaky"), allow_unlisted_build=True) as service:
        assert service.run("evaluate", [{"id": "a", "ast": [["top"]]},
                                        {"id": "b", "ast": [["top"]]}]) == [
            {"id": "a", "status": "ok", "values": [True], "value": True, "canonical": ""},
            {"id": "b", "status": "ok", "values": [True], "value": True, "canonical": ""}]
        assert service.stats["retries"] == 1 and service.stats["starts"] == 2
    assert expired.waits == [HANG_TIMEOUT] * 2


@pytest.mark.parametrize("behaviour,mode,case", [
    ("missing-valid", "check-certificate", {"id": "c"}),
    ("string-valid", "check-certificate", {"id": "c"}),
    ("missing-valid", "order", {"id": "c", "kind": "certificate"}),
    ("string-valid", "order", {"id": "c", "kind": "certificate"}),
    ("wrong-case-id", "check-certificate", {"id": "c"}),
    ("wrong-case-id", "evaluate", {"id": "c"}),
    ("wrong-case-id", "route", {"id": "c", "kind": "certificate"}),
    ("wrong-case-id", "norms", {"id": "c", "kind": "norms-certificate"}),
    ("english-nested-bool", "english", {"cases": [{}]}),
    ("route-string-values", "route", {"id": "c", "kind": "evaluate"}),
    ("route-extra-field", "route", {"id": "c", "kind": "evaluate"}),
    ("order-bad-surface", "order", {"id": "c", "kind": "surface"}),
    ("admission-no-report", "route", {"id": "c", "kind": "admission"}),
    ("norms-bad-verdict", "norms", {"id": "c", "kind": "norms-conflict"}),
    ("english-bad-formula", "english", {"cases": [{}]}),
    ("english-negative-label", "english", {"cases": [{}]}),
    ("english-order-atom", "english", {"cases": [{}]}),
    ("english-deep-formula", "english", {"cases": [{}]}),
    ("background-boolean-premise", "route", {"id": "c", "kind": "background"}),
    ("background-boolean-premise", "norms", {"id": "c", "kind": "background"}),
])
def test_malformed_mode_result_retries_and_fails_closed(tmp_path, behaviour, mode, case):
    service = LeanService(fake(tmp_path, behaviour), allow_unlisted_build=True)
    with pytest.raises(CheckerUnavailable, match="malformed response"):
        service.run(mode, [case])
    assert service.stats["starts"] == 2 and service.stats["retries"] == 1
    assert service.pid is None
    service.close()


def test_client_does_not_recheck_binding_preserving_content(tmp_path):
    """Threat model (docs/spec/lean-service.md): a checked English item without a rendering
    keeps every binding, so the client accepts it; that the runner never emits one is the
    service's, tested by the Lean invariants (tests/test_lean_service_schema.py)."""
    with LeanService(fake(tmp_path, "english-checked-no-render"), allow_unlisted_build=True) as service:
        [row] = service.run("english", [{"cases": [{}]}])
        assert service.stats["retries"] == 0
    assert row["results"][0]["checked"] and row["results"][0]["rendered"] is None


_BOUND_CASES = [{"id": "a", "ast": [["top"]]}, {"id": "b", "ast": [["bottom"]]}, {"id": "a", "ast": [["top"]]}]


def _row(case, value):
    return {"id": case["id"], "status": "ok", "values": [value], "value": value, "canonical": ""}


def _bound(index, case_index, value=None):
    case = _BOUND_CASES[case_index]
    return {"index": index, "digest": {"$digest": case_index},
            "result": _row(case, case_index != 1 if value is None else value)}


@pytest.mark.parametrize("fault,results", [
    ("omitted", [_bound(0, 0), _bound(1, 1)]),
    ("reordered", [_bound(0, 1), _bound(1, 0), _bound(2, 2)]),
    ("reordered-positions", [_bound(1, 1), _bound(0, 0), _bound(2, 2)]),
    ("duplicated", [_bound(0, 0), _bound(1, 1), _bound(2, 2), _bound(2, 2)]),
    ("duplicate-in-place", [_bound(0, 0), _bound(1, 0), _bound(2, 2)]),
    ("substituted", [_bound(0, 0), {**_bound(1, 1), "digest": {"$digest": 0}}, _bound(2, 2)]),
    ("foreign-digest", [_bound(0, 0), {**_bound(1, 1), "digest": "0" * 64}, _bound(2, 2)]),
    ("wrong-index", [_bound(0, 0), {**_bound(1, 1), "index": 2}, _bound(2, 2)]),
    ("unbound", [_row(_BOUND_CASES[0], True), _row(_BOUND_CASES[1], False), _row(_BOUND_CASES[2], True)]),
    ("missing-digest", [_bound(0, 0), {k: v for k, v in _bound(1, 1).items() if k != "digest"}, _bound(2, 2)]),
    ("extra-binding-field", [_bound(0, 0), {**_bound(1, 1), "case": 1}, _bound(2, 2)]),
])
def test_results_not_bound_to_their_cases_fail_closed(tmp_path, fault, results):
    """Directive 3: an omitted, reordered, duplicated or substituted result is rejected by
    binding (position and case digest), not by semantic re-checking; after one retry the
    batch is CheckerUnavailable. Cases 0 and 2 are equal, so only positions tell them apart,
    and a result reordered with its id still breaks the binding."""
    answer = {"__bound__": True, "id": "__nonce__", "status": "ok", "mode": "evaluate", "results": results,
              "counts": {"cases": 3, "bytes": "__bytes__", "errors": 0}}
    marker = tmp_path / "marker"
    good = {**answer, "results": [_bound(0, 0), _bound(1, 1), _bound(2, 2)]}
    marker.write_text(json.dumps(good))
    with LeanService(fake(tmp_path, "scripted"), allow_unlisted_build=True) as service:
        assert service.run("evaluate", _BOUND_CASES) == [_row(_BOUND_CASES[0], True),
                                                        _row(_BOUND_CASES[1], False),
                                                        _row(_BOUND_CASES[2], True)]
        assert service.stats["retries"] == 0
        marker.write_text(json.dumps(answer))
        with pytest.raises(CheckerUnavailable, match="malformed response"):
            service.run("evaluate", _BOUND_CASES)
        assert service.stats["retries"] == 1


def _request_error(**change):
    """A request error for `_BOUND_CASES`, bound as the service binds it, with `change`."""
    answer = {"__bound__": True, "id": "__nonce__", "status": "error", "mode": "evaluate",
              "digests": [{"$digest": 0}, {"$digest": 1}, {"$digest": 2}],
              "error": "ResourceLimit: batch has 3 cases; budget is 2", "code": "ResourceLimit"}
    for key, value in change.items():
        if value is _DROP:
            del answer[key]
        else:
            answer[key] = value
    return answer


_DROP = object()


@pytest.mark.parametrize("message,raised", [("ResourceLimit: batch has 3 cases; budget is 2", ResourceLimit),
                                            ("unknown budget field steps", VEError)])
def test_bound_request_error_is_deterministic(tmp_path, message, raised):
    (tmp_path / "marker").write_text(json.dumps(_request_error(error=message)))
    with LeanService(fake(tmp_path, "scripted"), allow_unlisted_build=True) as service:
        pid = service.pid
        with pytest.raises(raised) as caught:
            service.run("evaluate", _BOUND_CASES)
        assert not isinstance(caught.value, CheckerUnavailable) and str(caught.value) == message
        assert service.stats["retries"] == 0 and service.stats["restarts"] == 0 and service.pid == pid


@pytest.mark.parametrize("fault,change", [
    ("unbound", {"mode": _DROP, "digests": _DROP}),
    ("unbound-case-error", {"mode": _DROP, "digests": _DROP, "error": "JSON: invalid batch"}),
    ("missing-mode", {"mode": _DROP}),
    ("missing-digests", {"digests": _DROP}),
    ("wrong-mode", {"mode": "order"}),
    ("null-digests", {"digests": None}),
    ("empty-digests", {"digests": []}),
    ("short-digests", {"digests": [{"$digest": 0}, {"$digest": 1}]}),
    ("extra-digest", {"digests": [{"$digest": 0}, {"$digest": 1}, {"$digest": 2}, {"$digest": 2}]}),
    ("reordered-digests", {"digests": [{"$digest": 1}, {"$digest": 0}, {"$digest": 2}]}),
    ("substituted-digest", {"digests": [{"$digest": 0}, {"$digest": 0}, {"$digest": 2}]}),
    ("foreign-digest", {"digests": [{"$digest": 0}, "0" * 64, {"$digest": 2}]}),
    ("digests-as-string", {"digests": "*"}),
    ("extra-field", {"results": []}),
])
def test_request_errors_without_their_binding_fail_closed(tmp_path, fault, change):
    """mig1d recheck: a nonce-matching error raised ResourceLimit with zero retries, so an
    error could answer a request it was not computed for. A request error must echo the
    request's mode and the digest of every case as sent; without that binding it is a
    protocol fault, retried once and then CheckerUnavailable, never ResourceLimit."""
    (tmp_path / "marker").write_text(json.dumps(_request_error(**change)))
    service = LeanService(fake(tmp_path, "scripted"), allow_unlisted_build=True)
    try:
        with pytest.raises(CheckerUnavailable, match="malformed response") as caught:
            service.run("evaluate", _BOUND_CASES)
        assert not isinstance(caught.value, ResourceLimit)
        assert service.stats["starts"] == 2 and service.stats["retries"] == 1 and service.pid is None
    finally:
        service.close()


def test_request_error_for_an_unsplit_batch_is_bound_to_null_digests(service_executable):
    """A cases text that does not split into cases has no case digests: the service binds
    its error to `null`, which is what the client expects for that request."""
    with LeanService(service_executable) as service:
        _, response = service.exchange("evaluate", "{}", 0, budget={"cases": 1})
        assert service.stats["retries"] == 0
    assert response["digests"] is None and response["mode"] == "evaluate"
    assert response["error"] == "request field cases must be an array"


def test_generated_parse_of_any_depth_is_accepted(tmp_path):
    """Generated formulas are not bounded by the decoders' 64 (an English parse nests one
    negation per prefix): a valid parse of depth 5001 is checked without recursion and
    accepted with no retry, while the same parse with a bad leaf fails closed above."""
    with LeanService(fake(tmp_path, "english-deep-parse"), allow_unlisted_build=True) as service:
        [row] = service.run("english", [{"cases": [{}]}])
        assert service.stats["retries"] == 0
    parsed = row["results"][0]["parsed"][0]
    for _ in range(5000):
        parsed = parsed[1]
    assert parsed == ["top"]


def _scripted_response_rejected(tmp_path, mode, case, row):
    answer = {"id": "__nonce__", "status": "ok", "mode": mode, "results": [row],
              "counts": {"cases": 1, "bytes": "__bytes__",
                         "errors": int(row.get("status") == "error")}}
    executable = fake(tmp_path, "scripted")
    (tmp_path / "marker").write_text(json.dumps(answer))
    with LeanService(executable, allow_unlisted_build=True) as service:
        with pytest.raises(CheckerUnavailable, match="malformed response"):
            service.run(mode, [case])
        assert service.stats["retries"] == 1 and service.stats["starts"] == 2


@pytest.mark.parametrize("mode,kind,field", [
    ("route", "background", "both"),
    ("norms", "background", "both"),
    ("norms", "norms-elaborate", "background"),
    ("norms", "norms-elaborate", "premises"),
    ("norms", "norms-elaborate", "conflict_targets"),
    ("route", "admission", "root"),
    ("route", "admission", "assumptions"),
    ("norms", "admission", "root"),
    ("norms", "admission", "assumptions"),
])
def test_fol_response_fields_reject_order_only_ast(tmp_path, mode, kind, field):
    order_atom = ["lt", ["num", "0"], ["num", "1"]]
    if kind == "background":
        row = {"id": "c", "status": "ok", "background": [["top"]],
               "premises": [["top"]], "generators": ["g"]}
        row["background"] = row["premises"] = [order_atom]
    elif kind == "norms-elaborate":
        row = {"id": "c", "status": "ok", "order": [], "background": [],
               "premises": [{"label": "p", "ast": ["top"]}],
               "conflict_targets": [{"target": "p", "sorts": [], "ast": ["top"]}],
               "fragment": True}
        if field == "background":
            row[field] = [{"generator": "g", "ast": order_atom}]
        else:
            row[field][0]["ast"] = order_atom
    else:
        row = {"id": "c", "status": "ok", "admitted": True,
               "report": {"root": {"name": "p", "ast": ["top"]}, "assumptions": []},
               "report_id": "0" * 64, "kinds": []}
        if field == "root":
            row["report"]["root"]["ast"] = order_atom
        else:
            row["report"]["assumptions"] = [{"name": "a", "ast": order_atom}]
    _scripted_response_rejected(tmp_path, mode, {"id": "c", "kind": kind}, row)


@pytest.mark.parametrize("numeral", ["00", "-0", "01", "-01", "1" * 41])
@pytest.mark.parametrize("term_tag", ["num", "scale"])
def test_order_surface_rejects_noncanonical_numerals(tmp_path, numeral, term_tag):
    term = ["num", numeral] if term_tag == "num" else ["scale", numeral, ["var", 0]]
    row = {"id": "c", "status": "ok", "ast": [["lt", term, ["num", "1"]]]}
    _scripted_response_rejected(tmp_path, "order", {"id": "c", "kind": "surface"}, row)


@pytest.mark.parametrize("mode", ["evaluate", "order", "route", "norms"])
@pytest.mark.parametrize("values", [[True], [], [True, False, True]])
def test_evaluation_response_requires_one_value_per_formula(tmp_path, mode, values):
    case = {"id": "c", "ast": [["top"], ["bottom"]]}
    if mode != "evaluate":
        case["kind"] = "evaluate"
    row = {"id": "c", "status": "ok", "values": values}
    if mode == "evaluate":
        row.update(value=all(values), canonical="")
    _scripted_response_rejected(tmp_path, mode, case, row)


@pytest.mark.parametrize("mode", ["evaluate", "check-certificate", "order", "route", "norms"])
def test_nested_boolean_id_substitution_is_operational_failure(tmp_path, mode):
    case = {"id": {"nested": [0]}}
    row = {"id": {"nested": [False]}, "status": "error", "error": "rejected"}
    if mode in ("check-certificate", "order"):
        row["valid"] = False
    _scripted_response_rejected(tmp_path, mode, case, row)


_SCHEMA_SEEDS = {
    "evaluate": ({"id": "c"}, {"id": "c", "status": "ok", "values": [True],
                              "value": True, "canonical": ""}),
    "check-certificate": ({"id": "c"}, {"id": "c", "status": "ok", "valid": True}),
    "order": ({"id": "c", "kind": "certificate"}, {"id": "c", "status": "ok", "valid": True}),
    "route": ({"id": "c", "kind": "evaluate"}, {"id": "c", "status": "ok", "values": [True]}),
    "norms": ({"id": "c", "kind": "norms-certificate"},
              {"id": "c", "status": "ok", "valid": True, "background": 0, "layers": 0}),
    "english": ({"cases": [{}]}, {"admissible": True, "covers": True,
                                 "results": [{"parsed": None, "checked": False,
                                              "rendered": None, "roundtrip": False}]}),
    "english.read": ({"id": "c"}, {"id": "c", "status": "ok", "result": {}}),
    "english.grammar": ({"id": "c"}, {"id": "c", "status": "ok", "result": {}}),
    "english.check": ({"id": "c"}, {"id": "c", "status": "ok", "result": {}}),
    "english.question": ({"id": "c"}, {"id": "c", "status": "ok", "result": {}}),
    "environment": ({"id": "c", "environment": {"profiles": ["relational-fol@0"]}},
                    {"id": "c", "status": "ok", "environment_id": "a" * 64,
                     "profiles": ["relational-fol@0"], "family": "fol"}),
    "model": ({"id": "c"}, {"id": "c", "status": "ok", "valid": True,
                           "model_id": "a" * 64}),
    "check": ({"id": "c"}, {"id": "c", "status": "ok", "well_typed": True,
                           "meaning_id": "a" * 64}),
    "identity": ({"id": "c", "kind": "source"},
                 {"id": "c", "status": "ok", "kind": "source", "identity_id": "a" * 64}),
    "parse": ({"id": "c", "source": "true.\n"},
              {"id": "c", "status": "ok", "ast": [["top"]], "canonical": "true.\n"}),
    "graph": ({"id": "c", "root": "r"},
              {"id": "c", "status": "ok", "report": {"root": "r", "assumptions": ["r"]},
               "assumptions": ["r"], "supporting_edges": [], "background": []}),
    "readings": ({"id": "c", "verdict": "ALL"}, {"id": "c", "status": "ok", "verdict": "ALL"}),
    "bundle": ({"id": "c", "lemmas": [{"meaning_id": "a" * 64}]},
               {"id": "c", "status": "ok", "checked": 1, "lemmas": ["a" * 64]}),
    "family-norms": ({"id": "c", "kind": "norms-certificate"},
                     {"id": "c", "status": "ok", "valid": True, "background": 0, "layers": 1}),
    "risk-eval": ({"conditions": []}, {"status": "ok", "results": []}),
    "diagnose": ({"id": "c", "unit": "soft-norms@0", "kind": "soft-elaborate"},
                 {"id": "c", "status": "ok", "outcome": "clean"}),
    # One closed answer per statement-layer route mode (<mode>.json), each on the mode's own path.
    "soft-norms": ({"id": "c", "kind": "soft-certificate"},
                   {"id": "c", "status": "ok", "valid": True, "background": 0, "layers": 0, "conditional_on": []}),
    "rights": ({"id": "c", "kind": "rights-certificate"},
               {"id": "c", "status": "ok", "valid": True, "background": 0, "layers": 0, "conditional_on": []}),
    "speech-acts": ({"id": "c", "kind": "speech-answer", "question": "q"},
                    {"id": "c", "status": "ok", "question": "q", "answer": "UNKNOWN (certificate not accepted)"}),
    "reports": ({"id": "c", "kind": "reports-countermodel"},
                {"id": "c", "status": "ok", "refutes": True, "source_model": []}),
    "alternatives": ({"id": "c", "kind": "alt-certificate"},
                     {"id": "c", "status": "ok", "valid": True, "background": 0, "layers": 0,
                      "conditional_on": ["alternatives:own"]}),
    "risk": ({"id": "c", "kind": "risk-certificate"}, {"id": "c", "status": "ok", "valid": True, "conditional_on": []}),
    "quantity": ({"id": "c", "kind": "day"}, {"id": "c", "status": "ok", "day": 1}),
    "norm-defaults": ({"id": "c", "kind": "norm-defaults-certificate"},
                      {"id": "c", "status": "ok", "valid": True, "premises": 0}),
    "discourse": ({"id": "c", "kind": "discourse-validity"}, {"id": "c", "status": "ok", "validity": {}}),
    "readings-route": ({"id": "c", "kind": "readings-validate"},
                       {"id": "c", "status": "ok", "content_bearing": False}),
    "document": ({"id": "c", "document": "---\n{}\n---\nA"},
                 {"id": "c", "status": "ok", "document_id": "a" * 64,
                  "source_id": "b" * 64, "source": "A",
                  "units": [{"id": "u", "span": [0, 1], "kind": "exposition",
                             "meaning": "specified", "support": "none", "status": "LABELLED"}],
                  "coverage": {"source_bytes": 1, "accounted_bytes": 1,
                               "coverage_percent": 100, "bytes_by_kind": {"exposition": 1},
                               "bytes_by_status": {"LABELLED": 1},
                               "unformalised_reasons": {}, "residual": {}, "residual_total": 0}}),
}


@settings(max_examples=48, deadline=None,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(mode=st.sampled_from(MODES), mutation=st.sampled_from(
    ("wrong-mode", "wrong-nonce", "wrong-status", "wrong-count", "missing-row-field",
     "extra-row-field", "wrong-row-type", "wrong-error-shape", "wrong-digest", "wrong-index",
     "unbound-row")))
def test_random_malformed_responses_never_escape_schema(tmp_path, mode, mutation):
    case, row = _SCHEMA_SEEDS[mode]
    answer = {"id": "__nonce__", "status": "ok", "mode": mode, "results": [row.copy()],
              "counts": {"cases": 1, "bytes": "__bytes__", "errors": 0}}
    if mutation == "wrong-mode":
        answer["mode"] = next(other for other in MODES if other != mode)
    elif mutation == "wrong-nonce":
        answer["id"] = "other"
    elif mutation == "wrong-status":
        answer["status"] = "unknown"
    elif mutation == "wrong-count":
        answer["counts"]["cases"] = 2
    elif mutation == "missing-row-field":
        answer["results"][0].pop(next(iter(row)))
    elif mutation == "extra-row-field":
        answer["results"][0]["extra"] = 1
    elif mutation == "wrong-row-type":
        field = ("status" if mode in ("english.read", "english.grammar", "english.check", "english.question") else
                 "id" if mode in ROUTE_MODES else
                 "outcome" if mode == "diagnose" else
                 "results" if mode == "risk-eval" else
                 "admissible" if mode == "english" else
                 "valid" if mode in ("check-certificate", "order", "norms", "model") else
                 "environment_id" if mode == "environment" else
                 "identity_id" if mode == "identity" else
                 "meaning_id" if mode == "check" else
                 "ast" if mode == "parse" else
                 "supporting_edges" if mode == "graph" else
                 "verdict" if mode == "readings" else
                 "lemmas" if mode == "bundle" else
                 "valid" if mode == "family-norms" else "values")
        answer["results"][0][field] = "true"
    elif mutation in ("wrong-digest", "wrong-index", "unbound-row"):
        bound = {"index": 0, "digest": {"$digest": 0}, "result": row.copy()}
        if mutation == "wrong-digest":
            bound["digest"] = "f" * 64
        elif mutation == "wrong-index":
            bound["index"] = 1
        answer = {**answer, "__bound__": True, "results": [row.copy() if mutation == "unbound-row" else bound]}
    else:
        answer = {"id": "__nonce__", "status": "error", "error": {"message": "bad"}}
    executable = fake(tmp_path, "scripted")
    (tmp_path / "marker").write_text(json.dumps(answer))
    service = LeanService(executable, allow_unlisted_build=True)
    try:
        with pytest.raises(CheckerUnavailable):
            service.run(mode, [case])
        assert service.stats["starts"] == 2 and service.stats["retries"] == 1
        assert service.pid is None
    finally:
        service.close()


@pytest.mark.parametrize("behaviour", ["handshake", "silent", "null-modes", "small-limits",
                                       "bad-protocol", "startup-eof"])
def test_bad_or_missing_handshake_is_unavailable(tmp_path, expired, behaviour):
    expired.handshakes = behaviour == "silent"
    service = LeanService(fake(tmp_path, behaviour), allow_unlisted_build=True)
    with pytest.raises(CheckerUnavailable, match="handshake"):
        service.start()
    assert service.pid is None and service.stats["starts"] == 2 and service.stats["retries"] == 1
    service.close()


def test_users_keep_the_mode_deadlines(tmp_path, monkeypatch, expired):
    """Load reproducer (W6a generator, Lean authority, a 2 h 14 min suite): the users'
    defaults are kept; without a setting a request waits its mode's wall-clock cap,
    `WALL_FACTOR` times its CPU deadline (lean-first batch 1, F4; a start 30 s), and a
    request given a timeout waits that. Each default is checked at the deadline that
    reaches the wait, on an injected clock that only moves when a test expires a wait,
    so load cannot expire one: the services start under the suite's settings, so no
    real child runs against a default (tests/conftest.py refuses one)."""
    from ve.backends import lean_service
    assert (lean_service.WALL_FACTOR, lean_service.STARTUP_TIMEOUT) == (10.0, 30.0)
    expired.frozen = True
    case = {"id": "a", "ast": [["top"]]}
    size = len(json.dumps([case], separators=(",", ":")).encode())
    with LeanService(fake(tmp_path, "ok"), allow_unlisted_build=True) as service, \
            LeanService(fake(tmp_path, "ok"), timeout=3, allow_unlisted_build=True) as fixed:
        for variable in ("VE_LEAN_SERVICE_TIMEOUT", "VE_LEAN_SERVICE_STARTUP_TIMEOUT"):
            monkeypatch.delenv(variable)
        service.run("evaluate", [case])
        service.run("evaluate", [case], timeout=7)
        fixed.run("evaluate", [case])
    cap = lean_service.WALL_FACTOR * lean_service.deadline("evaluate", size)
    assert expired.waits == [round(cap, 6), 7, 3]
    assert expired.starts == [HANG_TIMEOUT] * 2
    assert lean_service.configured_seconds("VE_LEAN_SERVICE_STARTUP_TIMEOUT", 30.0) == 30.0

    class Unstarted:
        """A service process that is never started: two ends of a pipe."""
        def __init__(self, argv, **options):
            read, write = os.pipe()
            self.stdout, self.stdin = open(read, "rb", buffering=0), open(write, "wb", buffering=0)

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0
    starts = []

    def handshake(self, deadline):
        starts.append(deadline.wall)
        raise lean_service._Failure("instrumented start")
    monkeypatch.setattr(lean_service, "subprocess", SimpleNamespace(
        Popen=Unstarted, PIPE=subprocess.PIPE, TimeoutExpired=subprocess.TimeoutExpired))
    monkeypatch.setattr(lean_service, "time", SimpleNamespace(monotonic=lambda: 0.0))
    monkeypatch.setattr(LeanService, "_read_line", handshake)
    for startup_timeout in (None, 4):
        with pytest.raises(CheckerUnavailable, match="instrumented start"):
            LeanService(fake(tmp_path, "ok"), startup_timeout=startup_timeout, address_space=None,
                        allow_unlisted_build=True).start()
    # The setting replaces the 30 s default: each handshake ends at the setting after its start.
    monkeypatch.setenv("VE_LEAN_SERVICE_STARTUP_TIMEOUT", "1234.5")
    with pytest.raises(CheckerUnavailable, match="instrumented start"):
        LeanService(fake(tmp_path, "ok"), address_space=None, allow_unlisted_build=True).start()
    assert starts == [30.0, 30.0, 4, 4, 1234.5, 1234.5]  # one retry each


def test_the_setting_replaces_the_request_and_startup_defaults(tmp_path, monkeypatch, expired):
    """A request (or a start) that outlasts the setting is stopped, retried once and
    recovered: the setting, not the 5 s (30 s) default, is each attempt's wait. The
    first request's deadline, and every handshake's of the silent service, is injected
    as expired; each deadline is recorded where it reaches the wait."""
    monkeypatch.setenv("VE_LEAN_SERVICE_TIMEOUT", "1234.5")
    expired.requests = {0}
    service = LeanService(fake(tmp_path, "flaky"), allow_unlisted_build=True)
    with service:
        assert service.run("evaluate", [{"id": "a", "ast": [["top"]]}])[0]["status"] == "ok"
        assert service.stats["retries"] == 1 and service.stats["starts"] == 2
    assert expired.waits == [1234.5, 1234.5]
    monkeypatch.setenv("VE_LEAN_SERVICE_STARTUP_TIMEOUT", "1234.5")
    expired.handshakes, expired.starts[:] = True, []
    silent = LeanService(fake(tmp_path, "silent"), allow_unlisted_build=True)
    with pytest.raises(CheckerUnavailable, match="handshake"):
        silent.start()
    assert silent.stats["starts"] == 2 and silent.stats["retries"] == 1
    assert expired.starts == [1234.5, 1234.5]
    silent.close()


@pytest.mark.parametrize("variable", ["VE_LEAN_SERVICE_TIMEOUT", "VE_LEAN_SERVICE_STARTUP_TIMEOUT"])
@pytest.mark.parametrize("value", ["", "0", "-1", "nan", "inf", "five"])
def test_a_setting_that_is_not_positive_seconds_is_refused(tmp_path, monkeypatch, variable, value):
    monkeypatch.setenv(variable, value)
    service = LeanService(fake(tmp_path, "ok"), allow_unlisted_build=True)
    with pytest.raises(CheckerUnavailable, match=variable) as caught:
        service.run("evaluate", [{"id": "a"}])
    assert not isinstance(caught.value, VEError)
    assert service.stats["starts"] == 0 and service.pid is None
    service.close()


def test_spawn_error_is_supervised_and_cleans_up(tmp_path):
    executable = tmp_path / "not-executable"
    executable.write_text("not an executable")
    service = LeanService(executable, allow_unlisted_build=True)
    with pytest.raises(CheckerUnavailable, match="startup"):
        service.start()
    assert service.pid is None and service.stats["retries"] == 1
    assert service._stderr is None


@pytest.mark.parametrize("fault", ["directory", "hash-read", "stderr-file"])
def test_pre_spawn_faults_are_supervised(tmp_path, monkeypatch, fault):
    import ve.backends.lean_service as backend

    executable = tmp_path if fault == "directory" else fake(tmp_path, "normal")
    if fault == "hash-read":
        def fail_hash(_):
            raise PermissionError("hash read denied")
        monkeypatch.setattr(backend, "executable_sha256", fail_hash)
    if fault == "stderr-file":
        def fail_file():
            raise OSError("temporary file denied")
        monkeypatch.setattr(backend.tempfile, "TemporaryFile", fail_file)
    service = LeanService(executable, allow_unlisted_build=True)
    with pytest.raises(CheckerUnavailable, match="startup"):
        service.start()
    assert service.pid is None and service._stderr is None
    assert service.stats["starts"] == 0 and service.stats["retries"] == 1
    assert service.stats["restarts"] == 2


def test_unlisted_build_is_refused_by_default(tmp_path):
    service = LeanService(fake(tmp_path, "normal"))
    with pytest.raises(CheckerUnavailable, match="unlisted build"):
        service.start()
    assert service.pid is None
    with LeanService(service.executable, allow_unlisted_build=True) as overridden:
        assert overridden.pid is not None


def test_executable_hash_cache_not_fooled_by_restored_mtime(tmp_path):
    wrapper = fake(tmp_path, "normal")
    original = executable_sha256(wrapper)
    stat = wrapper.stat()
    wrapper.write_text(wrapper.read_text().replace("normal", "bogusx"))
    os.utime(wrapper, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    assert wrapper.stat().st_size == stat.st_size
    assert executable_sha256(wrapper) != original


def test_oversized_exchange_is_resource_limit_without_start(tmp_path):
    service = LeanService(fake(tmp_path, "normal"), allow_unlisted_build=True)
    with pytest.raises(ResourceLimit, match="request line exceeds"):
        service.exchange("evaluate", '["' + 'a' * (17 << 20) + '"]', 1)
    assert service.pid is None


def test_latency_harness_closes_every_cold_start(tmp_path, monkeypatch):
    from tools import lean_service_latency as latency
    instances = []

    class Probe:
        stats = {}

        def __init__(self, **kwargs):
            self.started = self.closed = False
            instances.append(self)

        def start(self):
            self.started = True

        def close(self):
            self.closed = True

    monkeypatch.setattr(latency, "LeanService", Probe)
    monkeypatch.setattr(latency, "workloads", lambda *args: [])
    monkeypatch.setattr(latency, "machine", lambda: {"commit": "test", "cpu": "test",
                                                      "logical_cpus": 1, "loadavg": [0], "python": "test"})
    latency.main(["--out", str(tmp_path), "--cold-starts", "3"])
    assert len(instances) == 4
    assert all(x.started and x.closed for x in instances)


def test_pool_answers_a_batch_in_parallel_with_the_same_results(service_executable):
    cases = CASES[:40]
    with LeanService(service_executable, batch_cases=8) as single:
        expected = single.run("evaluate", cases)
    with LeanServicePool(2, executable=service_executable, batch_cases=8) as pool:
        assert pool.run("evaluate", cases) == expected
        assert all(s.stats["requests"] >= 1 for s in pool.services)
        assert sum(s.stats["requests"] for s in pool.services) == 5
        assert pool.run("evaluate", cases[:3]) == expected[:3]  # split to one request per process
        assert pool.run("evaluate", []) == []


def test_pool_raises_the_earliest_failing_request(service_executable):
    cases = CASES[:4] + [{"id": None}] + CASES[:3] + [{"id": 1.5}]
    with LeanServicePool(2, executable=service_executable, batch_cases=4) as pool:
        with pytest.raises(VEError) as caught:
            pool.run("evaluate", cases)
        assert "null" in str(caught.value) or "JSON" in str(caught.value)
        assert all(s.stats["restarts"] == 0 for s in pool.services)
    with LeanService(service_executable, batch_cases=4) as single:
        with pytest.raises(VEError) as expected:
            single.run("evaluate", cases)
    assert str(caught.value) == str(expected.value)


@pytest.mark.parametrize("result, coding", [
    ({"id": "c", "status": "error", "error": "rejected"}, {}),
    ({"id": "c", "status": "error", "error": "rejected"}, {"code": "Nonsense"}),
    ({"id": "c", "status": "error", "error": "rejected"}, {"code": 7}),
    ({"id": "c", "status": "error", "error": "rejected"}, {"code": "InvalidInput", "generator": 1}),
    ({"id": "c", "status": "error", "error": "rejected"}, {"code": "InvalidInput", "other": "x"}),
    ({"id": "c", "status": "ok", "kind": "source", "identity_id": "0" * 64}, {"code": "InvalidInput"}),
    ({"id": "c", "status": "ok", "kind": "source", "identity_id": "0" * 64}, {"generator": "literals"}),
])
def test_a_rejection_needs_its_public_code_and_nothing_else_carries_one(tmp_path, result, coding):
    """Lean-first batch 0: beside a rejection the service sets one of the handshake's codes
    (`Service.Protocol.coding`); a missing or unknown code, or a code beside a success, is an
    operational failure, never a verdict."""
    answer = {"__bound__": True, "id": "__nonce__", "status": "ok", "mode": "identity",
              "results": [{"index": 0, "digest": {"$digest": 0}, "result": result, **coding}],
              "counts": {"cases": 1, "bytes": "__bytes__", "errors": int(result["status"] == "error")}}
    executable = fake(tmp_path, "scripted")
    (tmp_path / "marker").write_text(json.dumps(answer))
    with LeanService(executable, allow_unlisted_build=True) as service:
        with pytest.raises(CheckerUnavailable, match="malformed response"):
            service.run("identity", [{"id": "c", "kind": "source", "source": "x"}])


def test_a_rejection_with_its_code_is_accepted(tmp_path):
    """The control of the test above: the same scripted entry with a public code is a row."""
    result = {"id": "c", "status": "error", "error": "rejected"}
    answer = {"__bound__": True, "id": "__nonce__", "status": "ok", "mode": "identity",
              "results": [{"index": 0, "digest": {"$digest": 0}, "result": result, "code": "InvalidInput"}],
              "counts": {"cases": 1, "bytes": "__bytes__", "errors": 1}}
    executable = fake(tmp_path, "scripted")
    (tmp_path / "marker").write_text(json.dumps(answer))
    with LeanService(executable, allow_unlisted_build=True) as service:
        assert service.run("identity", [{"id": "c", "kind": "source", "source": "x"}]) == [result]
