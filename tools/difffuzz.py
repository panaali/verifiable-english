"""Cross-language differential fuzzer: Python, the Lean routes and Rust on seeded mutants.

Every fixture of the conformance corpus and the use cases is read into seeds, or excluded with a reason
(`tools/difffuzz_corpus.py`). A seed belongs to a *surface*, which says how each implementation runs it and
how their answers compare:

* `requests`: every route request of the fixtures (the P0 families, the v0 families, the use cases' requests
  and their models against their environments), through `conformance.three_way`: Python in process, Lean by
  the runner its environment's language takes (`LEAN_REQUESTS`: `ve_conformance route` for ve.core@0.2,
  `ve_conformance` and its `check-certificate` mode for v0), Rust by `ve conformance` where `rust_request`
  maps the case. Each implementation's own diagnostic code is compared; a text where the P0 contract fixes it
  (`three_way.KNOWN`, P0 route only).
* `environment`: every distinct environment of the fixtures, decoded by Python's `Environment`, by the Lean
  route that decodes that envelope (`lean_route`) and by Rust, each as the route table `ROUTES` says (an
  engine with no path there is named with the reason). A text is compared when either side is a decoder
  type diagnostic (`TYPE_DIAGNOSTICS`), and the environment identity when the engines report one. A route
  that names its own code (`OwnCodes`: the soft-norms route's `code`) keeps it: the code is compared with
  its Python counterpart's, and its class in the route's contract is the code compared with the others.
* `wire`: the wire-contract units (`demo@0`, `defer@0`, `forms@0`, `soft-norms@0`, `norms@0`,
  `norm-defaults@0`), by the Python engine and `ve_diagnose`; the whole diagnostic record is compared, except
  the text and args of an inherited check (the contract's `inherited` flag).

Each seed is run as it is, and its 1-fault and 2-fault mutants (`one_faults`): every JSON node replaced by
7, true, null, [], {} and "x"; an object member removed; keys and lists reversed; a list's first entry
duplicated; string values and object keys with NBSP, a double space, a tab, a carriage return, U+212A, a
dotted capital I, upper case, Arabic-Indic digits, a curly quote and a control character (U+001C); and
every array or string a wire-contract table limits resized to limit - 1, limit and limit + 1
(`limit_patterns`). An implementation takes part on an input when the surface gives it a path; an input
off the restricted wire (null, a float) is refused by every Lean and Rust package reader, so their answer
is that refusal (`framing`), which agrees with any rejection and disagrees with an acceptance.

Every row a Lean or Rust runner returns is checked against the schema its producer declares before it is
read (the `*_row_problem` checks: the Lean service schemas, the assurance manifest's runner bindings, and the
encoders' response tables `LEAN_ROUTE_FIELDS`, `RECORD_FIELDS` and `RUST_ROWS`, with each route's own code);
a row that fails is a runner that did not answer, never an answer. The row of a case a runner could not read
is `POSITION_ROW` alone: no field of the route it never ran. A runner that does not answer at all (a crash, a
hang, output that is not Unicode text or JSON) or refuses a package is a value of its own type (`NoAnswer`,
`Refused`), never a row, so nothing a runner prints can pass for either. Every answer enters the comparison
through `held`: one that cannot be kept as JSON text is a crash or no answer, never the fuzzer's exception.

A *finding* is a Python exception other than VEError, a Python call that does not finish in its CPU
budget, a Lean or Rust process that does not answer (panic, signal, hang, malformed output), or a disagreement
between the answers of the implementations that take part. Findings are grouped by signature (surface,
profile, classes and the compared answers). A signature in the reviewed baseline
(`conformance/difffuzz-baseline.json`) is known; any other is new, and is minimised (`minimise`) before it
is reported. Every baseline entry is replayed on its minimised input and must still give its recorded
answers, so a fix must shrink the baseline.

    python3 tools/difffuzz.py --ci           # seeded and bounded; tests/test_difffuzz.py runs it
    python3 tools/difffuzz.py --deep 20      # nightly: 20 times the CI sample, seeded by the date
    python3 tools/difffuzz.py --ci --update-baseline   # rewrite the baseline (then review it)

Exit status: 0 when nothing is new and every baseline entry reproduces, 1 otherwise.
"""
from __future__ import annotations

import argparse
import atexit
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
import datetime
import hashlib
import json
import os
from pathlib import Path
import random
import re
import resource
import signal
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.subprocesses import HANG_TIMEOUT, run_cpu_bounded  # noqa: E402
from tools import difffuzz_corpus as corpus  # noqa: E402

BIN = ROOT / "lean/.lake/build/bin"
BASELINE = ROOT / "conformance/difffuzz-baseline.json"
FORMAT = "ve-difffuzz-baseline@2"
ENGINES = ("python", "lean", "rust")

# The whole environment of a Lean or Rust runner: nothing from the caller's shell reaches it.
CHILD_ENV = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}

# CPU seconds one Python call or one Lean/Rust batch may spend before it counts as not answering.
PYTHON_CPU = 20
BATCH_CPU = 300
BATCH_CASES = 400

# The CI sample: 1-fault and 2-fault mutants per surface. `--deep N` multiplies both.
CI_BUDGET = {"requests": (6000, 1500), "environment": (6000, 1500), "wire": (6000, 1500)}
CHUNK = 2000
MINIMISE_EVALUATIONS = 3000
# New signatures minimised in one run; any beyond are reported as found (`"minimised": false`).
MINIMISE_LIMIT = 40
MINIMISE_BATCH = 200


def rust_binary() -> Path:
    if os.environ.get("VE_RUST_PREBUILT"):
        return Path(os.environ["VE_RUST_BINARY"])
    return ROOT / "rust/target/release/ve"


# ---------------------------------------------------------------- JSON paths

def get(root, path):
    for step in path:
        root = root[step]
    return root


def put(root, path, value):
    get(root, path[:-1])[path[-1]] = value


def walk(value, path=()):
    """Every (path, node) of a JSON value, the root first."""
    yield path, value
    if type(value) is dict:
        for key, item in value.items():
            yield from walk(item, path + (key,))
    elif type(value) is list:
        for index, item in enumerate(value):
            yield from walk(item, path + (index,))


def related(left, right):
    return left[:len(right)] == right or right[:len(left)] == left


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()[:16]


def unholdable(value):
    """Why `value` cannot be signed, reported and kept in the baseline (`canonical`, then UTF-8: a lone
    surrogate, a number JSON cannot print, a value that is not JSON), or None when it can."""
    try:
        canonical(value).encode("utf-8")
    except (TypeError, ValueError, RecursionError) as exc:
        return f"{type(exc).__name__}: {exc}"[:200]
    return None


# ---------------------------------------------------------------- mutations

TYPES = {"number": 7, "boolean": True, "null": None, "array": [], "object": {}, "string": "x"}


def _replace_first(text, olds, new):
    for index, char in enumerate(text):
        if char in olds:
            return text[:index] + new + text[index + 1:]
    return None


def _insert_space(text, space):
    """`text` with its first space replaced by `space`, or `space` inside it."""
    if " " in text:
        return text.replace(" ", space, 1)
    return text[:1] + space + text[1:]


UNICODE = {
    "nbsp": lambda s: _insert_space(s, " "),
    "double-space": lambda s: _insert_space(s, "  "),
    "tab": lambda s: _insert_space(s, "\t"),
    "cr": lambda s: s + "\r",
    "kelvin": lambda s: _replace_first(s, "kK", "K"),
    "dotted-i": lambda s: _replace_first(s, "iI", "İ"),
    "upper": lambda s: s.upper(),
    "digits": lambda s: "".join(chr(0x660 + int(c)) if c in "0123456789" else c for c in s),
    "curly-quote": lambda s: (_replace_first(s, "'", "’") or _replace_first(s, '"', "”")
                              or s + "’"),
    "control": lambda s: s + "\x1c",
}


def _resized(node, size):
    if type(node) is str:
        return (node + "a" * size)[:size] if node else "a" * size
    if not node:
        return None
    return [deepcopy(node[index % len(node)]) for index in range(size)]


def apply(root, mutation):
    """`root` with one mutation applied, or None when it does not apply. A mutation is a JSON list:
    [op, path, arg]."""
    op, path, arg = mutation[0], tuple(mutation[1]), mutation[2]
    out = deepcopy(root)
    try:
        node = get(out, path)
    except (KeyError, IndexError, TypeError):
        return None
    if op == "type":
        value = TYPES[arg]
        if type(node) is type(value) and node == value:
            return None
        if not path:
            return deepcopy(value)
        put(out, path, deepcopy(value))
    elif op == "absent":
        parent = get(out, path[:-1]) if path else None
        if type(parent) is not dict:
            return None
        del parent[path[-1]]
    elif op == "reorder":
        if type(node) is dict and len(node) > 1:
            reordered = dict(reversed(list(node.items())))
        elif type(node) is list and node != node[::-1]:
            reordered = node[::-1]
        else:
            return None
        if not path:
            return reordered
        put(out, path, reordered)
    elif op == "duplicate":
        if type(node) is not list or not node:
            return None
        node.insert(1, deepcopy(node[0]))
    elif op == "unicode":
        if type(node) is not str:
            return None
        changed = UNICODE[arg](node)
        if changed is None or changed == node:
            return None
        if not path:
            return changed
        put(out, path, changed)
    elif op == "key":
        parent = get(out, path[:-1]) if path else None
        if type(parent) is not dict:
            return None
        changed = UNICODE[arg](path[-1])
        if changed is None or changed == path[-1] or changed in parent:
            return None
        items = [(changed if key == path[-1] else key, value) for key, value in parent.items()]
        parent.clear()
        parent.update(items)
    elif op == "limit":
        if type(node) not in (str, list):
            return None
        resized = _resized(node, arg)
        if resized is None or resized == node:
            return None
        if not path:
            return resized
        put(out, path, resized)
    else:
        raise ValueError(f"unknown mutation {op}")
    return out


def apply_all(root, mutations):
    for mutation in mutations:
        root = apply(root, mutation)
        if root is None:
            return None
    return root


