"""Apply the 2026-10-17T1800Z audit repair (repair15_specs.py says what and why) to translation.ve.md and readings/.

Every unit not named in repair15_specs.ORDER is left exactly as it was.

    uv run --frozen python usecases/udhr-pilot/run-20261017T1800Z/repair15.py
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

import repair15_specs as R  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.document import check_document, load_document  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
READINGS = HERE / "readings"
STAMP = "repaired 2026-10-17T1800Z"


def main():
    raw = (HERE.parent / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = P.read(HERE / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    units = {u["id"]: u for u in meta["units"]}
    sets = {s["unit"]: s for s in meta["reading_sets"]}
    shared_id, shared_model = next(iter(sets["u055"]["models"].items()))
    witnesses = {}
    for uid, order in R.ORDER.items():
        old_ids = [r["id"] for r in sets[uid]["readings"]]
        for path in READINGS.glob(f"{uid}.*.ve.md"):
            path.unlink()
        a, b = units[uid]["span"]
        readings = []
        for cid, spec, why in R.NEW[uid]:
            path = U.write_companion(READINGS, uid, cid, spec, raw[a:b], meta["open_terms"])
            doc = load_document(path)
            verdict = check_document(path)
            assert verdict["premises"]["status"] == "model", (uid, cid, verdict["premises"])
            outs = WND.run(path, spec)
            assert all(o["as_expected"] for o in outs), (uid, cid, [o for o in outs if not o["as_expected"]])
            witnesses[f"{uid}.{cid}"] = outs
            readings.append({"id": cid, "kind": "norm", "meaning_id": doc["units"][0]["meaning_id"], "content": None,
                             "admission": {"who": "translator", "why": why, "distinguishing_models": {}}})
            print("written and checked:", uid, cid, [o["lean_point_status"] for o in outs], flush=True)
        assert [r["id"] for r in readings] == order
        s = deepcopy(sets[uid])
        s["models"] = {shared_id: shared_model}
        for r in readings:
            r["admission"]["distinguishing_models"] = {o: shared_id for o in order if o != r["id"]}
        s["readings"] = readings
        s["version"] += 1
        audit = uid in R.AUDIT_REJECTED
        s["rejected_history"] = [*s.get("rejected_history", []),
                                 {"version": s["version"] - 1, "readings": old_ids,
                                  "reason": f"{'Rejected by the 20261017T0600Z audit' if audit else 'Named by the 20261017T0600Z audit'}; "
                                            f"{STAMP}: {R.REASON[uid]}."}]
        sets[uid] = s
    meta["reading_sets"] = [sets[u["id"]] for u in meta["units"] if u["id"] in sets]
    P.write(HERE / "translation.ve.md", meta, raw)
    (HERE / "witnesses_repaired15.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("wrote translation.ve.md")


if __name__ == "__main__":
    main()
