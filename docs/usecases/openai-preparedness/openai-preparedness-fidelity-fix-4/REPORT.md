# openai-preparedness-fidelity-fix-4: PF round B part 2 (the other six units REAL by both adjudicators)

DRI signatures reserved: none. DELTA: none (use-case files only; no ve/, lean/ or rust/ change; no key edit).
Status: all 6 named units fixed, in the task's batch order. By the DRI ruling of 2026-11-13 item 2
(reviews/dri-decisions-20261113-openai-preparedness-fidelity-fix-4.md), c2-misalignment-default also lost the same guard.
Union count: PROJECTED 132 -> 156 (batch 1) -> 157 (batch 2) -> 157 (batch 3). The re-read decides.
Answers: one answer moved. G9, a key finding, went from SOME(96 choices) to NONE. Its key is ALL, so it was off the key
before and is off it now. The DRI ruled on this (item 1), and PLAN 12 item 25 amends item 20. Every other answer is
unchanged: 236 / 239 agree, as before.

## Units changed, by checklist class

| Unit (block) | Finding (where) | Fix | Classes |
|---|---|---|---|
| f3-develop | sess-3 C1/C7; pool 2 Q04 REAL by both. C1: "Neither this act nor its legend (V:141-143) preserves 'additional'". C7: "Every situation" inherits "of a covered model" (V:238). | The shared act `safeguards_during_development` is now "{0} have sufficient additional safety plus security controls during development" (79 characters). Its legend quotes 4.4's "Such models require additional safeguards (safety and security controls) during development, regardless of whether or when they are externally deployed.", 4.2's and Appendix C's sentences in full. C7: the `situation` sort already has no "covered" (fix-3, under the fix-2 q3 ruling item 2). I verified this rather than redoing it, and the header says "no coverage condition". | 1, 7, 11 |
| f3-develop-forecast | sess-3 C1/C7, forecast branch (R:46); pool 2 Q05 | The same act and header note | 1, 7, 11 |
| f3-reminder | sess-3 C7: R:52's "Every situation" "is thereby restricted to covered models"; pool 2 Q06 | No coverage condition: the sort as above, and a header note. "Sufficient" is kept. The block reads the shared act (not forked, as the task says). The header says that "also" makes these safeguards additional to those required before deployment. | 7, 11 |
| c2-misalignment-strict | sess-5 C7: R:100 adds "if that situation is classified as 'misaligned_model_risk'", "an independent positive risk premise"; pool 1 Q01 | The guard is dropped. "must" is kept (RS9 = strict). The legend of `misalignment_risk_minimized` quotes the full C.2 sentence. The header says there is no applicability condition. | 7, 11 |
| c2-misalignment-default | Not a named unit; FAITHFUL in both passes. It reads the same guard on the same sentence (STOP RULE question 3). | DRI ruling 2026-11-13 item 2 (SIGNED): the same fix, keeping "should". The fallback (revert if a counted answer moves off its key) was not needed: no counted answer moved. | 7, 11 |
| c3-access-strict | sess-6 C1/C2/C7: R:104 ranges over situations "of a covered model"; the header drops "may require additional approvals" "with no reason"; pool 1 Q03 | C7: the sort as above, and the header says "no coverage condition … it is for all models". The "may require" clause is still untranslated, now with a stated reason. The header says it "states a possibility, that access may need additional approvals, not a duty, and it grants no one a permission, so no rule of either reading carries it; PLAN 3.3". spans.json's `rs9-access` record has `"untranslated": [{"span": [64799, 64846], "reason": "possibility_not_duty", "detail": …}]`. This record comes from the new `build_document.UNTRANSLATED` table, which stores the clause's byte span and never its text. | 1, 2, 7, 11 |
| c3-access-default | The same (R:106; pool 1 Q02) | The same | 1, 2, 7, 11 |

Blocks changed only because a named fix changed something they share:
- f3-develop-inuse and f3-develop-inuse-forecast: their rule sentence names the shared act, so it now reads "sufficient additional safety plus security controls during development". Their headers are unchanged.
- The vocabulary predicate `misaligned_model_risk` is removed, because no rule reads it any more.

No other block, case or query changed. run.py changed only in G9's cause text.

