"""ADR 0001's census: every string and integer leaf of every Lean response shape, and how it is bound today.

    uv run python tools/binding_census.py --write          # the census from the shapes and the recorded evidence
    uv run python tools/binding_census.py --check          # exit 1 if the committed census is stale
    uv run python tools/binding_census.py --show [MODE]    # the census view, each hand check at its current line
    uv run python tools/binding_census.py --record [TEST ...]   # re-record the answers and re-probe (slow, live)
    uv run python tools/binding_census.py --probe DIR [TEST ...] # the probe run alone, appending to DIR
                                         [--wire]                # mutants delivered before the shape check
    uv run python tools/binding_census.py --collect DIR          # record from a probe run's DIR
    uv run python tools/binding_census.py --answers              # re-ask every recorded case (a Lean change)

**The shapes' part** comes from the Lean-rendered schemas (`ve/backends/lean_service_schema/`), read by the
generic checker `ve.backends.shape_binding`: every leaf of every mode's row with ADR 0001's class (bound and
its relation, closed domain, none), its format keywords and its schema site; every array with what binds its
length and positions; the delegated branches. Leaves inside a tagged grammar (formulas, terms, kinds) are listed
once per grammar (`grammars`); each mode lists where a grammar occurs and whether an ancestor binds it whole.

**How it is bound today** comes from two recordings (`--record`, which needs the built service):

* `ANSWERS`: genuine answers of every mode, the requests of `tests/data/relay-gate-cases.jsonl` asked of the
  current build, and the answers the probed tests received. `observed` counts each leaf's instances in them,
  and `tests/test_shape_binding_mutants.py` mutates them;
* `PROBES`: what the Python hand path does with every shape-generated mutant of a genuine answer, delivered
  after the shape check (`tests/binding_probe.py`, run over `PROBE_TESTS`): the hand check that refused it
  (`file`, `function`, the raising line's text and its line at the probe's commit), or that the hand path
  accepted it, misread it or crashed on it; with the generic checker's verdict on the same mutant.

A leaf of class none is "bound today" by the hand checks that refused a mutant of it that the generic checker
accepts; it is "unbound" if every probed mutant of it passed both, and "not probed" if no probed test reached
it. `hand_binders` groups the refusals by hand check: a check that refused a mutant the generic checker accepts
carries the binding; one whose every refusal the generic checker also makes is covered at the probed fields.
`rd9` places each of the 47 fields of the rd-9 binding audit (reviews/rd-9-binding-audit.md, transcribed in
`RD9`) in the census.

The census holds no line numbers of the current tree, so an edit elsewhere in a route module leaves it valid:
a hand check is named by its file, function and line text (`--show` finds it), and by its line at the probe's
commit. `--check` regenerates the census and compares it. A cited line text that is no longer in its function
is marked `present: false` (the binder changed: re-probe), so `--write` records it and no edit of a route
module waits for a probe run. The census is a measurement (ADR 0001: "the census proves that every leaf is
classified, not that it is correctly classified"); the tests that can fail are
`tests/test_shape_binding_mutants.py` (the shapes refuse what the classification says they refuse) and
`tests/test_binding_census.py`.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve.backends import shape_binding  # noqa: E402
from ve.backends.service_schema import DIRECTORY, MODES  # noqa: E402

CENSUS = ROOT / "docs/test-architecture/binding-census.json"
VIEW = ROOT / "docs/test-architecture/binding-census.md"
ANSWERS = ROOT / "tests/data/binding-answers.jsonl.gz"
PROBES = ROOT / "docs/test-architecture/binding-probes.jsonl.gz"
RD9 = ROOT / "docs/test-architecture/rd9-binding-rows.json"
CASES = ROOT / "tests/data/relay-gate-cases.jsonl"
# The tests the probe runs: together they relay every mode through its consumers (the relay gate's recording
# set, the routes' own Lean tests and the hand fuzz tests whose binders this census looks for).
PROBE_TESTS = (
    "tests/test_lean_service.py", "tests/test_relay.py", "tests/test_english_lean_route.py",
    "tests/test_english_e2_relay.py", "tests/test_stage2_graph.py", "tests/test_stage2_bundle.py",
    "tests/test_stage2_norms.py", "tests/test_stage2_parse.py", "tests/test_stage2_validation.py",
    "tests/test_stage2_readings.py", "tests/test_bundle.py", "tests/test_speech_source_relay.py",
    "tests/test_w6a_certificate_steps.py", "tests/test_argument.py", "tests/test_readings_s1_lean.py",
    "tests/test_readings_s2_lean.py", "tests/test_units_relay_w6a.py", "tests/test_parser_renderer.py",
    "tests/test_readings_route_relay.py", "tests/test_document_lean_switch.py", "tests/test_discourse_lean.py",
    "tests/test_discourse_answer.py", "tests/test_reports_lean.py", "tests/test_risk_lean_route.py",
    "tests/test_risk_profile.py", "tests/test_speech_acts_lean.py", "tests/test_readings_nd_lean.py",
    "tests/test_metered_lean.py", "tests/test_evaluate_search.py", "tests/test_closure_certificates.py",
    "tests/test_question_reading.py", "tests/test_ask_relay.py", "tests/test_ask_fixtures.py",
    "tests/test_ask_cli.py", "tests/test_words.py", "tests/test_rights_lean.py", "tests/test_rights.py",
    "tests/test_soft_norms_lean.py", "tests/test_softnorms_public_contract.py", "tests/test_norm_defaults.py",
    "tests/test_norm_defaults_switch.py", "tests/test_alternatives_profile.py", "tests/test_background.py",
    "tests/test_order.py", "tests/test_document.py", "tests/test_discourse.py",
)
# Recorded answers kept per (mode, answer shape).
PER_SHAPE = 3
LEAF_KINDS = ("flip", "plus", "minus", "exceed", "swap")
HEADER = ("ADR 0001 census of the Lean response shapes, generated by tools/binding_census.py --write from "
          "ve/backends/lean_service_schema/ and the recorded evidence; do not edit.")


# Recorded evidence


def load_answers(path: Path = ANSWERS) -> list[tuple]:
    """[(mode, case, row, index)] of the recorded genuine answers."""
    with gzip.open(path, "rt") as handle:
        return [tuple(json.loads(line)) for line in handle if line.strip()]


def load_probes(path: Path = PROBES) -> list[dict]:
    if not path.exists():
        return []
    with gzip.open(path, "rt") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _shape_key(mode, case, row) -> tuple:
    kind = case.get("kind", "") if isinstance(case, dict) and type(case.get("kind")) is str else ""
    status = row.get("status") if isinstance(row, dict) else None
    return mode, kind, str(status), tuple(sorted(row)) if isinstance(row, dict) else ()


def _write_gzip(path: Path, lines: list[str]) -> None:
    """Gzip text with no timestamp or name, so the same lines give the same bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as handle:
        handle.write("".join(line + "\n" for line in lines).encode())


