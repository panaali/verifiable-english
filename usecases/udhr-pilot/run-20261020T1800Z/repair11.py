"""Audit repair of the UDHR translation for the 2026-10-12T0600Z run (repair11_specs.py says what and why), plus the removal of every
trace of removed readings from the reading sets (`rejected_history`).

Reads translation.ve.md and readings/ of this directory (copied from run-20261010T0600Z; the originals are kept in
previous-20261010T0600Z/) and writes them back. Every other unit is left exactly as it was.

    uv run --frozen python usecases/udhr-pilot/run-20261012T0600Z/repair11.py
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

import repair11_specs as R  # noqa: E402
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

    # ---- u061: the entitlement, replacing the old duty candidate
    witnesses = {}
    for uid, order in R.ORDER.items():
        for path in READINGS.glob(f"{uid}.*.ve.md"):
            path.unlink()
        a, b = units[uid]["span"]
        ids = {}
        for cid, spec, _why in R.NEW[uid]:
            path = U.write_companion(READINGS, uid, cid, spec, raw[a:b], meta["open_terms"])
            ids[cid] = load_document(path)["units"][0]["meaning_id"]
            verdict = check_document(path)
            assert verdict["premises"]["status"] == "model", (uid, cid, verdict["premises"])
            outs = WND.run(path, spec)
            assert all(o["as_expected"] for o in outs), (uid, cid, [o for o in outs if not o["as_expected"]])
            witnesses[f"{uid}.{cid}"] = outs
        s = sets[uid]
        why = {c[0]: c[2] for c in R.NEW[uid]}
        s["readings"] = [{"id": cid, "kind": "norm", "meaning_id": ids[cid], "content": None,
                          "admission": {"who": "translator", "why": why[cid], "distinguishing_models": {}}} for cid in order]
        s["models"] = {}
        s["version"] += 1
    print("companions written and checked:", sorted(witnesses), flush=True)

    # ---- u105b, u105c: the legacy form (readings@1 absent) cannot hold labels or couplings; integrate.py adds the coupling to the parts
    for uid, set_id in R.COUPLED.items():
        assert sets[uid]["id"] == set_id
        sets[uid]["version"] += 1

    # ---- every trace of a removed reading goes: the ledger of rejected candidates is not part of the translation
    for s in meta["reading_sets"]:
        s.pop("rejected_history", None)

    # ... and so does a sentence of an admission's `why` that tells what an earlier version of the set held (u054)
    gone = (" Removed after the audit: the claim guarded by owes_nationality_to (it could leave everyone without the entitlement) and the "
            "permission-only liberty (it weakens an entitlement to a permission).")
    for s in meta["reading_sets"]:
        for r in s["readings"]:
            r["admission"]["why"] = r["admission"]["why"].replace(gone, "")
        assert not any("emoved" in r["admission"]["why"] for r in s["readings"]), s["id"]

    meta["reading_sets"] = [sets[u["id"]] for u in meta["units"] if u["id"] in sets]
    P.write(HERE / "translation.ve.md", meta, raw)
    (HERE / "witnesses_repaired11.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("wrote translation.ve.md")


if __name__ == "__main__":
    main()
