# verdict-unknown-rule: an UNKNOWN on one side of a verdict sample is not a mismatch

Status: done, installed in manage-agents. The VE branch holds evidence only (no product code).
What changed: `cloud-verdict-compare.py`, the comparator behind verdict-sample.sh and cloud-late.py, now treats a mutant that is UNKNOWN on one side and KILLED or SURVIVOR on the other as **undecided**: it is counted separately and is not a mismatch. KILLED vs SURVIVOR, INVALID vs anything, and every other difference still trip the pool.
Open items: none. No DRI signature is needed (no VE delta; see "Trust and DELTA").

## The row

Backlog row `verdict-unknown-rule` (DRI, p40; jt-2c M010, 2026-10-30 13:15Z). In that sample, M010 was UNKNOWN on the loaded VM
("Lean could not finish") and KILLED on Actions. Inputs, files and the other 79 mutants were equal. The comparator exited 1,
verdict-sample.sh removed ACTIONS_POOL, and the DRI turned the pool back on at 13:16Z (`manage-agents/ACTIONS_POOL` text).

## What changed (`/home/seyran/code/manage-agents/cloud-verdict-compare.py`; diff in `manage-agents.diff`)

- `undecided(a, b)`: one side's `raw_status` (the verdict before --allow) is UNKNOWN and the other's is KILLED or SURVIVOR.
  Each side's `status` must be that verdict or ALLOWED, so an allowed UNKNOWN vs an allowed SURVIVOR counts as undecided too.
- For an undecided mutant, the comparator skips the verdict fields (`status`, `raw_status`, `detail`, `killed_at`) and `reads`.
  trust_mutants `verdict()` sets `reads` only for a KILLED or INVALID verdict (`tools/trust_mutants.py:1329-1337`). Every identity
  field (`file`, `line`, `definition`, `operator`, `lines`, `before`, `after`, `trust_class`, `trusted`) is still compared.
  A differing identity field makes the mutant a normal difference.
- `counts` may differ only by those mutants' statuses: vm count minus cloud count, for each key, equals the shift the undecided
  mutants cause. Any other count difference still trips.
- The separate count appears in the output in three places:
  - the line `UNDECIDED (...): <id> (vm X, cloud Y), ...`;
  - the field `N undecided` in the `mutants:` line, within the first 130 characters, so it reaches the verdict-sample.sh trial-log
    row and the cloud-late.py summary, which both cut that line at 240-260 characters;
  - `counts: ... differ by the undecided mutants only` and `VERDICTS EQUAL (N undecided, not compared)`.
- Exit codes are unchanged: 0 equal, 1 differ, 3 invalid reference, 4 failed. verdict-sample.sh and cloud-late.py are unchanged.
  A sample whose only differences are undecided mutants is EQUAL and meets the sampling obligation.

Install: `.new` copy, py_compile and `zsh -n`, backups `*.bak-20261030-verdict-unknown-rule`, then `mv`.

## Live effect: the M010 case replayed

`python3 -I cloud-verdict-compare.py cloud-jobs/jt-2c-0e79c259/vm-ref.json cloud-jobs/jt-2c-0e79c259/cloud-verdicts.json`
now exits 0 (`m010-replay.txt`): `UNDECIDED ...: M010 (vm UNKNOWN, cloud KILLED)`,
`mutants: 80 vm, 80 cloud, 0 with a differing identity or verdict field, 1 undecided`,
`counts: ... differ by the undecided mutants only`, `VERDICTS EQUAL (1 undecided, not compared)`.
The verdict-sample.sh row summary of that output (its `grep -E '^(mutants:|counts:|...)' | cut -c1-260`) begins
`mutants: 80 vm, 80 cloud, 0 with a differing identity or verdict field, 1 undecided`.

## Tests (`/home/seyran/code/manage-agents/test-harness/comparators/test-comparators.zsh`, new section "UNKNOWN vs decided")

`zsh test-harness/comparators/test-comparators.zsh` gives `comparators: 33 passed, 0 failed`, exit 0 (`test-output.txt`). The 10 new tests:

| must accept (undecided, exit 0, `1 undecided`) | must refuse (exit 1, VERDICTS DIFFER) |
|---|---|
| UNKNOWN on the VM, KILLED in the cloud (the M010 shape; counts shifted) | KILLED vs SURVIVOR |
| KILLED on the VM, UNKNOWN in the cloud | INVALID vs KILLED |
| UNKNOWN vs SURVIVOR | UNKNOWN vs INVALID |
| allowed UNKNOWN vs allowed SURVIVOR (raw_status differs) | UNKNOWN vs KILLED with another mutant text (identity `after`) |
| equal records: `0 undecided`, plain `VERDICTS EQUAL` | UNKNOWN vs KILLED whose counts differ by more than that mutant |

With the pre-change comparator (`CVC=` the `.bak` copy) the harness gives 27 passed, 6 failed: the 4 undecided cases and the
2 tests that check the new count text. Output quoted in `mutants.json` `note`.

