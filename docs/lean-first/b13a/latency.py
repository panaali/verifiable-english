"""Measure batch 13a's warm parse and certificate service calls in this checkout.

Run from either checkout root with its own virtualenv Python. Prints JSON to stdout.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import statistics
import time

from conformance.order import environment as order_environment
from ve import Environment
from ve.ast import Top, formula_to_data
from ve.backends.lean_service import LeanService
from ve.entailment import prove_entailment


ROOT = Path.cwd()


def schedstat(pid: int) -> tuple[int, int]:
    run, wait, _ = Path(f"/proc/{pid}/schedstat").read_text().split()
    return int(run), int(wait)


def sample(service: LeanService, mode: str, case: dict, count: int = 100) -> dict:
    for _ in range(10):
        service.run(mode, [case])
    walls = []
    before = schedstat(service.pid)
    for _ in range(count):
        start = time.perf_counter_ns()
        service.run(mode, [case])
        walls.append((time.perf_counter_ns() - start) / 1_000_000)
    after = schedstat(service.pid)
    walls.sort()
    return {"mode": mode, "calls": count,
            "case_sha256": hashlib.sha256(json.dumps(case, sort_keys=True).encode()).hexdigest(),
            "wall_p50_ms": round(statistics.median(walls), 3),
            "wall_p95_ms": round(walls[int(0.95 * count) - 1], 3),
            "service_cpu_ms_per_call": round((after[0] - before[0]) / count / 1_000_000, 3),
            "runqueue_wait_ms_per_call": round((after[1] - before[1]) / count / 1_000_000, 3)}


def main() -> None:
    os.environ["VE_AUTHORITY"] = "python"
    order = order_environment().to_dict()
    raw = json.loads((ROOT / "conformance/evaluation.json").read_text())[0]["environment"]
    env = Environment.from_dict(raw)
    certificate = prove_entailment(env, [Top()], Top()).certificate
    assert certificate is not None
    formula = formula_to_data(env, Top())
    cert = {"id": "latency-cert", "environment": raw, "premises": [formula],
            "conclusion": formula, "certificate": certificate, "max_steps": 10000}
    workloads = [
        ("parse_accept", "parse", {"id": "latency-parse", "environment": order, "source": "true.\n"}),
        ("parse_reject", "parse", {"id": "latency-parse", "environment": order, "source": "true  .\n"}),
        ("certificate_accept", "check-certificate", cert),
        ("certificate_budget", "check-certificate", {**cert, "max_steps": 0}),
    ]
    with LeanService() as service:
        result = {name: sample(service, mode, case) for name, mode, case in workloads}
    print(json.dumps({"load": round(os.getloadavg()[0], 2), "workloads": result}, indent=2))


if __name__ == "__main__":
    main()
