# Lean first batch 18: the cleanup batch

**Stops for one DRI signature (L52): DELTA row L1**, the agent-policy harness's `check.py base` at 1.42× the base
wall (identical output) against the use-case harness row's 1.25×. Every other row is signed by a standing ruling.

**Scope.** Plan row 18 and the DRI's 2026-10-14 addition (`prompts/lf-18-task.txt`): one `VE/Limits.lean`;
Python reads the I/O caps from the service handshake; one Python error class per Lean code; the `python`
authority and `VE_AUTHORITY_OVERRIDES` removed; assist and Cedar decisions through Lean replay; the assurance
manifest updated. Removing the `python` authority moves the last three operations it still decided
(`evaluate`, `countermodel_check`, model validation) to Lean, which needed the batch-15a metered evaluator as a
service mode (the one-shot `ve_metered` costs 94 ms a call, the service 1.9 ms).

## Deliverables

| Plan row 18 / DRI addition | Delivered | Commit | Tests |
|---|---|---|---|
| One `VE/Limits.lean` (six copies of `maxNodes`) | `lean/VE/Limits.lean` owns the 15 envelope limits; the six `maxNodes`, three `maxDepth`, two `maxSourceBytes`, two `maxPredicates`, `maxSorts`, `maxIndex`, `maxEvaluations`, `maxNumeralChars` and the service's `maxLineBytes`/`maxCases` are `export VE.Limits (...)`. The hash-frozen decoders (`VE.Json`, `VE.Bridge`, `VE.Order.Wire`) and the grammar-locked English lexer keep their literals; `VE/LimitTies.lean` `#guard`s each against `VE.Limits` (at the limit and one past it). | `f98bd6f2` | `lake build` (the `#guard`s), `tests/test_lean_service.py::test_handshake` |
| Python reads I/O caps from the service handshake | The handshake states every limit (`VE.Limits.stated`); `envelope.json` pins each as a `const` (before: `minimum` for three); `ve/limits.py`, `lean_service.py`, `rust_jsonl.py` and `surface/time.py` read them from there, no copy left. A service stating other limits, or lacking one, is refused at its start. | `f98bd6f2` | `test_handshake` (live service against `ve.limits`' names), `test_bad_or_missing_handshake_is_unavailable[large-limits, missing-limit]` |
| One Python error class per Lean code | The shadowed duplicate `CheckerUnavailable(VEError)` is deleted; `AdmissionError` moves into `ve/errors.py` (`ve.admission` re-exports it); `relay.CLASSES` is derived from the classes' own `code` against the handshake's code list, no hand table (`VEError` is `InvalidInput`'s class, as Lean's English route names it). | `f98bd6f2` | `tests/test_relay.py::test_each_code_has_exactly_one_class_in_ve_errors`, `test_one_class_per_code_of_the_service` |
| `python` authority and `VE_AUTHORITY_OVERRIDES` removed | `ve/backends/dispatch.py` 285 → 38 lines: `python`, `shadow`, `rust-experimental`, `VE_AUTHORITY`, `VE_AUTHORITY_OVERRIDES`, `pinned`, `composed`, `execute`, `shadowed` and the shadow log are deleted; `evaluate`, `countermodel_check` and `model_validation` join `LEAN_OWNED` and run through `owned()`; the `VE_AUTHORITY == "python"` refusals of `risk.py` and `alternatives.py` and the English override go. The English comparator keeps its record writer, moved to `english_lean.py`. | `dadfec02` | `tests/test_stage2_dispatch.py::test_no_setting_selects_an_authority` (four leftover settings), `tests/test_single_owner.py` |
| (needed by the removal) the metered evaluator in the service | Service mode `metered` (`runMode_metered`); `MeteredTrace` builds a typed `Trace` and writes it as preorder rows, so `metered.json` needs no recursive shape; an evaluation is one of three typed results (Satisfied/true, Violated/false, ResourceLimit/null); `ResponseShape.Encoders.Metered.runCaseReported_fits` proves every row fits. Python sends both case kinds to it and binds the alternative to the kind sent; `evaluate._explanation` rebuilds the tree and refuses rows that are not one tree. | `dadfec02`, `7e63113f` | `tests/test_metered_lean.py` (all four families' traces against Python's), `test_explanation_rows_must_be_exactly_one_tree`, `test_a_metered_answer_of_the_other_kind_is_no_answer`, relay gate `service:metered` 646/646 mutants refused |
| Assist `_decide`, `_entails` and Cedar allow/deny through Lean replay (plan rows marked 18) | Delivered by batch 17 (`19c5bbe69`, merged): no change needed here; the `pinned("lean")` wrappers they used are gone with the authorities. | — | `tests/test_b17_owner.py` (6 tests pass on this HEAD) |
| Assurance manifest updated | `evaluate` and `countermodel.check` are `migrated` (their entries relay Lean, `semantic_entry(..., engine="lean")`); the metered bindings name `ve_service metered`; the one-shot call sites and the shadow handler's review entry are gone; `docs/spec/assurance-manifest.md` regenerated. | `2f66d1ab`, `8c52e0c0` | `tests/test_assurance_manifest.py` (137) |
| Delete the duplicates | `limits.py` constants, the dispatch shadow and authorities, the duplicate error class and hand class table, the six Lean limit copies. | all | — |

Not migrated in the manifest (follow-up F1): the batch-13b operations (parse, typing, admission, label, readings,
graph, bundle, certificates, norms, definitions, premise status, compare) still read `authority: python` although
Lean decides them; each keeps a retained Python branch for inputs outside its Lean scope, so marking them
`migrated` would refuse those branches. `ve_metered` stays built as a test oracle only; no product path runs it.

## Lines

Range `main..HEAD --no-merges` at the code head, base `ffb3155a5` (saved in `evidence/scope.json`).
`ve/` Python: +369 −483 (net −114; `dispatch.py` −265). Lean by hand (no generated `Audit.lean`): +335 −54, of
which `VE/Limits.lean` 54, `VE/LimitTies.lean` 31, the metered shape and its proofs 162. Tests: +392 −668.

## Gate evidence (section 5.1)

- **A/B** (`evidence/ab.json`, `DELTA.md`): 100,410 records over every corpus; 100,399 identical, 11 unavailable
  on both sides with identical outputs (R7); `tools/lean_first_diff.py compare --delta DELTA.json` exits 0. The
  first recording's two load-decided UDHR timeouts and their re-recording are saved.
- **Difffuzz**: CI sample on the head: 242 baseline entries, 0 new, 0 not reproduced. Paired base/head over the
  CI sample and 14 date seeds: `evidence/difffuzz-ab.json` (no head-only signature).
- **Relay mutation gate**: 42 routes, 121,464 mutants, 0 failures (`evidence/relay-gate.json`); the one-shot
  `ve_metered` readers and allow entry F8 (whose fix this is) are gone.
- **Latency** (`evidence/latency.json`, batch 13b's paired script): UDHR 0.94×, eligibility 0.72×,
  agent-policy `check.py base` 1.42× wall, 1.18× child CPU (DELTA L1).
- **Trust budget**: V +34, S −3, K +0 (DELTA T1, R16).
- `lake build` (965 jobs), `tools/regen_generated.py --check` and `python3 tools/rust_build.py --check` pass.
