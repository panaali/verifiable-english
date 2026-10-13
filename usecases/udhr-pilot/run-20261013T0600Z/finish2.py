"""Write units.json, metrics.json, witnesses.json and readings-rendered.md for the 2026-10-04T1800Z run.

Starts from the previous run's units.json and metrics.json (kept under previous/ by this script's first run), re-checks every
companion document (norm-defaults@0, completion 'unspecified') and its status witnesses, and patches the nine repaired units.
Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261004T1800Z/finish2.py
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
import repair as RP  # noqa: E402
import repair_specs as R  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
from ve.document import check_document, render_document  # noqa: E402

PREV_DIR = HERE / "previous"
if not PREV_DIR.exists():                      # the 0600Z run's artifacts, as copied at the start of this run
    PREV_DIR.mkdir()
    for name in ("units.json", "metrics.json", "AUDIT.md", "SUMMARY.md"):
        shutil.move(str(HERE / name), str(PREV_DIR / name))
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
    if uid in R.REPAIRED:
        continue
    for cid, spec, _why in cands:
        specs[f"{uid}.{cid}"] = spec
for uid, cands in R.CANDIDATES.items():
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
                          "required' and never permitted. Repaired after the 2026-10-04T0600Z audit: " + RP.REASON[uid] + "."),
            audit_repair=("Rejected by the 2026-10-04T0600Z audit" if uid in ("u022a", "u022c", "u046", "u054", "u087", "u098",
                                                                            "u099b") else
                          "Shares a sentence with a unit the 2026-10-04T0600Z audit rejected (not itself sampled)")
            + "; repaired 2026-10-04T1800Z: " + RP.REASON[uid] + ". Pending a fresh independent audit.",
            residual_missing_features=[
                "other:cross_set_verdicts (premise verdict UNKNOWN: reading elaboration pending)",
                "other:norm_candidates_hold_no_content_in_main_document (companions carry the norm-defaults@0 content)",
                "other:english_wording (plain and unary base predicates render as 'classified as ...' unless the wording is one word "
                "after 'is')"])
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

audit_0600_sample = "u001 u002 u014 u022a u022c u028 u037 u045b u046 u054 u074 u075 u080 u083 u087 u095 u098 u099b u111 u114".split()
audit_0600_unfaithful = sorted("u022a u022c u046 u054 u087 u098 u099b".split())
audit_0600_faithful = sorted(set(audit_0600_sample) - set(audit_0600_unfaithful))
assert len(audit_0600_sample) == 20 and len(audit_0600_faithful) == 13
verified = sorted((set(old["audit_verified_units"]) | set(audit_0600_faithful)) - set(R.REPAIRED))
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
    "baseline": "ve-green-layers2-b2",
    "previous_run": "run-20261004T0600Z (ve-green-env-profiles; its units, metrics, summary and AUDIT.md are in previous/); this "
                    "translation changes only the nine units listed in repaired_units (repair.py, repair_specs.py)",
    "features_merged_since_previous_baseline": [
        "infra/gate-collection (test-collection gate), infra/layers2-b2 (Rust ve-core split into kernel, profile and surface crates "
        "behind a facade): no change to the language",
        "proof/decision-only-sound (a Lean theorem about the readings route; the wire still reports 'separated only by decision' as "
        "not certified): no change to what a translator can state"],
    "language_change_for_udhr": (
        "none. No file under ve/ changed since ve-green-env-profiles (the merged diff is the Rust crate layout, Lean proofs, test "
        "gates and docs), so every difference to the previous run is a repair of "
        "the previous audit, not progress of the language."),
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
    "audit_0600z_note": "the 2026-10-04T0600Z audit of the previous run (previous/AUDIT.md) sampled 20 units (CHECKED 1, LABELLED 8, "
                        "READINGS 11) and rejected seven (u022a, u022c, u046, u054, u087, u098, u099b; the summary of that audit says "
                        "13/20 faithful); its sample is stratified, so 13/20 is not a corpus rate",
    "audit_0600z_sample": audit_0600_sample,
    "audit_0600z_units_faithful": audit_0600_faithful,
    "audit_0600z_units_unfaithful": audit_0600_unfaithful,
    "repaired_units": R.REPAIRED,
    "repaired_unit_reasons": RP.REASON,
    "repaired_candidates_removed": repair_removed,
    "repaired_candidates_added": repair_added,
    "units_rejected_by_audit_and_repaired": audit_0600_unfaithful,
    "units_sharing_a_rejected_sentence_and_repaired": sorted(set(R.REPAIRED) - set(audit_0600_unfaithful)),
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
        "no new language feature reached the UDHR since ve-green-env-profiles; the run repairs the seven units the previous audit "
        "rejected and two units that share a rejected unit's sentence (u022b, u099a)",
        "plain regulated predicates (norms@0 role 'plain' with completion 'unspecified') state an entitlement with no bearer: they let "
        "'Everyone has the right to X' stay a categorical claim whose responsibility is unspecified (u022a-c, u046, u054, u087), "
        "which a bearer-and-person duty cannot do without a guard that may empty it or a universal duty the text does not assign. They "
        "were available before this run; the previous run had not used them for rights",
        "universal positive duties are no longer offered where the text assigns no bearer: protection (u022a-c, u046), enabling "
        "(u087) and making available (u099a, u099b) are States' only; noninterference is still offered for every State, group and "
        "person. The same pattern remains in the other right units this run did not touch (u029, u032, u033a-b, u048, u049, u063, "
        "u066, u070, u073, u081, u084a-d, u096, u105a-c): they still carry an 'anyone' positive candidate and no bearer-less "
        "entitlement, and would need the same audit",
        "antecedents of 'such' are checked structure when the antecedent is a named list: u046's case sort carries the interference "
        "and attacks of the preceding sentence, in two scopes (with or without 'arbitrary'); the predicate is not a reference to u045a "
        "and u045b, because the document format has no cross-unit reference for a base predicate",
        "a parent-or-guardian duty is expressible with a sort of its own (u098); the age gate is gone, so 'for whom it is compulsory' "
        "stays inside the open term compulsory instead of an invented relation",
        "act phrases are at most 80 bytes of plain words and may not contain and, or, for, if, is, no, not (the checker's grammar); "
        "u087's purpose clause therefore reads 'to protect interests' and its noninterference candidate 'leave ... free to form as well "
        "as join trade unions'",
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
