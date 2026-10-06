"""Bounded client for Rust's JSON-lines evaluator and searcher.

Each call sends one case line and reads one record line. Since lean-first batch 2 (F6 in
docs/LEAN-FIRST-PLAN.md section 4) the line goes to a persistent `ve jsonl -` process, which
answers and flushes each record, instead of a new process per case (13 ms of wall and 4 ms of
CPU per call in the agent-policy harness, plus a SHA-256 of the binary per call). Records are
independent, so a process is reused across calls; one that times out, ends its output or
writes anything but one record is killed and never reused, and the call is
`CheckerUnavailable`, as a failed one-shot process was. A process is reused only while its
executable keeps the file identity it was started from.
"""
from __future__ import annotations

import atexit
import json
import os
from pathlib import Path
import selectors
import subprocess
import tempfile
import threading
import time

from ..errors import ResourceLimit
from .diagnostics import require_ok
from ..environment_wire import EncodedEnvironment, encoded_environment, wire_checked
from .lean_service import CheckerUnavailable, _decode_json, configured_seconds, executable_sha256
from .service_schema import Compiler, Context, Invalid

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = Path(__file__).resolve().parent / "rust_schema"
DEFAULT_EXECUTABLE = ROOT / "rust/target/release/ve"
BUILD_LOCK = ROOT / "lean/checkers.lock"
MAX_LINE_BYTES = 16 * 1024 * 1024
DEFAULT_TIMEOUT = 5.0


def configured_timeout(default: float = DEFAULT_TIMEOUT) -> float:
    """The wall-clock timeout of one Rust call whose caller's default is `default`:
    `VE_RUST_TIMEOUT` when set (the test suite raises it to its hang guard, so
    machine load cannot fail a test), else `default`. A guard against a hung
    checker only; Rust's work limits are its evaluation budgets."""
    return configured_seconds("VE_RUST_TIMEOUT", default)


def _identity(path: str):
    """The file identity of an executable: a process is reused only while it is unchanged."""
    st = os.stat(path)
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


def _deadline(timeout: float) -> float:
    """The monotonic time a call given `timeout` seconds must be answered by (a test seam: a
    deadline test injects an expired one)."""
    return time.monotonic() + timeout


class _Checker:
    """One persistent `ve jsonl -` process: a case line in, its record line out."""

    def __init__(self, argv):
        self.argv = list(argv)
        self.identity = _identity(self.argv[0])
        self.stderr = tempfile.TemporaryFile()
        self.process = subprocess.Popen(self.argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self.stderr, bufsize=0, close_fds=True)
        os.set_blocking(self.process.stdin.fileno(), False)
        os.set_blocking(self.process.stdout.fileno(), False)
        self.buffer = bytearray()

    def usable(self) -> bool:
        """Whether the process may answer another case: it runs, its executable is unchanged, and it
        has written nothing since its last record (output that answers no case is never read as the
        next case's answer)."""
        try:
            if self.process.poll() is not None or _identity(self.argv[0]) != self.identity:
                return False
            os.read(self.process.stdout.fileno(), 1)
        except BlockingIOError:
            return True
        except OSError:
            return False
        return False

    def _failure(self, what: str) -> OSError:
        try:
            code = self.process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            code = None
        self.stderr.seek(0)
        detail = self.stderr.read()[-200:].decode("utf-8", "replace").strip()
        return OSError(f"{what} (exit {code}{'; ' + detail if detail else ''})")

    def exchange(self, data: bytes, timeout: float) -> bytes:
        """The record line answering the case line `data`. `TimeoutExpired` once `timeout`
        seconds have passed; `OSError` if the process stops reading or ends its output, or its
        record exceeds the line limit."""
        deadline = _deadline(timeout)
        view = memoryview(data)
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdin.fileno(), selectors.EVENT_WRITE)
            while view:
                if time.monotonic() >= deadline:
                    raise subprocess.TimeoutExpired(self.argv, timeout)
                if not selector.select(deadline - time.monotonic()):
                    continue
                try:
                    view = view[os.write(self.process.stdin.fileno(), view):]
                except BlockingIOError:
                    continue
                except OSError:
                    raise self._failure("the Rust checker stopped reading") from None
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdout.fileno(), selectors.EVENT_READ)
            while (end := self.buffer.find(b"\n")) < 0:
                if len(self.buffer) > MAX_LINE_BYTES:
                    raise OSError("oversized Rust JSONL response")
                if time.monotonic() >= deadline:
                    raise subprocess.TimeoutExpired(self.argv, timeout)
                if not selector.select(deadline - time.monotonic()):
                    continue
                try:
                    chunk = os.read(self.process.stdout.fileno(), 1 << 20)
                except BlockingIOError:
                    continue
                if not chunk:
                    raise self._failure("the Rust checker ended its output")
                self.buffer += chunk
        line = bytes(self.buffer[:end])
        del self.buffer[:end + 1]
        if self.buffer:
            raise OSError("the Rust checker wrote more than one record")
        return line

    def close(self) -> None:
        for stream in (self.process.stdin, self.process.stdout):
            try:
                stream.close()
            except OSError:
                pass
        if self.process.poll() is None:
            self.process.kill()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        self.stderr.close()


