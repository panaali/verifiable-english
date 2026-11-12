# fsf-fidelity-fix: the DeepMind FSF translation repaired where both uc-auditors found it unfaithful

No DRI signature is reserved and no DELTA row exists: no product code (ve/, lean/, rust/) changed, and the task puts the
answer changes in this report (old -> new, below). The gate is the DRI's signed decision,
`reviews/dri-decisions-20261029-uc-audit2.md` item 1, (a)-(d) and its condition.

Branch `feature/fsf-fidelity-fix`, base main `e78b6d949`. Commits (`git log --oneline main..HEAD`): 64f7f147b (translation
repair and regenerated outputs), 429e7c019 (norm-block recapture, R-stale, quantifier fixture), dfdc814dd (f16 fixture),
1858cd932 (seeded-bug record), 9b5594edb (Test-removed trailer), 81315d460 (lexicon report), and this report.

SIZE: 0 product, 117 tests, 384 other hand-written lines (`git diff --numstat $(git merge-base HEAD main)`, without this
report; 2,720 generated lines: results.json, coverage.json, spans.json, readings/results.json, environment.d1.json,
tests/data/norm-blocks/fsf.jsonl, tests/data/route-cases.jsonl, conformance/english-lean/lexicon-report.json).

## Deliverables

| Decision row | Delivered | Evidence |
|---|---|---|
| (a) remove RS9 = same, RS6 = same and the rules only they select | `translation.READING_SETS` keeps one reading ("different") for RS6 and RS9; `translation.EXCLUDED_READINGS` records both with the source reason; f10-dm-same, f10-rel-same and f15-same are deleted from rules.d1.ve, build_document.READINGS (sets rs6_insider, rs9_bullet3 gone), run.CONFLICT_CLUSTERS and reference.SETS; a rule block naming an excluded reading is refused when read (`read_blocks`). PLAN section 12 item 23 lists both under "Excluded readings", citing footnote 5 (p.7), R14 and this item. | `test_excluded_readings_and_their_rules_are_never_offered_again`; seeded bug S1 (RS9 = same restored) fails it |
| (b) fix the other agreed-unfaithful blocks, each quoting its span | f4-check-d/-r plus f4-need-d/-r, f9-acc, f10-acc, f10-rel-diff, f11-rel, f16-ds, f16-ds-strict, f17-pra plus f17-hri, f20-holistic-*, f20-within-*, FACTS (bridge-one-domain), CASES (G7, G8). Table by class below; each rules.d1.ve header quotes the span. PLAN section 12 item 24. | `test_one_mitigated_level_does_not_discharge_another_reached_level`, `test_a_possible_adjustment_is_no_exception_to_the_recommended_level`, `test_results_agree_with_the_key_except_the_recorded_findings` (A-L5/6/7-INT/DM now agree), `test_rerun_equals_committed_results` |
| (c) section-12 entries giving NONE for C1, C3 and C-doc, key untouched | PLAN section 12 item 23. answer-key.json is unchanged (`test_answer_key_is_the_transcription`: sha256 8fbb0475... as before); PLAN section 6 is unchanged (my edit script asserted the section's text equal before writing). run.py `DEVIATIONS` adds a `deviation` field beside each of the three rows. | `test_results_agree_with_the_key_except_the_recorded_findings` asserts the three entries and their agreement |
| (d) regenerate results.json, coverage.json, readings/results.json by the harness; the condition | run.py wrote results.json (260/262 against the key); build_document.py wrote spans.json and coverage.json; readings_r1.py wrote readings/results.json. `run.py --check` (`test_rerun_equals_committed_results`, passed in the selected run), `build_document.py --check` and `readings_r1.py --check` (both exit 0 with the pinned source, sha256 18e3375b..., copied from the debate folder) | Condition: no rule is selected under RS9 = same or RS6 = same (no such choice exists; the test scans every choice, detail and rule list of results.json); the run's C1, C3 and C-doc are NONE and agree with the section-12 NONE entries |
| uc-audit re-run | Not run here, as the task says. | next item `fsf-fidelity-audit` |

## Answer changes (old -> new; `run.py`, comparison rows of results.json, main e78b6d949 against HEAD)

| Item | Old VE | New VE | Against the key | Unit that moved it |
|---|---|---|---|---|
| A-L5-INT/DM | NONE, REL NONE | NONE, REL SOME(RS1=G & RS8=rel) | disagree -> agree | f11-rel (release covers ordinary internal deployment) |
| A-L6-INT/DM | NONE, REL NONE | NONE, REL SOME(RS1=G & RS8=rel) | disagree -> agree | f10-rel-diff |
| A-L7-INT/DM | NONE, REL NONE | NONE, REL SOME(RS1=G & RS8=rel) | disagree -> agree | f10-rel-diff |
| C1 | SOME(RS3=Ds & RS3force=strict & RS6=same) | NONE | disagree -> agree (key NONE; section-12 NONE agrees) | f15-same removed (RS6 = same) |
| C3 | SOME(RS1=G & RS8=rel & RS9=same) | NONE | agree -> disagree with the key's literal cell; agrees with section-12 NONE | f10-dm-same, f10-rel-same removed (RS9 = same) |
| C-doc | SOME(RS1=G & RS8=rel & RS9=same \| RS3=Ds & RS3force=strict & RS6=same) | NONE | disagree -> disagree with the key; agrees with section-12 NONE | the two above |

Agreement with the key: 257/262 -> 260/262; 262/262 counting the section-12 entries. The key's C3 and C-doc condition
names RS9 = same, which no admissible choice satisfies; `run.same_set` counts such a condition as a disagreement, never as
a vacuous NONE (seeded bug S2). Every other keyed answer is unchanged (the comparison script over both results.json
files printed only these six rows); 31 items' choice records changed only because their cones lost the second value
of RS6 or RS9. G7, G8 and N1 keep their answers (ALL) with the CASES and FACTS fixes: N1's certificate is now from the
premises plus N1's own four-exclusion bridge (`items.N1.own_premises == ["bridge-one-domain"]`, both certificates
replayed). Other measured changes: M7 conflicted cells 3 -> 0 (B-L2/3/4 RECSEC were the RS6 = same conflict);
mutant m6's C3 SOME -> NONE (PLAN 11 expected exactly this; item 15's "moved" conflict needed RS9 = same); prover calls
2,054 -> 1,732; premises 43 -> 37.

