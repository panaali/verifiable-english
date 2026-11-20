# defs-repair-safety-framework-1119 REPORT

**Summary.** Status: review fixes F1, F2 built (review of 610eafced7); ready for the chain gate. No DRI signature needed.
- 42 of the 44 P1 rows are KEPT, each whole quote unbroken in a shown and counted legend (28 legends, vocabulary.py);
  x33, x34 are DROPPED (carried by fsf-repair-f6-sl2plus-1119, now checked shown AND counted too).
- Condition test `tests/test_defs_repair_safety_framework_1119.py`: 138 passed at HEAD; main's legends: 44 failed.
- Open: none in scope; overlap with `infra/srccov-safety-framework-1119` (section 7). Base main 941208a12d.

## 0. Verification of every candidate (before any edit)

The pinned source `~/code/manage-agents/pilots/safety-framework/source/fsf-3.1.txt` has sha256 `18e3375b…c53946` and
54,373 bytes. Both match `usecases/pinned_sources.json` `safety-framework.text_sha256` / `text_bytes`
(`sha256sum`, `wc -c`). Each row's quote was searched in the source as a regex that varies only quote marks and
whitespace (/tmp/dsf/bin/spans.py). All 44 quotes occur exactly once, byte for byte, on the line the row names.
Each row was then checked at main 941208a12d against three things:
- the committed legend of its carrier (`omit_norm`, the project's quote normalisation);
- whether the carrier is used by the row's blocks (`tools/defs_carried_counter.used_predicates`);
- the counter's literal reading.

| row | verdict | reason (file:line at HEAD) |
|---|---|---|
| x1 | KEPT | PARTIAL-COVER:F2. F2 carried the Glossary entry's sentence 2 without its full stop; F2's quote now goes on with sentences 3-4 in one run (`frontier`, vocabulary.py:207; review F1) |
| x2 | KEPT | not on main; carried in `subsequent` (vocabulary.py:217) |
| x3 | KEPT | not on main; `concerns` (vocabulary.py:73) |
| x4 | KEPT | not on main; `misuse` (vocabulary.py:84) |
| x5 | KEPT | not on main; `ml_rd_and_misalignment` (vocabulary.py:90) |
| x7 | KEPT | not on main (fragment only); `critical` (vocabulary.py:53) |
| x8 | KEPT | not on main; `critical` (vocabulary.py:53) |
| x9 | KEPT | not on main (fragment only); `tracked` (vocabulary.py:64) |
| x10 | KEPT | not on main; `tracked` (vocabulary.py:64) |
| x11 | KEPT | not on main; `approaches` (vocabulary.py:169) |
| x12 | KEPT | not on main; `approaches` (vocabulary.py:169) |
| x13 | KEPT | not on main; `reached` (vocabulary.py:164) |
| x14 | KEPT | not on main; `further_assessed` (vocabulary.py:360) |
| x15 | KEPT | not on main; `further_need_checked` (vocabulary.py:355) |
| x16 | KEPT | not on main (F9 carries the 1.3.2 sentences, not the Glossary entry); `change_assessed` (vocabulary.py:365) |
| x17 | KEPT | not on main (as x16); `assessed` (vocabulary.py:339) |
| x18 | KEPT | not on main; `could_undermine_justification` (vocabulary.py:227) |
| x19 | KEPT | not on main; `mitigates` (vocabulary.py:244) |
| x20 | KEPT | not on main; `harm_mitigated` (vocabulary.py:429) |
| x21 | KEPT | not on main; `severe_harm_mitigated` (vocabulary.py:437) |
| x22 | KEPT | not on main; `significant_harm_mitigated` (vocabulary.py:443) |
| x23 | KEPT | not on main; `residual_assessed` (vocabulary.py:383) |
| x24 | KEPT | not on main; `mitigates` (vocabulary.py:244) |
| x25 | KEPT | not on main (paraphrase only); `external` (vocabulary.py:198) |
| x26 | KEPT | PARTIAL-COVER:F2. F2 carries sentence 1; the row's quote (sentences 2-3) is not on main; `secured` (vocabulary.py:449) |
| x27 | KEPT | not on main; `applies` (vocabulary.py:182) |
| x28 | KEPT | not on main; `recommends` (vocabulary.py:132) |
| x29 | KEPT | not on main; `recommends` (vocabulary.py:132) |
| x30 | KEPT | not on main; `recommends` (vocabulary.py:132) |
| x31 | KEPT | shown on main but not counted: F6 wrote its inner quotes `\"`, which the counter keeps; now “ ” (`recommends`, vocabulary.py:133-136; review F2) |
| x33 | DROPPED | already carried word for word in `recommends` by F6, footnote 12 (vocabulary.py:137-139) |
| x34 | DROPPED | already carried word for word in `recommends` by F6, footnote 13 (vocabulary.py:140-143) |
| x35 | KEPT | not on main; `recommends` (vocabulary.py:132) |
| x36 | KEPT | not on main; `misuse` (vocabulary.py:84) |
| x37 | KEPT | not on main; `ml_rd_and_misalignment` (vocabulary.py:90) |
| x38 | KEPT | not on main; `ml_rd_and_misalignment` (vocabulary.py:90) |
| x39 | KEPT | PARTIAL-COVER:F7. F7 quotes the 2.1.2 sentence ("proposed external deployment"); the 3.1.2 sentence is not on main; `governance_found_…` (vocabulary.py:282) |
| x40 | KEPT | PARTIAL-COVER:F2. F2 carries sentence 1; sentences 2-3 are not on main; `residual_assessed` (vocabulary.py:383) |
| x41 | KEPT | not on main; `periodic_assessed` (vocabulary.py:411) |
| x42 | KEPT | not on main; `periodic_covers_internal` (vocabulary.py:418) |
| x43 | KEPT | not on main; `safety_case` (vocabulary.py:396) |
| x44 | KEPT | PARTIAL-COVER:F4. Sentence 1 is on main; sentences 2-3 are not; `safety_case` (vocabulary.py:396) |
| x45 | KEPT | PARTIAL-COVER:F3. F3 carried sentence 1; F3's quote now goes on with sentences 2-3 in one run, before the step-2 quotes (`governance_found_…`, vocabulary.py:282-293; review F1) |
| x46 | KEPT | not on main; `material_safety_case_update` (vocabulary.py:236) |

All kept carriers pass three checks: the term is in the quote; the carrier is used by at least one of the row's
blocks (the block named in the test's `ROWS`); and no quote stops mid-sentence. The test checks the boundaries
against the source line. No row was added; the P2 rows x6 and x32 were not taken.

## 1. Deliverables

| # | Deliverable | Status / commit |
|---|---|---|
| 0 | Verify every candidate first | section 0 (done before the first edit; /tmp/dsf/bin/verify.py, spans.py) |
| 1 | Carry each KEPT definition word for word in a shown legend of a predicate the rule uses | done, 3b99540a22. The passages are appended in the source's own bytes (curly quotes kept, footnote marks kept and named), as literal strings at each key. They are shown (environment.d1.json) and counted (`legend_raw` + `_omit_legend_segments`) |
| 2 | Regenerate derived files with the project's tools only | done, 3b99540a22 and the results.json commit (section 4) |
| 3 | Condition test in a new file | done: `tests/test_defs_repair_safety_framework_1119.py` (1ce7a22a9e, 90395d9675; review fix f087a6422f, 25b26fe75c) |
| R | Review of 610eafced7: F1 (x1, x45 split), F2 (x31 not counted) | done: legends 3d0a894d06, test f087a6422f and 25b26fe75c, results.json bfae0fafb0 |

No sealed artefact was rewritten. The carriers are vocabulary.py and environment.d1.json, neither of which is in a
frozen run directory. No theorem statement or rule formula changed. No VE text changed: rules.d1.ve and facts.d1.ve
are untouched.

## 2. The condition test (`tests/test_defs_repair_safety_framework_1119.py`)

The test stores each of the 44 rows' whole quote, in the source's bytes, with its line and section (`ROWS`, one quote
per row; `DROPPED` names x33, x34). The quotes equal the audit TSV's `quote` column byte for byte.
- `test_each_definition_is_carried_whole_in_its_legend[xN]` (all 44 rows): the whole quote stands unbroken in the
  committed legend and in `vocabulary.environment()` (`omit_norm`), and in the counter's counted meaning text. The
  quote's counted form comes from the counter's own `_omit_legend_segments`, so the citation cut is the counter's.
- `test_a_split_quote_or_a_kept_escape_is_not_carried`: the two review shapes, planted in a tmp copy of
  vocabulary.py (x1 split as at 610eafced7; x31's `\"`), are not carried, while each part of the split quote is.
- `test_each_carrier_is_a_predicate_its_rule_uses[xN]`: `used_predicates` of the named block includes the carrier.
- `test_each_stored_quote_is_the_audit_rows_whole_quote`: every P1 row is in `ROWS` and its quote's sha256 equals
  that of the audit's quote (review note C1: a quote cut at a sentence end fails here).
- `test_each_stored_quote_is_in_the_pinned_source_at_its_line[xN]`: runs when the text is stored at its pin. The
  quote occurs once, on its line, starts at a sentence, list or footnote start and ends at a full stop or footnote
  mark. When the text is absent, it checks only the quote's end and never skips (the F3 pattern).
- `test_no_quoted_passage_holds_an_escape_the_counter_keeps[<use case>]` (every `usecases/*/*vocabulary.py`, read with
  `tokenize`): no escaped quote opens inside an open quoted passage and no other escape sits inside one: the class of
  review F2. `test_the_escape_guard_finds_the_x31_shape` shows it flags 610eafced7's literal.

Runs (logs under /tmp):
- HEAD: `138 passed` (fsf1119_t4.log, with tests/test_history_tests.py: 165 passed).
- main's vocabulary.py and environment.d1.json swapped in: `44 failed, 94 passed`: the 42 kept rows, the planted-shape
  test and the FSF escape guard (fsf1119_swap2_941208a12d.log). x33, x34 pass: carried on main.
- 610eafced7's swapped in: `5 failed`: x1, x31, x45, the planted-shape test and the FSF guard
  (fsf1119_swap2_610eafced7.log).
- Earlier runs of the first version (127 passed; main 41 failed) are superseded.

## 3. Answers touched (rows' answers_touched, "k of 262 keyed", from the audit TSV)

x1 42, x2 1, x3 140, x4 140, x5 148, x7 243, x8 243, x9 132, x10 132, x11 8, x12 8, x13 187, x14 1, x15 0, x16 1,
x17 42, x18 1, x19 12, x20 41, x21 41, x22 40, x23 8, x24 12, x25 98, x26 42, x27 12, x28 62, x29 62, x30 62,
x31 22, x35 22, x36 155, x37 163, x38 163, x39 46, x40 8, x41 8, x42 8, x43 8, x44 8, x45 87, x46 1.

The `critical` legend (x7, x8) is shown with the FACTS unit, so the change reaches up to 243 of 262 keyed answers.
Every FSF read after this merge re-pins at the merge commit.

## 4. Commands and regenerated files

- `uv run python usecases/safety-framework/vocabulary.py` wrote environment.d1.json: 28 descriptions; description
  bytes 16,360 to 30,924 (+14,564).
- `uv run python usecases/safety-framework/build_document.py` wrote coverage.json (1 line). It reads the default
  pinned path.
- `uv run python docs/en-e3-norm/en-2b/route_fixtures.py --write` wrote tests/data/route-cases.jsonl (1 line).
- `uv run python conformance/english_lean_lexicon.py` wrote lexicon-report.json (1 line; `"valid": 43, "invalid": 0`).
- `uv run python -m conformance.english_lean_seal` wrote corpus-seal.json: the FSF environment's sha256 and the
  seal id. `--check` then printed `0 difference(s)`; before the write it printed `1 difference(s)`, this file only.
- `uv run python usecases/safety-framework/run.py` wrote results.json. It was needed:
  `test_safety_framework.py::test_rerun_equals_committed_results` failed in the selected run. results.json was not
  opened. A script printed only the JSON paths that differ from main's copy, with no values: `2 changed paths:
  ['/items/N1/goals/cyber/certificate_sha256', '/items/N1/goals/harmful_manipulation/certificate_sha256']`. The
  failed test then passed (`1 passed in 711.13s`, t-rerun.log).
- `uv run python tools/regen_generated.py --check`:
  - First run, before the checker binaries existed in this worktree: `failed: route-cases, checker-pins`
    (`the Rust release binary is missing or not pinned`).
  - At HEAD 90395d9675: exit 0 (/tmp/dsf/regen-check2.log). Its only remark is the advisory `WARN: codemap is
    stale (regenerated on merge)`. docs/codemap is outside this row's paths and is left to the merge.

Files: usecases/safety-framework/{vocabulary.py, environment.d1.json, coverage.json, results.json},
tests/data/route-cases.jsonl, conformance/english-lean/{lexicon-report.json, corpus-seal.json},
tests/test_defs_repair_safety_framework_1119.py, and this directory. All are within the row's path list, except the
generated route-cases.jsonl and lexicon-report.json, which every FSF repair regenerates (R12).

## 5. Seeded bugs (Python: vocabulary.py, environment.d1.json; each restored with `git checkout`, tree clean after)

| # | Behaviour | Mutation | Failing test |
|---|---|---|---|
| 1 | passage carried word for word | vocabulary.py `concerns`: "radiological, " deleted from the Risk Domains quote | `test_each_kept_definition_is_carried_word_for_word_in_its_legend[x3]` (seed1.log) |
| 2 | carried text is counted, not only shown | vocabulary.py `periodic_assessed`: the RRA passage moved to a module constant used by an f-string. The shown legend stays identical (checked `True`) | `…_in_its_legend[x41]`, at the `_counted` assert (seed2.log) |
| 3 | carrier is used by the row's rule | vocabulary.py + regenerated environment.d1.json: `subsequent` verbalisation "{0} is subsequent" changed to "{0} is a later release" | `test_each_carrier_is_a_predicate_its_rule_uses[x2]` (seed3.log) |
| 4 | dropped rows stay carried | vocabulary.py `recommends`: "non-state external actors" changed to "non-state actors" in F6's SL2+ sentence | `test_the_dropped_rows_are_already_carried` (seed4.log) |
| 5 | passage whole and adjacent in the source (test side) | x27's two pieces swapped in `ROWS`; each is still on line 19 | `test_each_stored_passage_is_in_the_pinned_source_at_its_line[x27]` (seed5.log; seed5b.log on the code of 90395d9675; the pieces are one quote since the F1 fix) |
| 6 | whole quote, unbroken (review F1) | 610eafced7's vocabulary.py and environment.d1.json (x1, x45 split) | `…_carried_whole_in_its_legend[x1]`, `[x45]` (fsf1119_swap2_610eafced7.log) |
| 7 | counted, not only shown (review F2) | same swap (x31's `\"`); and vocabulary.py footnote 12 written `\\u0031\\u0032` (shown the same) | `[x31]`; `[x33]` and `test_no_quoted_passage_holds_an_escape_the_counter_keeps[safety-framework]` (fsf1119_seed_x33.log) |
| 8 | the stored quote is the audit's whole quote (note C1) | test's `RISK_DOMAINS` cut after its first sentence-ending "AI risks." | `test_each_stored_quote_is_the_audit_rows_whole_quote` only; `[x3]` carried/source tests pass (fsf1119_seed_c1.log) |

Seeds 1-5 ran on the first version of the test: since the review fix, seed 1's and 2's test is
`test_each_definition_is_carried_whole_in_its_legend`, and seed 4's check (`test_the_dropped_rows_are_already_carried`,
shown side only) is folded into it for x33, x34 (seed 7). Seeds 6-8 ran on the review fix.

Lean and Rust: not changed, so no seed there.

## 6. Trust, mutants, size

- `uv run python tools/trust_map.py --check`: `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`, PASS.
- Light lane: `NOT 636 changed lines outside generated files > 150 (8 files)`. Its count includes the regenerated
  data files. `uv run python tools/trust_mutants.py --plan` gave `"definitions": 0, "mutants": 0, "to_run": 0`, so
  a sweep has nothing to mutate (no Lean change). No R16 row, no mutants.json, no FOLLOW-UPS.md row.
- SIZE: 230 product (vocabulary.py legend text, 202 added / 28 changed), 341 tests, 256 other hand-written lines
  (this REPORT and DELTA.md). Generated: environment.d1.json 56, results.json 4, coverage.json 2,
  route-cases.jsonl 2, lexicon-report.json 2, corpus-seal.json 4.
- Pilot bytes the item is expected to move (an estimate; nothing is claimed before a pilot audit):
  - +14,564 B of legend text in environment.d1.json.
  - The largest unit's legend block grows from 4,632 to 9,424 B (FACTS; f10-acc from 4,429 to 8,867 B).
  - The prompt lower bound stays far under ARG_LIMIT 131,000: `tools/defs_carried.py` reports a maximum of 66,999 B.

## 7. Overlaps and order

- `git diff --name-only main...<branch>` over the in-flight branches: `infra/srccov-safety-framework-1119` edits
  vocabulary.py (`critical`, `misuse`, `ml_rd_and_misalignment`, `recommends`, `external`, `assessed`, ...) and
  environment.d1.json. It appends some of the same source sentences (footnotes 2, 8, the 3.2.2 ML R&D CCL sentence,
  the 2.2 recommendation sentence, part of the External Deployments entry).
  - If that branch merges first, this branch rebases. A sentence it has already carried word for word is not
    appended twice, and the generated files are regenerated.
  - If this branch merges first, that branch can drop its duplicates.
- The FSF repair rows F1, F2, F3, F6, F7 and F8 are merged on main (the COVER condition holds).
- Other branches touch only generated files: corpus-seal.json, lexicon-report.json and route-cases.jsonl (R12).

## 8. Not run

- The full gate: the chain runs it on the final HEAD.
- lake build and rust_build: no Lean or Rust change.
- Selected run: `mac-pytest.sh --select` on tree 2cf929cef9 recorded 387 units on ve-cloud-2 (4630 s), `1 failed`
  (select.log). The only failure was `test_rerun_equals_committed_results`; results.json was regenerated and the test
  passed on rerun.
- Later commits change only results.json and the new test file. Their tests were rerun: the new file (127 passed)
  and the failed id (passed).
- Review fix: `mac-pytest.sh --select` on bfae0fafb0 (GitHub Actions, 5 shards, 1743 s; fsf1119_select.log): one
  failure, `test_history_tests.py` (the new test imported `tools/defs_carried.py`, which starts git). Fixed in
  25b26fe75c (the counter's own reader instead); that file and the new test file then gave `165 passed`.

## Notes for the DRI

- **Literal copies, not one constant.** Shared passages (deployment mitigations on 5 keys, CCA on 3, RRA on 3, MCCA
  and safety cases on 2) are written as literal strings at each key, not as one module constant. The definitions
  counter reads only the literal strings of a key's entry (`legend_raw` / `_omit_legend_segments`), so a
  constant-built legend would be shown but not counted (METHOD-READDOCS §0: PARTIAL-ELSEWHERE). The text is source
  quotation, not logic. The test pins every copy to the one stored source passage, so the copies cannot drift.
- **x31 is now carried (review F2).** The drop reason "already carried word for word" held only on the shown side:
  F6 wrote the inner quotes as escaped `\"`, which the counter keeps. They are now “ ” (shown the same after
  `omit_norm`); x31 is KEPT. `recommends` is this row's carrier for x28-x31 and x35, inside the row's paths.
- **F2 and F3 tests.** Their legends' quotes now go on past the sentence they pin (F1), so their checks accept the
  quote closing after the sentence or going on with the source's next sentence (F2 reads it from the source; F3 pins
  it and checks it against the source). The F2 test's prefix moves out of the parenthesis: "Section 1.3" in the
  continued quote would make the parenthesis a citation the counter cuts.
- **Seal handling.**
  - I opened no FSF read output, answers/, reports/ or readings/.
  - results.json was compared by JSON path only, with no values printed.
  - `build_document.py` printed a byte-count summary to stdout; its last 3 lines showed once in my terminal (`"OPEN":
    8135`). coverage.json itself was not opened.
- **Line numbers.** The audit TSV cites `fsf-3.1.txt:<line>`; every quote is on that line. x35's "repeated L14-15"
  is not a byte-identical repeat: the exact quote occurs once, on line 11.

## Spec re-read

- Deliverable 1 ("full span as the row's quote gives it"): every kept row's quote, checked against
  rows-safety-framework-x.tsv column `quote`, now stored whole per row and pinned by sha256. For the PARTIAL-COVER
  rows x1 and x45, the part already on main and the part added here stand in one unbroken quote (review F1).
- Deliverable 3 ("stored in the test with their source location ... never downloads"): `ROWS[*].line/location`;
  `pinned_source(skip=False)`.
- COVER: "drop a row now carried word for word": x33, x34, checked shown and counted by the condition test (x31
  failed the counted side and is kept, review F2).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed answer or schema changes.
2. Every deliverable built: PASS. Section 1; the test ids are in section 2. Rule-break grep: no Python copy of a Lean
   decision, no report test, overlap reported (section 7).
3. Tests can fail: PASS. Seeds 1-8 (section 5); main swap gives 44 failed, 610eafced7 swap 5 failed (section 2).
4. Py/Lean/Rust agree: N.A. No checker path changed. `results.json` paths changed: 2, certificate hashes only.
5. R8 binding: N.A. No relayed field.
6. Gate evidence on the final HEAD: N.A. here; the chain runs the gate on the final HEAD. Main has not moved
   (`git log HEAD..main` is empty).
7. No unsigned item: PASS. DELTA.md has no rows; trust +0 (`trust_map.py --check`).
8. Every user-visible change in DELTA: PASS. No VE output changes; the results.json path diff is in section 4.
9. Selection finds the tests: PASS. The selected run listed `tests/test_defs_repair_safety_framework_1119.py` and
   the seven F-row tests (select.log:81, 316-322) and caught `test_rerun_equals_committed_results`.
10. Lean statements: N.A. No Lean change.
11. Budgets and limits: N.A. No evaluator or limit. The test has no timing, sleep or deadline.
12. CPU and memory: N.A. Legend text only. The prompt bound stays under ARG_LIMIT (section 6).
13. Test-removed trailers: N.A. No test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS.
    - The carriers pass at HEAD and fail on main.
    - The whole quote is checked unbroken, shown and counted; split and escaped shapes fail (seeds 6, 7).
    - The counted check refuses a shown-only legend (seed 2).
    - Each claim above names its command and log. Spec re-read is the section above.
15. Overclaim, silent cut, every check can fail, limits: PASS.
    - "unchanged" verdicts: the path diff.
    - "all 44 quotes": spans.py output (`exact 1` for each).
    - No deliverable was cut.
    - Each new test function has a seed (1-5).
    - Limits: N.A.
