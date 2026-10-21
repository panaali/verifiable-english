#!/usr/bin/env python3
"""Run 20261005T1800Z: re-run VE on the unchanged translation at ve-green-english-lean-s2, write the ledger, rendering and metrics.

Run after probe_unspecified.py, probe_s1.py, probe_risk.py, probe_discourse.py, probe_rights.py, s1.py and the S2a conclusion
probes (probes/s2/), from anywhere (PATH must contain ~/.elan/bin for the Lean routes):
    uv run python usecases/claude-constitution-pilot/run-20261005T1800Z/finish.py

The translation is the previous run's (prev/translation.ve.md, copied unchanged): the previous audit (20261005T0600Z, 20/20 faithful)
rejected nothing and no merged feature adds a form of text, so no unit is upgraded. This script therefore does not build; it
re-checks that the ledger and the documents are unchanged, re-measures them with VE at this tag, recomputes the audit-verified
bytes from the new audit, and adds the S2a (composition stage S2a, compose-s2) measurement on the demonstration companion.
finish_0600.py is the previous run's script; its constants and renderers are reused (it is not run).
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))
import finish_0600 as old  # noqa: E402

RUN_ID = "20261005T1800Z"
PREV_RUN = "20261005T0600Z"
TAG = "ve-green-english-lean-s2"
PREV_TAG = "ve-green-difffuzz"
COVERED = old.COVERED
DOCS = old.DOCS
SOURCE = old.SOURCE
ve, front_matter = old.ve, old.front_matter
dump = lambda p, o: (RUN / p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")

# the 20261005T0600Z audit (AUDIT-20261005T0600Z-received.md, 20/20): the units it sampled, by the status each has in the ledger
AUDIT_20261005 = [l.split()[0] for l in (RUN / "AUDIT-20261005T0600Z-received.md").read_text().split("```text")[1].split("```")[0].strip().splitlines()
                  if l.split()[1] == "FAITHFUL"]
AUDIT_20261005_ALL = [l.split() for l in (RUN / "AUDIT-20261005T0600Z-received.md").read_text().split("```text")[1].split("```")[0].strip().splitlines()]
AUDIT_20261005_REJECTED = [u for u, v in AUDIT_20261005_ALL if v != "FAITHFUL"]


def main():
    # ---- ledger and documents are the previous run's, byte for byte
    prev = json.load(open(RUN / "prev/units.json"))
    ledger = json.load(open(RUN / "units.json"))
    assert ledger == prev, "units.json must start as the previous run's"
    for rel in ("translation.ve.md",):
        assert (RUN / rel).read_bytes() == (RUN / "prev" / rel).read_bytes(), rel
    for rel in ("readings/all-strict.ve.md", "readings/all-default.ve.md", "readings/s1.ve.md"):
        assert (RUN / rel).read_bytes() == (RUN / "prev" / rel).read_bytes(), rel
    prev_metrics = json.load(open(RUN / "prev/metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == prev_metrics["source_sha256"]

    # ---- VE runs at this tag
    results = {}
    for key, path in DOCS.items():
        rel = str(path.relative_to(ROOT))
        results[key] = {"check": json.loads(ve("document", "check", rel)),
                        "coverage": json.loads(ve("document", "coverage", rel)),
                        "render": ve("document", "render", rel)}
    main_meta, soft_meta = front_matter(DOCS["main"]), front_matter(DOCS["default"])
    prev_check = {"main": json.load(open(RUN / "check.json")), "strict": json.load(open(RUN / "readings/check-all-strict.json")),
                  "default": json.load(open(RUN / "readings/check-all-default.json"))}
    same_verdicts = {k: results[k]["check"] == prev_check[k] for k in prev_check}
    assert all(same_verdicts.values()), same_verdicts        # main, strict and default: the previous run's check output, unchanged
    same_render = {k: results[k]["render"] == (RUN / "readings" / name).read_text()
                   for k, name in (("strict", "rendered-all-strict.md"), ("default", "rendered-all-default.md"))}
    assert all(v for v in same_render.values()), same_render
    dump("check.json", results["main"]["check"])
    dump("coverage.json", results["main"]["coverage"])
    dump("readings/check-all-strict.json", results["strict"]["check"])
    dump("readings/check-all-default.json", results["default"]["check"])
    dump("readings/check-s1.json", results["s1"]["check"])
    dump("readings/coverage-s1.json", results["s1"]["coverage"])
    (RUN / "readings/rendered-s1.md").write_text(results["s1"]["render"])
    (RUN / "readings/rendered-all-strict.md").write_text(results["strict"]["render"])
    (RUN / "readings/rendered-all-default.md").write_text(results["default"]["render"])
    rendered = old.annotate_hard(old.expand_main(results["main"]["render"], main_meta, ledger), ledger)
    assert rendered == (RUN / "rendered.md").read_text(), "rendered.md changed"
    prev_s1 = json.load(open(RUN / "prev/readings/check-s1.json"))

    # ---- ledger invariants
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE)
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    assert [(u["id"], tuple(u["span"])) for u in main_meta["units"]] == [(e["id"], tuple(e["span"])) for e in ledger]
    u, nb = old.counts(ledger)
    n_old, old_units, _ = old.aggregate(ledger)
    claimed = sum(v for k, v in nb.items() if k in COVERED)
    doc_cov = results["main"]["coverage"]
    assert doc_cov["bytes_by_status"].get("OPEN", 0) == nb["OPEN"] + nb["READINGS"]
    assert claimed == prev_metrics["claimed_covered_bytes"]
    assert old.full(u) == prev_metrics["sentence_clause_units"]["unit_counts_by_status"]
    status = {e["id"]: e["status"] for e in ledger}
    spans = {e["id"]: e["span"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)

    # ---- S2a: what the superposed route gives the demonstration companion (readings/s1.ve.md)
    s1c = results["s1"]["check"]
    rd, pr = s1c["readings"], s1c["premises"]
    assert prev_s1["premises"]["status"] == "UNKNOWN" and pr["status"] == "model" and pr["route"] == "superposed"
    cand_status = {f"{c['set']}:{c['index']}": c["status"] for c in pr["candidates"]}
    set_of_unit = {s["unit"]: s["set"] for s in rd["sets"]}
    concl = {}
    for name, f in (("across_all_readings", "conclusion-no-denial-result.json"), ("under_must", "conclusion-no-denial-under-0.json"),
                    ("under_should", "conclusion-no-denial-under-1.json")):
        r = json.load(open(RUN / "probes/s2" / f))
        concl[name] = {k: r[k] for k in ("verdict", "route", "evidence", "assumed", "budget") if k in r}
        concl[name]["english"] = r.get("english", [])
    s2a = {
        "feature": "composition S2a (compose-s2, merged before ve-green-compose-s2): verdicts across readings of a content-bearing reading "
                   "set on the soft and norms chains, by one superposed document; `ve document check` reports route, choice, model, "
                   "per-candidate premise status, conflict status under every reading, dead readings; `ve document readings --conclusion` "
                   "answers ALL/SOME/NONE across readings or under named readings (`--under set:index`)",
        "document": "readings/s1.ve.md", "demonstration_only": True,
        "demonstration_note": "readings/s1.ve.md completes duties and the operator permission with `deny` (soft-norms@0 needs a completion), "
                              "which the source does not state; nothing in it is claimed for any unit. S2a does not apply to the main "
                              "document (norm-defaults@0: `readings@1` content is the named abstention, probes/s1-probe.json b).",
        "before_this_tag": {"premises": prev_s1["premises"], "conflict_status": prev_s1["readings"]["status"]},
        "now": {"premises_status": pr["status"], "route": pr["route"], "evidence": pr["evidence"], "choice": pr["choice"],
                "conflict_status": rd["status"], "conflict_evidence": rd["conflict"]["evidence"], "route_of_readings": rd["route"],
                "choice_count": rd["choice_count"], "choices_checked": rd["choices_checked"], "dead_readings": rd["dead_readings"],
                "reading_premises_in_force": len(rd["reading_premises"]), "sizes": rd["sizes"], "not_superposable": rd["not_superposable"],
                "english": rd["english"]},
        "candidate_premise_status": cand_status,
        "candidate_status_counts": dict(Counter(cand_status.values())),
        "candidates_without_model": [k for k, v in cand_status.items() if v != "model"],
        "candidates_without_model_note": "the ability candidates of u0062.s01 and u0123.s02.p1: no model and no certificate within budget "
                                         "(UNKNOWN, never `dead` without a certificate, spec 4.6)",
        "units_with_a_set_in_the_companion": {k: v for k, v in set_of_unit.items()},
        "conclusion_probe": {
            "unit": "u0125.s04.p2", "formula": "every instance of Claude: denial_of_being_claude_avoidance_required (probes/s2/conclusion-no-denial.json)",
            "results": concl,
            "reading": "ALL under the strict reading (*must*), with a Lean-replayed certificate and the English \"Read sentence 471 as *must*: "
                       "the conclusion follows\"; not entailed (UNKNOWN: prover budget, no certificate) under the *should* reading; and "
                       "UNKNOWN across all readings because the 8 open sets give more than 64 compatible choices (E28), so SOME/NONE "
                       "cannot be reported. The same differences were visible only as separate companion documents before.",
        },
        "companions_redundant": "partly: the superposed document gives under `--under` every strict (or default) choice what all-strict (or "
                                "all-default) would give for the force sets, and the premise status 'model' agrees; they are not redundant for "
                                "the main document, which is norm-defaults@0 (the strict companion is the one that completes nothing with deny)",
        "claimed": False,
        "units_upgraded": 0,
        "load_and_check_seconds": "about 7 minutes for `ve document check` of readings/s1.ve.md at this tag (6 to 7 minutes in two runs); the "
                                  "conclusion queries took 41 to 62 seconds each",
    }

    # ---- audit-verified bytes: accepted by an independent audit of this lineage AND byte-identical in this run to the form it saw
    # The 20261005T0600Z audit saw the previous run's form, and this run keeps every ledger entry and document unit unchanged.
    ledger_by_id = {e["id"]: e for e in ledger}
    prev_verified_sub = list(prev_metrics["audit_verified_covered_units"])
    accepted = [i for i in AUDIT_20261005 if i in ledger_by_id]
    assert len(accepted) == 20 and not AUDIT_20261005_REJECTED
    accepted_sub = [i for i in accepted if status[i] in COVERED and status[i] != "LABELLED"]
    accepted_lab = [i for i in accepted if status[i] == "LABELLED"]
    verified_sub = list(dict.fromkeys(prev_verified_sub + accepted_sub))
    newly_sub = [i for i in verified_sub if i not in prev_verified_sub]
    cand_lab = list(dict.fromkeys(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED + accepted_lab))
    verified_lab = [i for i in cand_lab if i in ledger_by_id and status[i] == "LABELLED"]
    newly_lab = [i for i in accepted_lab if i not in set(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED)]
    assert all(status[i] in COVERED for i in verified_sub)
    sub_bytes, lab_bytes = width(verified_sub), width(verified_lab)
    assert lab_bytes == prev_metrics["audit_verified_metadata_bytes"] and not newly_lab, (lab_bytes, newly_lab)
    assert sub_bytes == prev_metrics["audit_verified_covered_bytes"] + width(newly_sub)
    repaired_unverified = sorted(set(prev_metrics["audit_rejected_units_and_repair_status"]["repaired_in_20261005T0600Z"]) - set(verified_sub))
    prev_ap = prev_metrics["audit_rejected_units_and_repair_status"]

    # ---- profile combinations at this tag
    profile_probe = old.probe_profiles()
    s1_probe = json.load(open(RUN / "probes/s1-probe.json"))
    unspecified = json.load(open(RUN / "probes/unspecified-probe.json"))

    m = copy.deepcopy(prev_metrics)
    m.update({
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "sentence_clause_units": {**prev_metrics["sentence_clause_units"],
                                  "previous_run": {k: prev_metrics["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {**prev_metrics["aggregated_to_previous_boundaries"],
                                              "previous_run": {k: prev_metrics["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")}},
        "claimed_covered_bytes_previous_run": prev_metrics["claimed_covered_bytes"], "claimed_covered_bytes_gained": 0,
        "substantive_covered_bytes_previous_run": prev_metrics["substantive_covered_bytes"],
        "audit_verified_covered_bytes": sub_bytes, "audit_verified_covered_percent": round(100 * sub_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified_sub,
        "audit_verified_covered_bytes_previous_run": prev_metrics["audit_verified_covered_bytes"],
        "audit_verified_metadata_bytes": lab_bytes, "audit_verified_metadata_percent": round(100 * lab_bytes / len(SOURCE), 4),
        "audit_verified_metadata_bytes_previous_run": prev_metrics["audit_verified_metadata_bytes"],
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run to the form that "
            "audit saw. The latest audit (20261005T0600Z, 20/20, a verdict for every sampled unit) saw the previous run's form; this run keeps "
            "every ledger entry and every document unit as it was (finish.py asserts the ledger, the main document and the three companions "
            "equal the previous run's), so every acceptance counts. It accepted u0123.s01.p1, u0062.s01 and u0123.s02.p1 (the units the "
            "20261004T1800Z audit rejected and the previous run repaired) and u0165.s03 and u0165.s04, none of them verified before: they "
            "join. It accepted seven labels that were verified already (label bytes unchanged). u0123.s03 was repaired the same way but not "
            "sampled, so it stays claimed, not verified."),
        "audit_verified_newly_from_20261005T0600Z": newly_sub,
        "audit_verified_newly_label_units_from_20261005T0600Z": newly_lab,
        "audit_verified_dropped_because_changed_or_rejected": {"changed_since_acceptance": [], "rejected_by_an_audit_and_not_re_accepted": []},
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261005T0600Z_audit": AUDIT_20261005_REJECTED,
            "repair_needed_in_20261005T1800Z": "none: the 20261005T0600Z audit accepted all 20 sampled units, so there was nothing to repair",
            "accepted_by_20261005T0600Z_audit_after_repair": ["u0123.s01.p1", "u0062.s01", "u0123.s02.p1"],
            "repaired_in_20261005T0600Z_and_not_yet_sampled": repaired_unverified,
            "earlier": {k: v for k, v in prev_ap.items()},
        },
        "claimed_but_not_audit_verified_bytes": claimed - sub_bytes - lab_bytes,
        "repaired_bytes_not_audit_verified": width(repaired_unverified),
        "document_profiles": {k: front_matter(v)["environment"]["profiles"] for k, v in DOCS.items()},
        "check_verdicts": {**prev_metrics["check_verdicts"],
                           "main": {**prev_metrics["check_verdicts"]["main"],
                                    "identical_to_previous_run": same_verdicts["main"]},
                           "all_strict": {**prev_metrics["check_verdicts"]["all_strict"], "identical_to_previous_run": same_verdicts["strict"]},
                           "all_default": {**prev_metrics["check_verdicts"]["all_default"], "identical_to_previous_run": same_verdicts["default"]},
                           "s1": {"premises": {k: v for k, v in pr.items() if k not in ("model", "candidates")},
                                  "readings": {k: v for k, v in rd.items() if k in ("separations", "findings", "route", "choice_count", "choices_checked",
                                                                                       "status", "dead_readings", "sizes")},
                                  "residual": results["s1"]["coverage"]["residual"],
                                  "bytes_by_status": results["s1"]["coverage"]["bytes_by_status"]}},
        "s2a": s2a,
        "unspecified_probe": {**prev_metrics["unspecified_probe"], "identical_to_previous_run": True},
        "profile_combination_probe": profile_probe,
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "unchanged_entries": len(ledger), "changed_or_replaced_ids": [],
            "added_ids": [], "units_newly_covered": [], "units_newly_covered_parent_previous_status": {}, "units_with_status_change": [],
            "reason": "the previous audit rejected nothing and no merged feature can express a unit that was not expressed: the "
                      "translation, the ledger and the three companions are byte-identical to the previous run's (asserted by finish.py), "
                      "and `ve document check` of the main document, the strict companion and the default companion gives the previous "
                      "run's output exactly"},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "git_diff": "414 files, 73 under ve/ (ve/readings_sup.py, readings_verdicts.py, readings_s2_wording.py, readings_s2_english.py, "
                        "readings_route.py, readings_s1.py, english_grammar/, lean_service_schema/*.json, backends/relay.py) and Lean under "
                        "lean/VE/Compose, lean/VE/Readings, lean/VE/ResponseShape, lean/VE/English*",
            "merged": {
                "compose-s2 (S2a)": "superposed verdicts across readings for a content-bearing `readings@1` document on the soft and norms chains; "
                                    "enumerated fallback (up to 64 compatible choices); `ve document readings --conclusion/--under`; rights chain is "
                                    "S2b (not merged). The one change that adds something to the language the constitution can use",
                "english-lean S2": "English reading and printing as a Lean executable (`ve_english_route`), Python shadowing it; same English as before",
                "lean-first b1 (lf-1)": "response shapes of the Lean routes proved against their encoders; no new text form",
                "lean-first b3b, b3d": "the readings and discourse relays' tables and sides composed; performance and removal of Python duplicates",
                "infra/consolidate-b1": "consolidation of duplicated logic across Python, Lean and Rust"},
            "newly_expressible_features": 1,
            "newly_expressible": "verdicts across the readings of a reading set, on the soft chain and only for documents without norm-defaults@0",
            "units_upgraded_by_new_features": 0,
            "why_no_unit_changed_status": "S2a adds no status (spec 11: no status change of any unit expected) and does not apply to the main document: "
                                          "`readings@1` content beside norm-defaults@0 is a named abstention (probes/s1-probe.json, case b: "
                                          "`UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented`); the soft companion "
                                          "that S2a can use completes duties with `deny`, which the source does not state, so it stays a demonstration",
            "profile_combination_result": "see profile_combination_probe and probes/s1-probe.json: (a) the main document with readings@1 added is now "
                                          "accepted (it was refused with a false message `readings@1 requires norms@0`); it adds nothing, since no set "
                                          "has content; (b) a content-bearing strict candidate beside norm-defaults@0 is the named abstention; (c) the "
                                          "soft companion with norm-defaults@0 added is refused as before"},
        "carried_probes_note": "all five probes re-run at this tag; the unspecified, risk, discourse and rights probe files are byte-identical to the "
                               "previous run's; probes/s1-probe.json differs: (a) is now accepted, (b)'s rejection is the named abstention, (c)'s "
                               "wording names the soft and rights routes; probes/s2/ is new (conclusions across and under readings)",
    })
    m["s1"] = {**prev_metrics["s1"], "premises": {k: v for k, v in pr.items() if k not in ("model", "candidates")},
               "premises_before_this_tag": prev_s1["premises"], "see_s2a": "metrics s2a"}
    dump("metrics.json", m)
    dump("units.json", ledger)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes",
                                         "audit_verified_covered_percent", "audit_verified_metadata_bytes", "claimed_but_not_audit_verified_bytes")}))
    print("newly verified:", newly_sub, "s2a candidates:", s2a["candidate_status_counts"])
    print("profile probe:", json.dumps(profile_probe, indent=1))


if __name__ == "__main__":
    main()
