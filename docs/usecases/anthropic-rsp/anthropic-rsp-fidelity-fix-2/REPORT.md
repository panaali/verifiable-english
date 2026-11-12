# anthropic-rsp-fidelity-fix-2: REPORT

This is cycle 2 of the RSP fix cycle. It repairs the units that both seats of the 11-11 re-audit still judged
UNFAITHFUL (`debates/uc-audit-anthropic-rsp-20261111T1710Z/` in manage-agents, on VE 19013ac5f7). It also applies the
DRI's rulings on the three STOP-RULE questions. Ruling: DRI allocation 2026-11-12 item 2. The fixes are recorded in
PLAN section 12, items 20 (the fixes) and 21 (the key deviations). PLAN section 6 and `answer-key.json` are unchanged.
No ve/, lean/ or rust/ file changed.

## Plan rows delivered

All of fixes 1a to 1e, 2, 3, 4, 5, 6, 7 and 8a to 8d were delivered, and so were the DRI's rulings on questions 1 to 3.
None was cut. The checklist classes are those of `prompts/translation-fidelity-checklist.md`.

| Class | Units and items changed | Fix |
|---|---|---|
| 1 dropped clause | f10-in-line, f19-unredacted, f14-ltbt-request, f16-ask-commentary, f15-revenue-strict, f15-revenue-default, s1-advance-default, f6-keep-past, f19-brief-ltbt | The act or the legend now carries "we have in place (or plan to implement shortly)", "final", "subject to the procedures outlined below", 3.6.3's "public written report", "continuing to work with them", the four means, "at that link" and the open "including" list. |
| 4 one predicate reused | f16-ask-commentary; f26-need-not-delay on the shared `delay` act | One act now names both 3.6.2 and 3.6.3. F26's release yields to F24/F25 (DRI item 1). |
| 7 invented guard | f25-meet, f25-delay, f26-effort, f26-need-not-delay; f15-select-approval; f10-in-line | The fact guards `competitors_strong_measures` and `competitor_better_mitigation` are removed (from the vocabulary as well). F15 has no "after". F10's guard is no longer broader than its source. |
| 7 inaccurate limit (run.py) | K15a, K17, K12a, K12b | These are answered from `f20-notify-board`, `f23-publish` and `f15-select-approval`. The remaining K limits are one table (`run.K_LIMITS`: K9 and K10). |
| 8 case facts | K20, K21a, K21b | A scenario is a label (`run.SCENARIOS`), not an atom. Cases set only the evidence PLAN 5 stipulates. |
| 9 invented reading | FACTS (`s2-suff-result`, `s2-only-if-result`); f26-need-not-delay under RS4 = rel | RS3c = result is excluded (DRI item 2). Under rel, F26 releases only its own scenario's delay (DRI item 1). |
| 10 key cells | K18, T7, C1, C7, C-doc | PLAN 12 item 21 records these deviations, and `run.compare` reads that table. The frozen key is untouched. |
| 11 elided quote | f10-in-line, f14-ltbt-request, f15-select-approval, f16-ask-commentary, f19-brief-ltbt, f19-unredacted, s1-advance-default, f6-keep-past, f26-need-not-delay, s2-suff-third | Each header quotes its whole sentence. |

Blocks not named in the task that changed only through a shared legend: the `external_review_process` legend (which
now includes an LTBT-requested review) is read by f16-before-board-default, f16-all-sections, f16-split-p and
f16-only-legal. Their rule text is unchanged. `s2-only-if-third` lost its `RS3c=third` tag (RS3c is no reading set).

Regulated predicates: **64 of 64**. The one new predicate, `mitigation_in_place_or_planned`, is an uncapped
situation classification. Two base predicates were removed.

## Answer changes (main's `results.json` -> this branch)

