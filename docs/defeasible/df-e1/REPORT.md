# DF-E1r build report

CALLS-BLOCKED: `busy: permission denied: /proc/23/environ` from the subscription account picker; zero reader calls.
HEAD: `feature/df-e1r`; preregistration committed in `afa0f9dc9` before the attempted call.
Changed: 24 checked reader items, the frozen rendering rule, a byte comparison test, and measured-usage runner.
Open: the delegate runs the command below outside this sandbox, then commits `raw/` and `RESULTS.md`.
No DRI signature is reserved. DELTA: none; no user-visible product change.

## Blocked call and handoff

Command: `UV_CACHE_DIR=/tmp/df-e1r-uv-cache uv run python docs/defeasible/df-e1/runner.py run`.
It exited 1 in `account()` before dispatch. The picker itself, run as
`PICK_SHORT=1 PICK_NOWAIT=1 zsh /home/seyran/code/manage-agents/pick-claude-account.sh`, exited 1 with
`busy: permission denied: /proc/23/environ`. No account override or paid credits were used. The empty `raw/.lock`
created before the picker was removed. Per this item's sandbox rule, the experiment stops here. There is no result,
PASS/FAIL, or human-reader claim. After the delegate's run, `runner.py score` supplies the counts for `RESULTS.md`.

## Plan rows and evidence

| Acceptance | Owner | State and evidence |
| --- | --- | --- |
| 24 rendered items, 12 `needs` with checked strict countermodels, 12 strict | AGENT | `prepare.py --items` generated `items.json` from `ve.defaults.ask()` and real Lean rows; `test_saved_item_bytes_equal_checked_renderers` passed. |
| Six short eligible; six other `needs` including stated conditions, switch and ranking | AGENT | N01–N06, N07–N08, N09–N10 and N11–N12 in `items.json`; the same test checks six short renderings. |
| Strict controls through the existing strict route; paired forms from one checked row | AGENT | `PRE-REGISTRATION.md` fixes both settled rules; `test_saved_item_bytes_equal_checked_renderers` passed. |
| Committed preregistration before the first call | AGENT | `afa0f9dc9`; `prereg_committed()` checks its three inputs before dispatch. |
| Separate subscription Sonnet 5.5 calls, at most 40 and 3M CW | EXTERNAL | Runner prepared; picker refused before a call. `test_failed_attempt_is_reserved_before_dispatch_and_never_retried` and `test_aggregate_charge_cap_applies_to_score_and_resume` passed. Delegate owns the call run. |
| Raw prompts, full results and usage; per-form misreadings and one-line outcome | EXTERNAL | Pending delegate call run. `runner.py` saves these fields and `score()` applies the frozen bar. |
| Apply a dropped short form in Lean | EXTERNAL | Follow-up `df-e1b` only if the short form is dropped; no `ve/` or `lean/` change here. |

Spec re-read: plan §DF-E1 at `docs/spec/defeasible-PLAN.md:1090`, D6 at line 135, and DE1/DE1′/DE6/DE6′ at lines 288–300. The question and bar in `PRE-REGISTRATION.md` match §DF-E1. The statement review is accepted in the plan; this item changes no statement.

## Tests, limits and seeded bugs

`UV_CACHE_DIR=/tmp/df-e1r-uv-cache uv run pytest -q tests/test_df_e1.py` passed **25** tests after the final code edit. `UV_CACHE_DIR=/tmp/df-e1r-uv-cache uv run python tools/trust_map.py --check` passed with K +0, S +0 and trusted +0 against main. `git diff main...HEAD --numstat` showed 802 generated `items.json` lines; hand-written changes are below the 600-line limit. Pilot bytes expected to move: 0; this is reader measurement only. No Lean audit, trust mutants or central regeneration applies; no Lean or Rust source changed. The release gate is run by the chain on the committed final HEAD.

The required selected run through `mac-pytest.sh --select` used the VM fallback and selected 26 units. Twenty-five
units exited 0; `tests/test_history_tests.py` had two failures because the generated history inventory had not
recorded the new `git rev-parse` call in `prepare.py` (run log `/tmp/ve-select-run-dpieiztw/`).
`UV_CACHE_DIR=/tmp/df-e1r-uv-cache uv run python tools/history_tests.py --write` refreshed
`tests/history-dependent.json` (135 history-reading tests). The two failed IDs were rerun alone through
`mac-pytest.sh --` on ve-mac-1: **2 passed in 18.82s**, exit 0. The runner's 2,395s total includes slot wait and
worktree setup. `UV_CACHE_DIR=/tmp/df-e1r-uv-cache uv run python tools/gate_collection.py --check --prebuilt`
reported 30,275 collected, 0 refused, 0 stale and 0 malformed test-removal trailers.

Three seeded bugs in `docs/defeasible/df-e1/runner.py` were planted, each with one named failing test, then restored:

| Bug | Failing test |
| --- | --- |
| Omit rule text from the prompt | `test_prompt_contains_only_rule_answer_and_question` |
| Make `within_caps` accept every charge | `test_aggregate_charge_cap_applies_to_score_and_resume` |
| Allow three long-form `needs` misreadings | `test_score_bar_and_short_comparison` |

## Next items

`df-1bbb` supplies DE6 gap sentences with the reader result. If the short form is dropped, `df-e1b` applies the decision in Lean. This report records a transport blocker, not a wording outcome.

## Self-review against BUILDER-CHECKLIST

1. N.A. — no relayed response schema or product route changed.
2. PASS — plan rows above; `test_saved_item_bytes_equal_checked_renderers`.
3. PASS — three seeded failures above; each named test failed on the planted code.
4. N.A. — no Python, Lean or Rust product semantics changed.
5. N.A. — no R8 relay binding changed.
6. N.A. — the chain runs the final-HEAD release gate after this committed handoff.
7. PASS — no DELTA row or trust growth; `tools/trust_map.py --check`.
8. PASS — no product files changed; `git diff main...HEAD --name-only`.
9. PASS — `tests/test_df_e1.py` was selected by `mac-pytest.sh --select`; generated history inventory fixed after its two failed IDs.
10. N.A. — no Lean theorem statement or proof changed.
11. PASS — `test_aggregate_charge_cap_applies_to_score_and_resume`, `test_failed_attempt_is_reserved_before_dispatch_and_never_retried`.
12. N.A. — no product CPU or memory path changed.
13. PASS — renamed transport tests have `Test-removed` trailers in `afa0f9dc9` and `d490ae83a`; `gate_collection.py --check --prebuilt` reports 0 refused.
14. PASS — both sides of answer scoring in `test_score_bar_and_short_comparison`; spec re-read above; blocked command and test outputs cited here.
