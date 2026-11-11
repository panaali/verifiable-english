"""Run a use-case harness and record which Lean service modes and case kinds it asks for.
usage: python tools/kernel_trace.py <out.json> <script.py> [args...]   (measurement aid; changes no product code)"""
import collections, json, runpy, sys, time
out, script, *rest = sys.argv[1:]
from ve.backends import lean_service, lean
calls = collections.Counter(); secs = collections.Counter(); verdicts = collections.Counter()
orig = lean_service.LeanServicePool.run_bound
def run_bound(self, mode, cases, **kw):
    t = time.monotonic()
    try:
        return orig(self, mode, cases, **kw)
    finally:
        dt = time.monotonic() - t
        for c in cases:
            k = c.get("kind") if isinstance(c, dict) else None
            calls[f"{mode}|{k}"] += 1
        secs[mode] += dt
lean_service.LeanServicePool.run_bound = run_bound
orig_run = lean.run
def run(operation, executable, cases, **kw):
    t = time.monotonic()
    try:
        return orig_run(operation, executable, cases, **kw)
    finally:
        calls[f"oneshot:{operation}|{kw.get('mode','')}"] += len(cases); secs[f"oneshot:{operation}"] += time.monotonic() - t
lean.run = run
sys.argv = [script, *rest]
t0 = time.monotonic(); rc = 0
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit as e:
    rc = e.code
finally:
    json.dump({"script": script, "args": rest, "rc": rc, "wall_s": round(time.monotonic() - t0, 1),
               "calls": dict(sorted(calls.items())), "seconds_by_mode": {k: round(v, 1) for k, v in sorted(secs.items())}},
              open(out, "w"), indent=1)
