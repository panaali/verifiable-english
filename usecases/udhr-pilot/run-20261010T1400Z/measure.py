"""RD-5 steps 3 to 5: check, measure and query the migrated UDHR, beside the run of 20261006T1800Z as committed.

    uv run --frozen python usecases/udhr-pilot/run-20261010T1400Z/measure.py

Everything runs in the foreground at one commit (recorded), and every timed step in a child process of its own, so
its wall time and its CPU (the child's and the Lean processes it waits for, `RUSAGE_CHILDREN`) are its own; the host
load is recorded beside each. Writes `metrics.json`, `answers/` (each query's answer, verbatim) and the reports of
both documents under `reports/`; `SUMMARY.md` is rendered from `metrics.json` by `summary.py`.

- **Checks** (step 3): `load_document`, `check_document` and `render_document` of the migrated document; every
  component's status witnesses through `readings-choice` and the 156 companions re-checked alone
  (`witnesses.py`).
- **Measurements** (step 4): the table of the plan's RD-5 step 4, before and after. The counts per component (its
  regulated predicates, its readings, the generated `F_p` rules of each choice's document) are read from Lean's
  answers: its split (`readings-elaborate`) and each choice's `norm-defaults-elaborate`. The Lean-decided share is
  `tools/lean_decided_share.py` on Lean's `decided_units` (the check report's readings block); before, the report
  has no readings block, so no unit is decided.
- **Queries** (step 5): the three demonstrations of the spec's 8.6 through `ve document readings`.
"""
from __future__ import annotations

import json
import os
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from migrate import COMMIT, RUN, git_ls, git_show, split_document  # noqa: E402

MIGRATED = HERE / "translation.ve.md"
RECORDED = {"claimed_covered_bytes": 4792, "audit_verified_covered_bytes": 2543, "premises": "UNKNOWN",
            "source": f"{RUN}/metrics.json and verdict.json at {COMMIT}"}
QUERIES = [
    {"name": "u029-recognise", "sentence": "u029", "under": [],
     "english": "every State must recognise each person everywhere as a person before the law",
     "conclusion": ["forall", "state", ["forall", "person",
                                        ["binary", "secure_recognition_as_person_required", ["var", 1], ["var", 0]]]],
     "expected": "SOME"},
    {"name": "u081-secure", "sentence": "u081", "under": [],
     "english": "every State whose organization and resources allow it must secure each person social security",
     "conclusion": ["forall", "state", ["implies", ["unary", "resources_allow", ["var", 0]],
                                        ["forall", "person", ["binary", "secure_social_security_required",
                                                              ["var", 1], ["var", 0]]]]],
     "expected": "SOME"},
    {"name": "u081-secure-under-2", "sentence": "u081", "under": ["rs_u081:2"],
     "english": "every State whose organization and resources allow it must secure each person social security",
     "conclusion": ["forall", "state", ["implies", ["unary", "resources_allow", ["var", 0]],
                                        ["forall", "person", ["binary", "secure_social_security_required",
                                                              ["var", 1], ["var", 0]]]]],
     "expected": "ALL"},
    {"name": "u081-none", "sentence": "u081", "under": [],
     "english": "no State must secure any person social security",
     "conclusion": ["forall", "state", ["forall", "person", ["not", ["binary", "secure_social_security_required",
                                                                     ["var", 1], ["var", 0]]]]],
     "expected": "NONE"},
]


def timed(step, *args):
    """Run `measure.py step <step> <args>` in a child: (its JSON output, wall s, CPU s with Lean's, load before)."""
    load = os.getloadavg()[0]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    done = subprocess.run([sys.executable, str(Path(__file__)), "step", step, *map(str, args)], cwd=ROOT,
                          capture_output=True, text=True)
    wall = time.monotonic() - started
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    if done.returncode != 0:
        raise SystemExit(f"measure: step {step} failed: {done.stderr[-2000:]}")
    return json.loads(done.stdout), {"wall_seconds": round(wall, 1), "cpu_seconds": round(cpu, 1),
                                     "load_before": round(load, 1), "load_after": round(os.getloadavg()[0], 1)}


def step(name, path, out=None):
    """One timed step, in this (child) process; prints its JSON."""
    from ve.document import check_document, load_document, render_document
    from ve.errors import VEError
    path = Path(path)
    try:
        if name == "load":
            doc = load_document(path)
            result = {"units": len(doc["units"]), "source_bytes": len(doc["source"])}
        elif name == "check":
            report = check_document(path)
            Path(out).write_text(json.dumps(report, indent=1, ensure_ascii=False, default=str) + "\n")
            result = {"premises": report["premises"]["status"]}
        elif name == "render":
            text = render_document(path)
            Path(out).write_text(text)
            result = {"characters": len(text)}
        else:
            raise SystemExit(f"unknown step {name}")
    except VEError as exc:
        result = {"refused": exc.message}
    print(json.dumps(result))


