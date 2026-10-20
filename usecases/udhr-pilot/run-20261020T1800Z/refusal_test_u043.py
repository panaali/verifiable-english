"""u043's reading set is held by Lean, not by this script: a wrong separating situation is refused at load (foreground; scratch files under a temp dir).

(a) the situation's recorded value is flipped; (b) the existential reading is replaced by a copy of the universal one (the two no longer differ),
so the recorded situation cannot separate them.  Writes refusal-test-u043.json.
"""
import json, sys, copy, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[2])); sys.path.insert(0, str(HERE.parents[2] / "tools"))
import readings_s1_pilot as P
import vocab_patch as V
from tests.test_readings_s1_lean import situation_id
from ve.document import load_document
from ve.errors import VEError

meta, src = P.read(HERE / "translation-part01.ve.md")
scratch = Path(tempfile.mkdtemp(prefix="udhr-refusal-u043-"))


def attempt(name, m, expect_refusal=True):
    path = scratch / f"{name}.ve.md"
    P.write(path, m, src)
    try:
        load_document(path)
        return "admitted" if not expect_refusal else "ADMITTED (unexpected)"
    except VEError as e:
        return f"refused: {getattr(e, 'message', None) or e}"[:300]


item = next(s for s in meta["reading_sets"] if s["unit"] == "u043")
sid, entry = next(iter(item["situations"].items()))
assert situation_id(meta["environment"], entry) == sid
out = {"control_unchanged_loads": attempt("control", meta, expect_refusal=False)}
# (a) flipped value
m = copy.deepcopy(meta)
bad = copy.deepcopy(entry); bad["value"] = not bad["value"]
new = situation_id(m["environment"], bad)
it = next(s for s in m["reading_sets"] if s["unit"] == "u043")
it["situations"] = {new: bad}
for r in it["readings"]:
    r["admission"]["distinguishing_models"] = {o: new for o in r["admission"]["distinguishing_models"]}
out["a_flipped_value"] = attempt("flipped", m)
# (b) the two readings made equal
m = copy.deepcopy(meta)
it = next(s for s in m["reading_sets"] if s["unit"] == "u043")
it["readings"][1]["content"] = copy.deepcopy(it["readings"][0]["content"])
it["readings"][1]["content"]["norm"]["name"] = "u043-existential"
it["readings"] = V.reidentified(m["environment"], [it], {}, {}, [], [])[0]["readings"]
out["b_readings_equal"] = attempt("equal", m)
print(json.dumps(out, indent=1))
(HERE / "refusal-test-u043.json").write_text(json.dumps(out, indent=1) + "\n")
