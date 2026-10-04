"""Cross-language differential fuzzer: Python, the Lean routes and Rust on seeded mutants.

Every fixture of the conformance corpus and the use cases is a *seed*. A seed belongs to a *surface*,
which says how each implementation runs it and how its answers compare:

* `p0`: the P0 route cases (`conformance/p0.py`), through `conformance.three_way` (Python in process,
  `ve_conformance route`, `ve conformance`); verdicts and errors are reduced as the P0 three-way test
  reduces them, so a text is compared when the P0 contract fixes it (`three_way.KNOWN`).
* `environment`: every distinct environment of the corpus and the use cases, decoded by Python's
  `Environment`, by the Lean route that decodes that envelope (`lean_route`) and by Rust (a `label`
  case); a text is compared when either side is a decoder type diagnostic (`TYPE_DIAGNOSTICS`), and the
  environment identity when both engines report one.
* `wire`: the wire-contract units (`demo@0`, `defer@0`, `forms@0`, `soft-norms@0`), by the Python
  engine and `ve_diagnose`; the whole diagnostic record is compared, except the text and args of an
  inherited check (the contract's `inherited` flag).

Each seed gets 1-fault and 2-fault mutants (`one_faults`): every JSON node replaced by 7, true, null,
[], {} and "x"; an object member removed; keys and lists reversed; a list's first entry duplicated;
string values and object keys with NBSP, a double space, a tab, a carriage return, U+212A, a dotted
capital I, upper case and Arabic-Indic digits; and every array or string a wire-contract table limits
resized to limit - 1, limit and limit + 1 (`limit_patterns`). An implementation takes part on a seed
when it has a path for it: it accepts the unmutated seed (or, for `p0`, the three-way test runs it).

A *finding* is a Python exception other than VEError, a Lean or Rust process that does not answer
(panic, signal, malformed output), or a disagreement between the answers of the implementations that
take part. Findings are grouped by signature (surface, profile, classes and the compared answers).
A signature in the reviewed baseline (`conformance/difffuzz-baseline.json`) is known; any other is
new, and is minimised (`minimise`) before it is reported. Every baseline entry is replayed on its
minimised input and must still give its recorded answers, so a fix must shrink the baseline.

    python3 tools/difffuzz.py --ci           # seeded and bounded; tests/test_difffuzz.py runs it
    python3 tools/difffuzz.py --deep 20      # nightly: 20 times the CI sample, seeded by the date
    python3 tools/difffuzz.py --ci --update-baseline   # rewrite the baseline (then review it)

Exit status: 0 when nothing is new and every baseline entry reproduces, 1 otherwise.
"""
from __future__ import annotations

import argparse
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
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.subprocesses import HANG_TIMEOUT, run_cpu_bounded  # noqa: E402

BIN = ROOT / "lean/.lake/build/bin"
BASELINE = ROOT / "conformance/difffuzz-baseline.json"
FORMAT = "ve-difffuzz-baseline@1"
ENGINES = ("python", "lean", "rust")

# CPU seconds one Python call or one Lean/Rust batch may spend before it counts as not answering.
PYTHON_CPU = 20
BATCH_CPU = 300
BATCH_CASES = 400

# The CI sample: 1-fault and 2-fault mutants per surface. `--deep N` multiplies both.
CI_BUDGET = {"p0": (6000, 1500), "environment": (6000, 1500), "wire": (6000, 1500)}
CHUNK = 2000
MINIMISE_EVALUATIONS = 3000
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


def one_faults(root, protected, limits, mutate_root=False):
    """Every 1-fault mutation of `root` that changes it: [op, path, arg] lists, the limit ones last."""
    out = []
    nodes = [(path, node) for path, node in walk(root)
             if (path or mutate_root) and not any(related(path, p) and len(path) >= len(p) for p in protected)]
    for path, node in nodes:
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
    for pattern, kind, limit in limits:
        for path, node in nodes:
            if _matches(pattern, path) and type(node) is (list if kind == "max_items" else str):
                out.extend(["limit", list(path), size] for size in (limit - 1, limit, limit + 1)
                           if size >= 0 and size != len(node) and _resized(node, size) is not None)
    return out


