"""The Lean answer store (tests/answer_store.py): R1 only, exact batches, every client check on a hit.

Every test here installs its own store under `tmp_path` and asks the real service; none relies on a store a
run was given, so all are `live_service`.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

import answer_store
from answer_store import (ENV, GATE_FLAG, INVENTORY, LIVE_MARK, SEAM_GLOBALS, Seam, Store, changed_guarded_paths,
                          decode, key, limits, replay, settings)
from subprocesses import HANG_TIMEOUT
from tests import lean_routes
from tests.lean_build import lean_build
from tools import answer_replay, gate, nested_pytest
from ve.backends import lean_service
from ve.backends.lean_service import CheckerUnavailable, LeanService

pytestmark = pytest.mark.live_service

ROOT = Path(__file__).resolve().parents[1]
EVALUATION = json.loads((ROOT / "conformance/evaluation.json").read_text())
CASES = EVALUATION[:3]


@pytest.fixture(scope="module")
def executable():
    return lean_build("ve_service") / "ve_service"


@pytest.fixture
def seam(tmp_path, monkeypatch, executable):
    """A store under tmp_path in the client's seam, no hit sampled, outside any gate."""
    monkeypatch.delenv(GATE_FLAG, raising=False)
    monkeypatch.delenv("VE_LEAN_SERVICE", raising=False)
    installed = Seam(Store(tmp_path / "store"), sample=0.0)
    monkeypatch.setattr(lean_service, "answer_store", installed)
    return installed


def entries(seam, build):
    return list(seam.store.entries(build))


def plant(seam, build, entry, recorded, line, response):
    """Replace an entry on disk, as a store another run left would hold it (this process forgets its copy)."""
    seam.store.put(build, entry, recorded, line, response)
    seam.memory.clear()
    seam.memory_bytes = 0


def test_a_stored_answer_is_served_after_the_process_starts(seam, tmp_path, monkeypatch):
    with LeanService() as service:
        live = service.run_bound("evaluate", CASES)
    assert seam.counts["recorded"] == 1 and seam.counts["hits"] == 0
    service = LeanService()  # not started: the request itself starts it
    try:
        served = service.run_bound("evaluate", CASES)
        # The store answered after _ensure: the process was started, pinned and handshaken.
        assert service.pid is not None and service.handshake is not None and service.stats["starts"] == 1
    finally:
        service.close()
    assert served == live and seam.counts["hits"] == 1 and seam.alarms == []
    # A build the pins do not list is refused before the store is asked, though it holds the answer.
    lock = tmp_path / "checkers.lock"
    lock.write_text(json.dumps({"ve_service": ["0" * 64]}))
    monkeypatch.setattr(lean_service, "BUILD_LOCK", lock)
    with pytest.raises(CheckerUnavailable, match="unlisted build"):
        LeanService().run_bound("evaluate", CASES)
    assert seam.counts["hits"] == 1


def test_a_store_mode_line_stands_alone(seam):
    """The same cases give the same line whatever handles the process holds: every environment is registered in
    the line, and the nonce is derived from the rest of it."""
    lines = []
    asked = seam.answer
    seam.answer = lambda service, line: lines.append(line) or asked(service, line)
    with LeanService() as service:
        service.run_bound("evaluate", CASES)
        service.run_bound("evaluate", CASES)  # the process now holds the handles
    with LeanService() as service:
        service.run_bound("evaluate", CASES)
    assert len(lines) == 3 and len(set(lines)) == 1
    request = json.loads(lines[0])
    named = {case[lean_service.HANDLE_KEY] for case in request["cases"]}
    assert named and named == set(request["environments"]) and request["id"].startswith("store-")
    # Live, the second request of one process names its handles without registering them again.
    live = []
    write = LeanService._write_all
    seam.reason = lambda service, timeout: "off"
    with LeanService() as service:
        service._write_all = lambda data, deadline: live.append(data) or write(service, data, deadline)
        service.run_bound("evaluate", CASES)
        service.run_bound("evaluate", CASES)
    assert b'"environments"' in live[0] and b'"environments"' not in live[1] and live[0] != live[1]


