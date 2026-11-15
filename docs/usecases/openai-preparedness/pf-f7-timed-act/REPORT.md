# pf-f7-timed-act: REPORT

1. Status: done except B4. A, B1 to B3 and B5 to B8 are built, and `moved: []` (236 of 239 agree, as on main). B4 (the
   f16-without guard) hit the expected stop and keeps its guard by DRI decision (follow-up row pf-f16-without-n2).
2. Product HEAD 1a4f7b90fe (this report's commit follows it). Changed: usecases/openai-preparedness/, tests, saved evidence under docs/.
3. Open: B4 (row pf-f16-without-n2, architect); the three f9 units stay unresolved pending the Astra challenge.
4. DRI signature needed: none. DELTA: none (trust_map +0 in every tier). Exposure 6 before, 6 after (same rows).
5. Not run by me: the full gate (the chain runs it). The selected run's result is at the end of this file.

Task: prompts/task-pf-f7-timed-act.txt (written 2026-11-15 by dri-decider). Rulings: architect
fable-team/architect/rulings/et-5c-5d-coverage-20261115.md section 3 (A); pf-split-units-20261115.md section 2 (B);
reviews/dri-decisions-20261115-arch-round6.md items 1 and 2; reviews/dri-decisions-20261115-pf-f7-timed-act.md items
1 to 3 (this item's stops, decided 2026-11-15 12:22Z).

## Deliverables

| Task line | What is on the branch | Commit | Test |
|---|---|---|---|
| A (1) guard names the reference event, RS3 ext / any as f2-deploy | `f7-evaluations` is RS3=ext (guard `covered` and `external_deployment`); the new block `f7-evaluations-any` is RS3=any (guard `covered` and external or internal deployment) | 58f1b0d260 | `test_f7_evaluations_names_its_timing_in_the_act_and_deployment_in_the_guard` |
| A (2) the act in the source's timing words | act of `evaluations_before_deployment`: "undergo the suite of Scalable Evaluations prior to deployment"; its legend quotes the 3.3 sentence (1a4f7b90fe) | 58f1b0d260 | same test (the act phrase is in each Rule line) |
| A record line | both headers and PLAN 12 item 29: "order against deployment is inside the act; dated facts are not classified" | 58f1b0d260, 1a4f7b90fe | same test; `test_plan12_item_29_names_only_the_units_it_records` |
| A harness lists (DRI decision item 1) | run.py COMMITMENTS F7 and CLUSTERS C4, pf_translation.RS0_STATEMENTS, build_document rs3-deploy (both RS3 names, as f2-deploy is listed) | 58f1b0d260 | `test_f7_evaluations_any_is_listed_with_its_ext_twin` |
| B1 BIO-H's own act | `misuse_safeguards_before_external`: "have misuse safeguards meeting the High standard before external deployment" (79 characters with its place; the limit did not bite); 62 of 64 regulated; run.py ATOMS["MIS"] and THRESHOLD_PREDICATES read it (DRI decision item 2) | 58f1b0d260 | `test_bio_h_misuse_bullet_has_its_own_timed_act`; `test_regulated_predicates_stay_within_64` (62); `test_touched_answers_on_a_live_query_equal_the_snapshot` |
| B2 f1-halt legend | `critical_standard_unspecified` quotes the row (BIO-C, AIS-C) and CYB-C's "safeguards and security controls standards" | 94167f21d4 | `test_critical_standard_legend_names_the_rows_object_of_specified` |
| B3 f16-sag-recommend | guard is `framework_deployment` alone | 94167f21d4 | `test_f16_sag_recommend_tests_only_its_own_condition`; `test_pf_checked_norms_keep_their_source_scope` |
| B4 f16-without x2 | NOT APPLIED: the guard stays (DRI decision item 3) | none | `test_f16_without_keeps_its_guard_until_n2_is_ruled`; `test_touched_rules_keep_a_witness_model[f16-informed]` |
| B5 f16-board legend | `board_finds_necessary`: "it is necessary at {0} to act on the decision (Appendix B: “Where necessary”); the source names no decider: the decider is unstated (an open term, as OT13)"; predicate not renamed | 94167f21d4 | `test_board_guard_legend_is_the_open_term_form_with_no_decider` |
| B6 f15 legend | `deeper_testing_warranted`: "OpenAI ('we') deems that the deployment at {0} warrants deeper testing of Tracked Categories of capability" | 94167f21d4 | `test_deeper_testing_legend_keeps_a_deployment`; `test_f15_third_party_act_is_openais_work_with_third_parties` |
| B7 f9-efficacy legend | quotes “For each identified safeguard, we identify methods to measure their efficacy” | 94167f21d4 | `test_efficacy_legend_quotes_its_sentence` |
| B8 f9 record lines | the f9-risk-paths header and the `risk_paths` legend: "the order follows from the second step's 'each of those'"; f9-specific and f9-efficacy: one line each in the header and in PLAN 12 item 29; f9-specific's legend keeps "that either exist or should be implemented" | 94167f21d4, aaa8dc9ecf | `test_risk_paths_order_follows_from_each_of_those`; `test_f9_record_lines_and_kept_legend_words`; `test_f9_selection_steps_carry_their_order_word_and_record_the_order_as_et` |
| C regenerate, `moved` | pf_vocabulary.py, build_document.py, stage0.py, measure.py, source/quote_evidence.py, run.py, safetyfw_accounting.py --report; conformance/english_lean_lexicon.py for lexicon-report.json (PF's environment lexicon: 138 -> 139 symbols; 43 valid, 0 invalid) | 94167f21d4, 58f1b0d260, 1a4f7b90fe, the commit after 9be7968419 | `test_no_pf_answer_moved_against_the_merge_base_snapshot`; `test_every_corpus_environment_has_a_valid_selected_lexicon` |

f7-compile: no change, as the task says. The three f9 rulings are provisional. No record, test or fixture on this
branch cites their rule, and this report does not count them as cleared.

## Stops and the DRI's decisions (one message, 2026-11-15 12:20Z; answered 12:22Z)

All three were measured with `uv run python usecases/openai-preparedness/run.py --base-only` on temporary edits, then
undone (logs /tmp/pf7-exp-b1.txt, /tmp/pf7-exp-b1b.txt, /tmp/pf7-exp-a.txt, /tmp/pf7-exp-a2.txt, /tmp/pf7-base-b.txt).
- Q1, stop 4 (part A): without a run.py change, N3 went NONE -> UNDECIDED ("no witness model or no commitment part for
  f7-evaluations-any"). With the name added to the lists: 236 of 239. SIGNED for name-list edits (item 1).
- Q2, stops 1 and 4 (B1): without a run.py change, A-BIO-H-EXT/MIS went ALL -> NONE and A-BIO-C-EXT/MIS went SOME(nest) -> NONE.
  With the new predicate in ATOMS["MIS"] and THRESHOLD_PREDICATES: 236 of 239. SIGNED (item 2).
- Q3, stops 1 and 2 (B4): measured with the f16-without rules testing `leadership_decision` alone, N3 went NONE ->
  UNDECIDED ("no witness model ... for f16-informed"): under RS7=noinput, N2 precedence lets the noinput rule
  override f16-informed on every leadership decision. C2 stayed NONE. With that guard gone, no legend would carry
  "make decisions without the SAG's participation" any more: the accounting check (usecases/safetyfw_accounting.py
  --check) then flagged 'make', 'particip' and "sag'" on both rules, and the omission rule reads a `reading RS7` tag on
  those words as a mistag. The DRI kept the guard (item 3; follow-up row pf-f16-without-n2).

## Answers: old -> new

`moved: []`. Command: a comparison of `git show 26916f7349:usecases/openai-preparedness/results.json` (saved as
docs/usecases/openai-preparedness/pf-f7-timed-act/answers-at-merge-base.json) with results.json at HEAD. All 239 VE
answers are identical, the key column equals answer-key.json, and the mutants and the narrowing reruns are byte-equal.
run.py's own summary line was "236 / 239 (1962.9 s)" (/tmp/pf7-run2.txt). The metrics that moved are harness counts,
not answers:
- M5 regulated predicates 61 -> 62; M10 rules 90 -> 91, documents built 352 -> 354, choices 1043 -> 1045;
- M7 sensitive choices 681 -> 689, insensitive 112 -> 104. The 8 are the RS1 choices of A-BIO-H-EXT/MIS,
  A-BIO-C-EXT/MIS (nest), A-CYB-H-EXT/MIS and A-CYB-C-EXT/MIS (nest). MIS now asks two acts, and in each case one of
  them is silent, so the default completion touches that one. `holds` is unchanged on every choice;
- M8 W1 conflict-free 52 -> 54. C4's cone gains RS3 (4 choices, none a conflict; C4 stays NONE).
- N3's witness model for f16-sag-recommend no longer lists `covered`.

```
A-L0-DEV/SEC: NONE -> NONE (key NONE)
A-L0-DEV/MIS: NONE -> NONE (key NONE)
A-L0-DEV/ALN: NONE -> NONE (key NONE)
A-L0-DEV/SUF: NONE -> NONE (key NONE)
A-L0-DEV/HALT: NONE -> NONE (key NONE)
A-L0-INT/SEC: NONE -> NONE (key NONE)
A-L0-INT/MIS: NONE -> NONE (key NONE)
A-L0-INT/ALN: NONE -> NONE (key NONE)
A-L0-INT/SUF: NONE -> NONE (key NONE)
A-L0-INT/HALT: NONE -> NONE (key NONE)
A-L0-LINT/SEC: NONE -> NONE (key NONE)
A-L0-LINT/MIS: NONE -> NONE (key NONE)
A-L0-LINT/ALN: NONE -> NONE (key NONE)
A-L0-LINT/SUF: NONE -> NONE (key NONE)
A-L0-LINT/HALT: NONE -> NONE (key NONE)
A-L0-EXT/SEC: NONE -> NONE (key NONE)
A-L0-EXT/MIS: NONE -> NONE (key NONE)
A-L0-EXT/ALN: NONE -> NONE (key NONE)
A-L0-EXT/SUF: NONE -> NONE (key NONE)
A-L0-EXT/HALT: NONE -> NONE (key NONE)
A-BIO-H-DEV/SEC: ALL -> ALL (key ALL)
A-BIO-H-DEV/MIS: NONE -> NONE (key NONE)
A-BIO-H-DEV/ALN: NONE -> NONE (key NONE)
A-BIO-H-DEV/SUF: NONE -> NONE (key NONE)
A-BIO-H-DEV/HALT: NONE -> NONE (key NONE)
A-BIO-H-INT/SEC: ALL -> ALL (key ALL)
A-BIO-H-INT/MIS: NONE -> NONE (key NONE)
A-BIO-H-INT/ALN: NONE -> NONE (key NONE)
A-BIO-H-INT/SUF: SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) (key SOME(any))
A-BIO-H-INT/HALT: NONE -> NONE (key NONE)
A-BIO-H-LINT/SEC: ALL -> ALL (key ALL)
A-BIO-H-LINT/MIS: NONE -> NONE (key NONE)
A-BIO-H-LINT/ALN: NONE -> NONE (key NONE)
A-BIO-H-LINT/SUF: SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) (key SOME(any))
A-BIO-H-LINT/HALT: NONE -> NONE (key NONE)
A-BIO-H-EXT/SEC: ALL -> ALL (key ALL)
A-BIO-H-EXT/MIS: ALL -> ALL (key ALL)
A-BIO-H-EXT/ALN: NONE -> NONE (key NONE)
A-BIO-H-EXT/SUF: ALL -> ALL (key ALL)
A-BIO-H-EXT/HALT: NONE -> NONE (key NONE)
A-BIO-C-DEV/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-BIO-C-DEV/MIS: NONE -> NONE (key NONE)
A-BIO-C-DEV/ALN: NONE -> NONE (key NONE)
A-BIO-C-DEV/SUF: ALL -> ALL (key ALL)
A-BIO-C-DEV/HALT: ALL -> ALL (key ALL)
A-BIO-C-INT/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-BIO-C-INT/MIS: NONE -> NONE (key NONE)
A-BIO-C-INT/ALN: NONE -> NONE (key NONE)
A-BIO-C-INT/SUF: SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) (key SOME(inuse | (nest & any)))
A-BIO-C-INT/HALT: NONE -> NONE (key NONE)
A-BIO-C-LINT/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-BIO-C-LINT/MIS: NONE -> NONE (key NONE)
A-BIO-C-LINT/ALN: NONE -> NONE (key NONE)
A-BIO-C-LINT/SUF: SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) (key SOME(inuse | (nest & any)))
A-BIO-C-LINT/HALT: NONE -> NONE (key NONE)
A-BIO-C-EXT/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-BIO-C-EXT/MIS: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-BIO-C-EXT/ALN: NONE -> NONE (key NONE)
A-BIO-C-EXT/SUF: SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=ext&RS5=within | RS18=devonly&RS2=nest&RS3=ext&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=ext&RS5=within | RS18=devonly&RS2=nest&RS3=ext&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) (key SOME(nest))
A-BIO-C-EXT/HALT: NONE -> NONE (key NONE)
A-CYB-H-DEV/SEC: ALL -> ALL (key ALL)
A-CYB-H-DEV/MIS: NONE -> NONE (key NONE)
A-CYB-H-DEV/ALN: NONE -> NONE (key NONE)
A-CYB-H-DEV/SUF: NONE -> NONE (key NONE)
A-CYB-H-DEV/HALT: NONE -> NONE (key NONE)
A-CYB-H-INT/SEC: ALL -> ALL (key ALL)
A-CYB-H-INT/MIS: NONE -> NONE (key NONE)
A-CYB-H-INT/ALN: NONE -> NONE (key NONE)
A-CYB-H-INT/SUF: SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) (key SOME(any))
A-CYB-H-INT/HALT: NONE -> NONE (key NONE)
A-CYB-H-LINT/SEC: ALL -> ALL (key ALL)
A-CYB-H-LINT/MIS: NONE -> NONE (key NONE)
A-CYB-H-LINT/ALN: ALL -> ALL (key ALL)
A-CYB-H-LINT/SUF: SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) (key SOME(any))
A-CYB-H-LINT/HALT: NONE -> NONE (key NONE)
A-CYB-H-EXT/SEC: ALL -> ALL (key ALL)
A-CYB-H-EXT/MIS: ALL -> ALL (key ALL)
A-CYB-H-EXT/ALN: NONE -> NONE (key NONE)
A-CYB-H-EXT/SUF: ALL -> ALL (key ALL)
A-CYB-H-EXT/HALT: NONE -> NONE (key NONE)
A-CYB-C-DEV/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-CYB-C-DEV/MIS: NONE -> NONE (key NONE)
A-CYB-C-DEV/ALN: NONE -> NONE (key NONE)
A-CYB-C-DEV/SUF: ALL -> ALL (key ALL)
A-CYB-C-DEV/HALT: ALL -> ALL (key ALL)
A-CYB-C-INT/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-CYB-C-INT/MIS: NONE -> NONE (key NONE)
A-CYB-C-INT/ALN: NONE -> NONE (key NONE)
A-CYB-C-INT/SUF: SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) (key SOME(inuse | (nest & any)))
A-CYB-C-INT/HALT: NONE -> NONE (key NONE)
A-CYB-C-LINT/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-CYB-C-LINT/MIS: NONE -> NONE (key NONE)
A-CYB-C-LINT/ALN: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-CYB-C-LINT/SUF: SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) (key SOME(inuse | (nest & any)))
A-CYB-C-LINT/HALT: NONE -> NONE (key NONE)
A-CYB-C-EXT/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-CYB-C-EXT/MIS: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-CYB-C-EXT/ALN: NONE -> NONE (key NONE)
A-CYB-C-EXT/SUF: SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=ext&RS5=within | RS18=devonly&RS2=nest&RS3=ext&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=ext&RS5=within | RS18=devonly&RS2=nest&RS3=ext&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) (key SOME(nest))
A-CYB-C-EXT/HALT: NONE -> NONE (key NONE)
A-AIS-H-DEV/SEC: ALL -> ALL (key ALL)
A-AIS-H-DEV/MIS: NONE -> NONE (key NONE)
A-AIS-H-DEV/ALN: NONE -> NONE (key NONE)
A-AIS-H-DEV/SUF: NONE -> NONE (key NONE)
A-AIS-H-DEV/HALT: NONE -> NONE (key NONE)
A-AIS-H-INT/SEC: ALL -> ALL (key ALL)
A-AIS-H-INT/MIS: NONE -> NONE (key NONE)
A-AIS-H-INT/ALN: NONE -> NONE (key NONE)
A-AIS-H-INT/SUF: SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) (key SOME(any))
A-AIS-H-INT/HALT: NONE -> NONE (key NONE)
A-AIS-H-LINT/SEC: ALL -> ALL (key ALL)
A-AIS-H-LINT/MIS: NONE -> NONE (key NONE)
A-AIS-H-LINT/ALN: NONE -> NONE (key NONE)
A-AIS-H-LINT/SUF: SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS3=any&RS5=within | RS18=inuse&RS3=any&RS5=exception | RS18=devonly&RS3=any&RS5=within | RS18=devonly&RS3=any&RS5=exception) (key SOME(any))
A-AIS-H-LINT/HALT: NONE -> NONE (key NONE)
A-AIS-H-EXT/SEC: ALL -> ALL (key ALL)
A-AIS-H-EXT/MIS: NONE -> NONE (key NONE)
A-AIS-H-EXT/ALN: NONE -> NONE (key NONE)
A-AIS-H-EXT/SUF: ALL -> ALL (key ALL)
A-AIS-H-EXT/HALT: NONE -> NONE (key NONE)
A-AIS-C-DEV/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-AIS-C-DEV/MIS: NONE -> NONE (key NONE)
A-AIS-C-DEV/ALN: NONE -> NONE (key NONE)
A-AIS-C-DEV/SUF: ALL -> ALL (key ALL)
A-AIS-C-DEV/HALT: ALL -> ALL (key ALL)
A-AIS-C-INT/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-AIS-C-INT/MIS: NONE -> NONE (key NONE)
A-AIS-C-INT/ALN: NONE -> NONE (key NONE)
A-AIS-C-INT/SUF: SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) (key SOME(inuse | (nest & any)))
A-AIS-C-INT/HALT: NONE -> NONE (key NONE)
A-AIS-C-LINT/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-AIS-C-LINT/MIS: NONE -> NONE (key NONE)
A-AIS-C-LINT/ALN: NONE -> NONE (key NONE)
A-AIS-C-LINT/SUF: SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=inuse&RS2=sep&RS3=ext&RS5=within | RS18=inuse&RS2=sep&RS3=ext&RS5=exception | RS18=inuse&RS2=sep&RS3=any&RS5=within | RS18=inuse&RS2=sep&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) (key SOME(inuse | (nest & any)))
A-AIS-C-LINT/HALT: NONE -> NONE (key NONE)
A-AIS-C-EXT/SEC: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
A-AIS-C-EXT/MIS: NONE -> NONE (key NONE)
A-AIS-C-EXT/ALN: NONE -> NONE (key NONE)
A-AIS-C-EXT/SUF: SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=ext&RS5=within | RS18=devonly&RS2=nest&RS3=ext&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) -> SOME(RS18=inuse&RS2=nest&RS3=ext&RS5=within | RS18=inuse&RS2=nest&RS3=ext&RS5=exception | RS18=inuse&RS2=nest&RS3=any&RS5=within | RS18=inuse&RS2=nest&RS3=any&RS5=exception | RS18=devonly&RS2=nest&RS3=ext&RS5=within | RS18=devonly&RS2=nest&RS3=ext&RS5=exception | RS18=devonly&RS2=nest&RS3=any&RS5=within | RS18=devonly&RS2=nest&RS3=any&RS5=exception) (key SOME(nest))
A-AIS-C-EXT/HALT: NONE -> NONE (key NONE)
B-L0/CAPREP: ALL -> ALL (key ALL)
B-L0/SAFEREP: NONE -> NONE (key NONE)
B-L0/MREP: NONE -> NONE (key NONE)
B-L0/DISC: NONE -> NONE (key NONE)
B-L0/PUBRES: ALL -> ALL (key ALL)
B-L0/CONTRIB: NONE -> NONE (key NONE)
B-BIO-H/CAPREP: ALL -> ALL (key ALL)
B-BIO-H/SAFEREP: ALL -> ALL (key ALL)
B-BIO-H/MREP: SOME(RS4=N&RS4s=unscoped) -> SOME(RS4=N&RS4s=unscoped) (key SOME(N ∧ unscoped))
B-BIO-H/DISC: ALL -> ALL (key ALL)
B-BIO-H/PUBRES: ALL -> ALL (key ALL)
B-BIO-H/CONTRIB: NONE -> NONE (key NONE)
B-BIO-C/CAPREP: ALL -> ALL (key ALL)
B-BIO-C/SAFEREP: ALL -> ALL (key ALL)
B-BIO-C/MREP: SOME(RS2=nest&RS4=N&RS4s=unscoped | RS2=sep&RS4=N&RS4s=unscoped) -> SOME(RS2=nest&RS4=N&RS4s=unscoped | RS2=sep&RS4=N&RS4s=unscoped) (key SOME(N ∧ unscoped))
B-BIO-C/DISC: SOME(RS2=nest) -> SOME(RS2=nest) (key SOME(nest))
B-BIO-C/PUBRES: ALL -> ALL (key ALL)
B-BIO-C/CONTRIB: ALL -> ALL (key ALL)
B-CYB-H/CAPREP: ALL -> ALL (key ALL)
B-CYB-H/SAFEREP: ALL -> ALL (key ALL)
B-CYB-H/MREP: SOME(RS4=N&RS4s=unscoped) -> SOME(RS4=N&RS4s=unscoped) (key SOME(N ∧ unscoped))
B-CYB-H/DISC: ALL -> ALL (key ALL)
B-CYB-H/PUBRES: ALL -> ALL (key ALL)
B-CYB-H/CONTRIB: ALL -> ALL (key ALL)
B-CYB-C/CAPREP: ALL -> ALL (key ALL)
B-CYB-C/SAFEREP: ALL -> ALL (key ALL)
B-CYB-C/MREP: SOME(RS2=nest&RS4=N&RS4s=unscoped | RS2=sep&RS4=N&RS4s=unscoped) -> SOME(RS2=nest&RS4=N&RS4s=unscoped | RS2=sep&RS4=N&RS4s=unscoped) (key SOME(N ∧ unscoped))
B-CYB-C/DISC: SOME(RS2=nest) -> SOME(RS2=nest) (key SOME(nest))
B-CYB-C/PUBRES: ALL -> ALL (key ALL)
B-CYB-C/CONTRIB: SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) -> SOME(RS1=strict&RS2=nest | RS1=default&RS2=nest) (key SOME(nest))
B-AIS-H/CAPREP: ALL -> ALL (key ALL)
B-AIS-H/SAFEREP: ALL -> ALL (key ALL)
B-AIS-H/MREP: SOME(RS4=N&RS4s=unscoped) -> SOME(RS4=N&RS4s=unscoped) (key SOME(N ∧ unscoped))
B-AIS-H/DISC: ALL -> ALL (key ALL)
B-AIS-H/PUBRES: ALL -> ALL (key ALL)
B-AIS-H/CONTRIB: NONE -> NONE (key NONE)
B-AIS-C/CAPREP: ALL -> ALL (key ALL)
B-AIS-C/SAFEREP: ALL -> ALL (key ALL)
B-AIS-C/MREP: SOME(RS2=nest&RS4=N&RS4s=unscoped | RS2=sep&RS4=N&RS4s=unscoped) -> SOME(RS2=nest&RS4=N&RS4s=unscoped | RS2=sep&RS4=N&RS4s=unscoped) (key SOME(N ∧ unscoped))
B-AIS-C/DISC: SOME(RS2=nest) -> SOME(RS2=nest) (key SOME(nest))
B-AIS-C/PUBRES: ALL -> ALL (key ALL)
B-AIS-C/CONTRIB: NONE -> NONE (key NONE)
K1: ALL -> ALL (key ALL)
K2: SOME(RS16=coupled) -> SOME(RS16=coupled) (key SOME(coupled))
K3: NONE -> NONE (key NONE)
K4: ALL -> ALL (key ALL)
K5: ALL -> ALL (key ALL)
K6a: ALL -> ALL (key ALL)
K6b: ALL -> ALL (key ALL)
K6c: ALL -> ALL (key ALL)
K7: ALL -> ALL (key ALL)
K8: NONE -> NONE (key NONE)
K9: SOME(RS4=N&RS4s=scoped | RS4=N&RS4s=unscoped) -> SOME(RS4=N&RS4s=scoped | RS4=N&RS4s=unscoped) (key SOME(N))
K10: SOME(RS4=N&RS4s=scoped | RS4=N&RS4s=unscoped) -> SOME(RS4=N&RS4s=scoped | RS4=N&RS4s=unscoped) (key SOME(N))
K11: ALL -> ALL (key ALL)
K12: ALL -> ALL (key ALL)
K13: ALL -> ALL (key ALL)
K14: ALL -> ALL (key ALL)
K15: ALL -> ALL (key ALL)
K16: SOME(RS13=permission) -> SOME(RS13=permission) (key SOME(permission))
K17: ALL -> ALL (key ALL)
K18: SOME(RS4=N&RS4s=scoped | RS4=N&RS4s=unscoped) -> SOME(RS4=N&RS4s=scoped | RS4=N&RS4s=unscoped) (key SOME(N))
K19: SOME(RS4=N&RS4s=scoped | RS4=N&RS4s=unscoped) -> SOME(RS4=N&RS4s=scoped | RS4=N&RS4s=unscoped) (key SOME(N))
K20: ALL -> ALL (key ALL)
T1: ALL -> ALL (key ALL)
T2: NONE -> NONE (key NONE)
C1: NONE -> NONE (key NONE)
C2: NONE -> NONE (key NONE)
C3: NONE -> NONE (key NONE)
C4: NONE -> NONE (key NONE)
C5: NONE -> NONE (key NONE)
C6: NONE -> NONE (key SOME(final & bperm))  disagree, as on main
C-doc: NONE -> NONE (key SOME(final & bperm))  disagree, as on main
G1: ALL -> ALL (key ALL)
G2: ALL -> ALL (key ALL)
G3: ALL -> ALL (key ALL)
G4: ALL -> ALL (key ALL)
G5: ALL -> ALL (key ALL)
G6: SOME(RS15=explanation) -> SOME(RS15=explanation) (key SOME(explanation))
G7: ALL -> ALL (key ALL)
G8: NONE -> NONE (key NONE)
G9: NONE -> NONE (key ALL)  disagree, as on main
G10: ALL -> ALL (key ALL)
N1: ALL -> ALL (key ALL)
N2: ALL -> ALL (key ALL)
N3: NONE -> NONE (key NONE)
N4: ALL -> ALL (key ALL)
S1: ALL -> ALL (key ALL)
S2: NONE -> NONE (key NONE)
S3: ALL -> ALL (key ALL)
S4: NONE -> NONE (key NONE)
S5: ALL -> ALL (key ALL)
S6: NONE -> NONE (key NONE)
S7: ALL -> ALL (key ALL)
S8: NONE -> NONE (key NONE)
D1: ALL -> ALL (key ALL)
D2: SOME(RS10=publication) -> SOME(RS10=publication) (key SOME(publication))
D3: SOME(RS14=appointment) -> SOME(RS14=appointment) (key SOME(appointment))
D4: ALL -> ALL (key ALL)
```

## exposure.py (python3 -I .../reviews/facts-cases-diag/exposure.py openai-preparedness <sha>)

The script resolves its ref in the main checkout, so it was given this branch's commit sha. Both outputs are saved
whole next to this file, exposure-before.txt (base 26916f7349) and exposure-after.txt (1a4f7b90fe); they are not
pasted here because their rows would read as records of this report. First and last lines:

```
before: counter sha256 f4345f44  case openai-preparedness  commit 26916f7349  state run
before: 6 exposures on FACTS/CASES
after:  counter sha256 f4345f44  case openai-preparedness  commit 1a4f7b90fe  state run
after:  6 exposures on FACTS/CASES
```

The 7 rows below the first line are identical in the two files (`diff` of the outputs without their first line is
empty): this item adds no exposure.

## Accounting and records of the units this round touches

`uv run python usecases/safetyfw_accounting.py openai-preparedness --source <pinned pf-v2.txt> --check` exits 0
(101 blocks, 15 with a loss, 0 of 118 quotes unanchored). The saved report docs/usecases/safetyfw/openai-preparedness/
accounting.json was regenerated with `--report`. accounting.d1.txt changes in two lines. The new RS3=any block has
its own line, the same single entry as its twin. The twin's "Prior to" entry is gone, because those words are now in
the act. No `loss` entry was added or reworded.

The accounting line of f1-halt-strict stays as it was, although its legend now quotes those words: whether its
entries clear is the two-seat re-read's call. Omission-rule record paths of the 15 units this round touches, at the base and at HEAD, are saved in
record-paths.json (tests/omission_rule.record_paths, measured without this report). Three units gain one `plan12`
record each, the record lines the rulings ask for in PLAN 12 item 29, and the new RS3=any block has one; the two f7
mistags clear; every other unit's paths are as at the base (six of them pinned in
`test_plan12_item_29_names_only_the_units_it_records`).
spans.json still lists p10-u153 (f7-evaluations) as blocked with reason event_order and ET among its waits. Its
blocked-rule reason in build_document.py is not one of the name lists the DRI signed, and a status change belongs to the
two-seat re-read.

## Seeded bugs (each planted, its one test run, then restored with `git checkout`; tree clean after)

Command: /tmp/pf7-seeds.py (output /tmp/pf7-seeds.txt). Python product files are pf_vocabulary.py and run.py (S1,
S4, S5, S7). The rest are the VE rules (S2, S3, S6) and the saved evidence (S8).

| Seed | File | Failing test | Result |
|---|---|---|---|
| S1 f7 timing words moved into the legend (task seed a) | `usecases/openai-preparedness/pf_vocabulary.py` | `test_f7_evaluations_names_its_timing_in_the_act_and_deployment_in_the_guard` | 1 failed in 2.49s |
| S2 the f16-without-noinput rule tests `leadership_decision` alone (DRI item 3 seed) | `usecases/openai-preparedness/rules.d1.ve` | `test_touched_rules_keep_a_witness_model[f16-informed]` | 1 failed in 19.48s |
| S3 key-relevant guard of f1-misuse-bio-strict changed (task seed c) | `usecases/openai-preparedness/rules.d1.ve` | `test_touched_answers_on_a_live_query_equal_the_snapshot[A-BIO-H-EXT/MIS]` | 1 failed in 25.45s |
| S4 COMMITMENTS F7 lists only the RS3=ext block (DRI item 1 seed) | `usecases/openai-preparedness/run.py` | `test_f7_evaluations_any_is_listed_with_its_ext_twin` | 1 failed in 2.37s |
| S5 new predicate dropped from ATOMS[MIS] (DRI item 2 seed) | `usecases/openai-preparedness/run.py` | `test_touched_answers_on_a_live_query_equal_the_snapshot[A-BIO-H-EXT/MIS]` | 1 failed in 25.96s |
| S6 covered restored on f16-sag-recommend | `usecases/openai-preparedness/rules.d1.ve` | `test_f16_sag_recommend_tests_only_its_own_condition` | 1 failed in 2.97s |
| S7 board legend back to 'the Board finds it necessary' | `usecases/openai-preparedness/pf_vocabulary.py` | `test_board_guard_legend_is_the_open_term_form_with_no_decider` | 1 failed in 2.55s |
| S8 one saved answer in results.json changed (C4's `ve` NONE to ALL) | `usecases/openai-preparedness/results.json` | `test_no_pf_answer_moved_against_the_merge_base_snapshot` | 1 failed: `assert moved == []` got `['C4']` (rerun with C4's saved `ve` set to ALL) |

S1 is the task's seed (a). S2 replaces seed (b), as DRI decision item 3 says. S3 is seed (c). S4 and S5 are the seeds
DRI decision items 1 and 2 ask for (S5 shows the live moved check failing).

## Tests run

- `uv run pytest -q tests/test_pf_f7_timed_act.py tests/test_pf_fidelity_fix.py tests/test_safetyfw_accounting.py`:
  160 passed and 1 failed (the saved accounting report). After `--report`: `-k "accounting or saved or plan12 or record"`
  74 passed (/tmp/pf7-t-4.txt, /tmp/pf7-t-5.txt).
- `uv run pytest -q tests/test_rsp_fidelity_fix.py::test_regulated_predicates_stay_within_lean_limit`: 1 passed.
- `uv run python tools/trust_map.py --check`: "against 26916f73493d: K +0, S +0, D +0, G +0, tied +0, unclassified +0,
  trusted +0".
- `tools/select_tests.py --base 26916f7349` selects tests/test_pf_f7_timed_act.py, test_pf_fidelity_fix.py,
  test_safetyfw_usecases.py, test_safetyfw_accounting.py, test_usecase_key_transcription.py, test_keyed_answers_authority.py,
  test_kb10_shadow.py and test_fidmech_segment.py among 49 files.
- light-lane: NOT (2026 changed lines, most of them results.json). trust_mutants: N.A., because no Lean or trusted file
  changed (build checklist 13a is for trusted Lean growth).

## Notes for the DRI

- In-flight overlap: feature/kb-10c also edits usecases/openai-preparedness/run.py and tests/test_safetyfw_usecases.py
  (4 lines each, away from the lines changed here).
- The ruling's G1 note ("ends when a standard is specified") is in PLAN section 6, which this item may not edit; it
  is as it was.
- The `efficacy_threshold_per_safeguard` legend is still the bare pointer "4.1: third safeguard-selection step". It
  is not in this row.
- f9-specific's header and spans.json still record the order word 'then' as ET, and f9-risk-paths' spans.json entry
  keeps its `event_order` record on 'first'. The task changes only f9-risk-paths' header and legend, and the spans
  record is written by build_document.py.
- Spec re-read: A against et-5c-5d-coverage-20261115.md:37-46; B1 to B8 against pf-split-units-20261115.md:30-40; the
  allowed lists against dri-decisions-20261115-pf-f7-timed-act.md items 1 to 3.

SIZE: 67 product (usecases/openai-preparedness case files: +43 -24), 260 tests (+243 -17), 27 other hand-written
(PLAN 12) plus this report. Generated or saved evidence: results.json, coverage.json, environment.d1.json, stage0.json,
quote-hashes.json, accounting.json, lexicon-report.json, answers-at-merge-base.json (`git diff --numstat 26916f7349 HEAD`).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relay or schema changed.
2. Deliverables: PASS. See the table above; B4 is moved by DRI decision item 3. No new report test: the moved check reads saved evidence (D4).
3. Tests can fail: PASS, seeds S1 to S8 above.
4. Py/Lean/Rust agree: N.A., no checker code changed. Base against HEAD on the PF corpus: `moved: []` (`test_no_pf_answer_moved_against_the_merge_base_snapshot`).
5. R8 binding: N.A., no field read from a Lean answer changed.
6. Gate evidence: PASS for what I run. The evidence commit list comes from `main..HEAD --no-merges` (4 commits, above), on base 26916f7349. The chain runs the gate.
7. No unsigned item: PASS. No DELTA row; trust_map +0 (`tools/trust_map.py --check`).
8. User-visible change in DELTA: PASS. The only answer-bearing output, results.json, is unchanged in every answer (`moved: []`). The metric shifts are listed above.
9. Test selection: PASS. `tools/select_tests.py` selects tests/test_pf_f7_timed_act.py, the file that catches S1 to S8.
10. Lean statements: N.A., no Lean changed.
11. Budgets and deadlines: N.A., no evaluator changed.
12. CPU and memory: N.A. The PF run took 1962.9 s against 1824.5 s with the B-only tree, from one more block (two documents more). This is not measured as a benchmark.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions: PASS. f16-sag-recommend has no `covered` (and f7's blocks keep it: `test_f4_security_reads_no_coverage_condition`); f16-without keeps its guard (`test_f16_without_keeps_its_guard_until_n2_is_ruled`); the CYB-H rules keep the shared act (`test_bio_h_misuse_bullet_has_its_own_timed_act`).
15. No overclaim: PASS ("every answer": the moved test; "unchanged" exposure: the empty diff of the two outputs). No silent cut: B4 is stopped by DRI ruling. New checks can fail: S1 to S8. Limits: N.A.
