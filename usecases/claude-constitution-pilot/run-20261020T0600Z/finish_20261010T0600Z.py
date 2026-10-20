#!/usr/bin/env python3
"""Run 20261010T0600Z: re-run VE at ve-green-lf-16c, write the ledger, renderings and metrics.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python usecases/claude-constitution-pilot/run-20261010T0600Z/repair_20261010T0600Z.py   # base/ + prev/ -> translation-without-content.ve.md, units.json
    uv run python .../nd.py all                          # readings/nd-all.ve.md becomes translation.ve.md; about 2 min
    cp readings/nd-all.ve.md translation.ve.md && rm readings/nd-all.ve.md
    uv run python -m ve document coverage translation.ve.md > readings/coverage-nd-all.json
    probes (README.md), conclusion queries (probes/nd/, README.md)
    uv run python .../finish_20261010T0600Z.py            # about 3 min

The translation is the previous run's (20261009T1800Z), with the five units its audit rejected repaired (AUDIT-REPAIR.md): the four operator
units lose their wide candidate and stop being reading sets (OPEN, one reading), u0166.s04.p4 keeps UNFORMALISED with a corrected note.
No unit gains a covered status from a new feature.
"""
from __future__ import annotations

import copy
import difflib
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))
import finish_0600 as old  # noqa: E402

