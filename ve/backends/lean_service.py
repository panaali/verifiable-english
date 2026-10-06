"""Supervisor and client for the persistent Lean service `ve_service`.

Stage 1 of docs/spec/SEMANTICS-MIGRATION-PLAN.md. The service speaks JSON lines: a
handshake line, then one response line per request line. A request is one batch of
cases for one mode, and each result is exactly what the one-shot runner for that mode
prints for the case (`lean/VE/Service/Protocol.lean`). `relay.py` is its one caller in `ve`;
since lean-first batch 1 every statement-layer route is a mode of this service.

Failure classes:

* A deterministic rejection of a whole request by the service (its budget, a batch the
  restricted decoder rejects) raises the exception of the service's `code` with its text
  (`relay.rejection`); the process stays up. Such a request error is bound
  like a response, to the nonce, the mode and every case digest; one without that
  binding is operational.
* Anything operational (wall-clock timeout, crash, end of output, garbage, a response
  whose id is not the request's nonce or that the response schemas reject, a handshake
  from an unexpected build) kills the process. The batch is retried once on a fresh process, since requests are stateless;
  a second failure raises `CheckerUnavailable`, which is never a verdict and never
  `ResourceLimit`. There is no fallback to Python.

Threat model (docs/spec/lean-service.md): the Lean service is the semantic authority,
covered by Lean proofs and parity tests; this client does not re-derive semantic
content. It guarantees binding and integrity: every response line, request errors
included, must echo the request nonce and mode, a request error every case digest, and
result `i` must carry position `i`, the SHA-256 of the text
of case `i` as sent (`case_digests`) and the identity fields the runners echo from the
case, so an omitted, reordered, duplicated or substituted result is rejected by binding.
Every field must also be well formed (`lean_service_schema/`, compiled by
`service_schema.py`). Content that preserves binding, such as the targets inside one
norms result, is the service's responsibility and is not checked here.

Supervision: an address-space limit on the process, a deadline per request, recycling
after a number of requests or above an RSS threshold, and a small pool.

Environment handles (docs/LEAN-FIRST-PLAN.md, F2, batch 2). A case whose `environment` is a JSON
object is sent naming it by `environment_handle`, the SHA-256 of its compact text, and the request
registers each environment the process does not hold yet (`environments`); the service answers it
as the case with that environment (`VE.Service.Handles`). The client keeps the same table as the
service (`_note` mirrors `Handles.insert`) and forgets it with the process. A request with handles
that the service answers with a request error, a handle it no longer holds among them, is sent
again with its environments in its cases, as before batch 2, and that answer is the answer: a
handle never changes an answer, it only saves sending and decoding the environment again. Response
checks read each case with its environment, as sent before.

Deadlines (docs/LEAN-FIRST-PLAN.md, F4). A request's deadline is its operation's
(`DEADLINES`): CPU seconds of the service process, a base per case plus a share per MiB of cases,
measured where the platform reports a process's CPU time (`/proc`) and otherwise read as
wall-clock seconds. Load on the host therefore does not stop a request; a request that needs
more CPU than its deadline is `CheckerUnavailable` naming its mode, and is not retried, since
the same request needs the same work. A request that is given a `timeout` has that wall-clock
limit instead, as before. Every request also has a wall-clock cap, `WALL_FACTOR` times its CPU
deadline, for a process that stops being scheduled.

The wall-clock guards are not work limits: `VE_LEAN_SERVICE_TIMEOUT` replaces the wall-clock
cap of a request without a `timeout` (and, where the CPU time is not reported, its deadline),
and `VE_LEAN_SERVICE_STARTUP_TIMEOUT` the 30 s a process has to start; the test suite raises
both to its hang guard, so machine load cannot fail a test.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from decimal import Decimal
import math
import os
from pathlib import Path
import queue
import re
import secrets
import selectors
import subprocess
import tempfile
import threading
import time

from ..errors import CheckerUnavailable, ResourceLimit, VEError
from .service_schema import MODES, Invalid, check_handshake, check_response

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXECUTABLE = ROOT / "lean/.lake/build/bin/ve_service"
BUILD_LOCK = ROOT / "lean/checkers.lock"
MAX_LINE_BYTES = 16 * 1024 * 1024
MAX_CASES = 4096
BATCH_CASES = 256
BATCH_BYTES = 4 * 1024 * 1024
STARTUP_TIMEOUT = 30.0
ADDRESS_SPACE = 4 << 30
MAX_RSS = 2 << 30
MAX_REQUESTS = 10_000
MAX_RESPONSE_BYTES = 1 << 30
# Room for the request envelope around the cases text within one line.
ENVELOPE_BYTES = 1024
# The handle table's case member and bounds are the service's: its handshake states them
# (`handles`: `VE.Service.handleKey`, `maxHandles`, `maxHandleBytes`), the response schema pins them
# (`envelope.json`, rendered from the Lean shapes) and the client reads them from there.
_HANDLES = json.loads((Path(__file__).resolve().parent / "lean_service_schema/envelope.json").read_text())[
    "handshake"]["properties"]["handles"]["properties"]
HANDLE_KEY = _HANDLES["member"]["const"]
MAX_HANDLES = _HANDLES["max"]["const"]
MAX_HANDLE_BYTES = _HANDLES["max_bytes"]["const"]
# The modes whose cases the service never expands (`expandCases`).
UNHANDLED_MODES = frozenset({"english", "risk-eval"})


# CPU seconds by mode: (base per case, per MiB of cases); each case is one operation. The core modes
# kept a flat 5 s per request before; their measured CPU is 0.5–1.6 ms per case at the median and
# about 0.8 ms per KiB of environment re-sent with each case (LEAN-FIRST-PLAN 3.3, 3.4), so 5 s per
# case plus 30 s per MiB is far above any measured request. The statement-layer routes keep their one-shot
# callers' limits as the base (120 s, reports and quantity 60 s, alternatives and risk 180 s,
# discourse 300 s) with a share per MiB above their measured CPU: about 1.3 s per MiB for soft
# norms, 100 s per MiB for the rights chain (2.2–2.9 s per 28 KiB document). The readings
# route's share is the exception: the UDHR document needs about 2,300 s per MiB (3.5), and
# its deadline (120 s plus 240 s per MiB) keeps it unavailable until F5 is built.
_CORE = (5.0, 30.0)
DEADLINES: dict[str, tuple[float, float]] = {
    **{mode: _CORE for mode in ("evaluate", "check-certificate", "order", "route", "norms", "english",
                                "environment", "model", "check", "identity", "parse", "graph", "readings",
                                "bundle", "family-norms")},
    "soft-norms": (120.0, 120.0), "rights": (120.0, 1000.0), "speech-acts": (120.0, 120.0),
    "reports": (60.0, 60.0), "alternatives": (180.0, 180.0), "risk": (180.0, 180.0),
    "risk-eval": (60.0, 60.0), "quantity": (60.0, 60.0), "norm-defaults": (120.0, 120.0),
    "discourse": (300.0, 300.0), "readings-route": (120.0, 240.0), "diagnose": (120.0, 120.0),
}
WALL_FACTOR = 10.0
_MIB = 1 << 20


def deadline(mode: str, size: int, cases: int = 1) -> float:
    """CPU seconds a request of `mode` with `cases` cases in `size` bytes may use (`DEADLINES`)."""
    base, per_mib = DEADLINES[mode]
    return base * max(cases, 1) + per_mib * size / _MIB


def _cpu_seconds(pid: int) -> float | None:
    """CPU time (user and system) of process `pid`, or None where /proc does not report it."""
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:
            fields = f.read().rsplit(b")", 1)[1].split()
    except (OSError, IndexError):
        return None
    # Fields 14 and 15 (utime, stime) are the 12th and 13th after the command name.
    return (int(fields[11]) + int(fields[12])) / os.sysconf("SC_CLK_TCK")


class _Failure(Exception):
    """An operational failure of one process; the supervisor restarts it."""


class _Deadline:
    """When a request must be answered: by `wall` (monotonic), and, if `cpu` is set, before
    the process has used `cpu` more seconds of CPU than `start` (its CPU time at the request)."""
    __slots__ = ("wall", "cpu", "start", "mode")

    def __init__(self, wall: float, cpu: float | None = None, start: float | None = None, mode: str = ""):
        self.wall, self.cpu, self.start, self.mode = wall, cpu, start, mode


def configured_seconds(variable: str, default: float) -> float:
    """The wall-clock timeout the environment variable `variable` sets, else `default`.

    Only a guard against a hung checker: the semantic work limits are the
    backends' own budgets and do not depend on it. A value that is not a positive
    finite number of seconds is refused, never replaced by the default."""
    text = os.environ.get(variable)
    if text is None:
        return default
    try:
        seconds = float(text)
    except ValueError:
        seconds = math.nan
    if not (math.isfinite(seconds) and seconds > 0):
        raise CheckerUnavailable(f"CheckerUnavailable: {variable} must be a positive number of seconds, "
                                 f"not {text!r}")
    return seconds


def _decode_json(line: bytes | str) -> object:
    """A checker's JSON output (this service, the one-shot Lean runners, the Rust JSONL checker):
    bytes that are not UTF-8, duplicate fields, non-finite constants and strings that are not
    Unicode text (a `\\ud800` escape decodes to a lone surrogate, which no Lean or Rust string
    holds) and numbers no float holds (`_json_float`) raise ValueError, and so does nesting beyond
    Python's recursion limit (otherwise a RecursionError): every way the bytes are no answer is a
    ValueError. Bytes are decoded as strict UTF-8 here; json.loads alone would guess UTF-16 or UTF-32."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON field {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f"invalid JSON number {value}")

    text = line.decode("utf-8") if isinstance(line, (bytes, bytearray)) else line
    try:
        value = json.loads(text, object_pairs_hook=unique, parse_constant=invalid_constant,
                           parse_int=_json_integer, parse_float=_json_float)
    except RecursionError:
        raise ValueError("JSON nesting exceeds the runtime limit") from None
    pending = [value]
    while pending:
        item = pending.pop()
        if type(item) is str:
            item.encode("utf-8")  # UnicodeEncodeError, a ValueError, on a lone surrogate
        elif type(item) is list:
            pending.extend(item)
        elif type(item) is dict:
            pending.extend(item)
            pending.extend(item.values())
    return value