def probe(directory: Path, tests: list[str], workers: int, wire: bool = False) -> int:
    """Run `tests` under the probe plugin, appending its lines to `directory`; with `wire`, each mutant passes the
    shape check first (`tests/binding_probe.py`)."""
    sys.path.insert(0, str(ROOT / "tools"))
    import nested_pytest
    directory.mkdir(parents=True, exist_ok=True)
    done = subprocess.run(nested_pytest.command(["-q", "-p", "tests.binding_probe", *tests], workers=workers,
                                                dist="loadfile"),
                          cwd=ROOT, env=nested_pytest.environment(os.environ, VE_BINDING_PROBE=str(directory),
                                                                  VE_BINDING_PROBE_WIRE="1" if wire else "0"))
    if done.returncode not in (0, 1):
        print(f"binding_census: the probe run failed ({done.returncode})", file=sys.stderr)
        return 2
    return 0


def collect(directory: Path) -> int:
    """Write PROBES from a probe run's lines, and ANSWERS: the relay gate's service requests asked of the current
    build and the genuine answers the probe saw."""
    lines = [json.loads(line) for path in sorted(directory.glob("probe-*.jsonl"))
             for line in path.read_text().splitlines() if line.strip()]
    probes, genuine = [], []
    for line in lines:
        if "genuine" in line:
            genuine.append(tuple(line["genuine"]))
        elif "error" not in line:
            probes.append(_attributed(line))
    probes.sort(key=lambda p: (p["mode"], p["caller"], p["path"], p["kind"], p["test"]))
    _write_gzip(PROBES, [json.dumps(p, sort_keys=True, separators=(",", ":")) for p in probes])
    return record_answers(genuine, f"{len(probes)} probes, "
                                   f"{sum(1 for p in probes if p['refused'] == 'hand')} hand refusals")


