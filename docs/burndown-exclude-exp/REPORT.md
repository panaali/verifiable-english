# burndown-exclude-exp: experiment rows leave the sprint burndown

Backlog row burndown-exclude-exp (infra, p35). DRI ruling 20:26Z Oct 29 (manage-agents `reviews/escalations-20261029.md`,
"DRI rulings 20:26Z on dri-sprint's escalations" item 1): the experiment rows leave the sprint and run after Nov 12;
DF-E1r and JT-E1r stay because they gate builds.

No VE product code changed. The change is in manage-agents `tools-local/` (not a git repository): `burndown.py` (written as
`.new`, compiled, then moved in; backup `burndown.py.bak-20261030-burndown-exclude-exp`) and a new test file
`test_burndown.py`. This branch holds only this report and its evidence. No DELTA rows: nothing user-visible in VE changes.

## What changed in `tools-local/burndown.py`

- `EXP_IN_SPRINT = {"df-e1r", "jt-e1r"}` and `sprint_scope(items)`. The sprint now counts build rows plus those two
  experiments. Every other `exp` row goes to `outside`. `doc` rows were not counted before and still are not.
- The total, each family's left count, the queue-ordered projection and the all-items date use the sprint rows only.
- A merge of an outside experiment row, or of a sub-batch of one (`match_id`, split out of `family_of`), is not a sprint
  merge: it is left out of "merged today" and the 72 h rate.
- The new line after the family table reads: "Experiment rows outside the sprint (DRI ruling 20:26Z Oct 29, ...;
  df-e1r/jt-e1r stay and are counted above): N left, M merged; not in the total, the rate or the projection: <family n, ...>."
- `--json` gains `exp_outside` (`left`, `merged`, `families`), and each `sprint-burndown.jsonl` line gains `exp_outside`.
  From the next day's line on, `left` counts sprint rows only. The lines written up to 2026-10-30 still include experiments.

## Live effect

`python3 -I tools-local/burndown.py --write` at 23:33Z, first line of SPRINT-BURNDOWN.md:
"191 plan items left (~588 merges at 3.1 merges per plan item ...); merged today 14; rate 13.3 sprint merges/day (72 h)".
The old script at 23:32Z (`python3 -I tools-local/burndown.py --no-guard`, before the move) gave "247 plan items left (~761
merges ...)" and all items "Sun Dec 27". The new script gives "Mon Dec 14". The new line says "56 left, 0 merged". The ruling
counted 59 rows of 253 on Oct 29; SPRINT-ITEMS.tsv now has 58 `exp` rows (`awk -F'\t' '!/^#/{print $3}' SPRINT-ITEMS.tsv |
sort | uniq -c`: 204 build, 9 doc, 58 exp), and 2 of those (df-e1r, jt-e1r, both merged) stay in the sprint.

## Tests

`python3 -W ignore -I tools-local/test_burndown.py -v` ran 6 tests, all OK. Output saved in `test-output.txt`. The tests are
hermetic: a temp `BURNDOWN_M`, `split_factor` stubbed and no live git. With `BURNDOWN_SCRIPT=<old burndown.py>`, 4 fail and
2 error.

- `test_scope_keeps_only_the_gating_experiments`: build rows, df-e1r and jt-e1r are counted; df-e2, df-e3 and jt-e2 are
  outside; doc rows are in neither list.
- `test_total_excludes_outside_experiments`: `left` is 4. The per-family build/exp split and `exp_outside` are exact.
- `test_projection_ignores_outside_experiments`: 10 experiments are queued ahead of df-1. The projected date is the same
  as without them.
- `test_outside_experiment_merges_are_not_sprint_merges`: merges of df-e2, its sub-batch df-e2b and jt-e2 are left out.
  df-1 and jt-e1r still count in the rate and in merged today (both directions).
- `test_separate_line`: exactly one line, with its counts and families. No outside row appears in the table.
- `test_write_records_outside_count`: `--write` records `left` 4 and `exp_outside` 2 in the jsonl, and the line is in
  SPRINT-BURNDOWN.md.

## Seeded bugs (Python; file /home/seyran/code/manage-agents/tools-local/burndown.py; `mutants.json`)

Each bug was planted in a scratch copy in /tmp and run with `BURNDOWN_SCRIPT=<copy> python3 -I tools-local/test_burndown.py`.
The installed file was never changed.

1. `sprint_scope` counts every exp row. Caught by `test_projection_ignores_outside_experiments`, among others (FAILED
   (failures=5)).
2. `EXP_IN_SPRINT = set()`. Caught by `test_scope_keeps_only_the_gating_experiments` and `test_outside_experiment_merges_are_not_sprint_merges`
   (failures=5).
3. `fam_of` without the `out_ids` check. Caught by `test_outside_experiment_merges_are_not_sprint_merges` (failures=1).
4. `out_left = list(outside)`. Caught by `test_separate_line` (failures=3).
5. The line is not appended. Caught by `test_separate_line` and `test_write_records_outside_count` (failures=2).

## Not changed (outside the row)

- With rate 0, the projection overflows (`timedelta(days=1e9)`). The old script does this too, and the tests seed one
  older merge to avoid it.
- ve-limits is outside the sprint by the same ruling's item 2. This row only names experiments, so the script still counts
  ve-limits rows.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed Lean answer is touched.
2. Deliverables built, no rule broken: PASS. Exclusion, projection and separate line are covered by the 6 tests above. The
   script was edited only through `.new`, `py_compile`, `.bak-20261030-burndown-exclude-exp` and `mv`.
3. Tests can fail: PASS. 5 seeded bugs are each caught (`mutants.json`), and the old script fails 6 of 6.
4. Python/Lean/Rust agree: N.A., this is a manage-agents Python tool only.
5. R8 binding: N.A., no binding.
6. Gate evidence matches final HEAD: PASS. The chain runs the gate on the final HEAD. Selected tests ran once on 1d3713da7: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` rc 0, 4 shards with 38+29+27+27 = 121 units, all passed (GitHub Actions run burndown-exclude-exp-1d3713da-t403301, 1602 s).
7. No unsigned item: PASS, no DELTA rows and no reserved signature.
8. User-visible change in DELTA: N.A., VE's user-visible behaviour is unchanged.
9. Test selection: N.A., no VE code changed. `test_burndown.py` runs directly, like the other tools-local tests.
10. Lean statements: N.A.
11. Budgets fail closed: N.A. The only budget-like edge is rate 0, which predates this change (see "Not changed").
12. No CPU or memory regression: PASS. Only list filters were added. `/usr/bin/time -f '%e s %M KB' python3 -I tools-local/burndown.py --no-guard` gives 0.12 s and 14292 KB; the `.bak` gives 0.12 s and 13732 KB.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. Both directions are in `test_scope_*` and `test_outside_experiment_merges_*`.
    Spec re-read: "the 59 experiment rows ... leave the sprint ... (DF-E1r/JT-E1r stay, they gate builds)" against
    manage-agents `reviews/escalations-20261029.md:67`, and the row title against `backlog.sh show burndown-exclude-exp`.
