# safety-framework-fidelity-fix-2: REPORT

**Status:** batches 1-6 delivered (all 19 confirmed units). Final selected run: 60 units, 0 failed (Tests). No VE answer moved (run.py: 260/262, the same two section-12 disagreements, C3 and C-doc).
**HEAD:** see `git log`; commits below. **Changed:** use-case files only (rules, vocabulary, facts, cases, D2 cell, span map), plus their regenerated outputs and tests. No ve/, lean/ or rust/ change. No key edit.
**PROJECTED union count** (nothing claimed before the re-read): 165 -> 223 (batch 1) -> 235 -> 243 -> 251 -> 252 -> 253 (batch 6).
**Open:** no DRI question sent (no answer left its key). No DRI signature needed, no DELTA rows.
**Next item:** the production checklist pass re-reads the changed units, then the full union audit at the Nov 23 checkpoint (needs row uc-audit-packet-fsf-history merged). Both are launched by the DRI decider.

SIZE: 160 product (use-case translation and harness: rules.d1.ve 52, vocabulary.py 47, severity_and_dates.py 20, build_document.py 11, reference.py 9, cases.json 8, measure_r1/r2 5, run.py 4, facts.d1.ve 4), 173 tests, 27 + this REPORT + mutants.json other hand-written lines (added + deleted, `git diff --numstat $(git merge-base HEAD main)`). No cut.

Ruling: orchestrator FSF ruling 2026-11-12 21:24Z (option A; planning 223, upper bound 252). Binding as well: audit-stability addendum 9 items 58-63 and the post-sprint plan section 1. Base: main 6949e5de43, which contains fsf-fidelity-fix (9be13b93de). No AMENDMENT line was in the task file, so no unit was dropped.

## Commits (main..HEAD --no-merges)

| commit | what |
|---|---|
| 5cd2d48a83 | batches 1-2: the OT3 finding carries the safety case (f3, f12-*, f13-*); f16 has no OT4/OT5 exception |
| 6ceaa4a091 | batch 3: f6 keeps the experts |
| 6a54c698b7 | batch 4: f7-rra keeps "as part of evaluating their deployment mitigations" |
| 8166b733d1 | batch 5: f14's possibility clause is a hedged, LABELLED unit |
| 479d5850ac | batch 6: the f20 pairs, FACTS, CASES (G8), D2D3 |
| 2c810b2152 | spans.json, coverage.json, readings/results.json regenerated |
| 0cadd1f6c7 | FSF norm blocks recaptured; lexicon report regenerated |
| 5c69400c79 | R-stale route fixture; measure_r1/r2; f16-ds quote test |
| 1a4814a62e | PLAN section 12 entry 25 |

## One line per unit

Sources of the findings: per-unit pass `debates/seat-calib-safety-framework-20261112T1957ZB/sess-N/astra.md`, called "(b)" below; whole-document pass `debates/seat-calib-safety-framework-20261112T2016ZA` (+ -r2rerun), called "(a)"; and the adjudication files under `reviews/audit-newrule-fsfpf/`. R = rules.d1.ve, V = vocabulary.py, both on this branch.