def refresh_answers() -> int:
    """Re-record ANSWERS without probing: every case it holds, and the relay gate's, asked of the current build."""
    return record_answers([(mode, case, None, 0) for mode, case, _, _ in load_answers()], "probes kept")


def record_answers(genuine: list, note: str) -> int:
    """Write ANSWERS: the relay gate's service requests and the `genuine` (mode, case, row, index) answers, the
    smallest PER_SHAPE of each answer shape. A case without its row (None) is asked of the current build, alone,
    so its row is at index 0."""
    from ve.backends.lean_service import DEFAULT_EXECUTABLE, LeanService
    answers = []
    with LeanService(DEFAULT_EXECUTABLE) as service:
        def ask(mode, case):
            _, response = service.exchange(mode, "[" + json.dumps(case, separators=(",", ":")) + "]", 1)
            return None if response.get("status") == "error" else response["results"][0]["result"]
        for row in (json.loads(line) for line in CASES.read_text().splitlines() if line.strip()):
            if row[0] == "service" and row[1] in MODES:
                answers.append((row[1], row[2], ask(row[1], row[2]), 0))
        for mode, case, row, index in genuine:
            if row is None and mode in MODES:
                answers.append((mode, case, ask(mode, case), 0))
            elif row is not None:
                answers.append((mode, case, row, index))
    unique: dict = {}
    for answer in answers:
        if answer[2] is not None:
            unique.setdefault(json.dumps(answer[:2], sort_keys=True), answer)
    answers = list(unique.values())
    kept, shapes = [], Counter()
    for mode, case, row, index in sorted(answers, key=lambda a: (len(json.dumps(a)), json.dumps(a))):
        key = _shape_key(mode, case, row)
        if shapes[key] < PER_SHAPE:
            shapes[key] += 1
            kept.append(json.dumps([mode, case, row, index], sort_keys=True, separators=(",", ":")))
    _write_gzip(ANSWERS, sorted(kept))
    print(f"binding_census: {len(kept)} answers recorded ({note})")
    return 0


def record(tests: list[str], workers: int) -> int:
    """`probe` then `collect`, through a temporary directory."""
    with tempfile.TemporaryDirectory(prefix="binding-probe-") as directory:
        return probe(Path(directory), tests, workers) or collect(Path(directory))


