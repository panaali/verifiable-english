"""Repair the units of the 2026-10-05T0600Z audit's rejections (and the units with the same defect), in place, for the 2026-10-05T1800Z run.

Reads translation.ve.md (the previous run's translation, copied here), changes the reading sets and companion documents of the
units in repair3_specs.REPAIRED (and the vocabulary and one formula of u112's set), re-identifies every set's meaning and model ids over
the changed vocabulary, and writes translation.ve.md back. Everything else is left as it was, so the difference to the previous
run measures the repair, not translator variance.

    uv run --frozen python usecases/udhr-pilot/run-20261005T1800Z/repair3.py
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

import repair3_specs as R  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.document import _environment, check_document, load_document  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
READINGS = HERE / "readings"
NOTE = "Rejected by the 2026-10-05T0600Z audit (previous-20261005T0600Z/AUDIT.md), or carrying the defect the audit named in a unit it did not sample"


def main():
    raw = (HERE.parent / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = P.read(HERE / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    units = {u["id"]: u for u in meta["units"]}
    sets = {s["unit"]: deepcopy(s) for s in meta["reading_sets"]}

    # ---- u112: the vocabulary gains exercise_of_declared_right; the formula reading is restricted to it
    name, decl = R.U112_DECLARED
    preds = meta["environment"]["vocabulary"]["predicates"]
    assert name not in preds
    preds[name] = decl
    meta["environment"]["vocabulary"]["predicates"] = dict(sorted(preds.items()))
    s112 = sets["u112"]
    for model in s112["models"].values():
        model["relations"][name] = [["e0"]]
    for r in s112["readings"]:
        if r["id"] == "exercise_unprotected":
            r["content"] = R.U112_CONTENT
            r["admission"]["why"] = R.U112_WHY
    env = _environment(meta["environment"])
    for uid in list(sets):
        sets[uid] = P._reidentified(env, sets[uid])
    model_id, model = next(iter(sets["u022a"]["models"].items()))

    # ---- companions: removed, rewritten, loaded and checked
    for uid, cids in R.REMOVED.items():
        for cid in cids:
            (READINGS / f"{uid}.{cid}.ve.md").unlink()
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

    def row(uid, cid, meaning_id, why, others, mid):
        return {"id": cid, "kind": "norm", "meaning_id": meaning_id, "content": None,
                "admission": {"who": "translator", "why": why,
                              "distinguishing_models": {o: mid for o in others if o != cid}}}

    # ---- the reading sets of the repaired units
    for uid in [u for u in R.REPAIRED if u != "u112"]:
        s = sets[uid]
        old_ids = [r["id"] for r in s["readings"]]
        why = {c[0]: c[2] for c in R.NEW_CANDIDATES.get(uid, [])}
        keep = [r for r in s["readings"] if r["id"] not in R.REMOVED.get(uid, [])]
        if uid == "u051":
            order = ["entitlement", "liberty", "state_avoid", "anyone_avoid"]
        elif uid == "u098":
            order = old_ids
        else:
            order = [r["id"] for r in keep]
        by_id = {r["id"]: r for r in keep}
        readings = []
        for cid in order:
            if cid in why:
                readings.append(row(uid, cid, ids[(uid, cid)], why[cid], order, model_id))
            else:
                readings.append(by_id[cid])
        for r in readings:
            r["admission"]["distinguishing_models"] = {o: model_id for o in order if o != r["id"]}
        s["readings"] = readings
        assert len(readings) > 1 and set(s["models"]) == {model_id}, (uid, list(s["models"]))
        s["version"] += 1
        s["rejected_history"] = [*s.get("rejected_history", []),
                                 {"version": s["version"] - 1, "readings": old_ids,
                                  "reason": f"{NOTE}; repaired 2026-10-05T1800Z: {R.REASON[uid]}."}]
    # u112 keeps its own model (it also has the declared-right relation)
    for uid in R.REPAIRED:
        for r in sets[uid]["readings"]:
            if (READINGS / f"{uid}.{r['id']}.ve.md").exists():
                assert load_document(READINGS / f"{uid}.{r['id']}.ve.md")["units"][0]["meaning_id"] == r["meaning_id"], (uid, r["id"])
    s = sets["u112"]
    s["version"] += 1
    s["rejected_history"] = [*s.get("rejected_history", []),
                             {"version": s["version"] - 1, "readings": [r["id"] for r in s["readings"]],
                              "reason": f"{NOTE}; repaired 2026-10-05T1800Z: {R.REASON['u112']}."}]
    meta["reading_sets"] = [sets[u["id"]] for u in meta["units"] if u["id"] in sets]
    P.write(HERE / "translation.ve.md", meta, raw)
    (HERE / "witnesses_repaired3.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("wrote translation.ve.md")


if __name__ == "__main__":
    main()
