"""Measure identical readings-route requests on the base and batch Lean builds.

Usage: python tools/readings_batch_latency.py BASE_ROOT HEAD_ROOT CORPUS HEAD_COMMIT OUT
The caller supplies the same generated corpus used by lean_first_diff.py. Both commits are read from the two
checkouts (HEAD_COMMIT must be the head checkout's). Five
paired runs reduce host load noise; the gate compares mean Lean CPU per call
(the pairing, the CPU reading and the 20% rule are tools/evidence/latency.py's).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tools.evidence import checkouts, latency
from ve.backends.lean_service import LeanService
from ve.errors import VEError
from ve.readings_route import document_wire
from ve.readings_s1 import wire


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
    before = latency.cpu_ns(service.pid)
    for _ in range(calls):
        answer(service, case)
    return (latency.cpu_ns(service.pid) - before) / calls / 1_000_000


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base_root", "head_root", "corpus", "head_commit", "out"):
        parser.add_argument(name)
    parser.add_argument("--calls", type=int, default=100)
    parser.add_argument("--pairs", type=int, default=5)
    args = parser.parse_args()
    if args.calls <= 0 or args.pairs <= 0:
        parser.error("calls and pairs must be positive")
    base_commit, head_commit = checkouts(args.base_root, args.head_root)
    if head_commit != args.head_commit:
        parser.error(f"the head checkout is at {head_commit}, not {args.head_commit}")
    corpus = json.loads(Path(args.corpus).read_text())
    if len(corpus) < 3:
        parser.error("readings corpus has fewer than three cases")
    selected = [corpus[i] for i in (0, len(corpus) // 2, len(corpus) - 1)]
    binary = [Path(root) / "lean/.lake/build/bin/ve_service" for root in (args.base_root, args.head_root)]
    with LeanService(executable=binary[0]) as base, LeanService(executable=binary[1]) as head:
        cases = {}
        for item in selected:
            if item["case"] in cases:
                # Keyed by case name: a second case of the name would replace the first's row.
                raise RuntimeError(f"two readings cases are named {item['case']}")
            cases[item["case"]] = make_case(item)
        for key, case in cases.items():
            if answer(base, case) != answer(head, case):
                raise RuntimeError(f"base and head disagree on {key}")
        samples = latency.paired(cases, lambda key: measure(base, cases[key], args.calls),
                                 lambda key: measure(head, cases[key], args.calls), args.pairs)
        for key, row in samples.items():
            row.update(case_sha256=hashlib.sha256(json.dumps(cases[key], sort_keys=True).encode()).hexdigest(),
                       calls_per_side=args.calls * args.pairs)
    result = latency.record(base_commit, head_commit, samples,
                            "paired warm readings-route service calls; /proc service CPU time",
                            corpus_sha256=hashlib.sha256(Path(args.corpus).read_bytes()).hexdigest())
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
