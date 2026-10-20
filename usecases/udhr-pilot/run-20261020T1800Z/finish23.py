"""Write units.json, metrics.json and the evidence for the 2026-10-18T1800Z run (language at ve-green-eff-20261018-1). Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261018T1800Z/finish23.py

The run starts from the 20261018T0600Z run (kept in previous-20261018T0600Z/). Three plan-directed changes, no feature upgrade:
JT-0p item 2 (u010, u060), ET-0 (u042, u043), and JT-0p item 1 (the open-term class instrument: ledger fields only).
Inputs: this run's saved check results (parts-check.json, unit-compare.json, companions-check.json, witnesses.json, evidence/, experiment-whole/whole-check.json).
"""
import json
import re
from collections import Counter
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE / "previous-20261018T0600Z"
m = json.loads((PREV / "metrics.json").read_text())
old_m = deepcopy(m)
ud = json.loads((PREV / "units.json").read_text())
pc = json.loads((HERE / "parts-check.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
comp = json.loads((HERE / "companions-check.json").read_text())
wit = json.loads((HERE / "witnesses.json").read_text())["norm_defaults_status"]
compare = json.loads((HERE / "unit-compare.json").read_text())
refusal = json.loads((HERE / "refusal-test.json").read_text())
refusal43 = json.loads((HERE / "refusal-test-u043.json").read_text())
seeded = json.loads((HERE / "seeded-bugs-translation.json").read_text())
rebuild_cmd = json.loads((HERE / "evidence" / "rebuild-command.json").read_text())
et0 = json.loads((HERE / "evidence" / "et0-rerun-part01-prlimit.json").read_text())
legacy_cov = json.loads((HERE / "coverage.json").read_text())["coverage"]
legacy_ver = json.loads((HERE / "verdict.json").read_text())["report"]
phase1 = json.loads((HERE / "evidence" / "judgment-terms-instrument-udhr-jt0p.json").read_text())
OLD, TAG = "ve-green-tarch-histdep", "ve-green-eff-20261018-1"
RUN, PREV_RUN = "run-20261018T1800Z", "run-20261018T0600Z"
prev_parts = json.loads((PREV / "parts-check.json").read_text())
CHANGED = ["u010", "u060", "u042", "u043"]

for n, v in pc.items():
    assert "error" not in v and v["premises"]["status"] == "model" and v["conflict"] in (None, "CONFLICT-FREE"), (n, v)
assert "error" not in whole.get("load", {}) and "error" not in whole.get("check", {}), whole
assert whole["load"]["coverage_percent"] == 100 and whole["check"]["premises"] == "model" and whole["check"]["readings_status"] == "CONFLICT-FREE", whole
assert sorted(d["unit"] for d in compare["differences"]) == sorted(CHANGED) and not compare["unexpected"] and compare["units"] == 130
assert et0["verdict"] == "ok" and et0["premises"] == "model" and et0["conflict"] == "CONFLICT-FREE"

# ------------------------------------------------------------------------------------------------ parts: vocabulary facts
fronts = {}
for n in range(1, 5):
    raw = (HERE / f"translation-part0{n}.ve.md").read_bytes()
    fronts[n] = json.loads(raw.split(b"---\n", 2)[1])
shared = fronts[1]["open_terms"]
assert [t for t in shared if t["name"] != "heavier"] == fronts[2]["open_terms"] == fronts[3]["open_terms"] == fronts[4]["open_terms"], "the shared record list differs between parts"
assert [t["name"] for t in shared].count("heavier") == 1 and all("heavier" not in [t["name"] for t in fronts[n]["open_terms"]] for n in (2, 3, 4))   # ET-0's term is in part01 only
open_names = [t["name"] for t in shared]
for n, f in fronts.items():
    sorts = f["environment"]["vocabulary"]["sorts"]
    assert "entity" not in sorts and sum(1 for s in sorts.values() if s["verbalisation"]["singular"] == "thing") <= 1, n     # X2: no `entity`, one `thing`
regulated = {n: sorted(p for p, d in f["environment"]["vocabulary"]["predicates"].items() if "regulated" in d) for n, f in fronts.items()}
distinct_regulated = sorted({p for v in regulated.values() for p in v})

# ------------------------------------------------------------------------------------------------ the open-term class instrument (JT-0p item 1)
CLS = dict(phase1["open_term_class"])
NEW_CLASS = {
    "free_education": ("judgment", "'free' needs a threshold the text does not state (does a nominal fee, or the cost of books, make education not free?); a graded word"),
    "equal_pay_for_equal_work": ("judgment", "which work counts as equal and which pay as equal needs a comparison standard the text does not state; it also classifies work, so it is borderline"),
    "adequate_standard_of_living": ("judgment", "'adequate' is evaluative: the standard of adequacy is not stated"),
    "moral_and_material_interests": ("classification", "which interests result from a production is a matter of classifying interests; no evaluative or threshold standard is involved"),
    "own_country": ("classification", "which country is a person's own is a matter of classifying the relation (the words do not say which relation); no evaluative standard"),
    "heavier": ("judgment", "a graded comparative: the standard for comparing the weight of two penalties is not stated"),
}
for name, (cls, _why) in NEW_CLASS.items():
    CLS[name] = cls
BORDER = sorted(set(phase1["borderline_judgment_terms"]) | {"equal_pay_for_equal_work"})
assert set(CLS) >= set(open_names), sorted(set(open_names) - set(CLS))
assert set(CLS) == set(open_names), sorted(set(CLS) - set(open_names))
assert set(CLS.values()) <= {"judgment", "classification", "exception", "attitude", "proportion"}
CLS = {n: CLS[n] for n in open_names}
reasons = {n: why for n, (_c, why) in NEW_CLASS.items()}
reasons["of_greatest_importance_for"] = "carried from phase 1 (judgment): 'greatest importance' is graded and evaluative; the record replaces the unused greatest_importance placeholder (JT-0p item 2)"
reasons["natural_and_fundamental_group_unit_of_society"] = "carried from phase 1 (judgment): 'natural' and 'fundamental' need standards the text does not state; the record replaces the unused natural_group_unit placeholder (JT-0p item 2)"
terms_unchanged = [n for n in open_names if n in phase1["open_term_class"]]
differs_from_phase1 = [n for n in terms_unchanged if CLS[n] != phase1["open_term_class"][n]]
assert not differs_from_phase1

# ------------------------------------------------------------------------------------------------ the ledger
rows = ud["units"]
byid = {u["id"]: u for u in rows}
span = lambda u: u["span"][1] - u["span"][0]
UNSPEC_NOTE = ("The words name no one who must act, so no bearer is named. Completion 'unspecified' (norm-defaults@0): a case outside the rule is UNDECIDED, "
               "never permitted and never 'not required'.")
for uid in CHANGED:
    byid[uid]["previous_missing_feature"] = byid[uid].pop("missing_feature")
    byid[uid].pop("blocker_detail", None)
    byid[uid]["part_document"] = "translation-part01.ve.md" if uid in ("u010", "u042", "u043") else "translation-part02.ve.md"
    byid[uid]["status_in_previous_run"] = "UNFORMALISED"
    byid[uid]["in_document_content"] = True
u = byid["u010"]
u.update({"status": "OPEN", "open_terms": ["of_greatest_importance_for"], "semantic_kind": "asserted judgment", "claimed": True,
          "plan_repair": {"plan": "judgment-terms", "item": "JT-0p"}, "blocker_cleared": "other:evaluative_open_claim",
          "formal_depth": "1 ground atom, of_greatest_importance_for(common_understanding_of_these_rights_and_freedoms, full_realization_of_this_pledge), "
                          "kind asserted, meaning {open: [of_greatest_importance_for]}; sort `thing`; no new profile",
          "jt0p_note": "JT-0p item 2: an asserted judgment, OPEN. The atom says that a common understanding of these rights and freedoms is of the greatest importance for "
                       "the full realization of this pledge; whether it is, is a judgment the text leaves to no one it names (decider unresolved_decider). The recital "
                       "function of 'Whereas' (a reason given for the proclamation) is not represented. Bytes are claimed until the targeted audit finds the unit unfaithful (plan JT-0p); "
                       "not audit-verified yet.",
          "audit_pending": "JT-0p item 2 (a plan repair): audit-verified only after an audit finds it FAITHFUL"})
u = byid["u060"]
u.update({"status": "OPEN", "open_terms": ["natural_and_fundamental_group_unit_of_society"], "semantic_kind": "asserted judgment", "missing_feature": "presupposition",
          "claimed": False, "plan_repair": {"plan": "judgment-terms", "item": "JT-0p"}, "blocker_cleared": "other:evaluative_open_claim",
          "formal_depth": "1 ground atom, natural_and_fundamental_group_unit_of_society(the_family), kind asserted, meaning {open: [natural_and_fundamental_group_unit_of_society]}; "
                          "sort `thing`; 'the family' is the institution (one constant), not any one family; no new profile",
          "jt0p_note": "JT-0p item 2: an asserted judgment, OPEN, written and audited but NOT claimed (DRI X5): 'the' (uniqueness: the one natural and fundamental group unit) is not "
                       "represented; that is presupposition's. u061 reads 'everyone ... the family' distributively for its own entitlement."})
ET_NOTE = ("ET-0 rerun (events-time-causation plan section 5, content pre-registered on research/events-time-causation-p1: part01.u042u043.ve.md and ledger-proposal.json, "
           "used unchanged). Claimed:false as the ledger proposal says: its bytes count only after this run's audit.")
u = byid["u042"]
u.update({"status": "CHECKED", "claimed": False, "plan_repair": {"plan": "events-time-causation", "item": "ET-0"}, "blocker_cleared": "time",
          "semantic_kind": "norm (permission, bearer unassigned)",
          "formal_depth": "1 norm unit: finding_of_guilt_permitted(finding) is forbidden if some act, committed on some day, is the ground of the finding and did not constitute a penal "
                          "offence under national or international law on that day (sorts finding, act, day; regulated predicate with the act '{0} take place', default unspecified)",
          "et0_note": ET_NOTE, "et0_ledger_proposal": {"id": "u042", "span": [4151, 4351], "bytes": 200, "status_in_run": "UNFORMALISED", "status_on_load": "CHECKED",
                                                       "part_document": "part01.u042.ve.md", "audit": "DEFERRED (model call)", "claimed": False},
          "companions": ["readings/u042.prohibited.ve.md"], "norm_defaults_companions": ["readings/u042.prohibited.ve.md"],
          "claim_pending_audit": 200, "words_only_single_reading": True, "single_reading": True,
          "unchecked_note": "Not part of any reading: the words do not say who may not hold a person guilty. The two lint-refused wordings (committed_on, constitutes_penal_offence_on) render as recorded relations; ET-6 restates them."})
u = byid["u043"]
u.update({"status": "READINGS", "claimed": False, "plan_repair": {"plan": "events-time-causation", "item": "ET-0"}, "blocker_cleared": "time",
          "semantic_kind": "norm (permission, bearer unassigned), two readings",
          "open_terms": ["heavier"], "reading_set": "rs_u043", "candidates": ["universal", "existential"],
          "formal_depth": "2 candidates (universal, existential), each content in translation-part01.ve.md, one reading set whose separating situation Lean admitted (two penalties applicable on the day, "
                          "the imposed one heavier than the lighter only); sorts imposition, penalty, applicability (plus act, day); heavier_than a named open comparison (term heavier)",
          "et0_note": ET_NOTE + " Plan P2: 'the one that was applicable' admits two readings, universal (heavier than every penalty applicable on that day, given that one is: the pre-registered "
                      "text) and existential (heavier than some penalty applicable then); they differ only when several penalties were applicable on that day, where the existential reading forbids more.",
          "et0_ledger_proposal": {"id": "u043", "span": [4351, 4469], "bytes": 118, "status_in_run": "UNFORMALISED", "status_on_load": "OPEN", "open_terms": ["heavier"],
                                  "part_document": "part01.u042u043.ve.md", "audit": "DEFERRED (model call)", "claimed": False},
          "companions": ["readings/u043.universal.ve.md", "readings/u043.existential.ve.md"],
          "norm_defaults_companions": ["readings/u043.universal.ve.md", "readings/u043.existential.ve.md"],
          "claim_pending_audit": 118, "words_only_single_reading": False,
          "reading_basis": "the definite 'the one' with several applicable penalties (the task's plan P2); the existential guard is the pre-registered universal guard with `forall` read as `exists`",
          "unchecked_note": "Not part of any reading: the words do not say who may not impose the penalty. 'Applicable at the time the offence was committed' is one applicability per penalty, act and day."})
for uid in CHANGED:
    byid[uid]["status_in_run_20261018T1800Z"] = byid[uid]["status"]
for uid, r in byid.items():
    r["judgment_terms"] = [t for t in r.get("open_terms", []) if CLS.get(t) == "judgment"]
    assert all(t in CLS for t in r.get("open_terms", [])), (uid, [t for t in r["open_terms"] if t not in CLS])
ud["audit_note_20261018T1800Z"] = ("this run changes four units by plan direction: u010, u060 (JT-0p item 2) and u042, u043 (ET-0); none is audit-verified yet. u010 is claimed until audited; "
                                  "u060, u042 and u043 are claimed:false (X5 / the ledger proposal). Every other row is the previous run's (judgment_terms is a new ledger field).")
(HERE / "units.json").write_text(json.dumps(ud, indent=1, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------------------------------------ numbers
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")
order = [x["id"] for x in rows]
counts = Counter(x["status"] for x in rows)
bytes_by = Counter()
for x in rows:
    bytes_by[x["status"]] += span(x)
assert sum(bytes_by.values()) == 10916 and len(rows) == 130
claimed = sum(span(x) for x in rows if x["status"] in COVERED and x.get("claimed", True))
covered = sum(span(x) for x in rows if x["status"] in COVERED)
verified = set(old_m["audit_verified_units"])
assert all(byid[i]["status"] in COVERED and byid[i].get("claimed", True) for i in verified) and not (verified & set(CHANGED))
verified_bytes = sum(span(byid[i]) for i in verified)
assert verified_bytes == old_m["audit_verified_covered_bytes"] == 4820
pending_claimed = [i for i in CHANGED if byid[i].get("claimed", True)]
pending_unclaimed = [i for i in CHANGED if not byid[i].get("claimed", True)]
assert claimed == 4820 + 132 and pending_claimed == ["u010"]
tally = Counter(x["missing_feature"] for x in rows if x["status"] == "UNFORMALISED")
bylu = {x["id"]: x for x in rows}
# aggregated to the old (116) unit boundaries
agg = Counter()
for old, news in old_m["old_to_new_units"].items():
    s = {bylu[n]["status"] for n in news}
    agg[next(iter(s)) if len(s) == 1 else "MIXED"] += 1
# judgment-term units/bytes
jt_units = [x for x in rows if x["judgment_terms"]]


def split(rows_, key):
    out = {}
    for x in rows_:
        out[key(x)] = out.get(key(x), 0) + 1
    return dict(sorted(out.items()))


def split_bytes(rows_, key):
    out = {}
    for x in rows_:
        out[key(x)] = out.get(key(x), 0) + span(x)
    return dict(sorted(out.items()))


mf = lambda x: x.get("missing_feature") or "none"
judgment_term_units = {"total": len(jt_units), "by_status": split(jt_units, lambda x: x["status"]), "by_missing_feature": split(jt_units, mf)}
judgment_term_bytes = {"total": sum(span(x) for x in jt_units), "by_status": split_bytes(jt_units, lambda x: x["status"]),
                       "by_missing_feature": split_bytes(jt_units, mf)}
by_class = {}
for c in ("attitude", "classification", "exception", "judgment", "proportion"):
    us = [x for x in rows if any(CLS.get(t) == c for t in x.get("open_terms", []))]
    by_class[c] = {"units": len(us), "bytes": sum(span(x) for x in us)}
class_counts = dict(sorted(Counter(CLS.values()).items()))
jt = {"open_term_class": CLS, "open_term_class_borderline": BORDER, "class_counts": class_counts, "judgment_term_units": judgment_term_units,
      "judgment_term_bytes": judgment_term_bytes, "units_by_open_term_class": by_class,
      "judgment_terms": {x["id"]: x["judgment_terms"] for x in rows if x["judgment_terms"]},
      "reasons_for_new_terms": reasons, "terms_unchanged_since_20261012T1800Z": terms_unchanged,
      "differs_from_phase1": differs_from_phase1,
      "phase1_reference": "git show research/judgment-terms-p1:docs/research/evidence/judgment-terms/instrument-udhr-jt0p.json (copied to evidence/judgment-terms-instrument-udhr-jt0p.json)",
      "note": "ledger fields only: they change no status or content and do not make a unit a changed unit (JT-0p item 1)"}
(HERE / "judgment-terms.json").write_text(json.dumps(jt, indent=1, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------------------------------------ metrics
m["run"] = RUN
m["previous_run"] = f"{PREV_RUN} ({OLD}); its parts, units, readings and metrics are in previous-20261018T0600Z/"
m["previous_baseline"] = OLD
m["baseline"] = TAG
m["features_merged_since_previous_baseline"] = [
    "no construct, profile or sentence form was found that this run tried to use beyond the two directed plan sections. Merges since ve-green-tarch-histdep (155 commits) are jt-1, et-3, et-7, pk-1s, fsf-r1, me-1b, me-1c, "
    "ties-me-1a/b/c, speed-abcache, tarch-manifest-ops and eff-20261018-1 (trust classes, manifests, tests, speed and evidence tooling); this run did not search the 38 remaining "
    "UNFORMALISED units for newly expressible ones, because its instructions direct only JT-0p and ET-0."]
m["feature_upgrades"] = {"bytes": 0, "count": 0, "note": "none: the four changed units are plan-directed repairs, not upgrades from a newly merged feature", "units": []}
m["plan_repairs"] = [{"unit": "u010", "plan": "judgment-terms", "item": "JT-0p"}, {"unit": "u060", "plan": "judgment-terms", "item": "JT-0p"},
                     {"unit": "u042", "plan": "events-time-causation", "item": "ET-0"}, {"unit": "u043", "plan": "events-time-causation", "item": "ET-0"}]
m["plan_repairs_note"] = ("JT-0p item 2 (u010, u060: UNFORMALISED -> OPEN) and ET-0 (u042: UNFORMALISED -> CHECKED; u043: UNFORMALISED -> READINGS in the ledger, OPEN in the loader) landed; "
                          "JT-0p item 1 (the open-term class instrument) is ledger fields only and is not a changed unit. The carried plan repairs (u097 QT-0p, u085, u091, u106 AP-0 item 1; "
                          "u039 not landed) are in plan_repairs_in_carried_state. QT-0p's preconditions were re-checked: u097's span is 8857-8933 and part03 differs from the previous run's only in "
                          "the shared open-term record list.")
m["changed_units"] = list(CHANGED)
m["units_changed_this_run"] = list(CHANGED)
for k in ("repaired_units", "audit_repairs", "units_rejected_by_audit_and_repaired", "units_repaired_same_defect_not_rejected"):
    m[k] = []
m["repaired_unit_reasons"] = {}
m["audit_repairs_previous_run"] = old_m["audit_repairs"]
m["previous_run_unit_counts_by_status"] = old_m["unit_counts_by_status"]
m["unit_counts_by_status"] = dict(sorted(counts.items()))
m["bytes_by_status"] = dict(sorted(bytes_by.items()))
m["unit_counts_by_status_change"] = {"audit_repairs": {"bytes": 0, "units": 0}, "feature_upgrades": {"bytes": 0, "units": 0},
                                     "plan_repairs": {"bytes": sum(span(byid[i]) for i in CHANGED), "units": 4,
                                                      "by_plan": {"judgment-terms JT-0p": {"units": 2, "bytes": 198}, "events-time-causation ET-0": {"units": 2, "bytes": 318}}}}
m["claimed_covered_bytes_previous_run"] = old_m["claimed_covered_bytes"]
m["claimed_covered_bytes_previous_run_under_x5"] = old_m["claimed_covered_bytes"]
m["claimed_covered_bytes"] = claimed
m["claimed_covered_percent"] = round(100 * claimed / 10916, 2)
m["claimed_change_vs_previous_run_bytes"] = claimed - old_m["claimed_covered_bytes"]
m["claimed_change_vs_previous_run_bytes_under_x5"] = claimed - old_m["claimed_covered_bytes"]
m["claimed_covered_bytes_without_x5_marks"] = covered
m["claimed_covered_percent_without_x5_marks"] = round(100 * covered / 10916, 2)
m["covered_bytes_all_statuses_including_claimed_false"] = covered
m["claimed_false_pending_audit"] = {"units": pending_unclaimed, "bytes": sum(span(byid[i]) for i in pending_unclaimed if i != "u060"),
                                    "note": "u042 (200 B) and u043 (118 B) are claimed:false until this run's audit, as the ET-0 ledger proposal and the prompt say; u060 (66 B) is claimed:false for presupposition (X5). "
                                            "If the audit finds u042 and u043 FAITHFUL they add 318 B to the claimed and verified bytes."}
m["audit_verified_units"] = sorted(verified, key=order.index)
m["audit_verified_units_form_unchanged"] = list(m["audit_verified_units"])
m["audit_verified_units_reexpressed_this_run"] = []
m["audit_verified_units_withdrawn_this_run"] = {}
m["previous_run_audit_verified_covered_bytes"] = old_m["audit_verified_covered_bytes"]
m["audit_verified_covered_bytes"] = verified_bytes
m["audit_verified_covered_percent"] = round(100 * verified_bytes / 10916, 2)
m["audit_verified_note"] = ("verified = judged FAITHFUL by an audit and not changed since, and not marked claimed:false. The four changed units are not audited yet, so verified bytes stay at 4,820 "
                            "while claimed bytes rise to 4,952 (u010, 132 B, claimed until audited).")
m["audit_pending_units"] = ["u010"]
m["audit_pending_bytes"] = 132
m["audit_pending_claim_units"] = pending_unclaimed
m["audit_newly_verified_units"] = []
m["audit_20261018T0600Z"] = {"file": "previous-20261018T0600Z/AUDIT.md", "sampled": 20, "faithful": 20, "changed_units_checked": 0, "unfaithful": [],
                             "note": "the previous audit rejected no unit and asked for no repair; its verdicts are carried"}
m["audit_repair_this_run"] = "none: the previous audit (20261018T0600Z) rejected no unit"
m["missing_feature_tally_previous_run"] = old_m["missing_feature_tally"]
m["missing_feature_tally"] = dict(sorted(tally.items()))
assert sum(tally.values()) == counts["UNFORMALISED"] == 38
m["limits_unchanged_note"] = ("limits still blocking the 38 UNFORMALISED units: act-phrase grammar (8), rules (7), causation (4), attribution (4), right lines across open sets (4), time (3), comparison (2), "
                              "modality/belief (2), and singletons. ET-0 moved two 'time' units (u042, u043) and JT-0p two 'evaluative open claim' units (u010, u060) out of the tally.")
m["old_boundary_aggregation"] = dict(sorted(agg.items()))
m["previous_run_old_boundary_aggregation"] = old_m["old_boundary_aggregation"]
m["open_terms"] = [{"decided_by": t["decided_by"], "factors": t["factors"], "name": t["name"], "necessary": t["necessary"], "sufficient": t["sufficient"]} for t in shared]
m["open_terms_count"] = len(shared)
m["open_terms_added"] = ["heavier", "of_greatest_importance_for", "natural_and_fundamental_group_unit_of_society"]
m["open_terms_dropped"] = ["greatest_importance", "natural_group_unit"]
m["open_terms_replaced"] = {"greatest_importance": "of_greatest_importance_for", "natural_group_unit": "natural_and_fundamental_group_unit_of_society"}
m["reading_set_count"] = 12
m["reading_set_candidates"] = 24
m["previous_run_reading_set_count"] = old_m["reading_set_count"]
m["previous_run_reading_set_candidates"] = old_m["reading_set_candidates"]
m["reading_sets_multi_candidate"] = sorted(old_m["reading_sets_multi_candidate"] + ["u043"], key=order.index)
m["reading_sets_changed_this_run"] = {"u043": "new: universal and existential readings of 'the one that was applicable' (ET-0, plan P2)"}
m["words_only"] = {"rule": old_m["words_only"]["rule"], "readings_added_this_run": {"u043": ["universal", "existential"]}, "readings_removed_this_run": {}, "readings_changed_this_run": {},
                   "open_questions_listed_that_the_text_does_not_raise": 0,
                   "note": "u043's two readings come from the words 'the one that was applicable' (a definite description that fits one applicable penalty and does not say which to compare with when "
                           "several were applicable), as the ET-0 plan P2 and the run's instruction state; no outside knowledge is used. u010 and u060 are single-reading units. No other reading changed."}
m["part_checks"] = {n: {"seconds": v["seconds"], "premises": v["premises"], "readings_status": v["readings_status"], "conflict": v["conflict"],
                        "coverage_bytes_by_status": v["coverage"]["bytes_by_status"], "residual": v["coverage"]["residual"], "document_id": v["document_id"]} for n, v in pc.items()}
m["document_ids"] = {n: v["document_id"] for n, v in pc.items()}
m["document_ids_changed_in"] = [n for n in pc if pc[n]["document_id"] != prev_parts[n]["document_id"]]
parts = json.loads((HERE / "parts.json").read_text())
parts[0]["choices"] = 16
(HERE / "parts.json").write_text(json.dumps(parts, indent=1))
m["parts"] = parts
m["part_regulated_predicates"] = {f"translation-part0{n}.ve.md": len(v) for n, v in regulated.items()}
m["distinct_regulated_predicates_across_parts"] = len(distinct_regulated)
m["whole_document_legacy"]["coverage"] = legacy_cov
m["whole_document_legacy"]["premises"] = legacy_ver["premises"]
m["whole_document_legacy"]["note"] = ("translation.ve.md (the pre-parts form) keeps its units as they were; only its shared open-term record list was updated (greatest_importance -> of_greatest_importance_for, "
                                      "natural_group_unit -> natural_and_fundamental_group_unit_of_society), so no record names a removed term. It is no longer the source the parts are built from.")
m["companion_documents"] = len(comp)
m["status_witnesses"] = wit
m["status_witness_rows"] = sum(len(v) for v in wit.values())
assert len(comp) == 64 and m["status_witness_rows"] == 148
m["no_invented_permissions"]["status_rows"] = (f"{m['status_witness_rows']} Lean status rows over {len(comp)} companions, all as expected (135 over 61 are the previous run's, identical; 13 over 3 are "
                                               "new: u042.prohibited, u043.universal, u043.existential)")
m["no_invented_permissions"]["new_units"] = ("u042 and u043 declare the completion 'unspecified'; a case outside either rule is UNDECIDED in the Lean status rows (never permitted); u010 and u060 are assertions "
                                             "with no norm predicate")
m["qt0p_u097"]["in_this_run"]["note"] = ("carried unchanged. Preconditions re-checked: u097's span is 8857-8933; part03 differs from the previous run's only in the shared open-term record list. "
                                         "The isolated measurement (qt0p_isolated.py) was not re-run: it builds from the superseded previous-20261013T0600Z/ directory that is no longer in this run; "
                                         "the companion witnesses (probe UNDECIDED at a higher stage, three controls SETTLED yes) were re-run and are unchanged.")
m["rendering_change"] = {"what": "rendered-parts/ regenerated. Against the previous run's rendering: u010 now reads 'Open reading: \"common_understanding_of_these_rights_and_freedoms\" has the recorded relation "
                                  "\"of_greatest_importance_for\" to \"full_realization_of_this_pledge\".'; u060 reads 'Open reading: \"the_family\" is classified as \"natural_and_fundamental_group_unit_of_society\".'; "
                                  "u042 and u043 render their rule with the two lint-refused wordings as recorded relations (\"committed_on\", \"constitutes_penal_offence_on\"); and u025's distinguishing "
                                  "situation names one more element (\"thing is a thing\").",
                         "verdict": "JT-0p's rendering expectation holds: the rendering changes only at u010, at u060 and at the one line of u025's situation (u042 and u043 are ET-0's)"}
m["vocabulary_change_check"] = {
    "rule": "DRI 2026-10-14 15:30Z (2): after any vocabulary change rerun the situation step and check every existing unit parses unchanged",
    "situation_step": "this pilot has no nd.py: the step is witnesses_all.py (Lean status rows for every companion), check_parts.py (every part), compare_units.py (every unit's status and row) and, for the new reading set, the Lean-elaborated search in et0_apply.py",
    "changes": "JT-0p: sort `thing` (noun 'thing', plural 'things') in part01, part02 and the whole declaration, 3 constants, 2 predicates; ET-0: sorts finding, act, day, imposition, penalty, applicability and 11 predicates in part01 and the whole declaration",
    "result": {"differences": [d["unit"] for d in compare["differences"]], "environment_changed_in": compare["environment_changed_in"], "unexpected": compare["unexpected"], "units": compare["units"],
              "note": "130 of 130 units were compared with the previous run's parts: exactly the four changed units differ (status and row); every fenced unit of the other 126 parses with the same status and the same row"},
    "companions": "witnesses_all.py: 61 previous companions and 135 rows identical to the previous run's, plus 3 new companions and 13 rows",
    "entity_sort": "no sort named `entity` is declared in any part (checked by finish23.py); each part has at most one sort with the noun 'thing' (part01 and part02: `thing`)",
    "rebuild_command": "the committed `tools/readings_s1_pilot.py --rebuild-reading-ids <part> --check-noop` is NOT a no-op on the unchanged parts 1, 2, 4 and the whole declaration (part03 is), and the document it writes for them does not load "
                       "('invalid situation'): it extends situation bases by every declared sort and by the regulated predicates' relations, which Lean refuses in a base. The ids were therefore rebuilt by "
                       "vocab_patch.py (the reference build's rule: extend only by the new vocabulary, then recompute every id with VE's own identity functions); evidence/rebuild-command.json",
    "rust_time_limit": f"default VE_RUST_TIMEOUT kept. part01's check under `prlimit --as=6442450944`: cap {et0['address_space_cap_bytes']} bytes, wall {et0['wall_seconds']} s, peak child resident set "
                       f"{et0['peak_child_resident_set_mb_max']} MB (ve_service; sampled every 0.1 s, the Rust ve process peaked at {et0['peak_child_resident_set_mb'].get('ve', 'n/a')} MB in the samples); no raised limit (evidence/et0-rerun.json)"}
m["whole_document_experiment"]["components"] = {"load": whole["load"], "check": whole["check"]}
m["whole_document_experiment"]["result"] = "loads and checks at " + TAG
m["whole_document_experiment"]["note"] = ("whole.py was NOT re-run: the whole declaration's new vocabulary and the four units were applied to experiment-whole/translation-whole.ve.md directly by the same scripts as the parts "
                                           "(jt0p_apply.py, et0_apply.py), because the pre-parts translation.ve.md the builder reads is not kept up to date")
et0_json = {"plan": "events-time-causation ET-0 rerun", "rows": {"u042": {"bytes": 200, "status": "CHECKED", "claimed": False}, "u043": {"bytes": 118, "status": "OPEN in the loader, READINGS in the ledger", "claimed": False}},
            "part01": et0, "bar": {"u042_loads_and_checks": True, "part01_conflict_free_under_every_reading": et0["conflict"] == "CONFLICT-FREE", "premises_model": et0["premises"] == "model",
                                   "checker_available": et0["verdict"] == "ok"},
            "expected_vs_measured": {"u042_bytes": [200, 200], "u043_bytes": [118, 118]},
            "whole_declaration": {"load_seconds": whole["load"]["seconds"], "check_seconds": whole["check"]["seconds"], "premises": whole["check"]["premises"], "readings_status": whole["check"]["readings_status"]},
            "other_parts_seconds": {n: v["seconds"] for n, v in pc.items()},
            "note": "ET-6 takes the part01 wall time, peak child resident set and verdict as its check-time evidence. The whole-declaration run took about 3.8 times as long as last run's; its user CPU time equals its wall time (86 min vs 85 min), so the slowdown is added work, not contention (the VM's load average was 30 to 44 on 32 CPUs)."}
(HERE / "evidence" / "et0-rerun.json").write_text(json.dumps(et0_json, indent=1) + "\n")
m["et0_rerun"] = et0_json
m["jt0p"] = {"item1_instrument": "judgment-terms.json (and the keys open_term_class etc. below)", "item2_units": {"u010": {"bytes": 132, "status": "OPEN", "claimed": True},
                                                                                                           "u060": {"bytes": 66, "status": "OPEN", "claimed": False, "missing_feature": "presupposition"}},
             "preconditions": "u010 (span 1330-1462) and u060 (5733-5799) were unchanged and UNFORMALISED; the records greatest_importance and natural_group_unit were in the shared list and unused",
             "expected_vs_measured": {"u010_bytes_claimed": [132, 132], "u060_bytes": [66, 66], "other_units_keep_status": True, "premises_readings_conflicts_equal": True},
             "labels": "of_greatest_importance_for's record has the argument labels [understanding, realization] (distinct, not [thing, thing])", "verbalisation": "none for of_greatest_importance_for (the wording lint rejects '{0} is of the greatest importance for {1}')"}
m.update({k: jt[k] for k in ("open_term_class", "open_term_class_borderline", "judgment_term_units", "judgment_term_bytes", "units_by_open_term_class")})
m["open_term_class_counts"] = class_counts
m["open_term_class_reasons_for_new_terms"] = reasons
m["open_term_class_differs_from_phase1"] = differs_from_phase1
m["open_term_class_note"] = ("first live run of the instrument: no previous class of this pilot; the 52 terms unchanged since 20261012T1800Z reproduce phase 1's classes (0 differ); the seven new or renamed terms "
                             "are given a one-line reason in open_term_class_reasons_for_new_terms. 'heavier' (u043) is new this run.")
m["presupposition_check"] = ("No heading or speaker marker presupposes a substantive claim; no heading or label changed this run. u060 ('The family is the natural and fundamental group unit of society') is now an OPEN asserted "
                             "judgment whose presupposition ('the' = uniqueness) is recorded as missing_feature presupposition, claimed:false. u045b, u099b and u100b begin with a conjunction: each carries the subject "
                             "of the previous unit (noted in its elided field), not a presupposed claim.")
ch = m["checks"]
ch["companions"] = f"PASS: {len(comp)} companions check (premises model) and {m['status_witness_rows']} Lean status rows as expected (re-run at {TAG}; the previous run's 135 rows are identical, 13 are new for u042/u043)"
ch["legacy_document"] = {"check_seconds": 0.1, "coverage": "PASS (100%)", "premises": legacy_ver["premises"]}
ch["parts"] = (f"PASS: ve document check on all 4 parts at {TAG}: premises 'model' for every choice, CONFLICT-FREE under every reading "
               f"(part01 {pc['translation-part01.ve.md']['seconds']} s, part02 {pc['translation-part02.ve.md']['seconds']} s, part03 {pc['translation-part03.ve.md']['seconds']} s, part04 {pc['translation-part04.ve.md']['seconds']} s)")
ch["unchanged_units"] = "PASS: 126 of 130 units have the same status and row in the part files as in the previous run; the four others are the changed units"
ch["wrong_separating_situation"] = {"result": refusal["result"], "set": refusal["set"], "u043": refusal43}
ch["whole_document"] = {"check_seconds": whole["check"]["seconds"], "coverage_percent": whole["load"]["coverage_percent"], "load_seconds": whole["load"]["seconds"],
                        "premises": whole["check"]["premises"], "readings_status": whole["check"]["readings_status"], "tag": TAG}
ch["repaired_units"] = {"note": "no audit repair this run; the four plan repairs are listed in plan_repairs"}
ch["seeded_bugs_translation"] = seeded
ch["limits_met"][0] = (f"Rust checker: default VE_RUST_TIMEOUT kept. Part01 (11 regulated predicates, 21 sorts, 16 choices) checks under prlimit --as=6442450944 in {et0['wall_seconds']} s with a peak child resident set of "
                       f"{et0['peak_child_resident_set_mb_max']} MB; no raised limit was needed")
ch["limits_met"][1] = (f"the whole declaration as ONE document (experiment-whole/): six two-reading sets with their own vocabulary as RD-4b components and the rest in the main component (now with u043's set); at {TAG} "
                       f"load_document succeeds after {whole['load']['seconds']} s (coverage {whole['load']['coverage_percent']}%) and check_document answers {whole['check']['readings_status']}, premises "
                       f"'{whole['check']['premises']}' after {whole['check']['seconds']} s (previous run: 648.3 s and 687.0 s; about 3.8 times slower now: the process's user CPU time, 86 min, equals its 85 min wall time, so this is added cost of the whole declaration with the 7 new sorts, not queueing on a loaded machine, though the VM load average was 30 to 44)")
ch["build"] = "lake build (the default targets) and tools/rust_build.py (binary pinned in lean/checkers.lock) built in this worktree before the checks"
m["x5_claimed_false"]["note"] = ("u035 and u111 carried; u060 (presupposition) and, until the audit, u042 and u043 are also claimed:false (see claimed_false_pending_audit). "
                                 "Counts with and without the mark are both given.")
m["language_change_for_udhr"] = ("none for what a translator can write: no construct was added. The four changed units use constructs that were already there (reified events and days as sorts, an open "
                                 "comparison, an asserted ground atom, a reading set); ET-0 is a rerun made possible by the checker now answering on part01 with the larger vocabulary.")
m["language_findings"] = [
    f"u042 loads CHECKED (200 B) and u043 loads OPEN in the loader (118 B; READINGS in the ledger as a reading set of both readings, with a Lean-admitted separating situation); part01 stays CONFLICT-FREE under every "
    f"one of its 16 choices with premises 'model' ({et0['wall_seconds']} s under a 6 GB address-space cap, peak child {et0['peak_child_resident_set_mb_max']} MB): the ET-0 bar is met.",
    "u010 and u060 are OPEN asserted judgments (+132 B and +66 B); rendering changed only where JT-0p expected. Both are stated with no new profile; u060's 'the' (uniqueness) is the missing presupposition.",
    "the committed `--rebuild-reading-ids` command is unusable on this pilot's parts: not a no-op on the unchanged parts 1, 2, 4 and the whole declaration, and its output does not load (evidence/rebuild-command.json). "
    "This is a defect in the committed tool (it adds regulated-predicate relations to situation bases), not in the translation.",
    "the natural view still words the two ET-0 predicates as 'has the recorded relation \"committed_on\" to ...' because their English wordings are refused by the lint; ET-6 restates them.",
    "u043's two readings differ only when several penalties were applicable on the day; the Lean-checked separating situation has two (a lighter and a heavier one). 'The one' in the source is a definite description that presupposes one: that presupposition is not represented.",
    f"the whole declaration as ONE document loads in {whole['load']['seconds']} s and checks in {whole['check']['seconds']} s (about 3.8 times last run's 648.3 s and 687.0 s; CPU time equals wall time, so it is added work from the 7 new sorts and the new set, not machine load), CONFLICT-FREE under every reading, premises 'model'."]
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits)", "no seeded bug in product code (this run changed no file under ve/, lean/ or rust/); seeded faults in the translation are in seeded-bugs-translation.json",
                          "JT-5r (the 31 term splits) was not started, as directed", "no search of the other 38 UNFORMALISED units for newly expressible ones (not directed)"]
m["scope_tally"]["note"] = "carried unchanged (scope-tally.json): u010, u060, u042 and u043 keep their other:scope tag and governed_by; the tally changes no status or content"
m["seeded_bugs_translation"] = seeded
m["rebuild_command_check"] = rebuild_cmd
m["audit_20261018T1800Z_note"] = "the orchestrator's audit of this run should re-verify changed_units: u010, u060, u042, u043"
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
print("ok", dict(counts), dict(bytes_by), "claimed", claimed, "verified", verified_bytes, "agg", dict(agg), "tally", dict(tally))
print("judgment units", judgment_term_units, judgment_term_bytes, "class counts", class_counts)