- **f3** - (b) sess-1 C1/C11: "The header ends its quotation at 'acceptable' ..., omitting the source's 'including with a safety case where a CCL has been reached'". (a) Astra: "Requiring a safety case separately through f7-sc does not establish that one accompanied this determination". - Footnote 4: "... if the appropriate governance function determines the residual risk of such deployments to be acceptable even if the model has reached a T/CCL (including with a safety case where a CCL has been reached)". The header now quotes the whole sentence. The guard's finding is the one OT3 finding `governance_found_acceptable_with_safety_case_where_ccl_reached`. Its legend reads "including a safety case where the model of {0} has reached a CCL ... a determination without that safety case at a CCL is not this finding".
- **f12-p, f12-u** - (b) sess-3 C1: "VE rules.d1.ve:50 lifts the prohibition 'unless that proposal is classified as "governance_found_acceptable"' ... The safety case appears merely among OT3's factors". (a) Astra: "They therefore lift it even for a CCL determination lacking the required safety case". - 2.1.2 step 2: "external deployments of a model take place only after the appropriate governance function determines the residual risk to be acceptable (including a safety case where a CCL has been reached)". The headers quote this sentence; the guards name the same OT3 finding. In build_document.py the OT3 declaration ("... including a safety case where a CCL has been reached ...: the safety case is part of the finding") no longer lists the safety case as a factor.
- **f13-p, f13-u** - (b) sess-3 C1: the same finding for src:14 (rules.d1.ve:54, :56). - 3.1.2 step 2: "external deployments and high-risk internal deployments of a model take place only after the appropriate governance function determines the residual risk to be acceptable (including a safety case where a CCL has been reached)". Same fix.
- **f16-ds, f16-ds-strict** - (a) Astra (2016ZA:326, round 3 :1068): "source line 7 makes these alternatives conditions for an acceptable-risk classification ... Acceptable-risk classification does not automatically cancel that separate recommendation. Importing its alternatives as sufficient exceptions conflates the regimes". - The OT4/OT5 exception is removed from both rules. The headers quote 2.2 whole, "... may be adjusted if our understanding of the risks changes. This may occur if, for example, ... or if we assess that the benefits of the open release of model weights outweigh the risks", as possible reasons. They quote 1.3.5's "or we otherwise assess ... or we assess that the benefits ... outweigh the risks" as alternatives of the classification (f9-acc, f10-acc, f11-acc). This is a new form of round 1's "a possible adjustment is not sufficient": round 1 dropped OT16 and kept OT4/OT5 (PLAN 12 item 24). Entry 25 records the change.
- **f6** - (b) sess-1 C1/C11: "The full sentence requires 'involving internal and external experts as needed' ... VE's act is only 'an assessment of proximity to each level with a risk analysis'". (a) Astra: "Conditional involvement disappears". - 1.3.3: "we will assess the proximity of the model to the CCL and analyze the risk posed, involving internal and external experts as needed". The header quotes the whole sentence. The `proximity_assessed` legend carries the involvement. An act phrase may not hold "and" (`actReserved`, lean/VE/Acts/LexicalBase.lean:7), which is the task's "or the legend quotes the full sentence" branch.
- **f7-rra** - relay 4 Q05, (ii) by both: "'as part of evaluating their deployment mitigations' (src:7) is plain, dropped at rules.d1.ve:20 and vocabulary.py:162-163 with no reading set or reason". - 1.3.4: "Models reaching TCLs or CCLs will be subject to residual risk assessments as part of evaluating their deployment mitigations". The act is now "be subject to residual risk assessments in evaluating deployment mitigations" (80 characters, the act limit). The legend says "as part of evaluating its deployment mitigations", and the header quotes the sentence.
- **f14** - relay 4 Q01, (iv) by both: "the 'might result in updates' clause is neither labelled nor a might cell while the span map marks the sentence CHECKED". - 2.1.2 and 3.1.2 step 3: "... for review and might result in updates to the related residual risk assessment or safety case". The clause is its own hedged unit in both sections (`s212-might-update` and `s312-might-update`, kind hedged/could, LABELLED), handled as PLAN 3.3 handles possibilities. f14's CHECKED unit now ends at "for review". The header quotes the whole sentence and says the review duty is the only duty.
- **f20-holistic-strict, f20-holistic-default** - adjudication Q02/Q03, REAL by both: "the legend (vocabulary.py:215-216) gives proportionality to 'the mitigation' only" / "the header (rules.d1.ve:77) says 'the second on the mitigation itself'". - 1.3.5 Note: "The mitigation and the effects of such mitigation should also be assessed holistically and be proportionate with expected impact of a model's risk". The legend now reads "the mitigation and its effects are both proportionate ...". The strict header says "two demands, both on one subject, the mitigation and its effects". The act is unchanged ("holistically assessed mitigations proportionate with expected impact"): no 80-character act without "and" holds both nouns.
- **f20-within-strict, f20-within-default** - (b) sess-4 C1: "'as determined by the T/CCLs as relevant' ... Neither the operative rule nor its meaning preserves how the acceptable levels are determined". - Glossary: "The residual risk should be brought within the acceptable levels, as determined by the T/CCLs as relevant". The legend and both headers now carry the qualification. This is not a recurrence: round 1's finding was an added reached-level guard, and that guard stays removed.
- **f20-elicitation-strict, f20-elicitation-default** - (b) sess-4 C1/C6/C11 and (a) Astra classes 1, 6, 11: "Consideration alone does not preserve conservative evaluations". - Note on ML R&D CCLs: "... than we put into assessing risk, thus requiring conservatism in the form of evaluations". The act is "have its risk assessment conservatively weigh greater elicitation by others" (79 characters). The legend reads "... than the developer puts into assessing risk, and its evaluations are conservative accordingly", and the header quotes the whole sentence. This unit was not in round 1.
- **FACTS** - (a) Opus (2016ZA:326-331): "facts.d1.ve:13-14 ... It is the whole meaning of the CHECKED unit s211-sl2plus ... The baseline and the external-actor conjunct are dropped. The constant `insider_threat_measures` splits off a measure group that the source does not split". (a) Astra holds the same. - 2.1.1: "which uses RAND Security Level 2 (SL2) as a baseline, with additional security measures designed to address risks from insider threats and well-resourced non-state external actors". New facts: SL2+ includes `rand_security_level_2`; SL2+ includes `sl2_plus_additional_measures`; that group addresses `insiders` and `well_resourced_non_state_external_actors` (new constants in V). This is not a recurrence: round 1's FACTS finding was the bridge-one-domain exclusions, which stay N1's own.
- **CASES** - (b) sess-3 C8 and (a) Astra class 8: "G8 specifies only 'post-deployment evidence that the safeguards are circumvented' ... Nevertheless, cases.json:934-944 assigns `"levels": ["cbrn_uplift_level_1"]` and `"activity": "EXT"`". - PLAN 5: "exactly the levels named ... and no others", and "Every other open term is unset unless the case says so". G8 now has no level and no activity; its only finding is `circumvention_evidence`. This is a partial recurrence: round 1 removed G8's OT3, and this round removes its remaining stipulations. G8 stays ALL (`test_g8_stipulates_only_the_circumvention_evidence`).
- **D2D3** - relay 2 (fsf-relay2/result.md): still split. Astra: "the stated cell drops the 'adequate computational resources' qualification and does not keep 'unrestricted access' explicitly". The repair both seats accept is "state the cell with src:15's conditions". - 3.2.2: "Unrestricted access to models at this level of capability could give an actor (or AI systems) with adequate computational resources the ability to reach capabilities much more powerful ... This could be catastrophic if there is no effective way of defending against rapidly improving and potentially superhuman AI systems wielded by threat actors". The catastrophic cell is now stated, still as `might`, of its own alternative `unrestricted_access_ml_rd_automation_level_1`. Its label is "giving an actor (or AI systems) with adequate computational resources unrestricted access to a model that has reached ml_rd_automation_level_1, when there is no effective way of defending against rapidly improving and potentially superhuman AI systems wielded by threat actors". The harm's description quotes both sentences. No condition was missing from the language: the conditions are part of the alternative, so STOP question 2 did not arise. S and D answers are unchanged.

