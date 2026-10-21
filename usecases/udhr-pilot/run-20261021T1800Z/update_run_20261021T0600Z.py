"""Ledger of run 20261021T0600Z: units.json, metrics.json, judgment-terms.json from the previous run's copies (previous-20261020T1800Z/) and this run's saved checks.

    uv run --frozen python usecases/udhr-pilot/run-20261021T0600Z/update_run_20261021T0600Z.py

Idempotent: it always starts from previous-20261020T1800Z/.  Nothing here calls a model.  This run repairs the four units the 20261020T1800Z audit rejected
(u042, u043, u060, u061) and upgrades none (no construct a translator can write was merged between ve-green-sc-1ac and ve-green-sc-1ad).
"""
import json
import re
from collections import Counter
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE / "previous-20261020T1800Z"
RUN, PREV_RUN, TAG, OLD = "run-20261021T0600Z", "run-20261020T1800Z", "ve-green-sc-1ad", "ve-green-sc-1ac"
REPAIRED = ["u042", "u043", "u060", "u061"]
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")

old_m = json.loads((PREV / "metrics.json").read_text())
m = deepcopy(old_m)
ud = json.loads((PREV / "units.json").read_text())
pc = json.loads((HERE / "parts-check.json").read_text())
compare = json.loads((HERE / "unit-compare.json").read_text())
comp = json.loads((HERE / "companions-check.json").read_text())
wit = json.loads((HERE / "witnesses.json").read_text())["norm_defaults_status"]
seeded = json.loads((HERE / "seeded-bugs-translation.json").read_text())
rebuild = json.loads((HERE / "evidence" / "rebuild-command.json").read_text())
p01 = json.loads((HERE / "evidence" / "part01-check-sc1ad.json").read_text())
whole_file = HERE / "experiment-whole" / "whole-check.json"
whole = json.loads(whole_file.read_text())
phase1 = json.loads((HERE / "evidence" / "judgment-terms-instrument-udhr-jt0p.json").read_text())

for n, v in pc.items():
    assert "error" not in v and v["premises"]["status"] == "model" and v["conflict"] in (None, "CONFLICT-FREE"), (n, v)
assert sorted(d["unit"] for d in compare["differences"]) == sorted(REPAIRED) and not compare["unexpected"] and compare["units"] == 130
assert p01["verdict"] == "ok" and p01["premises"] == "model" and p01["conflict"] == "CONFLICT-FREE"
assert len(comp) == 61 and sum(len(v) for v in wit.values()) == 136, (len(comp), sum(len(v) for v in wit.values()))
assert "u042.prohibited" not in wit and "u043.universal" not in wit and "u043.existential" not in wit
assert all(o["as_expected"] for v in wit.values() for o in v)
whole_done = "error" not in whole.get("load", {"error": 1}) and "error" not in whole.get("check", {"error": 1}) and whole["load"]["seconds"] != 2033.0
print("whole-declaration results are this run's:", whole_done)

# ------------------------------------------------------------------------------------------------ vocabulary facts of the parts
fronts = {n: json.loads((HERE / f"translation-part0{n}.ve.md").read_bytes().split(b"---\n", 2)[1]) for n in range(1, 5)}
shared = fronts[1]["open_terms"]
assert shared == fronts[2]["open_terms"] == fronts[3]["open_terms"] == fronts[4]["open_terms"], "the shared record list differs between parts"
open_names = [t["name"] for t in shared]
assert "heavier" not in open_names
for n, f in fronts.items():
    voc = f["environment"]["vocabulary"]
    assert "entity" not in voc["sorts"] and sum(1 for s in voc["sorts"].values() if s["verbalisation"]["singular"] == "thing") <= 1, n
    assert not set(voc["sorts"]) & {"finding", "act", "day", "imposition", "penalty", "applicability", "family"}, n
    assert not set(voc["predicates"]) & {"finding_of_guilt_permitted", "on_account_of", "committed_on", "constitutes_penal_offence_on", "imposition_permitted",
                                         "imposes", "imposed_for", "applicability_of", "applicability_to", "applicable_on", "heavier_than"}, n
regulated = {n: sorted(p for p, d in f["environment"]["vocabulary"]["predicates"].items() if "regulated" in d) for n, f in fronts.items()}
distinct_regulated = sorted({p for v in regulated.values() for p in v})

# ------------------------------------------------------------------------------------------------ open-term classes
CLS = dict(old_m["open_term_class"])
del CLS["heavier"]
CLS = {n: CLS[n] for n in open_names}
assert set(CLS) == set(open_names) and set(CLS.values()) <= {"judgment", "classification", "exception", "attitude", "proportion"}
reasons = {k: v for k, v in old_m["open_term_class_reasons_for_new_terms"].items() if k != "heavier"}
BORDER = old_m["open_term_class_borderline"]
terms_unchanged = [n for n in open_names if n in phase1["open_term_class"]]
differs_from_phase1 = [n for n in terms_unchanged if CLS[n] != phase1["open_term_class"][n]]
assert not differs_from_phase1

# ------------------------------------------------------------------------------------------------ the ledger
rows = ud["units"]
byid = {u["id"]: u for u in rows}
span = lambda u: u["span"][1] - u["span"][0]
AUDIT = "AUDIT-20261020T1800Z.md"

