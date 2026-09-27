"""Stage 1 Lean service: protocol, byte identity with the one-shot runners, faults.

The full-fixture parity, soak and latency runs are `tools/lean_service_parity.py`,
`tools/lean_service_soak.py` and `tools/lean_service_latency.py`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time

import pytest

from subprocesses import HANG_TIMEOUT
from ve.backends.lean_service import (CheckerUnavailable, LeanService, LeanServicePool, MODES,
                                      executable_sha256)
from ve.errors import ResourceLimit, VEError

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin"
CASES = json.loads((ROOT / "conformance/evaluation.json").read_text())


@pytest.fixture(scope="session")
def service_executable():
    lake = shutil.which("lake")
    if lake is None and not (BIN / "ve_service").exists():
        pytest.skip("lake is not available")
    if lake is not None and not os.environ.get("VE_LEAN_PREBUILT"):
        build = subprocess.run([lake, "build", "ve_service", "ve_conformance", "ve_norms_route"],
                               cwd=ROOT / "lean", capture_output=True, text=True, timeout=HANG_TIMEOUT)
        assert build.returncode == 0, build.stdout + build.stderr
    return BIN / "ve_service"


def raw_session(executable, lines: bytes, timeout=120):
    proc = subprocess.run([str(executable)], input=lines, capture_output=True, timeout=timeout)
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout.split(b"\n")
    assert out[-1] == b""
    return [json.loads(line) for line in out[1:-1]], out[1:-1]


def test_english_mode_is_the_generated_copy_of_the_english_runner():
    result = subprocess.run([sys.executable, "VE/Service/english_copy.py", "--check"], cwd=ROOT / "lean",
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


def test_handshake(service_executable):
    with LeanService(service_executable) as service:
        assert service.handshake["service"] == "ve-lean@1"
        assert tuple(service.handshake["modes"]) == MODES
        assert service.handshake["limits"] == {"max_line_bytes": 16777216, "max_cases": 4096,
                                               "json_depth": 256}
        assert len(service.build) == 64


def test_results_are_the_one_shot_bytes(service_executable):
    cases = CASES[:40]
    text = json.dumps(cases)
    one_shot = subprocess.run([str(BIN / "ve_conformance")], input=text.encode(),
                              capture_output=True, timeout=HANG_TIMEOUT)
    with LeanService(service_executable) as service:
        raw, response = service.exchange("evaluate", text, len(cases))
    assert response["status"] == "ok"
    start = raw.index(b'"results":') + len(b'"results":')
    assert raw[start:].startswith(one_shot.stdout.strip())
    assert raw[start + len(one_shot.stdout.strip()):] == b',"status":"ok"}'


def test_protocol_errors_answer_one_line_and_continue(service_executable):
    good = json.dumps({"id": "ok", "mode": "evaluate", "cases": CASES[:1]}).encode()
    lines = [
        b"not json",
        b'{"id":"a","mode":"evaluate"}',
        b'{"id":"b","mode":"missing","cases":[]}',
        b'{"id":"c","mode":"evaluate","cases":{}}',
        b'{"id":"d","mode":"evaluate","cases":[],"cases":[]}',
        b'{"id":"e","mode":"evaluate","cases":[],"extra":1}',
        b'{"id":"f","mode":"evaluate","cases":[{"id":1,}]}',
        b'{"id":"g","mode":"evaluate","budget":{"cases":1},"cases":[{},{}]}',
        b'{"id":"h","mode":"evaluate","budget":{"bytes":3},"cases":[{},{}]}',
        b"",
        b'{"id":"i","mode":"evaluate","cases":[' + good[:40],
        b"{" + b" " * (16 * 1024 * 1024 + 8) + b"}",
        good,
    ]
    rows, _ = raw_session(service_executable, b"\n".join(lines) + b"\n")
    ids = [row["id"] for row in rows]
    assert ids == [None, "a", "b", "c", "d", "e", "f", "g", "h", None, None, "ok"]
    assert all(row["status"] == "error" for row in rows[:-1])
    assert rows[7]["error"] == "ResourceLimit: batch has 2 cases; budget is 1"
    assert rows[8]["error"].startswith("ResourceLimit: cases are 7 bytes")
    assert rows[10]["error"].startswith("ResourceLimit: request line exceeds")
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
        assert response == {"id": response["id"], "status": "error",
                            "error": "ResourceLimit: batch has 3 cases; budget is 2"}
        assert service.run("evaluate", CASES[:5]) == service.run("evaluate", CASES[:5])
        assert service.pid == pid and service.stats["restarts"] == 0
        with pytest.raises(ResourceLimit):
            service.run("evaluate", [{"x": "y" * (17 * 1024 * 1024)}])


def test_batch_decode_rejection_is_a_ve_error(service_executable):
    with LeanService(service_executable) as service:
        with pytest.raises(VEError):
            service.run("evaluate", [{"id": None}])  # null is outside the restricted JSON
        assert service.stats["restarts"] == 0


def test_killed_process_is_replaced_between_requests(service_executable):
    with LeanService(service_executable) as service:
        first = service.pid
        os.kill(first, 9)
        time.sleep(0.2)
        assert service.run("evaluate", CASES[:2])[0]["status"] == "ok"
        assert service.pid != first


def test_kill_during_a_batch_retries_once_on_a_fresh_process(service_executable):
    with LeanService(service_executable, timeout=120, batch_cases=4096,
                     batch_bytes=16 << 20) as service:
        first = service.pid
        threading.Timer(0.5, os.kill, (first, 9)).start()
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
    with service:
        assert [r["id"] for r in service.run("evaluate", CASES[:40])] == [c["id"] for c in CASES[:40]]
        assert service.stats["requests"] == len(chunks) and service.stats["restarts"] == 0


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
import json, os, sys, time
behaviour, marker = sys.argv[1], sys.argv[2]
hello = {"service": "ve-lean@1", "modes": ["evaluate", "check-certificate", "order", "route", "norms", "english"]}
if behaviour == "handshake":
    hello["service"] = "other"
if behaviour == "silent":
    time.sleep(60)
print(json.dumps(hello), flush=True)
for line in sys.stdin:
    request = json.loads(line)
    first = not os.path.exists(marker)
    open(marker, "a").close()
    if behaviour == "hang" or (behaviour == "flaky" and first):
        time.sleep(60)
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
    n = len(request["cases"])
    print(json.dumps({"id": request["id"], "status": "ok", "results": [{"n": i} for i in range(n)]}), flush=True)
'''


def fake(tmp_path, behaviour):
    script = tmp_path / "fake.py"
    script.write_text(FAKE)
    wrapper = tmp_path / f"fake-{behaviour}"
    wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {script} {behaviour} {tmp_path / 'marker'}\n")
    wrapper.chmod(0o755)
    return wrapper


@pytest.mark.parametrize("behaviour", ["hang", "crash", "garbage", "truncated", "wrong-id", "short"])
def test_operational_faults_fail_closed(tmp_path, behaviour):
    service = LeanService(fake(tmp_path, behaviour), timeout=0.5)
    try:
        with pytest.raises(CheckerUnavailable) as caught:
            service.run("evaluate", [{}])
        assert caught.value.code == "CheckerUnavailable"
        assert not isinstance(caught.value, ResourceLimit)
        assert service.stats["starts"] == 2 and service.stats["retries"] == 1
    finally:
        service.close()


def test_one_retry_recovers_a_hung_batch(tmp_path):
    with LeanService(fake(tmp_path, "flaky"), timeout=0.5) as service:
        assert service.run("evaluate", [{}, {}]) == [{"n": 0}, {"n": 1}]
        assert service.stats["retries"] == 1 and service.stats["starts"] == 2


@pytest.mark.parametrize("behaviour", ["handshake", "silent"])
def test_bad_or_missing_handshake_is_unavailable(tmp_path, behaviour):
    service = LeanService(fake(tmp_path, behaviour), startup_timeout=0.5)
    with pytest.raises(CheckerUnavailable, match="handshake"):
        service.start()
    service.close()
