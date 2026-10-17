import json, sys, collections, difflib
from pathlib import Path
a, b = Path(sys.argv[1]), Path(sys.argv[2])
def load(d):
    out = collections.defaultdict(list)
    for p in d.glob("dump-*.jsonl"):
        for l in p.open():
            r = json.loads(l); out[r["k"]].append(r)
    return out
A, B = load(a), load(b)
shown = collections.Counter()
for k, rs in B.items():
    if k not in A: continue
    ra = {x["raw"] for x in A[k]}
    for r in rs:
        if r["raw"] not in ra:
            f = r["t"].split("::")[0]
            shown[f] += 1
            if shown[f] <= 2:
                x, y = sorted(ra)[0], r["raw"]
                i = next((i for i in range(min(len(x), len(y))) if x[i] != y[i]), None)
                print("==", r["t"], "len", len(x), len(y), "first diff at", i)
                if i is not None: print("  A:", x[max(0,i-150):i+150]); print("  B:", y[max(0,i-150):i+150])
print(shown)
