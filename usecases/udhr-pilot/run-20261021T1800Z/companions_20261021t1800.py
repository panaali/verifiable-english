"""Companion documents and status witnesses for u048's two readings (run 20261021T1800Z); the old `u048.entitlement` companion is removed.

    uv run --frozen python usecases/udhr-pilot/run-20261021T1800Z/companions_20261021t1800.py
"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[2]))
import repair_specs as RS
import repair_20261021t1800 as R
import udhr_specs as U
import witnesses_nd as WND
from ve.document import check_document, coverage, load_document

READINGS = HERE / "readings"
meta, _ = R.read(HERE / "translation-part02.ve.md")
raw = (HERE.parent / "source" / "udhr.md").read_bytes()
a, b = next(u for u in json.loads(Path(HERE / "units.json").read_text())["units"] if u["id"] == "u048")["span"]
old = READINGS / "u048.entitlement.ve.md"
if old.exists():
    old.unlink()
wit = json.loads((HERE / "witnesses.json").read_text())
chk = json.loads((HERE / "companions-check.json").read_text())
wit["norm_defaults_status"].pop("u048.entitlement", None); chk.pop("u048.entitlement", None)
for cid, stem in R.CANDIDATES:
    pred = R.PREDICATES[stem]
    spec = RS.entitlement("u048", cid, stem, pred["verbalisation"], pred["description"], [])
    path = U.write_companion(READINGS, "u048", cid, spec, raw[a:b], meta["open_terms"])
    rep = check_document(path)
    assert rep["premises"]["status"] == "model", rep["premises"]
    outs = WND.run(path, spec)
    assert all(o["as_expected"] for o in outs), outs
    wit["norm_defaults_status"][f"u048.{cid}"] = outs
    doc = load_document(path)
    chk[f"u048.{cid}"] = {"coverage_bytes": coverage(doc)["bytes_by_status"], "path": f"readings/u048.{cid}.ve.md", "premises": rep["premises"]["status"],
                          "profiles": json.loads(path.read_bytes().split(b"---\n", 2)[1])["environment"]["profiles"]}
    print(cid, "ok", outs[0]["lean_point_status"], flush=True)
wit["norm_defaults_status"] = dict(sorted(wit["norm_defaults_status"].items())); chk = dict(sorted(chk.items()))
(HERE / "witnesses.json").write_text(json.dumps(wit, indent=1)); (HERE / "companions-check.json").write_text(json.dumps(chk, indent=1))