def _json_integer(digits: str) -> int | Decimal:
    """Accept Lean's unbounded JSON integers without changing small wire integers."""
    try:
        return int(digits)
    except ValueError:
        # Python's decimal-digit guard is an implementation limit, not a JSON or
        # Lean limit. Decimal preserves the value without disabling that guard.
        return Decimal(digits)


def _json_float(text: str) -> float:
    """A JSON number with a fraction or exponent, as its nearest float. `json` reads an
    exponent beyond the float range as infinity (`1e999`) or zero (`1e-999`) without calling
    `parse_constant`: such a number is ValueError, never a value it is not."""
    value = float(text)
    if not math.isfinite(value) or (value == 0 and re.split("[eE]", text)[0].strip("-+0.")):
        raise ValueError(f"JSON number {text} is outside the float range")
    return value


_JSON_WHITESPACE = " \t\r\n"
_DELIMITERS = re.compile(r'[\[\]{}",\\]')


def case_texts(cases_text: str) -> list[str] | None:
    """The case texts of a JSON array text, split and trimmed as the service splits them
    (`VE.JsonInput.caseTexts`, then `String.trim`); `None` if it is not an array."""
    text = cases_text.strip(_JSON_WHITESPACE)
    if not (text.startswith("[") and text.endswith("]")):
        return None
    body = text[1:-1]
    if not body.strip(_JSON_WHITESPACE):
        return []
    cases, start, depth, quoted, escaped_at = [], 0, 0, False, -1
    for match in _DELIMITERS.finditer(body):  # every other character leaves the state unchanged
        i, c = match.start(), match.group()
        if quoted:
            if escaped_at == i - 1:
                escaped_at = -1
            elif c == "\\":
                escaped_at = i
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c in "[{":
            depth += 1
        elif c in "]}":
            if depth == 0:
                return None
            depth -= 1
        elif c == "," and depth == 0:
            cases.append(body[start:i].strip(_JSON_WHITESPACE))
            start = i + 1
    if quoted or depth:
        return None
    cases.append(body[start:].strip(_JSON_WHITESPACE))
    return cases


