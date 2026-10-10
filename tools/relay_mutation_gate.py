"""Relay mutation gate: every Lean answer Python relays must refuse every mutant of a genuine answer.

    uv run python tools/relay_mutation_gate.py [--json OUT] [--route NAME ...]
    uv run python tools/relay_mutation_gate.py --record [TEST ...]

A *route* is one way `ve` reads a Lean answer:

* each mode of the persistent service (`ve.backends.service_schema.MODES`, checked against the modes the
  built service lists in its handshake), read by `LeanService.exchange` (the transport of `relay`);
* each one-shot runner call that a `ve` call site makes: every assurance-manifest binding of a runner other
  than `ve_service` whose operation has Lean call sites, and every call of the one-shot route reader
  (`run_route_cases`, `run_english_cases`, `read_rows`) outside `ve/backends/lean.py`, read by the call
  site's own function (`ONE_SHOT`).

Fixtures are the committed genuine requests in `tests/data/relay-gate-cases.jsonl` (`--record` writes it
from the requests a test run relays, `tests/route_case_recorder.py`, and the service corpus
`tests/lean_service_corpus.py`, keeping the smallest few cases of each answer shape). The gate asks the built Lean executables for their answers to those requests, so the
answers are always the current build's. Each field of each answer (every key to `DEPTH` levels; lists
through their first and last element) is mutated:

* `drop`: the field removed;
* `empty`: a non-empty string, array or object made empty;
* `duplicate`: an element of an array repeated, and a key of an object written twice in the line;
* `retype`: the value replaced by one of each other JSON type (null, true, 7, 7.5 for an integer, "7",
  [], {});
* `rebind`: a value the request names (a string that occurs in the case, the result's position, its
  case digest, the nonce, the envelope's counts) replaced by one the request does not hold.

Each mutant goes through the route's own reader exactly as the genuine answer does (the service client's
`exchange`, or the one-shot call site with a stand-in runner that prints the mutant). The route's error is
`CheckerUnavailable`: a mutant must raise it. A mutant that is returned is *accepted*; one that raises
another `VEError` is *misread* (a malformed answer taken as Lean's rejection); any other exception is a
*crash*. A field every retype of which is accepted is reported as *untyped*, and so is a manifest
response type `json`.

The gate fails (exit 1) on: a route without an `ok` fixture; a genuine answer its reader refuses; an
accepted, misread or untyped mutant that `tools/relay-gate-allow.json` does not list; a crash; an
allow-list entry that matches nothing (each entry names a route, a mutation and a path pattern, `*` for
any list position, with its reason and whether it is by design or a follow-up). `--json` writes the
counts and findings (the saved evidence of `docs/merge-tooling.md`).
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from copy import deepcopy
from fnmatch import fnmatchcase
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve.backends import lean as lean_backend  # noqa: E402
from ve.backends.lean_service import DEFAULT_EXECUTABLE, LeanService, _Deadline  # noqa: E402
from ve.backends.service_schema import MODES  # noqa: E402
from ve.errors import CheckerUnavailable, VEError  # noqa: E402

CASES = ROOT / "tests/data/relay-gate-cases.jsonl"
ALLOW = ROOT / "tools/relay-gate-allow.json"
BIN = ROOT / "lean/.lake/build/bin"
MANIFEST = ROOT / "ve/assurance-manifest.json"
DEPTH = 8
PER_SHAPE = 2
FRESH = "zz-not-in-request"
# The test files `--record` runs by default: together they relay every route.
RECORD_TESTS = (
    "tests/test_lean_service.py", "tests/test_relay.py", "tests/test_english_lean_route.py",
    "tests/test_english_e2_relay.py", "tests/test_stage2_graph.py", "tests/test_stage2_bundle.py",
    "tests/test_stage2_norms.py", "tests/test_senses_route.py", "tests/test_bundle.py",
    "tests/test_speech_source_relay.py", "tests/test_w6a_certificate_steps.py", "tests/test_argument.py",
    "tests/test_argument_adversarial.py", "tests/test_readings_s1_lean.py", "tests/test_readings_s2_lean.py",
    "tests/test_readings_s1_python.py", "tests/test_units_relay_w6a.py", "tests/test_parser_renderer.py",
    "tests/test_readings_route_relay.py", "tests/test_document_lean_switch.py", "tests/test_lean_handles.py",
    "tests/test_discourse_lean.py", "tests/test_reports_lean.py", "tests/test_risk_fixtures.py",
    "tests/test_speech_acts_lean.py", "tests/test_readings_nd_lean.py", "tests/test_metered_lean.py",
    "tests/test_evaluate_search.py", "tests/test_closure_certificates.py", "tests/test_p0_three_way.py",
    "tests/test_stage2_dispatch.py", "tests/test_stage2_faults.py", "tests/test_stage2_readings.py",
)
# Calls that read a one-shot runner's rows; a `ve` call site of one is a route of its own.
ONE_SHOT_READERS = ("run_route_cases", "run_english_cases", "read_rows")
DROP = object()


# Mutations


def _nodes(value, path=()):
    """(path, value) for `value` and every field below it to DEPTH levels; lists through their first and last
    element."""
    yield path, value
    if len(path) >= DEPTH:
        return
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _nodes(item, path + (key,))
    elif isinstance(value, list) and value:
        for index in sorted({0, len(value) - 1}):
            yield from _nodes(value[index], path + (index,))


def _replace(root, path, new):
    copy = deepcopy(root)
    node = copy
    for step in path[:-1]:
        node = node[step]
    if new is DROP:
        del node[path[-1]]
    else:
        node[path[-1]] = new
    return copy


def _type(value) -> str:
    if value is None:
        return "null"
    if type(value) is bool:
        return "boolean"
    if type(value) is int:
        return "integer"
    if type(value) is float:
        return "number"
    if type(value) is str:
        return "string"
    return "array" if isinstance(value, list) else "object"


RETYPES = {"null": None, "boolean": True, "integer": 7, "string": "7", "array": [], "object": {}}


def _strings(value) -> set[str]:
    """Every string a request holds, as a value or a key."""
    found, pending = set(), [value]
    while pending:
        item = pending.pop()
        if type(item) is str:
            found.add(item)
        elif isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, dict):
            found.update(item)
            pending.extend(item.values())
    return found


class Mutant:
    __slots__ = ("kind", "path", "value", "duplicate_key")

    def __init__(self, kind, path, value=None, duplicate_key=None):
        self.kind, self.path, self.value, self.duplicate_key = kind, path, value, duplicate_key

    def pattern(self, prefix=()) -> str:
        return "/".join("*" if type(step) is int else str(step) for step in self.path[len(prefix):]) or "."


def mutants(answer, named: set[str], rebind_ints: dict[tuple, int]) -> list[tuple[Mutant, object]]:
    """[(mutant, mutated answer)] for every field of `answer`: drop, empty, duplicate, retype, rebind.
    `named` are the strings the request holds; `rebind_ints` maps the paths of integers bound to the request
    (positions, counts) to a value the request does not give them."""
    out = []
    for path, value in _nodes(answer):
        if not path:
            continue
        if isinstance(path[-1], str):
            out.append((Mutant("drop", path), _replace(answer, path, DROP)))
        if value not in ("", [], {}) and isinstance(value, (str, list, dict)):
            # An emptied name the request gives is a rebind: "" names nothing the request holds.
            kind = "rebind" if type(value) is str and value in named and "" not in named else "empty"
            out.append((Mutant(kind, path, "" if kind == "rebind" else None), _replace(answer, path, type(value)())))
        if isinstance(value, list) and value:
            out.append((Mutant("duplicate", path), _replace(answer, path, value + [deepcopy(value[0])])))
        if isinstance(value, dict) and value:
            out.append((Mutant("duplicate", path, duplicate_key=next(iter(value))), answer))
        for kind, new in RETYPES.items():
            if kind != _type(value):
                out.append((Mutant("retype", path, kind), _replace(answer, path, new)))
        if type(value) is int:
            out.append((Mutant("retype", path, "number"), _replace(answer, path, 7.5)))
        if type(value) is str and value in named:
            out.append((Mutant("rebind", path), _replace(answer, path, FRESH)))
        if path in rebind_ints:
            out.append((Mutant("rebind", path), _replace(answer, path, rebind_ints[path])))
    return out


def dumps(value, duplicate_at=None, key=None, path=()) -> str:
    """Compact JSON text of `value`; the object at `duplicate_at` writes its field `key` twice."""
    if isinstance(value, dict):
        items = [json.dumps(k, ensure_ascii=False) + ":" + dumps(v, duplicate_at, key, path + (k,))
                 for k, v in value.items()]
        if path == duplicate_at:
            items.insert(0, json.dumps(key, ensure_ascii=False) + ":" + dumps(value[key]))
        return "{" + ",".join(items) + "}"
    if isinstance(value, list):
        return "[" + ",".join(dumps(v, duplicate_at, key, path + (i,)) for i, v in enumerate(value)) + "]"
    return json.dumps(value, ensure_ascii=False)


def _text(mutant: Mutant, answer) -> str:
    if mutant.duplicate_key is not None:
        return dumps(answer, mutant.path, mutant.duplicate_key)
    return dumps(answer)


# Routes


def _calls(module_path: Path, names) -> list[str]:
    """`module:function` of every call of one of `names` in a module."""
    tree = ast.parse(module_path.read_text(), str(module_path))
    module = ".".join(module_path.relative_to(ROOT).with_suffix("").parts)
    sites = []

    def visit(node, scope):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                visit(child, scope + [child.name])
            elif isinstance(child, ast.ClassDef):
                visit(child, scope + [child.name])
            else:
                if isinstance(child, ast.Call):
                    func = child.func
                    name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
                    if name in names:
                        sites.append(f"{module}:{'.'.join(scope) or '<module>'}")
                visit(child, scope)
    visit(tree, [])
    return sites


def _runners(site: str) -> set[str]:
    """The `runner=` literals of the Lean calls in the function `module:qualname`."""
    module, qualname = site.split(":")
    tree = ast.parse((ROOT / (module.replace(".", "/") + ".py")).read_text())
    node = tree
    for name in qualname.split("."):
        node = next(child for child in ast.iter_child_nodes(node)
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and child.name == name)
    return {keyword.value.value for call in ast.walk(node) if isinstance(call, ast.Call)
            for keyword in call.keywords if keyword.arg == "runner" and isinstance(keyword.value, ast.Constant)}


def one_shot_inventory() -> dict[str, list[str]]:
    """{route: [why it is a route]} for every one-shot runner a `ve` call site reads: each manifest binding
    of an operation whose declared call sites name that binding's runner, and each call of the one-shot route
    reader outside its module."""
    manifest = json.loads(MANIFEST.read_text())
    found: dict[str, list[str]] = defaultdict(list)
    for operation in manifest["operations"]:
        sites = operation.get("lean_call_sites") or []
        runners = set().union(*(_runners(site) for site in sites)) if sites else set()
        for binding in (operation.get("lean") or {}).get("bindings", ()):
            if binding["executable"] != "ve_service" and binding["executable"] in runners:
                route = f"{binding['executable']}:{binding['mode']}:{operation['id']}"
                found[route].append(f"manifest {operation['id']} {binding['executable']} {binding['mode']!r} "
                                    f"called from {', '.join(sites)}")
    for path in sorted((ROOT / "ve").rglob("*.py")):
        if path == ROOT / "ve/backends/lean.py":
            continue
        for site in _calls(path, ONE_SHOT_READERS):
            found[f"call:{site}"].append(f"one-shot reader call in {site}")
    return dict(found)


class _Replay(LeanService):
    """The service client with its process replaced by one answer line: `exchange` reads the line through
    its own decode, nonce and schema checks, and retries a failure once, as with a real process. The line
    is answered with the request's nonce unless the mutant rebinds or drops it."""

    def __init__(self):
        super().__init__(DEFAULT_EXECUTABLE, retries=1)
        self.answer = None
        self.mutant = None
        self.nonce = None

    def _ensure(self):
        pass

    def _stop(self, graceful):
        pass

    def _stderr_tail(self):
        return ""

    def _deadline(self, mode, size, cases, timeout):
        return _Deadline(time.monotonic() + 3600.0, mode=mode)

    def _write_all(self, data, deadline):
        self.nonce = json.loads(data)["id"]

    def _read_line(self, deadline):
        answer = self.answer
        if self.mutant is None or self.mutant.path[:1] != ("id",):
            if isinstance(answer, dict) and "id" in answer:
                answer = {**answer, "id": self.nonce}
        return (_text(self.mutant, answer) if self.mutant is not None else dumps(answer)).encode()


