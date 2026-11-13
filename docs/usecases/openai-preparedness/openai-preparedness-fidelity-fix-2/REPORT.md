# openai-preparedness-fidelity-fix-2: PF union-rule fix, round A (12 units)

DRI signatures reserved: none. Open: f3-develop-inuse(-forecast) C7 (the situation sort's legend "of a covered model"), moved to openai-preparedness-fidelity-fix-3 by reviews/dri-decisions-20261112-openai-preparedness-fidelity-fix-2-q3.md item 1 (STOP RULE question 3, ruled (b)); the legend is unchanged here.
Status: all 12 units fixed in batch order (5 batches, one commit each, then tests and regeneration); no ve/, lean/ or rust/ change; no key edit; DELTA: none.
Answers: no item's VE answer changed: 236 of 239 agree before and after (run.py; diff of `comparison` against main's results.json, empty). Mutants m1 to m6 still change exactly their named results.
Union count (PROJECTED, the re-read decides): 87 after batches 1 and 2, 90 after batch 3 (C4, K3, K16), up to 93 after batch 4 (K9, K10, K12) and 94 after batch 5 (N4) if a blind read clears those items.
Regulated predicates: 60 of 64 (59 before). Next: the production checklist pass re-reads only the changed units (addendum 8 item 56), launched by the DRI decider.

## Units changed, by checklist class

| Unit (block) | Finding (seat, where) | Fix | Classes answered |
|---|---|---|---|
| f3-develop-inuse | (a) Astra r1, Opus r2 (1718ZA): R:48 requires controls "during development" when only internal_deployment holds; (b) sess-3 C1/C4: "preserves neither additionality nor the internal-use timing" | the block keeps the body's development branch only (guard further_development); the heading's internal use is the new block `f3-inuse` with its own act `safeguards_before_internal_use`, "additional safety as well as security controls before internal use"; both legends quote 4.4's "additional safeguards (safety and security controls)" | 1, 4, 11 (C7 moved to fix-3, question 3 ruled (b)) |
| f3-develop-inuse-forecast | the same, forecast branch (R:50) | the same on the forecast branch; new block `f3-inuse-forecast` | 1, 4, 11 (C7 moved to fix-3) |
| f11-exception | (a) Opus r1-3 class 2: one area's confirmed scenario "releases every area"; (b) sess-7 C1/C2: R:136 releases "the entire situation's safeguard-sufficiency obligation" | the release holds when a reached level is in an area whose confirmed scenario the situation adjusts (new relation `adjustment_area`, "{0} adjusts {1}", legend "that capability area"), unless another reached level is in no such area | 2, 7, 11 |
| f11-exception-deploy | (a) Opus r1: "a bare permission to deploy at any level"; (b) sess-7 C1/C2/C5 | the same area bound on "may be deployed"; its precedence over f2-no-deploy(-any) therefore reaches only the confirmed area | 2, 5, 7, 11 |
| f6-rel | (a) Astra r1, Opus r2: V:70 "derives from a model determined below High" is broader; (b) sess-7 C1/C3: omits OpenAI and the three methods | guard class renamed `distilled_finetuned_or_quantized_from_below_high`, legend "a model that OpenAI distills, fine-tunes, or quantizes from a model that was previously determined not to cross a High capability threshold (footnote 6)"; "generally" and the significant-increase carve-out kept | 3, 1 |
| f14-summary | (a) both seats r1: only "testing results"; employee_request guard; (b) sess-5 C1/C7 | act "have employees request as well as receive the testing as well as SAG summary" (80 characters, the limit); legend quotes the full 5.1 sentence; no request guard; beyond_sensitive_limits stays the carve-out | 1, 7 |
| f12-undermining | (b) sess-9 C1: "replaces the source's alternative with a conjunction"; (a) Astra r1-2 | act "have a safeguards case robust to what was discovered"; legend quotes the Table 2 sentence with "and/or" | 1, 5 |
| f12-undermining-unscoped | the same (R:160) | the same | 1, 5 |
| f12-sandbagging | (a) Astra r1-3 and relay: "a conditional obligation to perform one particular alternative"; run.py's bound-is-false assumption | one duty `sandbagging_response`, act "have sandbagging handled", legend quoting the row's two alternatives; carve-out, its open term `conservative_upper_bound_used` and run.py's `ALTERNATIVES` removed; PLAN 12 item 23 amends item 22 | 1, 5, 7, 8 |
| f12-sandbagging-unscoped | the same (R:152, no guard) | the same | 1, 5, 7, 8 |
| f16-year | (a) Astra r1, Opus r2: drops the object; (b) sess-7 C1/C2: object, purpose, and per-situation scope | a duty of the Framework itself, once: new one-member sort `framework`; "Every framework must be reviewed at least once a year as to its continued sufficiency"; legend quotes Appendix B's sentence; "potentially update" is no duty | 1, 2 |
| FACTS | (a) Astra r1-3, Opus r2-3; (b) sess-9 C7: facts.d1.ve exceeds its stated inventory | `cl-levels` and `fn5-indicator` moved to rules.d1.ve, each under its own `## <id> \| always \| <source sentence>` header (their texts unchanged); facts.d1.ve holds exactly the six levels, rs2-nest and no-critical-models; N4's record names `cl-levels` and G7's rows name `fn5-indicator` (review F1), both derived by `run.premise_units` from the route's goal | 7 |

