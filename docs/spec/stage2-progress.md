# Semantics migration Stage 2 progress

This checkpoint follows [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md), revision 3. Stage 0 and Stage 1 are merged on `mig/stage2`, and `main` was merged in at `3aab6626` (Lean service protocol 2, soft norms, units/time, attribution, causation, alternatives, the assurance manifest and the release gate). The Stage 0 `python.json` behaviour baseline remains the oracle. `VE_AUTHORITY` still defaults to `python`.

## Gate 2 measurement

`tools/stage2_parity.py --authority lean` reruns every Stage 0 probe (9,384 cells plus the graph, boundary and feature probes). Inputs are built by the retained Python and each probed call runs under the backend authority. It compares the result with the frozen baseline and with today's Python. The current report is [stage2-parity.md](stage2-parity.md). Cells fall into these classes:

| Class | Cells | Meaning |
|---|---:|---|
| regression | 0 | S→R/U/X, a changed S verdict status, or a changed R/U code |
| different | 0 | same cell and code, different record |
| baseline drift | 115 | differs from the baseline exactly as today's Python does (main added `lean_outcome` to bundle records) |
| same, adapter | 3,220 | identical; the operation's own adapter ran on the backend |
| same, constituents | 2,612 | identical; only constituent adapters (Background, typing, evaluation, search) ran on the backend, and the operation's verdict is still Python's |
| same, python | 3,437 | identical; no adapter was dispatched |

Every named graph, boundary and feature probe is also `same` or `baseline drift`; none is `different`. The regression diff is empty over the whole matrix. Over the Stage 2 sessions the count fell from 2,150 to 16, and then to 0. The last three classes were closed as follows:

- **Norms admission with `data@0` flags (16 regressions).** `Norms.Wire.decodeSource` takes a `flags` switch, and only document admission sets it. Admission's `background:flags` leaves are W2's, regenerated from the decoded flags (`Route.Admission`). `norms_wire_report_consequence` already takes the flag premises as its own hypothesis (`hflags`), so no theorem changed. The other norms cases (`norms-elaborate`, `norms-certificate`, `norms-conflict`) keep the gate: their regenerated Background and the conflict small-model argument are stated over `backgroundBase` (literals only). `VE/Norms/SmallModel.lean` assumes there are no `functional`/`total` flags, so the base theory is ground. It restricts a witness to a finite substructure, and that restriction does not preserve a `total` (∀∃) flag. No probe cell regresses there, because those operations have no adapter yet. They must be closed before their adapters are added (see the checklist).
- **Norms admission `UnsupportedProfile` wording (80 cells).** `Norms.Admission.envelopeGate` checks `norms@0` and the FOL family before the document, with Python's diagnostics ("norm document admission is FOL-only"). This is aligned wording, not documented wording.
- **Typing budget wording (named probes `MAX_NODES` and `MAX_DEPTH`).** The Lean typing diagnostic walk (`VE/Service/TypingDiagnostic.lean`) keeps `_Checker`'s node counter, shared across a document's formulas, and its formula and term depths. A budget rejection therefore gets Python's code and message at the node where Python meets it. The adapter strips the `ResourceLimit:` prefix only from `_Checker`'s three budget messages (`ve/backends/diagnostics.py`), because Python raises all other `ResourceLimit` messages with the prefix.

Building the budget test exposed one verdict difference outside the probe matrix, and it is fixed. On the order, closure and closure+nary families, Lean's standalone typing accepted a 10,001-node formula that Python rejects. The single-formula decoders of those families check depth only. `Standalone.decodeTyped` now runs `Route.AstLimit.check`, Python's decoder-order limit walk, on every family first. `tests/test_stage2_standalone.py::test_lean_typing_budget_diagnostics_match_python` covers all five envelope kinds.

An empty diff is not backend coverage. The 2,612 `same, constituents` and 3,437 `same, python` cells still take their verdict from Python.

For information only, `--authority rust-experimental` gives 2,497 regressions. This is by design: that authority sends only evaluation and search to Rust, and every other operation is `CheckerUnavailable`. It also gives 690 `different` cells, where Rust's `UnknownSymbol` wording in search and distinguishing differs. That authority is not part of Gate 2.

## Status by plan item

