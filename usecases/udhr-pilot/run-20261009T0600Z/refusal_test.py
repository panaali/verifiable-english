"""A deliberately wrong separating situation is refused by Lean at load time (part07)."""
import json, sys, copy
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[2])); sys.path.insert(0, str(HERE.parents[2] / "tools"))
import readings_s1_pilot as P
from tests.test_readings_s1_lean import situation_id
from ve.document import load_document
from ve.errors import VEError

meta, src = P.read(HERE / "translation-part07.ve.md")
item = next(s for s in meta["reading_sets"] if s.get("situations"))
sid, entry = next(iter(item["situations"].items()))
assert situation_id(meta["environment"], entry) == sid
bad = copy.deepcopy(entry); bad["value"] = not bad["value"]          # the probe's value no longer separates the pair
new = situation_id(meta["environment"], bad)
text = json.dumps({"s": item["situations"], "r": [r["admission"]["distinguishing_models"] for r in item["readings"]]})
bad_item = json.loads(json.dumps(item).replace(sid, new))
bad_item["situations"] = {new if k == sid else k: (bad if k == sid else v) for k, v in item["situations"].items()}
meta["reading_sets"] = [bad_item if s["id"] == item["id"] else s for s in meta["reading_sets"]]
P.write("/tmp/exp/bad-part07.ve.md", meta, src)
try:
    load_document("/tmp/exp/bad-part07.ve.md"); result = "ADMITTED (unexpected)"
except VEError as e:
    result = f"refused: {e}"
print(item["id"], result)
(HERE / "refusal-test.json").write_text(json.dumps({"set": item["id"], "result": result}))
