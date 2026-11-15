# safety-framework-case-alternatives: REPORT

- Status: built, ready for the gate. No DRI signature is needed and DELTA has no rows. HEAD: the commit that adds this file.
- What changed: run.py can give a case alternatives. G3, G7 and G9 now carry every branch their PLAN 5 row names.
  measures-sl2plus now lives in rules.d1.ve, scoped to the seven F16 items, and their records name it.
- Answers: none moved (260/262 before and after; G3, G7 and G9 are ALL before and after). The FACTS/CASES
  exposures went from 3 to 2.
- Open: nothing in this row. The FSF freeze no longer waits on this row.

Ruling: reviews/dri-decisions-20261114-safety-framework-fidelity-fix-3.md items 3 and 5 (SIGNED). Critical path:
reviews/dri-decisions-20261115-adv0223.md item 1.

## Delivered (task DELIVER 1-4)

| Row | Commit | Test |
|---|---|---|
| 1. run.py: one parts-style alternative in the case model | 2aa79f0303 | `tests/test_fsf_case_alternatives.py::test_an_alternative_that_fails_makes_the_item_fail` |
| 2. cases.json: G7 both branches, G3 "or reaching", G9 its TCL half; README G7 row | 2aa79f0303 | `test_g7_states_a_tcl_and_a_mitigated_ccl_risk`, `test_g3_states_approaching_and_reaching_a_tcl`, `test_g9_states_every_tcl_and_ccl_model`, `test_each_alternative_is_answered_and_the_answer_holds_in_every_one[G3,G7,G9]` |
| 3. measures-sl2plus scoped to the F16 items, named in their records | 2aa79f0303 | `test_measures_sl2plus_is_scoped_to_the_items_that_read_it`, `test_the_f16_items_load_the_block_and_their_proofs_use_it` |
| 4. Regenerated with the case's own scripts; every answer old -> new | 2aa79f0303 | `run.py --check` exit 0 (log /tmp/sfca-run2.log: "agreement with the answer key: 260/262") |

### 1. The case alternative (run.py)

- I reused the existing parts shape. A case may list `alternatives`, and `situations(case)` gives one situation per
  alternative. `item_result` evaluates the item on each one and joins them with `intersect_results`, the shape
  SILENT:EVIDENCE already uses. The record keeps every alternative's own result under `alternatives`.
- The rule for "or": a PLAN 5 row "X or Y" has one key cell that answers both X and Y. So the item holds at a choice
  exactly when it holds in every alternative (PLAN 5 "ALL: the item holds under every complete choice",
  PLAN.md:210).
- `case_atoms` refuses a case that has alternatives. Every path that builds a case model must therefore go through
  `situations()`: the premise check (`case_premises`), default sensitivity (rows joined per choice), and N3's
  witness search.
- DM and CCA carry a release set that this join does not compute, so `item_result` refuses alternatives for them.
  No such case exists today.
- Nothing outside run.py's case evaluation was needed for the alternative (no ve/ or lean/ change). STOP question 2
  did not arise.

### 2. The cases (cases.json)

Each branch lists one situation per level of the class it names. The level classes come from facts.d1.ve's level
table (tracked: L1, L5; critical: L2, L3, L4, L6, L7), so the translation picks no level of its own.

| Case | PLAN row | Alternatives |
|---|---|---|
| G3 | PLAN.md:349 "approaching or reaching a TCL" | `approaches(p, l)` for each TCL (2); `reached(p, l)` for each TCL (2) |
| G7 | PLAN.md:353 "disclosure for a TCL or for a mitigated CCL risk" | each TCL, no finding (2); each CCL with `mitigates(p, l)` (OT2) and both OT11 findings unset (5) |
| G9-TCCL | PLAN.md:355 "for T/CCL models" | each TCL and CCL under EXT-NOGOV (7) |

The cases.json `source` note says what an `alternatives` case is. README.md:199 now reads "disclosure for a TCL,
or for a CCL whose risk is mitigated | silent: disclosure needs a CCL with an unmitigated, material risk".

### 3. measures-sl2plus

- The block is now the last block of rules.d1.ve. Its header is `item B-L2/RECSEC, B-L3/RECSEC, B-L4/RECSEC,
  B-L6/RECSEC, B-L7/RECSEC, C1, C4`, and its source and text are unchanged. facts.d1.ve holds the other 14 blocks
  (35 premises).
