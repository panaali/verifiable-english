#!/usr/bin/env python3
"""Run 20261012T1800Z: repair of the five units the audit of run 20261012T0600Z rejected, then the measurement at ve-green-ts-B1.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python .../repair_20261012T1800Z.py            # base/ -> translation-without-content.ve.md, readings/all-strict.ve.md
    uv run python .../nd.py all                           # about 1 min; then: mv readings/nd-all.ve.md translation.ve.md
    uv run python -m ve document coverage .../translation.ve.md > .../readings/coverage-nd-all.json
    probes (README.md)
    uv run python .../finish_20261012T1800Z.py            # ledger (units.json), renderings, check, coverage, metrics.json

The previous run's translation is `prev/translation.ve.md`; the units this run changed are in CHANGED below.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))
import finish_0600 as old  # noqa: E402
import finish_20261012T0600Z as prevf  # noqa: E402  (slice_result, concl: readers of the nd result and conclusion files)

RUN_ID = "20261012T1800Z"
PREV_RUN = "20261012T0600Z"
TAG = "ve-green-ts-B1"
PREV_TAG = "ve-green-devtime-1"
COVERED = old.COVERED
SOURCE = old.SOURCE
ve, front_matter = old.ve, old.front_matter
dump = lambda p, o: (RUN / p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")
PREV_DIR = RUN / "prev"
MAIN = RUN / "translation.ve.md"
STRICT = RUN / "readings/all-strict.ve.md"
KNOW = "restricted_action_knowing_or_quite_likely"
HC_UNITS = [f"u0165.s0{i}" for i in range(1, 8)]
U0125 = "u0125.s04.p2"
SETS_KEPT = ["u0036.s05", "u0156.s03", "u0263.s04.p2"]
U0173 = "u0173.s01"
CHANGED = [U0125, *HC_UNITS, *SETS_KEPT, U0173]

# the audit of run 20261012T0600Z (15/20 sampled faithful, 0/0 changed), verdicts as received (AUDIT-20261012T0600Z-received.md)
AUDIT_0600_FAITHFUL = ["u0008.heading", "u0023", "u0027.heading", "u0036.s05", "u0052.s01", "u0062.s01", "u0069.heading", "u0073.s05", "u0095.heading",
                       "u0103", "u0156.s03", "u0248", "u0260.heading", "u0263.s04.p2", "u0265"]
AUDIT_0600_UNFAITHFUL = [U0125, "u0165.s02", "u0165.s03", "u0165.s05", "u0165.s07"]

U0125_NOTE = (
    "“Claude should never directly deny that it is Claude” is read as a prohibition on instances of Claude: the act is Claude directly denying that it is "
    "Claude. Written as a permission predicate with a negative rule, scoped to instances of Claude (the party the source names), completion `unspecified`: "
    "the rule makes nothing permitted or forbidden for any other party. One reading: “never” excludes exceptions and the words state none; the next clause "
    "gives the reason (“as that would cross the line into deception that could seriously mislead the user”, u0125.s04.p3, UNFORMALISED: causation), and "
    "u0170.s01 says the list of hard constraints “is not a list of all the behaviors we think Claude should never exhibit”. “Directly” is part of the act "
    "as the source words it; the source gives no test for where a direct denial ends, and no open term is added for it (the act is one primitive of the "
    "vocabulary).")
U0125_REPAIR = (
    "Audit 20261012T0600Z (u0125.s04.p2 UNFAITHFUL): the defeasible candidate invented an exception to “should never directly deny that it is Claude”. "
    "“Claude should basically never directly lie or actively deceive anyone” (u0109.s06) is about honesty in general and names no exception to this specific "
    "prohibition, and u0170.s01 says the hard-constraint list does not exhaust the behaviours Claude should never exhibit. Repaired: the reading set, its "
    "defeasible candidate and its open term (the exception it needed) are removed; the unit has one reading, the strict prohibition, written as content on "
    "the unit; status CHECKED (no open term). Not audited.")
HC_ADD = (
    " Epistemic condition (audit 20261012T0600Z): u0173.s01 to s04 qualify the list. The hard constraints are “centrally meant to apply to cases where Claude "
    "would either be knowingly and intentionally engaging in an action of the relevant restricted category, or where Claude thinks it quite likely that a given "
    "action would fall into such a category” (u0173.s01); “for cases that are more unclear or uncertain” Claude is to be “guided by the more holistic and nuanced "
    "prioritization at stake in the rest of this document” (u0173.s02); the restriction is “the operative consideration only in a small number of flagrant "
    "cases” (u0173.s03); and Claude “could in principle end up contributing unknowingly to the sorts of outcomes the constraints aim to avoid … without "
    "actually violating one of the constraints” (u0173.s04). So the guard of the rule is the case atom AND the open term " + KNOW + " (one term for the seven "
    "rules, whose words are u0173.s01's). Where the guard does not hold the rule says nothing (completion `unspecified`): an unclear, uncertain or unknowing "
    "case is neither forbidden nor permitted by it. u0173.s01 to s04 stay UNFORMALISED (modality/belief; “quite likely” is a quantity); they are used, not claimed.")
HC_REPAIR = (
    "Audit 20261012T0600Z (u0165.s02, s03, s05 and s07 UNFAITHFUL; s01, s04 and s06 are the same class and repaired with them): the absolute prohibition depended on "
    "the action category alone and omitted u0173.s01 to s04's knowledge, intention and perceived-likelihood qualification. Repaired: the guard is the category "
    "case atom and the open term " + KNOW + "; the term's factors are the two the words leave open. Not audited.")
KNOW_CASE = ("the situation is a case in which Claude would be knowingly and intentionally engaging in an action of the relevant restricted category, or in which "
             "Claude thinks it quite likely that the action would fall into such a category")
SET_OLD = re.compile(r"the eight sets together have 32 compatible choices \(16 for the four force sets x 2 for the four operator sets, which a coupling on the "
                     r"label axis limits-scope ties to one scope\), all conflict-free; readings/nd-force\.ve\.md is the slice of the translation with this set's group\.")
SET_NEW = ("the three sets together have 8 compatible choices, all conflict-free (readings/nd-all-result.json and readings/nd-all-check.json are the records of "
           "that run).")
U0173_NOTE = ("Not claimed. Its words are used as the open term " + KNOW + " in the guards of the seven hard-constraint rules (u0165.s01 to u0165.s07), so that "
              "those rules do not go beyond it; the unit itself stays UNFORMALISED because knowing, intending and thinking something quite likely are not typed "
              "(modality/belief) and “quite likely” is a quantity.")


def update_ledger(prev, eng, silence, probe):
    ledger = copy.deepcopy(prev)
    pts = {p["label"]: p["status"] for p in probe["points"]}
    for e in ledger:
        i = e["id"]
        if i == U0125:
            for k in ("reading_set", "checked_content", "strict_reading_predicate", "defeasible_reading_predicate"):
                e.pop(k, None)
            e.update({
                "status": "CHECKED", "status_in_previous_run": "READINGS", "note": U0125_NOTE, "audit_repair": U0125_REPAIR, "repaired_in_run": RUN_ID,
                "audit_verified": False,
                "where_the_text_is_silent": silence["denial_of_being_claude_permitted"],
                "readings": [{"id": "only", "in": "translation.ve.md and readings/all-strict.ve.md", "predicate": "denial_of_being_claude_permitted",
                              "completion": "unspecified", "english": eng["no-denying-being-claude"]["text"],
                              "english_round_trip": eng["no-denying-being-claude"]["round_trip"],
                              "meaning": "a strict rule (a prohibition: a permission predicate with a negative rule)"}],
                "document_status": "CHECKED (one reading; no open term; norm-defaults@0, completion unspecified)"})
        elif i in HC_UNITS:
            assert e["status"] == "OPEN" and len(e["open_terms"]) == 1, i
            case_term = e["open_terms"][0]
            rule = e["rule"]
            e["open_terms"] = [case_term, KNOW]
            e["case_atoms"] = {**e["case_atoms"], KNOW: KNOW_CASE}
            e["note"] = e["note"] + HC_ADD
            e["audit_repair"] = e["audit_repair"] + " | " + HC_REPAIR
            e["repaired_in_run"] = RUN_ID
            e["audit_verified"] = False
            e["where_the_text_is_silent"] = silence[e["predicate"]]
            e["check"] = {
                "case holds and Claude knows or thinks it quite likely": pts[f"{i}: the case holds and Claude knowingly engages in it or thinks it quite likely"],
                "case holds, neither": pts[f"{i}: the case holds but neither knowingly nor thought quite likely"],
                "case does not hold": pts[f"{i}: the case does not hold"],
                "case does not hold, knowledge atom holds": pts[f"{i}: the case does not hold (the knowledge atom does)"],
                "meaning": "SETTLED no = the text says Claude may not; UNDECIDED = the text does not say (nothing is permitted or forbidden by default)"}
            e["readings"][0]["english"] = eng[rule]["text"]
            e["readings"][0]["english_round_trip"] = eng[rule]["round_trip"]
            e["readings"][0]["meaning"] = ("a strict rule: Claude may not do the act in a situation that is a case of the source's words AND one in which "
                                           "Claude knowingly and intentionally engages in it or thinks it quite likely (u0173.s01)")
            e["document_status"] = "OPEN (one strict reading; its case atom and its knowledge atom are open terms)"
        elif i in SETS_KEPT:
            assert SET_OLD.search(e["note"]), i
            e["note"] = SET_OLD.sub(SET_NEW, e["note"])
            e["checked_content"] = {"set": e["reading_set"], "document": "translation.ve.md", "record": "readings/nd-all-result.json, readings/nd-all-check.json"}
            e["repaired_in_run"] = RUN_ID
            e["note_edited_in_run"] = ("the count of compatible choices and the name of the slice document were out of date (a slice file that no longer exists); "
                                       "no reading or content changed")
        elif i == U0173:
            e["note"] = U0173_NOTE
    # no trace of the removed reading may remain in the ledger
    blob = json.dumps([e for e in ledger if e["id"] != U0125], ensure_ascii=False)
    for stale in ("force-u0125", "exception_to_never_denying", "denial_of_being_claude_avoidance_required", "32 compatible", "nd-force", "four force sets",
                  "four operator sets"):
        assert stale not in blob, stale
    own = json.dumps([e for e in ledger if e["id"] == U0125], ensure_ascii=False)
    for stale in ("force-u0125", "exception_to_never_denying", "avoidance_required", "nd-force"):
        assert stale not in own.replace(U0125_REPAIR, ""), stale
    return ledger


def annotate(text, ledger):
    """Under each one-reading prohibition of the hard constraints, print its source words and VE's verdicts."""
    lines, out = text.split("\n"), []
    by_english = {e["readings"][0]["english"]: e for e in ledger if e["id"] in HC_UNITS}
    done = set()
    for line in lines:
        out.append(line)
        m = re.match(r"^(Open|Checked) reading: (.*)$", line)
        if m and m.group(2) in by_english:
            e = by_english[m.group(2)]
            done.add(e["id"])
            c = e["check"]
            out.append(f"  Source words of the case (open term “{e['open_terms'][0]}”): {e['case_atoms'][e['open_terms'][0]]}.")
            out.append(f"  Source words of the knowledge condition (open term “{KNOW}”, u0173.s01): {KNOW_CASE}.")
            out.append(f"  VE: where both hold, {c['case holds and Claude knows or thinks it quite likely']}; where the case holds but the condition does not, "
                       f"{c['case holds, neither']}; where the case does not hold, {c['case does not hold']}. "
                       f"{e['where_the_text_is_silent'][0].upper() + e['where_the_text_is_silent'][1:]}.")
    assert done == set(HC_UNITS), done
    return "\n".join(out)


