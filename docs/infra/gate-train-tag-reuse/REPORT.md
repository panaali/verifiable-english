# gate-train-tag-reuse: report

**NO INSTALL NEEDED; nothing waits for a decider read.** The fix this row asks for is already in the installed
`/home/seyran/code/manage-agents/gate-train.sh`, lines 25-26. reviews/dri-decisions-20261108-et-4b-sync.md item 2 put it
there on 2026-11-08 ("First relaunch, 13:51Z ... Fix: the record now moves together with its sidecars, and when the stale
record is the run's own output, the inventory reads the moved copy"). This item does not change the script. It adds the
row's missing deliverable: the stub test. No DELTA row and no signature are needed, because no Lean, Rust or Python
product code in this repository changed.

## The item

Task: prompts/task-gate-train-tag-reuse.txt. Row note: "pass $out.old-$t0 to tm-inventory when a[2] == $out, plus a stub
test". Found 2026-11-05 at the pc-1g F3 restart (reviews/dri-decisions-20261105-pc-1g-f3.md item 1, worked around with a
new tag).

**The bug.** `gate-train.sh` writes a targeted record to `out=$M/reviews/tm-targeted/<n>-<tag>.json`. Before the
targeted run, it moves an existing `$out` aside to `$out.old-$t0`. When the barrier's STALE record (`a[2]`) is that same
`$out`, an older script then passed the vanished path to `tm-inventory.py apply`. That path raised
`FileNotFoundError`, and the run stopped with "targeted inventory refused".

**The installed fix**, in `gate-train.sh` lines 25-26 and line 12 (`tmback`):
```
tmold=""; if [ -f $out ]; then tmold=$out.old-$t0; mv $out $tmold; for s in inventory ruling; do [ -f $out.$s.json ] && mv $out.$s.json $out.old-$t0.$s.json; done
  [ "$a[2]" = $out ] && a[2]=$out.old-$t0; fi
```
`tmback` moves the record and its sidecars back to `$out` when the run writes no new record.

## The stub test (new file, outside this repository)

`/home/seyran/code/manage-agents/test-harness/gatetrain/test-gatetrain.zsh` (86 lines; full text in `new-test.diff`;
sha256 in `sha256.txt`). It is the first harness for `gate-train.sh`: the task's "existing tests" of `gate-train.sh` do
not exist, so it sits next to the other stub harnesses in `test-harness/`. It follows `test-harness/trustmut`'s pattern.
- `sed` points `M=` at a mktemp scratch, so no real record, inbox or train is touched.
- These are stubs: `tm-barrier.py` (STALE `<record>` on its first call, covers HEAD after), `tm-inventory.py`,
  `msg.sh`, `mac-pytest.sh`, `chain-gate.sh`, `merge-train.sh`, and `uv` (HOME points at the scratch).
- The stub `tm-inventory.py` reads the record it is given with `json.load(open(rec))`, as the real one does. A missing
  file therefore fails the same way the real run did.
- git is real: W is a scratch repository on `main`.

Usage: `zsh test-harness/gatetrain/test-gatetrain.zsh [script]` (default: the installed `gate-train.sh`).

