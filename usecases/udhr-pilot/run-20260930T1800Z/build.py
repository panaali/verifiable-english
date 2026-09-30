"""Rebuild the UDHR measurement at ve-green-risk from the pinned prior run, without model calls.

Starts from prev/ (the 2026-09-29T1800Z translation, unchanged bytes), replays the 2026-09-30T0600Z changes
(rights@0 units, u052/u112 repairs, unstated deciders), and adds the repairs the 2026-09-30 audit demanded:
u054 (asserted readings, not a claim on every state), u039 and u035 (scope in a prose-scoped holder sort, one
polarity, the rest listed as elided), u032, u033a, u049 (polarity offered only where the duties differ), and the
same duplicate-polarity defect in u029, u046, u077. No unit is newly expressible at ve-green-risk: risk@0 needs
alternatives@0, which cannot combine with soft-norms@0, which rights@0 requires (ve.profiles.checker_family).
Run from the worktree root with PATH=~/.elan/bin:$PATH so the Lean rights route is found.
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

from table import HOLDER_SORTS, NATIONALITY, OPEN_TERMS, RIGHT_UNITS
from rights_sets import candidates, predicates_for
from ve.document import _environment, check_document, coverage, load_document, render_document
from ve.readings import _right_situation, rights_meaning_id
from ve.rights import RightsDocument

SOURCE = HERE.parent / "source" / "udhr.md"
PREV = HERE / "prev"
LAST = HERE / "prev0930"  # the 2026-09-30T0600Z run: its metrics, audit and units are the comparison baseline
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
vocab["sorts"]["charged_person"] = sort("charged person", "charged people",
                                        "a person charged with a penal offence")
vocab["predicates"]["is_state"] = {"arguments": ["bearer"], "description": "The bearer is a state",
                                   "verbalisation": "{0} is a state"}
for name, (singular, plural, description) in HOLDER_SORTS.items():
    vocab["sorts"][name] = sort(singular, plural, description)
vocab["predicates"].update(NATIONALITY["predicates"])
vocab["rights"] = {"holders": sorted(["person", "charged_person", *HOLDER_SORTS]), "bearers": ["bearer"],
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
import companions as C
from ve.ast import Binary, Forall, Implies, Not, Or, Unary, Var, formula_to_data
from ve.identity import meaning_id
from ve.model import FiniteModel

meta["open_terms"].extend(t for t in C.NEW_OPEN_TERMS if t["name"] not in {x["name"] for x in meta["open_terms"]})
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
            "u112": ["exercise_prohibited", "exercise_unprotected"], "u114": ["interpretive_ban", "no_implied_right"]}
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
READINGS_DIR = HERE / "readings"
READINGS_DIR.mkdir(exist_ok=True)
companion = {}
for uid, ids in OLD_SETS.items():
    a, b_ = by_id[uid]["span"]
    for cid in ids:
        if (uid, cid) in FORMULAS:
            continue
        path = C.write_companion(READINGS_DIR, uid, cid, raw[a:b_], meta["open_terms"])
        companion[(uid, cid)] = load_document(path)["units"][0]["meaning_id"]

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
    previous = next(rs for rs in meta["reading_sets"] if rs["unit"] == uid)
    history = list(previous.get("rejected_history", []))
    version = previous["version"]
    if uid in ("u052", "u112"):
        history.append({"version": version, "readings": [r["id"] for r in previous["readings"]],
                        "reason": "rejected by the 2026-09-29 audit: the assertion and norm readings applied to the "
                                  "person or to every exercise of a person, not to the case or the single exercise"})
        version += 1
    sets.append({"id": f"rs_{uid}", "unit": uid, "version": version, "status": "open",
                 "models": {mid_: wire}, "readings": readings,
                 **({"rejected_history": history} if history else {})})
    unit_by_id[uid]["kind"] = "norm"
UNIT_OPEN = {"u017": ["spirit_of_brotherhood"],
             "u052": ["genuine", "non_political_crime", "contrary_to_un_purposes_and_principles"],
             "u112": ["rights_and_freedoms_set_forth", "contrary_to_un_purposes_and_principles"],
             "u114": ["rights_and_freedoms_set_forth", "aimed_at_destruction_of_rights"]}
for uid, names in UNIT_OPEN.items():
    unit_by_id[uid]["meaning"] = {"open": names}

# ---------------------------------------------------------------- u054 (Art. 15(1)): asserted readings
from ve.ast import And, Exists
F54 = {"each_person_has_a_nationality": Forall("person", Unary("has_a_nationality", V0)),
       "some_state_grants_each": Forall("person", Exists("bearer", And(
           Unary("is_state", V0), Binary("grants_nationality", V0, Var(1)))))}
wire54 = plain_model({"has_a_nationality": [["p0"]]})  # holds for the first reading, false for the second
mid54 = FiniteModel.from_dict(renv, wire54).model_id
sets.append({"id": "rs_u054", "unit": "u054", "version": 1, "status": "open", "models": {mid54: wire54},
             "readings": [{"id": cid, "kind": "asserted", "meaning_id": meaning_id(renv, f),
                           "content": formula_to_data(renv, f),
                           "admission": {"who": "translator", "why": NATIONALITY["why"][cid],
                                         "distinguishing_models": {o: mid54 for o in F54 if o != cid}}}
                          for cid, f in F54.items()]})
unit_by_id["u054"]["kind"] = "asserted"
unit_by_id["u054"]["meaning"] = "specified"
meta["reading_sets"] = sets

# ---------------------------------------------------------------- u111: one limitation (u111a and u111b merged)
u111a, u111b = unit_by_id["u111a"], unit_by_id["u111b"]
merged = {**u111a, "id": "u111", "span": [u111a["span"][0], u111b["span"][1]], "kind": "limitation",
          "meaning": {"open": ["determined_by_law", "due_recognition_and_respect", "just_requirements",
                               "morality", "public_order", "general_welfare", "democratic_society"]},
          "content": {"limitation": {
              "name": "limitation-29", "scope": "all", "kinds": "all", "decided_by": "unstated",
              "conditions": [
                  {"name": "determined_by_law", "role": "necessary", "decided_by": None,
                   "verbalisation": "the limitation is determined by law"},
                  {"name": "solely_for_permitted_purpose", "role": "necessary", "decided_by": None,
                   "verbalisation": "the limitation is solely for a permitted purpose",
                   "purposes": ["securing due recognition and respect for the rights and freedoms of others",
                                "meeting the just requirements of morality, public order and the general welfare "
                                "in a democratic society"]}],
              "factors": []}}}
meta["units"][meta["units"].index(u111a):meta["units"].index(u111b) + 1] = [merged]
old_a, old_b = by_id["u111a"], by_id["u111b"]
rows[rows.index(old_a):rows.index(old_b) + 1] = [{**old_a, "id": "u111", "span": merged["span"],
                                                   "source": raw[merged["span"][0]:merged["span"][1]].decode(),
                                                   "previous_unit": "u111", "old_unit": "u111"}]
by_id = {r["id"]: r for r in rows}
unit_by_id = {u["id"]: u for u in meta["units"]}
for name, factors in {
        "determined_by_law": ["what it is for a limitation to be determined by law"],
        "due_recognition_and_respect": ["what due recognition and respect for the rights and freedoms of others requires"],
        "just_requirements": ["which requirements are just"],
        "morality": ["whose morality", "which requirements of morality"],
        "public_order": ["what counts as public order"],
        "general_welfare": ["what counts as the general welfare"],
        "democratic_society": ["what makes a society democratic"]}.items():
    if name not in {t["name"] for t in meta["open_terms"]}:
        meta["open_terms"].append(open_term(name, factors))

# ---------------------------------------------------------------- units blocked for a reason other than norms
FORCE = ("other_force_variants_in_one_reading_set", "u020 u024 u025 u027 u037 u042 u043 u045a u045b u055 u059 u064 u078 "
         "u079a u079b u094 u097 u098 u099a u099b u100a u100b u101 u102 u081 u082 u084a u084b u084c u084d u085 u086 u087 "
         "u089 u091 u092 u093 u096 u103 u105a u105b u105c u106".split())
INCLUDES = ("other_right_lines_in_reading_sets", "u067 u068 u071a u071b".split())
GRAMMAR = ("other_act_phrase_grammar", "u076 u108".split())
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
                                      "coverage_bytes": v["coverage"]["bytes_by_status"], "residual": v["coverage"]["residual"]}
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
(HERE / "witnesses.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

# ================================================================ units.json
RIGHT_NOTE_FORCE = ("Force is read as strict for every candidate: the unit has no weakening word ('should', 'shall', "
                    "'generally', a resources qualifier) and lies outside Articles 22-27, where Article 22 opens force by "
                    "cross-reference. A defeasible variant cannot share a reading set with a strict one (metrics.language_findings).")
AUDIT_REJECTED = {  # the six units the 2026-09-30 audit marked unfaithful, plus the same defect found in three others
    "u054": "Rejected 2026-09-30 (strengthened: every state must grant each person a nationality). Repaired: the claim "
            "candidates are dropped; the set holds the asserted readings 'each person has some nationality' and 'for each "
            "person some state grants a nationality'.",
    "u039": "Rejected 2026-09-30 (weakened and unscoped). Repaired: the holder sort person_in_determination carries the scope "
            "'in the determination of rights and obligations and of any criminal charge' in prose; the act phrase keeps 'fair "
            "public hearing by an independent impartial tribunal'; 'in full equality' is the named open term full_equality and "
            "listed as elided in every candidate's reason; the duplicate negative candidate is dropped.",
    "u035": "Rejected 2026-09-30 (scope lost). Repaired: the holder sort person_with_violated_rights carries 'for acts violating "
            "the fundamental rights granted by the constitution or by law' in prose, disclosed as elided in the candidates' "
            "reasons; the duplicate negative candidate is dropped.",
    "u032": "Rejected 2026-09-30 (labels: the two polarities were one duty). Repaired: one polarity, no polarity label; the "
            "act phrase keeps 'without any discrimination'.",
    "u033a": "Rejected 2026-09-30 (labels and content: the negative candidate dropped 'equal protection'). Repaired: only the "
             "positive candidate 'protect equally against discrimination in violation of this Declaration'.",
    "u049": "Rejected 2026-09-30 (labels: the positive candidate repeated the negative duty). Repaired: only the avoiding "
            "duty, plus the liberty reading.",
    "u029": "Same defect as the rejected units (found by the translator, not sampled): 'avoid refusing recognition' and "
            "'recognise' are one duty. One polarity.",
    "u046": "Same defect as the rejected units (not sampled): 'avoid denying protection by law' and 'protect by law' are one "
            "duty. One polarity.",
    "u077": "Same defect as the rejected units (not sampled): 'avoid denying equal access' and 'give equal access' are one "
            "duty. One polarity.",
}
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
        if uid in AUDIT_REJECTED:
            row["audit_repair"] = AUDIT_REJECTED[uid] + " Pending a fresh independent audit."
        row.pop("missing_feature", None)
        row.pop("semantic_kind", None)
    elif uid == "u054":
        row.update(status="READINGS", candidates=[r["id"] for r in next(s for s in meta["reading_sets"]
                                                                        if s["unit"] == uid)["readings"]],
                   open_terms=[], new_feature="rights@0 environment with asserted readings (FOL quantifiers over person and bearer)",
                   axes_open=["statement"],
                   formal_depth=("Two asserted formulas, checked at load and separated by a checked finite situation: each person "
                                 "has some nationality; for each person some state grants a nationality. The claim reading "
                                 "(some state must grant it) is absent: a right block cannot say 'some state' and a norm "
                                 "cannot be a disjunction over bearers; rights and assertions cannot share one set "
                                 "(UnsupportedProfile: mixed rights distinguishing situations)."),
                   residual_missing_features=["other:bearer_holder_relation (a duty on 'some state' or 'his country')",
                                              "other:rights_and_assertions_in_one_reading_set"],
                   audit_repair=AUDIT_REJECTED["u054"] + " Pending a fresh independent audit.",
                   note=NATIONALITY["note"])
        row.pop("missing_feature", None)
        row.pop("semantic_kind", None)
    elif uid in ("u017", "u114"):
        row.update(status="READINGS", previous_status="READINGS", open_terms=UNIT_OPEN[uid])
    elif uid in ("u052", "u112"):
        row.update(status="READINGS", previous_status="READINGS", open_terms=UNIT_OPEN[uid],
                   candidates=[r["id"] for r in next(s for s in meta["reading_sets"] if s["unit"] == uid)["readings"]],
                   audit_repair=("Repaired after the 2026-09-29 audit. " + (
                       "The norm reading now ranges over (person, excluded prosecution) so it bars invoking the right in "
                       "the case of such a prosecution only; the formula reading ranges over prosecutions, not persons; "
                       "the act phrase says 'seek as well as enjoy'; the person-level readings are dropped."
                       if uid == "u052" else
                       "The formula reading now ranges over single exercises (an exercise is not a person), so one contrary "
                       "exercise removes protection from that exercise only; the norm reading is unchanged."))
                                + " Pending a fresh independent audit.")
    elif uid == "u111":
        row.update(status="OPEN", open_terms=unit_by_id["u111"]["meaning"]["open"],
                   new_feature="rights@0 (limitation with necessary conditions and purposes)",
                   formal_depth=("A limitation on every right and every line: the right is limited in a situation only where "
                                 "the limitation holds; it holds only where it is determined by law and only where it is solely "
                                 "for a permitted purpose (two purposes listed). Its decider is unstated. The two source units "
                                 "u111a and u111b are one unit because splitting the purpose clause changes its meaning "
                                 "('and' joins the two permitted purposes). INERT for now: the document's rights lines are all "
                                 "reading-set candidates, so no act is in the limitation's scope (limitation_terms = 0) until "
                                 "per-choice elaboration exists."),
                   residual_missing_features=["other:per_choice_rights_elaboration"])
        row.pop("missing_feature", None)
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
        else:
            row["blocker_detail"] = ("The act would not fit an act phrase (at most 80 bytes; no 'or', 'and', 'for', 'in which' clauses).")
    if uid in by_id and old_prev.get(uid) and row["status"] == "UNFORMALISED" and uid not in RETAG:
        pass
(HERE / "units.json").write_text(json.dumps({"source_sha256": PIN, "units": rows, "note":
    "READINGS units hold an open reading set; the tool reports them as OPEN. Right candidates carry their content in the "
    "document; the norm candidates of u017, u052, u112, u114 sit in readings/ companion documents."},
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
previous_verified = "u001 u002 u021 u030 u034 u053 u056 u062 u065 u069 u072 u095 u104 u109 u113 u074".split()
audited_faithful = "u002 u012 u014 u021 u026 u028 u036 u050 u053 u072 u080 u083 u088 u095 u109 u074 u017 u114".split()
# 2026-09-30 audit of run 20260930T0600Z: 14 of 20 faithful (the four sampled headings are u023 u069 u104 u107)
audit_0930_faithful = "u023 u069 u104 u107 u074 u022a u022b u022c u048 u066 u070 u073 u114 u111".split()
audit_0930_unfaithful = "u054 u039 u035 u032 u033a u049".split()
verified = sorted(set(previous_verified) | set(audited_faithful) | set(audit_0930_faithful))
assert not set(verified) & set(audit_0930_unfaithful) | set(verified) & set(AUDIT_REJECTED)
assert all(by_id[u]["status"] in ("CHECKED", "LABELLED", "OPEN", "READINGS") for u in verified)
last = json.loads((LAST / "metrics.json").read_text())
last_verified = last["audit_verified_units"]
audit_bytes = sum(by_id[u]["span"][1] - by_id[u]["span"][0] for u in verified)
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")
claimed = sum(bytes_by_status[s] for s in COVERED)
right_ids = list(RIGHT_UNITS)  # right-block sets; u054 is an asserted set and is counted separately
right_bytes = sum(by_id[u]["span"][1] - by_id[u]["span"][0] for u in right_ids)
repaired = list(AUDIT_REJECTED)
all_pairs = sum(len(s["readings"]) * (len(s["readings"]) - 1) for s in meta["reading_sets"] if s["unit"] in RIGHT_UNITS)
regulated = [n for n, p in vocab["predicates"].items() if "regulated" in p]
tool_bytes = cov["bytes_by_status"]
metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw), "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-risk",
    "previous_run": "run-20260930T0600Z (ve-green-discourse); its translation is rebuilt from prev/ (the 2026-09-29T1800Z "
                    "translation) with only the changes stated in build.py; its AUDIT.md repairs are applied",
    "features_merged_since_previous_baseline": [
        "risk@0 (severity classes, decision records, certified margins over the alternatives route; NOT USED: risk@0 requires "
        "alternatives@0, alternatives@0 cannot combine with soft-norms@0, and rights@0 requires soft-norms@0 "
        "(ve.profiles.checker_family); the UDHR text states no quantities, margins or chooser/harm structure either)",
        "infra: Lean risk route, W6 unit-extension diagnostics, assurance manifest (no change to rights, norms or readings)"],
    "language_change_for_udhr": "none: no unit gains a status from a newly merged feature; differences from the previous run are audit repairs only",
    "old_unit_count": old_metrics["old_unit_count"],
    "old_boundary_aggregation": dict(sorted(old_aggregation.items())),
    "old_to_new_units": old_to_new,
    "unit_scale": "sentence or clause; coordinated regulated acts split; headings separate. Changes from the previous run: "
                  "u022 split into u022a-c (three coordinated rights); u111a and u111b merged into u111 (one limitation)",
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
    "audit_0930_units_faithful": audit_0930_faithful,
    "audit_0930_units_unfaithful_repaired": audit_0930_unfaithful,
    "statuses_dropped_by_repair": "none: every rejected unit stays READINGS, with narrower or different candidates; the claimed "
                                  "bytes are unchanged but what a covered byte claims is now weaker and disclosed (see units.json)",
    "covered_by_rights_readings_bytes": right_bytes,
    "covered_by_rights_units": right_ids + ["u111"],
    "asserted_reading_set_units": ["u054"],
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
        "limitation and bar act on rights lines fixed in the document; here every line is a reading-set candidate, so the u111 limitation has empty scope (limitation_terms 0) until per-choice elaboration exists",
        "document reading sets cannot hold norm content, so u017, u052, u112, u114 keep companion documents for their norm candidates",
        "load time: validating 20 right reading sets takes about 85 seconds per document load"],
    "no_invented_permissions": {
        "claims": "every claim predicate is obligation-role with completion 'deny' (= not required); no permission predicate is used for a duty, so no prohibition makes anything permitted for anyone else. The state reading is the same duty guarded by is_state: for non-states its completion is 'not required', declared and not derived from the source (witnesses.json shows the rule decides every state under both completions and that dropping it loses the conclusion)",
        "liberties": "the seven liberty predicates are permission-role with completion 'deny' (the tool requires some completion); in the liberty reading the rule is unconditional over the whole person sort, so the completion is never consulted (witnesses.json, both completions); in the other readings the predicate is mentioned by no rule. This stray declaration is flagged for the audit",
        "u074": "unchanged: unconditional prohibition; completion never consulted",
        "u052_u112_u114": "norm candidates unchanged in form: unconditional prohibitions over a sort whose description carries the conditions (prose-scoped), completion never consulted",
        "u041": "holder sort charged_person carries 'charged with a penal offence' as prose; no duty is stated for anyone else",
        "u035_u039": "holder sorts person_with_violated_rights and person_in_determination carry the scope as prose; a duty is stated "
                     "only toward their members and nobody is permitted anything; completion 'deny' means 'not required'",
        "u054": "asserted formulas over has_a_nationality and grants_nationality: no norm predicate, no default, no permission",
        "polarity_repairs": "u029, u032, u033a, u035, u039, u046, u049, u077 now carry one duty (or the avoiding duty plus a "
                            "liberty); no 'allow' reading of a prohibition was added"},
    "audit_repairs_0930": AUDIT_REJECTED,
    "presupposition_check": "No heading or speaker marker presupposes a substantive claim; the labelled units are unchanged from the audited previous run. u060 (the family is the natural and fundamental group unit) stays UNFORMALISED as an evaluative claim.",
    "checks": {
        "document_load": "PASS", "byte_partition": "PASS (units partition all 10,916 bytes)",
        "document_check": "PASS", "premises": verdict["premises"], "reading_plan": {k: verdict["reading_plan"][k] for k in ("route", "choice_count") if k in verdict["reading_plan"]},
        "rights_report": verdict["rights"]["report_status"],
        "reading_sets_validated_at_load": "PASS (each right candidate elaborated through the rights route; each ordered pair separated by a checked finite situation)",
        "companion_documents": companion_docs,
        "witnesses": "PASS: rule kept entails its conclusion under both completions with replayed certificates; dropping the rule loses it",
        "render": "PASS (rendered.md, readings-rendered.md)",
        "english_vocabulary_lint": LINT},
    "document_id": verdict["document_id"], "source_id": verdict["source_id"], "coverage_tool": cov,
}
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
print(json.dumps({k: metrics[k] for k in ("unit_counts_by_status", "bytes_by_status", "claimed_covered_bytes",
                                            "claimed_covered_percent", "audit_verified_covered_bytes",
                                            "old_boundary_aggregation", "missing_feature_tally")}, indent=1))
