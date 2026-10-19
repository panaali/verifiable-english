"""Write units.json, metrics.json, witnesses.json and readings-rendered.md for the 2026-10-08T0600Z run.

Starts from the previous run's units.json and metrics.json (previous-20261007T1800Z/), re-checks every companion document
(norm-defaults@0, completion 'unspecified') and its status witnesses (Lean's status rows, witnesses_nd.py), and patches the units
repaired this run (repair6.py, repair6_specs.py). Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261008T0600Z/finish7.py
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
import repair3_specs as R3  # noqa: E402
import repair4_specs as R4  # noqa: E402
import repair5_specs as R5  # noqa: E402
import repair6_specs as R  # noqa: E402
import repair_specs as RS  # noqa: E402
import udhr_specs as U  # noqa: E402
import witnesses_nd as WND  # noqa: E402
from ve.document import check_document, render_document  # noqa: E402

PREV_DIR = HERE / "previous-20261007T1800Z"
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
for uid, cands in [*U.CANDIDATES.items(), *RS.CANDIDATES.items(), *R2.CANDIDATES.items(), *R3.NEW_CANDIDATES.items(),
                   *R4.NEW_CANDIDATES.items(), *R5.NEW_CANDIDATES.items(), *R.NEW.items()]:
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
stale = [uid for uid in R.REPAIRED if uid != 'u110' for r in sets[uid]["readings"] if f"{uid}.{r['id']}" not in companion_docs]
extra = sorted(k for k in companion_docs if k.split('.')[0] in R.ORDER and k.split('.')[1] not in R.ORDER[k.split('.')[0]])
assert not extra, extra
assert not [p for p in companion_docs if p.startswith('u110.')], 'u110 has asserted readings only'
assert not stale, stale

RP_REASON = R.REASON

# ------------------------------------------------------------------ units.json
AUDIT_SAMPLE = ("u002 u021 u023 u027 u033b u038 u044 u046 u059 u063 u074 u077 u095 u099a u099b u100b u104 u105c u107 u110").split()
AUDIT_UNFAITHFUL = sorted("u046 u063 u077 u100b u105c u110".split())
AUDIT_FAITHFUL = sorted(set(AUDIT_SAMPLE) - set(AUDIT_UNFAITHFUL))
assert len(AUDIT_SAMPLE) == 20 and len(AUDIT_FAITHFUL) == 14
assert set(AUDIT_UNFAITHFUL) == set(R.AUDIT_REJECTED)
OPENS = {r["id"]: r.get("open_terms", []) for r in prev_rows.values()}
_old_sets = {s["unit"]: s for s in old["reading_sets"]}


def repair_gone_ids(uid):
    return sorted(set(c["id"] for c in _old_sets[uid]["candidates"]) - set(r["id"] for r in sets[uid]["readings"]))

rows = []
for uid, row in prev_rows.items():
    row = dict(row)
    row["status_in_previous_run"] = row["status"]
    row.pop("status_in_previous_run_2", None)
    for key in [k for k in row if k.startswith("audit_2026") and k != "audit_20261005T1800Z"]:
        pass
    if uid in R.REPAIRED:
        s = sets[uid]
        cids = [r["id"] for r in s["readings"]]
        why = R.REASON[uid]
        history = (f"Rejected by the 2026-10-07T1800Z audit" if uid in R.AUDIT_REJECTED else
                   "Words-only repair (lead, 2026-10-08): readings that came from outside knowledge or named a bearer the words do not name are removed")
        if uid == "u110":
            row.update(
                reading_set=s["id"], candidates=cids, companions=[], norm_defaults_companions=[],
                open_terms=["community_of_full_development", "duties_to_the_community", "free_and_full_development"],
                formal_depth="2 asserted candidates over a community sort (relations: has duties to, free and full development is "
                             "possible in): per_person (every person has duties to a community in which that person's development "
                             "is possible and in no other; the community may differ between persons) and one_for_all (one community "
                             "for everyone with the same property). Lean checks the separating situation (m1 separates them; a "
                             "situation that does not separate them is refused). Repaired after the 2026-10-07T1800Z audit: " + why + ".")
        else:
            one = len(cids) == 1
            row.update(
                reading_set=s["id"], candidates=cids, open_terms=OPENS[uid],
                companions=[f"readings/{uid}.{c}.ve.md" for c in cids],
                norm_defaults_companions=[f"readings/{uid}.{c}.ve.md" for c in cids],
                formal_depth=((f"{len(cids)} norm candidate{'s' if not one else ''} ({', '.join(cids)}), each a one-unit "
                               "norm-defaults@0 companion document (completion 'unspecified'; source = the unit's exact bytes), checked "
                               "on its own with Lean-checked status witnesses: a case inside the rule is SETTLED, a case outside it "
                               "UNDECIDED, never 'not required' and never permitted. The words support ")
                              + ("one reading, so the set holds one candidate. " if one else f"{len(cids)} readings. ")
                              + "No candidate names a bearer the words do not name. Repaired 2026-10-08T0600Z: " + why + "."))
        row["audit_repair"] = history + "; repaired 2026-10-08T0600Z: " + why + ". Pending a fresh independent audit."
        row["words_only_single_reading"] = len(cids) == 1
        gone = [c for c in repair_gone_ids(uid) if any(w in c for w in ("state", "anyone", "country", "guardian"))]
        if gone:
            row["unchecked_note"] = ("Not part of any reading: the words do not say who must act, so no candidate names a bearer. A reader "
                                     "who knows how the Declaration is used in later treaties may expect States to be the bearers; "
                                     "removed readings: " + ", ".join(gone) + ".")
    if uid in AUDIT_SAMPLE:
        row["audit_20261007T1800Z"] = "UNFAITHFUL (repaired this run)" if uid in AUDIT_UNFAITHFUL else "FAITHFUL"
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

lost = sorted(set(AUDIT_FAITHFUL) & set(R.REPAIRED))   # audited faithful last time, changed now: no longer audit-verified
verified = sorted((set(old["audit_verified_units"]) | set(AUDIT_FAITHFUL)) - set(R.REPAIRED))
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

bearer_sorts = {}
for path in sorted(READINGS.glob("*.ve.md")):
    voc = json.loads(path.read_bytes()[4:].split(b"\n---\n", 1)[0])["environment"]["vocabulary"]
    for name in voc["sorts"]:
        if name in ("state", "bearer", "country", "guardian", "tribunal"):
            bearer_sorts[path.name[:-len(".ve.md")]] = name
single_reading_sets = sorted(s["unit"] for s in meta["reading_sets"] if len(s["readings"]) == 1)

metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw), "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-rd-6a",
    "previous_run": "run-20261007T1800Z (ve-green-readings-defaults; its units, metrics, verdict, coverage, translation, rendered view, "
                    "readings and AUDIT.md are in previous-20261007T1800Z/); this translation changes only the units listed in "
                    "repaired_units (repair6.py, repair6_specs.py)",
    "features_merged_since_previous_baseline": [
        "lean-first b6 (Lean): soft norms move to Lean behind the same answers (no UDHR unit uses soft-norms@0 any more)",
        "lean-first b10b (Lean): norm defaults move to Lean and Python's status semantics are deleted; the status witnesses of the "
        "companions are now Lean's `norm-defaults-status` rows (witnesses_nd.py was rewritten to read them); the language a "
        "translator writes is unchanged",
        "readings-defaults RD-8 (Lean and Python): `ve-document@1` may name `senses`, and then every `surface: english` fence is read by "
        "Lean's sense reader (word senses, defaults, refusals that say which sense to add). It reads one FOL-expressible sentence per fence "
        "in a document without norm-defaults@0, soft-norms@0, rights@0 or readings@1; no UDHR unit is blocked by a missing sense, so "
        "none can be upgraded by it",
        "readings-defaults RD-6a (Lean): the superposition with a carried base-premise family is stated and proved; nothing calls it "
        "and RD-2 to RD-5 (norm content in a reading set beside norm-defaults@0, the verdict fold, companions as components) are still "
        "not built, so the norm readings stay in companion documents and the premises verdict stays UNKNOWN"],
    "language_change_for_udhr": (
        "none that a translator can use. Of the four merges since ve-green-readings-defaults, lf-6 and lf-10b relocate soft norms and "
        "norm defaults to Lean behind the same answers, rd-8 adds English fences with word senses to documents that carry none of "
        "the profiles the UDHR needs, and rd-6a adds Lean statements nothing calls. `ve document` still has no norm content in a "
        "reading set beside norm-defaults@0 (RD-4b `companion` is refused in Python until RD-4a), so no UNFORMALISED unit is "
        "upgraded. Every difference to the previous run is a repair, not progress of the language."),
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
    "audit_20261005T0600Z_note": old["audit_20261005T0600Z_note"],
    "audit_20261005T0600Z_sample": old["audit_20261005T0600Z_sample"],
    "audit_20261005T0600Z_units_faithful": old["audit_20261005T0600Z_units_faithful"],
    "audit_20261005T0600Z_units_unfaithful": old["audit_20261005T0600Z_units_unfaithful"],
    "audit_20261005T1800Z_note": old["audit_20261005T1800Z_note"],
    "audit_20261005T1800Z_sample": old["audit_20261005T1800Z_sample"],
    "audit_20261005T1800Z_units_faithful": old["audit_20261005T1800Z_units_faithful"],
    "audit_20261005T1800Z_units_unfaithful": old["audit_20261005T1800Z_units_unfaithful"],
    "audit_20261006T1800Z_note": old["audit_20261006T1800Z_note"],
    "audit_20261006T1800Z_sample": old["audit_20261006T1800Z_sample"],
    "audit_20261006T1800Z_units_faithful": old["audit_20261006T1800Z_units_faithful"],
    "audit_20261006T1800Z_units_unfaithful": old["audit_20261006T1800Z_units_unfaithful"],
    "audit_20261007T1800Z_note": "the 2026-10-07T1800Z audit of the previous run (previous-20261007T1800Z/AUDIT.md) sampled 20 units "
                                 "(CHECKED 1, LABELLED 8, READINGS 11) with random.Random('20261007T1800Z') and rejected six "
                                 "(u046, u063, u077, u100b, u105c, u110); 14/20 faithful, a sample of the claimed units, not a corpus rate",
    "audit_20261007T1800Z_sample": AUDIT_SAMPLE,
    "audit_20261007T1800Z_units_faithful": AUDIT_FAITHFUL,
    "audit_20261007T1800Z_units_unfaithful": AUDIT_UNFAITHFUL,
    "repaired_units": R.REPAIRED,
    "repaired_unit_reasons": RP_REASON,
    "repaired_candidates_removed": repair_removed,
    "repaired_candidates_added": repair_added,
    "repaired_candidates_replaced_in_place": {},
    "units_rejected_by_audit_and_repaired": AUDIT_UNFAITHFUL,
    "units_repaired_for_the_words_only_rule": sorted(set(R.REPAIRED) - set(AUDIT_UNFAITHFUL)),
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
        "no construct reached the UDHR since ve-green-readings-defaults: lf-6 and lf-10b move soft norms and norm defaults to Lean, "
        "rd-8 adds English fences with word senses, rd-6a adds Lean statements. RD-2 to RD-5 (norm content in a reading set beside "
        "norm-defaults@0, the verdict fold, companions as components, the pilot migration) are still not built, so the norm readings "
        "live in companion documents and the main document's premises verdict stays UNKNOWN. No UNFORMALISED unit can be upgraded",
        "the words-only rule is expressible with what exists: a passive or an unnamed duty keeps its bearer out of the language. A "
        "prohibition ('No one shall be held in slavery') is a permission predicate over the thing itself (the holding) refused by the "
        "rule; a duty ('shall be made available') is an obligation over the thing with no bearer argument; 'has the right to X' is the "
        "entitlement (a plain predicate), the liberty (a permission) and claims that say, of no stated party, what must hold of every "
        "person. VE reports such a case SETTLED and every other case UNDECIDED, and says nothing about any State, group or person",
        "a limit that remains: an obligation's act phrase is 80 bytes with no 'and', 'not', 'or', 'for', 'no' or 'is' and no comma, and "
        "an English-view noun may not hold 'the' or 'and'. The combined (noninterference plus securing) reading of nine long rights "
        "is therefore a claim over a sort of right holders (persons) whose name is the right's topic and whose description carries the "
        "source's whole phrase; a plain obligation over the person cannot carry the phrase twice",
        "the status witnesses of the companions are Lean's rows since lf-10b: the previous Python `situation`/`status` objects no longer "
        "exist, and witnesses_nd.py reads `norm-defaults-status` (enumerate, then the `undecided` replay) through the public route",
        "limits unchanged and still blocking: act-phrase grammar (11 units), time (5), causation (4), comparison (2), quantities (1), "
        "grounding of authority (1), priority of rights (1), right_lines across open sets (4), attribution, modality/belief, "
        "evaluative claims; defaults beside soft norms (u017); none of these moved"],
    "no_invented_permissions": {
        "main_document": old["no_invented_permissions"]["main_document"],
        "companions": f"every regulated predicate of the {len(companion_docs)} companion documents declares the completion 'unspecified' "
                      f"({dict(sorted(companion_regulated.items()))}); the status witnesses (Lean rows) show a case outside a rule's guard "
                      "UNDECIDED, never 'not required' and never permitted",
        "scope": "no companion makes a State, a group or a person who is not named by the words a bearer: the State and anyone readings "
                 "are removed; the entitlement readings, the claims, the liberties, the prohibitions and the unassigned readings have no "
                 "bearer argument; the bearers that remain are named by the words (the tribunals of u035, society and the State of u061, "
                 "the person who must attend of u098); u110's readings are assertions, not norms"},
    "words_only": {
        "rule": "lead, 2026-10-08: a reading set is allowed only where the English itself supports more than one meaning; no reading "
                "from outside knowledge (who usually bears a duty); outside knowledge only in an unchecked note",
        "readings_removed": repair_removed,
        "readings_removed_count": sum(len(v) for v in repair_removed.values()),
        "bearer_sorts_remaining": bearer_sorts,
        "single_reading_sets": single_reading_sets,
        "unchecked_notes": ("Outside knowledge that would help a reader (for instance that the Declaration is addressed to States and "
                            "that treaties assign these duties to States) is not put in any reading and is not a candidate; it may "
                            "be said in the summary, as an unchecked remark."),
        "open_questions_listed_that_the_text_does_not_raise": 0},
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
