# usecase-safetyfw: three frontier-lab safety frameworks in VE (build report)

- **Status:** F14 (B) fixed as a class (section 25): one Rust table of Lean's sort decoders, a three-engine truth table over all 1,045 admitted profile lists, two hunts. F1-F4, F6-F13 stay fixed. No DRI signature is reserved.
- **HEAD:** see the final local commit; section 25 records the exact test results.
- **What changed:** Rust's environment decoder (`rust/ve-kernel/src/environment.rs`) and its tests; the differential baseline. Lean and Python product code are unchanged.
- **Open items:** H1-c (Lean's request and environment modes order faults differently, DF-21), the out-of-class forms in section 25.4, F5 (C, follow-up); completion of the OpenAI translation before `usecase-pf-run`, `usecase-rsp-run`, `fsf-r3`.

## 1. Task rows

| Task row | Delivered | Commit | Checked by |
|---|---|---|---|
| 1. cases.json and answer-key.json for both cases from PLAN 5 and 6, no key change | yes: 49 cases and 126 items (anthropic-rsp); 67 cases and 239 items (openai-preparedness) | f4d0cb0ac | `tests/test_safetyfw_usecases.py` |
| 1(a) a test recomputes the section-6 SHA-256 of KEY-FREEZE.md | yes | f4d0cb0ac | `::test_section_6_is_the_frozen_key` |
| 1(b) the item count equals the section 5 total (126, 239) | yes, parsed from section 5's table | f4d0cb0ac | `::test_answer_key_has_every_item_of_section_5` |
| 1(c) every family's count | yes, plus the ALL/SOME/NONE totals section 6 states, and a hash pin of both transcriptions | f4d0cb0ac | `::test_answer_key_has_every_item_of_section_5`, `::test_verdict_totals_are_those_section_6_states`, `::test_transcription_is_pinned` |
| 2(a) the existing harness, unchanged; every changed unit with its cause | yes: all four `--check` pass; no unit changed status or answer | deefa264d | [fsf-r2/probes.md](../safety-framework/fsf-r2/probes.md) (a); `tests/test_safety_framework.py::test_fsf_r2_measures_every_unit_as_saved_and_none_moved_since_oct18` |
| 2(b) per fsf-r1 family, a probe on a part document per merged item | yes: JT-a to JT-d (jt-2, jt-2b), DF-a to DF-c (df-1b, df-1bb), SC-a to SC-d (sc-5r, sc-5rb); the families no merged item touches are named | deefa264d | `::test_fsf_r2_probes_record_lean_s_answer_on_each_merged_item`, `::test_fsf_r2_probes_rerun_equals_saved_probes` |
| 2(b) no rule or reading of the translation changed; re-expressions named as `fsf-r3` with expected bytes | yes: rules.d1.ve, facts.d1.ve, build_document.py, readings untouched; fsf-r3 table in probes.md | deefa264d | `git diff main...HEAD -- usecases/safety-framework` touches only `measure_r2.py` |
| 2(c) docs/usecases/safety-framework/fsf-r2/ (units.json, gaps.json, probes.md); fsf-r1 unchanged | yes (and probes.json) | deefa264d | `measure_r1.py --check` passes |
| 3. anthropic-rsp: vocabulary, environments D1, D2, D3 | D1: `rsp_vocabulary.py`, `environment.d1.json`; D2 and D3 are built in `stage0.py` (no source prose, no separate file) | a0c22aafd | `::test_rsp_environment_file_is_generated`, `::test_rsp_stage0_rerun_equals_saved` |
| 3. rules.d1.ve, facts.d1.ve with the source sentence beside each rule | 76 rules, 11 premise blocks | a0c22aafd | `::test_rsp_every_rule_and_premise_parses_with_one_reading`, M6 in `::test_rsp_identifiers_and_inventions` |
| 3. span accounting: every byte in one unit; status by VE's check; kind; reason; residual | yes, 303 units; coverage.json has `bytes_by_status`, `master_bytes_by_status`, `bytes_by_kind`, `unformalised_reasons`, `residual` (safety-framework's shape) | a0c22aafd | `::test_rsp_every_byte_is_in_exactly_one_unit`, `::test_rsp_reviewer_prohibitions_are_separate_coverage_units` |
| 3. stage 0 probes P1 to P8 | yes ([stage0.json](anthropic-rsp/stage0.json)) | a0c22aafd, c1fd40403 | `::test_rsp_stage0_saved_answers`, `::test_rsp_stage0_rerun_equals_saved` |
| 3. a measure script writing gaps.json by family, all blockers and alone | `measure.py` ([gaps.json](anthropic-rsp/gaps.json), [units.json](anthropic-rsp/units.json)) | a0c22aafd | `::test_rsp_every_byte_not_checked_waits_for_a_named_family` |
| 3. shared code with safety-framework by import; safety-framework's outputs unchanged | the unit-spec helpers and `measure` of its build_document.py are imported (loaded apart, as its test loads them) | a0c22aafd | safety-framework's `build_document.py --check` and `run.py --check` pass |
| 3. CHECKED-bar lint (P7), invention audit (M6) | 0 violations, 0 untraced | a0c22aafd | `::test_rsp_identifiers_and_inventions` |
| 3. PLAN section 12: only this item's deviations | 13 items | d78e9b9d9 | `::test_section_6_is_the_frozen_key` (section 6 unchanged) |
| 4. openai-preparedness baseline | 389-unit source partition, D1 vocabulary and source-linked blocks, D2/D3 probes, P1–P8, P7/M6, gaps; sparse translation and quantity gaps recorded in PLAN 12 | this branch | `tests/test_safetyfw_usecases.py -k test_pf_` |
| 5. README per new case; this REPORT | both READMEs include measured coverage; sections 3–4 rank all three frameworks | d78e9b9d9, this branch | `test_pf_every_byte_has_ve_status_and_one_unit`, saved gaps |

## 2. The sources and the licence decision

| Framework | Version | Text bytes | Text SHA-256 | Licence |
|---|---|---|---|---|
| Google DeepMind, *Frontier Safety Framework* | 3.1 (17 April 2026) | 54,373 | `18e3375b…0c53946` | none stated |
| Anthropic, *Responsible Scaling Policy* | 3.4 (effective 8 July 2026) | 59,410 | `c7de7fe2…2c3063` | none stated |
| OpenAI, *Preparedness Framework* | 2 (15 April 2025) | 67,418 | `d2e3dd5b…e48d0f` | none stated |

No source states a licence. So, as for safety-framework, no PDF, no extracted text and no document with the source
prose is committed. The repository keeps the hashes, the extractors, byte spans, unit ids and short quotations. Each
builder reads the stored copy under `~/code/manage-agents/pilots/<case>/source/`, checks its SHA-256 against PLAN
section 1, and writes the `.ve.md` document beside it or in a temporary directory (`--check`). Both stored copies
were checked against their PLAN hashes before use. Tests that need a copy skip without it: the fsf-r2 probe rerun is
in `tools/gate-optional.json`. The RSP build check and the stage 0 source probes run only where the copy exists, in
the same way as safety-framework's `test_span_accounting_is_complete`.

## 3. Coverage of the three frameworks

| Framework | Measured | CHECKED | OPEN | LABELLED | UNFORMALISED | Bytes |
|---|---|---|---|---|---|---|
| DeepMind FSF 3.1 | Oct 1 (first run) | 4,595 (8.5%) | 7,356 (13.5%) | 35,557 (65.4%) | 6,865 (12.6%) | 54,373 |
| DeepMind FSF 3.1 | Oct 18 (fsf-r1) | 4,595 (8.5%) | 7,356 (13.5%) | 35,557 (65.4%) | 6,865 (12.6%) | 54,373 |
| DeepMind FSF 3.1 | Oct 28 (fsf-r2) | 4,595 (8.5%) | 7,356 (13.5%) | 35,557 (65.4%) | 6,865 (12.6%) | 54,373 |
| Anthropic RSP 3.4 | Oct 28 (corrected baseline) | 5,327 (9.0%) | 13,214 (22.2%) | 37,248 (62.7%) | 3,621 (6.1%) | 59,410 |
| OpenAI PF v2 | Oct 29 (D1 family drafts) | 170 (0.3%) | 7,052 (10.5%) | 5,327 (7.9%) | 54,869 (81.4%) | 67,418 |

