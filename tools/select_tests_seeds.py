"""Seeded edits that check tools/select_tests.py against the complete suite.

Each seed is an edit a test can observe: a field of one assurance-manifest operation that
`ve` reads at run time (a Lean binding, a call site, a response field), or a Lean module
added to one executable's import closure. For each seed the selector plans the edit with a
coverage map recorded at the same commit (so no drift widens the plan), and the complete
suite runs with the edit applied. Every test file that fails must be in the plan.

The suite runs once with every seed applied (they touch disjoint operations and one
executable), then every file that failed runs again under each seed alone and, for failures
no single seed explains, without any seed. A seed's failures are those of its own rerun.
Failures that also fail without any seed are left out. That equals running the complete
suite under the seed alone unless another seed hides one of its failures; each seed only
adds a refusal, so none can, and a failure no rerun reproduces fails the tool.

    python tools/select_tests_seeds.py run --map MAP --work DIR [--workers N]

writes `--output` (default docs/test-speed-b1/evidence/manifest-seeds.json). It resumes
from `--work`, so the complete run and the reruns can be separate calls. It needs a clean
tree at the map's commit and built binaries; it restores every seeded file.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from layer_policy import ROOT
import nested_pytest
import select_tests
import test_map

OUTPUT = ROOT / "docs/test-speed-b1/evidence/manifest-seeds.json"
MANIFEST = select_tests.MANIFEST
SEED_MODULE = "lean/VE/SeedProbe.lean"
SEED_ROOT = "lean/SensesMain.lean"
SEED_EXECUTABLE = "ve_senses_route"


def manifest_text(manifest: dict) -> str:
    """The manifest file's own layout, so a seed changes only the edited field."""
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def _operation(manifest: dict, op_id: str) -> dict:
    return next(row for row in manifest["operations"] if row["id"] == op_id)


def _binding(op: dict, executable: str, mode: str, kinds: tuple[str, ...] = ()) -> dict:
    return next(b for b in op["lean"]["bindings"]
                if b["executable"] == executable and b["mode"] == mode and tuple(b.get("kinds", ())) == kinds)


def _rename_mode(executable, mode, kinds=()):
    return lambda op: _binding(op, executable, mode, kinds).update(mode=f"{mode}-seeded")


def _require_field(executable, mode, kinds=()):
    return lambda op: _binding(op, executable, mode, kinds)["response"].update(seeded="bool")


def _no_call_sites(op):
    op["lean_call_sites"] = []


# (operation, the field the edit changes, the edit). Each field is read at run time:
# `require_lean_binding` matches executable and mode, `row_problem` requires every field of
# `response`, `require_lean_call_site` checks the calling function.
MANIFEST_SEEDS = (
    ("graph.compose", "lean.bindings[ve_conformance check-certificate].mode",
     _rename_mode("ve_conformance", "check-certificate")),
    ("norms.elaborate", "lean.bindings[ve_service norms].mode",
     _rename_mode("ve_service", "norms", ("norms-elaborate",))),
    ("certificate.check", "lean.bindings[ve_conformance route certificate].response",
     _require_field("ve_conformance", "route", ("certificate",))),
    ("evaluate", "lean_call_sites", _no_call_sites),
    ("bundle.check", "lean_call_sites", _no_call_sites),
)

LEAN_SEED_MODULE = ('/-! A module the selector evidence adds for one run (tools/select_tests_seeds.py). -/\n'
                    'def VE.SeedProbe.banner : String := "seeded module"\n')


def seeds(root: Path = ROOT) -> list[dict]:
    """Every seed: its name, kind, operation (manifest seeds) and the files it writes."""
    original = (root / MANIFEST).read_text(encoding="utf-8")
    rows = []
    for op_id, field, edit in MANIFEST_SEEDS:
        manifest = json.loads(original)
        edit(_operation(manifest, op_id))
        rows.append({"name": f"{op_id}: {field}", "kind": "manifest", "operation": op_id, "field": field,
                     "edit": edit, "files": {MANIFEST: manifest_text(manifest)}})
    senses = (root / SEED_ROOT).read_text(encoding="utf-8")
    header, _, body = senses.partition("\n\n")
    if not body.startswith("def main (args : List String) : IO UInt32 := "):
        raise RuntimeError(f"{SEED_ROOT} changed; update the Lean seed")
    call = body.removeprefix("def main (args : List String) : IO UInt32 := ").strip()
    rows.append({"name": f"{SEED_MODULE} added to {SEED_EXECUTABLE}", "kind": "lean", "operation": None,
                 "field": f"{SEED_ROOT} imports the added module and prints its banner first",
                 "files": {SEED_MODULE: LEAN_SEED_MODULE,
                           SEED_ROOT: f"{header}\nimport VE.SeedProbe\n\n"
                                      "def main (args : List String) : IO UInt32 := do\n"
                                      "  IO.println VE.SeedProbe.banner\n"
                                      f"  {call}\n"}})
    return rows


