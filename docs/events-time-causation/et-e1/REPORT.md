# et-e1 REPORT: comprehension of the explicit wordings (ET-E1)

Status: done; no DRI signature reserved. HEAD: the branch head after this file (feature/et-e1).
Changed: the pre-registration, a runner and scorer, 150 Sonnet 5.5 answers, RESULTS.md and a scorer test. One line
in `tools/regen_generated.py` registers the scorer as evidence. No change to `ve/`, `lean/` or `rust/`.
Result (early evidence from a model proxy): 13 of 16 groups PASS, including all 13 wordings of 2.7. `until-U1` (13/25) and
"until" told apart (8/20) are below the bar, and RESULTS.md proposes a U1 rewording for ET-5 (not applied).
Open: ET-5 takes the U1 rewording; the ET-6 rerun covers the U1 items only. Hand-written size is over ~600 (see Size).

## Model calls

`SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 7)`. 150 calls to
`claude-sonnet-5-5` through the `claude` CLI on the account `pick-claude-account.sh` picked (`claude-panaali2`, an
OAuth subscription login). The runner refuses a non-OAuth account and strips `ANTHROPIC_*` variables. No API key
and no paid credits were used. The pre-registration was committed in `4158614c2` at 13:12:51Z, and the first call
started at 13:13:10Z. There were no transport errors or retries. Every answer reports the model `claude-sonnet-5-5`.

## DELTA

None: there is no user-visible change, so no DELTA.md is written.

## Plan rows delivered

