"""Carry the previous run's metrics to this run (no unit changed); record the re-run results at ve-green-fix-abbrev."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
m = json.loads((HERE / "metrics.json").read_text())
pc = json.loads((HERE / "parts-check.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
TAG = "ve-green-fix-abbrev"

def swap(x):
    if isinstance(x, str):
        return (x.replace("(re-run at ve-green-lf-14b)", f"(re-run at {TAG})")
                 .replace("re-run this run at ve-green-lf-14b; previous run 1022.1 s", f"re-run this run at {TAG}; previous run 1022.1 s")
                 .replace("PASS: ve document check on all 4 parts at ve-green-lf-14b", f"PASS: ve document check on all 4 parts at {TAG}")
                 .replace("were re-run at ve-green-lf-14b and give", f"were re-run at {TAG} and give"))
    if isinstance(x, list):
        return [swap(i) for i in x]
    if isinstance(x, dict):
        return {k: swap(v) for k, v in x.items()}
    return x
m = swap(m)
secs = whole["load"]["seconds"]
m["run"] = "run-20261015T1800Z"
m["previous_run"] = "run-20261015T0600Z (ve-green-lf-14b); its translation, units, metrics, audit and summary are in previous-20261015T0600Z/ (earlier runs' copies stay beside them)"
m["previous_baseline"] = "ve-green-lf-14b"
m["baseline"] = TAG
m["features_merged_since_previous_baseline"] = [
    "none a translator can write. The merges since ve-green-lf-14b: question-answering/q2 (qa-q2: `ve ask DOC QUESTION` answers a yes-or-no question about a document in Lean's words, with the `ask` and `words` service modes; a reader-side feature, no construct, profile or limit a translator can write changed), lean-first b14a (lf-14a: the `definitions@0` sugar is read by Lean; the Python fallback is deleted; the corpus answers are identical), infra/layer-research, infra/map-version-notice, infra/tarch-b1 and fix/abbrev (test code only)."]
m["feature_upgrades"] = {"bytes": 0, "count": 0, "note": "no newly merged feature lets any UNFORMALISED unit move; nothing was changed this run", "units": []}
m["changed_units"] = []
m["plan_repairs"] = []
m["units_changed_this_run"] = []
m["repaired_units"] = []
m["language_change_for_udhr"] = (f"none. No construct was added and no unit changed: the four translation parts are the previous run's, byte for byte, and all 130 units load with the same status and the same row (unit-compare.json, no difference). The checks were re-run on the new tag ({TAG}: Lean, Rust and Python) and give the same results. The one new capability is reader-side: `ve ask` (see language_findings).")
m["language_findings"] = [
    f"NO NEW TRANSLATION CAPABILITY for the UDHR at {TAG}: qa-q2 adds `ve ask` (answering a question about a document), lf-14a moves the `definitions@0` sugar into Lean, the rest is tooling or test code. No construct a translator can write was added. The 42 UNFORMALISED units keep the blockers they had.",
    "the four parts load and check at the new tag exactly as before (premises 'model', CONFLICT-FREE under every reading; same document ids, same unit rows, same 118 Lean status rows)",
    f"NEW, READER-SIDE: `ve ask` works on the u097 companion document (readings/u097.free_required.ve.md; logs/ask-try.log): 'Must every education kind that is elementary be free?' is answered Yes in 0.6 s, citing the sentence; 'Must every education kind be free?' is 'The text does not settle this' with the situation 'e0 is an education kind'. A question with 'neither ... nor' has no reading with the current vocabulary (refused with the nearest declared wordings). On the whole part03 document `ve ask` is refused: 'ask answers a readings document on the enumerated route with at most 64 compatible readings'. So question answering helps a reader of a single-rule document, not yet of a declaration-sized part.",
    f"LIMIT, size (re-measured): the whole declaration as ONE document still fails to load on the Rust checker's 5 s limit (after {secs} s, was 1022.1 s); the default limit was kept (no prlimit run); the four-part split stays",
    "the natural view still shows entitlements only as 'classified as <name>' (rendered-parts are byte-identical to the previous run's)"]
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits); no seeded bug in product code (no product file under ve/, lean/ or rust/ was changed; see seeded-bugs.md)"]
m["audit_20261015T0600Z"] = {"file": "previous-20261015T0600Z/AUDIT.md", "sampled": 20, "faithful": 20, "unfaithful": [], "changed_units_checked": 0,
    "note": "all 20 sampled units were already in audit_verified_units, so the verified bytes do not change (4,660 B, 42.69%); the auditor's minor note on u027 (no open-term record for 'torture', which changes no meaning) is carried as a note, not a repair"}
for name, v in pc.items():
    if name in m["part_checks"]:
        m["part_checks"][name]["seconds"] = v["seconds"]
wd = m["whole_document_experiment"]
wd.setdefault("components", {})["load"] = whole["load"]
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
print("ok", secs, {k: v["seconds"] for k, v in pc.items()})
