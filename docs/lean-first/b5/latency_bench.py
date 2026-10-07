"""Time 100 accepted alternatives and risk envelope decodes in one process.

Run from each checkout with its locked Python environment. CPU is the client
process only; the wall reading includes the Lean service and host load.
"""
import json
import runpy
import sys
import time

from ve.environment import Environment
from ve.backends import relay

sys.path.insert(0, "tests")


def lean_cpu():
    pool = relay._pool
    return sum(service.cpu_seconds() or 0.0 for service in pool.services) if pool else 0.0

for name, source in (
    ("alternatives", runpy.run_path("tests/test_alternatives_profile.py")["source"]()),
    ("risk", runpy.run_path("tests/test_risk_integration.py")["cell_env"]()),
):
    Environment(source)
    start = time.perf_counter()
    cpu_start = lean_cpu()
    for _ in range(100):
        Environment(source)
    print(json.dumps({"operation": name, "calls": 100,
                      "wall_seconds": round(time.perf_counter() - start, 3),
                      "lean_cpu_seconds": round(lean_cpu() - cpu_start, 3)}))
