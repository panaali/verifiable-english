# Batch 16f build report

DRI attention (first line, BUILDER-CHECKLIST 7): two signatures are needed. DELTA.md row 6: the trusted base grew by
+273 V (+142 at the build, signed by R16 and recorded; +131 for the review fixes: the senses route's composition and
the F3 speedups), over R16's 150 per item, so `tools/trust_map.py --check` fails until the DRI records the +131
allowance (the command is in row 6). DELTA.md row 7: the render ratio on the two largest constitution pilots, 1.27
and 1.22 after the F3 speedups (+0.19 s and +0.09 s; R4 signs the absolute budgets, which hold). The twelve ledger
cases outside every batch's groups need scheduling. Every other delta row is signed by a standing ruling (R2, R3, R4,
R7, R16) or needs none.

Review fixes (`lf-16f-review.final.md`): F1 (a soft-norms document's parts pre-scan raised a later unit's fault before
an earlier one's) and F2 (the senses group was measured without its pack, and the mode did not compose the senses
route) are fixed; F3's pilot render ratio is reduced and the rest is for the DRI (row 7). F4 to F6 are follow-ups.

See [DELTA.md](DELTA.md) for the measurement, the routes the mode now calls, the binding, every delta with its ruling,
the seeded faults and what was not run.

## The task, line by line

| Directive | Delivered by | Evidence or test |
|-----------|--------------|------------------|
| Soft norms (22 pilots) decided by Lean | `softSource`, `softLayer`, `softContentOf`, soft admission in `admitGraph` (commit "the document mode composes a soft-norms@0 document from the soft route") | `evidence/cases.json.gz`: 22 ok, reports equal to the prior path's; `test_the_layer_seeds_are_decided_by_lean_with_the_retained_public_outcome[soft-norms]` |
| Norm content (18) | `contentOf`, `checkNorms`, norms admission (commit "decides plain norms@0 norm content on the norms route") | 18 ok; `test_the_layer_seeds_...[norms-content]` |
| Senses (7) | `sensesLayer`, `sensesContentOf`, `frozenEnv` (the senses route composed, over the frozen `ve.core@0` envelope of all seven); Python sends the pack texts (review F2) | `cases.json.gz`: 4 ok, 1 error, 2 retained with their genuine diagnostics (an unresolved word, a sentence with no reading); `tests/test_b16f_senses_document.py` |
| Fenced content (9; 12 with the pilots) | `locatedFence`, `fence_error` | 9 errors with the parse mode's text and span, 3 ok; `test_a_strict_fence_s_syntax_error_has_the_parse_mode_s_span` |
| Distinguishing models (26) | `locatedModel`, `model_error`, nulls inside models | 26 errors, text and path equal; `test_a_refused_distinguishing_model_is_lean_s_located_diagnostic` |
| Malformed-profile (8) and environment-key (25) groups | `environmentFault`, `undecided` | 33 errors equal to the prior path's; `test_an_environment_fault_is_the_environment_mode_s` |
| Wire it into `document` mode by calling existing Lean routes; no new semantics, no Python decisions | Every step is an existing route (DELTA.md, first section); undecidable classes fail closed | review of `git diff main...HEAD`; seeded faults |
| Measure from the residue ledger | `measure.py` (case names and source bytes checked against the 16c ledger; every case compared with the prior path; a pilot written with the files it names) | `evidence/cases.json.gz`, `share.json`: 116/118 decided, 0 differing errors, 2 genuine invalid inputs, 0 problems |
| Corpus A/B over all nine corpora, 0 unlisted differences | `make_ab.py`, `splice_recording.py`; the recorder writes a pilot with its files (`write_pilot`) | `evidence/ab.json`, `delta.json`, `ab-recorded.json`: 100,394 records per side, 100,386 the same, 8 unavailable on both sides (R7), 0 unlisted, 0 wording |
| Fully typed response schema and request binding for every field added | `plain_error`, `model_error`, `fence_error`; `_names_a_model_member`, `_spans_a_strict_fence`, `_soft_bound`, `E″` meaning ids | `test_every_unit_field_is_typed_and_every_row_bound`, `test_the_located_error_rows_are_typed`, `test_a_model_path_is_bound_...`, `test_a_fence_span_is_bound_...`, `test_a_fence_the_route_read_keeps_its_formula`; relay gate `evidence/relay-gate.json` |
| Seeded bugs, one per language changed | `seed_faults.py` | `evidence/mutants.json`: 18/18 caught (10 Lean, 8 Python) |
| Report and evidence tests check saved evidence only | `report.py` renders DELTA.md from `evidence/`; no new permanent report test (D4) | DELTA.md metrics block |
| One owner per piece of logic | Lean decides; Python binds and builds containers; the soft rule binding reads the existing container (`SoftRule.to_dict`), no new copy | — |

## Tests and runs

- Looprecheck1 fix (F7), selected tests (`mac-pytest.sh --select`, Mac runner) on f343e11e (the final code commit):
  358 units, the same 1 failure, `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check` (DELTA row 6,
  no Lean change in this round). New: `tests/test_b16f_senses_document.py::test_a_fence_the_route_read_keeps_its_formula`
  (4), `::test_a_fence_the_route_read_to_no_formula_has_no_content`,
  `::test_every_mutant_of_a_senses_answer_is_refused_or_changes_nothing` (2) and
  `tests/test_relay_mutation_gate.py::test_document_is_read_as_ve_document_reads_it` (3); four seeded faults added
  (`seed_faults.py ve/document.py tools/relay_mutation_gate.py` reran the Python ones, the Lean records kept).
