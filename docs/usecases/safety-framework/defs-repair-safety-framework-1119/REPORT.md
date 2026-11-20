# defs-repair-safety-framework-1119 REPORT

**Summary.** Status: built; ready for the chain gate. No DRI signature is needed.
- Base: VE main 941208a12d. The change merges at the train's merge of this branch's HEAD; later reads re-pin there.
- 41 of the 44 P1 rows are KEPT and carried word for word in 28 legends of `usecases/safety-framework/vocabulary.py`.
  3 rows are DROPPED (x31, x33, x34), because fsf-repair-f6-sl2plus-1119 already carries them word for word.
- Condition test: `tests/test_defs_repair_safety_framework_1119.py`. It fails on main (41 failed) and passes at HEAD
  (127 passed).
- Open: none in scope. Overlap: `infra/srccov-safety-framework-1119` edits the same legends; whichever merges second
  rebases (section 7).

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
| x1 | KEPT | PARTIAL-COVER:F2. F2 carries the Glossary entry's sentence 2 without its full stop; sentences 3-4 are carried now (`frontier`, vocabulary.py:207) |
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
| x31 | DROPPED | already carried word for word in `recommends` by F6 (vocabulary.py:133-136) |
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
| x45 | KEPT | PARTIAL-COVER:F3. F3 carries sentence 1; sentences 2-3 are carried now (`governance_found_…`, vocabulary.py:282) |
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
| 3 | Condition test in a new file | done: `tests/test_defs_repair_safety_framework_1119.py` (1ce7a22a9e, 90395d9675) |

No sealed artefact was rewritten. The carriers are vocabulary.py and environment.d1.json, neither of which is in a
frozen run directory. No theorem statement or rule formula changed. No VE text changed: rules.d1.ve and facts.d1.ve
are untouched.

## 2. The condition test (`tests/test_defs_repair_safety_framework_1119.py`)

The test stores each passage, in the source's bytes, with its line and section (`ROWS`; `DROPPED` for x31/x33/x34).
- `test_each_kept_definition_is_carried_word_for_word_in_its_legend[xN]`: each piece is in the committed legend, in
  `vocabulary.environment()` and in the counter's counted meaning text (`omit_norm`).
- `test_each_carrier_is_a_predicate_its_rule_uses[xN]`: `used_predicates` of the named block includes the carrier.
- `test_the_dropped_rows_are_already_carried`: guards the drop reason.
- `test_each_stored_passage_is_in_the_pinned_source_at_its_line[xN]`: runs when the text is stored at its pin. Each
  piece occurs once, on its line; the pieces are adjacent; the passage starts at a sentence, list or footnote start
  and ends at a full stop or footnote mark. When the text is absent, it checks only the stored pieces' end, and it
  never skips (the F3 pattern). With `VE_REQUIRE_PINNED_SOURCES=1`, `pinned_source` fails instead.

Runs (logs under /tmp/dsf):
- HEAD: `uv run pytest -q tests/test_defs_repair_safety_framework_1119.py` gave `127 passed` (t2.log).
- With `HOME=/tmp/dsf/nohome` (no stored source), `-k pinned_source` gave `44 passed` (t2-nohome.log).
- main's vocabulary.py and environment.d1.json swapped in: `41 failed, 86 passed`. The 41 are exactly the kept rows'
  condition test (t-main.log).

## 3. Answers touched (rows' answers_touched, "k of 262 keyed", from the audit TSV)

