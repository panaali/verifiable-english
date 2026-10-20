"""Ledger update of run 20261020T0600Z: no unit changed; record this run's re-checks at ve-green-ap-1a (foreground).

    python3 usecases/udhr-pilot/run-20261020T0600Z/update_run_20261020T0600Z.py
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
m = json.loads((HERE / "metrics.json").read_text())
prev = json.loads((HERE / "previous-20261019T1800Z" / "metrics.json").read_text())
pc = json.loads((HERE / "parts-check.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
apa1 = json.loads((HERE / "evidence" / "et0-rerun-prlimit-apa1.json").read_text())
rb = json.loads((HERE / "evidence" / "rebuild-command.json").read_text())
secs = {k.replace("translation-", "").replace(".ve.md", ""): v["seconds"] for k, v in pc.items()}
assert m["run"] == "run-20261019T1800Z", "already updated"

# --- identity of the run
m["run"] = "run-20261020T0600Z"
m["previous_baseline"] = "ve-green-et-3b"
m["baseline"] = "ve-green-ap-1a"
m["previous_run"] = "run-20261019T1800Z (ve-green-et-3b); its parts, units, readings and metrics are carried here unchanged"

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
m["rendering_change"] = {"verdict": "none: the rendering of the four parts and the 64 companions is byte-identical to the previous run's",
                         "what": "rendered-parts/ and readings-rendered.md regenerated at ve-green-ap-1a and compared with run 20261019T1800Z"}
m["audit_newly_verified_units_note"] = "none: the 20261019T1800Z audit sampled 20 units, all already audit-verified"
m["audit_repair_this_run"] = "none: the 20261019T1800Z audit rejected no unit"
m["audit_pending_bytes"] = 0
m["claimed_false_pending_audit"] = {"bytes": 0, "note": "none pending; u060 (66 B), u035 and u111 stay claimed:false (X5)", "units": []}
m["plan_repairs_in_carried_state"] = ("JT-0p (u010, u060), ET-0 (u042, u043), QT-0p (u097), AP-0 (u085, u091, u106) and the SC-M0 scope tally were applied in earlier runs and are in the carried translation; "
                                      "this run did not re-apply them (plan_repairs is empty). Their spans, statuses and checks were re-verified at ve-green-ap-1a (below). "
                                      "The research branches' heads are the ones the evidence copies in evidence/SOURCES.md were taken from.")

# --- audit of the previous run
audit = (HERE / "AUDIT.md").read_text()
sampled = re.findall(r"^(u\d+[a-z]?) FAITHFUL$", audit, re.M)
assert len(sampled) == 20
m["audit_20261019T1800Z"] = {"file": "previous-20261019T1800Z/AUDIT.md (the 20261019T1800Z audit of the previous run, carried as written; AUDIT.md in this directory is the same file)",
                             "sampled": len(sampled), "faithful": len(sampled), "unfaithful": [], "units": sampled, "changed_units_checked": 0,
                             "note": "all sampled units were already audit-verified, so audit-verified bytes stay 5,270 (48.28%); no repair asked for. Its three missing-feature remarks: act-phrase grammar through a route (8 units, 1,403 B), equality and non-discrimination norms (7 units, 1,064 B), plain-English rendering of open-term classifications."}
assert set(sampled) <= set(m["audit_verified_units"]), set(sampled) - set(m["audit_verified_units"])
m["audit_verified_note"] = ("verified = judged FAITHFUL by an audit and not changed since, and not marked claimed:false. Claimed and verified bytes are equal (5,270 B, 48.28%); "
                            "no unit changed since its audit.")

# --- features
m["feature_upgrades"] = {"bytes": 0, "count": 0, "units": [],
    "note": "none: no construct, profile or sentence form a translator can write was added between ve-green-et-3b and ve-green-ap-1a"}
m["features_merged_since_previous_baseline"] = [
    "ve-green-et-3b -> ve-green-ap-1a (8 merges): me-5 (Calc derivations over rational unknowns; 'Public output: none', Lean modules only), jt-1b (judgments@0 unit status and usage map; 'reached by no route until JT-2'), "
    "et-8 (no product code: a harness, a test and README text), ar-10a (the profile-gate table; no verdict moves, only the text of a refusal for an unregistered profile), "
    "ap-1a (lexical acts, VE.Acts.Lexical; 'acts@0 has no profile row (ap-1b), so the envelope refuses it'; 330 recorded route cases byte-identical), pk-1b (premise-pack kind table; 0 output differences over 366 invocations), "
    "and the two architecture merges arch-20261019-1 and arch-20261019-2 (ve/document.py split into the ve/document/ package, ve/profile_table.json).",
    "evidence that none is writable by a translator for the UDHR: the DELTA.md of each merge says what users see does not change; `acts@0` (the only one aimed at a UDHR blocker, the 8 act-phrase units) is refused by the envelope until ap-1b; "
    "the 4 parts, 64 companions and 148 Lean status rows give the previous run's document ids, statuses, verdicts and rendering byte for byte.",
    "the 38 UNFORMALISED units were searched against these: act-phrase grammar (8 units) needs `acts@0` through a route (ap-1b); the others need norms, causation, attribution, time, comparison, modality/belief or priority-of-rights constructs that no merge here adds."]
m["language_change_for_udhr"] = "none: nothing a translator can write was added; every difference to the previous run is a measurement (timings) and no ledger claim changed."
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits)",
    "no seeded bug in product code (this run changed no file under ve/, lean/ or rust/); the translation's seeded faults are carried (seeded-bugs-translation.json)",
    "JT-5r (the 31 term splits) was not started, as directed",
    "no JT-0p/ET-0/QT-0p/AP-0/SC-M0 section was re-applied: all are already in the carried translation, and re-checked here",
    "no `lake build`: the pinned ve_service of the same commit b1f7ca7ad (sha 295c6123.., listed in lean/checkers.lock) was copied from a sibling worktree; the Rust binary was built by tools/rust_build.py"]

# --- checks
c = m["checks"]
c["build"] = ("ve_service: the pinned binary (sha256 295c612300ec5a69.., in lean/checkers.lock) built from this very commit b1f7ca7ad in a sibling worktree was copied to lean/.lake/build/bin; "
              "Rust: tools/rust_build.py (binary 6422647f.. pinned in lean/checkers.lock, `--check` passes). The Lean library was not rebuilt here.")
c["companions"] = "PASS: 64 companions check (premises model) and 148 Lean status rows as expected; witnesses.json, companions-check.json and readings-rendered.md byte-identical to the previous run's"
c["parts"] = ("PASS: ve document check on all 4 parts at ve-green-ap-1a: premises 'model', CONFLICT-FREE (part01 %.1f s, part02 %.1f s, part03 %.1f s, part04 %.1f s); document ids, unit statuses, coverage, premises and rendering equal to the previous run"
              % (secs["part01"], secs["part02"], secs["part03"], secs["part04"]))
c["unchanged_units"] = "PASS: all 130 units have the same status and row in the part files as in the previous run (no changed unit); source sha256 d6495201.. matches"
c["legacy_document"] = {"check_seconds": 0.1, "coverage": "PASS (100%)", "premises": {"reason": "non-assertion reading elaboration pending", "status": "UNKNOWN"}}
c["whole_document"] = {"load": {"coverage_percent": whole["load"]["coverage_percent"], "seconds": whole["load"]["seconds"]},
                       "check": {"premises": whole["check"]["premises"], "readings_status": whole["check"]["readings_status"], "seconds": whole["check"]["seconds"]},
                       "note": "the same document as last run (translation-whole.ve.md byte-identical); equal verdicts. Wall time %.0f s and %.0f s against 2517 s and 2740 s last run; user CPU equals wall time, so wall time follows the host load (load average 42 to 86 here, about 47 last run), not the language" % (whole["load"]["seconds"], whole["check"]["seconds"])}
c["limits_met"] = [
    "Rust checker: default VE_RUST_TIMEOUT kept. Part01 checks under prlimit --as=6442450944 in %.1f s with a peak child resident set of %.1f MB; no raised limit was needed" % (apa1["wall_seconds"], apa1["peak_child_resident_set_mb_max"]),
    "the whole declaration as ONE document (experiment-whole/): six two-reading sets as RD-4b components and the rest in the main component; at ve-green-ap-1a load_document succeeds after %.1f s (coverage 100%%) and check_document answers CONFLICT-FREE, premises 'model' after %.1f s (previous run 2516.8 s and 2739.9 s)" % (whole["load"]["seconds"], whole["check"]["seconds"]),
    c["limits_met"][2]]
c["repaired_units"] = {"note": "no audit repair and no plan repair this run"}
m["part_checks"] = {k: {**v, "seconds": pc[k]["seconds"]} for k, v in m["part_checks"].items()}
for k, v in m["part_checks"].items():
    old, new = prev["part_checks"][k], pc[k]
    assert old["document_id"] == new["document_id"] == v["document_id"], k

# --- ET-0 / whole / rebuild evidence
m["et0_rerun"]["requalified_at_ap_1a"] = {"VE_RUST_TIMEOUT": "default (unset)", "address_space_cap_bytes": 6442450944, "evidence": "evidence/et0-rerun-prlimit-apa1.json",
    "peak_child_resident_set_mb": apa1["peak_child_resident_set_mb_max"], "verdict": apa1["verdict"], "premises": apa1["premises"], "conflict": apa1["conflict"], "wall_seconds": apa1["wall_seconds"]}
m["et0_rerun"]["whole_declaration"] = {"check_seconds": whole["check"]["seconds"], "load_seconds": whole["load"]["seconds"], "premises": "model", "readings_status": "CONFLICT-FREE"}
m["et0_rerun"]["other_parts_seconds"] = {k: v["seconds"] for k, v in pc.items()}
m["whole_document_experiment"]["components"] = {"load": {"coverage_percent": 100, "seconds": whole["load"]["seconds"]}, "check": {"premises": "model", "readings_status": "CONFLICT-FREE", "seconds": whole["check"]["seconds"]}}
m["whole_document_experiment"]["result"] = "loads and checks at ve-green-ap-1a"
m["whole_document_experiment"]["note"] = "whole.py was NOT re-run; experiment-whole/translation-whole.ve.md is carried unchanged from the previous run and loaded/checked again at ve-green-ap-1a (whole_check.py load, then check)"
for k, v in rb.items():
    assert (v["check_noop_exit"] == 0) == (k == "part03"), (k, v)
    m["rebuild_command_check"][k] = v
m["rebuild_command_check"].pop("requalified_at_et_3b", None)
m["rebuild_command_check"]["requalified_at_ap_1a"] = "part01, part02, part04 and the whole declaration `--check-noop` still exit 2 ('rebuild is not a no-op'); part03 is a no-op; the rebuilt documents of the first four still fail to load ('invalid situation'); evidence/rebuild-command.json"
m["language_findings"] = [
    "at ve-green-ap-1a the 4 parts load and check exactly as at ve-green-et-3b: same document ids, unit statuses, coverage, premises (model), CONFLICT-FREE, and rendering; the 64 companions and 148 Lean status rows are identical.",
    "ET-0 bar re-met: part01 checks in %.1f s under prlimit --as=6442450944 with a %.1f MB peak child (default Rust limit kept), premises model, CONFLICT-FREE (previous: 29.1 s, 107.6 MB)." % (apa1["wall_seconds"], apa1["peak_child_resident_set_mb_max"]),
    "the whole declaration as ONE document loads in %.1f s (100%%) and checks in %.1f s (CONFLICT-FREE, premises model); previous run 2516.8 s and 2739.9 s for the identical document. User CPU equals wall time and the host was loaded." % (whole["load"]["seconds"], whole["check"]["seconds"]),
    "the committed `--rebuild-reading-ids` is still not a no-op on part 1 (`--check-noop` exits 2) nor on parts 2, 4 and the whole declaration: the defect found earlier stands. I did not use it and changed no ids.",
    "the natural view still words the two ET-0 predicates as 'has the recorded relation \"committed_on\" ...' (lint-refused wordings; ET-6 restates them).",
    "ap-1a puts lexical acts in the Lean library, but `acts@0` has no profile row until ap-1b and the envelope refuses it, so the 8 act-phrase units (1,403 B) are still blocked: the next feature that moves the UDHR number is ap-1b."]
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n")

# --- units.json: audit marks, notes
u = json.loads((HERE / "units.json").read_text())
for x in u["units"]:
    if x["id"] in sampled:
        x["audit_20261019T1800Z"] = "FAITHFUL"
u["audit_note_20261020T0600Z"] = ("this run changes no unit: no construct a translator can write was merged between ve-green-et-3b and ve-green-ap-1a. The 20261019T1800Z audit (AUDIT.md) sampled 20 units, all FAITHFUL and already audit-verified, "
                                  "and rejected nothing. Claimed and audit-verified bytes stay 5,270 (48.28%).")
(HERE / "units.json").write_text(json.dumps(u, indent=1, ensure_ascii=False) + "\n")
print("ok", len(sampled), "sampled")