Sources: [fsf-r2/gaps.json](../safety-framework/fsf-r2/gaps.json) (`master_bytes_by_status`, Oct 1, Oct 18 and
today), [anthropic-rsp/gaps.json](anthropic-rsp/gaps.json) and
[openai-preparedness/gaps.json](openai-preparedness/gaps.json). All three plans expected a CHECKED share under 10%;
the OpenAI plan expected under 5%. Its lower share is chiefly the deliberately sparse translation in PLAN 12, not
a like-for-like comparison of VE capability.

The RSP has more OPEN and less UNFORMALISED text than the FSF. Its open terms are named on the rules
themselves (28 records), and most of its process sentences are commitments without an open term in their guards (34
CHECKED rules). The DeepMind framework has more process wording ("periodically", "this will inform") that has no rule.

The 3.6.1 paragraph was overcounted as CHECKED: its organization financial-interest rule covered the first 95
bytes, while the next 324 bytes also prohibit financial interests of individual reviewers and their reporting chain,
and close personal relationships. Those two clauses now have separate UNFORMALISED units (182 and 142 bytes) waiting
for SC. The frozen key, including K13, is unchanged. This corrects use-case source coverage; no Lean checker verdict
or diagnostic changed (`test_rsp_reviewer_prohibitions_are_separate_coverage_units`).

## 4. What the bytes that are not CHECKED wait for, all three frameworks, ranked by bytes

A unit counts under every blocker it has; “alone” counts a unit only when it has one blocker. The source files are
[DeepMind fsf-r2](../safety-framework/fsf-r2/gaps.json), [Anthropic](anthropic-rsp/gaps.json), and
[OpenAI](openai-preparedness/gaps.json). DeepMind and Anthropic retain their earlier measurements. The OpenAI
source classification now has zero `not_translated` units. AP records duties without a complete D1 act or rule;
readings records source claims that still lack a chosen formal reading. The figures below are all-blocker bytes, followed by sole-blocker bytes.

| Family | DeepMind: all / alone | Anthropic: all / alone | OpenAI: all / alone | Three: all / alone |
|---|---:|---:|---:|---:|
| no claim to check | 29,619 / 29,619 | 31,104 / 31,104 | 5,327 / 5,327 | 66,050 / 66,050 |
| readings | 3,597 / 735 | 3,989 / 2,106 | 13,583 / 11,178 | 21,169 / 14,019 |
| JT | 7,976 / 5,114 | 11,372 / 6,892 | 4,685 / 1,613 | 24,033 / 13,619 |
| AT | 5,617 / 5,617 | 6,510 / 6,510 | 12,973 / 12,386 | 25,100 / 24,513 |
| ET | 2,212 / 2,212 | 1,390 / 489 | 8,086 / 5,728 | 11,688 / 8,429 |
| external reference | 1,978 / 1,978 | 797 / 797 | 309 / 309 | 3,084 / 3,084 |
| DF | 551 / 551 | 866 / 405 | 1,185 / 0 | 2,602 / 956 |
| SC | 283 / 283 | 1,935 / 693 | 4,896 / 3,945 | 7,114 / 4,921 |
| WG | 807 / 807 | 551 / 551 | 183 / 0 | 1,541 / 1,358 |
| QT | 0 / 0 | 105 / 0 | 702 / 305 | 807 / 305 |
| AP | 0 / 0 | 0 / 0 | 21,638 / 20,766 | 21,638 / 20,766 |

AP now carries the largest share of non-CHECKED bytes in the OpenAI case because the D1
act vocabulary does not express those source duties. The table is regenerated from the saved
gap counts; the other two cases retain their earlier measurements.

## 5. fsf-r2: the DeepMind case after the merged items

Full results: [fsf-r2/probes.md](../safety-framework/fsf-r2/probes.md).

| Merged item | Probe answers | Bytes moved since Oct 18 |
|---|---|---|
| jt-2, jt-2b (`judgments@0`) | D1 with `judgments@0`: refused (`judgments@0 with soft-norms@0 needs its composed Lean route`). Without `soft-norms@0`, D1's open-term records are refused (`JudgmentUnbound`: they are names no formula reads). Declared on the open predicates the rules read, all 8 rule units (1,291 B) are admitted and OPEN, with Lean's usage map | 0 |
| df-1b, df-1bb (defaults flag) | refused on every force set (`applies to a soft-norms@0 document without open reading sets`). On the same unit with only the default reading (a collapse, probe only), the flag needs `norm-defaults@0`; with it, the answer is UNKNOWN ("no certificate") and `ve document check` refuses the profile | 0 |
| sc-5r, sc-5rb (`scope@0` per choice) | RS8's unit, written as a governor re-guarding f9-dm, holds the set: refused, `ScopeReadings: s135-bullet2-only` (a set on a governor's own unit is SC-5's case). Without the set it is admitted and OPEN. On D1's soft chain with `readings@1`: not composed | 0 |

No byte moved, as expected, because (a) found no change. `fsf-r3` would re-express the open terms on their
predicates once jt-2c lands, and the "may be adjusted" units as default rules once `ve document check` admits
`norm-defaults@0`. At most 1,906 B would move, from UNFORMALISED to OPEN, and none to CHECKED.

## 6. Key findings

None. No step of either translation contradicted a frozen key cell, and no key cell was edited. Neither baseline
answers key items; that remains for `usecase-rsp-run` and `usecase-pf-run`. OpenAI PLAN 12 documents translation
gaps, especially the unrepresented quantity bridges, without changing an answer.

## 7. VE observations (no product code changed; repros saved)

None of these gives a wrong verdict. Each is a limit the translation had to work around, recorded with its repro.

1. **Two entry points admit different documents.** `ve document readings --assume-no-exception` admits a document
   whose environment lists `norm-defaults@0` and answers it. `ve document check` refuses the same file:
   `UnsupportedProfile: Unsupported profile norm-defaults@0`. Repro: fsf-r2 probe DF-c (`probes.json`; the document
   is DF-b's with `norm-defaults@0` and `documents@1` listed). This may be by design, since the flag is its own
   route, but it is the kind of difference build checklist item 10 asks about.
2. **Two lists of attributed acts.** `VE.Route.Admission.acts` (the document route) has `says`, `promised`,
   `believes`, `intends`, `expects`, `denies`. `VE.Attribution.Wire.reportActs` adds `wants`. A document unit
   `["attributed", "developer", "wants", ...]` is refused (`invalid attributed kind`). The RSP's "We want" is written
   `intends`, and its hopes and preference are UNFORMALISED (PLAN 12, item 7).
3. **A harm with no class cannot be stated.** The risk route refuses an unclassified harm (`HarmUnclassified`, P3),
   so the RSP's T4 harm, which the text gives no class word, is left out of D2 (PLAN 12, item 8).
4. **Act phrases refuse digits, `for` and joins** outside a fixed phrase, and an environment holds at most 64
   regulated predicates. Both forced rewordings and merges (PLAN 12, items 3 and 4).

## 8. Follow-ups

| Item | What it needs |
|---|---|
| `usecase-rsp-run` | `run.py`: cases.json's situations as atoms over the D1 vocabulary; per-choice expansion of `build_document.READINGS` (a reading's rules, premises and `case:` premises); both completion defaults; S from P3's tables, D from P4 (with checked countermodels for D3a and D6a, and RS9 in D3 with a day-count bridge), T5's cost factor in D3; `reference.py` (A, B, C, G from PLAN 3 and 4 alone); results.json; M1, M2, M4, M7 to M10; mutants m1 to m6; fsf-r1's content-bearing sets for the sets whose readings are each one rule (RS8, RS12, RS13, RS6) |
| `usecase-pf-run` | complete the explicit F1–F17 source readings and D2/D3 quantity bridges named in PLAN 12, then implement `run.py` and `reference.py` for the 239 frozen items, both completion defaults, results.json and M1/M2/M4/M7–M10; no key cell may change |
| `fsf-r3` | the re-expressions of fsf-r2 (probes.md): open terms on their predicates under `judgments@0` after jt-2c; "may be adjusted" as a default rule once `ve document check` admits `norm-defaults@0`; RS8 after SC-5. Needs a second-model fidelity check |