def _exchange_outcome(replay: _Replay, mode: str, text: str) -> tuple[str, str]:
    try:
        replay.exchange(mode, text, 1)
    except CheckerUnavailable as exc:
        return "refused", exc.message[:160]
    except VEError as exc:
        return "misread", f"{type(exc).__name__}: {exc.message[:160]}"
    except Exception as exc:  # noqa: BLE001 - a crash is a finding
        return "crash", _crash(exc)
    return "accepted", ""


def _service_answers(executable: Path, mode: str, cases: list[str]) -> list[dict]:
    """The service's single-case answers to `cases` (case texts), from one real exchange per case."""
    answers = []
    with LeanService(executable) as service:
        for text in cases:
            try:
                _, response = service.exchange(mode, "[" + text + "]", 1)
            except VEError as exc:
                response = {"status": "error", "error": exc.message}
            answers.append(response)
    return answers


def _case_kind(case) -> str:
    return case.get("kind", "") if isinstance(case, dict) and type(case.get("kind")) is str else ""


def _shape(case, row) -> tuple:
    status = row.get("status") if isinstance(row, dict) else None
    return (_case_kind(case), str(status), tuple(sorted(row)) if isinstance(row, dict) else ())


# One-shot routes: how a call site reads its runner's answer to a recorded case.


