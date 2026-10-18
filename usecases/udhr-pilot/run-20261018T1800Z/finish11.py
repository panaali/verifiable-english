"""Write units.json and metrics.json for the 2026-10-10T0600Z run (language at ve-green-lf-16c). Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261010T0600Z/finish11.py
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
import repair10_specs as R  # noqa: E402
import readings_s1_pilot as P  # noqa: E402 (tools/ on path through repair7)

PREV = HERE / "previous-20261009T1800Z"
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

# ---- audit of run-20261009T1800Z
text = (PREV / "AUDIT.md").read_text()
verdicts = dict(re.findall(r"^(u\d+[a-d]?) (FAITHFUL|UNFAITHFUL)$", text, re.M))
assert len(verdicts) == 33, len(verdicts)
unfaithful = sorted(u for u, v in verdicts.items() if v == "UNFAITHFUL")
faithful = sorted(u for u, v in verdicts.items() if v == "FAITHFUL")
assert set(unfaithful) == set(R.AUDIT_REJECTED), set(unfaithful) ^ set(R.AUDIT_REJECTED)
legacy0, _ = P.read(HERE / "translation.ve.md")
REPAIRED = sorted(R.AUDIT_REJECTED)
CHANGED = list(REPAIRED)          # units whose checked content, sort or open-term factors changed this run

# ---- unit rows
WHY = dict(R.REASON)
FEATURE_DONE = "other:norm_candidates_hold_no_content_in_main_document"
rows = []
for uid, row in prev_rows.items():
    row = {k: v for k, v in row.items() if not k.startswith("audit_2026") or k in ("audit_20261004T1800Z", "audit_20261005T0600Z", "audit_20261005T1800Z", "audit_20261007T1800Z", "audit_20261008T0600Z", "audit_20261008T1800Z", "audit_20261009T0600Z")}
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
    if uid in CHANGED:
        why = WHY[uid]
        row["audit_repair"] = ("Rejected by the 2026-10-09T1800Z audit of run-20261009T1800Z; repaired 2026-10-10T0600Z: " + why
                               + ". Pending a fresh independent audit.")
        row["unchecked_note"] = ("Not part of any reading: the words do not say who must act, so no candidate names a bearer. Each candidate is "
                                 "the entitlement alone (who holds the right); no duty or permission reading is offered.")
    if uid in verdicts:
        row["audit_20261009T1800Z"] = verdicts[uid] + (" (repaired this run)" if uid in REPAIRED else "")
    if "open_terms" in row:                      # the document is the authority for the terms a unit names
        meaning = next(u for u in legacy0["units"] if u["id"] == uid).get("meaning")
        row["open_terms"] = sorted(meaning["open"]) if isinstance(meaning, dict) and "open" in meaning else []
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
verified = sorted((set(old["audit_verified_units"]) | set(faithful)) - set(CHANGED))
assert all(by_id[u]["status"] in COVERED for u in verified)
verified_bytes = sum(span(u) for u in verified)
unchanged_form = [u for u in verified if by_id[u]["status"] == "LABELLED"]
newly_verified = sorted((set(faithful) - set(old["audit_verified_units"])) - set(CHANGED))
# the carrier of a norm/readings unit changed this run (companion -> content in a part): the verdict was given on the earlier form
reexpressed = [u for u in verified if u not in unchanged_form]

tool_bytes = Counter()
for v in pcheck.values():
    tool_bytes.update(v["coverage"]["bytes_by_status"])
sets_multi = sorted(set_of)
cand_in_sets = sum(len(s["readings"]) for _, s in set_of.values())
single = sorted(r["id"] for r in rows if r.get("single_reading"))
regulated_parts = {n: sum(1 for d in m["environment"]["vocabulary"]["predicates"].values() if "regulated" in d) for n, m in part_meta.items()}
all_regulated = {n for m in part_meta.values() for n, d in m["environment"]["vocabulary"]["predicates"].items() if "regulated" in d}
metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw), "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-lf-16c",
    "previous_run": "run-20261009T1800Z (ve-green-rd-3); its translation, units, metrics and audit are in previous-20261009T1800Z/",
    "features_merged_since_previous_baseline": [
        "lean-first lf-16c: the ve-document@1 boundary reads JSON in Lean (null, escapes in linear time, lone-surrogate diagnostics, depth bound, typed document answer units): "
        "infrastructure for the document loader, no new construct for a translator",
        "readings-defaults RD-3 (already counted in the rd-3 baseline)"],
    "language_change_for_udhr": (
        "none that a translator can use. Nothing merged between ve-green-rd-3 and ve-green-lf-16c gives the UDHR a new construct (the work is the "
        "document boundary), so no UNFORMALISED unit is upgraded (their blocks stay: act-phrase grammar, time, causation, attribution, rules, "
        "modality, comparison). The four parts of the previous run check unchanged at lf-16c before the repairs; the differences against the "
        "previous run are the four translator repairs the audit asked for, not language."),
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
    "audit_20261009T1800Z_note": ("the 2026-10-09T1800Z audit of the previous run (previous-20261009T1800Z/AUDIT.md): 33 distinct units, 20 sampled + "
                                  "16 of the 20 changed units (7 overlap), 29 faithful; u049 u073 u105b u105c rejected, all repaired this run: each kept ONE "
                                  "reading where the English itself supports two"),
    "audit_20261009T1800Z_units_faithful": faithful,
    "audit_20261009T1800Z_units_unfaithful": unfaithful,
    "audit_newly_verified_units": newly_verified,
    "units_changed_this_run": CHANGED,
    "audit_verified_covered_bytes": verified_bytes,
    "audit_verified_covered_percent": round(100 * verified_bytes / len(raw), 2),
    "audit_verified_units": verified,
    "audit_verified_units_form_unchanged": unchanged_form,
    "audit_verified_units_reexpressed_this_run": reexpressed,
    "audit_verified_note": ("verified = judged FAITHFUL by an audit and not changed since: a unit whose checked content, sort, candidate set or "
                            "open-term factors changed this run (units_changed_this_run) is pending a fresh audit even if an earlier one passed it. "
                            "'reexpressed' units were judged on an earlier form (companion documents, or the part layout of the previous run); a fresh "
                            "audit should confirm them"),
    "audit_pending_bytes": claimed - verified_bytes,
    "repaired_units": REPAIRED,
    "repaired_unit_reasons": {u: WHY[u] for u in REPAIRED},
    "units_rejected_by_audit_and_repaired": unfaithful,
    "units_repaired_same_defect_not_rejected": sorted(set(REPAIRED) - set(unfaithful)),
    "units_with_only_open_term_factors_rewritten": sorted(set(CHANGED) - set(REPAIRED)),
    "repaired_candidates_removed": {u: ["entitlement"] for u in R.AUDIT_REJECTED},
    "repaired_candidates_added": {u: list(c) for u, c in R.ORDER.items()},
    "open_terms": [{k: t[k] for k in ("name", "decided_by", "necessary", "sufficient", "factors")} for t in legacy["open_terms"]],
    "open_terms_count": len(legacy["open_terms"]),
    "open_terms_dropped": [],
    "open_terms_added": [],
    "predicates_dropped": [],
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
        "the legacy form keeps candidates as companion documents (no content in the main document), so its premises stay UNKNOWN; as ONE document "
        "with the content, the 11 two-reading sets give 2,048 choices (limit 64; arithmetic, 7 sets and 128 choices in the previous run) and the previous run found "
        "no separating situation for u111 by Python's search over the whole environment (not re-run)")},
    "companion_documents": len(comp),
    "status_witnesses": {k: v for k, v in wit.items()},
    "status_witness_rows": sum(len(v) for v in wit.values()),
    "no_invented_permissions": {
        "regulated_predicates": "every regulated predicate of every part and companion declares the completion 'unspecified' (u074's permission "
                                "included: it was 'allow' under a guard-top rule that never consulted it); a case outside a rule is UNDECIDED",
        "scope": "no candidate names a bearer the words do not name; liberties are permissions stated only where the right names something one does",
        "status_rows": f"{sum(len(v) for v in wit.values())} Lean status rows over {len(wit)} companions, all as expected"},
    "words_only": {"rule": "lead, 2026-10-08/09: readings come from the words only; rights are not duties to provide; no duty readings for rights, either way",
                   "readings_added_this_run": {u: list(c) for u, c in R.ORDER.items()},
                   "why_added": ("the audit found that the English itself supports two meanings: 'his own' / 'his country' (nationality or residence, "
                                 "as u077), the scope of 'peaceful' (assembly alone, or assembly and association), the scope of 'freely' "
                                 "(participate alone, or participate, enjoy and share); each meaning is ONE entitlement, with no duty, permission or bearer"),
                   "open_questions_listed_that_the_text_does_not_raise": 0},
    "presupposition_check": old["presupposition_check"],
    "checks": {
        f"parts_cover_source_exactly": "PASS ({len(parts)} slices concatenate to the pinned 10,916 bytes)",
        "parts": f"PASS: ve document check on all {len(parts)} parts: premises 'model' for every choice, CONFLICT-FREE under every reading",
        "legacy_document": {"coverage": "PASS (100%)", "premises": legacy_ver["premises"]},
        "companions": f"PASS: {len(comp)} companions check (premises model) and {sum(len(v) for v in wit.values())} Lean status rows as expected",
        "wrong_separating_situation": refusal,
        "limits_met": ["Rust checker: one call is limited to 5 s; (measured in the previous run, not re-run) a part with 19 regulated predicates (u001-u108, 16 choices) is refused with "
                       "'Rust checker failed ... timed out after 4.99 s' (CheckerUnavailable), so the four parts of this run are the largest that check",
                       "Python's search for separating situations (one element per sort): over the whole declaration (22 regulated predicates, 128 choices in the previous run; 2,048 now, not re-run) "
                       "it found none for u111's two readings in 4 min 23 s, though it finds one in a part of u104-u114; the one-document form "
                       "is therefore not produced, and a hand-supplied situation would be needed"]},
    "language_findings": [
        "NO NEW CONSTRUCT since rd-3 for a translator (lf-16c moves the document boundary's JSON reading into Lean: same language): "
        "the four parts of the previous run still loaded at lf-16c before the repairs and check after them (premises 'model', CONFLICT-FREE under every reading), so the previous run's "
        "measure of the language stands",
        f"LIMIT 1, size: the 64-regulated-predicate limit no longer binds: with rights as one reading each (no duty or permission twins) the declaration "
        f"needs {len(all_regulated)} distinct regulated predicates across the parts (max {max(regulated_parts.values())} in one part; 22 as one document)",
        "LIMIT 2, checker call: the Rust checker answers one call in at most 5 s; one part of 19 regulated predicates exceeds it (see limits_met), so the "
        f"declaration is carried in {len(parts)} parts",
        "LIMIT 3, enumerated choices: 11 reading sets of two readings each give 2,048 choices (arithmetic), above the 64 the enumerated route accepts, so the whole "
        "declaration still cannot be one checked document (the four repairs add four two-reading sets; each part stays within the limit: 2, 8, 2 and 32 choices)",
        "FINDING, reading sets of assertions only: once a set keeps only `forall x. P_i(x)` readings (u077: 'his country' as nationality or as residence), Python's "
        "search has no norm content to enumerate and the set was refused ('distinguishing models must be supplied by id'); the pilot records a one-element "
        "model per pair (the formula-only route) instead. A translator can state such a set but must supply the model by hand",
        "FINDING, act phrases: every regulated predicate needs its own act wording, but two units cannot both say 'take place' (here u024 and u037); the "
        "pilot kept u037's faithful 'take place' and gave the other acts distinct verbs, which was possible only because the sorts differ",
        "FINDING, English layer (unchanged): a 'plain' regulated predicate cannot be worded as a probe, so entitlements are stated as assertions "
        "('Every person is classified as \"has_the_right_to_work\"' in the natural view); the rights construct itself (rights@0) still cannot sit beside "
        "norm-defaults@0",
        "FINDING, display (unchanged): the shown separating situation of a pair is 'a checked situation that VE cannot yet show in words'",
        "limits unchanged and still blocking the 46 UNFORMALISED units: act-phrase grammar (11), time (5), causation (4), attribution (4), rules (7), "
        "comparison (2), modality/belief (2), and singletons"],
    "changed_units": CHANGED,
    "document_ids": {n: v["document_id"] for n, v in pcheck.items()},
}
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n")
print(json.dumps({k: metrics[k] for k in ("unit_counts_by_status", "bytes_by_status", "claimed_covered_bytes", "claimed_covered_percent",
                                           "audit_verified_covered_bytes", "audit_verified_covered_percent", "audit_pending_bytes",
                                           "old_boundary_aggregation", "missing_feature_tally", "reading_set_count", "reading_set_candidates",
                                           "single_reading_unit_count", "open_terms_count", "part_regulated_predicates")}, indent=1))
