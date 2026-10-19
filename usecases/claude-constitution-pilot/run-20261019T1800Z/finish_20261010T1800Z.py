#!/usr/bin/env python3
"""Run 20261010T1800Z: re-run VE at ve-green-arch-AR-6, write the ledger, renderings and metrics.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python usecases/claude-constitution-pilot/run-20261010T1800Z/repair_20261010T1800Z.py   # base/ + prev/ -> translation-without-content.ve.md, units.json
    uv run python .../nd.py all                          # readings/nd-all.ve.md becomes translation.ve.md; about 2 min
    cp readings/nd-all.ve.md translation.ve.md && rm readings/nd-all.ve.md
    uv run python -m ve document coverage translation.ve.md > readings/coverage-nd-all.json
    probes (README.md), conclusion queries (probes/nd/, README.md)
    uv run python .../finish_20261010T1800Z.py            # about 3 min

The translation is the previous run's (20261010T0600Z), with the seven units its audit rejected repaired (AUDIT-REPAIR.md): the shared open
terms lose the unsupported factors (scope of the role-play phrase; decline/reveal), the notes of the four operator units say only what the one
reading is, and the "two readings" clause is deleted from the seven hard-constraint notes. No unit gains a covered status from a new feature.
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

RUN_ID = "20261010T1800Z"
PREV_RUN = "20261010T0600Z"
TAG = "ve-green-arch-AR-6"
PREV_TAG = "ve-green-lf-16c"
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
FORCE_UNITS = ["u0036.s05", "u0125.s04.p2", "u0156.s03", "u0263.s04.p2"]
OP_UNITS = ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03"]
HC_UNITS = [f"u0165.s0{i}" for i in range(1, 8)]
# the audit of run 20261010T0600Z (14/20 sampled + 1/5 changed): verdicts as received (AUDIT-20261010T0600Z-received.md)
AUDIT_REJECTED_0600 = ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03", "u0165.s04", "u0165.s05", "u0165.s07"]
AUDIT_FAITHFUL_0600 = ["u0013.heading", "u0036.s05", "u0073.s05", "u0103", "u0125.s04.p2", "u0126", "u0156.s03", "u0166.s04.p4", "u0168.s01",
                       "u0212.heading", "u0235.heading", "u0238.heading", "u0248", "u0263.s04.p2", "u0298"]
# the changed units: the seven the audit rejected, plus the four hard-constraint units with the same stale note clause (u0165.s01, s02, s03, s06)
CHANGED = sorted(OP_UNITS + HC_UNITS)
DROPPED_FACTORS = {"instruction_abandon_identity_in_persona", "instruction_decline_or_withhold"}


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
    ledger = json.load(open(RUN / "units.json"))   # written by repair_20261010T1800Z.py
    prev_metrics = json.load(open(RUN / "prev/metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == prev_metrics["source_sha256"]
    by_prev = {e["id"]: e for e in prev}
    by_id = {e["id"]: e for e in ledger}
    changed_entries = sorted(e["id"] for e in ledger if e != by_prev[e["id"]])
    assert changed_entries == CHANGED, changed_entries
    assert by_id["u0166.s04.p4"] == by_prev["u0166.s04.p4"] and by_id["u0166.s04.p4"]["status"] == "UNFORMALISED"
    assert all(by_id[i]["status"] == by_prev[i]["status"] for i in by_id)   # no unit changes status
    prev_main = front_matter(PREV_DIR / "translation.ve.md")
    main_meta = front_matter(MAIN)
    assert [(u["id"], tuple(u["span"])) for u in main_meta["units"]] == [(e["id"], tuple(e["span"])) for e in ledger]
    prev_units = {u["id"]: u for u in prev_main["units"]}
    unit_diff = sorted(u["id"] for u in main_meta["units"] if u != prev_units[u["id"]])
    assert unit_diff == [], unit_diff   # the document's units are byte for byte the previous run's; only two open terms lose a factor
    pv = prev_main["environment"]["vocabulary"]["predicates"]
    nv = main_meta["environment"]["vocabulary"]["predicates"]
    pred_gone = sorted(k for k in pv if k not in nv)
    pred_new = sorted(k for k in nv if k not in pv)
    assert pred_gone == [], pred_gone
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
    same_whole_set = {i: front_set(main_meta, SETS[i]) == front_set(prev_main, SETS[i]) for i in SETS}   # identifiers included

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

    check_same_as_previous = same_except(check, prev_check, {"coverage", "residual", "readings", "document_id", "admission"})   # the ids hash the document, whose open terms changed

    # ---- ledger: the notes of the changed units were written by repair_20261010T0600Z.py; nothing is appended here
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE)
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    u, nb = old.counts(ledger)
    claimed = sum(v for k, v in nb.items() if k in COVERED)
    assert claimed == prev_metrics["claimed_covered_bytes"], claimed   # no status changes
    n_old, old_units, _ = old.aggregate(ledger)
    spans = {e["id"]: e["span"] for e in ledger}
    status = {e["id"]: e["status"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)

    # ---- audit-verified bytes: accepted by an audit AND byte-identical in this run to the form it saw
    prev_verified = list(prev_metrics["audit_verified_covered_units"])
    assert not [i for i in prev_verified if i in AUDIT_REJECTED_0600 and i not in HC_UNITS]
    dropped_now = [i for i in prev_verified if by_id[i] != by_prev[i]]   # u0165.s01 to s07: the note changed (s04, s05, s07 were rejected)
    dropped_now = sorted(dropped_now)
    assert dropped_now == sorted(HC_UNITS), dropped_now
    keep = [i for i in prev_verified if i not in dropped_now]
    for i in keep:   # unchanged since the audit that accepted them
        assert by_id[i] == by_prev[i] and i not in unit_diff, i
    faithful_sub = [i for i in AUDIT_FAITHFUL_0600 if status[i] in COVERED and status[i] != "LABELLED"]
    faithful_lab = [i for i in AUDIT_FAITHFUL_0600 if status[i] == "LABELLED"]
    # accepted by the 20261010T0600Z audit in the form it saw; byte-identical here (ledger entry, document unit, and for a set the whole set)
    newly = [i for i in faithful_sub if i not in keep]
    for i in newly:
        assert by_id[i] == by_prev[i] and i not in unit_diff and (i not in SETS or same_whole_set[i]), i
    for i in faithful_sub:   # the four sets and the other accepted units are verified in the very form the audit saw
        assert by_id[i] == by_prev[i] and (i not in SETS or same_whole_set[i]), i
    assert newly == [], newly
    verified = list(dict.fromkeys(keep + newly))
    assert all(by_id[i]["status"] in COVERED for i in verified)
    verified_bytes = width(verified)
    verified_before = prev_metrics["audit_verified_covered_bytes"]
    assert verified_bytes == verified_before - width(dropped_now) + width(newly), (verified_bytes, verified_before)
    verified_if_note_edits_ignored = verified_bytes + width([i for i in dropped_now if i not in AUDIT_REJECTED_0600])
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
    def verdicts(c):
        return {k: (v["verdict"], v["route"]) for k, v in c.items()}
    prev_cc = prev_metrics["checked_content_main_chain"]
    prev_force_results = {k: v for k, v in prev_cc["conclusion_probe"]["results"].items() if k != "across_all_readings_in_the_translation"}
    concl_force_same = concl_force == prev_force_results
    concl_force_verdicts_same = verdicts(concl_force) == verdicts(prev_force_results)
    assert concl_force_verdicts_same
    concl_op_prev = prev_cc["conclusion_probe_operators"]["results"]
    concl_op_same = concl_op == concl_op_prev

    unspec = json.load(open(RUN / "probes/unspecified-probe.json"))
    points = unspec["points"]
    s1_probe = json.load(open(RUN / "probes/s1-probe.json"))
    profile_probe = old.probe_profiles()
    probe_same = {name: (RUN / f"probes/{name}.json").read_bytes() == (PREV_DIR / f"probes/{name}.json").read_bytes()
                  for name in ("unspecified-probe", "risk-probe", "s1-probe", "senses-probe", "senses-document-probe", "discourse-probe",
                               "rights-reading-probe")}
    rights = json.load(open(RUN / "probes/rights-reading-probe.json"))

    comp = json.load(open(RUN / "probes/companion-probe.json"))
    comp_ok = comp["attempts"]["without_source_word"]
    comp_bad = comp["attempts"]["with_source_word"]
    assert comp_ok["check"]["returncode"] == 0 and comp_bad["check"]["returncode"] == 5
    comp_share = comp_ok["lean_decided_share"]
    comp_q = {}
    for name in ("no-denial", "no-denial-under-0", "no-denial-under-1", "claim-human"):
        d = json.load(open(RUN / f"probes/companion/query-{name}.json"))
        comp_q[name] = {"verdict": d["verdict"], "route": d["route"], "component": d["component"], "decided_units": len(d["decided_units"]), "english": d["english"]}
    plain_english = {name: json.load(open(RUN / f"probes/nd/{f}.json")).get("english")
                     for name, f in (("across_all_readings", "conclusion-no-denial-result"), ("under_defeasible", "conclusion-no-denial-under-1"))}

    cv = copy.deepcopy(prev_metrics["check_verdicts"])
    cv["main"] = {"document_loaded": True, "coverage_percent": coverage["coverage_percent"], "premises": {k: check["premises"][k] for k in ("status", "route", "evidence")},
                  "premises_by_choice": dict(Counter(c["status"] for c in check["premises"]["choices"])),
                  "reading_plan": {"route": check["reading_plan"]["route"], "choice_count": len(check["reading_plan"]["choices"]),
                                   "conditional_on": check["reading_plan"].get("conditional_on")},
                  "reading_plan_previous_run": prev_metrics["check_verdicts"]["main"]["reading_plan"],
                  "residual": coverage["residual"], "norm_defaults": check["norm_defaults"],
                  "identical_to_previous_run": check_same_as_previous,
                  "what_changed": "nothing in the verdict fields: premises model in every choice, enumerated reading plan, 16 choices, conflict-free, as in the previous run; "
                                  "the translation differs from the previous run only in two open terms (factors deleted) and in ledger notes; "
                                  "the check of the unchanged previous translation at ve-green-arch-AR-6 (check-baseline.json) gives the same verdicts as at ve-green-lf-16c",
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
        "previous_runs_note": "run 20261010T0600Z is the previous run's own output (usecases/claude-constitution-pilot/run-20261010T0600Z on branch pilot/cc-20261010T0600Z); its audit is AUDIT-20261010T0600Z-received.md; prev/ here holds the files this run starts from and compares with",
        "changed_units": CHANGED,
        "changed_units_note": {
            "u0123.s03": "audit 20261010T0600Z: the open term instruction_abandon_identity_in_persona no longer lists the scope of the role-play phrase as an unresolved factor (the phrase belongs to the first item only); the note says only what the one reading is. Status OPEN as before",
            "u0123.s01.p1": "same open term, same repair (the permission is scoped by the six limits); note rewritten. OPEN as before",
            "u0062.s01": "same. OPEN as before",
            "u0123.s02.p1": "same, and the open term instruction_decline_or_withhold no longer lists the decline/reveal ambiguity the words do not raise. OPEN as before",
            "u0165.s04": "audit 20261010T0600Z: the note no longer says u0166.s04 has two readings (it has none; u0166.s04.p4 is UNFORMALISED with a settled meaning). OPEN as before",
            "u0165.s05": "same", "u0165.s07": "same",
            "u0165.s01": "not sampled; the same sentence was in the note, so it is deleted here too. OPEN as before",
            "u0165.s02": "same as u0165.s01", "u0165.s03": "same as u0165.s01", "u0165.s06": "same as u0165.s01"},
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": old.full(u), "bytes_by_status": old.full(nb),
                                  "previous_run": {k: prev_metrics["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units, "bytes_by_substatus": old.full(nb),
                                              "previous_run": {k: prev_metrics["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")}},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": prev_metrics["claimed_covered_bytes"], "claimed_covered_bytes_gained": claimed - prev_metrics["claimed_covered_bytes"],
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"], "substantive_covered_bytes_previous_run": prev_metrics["substantive_covered_bytes"],
        "audit_verified_covered_bytes": verified_bytes, "audit_verified_covered_percent": round(100 * verified_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified, "audit_verified_covered_bytes_previous_run": verified_before,
        "audit_verified_covered_bytes_if_justification_only_edits_are_ignored": verified_if_note_edits_ignored,
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run to the form that audit saw. The audit of run "
            "20261010T0600Z (14/20 sampled faithful, 1/5 changed units faithful) rejected u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03, u0165.s04, u0165.s05 and u0165.s07; "
            "it accepted u0036.s05, u0125.s04.p2, u0156.s03, u0263.s04.p2 (whole reading sets), u0073.s05, u0168.s01 and u0248 in the form this run keeps byte for byte (all were verified already), "
            "and the labels u0013.heading, u0103, u0126, u0212.heading, u0235.heading, u0238.heading, u0298 (verified earlier or counted as metadata). "
            "The seven hard-constraint units u0165.s01 to u0165.s07 leave the audit-verified list because their notes changed (the audit rejected s04, s05, s07; s01, s02, s03, s06 carry the same deleted clause "
            "and were not sampled): 1,638 -> " + str(verified_bytes) + " bytes. If the four unsampled, note-only edits were ignored the figure would be " + str(verified_if_note_edits_ignored) + ". "
            "Nothing this run changed is audit-verified."),
        "audit_verified_dropped_because_changed_or_rejected": {**prev_metrics["audit_verified_dropped_because_changed_or_rejected"],
                                                               "rejected_by_20261010T0600Z_audit_u0165_s04_s05_s07_were_verified_before": ["u0165.s04", "u0165.s05", "u0165.s07"],
                                                               "changed_by_note_only_in_20261010T1800Z": [i for i in HC_UNITS if i not in AUDIT_REJECTED_0600],
                                                               "rejected_by_20261010T0600Z_audit_never_verified": OP_UNITS},
        "audit_verified_newly_from_20261010T0600Z": [i for i in newly], "audit_verified_newly_label_units_from_20261010T0600Z": newly_lab,
        "audit_verified_dropped_now": dropped_now,
        "audit_verified_metadata_bytes": verified_meta,
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "repaired_bytes_not_audit_verified": repaired_bytes,
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261010T0600Z_audit": AUDIT_REJECTED_0600,
            "repair_done_in_20261010T1800Z": "see AUDIT-REPAIR.md: the shared open terms lose the unsupported factors, the four operator notes say only what the one reading is, "
                                            "the 'two readings' clause is deleted from the seven hard-constraint notes",
            "repaired_and_not_yet_sampled": AUDIT_REJECTED_0600, "earlier": prev_metrics["audit_rejected_units_and_repair_status"]},
        "document_profiles": {"main": main_meta["environment"]["profiles"], "strict": front_matter(STRICT)["environment"]["profiles"]},
        "documents": {"translation": "translation.ve.md (the previous run's, repaired: two open terms lose a factor; the four 'should' reading sets carry content)", "without_content": "translation-without-content.ve.md",
                      "strict": "readings/all-strict.ve.md (carried: the source of the strict content of the four 'should' sets)",
                      "slices": None,
                      "not_carried": "readings/all-default.ve.md, readings/s1.ve.md (soft-chain demonstrations; the probes that need them were run on the earlier runs' copies, then removed)"},
        "open_terms": open_terms, "open_terms_count": len(open_terms), "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "open_terms_added": new_terms, "open_terms_removed_this_run": gone_terms,
        "open_terms_with_changed_factors": factors_changed,
        "reading_sets": {"count": 4, "unresolved": 4, "count_previous_run": 4,
                         "candidates": {s.get("unit"): [r["id"] for r in s["readings"]] for s in main_meta["reading_sets"]},
                         "candidates_previous_run": prev_metrics["reading_sets"]["candidates"],
                         "units": [s["unit"] for s in main_meta["reading_sets"]], "couplings": [],
                         "narrowings": [], "choices": 16, "choices_previous_run": 16,
                         "readings_from_the_words": {**{k: v for k, v in prev_metrics["reading_sets"]["readings_from_the_words"].items() if not k.startswith(("can_cannot", "scope_set", "checked_again", "removed_by_20261010T0600Z"))},
                                                     "checked_again_20261010T1800Z": (
                                                         "every candidate of the four reading sets was re-read against the words-only rule: each cites the document's own account of 'should' "
                                                         "(u0253.s04, u0011.s01) or its statement that these are almost hard constraints (u0109.s05, u0109.s06). The other units have one reading each. "
                                                         "No outside knowledge is used; no open term lists a question the words do not raise about the operator units.")}},
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
        "renderings_identical_to_previous_run": {"raw": changed_render["raw"] == 0, "changed_lines": changed_render,
                                                 "why": "byte-identical: the rendering does not print open-term factors, and no unit, content or reading changed"},
        "senses_probe": {**prev_metrics["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-probe"]},
        "senses_document_probe": {**prev_metrics["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-document-probe"]},
        "discourse_probe": {**prev_metrics["discourse_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["discourse-probe"],
                            "difference": "none: byte-identical to the previous run's JSON at ve-green-lf-16c"},
        "rights_reading_probe": {**rights, "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["rights-reading-probe"],
                                 "difference": "none: byte-identical to the previous run's JSON at ve-green-lf-16c"},
        "s1": {**prev_metrics["s1"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"],
               "historical_note": "figures and models of the soft-chain demonstration document of earlier runs (readings/s1.ve.md, not carried, not part of the translation); "
                                  "its model still names relations the translation no longer has"},
        "s2a": {**prev_metrics["s2a"], "re_run_at_this_tag": False,
                "note": "superseded: the same queries run on the translation itself (checked_content_main_chain.conclusion_probe_operators and conclusion_probe)"},
        "readings_defaults_probe": {**prev_metrics["readings_defaults_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"],
                                    "outcome": {"a_main_with_readings@1": "accepted; premises UNKNOWN (no set carries content)",
                                                "b_main_with_one_strict_norm_candidate": "accepted (premises UNKNOWN: the other sets are pending)",
                                                "c_s1_document_with_norm_defaults@0": s1_probe["c_s1_document_with_norm_defaults@0"]["rejection"]}},
        "lean_decided_share": {"decided_bytes": 0, "decided_share_percent": "0.00", "script": "tools/lean_decided_share.py",
                               "meaning": "units whose every verdict is a Lean answer that is not UNKNOWN across readings. For the translation itself (no companion set) it is still 0.00% at ve-green-arch-AR-6: "
                                          "`ve document check` and `ve document readings` report no `decided_units` for a document without companion sets (rd-4b: 'without companions the established route is used')",
                               "with_companion_sets": {"document": "probes/companion/translation-companions-without_source_word.ve.md", "decided_units": len(comp_share["decided_units"]),
                                                       "decided_bytes": comp_share["decided_bytes"], "decided_share_percent": comp_share["decided_share_percent"],
                                                       "units": comp_share["decided_units"],
                                                       "caveat": "a probe document, not the translation; each of the four 'should' sets is checked by itself as a component (VE says so in its English), "
                                                                 "and a rule checked by itself is CONFLICT-FREE by construction (lean_decided_share's own caveat)"}},
        "companion_probe": {
            "what": "the four 'should' reading sets re-written as companion sets (readings-defaults rd-4b): each candidate carries the main environment (without readings@1) and the open terms its content names; same units, contents, situations (probe_companions.py)",
            "accepted_with_source_word": False, "refusal_with_source_word": comp_bad["check"]["stdout_error"],
            "defect": "a set with `source_word` (the span of its “should”, used by the English of E22/E23) makes `ve document check`, `coverage` and `render` fail with CheckerUnavailable "
                      "'ReadingsConstruction ... KeyError': ve/readings_components.py `subdoc` builds the component's document without the `source` key that ve/readings_route.py `Wording.source_word` reads (line 804)",
            "accepted_without_source_word": True,
            "route": comp_ok["summary"]["route"], "components": comp_ok["summary"]["components"], "conflict": comp_ok["summary"]["conflict"], "premises": comp_ok["summary"]["premises"],
            "premises_components": comp_ok["summary"]["premises_components"], "separations": comp_ok["summary"]["separations"],
            "bytes_by_status_same_as_translation": comp_ok["coverage"]["json"]["bytes_by_status"] == coverage["bytes_by_status"],
            "decided_units": len(comp_share["decided_units"]), "decided_bytes": comp_share["decided_bytes"], "decided_share_percent": comp_share["decided_share_percent"],
            "queries_need_sentence": "a conclusion that fits several sentences is refused unless `--sentence <unit>` names one (19 sentences fit the denial query)",
            "queries": comp_q,
            "plain_route_for_comparison": {"denial_across_readings": concl_force["across_all_readings"]["verdict"], "denial_under_strict": concl_force["under_strict"]["verdict"],
                                           "denial_under_defeasible": concl_force["under_defeasible"]["verdict"], "claim_human": concl_op["across_all_readings"]["verdict"]},
            "reading": "with companions the denial query is decided: ALL under the strict reading, NONE under the defeasible one (its exception can hold), SOME across readings, where the plain route "
                       "gives UNKNOWN across readings and under the defeasible reading (its English: 'VE could not check whether the conclusion follows' for a choice of all four sets). The claim-to-be-human query is ALL in both. "
                       "Not analysed here: why the plain route cannot decide those two. The readings and contents are the same in both documents; only the packaging differs (each set a component, checked by itself)."},
        "checked_content_main_chain": {
            "what": "reading sets whose every candidate carries content that Lean checked on the main chain itself (norm-defaults@0, completion unspecified): readings@1 beside norm-defaults@0 (readings-defaults RD-2a/RD-2b); no coupling",
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
                                           "reading": "ALL: with one reading of u0123.s03 the prohibition holds whenever"},
            "conclusion_probes_identical_to_previous_run": {"denial_query": concl_force_same, "claim_to_be_human_query": concl_op_same,
                                                            "verdicts_equal": concl_force_verdicts_same,
                                                            "english_now_present": "the plain route's UNKNOWN answers now carry an English sentence naming each chosen reading's own sentence ('Read sentence 132 as ... and sentence 471 as ...') — rd-4b's change; "
                                                                                   "the verdicts, routes and evidence are unchanged",
                                                            "english_now": plain_english},
            "defeasible_candidates": "the soft chain's `exception: unstated` becomes one base predicate per set that is an open term (exception_to_*), used as an `unless`; the text names no exception",
            "not_representable": [
                "defeasibility beside norm-defaults@0 as VE's own mode: probe c still refuses norm-defaults@0 with soft-norms@0 ('await the Lean route')",
                "decided units for a document without companion sets: `decided_units` is reported only by the companion (product) route (rd-4b); the translation itself stays 0.00%, the companion probe reaches the share in lean_decided_share.with_companion_sets",
                "companion sets together with `source_word`: refused with CheckerUnavailable (a Python defect, see companion_probe.defect)",
                "a companion set is checked by itself: it is not checked together with the document's other sentences (VE's English says so)"],
            "premises_unknown": {"candidates": [k for k, v in nd["all"]["premises_by_candidate"].items() if v != "model"], "why": "none: every candidate has a model"}},
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "unchanged_entries": len(ledger) - len(CHANGED),
            "changed_or_replaced_ids": CHANGED, "added_ids": [], "units_newly_covered": [], "units_with_status_change": {},
            "units_changed_by_audit_repair": CHANGED, "open_terms_with_changed_factors": factors_changed,
            "reason": "the audit of 20261010T0600Z found (1) that the open term instruction_abandon_identity_in_persona still listed the scope of the role-play phrase as an unresolved factor, "
                      "and instruction_decline_or_withhold an ambiguity the words do not raise (both factors deleted; the notes of the four operator units say only what the one reading is), "
                      "(2) that the notes of u0165.s04, s05, s07 (and the identical clause in s01, s02, s03, s06) spoke of two readings of u0166.s04 (clause deleted). "
                      "No status changes and no unit is upgraded: the batches merged since lf-16c do not change what a document can say."},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {
                "question-answering Q1": "`ve ask`: a question (a sentence ending in ?) is read by the English reader and answered; no new form of document content",
                "infra/eff-tests, infra/eff-merge, infra/arch-AR-6": "test, merge-tooling and architecture-map work; no change to what a document can say",
                "readings-defaults/rd4b (rd-4b)": "readings with their own vocabulary (`companion`) through `ve document`: Lean splits the document into components, each companion set is checked by itself, "
                                                  "the verdicts are a product; `decided_units` (Lean-decided units) is reported on this route; 'reading N' is the reading's own sentence in the English"},
            "newly_expressible_features": 0, "newly_expressible": "no new meaning: companion sets repackage reading sets (their own vocabulary, checked alone); no unit gains a status",
            "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "newly_measurable": "the Lean-decided share (companion_probe, lean_decided_share.with_companion_sets) and decided conclusion queries; one new defect found (source_word)",
            "what_made_the_difference": "not a feature: this run repairs units the audit rejected and measures rd-4b on a probe document"},
        "question_probe": {
            "what": "`ve ask --reading --json` (question-answering Q1; answering is not built, Q2) on the translation: five yes-or-no questions about the denial, clarification and claim-to-be-human units (probes/ask/)",
            "read": sum(1 for i in range(1, 6) if json.load(open(RUN / f"probes/ask/q{i}.json"))["result"].get("status") != "none"),
            "no_reading": [json.load(open(RUN / f"probes/ask/q{i}.json"))["result"]["text"] for i in range(1, 6)],
            "reading": "none of the five is read: the question reader accepts only the controlled English of the document's vocabulary (it does not know “must not”, “each situation”, “may give Claude an instruction to …” as phrases). "
                       "Questions are not part of the language the units are written in; this changes no unit"},
        "reading_set_gaps": [
            {"gap": "a defeasible rule beside norm-defaults@0 (soft-norms@0 with norm-defaults@0 is refused, probe c)", "feature": "defaults", "workaround": "one named exception predicate per set, used as an `unless` (an open term)"},
            {"gap": "decided units are reported only for a document with companion sets (rd-4b); a set with `source_word` fails there", "feature": "other:RD-4b-report", "workaround": "a probe document without `source_word` (companion_probe)"},
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
