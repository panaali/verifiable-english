"""The Lean answer store: `ve_service`'s exact answers to the suite's request lines, for R1 only.

docs/test-architecture/store/REPORT.md (plan: reviews/test-architecture-2026-10-14.md, section 3.6). An R1 run
(a commit, a fix round or a recheck: `tools/select_tests.py --run`, `mac-pytest.sh`) may answer a request line
the default service already answered from the store; the merge (R2) and the nightlies (R3) run
`tools/gate.py`, which never uses it.

* **On only when asked, never under the gate.** `--answer-store DIR` or `VE_ANSWER_STORE=DIR` turns it on;
  the variable is then removed from the environment, so no child of a test inherits it. Under `tools/gate.py`
  (`VE_GATE_PYTEST_RESULT` set) asking for it stops the run (`pytest.UsageError`), and the seam answers no
  request there even when installed by hand. The gate's stages also start from a listed environment that
  does not carry the variable.
* **Unit: the exact batch.** The client asks the store (`lean_service.answer_store`) inside `_roundtrip`,
  after `_ensure`: the process is started, pinned and checked, the deadline computed, and the stored line
  then goes through the client's framing, decoding, nonce, schema and binding checks as the process's line
  would. Nothing is stripped, normalised or rewritten. A stored line the client refuses is an operational
  failure of that attempt (`failed`), retried on the process, and an alarm.
* **Only what a hit cannot skip is stored.** A hit writes nothing to the process's standard error, needs no
  retry and is not timed, so an answer is stored only when its request wrote nothing to standard error (no
  `PANIC`) and was answered on its first attempt; a retry after any failed attempt asks the process and is
  not stored. A sampled hit whose live request breaks either is an alarm, and the byte replay compares the
  standard error too.
* **Key:** SHA-256 of the service binary's actual digest (`LeanService.build`, not a pin: the Mac's pins are
  the runner's own), its start-up limits (address space, RSS and request limits) and the request bytes. In
  store mode the client derives the nonce from the rest of the line and registers every environment its
  cases name in the line itself, so the line, and Lean's answer, stand alone: the measured answers that
  differed between two runs of the same line all came from the handle table a process held (REPORT.md,
  step 0). The one answer that can still depend on that table, a `CheckerUnavailable` request error (a handle
  not registered), is never stored.
* **Serving is off** for a branch that changes a guarded path (`GUARDED`: the client and relay, the service
  protocol, the pins, the suite's process guards and this file), for a request with an explicit timeout, a
  non-default executable, an expected hash or an unlisted build, a subclass of the client, a client whose
  methods, module bindings or module tables (a lowered `DEADLINES` entry, as `lean_routes.completed_within`
  sets) or `VE_LEAN_SERVICE*` settings differ from those the store was installed with (`SEAM`,
  `SEAM_GLOBALS`, `SEAM_ENV`: read from the client itself), and for every test marked `live_service` (the
  inventory's live column, `INVENTORY`).
* **Checks.** A random 1% of hits (`SAMPLE`) is asked of the process as well and compared byte for byte: a
  drift alarm only. The nightly replays the whole store against its build (`replay`,
  `tools/answer_replay.py store-replay`) and fails on any byte that differs, or on any standard error. The
  store is not the safety
  argument: R2 is complete and live.
"""
from __future__ import annotations

from collections import OrderedDict
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import threading
import time
import types
import zlib

import pytest

from tests.subprocesses import HANG_TIMEOUT
from ve.backends import lean_service
from ve.backends.lean_service import LeanService, _Deadline, _Failure

ROOT = Path(__file__).resolve().parents[1]
FORMAT = "v1"
ENV = "VE_ANSWER_STORE"
# Set by tools/gate.py for its pytest stage (R2, and R3 = `tools/gate.py --no-quarantine`).
GATE_FLAG = "VE_GATE_PYTEST_RESULT"
LIVE_MARK = "live_service"
SAMPLE = 0.01
# Response bytes each process keeps of the entries it read or recorded, so a repeated batch is not read again.
MEMORY_BYTES = 64 << 20
# A branch that changes one of these runs every request live.
GUARDED = ("ve/backends/", "lean/VE/Service/", "lean/checkers.lock", "tests/subprocesses.py",
           "tests/conftest.py", "tests/answer_store.py")