## 9. Seeded bugs (each planted, its test shown failing, then removed)

| # | File | Bug | Failing test |
|---|---|---|---|
| 1 | `usecases/anthropic-rsp/answer-key.json` | key cell A-T0/PROT2 `SOME(uncond)` → `NONE` | `tests/test_safetyfw_usecases.py::test_verdict_totals_are_those_section_6_states[anthropic-rsp]`, `::test_transcription_is_pinned[anthropic-rsp]` |
| 2 | `usecases/anthropic-rsp/answer-key.json` | one item dropped | `::test_answer_key_has_every_item_of_section_5[anthropic-rsp]`, `::test_transcription_is_pinned[anthropic-rsp]` |
| 3 | `usecases/openai-preparedness/PLAN.md` | section 6 cell K8 `NONE` → `ALL` | `::test_section_6_is_the_frozen_key[openai-preparedness]` |
| 4 | `tools/difffuzz_corpus.py` | the `usecases/anthropic-rsp/cases.json` entry dropped | `tests/test_difffuzz.py::test_every_fixture_is_read_or_excluded_with_a_reason` |
| 5 | `docs/usecases/safety-framework/fsf-r2/units.json` | s134-rra saved as CHECKED | `tests/test_safety_framework.py::test_fsf_r2_measures_every_unit_as_saved_and_none_moved_since_oct18` |
| 6 | `usecases/safety-framework/measure_r2.py` | "judgment terms" mapped to QT | `tests/test_safety_framework.py::test_fsf_r2_measures_every_unit_as_saved_and_none_moved_since_oct18` |
| 7 | `usecases/safety-framework/measure_r2.py` | JT-c's record put back on the token `ot1_level_reached` | `tests/test_safety_framework.py::test_fsf_r2_probes_rerun_equals_saved_probes` |
| 8 | `usecases/anthropic-rsp/build_document.py` | a byte moved between units: s2-share's anchor 8 bytes later | `::test_rsp_every_byte_is_in_exactly_one_unit` ("spans.json or coverage.json is out of date") |
| 9 | `usecases/anthropic-rsp/measure.py` | `degree_term` mapped to WG | `::test_rsp_every_byte_not_checked_waits_for_a_named_family` |
| 10 | `usecases/anthropic-rsp/rsp_vocabulary.py` | a predicate renamed `review_if_board` | `::test_rsp_identifiers_and_inventions` |
| 11 | `usecases/anthropic-rsp/rules.d1.ve` | an invented stop rule on no unit (PLAN 11 m2) | `::test_rsp_identifiers_and_inventions` (M6 untraced) |
| 12 | `usecases/anthropic-rsp/stage0.py` | PLAN mutant m6: D4's "Within 30 days" → 60 | `::test_rsp_stage0_rerun_equals_saved`. On the first try it was **not** caught: D4 and D5 compared the day asked about with the deadline the wrong way round. Fixed in c1fd40403; the saved answers are unchanged |
| 13 | `tools/difffuzz_corpus.py` | removed the anthropic-rsp cases.json exclusion, then restored it | `tests/test_difffuzz.py::test_every_fixture_is_read_or_excluded_with_a_reason` failed with that fixture unread |
| 14 | `usecases/anthropic-rsp/build_document.py` | removed the personal-relationships unit, then restored it | `tests/test_safetyfw_usecases.py::test_rsp_reviewer_prohibitions_are_separate_coverage_units` failed with that builder unit absent |
| 15 | `usecases/openai-preparedness/pf_vocabulary.py` | renamed the CYB-C level constant | `::test_pf_translation_lint_and_invention_audit` failed (environment differs) |
| 16 | `usecases/openai-preparedness/build_document.py` | changed the pinned source length to 67,417 | `::test_pf_every_byte_has_ve_status_and_one_unit` failed |
| 17 | `usecases/openai-preparedness/measure.py` | mapped `not_translated` to JT rather than readings | `::test_pf_stage0_and_gaps` failed (saved gaps differ) |
| 18 | `usecases/openai-preparedness/stage0.py` | forced the stated BIO-C `might` cell to false | `::test_pf_stage0_and_gaps` failed on the stage 0 rerun |
| 19 | `usecases/openai-preparedness/build_document.py` | classified page 2's policy-summary claims as exposition | `::test_pf_every_byte_has_ve_status_and_one_unit` failed on the source rerun |
| 20 | `docs/usecases/safetyfw/REPORT.md` | changed the OpenAI CHECKED cell from 708 to 709 B | `::test_pf_every_byte_has_ve_status_and_one_unit` failed on the saved-report comparison |

Product code in the reviewed sense: Python under `tools/` (`difffuzz_corpus.py`, one registry entry; bug 4). No
Lean or Rust file changed. Rows 15–18 are this branch's Python use-case-script mutants; each was restored before
the saved checks were run again. Bug 19 was planted after the review correction that moved page 2 from LABELLED to
UNFORMALISED; it failed the saved source check and was restored.

## 10. Tests and checks run

- While iterating: each new test file and `-k` selection; `difffuzz -k test_every_fixture_is_read_or_excluded_with_a_reason`.
- safety-framework's harness, unchanged: `run.py --check` (3 min 7 s), `build_document.py --check`,
  `readings_r1.py --check`, `measure_r1.py --check`, all exit 0. Before that: `lake build` and
  `python3 tools/rust_build.py` (the binary already pinned).
- `uv run python tools/trust_map.py --check`: PASS, K +0, S +0, D +0, trusted +0.
- `uv run python tools/gate_collection.py --check --prebuilt`: 21 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- `uv run python tools/regen_generated.py --check`: 33 entries up to date.
- Selected tests, once (`mac-pytest.sh --select`; the Mac was unreachable and it ran on the VM): 51 units, 2 failed:
  `tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon` and
  `tests/test_english_lean_s3.py::test_lx14_every_wording_python_selects_on_the_corpus_is_subject_first`. Both pin the
  corpus at 39 environments, and the new `environment.d1.json` makes 40, all valid. Fixed (a40a0f4d9: the report
  regenerated by its generator, the pins moved to 40), and the two ids rerun: 2 passed.
- **Not run:** the full gate (the chain runs it on the final HEAD); `trust_mutants` (no Lean change); any model call,
  pilot or whole-document run. No item of `main-known-red.txt` was touched.

## 11. Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A., because no relay or schema changed. The new scripts read Lean
   answers only through `ve.backends.relay` (`answer`, `rows`) and `ve.document`, which check them.
2. Every deliverable built, no rule broken: PASS. Task rows are in section 1 with commits and tests. Part 4 is cut
   under the task's own size rule. No new Python copy of a Lean decision: every status and verdict is VE's
   (`test_rsp_every_byte_is_in_exactly_one_unit` reads `ve.document.coverage`). No report test checks batch
   evidence.
3. Tests can fail: PASS. 14 seeded bugs in section 9, one of which found a real error (m6).
4. Py/Lean/Rust agree, valid inputs pass: N.A., because no checker code changed. safety-framework's `run.py --check`
   reproduces every saved answer.
5. R8 binding: N.A., because no relayed field was added.
6. Gate evidence on the final HEAD: N.A. for this build, since the chain runs the gate. The evidence commit list in
   section 1 comes from `main..HEAD --no-merges`.
7. No unsigned item: PASS. No DELTA row, trust +0 (`tools/trust_map.py --check`).
8. Every user-visible change in DELTA: PASS, with "none": no `ve` behaviour changed. The new use-case outputs are new
   files, and safety-framework's outputs are byte-identical (`build_document.py --check`, `run.py --check`).
9. Test selection finds the tests: PASS. `tools/select_tests.py` selected 51 units, not all, and the selection held
   the two corpus tests the new environment broke.
10. Lean statements: N.A., because no Lean change.
11. Budgets and deadlines: N.A., because no budgeted operation was added. The new tests use no sleep and no timeout
    (`tests/test_hang_guards.py` is in the selection and passed).
12. CPU and memory: N.A., because no product path changed. The stage 0 probes are part documents, never a
    whole-document readings run (L70).
