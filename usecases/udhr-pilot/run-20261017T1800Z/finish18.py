"""Carry the previous run's metrics to this run (no unit changed); record the re-run results at ve-green-premise-scale."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
m = json.loads((HERE / "metrics.json").read_text())
pc = json.loads((HERE / "parts-check.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
TAG = "ve-green-premise-scale"

def swap(x):
    if isinstance(x, str):
        return (x.replace("(re-run at ve-green-fix-abbrev)", f"(re-run at {TAG})")
                 .replace("on all 4 parts at ve-green-fix-abbrev", f"on all 4 parts at {TAG}")
                 .replace("were re-run at ve-green-fix-abbrev and give", f"were re-run at {TAG} and give"))
    if isinstance(x, list):
        return [swap(i) for i in x]
    if isinstance(x, dict):
        return {k: swap(v) for k, v in x.items()}
    return x
m = swap(m)
wl, wc = whole["load"], whole["check"]
m["run"] = "run-20261016T0600Z"
m["previous_run"] = "run-20261015T1800Z (ve-green-fix-abbrev); its translation parts, units and metrics are in previous-20261015T1800Z/ (earlier runs' copies stay beside them)"
m["previous_baseline"] = "ve-green-fix-abbrev"
m["baseline"] = TAG
m["features_merged_since_previous_baseline"] = [
    "none a translator can write. The merges since ve-green-fix-abbrev: infra/premise-scale (the premise check finds a Lean-checked model where the premises force many things of one sort; a Rust timeout in the premise search is 'no witness'; the default Rust limit of a model search grows with the size of the case, about 4 times its measured time, never under 5 s), lean-first b14c (lf-14c: more of the route wire is decoded by Lean), arch-AR-2, arch-AR-4, tarch-b8, test-tail and fix/x86-cpu-deadline (architecture, test or timing code). No new construct, profile or sentence form."]
m["feature_upgrades"] = {"bytes": 0, "count": 0, "note": "no newly merged feature lets any UNFORMALISED unit move; nothing was changed this run", "units": []}
m["changed_units"] = []
m["plan_repairs"] = []
m["units_changed_this_run"] = []
m["repaired_units"] = []
m["language_change_for_udhr"] = (f"none for what a translator can write: no construct was added and no unit changed (the four translation parts are the previous run's, byte for byte; all 130 units load with the same status and the same row, unit-compare.json). One LIMIT moved: the whole declaration as ONE document now loads and checks at {TAG} (it failed to load in every earlier run).")
m["language_findings"] = [
    "NO NEW TRANSLATION CAPABILITY for the UDHR at " + TAG + ": premise-scale changes how large documents are checked (premise model search, Rust time limit), not what can be written. The 42 UNFORMALISED units keep the blockers they had.",
    "the four parts load and check at the new tag exactly as before (premises 'model', CONFLICT-FREE under every reading; same document ids, same unit rows, same 118 Lean status rows; part checks 4.2 to 9.3 s, was 4.9 to 14.1 s)",
    f"LIMIT MOVED, size: the whole declaration as ONE document (experiment-whole/translation-whole.ve.md: four two-reading sets as components u025, u055, u073, u111, the rest in the main component, 16 choices) now LOADS in {wl['seconds']} s at {wl['coverage_percent']}% coverage and CHECKS in {wc['seconds']} s with readings {wc['readings_status']} and premises '{wc['premises']}'. In the previous run it failed to load on the Rust checker's 5 s limit after 1,228.9 s. Cause: the default Rust limit for a model search now scales with the case (premise-scale, DRI ME1); VE_RUST_TIMEOUT was not set and no prlimit run was made, so no raised limit and no peak resident-set record. The cost is still about 19 minutes to load and 17 minutes to check, so the 4-part split (27 s for all four) stays the practical form; the whole file is the proof that no limit forces the split.",
    "the whole declaration with every candidate in the main document (integrate.py u001 u114) was not re-run this run (earlier result: Python's one-element search finds no separating situation for u111's pair)",
    "the natural view still shows entitlements only as 'classified as <name>' (rendered-parts are byte-identical to the previous run's)"]
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits); no seeded bug in product code (no product file under ve/, lean/ or rust/ was changed; see seeded-bugs.md)"]
m["audit_20261015T1800Z"] = {"file": "AUDIT.md (the previous run's, carried unchanged)", "unfaithful": [], "changed_units_checked": 0,
    "note": "the previous audit found no unfaithful unit; audit-verified covered bytes are unchanged (4,660 B, 42.69%); 160 claimed bytes (u098, u110) are still unaudited"}
for name, v in pc.items():
    if name in m["part_checks"]:
        m["part_checks"][name]["seconds"] = v["seconds"]
lim = m["checks"]["limits_met"]
lim[0] = ("Rust checker: default VE_RUST_TIMEOUT kept (a model search's default limit now scales with the case, premise-scale ME1; other calls keep 5 s); no prlimit run, so no raised limit and no peak resident-set record; "
          "(measured in an earlier run, not re-run) a part with 19 regulated predicates (u001-u108, 16 choices) was refused at the old 5 s limit, so the four parts were the largest that checked then")
lim[1] = (f"the whole declaration as ONE document (experiment-whole/): four two-reading sets with their own vocabulary as RD-4b components (u025, u055, u073, u111) and the rest in the main component, built by whole.py; "
          f"at {TAG} load_document SUCCEEDS after {wl['seconds']} s (coverage {wl['coverage_percent']}%) and check_document answers {wc['readings_status']}, premises '{wc['premises']}' after {wc['seconds']} s (previous run: load failed on the 5 s limit after 1,228.9 s; experiment-whole/whole-check.json)")
m["checks"]["whole_document"] = {"load_seconds": wl["seconds"], "coverage_percent": wl["coverage_percent"], "check_seconds": wc["seconds"],
                                 "readings_status": wc["readings_status"], "premises": wc["premises"], "tag": TAG}
wd = m["whole_document_experiment"]
wd["components"] = {"load": wl, "check": wc}
wd["result"] = "loads and checks at " + TAG
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
print("ok", {k: v["seconds"] for k, v in pc.items()})
