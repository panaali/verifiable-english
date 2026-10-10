"""Repair the units of the 2026-10-05T1800Z audit's rejections (and the units with the same defect), in place, for the 2026-10-06T1800Z run.

Reads translation.ve.md (the previous run's translation, copied here), replaces or adds the companion documents and reading-set rows of
the units in repair4_specs.REPAIRED, and writes translation.ve.md back. The main document's vocabulary is unchanged, so no other
reading set's ids move. Everything else is left as it was, so the difference to the previous run measures the repair.

    uv run --frozen python usecases/udhr-pilot/run-20261006T1800Z/repair4.py
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

import repair4_specs as R  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.document import check_document, load_document  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
READINGS = HERE / "readings"
NOTE = "Rejected by the 2026-10-05T1800Z audit (previous-20261005T1800Z/AUDIT.md), or carrying the defect it named in a unit it did not sample"


def main():
    raw = (HERE.parent / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = P.read(HERE / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    units = {u["id"]: u for u in meta["units"]}
    sets = {s["unit"]: deepcopy(s) for s in meta["reading_sets"]}

    ids, witnesses = {}, {}
    for uid, cands in R.NEW_CANDIDATES.items():
        a, b = units[uid]["span"]
        for cid, spec, _why in cands:
            path = U.write_companion(READINGS, uid, cid, spec, raw[a:b], meta["open_terms"])
            ids[(uid, cid)] = load_document(path)["units"][0]["meaning_id"]
            verdict = check_document(path)
            assert verdict["premises"]["status"] == "model", (uid, cid, verdict["premises"])
            outs = WND.run(path, spec)
            assert all(o["as_expected"] for o in outs), (uid, cid, [o for o in outs if not o["as_expected"]])
            witnesses[f"{uid}.{cid}"] = outs
    print("companions written and checked:", len(ids), flush=True)

    for uid in R.REPAIRED:
        s = sets[uid]
        model_id = next(iter(s["models"]))
        old_ids = [r["id"] for r in s["readings"]]
        why = {c[0]: c[2] for c in R.NEW_CANDIDATES[uid]}
        by_id = {r["id"]: r for r in s["readings"]}
        order = list(old_ids)
        for cid in R.ADDED.get(uid, []):
            assert cid not in by_id, (uid, cid)
            after = "state_positive" if "state_positive" in order else order[-1]
            order.insert(order.index(after) + 1, cid)
        readings = []
        for cid in order:
            if cid in why:
                readings.append({"id": cid, "kind": "norm", "meaning_id": ids[(uid, cid)], "content": None,
                                 "admission": {"who": "translator", "why": why[cid], "distinguishing_models": {}}})
            else:
                readings.append(by_id[cid])
        for r in readings:
            r["admission"]["distinguishing_models"] = {o: model_id for o in order if o != r["id"]}
        s["readings"] = readings
        assert len(readings) > 1 and set(s["models"]) == {model_id}, (uid, list(s["models"]))
        s["version"] += 1
        s["rejected_history"] = [*s.get("rejected_history", []),
                                 {"version": s["version"] - 1, "readings": old_ids,
                                  "reason": f"{NOTE}; repaired 2026-10-06T1800Z: {R.REASON[uid]}."}]
        for r in readings:
            path = READINGS / f"{uid}.{r['id']}.ve.md"
            assert load_document(path)["units"][0]["meaning_id"] == r["meaning_id"], (uid, r["id"])
    meta["reading_sets"] = [sets[u["id"]] for u in meta["units"] if u["id"] in sets]
    P.write(HERE / "translation.ve.md", meta, raw)
    (HERE / "witnesses_repaired4.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("wrote translation.ve.md")


if __name__ == "__main__":
    main()
