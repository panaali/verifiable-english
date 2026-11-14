"""Count soft-selected calls under any script run (runpy): usage count2.py <root> <script> [args]."""
import sys, time, json, runpy, collections
root, script, *args = sys.argv[1:]
sys.path.insert(0, root)
from ve import soft_route
orig = soft_route.selected_at; n = collections.Counter()
def wrapped(d, m, q):
    n["calls"] += 1; n["queries"] += len(q); return orig(d, m, q)
soft_route.selected_at = wrapped
sys.argv = [script, *args]; s = time.monotonic(); rc = 0
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit as e:
    rc = e.code
print(json.dumps({"rc": rc, "wall": round(time.monotonic() - s, 1), **n}))
