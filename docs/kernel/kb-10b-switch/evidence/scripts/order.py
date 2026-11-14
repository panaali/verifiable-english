"""The (document, model) pairs of a harness --check run in first-question order (the order the kb-10b switch sends
its soft-selected calls), recorded on the base code by kb-10b step (1)'s shadow wrappers (no Lean comparison).
usage (from the base worktree): order.py <harness> <out.json>"""
import sys, json, time
sys.path.insert(0, "."); sys.path.insert(0, "usecases")
import safetyfw_shadow as S
name, out = sys.argv[1:3]
spec = dict(S.HARNESSES[name]); harness = S.load(name); shadow = S.Shadow()
contexts = dict(spec["contexts"]); contexts.pop("progress", None); spec["contexts"] = contexts
s = time.monotonic()
with S.installed(shadow, harness, spec):
    try:
        rc = harness.main(spec["args"])
    except SystemExit as e:
        rc = e.code
pairs = list(shadow.groups())
json.dump({"harness": name, "rc": rc, "seconds": round(time.monotonic() - s, 1), "calls": len(shadow.calls),
           "documents": len(shadow.documents), "pairs": len(pairs), "order": [d for d, _ in pairs]}, open(out, "w"))
print(name, rc, len(shadow.calls), "calls", len(pairs), "pairs", len(shadow.documents), "documents")