# The client below the seam, read from the client itself: replaced on the class, on the instance or in the
# module, a module table changed (a lowered `DEADLINES` entry) or a `VE_LEAN_SERVICE*` setting changed, the
# store is off for the request, since a hit would skip what the test put there (a deadline it enforces).
SEAM = tuple(name for name, value in vars(LeanService).items()
             if isinstance(value, (types.FunctionType, property, staticmethod, classmethod)))
# Every module binding but the seam itself and the digest cache, which a test may reset.
SEAM_STATE = ("answer_store", "_hashes")
SEAM_GLOBALS = tuple(name for name in vars(lean_service) if not name.startswith("__") and name not in SEAM_STATE)
SEAM_ENV = "VE_LEAN_SERVICE"
# Wall-clock seconds the byte replay waits for one answer: no CPU deadline, so a loaded nightly never turns an
# answer into a difference; a hung build still ends.
REPLAY_TIMEOUT = HANG_TIMEOUT

# The client behaviours a stored answer could skip, and the deterministic tests that keep each one live
# (plan 3.6, rows 1-13; row 14 from the review): (row, behaviour, what the wire seam skips, tests). Every test named here carries
# the `live_service` mark (tests/test_answer_store.py checks it), so no store ever answers it.
LS, LH = "tests/test_lean_service.py", "tests/test_lean_handles.py"
LSS, EF = "tests/test_lean_service_schema.py", "tests/test_environment_field_types.py"
INVENTORY = (
    (1, "relay: wire check, memo, error classes", "nothing", ("tests/test_relay.py",)),
    (2, "pool split, parallel workers, earliest failure first", "nothing (the pool size shapes the lines)",
     (f"{LS}::test_pool_serves_concurrent_callers", f"{LS}::test_pool_answers_a_batch_in_parallel_with_the_same_results",
      f"{LS}::test_pool_raises_the_earliest_failing_request")),
    (3, "environment handles: encoding, registration, mirror, resend",
     "the handle reuse between requests (store mode registers every environment in its line)", (LH,)),
    (4, "chunking: 256 cases / 4 MiB; a case over 16 MiB is ResourceLimit", "nothing",
     (f"{LS}::test_chunks_fit_their_byte_budget",)),
    (5, "budget member, envelope, 16 MiB line cap", "the random nonce (derived in store mode)",
     (f"{LS}::test_bound_request_error_is_deterministic", f"{LS}::test_oversized_exchange_is_resource_limit_without_start",
      f"{LS}::test_operational_faults_fail_closed")),
    (6, "spawn, pin check, RLIMIT_AS, handshake", "nothing (the store answers after _ensure)",
     (f"{LS}::test_unlisted_build_is_refused_by_default", f"{LS}::test_bad_or_missing_handshake_is_unavailable",
      f"{LS}::test_the_service_runs_under_its_address_space_limit")),
    (7, "deadline computation (_deadline)", "nothing: it runs, but nothing is enforced",
     (f"{LS}::test_the_injected_clock_records_a_miscomputed_deadline",
      "tests/test_w6a_limit_generator.py::test_lean_authority_reports_resource_limit_on_every_generated_case")),
    (8, "enforcement: CPU-deadline kill, wall cap, timeout",
     "all of it (a changed DEADLINES entry or VE_LEAN_SERVICE_TIMEOUT turns the store off)",
     (f"{LS}::test_a_request_past_its_cpu_deadline_names_its_mode_and_is_not_retried",
      f"{LS}::test_each_phase_of_a_request_is_bounded_by_its_cpu_deadline",
      f"{LS}::test_a_request_that_gets_no_cpu_meets_the_wall_cap",
      "tests/test_soft_request_economy.py::test_soft_requests_on_the_widest_environment_stay_within_a_cpu_deadline",
      "tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline",
      # CPU deadlines lowered through lean_routes.completed_within
      "tests/test_readings_lazy_pairs.py::test_the_review_reproducer_gives_the_specified_answer",
      "tests/test_lean_layers_once.py::test_a_rights_request_over_a_wide_environment_is_cheap",
      "tests/test_readings_lean_sharing.py::test_the_other_side_is_scanned_lazily_on_the_review_reproducer",
      "tests/test_readings_lean_sharing.py::test_admission_stops_at_the_first_ill_formed_candidate",
      "tests/test_readings_lean_sharing.py::test_no_pending_candidates_document_is_built")),
    (9, "retry once, restart, RSS recycle",
     "the process's failures and its RSS growth (an answer that needed a retry is never stored)",
     (f"{LS}::test_operational_faults_fail_closed", f"{LS}::test_one_retry_recovers_a_hung_batch",
      f"{LS}::test_recycling_after_max_requests",
      f"{LS}::test_a_process_above_its_rss_threshold_is_recycled_before_the_next_request",
      # retries == 0 on genuine requests
      f"{LSS}::test_genuine_request_errors_are_bound_and_accepted",
      f"{LSS}::test_request_errors_without_their_binding_are_rejected",
      f"{LSS}::test_generated_formulas_follow_each_routes_limits")),
    (10, "framing and decoding: line reader, 1 GiB cap, strict JSON, nonce match",
     "nothing (the stored line goes through _read_line)",
     (f"{LS}::test_complete_lean_response_obeys_size_cap", f"{LS}::test_operational_faults_fail_closed")),
    (11, "schema check (check_response)", "nothing",
     (f"{LS}::test_random_malformed_responses_never_escape_schema", "tests/test_lean_first_b13b.py")),
    (12, "binding: id, mode, one row per case, digest, index, case_index", "nothing",
     (f"{LS}::test_results_not_bound_to_their_cases_fail_closed",
      f"{LS}::test_request_errors_without_their_binding_fail_closed")),
    (13, "stats counters", "the process's own counts (registered, restarts) for a hit",
     (f"{LS}::test_pool_serves_concurrent_callers", LH)),
    (14, "the process's standard error (Lean's PANIC messages, `LeanService.stderr`)",
     "the process's writes (an answer whose request wrote to standard error is never stored)",
     (f"{EF}::test_every_lean_route_rejects_every_wrong_type_without_panicking",
      f"{EF}::test_every_lean_route_reads_every_nested_value_without_panicking",
      "tests/test_lean_first_triage.py::test_df12_risk_route_rejects_an_nbsp_act_phrase")),
)


