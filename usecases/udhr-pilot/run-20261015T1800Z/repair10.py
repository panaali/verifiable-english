"""Audit repair of the UDHR translation for the 2026-10-10T0600Z run (repair10_specs.py says what and why).

Reads translation.ve.md and readings/ of this directory (copied from run-20261009T1800Z; the originals are kept in
previous-20261009T1800Z/) and writes them back. Every other unit is left exactly as it was.

    uv run --frozen python usecases/udhr-pilot/run-20261010T0600Z/repair10.py
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

import repair10_specs as R  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.document import check_document, load_document  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
READINGS = HERE / "readings"
AUDIT = "Rejected by the 2026-10-09T1800Z audit (previous-20261009T1800Z/AUDIT.md)"


def main():
    raw = (HERE.parent / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = P.read(HERE / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    units = {u["id"]: u for u in meta["units"]}
    sets = {s["unit"]: s for s in meta["reading_sets"]}
    shared_id, shared_model = next(iter(sets["u077"]["models"].items()))     # all relations empty: separates plain predicates

    ids, witnesses = {}, {}
    for uid, order in R.ORDER.items():
        for path in READINGS.glob(f"{uid}.*.ve.md"):
            path.unlink()
        a, b = units[uid]["span"]
        for cid, spec, _why in R.NEW[uid]:
            path = U.write_companion(READINGS, uid, cid, spec, raw[a:b], meta["open_terms"])
            ids[(uid, cid)] = load_document(path)["units"][0]["meaning_id"]
            verdict = check_document(path)
            assert verdict["premises"]["status"] == "model", (uid, cid, verdict["premises"])
            outs = WND.run(path, spec)
            assert all(o["as_expected"] for o in outs), (uid, cid, [o for o in outs if not o["as_expected"]])
            witnesses[f"{uid}.{cid}"] = outs
    print("companions written and checked:", len(ids), flush=True)

    for uid, order in R.ORDER.items():
        s = sets[uid]
        old_ids = [r["id"] for r in s["readings"]]
        why = {c[0]: c[2] for c in R.NEW[uid]}
        readings = [{"id": cid, "kind": "norm", "meaning_id": ids[(uid, cid)], "content": None,
                     "admission": {"who": "translator", "why": why[cid],
                                   "distinguishing_models": {o: shared_id for o in order if o != cid}}} for cid in order]
        s["models"] = {shared_id: shared_model}
        s["readings"] = readings
        s["version"] += 1
        s["rejected_history"] = [*s.get("rejected_history", []),
                                 {"version": s["version"] - 1, "readings": old_ids,
                                  "reason": f"{AUDIT}; repaired 2026-10-10T0600Z: {R.REASON[uid]}."}]
        for r in readings:
            path = READINGS / f"{uid}.{r['id']}.ve.md"
            assert load_document(path)["units"][0]["meaning_id"] == r["meaning_id"], (uid, r["id"])

    meta["reading_sets"] = [sets[u["id"]] for u in meta["units"] if u["id"] in sets]
    P.write(HERE / "translation.ve.md", meta, raw)
    (HERE / "witnesses_repaired10.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("wrote translation.ve.md")


if __name__ == "__main__":
    main()
