"""en-e3bb's W1 delta evidence (docs/spec/en-e3-norm.md 2.4, Delta report; section 6).

    uv run python docs/en-e3-norm/en-2/w1_delta.py [--workers N]

Every corpus runs through the shadow itself: `parse_english`'s W1 path with `VE_STATEMENT_COMPARATOR=1` and
`VE_SHADOW_LOG` set to a scratch log, so each record is the one the shadow writes (`statement_record`), tagged here
with its corpus and id. The corpora:

* `suite`, `soft-rights`: every test unit that may call `parse_english` (`SUITE`, derived by `suite_plan` from the
  coverage map nearest below HEAD, never listed by hand: the units the map records running `parse_english`, every
  unit the map does not record cleanly (absent, failed or opaque) and every unit whose run may have changed since the
  map (`select_tests.uncertain_since`); no map is the whole suite), run by pytest with this file as a plugin
  (`-p w1_delta`); a record of a soft or rights environment (whose W1 call is `_w1=True`: the soft reader's, through
  `ve/surface/rights.py`'s `parse_line` too) is `soft-rights`, any other `suite`. Records are kept once per
  (source, Python's outcome, Lean's outcome), with the first test that made them;
* `pinned`: the 120 blocks of `tests/data/norm-blocks/` in their use cases' environments;
* `udhr`, `constitution`: every norm unit and norm reading of the UDHR and constitution pilot documents, one at a
  time (never a whole-document check): its node as a one-rule document, rendered to English and read back;
* `known`: one text per known difference of english-lean-s6.md section 5, each named by `difference`.

Writes `delta.json` (the commit, the suite's derivation and pytest's summary line, each corpus's size and per-class
counts, every row of a class other than `agree` and `both-refuse`, every record Lean answers `NodeRefused` or
`NodeLimit`, the `lean-unavailable` ids) and `DELTA.md` from it. The report's test reads these saved files only.
"""
from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CLASSES = ("lean-unavailable", "agree", "lean-unknown", "lean-stricter", "lean-looser", "different-node",
           "both-refuse")
DECIDED = ("agree", "both-refuse")
SHADOWED = ("ve/norm_english.py", "parse_english")  # the one function whose W1 path writes a shadow record
PILOTS = {"udhr": "usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md",
          "constitution": "usecases/claude-constitution-pilot/run-20261104T0716Z/probe-translation.probe.md"}
TAG: dict = {}  # the corpus and id of the call in progress, added to its record


def derive_suite(coverage, units: set[str], uncertain: set[str]) -> dict:
    """The suite corpus's units from a coverage map (`select_tests.Coverage`): `reached`, the units the map records
    running `SHADOWED` (or anything nested in it); `unknown`, the other units whose call is not known from the map:
    not recorded cleanly there (absent, failed or opaque: `Coverage.recorded`) or `uncertain` (their run may have
    changed since the map). A unit the map records running only other code of the module (its import) is left out:
    it reaches no shadow. `files` is both, in order."""
    reached = coverage.tests_of(*SHADOWED) & units
    unknown = ((units - coverage.recorded) | uncertain) & units - reached
    return {"map": coverage.commit, "function": ":".join(SHADOWED), "reached": sorted(reached),
            "unknown": sorted(unknown), "files": sorted(reached | unknown)}


def suite_plan(base: str = "HEAD") -> dict:
    """`derive_suite` over the map `select_tests` would use for `base` (its drift since the map included); with no
    usable map, every unit (`map` null)."""
    sys.path.insert(0, str(ROOT / "tools"))
    import select_tests
    import source_graph
    units = set(select_tests.units())
    coverage = select_tests.resolve_map(base, "auto")
    if coverage is None:
        return {"map": None, "function": ":".join(SHADOWED), "reached": [], "unknown": sorted(units),
                "files": sorted(units)}
    uncertain, _ = select_tests.uncertain_since(coverage, source_graph.load(ROOT), units, base)
    return derive_suite(coverage, units, uncertain)


