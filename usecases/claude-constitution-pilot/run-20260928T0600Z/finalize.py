"""Cross-check VE reports against the translation ledger and record pilot metrics."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ve.document import load_document

RUN = Path(__file__).resolve().parent
SOURCE = (RUN.parent / "source/claude-constitution.md").read_bytes()
ledger = json.loads((RUN / "units.json").read_text())
metrics = json.loads((RUN / "metrics.json").read_text())
check = json.loads((RUN / "check.json").read_text())
coverage = json.loads((RUN / "coverage.json").read_text())
prior = json.loads((RUN / "previous-run-metrics.json").read_text())

assert hashlib.sha256(SOURCE).hexdigest() == metrics["source_sha256"]
assert SOURCE == load_document(RUN / "translation.ve.md")["source"]
assert coverage["accounted_bytes"] == coverage["source_bytes"] == len(SOURCE)
assert coverage["coverage_percent"] == 100
assert coverage["bytes_by_status"] == {k: v for k, v in metrics["sentence_clause_units"]["bytes_by_status"].items() if v}
assert check["admission"]["admitted"] is True
assert check["premises"]["status"] == "model"
assert check["reading_plan"]["route"] == "single"
assert [r["id"] for r in ledger if r["status"] == "OPEN"] == ["u0165.s07"]
assert next(r for r in ledger if r["id"] == "u0214.s01")["status"] == "UNFORMALISED"
assert (RUN / "checked-natural.md").read_text().strip() == "Claude is not human."

metrics["previous_run_20260927T1800Z_sentence_clause_units"] = prior["sentence_clause_units"]
metrics["check_verdicts"] = {
    "document_loaded_and_english_fence_parsed": True,
    "graph_admitted": True,
    "premises_status": check["premises"]["status"],
    "premises_model_id": check["premises"]["model_id"],
    "reading_plan": check["reading_plan"]["route"],
    "source_id": check["source_id"],
    "document_id": check["document_id"],
    "coverage_percent": coverage["coverage_percent"],
    "natural_render_checked_clause": (RUN / "checked-natural.md").read_text().strip(),
    "norm_unit": "u0165.s07",
    "norm_unit_status": "OPEN",
}
(RUN / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")

summary = """# Claude constitution pilot, 28 September 06:00 UTC
The pinned 184,893-byte source is unchanged, and all source bytes are assigned to 1,124 sentence or clause units.
One hard-constraint bullet is now an admitted rule: Claude must not generate child sexual abuse material; the material classification remains an open term.
The unit counts are 1 CHECKED, 39 LABELLED, 1 OPEN, 0 READINGS, and 1,083 UNFORMALISED.
At the 299 older boundaries, the counts are 1 CHECKED, 10 LABELLED, 30 MIXED, and 258 UNFORMALISED.
Claimed covered bytes are 419 (0.2266%); independently audit-verified covered bytes remain 22 (0.0119%).
Six terms have unresolved deciders, no reading set is admitted, and 676 units still cite norms as their main missing feature.
The latest prior audit rejected no sampled units; the earlier rejected principal-hierarchy unit remains unformalised.
The checker admitted the document and found a premise model; byte coverage is 100%.
The document renderer calls the OPEN rule a “Checked reading”; the ledger and coverage report give its actual status.
"""
(RUN / "SUMMARY.md").write_text(summary)
