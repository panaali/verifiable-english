"""Measure batch 14a's changed path in this checkout: warm `parse` service calls over a `definitions@0`
environment, and the public `ve.parser.parse` of the same sources (plan 5.1 item 4).

Run from either checkout root with its own virtualenv Python (`cd ROOT && uv run python
<this file>`); prints JSON to stdout. At the base a sugared source never reached the service (Python's
reading was kept); the service rows are measured on both sides all the same, so the
non-sugar rows compare like for like and the sugar rows show the head's new cost.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import time

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from tests import probe_matrix as pm  # noqa: E402
from ve import Environment  # noqa: E402
from ve.backends.lean_service import LeanService  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.parser import parse  # noqa: E402

SOURCES = {
    "plain_accept": "@x is derived.\n",
    "plain_reject": "@x is  derived.\n",
    "no_accept": "no item is base.\n",
    "every_accept": "every item a that is derived, (a is base).\n",
    "iff_accept": "(@x is base) iff (@x is derived).\n",
    "define_accept": "define derived(a) as (a is base).\n@x is derived.\n",
    "define_reject": "define derived(a) as (true).\n",
}


def schedstat(pid: int) -> tuple[int, int]:
    run, wait, _ = Path(f"/proc/{pid}/schedstat").read_text().split()
    return int(run), int(wait)


def percentiles(walls: list[float]) -> dict:
    walls = sorted(walls)
    return {"wall_p50_ms": round(statistics.median(walls), 3), "wall_p95_ms": round(walls[int(0.95 * len(walls)) - 1], 3)}


def service_sample(service: LeanService, case: dict, count: int = 100) -> dict:
    for _ in range(10):
        service.run("parse", [case])
    walls = []
    before = schedstat(service.pid)
    for _ in range(count):
        start = time.perf_counter_ns()
        service.run("parse", [case])
        walls.append((time.perf_counter_ns() - start) / 1_000_000)
    after = schedstat(service.pid)
    return {"calls": count, "case_sha256": hashlib.sha256(json.dumps(case, sort_keys=True).encode()).hexdigest(),
            **percentiles(walls),
            "service_cpu_ms_per_call": round((after[0] - before[0]) / count / 1_000_000, 3),
            "runqueue_wait_ms_per_call": round((after[1] - before[1]) / count / 1_000_000, 3)}


def public_sample(env: Environment, source: str, count: int = 100) -> dict:
    def call():
        try:
            parse(env, source)
            return "accepted"
        except VEError as exc:
            return exc.code
    answer = call()
    walls = []
    for _ in range(count):
        start = time.perf_counter_ns()
        call()
        walls.append((time.perf_counter_ns() - start) / 1_000_000)
    return {"calls": count, "answer": answer, **percentiles(walls)}


def main() -> None:
    os.environ.pop("VE_AUTHORITY", None)
    raw = pm.raw_environment(("definitions@0",))
    env = Environment(raw)
    with LeanService() as service:
        rows = {name: service_sample(service, {"id": "latency-parse", "environment": raw, "source": source})
                for name, source in SOURCES.items()}
    public = {name: public_sample(env, source) for name, source in SOURCES.items()}
    print(json.dumps({"load": round(os.getloadavg()[0], 2), "service": rows, "public_parse": public}, indent=2))


if __name__ == "__main__":
    main()
