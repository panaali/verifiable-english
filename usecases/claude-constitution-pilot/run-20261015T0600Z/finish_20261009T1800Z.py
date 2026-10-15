#!/usr/bin/env python3
"""Run 20261009T1800Z: re-run VE at ve-green-rd-3, write the ledger, renderings and metrics.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python usecases/claude-constitution-pilot/run-20261009T1800Z/repair_20261009T1800Z.py   # base/ + prev/ -> translation-without-content.ve.md, units.json
    uv run python .../nd.py all (then force, op)          # readings/nd-all.ve.md becomes translation.ve.md; about 2 min each
    cp readings/nd-all.ve.md translation.ve.md && rm readings/nd-all.ve.md
    for g in force op all; do uv run python -m ve document coverage ... > readings/coverage-nd-$g.json; done
    probes (README.md), conclusion queries (probes/nd/, README.md)
    uv run python .../finish_20261009T1800Z.py            # about 3 min

The translation is the previous run's (20261009T0600Z), with the five units its audit rejected repaired (AUDIT-REPAIR.md) and the
operator sets' wide candidate stated on the instructed behaviour. No unit gains a covered status from a new feature.
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

RUN_ID = "20261009T1800Z"
PREV_RUN = "20261009T0600Z"
TAG = "ve-green-rd-3"
PREV_TAG = "ve-green-lf-17"
COVERED = old.COVERED
SOURCE = old.SOURCE
ve, front_matter = old.ve, old.front_matter
dump = lambda p, o: (RUN / p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")
PREV_DIR = RUN.parent / f"run-{PREV_RUN}"
MAIN = RUN / "translation.ve.md"
STRICT = RUN / "readings/all-strict.ve.md"
SETS = {  # unit -> (set, slice document that also carries the set)
    "u0036.s05": ("force-u0036-s05", "nd-force"), "u0125.s04.p2": ("force-u0125-s04-p2", "nd-force"),
    "u0156.s03": ("force-u0156-s03", "nd-force"), "u0263.s04.p2": ("force-u0263-s04-p2", "nd-force"),
    "u0062.s01": ("modal-u0062-s01", "nd-op"), "u0123.s01.p1": ("modal-u0123-s01-p1", "nd-op"),
    "u0123.s02.p1": ("modal-u0123-s02-p1", "nd-op"), "u0123.s03": ("scope-modal-u0123-s03", "nd-op")}
FORCE_UNITS = ["u0036.s05", "u0125.s04.p2", "u0156.s03", "u0263.s04.p2"]
OP_UNITS = ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03"]
AUDIT_REJECTED_0600 = ["u0166.s04.p4", "u0165.s03", "u0123.s01.p1", "u0123.s03", "u0062.s01"]
AUDIT_FAITHFUL_0600_SUBSTANTIVE = ["u0248", "u0165.s05", "u0052.s01", "u0168.s01", "u0165.s02", "u0125.s04.p2", "u0156.s03", "u0263.s04.p2"]
# the changed units: the five the audit rejected, plus u0123.s02.p1 (the same set of four: its wide candidate changes with theirs)
CHANGED = sorted(AUDIT_REJECTED_0600 + ["u0123.s02.p1"])
REMOVED_PREDICATES = ["operator_unlocks", "user_unlocks"]


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
    ledger = json.load(open(RUN / "units.json"))   # written by repair_20261009T1800Z.py
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
    assert unit_diff == ["u0166.s04.p4"], unit_diff
    pv = prev_main["environment"]["vocabulary"]["predicates"]
    nv = main_meta["environment"]["vocabulary"]["predicates"]
    pred_gone = sorted(k for k in pv if k not in nv)
    pred_new = sorted(k for k in nv if k not in pv)
    assert pred_gone == sorted(REMOVED_PREDICATES + ["instruction_given_while_role_playing_persona"]), pred_gone
    assert pred_new == ["instruction_is_for_behaviour_while_role_playing_persona"], pred_new
    assert {k: v for k, v in nv.items() if k in pv} == {k: v for k, v in pv.items() if k in nv}
    # the force sets are exactly as the audit of 20261009T0600Z saw them
    prev_sets = {s["id"]: s for s in prev_main["reading_sets"]}
    def set_form(item):   # what a reader sees of a set; the identifiers (meaning ids, situation keys) change with the environment's, which lost two relations
        return {k: ([{kk: vv for kk, vv in r.items() if kk not in ("meaning_id", "admission")} | {"why": r["admission"]["why"], "who": r["admission"]["who"]}
                     for r in v] if k == "readings" else v) for k, v in item.items() if k not in ("situations", "models")}
    same_set = {i: set_form(front_set(main_meta, SETS[i][0])) == set_form(prev_sets[SETS[i][0]]) for i in SETS}
    assert all(same_set[i] for i in FORCE_UNITS), same_set
    assert not any(same_set[i] for i in OP_UNITS), same_set

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
    assert check["reading_plan"]["route"] == "enumerate" and len(check["reading_plan"]["choices"]) == 32
    prev_check = json.load(open(PREV_DIR / "check.json"))

    def same_except(a, b, skip):
        return all(a.get(k) == b.get(k) for k in set(a) | set(b) if k not in skip)

    check_same_as_previous = same_except(check, prev_check, {"coverage", "residual", "readings"})

    # ---- ledger: the notes of the eight sets were written by 20261009T0600Z's finish and by repair_20261009T1800Z.py; nothing is appended here
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE)
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    u, nb = old.counts(ledger)
    claimed = sum(v for k, v in nb.items() if k in COVERED)
    assert claimed == prev_metrics["claimed_covered_bytes"] - 45, claimed
    n_old, old_units, _ = old.aggregate(ledger)
    spans = {e["id"]: e["span"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)

    # ---- audit-verified bytes: accepted by an audit AND byte-identical in this run to the form it saw
    prev_verified = list(prev_metrics["audit_verified_covered_units"])
    rejected_now = [i for i in prev_verified if i in AUDIT_REJECTED_0600]          # u0166.s04.p4, u0165.s03 (accepted by earlier audits, rejected now)
    assert sorted(rejected_now) == ["u0165.s03", "u0166.s04.p4"], rejected_now
    keep = [i for i in prev_verified if i not in rejected_now]
    for i in keep:   # unchanged since the audit that accepted them
        assert by_id[i] == by_prev[i] and i not in unit_diff, i
    # accepted by the 20261009T0600Z audit in the form it saw; byte-identical here (ledger entry, document unit, and for a set the whole set)
    newly = [i for i in AUDIT_FAITHFUL_0600_SUBSTANTIVE if i not in keep]
    for i in newly:
        assert by_id[i] == by_prev[i] and i not in unit_diff and (i not in SETS or same_set[i]), i
    verified = list(dict.fromkeys(keep + newly))
    assert all(by_id[i]["status"] in COVERED for i in verified)
    verified_bytes = width(verified)
    verified_before = prev_metrics["audit_verified_covered_bytes"]
    assert verified_bytes == verified_before - width(rejected_now) + width(newly), (verified_bytes, verified_before)
    awaiting = ["u0036.s05"]   # accepted by the 20261008T1800Z audit in a form without content; the set now carries content and was not sampled again
    repaired_bytes = width(CHANGED)
    verified_meta = prev_metrics["audit_verified_metadata_bytes"]   # the 20261009T0600Z audit's labels were all verified already (checked in README: 345 bytes)

    nd = {g: slice_result(g) for g in ("force", "op", "all")}
    for g in ("force", "op", "all"):
        assert nd[g]["conflict"] == "CONFLICT-FREE" and nd[g]["premises"] == "model"
    sep_all = sum(nd["all"]["separations"].values())
    assert sep_all == sum(sum(nd[g]["separations"].values()) for g in ("force", "op"))
    assert nd["all"]["choice_count"] == 32 == nd["force"]["choice_count"] * nd["op"]["choice_count"]
    cand_status = Counter(nd["all"]["premises_by_candidate"].values())

    concl_force = concl((("across_all_readings", "conclusion-no-denial-result.json"), ("under_strict", "conclusion-no-denial-under-0.json"),
                         ("under_defeasible", "conclusion-no-denial-under-1.json"), ("across_all_readings_in_the_translation", "conclusion-no-denial-all.json")))
    concl_op = concl((("across_all_readings", "claim-human-result.json"), ("under_narrow_scope", "claim-human-under-0.json"),
                      ("under_wide_scope", "claim-human-under-1.json")))
    assert concl_op["under_narrow_scope"]["verdict"] == "ALL" and concl_op["under_wide_scope"]["verdict"] == "UNKNOWN"
    prev_cc = prev_metrics["checked_content_main_chain"]
    concl_same = (concl_force == prev_cc["conclusion_probe"]["results"] and concl_op == prev_cc["conclusion_probe_operators"]["results"])

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
                  "what_changed": "same verdicts as the previous run (premises model in all 32 choices, enumerated reading plan, conflict-free); "
                                  f"open terms 36 -> {len(main_meta['open_terms'])} (-operator_unlocks, -user_unlocks; the wide-scope term renamed to "
                                  "instruction_is_for_behaviour_while_role_playing_persona), assumptions 20 -> 19; the check runs in about 80 s "
                                  "(about 5 minutes at ve-green-lf-17: RD-3 moved the enumerated folds to Lean)",
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
        "previous_runs_note": "run 20261009T0600Z is the previous run's own output (usecases/claude-constitution-pilot/run-20261009T0600Z on branch pilot/cc-20261009T0600Z, with its AUDIT.md)",
        "changed_units": CHANGED,
        "changed_units_note": {
            "u0166.s04.p4": "OPEN (ability statement) -> UNFORMALISED (modality/belief); audit 20261009T0600Z rejected the ability statement",
            "u0165.s03": "OPEN term lost the factor 'how likely deployment must be' (audit)",
            "u0123.s03": "READINGS: the wide candidate states the role-play condition on the instructed behaviour (audit)",
            "u0123.s01.p1": "READINGS: the wide candidate's exception, same fix (audit)",
            "u0062.s01": "READINGS: the wide candidate's exception, same fix (audit)",
            "u0123.s02.p1": "READINGS: the wide candidate's exception, same fix (the fourth set of the coupled four; not in the audit's sample)"},
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
            "20261009T0600Z (15/20 faithful) rejected u0166.s04.p4 and u0165.s03 (accepted by earlier audits: they leave the list) and u0123.s01.p1, u0123.s03, u0062.s01 (already off it). "
            "It accepted u0125.s04.p2, u0156.s03 and u0263.s04.p2 in the form with content that this run keeps byte for byte (ledger entry, document unit, whole reading set), so they join; "
            "u0165.s05, u0165.s02, u0168.s01, u0052.s01 and u0248 were verified already. u0036.s05 was accepted by the 20261008T1800Z audit in a form without content and now carries content: it waits "
            "for a re-audit. The headings and labels that audit accepted were verified already (metadata bytes stay 345). Nothing this run changed is audit-verified."),
        "audit_verified_dropped_because_changed_or_rejected": {**prev_metrics["audit_verified_dropped_because_changed_or_rejected"],
                                                               "rejected_by_20261009T0600Z_audit_and_dropped_now": rejected_now,
                                                               "rejected_by_20261009T0600Z_audit_never_verified": ["u0123.s01.p1", "u0123.s03", "u0062.s01"],
                                                               "accepted_20261008T1800Z_but_content_added_awaiting_re_audit": awaiting},
        "audit_verified_newly_from_20261009T0600Z": [i for i in newly], "audit_verified_newly_label_units_from_20261009T0600Z": [],
        "audit_verified_metadata_bytes": verified_meta,
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "repaired_bytes_not_audit_verified": repaired_bytes,
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261009T0600Z_audit": AUDIT_REJECTED_0600,
            "repair_done_in_20261009T1800Z": "see AUDIT-REPAIR.md: u0165.s03 and two operator terms lose an invented 'how likely' factor; u0166.s04.p4 becomes UNFORMALISED (modality/belief); "
                                            "the wide candidate of the four operator sets states the role-play condition on the instructed behaviour",
            "repaired_and_not_yet_sampled": AUDIT_REJECTED_0600, "earlier": prev_metrics["audit_rejected_units_and_repair_status"]},
        "document_profiles": {"main": main_meta["environment"]["profiles"], "strict": front_matter(STRICT)["environment"]["profiles"]},
        "documents": {"translation": "translation.ve.md (the previous run's, repaired; every reading set carries content)", "without_content": "translation-without-content.ve.md",
                      "strict": "readings/all-strict.ve.md (carried: the source of the strict content of the four 'should' sets)",
                      "slices": {"force": "readings/nd-force.ve.md", "op": "readings/nd-op.ve.md"},
                      "not_carried": "readings/all-default.ve.md, readings/s1.ve.md (soft-chain demonstrations; the probes that need them were run on the earlier runs' copies, then removed)"},
        "open_terms": open_terms, "open_terms_count": len(open_terms), "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "open_terms_added": new_terms, "open_terms_removed_this_run": gone_terms, "open_term_factors_removed": {
            "damaging_cyberweapon_or_malicious_code": "how likely deployment must be for the damage to count as one that could happen",
            "instruction_deceptive_tactics_harming_users": "how likely harm must be for the tactics to be ones that could harm users",
            "instruction_false_information_deceiving_user": "how likely deception must be for the information to be information that could deceive"},
        "open_terms_with_changed_factors": factors_changed,
        "reading_sets": {"count": 8, "unresolved": 8, "count_previous_run": 8,
                         "candidates": {s.get("unit"): [r["id"] for r in s["readings"]] for s in main_meta["reading_sets"]},
                         "candidates_previous_run": prev_metrics["reading_sets"]["candidates"],
                         "units": [s["unit"] for s in main_meta["reading_sets"]], "couplings": [c["id"] for c in main_meta["couplings"]],
                         "narrowings": [], "choices": 32, "choices_previous_run_if_unlinked": 144,
                         "readings_from_the_words": {**prev_metrics["reading_sets"]["readings_from_the_words"],
                                                     "checked_again_20261009T1800Z": (
                                                         "every candidate of the eight sets was re-read against the words-only rule: the four 'should' sets cite the document's own "
                                                         "account of 'should' (u0253.s04, u0011.s01); the four operator sets hold only the two attachments of “while role-playing as a "
                                                         "custom AI persona”. No outside knowledge is used. Changed: the wide attachment now puts the role-play condition on the behaviour "
                                                         "the instruction asks for, not on the time it is given (audit 20261009T0600Z)."),
                                                     "scope_set": "u0062.s01, u0123.s01.p1, u0123.s02.p1 and u0123.s03: how far “while role-playing as a custom AI persona” reaches in "
                                                                  "u0123.s03 (the first item only, or every item), and what that does to the permissions the limits attach to; one coupled axis"}},
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
                                                 "why": "u0166.s04.p4 is unformalised (its fenced statement is gone), the wide candidates read differently, and the open terms lost their factors"},
        "senses_probe": {**prev_metrics["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-probe"]},
        "senses_document_probe": {**prev_metrics["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-document-probe"]},
        "discourse_probe": {**prev_metrics["discourse_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["discourse-probe"]},
        "rights_reading_probe": {**rights, "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["rights-reading-probe"],
                                 "difference": "same conclusion; two of the four diagnostics changed: a wire missing a generated soft__excepted__ table now crashes with a Python KeyError in "
                                               "ve/model.py (_decode, ve-green-rd-3) where it was refused by name ('relations must contain exactly the base predicates'); the other mismatch is "
                                               "refused with a longer InvalidModel message. A refusal became a crash: a defect in the tool, not in the translation"},
        "s1": {**prev_metrics["s1"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"],
               "historical_note": "figures and models of the soft-chain demonstration document of earlier runs (readings/s1.ve.md, not carried, not part of the translation); "
                                  "its model still names relations the translation no longer has (instruction_is_legitimate, instruction_given_while_role_playing_persona)"},
        "s2a": {**prev_metrics["s2a"], "re_run_at_this_tag": False,
                "note": "superseded: the same queries run on the translation itself (checked_content_main_chain.conclusion_probe_operators and conclusion_probe)"},
        "readings_defaults_probe": {**prev_metrics["readings_defaults_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"],
                                    "outcome": {"a_main_with_readings@1": "accepted; premises UNKNOWN (no set carries content)",
                                                "b_main_with_one_strict_norm_candidate": "accepted (premises UNKNOWN: the other sets are pending)",
                                                "c_s1_document_with_norm_defaults@0": s1_probe["c_s1_document_with_norm_defaults@0"]["rejection"]}},
        "lean_decided_share": {"decided_bytes": 0, "decided_share_percent": "0.00", "script": "tools/lean_decided_share.py",
                               "meaning": "units whose every verdict is a Lean answer that is not UNKNOWN across readings. Still 0.00% at ve-green-rd-3: RD-3 moved the enumerated folds to Lean "
                                          "(`readings-verdicts`), but neither `ve document check` nor any route reports the answer's `decided_units` (no code outside tools/lean_decided_share.py "
                                          "and its test mentions them; the Lean `setDecided` of spec 1.10 is not in lean/VE). The per-choice results and the conclusion queries are Lean's, but are not "
                                          "reported as decided units"},
        "checked_content_main_chain": {
            "what": "reading sets whose every candidate carries content that Lean checked on the main chain itself (norm-defaults@0, completion unspecified): readings@1 beside norm-defaults@0 (readings-defaults RD-2a/RD-2b) with one coupling",
            "script": "nd.py", "documents": nd, "the_translation_is_the_all_document": True,
            "reading_sets_with_checked_content": 8, "reading_sets_total": len(main_meta["reading_sets"]),
            "candidates_with_content": sum(len(s["candidates"]) for s in nd["all"]["sets"]), "candidates_total": sum(len(s["candidates"]) for s in nd["all"]["sets"]),
            "candidate_premise_status": dict(cand_status), "choices_checked_one_at_a_time": nd["all"]["choices_checked"],
            "choices_conflict_free": nd["all"]["choices_checked"], "choices_conflict": 0, "separating_situations_checked_by_lean": sep_all,
            "separated_by_decision_only_findings": 0,
            "all_eight_in_one_document": {"admitted": nd["all"]["admitted"], "choices": nd["all"]["choice_count"], "budget": 64, "verdict": nd["all"]["conflict_text"],
                                          "separations": nd["all"]["separations"]},
            "split": None,
            "conclusion_probe": {"query": "every instance of Claude is not permitted to directly deny being Claude (denial_of_being_claude_permitted)", "results": concl_force},
            "conclusion_probe_operators": {"query": "no operator is permitted to give Claude an operator input classified as an instruction to claim to be human when directly and sincerely asked "
                                                    "(forall operator, input: instruction_claim_human_when_asked(input) -> not operator_input_permitted(operator, input))",
                                           "results": concl_op,
                                           "reading": "ALL under the narrow scope (the prohibition holds whenever), UNKNOWN under the wide scope (it holds only for behaviour Claude is to carry out while role-playing a custom persona; nothing else decides): "
                                                      "the one ambiguity the words carry changes the answer, and VE does not pick"},
            "conclusion_probes_identical_to_previous_run": concl_same,
            "defeasible_candidates": "the soft chain's `exception: unstated` becomes one base predicate per set that is an open term (exception_to_*), used as an `unless`; the text names no exception",
            "not_representable": [
                "defeasibility beside norm-defaults@0 as VE's own mode: probe c still refuses norm-defaults@0 with soft-norms@0 ('await the Lean route')",
                "decided units: RD-3's `readings-verdicts` is merged, but its `decided_units` are not reported by the CLI or any route at this tag (lean_decided_share stays 0)",
                "the companion split (RD-4a) is merged in Lean but `ve document` still refuses a reading with `companion` (RD-4b): not used, and no longer needed here"],
            "premises_unknown": {"candidates": [k for k, v in nd["all"]["premises_by_candidate"].items() if v != "model"], "why": "none: every candidate has a model"}},
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "unchanged_entries": len(ledger) - len(CHANGED),
            "changed_or_replaced_ids": CHANGED, "added_ids": [], "units_newly_covered": [], "units_with_status_change": ["u0166.s04.p4"],
            "units_changed_by_note_only": [], "units_changed_by_audit_repair": CHANGED,
            "reason": "one status changes: u0166.s04.p4 OPEN -> UNFORMALISED (modality/belief), so claimed coverage falls by its 45 bytes (2,996 -> 2,951). The other five units keep their status; "
                      "their open terms or wide candidates are repaired. No unit is upgraded: no feature merged since lf-17 changes what a document can say."},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {
                "lean-first/b12 (lf-12)": "Lean validates every authored environment and model envelope before Python builds one (the Python profile gate and decoder refusals are deleted); "
                                          "a generated soft or rights search environment is built without Python's shape check, so the rights probe's refusal by name became a KeyError; no new form of text",
                "readings-defaults/rd3 (rd-3)": "RD-3: the enumerated route's conflict, premise and entailment folds, their three-valued gate, the restrictions and the English plan are Lean's (`readings-verdicts`); "
                                                 "the verdicts are the same and `ve document check` of the translation takes about 80 s instead of about 5 minutes. `decided_units` is not reported yet"},
            "newly_expressible_features": 0, "newly_expressible": "none: neither merged batch changes what a document can say",
            "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "what_made_the_difference": "not a feature: this run repairs units the audit rejected and applies the words-only rule again"},
        "reading_set_gaps": [
            {"gap": "a defeasible rule beside norm-defaults@0 (soft-norms@0 with norm-defaults@0 is refused, probe c)", "feature": "defaults", "workaround": "one named exception predicate per set, used as an `unless` (an open term)"},
            {"gap": "the folded verdicts are Lean's (RD-3) but the report has no decided units: `readings-verdicts` is merged and its `decided_units` are not surfaced", "feature": "other:RD-3-report", "workaround": "none needed for the per-choice results"},
            {"gap": "the scope of “while role-playing as a custom AI persona” is one ambiguity expressed four times (one candidate pair per set) tied by a coupling; a reading set cannot say that one sentence's reading is another's premise", "feature": "other:cross-set-dependence", "workaround": "coupling on a label axis"},
            {"gap": "“cannot be unlocked by any operator or user” is ability, permission or authority to override; the language has no typed modality to keep the ambiguity, and the duty and ability readings are excluded", "feature": "modality/belief", "workaround": "the clause is UNFORMALISED"},
            {"gap": "an exception the text does not name is an open term the translator names (exception_to_*), four open terms", "feature": "other:graded-force", "workaround": "recorded as open terms with 'the source names no exception' as their only factor"}],
        "carried_probes_note": "all seven carried probes re-run at this tag; byte-identical JSON: " + ", ".join(k for k, v in probe_same.items() if v) +
                               "; differs: " + ", ".join(k for k, v in probe_same.items() if not v),
    })
    dump("metrics.json", m)
    dump("units.json", ledger)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent", "claimed_but_not_audit_verified_bytes", "repaired_bytes_not_audit_verified", "changed_units")}))
    print(dict(u), dict(nb))
    print("changed render lines:", changed_render, "probe_same:", probe_same, "check same:", check_same_as_previous, "concl same:", concl_same)
    print("profile probe same:", m["profile_combination_probe_same_as_previous_run"])


if __name__ == "__main__":
    main()
