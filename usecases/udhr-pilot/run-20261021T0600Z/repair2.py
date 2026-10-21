"""Repair the units of the 2026-10-04T1800Z audit's rejections (and the units with the same defect), in place, for the 2026-10-05T0600Z run.

Reads translation.ve.md (the previous run's translation, copied here), replaces the reading sets and companion documents of
the units in repair2_specs.REPAIRED, and writes translation.ve.md back. Everything else is left byte for byte as it was, so
the difference to the previous run measures the repair, not translator variance.

    uv run --frozen python usecases/udhr-pilot/run-20261005T0600Z/repair2.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import repair2_specs as R  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.document import check_document, load_document  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
READINGS = HERE / "readings"
AUDIT_NOTE = ("Rejected by the 2026-10-04T1800Z audit (previous-1800Z/AUDIT.md), or carrying the defect the audit named in a unit it "
              "did not sample; see the module notes of repair2_specs.py; repaired 2026-10-05T0600Z, pending a fresh independent audit.")
REASON = R.REASON


def main():
    raw = (HERE.parent / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = P.read(HERE / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    units = {u["id"]: u for u in meta["units"]}
    previous = {s["unit"]: s for s in meta["reading_sets"]}
    model_id, model = next(iter(previous["u022a"]["models"].items()))

    for unit in R.REPAIRED:
        for path in READINGS.glob(f"{unit}.*.ve.md"):
            path.unlink()

    ids, witnesses = {}, {}
    for unit, cands in R.CANDIDATES.items():
        a, b = units[unit]["span"]
        for cid, spec, _why in cands:
            path = U.write_companion(READINGS, unit, cid, spec, raw[a:b], meta["open_terms"])
            ids[(unit, cid)] = load_document(path)["units"][0]["meaning_id"]
            verdict = check_document(path)
            assert verdict["premises"]["status"] == "model", (unit, cid, verdict["premises"])
            outs = WND.run(path, spec)
            assert all(o["as_expected"] for o in outs), (unit, cid, [o for o in outs if not o["as_expected"]])
            witnesses[f"{unit}.{cid}"] = outs
    print("companions written and checked:", len(ids), flush=True)

    sets = {s["unit"]: s for s in meta["reading_sets"]}
    for unit, cands in R.CANDIDATES.items():
        cids = [c[0] for c in cands]
        readings = []
        for cid, _spec, why in cands:
            readings.append({"id": cid, "kind": "norm", "meaning_id": ids[(unit, cid)], "content": None,
                             "admission": {"who": "translator", "why": why,
                                           "distinguishing_models": {o: model_id for o in cids if o != cid}}})
        prev = previous[unit]
        kind = "Rejected by the" if unit in R.AUDIT_REJECTED else "Same defect as the units rejected by the"
        history = [*prev.get("rejected_history", []),
                   {"version": prev["version"], "readings": [r["id"] for r in prev["readings"]],
                    "reason": f"{kind} 2026-10-04T1800Z audit / repaired 2026-10-05T0600Z: {REASON[unit]}."}]
        sets[unit] = {"id": f"rs_{unit}", "unit": unit, "version": prev["version"] + 1, "status": "open",
                      "models": {model_id: model} if len(cands) > 1 else {}, "readings": readings,
                      "rejected_history": history}
    meta["reading_sets"] = [sets[u["id"]] for u in meta["units"] if u["id"] in sets]
    P.write(HERE / "translation.ve.md", meta, raw)
    (HERE / "witnesses_repaired2.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("wrote translation.ve.md")


if __name__ == "__main__":
    main()