def _git(*args: str) -> str:
    return subprocess.run(("git", *args), cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def _environment(result: Path | None = None) -> dict[str, str]:
    env = nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1", VE_LEAN_PREBUILT="1")
    env.setdefault("UV_CACHE_DIR", "/tmp/ve-layers-uv-cache")
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
    env["PYTHONPATH"] = str(ROOT / "tools") + os.pathsep + env.get("PYTHONPATH", "")
    if result is not None:
        env["VE_GATE_PYTEST_RESULT"] = str(result)
    return env


def combined_files(rows: list[dict], root: Path = ROOT) -> dict[str, str]:
    """The files of every seed in `rows` applied together: one manifest with each edit."""
    files = {path: text for row in rows if row["kind"] != "manifest" for path, text in row["files"].items()}
    edits = [row for row in rows if row["kind"] == "manifest"]
    if edits:
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        for row in edits:
            row["edit"](_operation(manifest, row["operation"]))
        files[MANIFEST] = manifest_text(manifest)
    return files


class Applied:
    """Write seeds' files, rebuild what a Lean seed changes, and restore everything on exit."""

    def __init__(self, rows: list[dict], *, build: bool = True):
        self.files = combined_files(rows)
        self.lean = build and any(row["kind"] == "lean" for row in rows)

    def __enter__(self):
        self.before = {path: (ROOT / path).read_text(encoding="utf-8") if (ROOT / path).exists() else None
                       for path in self.files}
        for path, text in self.files.items():
            (ROOT / path).write_text(text, encoding="utf-8")
        if self.lean:
            _build()
        return self

    def __exit__(self, *exc):
        for path, text in self.before.items():
            if text is None:
                (ROOT / path).unlink(missing_ok=True)
            else:
                (ROOT / path).write_text(text, encoding="utf-8")
        if self.lean:
            _build()


def _build() -> None:
    subprocess.run(["lake", "build", SEED_EXECUTABLE], cwd=ROOT / "lean", env=_environment(), check=True,
                   stdout=subprocess.DEVNULL)


def failures(units: list[str], work: Path, label: str, workers: int) -> list[str]:
    """Failing test ids (a file id when the file failed to collect) of `units` in the current tree."""
    pytest_units = [u for u in units if u not in test_map.EXTRA_UNITS]
    result = work / f"{label}.json"
    failed: set[str] = set()
    if pytest_units:
        command = nested_pytest.command(
            ["-q", "-p", "no:cacheprovider", "-p", "gate_pytest", *pytest_units],
            workers=max(1, min(workers, len(pytest_units))),
            python=["uv", "run", "--frozen", "--group", "dev", "python"])
        with (work / f"{label}.log").open("w") as log:
            subprocess.run(command, cwd=ROOT, env=_environment(result), stdout=log, stderr=subprocess.STDOUT,
                           check=False)
        events = json.loads(result.read_text())
        failed |= {row["nodeid"] for row in events["collection_reports"] if row["outcome"] == "failed"}
        failed |= {nodeid for nodeid, row in events["tests"].items() if row["outcome"] == "failed"}
        if not events["tests"] and not failed:
            raise RuntimeError(f"{label}: pytest recorded no test; see {work / f'{label}.log'}")
    for unit in units:
        if unit in test_map.EXTRA_UNITS:
            done = subprocess.run(test_map.EXTRA_UNITS[unit], cwd=ROOT, env=_environment(),
                                  capture_output=True, check=False)
            if done.returncode != 0:
                failed.add(unit)
    return sorted(failed)


def _file(nodeid: str) -> str:
    return nodeid.split("::", 1)[0]


def run(args: argparse.Namespace) -> int:
    if _git("status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("the tree must be clean: the seeds are written into it and restored")
    head = _git("rev-parse", "HEAD")
    coverage = test_map.load(Path(args.map))
    if coverage["commit"] != head:
        raise SystemExit(f"the map is for {coverage['commit'][:12]}, not HEAD {head[:12]}")
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    state_path = work / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {"head": head}
    if state["head"] != head:
        raise SystemExit("--work holds results for another commit")

    def save():
        state_path.write_text(json.dumps(state, indent=1) + "\n")

    rows = seeds()
    every = test_map.units()
    plans = state.setdefault("plans", {})
    for row in rows:
        if row["name"] in plans:
            continue
        with Applied([row], build=False):  # the plan reads the files; nothing to build yet
            plan = select_tests.select(sorted(row["files"]), base="HEAD", coverage=coverage)
        plans[row["name"]] = {"selected": sorted(plan["selected"]), "full": plan["full"],
                              "full_reasons": plan["full_reasons"]}
        save()
    if "combined" not in state:
        started = time.monotonic()
        with Applied(rows):
            state["combined"] = failures(every, work, "combined", args.workers)
        state["combined_seconds"] = round(time.monotonic() - started)
        save()
    files = sorted({_file(nodeid) for nodeid in state["combined"]})
    alone = state.setdefault("alone", {})
    for row in rows:
        if row["name"] not in alone:
            with Applied([row]):
                alone[row["name"]] = failures(files, work, f"alone-{len(alone)}", args.workers) if files else []
            save()
    if "unseeded" not in state:
        state["unseeded"] = failures(files, work, "unseeded", args.workers) if files else []
        save()
    baseline = set(state["unseeded"])  # fails without any seed: not evidence about a seed
    explained = {nodeid for found in alone.values() for nodeid in found} | baseline
    unexplained = sorted(set(state["combined"]) - explained)
    report = {
        "schema": 2, "head": head, "map_commit": coverage["commit"], "map_version": coverage["version"],
        "map_tests": len(coverage["tests"]), "full_count": len(every),
        "map_failed_units": sorted(t for t, s in coverage["status"].items() if s["exit"] not in (0, 5)),
        "method": "complete suite once with every seed applied, then each failing file under each seed alone",
        "combined_failure_nodeids": state["combined"], "combined_seconds": state["combined_seconds"],
        "failures_no_seed_explains": unexplained, "failures_without_seeds": state["unseeded"],
        "seeds": []}
    # A seed's failures exclude those that also fail without seeds.
    for row in rows:
        plan, found = plans[row["name"]], sorted(set(alone[row["name"]]) - baseline)
        report["seeds"].append({
            "name": row["name"], "kind": row["kind"], "operation": row["operation"], "field": row["field"],
            "paths": sorted(row["files"]), "selected": plan["selected"], "selected_count": len(plan["selected"]),
            "selection_full": plan["full"], "full_reasons": plan["full_reasons"],
            "recorded_entry_readers": sorted(coverage["tests"][i] for i in coverage["operations"].get(
                row["operation"], ())) if row["operation"] else [],
            "full_failure_nodeids": found,
            "failures_outside_selection": sorted({_file(n) for n in found} - set(plan["selected"]))})
    Path(args.output).write_text(json.dumps(report, indent=1) + "\n")
    problems = [f"{seed['name']}: {seed['failures_outside_selection'] or 'no failure'}" for seed in report["seeds"]
                if seed["failures_outside_selection"] or not seed["full_failure_nodeids"]]
    print("\n".join(problems) or f"{len(rows)} seeds: every failure selected")
    if unexplained:
        print(f"failed only with every seed applied (flaky, or seeds that interact): {unexplained}")
    return 1 if problems or unexplained else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    go = sub.add_parser("run")
    go.add_argument("--map", required=True, help="a coverage map recorded at HEAD")
    go.add_argument("--work", required=True, help="logs and partial results; a rerun resumes from it")
    go.add_argument("--workers", type=int, default=12)
    go.add_argument("--output", default=str(OUTPUT))
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
