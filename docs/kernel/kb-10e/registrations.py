import json, sys
from collections import OrderedDict
r = json.load(open(sys.argv[1]))
sizes = r["sizes"]; pairs = [p[0] for p in r["pairs"]]; calls = [c[0] for c in r["calls"]]
MB = 67108864
def empty_rule(seq, n=64, mb=MB):
    held, b, regs, empt = set(), 0, 0, 0
    for d in seq:
        if d in held: continue
        if len(held) + 1 > n or b + sizes[d] > mb: held, b, empt = set(), 0, empt + 1
        held.add(d); b += sizes[d]; regs += 1
    return regs, empt
def lru(seq, n=64, mb=MB):
    held, b, regs = OrderedDict(), 0, 0
    for d in seq:
        if d in held: held.move_to_end(d); continue
        while held and (len(held) + 1 > n or b + sizes[d] > mb):
            _, s = held.popitem(last=False); b -= s
        held[d] = sizes[d]; b += sizes[d]; regs += 1
    return regs
docs = len(sizes)
sz = sorted(sizes.values())
print(f"documents {docs}, text bytes median {sz[len(sz)//2]}, max {sz[-1]}, total {sum(sz)}")
# runs: how many times the document changes in pair order
for name, seq in (("pair order (one Lean call per document and model)", pairs), ("call order (one Lean call per harness call)", calls)):
    switches = sum(1 for a, b in zip(seq, seq[1:]) if a != b) + 1
    print(f"\n{name}: {len(seq)} asks, {switches} runs of one document")
    for n in (64, 128, 256, 1024):
        regs, e = empty_rule(seq, n)
        print(f"  empty-when-full, bound {n}: {regs} registrations ({regs/docs:.2f} per document), emptied {e} times")
    for n in (64, 128, 256):
        regs = lru(seq, n)
        print(f"  evict least recently used, bound {n}: {regs} registrations ({regs/docs:.2f} per document)")
