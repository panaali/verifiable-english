"""Rebuild the UDHR measurement at ve-green-bluedot2 from the pinned prior run, without model calls.

Starts from prev/ (the 2026-09-29T1800Z translation, unchanged bytes), replays the 2026-09-30 and 2026-10-01 changes
(rights@0 units, repairs) and applies what the 2026-10-02 run adds:
  1. the repairs the 2026-10-01T1800Z audit demanded (it rejected u051, u035, u039, u077);
  2. norm-defaults@0 (merged 2026-10-01): norm candidates are companion documents with the `unspecified` completion and
     their scope in checked guards (companions_nd.py): u017 strict, u052, u112, u114 move their conditions back into
     guards; u035, u051, u077 are re-translated as norm readings (their right-block candidates were rejected); u039 does
     not fit the 80-byte act phrase and becomes UNFORMALISED; u074 gets an unspecified companion and a migration audit.
A document cannot enable norm-defaults@0 together with soft-norms@0 or rights@0 (ve/document.py), so the main document
keeps its rights@0 candidates with their declared completions; this is reported as a language limit.
Run from the worktree root's python (lark installed) with PATH=~/.elan/bin:$PATH so the Lean routes are found.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from table import HOLDER_SORTS, OPEN_TERMS, RIGHT_UNITS
import companions_nd as ND
import witnesses_nd as WND
from rights_sets import candidates, predicates_for
from ve.document import _environment, check_document, coverage, load_document, render_document
from ve.english import lint_english_vocabulary
from ve.readings import _right_situation, rights_meaning_id
from ve.rights import RightsDocument

SOURCE = HERE.parent / "source" / "udhr.md"
PREV = HERE / "prev"
LAST = HERE / "prev1002"  # the 2026-10-02T0600Z run (ve-green-bluedot2): its metrics, audit and units are the comparison baseline
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == PIN

prior = (PREV / "translation.ve.md").read_bytes()
front, body = prior[4:].split(b"\n---\n", 1)
assert body == raw
meta = json.loads(front)
rows = json.loads((PREV / "units.json").read_text())["units"]
old_metrics = json.loads((PREV / "metrics.json").read_text())
assert len(meta["units"]) == len(rows) == 129
by_id = {r["id"]: r for r in rows}
unit_by_id = {u["id"]: u for u in meta["units"]}


def sort(singular, plural, description):
    return {"description": description, "verbalisation": {"singular": singular, "plural": plural}}


# ---------------------------------------------------------------- open terms: no invented deciders
decider_changes = {t["name"]: t["decided_by"] for t in meta["open_terms"] if t["decided_by"] != "unstated"}
for t in meta["open_terms"]:
    t["decided_by"] = "unstated"


def open_term(name, factors):
    return {"arguments": [], "decided_by": "unstated", "factors": factors, "jurisdiction": "universal",
            "name": name, "necessary": [], "precedents": [], "sufficient": [], "version": 1}


have = {t["name"] for t in meta["open_terms"]}
for name, factors in OPEN_TERMS.items():
    if name not in have:
        meta["open_terms"].append(open_term(name, factors))

# ---------------------------------------------------------------- environment
env_json = meta["environment"]
env_json["profiles"] = sorted(set(env_json["profiles"]) | {"soft-norms@0", "rights@0"})
vocab = env_json["vocabulary"]
for gone in ("genuinely_prosecuted_for_non_political_crime", "genuinely_prosecuted_for_acts_contrary_to_un",
             "entitled_to_asylum", "exercises_contrary_to_un", "right_protects_exercise"):
    del vocab["predicates"][gone]  # person-level formulas the 2026-09-29 audit rejected (u052, u112)
del vocab["sorts"]["right"]
vocab["sorts"]["prosecution"] = sort("prosecution", "prosecutions", "a prosecution of a person")
vocab["sorts"]["exercise"] = sort("exercise", "exercises",
                                  "one exercise of a right or freedom by a person on one occasion")
vocab["predicates"].update({
    "arises_from_non_political_crime": {"arguments": ["prosecution"], "description":
        "The prosecution genuinely arises from a non-political crime"},
    "arises_from_acts_contrary_to_un": {"arguments": ["prosecution"], "description":
        "The prosecution genuinely arises from acts contrary to the purposes and principles of the United Nations"},
    "asylum_right_covers_case": {"arguments": ["prosecution"], "description":
        "The right to seek and to enjoy asylum (Article 14, paragraph 1) may be invoked in the case of the prosecution"},
    "exercise_contrary_to_un": {"arguments": ["exercise"], "description":
        "The exercise is contrary to the purposes and principles of the United Nations"},
    "right_protects_exercise": {"arguments": ["exercise"], "description":
        "The right or freedom protects the exercise"},
})
vocab["predicates"]["is_state"] = {"arguments": ["bearer"], "description": "The bearer is a state",
                                   "verbalisation": "{0} is a state"}
for name, (singular, plural, description) in HOLDER_SORTS.items():
    vocab["sorts"][name] = sort(singular, plural, description)
# (has_a_nationality and grants_nationality, the accomplished-fact predicates of u054, are dropped: audit 2026-10-02T0600Z)
vocab["rights"] = {"holders": sorted(["person", *HOLDER_SORTS]), "bearers": ["bearer"],
                   "protected": [], "alters": {}}
for uid, entry in RIGHT_UNITS.items():
    vocab["predicates"].update(predicates_for(uid, entry))

# ---------------------------------------------------------------- unit split: u022 becomes three units
old = unit_by_id["u022"]
a, b = old["span"]
text = raw[a:b].decode()
assert text == "Everyone has the right to life, liberty and security of person.\n\n"
cut1 = a + len("Everyone has the right to life")
cut2 = a + len("Everyone has the right to life, liberty")
pieces = [("u022a", a, cut1), ("u022b", cut1, cut2), ("u022c", cut2, b)]
index = meta["units"].index(old)
meta["units"][index:index + 1] = [
    {**copy.deepcopy(old), "id": uid, "span": [s, e]} for uid, s, e in pieces]
row_index = rows.index(by_id["u022"])
rows[row_index:row_index + 1] = [
    {**copy.deepcopy(by_id["u022"]), "id": uid, "span": [s, e], "source": raw[s:e].decode(),
     "previous_unit": "u022", "old_unit": "u022"} for uid, s, e in pieces]
by_id = {r["id"]: r for r in rows}
unit_by_id = {u["id"]: u for u in meta["units"]}

# ---------------------------------------------------------------- u111: one unit (u111a and u111b merged)
u111a, u111b = unit_by_id["u111a"], unit_by_id["u111b"]
merged = {**u111a, "id": "u111", "span": [u111a["span"][0], u111b["span"][1]], "kind": "norm",
          "meaning": {"open": ["determined_by_law", "due_recognition_and_respect", "just_requirements",
                               "morality", "public_order", "general_welfare", "democratic_society"]}}
merged.pop("content", None)  # the rights@0 limitation of the previous runs constrained no right (audit 2026-10-02T0600Z); the norm candidates are in readings/
meta["units"][meta["units"].index(u111a):meta["units"].index(u111b) + 1] = [merged]
old_a, old_b = by_id["u111a"], by_id["u111b"]
rows[rows.index(old_a):rows.index(old_b) + 1] = [{**old_a, "id": "u111", "span": merged["span"],
                                                   "source": raw[merged["span"][0]:merged["span"][1]].decode(),
                                                   "previous_unit": "u111", "old_unit": "u111"}]
by_id = {r["id"]: r for r in rows}
unit_by_id = {u["id"]: u for u in meta["units"]}

# ---------------------------------------------------------------- reading sets for the right units
renv = _environment(env_json)
sets = []


def situation_for(uid, contents):
    doc = RightsDocument(renv, [{"source_units": [uid]}, contents[0]])
    base = doc.soft_document.elaborated.base_environment()
    domains = {s: [f"{s[:1]}0"] for s in sorted(renv.sorts)}
    domains["bearer"] = ["b0", "b1"]  # b0 is a state, b1 is not: the state and anyone readings differ on b1
    relations = {n: [] for n in sorted(base.predicates)}
    relations["is_state"] = [["b0"]]
    wire = {"complete": True, "constants": {}, "domains": domains, "relations": relations}
    ids = {_right_situation(renv, c, wire, [uid])[0] for c in contents}
    assert len(ids) == 1, (uid, ids)
    return ids.pop(), wire


for uid, entry in RIGHT_UNITS.items():
    cands = candidates(uid, entry)
    contents = [c["content"] for c in cands]
    model_id, wire = situation_for(uid, contents)
    readings = []
    for c in cands:
        readings.append({
            "id": c["id"], "kind": "right", "labels": c["labels"], "content": c["content"],
            "meaning_id": rights_meaning_id(renv, c["content"]),
            "admission": {"who": "translator", "why": c["why"],
                          "distinguishing_models": {o["id"]: model_id for o in cands if o is not c}}})
    sets.append({"id": f"rs_{uid}", "unit": uid, "version": 1, "status": "open",
                 "models": {model_id: wire}, "readings": readings})
    unit = unit_by_id[uid]
    unit["kind"] = "right"
    unit["meaning"] = {"open": entry["open"]} if entry["open"] else "specified"


# ---------------------------------------------------------------- readings that are not right blocks (u017, u052, u112, u114)
U111_FACTORS = {
    "determined_by_law": ["what it is for a limitation to be determined by law"],
    "due_recognition_and_respect": ["what due recognition and respect for the rights and freedoms of others requires"],
    "just_requirements": ["which requirements are just"],
    "morality": ["whose morality", "which requirements of morality"],
    "public_order": ["what counts as public order"],
    "general_welfare": ["what counts as the general welfare"],
    "democratic_society": ["what makes a society democratic"]}
for name, factors in U111_FACTORS.items():
    if name not in {t["name"] for t in meta["open_terms"]}:
        meta["open_terms"].append(open_term(name, factors))
# u051 (2026-10-02T0600Z audit): persecution may be threatened and not yet suffered
for t in meta["open_terms"]:
    if t["name"] == "persecution" and "whether persecution that is only threatened counts" not in t["factors"]:
        t["factors"].append("whether persecution that is only threatened counts")

import companions as C
from ve.ast import Binary, Forall, Implies, Not, Or, Unary, Var, formula_to_data
from ve.identity import meaning_id
from ve.model import FiniteModel

meta["open_terms"].extend(t for t in [*C.NEW_OPEN_TERMS, *ND.NEW_OPEN_TERMS] if t["name"] not in {x["name"] for x in meta["open_terms"]})
V0 = Var(0)
FORMULAS = {
    ("u052", "case_excluded"): Forall("prosecution", Implies(
        Or(Unary("arises_from_non_political_crime", V0), Unary("arises_from_acts_contrary_to_un", V0)),
        Not(Unary("asylum_right_covers_case", V0)))),
    ("u112", "exercise_unprotected"): Forall("exercise", Implies(
        Unary("exercise_contrary_to_un", V0), Not(Unary("right_protects_exercise", V0)))),
    ("u114", "no_implied_right"): Forall("bearer", Not(Unary("declaration_implies_destructive_right", V0))),
}
FALSIFYING = {  # a finite situation in which the assertion reading is false
    "u052": {"arises_from_non_political_crime": [["p0"]], "asylum_right_covers_case": [["p0"]]},
    "u112": {"exercise_contrary_to_un": [["e0"]], "right_protects_exercise": [["e0"]]},
    "u114": {"declaration_implies_destructive_right": [["b0"]]},
}


def plain_model(relations):
    domains = {s: [f"{s[:1]}0"] for s in sorted(renv.sorts)}
    full = {name: [] for name in renv.predicates}
    full.update(relations)
    return {"complete": True, "constants": {}, "domains": domains, "relations": full}


OLD_SETS = {"u017": ["strict", "default"], "u052": ["invocation_barred", "case_excluded"],
            "u112": ["exercise_prohibited", "exercise_unprotected"], "u114": ["interpretive_ban", "no_implied_right"],
            "u035": ["tribunal_claim", "state_claim"], "u051": ["liberty", "state_avoid", "anyone_avoid"],
            "u077": ["nationality_country_claim", "residence_country_claim"],
            "u061": ["claim"], "u110": ["duty"],
            "u054": ["claim", "liberty"],
            "u111": ["strict_listed_aims", "strict_both_aims", "default_listed_aims", "default_both_aims"]}
NEWLY_EXPRESSIBLE = ["u061", "u110"]  # UNFORMALISED (norms) in the previous run
NEW_RESETS = {  # units whose reading set is new in this build: the rejected right-block candidates of 2026-10-01
    "u035": ["state_claim", "anyone_claim"],
    "u051": ["state_negative", "state_positive", "anyone_negative", "anyone_positive", "liberty"],
    "u077": ["state_claim", "anyone_claim"]}
REJECTED_REASON = {
    "u035": "rejected by the 2026-10-01T1800Z audit: the checked duty had no argument for the rights-violating act and its "
            "prose holder sort could not ensure an effective remedy for each qualifying violation",
    "u051": "rejected by the 2026-10-01T1800Z audit: the positive candidates required every bearer to grant asylum to every "
            "person and omitted seeking",
    "u077": "rejected by the 2026-10-01T1800Z audit: no checked relation connected a bearer to the holder's country, so the "
            "candidates bound unrelated bearers"}
WHY = {
    ("u017", "strict"): "Article 1 'should' read as a strict obligation on every human being to act towards each other "
                        "human being in a spirit of brotherhood (readings/u017.strict.ve.md).",
    ("u017", "default"): "Article 1 'should' read as a defeasible rule: the same obligation holds unless the rule's exception "
                         "applies, and the source names no decider (readings/u017.default.ve.md).",
    ("u052", "invocation_barred"): "Article 14(2) read as a prohibition on invoking the asylum right in the case of an "
                                   "excluded prosecution: the norm ranges over (person, prosecution) pairs of the sort "
                                   "excluded_prosecution, so it bars the invocation in that case and nothing else "
                                   "(readings/u052.invocation_barred.ve.md).",
    ("u052", "case_excluded"): "Article 14(2) read as a statement about the right's coverage: for every prosecution that "
                               "genuinely arises from a non-political crime or from acts contrary to UN purposes and "
                               "principles, the asylum right cannot be invoked in the case of that prosecution. A formula "
                               "over prosecutions in this document; it says nothing about a person's other cases.",
    ("u112", "exercise_prohibited"): "Article 29(3) read as an unconditional prohibition on carrying out an exercise "
                                     "contrary to UN purposes and principles (readings/u112.exercise_prohibited.ve.md).",
    ("u112", "exercise_unprotected"): "Article 29(3) read as a limit on the rights' scope: no right or freedom protects an "
                                      "exercise contrary to UN purposes and principles. A formula over single exercises "
                                      "(not persons), so one contrary exercise removes protection from that exercise only.",
    ("u114", "interpretive_ban"): "Article 30 read as a prohibition on interpreting the Declaration as implying, for any "
                                  "State, group or person, a right to destroy declared rights (readings/u114.interpretive_ban.ve.md).",
    ("u114", "no_implied_right"): "Article 30 read as a statement of the Declaration's content: it implies for no State, group "
                                  "or person a right to engage in any activity or act aimed at destroying any declared right.",
}
ND_WHY = {
    ("u017", "strict"): "Article 1 'should' read as a strict obligation on every human being to act towards each other "
                        "human being in a spirit of brotherhood, with the completion unspecified (norm-defaults@0): "
                        "the rule is unconditional, so VE reports gaps: none (readings/u017.strict.ve.md).",
    ("u052", "invocation_barred"): "Article 14(2) read as a prohibition on invoking the asylum right in the case of a "
                                   "prosecution that genuinely arises from a non-political crime or from acts contrary to "
                                   "UN purposes and principles. The two grounds are guards over the prosecution; for any "
                                   "other prosecution the text says nothing, and VE reports UNDECIDED, not permitted "
                                   "(readings/u052.invocation_barred.ve.md).",
    ("u112", "exercise_prohibited"): "Article 29(3) read as a prohibition on carrying out an exercise of a declared right or "
                                     "freedom that is contrary to UN purposes and principles. Both conditions are guards "
                                     "over the exercise; other exercises are UNDECIDED (readings/u112.exercise_prohibited.ve.md).",
    ("u114", "interpretive_ban"): "Article 30 read as a prohibition on adopting an interpretation that implies, for a State, "
                                  "group or person, a right to destroy declared rights. The implication is the guard over "
                                  "the interpretation; other interpretations are UNDECIDED (readings/u114.interpretive_ban.ve.md).",
    ("u035", "tribunal_claim"): "Article 8 read as a duty on a competent national tribunal to provide an effective remedy "
                                "against an act that violates a fundamental right granted by the constitution or by law "
                                "(both conditions are guards; the bearer is named by the source's 'by the competent national "
                                "tribunals'). Strict force; the remedy is owed to the victim of the act, who is not an "
                                "argument (predicates have at most two) (readings/u035.tribunal_claim.ve.md).",
    ("u035", "state_claim"): "Article 8 read as a duty on a State to ensure that competent national tribunals provide an "
                             "effective remedy against such an act (same guard on the act). Strict force "
                             "(readings/u035.state_claim.ve.md).",
    ("u051", "liberty"): "Article 14(1) read as a liberty: a person may seek and enjoy asylum from persecution in other "
                         "countries (the unconditional permission names no other case) (readings/u051.liberty.ve.md).",
    ("u051", "state_avoid"): "Article 14(1) read as a duty on every State to avoid barring a person who seeks or enjoys "
                             "asylum from persecution from seeking as well as enjoying it in other countries. 'From "
                             "persecution' is a guard on the person; no positive duty to grant asylum is a candidate "
                             "(the audit found it strengthened the source) (readings/u051.state_avoid.ve.md).",
    ("u051", "anyone_avoid"): "As state_avoid, bound on every State, group and person (the source names no bearer) "
                              "(readings/u051.anyone_avoid.ve.md).",
    ("u077", "nationality_country_claim"): "Article 21(2) read as a duty on the country of which the person is a national to "
                                           "give equal access to public service. 'His country' is the relation "
                                           "is_nationality_country_of in the guard, so unrelated bearers are not bound "
                                           "(readings/u077.nationality_country_claim.ve.md).",
    ("u061", "claim"): "Article 16(3), second clause read as a duty on society and on the State to protect the family. The "
                       "subject (the family) is read from u060 and is not a checked reference; the guard names the two "
                       "protectors the source names. One reading is offered; no other is known to the translator, and "
                       "the set stays open (readings/u061.claim.ve.md).",
    ("u110", "duty"): "Article 29(1) read as a duty on each person to perform duties to the community in which alone the "
                      "free and full development of the person's personality is possible; the relative clause is a guard "
                      "(a base relation between community and person) and which duties is the named open term "
                      "duties_to_the_community. One reading is offered and the set stays open (readings/u110.duty.ve.md).",
    ("u077", "residence_country_claim"): "Article 21(2) read with 'his country' as the country in which the person resides "
                                         "(guard is_residence_country_of); the source does not say which country is meant "
                                         "(readings/u077.residence_country_claim.ve.md).",
}
ND_WHY.update({
    ("u054", "claim"): "Article 15(1) read as an entitlement: each person must receive a nationality. The duty is stated "
                       "for the person as the one entitled and names no bearer, because the source names none; the "
                       "right is not read as already fulfilled (readings/u054.claim.ve.md).",
    ("u054", "liberty"): "Article 15(1) read as a liberty: each person is permitted to have a nationality "
                         "(readings/u054.liberty.ve.md).",
    ("u111", "strict_listed_aims"): "Article 29(2) read as a strict duty to keep each person free of a limitation unless it "
                                    "is determined by law and solely for one or both of the two aims the text lists. The "
                                    "conditions are necessary, never sufficient: a limitation that meets them is UNDECIDED "
                                    "(readings/u111.strict_listed_aims.ve.md).",
    ("u111", "strict_both_aims"): "As strict_listed_aims, with 'solely for the purpose of securing ... and of meeting ...' read "
                                  "as requiring both aims (readings/u111.strict_both_aims.ve.md).",
    ("u111", "default_listed_aims"): "As strict_listed_aims, with 'shall' read as a defeasible rule whose exception has no "
                                     "stated decider (soft-norms@0 companion; the completion declared there is 'deny' = not "
                                     "required) (readings/u111.default_listed_aims.ve.md).",
    ("u111", "default_both_aims"): "As strict_both_aims, with 'shall' read as a defeasible rule (soft-norms@0 companion) "
                                   "(readings/u111.default_both_aims.ve.md).",
})
WHY.update(ND_WHY)
READINGS_DIR = HERE / "readings"
READINGS_DIR.mkdir(exist_ok=True)
companion = {}
for uid, ids in OLD_SETS.items():
    a, b_ = by_id[uid]["span"]
    for cid in ids:
        if (uid, cid) in FORMULAS:
            continue
        if cid in ND.SPECS.get(uid, {}):
            path = ND.write_companion(READINGS_DIR, uid, cid, raw[a:b_], meta["open_terms"])
        else:
            path = C.write_companion(READINGS_DIR, uid, cid, raw[a:b_], meta["open_terms"])
        companion[(uid, cid)] = load_document(path)["units"][0]["meaning_id"]
# u074 (CHECKED in the main document): the same prohibition as a norm-defaults companion
a, b_ = by_id["u074"]["span"]
U074_COMPANION = ND.write_companion(READINGS_DIR, "u074", "prohibition", raw[a:b_], meta["open_terms"])

model_ids = {}
for uid in OLD_SETS:
    rel = FALSIFYING.get(uid, {})
    wire = plain_model(rel)
    model_ids[uid] = (FiniteModel.from_dict(renv, wire).model_id, wire)
for uid, ids in OLD_SETS.items():
    mid_, wire = model_ids[uid]
    readings = []
    for cid in ids:
        if (uid, cid) in FORMULAS:
            kind, content, meaning = "asserted", formula_to_data(renv, FORMULAS[(uid, cid)]), meaning_id(renv, FORMULAS[(uid, cid)])
        else:
            kind, content, meaning = "norm", None, companion[(uid, cid)]
        readings.append({"id": cid, "kind": kind, "meaning_id": meaning, "content": content,
                         "admission": {"who": "translator", "why": WHY[(uid, cid)],
                                       "distinguishing_models": {o: mid_ for o in ids if o != cid}}})
    previous = next((rs for rs in meta["reading_sets"] if rs["unit"] == uid), None)
    history = list(previous.get("rejected_history", [])) if previous else []
    version = previous["version"] if previous else 1
    if uid in ("u052", "u112"):
        history.append({"version": version, "readings": [r["id"] for r in previous["readings"]],
                        "reason": "rejected by the 2026-09-29 audit: the assertion and norm readings applied to the "
                                  "person or to every exercise of a person, not to the case or the single exercise"})
        version += 1
    if uid in ("u017", "u052", "u112", "u114"):
        history.append({"version": version, "readings": [r["id"] for r in previous["readings"]],
                        "reason": "replaced 2026-10-02: the norm candidate declared a completion (allow or deny) that "
                                  "the source does not state (u052, u112 and u114 also kept their conditions in a sort "
                                  "description); it is now a norm-defaults@0 companion with the completion unspecified "
                                  "and the conditions in guards"})
        version += 1
    if uid in NEW_RESETS:
        history.append({"version": version, "readings": NEW_RESETS[uid], "reason": REJECTED_REASON[uid]})
        version += 1
    if uid == "u054":
        history.append({"version": 1, "readings": ["each_person_has_a_nationality", "some_state_grants_each"],
                        "reason": "rejected by the 2026-10-02T0600Z audit: both asserted readings turned a right to a "
                                  "nationality into an accomplished fact (everyone already has one, or some state already "
                                  "grants one to everyone); the source does not say the right is fulfilled"})
        version = 2
    if uid == "u051":
        history.append({"version": version, "readings": ["liberty", "state_avoid", "anyone_avoid"],
                        "reason": "rejected by the 2026-10-02T0600Z audit: the two avoiding duties applied only if the person "
                                  "is persecuted, so a person seeking asylum from persecution that is only threatened fell "
                                  "outside the guard and the right to seek asylum from persecution was weakened; the guard is "
                                  "now the person's seeking or enjoying asylum from persecution, suffered or threatened"})
        version += 1
    if uid == "u111":
        history.append({"version": 1, "readings": ["limitation-29 (rights@0 limitation)"],
                        "reason": "rejected by the 2026-10-02T0600Z audit: the assembled document reported zero limitation "
                                  "terms, so the limitation constrained none of the rights, which were all reading-set "
                                  "candidates; it is replaced by norm candidates whose guards carry the necessary conditions"})
        version = 2
    sets.append({"id": f"rs_{uid}", "unit": uid, "version": version, "status": "open",
                 "models": {mid_: wire} if len(ids) > 1 else {}, "readings": readings,
                 **({"rejected_history": history} if history else {})})
    unit_by_id[uid]["kind"] = "norm"
UNIT_OPEN = {"u017": ["spirit_of_brotherhood"],
             "u052": ["genuine", "non_political_crime", "contrary_to_un_purposes_and_principles"],
             "u112": ["rights_and_freedoms_set_forth", "contrary_to_un_purposes_and_principles"],
             "u114": ["rights_and_freedoms_set_forth", "aimed_at_destruction_of_rights"],
             "u035": ["effective", "competent", "fundamental_rights_granted"], "u051": ["persecution"], "u077": [],
             "u061": ["protection_of_the_family"], "u110": ["duties_to_the_community", "free_and_full_development"],
             "u054": [], "u111": ND.U111_OPEN}
for uid, names in UNIT_OPEN.items():
    unit_by_id[uid]["meaning"] = {"open": names} if names else "specified"

meta["reading_sets"] = sets

# ---------------------------------------------------------------- units blocked for a reason other than norms
FORCE = ("other_force_variants_in_one_reading_set", "u020 u024 u025 u027 u037 u042 u043 u045a u045b u055 u059 u064 u078 "
         "u079a u079b u094 u097 u098 u099a u099b u100a u100b u101 u102 u081 u082 u084a u084b u084c u084d u085 u086 u087 "
         "u089 u091 u092 u093 u096 u103 u105a u105b u105c u106".split())
INCLUDES = ("other_right_lines_in_reading_sets", "u067 u068 u071a u071b".split())
GRAMMAR = ("other_act_phrase_grammar", "u039 u041 u076 u108".split())
RETAG = {}
for tag, ids in (FORCE, INCLUDES, GRAMMAR):
    for uid in ids:
        assert unit_by_id[uid]["meaning"] == {"unformalised": "norms"}, uid
        unit_by_id[uid]["kind"] = ["unformalised", tag]
        unit_by_id[uid]["meaning"] = {"unformalised": tag}
        RETAG[uid] = tag

document = HERE / "translation.ve.md"
document.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2).encode()
                     + b"\n---\n" + raw)

# ================================================================ check, coverage, render
doc = load_document(document)
verdict = check_document(document)
cov = coverage(doc)
rendered = render_document(document)
assert doc["source"] == raw
assert cov["source_bytes"] == cov["accounted_bytes"] == len(raw)
assert sum(u["span"][1] - u["span"][0] for u in meta["units"]) == len(raw)
assert [u["span"] for u in meta["units"]] == [r["span"] for r in rows]
(HERE / "rendered.md").write_text(rendered)
companion_docs = {}
for (uid, cid) in sorted(companion):
    path = READINGS_DIR / f"{uid}.{cid}.ve.md"
    v = check_document(path)
    assert v["premises"]["status"] == "model", (uid, cid, v["premises"])
    companion_docs[f"{uid}.{cid}"] = {"path": f"readings/{path.name}", "premises": v["premises"]["status"],
                                      "coverage_bytes": v["coverage"]["bytes_by_status"], "residual": v["coverage"]["residual"],
                                      "norm_defaults_report": (v.get("norm_defaults") or {}).get("report"),
                                      "profiles": json.loads(path.read_bytes()[4:].split(b"\n---\n", 1)[0])["environment"]["profiles"]}
v74 = check_document(U074_COMPANION)
assert v74["premises"]["status"] == "model"
companion_docs["u074.prohibition"] = {"path": f"readings/{U074_COMPANION.name}", "premises": v74["premises"]["status"],
                                      "coverage_bytes": v74["coverage"]["bytes_by_status"], "residual": v74["coverage"]["residual"],
                                      "norm_defaults_report": v74["norm_defaults"]["report"],
                                      "profiles": json.loads(U074_COMPANION.read_bytes()[4:].split(b"\n---\n", 1)[0])["environment"]["profiles"]}
(HERE / "readings-rendered.md").write_text("\n\n".join(
    f"## {k}\n\n" + render_document(HERE / item["path"]) for k, item in sorted(companion_docs.items())) + "\n")

# ================================================================ witnesses (no invented permissions, reading separation)
from ve.entailment import check_entailment_certificate, prove_entailment
from ve.environment import Environment
from ve.norms import NormDocument


def replayed(env_, premises, conclusion):
    result = prove_entailment(env_, premises, conclusion)
    ok = (result.status == "Found"
          and check_entailment_certificate(env_, premises, conclusion, result.certificate).valid)
    return {"status": result.status, "certificate_replayed": bool(ok)}


def mini_env(preds, holder, default):
    predicates = {"is_state": {"arguments": ["bearer"], "description": "The bearer is a state"}}
    for name, decl in preds.items():
        d = json.loads(json.dumps(decl))
        d["regulated"]["default"] = default
        predicates[name] = d
    return Environment({"language": "ve.core@0.2", "profiles": ["norms@0", "relational-fol@0"],
                        "spec_revision": env_json["spec_revision"],
                        "vocabulary": {"constants": {}, "predicates": predicates,
                                       "sorts": {s: vocab["sorts"][s] for s in ("bearer", "person", holder)}}})


def norm_doc(preds, holder, default, norm, keep=True):
    e = mini_env(preds, holder, default)
    return NormDocument(e, [NormDocument._decode({"norm": norm})] if keep else [])


witnesses = {}
liberties_checked = 0
for uid, entry in RIGHT_UNITS.items():
    holder = entry.get("holder", "person")
    preds = predicates_for(uid, entry)
    out = {}
    for cand in candidates(uid, entry):
        line = cand["content"]["right"]["lines"][0]
        norm = line["norm"]
        pred = norm["predicate"]
        arity = preds[pred]["arguments"]
        if cand["id"] == "liberty":
            concl = Forall("person", Unary(pred, V0))
        else:
            atom = Binary(pred, Var(1), V0)
            concl = Forall("bearer", Forall(holder, Implies(Unary("is_state", Var(1)), atom)
                                            if cand["id"].startswith("state") else atom))
        r = {}
        for default in ("deny", "allow"):
            d = norm_doc(preds, holder, default, norm)
            r[f"rule_kept_completion_{default}"] = replayed(d.env, tuple(f for _, f in d.premises()), concl)
            assert r[f"rule_kept_completion_{default}"]["certificate_replayed"], (uid, cand["id"], default)
        d = norm_doc(preds, holder, "deny", norm, keep=False)
        r["rule_dropped_completion_deny"] = replayed(d.env, tuple(f for _, f in d.premises()), concl)
        assert r["rule_dropped_completion_deny"]["status"] != "Found", (uid, cand["id"])
        out[cand["id"]] = r
        liberties_checked += cand["id"] == "liberty"
    witnesses[uid] = out
# zero-training English: which base predicates of the norm-defaults companions read as plain English in the render
companion_lint = {}
for key_, item_ in companion_docs.items():
    if "norm-defaults@0" not in item_["profiles"]:
        continue
    env_data = json.loads((HERE / item_["path"]).read_bytes()[4:].split(b"\n---\n", 1)[0])["environment"]
    cenv = _environment(env_data)
    failing = sorted({i.path.split("/")[3] for i in lint_english_vocabulary(cenv) if "/predicates/" in i.path})
    basep = sorted(n for n, p in env_data["vocabulary"]["predicates"].items() if "regulated" not in p)
    companion_lint[key_] = {"base_predicates": basep, "read_as_plain_english": [n for n in basep if n not in failing],
                            "fall_back_to_the_quoted_identifier": [n for n in basep if n in failing]}
# norm-defaults@0 companions: a case inside the guard is SETTLED, a case outside it is UNDECIDED (never silently permitted)
nd_witnesses = {}
for uid_, cands_ in ND.SPECS.items():
    for cid_, spec_ in cands_.items():
        if spec_.get("soft"):
            continue  # soft-norms@0 companions have no norm-defaults status
        nd_witnesses[f"{uid_}.{cid_}"] = WND.run(READINGS_DIR / f"{uid_}.{cid_}.ve.md", spec_)
assert all(o["as_expected"] for outs in nd_witnesses.values() for o in outs), nd_witnesses
# migration audit of u074: the main document declares completion 'allow'; norm-defaults@0 certifies it is never consulted
from ve.norm_defaults import audit_completions, load_audit_source
AUDIT_DIR = HERE / "audit"
AUDIT_DIR.mkdir(exist_ok=True)
u074_meta = json.loads(U074_COMPANION.read_bytes()[4:].split(b"\n---\n", 1)[0])
u074_meta["environment"]["vocabulary"]["predicates"]["compel_association_membership_permitted"]["regulated"]["default"] = "allow"
u074_allow = AUDIT_DIR / "u074.allow.ve.md"
u074_allow.write_bytes(b"---\n" + json.dumps(u074_meta, ensure_ascii=False, sort_keys=True, indent=2).encode()
                       + b"\n---\n" + raw[by_id["u074"]["span"][0]:by_id["u074"]["span"][1]])
env74, units74 = load_audit_source(u074_allow.read_bytes())
audit74 = audit_completions(env74, units74, prove=True)
u074_audit = [{k: (v if k != "certificate" else {"present": v is not None, "target": (v or {}).get("target"),
                                                "checker_version": ((v or {}).get("certificate") or {}).get("checker_version")})
               for k, v in c.items()} for c in audit74["completions"]]
assert u074_audit[0]["default_reached"] == "none" and u074_audit[0]["switched_gaps"] == "none", u074_audit
(HERE / "witnesses.json").write_text(json.dumps(
    {"rights_completions": witnesses, "norm_defaults_status": nd_witnesses, "u074_migration_audit": u074_audit},
    ensure_ascii=False, indent=2, sort_keys=True) + "\n")

# ================================================================ units.json
RIGHT_NOTE_FORCE = ("Force is read as strict for every candidate: the unit has no weakening word ('should', 'shall', "
                    "'generally', a resources qualifier) and lies outside Articles 22-27, where Article 22 opens force by "
                    "cross-reference. A defeasible variant cannot share a reading set with a strict one (metrics.language_findings).")
AUDIT_VERIFIED_AFTER_REPAIR = {"u032", "u033a", "u049", "u046", "u033b", "u063", "u029"}  # repaired, found faithful by the 2026-09-30T1800Z or 2026-10-01T1800Z audit
AUDIT_REJECTED = {  # the six units the 2026-09-30 audit marked unfaithful, plus the same defect found in three others
    "u054": "Rejected 2026-09-30 (strengthened: every state must grant each person a nationality). Repaired: the claim "
            "candidates are dropped; the set holds the asserted readings 'each person has some nationality' and 'for each "
            "person some state grants a nationality'.",
    "u032": "Rejected 2026-09-30 (labels: the two polarities were one duty). Repaired: one polarity, no polarity label; the "
            "act phrase keeps 'without any discrimination'.",
    "u033a": "Rejected 2026-09-30 (labels and content: the negative candidate dropped 'equal protection'). Repaired: only the "
             "positive candidate 'protect equally against discrimination in violation of this Declaration'.",
    "u049": "Rejected 2026-09-30 (labels: the positive candidate repeated the negative duty). Repaired: only the avoiding "
            "duty, plus the liberty reading.",
    "u029": "Same defect as the rejected units (found by the translator, not sampled): 'avoid refusing recognition' and "
            "'recognise' are one duty. One polarity.",
    "u046": "Same defect as the rejected units (not sampled): 'avoid denying protection by law' and 'protect by law' are one "
            "duty. One polarity. REJECTED AGAIN 2026-09-30T1800Z (weakened: protection against attacks upon honour and "
            "reputation absent); repaired 2026-10-01 below.",
}
AUDIT_REJECTED_1001 = {  # the four units the 2026-09-30T1800Z audit marked unfaithful; repaired 2026-10-01
    "u041": "Rejected 2026-09-30T1800Z (weakened: both duties dropped 'in a public trial at which he has had all the guarantees "
            "necessary for his defence'). The whole clause (according to law, in a public trial, with all guarantees necessary "
            "for the defence) needs more than the 80 bytes of an act phrase, and carrying only part of it is the defect the "
            "audit found, so the unit leaves READINGS and is UNFORMALISED (other:act_phrase_grammar). The open term "
            "guarantees_necessary_for_defence stays declared. Its holder sort charged_person is dropped.",
    "u046": "Rejected 2026-09-30T1800Z (weakened). Repaired: the act phrase is 'protect by law against such interference as "
            "well as attacks' (67 bytes), the source's own anaphor; 'such interference or attacks' is read from u045a and "
            "u045b in the reason (not a checked reference); 'or' is worded 'as well as'.",
    "u033b": "Rejected 2026-09-30T1800Z (label: a negative 'avoid inciting discrimination' candidate dropped 'equal "
             "protection'). Repaired: one polarity, the positive duty 'protect equally against incitement to such "
             "discrimination' (65 bytes, the anaphor kept).",
    "u063": "Not sampled; same defect class (the duties dropped 'alone as well as in association with others'). The duties "
            "now say 'alone as well as jointly with others' / 'alone as well as with others'. Pending a fresh audit.",
}
AUDIT_REJECTED_1002 = {  # the four units the 2026-10-01T1800Z audit marked unfaithful; repaired 2026-10-02
    "u051": "Rejected 2026-10-01T1800Z (strengthened and incomplete: the positive candidates required every bearer to grant "
            "asylum to every person and omitted seeking). Repaired with norm-defaults@0: no positive grant candidate; the "
            "reading set is a liberty (a person may seek and enjoy asylum from persecution in other countries) and the "
            "avoiding duty, bound on every State or on every bearer, whose act phrase says 'seeking as well as enjoying' and "
            "whose guard 'the person is seeking or enjoying asylum from persecution' carries 'from persecution' as a checked "
            "scope. Pending a fresh independent audit.",
    "u035": "Rejected 2026-10-01T1800Z (the checked duty had no argument for the rights-violating act; prose holder). Repaired "
            "with norm-defaults@0: the duty ranges over (tribunal or State, act) and a guard 'the act violates a fundamental right granted "
            "to a person by the constitution or by law' carries the scope as checked structure; the bearer is named by a guard "
            "(a competent national tribunal, or a State that must ensure tribunals provide the remedy). The victim is not an "
            "argument (predicates have at most two); it is the person whose right the act violates, in the act phrase. "
            "Pending a fresh independent audit.",
    "u039": "Rejected 2026-10-01T1800Z ('in full equality' unattached; no determination or charge argument). A repair with "
            "norm-defaults@0 (a guard on a determination argument) fits the scope but the duty 'give in full equality a fair "
            "public hearing by an independent impartial tribunal in the case' is 88 to 93 bytes, over the 80-byte act phrase; "
            "dropping 'in full equality' is the rejected defect. The unit is UNFORMALISED (other:act_phrase_grammar).",
    "u077": "Rejected 2026-10-01T1800Z (no checked relation connected a bearer to the holder's country, so unrelated bearers "
            "were bound). Repaired with norm-defaults@0: the guard is a base relation between the bearer and the person; "
            "'his country' is read two ways in the reading set (the country of which the person is a national, the country "
            "in which the person resides) because the source does not say. Pending a fresh independent audit.",
}
AUDIT_REJECTED_0600 = {  # the three units the 2026-10-02T0600Z audit marked unfaithful; repaired 2026-10-02T1800Z
    "u054": "Rejected 2026-10-02T0600Z (both asserted readings turned a right to a nationality into an accomplished fact). "
            "Repaired: the asserted readings are dropped; the set holds an entitlement (each person must receive a nationality; "
            "the source names no bearer, so none is named) and a liberty (each person is permitted to have a nationality), as "
            "norm-defaults@0 companions with the completion unspecified. 'Some state must grant it' is not expressible: a norm "
            "cannot be an existential over bearers. Pending a fresh independent audit.",
    "u051": "Rejected 2026-10-02T0600Z (the avoiding duties applied only if the person is persecuted, so a person seeking asylum "
            "from threatened persecution fell outside the guard). Repaired: the guard is the base relation 'the person seeks or "
            "enjoys asylum from persecution' (suffered or threatened), a checked scope that does not require persecution to have "
            "occurred; the open term persecution gains the factor 'whether persecution that is only threatened counts'. "
            "Pending a fresh independent audit.",
    "u111": "Rejected 2026-10-02T0600Z (the limitation reported zero limitation terms, so it constrained none of the rights). "
            "Repaired: the rights@0 limitation is dropped and the unit holds norm candidates over a limitation argument whose guard "
            "is the negation of the source's necessary conditions (determined by law; solely for the listed aims), so a limitation "
            "that misses a condition is settled (the person must be free of it) and one that meets them is UNDECIDED (the conditions "
            "are necessary, never sufficient). Four candidates: 'solely for the purpose of A and of B' as one or both of the two "
            "aims, or as both aims; 'shall' as strict (norm-defaults@0) or defeasible (soft-norms@0, completion 'deny' = not "
            "required). Pending a fresh independent audit.",
}
NORMS_DETAIL = {
    "u013a": "A proclamation (a speech act of the General Assembly) of the Declaration as a common standard of achievement for all peoples and nations: a standard has no bearer and no completion to leave unspecified.",
    "u013ba": "'shall strive ... keeping this Declaration constantly in mind': 'shall' needs a strict and a defeasible reading, and the defeasible one needs soft-norms@0, which cannot be enabled with norm-defaults@0; 'strive' is effort, not an outcome; 'constantly' is time.",
    "u013bb": "'shall strive ... by progressive measures ... to secure universal and effective recognition': as u013ba (force variants, effort, a sequence of measures).",
    "u019": "Needs a duty over a bearer, a person and a ground of distinction (three arguments; predicates have at most two) and a quantifier over 'all the rights and freedoms set forth in this Declaration' (a self-reference to a list that is not a sort here).",
    "u031": "'All are equal before the law' is a comparison of treatment among persons, not a duty on a named bearer; no norm predicate says what equality requires, and 'equal before the law' stays a named open term.",
    "u057": "'without any limitation due to race, nationality or religion' conditions every limitation by its ground: bearer, person and ground are three arguments (predicates have at most two), and 'men and women of full age' adds a scope.",
    "u058": "'equal rights as to marriage, during marriage and at its dissolution' compares the rights of two parties in three phases; there is no comparison of rights and no phase argument.",
}
ND_DEPTH = {
    "u061": "One norm candidate under norm-defaults@0: society and the State must protect the family (guard: the bearer is society or "
            "a State); every other bearer is UNDECIDED. The subject is read from u060; 'protection' is a named open term.",
    "u110": "One norm candidate under norm-defaults@0: a person must perform duties to a community in which alone the free and "
            "full development of that person's personality is possible (a guard over a base relation). Which duties is a named open "
            "term; the strength of 'alone' and 'possible' lives in the relation's description, not in a checked clause.",
    "u017": "Both candidates are formal: an obligation on every human being, strict (norm-defaults@0 companion, completion "
            "unspecified, gaps: none) or defeasible with an open exception (soft-norms@0 companion; it keeps the declared "
            "completion 'deny' because soft-norms@0 and norm-defaults@0 cannot be enabled together). 'Each other human being' "
            "sits in the act phrase and 'spirit of brotherhood' is a named open term.",
    "u052": "The norm candidate is a prohibition over (person, prosecution) with the two grounds as guards, completion "
            "unspecified, so a prosecution outside the grounds is UNDECIDED (status witnesses in witnesses.json). The assertion "
            "candidate is a formula over prosecutions. 'Genuinely', 'non-political' and 'contrary to the purposes and principles' "
            "stay named open terms.",
    "u112": "The norm candidate is a prohibition on carrying out an exercise, guarded by 'an exercise of a right or freedom set "
            "forth in this Declaration' and 'contrary to the purposes and principles of the United Nations'; other exercises are "
            "UNDECIDED. The assertion candidate is a formula over exercises.",
    "u114": "The norm candidate is a prohibition on adopting an interpretation, guarded by 'implies, for a State, group or person, "
            "a right to engage in an activity or to perform an act aimed at the destruction of a declared right'; other "
            "interpretations are UNDECIDED. The assertion candidate is a formula over bearers.",
    "u035": "Two norm candidates under norm-defaults@0: a competent national tribunal must provide an effective remedy against an "
            "act, or a State must ensure tribunals do. Both are guarded by 'the act violates a fundamental right granted by the "
            "constitution or by law'; elsewhere UNDECIDED. 'Effective', 'competent' and 'fundamental rights granted' are named open terms.",
    "u051": "Three norm candidates under norm-defaults@0: a liberty to seek and enjoy asylum from persecution in other countries, "
            "and the duty to avoid barring a person who seeks or enjoys such asylum, on every State or on every bearer. "
            "'From persecution' is a checked guard on the person (the open term persecution stays named). No positive grant candidate.",
    "u077": "Two norm candidates under norm-defaults@0: the country of which the person is a national, or the country in which "
            "the person resides, must give the person equal access to public service in their country. The bearer-holder "
            "relation is a checked base relation in the guard; other bearers are UNDECIDED.",
}
ND_DEPTH.update({
    "u054": "Two norm candidates under norm-defaults@0, no accomplished fact: each person must receive a nationality (an "
            "entitlement; the source names no bearer, so the duty is stated for the person as the one entitled and no bearer "
            "is invented), or each person is permitted to have a nationality. No asserted candidate remains.",
    "u111": "Four norm candidates over a limitation argument: a person must be free of a limitation that is not determined by "
            "law or is not solely for the listed aims (guard: the negation of the necessary conditions); a limitation that meets "
            "both conditions is UNDECIDED, so the necessary conditions are never read as sufficient. 'And' between the two aims "
            "is read as one or both (listed aims) or both; 'shall' as strict or defeasible. The second aim's coordination of "
            "morality, public order and the general welfare stays inside one base predicate and named open terms.",
})
ND_DEPTH["u051"] = ("Three norm candidates under norm-defaults@0: a liberty to seek and enjoy asylum from persecution in other "
                    "countries, and the duty to avoid barring a person who seeks or enjoys such asylum, on every State or on every "
                    "bearer. The guard is the base relation 'the person seeks or enjoys asylum from persecution' (suffered or "
                    "threatened); the open term persecution stays named. No positive grant candidate.")
ND_RESIDUAL = {
    "u061": ["other:norm_candidates_hold_no_content_in_ve-document@1", "other:anaphor_subject_from_previous_unit"],
    "u110": ["other:norm_candidates_hold_no_content_in_ve-document@1",
             "modality/belief (what is 'possible' for 'alone' is carried by a relation description)"],
    "u017": ["other:norm_defaults_with_soft_norms (the defeasible candidate keeps the declared completion 'deny')",
             "other:pairwise_relation_only_in_act_phrase", "other:norm_candidates_hold_no_content_in_ve-document@1"],
    "u052": ["other:norm_candidates_hold_no_content_in_ve-document@1"],
    "u112": ["other:norm_candidates_hold_no_content_in_ve-document@1"],
    "u114": ["other:norm_candidates_hold_no_content_in_ve-document@1"],
    "u035": ["other:norm_candidates_hold_no_content_in_ve-document@1", "other:predicates_have_at_most_two_arguments (the victim)",
             "defaults (the 'shall'-free strict force is assumed; a defeasible variant needs soft-norms@0, which cannot combine with norm-defaults@0)"],
    "u051": ["other:norm_candidates_hold_no_content_in_ve-document@1", "other:act_phrase_grammar (80 bytes; 'from persecution' moved to a guard)",
             "defaults (as u035)"],
    "u077": ["other:norm_candidates_hold_no_content_in_ve-document@1", "defaults (as u035)"],
    "u054": ["other:norm_candidates_hold_no_content_in_ve-document@1",
             "other:existential_bearer ('some state must grant it' cannot be a norm over bearers)"],
    "u111": ["other:norm_candidates_hold_no_content_in_ve-document@1",
             "other:soft_norms_with_norm_defaults (the two defeasible candidates keep the declared completion 'deny' = not required)",
             "other:limitation_not_attached_to_rights_lines (the limitation is a norm over a limitation argument, not a rights@0 limitation)"],
}
ND_RESIDUAL["u051"] = ["other:norm_candidates_hold_no_content_in_ve-document@1", "defaults (as u035)"]
old_prev = {r["id"]: r for r in json.loads((PREV / "units.json").read_text())["units"]}
for row in rows:
    uid = row["id"]
    row["previous_status"] = old_prev[uid]["status"] if uid in old_prev else old_prev["u022" if uid.startswith("u022") else "u111a"]["status"]
    if uid in RIGHT_UNITS:
        entry = RIGHT_UNITS[uid]
        rs = next(s for s in meta["reading_sets"] if s["unit"] == uid)
        row.update(status="READINGS", candidates=[r["id"] for r in rs["readings"]], open_terms=entry["open"],
                   new_feature="rights@0 (holder, claim and liberty lines, reading sets with labelled axes)",
                   axes_open=sorted({a for r in rs["readings"] for a in r["labels"] if a != "force"}),
                   force_note=RIGHT_NOTE_FORCE,
                   formal_depth=("Every candidate is a complete right block (holder, one line) checked at load; every pair of "
                                 "candidates is separated by a checked finite situation. Act phrases follow the act-phrase "
                                 "grammar and can be shorter than the source clause"
                                 + (f"; elided from the act phrases: {entry['elided']}" if entry.get("elided") else "")
                                 + ". The full source clause is in each predicate's description."),
                   residual_missing_features=["defaults (a defeasible variant cannot share this set)",
                                              "other:act_phrase_grammar (act phrases shorter than the clause)"]
                                             + (["other:prose_scoped_holder_sort"] if entry.get("holder") else []),
                   note=entry["note"])
        if entry.get("polarity", "both") != "both":
            row["polarity_note"] = ("One polarity only: the audit found 'avoid denying X' and 'give X' to be one duty, so "
                                    "no polarity axis is offered (table.py)")
        if uid in AUDIT_REJECTED_1001 or uid in AUDIT_REJECTED:
            row["audit_repair"] = (AUDIT_REJECTED_1001.get(uid) or AUDIT_REJECTED[uid]) + (
                "" if uid in AUDIT_VERIFIED_AFTER_REPAIR else " Pending a fresh independent audit.")
        row.pop("missing_feature", None)
        row.pop("semantic_kind", None)
    elif uid in OLD_SETS:  # the units whose candidates are companion documents
        rs = next(x for x in meta["reading_sets"] if x["unit"] == uid)
        nd_ids = [c for c in OLD_SETS[uid] if c in ND.SPECS.get(uid, {}) and not ND.SPECS[uid][c].get("soft")]
        row.update(status="READINGS", open_terms=UNIT_OPEN[uid],
                   reading_set=rs["id"], candidates=[r["id"] for r in rs["readings"]],
                   companions=[f"readings/{uid}.{c}.ve.md" for c in OLD_SETS[uid] if (uid, c) in companion],
                   norm_defaults_companions=[f"readings/{uid}.{c}.ve.md" for c in nd_ids],
                   new_feature="norm-defaults@0 (completion unspecified; the source's scope in checked guards)",
                   reading_elaboration="pending in this document (premise verdict UNKNOWN); every norm candidate is checked in "
                                       "its companion document",
                   formal_depth=ND_DEPTH[uid], residual_missing_features=ND_RESIDUAL[uid])
        row.pop("unresolved_features", None)
        row.pop("missing_feature", None)
        if uid in AUDIT_REJECTED_0600:
            row["audit_repair"] = AUDIT_REJECTED_0600[uid]
        elif uid in AUDIT_REJECTED_1002:
            row["audit_repair"] = AUDIT_REJECTED_1002[uid]
        elif uid in NEWLY_EXPRESSIBLE:
            row["newly_expressible_by"] = "norm-defaults@0"
            row["previous_missing_feature"] = "norms"
        else:
            row["audit_repair"] = ("Re-translated 2026-10-02: the norm candidate declared a completion (allow or deny) the source "
                                   "does not state (u052, u112 and u114 also kept their conditions in a sort description); it is now a "
                                   "norm-defaults@0 companion with the completion unspecified and the conditions in guards. Pending a "
                                   "fresh independent audit.")
    elif uid == "u074":
        row.update(companions=["readings/u074.prohibition.ve.md"], norm_defaults_companions=["readings/u074.prohibition.ve.md"],
                   norm_defaults_note=("Unchanged in this document (CHECKED, audit-verified), where the predicate still declares the "
                                       "completion 'allow' because a rights@0/soft-norms@0 document cannot enable norm-defaults@0. "
                                       "readings/u074.prohibition.ve.md is the same prohibition with the completion 'unspecified' "
                                       "(gaps: none), and the migration audit certifies the declared 'allow' is never consulted "
                                       "(metrics.norm_defaults.u074_migration_audit)."))
    elif uid in NORMS_DETAIL:
        row["blocker_detail"] = NORMS_DETAIL[uid]
        row["norm_defaults_note"] = "re-examined 2026-10-02 with norm-defaults@0: it removes the need for an invented completion, not this blocker"
    elif uid in RETAG:
        row["missing_feature"] = "other:" + RETAG[uid][len("other_"):]
        row["previous_missing_feature"] = "norms"
        if uid in RETAG and RETAG[uid] == "other_force_variants_in_one_reading_set":
            row["blocker_detail"] = ("The unit either uses 'shall' (soft-norms 2.2: a READINGS set on force) or lies in Articles "
                                     "22-27 (force opened by Article 22). A strict and a defeasible candidate need different base "
                                     "predicates, so no single checked situation separates them and no reading set can hold both.")
        elif RETAG[uid] == "other_right_lines_in_reading_sets":
            row["blocker_detail"] = ("'this right includes ...' adds lines to an existing right (right_lines), but a reading-set "
                                     "candidate can only be a whole right block, so the inclusion cannot be stated in a set.")
        elif uid == "u039":
            row["audit_repair"] = AUDIT_REJECTED_1002["u039"]
            row["blocker_detail"] = ("Demoted from READINGS by the 2026-10-01T1800Z audit ('in full equality' was an unattached open "
                                     "term and the duty had no determination or charge argument). Repair attempted with norm-defaults@0: the "
                                     "determination (or criminal charge) is a guard on a case argument, but the duty 'give in full "
                                     "equality a fair public hearing by an independent impartial tribunal in the case' is 88 to 93 bytes, "
                                     "over the 80-byte act phrase; splitting the tribunal into the bearer's guard works for a tribunal "
                                     "bearer but not for the State reading, and dropping 'in full equality' is the rejected defect.")
        elif uid == "u041":
            row["blocker_detail"] = ("Demoted from READINGS by the 2026-09-30T1800Z audit: the clause 'until proved guilty according "
                                     "to law in a public trial at which he has had all the guarantees necessary for his defence' "
                                     "does not fit an 80-byte act phrase (the nearest wording is 93 to 103 bytes), and the "
                                     "shorter wording the audit accepted as fitting still drops the guarantees, which was the "
                                     "defect (a closed trial would end the presumption).")
        else:
            row["blocker_detail"] = ("The act would not fit an act phrase (at most 80 bytes; no 'or', 'and', 'for', 'in which' clauses).")
    if uid in by_id and old_prev.get(uid) and row["status"] == "UNFORMALISED" and uid not in RETAG:
        pass
prev_run_rows = {r["id"]: r for r in json.loads((LAST / "units.json").read_text())["units"]}
assert list(prev_run_rows) == [r["id"] for r in rows], "the unit ids of the previous run changed"
for row in rows:
    row["status_in_previous_run"] = prev_run_rows[row["id"]]["status"]
    row.pop("previous_status", None)
(HERE / "units.json").write_text(json.dumps({"source_sha256": PIN, "units": rows, "note":
    "READINGS units hold an open reading set; the tool reports them as OPEN. Right candidates carry their content in the "
    "document; the norm candidates of u017, u052, u112, u114, u035, u051, u077 sit in readings/ companion documents (norm-defaults@0 "
    "where the completion is unspecified)."},
    ensure_ascii=False, indent=2) + "\n")

# ================================================================ metrics
from ve.english import lint_english_vocabulary
LINT = [f"{i.path}: {i.code}" for i in lint_english_vocabulary(renv)]
counts = Counter(r["status"] for r in rows)
bytes_by_status = Counter()
missing = Counter()
for row in rows:
    bytes_by_status[row["status"]] += row["span"][1] - row["span"][0]
    if row["status"] == "UNFORMALISED":
        missing[row["missing_feature"]] += 1
old_to_new = {k: list(v) for k, v in old_metrics["old_to_new_units"].items()}
old_to_new["u022"] = ["u022a", "u022b", "u022c"]
old_to_new["u111"] = ["u111"]
assert sorted(x for v in old_to_new.values() for x in v) == sorted(by_id), "old-to-new mapping is not a partition"
old_aggregation = Counter()
for children in old_to_new.values():
    statuses = {by_id[c]["status"] for c in children}
    old_aggregation[next(iter(statuses)) if len(statuses) == 1 else "MIXED"] += 1
# 2026-10-01T1800Z audit of the previous run (this run's input): 16 of 20 faithful (sample: u074, u111, 14 READINGS, 4 LABELLED)
audit_1002_faithful = "u074 u111 u033a u022a u032 u112 u022c u063 u049 u046 u033b u029 u104 u069 u090 u109".split()
audit_1002_unfaithful = sorted(AUDIT_REJECTED_1002)
# 2026-10-02T0600Z audit of the previous run (this run's input): 17 of 20 faithful. Sample: u074, u111, 14 READINGS, 4 LABELLED
audit_0600_sample = ("u074 u111 u110 u032 u022c u017 u066 u029 u052 u049 u022b u054 u051 u046 u112 u033a u021 u040 u109 u056").split()
audit_0600_unfaithful = sorted(AUDIT_REJECTED_0600)
audit_0600_faithful = sorted(set(audit_0600_sample) - set(audit_0600_unfaithful))
assert len(audit_0600_sample) == 20 and len(audit_0600_faithful) == 17
# audit-verified bytes count only content an audit saw: every unit re-translated this run waits for a new audit
retranslated = sorted(AUDIT_REJECTED_0600)  # the only units re-translated this run
prior_verified = set(json.loads((LAST / "metrics.json").read_text())["audit_verified_units"])
verified = sorted((prior_verified | set(audit_1002_faithful) | set(audit_0600_faithful)) - set(retranslated) - set(audit_1002_unfaithful))
pending_repairs = sorted((set(AUDIT_REJECTED) | set(AUDIT_REJECTED_1001) | set(AUDIT_REJECTED_1002) | set(AUDIT_REJECTED_0600)) - AUDIT_VERIFIED_AFTER_REPAIR)
assert not set(verified) & set(audit_1002_unfaithful)
assert not set(verified) & set(pending_repairs)
assert all(by_id[u]["status"] in ("CHECKED", "LABELLED", "OPEN", "READINGS") for u in verified)
last = json.loads((LAST / "metrics.json").read_text())
last_verified = last["audit_verified_units"]
audit_bytes = sum(by_id[u]["span"][1] - by_id[u]["span"][0] for u in verified)
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")
claimed = sum(bytes_by_status[s] for s in COVERED)
right_ids = list(RIGHT_UNITS)  # right-block sets; u054 is an asserted set and is counted separately
right_bytes = sum(by_id[u]["span"][1] - by_id[u]["span"][0] for u in right_ids)
repaired = sorted(pending_repairs + sorted(AUDIT_VERIFIED_AFTER_REPAIR))
all_pairs = sum(len(s["readings"]) * (len(s["readings"]) - 1) for s in meta["reading_sets"] if s["unit"] in RIGHT_UNITS)
regulated = [n for n, p in vocab["predicates"].items() if "regulated" in p]
declared_completions = {
    "predicates": len(regulated),
    "by_role_and_completion": dict(sorted(Counter(f"{vocab['predicates'][n]['regulated']['role']}:{vocab['predicates'][n]['regulated']['default']}"
                                                  for n in regulated).items())),
    "also_declared_in_companions": {"u017.default": "obligation:deny (soft-norms@0 companion)",
                                    "u111.default_listed_aims": "obligation:deny (soft-norms@0 companion; = not required)",
                                    "u111.default_both_aims": "obligation:deny (soft-norms@0 companion; = not required)"},
    "note": "none of these completions is stated by the source; the rights@0 claim and liberty lines need some completion, and "
            "norm-defaults@0 is not available in a rights@0/soft-norms@0 document"}
tool_bytes = cov["bytes_by_status"]
metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw), "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-wire",
    "previous_run": "run-20261002T0600Z (ve-green-bluedot2; prev1002/ holds its translation, units, metrics, summary and AUDIT.md); "
                    "this translation is rebuilt from prev/ (the 2026-09-29T1800Z translation) with the changes stated in build.py",
    "features_merged_since_previous_baseline": [
        "wire-contract codegen for soft-norms@0 (Python and Lean tables, shadow gate; merged 2026-10-02): plumbing, the soft-norms@0 "
        "language is unchanged for the translator",
        "soft-norms@0 revision 3 and S3-pre: the soft route alone refuses a source that lists rights@0 (the rights route strips it); no effect on documents",
        "S0 VE.Compose (stack contract, base-premise slot, dispatcher): Lean theorems only; docs/INTEGRATION-GAPS.md states the dispatcher "
        "is not called by document admission, so norm-defaults@0 still cannot be enabled with soft-norms@0 or rights@0 "
        "(ve/document.py: UnsupportedProfile 'norm-defaults@0 documents on the soft and rights routes await the Lean route')",
        "use cases agent-policy (unspecified re-run) and asimov: documents, not language"],
    "language_change_for_udhr": "none: no feature merged between ve-green-bluedot2 and ve-green-wire lets the translator express a "
                                "unit it could not express before, so no unit changed status because of the language. Every change "
                                "in this run is an audit repair (u054, u051, u111) made with features that were already merged; "
                                "statuses of the other 127 units are those of the previous run.",
    "old_unit_count": old_metrics["old_unit_count"],
    "old_boundary_aggregation": dict(sorted(old_aggregation.items())),
    "old_to_new_units": old_to_new,
    "unit_scale": "sentence or clause; coordinated regulated acts split; headings separate. Changes from the previous run: "
                  "u022 split into u022a-c (three coordinated rights); u111a and u111b merged into u111 (one unit)",
    "bytes_accounted": cov["accounted_bytes"], "bytes_accounted_percent": cov["coverage_percent"],
    "unit_count": len(rows),
    "unit_counts_by_status": dict(sorted(counts.items())),
    "bytes_by_status": dict(sorted(bytes_by_status.items())),
    "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(raw), 2),
    "claimed_covered_bytes_previous_run": last["claimed_covered_bytes"],
    "claimed_covered_bytes_previous_run_percent": last["claimed_covered_percent"],
    "newly_covered_bytes": claimed - last["claimed_covered_bytes"],
    "previous_run_unit_counts_by_status": last["unit_counts_by_status"],
    "previous_run_old_boundary_aggregation": last["old_boundary_aggregation"],
    "previous_run_audit_verified_covered_bytes": last["audit_verified_covered_bytes"],
    "audit_0930_units_faithful": last["audit_0930_units_faithful"],
    "audit_0930_units_unfaithful_repaired": last["audit_0930_units_unfaithful_repaired"],
    "audit_1001_units_faithful": last["audit_1001_units_faithful"],
    "audit_1001_units_unfaithful": last["audit_1001_units_unfaithful"],
    "audit_1001_repairs": AUDIT_REJECTED_1001,
    "audit_1002_units_faithful": audit_1002_faithful,
    "audit_1002_units_unfaithful": audit_1002_unfaithful,
    "audit_1002_repairs": AUDIT_REJECTED_1002,
    "audit_0600_units_faithful": audit_0600_faithful,
    "audit_0600_units_unfaithful": audit_0600_unfaithful,
    "audit_0600_sample": audit_0600_sample,
    "audit_0600_repairs": AUDIT_REJECTED_0600,
    "audit_0600_note": "the 2026-10-02T0600Z audit of the previous run (its AUDIT.md) sampled 20 units (u074, u111, 14 READINGS, 4 LABELLED) and rejected three; the sample is stratified, so 17/20 is not a corpus rate",
    "audit_1002_note": "the 2026-10-01T1800Z audit of the previous run (its AUDIT.md) sampled 20 units and rejected four; its sample is stratified, so 16/20 is not a corpus rate",
    "units_re_translated_this_run_pending_audit": retranslated,
    "statuses_dropped_by_repair": {
        "u041": "READINGS -> UNFORMALISED (other:act_phrase_grammar) on 2026-10-01: no act phrase of 80 bytes holds 'according to law in a public trial at which ... all the guarantees necessary for his defence', and a shorter one was the rejected defect",
        "u039": "READINGS -> UNFORMALISED (other:act_phrase_grammar) on 2026-10-02: the case scope now fits a guard, but 'give in full equality a fair public hearing by an independent impartial tribunal in the case' is 88 to 93 bytes; dropping 'in full equality' or the tribunal clause is the defect the audit found"},
    "statuses_kept_with_repaired_content": "u035, u051, u077 stay READINGS: their right-block candidates are replaced by norm-defaults@0 norm candidates with scope in guards (companions)",
    "covered_by_rights_readings_bytes": right_bytes,
    "covered_by_rights_units": right_ids,
    "covered_by_norm_defaults_companion_units": sorted(u for u in OLD_SETS if any(c in ND.SPECS.get(u, {}) and not ND.SPECS[u][c].get("soft") for c in OLD_SETS[u])) + ["u074 (second companion)"],
    "asserted_reading_set_units": [],
    "audit_verified_covered_bytes": audit_bytes,
    "audit_verified_covered_percent": round(100 * audit_bytes / len(raw), 2),
    "audit_verified_units": verified,
    "audit_pending_bytes": claimed - audit_bytes,
    "audit_repaired_units": repaired,
    "tool_status_bytes": tool_bytes,
    "open_terms": [{k: t[k] for k in ("name", "decided_by", "necessary", "sufficient", "factors")} for t in meta["open_terms"]],
    "open_term_deciders_changed_to_unstated": decider_changes,
    "reading_sets": [{"id": s["id"], "unit": s["unit"], "version": s["version"],
                      "candidates": [{"id": r["id"], "kind": r["kind"], "labels": r.get("labels"),
                                      "content_in_document": r["content"] is not None,
                                      "companion": (f"readings/{s['unit']}.{r['id']}.ve.md" if (s["unit"], r["id"]) in companion else None)}
                                     for r in s["readings"]]} for s in meta["reading_sets"]],
    "right_reading_sets": len(RIGHT_UNITS),
    "right_candidates": sum(len(s["readings"]) for s in meta["reading_sets"] if s["unit"] in RIGHT_UNITS),
    "ordered_candidate_pairs_separated_by_a_checked_situation": all_pairs,
    "missing_feature_tally": dict(sorted(missing.items())),
    "missing_feature_tally_previous_run": last["missing_feature_tally"],
    "tool_residual": cov["residual"],
    "vocabulary_use": {"regulated_predicates": len(regulated), "regulated_limit": 64,
                       "predicates": len(vocab["predicates"]), "predicate_limit": 256,
                       "sorts": len(vocab["sorts"]), "sort_limit": 32},
    "language_findings": [
        "force: a strict and a defeasible right candidate need different base predicates (the defeasible one adds its exception decision), so a reading set cannot hold both and no single checked situation separates them; force is therefore fixed strict for units without a weakening word, and the 43 'shall' and Articles 22-27 units stay UNFORMALISED",
        "act phrases: at most 80 bytes, plain words only, no 'and', 'or', 'for', 'no', 'not', 'is', 'if', each slot once; lists are worded with 'as well as' and long clauses are shortened, with the full clause in the predicate description",
        "size: at most 64 regulated predicates per environment; four readings per right (two polarities, two bearers) cost two predicates per right once the two bearer readings share predicates through an is_state guard",
        "reading-set candidates must be whole right blocks: 'this right includes ...' (right_lines), limitations and bars cannot be candidates, so u067, u068, u071a, u071b stay blocked and Article 30's bar is not used",
        "limitation and bar act on rights lines fixed in the document; here every line is a reading-set candidate, so a rights@0 limitation would have empty scope (limitation_terms 0) until per-choice elaboration exists: u111 therefore states its necessary conditions as norm candidates over a limitation argument (guards), which constrain no rights line; the link from a limitation to a particular right is not expressible",
        "document reading sets cannot hold norm content, so u017, u052, u112, u114 keep companion documents for their norm candidates",
        "load time: validating 14 right reading sets takes about 35 seconds per document load",
        "entitlement without a bearer: a right whose source names no bearer (u054) can be a norm over the holder as the passive subject ('each person must receive a nationality') or a liberty; 'some state must grant it' needs an existential over bearers that a norm cannot state, and a right block would bind every state (the rejected strengthening)",
        "prospective harm: 'asylum from persecution' includes threatened persecution, so the guard of u051 is the person's asylum seeking (a base relation whose description covers suffered or threatened persecution), not the person's being persecuted; whether the persecution is real stays the named open term persecution",
        "necessary conditions: a prohibition guarded by the negation of the conditions (u111) settles every case that misses a condition and reports UNDECIDED for the cases that meet them, so 'only' limitations of this kind is never read as 'all' limitations of this kind are permitted",
        "norm-defaults@0 and soft-norms@0 still cannot share a document: the two defeasible candidates of u111 (as that of u017) are soft-norms@0 companions with the declared completion 'deny' on an obligation-role predicate (= not required), so they invent no permission",
        "norm-defaults@0 cannot be enabled together with soft-norms@0 or rights@0 (UnsupportedProfile: norm-defaults@0 documents on the soft and rights routes await the Lean route): the 14 right-block reading sets keep their declared 'deny' completions ('not required'), u074 keeps 'allow' in the main document, and the defeasible candidate of u017 keeps 'deny'; every norm candidate that can live in a norms@0 document is a companion with the completion unspecified",
        "predicates have at most two arguments: a duty with a bearer, a beneficiary and a case (remedy for an act, hearing in a determination) must fold one of them into a sort, so the victim of u035 and the person of u039 are not arguments",
        "act phrases are still at most 80 bytes in norm-defaults@0 documents: u039 ('give in full equality a fair public hearing by an independent impartial tribunal in the case', 88 to 93 bytes) cannot be stated without dropping a clause",
        "norm candidates of a reading set hold no content in the main document (they are cited by meaning id from companion documents), so the main document's premise verdict stays UNKNOWN"],
    "no_invented_permissions": {
        "claims": "every claim predicate is obligation-role with completion 'deny' (= not required); no permission predicate is used for a duty, so no prohibition makes anything permitted for anyone else. The state reading is the same duty guarded by is_state: for non-states its completion is 'not required', declared and not derived from the source (witnesses.json shows the rule decides every state under both completions and that dropping it loses the conclusion)",
        "liberties": "the seven liberty predicates are permission-role with completion 'deny' (the tool requires some completion); in the liberty reading the rule is unconditional over the whole person sort, so the completion is never consulted (witnesses.json, both completions); in the other readings the predicate is mentioned by no rule. This stray declaration is flagged for the audit",
        "u074": "the main document still declares 'allow' (a rights/soft document cannot say 'unspecified'); readings/u074.prohibition.ve.md says 'unspecified' with gaps: none, and the migration audit (witnesses.json) certifies the declared 'allow' is never consulted and that switching it preserves meaning",
        "u017_u052_u112_u114_u035_u051_u077_u054_u111": "every norm candidate is a norm-defaults@0 companion with completion 'unspecified' and its scope in guards; outside the guard VE reports UNDECIDED, not permitted and not forbidden (witnesses.json norm_defaults_status). The one exception is the defeasible candidate of u017 (soft-norms@0), which keeps the declared completion 'deny'",
        "u041_u039": "UNFORMALISED: no norm predicate, no duty stated",
        "u054_u111": "norm-defaults@0 companions with completion 'unspecified'; u111's defeasible candidates use an obligation-role predicate with completion 'deny' (= not required); no permission is declared for anyone",
        "polarity_repairs": "u029, u032, u033a, u033b, u046, u049 carry one duty (or the avoiding duty plus a liberty); no 'allow' reading of a prohibition was added",
        "remaining_declared_completions_in_the_main_document": declared_completions},
    "norm_defaults": {
        "profile": "norm-defaults@0",
        "unspecified_completion_predicates": {uid_: sorted({p for c in cands_.values() for p, d in c["predicates"].items() if "regulated" in d})
                                              for uid_, cands_ in ND.SPECS.items()},
        "companions": {k: {"profiles": v["profiles"], "report": v["norm_defaults_report"]} for k, v in companion_docs.items()
                       if "norm-defaults@0" in v["profiles"]},
        "status_witnesses": nd_witnesses,
        "u074_migration_audit": u074_audit,
        "english_wordings_of_base_predicates": companion_lint,
        "ungrounded_defaults": "0 in the companions (no deny or allow is declared); the main document cannot be audited under the profile",
        "main_document_blocked": "UnsupportedProfile: norm-defaults@0 documents on the soft and rights routes await the Lean route"},
    "audit_repairs_0930": AUDIT_REJECTED,
    "presupposition_check": "No heading or speaker marker presupposes a substantive claim; the labelled units are unchanged from the audited previous run (the 2026-10-02T0600Z audit sampled u021, u040, u109 and u056 and found them faithful). u060 (the family is the natural and fundamental group unit) stays UNFORMALISED as an evaluative claim.",
    "checks": {
        "document_load": "PASS", "byte_partition": "PASS (units partition all 10,916 bytes)",
        "document_check": "PASS", "premises": verdict["premises"], "reading_plan": {k: verdict["reading_plan"][k] for k in ("route", "choice_count") if k in verdict["reading_plan"]},
        "rights_report": verdict["rights"]["report_status"],
        "reading_sets_validated_at_load": "PASS (each right candidate elaborated through the rights route; each ordered pair separated by a checked finite situation)",
        "companion_documents": companion_docs,
        "norm_defaults_companions": "PASS: every norm-defaults@0 companion loads, checks (premises: model) and reports completion: unspecified; the status witnesses (witnesses.json) settle the case inside each guard and report UNDECIDED outside it",
        "witnesses": "PASS: rule kept entails its conclusion under both completions with replayed certificates; dropping the rule loses it",
        "render": "PASS (rendered.md, readings-rendered.md)",
        "english_vocabulary_lint": LINT},
    "document_id": verdict["document_id"], "source_id": verdict["source_id"], "coverage_tool": cov,
}
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print(json.dumps({k: metrics[k] for k in ("unit_counts_by_status", "bytes_by_status", "claimed_covered_bytes",
                                            "claimed_covered_percent", "audit_verified_covered_bytes",
                                            "old_boundary_aggregation", "missing_feature_tally")}, indent=1))
