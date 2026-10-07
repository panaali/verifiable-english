# English in Lean S3: integration report

Status: **the spec fixture slice passes with its two approved dispositions; G3 and GE2 remain open**.
This report joins `english-lean-s3/py` and `english-lean-s3/lean` on
`english-lean-s3/integrate`. Python remains the admission authority; D9 changes the accepted risk wording
and selected lexicon identity. No model call was made. The case records are
`conformance/english-lean/s3-python-report.json` and
`conformance/english-lean/s3-fixture-comparison.json`.

## Integrated work

The Python branch supplies the generated `order@0` and `alternatives@0` tables, the Python
severity wording, 163 spec fixture outcomes, and the dispatched-boundary comparator. The Lean
branch supplies the staged reader, real JSON profile boundary, actions, ten approved proofs,
profile guards and exact-statement check. The merge uses the generated staged catalogue and
tables with the completed Lean actions. `tools/english_grammar_gen.py --check`,
`tools/check_english_s3_statements.py`, `lake build`, `lean/audit.py`, and the focused
`tests/test_english_lean_s3.py` and `tests/test_english_lean_s3_compare.py` pass. The Lean audit
finds only the standard axiom allowlist and no `sorry` in the changed modules. Frozen source,
assurance, declaration and gate collection inventories were regenerated; the corpus seal now
reports zero drift.

## Measured fixture differences

### Risk surface delta (DRI ruling 2)

| Before S3 D9 | After S3 D9 |
|---|---|
| `Catastrophic is more severe than minor.` was rejected by Python | Python accepts it as `risk__more_severe(catastrophic, minor)`; Lean reads the same formula (`ri7`) |
| The `asimov-extended` lexicon failed V1 for missing `risk__more_severe` | The selected lexicon includes the wording and passes V1; its `lexicon_id` changes from `baef1a705ac0ebe43a084d91cf1bedf6ade5da1610acaf96fe412980ac23e753` to `833cf8d5d499d31d9567cd6030037e568a90e38458fbe958985053f2b376b225` |

The refreshed lexicon report derives validity over all 39 corpus environments, and
`test_every_corpus_environment_has_a_valid_selected_lexicon` verifies the complete report. This surface
change was signed in S3 D9; S0/S1's unchanged-behavior merge scope does not govern S3.

The submitted-environment boundary repair changed `Run.lean`, so the English grammar lock requires
`actions_version` 9 (formerly 8). The regenerated 200-case comparison records version 9 for
every case; the version identifies the changed reader even where its verdict is unchanged.

Python agrees with the spec's mapped class, formulas, and marks on 147 of the 163 exact texts. All 16 exact-text
differences agree when written with Python's selected wording. Python selects the quoted fallback for `safe`
under `FA` and `FR`, because its declared `{0} is safe` collides with the fixed role wording; it selects `C`
instead of `A` as the action letter under `FA`. These are findings against the hand-written spec lexicons,
not hidden fixture passes.

The integrated fixture comparison has 200 cases, including 37 selected-wording variants. It records 198 agreements
and 2 differences, both dispositioned, with zero unexplained differences. The hand parser and Lark
were run independently for each case; their outcomes are saved beside the dispatched Python and
Lean results in each case record. The two differences are `or38a` and `or38b`, the mixed-fault depth
precedence of spec 2.11/Q11: Python returns `ResourceLimit` and Lean returns `NoDerivation`.

| Environment | Cases | Agree | Differ | Current Lean result |
|---|---:|---:|---:|---|
| `FO` | 57 | 55 | 2 | `or38a`, `or38b` dispositioned |
| `FO+cap` | 3 | 3 | 0 | Same outcomes |
| `FD` | 24 | 24 | 0 | Same outcomes |
| `FA` | 68 | 68 | 0 | Same outcomes |
| `FA2` | 8 | 8 | 0 | Same outcomes |
| `FR` | 35 | 35 | 0 | Same outcomes |
| `FM` | 5 | 5 | 0 | Same outcomes |