def test_a_planted_positional_mismatch_is_refused_not_served(seam):
    with LeanService() as service:
        genuine = service.run_bound("evaluate", CASES)
        build = service.build
    [(entry, path)] = entries(seam, build)
    recorded, line, response = decode(path.read_bytes())
    swapped = response.replace(b'"index":0,', b'"index":9,').replace(b'"index":1,', b'"index":0,').replace(
        b'"index":9,', b'"index":1,')
    assert swapped != response
    plant(seam, build, entry, recorded, line, swapped)
    with LeanService() as service:
        assert service.run_bound("evaluate", CASES) == genuine  # asked again, of the process
        assert service.stats["retries"] == 1
    assert [alarm["kind"] for alarm in seam.alarms] == ["refused"] and seam.counts["hits"] == 1
    assert seam.store.get(build, entry) is None  # the refused entry goes; the retry asked the process live
    plant(seam, build, entry, recorded, line, swapped)
    with LeanService(retries=0) as service, pytest.raises(CheckerUnavailable, match="malformed response"):
        service.run_bound("evaluate", CASES)


def test_a_planted_wrong_entry_fails_the_byte_replay(seam, executable, capsys):
    with LeanService() as service:
        service.run_bound("evaluate", CASES[:1])
        service.run_bound("evaluate", CASES[1:])
        build = service.build
    clean = replay(seam.store.root, executable, jobs=2)
    assert clean["ok"] and clean["same"] == clean["entries"] == 2 and clean["different"] == []
    assert answer_replay.main(["store-replay", "--store", str(seam.store.root)]) == 0
    (entry, path), _ = sorted(entries(seam, build))
    recorded, line, response = decode(path.read_bytes())
    seam.store.put(build, entry, recorded, line, response.replace(b'"status":"ok"', b'"status":"ok" ', 1))
    planted = replay(seam.store.root, executable, jobs=2)
    assert not planted["ok"] and [row["key"] for row in planted["different"]] == [entry] and planted["same"] == 1
    assert answer_replay.main(["store-replay", "--store", str(seam.store.root)]) == 1
    capsys.readouterr()


def test_an_empty_or_unreadable_store_is_reported(tmp_path, executable):
    empty = replay(tmp_path / "none", executable)
    assert empty["entries"] == 0 and empty["ok"]
    store = Store(tmp_path / "store")
    build = lean_service.executable_sha256(executable)
    store.path(build, "ab" * 32).parent.mkdir(parents=True)
    store.path(build, "ab" * 32).write_bytes(b"not an entry")
    broken = replay(store.root, executable)
    assert not broken["ok"] and [row["key"] for row in broken["unreadable"]] == ["ab" * 32]


PROXY = r'''
import json, os, subprocess, sys
real, counter, mode = sys.argv[1], sys.argv[2], sys.argv[3]
generation = int(open(counter).read()) if os.path.exists(counter) else 0
open(counter, "w").write(str(generation + 1))
if mode == "never" or (mode == "startup" and generation == 0):  # no handshake: always, or from the first
    sys.exit(1)
child = subprocess.Popen([real], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
sys.stdout.buffer.write(child.stdout.readline()); sys.stdout.flush()
for line in sys.stdin.buffer:
    if mode == "crash" and generation == 0:  # the first process dies on its first request
        child.kill(); sys.exit(1)
    if mode == "garbage" and generation == 0:  # the first process answers its first request with no JSON
        sys.stdout.buffer.write(b"garbage\n"); sys.stdout.flush(); child.kill(); sys.exit(1)
    child.stdin.write(line); child.stdin.flush()
    out = child.stdout.readline()
    if mode == "perturb" and generation % 2:  # the same value, other bytes, in every second process
        out = (json.dumps(json.loads(out)) + "\n").encode()
    if mode == "panic":  # what Lean prints for a panic, before the answer
        sys.stderr.write("PANIC at planted: index out of bounds\n"); sys.stderr.flush()
    sys.stdout.buffer.write(out); sys.stdout.flush()
'''


