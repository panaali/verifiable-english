#!/usr/bin/env python3
"""Run 20261008T1800Z: re-run VE at ve-green-lf-15b, write the ledger, renderings and metrics.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; lake build in lean/ and tools/rust_build.py done):
    uv run python usecases/claude-constitution-pilot/run-20261008T1800Z/reword.py     # once: two act wordings, availability repair
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python .../probe_$p.py; done
    for g in force op s1 s01p1 all; do uv run python .../nd.py $g; done              # the checked-content documents (about 12 min)
    uv run python -m ve document coverage|render .../readings/nd-<g>.ve.md            # into coverage-nd-<g>.json, rendered-nd-<g>.md
    uv run python -m ve document readings .../readings/nd-force.ve.md --conclusion .../probes/nd/conclusion-no-denial.json [--under force-u0125-s04-p2:0|1]
    uv run python .../finish.py

The translation is the previous run's (prev/), unchanged except the two act wordings of reword.py; the ledger gains notes on eight units and
no status changes (asserted below). finish_0600.py (constants and renderers) is reused.
"""
from __future__ import annotations

import copy
import difflib
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))
import finish_0600 as old  # noqa: E402

RUN_ID = "20261008T1800Z"
PREV_RUN = "20261008T0600Z"
TAG = "ve-green-lf-15b"
PREV_TAG = "ve-green-rd-6a"
COVERED = old.COVERED
SOURCE = old.SOURCE
ve, front_matter = old.ve, old.front_matter
dump = lambda p, o: (RUN / p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")
PREV_DIR = Path("/home/seyran/code/manage-agents/pilots/claude-constitution") / f"run-{PREV_RUN}"
DOCS = {"main": RUN / "translation.ve.md", "strict": RUN / "readings/all-strict.ve.md", "default": RUN / "readings/all-default.ve.md"}
SETS = {  # unit -> (set, document of this run that carries checked content for every candidate of the set)
    "u0036.s05": ("force-u0036-s05", "nd-force"), "u0125.s04.p2": ("force-u0125-s04-p2", "nd-force"),
    "u0156.s03": ("force-u0156-s03", "nd-force"), "u0263.s04.p2": ("force-u0263-s04-p2", "nd-force"),
    "u0062.s01": ("modal-u0062-s01", "nd-op"), "u0123.s02.p1": ("modal-u0123-s02-p1", "nd-op"),
    "u0123.s03": ("scope-modal-u0123-s03", "nd-op"), "u0123.s01.p1": ("modal-u0123-s01-p1", "nd-s01p1")}
NOTE = ("Run 20261008T1800Z (ve-green-lf-15b, readings-defaults RD-2b): every candidate of this unit's reading set now carries content that Lean checked on the "
        "main chain itself (norm-defaults@0, completion unspecified, no `deny`) in readings/{doc}.ve.md, one compatible choice at a time; the translation proper "
        "keeps the set without content, because the eight sets together have 1,152 choices and the enumerated route stops at 64.")
WORDING_UNITS = ["u0073.s05", "u0156.s03"]  # units whose predicate's act wording was changed by reword.py


def main():
    prev = json.load(open(RUN / "prev/units.json"))
    ledger = json.load(open(RUN / "units.json"))
    prev_metrics = json.load(open(RUN / "prev/metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == prev_metrics["source_sha256"]
    for e in ledger:  # idempotent: a re-run starts from the ledger this script wrote
        if "checked_content" in e:
            del e["checked_content"]
            e["note"] = e["note"][:e["note"].index(" Run 20261008T1800Z (ve-green-lf-15b")]
    assert ledger == prev
    assert (RUN / "prev/translation.ve.md").read_bytes() != DOCS["main"].read_bytes()  # only the two act wordings differ (reword.py)
    prev_main = front_matter(RUN / "prev/translation.ve.md")
    main_meta = front_matter(DOCS["main"])
    dv = old.__dict__.get("differing_paths")
    for k in ("units", "open_terms", "reading_sets", "narrowings", "graph", "format"):
        if k == "reading_sets":
            assert [(r["id"], r["unit"], [x["id"] for x in r["readings"]]) for r in main_meta[k]] == [(r["id"], r["unit"], [x["id"] for x in r["readings"]]) for r in prev_main[k]]
        else:
            assert main_meta[k] == prev_main[k], k
    assert {k: v for k, v in main_meta["environment"]["vocabulary"]["predicates"].items() if k not in ("system_prompt_compliance_required", "system_prompt_deception_permitted")} == \
           {k: v for k, v in prev_main["environment"]["vocabulary"]["predicates"].items() if k not in ("system_prompt_compliance_required", "system_prompt_deception_permitted")}

    # ---- VE runs at this tag
    results = {}
    for key, path in DOCS.items():
        rel = str(path.relative_to(ROOT))
        r = {"check": json.loads(ve("document", "check", rel)), "coverage": json.loads(ve("document", "coverage", rel))}
        try:
            r["render"] = ve("document", "render", rel)
        except SystemExit as exc:
            r["render"] = None
            r["render_error"] = str(exc).strip().splitlines()[-1]
        results[key] = r
    prev_check = {"main": json.load(open(PREV_DIR / "check.json")), "strict": json.load(open(PREV_DIR / "readings/check-all-strict.json")),
                  "default": json.load(open(PREV_DIR / "readings/check-all-default.json"))}
    for k in prev_check:
        assert results[k]["check"]["premises"]["status"] == prev_check[k]["premises"]["status"], k
    dump("check.json", results["main"]["check"])
    dump("coverage.json", results["main"]["coverage"])
    dump("readings/check-all-strict.json", results["strict"]["check"])
    dump("readings/check-all-default.json", results["default"]["check"])
    dump("environment.json", main_meta["environment"])
    soft_meta = front_matter(DOCS["default"])
    dump("readings/environment-all-default.json", soft_meta["environment"])
    changed_render_lines = {}
    lines = lambda text: [d for d in difflib.unified_diff(*text, lineterm="", n=0) if d[:1] in "+-" and d[:3] not in ("+++", "---")]
    (RUN / "readings/rendered-all-strict.md").write_text(results["strict"]["render"])
    changed_render_lines["strict"] = len(lines(((PREV_DIR / "readings/rendered-all-strict.md").read_text().splitlines(), results["strict"]["render"].splitlines())))
    if results["default"]["render"] is not None:
        (RUN / "readings/rendered-all-default.md").write_text(results["default"]["render"])
        changed_render_lines["default"] = len(lines(((PREV_DIR / "readings/rendered-all-default.md").read_text().splitlines(), results["default"]["render"].splitlines())))
    else:
        changed_render_lines["default"] = "not rendered: " + results["default"]["render_error"]
    rendered = old.annotate_hard(old.expand_main(results["main"]["render"], main_meta, ledger), ledger)
    changed_render_lines["main_expanded"] = len(lines(((PREV_DIR / "rendered.md").read_text().splitlines(), rendered.splitlines())))
    changed_render_lines["main_raw"] = len(lines(((PREV_DIR / "rendered-raw.md").read_text().splitlines(), results["main"]["render"].splitlines())))
    (RUN / "rendered.md").write_text(rendered)
    (RUN / "rendered-raw.md").write_text(results["main"]["render"])

    # ---- ledger: notes on the eight units, no status change
    by_id = {e["id"]: e for e in ledger}
    for unit, (set_id, doc) in SETS.items():
        e = by_id[unit]
        assert e["status"] == "READINGS"
        e["checked_content"] = {"set": set_id, "document": f"readings/{doc}.ve.md"}
        e["note"] = e["note"] + " " + NOTE.format(doc=doc)
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE)
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    assert [(u["id"], tuple(u["span"])) for u in main_meta["units"]] == [(e["id"], tuple(e["span"])) for e in ledger]
    u, nb = old.counts(ledger)
    claimed = sum(v for k, v in nb.items() if k in COVERED)
    assert claimed == prev_metrics["claimed_covered_bytes"]
    n_old, old_units, _ = old.aggregate(ledger)
    spans = {e["id"]: e["span"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)

    # ---- audit-verified bytes: unchanged units; the two reworded predicates make u0073.s05's rendered rule differ from the form the audit saw
    verified = list(prev_metrics["audit_verified_covered_units"])
    dropped = [i for i in verified if i in WORDING_UNITS]
    verified_now = [i for i in verified if i not in dropped]
    sub_bytes, sub_bytes_lenient = width(verified_now), width(verified)
    assert sub_bytes_lenient == prev_metrics["audit_verified_covered_bytes"]

    # ---- the checked-content documents
    nd = {}
    for g in ("force", "op", "s01p1", "all"):
        r = json.load(open(RUN / f"readings/nd-{g}-result.json"))
        cov = json.load(open(RUN / f"readings/coverage-nd-{g}.json"))
        rd, pr = r["readings"], r["premises"]
        nd[g] = {"document": f"readings/nd-{g}.ve.md", "admitted": r["admitted"], "load_seconds": r.get("load_seconds"), "check_seconds": r.get("check_seconds"),
                 "separation_search_seconds": r["search_seconds"], "sets": [{"set": s["set"], "unit": s["unit"], "candidates": s["candidates"]} for s in r["sets"]],
                 "route": rd["route"], "choice_count": rd.get("choice_count"), "choices_checked": rd.get("choices_checked"),
                 "conflict": rd["conflict"]["status"], "conflict_text": rd["status"], "premises": pr["status"],
                 "premises_by_choice": dict(Counter(c["status"] for c in pr.get("choices", []))),
                 "premises_by_candidate": {f"{c['set']}:{c['index']}": c["status"] for c in pr.get("candidates", [])},
                 "separations": rd["separations"], "findings": rd["findings"], "pending_candidates": rd["pending_candidates"], "dead_readings": rd["dead_readings"],
                 "not_superposable": rd.get("not_superposable"), "pairs_without_situation": r["pairs_without_situation"],
                 "residual": cov["residual"], "bytes_by_status": cov["bytes_by_status"]}
    concl = {}
    for name, f in (("across_all_readings", "conclusion-no-denial-result.json"), ("under_strict", "conclusion-no-denial-under-0.json"),
                    ("under_defeasible", "conclusion-no-denial-under-1.json")):
        c = json.load(open(RUN / "probes/nd" / f))
        concl[name] = {k: c[k] for k in ("verdict", "route", "evidence", "assumed") if k in c}
    sets_total = sum(len(v["sets"]) for g, v in nd.items() if g != "all")
    cands_total = sum(len(s["candidates"]) for g, v in nd.items() if g != "all" for s in v["sets"])
    cand_status = Counter(st for g, v in nd.items() if g != "all" for st in v["premises_by_candidate"].values())
    choices_total = sum(v["choice_count"] for g, v in nd.items() if g != "all")
    sep_total = sum(sum(v["separations"].values()) for g, v in nd.items() if g != "all")
    assert sep_total == sum(nd["all"]["separations"].values())
    product = 1
    for s in nd["all"]["sets"]:
        product *= len(s["candidates"])
    assert product == 1152

    s1_probe = json.load(open(RUN / "probes/s1-probe.json"))
    unspec = json.load(open(RUN / "probes/unspecified-probe.json"))
    senses_doc = json.load(open(RUN / "probes/senses-document-probe.json"))
    points = unspec["points"]
    profile_probe = old.probe_profiles()
    s1_now = json.load(open(RUN / "readings/check-s1-now.json"))

    cv = copy.deepcopy(prev_metrics["check_verdicts"])
    doc_cov = results["main"]["coverage"]
    cv["main"].update({"coverage_percent": doc_cov["coverage_percent"], "premises": results["main"]["check"]["premises"],
                       "reading_plan": results["main"]["check"]["reading_plan"], "residual": doc_cov["residual"],
                       "identical_to_previous_run": False,
                       "verdict_differences_from_previous_run": "ids only (the vocabulary's two act wordings changed); premises, reading plan, residual, gaps equal"})
    cv["all_strict"].update({"premises": results["strict"]["check"]["premises"], "residual": results["strict"]["coverage"]["residual"],
                             "bytes_by_status": results["strict"]["coverage"]["bytes_by_status"]})
    cv["all_default"].update({"premises": results["default"]["check"]["premises"], "residual": results["default"]["coverage"]["residual"],
                              "bytes_by_status": results["default"]["coverage"]["bytes_by_status"],
                              "render": results["default"].get("render_error", "rendered")})
    cv["s1"] = {"status": "CheckerUnavailable", "message": s1_now["error"]["message"],
                "files_at_previous_tag": "readings/at-rd-6a/ (check-s1.json, coverage-s1.json, rendered-s1.md, s1-result.json, separating-situations.json)",
                "why": "readings/s1.ve.md (the soft-chain demonstration companion) holds the two act wordings with an apostrophe; Lean's English reader refuses them (V3, one sentence). "
                       "reword.py repairs the main, strict and default documents; the s1 companion is not rebuilt, because the documents of readings/nd-*.ve.md replace it on the main chain"}

    m = copy.deepcopy(prev_metrics)
    m.update({
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "previous_runs_note": "run 20261008T0600Z is the previous run's own output (manage-agents/pilots/claude-constitution/run-20261008T0600Z)",
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": old.full(u), "bytes_by_status": old.full(nb),
                                  "previous_run": {k: prev_metrics["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units, "bytes_by_substatus": old.full(nb),
                                              "previous_run": {k: prev_metrics["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")}},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": prev_metrics["claimed_covered_bytes"], "claimed_covered_bytes_gained": 0,
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"], "substantive_covered_bytes_previous_run": prev_metrics["substantive_covered_bytes"],
        "audit_verified_covered_bytes": sub_bytes, "audit_verified_covered_percent": round(100 * sub_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified_now,
        "audit_verified_covered_bytes_previous_run": prev_metrics["audit_verified_covered_bytes"],
        "audit_verified_covered_bytes_if_justification_only_edits_are_ignored": sub_bytes_lenient,
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run to the form that audit saw. No audit has seen a form of this "
            "run. No unit was edited. The one vocabulary change (reword.py: the act wordings of system_prompt_compliance_required and system_prompt_deception_permitted lose an "
            f"apostrophe, because Lean's English reader refused them at ve-green-lf-15b) changes the English of u0073.s05, which an audit had accepted, so it is dropped from the "
            f"verified set until re-audited ({sub_bytes} bytes; {sub_bytes_lenient} if the wording-only change were ignored). The five units changed in run 20261008T0600Z are "
            "still waiting for re-audit. The new checked-content documents are not audited and add nothing here."),
        "audit_verified_dropped_because_changed_or_rejected": {**prev_metrics["audit_verified_dropped_because_changed_or_rejected"],
                                                               "dropped_in_20261008T1800Z_wording_only": dropped},
        "claimed_but_not_audit_verified_bytes": claimed - sub_bytes - prev_metrics["audit_verified_metadata_bytes"],
        "document_profiles": {k: front_matter(v)["environment"]["profiles"] for k, v in DOCS.items()},
        "documents": {**prev_metrics["documents"], "s1": "readings/s1.ve.md (kept; CheckerUnavailable at this tag)",
                      "checked_content": {g: f"readings/nd-{g}.ve.md" for g in nd}},
        "open_terms": [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")} for t in main_meta["open_terms"]],
        "open_terms_count": len(main_meta["open_terms"]), "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "reading_sets": {**prev_metrics["reading_sets"], "count_previous_run": prev_metrics["reading_sets"]["count"]},
        "missing_feature_tally": old.tally(ledger), "missing_feature_tally_previous_run": prev_metrics["missing_feature_tally"],
        "check_verdicts": cv,
        "unspecified_probe": {**prev_metrics["unspecified_probe"], "points_asked": len(points), "undecided": sum(1 for p in points if p["status"] == "UNDECIDED"),
                              "settled": sum(1 for p in points if p["status"].startswith("SETTLED")),
                              "conflict": sum(1 for p in points if p["status"].startswith("CONFLICT")), "conflict_reports": unspec["conflict"],
                              "gaps": {p: g["reached"] for p, g in unspec["gaps"].items()}, "identical_to_previous_run": True},
        "profile_combination_probe": profile_probe,
        "profile_combination_probe_same_as_previous_run": profile_probe == prev_metrics["profile_combination_probe"],
        "renderings_identical_to_previous_run": {k: v == 0 for k, v in changed_render_lines.items() if isinstance(v, int)} | {"changed_lines": changed_render_lines},
        "senses_probe": {**prev_metrics["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": True},
        "senses_document_probe": {**prev_metrics["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": True},
        "s1": {**prev_metrics["s1"], "status_at_this_tag": "CheckerUnavailable (V3, see check_verdicts.s1); the figures below are those of run 20261008T0600Z at ve-green-rd-6a"},
        "s2a": {**prev_metrics["s2a"], "re_run_at_this_tag": False, "note": "the soft-chain companion cannot be checked at this tag; the same three queries were run on the main-chain document readings/nd-force.ve.md (checked_content_main_chain.conclusion_probe)"},
        "readings_defaults_probe": {**prev_metrics["readings_defaults_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": False,
                                    "outcome": {"a_main_with_readings@1": "accepted; premises UNKNOWN (no set carries content)",
                                                "b_main_with_one_strict_norm_candidate": "ACCEPTED at this tag (premises UNKNOWN: the other sets are pending) - at ve-green-rd-6a it was refused by name",
                                                "c_s1_document_with_norm_defaults@0": s1_probe["c_s1_document_with_norm_defaults@0"]["rejection"]},
                                    "why": "RD-2b relays Lean's answer for content-bearing sets under the completion; the soft chain (soft-norms@0, defeasible rules) is still not joined with norm-defaults@0"},
        "lean_decided_share": {"decided_bytes": 0, "decided_share_percent": "0.00", "script": "tools/lean_decided_share.py",
                               "meaning": "units whose every verdict is a Lean answer that is not UNKNOWN across readings. Still 0.00%: the script needs a `readings-verdicts` answer (RD-3), which no route emits; the checked-content "
                                          "documents are decided choice by choice (checked_content_main_chain) but not reported as decided units"},
        "checked_content_main_chain": {
            "what": "reading sets whose every candidate carries content that Lean checked on the main chain itself (norm-defaults@0, completion unspecified): readings@1 beside norm-defaults@0 (readings-defaults RD-2a/RD-2b)",
            "script": "nd.py", "documents": nd,
            "reading_sets_with_checked_content": sets_total, "reading_sets_total": len(main_meta["reading_sets"]),
            "candidates_with_content": cands_total, "candidates_total": cands_total,
            "candidate_premise_status": dict(cand_status), "choices_checked_one_at_a_time": choices_total,
            "choices_conflict_free": choices_total, "choices_conflict": 0, "separating_situations_checked_by_lean": sep_total,
            "separated_by_decision_only_findings": 0,
            "all_eight_in_one_document": {"admitted": nd["all"]["admitted"], "choices": product, "budget": 64, "verdict": nd["all"]["conflict_text"], "separations": nd["all"]["separations"]},
            "split": {"nd-force": [s["unit"] for s in nd["force"]["sets"]], "nd-op": [s["unit"] for s in nd["op"]["sets"]], "nd-s01p1": [s["unit"] for s in nd["s01p1"]["sets"]]},
            "conclusion_probe": {"query": "every instance of Claude is not permitted to directly deny being Claude (denial_of_being_claude_permitted)", "results": concl},
            "defeasible_candidates": "the soft chain's `exception: unstated` becomes one base predicate per set that is an open term (exception_to_*), used as an `unless`; the text names no exception",
            "not_representable": [
                "the permission candidates of u0062.s01 and u0123.s02.p1 are limited by whatever u0123.s03 forbids 'under that sentence's own reading': one content cannot depend on another set's choice, so they carry the narrow-limits form (the one of readings/all-strict.ve.md); pairing them with the wide reading of u0123.s03 is allowed by the enumerated route and VE says CONFLICT-FREE, which is true of those rules but is not a statement about the wide reading of the text",
                "defeasibility beside norm-defaults@0 as VE's own mode: probe c still refuses norm-defaults@0 with soft-norms@0 ('await the Lean route')",
                "more than 64 choices in one document (the split by companions, RD-4a, is not merged)"],
            "premises_unknown": {"candidates": [k for k, v in nd['op']['premises_by_candidate'].items() if v != 'model'],
                                 "why": "the two ability candidates are existence claims (some operator can supply some input of the kinds); the model search finds no model for them within its limits"}},
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "unchanged_entries": len(ledger) - len(SETS),
            "changed_or_replaced_ids": sorted(SETS), "added_ids": [], "units_newly_covered": [], "units_with_status_change": [],
            "units_changed_by_note_only": sorted(SETS),
            "reason": "no status changed: the eight READINGS units keep their translation; each now has a document in which Lean checks the content of every candidate (checked_content_main_chain). "
                      "The vocabulary's two act wordings changed (reword.py)."},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {
                "english-lean-e2 (e2)": "Lean's English reader takes over admission/rendering; it refuses a predicate wording that is not one sentence (V3). Availability regression for this pilot: render of the previous run's documents answered CheckerUnavailable until the two act wordings lost an apostrophe (reword.py)",
                "lean-first/b15a (lf-15a), b16a (lf-16a), b15b (lf-15b)": "Lean-first: search, evaluate, document steps and Rust's source parser/printer move or are deleted; no new form of text. lf-15b: `ve.search` and `ve.evaluate` read Lean's answers; Rust no longer reads source text",
                "readings-defaults/rd2a (rd-2a)": "Lean: admission, separation and choices of a content-bearing readings@1 set under norm-defaults@0 (the unspecified completion): fill_premises, filled document, elaborate/choice runners",
                "readings-defaults/rd2b (rd-2b)": "relay and generators under the completion: a `readings@1` document with content under `norm-defaults@0` now loads, checks, renders and answers queries across readings (enumerated route, at most 64 choices, evidence per choice from Lean); the S1 generator reads Lean's filled document"},
            "newly_expressible_features": 1,
            "newly_expressible": "readings@1 content-bearing reading sets beside norm-defaults@0 (the top blocker F1 of the previous runs)",
            "units_upgraded_by_new_features": 0,
            "reading_sets_upgraded_by_new_features": sets_total,
            "why_no_unit_changed_status": "the eight units are READINGS before and after; what changed is that every candidate of every set now has Lean-checked content on the main chain (CONFLICT-FREE under all 43 choices, 17 separations). A status ladder with 'READINGS, content checked' would count them"},
        "reading_set_gaps": [
            {"gap": "more than 64 choices in one document: the eight sets have 1,152 together; the enumerated route answers UNKNOWN beyond 64", "feature": "other:companion-split (RD-4a, not merged)",
             "workaround": "three documents (nd-force 16 choices, nd-op 24, nd-s01p1 3)"},
            {"gap": "a candidate whose content depends on the reading chosen in another set (u0062.s01, u0123.s02.p1 are limited by u0123.s03 'under its own reading')", "feature": "other:cross-set-dependence",
             "workaround": "the narrow-limits form is the one content; couplings tie labels, not contents"},
            {"gap": "a defeasible rule beside norm-defaults@0 (soft-norms@0 with norm-defaults@0 is refused, probe c)", "feature": "defaults",
             "workaround": "one named exception predicate per set, used as an `unless` (an open term)"},
            {"gap": "the folded verdicts and decided units are Python's fold over Lean's per-choice evidence; `readings-verdicts` (RD-3) is not built", "feature": "other:RD-3", "workaround": "none needed for the per-choice results"},
            {"gap": "Lean's English reader refuses an act wording with an apostrophe (V3); render of the previous run's documents was CheckerUnavailable", "feature": "other:english-lexicon-v3", "workaround": "reword.py"},
            {"gap": "render of the soft-chain companion all-default.ve.md fails: InvalidInput: invalid soft name soft__excepted__clarify_ambiguity (check still runs)", "feature": "other:soft-chain-render", "workaround": "none; the file is not rendered at this tag"}],
        "carried_probes_note": "all seven carried probes re-run at this tag; six byte-identical to the previous run's; the S1 probe's case b changed (accepted now)",
    })
    dump("metrics.json", m)
    dump("units.json", ledger)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent", "claimed_but_not_audit_verified_bytes")}))
    print(dict(u), dict(nb))
    print("render lines changed:", changed_render_lines)
    print("profile probe same:", m["profile_combination_probe_same_as_previous_run"])


if __name__ == "__main__":
    main()
