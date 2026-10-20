"""Audit repair of the UDHR translation for the 2026-10-08T1800Z run (repair7_specs.py says what and why).

Reads previous-20261008T0600Z/ (translation.ve.md and readings/) and writes translation.ve.md and readings/ back: candidates removed,
two companions rewritten, open terms and factors repaired. Every other unit is left exactly as it was.

    uv run --frozen python usecases/udhr-pilot/run-20261008T1800Z/repair7.py
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

import repair7_specs as R  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.document import check_document, load_document  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
PREV = HERE / "previous-20261008T0600Z"
READINGS = HERE / "readings"
AUDIT = "Rejected by the 2026-10-08 audit of run-20261008T0600Z (previous-20261008T0600Z/AUDIT.md)"


def main():
    raw = (HERE.parents[0] / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = P.read(PREV / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    units = {u["id"]: u for u in meta["units"]}
    sets = {s["unit"]: s for s in meta["reading_sets"]}

    if READINGS.exists():
        shutil.rmtree(READINGS)
    shutil.copytree(PREV / "readings", READINGS)

    # ---- candidates removed
    for uid, gone in R.REMOVE.items():
        s = sets[uid]
        have = [r["id"] for r in s["readings"]]
        assert all(c in have for c in gone), (uid, have, gone)
        for cid in gone:
            (READINGS / f"{uid}.{cid}.ve.md").unlink()
        s["readings"] = [r for r in s["readings"] if r["id"] not in gone]

    # ---- companions rewritten or new
    witnesses, ids = {}, {}
    for uid, cands in R.NEW.items():
        a, b = units[uid]["span"]
        s = sets[uid]
        for cid, spec, why in cands:
            for path in READINGS.glob(f"{uid}.*.ve.md"):
                path.unlink()
            path = U.write_companion(READINGS, uid, cid, spec, raw[a:b], meta["open_terms"])
            verdict = check_document(path)
            assert verdict["premises"]["status"] == "model", (uid, cid, verdict["premises"])
            outs = WND.run(path, spec)
            assert all(o["as_expected"] for o in outs), (uid, cid, [o for o in outs if not o["as_expected"]])
            witnesses[f"{uid}.{cid}"] = outs
            ids[(uid, cid)] = load_document(path)["units"][0]["meaning_id"]
            old = s["readings"]
            s["readings"] = [{"id": cid, "kind": "norm", "meaning_id": ids[(uid, cid)], "content": None,
                              "admission": {"who": "translator", "why": why, "distinguishing_models": {}}}]
            s["rejected_history"] = [*s.get("rejected_history", []), {"version": s["version"], "readings": [r["id"] for r in old],
                                                                       "reason": f"{AUDIT}; repaired 2026-10-08T1800Z: {R.REASON[uid]}."}]
        s["models"] = {}
        s["version"] += 1

    # ---- the sets that lost candidates: references to them go, a lone reading has no distinguishing model
    for uid in R.REMOVE:
        s = sets[uid]
        for r in s["readings"]:
            r["admission"]["distinguishing_models"] = {o: m for o, m in r["admission"]["distinguishing_models"].items()
                                                       if o in [x["id"] for x in s["readings"]]}
        if len(s["readings"]) == 1:
            s["models"] = {}
        s["version"] += 1
        s["rejected_history"] = [*s.get("rejected_history", []),
                                 {"version": s["version"] - 1, "readings": R.REMOVE[uid],
                                  "reason": f"{AUDIT if uid in R.AUDIT_REJECTED else 'Same defect as rejected siblings'}; repaired "
                                            f"2026-10-08T1800Z: {R.REASON[uid]}."}]

    # ---- open terms and units
    for uid, opens in R.OPEN_OF_UNIT.items():
        units[uid]["meaning"] = {"open": opens} if opens else "specified"
    terms = {t["name"]: t for t in meta["open_terms"]}
    for name, factors in R.NEW_FACTORS.items():
        terms[name]["factors"] = factors
    def used_by(m):
        return {t for u in m["units"] if isinstance(u.get("meaning"), dict) for t in u["meaning"].get("open", [])}
    prev_meta, _ = P.read(PREV / "translation.ve.md")
    used = used_by(meta)
    dropped = [t for t in used_by(prev_meta) - used if t not in used_by(meta)]
    meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] not in dropped]
    print("open terms dropped (unused):", dropped)

    # ---- every companion still loads, checks, and keeps its meaning id
    for s in meta["reading_sets"]:
        for r in s["readings"]:
            if r["content"] is None:
                path = READINGS / f"{s['unit']}.{r['id']}.ve.md"
                assert load_document(path)["units"][0]["meaning_id"] == r["meaning_id"], (s["unit"], r["id"])
    P.write(HERE / "translation.ve.md", meta, raw)
    (HERE / "witnesses_repaired7.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    json.dump({"open_terms_dropped": dropped}, open(HERE / "repair7-dropped.json", "w"))
    print("wrote translation.ve.md; companions:", len(list(READINGS.glob("*.ve.md"))))


if __name__ == "__main__":
    main()