def proxy(tmp_path, executable, name, mode):
    """A wrapper around the real service: `same`, `perturb`, `panic`, `crash`, `garbage`, `startup` or `never`
    (PROXY)."""
    script = tmp_path / "proxy.py"
    script.write_text(PROXY)
    wrapper = tmp_path / name
    wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {script} {executable} {tmp_path / (name + '.count')} "
                       f"{mode}\n")
    wrapper.chmod(0o755)
    return wrapper


@pytest.mark.parametrize("perturb", [False, True], ids=["deterministic", "nondeterministic"])
def test_a_planted_nondeterministic_answer_fails_the_byte_replay(tmp_path, executable, perturb):
    service_path = proxy(tmp_path, executable, f"service-{int(perturb)}", "perturb" if perturb else "same")
    store = Store(tmp_path / "store")
    with LeanService(service_path, allow_unlisted_build=True) as service:
        service._ensure()
        line = LeanService._request_line("store-x", "evaluate", json.dumps(CASES[:1]), {"cases": 1, "bytes": 99999})
        deadline = lean_service._Deadline(lean_service.time.monotonic() + HANG_TIMEOUT)
        service._write_all(line, deadline)
        raw = service._read_line(deadline)
        store.put(service.build, key(service.build, limits(service), line), limits(service), line, raw)
    result = replay(store.root, service_path, allow_unlisted_build=True, jobs=1)
    assert result["entries"] == 1
    assert result["ok"] is (not perturb) and len(result["different"]) == int(perturb)


def test_an_answer_whose_request_wrote_to_standard_error_is_never_served(seam, tmp_path, executable):
    """Review F1: a hit writes nothing to the process's standard error, so a PANIC a live request prints must
    reach the test on every run: such an answer is never stored, a sampled hit that prints one is an alarm,
    and the byte replay fails on it."""
    seam.reason = lambda service, timeout: None  # the proxy is an unlisted build
    service_path = proxy(tmp_path, executable, "panic", "panic")
    seen = []
    record = seam.record
    seam.record = lambda service, line, raw, response: seen.append((line, raw)) or record(service, line, raw, response)
    for _ in range(2):
        with LeanService(service_path, allow_unlisted_build=True) as service:
            genuine = service.run_bound("evaluate", CASES)
            assert "PANIC" in service.stderr()[1]
            build, recorded = service.build, limits(service)
    assert seam.counts["recorded"] == 0 and seam.counts["not_recorded"] == 2 and seam.counts["hits"] == 0
    assert not seam.store.root.exists()
    # An entry for that line, as a silent run would have left it: the replay sees the PANIC ...
    (line, raw), _ = seen
    entry = key(build, recorded, line)
    plant(seam, build, entry, recorded, line, raw)
    replayed = replay(seam.store.root, service_path, allow_unlisted_build=True, jobs=1)
    assert not replayed["ok"] and [row["key"] for row in replayed["different"]] == [entry]
    assert "PANIC" in replayed["different"][0]["stderr"]
    # ... and so does a sampled hit: an alarm, the entry goes, the caller gets the process's answer.
    seam.sample = 1.0
    with LeanService(service_path, allow_unlisted_build=True) as service:
        assert service.run_bound("evaluate", CASES) == genuine and "PANIC" in service.stderr()[1]
    assert [alarm["kind"] for alarm in seam.alarms] == ["stderr"] and seam.store.get(build, entry) is None


def test_an_answer_that_needed_a_retry_is_never_stored(seam, tmp_path, executable):
    """Review F1 (row 9): a hit needs no retry, so `retries == 0` after a hit must mean the process answered at
    once. The retry after a failed attempt asks the process and is not stored."""
    seam.reason = lambda service, timeout: None  # the proxy is an unlisted build
    service_path = proxy(tmp_path, executable, "crash", "crash")
    with LeanService(service_path, allow_unlisted_build=True) as service:
        genuine = service.run_bound("evaluate", CASES)
        assert service.stats["retries"] == 1
    assert seam.counts["recorded"] == 0 and seam.counts["not_recorded"] == 1 and not seam.store.root.exists()
    with LeanService(service_path, allow_unlisted_build=True) as service:  # later processes answer at once
        assert service.run_bound("evaluate", CASES) == genuine and service.stats["retries"] == 0
    assert seam.counts["recorded"] == 1
    with LeanService(service_path, allow_unlisted_build=True) as service:
        assert service.run_bound("evaluate", CASES) == genuine
    assert seam.counts["hits"] == 1