Coverage (coverage.json): master CHECKED 4,595 -> 4,558 bytes, OPEN 7,356 -> 7,439, LABELLED 35,557 -> 35,511;
s131-four-domains CHECKED -> LABELLED (the bridge is not stated), s22-insider-not-required OPEN -> CHECKED (f15-diff, one
reading left), s321-internal LABELLED -> OPEN (f17-hri). readings/results.json: 16 placed sets, 5 with content (was 18
and 7).

## Fixes by failure class (prompts/translation-fidelity-checklist.md)

| Class | Units changed | The fix and the span it follows |
|---|---|---|
| 1 Dropped conjunct or clause | f4-check-d, f4-check-r (+ f4-need-d, f4-need-r); f17-pra (+ f17-hri) | 1.3.2 "we determine whether a substantial modification has been made and whether a further critical capability assessment is required if (1) ... and (2) ...": the second determination is its own obligation (`further_need_checked`), under both RS5 readings. 3.2.1 "these assessments will also account for the safety implications of high-risk internal deployments for such models": f17-hri (`periodic_covers_internal`); PRA asks both predicates. Each is a separate rule because Lean's act-phrase check refuses a phrase over 80 characters or with "and", "is" or "for" (`canonicalAct`, lean/VE/Norms/Wire.lean). |
| 2 Quantifier scope | f9-acc, f10-acc | 2.1.2 and 3.1.2 step 2 "for the T/CCLs the model has reached": the conditions hold "for every level that is misuse and that that proposal has reached" (F9), and for every critical ML R&D level reached (F10), beside the existence of one. |
| 3 Exclusive "only" | f10-rel-diff, f11-rel | 1.3.5 bullets 3 and 4 "This is required only for external deployment and high-risk internal deployment, not further development": the release (RS8 = rel) covers further development and internal deployment that is not high-risk. |
| 4 One predicate across bullets | f10-dm-same, f10-rel-same, f15-same removed; RS9, RS6 one reading | footnote 5 "deployment mitigations for the ML R&D CCLs are different than those for the misuse CCLs"; 2.2 insider *misuse* against 2.1.1 insider *threats* (R14). |
| 5 Modal strength | f16-ds, f16-ds-strict | 2.2 "may be adjusted if our understanding of the risks changes. This may occur if, for example, ...": OT16 (`like_public_models`) is no exception any more; 1.3.5's "or we otherwise assess that the level of security applied is adequate ... or we assess that the benefits of the open release ... outweigh the risks" stays the excepted case. |
| 6 Obligation turned into method | f20-holistic-strict, f20-holistic-default | 1.3.5 Note "The mitigation and the effects of such mitigation should also be assessed holistically and be proportionate with expected impact of a model's risk": act "have holistically assessed mitigations proportionate with expected impact" (the mitigation itself must be proportionate). |
| 7 Invented guards and exclusions | f20-within-strict, f20-within-default; FACTS bridge-one-domain | Glossary "The residual risk should be brought within the acceptable levels, as determined by the T/CCLs as relevant": no reached-level guard. The bridge is no premise of the document (header `item N1`, `translation.facts("N1")`); only the four exclusions N1 needs remain (cyber and harmful manipulation against CBRN and ML R&D), marked as N1's assumption; unit s131-four-domains is LABELLED. |
| 8 Case facts fixing open terms | CASES G7, G8 | PLAN 5 "Every other open term is unset unless the case says so": G7's OT11 findings and G8's `governance_found_acceptable` (OT3) removed. |
| 9 Readings that manufacture conflicts | RS9 = same, RS6 = same | removed (deliverable a); C1, C3, C-doc NONE. |
| 10 Key cells | C1, C3, C-doc | PLAN section 12 item 23 (NONE), key file untouched. |
| 11 Elided quotes | f4 headers, f16 headers, f17-pra/f17-hri headers | Checked each against the full sentence in the pinned source (`fsf-3.1.txt`); the f4 header now quotes the whole sentence with conditions (1) and (2). |

