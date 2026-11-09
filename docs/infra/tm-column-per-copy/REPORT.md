# tm-column-per-copy: each copy of an error is judged at its own column

**Summary.**
- Status: built, waiting for the chain gate. Code commits: 66933f341 (the fix and its test) and c869cec6b (line wraps). The final HEAD is the report commit after them, named in the build report.
- What changed: `tools/trust_mutants.py` only. `run`'s `build` now returns each located error with its own column, so `invalid` judges each copy of a message on its own position. The `(file, line, message)` dict is gone.
- DELTA: none. This is a tool-only change with no user-visible effect on the VE product. No DRI signature is reserved, and trust growth is +0.
- Open: none. The reclass re-check still gives all 12 ids INVALID.

## Problem (review tm-elab-unknown-ov F2, DRI adv0314 item 1)

`run` kept each error's column in `columns: dict[(file, line, message), int]` (`build` filled it, the mutated-declaration branch read it). If one message appeared twice on a line, every copy got the column of the last copy. So a copy outside the mutant's text could be read as inside it, and the mutant was classed INVALID, which is never counted as a survivor, where it should be UNKNOWN.

## Fix

- `build` returns `(file, line, message, column)` for each located error, and `("", 0, text, 0)` when there is no located error. The `columns` dict is removed.
- The mutated-declaration branch passes each error's own column to `invalid`.
- `rebuild` (read by `settle`) and the `settle(found, …)` call drop the column, so they get the same 3-tuples as before.
- `each(...)` and the controls already ignore anything after the message (`f, n, message, *_`, `[0][0]`, `[0][2]`).
- `invalid` (`tools/trust_mutants.py:1341`) is the only reader of a column, and it now gets each copy's own. No other path reads a column. So no key is ambiguous, and the task's fallback for one is not needed.
- Unchanged: the KILLED / SURVIVOR judgement, the barrier, the refusal-table messages, `invalid`, `refused`, `settle` and `judge`. In `git diff 7dbc43ed0...HEAD -- tools/trust_mutants.py`, all four hunks (`@@ -1269`, `-1293`, `-1335`, `-1363`) are inside `run`.

## Tests (`tests/test_trust_mutants.py`)

`test_each_copy_of_an_error_is_read_at_its_own_column` (6 cases) drives `run` itself. It uses a fake `Scratch` whose `lake build` prints Lake's error lines, so the errors go through `located`, `build` and `invalid`.

The mutated file is the M170 mutant. Its declaration is at lines 399-404, and the mutant's text is on line 401 at columns 15 to 95 (81 characters, end exclusive at 96). The test asserts these columns.

| case | errors (line 401, column) | verdict |
|---|---|---|
| M170-four-inside | `.str` ×4 at 26, 44, 61, 80 | INVALID |
| F2-outside-then-inside | `.str` at 4, then 26 | UNKNOWN |
| F2-inside-then-outside | `.str` at 26, then 4 | UNKNOWN |
| F2-inside-then-after-the-edit | `.str` at 26, then 96 | UNKNOWN |
| invalid-field-twice-inside | "Invalid field" at 16, 90 | INVALID |
| invalid-field-outside-then-inside | "Invalid field" at 4, then 16 | UNKNOWN |

Run: `VE_NATIVE_PREBUILT=1 uv run pytest -q tests/test_trust_mutants.py -k "each_copy_of_an_error or elaboration_error_in_the_mutants or needs_every_error or only_when_lean_refuses or read_with_its_whole_message"`.
- Before I fixed the test's own column assertion (see below), the output was `6 failed, 53 passed`. After it, the whole selection gives `59 passed, 753 deselected` (rerun by the self-reviewer on this code).
- The tm-elab-unknown 14-case test (`test_an_elaboration_error_in_the_mutants_own_text_is_invalid`) and the "Invalid field" cases (`test_invalid_only_when_lean_refuses_the_mutated_text`, `test_invalid_needs_every_error_of_the_mutated_declaration_to_be_a_refusal`) pass unchanged in the same run.
- The 6 early failures came from the test's own column assertion (81 characters, not 80), which I fixed. They were not product failures.

## Seeded bugs (Python; the only product language changed)

Each bug was planted in `tools/trust_mutants.py`, run with `-k each_copy_of_an_error`, then restored with `cp`. `git diff --stat` afterwards showed only the intended diff.

| # | bug | failing tests |
|---|---|---|
| 1 | Columns keyed by (file, line, message) again: `{(g, k, t): d for g, k, t, d in found}[(f, n, message)]` at the `invalid` call | `[F2-outside-then-inside]`, `[invalid-field-outside-then-inside]` (2 failed, 4 passed) |
| 2 | `build` drops the column (`(f, n, message, 0)`) | `[M170-four-inside]`, `[invalid-field-twice-inside]` (2 failed, 4 passed) |
| 3 | Every copy takes the first copy's column (`next(d for g, k, d, t in found if (g, k, t) == (f, n, message))`) | `[F2-inside-then-outside]`, `[F2-inside-then-after-the-edit]` (2 failed, 4 passed) |