def query(path, q, out):
    """One demonstration through `ve document readings`, its answer saved verbatim."""
    folder = Path(tempfile.mkdtemp(prefix="rd5-query-"))
    conclusion = folder / "conclusion.json"
    conclusion.write_text(json.dumps(q["conclusion"]))
    args = [sys.executable, "-m", "ve", "document", "readings", str(path), "--conclusion", str(conclusion),
            "--sentence", q["sentence"], *[x for u in q["under"] for x in ("--under", u)]]
    load = os.getloadavg()[0]
    started = time.monotonic()
    done = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    wall = time.monotonic() - started
    out.write_text(done.stdout)
    answer = json.loads(done.stdout) if done.returncode == 0 else None
    return {"name": q["name"], "english_query": q["english"], "sentence": q["sentence"], "under": q["under"],
            "conclusion": q["conclusion"], "expected": q["expected"], "exit": done.returncode,
            "verdict": answer["verdict"] if answer else None, "stderr": done.stderr[-500:],
            "english": answer["english"] if answer else None, "answer": f"answers/{out.name}",
            "wall_seconds": round(wall, 1), "load_before": round(load, 1)}


def lean_split(meta):
    """Lean's split of the migrated document (`readings-elaborate`): each case's environment and choices."""
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import wire
    env, doc = wire(meta["environment"]), wire(document_wire(meta["units"], meta["reading_sets"]))
    [row] = run_lean([{"id": "split", "kind": "readings-elaborate", "environment": env, "document": doc}])
    if row.get("status") != "ok":
        raise SystemExit(f"measure: Lean refused the migrated document: {row.get('error')}")
    return env, doc, {c["component"]: c for c in row["components"]}


def component_sizes(env, doc, parts):
    """Per companion case, read from Lean's answers: its regulated predicates and readings (its merged frame and
    its set), its choices, and per choice the generated `F_p` rules (one per unspecified predicate Lean's
    `norm-defaults-elaborate` names) beside the choice's author rules (its readings with a norm content: a norm
    content is one rule, an asserted one none)."""
    from ve.readings_route import run_lean
    sizes = {}
    cases, keys = [], []
    for name, part in parts.items():
        if name == "main":
            continue
        vocabulary = part["environment"]["vocabulary"]
        [item] = part["document"]["reading_sets"]
        choices = part["answer"]["choices"]
        sizes[name] = {"regulated_predicates": sum("regulated" in d for d in vocabulary["predicates"].values()),
                       "readings": len(item["readings"]), "choices": len(choices), "per_choice": []}
        for choice in choices:
            author = sum("norm" in (item["readings"][i].get("content") or {}) for _, i in choice
                         if type(item["readings"][i].get("content")) is dict)
            cases.append({"id": f"{name}:{choice}", "kind": "readings-choice", "environment": env, "document": doc,
                          "component": name, "choice": choice, "inner": {"kind": "norm-defaults-elaborate"}})
            keys.append((name, choice, author))
    rows = []
    for k in range(0, len(cases), 40):
        rows += run_lean(cases[k:k + 40])
    for (name, choice, author), row in zip(keys, rows):
        if row.get("status") != "ok" or row["inner"].get("status") != "ok":
            raise SystemExit(f"measure: Lean refused {name} {choice}: {row}")
        generated = len(row["inner"]["unspecified"])
        sizes[name]["per_choice"].append({"choice": choice, "author_rules": author, "generated_rules": generated,
                                          "rules": author + generated})
    return sizes


def checked_outside(commit, meta):
    """The units every reading of which had a companion checked by the run as a document of its own (and u074's
    kept companion): the units whose decided bytes the pilot had already checked outside the document (E2)."""
    names = {tuple(n.split(".")[:2]) for n in git_ls(commit, f"{RUN}/readings") if n.endswith(".ve.md")}
    units = {u for u, _ in names}
    by_unit = {s["unit"]: s for s in meta["reading_sets"]}
    return sorted(u for u in units if u not in by_unit or all((u, r["id"]) in names for r in by_unit[u]["readings"]))


def share(path, report_path, outside):
    """`tools/lean_decided_share.py` on the document with Lean's readings answer (if the report has one)."""
    folder = Path(tempfile.mkdtemp(prefix="rd5-share-"))
    report = json.loads(Path(report_path).read_text())
    args = [sys.executable, "tools/lean_decided_share.py", str(path)]
    if report.get("readings") is not None:
        (folder / "answer.json").write_text(json.dumps(report["readings"]))
        args += ["--answer", str(folder / "answer.json")]
    (folder / "outside.json").write_text(json.dumps(outside))
    args += ["--checked-outside", str(folder / "outside.json")]
    done = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(done.stdout)