def _helper(path: str, function: str) -> bool:
    """Whether `function` in `path` only builds a CheckerUnavailable (the binder is its caller)."""
    node = _function(path, function)
    if node is None:
        return False
    body = [n for n in node.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
    if len(body) != 1 or not isinstance(body[0], (ast.Return, ast.Raise)):
        return False
    value = body[0].value if isinstance(body[0], ast.Return) else body[0].exc
    return isinstance(value, ast.Call) and getattr(value.func, "id", getattr(value.func, "attr", "")) == \
        "CheckerUnavailable"


def _attributed(line: dict) -> dict:
    """A probe line with the hand check that refused the mutant: the first refusal not made by the service client,
    at the exception it was converted from (if a `ve` line raised one) or at its first frame that is not a helper
    that only builds the error."""
    out = {key: line.get(key) for key in ("mode", "test", "kind", "path", "expect", "why", "generic", "outcome")}
    out["caller"] = "{}:{}".format(*line["caller"])
    refusals = line.get("refusals") or []
    refusal = next((r for r in refusals if not r.get("transport")), None)
    out["refused"] = "hand" if refusal else ("transport" if refusals else None)
    if line.get("outcome") == "wire":
        out["refused"] = "wire"  # refused by the shape check before the hand path (`--wire`)
    frame = None
    if refusal and (refusal.get("cause") or {}).get("transport"):
        refusal, out["refused"] = None, "transport"  # a later request's rejection, converted by the hand path
    if refusal:
        cause = refusal.get("cause") or {}
        frames = cause.get("frames") or []
        frame = frames[0] if frames else next((f for f in refusal["frames"] if not _helper(f[0], f[2])),
                                              refusal["frames"][0] if refusal["frames"] else None)
    elif line.get("outcome") not in (None, "passed", "AssertionError", "CheckerUnavailable", "timeout",
                                     "no-report") and line.get("raised"):
        frame = line["raised"][0]  # a crash or misread: where `ve` raised it
    out["site"] = None if frame is None else {"file": frame[0], "line": frame[1], "function": frame[2],
                                              "text": _line(frame[0], frame[1])}
    return out


def _line(path: str, number: int) -> str:
    try:
        return (ROOT / path).read_text().splitlines()[number - 1].strip()
    except (OSError, IndexError):
        return ""


_FUNCTIONS: dict = {}


def _functions(path: str, name: str) -> list:
    """The (first line, last line) of every function or method named `name` in `path`; the whole file for a frame
    that is no definition (`<genexpr>`, `<lambda>`, `<module>`)."""
    key = (path, name)
    if key not in _FUNCTIONS:
        try:
            source = (ROOT / path).read_text()
            tree = ast.parse(source)
        except (OSError, SyntaxError):
            _FUNCTIONS[key] = []
            return []
        if name.startswith("<"):
            _FUNCTIONS[key] = [(1, len(source.splitlines()))]
        else:
            _FUNCTIONS[key] = [(node.lineno, node.end_lineno or node.lineno) for node in ast.walk(tree)
                               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    return _FUNCTIONS[key]


def _function(path: str, name: str):
    """The definition of `name` in `path` (the first, for the helper test)."""
    try:
        tree = ast.parse((ROOT / path).read_text())
    except (OSError, SyntaxError):
        return None
    return next((node for node in ast.walk(tree)
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name), None)


def current_line(site: dict) -> int | None:
    """The line of `site`'s text inside a function of its name in the current tree (the one nearest the line at
    the probe), or None if it is in none of them."""
    if not site["text"]:
        return None
    try:
        lines = (ROOT / site["file"]).read_text().splitlines()
    except OSError:
        return None
    found = [number for first, last in _functions(site["file"], site["function"])
             for number in range(first, last + 1) if lines[number - 1].strip() == site["text"]]
    near = site.get("line_at_probe") or 0
    return min(found, key=lambda number: abs(number - near)) if found else None


# The census


def _leaf_row(leaf, observed: int) -> dict:
    binding = leaf.binding
    return {"path": leaf.path, "kind": leaf.kind, "class": binding.cls, "keyword": binding.keyword,
            "relation": binding.relation, "format": [k for k, _ in leaf.format], "site": leaf.site,
            "branches": len({b for b in leaf.branch}) or 1, "observed": observed}


def _split(path: str) -> tuple[str, str] | None:
    """(outer path, grammar-internal path) of a leaf inside a tagged grammar."""
    index = path.find("/~")
    return None if index < 0 else (path[:index] or "/", path[index:])


def build() -> tuple[dict, str]:
    """The census and its markdown view."""
    answers = load_answers()
    probes = load_probes()
    observed: dict = defaultdict(Counter)
    for mode, case, row, index in answers:
        placed, _ = shape_binding.classify(mode, case, row, index)
        for _, _, leaf in placed:
            observed[mode][leaf.path] += 1
    by_leaf: dict = defaultdict(list)
    for probe in probes:
        for path in probe["path"].split(","):
            by_leaf[(probe["mode"], path)].append(probe)
    modes, grammars, totals = {}, {}, Counter()
    for mode in MODES:
        census = shape_binding.census(mode)
        rows, occurrences = [], {}
        for leaf in shape_binding.leaves(mode):
            split = _split(leaf.path)
            if split is None:
                row = _leaf_row(leaf, observed[mode][leaf.path])
                row["today"] = _today(row, by_leaf.get((mode, leaf.path), []))
                rows.append(row)
                totals[f"leaves:{row['class']}"] += 1
                totals[f"today:{row['today']['status']}"] += 1
                continue
            outer, inner = split
            name = inner[2:].split("/")[0].split(":")[0]
            grammar = grammars.setdefault(name, {})
            if leaf.binding.at is None and leaf.binding.cls != "bound":
                grammar.setdefault((inner, leaf.kind), _leaf_row(leaf, 0))
            occurrence = occurrences.setdefault((outer, name), {"path": outer, "grammar": name, "bound": None,
                                                                 "observed": 0})
            if leaf.binding.cls == "bound" and leaf.binding.at is not None:
                occurrence["bound"] = leaf.binding.keyword
            occurrence["observed"] += observed[mode][leaf.path]
        arrays = {}
        for node in census.arrays:
            if "/~" in node.path:
                continue
            old = arrays.get(node.path, {"path": node.path, "length": None, "positional": None, "fixed": False,
                                         "agrees": None, "unique": False})
            arrays[node.path] = {"path": node.path, "length": old["length"] or node.length,
                                 "positional": old["positional"] or node.positional, "fixed": old["fixed"] or node.fixed,
                                 "agrees": old["agrees"] or node.agrees, "unique": old["unique"] or node.unique}
        for row in arrays.values():
            row["today"] = _today_structure(by_leaf.get((mode, row["path"]), []))
        modes[mode] = {
            "leaves": rows,
            "grammar_occurrences": sorted(occurrences.values(), key=lambda o: (o["path"], o["grammar"])),
            "arrays": sorted(arrays.values(), key=lambda a: a["path"]),
            "delegates": sorted({(d.path, d.mode) for d in census.delegations}),
            "answers": sum(1 for a in answers if a[0] == mode),
        }
        totals["modes"] += 1
    grammar_rows = {name: sorted(rows.values(), key=lambda r: (r["path"], r["kind"]))
                    for name, rows in sorted(grammars.items())}
    for name, rows in grammar_rows.items():
        for row in rows:
            row["path"] = row["path"].split("/", 2)[-1] if row["path"].startswith("/~") else row["path"]
            del row["observed"]
    binders = hand_binders(probes)
    rd9 = rd9_rows(modes, by_leaf)
    census = {
        "comment": HEADER,
        "inputs": {
            "schemas": hashlib.sha256(b"".join(path.read_bytes() for path in sorted(DIRECTORY.glob("*.json")))).hexdigest(),
            str(ANSWERS.relative_to(ROOT)): _sha256(ANSWERS),
            str(PROBES.relative_to(ROOT)): _sha256(PROBES) if PROBES.exists() else None,
            str(RD9.relative_to(ROOT)): _sha256(RD9),
        },
        "totals": dict(sorted(totals.items())) | {"answers": len(answers), "probes": len(probes),
                                                   "hand_binders": len(binders)},
        "modes": modes,
        "grammars": grammar_rows,
        "hand_binders": binders,
        "rd9": rd9,
    }
    return census, render(census)


def _site_key(site: dict) -> str:
    return f"{site['file']}:{site['function']}"


def _today(row: dict, probes: list) -> dict:
    """How a leaf is bound today: by its shape, by the hand checks that refused its mutants, or not at all."""
    leaf_probes = [p for p in probes if p["kind"] in LEAF_KINDS]
    out = {"status": None, "probed": len(leaf_probes)}
    hand = sorted({_site_key(p["site"]) for p in leaf_probes if p["refused"] == "hand" and p.get("site")})
    carried = sorted({_site_key(p["site"]) for p in leaf_probes
                      if p["refused"] == "hand" and p.get("site") and p["generic"] == "accept"})
    crashes = sorted({_site_key(p["site"]) for p in leaf_probes if not p["refused"] and p.get("site")})
    if row["class"] != "none":
        out["status"] = "shape"
    elif carried:
        out["status"] = "hand"
    elif not leaf_probes:
        out["status"] = "not probed"
    elif any(p["refused"] == "transport" and p["generic"] == "accept" for p in leaf_probes):
        out["status"] = "later Lean request"
    else:
        out["status"] = "unbound"
    if hand:
        out["hand"] = hand
    if carried:
        out["carried"] = carried
    if crashes:
        out["crash_or_misread"] = crashes
    return out


def _today_structure(probes: list) -> dict:
    """The probed array mutants of a path: per kind, the generic verdict and what the hand path did."""
    out = {}
    for probe in probes:
        if probe["kind"] in LEAF_KINDS:
            continue
        hand = _site_key(probe["site"]) if probe["refused"] == "hand" and probe.get("site") else (
            probe["refused"] or "accepted")
        out.setdefault(probe["kind"], set()).add(f"{probe['generic']}/{hand}")
    return {kind: sorted(values) for kind, values in sorted(out.items())}


def hand_binders(probes: list) -> list[dict]:
    """The hand checks that refused a probed mutant: the fields of each, whether the generic checker also refuses
    each such mutant, and whether the check could be retired later on that evidence."""
    groups: dict = {}
    for probe in probes:
        if probe["refused"] != "hand" or not probe.get("site"):
            continue
        site = probe["site"]
        group = groups.setdefault(_site_key(site), {"file": site["file"], "function": site["function"],
                                                    "lines": {}, "modes": set(), "only_hand": set(),
                                                    "also_generic": set()})
        group["lines"][site["text"]] = site["line"]
        group["modes"].add(probe["mode"])
        target = group["only_hand"] if probe["generic"] == "accept" else group["also_generic"]
        target.add(f"{probe['mode']} {probe['kind']} {probe['path']}")
    out = []
    for key, group in sorted(groups.items()):
        only = sorted(group["only_hand"])
        out.append({
            "binder": key,
            # `present`: the line is still in its function in this tree (False: the binder changed; re-probe).
            "lines": [{"text": text, "line_at_probe": line,
                       "present": current_line({"file": group["file"], "function": group["function"], "text": text,
                                                "line_at_probe": line}) is not None}
                      for text, line in sorted(group["lines"].items())],
            "modes": sorted(group["modes"]),
            "refused_only_by_hand": only,
            "refused_by_generic_too": sorted(group["also_generic"]),
            "retirable_later": not only,
            "why": ("every probed mutant it refuses is refused by the generic checker too" if not only else
                    f"the generic checker accepts {len(only)} probed mutant(s) only it refuses"),
        })
    return out


def rd9_rows(modes: dict, by_leaf: dict) -> list[dict]:
    """rd-9's 47 fields (RD9) in the census: each path's class and how it is bound today."""
    out = []
    for entry in json.loads(RD9.read_text())["rows"]:
        places = []
        for mode, path in entry["census"]:
            row = next((r for r in modes.get(mode, {}).get("leaves", ()) if r["path"] == path), None)
            array = next((a for a in modes.get(mode, {}).get("arrays", ()) if a["path"] == path), None)
            if row is not None:
                places.append({"mode": mode, "path": path, "class": row["class"], "today": row["today"]["status"],
                               "hand": row["today"].get("carried", [])})
            elif array is not None:
                places.append({"mode": mode, "path": path, "class": "array", "length": array["length"],
                               "today": array["today"]})
            else:
                places.append({"mode": mode, "path": path, "class": "missing"})
        shape_bound = any(p["class"] not in ("none", "missing", "array") for p in places)
        out.append({"row": entry["row"], "field": entry["field"], "rd9": entry["rd9"], "places": places,
                    **({"note": entry["note"]} if "note" in entry else {}),
                    "shape": "bound or closed" if shape_bound else "unbound by the shapes",
                    "agrees": entry["rd9"] in ("No", "Partly") and not shape_bound})
    return out


# The view


def render(census: dict, lines_now: bool = False) -> str:
    """The census as markdown; with `lines_now`, each hand check's line in the current tree."""
    t = census["totals"]
    out = [f"# Binding census (ADR 0001)", "", f"<!-- {census['comment']} -->", "",
           "Every string, integer and map-key leaf of every Lean response shape, its class under ADR 0001, and how "
           "it is bound today. Generated by `tools/binding_census.py`; the data is "
           "`docs/test-architecture/binding-census.json`.", "",
           "| | count |", "|---|---:|"]
    for key, value in t.items():
        out.append(f"| {key} | {value} |")
    out += ["", "## Hand binders", "",
            "A hand check refused a probed mutant; `only hand` counts the mutants the generic checker accepts. Lines are "
            "at the probe's commit (`--show` prints the current ones).", "",
            "| hand check | lines | modes | only hand | generic too | retirable later |", "|---|---|---|---:|---:|---|"]
    for binder in census["hand_binders"]:
        lines = "; ".join(_cite(binder["binder"], line, lines_now) for line in binder["lines"])
        out.append(f"| `{binder['binder']}` | {lines} | {', '.join(binder['modes'])} | "
                   f"{len(binder['refused_only_by_hand'])} | {len(binder['refused_by_generic_too'])} | "
                   f"{'yes' if binder['retirable_later'] else 'no'} |")
    out += ["", "## rd-9's 47 fields", "", "| row | field | rd-9 | census | today |", "|---|---|---|---|---|"]
    for row in census["rd9"]:
        today = "; ".join(f"{p['mode']} `{p['path']}` {p.get('class')}"
                          f"{' ' + str(p.get('today')) if p.get('class') != 'missing' else ''}" for p in row["places"])
        out.append(f"| {row['row']} | {row['field']} | {row['rd9']} | {row['shape']} | {today} |")
    for mode, data in census["modes"].items():
        out += ["", f"## {mode}", "", f"{data['answers']} recorded answers."]
        if data["delegates"]:
            out.append("Delegates: " + ", ".join(f"`{p}` to {m}" for p, m in data["delegates"]) + ".")
        out += ["", "| leaf | kind | class | keyword | format | observed | bound today |", "|---|---|---|---|---|---:|---|"]
        for row in data["leaves"]:
            today = row["today"]
            how = today["status"] + (": " + ", ".join(f"`{h}`" for h in today["carried"]) if today.get("carried") else "")
            out.append(f"| `{row['path']}` | {row['kind']} | {row['class']} | {row['keyword'] or ''} | "
                       f"{' '.join(row['format'])} | {row['observed']} | {how} |")
        if data["grammar_occurrences"]:
            out += ["", "| grammar at | grammar | bound whole by | observed |", "|---|---|---|---:|"]
            for o in data["grammar_occurrences"]:
                out.append(f"| `{o['path']}` | {o['grammar']} | {o['bound'] or ''} | {o['observed']} |")
        if data["arrays"]:
            out += ["", "| array | length bound by | positions bound by | internal agreement | probed (generic/hand) |",
                    "|---|---|---|---|---|"]
            for a in data["arrays"]:
                probed = "; ".join(f"{k}: {', '.join(v)}" for k, v in a["today"].items())
                internal = " ".join(filter(None, (a["agrees"], "x-unique-strings" if a["unique"] else None)))
                out.append(f"| `{a['path']}` | {a['length'] or ''} | {a['positional'] or ''} | {internal} | {probed} |")
    out += ["", "## Grammars", ""]
    for name, rows in census["grammars"].items():
        out.append(f"- **{name}**: " + ", ".join(f"`{r['path']}` {r['class']}" for r in rows))
    return "\n".join(out) + "\n"


def _cite(binder: str, line: dict, lines_now: bool) -> str:
    path, function = binder.split(":", 1)
    if lines_now:
        now = current_line({"file": path, "function": function, "text": line["text"],
                            "line_at_probe": line["line_at_probe"]})
        return f"{path}:{now if now else 'changed since the probe'}"
    return f"{path}:{line['line_at_probe']}" + ("" if line["present"] else " (changed since the probe)")


def missing_anchors(census: dict) -> list[str]:
    """The hand checks whose cited line text is no longer in their function."""
    missing = []
    for binder in census["hand_binders"]:
        path, function = binder["binder"].split(":", 1)
        for line in binder["lines"]:
            if current_line({"file": path, "function": function, "text": line["text"],
                             "line_at_probe": line["line_at_probe"]}) is None:
                missing.append(f"{binder['binder']}: {line['text']!r}")
    return missing


def dumps(census: dict) -> str:
    """One line per leaf, array and binder, so a change reads as a line diff."""
    lines = ["{"]
    keys = list(census)
    for i, key in enumerate(keys):
        value = census[key]
        tail = "," if i < len(keys) - 1 else ""
        if key == "modes":
            lines.append(' "modes": {')
            names = list(value)
            for j, mode in enumerate(names):
                lines.append(f"  {json.dumps(mode)}: {{")
                parts = list(value[mode].items())
                for k, (part, items) in enumerate(parts):
                    end = "," if k < len(parts) - 1 else ""
                    if isinstance(items, list) and items:
                        lines.append(f"   {json.dumps(part)}: [")
                        lines += [f"    {json.dumps(item, sort_keys=True)}{',' if n < len(items) - 1 else ''}"
                                  for n, item in enumerate(items)]
                        lines.append(f"   ]{end}")
                    else:
                        lines.append(f"   {json.dumps(part)}: {json.dumps(items)}{end}")
                lines.append(f"  }}{',' if j < len(names) - 1 else ''}")
            lines.append(f" }}{tail}")
        elif isinstance(value, list) or key == "grammars":
            items = list(value.items()) if isinstance(value, dict) else value
            opener, closer = ("{", "}") if isinstance(value, dict) else ("[", "]")
            lines.append(f" {json.dumps(key)}: {opener}")
            for n, item in enumerate(items):
                text = (f"{json.dumps(item[0])}: {json.dumps(item[1], sort_keys=True)}" if isinstance(value, dict)
                        else json.dumps(item, sort_keys=True))
                lines.append(f"  {text}{',' if n < len(items) - 1 else ''}")
            lines.append(f" {closer}{tail}")
        else:
            lines.append(f" {json.dumps(key)}: {json.dumps(value, sort_keys=True)}{tail}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="write the census and its view")
    group.add_argument("--check", action="store_true", help="exit 1 if the census or its view is stale")
    group.add_argument("--show", nargs="?", const="", metavar="MODE", help="print the view with current lines")
    group.add_argument("--record", nargs="*", metavar="TEST", help="re-record the answers and re-probe")
    group.add_argument("--probe", nargs="+", metavar=("DIR", "TEST"), help="probe TESTs (default PROBE_TESTS) "
                       "into DIR, appending")
    group.add_argument("--collect", type=Path, metavar="DIR", help="record the answers and a probe run's lines")
    group.add_argument("--answers", action="store_true", help="re-record the answers only, asking the current "
                       "build again for every case recorded (after a Lean change)")
    parser.add_argument("--workers", type=int, default=int(os.environ.get("BINDING_PROBE_WORKERS", "8")))
    parser.add_argument("--wire", action="store_true", help="with --probe: deliver each mutant before the shape "
                        "check, as the service would")
    args = parser.parse_args(argv)
    if args.record is not None:
        return record(args.record or list(PROBE_TESTS), args.workers)
    if args.probe is not None:
        return probe(Path(args.probe[0]), args.probe[1:] or list(PROBE_TESTS), args.workers, args.wire)
    if args.collect is not None:
        return collect(args.collect)
    if args.answers:
        return refresh_answers()
    census, view = build()
    if args.show is not None:
        if args.show:
            census = {**census, "modes": {args.show: census["modes"][args.show]}}
        print(render(census, lines_now=True), end="")
        return 0
    text = dumps(census)
    if args.write:
        CENSUS.write_text(text)
        VIEW.write_text(view)
        print(f"binding_census: wrote {CENSUS.relative_to(ROOT)} and {VIEW.relative_to(ROOT)}")
        return 0
    problems = [f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path} is stale; run "
                "tools/binding_census.py --write"
                for path, want in ((CENSUS, text), (VIEW, view)) if not path.exists() or path.read_text() != want]
    for problem in problems:
        print(f"binding_census: {problem}", file=sys.stderr)
    for item in missing_anchors(census):
        print(f"binding_census: note: a hand check changed since the probe (re-probe with --record): {item}",
              file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
