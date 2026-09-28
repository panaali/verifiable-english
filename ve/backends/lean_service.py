"""Supervisor and client for the persistent Lean service `ve_service`.

Stage 1 of docs/spec/SEMANTICS-MIGRATION-PLAN.md. The service speaks JSON lines: a
handshake line, then one response line per request line. A request is one batch of
cases for one mode, and each result is exactly what the one-shot runner for that mode
prints for the case (`lean/VE/Service/Protocol.lean`). Nothing in `ve` calls this
module yet: no Python semantics is switched.

Failure classes:

* A deterministic rejection of a whole request by the service (its budget, a batch the
  restricted decoder rejects) raises `ResourceLimit` or `VEError`, as the one-shot
  runners' exit-2 diagnostics would; the process stays up. Such a request error is bound
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

Supervision: an address-space limit on the process, a per-batch timeout (5 s
interactive, 60 s for batch callers), recycling after a number of requests or above
an RSS threshold, and a small pool.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from decimal import Decimal
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
INTERACTIVE_TIMEOUT = 5.0
BATCH_TIMEOUT = 60.0
STARTUP_TIMEOUT = 30.0
ADDRESS_SPACE = 4 << 30
MAX_RSS = 2 << 30
MAX_REQUESTS = 10_000
MAX_RESPONSE_BYTES = 1 << 30
# Room for the request envelope around the cases text within one line.
ENVELOPE_BYTES = 1024


class _Failure(Exception):
    """An operational failure of one process; the supervisor restarts it."""


def _decode_json(line: bytes) -> object:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON field {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f"invalid JSON number {value}")

    return json.loads(line, object_pairs_hook=unique, parse_constant=invalid_constant,
                      parse_int=_json_integer)


def _json_integer(digits: str) -> int | Decimal:
    """Accept Lean's unbounded JSON integers without changing small wire integers."""
    try:
        return int(digits)
    except ValueError:
        # Python's decimal-digit guard is an implementation limit, not a JSON or
        # Lean limit. Decimal preserves the value without disabling that guard.
        return Decimal(digits)


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
                    texts: list[str] | None = None) -> dict:
    """What a response to the request is checked against (`lean_service_schema/envelope.json`):
    `{"id", "mode", "cases", "digests", "bytes"}`. A request error is bound to the digests
    of the case texts as split, whether or not they decode (`null` if the text does not
    split); results also need the decoded cases, one per case (`null` otherwise, so that
    only a request error can answer the request)."""
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


