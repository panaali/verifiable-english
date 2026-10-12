# Lean-first batch 14d

Batch 14d moves coupled reading plans and the ALL/SOME/NONE/UNKNOWN verdict over coupled and discourse joint choices to Lean. `ve/readings.py` now relays those decisions and supplies untrusted proof or model proposals. [LEDGER.md](LEDGER.md) maps the deleted Python decisions to their Lean owners. [DELTA.md](DELTA.md) records the standing rulings and the completed A/B review.

The implementation adds 393 Lean source lines and deletes 91 Python product lines against the fixed batch base; 405 lines are deleted across the whole diff. The Lean service and response encoder build; the focused choice, document, rights and architecture regressions pass. The trust table classifies every new Lean declaration (zero unclassified lines), and `test_committed_trust_table_covers_every_declaration` passes. Six planted bugs in changed Lean and Python files each failed their named test and were removed; see [mutants.json](evidence/mutants.json). The restored service SHA-256 is recorded there. `lean/checkers.lock` pins that one new service binary; temporary mutant hashes were removed through `tools/regen_generated.py`.

The official nine-corpus A/B compared 100,333 records per side: 100,326 identical available outcomes, seven identical unavailable pilots signed under R7, and zero unlisted differences ([full-ab.json](evidence/full-ab.json)). The readings subset is identical on 1,137 records ([readings-ab.json](evidence/readings-ab.json)). The new `readings-choices` relay refused all 1,617 mutations of ten request shapes ([relay-mutations.json](evidence/relay-mutations.json)). `test_mutated_genuine_responses_agree_with_lean_decoders` passes after Python's malformed-unit fallback was aligned with Lean's request binding. The pilot comparator canonicalizes only its own scratch-directory prefix in diagnostic text; `test_pilot_comparison_normalizes_only_its_own_scratch_directory` proves that a changed file name still differs, and the seeded `expose_pilot_scratch_directory` fault made that test fail. All 75 comparator tests pass. The resolved 486-document pilot comparison has 479 identical available answers and seven identical unavailable pairs.

The paired coupled-verdict CPU sample has the same `SOME` answer and median CPU 661 ms at the base versus 659 ms at the head ([latency.json](evidence/latency.json)). All 15 CI and date-seed differential fuzz pairs passed with zero head-only findings and no missing baseline entry ([difffuzz-ab.json](evidence/difffuzz-ab.json)). Three document checks hit Rust's five-second deadline in the loaded head recording; paired base/head retries at a 60-second checker deadline returned identical reports ([document-retry.json](evidence/document-retry.json)). The broad selected run was interrupted under heavy host load after more than 280 files had produced results; focused failures caused by earlier changes were fixed and rerun, while remaining timeouts are not counted as passes. The clean final-head release gate remains pending and is the acceptance test for the full suite.

## Seeded bugs

Each planted change failed the named test in [mutants.json](evidence/mutants.json) and was removed:

- `ignore_coupling_labels` in `lean/VE/Service/ReadingsChoices.lean` admitted four choices where two were compatible.
- `mixed_evidence_is_all` in `lean/VE/Service/ReadingsChoices.lean` returned ALL for mixed evidence instead of SOME.
- `couplings_bypass_lean` in `ve/readings.py` suppressed the Lean verdict request.
- `expose_pilot_scratch_directory` in `tools/lean_first_diff.py` made identical pilot diagnostics compare differently.
- `accept_different_unavailable_outputs` in `tools/batch_evidence.py` incorrectly signed a changed timeout.
- `use_untyped_request_unit_as_binding` in `ve/backends/service_schema.py` crashed on a request unit that Lean binds through its set ID.

Acceptance: **AGENT** for the route, deletion, schema binding, tests, fault injection and gate evidence; **HUMAN (DRI)** for the pending D1 classification and any A/B delta outside a standing ruling; **EXTERNAL** none.
