"""Check that a batch's saved gate, corpus comparison and latency evidence cover HEAD.

The gate result lives in a git note so recording it does not move the commit it
checked. Call this tool with the final commit and the three evidence files before
attaching the note. No missing or partial measurement counts as a pass.

A note is a local ref that a merge or push does not carry, so the batch may also commit
a copy of the evidence. That report commit comes after the gated one; with
`--report-commit SHA --report-dir DIR` the tool also checks that the gated commit is an
ancestor of it and that nothing between them changes a path outside DIR, so the gate
still covers every line of code the report commit holds.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from tools import gate_collection

REQUIRED_STAGES = ("toolchains", "lean_build", "lean_audit", "rust_build", "cargo_test", "pytest")
REQUIRED_CORPORA = {"probe", "conformance", "readings", "pilots", "discourse", "rights", "quantity"}


def problems(head: str, gate: dict, comparison: dict, latency: dict) -> list[str]:
    errors = []
    if gate.get("commit_sha") != head or gate.get("dirty") is not False:
        errors.append("full gate did not run on a clean HEAD")
    if gate.get("status") != "passed" or gate.get("stages") != list(REQUIRED_STAGES):
        errors.append("full gate is incomplete or failed")
    counts = gate.get("counts")
    if not isinstance(counts, dict) or not all(type(counts.get(key)) is int and counts[key] > 0
                                                for key in ("passed", "rust_passed")):
        errors.append("full gate has no passing Python and Rust tests")
    if comparison.get("head_commit") != head:
        errors.append("corpus comparison did not run on HEAD")
    if comparison.get("unlisted") != 0 or comparison.get("unavailable_both") != {}:
        errors.append("corpus comparison has an unlisted or unavailable result")
    records = comparison.get("records")
    if not isinstance(records, dict) or not REQUIRED_CORPORA <= {k.split("/", 1)[0] for k, v in records.items()
                                                                 if type(v) is int and v > 0}:
        errors.append("corpus comparison omitted a required corpus")
    if latency.get("head_commit") != head or latency.get("pass") is not True:
        errors.append("latency budget was not measured and passed on HEAD")
    samples = latency.get("samples")
    if not isinstance(samples, dict) or not samples or not all(
        isinstance(row, dict) and type(row.get("base_cpu_ms")) in (int, float)
        and type(row.get("head_cpu_ms")) in (int, float) and row["base_cpu_ms"] > 0
        and 0 <= row["head_cpu_ms"] <= 1.2 * row["base_cpu_ms"]
        for row in samples.values()
    ):
        errors.append("latency evidence is empty, malformed or above the 20% Lean CPU budget")
    return errors


def outside_report(changed: list[str], report_dir: str) -> list[str]:
    """The errors of a commit after the gate: every changed path outside `report_dir`."""
    prefix = report_dir.strip("/") + "/"
    outside = sorted(path for path in changed if not path.startswith(prefix))
    return [f"a commit after the gate changes {path}, outside {prefix}" for path in outside]


def changed_since(gated: str, report: str, cwd: Path | None = None) -> list[str]:
    """The paths that differ between the gated commit and the report commit (renames as delete and add), or an
    error if the gated commit is not an ancestor of the report commit."""
    git = ["git", "--no-optional-locks", "-c", "core.quotePath=false"]
    if subprocess.run(git + ["merge-base", "--is-ancestor", gated, report], cwd=cwd).returncode != 0:
        raise ValueError(f"the gated commit {gated} is not an ancestor of {report}")
    out = subprocess.run(git + ["diff", "--no-renames", "--name-only", "-z", gated, report], cwd=cwd,
                         check=True, capture_output=True).stdout
    return [path for path in out.decode().split("\0") if path]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("head")
    parser.add_argument("gate", type=Path)
    parser.add_argument("comparison", type=Path)
    parser.add_argument("latency", type=Path)
    parser.add_argument("--report-commit", help="a later commit that may change only --report-dir")
    parser.add_argument("--report-dir", help="the batch's report directory, relative to the repository root")
    args = parser.parse_args()
    if (args.report_commit is None) != (args.report_dir is None):
        parser.error("--report-commit and --report-dir go together")
    try:
        values = [json.loads(p.read_text()) for p in (args.gate, args.comparison, args.latency)]
        errors = problems(args.head, *values)
        # A local gate note is the authoritative record when present. A copy
        # travels with batch evidence because git notes do not travel with a merge.
        note = gate_collection.read_gate_result(args.head, cwd=Path.cwd())
        if note is not None and note != values[0]:
            errors.append("gate evidence differs from its git note")
        if args.report_commit is not None:
            errors += outside_report(changed_since(args.head, args.report_commit), args.report_dir)
    except (OSError, ValueError, TypeError, subprocess.CalledProcessError) as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(errors))
        return 1
    later = f"; report commit {args.report_commit} changes only {args.report_dir}" if args.report_commit else ""
    print(f"batch evidence PASS on {args.head}{later}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
