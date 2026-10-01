# Semantics migration Stage 2 progress

This checkpoint follows [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md), revision 3. Stage 0 and Stage 1 are merged on `mig/stage2`. `main` was merged in at `3aab6626` and again at `5eac1968`. The second merge brought rights, speech acts, eligibility, the agent policy, the release gate and the pre-commit hook. The Stage 0 `python.json` behaviour baseline remains the oracle. `VE_AUTHORITY` still defaults to `python`.

## Decisions recorded

- **DRI decision (orchestrator, 2026-09-29): the search-refusal change is accepted.** Gate 2 checklist item 1b listed one test change that is not wording: under a backend authority, a search witness that the Lean countermodel check refuses returns `CheckerUnavailable` (`tests/test_assurance_manifest.py`). This follows the fail-closed assurance rule: a refused witness is a generator/check disagreement, never a verdict. The same rule governs every adapter.
- **DRI decision (orchestrator, 2026-09-30): the Python-meter tests select the Python authority; accepted with a condition, now met.** Main's rewritten `tests/test_w6a_limit_generator.py` counts the charges of Python's own evaluator (`_Evaluator.tick`) while it runs public calls. Under `VE_AUTHORITY=lean` those calls evaluate on Rust and Lean, so the meter counts nothing and three tests fail. `meter_python` now sets `VE_AUTHORITY=python`, since what these tests measure is Python's evaluator. No assertion changed. The suite already has this pattern in `tests/test_assurance_manifest.py:690` and `tests/test_alternatives_profile.py:101`. The condition: a Lean-authority counterpart. `test_lean_authority_reports_resource_limit_on_every_generated_case` feeds every case the same generator makes, for each seed, through the same public calls under `VE_AUTHORITY=lean`. It asserts `ResourceLimit` on each case and that every dispatched operation ran on Lean, with no Python fallback. It also asserts that the operations deciding the work-budget and domain cases (`evaluate`, `countermodel_check`, `model_validation`, `definitions_elaboration`) were dispatched. It counts no Python units.

## Gate 2 measurement

`tools/stage2_parity.py --authority lean` reruns every Stage 0 probe: 9,384 cells, plus the graph, boundary and feature probes. The retained Python builds the inputs, and each probed call runs under the backend authority. The tool compares each result with the frozen baseline and with today's Python. The current report is [stage2-parity.md](stage2-parity.md).

| Class | Cells | Meaning |
|---|---:|---|
| regression | 0 | S→R/U/X, a changed S verdict status, or a changed R/U code |
| different | 0 | same cell and code, different record |
| baseline drift | 115 | differs from the baseline exactly as today's Python does (main added `lean_outcome` to bundle records); all 115 ran the bundle's own adapter |
| same, adapter | 6,120 | identical; the operation's own adapter ran on the backend (5,112 at the previous checkpoint) |
| same, backend rejection | 1,035 | identical rejection returned by the Lean service in a constituent adapter before the operation's own adapter was reached (new class, below) |
| same, constituents | 115 | identical; only constituent adapters ran: the English-surface positives, where Lean types the AST |
| same, python | 1,999 | identical; no adapter dispatched: 1,769 cells Python itself answers `UnsupportedProfile`, and 230 English-surface rejections |

All 11 named graph probes are `same, adapter`. Every named boundary and feature probe is `same` or `baseline drift`. The non-empty bundle probes on the closure, core and order families now route through Lean's bundle mode.

**Backend rejections.** The Lean service's rejection is marked on the error (`diagnostics.backend_rejection`), including when the validation decision rule names it with Python's diagnostic. A rejection cell counts as backend-decided only if the error the operation raised carries that mark. Examples: Lean's typing check refusing an unknown conclusion predicate before a countermodel search, and Lean's model mode refusing a stale model identity before an evaluation.

### How the 2,388 cells outside the adapters' scope were closed

The previous checkpoint left 2,388 reachable cells without a backend decision. By class:

