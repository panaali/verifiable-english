"""Ledger update of run 20261019T1800Z: no unit changed; record this run's re-checks at ve-green-et-3b (foreground).

    python3 usecases/udhr-pilot/run-20261019T1800Z/update_run_20261019T1800Z.py
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
m = json.loads((HERE / "metrics.json").read_text())
prev = json.loads((HERE / "previous-20261019T0600Z" / "metrics.json").read_text())
pc = json.loads((HERE / "parts-check.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
etb3 = json.loads((HERE / "evidence" / "et0-rerun-prlimit-etb3.json").read_text())
rb = json.loads((HERE / "evidence" / "rebuild-command.json").read_text())
secs = {k.replace("translation-", "").replace(".ve.md", ""): v["seconds"] for k, v in pc.items()}

# --- identity of the run
m["run"] = "run-20261019T1800Z"
m["previous_baseline"] = "ve-green-qt-b1"
m["baseline"] = "ve-green-et-3b"
m["previous_run"] = "run-20261019T0600Z (ve-green-qt-b1); its parts, units, readings and metrics are carried here unchanged"

# --- previous-run comparators (all equal: no unit changed)
m["previous_run_unit_counts_by_status"] = prev["unit_counts_by_status"]
m["previous_run_audit_verified_covered_bytes"] = prev["audit_verified_covered_bytes"]
m["claimed_covered_bytes_previous_run"] = prev["claimed_covered_bytes"]
m["claimed_covered_bytes_previous_run_under_x5"] = prev["claimed_covered_bytes"]
m["claimed_change_vs_previous_run_bytes"] = 0
m["claimed_change_vs_previous_run_bytes_under_x5"] = 0
m["missing_feature_tally_previous_run"] = prev["missing_feature_tally"]
m["previous_run_reading_set_count"] = prev["reading_set_count"]
m["previous_run_reading_set_candidates"] = prev["reading_set_candidates"]
m["unit_counts_by_status_change"] = {"audit_repairs": {"bytes": 0, "units": 0}, "feature_upgrades": {"bytes": 0, "units": 0}, "plan_repairs": {"bytes": 0, "units": 0}}
assert prev["unit_counts_by_status"] == m["unit_counts_by_status"] and prev["bytes_by_status"] == m["bytes_by_status"]

# --- nothing changed
for k in ("changed_units", "plan_repairs", "units_changed_this_run", "ledger_only_changes", "audit_repairs", "repaired_units", "audit_newly_verified_units",
          "audit_pending_units", "audit_pending_claim_units", "document_ids_changed_in", "open_terms_added", "open_terms_dropped", "predicates_dropped",
          "units_rejected_by_audit_and_repaired", "units_repaired_same_defect_not_rejected", "units_with_only_open_term_factors_rewritten",
          "audit_verified_units_reexpressed_this_run"):
    m[k] = []
for k in ("open_terms_replaced", "reading_sets_changed_this_run", "repaired_unit_reasons", "audit_verified_units_withdrawn_this_run"):
    m[k] = {}
m["rendering_change"] = {"verdict": "none: the rendering of the four parts and the 64 companions is byte-identical to the previous run's", "what": "rendered-parts/ and readings-rendered.md regenerated at ve-green-et-3b and compared with run 20261019T0600Z"}
m["audit_newly_verified_units_note"] = "none: the 20261019T0600Z audit sampled 20 units, all already audit-verified"
m["audit_repair_this_run"] = "none: the 20261019T0600Z audit rejected no unit"
m["audit_pending_bytes"] = 0
m["claimed_false_pending_audit"] = {"bytes": 0, "note": "none pending; u060 (66 B), u035 and u111 stay claimed:false (X5)", "units": []}
m["plan_repairs_in_carried_state"] = ("JT-0p (u010, u060), ET-0 (u042, u043), QT-0p (u097), AP-0 (u085, u091, u106) and the SC-M0 scope tally were applied in earlier runs and are in the carried translation; "
                                      "this run did not re-apply them (plan_repairs is empty). Their checks are re-run below at ve-green-et-3b.")

# --- audit of the previous run
audit = (HERE / "AUDIT.md").read_text()
sampled = re.findall(r"^(u\d+[a-z]?) FAITHFUL$", audit, re.M)
m["audit_20261019T0600Z"] = {"file": "AUDIT.md (the 20261019T0600Z audit of the previous run, carried as written)", "sampled": len(sampled), "faithful": len(sampled), "unfaithful": [],
                             "units": sampled, "changed_units_checked": 0,
                             "note": "all sampled units were already audit-verified, so audit-verified bytes stay 5,270 (48.28%); no repair asked for. Its three missing-feature remarks: act-phrase grammar through a route (8 units), checked references/scoped limitations, plain-English rendering."}
assert set(sampled) <= set(m["audit_verified_units"]), set(sampled) - set(m["audit_verified_units"])
m["audit_verified_note"] = ("verified = judged FAITHFUL by an audit and not changed since, and not marked claimed:false. Claimed and verified bytes are equal (5,270 B, 48.28%); "
                            "no unit changed since its audit.")

# --- features
m["feature_upgrades"] = {"bytes": 0, "count": 0, "units": [],
    "note": "none: no construct, profile or sentence form a translator can write was added between ve-green-qt-b1 and ve-green-et-3b"}
m["features_merged_since_previous_baseline"] = [
    "ve-green-qt-b1 -> ve-green-et-3b (133 files, 9 merges): df-03 (defeasible baseline record, no product code), df-1a (lean/VE/Defaults premises; 'no service mode reaches it'), qt-a2 (Cardinality syntax/semantics; 'reachable from no service mode'), "
    "me-6 (physical dimensions in Calc; 'public output: none'), sc-3a (layout anchors; 'reach no caller until scope's govern'), et-3b (Events completion; 'not reachable from any service mode'), "
    "et-7b (alternatives validate with norm-defaults completion: scenario values for alt-validate; not a UDHR construct), lf-18 (metered mode and the end of the authority switch; 'no verdict, wording, order or availability changes' over 100,410 records), "
    "ps-6r (four idiom wordings for the constitution's heading presuppositions: 'is a core value / guideline / mission / nature of').",
    "evidence that none is writable by a translator for the UDHR: the DELTA.md of each merge says what users see does not change; the git diff of ve/ between the tags is refactoring (authority-switch removal, MAX_SOURCE_BYTES, error class names) plus the four idiom rows; "
    "the 4 parts, 64 companions and 148 Lean status rows give the previous run's document ids, statuses, verdicts and rendering byte for byte.",
    "the 38 UNFORMALISED units were searched against these: none contains the words 'core value', 'guideline', 'mission' or 'nature' (the only substring hit, 'omission' in Article 11, is a different word), no unit's blocker is a cardinality, scale, dimension, layout-scope, event or default route a service mode reads yet, so none can be expressed."]
m["language_change_for_udhr"] = "none: nothing a translator can write was added; every difference to the previous run is a measurement (timings) and no ledger claim changed."
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits)",
    "no seeded bug in product code (this run changed no file under ve/, lean/ or rust/); the translation's seeded faults are carried (seeded-bugs-translation.json)",
    "JT-5r (the 31 term splits) was not started, as directed",
    "no JT-0p/ET-0/QT-0p/AP-0 section was re-applied: all are already in the carried translation, and re-checked here"]

# --- checks
c = m["checks"]
c["build"] = "lake build (default targets, 1033 jobs, 36 min 50 s) and tools/rust_build.py (binary 6422647f.. pinned in lean/checkers.lock, `--check` passes) built in this worktree at ve-green-et-3b before the checks"
c["companions"] = "PASS: 64 companions check (premises model) and 148 Lean status rows as expected; witnesses.json, companions-check.json and readings-rendered.md identical to the previous run's"
c["parts"] = ("PASS: ve document check on all 4 parts at ve-green-et-3b: premises 'model', CONFLICT-FREE (part01 %.1f s, part02 %.1f s, part03 %.1f s, part04 %.1f s); document ids, unit statuses, coverage, premises and rendering equal to the previous run"
              % (secs["part01"], secs["part02"], secs["part03"], secs["part04"]))
c["unchanged_units"] = "PASS: all 130 units have the same status and row in the part files as in the previous run (no changed unit)"
c["whole_document"] = {"load": {"coverage_percent": whole["load"]["coverage_percent"], "seconds": whole["load"]["seconds"]},
                       "check": {"premises": whole["check"]["premises"], "readings_status": whole["check"]["readings_status"], "seconds": whole["check"]["seconds"]},
                       "note": "the same document as last run (translation-whole.ve.md byte-identical); equal verdicts. Wall time 2517 s and 2740 s against 1721 s and 1895 s last run with user CPU equal to wall time and a host load average of about 47: load on the host, not the language"}
c["limits_met"] = [
    "Rust checker: default VE_RUST_TIMEOUT kept. Part01 checks under prlimit --as=6442450944 in %.1f s with a peak child resident set of %.1f MB; no raised limit was needed" % (etb3["wall_seconds"], etb3["peak_child_resident_set_mb_max"]),
    "the whole declaration as ONE document (experiment-whole/): six two-reading sets as RD-4b components and the rest in the main component; at ve-green-et-3b load_document succeeds after %.1f s (coverage 100%%) and check_document answers CONFLICT-FREE, premises 'model' after %.1f s (previous run 1721.4 s and 1895.2 s)" % (whole["load"]["seconds"], whole["check"]["seconds"]),
    c["limits_met"][2] if len(c["limits_met"]) > 2 else ""]
c["limits_met"] = [x for x in c["limits_met"] if x]
c["repaired_units"] = {"note": "no audit repair and no plan repair this run"}
m["part_checks"] = {k: {**v, "seconds": pc[k]["seconds"]} for k, v in m["part_checks"].items()}
for k, v in m["part_checks"].items():
    old, new = prev["part_checks"][k], pc[k]
    assert old["document_id"] == new["document_id"] == v["document_id"], k

# --- ET-0 / whole / rebuild evidence
m["et0_rerun"]["requalified_at_et_3b"] = {"VE_RUST_TIMEOUT": "default (unset)", "address_space_cap_bytes": 6442450944, "evidence": "evidence/et0-rerun-prlimit-etb3.json",
    "peak_child_resident_set_mb": etb3["peak_child_resident_set_mb_max"], "verdict": etb3["verdict"], "premises": etb3["premises"], "conflict": etb3["conflict"], "wall_seconds": etb3["wall_seconds"]}
m["et0_rerun"]["whole_declaration"] = {"check_seconds": whole["check"]["seconds"], "load_seconds": whole["load"]["seconds"], "premises": "model", "readings_status": "CONFLICT-FREE"}
m["et0_rerun"]["other_parts_seconds"] = {k: v["seconds"] for k, v in pc.items()}
m["whole_document_experiment"]["components"] = {"load": {"coverage_percent": 100, "seconds": whole["load"]["seconds"]}, "check": {"premises": "model", "readings_status": "CONFLICT-FREE", "seconds": whole["check"]["seconds"]}}
m["whole_document_experiment"]["result"] = "loads and checks at ve-green-et-3b"
m["whole_document_experiment"]["note"] = "whole.py was NOT re-run; experiment-whole/translation-whole.ve.md is carried unchanged from the previous run and loaded/checked again at ve-green-et-3b (whole_check.py load, then check)"
for k, v in rb.items():
    assert (v["check_noop_exit"] == 0) == (k == "part03"), (k, v)
    m["rebuild_command_check"][k] = v
m["rebuild_command_check"]["requalified_at_et_3b"] = "part01, part02, part04 and the whole declaration `--check-noop` still exit 2 ('rebuild is not a no-op'); part03 is a no-op; the rebuilt documents of the first four still fail to load ('invalid situation'); evidence/rebuild-command.json"
m["language_findings"] = [
    "at ve-green-et-3b the 4 parts load and check exactly as at ve-green-qt-b1: same document ids, unit statuses, coverage, premises (model), CONFLICT-FREE, and rendering; the 64 companions and 148 Lean status rows are identical.",
    "ET-0 bar re-met: part01 checks in %.1f s under prlimit --as=6442450944 with a %.1f MB peak child (default Rust limit kept), premises model, CONFLICT-FREE (previous: 34.4 s, 105.0 MB)." % (etb3["wall_seconds"], etb3["peak_child_resident_set_mb_max"]),
    "the whole declaration as ONE document loads in %.1f s (100%%) and checks in %.1f s (CONFLICT-FREE, premises model); previous run 1721.4 s and 1895.2 s for the identical document, user CPU equals wall time, host load average about 47: slower because of the host, not the language. Lean-first b18's own note puts the document at 520 to 620 s on a quiet host." % (whole["load"]["seconds"], whole["check"]["seconds"]),
    "the committed `--rebuild-reading-ids` is still not a no-op on part 1 (`--check-noop` exits 2) nor on parts 2, 4 and the whole declaration: the defect found two runs ago stands. I did not use it and changed no ids.",
    "the natural view still words the two ET-0 predicates as 'has the recorded relation \"committed_on\" ...' (lint-refused wordings; ET-6 restates them).",
    "the ps-6r idiom rows ('is a core value / a guideline / a mission / a nature of') are not needed by any UDHR unit (no such word in the source)."]
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n")

# --- units.json: audit marks, notes
u = json.loads((HERE / "units.json").read_text())
for x in u["units"]:
    if x["id"] in sampled:
        x["audit_20261019T0600Z"] = "FAITHFUL"
d = {x["id"]: x for x in u["units"]}
d["u010"]["jt0p_note"] = d["u010"]["jt0p_note"].replace("Bytes are claimed until the targeted audit finds the unit unfaithful (plan JT-0p); not audit-verified yet.", "Bytes are claimed and audit-verified (the 20261018T1800Z audit found the unit FAITHFUL).")
for i in ("u042", "u043"):
    d[i]["et0_note"] = d[i]["et0_note"].replace("Claimed:false as the ledger proposal says: its bytes count only after this run's audit.", "Claimed and audit-verified since the 20261018T1800Z audit found the unit FAITHFUL.")
u["audit_note_20261019T1800Z"] = ("this run changes no unit: no construct a translator can write was merged between ve-green-qt-b1 and ve-green-et-3b. The 20261019T0600Z audit (AUDIT.md) sampled 20 units, all FAITHFUL and already audit-verified, "
                                  "and rejected nothing. Claimed and audit-verified bytes stay 5,270 (48.28%). The two stale ledger sentences about pending claims (u010 jt0p_note, u042 and u043 et0_note) are corrected.")
(HERE / "units.json").write_text(json.dumps(u, indent=1, ensure_ascii=False) + "\n")
print("ok", len(sampled), "sampled")
