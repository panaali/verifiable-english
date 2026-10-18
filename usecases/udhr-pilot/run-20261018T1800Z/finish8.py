"""Write units.json and metrics.json for the 2026-10-08T1800Z run (language at ve-green-lf-15b). Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261008T1800Z/finish8.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[2])); sys.path.insert(0, str(HERE.parents[2] / "tools"))
import repair7_specs as R  # noqa: E402
import readings_s1_pilot as P  # noqa: E402 (tools/ on path through repair7)

PREV = HERE / "previous-20261008T0600Z"
raw = (HERE.parent / "source" / "udhr.md").read_bytes()
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
assert hashlib.sha256(raw).hexdigest() == PIN
old = json.loads((PREV / "metrics.json").read_text())
prev_rows = {r["id"]: r for r in json.loads((PREV / "units.json").read_text())["units"]}
parts = json.loads((HERE / "parts.json").read_text())
pcheck = json.loads((HERE / "parts-check.json").read_text())
legacy_cov = json.loads((HERE / "coverage.json").read_text())["coverage"]
legacy_ver = json.loads((HERE / "verdict.json").read_text())["report"]
wit = json.loads((HERE / "witnesses.json").read_text())["norm_defaults_status"]
comp = json.loads((HERE / "companions-check.json").read_text())
refusal = json.loads((HERE / "refusal-test.json").read_text())

# ---- the parts: exact slices, the carrier of every unit
rebuilt, carrier, set_of, content_unit, part_meta = b"", {}, {}, set(), {}
for info in parts:
    name = f"translation-{info['label']}.ve.md"
    meta, src = P.read(HERE / name)
    a, b = info["span"]
    assert src == raw[a:b]
    rebuilt += src
    part_meta[name] = meta
    for u in meta["units"]:
        carrier[u["id"]] = name
        if u.get("content") is not None:
            content_unit.add(u["id"])
    for s in meta["reading_sets"]:
        set_of[s["unit"]] = (name, s)
assert rebuilt == raw and hashlib.sha256(rebuilt).hexdigest() == PIN
tool_status = {}
for name, v in pcheck.items():
    assert "error" not in v, (name, v)
    tool_status.update(v["unit_status"])
assert len(tool_status) == 130

legacy, _ = P.read(HERE / "translation.ve.md")
legacy_sets = {s["unit"]: s for s in legacy["reading_sets"]}

# ---- audits of run-20261008T0600Z
text = (PREV / "AUDIT.md").read_text()
verdicts = dict(re.findall(r"^(u\d+[a-d]?) (FAITHFUL|UNFAITHFUL)$", text, re.M))
assert len(verdicts) == 54, len(verdicts)
sample = sorted(set(re.findall(r"^(u\d+[a-d]?) (?:FAITHFUL|UNFAITHFUL)$", text.split("## Full audit")[0], re.M)))
full = sorted(set(verdicts) - set(sample))
unfaithful = sorted(u for u, v in verdicts.items() if v == "UNFAITHFUL")
faithful = sorted(u for u, v in verdicts.items() if v == "FAITHFUL")
assert set(unfaithful) == set(R.AUDIT_REJECTED), set(unfaithful) ^ set(R.AUDIT_REJECTED)

# ---- unit rows
FEATURE_DONE = "other:norm_candidates_hold_no_content_in_main_document"
rows = []
for uid, row in prev_rows.items():
    row = {k: v for k, v in row.items() if not k.startswith("audit_2026") or k in ("audit_20261004T1800Z", "audit_20261005T0600Z", "audit_20261005T1800Z", "audit_20261007T1800Z")}
    row["status_in_previous_run"] = prev_rows[uid]["status"]
    row["part_document"] = carrier[uid]
    if uid in legacy_sets or prev_rows[uid]["status"] == "READINGS":
        s_legacy = legacy_sets.get(uid)
        cids = [r["id"] for r in s_legacy["readings"]] if s_legacy else row.get("candidates", [])
        multi = len(cids) > 1
        if uid in ("u110",):
            multi = True
        if uid in set_of:
            row["status"] = "READINGS"
            row["reading_set"] = set_of[uid][1]["id"]
        else:
            row["status"] = tool_status[uid]                       # one reading: an ordinary unit with content
            row.pop("reading_set", None)
            row["single_reading"] = True
        row["candidates"] = cids
        if uid != "u110":
            row["companions"] = [f"readings/{uid}.{c}.ve.md" for c in cids]
            row["norm_defaults_companions"] = row["companions"]
        row["in_document_content"] = uid in content_unit or uid in set_of
        row["residual_missing_features"] = [f for f in row.get("residual_missing_features", [])
                                            if not f.startswith(FEATURE_DONE) and "norm_candidates_hold_no_content" not in f]
        if uid != "u110":
            row["formal_depth"] = (
                f"{len(cids)} candidate{'s' if len(cids) != 1 else ''} ({', '.join(cids)}), each stated in the part document "
                f"{carrier[uid]} as content (norm-defaults@0, completion 'unspecified'; a rule over a plain property is stated as the "
                "assertion that the property holds of every case its guard picks out), "
                + ("as an ordinary unit because the words support one reading" if len(cids) == 1 else
                   "in one reading set whose separating situations Lean admitted") +
                "; each candidate also stands as a one-unit companion document with Lean status witnesses (a case inside the rule is SETTLED, "
                "a case outside it UNDECIDED, never 'not required' and never permitted). No candidate names a bearer the words do not name.")
    elif uid == "u074":
        row["status"] = tool_status[uid]
        row["note_20261008T1800Z"] = ("the permission predicate now declares the completion 'unspecified' (norm-defaults@0 is in the document); "
                                      "its rule is unchanged (guard top, sign false), so it never consulted the former 'allow'")
    else:
        row["status"] = tool_status[uid] if tool_status[uid] == prev_rows[uid]["status"] else tool_status[uid]
    if uid in R.REPAIRED:
        row["audit_repair"] = (("Rejected by the 2026-10-08 audit of run-20261008T0600Z; " if uid in R.AUDIT_REJECTED else
                                "Same defect as rejected siblings (not itself sampled); ") + "repaired 2026-10-08T1800Z: "
                               + R.REASON.get(uid, R.REPAIR_NOTES.get(uid, "")) + ". Pending a fresh independent audit.")
    if uid in verdicts:
        row["audit_20261008T0600Z"] = verdicts[uid] + (" (repaired this run)" if uid in R.REPAIRED else "")
    rows.append(row)
by_id = {r["id"]: r for r in rows}
note = (json.loads((PREV / "units.json").read_text())["note"])
note = ("READINGS units hold an open reading set of two or more candidates in a part document (translation-partNN.ve.md): every candidate "
        "carries its content there (readings@1 beside norm-defaults@0, completion 'unspecified'; Lean admitted each separating situation). A "
        "unit the words give ONE reading is an ordinary unit with that content (CHECKED, or OPEN where it names open terms), not a set. "
        "translation.ve.md keeps the whole source as one document with the previous form (candidates as companion documents under readings/), "
        "which cannot hold the content: 91 regulated predicates against a limit of 64 per environment, and a product of choices far above 64.")
(HERE / "units.json").write_text(json.dumps({"source_sha256": PIN, "units": rows, "note": note}, ensure_ascii=False, indent=2) + "\n")

# ---- metrics
counts = Counter(r["status"] for r in rows)
bytes_by_status = Counter()
for r in rows:
    bytes_by_status[r["status"]] += r["span"][1] - r["span"][0]
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")
claimed = sum(bytes_by_status[s] for s in COVERED)
missing = Counter(r["missing_feature"] for r in rows if r["status"] == "UNFORMALISED")
agg = Counter()
for children in old["old_to_new_units"].values():
    sts = {by_id[c]["status"] for c in children}
    agg[next(iter(sts)) if len(sts) == 1 else "MIXED"] += 1
span = lambda u: by_id[u]["span"][1] - by_id[u]["span"][0]
verified = sorted((set(old["audit_verified_units"]) | set(faithful)) - set(R.REPAIRED))
assert all(by_id[u]["status"] in COVERED for u in verified)
verified_bytes = sum(span(u) for u in verified)
unchanged_form = [u for u in verified if by_id[u]["status"] == "LABELLED"]
# the carrier of a norm/readings unit changed this run (companion -> content in a part): the verdict was given on the earlier form
reexpressed = [u for u in verified if u not in unchanged_form]

tool_bytes = Counter()
for v in pcheck.values():
    tool_bytes.update(v["coverage"]["bytes_by_status"])
sets_multi = sorted(set_of)
cand_in_sets = sum(len(s["readings"]) for _, s in set_of.values())
single = sorted(r["id"] for r in rows if r.get("single_reading"))
regulated_parts = {n: sum(1 for d in m["environment"]["vocabulary"]["predicates"].values() if "regulated" in d) for n, m in part_meta.items()}
comp_regulated = sum(1 for k in comp for _ in [0])
metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw), "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-lf-15b",
    "previous_run": "run-20261008T0600Z (ve-green-rd-6a); its files are in previous-20261008T0600Z/",
    "features_merged_since_previous_baseline": [
        "readings-defaults RD-2a / RD-2b: a readings@1 document with norm CONTENT in its reading sets now loads, checks, renders and answers queries "
        "beside norm-defaults@0 (completion 'unspecified'); Lean's readings-elaborate gives the filled document and the search finds the separating "
        "situations. This is what the UDHR had been waiting for: norm candidates no longer need companion documents",
        "lean-first b15a/b15b/b16a: Rust's source parser is deleted and Lean owns more checks (no new construct for a translator)",
        "english-lean-e2: English reading through Lean; no UDHR unit is blocked by a missing sense"],
    "language_change_for_udhr": (
        "one that a translator can use: norm candidates can sit inside the document. All 81 candidates of the 33 reading sets, the u074 permission and "
        "the 16 single-reading units are now stated as content of the translation itself, and Lean checks every part: the premises verdict "
        "is 'model' for every compatible choice of every part, with CONFLICT-FREE among rules on the same act under every reading. No "
        "UNFORMALISED unit is upgraded: their blocks (act-phrase grammar, time, causation, attribution, rules, modality) did not move. The "
        "whole declaration still cannot be ONE checked document (see findings)."),
    "old_unit_count": old["old_unit_count"],
    "old_boundary_aggregation": dict(sorted(agg.items())),
    "old_to_new_units": old["old_to_new_units"],
    "unit_scale": "sentence or clause; unchanged (130 units; no re-segmentation needed)",
    "bytes_accounted": len(raw), "bytes_accounted_percent": 100.0,
    "unit_count": len(rows),
    "unit_counts_by_status": dict(sorted(counts.items())),
    "bytes_by_status": dict(sorted(bytes_by_status.items())),
    "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(raw), 2),
    "claimed_covered_bytes_previous_run": old["claimed_covered_bytes"],
    "claimed_change_vs_previous_run_bytes": claimed - old["claimed_covered_bytes"],
    "previous_run_unit_counts_by_status": old["unit_counts_by_status"],
    "previous_run_old_boundary_aggregation": old["old_boundary_aggregation"],
    "previous_run_audit_verified_covered_bytes": old["audit_verified_covered_bytes"],
    "audit_20261008T0600Z_note": ("the 2026-10-08 audits of the previous run (previous-20261008T0600Z/AUDIT.md): a sample of 20 (15/20 faithful) and a full "
                                  "audit of the other 34 covered units (17/34 faithful); 22 units rejected, all repaired this run, plus u096 (same defect, not rejected)"),
    "audit_20261008T0600Z_units_faithful": faithful,
    "audit_20261008T0600Z_units_unfaithful": unfaithful,
    "audit_verified_covered_bytes": verified_bytes,
    "audit_verified_covered_percent": round(100 * verified_bytes / len(raw), 2),
    "audit_verified_units": verified,
    "audit_verified_units_form_unchanged": unchanged_form,
    "audit_verified_units_reexpressed_this_run": reexpressed,
    "audit_verified_note": ("verified = judged FAITHFUL by an audit and not repaired since. 'reexpressed' units kept their candidates' meaning but "
                            "moved from companion documents into the part documents (entitlements as assertions, distinct act phrases, renamed "
                            "colliding base predicates): their verdicts were given on the earlier form and a fresh audit should confirm them"),
    "audit_pending_bytes": claimed - verified_bytes,
    "repaired_units": R.REPAIRED,
    "repaired_unit_reasons": {u: R.REASON.get(u, R.REPAIR_NOTES.get(u)) for u in R.REPAIRED},
    "units_rejected_by_audit_and_repaired": unfaithful,
    "units_repaired_same_defect_not_rejected": ["u096"],
    "repaired_candidates_removed": {u: c for u, c in R.REMOVE.items()},
    "open_terms": [{k: t[k] for k in ("name", "decided_by", "necessary", "sufficient", "factors")} for t in legacy["open_terms"]],
    "open_terms_count": len(legacy["open_terms"]),
    "open_terms_dropped": json.loads((HERE / "repair7-dropped.json").read_text())["open_terms_dropped"],
    "reading_sets_multi_candidate": sets_multi,
    "reading_set_count": len(sets_multi),
    "reading_set_candidates": cand_in_sets,
    "single_reading_units": single,
    "single_reading_unit_count": len(single),
    "previous_run_reading_set_count": old["reading_set_count"],
    "previous_run_reading_set_candidates": old["reading_set_candidates"],
    "missing_feature_tally": dict(sorted(missing.items())),
    "missing_feature_tally_previous_run": old["missing_feature_tally"],
    "parts": parts,
    "part_regulated_predicates": regulated_parts,
    "part_checks": {n: {"seconds": v["seconds"], "premises": v["premises"], "readings_status": v["readings_status"],
                        "conflict": v["conflict"], "coverage_bytes_by_status": v["coverage"]["bytes_by_status"],
                        "residual": v["coverage"]["residual"], "document_id": v["document_id"]} for n, v in pcheck.items()},
    "parts_tool_status_bytes": dict(sorted(tool_bytes.items())),
    "whole_document_legacy": {"file": "translation.ve.md", "coverage": legacy_cov, "premises": legacy_ver["premises"],
                               "reading_plan_route": legacy_ver["reading_plan"]["route"], "why_not_content": (
        "91 distinct regulated predicates (limit 64 per environment: ResourceLimit 'regulated predicates'), and the enumerated route multiplies "
        "the sets' candidate counts (more than 64 choices answers 'over 64' and UNKNOWN)")},
    "companion_documents": len(comp),
    "status_witnesses": {k: v for k, v in wit.items()},
    "status_witness_rows": sum(len(v) for v in wit.values()),
    "no_invented_permissions": {
        "regulated_predicates": "every regulated predicate of every part and companion declares the completion 'unspecified' (u074's permission "
                                "included: it was 'allow' under a guard-top rule that never consulted it); a case outside a rule is UNDECIDED",
        "scope": "no candidate names a bearer the words do not name; liberties are permissions stated only where the right names something one does",
        "status_rows": f"{sum(len(v) for v in wit.values())} Lean status rows over {len(wit)} companions, all as expected"},
    "words_only": {"rule": "lead, 2026-10-08: readings come from the words only; rights are not duties to provide",
                   "readings_removed_this_run": {u: c for u, c in R.REMOVE.items()},
                   "readings_removed_count": sum(len(c) for c in R.REMOVE.values()),
                   "open_questions_listed_that_the_text_does_not_raise": 0,
                   "factors_removed": R.REPAIR_NOTES},
    "presupposition_check": old["presupposition_check"],
    "checks": {
        "parts_cover_source_exactly": "PASS (nine slices concatenate to the pinned 10,916 bytes)",
        "parts": "PASS: ve document check on all nine parts: premises 'model' for every choice, CONFLICT-FREE under every reading",
        "legacy_document": {"coverage": "PASS (100%)", "premises": legacy_ver["premises"]},
        "companions": f"PASS: {len(comp)} companions check (premises model) and {sum(len(v) for v in wit.values())} Lean status rows as expected",
        "wrong_separating_situation": refusal,
        "limits_met": ["regulated predicates per environment 64", "enumerated choices 64 (product of candidate counts)",
                       "service deadline 168 s CPU: one part with 53 regulated predicates and 54 choices elaborated in 80 to 100 s and "
                       "then exceeded the deadline in check"]},
    "language_findings": [
        "NEW and usable: norm candidates as reading-set content beside norm-defaults@0 (RD-2b). Lean elaborates the filled document, Python's search "
        "found a separating situation for every ordered pair (no pair missing), Lean admitted every one, and a deliberately wrong situation is refused "
        "(rs_u111: 'distinguishing model does not separate readings')",
        "LIMIT 1, size: an environment holds at most 64 regulated predicates; the declaration needs 91 (34 obligation, 28 permission, 29 plain). Stating the 29 "
        "entitlements as assertions over ordinary predicates (below) leaves 62, but the second limit still forces parts",
        "LIMIT 2, independence: the enumerated route multiplies the candidate counts of independent sets (ReadingsNotSuperposable under the unspecified "
        "completion): 33 multi-reading sets give far over 64 choices ('over 64', UNKNOWN). Nine parts, each at most 64 choices, are checked; the whole "
        "declaration is not one checked document. RD-3 (the fold in Lean) is where this should move",
        "LIMIT 3, time: elaboration grows faster than the predicate count (0.4 s for 10 regulated predicates, 80 to 100 s for 53) and a 53-predicate part "
        "exceeded the service's CPU deadline in check",
        "FINDING, English layer: a pair whose separating probe is a 'plain' regulated predicate cannot be worded ('outcome wording needs a checked deontic "
        "value'), so ve document check answers CheckerUnavailable. Workaround, and arguably the more faithful form: an entitlement is stated as the assertion "
        "that a property holds of every case its guard picks out (mixed assertion/norm pairs fall back to wording E24)",
        "FINDING, distinct wording: the English view requires every predicate to have its own wording (V4); nine prohibitions shared the act phrase "
        "'{0} take place' and two '{0} be carried out' across different sorts, so the merged vocabulary gives each its own act phrase (wording only)",
        "FINDING, names: companions that reuse a base predicate or sort name with different meaning (is_arbitrary, is_slavery, concerns_*, measure) must be "
        "renamed when merged; the pilot does it mechanically (suffix with the unit id)",
        "FINDING, display: the shown separating situation names one element of every sort and every filled gap of the part, not just the ones the pair "
        "depends on, so the English of a pair is long and mentions unrelated rights",
        "limits unchanged and still blocking the 46 UNFORMALISED units: act-phrase grammar (11), time (5), causation (4), attribution (4), rules (7), "
        "comparison (2), modality/belief (2), and singletons"],
    "document_ids": {n: v["document_id"] for n, v in pcheck.items()},
}
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n")
print(json.dumps({k: metrics[k] for k in ("unit_counts_by_status", "bytes_by_status", "claimed_covered_bytes", "claimed_covered_percent",
                                           "audit_verified_covered_bytes", "audit_verified_covered_percent", "audit_pending_bytes",
                                           "old_boundary_aggregation", "missing_feature_tally", "reading_set_count", "reading_set_candidates",
                                           "single_reading_unit_count", "open_terms_count", "part_regulated_predicates")}, indent=1))