- translation.py: an item header may now name several items. `facts(item)` gives the blocks that name the item.
  `fact_items()` and `fact_formulas()` give every fact block, so build_document.py can still assert the 2.1.1
  facts as the source document's premise unit `s211-sl2plus`.
- run.py:
  - `own_facts(item)` gives an item's own blocks.
  - `item_case` attaches the item to its case. `case_atoms` then adds the block's facts to the case model, and
    `premise_status`/`PREMISES` check them.
  - C1 and C4 pass them to the conflict prover.
  - `with_own_premises` writes `own_premises: ["measures-sl2plus"]` into the seven records. N1 keeps its own field.
- The F16 proof uses the block. RECSEC details now list the measures that F16 selects. For B-L2 at RS3 = Ds, the
  list is `rand_security_level_2, security_level_2_plus, sl2_plus_additional_measures` with the block, and
  `security_level_2_plus` alone without it (`test_the_f16_items_load_the_block_and_their_proofs_use_it`).
- Which items read the block. The item records that name f16-ds or f16-ds-strict on main are the seven items
  above plus N3. N3's witness for each F16 rule comes from a level that recommends the measure itself, so N3 does
  not load the block, and its witnesses are the same as on main. G8 (SILENT:EVIDENCE), C-doc and N3 still evaluate
  the F16 rules, but without the block. Measured on main with the block taken out of facts.d1.ve (a scratch run,
  /tmp/sfca-results-nosl2.json): the only change in results.json was `cost.premises`. So no record of any item
  changes without the block.
- invention_audit stays true. `untraced` now also checks the item-scoped fact blocks and is still `[]`, and
  `bridges` is still `["bridge-one-domain"]`.
- The counter agrees: `uc-audit.fsf_prepare` lists `measures-sl2plus` as a unit used by exactly the seven items.

### 4. Regeneration and answers

- results.json: `run.py` (log /tmp/sfca-run1.log), then `run.py --check` exit 0 (/tmp/sfca-run2.log), 260/262.
- coverage.json and spans.json: `build_document.py --source <copy>`. Both are byte-identical to main (git diff
  empty), so the built document is the same.
- readings/results.json: `readings_r1.py`, unchanged.
- `tools/regen_generated.py --check`: exit 0, 41 entries checked, so no `--write` was needed.
- Every answer, old -> new (results.json comparison, main ce3fe4ed34 against this branch): 262 rows, 0 moved.

| Item | Key | Old | New |
|---|---|---|---|
| G3 | ALL | ALL | ALL |
| G7 | ALL | ALL | ALL |
| G9 | FORBIDS ALL; FORBIDS@G9-L0 SOME(U) | ALL; SOME(RS2=U) | ALL; SOME(RS2=U) |

Records that changed in results.json, with no answer change:
- The B-L*/RECSEC details gained `measures`.
- Seven records gained `own_premises`.
- G3, G7 and G9 gained `alternatives`.
- C1 and C4: `own_premises` only.
- `variants.with_N2` (B-L2/RECSEC `measures`), `cost.premises` 39 -> 35, `cost.case_models`.

## exposure.py (CASES and FACTS)

Before (`exposure.py safety-framework ce3fe4ed34`, main):

The quoted sentence of the report lines is shown by its place, not repeated (repeating it here would add the same
records again).

```
counter sha256 f4345f44  case safety-framework  commit ce3fe4ed34  state run
FACTS <- measures-sl2plus     plan12       | - **Facts.** `measures-sl2plus` states 2.1.1 as written:
FACTS <- FACTS                report       | <the sentence at safety-framework-fidelity-fix-2/REPORT.md:213>
CASES <- CASES                report       | <the sentence at safety-framework-fidelity-fix-2/REPORT.md:213>
D2D3  <- D2D3                 report       | <the sentence at safety-framework-fidelity-fix-2/REPORT.md:213>
3 exposures on FACTS/CASES
```

After (`exposure.py safety-framework 2aa79f0303`):