# ---------------------------------------------------------------- answers

def ok(value=None):
    return {"outcome": "ok", "value": value}


def error(code, text):
    return {"outcome": "error", "code": code, "text": text}


NOT_APPLICABLE = {"outcome": "n/a"}
OFF_WIRE = {"outcome": "off-wire"}


def on_wire(value):
    """Whether `value` is restricted JSON, the only input the Lean and Rust package readers take."""
    from ve.errors import VEError
    from ve.wire import canonical_json
    try:
        canonical_json(value)
        return True
    except VEError:
        return False


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


def call_python(function, harness):
    """Run one Python call. A VEError is the implementation's answer; any other exception raised
    inside `ve/` is a crash; one raised by the harness itself (`harness` files: a field the adapter
    reads is missing or mistyped) means the call cannot be made, and is not applicable."""
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


def run_rows(command, cases):
    """One row per case from a batch runner, or the reason it did not answer: a batch that does not
    answer is split until the case that does not answer is alone (`{"panic": reason}`)."""
    if not cases:
        return []
    text = json.dumps(cases, ensure_ascii=False)
    completed, _ = run_cpu_bounded([str(c) for c in command], text, BATCH_CPU)
    reason = None
    if completed.returncode not in (0, 1):
        reason = f"exit {completed.returncode}: {completed.stderr[-300:]}"
    elif "PANIC" in completed.stderr or "panicked" in completed.stderr:
        reason = f"panic: {completed.stderr[-300:]}"
    else:
        try:
            rows = json.loads(completed.stdout)
        except ValueError:
            rows = None
        if type(rows) is not list or len(rows) != len(cases) or not all(type(r) is dict for r in rows):
            reason = f"malformed output: {completed.stdout[:200]}"
        elif [r.get("id") for r in rows] != [c.get("id") for c in cases]:
            reason = "rows out of order"
    if reason is None:
        return rows
    if len(cases) == 1:
        if completed.returncode == 2 and reason.startswith("exit 2"):
            # The runner refused the package (framing): an answer, compared with Python's.
            return [{"framing": completed.stderr.strip()[-300:]}]
        return [{"panic": reason}]
    middle = len(cases) // 2
    return run_rows(command, cases[:middle]) + run_rows(command, cases[middle:])


def batched(command, cases):
    rows = []
    for start in range(0, len(cases), BATCH_CASES):
        rows.extend(run_rows(command, cases[start:start + BATCH_CASES]))
    return rows


def panic(row):
    if "framing" in row:
        return error("framing", row["framing"])
    return {"outcome": "panic", "text": row["panic"]} if "panic" in row else None


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
        """{engine: answer} for each (seed, root), from the engines of `ENGINES` that take part on its
        seed; each of Lean and Rust answers every item in batches."""
        out = [{} for _ in items]
        wire = [on_wire(root) for _, root in items]
        for engine in ENGINES:
            chosen = [index for index, (seed, _) in enumerate(items) if engine in seed.engines]
            if engine != "python":
                # Lean and Rust read packages of restricted JSON only (no null, no float): an input
                # off that wire never reaches them, so they have no answer to compare.
                for index in chosen:
                    if not wire[index]:
                        out[index][engine] = OFF_WIRE
                chosen = [index for index in chosen if wire[index]]
            if not chosen:
                continue
            if engine == "python":
                results = [self.python(*items[index]) for index in chosen]
            else:
                results = getattr(self, engine)([items[index] for index in chosen])
            for index, answer in zip(chosen, results):
                out[index][engine] = answer
        return out

    def text_fixed(self, seed, left, right):
        """Whether a contract fixes the text of two engines' errors of one code: (engine, answer)."""
        raise NotImplementedError

    def error_key(self, answer):
        """What of an error the contract fixes beyond its code."""
        return answer.get("text")

    def value_compared(self, seed, engine):
        return True