- Review fixes, selected tests (`mac-pytest.sh --select`, Mac runner) on 378fabde (the final code commit): 358 units,
  1 failure, `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check`: the trust growth over R16 (DELTA
  row 6), which passes once the DRI records the allowance. An earlier selected run on 769fc7c3 found four more,
  fixed in 378fabde (b16b's seeded senses fault, a pilot recorder test, two tests that patch the senses route's
  `_text`).
- New tests: `tests/test_b16f_senses_document.py` (59 collected: the seven senses documents on both envelopes, every
  senses fault, the request's pack texts, the projected-environment binding, the recorder writing a pilot with its
  files) and `tests/test_b16f_document.py::test_a_later_unit_s_structural_fault_comes_after_an_earlier_unit_s_fault`
  (F1, five seeds by 30 fault pairs). Changed: `tests/test_document_lean_switch.py` (the senses retained reason,
  Test-removed trailer in e415011e). Build: `tests/test_b16f_document.py` (25 test functions), the wrapper tests, and
  16e's `test_soft_norms_is_owned_only_beneath_rights` removed (Test-removed trailer).
- `lake build` (957 jobs) and `python3 lean/audit.py` passed on 378fabde; `tools/regen_generated.py --check` passes
  every entry but `trust-tables` (row 6, the DRI's signature).
- Probes: PROBE F1 failed before the fix ("MIXED unit needs partitioned parts" against "invalid support") and passes
  after. PROBE F2 as written calls `_lean_answer(raw, True)` without the document's directory, so the pack beside it
  cannot be read and it still fails; with the directory (`_lean_answer(raw, True, p.parent)`, as `load_document`
  calls it) it passes; `test_a_valid_senses_document_is_decided_by_lean` is its regression test.
- Main known-red tests (`main-known-red.txt`): not touched.
- The full release gate is the chain's, on the final HEAD.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: PASS — `tests/test_b16f_document.py::test_every_unit_field_is_typed_and_every_row_bound`, `test_the_located_error_rows_are_typed`; `tests/test_b16f_senses_document.py::test_every_mutant_of_a_senses_answer_is_refused_or_changes_nothing`, `test_a_fence_the_route_read_keeps_its_formula` (looprecheck1 F7); relay mutation gate on the document route, read through `_lean_document`, 3,661 mutants, 0 failures (`evidence/relay-gate.json`).
2. Every deliverable built, no rule broken: PASS — the table above; the senses group is composed (review F2: the build's "missing file" was its own measurement writing each pilot alone); the two retained senses documents and the twelve outside cases are listed with causes.
3. Tests and gates can fail: PASS — `evidence/mutants.json` 18/18 caught (10 Lean, 8 Python); the encoder theorem broke on a renamed `span` key and a `BOGUS` status (DELTA.md); `measure.py` stops on any differing or retained valid in-group case.
4. Python, Lean and Rust agree, valid inputs pass: PASS — `evidence/ab.json` (0 unlisted over nine corpora), `evidence/cases.json.gz` (0 differing errors), `evidence/difffuzz-ci.json` (0 new); seeds with keys reordered and generated-prefix names (`soft__excepted__share_rule`) in `conformance/document_wrapper.py` `_layer_seeds`.
5. R8 binding refuses undeclared names: PASS — `test_a_model_path_is_bound_to_a_member_of_a_model_of_the_document` (absent, shifted, out-of-range, leading-zero, non-ASCII digit), `test_a_fence_span_is_bound_to_a_strict_fence_of_the_document`, `test_an_empty_extra_or_duplicated_unit_row_is_refused`, `test_a_soft_meaning_id_is_bound_to_the_extended_environment`.
6. Gate evidence matches the final HEAD: PASS — main has not moved (merge base 85b20fcb); scope from `main..HEAD --no-merges` at the final code commit (`evidence/scope.json`); the chain runs the gate on the final HEAD.
7. No unsigned item: FAIL, two DRI signatures — row 6's trust growth over R16 (+131 of +273) and row 7's pilot render ratio; both are named in this report's first line. Every other row cites R2, R3, R4, R7 or R16, or needs none.
8. Every user-visible change in DELTA: PASS — the A/B and the measurement diff base and head across every corpus, retained paths included (DELTA.md rows 1 to 8).
9. Test selection finds the tests: PASS — `tools/select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_b16f_document.py` and the wrapper tests; it is broad because `ve_service` changed, which nearly every unit runs.
10. Lean statements say what is claimed: PASS — `locatedRow_fits` and `runCaseReported_fits` break on a wrong row (DELTA.md); no approved statement changed (`lean/statements.txt` regenerated, only new shape theorems).
11. Budgets, limits and deadlines fail closed: N.A. — the batch adds no budget or deadline; the mode's `ResourceLimit` path is unchanged.
12. No CPU or memory regression: PASS with a DRI signature pending — `evidence/cpu.json` (ratios 0.97 to 1.27 after the F3 speedups; Lean request at most 0.253 s); R4 for the absolute budgets, row 7 for the pilot render ratio.
13. Every removed test has a Test-removed trailer: PASS — `tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