RUN_ID = "20261010T0600Z"
PREV_RUN = "20261009T1800Z"
TAG = "ve-green-lf-16c"
PREV_TAG = "ve-green-rd-3"
COVERED = old.COVERED
SOURCE = old.SOURCE
ve, front_matter = old.ve, old.front_matter
dump = lambda p, o: (RUN / p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")
PREV_DIR = RUN / "prev"   # the previous run's outputs, copied (the run directory itself is not in this branch)
MAIN = RUN / "translation.ve.md"
STRICT = RUN / "readings/all-strict.ve.md"
SETS = {  # unit -> its reading set (the translation itself carries the sets)
    "u0036.s05": "force-u0036-s05", "u0125.s04.p2": "force-u0125-s04-p2",
    "u0156.s03": "force-u0156-s03", "u0263.s04.p2": "force-u0263-s04-p2"}
OPSETS = ["modal-u0062-s01", "modal-u0123-s01-p1", "modal-u0123-s02-p1", "scope-modal-u0123-s03"]   # the previous run's operator sets: gone
FORCE_UNITS = ["u0036.s05", "u0125.s04.p2", "u0156.s03", "u0263.s04.p2"]
OP_UNITS = ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03"]
# the audit of run 20261009T1800Z (18/20 sampled + 1/6 changed): verdicts as received (AUDIT-20261009T1800Z-received.md)
AUDIT_REJECTED_1800 = ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03", "u0166.s04.p4"]
AUDIT_FAITHFUL_1800 = ["u0036.s05", "u0040.heading", "u0042.heading", "u0073.s05", "u0075.heading", "u0125.s04.p2", "u0126", "u0156.s03",
                       "u0165.s02", "u0165.s03", "u0165.s04", "u0165.s05", "u0165.s06", "u0168.s01", "u0212.heading", "u0248",
                       "u0254.heading", "u0263.s04.p2", "u0286.heading"]
# the changed units: the five the audit rejected (the fourth operator unit, u0123.s02.p1, was one of them)
CHANGED = sorted(AUDIT_REJECTED_1800)
WIDE = "instruction_is_for_behaviour_while_role_playing_persona"


def slice_result(g):
    r = json.load(open(RUN / f"readings/nd-{g}-result.json"))
    cov = json.load(open(RUN / f"readings/coverage-nd-{g}.json"))
    rd, pr = r["readings"], r["premises"]
    return {"document": f"readings/nd-{g}.ve.md" if g != "all" else "translation.ve.md", "admitted": r["admitted"], "load_seconds": r.get("load_seconds"),
            "check_seconds": r.get("check_seconds"), "separation_search_seconds": r["search_seconds"],
            "sets": [{"set": s["set"], "unit": s["unit"], "candidates": s["candidates"]} for s in r["sets"]],
            "route": rd["route"], "choice_count": rd.get("choice_count"), "choices_checked": rd.get("choices_checked"),
            "couplings": rd.get("couplings"), "conflict": rd["conflict"]["status"], "conflict_text": rd["status"], "premises": pr["status"],
            "premises_by_choice": dict(Counter(c["status"] for c in pr.get("choices", []))),
            "premises_by_candidate": {f"{c['set']}:{c['index']}": c["status"] for c in pr.get("candidates", [])},
            "separations": rd["separations"], "findings": rd["findings"], "pending_candidates": rd["pending_candidates"], "dead_readings": rd["dead_readings"],
            "not_superposable": rd.get("not_superposable"), "pairs_without_situation": r["pairs_without_situation"],
            "residual": cov["residual"], "bytes_by_status": cov["bytes_by_status"]}


def concl(names):
    out = {}
    for name, f in names:
        c = json.load(open(RUN / "probes/nd" / f))
        out[name] = {k: c[k] for k in ("verdict", "route", "evidence", "assumed") if k in c}
    return out


def front_set(meta, set_id):
    return next(s for s in meta["reading_sets"] if s["id"] == set_id)


def main():
    prev = json.load(open(RUN / "prev/units.json"))
    ledger = json.load(open(RUN / "units.json"))   # written by repair_20261010T0600Z.py
    prev_metrics = json.load(open(RUN / "prev/metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == prev_metrics["source_sha256"]
    by_prev = {e["id"]: e for e in prev}
    by_id = {e["id"]: e for e in ledger}
    changed_entries = sorted(e["id"] for e in ledger if e != by_prev[e["id"]])
    assert changed_entries == CHANGED, changed_entries
    assert by_id["u0166.s04.p4"]["status"] == "UNFORMALISED" and by_id["u0166.s04.p4"]["missing_feature"] == "modality/belief"
    prev_main = front_matter(PREV_DIR / "translation.ve.md")
    main_meta = front_matter(MAIN)
    assert [(u["id"], tuple(u["span"])) for u in main_meta["units"]] == [(e["id"], tuple(e["span"])) for e in ledger]
    prev_units = {u["id"]: u for u in prev_main["units"]}
    unit_diff = sorted(u["id"] for u in main_meta["units"] if u != prev_units[u["id"]])
    assert unit_diff == sorted(OP_UNITS), unit_diff   # the four operator units gain their content; u0166.s04.p4 was unformalised in the document already
    pv = prev_main["environment"]["vocabulary"]["predicates"]
    nv = main_meta["environment"]["vocabulary"]["predicates"]
    pred_gone = sorted(k for k in pv if k not in nv)
    pred_new = sorted(k for k in nv if k not in pv)
    assert pred_gone == [WIDE], pred_gone
    assert pred_new == [], pred_new
    assert {k: v for k, v in nv.items() if k in pv} == {k: v for k, v in pv.items() if k in nv}
    # the force sets are exactly as the audit of 20261009T1800Z saw them; the operator sets are gone
    prev_sets = {s["id"]: s for s in prev_main["reading_sets"]}
    def set_form(item):   # what a reader sees of a set; the identifiers (meaning ids, situation keys) change with the environment's, which lost two relations
        return {k: ([{kk: vv for kk, vv in r.items() if kk not in ("meaning_id", "admission")} | {"why": r["admission"]["why"], "who": r["admission"]["who"]}
                     for r in v] if k == "readings" else v) for k, v in item.items() if k not in ("situations", "models")}
    same_set = {i: set_form(front_set(main_meta, SETS[i])) == set_form(prev_sets[SETS[i]]) for i in SETS}
    assert all(same_set[i] for i in FORCE_UNITS), same_set
    assert [s["id"] for s in main_meta["reading_sets"]] == sorted(SETS.values()) and not main_meta.get("couplings")
    assert not any(s in OPSETS for s in (x["id"] for x in main_meta["reading_sets"]))

    # ---- VE runs at this tag
    rel = str(MAIN.relative_to(ROOT))
    check = json.loads(ve("document", "check", rel))
    coverage = json.loads(ve("document", "coverage", rel))
    render = ve("document", "render", rel)
    strict = {"check": json.loads(ve("document", "check", str(STRICT.relative_to(ROOT)))),
              "coverage": json.loads(ve("document", "coverage", str(STRICT.relative_to(ROOT))))}
    dump("check.json", check)
    dump("coverage.json", coverage)
    dump("environment.json", main_meta["environment"])
    dump("readings/check-all-strict.json", strict["check"])
    (RUN / "readings/rendered-all-strict.md").write_text(ve("document", "render", str(STRICT.relative_to(ROOT))))
    lines = lambda a, b: [d for d in difflib.unified_diff(a, b, lineterm="", n=0) if d[:1] in "+-" and d[:3] not in ("+++", "---")]
    rendered = old.annotate_hard(render, ledger)
    changed_render = {"raw": len(lines((PREV_DIR / "rendered-raw.md").read_text().splitlines(), render.splitlines()))}
    (RUN / "rendered.md").write_text(rendered)
    (RUN / "rendered-raw.md").write_text(render)
    assert check["premises"]["status"] == "model", check["premises"]
    assert check["reading_plan"]["route"] == "enumerate" and len(check["reading_plan"]["choices"]) == 16
    prev_check = json.load(open(PREV_DIR / "check.json"))

    def same_except(a, b, skip):
        return all(a.get(k) == b.get(k) for k in set(a) | set(b) if k not in skip)

    check_same_as_previous = same_except(check, prev_check, {"coverage", "residual", "readings"})

    # ---- ledger: the notes of the changed units were written by repair_20261010T0600Z.py; nothing is appended here
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE)
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    u, nb = old.counts(ledger)
    claimed = sum(v for k, v in nb.items() if k in COVERED)
    assert claimed == prev_metrics["claimed_covered_bytes"], claimed   # READINGS -> OPEN keeps the claimed bytes; u0166.s04.p4 stays UNFORMALISED
    n_old, old_units, _ = old.aggregate(ledger)
    spans = {e["id"]: e["span"] for e in ledger}
    status = {e["id"]: e["status"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)

    # ---- audit-verified bytes: accepted by an audit AND byte-identical in this run to the form it saw
    prev_verified = list(prev_metrics["audit_verified_covered_units"])
    assert not [i for i in prev_verified if i in AUDIT_REJECTED_1800]
    keep = list(prev_verified)
    for i in keep:   # unchanged since the audit that accepted them
        assert by_id[i] == by_prev[i] and i not in unit_diff, i
    faithful_sub = [i for i in AUDIT_FAITHFUL_1800 if status[i] in COVERED and status[i] != "LABELLED"]
    faithful_lab = [i for i in AUDIT_FAITHFUL_1800 if status[i] == "LABELLED"]
    # accepted by the 20261009T1800Z audit in the form it saw; byte-identical here (ledger entry, document unit, and for a set the whole set)
    newly = [i for i in faithful_sub if i not in keep]
    for i in newly:
        assert by_id[i] == by_prev[i] and i not in unit_diff and (i not in SETS or same_set[i]), i
    assert sorted(newly) == ["u0036.s05", "u0165.s03"], newly
    verified = list(dict.fromkeys(keep + newly))
    assert all(by_id[i]["status"] in COVERED for i in verified)
    verified_bytes = width(verified)
    verified_before = prev_metrics["audit_verified_covered_bytes"]
    assert verified_bytes == verified_before + width(newly), (verified_bytes, verified_before)
    cand_lab = list(dict.fromkeys(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED + ["u0212.heading"]))
    verified_lab_before = [i for i in cand_lab if i in by_id and status[i] == "LABELLED"]
    assert width(verified_lab_before) == prev_metrics["audit_verified_metadata_bytes"], width(verified_lab_before)
    newly_lab = [i for i in faithful_lab if i not in verified_lab_before]
    verified_lab = verified_lab_before + newly_lab
    verified_meta = width(verified_lab)
    repaired_bytes = width(CHANGED)

    nd = {"all": slice_result("all")}
    assert nd["all"]["conflict"] == "CONFLICT-FREE" and nd["all"]["premises"] == "model" and nd["all"]["choice_count"] == 16
    sep_all = sum(nd["all"]["separations"].values())
    cand_status = Counter(nd["all"]["premises_by_candidate"].values())

    concl_force = concl((("across_all_readings", "conclusion-no-denial-result.json"), ("under_strict", "conclusion-no-denial-under-0.json"),
                         ("under_defeasible", "conclusion-no-denial-under-1.json")))
    concl_op = concl((("across_all_readings", "claim-human-result.json"),))
    assert concl_op["across_all_readings"]["verdict"] == "ALL", concl_op
    prev_cc = prev_metrics["checked_content_main_chain"]
    prev_force_results = {k: v for k, v in prev_cc["conclusion_probe"]["results"].items() if k != "across_all_readings_in_the_translation"}
    concl_force_same = concl_force == prev_force_results
    concl_op_prev = prev_cc["conclusion_probe_operators"]["results"]

    unspec = json.load(open(RUN / "probes/unspecified-probe.json"))
    points = unspec["points"]
    s1_probe = json.load(open(RUN / "probes/s1-probe.json"))
    profile_probe = old.probe_profiles()
    probe_same = {name: (RUN / f"probes/{name}.json").read_bytes() == (PREV_DIR / f"probes/{name}.json").read_bytes()
                  for name in ("unspecified-probe", "risk-probe", "s1-probe", "senses-probe", "senses-document-probe", "discourse-probe",
                               "rights-reading-probe")}
    rights = json.load(open(RUN / "probes/rights-reading-probe.json"))

    cv = copy.deepcopy(prev_metrics["check_verdicts"])
    cv["main"] = {"document_loaded": True, "coverage_percent": coverage["coverage_percent"], "premises": {k: check["premises"][k] for k in ("status", "route", "evidence")},
                  "premises_by_choice": dict(Counter(c["status"] for c in check["premises"]["choices"])),
                  "reading_plan": {"route": check["reading_plan"]["route"], "choice_count": len(check["reading_plan"]["choices"]),
                                   "conditional_on": check["reading_plan"].get("conditional_on")},
                  "reading_plan_previous_run": prev_metrics["check_verdicts"]["main"]["reading_plan"],
                  "residual": coverage["residual"], "norm_defaults": check["norm_defaults"],
                  "identical_to_previous_run": False,
                  "what_changed": "same kinds of verdict (premises model in every choice, enumerated reading plan, conflict-free) over 16 choices instead of 32: "
                                  f"the four operator units are single-reading OPEN units now, not reading sets; open terms {prev_metrics['open_terms_count']} -> {len(main_meta['open_terms'])} "
                                  "(the wide-scope term is gone); the check of the unchanged previous translation at ve-green-lf-16c (check-baseline.json) gives the same verdicts as at ve-green-rd-3",
                  "verdict_fields_identical_to_previous_run": check_same_as_previous}
    cv["all_strict"].update({"premises": strict["check"]["premises"], "residual": strict["coverage"]["residual"],
                             "bytes_by_status": strict["coverage"]["bytes_by_status"]})
    m = copy.deepcopy(prev_metrics)
    open_terms = [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")} for t in main_meta["open_terms"]]
    new_terms = sorted({t["name"] for t in main_meta["open_terms"]} - {t["name"] for t in prev_main["open_terms"]})
    gone_terms = sorted({t["name"] for t in prev_main["open_terms"]} - {t["name"] for t in main_meta["open_terms"]})
    factors_changed = sorted(t["name"] for t in main_meta["open_terms"]
                             if t["name"] in {p["name"] for p in prev_main["open_terms"]}
                             and t["factors"] != next(p for p in prev_main["open_terms"] if p["name"] == t["name"])["factors"])
    m.update({
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "previous_runs_note": "run 20261009T1800Z is the previous run's own output (usecases/claude-constitution-pilot/run-20261009T1800Z on branch pilot/cc-20261009T1800Z, with its AUDIT.md); prev/ here holds the files this run starts from and compares with",
        "changed_units": CHANGED,
        "changed_units_note": {
            "u0166.s04.p4": "UNFORMALISED (modality/belief) as before; the ledger note no longer offers inability and a duty as unresolved alternatives (audit 20261009T1800Z)",
            "u0123.s03": "READINGS -> OPEN: the wide reading (the role-play phrase qualifying all six items) is not in the words; one reading, as content on the unit (audit)",
            "u0123.s01.p1": "READINGS -> OPEN: its wide candidate went with u0123.s03's; one reading, the permission scoped by the six limits (audit)",
            "u0062.s01": "READINGS -> OPEN: same (audit)",
            "u0123.s02.p1": "READINGS -> OPEN: same (audit)"},
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": old.full(u), "bytes_by_status": old.full(nb),
                                  "previous_run": {k: prev_metrics["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units, "bytes_by_substatus": old.full(nb),
                                              "previous_run": {k: prev_metrics["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")}},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": prev_metrics["claimed_covered_bytes"], "claimed_covered_bytes_gained": claimed - prev_metrics["claimed_covered_bytes"],
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"], "substantive_covered_bytes_previous_run": prev_metrics["substantive_covered_bytes"],
        "audit_verified_covered_bytes": verified_bytes, "audit_verified_covered_percent": round(100 * verified_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified, "audit_verified_covered_bytes_previous_run": verified_before,
        "audit_verified_covered_bytes_if_justification_only_edits_are_ignored": verified_bytes,
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run to the form that audit saw. The audit of run "
            "20261009T1800Z (18/20 sampled faithful, 1/6 changed units faithful) rejected u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03 and u0166.s04.p4 (none was audit-verified). "
            "It accepted u0165.s03 (repaired in that run) and u0036.s05 (carried content since 20261009T0600Z) in the form this run keeps byte for byte, so both join; "
            "u0125.s04.p2, u0156.s03, u0263.s04.p2 (whole reading sets), u0165.s02, u0165.s04 to u0165.s06, u0168.s01, u0248 and u0073.s05 were verified already. "
            "Six headings or labels it accepted (u0040.heading, u0042.heading, u0075.heading, u0126, u0254.heading, u0286.heading) were verified by earlier audits already; the metadata bytes are recomputed from the lists. "
            "Nothing this run changed is audit-verified."),
        "audit_verified_dropped_because_changed_or_rejected": {**prev_metrics["audit_verified_dropped_because_changed_or_rejected"],
                                                               "rejected_by_20261009T1800Z_audit_never_verified": AUDIT_REJECTED_1800},
        "audit_verified_newly_from_20261009T1800Z": [i for i in newly], "audit_verified_newly_label_units_from_20261009T1800Z": newly_lab,
        "audit_verified_metadata_bytes": verified_meta,
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "repaired_bytes_not_audit_verified": repaired_bytes,
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261009T1800Z_audit": AUDIT_REJECTED_1800,
            "repair_done_in_20261010T0600Z": "see AUDIT-REPAIR.md: the four operator units lose the wide reading and are single-reading OPEN units (no reading set, no coupling, no scope axis); "
                                            "u0166.s04.p4 stays UNFORMALISED (modality/belief) with a corrected note",
            "repaired_and_not_yet_sampled": AUDIT_REJECTED_1800, "earlier": prev_metrics["audit_rejected_units_and_repair_status"]},
        "document_profiles": {"main": main_meta["environment"]["profiles"], "strict": front_matter(STRICT)["environment"]["profiles"]},
        "documents": {"translation": "translation.ve.md (the previous run's, repaired; the four 'should' reading sets carry content)", "without_content": "translation-without-content.ve.md",
                      "strict": "readings/all-strict.ve.md (carried: the source of the strict content of the four 'should' sets)",
                      "slices": None,
                      "not_carried": "readings/all-default.ve.md, readings/s1.ve.md (soft-chain demonstrations; the probes that need them were run on the earlier runs' copies, then removed)"},
        "open_terms": open_terms, "open_terms_count": len(open_terms), "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "open_terms_added": new_terms, "open_terms_removed_this_run": gone_terms,
        "open_terms_with_changed_factors": factors_changed,
        "reading_sets": {"count": 4, "unresolved": 4, "count_previous_run": 8,
                         "candidates": {s.get("unit"): [r["id"] for r in s["readings"]] for s in main_meta["reading_sets"]},
                         "candidates_previous_run": prev_metrics["reading_sets"]["candidates"],
                         "units": [s["unit"] for s in main_meta["reading_sets"]], "couplings": [],
                         "narrowings": [], "choices": 16, "choices_previous_run": 32,
                         "left_as_reading_sets_by_this_run": "none; the four operator sets (u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03) became single-reading OPEN units",
                         "readings_from_the_words": {**{k: v for k, v in prev_metrics["reading_sets"]["readings_from_the_words"].items() if not k.startswith(("can_cannot", "scope_set", "checked_again"))},
                                                     "checked_again_20261010T0600Z": (
                                                         "every candidate of the four remaining sets was re-read against the words-only rule: each cites the document's own account of 'should' "
                                                         "(u0253.s04, u0011.s01) or its statement that these are almost hard constraints (u0109.s05, u0109.s06). The four operator sets are removed: the audit of "
                                                         "20261009T1800Z found that “while role-playing as a custom AI persona” qualifies the first of the six coordinated items only, so the 'wide' candidate was not in "
                                                         "the words. No outside knowledge is used."),
                                                     "removed_by_20261010T0600Z": {"u0062.s01": ["permission-wide-limits"], "u0123.s01.p1": ["permission-wide-limits"],
                                                                                   "u0123.s02.p1": ["permission-wide-limits"], "u0123.s03": ["wide-prohibition"]}}},
        "missing_feature_tally": old.tally(ledger), "missing_feature_tally_previous_run": prev_metrics["missing_feature_tally"],
        "check_verdicts": cv,
        "unspecified_probe": {**prev_metrics["unspecified_probe"], "points_asked": len(points), "undecided": sum(1 for p in points if p["status"] == "UNDECIDED"),
                              "settled": sum(1 for p in points if p["status"].startswith("SETTLED")),
                              "conflict": sum(1 for p in points if p["status"].startswith("CONFLICT")), "conflict_reports": unspec["conflict"],
                              "gaps": {p: g["reached"] for p, g in unspec["gaps"].items()}, "identical_to_previous_run": probe_same["unspecified-probe"]},
        "profile_combination_probe": profile_probe,
        "profile_combination_probe_same_as_previous_run": profile_probe == prev_metrics["profile_combination_probe"],
        "profile_combination_probe_differences": {k: {"previous": prev_metrics["profile_combination_probe"].get(k), "now": v}
                                                  for k, v in profile_probe.items() if v != prev_metrics["profile_combination_probe"].get(k)},
        "renderings_identical_to_previous_run": {"raw": False, "changed_lines": changed_render,
                                                 "why": "the four operator units are single-reading OPEN units (their reading blocks and the wide-scope term are gone, the rules print as content of the units)"},
        "senses_probe": {**prev_metrics["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-probe"]},
        "senses_document_probe": {**prev_metrics["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-document-probe"]},
        "discourse_probe": {**prev_metrics["discourse_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["discourse-probe"],
                            "difference": "same verdicts; the refusal message of the discourse block on the real translation (attempt 5) now reads 'UnsupportedProfile: Unsupported profile norm-defaults@0' where it read 'unknown document metadata' (lf-16c's Lean document boundary); a diagnostic wording change"},
        "rights_reading_probe": {**rights, "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["rights-reading-probe"],
                                 "difference": "none: byte-identical to the previous run's JSON at ve-green-lf-16c (the KeyError the previous run saw at rd-3 does not appear in the recorded diagnostics)"},
        "s1": {**prev_metrics["s1"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"],
               "historical_note": "figures and models of the soft-chain demonstration document of earlier runs (readings/s1.ve.md, not carried, not part of the translation); "
                                  "its model still names relations the translation no longer has (instruction_is_legitimate, instruction_given_while_role_playing_persona, instruction_is_for_behaviour_while_role_playing_persona)"},
        "s2a": {**prev_metrics["s2a"], "re_run_at_this_tag": False,
                "note": "superseded: the same queries run on the translation itself (checked_content_main_chain.conclusion_probe_operators and conclusion_probe)"},
        "readings_defaults_probe": {**prev_metrics["readings_defaults_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"],
                                    "outcome": {"a_main_with_readings@1": "accepted; premises UNKNOWN (no set carries content)",
                                                "b_main_with_one_strict_norm_candidate": "accepted (premises UNKNOWN: the other sets are pending)",
                                                "c_s1_document_with_norm_defaults@0": s1_probe["c_s1_document_with_norm_defaults@0"]["rejection"]}},
        "lean_decided_share": {"decided_bytes": 0, "decided_share_percent": "0.00", "script": "tools/lean_decided_share.py",
                               "meaning": "units whose every verdict is a Lean answer that is not UNKNOWN across readings. Still 0.00% at ve-green-lf-16c: RD-3 moved the enumerated folds to Lean "
                                          "(`readings-verdicts`), but neither `ve document check` nor any route reports the answer's `decided_units` (no code outside tools/lean_decided_share.py "
                                          "and its test mentions them; the Lean `setDecided` of spec 1.10 is not in lean/VE). The per-choice results and the conclusion queries are Lean's, but are not "
                                          "reported as decided units"},
        "checked_content_main_chain": {
            "what": "reading sets whose every candidate carries content that Lean checked on the main chain itself (norm-defaults@0, completion unspecified): readings@1 beside norm-defaults@0 (readings-defaults RD-2a/RD-2b); no coupling since the operator sets are gone",
            "script": "nd.py", "documents": nd, "the_translation_is_the_all_document": True,
            "reading_sets_with_checked_content": 4, "reading_sets_total": len(main_meta["reading_sets"]),
            "candidates_with_content": sum(len(s["candidates"]) for s in nd["all"]["sets"]), "candidates_total": sum(len(s["candidates"]) for s in nd["all"]["sets"]),
            "candidate_premise_status": dict(cand_status), "choices_checked_one_at_a_time": nd["all"]["choices_checked"],
            "choices_conflict_free": nd["all"]["choices_checked"], "choices_conflict": 0, "separating_situations_checked_by_lean": sep_all,
            "separated_by_decision_only_findings": 0,
            "all_four_in_one_document": {"admitted": nd["all"]["admitted"], "choices": nd["all"]["choice_count"], "budget": 64, "verdict": nd["all"]["conflict_text"],
                                         "separations": nd["all"]["separations"]},
            "split": None,
            "conclusion_probe": {"query": "every instance of Claude is not permitted to directly deny being Claude (denial_of_being_claude_permitted)", "results": concl_force},
            "conclusion_probe_operators": {"query": "no operator is permitted to give Claude an operator input classified as an instruction to claim to be human when directly and sincerely asked "
                                                    "(forall operator, input: instruction_claim_human_when_asked(input) -> not operator_input_permitted(operator, input))",
                                           "results": concl_op,
                                           "previous_run_results": concl_op_prev,
                                           "reading": "ALL: with one reading of u0123.s03 the prohibition holds whenever (the previous run's UNKNOWN under the 'wide' scope went with the wide reading, which the audit of 20261009T1800Z found is not in the words)"},
            "conclusion_probes_identical_to_previous_run": {"denial_query": concl_force_same, "claim_to_be_human_query": False,
                                                            "why_claim_human_changed": "UNKNOWN under the wide scope no longer exists: the operator sets, with their scope axis, are gone"},
            "defeasible_candidates": "the soft chain's `exception: unstated` becomes one base predicate per set that is an open term (exception_to_*), used as an `unless`; the text names no exception",
            "not_representable": [
                "defeasibility beside norm-defaults@0 as VE's own mode: probe c still refuses norm-defaults@0 with soft-norms@0 ('await the Lean route')",
                "decided units: RD-3's `readings-verdicts` is merged, but its `decided_units` are not reported by the CLI or any route at this tag (lean_decided_share stays 0)",
                "the companion split (RD-4a) is merged in Lean but `ve document` still refuses a reading with `companion` (RD-4b): not used, and no longer needed here"],
            "premises_unknown": {"candidates": [k for k, v in nd["all"]["premises_by_candidate"].items() if v != "model"], "why": "none: every candidate has a model"}},
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "unchanged_entries": len(ledger) - len(CHANGED),
            "changed_or_replaced_ids": CHANGED, "added_ids": [], "units_newly_covered": [],
            "units_with_status_change": {"u0062.s01": "READINGS -> OPEN", "u0123.s01.p1": "READINGS -> OPEN", "u0123.s02.p1": "READINGS -> OPEN", "u0123.s03": "READINGS -> OPEN"},
            "units_changed_by_note_only": ["u0166.s04.p4"], "units_changed_by_audit_repair": CHANGED,
            "reason": "the audit of 20261009T1800Z found the 'wide' reading of the role-play phrase is not in the words, so the four operator sets (u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03) "
                      "have one reading each and are OPEN units, not READINGS; claimed coverage is unchanged (both are covered statuses). u0166.s04.p4 stays UNFORMALISED with a corrected note. "
                      "No unit is upgraded: lf-16c does not change what a document can say."},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {
                "lean-first/b16c (lf-16c)": "document mode (ve-document@1 JSON boundary) in Lean: Lean's JSON reader admits `null` where Python reads it as absent, a lone UTF-16 surrogate is refused with the boundary's diagnostic, "
                                            "numbers other than naturals up to 2^53-1 fail closed, and response units/narrowings are typed. The batch says itself it is incomplete: Lean decides 4 of 412 pilot inputs "
                                            "(norm-defaults, rights, soft norms, senses and norm content stay Python-side residues); no new form of text, no new profile"},
            "newly_expressible_features": 0, "newly_expressible": "none: the merged batch changes the document boundary, not what a document can say",
            "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "what_made_the_difference": "not a feature: this run repairs units the audit rejected and applies the words-only rule again"},
        "reading_set_gaps": [
            {"gap": "a defeasible rule beside norm-defaults@0 (soft-norms@0 with norm-defaults@0 is refused, probe c)", "feature": "defaults", "workaround": "one named exception predicate per set, used as an `unless` (an open term)"},
            {"gap": "the folded verdicts are Lean's (RD-3) but the report has no decided units: `readings-verdicts` is merged and its `decided_units` are not surfaced", "feature": "other:RD-3-report", "workaround": "none needed for the per-choice results"},
            {"gap": "“cannot be unlocked by any operator or user”: who has authority to change what a norm requires; the language has no typed authority/modal (“can”, “cannot”, “may” as ability, permission or authority)", "feature": "modality/belief", "workaround": "the clause is UNFORMALISED; its effect is carried by the hard constraints' exception-free rules"},
            {"gap": "an exception the text does not name is an open term the translator names (exception_to_*), four open terms", "feature": "other:graded-force", "workaround": "recorded as open terms with 'the source names no exception' as their only factor"}],
        "carried_probes_note": "all seven carried probes re-run at this tag; byte-identical JSON: " + ", ".join(k for k, v in probe_same.items() if v) +
                               "; differs: " + ", ".join(k for k, v in probe_same.items() if not v),
    })
    dump("metrics.json", m)
    dump("units.json", ledger)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent", "claimed_but_not_audit_verified_bytes", "repaired_bytes_not_audit_verified", "changed_units")}))
    print(dict(u), dict(nb))
    print("changed render lines:", changed_render, "probe_same:", probe_same, "check same:", check_same_as_previous, "concl same:", concl_force_same)
    print("profile probe same:", m["profile_combination_probe_same_as_previous_run"])


if __name__ == "__main__":
    main()
