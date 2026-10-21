#!/usr/bin/env python3
"""Run 20261006T1800Z: re-run VE on the unchanged translation at ve-green-senses, write the ledger, rendering and metrics.

Run after probe_unspecified.py, probe_s1.py, probe_risk.py, probe_discourse.py, probe_rights.py, probe_senses.py, the check of
readings/s1.ve.md (readings/check-s1.json, coverage-s1.json) and the S2a conclusion probes (probes/s2/), from anywhere (PATH must
contain ~/.elan/bin for the Lean routes):
    uv run python usecases/claude-constitution-pilot/run-20261006T1800Z/finish.py

The translation is the previous run's (prev/translation.ve.md, copied unchanged). The previous audit (AUDIT-20261005T1800Z-received.md,
20/20 faithful) rejected nothing, and none of the seven features merged since ve-green-english-lean-s2 adds a form of text a
document can carry (see FEATURE-REVIEW.md), so no unit is upgraded. This script therefore does not build; it re-checks that the
ledger and the documents are unchanged, re-measures them with VE at this tag, and recomputes the audit-verified bytes from the
new audit. finish_0600.py (constants and renderers) and finish_20261005T1800Z.py (the previous run's script) are reused or kept
for reference.
"""
from __future__ import annotations

import copy
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

RUN_ID = "20261006T1800Z"
PREV_RUN = "20261005T1800Z"
TAG = "ve-green-senses"
PREV_TAG = "ve-green-english-lean-s2"
COVERED = old.COVERED
DOCS = old.DOCS
SOURCE = old.SOURCE
ve, front_matter = old.ve, old.front_matter
dump = lambda p, o: (RUN / p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")

# the 20261005T1800Z audit (AUDIT-20261005T1800Z-received.md, 20/20): the units it sampled
_audit_rows = [l.split() for l in (RUN / "AUDIT-20261005T1800Z-received.md").read_text().split("```text")[1].split("```")[0].strip().splitlines()]
AUDIT_LATEST = [u for u, v in _audit_rows if v == "FAITHFUL"]
AUDIT_LATEST_REJECTED = [u for u, v in _audit_rows if v != "FAITHFUL"]
AUDIT_LATEST_ID = "20261005T1800Z"


def main():
    # ---- ledger and documents are the previous run's, byte for byte
    prev = json.load(open(RUN / "prev/units.json"))
    ledger = json.load(open(RUN / "units.json"))
    assert ledger == prev, "units.json must start as the previous run's"
    assert (RUN / "translation.ve.md").read_bytes() == (RUN / "prev/translation.ve.md").read_bytes()
    prev_metrics = json.load(open(RUN / "prev/metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == prev_metrics["source_sha256"]
    # the previous run's companions are in readings/ (copied) and are not rewritten: compare with the previous run's own files
    PREV_DIR = Path("/home/seyran/code/manage-agents/pilots/claude-constitution") / f"run-{PREV_RUN}"
    for rel in ("readings/all-strict.ve.md", "readings/all-default.ve.md", "readings/s1.ve.md"):
        assert (RUN / rel).read_bytes() == (PREV_DIR / rel).read_bytes(), rel

    # ---- VE runs at this tag (main, strict, default fresh; s1 check and coverage were run by hand, 5 min 28 s, and are read here)
    results = {}
    for key, path in DOCS.items():
        rel = str(path.relative_to(ROOT))
        if key == "s1":
            results[key] = {"check": json.load(open(RUN / "readings/check-s1.json")),
                            "coverage": json.load(open(RUN / "readings/coverage-s1.json")), "render": ve("document", "render", rel)}
        else:
            results[key] = {"check": json.loads(ve("document", "check", rel)), "coverage": json.loads(ve("document", "coverage", rel)),
                            "render": ve("document", "render", rel)}
    main_meta, soft_meta = front_matter(DOCS["main"]), front_matter(DOCS["default"])
    prev_check = {"main": json.load(open(PREV_DIR / "check.json")), "strict": json.load(open(PREV_DIR / "readings/check-all-strict.json")),
                  "default": json.load(open(PREV_DIR / "readings/check-all-default.json")), "s1": json.load(open(PREV_DIR / "readings/check-s1.json"))}
    same_verdicts = {k: results[k]["check"] == prev_check[k] for k in prev_check}
    assert all(same_verdicts.values()), same_verdicts
    same_render = {k: results[k]["render"] == (PREV_DIR / "readings" / name).read_text()
                   for k, name in (("strict", "rendered-all-strict.md"), ("default", "rendered-all-default.md"), ("s1", "rendered-s1.md"))}
    assert all(same_render.values()), same_render
    dump("check.json", results["main"]["check"])
    dump("coverage.json", results["main"]["coverage"])
    dump("readings/check-all-strict.json", results["strict"]["check"])
    dump("readings/check-all-default.json", results["default"]["check"])
    (RUN / "readings/rendered-s1.md").write_text(results["s1"]["render"])
    (RUN / "readings/rendered-all-strict.md").write_text(results["strict"]["render"])
    (RUN / "readings/rendered-all-default.md").write_text(results["default"]["render"])
    rendered = old.annotate_hard(old.expand_main(results["main"]["render"], main_meta, ledger), ledger)
    assert rendered == (PREV_DIR / "rendered.md").read_text(), "rendered.md changed"
    (RUN / "rendered.md").write_text(rendered)
    (RUN / "rendered-raw.md").write_text(results["main"]["render"])
    prev_s1 = prev_check["s1"]

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
    assert old.full(u) == prev_metrics["sentence_clause_units"]["unit_counts_by_status"]
    status = {e["id"]: e["status"] for e in ledger}
    spans = {e["id"]: e["span"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)

    # ---- S2a (unchanged by this tag): the superposed route on the demonstration companion
    s1c = results["s1"]["check"]
    rd, pr = s1c["readings"], s1c["premises"]
    cand_status = {f"{c['set']}:{c['index']}": c["status"] for c in pr["candidates"]}
    concl = {}
    for name, f in (("across_all_readings", "conclusion-no-denial-result.json"), ("under_must", "conclusion-no-denial-under-0.json"),
                    ("under_should", "conclusion-no-denial-under-1.json")):
        r = json.load(open(RUN / "probes/s2" / f))
        prev_r = json.load(open(PREV_DIR / "probes/s2" / f))
        assert r == prev_r, f
        concl[name] = {k: r[k] for k in ("verdict", "route", "evidence", "assumed", "budget") if k in r}
    s2a = {**prev_metrics["s2a"],
           "re_run_at_this_tag": True, "identical_to_previous_run": True,
           "now": {**prev_metrics["s2a"]["now"]}, "candidate_status_counts": dict(Counter(cand_status.values())),
           "conclusion_probe_re_run": concl,
           "load_and_check_seconds": "5 min 28 s for `ve document check` of readings/s1.ve.md at this tag (about 7 minutes at ve-green-english-lean-s2); "
                                     "the conclusion queries took 69 s (across readings), 48 s (under must), 65 s (under should)"}

    # ---- audit-verified bytes: accepted by an independent audit of this lineage AND byte-identical in this run to the form it saw
    ledger_by_id = {e["id"]: e for e in ledger}
    prev_verified_sub = list(prev_metrics["audit_verified_covered_units"])
    accepted = [i for i in AUDIT_LATEST if i in ledger_by_id]
    assert len(accepted) == 20 and not AUDIT_LATEST_REJECTED
    accepted_sub = [i for i in accepted if status[i] in COVERED and status[i] != "LABELLED"]
    accepted_lab = [i for i in accepted if status[i] == "LABELLED"]
    verified_sub = list(dict.fromkeys(prev_verified_sub + accepted_sub))
    newly_sub = [i for i in verified_sub if i not in prev_verified_sub]
    prior_lab = list(dict.fromkeys(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED + [
        "u0286.heading", "u0013.heading", "u0055.heading", "u0008.heading", "u0023", "u0126", "u0282"]))
    cand_lab = list(dict.fromkeys(prior_lab + accepted_lab))
    verified_lab = [i for i in cand_lab if i in ledger_by_id and status[i] == "LABELLED"]
    newly_lab = [i for i in verified_lab if i not in set(prior_lab)]
    assert all(status[i] in COVERED for i in verified_sub)
    sub_bytes, lab_bytes = width(verified_sub), width(verified_lab)
    assert sub_bytes == prev_metrics["audit_verified_covered_bytes"] + width(newly_sub)
    prev_ap = prev_metrics["audit_rejected_units_and_repair_status"]
    repaired_unverified = sorted(set(prev_ap["repaired_in_20261005T0600Z_and_not_yet_sampled"]) - set(verified_sub))

    # ---- profile combinations at this tag, and the senses probe
    profile_probe = old.probe_profiles()
    s1_probe = json.load(open(RUN / "probes/s1-probe.json"))
    senses = json.load(open(RUN / "probes/senses-probe.json"))
    assert profile_probe == prev_metrics["profile_combination_probe"], "profile combinations changed"
    units_for_senses = {i: {"status": status[i], "source": ledger_by_id[i]["source_excerpt"][:140]}
                        for i in ("u0220.s01", "u0220.s04", "u0233.s01")}

    m = copy.deepcopy(prev_metrics)
    m.update({
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "previous_runs_note": "run 20261006T0600Z (language ve-green-lf-11a) left no files; this run starts from 20261005T1800Z, the last run with committed output",
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
            f"Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run to the form that "
            f"audit saw. The latest audit ({AUDIT_LATEST_ID}, 20/20, a verdict for every sampled unit) saw the previous run's form; this run keeps "
            f"every ledger entry and every document unit as it was (finish.py asserts the ledger, the main document and the companions equal "
            f"the previous run's), so every acceptance counts. Substantive units it newly accepted: {', '.join(newly_sub) or 'none'}. Label units "
            f"it newly accepted: {', '.join(newly_lab) or 'none'}. u0123.s03 (repaired two runs ago, not sampled until this audit) is now verified."),
        "audit_verified_newly_from_20261005T1800Z": newly_sub,
        "audit_verified_newly_label_units_from_20261005T1800Z": newly_lab,
        "audit_verified_dropped_because_changed_or_rejected": {"changed_since_acceptance": [], "rejected_by_an_audit_and_not_re_accepted": []},
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261005T1800Z_audit": AUDIT_LATEST_REJECTED,
            "repair_needed_in_20261006T1800Z": "none: the 20261005T1800Z audit accepted all 20 sampled units, so there was nothing to repair",
            "repaired_and_not_yet_sampled": repaired_unverified,
            "earlier": {k: v for k, v in prev_ap.items()},
        },
        "claimed_but_not_audit_verified_bytes": claimed - sub_bytes - lab_bytes,
        "repaired_bytes_not_audit_verified": width(repaired_unverified),
        "document_profiles": {k: front_matter(v)["environment"]["profiles"] for k, v in DOCS.items()},
        "check_verdicts": {**prev_metrics["check_verdicts"],
                           "main": {**prev_metrics["check_verdicts"]["main"], "identical_to_previous_run": same_verdicts["main"]},
                           "all_strict": {**prev_metrics["check_verdicts"]["all_strict"], "identical_to_previous_run": same_verdicts["strict"]},
                           "all_default": {**prev_metrics["check_verdicts"]["all_default"], "identical_to_previous_run": same_verdicts["default"]},
                           "s1": {**prev_metrics["check_verdicts"]["s1"], "identical_to_previous_run": same_verdicts["s1"]}},
        "renderings_identical_to_previous_run": {"main_expanded": True, **same_render},
        "s2a": s2a,
        "unspecified_probe": {**prev_metrics["unspecified_probe"], "identical_to_previous_run": True},
        "profile_combination_probe": profile_probe,
        "senses_probe": {
            "file": "probes/senses-probe.json", "script": "probe_senses.py", "feature": "senses (senses/integrate): word senses as named projected predicates; "
            "`ve senses check --env --pack source`, admission only (`conclusions: not_checked`, assurance `experimental`)",
            "not_part_of_the_translation": True, "claimed": False, "units_upgraded": 0,
            "what_it_expresses": "a word with several senses and no chosen default makes its sentence an OPEN reading set whose candidates are named, "
                                 "formula-bearing and each with the English line that would choose it; a default line or a parenthetical gloss resolves it to one reading; "
                                 "a gloss that is not a sense of the word is refused",
            "outcomes": {k: {"source": v["source"], "status": v["reading"]["status"], **({"unresolved": v["reading"]["units"][0]["unresolved"]} if v["reading"].get("units") and v["reading"]["units"][0].get("unresolved") else {}),
                                  **({"formulas": [c["formula"] for c in v["reading"]["units"][0]["candidates"]]} if v["reading"]["status"] == "open" else {}),
                                  **({"formula": v["reading"]["units"][0]["formula"]} if v["reading"]["status"] == "one" else {}),
                                  **({"code": v["reading"].get("code")} if v["reading"]["status"] == "none" else {})}
                         for k, v in senses.items()},
            "constitution_units_it_would_fit": units_for_senses,
            "why_no_unit_changes": "the document format has no senses block: `ve document check` and render take no sense pack, `ve check` has no --senses (senses-integration-report.md: "
                                   "B6 service, B7 display and reading sets open); a sense pack is read only by the standalone `ve senses check`, outside a document, with no "
                                   "units, spans or statuses. The constitution units that fix or discuss a sense of a word (u0220.s01 \"corrigible\", u0233.s01) are UNFORMALISED for "
                                   "norms (what the disposition requires), not for the word's sense",
        },
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "unchanged_entries": len(ledger), "changed_or_replaced_ids": [],
            "added_ids": [], "units_newly_covered": [], "units_newly_covered_parent_previous_status": {}, "units_with_status_change": [],
            "reason": "no merged feature since the previous tag adds a form of text a document can carry (senses, English S3's order@0/alternatives@0 grammar, "
                      "layered norm-defaults conformance, Lean-first shapes/B2/B10a/B11a, consolidation): the translation, the ledger and the three "
                      "companions are byte-identical to the previous run's (asserted by finish.py) and `ve document check` of the main document, the strict, "
                      "default and s1 companions, and every rendering give the previous run's output exactly"},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "git_diff": "250 files; 27 under ve/ (ve/senses/, ve/backends/senses.py, ve/english_grammar/order@0.json and alternatives@0.json, lean_service, "
                        "rust_jsonl, relay, environment_wire) and Lean under lean/VE/Senses, lean/VE/EnglishGrammar, lean/VE/Service, lean/VE/ResponseShape",
            "merged": {
                "senses/integrate (senses)": "word senses read by the compiled Lean reader: packs of senses, one default per word by one English line, a gloss to switch an "
                                             "occurrence, an unchosen ambiguous word is an open reading set of named candidates; `ve senses check` is admission only; "
                                             "no document, render or check integration yet. The one genuinely new thing the constitution's wording can use",
                "english-lean-s3/integrate": "English in Lean S3: `order@0` (integer terms and comparisons) and `alternatives@0` (either/or, both/and verb phrases) reader tables, "
                                             "risk comparative wording ('more severe than'); the document checker still refuses both profiles beside norms",
                "lean-first/shapes, b2, b10a, b11a (lf-2, lf-10a, lf-11a)": "service handles for environments, response shapes proved against encoders, "
                                                                           "difffuzz gates; no new form of text",
                "infra/consolidate-b2": "consolidation of duplicated logic across Python, Lean and Rust",
            },
            "newly_expressible_features": 1,
            "newly_expressible": "lexical-sense reading sets (word senses) as a standalone reading, not as a document feature",
            "units_upgraded_by_new_features": 0,
            "why_no_unit_changed_status": "the one new expressible thing (senses) cannot be carried by a document, and the unchanged blocker F1 (`readings@1` content beside "
                                          "`norm-defaults@0`: the named abstention `UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented`) still "
                                          "keeps S2a away from the main translation (probes/s1-probe.json identical to the previous run's)",
            "profile_combination_result": "identical to the previous run's for all 13 added profiles (order@0 and closure@0 still `norm document admission is FOL-only`, "
                                          "alternatives@0 still `InvalidInput: alternatives.block`, risk@0 still `requires alternatives@0`, discourse still refused beside norm-defaults@0)"},
        "carried_probes_note": "all five carried probes re-run at this tag and byte-identical to the previous run's; probe_senses.py is new",
    })
    dump("metrics.json", m)
    dump("units.json", ledger)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes",
                                         "audit_verified_covered_percent", "audit_verified_metadata_bytes", "claimed_but_not_audit_verified_bytes")}))
    print("newly verified:", newly_sub, "newly verified labels:", newly_lab, "still repaired-unverified:", repaired_unverified)


if __name__ == "__main__":
    main()
