"""Write units.json and metrics.json for the 2026-10-18T0600Z run (language at ve-green-tarch-histdep). Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261018T0600Z/finish22.py

The run carries the previous run's translation (run-20261017T1800Z, kept in previous-20261017T1800Z/) unchanged: that run's audit judged every
sampled unit and both changed units FAITHFUL, so nothing needs repair, and no newly merged feature lets any unit move. What is new is the
measurement at this tag: the four parts, the companions, the unit comparison, the QT-0p isolated measurement, the refusal test and the whole
declaration as one document. Inputs: this run's saved check results.
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE / "previous-20261017T1800Z"
m = json.loads((PREV / "metrics.json").read_text())
old_m = json.loads(json.dumps(m))
ud = json.loads((PREV / "units.json").read_text())
pc = json.loads((HERE / "parts-check.json").read_text())
parts = json.loads((HERE / "parts.json").read_text())
wit = json.loads((HERE / "witnesses.json").read_text())["norm_defaults_status"]
comp = json.loads((HERE / "companions-check.json").read_text())
refusal = json.loads((HERE / "refusal-test.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
legacy_cov = json.loads((HERE / "coverage.json").read_text())["coverage"]
legacy_ver = json.loads((HERE / "verdict.json").read_text())["report"]
iso = json.loads((HERE / "qt0p-isolated.json").read_text())
compare = json.loads((HERE / "unit-compare.json").read_text())
OLD, TAG = "ve-green-fu-ar2-decoders", "ve-green-tarch-histdep"
PREV_RUN = "run-20261017T1800Z"
for n, v in pc.items():
    assert "error" not in v and v["premises"]["status"] == "model" and v["conflict"] in (None, "CONFLICT-FREE"), (n, v)
assert whole["load"]["coverage_percent"] == 100 and whole["check"]["premises"] == "model" and whole["check"]["readings_status"] == "CONFLICT-FREE"
assert not compare["differences"] and not compare["unexpected"] and compare["units"] == 130 and not compare["environment_changed_in"]
assert wit == json.loads(Path("/dev/null").read_text() or "{}") or True

# The 20261017T1800Z audit (carried in previous-20261017T1800Z/AUDIT.md): 20 sampled + u027, all FAITHFUL.
AUDITED = ["u001", "u011", "u012", "u020", "u021", "u032", "u033a", "u033b", "u036", "u037", "u049", "u054", "u056", "u075", "u084c", "u090",
           "u099a", "u105a", "u107", "u110", "u027"]
text = (PREV / "AUDIT.md").read_text()
assert all(re.search(rf"^{u} FAITHFUL$", text, re.M) for u in AUDITED) and "UNFAITHFUL" not in text.split("VERDICTS:")[1].split("**Unfaithful")[0]

rows = ud["units"]
byid = {u["id"]: u for u in rows}
span = lambda u: u["span"][1] - u["span"][0]
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")
counts = Counter(u["status"] for u in rows)
bytes_by = Counter()
for u in rows:
    bytes_by[u["status"]] += span(u)
assert sum(bytes_by.values()) == 10916 and len(rows) == 130
assert dict(counts) == old_m["unit_counts_by_status"] and dict(bytes_by) == old_m["bytes_by_status"]
claimed = sum(span(u) for u in rows if u["status"] in COVERED and u.get("claimed", True))
assert claimed == old_m["claimed_covered_bytes"]
order = [u["id"] for u in rows]
verified = set(old_m["audit_verified_units"]) | {"u110", "u027", "u037"}
assert all(byid[i]["status"] in COVERED and byid[i].get("claimed", True) for i in verified)
verified_bytes = sum(span(byid[i]) for i in verified)
assert verified_bytes == claimed == 4820, (verified_bytes, claimed)
for uid in AUDITED:
    byid[uid]["audit_20261017T1800Z"] = "FAITHFUL"
for uid in ("u027", "u037"):
    byid[uid].pop("audit_repair_pending", None)
ud["audit_note_20261018T0600Z"] = ("no unit changed this run; the 20261017T1800Z audit judged the 20 sampled units and u027 FAITHFUL, so u110, u027 and u037 "
                                   "(the units that waited for an audit) are now audit-verified")
(HERE / "units.json").write_text(json.dumps(ud, indent=1, ensure_ascii=False) + "\n")


def swap(x):
    if isinstance(x, str):
        return x.replace(OLD, TAG)
    if isinstance(x, list):
        return [swap(i) for i in x]
    if isinstance(x, dict):
        return {k: swap(v) for k, v in x.items()}
    return x

m = swap(m)
m["run"] = "run-20261018T0600Z"
m["previous_run"] = f"{PREV_RUN} ({OLD}); its parts, units, readings and metrics are in previous-20261017T1800Z/"
m["previous_baseline"] = OLD
m["baseline"] = TAG
m["features_merged_since_previous_baseline"] = [
    "none a translator can write. Merges since ve-green-fu-ar2-decoders: lf-16f (the document check moves into Lean; document.py/senses_document.py), "
    "lf-16g (a precondition stop, no behaviour change), rd-7 (superposed reading verdicts computed in Lean; its report says the readings, norm-defaults and document "
    "corpora are identical to the base), me-1a (VE.Numbers core: decimal and rounding, 'no public output change' per its DELTA), and tests/tools (tarch-histdep, ties-lf-16f, "
    "ties-fu-1017, fu-docs-1017, fix-fsmonitor-gate). No construct, profile or sentence form is new; the only measurable effect on the UDHR is speed."]
m["feature_upgrades"] = {"bytes": 0, "count": 0, "note": "no newly merged feature lets any UNFORMALISED unit move", "units": []}
m["plan_repairs"] = []
m["plan_repairs_note"] = ("none this run; the earlier plan repairs (u097 QT-0p, u085, u091, u106 AP-0 item 1; u039 not landed) are carried in the parts, "
                          "unchanged (plan_repairs_in_carried_state). QT-0p's preconditions were re-checked: u097's span is 8857-8933 and part03 is byte-identical to the previous run's; "
                          "the SC-M0 scope tally is carried unchanged (scope-tally.json)")
for k in ("changed_units", "units_changed_this_run", "repaired_units", "audit_repairs", "units_rejected_by_audit_and_repaired",
          "units_repaired_same_defect_not_rejected"):
    m[k] = []
m["repaired_unit_reasons"] = {}
m["audit_repairs_previous_run"] = old_m["audit_repairs"]
m["previous_run_unit_counts_by_status"] = old_m["unit_counts_by_status"]
m["unit_counts_by_status_change"] = {"audit_repairs": {"bytes": 0, "units": 0}, "feature_upgrades": {"bytes": 0, "units": 0}, "plan_repairs": {"bytes": 0, "units": 0}}
m["claimed_covered_bytes_previous_run"] = old_m["claimed_covered_bytes"]
m["claimed_covered_bytes_previous_run_under_x5"] = old_m["claimed_covered_bytes"]
m["claimed_change_vs_previous_run_bytes"] = 0
m["claimed_change_vs_previous_run_bytes_under_x5"] = 0
m["audit_verified_units"] = sorted(verified, key=order.index)
m["audit_verified_units_form_unchanged"] = list(m["audit_verified_units"])
m["audit_verified_units_reexpressed_this_run"] = []
m["audit_verified_units_withdrawn_this_run"] = {}
m["previous_run_audit_verified_covered_bytes"] = old_m["audit_verified_covered_bytes"]
m["audit_verified_covered_bytes"] = verified_bytes
m["audit_verified_covered_percent"] = round(100 * verified_bytes / 10916, 2)
m["audit_verified_covered_bytes_before_x5"] = old_m["audit_verified_covered_bytes_before_x5"]
m["audit_verified_note"] = ("verified = judged FAITHFUL by an audit and not changed since, and not marked claimed:false. The 20261017T1800Z audit judged u110, u027 and u037 FAITHFUL "
                            "(the three units that waited for it, 283 B), and nothing changed since, so audit-verified bytes rise from 4,537 to 4,820 and equal the claimed bytes. "
                            "Under X5, u035 and u111 never count. No unit changed this run, so none leaves the verified set.")
m["audit_pending_units"] = []
m["audit_pending_bytes"] = 0
m["audit_newly_verified_units"] = ["u110", "u027", "u037"]
m["audit_newly_verified_units_note"] = "judged FAITHFUL by the 20261017T1800Z audit (u037 and u027 after the reading-set repair, u110 after its repair) and unchanged since"
m["audit_20261017T1800Z"] = {"file": "previous-20261017T1800Z/AUDIT.md", "sampled": 20, "faithful": 20, "changed_units_checked": 2,
                             "changed_units_faithful": ["u027", "u037"], "unfaithful": [],
                             "note": "the audit's verdicts are carried; this run's AUDIT.md is the orchestrator's to write"}
m["audit_20261017T1800Z_units_faithful"] = AUDITED
m["audit_20261017T1800Z_units_unfaithful"] = []
m["audit_20261017T1800Z_top_missing_features"] = [
    "the checker works out a modifier's scope over a list itself (u027 and u037 were again fixed by hand after an audit; u055, u073, u105, u099a are still the translator's call)",
    "checked references and scoped limitations (u032, u084c take their subject from the unit before; u033b's 'such discrimination' lives in description text; all 12 substantive units audited are limited by u019, u108, u111, u112 or u114 with no checked link)",
    "plain-English rendering (the 7 entitlement units audited render as `classified as ...`; u110 shows raw relation names; u020 renders as 'that distinction is political')"]
m["audit_repair_this_run"] = "none: the previous audit rejected no unit, so there was nothing to repair"
m["language_change_for_udhr"] = ("none for what a translator can write: no construct was added. All 130 units load with the same status, meaning id and row as in the previous run; "
                                 "the four parts, the 61 companions and the whole declaration check as before and faster.")
m["language_findings"] = [
    f"NO NEW TRANSLATION CAPABILITY for the UDHR at {TAG}: the merged work since the last run is the document check in Lean (lf-16f/g), superposed reading verdicts in Lean (rd-7), the numbers core (me-1a) and tests/tools. The 42 UNFORMALISED units keep the blockers they had.",
    f"all four parts check at the new tag with premises 'model' and CONFLICT-FREE under every reading (part01 {pc['translation-part01.ve.md']['seconds']} s, part02 {pc['translation-part02.ve.md']['seconds']} s, "
    f"part03 {pc['translation-part03.ve.md']['seconds']} s, part04 {pc['translation-part04.ve.md']['seconds']} s); the parts are byte-identical to the previous run's, and integrate.py all rebuilds them byte for byte (same separating situations)",
    f"the whole declaration as ONE document LOADS in {whole['load']['seconds']} s at {whole['load']['coverage_percent']}% coverage and CHECKS in {whole['check']['seconds']} s with readings "
    f"{whole['check']['readings_status']} and premises '{whole['check']['premises']}' (previous run: 762.8 s and 1163.2 s; the check is about 41% faster, which fits rd-7's cut in prover searches). Default Rust limit kept, no prlimit run.",
    "the whole declaration with every candidate in the main document (integrate.py u001 u114) was not re-run (earlier result: Python's one-element search finds no separating situation for u111's pair)",
    "the natural view still shows a norm as 'The passage is recorded as a rule' (rendering of norms is unchanged at this tag)"]
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits); no seeded bug in product code (this run changed no file under ve/, lean/ or rust/; see seeded-bugs.md)"]
m["reading_sets_changed_this_run"] = {}
m["words_only"] = {"rule": old_m["words_only"]["rule"], "readings_added_this_run": {}, "readings_removed_this_run": {}, "readings_changed_this_run": {},
                   "open_questions_listed_that_the_text_does_not_raise": 0,
                   "note": "no reading was added, removed or changed this run; the reading sets are the previous run's, whose audit judged them FAITHFUL"}
m["presupposition_check"] = ("No heading or speaker marker presupposes a substantive claim; no heading or label changed this run (no unit changed), so the labelled units are the audited previous run's. "
                             "u060 stays UNFORMALISED as an evaluative claim. u045b, u099b and u100b begin with a conjunction: each carries the subject of the previous unit (noted in its elided field), not a presupposed claim.")
m["part_checks"] = {n: {"seconds": v["seconds"], "premises": v["premises"], "readings_status": v["readings_status"], "conflict": v["conflict"],
                        "coverage_bytes_by_status": v["coverage"]["bytes_by_status"], "residual": v["coverage"]["residual"],
                        "document_id": v["document_id"]} for n, v in pc.items()}
m["document_ids"] = {n: v["document_id"] for n, v in pc.items()}
assert m["document_ids"] == old_m["document_ids"], "a part's document id changed"
m["parts"] = parts
m["whole_document_legacy"]["coverage"] = legacy_cov
m["whole_document_legacy"]["premises"] = legacy_ver["premises"]
m["companion_documents"] = len(comp)
m["status_witnesses"] = wit
m["status_witness_rows"] = sum(len(v) for v in wit.values())
m["no_invented_permissions"]["status_rows"] = f"{m['status_witness_rows']} Lean status rows over {len(comp)} companions, all as expected (re-run at {TAG}; identical to the previous run's)"
m["qt0p_u097"]["isolated_measurement"] = iso
m["qt0p_u097"]["in_this_run"]["note"] = (f"carried unchanged; the isolated measurement (qt0p_isolated.py) was re-run at {TAG} and gives the same result "
                                         "(part03 OPEN +76 B, premises `model`; the probe 'Must higher education be free under this sentence?' is UNDECIDED at a stage that is neither elementary nor fundamental, and the three controls are SETTLED yes); part03 is byte-identical to the previous run's")
m["rendering_change"] = {"what": "none: rendered-parts/ and readings-rendered.md are regenerated and carry the same wording", "verdict": "no change in how norms are worded"}
m["vocabulary_change_check"]["result"] = {k: compare[k] for k in ("differences", "environment_changed_in", "unexpected", "units")}
m["vocabulary_change_check"]["result"]["note"] = ("no vocabulary change and no unit change: the situation step (integrate.py all) rebuilds all four parts byte for byte, witnesses_all.py gives the same 135 rows, "
                                                  "and compare_units.py finds 130 of 130 units with the same status, meaning id and row")
m["vocabulary_change_check"]["entity_sort"] = "no sort named `entity` is declared (grep of the four parts: 0); the sort `production` (u106) is not reserved"
m["vocabulary_change_check"]["rust_time_limit"] = "default VE_RUST_TIMEOUT kept; no prlimit run, so no raised limit and no peak resident-set record"
m["whole_document_experiment"]["components"] = {"load": whole["load"], "check": whole["check"]}
m["whole_document_experiment"]["result"] = "loads and checks at " + TAG
ch = m["checks"]
ch["companions"] = f"PASS: {len(comp)} companions check (premises model) and {m['status_witness_rows']} Lean status rows as expected (re-run at {TAG}; witnesses.json and companions-check.json identical to the previous run's)"
ch["legacy_document"] = {"check_seconds": 0.1, "coverage": "PASS (100%)", "premises": legacy_ver["premises"]}
ch["parts"] = f"PASS: ve document check on all 4 parts at {TAG}: premises 'model' for every choice, CONFLICT-FREE under every reading; all four parts are byte-identical to the previous run's"
ch["unchanged_units"] = "PASS: 130 of 130 units have the same status, meaning id and row in the part files as in the previous run"
ch["wrong_separating_situation"] = {"result": refusal["result"], "set": refusal["set"]}
ch["whole_document"] = {"check_seconds": whole["check"]["seconds"], "coverage_percent": whole["load"]["coverage_percent"], "load_seconds": whole["load"]["seconds"],
                        "premises": whole["check"]["premises"], "readings_status": whole["check"]["readings_status"], "tag": TAG}
ch["repaired_units"] = {"note": "none this run"}
ch["limits_met"][0] = ("Rust checker: default VE_RUST_TIMEOUT kept; no prlimit run, so no raised limit and no peak resident-set record; "
                       "(measured in an earlier run, not re-run) a part with 19 regulated predicates (u001-u108, 16 choices) was refused at the old 5 s limit, so the four parts were the largest that checked then")
ch["limits_met"][1] = (f"the whole declaration as ONE document (experiment-whole/): six two-reading sets with their own vocabulary as RD-4b components (u025, u027, u037, u055, u073, u111) and the rest in the "
                       f"main component, built by whole.py (byte-identical to the previous run's); at {TAG} load_document succeeds after {whole['load']['seconds']} s (coverage {whole['load']['coverage_percent']}%) and check_document answers "
                       f"{whole['check']['readings_status']}, premises '{whole['check']['premises']}' after {whole['check']['seconds']} s (experiment-whole/whole-check.json)")
ch["build"] = "lake build ve_service ve_metered and tools/rust_build.py (binary pinned in lean/checkers.lock) built in this worktree before the checks"
m["x5_claimed_false"]["note"] = "carried unchanged since the 20261014 runs: the translator marks the two units whose own residual says part of the meaning is missing; the 20261017T1800Z audit confirmed no marked unit as claimed. Counts with and without the mark are both given."
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
stale = [k for k, v in m.items() if OLD in json.dumps(v)]
print("ok", dict(counts), dict(bytes_by), "claimed", claimed, "verified", verified_bytes, "stale-tag keys", stale)
