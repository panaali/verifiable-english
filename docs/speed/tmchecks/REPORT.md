# speed-tmchecks: carry trust_mutants verdicts across a check-only change

No DRI signature is needed: DELTA.md has no rows (tooling only), and trust is +0 (no Lean change).

Infra item speed-tmchecks (acting DRI dri-improve, 2026-10-26 12Z; PIPELINE-LIMITS L102, follows L91). The tool is
`tools/trust_mutants.py --rescore PREV.json`; the tests are in `tests/test_trust_mutants.py`. Section 1's numbers
are saved with the batch (D4): `measure.md` (from `measure.py`), `replay-tmrerun.json` and `replay-tools.json`
(from `replay.py`), and the two sc-1b evidence files in `evidence/`. The seeded bugs are in `mutants.json`, with
their results in `mutants-evidence.json`.

## 1. Measure (step 1)

### 1a. Consecutive sweeps of one item, Oct 20-26

`measure.py` reads every committed version of each item's evidence JSON on all refs (git only reads), one run per
distinct blob, and sc-1b's three reruns (sc-1b committed its evidence JSON only at its end, at 6ea6dc913). A pair
is check-only when every file that differs between the two heads is a module of lean/ outside every selected
declaration's file and import closure (the second run's `definitions`; the closure read at the second head with
`check_lean_imports.imports`), an outside --test file or a generated inventory, with the same base and options. The
full table, 28 pairs, is `measure.md`. The check-only rows:

| item | first | second | mutants | check-only | second took (min) | files that differ |
|---|---|---|---|---|---|---|
| me-9b | 6369f18b5 | 7c63292cb | 46 | y | 18 | VE/Audit.lean, VE/Calc/IdentityExamples.lean, axioms.txt, declarations.txt, statements.txt |
| sc-1ad | 3eb6bb51a | c1903fd95 | 163 | y | 63 | VE/Scope/Examples.lean, declarations.txt |
| sc-1ad | c1903fd95 | a22ec823c | 163 | y | 55 | VE/Scope/Examples.lean, declarations.txt |
| sc-1ad | a22ec823c | fc0c533ea | 163 | y | 12 | VE/Scope/Examples.lean, declarations.txt |
| sc-1b | b548c10d2 | 34e1a60d1 | 328 | y | 60 | VE/Compose/Examples.lean, VE/Scope/WireExamples.lean, VE/Service/ScopeExamples.lean, declarations.txt |
| sc-1b | 34e1a60d1 | 5a0051f93 | 328 | y | 67 | VE/Scope/WireExamples.lean, declarations.txt |
| sc-1b | 5a0051f93 | 24504cdd5 | 328 | y | 79 | VE/Scope/WireExamples.lean, declarations.txt |

Every other pair is n: 15 changed a selected declaration's file or its closure (a definition, or a theorem or
check added to the definitions' own module, as df-1ac's 6bd8247b0 -> f484e28cc did: speed-tmrerun carried 84 of 90
there, but this item's narrower rule gives it a full run), 2 changed the base and options, and 4 had identical
inputs (speed-tmrescore's case). The seven check-only reruns took 354 min (5.9 h), over the 2 h stop line. sc-1b's
times are as the task gives them for the first two; the third is its evidence's `seconds` (4761, Mac, `--jobs 6`,
load 38-42).

### 1b. Replay on sc-1b 5a0051f93 -> 24504cdd5, and its check against the full sweep

`replay.py` checks out both commits detached in a scratch directory (feature/sc-1b is only read), plans each
(`plan`, no build), matches the saved 5a0051f93 rows to the first plan (all 328, by position), computes what each
KILLED and INVALID verdict reads on the first tree and carries it where that reads the same on the second.

| rule | mutants | carried | rerun | why rerun |
|---|---|---|---|---|
| rule.py (infra/speed-tmrerun, `--rule tmrerun`) | 328 | 285 (237 KILLED, 48 INVALID) | 43 | 12 raw SURVIVOR, 31 raw UNKNOWN (all ALLOWED): never carried |
| the rule as moved into the tool (`--rule tools`) | 328 | 285 (237 KILLED, 48 INVALID) | 43 | the same |

