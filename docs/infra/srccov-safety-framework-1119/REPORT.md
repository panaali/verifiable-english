# srccov-safety-framework-1119: REPORT

DRI signature needed: none. DELTA.md has no row and reserves no signature. Trust changes by +0: no Lean, Rust, `ve/`
or `tools/` file changed, and `tools/trust_mutants.py` plans 0 definitions.

- **Status:** 14 of the 33 candidate rows are KEPT (23 of their 70 units) and 19 are DROPPED. Each kept unit is now
  quoted word for word in the legend of a predicate that a rule or fact block uses, the legend a reader is shown with
  that block. All kept carries are one kind: a legend append. No out-of-scope record was written.
- **Merges at:** VE main `941208a12d` (the branch is rebased onto it). The six dependencies were merged first:
  fsf-repair-f1/f2/f3/f6/f7/f8-1119 (`git log main --oneline | grep fsf-repair`: 727d1d2103, 09bea0972d, ef7ecd59ac,
  44754d9bf9, 17b65fff3b, c0693260f7). I dropped the units they already carry (table below).
- **Inputs read:** manage-agents `reviews/source-coverage-1119/` METHOD.md (with amendments 1-17), CHALLENGE.md,
  challenge2/RESULT.md, SUMMARY.md (FSF spot check), safety-framework.md, rows-safety-framework.tsv and
  units-safety-framework.tsv. From VE: `usecases/safety-framework/` vocabulary.py, environment.d1.json, rules.d1.ve,
  facts.d1.ve and spans.json. From spans.json I read only the fields `id/kind/span/status/reason/untranslated/
  restates/rule/open_terms`, and whether `waits` is set. Also read: build_document.py `main`, `tests/omission_rule.py`
  (the repo's port of the counter) and the pinned `fsf-3.1.txt`. I opened no readings/, answers/, reports/,
  counted-read, sealed or diagnostic file.

## 0. Verify table

Line numbers are `usecases/safety-framework/vocabulary.py` at HEAD unless another file is named. Three rules decide
whether a carrier is shown, and so whether it can carry a unit:

- **Shown.** The counter shows a block with its rule/fact lines and with the legends of the predicates that block uses
  (`tests/omission_rule.py:66` `used_predicates`, `:176-185` `carrier`). The legends of constants and sorts are not
  shown. fsf-repair-f1 made the same finding (`docs/usecases/safety-framework/fsf-repair-f1-leveldefs-1119/REPORT.md:22-24`),
  and the task bars "bare constant tables" as carriers.
- **Open terms carry nothing.** Under METHOD amendment 4, as the merge spot check applied it (SUMMARY.md lines 21-23,
  S0229/S0274), the legend of an open-term predicate does not carry a unit.
- **Lead-ins.** Under amendment 8(b), a lead-in unit takes the lowest class of its items.

| row id | KEPT / DROPPED | units kept | reason |
|---|---|---|---|
| srccov-safety-framework-s10-1-1119 | DROPPED | none | The carrier `constants.cbrn` is an entry in the DOMAINS constant table (:399-404). A constant legend is not shown with a block. |
| srccov-safety-framework-s10-2-1119 | DROPPED | none | As row 1: `constants.cyber` (:399-404). |
| srccov-safety-framework-s10-3-1119 | DROPPED | none | As row 1: `constants.harmful_manipulation` (:399-404). |
| srccov-safety-framework-s10-4-1119 | DROPPED | none | As row 1: `constants.ml_rd_and_misalignment_domain` (:399-404). |
| srccov-safety-framework-s10-5-1119 | KEPT (2 of 3) | S0022, S0159 | Carried in the `misuse` legend (:65-69), which 11 blocks use. S0034 is dropped: it is the lead-in to S0035-S0037, which have no shown carrier (rows 1-3 are dropped), so under amendment 8(b) carrying S0034 alone would not carry it. |
| srccov-safety-framework-s10-6-1119 | DROPPED | none | S0155 is already carried at main: f1's `defined` legend (:77-99) quotes the definition. The row's carrier is also a constant (LEVELS :390-398). |
| srccov-safety-framework-s10-7-1119 | DROPPED | none | As row 6: S0158 (`defined` legend :77-99). |
| srccov-safety-framework-s10-8-1119 | DROPPED | none | As row 6: S0161. |
| srccov-safety-framework-s10-9-1119 | DROPPED | none | As row 6: S0167. |
| srccov-safety-framework-s10-10-1119 | DROPPED | none | As row 6: S0198. |
| srccov-safety-framework-s10-11-1119 | DROPPED | none | As row 6: S0206. |
| srccov-safety-framework-s10-12-1119 | DROPPED | none | S0212 is carried at main (`defined` :77-99). The carrier of S0215 is the constant `ml_rd_automation_level_1` (:397), which is not shown with a block. |
| srccov-safety-framework-s10-13-1119 | KEPT | S0203 | Carried in the `ml_rd_and_misalignment` legend (:70-72), which 16 blocks use (`classified as`). |
| srccov-safety-framework-s10-14-1119 | KEPT | S0009, S0249 | Carried in the `critical` legend (:53-59), which 16 blocks use. |
| srccov-safety-framework-s10-15-1119 | DROPPED | none | `approaches` is open term OT1 (:123, `OPEN_PREDICATES` :217). Amendment 4 applies. |
| srccov-safety-framework-s10-16-1119 | KEPT (4 of 5) | S0012, S0060, S0259, S0260 | Carried in the `assessed` legend (:239-254), which blocks f2 and f3 use. S0258 is already carried at main by f2 (:241). |
| srccov-safety-framework-s10-17-1119 | KEPT | S0056, S0261, S0262 | Carried in the `change_assessed` legend (:263-275), which block f5 uses. |
| srccov-safety-framework-s10-18-1119 | DROPPED | none | `reached` is open term OT1 (:121). Amendment 4 applies. |
| srccov-safety-framework-s10-19-1119 | DROPPED | none | `could_undermine_justification` is open term OT10 (:154). Amendment 4 applies. |
| srccov-safety-framework-s10-20-1119 | KEPT | S0044 | Carried in the `proximity_assessed` legend (:276-283), which blocks f6 and f6-tcl use. |
| srccov-safety-framework-s10-21-1119 | DROPPED | none | S0091 is already carried at main, whole, in the `acceptable` legend (:339-345). |
| srccov-safety-framework-s10-22-1119 | DROPPED | none | `mitigates` is open term OT2 (:160). Amendment 4 applies. S0139 stands at main in the `governance_found_acceptable...` legend, which is OT3. |
| srccov-safety-framework-s10-23-1119 | DROPPED | none | `security_assessed_adequate` is open term OT4 (:181). Amendment 4 applies. |
| srccov-safety-framework-s10-24-1119 | KEPT (3 of 4) | S0078, S0105, S0276 | Carried in the `secured` legend (:319-332), which blocks f9-sec and f10-sec use. S0275 is already carried at main by f2 (:322). |
| srccov-safety-framework-s10-25-1119 | KEPT | S0103 | Carried in the `holistic` legend (:367-374), which blocks f20-holistic-strict and f20-holistic-default use. |
| srccov-safety-framework-s10-26-1119 | KEPT | S0149 | Carried in the `recommends` legend (:100-115), which 9 blocks use. |
| srccov-safety-framework-s10-27-1119 | KEPT | S0201 | Carried in the `periodic_covers_internal` legend (:302-307), which block f17-hri uses. |
| srccov-safety-framework-s10-28-1119 | DROPPED | none | `frontier` is open term OT9 (:145). Both units already stand in its legend at main (f2, :146-147). |
| srccov-safety-framework-s10-29-1119 | DROPPED | none | `sorts.proposal` (:29) is a sort legend, which is not shown with a block. |
| srccov-safety-framework-s10-30-1119 | KEPT | S0271 | Carried in the `external` legend (:138-140), which 13 blocks use. |
| srccov-safety-framework-s10-31-1119 | KEPT (1 of 2) | S0281 | Carried in the `residual_assessed` legend (:284-291), which block f7-rra uses. S0280 is already carried at main by f2 in the same legend. |
| srccov-safety-framework-s10-32-1119 | KEPT | S0284 | Carried in the `safety_case` legend (:292-298), which block f7-sc uses. |
| srccov-safety-framework-s10-33-1119 | KEPT (1 of 2) | S0020 | Carried in the `yearly_review` legend (:355-359), which block f18-yearly uses. S0224 is already carried at main by f8 (`REVIEW_PROCESS` :221, in the same legend). |

Every kept row needs no new rule or fact line, no language feature, no theorem or formula change, no trust and no
DELTA row. Two kept units have spans.json records that name a gap: S0020 (`ov-review-periodically`, UNFORMALISED,
reason `no_deadline_or_trigger`) and S0159 (`fn8`, UNFORMALISED, `degree_term`). Neither has `waits` set. The legend
quotes their words. It does not formalise them, so I left both records as they are. Under METHOD section 2, class 1
(CARRIED-VERBATIM) is decided before records are considered.

## 1. Rows carried

Each quote is the source sentence, after `safetyfw_accounting.norm`, written inline in `vocabulary.py`. Every quote
sits outside any parenthesised citation, because the counter cuts those. No quote is held in a variable, because the
counter's `legend_raw` reads the raw lines. A section heading, Glossary label, footnote mark, list bullet or the
page-18 running head stays outside the quote. `environment.d1.json` was rewritten by `python
usecases/safety-framework/vocabulary.py`.

| predicate | units | cited as |
|---|---|---|
| misuse | S0022, S0159 | footnote 2; footnote 8 |
| ml_rd_and_misalignment | S0203 | Section 3.2.2 |
| critical | S0009, S0249 | Overview; Glossary, Critical Capability Levels (CCLs) |
| assessed | S0012, S0060, S0259+S0260 | Overview; Section 1.3.2; Glossary, Early Warning Evaluations (one passage) |
| change_assessed | S0056, S0261+S0262 | Section 1.3.2; Glossary, Material Capability Change Assessments (one passage) |
| proximity_assessed | S0044 | Section 1.2, for TCLs |
| secured | S0276, S0078, S0105 | Glossary, Security Mitigations; Section 1.3.3; Section 2.1 |
| holistic | S0103 | "The Note in full", after the existing `(1.3.5 Note ...)` paraphrase, which F20's test pins |
| recommends | S0149 | Section 2.2 |
| periodic_covers_internal | S0201 | Section 3.2.1 |
| external | S0271 | Glossary, External Deployments |
| residual_assessed | S0281 | Glossary, Residual Risk Assessments |
| safety_case | S0284 | Glossary, Safety Cases |
| yearly_review | S0020 | Overview, placed before the closing `(5.1: "...")` that f8's test reads as the last parenthesis |

## 2. Derived files (each from its own writer)

| file | writer | change |
|---|---|---|
| usecases/safety-framework/environment.d1.json | `python usecases/safety-framework/vocabulary.py` | 14 descriptions; sha256 e5a580e5… → 42865a83… |
| usecases/safety-framework/coverage.json | `build_document.py --source /tmp/sf1119/src/fsf-3.1.txt` (a copy of the pinned text) | `document_sha256` only; spans.json unchanged |
| usecases/safety-framework/results.json | `run.py` | 2 `certificate_sha256`; no verdict moves (`run.py --check` exit 0 afterwards) |
| conformance/english-lean/lexicon-report.json | `conformance/english_lean_lexicon.py` | `lexicon_id` |
| tests/data/route-cases.jsonl | `docs/en-e3-norm/en-2b/route_fixtures.py --write` | the `stale` fixture's environment |

These are not regenerated, by design:
- `tests/data/fidmech/wording-golden.json`, `wording-inputs/` and `fp1-inputs/safety-framework/` are frozen golden
  inputs. They already differed from main's vocabulary.py before this item (`diff -q`), and f1, f2 and f8 left them
  unchanged.
- `tools/fidmech/manifests.py` pins the sha256 of the four manage-agents input files only, not environment.d1.json
  (`manifests.py:31-36`).

`regen_generated.py --list` has no entry for these files.

## 3. Condition test

`tests/test_srccov_safety_framework_1119.py` is a new file with 44 tests:

- **`test_the_legend_quotes_the_pinned_source_sentence`** (21 passages). It reads each unit from the pinned text at
  its UTF-8 byte span through `tests/pinned_source.py`, normalises it, cuts the named heading or label (which must
  stand there) and the running head, and checks the last words. The sentence must then stand in quotes in the
  committed legend.
- **`test_the_carrier_is_a_legend_a_reader_is_shown`** (21 passages; needs no source). It checks four things:
  - a block uses the predicate (`used_predicates`);
  - the predicate is not in `OPEN_PREDICATES` and its legend has no "Open term";
  - the quote is not inside an open parenthesis;
  - the counter's `legend_raw` holds the quote's last words.
- Two more tests check the passage partition and the cut strings.

Results:
- **Before the change:** main's `environment.d1.json` and `vocabulary.py` give 42 failed, 2 passed. The two that pass
  do not depend on any carry. Run: `git show d5f402140f:<file> > <file>`, then pytest, then `git checkout HEAD`.
- **After the change:** 44 passed.

## 4. Seeded bugs (Python: the only changed language; all in `usecases/safety-framework/vocabulary.py`)

Each bug was planted with `/tmp/sf1119/seed.py <name>`. I then regenerated `environment.d1.json`, ran
`pytest tests/test_srccov_safety_framework_1119.py` and restored the files with `git checkout HEAD --
usecases/safety-framework/`. `git status` was clean afterwards.

| bug | behaviour claimed | result |
|---|---|---|
| B1: remove the carried S0284 sentence from `safety_case` | each kept unit is carried (the carry kind: legend append) | 2 failed: `test_the_legend_quotes_the_pinned_source_sentence[S0284]`, `test_the_carrier_is_a_legend_a_reader_is_shown[S0284]` |
| B2: "periodically" → "regularly" in S0020 | the quote is word for word | 1 failed: `test_the_legend_quotes_the_pinned_source_sentence[S0020]` |
| B3: open the S0149 quote inside "(2.2: …" | the quote is outside any parenthesised citation | 1 failed: `test_the_carrier_is_a_legend_a_reader_is_shown[S0149]` |
| B4: hold S0201 in a module variable `SINCE` | the counter's raw legend read sees the words | 1 failed: `test_the_carrier_is_a_legend_a_reader_is_shown[S0201]` |

## 5. Tests run

- `pytest tests/test_safety_framework.py` plus the f2, f8, f9 and f3 test files, after the first carry: 2 failed.
  - `test_rerun_equals_committed_results` failed because `results.json` held stale certificate hashes. I regenerated
    it with run.py.
  - `test_fsf_repair_f8_disclosure_1119.py::...[5.1]` failed because the S0020 quote stood after the 5.1
    parenthesis. I moved it before.
- After both fixes, the failed ids, the new file and `test_span_accounting_is_complete`: 48 passed.
- Selected run (`mac-pytest.sh --select -- --base 941208a12d --run`, ran on ve-cloud-2): exit 0, "recorded 388 units
  for tree 6a6d8688dd; … 0 failed". It ran `tests/test_srccov_safety_framework_1119.py` first. It deferred 18 slow
  test files, selected for weak reasons, to the chain gate.
- `light-lane.py check`: NOT (264 lines over 150).
- trust_mutants sweep (`mac-pytest.sh --trustmut`): "0 definitions, 0 mutants … 0 SURVIVOR … exit=0".
- No test in `main-known-red.txt` was touched.

## 6. Answers the change touches (for re-pinning later reads)

The legend text shown with 45 of the 61 FSF blocks changes:

- **activities-:** development, internal-external, low-risk.
- **closure-:** ccl-kinds, misuse-ccls.
- **levels-:** cbrn, cyber, manipulation, ml-rd-acceleration, ml-rd-automation, stealth.
- **f-blocks:** f2, f3, f5, f6, f6-tcl, f7-rra, f7-sc, f9-acc, f9-dm, f9-rel, f9-sec, f10-acc, f10-dm-diff,
  f10-rel-diff, f10-sec, f11-acc, f11-dm, f11-rel, f11-sec, f12-p, f12-u, f13-p, f13-u, f15-diff, f16-ds,
  f16-ds-strict, f17-add, f17-hri, f17-pra, f18-yearly, f19-default, f20-holistic-default, f20-holistic-strict.
- **other:** tcl-not-ccl.

`environment.d1.json` sha256 changes from e5a580e517b9… to 42865a8360b3…. Any read pinned to the FSF environment, or
to these blocks' rendered legends, re-pins. No verdict and no keyed answer value changes: in `results.json`, only the
certificate hashes change.

## Files

The numbers are from `git diff --numstat 941208a12d HEAD`:

- `usecases/safety-framework/vocabulary.py`: +68 -16.
- `tests/test_srccov_safety_framework_1119.py`: +142.
- Generated files: environment.d1.json 14/14, results.json 2/2, coverage.json 1/1, lexicon-report.json 1/1,
  route-cases.jsonl 1/1.
- The REPORT and DELTA in this directory.

SIZE: 84 product, 142 tests, 256 other hand-written lines (this REPORT and DELTA).

## Notes for the DRI

- **Rows 1-4 and S0034 could carry in the next item.** The `concerns` predicate is used by every `levels-*` block. A
  legend of its own could carry the domain definitions S0035-S0037, S0154, S0160, S0164, S0244-S0248 together with
  the lead-in S0034, the way f1 carried level definitions in `defined`. I did not do this, because it changes the
  rows' carrier, and the conservative reading is to drop. S0215 could likewise join the `defined` legend.
- **The counter cannot see legends held in variables.** `legend_raw` reads raw vocabulary.py lines, so a legend held
  in a variable (f8's `{REVIEW_PROCESS}`, `{DISCLOSED_INFORMATION}`) shows the counter the variable name, not the
  text. The reader is shown environment.d1.json, which has the text. I wrote every new quote inline. This is a note,
  not a defect in any verdict.
- **The quote in the holistic legend is cut by the counter.** It stands inside "(1.3.5 Note …)". F20's test pins that
  shape, so I added the whole sentence after it rather than moving it.

## Spec re-read

- The carrier against METHOD amendment 4: "legends ... of a predicate, constant or sort that a rule/fact line in the
  same read file uses ... `open_terms` carry nothing". This is METHOD.md line 61 in manage-agents. I added the
  repo's rule that only predicate legends are shown (`tests/omission_rule.py:176-185`).
- The lead-in rule against amendment 8(b) (METHOD.md line 64).
- The known-gap rule against amendment 13 (METHOD.md line 70). Class order is in section 2 (METHOD.md lines 32-36).
- The condition test against deliverable 3: byte for byte after the project's quote normalisation
  (`usecases/safetyfw_accounting.py:89-95`), reading the source through `tests/pinned_source.py`.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed route or Lean answer changed.
2. Every deliverable built: PASS. Deliverables 0-3 are in sections 0-3, verified by
   `test_the_legend_quotes_the_pinned_source_sentence` (44 passed).
3. Tests can fail: PASS. Seeded bugs B1-B4 (section 4), and 42 failures on main's legends (section 3).
4. Python, Lean and Rust agree: N.A. No decision path changed. `run.py --check` exit 0, and results.json moves no
   verdict.
5. R8 binding: N.A. No relayed answer.
6. Gate evidence matches the final HEAD: PASS (pending). The selected run was on the rebased tree. The chain runs the
   full gate on the final HEAD.
7. No unsigned item: PASS. DELTA.md has no row and no reserved signature.
8. Every user-visible change in DELTA: PASS. DELTA.md records the legend text and the certificate hashes. No verdict,
   diagnostic or availability changes (`run.py --check`).
9. Test selection finds the tests: PASS. The selected plan ran `tests/test_srccov_safety_framework_1119.py` and
   `tests/test_safety_framework.py` (select.log line 14). B1 fails a selected test.
10. Lean statements: N.A. No Lean change.
11. Budgets and limits: N.A. None touched.
12. CPU and memory: N.A. Text only. The longest changed legend is 16 vocabulary.py lines, under `legend_raw`'s
    40-line read (`test_the_carrier_is_a_legend_a_reader_is_shown`).
13. Test-removed trailer: N.A. No test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS.
    - Accept: 44 passed at HEAD.
    - Refuse: B1-B4, and 42 failed at main.
    - The spec re-read is listed above.
15. Overclaim, silent cut, new checks fail, limits:
    - Overclaim and silent cut: PASS. Every dropped row is in the verify table with its reason.
    - New checks can fail: PASS. B3 and B4 cover the two new guards.
    - Limits: N.A.