FAILURES = ["startup", "crash", "garbage", "never"]


def _outcome(service_path, handles):
    """The answer (or CheckerUnavailable) and the retries and restarts of a client whose first request starts
    the process (not `with`, whose `start` would retry a failed start before any request)."""
    service = LeanService(service_path, allow_unlisted_build=True, handles=handles)
    try:
        try:
            answer = service.run_bound("evaluate", CASES)
        except CheckerUnavailable:
            answer = CheckerUnavailable
        return answer, service.stats["retries"], service.stats["restarts"]
    finally:
        service.close()


@pytest.mark.parametrize("handles", [True, False], ids=["environments", "inline"])
@pytest.mark.parametrize("failure", FAILURES)
def test_a_failed_attempt_with_the_store_on_ends_as_it_does_without(seam, monkeypatch, tmp_path, executable,
                                                                     failure, handles):
    """Review F6: whatever step of the first attempt fails (the process does not start, so a line that carries
    environments was never built; it dies on the request; it answers garbage; it never starts), the client with
    the store on retries as the client without it does and ends the same way: the same answer, or
    CheckerUnavailable, never a crash. Nothing is stored from an attempt that needed a retry."""
    seam.reason = lambda service, timeout: None  # the proxy is an unlisted build
    for side in ("on", "off"):  # each side's proxy counts its own process generations
        (tmp_path / side).mkdir()
    on = _outcome(proxy(tmp_path / "on", executable, failure, failure), handles)
    monkeypatch.setattr(lean_service, "answer_store", None)
    off = _outcome(proxy(tmp_path / "off", executable, failure, failure), handles)
    assert on == off and on[1] == 1
    assert (on[0] is CheckerUnavailable) is (failure == "never")
    assert seam.counts["recorded"] == 0 and not seam.store.root.exists() and seam.alarms == []


def test_a_checker_unavailable_request_error_is_never_recorded(seam):
    service = LeanService()
    line = b'{"id":"store-x","mode":"evaluate","cases":[]}\n'
    seam.local.pending = (line, "b" * 64, "k" * 64, None, 0)
    seam.record(service, line, b"{}", {"status": "error", "code": "CheckerUnavailable"})
    seam.local.pending = (line, "b" * 64, "k" * 64, b"stored", 0)
    seam.record(service, line, b"{}", {"status": "error", "code": "CheckerUnavailable"})
    assert seam.counts["not_recorded"] == 1 and seam.counts["sampled_inconclusive"] == 1
    assert seam.counts["recorded"] == 0 and seam.alarms == [] and not seam.store.root.exists()


def test_a_sampled_hit_that_drifted_is_an_alarm_and_the_caller_gets_the_process_answer(seam):
    with LeanService() as service:
        genuine = service.run_bound("evaluate", CASES)
        build = service.build
    [(entry, path)] = entries(seam, build)
    recorded, line, response = decode(path.read_bytes())
    plant(seam, build, entry, recorded, line, response.replace(b'"status":"ok"', b'"status":"ok" ', 1))
    seam.sample = 1.0
    with LeanService() as service:
        assert service.run_bound("evaluate", CASES) == genuine
    assert seam.counts["sampled"] == 1 and seam.counts["hits"] == 0
    assert [alarm["kind"] for alarm in seam.alarms] == ["drift"] and seam.store.get(build, entry) is None
    plant(seam, build, entry, recorded, line, response)
    seam.alarms.clear()
    with LeanService() as service:
        service.run_bound("evaluate", CASES)
    assert seam.counts["sampled_same"] == 1 and seam.alarms == []