Counts per class (units): class 1: 4; class 2: 2; class 7: 7; class 11: 7. Every changed block's header quotes its full source sentence (test_every_header_quotes_whole_source_text passes).

The post-merge re-read should re-read these 9 blocks: f3-develop, f3-develop-forecast, f3-develop-inuse, f3-develop-inuse-forecast, f3-reminder, c2-misalignment-strict, c2-misalignment-default, c3-access-strict and c3-access-default.

Regulated predicates: 60 of 64, unchanged. No predicate was added. The removed `misaligned_model_risk` was not regulated. Evidence: test_regulated_predicates_stay_within_64 passes, and stage0.json P7 = 60.

## Batches: PROJECTED union count after each

Method: /tmp/pf4/project.py is fix-3's script, unchanged. It reapplies uc-score-2's rule to the union VERDICTS.md rows at 175814252d. An item counts if:
- its item verdict was FAITHFUL,
- its VE answer equals the key, and
- every unit it uses is FAITHFUL, fixed or cleared.

The baseline reproduces: nothing fixed gives 87; round A + f9-threshold gives 90; fix-3's six units added give 132.

Each batch ran run.py's comparison (/tmp/pf4/cmp.py calls `run.run()` and diffs it against the saved results.json). The final full `run.py` wrote results.json.

| Batch | Units | run.py | Answer changes old -> new (cause) | PROJECTED union count |
|---|---|---|---|---|
| 1 | f3-develop, f3-reminder, f3-develop-forecast | 236 / 239, "rows changed 0" (141 s) | none | 156: 22 A-*/SUF items, G8 and K7 now rest on no failing unit |
| 2 | c2-misalignment-strict (+ c2-misalignment-default, DRI item 2) | 236 / 239, "rows changed 1" (188 s) | G9: SOME(96 choices: RS4=P or RS4s=scoped) -> NONE. Strict alone gave SOME(48 choices, RS9=default only). Cause: the unguarded C.2 duty binds G9's uncovered, no-threshold model. Key ALL; still a key finding. | 157: G3 |
| 3 | c3-access-strict, c3-access-default | 236 / 239, "rows changed 0" (186 s); final full run "236 / 239 (1126.0 s)" | none | 157 (both c3 units carry no counted answer alone) |

Old -> new for the items the task names (main's results.json against HEAD's; /tmp/pf4/table.py). "Not counted" lists the units still failing:

| Item | old -> new | key | agree | union status after this item (PROJECTED) |
|---|---|---|---|---|
| A-*/SUF (28) | unchanged (none of the 28 changed): 6 ALL, 7 NONE, 15 SOME | = key | all 28 agree | 22 counted (the other 6 are the next row) |
| A-{BIO,CYB,AIS}-C-{INT,LINT}/SUF (6) | SOME(10 choices) -> the same | SOME(inuse \| (nest & any)) | agree | not counted: the item verdict at 175814252d was UNFAITHFUL; the re-read decides |
| C3 | NONE -> NONE | NONE | agree | not counted: f1-halt-strict, f1-halt-default |
| G1 | ALL -> ALL | ALL | agree | not counted: f1-halt-*, f2-no-deploy-any |
| G2 | ALL -> ALL | ALL | agree | not counted: f1-halt-* |
| G3 | ALL -> ALL | ALL | agree | COUNTED |
| G4 | ALL -> ALL | ALL | agree | not counted: f1-misuse-bio-* |
| G5 | ALL -> ALL | ALL | agree | not counted: f1-halt-*, f1-misuse-bio-*, f2-no-deploy-any |
| G8 | NONE -> NONE | NONE | agree | COUNTED |
| K7 | ALL -> ALL | ALL | agree | COUNTED |
| N1 | ALL -> ALL | ALL | agree | not counted: f1-halt-* |
| N3 | NONE -> NONE | NONE | agree | not counted: 15 other failing units |
| G9 (information only) | SOME(96 choices) -> NONE | ALL | disagree (before and after) | not counted (VE != key; PLAN 12 item 20, amended by item 25) |

Other results.json changes: metrics M2 some_answers 50 -> 49, and M4 conditional_by_family G 2 -> 1 (both from G9). The mutants and without_narrowings are unchanged (the diff of main's results.json against HEAD's found changes only in `comparison`, `items` and `metrics`).

