"""Re-check every companion document and its Lean status witnesses at this tag (foreground)."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[2]))
import companions_nd as ND, repair2_specs as R2, repair3_specs as R3, repair4_specs as R4, repair5_specs as R5, repair6_specs as R6
import repair_specs as RS, repair7_specs as R7, repair8_specs as R8, repair10_specs as R10, repair11_specs as R11, repair12_specs as R12, repair13_specs as R13, repair15_specs as R15, udhr_specs as U, witnesses_nd as WND
from ve.document import check_document, render_document

specs = {}
for uid, per in ND.SPECS.items():
    for cid, spec in per.items():
        specs[f"{uid}.{cid}"] = spec
for uid, cands in [*U.CANDIDATES.items(), *RS.CANDIDATES.items(), *R2.CANDIDATES.items(), *R3.NEW_CANDIDATES.items(),
                   *R4.NEW_CANDIDATES.items(), *R5.NEW_CANDIDATES.items(), *R6.NEW.items(), *R7.NEW.items(), *R10.NEW.items(), *R11.NEW.items(), *R12.NEW.items(), *[(u, [(c, sp, w)]) for u, (c, sp, w) in R13.NEW.items()], *R15.NEW.items(), *[("u020", [("prohibited", R8.U020, "")]), ("u098", [("unassigned", R8.U098, "")])]]:
    for cid, spec, _why in cands:
        specs[f"{uid}.{cid}"] = spec
docs, status, bad = {}, {}, []
for path in sorted((HERE / "readings").glob("*.ve.md")):
    key = ".".join(path.name.split(".")[:2])
    verdict = check_document(path)
    assert verdict["premises"]["status"] == "model", (path.name, verdict["premises"])
    spec = specs.get(key)
    if spec is None:
        bad.append(key); continue
    outs = WND.run(path, spec)
    assert all(o["as_expected"] for o in outs), (key, outs)
    status[key] = outs
    docs[key] = {"path": f"readings/{path.name}", "premises": verdict["premises"]["status"], "coverage_bytes": verdict["coverage"]["bytes_by_status"],
                 "profiles": json.loads(path.read_bytes()[4:].split(b"\n---\n", 1)[0])["environment"]["profiles"]}
(HERE / "readings-rendered.md").write_text("\n\n".join(f"## {k}\n\n" + render_document(HERE / v["path"]) for k, v in sorted(docs.items())) + "\n")
(HERE / "witnesses.json").write_text(json.dumps({"norm_defaults_status": status}, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
(HERE / "companions-check.json").write_text(json.dumps(docs, indent=1, sort_keys=True))
print("companions", len(docs), "without spec", bad, "witness rows", sum(len(v) for v in status.values()))
