# Lean first batch 18: the cleanup batch

**DRI signature needed for DELTA row L1 (L52: the reason this item stops):** the agent-policy harness's
`check.py base` runs at 1.42× the base wall time (median of three paired runs; child CPU 1.18×; identical
output). The use-case harness row allows 1.25×. Every other DELTA row is signed by a standing ruling.

**Scope.** Plan row 18 and the DRI's 2026-10-14 addition (`prompts/lf-18-task.txt`): one `VE/Limits.lean`;
Python reads the I/O caps from the service handshake; one Python error class per Lean code; the `python`
authority and `VE_AUTHORITY_OVERRIDES` removed; assist and Cedar decisions through Lean replay; the assurance
manifest updated. Removing the `python` authority moves to Lean the last three operations it still decided by
default: `evaluate`, `countermodel_check` and model validation. That needed batch 15a's metered evaluator as a
service mode: the one-shot `ve_metered` costs 94 ms a call, the service mode 1.9 ms (measured on the closure
fixtures).

## Deliverables

| Plan row 18 / DRI addition | Delivered | Commit | Tests |
|---|---|---|---|
| One `VE/Limits.lean` (six copies of `maxNodes`) | `lean/VE/Limits.lean` owns the envelope limits. The six `maxNodes` copies, three `maxDepth`, two `maxSourceBytes`, two `maxPredicates`, `maxSorts`, `maxIndex`, `maxEvaluations`, `maxNumeralChars` and the service's `maxLineBytes`/`maxCases` became `export VE.Limits (...)`: one definition each, and the qualified names resolve to it. After review F2 every non-frozen check reads `VE.Limits` (146 literal sites in 53 files), and the limits are reducible so approved statements that name a value still hold of the checks. The hash-frozen decoders (`VE.Json`, `VE.Bridge`, `VE.Order.Wire`, `VE.CertificateWire`), the grammar-locked English lexer and the generated wire-contract name classes keep their literals; `VE/LimitTies.lean` `#guard`s each against `VE.Limits`, at the limit and one past it (node totals, depth, sorts, predicates, entities, the JSON caps), and `VE/WireContract/Hooks/Norms.lean` the name classes. | `f98bd6f2`, `f1acf6b3` | `lake build` (the `#guard`s), `test_handshake`, `tests/test_lean_limits.py` |
| Python reads I/O caps from the service handshake | The handshake states every limit (`VE.Limits.stated`), and `envelope.json` pins each as a `const` (three were `minimum` before). `ve/limits.py`, `lean_service.py`, `rust_jsonl.py` and `surface/time.py` read them from there; no Python copy is left. A service that states other limits, or omits one, is refused at start. | `f98bd6f2` | `tests/test_lean_service.py::test_handshake` (live service against `ve.limits`' names), `test_bad_or_missing_handshake_is_unavailable[large-limits]`, `[missing-limit]` |
| One Python error class per Lean code | The shadowed duplicate `CheckerUnavailable(VEError)` is deleted. `AdmissionError` moves into `ve/errors.py` (`ve.admission` re-exports it). `relay.CLASSES` is derived from each class's own `code`, checked against the handshake's code list, instead of a hand table. `VEError` is `InvalidInput`'s class, as Lean's English route names it. | `f98bd6f2` | `tests/test_relay.py::test_each_code_has_exactly_one_class_in_ve_errors`, `test_one_class_per_code_of_the_service` |
| `python` authority and `VE_AUTHORITY_OVERRIDES` removed | `ve/backends/dispatch.py` went from 285 to 38 lines. Deleted: the `python`, `shadow` and `rust-experimental` authorities, `VE_AUTHORITY`, `VE_AUTHORITY_OVERRIDES`, `pinned`, `composed`, `execute`, `shadowed` and the shadow log. `evaluate`, `countermodel_check` and `model_validation` join `LEAN_OWNED` and run through `owned()`. The `VE_AUTHORITY == "python"` refusals in `risk.py` and `alternatives.py` and the English override are gone. The English comparator's record writer moved to `english_lean.py`, its one user. The countermodel route is sent the model environment (`background_environment`), so environments with an `alternatives` block keep their answer. | `dadfec02`, `1e7cfd19` | `tests/test_stage2_dispatch.py::test_no_setting_selects_an_authority` (four leftover settings), `tests/test_single_owner.py`, `tests/test_model_environment.py` |
| (needed by the removal) the metered evaluator in the service | Service mode `metered`, pinned by `runMode_metered`. `MeteredTrace` builds a typed `Trace` and writes it as preorder rows, so `metered.json` needs no recursive shape. An evaluation is one of three typed results (Satisfied/true, Violated/false, ResourceLimit/null). `ResponseShape.Encoders.Metered.runCaseReported_fits` proves every row fits the shape. Python sends both case kinds to the service and binds the answer's alternative to the kind it sent; `evaluate._explanation` rebuilds the tree and refuses rows that are not exactly one tree, and a trace binding whose sort or entity the case's model does not hold (review F1, R8 (b)). | `dadfec02`, `7e63113f`, `50642ad6` | `tests/test_metered_lean.py` (traces of all four families against Python's; malformed rows; wrong-kind answers), `tests/test_metered_answer.py` (binding mutants), relay gate `service:metered`: 1,216 mutants, 1,200 refused, 16 listed (B4, B10, F11) |
| Assist `_decide`, `_entails` and Cedar allow/deny through Lean replay (plan rows marked 18) | Already delivered by batch 17 (`19c5bbe69`, merged). The `pinned("lean")` wrappers they used went with the authorities. | — | `tests/test_b17_owner.py` (6 pass on this HEAD) |
| Assurance manifest updated | `evaluate` and `countermodel.check` are `migrated`: their entries relay Lean (`semantic_entry(..., engine="lean")`). The metered bindings name `ve_service metered`. The one-shot call sites and the shadow handler's review entry are gone. `docs/spec/assurance-manifest.md` is regenerated. | `2f66d1ab`, `8c52e0c0` | `tests/test_assurance_manifest.py` (137) |
| Delete the duplicates | The Python constants in `limits.py`, the dispatch shadow and authorities, the duplicate error class and the hand class table, the six Lean limit copies, the one-shot `ve_metered` readers and the relay-gate allow entry F8 (fixed by the typed shape). | all | — |

Costs of relaying every evaluation (`1ffcda5f`): each model and formula object is encoded once and wire-checked
once. The cache is keyed by the object itself, never by the identities a model claims; a forged `model_id` is
refused (`test_a_cached_model_encoding_never_stands_for_another_model`). The lone-surrogate check now uses one
compiled character class (equivalent on 20,007 strings). The validation cache key hashes an encoded object's
exact text.

Left open: the assurance manifest still marks the batch-13b operations `authority: python` (FOLLOW-UPS lf-18
F1). Each keeps a retained Python branch for inputs outside its Lean scope, so those branches must be named
before `migrated` fits. About 20 test functions still loop over `VE_AUTHORITY` values, a setting nothing reads
any more; their operations have been Lean-owned since batches 12b and 13b (F2). `ve_metered` stays built, as a
test oracle only.

## Lines

`evidence/scope.json` holds the commit list and per-file numbers of `main..HEAD --no-merges` at code head
`cd400d7a`; base `ffb3155a5`. Changes since then are this report, DELTA, the evidence, the trust allowance, the
manifest's `other_json` entry for `ResponseShape/Schemas/Metered.lean` and the mutant runner's pytest builder
(`570725fb`; their tests pass: `test_assurance_manifest.py`, `test_nested_pytest.py`).

- `ve/` Python: +369 −483 (net −114; `dispatch.py` −265).
- Lean written by hand (generated `Audit.lean` excluded): +335 −54. New files: `VE/Limits.lean` 51,
  `VE/LimitTies.lean` 27, `ResponseShape/Schemas/Metered.lean` 78, `ResponseShape/Encoders/Metered.lean` 81.
- Tests: +437 −668.

## Gate evidence (section 5.1)

| Item | Result | Evidence |
|---|---|---|
| Corpus A/B | 100,410 records over every corpus of `tools/lean_first_diff.py`, recorded on the final code: 100,398 identical, 12 unavailable on both sides with identical outputs (R7). `compare --delta DELTA.json` exits 0. Pilots that the 600 s recorder limit cut on one side under load were re-recorded on both sides together (DELTA.md). | `evidence/ab.json`, `base-ab.jsonl.gz`, `head-ab.jsonl.gz`, `ab-initial.json`, `pilot-rerun.json` |
| Difffuzz baseline does not grow | CI sample on the head: 242 baseline entries, 0 new, 0 not reproduced. Paired base and head over the CI sample and 14 date seeds: all 15 pairs equal, with no head-only and no base-only signature. | `evidence/difffuzz-ci.json`, `difffuzz-ab.json` (`difffuzz_ab.py`) |
| Relay mutation gate | 42 routes, 131,278 mutants, 0 failures on the review-fixed code (fields are now mutated 7 levels below a service row, as below a one-shot row; review F1). | `evidence/relay-gate.json` |
| Latency | UDHR document 0.94× and eligibility 0.72× of the base wall. Agent-policy `check.py base` 1.42× wall and 1.18× child CPU (DELTA L1); the whole harness was 1.23× when run concurrently with the base. | `evidence/latency.json` (batch 13b's script), `agent-policy-concurrent.json` |
| Trust budget | V +34, S −3, K +0 (DELTA T1, R16); the allowance is recorded in `docs/trust-baseline.json`; `trust_map.py --check` passes. | — |
| Build and generated files | `lake build` (965 jobs) passes. `tools/regen_generated.py --check` passes except trust-tables before the allowance. `rust_build.py --check` passes (Rust unchanged). | — |

The selected tests (Mac runner, `--maxfail 0`) were run during the work, and every failure they found is fixed;
the chain's full gate on the final HEAD decides. Pre-existing failures on main (`main-known-red.txt`: the two
sub-tick deadline tests and `test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target`)
are not touched.

Not run: the agent-policy `replay` part, and the 1,000-document rights and soft-norm differentials beyond the
A/B's own corpora.

## Seeded bugs

`evidence/mutants.json` (`seed_mutants.py`; the Lean mutants were run by hand and are recorded there). Each was
removed, and its test passed again.

| Language | File | Seeded bug | Test that failed |
|---|---|---|---|
| Lean | `lean/VE/Route/MeteredTrace.lean` | `Trace.rows` counts one child too many | `tests/test_metered_lean.py::test_budgeted_values_counts_and_traces_match_python`, `tests/test_stage2_evaluation.py::test_traced_evaluation_matches_python` (18 failed: "names children past its end") |
| Lean | `lean/VE/Service/Protocol.lean` | the handshake omits `max_nodes` | `tests/test_lean_service.py::test_handshake`; the full build also fails at the handshake `#guard` |
| Lean | `lean/VE/Route/MeteredTrace.lean` | `Row.json` renames `children` | the build of `ResponseShape.Encoders.Metered` fails (`row_fits`); BUILDER-CHECKLIST 10 |
| Python | `ve/backends/lean_runner.py` | model encodings keyed by the claimed `model_id` | `test_a_cached_model_encoding_never_stands_for_another_model` |
| Python | `ve/errors.py` | a second `CheckerUnavailable(VEError)` class | `tests/test_relay.py::test_each_code_has_exactly_one_class_in_ve_errors` |
| Python | `ve/evaluate.py` | `VE_AUTHORITY=python` answers with Python's evaluator | `tests/test_stage2_dispatch.py::test_no_setting_selects_an_authority` |
| Python | `ve/limits.py` | `MAX_DEPTH` read from `max_nodes` | `tests/test_lean_service.py::test_handshake` |
| Python | `ve/evaluate.py` | trace rows outside the tree accepted | `tests/test_metered_lean.py::test_explanation_rows_must_be_exactly_one_tree` |
| Python | `ve/backends/lean_runner.py` | a metered answer's kind not bound to the case | `tests/test_metered_lean.py::test_a_metered_answer_of_the_other_kind_is_no_answer` |
| Python | `ve/search.py` | the countermodel route sent the whole environment | `tests/test_model_environment.py::test_search_status_and_comparison_answer_as_the_base_did` |

AGENT: everything above. HUMAN: the DRI's decision on DELTA L1. EXTERNAL: none.

## Sibling lessons (lf-16g review)

F1 (numbers re-measured, not cited): every number here was re-measured on this branch, and the A/B ran on the
final code; the earlier A/B round is kept separately. F2 (scope notes complete): the open items are listed above
and in FOLLOW-UPS. F3 (claims shown, not asserted): each claim names a test, and seeded bugs show the tests can
fail. The stop condition is real: `review-ready.py --delta-dri-needed` reports L1.

## Review fixes (`lf-18-review.final.md`)

| Finding | Fix (the class, not the example) | Commit | Regression tests |
|---|---|---|---|
| F1 (B): the `metered` relay showed trace bindings naming a sort and an entity the request does not hold | `ve.evaluate.read_evaluation`, the reader `evaluate` uses, binds every trace binding to the case's model: its sort is a sort of the model, its entity an entity of that sort, its de Bruijn index its position (R8 (b)). The relay gate reads `metered` answers with the same readers (`lean_runner.metered_row`, `read_evaluation`, `search.read_nonvacuity`); two fixtures ask for a trace; and fields are mutated to the same depth below a service row as below a one-shot row (7 levels), so the bindings, 6 levels down, are rebound. The deeper walk found 17 accepted mutants on other routes (graph, risk, quantity, discourse, readings-route), listed as follow-ups (F3, F4, F5, F11). | `50642ad6` | `tests/test_metered_answer.py` (one- and two-fault binding mutants; the reviewer's probe through `evaluate`), `tests/test_relay_mutation_gate.py::test_the_metered_fixtures_ask_for_a_trace_and_the_gate_reaches_its_bindings`, `::test_a_metered_reader_without_its_trace_binding_fails_the_gate` |
| F2 (B): 20 non-frozen checks hard-coded 10000, 65536 or 64, and the frozen decoders' node and depth literals were not tied | Every non-frozen check that compared with a limit's literal reads `VE.Limits` (146 sites in 53 files: decoder depth fuel, node totals, depth, identifier, source, tuple, entity, sort, predicate, numeral and JSON-depth bounds, the largest integer). The limits are `abbrev`s, so approved theorem statements and specification predicates that name a value are unchanged (`lean/statements.txt` and `predicates.txt` did not change) and their proofs hold of the checks. `VE.LimitTies` ties the frozen decoders at the limit and one past it (`VE.Bridge` and `VE.Order.Wire` documents, countermodel and certificate queries, sorts, predicates and domains; `VE.CertificateWire` closure queries and invariants; `VE.Json`'s integer and package caps), the diagnostics that state a limit; `VE.WireContract.Hooks.Norms` ties the generated wire-contract name classes (diagnostic-only, spec 7.3). Trust is unchanged (the new helpers are class T): V +34, S −3, K +0 as in DELTA T1. | `f1acf6b3`, `45687d6a` | `tests/test_lean_limits.py` (the lint: 146 sites on the previous tree, 0 now; the reviewer's probe; a seeded line per limit; a guard per frozen, hashed or generated copy); `lake build` (the `#guard`s) |

PROBE F1 printed `accepted` (exit 1) before the fix and prints `refused` after it; PROBE F2 listed 20 sites
before and passes after. Both are regression tests (`test_the_reviewers_probe_is_refused_through_evaluate`,
`test_lean_limits.py::test_the_reviewers_probe`).

Seeded bugs for the fixes (each restored; its test passed again):

| Language | File | Seeded bug | Test that failed |
|---|---|---|---|
| Python | `ve/evaluate.py` | `_bound_binding` drops the model membership check | `tests/test_metered_answer.py` (8 of 11 failed); the relay gate on `service:metered` (2 failures: `bindings/*/sort`, `bindings/*/local_id` rebind accepted) |
| Lean | `lean/VE/Closure/Bridge.lean` | the node total compared with the literal 10000 again | `tests/test_lean_limits.py::test_no_non_frozen_lean_check_hard_codes_a_limit` (the line is found) |
| Lean | `lean/VE/LimitTies.lean` | every guard checked against `maxNodes + 1` and `maxDepth + 1` (a changed limit) | 20 `#guard`s fail to elaborate |

Fix-round evidence: `evidence/relay-gate.json` was re-run on the fixed code (42 routes, 131,278 mutants, 0
failures). The A/B, difffuzz and latency evidence are the build's: the fixes change no answer (the limits keep
their values; the relay refuses only answers Lean never writes).