```
counter sha256 f4345f44  case safety-framework  commit 2aa79f0303  state run
FACTS <- FACTS                report       | <the sentence at safety-framework-fidelity-fix-2/REPORT.md:213>
CASES <- CASES                report       | <the sentence at safety-framework-fidelity-fix-2/REPORT.md:213>
D2D3  <- D2D3                 report       | <the sentence at safety-framework-fidelity-fix-2/REPORT.md:213>
2 exposures on FACTS/CASES
```

- The PLAN.md:647 record now goes to the `measures-sl2plus` unit, which reaches only its seven items.
- The remaining two come from docs/usecases/safety-framework/safety-framework-fidelity-fix-2/REPORT.md:213, which
  belongs to row safety-framework-facts-repair's question 1, not to this row.
- This item adds no exposure.
- I wrote no `loss` tag and changed no record of an omission.

## Condition tests (tests/test_fsf_case_alternatives.py, new file)

- (a) `test_g7_states_a_tcl_and_a_mitigated_ccl_risk`, `test_g3_states_approaching_and_reaching_a_tcl` and
  `test_g9_states_every_tcl_and_ccl_model` each fail on the main case (no `alternatives`), and pass now.
  `test_each_alternative_is_answered_...` checks the saved records.
- (b) `test_measures_sl2plus_is_scoped_to_the_items_that_read_it` fails if the block is back in facts.d1.ve, or if
  the F16 records do not name it.
- Kept and selected: `tests/test_safety_framework.py`, which has the frozen key, the transcription pin and fix-3's
  bridge tests. I changed three of its tests, and only where they pinned the old place of the block:
  - `test_security_level_2_plus_...` now reads `run.document_atoms()`.
  - `FACTS_BLOCKS` no longer lists the block.
  - `test_facts_holds_...` now expects two item-scoped blocks, and N1's header is unchanged.
  - Command: `uv run pytest -q tests/test_safety_framework.py -k "security_level_2_plus or facts_holds or refused or n1_alone or g8_stipulates"`: 6 passed.
- New file: `uv run pytest -q tests/test_fsf_case_alternatives.py`: 9 passed.

## Seeded bugs (Python, the only product language changed)

Script /tmp/sfca-scratch/seed.sh planted each bug, ran one test, then restored the tree. Logs:
/tmp/sfca-seed-{a..e}.log. `git status` was clean afterwards.

| # | Bug | File | Failing test |
|---|---|---|---|
| a | G7 has no mitigated-CCL branch | usecases/safety-framework/cases.json | `test_g7_states_a_tcl_and_a_mitigated_ccl_risk` |
| b | measures-sl2plus back in facts.d1.ve (`always`) | usecases/safety-framework/facts.d1.ve, rules.d1.ve | `test_measures_sl2plus_is_scoped_to_the_items_that_read_it` |
| c | run.py reads only the first alternative (`situations(case)[:1]`) | usecases/safety-framework/run.py | `test_an_alternative_that_fails_makes_the_item_fail` |
| d | an item-scoped block reaches only the last item its header names | usecases/safety-framework/translation.py | `test_the_f16_items_load_the_block_and_their_proofs_use_it` |
| e | the case model ignores the item's own premises | usecases/safety-framework/run.py | `test_the_f16_items_load_the_block_and_their_proofs_use_it` |

## Trust, DELTA, trust mutants