13. `Test-removed` trailers: PASS. No test removed or renamed (`gate_collection.py --check --prebuilt`: 0 removed,
    0 stale, 0 malformed).

## 12. Review correction

- F1: split the 3.6.1 paragraph into three source clauses; only the organizational rule remains CHECKED.
  `test_rsp_reviewer_prohibitions_are_separate_coverage_units` and the saved-report consistency test passed;
  the review's F1 probe failed before and passed after. Commit 92a2fd643.
- F-ready1: planted and restored the changed Python corpus-registry mutant; its fixture-coverage test failed.
  The committed [seed-mutants.json](seed-mutants.json) names that file and the builder mutant for the new coverage
  rule. The review-ready mutant check is rerun on the final commit.
- Verification: 20 use-case tests passed; the corpus-registry regression passed after restoration. The selected
  runner's preflight completed `lake build` and `python3 lean/audit.py`, then reported `FULL: missing coverage map`
  and expanded pytest to 484 units; that pytest expansion was stopped under this item's selected-only instruction.
  No release gate or model call ran. The three entries in `main-known-red.txt` were left untouched.

## 13. OpenAI baseline verification (this branch)

- Implementation and saved evidence: `8797d5328`. The pinned PDF (170,399 B,
  `fae6e4cc6f7212a010bb9348fc0cde1fe711b9cad426c6a99db97740ee52729b`) and extracted text (67,418 B,
  `d2e3dd5b80e5bb86079911230358e0c2bb78f12435757959e14dae50e4d48d0f`) match PLAN 1; neither was
  committed. D1 `build_document.py --check`, P1–P8 `stage0.py --check`, `measure.py --check` passed through
  `test_pf_every_byte_has_ve_status_and_one_unit` and `test_pf_stage0_and_gaps`.
- Diff review found that page 2's policy-summary claims had been labelled as exposition. The corrected evidence
  assigns those 2,365 bytes to UNFORMALISED, with no CHECKED byte moved. The focused page-2 assertion and seeded
  bug 19 now guard that boundary. Bug 20 showed that a stale report cell also fails.
- `tests/test_safetyfw_usecases.py -k test_pf_`: 3 passed. The new D1, D2 and D3 environment files and all 32 rule
  blocks passed `test_pf_translation_lint_and_invention_audit`. The six seeded bugs in section 9 each made its
  named test fail, then were restored.
- The English corpus grew from 40 to 43 environments (D1, D2 and D3). The lexicon report generator found 43 valid,
  0 invalid; both `test_every_corpus_environment_has_a_valid_selected_lexicon` and
  `test_lx14_every_wording_python_selects_on_the_corpus_is_subject_first` passed.
- Shared-code invariance: Anthropic `build_document.py --check`, `measure.py --check` and `stage0.py --check` passed.
  DeepMind `build_document.py --check`, `measure_r1.py --check`, `readings_r1.py --check` and `run.py --check` passed;
  the latter reproduced its saved 257/262 agreement and five known disagreements.
- `tools/trust_map.py --check`: K +0, S +0, D +0, G +0, trusted +0. `tools/gate_collection.py --check --prebuilt`:
  3 added tests, 0 removed, 0 refused, 0 stale, 0 malformed. `tools/regen_generated.py --write` wrote its 33
  registered entries once after the initial implementation; the English lexicon report was regenerated by its own
  generator after the final vocabulary edit.