The change added one `#guard` to `WireExamples.lean` (lines 148-151) and regenerated `declarations.txt`. Two kills
(M019, M051) were at the check it pushed from line 148 to 152: they were carried with their line followed. The other
235 KILLED name checks above it (161 in `WireExamples.lean`) or in two other files (`Service/ScopeExamples.lean` 53,
`Compose/Examples.lean` 21). 285 of 328 is 87%, over half.

Validation. sc-1b's own full sweep at 24504cdd5 finished at 13:44Z (`evidence/sc-1b-24504cdd5.json`: 239 KILLED,
48 INVALID, 41 ALLOWED, 0 left, 4761 s; copied from its commit 6ea6dc913, byte-equal to its worktree's file). With
`--full` the replay compares every carried verdict with that run's status before --allow:
- 0 of 285 differ in status, and all 285 name the same killing file:line.
- Of the 43 that rerun, the full run gave 10 SURVIVOR, 31 UNKNOWN and 2 KILLED. The 2 (M218, M326: `byStatus`
  list cuts) are former ALLOWED survivors that the new check at line 148 kills, which is why a SURVIVOR always runs.

So none of the three stop rules applies (check-only reruns 5.9 h > 2 h; 87% carried; no carried verdict differs).

With the carry, sc-1b's third sweep runs 43 mutants and the control build instead of 328: at that run's own pace
(4761 s for 328 at 6 jobs) about 10 min plus the control build, instead of 79 min.

## 2. Orchestrator lines (not applied here: /home/seyran/code/manage-agents is read only for this item)

1. BUILDER-CHECKLIST.md item 3, the R16 sub-bullet: replace "After an allow-only edit or for UNKNOWNs, rerun with
   `--rescore <the last evidence JSON>` (it reuses verdicts only on byte-identical inputs; the PREV must be in the
   worktree); a code change still needs a full run." with:
   `After an allow-only edit or for UNKNOWNs, rerun with --rescore <the last evidence JSON> (identical inputs reuse
   every verdict); after a fix that only adds or changes checks, rerun with --rescore <the last evidence JSON>
   (check-only carry); a change to a trusted definition or what it imports still needs a full run. The PREV must be
   in the worktree.`
   In the same bullet, replace `"reused_from": <head> and records "rescore": {file, head, reused, rerun}` with
   `"reused_from": <head> (and "carried": "checks" when it was carried across a check-only change) and records
   "rescore": {file, head, mode, changed, reused, rerun}` and add `(2026-10-26, speed-tmchecks merged, L102)`.
