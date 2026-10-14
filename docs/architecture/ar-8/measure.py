"""AR-8 evidence: measure `main..HEAD --no-merges` at the code head into evidence.json and render REPORT.md's table.

    uv run python docs/architecture/ar-8/measure.py

runs on a clean tree at the batch's last code commit. It reads `git diff --numstat BASE HEAD` (BASE is the
merge base with `main`), the line counts of the changed tools at both commits, `git log --no-merges BASE..HEAD`,
plants each seeded bug below in turn and runs its tests (restoring the file after each), writes evidence.json
next to this file, and rewrites the table between the markers in REPORT.md from it. The next commit, with the
subject REPORT_SUBJECT, holds only this folder; tests/test_ar8_evidence.py checks the table against the saved
evidence and that the saved commits are every commit before that report commit, so a code commit made after the
evidence fails until the evidence is measured again.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import nested_pytest  # noqa: E402
EVIDENCE = HERE / "evidence.json"
REPORT = HERE / "REPORT.md"
REPORT_SUBJECT = "AR-8: saved evidence and report"
START, END = "<!-- measured: begin -->", "<!-- measured: end -->"
FILES = ("tools/check_rust_deps.py", "tools/rust-module-exceptions.json", "tools/test_layer_policy.py")
CHECKER, HOOK = "tools/check_rust_deps.py", "tools/hooks/precommit.py"
POLICY = "tools/test_layer_policy.py::LayerSelectionTests::"
# Seeded bugs, one per behaviour the report claims: (id and behaviour, file, text, replacement, tests).
MUTANTS = (
    ("M1 outward edges never reported", CHECKER,
     'found.append(f"outward crate dependency: {name} -> {target}")', "pass",
     [POLICY + "test_outward_crate_dependencies_are_rejected"]),
    ("M2 dev and build dependencies skipped", CHECKER,
     'for dependency in package["dependencies"]:\n            targets',
     'for dependency in [d for d in package["dependencies"] if d["kind"] is None]:\n            targets',
     [POLICY + "test_renamed_and_inherited_rust_dependencies_are_read_as_cargo_resolves_them"]),
    ("M3 facade modules ignored", CHECKER, 'rglob("*.rs")) if path != entry]', 'rglob("*.rs")) if False]',
     [POLICY + "test_modules_in_the_facade_are_rejected"]),
    ("M4 outside path dependency accepted", CHECKER,
     'found.append(f"path dependency outside the workspace: {name} -> {alias}")', "pass",
     [POLICY + "test_unmapped_crates_and_outside_path_dependencies_are_rejected"]),
    ("M5 hook snapshot without Rust sources", HOOK, "if RUST_WORKSPACE.fullmatch(p))]",
     'if RUST_WORKSPACE.fullmatch(p) and p.endswith(".toml"))]',
     ["tests/test_precommit_hook.py::test_staged_rust_workspace_is_read_by_cargo"]),
    ("M6 facade without a library accepted", CHECKER, 'found.append(f"the {FACADE} facade has no library target")',
     "pass", [POLICY + "test_modules_in_the_facade_are_rejected"]),
    ("M7 unmapped crates accepted", CHECKER, "if names != set(CRATE_LAYERS):", "if False:",
     [POLICY + "test_unmapped_crates_and_outside_path_dependencies_are_rejected"]),
    ("M8 declared name of a path dependency not compared", CHECKER, 'if reached != dependency["name"]:', "if False:",
     [POLICY + "test_path_dependencies_must_name_the_crate_their_path_holds"]),
    ("M9 facade lib.rs not read", CHECKER, "found += facade_errors(entry.read_bytes(), roots)", "found += []",
     [POLICY + "test_the_facade_holds_only_re_exports"]),
    ("M10 facade re-exports from any crate", CHECKER, 'use["root"] in roots', "True",
     [POLICY + "test_the_facade_holds_only_re_exports"]),
    ("M11 facade may end inside an item", CHECKER, "if block or attributes else []", "if False else []",
     [POLICY + "test_the_facade_holds_only_re_exports"]),
)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def lines_at(commit: str, path: str) -> int:
    found = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return found.stdout.count("\n") if found.returncode == 0 else 0


def run_mutants() -> list[dict]:
    """Plant each seeded bug alone, run its tests, and restore the file."""
    rows = []
    for mutant, path, text, replacement, tests in MUTANTS:
        file = ROOT / path
        original = file.read_text()
        if original.count(text) != 1:
            raise SystemExit(f"{mutant}: the planted text is not found exactly once in {path}")
        try:
            file.write_text(original.replace(text, replacement))
            run = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", *tests]), cwd=ROOT,
                                 env=nested_pytest.environment(os.environ), capture_output=True, text=True)
        finally:
            file.write_text(original)
        summary = run.stdout.strip().splitlines()[-1].strip("= ") if run.stdout.strip() else run.stderr.strip()
        rows.append({"mutant": mutant, "file": path, "tests": tests, "exit": run.returncode, "summary": summary})
    return rows


def measure(base: str, head: str, mutants: list[dict]) -> dict:
    numstat = {}
    for row in git("diff", "--numstat", "--no-renames", base, head).splitlines():
        added, deleted, path = row.split("\t")
        numstat[path] = [int(added), int(deleted)]
    commits = [line.split(" ", 1) for line in git("log", "--no-merges", "--reverse", "--format=%H %s",
                                                     f"{base}..{head}").splitlines()]
    return {
        "batch": "AR-8", "range": "main..HEAD --no-merges", "report_subject": REPORT_SUBJECT,
        "base": git("rev-parse", base).strip(), "head": git("rev-parse", head).strip(),
        "commits": [{"sha": sha, "subject": subject} for sha, subject in commits],
        "numstat": numstat,
        "totals": {"added": sum(a for a, _ in numstat.values()), "deleted": sum(d for _, d in numstat.values())},
        "lines": {path: {"base": lines_at(base, path), "head": lines_at(head, path)} for path in FILES},
        "mutants": mutants,
    }


def render(evidence: dict) -> str:
    """The report's measured table, from the saved evidence alone."""
    rows = ["| Measure | Base | Head |", "|---|---:|---:|"]
    rows += [f"| `{path}` lines | {count['base']} | {count['head']} |" for path, count in evidence["lines"].items()]
    totals = evidence["totals"]
    rows += ["", f"Diff `{evidence['base'][:8]}..{evidence['head'][:8]}` (`{evidence['range']}` at the code head) "
             f"over {len(evidence['commits'])} commits and {len(evidence['numstat'])} files: +{totals['added']} "
             f"−{totals['deleted']} lines (net {totals['added'] - totals['deleted']}).", "",
             "| Seeded bug | File | Test run | Exit | Result |", "|---|---|---|---:|---|"]
    rows += [f"| {row['mutant']} | `{row['file']}` | `{' '.join(row['tests']).split('::', 1)[-1]}` | {row['exit']} | "
             f"{row['summary']} |" for row in evidence["mutants"]]
    return "\n".join(rows)


def splice(report: str, table: str) -> str:
    head, rest = report.split(START, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{START}\n{table}\n{END}{tail}"


if __name__ == "__main__":
    if sys.argv[1:] or git("status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("usage: measure.py (no arguments), on a clean tree at the batch's last code commit")
    base = git("merge-base", "HEAD", "main").strip()
    evidence = measure(base, "HEAD", run_mutants())
    EVIDENCE.write_text(json.dumps(evidence, indent=1, ensure_ascii=False) + "\n")
    REPORT.write_text(splice(REPORT.read_text(), render(evidence)))