def limit_patterns():
    """(pattern, kind, limit) for every `max_items` and `max_bytes` check of the wire-contract tables:
    the production `soft-norms@0` contract (its limits from `ve/wire_contract/limits.json`) and each
    conformance unit (its limits from `conformance/wire-contract/contracts/limits.json`). A pattern is
    a tuple of JSON pointer tokens, `*` for any key or index; `unit` is None for the production table,
    which applies wherever its pattern matches."""
    from ve.wire_contract.engine import load
    from tests.test_wire_contract_corpus import CONTRACTS, LIMITS
    production = json.loads((ROOT / "ve/wire_contract/limits.json").read_text())
    tables = [(None, load("soft-norms@0"), production)] + [
        (unit, load(unit), production) for unit in corpus.WIRE_UNITS if unit != "soft-norms@0"] + [
        (unit, contract, LIMITS) for unit, contract in sorted(CONTRACTS.items())]
    out = []

    def resolve(pattern, items):
        if pattern.startswith("@"):
            head, _, tail = pattern.partition("/")
            base = items[int(head[1:] or 0)]
            return base + (tuple(tail.split("/")) if tail else ())
        return tuple(pattern.split("/")[1:]) if pattern else ()

    def visit(entries, items, unit, limits):
        for entry in entries:
            if "each" in entry:
                visit(entry["checks"], [resolve(entry["each"], items)] + items, unit, limits)
            elif entry.get("kind") in ("max_items", "max_bytes"):
                limit = entry["limit"]
                limit = limits[limit] if type(limit) is str else limit
                pattern = resolve(entry.get("at", "@"), items)
                out.append((unit, pattern, entry["kind"], limit))

    for unit, contract, limits in tables:
        for phase in contract["phases"]:
            visit(phase["checks"], [], unit, limits)
    return out


def _matches(pattern, path):
    return len(pattern) == len(path) and all(p == "*" or p == str(s) for p, s in zip(pattern, path))


def fault_nodes(root, protected, mutate_root=False):
    """The (path, node) pairs of `root` a mutation may change."""
    return [(path, node) for path, node in walk(root)
            if (path or mutate_root) and not any(related(path, p) and len(path) >= len(p) for p in protected)]


def node_faults(root, path, node):
    """Every 1-fault mutation of one node that changes it, but the limit ones."""
    out = []
    where = list(path)
    for kind, value in TYPES.items():
        if not (type(node) is type(value) and node == value):
            out.append(["type", where, kind])
    if path and type(path[-1]) is str:
        out.append(["absent", where, None])
        siblings = get(root, path[:-1])
        for name, change in UNICODE.items():
            changed = change(path[-1])
            if changed is not None and changed not in siblings:
                out.append(["key", where, name])
    if (type(node) is dict and len(node) > 1) or (type(node) is list and node != node[::-1]):
        out.append(["reorder", where, None])
    if type(node) is list and node:
        out.append(["duplicate", where, None])
    if type(node) is str:
        for name, change in UNICODE.items():
            changed = change(node)
            if changed is not None and changed != node:
                out.append(["unicode", where, name])
    return out


def limit_faults(nodes, limits):
    """The limit - 1, limit and limit + 1 resizings of every node a limit pattern matches."""
    out = []
    for pattern, kind, limit in limits:
        for path, node in nodes:
            if _matches(pattern, path) and type(node) is (list if kind == "max_items" else str):
                # `_resized` makes nothing of an empty list; asking it would copy the node for each size.
                out.extend(["limit", list(path), size] for size in (limit - 1, limit, limit + 1)
                           if size >= 0 and size != len(node) and (type(node) is str or node))
    return out


def one_faults(root, protected, limits, mutate_root=False):
    """Every 1-fault mutation of `root` that changes it: [op, path, arg] lists, the limit ones last."""
    nodes = fault_nodes(root, protected, mutate_root)
    return [m for path, node in nodes for m in node_faults(root, path, node)] + limit_faults(nodes, limits)


class Faults:
    """The 1-fault mutations of one seed, drawn without listing them all: a node (or the seed's limit
    resizings, as one more entry) at random, then one of its mutations at random, never the same twice."""

    def __init__(self, root, protected, limits, mutate_root):
        self.root = root
        self.nodes = fault_nodes(root, protected, mutate_root)
        self.limits = limit_faults(self.nodes, limits)
        self.used = set()

    def draw(self, rng, attempts=24):
        entries = len(self.nodes) + (1 if self.limits else 0)
        for _ in range(attempts if entries else 0):
            pick = rng.randrange(entries)
            candidates = self.limits if pick == len(self.nodes) else node_faults(self.root, *self.nodes[pick])
            if not candidates:
                continue
            mutation = candidates[rng.randrange(len(candidates))]
            key = canonical(mutation)
            if key not in self.used:
                self.used.add(key)
                return mutation
        return None


# ---------------------------------------------------------------- answers

def ok(value=None):
    return {"outcome": "ok", "value": value}


def error(code, text):
    return {"outcome": "error", "code": code, "text": text}


NOT_APPLICABLE = {"outcome": "n/a"}
# A Lean or Rust package reader's refusal of an input as a whole: it agrees with any rejection.
FRAMING = "framing"


def refusal(text):
    """A package reader's refusal: the code `framing` is how it is shown; `refused` is what makes it one,
    which no runner's own code (a Rust error code `framing`, say) can set."""
    return {**error(FRAMING, text), "refused": True}


def refused(answer):
    return answer.get("refused") is True


def malformed(problem):
    return {"outcome": "panic", "text": f"malformed row: {problem}"[:300]}


def off_wire(value):
    """Why `value` is not restricted JSON (the only input the Lean and Rust package readers take, and the
    only one the Lean and Rust backends send: `ve.wire.canonical_json` checks it so), or None when it is."""
    from ve.errors import VEError
    from ve.wire import validate_json
    try:
        validate_json(value)
        return None
    except VEError as exc:
        return exc.message


def on_wire(value):
    return off_wire(value) is None