_LIMITS = None


def LIMITS():
    global _LIMITS
    if _LIMITS is None:
        _LIMITS = limit_patterns()
    return _LIMITS


# P0 ---------------------------------------------------------------------------

P0_FAMILIES = ("elaborated-document", "invalid-background-model", "dependency-order", "labels", "admission")
P0_VALUES = {"label": ("label",), "dependency-order": ("order",), "evaluate": ("values",),
             "countermodel": ("refutes",), "search": ("found", "model"), "certificate": ("valid",),
             "background": ("background", "generators"),
             "admission": ("admitted", "report", "report_id", "kinds")}


class P0(Surface):
    """The P0 route families of the three-way test (the vacuity family asserts its own witness)."""
    name = "p0"
    protected = (("id",), ("kind",), ("max_domain_size",))
    env_prefix = ("environment",)
    harness = frozenset({"difffuzz.py", "three_way.py"})

    def seeds(self):
        from conformance.three_way import rust_request
        out = []
        for family in P0_FAMILIES:
            for case in json.loads((ROOT / f"conformance/{family}.json").read_text()):
                if "pending" in case:
                    continue
                root = {k: v for k, v in case.items() if k != "expected"}
                engines = ["python"]
                if case["kind"] != "search":
                    engines.append("lean")
                if rust_request(case) is not None:
                    engines.append("rust")
                out.append(Seed("p0", f"{family}:{case['kind']}", f"{family}/{case['id']}", root,
                                tuple(engines), {"expected": case["expected"], "kind": case["kind"]}))
        return out

    def _verdict(self, seed, verdict):
        kind = seed.meta["kind"]
        if verdict["status"] == "error":
            if kind == "certificate" and verdict["code"] not in ("UnsupportedProfile", "ResourceLimit"):
                # `three_way.lean_verdict`'s certificate rule, applied to every engine alike.
                return ok({"valid": False})
            return {**error(verdict["code"], verdict["error"]),
                    **({"generator": verdict["generator"]} if "generator" in verdict else {})}
        return ok({key: verdict.get(key) for key in P0_VALUES[kind]})

    def python(self, seed, root):
        from conformance.three_way import python_verdict
        answer = call_python(lambda: python_verdict(deepcopy(root)), self.harness)
        return self._verdict(seed, answer) if "status" in answer else answer

    def lean(self, items):
        from conformance.three_way import lean_verdict
        rows = batched([BIN / "ve_conformance", "route", "-"],
                       [{**root, "id": str(index)} for index, (_, root) in enumerate(items)])
        return [panic(row) or self._lean(seed, root, row, lean_verdict) for (seed, root), row in zip(items, rows)]

    def _lean(self, seed, root, row, lean_verdict):
        try:
            return self._verdict(seed, lean_verdict(root, row))
        except (KeyError, TypeError) as exc:
            return {"outcome": "panic", "text": f"malformed row {exc!r}: {canonical(row)[:200]}"}

    def rust(self, items):
        from conformance.three_way import rust_request, rust_verdict
        requests = []
        for index, (seed, root) in enumerate(items):
            try:
                request = rust_request({**root, "expected": seed.meta["expected"]})
            except (KeyError, TypeError, AttributeError):
                request = None
            requests.append(request if request is None else {**request, "id": str(index)})
        sent = [r for r in requests if r is not None]
        rows = iter(batched([rust_binary(), "conformance"], sent))
        out = []
        for (seed, root), request in zip(items, requests):
            if request is None:
                out.append(NOT_APPLICABLE)
                continue
            row = next(rows)
            try:
                out.append(panic(row) or self._verdict(seed, rust_verdict(root, row)))
            except (KeyError, TypeError) as exc:
                out.append({"outcome": "panic", "text": f"malformed row {exc!r}: {canonical(row)[:200]}"})
        return out

    def value_compared(self, seed, engine):
        # Rust's certificate verdict is a bounded search, not a replay (three-way test, plan 3.7).
        return not (engine == "rust" and seed.meta["kind"] == "certificate")

    def text_fixed(self, seed, left, right):
        from conformance.three_way import KNOWN
        return left[1]["code"] in KNOWN

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

