"""PART 1a probe: norms-elaborate cost by rule shape at 32 and 48 regulated (REPORT 1a). Run from the checkout root."""
import sys, json
sys.path.insert(0, "docs/translim/translim-predicates")
import cost_curve as C
from pathlib import Path
exe = Path(C.lean_service.DEFAULT_EXECUTABLE)
for n in (32, 48):
    env, reg = C.environment(n, C.NORMS)
    r = C.rules(reg, "flat")
    variants = {
      "no rules": {"kind": "norms-elaborate", "environment": env, "norms": []},
      "rules, guard top": {"kind": "norms-elaborate", "environment": env, "norms": [{"norm": {**x["norm"], "guard": ["top"]}} for x in r]},
      "rules, one guard pred": {"kind": "norms-elaborate", "environment": env, "norms": [{"norm": {**x["norm"], "guard": ["unary", "publicly_deployed", ["var", 0]]}} for x in r]},
      "flat (4 guard preds)": {"kind": "norms-elaborate", "environment": env, "norms": r},
      "half rules (obligations)": {"kind": "norms-elaborate", "environment": env, "norms": [x for x in r if x["norm"]["predicate"].endswith("_required")]},
    }
    small = json.loads(json.dumps(env)); small["vocabulary"]["predicates"] = {k: v for k, v in small["vocabulary"]["predicates"].items() if "regulated" in v or k in C.FRAME_GUARDS}
    variants["flat, frame cut to 4 preds"] = {"kind": "norms-elaborate", "environment": small, "norms": r}
    for label, case in variants.items():
        w, cpu, dl, a = C.timed("norms", case, exe)
        print(n, label.ljust(28), "wall %.2f" % w, "cpu", cpu, a[:40], flush=True)
