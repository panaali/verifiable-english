# Batch 16e work in progress

This checkout does **not** implement batch 16e. No rights residue has been moved to
Lean's `document` mode, and no corpus A/B is claimed. The repository release
gate is recorded below under standing ruling R13.

The 16c ledger names 1,250 rights cases: 1,000 rights documents and 250 with
`readings@1` as the head profile. The generated corpus has the same 1,250 case
names and source hashes. At the current code, a valid first case (`s0`) is
retained with `CheckerUnavailable: document checks under rights@0 need its Lean
profile route`. `measure.py` stops on that case by design. Its retained-case
exception is only for a genuinely invalid prior input.

The existing Lean rights route elaborates sampled cases `s0`,
`s0/readings@1`, `s1`, and `s4`. This is not a document-mode decision: the
document wrapper still refuses these profiles before unit checking. The
remaining integration needs the rights source, its generated vocabulary,
coverage and report fields, and the readings-defaults content in parts to be
returned in a fully typed, request-bound document answer. The sibling review's
quoted-norm and free-document selection cases must be preserved.

`lake build ve_service` and `tools/rust_build.py` passed on the baseline. The
required selected-test command was started on the committed measurement script.
Its `test_english_evidence.py` unit hit the runner's 3,600-second timeout; the
run was stopped while `test_wire_gate_corpus.py` remained active. Other units
reported as passed, including `test_relay_mutation_gate.py`,
`test_route_row_schemas.py`, and `test_document_lean_switch.py`. This is **not**
a passing selected run. At that point no full release gate, nine-corpus A/B,
seeded bugs, or pre-review gate had been performed. The two-file diff against
`main` was reviewed; it contained only this measurement script and report.

Acceptance: the measurement guard and repository release gate are AGENT work
completed; the rights route, batch evidence, and batch tests are AGENT work
pending. There are no HUMAN or EXTERNAL
acceptance items claimed here.

## Pre-review gate continuation

The mechanical pre-review check found no saved passing release gate result.
The first full gate on `ac1d9654` built Lean and Rust and ran the Python suite:
14,388 passed, 92 skipped, and three failed. All three failures were the
parameterizations of
`tests/test_gate_integrity.py::test_interrupted_gate_cannot_record_pass`.
They passed alone (3/3). That test reached its injected interruption only
after checking shared Lean build artifacts, which other tests can rebuild or
prune concurrently. The test now stubs the artifact freshness operations so
the interrupt assertion does not depend on concurrent build state. It still
tests that an interruption leaves the gate record failed.

The three failed cases passed after the fix (3/3). The selected-test command
passed all 88 selected test files and saved its coverage map under a writable
`VE_TESTMAP_CACHE` in `/tmp` (0 failed). The first selected attempt also passed
all 88 files but failed after testing while writing that map to the read-only
home cache. No product code or user-visible behavior changed in this
continuation, so no DRI delta ruling or product-code seeded bug applies.

The full gate on committed `9801fe70` built Lean, passed the Lean audit and
36 Rust tests, and ran 14,483 selected Python tests: 14,390 passed, 92 skipped,
and one failed. Its sole failure was
`tests/test_gate_integrity.py::test_fsmonitor_hook_cannot_hide_edited_source`.
The same-commit serial `tools/gate.py --rerun-failed` ran the entire containing
file: 37 passed, 0 failed, and the failed test's recorded outcome is `passed`.
**SIGNED by standing ruling R13 (DRI-RULINGS.md):** this full gate counts as
passed after its only failing test passed on the same-commit rerun. The saved
records are `evidence/gate-full.json` and `evidence/gate.json`. The latter is
the final gate result (`rerun-passed`, clean, bound to `9801fe70`). The
fsmonitor test is load-sensitive; follow-up is to make its same-length edit
fixture deterministic if it fails again this week.
