# JT-E1s build report

**Result: FAIL. The item stops here as the task requires: there is no second revision, and the DRI has been told.** No DRI signature is reserved, and there are no DELTA rows. The gate is bar (a): English 25/40 against identifier 20/40, a margin of 5, where at least 36/40 and a margin of 6 were needed. Bar (b) passes with 0 critical misreadings. This is proxy readability from Sonnet 5.5, not human comprehension.

DRI message: `zsh /home/seyran/code/manage-agents/msg.sh dri jt-e1s "JT-E1s FAIL: ..."`. It was written to `inbox/dri/20261031T232738Z-jt-e1s-3080150.md`.

## Deliverables (task order)

| # | Deliverable | Commit | Evidence |
|---|---|---|---|
| 1 | The one revision of 2.4's generated English, with its reason stated before any call | `cc2e46732` | [`PRE-REGISTRATION.md`](PRE-REGISTRATION.md) "The one revision, and why". The JT-3 amendment line is `docs/spec/judgment-terms-PLAN.md:588`. `test_revision_keeps_the_declaration_and_adds_the_answer_row` |
| 2 | A fresh 40-row frame with JT-E1r's composition (20 UDHR, 20 constitution, all three classes), frozen and committed before any call; the bars quoted verbatim | `cc2e46732` (calls began after it) | `test_frozen_frame_and_real_capture_bytes`, `test_items_are_fresh`, `test_pre_registration_quotes_the_bars_verbatim` |
| 3 | Control = main's renderer stdout at `4d9a0eeb0`; English = template-generated; identical fallback for an absent or rejected template | `cc2e46732` | `render.audit()` returns the 8 fallback rows; `test_frozen_frame_and_real_capture_bytes` |
| 4 | Separate blinded calls; a failed call scores incorrect; raw records saved; `--score` reproducible | `3090b6d41` | 80 records in [`raw/`](raw/), 0 errors. `uv run python docs/judgment-terms/jt-e1s/runner.py --score` gives `{"identifier": 20, "english": 25}`, `bar_a: false`, `bar_b: true`, `cw: 1185742`. `test_saved_records_reproduce_the_gate_line` |
| 5 | RESULTS.md with one gate line; tests in the style of `tests/test_jt_e1r.py` | `3090b6d41`, `392887ff4` | [`RESULTS.md`](RESULTS.md) line 3; `tests/test_jt_e1s.py` (8 tests) |
| — | On FAIL: stop, record it, message the DRI | `3090b6d41` | plan line 588 "Result (2026-10-31): FAIL"; the message above |

On PASS, the task asks for the renderer file JT-3's conformance test must equal. The result is FAIL, so no file is named. The JT-3 amendment line records that JT-3's declaration lines use today's identifier wording.

**Which fallback applies.** The task names identifier wording. The plan's section 6 (line 777) says "If it fails again, JT-3 lands with the legend line only and the zone rows wait". Both texts agree that 2.4's English is not gated in. How JT-3 lands is for the DRI to decide, and the message above asks for that decision.

**Synthesis edits (`debates/plan-synthesis-2/edits-judgment-terms.md`).** This item implements none of the four edits. The frame uses the decider token `unstated`, which agrees with edit 1.

**Model calls.** These ran under the task's authorisation, the same as JT-E1r (reviews/lp-answers-20261029T1620.md item 2): 80 Sonnet 5.5 calls and 1,185,742 CW, against caps of 100 calls and 3M CW. The picker chose `claude-panaali2` for every call, `fallback_credit` was `null` on all 80, and no call failed. The `--score` output above is the source for these figures.

## How it is built

