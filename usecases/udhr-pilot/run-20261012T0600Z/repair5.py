"""Repair the units of the 2026-10-06T1800Z audit's rejections (and the units with the same defect), in place, for the 2026-10-07T1800Z run.

Reads translation.ve.md (the previous run's translation, copied here), adds the community vocabulary u110 needs to the main
environment (every reading set's model and meaning ids are recomputed over it), replaces or adds the companion documents and
reading-set rows of the units in repair5_specs.REPAIRED, and writes translation.ve.md back. Everything else is left as it was, so
the difference to the previous run measures the repair.

    uv run --frozen python usecases/udhr-pilot/run-20261007T1800Z/repair5.py
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

import repair5_specs as R  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.ast import And, Binary, Eq, Exists, Forall, Implies, Var, _to_data  # noqa: E402
from ve.document import _environment, check_document, load_document  # noqa: E402
from ve.identity import meaning_id  # noqa: E402
from ve.ast import formula_from_data  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
from ve.readings import _reading_evaluation  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
READINGS = HERE / "readings"
NOTE = "Rejected by the 2026-10-06T1800Z audit (previous-20261006T1800Z/AUDIT.md), or carrying the defect it named in a unit it did not sample"
V = Var

OWES, POSS, IDENT = "owes_duties_to", "full_development_possible_in", "community_identified_for"


def vocabulary(meta):
    v = meta["environment"]["vocabulary"]
    v["sorts"]["community"] = {"description": "a community", "verbalisation": {"plural": "communities", "singular": "community"}}
    v["predicates"][OWES] = {"arguments": ["person", "community"],
                             "description": "The person has duties to the community (the open term duties_to_the_community)"}
    v["predicates"][POSS] = {"arguments": ["person", "community"],
                             "description": "The free and full development of the person's personality is possible in the community "
                                            "(the open term free_and_full_development)"}
    v["predicates"][IDENT] = {"arguments": ["person", "community"],
                              "description": "The community is the one the sentence picks out for the person, the one in which the "
                                             "free and full development of the person's personality is possible (the open term "
                                             "community_of_full_development)"}


def u110_formulas():
    # innermost variable is 0
    per_person = Forall("person", Exists("community", And(Binary(OWES, V(1), V(0)), And(
        Binary(POSS, V(1), V(0)), Forall("community", Implies(Binary(POSS, V(2), V(0)), Eq(V(0), V(1))))))))
    one_for_all = Exists("community", Forall("person", And(Binary(OWES, V(0), V(1)), And(
        Binary(POSS, V(0), V(1)), Forall("community", Implies(Binary(POSS, V(1), V(0)), Eq(V(0), V(2))))))))
    identified = Forall("person", Exists("community", And(Binary(OWES, V(1), V(0)), Binary(IDENT, V(1), V(0)))))
    return {"per_person": _to_data(per_person), "one_for_all": _to_data(one_for_all), "identified_community": _to_data(identified)}


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
    "identified_community": "Article 29(1) read with the relative clause only picking out which community is meant, not asserting "
                            "anything of it: every person has duties to the community the sentence identifies for that person (the "
                            "base relation 'community identified for', the open term community_of_full_development); whether "
                            "development is possible only there is left to the open term and not asserted. The existence of the "
                            "community and of the duties is asserted.",
}
U110_MODELS = {
    # name: (persons, communities, owes, possible, identified); the three readings' truth values: (per_person, one_for_all, identified)
    "m1": (["p0", "p1"], ["c0", "c1"], [["p0", "c0"], ["p1", "c1"]], [["p0", "c0"], ["p1", "c1"]], [], (True, False, False)),
    "m2": (["p0"], ["c0"], [["p0", "c0"]], [["p0", "c0"]], [], (True, True, False)),
}


def main():
    raw = (HERE.parent / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = P.read(HERE / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    units = {u["id"]: u for u in meta["units"]}
    sets = {s["unit"]: deepcopy(s) for s in meta["reading_sets"]}

    # ---- the main environment grows the community vocabulary; every set's ids move with it
    vocabulary(meta)
    env = _environment(meta["environment"])
    for uid in list(sets):
        sets[uid] = P._reidentified(env, sets[uid])
    model_env, _ = _reading_evaluation(env)
    shared_id, shared_model = next(iter(sets["u112"]["models"].items()))

    # ---- companions
    for uid, cids in R.REMOVED.items():
        for cid in cids:
            (READINGS / f"{uid}.{cid}.ve.md").unlink(missing_ok=True)
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

    # ---- the norm-candidate sets
    order_of = {"u099a": ["state", "unassigned"], "u099b": ["state", "unassigned"],
                "u100a": ["state", "education", "unassigned"], "u100b": ["state", "education", "unassigned"],
                "u105c": ["entitlement", "state_negative", "anyone_negative", "state_positive", "state_combined", "liberty"]}
    for uid, order in order_of.items():
        s = sets[uid]
        old_ids = [r["id"] for r in s["readings"]]
        by_id = {r["id"]: r for r in s["readings"]}
        why = {c[0]: c[2] for c in R.NEW_CANDIDATES.get(uid, [])}
        if s["models"]:
            model_id = next(iter(s["models"]))
        else:
            model_id = shared_id
            s["models"] = {shared_id: shared_model}
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
        assert len(readings) > 1 and len(s["models"]) == 1, (uid, list(s["models"]))
        s["version"] += 1
        s["rejected_history"] = [*s.get("rejected_history", []),
                                 {"version": s["version"] - 1, "readings": old_ids,
                                  "reason": f"{NOTE}; repaired 2026-10-07T1800Z: {R.REASON[uid]}."}]
        for r in readings:
            path = READINGS / f"{uid}.{r['id']}.ve.md"
            assert load_document(path)["units"][0]["meaning_id"] == r["meaning_id"], (uid, r["id"])

    # ---- u110: three asserted readings over the community vocabulary
    s = sets["u110"]
    old_ids = [r["id"] for r in s["readings"]]
    formulas = u110_formulas()
    models = {}
    truth = {}
    for name, (persons, communities, owes, poss, ident, values) in U110_MODELS.items():
        base = deepcopy(next(iter(sets["u112"]["models"].values())))
        base["domains"]["person"], base["domains"]["community"] = persons, communities
        base["relations"][OWES], base["relations"][POSS], base["relations"][IDENT] = owes, poss, ident
        mid = FiniteModel.from_dict(model_env, base).model_id
        models[mid] = base
        truth[name] = (mid, dict(zip(("per_person", "one_for_all", "identified_community"), values)))
    mid = {n: truth[n][0] for n in truth}
    pick = {("per_person", "one_for_all"): "m1", ("per_person", "identified_community"): "m1",
            ("one_for_all", "identified_community"): "m2"}
    readings = []
    for cid, data in formulas.items():
        others = [o for o in formulas if o != cid]
        dm = {}
        for o in others:
            name = pick.get((cid, o)) or pick[(o, cid)]
            assert truth[name][1][cid] != truth[name][1][o], (cid, o, name)
            dm[o] = mid[name]
        readings.append({"id": cid, "kind": "asserted", "content": data,
                         "meaning_id": meaning_id(env, formula_from_data(env, data)),
                         "admission": {"who": "translator", "why": U110_WHY[cid], "distinguishing_models": dm}})
    s["readings"], s["models"] = readings, models
    s["version"] += 1
    s["rejected_history"] = [*s.get("rejected_history", []),
                             {"version": s["version"] - 1, "readings": old_ids,
                              "reason": f"{NOTE}; repaired 2026-10-07T1800Z: {R.REASON['u110']}."}]
    units["u110"]["kind"] = "asserted"      # every reading of the sentence is an assertion now (the norm readings are gone)
    for cid in R.REMOVED["u110"]:
        assert not (READINGS / f"u110.{cid}.ve.md").exists()

    meta["reading_sets"] = [sets[u["id"]] for u in meta["units"] if u["id"] in sets]
    P.write(HERE / "translation.ve.md", meta, raw)
    (HERE / "witnesses_repaired5.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("wrote translation.ve.md")


if __name__ == "__main__":
    main()
