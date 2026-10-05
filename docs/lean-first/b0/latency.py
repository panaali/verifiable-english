"""Batch 0's latency item (LEAN-FIRST-PLAN.md 5.1 item 4, section 4 budgets): one service call.

Run with the checkout to measure first on the path, so each commit is measured with its own
client and service build:

    PYTHONPATH=<checkout> python docs/lean-first/b0/latency.py [N]

Sends N single-case `check` requests, half accepted and half rejected (the rejections carry the
code batch 0 adds), to one warm `ve_service`, and prints wall p50/p95 per call and the service's
CPU per call (from /proc, utime + stime of the service process over the run).
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time

from tests.probe_matrix import raw_environment
from ve import Environment, Unary, Const
from ve.ast import formula_to_data
from ve.backends.lean_service import LeanService


def cpu_seconds(pid: int) -> float:
    fields = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()
    return (int(fields[11]) + int(fields[12])) / os.sysconf("SC_CLK_TCK")


def main(n: int) -> None:
    os.environ["VE_AUTHORITY"] = "python"
    env = Environment(raw_environment(()))
    good = formula_to_data(env, Unary("base", Const("x")))
    bad = json.loads(json.dumps(good).replace('"base"', '"missing"'))
    cases = [{"id": "c", "environment": env.to_dict(), "ast": [good if i % 2 else bad]} for i in range(n)]
    with LeanService() as service:
        service.run("check", cases[:20])
        pid, walls = service.pid, []
        start = cpu_seconds(pid)
        for case in cases:
            t0 = time.perf_counter()
            service.run("check", [case])
            walls.append((time.perf_counter() - t0) * 1000)
        cpu = (cpu_seconds(pid) - start) * 1000 / n
    walls.sort()
    print(json.dumps({"calls": n, "wall_p50_ms": round(statistics.median(walls), 3),
                      "wall_p95_ms": round(walls[int(0.95 * n) - 1], 3), "service_cpu_ms_per_call": round(cpu, 3),
                      "load": os.getloadavg()[0]}))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2000)
