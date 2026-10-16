"""Narrow the `ve_service` users a Lean change selects: an R1 experiment, off by default.

docs/test-architecture/cutoff/REPORT.md has the evidence, the measurement and the activation
status. tools/gate.py, the merge train and the nightlies never use this module: they run every
test. `tools/select_tests.py --cutoff RULE` is its one entry, for feedback runs only.

Two rules replace only the part of today's selection that runs because a test sent requests to
`ve_service` (`select_tests.service_impact`); everything else is selected as today: the tests
that read a changed file, run a one-shot Lean executable whose imports hold a changed module
(tests/test_units_lean_gate_w6a.py runs ve_conformance itself), run lake or lean, or read the
pins as data, and every unit the map does not cover.

* `modes`: ts-B2's per-mode rule (`select_tests.proposed_service_impact`): the recorded users of
  the modes whose `runMode` roots import the changed module.
* `answers=DIFF`: the users of the cases whose answers changed between the base build and the
  new one (`diff` below, of two `tools/answer_replay.py replay` runs), plus every unit that is unknown here: no complete
  request recording, a request the recorder could not replay, an explicit timeout, randomised
  inputs, or code that changed since the recording. A change to the service's request handling
  (lean/VE/Service/Protocol.lean, lean/Serve.lean, lean/VE/Json.lean) or to the Lean project
  selects every user, since one case per request cannot show it. A unit that read
  lean/checkers.lock only through the client's pin check (`LeanService._spawn`) is not selected
  by a pin change when the new build is pinned: its pin check then admits that build, as before.

`record` runs every unit under the coverage recorder with request recording on
(tools/test_map_recorder.py) and writes a directory that holds the coverage map of that run, the
request index and the recorded cases.
"""
from __future__ import annotations

import argparse
import ast
from collections.abc import Iterator
import contextlib
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import answer_replay
from answer_replay import digest_file, read_json, write_json
from layer_policy import ROOT
import select_tests
import source_graph
import test_map

VERSION = 1
SERVICE = "lean/.lake/build/bin/ve_service"
PIN_FILE = "lean/checkers.lock"
# Lean inputs whose effect one case per request cannot show: the request loop, batch budgets,
# handles and case splitting.
REQUEST_HANDLING = ("lean/VE/Service/Protocol.lean", "lean/Serve.lean", "lean/VE/Json.lean")
# Calls that make a test's inputs differ from run to run.
UNSEEDED = {"random": None, "secrets": None, "uuid": {"uuid1", "uuid4"}, "os": {"urandom"}}
RULES = ("modes", "answers=DIFF")


@contextlib.contextmanager
def service_rule(rule) -> Iterator[None]:
    """Select `ve_service` users by `rule` (the signature of `select_tests.service_impact`) inside the block."""
    original = select_tests.service_impact
    select_tests.service_impact = rule
    try:
        yield
    finally:
        select_tests.service_impact = original


# Recording


def unit_directory(unit: str) -> str:
    return unit.replace("/", "__")  # tools/test_map.py's name for a unit's records


def lines(path: Path) -> list[str]:
    """A record file's lines: split at newlines only, since a case text may hold U+2028."""
    return [line for line in path.read_text(encoding="utf-8").split("\n") if line]


def fold(requests: Path, units: list[str]) -> dict:
    """The request index of a recording directory the recorder wrote: per unit, its case keys and
    what makes it unknown; with every key's mode."""
    names = {unit_directory(unit): unit for unit in units}
    keys: dict[str, str] = {}
    folded: dict[str, dict] = {}
    for directory in sorted((requests / "units").glob("*")) if (requests / "units").is_dir() else ():
        unit = names.get(directory.name)
        if unit is None:
            continue
        entry = folded.setdefault(unit, {"keys": set(), "timed": False, "pins": set(), "unknown": set()})
        for path in directory.glob("*.jsonl"):
            for line in lines(path):
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    entry["unknown"].add("a truncated request record")
                    continue
                if record[0] == "q":
                    keys[record[2]] = record[1]
                    entry["keys"].add(record[2])
                    entry["timed"] |= bool(record[3])
                elif record[0] == "k":
                    entry["pins"].add(record[1])
                elif record[0] == "u":
                    entry["unknown"].add(record[1])
    order = sorted(keys)
    position = {key: i for i, key in enumerate(order)}
    return {"keys": order, "modes": [keys[key] for key in order],
            "units": {unit: {"keys": sorted(position[key] for key in entry["keys"]), "timed": entry["timed"],
                             "pins": sorted(entry["pins"]), "unknown": sorted(entry["unknown"])}
                      for unit, entry in sorted(folded.items())}}


