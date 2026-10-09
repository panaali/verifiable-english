"""Latency of the public operations lean-first batch 15b changes (gate item 4), in one checkout.

* `evaluate` under `VE_AUTHORITY=lean`: base, Rust's evaluator with Lean checking the value; head, Lean's
  metered evaluator (`ve_metered`, one process per call).
* `find_countermodel` under the default authority on the search fixtures (`conformance/search.json`):
  base, Python's search; head, Rust's search with its witness checked.

Run once per checkout (its own `ve`, Lean and Rust builds) and compare the two outputs::

    uv run --frozen python docs/lean-first/b15b/latency.py --out latency-head.json
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import resource
import statistics
import sys
import time

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))


def _cpu() -> float:
    own, children = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + children.ru_utime + children.ru_stime


def timed(call, repeats: int) -> dict:
    call()  # warm: start the persistent processes
    walls, cpus = [], []
    for _ in range(repeats):
        cpu, started = _cpu(), time.perf_counter()
        call()
        walls.append(time.perf_counter() - started)
        cpus.append(_cpu() - cpu)
    walls.sort()
    return {"calls": repeats, "wall_p50_ms": round(statistics.median(walls) * 1000, 3),
            "wall_p95_ms": round(walls[int(0.95 * (len(walls) - 1))] * 1000, 3),
            "cpu_p50_ms": round(statistics.median(cpus) * 1000, 3)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repeats", type=int, default=40)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    from ve import Environment, FiniteModel
    from ve.ast import document_from_data, formula_from_data
    from ve.evaluate import evaluate
    from ve.search import find_countermodel
    result = {"load": Path("/proc/loadavg").read_text().split()[0]}
    cases = json.loads((ROOT / "conformance/evaluation.json").read_text())[:10]
    loaded = []
    for case in cases:
        env = Environment(case["environment"])
        loaded.append((env, document_from_data(env, case["ast"]), FiniteModel.from_dict(env, case["model"])))
    os.environ["VE_AUTHORITY"] = "lean"
    result["evaluate_lean_traced"] = timed(lambda: [evaluate(e, d, m) for e, d, m in loaded], args.repeats)
    del os.environ["VE_AUTHORITY"]
    queries = [q for q in json.loads((ROOT / "conformance/search.json").read_text()) if "expected_search" in q]
    searches = []
    for q in queries:
        env = Environment(q["environment"])
        searches.append((env, [formula_from_data(env, p) for p in q["premises"]],
                         formula_from_data(env, q["conclusion"]),
                         {k: q[k] for k in ("max_domain_size", "max_models", "max_evaluations")}))
    result["search_default_authority"] = timed(
        lambda: [find_countermodel(e, ps, c, **o) for e, ps, c, o in searches], max(args.repeats // 4, 5))
    result["per_call"] = {"evaluate": len(loaded), "search": len(searches)}
    Path(args.out).write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
