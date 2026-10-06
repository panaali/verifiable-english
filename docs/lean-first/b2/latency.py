"""Per-call latency at the base and the head of lean-first batch 2 (F2 handles, F6 the persistent Rust checker).

    uv run --frozen --project ROOT python docs/lean-first/b2/latency.py ROOT    # once per checkout

One warm service; the agent-policy environment (the one its harness's typing, evaluation and Background calls
carry). Lean CPU per call is read from /proc/<pid>/schedstat; wall is the client's. The Rust rows time
`rust_jsonl.run` of a typing case: a process per call at the base, one persistent process at the head.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
CALLS = 500


def cpu(pid):
    return int(Path(f"/proc/{pid}/schedstat").read_text().split()[0]) / 1e9


def median(values):
    return sorted(values)[len(values) // 2]


def main():
    from ve.backends import rust_jsonl
    from ve.backends.lean_service import LeanService
    from ve.environment import Environment
    env = Environment(json.loads((ROOT / "usecases/agent-policy/environment.lean.json").read_text()))
    policy = env.to_dict()
    rows = {}
    with LeanService(timeout=600) as service:
        for label, mode, case in (("check top", "check", {"id": "x", "environment": policy, "ast": [["top"]]}),
                                  ("environment", "environment", {"id": "x", "environment": policy})):
            service.run(mode, [case])
            cpus, walls = [], []
            for _ in range(CALLS):
                before, started = cpu(service.pid), time.perf_counter()
                service.run(mode, [case])
                walls.append(time.perf_counter() - started)
                cpus.append(cpu(service.pid) - before)
            cases = [dict(case, id=f"t{n}") for n in range(300)]
            before, started = cpu(service.pid), time.perf_counter()
            service.run(mode, cases)
            wall, used = time.perf_counter() - started, cpu(service.pid) - before
            rows[label] = {"lean_cpu_p50_ms": round(median(cpus) * 1000, 3), "wall_p50_ms": round(median(walls) * 1000, 3),
                           "batched_300_lean_cpu_per_case_ms": round(used / 300 * 1000, 3),
                           "batched_300_wall_per_case_ms": round(wall / 300 * 1000, 3)}
    case = {"id": "typing", "kind": "check", "environment": rust_jsonl.rust_environment(env), "ast": [["top"]]}
    rust_jsonl.run(case, timeout=600)
    walls = []
    for _ in range(CALLS):
        started = time.perf_counter()
        rust_jsonl.run(case, timeout=600)
        walls.append(time.perf_counter() - started)
    rows["rust typing call"] = {"wall_p50_ms": round(median(walls) * 1000, 3)}
    print(json.dumps({"root": str(ROOT), "load": Path("/proc/loadavg").read_text().split()[0], "rows": rows}))


if __name__ == "__main__":
    main()