def _environment(data):
    from ve.environment import Environment
    return Environment.from_dict(data)


def _metered(operation):
    def call(case, executable):
        return lean_backend.run(operation, executable, [case], runner="ve_metered",
                                timeout=lean_backend.configured_timeout(lean_backend.ROUTE_TIMEOUT))
    return call


def _graph_compose(case, executable):
    return lean_backend.run("graph.compose", executable, [case], runner="ve_conformance",
                            mode="route" if case.get("kind") == "certificate" else "check-certificate",
                            timeout=lean_backend.configured_timeout(lean_backend.ROUTE_TIMEOUT))


def _bundle(case, executable):
    from ve.bundle import lean_bundle_verdict
    return lean_bundle_verdict(executable, case["environment"], case["lemmas"], case.get("document"))


def _senses(case, executable):
    from ve.backends import senses
    env = _environment(case["environment"])
    packs = [text.encode() for text in case["packs"]]
    if "fences" in case:
        return senses.read_fences(env, case["fences"], packs, own=case["own"], defaults=case.get("defaults"),
                                  budget=case["budget"], executable=executable, fence_ids=case["fence_ids"],
                                  reading_set_units=case["reading_set_units"])
    return senses.read(env, case["source"], packs, own=case["own"], overlay=case.get("overlay"),
                       budget=case["budget"], executable=executable)


