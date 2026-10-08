"""Measure identical readings-route requests on the base and batch Lean builds.

Usage: python tools/readings_batch_latency.py BASE_ROOT HEAD_ROOT CORPUS HEAD_COMMIT OUT
The caller supplies the same generated corpus used by lean_first_diff.py. Five
paired runs reduce host load noise; the gate compares mean Lean CPU per call.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ve.backends.lean_service import LeanService
from ve.errors import VEError
from ve.readings_route import document_wire
from ve.readings_s1 import wire


def cpu_ns(pid: int) -> int:
    return int(Path(f"/proc/{pid}/schedstat").read_text().split()[0])


def make_case(item: dict) -> dict:
    """Send the same normalized request as the public readings validator."""
    document = item["document"]
    units = [{"id": unit["id"], "kind": unit.get("kind"),
              **({"content": unit["content"]} if "content" in unit else {})}
             for unit in document["units"]]
    return {"id": "readings-s1", "kind": "readings-validate",
            "environment": wire(item["environment"]),
            "document": wire(document_wire(units, document["reading_sets"]))}


def answer(service: LeanService, case: dict):
    try:
        return ("returned", service.run("readings-route", [case]))
    except VEError as exc:
        return ("raised", exc.code, exc.message)


def measure(service: LeanService, case: dict, calls: int) -> float:
    answer(service, case)
    before = cpu_ns(service.pid)
    for _ in range(calls):
        answer(service, case)
    return (cpu_ns(service.pid) - before) / calls / 1_000_000


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base_root", "head_root", "corpus", "head_commit", "out"):
        parser.add_argument(name)
    parser.add_argument("--calls", type=int, default=100)
    parser.add_argument("--pairs", type=int, default=5)
    args = parser.parse_args()
    if args.calls <= 0 or args.pairs <= 0:
        parser.error("calls and pairs must be positive")
    corpus = json.loads(Path(args.corpus).read_text())
    if len(corpus) < 3:
        parser.error("readings corpus has fewer than three cases")
    selected = [corpus[i] for i in (0, len(corpus) // 2, len(corpus) - 1)]
    binary = [Path(root) / "lean/.lake/build/bin/ve_service" for root in (args.base_root, args.head_root)]
    with LeanService(executable=binary[0]) as base, LeanService(executable=binary[1]) as head:
        samples = {}
        for item in selected:
            case = make_case(item)
            if answer(base, case) != answer(head, case):
                raise RuntimeError(f"base and head disagree on {item['case']}")
            base_cpu, head_cpu = [], []
            for _ in range(args.pairs):
                base_cpu.append(measure(base, case, args.calls))
                head_cpu.append(measure(head, case, args.calls))
            samples[item["case"]] = {
                "case_sha256": hashlib.sha256(json.dumps(case, sort_keys=True).encode()).hexdigest(),
                "calls_per_side": args.calls * args.pairs,
                "base_cpu_ms": round(sum(base_cpu) / len(base_cpu), 6),
                "head_cpu_ms": round(sum(head_cpu) / len(head_cpu), 6),
            }
    passed = all(row["head_cpu_ms"] <= 1.2 * row["base_cpu_ms"] for row in samples.values())
    result = {"head_commit": args.head_commit, "corpus_sha256": hashlib.sha256(Path(args.corpus).read_bytes()).hexdigest(),
              "method": "paired warm readings-route service calls; /proc service CPU time", "samples": samples,
              "pass": passed}
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