def read_store(requests: Path, kind: str, key: str) -> dict[str, dict]:
    """Each recorded text of `kind` (the recorder writes one per process), by its key."""
    rows: dict[str, dict] = {}
    for path in sorted((requests / kind).glob("*.jsonl")) if (requests / kind).is_dir() else ():
        for line in lines(path):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue  # a process killed mid-line: its case is then missing, and its unit unknown
            rows.setdefault(row[key], row)
    return rows


def write_store(rows: dict[str, dict], output: Path) -> None:
    with gzip.open(output, "wt", encoding="utf-8") as handle:
        for name in sorted(rows):
            handle.write(json.dumps(rows[name], ensure_ascii=False) + "\n")


def handle_of(text: str) -> str | None:
    """The environment handle a case text names, if any."""
    lean_service = answer_replay.lean_service
    try:
        case = lean_service._decode_json(text)
    except ValueError:
        return None
    handle = case.get(lean_service.HANDLE_KEY) if type(case) is dict else None
    return handle if isinstance(handle, str) else None


def store_cases(requests: Path, index: dict, output: Path) -> tuple[int, int]:
    """Write the recorded cases and environments; a unit with a case whose text or environment
    was not recorded (a process that ended before writing it) becomes unknown."""
    bodies = read_store(requests, "bodies", "k")
    environments = read_store(requests, "environments", "d")
    cases = {key: bodies[key] for key in index["keys"] if key in bodies}
    named = {key: handle_of(row["c"]) for key, row in cases.items()}
    missing = {key for key in index["keys"] if key not in cases
               or (named[key] is not None and named[key] not in environments)}
    for entry in index["units"].values():
        if any(index["keys"][i] in missing for i in entry["keys"]):
            entry["unknown"].append("a case whose text or environment was not recorded")
    write_store({key: row for key, row in cases.items() if key not in missing}, output / "cases.jsonl.gz")
    used = {handle for key, handle in named.items() if handle is not None and key not in missing}
    write_store({digest: environments[digest] for digest in used}, output / "environments.jsonl.gz")
    return len(cases) - len(missing & cases.keys()), len(used)


def record(args: argparse.Namespace) -> int:
    commit = test_map.clean_head(args)
    if commit is None:
        return 2
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    work = Path(args.work or tempfile.mkdtemp(prefix="ve-cutoff-record-"))
    requests = work / "requests"
    if os.environ.get("VE_TESTMAP_REQUESTS") and os.environ.get("VE_TESTMAP_REQUESTS_UNIT"):
        # Inside another request recording, this run's requests are not that unit's: it is unknown.
        outer = Path(os.environ["VE_TESTMAP_REQUESTS"]) / "units" / os.environ["VE_TESTMAP_REQUESTS_UNIT"]
        outer.mkdir(parents=True, exist_ok=True)
        with (outer / f"{os.getpid()}.jsonl").open("a") as handle:
            handle.write(json.dumps(["u", "a nested request recording"]) + "\n")
    os.environ["VE_TESTMAP_REQUESTS"] = str(requests)
    os.environ.pop("VE_TESTMAP_REQUESTS_UNIT", None)  # this run's units are the units
    if not args.no_build:
        test_map.build_natives()
    selected = args.units or test_map.units()
    results = test_map.record_units(selected, work / "units", args.jobs, args.timeout)
    data = test_map.build_map(results, commit)
    test_map.write_map(data, output / "map.json.gz")
    index = fold(requests, selected)
    cases, environments = store_cases(requests, index, output)
    service = ROOT / SERVICE
    index.update(version=VERSION, commit=commit, map=digest_file(output / "map.json.gz"),
                 service=hashlib.sha256(service.read_bytes()).hexdigest() if service.exists() else None)
    write_json(index, output / "requests.json.gz")
    if not args.keep:
        shutil.rmtree(work, ignore_errors=True)
    print(f"recorded {len(results)} units, {cases} distinct cases and {environments} environments: {output}")
    return 0


# Selection


