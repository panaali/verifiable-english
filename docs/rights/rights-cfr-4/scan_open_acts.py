"""rights-cfr-4 evidence: the rights@0 documents with declared open_terms under the given roots, and every unit content
whose predicate (or fan-out predicate) is one of them (the only units the act scan can move). Usage:
uv run python docs/rights/rights-cfr-4/scan_open_acts.py tests conformance usecases docs examples experiments"""
import json, os, re, sys
hits, docs, paths = [], 0, []
def acts(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "predicate" and isinstance(v, str): out.add(v)
            if k == "fan_out" and isinstance(v, dict):
                for x in v.values():
                    if isinstance(x, str): out.add(x)
            acts(v, out)
    elif isinstance(obj, list):
        for v in obj: acts(v, out)
def front(text):
    if text.startswith("---\n"):
        try: return json.loads(text[4:text.index("\n---\n", 4)])
        except Exception: return None
    try: return json.loads(text)
    except Exception: return None
for root in sys.argv[1:]:
    for dp, dn, fn in os.walk(root):
        if ".lake" in dp or "node_modules" in dp or "/target" in dp: continue
        for f in fn:
            if not (f.endswith(".md") or f.endswith(".json")): continue
            p = os.path.join(dp, f)
            try:
                if os.path.getsize(p) > 50_000_000: continue
                t = open(p, encoding="utf-8").read()
            except Exception: continue
            if "rights@0" not in t or "open_terms" not in t: continue
            m = front(t)
            if not isinstance(m, dict): continue
            ots = m.get("open_terms") or []
            names = {o.get("name") for o in ots if isinstance(o, dict)}
            if not names: continue
            docs += 1
            paths.append(p)
            for u in m.get("units", []):
                for part in [u] + (u.get("parts") or []):
                    c = part.get("content")
                    if not isinstance(c, dict): continue
                    a = set(); acts(c, a)
                    if a & names: hits.append((p, part.get("id"), sorted(a & names)))
print("docs with rights@0 and open_terms:", docs)
for q in sorted(paths): print(" ", q)
print("units whose act is a declared open term:", len(hits))
for h in hits: print(h)
