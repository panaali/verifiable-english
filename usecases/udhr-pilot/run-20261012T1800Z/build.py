"""Build the 2026-10-04T0600Z UDHR translation at ve-green-env-profiles from the previous run's translation.

Merged since the previous baseline (ve-green-wire-s4): infra/layers2-b1 (layer checks, no language change) and
fix/env-field-types (environment profile fields on the block routes). Neither gives the translator anything new for the
UDHR, so this run measures the language as it was and spends its work on the previous audit:

  1. the 2026-10-03 audit rejected nine sampled units; eight for the same reason: a candidate that declares the
     completion `deny` (or `permission deny`) asserts 'not required' / 'not permitted' where the source is silent
     (the other reasons: unconstrained defeasible twins of 'shall', an open factor for explicit punishment, 'private
     life' for four named domains, an Article 22 clause as an unconstrained exception, no liberty candidate for 'freely
     to enjoy the arts', a guard that empties the duty of 'everyone has duties');
  2. every unit that carried the same defect (readings@1 or rights@0 content: 39 units) is re-stated as norm-defaults@0
     companion documents with the completion `unspecified` (readings@1 content refuses norm-defaults@0), strict force
     only, explicit enumerations as checked structure (udhr_specs.py), and the main document drops rights@0, soft-norms@0
     and readings@1, because no unit needs them any more;
  3. u017 ('should ...') loses its defeasible candidate: soft-norms@0 refuses norm-defaults@0, so the unit is
     UNFORMALISED (defaults) with its strict companion kept as a partial reading;
  4. u111 loses its four defeasible candidates (no stated exception); u110 gets two readings of its relative clause.

    uv run --frozen python usecases/udhr-pilot/run-20261004T0600Z/build.py
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

import blockers as B  # noqa: E402
import companions_nd as ND  # noqa: E402
import force_table as T  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.document import _environment, check_document, load_document  # noqa: E402

PREV = HERE.parent / "run-20261003T0600Z"
SOURCE = HERE.parent / "source" / "udhr.md"
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
READINGS = HERE / "readings"
PARTIAL = HERE / "readings-partial"

NEW_UNITS = [u for u in U.CANDIDATES if u != "u110"]            # the 39 units that carried deny completions
AUDIT_REJECTED = {                                                # 2026-10-03T0600Z audit, run-20261003T0600Z/AUDIT.md
    "u048", "u105b", "u081", "u045a", "u025", "u027", "u110", "u098", "u017"}
KEPT_COMPANIONS = ["u035", "u051", "u054", "u061", "u077", "u052", "u112", "u114", "u074"]

REJECTION = {
    "u017": "Rejected 2026-10-03T0600Z: the defeasible companion declares the completion 'deny' (not required), which the source does "
            "not state. soft-norms@0 cannot sit beside norm-defaults@0 ('unspecified'), so the defeasible reading of 'should' is not "
            "expressible without that invented completion: the unit is UNFORMALISED (defaults); the strict reading is kept as a "
            "partial companion (readings-partial/).",
    "u110": "Rejected 2026-10-03T0600Z: the sole-development relation became a guard, so where it is empty nobody has an operative "
            "duty although the source says everyone has duties; the relative clause's content is lost. Repaired: two readings, the "
            "clause as a restriction (guard, as before) and as a description of the one community (no guard).",
}
ADMISSIBLE_NOTE = (
    "Replaced after the 2026-10-03 audit. The previous candidates declared the completion 'deny' (rights@0 and readings@1 content "
    "refuse norm-defaults@0's 'unspecified'), which asserts 'not required' (or 'not permitted') where the source is silent, and "
    "offered a defeasible twin of every 'shall' and of Articles 22-27's rights although the text states no exception. The audit "
    "rejected eight of eight sampled units of this kind (u048, u105b, u081, u045a, u025, u027, u098; u017 for the same completion); "
    "this unit had the same defect and is re-stated, pending a fresh audit.")


def sha(raw):
    assert hashlib.sha256(raw).hexdigest() == PIN
    return raw


def trimmed_environment(env):
    """The main document needs neither rights@0, soft-norms@0 nor readings@1 any more."""
    env = deepcopy(env)
    env["profiles"] = ["documents@1", "norms@0", "relational-fol@0"]
    vocab = env["vocabulary"]
    vocab.pop("rights", None)
    keep = {"compel_association_membership_permitted"}
    vocab["predicates"] = {n: p for n, p in vocab["predicates"].items()
                           if ("regulated" not in p and n not in ("is_state", "of_age_for_elementary_education")) or n in keep}
    return env


def filtered_models(item, env):
    from ve.readings import _reading_evaluation
    model_env, _ = _reading_evaluation(env)
    out = {}
    for old, data in item.get("models", {}).items():
        out[old] = {**data, "domains": {k: v for k, v in data["domains"].items() if k in model_env.model_sorts},
                    "relations": {k: v for k, v in data["relations"].items() if k in model_env.predicates}}
    return {**item, "models": out}


def candidate_row(cid, meaning_id, why, others, model_id):
    return {"id": cid, "kind": "norm", "meaning_id": meaning_id, "content": None,
            "admission": {"who": "translator", "why": why, "distinguishing_models": {o: model_id for o in others if o != cid}}}


def main():
    raw = sha(SOURCE.read_bytes())
    meta, source = P.read(PREV / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    units = {u["id"]: u for u in meta["units"]}
    spans = {i: u["span"] for i, u in units.items()}

    # ---- environment and the surviving sets
    meta["environment"] = trimmed_environment(meta["environment"])
    env = _environment(meta["environment"])
    drop = set(NEW_UNITS) | {"u017", "u110"}
    surviving = {}
    for item in meta["reading_sets"]:
        if item["unit"] in drop:
            continue
        surviving[item["unit"]] = P._reidentified(env, filtered_models(item, env))
    model_id, model = next(iter(surviving["u054"]["models"].items()))
    previous = {s["unit"]: s for s in meta["reading_sets"]}

    # ---- open terms
    have = {t["name"] for t in meta["open_terms"]}
    for name, factors in {**U.OPEN_NEW}.items():
        if name not in have:
            meta["open_terms"].append({"arguments": [], "decided_by": "unstated", "factors": factors,
                                       "jurisdiction": "universal", "name": name, "necessary": [], "precedents": [],
                                       "sufficient": [], "version": 1})

    # ---- companions: the kept ones are copied, the new ones are written, loaded and checked
    for d in (READINGS, PARTIAL):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    for unit in KEPT_COMPANIONS:
        for path in (PREV / "readings").glob(f"{unit}.*.ve.md"):
            shutil.copy(path, READINGS / path.name)
    for path in (PREV / "readings").glob("u111.*.ve.md"):
        if path.name.split(".")[1].startswith("strict_"):
            shutil.copy(path, READINGS / path.name)
    shutil.copy(PREV / "readings" / "u017.strict.ve.md", PARTIAL / "u017.strict.ve.md")

    ids, witnesses, checks = {}, {}, {}
    for unit, cands in U.CANDIDATES.items():
        a, b = spans[unit]
        for cid, spec, _why in cands:
            path = U.write_companion(READINGS, unit, cid, spec, raw[a:b], meta["open_terms"])
            ids[(unit, cid)] = load_document(path)["units"][0]["meaning_id"]
            verdict = check_document(path)
            assert verdict["premises"]["status"] == "model", (unit, cid, verdict["premises"])
            outs = WND.run(path, spec)
            assert all(o["as_expected"] for o in outs), (unit, cid, [o for o in outs if not o["as_expected"]])
            witnesses[f"{unit}.{cid}"] = outs
            checks[f"{unit}.{cid}"] = verdict["premises"]["status"]
    print("companions written and checked:", len(ids), flush=True)

    # ---- new sets
    sets = dict(surviving)
    for unit, cands in U.CANDIDATES.items():
        cids = [c[0] for c in cands]
        readings = [candidate_row(cid, ids[(unit, cid)], why, cids, model_id) for cid, _spec, why in cands]
        prev = previous.get(unit)
        history = list(prev.get("rejected_history", [])) if prev else []
        if prev:
            history.append({"version": prev["version"], "readings": [r["id"] for r in prev["readings"]],
                            "reason": REJECTION.get(unit, ADMISSIBLE_NOTE)})
        sets[unit] = {"id": f"rs_{unit}", "unit": unit, "version": (prev["version"] + 1) if prev else 1, "status": "open",
                      "models": {model_id: model}, "readings": readings,
                      **({"rejected_history": history} if history else {})}
    # u111: only the strict candidates survive (the text states no exception to 'shall')
    u111 = surviving["u111"]
    keep = [r for r in u111["readings"] if r["id"].startswith("strict_")]
    dropped = [r["id"] for r in u111["readings"] if not r["id"].startswith("strict_")]
    for r in keep:
        r["admission"]["distinguishing_models"] = {o: m for o, m in r["admission"]["distinguishing_models"].items()
                                                   if o.startswith("strict_")}
        r["admission"]["why"] = r["admission"]["why"].replace("'shall' read as a strict duty ('must')",
                                                                "'shall' read as a strict duty ('must'; the text states no exception)")
    sets["u111"] = {**u111, "readings": keep, "version": u111["version"] + 1,
                    "rejected_history": [*u111.get("rejected_history", []),
                                         {"version": u111["version"], "readings": dropped,
                                          "reason": "Removed 2026-10-04: the four defeasible candidates (soft-norms@0, completion 'deny' = "
                                                    "not required) added an exception the text does not state and a completion the source "
                                                    "does not state; 'shall' keeps only its strict reading."}]}
    meta["reading_sets"] = [sets[u["id"]] for u in meta["units"] if u["id"] in sets]

    # ---- units
    for uid in NEW_UNITS + ["u110"]:
        unit = units[uid]
        opens = sorted({t for _c, spec, _w in U.CANDIDATES[uid] for t in spec["open"]})
        unit["kind"] = "norm"
        unit["meaning"] = {"open": opens} if opens else "specified"
    units["u017"]["kind"] = ["unformalised", "defaults"]
    units["u017"]["meaning"] = {"unformalised": "defaults"}

    out = HERE / "translation.ve.md"
    P.write(out, meta, raw)
    (HERE / "witnesses.json").write_text(json.dumps({"norm_defaults_status": witnesses}, ensure_ascii=False, indent=2,
                                                    sort_keys=True) + "\n")
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