def case_digest(text: str) -> str:
    """The binding identity of a case (`VE.Service.caseDigest`): SHA-256 of its text."""
    return hashlib.sha256(text.encode()).hexdigest()


def request_context(nonce: str, mode: str, cases_text: str, count: int,
                    texts: list[str] | None = None, cases: list | None = None) -> dict:
    """What a response to the request is checked against (`lean_service_schema/envelope.json`):
    `{"id", "mode", "cases", "digests", "bytes"}`. A request error is bound to the digests
    of the case texts as split, whether or not they decode (`null` if the text does not
    split); results also need the decoded cases, one per case (`null` otherwise, so that
    only a request error can answer the request). `cases`, when given, are the decoded cases
    with each handle replaced by its environment (`_Sent.expanded`)."""
    if cases is None:
        try:
            cases = json.loads(cases_text, parse_int=_json_integer)
        except (ValueError, RecursionError):
            cases = None
    if texts is None:
        texts = case_texts(cases_text)
    digests = None if texts is None else [case_digest(text) for text in texts]
    if not isinstance(cases, list) or len(cases) != count or digests is None or len(digests) != count:
        cases = None
    return {"id": nonce, "mode": mode, "cases": cases, "digests": digests,
            "bytes": len(cases_text.strip().encode())}


_hashes: dict[tuple, str] = {}


_HEX64 = re.compile(r"[0-9a-f]{64}")


