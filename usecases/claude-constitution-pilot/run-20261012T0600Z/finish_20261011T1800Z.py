#!/usr/bin/env python3
"""Run 20261011T1800Z: re-run VE at ve-green-arch-AR-8, write the ledger copy, renderings and metrics.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    probes and conclusion queries (README.md)
    uv run python .../nd.py all                          # readings/nd-all.ve.md must equal translation.ve.md; about 2 min
    uv run python .../finish_20261011T1800Z.py           # about 3 min

The translation is the previous run's (20261010T1800Z) byte for byte: that run's audit found all 31 sampled and changed units faithful
(AUDIT-20261010T1800Z-received.md), and the batches merged since (readings-defaults RD-6b, infra AR-8) do not change what a document can say.
No unit changes, so `changed_units` is empty; the measurement is what the language now does with the same document.
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

RUN_ID = "20261011T1800Z"
PREV_RUN = "20261010T1800Z"
TAG = "ve-green-arch-AR-8"
PREV_TAG = "ve-green-arch-AR-6"
COVERED = old.COVERED
SOURCE = old.SOURCE
ve, front_matter = old.ve, old.front_matter
dump = lambda p, o: (RUN / p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")
PREV_DIR = RUN / "prev"
MAIN = RUN / "translation.ve.md"
STRICT = RUN / "readings/all-strict.ve.md"
SETS = {"u0036.s05": "force-u0036-s05", "u0125.s04.p2": "force-u0125-s04-p2", "u0156.s03": "force-u0156-s03", "u0263.s04.p2": "force-u0263-s04-p2"}
OP_UNITS = ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03"]
HC_UNITS = [f"u0165.s0{i}" for i in range(1, 8)]
# the audit of run 20261010T1800Z (20/20 sampled + 11/11 changed faithful), verdicts as received (AUDIT-20261010T1800Z-received.md)
AUDIT_FAITHFUL_1800 = ["u0036.s05", "u0052.s01", "u0062.s01", "u0073.s05", "u0095.heading", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03", "u0125.s04.p2", "u0126",
                       "u0143.heading", "u0156.s03", "u0165.s01", "u0165.s02", "u0165.s03", "u0165.s04", "u0165.s05", "u0165.s06", "u0165.s07", "u0168.s01",
                       "u0174.heading", "u0245.heading", "u0248", "u0257.heading", "u0263.s04.p2", "u0294"]


def slice_result(g):
    r = json.load(open(RUN / f"readings/nd-{g}-result.json"))
    cov = json.load(open(RUN / f"readings/coverage-nd-{g}.json"))
    rd, pr = r["readings"], r["premises"]
    choices = rd["conflict"].get("choices") or []
    return {"document": "translation.ve.md", "admitted": r["admitted"], "load_seconds": r.get("load_seconds"),
            "check_seconds": r.get("check_seconds"), "separation_search_seconds": r["search_seconds"],
            "sets": [{"set": s["set"], "unit": s["unit"], "candidates": s["candidates"]} for s in r["sets"]],
            "route": rd["route"], "choice_count": rd.get("choice_count"), "choices_checked": rd.get("choices_checked"), "sizes": rd.get("sizes"),
            "couplings": rd.get("couplings"), "conflict": rd["conflict"]["status"], "conflict_evidence": rd["conflict"].get("evidence"),
            "conflict_text": rd["status"], "conflict_by_choice": dict(Counter(c["status"] for c in choices)),
            "premises": pr["status"], "premises_route": pr["route"], "premises_gaps": pr.get("gaps"),
            "premises_by_candidate": {f"{c['set']}:{c['index']}": c["status"] for c in pr.get("candidates", [])},
            "separations": rd["separations"], "findings": rd["findings"], "pending_candidates": rd["pending_candidates"], "dead_readings": rd["dead_readings"],
            "not_superposable": rd.get("not_superposable"), "pairs_without_situation": r["pairs_without_situation"],
            "english": rd["english"], "residual": cov["residual"], "bytes_by_status": cov["bytes_by_status"]}


def concl(names):
    out = {}
    for name, f in names:
        c = json.load(open(RUN / "probes/nd" / f))
        out[name] = {k: c[k] for k in ("verdict", "route", "evidence", "assumed", "english") if k in c}
    return out


def main():
    prev = json.load(open(PREV_DIR / "units.json"))
    ledger = json.load(open(RUN / "units.json"))
    prev_metrics = json.load(open(PREV_DIR / "metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == prev_metrics["source_sha256"]
    assert ledger == prev, "the ledger is the previous run's"
    assert MAIN.read_bytes() == (PREV_DIR / "translation.ve.md").read_bytes(), "the translation is the previous run's"
    by_id = {e["id"]: e for e in ledger}
    main_meta = front_matter(MAIN)
    prev_main = front_matter(PREV_DIR / "translation.ve.md")
    assert [(u["id"], tuple(u["span"])) for u in main_meta["units"]] == [(e["id"], tuple(e["span"])) for e in ledger]

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
    rendered = old.annotate_hard(render, ledger)
    (RUN / "rendered.md").write_text(rendered)
    (RUN / "rendered-raw.md").write_text(render)
    render_same = render == (PREV_DIR / "rendered-raw.md").read_text()
    assert check["premises"]["status"] == "model", check["premises"]
    assert check["reading_plan"]["route"] == "enumerate" and len(check["reading_plan"]["choices"]) == 16
    prev_check = json.load(open(PREV_DIR / "check.json"))
    skip = {"coverage", "residual", "readings", "document_id", "admission", "premises"}
    check_same = all(check.get(k) == prev_check.get(k) for k in set(check) | set(prev_check) if k not in skip)
    cov_same = {k: coverage[k] for k in ("bytes_by_status", "coverage_percent", "residual")} == {k: json.load(open(PREV_DIR / "coverage.json"))[k] for k in ("bytes_by_status", "coverage_percent", "residual")}
    assert cov_same and render_same

    # ---- ledger and counts
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE)
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    u, nb = old.counts(ledger)
    claimed = sum(v for k, v in nb.items() if k in COVERED)
    assert claimed == prev_metrics["claimed_covered_bytes"], claimed
    n_old, old_units, _ = old.aggregate(ledger)
    spans = {e["id"]: e["span"] for e in ledger}
    status = {e["id"]: e["status"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)

    # ---- audit-verified bytes: accepted by an audit of this lineage AND byte-identical here to the form that audit saw (everything is: nothing changed)
    prev_verified = list(prev_metrics["audit_verified_covered_units"])
    assert all(by_id[i]["status"] in COVERED for i in prev_verified)
    faithful_sub = [i for i in AUDIT_FAITHFUL_1800 if status[i] in COVERED and status[i] != "LABELLED"]
    faithful_lab = [i for i in AUDIT_FAITHFUL_1800 if status[i] == "LABELLED"]
    newly = [i for i in faithful_sub if i not in prev_verified]
    verified = list(dict.fromkeys(prev_verified + newly))
    verified_bytes = width(verified)
    assert verified_bytes == prev_metrics["audit_verified_covered_bytes"] + width(newly)
    cand_lab = list(dict.fromkeys(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED + ["u0212.heading"]))
    verified_lab_before = [i for i in cand_lab if i in by_id and status[i] == "LABELLED"]
    assert width(verified_lab_before) == prev_metrics["audit_verified_metadata_bytes"], width(verified_lab_before)
    newly_lab = [i for i in faithful_lab if i not in verified_lab_before]
    verified_lab = verified_lab_before + newly_lab
    verified_meta = width(verified_lab)
    sampled_changed_now_verified = sorted(set(HC_UNITS + OP_UNITS) & set(verified))
    assert sampled_changed_now_verified == sorted(HC_UNITS + OP_UNITS)

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
    prev_op = prev_cc["conclusion_probe_operators"]["results"]
    verdicts = lambda c: {k: v["verdict"] for k, v in c.items()}
    assert verdicts(concl_force) == verdicts(prev_force_results) and verdicts(concl_op) == verdicts(prev_op)
    both = {**{f"denial_{k}": v for k, v in concl_force.items()}, "claim_human_across_all_readings": concl_op["across_all_readings"]}
    routes_now = {k: v["route"] for k, v in both.items()}

    unspec = json.load(open(RUN / "probes/unspecified-probe.json"))
    points = unspec["points"]
    s1_probe = json.load(open(RUN / "probes/s1-probe.json"))
    profile_probe = old.probe_profiles()
    probe_names = ("unspecified-probe", "risk-probe", "s1-probe", "senses-probe", "senses-document-probe", "discourse-probe", "rights-reading-probe")
    probe_same = {n: (RUN / f"probes/{n}.json").read_bytes() == (PREV_DIR / f"probes/{n}.json").read_bytes() for n in probe_names}
    rights = json.load(open(RUN / "probes/rights-reading-probe.json"))

    comp = json.load(open(RUN / "probes/companion-probe.json"))
    comp_ok = comp["attempts"]["without_source_word"]
    comp_bad = comp["attempts"]["with_source_word"]
    assert comp_ok["check"]["returncode"] == 0 and comp_bad["check"]["returncode"] == 5
    comp_share = comp_ok["lean_decided_share"]
    comp_q_same = {}
    comp_q = {}
    for name in ("no-denial", "no-denial-under-0", "no-denial-under-1", "claim-human"):
        d = json.load(open(RUN / f"probes/companion/query-{name}.json"))
        comp_q_same[name] = (RUN / f"probes/companion/query-{name}.json").read_bytes() == (PREV_DIR / f"probes/companion/query-{name}.json").read_bytes()
        comp_q[name] = {"verdict": d["verdict"], "route": d["route"], "component": d["component"], "decided_units": len(d["decided_units"]), "english": d["english"]}

    asks = [json.load(open(RUN / f"probes/ask/q{i}.json")) for i in range(1, 6)]
    ask_questions = [(RUN / f"probes/ask/q{i}.question.txt").read_text().strip() for i in range(1, 6)]
    ask_read = sum(1 for a in asks if a["result"].get("status") != "none")

    cv = copy.deepcopy(prev_metrics["check_verdicts"])
    cv["main"] = {"document_loaded": True, "coverage_percent": coverage["coverage_percent"],
                  "premises": {k: check["premises"][k] for k in ("status", "route", "evidence")},
                  "premises_gaps": check["premises"].get("gaps"),
                  "reading_plan": {"route": check["reading_plan"]["route"], "choice_count": len(check["reading_plan"]["choices"]),
                                   "conditional_on": check["reading_plan"].get("conditional_on")},
                  "conflict": {"route": check["readings"]["route"], "status": check["readings"]["conflict"]["status"], "evidence": check["readings"]["conflict"].get("evidence"),
                               "status_text": check["readings"]["status"], "choices": dict(Counter(c["status"] for c in check["readings"]["conflict"]["choices"])),
                               "sizes": check["readings"].get("sizes"), "english": check["readings"]["english"]},
                  "previous_run": {"premises_route": prev_check["premises"]["route"], "conflict_route": prev_check["readings"]["route"], "conflict_status_text": prev_check["readings"]["status"],
                                   "not_superposable": prev_check["readings"].get("not_superposable"), "english": prev_check["readings"]["english"]},
                  "residual": coverage["residual"], "norm_defaults": check["norm_defaults"],
                  "verdict_fields_identical_to_previous_run": check_same,
                  "what_changed": "the route, not the verdicts: at ve-green-arch-AR-6 the four 'should' sets could not be superposed under the unspecified completion ('ReadingsNotSuperposable ... the unspecified completion') "
                                  "and VE checked the 16 choices one at a time; at ve-green-arch-AR-8 (readings-defaults RD-6b) it checks all 16 together on one superposed document "
                                  "(route 'superposed', 199 nodes, 69 predicates). Verdicts are the same: premises model, conflict-free (all 16 choices CONFLICT-FREE), 16 choices, enumerated reading plan."}
    cv["all_strict"].update({"premises": strict["check"]["premises"], "residual": strict["coverage"]["residual"],
                             "bytes_by_status": strict["coverage"]["bytes_by_status"]})
    m = copy.deepcopy(prev_metrics)
    open_terms = [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")} for t in main_meta["open_terms"]]
    assert open_terms == prev_metrics["open_terms"]
    sup_before = prev_metrics["checked_content_main_chain"]["documents"]["all"]
    m.update({
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "previous_runs_note": "run 20261010T1800Z is the previous run's own output (usecases/claude-constitution-pilot/run-20261010T1800Z); its audit is AUDIT-20261010T1800Z-received.md; "
                              "prev/ here holds the files this run starts from and compares with",
        "changed_units": [],
        "changed_units_note": "none: no unit was added, changed or repaired. The previous audit found no unit unfaithful, and no merged feature newly expresses a unit",
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": old.full(u), "bytes_by_status": old.full(nb),
                                  "previous_run": {k: prev_metrics["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units, "bytes_by_substatus": old.full(nb),
                                              "previous_run": {k: prev_metrics["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")}},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": prev_metrics["claimed_covered_bytes"], "claimed_covered_bytes_gained": claimed - prev_metrics["claimed_covered_bytes"],
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"], "substantive_covered_bytes_previous_run": prev_metrics["substantive_covered_bytes"],
        "audit_verified_covered_bytes": verified_bytes, "audit_verified_covered_percent": round(100 * verified_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified, "audit_verified_covered_bytes_previous_run": prev_metrics["audit_verified_covered_bytes"],
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run to the form that audit saw. The audit of run 20261010T1800Z "
            "(20/20 sampled faithful, 11/11 changed units faithful; no unit unfaithful) accepted u0036.s05, u0125.s04.p2, u0156.s03, u0263.s04.p2 (the whole reading sets), u0052.s01, u0073.s05, u0168.s01, u0248, "
            "the four operator units u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03 and the seven hard-constraint units u0165.s01 to u0165.s07 (the eleven repaired in that run), and the labels "
            "u0095.heading, u0126, u0143.heading, u0174.heading, u0245.heading, u0257.heading, u0294. This run's translation, ledger and open terms are byte-identical to the form that audit saw, "
            "so all of them count: " + str(prev_metrics["audit_verified_covered_bytes"]) + " -> " + str(verified_bytes) + " bytes of CHECKED/OPEN/READINGS, and the verified labels "
            + str(prev_metrics["audit_verified_metadata_bytes"]) + " -> " + str(verified_meta) + " bytes. Nothing this run changed is audit-verified, because this run changed no unit."),
        "audit_verified_newly_from_20261010T1800Z": newly, "audit_verified_newly_label_units_from_20261010T1800Z": newly_lab,
        "audit_verified_dropped_now": [],
        "audit_verified_metadata_bytes_previous_run": prev_metrics["audit_verified_metadata_bytes"],
        "audit_verified_metadata_bytes": verified_meta, "audit_verified_metadata_percent": round(100 * verified_meta / len(SOURCE), 4),
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "repaired_bytes_not_audit_verified": 0,
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261010T1800Z_audit": [],
            "repair_done_in_20261011T1800Z": "none needed: the audit of 20261010T1800Z found every sampled and changed unit faithful (AUDIT-20261010T1800Z-received.md)",
            "earlier": prev_metrics["audit_rejected_units_and_repair_status"]},
        "document_profiles": {"main": main_meta["environment"]["profiles"], "strict": front_matter(STRICT)["environment"]["profiles"]},
        "documents": {"translation": "translation.ve.md (the previous run's, byte for byte; the four 'should' reading sets carry content)", "without_content": "translation-without-content.ve.md",
                      "strict": "readings/all-strict.ve.md (carried: the source of the strict content of the four 'should' sets)", "slices": None,
                      "not_carried": "readings/all-default.ve.md, readings/s1.ve.md (soft-chain demonstrations; the probes that need them were run on the earlier runs' copies, then removed)",
                      "reproduced": "nd.py all re-built the translation from translation-without-content.ve.md at arch-AR-8: the output is byte-identical to translation.ve.md (cmp)"},
        "open_terms": open_terms, "open_terms_count": len(open_terms), "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "open_terms_added": [], "open_terms_removed_this_run": [], "open_terms_with_changed_factors": [],
        "reading_sets": {**prev_metrics["reading_sets"], "count_previous_run": 4, "candidates_previous_run": prev_metrics["reading_sets"]["candidates"], "choices_previous_run": 16,
                         "readings_from_the_words": {**{k: v for k, v in prev_metrics["reading_sets"]["readings_from_the_words"].items() if not k.startswith("checked_again")},
                                                     "checked_again_20261011T1800Z": "no reading was added, removed or edited; the four sets are the 20261010T1800Z sets, which that audit found faithful "
                                                                                     "(each cites the document's own account of 'should' or its statement that these are almost hard constraints); the other units have one reading each"}},
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
        "renderings_identical_to_previous_run": {"raw": render_same, "why": "byte-identical: no unit, content or reading changed, and the rendering does not show the route"},
        "senses_probe": {**prev_metrics["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-probe"]},
        "senses_document_probe": {**prev_metrics["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-document-probe"]},
        "discourse_probe": {**prev_metrics["discourse_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["discourse-probe"],
                            "difference": "none: byte-identical to the previous run's JSON at ve-green-arch-AR-6"},
        "rights_reading_probe": {**rights, "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["rights-reading-probe"],
                                 "difference": "none: byte-identical to the previous run's JSON at ve-green-arch-AR-6"},
        "s1": {**prev_metrics["s1"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"]},
        "readings_defaults_probe": {**prev_metrics["readings_defaults_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"],
                                    "outcome": {"a_main_with_readings@1": "accepted; premises UNKNOWN (no set carries content)",
                                                "b_main_with_one_strict_norm_candidate": "accepted (premises UNKNOWN: the other sets are pending)",
                                                "c_s1_document_with_norm_defaults@0": s1_probe["c_s1_document_with_norm_defaults@0"]["rejection"]}},
        "lean_decided_share": {"decided_bytes": 0, "decided_share_percent": "0.00", "script": "tools/lean_decided_share.py",
                               "meaning": "units whose every verdict is a Lean answer that is not UNKNOWN across readings. For the translation itself (no companion set) it is still 0.00% at ve-green-arch-AR-8: "
                                          "`ve document check` reports no `decided_units` (basis: 'no Lean answer across readings'), also on the new superposed route",
                               "with_companion_sets": {"document": "probes/companion/translation-companions-without_source_word.ve.md", "decided_units": len(comp_share["decided_units"]),
                                                       "decided_bytes": comp_share["decided_bytes"], "decided_share_percent": comp_share["decided_share_percent"],
                                                       "units": comp_share["decided_units"],
                                                       "caveat": "a probe document, not the translation; each of the four 'should' sets is checked by itself as a component (VE says so in its English), "
                                                                 "and a rule checked by itself is CONFLICT-FREE by construction (lean_decided_share's own caveat)"}},
        "companion_probe": {**prev_metrics["companion_probe"], "re_run_at_this_tag": True,
                            "refusal_with_source_word": comp_bad["check"]["stdout_error"], "defect_still_present_at_arch_AR_8": True,
                            "route": comp_ok["summary"]["route"], "components": comp_ok["summary"]["components"], "conflict": comp_ok["summary"]["conflict"], "premises": comp_ok["summary"]["premises"],
                            "premises_components": comp_ok["summary"]["premises_components"], "separations": comp_ok["summary"]["separations"],
                            "decided_units": len(comp_share["decided_units"]), "decided_bytes": comp_share["decided_bytes"], "decided_share_percent": comp_share["decided_share_percent"],
                            "queries": comp_q, "query_files_identical_to_previous_run": comp_q_same,
                            "plain_route_for_comparison": {"denial_across_readings": concl_force["across_all_readings"]["verdict"], "denial_under_strict": concl_force["under_strict"]["verdict"],
                                                           "denial_under_defeasible": concl_force["under_defeasible"]["verdict"], "claim_human": concl_op["across_all_readings"]["verdict"]},
                            "reading": "unchanged by RD-6b: the companion route still decides the denial query (ALL / NONE / SOME) and the plain route, now superposed, still answers UNKNOWN across readings and under the defeasible reading"},
        "checked_content_main_chain": {
            **{k: v for k, v in prev_cc.items() if k not in ("documents", "choices_checked_one_at_a_time", "choices_conflict_free", "choices_conflict", "separating_situations_checked_by_lean",
                                                             "conclusion_probe", "conclusion_probe_operators", "conclusion_probes_identical_to_previous_run", "candidate_premise_status",
                                                             "all_four_in_one_document", "not_representable", "premises_unknown")},
            "documents": nd, "candidate_premise_status": dict(cand_status), "choices_checked": nd["all"]["choices_checked"],
            "choices_conflict_free": nd["all"]["conflict_by_choice"].get("CONFLICT-FREE", 0), "choices_conflict": nd["all"]["conflict_by_choice"].get("CONFLICT", 0),
            "choices_checked_one_at_a_time": 0, "separating_situations_checked_by_lean": sep_all, "separated_by_decision_only_findings": 0,
            "all_four_in_one_document": {"admitted": nd["all"]["admitted"], "choices": nd["all"]["choice_count"], "budget": 64, "verdict": nd["all"]["conflict_text"],
                                         "separations": nd["all"]["separations"], "route": nd["all"]["route"], "sizes": nd["all"]["sizes"]},
            "route_change": {"before": {"route": sup_before["route"], "not_superposable": sup_before["not_superposable"], "status": sup_before["conflict_text"], "choices_checked": sup_before["choices_checked"],
                                        "check_seconds": sup_before["check_seconds"], "separation_search_seconds": sup_before["separation_search_seconds"]},
                             "now": {"route": nd["all"]["route"], "not_superposable": nd["all"]["not_superposable"], "status": nd["all"]["conflict_text"], "choices_checked": nd["all"]["choices_checked"],
                                     "check_seconds": nd["all"]["check_seconds"], "separation_search_seconds": nd["all"]["separation_search_seconds"]},
                             "verdicts_same": True,
                             "timing_note": "single runs on one machine, not a controlled comparison. RD-6b's own saved evidence (docs/readings-defaults/rd6b/DELTA.md): its 29 changed pilot documents took 721 s in total against 1,076 s on the base, but 6 were more than 20% slower, three of them earlier documents of this pilot (nd-s01p1, nd-force, nd-op) that the DRI is to review"},
            "conclusion_probe": {"query": prev_cc["conclusion_probe"]["query"], "results": concl_force,
                                 "previous_run_results": prev_force_results},
            "conclusion_probe_operators": {"query": prev_cc["conclusion_probe_operators"]["query"], "results": concl_op, "previous_run_results": prev_op,
                                           "reading": "ALL: with one reading of u0123.s03 the prohibition holds whenever"},
            "conclusion_probes_identical_to_previous_run": {"verdicts_equal": True, "routes_now": routes_now,
                                                            "route_before": "enumerated (all four queries)",
                                                            "english_changed": "the UNKNOWN answers (denial across readings; denial under the defeasible reading) no longer carry the "
                                                                               "'Read sentence 132 as ... : VE could not check whether the conclusion follows' line: the superposed route gives no English for a gated UNKNOWN "
                                                                               "(docs/spec/readings-defaults.md says so; follow-up work). The ALL/NONE answers gain 'This does not depend on how sentence N is read.' lines",
                                                            "english_now": {k: v.get("english") for k, v in both.items()}},
            "not_representable": [
                "defeasibility beside norm-defaults@0 as VE's own mode: probe c still refuses norm-defaults@0 with soft-norms@0 ('await the Lean route')",
                "decided units for a document without companion sets: `decided_units` is reported only by the companion (product) route; the translation itself stays 0.00%",
                "companion sets together with `source_word`: refused with CheckerUnavailable (a Python defect, still present at arch-AR-8)",
                "English for a gated UNKNOWN conclusion on the superposed route (spec: follow-up work)"],
            "premises_unknown": {"candidates": [k for k, v in nd["all"]["premises_by_candidate"].items() if v != "model"], "why": "none: every candidate has a model"}},
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "unchanged_entries": len(ledger),
            "changed_or_replaced_ids": [], "added_ids": [], "units_newly_covered": [], "units_with_status_change": {},
            "units_changed_by_audit_repair": [], "open_terms_with_changed_factors": [],
            "reason": "the audit of 20261010T1800Z found no unfaithful unit; RD-6b and AR-8 do not change what a document can say. The translation is byte-identical to the previous run's"},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {
                "readings-defaults/rd6b (RD-6b)": "the superposed route under the unspecified completion: a document whose reading sets carry norm-defaults content is checked on one superposed document "
                                                  "(conflict, certificate, model) instead of one choice at a time; the enumerated route remains where the document is not superposable; sizes and limits reported "
                                                  "(`sizes`: nodes, predicates, sorts); per-choice conflict statuses listed; the old sentence 'checked one way at a time' is dropped on this route",
                "infra/arch-AR-8": "Rust crate-boundary check, facade lib.rs rules, gate collection; no change to what a document can say"},
            "newly_expressible_features": 0, "newly_expressible": "no new meaning: RD-6b changes how reading sets are checked, not what a document can say",
            "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "newly_measurable": "the translation's four 'should' sets now check on the superposed route (the previous tag refused: ReadingsNotSuperposable, the unspecified completion); same verdicts",
            "what_made_the_difference": "nothing in this run changed a unit; the route changed"},
        "question_probe": {
            "what": "`ve ask --reading --json` (question-answering Q1; answering is not built) on the translation: five yes-or-no questions about the denial, clarification and claim-to-be-human units (probes/ask/, question text in q*.question.txt)",
            "questions": ask_questions, "read": ask_read, "no_reading": [a["result"]["text"] for a in asks],
            "reading": "none of the five is read: the reader accepts only the controlled English of the document's vocabulary (it does not know 'must not', 'must seek clarification in each situation', 'each situation' as phrases). "
                       "Questions are not part of the language the units are written in; this changes no unit"},
        "reading_set_gaps": [
            {"gap": "a defeasible rule beside norm-defaults@0 (soft-norms@0 with norm-defaults@0 is refused, probe c)", "feature": "defaults", "workaround": "one named exception predicate per set, used as an `unless` (an open term)"},
            {"gap": "decided units are reported only for a document with companion sets; a set with `source_word` fails there", "feature": "other:RD-4b-report", "workaround": "a probe document without `source_word` (companion_probe)"},
            {"gap": "“cannot be unlocked by any operator or user”: who has authority to change what a norm requires; the language has no typed authority/modal (“can”, “cannot”, “may” as ability, permission or authority)", "feature": "modality/belief", "workaround": "the clause is UNFORMALISED; its effect is carried by the hard constraints' exception-free rules"},
            {"gap": "an exception the text does not name is an open term the translator names (exception_to_*), four open terms", "feature": "other:graded-force", "workaround": "recorded as open terms with 'the source names no exception' as their only factor"},
            {"gap": "the superposed route gives no English for a gated UNKNOWN conclusion (the enumerated route did)", "feature": "other:superposed-unknown-english", "workaround": "none needed for the translation; the query is read from the verdict and route"}],
        "carried_probes_note": "all seven carried probes re-run at this tag; byte-identical JSON: " + ", ".join(k for k, v in probe_same.items() if v) +
                               "; differs: " + ", ".join(k for k, v in probe_same.items() if not v),
    })
    dump("metrics.json", m)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent",
                                         "audit_verified_metadata_bytes", "claimed_but_not_audit_verified_bytes", "changed_units")}))
    print(dict(u), dict(nb))
    print("render same:", render_same, "check same:", check_same, "probe_same:", probe_same, "profile probe same:", m["profile_combination_probe_same_as_previous_run"])
    print("ask read:", ask_read, "companion q same:", comp_q_same, "routes:", routes_now)


if __name__ == "__main__":
    main()
