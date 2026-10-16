"""Measure batch 14c's core route CPU and wall on the same host.

Usage: uv run python docs/lean-first/b14c/latency.py BASE_ROUTER HEAD_ROUTER OUT
The input is a fixed one-case JSON request; each invocation starts a process.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import resource
import statistics
import subprocess
import sys
import time

from tests.test_b14c import case
from tests.subprocesses import HANG_TIMEOUT


def measure(binary: Path, request: dict, rounds: int = 5) -> dict:
    cpu, wall = [], []
    data = json.dumps([request])
    for _ in range(rounds):
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        started = time.perf_counter()
        result = subprocess.run([str(binary), "route", "-"], input=data, text=True,
                                capture_output=True, timeout=HANG_TIMEOUT, check=False)
        wall.append(1000 * (time.perf_counter() - started))
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu.append(1000 * ((after.ru_utime + after.ru_stime) -
                           (before.ru_utime + before.ru_stime)))
        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(result.stdout)[0]["status"] == "ok"
    return {"cpu_ms": round(statistics.median(cpu), 3),
            "wall_ms": round(statistics.median(wall), 3)}


def main() -> None:
    base, head, out = map(Path, sys.argv[1:])
    env, model = case()
    plain = deepcopy(env)
    plain["profiles"] = ["closure@0", "nary@0", "relational-fol@0"]
    for entry in plain["vocabulary"]["predicates"].values():
        entry.pop("defined", None)
    common = {"id": "common", "kind": "background", "environment": plain}
    nary = {"id": "nary", "kind": "evaluate", "environment": env, "model": model,
            "ast": [["exists", "s", ["exists", "s", ["exists", "s",
                     ["atom", "derived", [["var", 2], ["var", 1], ["var", 0]]]]]]]}
    base_result = measure(base, common)
    head_result = measure(head, common)
    nary_result = measure(head, nary)
    evidence = {"samples": {"core-background": {
        "base_cpu_ms": base_result["cpu_ms"], "head_cpu_ms": head_result["cpu_ms"],
        "base_wall_ms": base_result["wall_ms"], "head_wall_ms": head_result["wall_ms"]}},
        "nary": nary_result,
        "pass": head_result["cpu_ms"] <= 1.2 * base_result["cpu_ms"] and
                nary_result["cpu_ms"] <= 1000 and nary_result["wall_ms"] <= 2000}
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    main()