# Idle processes by argv. A call takes one (or starts one) and gives it back only after a
# complete answer, so concurrent callers never share a process.
_idle: dict[tuple, list[_Checker]] = {}
_idle_lock = threading.Lock()


def _close_all() -> None:
    with _idle_lock:
        checkers = [checker for idle in _idle.values() for checker in idle]
        _idle.clear()
    for checker in checkers:
        checker.close()


def _forget_in_child() -> None:
    """A forked child does not inherit its parent's processes (their pipes are the parent's)."""
    global _idle_lock
    _idle.clear()
    _idle_lock = threading.Lock()


atexit.register(_close_all)
os.register_at_fork(after_in_child=_forget_in_child)


def _answer(checker: _Checker, data: bytes, timeout: float) -> bytes:
    """`checker`'s record for `data`; a process that gives none is closed, whatever stopped it."""
    answered = False
    try:
        line = checker.exchange(data, timeout)
        answered = True
        return line
    finally:
        if not answered:
            checker.close()


def _run_checker(argv, *, input, timeout):
    """The record a persistent `argv` process writes for the case line `input`, as a completed
    process with that line as its output. `TimeoutExpired` or `OSError` when it gives no record;
    that process is then killed."""
    deadline = _deadline(timeout)
    key = tuple(argv)
    checker = None
    with _idle_lock:
        idle = _idle.get(key, [])
        while idle and checker is None:
            candidate = idle.pop()
            if candidate.usable():
                checker = candidate
            else:
                candidate.close()
    reused = checker is not None
    if checker is None:
        checker = _Checker(argv)
    try:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise subprocess.TimeoutExpired(argv, timeout)
        line = _answer(checker, input, remaining)
    except OSError:
        if not reused:
            raise
        # A reused process may have ended since its last answer: the case goes once to a new one.
        checker = _Checker(argv)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            checker.close()
            raise subprocess.TimeoutExpired(argv, timeout)
        line = _answer(checker, input, remaining)
    except subprocess.TimeoutExpired:
        checker.close()
        raise
    completed = subprocess.CompletedProcess(list(argv), 0, line + b"\n", b"")
    # The caller owns this process until the response is decoded and bound to its case.
    completed._checker = checker
    completed._key = key
    return completed


def _release(completed, *, valid: bool) -> None:
    """Only a fully validated record can put its producer back in the idle pool."""
    checker = getattr(completed, "_checker", None)
    if checker is None:  # A synthetic CompletedProcess supplied by a test.
        return
    if valid:
        with _idle_lock:
            _idle.setdefault(completed._key, []).append(checker)
    else:
        checker.close()


def soft_case(env) -> dict:
    """The case field carrying a validated soft document's Background slot,
    followed by a correlated rights document's.

    Soft and rights premises are not environment data (Python keeps them on the
    extended environment); Rust validates every model against them as Python
    does.
    """
    premises = (*getattr(env, "soft_premises", ()), *getattr(env, "rights_premises", ()))
    if not premises:
        return {}
    from ..ast import _to_data
    return {"soft_premises": [_to_data(formula) for _, formula in premises]}


def rust_environment(env) -> dict:
    """The environment of a Rust evaluation or search case: without the
    `speech-acts@0` scope and the `rights@0` block, which declare no vocabulary
    and constrain no model (their Lean routes check them). Rust answers carry
    no environment identity; witnesses are validated over `env` itself."""
    data = env.to_dict()
    if "speech-acts@0" in env.profiles:
        data = {**{key: value for key, value in data.items() if key != "speech_acts"},
                "profiles": [p for p in data["profiles"] if p != "speech-acts@0"]}
    if "rights@0" in env.profiles:
        data = {**data, "vocabulary": {key: value for key, value in data["vocabulary"].items()
                                       if key != "rights"},
                "profiles": [p for p in data["profiles"] if p != "rights@0"]}
    return data


