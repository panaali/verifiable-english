"""The ruling's split of a harness --check run: Lean time of each document's first soft-selected call, of later
calls, and the rest (Python and other Lean kinds). usage: split.py <root> <harness>"""
import sys, time, json, hashlib, importlib.util
root, name = sys.argv[1], sys.argv[2]
sys.path.insert(0, root)
from ve import soft_route
orig = soft_route.selected_at; seen = set(); acc = {"first": [0, 0.0], "later": [0, 0.0]}; each = []
def wrapped(d, m, q):
    k = hashlib.sha256(json.dumps([d.env.to_dict(), [r.to_dict() for r in d.rules]], sort_keys=True).encode()).hexdigest()
    kind = "later" if k in seen else "first"; seen.add(k)
    s = time.monotonic()
    try:
        return orig(d, m, q)
    finally:
        acc[kind][0] += 1; acc[kind][1] += time.monotonic() - s; each.append(time.monotonic() - s)
soft_route.selected_at = wrapped


def service_cpu():
    """CPU seconds (user + system) of this process's child processes (the Lean services), from /proc."""
    import os
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


cpu = []
_timed = wrapped


def wrapped(d, m, q):  # noqa: F811  (the Lean CPU of each call too)
    before = service_cpu()
    try:
        return _timed(d, m, q)
    finally:
        cpu.append(service_cpu() - before)
soft_route.selected_at = wrapped
spec = importlib.util.spec_from_file_location("h", f"{root}/usecases/{name}/run.py"); mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, f"{root}/usecases/{name}"); spec.loader.exec_module(mod)
s = time.monotonic(); rc = mod.main(["--check"]); wall = time.monotonic() - s
lean = acc["first"][1] + acc["later"][1]
print(json.dumps({"harness": name, "rc": rc, "wall": round(wall, 1),
                  "first_calls": acc["first"][0], "first_s": round(acc["first"][1], 1),
                  "later_calls": acc["later"][0], "later_s": round(acc["later"][1], 1),
                  "rest_s": round(wall - lean, 1), "max_call_s": round(max(each, default=0), 3),
                  "calls_over_1s": sum(x > 1 for x in each), "calls_over_2s": sum(x > 2 for x in each),
                  "lean_cpu_s": round(sum(cpu), 1), "max_call_cpu_s": round(max(cpu, default=0), 3),
                  "calls_over_1s_cpu": sum(x > 1 for x in cpu)}))
