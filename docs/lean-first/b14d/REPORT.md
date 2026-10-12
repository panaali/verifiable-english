# Lean-first batch 14d

Batch 14d moves coupled reading plans and the ALL/SOME/NONE/UNKNOWN verdict over coupled and discourse joint choices to Lean. `ve/readings.py` now relays those decisions and supplies untrusted proof or model proposals. [LEDGER.md](LEDGER.md) maps the deleted Python decisions to their Lean owners. [DELTA.md](DELTA.md) records the standing ruling and the pending A/B review.

The implementation adds 393 Lean source lines and deletes 91 Python product lines against the fixed batch base. The Lean service and response encoder build; the focused choice, document, rights and architecture regressions pass. Four planted bugs in changed Lean and Python files each failed their named test and were removed; see [mutants.json](evidence/mutants.json). The restored service SHA-256 is recorded there.

The readings A/B is identical on 1,137 records ([readings-ab.json](evidence/readings-ab.json)). The new `readings-choices` relay refused all 515 mutations of three genuine response shapes ([relay-mutations.json](evidence/relay-mutations.json)). The pilot comparator now canonicalizes only its own scratch-directory prefix in diagnostic text; `test_pilot_comparison_normalizes_only_its_own_scratch_directory` proves that a changed file name still differs, and the seeded `expose_pilot_scratch_directory` fault made that test fail. All 75 comparator tests pass.

The full nine-corpus A/B, differential fuzz comparison, selected-suite completion, latency evidence, and clean final-head release gate remain in progress. No pass is claimed for them here.

Acceptance: **AGENT** for the route, deletion, schema binding, tests, fault injection and gate evidence; **HUMAN (DRI)** for the pending D1 classification and any A/B delta outside a standing ruling; **EXTERNAL** none.