def executable_sha256(path: Path) -> str:
    """SHA-256 of the executable file, cached while its filesystem identity is unchanged."""
    st = path.stat()
    key = (str(path), st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
    if key not in _hashes:
        digest = hashlib.sha256()
        with path.open("rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                digest.update(block)
        _hashes[key] = digest.hexdigest()
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
                 timeout: float = INTERACTIVE_TIMEOUT, startup_timeout: float = STARTUP_TIMEOUT,
                 address_space: int | None = ADDRESS_SPACE, max_requests: int = MAX_REQUESTS,
                 max_rss: int | None = MAX_RSS, expected_sha256: str | None = None,
                 allow_unlisted_build: bool = False,
                 batch_cases: int = BATCH_CASES, batch_bytes: int = BATCH_BYTES, retries: int = 1):
        self.executable = Path(executable or os.environ.get("VE_LEAN_SERVICE") or DEFAULT_EXECUTABLE)
        self.timeout, self.startup_timeout = timeout, startup_timeout
        self.address_space, self.max_requests, self.max_rss = address_space, max_requests, max_rss
        self.expected_sha256 = expected_sha256
        self.allow_unlisted_build = allow_unlisted_build
        self.batch_cases, self.batch_bytes = min(batch_cases, MAX_CASES), batch_bytes
        self.retries = retries
        self.handshake: dict | None = None
        self.stats = {"starts": 0, "restarts": 0, "recycles": 0, "requests": 0, "retries": 0}
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
            self.stats["starts"] += 1
            line = self._read_line(time.monotonic() + self.startup_timeout)
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

    def _write_all(self, data: bytes, deadline: float) -> None:
        fd = self._proc.stdin.fileno()
        view = memoryview(data)
        with selectors.DefaultSelector() as sel:
            sel.register(fd, selectors.EVENT_WRITE)
            while view:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise _Failure("timeout writing the request")
                if not sel.select(remaining):
                    continue
                try:
                    written = os.write(fd, view)
                except BlockingIOError:
                    continue
                except (BrokenPipeError, OSError) as exc:
                    raise _Failure(f"service input closed: {exc}") from None
                view = view[written:]

    def _read_line(self, deadline: float) -> bytes:
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
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise _Failure("timeout waiting for the response")
                if not sel.select(remaining):
                    continue
                try:
                    chunk = os.read(fd, 1 << 20)
                except BlockingIOError:
                    continue
                if not chunk:
                    raise _Failure("service exited (end of output)")
                self._buffer += chunk

    @staticmethod
    def _request_line(nonce: str, mode: str, cases_text: str, budget: dict) -> bytes:
        return ('{"id":' + json.dumps(nonce) + ',"mode":' + json.dumps(mode) + ',"budget":'
                + json.dumps(budget, separators=(",", ":")) + ',"cases":' + cases_text + "}\n").encode()

    def _roundtrip(self, mode: str, cases_text: str, count: int, timeout: float,
                   nonce: str, line: bytes, texts: list[str] | None) -> tuple[bytes, dict]:
        deadline = time.monotonic() + timeout
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
            check_response(mode, response, request_context(nonce, mode, cases_text, count, texts))
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
                 budget: dict | None = None, texts: list[str] | None = None) -> tuple[bytes, dict]:
        """Send one request whose `cases` is `cases_text` (a JSON array of `count` cases).
        `texts`, when the caller has them, are the case texts `cases_text` joins without
        whitespace (`case_texts(cases_text)`, which is then not recomputed).

        Returns the raw response line and its decoding, whose results are still bound
        (`{"digest", "index", "result"}`). A request error from the service, bound to the
        nonce, mode and case digests, is returned as is (`status: error`); operational
        failures, unbound errors included, are retried once, then raise `CheckerUnavailable`.
        """
        if mode not in MODES:
            raise VEError(f"unknown Lean service mode {mode!r}")
        timeout = self.timeout if timeout is None else timeout
        if budget is None:
            budget = {"cases": max(count, 1), "bytes": len(cases_text.encode())}
        with self._lock:
            attempt = 0
            while True:
                nonce = f"{self._nonce}-{next(self._counter)}"
                line = self._request_line(nonce, mode, cases_text, budget)
                if len(line) > MAX_LINE_BYTES + 1:
                    raise ResourceLimit(f"ResourceLimit: request line exceeds {MAX_LINE_BYTES} bytes")
                try:
                    self._ensure()
                    raw, response = self._roundtrip(mode, cases_text, count, timeout, nonce, line, texts)
                except _Failure as failure:
                    self._failed_attempt(failure, attempt)
                    attempt += 1
                    continue
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

    def _chunks(self, texts: list[str], parts: int = 1):
        """Requests of at most `batch_cases` cases and `batch_bytes`, and at least `parts`
        requests when there are that many cases (so a pool can answer them in parallel)."""
        # `size` is the byte length of "[" + ",".join(chunk) + "]".
        limit = min(self.batch_cases, max(1, -(-len(texts) // max(parts, 1))))
        chunk: list[str] = []
        size = 1
        for text in texts:
            n = len(text.encode())
            if n + 2 + ENVELOPE_BYTES > MAX_LINE_BYTES:
                raise ResourceLimit(f"ResourceLimit: case exceeds {MAX_LINE_BYTES} bytes")
            if chunk and (len(chunk) >= limit or size + n + 1 > self.batch_bytes):
                yield chunk
                chunk, size = [], 1
            chunk.append(text)
            size += n + 1
        if chunk:
            yield chunk

    def _run_chunk(self, mode: str, chunk: list[str], timeout: float | None) -> list:
        cases_text = "[" + ",".join(chunk) + "]"
        size = len(cases_text.encode())
        budget = {"cases": self.batch_cases,
                  "bytes": self.batch_bytes if size <= self.batch_bytes else MAX_LINE_BYTES - ENVELOPE_BYTES}
        _, response = self.exchange(mode, cases_text, len(chunk), timeout=timeout, budget=budget, texts=chunk)
        if response.get("status") == "error":
            message = str(response.get("error", ""))
            if message.startswith("ResourceLimit"):
                raise ResourceLimit(message)
            raise VEError(message)
        return [bound["result"] for bound in response["results"]]

    def run(self, mode: str, cases: list, *, timeout: float | None = None) -> list:
        """The runner results for `cases`, in order. Batches above the adapter caps (256
        cases or 4 MiB) are split into several requests; each is one timeout unit."""
        results: list = []
        for chunk in self._chunks(_texts(cases)):
            results.extend(self._run_chunk(mode, chunk, timeout))
        return results


def _texts(cases: list) -> list[str]:
    return [json.dumps(case, ensure_ascii=False, separators=(",", ":")) for case in cases]


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
        chunks = list(self._services[0]._chunks(_texts(cases), parts=len(self._services)))
        if len(chunks) <= 1:
            return self._on_idle(lambda service: service.run(mode, cases, timeout=timeout))
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