# The Lean route that decodes each kind of envelope, and a case on which that route answers with the
# environment decoded and nothing else to fail.
ROUTE_CASES = {
    "alternatives": ("ve_alternatives_route", {"kind": "alt-elaborate", "norms": []}),
    "risk": ("ve_risk_route", {"kind": "risk-elaborate", "document": {"norms": []}}),
    "soft-norms": ("ve_soft_norms_route", {"kind": "soft-elaborate", "norms": []}),
    "speech": ("ve_speech_acts_route", {"kind": "speech-elaborate", "document": {"units": []}}),
    "reports": ("ve_reports_route", {"kind": "reports-elaborate", "document": {"units": []}}),
    "quantity": ("ve_quantity", {"kind": "document", "document": {"units": []}}),
}


def lean_route(data):
    """The Lean route that decodes an environment, read from the environment itself: a frozen
    envelope's language and every envelope no block route takes go to the service's `environment`
    mode ("envelope"); otherwise the profiles choose when they are an array of strings, else the
    blocks the envelope carries; then the W6 fields choose the quantity route."""
    if type(data) is not dict:
        return "envelope"
    if data.get("language") in ("ve.core@0", "ve.core@0.1"):
        return "envelope"
    profiles = data.get("profiles")
    if type(profiles) is list and all(type(p) is str for p in profiles):
        chosen = [route for profile, route in (("risk@0", "risk"), ("alternatives@0", "alternatives"),
                                               ("speech-acts@0", "speech"), ("reports@0", "reports"),
                                               ("soft-norms@0", "soft-norms"))
                  if profile in profiles]
    else:
        chosen = [route for block, route in (("risk", "risk"), ("alternatives", "alternatives"),
                                             ("speech_acts", "speech")) if block in data]
    if chosen:
        return chosen[0]
    return "quantity" if {"unit_schema", "units"} & set(data) else "envelope"