| Item | Key | Old | New | Cause |
|---|---|---|---|---|
| K15a | ALL | UNDECIDED | ALL | fix 2: answered by f20-notify-board |
| K17 | ALL | UNDECIDED | ALL | fix 2: answered by f23-publish |
| K12a, K12b | ALL | UNDECIDED | ALL | fix 6 (the act is unordered), so the "share one act" limit (fix 2's class) is gone |
| K18 | ALL | ALL | NONE | fix 3. Key deviation (DRI, `-k18.md`): the case leaves the in-place-or-planned status open. |
| T7 | SOME(result) | SOME(RS3c=result …) | NONE | DRI item 2: RS3c = result is excluded |
| C1, C7 | SOME(rel) | SOME(RS4=rel) | NONE | DRI item 1: F24/F25's delay prevails over F26's release |
| C-doc | SOME(rel) | SOME(… RS4=rel …) | NONE (CONFLICT-FREE) | DRI item 1 |
| T2b, T4b | SOME(iffo), SOME(iffo ∧ iffi) | agree | agree | the condition is restated without RS3c |

These items did not move: K20 ALL, K21a ALL, K21b NONE, K22b NONE, C3 NONE, C5 NONE, C6 NONE, K11 ALL, G1 ALL, N2 ALL
and N3 ALL all agree; G5, G6 and N4 stay UNDECIDED, because their limits (ET, SC) are untouched by fixes 6 and 7.

Score against the frozen key: 111 -> **110 / 126**; faithful undecided: 15 -> **11**. The 5 other non-agreeing rows
(K18, T7, C1, C7, C-doc) answer exactly as PLAN 12 item 21 rules, and their `cause` cites it. That makes
**115 / 126** against the key as corrected there. This is an estimate until the re-audit; nothing is claimed before it.
Removing N1 changes 53 cells (was 54). With m1 limited to step 5's precedence and m3's expected list `["N2"]`, the six
mutants still change exactly their named results. m3's named "C1, C7 and C-doc become NONE" now holds without the mutant.
Span accounting: the byte statuses are unchanged (CHECKED 5,327 bytes), and there is one unresolved reading set fewer
(`t4-continuation` is now a condition). Source accounting: blocks with a loss went from 9 to 6, and
`docs/usecases/safetyfw/anthropic-rsp/accounting.json` was re-saved by its tool with `--source`.

## Open list (questions sent and their answers)

1. C1/C7/C-doc (f26-need-not-delay's release). Answered in manage-agents
   `reviews/dri-decisions-20261112-anthropic-rsp-fidelity-fix-2.md` item 1 (SIGNED by the DRI): non-overriding;
   C1, C7 and C-doc are NONE. Done as a precedence (`rsp_translation.PRECEDENCE`).
2. K18. Answered in `…-fix-2-k18.md` item 1 (SIGNED by the DRI): a K finding, NONE, with the case unchanged.
3. FACTS/T7. Answered in `…-fix-2.md` item 2 (SIGNED by the DRI): RS3c = result is excluded; T7 is NONE; FACTS is repaired here.

No question is open. The DRI's tests-must-stay-selected conditions are met: `test_section_6_is_the_frozen_key`,
`test_transcription_is_pinned` and `test_every_answer_key_cell_equals_its_section_6_cell` are unchanged.

## Tests

New tests are in `tests/test_rsp_fidelity_fix.py` (fix-2 section):
- `test_no_predicate_restates_the_fact_an_evidence_term_is_about` (the class: no vocabulary twin of an evidence term)
- `test_appendix_a_guards_are_the_evidence_alone`
- `test_cases_set_only_declared_atoms_and_the_stipulated_evidence`
- `test_no_k_limit_hides_an_answer_the_selected_rules_give` (the class: every K limit is checked against what the rules alone answer)
- `test_f10_in_line_guard_is_live_both_ways`
- `test_acts_and_legends_carry_the_restored_qualifiers`
- `test_f26_release_yields_to_f24_and_f25`
- `test_rs3c_result_is_never_offered` (with a fixture that re-offers it three ways)
- `test_t7_answers_none`
- `test_key_deviations_are_plan_section_12s_and_the_saved_causes_cite_them`
- `test_regulated_predicates_stay_64_after_fix_2`

These existing tests changed because they pinned results that the fixes or rulings move:
- In `tests/test_safetyfw_usecases.py`:
  - `test_rsp_every_rule_and_premise_parses_with_one_reading`: 15 -> 12 premises.
  - `test_rsp_n1_filters_all_rs0_definition_premises`: two blocks removed.
  - `test_rsp_n1_counterfactual_removes_t_family_definition[T7-T7]`: T7 is now NONE.
  - `test_rsp_n1_saved_comparison_includes_t_family`: 54 -> 53.
  - `test_rsp_run_recomputes_every_key_item_and_records_causes`: a disagreement is allowed only as a PLAN 12 deviation; M8 lists the undecided rows.
  - `test_rsp_independent_reference_and_comparator_catch_wrong_answers`: the reference reports C1, C7 and C-doc.
- Cycle 1's `test_f25_quantifies_over_each_competitor_and_n3_enumerates_rs5`: F25's delay is checked by a query.
- Cycle 1's `test_c_doc_checks_the_f13_f16_pair_over_plan_m2s_cone`: C-doc is NONE.

No test was removed.

## Seeded bugs (each planted in Python or a case file, the test run, then restored with `git checkout`)

| Bug | File | Failing test |
|---|---|---|
| (a) `competitors_strong_measures` back on f25-delay (with its vocabulary entry) | rules.d1.ve, rsp_vocabulary.py | `test_no_predicate_restates_the_fact_an_evidence_term_is_about`, `test_appendix_a_guards_are_the_evidence_alone` |
| (b) `competitor_better_mitigation` back on f26-effort | rules.d1.ve, rsp_vocabulary.py | the same two |
| (c) K21's case gets the fact atom again | run.py | `test_cases_set_only_declared_atoms_and_the_stipulated_evidence` |
| (d) K15a's hard-coded limit restored | run.py | `test_no_k_limit_hides_an_answer_the_selected_rules_give` |
| (e) "final" dropped from f19-unredacted | rsp_vocabulary.py, rules.d1.ve | `test_acts_and_legends_carry_the_restored_qualifiers` |
| (f) "after consulting the Board" restored in f15-select-approval | rsp_vocabulary.py, rules.d1.ve | the same |
| (g) "continuing to work with them" dropped | rsp_vocabulary.py | the same |
| DRI k18: clause (b)'s `mitigation_in_place_or_planned` dropped from f10-in-line | rules.d1.ve | `test_f10_in_line_guard_is_live_both_ways` (K18 answers ALL) |
| DRI 1: the universal release restored (no F24/F25 precedence) | rsp_translation.py | `test_f26_release_yields_to_f24_and_f25` (C1 holds under rel) |
| DRI 2: RS3c = result offered again | rsp_translation.py | `test_rs3c_result_is_never_offered` |
| K12's limit restored | run.py | `test_no_k_limit_hides_an_answer_the_selected_rules_give` |

There are no Lean or Rust changes, so there are no seeded bugs in those languages.

## Trust, DELTA, mutants

`tools/trust_map.py --check` against e78b6d94 gives K +0, S +0, trusted +0 (PASS). There is no new trusted definition,
so no R16 mutants and no `mutants.json`. There is no DELTA: no user-visible product delta.

## Budget readings

- The DRI admitted the first build on a VM1 reading: 12.02M of 14M left at 04:40Z 2026-11-12 (`fix-budget/admitted`).
- I ran the check once, read-only, before reading the task's "do not run it yourself" line: `ucfix-budget.py --check` at
  about 04:44Z printed "joint allowance left 11.98M of 14M; round budget 1.00M (ALLOCATED): START", exit 0.
- There was no `anthropic-rsp-fidelity-fix-2-loop.log` to read.

## Size

There are about 520 hand-written changed lines outside generated files, including this report. That is over the
task's ~400. The overrun is the DRI's three rulings, which the decider assigned to this item: the precedence, the RS3c
removal, the PLAN 12 key-deviation table and its reader, and their tests.

## Next item

The re-audit, in the usecase-rsp-reaudit form (`zsh uc-audit.sh anthropic-rsp main 3` on the merged commit), launched
by the DRI decider when Codex has room. Its C1, C7, C-doc, K18, FACTS and T7 rows are checked against PLAN 12 item 21.
