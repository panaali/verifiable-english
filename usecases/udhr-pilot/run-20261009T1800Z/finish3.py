"""Write units.json, metrics.json, witnesses.json and readings-rendered.md for the 2026-10-05T0600Z run.

Starts from the previous run's units.json and metrics.json (previous-1800Z/), re-checks every companion document
(norm-defaults@0, completion 'unspecified') and its status witnesses, and patches the units repaired this run.
Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261005T0600Z/finish3.py
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))
import companions_nd as ND  # noqa: E402
import repair2 as RP  # noqa: E402
import repair2_specs as R  # noqa: E402
import repair_specs as RS  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
from ve.document import check_document, render_document  # noqa: E402

PREV_DIR = HERE / "previous-1800Z"
prev_rows = {r["id"]: r for r in json.loads((PREV_DIR / "units.json").read_text())["units"]}
old = json.loads((PREV_DIR / "metrics.json").read_text())

raw = (HERE.parent / "source" / "udhr.md").read_bytes()
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
assert hashlib.sha256(raw).hexdigest() == PIN
doc_bytes = (HERE / "translation.ve.md").read_bytes()
front, body = doc_bytes[4:].split(b"\n---\n", 1)
assert body == raw
meta = json.loads(front)
cov = json.loads((HERE / "coverage.json").read_text())["coverage"]
ver = json.loads((HERE / "verdict.json").read_text())
report = ver["report"]
unmodified = json.loads((HERE / "unmodified.json").read_text())
assert cov["source_bytes"] == cov["accounted_bytes"] == len(raw)
assert [u["span"] for u in meta["units"]] == [r["span"] for r in prev_rows.values()]
sets = {s["unit"]: s for s in meta["reading_sets"]}

# ------------------------------------------------------------------ companions: check, witnesses, render
READINGS = HERE / "readings"
specs = {}
for uid, per in ND.SPECS.items():
    for cid, spec in per.items():
        specs[f"{uid}.{cid}"] = spec
for uid, cands in U.CANDIDATES.items():
    if uid in R.REPAIRED or uid in RS.REPAIRED:
        continue
    for cid, spec, _why in cands:
        specs[f"{uid}.{cid}"] = spec
for uid, cands in [*RS.CANDIDATES.items(), *R.CANDIDATES.items()]:
    for cid, spec, _why in cands:
        specs[f"{uid}.{cid}"] = spec
companion_docs, nd_status = {}, {}
for path in sorted(READINGS.glob("*.ve.md")):
    uid, cid = path.name.split(".")[:2]
    verdict = check_document(path)
    assert verdict["premises"]["status"] == "model", (path.name, verdict["premises"])
    profiles = json.loads(path.read_bytes()[4:].split(b"\n---\n", 1)[0])["environment"]["profiles"]
    assert "norm-defaults@0" in profiles, path.name
    companion_docs[f"{uid}.{cid}"] = {"path": f"readings/{path.name}", "premises": verdict["premises"]["status"],
                                      "coverage_bytes": verdict["coverage"]["bytes_by_status"], "profiles": profiles,
                                      "norm_defaults_report": (verdict.get("norm_defaults") or {}).get("report")}
    spec = specs.get(f"{uid}.{cid}")
    assert spec is not None and not spec.get("soft"), path.name
    outs = WND.run(path, spec)
    assert all(o["as_expected"] for o in outs), (path.name, outs)
    nd_status[f"{uid}.{cid}"] = outs
(HERE / "readings-rendered.md").write_text("\n\n".join(
    f"## {k}\n\n" + render_document(HERE / v["path"]) for k, v in sorted(companion_docs.items())) + "\n")
partial = sorted(p.name for p in (HERE / "readings-partial").glob("*.ve.md"))
stale = [uid for uid in R.REPAIRED for r in sets[uid]["readings"] if f"{uid}.{r['id']}" not in companion_docs]
assert not stale, stale

# ------------------------------------------------------------------ units.json
AUDIT_1800_SAMPLE = ("u022a u045a u037 u025 u061 u100b u074 u050 u034 u084c u111 u036 u073 u062 u021 u033a u095 u020 u084a "
                     "u014").split()
AUDIT_1800_UNFAITHFUL = sorted("u100b u084c u073 u033a u084a".split())
AUDIT_1800_FAITHFUL = sorted(set(AUDIT_1800_SAMPLE) - set(AUDIT_1800_UNFAITHFUL))
assert len(AUDIT_1800_SAMPLE) == 20 and len(AUDIT_1800_FAITHFUL) == 15
assert set(AUDIT_1800_UNFAITHFUL) == set(R.AUDIT_REJECTED)
rows = []
for uid, row in prev_rows.items():
    row = dict(row)
    row["status_in_previous_run"] = row["status"]
    row.pop("status_in_previous_run_2", None)
    if uid in R.REPAIRED:
        s = sets[uid]
        cids = [r["id"] for r in s["readings"]]
        opens = sorted({t for _c, sp, _w in R.CANDIDATES[uid] for t in sp["open"]})
        row.update(
            reading_set=s["id"], candidates=cids, open_terms=opens,
            companions=[f"readings/{uid}.{c}.ve.md" for c in cids],
            norm_defaults_companions=[f"readings/{uid}.{c}.ve.md" for c in cids],
            formal_depth=(f"{len(cids)} norm candidate{'s' if len(cids) > 1 else ''} ({', '.join(cids)}), each a one-unit "
                          "norm-defaults@0 companion document (completion 'unspecified'; source = the unit's exact bytes), checked on "
                          "its own with status witnesses: a case inside the rule is SETTLED, a case outside it UNDECIDED, never 'not "
                          "required' and never permitted. Repaired after the 2026-10-04T1800Z audit: " + RP.REASON[uid] + "."),
            audit_repair=("Rejected by the 2026-10-04T1800Z audit" if uid in R.AUDIT_REJECTED else
                          "Carries the defect the 2026-10-04T1800Z audit named in other units (not itself sampled)")
            + "; repaired 2026-10-05T0600Z: " + RP.REASON[uid] + ". Pending a fresh independent audit.",
            residual_missing_features=[
                "other:cross_set_verdicts (premise verdict UNKNOWN: reading elaboration pending)",
                "other:norm_candidates_hold_no_content_in_main_document (companions carry the norm-defaults@0 content)",
                "other:english_wording (plain and unary base predicates render as 'classified as ...' unless the wording is one word "
                "after 'is')"])
    if uid in AUDIT_1800_SAMPLE:
        row["audit_20261004T1800Z"] = "UNFAITHFUL (repaired this run)" if uid in AUDIT_1800_UNFAITHFUL else "FAITHFUL"
    rows.append(row)
rows_out = {"source_sha256": PIN, "units": rows,
            "note": prev_rows and json.loads((PREV_DIR / "units.json").read_text())["note"]}
(HERE / "units.json").write_text(json.dumps(rows_out, ensure_ascii=False, indent=2) + "\n")

# ------------------------------------------------------------------ metrics
by_id = {r["id"]: r for r in rows}
counts = Counter(r["status"] for r in rows)
bytes_by_status = Counter()
for r in rows:
    bytes_by_status[r["status"]] += r["span"][1] - r["span"][0]
missing = Counter(r["missing_feature"] for r in rows if r["status"] == "UNFORMALISED")
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")
claimed = sum(bytes_by_status[s] for s in COVERED)
old_to_new = old["old_to_new_units"]
aggregation = Counter()
for children in old_to_new.values():
    statuses = {by_id[c]["status"] for c in children}
    aggregation[next(iter(statuses)) if len(statuses) == 1 else "MIXED"] += 1

assert all(u not in R.REPAIRED for u in AUDIT_1800_FAITHFUL)
verified = sorted((set(old["audit_verified_units"]) | set(AUDIT_1800_FAITHFUL)) - set(R.REPAIRED))
assert all(by_id[u]["status"] in COVERED for u in verified), [u for u in verified if by_id[u]["status"] not in COVERED]
audit_bytes = sum(by_id[u]["span"][1] - by_id[u]["span"][0] for u in verified)

vocab = meta["environment"]["vocabulary"]
main_regulated = {n: p for n, p in vocab["predicates"].items() if "regulated" in p}
companion_regulated = Counter()
for path in READINGS.glob("*.ve.md"):
    env = json.loads(path.read_bytes()[4:].split(b"\n---\n", 1)[0])["environment"]["vocabulary"]["predicates"]
    for p in env.values():
        if "regulated" in p:
            companion_regulated[f"{p['regulated']['role']}:{p['regulated']['default']}"] += 1
set_rows = [{"id": s["id"], "unit": s["unit"], "version": s["version"],
             "candidates": [{"id": r["id"], "kind": r["kind"],
                             "companion": (f"readings/{s['unit']}.{r['id']}.ve.md"
                                           if (READINGS / f"{s['unit']}.{r['id']}.ve.md").exists() else None)}
                            for r in s["readings"]]} for s in meta["reading_sets"]]
n_cands = sum(len(s["readings"]) for s in meta["reading_sets"])
old_cands = old["reading_set_candidates"]
repair_removed = {u: sorted(set(c["id"] for c in next(s for s in old["reading_sets"] if s["unit"] == u)["candidates"])
                            - set(r["id"] for r in sets[u]["readings"])) for u in R.REPAIRED}
repair_added = {u: sorted(set(r["id"] for r in sets[u]["readings"])
                          - set(c["id"] for c in next(s for s in old["reading_sets"] if s["unit"] == u)["candidates"]))
                for u in R.REPAIRED}

metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw), "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-difffuzz",
    "previous_run": "run-20261004T1800Z (ve-green-layers2-b2; its units, metrics, summary and AUDIT.md are in previous-1800Z/, the "
                    "0600Z run's in previous-0600Z/); this translation changes only the units listed in repaired_units "
                    "(repair2.py, repair2_specs.py)",
    "features_merged_since_previous_baseline": [
        "lean-first b0, b3, b4 (the readings route, norms@0, norm-defaults@0 and discourse routes now relay Lean's answers through one "
        "transport; ve/readings_s1.py and ve/discourse.py shrink by about 2,300 lines): the same answers, checked by differential "
        "tests, no new construct",
        "english-lean (English in Lean, S1a and S1b; conformance engines only), infra/testselect2, infra/difffuzz (tests and fuzz "
        "corpora), infra/testperf: no change to what a translator can state",
        "numeral and name hardening (numeral_value, wording_key, MAX_CARVE_OUTS 8 and rule_name in the norms@0 contract): limits and "
        "error types, not constructs"],
    "language_change_for_udhr": (
        "none. The diff of ve/ between ve-green-layers2-b2 and ve-green-difffuzz moves logic from Python into Lean behind the same "
        "wire answers, adds wire contracts for norms@0 and norm-defaults@0, and hardens numerals; no profile, construct or "
        "act-phrase rule was added or relaxed. Every difference to the previous run is a repair of the previous audit, not "
        "progress of the language."),
    "old_unit_count": old["old_unit_count"],
    "old_boundary_aggregation": dict(sorted(aggregation.items())),
    "old_to_new_units": old_to_new,
    "unit_scale": "sentence or clause; unchanged from the previous run (130 units; no re-segmentation needed)",
    "bytes_accounted": cov["accounted_bytes"], "bytes_accounted_percent": cov["coverage_percent"],
    "unit_count": len(rows),
    "unit_counts_by_status": dict(sorted(counts.items())),
    "bytes_by_status": dict(sorted(bytes_by_status.items())),
    "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(raw), 2),
    "claimed_covered_bytes_previous_run": old["claimed_covered_bytes"],
    "claimed_covered_bytes_previous_run_percent": old["claimed_covered_percent"],
    "claimed_change_vs_previous_run_bytes": claimed - old["claimed_covered_bytes"],
    "previous_run_unit_counts_by_status": old["unit_counts_by_status"],
    "previous_run_old_boundary_aggregation": old["old_boundary_aggregation"],
    "previous_run_audit_verified_covered_bytes": old["audit_verified_covered_bytes"],
    "audit_0600z_note": old["audit_0600z_note"],
    "audit_0600z_sample": old["audit_0600z_sample"],
    "audit_0600z_units_faithful": old["audit_0600z_units_faithful"],
    "audit_0600z_units_unfaithful": old["audit_0600z_units_unfaithful"],
    "audit_1800z_note": "the 2026-10-04T1800Z audit of the previous run (previous-1800Z/AUDIT.md) sampled 20 units (CHECKED 1, LABELLED 7, "
                        "READINGS 12) with random.Random('20261004T1800Z').sample and rejected five (u033a, u073, u084a, u084c, "
                        "u100b); 15/20 faithful, a sample of the claimed units, not a corpus rate",
    "audit_1800z_sample": AUDIT_1800_SAMPLE,
    "audit_1800z_units_faithful": AUDIT_1800_FAITHFUL,
    "audit_1800z_units_unfaithful": AUDIT_1800_UNFAITHFUL,
    "repaired_units": R.REPAIRED,
    "repaired_unit_reasons": RP.REASON,
    "repaired_candidates_removed": repair_removed,
    "repaired_candidates_added": repair_added,
    "units_rejected_by_audit_and_repaired": AUDIT_1800_UNFAITHFUL,
    "units_sharing_a_rejected_sentence_and_repaired": sorted(set(R.REPAIRED) - set(AUDIT_1800_UNFAITHFUL)),
    "units_re_translated_this_run_pending_audit": R.REPAIRED,
    "units_re_translated_count": len(R.REPAIRED),
    "audit_verified_covered_bytes": audit_bytes,
    "audit_verified_covered_percent": round(100 * audit_bytes / len(raw), 2),
    "audit_verified_units": verified,
    "audit_pending_bytes": claimed - audit_bytes,
    "tool_status_bytes": cov["bytes_by_status"],
    "open_terms": [{k: t[k] for k in ("name", "decided_by", "necessary", "sufficient", "factors")} for t in meta["open_terms"]],
    "reading_sets": set_rows,
    "reading_set_count": len(set_rows),
    "reading_set_candidates": n_cands,
    "reading_set_candidates_previous_run": old_cands,
    "companion_documents": len(companion_docs),
    "missing_feature_tally": dict(sorted(missing.items())),
    "missing_feature_tally_previous_run": old["missing_feature_tally"],
    "tool_residual": cov["residual"],
    "vocabulary_use": {"regulated_predicates_in_main_document": len(main_regulated), "regulated_limit": 64,
                       "predicates_in_main_document": len(vocab["predicates"]),
                       "regulated_in_companions_by_role_and_completion": dict(sorted(companion_regulated.items()))},
    "language_findings": [
        "no new language feature reached the UDHR since ve-green-layers2-b2 (lean-first and english-lean relocate checking into Lean "
        "behind the same answers); the run repairs the five units the 1800Z audit rejected and the 16 units with the same defect",
        "the audit's pattern is now closed for every right unit: where a right sentence names no bearer, the reading set has a "
        "bearer-less entitlement (a plain regulated predicate, completion 'unspecified'), noninterference for every State, group and "
        "person where the right has a noninterference side, protection or enabling for States only, and a State reading that "
        "combines noninterference with protection in one act phrase (u048, u063, u066, u070, u073, u084a, u084b, u096, u105a, u105b)",
        "the universal positive candidate ('every State, group and person must secure/protect/provide') is gone from all right "
        "units that still had one; the passive purposes of Article 26(2) (u100a, u100b) are a State duty plus a bearer-less statement "
        "about education, because a passive 'shall be directed' assigns no individual duty",
        "act phrases cap at 80 bytes with one use of each slot in order and no 'and', 'or', 'for', 'if', 'is', 'no', 'not': the "
        "combined acts of u063, u066, u073 and u105a therefore drop a connective or 'freedom of' / 'of the community' (the candidate's "
        "admission text says which); u100b avoids the cap by a case sort of the two objects of respect (human rights; fundamental "
        "freedoms), which also restores the word 'fundamental' the audit found missing",
        "regulated predicate names are capped at 56 bytes under norm-defaults@0 (unspecified name length); four longer names were "
        "shortened, which a translator can only learn by running the loader",
        "antecedents of 'such' (u046), a parent-or-guardian duty (u098) and plain entitlements (u022a-c, u054, u087) are as in the "
        "previous run",
        "English of the generated sentences: plain and unary base predicates render as 'classified as \"...\"' unless the wording is "
        "one word after 'is'; the full clause is in the predicate description and the candidate's admission text",
        "limits unchanged and still blocking: act-phrase grammar (11 units), time (5), causation (4), comparison (2), quantities (1), "
        "grounding of authority (1), priority of rights (1), right_lines across open sets (4), attribution, modality/belief, "
        "evaluative claims; defaults beside soft norms (u017); none of these moved"],
    "no_invented_permissions": {
        "main_document": old["no_invented_permissions"]["main_document"],
        "companions": f"every regulated predicate of the {len(companion_docs)} companion documents declares the completion 'unspecified' "
                      f"({dict(sorted(companion_regulated.items()))}); the status witnesses show a case outside a rule's guard UNDECIDED, "
                      "never 'not required' and never permitted",
        "scope": "the State readings are rules over the sort State (parties that are not States are not mentioned), the anyone readings "
                 "over every State, group and person, the entitlement readings name no bearer"},
    "norm_defaults": {
        "profile": "norm-defaults@0",
        "companions": {k: {"profiles": v["profiles"], "report": v["norm_defaults_report"]} for k, v in companion_docs.items()},
        "status_witnesses": nd_status,
        "partial_companions": partial,
        "u074_migration_audit": old["norm_defaults"]["u074_migration_audit"],
        "u074_note": "carried unchanged: u074 and its companion are untouched"},
    "presupposition_check": old["presupposition_check"],
    "checks": {
        "document_load": f"PASS ({json.loads((HERE / 'coverage.json').read_text())['load_seconds']} s; the tag's own limits suffice)",
        "byte_partition": "PASS (units partition all 10,916 bytes)",
        "document_check": "PASS", "premises": report["premises"],
        "coverage": "PASS (100% of bytes accounted)",
        "tag_limits": unmodified,
        "companion_documents": companion_docs,
        "witnesses": "PASS: every companion settles the cases inside its rule and reports UNDECIDED outside it (witnesses.json, "
                     "metrics.norm_defaults.status_witnesses)",
        "render": "PASS (rendered.md, readings-rendered.md)"},
    "document_id": report["document_id"], "source_id": report["source_id"], "coverage_tool": cov,
}
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n")
(HERE / "witnesses.json").write_text(json.dumps({"norm_defaults_status": nd_status}, ensure_ascii=False, indent=2,
                                                sort_keys=True) + "\n")
print(json.dumps({k: metrics[k] for k in ("unit_counts_by_status", "bytes_by_status", "claimed_covered_bytes",
                                            "claimed_covered_percent", "audit_verified_covered_bytes",
                                            "audit_verified_covered_percent", "audit_pending_bytes", "old_boundary_aggregation",
                                            "missing_feature_tally", "reading_set_count", "reading_set_candidates",
                                            "reading_set_candidates_previous_run", "companion_documents", "vocabulary_use")}, indent=1))