- Selected runner: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` first fell back to the VM
  and stopped before pytest because the Lean-build cache path was read-only. With `VE_LEAN_BUILDS` and
  `VE_TESTMAP_CACHE` under `/tmp` and VM fallback forced, it selected 67 files but expanded into recording 486 test
  units because the VM had no usable coverage map. The one-hour command timeout stopped that recording before the
  selected pytest phase. Every unit listed as completed in its log exited 0; there is no completed selected-test
  summary. It was not rerun on unchanged code. The chain's final-HEAD gate remains the next full check.
- No Lean or Rust source changed, so the Lean rebuild, audit and trust mutants are inapplicable. No model call,
  pilot, whole-UDHR/constitution run or local full release gate was made. The three known red tests on main were
  neither edited nor included as fixes.

Acceptance ownership for this baseline:

| Acceptance item | Tag | Status and owner |
|---|---|---|
| Pinned hashes, source partition, VE statuses, stage 0, gaps, P7/M6 | AGENT | Built and checked by the named `test_pf_` tests |
| Publisher's current-version claim | EXTERNAL | Observation only; OpenAI owns any later publication, and no VE verdict depends on it |
| Completion and independent source fidelity of remaining untranslated clauses | AGENT | Open in this branch; no DRI ruling has moved the planned D1–D3 translation to another batch |

## 14. Self-review against BUILDER-CHECKLIST

1. **N.A.** No relay or schema changed; case scripts call `ve.document` and `ve.backends.relay` for every answer.
2. **FAIL for the OpenAI D1–D3 deliverable** — PLAN 7 requires the complete translation. PLAN 12 discloses the
   sparse baseline but is not a DRI ruling that moves the remaining work.
3. **PASS** — seeded bugs 15–20 in section 9 each failed its named `test_pf_` test before restoration.
4. **N.A.** No checker path changed; DeepMind `run.py --check` reproduced saved results.
5. **N.A.** No relayed field or request binding changed.
6. **N.A.** The chain, not this builder, runs the full gate on the committed final HEAD; the selected runner's
   timeout is recorded in section 13.
7. **PASS** — no DELTA row or unsigned user-visible delta; `tools/trust_map.py --check` measured trust +0.
8. **PASS** — no VE behaviour changed; Anthropic and DeepMind saved-output `--check` commands passed (section 13).
9. **PASS** — the selector identified `tests/test_safetyfw_usecases.py` and both corpus tests among its 67 files;
   section 13 records why its VM test phase did not finish.
10. **N.A.** No Lean theorem or statement changed.
11. **N.A.** No public budget or deadline path changed; `test_pf_stage0_and_gaps` checks saved UNKNOWN on P2.
12. **N.A.** No checker path changed; the stage 0 probes are part documents and `test_pf_stage0_and_gaps` passed.
13. **PASS** — no test was removed or renamed; `tools/gate_collection.py --check --prebuilt` reports 0 removed,
    refused, stale and malformed.

## 15. Review correction on this branch

At the recheck1 HEAD, F1 remained open. The D1 document lacked F5/F6/F11/F12/F17 per-choice rules. Its former generic
`not_translated` backlog is classified by immediate blocker, but those source claims remain unformalised.
D2 still leaves the two AIS causal cells open; D3 still leaves the vague severity quantities open.
The sparse translation cannot be reported as a completed PLAN 7 deliverable, and no DRI ruling signs a
scope move. `usecase-pf-run` remains the answering harness; it does not cover this translation gap.

F2 is corrected as a coverage claim: the F7 predeployment and three F9 per-item source units are
UNFORMALISED with ET/SC blockers. Their source-linked draft blocks use explicit temporal/per-item act names but
are not attached as CHECKED content. `test_pf_temporal_and_per_item_rules_are_not_weakened_into_checked_claims`
checks both the rebuilt source partition and saved statuses. Seed mutations changing the F7 or F9 blocker reason
each failed that test before restoration. The F2 print probe now shows
`evaluations_before_deployment` in the parsed draft.

F3 is corrected in the page classifier: the blanket change-log and Appendix C exposition ranges were removed.
The two RS15 undertakings are OPEN reading sets, and the two Appendix C restatements are OPEN F2/F3 rules.
`test_pf_exposition_fallback_preserves_claims_and_rs15_readings` guards the four spans and an unlisted claim on
both pages. A seed mutation restoring the page-15 blanket label failed that test before restoration. The F3
probe now passes. These coverage corrections do not change Lean, Python relay, or Rust checker verdicts; there is
no checker DELTA row or claim of a signed scope change.

## 16. Recheck2 correction (2026-10-29)

Status: class W and L source coverage corrected; F1 translation remains open.
HEAD for the selected run: `3609ce939` plus the uncommitted class correction (Mac snapshot `d08c1950`).
The source partition still totals 67,418 bytes; the frozen key did not change.
No DRI signature is reserved, and no checker verdict or Lean trust budget changed.

The D1 rule admission now fails closed when a draft has a wait or lacks an exhaustive source-clause map.
`p10-u152` (AT wait), `p13-u218` (SAG reports and reasoning), and `p16-u271` (recommendation contents)
are UNFORMALISED with blockers. `p16-u283` is CHECKED after its Board/process clauses were mapped and its
rule act was completed. The other source-linked draft rules remain available for future completion.
The label classifier acts on the whole source unit and requires a positive
exposition kind without any duty or hedge marker. It exposes `p11-u169`, `p19-u327`, `p19-u335` and
`p19-u336` as non-LABELLED. `test_pf_checked_has_no_wait_or_unmapped_source_clause` and
`test_pf_label_requires_positive_exposition_without_claim_marker` check these classes.

The single requested adversarial hunt found the previously unlisted W form `p16-u271` and L forms
`p11-u169`, `p19-u327` and `p19-u336`. All are covered by the same tests. Before restoration, a Python
mutant that bypassed the clause-map gate failed
`test_pf_checked_has_no_wait_or_unmapped_source_clause`; a mutant that restored the page-18–20 blanket
label failed `test_pf_label_requires_positive_exposition_without_claim_marker`. No second hunt ran.

F8 and F9 stale artifacts were regenerated and committed as `3609ce939`; their probes passed. The selected
run passed 80 units with zero failures on the Mac runner (snapshot `d08c1950`). The local `lake build` and
`python3 lean/audit.py` passed. The full suite and release gate were not run under this branch's test instruction.
The three `main-known-red.txt` tests are pre-existing and were not changed.

D2/P3 now checks BIO-H, BIO-C, CYB-H and CYB-C as `might` cells and confirms none becomes `leads`.
The AIS-H and AIS-C rows retain explicit AT blockers. D3/P4 admits the source's one-fifth time inequality,
distinguishes the frozen T1/T2 durations with Lean certificates, and replays the three conditional date bridges.
`test_pf_p3_p4_are_recomputed_without_source_text` and
`test_pf_one_fifth_time_bound_distinguishes_the_two_frozen_cases` cover these additions.
Python mutants changing the one-fifth coefficient to four and changing BIO-H's `might` to `leads`
each failed `test_pf_p3_p4_are_recomputed_without_source_text` before restoration.

## 17. Selected-run differential fault order

On committed `b469eacdf`, the final selected run found one new differential case in
`tests/test_difffuzz.py::test_ci_run`: a `defined` field on a plain relational predicate also contained an
invalid variable index. Python and Lean reported `UnboundVariable`; Rust reported the outer extra-field
`InvalidInput`. The single-test Mac rerun reproduced it. Rust now decodes the nested definition before
rejecting the unsupported field, following Lean's deterministic order. A well-formed nested definition still
gets the outer `InvalidInput`.

| Delta | Ruling | Evidence |
|---|---|---|
| Rust diagnostic order for a malformed nested `defined` on a relational-only predicate | R2 (standing ruling, DRI-RULINGS.md): the nested variable fault precedes the outer field fault, deterministically | `tests/test_difffuzz.py::test_unprofiled_definition_checks_nested_fault_before_field_refusal`; `rust/ve-kernel/tests/environment_definition_order.rs::malformed_nested_definition_precedes_unsupported_field` |

Restoring Rust's earlier outer-field-first branch as a seeded mutant made the new Rust regression fail; the
restored source passed. No Lean or Python product code changed for this diagnostic. The `main-known-red.txt`
tests remain untouched.
The baseline generator dropped the two now-fixed DF-20 entries (242 to 240). After that regeneration, the
focused Mac rerun of `test_ci_run` and the new three-way regression passed, 2/2. The initial selected run
had 79/80 units pass and this one difffuzz failure. On `db162a36f`, the final selector ran all 366 selected
test files on the VM; their saved results each have exit 0, including `test_difffuzz.py` and
`test_safetyfw_usecases.py`. The wrapper exited 1 only after the tests, when writing its performance map to
the read-only home cache (`~/.cache/ve-testmap`). No test failed; the map write needs a writable
`VE_TESTMAP_CACHE` on a future selection run.

## 18. Recheck1 F1 family completion (2026-10-29)

F1's executable probe failed before this change and passes after it. D1 now has source-linked draft blocks for
F5, F6, F11, F12 and F17, plus F13, so every planned F1–F17 family has a block. The reading inventory binds F6's
default, F11's two adjustment interpretations and their shared conditions, the five separate Table 2 responses,
and F17's sufficient and iff interpretations to their named choices. The F17 iff interpretation includes a
separate negative guard over the five individual criteria. `test_pf_all_planned_d1_families_have_source_bound_drafts`
checks all families, source linkage, choice binding, parsed guards and source-unit status. Removing F11's exception
from the choice inventory made that test fail before restoration.

The source partition still totals 67,418 bytes and keeps 170 CHECKED bytes. The five Table 2 source units are OPEN;
Sandbagging and Nuclear retain AP waits for the disjunctive response and consultation details. F5's decision and
checkpoint and F13's periodic review and assessment remain UNFORMALISED. The pending reading sets still contain no
admitted rule content, so these drafts do not answer any frozen key item. The generated D1 environment, source
spans, coverage, stage 0 and gaps were refreshed from their owning scripts. There is no checker verdict, diagnostic,
fault-order or trust-budget delta, hence no new DELTA row or DRI signature.

The three `main-known-red.txt` tests remain pre-existing and were not edited. The full suite and release gate were
not run under this branch's test instruction.

## 19. Selected-run constant-container fault order

The selected test `tests/test_difffuzz.py::test_ci_run` found a dual-fault environment where the constant named
`legal` was a list and a predicate argument used the reserved `$string` sort without `data@0`. Python and Lean
reported `InvalidInput`; Rust reported `UnknownSymbol`. Rust now defers this unsupported built-in signature
until after constant declarations, reporting their fault first. A subsequent fuzzer sample showed that an
ordinary unknown predicate sort must still be reported before a malformed constant declaration; the temporary
broad constant precheck was removed. The
three-engine regression `tests/test_difffuzz.py::test_predicate_signature_and_constant_fault_order` and Rust unit
`environment_definition_order::predicate_signature_and_constant_fault_order` exercise both orders and codes.
The Rust release binary was rebuilt and `lean/checkers.lock` regenerated by its owner.

| Delta | Ruling | Evidence |
|---|---|---|
| Rust reports constant declaration faults before an unsupported built-in signature, and an ordinary unknown predicate sort before a malformed constant | R2 (standing ruling, DRI-RULINGS.md): unsupported built-in signatures follow constants; ordinary unknown sorts precede constants, deterministically | `tests/test_difffuzz.py::test_predicate_signature_and_constant_fault_order`; `rust/ve-kernel/tests/environment_definition_order.rs::predicate_signature_and_constant_fault_order` |

## 20. Selected-run request-envelope fault order

The focused rerun of `tests/test_difffuzz.py::test_ci_run` found a request whose environment omitted required
outer fields and also named an undeclared predicate argument sort. The public Python path reported the nested
sort fault through the Lean environment service, while the Lean request runner and Rust reported the envelope
fault. The service now checks the route envelope before using the shared vocabulary location decoder to refine
a diagnostic. The frozen route uses its exact envelope decoder; composed routes first require their common
header fields, profile shape and revision. The existing response-shape proof covers the new branch.

`tests/test_difffuzz.py::test_request_envelope_fields_precede_predicate_sort_fault` failed before the change and
passes after it. It checks missing profiles, missing revision and an extra outer field against all three engines.
The Lean library and executables built successfully after the proof change; `lean/checkers.lock` was regenerated
by its owner for the new executable hash.

| Delta | Ruling | Evidence |
|---|---|---|
| The environment service reports an outer field fault before a nested predicate-sort fault on the same malformed route environment | R2 (standing ruling, DRI-RULINGS.md): envelope fields precede vocabulary semantics deterministically | `tests/test_difffuzz.py::test_request_envelope_fields_precede_predicate_sort_fault`; `ResponseShape.Encoders.Standalone.environment_reported` |

## 21. Differential sample after the fault-order fixes

The final bounded `test_ci_run` passes. Its baseline was refreshed from the saved sample: 240 entries became 236.
The previously recorded envelope mismatches resolved by the Lean header check were retired. Six minimized
signatures that still describe existing direct-runner or Rust route disagreements were classified under the
reviewed DF-9 and DF-13 follow-ups in `conformance/difffuzz-baseline.json`; no `TODO` follow-up remains.
The three tests in `main-known-red.txt` were not edited or treated as branch regressions.

## 22. Route header trust classification

The selected `test_committed_trust_table_covers_every_declaration` found that the new Lean helper had no trust
class. `tools/trust-classes.json` now classifies `VE.Service.Standalone.routeHeaderAccepted` as S. On this tree,
`tools/trust_map.py` measures 13 added S lines and 2 added untied V lines, both in
`lean/VE/Service/Standalone.lean` (15 trusted lines total, K unchanged). The executable three-engine envelope
regression tests the new definition and failed before its fix. `FOLLOW-UPS.md` records the ties pass required
by R16.

| Delta | Ruling | Evidence |
|---|---|---|
| `lean/VE/Service/Standalone.lean`: S +13, untied V +2, K +0 | R16 (standing ruling, DRI-RULINGS.md): 15 new trusted lines for the tested route header guard, with a follow-up ties pass | `tools/trust_map.py --check`; `tests/test_difffuzz.py::test_request_envelope_fields_precede_predicate_sort_fault`; `docs/usecases/safetyfw/FOLLOW-UPS.md` |

## 23. Recheck2 F1 and F12 correction (2026-10-29)

F1 -> OPEN RS13 and source-bound residuals -> `test_pf_rs13_and_untranslated_claims_have_named_residuals`, `test_pf_every_byte_has_ve_status_and_one_unit` -> `fb4103767`, `bc7cadbc0`, `3ecb627f7`.
F12 -> Rust `UnknownSymbol` parity -> `test_legacy_undeclared_builtin_sorts_are_unknown_symbols` -> `0ce92f6a5`.

F1: the 5.1 employee summary sentence is an RS13 OPEN reading with `permission` and `might` choices, as PLAN 3.1 states. Both choices remain pending because the source limits highly sensitive information without specifying the limit, and D1 has no complete act for request and receipt. It is not counted as CHECKED. Each remaining fallback UNFORMALISED unit carries a unique source-span hash residual in `spans.json`, keeping the 195 broad `unmapped_claim` and `unmapped_duty` cases independently addressable without saving private source prose. `test_pf_rs13_and_untranslated_claims_have_named_residuals` checks the reading, every residual, and the source binding when the pinned source is available. The original F1 probe failed before the change and passed afterward.

F12: legacy undeclared `$int` and `$string` predicate argument sorts now return `UnknownSymbol` in Rust, matching Python and Lean; composed-route delayed built-in validation remains covered by `test_predicate_signature_and_constant_fault_order`. `test_legacy_undeclared_builtin_sorts_are_unknown_symbols` checks all three engines, an ordinary missing sort, and a declared-sort acceptance case. Rust's `environment_definition_order::legacy_undeclared_builtin_sorts_are_unknown_symbols` covers the same boundary. The original F12 probe failed before the change and passed afterward.

F5 (C) is recorded in `FOLLOW-UPS.md` under the 2026-10-29 DRI focus. The three `main-known-red.txt` tests are pre-existing and were not edited. The full suite and release gate were not run under this branch's test instruction.

Validation commands and outputs on this worktree:

- The exact `PROBE F1` and `PROBE F12` commands in `usecase-safetyfw-b-c290542-looprecheck2.final.md` exited 1 before the fixes and 0 after them; F12 then printed `UnknownSymbol` and `unknown predicate argument sort`.
- `.venv/bin/python -m pytest -q tests/test_safetyfw_usecases.py::test_pf_rs13_and_untranslated_claims_have_named_residuals tests/test_difffuzz.py::test_legacy_undeclared_builtin_sorts_are_unknown_symbols` reported `2 passed`.
- `cargo test -q --manifest-path rust/Cargo.toml -p ve-kernel --test environment_definition_order` reported `3 passed`. A Python mutant that changed RS13 `permission` to `grant` failed `test_pf_rs13_and_untranslated_claims_have_named_residuals`; a Rust mutant that returned `InvalidInput` for the legacy sort failed `legacy_undeclared_builtin_sorts_are_unknown_symbols`. Both were restored, and the two focused commands passed afterward.
- `.venv/bin/python usecases/openai-preparedness/build_document.py --check`, `measure.py --check`, and `stage0.py --check` each exited 0. The regenerated partition still has 389 units and 67,418 bytes: 7 CHECKED, 34 OPEN, 48 LABELLED, and 300 UNFORMALISED. The 195 broad unmapped cases each have a source-bound residual.
- `PATH=$HOME/.elan/bin:$PATH lake build` in `lean/` reported `Build completed successfully (1135 jobs)`; `python3 lean/audit.py` reported `PASS: 653 source files; 7286 named theorem declarations audited`; `python3 tools/rust_build.py --check` reported the Rust release SHA-256 is pinned.
- `zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on the final code and evidence snapshot `7b547257` reported `recorded 397 units for tree e44a552c6a; 0 failed` and exited 0 (`/tmp/ve-safetyfw-selected-final.log`, Mac summary 2026-10-29 18:44:10 UTC). This run included `tests/test_safetyfw_usecases.py` and `tests/test_difffuzz.py`, each exit 0. An earlier selected snapshot exposed stale README and report coverage numbers; its sole `test_safetyfw_usecases.py` failure was `test_pf_every_byte_has_ve_status_and_one_unit`. After the table correction, that test passed alone (`1 passed`) and in the final selected run. The earlier snapshot was stopped after this fix; no test process remains from it.

