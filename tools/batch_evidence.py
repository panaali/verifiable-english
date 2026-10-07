"""Check that a batch's saved gate, corpus comparison and latency evidence cover HEAD.

The gate result lives in a git note so recording it does not move the commit it
checked. Call this tool with the final commit and the three evidence files before
attaching the note. No missing or partial measurement counts as a pass.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("head")
    parser.add_argument("gate", type=Path)
    parser.add_argument("comparison", type=Path)
    parser.add_argument("latency", type=Path)
    args = parser.parse_args()
    try:
        values = [json.loads(p.read_text()) for p in (args.gate, args.comparison, args.latency)]
        errors = problems(args.head, *values)
    except (OSError, ValueError, TypeError) as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(errors))
        return 1
    print(f"batch evidence PASS on {args.head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
