"""Review F8: the switch's soft-selected calls on a harness against the (document, model) pairs step (1)'s shadow
counts, in ONE run of the head code. usage: f8_pairs.py <harness> <out.json> (from the worktree root)

The shadow's recording wrappers (usecases/safetyfw_shadow.py `installed`) record each harness question by
(document, model) as step (1) did; a wrapper on `ve.softnorms.selected_at` (the relay the document calls) records
each call by the same two digests, its query count and the harness line it came from. No Lean comparison is run.
"""
import json
import sys
import traceback
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "usecases"))
import safetyfw_shadow as shadow_mod  # noqa: E402
from ve import softnorms  # noqa: E402

name, out = sys.argv[1], sys.argv[2]
spec = dict(shadow_mod.HARNESSES[name])
harness = shadow_mod.load(name)
shadow = shadow_mod.Shadow()
contexts = dict(spec["contexts"]); contexts.pop("progress", None); spec["contexts"] = contexts
calls = []
genuine = softnorms.selected_at


def recording(source, model, queries):
    document = shadow_mod._digest([source.env.to_dict(), [rule.to_dict() for rule in source.rules]])
    data = model.to_dict() if hasattr(model, "to_dict") else model
    frames = [f for f in traceback.extract_stack()[:-1] if "usecases" in f.filename]
    calls.append({"document": document, "model": shadow_mod._digest(data), "queries": len(queries),
                  "from": [f"{Path(f.filename).parent.name}/{Path(f.filename).name}:{f.name}:{f.lineno}"
                           for f in frames[-3:]]})
    return genuine(source, model, queries)


softnorms.selected_at = recording
with shadow_mod.installed(shadow, harness, spec):
    code = harness.main(spec["args"])
shadow_pairs = Counter((c[1], c[2]) for c in shadow.calls)
switch_pairs = Counter((c["document"], c["model"]) for c in calls)
extra = [c for c in calls if (c["document"], c["model"]) not in shadow_pairs]
repeated = [c for c in calls if switch_pairs[(c["document"], c["model"])] > 1]
report = {"harness": name, "exit": code, "switch_calls": len(calls), "switch_pairs": len(switch_pairs),
          "shadow_pairs": len(shadow_pairs), "shadow_questions": len(shadow.calls),
          "pairs_not_in_shadow": extra, "calls_of_repeated_pairs": repeated,
          "shadow_pairs_not_asked": len(set(shadow_pairs) - set(switch_pairs))}
Path(out).write_text(json.dumps(report, indent=1) + "\n")
print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in report.items()}))
