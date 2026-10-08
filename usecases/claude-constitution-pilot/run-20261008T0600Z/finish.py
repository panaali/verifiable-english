#!/usr/bin/env python3
"""Run 20261008T0600Z: re-run VE at ve-green-rd-6a on the repaired translation, write the ledger, renderings and metrics.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1):
    python3 -I usecases/claude-constitution-pilot/run-20261008T0600Z/repair.py     # once; the readings-from-the-words repair
    uv run python .../probe_unspecified.py ... probe_senses.py probe_senses_doc.py  # the carried probes and the new one
    uv run python -m ve document check .../readings/s1.ve.md > .../readings/check-s1.json    # about 2.5 min
    uv run python -m ve document coverage .../readings/s1.ve.md > .../readings/coverage-s1.json
    uv run python -m ve document readings .../readings/s1.ve.md --conclusion .../probes/s2/conclusion-no-denial.json [--under force-u0125-s04-p2:0|1]
    uv run python tools/lean_decided_share.py .../translation.ve.md > .../probes/lean-decided-share-main.txt
    uv run python usecases/claude-constitution-pilot/run-20261008T0600Z/finish.py

The translation is the previous run's (prev/) with the repair of repair.py; the differences are asserted below. finish_0600.py
(constants and renderers) is reused; finish.py of earlier runs are kept for reference.
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

RUN_ID = "20261008T0600Z"
PREV_RUN = "20261007T1800Z"
TAG = "ve-green-rd-6a"
PREV_TAG = "ve-green-readings-defaults"
COVERED = old.COVERED
DOCS = old.DOCS
SOURCE = old.SOURCE
ve, front_matter = old.ve, old.front_matter
dump = lambda p, o: (RUN / p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")
PREV_DIR = Path("/home/seyran/code/manage-agents/pilots/claude-constitution") / f"run-{PREV_RUN}"

# units changed by the repair: u0052.s01 in substance (its defeasible reading removed); the other four force sets only gain the
# text spans that admit their readings (note and admission wording), their readings are as they were
REPAIR_SUBSTANCE = ["u0052.s01"]
REPAIR_JUSTIFICATION_ONLY = ["u0036.s05", "u0125.s04.p2", "u0156.s03", "u0263.s04.p2"]
REMOVED_OPEN_TERMS = ["broad_safety", "appropriate_oversight", "genuine_helpfulness", "ethical_harm"]

# the 20261007T1800Z audit (AUDIT-20261007T1800Z-received.md, 20/20): the units it sampled
_rows = [r for r in (l.split() for l in (RUN / "AUDIT-20261007T1800Z-received.md").read_text().split("```text")[1].split("```")[0].strip().splitlines()) if len(r) == 2]
AUDIT_LATEST = [u for u, v in _rows if v == "FAITHFUL"]
AUDIT_LATEST_REJECTED = [u for u, v in _rows if v != "FAITHFUL"]
AUDIT_LATEST_ID = "20261007T1800Z"


def differing_paths(x, y, path=""):
    """Paths of the leaves where two JSON values differ (shape differences are reported as the path of the container)."""
    if type(x) is not type(y):
        return [path]
    if isinstance(x, dict):
        keys = set(x) | set(y)
        return [p for k in sorted(keys) for p in (differing_paths(x[k], y[k], f"{path}/{k}") if k in x and k in y else [f"{path}/{k}"])]
    if isinstance(x, list):
        if len(x) != len(y):
            return [path]
        return [p for i, (a, b) in enumerate(zip(x, y)) for p in differing_paths(a, b, f"{path}/{i}")]
    return [] if x == y else [path]


def main():
    prev = json.load(open(RUN / "prev/units.json"))
    ledger = json.load(open(RUN / "units.json"))
    prev_metrics = json.load(open(RUN / "prev/metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == prev_metrics["source_sha256"]
    prev_by_id = {e["id"]: e for e in prev}
    for e in ledger:
        e["status_in_previous_run"] = prev_by_id[e["id"]]["status"]

    # ---- the repair, asserted: only these ledger entries differ from the previous run's
    changed = [e["id"] for e in ledger if {k: v for k, v in e.items() if k != "status_in_previous_run"} != {k: v for k, v in prev_by_id[e["id"]].items() if k != "status_in_previous_run"}]
    assert sorted(changed) == sorted(REPAIR_SUBSTANCE + REPAIR_JUSTIFICATION_ONLY), changed
    assert [e["id"] for e in ledger] == [e["id"] for e in prev]
    status_changes = {e["id"]: (prev_by_id[e["id"]]["status"], e["status"]) for e in ledger if e["status"] != prev_by_id[e["id"]]["status"]}
    assert status_changes == {"u0052.s01": ("READINGS", "OPEN")}, status_changes
    assert (RUN / "translation.ve.md").read_bytes() != (RUN / "prev/translation.ve.md").read_bytes()
    for rel in ("readings/all-strict.ve.md", "readings/all-default.ve.md", "readings/s1.ve.md"):
        assert (RUN / rel).read_bytes() != (PREV_DIR / rel).read_bytes(), rel

    # ---- VE runs at this tag (main, strict, default fresh; s1 check and coverage were run by hand and are read here)
    results = {}
    for key, path in DOCS.items():
        rel = str(path.relative_to(ROOT))
        if key == "s1":
            results[key] = {"check": json.load(open(RUN / "readings/check-s1.json")),
                            "coverage": json.load(open(RUN / "readings/coverage-s1.json")), "render": ve("document", "render", rel)}
        else:
            results[key] = {"check": json.loads(ve("document", "check", rel)), "coverage": json.loads(ve("document", "coverage", rel)),
                            "render": ve("document", "render", rel)}
    main_meta, strict_meta, soft_meta, s1_meta = (front_matter(DOCS[k]) for k in ("main", "strict", "default", "s1"))
    prev_main_meta = old.front_matter(RUN / "prev/translation.ve.md")
    assert [r["id"] for r in prev_main_meta["reading_sets"]] == [r["id"] for r in main_meta["reading_sets"]] + ["force-u0052-s01"] or \
        sorted(r["id"] for r in prev_main_meta["reading_sets"]) == sorted([r["id"] for r in main_meta["reading_sets"]] + ["force-u0052-s01"])
    assert [t["name"] for t in prev_main_meta["open_terms"] if t["name"] not in {t["name"] for t in main_meta["open_terms"]}] == REMOVED_OPEN_TERMS
    prev_check = {"main": json.load(open(PREV_DIR / "check.json")), "strict": json.load(open(PREV_DIR / "readings/check-all-strict.json")),
                  "default": json.load(open(PREV_DIR / "readings/check-all-default.json")), "s1": json.load(open(PREV_DIR / "readings/check-s1.json"))}
    diffs = {k: differing_paths(results[k]["check"], prev_check[k]) for k in prev_check}
    for k in ("main", "strict", "default"):
        assert results[k]["check"]["premises"]["status"] == prev_check[k]["premises"]["status"], k
    dump("check.json", results["main"]["check"])
    dump("coverage.json", results["main"]["coverage"])
    dump("readings/check-all-strict.json", results["strict"]["check"])
    dump("readings/check-all-default.json", results["default"]["check"])
    dump("environment.json", main_meta["environment"])
    dump("readings/environment-all-default.json", soft_meta["environment"])
    prev_render = {k: (PREV_DIR / "readings" / n).read_text() for k, n in (("strict", "rendered-all-strict.md"), ("default", "rendered-all-default.md"), ("s1", "rendered-s1.md"))}
    changed_render_lines = {}
    for key, name in (("strict", "rendered-all-strict.md"), ("default", "rendered-all-default.md"), ("s1", "rendered-s1.md")):
        (RUN / "readings" / name).write_text(results[key]["render"])
        changed_render_lines[key] = sum(1 for d in difflib.unified_diff(prev_render[key].splitlines(), results[key]["render"].splitlines(), lineterm="", n=0)
                                        if d[:1] in "+-" and d[:3] not in ("+++", "---"))
    rendered = old.annotate_hard(old.expand_main(results["main"]["render"], main_meta, ledger), ledger)
    prev_rendered = (PREV_DIR / "rendered.md").read_text()
    changed_render_lines["main_expanded"] = sum(1 for d in difflib.unified_diff(prev_rendered.splitlines(), rendered.splitlines(), lineterm="", n=0)
                                                if d[:1] in "+-" and d[:3] not in ("+++", "---"))
    changed_render_lines["main_raw"] = sum(1 for d in difflib.unified_diff((PREV_DIR / "rendered-raw.md").read_text().splitlines(), results["main"]["render"].splitlines(), lineterm="", n=0)
                                           if d[:1] in "+-" and d[:3] not in ("+++", "---"))
    (RUN / "rendered.md").write_text(rendered)
    (RUN / "rendered-raw.md").write_text(results["main"]["render"])

    # ---- the S1 companion's separating situations and result file (the u0052.s01 set is gone)
    s1c = results["s1"]["check"]
    s1_result = json.loads((RUN / "readings/s1-result.json").read_text())
    if any(s["set"] == "force-u0052-s01" for s in s1_result["sets"]):
        s1_result["sets"] = [s for s in s1_result["sets"] if s["set"] != "force-u0052-s01"]
        s1_result["document"] = "usecases/claude-constitution-pilot/run-20261008T0600Z/readings/s1.ve.md"
        s1_result["note_20261008T0600Z"] = "the set force-u0052-s01 was removed (repair.py: the defeasible reading of u0052.s01 is not admissible); the other entries are as in run 20261007T1800Z"
        dump("readings/s1-result.json", s1_result)
    separation = old.separating_situations(s1c, s1_result)
    dump("readings/separating-situations.json", separation)
    rd, pr = s1c["readings"], s1c["premises"]
    cand_status = {f"{c['set']}:{c['index']}": c["status"] for c in pr["candidates"]}
    concl = {}
    for name, f in (("across_all_readings", "conclusion-no-denial-result.json"), ("under_must", "conclusion-no-denial-under-0.json"),
                    ("under_should", "conclusion-no-denial-under-1.json")):
        r = json.load(open(RUN / "probes/s2" / f))
        prev_r = json.load(open(PREV_DIR / "probes/s2" / f))
        assert {k: r[k] for k in r if k != "english"} == {k: prev_r[k] for k in prev_r if k != "english"}, f
        concl[name] = {k: r[k] for k in ("verdict", "route", "evidence", "assumed", "budget") if k in r}
    prev_s2 = prev_metrics["s2a"]
    set_of_unit = {s["unit"]: s["set"] for s in rd["sets"]}
    s2a = {**prev_s2, "re_run_at_this_tag": True, "identical_to_previous_run": False,
           "differences_from_previous_run": "the companion lost the set force-u0052-s01 (one set fewer: 7 content-bearing sets, 17 candidates); the three conclusion queries give the "
                                            "previous verdicts, routes, evidence and assumptions exactly; their English no longer says sentence 190 (u0052.s01)",
           "before_this_tag": prev_s2["before_this_tag"],
           "now": {"premises_status": pr["status"], "route": pr["route"], "evidence": pr["evidence"], "choice": pr["choice"],
                   "conflict_status": rd["status"], "conflict_evidence": rd["conflict"]["evidence"], "route_of_readings": rd["route"],
                   "choice_count": rd["choice_count"], "choices_checked": rd["choices_checked"], "dead_readings": rd["dead_readings"],
                   "reading_premises_in_force": len(rd["reading_premises"]), "sizes": rd["sizes"], "not_superposable": rd["not_superposable"],
                   "english": rd["english"]},
           "candidate_premise_status": cand_status, "candidate_status_counts": dict(Counter(cand_status.values())),
           "candidates_without_model": [k for k, v in cand_status.items() if v != "model"],
           "units_with_a_set_in_the_companion": set_of_unit,
           "conclusion_probe_re_run": concl,
           "conclusion_probe": {**prev_s2["conclusion_probe"], "results": {**prev_s2["conclusion_probe"]["results"]}},
           "load_and_check_seconds": "2 min 21 s for `ve document check` of readings/s1.ve.md at this tag (5 min 18 s at ve-green-readings-defaults, on another machine "
                                     "state, one set fewer); the conclusion queries took 63 s (across readings), 22 s (under must), 46 s (under should)"}
    s2a["conclusion_probe"]["results"].update(concl)

    # ---- ledger invariants
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE)
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    assert [(u["id"], tuple(u["span"])) for u in main_meta["units"]] == [(e["id"], tuple(e["span"])) for e in ledger]
    u, nb = old.counts(ledger)
    claimed = sum(v for k, v in nb.items() if k in COVERED)
    doc_cov = results["main"]["coverage"]
    assert doc_cov["bytes_by_status"].get("OPEN", 0) == nb["OPEN"] + nb["READINGS"]
    assert claimed == prev_metrics["claimed_covered_bytes"]
    n_old, old_units, _old_bytes = old.aggregate(ledger)
    status = {e["id"]: e["status"] for e in ledger}
    spans = {e["id"]: e["span"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)
    ledger_by_id = {e["id"]: e for e in ledger}

    # ---- audit-verified bytes: accepted by an independent audit of this lineage AND byte-identical in this run to the form it saw
    prev_verified_sub = list(prev_metrics["audit_verified_covered_units"])
    accepted = [i for i in AUDIT_LATEST if i in ledger_by_id]
    assert len(accepted) == 20 and not AUDIT_LATEST_REJECTED
    accepted_sub = [i for i in accepted if status[i] in COVERED and status[i] != "LABELLED"]
    accepted_lab = [i for i in accepted if status[i] == "LABELLED"]
    changed_since = [i for i in prev_verified_sub + accepted_sub if i in REPAIR_SUBSTANCE + REPAIR_JUSTIFICATION_ONLY]
    changed_since = list(dict.fromkeys(changed_since))
    verified_sub = [i for i in dict.fromkeys(prev_verified_sub + accepted_sub) if i not in changed_since]
    newly_sub = [i for i in verified_sub if i not in prev_verified_sub]
    _a5 = [r for r in (l.split() for l in (RUN / "AUDIT-20261005T1800Z-received.md").read_text().split("```text")[1].split("```")[0].strip().splitlines()) if len(r) == 2]
    prior_lab = list(dict.fromkeys(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED + [
        "u0286.heading", "u0013.heading", "u0055.heading", "u0008.heading", "u0023", "u0126", "u0282"]
        + [u_ for u_, v in _a5 if v == "FAITHFUL" and u_ in ledger_by_id and status[u_] == "LABELLED"]))
    assert width([i for i in prior_lab if i in ledger_by_id and status[i] == "LABELLED"]) == prev_metrics["audit_verified_metadata_bytes"], "prior verified labels do not reproduce"
    cand_lab = list(dict.fromkeys(prior_lab + accepted_lab))
    verified_lab = [i for i in cand_lab if i in ledger_by_id and status[i] == "LABELLED"]
    newly_lab = [i for i in verified_lab if i not in set(prior_lab)]
    assert all(status[i] in COVERED for i in verified_sub)
    sub_bytes, lab_bytes = width(verified_sub), width(verified_lab)
    lenient = sub_bytes + width([i for i in changed_since if i in REPAIR_JUSTIFICATION_ONLY])
    prev_ap = prev_metrics["audit_rejected_units_and_repair_status"]
    repaired_unverified = sorted(set(prev_ap["repaired_and_not_yet_sampled"]) - set(verified_sub))
    still_unverified_covered = sorted(set(changed_since))

    # ---- profile combinations at this tag, the carried probes and the new senses-document probe
    profile_probe = old.probe_profiles()
    s1_probe = json.load(open(RUN / "probes/s1-probe.json"))
    unspec = json.load(open(RUN / "probes/unspecified-probe.json"))
    senses_doc = json.load(open(RUN / "probes/senses-document-probe.json"))
    points = unspec["points"]
    settled = sum(1 for p in points if p["status"].startswith("SETTLED"))
    undecided = sum(1 for p in points if p["status"] == "UNDECIDED")
    conflict_points = sum(1 for p in points if p["status"].startswith("CONFLICT"))
    ds = json.loads((RUN / "probes/lean-decided-share-main.txt").read_text())

    s1_prev = prev_metrics["s1"]
    s1_section = copy.deepcopy(s1_prev)
    s1_section["sets"] = {k: v for k, v in s1_section["sets"].items() if k != "u0052.s01"}
    s1_section.update({
        "profiles": s1_meta["environment"]["profiles"],
        "content_bearing_sets": len(rd["sets"]),
        "sets": {s["unit"]: {"set": s["set"], "source_word": {x["set"]: x["source_word"] for x in s1_result["sets"]}.get(s["set"]),
                             "candidates": [c["id"] for c in s["candidates"]],
                             "pairs": [{"readings": p["readings"], "probe": p["probe"], "wording": p["wording"]} for p in s["pairs"]],
                             "findings": s["findings"]} for s in rd["sets"]},
        "separations": rd.get("separations"), "findings": rd.get("findings"),
        "wordings": dict(Counter(p["wording"] for s in rd["sets"] for p in s["pairs"])),
        "not_certified": [f for s in rd["sets"] for f in s["not_certified"]],
        "premises": pr, "bytes_by_status": results["s1"]["coverage"]["bytes_by_status"],
        "probe": s1_probe,
        "removed_in_20261008T0600Z": "the set force-u0052-s01 (the defeasible reading of u0052.s01 is not admissible: “always”); the unit is now one strict rule in the companion"})
    cv = copy.deepcopy(prev_metrics["check_verdicts"])
    cv["main"].update({"coverage_percent": doc_cov["coverage_percent"], "premises": results["main"]["check"]["premises"],
                       "reading_plan": results["main"]["check"]["reading_plan"], "residual": doc_cov["residual"],
                       "norm_defaults": doc_cov.get("norm_defaults"),
                       "reading_plan_note": "`choice_count` is the running product of the sets' reading counts at the moment it first exceeds the budget of 64 (ve/readings.py plan_choices), "
                                            "so it depends on the order of the sets and is not the number of choices: 144 now, 72 before, with one set fewer"})
    cv["all_strict"].update({"premises": results["strict"]["check"]["premises"], "residual": results["strict"]["coverage"]["residual"],
                             "bytes_by_status": results["strict"]["coverage"]["bytes_by_status"], "norm_defaults": results["strict"]["coverage"].get("norm_defaults")})
    cv["s1"].update({"premises": pr, "readings": {k: v for k, v in rd.items() if k in ("separations", "findings")},
                     "residual": results["s1"]["coverage"]["residual"], "bytes_by_status": results["s1"]["coverage"]["bytes_by_status"]})
    cv["all_default"].update({"premises": results["default"]["check"]["premises"], "residual": results["default"]["coverage"]["residual"],
                              "bytes_by_status": results["default"]["coverage"]["bytes_by_status"],
                              "default_exceptions_by_decider": results["default"]["coverage"].get("default_exceptions_by_decider")})
    for k, key in (("main", "main"), ("all_strict", "strict"), ("all_default", "default"), ("s1", "s1")):
        cv[k]["verdict_differences_from_previous_run"] = diffs[key]

    m = copy.deepcopy(prev_metrics)
    ap_now = {
        "rejected_by_20261007T1800Z_audit": AUDIT_LATEST_REJECTED,
        "repair_needed_in_20261008T0600Z": "none from the audit (20/20 faithful, nothing marked unfaithful or incomplete). The repair of this run is the lead's rule of 2026-10-08, "
                                           "readings come from the words only: u0052.s01 lost its defeasible reading; four force sets now cite the spans that admit them; "
                                           "four open terms no unit uses were removed (see AUDIT-REPAIR.md)",
        "repaired_and_not_yet_sampled": sorted(set(repaired_unverified) | set(REPAIR_SUBSTANCE)),
        "earlier": {k: v for k, v in prev_ap.items()}}
    m.update({
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "previous_runs_note": "run 20261007T1800Z is the previous run's own output (manage-agents/pilots/claude-constitution/run-20261007T1800Z); a ve-green-rd-6a run is the first of the lineage after the lf-10b deletion of the Python norm-defaults route (probe_unspecified.py was ported)",
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": old.full(u), "bytes_by_status": old.full(nb),
                                  "previous_run": {k: prev_metrics["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units, "bytes_by_substatus": old.full(nb),
                                              "previous_run": {k: prev_metrics["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")}},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": prev_metrics["claimed_covered_bytes"], "claimed_covered_bytes_gained": claimed - prev_metrics["claimed_covered_bytes"],
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"],
        "substantive_covered_bytes_previous_run": prev_metrics["substantive_covered_bytes"],
        "audit_verified_covered_bytes": sub_bytes, "audit_verified_covered_percent": round(100 * sub_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified_sub,
        "audit_verified_covered_bytes_previous_run": prev_metrics["audit_verified_covered_bytes"],
        "audit_verified_covered_bytes_if_justification_only_edits_are_ignored": lenient,
        "audit_verified_metadata_bytes": lab_bytes, "audit_verified_metadata_percent": round(100 * lab_bytes / len(SOURCE), 4),
        "audit_verified_metadata_bytes_previous_run": prev_metrics["audit_verified_metadata_bytes"],
        "audit_verified_basis": (
            f"Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run to the form that audit saw. The latest audit "
            f"({AUDIT_LATEST_ID}, 20/20, a verdict for every sampled unit) saw the previous run's form. This run changed five audited units: u0052.s01 in substance "
            f"(defeasible reading removed) and u0036.s05, u0125.s04.p2, u0156.s03, u0263.s04.p2 only by adding the source spans that admit their readings to the note and "
            f"the admission wording (readings and content unchanged). To stay byte-identical-or-not-counted, all five are dropped from the verified set until re-audited "
            f"({sub_bytes} bytes); if the four justification-only edits were ignored the figure would be {lenient}. Label units are unchanged "
            f"({lab_bytes} verified heading-marker bytes)."),
        "audit_verified_newly_from_20261007T1800Z": newly_sub, "audit_verified_newly_label_units_from_20261007T1800Z": newly_lab,
        "audit_verified_dropped_because_changed_or_rejected": {"changed_since_acceptance": still_unverified_covered, "rejected_by_an_audit_and_not_re_accepted": [],
                                                              "changed_in_substance": REPAIR_SUBSTANCE, "changed_by_justification_only": REPAIR_JUSTIFICATION_ONLY},
        "audit_rejected_units_and_repair_status": ap_now,
        "claimed_but_not_audit_verified_bytes": claimed - sub_bytes - lab_bytes,
        "repaired_bytes_not_audit_verified": width(ap_now["repaired_and_not_yet_sampled"]),
        "document_profiles": {k: front_matter(v)["environment"]["profiles"] for k, v in DOCS.items()},
        "open_terms": [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")} for t in main_meta["open_terms"]],
        "open_terms_count": len(main_meta["open_terms"]), "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "open_terms_removed": {"names": REMOVED_OPEN_TERMS, "why": "no unit used them and their `factors` were the translator's, not questions the text raises at a covered unit "
                                                                     "(lead, 2026-10-08: never list unsettled questions the text does not raise); good_judgment's factors became the one question its words raise"},
        "reading_sets": {
            "count": len(main_meta["reading_sets"]), "unresolved": len(main_meta["reading_sets"]),
            "candidates": {rs["unit"]: [r["id"] for r in rs["readings"]] for rs in main_meta["reading_sets"]},
            "units": [rs["unit"] for rs in main_meta["reading_sets"]], "narrowings": [], "narrowings_note": prev_metrics["reading_sets"]["narrowings_note"],
            "count_previous_run": prev_metrics["reading_sets"]["count"],
            "readings_from_the_words": {
                "force_sets_kept_because_of_the_word_should": {"units": ["u0036.s05", "u0263.s04.p2"], "spans": ["u0253.s04", "u0011.s01"]},
                "force_sets_kept_because_the_text_implies_exceptions": {"units": ["u0125.s04.p2", "u0156.s03"], "spans": ["u0109.s06", "u0109.s05"]},
                "can_cannot_sets_kept_because_of_the_word_can": ["u0062.s01", "u0123.s02.p1", "u0123.s03"],
                "scope_set": "u0123.s01.p1 and u0123.s03: how far “while role-playing as a custom AI persona” reaches (syntax of the sentence) and how far the limits of u0123.s03 reach",
                "removed": {"u0052.s01": "“should always”: the word “always” excludes exceptions in the sentence itself and no span of the text implies one"}}},
        "missing_feature_tally": old.tally(ledger), "missing_feature_tally_previous_run": prev_metrics["missing_feature_tally"],
        "check_verdicts": cv,
        "unspecified_probe": {**prev_metrics["unspecified_probe"], "points_asked": len(points), "undecided": undecided, "settled": settled, "conflict": conflict_points,
                              "conflict_reports": unspec["conflict"], "gaps": {p: g["reached"] for p, g in unspec["gaps"].items()},
                              "identical_to_previous_run": False,
                              "differences_from_previous_run": "one point added (u0052.s01, now a rule: SETTLED yes everywhere); the 34 earlier points, the conflict reports and the gaps equal the previous "
                                                               "run's. The probe was ported: the Python status/conflict/report API was deleted by lean-first/b10b (see language_changes); "
                                                               "points are now Lean's `norm-defaults-status` rows, gaps Lean's `norm-defaults-report`, and the whole-document conflict verdict is Lean's "
                                                               "`norm-defaults-conflict` row on a certificate the frozen Python oracle proposed"},
        "profile_combination_probe": profile_probe,
        "profile_combination_probe_same_as_previous_run": profile_probe == prev_metrics["profile_combination_probe"],
        "separating_situations": {**prev_metrics["separating_situations"], "reading_sets": len(separation)},
        "s1": s1_section, "s2a": s2a,
        "senses_probe": {**prev_metrics["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": True},
        "senses_document_probe": {
            "file": "probes/senses-document-probe.json", "script": "probe_senses_doc.py", "documents": "probes/senses-documents/",
            "feature": "senses in `ve document` (RD-8, merged in ve-green-rd-6a): a `senses` front-matter key makes the document's English fences read by Lean's sense reader",
            "cases": {name: ({"loaded": c["loaded"], "units": c.get("units"), "refusal": c.get("refusal")} if c["loaded"] else {"loaded": False, "refusal": c.get("refusal") or c.get("error")})
                      for name, c in senses_doc.items()},
            "units_upgraded": 0,
            "why_no_unit_changed": "the senses block lets a document choose which sense of a word its sentences use (default, definition line, parenthetical) and refuses an unchosen "
                                   "ambiguous word with Lean's text; it cannot say that a word does NOT have a sense (u0220.s02 “corrigibility does not mean blind obedience”: the nearest "
                                   "sentence, case e, asserts a claim about Claude, not about the word), and the definition u0220.s01 “We call an AI that is broadly safe in this way "
                                   "‘corrigible’” needs its antecedent “in this way” (discourse) and is an act of Anthropic's (attribution), not the document's own stipulation. "
                                   "Switching the main document to a senses block would send every English fence through the sense reader (the main document has none: its units are "
                                   "structured), so nothing in it uses the feature. Also: a conjunction of two sentences each with a word of the pack was refused (“Sentence 2 has no "
                                   "reading with the current vocabulary”, case f)"},
        "readings_defaults_probe": {**prev_metrics["readings_defaults_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": True,
                                    "outcome": {"a_main_with_readings@1": "accepted; premises UNKNOWN (no set carries content)",
                                                "b_main_with_one_strict_norm_candidate": s1_probe["b_main_with_one_strict_norm_candidate"]["rejection"],
                                                "c_s1_document_with_norm_defaults@0": s1_probe["c_s1_document_with_norm_defaults@0"]["rejection"]},
                                    "why": "RD-6a (S2a with a carried base-premise family) is Lean-only and called by nothing: `lean/VE/Readings/Wire.lean` `abstention` still refuses a "
                                           "content-bearing set beside norm-defaults@0 (RD-2a, RD-3, RD-4 are not built)"},
        "lean_decided_share": {**ds, "script": "tools/lean_decided_share.py", "new_in_this_tag": False,
                               "meaning": "units whose every verdict is a Lean answer that is not UNKNOWN across readings; still no route emits `decided_units`, so 0 for the main translation and the s1 companion"},
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "unchanged_entries": len(ledger) - len(changed), "changed_or_replaced_ids": sorted(changed),
            "added_ids": [], "units_newly_covered": [], "units_newly_covered_parent_previous_status": {}, "units_with_status_change": ["u0052.s01"],
            "status_change": {"u0052.s01": "READINGS -> OPEN (one strict reading with content; the defeasible reading is removed)"},
            "units_changed_by_justification_only": REPAIR_JUSTIFICATION_ONLY,
            "reason": "the repair under the lead's rule of 2026-10-08 (readings come from the words only; see AUDIT-REPAIR.md). No newly merged feature adds a form of text the "
                      "translation can use, so no unit is upgraded by the language (FEATURE-REVIEW.md)"},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "git_diff": "184 files changed (77,011 insertions, 43,605 deletions); 25 under ve/ (relays, deletions, the senses document reader)",
            "merged": {
                "lean-first/b6 (lf-6)": "soft-norms decision code moves from Python to Lean (the Python copy kept as a conformance oracle); A/B recorded identical on the public corpora",
                "lean-first/b10b (lf-10b)": "norm-defaults decision code moves to Lean (`Explain`, layered report); the Python `UnspecifiedDocument.status`, `check_conflict` and `report` lines are deleted "
                                            "(the pinned copy lives in conformance/frozen_norm_defaults.py). Answers are the same; the pilot's probe_unspecified.py had to be ported",
                "readings-defaults/rd8 (rd-8)": "senses in `ve document`: a `senses` front-matter key (packs, own, defaults) sends every English fence to Lean's sense reader; new refusals relayed from Lean",
                "readings-defaults/rd6a (rd-6a)": "Lean only: S2a with a carried base-premise family (`superpose_all_extra` needed an added hypothesis, its approved form refuted in Lean); nothing calls it"},
            "newly_expressible_features": 1,
            "newly_expressible": "a document can choose a word's sense (senses block); nothing in the constitution translation needs it yet",
            "units_upgraded_by_new_features": 0,
            "why_no_unit_changed_status": "the feature aimed at the constitution (readings@1 content beside norm-defaults@0, F1) is still not built; the senses block cannot express a statement about what a word does not mean",
            "profile_combination_result": "the same accept/refuse outcome for all 13 added profiles; the refusal wording of closure@0 and order@0 changed (“norm document admission is FOL-only” -> “the norms route admits FOL documents only”)" if all((profile_probe[k] == prev_metrics["profile_combination_probe"][k]) or (profile_probe[k].startswith("UnsupportedProfile") and prev_metrics["profile_combination_probe"][k].startswith("UnsupportedProfile")) for k in profile_probe) else "changed (see profile_combination_probe)"},
        "carried_probes_note": "all six carried probes re-run at this tag; five byte-identical to the previous run's; probe_unspecified.py was ported to Lean's rows (same 34 statuses, one point added)",
        "readings_from_the_words_rule": {
            "from": "lead, 2026-10-08", "rule": "a reading set is allowed only where the English itself supports more than one meaning; no reading from outside knowledge; no unsettled question the text does not raise",
            "checked": {"reading_sets_before": 9, "reading_sets_after": 8,
                        "readings_removed": ["u0052.s01: default (defeasible) reading of “should always”"],
                        "readings_kept_with_their_text_spans": ["u0036.s05", "u0263.s04.p2", "u0125.s04.p2", "u0156.s03"],
                        "readings_kept_because_the_word_can_or_cannot_has_both_senses": ["u0062.s01", "u0123.s02.p1", "u0123.s03"],
                        "no_party_or_actor_reading_from_outside_knowledge_found": True,
                        "open_terms_removed": REMOVED_OPEN_TERMS},
            "judgment_calls_for_the_auditor": [
                "u0036.s05 and u0263.s04.p2 (plain “should”): both readings kept because “should” is the document's own “directive language” and it favours judgment over strict rules; "
                "a stricter reading of the rule would make them one-reading units like u0168.s01",
                "u0125.s04.p2 and u0156.s03 (“should never”, “shouldn’t”): defeasible reading kept because u0109.s06 says “should basically never directly lie or actively deceive” and u0109.s05 "
                "“something quite similar to” a hard constraint; the span is about honesty in general, the two sentences apply it",
                "u0123.s02.p1 “can legitimately instruct”: the ability reading is kept as the words of “can” admit it, although “legitimately” leans to permission"]},
    })
    dump("metrics.json", m)
    dump("units.json", ledger)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent",
                                         "audit_verified_metadata_bytes", "claimed_but_not_audit_verified_bytes")}))
    print(dict(u), dict(nb))
    print("verified:", verified_sub, "dropped:", still_unverified_covered)
    print("diffs:", {k: len(v) for k, v in diffs.items()})


if __name__ == "__main__":
    main()