Blocks kept, with the reason: f2, f3, f4-further-r, f5, f6, f7-rra, f7-sc, f8, f9-dm, f9-sec, f9-rel, f10-dm-diff (header
now cites footnote 5), f10-sec, f11-acc, f11-dm, f11-sec, f12-p, f12-u, f13-p, f13-u, f14, f15-diff, f17-add,
f18-yearly, f18-frequent, f19-default, f20-elicitation-*, and every fact block except bridge-one-domain: both auditors
found each FAITHFUL in round 3, and no class above applies (f11-acc's "there is a level" ranges over the one ML R&D TCL
the text defines, so class 2 does not change it).

**Still disputed, unchanged (8 items, A-L6/L7-*/DM):** A-L6-DEV/DM, A-L6-HRI/DM, A-L6-LRX/DM, A-L6-EXT/DM, A-L7-DEV/DM,
A-L7-HRI/DM, A-L7-LRX/DM, A-L7-EXT/DM. Their answers are unchanged (all agree with the key). The dispute was whether
f10-dm-same decides them; that rule no longer exists, so the re-run audit settles them.

## Seeded bugs (docs/usecases/safety-framework/fsf-fidelity-fix/mutants.json)

Each was planted, run against one test, seen to fail, and restored (`git checkout -- usecases`):

