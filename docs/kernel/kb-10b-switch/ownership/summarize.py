"""Summarize the per-item ownership trace (run_all.sh) into per-item.tsv and called-from.json, and print the
criterion-1 (no Python decision call) and agreement counts by family.
usage: summarize.py <items dir> <out dir>   (items in the RSP key's order, from <items dir>/../ids.txt)"""
import json
import sys
from collections import Counter
from pathlib import Path

items, out = Path(sys.argv[1]), Path(sys.argv[2])
ids = (items.parent / "ids.txt").read_text().split()
rows, called, clean, agree, total, errors = [], {}, Counter(), Counter(), Counter(), []
for item in ids:
    d = json.loads((items / (item.replace("/", "_") + ".json")).read_text())
    family = d["family"]
    total[family] += 1
    if d["error"]:
        errors.append((item, d["error"]))
    calls = d["python_decision_calls"]
    on_path = any(f in d["functions"] for f in ("softnorms.py:selected_at", "soft_route.py:selected_at"))
    rows.append("\t".join([item, json.dumps(d["verdict"]), json.dumps(d["key"]), str(d["agree"]), ";".join(calls),
                           str(d["route"]), str(on_path)]))
    if calls:
        called[item] = d["called_from"]
    clean[family] += not calls
    agree[family] += bool(d["agree"])
(out / "per-item.tsv").write_text("id\tverdict\tkey\tagree\tpython_decision_calls\troute\tsoft_selected_on_path\n"
                                  + "\n".join(sorted(rows)) + "\n")
(out / "called-from.json").write_text(json.dumps(dict(sorted(called.items())), indent=1) + "\n")
for family in total:
    print(family, total[family], "clean", clean[family], "agree", agree[family])
print("total", sum(total.values()), "clean", sum(clean.values()), "agree", sum(agree.values()), "errors", errors)
