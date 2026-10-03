"""Build the 2026-10-03T0600Z UDHR translation at ve-green-wire-s4 from the previous run's translation.

The previous run (prev-run-20261002T1800Z, language ve-green-wire) left 43 units UNFORMALISED because a strict and a
defeasible reading could not share a reading set (other:force_variants_in_one_reading_set), and 4 because a reading
set candidate could only be a whole right block (other:right_lines_in_reading_sets). Composition S1 (merged between
the two tags) admits content-bearing candidates, strict and default readings of one rule in one set, with one
checked situation per pair. This build:

  1. turns readings@1 on and re-identifies the previous run's sets over the new environment (nothing else about
     them changes; the norm-defaults companions cannot be merged: their completion `unspecified` is refused outside
     norm-defaults@0, which readings@1 content refuses to sit beside);
  2. states the units of force_table.py as open sets of strict/default candidates (force_table.py explains the axes);
  3. finds one separating situation per pair with Python's search (Lean checks each when the document loads);
  4. leaves every other unit as it was and gives each unit that is still UNFORMALISED its remaining blocker.

    uv run --frozen python usecases/udhr-pilot/run-20261003T0600Z/build.py [--only u024,u084d] [--out DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import blockers as B  # noqa: E402
import companions_nd as ND  # noqa: E402
import force_table as T  # noqa: E402
import s1doc as S  # noqa: E402
import witnesses_nd as WND  # noqa: E402

ROOT = S.ROOT
P = S.P
from ve.document import _environment  # noqa: E402
from ve.readings import s1_content_meaning_id  # noqa: E402

PREV = HERE.parent / "prev-run-20261002T1800Z"
SOURCE = HERE.parent / "source" / "udhr.md"
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
IS_STATE_ARG = {2: ["unary", "is_state", ["var", 1]], 1: ["unary", "is_state", ["var", 0]]}


def norm_node(name, predicate, arity, bearer, force, factors=()):
    guard = IS_STATE_ARG[arity] if bearer == T.STATE else ["top"]
    node = {"name": name, "predicate": predicate, "sign": True, "guard": guard, "unless": [], "over": []}
    if force == "default":
        node["mode"] = "default"
        node["exception"] = {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": list(factors)}
    return node


def sentence(act, who, holder="the person"):
    return act[len("{0} "):].replace("{1}", holder)


def describe(force, who, act, extra, word):
    strict_word = f"'{word}' read as 'must'" if word else "the source carries or opens its force"
    default_word = f"'{word}' read as 'should'" if word else "the source carries or opens its force"
    if force == "strict":
        text = (f"Strict reading ({strict_word}): {who} must {act}. The source names no bearer, so the bearer is the "
                "translator's candidate. Outside this rule the declared completion is 'deny' (not required): it "
                "grants no permission to anyone and is not stated by the source.")
    else:
        text = (f"Defeasible reading ({default_word}): {who} must {act} unless this rule's exception applies; the "
                "source names no decider (decided_by unstated). The declared completion is 'deny' (not required), "
                "as for the strict reading: not stated by the source, grants no permission to anyone.")
    return text + extra


def who_text(bearer):
    return {"state": "every state", "anyone": "every state, group and person", None: "each person"}[bearer]


def new_sets(raw, units, only):
    """Return (predicates, open_terms, sets, row notes) for the units of force_table.py."""
    predicates, sets, notes = {}, [], {}
    spans = {u["id"]: u["span"] for u in units}
    chosen = [u for u in list(T.NORM_UNITS) + list(T.RIGHT_UNITS) if only is None or u in only]
    for uid in chosen:
        span = spans[uid]
        if uid in T.NORM_UNITS:
            e = T.NORM_UNITS[uid]
            cands = []
            for rid, stem, act, args, bearers, axis, *extra in e["readings"]:
                guard_pred = extra[0] if extra else None
                if guard_pred:
                    predicates[guard_pred[0]] = {"arguments": [args[-1]], "description": guard_pred[1],
                                                 "verbalisation": guard_pred[2]}
                predicates[stem] = {
                    "arguments": list(args),
                    "description": (("The bearer" if args[0] == "bearer" else "The person") + " is required to "
                                    + sentence(act, "", "the person") + f". Source clause: {e['full']}."),
                    "regulated": {"role": "obligation", "default": "deny", "act": act}}
                for bearer in bearers:
                    for force in ("strict", "default"):
                        name = f"{e['name']}-{rid}" + (f"-{bearer}" if bearer else "")
                        node = norm_node(name, stem, len(args), bearer, force)
                        if guard_pred:
                            node["guard"] = ["unary", guard_pred[0], ["var", 0]]
                        cid = f"{rid}_{bearer}_{force}" if bearer else f"{rid}_{force}"
                        labels = {"force": force}
                        if bearer:
                            labels["bearer"] = bearer
                        if axis:
                            labels["duty"] = axis
                        who = who_text(bearer)
                        cands.append({"id": cid, "kind": "norm", "content": {"norm": node}, "labels": labels,
                                      "why": describe(force, who, sentence(act, who, "each person"),
                                                      (f" Scope: only where {guard_pred[2].replace('{0}', 'the person')} "
                                                       "(a named open relation; the source states no age).")
                                                      if guard_pred else "", e["word"])})
            word = None
            if e["word"]:
                at = raw[span[0]:span[1]].find(e["word"].encode())
                assert at >= 0, (uid, e["word"])
                word = [span[0] + at, span[0] + at + len(e["word"])]
            sets.append({"id": f"rs_{uid}", "unit": uid, "version": 1, "status": "open", "readings": cands,
                         **({"source_word": word} if word else {})})
            notes[uid] = e
        else:
            e = T.RIGHT_UNITS[uid]
            duties = [(p, e["neg"] if p == "negative" else e["pos"], "avoid" if p == "negative" else "secure")
                      for p in ("negative", "positive") if e["polarity"] in ("both", p)]
            for pol, act, stem in duties:
                predicates[f"{stem}_{e['key']}_required"] = {
                    "arguments": ["bearer", "person"],
                    "description": "The bearer is required to " + sentence(act, "", "the person")
                                   + f". Source clause: {e['full']}.",
                    "regulated": {"role": "obligation", "default": "deny", "act": act}}
            cands = []
            for bearer in (T.STATE, T.ANYONE):
                for pol, act, stem in duties:
                    for force in ("strict", "default"):
                        node = norm_node(f"{stem}-{e['right']}-by-{bearer}", f"{stem}_{e['key']}_required", 2, bearer, force,
                                         factors=[T.ARTICLE_22_FACTOR] if e["article"] in (
                                             "Article 22", "Article 23", "Article 26", "Article 27") else [])
                        line = {"kind": "claim", "holder_slot": None, "cites": {}, "norm": node}
                        cid = (f"{bearer}_{pol}_{force}" if e["polarity"] == "both" else f"{bearer}_claim_{force}")
                        labels = {"incident": "claim", "bearer": bearer, "force": force}
                        if e["polarity"] == "both":
                            labels["polarity"] = pol
                        who = who_text(bearer)
                        extra = (" The duty is to avoid harming the right." if pol == "negative" and e["polarity"] == "both"
                                 else " The duty is to secure the right." if e["polarity"] == "both" else
                                 " The right's one duty.")
                        if force == "default":
                            extra += (" The exception's factor is the organization and resources of each State, from "
                                      "Article 22 (the translator's cross-reference, not a checked one).")
                        cands.append({"id": cid, "kind": "right", "labels": labels,
                                      "content": {"right": {"name": e["right"], "holder": "person", "guard": ["top"],
                                                            "lines": [line]}},
                                      "why": "Claim reading, " + describe(force, who, sentence(act, who, "each holder"),
                                                                           extra, None)})
            sets.append({"id": f"rs_{uid}", "unit": uid, "version": 1, "status": "open", "readings": cands})
            notes[uid] = e
    return predicates, sets, notes


# ---------------------------------------------------------------- the four units the previous audit rejected
REPAIRED = {"u035": ["tribunal_claim", "state_claim"], "u054": ["claim", "liberty"],
            "u051": ["liberty", "state_avoid", "anyone_avoid"], "u111": list(ND.U111_SPECS)}
READINGS_DIR = HERE / "readings"
AUDIT_1800 = {
    "u035": "Rejected 2026-10-02T1800Z (the duties covered each violating act but had no victim argument, so a remedy "
            "for one victim could satisfy the duty while another victim of the same act received none). Repaired: the "
            "regulated argument is a violation, one violation of one person's right by one act (its victim is its own), "
            "and the act phrase names the victim ('provide the victim of {1} with an effective remedy'). Pending a fresh "
            "independent audit.",
    "u054": "Rejected 2026-10-02T1800Z (the claim made the person obliged to receive a nationality; a right to a "
            "nationality does not oblige its holder to accept one). Repaired: the claim is a duty on whichever bearer owes "
            "the person a nationality, through the base relation owes_nationality_to (open term "
            "bearer_of_the_nationality_duty), so the duty never sits on the holder and no bearer is invented; the liberty "
            "reading is unchanged. Pending a fresh independent audit.",
    "u051": "Rejected 2026-10-02T1800Z (the noninterference duties applied only to someone already seeking or enjoying "
            "asylum, leaving a person's opportunity to begin seeking it outside them). Repaired: the guard is the person's "
            "exposure to persecution, suffered or threatened (open term persecution), whether or not the person has begun "
            "to seek asylum; the liberty reading is unchanged. Pending a fresh independent audit.",
    "u111": "Rejected 2026-10-02T1800Z (the readings obliged every person to be free of each deficient limitation, tied no "
            "limitation to the affected person or to a particular right, and put the obligation on the right holder). "
            "Repaired: the duty is on a bearer (a State, or any State, group or person) who must avoid imposing a limitation; "
            "a limitation is one limitation on one person's exercise of one right or freedom, so the affected person and "
            "the right are its own. A relation from a limitation to a rights line is still not expressible (limitation "
            "scope names rights, which are open sets here; S2). Eight candidates: two readings of 'and' between the aims, "
            "strict or defeasible, state or any bearer. Pending a fresh independent audit.",
}
U111_WHY = {
    "listed": "'solely for the purpose of securing A and of meeting B' read as one or both of the two listed aims, and no other",
    "both": "'solely for the purpose of securing A and of meeting B' read as requiring both aims",
}
WHY_REPAIRED = {
    ("u035", "tribunal_claim"): "Article 8 read as a duty on a competent national tribunal to provide the victim of a violation "
        "of a fundamental right granted by the constitution or by law with an effective remedy. Both conditions are guards on "
        "the violation (one person's right violated by one act), so each victim of an act is owed a remedy. Strict force "
        "(readings/u035.tribunal_claim.ve.md).",
    ("u035", "state_claim"): "Article 8 read as a duty on a State to ensure that competent national tribunals give the victim of "
        "such a violation an effective remedy (same guard). Strict force (readings/u035.state_claim.ve.md).",
    ("u054", "claim"): "Article 15(1) read as an entitlement: whichever bearer owes the person a nationality must grant it. The "
        "source names no bearer, so who owes it is the open relation owes_nationality_to; the duty is never on the person and "
        "the right is not read as already fulfilled (readings/u054.claim.ve.md).",
    ("u054", "liberty"): "Article 15(1) read as a liberty: each person is permitted to have a nationality (readings/u054.liberty.ve.md).",
    ("u051", "liberty"): "Article 14(1) read as a liberty: a person may seek and enjoy asylum from persecution in other countries "
        "(the unconditional permission names no other case) (readings/u051.liberty.ve.md).",
    ("u051", "state_avoid"): "Article 14(1) read as a duty on every State to avoid barring a person who suffers or is threatened "
        "with persecution from seeking as well as enjoying asylum in other countries; the guard does not require the person to "
        "have begun seeking. No positive duty to grant asylum is a candidate (readings/u051.state_avoid.ve.md).",
    ("u051", "anyone_avoid"): "As state_avoid, bound on every State, group and person (the source names no bearer) "
        "(readings/u051.anyone_avoid.ve.md).",
}
for _force in ("strict", "default"):
    for _aims in ("listed", "both"):
        for _bearer in ("state", "anyone"):
            WHY_REPAIRED[("u111", f"{_force}_{_aims}_aims_{_bearer}")] = (
                f"Article 29(2): {U111_WHY[_aims]}; 'shall' read as "
                + ("a strict duty ('must')" if _force == "strict" else
                   "a defeasible rule ('should': soft-norms@0 companion, exception decided by no stated decider, declared completion 'deny' = not required)")
                + f"; the duty is on "
                + ("every State" if _bearer == "state" else "every State, group and person")
                + " to avoid imposing a limitation that is not determined by law or not solely for these aims. The conditions are "
                  "necessary, never sufficient: a limitation that meets them stays UNDECIDED "
                + f"(readings/u111.{_force}_{_aims}_aims_{_bearer}.ve.md).")


def write_repaired_companions(meta, raw):
    """Companion documents of the repaired units, their status witnesses and checks; returns {(unit, candidate): meaning id}."""
    from ve.document import check_document, load_document
    for old in READINGS_DIR.glob("u111.*.ve.md"):
        old.unlink()
    spans = {u["id"]: u["span"] for u in meta["units"]}
    have = {t["name"] for t in meta["open_terms"]}
    meta["open_terms"].extend(t for t in ND.NEW_OPEN_TERMS if t["name"] not in have)
    ids, witnesses = {}, {}
    for uid, cids in REPAIRED.items():
        a, b = spans[uid]
        for cid in cids:
            path = ND.write_companion(READINGS_DIR, uid, cid, raw[a:b], meta["open_terms"])
            ids[(uid, cid)] = load_document(path)["units"][0]["meaning_id"]
            verdict = check_document(path)
            assert verdict["premises"]["status"] == "model", (uid, cid, verdict["premises"])
            spec = ND.SPECS[uid][cid]
            if not spec.get("soft"):
                outs = WND.run(path, spec)
                assert all(o["as_expected"] for o in outs), (uid, cid, outs)
                witnesses[f"{uid}.{cid}"] = outs
    return ids, witnesses


def repaired_sets(meta, ids):
    sets = {s["unit"]: s for s in meta["reading_sets"]}
    for uid, cids in REPAIRED.items():
        prev = sets[uid]
        model_id, wire = next(iter(prev["models"].items()))
        readings = [{"id": cid, "kind": "norm", "meaning_id": ids[(uid, cid)], "content": None,
                     "admission": {"who": "translator", "why": WHY_REPAIRED[(uid, cid)],
                                   "distinguishing_models": {o: model_id for o in cids if o != cid}}} for cid in cids]
        history = list(prev.get("rejected_history", [])) + [{
            "version": prev["version"], "readings": [r["id"] for r in prev["readings"]],
            "reason": AUDIT_1800[uid].split(" Repaired:")[0]}]
        sets[uid] = {"id": prev["id"], "unit": uid, "version": prev["version"] + 1, "status": "open",
                     "models": {model_id: wire}, "readings": readings, "rejected_history": history}
    meta["reading_sets"] = [sets[s["unit"]] for s in meta["reading_sets"]]
    unit_meaning = {"u054": ["bearer_of_the_nationality_duty"]}
    for u in meta["units"]:
        if u["id"] in unit_meaning:
            u["meaning"] = {"open": unit_meaning[u["id"]]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--out", default=str(HERE))
    args = ap.parse_args(argv)
    only = set(args.only.split(",")) if args.only else None
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = S.read(PREV / "translation.ve.md")
    assert source == raw
    meta = deepcopy(meta)
    unit_by_id = {u["id"]: u for u in meta["units"]}
    preds, sets, notes = new_sets(raw, meta["units"], only)

    vocab = meta["environment"]["vocabulary"]
    assert not set(preds) & set(vocab["predicates"]), set(preds) & set(vocab["predicates"])
    vocab["predicates"].update(preds)
    have = {t["name"] for t in meta["open_terms"]}
    for name, factors in T.OPEN_TERMS.items():
        used = any(name in e["open"] for uid, e in notes.items())
        if used and name not in have:
            meta["open_terms"].append({"arguments": [], "decided_by": "unstated", "factors": factors,
                                       "jurisdiction": "universal", "name": name, "necessary": [], "precedents": [],
                                       "sufficient": [], "version": 1})
    for uid, e in notes.items():
        unit = unit_by_id[uid]
        unit["kind"] = e["kind"]
        unit["meaning"] = {"open": e["open"]} if e["open"] else "specified"
    for uid, (tag, _feature, _detail) in B.BLOCKERS.items():
        unit = unit_by_id[uid]
        assert unit["kind"][0] == "unformalised", uid
        unit["kind"] = ["unformalised", tag]
        unit["meaning"] = {"unformalised": tag}
    ids, nd_witnesses = write_repaired_companions(meta, raw)
    repaired_sets(meta, ids)
    meta["environment"] = P.with_readings(meta["environment"])
    env = _environment(meta["environment"])

    # previous sets re-identified over the new environment
    old = []
    for item in meta["reading_sets"]:
        if not S.bearing(item):
            old.append(P._reidentified(env, item))
            continue
        item = {k: v for k, v in item.items() if k != "models"}
        readings = [{**r, "meaning_id": P._identity(env, item["id"], r)} for r in item["readings"]]
        for r in readings:
            r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in readings if o["id"] != r["id"]}
        old.append({**item, "readings": readings})
    fresh = []
    for item in sets:
        readings = []
        for c in item["readings"]:
            r = {"id": c["id"], "kind": c["kind"], "content": c["content"], "labels": c["labels"]}
            r["meaning_id"] = s1_content_meaning_id(env, item["id"], r)
            r["admission"] = {"who": "translator", "why": c["why"], "distinguishing_models": {}}
            readings.append(r)
        for r in readings:
            r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in readings if o["id"] != r["id"]}
        fresh.append({**item, "readings": readings})
    meta["reading_sets"] = old + fresh

    started = time.monotonic()
    meta, missing, limits = P.find_situations(meta)
    print(f"search {time.monotonic() - started:.1f}s missing={missing} limits={limits}", flush=True)
    path = out / "translation.ve.md"
    S.write(path, meta, raw)
    (out / "witnesses.json").write_text(json.dumps({"norm_defaults_status": nd_witnesses}, ensure_ascii=False, indent=2,
                                                   sort_keys=True) + "\n")
    print("wrote", path, flush=True)
    return meta


if __name__ == "__main__":
    main()