U042_DETAIL = ("The 20261020T1800Z audit rejected the encoding: 'at the time when it was committed' compares the time of the act with the time of the law, and the civil `day` "
               "sort used for it cannot tell an act committed before a change of the law within that day from one committed after it. No finer notion of time is available to a "
               "translator (the event modules are not reachable from a document yet), so the unit is UNFORMALISED again (time). The reification of findings of guilt and of acts "
               "was accepted by the audit; only the day was not.")
U043_DETAIL = ("The 20261020T1800Z audit rejected the same temporal loss ('the time the penal offence was committed' as a civil day) and also the every/some pair: 'the one that was applicable' "
               "names one penalty to compare with, and the words do not themselves license two quantifications over several penalties, so the pair introduced a question the text does not raise. "
               "'A heavier penalty ... than the one' also compares two penalties (an order on penalties). Back to UNFORMALISED (time).")
for uid, prev_status, detail in (("u042", "CHECKED", U042_DETAIL), ("u043", "READINGS", U043_DETAIL)):
    old = byid[uid]
    keep = ("id", "article", "span", "source", "old_unit", "previous_unit", "part_document", "other_blockers", "governed_by", "status_in_run_20261013T0600Z",
            "status_in_run_20261018T1800Z", "status_in_run_20261019T0600Z", "audit_20261018T1800Z", "audit_20261019T0600Z")
    new = {k: old[k] for k in keep if k in old}
    new.update({"status": "UNFORMALISED", "missing_feature": "time", "previous_missing_feature": "time", "status_in_previous_run": prev_status, "claimed": False,
                "blocker_detail": detail, "judgment_terms": [], f"status_in_run_20261020T1800Z": prev_status,
                "audit_20261020T1800Z": "UNFAITHFUL (reverted to UNFORMALISED in run 20261021T0600Z)",
                "audit_repair": (f"Rejected by the 20261020T1800Z audit ({AUDIT}); repaired 2026-10-21 by returning the unit to UNFORMALISED (time). Its sorts, predicates"
                                 + (", open term" if uid == "u043" else "") + (" and reading set" if uid == "u043" else "") + " are removed from part01 and the whole declaration, "
                                 "and its companion documents and Lean status rows are gone. Not audit-verified; no bytes are claimed.")})
    byid[uid].clear()
    byid[uid].update(new)

u = byid["u010"]
u["claim_note_20261019T0600Z"] = "claimed since the 20261018T1800Z audit found the unit FAITHFUL"
u["audit_20261020T1800Z"] = "FAITHFUL"

u = byid["u060"]
for k in ("missing_feature", "jt0p_note"):
    u.pop(k, None)
u.update({"claimed": True, "status": "OPEN",
          "formal_depth": ("1 asserted formula over sort `thing`: natural_and_fundamental_group_unit_of_society(the_family) and every thing that is classified as "
                           "natural_and_fundamental_group_unit_of_society is the same as the_family; kind asserted, meaning {open: [natural_and_fundamental_group_unit_of_society]}; "
                           "'the family' is the institution (one constant), not any one family; no new profile"),
          "jt0p_note": ("JT-0p item 2: an asserted judgment, OPEN. The 20261020T1800Z audit rejected the unit because 'the ... group unit' conveys uniqueness and the content did not. "
                        "Repaired 2026-10-21: the content now has two conjuncts, that the family is the natural and fundamental group unit of society and that whatever is one is the family. "
                        "Whether English asserts or only presupposes that uniqueness is not represented; the content states it. Which sense of 'natural', 'fundamental' and 'group unit' "
                        "applies stays the open term (decider unresolved_decider)."),
          "audit_20261020T1800Z": "UNFAITHFUL (repaired in run 20261021T0600Z)",
          "audit_repair": (f"Rejected by the 20261020T1800Z audit ({AUDIT}): the uniqueness of 'the ... group unit' was acknowledged as unrepresented and an OPEN predicate does not supply it. "
                           "Repaired 2026-10-21: the uniqueness is now the second conjunct of the content (rendering: 'for every thing that is classified as ... , that thing is the same as \"the_family\"'). "
                           "Claimed, not audit-verified until an audit finds it FAITHFUL."),
          "audit_pending": "repaired this run; audit-verified only after an audit finds it FAITHFUL"})

u = byid["u061"]
if "audit_repair" in u:
    u["audit_repair_20261012T0600Z"] = u.pop("audit_repair")
u.update({"formal_depth": ("1 asserted ground atom over sort `thing`: is_entitled_to_protection_by_society_and_the_state(the_family), kind asserted, meaning {open: [protection_of_the_family]}; "
                           "the subject is the same constant as u060's (the institution, not 'every family'); the entitlement states what the family is entitled to and names no one who "
                           "must act. The candidate stands as a one-unit companion document (norm-defaults@0, completion 'unspecified': the family is SETTLED yes, any other thing UNDECIDED "
                           "in the Lean status rows, never denied and never allowed)."),
          "unchecked_note": ("Not part of any reading: the words do not say who must act, so no candidate names a bearer. The unit is the entitlement alone (who holds the right); no duty or "
                             "permission reading is offered. The subject is the family of u060 by the same constant `the_family`; that the clause continues u060's sentence is not checked "
                             "(no cross-unit reference)."),
          "audit_20261020T1800Z": "UNFAITHFUL (repaired in run 20261021T0600Z)",
          "audit_repair": (f"Rejected by the 20261020T1800Z audit ({AUDIT}): u061 read 'every family' while u060's vocabulary names the subject 'the family' as the institution, so the "
                           "institutional reading was missing. Repaired 2026-10-21: the unit's content and its companion are about `the_family` (sort `thing`); the sort `family` and its "
                           "domains are removed. Claimed, not audit-verified until an audit finds it FAITHFUL."),
          "audit_pending": "repaired this run; audit-verified only after an audit finds it FAITHFUL"})