| Class | Cells | Closed by |
|---|---:|---|
| Rejections decided by a constituent adapter | 730 | measurement: they carry the Lean service's rejection mark (`same, backend rejection`) |
| Stale model identity (evaluate, evaluate trace, countermodel check) | 345 | extension: Lean's `model` mode takes the model's claimed `environment_id` and `model_id` and rejects a mismatch itself (`FiniteModel.from_dict(_claimed=...)`) |
| `definitions@0` parse and canonicalise | 192 | extension: Lean's `parse` mode reads `definitions@0` environments; a source Python reads through the definitions sugar keeps Python's reading (recorded gap below) |
| Argument graph and readings on the closure, core and order families | 400 | extension: `VE/Service/GenericGraph.lean`, `GenericReadings.lean`, `Family.lean` |
| Bundles on the closure, core and order families and over norms environments | 96 | extension: `VE/Service/FamilyBundle.lean` (new `bundle` mode) |
| Norms elaborate, certificate and conflict on the closure, core and order families | 240 | extension: `VE/Service/FamilyNorms.lean` (new `family-norms` mode) |
| Frozen v0 and v0.1 envelopes (environment, model, parse, graph, readings, bundle) | 40 | extension: `Standalone.decodeLegacy` and legacy family contexts |
| English-surface parse | 345 | recorded, out of Lean's authority by plan decision (below) |

The counts overlap slightly between measurement and extension: some constituent rejections became own-adapter cells once the operation's adapter took the family. The totals above are the final measurement.

**The one class left on Python, by plan decision.** The English surface (345 `parse_accept` cells on `english-surface` rows) stays Python. The plan's section 2.3 gap table says "English surface | Python | … | stays Python by decision". Section 1.3 lists `english.py`, `fluent.py` and `natural.py` as surface "unchanged by this plan", and stage 4 labels English-input records `python:surface` in `trusted`. This is not a later stage: the plan keeps English parsing outside Lean's authority. On these rows Lean still types every AST the English parser produces (the 115 `same, constituents` cells).

### Scope gaps that remain (not probe cells)

Each adapter routes these inputs to the retained Python statically. They are recorded scope gaps, not fallbacks after a failure. All of them are Stage 2c work: "every matrix S cell Lean lacks". The plan sets 2c's deadline at Gate 4, not Gate 2: section 2.3 gap table row 1 ("close in Lean before gate 4 (stage 2c …)"), section 5 risk row 1 ("stage 2c closes the gaps in Lean before gate 4") and section 6 ("2c … sets the critical path to gate 4"). None of them occurs in the Stage 0 probe matrix.