| # | Case | Checks |
|---|---|---|
| 1 | **The row's test.** A rerun with the same tag whose STALE record is that tag's own `$out` | tm-inventory reads `$out.old-<t0>` (the old record's marker, sidecar beside it). The call names `$out.old-<t0>` as the record and `$out` as the output. There is no stop and the train runs. The new record is at `$out`, and the old one sits with both sidecars at `.old-<t0>` |
| 2 | The same rerun when the inventory writes no new record | tm-inventory still reads the old record. `tmback` puts the record and both sidecars back at `$out` |
| 3 | Opposite direction: a new tag (the pc-1g workaround) | the earlier tag's record is read in place and never moved. The new record is written at the new tag's path |
| 4 | Opposite direction: `$out` exists but the STALE record is another one (a tracked docs/ record) | `a[2]` is passed through unchanged |

## Results

| Run | Result | Log |
|---|---|---|
| `zsh test-harness/gatetrain/test-gatetrain.zsh` (installed `gate-train.sh`, sha256 `7383a13e…`) | 9 passed, 0 failed, rc 0 | `run-installed.log` |
| the same on `gate-train.sh.bak-20261108etsync` (before the fix) | 3 passed, 6 failed, rc 1. Case 1 reproduces the incident verbatim: `tm-inventory zz: FileNotFoundError: [Errno 2] No such file or directory: '…/reviews/tm-targeted/zz-t1.json'`, then `msg dri gate-train zz: targeted inventory refused: FileNotFoundError…` | `run-pre-fix-etsync.log` |
| the same on `gate-train.sh.bak-20261108etsync2` (redirect present, no `tmback`, no `--base`) | 7 passed, 2 failed: case 2's move-back, and case 1's call-shape check (that version has no `--base`) | `run-pre-fix-etsync2.log` |

**Deviation from the task's HOW.** The HOW says "Tests FAIL on the installed code and PASS on the staged one". The
installed code already holds the fix, so there is nothing to stage and no `.new-gatew` file. The tests pass on the
installed code. They fail on the pre-fix backup, which is the code the row was filed against (table above).

## Seeded bugs (`seeded-bugs.json`, logs `seed-<id>.log`)

Each seed is a one-line edit of a `/tmp` copy of the installed `gate-train.sh`. Each copy passes `zsh -n`. The live file
was not edited: its sha256 is in `sha256.txt` and matches the "installed" run.

| Seed | Bug | Harness |
|---|---|---|
| s1-no-redirect | drop `[ "$a[2]" = $out ] && a[2]=$out.old-$t0` | 4 passed, 5 failed |
| s2-sidecars-stay | move the record without its sidecars | 6 passed, 3 failed |
| s3-no-tmback | `tmback` does nothing | 8 passed, 1 failed |
| s4-redirect-always | redirect `a[2]` even when it is not `$out` | 8 passed, 1 failed |

## Repository checks

- Selected tests: `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on 24f9050892. It ran 10
  units with 0 failed, exit 0 (`selected-run.log`). The branch changes only `docs/infra/gate-train-tag-reuse/`.
- Trust mutants: `light-lane.py check` printed `NOT 464 changed lines outside generated files > 150 (11 files)`. All of
  those lines are this directory's evidence logs, and no trusted-core file changed. The sweep's plan is empty, so no
  sweep was run: `tools/trust_mutants.py --base <merge-base> --plan` printed `"definitions": 0, "mutants": 0`
  (`trust-mutants-plan.log`).
- The full gate is not run here. The chain runs it on the final HEAD.

## SIZE

SIZE: 0 product, 86 tests (`test-gatetrain.zsh`), about 190 other hand-written lines (this report and `seeded-bugs.json`).

## Notes for the DRI

- No install, so no `msg.sh dri "install read"` was sent (builder-overrides rule 2: no FYI messages). The new harness is
  a new file that no loop runs.
- A run killed with SIGKILL between the move and `tmback` leaves `$out` missing and `$out.old-<t0>` behind, and
  `tm-barrier.py`'s glob (`<item>-*.json`) does not match `.old-<t0>`, so the next run judges only the records still
  in place. UNVERIFIED: read from the code, not probed. This is outside this row and not filed.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer is added or changed.
2. PASS: the row's two deliverables. The fix was already installed; `run-installed.log` shows 9 passed. The stub test is
   `test-gatetrain.zsh` case 1. Breaking the task's HOW (no staged file) is explained under "Deviation".
3. PASS: the tests can fail. `run-pre-fix-etsync.log` has 6 failed, and seeds s1-s4 each fail at least one check
   (`seed-*.log`).
4. N.A.: no Python, Lean or Rust code changed.
5. N.A.: no R8 binding.
6. PASS: evidence and HEAD match. `selected-run.log` is from the committed tree. The full gate runs in the chain on the
   final HEAD.
7. PASS: no unsigned item is left. There is no DELTA row and no signature; the item is docs only (`git diff --stat main...HEAD`).
8. N.A.: no user-visible change in VE.
9. PASS: test selection still works. `selected-run.log` (10 units, 0 failed) shows `select_tests` ran on this branch.
10. N.A.: no Lean.
11. PASS: limits are untouched. `gate-train.sh`'s budgets (TM_TARGETED_BUDGET, TM_TARGETED_RETURN) are not touched.
    The harness has no sleep or timeout.
12. N.A.: no product code. The harness runs in under a minute (the four runs above).
13. N.A.: no test is removed or renamed.
14. PASS: both directions are tested. Case 1 and case 2 are the same-tag redirect; cases 3 and 4 are records that must
    not be redirected or moved. Seed s4 kills the "always redirect" mutant. Every claim cites a log in this directory.
    Spec re-read: "pass $out.old-$t0 to tm-inventory when a[2] == $out" against BACKLOG.jsonl row
    gate-train-tag-reuse and `gate-train.sh:26`: the condition and the path match exactly.
15. PASS: no overclaim. The universal words here ("no install", "never edited", "0 mutants") each cite
    `sha256.txt`/`run-installed.log` or `trust-mutants-plan.log`. Nothing was cut. Every new check has a seed. N.A. for
    limits.