class EnvironmentSurface(Surface):
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
        from ve.environment import Environment
        found = {}

        def add(origin, data):
            if type(data) is dict and "language" in data:
                found.setdefault(canonical(data), (origin, data))
        for family in (*P0_FAMILIES, "vacuity"):
            for case in json.loads((ROOT / f"conformance/{family}.json").read_text()):
                add(f"{family}/{case['id']}", case["environment"])
        for path in sorted(ROOT.glob("usecases/**/environment*.json")):
            add(str(path.relative_to(ROOT)), json.loads(path.read_text()))
        for test, environment, _ in json.loads(
                (ROOT / "conformance/wire-contract/soft-norms@0-test-inputs.json").read_text()):
            add(f"soft-norms@0-test-inputs/{test}", environment)
        from conformance.risk import agent_ops
        add("conformance/risk.agent_ops", agent_ops())
        seeds = []
        for origin, data in found.values():
            try:
                with python_authority():
                    Environment(deepcopy(data))
            except Exception:  # noqa: BLE001 - a seed Python rejects is not a seed
                continue
            seeds.append(Seed("environment", lean_route(data), origin, data))
        # Each engine takes part on a seed whose unmutated environment it accepts.
        lean = self.lean([(s, s.root) for s in seeds])
        rust = self.rust([(s, s.root) for s in seeds])
        for seed, l, r in zip(seeds, lean, rust):
            seed.engines = tuple(e for e, a in (("python", ok()), ("lean", l), ("rust", r))
                                 if a["outcome"] == "ok")
        return seeds

    def profile(self, seed, root):
        return lean_route(root)

    def python(self, seed, root):
        from ve.environment import Environment

        def decode():
            return ok({"environment_id": Environment(deepcopy(root)).environment_id})
        return call_python(decode, self.harness)

    def lean(self, items):
        from ve.backends.diagnostics import checker_error
        roots = [root for _, root in items]
        by_route = {}
        for index, root in enumerate(roots):
            by_route.setdefault(lean_route(root), []).append(index)
        out = [None] * len(roots)
        for route, indices in by_route.items():
            if route == "envelope":
                cases = [{"id": str(i), "environment": roots[i]} for i in indices]
                rows = self._service(cases)
            else:
                binary, case = ROUTE_CASES[route]
                rows = batched([BIN / binary, "-"],
                               [{"id": str(i), "environment": roots[i], **case} for i in indices])
            for i, row in zip(indices, rows):
                if "not-on-wire" in row:
                    out[i] = OFF_WIRE
                elif "panic" in row or "framing" in row:
                    out[i] = panic(row)
                elif row.get("status") == "error":
                    diagnostic = checker_error(str(row.get("error", ""))).to_dict()
                    out[i] = error(diagnostic["code"], diagnostic["message"])
                else:
                    out[i] = ok({"environment_id": row.get("environment_id")} if route == "envelope" else None)
        return out

    def _service(self, cases):
        """The Lean service's `environment` mode (the envelope decoder), one row per case; a case
        the service cannot answer is retried alone, and one that still fails did not answer."""
        from ve.backends.lean_service import LeanService
        from ve.errors import VEError
        try:
            if self._lean_service is None:
                self._lean_service = LeanService(timeout=HANG_TIMEOUT)
                self._lean_service.start()
            return self._lean_service.run("environment", cases)
        except Exception as exc:  # noqa: BLE001 - CheckerUnavailable, or a batch the transport refuses
            if not isinstance(exc, VEError):
                self.close()
            if len(cases) == 1:
                # The transport refuses what is not on the restricted wire (an explicit null): the
                # service never sees it, so it has no answer to compare.
                if isinstance(exc, VEError):
                    return [{"not-on-wire": str(exc)}]
                return [{"panic": f"{type(exc).__name__}: {exc}"[:300]}]
            middle = len(cases) // 2
            return self._service(cases[:middle]) + self._service(cases[middle:])

    def rust(self, items):
        cases = [{"id": str(i), "kind": "label", "label": "asserted", "environment": root}
                 for i, (_, root) in enumerate(items)]
        out = []
        for row in batched([rust_binary(), "conformance"], cases):
            if "panic" in row or "framing" in row:
                out.append(panic(row))
            elif row.get("status") == "error" and type(row.get("error")) is dict:
                out.append(error(row["error"].get("code"), row["error"].get("message")))
            elif row.get("status") == "error":
                out.append({"outcome": "panic", "text": f"malformed row {canonical(row)[:200]}"})
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
        return out

    def _engine(self, unit):
        from ve.wire_contract.engine import load
        if unit == "soft-norms@0":
            from ve.softnorms_contract import REGISTRY
            return load("soft-norms@0"), {"registry": REGISTRY}
        from tests.test_wire_contract_corpus import CONTRACTS, LIMITS as UNIT_LIMITS, NAMES, _registry
        return CONTRACTS[unit], {"registry": _registry(), "contracts": CONTRACTS, "limits": UNIT_LIMITS,
                                 "names": NAMES}

    def python(self, seed, root):
        from ve.wire_contract.engine import CLEAN, Deferred, run
        contract, options = self._engine(seed.profile)

        def diagnose():
            outcome = run(contract, deepcopy(root), **options)
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
            kind = "soft-elaborate" if unit == "soft-norms@0" else "corpus"
            cases = [{"id": str(i), "kind": kind, **items[i][1]} for i in indices]
            for i, row in zip(indices, batched([BIN / "ve_diagnose", unit, "-"], cases)):
                if "panic" in row or "framing" in row:
                    out[i] = panic(row)
                elif row.get("status") != "ok":
                    out[i] = {"outcome": "error", "code": "adapter", "text": str(row.get("error")), "record": None}
                elif row.get("outcome") == "clean":
                    out[i] = ok(None)
                else:
                    record = row.get("diagnostic") or {}
                    out[i] = {"outcome": "error", "code": record.get("code"), "text": record.get("text"),
                              "record": record}
        return out

    def rust(self, items):
        raise AssertionError("no Rust path for the wire-contract units")

    def _inherited(self, unit):
        if unit in self._inherited_cache:
            return self._inherited_cache[unit]
        try:
            contract, _ = self._engine(unit)
        except KeyError:
            return set()
        inherited = set()

        def visit(entries):
            for entry in entries:
                if "each" in entry:
                    visit(entry["checks"])
                for member in entry.get("emits", []) if entry.get("kind") == "classifier" else [entry]:
                    if member.get("inherited"):
                        inherited.add(member["id"])
        for phase in contract["phases"]:
            visit(phase["checks"])
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