# The store's files

def key(build: str, limits: tuple, line: bytes) -> str:
    """The entry's key: SHA-256 of the binary's actual digest, its start-up limits and the request bytes."""
    digest = hashlib.sha256(json.dumps([FORMAT, build, list(limits)], separators=(",", ":")).encode() + b"\0")
    digest.update(line)
    return digest.hexdigest()


def limits(service: LeanService) -> tuple:
    return (service.address_space, service.max_rss, service.max_requests)


def stderr_size(service: LeanService) -> int:
    """Bytes the current process has written to standard error (`LeanService.stderr`)."""
    return service.stderr(sys.maxsize)[0]


class Store:
    """Entries under `<root>/v1/<build digest>/<key[:2]>/<key>`: the start-up limits, then the request line
    (with its newline) and the response line exactly as written and read, compressed together."""

    def __init__(self, root: Path):
        self.root = Path(root)

    def namespace(self, build: str) -> Path:
        return self.root / FORMAT / build

    def path(self, build: str, entry: str) -> Path:
        return self.namespace(build) / entry[:2] / entry

    def get(self, build: str, entry: str) -> tuple[tuple, bytes, bytes] | None:
        """The stored (limits, request, response), None when absent; ValueError when unreadable."""
        try:
            data = self.path(build, entry).read_bytes()
        except FileNotFoundError:
            return None
        return decode(data)

    def put(self, build: str, entry: str, limits: tuple, line: bytes, response: bytes) -> None:
        path = self.path(build, entry)
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{entry}.", delete=False) as out:
            out.write(encode(limits, line, response))
        os.replace(out.name, path)

    def remove(self, build: str, entry: str) -> None:
        self.path(build, entry).unlink(missing_ok=True)

    def entries(self, build: str):
        """(key, path) of every entry of `build`, in key order."""
        for path in sorted(self.namespace(build).glob("??/*")):
            if not path.name.startswith("."):
                yield path.name, path


def encode(limits: tuple, line: bytes, response: bytes) -> bytes:
    if not line.endswith(b"\n") or b"\n" in line[:-1] or b"\n" in response:
        raise ValueError("an entry is one request line and one response line")
    return zlib.compress(json.dumps(list(limits)).encode() + b"\n" + line + response, 1)