## Checks run (on the final code)

- `lake build`: "Build completed successfully (1438 jobs)". Lean is unchanged; the build is for the service that run.py uses.
- `run.py` (full): "236 / 239 (1126.0 s)".
- `build_document.py`: spans.json gains the `untranslated` record, and coverage.json's `document_sha256` changed.
- `--check` runs: `build_document.py`, `stage0.py` and `measure.py` each exit 0.
- `pf_vocabulary.py` regenerated environment.d1.json. `source/quote_evidence.py` rewrote quote-hashes.json, which came out unchanged.
- `safetyfw_accounting.py openai-preparedness --source <pinned> --check`: rc 0, "99 blocks, 539 unaccounted words in 75 blocks, 17 blocks with a loss {'1': 19, '3': 1, 'limit 21': 1}, 0 of 116 quotes unanchored".
  - The saved report docs/usecases/safetyfw/openai-preparedness/accounting.json was regenerated with `--report`.
  - The f3-develop(-forecast) lines drop "Such models require additional safeguards" loss 1, because the act now carries it.
  - The c2 lines are now "omits: nothing", because the legend quotes the sentence.
  - The c3 lines keep "and may require additional approvals for access" loss 1, because the rule does not carry those words.
- `pytest tests/test_pf_fidelity_fix.py tests/test_usecase_key_transcription.py`: 78 passed and 1 failed. The failure was the K test's line-wrap match, which I fixed: `-k test_k_entries_are_the_saved_answers` gives "1 passed".
- `pytest tests/test_safetyfw_usecases.py tests/test_safetyfw_accounting.py -k "pf or preparedness"`: "55 passed".
- Final selected run: see the section of that name below.
- `tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 … PASS".
- light-lane.py: "NOT 632 changed lines outside generated files > 150 (13 files)". The count includes results.json, spans.json, coverage.json, environment.d1.json and accounting.json, which the case's own scripts generate.
  - No trusted-core file and no Lean file changed, and the task asks for no trust_mutants record.
  - So no sweep was run: there is no trusted Lean definition to mutate.
- Frozen key: test_answer_key_equals_section_6_cell_by_cell, test_section_6_is_the_frozen_key and test_transcription_is_pinned are unchanged and pass.

Tests changed in tests/test_pf_fidelity_fix.py (no pf_* test in test_safetyfw_usecases.py changed):
- test_f2_f3_acts_carry_the_sufficiency: pinned the old act text "sufficient safety as well as security controls". It now pins "sufficient additional safety plus security controls".
- test_k_entries_are_the_saved_answers: pinned G9 = SOME(P ∨ scoped). It now pins G9 = NONE and the item-25 amendment, as the DRI ruling item 1 orders.

New tests:
- test_f3_development_act_keeps_additional_with_the_sufficiency
- test_f3_development_units_read_no_coverage_condition
- test_an_uncovered_critical_model_still_needs_development_safeguards (live; it includes the opposite direction: below Critical, covered or not, nothing is selected)
- test_c3_access_reads_no_coverage_condition_and_states_why_may_require_is_untranslated
- test_an_uncovered_model_still_has_access_strictly_limited (live)
- test_c2_misalignment_has_no_risk_guard_under_either_reading
- test_c2_binds_a_model_with_no_risk_finding (live)

## Open list

- Questions sent: one message, at 2026-11-13 15:08Z (inbox/dri/20261113T150805Z-openai-preparedness-fidelity-fix-4-1885937.md):
  - (A) c2-misalignment-strict moves G9's K-entry answer.
  - (B) STOP RULE question 3, on c2-misalignment-default.
  - Both were answered in reviews/dri-decisions-20261113-openai-preparedness-fidelity-fix-4.md: item 1 (apply; amend item 20) and item 2 (drop the default's guard too, with a fallback). Both are applied.
- STOP RULE question 1 was not needed. The shared sort description had already lost "covered" in fix-3, under reviews/dri-decisions-20261112-openai-preparedness-fidelity-fix-2-q3.md item 2. test_f4_security_reads_no_coverage_condition and test_f3_development_units_read_no_coverage_condition pin this.
- STOP RULE question 2 was not triggered: no counted answer moved (table above).
- No unit is left unfixed. No AMENDMENT cleared a unit.
- Out of scope, with no work here:
  - C6 and C-doc (VE NONE != key; PLAN 12 item 19).
  - G9 (VE NONE != key ALL; PLAN 12 item 20, amended by item 25).
  - The 15 split or ARGUABLE units, which wait for the DRI decider's round-B ruling: f1-halt-strict, f1-halt-default, f1-misuse-bio-strict, f1-misuse-bio-default, f10-validate, f15-third-party, f16-board-mandate, f16-board-reverse, f16-without-nodelib, f16-without-noinput, f16-sag-recommend, f2-no-deploy-any, f9-efficacy, f9-risk-paths and f9-specific.
  - f9-threshold (NOT by both; cleared).
  - Row checklist-recalib-pf, which re-calibrates the checklist reader on PF (addendum 8 item 54).

## Seeded bugs (Python use-case files; no Lean or Rust product code changed)

Planted after a commit, each run against its named test, then restored with `git checkout`. Also recorded in mutants.json.

| # | File | Bug | Failing test |
|---|---|---|---|
| a1 | usecases/openai-preparedness/pf_vocabulary.py | situation sort back to "… of a covered model" | test_f3_development_units_read_no_coverage_condition ("assert 'covered' not in 'a developme...overed model'") |
| a2 | usecases/openai-preparedness/rules.d1.ve | explicit "that situation is covered" guard on f3-reminder | test_an_uncovered_critical_model_still_needs_development_safeguards ("{'f3-develop'} == {'f3-develop', 'f3-reminder'}") |
| b | usecases/openai-preparedness/pf_vocabulary.py (+ the five rule sentences) | "additional" dropped from the shared F3 act | test_f3_development_act_keeps_additional_with_the_sufficiency |
| c | usecases/openai-preparedness/rules.d1.ve (+ predicate) | misaligned_model_risk guard back on c2-misalignment-strict | test_c2_binds_a_model_with_no_risk_finding ("set() == {'c2-misalignment-strict'}"), test_c2_misalignment_has_no_risk_guard_under_either_reading |
| d | usecases/openai-preparedness/rules.d1.ve | both c3-access-* headers cut back to "(the “may require” clause is not translated)" | test_c3_access_reads_no_coverage_condition_and_states_why_may_require_is_untranslated |
| e | usecases/openai-preparedness/build_document.py | the UNTRANSLATED record skipped (spans.json regenerated) | the same test ("KeyError: 'untranslated'") |

## Budget readings

The launcher's reading is in the task's AMENDMENTS (2026-11-12 20:21Z on VM1): 9.48M CW in 24 h; joint allowance left 4.52M of 14M; round budget 1.00M (ALLOCATED): START. No `openai-preparedness-fidelity-fix-4-loop.log` exists in manage-agents, so I took no further reading. I did not run ucfix-budget.py, as the task says.

## Size

SIZE: 77 product, 117 tests, 278 other hand-written lines.
- Measured with `git diff --numstat $(git merge-base HEAD main)`, generated files excluded.
- Product: rules.d1.ve, pf_vocabulary.py, build_document.py, run.py, accounting.d1.txt.
- Other: PLAN.md 21, README.md 5, this REPORT 203 and mutants.json 49.

## Notes for the DRI

- f3-reminder reads "additional" through the shared act. The task says to reuse the act, not fork it. Appendix C's "also" (beyond the safeguards required before deployment) is the stated basis, and the header says so. If the re-read objects to "additional" on f3-reminder, the alternative is an Appendix-C-only act. That adds one regulated predicate (61 of 64) and adds it to run.ATOMS["SUF"] and CRITICAL_PREDICATES.
- The act uses "plus" for "and". "as well as" (PLAN 12 item 17's convention) does not fit in 80 characters beside "sufficient additional": that version is 85 characters. The legend says what "plus" stands for.
- README.md's sentence on G9's K finding now says NONE. It is a hand-written summary of PLAN 12 items 19 and 20, and was updated with item 25.
- Observation, with nothing changed: the c3 unit p21-u380 (bytes 64652-65002) also spans the next bullet, "Identity and Device Management: Employees must authenticate using multi-factor authentication (MFA) and managed devices meeting security baselines."

## Spec re-read

- 4.4 against pf-v2.txt line 13 of the extracted text: "Such models require additional safeguards (safety and security controls) during development, regardless of whether or when they are externally deployed." Exact.
- 4.2 against pf-v2.txt line 12: "Systems that reach Critical capability also require safeguards that sufficiently minimize associated risks during development." Exact.
- Appendix C against pf-v2.txt line 17: "Systems that reach Critical capability also require sufficient safeguards during development." Exact.
- C.2: the legend's quote equals the header's quote, which quote_evidence anchors ("0 of 116 quotes unanchored").
- C.3 clause: build_document checks that "and may require additional approvals for access" occurs exactly once in unit p21-u380. Otherwise the build raises.
- PLAN 3.3 at PLAN.md:128: "No permission the text does not grant."
- Act limit at lean/VE/Norms/Wire.lean:33: at most 80 characters, including "{0} ". The reserved words are at lean/VE/Acts/LexicalBase.lean:8. Neither "plus" nor "additional" is reserved.
- The DRI ruling's conditions (items 1-2):
  - test_k_entries_are_the_saved_answers pins the new G9.
  - test_section_6_is_the_frozen_key and test_transcription_is_pinned are unchanged.
  - The REPORT gives G3, G4 and G9 old -> new.

## Next item

After merge, the DRI decider launches the production checklist pass. It re-reads only the 9 changed blocks listed above (addendum 8 item 56). The full union audit follows at the Nov 23 checkpoint. The builder runs no audit. After that comes the DRI decider's ruling on the 15 PF units the adjudicators left split or ARGUABLE (reviews/audit-newrule-fsfpf/pf-adjud/result.md section 2).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relay, schema or Lean change.
2. Deliverables built, no rule broken: PASS.
   - All 6 named units are fixed, plus c2-misalignment-default by DRI item 2. The per-unit tests are listed above.
   - The vocabulary stays only in pf_vocabulary.py, the readings in build_document.py, and the queries in run.py. No test copies a decision.
   - The overlap re-check found no in-flight branch touching these files: `git diff --name-only main...<branch>` over every feature/infra/lean-first/foundation branch printed nothing.
3. Tests can fail: PASS. 6 seeded bugs, each failing a named test (mutants.json).
4. Py/Lean/Rust agree: N.A. No product code in ve/, lean/ or rust/. run.py's answers come from the Lean service (236 / 239).
5. R8 binding: N.A. No relay.
6. Gate evidence matches the final HEAD: PASS. results.json, spans.json and coverage.json were regenerated on the final translation, and the three `--check` scripts exit 0.
7. No unsigned item: PASS. No DELTA row and no reserved signature. The two DRI decisions are signed in the ruling file.
8. User-visible change in DELTA: N.A. Use-case data only. G9's answer change is a use-case answer under a K entry, ruled by the DRI (item 1). It is not a checker verdict change.
9. Test selection: PASS. The final selected run (below) selects tests/test_pf_fidelity_fix.py and the case's other test files.
10. Lean statements: N.A. No Lean change.
11. Budgets and limits: N.A. No evaluator or limit changed. Lean enforces the 80-character act limit when it admits the environment; run.py parses every rule.
12. CPU/memory: N.A. Only wording and two guards changed. The full run.py took 1126.0 s (fix-3: 1287.9 s).
13. Test-removed trailers: N.A. No test removed or renamed.
14. Both directions, cited evidence: PASS.
    - The F3 live test checks that an uncovered Critical model is bound and that a below-Critical model is not, covered or not.
    - The c2 test checks that both readings lose the guard and that RS9 still changes the modal.
    - test_f4_security_reads_no_coverage_condition still pins the rules whose source states coverage.
    - The claims above cite their commands.
15. Overclaim, silent cut, new checks fail, limits charged:
    - Overclaim: PASS. Union numbers are labelled PROJECTED, from /tmp/pf4/project.py.
    - Silent cut: PASS. No deliverable was cut.
    - New checks fail: PASS. See mutants.json.
    - Limits charged: N.A. No evaluator.
- Sibling lesson (fix-3 review C1, a test copying Lean's reserved words): no new test copies the reserved list or the 80 limit.

## Final selected run

(Filled in after the run on the committed tree.)
