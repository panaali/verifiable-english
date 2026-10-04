"""How much of a service call is the environment? (F2 and F3 in docs/LEAN-FIRST-PLAN.md section 4.)

    uv run --frozen python docs/lean-first/env_cost.py [--calls 300]

One warm service. The same trivial typing request (`check` of `top`) is sent one case per request with the
agent-policy environment (the one the harness's 23,000 typing calls carry) and with a minimal environment, then
as one batched request; the `environment` mode alone measures decoding the environment. Lean CPU per call is
read from /proc/<pid>/schedstat, so host load inflates it less than wall time.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _cpu(pid) -> float:
    return int(Path(f"/proc/{pid}/schedstat").read_text().split()[0]) / 1e9


def pct(values, q):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round(q * (len(ordered) - 1)))]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--calls", type=int, default=300)
    args = parser.parse_args()
    from ve.backends.lean_service import LeanService
    from ve.environment import Environment
    policy = Environment(json.loads((ROOT / "usecases/agent-policy/environment.lean.json").read_text())).to_dict()
    minimal = Environment({"language": policy["language"], "profiles": ["relational-fol@0"],
                           "spec_revision": policy["spec_revision"],
                           "vocabulary": {"sorts": {}, "constants": {}, "predicates": {}}}).to_dict()
    top = [["top"]]
    rows = []
    with LeanService(timeout=600) as service:
        def single(label, mode, case):
            service.run(mode, [case])  # warm
            walls, cpus = [], []
            for _ in range(args.calls):
                cpu, started = _cpu(service.pid), time.perf_counter()
                service.run(mode, [case])
                walls.append(time.perf_counter() - started)
                cpus.append(_cpu(service.pid) - cpu)
            rows.append({"what": label, "request_bytes": len(json.dumps(case, separators=(",", ":"))),
                         "wall_p50_ms": round(pct(walls, .5) * 1000, 2), "wall_p95_ms": round(pct(walls, .95) * 1000, 2),
                         "cpu_p50_ms": round(pct(cpus, .5) * 1000, 2), "cpu_p95_ms": round(pct(cpus, .95) * 1000, 2)})

        single("environment mode, agent-policy environment", "environment",
               {"id": "environment", "environment": policy})
        single("check top, agent-policy environment", "check", {"id": "typing", "environment": policy, "ast": top})
        single("check top, minimal environment", "check", {"id": "typing", "environment": minimal, "ast": top})
        cases = [{"id": f"t{n}", "environment": policy, "ast": top} for n in range(args.calls)]
        cpu, started = _cpu(service.pid), time.perf_counter()
        service.run("check", cases)
        wall, cpu = time.perf_counter() - started, _cpu(service.pid) - cpu
        rows.append({"what": f"check top, agent-policy environment, {args.calls} cases in one request",
                     "wall_per_case_ms": round(wall / args.calls * 1000, 2),
                     "cpu_per_case_ms": round(cpu / args.calls * 1000, 2)})
    print(json.dumps({"load": Path("/proc/loadavg").read_text().split()[0], "rows": rows}, indent=1))


if __name__ == "__main__":
    main()