def decode(data: bytes) -> tuple[tuple, bytes, bytes]:
    """An entry's start-up limits, request line (with its newline) and response line."""
    try:
        text = zlib.decompress(data)
        head, rest = text.split(b"\n", 1)
        recorded = tuple(json.loads(head))
    except (zlib.error, ValueError) as exc:
        raise ValueError(f"unreadable entry: {exc}") from None
    end = rest.find(b"\n")
    if end < 0 or b"\n" in rest[end + 1:]:
        raise ValueError("an entry is one request line and one response line")
    return recorded, rest[:end + 1], rest[end + 1:]


# The seam the client asks

class Seam:
    """What `lean_service.answer_store` holds in an R1 run: the store, the run's counts, and the test now
    running (whether it is live)."""

    def __init__(self, store: Store, sample: float = SAMPLE, rng: random.Random | None = None):
        self.store, self.sample = store, sample
        self.rng = rng or random.Random(os.urandom(16))
        self.methods = {name: LeanService.__dict__[name] for name in SEAM}
        self.globals = {name: vars(lean_service)[name] for name in SEAM_GLOBALS}
        # The client's tables by value (a test may change an entry in place, not only rebind the name).
        self.tables = {name: copy.deepcopy(value) for name, value in self.globals.items()
                       if isinstance(value, (dict, list, set, bytearray))}
        self.environment = self._environment()
        self.default = Path(lean_service.DEFAULT_EXECUTABLE).resolve()
        self.resolved: dict[Path, Path] = {}
        # key -> response bytes of entries this process read or recorded, least recently used first.
        self.memory: OrderedDict[str, bytes] = OrderedDict()
        self.memory_bytes = 0
        self.test, self.live = "", False
        self.lock = threading.Lock()
        self.local = threading.local()
        self.counts = {"asked": 0, "hits": 0, "misses": 0, "recorded": 0, "not_recorded": 0, "sampled": 0,
                       "sampled_same": 0, "sampled_inconclusive": 0}
        self.off: dict[str, int] = {}
        self.alarms: list[dict] = []
        self.live_tests: dict[str, int] = {}

    def _count(self, table: dict, name: str) -> None:
        with self.lock:
            table[name] = table.get(name, 0) + 1

    def _alarm(self, kind: str, build: str, entry: str, detail: str) -> None:
        with self.lock:
            self.alarms.append({"kind": kind, "build": build, "key": entry, "test": self.test, "detail": detail[:300]})

    def reason(self, service: LeanService, timeout) -> str | None:
        """Why the store may not answer this request, or None when it may."""
        if os.environ.get(GATE_FLAG):
            return "gate"
        if self.live:
            return "live_service test"
        if timeout is not None:
            return "explicit timeout"
        if type(service) is not LeanService:
            return "client subclass"
        if service.expected_sha256 is not None:
            return "expected hash"
        if service.allow_unlisted_build:
            return "unlisted build"
        resolved = self.resolved.get(service.executable)
        if resolved is None:
            resolved = self.resolved[service.executable] = service.executable.resolve()
        if resolved != self.default:
            return "non-default executable"
        if any(LeanService.__dict__.get(name) is not self.methods[name] or name in vars(service) for name in SEAM):
            return "client replaced by the test"
        if any(vars(lean_service).get(name) is not value for name, value in self.globals.items()):
            return "client replaced by the test"
        if any(self.globals[name] != value for name, value in self.tables.items()):
            return "client setting changed by the test"
        if self._environment() != self.environment:
            return "client setting changed by the test"
        return None

    @staticmethod
    def _environment() -> dict:
        return {name: value for name, value in os.environ.items() if name.startswith(SEAM_ENV)}

    def applies(self, service: LeanService, timeout) -> bool:
        why = self.reason(service, timeout)
        if why == "live_service test":
            with self.lock:
                self.live_tests[self.test] = self.live_tests.get(self.test, 0) + 1
        if why is not None:
            self._count(self.off, why)
        return why is None

    def answer(self, service: LeanService, line: bytes) -> bytes | None:
        """The stored response line to `line`, or None: absent, unreadable, or this hit sampled for a live
        comparison (`record` then compares)."""
        build = service.build
        entry = key(build, limits(service), line)
        self.local.pending = (line, build, entry, None, stderr_size(service))
        self._count(self.counts, "asked")
        with self.lock:
            response = self.memory.get(entry)
            if response is not None:
                self.memory.move_to_end(entry)
        if response is None:
            try:
                stored = self.store.get(build, entry)
            except (OSError, ValueError) as exc:
                self._alarm("unreadable", build, entry, str(exc))
                self.store.remove(build, entry)
                stored = None
            if stored is not None and (stored[1] != line or stored[0] != limits(service)):
                self._alarm("unreadable", build, entry, "the entry's request is not this line")
                self.store.remove(build, entry)
                stored = None
            if stored is None:
                self._count(self.counts, "misses")
                return None
            response = stored[2]
            self._remember(entry, response)
        if self.rng.random() < self.sample:
            self._count(self.counts, "sampled")
            self.local.pending = (*self.local.pending[:3], response, self.local.pending[4])
            return None
        self._count(self.counts, "hits")
        return response

    def _remember(self, entry: str, response: bytes) -> None:
        with self.lock:
            if entry not in self.memory:
                self.memory[entry] = response
                self.memory_bytes += len(response)
            while self.memory_bytes > MEMORY_BYTES and self.memory:
                self.memory_bytes -= len(self.memory.popitem(last=False)[1])

    def _forget(self, build: str, entry: str) -> None:
        with self.lock:
            response = self.memory.pop(entry, None)
            if response is not None:
                self.memory_bytes -= len(response)
        self.store.remove(build, entry)

    def record(self, service: LeanService, line: bytes, raw: bytes, response: dict) -> None:
        """The process's checked answer to `line`: stored, or compared with the sampled entry."""
        pending = getattr(self.local, "pending", None)
        self.local.pending = None
        if pending is None or pending[0] is not line:
            return
        _, build, entry, sampled, start = pending
        if response.get("status") == "error" and response.get("code") == "CheckerUnavailable":
            # The one answer that can depend on the process's handle table: never stored or compared.
            self._count(self.counts, "sampled_inconclusive" if sampled is not None else "not_recorded")
            return
        _, written = service.stderr(start)
        if written:
            # A hit writes nothing to standard error: an answer whose request did (a PANIC) is never stored.
            if sampled is not None:
                self._alarm("stderr", build, entry, f"the process wrote to standard error: {written}")
                self._forget(build, entry)
            else:
                self._count(self.counts, "not_recorded")
            return
        if sampled is not None:
            if sampled == raw:
                self._count(self.counts, "sampled_same")
            else:
                self._alarm("drift", build, entry, "the process answered other bytes than the store")
                self._forget(build, entry)
            return
        try:
            self.store.put(build, entry, limits(service), line, raw)
        except (OSError, ValueError):
            self._count(self.counts, "not_recorded")
            return
        self._remember(entry, raw)
        self._count(self.counts, "recorded")

    def failed(self, service: LeanService, line: bytes | None, failure: Exception, *, served: bool) -> None:
        """An attempt at `line` failed: the client refused the stored answer (`served`), or the process failed;
        `line` is None when the process failed to start before the line was built (then the store was not asked).
        The client then asks the process without the store, so an answer that needed a retry is never stored.
        A refused entry is an alarm, and the entry goes; a sampled hit whose live attempt failed compares
        nothing (an operational failure of the process, which the client's retry answers as without a store)."""
        pending = getattr(self.local, "pending", None)
        self.local.pending = None
        if pending is None or pending[0] is not line:
            return
        _, build, entry, sampled, _ = pending
        if served:
            self._alarm("refused", build, entry, str(failure))
            self._forget(build, entry)
        else:
            self._count(self.counts, "sampled_inconclusive" if sampled is not None else "not_recorded")

    def report(self) -> dict:
        with self.lock:
            return {"counts": dict(self.counts), "off": dict(self.off), "alarms": list(self.alarms),
                    "live_tests": dict(self.live_tests)}