- **`definitions@0` surface sugar** (`no`, `every … that is`, `iff`, `define`): no Lean surface parser has it. Python's parser records when it reads a sugar production, and such a source keeps Python's reading. Every other `definitions@0` source is Lean's to accept.
- **Norm documents with non-first-order guards on the closure, core and order families** (reachability, n-ary atoms, arithmetic): the Lean norms theory is first-order. First-order documents are regenerated over the environment's FOL view.
- **N-ary definitions on the core family**: Lean's core layer glue projects unary and binary predicates only. This affects environment, model, graph, readings and bundles over such environments.
- **Coupled reading sets** (`couplings`, from main's rights work): every per-choice certificate and model is checked on the backend, but the coupled enumeration and its verdict are Python's (trusted, narrowed). This construct was added after the Stage 0 baseline.
- **Statement-layer environments** (soft norms, reports, speech acts, rights, quantities, alternatives) are out of the standalone, graph, readings and norms modes. Their own Lean routes validate them.

For information only, `--authority rust-experimental` is not a Gate 2 authority. That authority sends only evaluation and search to Rust, so every other dispatched operation there is `CheckerUnavailable`.

## Adapters

Every class-A operation of the plan's section 2.3 dispatches its own adapter:

| Operation (dispatch name) | Lean interface | Not yet on the backend |
|---|---|---|
| norms elaborate, certificate, conflict (`norms_elaborate`, `norms_certificate`, `norms_conflict`) | FOL family: `ve_norms_route` cases with data flags (`VE/Norms/Flagged.lean`); closure, core, order: the `family-norms` mode (`VE/Service/FamilyNorms.lean`) | non-first-order norm guards; statement layers |
| norms admission (`norms_admission`) | norms route `admission` | none |
| premise status, compare (`premise_status`, `compare`) | the constituents pinned to the backend (`dispatch.composed`) | none (compare is trusted, narrowed) |
| typing (`typing`) | `check` mode (statement layers reduced, `rights@0` and `speech-acts@0` included) | W6 quantity environments |
| environment, model and Background validation (`environment_validation`, `model_validation`) | `environment` and `model` modes, legacy envelopes included; claimed model identities checked in Lean | statement layers; core-family n-ary definitions; search candidates without an identity |
| definitions elaboration (`definitions_elaboration`) | route `background` | as model validation |
| bundle (`bundle`) | FOL without norms: route `bundle` (`bundle_sound`); every other family, norms environments and legacy envelopes: the `bundle` mode (`VE/Service/FamilyBundle.lean`) | statement layers; core-family n-ary definitions |
| parse and canonicalise (`parse`) | `parse` mode over the family surface parsers, legacy envelopes included, with the frozen runners' source limits | `definitions@0` sugar; statement layers |
| argument graph (`graph`) | `graph` mode: `VE/Service/Graph.lean` (FOL, v0), `VE/Service/Family.lean` (closure, core, order, ve.core@0.1) | statement layers; core-family n-ary definitions |
| readings (`readings`) | `readings` mode: `VE/Service/Readings.lean` (FOL), `VE/Service/Family.lean` (other families and legacy envelopes) | coupled reading sets; statement layers; core-family n-ary definitions |

Rules every adapter follows:

- **Lean decides, Python names.** Where Python's code is also the structural decoder (environment, model, definitions, bundle, parse), both run. If Lean accepts, the Python container is returned only if its identity is the one Lean recomputed. If both reject, Python's diagnostic names the rejection and carries the backend's rejection mark. If only Lean rejects, Lean's diagnostic is raised. If Lean accepts what Python's decoder rejects, the call is `CheckerUnavailable`.
- **Generators stay untrusted.** Python's provers, model searches, conflict-witness search and readings search only propose evidence. Lean checks it. A proposal Lean refuses is `CheckerUnavailable`, and an exhausted generator is `UNKNOWN`. A Lean `UnsupportedProfile` during a certificate replay is `CheckerUnavailable`, never `InvalidCertificate`.
- **Composing operations pin their constituents** to the backend (`dispatch.composed`).

## Lean changes in this checkpoint

No existing theorem statement changed. New glue is in new files under `lean/VE/Service/`, each covered by `audit.py`, and each new mode is pinned by an `rfl` dispatch theorem in `VE/Service/Protocol.lean` (`runMode_graph`, `runMode_readings`, `runMode_bundle`, `runMode_familyNorms`).

- `GenericGraph.lean`: `VE.Graph`'s named claim-graph checker and its proofs, over any formula type and model semantics (`check_sound`, conditional only on the certificate contract).
- `GenericReadings.lean`: the three readings theorems over any formula type with a disjunction (`readings_all_sound`, `readings_none_sound`, `readings_some_sound`).
- `Family.lean`: a context per family: formula decoder with AST limits and typing, identities, certificate decoder and binding, the route's Background (norms profile premises included, embedded on the order family), and model decoder. It also holds the graph and readings cases over those contexts and legacy contexts for `ve.core@0` and `ve.core@0.1`. Theorems:
  - `closure_/core_/order_graph_sound`, `_entails`, `_unfolds`;
  - `fol_/closure_/core_/order_readings_all/none/some_sound`, from each family's certificate soundness, budgeted refutation soundness (`refutesF/C/N/B_sound`) and model decoder theorems.
- `FamilyBundle.lean`: the bundle rules of `VE.Definitions.Bundle` over any family context, with the same cut-pattern proof (`bundle_sound`, `fol_/closure_/core_/order_bundle_sound`). Background leaves stay hypotheses; no family theorem discharges them.
- `FamilyNorms.lean`:
  - regeneration through the unchanged FOL norms route over the environment's FOL view;
  - certificates decoded, bound to the submitted and base environments, and checked by the family checker on the embedded premises (`closure_/core_/order_norms_certificate_sound`, `_conflict_target_sound`).
- `Standalone.lean`:
  - the model mode checks claimed identities;
  - the frozen envelopes are decoded (`decodeLegacy`) by the environment, model and parse modes;
  - `parse` reads `definitions@0` environments and applies the frozen runners' identifier and numeral limits;
  - typing reduces `rights@0` and `speech-acts@0`.
- `Norms/Plain.lean`: statement layers `rights@0` and `speech-acts@0` are reduced like `reports@0` and `soft-norms@0`, and the order certificate branch takes norms profile premises (`orderCertificate`).

## Verification

On the final code of this checkpoint (`VE_NATIVE_PREBUILT=1`, twelve file chunks at `-n 10` to `-n 14`):

- **`VE_AUTHORITY=lean`:** 4,472 passed and 6 skipped, 0 failures.
  - `test_agent_policy_rerun.py` (3 tests; its fixture takes 323 s under Lean) ran alone.
  - `test_english_mixed_merge_smoke` exceeds the tool's 10-minute limit as one test. Its work ran as five slices of `english_mixed.mixed(1)` with each configuration's seed unchanged (offsets 0–4, 4–8, 8–11, 11–14, 14–18): 0 row failures over 5,825 texts in 18 vocabularies, and the slices together exercise all 15 registered constructs.
  - One run of the full chunk at `-n 14` hit the 5-second interactive service timeout twice in `test_t1c.py` (the supervisor retries once, then `CheckerUnavailable`). The test passes alone and on the rerun. Timeouts are operational, never verdicts, and latency under load is a Gate 4 measurement.
- **Default authority (`VE_AUTHORITY` unset):** 4,472 passed and 6 skipped, with the same agent-policy run and the same five merge-smoke slices and results.
- **Parity:** `tools/stage2_parity.py --authority lean` gives 0 regressions and 0 `different` cells over 9,384 cells and every named probe.
- **Lean:**
  - `lake build` passes;
  - `lean/VE/Route/frozen.py` passes, re-hashed with the new modules listed;
  - `lean/checkers.lock` pins the rebuilt `ve_service`;
  - `python lean/audit.py` audits 216 source files and 1,915 named theorems, with only `propext`, `Classical.choice` and `Quot.sound`, and no `sorry`.
- **Rust:** `cargo test --release` gives 33 passed. The binary is unchanged and still matches `checkers.lock`.
- **Hooks and lints:**
  - `tools/inventory_lint.py`: 0 violations, 13 recorded exceptions (main's rights and speech-act surface decoders added);
  - `tools/check_lean_imports.py` passes;
  - the Python layer ledger records the Stage 2 adapter edges into `ve.backends`.
  - The merge commit was made with `VE_SKIP_HOOKS=1`, because main's five unmapped modules are main's documented drift.

## Trusted composition points

- **Soft and rights premises.** In the Lean Background adapter, soft premises come from a validated soft document and rights premises from a correlated rights document; they are not environment data. They are composed after Lean's base Background, and certificate and Rust cases carry them in that order. The soft and rights routes regenerate and compare them.
- **Statement-layer reductions.** `reports@0`, `soft-norms@0`, `rights@0` and `speech-acts@0` are removed before route, typing and Rust cases whose answers carry no identity of their own. Identities keep the submitted environment. A Rust countermodel check's identities are checked against the environment Rust was sent.
- **The FOL view of a family norm document.** Regeneration over the view is the FOL route's. That the view's first-order formulas mean the same in the family's structures is the embedding's (`Closure.embed`, `Core.embed`, `Order.embed`), which the family theorems use as the checked premise list.
- **Legacy Background.** Legacy v0/v0.1 envelopes have an empty Background.
- **Displays.** These are Python display built over checked values:
  - the CONFLICT record's `situation`;
  - the bundle report's leaves, reading choices and English;
  - the readings labels;
  - the argument record's per-edge diagnostics and package-wide status (trusted, narrowed).
- **Source to AST in the graph mode.** A claim's source is bound through its `source_id`; its parse is the parse adapter's.

## Test changes

- Earlier checkpoints:
  - `tests/test_assurance_manifest.py`: the accepted search-refusal change, and allowing `ve/backends/rust_jsonl.py` to start processes;
  - `tests/test_replay_conservativity.py`: Lean's invalid-replay wording;
  - `tests/test_stage2_dispatch.py`: fault injection patches the Rust client's runner.
- This checkpoint:
  - `tests/test_w6a_limit_generator.py`: `meter_python` selects the Python authority (accepted by the DRI, above), and the new Lean-authority counterpart covers the same cases;
  - `tests/test_lean_service.py`: the handshake and per-mode schema seeds gain the `bundle` and `family-norms` modes, as the protocol requires;
  - the Stage 2 adapter tests (`test_stage2_*.py`) were extended for the new scope. Two assertions that pinned the old scope were replaced: `definitions@0` sources without sugar are now Lean's, and closure packages now compose through Lean.

## Gate 2 checklist: met

| # | Criterion | Status | Evidence or gap |
|---|---|---|---|
| 1 | The full suite passes under `VE_AUTHORITY=lean` | **Met** | 4,472 passed, 6 skipped. The merge smoke passes in five slices, and the agent-policy rerun passes alone. |
| 1a | … for every class-A operation | **Met for the probe matrix; later 2c scope recorded** | Every class-A operation dispatches its own adapter. Of the previous 2,388 out-of-scope cells, 2,043 are now backend-decided. The 345 English-surface cells stay Python by the plan's decision (section 2.3, section 1.3). Rechecked on 2026-09-30: all 345 are `parse_accept` cells on `english-surface` rows (`parse_english`). 115 are accepted, and Lean types each of their ASTs; 230 are Python rejections. The remaining non-probe scope gaps above are 2c items the plan schedules before Gate 4. |
| 1b | Fixture changes limited to `checker_build`, `record_id` and documented message wording | **Met** | The two test changes that are not wording are accepted by the DRI: the search refusal (2026-09-29), and the Python-meter tests with their Lean-authority counterpart (2026-09-30). |
| 2 | The full Stage 0 baseline and public API agree under the section-5 projection | **Met as measured** | 0 regressions and 0 different cells over 9,384 cells and every named probe. The 115 `baseline drift` cells are main's `lean_outcome` field, and each ran its own adapter. |
| 3 | Matrix Lean/Rust column: empty regression diff | **Met under `VE_AUTHORITY=lean`** | Same report |
| 4 | Adapter fault-injection tests | **Met** | `tests/test_stage2_faults.py` and `tests/test_stage2_dispatch.py` pass under both authorities |
| 5 | The inventory lint passes | **Met** | 0 violations, 13 recorded exceptions |
| 6 | The `graph` mode is merged | **Met** | On every family and on the v0 and v0.1 envelopes |
| 7 | The readings checker is merged | **Met** | FOL, closure, core, order and legacy envelopes, with the three soundness theorems per family |

Stage 2 obligations outside the Gate 2 paragraph that are still open:

- the scope gaps above (2c, due before Gate 4);
- record wording and provenance: the argument record still says "Python replay checked", and the `authority`, `assurance`, `covered_operations` and `trusted` fields are not added;
- batching (one request per operation for `premise_status`, `check_readings`, `check_argument`, `check_step`);
- Rust parse diagnostics (codes and spans);
- the assurance manifest's bindings for the service adapters. It pins the new decoders and maps the new theorems, but its bindings still describe the one-shot runners.