def executable_sha256(path: Path) -> str:
    """SHA-256 of the executable file, cached while its filesystem identity (device, inode, size,
    modification and change times) is unchanged: in this process, and across processes in the sidecar
    `<executable>.sha256-cache` (docs/LEAN-FIRST-PLAN.md section 4: hashing the 180 MiB service binary cost
    every CLI process about 0.2 s of CPU). Any write to the executable changes its change time, so a
    replaced or edited binary is hashed again; a sidecar that cannot be read or written is ignored."""
    st = path.stat()
    key = (str(path), st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
    if key not in _hashes:
        sidecar = path.with_name(path.name + ".sha256-cache")
        try:
            cached = json.loads(sidecar.read_text())
        except (OSError, ValueError):
            cached = None
        if (type(cached) is dict and cached.get("key") == list(key) and type(cached.get("sha256")) is str
                and _HEX64.fullmatch(cached["sha256"])):
            _hashes[key] = cached["sha256"]
        else:
            digest = hashlib.sha256()
            with path.open("rb") as f:
                for block in iter(lambda: f.read(1 << 20), b""):
                    digest.update(block)
            _hashes[key] = digest.hexdigest()
            written = None
            try:
                with tempfile.NamedTemporaryFile("w", dir=sidecar.parent, prefix=sidecar.name,
                                                 delete=False) as out:
                    written = out.name
                    json.dump({"key": list(key), "sha256": _hashes[key]}, out)
                os.replace(written, sidecar)
            except OSError:
                if written is not None:
                    Path(written).unlink(missing_ok=True)
    return _hashes[key]


def _rss_bytes(pid: int) -> int | None:
    try:
        with open(f"/proc/{pid}/status", encoding="ascii") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
    except OSError:
        return None
    return None


class LeanService:
    """One supervised `ve_service` process. Thread-safe; one batch in flight at a time."""

    def __init__(self, executable: str | os.PathLike | None = None, *,
                 timeout: float | None = None, startup_timeout: float | None = None,
                 address_space: int | None = ADDRESS_SPACE, max_requests: int = MAX_REQUESTS,
                 max_rss: int | None = MAX_RSS, expected_sha256: str | None = None,
                 allow_unlisted_build: bool = False,
                 batch_cases: int = BATCH_CASES, batch_bytes: int = BATCH_BYTES, retries: int = 1,
                 handles: bool = True):
        self.executable = Path(executable or os.environ.get("VE_LEAN_SERVICE") or DEFAULT_EXECUTABLE)
        # None: the configured default, read at each use (the shared pool outlives a setting).
        self.timeout, self.startup_timeout = timeout, startup_timeout
        self.address_space, self.max_requests, self.max_rss = address_space, max_requests, max_rss
        self.expected_sha256 = expected_sha256
        self.allow_unlisted_build = allow_unlisted_build
        self.batch_cases, self.batch_bytes = min(batch_cases, MAX_CASES), batch_bytes
        self.retries = retries
        self.handles = handles
        # The handles the current process holds, in registration order, with their sizes.
        self._registered: dict[str, int] = {}
        self._handle_bytes = 0
        self.handshake: dict | None = None
        self.stats = {"starts": 0, "restarts": 0, "recycles": 0, "requests": 0, "retries": 0,
                      "registered": 0, "handle_resends": 0}
        self._proc: subprocess.Popen | None = None
        self._stderr = None
        self._buffer = bytearray()
        self._served = 0
        self._recycle = False
        self._lock = threading.Lock()
        self._nonce = secrets.token_hex(6)
        self._counter = itertools.count()

    # Lifecycle

    @property
    def build(self) -> str:
        """SHA-256 of the executable (the handshake build identity)."""
        return executable_sha256(self.executable)

    @property
    def pid(self) -> int | None:
        return self._proc.pid if self._proc is not None else None

    def start(self) -> dict:
        with self._lock:
            attempt = 0
            while True:
                try:
                    self._ensure()
                    break
                except _Failure as failure:
                    self._failed_attempt(failure, attempt)
                    attempt += 1
            return self.handshake

    def close(self) -> None:
        with self._lock:
            self._stop(graceful=True)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.close()

    def rss(self) -> int | None:
        return _rss_bytes(self._proc.pid) if self._proc is not None else None

    def _ensure(self) -> None:
        if self._proc is not None and (self._recycle or self._proc.poll() is not None):
            if self._recycle:
                self.stats["recycles"] += 1
            else:  # died since the last request
                self.stats["restarts"] += 1
            self._stop(graceful=self._recycle)
        if self._proc is None:
            self._spawn()

    def _spawn(self) -> None:
        try:
            if not self.executable.exists():
                raise CheckerUnavailable(f"CheckerUnavailable: missing Lean service executable {self.executable}")
            if self.expected_sha256 is not None:
                allowed = {self.expected_sha256}
            elif self.allow_unlisted_build:
                allowed = None
            else:
                try:
                    allowed = set(json.loads(BUILD_LOCK.read_text())["ve_service"])
                except (OSError, ValueError, KeyError, TypeError):
                    raise CheckerUnavailable(f"CheckerUnavailable: invalid build lock {BUILD_LOCK}") from None
            build = self.build
            if allowed is not None and build not in allowed:
                raise CheckerUnavailable(f"CheckerUnavailable: {self.executable} has unlisted build {build}, "
                                         f"expected {', '.join(sorted(allowed))}")
            startup = (self.startup_timeout if self.startup_timeout is not None else
                       configured_seconds("VE_LEAN_SERVICE_STARTUP_TIMEOUT", STARTUP_TIMEOUT))
            if self._stderr is not None:
                self._stderr.close()
            self._stderr = tempfile.TemporaryFile()
            limit = self.address_space
            preexec = None
            if limit is not None and not hasattr(__import__("resource"), "prlimit"):
                def preexec():
                    import resource
                    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
            self._proc = subprocess.Popen([str(self.executable)], stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE, stderr=self._stderr,
                                          bufsize=0, close_fds=True, preexec_fn=preexec)
            if limit is not None and preexec is None:
                import resource
                resource.prlimit(self._proc.pid, resource.RLIMIT_AS, (limit, limit))
            os.set_blocking(self._proc.stdout.fileno(), False)
            os.set_blocking(self._proc.stdin.fileno(), False)
            self._buffer.clear()
            self._served, self._recycle = 0, False
            self._forget_handles()
            self.stats["starts"] += 1
            line = self._read_line(_Deadline(time.monotonic() + startup))
            handshake = _decode_json(line)
            try:
                check_handshake(handshake)
            except Invalid as exc:
                raise _Failure(f"unexpected handshake ({exc}) {line[:200]!r}") from None
        except CheckerUnavailable:
            self._stop(graceful=False)
            raise
        except (_Failure, OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
            self._stop(graceful=False)
            raise _Failure(f"startup/handshake from {self.executable}: {exc}") from None
        self.handshake = handshake

    def _stop(self, graceful: bool) -> None:
        proc, self._proc = self._proc, None
        self.handshake = None
        try:
            if proc is not None:
                if graceful and proc.poll() is None:
                    try:
                        proc.stdin.close()
                        proc.wait(timeout=2)
                    except (OSError, subprocess.TimeoutExpired):
                        pass
                if proc.poll() is None:
                    proc.kill()
                proc.wait(timeout=10)
        finally:
            if proc is not None:
                for stream in (proc.stdin, proc.stdout):
                    try:
                        stream.close()
                    except OSError:
                        pass
            if self._stderr is not None:
                self._stderr.close()
                self._stderr = None
            self._buffer.clear()

    def cpu_seconds(self) -> float | None:
        """CPU time the current process has used, where the platform reports it."""
        return None if self._proc is None else _cpu_seconds(self._proc.pid)

    def stderr(self, start: int = 0) -> tuple[int, str]:
        """The current process's standard error from byte `start` on, and its length: what a
        one-shot runner would have printed there (Lean's `PANIC` messages, for example)."""
        if self._stderr is None:
            return 0, ""
        try:
            self._stderr.seek(0, os.SEEK_END)
            size = self._stderr.tell()
            self._stderr.seek(min(start, size))
            return size, self._stderr.read().decode(errors="replace")
        except (OSError, ValueError):
            return 0, ""

    def _stderr_tail(self) -> str:
        if self._stderr is None:
            return ""
        try:
            self._stderr.seek(0, os.SEEK_END)
            size = self._stderr.tell()
            self._stderr.seek(max(0, size - 500))
            return self._stderr.read().decode(errors="replace").strip()
        except (OSError, ValueError):
            return ""

    # Framing

    def _wait(self, deadline: _Deadline, what: str) -> float:
        """Seconds to wait before `deadline` is checked again; raises once it has passed. A CPU
        deadline is checked at least as often as the process could have used up what is left of
        it (it runs one thread)."""
        remaining = deadline.wall - time.monotonic()
        if remaining <= 0:
            raise _Failure(f"timeout {what}" + (f" (mode {deadline.mode})" if deadline.mode else ""))
        if deadline.cpu is None:
            return remaining
        used = _cpu_seconds(self._proc.pid)
        if used is not None and used - deadline.start > deadline.cpu:
            self._stop(graceful=False)
            raise CheckerUnavailable(
                f"CheckerUnavailable: the Lean service mode {deadline.mode} used more than its deadline "
                f"of {deadline.cpu:.6g} s of CPU", operation=deadline.mode, backend="lean")
        left = deadline.cpu if used is None else deadline.cpu - (used - deadline.start)
        return min(remaining, max(left, 0.01))

    def _write_all(self, data: bytes, deadline: _Deadline) -> None:
        fd = self._proc.stdin.fileno()
        view = memoryview(data)
        with selectors.DefaultSelector() as sel:
            sel.register(fd, selectors.EVENT_WRITE)
            while view:
                if not sel.select(self._wait(deadline, "writing the request")):
                    continue
                try:
                    written = os.write(fd, view)
                except BlockingIOError:
                    continue
                except (BrokenPipeError, OSError) as exc:
                    raise _Failure(f"service input closed: {exc}") from None
                view = view[written:]

    def _read_line(self, deadline: _Deadline) -> bytes:
        fd = self._proc.stdout.fileno()
        with selectors.DefaultSelector() as sel:
            sel.register(fd, selectors.EVENT_READ)
            while True:
                end = self._buffer.find(b"\n")
                if end >= 0:
                    line = bytes(self._buffer[:end])
                    del self._buffer[:end + 1]
                    return line
                if len(self._buffer) > MAX_RESPONSE_BYTES:
                    raise _Failure("response line exceeds the size limit")
                if not sel.select(self._wait(deadline, "waiting for the response")):
                    continue
                try:
                    chunk = os.read(fd, 1 << 20)
                except BlockingIOError:
                    continue
                if not chunk:
                    raise _Failure("service exited (end of output)")
                self._buffer += chunk

    @staticmethod
    def _request_line(nonce: str, mode: str, cases_text: str, budget: dict,
                      environments: dict[str, str] | None = None) -> bytes:
        registered = ("" if not environments else ',"environments":{' + ",".join(
            json.dumps(digest) + ":" + text for digest, text in environments.items()) + "}")
        return ('{"id":' + json.dumps(nonce) + ',"mode":' + json.dumps(mode) + ',"budget":'
                + json.dumps(budget, separators=(",", ":")) + registered + ',"cases":' + cases_text
                + "}\n").encode()

    # Handles

    def _forget_handles(self) -> None:
        self._registered.clear()
        self._handle_bytes = 0

    def _note(self, digest: str, size: int) -> None:
        """Record that the process registered `digest` (`VE.Service.Handles.insert`)."""
        if digest in self._registered:
            return
        if len(self._registered) + 1 > MAX_HANDLES or self._handle_bytes + size > MAX_HANDLE_BYTES:
            self._forget_handles()
        self._registered[digest] = size
        self._handle_bytes += size

    def _deadline(self, mode: str, size: int, cases: int, timeout: float | None) -> _Deadline:
        """The request's deadline: `timeout` wall-clock seconds when given, else its mode's
        CPU deadline (`deadline`) with the wall-clock cap; wall-clock alone where the CPU time
        of the process is not reported."""
        now = time.monotonic()
        if timeout is not None:
            return _Deadline(now + timeout, mode=mode)
        cpu = deadline(mode, size, cases)
        start = _cpu_seconds(self._proc.pid)
        if start is None:
            return _Deadline(now + configured_seconds("VE_LEAN_SERVICE_TIMEOUT", cpu), mode=mode)
        cap = configured_seconds("VE_LEAN_SERVICE_TIMEOUT", WALL_FACTOR * cpu)
        return _Deadline(now + cap, cpu, start, mode)

    def _roundtrip(self, mode: str, cases_text: str, count: int, timeout: float | None,
                   nonce: str, line: bytes, texts: list[str] | None,
                   expanded: list | None = None) -> tuple[bytes, dict]:
        deadline = self._deadline(mode, len(cases_text.encode()), count, timeout)
        self._write_all(line, deadline)
        raw = self._read_line(deadline)
        try:
            response = _decode_json(raw)
        except (ValueError, RecursionError):
            raise _Failure(f"malformed response {raw[:200]!r}") from None
        if not isinstance(response, dict) or response.get("id") != nonce:
            if isinstance(response, dict) and response.get("id") is None and response.get("status") == "error":
                # A line the service could not read at all: framing is lost.
                raise _Failure(f"service could not read the request: {response.get('error')}")
            raise _Failure(f"response id does not match the request nonce: {raw[:200]!r}")
        try:
            check_response(mode, response, request_context(nonce, mode, cases_text, count, texts, expanded))
        except Invalid as exc:
            raise _Failure(f"malformed response ({exc}): {raw[:200]!r}") from None
        return raw, response

    def _after_request(self) -> None:
        self._served += 1
        self.stats["requests"] += 1
        if self._served >= self.max_requests:
            self._recycle = True
        elif self.max_rss is not None:
            rss = self.rss()
            if rss is not None and rss > self.max_rss:
                self._recycle = True

    def exchange(self, mode: str, cases_text: str, count: int, *, timeout: float | None = None,
                 budget: dict | None = None, texts: list[str] | None = None,
                 environments: dict[str, str] | None = None, expanded: list | None = None
                 ) -> tuple[bytes, dict]:
        """Send one request whose `cases` is `cases_text` (a JSON array of `count` cases).
        `texts`, when the caller has them, are the case texts `cases_text` joins without
        whitespace (`case_texts(cases_text)`, which is then not recomputed). `environments` are
        the texts of the handles the cases name, by digest: those the process does not hold are
        registered with the request; `expanded` are then the cases with their environments, which
        the response is checked against. A request error clears the client's handle table.

        Returns the raw response line and its decoding, whose results are still bound
        (`{"digest", "index", "result"}`). A request error from the service, bound to the
        nonce, mode and case digests, is returned as is (`status: error`); operational
        failures, unbound errors included, are retried once, then raise `CheckerUnavailable`.
        """
        if mode not in MODES:
            raise VEError(f"unknown Lean service mode {mode!r}")
        timeout = self.timeout if timeout is None else timeout
        if timeout is None:
            # The wall-clock cap's setting is refused before any process starts when it is not seconds.
            configured_seconds("VE_LEAN_SERVICE_TIMEOUT", WALL_FACTOR)
        if budget is None:
            budget = {"cases": max(count, 1), "bytes": len(cases_text.encode())}
        with self._lock:
            attempt = 0
            while True:
                nonce = f"{self._nonce}-{next(self._counter)}"
                needed: dict[str, str] = {}
                if not environments:
                    line = self._request_line(nonce, mode, cases_text, budget)
                    if len(line) > MAX_LINE_BYTES + 1:
                        raise ResourceLimit(f"ResourceLimit: request line exceeds {MAX_LINE_BYTES} bytes")
                try:
                    self._ensure()
                    if environments:
                        # Which environments to register depends on the process, known only now.
                        needed = {digest: text for digest, text in environments.items()
                                  if digest not in self._registered}
                        line = self._request_line(nonce, mode, cases_text, budget, needed)
                        if len(line) > MAX_LINE_BYTES + 1:
                            raise ResourceLimit(f"ResourceLimit: request line exceeds {MAX_LINE_BYTES} bytes")
                    raw, response = self._roundtrip(mode, cases_text, count, timeout, nonce, line, texts,
                                                    expanded)
                except _Failure as failure:
                    self._failed_attempt(failure, attempt)
                    attempt += 1
                    continue
                if response.get("status") == "error":
                    self._forget_handles()
                else:
                    for digest, text in needed.items():
                        self._note(digest, len(text.encode()))
                        self.stats["registered"] += 1
                self._after_request()
                return raw, response

    def _failed_attempt(self, failure: _Failure, attempt: int) -> None:
        detail = self._stderr_tail()
        self._stop(graceful=False)
        self.stats["restarts"] += 1
        if attempt >= self.retries:
            raise CheckerUnavailable(
                f"CheckerUnavailable: {failure}" + (f"; stderr: {detail}" if detail else "")) from None
        self.stats["retries"] += 1

    def _chunks(self, sent: list, parts: int = 1):
        """Requests of at most `batch_cases` cases and `batch_bytes`, and at least `parts`
        requests when there are that many cases (so a pool can answer them in parallel).
        `sent` are case texts or `_Sent` cases, measured by the text sent."""
        # `size` is the byte length of "[" + ",".join(chunk) + "]".
        limit = min(self.batch_cases, max(1, -(-len(sent) // max(parts, 1))))
        chunk: list = []
        size = 1
        for item in sent:
            n = len((item.text if isinstance(item, _Sent) else item).encode())
            if n + 2 + ENVELOPE_BYTES > MAX_LINE_BYTES:
                raise ResourceLimit(f"ResourceLimit: case exceeds {MAX_LINE_BYTES} bytes")
            if chunk and (len(chunk) >= limit or size + n + 1 > self.batch_bytes):
                yield chunk
                chunk, size = [], 1
            chunk.append(item)
            size += n + 1
        if chunk:
            yield chunk

    def _request(self, mode: str, chunk: list[str], timeout: float | None, *,
                 environments: dict[str, str] | None = None, expanded: list | None = None) -> dict:
        cases_text = "[" + ",".join(chunk) + "]"
        size = len(cases_text.encode())
        budget = {"cases": self.batch_cases,
                  "bytes": self.batch_bytes if size <= self.batch_bytes else MAX_LINE_BYTES - ENVELOPE_BYTES}
        _, response = self.exchange(mode, cases_text, len(chunk), timeout=timeout, budget=budget, texts=chunk,
                                    environments=environments, expanded=expanded)
        return response

    def _run_chunk(self, mode: str, chunk: list, timeout: float | None) -> list:
        """The bound entries for one request's cases (texts or `_Sent` cases). Cases that name
        handles are sent so first; if the service answers that request with a request error,
        the cases are sent again with their environments, in requests of their own size."""
        if chunk and isinstance(chunk[0], _Sent):
            if any(item.digest for item in chunk):
                response = self._handle_request(mode, chunk, timeout)
                if response is not None:
                    return response["results"]
                with self._lock:
                    self.stats["handle_resends"] += 1
            entries: list = []
            for inline in self._chunks([item.inline() for item in chunk]):
                entries.extend(self._run_chunk(mode, inline, timeout))
            return entries
        response = self._request(mode, chunk, timeout)
        if response.get("status") == "error":
            from .relay import rejection  # relay.py builds on this client
            raise rejection(response["code"], response["error"])
        return response["results"]

    def _handle_request(self, mode: str, chunk: list, timeout: float | None) -> dict | None:
        """The service's answer to `chunk` sent with handles, or None when it is a request error
        or would not fit one line with every environment registered."""
        environments: dict[str, str] = {}
        for item in chunk:
            if item.digest:
                environments.setdefault(item.digest, item.environment)
        texts = [item.text for item in chunk]
        line = sum(len(t.encode()) + 1 for t in texts) + sum(
            len(d) + len(t.encode()) + 4 for d, t in environments.items()) + ENVELOPE_BYTES
        if line > MAX_LINE_BYTES:
            return None
        decoded = {digest: json.loads(text, parse_int=_json_integer) for digest, text in environments.items()}
        response = self._request(mode, texts, timeout, environments=environments,
                                 expanded=[item.expanded(decoded) for item in chunk])
        return None if response.get("status") == "error" else response

    def _sent(self, mode: str, cases: list) -> list:
        """`cases` as sent: with handles for their environments where this client uses them."""
        if not self.handles or mode in UNHANDLED_MODES:
            return _texts(cases)
        return _encode(cases)

    def run_bound(self, mode: str, cases: list, *, timeout: float | None = None) -> list:
        """The bound entries for `cases`, in order: each runner result with, beside a rejection,
        its `code` (and `generator`). Batches above the adapter caps (256 cases or 4 MiB) are
        split into several requests; each is one timeout unit."""
        entries: list = []
        for chunk in self._chunks(self._sent(mode, cases)):
            entries.extend(self._run_chunk(mode, chunk, timeout))
        return entries

    def run(self, mode: str, cases: list, *, timeout: float | None = None) -> list:
        """The runner results for `cases`, in order (`run_bound` without the bindings)."""
        return [entry["result"] for entry in self.run_bound(mode, cases, timeout=timeout)]


def _dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class _Sent:
    """A case as sent with a handle: its text, naming its environment by `digest`, and the
    environment's text. A case without a JSON-object environment has no digest and is sent as is."""
    __slots__ = ("case", "text", "digest", "environment")

    def __init__(self, case, text: str, digest: str | None = None, environment: str | None = None):
        self.case, self.text, self.digest, self.environment = case, text, digest, environment

    def inline(self) -> str:
        """The case's text with its environment, as sent before batch 2."""
        return self.text if self.digest is None else _dumps(self.case)

    def expanded(self, environments: dict) -> object:
        """The case as the service reads it: the decoded text, its handle replaced by the
        decoded environment (`VE.Service.Handles.expand`)."""
        case = json.loads(self.text, parse_int=_json_integer)
        if self.digest is not None:
            del case[HANDLE_KEY]
            case["environment"] = environments[self.digest]
        return case


def _encode(cases: list) -> list[_Sent]:
    """Each case as sent: a case object whose `environment` is an object, and which names no
    handle itself, names its environment by the SHA-256 of the environment's compact text. An
    environment object shared by several cases is encoded once."""
    texts: dict[int, tuple[str, str]] = {}
    sent = []
    for case in cases:
        environment = case.get("environment") if type(case) is dict and HANDLE_KEY not in case else None
        if type(environment) is not dict:
            sent.append(_Sent(case, _dumps(case)))
            continue
        if id(environment) not in texts:
            text = _dumps(environment)
            texts[id(environment)] = (text, case_digest(text))
        text, digest = texts[id(environment)]
        rest = {key: value for key, value in case.items() if key != "environment"}
        rest[HANDLE_KEY] = digest
        sent.append(_Sent(case, _dumps(rest), digest, text))
    return sent


def _texts(cases: list) -> list[str]:
    return [_dumps(case) for case in cases]


class LeanServicePool:
    """A small pool of supervised services (default 2, the IDE footprint in section 4).

    A batch is split into at least one request per process and its requests are answered
    in parallel by idle processes. Requests are stateless, so the results are those of
    `LeanService.run`; if requests fail, the failure of the earliest one is raised."""

    def __init__(self, size: int = 2, **options):
        self._services = [LeanService(**options) for _ in range(size)]
        self._idle: queue.LifoQueue = queue.LifoQueue()
        for service in self._services:
            self._idle.put(service)

    @property
    def services(self) -> tuple[LeanService, ...]:
        return tuple(self._services)

    def start(self) -> None:
        for service in self._services:
            service.start()

    def _on_idle(self, call):
        service = self._idle.get()
        try:
            return call(service)
        finally:
            self._idle.put(service)

    def run(self, mode: str, cases: list, *, timeout: float | None = None) -> list:
        return [entry["result"] for entry in self.run_bound(mode, cases, timeout=timeout)]

    def run_bound(self, mode: str, cases: list, *, timeout: float | None = None) -> list:
        chunks = list(self._services[0]._chunks(self._services[0]._sent(mode, cases), parts=len(self._services)))
        if len(chunks) <= 1:
            return self._on_idle(lambda service: service.run_bound(mode, cases, timeout=timeout))
        answers: list = [None] * len(chunks)
        pending = iter(range(len(chunks)))
        claim = threading.Lock()

        def worker():
            while True:
                with claim:
                    index = next(pending, None)
                if index is None:
                    return
                try:
                    answers[index] = (True, self._on_idle(
                        lambda service: service._run_chunk(mode, chunks[index], timeout)))
                except Exception as exc:  # noqa: BLE001  (re-raised below, in request order)
                    answers[index] = (False, exc)

        threads = [threading.Thread(target=worker, daemon=True)
                   for _ in range(min(len(self._services), len(chunks)))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        results: list = []
        for ok, value in answers:
            if not ok:
                raise value
            results.extend(value)
        return results

    def close(self) -> None:
        for service in self._services:
            service.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