# Which branches may be served

def changed_guarded_paths(root: Path = ROOT) -> list[str] | None:
    """The guarded paths the checkout changes against its merge base with main, committed or not; None when
    git cannot say (then nothing is served)."""
    def git(*arguments):
        result = subprocess.run(["git", *arguments], cwd=root, capture_output=True, text=True, timeout=HANG_TIMEOUT)
        if result.returncode:
            raise OSError(result.stderr.strip())
        return result.stdout.split("\n")
    try:
        base = None
        for ref in ("main", "origin/main"):
            try:
                base = git("merge-base", "HEAD", ref)[0].strip()
                break
            except OSError:
                continue
        if not base:
            return None
        changed = git("diff", "--name-only", base, "--") + git("ls-files", "--others", "--exclude-standard")
    except (OSError, subprocess.SubprocessError):
        return None
    return sorted({path for path in changed if path and path.startswith(GUARDED)})


def settings(directory: str | None, *, environ=os.environ, root: Path = ROOT) -> dict | None:
    """What this run does with the store: None (not asked for), or `{"directory", "off"}`, where `off` is why
    nothing is served (None: served). Asked for under the gate, it stops the run."""
    if directory is None:
        return None
    if environ.get(GATE_FLAG):
        raise pytest.UsageError("the Lean answer store is for R1 only: tools/gate.py (R2, R3) never uses it "
                                f"({GATE_FLAG} is set)")
    changed = changed_guarded_paths(root)
    if changed is None:
        off = "git cannot say what this branch changes"
    elif changed:
        off = f"this branch changes {', '.join(changed[:5])}" + (" ..." if len(changed) > 5 else "")
    else:
        off = None
    return {"directory": str(Path(directory).expanduser().resolve()), "off": off}