def load_recording(directory: Path) -> tuple[dict, dict]:
    """The request index and its coverage map, each checked against the other."""
    index = read_json(directory / "requests.json.gz")
    if index.get("version") != VERSION or digest_file(directory / "map.json.gz") != index.get("map"):
        raise ValueError(f"{directory}: not a request recording, or its map was replaced")
    data = test_map.load(directory / "map.json.gz")
    if data["commit"] != index["commit"]:
        raise ValueError(f"{directory}: the map and the request index name different commits")
    return index, data


def randomised(unit: str, graph: source_graph.Graph, root: Path = ROOT) -> str | None:
    """Why `unit`'s inputs may differ between runs (property tests, unseeded randomness), or None.

    Read with Python's own parser from the unit's own file and the test code it imports. Another test
    file's property tests do not run in the unit that imports a helper from it, so hypothesis counts
    in the unit's file and in helper modules; unseeded randomness counts in any of them."""
    files = {unit} | {path for path in graph.closure(unit)[0] if path.startswith("tests/")}
    for path in sorted(files):
        property_tests = path == unit or not Path(path).name.startswith("test_")
        try:
            tree = ast.parse((root / path).read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError):
            return f"{path} does not parse"
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                names = [alias.name for alias in node.names]
                module = node.module if isinstance(node, ast.ImportFrom) else None
                if property_tests and (module == "hypothesis" or (module or "").startswith("hypothesis.") or any(
                        name == "hypothesis" or name.startswith("hypothesis.") for name in names)):
                    return f"{path} uses hypothesis"
                if module in UNSEEDED and any(UNSEEDED[module] is None and name != "Random"
                                              or name in (UNSEEDED[module] or ()) for name in names):
                    return f"{path} imports {module}'s {', '.join(names)}"
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and isinstance(node.func.value, ast.Name) and node.func.value.id in UNSEEDED:
                module, name = node.func.value.id, node.func.attr
                if module == "random" and name == "Random" and (node.args or node.keywords):
                    continue  # a seeded generator
                if UNSEEDED[module] is None or name in UNSEEDED[module]:
                    return f"{path} calls {module}.{name}"
    return None


def pinned(build: str, after: str | None) -> bool:
    """Whether the pins of `after` (the working tree for None) admit `build` as ve_service."""
    try:
        text = (ROOT / PIN_FILE).read_text() if after is None else subprocess.run(
            ["git", "show", f"{after}:{PIN_FILE}"], cwd=ROOT, check=True, capture_output=True, text=True).stdout
        return build in json.loads(text)["ve_service"]
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError):
        return False


def unknown_units(index: dict, coverage: select_tests.Coverage, graph: source_graph.Graph,
                  uncertain: set[str], root: Path = ROOT) -> dict[str, str]:
    """The service users whose recorded requests do not decide what a Lean change does to them, with why."""
    found = {}
    for unit in sorted(coverage.service_users()):
        entry = index["units"].get(unit)
        status = coverage.status.get(unit, {})
        if unit not in coverage.recorded:
            found[unit] = f"recorded with exit {status.get('exit')}" + (" and opaque" if status.get("opaque") else "")
        elif entry is None or not entry["keys"]:
            found[unit] = "started ve_service but sent no recorded request"
        elif entry["unknown"]:
            found[unit] = entry["unknown"][0]
        elif entry["timed"]:
            found[unit] = "a request with an explicit timeout"
        elif unit in uncertain:
            found[unit] = "ran code that changed since the recording"
        elif (reason := randomised(unit, graph, root)) is not None:
            found[unit] = reason
    return found


class CutoffCoverage(select_tests.Coverage):
    """The recording's map, but a pin change selects no unit whose only pin reads were the client's."""

    def __init__(self, data: dict, path: Path, client_pin_readers: set[str]):
        super().__init__(data, path)
        self.client_pin_readers = client_pin_readers

    def readers(self, path: str) -> set[str]:
        found = super().readers(path)
        return found - self.client_pin_readers if path == PIN_FILE else found


def answers_rule(diff: dict, index: dict, unknown: set[str]):
    keys = index["keys"]
    changed = set(diff["changed"])
    users = {unit for unit, entry in index["units"].items() if any(keys[i] in changed for i in entry["keys"])}

    def rule(coverage: select_tests.Coverage, graph: source_graph.Graph, path: str) -> set[str]:
        del graph
        everyone = coverage.service_users()
        if path in REQUEST_HANDLING or not path.endswith(".lean"):
            return everyone
        return everyone & (users | unknown)

    return rule, users


