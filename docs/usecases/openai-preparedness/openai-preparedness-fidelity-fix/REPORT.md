# openai-preparedness-fidelity-fix: REPORT

No DRI signature needed: no DELTA row (no `ve/`, `lean/` or `rust/` change), no stop-rule item, no key edit.

Item: the T fixes and K findings of the use-case audit for the OpenAI Preparedness Framework v2 (DRI decision
2026-11-10 23:46Z, reviews/dri-decisions-20261111-ucfix-cycle.md item 2; classification
reviews/ucfix-classify-20261111.tsv, rows `openai-preparedness`: 52 units, 50 items). Branch
`infra/openai-preparedness-fidelity-fix`.

SIZE: 547 product (`rules.d1.ve` 198, `pf_vocabulary.py` 143, `run.py` 130, `build_document.py` 60,
`pf_translation.py` 12, `facts.d1.ve` 4), 362 tests (`tests/test_pf_fidelity_fix.py` 347, `tests/test_safetyfw_usecases.py` 15),
about 80 + this REPORT other hand-written lines (PLAN section 12 47, README.md 30, docs/usecases/safetyfw/REPORT.md 2). Source: `git diff --numstat $(git merge-base HEAD main)`
(added + deleted). Generated, by the case's own scripts only: `environment.d1.json` (pf_vocabulary.py),
`spans.json`, `coverage.json` (build_document.py), `docs/usecases/safetyfw/openai-preparedness/{units,gaps}.json`
(measure.py), `docs/usecases/safetyfw/openai-preparedness/stage0.json` (stage0.py: P5 bytes, P7 regulated
predicates 58 -> 59), `results.json` (run.py).

DELTA: none (no product code under `ve/`, `lean/` or `rust/` changed).

## Deliverables, in the task's order

| Step | Deliverable | Commit | Test |
|---|---|---|---|
| 1 | f1 x8 "meeting the High standard" (C.1, C.2, C.3) | c1f86ba3b6 | `test_table_1_acts_name_the_high_standard` |
| 1 | f2 x4 "sufficiently minimizing severe-harm risk", f3 x5 "sufficient safety as well as security controls" | c1f86ba3b6 | `test_f2_f3_acts_carry_the_sufficiency` |
| 1 | f11-exception's precedence over f2-no-deploy and f2-no-deploy-any (`f11-exception-deploy`, pf_translation.PRECEDENCE) | c1f86ba3b6 | `test_f11_exception_precedes_every_f2_deployment_rule`, `test_c1_is_conflict_free_on_every_choice` |
| 1 | the run asks the corrected acts (A-*/SUF, MIS, ALN) | c1f86ba3b6, 2c84d2bdf4 (m3) | same two tests read `run.ATOMS` |
| 2 | f7-report "as well as decide on next steps"; `f7-compile` (+1 regulated predicate); CAPREP and K4 ask it | c1f86ba3b6 | `test_capabilities_report_items_ask_the_compilation_sentence` |
| 2 | f15-disclose (release; content list in the legend; major_deployment decider "unstated", OT13); f15-safeguards ("to sufficiently minimize associated risks"; the redaction sentence in the legend) | c1f86ba3b6 | `test_every_header_quotes_whole_source_text`; run.py PUBRES/DISC (results.json) |
| 3 | f11-within/acknowledge/protect/share, f6-rel, f8-start, f9 x4, f14 x4, f16-chair x2, cl4-persuasion, f12 x6 (K10), C1, N3 | c1f86ba3b6, 2c84d2bdf4 | run.py N3 (`run.COMMITMENTS`), K10, C1 rows of results.json; header test |
| 4 | c2 x2, f5-checkpoint (legend: 4816e211da), f13-review, f16-sag-recommend, f16-final (excluded reading), f16-process (no rule), f16-board-reverse + f16-board-mandate | c1f86ba3b6, 4816e211da | `test_rs11_final_is_excluded_and_no_rule_of_it_returns` |
| 4 | G7 (fact `fn5-indicator`, two finite models) and N4 (premise `cl-levels`, entailment certificate): both routes accepted in D1, no product change | 2c84d2bdf4 | results.json G7, N4 = ALL |
| K | PLAN 12 items 19 (C6, C-doc: NONE) and 20 (G9: SOME(P ∨ scoped)); item 18 the excluded reading | 4816e211da | `test_k_entries_are_the_saved_answers` |
| Key | answer-key.json equals section 6 cell by cell except the six B-*/MREP findings of PLAN 12 item 15 | c5ca07a749 | `test_answer_key_equals_section_6_cell_by_cell`, `test_the_cell_comparison_catches_one_changed_cell` |