x1 42, x2 1, x3 140, x4 140, x5 148, x7 243, x8 243, x9 132, x10 132, x11 8, x12 8, x13 187, x14 1, x15 0, x16 1,
x17 42, x18 1, x19 12, x20 41, x21 41, x22 40, x23 8, x24 12, x25 98, x26 42, x27 12, x28 62, x29 62, x30 62,
x35 22, x36 155, x37 163, x38 163, x39 46, x40 8, x41 8, x42 8, x43 8, x44 8, x45 87, x46 1.

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
- `uv run python tools/regen_generated.py --check`: every entry passed except `route-cases` (lean/VE/Route/examples)
  and `checker-pins`. Both need the Rust release binary, which this worktree has not built (`checker-pins: the Rust
  release binary is missing or not pinned`). Neither reads FSF files. The chain gate builds the binaries.

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
| 5 | passage whole and adjacent in the source (test side) | x27's two pieces swapped in `ROWS`; each is still on line 19 | `test_each_stored_passage_is_in_the_pinned_source_at_its_line[x27]` (seed5.log; seed5b.log on the code of 90395d9675) |

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
- The two binary-dependent regen checks (section 4).
- Selected run: `mac-pytest.sh --select` on tree 2cf929cef9 recorded 387 units on ve-cloud-2 (4630 s), `1 failed`
  (select.log). The only failure was `test_rerun_equals_committed_results`; results.json was regenerated and the test
  passed on rerun.
- Later commits change only results.json and the new test file. Their tests were rerun: the new file (127 passed)
  and the failed id (passed).

## Notes for the DRI

- **Literal copies, not one constant.** Shared passages (deployment mitigations on 5 keys, CCA on 3, RRA on 3, MCCA
  and safety cases on 2) are written as literal strings at each key, not as one module constant. The definitions
  counter reads only the literal strings of a key's entry (`legend_raw` / `_omit_legend_segments`), so a
  constant-built legend would be shown but not counted (METHOD-READDOCS §0: PARTIAL-ELSEWHERE). The text is source
  quotation, not logic. The test pins every copy to the one stored source passage, so the copies cannot drift.
- **x31 is shown but not counted.** It is shown word for word, but the counter's literal reading misses it: F6
  wrote the inner quotes as escaped `\"`, and the counter cuts "(SL2)". Making it counted means rewriting F6's
  carrier, which is outside this row. It stays DROPPED under the task's criterion ("already carried word for word").
- **Seal handling.**
  - I opened no FSF read output, answers/, reports/ or readings/.
  - results.json was compared by JSON path only, with no values printed.
  - `build_document.py` printed a byte-count summary to stdout; its last 3 lines showed once in my terminal (`"OPEN":
    8135`). coverage.json itself was not opened.
- **Line numbers.** The audit TSV cites `fsf-3.1.txt:<line>`; every quote is on that line. x35's "repeated L14-15"
  is not a byte-identical repeat: the exact quote occurs once, on line 11.

## Spec re-read

- Deliverable 1 ("full span as the row's quote gives it"): every kept row's quote, checked against
  rows-safety-framework-x.tsv column `quote`. For the PARTIAL-COVER rows x1 and x45, the part already on main and the
  part added here together form the row's whole quote: the source test checks that the pieces are adjacent.
- Deliverable 3 ("stored in the test with their source location ... never downloads"): `ROWS[*].line/location`;
  `pinned_source(skip=False)`.
- COVER: "drop a row now carried word for word": x31, x33, x34, checked by `test_the_dropped_rows_are_already_carried`.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed answer or schema changes.
2. Every deliverable built: PASS. Section 1; the test ids are in section 2. Rule-break grep: no Python copy of a Lean
   decision, no report test, overlap reported (section 7).
3. Tests can fail: PASS. Seeds 1-5 (section 5); main swap gives 41 failed (t-main.log).
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
    - The source check accepts adjacent pieces and refuses swapped ones (seed 5).
    - The counted check refuses a shown-only legend (seed 2).
    - Each claim above names its command and log. Spec re-read is the section above.
15. Overclaim, silent cut, every check can fail, limits: PASS.
    - "unchanged" verdicts: the path diff.
    - "all 44 quotes": spans.py output (`exact 1` for each).
    - No deliverable was cut.
    - Each new test function has a seed (1-5).
    - Limits: N.A.
