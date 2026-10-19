"""Run 20261019T0600Z: carry run-20261018T1800Z unchanged (no translator-facing feature merged), apply its audit, record the re-checks.

    python3 usecases/udhr-pilot/run-20261019T0600Z/apply_run_20261019.py
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
RUN, PREV = "run-20261019T0600Z", "run-20261018T1800Z"
units = json.loads((HERE / "units.json").read_text())
m = json.loads((HERE / "metrics.json").read_text())
parts = json.loads((HERE / "parts-check.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
ev = json.loads((HERE / "evidence" / "et0-rerun-part01-prlimit-qtb1.json").read_text())

# 1. the 20261018T1800Z audit (AUDIT.md): u010, u042, u043, u060 FAITHFUL; u042 and u043 accepted with both readings
newly = {"u010": 132, "u042": 200, "u043": 118}
for x in units["units"]:
    i = x["id"]
    if i in ("u010", "u042", "u043", "u060"):
        x["audit_20261018T1800Z"] = "FAITHFUL"
    if i in newly:
        x["claimed"] = True
        for k in ("audit_pending", "claim_pending_audit"):
            x.pop(k, None)
        if "et0_ledger_proposal" in x:
            x["et0_ledger_proposal"]["audit"] = "FAITHFUL (20261018T1800Z)"
            x["et0_ledger_proposal"]["claimed"] = True
        x["claim_note_20261019T0600Z"] = "claimed since the 20261018T1800Z audit found the unit FAITHFUL (reification accepted; for u043 both readings are kept as one set, none picked)"
    x[f"status_in_{RUN.replace('run-', 'run_')}"] = x["status"]
units["audit_note_20261019T0600Z"] = ("this run changes no unit: no construct a translator can write was merged since ve-green-eff-20261018-1. "
    "The 20261018T1800Z audit (AUDIT.md) found u010, u042, u043 and u060 FAITHFUL, so u010, u042 and u043 are claimed and audit-verified from this run (u060 stays claimed:false, presupposition, X5).")
(HERE / "units.json").write_text(json.dumps(units, indent=1))

# 2. metrics
cov = sum(x["span"][1] - x["span"][0] for x in units["units"] if x.get("claimed", True) and x["status"] in ("CHECKED", "LABELLED", "OPEN", "READINGS"))
assert cov == 5270, cov
m["run"], m["previous_run"] = RUN, f"{PREV} (ve-green-eff-20261018-1); its parts, units, readings and metrics are carried here unchanged"
m["baseline"], m["previous_baseline"] = "ve-green-qt-b1", "ve-green-eff-20261018-1"
m["claimed_covered_bytes_previous_run"] = m["claimed_covered_bytes_previous_run_under_x5"] = 4952
m["claimed_covered_bytes"], m["claimed_covered_percent"] = cov, round(100 * cov / 10916, 2)
m["claimed_change_vs_previous_run_bytes"] = m["claimed_change_vs_previous_run_bytes_under_x5"] = cov - 4952
m["previous_run_audit_verified_covered_bytes"] = 4820
m["audit_verified_covered_bytes"], m["audit_verified_covered_percent"] = cov, round(100 * cov / 10916, 2)
m["audit_verified_covered_bytes_before_x5"] = cov + 8
m["audit_verified_units"] = sorted(set(m["audit_verified_units"]) | set(newly))
m["audit_verified_units_form_unchanged"] = m["audit_verified_units"]
m["audit_newly_verified_units"] = sorted(newly)
m["audit_newly_verified_units_note"] = "judged FAITHFUL by the 20261018T1800Z audit (u010 132 B, u042 200 B, u043 118 B = 450 B) and unchanged since; claim flipped from pending to claimed in this run's ledger"
m["audit_pending_units"], m["audit_pending_bytes"], m["audit_pending_claim_units"] = [], 0, []
m["claimed_false_pending_audit"] = {"bytes": 0, "units": [], "note": "none pending: the 20261018T1800Z audit found u042 and u043 FAITHFUL (claimed now); u060 (66 B) was audited FAITHFUL and stays claimed:false for presupposition (X5)"}
m["x5_claimed_false"]["bytes"] = 571
m["x5_claimed_false"]["units"]["u060"] = {"bytes": 66, "reason": "'the' (uniqueness: the one natural and fundamental group unit) is not represented (missing_feature presupposition)"}
m["x5_claimed_false"]["note"] = "u035, u111 and u060 are claimed:false; u042 and u043 became claimed after the 20261018T1800Z audit"
m["audit_verified_note"] = "verified = judged FAITHFUL by an audit and not changed since, and not marked claimed:false. Claimed and verified bytes are now equal (5,270 B, 48.28%): the four plan-repaired units of the previous run were audited FAITHFUL; none changed since."
m["claimed_covered_bytes_without_x5_marks"] = m["covered_bytes_all_statuses_including_claimed_false"] = cov + 571
m["claimed_covered_percent_without_x5_marks"] = round(100 * (cov + 571) / 10916, 2)
m["audit_20261018T1800Z"] = {"file": "AUDIT-20261018T1800Z.md (the previous run's audit, carried)", "faithful": "20/20 sampled + 4/4 changed", "unfaithful": [], "repairs_needed": 0,
    "note": "its caveats are carried into the unit notes: the reification caveat (one act on two days; ET-6 closes it), u043's rendering defect (the unit's own copy of the universal reading is shown first; the loader treats it as quoted)"}
m["audit_20261018T1800Z_note"] = "audited by the orchestrator; no repair was asked for"
m["audit_repair_this_run"] = "none: the 20261018T1800Z audit rejected no unit"
m["changed_units"] = []
m["units_changed_this_run"] = []
m["changed_units_note"] = "none: this run changed no unit's content, status or span. Ledger-only: u010, u042, u043 claimed after the audit (claim flip, no content change)."
m["ledger_only_changes"] = [{"unit": u, "change": "claimed true after the 20261018T1800Z audit FAITHFUL", "bytes": b} for u, b in newly.items()]
m["plan_repairs_in_carried_state"]["items"] = m["plan_repairs"] + m["plan_repairs_in_carried_state"]["items"]
m["plan_repairs_in_carried_state"]["note"] = ("every plan repair of the merged research plans is already in this translation and carried unchanged: u010, u060 (JT-0p) and u042, u043 (ET-0) landed in run-20261018T1800Z and were audited FAITHFUL; "
    "u097 (QT-0p), u085, u091, u106 (AP-0) landed earlier (u039 was not landed). The sections of this run's prompt are the 18:00Z run's sections again: re-verified (parts load and check, same ids, same rendering), nothing re-applied, so none is a changed unit of this run")
m["plan_repairs"] = []
m["plan_repairs_note"] = "none applied this run (see plan_repairs_in_carried_state)"
m["feature_upgrades"] = {"bytes": 0, "count": 0, "units": [], "note": "none: no construct, profile or sentence form a translator can write was added between ve-green-eff-20261018-1 and ve-green-qt-b1"}
m["features_merged_since_previous_baseline"] = [
    "ve-green-eff-20261018-1 -> ve-green-qt-b1 (90 files, all Lean core, docs and trust tables): ap-2 (act grammar part 1: vocabulary, terminals, listing; Lean only, ap-2b not yet), qt-a1 and qt-a1b (cardinality@0 core and erasure soundness; 'reachable from no route'), qt-b1 (scales@0 core; 'no route reads the files'), sc-1a (layout list runs; Lean only), pk-1 (premise packs: LayeredU.packs replaces two fields, legacy theorems; no behaviour change claimed).",
    "evidence that none is reachable by a translator: git diff of ve/, rust/, lean/VE/Service and lean/ResponseShape between the two tags changes only ve/assurance-manifest.json and one encoder file (lean/ResponseShape/Encoders/NormDefaults.lean, pk-1 follow-up); the 4 parts, 64 companions and 148 status rows give the previous run's ids, statuses, verdicts and rendering byte for byte.",
    "the 38 UNFORMALISED units were searched against these merges (acts: AP grammar not wired; counting/quantities: cardinality and scales not wired; scope: layout only): none can be expressed yet."]
m["language_change_for_udhr"] = "none: nothing a translator can write was added; every difference to the previous run is a ledger change (claims after the audit)."
m["language_findings"] = [
    "at ve-green-qt-b1 the 4 parts load and check exactly as at ve-green-eff-20261018-1: same document ids, unit statuses, coverage, premises (model), CONFLICT-FREE, and rendering; the 64 companions and 148 Lean status rows are identical.",
    "ET-0 bar re-met: part01 checks in 34.4 s under prlimit --as=6442450944 with a 105.0 MB peak child (default Rust limit kept), premises model, CONFLICT-FREE (previous: 46.6 s, 104.0 MB).",
    "the whole declaration as ONE document loads in 1721.4 s (100%) and checks in 1895.2 s (CONFLICT-FREE, premises model); previous run 2577.8 s and 2525.2 s, 648.3 s and 687.0 s the run before. Same document, so this is machine load, not the language.",
    "the committed `--rebuild-reading-ids` is still not a no-op on part 1 (`--check-noop` exits 2): the defect found last run stands (tools/readings_s1_pilot.py is unchanged between the tags).",
    "the natural view still words the two ET-0 predicates as 'has the recorded relation \"committed_on\" ...' (lint-refused wordings; ET-6 restates them)."]
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits)",
    "no seeded bug in product code (this run changed no file under ve/, lean/ or rust/); the translation's seeded faults are carried (seeded-bugs-translation.json)",
    "JT-5r (the 31 term splits) was not started, as directed",
    "no JT-0p/ET-0/QT-0p/AP-0 section was re-applied: all are already in the carried translation"]
m["checks"]["build"] = "lake build (default targets) and tools/rust_build.py (binary 6422647f.. pinned in lean/checkers.lock) built in this worktree at ve-green-qt-b1 before the checks"
m["checks"]["parts"] = "PASS: ve document check on all 4 parts at ve-green-qt-b1: premises 'model', CONFLICT-FREE (" + ", ".join(f"{k[12:18]} {v['seconds']} s" for k, v in parts.items()) + "); document ids, unit statuses, coverage, premises and rendering equal to the previous run"
m["checks"]["companions"] = "PASS: 64 companions check (premises model) and 148 Lean status rows as expected; witnesses.json identical to the previous run's"
m["checks"]["whole_document"] = {"load": whole["load"], "check": whole["check"], "note": "equal verdicts to the previous run; wall times 1721.4 s and 1895.2 s (CPU equals wall)"}
for k, v in parts.items():
    pc = m["part_checks"][k]
    assert pc["document_id"] == v["document_id"]
    pc["seconds"] = v["seconds"]
m["whole_document_experiment"]["components"] = {"load": whole["load"], "check": whole["check"]}
m["et0_rerun"]["requalified_at_qt_b1"] = {"wall_seconds": ev["wall_seconds"], "peak_child_resident_set_mb_max": ev["peak_child_resident_set_mb_max"], "address_space_cap_bytes": ev["address_space_cap_bytes"], "VE_RUST_TIMEOUT": ev["VE_RUST_TIMEOUT"], "verdict": ev["verdict"], "premises": ev["premises"], "evidence": "evidence/et0-rerun-part01-prlimit-qtb1.json"}
m["rebuild_command_check"]["requalified_at_qt_b1"] = "part01 `--check-noop` still exits 2 ('rebuild is not a no-op'); tool unchanged between the tags"
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, sort_keys=True))
print("ok", cov, round(100 * cov / 10916, 2))