Every unit of the .tsv was fixed; none needed a language feature. Beyond the .tsv, seven old headers that cut their
quote ("…" or a fragment: f7-evaluations, f10-validate, f10-review, f16-year, f16-ssc-visibility, f5-ambiguous,
f13-results) and the three f17 headers (no quote) now quote the whole sentence, so the class 11 test covers every
block of rules.d1.ve and facts.d1.ve.

## Per checklist class (prompts/translation-fidelity-checklist.md)

A unit can answer several classes (the .tsv's `checklist_class`); counts are units.

| Class | Units | Fix |
|---|---|---|
| 1 dropped conjunct or clause | 42: f1 x8, f2 x4, f3 x5, f7-report, f8-start, f9 x4, f14-document, f14-investigate, f14-corrective, f15-disclose, f15-safeguards, f16-sag-recommend, c2 x2, cl4-persuasion, f16-board-reverse, f5-checkpoint, f11-within, f11-exception, f12 x6 | the act (or its legend, where 80 characters or a reserved word forbid it) carries the dropped words: the standard, the sufficiency, "decides on next steps", "with reasoning", "appropriately", "proportional", "and executing severe harms", "and/or propensity", "appropriate US government actors", "in that capability area", the Board's second alternative |
| 2 quantifier scope | 5: f9-residual x2, f9-risk-paths, f9-specific, f14-investigate | "based on the deployment", "in the proposed deployment", "each risk path"; f14-investigate's guard is any reported or otherwise identified potential noncompliance |
| 3 exclusive "only" and closed lists | 10: f14-summary, f15-disclose, f15-safeguards, f11-within, f11-exception, f11-acknowledge, f11-protect, f11-share, f12-sandbagging x2 | "but only if" duties on the marginal-risk adjustment; F11's exception over every F2 rule; f14-summary's carve-out narrowed to `beyond_sensitive_limits`; K10's "A, or B" as "A unless B" |
| 5 modal strength | 3: f16-final, f16-process, f6-rel | no invented prohibitions; f6's carve-out is "reason to believe" (decider `we`, OT20) |
| 7 invented guards | 16: f8-start, f14-summary, f15-disclose, f15-safeguards, f16-final, f16-process, f16-board-reverse, f16-chair x2, f6-rel, f11 x5, f13-review | likely_to_cross decided by `we` (OT9); no fast_track_requested guard; no research_category_review guard; major_deployment's decider unstated (OT13) |
| 9 readings that manufacture conflicts | 2: f16-final, f16-process | RS11 = final excluded (PLAN 12 item 18); RS11 = process selects no rule |
| 10 key cells | 0 units; items C6, C-doc, G9 | PLAN 12 items 19, 20 (section 6 not edited) |
| 11 elided quotes | 25 of the .tsv + the 10 headers above | each header quotes the whole sentence; `test_every_header_quotes_whole_source_text` |

Classes 4, 6 and 8: no unit of this case.

## Answer changes per case (main -> HEAD)

Command: `uv run python usecases/openai-preparedness/run.py` (wrote results.json: "230 / 239 (1971.0 s)"), then a
comparison of `git show main:usecases/openai-preparedness/results.json` with it (script in this session's log):

| Item | main | HEAD | Unit |
|---|---|---|---|
| C6 | SOME(RS11=final & RS17=bperm), agrees | NONE, key finding (PLAN 12 item 19) | f16-final removed (RS11 = final excluded) |
| C-doc | SOME(final & bperm & ...), agrees | NONE, key finding (item 19) | f16-final, f16-process removed |
| G9 | ALL, agrees | SOME on all choices but RS4 = N ∧ RS4s = unscoped, key finding (item 20) | SAFEGUARD_PREDICATES + nuclear act (f12-nuclear-unscoped) |
| G7 | UNDECIDED | ALL, agrees | fn5-indicator |
| N4 | UNDECIDED | ALL, agrees | cl-levels |

Same verdict, different rule or act asked: B-*/CAPREP x7 and K4 now select `f7-compile` (was `f7-report`); N3's
witnesses are PLAN 4.2's commitments (`run.COMMITMENTS`); every A-*/SUF, MIS, ALN item asks the corrected act;
B-*/PUBRES and DISC ask the corrected release and disclosure acts. Score: 231 -> 230 of 239 against the frozen key;
the 9 disagreements are the six B-*/MREP transcription findings (item 15) and the three K findings, and each names
its cause. Mutants m1 to m6 still each change exactly their named results (`results.json` `mutants`: all `exact`);
without N2 the changed items are C-doc and C2.

The K entries agree with the run: results.json gives `ve` NONE for C6 and C-doc, and G9's 96 choices hold exactly
when RS4 = P or RS4s = scoped (32 N/scoped, 32 P/scoped, 32 P/unscoped hold; N/unscoped does not), checked by
`test_k_entries_are_the_saved_answers`.

Items recovered: the .tsv's ceiling is 68 -> 228 audit-verified; the re-audit decides.

## Regulated predicates

59 of 64 (main: 58): +1 `capabilities_report_submitted` (f7-compile), +1 `revised_course_mandated`
(f16-board-mandate), -1 `process_change` (f16-process removed). Command: count of `regulated` entries in
`environment.d1.json`'s vocabulary at main and HEAD.

## K entries (PLAN section 12; KEY-FREEZE.md: no section-6 or answer-key.json cell changed)

- Item 19: C6 and C-doc are NONE, not SOME(final ∧ bperm); source "Where necessary, the Board may reverse a decision
  and/or mandate a revised course of action."
- Item 20: G9 is SOME(P ∨ scoped), not ALL; source Table 2's Nuclear and Radiological row, which states no condition.
- `test_section_6_is_the_frozen_key` and `test_transcription_is_pinned` are unchanged.

## F list

Empty: no unit needed a language feature, and G7 and N4 were answered in D1 without a product change.

## Seeded bugs (each planted, its test run, then restored with `git checkout`)

| | Bug | File | Failing test |
|---|---|---|---|
| a | drop "meeting the High standard" from the misuse act | usecases/openai-preparedness/pf_vocabulary.py | `tests/test_pf_fidelity_fix.py::test_table_1_acts_name_the_high_standard` |
| b | drop the sufficiency from the F2 act | usecases/openai-preparedness/pf_vocabulary.py | `::test_f2_f3_acts_carry_the_sufficiency` |
| c | restore RS11 = final in READING_SETS | usecases/openai-preparedness/pf_translation.py | `::test_rs11_final_is_excluded_and_no_rule_of_it_returns` |
| d | remove f11-exception-deploy's precedence over f2-no-deploy | usecases/openai-preparedness/pf_translation.py | `::test_f11_exception_precedes_every_f2_deployment_rule` |
| e | add a "soft" to K1 in answer-key.json (a non-MREP cell) | usecases/openai-preparedness/answer-key.json | `::test_answer_key_equals_section_6_cell_by_cell` |
| f | point CAPREP back at the SAG-review act | usecases/openai-preparedness/run.py | `::test_capabilities_report_items_ask_the_compilation_sentence` |

| g | the word-map gate back to rules only (`kind == "rule"`) | usecases/openai-preparedness/build_document.py | `::test_a_fact_anchored_on_a_partly_translated_unit_is_blocked` (`'kind': 'asserted', 'premises': ['cl-levels']`) |
| h | HEAD 5579e976's spans.json (p15-u245 CHECKED) | usecases/openai-preparedness/spans.json | `::test_every_checked_unit_is_a_rule_or_fact_with_a_complete_word_map`, `::test_change_log_removal_of_low_and_medium_is_a_blocked_unit` ("2 failed") |

Each run printed "1 failed"; (a) failed on `assert 'meeting the High standard' in '{0} have misuse safeguards'`,
(f) on `['f7-compile', 'f7-report'] == ['f7-compile']`. Python is the only language of product code changed.

## Existing tests changed

In `tests/test_safetyfw_usecases.py` (pf_* tests only; no test removed):
- `test_pf_rs13_and_untranslated_claims_have_named_residuals` pinned the old, unfaithful carve-out name
  `highly_sensitive`; it now names `beyond_sensitive_limits` (f14-summary).
- `test_pf_run_recomputes_every_key_item_and_records_causes` pinned the six B-*/MREP rows as the only disagreements;
  it now also expects C6, C-doc (PLAN 12 item 19) and G9 (item 20), each with cause "key finding".
- `test_pf_translation_lint_and_invention_audit` pinned the unanchored fact blocks; `fn5-indicator` (G7) joins them.

Found by the first selected run and fixed (the commit after db649565b7): `conformance/english-lean/lexicon-report.json`
regenerated (`uv run python -m conformance.english_lean_lexicon`); `build_document.py` keeps the residual id
`unmapped_duty-p6-u84-789e5489dfdf` the footnote 5 unit had on main now that the unit is the blocked rule
`fn5-indicator`; README.md's coverage and answer tables and docs/usecases/safetyfw/REPORT.md's PF row follow the
regenerated coverage (f7-compile's unit moves from SC to ET; the CHECKED 170 -> 344 bytes this commit recorded for
`cl-levels` was the overclaim the review's F1 found, undone below).

## Review fix (openai-preparedness-fidelity-fix-review.final.md)

| Finding | Fix | Regression tests | Commit |
|---|---|---|---|
| F1 (A, overclaim): `cl-levels` in FACT_ANCHORS made p15-u245 (change log item 2, its "because" clause untranslated) CHECKED, 170 -> 344 bytes | Class: anchored facts skipped the word map a CHECKED rule needs. Fact blocks now pass the same `CHECKED_CLAUSES` gate as rules (Table 1's six labels have maps; a fact without a complete map is placed as a blocked rule); `cl-levels` is a blocked unit like `fn5-indicator` and keeps main's residual id `unmapped_duty-p15-u245-b1881efef95f`. Found by the replanted bug: `BLOCKER_FAMILY` was a hand-copied subset of `BLOCKER_DETAIL`'s families without `unmapped_duty`; it is removed, `BLOCKER_DETAIL` owns each family. spans.json, coverage.json, units/gaps/stage0.json regenerated (CHECKED 170 bytes, 7 units, as on main); README (coverage table, AP row), the safetyfw REPORT PF row and PLAN 12 item 21 follow. N4 is unchanged: the fact stays selected. | `tests/test_pf_fidelity_fix.py::test_every_checked_unit_is_a_rule_or_fact_with_a_complete_word_map`, `::test_change_log_removal_of_low_and_medium_is_a_blocked_unit`, `::test_a_partial_fact_word_map_is_not_complete`, `::test_a_fact_anchored_on_a_partly_translated_unit_is_blocked`, `::test_every_blocked_reason_has_one_named_family`; `tests/test_safetyfw_usecases.py::test_pf_translation_lint_and_invention_audit` expects `cl-levels` unanchored | 989862dbe1, 4bd4c5afc2 |

PROBE F1 failed before the fix (`AssertionError: {... 'premises': ['cl-levels'], ... 'status': 'CHECKED'}`) and
passes after it (`status` UNFORMALISED, `blocked_rule` cl-levels). DELTA: none (no `ve/`, `lean/` or `rust/` change).

## Notes for the DRI

- f11-acknowledge, f11-protect, f11-share: the .tsv proposed the guard `adjustment_confirmed ∧ adjustment_conditions`.
  `adjustment_conditions`' legend is 4.3's three conditions themselves (acknowledgement and protection included), so
  that guard would make each duty follow from its own fulfilment. The source's "we could adjust ... but only if" puts
  the conditions on making the adjustment: the guard is `adjustment_made` (its legend now 4.3's marginal-risk
  adjustment, "in that capability area") ∧ `adjustment_confirmed`. K6a to K6c agree.
- f16-process: of the .tsv's two options ("a duty quoting the sentence, or no rule") I took no rule: the sentence
  assigns Leadership a role and states no norm, and no item asks for one (the narrower reading).
- `pf_vocabulary.py` has no `--check`: its writer always writes `environment.d1.json`.
- `reference.py` (the key's independent check, not edited: one owner) still derives C6, C-doc and G9 from PLAN 3.1
  as written, so it agrees with the frozen key cells there and not with PLAN 12 items 19 and 20;
  `test_pf_independent_reference_and_comparator_catch_wrong_answers` still lists only the six B-*/MREP rows.

## Next item

usecase-pf-reaudit: `zsh uc-audit.sh openai-preparedness main 3`, launched by the DRI decider after this merge.

## Tests run

1. `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` at b58ff0b36c (REPORT commit):
   the fast stage failed `tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon`
   (the committed lexicon report hashes the case's environment). Fixed in db649565b7.
2. The same selection at db649565b7: shards 1 and 2 passed (14 and 13 units); shard 3 "4 failed, 101 passed" in
   tests/test_safetyfw_usecases.py (test_pf_every_byte_has_ve_status_and_one_unit,
   test_pf_rs13_and_untranslated_claims_have_named_residuals, test_pf_run_recomputes_every_key_item_and_records_causes,
   test_pf_translation_lint_and_invention_audit). Fixed in 54764194a5; locally "4 passed, 101 deselected".
3. `mac-pytest.sh -- -q tests/test_safetyfw_usecases.py tests/test_english_lean_lexicon.py tests/test_pf_fidelity_fix.py`
   at 54764194a5: "1 failed, 175 passed" (test_pf_stage0_and_gaps: stage0.json stale since the WIP commits). Fixed
   in d7b10121.
4. `mac-pytest.sh -- -q tests/test_safetyfw_usecases.py::test_pf_stage0_and_gaps` at d7b10121: "1 passed", exit 0;
   `stage0.py`, `build_document.py` and `measure.py --check` exit 0 locally.

5. Review fix: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` at 989862dbe1: shards 1 and 2
   passed (16 and 12 units); shard 3 "1 failed, 104 passed" (test_pf_every_byte_has_ve_status_and_one_unit: README's
   AP row still had HEAD's 118 units). Fixed in 4bd4c5afc2; the failed test and the other PF README test then
   "2 passed". The five new tests and the lint test: "22 passed" locally; `build_document.py --check` exit 0;
   `lake build` "Build completed successfully"; `lean/audit.py` PASS.

No test in main-known-red.txt was involved.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relay or schema changed.
2. Every deliverable built: PASS, the deliverables table above (each row with commit and test).
3. Tests can fail: PASS, seeded bugs a to f; `test_the_cell_comparison_catches_one_changed_cell` (a changed value
   and a removed field are caught); `test_a_cut_altered_or_missing_quote_is_a_fault`.
4. Python, Lean and Rust agree: N.A., no checker code changed; run.py's base run main vs HEAD compared above.
5. R8 binding: N.A., no Lean answer field read.
6. Gate evidence matches HEAD: PASS for the tests run (see "Tests run"); the chain runs the gate on the final HEAD.
7. No unsigned item: PASS, no DELTA row.
8. Every user-visible change in DELTA: N.A. for product code; the use case's answer changes are in this REPORT.
9. Test selection: PASS, `tools/select_tests.py --base $(git merge-base HEAD main)` selects
   tests/test_pf_fidelity_fix.py and tests/test_safetyfw_usecases.py.
10. Lean statements: N.A., no Lean change.
11. Budgets fail closed: N.A., no budget code; N4's route reports UNDECIDED ("resource limit") without a certificate
    (run.low_medium_never).
12. No CPU or memory regression: N.A., no checker code; run.py took 1971 s (main's results were not timed here).
13. Test-removed trailer: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. Opposite directions: the cell test accepts the key and
    refuses a changed cell; the quote test accepts every header and refuses cut, altered and missing quotes;
    `test_rs11_...` requires RS11 = process to stay offered. Spec re-read: the K entries against PLAN.md section 12
    items 19 and 20 and section 6.5/6.6; the act phrases against the pinned pf-v2.txt (header test).
15. No overclaim / no silent cut / checks can fail / limits charged: PASS; nothing deferred, seeded bugs a to f;
    limits N.A.