def _senses_request(case):
    from ve.backends import senses
    env = _environment(case["environment"])
    return senses.request(env, case.get("source"), case["packs"], own=case["own"], overlay=case.get("overlay"),
                          budget=case["budget"], fences=case.get("fences"), defaults=case.get("defaults"),
                          fence_ids=case.get("fence_ids"), reading_set_units=case.get("reading_set_units"))


def _speech_source(case, executable):
    from ve.backends.speech_source import decide_source
    document = case["document"]
    return decide_source(document["metadata"], document["source"], document["fences"],
                         resolved_fences=document.get("resolved_fences"), premise_status=case.get("premise_status"),
                         executable=executable)


# route: (runner, mode, case kinds or None for any, call, rebuild the case the call sends or None if verbatim)
ONE_SHOT = {
    "ve_metered::evaluate": ("ve_metered", "", {"evaluate-budgeted"}, _metered("evaluate"), None),
    "ve_metered::countermodel.search": ("ve_metered", "", {"non-vacuity"}, _metered("countermodel.search"), None),
    "ve_conformance:route:graph.compose": ("ve_conformance", "route", {"certificate"}, _graph_compose, None),
    "ve_conformance:check-certificate:graph.compose": ("ve_conformance", "check-certificate", None,
                                                       _graph_compose, None),
    "ve_conformance:route:bundle.check": ("ve_conformance", "route", {"bundle"}, _bundle, None),
    "ve_senses_route::senses.read": ("ve_senses_route", "", None, _senses, _senses_request),
    "call:ve.backends.speech_source:decide_source": ("ve_speech_acts_route", "-", {"speech-source"},
                                                     _speech_source, None),
}


