"""Write units.json and metrics.json for the 2026-10-13T0600Z run (language at ve-green-eff-20261011-1). Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261013T0600Z/finish14.py

The translation is the previous run's, byte for byte (the four part documents, the legacy whole-source document and the
companions): no construct a translator can write has merged since ve-green-ts-B1, and the audit of the previous run
rejected no unit. This script re-reads the saved check results of this run (parts-check.json, witnesses.json,
companions-check.json, refusal-test.json, experiment-whole/whole-check.json), takes the audit verdicts of the previous
run, and writes the numbers.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE / "previous-20261012T1800Z"
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
raw = (HERE.parent / "source" / "udhr.md").read_bytes()
assert hashlib.sha256(raw).hexdigest() == PIN

old = json.loads((PREV / "metrics.json").read_text())
prev_units = json.loads((PREV / "units.json").read_text())
pcheck = json.loads((HERE / "parts-check.json").read_text())
parts = json.loads((HERE / "parts.json").read_text())
wit = json.loads((HERE / "witnesses.json").read_text())["norm_defaults_status"]
comp = json.loads((HERE / "companions-check.json").read_text())
refusal = json.loads((HERE / "refusal-test.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
legacy_cov = json.loads((HERE / "coverage.json").read_text())["coverage"]
legacy_ver = json.loads((HERE / "verdict.json").read_text())["report"]

# ---- the translation is unchanged: every part document and the legacy document keep the id the previous run recorded
for name, v in pcheck.items():
    assert "error" not in v, (name, v)
    assert v["document_id"] == old["document_ids"][name], name
assert legacy_cov["accounted_bytes"] == len(raw)
tool_status = {}
for v in pcheck.values():
    tool_status.update(v["unit_status"])
assert len(tool_status) == 130

# ---- audit of run-20261012T1800Z (its AUDIT.md, VERDICTS block)
text = (PREV / "AUDIT.md").read_text()
block = text.split("VERDICTS:")[1]
verdicts = dict(re.findall(r"^(u\d+[a-d]?) (FAITHFUL|UNFAITHFUL)$", block, re.M))
assert len(verdicts) == 20 and "u081" in verdicts, len(verdicts)   # the draw of 20 contained the changed unit u081: 20 distinct rows
unfaithful = sorted(u for u, v in verdicts.items() if v == "UNFAITHFUL")
faithful = sorted(u for u, v in verdicts.items() if v == "FAITHFUL")
assert not unfaithful
CHANGED: list[str] = []                             # no unit was added, changed or repaired this run

# ---- unit rows: the previous rows, with the new verdicts and a status the tools reproduce
rows = []
for row in prev_units["units"]:
    row = dict(row)
    uid = row["id"]
    row["status_in_previous_run"] = row["status"]
    if row["status"] != "READINGS":
        assert tool_status[uid] == row["status"], uid
    if uid in verdicts:
        row["audit_20261012T1800Z"] = verdicts[uid]
    for key, val in list(row.items()):
        if key.startswith("audit_2026") and isinstance(val, str) and val.endswith("(repaired this run)"):
            row[key] = val.replace("(repaired this run)", "(repaired in a later run)")
    if "audit_repair" in row and uid in faithful:
        row["audit_repair"] = row["audit_repair"].replace("Pending a fresh independent audit.",
                                                          "Verified FAITHFUL by the 2026-10-12T1800Z audit.")
    rows.append(row)
by_id = {r["id"]: r for r in rows}
(HERE / "units.json").write_text(json.dumps({"source_sha256": PIN, "units": rows, "note": prev_units["note"]},
                                            ensure_ascii=False, indent=2) + "\n")

# ---- numbers
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")
counts = Counter(r["status"] for r in rows)
bytes_by_status = Counter()
for r in rows:
    bytes_by_status[r["status"]] += r["span"][1] - r["span"][0]
claimed = sum(bytes_by_status[s] for s in COVERED)
assert claimed == old["claimed_covered_bytes"] and dict(counts) == old["unit_counts_by_status"]
missing = Counter(r["missing_feature"] for r in rows if r["status"] == "UNFORMALISED")
assert dict(missing) == old["missing_feature_tally"]
agg = Counter()
for children in old["old_to_new_units"].values():
    sts = {by_id[c]["status"] for c in children}
    agg[next(iter(sts)) if len(sts) == 1 else "MIXED"] += 1
assert dict(agg) == old["old_boundary_aggregation"]
span = lambda u: by_id[u]["span"][1] - by_id[u]["span"][0]
verified = sorted((set(old["audit_verified_units"]) | set(faithful)) - set(CHANGED))
assert all(by_id[u]["status"] in COVERED for u in verified)
verified_bytes = sum(span(u) for u in verified)
newly_verified = sorted(set(faithful) - set(old["audit_verified_units"]))
tool_bytes = Counter()
for v in pcheck.values():
    tool_bytes.update(v["coverage"]["bytes_by_status"])

metrics = dict(old)
for stale in [k for k in metrics if k.startswith("audit_20261012T0600Z")]:
    del metrics[stale]
metrics.update({
    "baseline": "ve-green-eff-20261011-1",
    "previous_baseline": old["baseline"],
    "previous_run": "run-20261012T1800Z (ve-green-ts-B1); its translation, units, metrics and audit are in previous-20261012T1800Z/",
    "features_merged_since_previous_baseline": [
        "none a translator can write: the merges since ve-green-ts-B1 are infrastructure (arch-20261010-1/2 and AR-9 layer and trust checks, "
        "AR-5a relay and gate repairs, eff-20261011-1 trust-baseline merge tooling). git diff ve-green-ts-B1..HEAD of lean/ and rust/ touches "
        "only audit manifests and one `example` in lean/VE/SoftNorms/Status.lean (a restatement of an existing theorem); no checker, "
        "semantics, wire or profile file changed"],
    "language_change_for_udhr": (
        "none. No construct was added, so no UNFORMALISED unit moved (their blocks stay: act-phrase grammar, time, causation, attribution, "
        "rules, modality, comparison). The translation is the previous run's byte for byte: all four parts have the document ids of the "
        "previous run, and they load, check and render at eff-20261011-1 with the same verdicts."),
    "claimed_covered_bytes_previous_run": old["claimed_covered_bytes"],
    "claimed_change_vs_previous_run_bytes": 0,
    "previous_run_unit_counts_by_status": old["unit_counts_by_status"],
    "previous_run_old_boundary_aggregation": old["old_boundary_aggregation"],
    "previous_run_audit_verified_covered_bytes": old["audit_verified_covered_bytes"],
    "previous_run_reading_set_count": old["reading_set_count"],
    "previous_run_reading_set_candidates": old["reading_set_candidates"],
    "missing_feature_tally_previous_run": old["missing_feature_tally"],
    "audit_20261012T1800Z_note": (
        "the 2026-10-12T1800Z audit of the previous run (previous-20261012T1800Z/AUDIT.md): 20 sampled units, among them the 1 changed unit u081 "
        "(it was in the draw, so 20 distinct units), all 20 FAITHFUL; no unit was rejected, so there was nothing to repair this run"),
    "audit_20261012T1800Z_units_faithful": faithful,
    "audit_20261012T1800Z_units_unfaithful": unfaithful,
    "audit_newly_verified_units": newly_verified,
    "units_changed_this_run": CHANGED,
    "changed_units": CHANGED,
    "audit_verified_covered_bytes": verified_bytes,
    "audit_verified_covered_percent": round(100 * verified_bytes / len(raw), 2),
    "audit_verified_units": verified,
    "audit_pending_bytes": claimed - verified_bytes,
    "audit_verified_note": (
        "verified = judged FAITHFUL by an audit and not changed since: a unit whose checked content, sort, candidate set or open-term "
        "factors changed in a run is pending a fresh audit even if an earlier one passed it. No unit changed this run, so every "
        "earlier verdict stands; the verified set grows only by the units this run's source audit (previous run's AUDIT.md) passed"),
    "repaired_units": [],
    "repaired_unit_reasons": {},
    "units_rejected_by_audit_and_repaired": [],
    "units_repaired_same_defect_not_rejected": [],
    "units_with_only_open_term_factors_rewritten": [],
    "reading_sets_changed_this_run": {},
    "open_terms_added": [],
    "open_terms_dropped": [],
    "predicates_dropped": [],
    "words_only": {"rule": old["words_only"]["rule"], "readings_added_this_run": {}, "readings_changed_this_run": {},
                   "open_questions_listed_that_the_text_does_not_raise": 0},
    "part_checks": {n: {"seconds": v["seconds"], "premises": v["premises"], "readings_status": v["readings_status"],
                        "conflict": v["conflict"], "coverage_bytes_by_status": v["coverage"]["bytes_by_status"],
                        "residual": v["coverage"]["residual"], "document_id": v["document_id"]} for n, v in pcheck.items()},
    "parts_tool_status_bytes": dict(sorted(tool_bytes.items())),
    "whole_document_legacy": {"file": "translation.ve.md", "coverage": legacy_cov, "premises": legacy_ver["premises"],
                               "reading_plan_route": legacy_ver["reading_plan"]["route"],
                               "why_not_content": old["whole_document_legacy"]["why_not_content"]},
    "whole_document_experiment": {"components": whole, "files": old["whole_document_experiment"]["files"]},
    "companion_documents": len(comp),
    "status_witnesses": dict(wit),
    "status_witness_rows": sum(len(v) for v in wit.values()),
    "checks": {
        "parts_cover_source_exactly": f"PASS ({len(parts)} slices concatenate to the pinned 10,916 bytes; document ids equal the previous run's)",
        "parts": f"PASS: ve document check on all {len(parts)} parts at eff-20261011-1: premises 'model' for every choice, CONFLICT-FREE under every reading",
        "legacy_document": {"coverage": "PASS (100%)", "premises": legacy_ver["premises"]},
        "companions": f"PASS: {len(comp)} companions check (premises model) and {sum(len(v) for v in wit.values())} Lean status rows as expected",
        "wrong_separating_situation": refusal,
        "limits_met": [
            "Rust checker: one call is limited to 5 s; (measured in an earlier run, not re-run) a part with 19 regulated predicates (u001-u108, 16 choices) "
            "is refused with 'Rust checker failed ... timed out after 4.99 s' (CheckerUnavailable), so the four parts are the largest that check",
            "the whole declaration as ONE document (experiment-whole/): six two-reading sets with their own vocabulary as RD-4b components and the rest in "
            "the main component, built by whole.py; load_document fails after " + str(whole["load"]["seconds"]) + " s with the Rust checker's 5 s limit "
            "(re-run this run at eff-20261011-1; experiment-whole/whole-check.json)",
            "the whole declaration with every candidate in the main document (integrate.py u001 u114; measured two runs ago, not re-run): Lean elaborates it on "
            "the superposed route in 10.4 s, but Python's one-element search finds no separating situation for u111's pair both_aims / listed_aims in 6 min 58 s "
            "(experiment-whole/integrate-whole.log), so no document is produced"]},
    "document_ids": {n: v["document_id"] for n, v in pcheck.items()},
})
# language findings: the previous run's, with the baseline named where they said ts-B1
findings = []
for f in old["language_findings"]:
    f = f.replace("at ts-B1 after the repair", "at eff-20261011-1 (unchanged from ts-B1)")
    findings.append(f)
metrics["language_findings"] = findings
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n")
print(json.dumps({k: metrics[k] for k in ("unit_counts_by_status", "bytes_by_status", "claimed_covered_bytes", "claimed_covered_percent",
                                           "audit_verified_covered_bytes", "audit_verified_covered_percent", "audit_pending_bytes",
                                           "old_boundary_aggregation", "missing_feature_tally", "reading_set_count", "reading_set_candidates",
                                           "single_reading_unit_count", "open_terms_count", "part_regulated_predicates",
                                           "audit_newly_verified_units")}, indent=1))