- `tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0", PASS.
- DELTA: none. The changes are use-case files only, and no checker verdict, refusal or relay changed. No standing
  ruling is invoked.
- light-lane.py printed NOT (1035 lines, including results.json and cases.json). No Lean or trusted-core file
  changed, and build checklist 13a applies only to trusted Lean growth. So no trust_mutants sweep is due, and none
  was run.

SIZE: 159 product (run.py 125, translation.py 26, build_document.py 8), 112 tests, 219 other hand-written lines
(cases.json 207, README.md 6, facts/rules 4, with 2 for the source note), plus this REPORT. results.json is
generated. (`git diff --numstat ce3fe4ed34`.)

## Notes for the DRI

- build_document.py changed in three code lines and one comment, although the OVERLAP note gives that file to
  safety-framework-proximity-tcl:
  - Lines 669 and 678: the document's premise unit `s211-sl2plus` looks up `T.fact_formulas()`.
  - Line 637: the reading-set models use `run.document_atoms()`.
  - Line 249: the comment now names rules.d1.ve as the bridge's place. Fix-3's REPORT left this to this row.
  - Without the line 637 change, the RS5 distinguishing model would no longer satisfy the 2.1.1 facts the document
    asserts. With it, the built document is byte-identical to main. The changed lines are far from the
    proximity hunk (:236-237).
- rules.d1.ve gained two lines at its end: the block, in the place translation.py gives item-scoped blocks. If
  safety-framework-proximity-tcl also appends at the end, the textual conflict is two lines.
- PLAN section 12 is unedited (OVERLAP). PLAN.md:647 ("`measures-sl2plus` states 2.1.1 as written") is still true
  wherever the block lives. PLAN.md:626 still says "(facts.d1.ve `item N1`)" for the bridge, wording from fix-3.
  It belongs to section 12, so I left it.
- I enumerated each branch's class instead of picking one level. As a result, G7's TCL branch now also covers
  the stealth TCL, and G9 covers all seven levels. Every alternative is ALL (scratch probe /tmp/sfca-probe.log,
  then the saved records).
- safety-framework-proximity-tcl expects G3 to move ALL -> NONE. G3 now has four alternatives, and that row's
  regeneration recomputes all of them.
- By default build_document.py writes the local `fsf.d1.ve.md` beside the pinned source in
  manage-agents/pilots/safety-framework/source/. My first run there wrote an intermediate document, and I restored
  the file to the current document (sha256 b7235a13..., the same on main and here). Later runs used
  `--source /tmp/sfca-src/fsf-3.1.txt`.

## Spec re-read

- G3 alternatives against PLAN.md:349. G7 against PLAN.md:353 and its justification "F19 needs a CCL with an
  unmitigated, material risk". G9 against PLAN.md:355.
- The "or" rule against PLAN 5's verdict definitions (PLAN.md:210-214).
- The scoping against DRI items 3 and 5 (the follow-on's conditions) and the task's item list "B-L2/3/4/6/7 RECSEC,
  C1, C4".
- `mitigates` against vocabulary.py:103 (OT2), and `approaches` against vocabulary.py:71.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean route or relayed answer changed. The use-case harness calls the checker in-process as before.
2. PASS: every DELIVER row is mapped to a commit and test in the table above. Rule-break grep: no Python copy of a
   Lean decision and no report test. The in-flight overlap is in the Notes.
3. PASS: seeded bugs a-e, each failing a named test (/tmp/sfca-seed-*.log). No R16 growth (trust_map +0).
4. PASS: base against HEAD on the case's whole key. 262/262 rows have the same answer, and coverage.json is
   byte-identical (run.py --check, build_document.py).
5. N.A.: no relayed field read from a Lean answer was added.
6. PASS: main is unchanged since the merge base (ce3fe4ed34). The chain runs the gate on the final HEAD.
7. PASS: no DELTA row and no trust growth (trust_map --check +0).
8. PASS: no user-visible checker output changed. The results.json record changes are listed under "4.", and no
   answer moved.
9. PASS: `tools/select_tests.py --base ce3fe4ed34` selects tests/test_fsf_case_alternatives.py and
   tests/test_safety_framework.py, which hold every seeded bug's failing test.
10. N.A.: no Lean statement or proof changed.
11. N.A.: no budget or deadline code changed. Each alternative is evaluated once per choice.
12. PASS: `run.py --check` took 113.9 s, against 178.1 s on main in the same worktree (/tmp/sfca-run0.log,
    /tmp/sfca-run2.log). Machine load varies, so this is no speed claim.
13. PASS: no test was removed or renamed. `gate_collection.py --check --prebuilt`: 9 added, 0 refused, 0 stale,
    0 malformed.
14. PASS: both directions are tested: an alternative that holds and one that fails
    (`test_an_alternative_that_fails_makes_the_item_fail`), and with and without the item's premises
    (`test_the_f16_items_load_the_block_and_their_proofs_use_it`). Claims cite commands above, and the spec re-read
    is listed.
15. PASS: "no answer moved" is backed by the comparison diff (262 rows) and `run.py --check`. "No exposure added"
    is backed by exposure.py before and after. No deliverable was cut. The new checks have mutants a-e. Limits:
    N.A. (fixed case data).