Counts per class (units): class 1: 9; class 2: 3; class 3: 1; class 4: 2; class 5: 5; class 7: 6; class 8: 2; class 11: 4 (every changed or new rule block quotes its full source sentence; checked by `test_every_header_quotes_whole_source_text` on the regenerated quote evidence).

Blocks changed only because a named fix moved what they read: none. New blocks: `f3-inuse`, `f3-inuse-forecast` (RS18 = inuse). Shared vocabulary changed: `safeguards_during_development`'s legend (also read by round-B f3-develop, f3-develop-forecast, f3-reminder; their rule text is unchanged and the legend keeps 4.2's and Appendix C's wording beside 4.4's), and the new `framework` sort.

## Batches: PROJECTED union count after each

Each batch ran `run.py` (the case's own harness, base comparison; batches 2 to 5 through a helper that diffs every item's `ve` against main's results.json). Answer changes old -> new: none in any batch.

| Batch | Units | run.py | Answer changes | PROJECTED union count |
|---|---|---|---|---|
| 1 | f3-develop-inuse, -forecast | 236 / 239 | none | 87 (their 30 and 27 counted answers also rest on round-B units) |
| 2 | f11-exception, -deploy | 236 / 239 | none (C1 NONE -> NONE) | 87 |
| 3 | f6-rel, f14-summary | 236 / 239 | none (C4, K3, K16 unchanged) | 90: C4, K3 (f6-rel), K16 (f14-summary) |
| 4 | f12-undermining(-unscoped), f12-sandbagging(-unscoped), f16-year | 236 / 239 | none (K9, K10 SOME(N), K12 ALL) | 90; up to 93 if a blind read clears K9, K10, K12 |
| 5 | FACTS | 236 / 239 | none (N4 ALL) | 90; up to 94 with N4 likewise |

Old -> new for the items the task names (all unchanged; values from main's and HEAD's results.json `comparison`):
every A-*/SUF item (28, including the 6 A-*-C-INT/LINT/SUF items, still SOME(inuse ∨ (nest ∧ any)) by choice, now reached through `f3-inuse`); C1 NONE -> NONE; C4 NONE -> NONE; G1 ALL -> ALL; G5 ALL -> ALL; G10 ALL -> ALL; K3 NONE -> NONE; K9 SOME(N) -> SOME(N); K10 SOME(N) -> SOME(N); K12 ALL -> ALL; K16 SOME(permission) -> SOME(permission); N3 NONE -> NONE; N4 ALL -> ALL; G7 ALL -> ALL. Every other item that reads FACTS: unchanged (the diff of all 239 rows is empty).

## Checks run

- `run.py` full regeneration (detached through wait-bg.sh, exit 0): "236 / 239 (1562.9 s)"; mutants m1 to m6 `exact: true`; M6 audit untraced [], choice_mismatches []; M5 violations [], regulated_predicates 60; N3 holds False (no dead commitment).
- Probe after batch 2: mutant m1 still makes C1 a conflict under RS5 = exception (both RS3 choices) and the witness builder finds a witness for f11-exception, f11-exception-deploy, f3-inuse, f3-inuse-forecast.
- `usecases/safetyfw_accounting.py openai-preparedness --source <pinned copy> --check`: passes; "99 blocks, 565 unaccounted words in 79 blocks, 18 blocks with a loss {'1': 22, '3': 1, 'limit 21': 1}, 0 of 115 quotes unanchored" (f16-year's and the two f3-develop-inuse lines' losses are gone).
- `uv run pytest tests/test_pf_fidelity_fix.py`: 33 passed; `tests/test_safetyfw_accounting.py tests/test_usecase_key_transcription.py`: 86 passed.
- Final selected run, committed HEAD 45512ef7f (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base 9be13b93d --run`, GitHub Actions run openai-preparedness-fidelity-fix-2-45512ef7-t519921, log /tmp/pfx/select.log): shard 1 "12 units, 12 passed", shard 3 "12 units, 12 passed", shard 2 "15 units, 14 passed": one failure, tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon (not on main-known-red). Cause: conformance/english-lean/lexicon-report.json records the PF environment.d1.json's lexicon id and symbol count (136 -> 138 with the new relation, act and sort). Fixed by its generator, `uv run python -m conformance.english_lean_lexicon` ("valid": 43, "invalid": 0; only the PF row changed), commit f39215f05; the failed id rerun alone (`mac-pytest.sh -- <id>`): "1 passed". The gate on the final HEAD is the chain's.
- Generated files, each by its own script on the pinned source copy (debates/seat-calib-openai-preparedness-20261112T1640ZB/pf-v2.txt, sha256 d2e3dd5b...48d0f = build_document.TEXT_SHA256): environment.d1.json (pf_vocabulary.py), spans.json (build_document.py: unchanged), coverage.json, stage0.json (stage0.py), gaps (measure.py: unchanged), quote-hashes.json (source/quote_evidence.py), accounting.json (`--report`), results.json (run.py), and conformance/english-lean/lexicon-report.json (`python -m conformance.english_lean_lexicon`). `tools/regen_generated.py --list` registers none of them.

## Seeded bugs (Python; no Lean or Rust product code changed)

Each planted, the one test run, the files restored with `git checkout` (tree clean after each). Also in mutants.json.

| Bug | File | Test that fails |
|---|---|---|
| (a) f3-inuse's act back to "during development" | usecases/openai-preparedness/rules.d1.ve | test_f3_internal_use_is_its_own_act_and_both_legends_say_additional |
| (b) f11-exception's old guard, no area | usecases/openai-preparedness/rules.d1.ve | test_one_areas_adjustment_does_not_release_another_areas_duty |
| (c) "Every situation may be deployed" with no area bound | usecases/openai-preparedness/rules.d1.ve | test_the_deploy_exception_permits_only_inside_the_confirmed_area |
| (d) "derives from a model determined below High" back in f6-rel's legend | usecases/openai-preparedness/pf_vocabulary.py | test_f6_guard_names_footnote_6s_three_methods |
| (e) f14-summary's employee_request guard restored | usecases/openai-preparedness/rules.d1.ve | test_f14_summary_covers_the_sag_recommendation_with_no_request_guard |
| (f) "as well as propensity" back in f12-undermining's act | usecases/openai-preparedness/pf_vocabulary.py | test_f12_undermining_keeps_and_or |
| (g) "unless conservative_upper_bound_used" and run.py's ALTERNATIVES restored | rules.d1.ve, run.py, pf_vocabulary.py | test_f12_sandbagging_is_one_disjunctive_duty |
| (h) "for continued sufficiency" dropped from f16-year's legend | usecases/openai-preparedness/pf_vocabulary.py | test_f16_year_reviews_the_framework_once_as_to_continued_sufficiency |
| (i) cl-levels back inside facts.d1.ve | facts.d1.ve, rules.d1.ve | test_facts_hold_exactly_their_stated_inventory |
| (j) review F1: premise_units ignores the goal (`names = set()`) | usecases/openai-preparedness/run.py | test_premise_units_follow_the_goal |
| (k) review F1: G7's rows lose `"rules": ["fn5-indicator"]` | usecases/openai-preparedness/results.json | test_facts_hold_exactly_their_stated_inventory, test_every_premise_unit_outside_facts_is_named_by_an_item |

## Review fix (openai-preparedness-fidelity-fix-2-review.final.md)

- F1 (B): moving `fn5-indicator` out of FACTS left G7 with no tie to its unit (uc-audit ties an item to the units its results.json record names, plus FACTS). Class: a route that rests on a premise unit outside FACTS but does not name it. Structural fix: `pf_translation.rule_fact_blocks()` is the one list of those units; `run.premise_units(goal)` names every one whose premises mention a predicate of the route's goal, and both premise routes use it (G7 `indicator_silence` -> `["fn5-indicator"]`, N4 `low_medium_never` -> `["cl-levels"]`, unchanged). results.json regenerated by run.py: "236 / 239", the only change is G7's two rows gaining `"rules": ["fn5-indicator"]` (no `comparison` row changed). Tests: `test_facts_hold_exactly_their_stated_inventory` (G7 names fn5-indicator), `test_every_premise_unit_outside_facts_is_named_by_an_item` (every rules.d1.ve fact unit is named by some item: the class), `test_premise_units_follow_the_goal`. Probe F1 failed before and passes after. Seeded bugs (j), (k). Checks on 56fbdc425: `mac-pytest.sh --select -- --base 9be13b93d --run` (GitHub Actions run openai-preparedness-fidelity-fix-2-56fbdc42-t529419): shards 15/15, 15/15, 9/9 passed, exit 0; `lake build` "Build completed successfully (1429 jobs)"; `python3 lean/audit.py` PASS; `tools/regen_generated.py --check` exit 0.

## Open list

- **Question 3 (sent once, 2026-11-12 20:32Z, inbox/dri/20261112T203257Z-openai-preparedness-fidelity-fix-2-3686951.md). RULED (b), reviews/dri-decisions-20261112-openai-preparedness-fidelity-fix-2-q3.md item 1: moved to openai-preparedness-fidelity-fix-3 (addendum 9 item 61 fixes the shared legend once there, with f4-security; item 2 pre-answers fix-3's question).** sess-3 C7 on f3-develop-inuse(-forecast): the situation sort's legend "a development, use, deployment, review or decision of a covered model" (pf_vocabulary.py `environment()`) restores a coverage scope the 4.4 sentence does not state. It is read by every rule (round-B f4-security fails on the same point, pf-adjud Q08). Recommendation sent: (a) drop "covered" from the legend in this item (every rule whose source states coverage tests "that situation is covered" explicitly; no answer moves), with every unit then treated as changed for the re-read; or (b) leave it to openai-preparedness-fidelity-fix-3 with f4-security. Not changed here: pf_vocabulary.py's situation sort is not in this diff, and the frozen-key tests stay selected and unchanged, as the ruling's condition says.
- Questions 1, 2, 4, 5 did not arise: C1 stays NONE and no A-*/SUF or G answer moved (1); K10 stays SOME(N) with no bound-is-false assumption (2); f16-year's once-for-the-Framework duty needed a vocabulary sort, not a language feature (4); the FACTS move needed no scorer or audit change, since uc-audit.py derives units from rules.d1.ve's `## <id> |` headers and N4 stays ALL (5).
- Out of scope, with their rulings: C6 and C-doc (VE NONE, key SOME(final ∧ bperm); PLAN 12 items 18-19, key findings) and G9 (VE SOME(P ∨ scoped), key ALL; PLAN 12 item 20); keys and scorer untouched. The 28 round-B units: openai-preparedness-fidelity-fix-3 (gated on the sample adjudication, reviews/audit-newrule-fsfpf/pf-adjud/).
- Amendments: none cleared a unit before it was reached (the 20:07-20:09Z relay left both sandbagging units split; both fixed in batch 4).

## Budget readings

No `openai-preparedness-fidelity-fix-2-loop.log` is readable on this host (ve-cloud-3; manage-agents holds only the placement files). The one reading available is the task's AMENDMENT: VM1 20:12Z, joint allowance left 4.62M of 14M, round budget 1.00M: START. I ran no ucfix-budget check (the launcher owns it).

## Size

SIZE: 134 product (use-case translation, vocabulary and harness: rules.d1.ve 27, pf_vocabulary.py 41, run.py 37, pf_translation.py 15, build_document.py 4, accounting.d1.txt 7, stage0.py 2, quote_evidence.py 1; facts.d1.ve -4), 178 tests, 25 PLAN plus this report and mutants.json other hand-written lines (`git diff --numstat $(git merge-base HEAD main)`). Generated: results.json, environment.d1.json, coverage.json, accounting.json, stage0.json, quote-hashes.json.

## Notes for the DRI

- The task file's line numbers are 175814252d's; main 9be13b93d had the same use-case files.
- Trust and trust mutants: no Lean, no trusted code; light-lane says NOT (3061 lines, results.json counted), but no sweep applies (build checklist 13a is for trusted Lean growth). No trust-map change.
- f14-summary's act sits at the 80-character limit; the full object is in the legend, as the task allows.
- `employee_request` stays in the vocabulary and in K16's case model (the case states a request) though no rule tests it any more.
- f11's "every area the situation has reached is either sufficiently safeguarded or the confirmed-adjustment area": `sufficient_safeguards` is one atom per situation, so where it holds F2's prohibition never fires and the permission is not needed; the area bound alone gives the stated scope.
- build_document.py and run.py each list the model domains (pre-existing duplication); both gained `framework`.

## Next item

After merge, the production checklist pass re-reads ONLY the changed units (addendum 8 item 56; addendum 6 item 41): f3-develop-inuse, f3-develop-inuse-forecast, f3-inuse, f3-inuse-forecast, f11-exception, f11-exception-deploy, f6-rel, f14-summary, f12-undermining, f12-undermining-unscoped, f12-sandbagging, f12-sandbagging-unscoped, f16-year, FACTS, cl-levels, fn5-indicator. Then the full union audit at the Nov 23 checkpoint; both launched by the DRI decider. Then round B (openai-preparedness-fidelity-fix-3) if its gate passes, which makes the shared "covered model" change ruled in question 3.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay or schema change).
2. Every deliverable built: PASS, the 12 numbered fixes are in the table above, each with its commit (batches 1-5: a70b37ccb, c48e5efba, b4014de9f, 774f29e81, 414703ff1) and test; C7 of items 1-2 moved to fix-3 by reviews/dri-decisions-20261112-openai-preparedness-fidelity-fix-2-q3.md item 1.
3. Tests can fail: PASS, 11 seeded bugs, each with its failing test (table above; mutants.json).
4. Python, Lean, Rust agree: N.A. (no product language path changed; the use case's answers are unchanged, 236/239).
5. R8 binding: N.A. (no relayed answer read).
6. Gate evidence on final HEAD: the chain runs the gate; final selected run on committed HEAD below.
7. No unsigned item: PASS, no DELTA row, no trust growth.
8. Every user-visible change in DELTA: N.A. (no product behaviour change; use-case answers identical).
9. Test selection: PASS (the final selected run found the lexicon report, fixed in f39215f05), `tools/select_tests.py --base $(git merge-base HEAD main)` selects tests/test_pf_fidelity_fix.py, tests/test_safetyfw_usecases.py, tests/test_safetyfw_accounting.py, tests/test_usecase_key_transcription.py.
10. Lean statements: N.A.
11. Budgets fail closed: N.A. (no new evaluator; K10's "unset negation is UNDECIDED" path is unchanged, test_pf_an_unset_negated_open_term_is_undecided).
12. No CPU regression: N.A. (no product code; run.py 1563 s full run).
13. Test-removed trailers: N.A. (no test removed or renamed; one cycle-1 assertion widened: test_f2_f3_acts_carry_the_sufficiency's SUF set gains the internal-use act; test_change_log_removal_of_low_and_medium_is_a_blocked_unit and test_rs11_final_is_excluded_and_no_rule_of_it_returns read fact_blocks()).
14. Both directions: PASS, each selection test asserts the accepted and the refused side (one area selects / two areas do not; inuse selects / devonly does not; K10 holds exactly under RS4 = N).
15. No overclaim: PASS, "no answer changed" cites the empty diff of all 239 rows; "236/239" cites run.py's output.
