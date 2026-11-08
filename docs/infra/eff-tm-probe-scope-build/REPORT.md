# eff-tm-probe-scope-build: probe only the checks a verdict reads

- **Status:** built as section 8 of reviews/eff-tm-probe-scope-design-20261031.md (manage-agents) describes, with the
  adjudicated review changes. Branch `infra/eff-tm-probe-scope-build`, synced with main (merge 35675df5b). The full
  gate was not run here; the chain runs it on the final HEAD.
- **What changed:** tools/trust_mutants.py only, plus its tests (tests/test_trust_mutants_probe_scope.py) and the
  regenerated tests/history-dependent.json. A mutant's probe walks only the checks `settle` hands over and drops the
  text after the last of them. Control probes are still whole-file.
- **Verification:** a qt-a3d 493da762 sweep with the shipped probe gives the same verdicts as
  `reviews/eff-tm-probe-scope-evidence/qta3d-dual.json` for all 69 mutants (status, raw_status and detail), with no
  fallback. Probe Lake time fell about 89% on this sweep, against the design's paired 46-75%.
- **Open items / signatures:** none. No DELTA rows, no trusted Lean line changed, no DRI signature reserved.

## Deliverables (design section 8 and the task)

| row | commit | test |
|---|---|---|
| READS: the `TM_TRUST_ONLY` gate is the walk's first statement | e6042cfa0 | `test_the_walk_reads_and_prints_only`, `test_a_cut_that_changes_a_parse_fails_closed_in_lean` |
| READS: `<k> done` is the walk's last line | e6042cfa0 | `test_the_walk_reads_and_prints_only`, `test_a_cut_that_changes_a_parse_fails_closed_in_lean` |
| `probe(only=...)`: the truncation (`kept`) | e6042cfa0 | `test_probe_walks_only_its_checks_and_drops_the_text_after_them`, `test_kept_cuts_at_the_line_before_the_next_command` |
| the keys come from `settle` (`scope=`), and reading raises on a key it was not given (`Probes`, `LookupError`) | e6042cfa0, b19c47f2d | `test_reading_refuses_a_key_settle_did_not_hand_over`, `test_settle_hands_its_keys_over_before_its_first_read`, and the seed test's `refused` rows (32 of 32 settle calls in the real tool) |
| an entry without `done` is absent, in the control and in the mutant's probe (`complete`, `refusal`) | e6042cfa0, b19c47f2d | `test_an_entry_without_its_done_marker_is_absent`, `test_probe_keeps_an_entry_whose_walk_did_not_finish_without_done` |
| fallback to the whole-file probe | e6042cfa0, b19c47f2d | `test_a_check_of_the_set_with_no_whole_entry_is_read_from_the_whole_file` (5 cases), and the seed test's `cut-1` mode (13 fallbacks) |
| F1/F2 in the docstring (UNKNOWN -> KILLED only where the whole file's probe gives no entry) | e6042cfa0 | the module docstring, the paragraph after the verdict list |
| the control probes stay whole-file | unchanged code in `main` | the seed test: every control row has `only` None, in all 5 modes |
| the dual mode is not shipped | n/a | dual, off, cut-1 and naive exist only in the seed test's `WRAPPER` (tests/test_trust_mutants_probe_scope.py) |
| the seed package as a real-Lean test, all 5 modes, with the negative controls | e41e069f9 | `test_the_scoped_probe_classifies_the_seeds_as_the_whole_file_probe` |
| a test over the READS text (gate first, no effects, `thmInfo` excluded) | e41e069f9 | `test_the_walk_reads_and_prints_only` (1 accept case, 9 negative-control edits) |
| the F3 truncation unit cases (`mutual … end`, `where`/`termination_by`, a docstring before the next command, `set_option … in`, a multi-line `#guard`) | e41e069f9 | `test_kept_cuts_at_the_line_before_the_next_command` (8 cases), `test_a_cut_that_changes_a_parse_fails_closed_in_lean` (the same shapes in Lean) |
| a forced fallback | e41e069f9 | `test_a_check_of_the_set_with_no_whole_entry_is_read_from_the_whole_file`, seed mode `cut-1` |
| the `done` marker required | e41e069f9 | `test_an_entry_without_its_done_marker_is_absent` |

## Design notes

- **One deviation from the prototype:** `probe(only=...)` runs no Lean when none of the set's checks can be probed
  by `named`. The whole-file probe has no entry for them either, so `refusal` returns the same reason
  (`test_probe_walks_only_its_checks_and_drops_the_text_after_them`, the `(3, 3)` case).
- **`Probes.scope` re-probes a file** if `settle` hands over a key of that file after the file was probed. That
  cannot happen today, because each file is settled once, but the check fails closed if it ever does
  (`test_reading_refuses_a_key_settle_did_not_hand_over`).
- **F3 in Lean** (`test_a_cut_that_changes_a_parse_fails_closed_in_lean`, run locally: 1 passed in 58 s). Probed
  alone, each of the 8 checks gives exactly the whole file's entry. That includes the `mutual` block a cut leaves
  open: Lean 4 elaborates it anyway. The test still lets that case be absent, because then the fallback covers it.
  A cut one line early changed 4 entries, and `refusal` refuses each one.

## Verification sweep (qt-a3d 493da762)

- **Tool.** The sweep used eff-tm-control's tool 97c9c4f4a, which the design's runs also used, with this branch's
  diff (`git diff main HEAD -- tools/trust_mutants.py`) applied. All 13 hunks applied cleanly. The tool was swept
  in a scratch worktree at 493da762, which has since been removed.
- **Command and record.** The sweep ran with
  `zsh mac-pytest.sh --worktree <scratch> --trustmut -- --max-mutants 1000 --base 1f28dddfb3ef480ba7680d6a7c51cb801e9cb876 --allow docs/quantities/qt-a3d/trust-mutants-allow.json --json …`.
  It went to 6 GitHub Actions parts, and cloud-pull merged them. The cloud snapshot was commit 28101c765, whose
  parent is 493da762, and its `tools/trust_mutants.py` has sha256 bd7543ee0f509d76…, the same as the patched
  tool's. The record is saved as `docs/infra/eff-tm-probe-scope-build/qta3d-scoped.json`.
- **Compared with** `/home/seyran/code/manage-agents/reviews/eff-tm-probe-scope-evidence/qta3d-dual.json`, using
  the evidence's own `cmp.py` (output in `docs/infra/eff-tm-probe-scope-build/compare.txt`):
  > 69 mutants; plan differs []; status/raw_status differs []; counts {'KILLED': 60, 'SURVIVOR': 0, 'UNKNOWN': 0,
  > 'INVALID': 4, 'ALLOWED': 5, 'NOT RUN': 0} vs the same; detail differs: 0
- **Verdicts:** identical for every mutant. No F1 or F2 case occurred on this sweep.
- **No fallback:** `steps.runs.mutant_probes` is 60, which is one probe run per kill.
- **Probe-time saving, measured on this sweep** (from `compare.txt`):
  - This sweep: mutant probes took 1,111 Lake-s for the 60 kills. eff-tm-control's whole-file record of the same
    commit and options (`git show 97c9c4f4a:docs/speed/tm-control/evidence.json`, runs[2]; VM, `--jobs 4`) took
    10,816 Lake-s. That is a raw saving of 89.7%.
  - Normalised by the step this change does not touch (mutant_checks: 9,183 vs 9,716 Lake-s), the saving is 89.1%.
  - The probes' share of Lake time went from 51.8% to 10.4%.
  - **Caveat:** the two runs are not paired. They ran on different machines (6 Actions runners, 24 jobs, against
    the VM's 4) and under different load. The design's paired figure for qt-a3d was 75%, and 46-75% over its two
    runs. jt-2c was not swept.

## Tests run

- `uv run pytest -q tests/test_trust_mutants_probe_scope.py -k "not seeds and not fails_closed"`: 28 passed.
- The same file `-k fails_closed`: 1 passed (58-67 s).
- The same file `-k seeds`: 1 passed in 775.90 s. Mode summary of that run:
  - 51 mutants in each mode.
  - off, on, dual and cut-1 each gave KILLED 22, UNKNOWN 20, SURVIVOR 9.
  - cut-1 fell back 13 times.
  - naive gave KILLED 27, UNKNOWN 15: the wrong design changes S1, as the negative control requires.
- The selected tests ran once, on finished code before the main merge:
  `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`. It ran on GitHub Actions in 3 shards:
  38 units, all passed, exit 0.
  - All 4 chunks of tests/test_trust_mutants.py ran there: 145 + 279 + 140 = 564 passed, 0 failed.
  - tests/test_trust_mutants_probe_scope.py ran in shard 1 and passed.
  - tests/test_hang_guards.py was in the run.
- After the main merge, `uv run python tools/regen_generated.py --check` checked 35 entries and found none stale.
  The merge touched none of this branch's files, and the selected tests were not rerun after it.
- **Not run:**
  - the full gate (the chain runs it);
  - lake build and lean/audit.py (no Lean under lean/ changed);
  - trust_mutants on this branch (no trusted Lean changed).

## Seeded bugs (docs/infra/eff-tm-probe-scope-build/seeded-bugs.json)

Each bug was planted alone in tools/trust_mutants.py and run against the one test named, then restored with
`git checkout`.

| id | lang | change | test that fails |
|---|---|---|---|
| S1 | Python | `Probes.__call__` accepts an ungiven key | `test_reading_refuses_a_key_settle_did_not_hand_over` (1 failed) |
| S2 | Python | `settle` no longer calls `scope` | `test_settle_hands_its_keys_over_before_its_first_read` (1 failed) |
| S3 | Python | `Probes` never falls back | `test_a_check_of_the_set_with_no_whole_entry_is_read_from_the_whole_file` (3 failed) |
| S4 | Python | `refusal` checks presence, not `done` | `test_an_entry_without_its_done_marker_is_absent` (1 failed) |
| S5 | Python | `kept` keeps the next command's first line | `test_kept_cuts_at_the_line_before_the_next_command` (7 failed) |
| S6 | Python | `TM_TRUST_ONLY` not set | `test_probe_walks_only_its_checks_and_drops_the_text_after_them` (1 failed) |
| S7 | Lean (READS) | gate inverted: walks the checks not named | `test_a_cut_that_changes_a_parse_fails_closed_in_lean` (1 failed: `{(5, 5)} <= {(6, 6)}`, so a check outside the set was walked) |
| S8 | Lean (READS) | `say "done"` removed | `test_a_cut_that_changes_a_parse_fails_closed_in_lean` (1 failed) |

## Rulings

- **No DELTA rows.** The tool's output format is unchanged. Its verdicts are the same except in F1/F2, where an
  UNKNOWN can become KILLED (design section 8, Rulings); the verification sweep had no such case.
- **READS is the tool's own probe module**, not lean/. No file under lean/ changed (`git diff --stat main...HEAD`:
  tests/history-dependent.json, tests/test_trust_mutants_probe_scope.py, tools/trust_mutants.py). So there is no
  trusted-line change to record under R16/R6. This item reserves no DRI signature.

## Spec re-read

- "`TM_TRUST_ONLY=<the set's tmChk names>`. `tmTrustWalk` returns as its first statement when its check is not named
  there" against design 2.2: READS lines 2-3 of `tmTrustWalk`; `hyps` and `synthInstance` stay before the walk.
- "Truncation. The text after the set's last check is dropped, cut at the line before the next command in `roles`"
  against design 2.2: `kept`.
- "`settle` compute them once and hand them to the probe before its first `reads` call … `reading` must raise on
  any key it was not given" against design 2.1 and review 2: `settle(..., scope=)`, `Probes`.
- "an entry without it counts as absent, in the control and in the mutant's probe alike" against design 2.4:
  `refusal` (`complete(entry)` and `complete(control)`).
- "Fallback … when any check of the set that `named` can probe has no complete entry in the scoped output, or the
  scoped run timed out" against design 2.5. A timed-out run prints no nonce line, so every check is absent.
- "The control probes are unchanged: whole file, all checks, up front" against design 2.3: `main`'s `control` still
  calls `probe` without `only`.
- "F1 and F2 … only from UNKNOWN to KILLED where today's UNKNOWN came from a probe that did not finish" against
  design 4: the docstring paragraph.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean service answer or relayed route is touched (a tool's probe output only).
2. PASS: every section 8 row maps to a commit and a test in the Deliverables table. The grep of the diff shows no
   new Python copy of a Lean decision and no report test; the only generated file is regenerated
   (tests/history-dependent.json, by `tools/regen_generated.py --write`).
3. PASS: seeded bugs S1-S8 (`seeded-bugs.json`). The seed test's negative controls `cut-1` and `naive`, and the
   READS-text test's 9 edits, all fail as intended.
4. N.A.: no Python/Lean/Rust decision path changed. The whole-file vs scoped comparison is the seed test's `dual`
   mode and the qt-a3d sweep (`compare.txt`).
5. N.A.: no relayed Lean answer. The key binding of `reading` is tested both ways
   (`test_reading_refuses_a_key_settle_did_not_hand_over`).
6. PASS: synced with main (35675df5b); the commit list is `git log --no-merges main..HEAD` (5 commits). The gate
   runs on the final HEAD in the chain.
7. PASS: no DELTA rows and no trusted growth (Rulings above).
8. PASS: no user-visible change. The verdicts on qt-a3d are identical (`compare.txt`), and so are the seed
   verdicts across modes (`test_the_scoped_probe_classifies_the_seeds_as_the_whole_file_probe`).
9. PASS: `select_tests` selected tests/test_trust_mutants_probe_scope.py and all of tests/test_trust_mutants.py
   (selected run, 38 units). Each seeded bug fails a test in that selection.
10. N.A.: no Lean theorem or statement changed.
11. PASS: a timed-out or crashed scoped run gives no complete entry, so the tool falls back, and an absent entry is
    UNKNOWN (`test_a_check_of_the_set_with_no_whole_entry_is_read_from_the_whole_file`, the `{}` case). The tests
    use `HANG_TIMEOUT` only (tests/test_hang_guards.py passed in the selected run).
12. PASS: the change cuts probe time (89% on qt-a3d, `compare.txt`). The fallback adds at most one whole-file probe
    per file, and only when the scoped probe left a check without an entry.
13. N.A.: no test removed or renamed.
14. PASS: both directions are tested: given and ungiven keys; complete and partial entries; fallback and no
    fallback; READS as it is and 9 edits; exact cuts and a cut one line early. Every claim in this report cites its
    command or file, and the spec re-read is listed above.
