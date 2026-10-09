"""Audit repair of the UDHR translation for the 2026-10-09T0600Z run (repair8_specs.py says what and why).

Reads previous-20261008T1800Z/ (translation.ve.md and readings/) and writes translation.ve.md and readings/ back. Every other unit is
left exactly as it was.

    uv run --frozen python usecases/udhr-pilot/run-20261009T0600Z/repair8.py
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

import repair8_specs as R  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.document import check_document, load_document  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
PREV = HERE / "previous-20261008T1800Z"
READINGS = HERE / "readings"
STAMP = "repaired 2026-10-09T0600Z"
AUDIT = "Rejected by the 2026-10-08T1800Z audit (previous-20261008T1800Z/AUDIT.md)"


def refresh_embedded_terms(terms):
    """Companion documents embed the open terms they use: bring those copies to the repaired factors."""
    changed = []
    for path in sorted(READINGS.glob("*.ve.md")):
        raw = path.read_bytes()
        _, front, body = raw.split(b"---\n", 2)
        meta = json.loads(front)
        new = [deepcopy(terms[t["name"]]) if t["name"] in terms else t for t in meta["open_terms"]]
        if new != meta["open_terms"]:
            meta["open_terms"] = new
            path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n---\n" + body)
            changed.append(path.name)
    return changed


def edit_u054():
    """u054's companion: the predicate no longer mentions a duty-bearer open term, and the unit has no open term."""
    path = READINGS / "u054.entitlement.ve.md"
    _, front, body = path.read_bytes().split(b"---\n", 2)
    m = json.loads(front)
    decl = m["environment"]["vocabulary"]["predicates"]["is_entitled_to_a_nationality"]
    assert "bearer_of_the_nationality_duty" in decl["description"], decl
    decl["description"] = "The person is entitled to a nationality"
    m["open_terms"] = []
    for unit in m["units"]:
        unit["meaning"] = "specified"
    path.write_bytes(b"---\n" + json.dumps(m, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n---\n" + body)


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

    # ---- positive claims removed (candidates and their companion files)
    for uid, gone in R.REMOVE.items():
        s = sets[uid]
        have = [x["id"] for x in s["readings"]]
        assert all(c in have for c in gone), (uid, have, gone)
        for cid in gone:
            (READINGS / f"{uid}.{cid}.ve.md").unlink()
        s["readings"] = [x for x in s["readings"] if x["id"] not in gone]
        ids = [x["id"] for x in s["readings"]]
        for x in s["readings"]:
            x["admission"]["distinguishing_models"] = {o: m for o, m in x["admission"]["distinguishing_models"].items() if o in ids}
        if len(s["readings"]) == 1:
            s["models"] = {}
        s["rejected_history"] = [*s.get("rejected_history", []), {"version": s["version"], "readings": gone,
                                                                   "reason": f"{STAMP}: {R.REMOVE_REASON}."}]
        s["version"] += 1

    # ---- open terms: new factors, the dropped one, the re-added one
    terms = {t["name"]: t for t in meta["open_terms"]}
    for name, factors in R.NEW_FACTORS.items():
        terms[name]["factors"] = factors
    meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] not in R.DROP_TERMS]
    meta["open_terms"].append(deepcopy(R.U098_TERM))
    terms = {t["name"]: t for t in meta["open_terms"]}
    for uid, opens in R.OPEN_OF_UNIT.items():
        units[uid]["meaning"] = {"open": opens} if opens else "specified"
    edit_u054()

    # ---- rewritten companions (u020, u098)
    witnesses = {}
    for uid, cid, spec, why in (("u020", "prohibited", R.U020, R.U020_WHY), ("u098", "unassigned", R.U098, R.U098_WHY)):
        a, b = units[uid]["span"]
        s = sets[uid]
        for path in READINGS.glob(f"{uid}.*.ve.md"):
            path.unlink()
        path = U.write_companion(READINGS, uid, cid, spec, raw[a:b], meta["open_terms"])
        verdict = check_document(path)
        assert verdict["premises"]["status"] == "model", (uid, cid, verdict["premises"])
        outs = WND.run(path, spec)
        assert all(o["as_expected"] for o in outs), (uid, cid, [o for o in outs if not o["as_expected"]])
        witnesses[f"{uid}.{cid}"] = outs
        old = s["readings"]
        s["readings"] = [{"id": cid, "kind": "norm", "meaning_id": load_document(path)["units"][0]["meaning_id"], "content": None,
                          "admission": {"who": "translator", "why": why, "distinguishing_models": {}}}]
        s["rejected_history"] = [*s.get("rejected_history", []), {"version": s["version"], "readings": [r["id"] for r in old],
                                                                   "reason": f"{AUDIT}; {STAMP}: {R.REASON[uid]}."}]
        s["models"] = {}
        s["version"] += 1
    units["u098"]["meaning"] = {"open": ["compulsory"]}

    # ---- the companions embed the open terms they use
    changed = refresh_embedded_terms(terms)
    print("companions with refreshed open terms:", changed)

    # ---- every companion still loads and keeps its meaning id (an id that moved with the factors is brought up to date)
    moved = []
    for s in meta["reading_sets"]:
        for r in s["readings"]:
            if r["content"] is None:
                path = READINGS / f"{s['unit']}.{r['id']}.ve.md"
                mid = load_document(path)["units"][0]["meaning_id"]
                if mid != r["meaning_id"]:
                    moved.append((s["unit"], r["id"]))
                    r["meaning_id"] = mid
    print("meaning ids that moved with the factors:", moved)
    P.write(HERE / "translation.ve.md", meta, raw)
    (HERE / "witnesses_repaired8.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    json.dump({"refreshed_companions": changed, "moved_meaning_ids": moved}, open(HERE / "repair8-log.json", "w"))
    print("wrote translation.ve.md; companions:", len(list(READINGS.glob("*.ve.md"))))


if __name__ == "__main__":
    main()
