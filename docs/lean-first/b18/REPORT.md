# Lean first batch 18: the cleanup batch

**The agent-policy harness is within the 1.25× budget: `check.py base` runs at 1.22× the base wall time**
(median of three paired runs on the code head `450a7101b`, base and head alternating; child CPU 1.06×; identical
output; `evidence/latency.json`). DELTA row L1 is gone: the DRI note's speed fix (F7, below) took it from 1.42×.
DELTA U1 cites R7 and T1 cites R16; no row reserves a signature.

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
- DRI note F7 (`47a916cf3..450a7101b`): `ve/` +19 −3 (`backends/lean_service.py`); Lean written by hand +274 −59
  (`VE/Service/Protocol.lean` +209 −38, of which the `#guard`s and their oracles are about 75, `VE/Route/MeteredRun.lean`
  +50 −16, `ResponseShape/Encoders/Metered.lean` +15 −5); tests +154 (`tests/test_metered_handles.py`).

## Gate evidence (section 5.1)

| Item | Result | Evidence |
|---|---|---|
| Corpus A/B | 100,410 records over every corpus of `tools/lean_first_diff.py`, recorded on the final code: 100,398 identical, 12 unavailable on both sides with identical outputs (R7). `compare --delta DELTA.json` exits 0. Pilots that the 600 s recorder limit cut on one side under load were re-recorded on both sides together (DELTA.md). After F7, every corpus but the pilots was re-recorded on `450a7101b`: 99,847 of 99,847 records identical. | `evidence/ab.json`, `base-ab.jsonl.gz`, `head-ab.jsonl.gz`, `ab-initial.json`, `pilot-rerun.json`, `ab-f7.json` |
| Difffuzz baseline does not grow | CI sample on the head: 242 baseline entries, 0 new, 0 not reproduced. Paired base and head over the CI sample and 14 date seeds: all 15 pairs equal, with no head-only and no base-only signature. | `evidence/difffuzz-ci.json`, `difffuzz-ab.json` (`difffuzz_ab.py`) |
| Relay mutation gate | 42 routes, 131,278 mutants, 0 failures on the review-fixed code (fields are now mutated 7 levels below a service row, as below a one-shot row; review F1). | `evidence/relay-gate.json` |
| Latency | On the code head `450a7101b` (DRI note F7): UDHR document 0.98×, eligibility 0.84× and agent-policy `check.py base` 1.22× of the base wall (child CPU 1.06×), identical outputs, all within section 4's 1.25×. Before F7: 1.42× (1.31× re-measured on 2026-10-19). | `evidence/latency.json` (batch 13b's script, re-run on the code head), `agent-policy-concurrent.json` (before F7) |
| Trust budget | V +120, S −3, K +0: +117 lines K+S+V (DELTA T1, R16; F7's V +86 of it); the two allowances are recorded in `docs/trust-baseline.json`; `trust_map.py --check` passes. | — |
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

AGENT: everything above. HUMAN: none. EXTERNAL: none.

## Sibling lessons (lf-16g review)

F1 (numbers re-measured, not cited): every number here was re-measured on this branch, and the A/B ran on the
final code; the earlier A/B round is kept separately. F2 (scope notes complete): the open items are listed above
and in FOLLOW-UPS. F3 (claims shown, not asserted): each claim names a test, and seeded bugs show the tests can
fail. The stop condition was real (`review-ready.py --delta-dri-needed` reported L1) until F7 removed the delta.

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

Fix-round evidence: `evidence/relay-gate.json` was re-run on the fixed code at `1a2e1dc2` (42 routes, 131,278
mutants, 0 failures). The selected tests for the branch (`select_tests --base $(git merge-base HEAD main)`, 433
units) passed on the Mac runner at `1a2e1dc2`; `lake build`, `lean/audit.py`, `trust_map.py --check` and
`regen_generated.py --check` pass. The A/B, difffuzz and latency evidence are the build's: the fixes change no answer (the limits keep
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
7. PASS: no unsigned item is left for the reviewer. DELTA U1 cites R7 and T1 cites R16; no row reserves a
   signature (L1 was removed by F7).
8. PASS: every user-visible change is in DELTA. The A/B covers every corpus; no wording, order, verdict or
   availability change.
9. PASS: test selection still finds the tests the change can break. `test_seeded_manifest_edits_*` passes with
   the new `evaluate` seed; the repo-map regression is pinned to its commit (`test_repo_map.py`).
10. PASS: Lean statements and proofs say what is claimed. The `Row.json` field-rename mutant breaks
    `runCaseReported_fits`; three statement texts changed only by naming `VE.Limits.*` for the same constants
    (no approved-statement checker pins them).
11. PASS: budgets, limits and deadlines fail closed. `test_handshake`, `[large-limits]`, `[missing-limit]`;
    the metered mode has a CPU deadline (120 s per case); `test_w6a_limit_generator` passes.
12. PASS: CPU and memory regression. UDHR 0.98×, eligibility 0.84×, agent-policy `check.py base` 1.22× wall
    (after F7; it was 1.42×). The handle table keeps at most 64 decoded environments, one per held handle.
13. PASS: every removed or renamed test has a trailer. 30 `Test-removed` trailers in the last commit;
    `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0 stale, 0 malformed.

## DRI note F7: the agent-policy speed fix (`lf-18-dri-note-20261019.md`)

**PROBE F7** (`latency.py`, three paired runs, base `ffb3155a5` checked out apart and alternating with the head):
before the fix the agent-policy row was `within_budget: false` (1.42× in the build; 1.31× re-measured on
2026-10-19 at load 5 to 17); on the code head `450a7101b` it is `within_budget: true`, `same_output: true`, at
1.22× (base 77.6, 77.9, 78.6 s; head 94.3, 95.3, 95.5 s; load 3 to 9). It is no regression test: the suite takes
no elapsed-time asserts (CLAUDE.md), and the numbers are saved evidence (`evidence/latency.json`).

Where the time went. Each of the harness's 8,169 sequential evaluations is one Lean `metered` request of about
4 KB. The builder's diagnosis, decoding the handle's environment again, was a small part of it: at 1.1 ms of Lean
CPU per request, the environment's validation and vocabulary took about 0.15 ms; the frozen `VE.JsonInput.caseTexts`
took 0.34 ms (it builds each case text from a list of characters) and the request splitter `objectMembers`
0.10 ms. A request's Lean CPU also doubles when Python works between requests (0.82 to 1.44 ms on the same
lines: cold caches), so the per-request costs count about twice in the harness. After F7, a request costs about
1.0 ms of Lean and 1.0 ms of Python relay at idle, against 0.2 ms for the base's in-process Python evaluator. The
ratio depends on the host's load: three paired runs during the work at load 11 to 37 measured 1.04× and 1.23× (on
`f6c4ecd7a`) and 1.16× (on `450a7101b`), and one at load 45 measured 1.38× (on `f6c4ecd7a`).

| Fix (the class, not the example) | Commit | Regression tests |
|---|---|---|
| The service keeps what the `metered` mode decodes from an environment alone (`VE.Route.MeteredRun.Prepared`: the validation and, on first use, the layers and each family's vocabulary) in that environment's handle entry (`VE.Service.Entry`). It is replaced or dropped exactly with its handle, so the table holds at most 64 (`maxHandles`), and it is always that entry's own environment's (`prepared_eq`, by construction). `caseResult_cached` proves a case against a held handle is answered with it exactly as the case with its environment re-sent; `runWith` meets faults in the order the case did before; `ResponseShape.Encoders.Metered.runWith_fits` covers both paths. The client keeps its decoded environments the same way, by digest, at most 64 (`LeanService._decoded_environment`). | `f6c4ecd7a` | `tests/test_metered_handles.py::test_interleaved_handles_answer_each_case_as_its_own_environment_does` (five families and two FOL environments, one case per request, equal to the re-sent answers), `::test_a_dropped_or_refused_handle_never_answers_from_its_old_decoding` (close past 64 registrations, refuse a replacement, reuse the id), `::test_the_client_keeps_one_decoding_per_environment_text` |
| One byte scan cuts the case texts of a request (`caseBounds`, shared with `caseDigests`) and its members (`objectMembers` by `memberCuts`), with the character scans' rules and messages; a batch the bounds do not cut goes to the frozen `parseCases` itself. Exhaustive `#guard`s compare them with `VE.JsonInput.parseCases` and with the character scan (kept as the test oracle `objectMembersByChars`), error text included, on all 16,105 inputs of at most four characters over the delimiters, an escape, a key, a number and a multi-byte character, and on nested, deep, padded and real ones. The pool sends a one-request batch as the cases it already encoded. | `f6c4ecd7a`, `450a7101b` | the `#guard`s in `VE/Service/Protocol.lean` (`lake build`); `tests/test_lean_service.py`, `tests/test_lean_handles.py` |

Answers are unchanged. The two request streams recorded from the harness (3,000 metered requests of one
process and 6,000 of the main process) are answered byte for byte as before. Every A/B corpus but the pilots
was re-recorded on the code head `450a7101b`: all 99,847 records equal the base's and the previous head's
(`evidence/ab-f7.json`; the 563 pilot records, whole documents of up to 600 s each, were not re-recorded).

Trust (R16): F7 adds V +86, `VE/Service/Protocol.lean` +62 and `VE/Route/MeteredRun.lean` +24; the item is V +120,
S −3, K +0 in all, +117 lines K+S+V, within R16's 150 and none in K (DELTA T1, re-measured on the final HEAD; the
guard oracles are class T). Each new definition has a test that can fail (above and the seeded bugs), and the ties
pass is a FOLLOW-UPS.md row.

