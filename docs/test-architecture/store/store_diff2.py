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
first = collections.defaultdict(list)
for r in recs(a): first[r["k"]].append(r)
c = collections.Counter(); ex = {}
for r in recs(b):
    rs = first.get(r["k"])
    if rs and r["r"] not in {x["r"] for x in rs}:
        o = rs[0]
        key = (r["t"].split("::")[0], r["m"], r["sc"], r.get("p"), (r.get("e") or "")[:90], (o.get("e") or "")[:90])
        c[key] += 1
print("cross-run diffs", sum(c.values()))
for k, v in c.most_common(40): print(v, k)
w = collections.Counter()
for k, rs in first.items():
    if len({x["r"] for x in rs}) > 1:
        w[(rs[0]["t"].split("::")[0], rs[0]["m"], rs[0]["sc"], rs[0].get("p"), tuple(sorted({(x.get("e") or "")[:70] for x in rs})))] += 1
print("within-run", sum(w.values()))
for k, v in w.most_common(20): print(v, k)
pat = collections.Counter((r["t"].split("::")[0], r.get("p")) for r in recs(b) if r.get("p"))
print("patched", pat.most_common(30))
