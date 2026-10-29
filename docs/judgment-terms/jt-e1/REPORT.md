# JT-E1 build report

Status: **PASS** on both pre-registered proxy-readability bars; 80/80 reader calls completed.
HEAD: `feature/jt-e1`, the commit containing this report (no push).
Changed: pre-registration, frozen 40-item frame, bounded runner, local tests, raw answers and results; no product code.
Open items: JT-3 may use the result; no DRI signature is reserved.
Model calls: `SIGNED by the DRI 2026-10-28 (prompts/dri-task-lp2001.txt item 5; recorded in reviews/lp-answers-20261028T2001.md item 5)`.

## Gate and scope

Plan: `docs/spec/judgment-terms-PLAN.md` at `32ffc3ec9`, sections 0.2, 2.4, 4.2 and 6 JT-E1; spec `docs/spec/judgment-terms.md`. The statement review's FIX was applied and its corrected statements re-elaborated in the plan/spec change logs. No theorem statement was added or changed. JT-2 and jt-2b are on main; JT-3 has not started. The DRI's item-5 decision authorises this model experiment within the picker caps. SYNTHESIS 4.2/4.3 and DRI-DECISIONS-PHASE2 impose no shared-file edit on this docs-only experiment.

The hand-written files touched are `PRE-REGISTRATION.md`, `items.tsv`, `runner.py`, `RESULTS.md`, this report and `tests/test_jt_e1.py`; `raw/` is call evidence. An overlap check of `main...branch` against 238 in-flight branch refs found no touched-file overlap. No `ve/`, `lean/`, or `rust/` file changed. QT-B4 is not on main: the hard-constraint items use the current form, a deviation recorded in the pre-registration before the first call. The synthetic identifier-shaped future answer lines are an experimental context, not a live JT-4 route; RESULTS states this limitation.

## Plan rows and evidence

| Plan row / directive | Delivery | Evidence |
|---|---|---|
| 40 items: 20 UDHR, 20 constitution, named units and synthetic variants | yes | `items.tsv`; `test_frozen_frame_and_two_arm_rendering` |
| Two arms from the same answer, expected class and decider, prompt and bars frozen before calls | yes | pre-registration commit `959b5205e`; `test_frozen_frame_and_two_arm_rendering` |
| QT-B4 deviation recorded before calls | yes | `PRE-REGISTRATION.md` in `959b5205e` |
| Sonnet 5.5, one separate subscription call per item/arm, human-visible context only | yes | 80 `raw/*.json`; model and fallback-credit probe in `RESULTS.md` |
| At most 100 calls and 3M CW; stop at caps | yes | 80 calls, 205,437 CW; `test_call_and_context_caps` |
| Correct / 40, difference, critical list and bar verdicts | yes | `RESULTS.md`; 16/40 vs 37/40, +52.5 points, no critical cases |
| Count items lacking a lint-accepted template | yes | 20/40 in the frozen synthetic frame; `test_frozen_frame_and_two_arm_rendering` |
| If a bar fails, revise once and rerun separately | not triggered | both bars PASS; JT-3 is next |

Acceptance is **AGENT** for the frozen protocol, raw-call count, scoring, account metadata and bars. Human comprehension is **HUMAN**, deferred: no human participants were measured. Actual JT-3/JT-4 rendering is **EXTERNAL** to this experiment and belongs to those items. The pilot-byte movement expected from JT-E1 is **0 B**; nothing is claimed before a pilot audit.

## Seeded bugs and local checks

Three Python runner bugs were planted one at a time and restored; each failed its named test, not a hash or build step:

1. `runner.py`: `Open reading:` → `Closed reading:`; `test_frozen_frame_and_two_arm_rendering` failed.
2. `runner.py`: score class without checking the decider; `test_scoring_requires_class_and_decider_and_flags_critical_misreading` failed.
3. `runner.py`: allow call 101; `test_call_and_context_caps` failed.

After restoration, `UV_CACHE_DIR=/tmp/uv-jt-e1 uv run pytest -q tests/test_jt_e1.py` passed (3). No Lean/Rust product code changed, so neither language needs a seeded bug. No generated-file input changed; no regeneration, Lean build, Lean audit or trust mutants was required. The full release gate is owned by the chain on the committed final HEAD, per the task instruction; it was not run here.

Trust: K +0, S +0, V +0 (no Lean edits); `UV_CACHE_DIR=/tmp/uv-jt-e1 uv run python tools/trust_map.py --check` passed against `6f59c66d6899`. DELTA: none; there is no user-visible product change. The source-word catalogue, rendering, diagnostics, verdicts and routes remain untouched.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean response or request decoder changed.
2. PASS: plan-row table above and `test_frozen_frame_and_two_arm_rendering` cover every experiment deliverable.
3. PASS: the three named seeded bugs above failed their local tests.
4. N.A.: no Python/Lean/Rust product semantics changed.
5. N.A.: no relay binding or response schema changed.
6. N.A.: the task assigns the final-HEAD full gate to the chain; raw-call evidence is committed here.
7. PASS: no DELTA or trust growth, verified by `git diff --name-only main...HEAD` and `tools/trust_map.py --check`.
8. PASS: no user-visible product delta; same diff and the product-file sweep above.
9. PASS: selected-test run on the finished code, recorded below.
10. N.A.: no Lean statement, theorem or proof changed.
11. PASS: `test_call_and_context_caps` checks both caps; each raw call records usage.
12. N.A.: no product runtime path changed.
13. N.A.: no test was removed or renamed (`git diff --name-status main...HEAD`).

## Final checks

`zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` passed on the finished worktree snapshot: 148 selected units, 0 failed/error ids, Mac runner `ve-mac-1`, 1906 s. The targeted local run after the scoring fix passed (`test_scoring_requires_class_and_decider_and_flags_critical_misreading`). No full release gate was run by this builder, per the task's chain-gate instruction. The current files are committed below; the chain gates that final HEAD.
