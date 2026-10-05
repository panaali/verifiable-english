"""Pytest plugin: where a test run's time goes (docs/testing-profile.md).

Load with ``-p tools.pytest_profile`` and set ``VE_TEST_PROFILE_DIR``; each
pytest process (every xdist worker) writes one JSON-lines file there:

* ``{"kind": "test", ...}`` per test: wall seconds of setup, call and
  teardown, the worker's own CPU seconds (Python work) and the CPU seconds of
  the child processes reaped during the test.
* ``{"kind": "proc", ...}`` per child process started through ``subprocess``:
  the executable's base name, the test that started it, its lifetime and its
  own CPU seconds (from ``wait4``).

The plugin only observes: it changes no test's inputs, outputs or timeouts.
``tools/test_profile_report.py`` aggregates the files.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import resource
import subprocess
import threading
import time

import pytest

_current = {"test": None, "phase": None}
_out = None
_out_lock = threading.Lock()
_rusage: dict[int, resource.struct_rusage] = {}


def _emit(record: dict) -> None:
    if _out is None:
        return
    with _out_lock:
        _out.write(json.dumps(record) + "\n")
        _out.flush()


def _wait4(pid, flags):
    pid_done, status, usage = os.wait4(pid, flags)
    if pid_done:
        _rusage[pid_done] = usage
    return pid_done, status


def _install() -> None:
    popen = subprocess.Popen
    original_init = popen.__init__
    original_handle = popen._handle_exitstatus

    def init(self, args, *rest, **kwargs):
        self._ve_profile = None
        original_init(self, args, *rest, **kwargs)
        first = args if isinstance(args, (str, bytes, os.PathLike)) else (args[0] if args else "")
        name = os.path.basename(os.fsdecode(first).split()[0]) if first else ""
        self._ve_profile = (name, time.monotonic(), _current["test"], _current["phase"])

    def handle(self, sts, *rest, **kwargs):
        original_handle(self, sts, *rest, **kwargs)
        info = getattr(self, "_ve_profile", None)
        if info is None:
            return
        self._ve_profile = None
        name, start, test, phase = info
        usage = _rusage.pop(self.pid, None)
        _emit({"kind": "proc", "exe": name, "test": test, "phase": phase,
               "end_test": _current["test"], "wall": time.monotonic() - start,
               "cpu": None if usage is None else usage.ru_utime + usage.ru_stime,
               "rc": self.returncode})

    def try_wait(self, wait_flags):
        try:
            return _wait4(self.pid, wait_flags)
        except ChildProcessError:
            return self.pid, 0

    popen.__init__ = init
    popen._handle_exitstatus = handle
    popen._try_wait = try_wait
    # `poll` reaps through this namespace's waitpid.
    subprocess._del_safe.waitpid = _wait4


def pytest_configure(config):
    global _out
    directory = os.environ.get("VE_TEST_PROFILE_DIR")
    if not directory:
        return
    worker = getattr(config, "workerinput", {}).get("workerid", "main")
    Path(directory).mkdir(parents=True, exist_ok=True)
    _out = open(Path(directory) / f"{worker}-{os.getpid()}.jsonl", "a", encoding="utf-8")
    _install()


def _cpu(who):
    usage = resource.getrusage(who)
    return usage.ru_utime + usage.ru_stime


def _phase(item, phase):
    _current["test"], _current["phase"] = item.nodeid, phase
    record = item.__dict__.setdefault("_ve_profile", {"kind": "test", "nodeid": item.nodeid})
    start, self0, child0 = time.monotonic(), _cpu(resource.RUSAGE_SELF), _cpu(resource.RUSAGE_CHILDREN)

    def done():
        record[phase] = time.monotonic() - start
        record["self_cpu"] = record.get("self_cpu", 0.0) + _cpu(resource.RUSAGE_SELF) - self0
        record["child_cpu"] = record.get("child_cpu", 0.0) + _cpu(resource.RUSAGE_CHILDREN) - child0
    return done


def _wrap(item, phase):
    if _out is None:
        yield
        return
    done = _phase(item, phase)
    yield
    done()
    if phase == "teardown":
        _emit(item._ve_profile)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    yield from _wrap(item, "setup")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    yield from _wrap(item, "call")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item):
    yield from _wrap(item, "teardown")


def pytest_unconfigure(config):
    global _out
    _current["test"], _current["phase"] = None, "session"
    if _out is not None:
        _out.flush()