def _one_shot_route(runner, mode, case) -> str | None:
    for route, (r, m, kinds, _, _) in ONE_SHOT.items():
        if r == runner and m == mode and (kinds is None or _case_kind(case) in kinds):
            return route
    return None


def _run_runner(runner: str, mode: str, case) -> tuple[int, bytes]:
    from ve.wire import canonical_json
    done = subprocess.run([str(BIN / runner), *([mode] if mode else [])], input=canonical_json([case]),
                          capture_output=True, timeout=lean_backend.configured_timeout(lean_backend.ROUTE_TIMEOUT))
    return done.returncode, done.stdout


class _StandIn:
    """A runner that prints one prepared answer and exits with the genuine run's status."""

    def __init__(self, directory: Path):
        self.output = directory / "answer"
        self.path = directory / "runner"
        self.path.write_text(f"#!/bin/sh\ncat > /dev/null\ncat '{self.output}'\nexit $(cat '{self.output}.status')\n")
        self.path.chmod(0o755)

    def set(self, text: bytes, status: int):
        self.output.write_bytes(text)
        Path(f"{self.output}.status").write_text(str(status))


def _call_outcome(call, case, executable) -> tuple[str, str]:
    try:
        call(case, executable)
    except CheckerUnavailable as exc:
        return "refused", exc.message[:160]
    except VEError as exc:
        return "misread", f"{type(exc).__name__}: {exc.message[:160]}"
    except Exception as exc:  # noqa: BLE001 - a crash is a finding
        return "crash", _crash(exc)
    return "accepted", ""


def _crash(exc: BaseException) -> str:
    """The exception and the innermost `ve` line it was raised at."""
    import traceback
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if "/ve/" in f.filename]
    where = f" at {Path(frames[-1].filename).relative_to(ROOT)}:{frames[-1].lineno}" if frames else ""
    return f"{type(exc).__name__}: {str(exc)[:160]}{where}"


# Fixtures


