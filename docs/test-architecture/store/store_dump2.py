import json, sys, collections
from pathlib import Path
for d in map(Path, sys.argv[1:]):
    out = collections.defaultdict(list)
    for p in d.glob("dump-*.jsonl"):
        for l in p.open():
            r = json.loads(l); out[r["k"]].append(r)
    n = 0
    for k, rs in out.items():
        raws = sorted({x["raw"] for x in rs})
        if len(raws) > 1:
            n += 1
            if n <= 3:
                x, y = raws[0], raws[1]
                i = next((i for i in range(min(len(x), len(y))) if x[i] != y[i]), None)
                print("==", d.name, rs[0]["t"], len(rs), "copies", len(raws), "variants; first diff at", i, "line", rs[0]["line"][:200])
                print("  A:", x[max(0,i-200):i+200]); print("  B:", y[max(0,i-200):i+200])
    print(d.name, "keys with >1 response:", n)
