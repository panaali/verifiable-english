# Batch 16f build report

DRI attention (first line, BUILDER-CHECKLIST 7): DELTA.md row 7 asks the DRI to acknowledge the render ratio on the
two largest constitution pilots (1.34 and 1.35, +0.14 s and +0.24 s; R4 signs the absolute budgets, which hold), and
the twelve ledger cases outside every batch's groups need scheduling. Every other delta row is signed by a standing
ruling (R2, R3, R4, R7, R16) or needs none.

See [DELTA.md](DELTA.md) for the measurement, the routes the mode now calls, the binding, every delta with its ruling,
the seeded faults and what was not run.

## The task, line by line

| Directive | Delivered by | Evidence or test |
|-----------|--------------|------------------|
| Soft norms (22 pilots) decided by Lean | `softSource`, `softLayer`, `softContentOf`, soft admission in `admitGraph` (commit "the document mode composes a soft-norms@0 document from the soft route") | `evidence/cases.json.gz`: 22 ok, reports equal to the prior path's; `test_the_layer_seeds_are_decided_by_lean_with_the_retained_public_outcome[soft-norms]` |
| Norm content (18) | `contentOf`, `checkNorms`, norms admission (commit "decides plain norms@0 norm content on the norms route") | 18 ok; `test_the_layer_seeds_...[norms-content]` |
| Senses (7) | Listed with a genuine invalid-input cause (a missing sense pack file, which Python reads) | `cases.json.gz` `prior_error`: `Cannot read sense pack: [Errno 2] ...` |
| Fenced content (9; 12 with the pilots) | `locatedFence`, `fence_error` | 9 errors with the parse mode's text and span, 3 ok; `test_a_strict_fence_s_syntax_error_has_the_parse_mode_s_span` |
| Distinguishing models (26) | `locatedModel`, `model_error`, nulls inside models | 26 errors, text and path equal; `test_a_refused_distinguishing_model_is_lean_s_located_diagnostic` |
| Malformed-profile (8) and environment-key (25) groups | `environmentFault`, `undecided` | 33 errors equal to the prior path's; `test_an_environment_fault_is_the_environment_mode_s` |
| Wire it into `document` mode by calling existing Lean routes; no new semantics, no Python decisions | Every step is an existing route (DELTA.md, first section); undecidable classes fail closed | review of `git diff main...HEAD`; seeded faults |
| Measure from the residue ledger | `measure.py` (case names and source bytes checked against the 16c ledger; every case compared with the prior path) | `evidence/cases.json.gz`, `share.json`: 111/118 decided, 0 differing errors, 7 genuine invalid inputs, 0 problems |
| Corpus A/B over all nine corpora, 0 unlisted differences | `make_ab.py`, `splice_recording.py` | `evidence/ab.json`, `delta.json`, `ab-recorded.json`: 100,394 records per side, 0 unlisted |
| Fully typed response schema and request binding for every field added | `plain_error`, `model_error`, `fence_error`; `_names_a_model_member`, `_spans_a_strict_fence`, `_soft_bound`, `E″` meaning ids | `test_every_unit_field_is_typed_and_every_row_bound`, `test_the_located_error_rows_are_typed`, `test_a_model_path_is_bound_...`, `test_a_fence_span_is_bound_...`; relay gate `evidence/relay-gate.json` |
| Seeded bugs, one per language changed | `seed_faults.py` | `evidence/mutants.json`: 10/10 caught (6 Lean, 4 Python) |
| Report and evidence tests check saved evidence only | `report.py` renders DELTA.md from `evidence/`; no new permanent report test (D4) | DELTA.md metrics block |
| One owner per piece of logic | Lean decides; Python binds and builds containers; the soft rule binding reads the existing container (`SoftRule.to_dict`), no new copy | — |

## Tests and runs

- Selected tests (`mac-pytest.sh --select`, Mac runner): 350 units, 0 failures, on 38b93aaa (the final product code).
- New tests: `tests/test_b16f_document.py` (25 test functions, 60 collected cases). Changed tests: `tests/test_lean_document_wrapper.py`
  (seeds and the owned-profile and gate tests), `tests/test_document_lean_switch.py` (its retained fence now under
  `readings@1`), `tests/test_nested_pytest.py` (the seed harness is an outermost runner), and 16e's
  `test_soft_norms_is_owned_only_beneath_rights` removed (Test-removed trailer).
- `lake build` (957 jobs) and `python3 lean/audit.py` passed; `tools/regen_generated.py --check` checks 28 entries;
  `tools/trust_map.py --check` passes with the R16 allowance; `tools/gate_collection.py --check --prebuilt` passes
  after this commit's trailer.
- Main known-red tests (`main-known-red.txt`): not touched.
- The full release gate is the chain's, on the final HEAD.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: PASS — `tests/test_b16f_document.py::test_every_unit_field_is_typed_and_every_row_bound`, `test_the_located_error_rows_are_typed`; relay mutation gate on the document route, 3,199 mutants, 0 failures (`evidence/relay-gate.json`).
2. Every deliverable built, no rule broken: PASS — the table above; senses and the twelve outside cases listed with causes.
3. Tests and gates can fail: PASS — `evidence/mutants.json` 10/10 caught (6 Lean, 4 Python); the encoder theorem broke on a renamed `span` key and a `BOGUS` status (DELTA.md); `measure.py` stops on any differing or retained valid in-group case.
4. Python, Lean and Rust agree, valid inputs pass: PASS — `evidence/ab.json` (0 unlisted over nine corpora), `evidence/cases.json.gz` (0 differing errors), `evidence/difffuzz-ci.json` (0 new); seeds with keys reordered and generated-prefix names (`soft__excepted__share_rule`) in `conformance/document_wrapper.py` `_layer_seeds`.
5. R8 binding refuses undeclared names: PASS — `test_a_model_path_is_bound_to_a_member_of_a_model_of_the_document` (absent, shifted, out-of-range, leading-zero, non-ASCII digit), `test_a_fence_span_is_bound_to_a_strict_fence_of_the_document`, `test_an_empty_extra_or_duplicated_unit_row_is_refused`, `test_a_soft_meaning_id_is_bound_to_the_extended_environment`.
6. Gate evidence matches the final HEAD: PASS — main has not moved (merge base 85b20fcb); scope from `main..HEAD --no-merges` at the final code commit (`evidence/scope.json`); the chain runs the gate on the final HEAD.
7. No unsigned item: PASS — every DELTA row cites R2, R3, R4, R7 or R16, or needs none; row 7's pilot render ratio is named in this report's first line for the DRI.
8. Every user-visible change in DELTA: PASS — the A/B and the measurement diff base and head across every corpus, retained paths included (DELTA.md rows 1 to 7).
9. Test selection finds the tests: PASS — `tools/select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_b16f_document.py` and the wrapper tests; it is broad because `ve_service` changed, which nearly every unit runs.
10. Lean statements say what is claimed: PASS — `locatedRow_fits` and `runCaseReported_fits` break on a wrong row (DELTA.md); no approved statement changed (`lean/statements.txt` regenerated, only new shape theorems).
11. Budgets, limits and deadlines fail closed: N.A. — the batch adds no budget or deadline; the mode's `ResourceLimit` path is unchanged.
12. No CPU or memory regression: PASS with a DRI note — `evidence/cpu.json` (ratios 1.0 to 1.35; Lean request at most 0.279 s); R4 for the absolute budgets, row 7 for the pilot render ratio.
13. Every removed test has a Test-removed trailer: PASS — `tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