def short(unit: str) -> str:
    """`tests/test_<name>.py` as `<name>`; any other unit (`test_map.EXTRA_UNITS`) by its path."""
    return unit[len("tests/test_"):-len(".py")] if unit.startswith("tests/test_") and "/" not in unit[6:] else unit


def __getattr__(name: str):  # `SUITE` is derived when asked, never when pytest loads this file as its plugin
    if name == "SUITE":
        return [short(unit) for unit in suite_plan()["files"]]
    raise AttributeError(name)


def install() -> None:
    """Tag every shadow record with `TAG`, and in a test run with its corpus (by the environment) and test."""
    from ve import norm_english
    record, shadow = norm_english.statement_record, norm_english._shadow
    ours, writing = os.environ.get("VE_SHADOW_LOG"), []  # this run's log; whether `_shadow` is writing to it

    def tagged_shadow(log, env, source, python):
        """Only a record written to this run's log is tagged: a test's own log (a `VE_SHADOW_LOG` it sets) and a
        test's own `statement_record` call see the records they would see without this plugin."""
        if str(log) != ours:
            return shadow(log, env, source, python)
        if os.environ.get("PYTEST_CURRENT_TEST"):
            TAG.update(corpus="soft-rights" if "soft-norms@0" in env.profiles else "suite",
                       id=os.environ["PYTEST_CURRENT_TEST"].rsplit(" ", 1)[0])
        writing.append(True)
        try:
            return shadow(log, env, source, python)
        finally:
            writing.pop()

    def tagged_record(source, python, lean):
        return {**record(source, python, lean), **TAG} if writing else record(source, python, lean)
    norm_english._shadow, norm_english.statement_record = tagged_shadow, tagged_record


def pytest_configure(config):  # noqa: ARG001 - the plugin of the suite corpus
    install()


def _read(env, text: str, corpus: str, ident: str, **extra) -> None:
    from ve.norm_english import parse_english
    TAG.clear()
    TAG.update(corpus=corpus, id=ident, **extra)
    try:
        parse_english(env, text)
    except Exception:  # noqa: BLE001 - Python's refusal is recorded by the shadow
        pass


def pinned() -> None:
    sys.path.insert(0, str(ROOT))
    from tests.test_english_statement_blocks import CASES, blocks
    for name, (case, module, _) in CASES.items():
        folder = str(ROOT / "usecases" / case)
        sys.path.insert(0, folder)
        spec = importlib.util.spec_from_file_location(f"pinned_{module}", f"{folder}/{module}.py")
        loader = sys.modules[spec.name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loader)
        sys.path.remove(folder)
        env = loader.environment()
        for row in blocks(name):
            _read(env, row["text"], "pinned", f"{name}/{row['id']}")


def units(name: str) -> int:
    """The pilot's norm units and norm readings with a node (a reading with a `companion` in its own environment),
    each rendered alone and read back; the count of nodes Python cannot render as a one-rule W1 document (no
    English round trip, so no record). A reading whose content is null has no node and is not counted."""
    from ve.environment import Environment
    from ve.norm_english import render_english
    from ve.norms import NormDocument
    raw = (ROOT / PILOTS[name]).read_text()
    meta = json.loads(raw.split("\n---\n", 1)[0].split("---\n", 1)[1])
    env = Environment(meta["environment"])
    nodes = [(u["id"], None, u["content"]) for u in meta["units"] if type(u.get("content")) is dict
             and "norm" in u["content"]]
    nodes += [(f"{s['unit']}/{r['id']}", r.get("companion"), r["content"]) for s in meta["reading_sets"]
              for r in s.get("readings", ()) if r.get("kind") == "norm" and r["content"] is not None]
    skipped = 0
    for ident, companion, content in nodes:
        try:
            own = env if companion is None else Environment(companion["environment"])
            text = render_english(NormDocument(own, [content]))[0]
        except Exception:  # noqa: BLE001 - no English round trip
            skipped += 1
            continue
        _read(own, text, name, f"{name}/{ident}")
    return skipped