def main():
    prev = json.load(open(PREV_DIR / "units.json"))
    prev_metrics = json.load(open(PREV_DIR / "metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == prev_metrics["source_sha256"]
    eng = old.english_nd(STRICT)
    silence, legend = old.silence_sentences(STRICT)
    probe = json.load(open(RUN / "probes/unspecified-probe.json"))
    ledger = update_ledger(prev, eng, silence, probe)
    dump("units.json", ledger)
    by_id = {e["id"]: e for e in ledger}
    main_meta = front_matter(MAIN)
    assert [(u["id"], tuple(u["span"])) for u in main_meta["units"]] == [(e["id"], tuple(e["span"])) for e in ledger]
    assert [(e["id"], tuple(e["span"])) for e in prev] == [(e["id"], tuple(e["span"])) for e in ledger]

    # ---- VE runs at this tag
    rel = str(MAIN.relative_to(ROOT))
    t0 = time.monotonic()
    check = json.loads(ve("document", "check", rel))
    t1 = time.monotonic()
    coverage = json.loads(ve("document", "coverage", rel))
    t2 = time.monotonic()
    timing = {"document_check": round(t1 - t0, 1), "document_coverage": round(t2 - t1, 1)}
    render = ve("document", "render", rel)
    strict = {"check": json.loads(ve("document", "check", str(STRICT.relative_to(ROOT)))),
              "coverage": json.loads(ve("document", "coverage", str(STRICT.relative_to(ROOT))))}
    dump("check.json", check)
    dump("coverage.json", coverage)
    dump("environment.json", main_meta["environment"])
    dump("readings/check-all-strict.json", strict["check"])
    (RUN / "readings/rendered-all-strict.md").write_text(ve("document", "render", str(STRICT.relative_to(ROOT))))
    (RUN / "rendered.md").write_text(annotate(render, ledger))
    (RUN / "rendered-raw.md").write_text(render)
    assert check["premises"]["status"] == "model", check["premises"]
    assert check["reading_plan"]["route"] == "enumerate" and len(check["reading_plan"]["choices"]) == 8
    assert check["readings"]["conflict"]["status"] == "CONFLICT-FREE"
    assert coverage["coverage_percent"] == 100 and coverage["source_bytes"] == len(SOURCE)
    prev_check = json.load(open(PREV_DIR / "check.json"))
    prev_cov = json.load(open(PREV_DIR / "coverage.json"))

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
    # VE's own coverage: CHECKED + OPEN(+READINGS) bytes
    assert coverage["bytes_by_status"]["CHECKED"] == nb["CHECKED"] and coverage["bytes_by_status"]["OPEN"] == nb["OPEN"] + nb["READINGS"]

    # ---- audit-verified bytes: accepted by an audit of this lineage AND byte-identical here to the form that audit saw
    prev_verified = list(prev_metrics["audit_verified_covered_units"])
    dropped = [i for i in prev_verified if i in CHANGED]
    kept = [i for i in prev_verified if i not in CHANGED]
    newly = [i for i in AUDIT_0600_FAITHFUL if status[i] in COVERED and status[i] != "LABELLED" and i not in CHANGED and i not in kept]
    verified = kept + newly
    verified_bytes = width(verified)
    # the three reading sets that only had a stale count in their notes: audit-verified in content, not byte-identical in the ledger note
    notes_only = [i for i in SETS_KEPT if i in prev_verified]
    verified_if_notes_ignored = verified_bytes + width(notes_only)
    cand_lab = list(dict.fromkeys(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED + ["u0212.heading"]
                                  + prevf.AUDIT_FAITHFUL_1800 + prevf.AUDIT_FAITHFUL_1811 + AUDIT_0600_FAITHFUL))
    verified_lab = [i for i in cand_lab if i in by_id and status[i] == "LABELLED"]
    verified_meta = width(verified_lab)
    assert verified_meta == prev_metrics["audit_verified_metadata_bytes"] == nb["LABELLED"], (verified_meta, nb["LABELLED"])
    repaired_bytes = width([i for i in CHANGED if status[i] in COVERED])

    # ---- reading sets, conclusion queries, probes
    nd = {"all": prevf.slice_result("all")}
    assert nd["all"]["conflict"] == "CONFLICT-FREE" and nd["all"]["premises"] == "model" and nd["all"]["choice_count"] == 8
    sep_all = sum(nd["all"]["separations"].values())
    cand_status = Counter(nd["all"]["premises_by_candidate"].values())
    concl = prevf.concl((("denial_one_reading", "conclusion-no-denial-result.json"), ("claim_human", "claim-human-result.json")))
    assert concl["denial_one_reading"]["verdict"] == "ALL" and concl["claim_human"]["verdict"] == "ALL"
    prev_cc = prev_metrics["checked_content_main_chain"]
    prev_concl = {**prev_cc["conclusion_probe"]["results"], "claim_human": prev_cc["conclusion_probe_operators"]["results"]["across_all_readings"]}
    points = probe["points"]
    probe_names = ("risk-probe", "s1-probe", "senses-probe", "senses-document-probe", "discourse-probe", "rights-reading-probe")
    probe_same = {n: (RUN / f"probes/{n}.json").read_bytes() == (PREV_DIR / f"probes/{n}.json").read_bytes() for n in probe_names}
    assert all(probe_same.values()), probe_same
    s1_probe = json.load(open(RUN / "probes/s1-probe.json"))
    rights = json.load(open(RUN / "probes/rights-reading-probe.json"))
    profile_probe = old.probe_profiles()
    comp = json.load(open(RUN / "probes/companion-probe.json"))
    comp_ok, comp_bad = comp["attempts"]["without_source_word"], comp["attempts"]["with_source_word"]
    assert comp_ok["check"]["returncode"] == 0 and comp_bad["check"]["returncode"] == 5
    comp_share = comp_ok["lean_decided_share"]
    comp_q = {}
    for name in ("no-denial", "claim-human"):
        d = json.load(open(RUN / f"probes/companion/query-{name}.json"))
        comp_q[name] = {"verdict": d["verdict"], "route": d["route"], "component": d["component"], "sentence": d.get("sentence"),
                        "decided_units": len(d["decided_units"]), "english": d["english"]}
    asks = [json.load(open(RUN / f"probes/ask/q{i}.json")) for i in range(1, 6)]
    ask_questions = [(RUN / f"probes/ask/q{i}.question.txt").read_text().strip() for i in range(1, 6)]
    ask_read = sum(1 for a in asks if a["result"].get("status") != "none")

    open_terms = [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")} for t in main_meta["open_terms"]]
    names = {t["name"] for t in open_terms}
    prev_names = {t["name"] for t in prev_metrics["open_terms"]}
    assert names - prev_names == {KNOW} and prev_names - names == {"exception_to_never_denying_being_claude"}, (names ^ prev_names)
    cv_main = {"document_loaded": True, "coverage_percent": coverage["coverage_percent"],
               "premises": {k: check["premises"][k] for k in ("status", "route", "evidence")}, "premises_gaps": check["premises"].get("gaps"),
               "reading_plan": {"route": check["reading_plan"]["route"], "choice_count": len(check["reading_plan"]["choices"]),
                                "conditional_on": check["reading_plan"].get("conditional_on")},
               "conflict": {"route": check["readings"]["route"], "status": check["readings"]["conflict"]["status"],
                            "evidence": check["readings"]["conflict"].get("evidence"), "status_text": check["readings"]["status"],
                            "choices": dict(Counter(c["status"] for c in check["readings"]["conflict"]["choices"])),
                            "sizes": check["readings"].get("sizes"), "english": check["readings"]["english"]},
               "previous_run": {"premises_route": prev_check["premises"]["route"], "conflict_route": prev_check["readings"]["route"],
                                "conflict_status_text": prev_check["readings"]["status"], "choices": len(prev_check["reading_plan"]["choices"]),
                                "open_sentences": 4},
               "residual": coverage["residual"], "residual_previous_run": prev_cov["residual"], "norm_defaults": check["norm_defaults"],
               "check_seconds_this_run": timing}
    cv_strict = {"document": "readings/all-strict.ve.md", "premises": strict["check"]["premises"], "residual": strict["coverage"]["residual"],
                 "bytes_by_status": strict["coverage"]["bytes_by_status"]}
    m = {
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "source_sha256": prev_metrics["source_sha256"], "source_bytes": len(SOURCE), "bytes_accounted": total, "bytes_accounted_percent": 100.0,
        "history_note": "this file records this run; the earlier runs' records (audit-verification history, the earlier probes' narrative) are in prev/metrics.json",
        "changed_units": sorted(CHANGED),
        "changed_units_detail": {
            U0125: "repaired (audit 20261012T0600Z): READINGS -> CHECKED; the defeasible candidate, its reading set and its open term are removed",
            **{i: "repaired (audit 20261012T0600Z): guard = case atom AND the open term " + KNOW + (" (rejected by the audit)" if i in ("u0165.s02", "u0165.s03", "u0165.s05", "u0165.s07") else " (same class, not sampled)")
               for i in HC_UNITS},
            **{i: "note only: the stale count of choices and slice name are corrected; no reading or content changed" for i in SETS_KEPT},
            U0173: "note only: UNFORMALISED, not claimed; says its words are used as the open term " + KNOW},
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": old.full(u), "bytes_by_status": old.full(nb),
                                  "previous_run": {k: prev_metrics["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units, "bytes_by_substatus": old.full(nb),
                                              "previous_run": {k: prev_metrics["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")}},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": prev_metrics["claimed_covered_bytes"], "claimed_covered_bytes_gained": claimed - prev_metrics["claimed_covered_bytes"],
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"], "substantive_covered_bytes_previous_run": prev_metrics["substantive_covered_bytes"],
        "audit_verified_covered_bytes": verified_bytes, "audit_verified_covered_percent": round(100 * verified_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified, "audit_verified_covered_bytes_previous_run": prev_metrics["audit_verified_covered_bytes"],
        "audit_verified_covered_bytes_if_note_only_edits_are_ignored": verified_if_notes_ignored,
        "audit_verified_dropped_because_changed": dropped,
        "audit_verified_newly_from_20261012T0600Z": newly,
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run to the form that audit saw. The audit of run "
            "20261012T0600Z (15/20 sampled faithful, 5 unfaithful: u0125.s04.p2, u0165.s02, u0165.s03, u0165.s05, u0165.s07; AUDIT-20261012T0600Z-received.md) is the latest. "
            "This run repaired those five and, being the same class, u0165.s01, u0165.s04 and u0165.s06; the eight repaired units, the three reading-set units whose ledger note lost a "
            "stale count (u0036.s05, u0156.s03, u0263.s04.p2) and u0173.s01 are changed and so are not audit-verified until re-audited. Labels are unchanged: 349 of 349 label bytes "
            "stay verified."),
        "audit_verified_metadata_bytes": verified_meta, "audit_verified_metadata_percent": round(100 * verified_meta / len(SOURCE), 4),
        "audit_verified_metadata_bytes_previous_run": prev_metrics["audit_verified_metadata_bytes"],
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "repaired_bytes_not_audit_verified": repaired_bytes,
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261012T0600Z_audit": AUDIT_0600_UNFAITHFUL,
            "repair_done_in_20261012T1800Z": ("see AUDIT-REPAIR.md: u0125.s04.p2 loses its defeasible candidate (CHECKED, one reading); the seven hard-constraint rules gain the "
                                              "knowledge-or-likelihood open term in their guards. None of the five keeps a status it had before the repair without the repair; "
                                              "all eight changed units are claimed but not audit-verified"),
            "kept_covered_status_without_repair": [],
            "earlier_audits": "the rejections and repairs of the earlier runs are recorded in prev/metrics.json and the AUDIT-*-received.md files"},
        "document_profiles": {"main": main_meta["environment"]["profiles"], "strict": front_matter(STRICT)["environment"]["profiles"]},
        "documents": {"translation": "translation.ve.md (three 'should' reading sets carry content; built by nd.py all from translation-without-content.ve.md, cmp-identical)",
                      "without_content": "translation-without-content.ve.md", "strict": "readings/all-strict.ve.md (the source of the strict content of the three sets)",
                      "not_carried": "readings/all-default.ve.md, readings/s1.ve.md (soft-chain demonstrations of earlier runs; copied in for probes s1 and rights, then removed)"},
        "open_terms": open_terms, "open_terms_count": len(open_terms), "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "open_terms_added": [KNOW], "open_terms_removed_this_run": ["exception_to_never_denying_being_claude"], "open_terms_with_changed_factors": [],
        "reading_sets": {"count": 3, "unresolved": 3, "count_previous_run": 4, "units": SETS_KEPT, "candidates": {i: ["strict", "default"] for i in SETS_KEPT},
                         "couplings": [], "narrowings": [],
                         "choices": nd["all"]["choice_count"], "choices_previous_run": 16, "removed_this_run": {U0125: "the defeasible candidate and the set (audit 20261012T0600Z)"},
                         "readings_from_the_words": {
                             "force_sets_kept_because_of_the_word_should": {"units": ["u0036.s05", "u0263.s04.p2"], "spans": ["u0253.s04", "u0011.s01"]},
                             "force_set_kept_because_the_text_implies_exceptions": {"units": ["u0156.s03"], "spans": ["u0109.s06", "u0109.s05"],
                                                                                    "note": "accepted again by the 20261012T0600Z audit (sampled)"},
                             "removed": {"u0052.s01": "“should always”: the word “always” excludes exceptions in the sentence itself and no span of the text implies one",
                                         U0125: "“should never directly deny that it is Claude”: the spans cited for a defeasible reading are about honesty in general and u0170.s01 says the hard-constraint list does not exhaust what Claude should never do; the audit found no exception stated or implied"},
                             "removed_by_audit_20261008T1800Z": {"u0062.s01": ["ability"], "u0123.s01.p1": ["permission-no-limits"], "u0123.s02.p1": ["conditional-permission", "ability"],
                                                                 "u0123.s03": ["narrow-ability", "wide-ability"]}}},
        "missing_feature_tally": old.tally(ledger), "missing_feature_tally_previous_run": prev_metrics["missing_feature_tally"],
        "check_verdicts": {"main": cv_main, "all_strict": cv_strict},
        "timing_single_runs": {"note": "one run each on one machine, not a controlled comparison (the previous figures come from the previous run's files; the machine may differ)",
                               "document_check_seconds": timing["document_check"], "document_check_seconds_previous_run": 48.9,
                               "document_coverage_seconds": timing["document_coverage"], "document_coverage_seconds_previous_run": 45.7,
                               "nd_all_load_seconds": [nd["all"]["load_seconds"], 9.0], "nd_all_check_seconds": [nd["all"]["check_seconds"], 52.5],
                               "nd_all_separation_search_seconds": [nd["all"]["separation_search_seconds"], 59.9],
                               "order": "[this run, previous run]; this run has three sets (8 choices) against four (16)"},
        "unspecified_probe": {"file": "probes/unspecified-probe.json", "document": "readings/all-strict.ve.md", "points_asked": len(points),
                              "undecided": sum(1 for p in points if p["status"] == "UNDECIDED"),
                              "settled": sum(1 for p in points if p["status"].startswith("SETTLED")),
                              "conflict": sum(1 for p in points if p["status"].startswith("CONFLICT")), "conflict_reports": probe["conflict"],
                              "gaps": {p: g["reached"] for p, g in probe["gaps"].items()},
                              "hard_constraint_points": {p["label"]: p["status"] for p in points if p["label"].startswith("u0165")},
                              "reading": "each hard constraint: SETTLED no where the case holds and Claude knowingly engages in it or thinks it quite likely; UNDECIDED where the case holds "
                                         "but neither (the text sends such cases to holistic judgment, u0173.s02), where only the knowledge atom holds, and where the case does not hold"},
        "profile_combination_probe": profile_probe, "profile_combination_probe_same_as_previous_run": profile_probe == prev_metrics["profile_combination_probe"],
        "silence_sentences_as_used_in_ledger": {k: v for k, v in silence.items()}, "legend_sentences": legend,
        "senses_probe": {**prev_metrics["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-probe"]},
        "senses_document_probe": {**prev_metrics["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-document-probe"]},
        "discourse_probe": {**prev_metrics["discourse_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["discourse-probe"]},
        "rights_reading_probe": {**rights, "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["rights-reading-probe"]},
        "risk_probe": {**prev_metrics["risk_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["risk-probe"]},
        "readings_defaults_probe": {"re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"],
                                    "outcome": {"a_main_with_readings@1": "accepted; premises UNKNOWN (no set carries content)",
                                                "b_main_with_one_strict_norm_candidate": "accepted (premises UNKNOWN: the other sets are pending)",
                                                "c_s1_document_with_norm_defaults@0": s1_probe["c_s1_document_with_norm_defaults@0"]["rejection"]}},
        "lean_decided_share": {"decided_bytes": 0, "decided_share_percent": "0.00", "script": "tools/lean_decided_share.py",
                               "meaning": "units whose every verdict is a Lean answer that is not UNKNOWN across readings. For the translation itself (no companion set) it is still 0.00% "
                                          "(`ve document check` reports no `decided_units`, basis 'no Lean answer across readings')",
                               "with_companion_sets": {"document": "probes/companion/translation-companions-without_source_word.ve.md", "decided_units": len(comp_share["decided_units"]),
                                                       "decided_bytes": comp_share["decided_bytes"], "decided_share_percent": comp_share["decided_share_percent"],
                                                       "units": comp_share["decided_units"],
                                                       "caveat": "a probe document, not the translation; each of the three 'should' sets is checked by itself as a component, and a rule checked by itself is CONFLICT-FREE by construction"}},
        "companion_probe": {"what": "the three 'should' reading sets re-written as companion sets (readings-defaults RD-4b): each candidate carries the main environment (without readings@1) and the open terms its content names",
                            "accepted_with_source_word": False, "refusal_with_source_word": comp_bad["check"]["stdout_error"], "defect_still_present_at_ts_B1": True,
                            "route": comp_ok["summary"]["route"], "components": comp_ok["summary"]["components"], "conflict": comp_ok["summary"]["conflict"],
                            "premises": comp_ok["summary"]["premises"], "premises_components": comp_ok["summary"]["premises_components"],
                            "separations": comp_ok["summary"]["separations"], "decided_units": len(comp_share["decided_units"]), "decided_bytes": comp_share["decided_bytes"],
                            "decided_share_percent": comp_share["decided_share_percent"], "queries": comp_q,
                            "reading": "u0125.s04.p2 is now a unit of the main component, decided with the others; the companion denial query (--sentence u0125.s04.p2) answers ALL, where it answered SOME with two readings"},
        "checked_content_main_chain": {
            "documents": nd, "candidate_premise_status": dict(cand_status), "choices_checked": nd["all"]["choices_checked"],
            "choices_conflict_free": nd["all"]["conflict_by_choice"].get("CONFLICT-FREE", 0), "choices_conflict": nd["all"]["conflict_by_choice"].get("CONFLICT", 0),
            "separating_situations_checked_by_lean": sep_all, "separated_by_decision_only_findings": 0,
            "all_three_in_one_document": {"admitted": nd["all"]["admitted"], "choices": nd["all"]["choice_count"], "verdict": nd["all"]["conflict_text"],
                                          "separations": nd["all"]["separations"], "route": nd["all"]["route"], "sizes": nd["all"]["sizes"]},
            "conclusion_probes": {"query_denial": "every instance of Claude: not denial_of_being_claude_permitted (probes/nd/conclusion-no-denial.json)",
                                  "query_claim_human": "no operator may give Claude an instruction to claim to be human when asked (probes/nd/conclusion-no-claim-human.json)",
                                  "results": concl, "previous_run_verdicts": {k: v["verdict"] for k, v in prev_concl.items()},
                                  "reading": "the denial query was UNKNOWN across the two readings of u0125.s04.p2 and ALL only under the strict one; with one reading it is ALL on the superposed route, with a certificate "
                                             "and an English line. The claim-human query is ALL as before. This is the only conclusion that moved, and it moved because the translation lost a reading, not because the language grew"},
            "not_representable": [
                "defeasibility beside norm-defaults@0 as VE's own mode: probe c still refuses norm-defaults@0 with soft-norms@0 ('await the Lean route')",
                "decided units for a document without companion sets: `decided_units` is reported only by the companion (product) route; the translation itself stays 0.00%",
                "companion sets together with `source_word`: refused with CheckerUnavailable (a Python defect, still present at ts-B1)",
                "English for a gated UNKNOWN conclusion on the superposed route",
                "typed knowledge, intention and likelihood (u0173.s01): carried only as an open term"]},
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "changed_or_replaced_ids": sorted(CHANGED), "added_ids": [], "units_newly_covered": [],
            "units_with_status_change": {U0125: "READINGS -> CHECKED"}, "units_changed_by_audit_repair": [U0125, *HC_UNITS],
            "open_terms_added": [KNOW], "open_terms_removed": ["exception_to_never_denying_being_claude"],
            "reading_sets_before_after": [4, 3], "choices_before_after": [16, 8]},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {"infra/ts-B5": "test speed B5: run order, --maxfail, a tracked quarantine, the gate never stops early; tooling and tests only",
                       "infra/ts-B1": "test speed B1: manifest, mode schemas and Lean module selection decoupled for test selection; ve/assurance.py audit events and a schema-compile lock in "
                                      "ve/backends/service_schema.py; no change to what a document can say"},
            "checked_by": "git diff ve-green-devtime-1..HEAD --stat -- ve lean rust conformance: two Python files (assurance.py, service_schema.py), neither in the grammar, profiles, lexicon, Lean or Rust",
            "newly_expressible_features": 0, "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "newly_measurable": "nothing new: every output of `ve document check`, `coverage`, `readings`, `ask` and the carried probes is the previous run's apart from the effects of this run's own repair",
            "what_made_the_difference": "the audit's repair, not the language"},
        "question_probe": {
            "what": "`ve ask --reading --json` on the translation: five yes-or-no questions about the denial, clarification and claim-to-be-human units (probes/ask/)",
            "questions": ask_questions, "read": ask_read, "no_reading": [a["result"]["text"] for a in asks],
            "reading": "none of the five is read (the reader does not know 'must not', 'must seek clarification in each situation'); the answers differ from the previous run's only in the environment and lexicon ids"},
        "reading_set_gaps": [
            {"gap": "a defeasible rule beside norm-defaults@0 (soft-norms@0 with norm-defaults@0 is refused, probe c)", "feature": "defaults", "workaround": "one named exception predicate per set, used as an `unless` (an open term)"},
            {"gap": "“cannot be unlocked by any operator or user”: who has authority to change what a norm requires; the language has no typed authority/modal", "feature": "modality/belief", "workaround": "the clause is UNFORMALISED; its effect is carried by the hard constraints' exception-free rules"},
            {"gap": "knowing, intending and thinking something quite likely (u0173.s01): no typed epistemic modal", "feature": "modality/belief", "workaround": "one open term in the guard of each hard constraint"},
            {"gap": "an exception the text does not name is an open term the translator names (exception_to_*), three open terms", "feature": "other:graded-force", "workaround": "recorded as open terms with 'the source names no exception' as their only factor"},
            {"gap": "decided units are reported only for a document with companion sets; a set with `source_word` fails there", "feature": "other:RD-4b-report", "workaround": "a probe document without `source_word`"},
            {"gap": "the superposed route gives no English for a gated UNKNOWN conclusion", "feature": "other:superposed-unknown-english", "workaround": "none needed here"}],
        "heading_presuppositions_exposed": prev_metrics["heading_presuppositions_exposed"],
        "regulated_predicates": prev_metrics["regulated_predicates"], "no_invented_permissions": prev_metrics["no_invented_permissions"],
        "carried_probes_note": "the six carried probes (risk, s1, senses, senses_document, discourse, rights) re-run at this tag; byte-identical JSON: " + ", ".join(probe_same),
        "seeded_bugs": {"needed": False, "why": "no product code (Lean, Python, Rust) was changed: this run adds files under usecases/ only"},
        "conflicts": {"reported_by_VE": 0, "classification": "none to classify: CONFLICT-FREE in all 8 choices; the whole-document proof attempt of the strict companion is CONFLICT-FREE"},
    }
    # no trace of the removed reading in this run's metrics
    blob = json.dumps({k: v for k, v in m.items() if k not in ("changes_against_previous_run", "audit_rejected_units_and_repair_status", "reading_sets",
                                                                  "changed_units_detail", "checked_content_main_chain", "open_terms_removed_this_run",
                                                                  "audit_verified_basis", "audit_verified_dropped_because_changed", "units")}, ensure_ascii=False)
    for stale in ("force-u0125", "exception_to_never_denying", "four 'should'", "16 of 16", "4 open sentences"):
        assert stale not in blob, stale
    whole = json.dumps({k: v for k, v in m.items() if k not in ("changes_against_previous_run", "open_terms_removed_this_run")}, ensure_ascii=False)
    for stale in ("force-u0125", "exception_to_never_denying"):
        assert stale not in whole, stale
    dump("metrics.json", m)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent",
                                         "audit_verified_metadata_bytes", "claimed_but_not_audit_verified_bytes", "changed_units")}))
    print(dict(u), dict(nb))
    print("probe_same:", probe_same, "profile probe same:", m["profile_combination_probe_same_as_previous_run"])
    print("ask read:", ask_read, "companion q:", {k: v["verdict"] for k, v in comp_q.items()}, "conclusions:", {k: v["verdict"] for k, v in concl.items()})


if __name__ == "__main__":
    main()
