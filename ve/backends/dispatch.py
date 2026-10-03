"""Per-operation authority selection and zero-tolerance shadow recording.

Python remains the default through stage 3.  A shadow call always returns the
Python result (or re-raises Python's exception); the candidate is the `lean=`
adapter run at the authority `lean`, and every difference, every unanswered
call and every recorder fault is written as a JSONL record before the call
returns (docs/spec/mig3.md 2.3 to 2.7).  A selected Lean or Rust authority
never falls back to Python.
"""
from __future__ import annotations

import atexit
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, fields, is_dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import secrets
import sys
import threading
import time
from typing import Callable, Iterator, TypeVar

from .lean_service import CheckerUnavailable

T = TypeVar("T")
_AUTHORITIES = frozenset({"python", "shadow", "lean", "rust-experimental"})
_log_lock = threading.RLock()
# Callables told (op, authority) on every dispatched call; the Gate 2 parity
# tool uses them to tell adapter-routed cells from Python-only ones.
observers: list[Callable[[str, str], None]] = []

# The 23 dispatch names of docs/spec/mig3.md 2.2: the first arguments of the
# calls of `execute` in `ve/` (fixture L11 scans for them).
DISPATCH_NAMES = (
    "parse", "typing", "environment_validation", "model_validation", "evaluate",
    "countermodel_check", "countermodel_search", "distinguishing_model", "certificate_replay",
    "background", "dependency_order", "definitions_elaboration", "norms_elaborate",
    "norms_conflict", "norms_certificate", "norms_admission", "admission", "label", "readings",
    "graph", "bundle", "premise_status", "compare",
)

# The conditions that route a class-A input to Python statically at the
# authority `shadow` (mig3.md 2.7): each adapter calls `note_uncompared` with
# one of these before it runs Python.  The calls are counted, never compared.
UNCOMPARED_REASONS = {
    "parse-scope": "the environment's family is outside Lean's surface parser",
    "typing-scope": "the environment is outside Lean's typing check",
    "environment-generated-reports": "the environment carries generated reports, which only Python decodes",
    "environment-scope": "a statement-layer or legacy envelope, validated by its own route",
    "model-deferred-id": "a search candidate without a model identity, decoded by Python",
    "model-scope": "the environment is outside Lean's model mode",
    "background-scope": "the environment is outside Lean's model mode",
    "background-soft": "a soft environment, whose premises the soft route regenerates",
    "background-no-model-id": "a model without an identity (a search candidate)",
    "definitions-scope": "the environment is outside Lean's model mode",
    "readings-scope": "the environment is outside Lean's readings mode",
    "graph-scope": "the graph is outside Lean's graph mode",
    "bundle-scope": "the bundle has no Lean bundle mode",
    "certificate-self-replay": "the prover's self-replay of a generated trace",
    "certificate-generated-premises": "a replay with labelled generated premises",
    "norms-route": "the norm document is outside the Lean norms route",
    "admission-soft": "a soft environment, admitted by the soft route",
}

# The base plan's ten classes (mig3.md 2.5): eight at zero tolerance and two
# recorded with bounds reported; `latency` is tallied and never in a class list.
ZERO_TOLERANCE = frozenset({"verdict", "identity", "diagnostic-code", "schema", "explanation",
                            "budget-outcome", "composition", "count-value"})
RECORDED = frozenset({"diagnostic-message", "latency"})
COMPOSITION_MEMBERS = frozenset({"composition", "assumptions", "assumption_claim_ids",
                                 "supporting_edge_ids", "unresolved_obligations"})
IDENTITY_MEMBERS = frozenset({"environment_id", "source_id", "meaning_id", "model_id", "claim_id",
                              "edge_id", "graph_id", "report_id", "document_hash"})