u.pop("residual_missing_features", None)
u["residual_missing_features"] = ["other:anaphor_subject_from_previous_unit"]

for uid, r in byid.items():
    r["judgment_terms"] = [t for t in r.get("open_terms", []) if CLS.get(t) == "judgment"]
    assert all(t in CLS for t in r.get("open_terms", [])), (uid, [t for t in r["open_terms"] if t not in CLS])
SUPERSEDED = (" [Superseded in run 20261021T0600Z: the 20261020T1800Z audit rejected u042 and u043, which are UNFORMALISED (time) again; u060 and u061 were repaired.]")
for k in ("audit_note_20261018T1800Z", "audit_note_20261019T0600Z"):
    ud[k] += SUPERSEDED
ud["audit_note_20261021T0600Z"] = ("this run repairs the four units the 20261020T1800Z audit rejected (AUDIT-20261020T1800Z.md): u042 and u043 are UNFORMALISED (time) again, u060 states the "
                                   "uniqueness of 'the ... group unit', u061 is the entitlement of the same institution (`the_family`). No feature upgrade: nothing a translator can write was "
                                   "merged between ve-green-sc-1ac and ve-green-sc-1ad. The four repaired units are not audit-verified; u060 and u061 are claimed, u042 and u043 are not covered.")
(HERE / "units.json").write_text(json.dumps(ud, indent=1, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------------------------------------ numbers
order = [x["id"] for x in rows]
counts = Counter(x["status"] for x in rows)
bytes_by = Counter()
for x in rows:
    bytes_by[x["status"]] += span(x)
assert sum(bytes_by.values()) == 10916 and len(rows) == 130
claimed = sum(span(x) for x in rows if x["status"] in COVERED and x.get("claimed", True))
covered = sum(span(x) for x in rows if x["status"] in COVERED)
verified = [i for i in old_m["audit_verified_units"] if i not in REPAIRED]
assert all(byid[i]["status"] in COVERED and byid[i].get("claimed", True) for i in verified)
verified_bytes = sum(span(byid[i]) for i in verified)
assert (claimed, verified_bytes, covered) == (5270 - 318 + 66, 5270 - 318 - 58, 5841 - 318), (claimed, verified_bytes, covered)
pending = ["u060", "u061"]
unclaimed = [x["id"] for x in rows if x["status"] in COVERED and not x.get("claimed", True)]
assert unclaimed == ["u035", "u111"], unclaimed
tally = Counter(x["missing_feature"] for x in rows if x["status"] == "UNFORMALISED")
assert sum(tally.values()) == counts["UNFORMALISED"] == 40
bylu = byid
agg = Counter()
for _old, news in old_m["old_to_new_units"].items():
    s = {bylu[n]["status"] for n in news}
    agg[next(iter(s)) if len(s) == 1 else "MIXED"] += 1
jt_units = [x for x in rows if x["judgment_terms"]]


def split(rows_, key, weight=lambda x: 1):
    out = {}
    for x in rows_:
        out[key(x)] = out.get(key(x), 0) + weight(x)
    return dict(sorted(out.items()))


mf = lambda x: x.get("missing_feature") or "none"
judgment_term_units = {"total": len(jt_units), "by_status": split(jt_units, lambda x: x["status"]), "by_missing_feature": split(jt_units, mf)}
judgment_term_bytes = {"total": sum(span(x) for x in jt_units), "by_status": split(jt_units, lambda x: x["status"], span), "by_missing_feature": split(jt_units, mf, span)}
by_class = {}
for c in ("attitude", "classification", "exception", "judgment", "proportion"):
    us = [x for x in rows if any(CLS.get(t) == c for t in x.get("open_terms", []))]
    by_class[c] = {"units": len(us), "bytes": sum(span(x) for x in us)}
class_counts = dict(sorted(Counter(CLS.values()).items()))
jt = {"open_term_class": CLS, "open_term_class_borderline": BORDER, "class_counts": class_counts, "judgment_term_units": judgment_term_units,
      "judgment_term_bytes": judgment_term_bytes, "units_by_open_term_class": by_class,
      "judgment_terms": {x["id"]: x["judgment_terms"] for x in rows if x["judgment_terms"]},
      "reasons_for_new_terms": reasons, "terms_unchanged_since_20261012T1800Z": terms_unchanged, "differs_from_phase1": differs_from_phase1,
      "phase1_reference": "git show research/judgment-terms-p1:docs/research/evidence/judgment-terms/instrument-udhr-jt0p.json (copied to evidence/judgment-terms-instrument-udhr-jt0p.json)",
      "note": "ledger fields only: they change no status or content and do not make a unit a changed unit (JT-0p item 1). `heavier` (u043) is gone with its unit."}
(HERE / "judgment-terms.json").write_text(json.dumps(jt, indent=1, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------------------------------------ metrics: identity
m["run"] = RUN
m["previous_run"] = f"{PREV_RUN} ({OLD}); its metrics, units and audit are in previous-20261020T1800Z/"
m["previous_baseline"] = OLD
m["baseline"] = TAG
m["features_merged_since_previous_baseline"] = [
    "ve-green-sc-1ac -> ve-green-sc-1ad (5 merges): ap-1c (theorems only; its DELTA.md: 'None'), me-6b (`VE.Calc.Units`, ve-units@2: 'registers no service mode, command or route'), "
    "et-3cb (the last ET-3 theorems; 'None. The modules lean/VE/Events/* are still not reachable from any service mode'), df-1ac (`VE/Defaults/Wire.lean`, the defaults-elaborate and "
    "defaults-coherence kinds: 'What users see does not change ... no service mode ... calls them'), sc-1ad (the graph step and `governFast` of scope's `govern`; 'Nothing a caller sees changes').",
    "evidence that none is writable by a translator for the UDHR: `git diff ve-green-sc-1ac ve-green-sc-1ad -- ve/ rust/` touches only ve/assurance-manifest.json; no lean/VE/Service, "
    "ResponseShape or schema file changes; the pinned ve_service (sha256 ba37ce5d..) is the same binary as for ve-green-sc-1ac.",
    "the 40 UNFORMALISED units were searched against these: scope's `govern` and the event, default-coherence and unit modules reach no document route (cross-sentence scope is still only the "
    "SC-M0 tally; time still has no route, which is why u042 and u043 are back here); act-phrase grammar (8 units) still needs `acts@0` through a route (ap-1b); the others need norms, causation, "
    "attribution, comparison, modality/belief or priority-of-rights constructs that no merge here adds."]
m["feature_upgrades"] = {"bytes": 0, "count": 0, "units": [], "note": "none: no construct, profile or sentence form a translator can write was added between ve-green-sc-1ac and ve-green-sc-1ad"}
m["language_change_for_udhr"] = "none: nothing a translator can write was added; every difference to the previous run is an audit repair (four units) or a measurement."

# ------------------------------------------------------------------------------------------------ metrics: changed units and repairs
m["changed_units"] = list(REPAIRED)
m["units_changed_this_run"] = list(REPAIRED)
m["changed_units_note"] = ("the four units the 20261020T1800Z audit rejected: u042 and u043 (reverted to UNFORMALISED, time), u060 (uniqueness added), u061 (the subject is the institution). "
                           "Ledger-only: u010 (claim note) and the judgment_terms of u043. Every other unit has the same row as in the previous run.")
m["plan_repairs"] = []
m["plan_repairs_note"] = ("none landed this run. The prompt repeats the ET-0 and JT-0p sections (u042, u043; u010, u060), but the 20261020T1800Z audit rejected u042, u043 and u060, and the audit rule "
                          "('a rejected unit keeps no covered status unless repaired') comes first: ET-0's u042 and u043 are reverted (the audit rejects the civil day the plan pre-registered), "
                          "u060 is repaired, u010 stays as audited FAITHFUL. QT-0p, AP-0 and SC-M0 are carried (plan_repairs_in_carried_state).")
m["plan_repairs_in_carried_state"] = ("JT-0p (u010; u060 as repaired this run), QT-0p (u097), AP-0 (u085, u091, u106) and the SC-M0 scope tally are in the carried translation and were not re-applied. "
                                      "ET-0 (u042, u043) was applied in 20261018T1800Z, found FAITHFUL by two audits and REJECTED by the 20261020T1800Z audit; it is reverted this run. "
                                      "JT-5r was not started.")
m["audit_repairs"] = list(REPAIRED)
m["repaired_units"] = list(REPAIRED)
m["units_rejected_by_audit_and_repaired"] = list(REPAIRED)
m["units_repaired_same_defect_not_rejected"] = []
m["audit_repairs_previous_run"] = old_m["audit_repairs"]
m["repaired_unit_reasons"] = {
    "u042": "the civil `day` cannot tell an act committed before a change within the day from one committed after it; no finer time is available, so the unit returns to UNFORMALISED (time)",
    "u043": "same temporal loss, and the every/some pair introduced a question the words do not raise ('the one that was applicable' names one comparison penalty); back to UNFORMALISED (time)",
    "u060": "'the ... group unit' conveys uniqueness and the content did not state it; the content now has the uniqueness as a second conjunct",
    "u061": "the source keeps the subject 'the family', which u060's vocabulary names as the institution; u061 said 'every family'; it is now the entitlement of the same constant `the_family`"}
m["unit_counts_by_status_change"] = {"audit_repairs": {"units": 4, "bytes": sum(span(byid[i]) for i in REPAIRED),
                                                       "by_unit": {"u042": "CHECKED -> UNFORMALISED (-200 B covered)", "u043": "READINGS -> UNFORMALISED (-118 B covered)",
                                                                   "u060": "OPEN -> OPEN (+66 B claimed: no longer claimed:false)", "u061": "OPEN -> OPEN (58 B, form changed)"}},
                                     "feature_upgrades": {"bytes": 0, "units": 0}, "plan_repairs": {"bytes": 0, "units": 0}}
m["open_terms_added"] = []
m["open_terms_dropped"] = ["heavier"]
m["open_terms_replaced"] = {}
m["predicates_dropped"] = ["finding_of_guilt_permitted", "on_account_of", "committed_on", "constitutes_penal_offence_on", "imposition_permitted", "imposes", "imposed_for",
                           "applicability_of", "applicability_to", "applicable_on", "heavier_than"]
m["sorts_dropped"] = ["finding", "act", "day", "imposition", "penalty", "applicability", "family"]
m["document_ids_changed_in"] = [n for n in pc if pc[n]["document_id"] != old_m["document_ids"][n]]
assert m["document_ids_changed_in"] == ["translation-part01.ve.md", "translation-part02.ve.md"], m["document_ids_changed_in"]

# ------------------------------------------------------------------------------------------------ metrics: numbers
m["previous_run_unit_counts_by_status"] = old_m["unit_counts_by_status"]
m["unit_counts_by_status"] = dict(sorted(counts.items()))
m["bytes_by_status"] = dict(sorted(bytes_by.items()))
m["claimed_covered_bytes_previous_run"] = old_m["claimed_covered_bytes"]
m["claimed_covered_bytes_previous_run_under_x5"] = old_m["claimed_covered_bytes"]
m["claimed_covered_bytes"] = claimed
m["claimed_covered_percent"] = round(100 * claimed / 10916, 2)
m["claimed_change_vs_previous_run_bytes"] = claimed - old_m["claimed_covered_bytes"]
m["claimed_change_vs_previous_run_bytes_under_x5"] = claimed - old_m["claimed_covered_bytes"]
m["claimed_covered_bytes_without_x5_marks"] = covered
m["claimed_covered_percent_without_x5_marks"] = round(100 * covered / 10916, 2)
m["covered_bytes_all_statuses_including_claimed_false"] = covered
m["x5_claimed_false"] = {"bytes": 168 + 337, "rule": old_m["x5_claimed_false"]["rule"],
                         "note": "u035 and u111 are claimed:false; u060 is claimed again (its uniqueness is now in the content), pending an audit",
                         "units": {k: v for k, v in old_m["x5_claimed_false"]["units"].items() if k != "u060"}}
m["claimed_false_pending_audit"] = {"bytes": 0, "units": [], "note": "none: u035 (168 B) and u111 (337 B) stay claimed:false (X5); u060 and u061 are claimed and pending audit (audit_pending_units)"}
m["audit_verified_units"] = verified
m["audit_verified_units_form_unchanged"] = list(verified)
m["audit_verified_units_reexpressed_this_run"] = []
m["audit_verified_units_withdrawn_this_run"] = {"u042": "rejected by the 20261020T1800Z audit; reverted", "u043": "rejected by the 20261020T1800Z audit; reverted",
                                                "u061": "rejected by the 20261020T1800Z audit; repaired, pending a new audit"}
m["previous_run_audit_verified_covered_bytes"] = old_m["audit_verified_covered_bytes"]
m["audit_verified_covered_bytes"] = verified_bytes
m["audit_verified_covered_percent"] = round(100 * verified_bytes / 10916, 2)
m["audit_verified_covered_bytes_before_x5"] = verified_bytes
m["audit_verified_note"] = ("verified = judged FAITHFUL by an audit and not changed since, and not marked claimed:false. Claimed bytes are %d (%.2f%%); audit-verified bytes are %d (%.2f%%): the "
                            "difference is u060 (66 B) and u061 (58 B), repaired this run and not audited yet. u042 and u043 (318 B) are no longer covered." %
                            (claimed, 100 * claimed / 10916, verified_bytes, 100 * verified_bytes / 10916))
m["audit_pending_units"] = list(pending)
m["audit_pending_claim_units"] = list(pending)
m["audit_pending_bytes"] = sum(span(byid[i]) for i in pending)
m["audit_newly_verified_units"] = []
m["audit_newly_verified_units_note"] = "none: the 20261020T1800Z audit rejected four units (u042, u043, u060, u061) and found u010 FAITHFUL (already verified)"
m["audit_20261018T1800Z"]["note"] = "its caveats concerned the encodings of u042 and u043, which were rejected by the 20261020T1800Z audit and are reverted (see audit_20261020T1800Z)"
m["audit_20261020T1800Z"] = {"file": AUDIT, "sampled": 20, "ledger_triggered_rechecks": 4, "faithful": 20, "unfaithful": list(REPAIRED),
                             "note": "19 of 20 sampled units and 1 of 4 ledger-triggered rechecks (u010) FAITHFUL; u042, u043, u060 (rechecks) and u061 (sampled) UNFAITHFUL. All four are repaired this run; "
                                     "none is audit-verified until a new audit. Highest-value missing features named by the audit: definite and generic reference, presuppositions and shared subjects across units; "
                                     "precise event times and intervals without an assumed daily granularity; compositional rights/action phrases with checked modifier, purpose and limitation links."}
m["audit_repair_this_run"] = "the 20261020T1800Z audit rejected u042, u043, u060, u061: all four repaired (see repaired_unit_reasons)"
m["missing_feature_tally_previous_run"] = old_m["missing_feature_tally"]
m["missing_feature_tally"] = dict(sorted(tally.items()))
m["limits_unchanged_note"] = ("limits still blocking the 40 UNFORMALISED units: act-phrase grammar (8), rules (7), causation (4), attribution (4), right lines across open sets (4), time (5, "
                              "u042 and u043 back among them), comparison (2), modality/belief (2), and singletons.")
m["previous_run_old_boundary_aggregation"] = old_m["old_boundary_aggregation"]
m["old_boundary_aggregation"] = dict(sorted(agg.items()))
m["unit_scale"] = "sentence or clause; unchanged (130 units; no re-segmentation needed)"
m["open_terms"] = [{"decided_by": t["decided_by"], "factors": t["factors"], "name": t["name"], "necessary": t["necessary"], "sufficient": t["sufficient"]} for t in shared]
m["open_terms_count"] = len(shared)
m["open_term_class"] = CLS
m["open_term_class_counts"] = class_counts
m["open_term_class_reasons_for_new_terms"] = reasons
m["open_term_class_note"] = ("first live run of the instrument: no previous class of this pilot; the terms unchanged since 20261012T1800Z reproduce phase 1's classes (0 differ). `heavier` left with u043 "
                             "this run; no term is new.")
m["judgment_term_units"] = judgment_term_units
m["judgment_term_bytes"] = judgment_term_bytes
m["units_by_open_term_class"] = by_class
m["parts_tool_status_bytes"] = dict(sorted(Counter({k: sum(v["coverage"]["bytes_by_status"].get(k, 0) for v in pc.values())
                                                    for k in ("CHECKED", "LABELLED", "OPEN", "UNFORMALISED")}).items()))
assert sum(m["parts_tool_status_bytes"].values()) == 10916

# readings
sets = {n: json.loads((HERE / f"translation-part0{n}.ve.md").read_bytes().split(b"---\n", 2)[1])["reading_sets"] for n in range(1, 5)}
rs_units = sorted({s["unit"] for v in sets.values() for s in v})
assert "u043" not in rs_units
m["previous_run_reading_set_count"] = old_m["reading_set_count"]
m["previous_run_reading_set_candidates"] = old_m["reading_set_candidates"]
m["reading_set_count"] = old_m["reading_set_count"] - 1
m["reading_set_candidates"] = old_m["reading_set_candidates"] - 2
m["reading_sets_multi_candidate"] = [u for u in old_m["reading_sets_multi_candidate"] if u != "u043"]
assert counts["READINGS"] == old_m["unit_counts_by_status"]["READINGS"] - 1
m["reading_sets_changed_this_run"] = {"u043": "removed: the universal/existential set of ET-0 (the unit is UNFORMALISED again)"}
m["words_only"] = {"rule": old_m["words_only"]["rule"], "readings_added_this_run": {}, "readings_removed_this_run": {"u043": ["universal", "existential"]}, "readings_changed_this_run": {},
                   "open_questions_listed_that_the_text_does_not_raise": 0,
                   "note": "the audit found no support in the words for u043's every/some pair, so both are removed with the unit. u060 and u061 are single-reading units; no outside knowledge is used."}
m["single_reading_units"] = list(old_m["single_reading_units"])
m["single_reading_unit_count"] = len(m["single_reading_units"])
assert "u042" not in m["single_reading_units"] and "u043" not in m["single_reading_units"]
m["no_invented_permissions"] = {
    "new_units": "no unit gains a norm predicate this run (u042 and u043 are UNFORMALISED again); u010, u060 and u061 are assertions with no norm predicate in the parts, and u061's companion declares the completion 'unspecified' (the family is SETTLED yes, any other thing UNDECIDED)",
    "regulated_predicates": old_m["no_invented_permissions"]["regulated_predicates"],
    "scope": old_m["no_invented_permissions"]["scope"],
    "status_rows": "%d Lean status rows over %d companions, all as expected (previous run: 148 over 64; u042.prohibited, u043.universal and u043.existential are gone, u061.entitlement is rebuilt over the institution)" % (sum(len(v) for v in wit.values()), len(comp))}
m["presupposition_check"] = ("No heading or speaker marker presupposes a substantive claim; no heading or label changed this run. u060 ('The family is the natural and fundamental group unit of society') now "
                             "states the uniqueness that 'the ... group unit' conveys as a second conjunct (whether English asserts or presupposes it is not represented; the content states it). "
                             "u061 continues u060's subject by the same constant. u045b, u099b and u100b begin with a conjunction: each carries the subject of the previous unit (noted in its elided field), not a presupposed claim.")
m["jt0p"]["item2_units"]["u060"] = {"bytes": 66, "claimed": True, "status": "OPEN", "repaired": "2026-10-21 (uniqueness conjunct added after the 20261020T1800Z audit); pending audit"}
m["jt0p"]["expected_vs_measured"] = {"other_units_keep_status": True, "premises_readings_conflicts_equal": True, "u010_bytes_claimed": [132, 132], "u060_bytes": [66, 66],
                                     "note": "carried from the 20261018T1800Z run; u060's claim changed after the repair"}
m["scope_tally"]["note"] = "carried unchanged (scope-tally.json): the tally changes no status or content; u042 and u043 keep their other:scope tag and governed_by as UNFORMALISED units"

# ------------------------------------------------------------------------------------------------ metrics: checks and measurements
m["document_ids"] = {n: v["document_id"] for n, v in pc.items()}
m["part_checks"] = {n: {"seconds": v["seconds"], "premises": v["premises"], "readings_status": v["readings_status"], "conflict": v["conflict"],
                        "coverage_bytes_by_status": v["coverage"]["bytes_by_status"], "residual": v["coverage"]["residual"], "document_id": v["document_id"]} for n, v in pc.items()}
parts = json.loads((HERE / "parts.json").read_text())
parts[0]["choices"] = 8
(HERE / "parts.json").write_text(json.dumps(parts, indent=1))
m["parts"] = parts
m["part_regulated_predicates"] = {f"translation-part0{n}.ve.md": len(v) for n, v in regulated.items()}
m["distinct_regulated_predicates_across_parts"] = len(distinct_regulated)
m["status_witness_rows"] = sum(len(v) for v in wit.values())
m["status_witnesses"] = wit
m["companion_documents"] = len(comp)
m["rendering_change"] = {"verdict": "changes only at u042, u043, u060, u061 and the sort list of u025's distinguishing situation",
                         "what": "rendered-parts/ regenerated at ve-green-sc-1ad and diffed with run 20261020T1800Z: part01 loses the 'Checked reading' of u042 and the reading set of u043 (they show 'Recorded meaning: ... time') "
                                 "and the six removed sorts leave the sentence that lists the sorts of u025's distinguishing situation; part02 shows u060's two conjuncts and u061 on \"the_family\"; parts 03 and 04 are identical."}
m["seeded_bugs_translation"] = seeded
m["vocabulary_change_check"] = {
    "rule": old_m["vocabulary_change_check"]["rule"],
    "changes": "ET-0 vocabulary removed from part01 and the whole declaration (sorts finding, act, day, imposition, penalty, applicability; the 11 predicates; the open term heavier); sort `family` removed from part02 and "
               "the whole declaration; the predicate is_entitled_to_protection_by_society_and_the_state takes `thing`; JT-0p's sort `thing` stays",
    "entity_sort": "no sort named `entity` is declared in any part (checked by update_run_20261021T0600Z.py); each part has at most one sort with the noun 'thing' (part01 and part02: `thing`)",
    "companions": "witnesses_all.py: %d companions and %d rows (previous: 64 and 148): the three companions of u042 and u043 are removed, u061's is rebuilt over `thing`; all rows as expected" % (len(comp), m["status_witness_rows"]),
    "rebuild_command": ("the committed `--rebuild-reading-ids <part> --check-noop` is still NOT a no-op on parts 1, 2, 4 and the whole declaration (part03 is), and the document it writes for them does not "
                        "load ('invalid situation'); evidence/rebuild-command.json. The ids were rebuilt by vocab_patch.reidentified_by (VE's own identity functions over the new environment; "
                        "the identity transform reproduces every old id, checked before use)."),
    "situation_step": old_m["vocabulary_change_check"]["situation_step"],
    "result": {"differences": REPAIRED, "environment_changed_in": compare["environment_changed_in"], "unexpected": [], "units": 130,
               "note": "130 of 130 units were compared with the previous run's parts: exactly the four repaired units differ (status and row); every fenced unit of the other 126 parses with the same status and the same row"},
    "rust_time_limit": ("default VE_RUST_TIMEOUT kept. part01's check under `prlimit --as=6442450944`: cap 6442450944 bytes, wall %.1f s, peak child resident set %.1f MB; no raised limit was needed "
                        "(evidence/part01-check-sc1ad.json)" % (p01["wall_seconds"], p01["peak_child_resident_set_mb_max"]))}
m["et0_rerun"] = {"plan": "events-time-causation ET-0 rerun", "status": "REVERTED in run 20261021T0600Z",
                  "reason": "the 20261020T1800Z audit rejected u042 and u043 (the civil `day` loses the order of events within a day; for u043 also the every/some pair). u042 and u043 are UNFORMALISED (time).",
                  "history": "landed in 20261018T1800Z, found FAITHFUL by the 20261018T1800Z and 20261019T0600Z audits, rejected by the 20261020T1800Z audit",
                  "evidence_kept": "evidence/et0-rerun*.json are the measurements of the landed state (ET-6's check-time evidence); they do not describe this run's parts",
                  "part01_without_et0": {"VE_RUST_TIMEOUT": "default (unset)", "address_space_cap_bytes": p01["address_space_cap_bytes"], "wall_seconds": p01["wall_seconds"],
                                         "peak_child_resident_set_mb_max": p01["peak_child_resident_set_mb_max"], "premises": p01["premises"], "conflict": p01["conflict"],
                                         "evidence": "evidence/part01-check-sc1ad.json"}}
m["rebuild_command_check"] = {**rebuild, "requalified_at_sc_1ad": "part01, part02, part04 and the whole declaration `--check-noop` exit 2; part03 is a no-op; the rebuilt documents of the first four fail to load ('invalid situation'); evidence/rebuild-command.json"}
c = m["checks"]
c["build"] = ("ve_service: the pinned binary (sha256 ba37ce5d9a69cf71.., in lean/checkers.lock) copied from the sibling worktree ve-sc-1ad (built there; the same binary as for ve-green-sc-1ac) to lean/.lake/build/bin; "
              "Rust: tools/rust_build.py (binary 6422647f.. pinned in lean/checkers.lock). The Lean library was not rebuilt here.")
c["companions"] = "PASS: %d companions check (premises model) and %d Lean status rows as expected (previous run: 64 and 148)" % (len(comp), m["status_witness_rows"])
c["parts"] = ("PASS: ve document check on all 4 parts at ve-green-sc-1ad: premises 'model', CONFLICT-FREE (part01 %.1f s, part02 %.1f s, part03 %.1f s, part04 %.1f s); only part01's and part02's document ids "
              "changed (their vocabulary changed)" % tuple(pc[f"translation-part0{n}.ve.md"]["seconds"] for n in range(1, 5)))
c["unchanged_units"] = "PASS: 126 of 130 units have the same status and row in the part files as in the previous run; the four repaired units differ (unit-compare.json); source sha256 d6495201.. matches"
c["repaired_units"] = {"u042": "UNFORMALISED (time)", "u043": "UNFORMALISED (time)", "u060": "OPEN, uniqueness conjunct added", "u061": "OPEN, ground atom over the_family"}
c["seeded_bugs_translation"] = seeded
c.pop("wrong_separating_situation", None)
c["limits_met"] = [
    "Rust checker: default VE_RUST_TIMEOUT kept. Part01 checks under prlimit --as=6442450944 in %.1f s with a peak child resident set of %.1f MB; no raised limit was needed" % (p01["wall_seconds"], p01["peak_child_resident_set_mb_max"]),
    c["limits_met"][1], c["limits_met"][2]]
if whole_done:
    wl, wc = whole["load"], whole["check"]
    c["whole_document"] = {"load": {"coverage_percent": wl["coverage_percent"], "seconds": wl["seconds"]},
                           "check": {"premises": wc["premises"], "readings_status": wc["readings_status"], "seconds": wc["seconds"]},
                           "note": "the whole declaration as one document with the repairs applied by repair_20261021.py; load, then check, in the foreground"}
    c["limits_met"][1] = ("the whole declaration as ONE document (experiment-whole/): six two-reading sets as RD-4b components and the rest in the main component; at ve-green-sc-1ad load_document "
                          "succeeds after %.1f s (coverage %s%%) and check_document answers %s, premises '%s' after %.1f s (previous run 2033.0 s and 2654.8 s)" %
                          (wl["seconds"], wl["coverage_percent"], wc["readings_status"], wc["premises"], wc["seconds"]))
    m["whole_document_experiment"]["components"] = {"load": {"coverage_percent": wl["coverage_percent"], "seconds": wl["seconds"]},
                                                    "check": {"premises": wc["premises"], "readings_status": wc["readings_status"], "seconds": wc["seconds"]}}
    m["whole_document_experiment"]["result"] = "loads and checks at ve-green-sc-1ad"
    m["whole_document_experiment"]["note"] = ("whole.py was NOT re-run: experiment-whole/translation-whole.ve.md is the previous run's with repair_20261021.py applied (the same edits as to the parts), "
                                              "then loaded and checked (whole_check.py load, then check)")
else:
    m["whole_document_experiment"]["result"] = "NOT YET RE-RUN in this run"
m["language_findings"] = [
    "no construct a translator can write was added between ve-green-sc-1ac and ve-green-sc-1ad (ap-1c, me-6b, et-3cb, df-1ac, sc-1ad: Lean modules and theorems that no document route reaches).",
    "the audit's temporal objection to ET-0 stands: a `day` sort loses the order of events within a day, and the event modules (et-3cb) still reach no route, so 'at the time when it was committed' (u042, u043) is blocked by time again. For ET-6: restating the two wordings with a sort of times whose grain the text does not fix is a candidate, not done here.",
    "'the' as uniqueness is expressible as a conjunct over an open predicate (u060: `for every thing that is classified as ..., that thing is the same as \"the_family\"`), checked by the loader; whether English asserts or presupposes it is still not represented.",
    "sharing a subject across units works only by naming the same constant in both (u060, u061); there is still no checked cross-unit reference.",
    "the committed `--rebuild-reading-ids` is still not a no-op on parts 1, 2, 4 or the whole declaration (`--check-noop` exits 2) and its output does not load; the ids were rebuilt with vocab_patch.reidentified_by.",
    "scope's effects and `govern` are in Lean (sc-1ab to sc-1ad) but reach no document route, so the SC-M0 tally cannot yet be turned into checked structure.",
    "the 8 act-phrase units (1,403 B) are still blocked: the next feature that moves the UDHR number is ap-1b."]
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits)",
                          "no seeded bug in product code (this run changed no file under ve/, lean/ or rust/); seeded faults in the translation are in seeded-bugs-translation.json",
                          "JT-5r (the 31 term splits) was not started, as directed",
                          "the ET-0 section was not re-applied: the 20261020T1800Z audit rejected its units, which are reverted (plan_repairs_note)",
                          "no `lake build`: the pinned ve_service was copied from the sibling worktree ve-sc-1ad; the Rust binary was built by tools/rust_build.py"]
m["source"] = old_m["source"]
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n")
print("claimed", claimed, "verified", verified_bytes, "counts", dict(counts), "tally", dict(tally))
