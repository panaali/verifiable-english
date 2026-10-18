"""Audit repair of the UDHR translation for the 2026-10-09T1800Z run (repair9_specs.py says what and why).

Reads previous-20261009T0600Z/ (translation.ve.md and readings/) and writes translation.ve.md and readings/ back. Every other unit is
left exactly as it was.

    uv run --frozen python usecases/udhr-pilot/run-20261009T1800Z/repair9.py
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import repair9_specs as R  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.document import _environment, load_document  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
PREV = HERE / "previous-20261009T0600Z"
READINGS = HERE / "readings"
STAMP = "repaired 2026-10-09T1800Z"
AUDIT = "Rejected by the 2026-10-09T0600Z audit (previous-20261009T0600Z/AUDIT.md)"


def main():
    raw = (HERE.parents[0] / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = P.read(PREV / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    sets = {s["unit"]: s for s in meta["reading_sets"]}
    if READINGS.exists():
        shutil.rmtree(READINGS)
    shutil.copytree(PREV / "readings", READINGS)

    for uid, gone in R.REMOVE.items():
        s = sets[uid]
        have = [x["id"] for x in s["readings"]]
        assert all(c in have for c in gone), (uid, have, gone)
        for cid in gone:
            path = READINGS / f"{uid}.{cid}.ve.md"
            if path.exists():
                path.unlink()
        s["readings"] = [x for x in s["readings"] if x["id"] not in gone]
        ids = [x["id"] for x in s["readings"]]
        for x in s["readings"]:
            x["admission"]["distinguishing_models"] = {o: m for o, m in x["admission"]["distinguishing_models"].items() if o in ids}
        if len(s["readings"]) == 1:
            s["models"] = {}
        why = R.REASON.get(uid, R.RIGHT_REASON)
        prefix = f"{AUDIT}; " if uid in R.AUDIT_REJECTED else ""
        s["rejected_history"] = [*s.get("rejected_history", []),
                                 {"version": s["version"], "readings": gone, "reason": f"{prefix}{STAMP}: {why}."}]
        s["version"] += 1

    preds = meta["environment"]["vocabulary"]["predicates"]
    for name in R.DROP_PREDICATES + R.DROP_SORTS:
        for s in meta["reading_sets"]:       # the saved models list every predicate and sort of the environment
            for model in s.get("models", {}).values():
                model["relations"].pop(name, None)
                model["domains"].pop(name, None)
        used = json.dumps([[x for x in s["readings"]] for s in meta["reading_sets"]] + [meta["units"]])
        assert f'"{name}"' not in used, name
        (preds if name in R.DROP_PREDICATES else meta["environment"]["vocabulary"]["sorts"]).pop(name)
    env = _environment(meta["environment"])
    meta["reading_sets"] = [P._reidentified(env, s) if s.get("models") else s for s in meta["reading_sets"]]

    # every companion still loads and keeps its meaning id
    moved = []
    for s in meta["reading_sets"]:
        for r in s["readings"]:
            if r["content"] is None:
                path = READINGS / f"{s['unit']}.{r['id']}.ve.md"
                mid = load_document(path)["units"][0]["meaning_id"]
                if mid != r["meaning_id"]:
                    moved.append((s["unit"], r["id"]))
                    r["meaning_id"] = mid
    print("meaning ids that moved:", moved)
    P.write(HERE / "translation.ve.md", meta, raw)
    json.dump({"removed": R.REMOVE, "moved_meaning_ids": moved}, open(HERE / "repair9-log.json", "w"), indent=1)
    print("wrote translation.ve.md; companions:", len(list(READINGS.glob("*.ve.md"))))


if __name__ == "__main__":
    main()
