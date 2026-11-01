# eff-20261101-1: test_the_parts_merged_are_the_one_runs_record no longer depends on runner load

**Status: built; ready for the chain's gate.** Branch infra/eff-20261101-1, merge base db9abd91d (main).
**What changed:** one test file, `tests/test_trust_mutants.py`. The test now sets each part's run seconds in the loaded
record instead of using a text replace that only fired when the recorded seconds were 0.
**No DRI signature needed; no DELTA rows (there is no user-visible change); trust +0; test-only.**
Backlog: tm-merge-test-load-flake.

## Cause

The no-quarantine nightly of main a73c2f53 (on the VM fallback, under load) failed
`test_the_parts_merged_are_the_one_runs_record[2-1]` (`assert 1 == 2`) and `[9-6]` (`assert 8 == 9`) at its last line,
`assert len({d["seconds"] for d in each}) == n`. The test gave each part distinct run seconds with
`p.read_text().replace('"seconds": 0,', f'"seconds": {k * 37 % 101},', 1)`. That replace only matched when the part's
recorded seconds were exactly 0, which is `round(time.monotonic() - started)` in `tools/trust_mutants.py:2031`. A part
that took 0.5 s or more on a loaded runner kept its real value, so two parts could share a value and the set had
fewer than n members.

## Diff summary

`git diff main...HEAD -- tests/`: one line removed and one changed in the loop over `paths`
(`tests/test_trust_mutants.py:2405-2410`):

```
-        p.write_text(p.read_text().replace('"seconds": 0,', f'"seconds": {k * 37 % 101},', 1))
         d = json.loads(p.read_text())
+        d["seconds"] = k * 37 % 101  # set, not replaced: a part on a loaded runner records its real seconds, not 0
```

The part is still written back through `sharded.tm.evidence(d)`, which re-seals the record. For k = 1..9 the values
`k * 37 % 101` are 37, 74, 10, 47, 84, 20, 57, 94, 30: all distinct and above 0 for every parametrised n (at most 9).
No assertion changed. All of these are still checked: the byte-identical bare record, the printed lines, the shards
list, the jobs and seconds sums and max, the steps sums, distinct seconds, and seconds > 0. No test was added, removed,
renamed, skipped, quarantined or re-parametrised.

**Grep for the same pattern (step 3):**
`grep -rn "replace('\"seconds\"" tests/` and `grep -rnE "\.replace\(['\"][^)]*(seconds|elapsed|took|duration|time)" tests/`
found only the one line at `tests/test_trust_mutants.py:2406`. The other text replaces in that file (`:592`, `:813`)
edit Lean source text, not run facts. `tests/test_answer_cutoff.py:914,934` contain `"seconds": 0` as literal
dict values, not as a replace. So there was no other instance to fix.

## Proof the fix holds (hermetic, tmp_path only)

To reproduce the problem without load, I added a temporary line (never committed) as the first statement of the loop,
before the text replace. It simulates a part that took 1 s:

```
d = json.loads(p.read_text()); d["seconds"] = 1; p.write_text(sharded.tm.evidence(d))  # TEMP: a slow part
```

**Before the fix**, with the temporary line:
`uv run python -m pytest -q "tests/test_trust_mutants.py::test_the_parts_merged_are_the_one_runs_record[2-1]"`

```
>       assert len({d["seconds"] for d in each}) == n and data["seconds"] > 0
E       assert (1 == 2)
1 failed in 1.28s
```

This is the same `1 == 2` failure as the nightly.

**After the fix**, with the same temporary line still in place:
`uv run python -m pytest -q "tests/test_trust_mutants.py::test_the_parts_merged_are_the_one_runs_record"`
(all six parametrisations, including [2-1] and [9-6]):

```
6 passed in 1.05s
```

Then I removed the temporary line. The same command on the committed fix gave `6 passed in 1.09s`.

## Seeded bugs

| id | file | change | failing test | output |
|---|---|---|---|---|
| S1 | tests/test_trust_mutants.py | the new line set to `d["seconds"] = 37` (every part the same) | `tests/test_trust_mutants.py::test_the_parts_merged_are_the_one_runs_record[2-1]` | `assert (1 == 2)`, `where 1 = len({37})`, at the distinct-seconds assert; `1 failed in 0.75s` |

