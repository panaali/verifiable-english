import json, sys, time
sys.path.insert(0, "/home/seyran/code/ve-udhr-20261021T1800Z")
from pathlib import Path
from ve.document import check_document, load_document, render_document
src = "1. Everyone has the right to take part in the government of his country, directly or through freely chosen representatives."
ACT = "{0} to take part in the government of his country directly or through freely chosen representatives"
meta = {"environment": {"language": "ve.core@0.2", "profiles": ["acts@0","documents@1","norm-defaults@0","norms@0","relational-fol@0"],
  "spec_revision": "ve-v0.2-expand2-2026-09-25",
  "vocabulary": {"constants": {}, "sorts": {"person": {"description": "a human person", "verbalisation": {"singular": "person", "plural": "people"}}},
    "predicates": {"has_the_right_to_take_part_in_government": {"arguments": ["person"], "description": "The person has the right to take part in the government of his country, directly or through freely chosen representatives",
       "regulated": {"role": "plain", "default": "unspecified", "act": ACT, "form": "has the right"}}},
    "acts": {"fixed": ["directly or through freely chosen representatives"]}}},
  "format": "ve-document@1", "open_terms": [],
  "units": [{"id": "u076", "kind": "norm", "meaning": "specified", "span": [0, len(src.encode())], "support": "none",
     "content": {"norm": {"guard": ["top"], "name": "u076-entitlement", "over": [], "predicate": "has_the_right_to_take_part_in_government", "sign": True, "unless": []}}}]}
p = Path("/tmp/udhr-ap1b/u076.ve.md")
p.write_bytes(b"---\n" + json.dumps(meta).encode() + b"\n---\n" + src.encode())
t = time.monotonic()
try:
    rep = check_document(p)
    print(json.dumps({k: v for k, v in rep.items() if k in ("coverage","premises")}, indent=1)[:2500])
    print(render_document(p))
except Exception as e:
    import traceback; traceback.print_exc()
    print("ERR", type(e).__name__, getattr(e, "message", e))
print(time.monotonic() - t)
