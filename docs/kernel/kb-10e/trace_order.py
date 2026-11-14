"""Trace the order of Lean soft-selected calls a harness would make (kb-10e registrations estimate)."""
import importlib.util, json, sys, time
from pathlib import Path
WT = Path("/home/seyran/code/ve-kb-10e")
sys.path.insert(0, str(WT))
spec = importlib.util.spec_from_file_location("kb10e_shadow", "/tmp/kb10e-trace/kb10e_shadow.py")
s = importlib.util.module_from_spec(spec); sys.modules["kb10e_shadow"] = s; spec.loader.exec_module(s)
s.ROOT = WT
name, out = sys.argv[1], sys.argv[2]
def compare(self, *, ask=None):
    order = list(self.groups())  # (document, model) in first-call order
    sizes = {}
    for d, (doc, _) in self.documents.items():
        text = json.dumps({"environment": doc.env.to_dict(), "norms": [r.to_dict() for r in doc.rules]},
                          ensure_ascii=False, separators=(",", ":"))
        sizes[d] = len(text.encode())
    calls = [(c[1], c[2]) for c in self.calls]
    return {"pairs": order, "sizes": sizes, "calls": calls}
s.Shadow.compare = compare
t = time.monotonic()
report = s.shadow_run(name)
report["trace_seconds"] = round(time.monotonic() - t, 1)
Path(out).write_text(json.dumps(report))
print(name, report["harness_outcome"], len(report["pairs"]), "pairs", len(report["sizes"]), "documents", len(report["calls"]), "calls")