| Delta | Ruling | Evidence |
|---|---|---|
| The 5.1 employee-summary source unit moves from UNFORMALISED to an OPEN RS13 reading with no admitted rule | SIGNED by DRI (`usecase-safetyfw-b-lp1600-focus.md`, 2026-10-29): the item-specific instruction requires RS13 and forbids semantic coverage from structure alone | `tests/test_safetyfw_usecases.py::test_pf_rs13_and_untranslated_claims_have_named_residuals` |

## 24. Recheck1 F13 correction (2026-10-29)

F13 -> Rust composed order sort classification matches Lean -> `tests/test_difffuzz.py::test_order_routes_reject_string_predicate_sort_before_constants`, `rust/ve-kernel/tests/environment_definition_order.rs::composed_order_rejects_string_predicate_sort_before_constants` -> `4a1ce48bc`.

The executable F13 probe and both new regressions failed before the fix. Rust now returns
`UnknownSymbol` for an undeclared `$string` predicate argument on every composed order route,
including `time@0` and `data@0`. `$int` still succeeds. The exact order route retains Lean's
constant-first fault order; composed order routes report the argument-sort fault first. The
three-engine regression tests all of these cases, including malformed constants. The probe,
Rust unit tests, and three-engine regression pass after the fix. Lean's answer is unchanged.
Restoring the old `InvalidInput` branch as a seeded Rust mutant made the new Rust regression
fail; restoring the committed code made all four Rust tests pass again.

| Delta | Ruling | Evidence |
|---|---|---|
| With both an undeclared `$string` predicate sort and a malformed constant, composed order routes report the sort fault first; the exact order route reports the constant fault first | R2 (standing ruling, DRI-RULINGS.md): Lean's route-specific order is deterministic | `tests/test_difffuzz.py::test_order_routes_reject_string_predicate_sort_before_constants`; `rust/ve-kernel/tests/environment_definition_order.rs::composed_order_rejects_string_predicate_sort_before_constants` |