def load_cases(path: Path = CASES) -> list[list]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def record(tests: list[str], out: Path = CASES, per_shape: int = PER_SHAPE) -> int:
    """Run `tests` with the recorder, then keep the smallest `per_shape` cases of each answer shape of
    each route (shapes read from the current build's answers)."""
    with tempfile.TemporaryDirectory(prefix="relay-gate-record-") as directory:
        sys.path.insert(0, str(ROOT / "tools"))
        import nested_pytest
        done = subprocess.run(nested_pytest.command(["-q", "-p", "tests.route_case_recorder", *tests],
                                                    workers=int(os.environ.get("RELAY_GATE_WORKERS", "8"))),
                              cwd=ROOT, env=nested_pytest.environment(os.environ, VE_RELAY_CASES=directory))
        if done.returncode not in (0, 1):
            print(f"relay_mutation_gate: recording run failed ({done.returncode})", file=sys.stderr)
            return 2
        seen: dict[tuple, None] = {}
        for path in sorted(Path(directory).glob("relay-*.jsonl")):
            for line in path.read_text().splitlines():
                seen.setdefault(tuple(json.loads(line)), None)
    # The service corpus of every mode and result kind (`tests/lean_service_corpus.py`) as well.
    from tests.lean_service_corpus import corpus
    for mode, cases in corpus().items():
        for case in cases:
            seen.setdefault(("service", mode, json.dumps(case, separators=(",", ":"))), None)
    by_route: dict[str, list[tuple]] = defaultdict(list)
    for row in seen:
        if row[0] == "service":
            by_route[f"service:{row[1]}"].append(row)
        else:
            route = _one_shot_route(row[1], row[2], json.loads(row[3]))
            if route is not None:
                by_route[route].append(row)
    kept = []
    for route, rows in sorted(by_route.items()):
        rows.sort(key=lambda row: (len(row[-1]), row[-1]))
        shapes: Counter = Counter()
        if route.startswith("service:"):
            mode = route.split(":", 1)[1]
            answers = _service_answers(DEFAULT_EXECUTABLE, mode, [row[2] for row in rows])
            for row, answer in zip(rows, answers):
                result = answer["results"][0]["result"] if answer.get("status") != "error" else {}
                shape = _shape(json.loads(row[2]), result)
                if answer.get("status") != "error" and shapes[shape] < per_shape:
                    shapes[shape] += 1
                    kept.append(["service", mode, json.loads(row[2])])
        else:
            for row in rows:
                case = json.loads(row[3])
                status, stdout = _run_runner(row[1], row[2], case)
                try:
                    [answer] = json.loads(stdout)
                except ValueError:
                    continue
                shape = _shape(case, answer)
                if status in (0, 1) and shapes[shape] < per_shape:
                    shapes[shape] += 1
                    kept.append(["one-shot", row[1], row[2], case])
    out.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in kept))
    print(f"relay_mutation_gate: kept {len(kept)} cases of {len(seen)} recorded in {out.relative_to(ROOT)}")
    return 0


# The gate


def _patterns(entry) -> list[str]:
    return entry["path"] if isinstance(entry["path"], list) else [entry["path"]]


def _allowed(entries, route, mutation, pattern):
    """The allow-list entry that lists this accepted mutant, marking the path pattern it matched as used."""
    candidates = [entry for entry in entries
                  if fnmatchcase(route, entry["route"]) and fnmatchcase(mutation, entry["mutation"])]
    # A listed path is first read literally (its `*` the list position of a finding's path), then as a pattern.
    for literal in (True, False):
        for entry in candidates:
            for listed in _patterns(entry):
                if listed == pattern if literal else fnmatchcase(pattern, listed):
                    entry.setdefault("_used", set()).add(listed)
                    return entry
    return None


def _service_rebind_ints(answer) -> dict[tuple, int]:
    """The integers of a single-case service answer bound to the request: its position and counts."""
    ints = {("results", 0, "index"): 1}
    for key, value in (answer.get("counts") or {}).items():
        if type(value) is int:
            ints[("counts", key)] = value + 1
    return ints


def _digest_rebind(answer) -> list[tuple[Mutant, object]]:
    """The answer bound to the digest of another case."""
    other = hashlib.sha256(b"another case").hexdigest()
    return [(Mutant("rebind", ("results", 0, "digest")), _replace(answer, ("results", 0, "digest"), other))]