SURFACES = {"p0": P0, "environment": EnvironmentSurface, "wire": Wire}


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
    if a["outcome"] != b["outcome"]:
        return {"outcome"}
    if a["outcome"] == "error":
        if a.get("code") != b.get("code"):
            return {"code"}
        if surface.text_fixed(seed, left, right) and surface.error_key(a) != surface.error_key(b):
            return {"diagnostic"}
        return set()
    if surface.value_compared(seed, left_engine) and surface.value_compared(seed, right_engine) and \
            a["value"] is not None and b["value"] is not None and canonical(a["value"]) != canonical(b["value"]):
        return {"value"}
    return set()


def classes(surface, seed, answers, root):
    """The finding classes of one mutant's answers ({engine: answer}), and the projection of each
    answer that its signature keeps: outcome, code and the texts a contract fixes, templated."""
    live = {e: a for e, a in answers.items() if a["outcome"] not in ("n/a", "timeout", "off-wire")}
    found = set()
    if live.get("python", {}).get("outcome") == "crash":
        found.add("python-crash")
    if any(a["outcome"] == "panic" for e, a in live.items() if e != "python"):
        found.add("no-answer")
    comparable = [(e, a) for e, a in live.items() if a["outcome"] in ("ok", "error")]
    fixed = set()
    for i, left in enumerate(comparable):
        for right in comparable[i + 1:]:
            found |= compare(surface, seed, left, right)
            if left[1]["outcome"] == right[1]["outcome"] == "error" and \
                    left[1].get("code") == right[1].get("code") and surface.text_fixed(seed, left, right):
                fixed |= {left[0], right[0]}
    projected = {}
    forms = input_forms(root) if fixed or found & {"python-crash", "no-answer"} else []
    for engine, answer in live.items():
        view = {k: answer[k] for k in ("outcome", "code") if k in answer}
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
    """`ones` 1-fault and `twos` 2-fault mutants, spread over the seeds round-robin: [(seed, mutations)]."""
    pools = []
    for seed in seeds:
        candidates = one_faults(seed.root, surface.protected, surface.limits(seed), surface.mutate_root)
        rng.shuffle(candidates)
        pools.append((seed, candidates))
    chosen = []
    cursor = 0
    while len(chosen) < ones and any(pool for _, pool in pools):
        seed, pool = pools[cursor % len(pools)]
        if pool:
            chosen.append((seed, [pool.pop()]))
        cursor += 1
    pairs = []
    rich = [(seed, candidates) for seed, candidates in pools if len(candidates) >= 2] or []
    attempts = 0
    while len(pairs) < twos and rich and attempts < twos * 20:
        attempts += 1
        seed, pool = rich[rng.randrange(len(rich))]
        first, second = rng.sample(pool, 2)
        if related(tuple(first[1]), tuple(second[1])):
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
        missing = [k for k in ("id", "surface", "profile", "seed", "input", "answers", "classes",
                               "signature", "follow_up") if not entry.get(k) and entry.get(k) != {}]
        if missing:
            problems.append(f"{entry.get('id')}: missing {missing}")
        if str(entry.get("follow_up", "")).strip().upper() in ("", "TODO"):
            problems.append(f"{entry.get('id')}: no follow-up id")
        if entry.get("id") in seen:
            problems.append(f"{entry.get('id')}: repeated id")
        seen.add(entry.get("id"))
    return problems