| Plan / task line | Delivered | Evidence |
|---|---|---|
| ET-E1: 30 items, the wordings of 2.7 | 20 items, one group per row of 2.7's table | `items.json`, `test_preregistration_is_well_formed` |
| the "until" reading sets per modality (D9) | U1/U2 for may, must, must not, need not; the date candidate (T11c) | `items.json` `until-*`, `until_pairs` |
| the T11 reading set | `t11-may-u1-before-e`, `t11-may-u1-e-day`, `t11-may-u2-e-day` (days 4 and 5 January; E's own day) | `items.json` |
| (1) pre-registration before the first call: items, expected answers, prompt text, bar | `PREREGISTRATION.md`, `items.json`, `prompt.txt` in `4158614c2` | commit time precedes `raw/*` `started` |
| Bar: >= 90% per wording; "until" told apart >= 90% | `run.py score`; pairs scored sample by sample | `test_one_miss_in_five_...`, `test_told_apart_needs_both_...` |
| (2) runner: Sonnet 5.5 via the `claude` CLI on the picked account, subscription only | `run.py run` | `raw/*.json` `account`, `cli.model_usage` |
| (3) raw answers and RESULTS.md: per wording correct/total, verdict, rewording for each below the bar | `raw/`, `results.json`, `RESULTS.md` | `python3 run.py score` |
| Early evidence, not proof about human readers | first line of RESULTS.md | — |
| No change to `ve/` or `lean/` | none | `git diff --stat main...HEAD` |

Not delivered: no plan row is missing.

## Tests run

- `tests/test_et_e1_probe.py` (11 tests: pre-registration well-formed, answer parsing, bar, told-apart pairing,
  binding of raw answers to items and samples).
- Selected tests on the Mac runner (`mac-pytest.sh --select`, 138 units): one unit failed. It was
  `tests/test_regen_generated.py::test_every_script_with_a_writing_mode_is_registered_or_excluded_with_a_reason`,
  because the scorer's `--write` flag was not registered. It is fixed by the `NOT_REGENERATED` line, and the rerun of
  that id plus the new file passes (12 passed).
- Not run: the full gate (the chain runs it), regen (no generated input changed), lake build and audit (no Lean
  change), and trust_mutants (no trusted Lean).

## Seeded bugs (`mutants.json`)

| Id | File | Bug | Failing test |
|---|---|---|---|
| S1 | `docs/events-time-causation/et-e1/run.py` | first `ANSWER` line instead of the last | `test_parse_answer_takes_the_last_answer_line` |
| S2 | same | per-wording bar `>` instead of `>=` | `test_one_miss_in_five_is_below_the_bar_and_one_in_ten_is_not` |
| S3 | same | a pair told apart if either reading is correct | `test_told_apart_needs_both_readings_of_the_same_sample` |
| S4 | same | absent answers accepted | `test_load_raw_refuses_unbound_answers[missing]` |
| S5 | same | int check on `sample` dropped | survived, as an equivalent mutant: the file-name binding still refuses `False` |
| S6 | `tools/regen_generated.py` | the et-e1 `NOT_REGENERATED` entry deleted | `test_every_script_with_a_writing_mode_is_registered_or_excluded_with_a_reason` |

## Trust, size, overlap, pilot bytes

- Trust: no Lean, Rust or `ve/` change, so K+S+V +0 and no R16 row.
- Size, hand-written lines: `items.json` 192 (the pre-registered items, frozen after the first call), `run.py`
  200, the test 114, RESULTS.md 82, PREREGISTRATION.md 50, `mutants.json` 26, `prompt.txt` 10,
  `tools/regen_generated.py` 1, and this report. That is about 790 lines, over the ~600 guide. Evidence that is not
  counted: `raw/` (150 files) and `results.json` (scorer output, 526 lines). The experiment is one unit and cannot be
  cut after the calls, so this is recorded rather than split.
- Overlap: `tools/regen_generated.py` is also edited by `foundation/me-1` and `infra/arch-AR-1`. This branch adds
  one line in the `NOT_REGENERATED` dict (between the `docs/premise-scale` and `df-1bb` entries). All other files
  are new and belong to this item.
- Pilot bytes moved: 0 (an experiment). ET-5's wordings move bytes later.

## Next item

et-4 (after et-3d), then et-5 with ET-E1's wordings: take RESULTS.md's U1 silence sentence and legend line. The
ET-6 rerun covers only the U1 items and the four "until" pairs, with the reworded options C/D (RESULTS.md).

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A., no relayed Lean answer.
2. Every required deliverable: PASS, the plan rows table above (`test_preregistration_is_well_formed`, `raw/`, RESULTS.md).
3. Tests can fail: PASS, seeded bugs S1-S4 and S6 (`mutants.json`), each killed by a named test. S5 is an equivalent mutant.
4. Py/Lean/Rust agree: N.A., no product code.
5. R8 binding: PASS for the scorer's own input: `test_load_raw_refuses_unbound_answers` (unknown item, sample out of range, bool sample, misnamed, missing).
6. Gate evidence matches HEAD: N.A. here, the chain gates the final HEAD. The selected-test run and rerun are on this branch.
7. No unsigned item: PASS, no DELTA rows and no trust growth; the model calls cite DRI decision item 7.
8. Every user-visible change in DELTA: N.A., no user-visible change.
9. Test selection: PASS, `tools/select_tests.py --base <merge-base>` selects `tests/test_et_e1_probe.py` and `tests/test_regen_generated.py`, the test that caught S6.
10. Lean statements: N.A., no Lean.
11. Budgets fail closed: N.A., no checker operation. A failed call is saved and scored incorrect, never correct.
12. No CPU or memory regression: N.A., no product code.
13. Test-removed trailers: N.A., no test removed or renamed.

## FIXMAP
- `docs/events-time-causation/et-e1/PREREGISTRATION.md`: design, reader, calls and bar (frozen at `4158614c2`).
- `docs/events-time-causation/et-e1/items.json`: the 30 items, option sets, wording groups, `until_pairs`, bar (frozen).
- `docs/events-time-causation/et-e1/prompt.txt`: system prompt and user template (frozen).
- `docs/events-time-causation/et-e1/run.py`: runner and scorer.
  - `prompt_parts` -> run.py:46 (renders an item); `parse_answer` -> run.py:56 (last ANSWER line)
  - `pick_account` -> run.py:68 (picker; refuses non-OAuth); `call`/`run_one` -> run.py:77/95 (one CLI call, retries)
  - `load_raw` -> run.py:129 (binds raw answers to items/samples); `score` -> run.py:148 (per-wording bar, told-apart)
- `docs/events-time-causation/et-e1/raw/*.json`: the 150 answers (evidence; never edit).
- `docs/events-time-causation/et-e1/results.json`: `python3 run.py score --write` output.
- `docs/events-time-causation/et-e1/RESULTS.md`: per-wording table, U1 analysis, proposed rewordings (ET-5).
- `docs/events-time-causation/et-e1/mutants.json`: seeded bugs S1-S6.
- `tests/test_et_e1_probe.py`: pre-registration and scorer tests (hermetic, no model calls).
- `tools/regen_generated.py`: one `NOT_REGENERATED` entry for run.py (its `--write` flag).
- Regression: `VE_NATIVE_PREBUILT=1 uv run pytest -q tests/test_et_e1_probe.py tests/test_regen_generated.py -k "et_e1 or writing_mode"`
- Rescore: `python3 docs/events-time-causation/et-e1/run.py score` (prints the table; `--write` rewrites results.json)
- Regen: none (no generated file owns these paths). trust_mutants: not used (no Lean).
## END FIXMAP
