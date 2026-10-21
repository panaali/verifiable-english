#!/usr/bin/env python3
"""Run 20261009T0600Z: re-run VE at ve-green-lf-17, write the ledger, renderings and metrics.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python usecases/claude-constitution-pilot/run-20261009T0600Z/repair_20261009.py   # prev/ -> translation-without-content.ve.md, units.json
    for g in force op all; do uv run python .../nd.py $g; done                             # about 9 min; nd-all.ve.md is the translation
    cp readings/nd-all.ve.md translation.ve.md && rm readings/nd-all.ve.md
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python .../probe_$p.py; done
    conclusion probes (probes/nd/), see README.md
    uv run python .../finish_20261009.py                                                     # about 6 min (one `ve document check` of the translation)

The translation is the previous run's, repaired for the three units the audit rejected (and u0062.s01, which had the same defect),
with the content of all eight reading sets in the document itself (the coupling makes it 32 choices, within the enumerated
route's 64). Statuses of the 1,132 units do not change.
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

RUN_ID = "20261009T0600Z"
PREV_RUN = "20261008T1800Z"
TAG = "ve-green-lf-17"
PREV_TAG = "ve-green-lf-15b"
COVERED = old.COVERED
SOURCE = old.SOURCE
ve, front_matter = old.ve, old.front_matter
dump = lambda p, o: (RUN / p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")
PREV_DIR = Path("/home/seyran/code/manage-agents/pilots/claude-constitution") / f"run-{PREV_RUN}"
MAIN = RUN / "translation.ve.md"
STRICT = RUN / "readings/all-strict.ve.md"
SETS = {  # unit -> (set, slice document that also carries the set)
    "u0036.s05": ("force-u0036-s05", "nd-force"), "u0125.s04.p2": ("force-u0125-s04-p2", "nd-force"),
    "u0156.s03": ("force-u0156-s03", "nd-force"), "u0263.s04.p2": ("force-u0263-s04-p2", "nd-force"),
    "u0062.s01": ("modal-u0062-s01", "nd-op"), "u0123.s01.p1": ("modal-u0123-s01-p1", "nd-op"),
    "u0123.s02.p1": ("modal-u0123-s02-p1", "nd-op"), "u0123.s03": ("scope-modal-u0123-s03", "nd-op")}
FORCE_UNITS = ["u0036.s05", "u0125.s04.p2", "u0156.s03", "u0263.s04.p2"]
OP_UNITS = ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03"]
REPAIRED_BY_AUDIT = ["u0123.s01.p1", "u0123.s02.p1", "u0123.s03"]
AUDIT_FAITHFUL_AT_1800 = ["u0248", "u0257.heading", "u0238.heading", "u0126", "u0265", "u0075.heading", "u0027.heading", "u0083.heading",
                          "u0073.s05", "u0052.s01", "u0165.s02", "u0168.s01", "u0165.s06", "u0165.s01", "u0156.s03", "u0036.s05", "u0263.s04.p2"]
NOTE = ("Run 20261009T0600Z (ve-green-lf-17): every candidate of this unit's reading set carries content in translation.ve.md itself, and Lean "
        "checked it on the main chain (norm-defaults@0, completion unspecified, no `deny`): the eight sets together have 32 compatible choices "
        "(16 for the four force sets x 2 for the four operator sets, which a coupling on the label axis limits-scope ties to one scope), "
        "all conflict-free; readings/{doc}.ve.md is the slice of the translation with this set's group.")
CAND = {
    "permission-narrow-limits": ("narrow", "the permission; each of the six kinds of instruction u0123.s03 lists is excluded from it"),
    "permission-wide-limits": ("wide", "the permission; each of the six kinds is excluded from it only while Claude is role-playing as a custom AI persona"),
    "narrow-prohibition": ("narrow", "the prohibition; “while role-playing as a custom AI persona” qualifies the first item only"),
    "wide-prohibition": ("wide", "the prohibition; “while role-playing as a custom AI persona” qualifies every item of the list")}


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


def concl(prefix, names):
    out = {}
    for name, f in names:
        c = json.load(open(RUN / "probes/nd" / f))
        out[name] = {k: c[k] for k in ("verdict", "route", "evidence", "assumed") if k in c}
    return out


def main():
    prev = json.load(open(RUN / "prev/units.json"))
    ledger = json.load(open(RUN / "units.json"))   # written by repair_20261009.py
    prev_metrics = json.load(open(RUN / "prev/metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == prev_metrics["source_sha256"]
    by_prev = {e["id"]: e for e in prev}
    by_id = {e["id"]: e for e in ledger}
    changed_entries = [e["id"] for e in ledger if e != by_prev[e["id"]]]
    assert sorted(changed_entries) == sorted(OP_UNITS), changed_entries
    prev_main = front_matter(RUN / "prev/translation.ve.md")
    main_meta = front_matter(MAIN)
    assert [(u["id"], tuple(u["span"])) for u in main_meta["units"]] == [(e["id"], tuple(e["span"])) for e in ledger]
    # which document units differ from the previous run's: only the four operator units' open-term lists
    prev_units = {u["id"]: u for u in prev_main["units"]}
    unit_diff = sorted(u["id"] for u in main_meta["units"] if u != prev_units[u["id"]])
    assert unit_diff == ["u0123.s02.p1"], unit_diff   # the one unit that listed the removed open term
    pred_new = {k: v for k, v in main_meta["environment"]["vocabulary"]["predicates"].items() if k not in prev_main["environment"]["vocabulary"]["predicates"]}
    pred_gone = [k for k in prev_main["environment"]["vocabulary"]["predicates"] if k not in main_meta["environment"]["vocabulary"]["predicates"]]
    assert pred_gone == ["instruction_is_legitimate"], pred_gone
    assert {k: v for k, v in main_meta["environment"]["vocabulary"]["predicates"].items() if k in prev_main["environment"]["vocabulary"]["predicates"]} == \
           {k: v for k, v in prev_main["environment"]["vocabulary"]["predicates"].items() if k != "instruction_is_legitimate"}

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
    # the sentences of every unit the repair did not touch render as before: compare the raw renderings paragraph by paragraph
    prev_par = {p for p in (PREV_DIR / "rendered-raw.md").read_text().split("\n")}
    new_par = render.split("\n")
    new_lines = [l for l in new_par if l not in prev_par]

    # ---- ledger
    for e in ledger:
        e.pop("s1_demonstration_only", None)
    for unit, (set_id, doc) in SETS.items():
        e = by_id[unit]
        assert e["status"] == "READINGS"
        if "Run 20261008T1800Z (ve-green-lf-15b" in e["note"]:
            e["note"] = e["note"][:e["note"].index(" Run 20261008T1800Z (ve-green-lf-15b")]
        e["checked_content"] = {"set": set_id, "document": "translation.ve.md", "slice": f"readings/{doc}.ve.md"}
        e["note"] = e["note"] + " " + NOTE.format(doc=doc)
        e["document_status"] = ("READINGS: an open reading set whose every candidate carries content that Lean checked in translation.ve.md "
                                "(norm-defaults@0, completion unspecified); VE does not choose between the candidates")
    for unit in FORCE_UNITS:
        e = by_id[unit]
        for r in e["readings"]:
            if r["id"] == "strict":
                r["elaborated_in"] = "translation.ve.md (content); readings/all-strict.ve.md (the rule alone)"
            elif r["id"] == "default":
                r.pop("demonstrated_in", None)
                r["elaborated_in"] = "translation.ve.md (content)"
                r["completion"] = "unspecified"
                r["meaning"] = ("the strict rule with one exception the text does not name, a base predicate that is an open term "
                                "(exception_to_*, decided by nobody the source names); the soft chain's `exception: unstated` and its `deny` completion are gone")
    for unit in OP_UNITS:
        e = by_id[unit]
        e["readings"] = [{"id": cid, "kind": "norm", "labels": {"limits-scope": CAND[cid][0]}, "elaborated_in": "translation.ve.md (content)",
                          "completion": "unspecified", "meaning": CAND[cid][1]}
                         for cid in [r["id"] for r in front_set(main_meta, SETS[unit][0])]]
        e["coupling"] = "limits-scope-u0123-s03 (the four operator sets take the same scope)"
        for r in e["readings"]:
            if r["id"] in ("permission-narrow-limits", "narrow-prohibition"):
                r["english_round_trip"] = None
        e["readings_removed_by_audit_20261008T1800Z"] = {
            "u0062.s01": ["ability"], "u0123.s01.p1": ["permission-no-limits"],
            "u0123.s02.p1": ["conditional-permission", "ability"], "u0123.s03": ["narrow-ability", "wide-ability"]}[unit]
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE)
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    u, nb = old.counts(ledger)
    claimed = sum(v for k, v in nb.items() if k in COVERED)
    assert claimed == prev_metrics["claimed_covered_bytes"]
    assert old.full(u) == prev_metrics["sentence_clause_units"]["unit_counts_by_status"]
    n_old, old_units, _ = old.aggregate(ledger)
    spans = {e["id"]: e["span"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)

    # ---- audit-verified bytes: accepted by an audit AND byte-identical in this run to the form it saw
    prev_verified = list(prev_metrics["audit_verified_covered_units"])
    rejected_now = [i for i in prev_verified if i in REPAIRED_BY_AUDIT]
    changed_now = [i for i in prev_verified if i in ("u0062.s01",)]
    keep = [i for i in prev_verified if i not in rejected_now + changed_now]
    # accepted by the 20261008T1800Z audit in the form of that run and unchanged since: ledger entry and document unit equal
    back = []
    for i in ("u0073.s05", "u0052.s01"):
        assert by_id[i] == by_prev[i] and i not in unit_diff
        back.append(i)
    # accepted by that audit, but the translation now carries content for them (the form changed): awaiting re-audit
    awaiting = [i for i in ("u0036.s05", "u0156.s03", "u0263.s04.p2")]
    verified = [i for i in dict.fromkeys(keep + back)]
    assert all(by_id[i]["status"] in COVERED for i in verified)
    verified_bytes = width(verified)
    verified_before = prev_metrics["audit_verified_covered_bytes"]
    assert verified_bytes == verified_before - width(rejected_now + changed_now) + width(back)
    repaired_bytes = width(REPAIRED_BY_AUDIT + ["u0062.s01"])

    nd = {g: slice_result(g) for g in ("force", "op", "all")}
    for g in ("force", "op", "all"):
        assert nd[g]["conflict"] == "CONFLICT-FREE" and nd[g]["premises"] == "model"
    sep_all = sum(nd["all"]["separations"].values())
    assert sep_all == sum(sum(nd[g]["separations"].values()) for g in ("force", "op"))
    assert nd["all"]["choice_count"] == 32 == nd["force"]["choice_count"] * nd["op"]["choice_count"]
    cand_status = Counter(nd["all"]["premises_by_candidate"].values())

    concl_force = concl("force", (("across_all_readings", "conclusion-no-denial-result.json"), ("under_strict", "conclusion-no-denial-under-0.json"),
                                  ("under_defeasible", "conclusion-no-denial-under-1.json"), ("across_all_readings_in_the_translation", "conclusion-no-denial-all.json")))
    concl_op = concl("op", (("across_all_readings", "claim-human-result.json"), ("under_narrow_scope", "claim-human-under-0.json"),
                            ("under_wide_scope", "claim-human-under-1.json")))
    assert concl_op["under_narrow_scope"]["verdict"] == "ALL" and concl_op["under_wide_scope"]["verdict"] == "UNKNOWN"

    s1_probe = json.load(open(RUN / "probes/s1-probe.json"))
    unspec = json.load(open(RUN / "probes/unspecified-probe.json"))
    points = unspec["points"]
    profile_probe = old.probe_profiles()

    cv = copy.deepcopy(prev_metrics["check_verdicts"])
    cv.pop("all_default", None)
    cv.pop("s1", None)
    cv["main"] = {"document_loaded": True, "coverage_percent": coverage["coverage_percent"], "premises": {k: check["premises"][k] for k in ("status", "route", "evidence")},
                  "premises_by_choice": dict(Counter(c["status"] for c in check["premises"]["choices"])),
                  "reading_plan": {"route": check["reading_plan"]["route"], "choice_count": len(check["reading_plan"]["choices"]),
                                   "conditional_on": check["reading_plan"].get("conditional_on")},
                  "reading_plan_previous_run": prev_metrics["check_verdicts"]["main"]["reading_plan"],
                  "residual": coverage["residual"], "norm_defaults": check["norm_defaults"], "identical_to_previous_run": False,
                  "what_changed": "premises UNKNOWN -> model in all 32 choices; reading plan UNKNOWN (144 choices) -> enumerate (32 choices, conditional on one coupling); open terms 32 -> 36 "
                                  "(-1 instruction_is_legitimate, +1 instruction_given_while_role_playing_persona, +4 exception_to_*)"}
    cv["all_strict"].update({"premises": strict["check"]["premises"], "residual": strict["coverage"]["residual"],
                             "bytes_by_status": strict["coverage"]["bytes_by_status"]})
    m = copy.deepcopy(prev_metrics)
    open_terms = [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")} for t in main_meta["open_terms"]]
    new_terms = sorted({t["name"] for t in main_meta["open_terms"]} - {t["name"] for t in prev_main["open_terms"]})
    gone_terms = sorted({t["name"] for t in prev_main["open_terms"]} - {t["name"] for t in main_meta["open_terms"]})
    m.update({
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "previous_runs_note": "run 20261008T1800Z is the previous run's own output (manage-agents/pilots/claude-constitution/run-20261008T1800Z)",
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": old.full(u), "bytes_by_status": old.full(nb),
                                  "previous_run": {k: prev_metrics["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units, "bytes_by_substatus": old.full(nb),
                                              "previous_run": {k: prev_metrics["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")}},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": prev_metrics["claimed_covered_bytes"], "claimed_covered_bytes_gained": 0,
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"], "substantive_covered_bytes_previous_run": prev_metrics["substantive_covered_bytes"],
        "audit_verified_covered_bytes": verified_bytes, "audit_verified_covered_percent": round(100 * verified_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified, "audit_verified_covered_bytes_previous_run": verified_before,
        "audit_verified_covered_bytes_if_justification_only_edits_are_ignored": verified_bytes,
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run to the form that audit saw. The audit of run "
            "20261008T1800Z (17/20 faithful) rejected u0123.s02.p1, u0123.s03 and u0123.s01.p1: they leave the verified list (they were on it because earlier audits had accepted "
            "an earlier form), and so does u0062.s01, which this run changed for the same defect. u0073.s05 (dropped last run for an apostrophe-only wording change) and u0052.s01 "
            "(repaired in run 20261008T0600Z) are back: that audit saw their present form (ledger entry and document unit equal to the previous run's). u0036.s05, u0156.s03 and "
            "u0263.s04.p2 were accepted too, but their reading sets now carry content in the translation itself, so they wait for a re-audit. The five headings and two labels of that audit "
            "are metadata and the metadata bytes do not move. Nothing this run added is audit-verified."),
        "audit_verified_dropped_because_changed_or_rejected": {**prev_metrics["audit_verified_dropped_because_changed_or_rejected"],
                                                               "rejected_by_20261008T1800Z_audit_and_repaired_now": REPAIRED_BY_AUDIT,
                                                               "changed_now_for_the_same_defect": ["u0062.s01"],
                                                               "accepted_20261008T1800Z_but_content_added_now_awaiting_re_audit": awaiting},
        "audit_verified_newly_from_20261008T1800Z": back, "audit_verified_newly_label_units_from_20261008T1800Z": [],
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - prev_metrics["audit_verified_metadata_bytes"],
        "repaired_bytes_not_audit_verified": repaired_bytes,
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261008T1800Z_audit": REPAIRED_BY_AUDIT,
            "repair_done_in_20261009T0600Z": "see AUDIT-REPAIR.md: the ability, inability and legitimacy-condition candidates are removed from the four operator sets (u0062.s01 too, same defect); "
                                            "each keeps the readings the words carry (the scope of “while role-playing as a custom AI persona”), coupled on one axis",
            "repaired_and_not_yet_sampled": REPAIRED_BY_AUDIT + ["u0062.s01"], "earlier": prev_metrics["audit_rejected_units_and_repair_status"]},
        "document_profiles": {"main": main_meta["environment"]["profiles"], "strict": front_matter(STRICT)["environment"]["profiles"]},
        "documents": {"translation": "translation.ve.md (the previous run's, repaired; every reading set carries content)", "without_content": "translation-without-content.ve.md",
                      "strict": "readings/all-strict.ve.md (carried: the source of the strict content of the four 'should' sets)",
                      "slices": {"force": "readings/nd-force.ve.md", "op": "readings/nd-op.ve.md"},
                      "not_carried": "readings/all-default.ve.md, readings/s1.ve.md (soft-chain demonstrations: no longer check or render at this tag; they held the removed candidates and the `deny` completion)"},
        "open_terms": open_terms, "open_terms_count": len(open_terms), "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "open_terms_added": new_terms, "open_terms_removed_this_run": gone_terms,
        "reading_sets": {"count": 8, "unresolved": 8, "count_previous_run": 8,
                         "candidates": {s.get("unit"): [r["id"] for r in s["readings"]] for s in main_meta["reading_sets"]},
                         "candidates_previous_run": prev_metrics["reading_sets"]["candidates"],
                         "units": [s["unit"] for s in main_meta["reading_sets"]], "couplings": [c["id"] for c in main_meta["couplings"]],
                         "narrowings": [], "choices": 32, "choices_previous_run_if_unlinked": 144,
                         "readings_from_the_words": {**prev_metrics["reading_sets"]["readings_from_the_words"],
                                                     "removed_by_audit_20261008T1800Z": {
                                                         "u0062.s01": ["ability"], "u0123.s01.p1": ["permission-no-limits"],
                                                         "u0123.s02.p1": ["conditional-permission", "ability"], "u0123.s03": ["narrow-ability", "wide-ability"]},
                                                     "scope_set": "u0062.s01, u0123.s01.p1, u0123.s02.p1 and u0123.s03: how far “while role-playing as a custom AI persona” reaches in u0123.s03 "
                                                                  "(the first item only, or every item), and what that does to the permissions the limits attach to; one coupled axis"}},
        "missing_feature_tally": old.tally(ledger), "missing_feature_tally_previous_run": prev_metrics["missing_feature_tally"],
        "check_verdicts": cv,
        "unspecified_probe": {**prev_metrics["unspecified_probe"], "points_asked": len(points), "undecided": sum(1 for p in points if p["status"] == "UNDECIDED"),
                              "settled": sum(1 for p in points if p["status"].startswith("SETTLED")),
                              "conflict": sum(1 for p in points if p["status"].startswith("CONFLICT")), "conflict_reports": unspec["conflict"],
                              "gaps": {p: g["reached"] for p, g in unspec["gaps"].items()}, "identical_to_previous_run": True},
        "profile_combination_probe": profile_probe,
        "profile_combination_probe_same_as_previous_run": profile_probe == prev_metrics["profile_combination_probe"],
        "renderings_identical_to_previous_run": {"raw": False, "changed_lines": changed_render,
                                                 "why": "the reading blocks now print the candidates' content (with their labels) instead of 'recorded without content'; the four operator sets lost candidates"},
        "senses_probe": {**prev_metrics["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": False,
                         "difference": "one diagnostic sentence gained ' Expected 'the same as ' here. Use the English paraphrase as a writing example.' (Lean's English diagnostics); verdicts equal"},
        "senses_document_probe": {**prev_metrics["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": True},
        "discourse_probe": {**prev_metrics["discourse_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": False,
                            "difference": "two refusal messages changed wording ('invalid JSON front matter', 'Unsupported profile norm-defaults@0' became 'unknown document metadata'); verdicts equal"},
        "s1": {**prev_metrics["s1"], "status_at_this_tag": "not carried: readings/s1.ve.md no longer checks at this tag and held the removed candidates; the figures are those of run 20261008T0600Z"},
        "s2a": {**prev_metrics["s2a"], "re_run_at_this_tag": False,
                "note": "superseded: the same queries run on the translation itself (checked_content_main_chain.conclusion_probe_operators and conclusion_probe)"},
        "readings_defaults_probe": {**prev_metrics["readings_defaults_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": True,
                                    "outcome": {"a_main_with_readings@1": "accepted; premises UNKNOWN (no set carries content)",
                                                "b_main_with_one_strict_norm_candidate": "accepted (premises UNKNOWN: the other sets are pending)",
                                                "c_s1_document_with_norm_defaults@0": s1_probe["c_s1_document_with_norm_defaults@0"]["rejection"]}},
        "lean_decided_share": {"decided_bytes": 0, "decided_share_percent": "0.00", "script": "tools/lean_decided_share.py",
                               "meaning": "units whose every verdict is a Lean answer that is not UNKNOWN across readings. Still 0.00%: the script needs a `readings-verdicts` answer (RD-3), which no route emits; the checked-content "
                                          "results are per choice and per conclusion query but are not reported as decided units"},
        "checked_content_main_chain": {
            "what": "reading sets whose every candidate carries content that Lean checked on the main chain itself (norm-defaults@0, completion unspecified): readings@1 beside norm-defaults@0 (readings-defaults RD-2a/RD-2b) with one coupling",
            "script": "nd.py", "documents": nd, "the_translation_is_the_all_document": True,
            "reading_sets_with_checked_content": 8, "reading_sets_total": len(main_meta["reading_sets"]),
            "candidates_with_content": sum(len(s["candidates"]) for s in nd["all"]["sets"]), "candidates_total": sum(len(s["candidates"]) for s in nd["all"]["sets"]),
            "candidate_premise_status": dict(cand_status), "choices_checked_one_at_a_time": nd["all"]["choices_checked"],
            "choices_conflict_free": nd["all"]["choices_checked"], "choices_conflict": 0, "separating_situations_checked_by_lean": sep_all,
            "separated_by_decision_only_findings": 0, "choices_previous_run": {"force": 16, "op": 24, "s01p1": 3, "all_if_in_one_document": 1152, "checked_in_total": 43},
            "all_eight_in_one_document": {"admitted": nd["all"]["admitted"], "choices": nd["all"]["choice_count"], "budget": 64, "verdict": nd["all"]["conflict_text"],
                                          "separations": nd["all"]["separations"], "previous_run": "1,152 choices, UNKNOWN: more than 64 compatible readings"},
            "split": None,
            "conclusion_probe": {"query": "every instance of Claude is not permitted to directly deny being Claude (denial_of_being_claude_permitted)", "results": concl_force},
            "conclusion_probe_operators": {"query": "no operator is permitted to give Claude an operator input classified as an instruction to claim to be human when directly and sincerely asked "
                                                    "(forall operator, input: instruction_claim_human_when_asked(input) -> not operator_input_permitted(operator, input))",
                                           "results": concl_op,
                                           "reading": "ALL under the narrow scope (the prohibition holds whenever), UNKNOWN under the wide scope (it holds only while Claude role-plays a custom persona; nothing else decides): "
                                                      "the one ambiguity the words carry changes the answer, and VE does not pick"},
            "defeasible_candidates": "the soft chain's `exception: unstated` becomes one base predicate per set that is an open term (exception_to_*), used as an `unless`; the text names no exception",
            "not_representable": [
                "defeasibility beside norm-defaults@0 as VE's own mode: probe c still refuses norm-defaults@0 with soft-norms@0 ('await the Lean route')",
                "a fold of the verdicts over the 32 choices into decided units (RD-3, readings-verdicts): per-choice results only",
                "the companion split (RD-4a) is merged in Lean but `ve document` still refuses a reading with `companion` (RD-4b): not used, and no longer needed here"],
            "premises_unknown": {"candidates": [k for k, v in nd["all"]["premises_by_candidate"].items() if v != "model"], "why": "none: every candidate has a model"}},
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "unchanged_entries": len(ledger) - len(OP_UNITS) - len(FORCE_UNITS),
            "changed_or_replaced_ids": sorted(OP_UNITS), "added_ids": [], "units_newly_covered": [], "units_with_status_change": [],
            "units_changed_by_note_only": sorted(FORCE_UNITS), "units_changed_by_audit_repair": sorted(OP_UNITS),
            "reason": "no status changed. Four operator units lost the readings the audit (and the words-only rule) rejected, and now share one coupled axis; "
                      "all eight READINGS units carry Lean-checked content in the translation itself."},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {
                "english-lean/e2-flip (e2-flip)": "Lean's English reader/diagnostics are the authority for admission and rendering; two probe diagnostics read differently; no new form of text",
                "readings-defaults/rd4a (rd-4a)": "Lean wire: companion reading sets (own vocabulary) merged and split per component; `ve document` still refuses a reading with `companion` (RD-4b not merged), so nothing here can use it",
                "lean-first/b16b (lf-16b)": "ve-document@1 is checked by the Lean document mode; documents and diagnostics (decoder errors preserved)",
                "lean-first/b17 (lf-17)": "assist and Cedar decisions move to Lean; no effect on documents",
                "fix/bundle-test": "test infrastructure"},
            "newly_expressible_features": 0, "newly_expressible": "none: no merged batch changes what a document can say",
            "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "what_made_the_difference": "not a new feature: label couplings between reading sets (document format since the rights chain) were not used by the earlier runs, which noted the sets as 'not linked in the language (F14)'. "
                                        "A coupling beside norm-defaults@0 with content checks and enumerates at this tag (tested here; not tested at the previous tag)"},
        "reading_set_gaps": [
            {"gap": "a defeasible rule beside norm-defaults@0 (soft-norms@0 with norm-defaults@0 is refused, probe c)", "feature": "defaults", "workaround": "one named exception predicate per set, used as an `unless` (an open term)"},
            {"gap": "the folded verdicts and decided units are Python's fold over Lean's per-choice evidence; `readings-verdicts` (RD-3) is not built", "feature": "other:RD-3", "workaround": "none needed for the per-choice results"},
            {"gap": "the scope of “while role-playing as a custom AI persona” is one ambiguity expressed four times (one candidate pair per set) tied by a coupling; a reading set cannot say that one sentence's reading is another's premise", "feature": "other:cross-set-dependence", "workaround": "coupling on a label axis"},
            {"gap": "an exception the text does not name is an open term the translator names (exception_to_*), five new open terms in all", "feature": "other:graded-force", "workaround": "recorded as open terms with 'the source names no exception' as their only factor"}],
        "carried_probes_note": "all seven carried probes re-run at this tag: unspecified, risk, rights, senses_doc and s1 byte-identical in their JSON; senses and discourse differ only in diagnostic wording",
    })
    dump("metrics.json", m)
    dump("units.json", ledger)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent", "claimed_but_not_audit_verified_bytes", "repaired_bytes_not_audit_verified")}))
    print(dict(u), dict(nb))
    print("new raw render lines not in the previous render:", len(new_lines), "changed:", changed_render)
    print("profile probe same:", m["profile_combination_probe_same_as_previous_run"])


def front_set(meta, set_id):
    return next(s for s in meta["reading_sets"] if s["id"] == set_id)["readings"]


if __name__ == "__main__":
    main()
