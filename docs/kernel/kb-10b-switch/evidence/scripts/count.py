"""Count soft-selected calls under one harness run: calls, queries, Lean seconds, distinct documents and pairs."""
import sys, time, json, hashlib, importlib.util, collections
root, name = sys.argv[1], sys.argv[2]
sys.path.insert(0, root)
from ve import soft_route
orig = soft_route.selected_at
stats = collections.Counter(); docs = set(); pairs = collections.Counter(); objs = set(); t = [0.0]
def wrapped(d, m, q):
    s = time.monotonic()
    try:
        return orig(d, m, q)
    finally:
        t[0] += time.monotonic() - s
        stats["calls"] += 1; stats["queries"] += len(q)
        dk = hashlib.sha256(json.dumps([d.env.to_dict(), [r.to_dict() for r in d.rules]], sort_keys=True).encode()).hexdigest()
        mk = hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()
        docs.add(dk); objs.add(id(d)); pairs[(dk, mk)] += 1
soft_route.selected_at = wrapped
path = f"{root}/usecases/{name}/run.py"
spec = importlib.util.spec_from_file_location("h", path); mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, f"{root}/usecases/{name}"); spec.loader.exec_module(mod)
s = time.monotonic()
try:
    rc = mod.main(["--check"])
except SystemExit as e:
    rc = e.code
print(json.dumps({"rc": rc, "wall": round(time.monotonic() - s, 1), "lean_s": round(t[0], 1), **stats,
                  "documents": len(docs), "document_objects": len(objs), "pairs": len(pairs),
                  "pairs_asked_more_than_once": sum(1 for v in pairs.values() if v > 1)}))
