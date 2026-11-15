"""Registrations a run makes under Protocol.lean's handle table (Handles.insert: at most maxHandles entries, emptied
first when one more would exceed it), from the soft-selected call order (order.py); and under other rules for comparison.
usage: handles.py <order.json>"""
import json, sys
from collections import OrderedDict
d = json.load(open(sys.argv[1])); order = d["order"]; docs = len(set(order))
def emptied(bound):
    table, n = set(), 0
    for doc in order:
        if doc not in table:
            if len(table) + 1 > bound:
                table = set()
            table.add(doc); n += 1
    return n
def lru(bound):
    table, n = OrderedDict(), 0
    for doc in order:
        if doc in table:
            table.move_to_end(doc)
        else:
            n += 1; table[doc] = True
            if len(table) > bound:
                table.popitem(last=False)
    return n
runs = sum(1 for i, doc in enumerate(order) if i == 0 or order[i - 1] != doc)
print(json.dumps({"harness": d["harness"], "calls": len(order), "documents": docs, "runs_of_one_document": runs}))
for bound in (64, 128, 256, 512, 1024, 2048):
    e, l = emptied(bound), lru(bound)
    print(json.dumps({"bound": bound, "emptied_when_full": e, "per_document": round(e / docs, 2),
                      "lru": l, "lru_per_document": round(l / docs, 2)}))
