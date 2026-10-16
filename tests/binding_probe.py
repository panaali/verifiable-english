"""A pytest plugin that finds which Python hand binder refuses each shape-generated mutant of a Lean answer.

Loaded with `-p tests.binding_probe` and `VE_BINDING_PROBE=<directory>` (by `tools/binding_census.py --probe`).
When a test's code receives Lean's answer (`LeanServicePool.run_bound`, through which every relay call goes),
the plugin forks the test process once per mutant of that answer (`tests/binding_mutants.py`). The child gets
the mutant in place of the answer, *after* the shape check, so what it shows is the hand path alone: it drops
the parent's service processes (and starts its own), runs the rest of the test, and reports

* every `CheckerUnavailable` the code created after the mutant arrived, with the `ve` lines that raised it
  (the first is the hand binder that refused it);
* how the test ended (passed, or the exception it failed with, and where `ve` raised it).

The parent waits for the child, then continues with the genuine answer, so the test itself runs unchanged.
Each (mode, calling function) is probed on its first `PER_CALLER` calls and on the first call of each answer
shape it receives (case kinds and row members); a mutant already probed for that caller (same path and kind)
is skipped. One line per probed mutant goes to `<directory>/probe-<pid>.jsonl`, with the
generic checker's verdict on the same mutant beside it, and one `genuine` line per probed call: its case and
Lean's answer.

Only answers received on the main thread are probed (a fork keeps only the calling thread).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import select
import signal
import sys
import time
import traceback
import warnings

import pytest

OUT = os.environ.get("VE_BINDING_PROBE")
PER_CALLER = 2
PER_MUTANT = 1
# The genuine answer of each probed call is kept (a recorded answer of the generic test) up to this size.
GENUINE_LIMIT = 200_000
# How long a child may run the rest of its test (a measurement tool's limit; a child past it is killed and
# recorded as `timeout`).
CHILD_TIMEOUT = 600
ROOT = Path(__file__).resolve().parents[1]
# The transport (the relay, the service client and the one-shot runner), the errors and the shape checker are never
# the hand binder: a refusal they make concerns a later Lean request, or is the shape check itself.
_TRANSPORT = ("ve/backends/relay.py", "ve/backends/lean_service.py", "ve/backends/lean.py")
_SKIP = (*_TRANSPORT, "ve/errors.py", "ve/backends/service_schema.py")
_state = {"child": None, "item": None, "phase": None, "created": [], "calls": {}, "probed": {}}


def _ve_frames(frames) -> list:
    """(file, line, function) of the `ve` frames, innermost first, outside the transport."""
    out = []
    for frame in reversed(frames):
        path = Path(frame.filename)
        try:
            relative = str(path.resolve().relative_to(ROOT))
        except ValueError:
            continue
        if relative.startswith("ve/") and relative not in _SKIP:
            out.append([relative, frame.lineno, frame.name])
    return out


def _created_in_transport(stack) -> bool:
    """Whether the innermost repository frame that built the error is the relay's or the service client's."""
    for frame in reversed(stack):
        path = Path(frame.filename).resolve()
        if path == Path(__file__).resolve() or not path.is_relative_to(ROOT):
            continue
        relative = str(path.relative_to(ROOT))
        if relative == "ve/errors.py":
            continue
        return relative in _TRANSPORT
    return False


def _relative(filename: str) -> str:
    path = Path(filename).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else ""


def _caller() -> tuple:
    frames = _ve_frames(traceback.extract_stack()[:-3])
    return tuple(frames[0][::2]) if frames else ("?", "?")


def _install():
    from ve import errors
    from ve.backends import relay
    from ve.backends.lean_service import LeanServicePool
    original_init = errors.CheckerUnavailable.__init__

    def init(self, *args, **kwargs):
        if _state["child"] is not None:
            handled = sys.exc_info()[1]
            stack = traceback.extract_stack()[:-1]
            _state["created"].append({
                "message": str(args[0])[:200] if args else "",
                "frames": _ve_frames(stack)[:4],
                # Created by the relay or the service client: a later request (the mutant sent back to Lean) was
                # refused, not the mutant itself by a binder.
                "transport": _created_in_transport(stack),
                # Raised while handling another exception (a binder's `except ...: raise unavailable(...)`): where
                # that one was raised is where the answer was found unbound.
                "cause": None if handled is None else {
                    "type": type(handled).__name__, "message": str(handled)[:200],
                    "frames": _ve_frames(traceback.extract_tb(handled.__traceback__))[:4],
                    # A later Lean request's rejection, converted by the hand path.
                    "transport": any(_relative(f.filename) in _TRANSPORT
                                     for f in traceback.extract_tb(handled.__traceback__))}})
        original_init(self, *args, **kwargs)
    errors.CheckerUnavailable.__init__ = init
    original = LeanServicePool.run_bound

    def run_bound(self, mode, cases, *, timeout=None):
        entries = original(self, mode, cases, timeout=timeout)
        if _state["child"] is not None or _state["item"] is None or not _main_thread():
            return entries
        caller = _caller()
        key, shape = (mode, caller), (mode, caller, _shape(cases, entries))
        # The first PER_CALLER calls of each caller, and the first call of each answer shape it receives.
        if _state["calls"].get(key, 0) >= PER_CALLER and shape in _state["calls"]:
            return entries
        _state["calls"][key] = _state["calls"].get(key, 0) + 1
        _state["calls"][shape] = 1
        _probe(relay, mode, list(cases), entries, caller)
        return entries
    LeanServicePool.run_bound = run_bound


def _shape(cases, entries) -> tuple:
    """The case kinds and row members of a call: what tells one answer branch from another."""
    return tuple((case.get("kind") if isinstance(case, dict) else None,
                  tuple(sorted(entry["result"])) if isinstance(entry.get("result"), dict) else ())
                 for case, entry in zip(cases, entries))


def _main_thread() -> bool:
    import threading
    return threading.current_thread() is threading.main_thread()


def _probe(relay, mode, cases, entries, caller):
    from tests import binding_mutants
    for index, entry in enumerate(entries):
        if "code" not in entry and isinstance(entry.get("result"), dict) and entry["result"].get("status") != "error":
            break
    else:
        return
    case, row = cases[index], entry["result"]
    genuine = json.dumps({"genuine": [mode, case, row, index], "caller": list(caller), "test": _state["item"]})
    if len(genuine) <= GENUINE_LIMIT:
        _write_text(genuine)
    try:
        found = binding_mutants.mutants(mode, case, row, index)
    except Exception as exc:  # noqa: BLE001 - recorded, never fatal to the test
        _write({"mode": mode, "caller": caller, "test": _state["item"], "error": f"{type(exc).__name__}: {exc}"})
        return
    for mutant in found:
        seen = (mode, caller, mutant.path, mutant.kind)
        if _state["probed"].get(seen, 0) >= PER_MUTANT:
            continue
        _state["probed"][seen] = _state["probed"].get(seen, 0) + 1
        mutated = [dict(e) for e in entries]
        mutated[index] = {**entry, "result": mutant.row}
        outcome = _fork(relay, mutated)
        _write({"mode": mode, "caller": list(caller), "test": _state["item"], "phase": _state["phase"],
                "kind": mutant.kind, "path": mutant.path, "where": [str(s) for s in mutant.where],
                "expect": mutant.expect, "why": mutant.why,
                "generic": binding_mutants.verdict(mode, case, mutant.row, index), **outcome})


def _fork(relay, mutated) -> dict:
    """Run the rest of the test in a child that receives `mutated`; its report."""
    read, write = os.pipe()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)  # forking with the service's reader threads alive
        pid = os.fork()
    if pid == 0:
        os.close(read)
        _state["child"] = write
        _state["created"] = []
        relay._pool, relay._pools = None, {}
        raise _Return(mutated)
    os.close(write)
    chunks, deadline = [], time.monotonic() + CHILD_TIMEOUT
    while True:
        remaining = deadline - time.monotonic()
        ready, _, _ = select.select([read], [], [], max(remaining, 0))
        if not ready:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
            os.close(read)
            return {"outcome": "timeout"}
        chunk = os.read(read, 1 << 16)
        if not chunk:
            break
        chunks.append(chunk)
    os.close(read)
    os.waitpid(pid, 0)
    try:
        return json.loads(b"".join(chunks))
    except ValueError:
        return {"outcome": "no-report"}


class _Return(BaseException):
    """Unwinds nothing: `run_bound`'s wrapper catches it in the child and returns the mutant."""

    def __init__(self, entries):
        super().__init__()
        self.entries = entries