## Self-review against BUILDER-CHECKLIST

1. PASS: every Lean answer is fully typed and contained. `service:metered` 1,216 mutants, none accepted unlisted;
   `test_random_malformed_responses_never_escape_schema` covers the `metered` seed;
   `test_explanation_rows_must_be_exactly_one_tree`.
2. PASS: every required deliverable is built and no rule is broken. The deliverables table names a commit and a
   test for every plan-row line; no permanent report test was added; `grep` of the diff finds no new Python copy
   of a Lean decision.
3. PASS: tests and gates can fail. 10 seeded bugs, one per behaviour, in both languages (`evidence/mutants.json`).
4. PASS: Python, Lean and Rust agree, and valid inputs still pass. A/B 100,398 identical; `test_metered_lean`
   (four families, traces); `test_model_environment` (347 environments).
5. PASS: undeclared names are refused (R8 binding). `test_a_metered_answer_of_the_other_kind_is_no_answer`,
   the relay gate's rebind mutants, `test_a_cached_model_encoding_never_stands_for_another_model`.
6. PASS: gate evidence matches the final HEAD. The A/B, relay gate, fuzz runs and latency were measured on the
   final code; scope comes from `main..HEAD --no-merges` (`evidence/scope.json`); the full gate is the chain's.
7. PASS: no unsigned item is left for the reviewer. DELTA U1 (R7) and T1 (R16) are signed; L1 is reserved and
   named in the first line (L52).
8. PASS: every user-visible change is in DELTA. The A/B covers every corpus; no wording, order, verdict or
   availability change.
9. PASS: test selection still finds the tests the change can break. `test_seeded_manifest_edits_*` passes with
   the new `evaluate` seed; the repo-map regression is pinned to its commit (`test_repo_map.py`).
10. PASS: Lean statements and proofs say what is claimed. The `Row.json` field-rename mutant breaks
    `runCaseReported_fits`; three statement texts changed only by naming `VE.Limits.*` for the same constants
    (no approved-statement checker pins them).
11. PASS: budgets, limits and deadlines fail closed. `test_handshake`, `[large-limits]`, `[missing-limit]`;
    the metered mode has a CPU deadline (120 s per case); `test_w6a_limit_generator` passes.
12. FAIL, listed: CPU and memory regression. UDHR 0.94×, eligibility 0.72×, agent-policy `check.py base` 1.42×
    wall (DELTA L1, the stop reason).
13. PASS: every removed or renamed test has a trailer. 30 `Test-removed` trailers in the last commit;
    `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0 stale, 0 malformed.