## Reclass re-check (df-5, et-4b)

I ran `PATH=~/.elan/bin:$PATH uv run python -I docs/infra/tm-elab-unknown/reclass.py . <manage-agents>/reviews/tm-targeted/df-5-df-5-c050431.json <manage-agents>/reviews/tm-targeted/et-4b-et-4b-c050416.json` on this tree, after `lean-prep.sh`.

- Output: [reclass.txt](reclass.txt), 12 lines. `grep -c "UNKNOWN -> INVALID"` gives 12.
- Every error is inside its edit span. For example, M170 has edit columns 15-96 and errors at 401:26, 44, 61, 80. M034 has edit columns 46-48 and errors at 131:46 ×2.
- Compared with `docs/infra/tm-elab-unknown/reclass.txt`, only M034's line differs:
  - Earlier run: `Run.lean:127 (record line 131) edit cols 26-28; errors at 127:26, 127:26`.
  - Now: `Run.lean:131 (record line 131) edit cols 46-48; errors at 131:46, 131:46`.
  - The cause: `softCase` was rewritten on main since then, so the script now finds the occurrence of `before` nearest the record's line at the record's own line 131.
  - The verdict is still INVALID, with both copies at the edit's first column.
- The script calls `invalid` with each error's own column, so this confirms DRI adv0314 item 1's finding on the current tree.

## Trust and DELTA

- `uv run python tools/trust_map.py --check` exited 0: `against 7dbc43ed02ed: K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`, `PASS`.
- DELTA: none. This is a tool-only change to `tools/trust_mutants.py`'s classification of mutants, not to the VE product's verdicts, diagnostics or output. No DELTA rows, and no DRI signature is reserved.
- No Lean or Rust changed, so I ran no lake build, audit or trust mutants.
- No regen is needed:
  - `regen_generated.py --owner tools/trust_mutants.py` gives `-`, so the file is not generated.
  - `regen_generated.py --list | grep -c trust_mutants` gives 0, so no generator lists it.
  - The code map reads only module docstrings, and neither changed file's module docstring changed.

## Spec re-read

- "carry each located error's own column from `located(output)` to the `invalid(...)` call": checked against the task file, FIX paragraph. `build` returns the column, and the mutated branch passes it to `invalid`.
- "No change to KILLED / SURVIVOR judgement, to the barrier, to the refusal-table messages, or to any other class": checked against the same paragraph. The diff's hunks are all inside `run` (see Fix).
- TESTS (1)-(3) and the seeded bug: checked against the task file, TESTS paragraph.
  - (1) is `F2-outside-then-inside`, through `run`'s build.
  - (2) is `M170-four-inside` at 401:26, 44, 61, 80 with the edit at columns 15-96.
  - (3) is the 14-case and "Invalid field" tests, unmodified and passing.
  - The seeded bug is bug 1 above.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed route or schema changed.
2. Deliverables: PASS. The fix is in 66933f341; tests (1)-(3) are in `test_each_copy_of_an_error_is_read_at_its_own_column` plus the unmodified 14-case test; the reclass re-check is in reclass.txt; this is the REPORT. No Python copy of a Lean decision, and no permanent report test.
3. Tests can fail: PASS. Seeded bugs 1-3 above, each with its failing case ids.
4. Py/Lean/Rust agree: N.A. This is a tool-only change with no product path.
5. R8 binding: N.A. No relay field.
6. Gate evidence: N.A. for the builder. The chain gate runs on the final HEAD, and the branch is level with main (merge base 7dbc43ed0).
7. Unsigned items: PASS. There are no DELTA rows, and `trust_map.py --check` gives +0 (see Trust and DELTA).
8. User-visible change: N.A. It is a tool-only change (see Trust and DELTA).
9. Test selection: PASS. `select_tests.py --base 7dbc43ed0` selects `tests/test_trust_mutants.py` (172/555 units), the file that catches seeded bugs 1-3.
10. Lean statements: N.A. No Lean changed.
11. Budgets and deadlines: N.A. No budget path changed. The test uses no sleep and no timeout.
12. CPU and memory: N.A. Only the tuples change: one more int per error, and one dict less.
13. Test-removed trailers: N.A. No test was removed or renamed.
14. Both directions and cited evidence: PASS. Every refusal case in COPIES has its accepting twin: the outside-then-inside, inside-then-outside and after-the-edit cases (UNKNOWN) against four-inside and twice-inside (INVALID). Each claim here names its command.
15. Overclaim, silent cut, checks that fail, limits: PASS for the first three. "Every"/"only" claims cite the diff hunks and the self-reviewer's consumer check. No deliverable was cut. Each new case is caught by a seeded bug. Limits: N.A.

## Not run here

- The full gate: the chain runs it on the final HEAD.
- The selected-test run's result is recorded in the build report.