# The pytest plugin (registered by tests/conftest.py)

def pytest_addoption(parser):
    parser.addoption("--answer-store", metavar="DIR", default=None,
                     help=f"R1 only: answer Lean service requests from the store in DIR (also {ENV}); "
                          "tools/gate.py refuses it (tests/answer_store.py)")


@pytest.hookimpl(trylast=True)  # after tests/conftest.py sets the client's settings (`Seam.environment`)
def pytest_configure(config):
    config.addinivalue_line("markers", f"{LIVE_MARK}: always asks the Lean service itself, never the answer "
                                       "store (tests/answer_store.py INVENTORY)")
    workerinput = getattr(config, "workerinput", None)
    asked = os.environ.pop(ENV, None)  # no child of a test inherits it
    if workerinput is not None:
        chosen = workerinput.get("answer_store")
    else:
        chosen = settings(config.getoption("answer_store") or asked)
    config._answer_store = chosen
    if chosen is not None and chosen["off"] is None:
        seam = Seam(Store(Path(chosen["directory"])))
        config._answer_store_seam = seam
        lean_service.answer_store = seam


@pytest.hookimpl(optionalhook=True)
def pytest_configure_node(node):
    node.workerinput["answer_store"] = getattr(node.config, "_answer_store", None)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    seam = getattr(item.config, "_answer_store_seam", None)
    if seam is None:
        yield
        return
    seam.test, seam.live = item.nodeid, item.get_closest_marker(LIVE_MARK) is not None
    if seam.live:
        seam.live_tests.setdefault(item.nodeid, 0)
    try:
        yield
    finally:
        seam.test, seam.live = "", False


@pytest.hookimpl(optionalhook=True)
def pytest_testnodedown(node, error):
    reports = node.config.__dict__.setdefault("_answer_store_reports", [])
    report = getattr(node, "workeroutput", {}).get("answer_store")
    if report is not None:
        reports.append(report)


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    seam = getattr(config, "_answer_store_seam", None)
    if hasattr(config, "workerinput"):
        if seam is not None:
            config.workeroutput["answer_store"] = seam.report()
        return
    chosen = getattr(config, "_answer_store", None)
    if chosen is None:
        return
    summary = merged([*config.__dict__.get("_answer_store_reports", []), *([seam.report()] if seam else [])])
    summary["off"] = chosen["off"]
    runs = Path(chosen["directory"]) / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    (runs / f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{os.getpid()}.json").write_text(
        json.dumps(summary, indent=1, sort_keys=True) + "\n")
    config._answer_store_summary = summary
    if summary["alarms"] and session.exitstatus == 0:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    summary = getattr(config, "_answer_store_summary", None)
    if summary is None:
        return
    if summary["off"]:
        terminalreporter.write_line(f"answer store: off ({summary['off']}); every request asked live")
        return
    c = summary["counts"]
    terminalreporter.write_line(
        f"answer store: {c['asked']} requests looked up, {c['hits']} answered from the store, {c['misses']} asked "
        f"live ({c['recorded']} recorded), {c['sampled']} hits sampled live ({c['sampled_same']} the same); "
        f"{sum(summary['off_requests'].values())} requests not eligible; {len(summary['live_tests'])} "
        f"live_service tests ran live")
    for alarm in summary["alarms"]:
        terminalreporter.write_line(f"ANSWER STORE ALARM ({alarm['kind']}) in {alarm['test']}: {alarm['detail']} "
                                    f"[{alarm['build'][:12]}/{alarm['key']}]", red=True)