def known() -> list[str]:
    """english-lean-s6.md section 5's known differences, one text each (and the layout rows of :533); the
    differences whose environment no `Environment` admits (so no W1 text reaches either reader) are returned."""
    sys.path.insert(0, str(ROOT))
    from tests.test_norms import environment, permission
    plain = {"arguments": ["act"], "description": "noteworthy"}
    env = lambda **extra: environment({"permitted": permission(), **extra})  # noqa: E731
    may, must = "Every act may be done.", "Every act must not be done."
    rows = [
        ("empty-text", env, ""),
        ("layout-shared-line", env, f"Rule 1. {may} Rule 2. {must}"),
        ("layout-several-lines", env, f"Rule 1.\n{may}"),
        ("layout-blank-line", env, f"Rule 1. {may}\n\nRule 2. {must}"),
        ("layout-trailing-line", env, f"Rule 1. {may}\n"),
        ("layout-precedence-first", env, f"Rule 2 takes precedence over rule 1.\nRule 1. {must}\nRule 2. {may}"),
        ("conditions-two-if", lambda: env(noteworthy=plain),
         "Rule 1. Every act may be done, if that act is noteworthy, if that act is noteworthy."),
        ("sort-three-times", lambda: env(triple={"arguments": ["act", "act", "act"], "description": "triple"}),
         f"Rule 1. {may}"),
        ("no-argument-predicate", lambda: env(raining={"arguments": [], "description": "raining"}), f"Rule 1. {may}"),
        ("casing-lowercase-rule", env, f"rule 1. {may}"),
        ("casing-except-When", lambda: env(noteworthy=plain),
         "Rule 1. Every act may be done, except When that act is noteworthy."),
        ("casing-lowercase-except-when", lambda: env(noteworthy=plain),
         f"Rule 1. {may} except when that act is noteworthy."),
        ("fold-outside-ascii", lambda: env(noteworthy=plain),
         "Rule 1. Every act may be done, if that act \u0130s noteworthy."),
        ("spacing-double", env, f"Rule 1.  {may}"),
        ("spacing-tab", env, f"Rule 1.\t{may}"),
        ("self-precedence", env, f"Rule 1. {may}\nRule 1 takes precedence over rule 1."),
        ("header-and-line-repeat", env, f"Rule 1. {must}\nRule 2 (exception to rule 1). {may}\n"
                                        "Rule 2 takes precedence over rule 1."),
    ]
    refused = []
    for difference, make, text in rows:
        try:
            environment_ = make()
        except Exception:  # noqa: BLE001 - an environment no reader is given
            refused.append(difference)
            continue
        _read(environment_, text, "known", f"known/{difference}", difference=difference)
    return refused


def suite(scratch: Path, workers: int, plan: dict) -> str:
    """Run `plan`'s units with the shadow on: the pytest units in one run with this file as its plugin, any other
    unit by its own command (`test_map.EXTRA_UNITS`; its records are `suite-subprocess`). Returns pytest's summary
    line."""
    sys.path.insert(0, str(ROOT / "tools"))
    import nested_pytest
    import test_map
    env = nested_pytest.environment(os.environ, PYTHONPATH=os.pathsep.join([str(HERE), str(ROOT)]),
                                    VE_STATEMENT_COMPARATOR="1", VE_SHADOW_LOG=str(scratch / "suite.jsonl"))
    files = [unit for unit in plan["files"] if unit not in test_map.EXTRA_UNITS]
    for unit in plan["files"]:
        if unit in test_map.EXTRA_UNITS:
            subprocess.run(test_map.EXTRA_UNITS[unit], cwd=ROOT, env=env, check=False)
    run = subprocess.run(nested_pytest.command(["-q", "-p", "w1_delta", *files], workers=workers), cwd=ROOT,
                         env=env, check=False, capture_output=True, text=True)
    print(run.stdout[-4000:], run.stderr[-2000:])
    counts = [m[1] for m in re.finditer(r"^=* ?((?:\d+ [a-z]+(?:, )?)+) in [0-9.]+s", run.stdout, re.M)]
    return counts[-1] if counts else f"no pytest summary (exit {run.returncode})"


def _outcome(record: dict) -> str:
    python, lean = record["python"], record["lean"]
    return json.dumps([python.get("class", "admits"), python.get("nodes"), lean.get("status"), lean.get("code"),
                       lean.get("nodes"), lean.get("message")], sort_keys=True)