COUNT_MEMBERS = ("evaluations", "steps", "models_checked")
_VERDICT_KEYS = frozenset({"valid", "value", "values", "refutes", "composed", "verdict"})
_EXPLANATION = frozenset({"explanation", "trace"})
# Upper bounds of the latency histogram in milliseconds; one more cell above them.
LATENCY_BOUNDS = (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1_000, 2_000, 5_000)
INPUT_LIMIT = 65_536
_TALLY_EVERY = 1_000
_WORDING = Path(__file__).resolve().parents[2] / "conformance/shadow/wording.json"


# The authority of every call inside an adapter that composes other operations
# (`pinned`); None outside one.
_pin: ContextVar[str | None] = ContextVar("ve_authority_pin", default=None)


@contextmanager
def pinned(authority: str) -> Iterator[None]:
    """Run a composing adapter's constituents on `authority`, whatever the
    per-operation selection: the adapter's verdict then rests on that backend's
    checks only, never on a constituent another override sent to Python."""
    if authority not in _AUTHORITIES - {"shadow"}:
        raise ValueError(f"invalid pinned authority {authority!r}")
    token = _pin.set(authority)
    try:
        yield
    finally:
        _pin.reset(token)


def composed(authority: str, run: Callable[[], T]) -> Callable[[], T]:
    """`run` with its constituents pinned to `authority` (an adapter for `execute`)."""
    def adapter() -> T:
        with pinned(authority):
            return run()
    return adapter


def authority_for(op: str) -> str:
    pin = _pin.get()
    if pin is not None:
        return pin
    selected = os.environ.get("VE_AUTHORITY", "python")
    for entry in filter(None, os.environ.get("VE_AUTHORITY_OVERRIDES", "").split(",")):
        name, sep, authority = entry.partition("=")
        if not sep or not name or authority not in _AUTHORITIES:
            raise ValueError(f"invalid VE_AUTHORITY_OVERRIDES entry {entry!r}")
        if name == op:
            selected = authority
    if selected not in _AUTHORITIES:
        raise ValueError(f"invalid VE_AUTHORITY {selected!r}")
    if selected == "shadow":
        # A worker registers before its first shadow call (mig3.md 2.7).
        _worker()
    return selected


