"""Carry the previous run's metrics to this run (no translation unit changed; two ledger lines repaired); record the re-run results at ve-green-rights-licence-relay."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
m = json.loads((HERE / "metrics.json").read_text())
pc = json.loads((HERE / "parts-check.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
OLD, TAG = "ve-green-trust-ties-rd9", "ve-green-rights-licence-relay"
wl, wc = whole["load"], whole["check"]
PREV_WL, PREV_WC = 807.4, 796.8

def swap(x):
    if isinstance(x, str):
        for a in (f"(re-run at {OLD})", f"at {OLD} load_document", f"on all 4 parts at {OLD}", f"re-run at {OLD}", f"at {OLD}:"):
            x = x.replace(a, a.replace(OLD, TAG))
        return x
    if isinstance(x, list):
        return [swap(i) for i in x]
    if isinstance(x, dict):
        return {k: swap(v) for k, v in x.items()}
    return x
m = swap(m)
m["run"] = "run-20261017T0600Z"
m["previous_run"] = "run-20261016T1800Z (ve-green-trust-ties-rd9); its parts, units and metrics are in /home/seyran/code/manage-agents/pilots/udhr/run-20261016T1800Z (earlier runs' copies stay in previous-*/)"
m["previous_baseline"] = OLD
m["baseline"] = TAG
m["features_merged_since_previous_baseline"] = [
    "none a translator can write. The merges since ve-green-trust-ties-rd9: tarch-binding, tarch-cutoff and tarch-store (test-architecture tooling: binding census, answer cutoff, answer store), and rights-licence-relay "
    "(the rights route returns each licence with its grounds, and Python binds them: lean/VE/Rights/Scope.lean `Ground`/`citedBy`, ve/rights_route.py). "
    "The UDHR parts declare documents@1, norm-defaults@0, norms@0, readings@1 and relational-fol@0: not rights@0, so the licence grounds are not reached. No new construct, profile or sentence form for these units."]
m["feature_upgrades"] = {"bytes": 0, "count": 0, "note": "no newly merged feature lets any UNFORMALISED unit move; no translation unit was changed this run", "units": []}
m["plan_repairs"] = []
m["plan_repairs_note"] = "none this run; the earlier plan repairs (u097, u085, u091, u106; u039 not landed) are carried in the parts (plan_repairs_in_carried_state)"
m["changed_units"] = ["u052", "u114"]
m["units_changed_this_run"] = ["u052", "u114"]
m["repaired_units"] = ["u052", "u114"]
m["repaired_unit_reasons"] = {
    "u052": "ledger only (the 20261016T1800Z audit's open gap): units.json listed readings/u052.case_excluded.ve.md as a companion; the asserted candidate has no status point and the file never existed. Companion lists and formal_depth corrected; translation, readings and meanings unchanged.",
    "u114": "ledger only (the 20261016T1800Z audit's open gap): units.json listed readings/u114.no_implied_right.ve.md as a companion; the asserted candidate has no status point and the file never existed. Companion lists and formal_depth corrected; translation, readings and meanings unchanged."}
m["audit_repairs"] = [{"audit": "20261016T1800Z", "unit": u, "reason": m["repaired_unit_reasons"][u]} for u in ("u052", "u114")]
m["language_change_for_udhr"] = ("none for what a translator can write: no construct was added and no translation unit changed (the four translation parts are the previous run's, byte for byte; "
                                 "all 130 units load with the same status and the same row, unit-compare.json). The load of a whole-declaration document still works.")
m["language_findings"] = [
    f"NO NEW TRANSLATION CAPABILITY for the UDHR at {TAG}: the merges since the last run are test-architecture tooling and the rights route's licence grounds, which the translation does not use. The 42 UNFORMALISED units keep the blockers they had.",
    "the four parts load and check at the new tag exactly as before (premises 'model', CONFLICT-FREE under every reading; same document ids, same unit rows, same 118 Lean status rows; part checks " +
    f"{min(v['seconds'] for v in pc.values())} to {max(v['seconds'] for v in pc.values())} s, was 2.7 to 6.9 s)",
    f"the whole declaration as ONE document (experiment-whole/translation-whole.ve.md, rebuilt by whole.py, byte-identical to the previous run's) LOADS in {wl['seconds']} s at {wl['coverage_percent']}% coverage and CHECKS in {wc['seconds']} s with readings {wc['readings_status']} and premises '{wc['premises']}' (previous run: {PREV_WL} s and {PREV_WC} s). Default Rust limit kept; no prlimit run, so no raised limit and no peak resident-set record.",
    "the whole declaration with every candidate in the main document (integrate.py u001 u114) was not re-run this run (earlier result: Python's one-element search finds no separating situation for u111's pair)",
    "the natural view still shows entitlements only as 'classified as <name>'; the rendered parts are byte-identical to the previous run's"]
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits); no seeded bug in product code (no product file under ve/, lean/ or rust/ was changed; see seeded-bugs.md)"]
m["audit_20261016T1800Z"] = {"file": "AUDIT.md (the previous run's, carried unchanged)", "sampled": 20, "faithful": 20, "unfaithful": [], "changed_units_checked": 0,
    "note": "no unit was marked unfaithful or incomplete, so no covered status is withdrawn; audit-verified covered bytes are unchanged (4,660 B, 42.69%); 160 claimed bytes (u098, u110) are still unaudited. Its open ledger gap (two companion files listed but never written) is repaired this run: u052 and u114 (units.json only)."}
for name, v in pc.items():
    if name in m["part_checks"]:
        m["part_checks"][name]["seconds"] = v["seconds"]
lim = m["checks"]["limits_met"]
lim[1] = (f"the whole declaration as ONE document (experiment-whole/): four two-reading sets with their own vocabulary as RD-4b components (u025, u055, u073, u111) and the rest in the main component, built by whole.py; "
          f"at {TAG} load_document succeeds after {wl['seconds']} s (coverage {wl['coverage_percent']}%) and check_document answers {wc['readings_status']}, premises '{wc['premises']}' after {wc['seconds']} s (experiment-whole/whole-check.json)")
m["checks"]["whole_document"] = {"load_seconds": wl["seconds"], "coverage_percent": wl["coverage_percent"], "check_seconds": wc["seconds"],
                                 "readings_status": wc["readings_status"], "premises": wc["premises"], "tag": TAG}
wd = m["whole_document_experiment"]
wd["components"] = {"load": wl, "check": wc}
wd["result"] = "loads and checks at " + TAG
m["qt0p_u097"]["in_this_run"]["note"] = f"carried unchanged; the isolated measurement (qt0p_isolated.py) and the probe rows were re-run at {TAG} and give the same result (unit-compare, qt0p-isolated, refusal-test and witnesses are byte-identical to the previous run's)"
m["rendering_change"] = {"what": "none this run: the rendered parts, readings-rendered.md and witnesses.json are byte-identical to the previous run's", "verdict": "no change"}
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
print("ok", {k: v["seconds"] for k, v in pc.items()}, wl, wc)
