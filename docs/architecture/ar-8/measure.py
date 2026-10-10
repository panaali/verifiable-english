"""AR-8 evidence: measure base..head (fixed commits) into evidence.json and render REPORT.md's table.

    python3 docs/architecture/ar-8/measure.py BASE HEAD MUTANTS.json

reads `git diff --numstat BASE HEAD`, the line counts of the changed tools at both commits,
`git log --no-merges BASE..HEAD`, and the saved seeded-mutant results, writes evidence.json
next to this file, and rewrites the table between the markers in REPORT.md from it.
tests/test_ar8_evidence.py re-renders the table from the saved evidence and compares.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence.json"
REPORT = HERE / "REPORT.md"
START, END = "<!-- measured: begin -->", "<!-- measured: end -->"
FILES = ("tools/check_rust_deps.py", "tools/rust-module-exceptions.json", "tools/test_layer_policy.py")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=HERE, capture_output=True, text=True, check=True).stdout


def lines_at(commit: str, path: str) -> int:
    found = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=HERE, capture_output=True, text=True)
    return found.stdout.count("\n") if found.returncode == 0 else 0


def measure(base: str, head: str, mutants: list[dict]) -> dict:
    numstat = {}
    for row in git("diff", "--numstat", "--no-renames", base, head).splitlines():
        added, deleted, path = row.split("\t")
        numstat[path] = [int(added), int(deleted)]
    commits = [line.split(" ", 1) for line in git("log", "--no-merges", "--reverse", "--format=%H %s",
                                                     f"{base}..{head}").splitlines()]
    return {
        "batch": "AR-8", "base": git("rev-parse", base).strip(), "head": git("rev-parse", head).strip(),
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
    rows += ["", f"Diff `{evidence['base'][:8]}..{evidence['head'][:8]}` over {len(evidence['commits'])} commits "
             f"and {len(evidence['numstat'])} files: +{totals['added']} −{totals['deleted']} lines "
             f"(net {totals['added'] - totals['deleted']}).", "",
             "| Seeded bug | File | Test run | Exit | Result |", "|---|---|---|---:|---|"]
    rows += [f"| {row['mutant']} | `{row['file']}` | `{' '.join(row['tests']).split('::', 1)[-1]}` | {row['exit']} | "
             f"{row['summary']} |" for row in evidence["mutants"]]
    return "\n".join(rows)


def splice(report: str, table: str) -> str:
    head, rest = report.split(START, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{START}\n{table}\n{END}{tail}"


if __name__ == "__main__":
    base, head, mutants = sys.argv[1:4]
    evidence = measure(base, head, json.loads(Path(mutants).read_text()))
    EVIDENCE.write_text(json.dumps(evidence, indent=1, ensure_ascii=False) + "\n")
    REPORT.write_text(splice(REPORT.read_text(), render(evidence)))
