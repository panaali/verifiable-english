"""After the vocabulary change: every unit of the previous parts (kept in /tmp copies or previous-*/ ) still loads with the same status and
meaning id, except the units this run changed (repair13_specs.ORDER). Foreground. Writes unit-compare.json.

    uv run --frozen python usecases/udhr-pilot/run-20261014T1800Z/compare_units.py <dir of the previous parts>
"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[2]))
import repair13_specs as R
from ve.document import load_document

old_dir = Path(sys.argv[1])
def front(path):
    return json.loads(Path(path).read_bytes().split(b"---\n", 2)[1])


out = {"changed_expected": R.ORDER, "units": 0, "differences": [], "environment_changed_in": [],
       "note": "a unit's meaning id includes its environment's id, so every unit of a part whose vocabulary changed gets a new meaning id; "
               "what is compared is the status and the unit's own row (kind, meaning, content, span) in the part file"}
for n in range(1, 5):
    name = f"translation-part0{n}.ve.md"
    old, new = load_document(old_dir / name), load_document(HERE / name)
    o = {u["id"]: (u["status"], u.get("meaning_id")) for u in old["units"]}
    w = {u["id"]: (u["status"], u.get("meaning_id")) for u in new["units"]}
    assert list(o) == list(w), name
    fo, fn = front(old_dir / name), front(HERE / name)
    ro = {u["id"]: u for u in fo["units"]}
    rn = {u["id"]: u for u in fn["units"]}
    if fo["environment"] != fn["environment"]:
        out["environment_changed_in"].append(name)
    for uid in o:
        out["units"] += 1
        if o[uid][0] != w[uid][0] or ro[uid] != rn[uid]:
            out["differences"].append({"unit": uid, "part": name, "before": o[uid][0], "after": w[uid][0], "row_changed": ro[uid] != rn[uid],
                                       "expected": uid in R.ORDER})
unexpected = [d for d in out["differences"] if not d["expected"]]
out["unexpected"] = unexpected
(HERE / "unit-compare.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