| Plan item | Status | Done in this checkpoint | Remaining |
|---|---|---|---|
| 2a Python adapters | Partial | Own adapters on the backend: typing, Background, dependency order, label, certificate replay (every family, including regulated, core-with-layers, reports and soft environments; Python's one-step-per-node budget applied to Lean's verdict; an invalid trace over the budget is `CheckerUnavailable`), admission (route, norms, soft and alternatives routes, W6 quantity through `ve_quantity` with a manifest binding and probe), evaluation, countermodel check, both searches. Search witnesses are published only through `countermodel.check`, as the assurance manifest requires. The adapters cover legacy v0/v0.1 envelopes and `reports@0`, `soft-norms@0` and `alternatives@0` environments. Typing rejections carry Python's codes and messages (`VE/Service/TypingDiagnostic.lean`). | No adapter yet for bundle, the norms operations, readings, argument graphs, compare, premise status, definitions elaboration, parse and canonicalize. `formula_from_data`/`formula_to_data` still type in Python. Also outstanding: operation batching, record provenance (`authority`, `assurance`, `covered_operations`, `trusted`), and complete fault injection. The service adapters are not yet declared in the assurance manifest, whose bindings and call sites describe the one-shot runners. |
| 2b Lean glue modes | Partial | The `check` mode covers legacy envelopes, core-family definitions and flags, norms, reports, soft and alternatives environments. It binds identities to the submitted environment. | `parse`, `normalize`, `graph` and `readings` modes, and `route/evaluate` with source. Environment and model modes are not yet wired into the Python constructors. |
| 2c Lean coverage closure | Closed on the probe matrix (empty regression diff) | `VE/Norms/Plain.lean`: regulated environments on every family (Background with profile premises, the profile model check, evaluate, countermodel). `VE/Core/Layers.lean`: definitions and data flags on closure+nary (Background, evaluate, countermodel, label). The norms tree now takes W3 definitions, so norms admission with definitions passes. The route refuses core-family admission as Python does. Norms document admission with `data@0` flags, with Python's envelope diagnostics. | Norms with data flags outside admission (elaborate, certificate, conflict), including a small-model argument that holds with `total` flags. Certificates on the order family with profile pairs. Closure bundles. |
| 2d readings checker | Open | — | `Route/Readings.lean` with its three soundness theorems |
| 2e Rust extensions | Mostly done | Order-family search, distinguishing models and full countermodel-check records, streaming Python's order candidates. The relational model stream now follows Python's exact order (domain sizes by total, relation subsets by size with permission and flag filters, then denotations); this removed every search count difference. `soft-norms@0` envelopes are accepted, with the soft document's premises as a model-validity filter. | Rust parse diagnostics with codes and spans |

## Verification

On the final code of this checkpoint:

- **Default authority (`VE_AUTHORITY` unset):** the full suite passes, 3,769 passed and 6 skipped. It ran as one parallel run (`-n 8 --dist loadfile`) plus `test_english_mixed_merge_smoke` run alone, which passed in 640 s. Setting `VE_AUTHORITY=python` explicitly fails 93 alternatives and Asimov tests with `CheckerUnavailable: alternatives@0 requires the Lean checker`. This is by design: alternatives is a Lean-only operation, and an explicit Python authority never runs Lean.
- **`VE_AUTHORITY=lean`:** the full suite passes, 3,769 passed and 6 skipped. It ran as three parallel chunks plus `test_english_mixed_merge_smoke` run alone, which passed in 649 s, the first completed run under this authority. The Hypothesis property test `test_astra_fix3_property_success_is_invariant_under_node_order_and_monotone_in_budget` takes 306 s under Lean and 84 s under Python. That is Gate 4 latency data, not a failure.
- `tools/stage2_parity.py --authority lean`: 0 regressions and 0 different cells over 9,384 cells, and no differing named probe ([stage2-parity.md](stage2-parity.md)).
- `lake build` passes. `lean/VE/Route/frozen.py` passes with the four edited modules re-hashed. `lean/checkers.lock` pins the rebuilt `ve_service`.
- `python lean/audit.py` audits 188 source files and 1,623 named theorems, with only `propext`, `Classical.choice` and `Quot.sound`. There is no `sorry`. No theorem statement changed in this checkpoint.
- Rust did not change in this checkpoint. `cargo test -p ve-core --locked` last passed at `87669fea` and was not rerun.
- New tests in this checkpoint:
  - `tests/test_stage2_evaluation.py::test_lean_norms_admission_with_data_flags_matches_python`: a norm layer leaf with a `background:flags` leaf, a rejected mislabelled flag leaf, and the closure envelope's FOL-only diagnostic, all identical under both authorities;
  - `tests/test_stage2_standalone.py::test_lean_typing_budget_diagnostics_match_python`: node and depth budgets, arithmetic term depth, typing-before-budget and budget-before-typing order, and a document's shared node counter, on five envelope kinds.
- Earlier tests cover:
  - typing diagnostics on nine envelopes and on legacy envelopes;
  - order search, distinguishing and countermodel checks against Python;
  - core-family layers;
  - the model-order budget sweep;
  - certificate replay on eight envelopes (valid, over-budget and stale certificates).