def build(records: list[dict], skipped: dict, commit: str, suite_run: dict) -> dict:
    kept, seen = [], set()
    for record in records:
        if "source_sha256" not in record:  # an `english.read` comparator record (the same log variable)
            continue
        if "corpus" not in record:  # a `ve` process a test started: it inherits the flags, not the plugin
            record.update(corpus="suite-subprocess", id=f"subprocess/{record['source_sha256'][:12]}")
        key = (record["corpus"], record["source_sha256"], _outcome(record)) if record["corpus"] in (
            "suite", "soft-rights", "suite-subprocess") else (record["corpus"], record["id"])
        if key not in seen:
            seen.add(key)
            kept.append(record)
    corpora = sorted({r["corpus"] for r in kept})
    rows = sorted((r for r in kept if r["class"] not in DECIDED or r["lean"].get("code") in ("NodeRefused", "NodeLimit")),
                  key=lambda r: (r["corpus"], r["id"], r["source_sha256"], _outcome(r)))  # not the workers' order
    return {"commit": commit, "suite": suite_run, "corpora": [{"name": c, "size": sum(r["corpus"] == c for r in kept),
                                           "no_round_trip": skipped.get(c, 0) if c != "known" else 0} for c in corpora],
            "counts": {c: {k: sum(r["corpus"] == c and r["class"] == k for r in kept) for k in CLASSES}
                       for c in corpora},
            "lean_unavailable": [r["id"] for r in rows if r["class"] == "lean-unavailable"],
            "known_not_constructible": skipped.get("known", []),
            "pinned": {r["id"]: r["class"] for r in kept if r["corpus"] == "pinned"},
            "rows": [{k: r[k] for k in ("corpus", "id", "source_sha256", "class", "python", "lean", "difference")
                      if k in r} for r in rows]}


def _cell(outcome: dict) -> str:
    if "nodes" in outcome and "status" not in outcome:
        return f"admits {len(outcome['nodes'])} rule(s)"
    if "class" in outcome:
        return f"{outcome['class']}: {outcome['message'][:90]}".replace("|", "/").replace("\n", " ")
    if outcome["status"] == "unavailable":
        return f"unavailable: {outcome['message'][:90]}".replace("|", "/").replace("\n", " ")
    return f"{outcome['status']} {outcome.get('code') or ''} ({len(outcome.get('nodes') or [])} node(s))".strip()


def lean_cause(lean: dict) -> str:
    """Lean's answer in a row of causes: its code, or its status when it has none; for a request Lean refused or
    could not answer, the refusal it gave (the relay's message), so the cause of every `lean-unavailable` row is
    named."""
    if lean["status"] == "unavailable":
        return lean["message"].replace("|", "/").replace("\n", " ")[:120]
    return lean.get("code") or lean["status"]


