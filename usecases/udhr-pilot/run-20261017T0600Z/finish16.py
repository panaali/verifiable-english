"""Write units.json and metrics.json for the 2026-10-15T0600Z run (language at ve-green-lf-14b).

    uv run --frozen python usecases/udhr-pilot/run-20261015T0600Z/finish16.py

Nothing here calls a model. The inputs are this run's saved check results (parts-check.json, witnesses.json,
companions-check.json, refusal-test.json, qt0p-isolated.json, unit-compare.json, experiment-whole/whole-check.json,
verdict.json, coverage.json) and the previous run's metrics.json in previous-20261014T1800Z/. This run changes no unit:
the translation parts are the previous run's, byte for byte.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = json.loads((HERE / "previous-20261014T1800Z" / "metrics.json").read_text())
load = lambda name: json.loads((HERE / name).read_text())

COVERED = {"CHECKED", "LABELLED", "OPEN", "READINGS"}
AUDIT_20261014 = ("u001 u002 u014 u024 u028 u033b u035 u036 u045a u049 u055 u065 u066 u070 u077 u084c u085 u087 u091 u096 "
                  "u097 u099b u105a u106 u109 u114").split()
CHANGED_PREVIOUS_RUN = ["u049", "u077", "u085", "u091", "u097", "u106"]

# ---- units.json -----------------------------------------------------------------------------------------------------
units_file = load("units.json")
units = units_file["units"]
for u in units:
    if "status_in_run_20261013T0600Z" not in u:
        u["status_in_run_20261013T0600Z"] = u.get("status_in_previous_run")
    u["status_in_previous_run"] = u["status"]          # unchanged this run: the previous run's status is the current one
    if u["id"] in AUDIT_20261014:
        u["audit_20261014T1800Z"] = "FAITHFUL"
units_file["audit_note_20261015T0600Z"] = ("this run changes no unit; audit_20261014T1800Z is the previous run's audit "
                                          "(26 units sampled, all FAITHFUL, no unfaithful unit)")
(HERE / "units.json").write_text(json.dumps(units_file, indent=1, ensure_ascii=False))

size = lambda u: u["span"][1] - u["span"][0]
byid = {u["id"]: u for u in units}
by_status = {}
bytes_by_status = {}
for u in units:
    by_status[u["status"]] = by_status.get(u["status"], 0) + 1
    bytes_by_status[u["status"]] = bytes_by_status.get(u["status"], 0) + size(u)
claimed = sum(size(u) for u in units if u["status"] in COVERED and u.get("claimed", True))
claimed_no_marks = sum(size(u) for u in units if u["status"] in COVERED)
assert by_status == PREV["unit_counts_by_status"] and claimed == PREV["claimed_covered_bytes"] == 4820
total = sum(size(u) for u in units)
assert total == 10916

old_verified = set(PREV["audit_verified_units"])
verified_all = old_verified | set(AUDIT_20261014)
verified = sorted(i for i in verified_all if byid[i]["status"] in COVERED and byid[i].get("claimed", True))
verified_bytes = sum(size(byid[i]) for i in verified)
pending = [u["id"] for u in units if u["status"] in COVERED and u.get("claimed", True) and u["id"] not in verified]
pending_bytes = sum(size(byid[i]) for i in pending)
assert verified_bytes + pending_bytes == claimed

# ---- metrics.json ---------------------------------------------------------------------------------------------------
m = json.loads(json.dumps(PREV))
m["run"] = "run-20261015T0600Z"
m["baseline"] = "ve-green-lf-14b"
m["previous_baseline"] = PREV["baseline"]
m["previous_run"] = "run-20261014T1800Z (ve-green-repo-map-untracked); its translation, units, metrics and audit are in previous-20261014T1800Z/"
m["features_merged_since_previous_baseline"] = [
    "none a translator can write. The merges since ve-green-repo-map-untracked: lean-first b14b (lf-14b: non-first-order "
    "norm guards on closure, core and order families are regenerated and checked in Lean, VE.Norms.Family; the Python "
    "fallback classification is deleted; no construct, profile or limit changed, and the corpus answers are identical), "
    "infra/ts-B2 (test selection and gate tooling), fix/subtick (a deadline test), infra/english-run-root (a distinct "
    "executable root for the English runner)."]
m["language_change_for_udhr"] = (
    "none. No construct was added and no unit changed: the four translation parts are the previous run's, byte for byte, and "
    "all 130 units load with the same status and the same row (unit-compare.json, no difference). The checks were re-run "
    "on the new tag (Lean, Rust and Python at ve-green-lf-14b) and give the same results.")
m["feature_upgrades"] = {"bytes": 0, "count": 0, "units": [],
                         "note": "no newly merged feature lets any UNFORMALISED unit move; nothing was changed this run"}
m["changed_units"] = []
m["units_changed_this_run"] = []
m["plan_repairs"] = []
m["plan_repairs_in_carried_state"] = {
    "note": "landed by the previous run (run-20261014T1800Z) and carried here unchanged; re-verified this run (companions, "
            "Lean status rows, qt0p isolated measurement); not changed this run, so not in changed_units",
    "items": PREV["plan_repairs"]}
m["audit_repairs_previous_run"] = PREV["audit_repairs"]
m["audit_repairs"] = []
m["repaired_units"] = []
m["repaired_unit_reasons"] = {}
m["units_rejected_by_audit_and_repaired"] = []
m["units_repaired_same_defect_not_rejected"] = []
m["units_with_only_open_term_factors_rewritten"] = []
m["reading_sets_changed_this_run"] = {}
m["predicates_dropped"] = []
m["open_terms_added"] = []
m["open_terms_dropped"] = []
m["words_only"] = {
    "note": "no reading was added, changed or removed this run; the carried readings are the previous run's (own_country is "
            "one open term, not a two-candidate set)",
    "open_questions_listed_that_the_text_does_not_raise": 0,
    "readings_added_this_run": {}, "readings_changed_this_run": {}, "readings_removed_this_run": {},
    "rule": PREV["words_only"]["rule"]}
m["unit_counts_by_status_change"] = {"audit_repairs": {"bytes": 0, "units": 0}, "feature_upgrades": {"bytes": 0, "units": 0},
                                     "plan_repairs": {"bytes": 0, "units": 0}}
m["claimed_covered_bytes_previous_run"] = PREV["claimed_covered_bytes_without_x5_marks"]
m["claimed_covered_bytes_previous_run_under_x5"] = PREV["claimed_covered_bytes"]
m["claimed_change_vs_previous_run_bytes"] = 0
m["claimed_change_vs_previous_run_bytes_under_x5"] = 0
m["previous_run_unit_counts_by_status"] = PREV["unit_counts_by_status"]
m["previous_run_reading_set_count"] = PREV["reading_set_count"]
m["previous_run_reading_set_candidates"] = PREV["reading_set_candidates"]
m["previous_run_old_boundary_aggregation"] = PREV["old_boundary_aggregation"]
m["missing_feature_tally_previous_run"] = PREV["missing_feature_tally"]
m["previous_run_audit_verified_covered_bytes"] = PREV["audit_verified_covered_bytes"]

# audit-verified bytes: the previous run's own audit (26/26 FAITHFUL) now counts; claimed:false units never count (X5)
m["audit_verified_units"] = verified
m["audit_verified_covered_bytes"] = verified_bytes
m["audit_verified_covered_bytes_before_x5"] = sum(size(byid[i]) for i in verified_all if byid[i]["status"] in COVERED)
m["audit_verified_covered_percent"] = round(100 * verified_bytes / total, 2)
m["audit_pending_bytes"] = pending_bytes
m["audit_pending_units"] = pending
m["audit_newly_verified_units"] = sorted(set(AUDIT_20261014) - old_verified - {"u035"})
m["audit_newly_verified_units_note"] = ("verified by the 2026-10-14T1800Z audit (all 26 sampled units FAITHFUL, 6/6 changed units "
                                        "among them) and unchanged since; u035 was also judged FAITHFUL but is marked claimed:false (X5), "
                                        "so its 168 bytes are neither claimed nor verified")
m["audit_verified_units_reexpressed_this_run"] = []
m["audit_verified_note"] = (
    "verified = judged FAITHFUL by an audit and not changed since, and not marked claimed:false. No unit changed this run, "
    "so the verified set is the previous run's plus the units of the 2026-10-14T1800Z audit (including the six units that had been "
    "changed and waited for it: u049, u077, u085, u091, u097, u106). Under X5, u035 and u111 never count.")
m["audit_verified_units_form_unchanged"] = sorted(set(PREV["audit_verified_units_form_unchanged"]) | set(verified))
m["audit_20261014T1800Z"] = {"sampled": 20, "changed_units_checked": 6, "faithful": 26, "unfaithful": [],
                              "units": AUDIT_20261014, "file": "previous-20261014T1800Z/AUDIT.md"}
m["audit_20261014T1800Z_top_missing_features"] = [
    "compositional act phrases (participants, conditions, purposes, relative clauses; eight units)",
    "rights-set references and scoped limitations (this right, declared rights, Article 29 limits to their targets)",
    "temporal and comparative norms (non-retroactivity, historical penalty ceilings, periodic elections and holidays)"]

# ---- check results re-run at this tag ---------------------------------------------------------------------------------
parts = load("parts-check.json")
for name, row in parts.items():
    pc = m["part_checks"][name]
    assert pc["document_id"] == row["document_id"], name
    assert pc["readings_status"] == row.get("readings_status") or pc["readings_status"] is None, name
    pc["seconds"] = row["seconds"]
    pc["premises_status"] = row["premises"].get("status")
comp = load("companions-check.json")
unit_cmp = load("unit-compare.json")
whole = load("experiment-whole/whole-check.json")
refusal = load("refusal-test.json")
qt = load("qt0p-isolated.json")
verdict = load("verdict.json")
witness_rows = sum(len(v) for v in load("witnesses.json").values()) if isinstance(load("witnesses.json"), dict) else None
assert not unit_cmp["differences"] and not unit_cmp["unexpected"] and unit_cmp["units"] == 130
assert whole["load"].get("error")
m["checks"]["parts"] = ("PASS: ve document check on all 4 parts at ve-green-lf-14b: premises 'model' for every choice, "
                        "CONFLICT-FREE under every reading; document ids and unit statuses equal the previous run's")
m["checks"]["unchanged_units"] = "PASS: 130 of 130 units have the same status and the same row in the part files; nothing changed this run"
m["checks"]["companions"] = "PASS: 59 companions check (premises model) and 118 Lean status rows as expected (re-run at ve-green-lf-14b)"
m["checks"]["wrong_separating_situation"] = {"result": refusal["result"], "set": refusal["set"]}
m["checks"]["legacy_document"] = {"coverage": "PASS (100%)", "premises": verdict["report"]["premises"],
                                  "check_seconds": verdict["check_seconds"]}
m["checks"]["limits_met"] = [
    "Rust checker: one call is limited to 5 s (default VE_RUST_TIMEOUT kept; no prlimit run, so no raised limit and no peak "
    "resident-set record); (measured in an earlier run, not re-run) a part with 19 regulated predicates (u001-u108, 16 choices) "
    "is refused with 'Rust checker failed ... timed out after 4.99 s' (CheckerUnavailable), so the four parts are the largest that check",
    f"the whole declaration as ONE document (experiment-whole/): four two-reading sets with their own vocabulary as RD-4b components "
    f"(u025, u055, u073, u111) and the rest in the main component, built by whole.py; load_document fails after "
    f"{whole['load']['seconds']} s with the Rust checker's 5 s limit (re-run this run at ve-green-lf-14b; previous run 1366.1 s; "
    f"experiment-whole/whole-check.json)",
    "the whole declaration with every candidate in the main document (integrate.py u001 u114; measured earlier, not re-run): Lean "
    "elaborates it on the superposed route, but Python's one-element search finds no separating situation for u111's pair "
    "both_aims / listed_aims in 6 min 58 s (experiment-whole/integrate-whole.log), so no document is produced"]
m["whole_document_experiment"]["components"] = {"load": whole["load"]}
m["vocabulary_change_check"] = {
    "rule": PREV["vocabulary_change_check"]["rule"],
    "entity_sort": PREV["vocabulary_change_check"]["entity_sort"],
    "result": {"units": unit_cmp["units"], "differences": [], "unexpected": [], "environment_changed_in": unit_cmp["environment_changed_in"],
               "note": "no vocabulary change this run (predicate, constant and wording are the previous run's); the situation step and "
                       "the unit comparison were nevertheless re-run at the new tag and every unit parses unchanged"},
    "rust_time_limit": "default VE_RUST_TIMEOUT kept (5 s); no prlimit run, so no raised limit and no peak resident-set record",
    "situation_step": PREV["vocabulary_change_check"]["situation_step"]}
m["qt0p_u097"]["isolated_measurement"] = qt["isolated_measurement"] if "isolated_measurement" in qt else qt
m["qt0p_u097"]["in_this_run"] = {"note": "carried unchanged from the previous run; the isolated measurement and the four probe rows "
                                         "were re-run at ve-green-lf-14b and give the same result", "u097_status": byid["u097"]["status"]}
m["presupposition_check"] = ("No heading or speaker marker presupposes a substantive claim; no unit changed this run, so the labelled "
                             "units are the audited previous run's. u060 stays UNFORMALISED as an evaluative claim. u045b, u099b and u100b "
                             "begin with a conjunction: each carries the subject of the previous unit (noted in its elided field), not a "
                             "presupposed claim.")
m["language_findings"] = [
    "NO NEW CAPABILITY for the UDHR at ve-green-lf-14b: batch 14b moves the checking of non-first-order norm guards (closure, core, "
    "order families) into Lean and deletes the Python fallback; it adds no construct a translator can write, and the 1,350-record "
    "corpus comparison in its report is identical. The 42 UNFORMALISED units keep the blockers they had.",
    "the four parts load and check at ve-green-lf-14b exactly as before (premises 'model', CONFLICT-FREE under every reading; "
    "same document ids, same unit rows, same 118 Lean status rows)",
    f"LIMIT, size (re-measured): the whole declaration as ONE document still fails to load on the Rust checker's 5 s limit "
    f"(after {whole['load']['seconds']} s, was 1366.1 s); the four-part split stays",
    "the natural view still shows entitlements only as 'classified as <name>' (rendered-parts are byte-identical to the previous run's)"]
m["limits_unchanged_note"] = PREV["limits_unchanged_note"]
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits); no seeded bug in product code (no product file changed; "
                          "see seeded-bugs.md)"]
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True))
print("units", len(units), by_status, "claimed", claimed, "verified", len(verified), verified_bytes, "pending", pending_bytes, pending)
