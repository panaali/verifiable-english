# eff-20261104-1 review F1 fix

Status: F1 fixed; verification results below.
HEAD: this report's commit; implementation commit `bcbb2d4e5`.
Change: rescore checks both plan inputs for named and directory reads in Lake, Lean, and outside tests.
Open items: none; no DRI signature is required because VE outputs do not change.

F1 -> `unread_by_build` gates `tools/trust-classes.json` and `tools/layer_policy.py`; a named or
directory read forces a full run ->
`tests/test_trust_mutants.py::test_a_plan_input_read_by_a_check_forces_a_full_run` -> `bcbb2d4e5`.
The test covers both inputs through outside checks, Lean checks, and directory reads. Existing
plan-only carry tests cover the unread case. The review's `PROBE F1` failed before the fix and
passed after it. This is Python rescore eligibility logic; Lean and Rust product code is unchanged,
so no cross-language mirror applies.

Seeded Python bugs, both restored before commit:

- `tools/trust_mutants.py`: bypassing the unread condition for the class table failed
  `test_a_plan_input_read_by_a_check_forces_a_full_run[outside-check-class-table]`.
- `tools/trust_mutants.py`: bypassing the tool-file check in `previous` failed
  `test_a_plan_input_read_by_a_check_forces_a_full_run[outside-check-plan-only-tool]`.

Verification:

- Local regression tests: 7 passed.
- `lake build`: passed (1296 jobs).
- Lean audit: passed (769 source files, 8570 named theorem declarations).
- Targeted Mac request: runner setup failed before pytest (stale snapshot checkout); its VM fallback
  could not write the `uv` cache. The selected run covers the same test file.
- First selected run: 33 of 35 units passed. Two old tests omitted the required scanned build text;
  they were corrected in `c0f35f625` and pass locally (13 cases plus the scope test).
- Final selected run on `c0f35f625` plus the report snapshot: passed on the Mac (35 units,
  no failed IDs; all 666 `test_trust_mutants.py` tests passed across four chunks).
- Full suite and release gate: intentionally left to the merge train under this item's instructions.

The three tests in `main-known-red.txt` remain pre-existing and were not edited in this branch.
DELTA.md has no VE output rows; the tooling-only reuse change needs no standing ruling citation.
