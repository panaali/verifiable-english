# Lean-first batch 14d

Batch 14d moves coupled reading plans and the ALL/SOME/NONE/UNKNOWN verdict over coupled and discourse joint choices to Lean. `ve/readings.py` now relays those decisions and supplies untrusted proof or model proposals. [LEDGER.md](LEDGER.md) maps the deleted Python decisions to their Lean owners. [DELTA.md](DELTA.md) records the standing ruling and the pending A/B review.

The committed implementation adds 390 Lean source lines and deletes 91 Python product lines against the batch base, measured from the fixed base and committed head. The Lean service and response encoder build; the focused choice, document, rights and architecture regressions pass. Three planted bugs in changed Lean and Python files each failed their named test and were removed; see [mutants.json](evidence/mutants.json). The original service SHA-256 is recorded there.

The full nine-corpus A/B, differential fuzz comparison, selected-suite completion, latency evidence, and clean final-head release gate remain in progress. No pass is claimed for them here.

Acceptance: **AGENT** for the route, deletion, schema binding, tests, fault injection and gate evidence; **HUMAN (DRI)** for the pending D1 classification and any A/B delta outside a standing ruling; **EXTERNAL** none.
