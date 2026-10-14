# fix-subtick build report

Task: DRI 2026-10-14 12:00Z, infra item fix-subtick. Base `dccd9cf5a`; code commits
`975790653` and `d2bc9eb59`.

## Change and evidence

`tests/test_lean_service.py::test_the_sub_tick_deadline_tests_hold_on_a_fast_machine_and_need_the_response_check`
now calls the two named deadline tests in the current pytest process. Each call gets an isolated patch
that freezes the service CPU reading at zero. In the `response unchecked` case, the patch also removes
the response wait's CPU deadline check. The wrapper records each test's `DID NOT RAISE
CheckerUnavailable` failure and requires that **both** named tests fail; in the checked case both must
pass. This preserves the original probe and avoids a child pytest session contending for the native
build lock while the outer session holds its read lock. The old child timed out at `HANG_TIMEOUT` on
the loaded VM.

Focused verification on the restored code:

- VM, `VE_NATIVE_PREBUILT=1`, with the repository's `conftest.py`: both parametrisations passed in
  2.84 s (4.37 s including process startup), under the 60 s target. On final code, both cases and
  the hang-guard lint passed together (3 passed in 18.40 s). An earlier run with
  `--noconftest` and equivalent hang-guard environment passed in 4.62 s while an unrelated process
  held this worktree's native build write lock; the normal-fixture run supersedes it.
- Mac aarch64, via `mac-pytest.sh`, with the repository's `conftest.py`: both parametrisations passed
  in 0.59 s before the lint-only follow-up. On final code, both parametrisations and
  `test_no_short_wait_outside_the_reviewed_allowlist` passed together (3 passed in 2.91 s).
- The selected test plan is `70/373` units for `tests/test_lean_service.py`; all 70 units exited 0
  on the final code, including `test_hang_guards.py`, `test_lean_service.py`,
  `test_relay_mutation_gate.py`, and `test_wire_gate_corpus.py`.

## Seeded bugs (all restored)

All three temporary changes were planted in `tests/test_lean_service.py` and checked on the Mac:

1. Simulated CPU reading `None` instead of `0.0`: the `[checked]` wrapper failed at the question
   test's `DID NOT RAISE CheckerUnavailable` assertion.
2. Reversed `if unchecked` to `if not unchecked`: both wrapper parametrisations failed because
   their observed outcomes were opposite the independently asserted expectations. This seed first
   survived an earlier wrapper arrangement; the final outcome assertion was moved outside the
   branch before repeating it.
3. Called the question deadline test twice instead of calling the document deadline test second:
   `[response unchecked]` failed on the required ordered names of the two failing tests.

No product code changed in Lean, Python, or Rust, so no per-product-language seed is applicable.

## Scope, rulings, and acceptance

Only a test harness changed. No verdict, diagnostic, response shape, request binding, limit, CPU
budget, user-facing wording, or other user-visible record changed. DELTA: none. No standing ruling
signature or DRI signature is needed. No generated file or report evidence test was added.

- **AGENT:** preserve both original assertions and both named deadline tests: code commit
  `975790653`; focused VM and Mac tests above. Commit `d2bc9eb59` keeps the assertion clear of the
  repository's time-assertion lint, which passes on final code.
- **AGENT:** make the check cheap and load-independent: direct calls, isolated patches, and measured
  VM test body under 60 s.
- **AGENT:** run selected tests, Mac focused tests, and three seeded bugs: evidence above and below.
- **AGENT:** commit all changes, review `main...HEAD`, and leave a clean tree: final checks below.
- **EXTERNAL:** full release gate on committed final HEAD: deferred to the chain test runner by the
  task's explicit override of build checklist item 22. This report does not claim a full-gate pass.

The sibling review lesson about detached or overlapping gates was followed: commands were supervised
in the foreground. The selected run executed on the VM through `mac-pytest.sh` after the Mac slots
remained occupied; no full gate was run here.

## Selected tests and final checks

`select_tests.py --base $(git merge-base HEAD main) --run` selected 70 units. On the final code,
every unit reported exit 0. The command itself then exited 1 solely because it tried to write its
coverage map to the sandbox's read-only default path
`/home/seyran/.cache/ve-testmap/tree-….json.gz.tmp`. The per-unit results are in
`/tmp/ve-select-run-57i00chl/`; no selected test failed. The earlier selected iteration found the
`test_hang_guards.py` lint failure, which commit `d2bc9eb59` fixed; its final unit exited 0.
The full release gate was not run here, per the task's override; the chain runs it on final HEAD.

Final checks: `git diff --check` passed; free disk was 40 GiB. The final diff and clean tree were
reviewed after this report was committed.

## Self-review against BUILDER-CHECKLIST

1. N.A. No Lean or Rust response path changed.
2. PASS — `git diff main...HEAD -- tests/test_lean_service.py`; only the requested test and report changed.
3. PASS — three seeded bug runs listed above, each failed at the intended assertion.
4. N.A. No parser, fixture meaning, or product output changed.
5. N.A. No relayed answer or binding code changed.
6. N.A. Full gate is assigned to the chain test runner by this task's explicit override.
7. PASS — DELTA is empty by the test-only diff; `git diff main...HEAD` review.
8. PASS — no user-visible output changed; `git diff main...HEAD` review.
9. PASS — `tools/select_tests.py --base $(git merge-base HEAD main) --run` selected
   `tests/test_lean_service.py` and 69 related test units; all 70 unit results were exit 0.
10. N.A. No Lean theorem, statement, or shape changed.
11. PASS — focused two-parametrisation probe and
    `test_no_short_wait_outside_the_reviewed_allowlist` on VM and Mac; no fixed waits or sleep added.
12. PASS — VM focused probe measured 4.37 s total; Mac test body 0.59 s.
