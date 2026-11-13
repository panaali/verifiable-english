# openai-preparedness-fidelity-fix-3: PF round B part 1 (the six units REAL by both adjudicators)

Status: all 6 units fixed, in the task's batch order (4 batches, one commit each). Then tests, regeneration, PLAN 12 item 24 and seeded bugs. Branch `feature/openai-preparedness-fidelity-fix-3`.
Changed: the situation sort's legend (no "covered"), and the acts and legends of `safeguards_report`, `cyberdefense_contribution` and `research_review`. The legend of `reasonable_evidence` also changed. No ve/, lean/ or rust/ change; no key edit; no answer changed (results.json is byte-identical to main's).
Union count: PROJECTED 90 -> 118 (batch 1) -> 125 (batch 2) -> 132 (batch 3) -> 132 (batch 4). The re-read decides.
Open: no question sent; no DRI signature needed; DELTA: none.

## Units changed, by checklist class

| unit | finding (who, where) | fix | classes |
|---|---|---|---|
| f4-security | (b) sess-3 C7: "Every situation" (R:54) inherits "a development, use, deployment, review or decision of a covered model" (V:238), despite the header's "no coverage condition"; pf-adjud Q08 REAL by both | the `situation` sort's legend is now "a development, use, deployment, review or decision of a model" (DRI ruling of 2026-11-12 on fix-2's question 3, item 2). `covered` stays only as the explicit guard of F2, F7, F8, F9 and `f16-sag-recommend`. f4-security's rule and the C.3 practice list are unchanged | 7 |
| f9-report | (b) sess-4 C1: "VE requires only 'have a Safeguards Report' (R:66); its legend is merely '4.1 and 4.2'"; Q10 REAL by both | act "{0} have planned safeguard information compiled into a Safeguards Report" (72 characters). The legend quotes 4.2 in full: "We compile the information on the planned safeguards needed to minimize the risk of severe harm into a Safeguards Report.", plus section 4's scope. The guards `covered` and "has reached a level" stay (PLAN 12 item 11) | 1 |
| f1-contrib-cyb-strict | (b) sess-2 C1: "omitting the tools' explicit purpose"; legend "Table 1 CYB-H: cyberdefense contribution"; Q06 REAL by both | shared act "{0} contribute to improved cyberdefense policies as well as cyberdefense tools" (78 characters). The legend quotes "Contribute towards improved cyberdefense policies and tools for cyberdefense" | 1 |
| f1-contrib-cyb-default | the same (R:28); Q05 REAL by both | the same predicate, changed once. The header now quotes the CYB-H bullet instead of "the same imperative" | 1, 11 |
| f10-review | (b) sess-5 C1/C7: the guard legend (V:41) drops "as expected" and replaces "we find" with existence; Q02 REAL by both | the `reasonable_evidence` legend reads "at {0} OpenAI ('we') finds reasonable evidence that its safeguards are not working as expected (4.2: “If we find reasonable evidence that our safeguards are not working as expected”); OpenAI ('we') decides this (OT11)". The guard is shared with **f10-validate** (pending 18), so changing it once changes both | 1, 7 |
| f13-review | (b) sess-9 C1/C2: "The review's specified objects - latest research and findings - are absent"; "each" is lost; Q09 REAL by both | act "{0} review the latest research as well as findings in each Research Category" (76 characters; "each" is no reserved word, so it stays in the act and STOP RULE question 2 was not needed). The legend quotes 2.3 in full. The periodicity stays ET-blocked (build_document `PLACEMENTS`) | 1, 2 |

Counts per class (units): class 1: 5; class 2: 1; class 7: 2; class 11: 1. Every changed block's header quotes its full source sentence, checked by `test_every_header_quotes_whole_source_text` on the regenerated `quote-hashes.json` (quote_evidence.py; 116 quotes, 0 unanchored).

The situation sort's legend changed for every unit that reads the sort. The ruling asks the post-merge re-read to re-read all of them. These are 85 rule blocks plus FACTS (the list is computed from rules.d1.ve; it is every block except f16-year, f17-suff, f17-iff, f17-iff-only, cl-levels and fn5-indicator):
f1-misuse-bio-strict, f1-misuse-bio-default, f1-misuse-cyb-strict, f1-misuse-cyb-default, f1-alignment-cyb-strict, f1-alignment-cyb-default, f1-security-strict, f1-security-default, f1-halt-strict, f1-halt-default, f1-contrib-bio-strict, f1-contrib-bio-default, f1-contrib-cyb-strict, f1-contrib-cyb-default, f2-deploy, f2-deploy-any, f2-reminder, f2-reminder-any, f2-security-developed, f2-no-deploy, f2-no-deploy-any, f3-develop, f3-develop-forecast, f3-develop-inuse, f3-develop-inuse-forecast, f3-inuse, f3-inuse-forecast, f3-reminder, f4-security, f7-evaluations, f7-report, f7-compile, f7-recommend, f8-start, f9-report, f9-residual-strict, f9-residual-default, f9-risk-paths, f9-specific, f9-efficacy, f9-threshold, f10-validate, f10-review, f14-document, f14-investigate, f14-corrective, f14-summary, f15-disclose, f15-safeguards, f15-third-party, f16-sag-recommend, c2-misalignment-strict, c2-misalignment-default, c3-access-strict, c3-access-default, cl4-persuasion, f16-ssc-visibility, f16-informed, f16-without-noinput, f16-without-nodelib, f16-board-reverse, f16-board-mandate, f16-chair-strict, f16-chair-default, f5-ambiguous, f5-checkpoint, f6-rel, f11-within, f11-exception, f11-exception-deploy, f11-acknowledge, f11-protect, f11-share, f12-lra, f12-lra-unscoped, f12-sandbagging, f12-sandbagging-unscoped, f12-ara, f12-ara-unscoped, f12-undermining, f12-undermining-unscoped, f12-nuclear, f12-nuclear-unscoped, f13-review, f13-results; FACTS.
This closes fix-2's open C7 on f3-develop-inuse(-forecast).

Other blocks changed only because a named fix changed something they use:
- f10-validate: its guard legend, `reasonable_evidence`.
- accounting.d1.txt:
  - The lines of f9-report, f10-validate, f10-review and f13-review drop the entries for words the new legends now carry. f9-report's "loss 1" is gone, and f13-review now "omits: nothing".
  - `safetyfw_accounting.py --check` passes. The saved report `docs/usecases/safetyfw/openai-preparedness/accounting.json` was regenerated with `--source`: losses 24 -> 23, blocks with a loss 18 -> 17.

No other block, case or query changed. run.py needed no change, because the predicate names are kept.

## Batches: PROJECTED union count after each

Method: /tmp/pf3/project.py re-applies uc-score-2's rule to the union `VERDICTS.md` rows at 175814252d. An item counts if it was FAITHFUL, its VE answer equals the key, and every unit it uses is FAITHFUL, fixed or cleared. The script reproduces the baseline: with nothing fixed it gives 87, the value in score.json. Round A's 12 units (fix-2's REPORT) plus f9-threshold (cleared) give 90. Each batch ran `run.py`: batch 1 the full run, batches 2-4 `--base-only`. Every run gave 236 / 239, and the only disagreements were the same three rows: C6, C-doc and G9.

| Batch | Units | run.py | Answer changes old -> new | PROJECTED union count |
|---|---|---|---|---|
| 1 | f4-security | 236 / 239 (full run; results.json identical to main's) | none | 118: the 28 A-*/SEC items now rest on no failing unit |
| 2 | f9-report | 236 / 239 | none | 125: the 7 B-*/SAFEREP items |
| 3 | f1-contrib-cyb-strict, f1-contrib-cyb-default | 236 / 239 | none | 132: the 7 B-*/CONTRIB items |
| 4 | f10-review, f13-review | 236 / 239; final full run 236 / 239 | none | 132: K5 still needs f10-validate; N3 still needs 18 other units |

Old -> new for the items the task names. All are unchanged and agree with the key (main's and HEAD's results.json `comparison`; /tmp/pf3/diffres.py: "comparison rows changed: 0"):

| items | old -> new | key | union status after this item (PROJECTED) |
|---|---|---|---|
| A-L0-{DEV,EXT,INT,LINT}/SEC (4) | NONE -> NONE | NONE | counted (f4-security fixed) |
| A-{BIO,CYB,AIS}-H-{DEV,EXT,INT,LINT}/SEC (12) | ALL -> ALL | ALL | counted |
| A-{BIO,CYB,AIS}-C-{DEV,EXT,INT,LINT}/SEC (12) | SOME(RS1=strict&RS2=nest \| RS1=default&RS2=nest) -> the same | SOME(nest) | counted |
| B-L0/SAFEREP | NONE -> NONE | NONE | counted (f9-report fixed) |
| B-{BIO,CYB,AIS}-{H,C}/SAFEREP (6) | ALL -> ALL | ALL | counted |
| B-L0/CONTRIB, B-BIO-H, B-AIS-H, B-AIS-C /CONTRIB (4) | NONE -> NONE | NONE | counted (both f1-contrib-cyb units fixed) |
| B-BIO-C/CONTRIB, B-CYB-H/CONTRIB | ALL -> ALL | ALL | counted |
| B-CYB-C/CONTRIB | SOME(RS1=strict&RS2=nest \| RS1=default&RS2=nest) -> the same | SOME(nest) | counted |
| G5 | ALL -> ALL | ALL | not counted: f1-halt-*, f1-misuse-bio-*, f2-no-deploy-any, f3-develop(-forecast), f3-reminder |
| K5 | ALL -> ALL | ALL | not counted: f10-validate (pending 18) |
| N3 | NONE -> NONE | NONE | not counted: 18 other failing units |

## Checks run (on the final code)

- `lake build`: "Build completed successfully (1433 jobs)". Lean is unchanged; the build is for the service run.py uses.
- `run.py` (full): "236 / 239 (1287.9 s)". results.json is byte-identical to main's.
- `build_document.py`: coverage.json was regenerated; only `document_sha256` changed. `build_document.py --check`, `stage0.py --check` and `measure.py --check`: all exit 0.
- `pf_vocabulary.py` regenerated environment.d1.json.
- `quote_evidence.py` regenerated quote-hashes.json.
- `safetyfw_accounting.py openai-preparedness --check`: no problems; "0 of 116 quotes unanchored".
- `pytest tests/test_pf_fidelity_fix.py tests/test_usecase_key_transcription.py`: "72 passed".
- `pytest tests/test_safetyfw_accounting.py -k preparedness`: "2 passed".
- Frozen key: `test_answer_key_equals_section_6_cell_by_cell`, `test_section_6_is_the_frozen_key` and `test_transcription_is_pinned` are unchanged and selected (`select_tests.py` lists tests/test_pf_fidelity_fix.py and tests/test_usecase_key_transcription.py).
- Regulated predicates: 60 of 64, none added. `test_regulated_predicates_stay_within_64` asserts 60.
- Selected tests (mac-pytest.sh --select, on the committed final code): see the build report.

## Open list

- Questions sent: none.
  - Question 1 was pre-answered: reviews/dri-decisions-20261112-openai-preparedness-fidelity-fix-2-q3.md item 2.
  - Question 2 was not needed: "each" is no reserved word, so the act states "in each Research Category".
  - Question 3 was not needed: no answer moved.
- Amendments: none clears a unit.
- Out of scope, with their rulings:
  - C6, C-doc and G9 (VE answer != key): PLAN 12 items 19-20, key findings; the keys and the scorer are untouched.
  - The 3 split units f16-without-noinput, f1-misuse-bio-default and f16-sag-recommend: pf-adjud Q01, Q03 and Q04. They count as failing until the DRI rules.
  - f9-threshold: Q07, NOT by both, cleared under item 13.
  - The 18 units under adjudication (rest-list.txt): six of them are REAL by both and go to prompts/task-openai-preparedness-fidelity-fix-4.txt; the others await a DRI ruling.
  - Row checklist-recalib-pf: addendum 8 item 54 / addendum 9 item 58.

## Seeded bugs (Python use-case files; no Lean or Rust product code changed)

Recorded in `mutants.json`. Each bug was planted, its one test run and the file restored; the tree was clean after each.

| id | file | bug | failing test |
|---|---|---|---|
| a | usecases/openai-preparedness/pf_vocabulary.py | situation legend back to "... of a covered model" | test_f4_security_reads_no_coverage_condition |
| a' | usecases/openai-preparedness/rules.d1.ve | f4-security gains "(a) that situation is covered" | test_f4_security_reads_no_coverage_condition |
| b | pf_vocabulary.py | act back to "{0} have a Safeguards Report" | test_f9_report_act_states_the_compilation_and_its_legend_quotes_4_2 |
| b' | pf_vocabulary.py | legend back to "4.1 and 4.2" | the same |
| c | pf_vocabulary.py | "for cyberdefense" dropped from the shared legend | test_cyberdefense_tools_keep_their_purpose |
| d | pf_vocabulary.py | "as expected" dropped from the reasonable_evidence legend | test_reasonable_evidence_quotes_4_2s_condition_with_its_decider |
| d' | pf_vocabulary.py | "we find" -> "there is" in the quoted condition | the same |
| e | pf_vocabulary.py | act without "the latest research as well as findings" | test_f13_review_names_the_latest_research_and_findings_per_category |

Bug (d) first survived: the test checked the quote but not the legend's own wording. The test was tightened (commit "pins \"as expected\"") and bug (d) now fails it. Bug (a')'s first form was ill-formed VE and failed on a SyntaxError, which does not count. It was replanted in valid form and now fails on the predicate-set assertion.

## Budget readings

The launcher's reading in the task's AMENDMENTS, 2026-11-12 20:16Z on VM1: 9.39M CW in 24 h; joint allowance left 4.61M of 14M; round budget 1.00M (ALLOCATED): START. No `openai-preparedness-fidelity-fix-3-loop.log` exists in manage-agents, so no further reading was taken. I did not run ucfix-budget.py myself.

## Size

SIZE: 59 product (use-case translation: pf_vocabulary.py 21, rules.d1.ve 10, accounting.d1.txt 8, PLAN.md 20), 99 tests, 63 other hand-written lines (mutants.json), plus this REPORT. Generated: environment.d1.json, coverage.json, quote-hashes.json, accounting.json. Source: `git diff --numstat $(git merge-base HEAD main)`.

## Notes for the DRI

- "towards" became "to" in the cyberdefense act. The task's example, "cyberdefense policies as well as cyberdefense tools", is 83 characters with "towards", over the limit of 80. The legend keeps the bullet verbatim.
- f7-report keeps its explicit `covered` guard although its header (3.3, "The SAG reviews the Capabilities Report ...") does not say "covered". The coverage comes from 3.3's context ("every covered model undergoes ..."), and the ruling's survey lists F7. It is not in this item's scope. The test pins the exact set of covered-guarded rules, so any change to that set is visible.
- f10-review's K5 and N3 also rest on f10-validate, which shares the guard changed here. f10-validate's own finding (pending 18) may need more than the guard.

## Spec re-read

- Situation legend against reviews/dri-decisions-20261112-openai-preparedness-fidelity-fix-2-q3.md item 2: "... of a model", with "covered" kept only as an explicit guard.
- f9 legend against pf-v2.txt section 4.2: "We compile the information on the planned safeguards needed to minimize the risk of severe harm into a Safeguards Report." (exact).
- CYB-H bullet against pf-v2.txt, line 6 of the extracted text: "Contribute towards improved cyberdefense policies and tools for cyberdefense" (exact).
- OT11 against PLAN.md:112: "reasonable evidence that our safeguards are not working as expected", decider `we`.
- 2.3 against pf-v2.txt, line 8 of the extracted text: "We will periodically review the latest research and findings for each Research Category." (exact).
- Act limits against lean/VE/Norms/Wire.lean:33 (80 characters including "{0} ") and lean/VE/Acts/LexicalBase.lean:8 (the reserved words).

## Next item

After merge, the DRI decider launches the production checklist pass. It re-reads only the changed units (addendum 8 item 56). Because the situation legend changed, that is every unit listed above. The full union audit follows at the Nov 23 checkpoint. Then come openai-preparedness-fidelity-fix-4 (the six REAL-by-both units of the other 18) and any K rulings. I ran no audit.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relay, schema or Lean change.
2. Deliverables built, no rule broken: PASS.
   - The 6 units are covered by the per-unit tests in tests/test_pf_fidelity_fix.py (test_f4_security_reads_no_coverage_condition ... test_f13_review_names_the_latest_research_and_findings_per_category).
   - The diff contains no Python copy of a decision and no report test.
   - No in-flight branch touches these files (checked with `git diff --name-only main...<branch>` over every feature/infra/lean-first/foundation branch).
3. Tests can fail: PASS. 8 seeded bugs, each failing a named test (mutants.json).
4. Py/Lean/Rust agree: N.A. No product code changed; the run.py answers come from the Lean service (236 / 239).
5. R8 binding: N.A. No relay.
6. Gate evidence matches the final HEAD: PASS. results.json and coverage.json were regenerated on the final translation; the `--check` scripts exit 0.
7. No unsigned item: PASS. No DELTA row; no signature reserved.
8. User-visible change in DELTA: N.A. This is use-case data only; no ve/, lean/ or rust/ change and no verdict change (results.json identical).
9. Test selection: PASS. `select_tests.py --base <merge-base>` selects tests/test_pf_fidelity_fix.py, test_safetyfw_usecases.py, test_safetyfw_accounting.py and test_usecase_key_transcription.py.
10. Lean statements: N.A. No Lean change.
11. Budgets and limits: N.A. No evaluator or limit changed. The act limit of 80 is checked by test_the_six_changed_acts_fit_the_act_limit and by Lean at build.
12. CPU/memory: N.A. Only the wording of legends and acts changed; run.py took 1280.8 s at batch 1 and 1287.9 s at the end.
13. Test-removed trailers: N.A. No test removed or renamed.
14. Both directions, cited evidence:
    - PASS. test_f4_security_reads_no_coverage_condition pins both directions: f4-security reads no `covered`, and the 11 rules whose source states coverage keep it.
    - The f9 test checks that the new act is present and that the covered and reached guards are kept.
    - The claims above cite their commands.
15. Overclaim, silent cut, new checks fail, limits charged:
    - Overclaim: PASS. Every union number is labelled PROJECTED, from /tmp/pf3/project.py.
    - Silent cut: PASS. All 6 deliverables were built.
    - New checks fail: PASS. mutants.json.
    - Limits charged: N.A. No evaluator.
- Sibling lesson (fix-2 review F1: a premise unit named by no item): PASS. No block moved out of a collection unit. The units each fixed answer rests on are still named in its record (VERDICTS uses: A-*/SEC name f4-security, B-*/SAFEREP f9-report, B-*/CONTRIB both f1-contrib-cyb units, K5 f10-review and f10-validate).