def replay(entries, surfaces):
    """Each baseline entry run again on its minimised input: (entry, status, now) where status is
    `reproduces`, `changed` (another finding) or `fixed` (no finding)."""
    out = []
    by_surface = {}
    for entry in entries:
        by_surface.setdefault(entry["surface"], []).append(entry)
    for name, group in by_surface.items():
        items = [(Seed(name, entry["profile"], entry["seed"], None, tuple(entry["engines"]),
                       dict(entry.get("meta", {}))), entry["input"]) for entry in group]
        rows = evaluate(surfaces[name], items)
        for entry, (found, projected, answers, sig) in zip(group, rows):
            status = "reproduces" if sig == entry["signature"] else "fixed" if not found else "changed"
            out.append((entry, status, {"classes": found, "answers": answers, "signature": sig}))
    return out


def entry_for(finding, profile, minimised, answers, follow_up=None, entry_id=None):
    seed = finding.seed
    return {"id": entry_id or f"{seed.surface}-{finding.signature}", "surface": seed.surface,
            "profile": profile, "seed": seed.id, "engines": list(seed.engines),
            "meta": {k: v for k, v in seed.meta.items() if k == "kind" or k == "expected"},
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
    report = {"seed": rng_seed, "scale": scale, "corpus": {}, "mutants": {}, "findings": {},
              "new": [], "baseline": {}}
    new = {}
    seen = {}
    for name in names:
        surface = built[name]
        seeds = surface.seeds()
        report["corpus"][name] = _count(seed.profile for seed in seeds)
        ones, twos = CI_BUDGET[name]
        rng = random.Random(f"{rng_seed}:{name}")
        mutants = sample(surface, seeds, ones * scale, twos * scale, rng)
        report["mutants"][name] = {"one-fault": sum(len(m) == 1 for _, m in mutants),
                                   "two-fault": sum(len(m) == 2 for _, m in mutants)}
        log(f"{name}: {len(seeds)} seeds, {len(mutants)} mutants")
        counts = {}
        for start in range(0, len(mutants), CHUNK):
            chunk = mutants[start:start + CHUNK]
            items = [(seed, apply_all(seed.root, mutations)) for seed, mutations in chunk]
            for (seed, mutations), (_, root), (found, projected, answers, sig) in zip(
                    chunk, items, evaluate(surface, items)):
                if not found:
                    continue
                for cls in found:
                    key = f"{surface.profile(seed, root)}:{cls}"
                    counts[key] = counts.get(key, 0) + 1
                seen[sig] = seen.get(sig, 0) + 1
                if sig not in known and sig not in new:
                    new[sig] = Finding(seed, mutations, root, found, answers, projected, sig)
        report["findings"][name] = dict(sorted(counts.items()))
    surfaces_built = built
    entries = []
    for sig, finding in new.items():
        surface = surfaces_built[finding.seed.surface]
        log(f"minimising {finding.seed.surface} {finding.seed.profile} {finding.classes}")
        minimised = minimise(surface, finding.seed, finding.root, sig)
        [(_, _, answers, _)] = evaluate(surface, [(finding.seed, minimised)])
        entries.append(entry_for(finding, surface.profile(finding.seed, minimised), minimised, answers))
    report["new"] = entries
    replayed = replay(baseline["entries"], surfaces_built)
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
    args = parser.parse_args(argv)
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