Seeded bugs for F7 (`evidence/mutants.json`; each restored, and its test passed again):

| Language | File | Seeded bug | Test that failed |
|---|---|---|---|
| Lean | `lean/VE/Service/Protocol.lean` | `Handles.entry?` ignores the handle and answers the table's first entry | `lake build` (`entry_hit`); with that proof stubbed, `test_interleaved_handles_answer_each_case_as_its_own_environment_does` |
| Lean | `lean/VE/Service/Protocol.lean` | `Handles.insert` never empties the table, so no entry is dropped | `test_a_dropped_or_refused_handle_never_answers_from_its_old_decoding` (the older eviction test passed) |
| Lean | `lean/VE/Service/Protocol.lean` | `restrictedCases` parses each cut text trimmed (a parse error's offset moves) | `lake build`: the `restrictedCases` `#guard` |
| Lean | `lean/VE/Service/Protocol.lean` | `memberCuts` takes every top-level `:` as the key's end | `lake build`: both `objectMembers` `#guard`s |
| Python | `ve/backends/lean_service.py` | `_decoded_environment` answers any kept decoding, whatever the digest | `test_the_client_keeps_one_decoding_per_environment_text` |

Runs on the code head `450a7101b`: the selected tests (`select_tests --base ffb3155a5`, 434 units, Mac runner)
passed with 0 failures; `lake build` (967 jobs), `lean/audit.py`, `tools/trust_map.py --check` and
`tools/regen_generated.py --check` (28 entries) pass. On `f6c4ecd7a` the selected tests had found only the two
trust-budget tests, before the R16 allowance was recorded in `450a7101b`.
