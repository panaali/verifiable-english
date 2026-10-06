"""Environment handles (docs/LEAN-FIRST-PLAN.md F2, lean-first batch 2) and the persistent Rust
checker (F6).

The F2 obligation: for every request of the corpus, the answer with a handle equals the answer with the
environment re-sent, and a handle miss is a bound request error after which the client resends, never a
different answer. The service keeps the handle table (`VE.Service.Handles`); the client mirrors it
(`LeanService._note`).
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import signal
import time

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import lean_build
from ve.backends import rust_jsonl
from ve.backends.lean_service import HANDLE_KEY, MAX_HANDLES, LeanService, LeanServicePool, case_digest
from ve.backends.service_schema import same_json
from ve.errors import CheckerUnavailable

ROOT = Path(__file__).resolve().parents[1]
EVALUATION = json.loads((ROOT / "conformance/evaluation.json").read_text())
POLICY = json.loads((ROOT / "usecases/agent-policy/environment.lean.json").read_text())


def _route_corpus() -> dict[str, list]:
    """The recorded corpus of every route answer kind (`tests/data/route-cases.jsonl`), by mode."""
    corpus: dict[str, list] = {}
    for line in (ROOT / "tests/data/route-cases.jsonl").read_text().splitlines():
        mode, case = json.loads(line)
        corpus.setdefault(mode, []).append(json.loads(case) if isinstance(case, str) else case)
    return corpus


@pytest.fixture(scope="module")
def executable():
    return lean_build("ve_service") / "ve_service"


def _answers(entries: list) -> list:
    """The bound entries without their binding: the digest binds the text sent, which a handle changes,
    and the index the position in its request, which the split into requests decides."""
    return [{key: value for key, value in entry.items() if key not in ("digest", "index")} for entry in entries]


def _with_and_without(executable, mode: str, cases: list) -> tuple[list, list, dict]:
    with LeanService(executable, handles=True) as handled, LeanService(executable, handles=False) as inline:
        return (_answers(handled.run_bound(mode, cases)), _answers(inline.run_bound(mode, cases)),
                dict(handled.stats))


def test_handles_answer_the_evaluation_corpus_as_resending_does(executable):
    with_handles, resent, stats = _with_and_without(executable, "evaluate", EVALUATION)
    assert len(with_handles) == len(EVALUATION) and same_json(with_handles, resent)
    # Every request named its environments by handle and none had to be resent.
    distinct = {case_digest(json.dumps(case["environment"], ensure_ascii=False, separators=(",", ":")))
                for case in EVALUATION}
    assert stats["handle_resends"] == 0 and 0 < stats["registered"] <= len(distinct)


@pytest.mark.parametrize("mode", sorted(_route_corpus()))
def test_handles_answer_the_route_corpus_as_resending_does(executable, mode):
    cases = _route_corpus()[mode]
    with_handles, resent, stats = _with_and_without(executable, mode, cases)
    assert same_json(with_handles, resent)
    assert stats["handle_resends"] == 0
    named = any(isinstance(case, dict) and isinstance(case.get("environment"), dict) for case in cases)
    # risk-eval reads its cases with Lean.Json.parse, so its environments are never handles.
    assert (stats["registered"] > 0) == (named and mode != "risk-eval")


def test_typing_with_a_real_environment_sends_it_once(executable):
    cases = [{"id": f"t{n}", "environment": POLICY, "ast": [["top"]]} for n in range(5)]
    with LeanService(executable) as service:
        sent = []
        original = service._write_all
        service._write_all = lambda data, deadline: (sent.append(data), original(data, deadline))[1]
        rows = [service.run("check", [case])[0] for case in cases]
    assert all(row["status"] == "ok" for row in rows)
    environment = json.dumps(POLICY, ensure_ascii=False, separators=(",", ":")).encode()
    assert [environment in line for line in sent] == [True, False, False, False, False]
    assert all(len(line) < 300 for line in sent[1:])


def test_a_missed_handle_is_resent_with_its_environment(executable):
    """The client believes the process holds a handle it does not: the request is a bound
    `CheckerUnavailable` request error, and the cases are sent again with their environment."""
    case = {"id": "t", "environment": POLICY, "ast": [["top"]]}
    with LeanService(executable, handles=False) as inline:
        expected = _answers(inline.run_bound("check", [case]))
    with LeanService(executable) as service:
        service.start()
        digest = case_digest(json.dumps(POLICY, ensure_ascii=False, separators=(",", ":")))
        service._registered[digest] = 1
        assert same_json(_answers(service.run_bound("check", [case])), expected)
        assert service.stats["handle_resends"] == 1 and not service._registered
        # The next request registers the environment again and is answered with its handle.
        assert same_json(_answers(service.run_bound("check", [case])), expected)
        assert service.stats["handle_resends"] == 1 and digest in service._registered


def test_the_miss_itself_is_a_bound_request_error(executable):
    digest = "a" * 64
    cases = '[{"id":"t","%s":"%s","ast":[["top"]]}]' % (HANDLE_KEY, digest)
    with LeanService(executable) as service:
        _, response = service.exchange("check", cases, 1)
    assert response["status"] == "error" and response["code"] == "CheckerUnavailable"
    assert response["error"] == f"CheckerUnavailable: environment handle {digest} is not registered"
    assert response["digests"] == [case_digest(cases[1:-1])]


def test_a_registration_whose_key_is_not_its_digest_is_refused(executable):
    """Handles are content-addressed: a key that is not the SHA-256 of its environment's text is a
    request error, and the case naming it is never answered with that environment."""
    text = json.dumps(POLICY, ensure_ascii=False, separators=(",", ":"))
    forged = case_digest("another environment")
    cases = '[{"id":"t","%s":"%s","ast":[["top"]]}]' % (HANDLE_KEY, forged)
    with LeanService(executable) as service:
        _, response = service.exchange("check", cases, 1, environments={forged: text})
        assert response["status"] == "error" and response["code"] == "InvalidInput"
        assert response["error"] == f"InvalidInput: environment handle {forged} is not the SHA-256 of its text"
        assert not service._registered
        # Nothing was registered under it either.
        _, response = service.exchange("check", cases, 1)
        assert response["code"] == "CheckerUnavailable"


def test_the_client_mirrors_the_services_eviction(executable):
    """Registering more than `MAX_HANDLES` environments empties both tables first; no request is resent."""
    environments = [{**POLICY, "spec_revision": f"r{n}"} for n in range(MAX_HANDLES + 3)]
    with LeanService(executable, handles=True) as service, LeanService(executable, handles=False) as inline:
        for environment in environments + environments[:2]:
            case = {"id": "e", "environment": environment}
            assert same_json(_answers(service.run_bound("environment", [case])),
                             _answers(inline.run_bound("environment", [case])))
        assert service.stats["handle_resends"] == 0
        assert len(service._registered) == 5 and service.stats["registered"] == MAX_HANDLES + 5
        # Every environment the client believes the process holds is answered by its handle alone.
        held = set(service._registered)
        for environment in environments:
            if case_digest(json.dumps(environment, ensure_ascii=False, separators=(",", ":"))) in held:
                service.run_bound("environment", [{"id": "e", "environment": environment}])
        assert service.stats["handle_resends"] == 0 and service.stats["registered"] == MAX_HANDLES + 5


def test_a_case_that_names_its_own_handle_is_sent_as_it_is(executable):
    """A caller's own `environment_handle` member is not the client's: the case goes as written."""
    case = {"id": "t", HANDLE_KEY: "b" * 64, "ast": [["top"]]}
    with LeanService(executable) as service:
        sent = service._sent("check", [case])
    assert sent[0].digest is None and json.loads(sent[0].text) == case


def test_the_pool_answers_with_handles_as_resending_does(executable):
    cases = EVALUATION[:300]
    with LeanServicePool(2, executable=executable) as pool, LeanService(executable, handles=False) as inline:
        assert same_json(_answers(pool.run_bound("evaluate", cases)), _answers(inline.run_bound("evaluate", cases)))
        assert sum(service.stats["registered"] for service in pool.services) > 0


# -- F6: the persistent Rust checker

def _rust_case():
    from ve.environment import Environment
    return {"id": "typing", "kind": "check", "environment": rust_jsonl.rust_environment(Environment(POLICY)),
            "ast": [["top"]]}


def test_adapter_environment_is_encoded_once_and_immutable():
    from ve.backends.lean_runner import cached_route_environment, route_environment
    from ve.environment import Environment
    env = Environment(POLICY)
    lean = cached_route_environment(env)
    rust = rust_jsonl.cached_rust_environment(env)
    assert cached_route_environment(env) is lean
    assert rust_jsonl.cached_rust_environment(env) is rust
    assert json.loads(lean.text) == route_environment(env)
    assert json.loads(rust.text) == rust_jsonl.rust_environment(env)
    with pytest.raises(TypeError):
        lean["vocabulary"]["sorts"].clear()
    with pytest.raises(TypeError):
        rust["profiles"].append("bogus@0")


def _checkers():
    return [checker for idle in rust_jsonl._idle.values() for checker in idle]


@pytest.fixture
def rust():
    rust_jsonl._close_all()
    yield
    rust_jsonl._close_all()


def test_one_rust_process_answers_every_call(rust):
    case = _rust_case()
    answers = [rust_jsonl.run(case, timeout=HANG_TIMEOUT) for _ in range(20)]
    assert answers == [{"id": "typing", "status": "ok", "well_typed": True}] * 20
    assert len(_checkers()) == 1


def test_a_rust_process_that_ended_is_replaced(rust):
    case = _rust_case()
    rust_jsonl.run(case, timeout=HANG_TIMEOUT)
    [checker] = _checkers()
    os.kill(checker.process.pid, signal.SIGKILL)
    checker.process.wait()
    assert rust_jsonl.run(case, timeout=HANG_TIMEOUT)["well_typed"] is True
    [replacement] = _checkers()
    assert replacement is not checker and replacement.process.poll() is None


def test_a_rust_process_that_times_out_is_killed_and_not_reused(rust, monkeypatch):
    case = _rust_case()
    rust_jsonl.run(case, timeout=HANG_TIMEOUT)
    [checker] = _checkers()
    monkeypatch.setattr(rust_jsonl, "_deadline", lambda timeout: time.monotonic() - 1)
    with pytest.raises(CheckerUnavailable, match="timed out"):
        rust_jsonl.run(case, timeout=HANG_TIMEOUT)
    assert checker.process.poll() is not None and not _checkers()


def test_a_replaced_rust_executable_gets_a_new_process(rust, tmp_path):
    """A process is reused only while its executable has the file identity it started from."""
    binary = tmp_path / "ve"
    binary.write_bytes(rust_jsonl.DEFAULT_EXECUTABLE.read_bytes())
    binary.chmod(0o755)
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    case = _rust_case()
    rust_jsonl.run(case, executable=binary, timeout=HANG_TIMEOUT, expected_sha256=digest)
    [first] = _checkers()
    os.utime(binary, ns=(time.time_ns(), time.time_ns() + 10**9))
    rust_jsonl.run(case, executable=binary, timeout=HANG_TIMEOUT, expected_sha256=digest)
    [second] = _checkers()
    assert second is not first and first.process.poll() is not None


def test_a_rust_process_that_writes_two_records_is_no_answer(rust, tmp_path):
    binary, records = tmp_path / "ve", tmp_path / "records"
    record = json.dumps({"id": "typing", "status": "ok", "well_typed": True})
    records.write_text(f"{record}\n{record}\n")  # one write: both records arrive together
    binary.write_text(f"#!/bin/sh\nhead -n 1 >/dev/null\ncat '{records}'\nsleep 600\n")
    binary.chmod(0o755)
    with pytest.raises(CheckerUnavailable):
        rust_jsonl.run(_rust_case(), executable=binary, timeout=HANG_TIMEOUT,
                       expected_sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
    assert not _checkers()


def test_rust_retry_keeps_the_original_deadline(monkeypatch):
    from types import SimpleNamespace
    rust_jsonl._close_all()
    clock = [0.0]
    waits = []

    class FakeChecker:
        instances = 0

        def __init__(self, argv):
            self.index = FakeChecker.instances
            FakeChecker.instances += 1
            self.closed = False

        def usable(self):
            return True

        def exchange(self, data, timeout):
            waits.append(timeout)
            if self.index == 0:
                clock[0] = 0.8
                raise OSError("reused process ended")
            return b'{"id":"x","status":"ok","well_typed":true}'

        def close(self):
            self.closed = True

    monkeypatch.setattr(rust_jsonl, "time", SimpleNamespace(monotonic=lambda: clock[0]))
    monkeypatch.setattr(rust_jsonl, "_Checker", FakeChecker)
    argv = ["fake", "jsonl", "-"]
    rust_jsonl._idle[tuple(argv)] = [FakeChecker(argv)]
    completed = rust_jsonl._run_checker(argv, input=b"{}\n", timeout=1.0)
    rust_jsonl._release(completed, valid=False)
    assert waits[0] == 1.0
    assert 0.19 < waits[1] < 0.21
    assert completed._checker.closed


# -- F3: the same Background request is asked once

def test_lean_background_is_asked_once_per_request(monkeypatch):
    from ve import background as background_module
    from ve.backends import relay
    from ve.environment import Environment
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    monkeypatch.delenv("VE_AUTHORITY_OVERRIDES", raising=False)
    monkeypatch.setattr(relay, "_answers", __import__("weakref").WeakKeyDictionary())
    described = json.loads(json.dumps(POLICY))
    sort = next(iter(described["vocabulary"]["sorts"].values()))
    sort["description"] = "another description"
    env, same, other = Environment(POLICY), Environment(POLICY), Environment(described)
    asked, decide = [], relay.decide
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **kw: (asked.append(mode), decide(mode, cases, **kw))[1])
    first = background_module.background(env)
    assert background_module.background(env) == first and background_module.background(same) == first
    assert asked == ["norms"] and first
    assert background_module.background(other) == first and asked == ["norms", "norms"]
    # Another pool (another build) is asked again.
    monkeypatch.setattr(relay, "_pool", None)
    assert background_module.background(env) == first and asked == ["norms", "norms", "norms"]
