"""Memory budgets of the checker processes (2026-10-10 and 2026-10-11 OOM incidents).

Both times a `ve jsonl` countermodel search over the whole UDHR (22 sorts, domain bound 2)
built all 3^22 domain-size vectors before its first model and grew to 91 GB and then 99 GB.
`rust/ve-profile/src/search.rs` `DomainSizes` now enumerates them lazily. The binary also holds
a global memory budget (`rust/ve/src/memory.rs`, `VE_RUST_MEMORY_LIMIT`). `rust_jsonl` passes the
budget to its child and caps the child's address space, and the Lean one-shot runners and the
service run under RLIMIT_AS too. Exhausting a budget is a refusal (ResourceLimit), never an answer.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from ve.backends import lean as lean_backend
from ve.backends import process_limits, rust_jsonl
from ve.errors import CheckerUnavailable, ResourceLimit
from ve.limits import MAX_RUST_MEMORY_BYTES

ROOT = Path(__file__).resolve().parents[1]
BINARY = rust_jsonl.DEFAULT_EXECUTABLE
pytestmark = pytest.mark.skipif(not BINARY.is_file(), reason="the Rust checker has not been built")

SPEC = "ve-v0.2-expand2-2026-09-25"
MESSAGE = re.compile(r"memory budget exhausted: (\d+) bytes \(VE_RUST_MEMORY_LIMIT\)")


def _environment(sorts: int, predicates: dict) -> dict:
    return {"language": "ve.core@0.2", "profiles": ["relational-fol@0"], "spec_revision": SPEC,
            "vocabulary": {"sorts": {f"s{i}": {"description": f"sort {i}"} for i in range(sorts)},
                           "predicates": predicates, "constants": {}}}


def many_sorts_search(sorts: int = 22) -> dict:
    """The incidents' shape: many sorts, no constants, domain bound 2, so every minimum is 0."""
    env = _environment(sorts, {"p": {"arguments": ["s0"], "description": "p"}})
    return {"id": "many-sorts", "environment": env, "premises": [],
            "conclusion": ["forall", "s0", ["unary", "p", ["var", 0]]], "max_domain_size": 2}


def runaway_case(entities: int = 300) -> dict:
    """A seeded runaway under a small budget: a complete model of 90,000 tuples, within every
    size limit (16 MiB line, 100,000 tuples) and tens of MB once decoded."""
    env = _environment(1, {"r": {"arguments": ["s0", "s0"], "description": "r"}})
    items = [f"e{i}" for i in range(entities)]
    model = {"complete": True, "domains": {"s0": items}, "constants": {},
             "relations": {"r": [[a, b] for a in items for b in items]}}
    return {"id": ["runaway", 7], "kind": "evaluate-budgeted", "environment": env,
            "ast": [["forall", "s0", ["exists", "s0", ["binary", "r", ["var", 1], ["var", 0]]]]],
            "model": model, "max_evaluations": 1_000_000}


def small_case() -> dict:
    return {"id": "small", "kind": "check", "environment": _environment(1, {}), "ast": [["top"]]}