The single-fault Rust diagnostic correction is parity with the unchanged Lean owner, rather than
a public Lean verdict delta. The three `main-known-red.txt` tests remain pre-existing and were
not edited. The full suite and release gate were not run under this branch's test instruction.
The F13 probe exited 1 before the fix and 0 afterward. `lake build` completed 1,135 jobs,
`python3 lean/audit.py` passed 653 source files and 7,286 named theorem declarations, and
`python3 tools/rust_build.py --check` confirmed the generated checker pin. The selected command
`zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`
recorded 397 units with 0 failed and exited 0 on the VM (2026-10-29 21:51 UTC). Its first attempt
stopped before collection because the default `uv` cache was read-only; the successful run set
`UV_CACHE_DIR=/tmp/ve-safetyfw-f13-uv-cache`.
The generated lock was refreshed again from its prior committed state after the selected run,
so only the final Rust release digest was added (`c7b18fc81`); the checker-pin generator and
Rust pin checks both passed.
The same selected command on this final code and lock state recorded 397 units, 0 failed,
and exited 0 on the VM (2026-10-29 23:42 UTC; tree `f540f4f050`).

## 25. Recheck2 F14: the built-in argument sort class (2026-10-30)

F14 -> one Rust table of Lean's sort decoders (`SortTable`, `located_pass`) in place of the per-route branches -> `tests/test_difffuzz.py::test_builtin_argument_sort_truth_table_agrees_on_every_profile_list`, `rust/ve-kernel/tests/environment_definition_order.rs::builtin_argument_sort_probes_take_lean_codes` -> `f244f474b`, `0c8f46575`, `76545de92`, `e39a10df7`.

Base `6b625cc7a`; DRI note `reviews/usecase-safetyfw-b-dri-note-20261030.md`. The F14 PROBE exited 1
before the fix (Rust `UnknownSymbol`) and 0 after it (`InvalidInput`, Lean's and Python's code).
Lean and Python product code are unchanged.

### 25.1 The table

F12, F13 and F14 were one class: Rust chose a built-in sort's code by profile-list equality and
per-route exceptions (`exact_order_route`, environment.rs:377 at the base). The argument-sort loop
now asks one table, `SortTable` in `rust/ve-kernel/src/environment.rs`. The table names the Lean
decoder that judges the vocabulary, chosen as Lean's `environment` mode chooses it:

- `located_pass` is Lean's located decoder (`locatedEnvironmentFields`, Standalone.lean:942-977).
  It runs first on every envelope. It skips a predicate holding `$string` without `data@0`, or
  `$int` without `order@0` (Standalone.lean:957-958). Every other cell must be declared, `$int`
  under `order@0`, or `$string` under `data@0`; otherwise the answer is `UnknownSymbol` at the
  sort (Standalone.lean:959-962, `VE.Bridge.checkArgumentSorts` Bridge.lean:44). On the frozen
  checker lists (`frozenFamilyProfiles`, Standalone.lean:350) every located fault is the answer,
  constants included (Standalone.lean:969-977, 1197-1201). Elsewhere only the unknown argument sort
  is (Standalone.lean:1165-1168, 1187-1191).
- Then the judge (`SortJudge`), as `validatedLayerEnvironment`/`validated`/`validateFamily`
  dispatch (Standalone.lean:44-54, 188-217, 226-296):
  - `Route` (`VE.Route.Wire.decodeVocabulary`): fol and closure lists, the norms route, and
    soft-norms@0, which decodes without the checker profiles (SoftNorms/Phases.lean:137-154).
    Accepted: a declared sort, or `$string` under `data@0` (Route/Wire.lean:170-172). Anything
    else: `InvalidInput` at the predicate.
  - `Order` (Route/Wire.lean:237-249, Order/Wire.lean:66-83). Accepted: a declared sort or `$int`.
    `$string`: `UnknownSymbol` at the predicate.
  - `Core` (Core/Bridge.lean:29-38): `UnknownSymbol` at the predicate.
  - `Layered` (Core/Layers.lean:64-80, 229-232), the n-ary family when a predicate carries
    `defined`, `functional` or `total`. A binary undefined predicate takes the route verdict.
    Anything the route accepts or does not read gets the core decoder's `UnknownSymbol` after the
    constants.
  - `Legacy` (`ve.core@0`, `ve.core@0.1`): `$int` under the frozen order envelope only, else
    `UnknownSymbol`.
- Each family decoder reads a predicate's and a constant's displays before their sorts. The order
  decoder refuses definitions, then checks the literals and their 64-limit, before any predicate
  (Route/Wire.lean:240-247). The norms routes over closure, n-ary or order check every regulated
  block first (`checkRegulated`, Standalone.lean:198-203). The constant-sort code is the route
  decoder's `InvalidInput` (Route/Wire.lean:196) or the shared validator's `UnknownSymbol`
  (Bridge.lean:58). soft-norms@0's phase 3 refusals follow its vocabulary
  (Phases.lean:195-203).

The DRI note's three outcomes (accepted, `UnknownSymbol` at the sort, `InvalidInput` after the
constants) do not cover Lean. Lean also reports `InvalidInput` at the sort (the route decoder) and
`UnknownSymbol` after the constants (the frozen order and n-ary lists, the layered core phase). The
table gives each of these cases, with its line in Lean.

Superseded: the orders recorded in sections 19 and 24 are now the table's. An unsupported built-in
on a composed fol list is the route decoder's `InvalidInput` at the predicate, and the exact order
list's constant-first order is the located decoder's.

### 25.2 The truth table

`test_builtin_argument_sort_truth_table_agrees_on_every_profile_list` runs on every profile list
Lean's profile table admits, 1,045 of them, plus the three frozen envelopes: 1,048 heads in all. The
lists are enumerated from `ve/profile_table.json`, which is generated from
`VE.Compose.profileTable`; none is sampled.

- **Cells.** Each head has `$int`, `$string` and a declared control. Each is tried beside no
  constant, a malformed constant and an undeclared-sort constant, unflagged, and flagged wherever
  `data@0` is listed. Each hunt form is added for both built-ins. That makes 32,976 cells, 23,265
  of them with a Rust path.
- **Assertions.** Python's code equals Lean's on every cell, and Rust's equals Lean's on every cell
  with a Rust path. The F12, F13 and F14 PROBE envelopes are cells of the table, named in
  `BUILTIN_SORT_PROBES`.
- **Exception.** Rust's own profile gate refuses lists with `acts@0`, `readings@1`, `rights@0` or
  `norm-defaults@0` (`Unsupported profile …`). For those lists the test asserts that Rust's answer
  is the same refusal in every cell, whatever the sort.

### 25.3 Seeded mutants (Rust, the one product language changed)

Each mutant was rebuilt, then run against the truth-table test, then restored (`/tmp/mut/run.py`
on `e39a10df7`):

| Mutant (file `rust/ve-kernel/src/environment.rs`) | Truth-table test |
|---|---|
| M1 the old `exact_order_route` branch seeded back into the argument loop | fails |
| M2 located faults never the answer on the frozen lists | fails |
| M3 regulated blocks checked after the sorts | fails |
| M4 a constant's sort before its displays | fails |
| M5 the order decoder's literal limit not first | fails |
| M6 the layered n-ary family read as core | fails |
| M7 soft-norms@0 phase 3 refusal dropped | fails |
| M8 the route decoder's constant fault as `UnknownSymbol` | fails |

On the first commit, M1 was also run alone: the test failed, and with the restored code it passed
(`f244f474b`). After the mutant runs the restored binary hashed to the pinned digest. The truth-table
test passed on it: 1 passed in 111.85 s.

### 25.4 Adversarial hunts

No subagent tool was available in this session. I ran both hunts myself, from the class
description, the three PROBEs, the Lean decoders and `tools/difffuzz.py`. They are not independent
of the fixer. Each hunt compared Lean and Rust on every admitted list and the frozen envelopes, and
controlled each difference with the same vocabulary over a declared sort. A difference that remains
over a declared sort is another class.

**Hunt 1**

- **Forms tried:** constants of sort `$int`/`$string`, with and without a description, or a
  non-string sort; `defined` bodies over a built-in, or beside one; `instruction_of`; ternary
  signatures with and without layers; flags without `data@0`; mixed and non-string cells; built-ins
  before and after an ordinary unknown sort; empty description, verbalisation or extra field on the
  built-in predicate; regulated built-in predicates; documents embedding the environment (the
  `requests` surface).
