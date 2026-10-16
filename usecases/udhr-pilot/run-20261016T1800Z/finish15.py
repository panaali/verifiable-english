"""Write units.json, scope-tally.json and metrics.json for the 2026-10-14T1800Z run (language at ve-green-repo-map-untracked).

    uv run --frozen python usecases/udhr-pilot/run-20261014T1800Z/finish15.py

Nothing here calls a model. The inputs are this run's saved check results (parts-check.json, witnesses.json, companions-check.json,
refusal-test.json, qt0p-isolated.json, unit-compare.json, experiment-whole/whole-check.json, coverage.json, verdict.json) and the
previous run's files in previous-20261013T0600Z/. Units changed this run: repair13_specs.ORDER (two audit repairs, four plan repairs).
Scope tally (SC-M0): the governors are listed by hand below (a UDHR reading of the rule in the prompt); every other number is computed.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import repair13_specs as R  # noqa: E402

PREV = HERE / "previous-20261013T0600Z"
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
raw = (HERE.parent / "source" / "udhr.md").read_bytes()
assert hashlib.sha256(raw).hexdigest() == PIN

old = json.loads((PREV / "metrics.json").read_text())
prev_units = json.loads((PREV / "units.json").read_text())
pcheck = json.loads((HERE / "parts-check.json").read_text())
parts = json.loads((HERE / "parts.json").read_text())
wit = json.loads((HERE / "witnesses.json").read_text())["norm_defaults_status"]
comp = json.loads((HERE / "companions-check.json").read_text())
refusal = json.loads((HERE / "refusal-test.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
legacy_cov = json.loads((HERE / "coverage.json").read_text())["coverage"]
legacy_ver = json.loads((HERE / "verdict.json").read_text())["report"]
iso = json.loads((HERE / "qt0p-isolated.json").read_text())
compare = json.loads((HERE / "unit-compare.json").read_text())
witnesses13 = json.loads((HERE / "witnesses_repaired13.json").read_text())
assert not compare["unexpected"] and sorted(d["unit"] for d in compare["differences"]) == sorted(R.ORDER)

for name, v in pcheck.items():
    assert "error" not in v and v["premises"]["status"] == "model", (name, v)
assert legacy_cov["accounted_bytes"] == len(raw)
tool_status = {}
for v in pcheck.values():
    tool_status.update(v["unit_status"])
assert len(tool_status) == 130

# ---- audit of run-20261013T0600Z (previous-20261013T0600Z/AUDIT.md, VERDICTS block)
text = (PREV / "AUDIT.md").read_text()
block = text.split("VERDICTS:")[1]
verdicts = dict(re.findall(r"^(u\d+[a-d]?) (FAITHFUL|UNFAITHFUL)$", block, re.M))
assert len(verdicts) == 20
unfaithful = sorted(u for u, v in verdicts.items() if v == "UNFAITHFUL")
faithful = sorted(u for u, v in verdicts.items() if v == "FAITHFUL")
assert unfaithful == sorted(R.AUDIT_REPAIRED)

CHANGED = sorted(R.ORDER)
PLAN_REPAIRS = [{"unit": u, "plan": p["plan"], "item": p["item"]} for u, p in sorted(R.PLAN_REPAIRS.items())]
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")

# ---- X5 (DRI 2026-10-14): a unit whose own ledger text says part of its meaning is missing is `claimed: false`
CLAIMED_FALSE = {
    "u035": "the victim ('granted him') is not tied to the right-holder: 'the victim is the violation's own, not a third argument' (residual other:victim_inside_a_sort)",
    "u111": "the limitations are not attached to the rights they limit: 'limitation scope names rights, which are open sets here' (residual other:limitation_not_attached_to_rights_lines)",
}

# ---- scope (SC-M0). Governors, by hand; reach and effect as the prompt defines them.
heads = [r["id"] for r in prev_units["units"] if r["source"].startswith("#")]
assert len(heads) == 32
ids = [r["id"] for r in prev_units["units"]]
art = {r["id"]: r["article"] for r in prev_units["units"]}
body = [i for i in ids if i not in heads]
in_arts = lambda lo, hi: [i for i in body if art[i].startswith("Article ") and lo <= int(art[i].split()[1]) <= hi]
RIGHT_WORDS = re.compile(r"\bright|entitled|freedom|freely", re.I)
text_of = {r["id"]: r["source"] for r in prev_units["units"]}
cand_rights = [i for i in in_arts(3, 28) if RIGHT_WORDS.search(text_of[i])]          # units that use the words right / entitled / freedom
cand_all = in_arts(1, 28)                                                              # every unit of Articles 1-28 that is not a heading
assert set(cand_rights) <= set(cand_all)
FRONTIER = {
    "candidates": [
        {"id": "A", "reading": "the rights and freedoms of Articles 3-28: units whose words say right, entitled, freedom or freely",
         "units": cand_rights},
        {"id": "B", "reading": "every unit of Articles 1-28 (rights, freedoms, prohibitions and the rest)", "units": cand_all},
        {"id": "C", "reading": "also rights and freedoms the Declaration does not set forth (no unit of this document)", "units": []}],
    "union": sorted(set(cand_all), key=ids.index)}
GOVERNORS = [
    {"unit": "u019", "reach": "frontier", "effect": "frame", "judgement": True,
     "words": "Everyone is entitled to all the rights and freedoms set forth in this Declaration, without distinction of any kind",
     "why": "adds 'without distinction of any kind' to every right and freedom of the Declaration; which units are those rights is open",
     "frontier": FRONTIER, "governed": FRONTIER["union"]},
    {"unit": "u052", "reach": "anchor", "effect": "carve-out",
     "words": "This right may not be invoked in the case of prosecutions genuinely arising from non-political crimes ...",
     "why": "'This right' is the right to seek and to enjoy asylum (Article 14, first sentence); the sentence carves cases out of it",
     "governed": ["u051"]},
    {"unit": "u108", "reach": "frontier", "effect": "none", "judgement": True,
     "words": "Everyone is entitled to a social and international order in which the rights and freedoms set forth in this Declaration can be fully realized",
     "why": "names the Declaration's rights and freedoms as a set; changes no rule of them",
     "frontier": FRONTIER, "governed": FRONTIER["union"]},
    {"unit": "u111", "reach": "frontier", "effect": "carve-out",
     "words": "In the exercise of his rights and freedoms, everyone shall be subject only to such limitations as are determined by law ...",
     "why": "adds limits to the exercise of 'his rights and freedoms'; the text does not say which units those are",
     "frontier": FRONTIER, "governed": FRONTIER["union"]},
    {"unit": "u112", "reach": "frontier", "effect": "carve-out",
     "words": "These rights and freedoms may in no case be exercised contrary to the purposes and principles of the United Nations",
     "why": "'These rights and freedoms' points back to Article 29(2)'s phrase, itself open; carves out exercise contrary to the UN's purposes",
     "frontier": FRONTIER, "governed": FRONTIER["union"]},
    {"unit": "u114", "reach": "rules", "effect": "carve-out",
     "words": "Nothing in this Declaration may be interpreted as implying for any State, group or person any right to engage in any activity ...",
     "why": "'this Declaration' names every unit but itself; it excludes one implication from all of them",
     "governed": [i for i in body if i != "u114"]},
]
CONSIDERED_NOT = [
    {"unit": "headings", "ids": heads, "why": "title headings (Article N, Preamble, the title) only name their section: they govern nothing and are not tagged"},
    {"unit": "u011", "why": "'Now, therefore,' ends in a comma, not ':'; it joins the recitals to the proclamation and changes no condition"},
    {"unit": "u013a", "why": "'Proclaims this Declaration as a common standard of achievement' states the Declaration's status, not a condition of any rule; closest rule: a sentence that frames the whole text (not computed as one)"},
    {"unit": "u020", "why": "'Furthermore, no distinction shall be made ...' adds a further prohibition; it is itself a rule and changes no other unit's condition"},
    {"unit": "u067", "why": "'this right includes freedom to change his religion or belief' adds items to the right (Article 18); it narrows nothing"},
    {"unit": "u071a", "why": "'this right includes freedom to hold opinions without interference' adds items to the right (Article 19); it narrows nothing"},
    {"unit": "u103", "why": "'Parents have a prior right to choose the kind of education ...' is a right with a priority ('prior') over unnamed parties; it changes no other unit's condition by its words (the ledger already tags it as priority of rights)"},
    {"unit": "u110", "why": "'Everyone has duties to the community ...' states a duty; it does not change other units"},
]

def span_len(u):
    return next(r["span"][1] - r["span"][0] for r in prev_units["units"] if r["id"] == u)

by_unit_governors: dict[str, list[str]] = {}
for g in GOVERNORS:
    g["governed"] = [u for u in g["governed"] if u != g["unit"]]            # a governor does not govern itself
    g["governor_bytes"] = span_len(g["unit"])
    g["bytes"] = sum(span_len(u) for u in g["governed"])
    for u in g["governed"]:
        by_unit_governors.setdefault(u, []).append(g["unit"])
assert not (set(by_unit_governors) & set(heads))                                       # a title heading is never governed
governor_units = sorted({g["unit"] for g in GOVERNORS})

# ---- unit rows
rows = []
for row in prev_units["units"]:
    row = dict(row)
    uid = row["id"]
    row["status_in_previous_run"] = row["status"]
    if uid in verdicts:
        row["audit_20261013T0600Z"] = verdicts[uid] + (" (repaired this run)" if uid in unfaithful else "")
    for key, val in list(row.items()):
        if key.startswith("audit_2026") and not key.endswith("20261013T0600Z") and isinstance(val, str) and val.endswith("(repaired this run)"):
            row[key] = val.replace("(repaired this run)", "(repaired in a later run)")
    if "audit_repair" in row and uid in faithful:
        row["audit_repair"] = row["audit_repair"].replace("Pending a fresh independent audit.", "Verified FAITHFUL by the 2026-10-13T0600Z audit.")
    rows.append(row)
by_id = {r["id"]: r for r in rows}

UNCHECKED = ("Not part of any reading: the words do not say who must act, so the reading names no bearer. A reader who knows how the "
             "Declaration is used in later treaties may expect States to be the bearers.")
WORDING = ["other:cross_set_verdicts (premise verdict UNKNOWN: reading elaboration pending)",
           "other:english_wording (plain and unary base predicates render as 'classified as ...' unless the wording is one word after 'is')"]
for uid in R.ORDER:
    cid, spec, why = R.NEW[uid]
    row = by_id[uid]
    for key in ("candidates", "reading_set", "companions", "norm_defaults_companions", "formal_depth", "residual_missing_features", "note",
                "polarity_note", "words_only_single_reading", "unchecked_note", "partial_companion", "missing_feature", "blocker_detail",
                "previous_missing_feature"):
        row.pop(key, None)
    prev_missing = prev_units_row = next(r for r in prev_units["units"] if r["id"] == uid)
    row["status"] = "OPEN"
    row["candidates"] = [cid]
    row["open_terms"] = list(spec["open"])
    row["reading_set"] = f"rs_{uid}"
    row["companions"] = [f"readings/{uid}.{cid}.ve.md"]
    row["norm_defaults_companions"] = [f"readings/{uid}.{cid}.ve.md"]
    row["formal_depth"] = (f"1 candidate ({cid}), stated in the part document {row.get('part_document')} as content (norm-defaults@0, completion "
                           "'unspecified'; a rule over a plain property is stated as the assertion that the property holds of every case its guard "
                           "picks out, or as a plain norm where the predicate has two arguments), as an ordinary unit because the words support one "
                           "reading; the candidate also stands as a one-unit companion document with Lean status witnesses (a case inside the rule is "
                           "SETTLED, a case outside it UNDECIDED, never 'not required' and never permitted). No candidate names a bearer the words do "
                           "not name.")
    row["residual_missing_features"] = list(WORDING)
    row["words_only_single_reading"] = True
    row["single_reading"] = True
    row["in_document_content"] = True
    row["unchecked_note"] = UNCHECKED
    row["repair_13"] = R.REASON[uid]
    if uid in R.PLAN_REPAIRS:
        row["plan_repair"] = R.PLAN_REPAIRS[uid]
        row["previous_missing_feature"] = prev_units_row.get("missing_feature")
        row["note"] = {"u097": "Article 26: Education shall be free, at least in the elementary and fundamental stages",
                       "u085": "Article 23(2): Everyone, without any discrimination, has the right to equal pay for equal work",
                       "u091": "Article 25(1), first clause: the right to an adequate standard of living",
                       "u106": "Article 27(2): the right to the protection of the moral and material interests of an author"}[uid]
    else:
        row["audit_repair"] = ("Rejected by the 2026-10-13T0600Z audit (UNFAITHFUL: the two-candidate set fixed 'his country' to nationality or "
                               "residence and said these exhaust the phrase); repaired 2026-10-14T1800Z: one reading with the open term own_country "
                               "(which country is a person's own). Pending a fresh independent audit.")
        row["note"] = {"u049": "Article 13(2): everyone has the right to leave any country, including their own, and to return to their country",
                       "u077": "Article 21(2): everyone has the right of equal access to public service in their country"}[uid]
    if uid == "u097":
        row["probe"] = ("Must higher education be free under this sentence? -> UNDECIDED (education_free_required at a stage that is neither "
                        "elementary nor fundamental); controls: elementary, fundamental, both -> SETTLED yes (witnesses.json u097.free_required)")
    if uid in ("u085", "u091", "u106"):
        row["act_phrases_note"] = ("whole act phrase kept as one predicate's wording (AP-0 item 1); blind audit of the research branch: FAITHFUL "
                                   "(manage-agents/act-phrases-ap0-audit-check.final.md); u039 failed that audit and is not landed")
    if uid in ("u085", "u091", "u106", "u097"):
        row["blocker_cleared"] = prev_units_row.get("missing_feature")
    # the status the tools compute
for r in rows:
    assert tool_status[r["id"]] == (r["status"] if r["status"] != "READINGS" else tool_status[r["id"]]), r["id"]
    if r["status"] == "OPEN" and r["id"] in R.ORDER:
        assert tool_status[r["id"]] == "OPEN", r["id"]

# ---- claimed (X5) and scope tags
for r in rows:
    uid = r["id"]
    r["claimed"] = r["status"] in COVERED and uid not in CLAIMED_FALSE
    if uid in CLAIMED_FALSE:
        r["claimed_false_reason"] = CLAIMED_FALSE[uid]
    if uid in by_unit_governors or uid in governor_units:
        blockers = r.setdefault("other_blockers", [])
        if "other:scope" not in blockers:
            blockers.append("other:scope")
    if uid in by_unit_governors:
        gov = list(by_unit_governors[uid])
        if r.get("scoped_by_source"):
            sb = r["scoped_by_source"]
            gov += [x for x in (sb if isinstance(sb, list) else [sb]) if x not in gov]
        r["governed_by"] = sorted(set(gov), key=ids.index)
    if uid in governor_units:
        r["governor"] = {"reach": next(g["reach"] for g in GOVERNORS if g["unit"] == uid), "effect": next(g["effect"] for g in GOVERNORS if g["unit"] == uid)}

(HERE / "units.json").write_text(json.dumps({"source_sha256": PIN, "units": rows, "note": prev_units["note"]}, ensure_ascii=False, indent=2) + "\n")

# ---- scope-tally.json
def bucket(units):
    return {"units": len(units), "bytes": sum(span_len(u) for u in units)}

def total_by(key):
    out = {}
    for g in GOVERNORS:
        e = out.setdefault(g[key], {"governors": 0, "governed_units_sum": 0, "governed_bytes_sum": 0, "governed_distinct": set()})
        e["governors"] += 1
        e["governed_units_sum"] += len(g["governed"])
        e["governed_bytes_sum"] += g["bytes"]
        e["governed_distinct"] |= set(g["governed"])
    return {k: {"governors": v["governors"], "governed_units_sum": v["governed_units_sum"], "governed_bytes_sum": v["governed_bytes_sum"],
                "governed_units_distinct": len(v["governed_distinct"]), "governed_bytes_distinct": sum(span_len(u) for u in v["governed_distinct"])}
            for k, v in out.items()}

all_governed = sorted(set(by_unit_governors), key=ids.index)
tally = {
    "run": "udhr run-20261014T1800Z", "source_sha256": PIN, "rule": "SC-M0 (research/scope-p1 docs/research/evidence/scope/pilot-prompt-addition.md, unchanged)",
    "governors": [{k: v for k, v in g.items() if k in ("unit", "reach", "effect", "governed", "bytes", "governor_bytes", "judgement", "words", "why", "frontier")}
                  for g in GOVERNORS],
    "titles": {"units": heads, "reach": "label", "effect": "title", "governed": [], "bytes": 0, "title_bytes": sum(span_len(u) for u in heads),
               "note": "title headings govern nothing and are not tagged (the research script finds the same 32: 0 list lead-ins, 0 bold labels)"},
    "considered_not_governors": CONSIDERED_NOT,
    "totals": {"governor_units": len(GOVERNORS), "governor_bytes": sum(g["governor_bytes"] for g in GOVERNORS),
               "governed_units_distinct": len(all_governed), "governed_bytes_distinct": sum(span_len(u) for u in all_governed),
               "title_headings_not_counted": bucket(heads), "units_total": 130, "bytes_total": len(raw),
               "by_reach": total_by("reach"), "by_effect": {**total_by("effect"), "title": {"governors": len(heads), "governed_units_sum": 0, "governed_bytes_sum": 0}}},
    "reach_note": ("frontier = the text leaves the reach open; every candidate is listed and none is picked; the governed units of a frontier governor "
                   "are the union of its candidates (tagged as possibly governed). 'rules' (u114) names this Declaration, so its reach is every unit but itself."),
    "structural_check": ("the research script (research/scope/sc_m0_tally.py, run on run-20261012T1800Z) finds for the UDHR 32 title headings, 0 colon "
                         "lead-ins, 0 bold labels, 0 When/If headings: this run's units have the same headings, so the structural reaches (list, label) "
                         "are empty here as well. The six governors above are the frontier, anchor and rules reaches, which that script does not compute "
                         "(its note: compared by hand). Not re-run on this run's units."),
    "plan_expectation": "the plan expected only title headings; this tally finds 6 governors beyond them (2 of them judgement calls, marked), see considered_not_governors for the rest",
}
(HERE / "scope-tally.json").write_text(json.dumps(tally, ensure_ascii=False, indent=2) + "\n")

# ---- numbers
counts = Counter(r["status"] for r in rows)
bytes_by_status = Counter()
for r in rows:
    bytes_by_status[r["status"]] += r["span"][1] - r["span"][0]
claimed_rows = [r for r in rows if r["claimed"]]
claimed = sum(span_len(r["id"]) for r in claimed_rows)
claimed_without_x5 = sum(bytes_by_status[s] for s in COVERED)
old_claimed_x5 = old["claimed_covered_bytes"] - sum(span_len(u) for u in CLAIMED_FALSE)
assert claimed_without_x5 == old["claimed_covered_bytes"] + 533 and counts["READINGS"] == 9 and counts["OPEN"] == 27 and counts["UNFORMALISED"] == 42, (claimed_without_x5, counts)
missing = Counter(r["missing_feature"] for r in rows if r["status"] == "UNFORMALISED")
old_to_new = old["old_to_new_units"]
agg = Counter()
for children in old_to_new.values():
    sts = {by_id[c]["status"] for c in children}
    agg[next(iter(sts)) if len(sts) == 1 else "MIXED"] += 1
verified = sorted((set(old["audit_verified_units"]) | set(faithful)) - set(CHANGED) - set(CLAIMED_FALSE) - set(unfaithful), key=ids.index)
assert all(by_id[u]["status"] in COVERED and by_id[u]["claimed"] for u in verified)
verified_bytes = sum(span_len(u) for u in verified)
verified_before_x5 = sorted((set(old["audit_verified_units"]) | set(faithful)) - set(CHANGED) - set(unfaithful), key=ids.index)
newly_verified = sorted(set(faithful) - set(old["audit_verified_units"]), key=ids.index)
tool_bytes = Counter()
for v in pcheck.values():
    tool_bytes.update(v["coverage"]["bytes_by_status"])

# open terms (current)
sys.path.insert(0, str(HERE.parents[2] / "tools"))
import readings_s1_pilot as P  # noqa: E402
meta, _ = P.read(HERE / "translation.ve.md")
open_terms_now = [{"decided_by": t["decided_by"], "factors": t["factors"], "name": t["name"], "necessary": t["necessary"], "sufficient": t["sufficient"]}
                  for t in meta["open_terms"]]
old_names = {t["name"] for t in old["open_terms"]}
added_terms = sorted(t["name"] for t in open_terms_now if t["name"] not in old_names)
multi = [s for s in meta["reading_sets"] if len(s["readings"]) >= 2]
single = sorted((s["unit"] for s in meta["reading_sets"] if len(s["readings"]) == 1), key=ids.index)
part_regulated = {}
distinct_reg = set()
for n in range(1, 5):
    f = P.read(HERE / f"translation-part0{n}.ve.md")[0]
    regs = [k for k, d in f["environment"]["vocabulary"]["predicates"].items() if "regulated" in d]
    part_regulated[f"translation-part0{n}.ve.md"] = len(regs)
    distinct_reg |= set(regs)

metrics = dict(old)
for stale in [k for k in metrics if k.startswith("audit_20261012T1800Z")]:
    del metrics[stale]
status_wit = dict(wit)
metrics.update({
    "baseline": "ve-green-repo-map-untracked",
    "previous_baseline": old["baseline"],
    "previous_run": "run-20261013T0600Z (ve-green-eff-20261011-1); its translation, units, metrics and audit are in previous-20261013T0600Z/",
    "features_merged_since_previous_baseline": [
        "none a translator can write. The merges since ve-green-eff-20261011-1: readings-defaults RD-5 (a measured UDHR run, docs and tests), "
        "lean-first b14d (the readings-choices relay: Lean enumerates a reading set's choices; lean/VE/Service/ReadingsChoices.lean, a new service "
        "mode), runner-portability, arch-AR-3, fix/main-relay and fix/repo-map-untracked (tooling, gates and repository map). No profile, "
        "construct, checker rule or vocabulary limit changed for a translator."],
    "feature_upgrades": {"units": [], "count": 0, "bytes": 0,
                         "note": "no newly merged feature lets any UNFORMALISED unit move; every change this run is a repair directed by an audit or a research plan"},
    "language_change_for_udhr": ("none. No construct was added. The six changed units are repairs: two audit repairs (u049, u077) and four plan-directed "
                                 "repairs (u097 for the quantities plan QT-0p; u085, u091, u106 for the act-phrases plan AP-0 item 1). The other 124 units "
                                 "are the previous run's, unchanged: same status and same unit row in the part files (unit-compare.json)."),
    "changed_units": CHANGED,
    "units_changed_this_run": CHANGED,
    "plan_repairs": PLAN_REPAIRS,
    "audit_repairs": [{"unit": u, "audit": "20261013T0600Z", "reason": R.REASON[u]} for u in R.AUDIT_REPAIRED],
    "unit_counts_by_status_change": {
        "audit_repairs": {"READINGS": -2, "OPEN": 2, "bytes": span_len("u049") + span_len("u077")},
        "plan_repairs": {"UNFORMALISED": -4, "OPEN": 4, "bytes": sum(span_len(u) for u in R.PLAN_REPAIRS),
                         "by_plan": {"quantities QT-0p": {"units": ["u097"], "bytes": span_len("u097")},
                                     "act-phrases AP-0 item 1": {"units": ["u085", "u091", "u106"], "bytes": sum(span_len(u) for u in ("u085", "u091", "u106"))}}},
        "feature_upgrades": {"units": 0, "bytes": 0}},
    "claimed_covered_bytes": claimed,
    "claimed_covered_percent": round(100 * claimed / len(raw), 2),
    "claimed_covered_bytes_without_x5_marks": claimed_without_x5,
    "claimed_covered_percent_without_x5_marks": round(100 * claimed_without_x5 / len(raw), 2),
    "claimed_covered_bytes_previous_run": old["claimed_covered_bytes"],
    "claimed_covered_bytes_previous_run_under_x5": old_claimed_x5,
    "claimed_change_vs_previous_run_bytes": claimed_without_x5 - old["claimed_covered_bytes"],
    "claimed_change_vs_previous_run_bytes_under_x5": claimed - old_claimed_x5,
    "x5_claimed_false": {"rule": "DRI X5, 2026-10-14: a unit whose ledger entry is marked `claimed: false` (an OPEN unit with part of its meaning missing) is never counted as claimed or verified bytes",
                         "units": {u: {"bytes": span_len(u), "reason": why} for u, why in CLAIMED_FALSE.items()},
                         "bytes": sum(span_len(u) for u in CLAIMED_FALSE),
                         "note": "no ledger entry carried the mark before this run; the translator marks the two units whose own residual says part of the meaning is missing, for the auditor to confirm or lift. Counts with and without the mark are both given."},
    "previous_run_unit_counts_by_status": old["unit_counts_by_status"],
    "previous_run_old_boundary_aggregation": old["old_boundary_aggregation"],
    "previous_run_audit_verified_covered_bytes": old["audit_verified_covered_bytes"],
    "previous_run_reading_set_count": old["reading_set_count"],
    "previous_run_reading_set_candidates": old["reading_set_candidates"],
    "missing_feature_tally_previous_run": old["missing_feature_tally"],
    "unit_count": 130,
    "unit_counts_by_status": dict(sorted(counts.items())),
    "bytes_by_status": dict(sorted(bytes_by_status.items())),
    "old_boundary_aggregation": dict(sorted(agg.items())),
    "missing_feature_tally": dict(sorted(missing.items())),
    "audit_20261013T0600Z_note": ("the 2026-10-13T0600Z audit of the previous run (previous-20261013T0600Z/AUDIT.md): 20 sampled units, 18 FAITHFUL, 2 UNFAITHFUL "
                                  "(u049, u077: 'his country' restricted to nationality or residence and said to exhaust the phrase). Both are repaired this run "
                                  "(one reading, open term own_country) and wait for a fresh audit"),
    "audit_20261013T0600Z_units_faithful": faithful,
    "audit_20261013T0600Z_units_unfaithful": unfaithful,
    "audit_newly_verified_units": newly_verified,
    "audit_verified_covered_bytes": verified_bytes,
    "audit_verified_covered_percent": round(100 * verified_bytes / len(raw), 2),
    "audit_verified_covered_bytes_before_x5": sum(span_len(u) for u in verified_before_x5),
    "audit_verified_units": verified,
    "audit_pending_bytes": claimed - verified_bytes,
    "audit_verified_note": ("verified = judged FAITHFUL by an audit and not changed since, and not marked claimed:false. The six changed units are pending a "
                            "fresh audit (u049 and u077 were rejected, and lose their earlier verdicts); u035 and u111 were judged FAITHFUL but are marked "
                            "claimed:false (X5), so their bytes are neither claimed nor verified. The verified set also grows by the units the previous "
                            "run's audit passed"),
    "audit_verified_units_form_unchanged": [u for u in old["audit_verified_units_form_unchanged"] if u not in CHANGED],
    "audit_verified_units_reexpressed_this_run": [u for u in old["audit_verified_units_reexpressed_this_run"] if u not in CHANGED],
    "repaired_units": sorted(R.AUDIT_REPAIRED),
    "repaired_unit_reasons": {u: R.REASON[u] for u in R.AUDIT_REPAIRED},
    "units_rejected_by_audit_and_repaired": sorted(R.AUDIT_REPAIRED),
    "units_repaired_same_defect_not_rejected": [],
    "units_with_only_open_term_factors_rewritten": [],
    "reading_set_count": len(multi),
    "reading_set_candidates": sum(len(s["readings"]) for s in multi),
    "reading_sets_multi_candidate": sorted((s["unit"] for s in multi), key=ids.index),
    "single_reading_units": single,
    "single_reading_unit_count": len(single),
    "reading_sets_changed_this_run": {u: "two candidates (nationality, residence) -> one reading with the open term own_country; the set is removed"
                                      for u in R.AUDIT_REPAIRED},
    "open_terms": open_terms_now,
    "open_terms_count": len(open_terms_now),
    "open_terms_added": added_terms,
    "open_terms_dropped": [],
    "predicates_dropped": ["has_the_right_to_leave_and_return_nationality", "has_the_right_to_leave_and_return_residence",
                           "has_right_to_equal_public_service_access_nationality", "has_right_to_equal_public_service_access_residence"],
    "words_only": {"rule": old["words_only"]["rule"], "readings_added_this_run": {},
                   "readings_removed_this_run": {u: ["entitlement_nationality", "entitlement_residence"] for u in R.AUDIT_REPAIRED},
                   "readings_changed_this_run": {}, "open_questions_listed_that_the_text_does_not_raise": 0,
                   "note": "the audit-rejected nationality/residence readings and every reference to them are gone (companions, sets, units.json fields, witnesses, findings); 'his country' is the open term own_country"},
    "part_checks": {n: {"seconds": v["seconds"], "premises": v["premises"], "readings_status": v["readings_status"], "conflict": v["conflict"],
                        "coverage_bytes_by_status": v["coverage"]["bytes_by_status"], "residual": v["coverage"]["residual"],
                        "document_id": v["document_id"]} for n, v in pcheck.items()},
    "parts": parts,
    "part_regulated_predicates": part_regulated,
    "distinct_regulated_predicates_across_parts": len(distinct_reg),
    "parts_tool_status_bytes": dict(sorted(tool_bytes.items())),
    "whole_document_legacy": {"file": "translation.ve.md", "coverage": legacy_cov, "premises": legacy_ver["premises"],
                              "reading_plan_route": legacy_ver["reading_plan"]["route"], "why_not_content": old["whole_document_legacy"]["why_not_content"]},
    "whole_document_experiment": {"components": whole, "component_sets": ["u025", "u055", "u073", "u111"],
                                  "files": old["whole_document_experiment"]["files"]},
    "companion_documents": len(comp),
    "status_witnesses": status_wit,
    "status_witness_rows": sum(len(v) for v in wit.values()),
    "qt0p_u097": {"isolated_measurement": iso, "in_this_run": {"u097_status": "OPEN", "part03_open_delta_with_all_part03_changes": 362,
                                                               "note": "part03 OPEN +362 B = u097 76 + u085 85 + u091 201; u097 alone +76 B as the plan expected"},
                  "probe": "Must higher education be free under this sentence?",
                  "probe_rows": witnesses13["u097.free_required"],
                  "norm_defaults_gap": "education_free_required joins the gap list of part03 (the 'at least' leaves the other stages unspecified)"},
    "act_phrases_ap0": {"landed": ["u085", "u091", "u106"], "not_landed": {"u039": "failed the targeted blind audit (act-phrases-ap0-audit-check.final.md)"},
                        "status_rows": {k: v for k, v in witnesses13.items() if k.split(".")[0] in ("u085", "u091", "u106")},
                        "landed_as": "u085 and u091 as assertions over person (plain predicate, guard top); u106 as a plain norm unit over person and production "
                                     "(guard: authorship and the kinds); integrate.py keeps a plain predicate with two arguments as a norm unit"},
    "vocabulary_change_check": {"rule": "DRI 2026-10-14 15:30Z (2): after any vocabulary change rerun the situation step and check every existing unit parses unchanged",
                                "situation_step": "witnesses_all.py (Lean status rows for every companion) and check_parts.py/compare_units.py (every part); this pilot has no nd.py",
                                "result": compare, "entity_sort": "no sort named `entity` is declared; the new sort `production` (u106) is not reserved",
                                "rust_time_limit": "default VE_RUST_TIMEOUT kept (5 s); no prlimit run, so no raised limit and no peak resident-set record"},
    "scope_tally": {"file": "scope-tally.json", "governors": [g["unit"] for g in GOVERNORS], "totals": tally["totals"]},
    "checks": {
        "parts_cover_source_exactly": f"PASS ({len(parts)} slices concatenate to the pinned 10,916 bytes)",
        "parts": f"PASS: ve document check on all {len(parts)} parts at ve-green-repo-map-untracked: premises 'model' for every choice, CONFLICT-FREE under every reading",
        "legacy_document": {"coverage": "PASS (100%)", "premises": legacy_ver["premises"]},
        "companions": f"PASS: {len(comp)} companions check (premises model) and {sum(len(v) for v in wit.values())} Lean status rows as expected",
        "unchanged_units": f"PASS: {compare['units'] - len(compare['differences'])} of {compare['units']} units have the same status and the same row in the part files; the {len(compare['differences'])} that differ are the changed units",
        "wrong_separating_situation": refusal,
        "limits_met": [
            "Rust checker: one call is limited to 5 s (default VE_RUST_TIMEOUT kept); (measured in an earlier run, not re-run) a part with 19 regulated predicates (u001-u108, 16 choices) "
            "is refused with 'Rust checker failed ... timed out after 4.99 s' (CheckerUnavailable), so the four parts are the largest that check",
            "the whole declaration as ONE document (experiment-whole/): four two-reading sets with their own vocabulary as RD-4b components (u025, u055, u073, u111) and the rest in "
            "the main component, built by whole.py; load_document fails after " + str(whole["load"]["seconds"]) + " s with the Rust checker's 5 s limit "
            "(re-run this run; experiment-whole/whole-check.json)",
            "the whole declaration with every candidate in the main document (integrate.py u001 u114; measured earlier, not re-run): Lean elaborates it on "
            "the superposed route, but Python's one-element search finds no separating situation for u111's pair both_aims / listed_aims in 6 min 58 s "
            "(experiment-whole/integrate-whole.log), so no document is produced"]},
    "document_ids": {n: v["document_id"] for n, v in pcheck.items()},
})
# gaps per part (norm-defaults), for the record
metrics["presupposition_check"] = old["presupposition_check"] + (" This run: no heading changed; the four AP-0/QT-0p units and the two repaired units are not headings.")
# language findings: the previous run's, with every trace of the removed sets updated
findings = []
for f in old["language_findings"]:
    f = f.replace("the six component sets leave 16 choices in the main component", "the four component sets leave 16 choices in the main component")
    f = f.replace("the four parts still load and check at eff-20261011-1 (unchanged from ts-B1)", "the four parts load and check at ve-green-repo-map-untracked")
    f = f.replace("at eff-20261011-1 (unchanged from ts-B1)", "at ve-green-repo-map-untracked")
    if f.startswith("FINDING, reading sets of assertions only"):
        f = ("FINDING, reading sets of assertions only (no longer needed by this declaration: u077 was the example until 2026-10-14, when the audit "
             "showed its two readings did not exhaust 'his country' and it became one reading with an open term): once a set keeps only "
             "`forall x. P_i(x)` readings, Python's search has no norm content to enumerate; a translator must supply the model by hand")
    if f.startswith("LIMIT 1, size"):
        f = (f"LIMIT 1, size: the declaration needs {len(distinct_reg)} distinct regulated predicates across the parts (max {max(part_regulated.values())} in one part; "
             "see whole_document_experiment for the single-document count), within the 64 limit")
    findings.append(f)
findings.append("FINDING, two-argument entitlements (u106): a plain regulated predicate with two arguments cannot be turned into a `forall` assertion by this "
                "pilot's integration (it assumed one argument); u106 stays a plain norm unit over person and production. The natural view of a plain predicate "
                "still reads 'classified as <name>' (unchanged)")
findings.append("FINDING, scope (SC-M0): the plan expected only title headings in the UDHR; the tally finds 6 governors beyond them (u052 anchor; u019, u108, u111, u112 "
                "frontier; u114 rules). The 'rights and freedoms' of Articles 2, 28 and 29 name a set the document does not delimit, so their reach is a frontier "
                "with candidates, never one pick; see scope-tally.json")
metrics["language_findings"] = findings
metrics["limits_unchanged_note"] = "limits unchanged and still blocking the 42 UNFORMALISED units: act-phrase grammar (8), time (5), causation (4), attribution (4), rules (7), comparison (2), modality/belief (2), and singletons"
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n")
print(json.dumps({k: metrics[k] for k in ("unit_counts_by_status", "bytes_by_status", "claimed_covered_bytes", "claimed_covered_percent",
                                           "claimed_covered_bytes_without_x5_marks", "claimed_covered_percent_without_x5_marks",
                                           "audit_verified_covered_bytes", "audit_verified_covered_percent", "audit_pending_bytes",
                                           "old_boundary_aggregation", "missing_feature_tally", "reading_set_count", "reading_set_candidates",
                                           "single_reading_unit_count", "open_terms_count", "part_regulated_predicates", "audit_newly_verified_units",
                                           "distinct_regulated_predicates_across_parts")}, indent=1))
print(json.dumps(tally["totals"], indent=1)[:2500])