@contextmanager
def _cpu_alarm(seconds):
    def expire(*_):
        raise _PythonBudget()
    previous = signal.signal(signal.SIGPROF, expire)
    signal.setitimer(signal.ITIMER_PROF, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.signal(signal.SIGPROF, previous)


class _PythonBudget(BaseException):
    """A Python call spent PYTHON_CPU seconds (not an answer of the implementation)."""


@contextmanager
def python_authority():
    previous = os.environ.get("VE_AUTHORITY")
    os.environ["VE_AUTHORITY"] = "python"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("VE_AUTHORITY", None)
        else:
            os.environ["VE_AUTHORITY"] = previous


def held(engine, answer):
    """`answer` as the fuzzer keeps it: every answer is signed, reported and stored as JSON text, so one
    that cannot be (`unholdable`: a diagnostic quoting a lone surrogate, say) is Python's crash, or a Lean
    or Rust runner that did not answer."""
    problem = unholdable(answer)
    if problem is None:
        return answer
    if engine == "python":
        return {"outcome": "crash", "code": "UnholdableAnswer", "text": problem}
    return {"outcome": "panic", "text": f"answer is not JSON text: {problem}"}


def call_python(function, harness):
    """Run one Python call. A VEError is the implementation's answer; any other exception raised
    inside `ve/` is a crash; one raised by the harness itself (`harness` files: a field the adapter
    reads is missing or mistyped) means the call cannot be made, and is not applicable. A call that
    spends its CPU budget is a `timeout`, which is a finding."""
    from ve.errors import VEError
    try:
        with python_authority(), _cpu_alarm(PYTHON_CPU):
            return function()
    except _PythonBudget:
        return {"outcome": "timeout"}
    except VEError as exc:
        return error(exc.code, exc.message)
    except RecursionError as exc:
        return {"outcome": "crash", "code": "RecursionError", "text": str(exc)[:200]}
    except Exception as exc:  # noqa: BLE001 - only VEError may escape; the rest is the finding
        frames = traceback.extract_tb(exc.__traceback__)
        innermost = Path(frames[-1].filename).resolve() if frames else None
        if innermost is not None and innermost.name in harness:
            return NOT_APPLICABLE
        return {"outcome": "crash", "code": type(exc).__name__, "text": str(exc)[:200]}


# ---------------------------------------------------------------- runner rows

# What a batch runner gives for one case: the row it printed (a JSON object, checked against its producer's
# schema before it is read), or one of these two. They are types of their own, so that nothing a runner
# prints can pass for one: a printed `{"framing": ...}` is a row, and a malformed one.

@dataclass(frozen=True)
class NoAnswer:
    """The runner did not answer the case: a crash, a signal, a hang, malformed output (`run_rows`)."""
    reason: str


@dataclass(frozen=True)
class Refused:
    """The runner's package reader refused the case as a whole (exit 2 with the case alone)."""
    text: str


def _exchange(command, cases):
    """(completed process, None) for one batch, or (None, the reason the runner did not answer): it could
    not be started, it did not finish within HANG_TIMEOUT, or its output is not text."""
    try:
        completed, _ = run_cpu_bounded([str(c) for c in command], json.dumps(cases, ensure_ascii=False),
                                       BATCH_CPU, env=CHILD_ENV)
    except subprocess.TimeoutExpired:
        return None, f"no answer within {HANG_TIMEOUT} s"
    except OSError as exc:
        return None, f"cannot start: {exc}"
    except UnicodeError as exc:
        return None, f"output is not UTF-8 text: {exc}"
    return completed, None


# The one-shot route executables are modes of the Lean service since lean-first batch 1 (`tests/lean_routes.py`
# `MODES`): a command naming one runs on its mode (`service_rows`); `ve_diagnose <unit>` names its unit in each case.
SERVICE_MODES = {"ve_norms_route": "norms", "ve_soft_norms_route": "soft-norms", "ve_rights_route": "rights",
                 "ve_speech_acts_route": "speech-acts", "ve_reports_route": "reports",
                 "ve_alternatives_route": "alternatives", "ve_risk_route": "risk", "ve_risk_eval": "risk-eval",
                 "ve_quantity": "quantity", "ve_norm_defaults_route": "norm-defaults",
                 "ve_discourse_route": "discourse", "ve_readings_route": "readings-route", "ve_diagnose": "diagnose"}
_SERVICE = []  # the run's one service for the route modes


def _close_service():
    while _SERVICE:
        _SERVICE.pop().close()


atexit.register(_close_service)


def service_rows(command, cases):
    """One row per case from the service mode of the one-shot route `command` names, each checked by the
    service client against the mode's schema (its binding included), or `NoAnswer`: a batch the service
    does not answer is split until the case is alone, as `run_rows` splits a runner's. A case alone that
    the service refuses as a request (the one-shot's package refusal) is `Refused`. The mode's CPU deadline
    stops a runaway case (`lean_service.DEADLINES`)."""
    from ve.backends.lean_service import LeanService
    from ve.errors import CheckerUnavailable, VEError
    if not cases:
        return []
    mode = SERVICE_MODES[Path(str(command[0])).name]
    sent = [{**case, "unit": str(command[1])} for case in cases] if mode == "diagnose" else cases
    try:
        if not _SERVICE:
            _SERVICE.append(LeanService())
        return _SERVICE[0].run(mode, sent)
    except CheckerUnavailable as exc:
        _close_service()
        if len(cases) == 1:
            return [NoAnswer(f"{type(exc).__name__}: {exc}"[:300])]
    except VEError as exc:
        if len(cases) == 1:
            return [Refused(str(exc)[-300:])]
    middle = len(cases) // 2
    return service_rows(command, cases[:middle]) + service_rows(command, cases[middle:])


def run_rows(command, cases):
    """One row per case from a batch runner, or `NoAnswer`: a batch that does not answer is split until
    the case that does not answer is alone. A batch answers when it prints one object per case, in
    order, each naming its case (`bind_rows`), and its exit status is 1 exactly when some row is an error
    (the one-shot runner contract, `ve/backends/lean.py`). A case alone that the runner refuses as a
    package (exit 2) is `Refused`. A command naming a one-shot route runs on its service mode
    (`service_rows`)."""
    if not cases:
        return []
    if Path(str(command[0])).name in SERVICE_MODES:
        return service_rows(command, cases)
    completed, reason = _exchange(command, cases)
    if reason is None:
        rows, reason = _read_batch(completed, cases)
        if reason is None:
            return rows
    if len(cases) == 1:
        if completed is not None and completed.returncode == 2:
            # The runner refused the package (framing): an answer, compared with Python's.
            return [Refused(completed.stderr.strip()[-300:] or completed.stdout.strip()[-300:])]
        return [NoAnswer(reason)]
    middle = len(cases) // 2
    return run_rows(command, cases[:middle]) + run_rows(command, cases[middle:])


def _read_batch(completed, cases):
    """(rows bound to `cases`, None), or (None, why the batch's output is not an answer)."""
    if completed.returncode not in (0, 1):
        return None, f"exit {completed.returncode}: {completed.stderr[-300:]}"
    if "PANIC" in completed.stderr or "panicked" in completed.stderr:
        return None, f"panic: {completed.stderr[-300:]}"
    from ve.backends.lean_service import _decode_json
    try:
        # The runners' reader: a string that is not Unicode text (a `\ud800` escape) is no answer.
        rows = _decode_json(completed.stdout)
    except UnicodeError:
        return None, "output is not Unicode text: a string holds a lone surrogate"
    except (ValueError, RecursionError):
        rows = None
    if type(rows) is not list or len(rows) != len(cases) or not all(type(r) is dict for r in rows):
        return None, f"malformed output: {completed.stdout[:200]}"
    bound = bind_rows(rows, cases)
    if bound is None:
        return None, "rows out of order"
    if (completed.returncode == 1) != any(r.get("status") == "error" for r in rows):
        return None, f"exit status {completed.returncode} disagrees with the rows"
    return bound, None


def _bound(row, case, index):
    """Whether a row names its case: by its id, or (an error row of a case the runner could not read) by
    its position, with JSON types kept apart (`false` is not case 0)."""
    if "id" in row:
        return row["id"] == case.get("id") and type(row["id"]) is type(case.get("id"))
    return row.get("status") == "error" and type(row.get("case_index")) is int and row["case_index"] == index


def bind_rows(rows, cases):
    """The rows, as printed, when each names its case (`_bound`), else None. A row that names its case by
    position (`case_index`) is the error of a case the runner could not read; it keeps that form, so its
    check knows the runner never ran the case's route."""
    if not all(_bound(row, case, index) for index, (row, case) in enumerate(zip(rows, cases))):
        return None
    return list(rows)


def batched(command, cases):
    rows = []
    for start in range(0, len(cases), BATCH_CASES):
        rows.extend(run_rows(command, cases[start:start + BATCH_CASES]))
    return rows


def panic(row):
    """The answer of a case the runner did not answer or refused, or None for a printed row."""
    if type(row) is Refused:
        return refusal(row.text)
    if type(row) is NoAnswer:
        return {"outcome": "panic", "text": row.reason}
    return None


# ---------------------------------------------------------------- responses

# Response types: the assurance manifest's (`ve/backends/lean.py` `conforms`): bool, nat, string, object,
# json, array<T>.
LEAN_ENVELOPE = {}  # the one-shot runner row contract alone (status, error, id), `row_problem`

# The ok rows of the Lean routes that decode an environment, by route: their encoders' fields
# (`lean/VE/<Route>/Run.lean`); `tests/test_difffuzz.py` checks them against genuine rows.
_ELABORATED = {"background": "array<json>", "conflict_targets": "array<json>", "fragment": "bool",
               "order": "array<json>", "premises": "array<json>"}
_ALTERNATIVES = {**_ELABORATED, "alternatives": "array<json>", "base_premises": "array<json>",
                 "followable": "object", "inlined": "array<json>", "legend": "array<json>",
                 "unmapped_obligations": "array<json>"}
LEAN_ROUTE_FIELDS = {
    "alternatives": {**_ALTERNATIVES, "profile_exists": "object"},
    "risk": {**_ALTERNATIVES, "document_hash": "string", "e_risk": "object", "environment_id": "string",
             "risk_premises": "array<json>", "unranked_severities": "array<json>"},
    "soft-norms": {**_ELABORATED, "colliding_pairs": "array<json>", "conditional_on": "array<json>",
                   "decisions": "array<json>", "derived": "array<json>", "environment_prime": "object",
                   "warnings": "array<json>"},
    "norm-defaults": {**_ELABORATED, "fill": "array<json>", "fragment_fill": "bool", "reached": "array<json>",
                      "unsaid": "array<json>", "unspecified": "array<json>"},
    "speech": {"commands": "array<json>", "dormant": "array<json>", "environment_id": "string",
               "legend": "array<json>", "policy": "object", "premises": "array<json>", "queries": "array<json>",
               "questions": "array<json>", "scope": "object"},
    "reports": {"bridge_formulas": "array<json>", "content_ids": "array<json>", "envelope": "object",
                "environment_reports_id": "string", "keys": "array<json>", "open_terms": "array<json>",
                "premises": "array<json>", "warnings": "array<json>"},
    # `lean/VE/Time/Wire.lean` `runCase`, kind `admission`.
    "quantity": {"assurance": "string", "Q": "json", "core": "json", "meaning_id": "string",
                 "core_meaning_id": "string", "environment_id": "string", "target_environment_id": "string"},
}

# The diagnostic record of a wire contract (`ve/wire_contract/engine.py`, the `Fault` record), which
# `ve_diagnose` emits for the same contract.
RECORD_FIELDS = {"contract": "string", "revision": "nat", "check": "string", "phase": "string",
                 "code": "string", "class": "string", "path": "string", "text": "string", "args": "object"}

# Rust `ve conformance` rows by request kind: (the statuses of an answer, its fields, counted fields);
# the encoders are `rust/ve-core/src/order.rs` and the core dispatch. An error row is `{"id", "status": "error",
# "error": {"code", "message"}}`.
RUST_ROWS = {
    "label": ({"ok"}, {"label": "string"}, {}),
    "dependency-order": ({"ok"}, {"order": "array<string>"}, {}),
    "evaluate": ({"ok"}, {"values": "array<bool>"}, {"values": "case.ast"}),
    "parse": ({"ok"}, {"ast": "json", "canonical": "string", "meaning_id": "string"}, {}),
    "countermodel": ({"ok", "Valid", "NotCountermodel"}, {"valid": "bool"}, {}),
    "search": ({"Found", "NotFound", "ResourceLimit"}, {"model": "json"}, {}),
}


def rust_operation(case):
    """The operation `ve conformance` reads a case as, by its fields (`rust/ve-core/src/order.rs`
    `order_case` and the core dispatch): a named kind, else premises and a conclusion are a countermodel
    check with a model and a search without, else a document is evaluated with a model and parsed
    without."""
    kind = case.get("kind")
    if kind in ("label", "dependency-order", "countermodel"):
        return kind
    if "premises" in case and "conclusion" in case:
        return "countermodel" if "model" in case else "search"
    return "evaluate" if "model" in case else "parse"


def manifest_bindings(executable, mode, kinds):
    """Every binding the assurance manifest declares for a Lean runner call (`ve/assurance-manifest.json`):
    the response fields and counts its `ok` rows carry."""
    from ve.assurance import OPERATIONS
    return [binding for op in OPERATIONS.values() for binding in (op.get("lean") or {}).get("bindings", ())
            if binding["executable"] == executable and binding["mode"] == mode
            and set(binding.get("kinds", ())) == set(kinds)]


def lean_row_problem(case, row, index, response=LEAN_ENVELOPE, counts=None, coded=False):
    from ve.backends.lean import row_problem
    return row_problem(case, row, index, response, counts, coded=coded)


def route_row_problem(case, row, index):
    """A `ve_conformance route` row against the service's `route` schema, which tests/test_lean_service_schema.py
    checks against the Lean decoders (`ve_response_decode`)."""
    from ve.backends.service_schema import Invalid, check_row
    checked_row = row
    if type(row) is dict and case.get("kind") == "certificate" and row.get("status") == "ok":
        if "steps" in row:
            return "one-shot route certificate unexpectedly carries service steps"
        # The frozen one-shot projection omits this service-only display field.
        checked_row = {**row, "steps": 0}
    try:
        check_row("route", checked_row, case, index)
    except Invalid as exc:
        return str(exc)
    return None


def bound_row_problem(executable, mode, kinds):
    """A row checked against every manifest binding of the call; a call with none declared is an error of
    the fuzzer's table, not a row problem."""
    bindings = manifest_bindings(executable, mode, kinds)
    assert bindings, f"no manifest binding for {executable} {mode or '(default)'} {kinds}"

    def check(case, row, index):
        for binding in bindings:
            problem = lean_row_problem(case, row, index, binding["response"], binding.get("counts"))
            if problem:
                return problem
        if row["status"] != "error":
            return None
        # The runner's error rows (`lean/Main.lean`) carry nothing but the error, and in the certificate
        # mode `valid: false` (`CertificateWire.runCaseReported`).
        if row.get("valid", False) is not False:
            return "an error row says its certificate is valid"
        valid = ("valid",) if mode in ("check-certificate", "order") else ()
        return closed_row_problem(row, {}, valid, valid)
    return check


def fields_row_problem(fields, counts=None):
    def check(case, row, index):
        return lean_row_problem(case, row, index, fields, counts)
    return check


# The row every Lean runner prints for a case it could not read (`JsonInput.parseCases` gave an error:
# `lean/Main.lean`, each route's `main`, `Service/Protocol.lean`; `ResponseDecode.lean` reads it so): it
# never ran the case's route, so it carries none of the route's fields. `lean/Main.lean` alone adds
# `valid: false` in its certificate and order modes.
POSITION_ROW = ("status", "case_index", "error")


def closed_row_problem(row, response, error_fields=(), position_fields=()):
    """The fields of a row its producer does not print, or None: an ok row is its id, status and
    `response`; an error row of a case the runner ran its id, status, error and at most `error_fields`;
    the error row of a case it could not read (named by position) `POSITION_ROW` and at most
    `position_fields`, never a field of the route it did not run."""
    if row["status"] == "ok":
        allowed = {"id", "status", *response}
    elif "id" in row:
        allowed = {"id", "status", "error", *error_fields}
    else:
        allowed = {*POSITION_ROW, *position_fields}
    extra = sorted(set(row) - allowed)
    return f"a row has fields its producer does not print: {extra}" if extra else None


def route_row_check(name):
    """The check of the rows of a Lean block route that decodes an environment (`ROUTES`): the one-shot
    runner contract; the encoder's ok fields (`LEAN_ROUTE_FIELDS`) and no other field; and, where the
    route names its own code (`OwnCodes`), that code on every error row of a case it ran: a string
    among its contract's codes. The row of a case the route could not read names no code
    (`closed_row_problem`)."""
    fields, own = LEAN_ROUTE_FIELDS[name], ROUTES[name].own
    error_fields = (own.field,) if own else ()
    # The one-shot reader takes a code only from a route whose rows name one (`identity_problem`).
    coded = own is not None and own.field == "code"

    def check(case, row, index):
        problem = (lean_row_problem(case, row, index, fields, coded=coded)
                   or closed_row_problem(row, fields, error_fields, ()))
        if problem or own is None or row["status"] != "error" or "id" not in row:
            return problem
        code = row.get(own.field)
        if type(code) is not str or code not in own.codes():
            return f"an error row has no {own.contract} code in {own.field!r}"
        return None
    return check


def rust_row_problem(kind):
    from ve.backends.lean import conforms
    statuses, fields, counts = RUST_ROWS[kind]

    def check(case, row, index):
        if type(row) is not dict:
            return "a result row is not an object"
        if row.get("id") != case.get("id") or type(row.get("id")) is not type(case.get("id")):
            return "result ids do not match the submitted cases"
        status = row.get("status")
        if status == "error":
            problem = row.get("error")
            if type(problem) is not dict or type(problem.get("code")) is not str or \
                    type(problem.get("message")) is not str:
                return "an error row has no error code and message"
            return closed_row_problem(row, {})
        if type(status) is not str or status not in statuses:
            return f"a result row has no status of {sorted(statuses | {'error'})}"
        for name, spec in fields.items():
            if name not in row or not conforms(row[name], spec):
                return f"an answer has no well-formed {name!r} ({spec})"
        for name, reference in counts.items():
            source, _, counted = reference.partition(".")
            other = (case if source == "case" else row).get(counted)
            if type(other) is not list or len(row[name]) != len(other):
                return f"an answer's {name!r} does not count {reference}"
        return None
    return check


def diagnose_row_problem(case, row, index):
    from ve.backends.lean import conforms
    problem = lean_row_problem(case, row, index)
    if problem or row["status"] == "error":
        # `Diagnose.lean`: an error row is the adapter's error alone.
        return problem or closed_row_problem(row, {})
    if row.get("outcome") == "clean":
        return None if set(row) == {"id", "status", "outcome"} else "a clean row has other fields"
    # `lean/VE/WireContract/Diagnose.lean` `diagnoseCase`: `clean`, or `fault` with one record.
    record = row.get("diagnostic")
    if row.get("outcome") != "fault" or set(row) != {"id", "status", "outcome", "diagnostic"}:
        return "an ok row is neither clean nor one fault"
    if type(record) is not dict or set(record) != set(RECORD_FIELDS):
        return f"a diagnostic is not a record of {sorted(RECORD_FIELDS)}"
    for name, spec in RECORD_FIELDS.items():
        if not conforms(record[name], spec):
            return f"a diagnostic has no well-formed {name!r} ({spec})"
    return None


def checked(problem_of, case, row):
    """(the row, None) when the runner printed a well-formed answer; else (None, the answer it is
    instead): its refusal, its not answering, or the reason the row is not an answer (`malformed`). A
    row that names its case by position was bound to it by that position (`bind_rows`)."""
    if type(row) in (NoAnswer, Refused):
        return None, panic(row)
    problem = problem_of(case, row, row["case_index"] if "id" not in row else 0)
    return (row, None) if problem is None else (None, malformed(problem))


# ---------------------------------------------------------------- surfaces

@dataclass
class Seed:
    surface: str
    profile: str          # the route or unit: findings are counted by it
    id: str
    root: object
    engines: tuple = ENGINES
    meta: dict = field(default_factory=dict)


class Surface:
    name = ""
    protected: tuple = ()
    mutate_root = False
    env_prefix: tuple | None = None
    harness = frozenset({"difffuzz.py"})

    def seeds(self) -> list[Seed]:
        raise NotImplementedError

    def close(self):
        """Stop what the surface keeps running between batches."""

    def profile(self, seed, root):
        """The route or unit an input takes: findings are counted and signed by it."""
        return seed.profile

    def path(self, engine, seed, root):
        """Whether `engine` has a path for the input `root` of `seed`."""
        return engine in seed.engines

    def limits(self, seed):
        out = []
        for unit, pattern, kind, limit in LIMITS():
            if unit is None and self.env_prefix is not None and pattern[:1] == ("environment",):
                out.append((self.env_prefix + pattern[1:], kind, limit))
            elif unit is None and self.name == "wire" and seed.profile == "soft-norms@0":
                out.append((pattern, kind, limit))
            elif unit is not None and seed.profile == unit:
                out.append((pattern, kind, limit))
        return out

    def answers(self, items):
        """{engine: answer} for each (seed, root): every engine of `ENGINES` answers, `n/a` when it has
        no path for the input (`path`); each of Lean and Rust answers its items in batches, and the input
        off the restricted wire gets every package reader's refusal (`framing`) without being sent."""
        out = [{} for _ in items]
        off = [off_wire(root) for _, root in items]
        for engine in ENGINES:
            chosen = []
            for index, (seed, root) in enumerate(items):
                if not self.path(engine, seed, root):
                    out[index][engine] = NOT_APPLICABLE
                elif engine != "python" and off[index] is not None:
                    out[index][engine] = refusal(off[index])
                else:
                    chosen.append(index)
            if not chosen:
                continue
            if engine == "python":
                results = [self.python(*items[index]) for index in chosen]
            else:
                results = getattr(self, engine)([items[index] for index in chosen])
            for index, answer in zip(chosen, results):
                out[index][engine] = held(engine, answer)
        return out

    def text_fixed(self, seed, left, right):
        """Whether a contract fixes the text of two engines' errors of one code: (engine, answer)."""
        raise NotImplementedError

    def error_key(self, answer):
        """What of an error the contract fixes beyond its code."""
        return answer.get("text")

    def value_compared(self, seed, engine):
        return True

    def equivalent(self, seed, left, right):
        """Whether two engines' different answers, each (engine, answer), mean the same under the
        surface's contract."""
        return False


_LIMITS = None


def LIMITS():
    global _LIMITS
    if _LIMITS is None:
        _LIMITS = limit_patterns()
    return _LIMITS


# Requests -----------------------------------------------------------------------

V0_LANGUAGES = ("ve.core@0", "ve.core@0.1")

# The Lean runner that answers each request kind, by its environment's language family (v0: ve.core@0 and
# ve.core@0.1; core: every other language): the `ve_conformance` mode, or None with the reason.
LEAN_REQUESTS = {
    "core": {kind: "route" for kind in ("label", "dependency-order", "admission", "background", "evaluate",
                                         "countermodel", "certificate")},
    "v0": {"evaluate": "", "countermodel": "", "certificate": "check-certificate"},
}
NO_LEAN = {
    ("core", "search"): "the route checks a search's model only as a countermodel",
    ("v0", "search"): "the v0 runner checks a search's model only as a countermodel",
    ("v0", "label"): "labels are a ve.core@0.2 route kind",
    ("v0", "dependency-order"): "dependency orders are a ve.core@0.2 route kind",
    ("v0", "admission"): "admission is a ve.core@0.2 route kind",
    ("v0", "background"): "Background is a ve.core@0.2 route kind",
}
REQUEST_VALUES = {"label": ("label",), "dependency-order": ("order",), "evaluate": ("values",),
                  "countermodel": ("refutes",), "search": ("found", "model"), "certificate": ("valid",),
                  "background": ("background", "generators"),
                  "admission": ("admitted", "report", "report_id", "kinds")}
# The v0 wire takes these kinds without a `kind` member (the manifest bindings' `kinds: []`).
V0_UNKINDED = ("evaluate", "certificate")


def language_family(environment):
    language = environment.get("language") if type(environment) is dict else None
    return "v0" if language in V0_LANGUAGES else "core"


def lean_request(seed, root):
    """The Lean case for an input and the mode it goes to (its seed's runner)."""
    mode = seed.meta["lean"]
    case = dict(root)
    if seed.meta["family"] == "v0" and case.get("kind") in V0_UNKINDED:
        del case["kind"]
    return mode, case


def lean_row_check(seed, case):
    family, kind, mode = seed.meta["family"], seed.meta["kind"], seed.meta["lean"]
    if mode == "route":
        return route_row_problem
    kinds = [] if kind in V0_UNKINDED else [kind]
    return bound_row_problem("ve_conformance", mode, kinds)


class Requests(Surface):
    """Every route request of the fixtures (`difffuzz_corpus.requests`)."""
    name = "requests"
    protected = (("id",), ("kind",), ("max_domain_size",))
    env_prefix = ("environment",)
    harness = frozenset({"difffuzz.py", "three_way.py"})

    def seeds(self):
        from conformance.three_way import python_verdict, rust_request
        out = []
        for origin, kind, case, expected in corpus.requests():
            family = language_family(case["environment"])
            mode = LEAN_REQUESTS[family].get(kind)
            root = {"id": origin, **case}
            if expected is None and kind == "certificate":
                # Rust's certificate verdict is a bounded search: it takes part when the certificate is valid.
                verdict = call_python(lambda: python_verdict(deepcopy(root)), self.harness)
                expected = {"valid": verdict.get("valid") is True}
            engines = ["python"] + (["lean"] if mode is not None else [])
            template = rust_request({**root, "expected": expected or {}})
            rust = None
            if template is not None:
                engines.append("rust")
                # The fields Rust's case reads from the input, and the ones `rust_request` sets itself.
                rust = {"fields": [k for k in template if k in root],
                        "constants": {k: v for k, v in template.items() if k not in root},
                        "operation": rust_operation(template)}
            stem = origin.split("/")[1].split(".json")[0] if origin.startswith("conformance/") else \
                "usecase:" + origin.split("/")[1]
            out.append(Seed("requests", f"{stem}:{kind}", origin, root, tuple(engines),
                            {"kind": kind, "family": family, "lean": mode, "rust": rust}))
        return out

    def _verdict(self, seed, verdict):
        if verdict["status"] == "error":
            return {**error(verdict["diagnostic_code"], verdict["error"]),
                    **({"generator": verdict["generator"]} if "generator" in verdict else {})}
        return ok({key: verdict.get(key) for key in REQUEST_VALUES[seed.meta["kind"]]})

    def python(self, seed, root):
        from conformance.three_way import python_verdict
        answer = call_python(lambda: python_verdict(deepcopy(root)), self.harness)
        return self._verdict(seed, answer) if "status" in answer else answer

    def lean(self, items):
        from conformance.three_way import error_verdict
        by_mode = {}
        for index, (seed, root) in enumerate(items):
            mode, case = lean_request(seed, root)
            by_mode.setdefault(mode, []).append((index, {**case, "id": str(index)}))
        out = [None] * len(items)
        for mode, group in by_mode.items():
            command = [BIN / "ve_conformance", *([mode] if mode else []), "-"]
            rows = batched(command, [case for _, case in group])
            for (index, case), row in zip(group, rows):
                seed, root = items[index]
                row, bad = checked(lean_row_check(seed, case), case, row)
                if bad:
                    out[index] = bad
                elif row["status"] == "error":
                    out[index] = self._verdict(seed, error_verdict(None, row["error"], row.get("generator")))
                else:
                    out[index] = ok({key: row.get(key) for key in REQUEST_VALUES[seed.meta["kind"]]})
        return out

    def rust_case(self, seed, root):
        """The Rust case of an input: the fields its seed's request reads (`rust_request` on the seed),
        each taken from the input where the input has it, and the ones `rust_request` sets."""
        rust = seed.meta["rust"]
        return {**{key: root[key] for key in rust["fields"] if key in root}, **rust["constants"]}

    def rust(self, items):
        from conformance.three_way import rust_verdict
        cases = [{**self.rust_case(seed, root), "id": str(index)} for index, (seed, root) in enumerate(items)]
        out = []
        for (seed, root), case, row in zip(items, cases, batched([rust_binary(), "conformance"], cases)):
            kind = seed.meta["kind"]
            operation = rust_operation(case)
            row, bad = checked(rust_row_problem(operation), case, row)
            if bad:
                out.append(bad)
            elif row["status"] != "error" and operation != seed.meta["rust"]["operation"]:
                # A field the mutant dropped makes Rust read another request (a document parsed, not
                # evaluated): Rust accepted the input, and its answer has nothing to compare.
                out.append(ok(None))
            else:
                out.append(self._verdict(seed, rust_verdict({"kind": kind}, row)))
        return out

    def value_compared(self, seed, engine):
        # Rust's certificate verdict is a bounded search, not a replay (three-way test, plan 3.7).
        return not (engine == "rust" and seed.meta["kind"] == "certificate")

    def equivalent(self, seed, left, right):
        # A certificate the Lean route rejects is an invalid certificate (`three_way.lean_verdict`): any
        # rejection but an unsupported profile or a resource limit means `valid: false`. Rust's
        # certificate answer is a bounded search that never reads the certificate, so the Lean route's
        # rejection of a certificate does not contradict it (Python's rejections are compared with it).
        if seed.meta["kind"] != "certificate":
            return False
        for (rejecter, x), (engine, y) in ((left, right), (right, left)):
            if x["outcome"] == "error" and x.get("code") not in ("UnsupportedProfile", "ResourceLimit") \
                    and y["outcome"] == "ok":
                if engine == "rust":
                    return rejecter == "lean"
                return (y.get("value") or {}).get("valid") is False
        return False

    def text_fixed(self, seed, left, right):
        from conformance.three_way import KNOWN
        return seed.meta["lean"] == "route" and left[1]["code"] in KNOWN

    def error_key(self, answer):
        # The P0 contract fixes an InvalidModel's generator, not its text.
        return answer.get("generator") if answer.get("code") == "InvalidModel" else answer.get("text")


# Environment --------------------------------------------------------------------

# Lean's decoder type diagnostics (`Json.getStr?`, `getArr?`, `getObj?`, `profilesOf` and the block
# decoders) as `checker_error` reads them: where either side gives one, the texts must be equal (the
# env-profiles directive).
TYPE_DIAGNOSTICS = {
    ("InvalidInput", "String expected"), ("InvalidInput", "array expected"),
    ("InvalidInput", "object expected"),
    ("UnsupportedProfile", "profiles must be a sorted unique array"),
    ("InvalidInput", "InvalidInput: speech_acts block"), ("InvalidInput", "InvalidInput: alternatives.block"),
    ("InvalidInput", "InvalidInput: risk.block"), ("InvalidInput", "units must be an object"),
    ("InvalidInput", "InvalidInput: environment vocabulary"),
}

TOP_QUANTITY = {"format": "ve-quantity@1", "formula": ["top"]}


@dataclass(frozen=True)
class OwnCodes:
    """A Lean route whose error rows name the producer's own code, in `field`. The code is one of the
    wire contract `contract`'s `codes`, whose `class` is the code compared with an engine that does not
    speak the contract; `python` is Python's counterpart of the route, which raises the same codes, so
    the own codes are compared too (`own` in an answer: the code, or None for an acceptance)."""
    contract: str
    python: object
    field: str = "code"

    def codes(self):
        return contract_codes(self.contract)


_CONTRACT_CODES = {}


def contract_codes(contract):
    """{code: {class, summary}} of a production wire contract (`ve/wire_contract/<contract>.json`)."""
    if contract not in _CONTRACT_CODES:
        from ve.wire_contract.engine import load
        _CONTRACT_CODES[contract] = load(contract)["codes"]
    return _CONTRACT_CODES[contract]


def _soft_route_python(environment):
    """Python's counterpart of the soft-norms route's `soft-elaborate` decode with no norms
    (`conformance/soft_norms.py` `compare_near_limit` holds its code equal to the route's)."""
    from ve.softnorms import load_soft_document
    load_soft_document(environment, [])


@dataclass(frozen=True)
class Route:
    """How each engine decodes one kind of environment. `lean` is the Lean executable and the case fields
    that make it decode the environment and nothing else to fail (`ve_service` is the service's
    `environment` mode); `rust` builds Rust's case for an environment, or is None with `no_rust` the
    reason. `identity`: the engines report the environment identity. `own`: the route's own codes."""
    lean: str
    case: dict | None
    rust: object = None
    no_rust: str = ""
    identity: bool = False
    own: OwnCodes | None = None


def _rust_label(env):
    return {"kind": "label", "label": "asserted", "environment": env}


ROUTES = {
    "envelope": Route("ve_service", None, _rust_label, identity=True),
    "alternatives": Route("ve_alternatives_route", {"kind": "alt-elaborate", "norms": []},
                          no_rust="Rust reads the four core envelope fields only (no alternatives block)"),
    "risk": Route("ve_risk_route", {"kind": "risk-elaborate", "document": {"norms": []}},
                  no_rust="Rust reads the four core envelope fields only (no risk block)"),
    "soft-norms": Route("ve_soft_norms_route", {"kind": "soft-elaborate", "norms": []}, _rust_label,
                        own=OwnCodes("soft-norms@0", _soft_route_python)),
    "speech": Route("ve_speech_acts_route", {"kind": "speech-elaborate", "document": {"units": []}},
                    no_rust="Rust reads the four core envelope fields only (no speech-acts block)"),
    "reports": Route("ve_reports_route", {"kind": "reports-elaborate", "document": {"units": []}},
                     no_rust="Rust reads the four core envelope fields only (no reports profile)"),
    "norm-defaults": Route("ve_norm_defaults_route", {"kind": "norm-defaults-elaborate", "norms": []},
                           no_rust="Rust evaluates Python's filled premise lists only (conformance/norm_defaults.py)"),
    "quantity": Route("ve_quantity", {"kind": "admission", "quantity": TOP_QUANTITY},
                      no_rust="Lean owns W6 (Lean-first batch 9 deleted Rust's quantity route)", identity=True),
}

# The block route each profile takes, first match first; then the blocks an envelope carries when its
# profiles are not an array of strings.
PROFILE_ROUTES = (("risk@0", "risk"), ("alternatives@0", "alternatives"), ("speech-acts@0", "speech"),
                  ("reports@0", "reports"), ("soft-norms@0", "soft-norms"), ("norm-defaults@0", "norm-defaults"))
BLOCK_ROUTES = (("risk", "risk"), ("alternatives", "alternatives"), ("speech_acts", "speech"))


def lean_route(data):
    """The Lean route that decodes an environment, read from the environment itself: a frozen
    envelope's language and every envelope no block route takes go to the service's `environment`
    mode ("envelope"); otherwise the profiles choose when they are an array of strings, else the
    blocks the envelope carries; then the W6 fields choose the quantity route."""
    if type(data) is not dict:
        return "envelope"
    if data.get("language") in V0_LANGUAGES:
        return "envelope"
    profiles = data.get("profiles")
    if type(profiles) is list and all(type(p) is str for p in profiles):
        chosen = [route for profile, route in PROFILE_ROUTES if profile in profiles]
    else:
        chosen = [route for block, route in BLOCK_ROUTES if block in data]
    if chosen:
        return chosen[0]
    return "quantity" if {"unit_schema", "units"} & set(data) else "envelope"


class EnvironmentSurface(Surface):
    """Every distinct environment of the fixtures (`difffuzz_corpus.environments`), each decoded by every
    engine its route gives a path (`ROUTES`), whether or not that engine accepts the seed."""
    name = "environment"
    env_prefix = ()
    mutate_root = True

    def __init__(self):
        self._lean_service = None

    def close(self):
        if self._lean_service is not None:
            self._lean_service.close()
            self._lean_service = None

    def seeds(self):
        return [Seed("environment", lean_route(env), origin, env) for origin, env in corpus.environments()]

    def profile(self, seed, root):
        return lean_route(root)

    def path(self, engine, seed, root):
        return engine != "rust" or ROUTES[lean_route(root)].rust is not None

    def python(self, seed, root):
        """`Environment`'s answer; on a route with its own codes, with Python's own code for the route
        (`own`), from the route's Python counterpart."""
        from ve.environment import Environment

        def decode():
            return ok({"environment_id": Environment(deepcopy(root)).environment_id})
        answer = call_python(decode, self.harness)
        own = ROUTES[lean_route(root)].own
        if own is None or answer["outcome"] not in ("ok", "error"):
            return answer

        def counterpart():
            own.python(deepcopy(root))
            return ok()
        mirrored = call_python(counterpart, self.harness)
        if mirrored["outcome"] in ("crash", "timeout"):
            return mirrored  # the counterpart's crash or timeout is the finding
        return {**answer, "own": mirrored.get("code")} if mirrored["outcome"] in ("ok", "error") else answer

    def lean(self, items):
        from ve.backends.diagnostics import checker_error
        roots = [root for _, root in items]
        by_route = {}
        for index, root in enumerate(roots):
            by_route.setdefault(lean_route(root), []).append(index)
        out = [None] * len(roots)
        for name, indices in by_route.items():
            route = ROUTES[name]
            if route.case is None:
                cases = [{"id": str(i), "environment": roots[i]} for i in indices]
                # The service client checks each row against the service's `environment` schema too.
                rows = self._service(cases)
                problem_of = fields_row_problem({"environment_id": "string"})
            else:
                cases = [{"id": str(i), "environment": roots[i], **route.case} for i in indices]
                rows = batched([BIN / route.lean, "-"], cases)
                problem_of = route_row_check(name)
            for i, case, row in zip(indices, cases, rows):
                row, bad = checked(problem_of, case, row)
                if bad:
                    out[i] = bad
                elif row["status"] == "error" and route.own is not None and "id" in row:
                    # The route's own code is kept; the code compared with Python's `Environment` and Rust
                    # is its class in the route's contract.
                    own = row[route.own.field]
                    out[i] = {**error(route.own.codes()[own]["class"], row["error"]), "own": own}
                elif row["status"] == "error":
                    # The other routes' texts carry their code, read as the Lean backend reads it.
                    diagnostic = checker_error(row["error"]).to_dict()
                    out[i] = error(diagnostic["code"], diagnostic["message"])
                else:
                    out[i] = ok({"environment_id": row["environment_id"]} if route.identity else None)
                    if route.own is not None:
                        out[i]["own"] = None
        return out

    def _service(self, cases):
        """The Lean service's `environment` mode (the envelope decoder), one row per case, checked by the
        service client against the service schemas; a batch the service does not answer well is split
        until the case is alone, and that case did not answer."""
        from ve.backends.lean_service import LeanService
        try:
            if self._lean_service is None:
                self._lean_service = LeanService(timeout=HANG_TIMEOUT)
                self._lean_service.start()
            return self._lean_service.run("environment", cases)
        except Exception as exc:  # noqa: BLE001 - CheckerUnavailable (a malformed response) or a crash
            self.close()
            if len(cases) == 1:
                return [NoAnswer(f"{type(exc).__name__}: {exc}"[:300])]
            middle = len(cases) // 2
            return self._service(cases[:middle]) + self._service(cases[middle:])

    def rust(self, items):
        cases = [{**ROUTES[lean_route(root)].rust(root), "id": str(i)} for i, (_, root) in enumerate(items)]
        out = []
        for case, row in zip(cases, batched([rust_binary(), "conformance"], cases)):
            row, bad = checked(rust_row_problem(case["kind"]), case, row)
            if bad:
                out.append(bad)
            elif row["status"] == "error":
                out.append(error(row["error"]["code"], row["error"]["message"]))
            else:
                out.append(ok(None))
        return out

    def text_fixed(self, seed, left, right):
        # The env-profiles directive fixes Python's text to Lean's type diagnostics; no contract
        # fixes Rust's decoder texts.
        if {left[0], right[0]} != {"python", "lean"}:
            return False
        return any((answer["code"], answer["text"]) in TYPE_DIAGNOSTICS for _, answer in (left, right))


# Wire contract -------------------------------------------------------------------

class Wire(Surface):
    name = "wire"
    env_prefix = None

    def __init__(self):
        self._inherited_cache = {}
        self._engines = {}

    def seeds(self):
        from tests.test_wire_contract_corpus import CASES
        from tests.test_wire_contract_lean import DEFER
        from tests.test_wire_contract_three_way import FORMS
        from tests.test_wire_contract_soft_lean import fixture_sources
        out = [Seed("wire", "demo@0", f"demo@0/{name}", root, ("python", "lean")) for name, root, _ in CASES]
        out += [Seed("wire", "defer@0", f"defer@0/{name}", root, ("python", "lean"))
                for name, (root, _) in DEFER.items()]
        out += [Seed("wire", "forms@0", f"forms@0/{name}", root, ("python", "lean"))
                for name, (root, _) in FORMS.items()]
        soft = {}
        for index, (environment, norms) in enumerate(fixture_sources()):
            soft.setdefault(canonical([environment, norms]), (f"fixture/{index}", environment, norms))
        for test, environment, norms in json.loads(
                (ROOT / "conformance/wire-contract/soft-norms@0-test-inputs.json").read_text()):
            soft.setdefault(canonical([environment, norms]), (test, environment, norms))
        out += [Seed("wire", "soft-norms@0", f"soft-norms@0/{name}", {"environment": e, "norms": n},
                     ("python", "lean")) for name, e, n in soft.values()]
        for unit in corpus.WIRE_UNITS[1:]:
            found = {}
            for test, environment, norms in json.loads(
                    (ROOT / f"conformance/wire-contract/{unit}-test-inputs.json").read_text()):
                found.setdefault(canonical([environment, norms]), (f"{test}#{len(found)}", environment, norms))
            out += [Seed("wire", unit, f"{unit}/{name}", {"environment": e, "norms": n}, ("python", "lean"))
                    for name, e, n in found.values()]
        return out

    def _engine(self, unit):
        """(contract, run options) of `unit`, loaded and lock-checked once."""
        if unit not in self._engines:
            self._engines[unit] = self._load_engine(unit)
        return self._engines[unit]

    def _load_engine(self, unit):
        from ve.wire_contract.engine import load
        if unit == "soft-norms@0":
            from ve.softnorms_contract import REGISTRY
            return load("soft-norms@0"), {"registry": REGISTRY}
        if unit in corpus.WIRE_UNITS:
            from conformance.wire_contract_faults import unit_module
            return load(unit), {"registry": unit_module(unit).REGISTRY}
        from tests.test_wire_contract_corpus import CONTRACTS, LIMITS as UNIT_LIMITS, NAMES, _registry
        return CONTRACTS[unit], {"registry": _registry(), "contracts": CONTRACTS, "limits": UNIT_LIMITS,
                                 "names": NAMES}

    def python(self, seed, root):
        from ve.wire_contract.engine import CLEAN, Deferred, run
        contract, options = self._engine(seed.profile)

        def diagnose():
            from ve.errors import VEError
            source = deepcopy(root)
            if "adapter" in contract:
                # As `ve_diagnose` does: the unit's adapter builds the root from the case, and refuses a case
                # outside the unit's domain before any check runs (wire-contract-s5.md 2.2).
                try:
                    source = options["registry"].adapters[contract["adapter"]](
                        {"kind": _diagnose_kind(seed.profile), **source})
                except VEError as exc:
                    return {"outcome": "error", "code": "adapter", "text": exc.message, "record": None}
            outcome = run(contract, source, **options)
            if outcome is CLEAN:
                return ok(None)
            if isinstance(outcome, Deferred):
                return NOT_APPLICABLE  # Python defers to Lean by design (spec 2.8)
            return {"outcome": "error", "code": outcome.record["code"], "text": outcome.record.get("text"),
                    "record": outcome.record}
        return call_python(diagnose, self.harness)

    def lean(self, items):
        by_unit = {}
        for index, (seed, _) in enumerate(items):
            by_unit.setdefault(seed.profile, []).append(index)
        out = [None] * len(items)
        for unit, indices in by_unit.items():
            kind = _diagnose_kind(unit)
            cases = [{"id": str(i), "kind": kind, **items[i][1]} for i in indices]
            for i, case, row in zip(indices, cases, batched([BIN / "ve_diagnose", unit, "-"], cases)):
                row, bad = checked(diagnose_row_problem, case, row)
                if bad:
                    out[i] = bad
                elif row["status"] == "error":
                    out[i] = {"outcome": "error", "code": "adapter", "text": row["error"], "record": None}
                elif row["outcome"] == "clean":
                    out[i] = ok(None)
                else:
                    record = row["diagnostic"]
                    out[i] = {"outcome": "error", "code": record["code"], "text": record["text"],
                              "record": record}
        return out

    def rust(self, items):
        raise AssertionError("no Rust path for the wire-contract units")


    def _inherited(self, unit):
        if unit in self._inherited_cache:
            return self._inherited_cache[unit]
        from ve.wire_contract.engine import load
        try:
            contract, options = self._engine(unit)
        except KeyError:
            return set()
        contracts = options.get("contracts") or {}
        inherited = set()

        # The gate's rule (`wire_contract_gate.inherited_checks`), with an include resolved as the engine
        # resolves it: an included contract's inherited check by its include path (`w1-environment/1.1`).
        def visit(entries, prefix):
            for entry in entries:
                if "each" in entry:
                    visit(entry["checks"], prefix)
                elif entry.get("kind") == "include":
                    inner = contracts.get(entry["contract"]) or load(entry["contract"])
                    visit([check for phase in inner["phases"] if phase["name"] in entry["phases"]
                           for check in phase["checks"]], prefix + entry["id"] + "/")
                elif entry.get("kind") == "classifier":
                    inherited.update(prefix + m["id"] for m in entry["emits"] if m.get("inherited"))
                elif entry.get("inherited"):
                    inherited.add(prefix + entry["id"])
        for phase in contract["phases"]:
            visit(phase["checks"], "")
        self._inherited_cache[unit] = inherited
        return inherited

    def error_key(self, answer):
        record = answer.get("record")
        if record is None:
            return {"code": answer["code"], "text": answer["text"]}
        record = dict(record)
        if record.get("check") in self._inherited(record.get("contract")):
            record.pop("text", None)
            record.pop("args", None)
        return record

    def text_fixed(self, seed, left, right):
        return True


def _diagnose_kind(unit):
    """The case kind `ve_diagnose` reads for `unit`: a production unit's legacy route kind (its fault
    catalogue's `CASE_KIND`), `corpus` for a conformance unit."""
    if unit == "soft-norms@0":
        return "soft-elaborate"
    if unit in corpus.WIRE_UNITS:
        from conformance.wire_contract_faults import unit_module
        return unit_module(unit).CASE_KIND
    return "corpus"


SURFACES = {"requests": Requests, "environment": EnvironmentSurface, "wire": Wire}


# ---------------------------------------------------------------- comparison

def input_forms(root):
    """The values a diagnostic may repeat from the input, as written and quoted, longest first: its
    strings and keys of two characters or more. A field name in a diagnostic's wording is replaced
    too, the same way on every input that has the field."""
    values = set()
    for path, node in walk(root):
        if type(node) is str and len(node) > 1:
            values.add(node)
        if path and type(path[-1]) is str and len(path[-1]) > 1:
            values.add(path[-1])
    return sorted({form for value in values for form in (value, repr(value), json.dumps(value),
                                                         json.dumps(value, ensure_ascii=False))},
                  key=len, reverse=True)


def template(value, forms):
    """`value` with the input values its strings repeat (`input_forms`) replaced by `<v>` and digit
    runs by `#`, so that one defect gives one signature whatever names and numbers the mutant
    carries."""
    if type(value) is dict:
        return {key: template(item, forms) for key, item in value.items()}
    if type(value) is list:
        return [template(item, forms) for item in value]
    if type(value) is not str:
        return value
    for form in forms:
        if form in value:
            value = re.sub(r"(?<![A-Za-z0-9_])" + re.escape(form) + r"(?![A-Za-z0-9_])", "<v>", value)
    return re.sub(r"[0-9]+", "#", value)


def compare(surface, seed, left, right):
    """The finding classes between two engines' answers, each (engine, answer)."""
    (left_engine, a), (right_engine, b) = left, right
    if surface.equivalent(seed, left, right):
        return set()
    # Two engines that speak one route's own codes (`OwnCodes`) are held to the same one, or both accept.
    found = {"code"} if own_differs(a, b) else set()
    if a["outcome"] != b["outcome"]:
        return found | {"outcome"}
    if a["outcome"] == "error":
        if refused(a) or refused(b):
            return found  # a package refusal carries no diagnostic; it agrees with any rejection
        if a.get("code") != b.get("code"):
            return found | {"code"}
        if surface.text_fixed(seed, left, right) and surface.error_key(a) != surface.error_key(b):
            return found | {"diagnostic"}
        return found
    if surface.value_compared(seed, left_engine) and surface.value_compared(seed, right_engine) and \
            a["value"] is not None and b["value"] is not None and canonical(a["value"]) != canonical(b["value"]):
        return found | {"value"}
    return found


def own_differs(a, b):
    """Whether two answers that both carry a route's own code (`own`: the code, None for an acceptance)
    carry different ones."""
    return "own" in a and "own" in b and a["own"] != b["own"]


CLASSES = ("python-crash", "timeout", "no-answer", "outcome", "code", "diagnostic", "value")


def classes(surface, seed, answers, root):
    """The finding classes of one mutant's answers ({engine: answer}), and the projection of each
    answer that its signature keeps: outcome, code and the texts a contract fixes, templated. Only an
    engine with no path (`n/a`) is left out; a Python call that does not finish is a `timeout`."""
    live = {e: a for e, a in answers.items() if a["outcome"] != "n/a"}
    found = set()
    if live.get("python", {}).get("outcome") == "crash":
        found.add("python-crash")
    if live.get("python", {}).get("outcome") == "timeout":
        found.add("timeout")
    if any(a["outcome"] == "panic" for e, a in live.items() if e != "python"):
        found.add("no-answer")
    comparable = [(e, a) for e, a in live.items() if a["outcome"] in ("ok", "error")]
    fixed, owned = set(), set()
    for i, left in enumerate(comparable):
        for right in comparable[i + 1:]:
            found |= compare(surface, seed, left, right)
            if left[1]["outcome"] == right[1]["outcome"] == "error" and not (refused(left[1]) or refused(right[1])) \
                    and left[1].get("code") == right[1].get("code") and surface.text_fixed(seed, left, right):
                fixed |= {left[0], right[0]}
            if own_differs(left[1], right[1]):
                owned |= {left[0], right[0]}
    projected = {}
    forms = input_forms(root) if fixed or found & {"python-crash", "no-answer"} else []
    for engine, answer in live.items():
        view = {k: answer[k] for k in ("outcome", "code") if k in answer}
        if engine in owned:
            view["own"] = answer["own"]
        if answer["outcome"] in ("crash", "panic") or engine in fixed:
            key = surface.error_key(answer) if answer["outcome"] == "error" else answer.get("text")
            view["fixed"] = template(key, forms)
        projected[engine] = view
    return sorted(found), projected


def signature(profile, seed, found, projected):
    return digest({"surface": seed.surface, "profile": profile, "classes": found,
                   "answers": {e: projected[e] for e in sorted(projected)}})


@dataclass
class Finding:
    seed: Seed
    mutations: list
    root: object
    classes: list
    answers: dict
    projected: dict
    signature: str


def evaluate(surface, items):
    """(classes, projected, answers, signature) for each (seed, root), on its seed's engines."""
    out = []
    for (seed, root), answers in zip(items, surface.answers(items)):
        found, projected = classes(surface, seed, answers, root)
        profile = surface.profile(seed, root)
        out.append((found, projected, answers, signature(profile, seed, found, projected) if found else None))
    return out


# ---------------------------------------------------------------- sampling

def sample(surface, seeds, ones, twos, rng):
    """Every seed as it is, then `ones` 1-fault and `twos` 2-fault mutants: [(seed, mutations)]. The
    1-fault mutants go round-robin over the profiles and, within each, over its seeds, so that a family
    of many seeds does not crowd out the others (`Faults` draws each seed's mutations)."""
    by_profile = {}
    for seed in seeds:
        by_profile.setdefault(seed.profile, []).append(seed)
    profiles = sorted(by_profile)
    faults = {}

    def draw(seed):
        if seed.id not in faults:
            faults[seed.id] = Faults(seed.root, surface.protected, surface.limits(seed), surface.mutate_root)
        return faults[seed.id].draw(rng)

    chosen = [(seed, []) for seed in seeds]
    cursors = {profile: 0 for profile in profiles}
    turn = 0
    exhausted = set()
    while len(chosen) - len(seeds) < ones and len(exhausted) < len(profiles):
        profile = profiles[turn % len(profiles)]
        turn += 1
        if profile in exhausted:
            continue
        group = by_profile[profile]
        for _ in range(len(group)):
            seed = group[cursors[profile] % len(group)]
            cursors[profile] += 1
            mutation = draw(seed)
            if mutation is not None:
                chosen.append((seed, [mutation]))
                break
        else:
            exhausted.add(profile)
    pairs = []
    attempts = 0
    while len(pairs) < twos and profiles and attempts < twos * 20:
        attempts += 1
        group = by_profile[profiles[rng.randrange(len(profiles))]]
        seed = group[rng.randrange(len(group))]
        first, second = draw(seed), draw(seed)
        if first is None or second is None or related(tuple(first[1]), tuple(second[1])):
            continue
        pairs.append((seed, [first, second]))
    return chosen + pairs


# ---------------------------------------------------------------- minimiser

def shrink_edits(root, protected):
    """The edits that make `root` smaller, biggest cut first: a member or element dropped, a
    container emptied, a string cut to its first character. An edit is (path, how)."""
    out = []
    for path, node in walk(root):
        if not path or any(related(path, p) for p in protected if len(path) <= len(p)):
            continue
        size = len(canonical(node))
        out.append((size + 1, path, "drop"))
        if type(node) in (dict, list) and node:
            out.append((size - 2, path, "empty"))
        if type(node) is str and len(node) > 1:
            out.append((size - 3, path, "cut"))
    return [(path, how) for _, path, how in sorted(out, key=lambda item: -item[0])]


def shrunk(root, path, how):
    out = deepcopy(root)
    if how == "drop":
        del get(out, path[:-1])[path[-1]]
    else:
        node = get(out, path)
        put(out, path, type(node)() if how == "empty" else node[:1])
    return out


def minimise(surface, seed, root, target, evaluations=MINIMISE_EVALUATIONS):
    """A smaller input whose answers keep the signature `target`: greedy, biggest cut first, each
    round's candidates evaluated in batches, at most `evaluations` candidates in all."""
    current = root
    spent = 0
    while spent < evaluations:
        edits = shrink_edits(current, surface.protected)
        accepted = None
        for start in range(0, len(edits), MINIMISE_BATCH):
            if spent >= evaluations:
                break
            chunk = [shrunk(current, path, how) for path, how in edits[start:start + MINIMISE_BATCH]]
            spent += len(chunk)
            for candidate, (_, _, _, sig) in zip(chunk, evaluate(surface, [(seed, c) for c in chunk])):
                if sig == target:
                    accepted = candidate
                    break
            if accepted is not None:
                break
        if accepted is None:
            break
        current = accepted
    return current


# ---------------------------------------------------------------- baseline

def load_baseline(path=BASELINE):
    if not path.exists():
        return {"format": FORMAT, "entries": []}
    data = json.loads(path.read_text())
    assert data.get("format") == FORMAT, f"{path}: unknown format"
    return data


def baseline_problems(baseline):
    """Entries that are not reviewed: each must name its input, answers and a follow-up id."""
    problems = []
    seen = set()
    for entry in baseline["entries"]:
        # The input may be any JSON value (a minimised environment can be `0` or `[]`); it must be there.
        missing = [k for k in ("id", "surface", "profile", "seed", "answers", "classes",
                               "signature", "follow_up") if not entry.get(k) and entry.get(k) != {}]
        missing += [] if "input" in entry else ["input"]
        if missing:
            problems.append(f"{entry.get('id')}: missing {missing}")
        if str(entry.get("follow_up", "")).strip().upper() in ("", "TODO"):
            problems.append(f"{entry.get('id')}: no follow-up id")
        if entry.get("id") in seen:
            problems.append(f"{entry.get('id')}: repeated id")
        seen.add(entry.get("id"))
    return problems


def seed_of(entry):
    """The seed a baseline entry names, rebuilt from the entry (its root is not needed to replay)."""
    return Seed(entry["surface"], entry["profile"], entry["seed"], None, tuple(entry["engines"]),
                dict(entry.get("meta", {})))


def replay(entries, surfaces):
    """Each baseline entry run again on its minimised input: (entry, status, now) where status is
    `reproduces`, `changed` (another finding) or `fixed` (no finding)."""
    out = []
    by_surface = {}
    for entry in entries:
        by_surface.setdefault(entry["surface"], []).append(entry)
    for name, group in by_surface.items():
        items = [(seed_of(entry), entry["input"]) for entry in group]
        rows = evaluate(surfaces[name], items)
        for entry, (found, projected, answers, sig) in zip(group, rows):
            status = "reproduces" if sig == entry["signature"] else "fixed" if not found else "changed"
            out.append((entry, status, {"classes": found, "answers": answers, "signature": sig}))
    return out


# The seed fields a replay needs beyond the input: the request surface's runners.
META_KEYS = ("kind", "family", "lean", "rust")


def entry_for(finding, profile, minimised, answers, follow_up=None, entry_id=None):
    seed = finding.seed
    meta = {k: v for k, v in seed.meta.items() if k in META_KEYS}
    return {"id": entry_id or f"{seed.surface}-{finding.signature}", "surface": seed.surface,
            "profile": profile, "seed": seed.id, "engines": list(seed.engines), "meta": meta,
            "mutation": finding.mutations, "input": minimised, "classes": finding.classes,
            "answers": answers, "signature": finding.signature, "follow_up": follow_up or "TODO"}


# ---------------------------------------------------------------- the run

def _children_cpu():
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


def fuzz(*, scale=1, rng_seed=20261004, surfaces=None, baseline_path=BASELINE, update=False,
         log=lambda message: None):
    """One run: sample, compare, minimise what is new, replay the baseline. Returns the report."""
    self_cpu, child_cpu = time.process_time(), _children_cpu()
    names = list(surfaces or SURFACES)
    built = {name: SURFACES[name]() for name in SURFACES}
    try:
        report = _fuzz(built, names, scale, rng_seed, baseline_path, update, log)
    finally:
        for surface in built.values():
            surface.close()
    # The children's CPU counts the processes that have ended, the Lean service among them.
    report["cpu_seconds"] = {"python": round(time.process_time() - self_cpu, 1),
                             "children": round(_children_cpu() - child_cpu, 1)}
    return report


def _fuzz(built, names, scale, rng_seed, baseline_path, update, log):
    baseline = load_baseline(baseline_path)
    known = {entry["signature"]: entry for entry in baseline["entries"]}
    report = {"seed": rng_seed, "scale": scale, "corpus": {}, "mutants": {}, "answers": {}, "findings": {},
              "new": [], "baseline": {}}
    new = {}
    seen = {}
    for name in names:
        surface = built[name]
        seeds = surface.seeds() if scale else []
        report["corpus"][name] = _count(seed.profile for seed in seeds)
        ones, twos = CI_BUDGET[name]
        rng = random.Random(f"{rng_seed}:{name}")
        mutants = sample(surface, seeds, ones * scale, twos * scale, rng)
        report["mutants"][name] = {"zero-fault": sum(len(m) == 0 for _, m in mutants),
                                   "one-fault": sum(len(m) == 1 for _, m in mutants),
                                   "two-fault": sum(len(m) == 2 for _, m in mutants)}
        log(f"{name}: {len(seeds)} seeds, {len(mutants)} inputs")
        counts = {}
        answered = {}
        for start in range(0, len(mutants), CHUNK):
            chunk = mutants[start:start + CHUNK]
            items = [(seed, apply_all(seed.root, mutations)) for seed, mutations in chunk]
            for (seed, mutations), (_, root), (found, projected, answers, sig) in zip(
                    chunk, items, evaluate(surface, items)):
                for engine, answer in answers.items():
                    key = f"{engine}:{answer['outcome']}"
                    answered[key] = answered.get(key, 0) + 1
                if not found:
                    continue
                for cls in found:
                    key = f"{surface.profile(seed, root)}:{cls}"
                    counts[key] = counts.get(key, 0) + 1
                seen[sig] = seen.get(sig, 0) + 1
                if sig not in known and sig not in new:
                    new[sig] = Finding(seed, mutations, root, found, answers, projected, sig)
        report["findings"][name] = dict(sorted(counts.items()))
        report["answers"][name] = dict(sorted(answered.items()))
    entries = []
    for index, (sig, finding) in enumerate(new.items()):
        surface = built[finding.seed.surface]
        if index < MINIMISE_LIMIT:
            log(f"minimising {finding.seed.surface} {finding.seed.profile} {finding.classes}")
            minimised = minimise(surface, finding.seed, finding.root, sig)
        else:
            minimised = finding.root
        [(_, _, answers, _)] = evaluate(surface, [(finding.seed, minimised)])
        entry = entry_for(finding, surface.profile(finding.seed, minimised), minimised, answers)
        if index >= MINIMISE_LIMIT:
            entry["minimised"] = False
        entries.append(entry)
    report["new"] = entries
    replayed = replay(baseline["entries"], built)
    report["baseline"] = {
        "entries": len(baseline["entries"]),
        "seen_in_sample": sum(1 for entry in baseline["entries"] if entry["signature"] in seen),
        "unreviewed": baseline_problems(baseline),
        "not_reproduced": [{"id": entry["id"], "status": status, "now": now}
                           for entry, status, now in replayed if status != "reproduces"]}
    if update:
        kept = [entry for entry, status, _ in replayed if status == "reproduces"]
        changed = [entry for entry, status, _ in replayed if status == "changed"]
        for entry in changed:
            log(f"baseline entry {entry['id']} changed; it is dropped and its finding is new again")
        baseline_path.write_text(json.dumps({"format": FORMAT, "entries": kept + entries},
                                            indent=1, ensure_ascii=False) + "\n")
    report["passed"] = not report["new"] and not report["baseline"]["not_reproduced"] and \
        not report["baseline"]["unreviewed"]
    return report


def _count(items):
    out = {}
    for item in items:
        out[item] = out.get(item, 0) + 1
    return dict(sorted(out.items()))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--ci", action="store_true", help="the seeded, bounded run of the test suite")
    mode.add_argument("--deep", type=int, metavar="N", help="N times the CI sample (nightly)")
    parser.add_argument("--seed", type=int, help="sample seed (CI: fixed; deep: today's date)")
    parser.add_argument("--surface", action="append", choices=sorted(SURFACES))
    parser.add_argument("--update-baseline", action="store_true",
                        help="drop entries that no longer reproduce and add new findings as TODO")
    parser.add_argument("--report", type=Path, help="write the JSON report here")
    parser.add_argument("--minimise-limit", type=int, metavar="N",
                        help=f"minimise at most N new signatures (default {MINIMISE_LIMIT})")
    args = parser.parse_args(argv)
    if args.minimise_limit is not None:
        globals()["MINIMISE_LIMIT"] = args.minimise_limit
    seed = args.seed if args.seed is not None else (
        20261004 if args.ci else int(datetime.date.today().strftime("%Y%m%d")))
    report = fuzz(scale=1 if args.ci else args.deep, rng_seed=seed, surfaces=args.surface,
                  update=args.update_baseline, log=lambda message: print(message, file=sys.stderr))
    text = json.dumps(report, indent=1, ensure_ascii=False)
    if args.report:
        args.report.write_text(text + "\n")
    summary = {k: report[k] for k in ("corpus", "mutants", "findings", "cpu_seconds", "passed")}
    summary["new"] = [{k: e[k] for k in ("id", "surface", "profile", "classes", "input", "answers")}
                      for e in report["new"]]
    summary["baseline"] = report["baseline"]
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
