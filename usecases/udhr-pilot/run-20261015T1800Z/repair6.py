"""Words-only repair and audit repair of the UDHR translation, for the 2026-10-08T0600Z run.

Reads previous-20261007T1800Z/translation.ve.md (the previous run's translation) and its companion documents, applies repair6_specs
(no reading from outside knowledge; the six units the 2026-10-07T1800Z audit rejected), and writes translation.ve.md and
readings/ back. Every unit not named in repair6_specs.ORDER (and u110) is left as it was, so the difference to the previous run
measures the repair, not translator variance.

    uv run --frozen python usecases/udhr-pilot/run-20261008T0600Z/repair6.py
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

import repair6_specs as R  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.ast import And, Binary, Eq, Exists, Forall, Implies, Var, _to_data, formula_from_data  # noqa: E402
from ve.document import _environment, check_document, load_document  # noqa: E402
from ve.identity import meaning_id  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
from ve.readings import _reading_evaluation  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
PREV = HERE / "previous-20261007T1800Z"
READINGS = HERE / "readings"
WORDS = ("Words-only repair (lead, 2026-10-08): a reading is kept only where the English itself supports it; readings that put a duty "
         "on every State, or on every State, group and person, where the words name no bearer, came from outside knowledge")
AUDIT = "Rejected by the 2026-10-07T1800Z audit (previous-20261007T1800Z/AUDIT.md)"
V = Var
OWES, POSS, IDENT = "owes_duties_to", "full_development_possible_in", "community_identified_for"

U110_WHY = {
    "per_person": "Article 29(1) read with 'the community in which alone the free and full development of his personality is possible' as "
                  "a restrictive description whose existence the sentence takes for granted: every person has duties to a community in "
                  "which that person's free and full development is possible, and in no other community (the clause is part of what is "
                  "asserted, so a person with no such community makes the statement false); each person may have a different community. "
                  "Open terms: duties_to_the_community, free_and_full_development.",
    "one_for_all": "Article 29(1) read as above, with 'the community' one community for everyone: there is a community to which every "
                   "person has duties, in which every person's free and full development is possible, and in no other community "
                   "(a stronger statement than the per-person reading: it implies it). Open terms: duties_to_the_community, "
                   "free_and_full_development, community_of_full_development.",
}


def u110_formulas():
    # innermost variable is 0
    per_person = Forall("person", Exists("community", And(Binary(OWES, V(1), V(0)), And(
        Binary(POSS, V(1), V(0)), Forall("community", Implies(Binary(POSS, V(2), V(0)), Eq(V(0), V(1))))))))
    one_for_all = Exists("community", Forall("person", And(Binary(OWES, V(0), V(1)), And(
        Binary(POSS, V(0), V(1)), Forall("community", Implies(Binary(POSS, V(1), V(0)), Eq(V(0), V(2))))))))
    return {"per_person": _to_data(per_person), "one_for_all": _to_data(one_for_all)}


def main():
    raw = (HERE.parent / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = P.read(PREV / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    units = {u["id"]: u for u in meta["units"]}
    sets = {s["unit"]: deepcopy(s) for s in meta["reading_sets"]}

    # ---- the identified-community relation is gone with the reading that used it; every set's ids move with the vocabulary
    del meta["environment"]["vocabulary"]["predicates"][IDENT]
    for s in sets.values():
        for model in s["models"].values():
            model["relations"].pop(IDENT, None)
    env = _environment(meta["environment"])
    for uid in list(sets):
        if uid != "u110":                                   # its readings are replaced below
            sets[uid] = P._reidentified(env, sets[uid])
    model_env, _ = _reading_evaluation(env)
    shared_id, shared_model = next(iter(sets["u112"]["models"].items()))

    # ---- companions: drop what is gone, write what is new, check every one
    if READINGS.exists():
        shutil.rmtree(READINGS)
    shutil.copytree(PREV / "readings", READINGS)
    for uid, order in R.ORDER.items():
        for path in READINGS.glob(f"{uid}.*.ve.md"):
            cid = path.name[len(uid) + 1:-len(".ve.md")]
            if cid not in order or cid in dict((c, 1) for c, _, _ in R.NEW.get(uid, [])):
                path.unlink()
    ids, witnesses = {}, {}
    for uid, cands in R.NEW.items():
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

    # ---- the norm-candidate sets
    for uid, order in R.ORDER.items():
        s = sets[uid]
        old_ids = [r["id"] for r in s["readings"]]
        by_id = {r["id"]: r for r in s["readings"]}
        why = {c[0]: c[2] for c in R.NEW.get(uid, [])}
        readings = []
        for cid in order:
            if cid in why:
                readings.append({"id": cid, "kind": "norm", "meaning_id": ids[(uid, cid)], "content": None,
                                 "admission": {"who": "translator", "why": why[cid], "distinguishing_models": {}}})
            else:
                r = deepcopy(by_id[cid])
                path = READINGS / f"{uid}.{cid}.ve.md"
                r["meaning_id"] = load_document(path)["units"][0]["meaning_id"]
                readings.append(r)
        if len(readings) > 1:
            s["models"] = {shared_id: shared_model}
            for r in readings:
                r["admission"]["distinguishing_models"] = {o: shared_id for o in order if o != r["id"]}
        else:
            s["models"] = {}
            readings[0]["admission"]["distinguishing_models"] = {}
        s["readings"] = readings
        s["version"] += 1
        audit = uid in R.AUDIT_REJECTED
        s["rejected_history"] = [*s.get("rejected_history", []),
                                 {"version": s["version"] - 1, "readings": old_ids,
                                  "reason": f"{AUDIT if audit else WORDS}; repaired 2026-10-08T0600Z: {R.REASON[uid]}."}]
        for r in readings:
            path = READINGS / f"{uid}.{r['id']}.ve.md"
            assert load_document(path)["units"][0]["meaning_id"] == r["meaning_id"], (uid, r["id"])

    # ---- u110: two asserted readings (the clause is part of what is said)
    s = sets["u110"]
    old_ids = [r["id"] for r in s["readings"]]
    formulas = u110_formulas()
    base = deepcopy(shared_model)
    base["domains"]["person"], base["domains"]["community"] = ["p0", "p1"], ["c0", "c1"]
    base["relations"][OWES] = [["p0", "c0"], ["p1", "c1"]]
    base["relations"][POSS] = [["p0", "c0"], ["p1", "c1"]]
    mid = FiniteModel.from_dict(model_env, base).model_id      # per_person is true here, one_for_all is false
    readings = []
    for cid, data in formulas.items():
        other = next(o for o in formulas if o != cid)
        readings.append({"id": cid, "kind": "asserted", "content": data,
                         "meaning_id": meaning_id(env, formula_from_data(env, data)),
                         "admission": {"who": "translator", "why": U110_WHY[cid], "distinguishing_models": {other: mid}}})
    s["readings"], s["models"] = readings, {mid: base}
    s["version"] += 1
    s["rejected_history"] = [*s.get("rejected_history", []),
                             {"version": s["version"] - 1, "readings": old_ids,
                              "reason": f"{AUDIT}; repaired 2026-10-08T0600Z: the `identified_community` reading kept the relative clause out "
                                        "of what is said (it stays true when development is possible nowhere) and is removed; the two "
                                        "readings left keep the clause as part of what is asserted."}]

    meta["reading_sets"] = [sets[u["id"]] for u in meta["units"] if u["id"] in sets]
    P.write(HERE / "translation.ve.md", meta, raw)
    (HERE / "witnesses_repaired6.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("wrote translation.ve.md")


if __name__ == "__main__":
    main()
