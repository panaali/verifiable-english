"""Write units.json, metrics.json, witnesses.json and readings-rendered.md for the 2026-10-05T1800Z run.

Starts from the previous run's units.json and metrics.json (previous-20261005T0600Z/), re-checks every companion document
(norm-defaults@0, completion 'unspecified') and its status witnesses, and patches the units repaired this run.
Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261005T1800Z/finish4.py
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
import repair2_specs as R2  # noqa: E402
import repair3_specs as R  # noqa: E402
import repair_specs as RS  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
from ve.document import check_document, render_document  # noqa: E402

PREV_DIR = HERE / "previous-20261005T0600Z"
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
    if uid in R2.REPAIRED or uid in RS.REPAIRED or uid in R.REPAIRED:
        continue
    for cid, spec, _why in cands:
        specs[f"{uid}.{cid}"] = spec
for uid, cands in [*RS.CANDIDATES.items(), *R2.CANDIDATES.items(), *R.NEW_CANDIDATES.items()]:
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
stale = [uid for uid in R.REPAIRED if uid != 'u112' for r in sets[uid]["readings"] if f"{uid}.{r['id']}" not in companion_docs]
assert not stale, stale

RP_REASON = R.REASON

# ------------------------------------------------------------------ units.json
AUDIT_0600_SAMPLE = "u074 u012 u028 u014 u026 u011 u088 u002 u056 u081 u025 u033a u098 u105c u073 u064 u051 u112 u070 u061".split()
AUDIT_0600_UNFAITHFUL = sorted("u098 u073 u051 u112".split())
AUDIT_0600_FAITHFUL = sorted(set(AUDIT_0600_SAMPLE) - set(AUDIT_0600_UNFAITHFUL))
assert len(AUDIT_0600_SAMPLE) == 20 and len(AUDIT_0600_FAITHFUL) == 16
assert set(AUDIT_0600_UNFAITHFUL) == set(R.AUDIT_REJECTED)
rows = []
for uid, row in prev_rows.items():
    row = dict(row)
    row["status_in_previous_run"] = row["status"]
    row.pop("status_in_previous_run_2", None)
    if uid in R.REPAIRED:
        s = sets[uid]
        cids = [r["id"] for r in s["readings"]]
        why = RP_REASON[uid]
        history = ("Rejected by the 2026-10-05T0600Z audit" if uid in R.AUDIT_REJECTED else
                   "Carries the defect the 2026-10-05T0600Z audit named in u073 (not itself sampled)")
        if uid == "u112":
            row.update(
                formal_depth="Two candidates: a norm candidate, a prohibition on carrying out an exercise (a norm-defaults@0 companion; "
                             "guards: an exercise of a right or freedom set forth in this Declaration, and contrary to the purposes and "
                             "principles of the United Nations; other exercises UNDECIDED), and an asserted formula over exercises: "
                             "no exercise that is both an exercise of a right or freedom set forth in this Declaration and contrary to "
                             "UN purposes and principles is protected by the right or freedom. Repaired after the 2026-10-05T0600Z "
                             "audit: " + why + ".")
        else:
            opens = row.get("open_terms", [])
            row.update(
                reading_set=s["id"], candidates=cids, open_terms=opens,
                companions=[f"readings/{uid}.{c}.ve.md" for c in cids],
                norm_defaults_companions=[f"readings/{uid}.{c}.ve.md" for c in cids],
                formal_depth=(f"{len(cids)} norm candidate{'s' if len(cids) > 1 else ''} ({', '.join(cids)}), each a one-unit "
                              "norm-defaults@0 companion document (completion 'unspecified'; source = the unit's exact bytes), checked on "
                              "its own with status witnesses: a case inside the rule is SETTLED, a case outside it UNDECIDED, never 'not "
                              "required' and never permitted. Repaired after the 2026-10-05T0600Z audit: " + why + "."))
        row["audit_repair"] = history + "; repaired 2026-10-05T1800Z: " + why + ". Pending a fresh independent audit."
    if uid in AUDIT_0600_SAMPLE:
        row["audit_20261005T0600Z"] = "UNFAITHFUL (repaired this run)" if uid in AUDIT_0600_UNFAITHFUL else "FAITHFUL"
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

assert all(u not in R.REPAIRED for u in AUDIT_0600_FAITHFUL)
verified = sorted((set(old["audit_verified_units"]) | set(AUDIT_0600_FAITHFUL)) - set(R.REPAIRED))
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
    "baseline": "ve-green-english-lean-s2",
    "previous_run": "run-20261005T0600Z (ve-green-difffuzz; its units, metrics, summary and AUDIT.md are in previous-20261005T0600Z/, "
                    "the earlier runs' in previous-older/); this translation changes only the units listed in repaired_units "
                    "(repair3.py, repair3_specs.py)",
    "features_merged_since_previous_baseline": [
        "compose-s2 (S2a): verdicts across the readings of a set that carries content (conflict, premise status, dead readings, ALL/SOME/NONE "
        "queries), but only for readings@1 content; beside norm-defaults@0 it stays S1's abstention (docs/spec/composition-s2.md 4.10), and "
        "the UDHR's norm candidates live in norm-defaults@0 companions, so the premise verdict stays UNKNOWN",
        "lean-first b1/b3b/b3d (response-shape encoders proved in Lean, lazy scans, type-strict comparison): the same answers, no new construct",
        "english-lean S1/S2 (the English reader and grammar in Lean, `ve_english_route`; english.admission is shadow-only and only a named "
        "override dispatches it): no construct a translator can state, no act-phrase limit moved"],
    "language_change_for_udhr": (
        "none. The ve/ diff between ve-green-difffuzz and ve-green-english-lean-s2 adds S2a verdicts for readings@1 content (not reachable "
        "beside norm-defaults@0), moves checking into Lean behind the same answers, and adds the Lean English reader as a shadow; no profile, "
        "construct or act-phrase rule was added or relaxed. Every difference to the previous run is a repair of the previous audit, not "
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
    "audit_1800z_note": old["audit_1800z_note"],
    "audit_1800z_sample": old["audit_1800z_sample"],
    "audit_1800z_units_faithful": old["audit_1800z_units_faithful"],
    "audit_1800z_units_unfaithful": old["audit_1800z_units_unfaithful"],
    "audit_20261005T0600Z_note": "the 2026-10-05T0600Z audit of the previous run (previous-20261005T0600Z/AUDIT.md) sampled 20 units "
                                 "(CHECKED 1, LABELLED 8, READINGS 11 by its own count) with random.Random('20261005T0600Z') and rejected "
                                 "four (u098, u073, u051, u112); 16/20 faithful, a sample of the claimed units, not a corpus rate",
    "audit_20261005T0600Z_sample": AUDIT_0600_SAMPLE,
    "audit_20261005T0600Z_units_faithful": AUDIT_0600_FAITHFUL,
    "audit_20261005T0600Z_units_unfaithful": AUDIT_0600_UNFAITHFUL,
    "repaired_units": R.REPAIRED,
    "repaired_unit_reasons": RP_REASON,
    "repaired_candidates_removed": repair_removed,
    "repaired_candidates_added": repair_added,
    "repaired_candidates_replaced_in_place": {"u051": ["state_avoid", "anyone_avoid"], "u098": ["guardian_ensures"],
                                              "u112": ["exercise_unprotected (formula restricted to declared rights)"]},
    "units_rejected_by_audit_and_repaired": AUDIT_0600_UNFAITHFUL,
    "units_sharing_a_rejected_sentence_and_repaired": sorted(set(R.REPAIRED) - set(AUDIT_0600_UNFAITHFUL)),
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
        "no new language feature reached the UDHR since ve-green-difffuzz (compose-s2 verdicts need readings@1 content, which refuses "
        "norm-defaults@0; lean-first and english-lean relocate checking into Lean behind the same answers); the run repairs the four units "
        "the 0600Z audit rejected and the six combined candidates with the defect it named",
        "act phrases cap at 80 bytes with one use of each slot in order and no 'and', 'or', 'for', 'if', 'is', 'no', 'not': the combined "
        "(noninterference plus protection) acts of u048, u063, u066, u073, u084a and u105a could not carry the source's whole phrase "
        "('within the borders of each state', 'with others', 'freedom of', 'of the community') and are removed rather than abridged; u070, "
        "u084b, u096 and u105b fit and stay. The same limit makes u051's duties say 'abroad' for 'in other countries'",
        "a guard can name a binary relation (u098: 'is a parent or guardian of' between a guardian and a person), so a duty can be scoped "
        "to the persons in a relationship; elsewhere the case is UNDECIDED, never a duty",
        "a vocabulary change (u112's exercise_of_declared_right) re-identifies every content-bearing reading and model of the main "
        "document: meaning and model ids of all reading sets changed, their contents did not",
        "the audit's pattern is closed for every right unit: where a right sentence names no bearer, the reading set has a bearer-less "
        "entitlement, noninterference for every State, group and person where the right has a noninterference side, protection or "
        "enabling for States only; u051's duties no longer narrow 'everyone' to the persecuted",
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