2. prompts/build-checklist.txt line 13a: the same two replacements (its text is the bullet's).
3. Review prompt, where it tells reviewers to rerun trust_mutants on the HEAD: `Reviewers still run trust_mutants
   on the HEAD without --rescore (a full run) and compare with the committed evidence, reading each mutant's
   reused_from and carried and the rescore block's mode (identical | checks | full) and changed files. A carried
   KILLED that the full run gives otherwise is a finding: the carry does not look for a new check that the mutant
   makes fail without a refutation.`
4. mac-pytest.sh needs no change: since Oct 21 its `--trustmut` loop passes `--rescore` through unchanged as a
   worktree-relative path (line 92 lists it among the options with a value, line 98 maps it into the worktree and
   refuses a path outside it). PREV must be in the snapshot (tracked, or untracked and not ignored).

## 3. What was built (step 2)

**Per-file digests.** `inputs()` keeps its five overall digests and adds `files`: the sha256 of each file the
`lean` and `tests` digests read (every file of lean/ that `Scratch` copies, trust_map's table, `.gitignore`, the
outside --test files), by root-relative path. `__pycache__` under lean/ is no longer digested: Lean never reads it,
and its bytes differ between machines (speed-tmrescore review F1). On this repository a run's JSON gains 654 file
digests (67 KB with no mutants).

**What each verdict reads.** Every `--json` records, on each KILLED and INVALID mutant (by `raw_status`), `reads`
(a digest) and, for a KILLED one, `killed_at` (its killing check's lines). `Reads` is speed-tmrerun's rule.py,
moved into the tool, with one addition: a kill carries only while its check's module is still one the mutant's
build reads (`targets`).

**`--rescore PREV.json`, mode "checks".** When PREV's mutant rows are this plan's and the tool, base and options
are the same, and every file whose digest differs is a module of lean/ outside every selected declaration's file and
import closure (`reach`), an outside --test file, or a generated inventory (`declarations.txt`, `statements.txt`,
`predicates.txt`, `axioms.txt`) (`check_only`), PREV's KILLED and INVALID verdicts whose reads read the same are
carried (`Reads.carry`). Each carried mutant gets `reused_from: <PREV head>` and `carried: "checks"`; a carried kill
names its check where it now is. Every other mutant runs: SURVIVOR, UNKNOWN and ALLOWED ones (a new check may kill
them), NOT RUN ones that fit, and a KILLED one whose killing check, the counted lines before it or what its file
imports changed. Any other change (a lakefile, toolchain, docs file, trust_map's table, a selected file or its
closure), a PREV without per-file digests, or an unreadable PREV is a full run, with one line saying why:
`trust_mutants: --rescore PREV: a full run, since its inputs differ (lean): lean/X is a selected declaration's file
or in its import closure`.

**What did not change.** Identical inputs reuse as before (mode "identical"). `rescore` gains `mode` and `changed`;
the summary ends `; N reused from <head> (identical inputs)` or `; N carried from <head> (check-only change:
<files>)`. The control build runs whenever at least one mutant runs. The exit codes are unchanged, and a mutant
that runs keeps today's verdict rules (`run` is unchanged). The module docstring states what a carried KILLED stands
on: its unchanged check's refutation. A new check that the mutant would make fail some other way is not looked for,
which is why reviewers run without --rescore.

## 4. Tests (step 3), on the tiny synthetic package

| Rule | Test |
|---|---|
| a check module added (it kills every former SURVIVOR of `evens`, which are built) and a killing check edited (`half_four`: its 2 mutants rerun): every other KILLED and INVALID carried, `reused_from` + `carried`, `rescore` mode checks with the changed files, the summary line; every verdict equals a full run's on the same tree | `test_rescore_after_a_check_only_change_carries_the_kills_it_reads_the_same` |
| `Reads`: a kill carries when nothing changed and when a check is added above it (its line follows); not when a definition is added above it, its check is edited or the closure changes, nor when the build no longer reads its check; INVALID carries unless the closure changes; a SURVIVOR never | `test_a_verdict_carries_only_while_what_it_reads_reads_the_same[none, check-added-above, definition-added-above, check-edited, closure-edited]` |
| `reach` is the selected files and their import closure; a change to either, a lakefile, toolchain, docs file, trust_map's table or an undeclared outside file is no check-only change | `test_a_check_only_change_lies_outside_every_selected_file_and_its_closure` |
| per file: a check file, `statements.txt` or an outside --test file is mode checks; `__pycache__` changes nothing; a selected file, the lakefile or trust_map's table, or another tool, `--deep`, `--test` or base (each beside a check-only change), or PREV without per-file digests is a full run | `test_any_changed_input_but_checks_gives_a_full_run[...]` (12 cases; renamed from `test_any_changed_input_gives_a_full_run`, with a Test-removed trailer) |
| identical inputs: today's path, now `mode: identical, changed: []` | `test_rescore_after_an_allow_only_edit_builds_nothing`, `test_rescore_runs_the_not_run_mutants_that_now_fit`, `test_rescore_reruns_only_the_unknown_mutants` |
| PREV's `reads` and `killed_at` are typed (a number, a one-item or bool-item list refused) | `test_rescore_of_evidence_whose_mutants_differ_is_a_full_run` |

The selected tests (`mac-pytest.sh --select`, 110 units, ran on the VM: no Mac slot) passed: 0 failed.

### Seeded bugs (Python: the only language changed)

`uv run python tools/mutants.py docs/speed/tmchecks/mutants.json` gives 14 of 14 killed (`mutants-evidence.json`,
each baseline passing first). The tool's sha256 was the same before and after (`8c069194...`, the final tool).

| Id | File | Bug | Failing test |
|---|---|---|---|
| TC1 | tools/trust_mutants.py | a SURVIVOR carried | `test_rescore_after_a_check_only_change_carries_the_kills_it_reads_the_same` |
| TC2 | tools/trust_mutants.py | the killing check's own text not compared | `test_a_verdict_carries_only_while_what_it_reads_reads_the_same[check-edited]`, the end-to-end test |
| TC3 | tools/trust_mutants.py | the lines before the killing check not compared | `...[definition-added-above]` |
| TC4 | tools/trust_mutants.py | a moved check's line not followed | `...[check-added-above]` |
| TC5 | tools/trust_mutants.py | `reach` without the import closure | `test_a_check_only_change_lies_outside_every_selected_file_and_its_closure` |
| TC6 | tools/trust_mutants.py | `reach` without the selected files | the same |
| TC7 | tools/trust_mutants.py | another tool allowed in mode checks | `test_any_changed_input_but_checks_gives_a_full_run[tool]` |
| TC8 | tools/trust_mutants.py | another base or option allowed | `...[base]`, `...[deep]`, `...[test-option]` |
| TC9 | tools/trust_mutants.py | PREV without per-file digests read as having this run's | `...[no-files]` |
| TC10 | tools/trust_mutants.py | any file under lean/ taken as a check module | the check-only test, `...[lakefile]` |
| TC11 | tools/trust_mutants.py | `carried` not written | the end-to-end test |
| TC12 | tools/trust_mutants.py | a kill carried when the build no longer reads its check | `...reads_the_same[none]` |
| TC13 | tools/trust_mutants.py | `__pycache__` digested again | `...[pycache]` |
| TC14 | tools/trust_mutants.py | identical inputs reported as mode checks | `test_rescore_after_an_allow_only_edit_builds_nothing` |

## 5. Rules kept

- R2 (the merge train's full live gate) and R3 (the nightlies) are unchanged. No gate, train or nightly reads
  trust_mutants or its evidence (`git grep -l trust_mutants tools/gate.py` is empty); it stays builder and reviewer
  evidence only.
- No Lean, `ve/` or `rust/` change; trust +0. DELTA.md has no rows.
- Load: one real-tree sweep was needed and not run by this item: sc-1b's own full sweep at 24504cdd5 finished in
  time and is the validation. The replay plans only (no build); the other runs are the synthetic package.
- Size: the tool has +199/-36 lines and the tests +167/-19, about 420 changed lines against the task's ~300. About
  90 of the tool's are rule.py's `Reads`, moved in as the task asks; the tests are 3 new functions (one end to end)
  and the rework of one parametrized test.
- Sibling lessons (speed-tmrescore review): F1 (`__pycache__` in the `lean` digest) is fixed here, since a `.pyc`
  would otherwise read as a changed file (TC13). F2 (`--max-mutants` left out of the digest) is unchanged: the limit
  picks which mutants run, never a verdict, and NOT RUN mutants always run when they fit.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; the tool reads its own evidence JSON, and `previous` types every field it
   reuses or carries and refuses anything else (`test_rescore_of_evidence_whose_mutants_differ_is_a_full_run`).
2. PASS: steps 1-4 delivered (sections 1-4; commits on this branch; task directive lines in section 3). No permanent
   report test (D4): section 1's numbers are saved files, read by no test.
3. PASS: 14 of 14 seeded bugs killed, one per rule (`docs/speed/tmchecks/mutants-evidence.json`). The R16
   trust_mutants run is N.A. (no Lean change).
4. N.A.: no Python/Lean/Rust parity path changes.
5. N.A.: no relayed field. PREV's rows are bound to the plan by id, file, line, definition, operator, before and
   after, and a carried kill to a check the build still reads (`test_a_verdict_carries_only_while_what_it_reads_reads_the_same`, TC12).
6. PASS: synced with main (merge 8d70b75e7; base 058fea806); the chain runs the gate on the final HEAD. Section 1
   reads committed history and saved evidence only.
7. PASS: DELTA.md has no rows and no reserved signature; trust +0.
8. PASS: no VE output changes (no `ve/`, `lean/`, `rust/` or `conformance/` file in `git diff main...HEAD`).
9. PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects 110/461 units, `tests/test_trust_mutants.py`
   among them; TC1-TC14 fail there.
10. N.A.: no Lean statement or proof.
11. PASS: a carried verdict is never UNKNOWN-derived: only KILLED and INVALID carry, and an UNKNOWN (a timeout, a
    budget) always runs (`test_rescore_reruns_only_the_unknown_mutants`; TC1 for SURVIVOR). The tests use no sleep
    and no fixed deadline.
12. N.A.: no VE runtime path; the change removes rebuilds (section 1b).
13. PASS: one test function renamed, with its trailer (`Test-removed: tests/test_trust_mutants.py::test_any_changed_input_gives_a_full_run — ...`);
    after `lake build`, `tools/gate_collection.py --check --prebuilt` reports 19 added, 8 removed by a trailer, 0
    refused, 0 stale and 0 malformed.
