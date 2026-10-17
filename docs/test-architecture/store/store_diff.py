import json, sys, collections
from pathlib import Path
a, b = Path(sys.argv[1]), Path(sys.argv[2])
def recs(d):
    for p in sorted(d.glob("*.jsonl")):
        for l in p.open():
            if l.strip():
                r = json.loads(l)
                if "r" in r and not r["el"]:
                    yield r
first = {}
for r in recs(a):
    first.setdefault(r["k"], []).append(r)
diff = []
within = collections.Counter()
for k, rs in first.items():
    if len({x["r"] for x in rs}) > 1:
        within[(rs[0]["t"].split("::")[0], rs[0]["m"], rs[0]["sc"])] += 1
for r in recs(b):
    if r["k"] in first:
        rr = {x["r"] for x in first[r["k"]]}
        if r["r"] not in rr:
            diff.append((r, first[r["k"]][0]))
c = collections.Counter((r["t"].split("::")[0], r["m"], r["sc"], r["err"], o["err"]) for r, o in diff)
print("cross-run diffs", len(diff))
for k, v in c.most_common(30): print(v, k)
print("within-run1 same key different responses", sum(within.values()))
for k, v in within.most_common(20): print(v, k)
