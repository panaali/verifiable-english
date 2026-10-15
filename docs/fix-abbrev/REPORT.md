# fix-abbrev: report

Infra item fix-abbrev (DRI 2026-10-13 19:15Z; main is red). Branch `fix/abbrev`, base `f98183bf5` (main).

DRI signature needed: none. The change is test code only; there is no user-visible delta, so DELTA.md is not
needed and no standing ruling is claimed.

## The fault

`tests/test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target` listed the
commit chain with `git log --format=%h`. `%h` is git's automatic abbreviation, whose length grows with the number
of objects in the repository; it is now nine digits here (`git log -1 --format=%h` prints `f98183bf5`), while
`docs/readings-defaults/rd8/evidence.json` saves eight-digit hashes. Every row then differed
(`"c3d869950\t..." != "c3d86995\t..."`).

## The fix (commit `506d62fed`)

- The test reads full hashes (`--format=%H`) and cuts them to `ABBREV = 8`, a module constant: the fixed length
  the saved evidence uses. The comparison no longer depends on git's abbreviation setting or repository size.
- `test_the_evidence_is_complete` checks every saved hash against the same `ABBREV`, now including
  `review_fix_commits` (which the chain test compares but the shape check did not cover), so the two sides
  share one length.
- The saved evidence is unchanged.

## Sweep for the same dependency

Searched `tools/`, `tests/`, `ve/` (and `docs/**/*.py`) for `%h`, `%p`, `%t`, `--oneline`, `--abbrev`,
`--abbrev-commit`, `core.abbrev`, `--short`, `describe` and fixed slices `[:7]`..`[:12]`:

- `%h` / `--oneline` / `--abbrev-commit` / `describe`: only the RD-8 test (fixed).
- `tools/select_tests_evidence.py:81` `rev-parse --short=10`, `docs/lean-first/b6/udhr_timing.py:93-94`
  `rev-parse --short=8`: explicit lengths that only write evidence; no test compares them against git's
  automatic length. Left as they are.
- Every other `[:8]`/`[:10]`/`[:12]` slices a full saved or computed hash, which is already a fixed explicit length.

## Seeded bugs (each made a test fail, then was removed with `git checkout`)

Only Python test code changed (no Lean, Rust or Python product code), so all three are in the changed file
`tests/test_readings_defaults_rd8_report.py`.

| Id | Behaviour | Mutation | Failing test |
|---|---|---|---|
| M1 | The chain does not depend on git's automatic abbreviation | the original code: `--format=%h`, no cut | `test_review_fix_commit_chain_and_final_gate_target` (`"c3d869950\t..." != "c3d86995\t..."`) |
| M2 | Hashes are cut to the saved length | `sha[:ABBREV + 1]` | `test_review_fix_commit_chain_and_final_gate_target` |
| M3 | One length is used on both sides | `ABBREV = 9` | `test_the_evidence_is_complete` and `test_review_fix_commit_chain_and_final_gate_target` |

A first M1 (`%h` with the cut kept) survived: cutting a nine-digit `%h` to eight digits is also correct. It was
replaced with the original code, which fails.

## Tests run

- `tests/test_readings_defaults_rd8_report.py`: 9 passed.
- Selected tests (`tools/select_tests.py --base $(git merge-base HEAD main) --run`, 93/373 units), at load
  average 60–100: 92 units passed; two timed out: `tests/test_difffuzz.py::test_ci_run`
  (`subprocess.TimeoutExpired`; the unit runs quarantined) and `tests/test_english_evidence.py` (unit exit
  timeout). Neither reads the changed file. Rerun alone
  (`pytest tests/test_english_evidence.py tests/test_difffuzz.py::test_ci_run`): 68 passed, 0 failed.
- This report adds four units to the selection (97/373): `tests/test_ar3_report.py`,
  `tests/test_b15a_evidence.py`, `tests/test_b15b_evidence.py`, `tests/test_lean_first_b13b.py`: 63 passed.
- The chain's first full gate on `3329bd415` failed in the agent-policy rerun fixture: the Lean `norms`
  service exceeded its 5.53893 s CPU deadline under a host load near 100. The three failures all came
  from that one fixture; they did not exercise the changed RD-8 test. The failed gate result named
  that commit SHA before subsequent gate runs replaced it.
- Retried the failed file directly with a writable uv cache:
  `UV_CACHE_DIR=/tmp/ve-fix-abbrev-uvcache uv run --frozen --no-sync pytest -q tests/test_agent_policy_rerun.py`;
  3 passed in 12m48s, including Lean certificate replay. No product or test code was changed for this
  resource-sensitive failure.
- The full gate is run after this report commit, on its clean final HEAD; its result is `gate-result.json`.
- A local full-gate attempt on `f95769e9f` used one pytest worker. Lean build and audit and Rust build
  and tests passed; Python collection found 15,081 tests. The Python suite advanced past the original
  failing agent-policy fixture, but after roughly six hours its `/tmp/ve-gate-*` scratch directory had
  disappeared while `gate-result.json` still held only the startup placeholder (empty commit and
  stages). The attached process was stopped with Ctrl-C (exit 130); this is not passing gate evidence.
  The final-HEAD gate uses four pytest workers to reduce suite wall time.
- The full gate on `082304d5f` completed with one failure:
  `tests/test_readings_rd6b_differential.py::test_generated_documents_agree_on_both_routes[2]`
  exceeded the Lean `check` service's 5.13438 s CPU deadline under heavy host load. Its other stages
  passed (Lean build and audit, Rust build and 36 Rust tests); pytest recorded 14,988 passed, 92 skipped,
  and one failed. The foreground `tools/gate.py --rerun-failed --workers 1` then selected that file and
  passed all 11 tests in 22m01s, including case `[2]`. No code was changed for this intermittent deadline.

## Self-review against BUILDER-CHECKLIST

1. N.A. — no relayed Lean answer is read or changed.
2. PASS — the task's three asks (test independent of abbreviation; other producers/comparers searched; saved
   evidence unchanged) are delivered by `506d62fed`, checked by
   `tests/test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target`; no new
   report test, no Lean decision copied.
3. PASS — seeded bugs M1–M3 above, each failing a named test.
4. N.A. — no checker behaviour changed.
5. N.A. — no relayed field read.
6. PASS — `gate-result.json` records the final committed HEAD after the gate run; the earlier failed
   gate on `3329bd415` and its direct test rerun are recorded above.
7. PASS — no DELTA row and no trust-budget growth; nothing to sign.
8. PASS — no user-visible output changed (test-only diff: `git diff main...HEAD --stat`).
9. PASS — `tools/select_tests.py --base $(git merge-base HEAD main)` selects 97/373 units (93 before the report) including
   `tests/test_readings_defaults_rd8_report.py`, the test the seeded bugs fail.
10. N.A. — no Lean statement or proof changed.
11. N.A. — no budget, limit or deadline touched; no sleep added (`tests/test_hang_guards.py` selected).
12. N.A. — no product code path changed.