def test_a_store_hit_in_an_r2_flagged_run_is_impossible(seam, monkeypatch, tmp_path):
    with LeanService() as service:
        genuine = service.run_bound("evaluate", CASES)
    assert seam.counts["recorded"] == 1
    monkeypatch.setenv(GATE_FLAG, str(tmp_path / "gate-result.json"))
    with LeanService() as service:
        assert service.run_bound("evaluate", CASES) == genuine
    assert seam.counts["hits"] == 0 and seam.off == {"gate": 1}
    # Asking for the store under the gate stops the run, in-process and in a pytest the gate starts.
    with pytest.raises(pytest.UsageError, match="R1 only"):
        settings(str(tmp_path / "s"), environ={GATE_FLAG: "x"})
    test = tmp_path / "test_one.py"
    test.write_text("def test_one():\n    pass\n")
    env = nested_pytest.environment(os.environ, PYTHONPATH=os.pathsep.join([str(ROOT / "tests"), str(ROOT)]),
                                    VE_GATE_PYTEST_RESULT=str(tmp_path / "gate-result.json"))
    run = subprocess.run(nested_pytest.command(["-p", "answer_store", "--answer-store", str(tmp_path / "s"), str(test)]),
                         cwd=tmp_path, env=env, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert run.returncode == pytest.ExitCode.USAGE_ERROR and "R1 only" in run.stderr
    assert not (tmp_path / "s").exists()
    # The gate's stages start from a listed environment: a store setting of the shell never reaches them.
    monkeypatch.setenv(ENV, str(tmp_path / "s"))
    assert ENV not in gate.gate_environment(tmp_path / "scratch")


def test_serving_is_off_for_every_request_the_plan_excludes(seam, monkeypatch, tmp_path, executable):
    default = LeanService()
    assert seam.reason(default, None) is None
    assert seam.reason(default, HANG_TIMEOUT) == "explicit timeout"
    # exchange passes the effective timeout: the request's, else the service's
    assert seam.reason(LeanService(timeout=HANG_TIMEOUT), HANG_TIMEOUT) == "explicit timeout"
    assert seam.reason(LeanService(expected_sha256="0" * 64), None) == "expected hash"
    assert seam.reason(LeanService(allow_unlisted_build=True), None) == "unlisted build"
    copy = tmp_path / "ve_service"
    copy.symlink_to(tmp_path / "elsewhere")
    assert seam.reason(LeanService(copy), None) == "non-default executable"

    class Sub(LeanService):
        pass
    assert seam.reason(Sub(), None) == "client subclass"
    seam.live = True
    assert seam.reason(default, None) == "live_service test"
    seam.live = False
    instance = LeanService()
    instance._read_line = lambda deadline: b""
    assert seam.reason(instance, None) == "client replaced by the test"
    for name in ("_write_all", "_read_line", "_deadline", "_spawn"):
        with monkeypatch.context() as patch:
            patch.setattr(LeanService, name, lambda *a, **k: None)
            assert seam.reason(default, None) == "client replaced by the test", name
    for name in ("time", "check_response", "_cpu_seconds", "_decode_json"):
        with monkeypatch.context() as patch:
            patch.setattr(lean_service, name, object())
            assert seam.reason(default, None) == "client replaced by the test", name
    monkeypatch.setenv(GATE_FLAG, "x")
    assert seam.reason(default, None) == "gate"


def test_a_service_with_its_own_timeout_is_never_served(seam):
    with LeanService() as service:
        service.run_bound("evaluate", CASES)
    with LeanService(timeout=HANG_TIMEOUT) as service:
        service.run_bound("evaluate", CASES)
        service.run_bound("evaluate", CASES, timeout=HANG_TIMEOUT)
    assert seam.counts["hits"] == 0 and seam.counts["recorded"] == 1 and seam.off == {"explicit timeout": 2}


def test_a_live_service_test_is_never_served_and_is_counted(seam):
    with LeanService() as service:
        service.run_bound("evaluate", CASES)
    seam.test, seam.live = "tests/x.py::test_live", True
    with LeanService() as service:
        service.run_bound("evaluate", CASES)
    assert seam.counts["hits"] == 0 and seam.live_tests == {"tests/x.py::test_live": 1}


def _repository(tmp_path, changes, untracked=()):
    repo = tmp_path / "repo"
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "init.defaultBranch=main", "-c",
           "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "-C", str(repo)]

    def run(*arguments):
        subprocess.run([*git, *arguments], check=True, capture_output=True, timeout=HANG_TIMEOUT)
    repo.mkdir()
    run("init", "-q")
    for name in ("ve/backends/relay.py", "docs/x.md", "tests/conftest.py"):
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text("base\n")
    run("add", "-A")
    run("commit", "-qm", "base")
    run("checkout", "-qb", "branch")
    for name in changes:
        (repo / name).write_text("changed\n")
    run("commit", "-qam", "change", "--allow-empty")
    for name in untracked:
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text("new\n")
    return repo


@pytest.mark.parametrize("changes, untracked, expected", [
    ((), (), []),
    (("docs/x.md",), (), []),
    (("ve/backends/relay.py",), (), ["ve/backends/relay.py"]),
    (("tests/conftest.py", "docs/x.md"), (), ["tests/conftest.py"]),
    ((), ("lean/VE/Service/New.lean",), ["lean/VE/Service/New.lean"]),
    ((), ("lean/checkers.lock", "tests/subprocesses.py", "tests/answer_store.py"),
     ["lean/checkers.lock", "tests/answer_store.py", "tests/subprocesses.py"]),
])
def test_serving_is_off_for_a_branch_that_changes_a_guarded_path(tmp_path, changes, untracked, expected):
    repo = _repository(tmp_path, changes, untracked)
    assert changed_guarded_paths(repo) == expected
    chosen = settings(str(tmp_path / "s"), environ={}, root=repo)
    assert (chosen["off"] is None) is (not expected)
    for path in expected:
        assert path in chosen["off"]


def test_serving_is_off_when_git_cannot_say_what_changed(tmp_path):
    (tmp_path / "plain").mkdir()
    assert changed_guarded_paths(tmp_path / "plain") is None
    assert "git cannot say" in settings(str(tmp_path / "s"), environ={}, root=tmp_path / "plain")["off"]


def test_the_plugin_takes_the_setting_out_of_the_environment_and_hands_it_to_workers(monkeypatch, tmp_path):
    monkeypatch.delenv(GATE_FLAG, raising=False)
    monkeypatch.setattr(lean_service, "answer_store", None)
    monkeypatch.setattr(answer_store, "changed_guarded_paths", lambda root=None: [])
    monkeypatch.setenv(ENV, str(tmp_path / "s"))
    config = SimpleNamespace(addinivalue_line=lambda *a: None, getoption=lambda name: None)
    answer_store.pytest_configure(config)
    assert ENV not in os.environ and isinstance(lean_service.answer_store, Seam)
    node = SimpleNamespace(config=config, workerinput={})
    answer_store.pytest_configure_node(node)
    assert node.workerinput["answer_store"] == {"directory": str((tmp_path / "s").resolve()), "off": None}
    worker = SimpleNamespace(addinivalue_line=lambda *a: None, getoption=lambda name: None,
                             workerinput=node.workerinput)
    monkeypatch.setattr(lean_service, "answer_store", None)
    answer_store.pytest_configure(worker)
    assert isinstance(lean_service.answer_store, Seam)
    # Not asked for: nothing installed; changed guarded paths: off, nothing installed.
    for asked, changed in ((None, []), (str(tmp_path / "s"), ["ve/backends/relay.py"])):
        monkeypatch.setattr(lean_service, "answer_store", None)
        monkeypatch.setattr(answer_store, "changed_guarded_paths", lambda root=None, changed=changed: changed)
        quiet = SimpleNamespace(addinivalue_line=lambda *a: None, getoption=lambda name, asked=asked: asked)
        answer_store.pytest_configure(quiet)
        assert lean_service.answer_store is None


def test_an_entry_is_one_request_line_and_one_response_line():
    entry = answer_store.encode((1, 2, 3), b'{"id":"x"}\n', b'{"id":"x"}')
    assert decode(entry) == ((1, 2, 3), b'{"id":"x"}\n', b'{"id":"x"}')
    for line, response in ((b"no newline", b"r"), (b"a\nb\n", b"r"), (b"a\n", b"r\n")):
        with pytest.raises(ValueError):
            answer_store.encode((1,), line, response)
    with pytest.raises(ValueError):
        decode(b"garbage")
    # The key binds the build, the start-up limits and every byte of the line.
    base = key("b" * 64, (1, 2, 3), b"line\n")
    assert len({base, key("c" * 64, (1, 2, 3), b"line\n"), key("b" * 64, (1, 2, 4), b"line\n"),
                key("b" * 64, (1, 2, 3), b"line \n")}) == 4


def _live(path: Path, name: str) -> bool:
    """Whether `name` (or, when empty, the whole module) in the test file carries the live_service mark."""
    tree = ast.parse(path.read_text())

    def marked(node):
        return any(isinstance(n, ast.Attribute) and n.attr == LIVE_MARK for n in ast.walk(node))
    module = any(isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "pytestmark" for t in node.targets)
                 and marked(node.value) for node in tree.body)
    if not name:
        return module
    [function] = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    return module or any(marked(decorator) for decorator in function.decorator_list)