def cached_rust_environment(env) -> dict:
    return encoded_environment(env, "rust", lambda: rust_environment(env))


def run(case: dict, *, executable: str | os.PathLike | None = None,
        timeout: float | None = None, expected_sha256: str | None = None) -> dict:
    """Run one case and return its checked record, or a classified error.

    The case goes to a persistent checker process (`_run_checker`); a process that gives no
    record is killed. A selected Rust backend never falls back to Python. Without a
    `timeout`, the call waits `configured_timeout()` seconds.
    """
    [case] = wire_checked([case])
    if timeout is None:
        timeout = configured_timeout()
    binary = Path(executable or os.environ.get("VE_RUST_JSONL") or DEFAULT_EXECUTABLE)
    if not binary.is_file():
        raise CheckerUnavailable(f"CheckerUnavailable: missing Rust executable {binary}")
    try:
        allowed = ([expected_sha256] if expected_sha256 is not None else
                   [os.environ["VE_RUST_SHA256"]] if "VE_RUST_SHA256" in os.environ else
                   json.loads(BUILD_LOCK.read_text())["rust_jsonl"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: invalid Rust build lock: {exc}") from None
    digest = executable_sha256(binary)
    if digest not in allowed:
        raise CheckerUnavailable(f"CheckerUnavailable: Rust executable hash mismatch: {binary} "
                                 "(build it with python3 tools/rust_build.py)")
    environment = case.get("environment") if type(case) is dict else None
    if isinstance(environment, EncodedEnvironment):
        rest = {key: value for key, value in case.items() if key != "environment"}
        prefix = json.dumps(rest, ensure_ascii=False, separators=(",", ":"))
        encoded = prefix[:-1] + ',"environment":' + environment.text + "}"
    else:
        encoded = json.dumps(case, ensure_ascii=False, separators=(",", ":"))
    data = encoded.encode() + b"\n"
    if len(data) > MAX_LINE_BYTES:
        raise ResourceLimit(f"Rust case exceeds {MAX_LINE_BYTES} bytes")
    try:
        completed = _run_checker([str(binary), "jsonl", "-"], input=data, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: Rust checker failed: {exc}") from None
    valid = False
    try:
        if len(completed.stdout) > MAX_LINE_BYTES:
            raise CheckerUnavailable("CheckerUnavailable: oversized Rust JSONL response")
        lines = completed.stdout.splitlines()
        if completed.returncode not in (0, 1) or len(lines) != 1:
            detail = completed.stderr[:200].decode("utf-8", "replace")
            raise CheckerUnavailable(
                f"CheckerUnavailable: Rust protocol failure (exit {completed.returncode}; {detail})")
        try:
            record = _decode_json(lines[0])
        except (ValueError, RecursionError):
            raise CheckerUnavailable("CheckerUnavailable: malformed Rust JSONL response") from None
        problem = record_problem(case, record)
        if problem:
            raise CheckerUnavailable(f"CheckerUnavailable: malformed Rust response ({problem})")
        valid = True
    finally:
        _release(completed, valid=valid)
    return require_ok(record)


def record_problem(case: dict, record) -> str | None:
    """Why `record` is not one `ve jsonl` writes for `case`, or None: the schema
    `rust_schema/jsonl.json` (the record's identity, its fields and their types, and
    a rejection's complete diagnostic), then the counters the case bounds."""
    try:
        _RECORD[0](record, Context(case), {})
    except Invalid as exc:
        return str(exc)
    except RecursionError:
        return "nesting exceeds the reader's depth"
    if record["status"] == "error":
        return None
    for name, bound in (("evaluations", "max_evaluations"), ("models_checked", "max_models")):
        if name in record and type(case.get(bound)) is int and record[name] > case[bound]:
            return f"{name} exceeds the case's {bound}"
    if "premise_values" in record and len(record["premise_values"]) > len(case["premises"]):
        return "more premise values than premises"
    return None


_RECORD = Compiler(SCHEMA).ref("jsonl.json", "#/record")
