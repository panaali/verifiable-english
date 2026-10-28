# usecase-safetyfw: three frontier-lab safety frameworks in VE (build report)

- **Status:** parts 1, 2, 3 and 5 done; part 4 (the openai-preparedness baseline) is cut for size and named
  `usecase-safetyfw-b`. No DRI signature is reserved, no DELTA row, trust +0 (no Lean file changed).
- **HEAD:** the branch tip; original baseline code at 18e9c937d, source-coverage correction at 92a2fd643
  (base main 6d0a10526).
- **What changed:** both frozen keys transcribed and pinned; fsf-r2 re-measured the DeepMind case (no byte moved
  since Oct 18) with one probe per merged item; anthropic-rsp has its corrected baseline: 59,410 bytes in 303 units,
  9.0% CHECKED, with stage 0 and the gaps by feature family.
- **Open items:** `usecase-safetyfw-b`, `usecase-rsp-run`, `usecase-pf-run`, `fsf-r3`. No key finding.

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
| 4. openai-preparedness baseline | **not here**: `usecase-safetyfw-b` (size rule; section 6) | | |
| 5. README per new case; this REPORT | anthropic-rsp/README.md (with today's numbers), openai-preparedness/README.md (status only) | d78e9b9d9, this commit | |

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
| OpenAI PF v2 | not measured (`usecase-safetyfw-b`) | | | | | 67,418 |

Sources: [fsf-r2/gaps.json](../safety-framework/fsf-r2/gaps.json) (`master_bytes_by_status`, oct1, oct18 and
today) and [anthropic-rsp/gaps.json](anthropic-rsp/gaps.json). Both plans expected a CHECKED share under 10%.

The RSP has more OPEN and less UNFORMALISED text than the FSF. Its open terms are named on the rules
themselves (28 records), and most of its process sentences are commitments without an open term in their guards (34
CHECKED rules). The DeepMind framework has more process wording ("periodically", "this will inform") that has no rule.

The 3.6.1 paragraph was overcounted as CHECKED: its organization financial-interest rule covered the first 95
bytes, while the next 324 bytes also prohibit financial interests of individual reviewers and their reporting chain,
and close personal relationships. Those two clauses now have separate UNFORMALISED units (182 and 142 bytes) waiting
for SC. The frozen key, including K13, is unchanged. This corrects use-case source coverage; no Lean checker verdict
or diagnostic changed (`test_rsp_reviewer_prohibitions_are_separate_coverage_units`).

## 4. What the bytes that are not CHECKED wait for, all three frameworks, ranked by bytes

A unit counts under every family it waits for; "alone" counts the units with that one blocker. DeepMind's features
(fsf-r1's names) are mapped to families in `measure_r2.FAMILIES`; anthropic-rsp's units carry families directly
(`measure.py`). OpenAI: not measured.

| Family | DeepMind: units, bytes | alone | Anthropic: units, bytes | alone | Both: bytes | alone |
|---|---|---|---|---|---|---|
| no claim to check | 165, 29,619 | 29,619 | 130, 31,104 | 31,104 | 60,723 | 60,723 |
| JT judgment terms | 36, 7,976 | 5,114 | 50, 11,372 | 6,892 | 19,348 | 12,006 |
| AT attitudes (beliefs, expectations, aims, hedges) | 31, 5,617 | 5,617 | 43, 6,510 | 6,510 | 12,127 | 12,127 |
| readings (readings differ in which rules hold) | 18, 3,597 | 735 | 17, 3,989 | 2,106 | 7,586 | 2,841 |
| ET time and process wording | 11, 2,212 | 2,212 | 7, 1,390 | 489 | 3,602 | 2,701 |
| external reference | 7, 1,978 | 1,978 | 6, 797 | 797 | 2,775 | 2,775 |
| SC scope (addressee, existential import) | 2, 283 | 283 | 9, 1,935 | 693 | 2,218 | 976 |
| DF defaults | 2, 551 | 551 | 4, 866 | 405 | 1,417 | 956 |
| WG weighing and causation | 3, 807 | 807 | 2, 551 | 551 | 1,358 | 1,358 |
| QT quantities | 0, 0 | 0 | 2, 105 | 0 | 105 | 0 |
| AP act phrases | 0, 0 | 0 | 0, 0 | 0 | 0 | 0 |

Among the families with a claim to check, JT is first in both texts, then AT. JT's landing (`judgments@0`) moves no
byte to CHECKED, because a judged unit stays OPEN by theorem (fsf-r2). The "alone" column is the most a family's
landing can move, since those units wait for nothing else: AT 12,127 B, external references 2,775 B (if the
referenced documents are translated), ET 2,701 B, WG 1,358 B, DF 956 B, SC 976 B. Whether a unit then becomes
CHECKED depends on how the feature represents it, and this item does not measure that. In the RSP, QT appears only
with JT (`t4-cost-factor`) or ET (the 3-6 month cadence).

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

None. No step of the translation contradicted a key cell of either plan, and no key cell was edited. The baseline
answers no key item (that is `usecase-rsp-run`), so a disagreement can still appear there.

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
| `usecase-safetyfw-b` | Part 4: the openai-preparedness baseline by its PLAN 7 to 10 (vocabulary and D1 to D3, rules and premises with sources, the span accounting over 67,418 bytes, stage 0 P1 to P8, the measure). Reuse anthropic-rsp's `build_document.py` W2-set builder, `stage0.py` (part documents, D2, D3, lint, audit) and `measure.py` by import. Factor the shared parts into one module when the second case imports them |
| `usecase-rsp-run` | `run.py`: cases.json's situations as atoms over the D1 vocabulary; per-choice expansion of `build_document.READINGS` (a reading's rules, premises and `case:` premises); both completion defaults; S from P3's tables, D from P4 (with checked countermodels for D3a and D6a, and RS9 in D3 with a day-count bridge), T5's cost factor in D3; `reference.py` (A, B, C, G from PLAN 3 and 4 alone); results.json; M1, M2, M4, M7 to M10; mutants m1 to m6; fsf-r1's content-bearing sets for the sets whose readings are each one rule (RS8, RS12, RS13, RS6) |
| `usecase-pf-run` | the same for openai-preparedness, after `usecase-safetyfw-b` |
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

Product code in the reviewed sense: Python under `tools/` (`difffuzz_corpus.py`, one registry entry; bug 4). No
Lean or Rust file changed.

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