def test_every_inventory_test_exists_and_runs_live():
    assert [row[0] for row in INVENTORY] == list(range(1, 15))
    for row, behaviour, skipped, tests in INVENTORY:
        for test in tests:
            path, _, name = test.partition("::")
            assert (ROOT / path).is_file(), test
            if row != 1:  # the relay sits above the seam: nothing of it is skipped
                assert _live(ROOT / path, name), (row, test)


def test_a_repeated_batch_is_answered_from_memory_within_its_bound(seam, monkeypatch):
    with LeanService() as service:
        genuine = service.run_bound("evaluate", CASES)
        build = service.build
    [(entry, path)] = entries(seam, build)
    path.unlink()  # a repeat in the same process does not read the store again
    with LeanService() as service:
        assert service.run_bound("evaluate", CASES) == genuine
    assert seam.counts["hits"] == 1 and seam.counts["misses"] == 1
    monkeypatch.setattr(answer_store, "MEMORY_BYTES", 0)
    with LeanService() as service:
        service.run_bound("evaluate", CASES[:1])
    assert seam.memory_bytes == 0 and not seam.memory


def test_a_changed_client_setting_turns_the_store_off(seam, monkeypatch):
    """Review F1 (row 8): `lean_routes.completed_within` lowers a mode's CPU deadline in place; a hit would skip
    its enforcement. Every binding, table and `VE_LEAN_SERVICE*` setting of the client is compared with those the
    store was installed with, read from the client itself, not listed by hand."""
    lean_routes.completed("evaluate", CASES)
    assert lean_routes.completed("evaluate", CASES).returncode == 0
    assert seam.counts["recorded"] == 1 and seam.counts["hits"] == 1
    assert lean_routes.completed_within("evaluate", CASES, cpu_seconds=HANG_TIMEOUT).returncode == 0
    assert seam.counts["hits"] == 1 and seam.off == {"client setting changed by the test": 1}
    default = LeanService()
    assert seam.reason(default, None) is None
    with monkeypatch.context() as patch:
        patch.setenv("VE_LEAN_SERVICE_TIMEOUT", str(2 * HANG_TIMEOUT))  # any change, not only a lower one
        assert seam.reason(default, None) == "client setting changed by the test"
    with monkeypatch.context() as patch:
        patch.setitem(lean_service.DEADLINES, "evaluate", (2 * HANG_TIMEOUT, 0.0))
        assert seam.reason(default, None) == "client setting changed by the test"
    assert {"DEADLINES", "MAX_RESPONSE_BYTES", "WALL_FACTOR", "time", "_cpu_seconds"} <= set(SEAM_GLOBALS)
    assert {"exchange", "_roundtrip", "_wait", "stderr", "build"} <= set(answer_store.SEAM)
    for name in SEAM_GLOBALS:
        with monkeypatch.context() as patch:
            patch.setattr(lean_service, name, object())
            assert seam.reason(default, None) == "client replaced by the test", name
    for name in answer_store.SEAM:
        with monkeypatch.context() as patch:
            patch.setattr(LeanService, name, object())
            assert seam.reason(default, None) == "client replaced by the test", name
    assert seam.reason(default, None) is None


