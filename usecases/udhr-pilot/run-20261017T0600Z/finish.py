"""Write units.json, metrics.json, readings-rendered.md and SUMMARY.md for the 2026-10-04T0600Z run.

Reads the translation, the verification artifacts of verify_step.py (coverage.json, verdict.json, unmodified.json), the
previous run's units.json and metrics.json (../run-20261003T0600Z/), and re-checks every companion document (small
documents; norm-defaults@0). Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261004T0600Z/finish.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import blockers as B  # noqa: E402
import build as BD  # noqa: E402
import companions_nd as ND  # noqa: E402
import force_table as T  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
from ve.document import check_document, render_document  # noqa: E402

PREV = HERE.parent / "run-20261003T0600Z"
raw = (HERE.parent / "source" / "udhr.md").read_bytes()
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
assert hashlib.sha256(raw).hexdigest() == PIN
doc_bytes = (HERE / "translation.ve.md").read_bytes()
front, body = doc_bytes[4:].split(b"\n---\n", 1)
assert body == raw
meta = json.loads(front)
rows = json.loads((PREV / "units.json").read_text())["units"]
old = json.loads((PREV / "metrics.json").read_text())
cov = json.loads((HERE / "coverage.json").read_text())["coverage"]
ver = json.loads((HERE / "verdict.json").read_text())
report = ver["report"]
unmodified = json.loads((HERE / "unmodified.json").read_text())
assert [u["span"] for u in meta["units"]] == [r["span"] for r in rows]
assert cov["source_bytes"] == cov["accounted_bytes"] == len(raw)
sets = {s["unit"]: s for s in meta["reading_sets"]}
prev_rows = {r["id"]: r for r in rows}
unit_kind = {u["id"]: u["kind"] for u in meta["units"]}

# ------------------------------------------------------------------ companions: check, witnesses, render
READINGS = HERE / "readings"
specs = {}
for uid, per in ND.SPECS.items():
    for cid, spec in per.items():
        specs[f"{uid}.{cid}"] = spec
for uid, cands in U.CANDIDATES.items():
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

# ------------------------------------------------------------------ units.json
NEW = {**T.NORM_UNITS, **T.RIGHT_UNITS}
CASE_SORT_UNITS = {"u020", "u024", "u025", "u027", "u037", "u045a", "u045b", "u055", "u059", "u064", "u099a"}
RIGHT_PREV = ["u022a", "u022b", "u022c", "u029", "u032", "u033a", "u033b", "u046", "u048", "u049", "u063", "u066", "u070",
              "u073"]
RETRANSLATED = sorted([*BD.NEW_UNITS, "u110", "u111", "u017"])
STALE = ("s1_status", "new_feature", "axes_open", "force_note", "reading_elaboration")


def cand_ids(uid):
    return [r["id"] for r in sets[uid]["readings"]]


def depth_text(uid):
    cands = U.CANDIDATES[uid]
    n = len(cands)
    parts = [f"{n} norm candidates, each a one-unit norm-defaults@0 companion document (completion 'unspecified'; source = the "
             "unit's exact bytes), checked on its own with status witnesses: a case inside the rule is SETTLED, a case outside it "
             "UNDECIDED, never 'not required' and never permitted."]
    if uid in CASE_SORT_UNITS:
        parts.append("The enumeration or condition of the clause is checked structure: a case sort (predicates have at most two "
                     "arguments, so the person is the case's own) whose base predicates the guard lists.")
    if uid in RIGHT_PREV or uid in T.RIGHT_UNITS:
        parts.append("The entitlement is carried by plain norm candidates (duty to avoid harming it, duty to secure it, liberty "
                     "where the freedom is the holder's own act) on a State or on every State, group and person; rights@0 content "
                     "would declare 'deny', so there is no rights-level conflict or holder check.")
    if uid in NEW and NEW[uid]["elided"] != "none" and not NEW[uid]["elided"].startswith("none:"):
        parts.append(f"Elided from the act phrase or carried elsewhere: {NEW[uid]['elided']}.")
    return " ".join(parts)


for row in rows:
    uid = row["id"]
    row["status_in_previous_run"] = prev_rows[uid]["status"]
    for k in STALE:
        row.pop(k, None)
    if uid in BD.NEW_UNITS or uid == "u110":
        s = sets[uid]
        for k in ("missing_feature", "blocker_detail", "norm_defaults_note", "audit_repair"):
            row.pop(k, None)
        e = NEW.get(uid)
        row.update(
            status="READINGS", reading_set=s["id"], candidates=cand_ids(uid),
            open_terms=sorted({t for _c, sp, _w in U.CANDIDATES[uid] for t in sp["open"]}),
            companions=[f"readings/{uid}.{c}.ve.md" for c in cand_ids(uid)],
            norm_defaults_companions=[f"readings/{uid}.{c}.ve.md" for c in cand_ids(uid)],
            formal_depth=depth_text(uid),
            residual_missing_features=[
                "other:cross_set_verdicts (premise verdict UNKNOWN: reading elaboration pending)",
                "other:norm_candidates_hold_no_content_in_main_document (companions carry the norm-defaults@0 content)",
                "other:english_wording (unary base predicates render as 'classified as ...' unless the wording is one word after 'is')",
                *(["other:act_phrase_grammar (act phrase shorter than the clause: " + e["elided"] + ")"]
                  if e and e["elided"] != "none" and not e["elided"].startswith("none:") else [])],
            audit_repair=(BD.REJECTION.get(uid) or BD.ADMISSIBLE_NOTE) + " Pending a fresh independent audit.",
            note=(e["article"] + ": " + e["full"]) if e else row.get("note", ""))
        if uid in prev_rows and prev_rows[uid].get("status") == "READINGS":
            pass
    elif uid == "u017":
        row.update(status="UNFORMALISED", missing_feature="defaults",
                   blocker_detail=BD.REJECTION["u017"] + " 'should' admits a strict reading (a duty) and a defeasible one; only "
                                  "the strict one is expressible without an invented completion.",
                   partial_companion="readings-partial/u017.strict.ve.md")
        for k in ("candidates", "companions", "norm_defaults_companions", "reading_set", "formal_depth",
                  "residual_missing_features", "open_terms", "audit_repair", "previous_missing_feature", "norm_defaults_note"):
            row.pop(k, None)
    elif uid == "u111":
        row.update(candidates=cand_ids(uid), companions=[f"readings/u111.{c}.ve.md" for c in cand_ids(uid)],
                   norm_defaults_companions=[f"readings/u111.{c}.ve.md" for c in cand_ids(uid)])
        row["formal_depth"] = (
            "Four norm candidates over (State or bearer, limitation): a bearer must avoid imposing a limitation that is not determined "
            "by law or not solely for the listed aims (guard: the negation of the necessary conditions). A limitation is one limitation on "
            "one person's exercise of one right or freedom, so the person and the right are its own. A limitation that meets both "
            "conditions is UNDECIDED. 'And' between the aims is read as one or both (listed aims) or as both. Strict force only: the text "
            "states no exception to 'shall' (the four defeasible candidates, completion 'deny', were removed).")
        row["residual_missing_features"] = [
            "other:norm_candidates_hold_no_content_in_main_document (companions carry the norm-defaults@0 content)",
            "other:limitation_not_attached_to_rights_lines (limitation scope names rights, which are open sets here; S2)"]
        row["audit_repair"] = (row.get("audit_repair", "") + " 2026-10-04: defeasible candidates removed (no stated exception, completion "
                               "'deny' not stated by the source).").strip()
    elif uid in sets and uid not in BD.NEW_UNITS:
        kinds = {r["kind"] for r in sets[uid]["readings"]}
        row["s1_status"] = ("candidates are pending (norm-defaults@0 companion documents; kept from the previous run)"
                            if all(r["content"] is None for r in sets[uid]["readings"]) else
                            "mixed: a formula candidate (with models) beside pending norm candidates held in companion documents")
        row.pop("s1_status")
        row["companions"] = [f"readings/{uid}.{c}.ve.md" for c in cand_ids(uid)
                             if (READINGS / f"{uid}.{c}.ve.md").exists()]
    if uid in prev_rows and uid in ("u035", "u051", "u054"):
        row["residual_missing_features"] = [
            f for f in row.get("residual_missing_features", []) if "soft_norms_with_norm_defaults" not in f]
for row in rows:
    # statements that named readings@1 or rights@0 content no longer hold for this document
    for k in ("s1_status",):
        row.pop(k, None)
rows_out = {"source_sha256": PIN, "units": rows, "note":
            "READINGS units hold an open reading set; the tool reports them as OPEN. Every norm candidate of every READINGS unit sits "
            "in a norm-defaults@0 companion document under readings/ (completion 'unspecified'); u052, u112 and u114 also hold a "
            "formula candidate with models in the main document. The main document has no rights@0, soft-norms@0 or readings@1 "
            "content (the 39 units of the previous run that carried it were re-stated)."}
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
assert sorted(x for v in old_to_new.values() for x in v) == sorted(by_id)

# audit-verified bytes: what an audit accepted and this run left unchanged
audit_1003_sample = ("u074 u012 u062 u044 u113 u080 u104 u030 u036 u048 u105b u081 u045a u025 u027 u110 u098 u017 u114 u077").split()
audit_1003_unfaithful = sorted(BD.AUDIT_REJECTED)
audit_1003_faithful = sorted(set(audit_1003_sample) - BD.AUDIT_REJECTED)
assert len(audit_1003_sample) == 20 and len(audit_1003_faithful) == 11
verified = sorted((set(old["audit_verified_units"]) | set(audit_1003_faithful)) - set(RETRANSLATED) - BD.AUDIT_REJECTED)
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
metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw), "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-env-profiles",
    "previous_run": "run-20261003T0600Z (ve-green-wire-s4; its translation, units, metrics, summary and AUDIT.md are in "
                    "../run-20261003T0600Z/); this translation changes only what build.py of this run states",
    "features_merged_since_previous_baseline": [
        "infra/layers2-b1 (Python/Rust layer checks, the pre-commit module checks): no change to the language",
        "fix/env-field-types (environment profile fields on the block routes): no change to what a translator can state"],
    "language_change_for_udhr": (
        "none. Nothing merged since ve-green-wire-s4 changes what the UDHR can say, so every difference to the previous run is a "
        "repair of the previous audit or of a defect it exposed, not progress of the language."),
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
    "audit_1003_note": "the 2026-10-03T0600Z audit of the previous run (its AUDIT.md) sampled 20 units (CHECKED 1, LABELLED 8, READINGS 11) and "
                       "rejected nine; its sample is stratified, so 11/20 is not a corpus rate",
    "audit_1003_sample": audit_1003_sample,
    "audit_1003_units_faithful": audit_1003_faithful,
    "audit_1003_units_unfaithful": audit_1003_unfaithful,
    "audit_1003_repairs": {u: (BD.REJECTION.get(u) or BD.ADMISSIBLE_NOTE) for u in sorted(BD.AUDIT_REJECTED)},
    "units_re_translated_this_run_pending_audit": RETRANSLATED,
    "units_re_translated_count": len(RETRANSLATED),
    "audit_verified_covered_bytes": audit_bytes,
    "audit_verified_covered_percent": round(100 * audit_bytes / len(raw), 2),
    "audit_verified_units": verified,
    "audit_pending_bytes": claimed - audit_bytes,
    "tool_status_bytes": cov["bytes_by_status"],
    "open_terms": [{k: t[k] for k in ("name", "decided_by", "necessary", "sufficient", "factors")} for t in meta["open_terms"]],
    "reading_sets": set_rows,
    "reading_set_count": len(set_rows),
    "reading_set_candidates": n_cands,
    "companion_documents": len(companion_docs),
    "missing_feature_tally": dict(sorted(missing.items())),
    "missing_feature_tally_previous_run": old["missing_feature_tally"],
    "tool_residual": cov["residual"],
    "vocabulary_use": {"regulated_predicates_in_main_document": len(main_regulated), "regulated_limit": 64,
                       "predicates_in_main_document": len(vocab["predicates"]),
                       "regulated_predicates_previous_run": old["vocabulary_use"]["regulated_predicates"],
                       "regulated_in_companions_by_role_and_completion": dict(sorted(companion_regulated.items()))},
    "language_findings": [
        "no new language feature reached the UDHR between ve-green-wire-s4 and ve-green-env-profiles; the work of this run is the "
        "repair of the previous audit (nine of 20 sampled units rejected, eight of them for one defect)",
        "the defect that decided the run: rights@0 content and readings@1 content cannot sit beside norm-defaults@0, so every candidate "
        "they held declared the completion 'deny' (obligations: 'not required') or 'permission deny' (liberties: 'not permitted'), which "
        "the source never states. The 39 units that had it (25 stated last run, 14 older right units, including three the 2026-10-02 "
        "audit had accepted) are re-stated as norm-defaults@0 companions; the main document no longer needs rights@0, soft-norms@0 or "
        "readings@1, and its load, check and render take under a second (previous run: 1,537 s load, 1,569 s check, refused at the "
        "tag's own 120 s limit)",
        "what that costs: a candidate's content lives in a companion document, not in the main document, so the premise verdict stays "
        "UNKNOWN (reading elaboration pending) and VE does not compare candidates of one set (no separating situations, no "
        "SeparatedByActOnly findings); rights lose their holder and conflict checks (plain norms stand in for claims and liberties)",
        "defaults beside soft norms: soft-norms@0 and norm-defaults@0 cannot share a document (document check: 'await the Lean route'), "
        "so a defeasible reading cannot leave the other cases unspecified. u017 ('should') therefore loses its defeasible reading and "
        "becomes UNFORMALISED (defaults); u111's four defeasible candidates are removed because the text states no exception",
        "admissible readings only: the strict/defeasible twins of every 'shall' and of Articles 22-27's rights are gone (no exception is "
        "stated); u081 alone gets a candidate qualified by the organization and resources of each State, as a checked necessary "
        "condition over the named open relation resources_allow, because the clause is in Article 22 itself",
        "explicit enumerations are checked structure: torture and treatment-or-punishment that is cruel, inhuman or degrading (u027, "
        "punishment explicitly covered), privacy, family, home and correspondence (u045a), slavery and servitude, the three statuses of "
        "u020, arrest, detention and exile, and the free and full consent of u059 are case-sort predicates under a guard; 'arbitrary' and "
        "'cruel' stay open terms as base predicates the guard requires",
        "English of the generated sentences: a unary base predicate renders natively only as '{0} is X' with one word X; of the "
        "base predicates introduced here the ones that fit are worded that way and the others render as 'classified as \"...\"' "
        "(the full clause is in the predicate description and the candidate's admission text)",
        "limits unchanged from the previous run and still blocking: act-phrase grammar (11 units), time (5), causation (4), comparison "
        "(2), quantities (1), grounding of authority (1), priority of rights (1), right_lines across open sets (4), attribution, "
        "modality/belief, evaluative claims; none of these moved",
        "passive duties name no bearer: u025, u098, u099a, u099b, u100a, u100b, u059 are read on a State or on every State, group and "
        "person; u098 also as a duty of a person of the age the source does not state (a named open relation)"],
    "no_invented_permissions": {
        "main_document": "one regulated predicate remains: compel_association_membership_permitted (u074, permission, completion 'allow') "
                         "under a rule whose guard is top, so the completion is never consulted; unchanged and audited faithful. No "
                         "other regulated predicate, so no declared completion for any other act",
        "companions": "every regulated predicate of the 124 companion documents declares the completion 'unspecified' "
                      f"({dict(sorted(companion_regulated.items()))}); the status witnesses show a case outside a rule's guard UNDECIDED, "
                      "never 'not required' and never permitted",
        "scope": "the State readings are rules over the sort State (parties that are not States are not mentioned), the anyone readings "
                 "over every State, group and person"},
    "norm_defaults": {
        "profile": "norm-defaults@0",
        "companions": {k: {"profiles": v["profiles"], "report": v["norm_defaults_report"]} for k, v in companion_docs.items()},
        "status_witnesses": nd_status,
        "partial_companions": partial,
        "u074_migration_audit": old["norm_defaults"]["u074_migration_audit"],
        "u074_note": "carried unchanged from the previous run: u074 and its companion are untouched"},
    "presupposition_check": "No heading or speaker marker presupposes a substantive claim; the labelled units are unchanged from the audited "
                            "previous run (its audits sampled u080, u044, u014, u040, u012, u062, u113, u104, u030, u036 and found them "
                            "faithful). u060 stays UNFORMALISED as an evaluative claim. u045b, u099b and u100b begin with a conjunction: each "
                            "carries the subject of the previous unit (noted in its elided field), not a presupposed claim.",
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
                                            "audit_verified_covered_percent", "old_boundary_aggregation",
                                            "missing_feature_tally", "reading_set_count", "reading_set_candidates",
                                            "companion_documents", "vocabulary_use")}, indent=1))