def run_gate(routes_wanted=None) -> dict:
    cases = load_cases()
    entries = json.loads(ALLOW.read_text())["entries"]
    report = {"routes": {}, "findings": [], "failures": []}
    fixtures: dict[str, list] = defaultdict(list)
    for row in cases:
        if row[0] == "service":
            fixtures[f"service:{row[1]}"].append(row[2])
        else:
            route = _one_shot_route(row[1], row[2], row[3])
            if route is None:
                report["failures"].append(f"fixture for no route: {row[1]} {row[2]!r} {_case_kind(row[3])!r}")
            else:
                fixtures[route].append(row[3])
    with LeanService(DEFAULT_EXECUTABLE) as service:
        listed = service.start().get("modes")
    if sorted(listed) != sorted(MODES):
        report["failures"].append(f"the service lists modes {sorted(set(listed) ^ set(MODES))} the client "
                                  f"does not, or the other way round")
    inventory = one_shot_inventory()
    for route in inventory:
        if route not in ONE_SHOT:
            report["failures"].append(f"route {route} ({'; '.join(inventory[route])}) has no reader in ONE_SHOT")
    for route in ONE_SHOT:
        if route not in inventory:
            report["failures"].append(f"ONE_SHOT reader {route} is no route of `ve` any more")
    routes = [f"service:{mode}" for mode in MODES] + list(ONE_SHOT)
    for route in routes:
        if routes_wanted and route not in routes_wanted:
            continue
        started = time.monotonic()
        stats = Counter()
        open_ = []
        if route.startswith("service:"):
            stats, open_ = _gate_service(route, fixtures.get(route, []), entries, report)
        else:
            stats, open_ = _gate_one_shot(route, fixtures.get(route, []), entries, report)
        if stats["ok_fixtures"] == 0:
            report["failures"].append(f"route {route} has no fixture with an ok answer")
        stats["seconds"] = round(time.monotonic() - started, 1)
        report["routes"][route] = dict(stats)
        report["findings"].extend(open_)
    for item in manifest_untyped():
        if (not routes_wanted or item["route"] in routes_wanted) and \
                not _allowed(entries, item["route"], "untyped", item["field"]):
            report["findings"].append({"route": item["route"], "mutation": "untyped", "path": item["field"],
                                       "outcome": "untyped", "detail": f"manifest response type {item['type']}"})
    for entry in entries:
        used = entry.pop("_used", set())
        if routes_wanted and not any(fnmatchcase(route, entry["route"]) for route in routes_wanted):
            continue
        for listed in _patterns(entry):
            if listed not in used:
                report["failures"].append(f"allow-list path matches nothing: {entry['id']} {entry['route']} "
                                          f"{entry['mutation']} {listed}")
    for finding in report["findings"]:
        report["failures"].append(f"{finding['outcome']} {finding['route']} {finding['mutation']} "
                                  f"{finding['path']}: {finding['detail']}")
    report["totals"] = dict(sum((Counter({k: v for k, v in s.items() if k != "seconds"})
                                 for s in report["routes"].values()), Counter()))
    return report


def _record(stats, findings, entries, route, mutant, outcome, detail, pattern, seen_untyped):
    stats["mutants"] += 1
    stats[outcome] += 1
    if outcome == "refused":
        return
    if outcome == "crash":
        findings.append({"route": route, "mutation": mutant.kind, "path": pattern, "outcome": outcome,
                         "detail": detail})
        return
    if _allowed(entries, route, mutant.kind, pattern):
        stats["allowed"] += 1
        return
    key = (route, mutant.kind, pattern, outcome)
    if key not in seen_untyped:
        seen_untyped.add(key)
        findings.append({"route": route, "mutation": mutant.kind, "path": pattern, "outcome": outcome,
                         "detail": detail or f"{mutant.kind} {mutant.value or ''}".strip()})


def _untyped(route, accepted_retypes, entries, findings, stats):
    """A field every retype of which was accepted (on some fixture) has no type."""
    for pattern, kinds in accepted_retypes.items():
        if len(kinds) >= len(RETYPES) - 1:
            stats["untyped"] += 1
            if not _allowed(entries, route, "untyped", pattern):
                findings.append({"route": route, "mutation": "untyped", "path": pattern, "outcome": "untyped",
                                 "detail": "every retype is accepted"})