- **Size.** `render.py` (62 lines) and `runner.py` (61 lines) load JT-E1r's frozen generator and runner as private module copies bound to this directory, so nothing is copied (one owner). Only `english()` changes: it is `declaration()` (JT-E1r's line, byte for byte) followed by `answer()` (2.4's settled, left to, or conflict rows).
- **Pre-call check.** `committed()` checks that this item's four frozen files and the two JT-E1r files it runs are committed unchanged.
- **Limits.** Every limit is JT-E1r's runner, unchanged: the 100-call cap, the 3M-CW cap with a 25k reserve per call, the 2 MB raw-record cap and the durable dispatch journal.

## Seeded bugs

This item changes no Lean, Rust or `ve/` product code. Its only code is Python in two new files, so all the seeded bugs are Python. Each was planted with a one-line edit, run against one test and restored with `git checkout`; `git status` was clean afterwards.

| # | File | Bug | Failing test |
|---|---|---|---|
| S1 | `docs/judgment-terms/jt-e1s/render.py` | turns row drops "(a judgment for <decider>)" | `test_revision_keeps_the_declaration_and_adds_the_answer_row` |
| S2 | `docs/judgment-terms/jt-e1s/render.py` | fallback row gets the English lines | `test_frozen_frame_and_real_capture_bytes` (audit: `old == new`) |
| S3 | `docs/judgment-terms/jt-e1s/render.py` | conditional row drops the line without the criterion | `test_revision_keeps_the_declaration_and_adds_the_answer_row` |
| S4 | `docs/judgment-terms/jt-e1s/runner.py` | the runner keeps JT-E1r's `raw/` directory | `test_runner_is_bound_to_this_frame` |
| S5 | `docs/judgment-terms/jt-e1s/runner.py` | the pre-call check skips `jt-e1r/runner.py` | `test_runner_is_bound_to_this_frame` and `test_commit_check_accepts_the_committed_frame_and_refuses_an_edit` |

Each run printed `1 failed, 6 deselected` (S5's second test: `1 failed, 7 deselected`).

## Numbers

- **Trust.** `uv run python tools/trust_map.py --check` reports `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0` and PASS. There are no trusted definitions, so no mutants.json is needed.
- **Size.** `git diff --numstat` against the merge base, excluding the generated captures, raw records and regenerated files, gives 354 hand-written lines before this report.
- **Pilot bytes.** The estimate is 0: no product path changes.
- **Selected tests.** `zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` ran on the finished code. The log is `/tmp/jt-e1s-select-run.log`: `SHARD 1/2: 96 units, 96 passed` and `SHARD 2/2: 76 units, 76 passed`, exit 0.
- **Regeneration.** `uv run python tools/regen_generated.py --write` was run once (`251fc101c`). It updated the code map and `tests/history-dependent.json`.
- **Pre-existing failures.** None of this item's tests are in `main-known-red.txt`.

## Spec re-read

- The declaration line against `docs/spec/judgment-terms-PLAN.md:246`: unchanged from JT-E1r.
- The settled row against `:249`. The `…` is filled with "that <conclusion>".
- The left-to row against `:250`. Every turns row names its decider, so the "(the text does not say who makes it)" variant never occurs.
- The conflict rows against `:252`. The "given" line is shown beside "These rules conflict where <atom>.", never instead of it.
- The bars against `:773`–`:774`, word for word (`test_pre_registration_quotes_the_bars_verbatim`).
- The one-revision rule against `:777`.

## Next item

The next item is jt-3, the declaration, legend and status lines with `tests/test_jt3_english.py`. Its wording gate is now FAIL, so its declaration lines use the identifier fallback until the DRI decides otherwise.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer or relay is added.
2. PASS: the deliverables table above. The diff has no Python copy of a Lean decision (the generator reuses JT-E1r's code), no permanent report test (`test_saved_records_reproduce_the_gate_line` reads saved raw records only), and no overlap with in-flight branches (`git diff --name-only main...<branch>` over the feature, lean-first, infra and foundation branches: none).
3. PASS: seeded bugs S1–S5, each killed by the named test.
4. N.A.: there is no Python, Lean or Rust implementation pair. The control is main's renderer, re-run by `render.audit()` in `test_frozen_frame_and_real_capture_bytes`.
5. N.A.: no relay or binding.
6. PASS: the gate runs on the committed final HEAD (chain). The evidence is saved raw records, not a live diff (`test_saved_records_reproduce_the_gate_line`).
7. PASS: no signature is reserved, and there are no DELTA rows.
8. N.A.: no user-visible product change.
9. PASS: `tools/select_tests.py --base <merge-base>` selects `tests/test_jt_e1s.py` and `tests/test_jt_e1r.py`, and the seeded S1–S5 failures are in `tests/test_jt_e1s.py`.
10. N.A.: no Lean statement.
11. PASS: the call, CW and raw-record caps are JT-E1r's, unchanged, and the scoring refuses a short frame (`test_runner_is_bound_to_this_frame`, 79 of 80). The tests use no sleeps or deadlines.
12. N.A.: no product path changes; there is no check or render time to compare.
13. N.A.: no test is removed or renamed.
14. PASS. Both directions are tested:
    - pre-call check: accepts the committed frame and refuses an edit (`test_commit_check_accepts_the_committed_frame_and_refuses_an_edit`);
    - fallback rows: identical in both arms, while template rows differ (`test_revision_keeps_the_declaration_and_adds_the_answer_row`);
    - scoring: 79 records raise, while 80 score (`test_runner_is_bound_to_this_frame`, `test_saved_records_reproduce_the_gate_line`).

    Every claim above cites its command, and the spec re-read is listed above.