def _finish(excinfo):
    """In the child: report and exit, skipping every teardown and the rest of the session."""
    report = {"refusals": _state["created"]}
    if excinfo is None:
        report["outcome"] = "passed"
    else:
        exc = excinfo.value
        frames = _ve_frames(traceback.extract_tb(excinfo.tb))[:3]
        report["outcome"] = type(exc).__name__
        report["raised"] = frames
        report["message"] = str(exc)[:200]
    data = json.dumps(report).encode()
    try:
        while data:
            data = data[os.write(_state["child"], data):]
    finally:
        relay = sys.modules.get("ve.backends.relay")
        if relay is not None:
            try:
                relay._close()
            except Exception:  # noqa: BLE001
                pass
        os._exit(0)


def _write(record):
    _write_text(json.dumps(record))


def _write_text(line: str):
    directory = Path(OUT)
    directory.mkdir(parents=True, exist_ok=True)
    with open(directory / f"probe-{os.getpid()}.jsonl", "a") as out:
        out.write(line + "\n")


if OUT:
    _install()
    from ve.backends.lean_service import LeanServicePool as _Pool
    _wrapped = _Pool.run_bound

    def _run_bound(self, mode, cases, *, timeout=None):
        try:
            return _wrapped(self, mode, cases, timeout=timeout)
        except _Return as returned:
            return returned.entries
    _Pool.run_bound = _run_bound

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(item, nextitem):
        _state["item"] = item.nodeid
        yield
        _state["item"] = None

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(item, call):
        _state["phase"] = call.when
        if _state["child"] is not None and (call.when != "setup" or call.excinfo is not None):
            _finish(call.excinfo)
        yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup(item):
        _state["phase"] = "setup"
        yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(item):
        _state["phase"] = "call"
        yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_teardown(item):
        _state["phase"] = "teardown"
        yield