def _gate_service(route, cases, entries, report):
    mode = route.split(":", 1)[1]
    stats, findings, seen = Counter(), [], set()
    texts = [json.dumps(case, separators=(",", ":")) for case in cases]
    answers = _service_answers(DEFAULT_EXECUTABLE, mode, texts) if texts else []
    replay = _Replay()
    accepted_retypes: dict[str, set] = defaultdict(set)
    for case, text, answer in zip(cases, texts, answers):
        stats["fixtures"] += 1
        replay.answer, replay.mutant = answer, None
        outcome, detail = _exchange_outcome(replay, mode, "[" + text + "]")
        if outcome != "accepted":
            report["failures"].append(f"genuine answer refused on {route}: {outcome} {detail}")
            continue
        if answer.get("status") == "error":
            continue
        bound = answer["results"][0]
        if "code" not in bound and bound["result"].get("status") != "error":  # not a rejection
            stats["ok_fixtures"] += 1
        named = _strings(case) | {mode}
        found = mutants(answer, named, _service_rebind_ints(answer)) + _digest_rebind(answer)
        found.append((Mutant("rebind", ("id",)), {**answer, "id": FRESH}))
        for mutant, mutated in found:
            replay.answer, replay.mutant = mutated, mutant
            outcome, detail = _exchange_outcome(replay, mode, "[" + text + "]")
            pattern = mutant.pattern()
            if mutant.kind == "retype" and outcome == "accepted":
                accepted_retypes[pattern].add(mutant.value)
            _record(stats, findings, entries, route, mutant, outcome, detail, pattern, seen)
    _untyped(route, accepted_retypes, entries, findings, stats)
    return stats, findings


def _gate_one_shot(route, cases, entries, report):
    runner, mode, _, call, rebuild = ONE_SHOT[route]
    stats, findings, seen = Counter(), [], set()
    accepted_retypes: dict[str, set] = defaultdict(set)
    with tempfile.TemporaryDirectory(prefix="relay-gate-") as directory:
        stand_in = _StandIn(Path(directory))
        for case in cases:
            stats["fixtures"] += 1
            if rebuild is not None and rebuild(case) != case:
                report["failures"].append(f"fixture of {route} is not the case its call site sends")
                continue
            status, stdout = _run_runner(runner, mode, case)
            stand_in.set(stdout, status)
            outcome, detail = _call_outcome(call, case, stand_in.path)
            if outcome != "accepted":
                report["failures"].append(f"genuine answer refused on {route}: {outcome} {detail}")
                continue
            rows = json.loads(stdout)
            if rows[0].get("status") == "ok":
                stats["ok_fixtures"] += 1
            named = _strings(case)
            for mutant, mutated in mutants(rows, named, {}):
                stand_in.set(_text(mutant, mutated).encode(), status)
                outcome, detail = _call_outcome(call, case, stand_in.path)
                pattern = mutant.pattern()
                if mutant.kind == "retype" and outcome == "accepted":
                    accepted_retypes[pattern].add(mutant.value)
                _record(stats, findings, entries, route, mutant, outcome, detail, pattern, seen)
    _untyped(route, accepted_retypes, entries, findings, stats)
    return stats, findings


def manifest_untyped() -> list[dict]:
    """Manifest response types that admit any JSON value (`json`), per binding of a one-shot route."""
    manifest = json.loads(MANIFEST.read_text())
    found = []
    for operation in manifest["operations"]:
        if not operation.get("lean_call_sites"):
            continue
        for binding in (operation.get("lean") or {}).get("bindings", ()):
            for field, spec in binding.get("response", {}).items():
                if "json" in spec:
                    found.append({"route": f"{binding['executable']}:{binding['mode']}:{operation['id']}",
                                  "field": field, "type": spec})
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--record", nargs="*", metavar="TEST", help="rewrite the fixture cases from a test run")
    parser.add_argument("--json", type=Path, help="write the report here")
    parser.add_argument("--route", action="append", help="gate only this route (repeatable)")
    args = parser.parse_args(argv)
    if args.record is not None:
        return record(args.record or list(RECORD_TESTS))
    report = run_gate(set(args.route) if args.route else None)
    if args.json:
        args.json.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    for route, stats in report["routes"].items():
        print(f"{route}: {stats.get('fixtures', 0)} fixtures, {stats.get('mutants', 0)} mutants, "
              f"{stats.get('refused', 0)} refused, {stats.get('allowed', 0)} allowed, {stats.get('seconds')} s")
    for failure in report["failures"]:
        print(f"relay_mutation_gate: {failure}", file=sys.stderr)
    print(f"relay_mutation_gate: {len(report['routes'])} routes, {report['totals'].get('mutants', 0)} mutants, "
          f"{len(report['failures'])} failures")
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
