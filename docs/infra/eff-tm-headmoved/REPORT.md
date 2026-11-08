# eff-tm-headmoved build report

Status: review fix round committed (F1, F2, F-ready1 fixed); see "Fix round" for the selected tests and probes.
HEAD: `infra/eff-tm-headmoved`, code commits `df0bd5b97`, `6579cf04a`, fix commits `ce4e8a71b` and `deafe590f` (this report follows them).
Change: `--resume` and `--merge` accept finished parts from different commits when their saved inputs and plan are identical, and record both commit identities.
Open item: the manage-agents caller change below is delegated; review follow-ups C1, C2, C3 and C4 are not done. No DRI signature is requested.

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

`UV_CACHE_DIR=/tmp/uv-cache uv run python tools/gate_collection.py --check --prebuilt` reported `7 added, 4 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers` (`/tmp/eff-tm-collection2.log`). The three trailers missing from the first collection check were added in `b62378d4c` as one contiguous commit-message block.

## Fix round (review of `9444e5104`)

| Finding | Fix | Regression test | Commit |
| --- | --- | --- | --- |
| F1 (B) the `resumed.carried` rule was untested, and it masked seven type cases | Each `RESUMED_PARTS` case is now one fault of a base that `sweep` writes (the part's own head, or a moved head with `carried`). A control test shows each base merges. Five `carried` cases were added: wrong value, retyped, moved head with no `carried`, `carried` at the same head, and `carried` on an ignored resume. The wording has one owner, `CARRIED` in `tools/trust_mutants.py`. | `test_merge_refuses_a_part_whose_tree_or_resume_is_not_written_by_this_tool[resumed-*]`, `test_a_part_resumed_at_its_head_or_carried_merges[own-head, moved-carried, ignored]` | `ce4e8a71b` |
| F2 (A) `docs/TESTING.md` said `--resume` needs the same HEAD | The `--resume` sentence now states the cross-commit rule and `carried`. The sweep found no other current document that makes the claim: the dated batch evidence under `docs/infra/` stays as recorded. | `test_the_testing_guide_states_resume_as_the_tool_does` (fails on the old guide) | `deafe590f` |
| F-ready1 (B) no committed seeded bug named the changed Python file | The `docs/infra/eff-tm-headmoved/seeded-mutants.json` record lists S1–S5 from the build round and S6–S9 from this round, all in `tools/trust_mutants.py`. | review-ready `[mutants]` | this report's commit |

Probes: before the fix, probe F1 printed `mutant A survives` (rc 1) and probe F2 exited 1. After the fix, both exit 0. Under mutant A, 8 `RESUMED_PARTS` cases fail, as at the merge base. Under mutant B, the 4 `carried`-rule cases fail.

Done from the follow-ups: the `--resume` docstring sentence now has its verb, and the caller's line numbers are corrected (below). Not done (C, follow-up): C1, `--merge` does not compare `tree` for same-head parts. C2, the merged `head` comes from part 1. C3, no test runs the real digest across a real docs-only commit. C4, the stale name `test_a_resume_of_another_heads_or_unbound_record_is_ignored` is kept, because renaming it would remove collected IDs.

## Caller delegate: manage-agents/mac-pytest.sh

In `tmparts()`, remove the early equality exit at line 262 that compares current `git rev-parse HEAD` with `vm_head`. Keep the `wt-snapshot.sh` call at lines 272–273 as a successful-snapshot check, but remove its `o[1] == vm_head` early exit. Continue pinning the cloud parent base through `pa+=(--base $vb)`. Run missing or partial parts at the current checkout; `trust_mutants --resume` checks the saved plan, all input digests, and selected tests, and `--merge` refuses parts whose inputs or plans differ. If snapshot creation fails, retain a fallback to the full sweep. Update the caller's header comments at lines 92–104, which still say moved HEAD is never resumable. `tm-shard.sh merge` runs the tool from `git archive $vh`, so `vm_head` must contain this change before the caller relies on a cross-commit merge. This exact caller change is outside this VE item.

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
3. PASS after the fix round (review F1 found it did not hold: the new `resumed.carried` rule could be deleted with no test failing, and it masked seven `RESUMED_PARTS` type cases). `docs/infra/eff-tm-headmoved/seeded-mutants.json` lists nine seeded failures, S6 and S7 being that rule and that type check.
4. N.A. — no Python/Lean/Rust product comparison route changed.
5. N.A. — no relayed Lean answer or R8 binding changed.
6. PASS — `git log main..HEAD --no-merges --oneline` names the two code commits; the chain owns the final-HEAD gate under this task's explicit instruction.
7. PASS — the tool delta table cites the item-specific DRI decision; changed-input tests show the refusal side.
8. PASS — the tool delta table records both CLI behavior changes; no VE product route changed (`repo_map.py file tools/trust_mutants.py`).
9. PASS — the selected runner selected `tests/test_trust_mutants.py`; `/tmp/eff-tm-selected.log` line 142 records the early stop.
10. N.A. — no Lean theorem or source statement changed.
11. N.A. — no budget, deadline, or limit logic changed; `test_a_deadline_stops_new_mutants_and_lists_the_rest_unjudged` remains in the existing suite.
12. N.A. — no VE check/render path changed; avoided rerun hours are deferred to three measured sweeps.
13. PASS — removed parameter IDs receive `Test-removed` trailers; `gate_collection.py --check --prebuilt` reported `0 refused, 0 stale and 0 malformed`.
14. PASS — opposite directions are the docs-only carry and changed-input/plan reruns; command outputs and spec re-read are above.
15. PASS — overclaim: this report marks caller work and measurements deferred; silent cut: acceptance table names both; checks can fail: five seeds above; limits charged before work: N.A. (limit logic unchanged).