def _run_binary(cases: list[dict], *, limit: int | None, command: str = "jsonl"):
    """`ve <command>` over `cases`: its stdout, stderr and exit code."""
    env = {key: value for key, value in os.environ.items() if key != "VE_RUST_MEMORY_LIMIT"}
    if limit is not None:
        env["VE_RUST_MEMORY_LIMIT"] = str(limit)
    stdin = ("".join(json.dumps(case) + "\n" for case in cases) if command == "jsonl"
             else json.dumps(cases)).encode()
    process = subprocess.Popen([str(BINARY), command, "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env)
    try:
        stdout, stderr = process.communicate(stdin, timeout=HANG_TIMEOUT)
    finally:
        process.kill()
    return stdout.decode(), stderr.decode(), process.returncode


# `ru_maxrss` keeps the high-water mark of the memory a child started from: a child that pytest
# spawns (vfork) reports pytest's own RSS. So a small launcher starts the binary and reports its peak.
LAUNCHER = """import json, os, sys
pid = os.posix_spawn(sys.argv[1], sys.argv[1:], os.environ)
_, status, usage = os.wait4(pid, 0)
print(json.dumps({"code": os.waitstatus_to_exitcode(status), "maxrss": usage.ru_maxrss * 1024}), file=sys.stderr)
"""


def _peak(cases: list[dict], limit: int) -> tuple[list[dict], int, int]:
    """The records, exit code and peak RSS in bytes of one `ve jsonl` run over `cases`."""
    done = subprocess.run([sys.executable, "-I", "-c", LAUNCHER, str(BINARY), "jsonl", "-"],
                          input="".join(json.dumps(case) + "\n" for case in cases).encode(),
                          capture_output=True, timeout=HANG_TIMEOUT,
                          env={**os.environ, "VE_RUST_MEMORY_LIMIT": str(limit)})
    report = json.loads(done.stderr.decode().splitlines()[-1])
    return [json.loads(line) for line in done.stdout.splitlines()], report["code"], report["maxrss"]


def test_runaway_input_returns_resource_limit_within_the_budget():
    limit = 32 << 20
    records, code, peak = _peak([runaway_case(), small_case()], limit)
    # The process ends with the exhausted case: memory is not reclaimed from a case midway.
    [record] = records
    assert record["id"] == ["runaway", 7] and record["status"] == "error"
    assert record["error"]["code"] == "ResourceLimit"
    assert MESSAGE.fullmatch(record["error"]["message"]).group(1) == str(limit)
    assert code == 1  # a rejected case, as `ve jsonl` exits after any
    # The budget charges heap chunks; allow the launcher's and the binary's own pages.
    assert peak <= limit + (16 << 20), peak
    # The same input under a larger budget is answered, so the bound is the budget, not the input.
    records, code, peak = _peak([runaway_case(), small_case()], 256 << 20)
    assert [r["status"] for r in records] == ["Satisfied", "ok"] and code == 0 and peak > limit


def test_the_same_input_is_answered_under_the_default_budget():
    stdout, _, code = _run_binary([runaway_case(), small_case()], limit=None)
    records = [json.loads(line) for line in stdout.splitlines()]
    assert [r["status"] for r in records] == ["Satisfied", "ok"] and code == 0


def test_every_other_command_reports_the_budget_as_a_failed_command():
    stdout, stderr, code = _run_binary([runaway_case()], limit=32 << 20, command="conformance")
    assert stdout == "" and code == 2
    error = json.loads(stderr)
    assert error["status"] == "error" and error["error"]["code"] == "ResourceLimit"
    assert MESSAGE.fullmatch(error["error"]["message"]).group(1) == str(32 << 20)


@pytest.mark.parametrize("text", ["", "0", "8G", "-1", "1.5", " 1", "١٢٣", "99999999999999999999999"])
def test_an_invalid_budget_setting_is_refused(text):
    env = {**os.environ, "VE_RUST_MEMORY_LIMIT": text}
    done = subprocess.run([str(BINARY), "jsonl", "-"], input=json.dumps(small_case()).encode() + b"\n",
                          capture_output=True, env=env, timeout=HANG_TIMEOUT)
    assert done.returncode == 2 and done.stdout == b""
    error = json.loads(done.stderr)["error"]
    assert error["code"] == "InvalidInput" and error["message"].startswith("VE_RUST_MEMORY_LIMIT must be")


def test_the_rust_default_is_the_python_default():
    help_text = subprocess.run([str(BINARY), "--help"], capture_output=True, text=True, timeout=HANG_TIMEOUT,
                               env={k: v for k, v in os.environ.items() if k != "VE_RUST_MEMORY_LIMIT"}).stdout
    assert f"memory budget: {MAX_RUST_MEMORY_BYTES} bytes (VE_RUST_MEMORY_LIMIT; default {MAX_RUST_MEMORY_BYTES})" \
        in help_text
    configured = subprocess.run([str(BINARY), "--help"], capture_output=True, text=True, timeout=HANG_TIMEOUT,
                                env={**os.environ, "VE_RUST_MEMORY_LIMIT": "12345"}).stdout
    assert f"memory budget: 12345 bytes (VE_RUST_MEMORY_LIMIT; default {MAX_RUST_MEMORY_BYTES})" in configured


def test_many_sorts_search_needs_no_memory():
    """The incidents' input shape. The eager enumeration exhausted any budget before its first
    model. The lazy one answers at once within 64 MiB."""
    stdout, _, code = _run_binary([many_sorts_search()], limit=64 << 20)
    [record] = [json.loads(line) for line in stdout.splitlines()]
    assert record["status"] == "Found", record
    assert record["model"]["domains"]["s0"] == ["e0"] and code == 0


def _limits(pid: int) -> dict[str, str]:
    rows = Path(f"/proc/{pid}/limits").read_text().splitlines()[1:]
    return {row[:26].strip(): row[26:47].strip() for row in rows}


def _child_environment(pid: int) -> dict[str, str]:
    pairs = Path(f"/proc/{pid}/environ").read_bytes().split(b"\0")
    return dict(pair.decode().partition("=")[::2] for pair in pairs if pair)


def test_the_client_passes_the_budget_and_caps_the_address_space(monkeypatch):
    monkeypatch.setenv("VE_RUST_MEMORY_LIMIT", str(48 << 20))
    rust_jsonl._close_all()
    assert rust_jsonl.run(small_case())["status"] == "ok"
    [checker] = [c for idle in rust_jsonl._idle.values() for c in idle]
    pid = checker.process.pid
    assert _child_environment(pid)["VE_RUST_MEMORY_LIMIT"] == str(48 << 20)
    assert _limits(pid)["Max address space"] == str((48 << 20) + rust_jsonl.ADDRESS_SPACE_HEADROOM)
    # A changed budget is never served by a process started under the old one.
    monkeypatch.setenv("VE_RUST_MEMORY_LIMIT", str(64 << 20))
    assert rust_jsonl.run(small_case())["status"] == "ok"
    [checker] = [c for idle in rust_jsonl._idle.values() for c in idle]
    assert checker.process.pid != pid and checker.memory == 64 << 20
    rust_jsonl._close_all()


def test_the_client_reads_an_exhausted_budget_as_resource_limit(monkeypatch):
    monkeypatch.setenv("VE_RUST_MEMORY_LIMIT", str(32 << 20))
    rust_jsonl._close_all()
    with pytest.raises(ResourceLimit, match=MESSAGE.pattern):
        rust_jsonl.run(runaway_case())
    # The exhausted process ended; the next case gets a new one.
    assert rust_jsonl.run(small_case())["status"] == "ok"
    rust_jsonl._close_all()


@pytest.mark.parametrize("text", ["0", "8G", "-5", "1e9", "١٢"])
def test_the_client_refuses_an_invalid_budget_setting(monkeypatch, text):
    monkeypatch.setenv("VE_RUST_MEMORY_LIMIT", text)
    with pytest.raises(CheckerUnavailable, match="VE_RUST_MEMORY_LIMIT must be a positive number of bytes"):
        rust_jsonl.run(small_case())


def test_the_client_default_budget(monkeypatch):
    monkeypatch.delenv("VE_RUST_MEMORY_LIMIT", raising=False)
    assert rust_jsonl.memory_limit() == MAX_RUST_MEMORY_BYTES == 8 << 30


def test_one_shot_runners_run_under_an_address_space_limit():
    # The child reads its input first, so it reports the limit after the client has set it.
    probe = ("import resource, sys; sys.stdin.read(); "
             "print(resource.getrlimit(resource.RLIMIT_AS)[0])")
    done = process_limits.run_limited([sys.executable, "-c", probe], input=b"[]", timeout=HANG_TIMEOUT,
                                      address_space=lean_backend.ADDRESS_SPACE)
    assert done.returncode == 0 and int(done.stdout) == lean_backend.ADDRESS_SPACE == 8 << 30
    # A child that allocates past the limit fails its allocation rather than growing on.
    grow = "import sys; sys.stdin.read(); x = bytearray(1 << 30)"
    done = process_limits.run_limited([sys.executable, "-c", grow], input=b"", timeout=HANG_TIMEOUT,
                                      address_space=256 << 20)
    assert done.returncode != 0 and b"MemoryError" in done.stderr


def test_one_shot_runner_timeout_kills_the_child():
    with pytest.raises(subprocess.TimeoutExpired):
        process_limits.run_limited([sys.executable, "-c", "import time; time.sleep(600)"], input=b"",
                                   timeout=0.5, address_space=1 << 30)


def test_the_lean_service_runs_under_its_address_space_limit():
    from ve.backends.lean_service import ADDRESS_SPACE, DEFAULT_EXECUTABLE, LeanService
    if not DEFAULT_EXECUTABLE.is_file():
        pytest.skip("the Lean service has not been built")
    with LeanService(DEFAULT_EXECUTABLE) as service:
        service.start()
        assert _limits(service._proc.pid)["Max address space"] == str(ADDRESS_SPACE)


def test_configured_bytes(monkeypatch):
    monkeypatch.delenv("VE_TEST_BYTES", raising=False)
    assert process_limits.configured_bytes("VE_TEST_BYTES", 7) == 7
    monkeypatch.setenv("VE_TEST_BYTES", "4096")
    assert process_limits.configured_bytes("VE_TEST_BYTES", 7) == 4096
    for text in ("", "0", "4k", "+4", " 4", "٤"):
        monkeypatch.setenv("VE_TEST_BYTES", text)
        with pytest.raises(CheckerUnavailable):
            process_limits.configured_bytes("VE_TEST_BYTES", 7)