def merged(reports: list[dict]) -> dict:
    counts: dict[str, int] = {}
    off: dict[str, int] = {}
    live: dict[str, int] = {}
    alarms: list = []
    for report in reports:
        for table, into in ((report["counts"], counts), (report["off"], off), (report["live_tests"], live)):
            for name, value in table.items():
                into[name] = into.get(name, 0) + value
        alarms.extend(report["alarms"])
    return {"counts": counts, "off_requests": off, "live_tests": live, "alarms": alarms}


# The nightly byte replay (tools/answer_replay.py store-replay)

def replay(root: Path, executable: Path, *, allow_unlisted_build: bool = False, jobs: int = 4) -> dict:
    """Every entry of the store for `executable`'s build, its request line sent to that build started under the
    entry's limits, and the answer compared with the stored response byte for byte. Entries go to `jobs`
    threads, each with one process per set of limits, restarted before a line could overflow its handle table
    (an entry's line registers every environment it names, so its answer never depends on earlier lines)."""
    store = Store(root)
    build = lean_service.executable_sha256(Path(executable))
    entries = list(store.entries(build))
    result = {"build": build, "entries": len(entries), "same": 0, "different": [], "unreadable": [],
              "other_builds": sorted(p.name for p in (store.root / FORMAT).glob("*")
                                     if p.is_dir() and p.name != build)}
    lock = threading.Lock()
    shares = [entries[i::max(jobs, 1)] for i in range(max(jobs, 1))]

    def run(share):
        services: dict[tuple, list] = {}  # limits -> [service, digests held since its start, bytes sent]
        try:
            for entry, path in share:
                try:
                    recorded, line, expected = decode(path.read_bytes())
                    registered = list(json.loads(line).get("environments") or {})
                except (OSError, ValueError) as exc:
                    with lock:
                        result["unreadable"].append({"key": entry, "detail": str(exc)[:300]})
                    continue
                if recorded not in services:
                    address_space, max_rss, max_requests = recorded
                    services[recorded] = [LeanService(executable, allow_unlisted_build=allow_unlisted_build,
                                                      address_space=address_space, max_rss=max_rss,
                                                      max_requests=max_requests), set(), 0]
                state = services[recorded]
                service = state[0]
                new = [d for d in registered if d not in state[1]]
                if new and (len(state[1]) + len(new) > lean_service.MAX_HANDLES
                            or state[2] + len(line) > lean_service.MAX_HANDLE_BYTES):
                    service._stop(graceful=True)
                    state[1], state[2] = set(), 0
                try:
                    service._ensure()
                    if service.stats["starts"] and service._served == 0:
                        state[1], state[2] = set(), 0  # a fresh process holds no handle
                    deadline = _Deadline(time.monotonic() + REPLAY_TIMEOUT)
                    start = stderr_size(service)
                    service._write_all(line, deadline)
                    answer = service._read_line(deadline)
                    service._served += 1
                    # A stored answer stands for a request that wrote nothing to standard error.
                    _, written = service.stderr(start)
                except _Failure as exc:
                    service._stop(graceful=False)
                    answer, written = f"<no answer: {exc}>".encode(), ""
                if new:
                    state[1].update(new)
                    state[2] += len(line)
                with lock:
                    if answer == expected and not written:
                        result["same"] += 1
                    else:
                        result["different"].append({"key": entry, "stored": expected[:300].decode(errors="replace"),
                                                    "replayed": answer[:300].decode(errors="replace"),
                                                    "stderr": written[:300]})
        finally:
            for service, _, _ in services.values():
                service.close()

    threads = [threading.Thread(target=run, args=(share,)) for share in shares if share]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    result["different"].sort(key=lambda row: row["key"])
    result["unreadable"].sort(key=lambda row: row["key"])
    result["ok"] = not result["different"] and not result["unreadable"] and result["same"] == result["entries"]
    return result
