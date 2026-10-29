# usecase-safetyfw: three frontier-lab safety frameworks in VE (build report)

- **Status:** the OpenAI baseline has two coverage corrections; completion of its planned D1–D3 translation remains open. No DRI signature is reserved; trust +0 (no Lean file changed).
- **HEAD:** the branch tip; original baseline code at 18e9c937d, source-coverage correction at 92a2fd643
  (base main 6d0a10526).
- **What changed:** the frozen keys and DeepMind/Anthropic baselines from the parent item remain; OpenAI now has
  67,418 bytes in 389 units, 0.7% CHECKED, stage 0 P1–P8 and gaps by feature family.
- **Open items:** completion of the OpenAI translation before `usecase-pf-run`, `usecase-rsp-run`, `fsf-r3`.
  No key finding.

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
| OpenAI PF v2 | Oct 29 (clause and label audit) | 170 (0.3%) | 5,446 (8.1%) | 5,327 (7.9%) | 56,475 (83.8%) | 67,418 |

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
| readings | 3,597 / 735 | 3,989 / 2,106 | 13,372 / 12,489 | 20,958 / 15,330 |
| JT | 7,976 / 5,114 | 11,372 / 6,892 | 4,157 / 1,613 | 23,505 / 13,619 |
| AT | 5,617 / 5,617 | 6,510 / 6,510 | 12,973 / 12,386 | 25,100 / 24,513 |
| ET | 2,212 / 2,212 | 1,390 / 489 | 8,086 / 6,071 | 11,688 / 8,772 |
| external reference | 1,978 / 1,978 | 797 / 797 | 309 / 309 | 3,084 / 3,084 |
| DF | 551 / 551 | 866 / 405 | 1,185 / 0 | 2,602 / 956 |
| SC | 283 / 283 | 1,935 / 693 | 4,457 / 4,341 | 6,675 / 5,317 |
| WG | 807 / 807 | 551 / 551 | 183 / 0 | 1,541 / 1,358 |
| QT | 0 / 0 | 105 / 0 | 702 / 305 | 807 / 305 |
| AP | 0 / 0 | 0 / 0 | 20,766 / 20,766 | 20,766 / 20,766 |

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

F1 remains open. The D1 document still lacks F5/F6/F11/F12/F17 per-choice rules. Its former generic
`not_translated` backlog is classified by immediate blocker, but those source claims remain unformalised.
D2 still omits Table 1 causal cells; D3 still omits the ratio, severity quantities and remaining date
bridges. The sparse translation cannot be reported as a completed PLAN 7 deliverable, and no DRI ruling signs a
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