| Id | File | Behaviour | Failing test |
|---|---|---|---|
| S1 | usecases/safety-framework/translation.py | RS9 = same restored in the readings (the task's required seed) | test_excluded_readings_and_their_rules_are_never_offered_again |
| S2 | usecases/safety-framework/run.py | the excluded-reading refusal in `same_set` deleted | test_results_agree_with_the_key_except_the_recorded_findings |
| S3 | usecases/safety-framework/facts.d1.ve | the bridge made a premise of the document again | test_every_rule_and_premise_parses_with_one_reading |
| S4 | usecases/safety-framework/rules.d1.ve | f9-acc back to "there is a level such that" | test_one_mitigated_level_does_not_discharge_another_reached_level[levels0-EXT-adequate0] |
| S5 | usecases/safety-framework/rules.d1.ve | f11-rel releases only further development | test_rerun_equals_committed_results ("results.json is out of date") |
| S6 | usecases/safety-framework/reference.py | bullet 3/4 release narrowed to further development | test_reference_reading_agrees_with_the_key_and_with_ve |
| S7 | usecases/safety-framework/rules.d1.ve | OT16 restored as an f16 exception | test_a_possible_adjustment_is_no_exception_to_the_recommended_level |

No Lean, Rust or `ve/` code changed, so no seeded bug is owed in those languages.

## Tests

- Selected run, on the committed tree at 9b5594edb (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base
  e78b6d949 --run`; ran locally, the Mac being last resort): 55 units, 54 passed, 1 failed:
  `tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon` (the committed
  lexicon report holds the FSF environment's lexicon id). Fixed in 81315d460 by its generator
  (`uv run python -m conformance.english_lean_lexicon`, only the safety-framework row moves: 81 -> 83 symbols); the
  failed id rerun alone passed (`mac-pytest.sh -- <id>`: 1 passed).
- `tests/test_english_statement_blocks.py` and `tests/test_safetyfw_accounting.py`: 64 passed after the recapture; Lean
  reads all 44 new FSF blocks as Python does (`test_lean_reads_each_pinned_block_as_python`).
- `uv run python tools/gate_collection.py --check --prebuilt`: 4 added, 1 removed by a trailer, 0 refused, 0 stale, 0
  malformed.
- `uv run python tools/regen_generated.py --check`: 40 entries checked, up to date.
- No test of main-known-red.txt was hit.

## Trust

`uv run python tools/trust_map.py --check`: K +0, S +0, D +0, G +0, tied +0, trusted +0 against e78b6d94990f, PASS. No
trusted definition is new; no R16 allowance and no FOLLOW-UPS row. Light lane: NOT (3,204 changed lines counted, most of
them regenerated results); no trust_mutants sweep, since no Lean changed and there is no trusted definition to mutate.

## Pilot bytes

deepmind-fsf (weight 3, 54,373 B) stands at 185/262 audit-verified. If the re-run audit agrees with these fixes, the
items the round-3 audit withheld through the repaired units (A DM 40, B PRA/RECSEC 16, R 10, C 4, G 4, N 2, K3 1) can
become audit-verified. Nothing is claimed before fsf-fidelity-audit reports.

## Next item

`fsf-fidelity-audit`: uc-audit safety-framework to convergence on the merged commit (its launcher runs it after the
merge). Its C1, C3 and C-doc rows should agree with PLAN section 12 item 23 (NONE).

## Notes for the DRI

- The reading sets RS6 and RS9 stay in the harness with one reading each, so the frozen key's condition notation
  (`RS9=same`) still parses. A key cell naming an excluded reading is a disagreement, so C3 and C-doc show as
  disagreements against the literal key and as agreements against section 12 (both shown per row).
- fsf-r2 (2026-10-28) evidence is read as saved (D4): `test_fsf_r2_measures_every_unit_as_saved_and_none_moved_since_oct18`
  now checks the saved units.json and gaps.json instead of re-measuring the live translation, and the live probe rerun
  `test_fsf_r2_probes_rerun_equals_saved_probes` is removed with a Test-removed trailer (9b5594edb). Re-measuring would
  show three units moved (listed above) and JT-d's probe now spanning s321-internal.
- tests/data/norm-blocks/fsf.jsonl was recaptured with `capture_blocks.capture` for FSF only, pinned at 64f7f147b; the
  RSP file is untouched.
- OT16 (`like_public_models`) stays declared as an open term of the text (PLAN 3.2); no rule uses it now.
- Astra also noted that G7 tests only the TCL branch of "a TCL or ... a mitigated CCL"; the case's levels are unchanged
  (the task names only its OT11 findings). Opus's round-2 note on measures-sl2plus was not in the agreed list and is
  unchanged.

## Spec re-read

- (a) "remove RS9 = same and RS6 = same, and the rules only they select (f10-dm-same, f10-rel-same, f15-same)" against
  reviews/dri-decisions-20261029-uc-audit2.md item 1: the three ids are exactly the deleted blocks; f10-dm-diff,
  f10-rel-diff and f15-diff stay (selected by "different").
- (c) "Record PLAN section-12 deviation entries giving NONE for C1, C3 and C-doc" against the same item: PLAN 12 item
  23, three entries, answer NONE each; answer-key.json hash unchanged.
- Condition "the case's run selects no rule under RS9 = same or RS6 = same, and a test or fixture fails if either
  reading is offered again": `test_excluded_readings_and_their_rules_are_never_offered_again`, S1.
- FACTS "the bridge-one-domain exclusions only N1 needs, stated as the text gives them" against the task text and
  checklist class 7: four exclusions, N1 only; the header cites 1.2's separate domain lists.
- CASES "G7's OT11 and G8's OT3 left unset as PLAN 5 says" against PLAN.md section 5 "Every other open term is unset
  unless the case says so".

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relay, schema or route changed (no ve/, lean/ or rust/ file in the diff).
2. Every deliverable built: PASS, Deliverables table above ((a)-(d) each with its test; the audit re-run is the next
   item by the task's own words).
3. Tests can fail: PASS, seeded bugs S1-S7 (mutants.json), each with its failing test.
4. Python, Lean, Rust agree: PASS for the changed inputs, `test_lean_reads_each_pinned_block_as_python` (Lean reads all
   44 recaptured FSF blocks as Python).
5. R8 binding: N.A., no Lean answer is read by new code.
6. Gate evidence matches HEAD: PASS, main has not moved (`git rev-list --count HEAD..main` = 0); the chain gates the
   final HEAD.
7. No unsigned item: PASS, no DELTA row, no trust growth (`trust_map.py --check` +0).
8. Every user-visible change in DELTA: N.A. by the task (answer changes are in this report, "Answer changes").
9. Test selection finds the tests: PASS, the selected run picked tests/test_english_lean_lexicon.py, which caught the
   lexicon report.
10. Lean statements: N.A., no Lean.
11. Budgets fail closed: N.A., no budget or limit changed.
12. No CPU regression: PASS, the harness's cost fell (prover calls 2,054 -> 1,732; case models 658 -> 301; results.json
    `cost`).
13. Test-removed trailer: PASS, `gate_collection.py --check --prebuilt`: 1 removed by a trailer, 0 refused/stale/malformed.
14. Both directions, cited evidence, spec re-read: PASS, the quantifier and f16 tests check the accepted and the refused
    side (ALL with both levels mitigated, NONE with one; RECSEC required with OT16, not with OT4); the excluded-reading
    test checks refusal and the one-reading sets; spec re-read above.
15. No overclaim / no silent cut / every new check can fail / limits: PASS, "Pilot bytes" claims nothing before the
    audit; no deliverable cut; S1-S7; no limit-bearing code.