def markdown(delta: dict) -> str:
    lines = ["# W1 delta of `english.statement` against Python's reader (EN-2 evidence)", "",
             f"Generated by `w1_delta.py` from `delta.json` at `{delta['commit'][:12]}`; spec en-e3-norm.md 2.4 and "
             "section 6. One row per `delta.json` row, with its class. The decision column is the DRI's, once for "
             "the W1 layer, at the stop point between EN-2 and EN-3; it gates en-e3, not this branch's merge.", "",
             f"The suite corpus ran the {len(delta['suite']['files'])} test units that may call "
             f"`{delta['suite']['function']}`, derived from the coverage map at `{str(delta['suite']['map'])[:12]}`: "
             f"{len(delta['suite']['reached'])} the map records calling it, {len(delta['suite']['unknown'])} it "
             f"cannot rule out (`w1_delta.derive_suite`). pytest: {delta['suite']['result']}.", "",
             "## Corpora", "", "| corpus | records | no round trip | " + " | ".join(CLASSES) + " |",
             "|---|---|---|" + "---|" * len(CLASSES)]
    for c in delta["corpora"]:
        counts = delta["counts"][c["name"]]
        lines.append(f"| {c['name']} | {c['size']} | {c['no_round_trip']} | "
                     + " | ".join(str(counts[k]) for k in CLASSES) + " |")
    lines += ["", f"`lean-unavailable` ids ({len(delta['lean_unavailable'])}): "
              + (", ".join(f"`{i}`" for i in delta["lean_unavailable"]) or "none"), "",
              f"Blocks Lean answers `NodeRefused` or `NodeLimit`: "
              f"{sum(r['lean'].get('code') in ('NodeRefused', 'NodeLimit') for r in delta['rows'])} "
              "(each would be a row below, whatever its class).", "",
              "Known differences of english-lean-s6.md section 5 whose environment no `Environment` admits, so that "
              "neither reader is given a text: " + (", ".join(f"`{d}`" for d in delta["known_not_constructible"])
                                                    or "none") + ".", "",
              "## Rows by Lean's answer", "", "| corpus | class | Lean | rows |", "|---|---|---|---|"]
    causes = Counter((r["corpus"], r["class"], lean_cause(r["lean"])) for r in delta["rows"])
    lines += [f"| {corpus} | {cls} | {lean} | {n} |" for (corpus, cls, lean), n in sorted(causes.items())] + [""]
    sections = [("Layout rows (english-lean-s6.md:533; decided here, a refused layout is a Lean code)",
                 lambda r: r.get("difference", "").startswith("layout-")),
                ("`lean-unknown` rows (not decided as rejections)",
                 lambda r: r["class"] == "lean-unknown" and not r.get("difference", "").startswith("layout-")),
                ("Other rows", lambda r: r["class"] != "lean-unknown" and not r.get("difference", "").startswith(
                    "layout-"))]
    for title, chosen in sections:
        rows = [r for r in delta["rows"] if chosen(r)]
        lines += [f"## {title}", "", "| corpus | id | class | Python | Lean | DRI decision |", "|---|---|---|---|---|---|"]
        lines += [f"| {r['corpus']} | `{r['id']}` | {r['class']} | {_cell(r['python'])} | {_cell(r['lean'])} |  |"
                  for r in rows]
        lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--scratch", type=Path, help="the scratch directory for the logs (default: a new one)")
    parser.add_argument("--build-only", action="store_true", help="rebuild the report from --scratch's logs")
    args = parser.parse_args(argv)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="w1-delta-") as directory:
        scratch = args.scratch or Path(directory)
        scratch.mkdir(parents=True, exist_ok=True)
        if args.build_only:  # the records of an earlier run in `--scratch`, read again, with its commit
            skipped = json.loads((scratch / "skipped.json").read_text())
            commit, suite_run = skipped.pop("commit"), skipped.pop("suite")
        else:
            dirty = subprocess.run(["git", "status", "--porcelain", "--", ".", f":!{HERE.relative_to(ROOT)}"],
                                   cwd=ROOT, capture_output=True, text=True).stdout
            if dirty:  # the records, the commit and the suite's drift since the map are all HEAD's
                parser.error(f"uncommitted changes outside {HERE.relative_to(ROOT)}: commit them first\n{dirty}")
            for name in ("own.jsonl", "suite.jsonl"):
                (scratch / name).unlink(missing_ok=True)
            os.environ.update(VE_STATEMENT_COMPARATOR="1", VE_SHADOW_LOG=str(scratch / "own.jsonl"))
            sys.path.insert(0, str(ROOT))
            install()
            pinned()
            skipped = {name: units(name) for name in PILOTS}
            skipped["known"] = known()
            plan = suite_plan()
            suite_run = {**plan, "result": suite(scratch, args.workers, plan)}
            (scratch / "skipped.json").write_text(json.dumps({**skipped, "commit": commit, "suite": suite_run}))
        records = [json.loads(line) for name in ("own.jsonl", "suite.jsonl") if (scratch / name).exists()
                   for line in (scratch / name).read_text().splitlines()]
    delta = build(records, skipped, commit, suite_run)
    (HERE / "delta.json").write_text(json.dumps(delta, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    (HERE / "DELTA.md").write_text(markdown(delta) + "\n")
    print(json.dumps(delta["counts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
