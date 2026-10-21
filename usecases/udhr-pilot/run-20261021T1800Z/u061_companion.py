"""Write and check u061's companion for run 20261021T0600Z (foreground)."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[2])); sys.path.insert(0, str(HERE.parents[2] / "tools"))
import json, hashlib
import udhr_specs as U, u061_specs as S, witnesses_nd as WND
from ve.document import check_document, load_document
import readings_s1_pilot as P

raw = (HERE.parent / "source" / "udhr.md").read_bytes()
legacy, lsrc = P.read(HERE / "translation.ve.md")
lu = next(u for u in legacy["units"] if u["id"] == "u061")
a, b = lu["span"]
path = U.write_companion(HERE / "readings", "u061", "entitlement", S.SPEC, raw[a:b], legacy["open_terms"])
v = check_document(path)
print(path.name, v["premises"]["status"], flush=True)
outs = WND.run(path, S.SPEC)
print([(o["row"], o["status"], o["as_expected"]) for o in outs])
print("meaning_id", load_document(path)["units"][0]["meaning_id"])