Shared names renamed (the task's "a block not named above is changed only where a named fix renames a shared predicate or legend"):
- `governance_found_acceptable` -> `governance_found_acceptable_with_safety_case_where_ccl_reached`. The 64-byte identifier limit ruled out "including". Only the five named blocks use it in rules. It is also named in cases.json (the LRX activity list, a rename only), run.py (`GOVERNANCE_FINDING`, which GOV items are asked without) and reference.py (`GOV_FINDING`, its own copy, since it stays independent).
- The acts of `residual_assessed` (f7-rra only) and `elicitation_considered` (the two f20-elicitation blocks only) changed. No other block changed.

## Per checklist class (prompts/translation-fidelity-checklist.md)

| class | units changed | fix |
|---|---|---|
| 1 dropped conjunct or clause | f3, f12-p, f12-u, f13-p, f13-u, f6, f7-rra, f14, f20-holistic x2, f20-within x2, f20-elicitation x2, FACTS, D2D3 | each clause restored in a guard's finding, act or legend; f14's as a labelled unit |
| 2 quantifier scope | - | - |
| 3 exclusive "only" | - | - |
| 4 one predicate across regimes | f16-ds, f16-ds-strict; FACTS (one measure group, not an insider-only split) | 1.3.5's classification alternatives no longer except 2.2's recommendation |
| 5 modal strength | f16-ds, f16-ds-strict (2.2's "may occur if" open-release case); f14 ("might") | reasons and possibilities, never sufficient conditions or duties |
| 6 obligation turned into method | f20-elicitation x2 (consider -> conservatively weigh); f20-holistic x2 (proportionality of the effects) | the outcome demand restored |
| 7 invented guards and exclusions | f16-ds, f16-ds-strict (OT4/OT5 exception removed); D2D3 (the cell's conditions stated) | |
| 8 case facts fixing open terms | CASES (G8) | level and activity removed |
| 9 readings that manufacture conflicts | - | - |
| 10 key cells | f3's C10 claim checked: no answer moved (table below) | - |
| 11 elided quotes | every changed block's header quotes the whole source sentence | - |

## PROJECTED union count after each batch (labelled PROJECTED; no claim before the re-read)

Computed with tools-local/uc-audit.py `compute` on reviews/audit-newrule-fsfpf/fsf-rescore/union, f5 cleared. This is the forecast's method (fsf_numbers.py), with the units of each batch set fixed in turn. An answer counts when VE = key, the item's own verdict is FAITHFUL, and every unit it rests on is fixed or cleared. VE's own answer moved in no batch (run.py after each batch: 260/262; `/tmp` comparison against main's results.json: "changed []"). So every "old -> new" below is "not counted -> counted (PROJECTED)", caused by the batch's unit fixes.

| batch | units | PROJECTED count | answers regained (old not counted -> new counted) |
|---|---|---|---|
| baseline | - | 165 | - |
| 1 | f3, f12-p, f12-u, f13-p, f13-u | **223** (+58) | A-L0..L7 DEV/INT/HRI/EXT GOV (32), A-L0..L7 LRX GOV (8), A-L0..L7 EXT/CCA (8), A-L0/L1/L5-LRX/CCA (3), C2, C5, G2, G6, G9, R9b/PERMITS, R9c/FORBIDS |
| 2 | f16-ds, f16-ds-strict | 235 (+12) | B-L0..L7/RECSEC (8), C1, C4, G4, G5 |
| 3 | f6 | 243 (+8) | G3, K1-L2/L3/L4/L6/L7/PROXIMITY, K2-L1/L5/PROXIMITY |
| 4 | f7-rra | 251 (+8) | B-L0..L7/RRA |
| 5 | f14 | 252 (+1) | K5/SUBMISSION |
| 6 | CASES, D2D3, FACTS, f20 x6 | 253 (+1) | N3 |

Still not counted (9, out of reach of unit fixes): A-L2/L3/L4/L6/L7-LRX/CCA (item verdict), G8 (item verdict), N1 (withdrawn single-seat finding), C3 and C-doc (VE != key, PLAN 12 item 23).

## Batch 1: CCL/LRX answers before and after (FORECAST RISK 1)

The checklist reader's C10 claim on f3 was checked by recording every LRX item and every item resting on f3, f12-* or f13-* (82 items) before and after batch 1. Before: main 6949e5de results.json. After: this branch's run.py. **No answer changed.** The reason: PLAN 5's LRX stipulation, "the governance function has determined this deployment's residual risk acceptable", is the OT3 finding, and OT3 is the determination "including a safety case where a CCL has been reached" (PLAN 3.2 OT3 row; Astra, 2016ZA round 3: "their stipulated determination is the complete source-defined OT3 finding"). Without that finding, F3 releases nothing and A-L2-LRX/CCA is ALL (`test_the_governance_determination_includes_the_safety_case_where_a_ccl_has_been_reached`, both directions). No case was changed to keep a key answer. The LRX activity entry was renamed, not changed. STOP question 1 did not arise.

| items | key | VE before (main 6949e5de) | VE after (this branch) | batch-1 units used |
|---|---|---|---|---|
| A-L0-DEV/GOV, A-L0-INT/GOV, A-L1-DEV/GOV, A-L1-INT/GOV, A-L2-DEV/GOV, A-L2-INT/GOV, A-L3-DEV/GOV, A-L3-INT/GOV, A-L4-DEV/GOV, A-L4-INT/GOV, A-L5-DEV/GOV, A-L5-INT/GOV, A-L6-DEV/GOV, A-L6-INT/GOV, A-L7-DEV/GOV, A-L7-INT/GOV, R9b/PERMITS, C5 | NONE | NONE | NONE | f12-p,f12-u,f13-p,f13-u |
| A-L0-HRI/GOV, A-L1-HRI/GOV, A-L2-HRI/GOV, A-L3-HRI/GOV, A-L4-HRI/GOV | SOME(U) | SOME(RS2=U) | SOME(RS2=U) | f12-p,f13-p,f13-u |
| A-L0-LRX/DM, A-L0-LRX/SEC | NONE | NONE | NONE | - |
| A-L0-LRX/GOV, A-L0-EXT/GOV | SOME(U) | SOME(RS2=U) | SOME(RS2=U) | f12-p,f12-u,f13-p,f13-u |
| A-L0-LRX/CCA, A-L1-LRX/CCA, A-L2-LRX/CCA, A-L3-LRX/CCA, A-L4-LRX/CCA, A-L5-LRX/CCA, A-L6-LRX/CCA, A-L7-LRX/CCA | SOME(M) | SOME(RS7=M) | SOME(RS7=M) | f3 |
| A-L0-EXT/CCA, A-L1-EXT/CCA, A-L2-EXT/CCA, A-L3-EXT/CCA, A-L4-EXT/CCA, A-L5-EXT/CCA, A-L6-EXT/CCA, A-L7-EXT/CCA | ALL | ALL | ALL | f3 |
| A-L1-LRX/DM, A-L1-LRX/SEC, A-L2-LRX/DM, A-L2-LRX/SEC, A-L3-LRX/DM, A-L3-LRX/SEC, A-L4-LRX/DM, A-L4-LRX/SEC, A-L5-LRX/DM, A-L5-LRX/SEC, A-L6-LRX/DM, A-L6-LRX/SEC, A-L7-LRX/DM, A-L7-LRX/SEC | SOME(G) | SOME(RS1=G) | SOME(RS1=G) | - |
| A-L1-LRX/GOV, A-L1-EXT/GOV, A-L2-LRX/GOV, A-L2-EXT/GOV, A-L3-LRX/GOV, A-L3-EXT/GOV, A-L4-LRX/GOV, A-L4-EXT/GOV, A-L5-LRX/GOV, A-L5-EXT/GOV, A-L6-LRX/GOV, A-L6-EXT/GOV, A-L7-LRX/GOV, A-L7-EXT/GOV, G2 | ALL | ALL | ALL | f12-p,f12-u,f13-p,f13-u |
| A-L5-HRI/GOV, A-L6-HRI/GOV, A-L7-HRI/GOV | ALL | ALL | ALL | f13-p,f13-u |
| R9c/FORBIDS | ALL | ALL | ALL | f12-p,f12-u,f13-u |
| C2 | NONE | NONE | NONE | f3 |
| C-doc | SOME(G & rel & RS9=same) | NONE | NONE | f12-p,f12-u,f13-p,f13-u,f3 |
| G6 | {"GOV": "SOME(U)", "SILENT:CCA": "ALL"} | {"GOV": "SOME(RS2=U)", "SILENT:CCA": "ALL"} | {"GOV": "SOME(RS2=U)", "SILENT:CCA": "ALL"} | f12-p,f12-u,f13-p,f13-u,f3 |
| G8 | ALL | ALL | ALL | f12-p,f12-u,f13-p,f13-u,f3 |
| G9 | {"FORBIDS": "ALL", "FORBIDS@G9-L0": "SOME(U)"} | {"FORBIDS": "ALL", "FORBIDS@G9-L0": "SOME(RS2=U)"} | {"FORBIDS": "ALL", "FORBIDS@G9-L0": "SOME(RS2=U)"} | f12-p,f12-u,f13-p,f13-u |
| N3 | NONE | NONE | NONE | f12-p,f12-u,f13-p,f13-u,f3 |

## Open list

- **Questions sent to the DRI decider:** none. No fix moved an answer off its key: run.py after every batch gave 260/262, with only C3 and C-doc disagreeing, as on main. No fix needed a ve/, lean/ or rust/ change, a key edit, or a reading the task does not name. So STOP questions 1-3 did not arise.
- **Out of scope, as the task rules:** N1 (rests only on a withdrawn single-seat finding; no fix applies). f5 (cleared, (iii) by both, relay 4 Q04). C3 and C-doc (VE != key; recorded key errors, PLAN 12 item 23). G8 and A-L2/L3/L4/L6/L7-LRX/CCA (blocked by their own item verdict). Neither block named above was changed.

## PLAN section 12

One new entry, **25** ("Source clauses kept whole"), lists every change above and records one deviation from earlier plan text. 4.2 F16 and item 24 kept OT4/OT5 as F16's excepted cases; entry 25 removes them, with the source reason. Sections 1-11 and section 6 are untouched: `test_answer_key_is_the_transcription` passes, so the key SHA-256 8fbb0475... and PLAN section 6 are unchanged.

## Tests

New tests in tests/test_safety_framework.py, one per behaviour:
- `test_the_governance_determination_includes_the_safety_case_where_a_ccl_has_been_reached` (batch 1, both directions)
- `test_the_proximity_assessment_involves_internal_and_external_experts_as_needed` (batch 3)
- `test_the_residual_risk_assessment_is_part_of_evaluating_the_deployment_mitigations` (batch 4)
- `test_the_possibility_of_updates_after_a_safety_case_review_is_labelled_not_checked` (batch 5)
- `test_the_f20_legends_keep_the_source_s_subject_qualification_and_conservatism`, `test_security_level_2_plus_is_its_baseline_and_one_group_of_measures_against_both_threats`, `test_g8_stipulates_only_the_circumvention_evidence`, `test_the_catastrophic_cell_states_the_l7_rationale_s_conditions` (batch 6)

Existing tests changed, each only where it pinned the old text (no test removed, so no Test-removed trailer):
- `test_a_possible_adjustment_is_no_exception_to_the_recommended_level` asserted RECSEC = NONE with OT4 (the exception batch 2 removes). It now asserts SOME(RS3=Ds) with OT4, with OT5 and with both, and that neither f16 block has an exception.
- `test_a_unit_whose_rule_or_premise_uses_an_open_predicate_is_open_with_its_term` pinned CHECKED bytes 4,043/2,935; they are now 3,959/2,851 (f14's possibility clause is LABELLED).
- tests/test_safetyfw_accounting.py `test_a_short_quote_does_not_make_the_text_between_two_quotes_a_quote` pinned f16-ds's cut 2.2 quote. It now reads the whole sentence.

Regenerated files, each only by its own script: results.json (run.py), environment.d1.json (vocabulary.py), spans.json and coverage.json (build_document.py on a scratch copy of the pinned source, sha256 18e3375b...), readings/results.json (readings_r1.py). Also tests/data/norm-blocks/fsf.jsonl (capture_blocks.capture, FSF only, pinned at 2c810b2152; 44 blocks, 0 refused), conformance/english-lean/lexicon-report.json (`python -m conformance.english_lean_lexicon`: 43 valid, 0 invalid; safety-framework row 83 -> 85 symbols) and the R-stale line of tests/data/route-cases.jsonl (written by docs/en-e3-norm/en-2b/route_fixtures.py, kept at its position). `regen_generated.py --write` was run once; it changed only docs/codemap files, through main's own lag (new lean/VE/Kernel and Route modules), and those were not committed. `--only route-cases --write` after the fixture: no change.

usecases/safety-framework/measure_r1.py and measure_r2.py read saved Oct 1 and Oct 18 statuses by unit id. The two new hedged units have none, so both now give such a unit no earlier status (None, counted as changed). Without this, `test_every_unit_and_item_is_measured_once` raised KeyError.

Runs while iterating:
- the named -k selections after each batch (all passed);
- `uv run pytest tests/test_safety_framework.py tests/test_safetyfw_accounting.py tests/test_english_statement_blocks.py tests/test_english_lean_lexicon.py`: **155 passed** in 752.79 s, on 5c69400c79's tree;
- `uv run python usecases/safety-framework/run.py` after batches 1, 2, 3, 4 and 6, and `run.py --check` after batch 5: each "agreement with the answer key: 260/262", DISAGREE C3 and C-doc only;
- `build_document.py --check` after seed S-e was restored: exit 0.

**Selected run** (final, on the committed clean tree e1c1b6b9fe, tree 3f59e7998e): `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base 6949e5de43 --run`. Output: "recorded 60 units for tree 3f59e7998e; ... 0 failed" and "summary: ran LOCALLY (VM) ...; exit=0; 3961s". It covers tests/test_safety_framework.py, test_safetyfw_accounting.py, test_safetyfw_usecases.py, test_english_statement_blocks.py, test_english_lean_lexicon.py and test_keyed_answers_authority.py. No test of main-known-red.txt was hit. Only this REPORT changed after it.

## Seeded bugs (docs/usecases/safety-framework/safety-framework-fidelity-fix-2/mutants.json)

Each bug was planted, its named test ran and FAILED, and the file was restored from a copy. Only Python and VE translation files of the use case changed; no ve/, lean/ or rust/ product code.

| id | file | change | failing test |
|---|---|---|---|
| S-a (task a) | usecases/safety-framework/rules.d1.ve | f13-u header: the safety-case clause cut | test_the_governance_determination_includes_the_safety_case_where_a_ccl_has_been_reached |
| S-b (task b) | usecases/safety-framework/vocabulary.py | residual_assessed legend: "as part of evaluating its deployment mitigations" cut | test_the_residual_risk_assessment_is_part_of_evaluating_the_deployment_mitigations |
| S-c (task c) | usecases/safety-framework/vocabulary.py | proximity_assessed legend: "internal and external" -> "internal external" | test_the_proximity_assessment_involves_internal_and_external_experts_as_needed |
| S-d (task d) | usecases/safety-framework/vocabulary.py | holistic legend: proportionality to "the mitigation" only | test_the_f20_legends_keep_the_source_s_subject_qualification_and_conservatism |
| S-e (task e) | usecases/safety-framework/build_document.py | s212-might-update deleted, spans regenerated (the sentence CHECKED whole) | test_the_possibility_of_updates_after_a_safety_case_review_is_labelled_not_checked (KeyError) |
| S-f (task f) | usecases/safety-framework/severity_and_dates.py | label: "with adequate computational resources" cut | test_the_catastrophic_cell_states_the_l7_rationale_s_conditions |
| S-g | usecases/safety-framework/rules.d1.ve | f16-ds-strict: the OT4/OT5 "unless" restored | test_a_possible_adjustment_is_no_exception_to_the_recommended_level (SOME(RS3=Ds & RS3force=default) != SOME(RS3=Ds)) |
| S-h | usecases/safety-framework/facts.d1.ve | measures-sl2plus: the external-actors fact cut | test_security_level_2_plus_is_its_baseline_and_one_group_of_measures_against_both_threats |

Two first versions of new tests were not strict enough, and both were tightened before the seed was recorded. The first S-c run passed because the legend's own source quotation still held the clause; the test now checks the legend's description before its quotation. An f6 header check joined every quoted phrase of the header; it now reads the first quote.

## Trust, DELTA, light lane

- `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 ... PASS". No allowance, no FOLLOW-UPS row.
- DELTA: none. No product code changed; the only answer changes are the PROJECTED union counts above, and VE's answers did not move.
- `light-lane.py check`: "NOT 546 changed lines outside generated files > 150". There was no trust_mutants sweep: no Lean changed and no trusted definition is new, so there is nothing to mutate. Round 1 recorded the same.
- Lean: no Lean file changed, so no lake build or lean/audit.py run was owed.

## ucfix-budget readings

The launcher owns `ucfix-budget.py --check` (fixloop.sh, before each fix round). No `safety-framework-fidelity-fix-2-loop.log` exists at report time, and safety-framework-fidelity-fix-2.chain.log is empty (0 lines; manage-agents, read 2026-11-13). This build is the item's first chain session, so no fixloop reading exists yet. I did not run the check (task rule).

## Overlap (re-checked 2026-11-13 against every lean-first/, feature/, infra/ and foundation/ branch)

No branch touches usecases/safety-framework/ or tests/test_safety_framework.py. Two in-flight branches touch generated files this item also regenerates:
- feature/openai-preparedness-fidelity-fix-4: conformance/english-lean/lexicon-report.json (its own row);
- feature/ve-limits-lm1: tests/data/route-cases.jsonl (other lines).

Both resolve through their generators (`regen_generated.py --resolve`, route_fixtures.py). Row uc-audit-packet-fsf-history may reword PLAN.md:615 and README.md:124. This item touched PLAN.md only in section 12 (a new entry 25 after item 24), did not edit README.md, and wrote no repair-history wording into rules.d1.ve, vocabulary.py or PLAN sections 1-11.

## Notes for the DRI

- **README.md is stale on two figures.** It says CHECKED 4,043 (2,935) and M3 7.4%; the span map now gives 3,959 (2,851). The task forbids README edits here, and PLAN 12 entry 25 records the new figures. The owner of README (uc-audit-packet-fsf-history or a later row) can refresh them.
- **f6 C5 (single-seat, sess-1).** Astra noted that PLAN 3.1:97 leaves a "will" sentence carrying "as needed" un-narrowed (RS4). Here "as needed" qualifies the experts' involvement, not the assessment. The header says so, and the rule keeps N1's strict commitment. Adding an RS4 reading set for F6 would be a reading the task does not name, so it is not done. The re-read may raise it again.
- **D2D3 C7 (single-seat, sess-2).** Astra found that the 365-day bridge for "a year" applies to an unstated anchor (severity_and_dates.py:224). The task names only src:15's conditions for D2D3, so this is unchanged. The re-read may raise it.
- **Act phrases.** f20-holistic's and f20-within's acts are unchanged; their legends and headers carry the restored text. The 80-character act limit, with "and" reserved, leaves no faithful act that names both the mitigation and its effects, or "the T/CCLs".
- **N3 and the f20 pairs.** N3 is the one answer batch 6 regains. It rests on all six f20 units, so it needs all three pairs to pass the re-read.

## Spec re-read

- "header quotes the full source sentence; the guard or act carries the condition 'where a CCL has been reached'; one shared predicate or legend, changed once" (task, deliverable 1), against R f3/f12-*/f13-*. Each header quotes the sentence, each guard names `..._with_safety_case_where_ccl_reached`, and the legend changed once in V.
- "act within 80 characters, or the legend quotes the full sentence" (deliverable 3) against `proximity_assessed`: the legend branch.
- "Restore the relation in the act or legend" (deliverable 4) against `residual_assessed`: both.
- "a labelled span or a might cell, never as a duty; make spans.json say what is checked" (deliverable 5) against spans.json `s212-might-update`/`s312-might-update`: LABELLED, hedged.
- "proportionality covers the mitigation and its effects" (deliverable 6) against V `holistic`.
- "state src:15's conditions in the cell (severity_and_dates.py:101-104) ...; keep the might rendering" (deliverable 6, D2D3) against `UNRESTRICTED_L7_LABEL` and the cell: `might` true, `leads` false.
- PLAN 5 "exactly the levels named ... Every other open term is unset unless the case says so" against cases.json G8.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relay, schema or route changed (use-case files only).
2. Every deliverable built: PASS. Batches 1-6 each have a commit and a test (tables above); nothing was cut.
3. Tests can fail: PASS. Seeded bugs S-a..S-h (mutants.json), each failing its named test.
4. Python, Lean and Rust agree: PASS for the changed rule blocks. `test_lean_reads_each_pinned_block_as_python` (in tests/test_english_statement_blocks.py, 155 passed) reads the 44 recaptured FSF blocks; no Rust change.
5. R8 binding: N.A. No field Python reads from a Lean answer is new.
6. Gate evidence matches the final HEAD: PASS. Commits are listed from main..HEAD --no-merges; the chain runs the gate on the committed final HEAD.
7. No unsigned item: PASS. No DELTA rows; trust_map +0.
8. Every user-visible change is in DELTA: N.A. No product output changed; VE answers are unchanged (run.py 260/262 per batch).
9. Test selection: PASS. `tools/select_tests.py --base 6949e5de43` selects tests/test_safety_framework.py, the test file whose tests the seeds S-a..S-h make fail (60 units in all).
10. Lean statements: N.A. No Lean change.
11. Budgets and deadlines: N.A. No evaluator or limit was added. The tests use no sleeps or deadlines.
12. No CPU or memory regression: N.A. Use-case data only. run.py times were 155.8 s, 112.3 s, 107.9 s, 107.3 s and 121.3 s, against 167.1 s after batch 1.
13. Test-removed trailers: N.A. No test was removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. The batch-1 test covers with and without the OT3 finding; the f16 test covers with and without OT4/OT5; the f14 test checks the duty CHECKED and the possibility LABELLED. Commands are cited above; the spec re-read section is above.
15. No overclaim, no silent cut, every check can fail, limits charged: PASS. The counts are labelled PROJECTED; no deliverable was cut; S-a..S-h; no limits are involved (N.A. for that sub-item).

## Next item

After merge, the production checklist pass re-reads ONLY the changed units (f3, f12-p, f12-u, f13-p, f13-u, f16-ds, f16-ds-strict, f6, f7-rra, f14, the six f20 units, FACTS, CASES, D2D3). Then comes the full union audit at the Nov 23 checkpoint, which needs row uc-audit-packet-fsf-history merged. The DRI decider launches both.