`tests/test_english_lean_s3_compare.py::test_committed_report_counts_are_derived_from_individual_records`
and `::test_spec_report_numbers_follow_the_committed_case_records` recompute these counts from case rows.
The independent hand and Lark outcomes are recorded even when the dispatched Python path refuses
an otherwise grammatical text.

## Open gates and ownership

| Acceptance item | Tag | State and owner |
|---|---|---|
| S3 profile reader, approved statements, and spec fixture comparison | AGENT | Done; integration worker. `tests/test_english_lean_s3.py`, `tests/test_english_lean_s3_compare.py`, and Lean profile guards. |
| G3 sealed core, reverse grammar, lexicon mutation, use-case and pilot comparisons, and latency | AGENT | Open; integration worker. The fixture slice alone does not establish G3. |
| E2.0–E2.4 service modes, V6, Lean `admit` relay, authority flip and deletion ledger | AGENT | Open; integration worker. Lean proves `admit`, but the route does not expose it and `english.admission` remains Python authority. |
| Bounded DRI recheck of changed spec statements and any verdict or availability delta | HUMAN | Deferred; DRI. No theorem statement was changed by the merge. |
| Full GE2 corpus and historical pilot inputs | EXTERNAL | Deferred; corpus and pilot owners. |

The fixture comparison is three-reader evidence for spec section 8. It does not claim the
57,765-text core comparison, GE2 corpus A/B, a deletion ledger, or service latency.

## Seeded bugs

Each temporary mutation to `conformance/english_lean_s3_compare.py` made the named test fail;
the file was restored after each mutation and the six comparison tests then passed.

1. Accept an empty corpus: `test_comparison_refuses_an_empty_corpus` failed.
2. Give every difference a blanket disposition: `test_comparison_detects_an_accepted_sentence_changed_to_no_reading` failed.
3. Ignore the response row ID: `test_comparison_rejects_a_response_for_a_different_request` failed.

## Build checklist

The numbers are the lines of `manage-agents/prompts/build-checklist.txt`. “Open” is an unmet
requirement, not an exception to G3 or GE2.

| Line | Status | Evidence or remaining work |
|---:|---|---|
| 1 | Open | E2's generated diagnostic code/text/phase table is not implemented. |
| 2 | Open | Three readers run independently on every spec fixture; one- and two-fault differential fuzz over the larger corpus is missing. |
| 3 | Open | Normalization variants are not checked across every parser and entry point. |
| 4 | Done | The route response validator checks schema, IDs, counts, trees and bool-for-int; response mutation tests pass. |
| 5 | Open | Profile and unit malformed declarations are tested, but all-node mutation through every decoder is not complete. |
| 6 | Open | English reader has distinct outcome states; budget-zero coverage of every public operation is incomplete. |
| 7 | Open | The comparator has a route timeout; whole-operation injected-delay tests remain. |
| 8 | Not applicable | No kind or owner fold was changed. |
| 9 | Open | Lean unique-reading proofs and profile fixtures pass; full render/parse coverage over the sealed corpus is missing. |
| 10 | Open | The E2 single `admit` relay across all entry points is not built. |
| 11 | Done | The new comparator uses JSON and the real parsers; it adds no regex language parser. |
| 12 | Not applicable | No state machine or ledger was added in this integration. |
| 13 | Done | The three seeded bugs above each failed a targeted test and were removed. |
| 14 | Done | The clean-HEAD gate uses its environment allowlist and rebuilt, hashed binaries; comparison writes deterministic records. |
| 15 | Done | Requests bind six identities and response validation checks them and the row ID. |
| 16 | Open | Generated tables, inventories, collection and corpus seal are current; the trust-map budget still needs disposition for the merged trusted surface. |
| 17 | Done for agent check | Ten statements match approved text; the bounded DRI recheck is deferred to its owner. |
| 18 | Done | Lean profile guards and proofs cover the spec fixture directions and boundaries. |
| 19 | Not applicable | No use-case formalisation rule was added. |
| 20 | Open | Fixture report numbers are tested from case rows; final gate metrics and G3/GE2 claims are not yet published. |
| 21 | Done | Every acceptance item above has an AGENT, HUMAN or EXTERNAL owner. |
| 22 | Open | Final clean-HEAD full gate and disk check belong to the final handoff. |