def _record(value):
    if hasattr(value, "to_dict"):
        return _record(value.to_dict())
    if is_dataclass(value):
        return _record(asdict(value))
    if isinstance(value, dict):
        return {key: _record(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_record(item) for item in value]
    return value


def _code(exc: BaseException) -> str:
    return getattr(exc, "code", type(exc).__name__)


def error_record(exc: BaseException) -> dict:
    """The public record of a raised exception (mig3.md 2.4): `to_dict()` where
    it has one, as the baseline compares it; otherwise its code (or type name)
    and its text."""
    if hasattr(exc, "to_dict"):
        return _record(exc.to_dict())
    return {"code": _code(exc), "message": str(exc)}


def baseline_projection(value):
    """Omit only checker-build-derived diagnostic identities from the oracle.

    The comparison projection of the Stage 0 baseline and of shadow: one
    definition (`tests/probe_matrix.py` imports it)."""
    if isinstance(value, dict):
        return {key: baseline_projection(item) for key, item in value.items()
                if key not in {"checker_build", "record_id"}}
    if isinstance(value, list):
        return [baseline_projection(item) for item in value]
    return value


# --- the wording map ------------------------------------------------------------

def wording_location_eligible(op, path) -> bool:
    """Whether a wording entry's operation and path name an eligible location:
    diagnostic text, or the graph record's root `proof` (mig3.md 2.4)."""
    if type(path) is not list or not path or not all(type(name) is str for name in path):
        return False
    if op == "graph" and path == ["proof"]:
        return True
    return (op in DISPATCH_NAMES and path[-1] in ("message", "detail")
            and not any(name in _EXPLANATION or name in COMPOSITION_MEMBERS for name in path))


def wording_entry_problem(entry) -> str | None:
    """Why `entry` is not a well-formed wording entry, or None."""
    if type(entry) is not dict or set(entry) != {"op", "path", "python", "backend", "reviewed"}:
        return "members"
    if not all(type(entry[name]) is str for name in ("python", "backend", "reviewed")) \
            or not entry["reviewed"]:
        return "members"
    if not wording_location_eligible(entry["op"], entry["path"]):
        return "location"
    return None


_wording_cache: tuple[float, frozenset] | None = None


def _wording() -> frozenset:
    """The reviewed wordings, as (op, path, python text, backend text); entries
    at an ineligible location are never applied."""
    global _wording_cache
    try:
        stamp = _WORDING.stat().st_mtime
    except OSError:
        return frozenset()
    if _wording_cache is None or _wording_cache[0] != stamp:
        entries = json.loads(_WORDING.read_text(encoding="utf-8"))
        _wording_cache = (stamp, frozenset(
            (entry["op"], tuple(entry["path"]), entry["python"], entry["backend"])
            for entry in entries if wording_entry_problem(entry) is None))
    return _wording_cache[1]


# --- the classes ----------------------------------------------------------------

_JSON_TYPES = (dict, list, str, bool, int, float, type(None))


def _kind(value):
    for kind in _JSON_TYPES:
        if type(value) is kind:
            return kind
    return type(value)


def classify(op: str, left, right, counts: dict | None = None) -> list[str]:
    """The class set of two records that both returned or both raised (case A
    of mig3.md 2.5), after the comparison projection.  `counts`, when given,
    receives the equal/different leaf comparisons of the count members."""
    left, right = baseline_projection(_record(left)), baseline_projection(_record(right))
    wording = _wording()
    classes: set[str] = set()

    def shape(path: tuple[str, ...]) -> None:
        classes.add("schema")
        if any(name in _EXPLANATION for name in path):
            classes.add("explanation")
        if any(name in COMPOSITION_MEMBERS for name in path):
            classes.add("composition")

    def leaf(path: tuple[str, ...]) -> None:
        key = path[-1] if path else ""
        if any(name in _EXPLANATION for name in path):
            classes.add("explanation")
        elif any(name in COMPOSITION_MEMBERS for name in path):
            classes.add("composition")
        elif key == "status":
            classes.update(("verdict", "budget-outcome"))
        elif key in _VERDICT_KEYS:
            classes.add("verdict")
            if key == "verdict" and op == "readings":
                classes.add("composition")
        elif key in IDENTITY_MEMBERS:
            classes.add("identity")
        elif key in COUNT_MEMBERS:
            classes.add("count-value")
        elif key in ("code", "generator"):
            classes.add("diagnostic-code")
        elif key in ("message", "detail"):
            classes.add("diagnostic-message")
        else:
            classes.add("schema")

    def visit(a, b, path: tuple[str, ...]) -> None:
        kind = _kind(a)
        if kind is not _kind(b):
            shape(path)
            return
        if kind is dict:
            if a.keys() != b.keys():
                shape(path)
            for key in a.keys() & b.keys():
                visit(a[key], b[key], (*path, key))
            return
        if kind is list:
            if len(a) != len(b):
                shape(path)
            for x, y in zip(a, b):
                visit(x, y, path)
            return
        equal = a == b or (kind is str and (op, path, a, b) in wording)
        if (counts is not None and path and path[-1] in COUNT_MEMBERS
                and not any(name in _EXPLANATION or name in COMPOSITION_MEMBERS for name in path)):
            cell = counts.setdefault(path[-1], {"equal": 0, "different": 0})
            cell["equal" if equal else "different"] += 1
        if not equal:
            leaf(path)

    visit(left, right, ())
    return sorted(classes)


def _mixed_classes(raised: dict, returned) -> list[str]:
    """Case B of mig3.md 2.5: one side returned and the other raised."""
    classes = {"verdict", "schema"}
    if raised.get("code") == "ResourceLimit" or (
            type(returned) is dict and returned.get("status") == "ResourceLimit"):
        classes.add("budget-outcome")
    return sorted(classes)


# --- records and tallies ---------------------------------------------------------

def _jsonable(value):
    """`value` with everything JSON cannot hold written as `<unserializable T>`."""
    kind = _kind(value)
    if kind is dict:
        result = {}
        for key, item in value.items():
            if type(key) is not str:
                key = (json.dumps(key) if _kind(key) in (int, bool, type(None)) else
                       f"<unserializable {type(key).__name__}>")
            result[key] = _jsonable(item)
        return result
    if kind is list or isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if kind is float and not math.isfinite(value):
        return f"<unserializable {type(value).__name__}>"
    if kind in (str, bool, int, float, type(None)):
        return value
    return f"<unserializable {type(value).__name__}>"


def _line(record: dict) -> str:
    return json.dumps(_jsonable(record), sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False) + "\n"


def payload_data(value):
    """The canonical JSON form of a call's payload (requirement (I) of mig3.md
    2.6): every input the operation's result depends on, with formula nodes and
    other dataclasses tagged by their type.  Raises TypeError for a value it
    cannot write."""
    kind = _kind(value)
    if kind in (str, bool, int, type(None)):
        return value
    if kind is float:
        if not math.isfinite(value):
            raise TypeError("non-finite float in payload")
        return value
    if kind is dict:
        return {str(key): payload_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [payload_data(item) for item in value]
    if isinstance(value, (set, frozenset)):
        items = [payload_data(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))
    if isinstance(value, (bytes, bytearray)):
        return {"$bytes": bytes(value).hex()}
    if isinstance(value, os.PathLike):
        return os.fspath(value)
    if hasattr(value, "to_dict"):
        try:
            data = value.to_dict()
        except TypeError:   # a `to_dict` that needs its context (a claim's environment)
            data = None
        else:
            return {"$type": type(value).__name__, "data": payload_data(data)}
    if is_dataclass(value) and not isinstance(value, type):
        return {"$type": type(value).__name__,
                **{field.name: payload_data(getattr(value, field.name)) for field in fields(value)}}
    raise TypeError(f"cannot write a {type(value).__name__} in a payload")


def _input(payload) -> tuple[str | None, object]:
    """The `input_digest` and `input` members of a record for `payload`."""
    try:
        data = payload_data(payload)
        text = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                          allow_nan=False)
    except (TypeError, ValueError, RecursionError):
        return None, None
    encoded = text.encode()
    return hashlib.sha256(encoded).hexdigest(), data if len(encoded) <= INPUT_LIMIT else None


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _op_counts() -> dict:
    return {"compared": 0, "agree": 0, "recorded_only": 0, "zero_tolerance": 0,
            "completion_failures": 0, "unavailable_other": 0, "uncompared": {}, "lean_only": 0,
            "recorder_faults": 0,
            "count_members": {name: {"equal": 0, "different": 0} for name in COUNT_MEMBERS},
            "latency": {side: {"count": 0, "sum": 0.0, "min": None, "max": None,
                               "histogram": [0] * (len(LATENCY_BOUNDS) + 1)}
                        for side in ("python", "backend")}}


def latency_cell(ms: float) -> int:
    """The histogram cell of a duration: the first whose bound is not below it."""
    return next((index for index, bound in enumerate(LATENCY_BOUNDS) if ms <= bound),
                len(LATENCY_BOUNDS))


class _Worker:
    """One process's evidence in one `VE_SHADOW_DIR` (mig3.md 2.6, 2.7)."""

    def __init__(self, directory: Path):
        self.directory, self.pid, self.nonce = directory, os.getpid(), secrets.token_hex(6)
        self.run = os.environ.get("VE_SHADOW_RUN")
        self.started, self.final, self.calls, self.ops = _now(), False, 0, {}
        self.records = directory / f"records-{self.pid}-{self.nonce}.jsonl"
        self.tally = directory / f"tally-{self.pid}-{self.nonce}.json"
        self.warned: set[str] = set()

    def op(self, name: str) -> dict:
        return self.ops.setdefault(name, _op_counts())

    def warn(self, what: str, exc: BaseException) -> None:
        # One line on standard error for the process, for each kind of write.
        if what not in self.warned:
            self.warned.add(what)
            _stderr(f"ve shadow: cannot write {what}: {exc}")

    def write_tally(self) -> None:
        data = {"run": self.run, "pid": self.pid, "nonce": self.nonce, "started": self.started,
                "final": self.final, "calls": self.calls, "ops": self.ops}
        temporary = self.tally.with_name(self.tally.name + ".tmp")
        try:
            temporary.write_text(_line(data), encoding="utf-8")
            os.replace(temporary, self.tally)
        except OSError as exc:
            self.warn("tally", exc)


_workers: dict[tuple[int, str], _Worker] = {}


def _stderr(line: str) -> None:
    try:
        sys.stderr.write(line + "\n")
        sys.stderr.flush()
    except (OSError, ValueError):
        pass


def _directory() -> str | None:
    """The run directory when records and tallies go to `VE_SHADOW_DIR`; an
    explicit `VE_SHADOW_LOG` comes first and keeps no tally."""
    if os.environ.get("VE_SHADOW_LOG"):
        return None
    return os.environ.get("VE_SHADOW_DIR") or None


def _worker() -> _Worker | None:
    """This process's worker in the current `VE_SHADOW_DIR`, registered (its
    tally written with `final: false`) the first time it is asked for."""
    directory = _directory()
    if directory is None:
        return None
    key = (os.getpid(), directory)
    worker = _workers.get(key)
    if worker is None:
        with _log_lock:
            worker = _workers.get(key)
            if worker is None:
                worker = _workers[key] = _Worker(Path(directory))
                worker.write_tally()
    return worker


@atexit.register
def _finalize() -> None:
    """Rewrite every tally of this process with `final: true` at a normal exit."""
    with _log_lock:
        for (pid, _), worker in list(_workers.items()):
            # A directory removed before the exit (a test's temporary run) has no run to finalize.
            if pid == os.getpid() and worker.directory.is_dir():
                worker.final = True
                worker.write_tally()


def _emit(record: dict, worker: _Worker | None) -> bool:
    """Append one record with one write, flushed before the call returns."""
    line = _line(record)
    if worker is not None:
        path, what = worker.records, "records"
    else:
        path, what = Path(os.environ.get("VE_SHADOW_LOG") or "ve-shadow.jsonl"), "records"
    try:
        with _log_lock:
            with path.open("a", encoding="utf-8") as stream:
                stream.write(line)
                stream.flush()
        return True
    except OSError as exc:
        if worker is not None:
            worker.warn(what, exc)
        else:
            _stderr(f"ve shadow: cannot write records: {exc}")
        return False


def _base(kind: str, op: str, payload, python, lean, python_ms, backend_ms) -> dict:
    digest, data = _input(payload)
    return {"kind": kind, "op": op, "input_digest": digest, "python": python, "lean": lean,
            "rust": None, "class": [], "python_ms": python_ms, "backend_ms": backend_ms,
            "run": os.environ.get("VE_SHADOW_RUN"), "test": os.environ.get("PYTEST_CURRENT_TEST"),
            "input": data}


def _fault(op: str, payload, exc: BaseException, worker: _Worker | None,
           python=None, lean=None, python_ms=None, backend_ms=None) -> None:
    """Count a recorder fault and write its record if it can be written."""
    try:
        if worker is not None:
            with _log_lock:
                worker.op(op)["recorder_faults"] += 1
        record = _base("recorder-fault", op, payload, python, lean, python_ms, backend_ms)
        record["error"] = f"{type(exc).__name__}: {exc}"
        _emit(record, worker)
    except Exception as again:  # noqa: BLE001 - the recorder never reaches the caller
        _stderr(f"ve shadow: recorder fault: {type(again).__name__}: {again}")


def _tick(worker: _Worker) -> None:
    worker.calls += 1
    if worker.calls % _TALLY_EVERY == 0:
        worker.write_tally()


_NO_ADAPTER = object()


def _settle(op: str, payload, outcome, candidate, python_ms, backend_ms,
            worker: _Worker | None) -> None:
    """Step 3 of mig3.md 2.3: compare, write a record if one is due, tally."""
    python_raised, python_value = outcome
    left = error_record(python_value) if python_raised else _record(python_value)
    if candidate is _NO_ADAPTER:
        backend_raised, right = True, {"code": "CheckerUnavailable", "message": f"no adapter for {op}"}
        backend_unavailable = True
    else:
        backend_raised, backend_value = candidate
        right = error_record(backend_value) if backend_raised else _record(backend_value)
        backend_unavailable = backend_raised and _code(backend_value) == "CheckerUnavailable"
    python_unavailable = python_raised and _code(python_value) == "CheckerUnavailable"
    counts = worker.op(op) if worker is not None else None
    if python_unavailable or backend_unavailable:
        sides = sorted(name for name, gone in (("backend", backend_unavailable),
                                               ("python", python_unavailable)) if gone)
        record = _base("unavailable", op, payload, left, right, python_ms, backend_ms)
        record["sides"] = sides
        if _emit(record, worker) is False and counts is not None:
            counts["recorder_faults"] += 1
        if counts is not None:
            counts["completion_failures" if sides == ["backend"] else "unavailable_other"] += 1
        return
    members: dict = {}
    if python_raised == backend_raised:
        classes = classify(op, left, right, members)
    else:
        classes = _mixed_classes(left if python_raised else right, right if python_raised else left)
    if classes:
        record = _base("divergence", op, payload, left, right, python_ms, backend_ms)
        record["class"] = classes
        if _emit(record, worker) is False and counts is not None:
            counts["recorder_faults"] += 1
    if counts is None:
        return
    counts["compared"] += 1
    if not classes:
        counts["agree"] += 1
    elif ZERO_TOLERANCE.intersection(classes):
        counts["zero_tolerance"] += 1
    else:
        counts["recorded_only"] += 1
    for name, cell in members.items():
        for verdict, number in cell.items():
            counts["count_members"][name][verdict] += number
    for side, ms in (("python", python_ms), ("backend", backend_ms)):
        latency = counts["latency"][side]
        latency["count"] += 1
        latency["sum"] += ms
        latency["min"] = ms if latency["min"] is None else min(latency["min"], ms)
        latency["max"] = ms if latency["max"] is None else max(latency["max"], ms)
        latency["histogram"][latency_cell(ms)] += 1


def _shadow(op: str, payload, python: Callable[[], T], lean: Callable[[], T] | None) -> T:
    """A shadow call (mig3.md 2.3): the outcome is always Python's."""
    worker = _worker()
    started = time.monotonic()
    try:
        outcome = (False, python())
    except Exception as exc:
        outcome = (True, exc)
    python_ms = (time.monotonic() - started) * 1000
    backend_ms = None
    if lean is None:
        candidate = _NO_ADAPTER
    else:
        started = time.monotonic()
        try:
            with pinned("lean"):
                candidate = (False, lean())
        except Exception as exc:
            candidate = (True, exc)
        backend_ms = (time.monotonic() - started) * 1000
    try:
        with _log_lock:
            _settle(op, payload, outcome, candidate, python_ms, backend_ms, worker)
            if worker is not None:
                _tick(worker)
    except Exception as exc:  # noqa: BLE001 - V1: a recorder fault never reaches the caller
        _fault(op, payload, exc, worker, python_ms=python_ms, backend_ms=backend_ms)
    if outcome[0]:
        raise outcome[1]
    return outcome[1]


def execute(op: str, payload, python: Callable[[], T], *,
            lean: Callable[[], T] | None = None,
            rust: Callable[[], T] | None = None) -> T:
    """Run the selected implementation, or compare both while returning Python.

    The caller passes independent implementations with the same public result
    type.  No class-A result may be inferred from the Python result in `lean`.
    `payload` holds every input the result depends on (mig3.md 2.6,
    requirement (I)); it is written only into shadow records.
    """
    authority = authority_for(op)
    for observe in observers:
        observe(op, authority)
    if authority == "python":
        return python()
    if authority == "lean":
        if lean is None:
            raise CheckerUnavailable(f"CheckerUnavailable: Lean adapter for {op} is not available")
        return lean()
    if authority == "rust-experimental":
        if rust is None:
            raise CheckerUnavailable(f"CheckerUnavailable: Rust adapter for {op} is not available")
        return rust()
    return _shadow(op, payload, python, lean)


def note_uncompared(op: str, reason: str | Callable[[], str]) -> None:
    """Count a call that the adapter answers from Python alone because its input
    is a scope gap (mig3.md 2.7).  Only counts, only at the authority `shadow`,
    and never raises.  A branch with several static conditions passes `reason`
    as a function naming the one that holds, so that nothing is evaluated at
    any other authority."""
    try:
        if _pin.get() is not None or (os.environ.get("VE_AUTHORITY") != "shadow" and "shadow"
                                      not in os.environ.get("VE_AUTHORITY_OVERRIDES", "")):
            return
        if authority_for(op) != "shadow":
            return
        if callable(reason):
            reason = reason()
        worker = _worker()
        registered = reason in UNCOMPARED_REASONS
        if worker is not None:
            with _log_lock:
                cell = worker.op(op)["uncompared"]
                name = reason if registered else "unregistered"
                cell[name] = cell.get(name, 0) + 1
        if not registered:
            _fault(op, {"reason": reason}, ValueError(f"unregistered uncompared reason {reason!r}"), worker)
    except Exception as exc:  # noqa: BLE001 - counting never reaches the caller
        _stderr(f"ve shadow: recorder fault: {type(exc).__name__}: {exc}")


def lean_only(executable, cases: list, call: Callable[[], T],
              rows: Callable[[T], list]) -> T:
    """Hand `cases` to a statement-layer route that has no Python implementation.

    While `VE_AUTHORITY` is `shadow`, one `lean-only` record is written for each
    case, with Lean's row for it (mig3.md 2.6); the call returns or raises as
    it does at every other authority."""
    if os.environ.get("VE_AUTHORITY") != "shadow":
        return call()
    started = time.monotonic()
    try:
        result = call()
    except Exception as exc:
        _lean_only_records(executable, cases, None, exc, (time.monotonic() - started) * 1000)
        raise
    _lean_only_records(executable, cases, result, None, (time.monotonic() - started) * 1000, rows)
    return result


def _lean_only_records(executable, cases, result, exc, backend_ms, rows=None) -> None:
    op = Path(os.fspath(executable)).name
    worker = None
    try:
        worker = _worker()
        answers = ([error_record(exc)] * len(cases) if exc is not None else
                   [_record(row) for row in rows(result)])
        if len(answers) != len(cases):
            raise ValueError("a Lean-only answer does not have one row per case")
        with _log_lock:
            for case, answer in zip(cases, answers):
                record = _base("lean-only", op, case, None, answer, None, backend_ms)
                if worker is not None:
                    worker.op(op)["lean_only"] += 1
                if _emit(record, worker) is False and worker is not None:
                    worker.op(op)["recorder_faults"] += 1
    except Exception as fault:  # noqa: BLE001 - the recorder never reaches the caller
        _fault(op, cases, fault, worker, backend_ms=backend_ms)
