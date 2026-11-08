# eff-tm-headmoved build report

Status: code committed; targeted checks pass; the selected pass stopped early on a stale merge-record assertion, whose five failing cases pass after the fix.
HEAD: `infra/eff-tm-headmoved`, code commits `df0bd5b97` and `6579cf04a` (this report follows them).
Change: `--resume` and `--merge` accept finished parts from different commits when their saved inputs and plan are identical, and record both commit identities.
Open item: manage-agents caller change below is delegated; the selected runner left three units unrun after stopping early. No DRI signature is requested.

## Delivery and evidence

| Acceptance item | Owner | Delivery and evidence |
| --- | --- | --- |
| Carry a judged part after a docs-only commit | AGENT | `df0bd5b97`; `test_resume_carries_judged_verdicts_after_a_docs_only_commit` checks the two kept and four rerun verdicts, old and new commits, and `carried: inputs identical`. |
| Merge parts from both commits | AGENT | `df0bd5b97`; `test_merge_carries_parts_from_identical_inputs_at_different_commits` resumes a partial part after the commit and merges it with an older finished part. `shards[].head` names each source. The merged record uses the first part's `head`. |
| Changed Lean input, selected test, or plan reruns | AGENT | `df0bd5b97`; three parameters of `test_resume_reruns_judged_verdicts_when_an_input_or_plan_changes` each assert six mutants run and zero are kept. Existing `test_any_changed_input_but_checks_gives_a_full_run` exercises the real `inputs()` digest function. |
| Keep mutation barrier and verdict rules | AGENT | `git diff main...HEAD -- tools/trust_mutants.py` shows changes to resume and merge identity checks, provenance, help text, and the partial message; `run`, `settle`, `judge`, and the KILLED/SURVIVOR rules are outside the diff. `git diff --check main...HEAD` exited 0. |
| Caller fallback after HEAD moves | EXTERNAL | Delegated to manage-agents, exact edit below. This repository change alone does not remove the caller's early exit. |
| Recovered verdicts and avoided rerun hours | EXTERNAL | **To be measured on the next 3 sweeps**; no estimate is made here. Owner: infra feed after the caller change is applied. |

The targeted command `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/test_trust_mutants.py -k 'merge_carries_parts_from_identical_inputs_at_different_commits or resume_carries_judged or resume_reruns_judged or resume_of_another_heads_or_unbound or merge_refuses_a_part_whose_tree_or_resume'` reported `29 passed, 740 deselected` (`/tmp/eff-tm-target5.log`). The earlier malformed-merge focused run reported `61 passed, 708 deselected` (`/tmp/eff-tm-target4.log`).

The required selected command `zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` ran on the VM and stopped at five cases of `test_the_parts_merged_are_the_one_runs_record` because their expected `shards` dictionaries lacked the new `head` field (`/tmp/eff-tm-selected.log`, lines 59–143). It reported `STOPPED EARLY (--maxfail 5)` and did not run the remaining units `tests/test_trust_mutants.py`, `tests/test_trust_mutants_probe_scope.py`, and `tools/test_layer_policy.py`. Commit `6579cf04a` updates that assertion. The specified Mac retry of exactly the five failed IDs reported `5 passed in 0.83s`, exit 0 (`/tmp/eff-tm-failed-ids.log`, lines 25–26). The chain will run the full gate on the final committed HEAD; this builder did not run it, as instructed.

`uv run python tools/repo_map.py file tools/trust_mutants.py` reported `generator: -` and layer 4 (tools). No Lean or Rust product code changed, so Lean build, `lean/audit.py`, generated-file regeneration, and a trust-mutant sweep do not apply. `df -h .` reported 83G free. `rg` over `main-known-red.txt` found no related known-red test.

## Caller delegate: manage-agents/mac-pytest.sh

In `tmparts()`, remove the early equality exit at line 255 that compares current `git rev-parse HEAD` with `vm_head`. Keep the `wt-snapshot.sh` call at lines 265–266 as a successful-snapshot check, but remove its `o[1] == vm_head` early exit. Continue pinning the cloud parent base through `pa+=(--base $vb)`. Run missing or partial parts at the current checkout; `trust_mutants --resume` checks the saved plan, all input digests, and selected tests, and `--merge` refuses parts whose inputs or plans differ. If snapshot creation fails, retain a fallback to the full sweep. Update the caller's header comments at lines 92–104, which still say moved HEAD is never resumable. This exact caller change is outside this VE item.

