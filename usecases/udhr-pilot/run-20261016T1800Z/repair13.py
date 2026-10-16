"""Apply the 2026-10-14T1800Z repairs (repair13_specs.py says what and why) to translation.ve.md and readings/.

The previous run's files are kept in previous-20261013T0600Z/. Every unit not named in repair13_specs.ORDER is left exactly as it was.

    uv run --frozen python usecases/udhr-pilot/run-20261014T1800Z/repair13.py
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

import repair13_specs as R  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.document import check_document, load_document  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
READINGS = HERE / "readings"


def main():
    raw = (HERE.parent / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = P.read(HERE / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    units = {u["id"]: u for u in meta["units"]}
    sets = {s["unit"]: s for s in meta["reading_sets"]}

    # the preconditions the plans name: part03 and u097's span are as the plans measured them
    assert units["u097"]["span"] == [8857, 8933] and raw[8857:8933] == b"Education shall be free, at least in the elementary and fundamental stages. "
    assert units["u097"]["kind"] == ["unformalised", "quantities"]
    for uid in ("u085", "u091", "u106"):
        assert units[uid]["kind"] == ["unformalised", "other_act_phrase_grammar"], uid

    have = {t["name"] for t in meta["open_terms"]}
    for name, term in R.NEW_TERMS.items():
        if name not in have:
            meta["open_terms"].append(deepcopy(term))
            have.add(name)

    witnesses = {}
    for uid in R.ORDER:
        for path in READINGS.glob(f"{uid}.*.ve.md"):
            path.unlink()
        cid, spec, why = R.NEW[uid]
        a, b = units[uid]["span"]
        if "source" in spec:                      # the research document quotes the same bytes (up to trailing white space)
            assert raw[a:b].strip() == spec["source"].strip(), uid
        path = U.write_companion(READINGS, uid, cid, spec, raw[a:b], meta["open_terms"])
        doc = load_document(path)
        meaning_id = doc["units"][0]["meaning_id"]
        verdict = check_document(path)
        assert verdict["premises"]["status"] == "model", (uid, verdict["premises"])
        outs = WND.run(path, spec)
        assert all(o["as_expected"] for o in outs), (uid, [o for o in outs if not o["as_expected"]])
        witnesses[f"{uid}.{cid}"] = outs
        reading = {"id": cid, "kind": "norm", "meaning_id": meaning_id, "content": None,
                   "admission": {"who": "translator", "why": why, "distinguishing_models": {}}}
        s = sets.get(uid)
        if s is None:
            s = {"id": f"rs_{uid}", "unit": uid, "version": 1, "status": "open", "models": {}, "readings": []}
        else:
            s = deepcopy(s)
            s["version"] += 1
        s["models"] = {}
        s["readings"] = [reading]
        sets[uid] = s
        unit = units[uid]
        unit["kind"] = "norm"
        unit["meaning"] = {"open": list(spec["open"])} if spec["open"] else "specified"
        print("written and checked:", uid, cid, meaning_id[:12], [o["lean_point_status"] for o in outs], flush=True)

    meta["reading_sets"] = [sets[u["id"]] for u in meta["units"] if u["id"] in sets]
    P.write(HERE / "translation.ve.md", meta, raw)
    (HERE / "witnesses_repaired13.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("wrote translation.ve.md")


if __name__ == "__main__":
    main()