S1 was restored and the six cases passed again (`6 passed in 1.09s`). The same row is recorded in `seeded-bugs.json`.
The only code this item changes is test Python (no Lean, Rust, `ve/`, `tools/` or `conformance/` change), so there
is no product language that needs its own seeded bug.

## Test counts

- **Collected IDs before and after:** `uv run python -m pytest -q --collect-only tests/test_trust_mutants.py`, run on
  the file at main (`git show HEAD~1:tests/...`) and at the fix, then sorted and compared with `cmp`: **564 and 564,
  identical (`SAME-IDS`)**.
- **Whole file after the fix:** `zsh mac-pytest.sh -- -q -rs tests/test_trust_mutants.py`. Output:
  `564 passed in 1469.35s (0:24:29)`, with no skips (`-rs` listed none). The Mac was unreachable, so it ran on the VM
  under the same load as the nightly.
- **Whole file before the fix:** I did not run this as a separate heavy run, following the one-heavy-run-per-check
  budget. A local foreground attempt (`timeout 600 uv run python -m pytest -q tests/test_trust_mutants.py`) was
  stopped by its 600 s timeout before it finished, so it gave no count. The before-fix behaviour this item is about
  is shown by the deterministic reproduction above. The quarantined nightly-vm of a73c2f53 also passed the file.
- **Selected tests:** see the section below.

## Selected tests

SELECTED-PLACEHOLDER

## Notes

- The task names `--base $(git merge-base HEAD ve-integration)`, but this checkout has no `ve-integration` ref
  (`git rev-parse --verify -q ve-integration` printed nothing). I used the worker rule's base,
  `$(git merge-base HEAD main)` = db9abd91d.
- I did not run the full gate (`tools/gate.py`) myself. The worker instructions say the chain runs it on the committed
  final HEAD and writes gate-result.json; this overrides the task's last line.
- This change adds no sleep, short timeout or elapsed-time assert. It makes the test independent of elapsed time.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (there is no relay or route change; test-only).
2. Deliverables built, no rule broken: PASS. Steps 1-3 of the task are covered by the diff above and the grep
   (Diff summary). There is no Python copy of a Lean decision and no new report test (`git diff main...HEAD --stat`
   shows only tests/test_trust_mutants.py and this folder).
3. Tests can fail: PASS. Seeded bug S1 fails `test_the_parts_merged_are_the_one_runs_record[2-1]`, and the slow-part
   reproduction fails before the fix (Proof section).
4. Python, Lean and Rust agree: N.A. (no product code changed).
5. R8 binding: N.A. (no field is read from a Lean answer).
6. Gate evidence matches the final HEAD: PASS. The chain runs the gate on the committed final HEAD. Nothing is
   committed after that except this report, if it is filled in afterwards.
7. No unsigned item: PASS. There are no DELTA rows and no trust growth (trust +0).
8. Every user-visible change in DELTA: N.A. (this is a test-only change with no output diff).
9. Test selection: PASS. `uv run python tools/select_tests.py --base db9abd91d` selects 27/523 units, including
   tests/test_trust_mutants.py (the changed file).
10. Lean statements: N.A. (no Lean change).
11. Budgets fail closed: PASS. There is no sleep or deadline. The test no longer depends on wall time; it is covered
    by tests/test_hang_guards.py in the selected run.
12. No CPU or memory regression: N.A. (one dict assignment in place of one text replace in a test).
13. Test-removed trailer: N.A. (no test removed or renamed; 564 = 564 collected IDs, same set).
14. Pre-review self-check: PASS. Opposite direction: the fix passes with a slow part (seconds 1), and seeded bug S1
    (equal seconds) fails. Every claim above cites its command and output. Spec re-read: the task's "What to change"
    items 1-3 against the diff (set in the loaded dict after `json.loads`, comment says why, text replace dropped,
    re-sealed by `evidence`, assertions unchanged).