## Delta and ruling

VE product delta: none. The CLI record and acceptance behavior of this developer tool change as follows.

| Tool delta | Test | Ruling |
| --- | --- | --- |
| A moved HEAD with identical saved inputs and plan now carries judged verdicts; `resumed.carried` says `inputs identical`. | `test_resume_carries_judged_verdicts_after_a_docs_only_commit`; changed-input and changed-plan parameters of `test_resume_reruns_judged_verdicts_when_an_input_or_plan_changes` | SIGNED by DRI (`/home/seyran/code/manage-agents/reviews/dri-decisions-20261108-lp0531.md`, item 3; bounded task in `lp1201.md`, item 3). |
| `--merge` accepts those mixed-commit parts and records every source commit in `shards[].head`, with `carried: inputs identical` for a part whose HEAD differs from the first part. | `test_merge_carries_parts_from_identical_inputs_at_different_commits`; `test_merge_refuses_parts_that_are_not_one_runs` | SIGNED by DRI (`/home/seyran/code/manage-agents/reviews/dri-decisions-20261108-lp0531.md`, item 3; bounded task in `lp1201.md`, item 3). |

Spec re-read: the plan and Lean/test input identity rule against `prompts/task-eff-tm-headmoved.txt` lines 1–4 and `reviews/dri-decisions-20261108-lp0531.md` item 3; provenance wording against the task's `carried: inputs identical` requirement. The former same-HEAD refusal cases were removed from the parametrized tests because the new accepted behavior has explicit positive tests.

## Seeded bugs

Each temporary Python product-code mutation was made in `tools/trust_mutants.py`, run against one named test, and restored before commit:

1. Restore the old HEAD equality guard: `test_resume_carries_judged_verdicts_after_a_docs_only_commit` failed (`/tmp/eff-tm-seed1.log`, line 48).
2. Skip the selected-test digest in the `inputs` comparison: `test_resume_reruns_judged_verdicts_when_an_input_or_plan_changes[test]` failed (`/tmp/eff-tm-seed2.log`, line 41).
3. Require equal heads in `AGREED`: `test_merge_carries_parts_from_identical_inputs_at_different_commits` failed (`/tmp/eff-tm-seed3.log`, line 47).
4. Omit the mutant's `after` from `PLANNED`: `test_resume_reruns_judged_verdicts_when_an_input_or_plan_changes[plan]` failed (`/tmp/eff-tm-seed4.log`, line 41).
5. Skip the Lean input digest in the `inputs` comparison: `test_resume_reruns_judged_verdicts_when_an_input_or_plan_changes[lean]` failed (`/tmp/eff-tm-seed5.log`, line 41).

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean response or request decoder changed.
2. PASS — acceptance table above; `git diff --stat main...HEAD` lists the tool and its tests.
3. PASS — five seeded failures listed above; `test_merge_refuses_parts_that_are_not_one_runs` keeps the opposite refusal path.
4. N.A. — no Python/Lean/Rust product comparison route changed.
5. N.A. — no relayed Lean answer or R8 binding changed.
6. PASS — `git log main..HEAD --no-merges --oneline` names the two code commits; the chain owns the final-HEAD gate under this task's explicit instruction.
7. PASS — the tool delta table cites the item-specific DRI decision; changed-input tests show the refusal side.
8. PASS — the tool delta table records both CLI behavior changes; no VE product route changed (`repo_map.py file tools/trust_mutants.py`).
9. PASS — the selected runner selected `tests/test_trust_mutants.py`; `/tmp/eff-tm-selected.log` line 142 records the early stop.
10. N.A. — no Lean theorem or source statement changed.
11. N.A. — no budget, deadline, or limit logic changed; `test_a_deadline_stops_new_mutants_and_lists_the_rest_unjudged` remains in the existing suite.
12. N.A. — no VE check/render path changed; avoided rerun hours are deferred to three measured sweeps.
13. PASS — removed parameter IDs receive `Test-removed` trailers in this branch's commit history; `git diff --check main...HEAD` exited 0.
14. PASS — opposite directions are the docs-only carry and changed-input/plan reruns; command outputs and spec re-read are above.
15. PASS — overclaim: this report marks caller work and measurements deferred; silent cut: acceptance table names both; checks can fail: five seeds above; limits charged before work: N.A. (limit logic unchanged).