def commit_of_tree():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "ve", "lean", "rust", "tools"], cwd=ROOT,
                           capture_output=True, text=True, check=True)
    return head.stdout.strip(), dirty.stdout.strip() == ""


def measure(out=HERE, commit=COMMIT):
    import witnesses
    out = Path(out)
    (out / "reports").mkdir(parents=True, exist_ok=True)
    (out / "answers").mkdir(parents=True, exist_ok=True)
    head, clean = commit_of_tree()
    before_path = Path(tempfile.mkdtemp(prefix="rd5-before-")) / "translation.ve.md"
    before_path.write_bytes(git_show(commit, f"{RUN}/translation.ve.md"))
    meta, _ = split_document(MIGRATED.read_bytes())
    before_meta, _ = split_document(before_path.read_bytes())
    unmigrated = json.loads((out / "unmigrated.json").read_text())
    sides = {}
    for side, path in (("before", before_path), ("after", MIGRATED)):
        load, load_t = timed("load", path)
        check, check_t = timed("check", path, out / "reports" / f"{side}.check.json")
        render, render_t = timed("render", path, out / "reports" / f"{side}.rendered.md")
        report = json.loads((out / "reports" / f"{side}.check.json").read_text())
        readings = report.get("readings") or {}
        sides[side] = {
            "document_bytes": path.stat().st_size, "load": {**load, **load_t}, "check": {**check, **check_t},
            "render": {**render, **render_t}, "premises": report["premises"]["status"],
            "conflict": (readings.get("conflict") or {}).get("status"),
            "bytes_by_status": report["coverage"]["bytes_by_status"],
            "share": share(path, out / "reports" / f"{side}.check.json", checked_outside(commit, before_meta)),
        }
    env, doc, parts = lean_split(meta)
    sizes = component_sizes(env, doc, parts)
    after = json.loads((out / "reports" / "after.check.json").read_text())["readings"]
    in_component = witnesses.in_components(env, doc, {k: v for k, v in parts.items() if k != "main"}, commit)
    alone = witnesses.alone(commit)
    queries = [query(MIGRATED, q, out / "answers" / f"{q['name']}.json") for q in QUERIES]
    separated = {s: unmigrated["situations"][s] for s in unmigrated["migrated"]}
    record = {
        "commit": head, "tree_clean_in_ve_lean_rust_tools": clean, "run": f"{RUN} at {commit}",
        "host": {"cpus": os.cpu_count()},
        "recorded": RECORDED,
        "before": sides["before"], "after": sides["after"],
        "components": {
            "count": len(parts), "companion_cases": len(sizes),
            "max_regulated_predicates": max(s["regulated_predicates"] for s in sizes.values()),
            "max_readings": max(s["readings"] for s in sizes.values()),
            "max_choices": max(s["choices"] for s in sizes.values()),
            "max_rules_in_one_choice_document": max(c["rules"] for s in sizes.values() for c in s["per_choice"]),
            "max_author_rules_in_one_choice_document": max(c["author_rules"] for s in sizes.values()
                                                           for c in s["per_choice"]),
            "per_component": sizes,
            "main_unchecked_sets": [u["set"] for c in after["components"] if c["component"] == "main"
                                    for u in c.get("unchecked", [])],
        },
        "migration": {
            "sets": unmigrated["sets"], "migrated": unmigrated["migrated"],
            "sets_admitted_with_every_pair_separated": len(separated),
            "situations_recorded": sum(separated.values()),
            "unseparated_pairs": [x for x in unmigrated["not_migrated"] if x["reason"] == "unseparated pairs"],
            "not_migrated": unmigrated["not_migrated"],
            "copied_declarations": unmigrated["copied_declarations"],
        },
        "witnesses": {
            "in_components": in_component,
            "in_components_total": sum(len(v["witnesses"]) for v in in_component.values()),
            "in_components_same": sum(w["same"] for v in in_component.values() for w in v["witnesses"]),
            "alone": alone,
            "companions_alone": len(alone),
            "companions_alone_model": sum(v["premises"] == "model" for v in alone.values()),
            "alone_total": sum(len(v["witnesses"]) for v in alone.values()),
            "alone_same": sum(w["same"] for v in alone.values() for w in v["witnesses"]),
        },
        "queries": queries,
    }
    (out / "metrics.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    return record


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "step":
        step(*argv[1:])
        return 0
    record = measure()
    print(json.dumps({"after": record["after"]["share"], "components": {k: v for k, v in record["components"].items()
                                                                        if k != "per_component"}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