## Trusted composition points added

- **Soft premises.** In the Lean Background adapter, soft premises come from a validated soft document and are not environment data. They are composed after Lean's base Background. Lean regenerates them in the soft route, and `soft_route.check_regenerated` compares them there.
- **Legacy Background.** Legacy v0/v0.1 envelopes have an empty Background: their Lean certificate runners bind case premises alone.
- **Reports and soft vocabularies.** `reports@0` and soft vocabularies are reduced before route cases whose answers carry no environment identity. The reports reduction is the vocabulary the Lean attribution decoder hands the route decoder.

- **Soft certificate premises.** Certificate cases on soft environments carry the soft document's premises, and the Lean norms route appends them after the profile premises. This is the same composition point as soft Background.

## Test changes

- `tests/test_assurance_manifest.py`: the refusal half of the search test expects `CheckerUnavailable` under a backend authority. A backend search returns one witness, and a refused witness is a generator/check disagreement. Python's generator still keeps searching.
- `tests/test_replay_conservativity.py`: under a backend authority, an invalid-certificate row accepts Lean's detail wording. Verdict, status and steps must still match exactly.
- `tests/test_stage2_dispatch.py`: the fault injection patches the Rust client's runner.
- `tests/test_assurance_manifest.py` allows `ve/backends/rust_jsonl.py` to start processes.

No existing test changed in this checkpoint. The assurance manifest re-pins `lean/VE/Norms/Wire.lean` (the decoder range now ends at line 313) and `lean/VE/Norms/Admission.lean`, and it records that `envelopeGate` only rejects, through the pinned `Gate.decodeEnvelope`.

## Gate 2 checklist: not passed

Each criterion from the plan's Gate 2 paragraph, in order:

| # | Criterion | Status | Evidence or gap |
|---|---|---|---|
| 1 | The full suite passes under `VE_AUTHORITY=lean` | **Met** | 3,769 passed, 6 skipped, including `test_english_mixed_merge_smoke` (649 s) |
| 1a | … for every class-A operation | **Not met** | No own adapter yet for bundle, the norms operations (elaborate, certificate, conflict, norms admission through `admit_norm_document`), readings, argument graphs, compare, premise status, definitions elaboration, environment and model validation, parse and canonicalize, or `formula_from_data`/`formula_to_data` typing. Under Lean, these still return Python's verdict. |
| 1b | Fixture changes limited to `checker_build`, `record_id` and documented message wording | **Partly met** | Four scoped test changes (listed above). The replay-wording change is documented wording. The search-refusal change (`CheckerUnavailable` when a backend witness is refused) is a behaviour change that needs the lead's review. |
| 2 | The full Stage 0 baseline and public API agree under the section-5 projection | **Met as measured** | 0 regressions and 0 different cells over 9,384 cells and every named probe. The 115 `baseline drift` cells are main's `lean_outcome` bundle field, which today's Python shares. Only 3,220 cells run the operation's own adapter (see 1a). |
| 3 | Matrix Lean/Rust column: no S→R, S→U or code change (empty regression diff) | **Met under `VE_AUTHORITY=lean`** | Same report. `rust-experimental` is not a Gate 2 authority (see above). |
| 4 | Adapter fault-injection tests | **Partly met** | `tests/test_stage2_dispatch.py` covers authority override and rejection, no fallback, shadow logging of an unavailable checker, and malformed Rust responses. Missing: per-adapter injection of missing or mismatched binaries, crashes and timeouts for every Lean adapter. |
| 5 | The inventory lint passes (no retained module imports a class-A body) | **Not met** | Not written. `.importlinter` checks layering only. |
| 6 | The `graph` mode is merged | **Not met** | `check_argument` composes in Python. The graph probes are `same, python`. |
| 7 | The readings checker is merged, or its exclusion from `covered_operations` is recorded | **Not met** | `Route/Readings.lean` does not exist, and no exclusion is recorded. |

Stage 2 obligations outside the Gate 2 paragraph that are also open:

- **Batching:** one request per operation for `premise_status`, `check_readings`, `check_argument` and `check_step`.
- **Provenance fields:** `authority`, `assurance`, `covered_operations` and `trusted` on records.
- **Rust parse diagnostics:** codes and spans.
- **Assurance manifest:** declare the Lean service adapters.
- **Norms data flags outside admission:** needed before the norms-operation adapters. The Background must carry flags, and the conflict small-model argument must survive `total` flags.
- **Order-family certificates with profile pairs:** still `CheckerUnavailable`.

Suggested order for the next session: the norms-operation adapters (with norms flags outside admission), then the `graph` mode and the argument-graph adapter, then the readings decision, then the inventory lint and fault injection.
