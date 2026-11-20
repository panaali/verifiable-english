# tm-nightly-unknown-disposition-3: build report (VE branch infra/tm-nightly-unknown-disposition-3)

Main report, per-id table, the decider's question and the install read:
/home/seyran/code/manage-agents/reviews/tm-nightly-unknown-disposition-3.md.
Decision: reviews/dri-decisions-20261120-tm-build-timeout-1120.md item 3. No DELTA row, no signature and no Lean change.

## The five ids (record test-skip/nightly/20261119T0727Z.json, head 9ccbf3fdf)
| id | disposition | evidence |
|---|---|---|
| M954 | (2) INVALID: a ctor-drop refusal of a constructor the edit removed, in the mutant's own file (tm-nightly.py `dropped_ctor`, staged in manage-agents) | manage-agents tools-local/test_tm_nightly_unknown_disposition_3.py(.new-ud3); copy in evidence/test_tm_nightly_unknown_disposition_3.py.staged |
| M2397 | (2)/(1) the tool misread fixed here (`targets`); with it the mutant is KILLED at 9ccbf3fdf | evidence/m2397-9ccbf3fdf.json, evidence/m2397-run.log |
| M465, M1082, M1423 | (3) allow through ci-3a's next item (re-run its record at a head that contains ci-3 F1 dc360e738b; the allow pair and its reason are already in ci-3a's file): for the decider | manage-agents report, "Disposition per id" |

## The change here
In tools/trust_mutants.py, `targets` now also returns each module of the mutated module's cone that holds a check and that a chosen target imports, however indirectly. Lake builds such a module with the mutant before the target that imports it, so adding it as a target leaves the set of compiled modules the same. Being a target puts it in `checked`, so it gets a control in both modes (lazy `ControlProbes`, eager `hashes`). Before, it had no control, and its failing check read "Lean could not elaborate it in the probe" (eff-20261108-1 F1).

The verdict rule (`settle`, `refusal`) is unchanged: a kill still needs each error to be a check's own refutation with a control that passes.

Evidence: M2397 at 9ccbf3fdf.
- With the fix (scratch commit 4884052810 = 9ccbf3fdf plus this tools/trust_mutants.py): KILLED at `lean/VE/Acts/DecodeExamples.lean:79`, 4,059 s, `--jobs 2 --build-timeout 3600`, the nightly part 7's 52 --test paths.
- The nightly's own run (tool at 9ccbf3fdf): UNKNOWN at ActsExamples.lean:79.

## Tests
- `test_a_check_module_of_the_cone_a_target_imports_is_a_target` (new, a stub tree). Mid, imported by the --test module through a module with no check, is a target. A module no target imports, one with no check and one outside the cone are not. With no tests the result is as before, and with --deep each cone check module is a target.
- `test_probe_f1_a_check_module_a_target_imports_is_judged_alike_in_both_modes` (real Lean). This renames `test_probe_f1_a_check_module_outside_the_targets_gives_lazy_the_eager_verdicts` and has a Test-removed trailer in 8cd66c9d1b. Lazy still gives eager's rows, and Far/Mid's failing `#guard` is now judged KILLED. The old code asserted UNKNOWN "could not elaborate".
- Runs:
  - the selected run on ve-cloud-2: exit 0, 0 failed. tests/test_trust_mutants.py ran 814 passed and tests/test_trust_mutants_probe_scope.py exit 0 (`mac-pytest.sh --select -- --base 09bea0972d --run`).
  - tests/test_trust_mutants_max_errors.py: 9 passed (`uv run pytest -q`).
  - `tools/gate_collection.py --check --prebuilt`: exit 0, 0 refused, 0 stale, 0 malformed.
  - `tools/regen_generated.py --check`: exit 0.

## Seeded bugs (seeded-bugs.json)
- B1 tools/trust_mutants.py: `targets` returns `chosen` only. Fails test_a_check_module_of_the_cone_a_target_imports_is_a_target and test_probe_f1_a_check_module_a_target_imports_is_judged_alike_in_both_modes (2 failed).
- B2 tools/trust_mutants.py: returns `chosen | reached`, so a module with no check is added. Fails test_a_check_module_of_the_cone_a_target_imports_is_a_target.
- B3 tools/trust_mutants.py: the walk starts from the whole cone, so a module no target imports is added. Fails test_a_check_module_of_the_cone_a_target_imports_is_a_target.
- B4-B6 are in manage-agents tm-nightly.py.new-ud3 `dropped_ctor`. Each fails test_b_other_refusals_of_a_ctor_drop_stay_unknown.

Each was restored afterwards; `git status` was clean after the run.

SIZE: 47 product (tools/trust_mutants.py +23/-5; manage-agents tm-nightly.py +19), 181 tests (39 + 142), about 300 other hand-written lines.

LIGHT lane: `light-lane.py check` printed LIGHT (67 changed lines, no trusted-core file), so no trust_mutants sweep was run. No Lean changed.

## Notes
- Sibling lesson F1 (-2 review): a guard path without a test. Here every branch of the new walk has a case in the stub test (reached, a module with no check, a module no target imports, outside the cone, --deep).

## Self-review against BUILDER-CHECKLIST
1. N.A.: no relayed Lean answer and no response schema changed.
2. PASS: each of the five ids has a disposition with evidence (manage-agents report table; test_c_the_record_counts_the_five_disposed_only_with_each_disposition).
3. PASS: tests can fail. Seeded bugs B1-B6 (seeded-bugs.json); the new manage-agents test fails on the installed tm-nightly.py (a, c).
4. N.A.: no Python/Lean/Rust behaviour pair changed (a tool and a nightly script only).
5. N.A.: no R8 binding.
6. PASS: the chain runs the gate on the final HEAD. The selected run and gate_collection were run on this branch's code (the last commits are docs and an empty trailer commit).
7. PASS: no unsigned item; no DELTA row is needed (no user-visible change).
8. N.A.: no user-visible change (a sweep tool and a nightly classifier).
9. PASS: the selected run picked tests/test_trust_mutants_probe_scope.py and tests/test_trust_mutants.py ("changed ['tests/test_trust_mutants_probe_scope.py']", /tmp/ud3-select.log).
10. N.A.: no Lean statement or proof.
11. PASS: budgets are unchanged; a control can now be computed for one more file, with no new timeout (the run's --build-timeout stays the limit). test_probe_f1_a_check_module_a_target_imports_is_judged_alike_in_both_modes.
12. PASS: no extra build. The added targets are modules Lake already builds as imports of a target. M2397's run: mutant_builds 11.4 s, mutant_checks 1,941 s at --jobs 2 (evidence/m2397-run.log).
13. PASS: Test-removed trailer for the renamed F1 test (commit 8cd66c9d1b); gate_collection --check --prebuilt exit 0.
14. PASS, both directions. Accept: M954, and Mid as a target. Refuse: N1-N6, and Lone / Plain / Side. Every claim above names its command or log.
    - Spec re-read: decision item 3 and the task's DO (1)-(3) against reviews/dri-decisions-20261120-tm-build-timeout-1120.md:23-26 and the task prompt's DO (2) ("an error in another file stays UNKNOWN": dropped_ctor reads the own file only, N1).
15. PASS:
    - No overclaim: M465/M1082/M1423 are written as pending ci-3a's next item, and the 9ccbf3fdf completion as a decider question.
    - No silent cut.
    - Each new check has a seeded bug.
    - No limit is involved.
