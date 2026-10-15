# Repo map tests with untracked files

## Change and acceptance

| Item | Owner | Evidence |
| --- | --- | --- |
| The three coverage-map expectations use `tests.unmapped`, so they accept the static answer when an untracked file makes a recorded run uncertain. | AGENT | `f69533869`; `tests/test_repo_map.py::{test_a_map_answers_only_for_the_test_files_it_recorded,test_a_test_file_whose_run_may_have_changed_gets_the_static_answer,test_file_answers_for_a_file_the_map_never_saw}` |
| A regression creates an untracked file in a temporary Git repository, supplies Git's untracked status to the map, and executes those three checks. | AGENT | `f69533869`; `tests/test_repo_map.py::test_map_expectations_with_an_untracked_file` |
| Selected tests pass on the Mac runner. | AGENT | `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on `f69533869`: all selected units passed. |
| Full release gate on the committed final HEAD. | EXTERNAL | Deferred to the chain by the task directive; this build did not run `tools/gate.py`. |

The pre-fix Mac run with an untracked worktree file failed exactly the three named tests. The focused `tests/test_repo_map.py` run passed after the edit. The map and product code are unchanged. There are no user-visible deltas and no DRI signature is needed. No model calls were made.

## Seeded bugs

Each mutant restored one old fixed-set expectation in `tests/test_repo_map.py` in memory, against a real untracked file in a temporary Git repository. Each produced an `AssertionError` in the named test; the committed source retains the corrected expectation.

| Seed | File | Failing test |
| --- | --- | --- |
| Subtract `did_not` even when it is unmapped. | `tests/test_repo_map.py` | `test_a_map_answers_only_for_the_test_files_it_recorded` |
| Require the entire unmapped set to equal only `did_not`. | `tests/test_repo_map.py` | `test_a_test_file_whose_run_may_have_changed_gets_the_static_answer` |
| Subtract both recorded tests even when they are unmapped. | `tests/test_repo_map.py` | `test_file_answers_for_a_file_the_map_never_saw` |

## Self-review against BUILDER-CHECKLIST

1. N.A. — No Lean or Rust answer was changed.
2. PASS — `git diff main...HEAD` review: the task changes only repo-map test expectations and the regression.
3. PASS — The three seeded bugs above each failed its named test function.
4. N.A. — No parser, verdict, or cross-language implementation changed.
5. N.A. — No relay binding changed.
6. N.A. — The task assigns the final full gate to the chain; `git status --short` checks the local tree before handoff.
7. PASS — `git diff main...HEAD` shows no user-visible delta or trust-budget change.
8. PASS — `git diff main...HEAD` shows test-only changes; no product output changed.
9. PASS — `tools/select_tests.py --base $(git merge-base HEAD main)` includes `tests/test_repo_map.py`; the selected run passed.
10. N.A. — No Lean statement or proof changed.
11. N.A. — No budget, limit, or deadline changed.
12. N.A. — No product execution path changed.