NESTED = '''
import json, pathlib
import pytest
from ve.backends.lean_service import LeanService
CASES = json.loads(pathlib.Path({evaluation!r}).read_text())[:3]


def ask():
    with LeanService() as service:
        return service.run_bound("evaluate", CASES)


def test_unmarked():
    ask()


@pytest.mark.live_service
def test_marked():
    ask()
'''


def test_the_plugin_serves_only_unmarked_tests_and_an_alarm_fails_the_run(tmp_path, monkeypatch, executable):
    """Review F2: the plugin itself, in a nested pytest with the store on, one and two workers: a test marked
    `live_service` is never served (pytest_runtest_protocol reads the mark), the workers' reports are merged
    (pytest_testnodedown, merged), and an alarm (a planted entry the client refuses) fails a run whose tests
    all pass."""
    monkeypatch.delenv("VE_LEAN_SERVICE", raising=False)
    (tmp_path / "test_nested.py").write_text(NESTED.format(evaluation=str(ROOT / "conformance/evaluation.json")))
    # This branch's checkout changes guarded paths, so the nested run is told it does not (the one stand-in).
    (tmp_path / "unchanged_branch.py").write_text("import answer_store\n"
                                                  "answer_store.changed_guarded_paths = lambda root=None: []\n")
    directory = tmp_path / "store"
    env = nested_pytest.environment(os.environ, PYTHONPATH=os.pathsep.join([str(tmp_path), str(ROOT / "tests"),
                                                                             str(ROOT)]))

    def run(workers):
        before = set((directory / "runs").glob("*.json"))
        done = subprocess.run(
            nested_pytest.command(["-q", "-p", "no:cacheprovider", "-p", "unchanged_branch", "-p", "answer_store",
                                   f"--answer-store={directory}", "test_nested.py"], workers=workers),
            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=HANG_TIMEOUT)
        [summary] = set((directory / "runs").glob("*.json")) - before
        return done, json.loads(summary.read_text())

    first, recorded = run(2)
    assert first.returncode == 0 and "2 passed" in first.stdout, first.stdout + first.stderr
    assert recorded["off"] is None and recorded["alarms"] == []
    assert recorded["counts"]["recorded"] == 1 and recorded["counts"]["hits"] == 0
    assert recorded["live_tests"] == {"test_nested.py::test_marked": 1}
    for workers in (2, 1):
        done, served = run(workers)
        assert done.returncode == 0 and "2 passed" in done.stdout, done.stdout + done.stderr
        counts = served["counts"]
        # Only the unmarked test is answered from the store (a sampled hit is asked live as well).
        assert counts["hits"] + counts["sampled"] == 1 and counts["recorded"] == 0, (workers, counts)
        assert served["off_requests"] == {"live_service test": 1} and served["alarms"] == []
        assert served["live_tests"] == {"test_nested.py::test_marked": 1}
        assert "answer store: 1 requests looked up" in done.stdout
    # A planted entry the client refuses: the test still passes (retried live), the run fails on the alarm.
    store = Store(directory)
    [build] = [path.name for path in (directory / answer_store.FORMAT).iterdir()]
    [(entry, path)] = store.entries(build)
    limits_, line, response = decode(path.read_bytes())
    swapped = response.replace(b'"index":0,', b'"index":9,').replace(b'"index":1,', b'"index":0,').replace(
        b'"index":9,', b'"index":1,')
    assert swapped != response
    store.put(build, entry, limits_, line, swapped)
    planted, alarmed = run(2)
    assert "2 passed" in planted.stdout and planted.returncode == pytest.ExitCode.TESTS_FAILED, planted.stdout
    assert {alarm["kind"] for alarm in alarmed["alarms"]} <= {"refused", "drift"} and alarmed["alarms"]
    assert "ANSWER STORE ALARM" in planted.stdout