- **In class, fixed (`0c8f46575`):**
  - H1-a: a constant sort that is not a string is the route decoder's `InvalidInput`.
  - H1-b: the order decoders read `$string` literals first; every family decoder reads a constant's
    displays before its sort.
  - H1-d: a predicate's description and verbalisations come before its sort, on every decoder
    including the frozen ones.
  - H1-e: definitions on the order family are refused before any predicate; not under soft-norms;
    the frozen decoders have no definition field.
  - H1-f: a definition over `$string` is untyped (`InvalidInput`), not `UnsupportedProfile`.
  - H1-g: soft-norms@0 admits arity two only.
  - H1-h: the exact closure+n-ary list with a definition is layered.
- **In class, open:** H1-c (25.5).

**Hunt 2**

- **Forms tried:** two built-ins in one vocabulary; a built-in beside a ternary built-in; a
  definition elsewhere; regulated blocks on the built-in predicate and on a later one; non-Boolean
  flags; empty or non-array arguments later; seven arguments; 65 literals; a bad sort entry; `$int`
  constants; reserved predicate names; predicate-name order; defined and flagged built-ins;
  `reports@0` lists with Rust forced (36 cells, all agree).
- **In class, fixed (`76545de92`):**
  - H2-a: the order decoder's 64-literal limit comes before any predicate.
  - H2-b: the norms routes over checker lists check every regulated block before any sort.
  - H2-c: on the frozen lists a later predicate's family-only field fault followed an earlier
    built-in (2 cells). Running Lean's located decoder over predicates and constants first, with no
    after-constants deferral, fixed it.

Every fixed form is a form of the truth table (`SORT_TABLE_FORMS`) and has a Rust case.

Found, out of class (the declared-sort control differs too); pre-existing and not fixed:

| Form | PROBE envelope (environment surface) | Python / Lean / Rust |
|---|---|---|
| O1 data flags without `data@0` on the norms routes (also non-Boolean flags) | `{"language":"ve.core@0.2","profiles":["definitions@0","norms@0","relational-fol@0"],"spec_revision":"ve-v0.2-expand2-2026-09-25","vocabulary":{"sorts":{"thing":{"description":"d"}},"predicates":{"p":{"arguments":["thing","thing"],"description":"d","functional":true}},"constants":{}}}` | InvalidInput / InvalidInput / UnsupportedProfile |
| O2 ternary data flags under `nary@0` | `{"language":"ve.core@0.2","profiles":["closure@0","data@0","nary@0","relational-fol@0"],"spec_revision":"ve-v0.2-expand2-2026-09-25","vocabulary":{"sorts":{"thing":{"description":"d"}},"predicates":{"p":{"arguments":["thing","thing","thing"],"description":"d","functional":true}},"constants":{}}}` | ok / ok / InvalidInput |
| O3 an `instruction_of` party outside the soft block (Rust reads no soft block, DF-18) | `{"language":"ve.core@0.2","profiles":["data@0","norms@0","relational-fol@0","soft-norms@0"],"spec_revision":"ve-v0.2-expand2-2026-09-25","vocabulary":{"sorts":{"thing":{"description":"d"}},"predicates":{"p":{"arguments":["$string"],"description":"d","instruction_of":"alice"}},"constants":{}}}` | UnknownSymbol / UnknownSymbol / ok |
| O4 the evaluate route's profile gating and the frozen envelope in a request | 400 `requests` cells over composed lists and `ve.core@0`, the same with a declared sort | Lean refuses; Python and Rust decode |

### 25.5 Open in-class form (B)

**H1-c, a built-in sort in a request's environment.** Lean's request modes decode the environment
with the family decoder alone (`Standalone.evaluable` -> `validated`). Python validates the same
environment through Lean's `environment` mode, whose located decoder runs first. So the two Lean
modes give different first faults for one environment, with a built-in sort and also with a
declared one (`relational-fol@0` with an undeclared constant: `environment` mode `UnknownSymbol`,
request mode `InvalidInput`).

Rust follows the `environment` mode, as Python does. A Rust split by mode was built and then
reverted: it made Rust agree with Lean's request mode and disagree with Python. The fix is one
decoder order in Lean for both modes. This round does not change Lean, so the form stays open,
filed as DF-21 in `conformance/DIFFFUZZ.md`.

PROBE H1-c: `.venv/bin/python -c 'from copy import deepcopy;from tools import difffuzz as d;s=d.SURFACES["requests"]();seed=next(x for x in s.seeds() if x.id=="conformance/elaborated-document.json/11");r=deepcopy(seed.root);v=r["environment"]["vocabulary"];v["predicates"]["p"]={"arguments":["$int"],"description":"d"};v["constants"]["bad"]=[];r["environment"]["profiles"]=["closure@0","nary@0","relational-fol@0"];a=[s.python(seed,r)["code"],s.lean([(seed,r)])[0]["code"],s.rust([(seed,r)])[0]["code"]];s.close();print(a);assert len(set(a))==1'`
exits 1 with `['InvalidInput', 'UnknownSymbol', 'InvalidInput']`.

### 25.6 Delta

| Delta | Ruling | Evidence |
|---|---|---|
| Rust reports a built-in argument sort at the predicate or after the constants as the Lean decoder that judges the list does (25.1), deterministically per decoder | R2 (standing ruling, DRI-RULINGS.md) | `tests/test_difffuzz.py::test_builtin_argument_sort_truth_table_agrees_on_every_profile_list`; `rust/ve-kernel/tests/environment_definition_order.rs::builtin_argument_sort_probes_take_lean_codes` |
| Rust reports a predicate's and a constant's display faults before their sort faults | R2 (standing ruling, DRI-RULINGS.md) | the truth table's `empty-description`, `empty-verbalisation` and `literal-empty-description` forms; `::builtin_argument_sort_follows_display_and_definition_faults` |
| Rust reports Lean's located decoder faults first: all of them on the frozen checker lists, the unknown argument sort elsewhere | R2 (standing ruling, DRI-RULINGS.md) | the truth table's `malformed` and `undeclared` constants and `bad-regulated-later` form; `::builtin_argument_sort_follows_literal_limit_and_regulated_blocks` |
| On the order family Rust refuses a definition, then checks the literals and their limit, before any predicate; on the norms routes over checker lists it checks every regulated block before any sort | R2 (standing ruling, DRI-RULINGS.md) | the truth table's `defined`, `literal-limit` and `regulated` forms; `::builtin_argument_sort_follows_literal_limit_and_regulated_blocks` |

The single-fault code changes are parity with the unchanged Lean owner: a constant sort's
`InvalidInput` on the route decoder; soft-norms@0's refusal of checker lists, definitions and data
flags; the untyped `$string` definition. They are bug fixes, not deltas. Ten baseline signatures
that Rust now answers as Lean does were dropped by two `--update-baseline` passes (`e39a10df7`).

### 25.7 Commands on the final code HEAD `a75497c3d`

- `cd lean && PATH=~/.elan/bin:$PATH lake build`: `Build completed successfully (1135 jobs).`
- `python3 lean/audit.py`: `PASS: 653 source files; 7286 named theorem declarations audited`.
- `python3 tools/rust_build.py --check`: `a4ce3be4…b9921 rust/target/release/ve: pinned in lean/checkers.lock`.
  Each intermediate digest was replaced, so only the final one is pinned.
- `uv run python tools/regen_generated.py --check`: exit 0, `checked 33 entries`.
- `cargo test --locked --release --workspace` (with `tools/rust_build.py`'s Cargo environment): exit 0,
  every crate `ok`. `environment_definition_order` has 7 tests.
- `.venv/bin/python -m tools.difffuzz --ci`: `passed` true; 0 new, 0 not reproduced, 0 unreviewed.
- `usecases/openai-preparedness/{build_document,measure,stage0}.py --check`: each exit 0.
- `usecases/anthropic-rsp/{build_document,measure,stage0}.py --check`: each exit 0.
- `usecases/safety-framework/{run,build_document,readings_r1,measure_r1,measure_r2}.py --check`:
  each exit 0.
- `zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`:
  `recorded 397 units for tree a0a636e298 … 0 failed`, on ve-mac-1 (aarch64), HEAD `a75497c3` (clean),
  5,125 s, exit 0. The three `main-known-red.txt` tests are pre-existing and were not edited.
- Not run: the full suite and the release gate (`tools/gate.py`), as this round's instructions say.