def select_answers(diff_path: Path, paths: list[str], *, base: str, after: str | None, full: bool = False,
                   assume_fresh: bool = False, build: str | None = None, head_pinned: bool | None = None) -> dict:
    """The `answers` plan. `build` is the ve_service build the tests will run (default: the one built
    here); the diff's head must be it. Whether the pins of `after` admit it is read from them, unless
    `head_pinned` says (a measurement whose build was made on another architecture than the pins')."""
    diff = read_json(diff_path)
    recording = Path(diff["recording_dir"])
    index, data = load_recording(recording)
    if diff.get("version") != answer_replay.VERSION \
            or diff.get("recording") != digest_file(recording / "requests.json.gz"):
        raise ValueError(f"{diff_path} is not a replay diff of {recording}")
    build = build or hashlib.sha256((ROOT / SERVICE).read_bytes()).hexdigest()
    if diff["head"] != build:
        raise ValueError(f"{diff_path} replayed build {diff['head'][:16]}, but the tests run {build[:16]}")
    plain = select_tests.Coverage(data, recording / "map.json.gz")
    changes = select_tests.read_changes(sorted(set(paths)), base=base, after=after)
    graph = source_graph.load(ROOT).overlay({change.path: change.old for change in changes})
    uncertain = set() if assume_fresh else select_tests.uncertain_since(
        plain, graph, set(select_tests.units()), base)[0]
    unknown = unknown_units(index, plain, graph, uncertain)
    client_only = {unit for unit, entry in index["units"].items() if entry["pins"] == ["client"]}
    head_pinned = pinned(build, after) if head_pinned is None else head_pinned
    coverage = CutoffCoverage(data, recording / "map.json.gz", client_only if head_pinned else set())
    rule, users = answers_rule(diff, index, set(unknown))
    with service_rule(rule):
        plan = select_tests.select(paths, full=full, base=base, after=after, coverage=coverage,
                                   assume_fresh=assume_fresh)
    plan["cutoff"] = {"rule": "answers", "diff": str(diff_path), "changed_cases": len(diff["changed"]),
                      "changed_users": sorted(users), "unknown": unknown, "head_pinned": head_pinned,
                      "request_handling": sorted(set(paths) & set(REQUEST_HANDLING))}
    return plan


def select(rule: str, paths: list[str], **options) -> dict:
    """`select_tests.select` under a cutoff rule (`RULES`); the hook of `select_tests.py --cutoff`."""
    if rule == "modes":
        with service_rule(select_tests.proposed_service_impact):
            plan = select_tests.select(paths, **options)
        plan["cutoff"] = {"rule": "modes"}
        return plan
    if rule.startswith("answers="):
        options.pop("coverage", None)  # the recording's own map: its requests are recorded against it
        return select_answers(Path(rule.removeprefix("answers=")), paths, **options)
    raise ValueError(f"unknown cutoff rule {rule!r}; expected one of {', '.join(RULES)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record", help="record every unit's coverage and ve_service requests")
    rec.add_argument("--output", required=True, help="directory for the map, the index and the cases")
    rec.add_argument("--jobs", type=int, default=8)
    rec.add_argument("--timeout", type=float, default=test_map.UNIT_TIMEOUT, help="seconds per test file")
    rec.add_argument("--work", help="directory for the per-unit records (default: a temporary one)")
    rec.add_argument("--keep", action="store_true", help="keep the per-unit records")
    rec.add_argument("--allow-dirty", action="store_true")
    rec.add_argument("--no-build", action="store_true", help="binaries are already built")
    rec.add_argument("units", nargs="*", help="record only these units")
    diff = sub.add_parser("diff", help="the changed answers of two replays, for --cutoff answers=")
    diff.add_argument("recording", type=Path)
    diff.add_argument("base", type=Path)
    diff.add_argument("head", type=Path)
    diff.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "record":
        return record(args)
    data = answer_replay.diff(read_json(args.base), read_json(args.head))
    if data["recording"] != digest_file(args.recording / "requests.json.gz"):
        raise SystemExit(f"the replays are not of {args.recording}")
    data["recording_dir"] = str(args.recording.resolve())
    write_json(data, args.output)
    print(f"{len(data['changed'])} of {data['cases']} answers changed: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
