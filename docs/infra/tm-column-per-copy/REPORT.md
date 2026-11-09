# tm-column-per-copy: each copy of an error is judged at its own column

**Summary.**
- Status: built, waiting for the chain gate. HEAD: the commit that adds this report on `infra/tm-column-per-copy` (`git log -1`; the code commit is 66933f341).
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
- Every path now keeps the copies apart, so the task's fallback for an ambiguous key is not needed.
- Unchanged: the KILLED / SURVIVOR judgement, the barrier, the refusal-table messages, `invalid` and `refused`.

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
- Before the column fix to the test (see below), the output was `6 failed, 53 passed`. After it: `6 passed` for the new test.
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
- Compared with `docs/infra/tm-elab-unknown/reclass.txt`, the only difference is M034's line: 131 instead of 127, because `VE/NormDefaults/Run.lean` moved on main since then. Its verdict is the same.
- The script calls `invalid` with each error's own column, so this confirms DRI adv0314 item 1's finding on the current tree.

## Trust and DELTA

- `uv run python tools/trust_map.py --check` exited 0: `against 7dbc43ed02ed: K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`, `PASS`.
- DELTA: none. This is a tool-only change to `tools/trust_mutants.py`'s classification of mutants, not to the VE product's verdicts, diagnostics or output. No DELTA rows, and no DRI signature is reserved.
- No Lean or Rust changed, so I ran no lake build, audit or trust mutants. No generated file has these files as input: `regen_generated.py --owner tools/trust_mutants.py` gives `-`, and the module docstring is unchanged.

## Not run here

- The full gate: the chain runs it on the final HEAD.
- The selected-test run's result is recorded in the build report.
