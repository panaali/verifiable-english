"""One side of kb-10c's paired wall-time run of a safety-framework harness's `--check`.

usage: pair.py <before|after> <harness>   (from the worktree root; prints one JSON line)

`after` is the harness as committed: its conflicts go through `ve.soft_route.decide_soft_conflict` (Lean's soft
route). `before` runs the same harness with that one call put back to what it replaced,
`ve.norms.check_conflict(doc.elaborated, ...)` (Python's retained path); nothing else differs. Each side records
its harness wall time and the conflict calls' wall time; `after` also records, for each conflict call that asks Lean
(its soft relays: `soft-elaborate` and `soft-conflict`), the relays' wall time and the Lean service CPU they used
(user + system of this process's child processes, from /proc): the figures standing ruling R4 reads (at most 1 s
Lean CPU and 2 s wall per document check).
"""
import importlib.util
import json
import os
import sys
import time

mode, name = sys.argv[1], sys.argv[2]
root = os.getcwd()
sys.path.insert(0, root)
from ve import norms, soft_route  # noqa: E402


def service_cpu():
    total, me = 0, str(os.getpid())
    for pid in os.listdir("/proc"):
        if pid.isdigit():
            try:
                fields = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()
            except OSError:
                continue
            if fields[1] == me:
                total += int(fields[11]) + int(fields[12])
    return total / os.sysconf("SC_CLK_TCK")


relay, relays, current = soft_route._run, [], []


def timed_relay(request, *args, **kwargs):
    """Every soft relay made inside one conflict call is that call's Lean work (its `soft-elaborate` and its
    `soft-conflict`)."""
    wall, cpu = time.monotonic(), service_cpu()
    try:
        return relay(request, *args, **kwargs)
    finally:
        if current:
            current[-1][0] += time.monotonic() - wall
            current[-1][1] += service_cpu() - cpu
            current[-1][2] += type(request) is dict and request.get("kind") == "soft-conflict"


soft_route._run = timed_relay
spec = importlib.util.spec_from_file_location(f"pair_{name.replace('-', '_')}", f"{root}/usecases/{name}/run.py")
module = importlib.util.module_from_spec(spec)
sys.path.insert(0, f"{root}/usecases/{name}")
spec.loader.exec_module(module)
decide, calls = module.decide_soft_conflict, []


def conflict(document, **options):
    started = time.monotonic()
    current.append([0.0, 0.0, 0])
    try:
        if mode == "before":
            return norms.check_conflict(document.elaborated, **options)
        return decide(document, **options)
    finally:
        calls.append(time.monotonic() - started)
        lean_wall, lean_cpu, conflicts = current.pop()
        if conflicts:
            relays.append((lean_wall, lean_cpu))


module.decide_soft_conflict = conflict
started = time.monotonic()
try:
    code = module.main(["--check"])
except SystemExit as stop:
    code = stop.code
wall = time.monotonic() - started
walls, cpus = [w for w, _ in relays], [c for _, c in relays]
print(json.dumps({"mode": mode, "harness": name, "rc": code or 0, "wall_s": round(wall, 1),
                  "conflict_calls": len(calls), "conflict_s": round(sum(calls), 1),
                  "checks_asking_lean": len(relays), "lean_s": round(sum(walls), 1),
                  "max_check_lean_wall_s": round(max(walls, default=0), 3),
                  "checks_over_1s_wall": sum(w > 1 for w in walls), "checks_over_2s_wall": sum(w > 2 for w in walls),
                  "lean_cpu_s": round(sum(cpus), 2), "max_check_lean_cpu_s": round(max(cpus, default=0), 3),
                  "checks_over_1s_cpu": sum(c > 1 for c in cpus)}))