Other harnesses that drive the comparator, run after the install:
- `test-harness/cloudplumb/test-advfix6.zsh`: 57 passed, 0 failed (comparator exit codes 0/1/3).
- `test-harness/cloudplumb/test-ccloud.zsh`: 46 passed, 0 failed.
- `test-harness/cloudplumb/test-advfix4.zsh`: 40 passed, 5 failed. Its verdict-sample.sh section (EQUAL, MISMATCH turning pools
  off, reuse, no load window) passes. The 5 failures are all Actions suspension and overflow cases. That code is actions-health.py
  and cloud-overflow.sh, which item actions-suspend-per-item installed at 06:20-06:28Z (CURRENT-STATE line 723). Those cases do
  not call the comparator.
- `test-harness/cloudplumb/test-cloudplumb.zsh`: 174 passed, 4 failed, all in the release upload and manifest deletion step,
  which does not call the comparator.
- These 9 failures are outside this row and are not fixed here.

Selected VE tests (`selected-run.txt`): 1 failure, `tests/test_lean_share.py::test_a_stored_build_restores_up_to_date_and_never_shares_a_file_lake_rewrites`.
That run went to the Claude cloud as root (`pytest-of-root`), where `os.access(path, W_OK)` is always true. Rerun alone on the
Mac runner at HEAD 51d02fe6: `1 passed`. This branch changes only docs, so the failure comes from the runner environment.

## Seeded bugs (Python; file `/home/seyran/code/manage-agents/cloud-verdict-compare.py`; `mutants.json`)

Each bug ran on a scratch copy via the harness's `CVC=` override; the installed file was never mutated.

1. UNKNOWN vs INVALID counted as undecided: "UNKNOWN vs INVALID still trips" fails.
2. counts unchecked when a mutant is undecided: "UNKNOWN vs KILLED whose counts differ by more than that mutant still trips" fails.
3. identity fields skipped for an undecided mutant: "UNKNOWN vs KILLED of another mutant text (identity field after) still trips" fails.
4. KILLED vs SURVIVOR counted as undecided: "KILLED vs SURVIVOR still trips" fails.
5. `reads` still compared (`VERDICT_OF = ()`): "UNKNOWN on the VM, KILLED in the cloud (jt-2c M010)" and its reversed twin fail.

No Lean or Rust code changed, so there are no Lean or Rust seeded bugs.

## Trust and DELTA

No VE user-visible delta: no diagnostic, verdict, field or trusted Lean changed. This is the orchestration guard that decides
whether a cloud pool stays on, and the backlog row comes from the DRI (source DRI). No DELTA.md and no signature are needed.

## Not changed (outside the row)

- UNKNOWN vs UNKNOWN with different details still trips.
- UNKNOWN vs INVALID still trips: the row lists "INVALID vs decided" as a real flip.
- verdict-sample.sh and cloud-late.py: their summaries already carry the `mutants:` line.

## Spec re-read

- "a mutant UNKNOWN on one side and KILLED/SURVIVOR on the other is not a mismatch" against the backlog title: both directions
  (VM UNKNOWN, cloud UNKNOWN) and both decided values are tested.
- "only KILLED vs SURVIVOR (or INVALID vs decided) flips trip the pool": KILLED vs SURVIVOR, INVALID vs KILLED and
  UNKNOWN vs INVALID are tested as trips. Every other difference that tripped before (ids, identity fields, counts beyond the
  shift, inputs) still trips.
- "record UNKNOWN-vs-decided as a separate count": the `N undecided` field of the `mutants:` line and the `UNDECIDED` line.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed Lean answer touched).
2. Required deliverables built: PASS. The comparator rule, the separate count and the tests are installed; `test-output.txt` shows 33 passed.
3. Tests and gates can fail: PASS. 5 seeded bugs are each caught (`mutants.json`), and the pre-change comparator fails 6 tests.
4. Python, Lean and Rust agree: N.A. (only a manage-agents Python script changed).
5. R8 binding: N.A. (no relayed answer).
6. Gate evidence matches the final HEAD: PASS. The chain runs the gate on the final HEAD; selected runs are at 51d02fe6 (`selected-run.txt`).
7. No unsigned item left: PASS. No DELTA rows and no reserved signature.
8. Every user-visible change in DELTA: N.A. (no VE user-visible change).
9. Test selection still finds the tests: N.A. (no VE code; the harness is run directly, `test-output.txt`).
10. Lean statements and proofs: N.A. (no Lean change).
11. Budgets fail closed: PASS. UNKNOWN is kept as "not decided" and never counted as a pass or a kill; counts beyond the shift
    trip (test "counts differ by more than that mutant").
12. No CPU or memory regression: N.A. (one dict per comparison).
13. Test-removed trailer: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS. Accept and refuse tables are in Tests; every claim cites a file or command;
    the spec re-read is above.
