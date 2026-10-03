"""Write units.json, metrics.json, readings-rendered.md and SUMMARY.md for the 2026-10-03T0600Z run.

Reads the translation, the verification artifacts of verify_step.py (coverage.json, verdict.json, unmodified.json), the
previous run's units.json and metrics.json (prev-run-20261002T1800Z/), and re-checks every companion document
(small documents; norm-defaults@0 and soft-norms@0 routes). Nothing here calls a model.
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
import witnesses_nd as WND  # noqa: E402
from ve.document import check_document, load_document, render_document  # noqa: E402

PREV = HERE.parent / "prev-run-20261002T1800Z"
raw = (HERE.parent / "source" / "udhr.md").read_bytes()
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
assert hashlib.sha256(raw).hexdigest() == PIN
doc_bytes = (HERE / "translation.ve.md").read_bytes()
front, body = doc_bytes[4:].split(b"\n---\n", 1)
assert body == raw
meta = json.loads(front)
rows = json.loads((PREV / "units.json").read_text())["units"]
old = json.loads((PREV / "metrics.json").read_text())
cov_art = json.loads((HERE / "coverage.json").read_text())
cov = cov_art["coverage"]
ver = json.loads((HERE / "verdict.json").read_text())
report = ver["report"]
unmodified = json.loads((HERE / "unmodified.json").read_text())
assert [u["span"] for u in meta["units"]] == [r["span"] for r in rows]
assert cov["source_bytes"] == cov["accounted_bytes"] == len(raw)
sets = {s["unit"]: s for s in meta["reading_sets"]}
prev_rows = {r["id"]: r for r in rows}

# ------------------------------------------------------------------ companions: check, witnesses, render
READINGS = HERE / "readings"
companion_docs, nd_status = {}, {}
spans = {u["id"]: u["span"] for u in meta["units"]}
for path in sorted(READINGS.glob("*.ve.md")):
    uid, cid = path.name.split(".")[:2]
    verdict = check_document(path)
    assert verdict["premises"]["status"] == "model", (path.name, verdict["premises"])
    profiles = json.loads(path.read_bytes()[4:].split(b"\n---\n", 1)[0])["environment"]["profiles"]
    companion_docs[f"{uid}.{cid}"] = {"path": f"readings/{path.name}", "premises": verdict["premises"]["status"],
                                      "coverage_bytes": verdict["coverage"]["bytes_by_status"], "profiles": profiles,
                                      "norm_defaults_report": (verdict.get("norm_defaults") or {}).get("report")}
    spec = ND.SPECS.get(uid, {}).get(cid)
    if spec is not None and not spec.get("soft"):
        outs = WND.run(path, spec)
        assert all(o["as_expected"] for o in outs), (path.name, outs)
        nd_status[f"{uid}.{cid}"] = outs
(HERE / "readings-rendered.md").write_text("\n\n".join(
    f"## {k}\n\n" + render_document(HERE / v["path"]) for k, v in sorted(companion_docs.items())) + "\n")

# ------------------------------------------------------------------ units.json
NEW = {**T.NORM_UNITS, **T.RIGHT_UNITS}
OPEN_FORCE = {"Article 22", "Article 23", "Article 26", "Article 27"}


def candidates_of(uid):
    return [r["id"] for r in sets[f"{uid}"]["readings"]]


NO_CONTENT = "other:norm_candidates_hold_no_content_in_main_document (the companions keep norm-defaults@0 content; readings@1 cannot take it)"
REPAIRED_DEPTH = {
    "u035": ("Two norm candidates under norm-defaults@0 over (tribunal or State, violation): a competent national tribunal must provide the "
             "victim of a violation with an effective remedy, or a State must ensure that competent national tribunals give the "
             "violation's victim one. A violation is one violation of one person's right by one act, so each victim of an act is owed a "
             "remedy; the scope ('violates a fundamental right granted by the constitution or by law') is a guard, elsewhere UNDECIDED. "
             "'Effective', 'competent' and 'fundamental rights granted' are named open terms.",
             [NO_CONTENT, "other:victim_inside_a_sort (the victim is the violation's own, not a third argument: predicates have at most two)",
              "defaults (strict force is assumed; a defeasible reading would need soft-norms@0 beside norm-defaults@0)"]),
    "u054": ("Two norm candidates: a claim on whichever bearer owes the person a nationality (guard: the base relation owes_nationality_to, "
             "open term bearer_of_the_nationality_duty), never on the person, and a liberty to have a nationality. The source names no "
             "bearer; no accomplished fact is stated.",
             [NO_CONTENT, "other:existential_bearer ('some state must grant it' is not a norm over bearers; the open relation names the bearer)"]),
    "u051": ("Three norm candidates under norm-defaults@0: a liberty to seek and enjoy asylum from persecution in other countries, and the "
             "duty to avoid barring a person who suffers or is threatened with persecution from seeking as well as enjoying it, on every "
             "State or on every bearer. The guard is exposure to persecution, suffered or threatened (open term persecution), and does not "
             "require asylum seeking to have begun. No positive grant candidate.",
             [NO_CONTENT, "defaults (as u035)"]),
    "u111": ("Eight norm candidates over (bearer, limitation): a bearer (a State, or any State, group or person) must avoid imposing a "
             "limitation that is not determined by law or not solely for the listed aims (guard: the negation of the necessary conditions). "
             "A limitation is one limitation on one person's exercise of one right or freedom, so the person and the right are its own. A "
             "limitation that meets both conditions is UNDECIDED: the necessary conditions are never read as sufficient. 'And' between the "
             "aims is read as one or both (listed aims) or as both; 'shall' as strict (norm-defaults@0) or defeasible (soft-norms@0, "
             "completion 'deny').",
             [NO_CONTENT, "other:soft_norms_with_norm_defaults (the four defeasible candidates keep the declared completion 'deny' = not required)",
              "other:limitation_not_attached_to_rights_lines (limitation scope names rights, which are open sets here; S2)"]),
}
for row in rows:
    uid = row["id"]
    row["status_in_previous_run"] = prev_rows[uid]["status"]
    if uid in NEW:
        e = NEW[uid]
        s = sets[uid]
        labels = sorted({a for r in s["readings"] for a in r.get("labels", {}) if a != "force"})
        for k in ("missing_feature", "blocker_detail", "norm_defaults_note"):
            row.pop(k, None)
        word = e.get("word") if uid in T.NORM_UNITS else None
        row.update(
            status="READINGS", previous_missing_feature="other:force_variants_in_one_reading_set",
            reading_set=s["id"], candidates=candidates_of(uid), open_terms=e["open"],
            new_feature="composition S1 (readings@1): content-bearing candidates; a strict and a defeasible reading of one "
                        "rule in one reading set, with one checked finite situation per ordered pair of candidates",
            axes_open=labels,
            force_note=(("'" + word + "' read as must (strict) or as should (defeasible, with an open exception whose decider "
                         "the source does not name)") if word else
                        ("the unit carries or opens its force: " + (
                            "force opened by Article 22 ('in accordance with the organization and resources of each State'); "
                            "a strict candidate and a defeasible candidate whose exception factor is that clause"
                            if e.get("article") in OPEN_FORCE and uid in T.RIGHT_UNITS else
                            "'shall' is carried from the previous unit; a strict and a defeasible candidate"))),
            formal_depth=("Every candidate is a complete " + ("plain norm" if uid in T.NORM_UNITS else "right block (holder, one claim line)")
                          + f" ({len(s['readings'])} candidates, {len(s['readings']) * (len(s['readings']) - 1)} ordered pairs, each "
                          "separated by a checked finite situation: Lean admits it, Python regenerates Lean's answer, Rust replays it "
                          "untrusted). Strict/default twins are separated only by the open exception's decision, which VE reports as "
                          "SeparatedByDecisionOnly (not certified: decision_only_sound is unproved). The full source clause is quoted in "
                          "each predicate's description."
                          + ("" if e["elided"] == "none" else
                             (f" Note: {e['elided'][len('none: '):]}." if e["elided"].startswith("none:") else
                              f" Elided from the act phrase or carried elsewhere: {e['elided']}."))),
            residual_missing_features=[
                "defaults (the predicate declares the completion 'deny' = not required, which the source does not state: "
                "norm-defaults@0's 'unspecified' is refused beside readings@1 content; no permission follows for anyone)",
                *([] if e["elided"].startswith("none") else
                  ["other:act_phrase_grammar (act phrase shorter than the clause: see formal_depth)"]),
                "other:cross_set_verdicts (premise verdict UNKNOWN: superposition pending, S2)"],
            note=e["article"] + ": " + e["full"])
    elif uid in B.BLOCKERS:
        tag, feature, detail = B.BLOCKERS[uid]
        row.update(missing_feature=feature, blocker_detail=detail,
                   previous_missing_feature=prev_rows[uid]["missing_feature"])
        row.pop("norm_defaults_note", None)
    elif uid in ("u013ba", "u013bb"):
        row.pop("norm_defaults_note", None)
        row["blocker_detail"] = (
            "'shall strive ...': the strict/defeasible force part is expressible since composition S1, but 'strive' is "
            "effort, not an outcome, and 'constantly' (u013ba) and 'by progressive measures' (u013bb) are time; the "
            "proclamation's bearer is 'every individual and every organ of society' (a sort with no regulated duty here).")
    if uid in BD.REPAIRED:
        row["formal_depth"], row["residual_missing_features"] = REPAIRED_DEPTH[uid]
        row["audit_repair"] = BD.AUDIT_1800[uid]
        row["candidates"] = [r["id"] for r in sets[uid]["readings"]]
        row["companions"] = [f"readings/{uid}.{c}.ve.md" for c in row["candidates"]]
        row["norm_defaults_companions"] = [f"readings/{uid}.{c}.ve.md" for c in row["candidates"]
                                           if not ND.SPECS[uid][c].get("soft")]
    if uid in sets and uid not in NEW:
        s = sets[uid]
        kinds = {r["kind"] for r in s["readings"]}
        if all(r["content"] is None for r in s["readings"]):
            row["s1_status"] = ("candidates are pending (norm-defaults@0 companion documents): readings@1 cannot take their content, "
                                "since the completion 'unspecified' is refused outside norm-defaults@0 and readings@1 content is "
                                "refused beside norm-defaults@0")
        elif kinds == {"right"}:
            row["s1_status"] = ("content-bearing under readings@1: admitted with a checked situation for every pair; the premise "
                                "verdict is UNKNOWN until S2")
        else:
            row["s1_status"] = ("mixed: a formula candidate (today's validation, with models) beside pending norm candidates held in "
                                "companion documents")
    row["previous_status"] = prev_rows[uid]["status"]
    row.pop("previous_status", None)
rows_out = {"source_sha256": PIN, "units": rows, "note":
            "READINGS units hold an open reading set; the tool reports them as OPEN. The 25 units newly stated and the 14 "
            "Article 3-21 right units carry content in the document (readings@1); the norm candidates of u017, u052, u112, "
            "u114, u035, u051, u077, u054, u111, u061, u110 sit in readings/ companion documents (completion unspecified "
            "where the profile allows)."}
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

# audit-verified bytes: what the audits accepted and this run left unchanged
audit_1800_sample = ("u074 u077 u035 u073 u054 u112 u017 u063 u070 u033a u022b u061 u049 u111 u033b u051 u080 u044 u014 u040").split()
audit_1800_unfaithful = sorted(BD.REPAIRED)
audit_1800_faithful = sorted(set(audit_1800_sample) - set(audit_1800_unfaithful))
assert len(audit_1800_sample) == 20 and len(audit_1800_faithful) == 16
retranslated = sorted([*BD.REPAIRED, *NEW])
verified = sorted((set(old["audit_verified_units"]) | set(audit_1800_faithful)) - set(retranslated))
assert all(by_id[u]["status"] in COVERED for u in verified)
audit_bytes = sum(by_id[u]["span"][1] - by_id[u]["span"][0] for u in verified)

vocab = meta["environment"]["vocabulary"]
regulated = {n: p for n, p in vocab["predicates"].items() if "regulated" in p}
readings = report["readings"]
wordings = Counter(p["wording"] for s in readings["sets"] for p in s["pairs"])
not_certified = [f for s in readings["sets"] for f in s["not_certified"]]
new_sets = [sets[u] for u in NEW]
new_pairs = sum(len(s["readings"]) * (len(s["readings"]) - 1) // 2 for s in new_sets)
set_rows = [{"id": s["id"], "unit": s["unit"], "version": s["version"],
             "candidates": [{"id": r["id"], "kind": r["kind"], "labels": r.get("labels"),
                             "content_in_document": r["content"] is not None,
                             "companion": (f"readings/{s['unit']}.{r['id']}.ve.md"
                                           if (READINGS / f"{s['unit']}.{r['id']}.ve.md").exists() else None)}
                            for r in s["readings"]]} for s in meta["reading_sets"]]
timing = {"previous_translation_as_readings@1_document_search_load_check_seconds": 101.3,
          "this_translation_load_seconds": cov_art["load_seconds"], "this_translation_check_seconds": ver["check_seconds"],
          "this_translation_render_seconds": 1549.9,
          "unmodified_tag_limits": unmodified,
          "note": "ve/backends/lean.py run_readings_cases has a fixed 120 s timeout for the one Lean call that admits the whole "
                  "document; the verification steps raised it in the harness script only (verify_step.py, VE_LEAN_TIMEOUT)."}
metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw), "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-wire-s4",
    "previous_run": "run-20261002T1800Z (ve-green-wire; prev-run-20261002T1800Z/ holds its translation, units, metrics, summary and AUDIT.md); "
                    "this translation starts from its final document and changes only what the build.py of this run states",
    "features_merged_since_previous_baseline": [
        "composition S1 (readings@1, merged 2026-10-02): content-bearing reading candidates (norm, right, right lines, limitation); a strict "
        "and a defeasible reading of one rule in one reading set; one checked situation per pair; findings SeparatedByActOnly and "
        "SeparatedByDecisionOnly (not certified); source-word English (E14), outcome English (E19)",
        "wire-contract S4 (Python and Lean public diagnostics, signed message changes): plumbing, no change to what a translator can state",
        "soft-norms diagnostics and norm-defaults fill route fixes: no change to the language"],
    "language_change_for_udhr": (
        "one: composition S1 removes the recorded blocker of 43 'shall' and Articles 22-27 units (other:force_variants_in_one_reading_set). "
        "25 of them are now stated as reading sets of strict and defeasible candidates over bearer, force and, for entitlements, "
        "polarity; the other 18 meet a second blocker that the old reason had hidden (act-phrase grammar 7, time 4, causation 2, "
        "comparison 2, quantities 1, grounding of authority 1, priority of rights 1). The 4 'this right includes' units "
        "(other:right_lines_in_reading_sets) stay blocked: S1 admits right_lines candidates but not a right that another open "
        "set declares (UnknownRight, tested). Nothing else changed for the translator."),
    "old_unit_count": old["old_unit_count"],
    "old_boundary_aggregation": dict(sorted(aggregation.items())),
    "old_to_new_units": old_to_new,
    "unit_scale": "sentence or clause; unchanged from the previous run (130 units; u022 split into u022a-c and u111a/u111b merged there)",
    "bytes_accounted": cov["accounted_bytes"], "bytes_accounted_percent": cov["coverage_percent"],
    "unit_count": len(rows),
    "unit_counts_by_status": dict(sorted(counts.items())),
    "bytes_by_status": dict(sorted(bytes_by_status.items())),
    "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(raw), 2),
    "claimed_covered_bytes_previous_run": old["claimed_covered_bytes"],
    "claimed_covered_bytes_previous_run_percent": old["claimed_covered_percent"],
    "newly_covered_bytes": claimed - old["claimed_covered_bytes"],
    "previous_run_unit_counts_by_status": old["unit_counts_by_status"],
    "previous_run_old_boundary_aggregation": old["old_boundary_aggregation"],
    "previous_run_audit_verified_covered_bytes": old["audit_verified_covered_bytes"],
    "audit_1800_note": "the 2026-10-02T1800Z audit of the previous run (its AUDIT.md) sampled 20 units (u074, 15 READINGS, 4 LABELLED) and "
                       "rejected four; its sample is stratified, so 16/20 is not a corpus rate",
    "audit_1800_sample": audit_1800_sample,
    "audit_1800_units_faithful": audit_1800_faithful,
    "audit_1800_units_unfaithful": audit_1800_unfaithful,
    "audit_1800_repairs": BD.AUDIT_1800,
    "units_re_translated_this_run_pending_audit": retranslated,
    "newly_stated_units": sorted(NEW),
    "newly_stated_bytes": sum(by_id[u]["span"][1] - by_id[u]["span"][0] for u in NEW),
    "audit_verified_covered_bytes": audit_bytes,
    "audit_verified_covered_percent": round(100 * audit_bytes / len(raw), 2),
    "audit_verified_units": verified,
    "audit_pending_bytes": claimed - audit_bytes,
    "tool_status_bytes": cov["bytes_by_status"],
    "open_terms": [{k: t[k] for k in ("name", "decided_by", "necessary", "sufficient", "factors")} for t in meta["open_terms"]],
    "reading_sets": set_rows,
    "reading_set_count": len(set_rows),
    "reading_set_candidates": sum(len(s["readings"]) for s in meta["reading_sets"]),
    "newly_stated_reading_sets": {"sets": len(new_sets), "candidates": sum(len(s["readings"]) for s in new_sets),
                                  "unordered_pairs": new_pairs},
    "composition_s1": {
        "content_bearing_sets_admitted": len(readings["sets"]),
        "separations_by_probe_form": readings["separations"],
        "findings": readings["findings"],
        "pairs_by_wording": dict(wordings),
        "not_certified_findings": len(not_certified),
        "pairs_without_a_situation": 0, "resource_limit_hits": 0, "single_attachment_refusal": False,
        "premises": report["premises"],
        "checked_by": readings["checked_by"],
        "timing": timing},
    "missing_feature_tally": dict(sorted(missing.items())),
    "missing_feature_tally_previous_run": old["missing_feature_tally"],
    "tool_residual": cov["residual"],
    "vocabulary_use": {"regulated_predicates": len(regulated), "regulated_limit": 64,
                       "predicates": len(vocab["predicates"]), "predicate_limit": 256,
                       "sorts": len(vocab["sorts"]), "sort_limit": 32,
                       "regulated_predicates_previous_run": old["vocabulary_use"]["regulated_predicates"]},
    "language_findings": [
        "composition S1 lifts the force blocker: a strict and a defeasible candidate of one rule now share one reading set with one checked "
        "situation per pair (the situation names the open exception's decision). Of the 43 force-blocked units 25 are now stated; the 18 "
        "others were blocked a second time, by something the single old reason had hidden (blockers.py)",
        "twins are not certified: every strict/default pair is separated only by deciding the open exception, which VE reports as "
        f"SeparatedByDecisionOnly (not certified, {readings['findings']['SeparatedByDecisionOnly']} findings): decision_only_sound is unproved, "
        "so the checked situation shows the two readings differ, not that nothing else differs",
        "readings@1 content refuses norm-defaults@0 (UnsupportedProfile) and the completion `unspecified` is refused outside it: every new "
        "predicate declares the completion 'deny' = not required, which the source does not state (no permission follows for anyone); the "
        "previous run's norm-defaults@0 companions (u017, u052, u112, u114, u035, u051, u077, u054, u111, u061, u110) could not move into the "
        "main document and keep pending candidates, so their verdicts across readings stay UNKNOWN",
        "regulated predicates: 62 of the 64 allowed (29 before); one more unit with a new act would not fit, and a document of this size "
        "cannot be split without breaking the single-document byte accounting",
        f"load time: admitting the document is one Lean call with a fixed 120 s timeout; the previous translation took 101 s for search, load and "
        f"check, this one {cov_art['load_seconds']:.0f} s to load and {ver['check_seconds']:.0f} s to check (about 15 times more), and with the tag's own limit "
        "the document is refused (CheckerUnavailable: ve_readings_route is unavailable after 120.3 s)",
        "right_lines across open sets: a right_lines candidate may name only a right its own document declares, so 'this right includes ...' "
        "after an open right set is refused (UnknownRight: freedom-of-thought-conscience-and-religion under rs_u067@1:0): the four units "
        "u067, u068, u071a, u071b stay UNFORMALISED; a fixed right_lines unit would pick one incident for all candidates",
        "limitation attached to a right: still not expressible beside right candidates (limitation scope names rights, which are open sets); "
        "u111 states its conditions over one limitation per person and right as norm candidates, not as a rights limitation",
        "act phrases: at most 80 bytes, no 'for', 'or', 'and', 'no', 'not', 'is'; seven of the 18 remaining force units fail only there "
        "(u079b, u082, u085, u086, u091, u092, u106), and 'equal pay for equal work' cannot be worded without 'for'",
        "English of the generated sentences: the paraphrase of a state-guarded rule reads 'if that bearer is classified as \"is_state\"' because "
        "the wording grammar allows one word after 'is'; the E19 situation lists one element of every sort in the document, including sorts "
        "the unit does not use",
        "force of Articles 22-27: the default candidates of the entitlement units cite 'the organization and resources of each State' "
        "(Article 22) as the exception factor; VE has narrowings that would pick the default reading, and this run does not apply one "
        "(a translator keeping all readings), so strict and defeasible stay open",
        "passive duties name no bearer: u025, u098, u099a, u099b, u100a, u100b are duties on a bearer read two ways (a state, or every "
        "state, group and person); where the source's passive names no age (u098) the duty is scoped by a named open relation, not by an "
        "invented age",
        "polarity budget: units that state an entitlement to a good or a protection (social security, conditions of work, protection against "
        "unemployment, a share in advancement) offer the securing duty only (the audit precedent: 'avoid denying X' is the same duty); the "
        "freedoms (work, free choice of employment, trade unions, education, participation, the arts) offer both polarities"],
    "no_invented_permissions": {
        "new_predicates": "every one of the 33 new regulated predicates is obligation-role with the declared completion 'deny' (= not required): "
                          "it grants no permission to anyone, is never consulted where a rule decides the act, and is not stated by the "
                          "source; no permission-role predicate was added",
        "scope": "the state readings are the same duty guarded by is_state: for a non-state the completion is 'not required', declared and "
                 "not derived from the source; u098's receive reading is scoped to the open relation of_age_for_elementary_education",
        "companions": "the nine repaired or unchanged norm-defaults@0 companions keep the completion 'unspecified' (witnesses: a case inside "
                      "the guard SETTLED, outside it UNDECIDED, never silently permitted); the defeasible candidates of u017 and u111 keep 'deny' on "
                      "an obligation-role predicate",
        "remaining_declared_completions_in_the_main_document": {
            "predicates": len(regulated),
            "by_role_and_completion": dict(sorted(Counter(f"{p['regulated']['role']}:{p['regulated']['default']}" for p in regulated.values()).items()))}},
    "norm_defaults": {
        "profile": "norm-defaults@0",
        "companions": {k: {"profiles": v["profiles"], "report": v["norm_defaults_report"]} for k, v in companion_docs.items()
                       if "norm-defaults@0" in v["profiles"]},
        "status_witnesses": nd_status,
        "main_document_blocked": "readings@1 content with norm-defaults@0 is not implemented (composition-s1.md 1.1); the completion "
                                 "`unspecified` is refused outside norm-defaults@0",
        "u074_migration_audit": old["norm_defaults"]["u074_migration_audit"],
        "u074_note": "carried unchanged from the previous run: u074 and its companion are untouched"},
    "presupposition_check": "No heading or speaker marker presupposes a substantive claim; the labelled units are unchanged from the audited "
                            "previous run (its audit sampled u080, u044, u014, u040 and found them faithful). u060 stays UNFORMALISED as an "
                            "evaluative claim. u045b, u099b and u100b begin with a conjunction: each carries the subject of the previous unit "
                            "(noted in its elided field), not a presupposed claim.",
    "checks": {
        "document_load": f"PASS with the Lean timeout raised in the harness ({cov_art['load_seconds']} s); REFUSED with the tag's own limits "
                         "(CheckerUnavailable at 120.3 s)",
        "byte_partition": "PASS (units partition all 10,916 bytes)",
        "document_check": "PASS", "premises": report["premises"],
        "coverage": "PASS (100% of bytes accounted)",
        "reading_sets_validated_at_load": "PASS: 39 content-bearing sets admitted, every ordered pair separated by a checked situation, "
                                          "no ResourceLimit, no single-attachment refusal",
        "companion_documents": companion_docs,
        "witnesses": "PASS: every norm-defaults@0 companion settles the case inside its guard and reports UNDECIDED outside it (witnesses.json "
                     "has the repaired ones; metrics.norm_defaults.status_witnesses all of them)",
        "render": "PASS (rendered.md, readings-rendered.md)"},
    "document_id": report["document_id"], "source_id": report["source_id"], "coverage_tool": cov,
}
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n")
(HERE / "witnesses.json").write_text(json.dumps({"norm_defaults_status": nd_status}, ensure_ascii=False, indent=2,
                                                sort_keys=True) + "\n")
print(json.dumps({k: metrics[k] for k in ("unit_counts_by_status", "bytes_by_status", "claimed_covered_bytes",
                                            "claimed_covered_percent", "audit_verified_covered_bytes",
                                            "audit_verified_covered_percent", "old_boundary_aggregation",
                                            "missing_feature_tally", "newly_covered_bytes", "vocabulary_use")}, indent=1))
