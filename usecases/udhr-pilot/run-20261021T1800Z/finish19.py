"""Carry the previous run's metrics to this run (no unit changed); record the re-run results at ve-green-trust-ties-rd9."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
m = json.loads((HERE / "metrics.json").read_text())
pc = json.loads((HERE / "parts-check.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
OLD, TAG = "ve-green-premise-scale", "ve-green-trust-ties-rd9"

def swap(x):
    if isinstance(x, str):
        return x.replace(f"(re-run at {OLD})", f"(re-run at {TAG})").replace(f"re-run at {OLD} and give", f"re-run at {TAG} and give")
    if isinstance(x, list):
        return [swap(i) for i in x]
    if isinstance(x, dict):
        return {k: swap(v) for k, v in x.items()}
    return x
m = swap(m)
wl, wc = whole["load"], whole["check"]
m["run"] = "run-20261016T1800Z"
m["previous_run"] = "run-20261016T0600Z (ve-green-premise-scale); its parts, units and metrics are in previous-20261016T0600Z/ (earlier runs' copies stay beside them)"
m["previous_baseline"] = OLD
m["baseline"] = TAG
m["features_merged_since_previous_baseline"] = [
    "none a translator can write. The merges since ve-green-premise-scale: rd-9 (the soft chain: readings@1 x soft-norms@0 x norm-defaults@0 under the unspecified completion, with its relay binding), "
    "lean-first b16e (Lean decides document mode for rights@0 and readings@1 documents), and test-architecture, relay-gate, CI-timeout and trust-tie work (infrastructure). "
    "The UDHR parts declare the profiles documents@1, norm-defaults@0, norms@0, readings@1 and relational-fol@0: neither rights@0 nor soft-norms@0, and the source states no exceptions to a 'shall', so the soft chain has nothing to carry. No new construct, profile or sentence form for these units."]
m["feature_upgrades"] = {"bytes": 0, "count": 0, "note": "no newly merged feature lets any UNFORMALISED unit move; nothing was changed this run", "units": []}
m["changed_units"] = []
m["plan_repairs"] = []
m["units_changed_this_run"] = []
m["repaired_units"] = []
m["language_change_for_udhr"] = ("none for what a translator can write: no construct was added and no unit changed (the four translation parts are the previous run's, byte for byte; "
                                 "all 130 units load with the same status and the same row, unit-compare.json). The load of a whole-declaration document still works.")
m["language_findings"] = [
    f"NO NEW TRANSLATION CAPABILITY for the UDHR at {TAG}: rd-9 and b16e concern the soft chain and rights documents, which the translation does not use. The 42 UNFORMALISED units keep the blockers they had.",
    "the four parts load and check at the new tag exactly as before (premises 'model', CONFLICT-FREE under every reading; same document ids, same unit rows, same 118 Lean status rows; part checks " +
    f"{min(v['seconds'] for v in pc.values())} to {max(v['seconds'] for v in pc.values())} s, was 4.2 to 9.3 s)",
    f"the whole declaration as ONE document (experiment-whole/translation-whole.ve.md, rebuilt by whole.py, byte-identical to the previous run's) LOADS in {wl['seconds']} s at {wl['coverage_percent']}% coverage and CHECKS in {wc['seconds']} s with readings {wc['readings_status']} and premises '{wc['premises']}' (previous run: 1,124.1 s and 1,028.3 s). Default Rust limit kept; no prlimit run, so no raised limit and no peak resident-set record. It is still about 13 minutes each, so the 4-part split (under 30 s for all four) stays the practical form.",
    "the whole declaration with every candidate in the main document (integrate.py u001 u114) was not re-run this run (earlier result: Python's one-element search finds no separating situation for u111's pair)",
    "the natural view still shows entitlements only as 'classified as <name>' (rendered-parts are byte-identical to the previous run's)"]
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits); no seeded bug in product code (no product file under ve/, lean/ or rust/ was changed; see seeded-bugs.md)"]
m["audit_20261016T0600Z"] = {"file": "AUDIT.md (the previous run's, carried unchanged)", "unfaithful": [], "changed_units_checked": 0,
    "note": "the previous audit found no unfaithful unit; audit-verified covered bytes are unchanged (4,660 B, 42.69%); 160 claimed bytes (u098, u110) are still unaudited"}
for name, v in pc.items():
    if name in m["part_checks"]:
        m["part_checks"][name]["seconds"] = v["seconds"]
lim = m["checks"]["limits_met"]
lim[0] = ("Rust checker: default VE_RUST_TIMEOUT kept (a model search's default limit scales with the case, premise-scale ME1; other calls keep 5 s); no prlimit run, so no raised limit and no peak resident-set record; "
          "(measured in an earlier run, not re-run) a part with 19 regulated predicates (u001-u108, 16 choices) was refused at the old 5 s limit, so the four parts were the largest that checked then")
lim[1] = (f"the whole declaration as ONE document (experiment-whole/): four two-reading sets with their own vocabulary as RD-4b components (u025, u055, u073, u111) and the rest in the main component, built by whole.py; "
          f"at {TAG} load_document succeeds after {wl['seconds']} s (coverage {wl['coverage_percent']}%) and check_document answers {wc['readings_status']}, premises '{wc['premises']}' after {wc['seconds']} s (experiment-whole/whole-check.json)")
m["checks"]["whole_document"] = {"load_seconds": wl["seconds"], "coverage_percent": wl["coverage_percent"], "check_seconds": wc["seconds"],
                                 "readings_status": wc["readings_status"], "premises": wc["premises"], "tag": TAG}
wd = m["whole_document_experiment"]
wd["components"] = {"load": wl, "check": wc}
wd["result"] = "loads and checks at " + TAG
m["qt0p_u097"]["in_this_run"]["note"] = f"carried unchanged; the isolated measurement (qt0p_isolated.py) and the probe rows were re-run at {TAG} and give the same result"
m["vocabulary_change_check"]["result"]["note"] = "no vocabulary change this run; the situation step and the unit comparison were nevertheless re-run at the new tag and every unit parses unchanged"
m["checks"]["parts"] = m["checks"]["parts"].replace("at ve-green-premise-scale", "at " + TAG)
m["rendering_change"] = {"file": "rendered-parts/translation-part01.md (line 66, the u025 separating situation)",
    "what": "display only: the situation text now states the gap for the regulated predicate the separation line concerns (practice must be prohibited / must not be carried out) instead of one 'text does not say' sentence for each of the six regulated predicates (line 66: 1,548 -> 828 bytes; part01 13,528 -> 12,808 bytes). Cause: rd-9 SC-A, one gap sentence per separation line. The document id, the unit rows and the Lean status rows are unchanged; the other three rendered parts are byte-identical.",
    "verdict": "improvement in the display; no change to meaning"}
m["language_findings"][-1] = "the natural view still shows entitlements only as 'classified as <name>'; its separating-situation text became shorter and precise (rendering_change): three of four rendered parts are byte-identical, part01 differs on one line"
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
print("ok", {k: v["seconds"] for k, v in pc.items()}, wl, wc)
