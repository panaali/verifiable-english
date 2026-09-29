# Semantics migration Stage 2 progress

This checkpoint follows [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md), revision 3. Stage 0 and Stage 1 are merged on `mig/stage2`, and `main` was merged in at `3aab6626` (Lean service protocol 2, soft norms, units/time, attribution, causation, alternatives, the assurance manifest and the release gate). The Stage 0 `python.json` behaviour baseline remains the oracle. `VE_AUTHORITY` still defaults to `python`.

## Gate 2 measurement

`tools/stage2_parity.py --authority lean` reruns every Stage 0 probe (9,384 cells plus the graph, boundary and feature probes). Inputs are built by the retained Python and each probed call runs under the backend authority. It compares the result with the frozen baseline and with today's Python. The current report is [stage2-parity.md](stage2-parity.md). Cells fall into these classes:

| Class | Cells | Meaning |
|---|---:|---|
| regression | 16 | S→R/U/X, a changed S verdict status, or a changed R/U code |
| different | 80 | same cell and code, different record (all are admission `UnsupportedProfile` message wording) |
| baseline drift | 115 | differs from the baseline exactly as today's Python does (main added `lean_outcome` to bundle records) |
| same, adapter | 2,779 | identical; the operation's own adapter ran on the backend |
| same, constituents | 2,957 | identical; only constituent adapters (Background, typing, evaluation, search) ran on the backend, and the operation's verdict is still Python's |
| same, python | 3,437 | identical; no adapter was dispatched |

The 16 regressions are norms admission with `data@0` flags. The Lean norms route has no flags slot in its Background (`Norms/Prefix.lean` `backgroundBase` is literals only). Closing this changes the norms layer theorems, and it is the remaining stage-2c gap the plan names as the largest uncertainty. During this session the regression count fell from 2,150 to 16.

With `VE_AUTHORITY=lean`, every test file of the suite passed in chunks (`test_english_mixed_merge_smoke` excepted, below). Chunks 2 and 5–7 passed before the last four commits and were not rerun afterwards; the files whose failures those commits fixed passed on rerun. Passing the suite is not Gate 2: cells counted as `same, python` or `same, constituents` still take their verdict from Python.

## Status by plan item

| Plan item | Status | Done in this checkpoint | Remaining |
|---|---|---|---|
| 2a Python adapters | Partial | Own adapters on the backend: typing, Background, dependency order, label, admission (route, norms, soft and alternatives routes, W6 quantity through `ve_quantity` with a manifest binding and probe), evaluation, countermodel check, both searches. Search witnesses are published only through `countermodel.check`, as the assurance manifest requires. The adapters cover legacy v0/v0.1 envelopes and `reports@0`, `soft-norms@0` and `alternatives@0` environments. Typing rejections carry Python's codes and messages (`VE/Service/TypingDiagnostic.lean`). | No adapter yet for certificate replay, bundle, the norms operations, readings, argument graphs, compare, premise status, definitions elaboration, parse and canonicalize. `formula_from_data`/`formula_to_data` still type in Python. Also outstanding: operation batching, record provenance (`authority`, `assurance`, `covered_operations`, `trusted`), and complete fault injection. The service adapters are not yet declared in the assurance manifest, whose bindings and call sites describe the one-shot runners. |
| 2b Lean glue modes | Partial | The `check` mode covers legacy envelopes, core-family definitions and flags, norms, reports, soft and alternatives environments. It binds identities to the submitted environment. | `parse`, `normalize`, `graph` and `readings` modes, and `route/evaluate` with source. Environment and model modes are not yet wired into the Python constructors. |
| 2c Lean coverage closure | Mostly closed on the probe matrix | `VE/Norms/Plain.lean`: regulated environments on every family (Background with profile premises, the profile model check, evaluate, countermodel). `VE/Core/Layers.lean`: definitions and data flags on closure+nary (Background, evaluate, countermodel, label). The norms tree now takes W3 definitions, so norms admission with definitions passes. The route refuses core-family admission as Python does. | Norms with data flags (the 16 regressions). Certificates on regulated, core-with-layers, reports and soft environments. Closure bundles. Admission `UnsupportedProfile` message wording (80 cells). |
| 2d readings checker | Open | — | `Route/Readings.lean` with its three soundness theorems |
| 2e Rust extensions | Mostly done | Order-family search, distinguishing models and full countermodel-check records, streaming Python's order candidates. The relational model stream now follows Python's exact order (domain sizes by total, relation subsets by size with permission and flag filters, then denotations); this removed every search count difference. `soft-norms@0` envelopes are accepted, with the soft document's premises as a model-validity filter. | Rust parse diagnostics with codes and spans |

## Verification

- The Python-default suite passed after the merge and again after the last Lean change. That run was 3,753 passed, 6 skipped, with `test_english_mixed_merge_smoke` not run: alone, it exceeds the 10-minute tool limit at this machine's load.
- `lake build` passes.
- `python lean/audit.py` audits 188 source files and 1,623 named theorems, with only `propext`, `Classical.choice` and `Quot.sound`. There is no `sorry`.
- `cargo test -p ve-core --locked` passes.
- New tests cover:
  - typing diagnostics on nine envelopes and on legacy envelopes;
  - order search, distinguishing and countermodel checks against Python;
  - core-family layers;
  - the model-order budget sweep.

## Trusted composition points added

- **Soft premises.** In the Lean Background adapter, soft premises come from a validated soft document and are not environment data. They are composed after Lean's base Background. Lean regenerates them in the soft route, and `soft_route.check_regenerated` compares them there.
- **Legacy Background.** Legacy v0/v0.1 envelopes have an empty Background: their Lean certificate runners bind case premises alone.
- **Reports and soft vocabularies.** `reports@0` and soft vocabularies are reduced before route cases whose answers carry no environment identity. The reports reduction is the vocabulary the Lean attribution decoder hands the route decoder.

## Gate 2: not passed

Still required:

1. Adapters for every remaining class-A operation. The first is certificate replay, the constituent of readings, compare, premise status, argument graphs and bundles.
2. The `graph` mode and the readings checker, or a recorded exclusion.
3. Norms data flags.
4. An empty regression diff with the 80 admission message differences either aligned or recorded as documented wording.
5. Batching, provenance fields and complete fault injection.
6. Rust parse diagnostics.
7. The inventory lint.
8. Declaring the service adapters in the assurance manifest.
9. A full Lean-authority suite run, including the merge smoke, on a less loaded machine.
