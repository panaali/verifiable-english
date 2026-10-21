"""Ledger of run 20261021T1800Z: units.json, metrics.json, judgment-terms.json from the previous run's copies (previous-20261021T0600Z/) and this run's saved checks.

    uv run --frozen python usecases/udhr-pilot/run-20261021T1800Z/update_run_20261021T1800Z.py

Idempotent: it always starts from previous-20261021T0600Z/.  Nothing here calls a model.  This run repairs the one unit the 20261021T0600Z audit rejected AND that a
translator can repair at ve-green-ap-1b (u048: a reading set of two scope readings), keeps u042 and u043 UNFORMALISED (time; the audit's objection to the pre-registered
ET-0 content stands), sets u060 to `claimed: false` as JT-0p item 2 directs, records u061 as audit-verified, and upgrades no unit (ap-1b is not reachable from a document).
"""
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE / "previous-20261021T0600Z"
RUN, PREV_RUN, TAG, OLD = "run-20261021T1800Z", "run-20261021T0600Z", "ve-green-ap-1b", "ve-green-sc-1ad"
REPAIRED = ["u048"]
LEDGER_ONLY = ["u060", "u061"]
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")
AUDIT = "AUDIT-20261021T0600Z.md"

old_m = json.loads((PREV / "metrics.json").read_text())
m = deepcopy(old_m)
ud = json.loads((PREV / "units.json").read_text())
pc = json.loads((HERE / "parts-check.json").read_text())
compare = json.loads((HERE / "unit-compare.json").read_text())
comp = json.loads((HERE / "companions-check.json").read_text())
wit = json.loads((HERE / "witnesses.json").read_text())["norm_defaults_status"]
seeded = json.loads((HERE / "seeded-bugs-translation.json").read_text())
rebuild = json.loads((HERE / "evidence" / "rebuild-command.json").read_text())
p01 = json.loads((HERE / "evidence" / "part01-check-ap1b-baseline.json").read_text())
p01et = json.loads((HERE / "evidence" / "part01-check-ap1b-et0.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
phase1 = json.loads((HERE / "evidence" / "judgment-terms-instrument-udhr-jt0p.json").read_text())

for n, v in pc.items():
    assert "error" not in v and v["premises"]["status"] == "model" and v["conflict"] in (None, "CONFLICT-FREE"), (n, v)
assert [d["unit"] for d in compare["differences"]] == REPAIRED and not compare["unexpected"] and compare["units"] == 130
assert p01["premises"] == "model" and p01["conflict"] == "CONFLICT-FREE" and p01et["premises"] == "model" and p01et["conflict"] == "CONFLICT-FREE"
assert len(comp) == 62 and sum(len(v) for v in wit.values()) == 137, (len(comp), sum(len(v) for v in wit.values()))
assert all(o["as_expected"] for v in wit.values() for o in v) and "u048.entitlement" not in wit
assert "error" not in whole["load"] and "error" not in whole["check"] and whole["check"]["premises"] == "model" and whole["check"]["readings_status"] == "CONFLICT-FREE"

fronts = {n: json.loads((HERE / f"translation-part0{n}.ve.md").read_bytes().split(b"---\n", 2)[1]) for n in range(1, 5)}
shared = fronts[1]["open_terms"]
assert shared == fronts[2]["open_terms"] == fronts[3]["open_terms"] == fronts[4]["open_terms"], "the shared record list differs between parts"
open_names = [t["name"] for t in shared]
for n, f in fronts.items():
    voc = f["environment"]["vocabulary"]
    assert "entity" not in voc["sorts"] and sum(1 for s in voc["sorts"].values() if s["verbalisation"]["singular"] == "thing") <= 1, n
    assert "has_the_right_to_movement_and_residence" not in voc["predicates"], n
assert "right_to_movement_and_residence_within_borders" in fronts[2]["environment"]["vocabulary"]["predicates"]
regulated = {n: sorted(p for p, d in f["environment"]["vocabulary"]["predicates"].items() if "regulated" in d) for n, f in fronts.items()}
distinct_regulated = sorted({p for v in regulated.values() for p in v})
CLS = dict(old_m["open_term_class"])
assert set(CLS) == set(open_names)            # no open term is new this run (u048 names none)
BORDER = old_m["open_term_class_borderline"]
terms_unchanged = [n for n in open_names if n in phase1["open_term_class"]]
assert not [n for n in terms_unchanged if CLS[n] != phase1["open_term_class"][n]]

rows = ud["units"]
byid = {u["id"]: u for u in rows}
span = lambda u: u["span"][1] - u["span"][0]

# ------------------------------------------------------------------------------------------------ the 20261021T0600Z audit's verdicts
SAMPLED = ["u010", "u011", "u012", "u022b", "u026", "u030", "u035", "u042", "u043", "u045a", "u048", "u052", "u055", "u056", "u060", "u061", "u062", "u083", "u085", "u090",
           "u098", "u100a", "u104", "u105b", "u110"]
for uid in SAMPLED:
    byid[uid]["audit_20261021T0600Z"] = "UNFAITHFUL" if uid in ("u042", "u043", "u048") else "FAITHFUL"

# ------------------------------------------------------------------------------------------------ u048: the repair
u = byid["u048"]
for k in ("single_reading", "words_only_single_reading", "audit_pending"):
    u.pop(k, None)
u.update({
    "status": "READINGS", "status_in_previous_run": "CHECKED", "candidates": ["borders_over_both", "borders_residence_only"], "reading_set": "rs_u048",
    "open_terms": [], "single_reading": False, "words_only_single_reading": False, "claimed": True,
    "companions": ["readings/u048.borders_over_both.ve.md", "readings/u048.borders_residence_only.ve.md"],
    "norm_defaults_companions": ["readings/u048.borders_over_both.ve.md", "readings/u048.borders_residence_only.ve.md"],
    "formal_depth": ("2 candidates (borders_over_both, borders_residence_only), each a plain predicate asserted of every person in the part document translation-part02.ve.md "
                     "(a unit whose content is its reading set), in one reading set whose separating model Lean admitted; each candidate also stands as a one-unit companion document with a "
                     "Lean status witness (the person is SETTLED yes). Each is ONE right (who holds it, nothing more); no duty or permission reading; no candidate names a bearer."),
    "unchecked_note": ("Not part of any reading: the words do not say who must act, so no candidate names a bearer. A reader who knows how the Declaration is used in later treaties "
                       "may expect States to be the bearers."),
    "audit_20261021T0600Z": "UNFAITHFUL (repaired in run 20261021T1800Z)",
    "audit_repair": (f"Rejected by the 20261021T0600Z audit ({AUDIT}): 'within the borders of each state' can qualify movement and residence together, or residence alone, and one opaque "
                     "predicate repeated the ambiguity. Repaired 2026-10-21T1800Z: u048 is a reading set of the two scopes, each a plain predicate (the old predicate "
                     "has_the_right_to_movement_and_residence and its companion are removed everywhere), with a model that separates them. Claimed, not audit-verified until an audit finds it FAITHFUL."),
    "audit_pending": "repaired this run; audit-verified only after an audit finds it FAITHFUL",
    "reading_note": ("The two readings come from the words only: the phrase 'within the borders of each state' follows 'freedom of movement and residence' and can attach to both nouns or to "
                     "'residence' alone. In the second reading the words attach no borders to movement; nothing about where one may move is said or added."),
    "status_in_run_20261021T0600Z": "CHECKED"})
u.pop("audit_repair_20261005T1800Z", None)
rs_old = [k for k in u if k.startswith("residual_missing") and k != "residual_missing_features"]
assert not rs_old

# ------------------------------------------------------------------------------------------------ u042, u043: stay UNFORMALISED (the audit's objection stands)
for uid in ("u042", "u043"):
    u = byid[uid]
    assert u["status"] == "UNFORMALISED" and u["missing_feature"] == "time" and u["claimed"] is False
    u["et0_rerun_20261021T1800Z"] = ("The pre-registered ET-0 content was measured on a copy at ve-green-ap-1b (evidence/et0-rerun.json, evidence/et0-variant/): part01 loads and checks, premises model, "
                                     "CONFLICT-FREE, u042 +200 B CHECKED, u043 +118 B OPEN. It is NOT landed: the 20261020T1800Z audit rejected its civil `day` (and u043's every/some pair) and "
                                     "the 20261021T0600Z audit still names the missing time. The unit stays UNFORMALISED (time) with claimed:false.")

# ------------------------------------------------------------------------------------------------ u060: claimed:false (JT-0p item 2, X5); u061: audited
u = byid["u060"]
u.update({"claimed": False, "missing_feature": "presupposition",
          "blocker_detail": ("JT-0p item 2 directs `missing_feature: presupposition` and `claimed: false` for u060: it is written and audited (the 20261021T0600Z audit: FAITHFUL, with the "
                             "uniqueness conjunct), but its bytes are not claimed. The content states the uniqueness of 'the ... group unit' as a second conjunct; whether English asserts or "
                             "only presupposes it is not represented (presupposition is the missing feature)."),
          "claim_note_20261021T1800Z": "claimed:false again, as JT-0p item 2 and DRI X5 direct; the 20261021T0600Z audit also gave u060 no verified bytes for this reason",
          "audit_pending": None})
u.pop("audit_pending")
u = byid["u061"]
u.pop("audit_pending", None)
u["audit_verified_note_20261021T1800Z"] = "judged FAITHFUL by the 20261021T0600Z audit (sampled): same subject constant as u060; verified bytes from this run"

for uid, r in byid.items():
    r["judgment_terms"] = [t for t in r.get("open_terms", []) if CLS.get(t) == "judgment"]
    assert all(t in CLS for t in r.get("open_terms", [])), (uid, [t for t in r["open_terms"] if t not in CLS])
ud["audit_note_20261021T1800Z"] = ("this run repairs u048 (the one unit of the 20261021T0600Z audit that a translator can repair: a reading set of its two scope readings). u042 and u043, the "
                                   "audit's other two rejections, stay UNFORMALISED (time): the only encoding available, ET-0's, is the one the 20261020T1800Z audit rejected; it was measured on a "
                                   "copy and is not landed. u061 was found FAITHFUL; u060 was found FAITHFUL and is claimed:false as JT-0p item 2 directs. No feature upgrade: `acts@0` (ap-1b) cannot be "
                                   "written in a document (evidence/ap1b-document-probe.json). u048 is claimed and not audit-verified.")
(HERE / "units.json").write_text(json.dumps(ud, indent=1, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------------------------------------ numbers
counts = Counter(x["status"] for x in rows)
bytes_by = Counter()
for x in rows:
    bytes_by[x["status"]] += span(x)
assert sum(bytes_by.values()) == 10916 and len(rows) == 130
claimed = sum(span(x) for x in rows if x["status"] in COVERED and x.get("claimed", True))
covered = sum(span(x) for x in rows if x["status"] in COVERED)
verified = [i for i in old_m["audit_verified_units"] if i not in REPAIRED] + ["u061"]
verified = sorted(set(verified))
assert all(byid[i]["status"] in COVERED and byid[i].get("claimed", True) for i in verified)
verified_bytes = sum(span(byid[i]) for i in verified)
assert (claimed, verified_bytes, covered) == (5018 - 66, 4894 - 98 + 58, 5523), (claimed, verified_bytes, covered)
pending = ["u048"]
unclaimed = [x["id"] for x in rows if x["status"] in COVERED and not x.get("claimed", True)]
assert unclaimed == ["u035", "u060", "u111"], unclaimed
tally = Counter(x["missing_feature"] for x in rows if x["status"] == "UNFORMALISED")
assert tally == Counter(old_m["missing_feature_tally"]) and counts["UNFORMALISED"] == 40
agg = Counter()
for _old, news in old_m["old_to_new_units"].items():
    s = {byid[n]["status"] for n in news}
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
jt = json.loads((PREV / "judgment-terms.json").read_text())
jt.update({"open_term_class": CLS, "class_counts": class_counts, "judgment_term_units": judgment_term_units, "judgment_term_bytes": judgment_term_bytes,
           "units_by_open_term_class": by_class, "judgment_terms": {x["id"]: x["judgment_terms"] for x in rows if x["judgment_terms"]},
           "terms_unchanged_since_20261012T1800Z": terms_unchanged, "differs_from_phase1": [],
           "note": "ledger fields only: they change no status or content and do not make a unit a changed unit (JT-0p item 1). No term is new, dropped or reclassified this run; u048 names no open term."})
(HERE / "judgment-terms.json").write_text(json.dumps(jt, indent=1, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------------------------------------ metrics: identity
m["run"] = RUN
m["previous_run"] = f"{PREV_RUN} ({OLD}); its metrics, units and audit are in previous-20261021T0600Z/ (AUDIT.md of that run is {AUDIT} here)"
m["previous_baseline"] = OLD
m["baseline"] = TAG
m["features_merged_since_previous_baseline"] = [
    "ve-green-sc-1ad -> ve-green-ap-1b (5 merges on main: ap-1d, sc-3ab, me-9b, me-5b, ap-1b; infra/speed-tmrescore): ap-1b admits the profile `acts@0` (long single acts up to 400 bytes, declared fixed phrases that may hold 'and', 'or', "
    "'for'; plain entitlement wording 'has the right ...') in Lean's environment, norms, plain and norm-defaults routes (docs/act-phrases/ap-1b/DELTA.md). ap-1d is theorems only; sc-3ab, me-9b and me-5b are Lean modules no document route reaches.",
    "evidence that ap-1b is not writable by a translator through `ve document` for the UDHR: a document that lists `acts@0` is refused at load with `UnsupportedProfile: Unsupported profile acts@0` by the typing "
    "check (ve/ast.py check_formula, the 'lean-base' encoding), with or without norm-defaults@0 (evidence/ap1b-document-probe.json); ap-1b's REPORT section 6 leaves the readings route, model questions and Python's printing "
    "to ap-1bb, and joined acts outside fixed phrases need AP-2 and AP-3, which are not merged.",
    "the 40 UNFORMALISED units were searched against these: the eight act-phrase units (u039, u041, u076, u079b, u082, u086, u092, u108; 1,403 B) wait for acts@0 through `ve document` (ap-1bb); "
    "the others need norms, time, causation, attribution, comparison, modality/belief or priority-of-rights constructs that no merge here adds."]
m["feature_upgrades"] = {"bytes": 0, "count": 0, "units": [], "note": "none: ap-1b's profile cannot be used in a document at ve-green-ap-1b (evidence/ap1b-document-probe.json)"}
m["language_change_for_udhr"] = "none: nothing a translator can write was added; the one changed unit (u048) is an audit repair, the rest are ledger or measurement changes."

# ------------------------------------------------------------------------------------------------ metrics: changed units and repairs
m["changed_units"] = list(REPAIRED)
m["units_changed_this_run"] = list(REPAIRED)
m["changed_units_note"] = ("u048 is the one changed unit (audit repair). Ledger-only, with no change of content or status: u060 (claimed:false, missing_feature presupposition, as JT-0p item 2 directs), "
                           "u061 (audit-verified), the audit verdicts of the 25 sampled units, and `judgment_terms`. Every other unit has the same row as in the previous run (unit-compare.json).")
m["plan_repairs"] = []
m["plan_repairs_note"] = ("none landed this run. The prompt repeats QT-0p (u097), SC-M0, AP-0 (u085, u091, u106), JT-0p (u010, u060) and ET-0 (u042, u043). QT-0p, SC-M0, AP-0 and JT-0p were applied in earlier runs "
                          "and are carried (their 'first check that ... UNFORMALISED' condition no longer holds because they are landed; u097, u085, u091, u106, u010 and u060 keep their statuses). "
                          "ET-0's u042 and u043 are NOT landed: the 20261020T1800Z audit rejected the civil `day` and the every/some pair, the 20261021T0600Z audit repeats that the time is missing, and a rejected "
                          "unit may not keep a covered status unless repaired; ET-0's content is not a repair of that objection. It was measured on a copy (evidence/et0-rerun.json). JT-5r was not started.")
m["plan_repairs_in_carried_state"] = ("JT-0p (u010; u060 with its uniqueness conjunct, now claimed:false), QT-0p (u097), AP-0 (u085, u091, u106) and the SC-M0 scope tally are in the carried translation and were not re-applied.")
m["audit_repairs"] = list(REPAIRED)
m["repaired_units"] = list(REPAIRED)
m["units_rejected_by_audit_and_repaired"] = list(REPAIRED)
m["units_rejected_by_audit_not_repaired"] = {"u042": "time (no finer time than ET-0's rejected `day` is available; the event modules reach no document route)",
                                             "u043": "time (same; and the every/some pair is not licensed by the words)"}
m["units_repaired_same_defect_not_rejected"] = []
m["audit_repairs_previous_run"] = old_m["audit_repairs"]
m["repaired_unit_reasons"] = {"u048": "'within the borders of each state' can qualify movement and residence together or residence alone; one opaque predicate repeated the ambiguity; it is now a reading set of the two scopes (words only), "
                                      "each ONE entitlement, with a model that separates them"}
m["unit_counts_by_status_change"] = {"audit_repairs": {"units": 1, "bytes": span(byid["u048"]), "by_unit": {"u048": "CHECKED -> READINGS (98 B stay covered and claimed; audit-verified bytes -98 until re-audited)"}},
                                     "feature_upgrades": {"bytes": 0, "units": 0}, "plan_repairs": {"bytes": 0, "units": 0},
                                     "ledger_only": {"u060": "claimed -66 B (claimed:false)", "u061": "audit-verified +58 B"}}
m["open_terms_added"] = []
m["open_terms_dropped"] = []
m["open_terms_replaced"] = {}
m["predicates_dropped"] = ["has_the_right_to_movement_and_residence"]
m["predicates_added"] = ["right_to_movement_and_residence_within_borders", "right_to_movement_and_residence_borders_on_residence"]
m["sorts_dropped"] = []
m["document_ids_changed_in"] = [n for n in pc if pc[n]["document_id"] != old_m["document_ids"][n]]
assert m["document_ids_changed_in"] == ["translation-part02.ve.md"], m["document_ids_changed_in"]

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
m["x5_claimed_false"] = {"bytes": 168 + 337 + 66, "rule": old_m["x5_claimed_false"]["rule"],
                         "note": "u035, u111 and u060 are claimed:false (u060 again, as JT-0p item 2 directs)",
                         "units": {**old_m["x5_claimed_false"]["units"],
                                   "u060": {"bytes": 66, "reason": "JT-0p item 2: written and audited, bytes not claimed; the uniqueness of 'the ... group unit' is stated as a conjunct, but asserting versus presupposing it is not represented (missing feature presupposition)"}}}
m["claimed_false_pending_audit"] = {"bytes": 0, "units": [], "note": "none: u035 (168 B), u060 (66 B) and u111 (337 B) are claimed:false (X5); u048 is claimed and pending audit (audit_pending_units)"}
m["audit_verified_units"] = verified
m["audit_verified_units_form_unchanged"] = [i for i in verified if i != "u061"]
m["audit_verified_units_reexpressed_this_run"] = []
m["audit_verified_units_withdrawn_this_run"] = {"u048": "rejected by the 20261021T0600Z audit; repaired this run, pending a new audit"}
m["previous_run_audit_verified_covered_bytes"] = old_m["audit_verified_covered_bytes"]
m["audit_verified_covered_bytes"] = verified_bytes
m["audit_verified_covered_percent"] = round(100 * verified_bytes / 10916, 2)
m["audit_verified_covered_bytes_before_x5"] = verified_bytes
m["audit_verified_note"] = ("verified = judged FAITHFUL by an audit and not changed since, and not marked claimed:false. Claimed bytes are %d (%.2f%%); audit-verified bytes are %d (%.2f%%): the "
                            "difference is u048 (98 B, repaired this run and not audited yet). u060 (66 B) was found FAITHFUL but is claimed:false, so it counts in neither. u042 and u043 (318 B) are not covered." %
                            (claimed, 100 * claimed / 10916, verified_bytes, 100 * verified_bytes / 10916))
m["audit_pending_units"] = list(pending)
m["audit_pending_claim_units"] = list(pending)
m["audit_pending_bytes"] = sum(span(byid[i]) for i in pending)
m["audit_newly_verified_units"] = ["u061"]
m["audit_newly_verified_units_note"] = "u061 (58 B): found FAITHFUL by the 20261021T0600Z audit after its repair; u060 was also FAITHFUL but is claimed:false"
m["audit_20261020T1800Z"]["note"] = (m["audit_20261020T1800Z"]["note"] + " [Updated: the 20261021T0600Z audit found u060 and u061 FAITHFUL after their repair; u042 and u043 are still untranslated.]")
m["audit_20261021T0600Z"] = {"file": AUDIT, "sampled": 20, "ledger_triggered_rechecks": 4, "faithful": "19 of 20 sampled + 2 of 4 changed (u060, u061; u010 recheck FAITHFUL)",
                             "unfaithful": ["u042", "u043", "u048"],
                             "note": ("u048: 'within the borders of each state' qualifies movement and residence together or residence alone (repaired this run). u042, u043: correctly labelled UNFORMALISED, "
                                      "but untranslated: reification of findings and acts is acceptable, 'substituting civil days for the relevant time loses distinctions', and for u043 'the words identify the "
                                      "contextually applicable penalty; they do not independently license the former every/some alternatives'. Not repaired this run (nothing available expresses the time). "
                                      "No sampled CHECKED unit uses an open-term predicate or an undeclared evaluative catalogue term; u035 receives no verified bytes under X5. Three highest-value missing "
                                      "features named by the audit: compositional rights/action phrases with explicit modifier scope and participant binding; checked references across units "
                                      "(shared subjects, the rights targeted by limitations); precise event times and historical applicability/penalty comparisons.")}
m["audit_repair_this_run"] = "the 20261021T0600Z audit rejected u042, u043, u048: u048 repaired; u042 and u043 stay UNFORMALISED (time), see units_rejected_by_audit_not_repaired"
m["missing_feature_tally_previous_run"] = old_m["missing_feature_tally"]
m["missing_feature_tally"] = dict(sorted(tally.items()))
m["limits_unchanged_note"] = ("limits still blocking the 40 UNFORMALISED units: act-phrase grammar (8; ap-1b's profile exists in Lean but is refused at document load), rules (7), causation (4), attribution (4), "
                              "right lines across open sets (4), time (5, u042 and u043 among them), comparison (2), modality/belief (2), and singletons.")
m["previous_run_old_boundary_aggregation"] = old_m["old_boundary_aggregation"]
m["old_boundary_aggregation"] = dict(sorted(agg.items()))
m["unit_scale"] = "sentence or clause; unchanged (130 units; no re-segmentation needed)"
m["open_terms"] = [{"decided_by": t["decided_by"], "factors": t["factors"], "name": t["name"], "necessary": t["necessary"], "sufficient": t["sufficient"]} for t in shared]
m["open_terms_count"] = len(shared)
m["open_term_class"] = CLS
m["open_term_class_counts"] = class_counts
m["open_term_class_note"] = ("terms unchanged since 20261012T1800Z reproduce phase 1's classes (0 differ); no term is new, dropped or reclassified this run (u048 names none).")
m["judgment_term_units"] = judgment_term_units
m["judgment_term_bytes"] = judgment_term_bytes
m["units_by_open_term_class"] = by_class
m["parts_tool_status_bytes"] = dict(sorted(Counter({k: sum(v["coverage"]["bytes_by_status"].get(k, 0) for v in pc.values())
                                                    for k in ("CHECKED", "LABELLED", "OPEN", "UNFORMALISED")}).items()))
assert sum(m["parts_tool_status_bytes"].values()) == 10916

sets = {n: json.loads((HERE / f"translation-part0{n}.ve.md").read_bytes().split(b"---\n", 2)[1])["reading_sets"] for n in range(1, 5)}
rs_units = sorted({s["unit"] for v in sets.values() for s in v})
assert "u048" in rs_units and len(rs_units) == old_m["reading_set_count"] + 1 == counts["READINGS"]
m["previous_run_reading_set_count"] = old_m["reading_set_count"]
m["previous_run_reading_set_candidates"] = old_m["reading_set_candidates"]
m["reading_set_count"] = old_m["reading_set_count"] + 1
m["reading_set_candidates"] = old_m["reading_set_candidates"] + 2
assert m["reading_set_candidates"] == sum(len(s["readings"]) for v in sets.values() for s in v)
m["reading_sets_multi_candidate"] = sorted([*old_m["reading_sets_multi_candidate"], "u048"])
m["reading_sets_changed_this_run"] = {"u048": "added: borders_over_both and borders_residence_only (the scope of 'within the borders of each state'), models-separated; every other set only has its ids recomputed over part02's new environment"}
m["words_only"] = {"rule": old_m["words_only"]["rule"], "readings_added_this_run": {"u048": ["borders_over_both", "borders_residence_only"]}, "readings_removed_this_run": {}, "readings_changed_this_run": {},
                   "open_questions_listed_that_the_text_does_not_raise": 0,
                   "note": "both u048 readings come from where the phrase 'within the borders of each state' can attach; no outside knowledge is used; no duty or permission reading, no bearer; no open term is added."}
m["single_reading_units"] = [i for i in old_m["single_reading_units"] if i != "u048"]
m["single_reading_unit_count"] = len(m["single_reading_units"])
m["no_invented_permissions"] = {
    "new_units": "no unit gains a norm predicate this run; u048's two readings are plain entitlements (who holds the right), each companion declares the completion 'unspecified' (the person is SETTLED yes)",
    "regulated_predicates": old_m["no_invented_permissions"]["regulated_predicates"],
    "scope": old_m["no_invented_permissions"]["scope"],
    "status_rows": "%d Lean status rows over %d companions, all as expected (previous run: 136 over 61; u048.entitlement is replaced by u048.borders_over_both and u048.borders_residence_only)" % (sum(len(v) for v in wit.values()), len(comp))}
m["presupposition_check"] = ("No heading or speaker marker presupposes a substantive claim; no heading or label changed this run. u060 states the uniqueness that 'the ... group unit' conveys as a second conjunct "
                             "(whether English asserts or presupposes it is not represented), and is claimed:false as JT-0p item 2 directs. u061 continues u060's subject by the same constant.")
m["jt0p"]["item2_units"]["u060"] = {"bytes": 66, "claimed": False, "status": "OPEN", "missing_feature": "presupposition", "audit": "FAITHFUL (20261021T0600Z)",
                                    "note": "claimed:false as JT-0p item 2 and DRI X5 direct; the uniqueness conjunct added 2026-10-21 stays"}
m["jt0p"]["expected_vs_measured"] = {"other_units_keep_status": True, "premises_readings_conflicts_equal": True, "u010_bytes_claimed": [132, 132], "u060_bytes": [66, 66],
                                     "note": "carried from the 20261018T1800Z run; JT-0p's two units are carried as landed (their `first check ... UNFORMALISED` precondition no longer holds); u060 claimed:false again"}
m["scope_tally"]["note"] = "carried unchanged (scope-tally.json): the tally changes no status or content; u048's other:scope tag and governed_by are unchanged"

# ------------------------------------------------------------------------------------------------ metrics: checks and measurements
m["document_ids"] = {n: v["document_id"] for n, v in pc.items()}
m["part_checks"] = {n: {"seconds": v["seconds"], "premises": v["premises"], "readings_status": v["readings_status"], "conflict": v["conflict"],
                        "coverage_bytes_by_status": v["coverage"]["bytes_by_status"], "residual": v["coverage"]["residual"], "document_id": v["document_id"]} for n, v in pc.items()}
m["parts"] = json.loads((HERE / "parts.json").read_text())
m["part_regulated_predicates"] = {f"translation-part0{n}.ve.md": len(v) for n, v in regulated.items()}
m["distinct_regulated_predicates_across_parts"] = len(distinct_regulated)
m["status_witness_rows"] = sum(len(v) for v in wit.values())
m["status_witnesses"] = wit
m["companion_documents"] = len(comp)
m["rendering_change"] = {"verdict": "changes only at u048", "what": "rendered-parts/ regenerated at ve-green-ap-1b and diffed with run 20261021T0600Z's: only part02 differs, at u048 (the 'Checked reading' becomes 'This sentence could mean: One reading is ... Another reading is ...'); parts 01, 03 and 04 are identical."}
m["seeded_bugs_translation"] = seeded
m["vocabulary_change_check"] = {
    "rule": old_m["vocabulary_change_check"]["rule"],
    "changes": "part02 and the whole declaration: the predicate has_the_right_to_movement_and_residence is replaced by right_to_movement_and_residence_within_borders and right_to_movement_and_residence_borders_on_residence (u048's two readings); no sort, constant or open term changed",
    "entity_sort": "no sort named `entity` is declared in any part (checked by update_run_20261021T1800Z.py); each part has at most one sort with the noun 'thing' (part01 and part02: `thing`)",
    "companions": "witnesses_all.py at ve-green-ap-1b: %d companions and %d rows (previous: 61 and 136); all rows as expected; the rows of every other companion are identical to the previous run's" % (len(comp), m["status_witness_rows"]),
    "rebuild_command": ("the committed `--rebuild-reading-ids <part> --check-noop` was run on the unchanged previous parts first: part03 is a no-op; parts 1, 2, 4 and the whole declaration still exit 2 and their output does not "
                        "load ('invalid situation'); evidence/rebuild-command.json. The ids were rebuilt by vocab_patch.reidentified_by (VE's own identity functions over the new environment; the identity transform reproduces every old id)."),
    "situation_step": ("`nd.py all` is the constitution's tool and does not exist for the UDHR; its UDHR counterpart is the reading sets' situations and models (rebuilt with the new environment's ids) and the load of every "
                       "part: all four parts load and check, and compare_units.py compares every unit with the previous run's"),
    "result": {"differences": REPAIRED, "environment_changed_in": compare["environment_changed_in"], "unexpected": [], "units": 130,
               "note": "130 of 130 units compared with the previous run's parts: exactly u048 differs (status and row); every fenced unit of the other 129 parses with the same status and the same row"},
    "rust_time_limit": ("default VE_RUST_TIMEOUT kept. part01's check under `prlimit --as=6442450944`: cap 6442450944 bytes, wall %.1f s, peak child resident set %.1f MB; no raised limit was needed "
                        "(evidence/part01-check-ap1b-baseline.json)" % (p01["wall_seconds"], p01["peak_child_resident_set_mb_max"]))}
m["et0_rerun"] = {"plan": "events-time-causation ET-0 rerun", "status": "MEASURED on a copy, NOT LANDED (run 20261021T1800Z)",
                  "reason": "the 20261020T1800Z audit rejected u042 and u043 (the civil `day`; for u043 also the every/some pair) and the 20261021T0600Z audit still lists them as untranslated for the time they lose; ET-0's content is not a repair of that objection, so u042 and u043 stay UNFORMALISED (time) and claimed:false.",
                  "bar_met": True, "evidence": "evidence/et0-rerun.json, evidence/part01-check-ap1b-et0.json, evidence/et0-variant/translation-part01.ve.md",
                  "part01_with_et0": {"VE_RUST_TIMEOUT": "default (unset)", "address_space_cap_bytes": p01et["address_space_cap_bytes"], "wall_seconds": p01et["wall_seconds"],
                                      "peak_child_resident_set_mb_max": p01et["peak_child_resident_set_mb_max"], "premises": p01et["premises"], "conflict": p01et["conflict"],
                                      "bytes_by_status": p01et["bytes_by_status"], "u042_bytes_checked": 200, "u043_bytes_open": 118},
                  "part01_without_et0": {"VE_RUST_TIMEOUT": "default (unset)", "address_space_cap_bytes": p01["address_space_cap_bytes"], "wall_seconds": p01["wall_seconds"],
                                         "peak_child_resident_set_mb_max": p01["peak_child_resident_set_mb_max"], "premises": p01["premises"], "conflict": p01["conflict"],
                                         "evidence": "evidence/part01-check-ap1b-baseline.json"}}
m["ap1b_probe"] = json.loads((HERE / "evidence" / "ap1b-document-probe.json").read_text())
m["rebuild_command_check"] = {**rebuild, "requalified_at_ap_1b": "part01, part02, part04 and the whole declaration `--check-noop` exit 2; part03 is a no-op; evidence/rebuild-command.json"}
c = m["checks"]
c["build"] = ("ve_service: built in this worktree (`cd lean && lake build ve_service`, 792 jobs, 12 min 56 s; pinned in lean/checkers.lock); Rust: tools/rust_build.py (binary 6422647f.. pinned in lean/checkers.lock, `--check` passes).")
c["companions"] = "PASS: %d companions check (premises model) and %d Lean status rows as expected (previous run: 61 and 136)" % (len(comp), m["status_witness_rows"])
c["parts"] = ("PASS: ve document check on all 4 parts at ve-green-ap-1b: premises 'model', CONFLICT-FREE where norms exist (part01 %.1f s, part02 %.1f s, part03 %.1f s, part04 %.1f s); only part02's document id "
              "changed (its vocabulary changed)" % tuple(pc[f"translation-part0{n}.ve.md"]["seconds"] for n in range(1, 5)))
c["unchanged_units"] = "PASS: 129 of 130 units have the same status and row in the part files as in the previous run; u048 differs (unit-compare.json); source sha256 d6495201.. matches"
c["repaired_units"] = {"u048": "READINGS, two scope readings with a separating model"}
c["seeded_bugs_translation"] = seeded
c.pop("wrong_separating_situation", None)
wl, wc = whole["load"], whole["check"]
c["whole_document"] = {"load": {"coverage_percent": wl["coverage_percent"], "seconds": wl["seconds"]},
                       "check": {"premises": wc["premises"], "readings_status": wc["readings_status"], "seconds": wc["seconds"]},
                       "note": "the whole declaration as one document with u048's repair applied by repair_20261021t1800.py; load, then check, in the foreground"}
c["limits_met"] = [
    "Rust checker: default VE_RUST_TIMEOUT kept. Part01 checks under prlimit --as=6442450944 in %.1f s with a peak child resident set of %.1f MB; no raised limit was needed" % (p01["wall_seconds"], p01["peak_child_resident_set_mb_max"]),
    ("the whole declaration as ONE document (experiment-whole/): six two-reading sets as RD-4b components and the rest (now with u048) in the main component; at ve-green-ap-1b load_document "
     "succeeds after %.1f s (coverage %s%%) and check_document answers %s, premises '%s' after %.1f s (previous run 1343.9 s and 1309.6 s)" % (wl["seconds"], wl["coverage_percent"], wc["readings_status"], wc["premises"], wc["seconds"])),
    old_m["checks"]["limits_met"][2]]
m["whole_document_experiment"]["components"] = {"load": {"coverage_percent": wl["coverage_percent"], "seconds": wl["seconds"]},
                                                "check": {"premises": wc["premises"], "readings_status": wc["readings_status"], "seconds": wc["seconds"]}}
m["whole_document_experiment"]["result"] = "loads and checks at ve-green-ap-1b"
m["whole_document_experiment"]["note"] = ("whole.py was NOT re-run: experiment-whole/translation-whole.ve.md is the previous run's with repair_20261021t1800.py applied (the same edit as to part02), "
                                          "then loaded and checked (whole_check.py load, then check)")
m["language_findings"] = [
    "ap-1b admits `acts@0` in Lean (environment, norms, plain and norm-defaults routes) but `ve document` cannot load an `acts@0` document: the typing check refuses the profile (`UnsupportedProfile: Unsupported profile acts@0`). The 8 act-phrase units (1,403 B) stay blocked until a route carries it (ap-1bb), and joined acts outside a fixed phrase need AP-2/AP-3.",
    "a scope ambiguity in a rights phrase ('within the borders of each state' over movement and residence) is expressible as a reading set of two plain predicates with a separating model (u048, as u073); the predicates are opaque, so which noun the phrase binds is carried by the wording only.",
    "the ET-0 content (finding, act, day) still loads and checks at ve-green-ap-1b, part01 stays CONFLICT-FREE with premises model, in %.1f s with a %.1f MB peak child resident set (evidence/et0-rerun.json); the audit's objection to the civil `day` is about meaning, not about the checker, so it is not landed." % (p01et["wall_seconds"], p01et["peak_child_resident_set_mb_max"]),
    "the committed `--rebuild-reading-ids` is still not a no-op on parts 1, 2, 4 or the whole declaration (`--check-noop` exits 2) and its output does not load; the ids were rebuilt with vocab_patch.reidentified_by.",
    "a unit that has a reading set may also carry its own content in the loader (a seeded fault that asserts one scope beside u048's set is ADMITTED); this is a loader leniency, not used by the translation.",
    "sharing a subject across units works only by naming the same constant in both (u060, u061); there is still no checked cross-unit reference.",
    "scope's effects and `govern` are in Lean but reach no document route, so the SC-M0 tally cannot yet be turned into checked structure."]
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits)",
                          "no seeded bug in product code (this run changed no file under ve/, lean/ or rust/); seeded faults in the translation are in seeded-bugs-translation.json",
                          "JT-5r (the 31 term splits) was not started, as directed",
                          "ET-0's u042 and u043 were measured on a copy and not landed (et0_rerun)",
                          "the eight act-phrase units were not upgraded: ap-1b's profile cannot be used in a document (ap1b_probe)"]
m["source"] = old_m["source"]
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n")
print("claimed", claimed, "verified", verified_bytes, "covered", covered, "counts", dict(counts), "agg", dict(agg))
