"""Records every Lean and Rust checker call of a VE process (measurements for docs/LEAN-FIRST-PLAN.md).

Active only when VE_LEANFIRST_LOG names a JSON-lines file; load it with
PYTHONPATH=docs/lean-first/hook. One line per call:

- `oneshot`: a `subprocess.run` of a `lean/.lake/build/bin` executable (exe, mode argument,
  input bytes, case count, wall seconds);
- `spawn`: a `ve_service` start (build hash and handshake included);
- `service`: one service request (`LeanService._roundtrip`): mode, cases, request bytes, wall
  seconds, of which `ipc` is write + read (Lean's compute plus the pipe) and the rest is the
  client's schema check;
- `rust`: one Rust JSON-lines process.

VE_LEANFIRST_TIMEOUT=<seconds> raises the service's 5 s interactive limit and Rust's 5 s limit (measurement
only), so a run under host load completes and can be timed.

Each line carries `tag` (VE_LEANFIRST_TAG), the pid and `caller`, the innermost `ve` frame
outside `ve/backends`, so calls can be attributed to an operation. `cpu` is the checker's own
CPU seconds (children's rusage for processes, `/proc/<pid>/schedstat` for the service), which
other load on the host does not inflate the way it inflates `wall`.
"""
from __future__ import annotations

import importlib.abc
import json
import os
import resource
import subprocess
import sys
import threading
import time

LOG = os.environ.get("VE_LEANFIRST_LOG")
TAG = os.environ.get("VE_LEANFIRST_TAG", "")
_lock = threading.Lock()


def _caller() -> str:
    frame = sys._getframe(2)
    fallback = None
    while frame is not None:
        name = frame.f_code.co_filename.replace(os.sep, "/")
        if "/ve/" in name and "/ve/backends/" not in name and "/ve/assurance" not in name:
            return f"{name.rsplit('/ve/', 1)[1]}:{frame.f_code.co_name}"
        if fallback is None and "/docs/lean-first/" not in name and "/subprocess.py" not in name \
                and "/ve/backends/" not in name:
            fallback = f"{name.rsplit('/', 1)[-1]}:{frame.f_code.co_name}"
        frame = frame.f_back
    return fallback or "?"


def _log(**record) -> None:
    record.update(tag=TAG, pid=os.getpid())
    line = json.dumps(record, separators=(",", ":")) + "\n"
    with _lock, open(LOG, "a") as handle:
        handle.write(line)


def _children_cpu() -> float:
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


def _oncpu(pid) -> float:
    try:
        with open(f"/proc/{pid}/schedstat") as handle:
            return int(handle.read().split()[0]) / 1e9
    except (OSError, ValueError, IndexError):
        return 0.0


def _count(data) -> int | None:
    if data is None:
        return None
    try:
        value = json.loads(data)
    except (ValueError, TypeError, RecursionError):
        return None
    return len(value) if type(value) is list else None


def _patch_subprocess() -> None:
    original = subprocess.run

    def run(*args, **kwargs):
        argv = args[0] if args else kwargs.get("args")
        exe = str(argv[0]) if isinstance(argv, (list, tuple)) and argv else str(argv)
        if "/.lake/build/bin/" not in exe and not exe.endswith("/lean"):
            return original(*args, **kwargs)
        data = kwargs.get("input")
        caller = _caller()
        cpu = _children_cpu()
        started = time.perf_counter()
        try:
            return original(*args, **kwargs)
        finally:
            _log(kind="oneshot", exe=exe.rsplit("/", 1)[-1],
                 args=[str(a) for a in argv[1:]] if isinstance(argv, (list, tuple)) else [],
                 bytes=len(data) if data is not None else None, cases=_count(data),
                 wall=time.perf_counter() - started, cpu=_children_cpu() - cpu, caller=caller)

    subprocess.run = run


TIMEOUT = os.environ.get("VE_LEANFIRST_TIMEOUT")


def _patch_service(module) -> None:
    service = module.LeanService
    if TIMEOUT:
        # Measurement only: the interactive 5 s limit fails under host load before a run can be timed.
        service.__init__.__kwdefaults__["timeout"] = float(TIMEOUT)
    spawn, roundtrip = service._spawn, service._roundtrip
    write, read = service._write_all, service._read_line

    def _spawn(self):
        started = time.perf_counter()
        try:
            return spawn(self)
        finally:
            _log(kind="spawn", wall=time.perf_counter() - started, caller=_caller())

    def _write_all(self, data, deadline):
        started = time.perf_counter()
        try:
            return write(self, data, deadline)
        finally:
            self._lf_ipc = getattr(self, "_lf_ipc", 0.0) + time.perf_counter() - started

    def _read_line(self, deadline):
        started = time.perf_counter()
        try:
            return read(self, deadline)
        finally:
            self._lf_ipc = getattr(self, "_lf_ipc", 0.0) + time.perf_counter() - started

    def _roundtrip(self, mode, cases_text, count, timeout, nonce, line, texts):
        self._lf_ipc = 0.0
        caller = _caller()
        pid = self.pid
        cpu = _oncpu(pid)
        started = time.perf_counter()
        try:
            return roundtrip(self, mode, cases_text, count, timeout, nonce, line, texts)
        finally:
            _log(kind="service", mode=mode, cases=count, bytes=len(line),
                 wall=time.perf_counter() - started, ipc=self._lf_ipc, cpu=_oncpu(pid) - cpu,
                 caller=caller)

    service._spawn, service._roundtrip = _spawn, _roundtrip
    service._write_all, service._read_line = _write_all, _read_line


def _patch_rust(module) -> None:
    original = module._run_checker
    if TIMEOUT:
        module.run.__kwdefaults__["timeout"] = float(TIMEOUT)

    def _run_checker(argv, *, input, timeout):
        caller = _caller()
        cpu = _children_cpu()
        started = time.perf_counter()
        try:
            return original(argv, input=input, timeout=timeout)
        finally:
            _log(kind="rust", bytes=len(input), wall=time.perf_counter() - started,
                 cpu=_children_cpu() - cpu, caller=caller)

    module._run_checker = _run_checker


_PATCHES = {"ve.backends.lean_service": _patch_service, "ve.backends.rust_jsonl": _patch_rust}


class _Finder(importlib.abc.MetaPathFinder):
    """Patches a module of `_PATCHES` right after it executes."""

    def find_spec(self, name, path, target=None):
        if name not in _PATCHES:
            return None
        sys.meta_path.remove(self)
        try:
            spec = importlib.util.find_spec(name)
        finally:
            sys.meta_path.insert(0, self)
        if spec is None or spec.loader is None:
            return spec
        loader = spec.loader
        execute = loader.exec_module

        def exec_module(module):
            execute(module)
            _PATCHES[name](module)

        loader.exec_module = exec_module
        return spec


if LOG:
    import importlib.util  # noqa: F401  (used by the finder)
    _patch_subprocess()
    sys.meta_path.insert(0, _Finder())
