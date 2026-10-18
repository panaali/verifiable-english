"""Measure batch 14b's warm family-norms service calls in each checkout.

    python docs/lean-first/b14b/latency.py --base /tmp/lf14b-base --out OUT.json

The FOL control request is identical on both sides. The reachability request
measures the new Lean work on the head; the base service does not accept it.
Each measurement owns and reaps its service child, so RUSAGE_CHILDREN is Lean
CPU rather than Python CPU. Measurements alternate base and head three times.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]


def worker(root: Path, iterations: int) -> dict:
    from ve.ast import Named, Reach, Top, Var
    from ve.backends.lean_service import LeanService
    from ve.environment import Environment
    from ve.norms import Norm, NormDocument, _lean_case
    from ve.profiles import LANGUAGE, SPEC_REVISION

    env = Environment({"language": LANGUAGE, "profiles": ["closure@0", "norms@0", "relational-fol@0"],
                       "spec_revision": SPEC_REVISION,
                       "vocabulary": {"sorts": {"act": {"description": "act"}},
                                      "predicates": {
                                          "before": {"arguments": ["act", "act"], "description": "before"},
                                          "permitted": {"arguments": ["act"], "description": "permitted",
                                                        "regulated": {"role": "permission", "default": "deny",
                                                                      "act": "{0} be done"}}},
                                      "constants": {}}})
    formulas = {"fol": Top(), "reach": Reach("star", Named("before"), Var(0), Var(0))}
    rows = {}
    for name, guard in formulas.items():
        doc = NormDocument(env, [Norm("may", "permitted", True, guard)])
        case = _lean_case(doc, "norms-elaborate")
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        start = time.perf_counter()
        longest_call = 0.0
        with LeanService(root / "lean/.lake/build/bin/ve_service") as service:
            first = None
            for _ in range(iterations):
                call_start = time.perf_counter()
                answer = service.run("family-norms", [case])[0]
                longest_call = max(longest_call, time.perf_counter() - call_start)
                if first is None:
                    first = answer
        wall = time.perf_counter() - start
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
        rows[name] = {"wall_ms_per_case": wall * 1000 / iterations,
                      "lean_cpu_ms_per_case": cpu * 1000 / iterations,
                      "longest_call_wall_ms": longest_call * 1000,
                      "total_lean_cpu_ms": cpu * 1000,
                      "answer_sha256": hashlib.sha256(json.dumps(first, sort_keys=True).encode()).hexdigest(),
                      "status": first.get("status")}
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--worker", type=Path)
    args = parser.parse_args()
    if args.worker is not None:
        print(json.dumps(worker(args.worker.resolve(), args.iterations)))
        return 0
    if args.base is None or args.out is None or args.iterations < 1:
        parser.error("--base, --out and positive --iterations are required")
    roots = {"base": args.base.resolve(), "head": ROOT}
    samples = {"base": [], "head": []}
    for _ in range(3):
        for side, root in roots.items():
            env = {**os.environ, "PYTHONPATH": str(root),
                   "PATH": str(Path.home() / ".elan/bin") + ":" + os.environ.get("PATH", "")}
            done = subprocess.run([sys.executable, __file__, "--worker", str(root),
                                   "--iterations", str(args.iterations)], env=env,
                                  capture_output=True, text=True, check=True)
            samples[side].append(json.loads(done.stdout))
    def median(side, name, metric):
        return statistics.median(row[name][metric] for row in samples[side])
    same_fol = len({row["fol"]["answer_sha256"] for side in samples for row in samples[side]}) == 1
    base_cpu = median("base", "fol", "lean_cpu_ms_per_case")
    head_cpu = median("head", "fol", "lean_cpu_ms_per_case")
    reach_cpu = median("head", "reach", "lean_cpu_ms_per_case")
    reach_wall = median("head", "reach", "wall_ms_per_case")
    reach_max_wall = max(row["reach"]["longest_call_wall_ms"] for row in samples["head"])
    reach_max_cpu_upper_bound = max(row["reach"]["total_lean_cpu_ms"] for row in samples["head"])
    result = {"samples": samples, "median": {"fol": {"base_cpu_ms": base_cpu, "head_cpu_ms": head_cpu},
                                               "reach": {"head_cpu_ms": reach_cpu,
                                                         "head_wall_ms": reach_wall,
                                                         "max_call_wall_ms": reach_max_wall,
                                                         "per_call_cpu_upper_bound_ms": reach_max_cpu_upper_bound}},
              "same_fol_answer": same_fol,
              "pass": (same_fol and head_cpu <= 1.2 * base_cpu
                       and reach_max_cpu_upper_bound <= 1000 and reach_max_wall <= 2000)}
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["median"] | {"same_fol_answer": same_fol, "pass": result["pass"]}))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
