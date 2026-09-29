# Semantics migration Stage 2 progress

This checkpoint follows [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md), revision 3. Stage 0 and Stage 1 are merged on `mig/stage2`, and `main` was merged in at `3aab6626` (Lean service protocol 2, soft norms, units/time, attribution, causation, alternatives, the assurance manifest and the release gate). The Stage 0 `python.json` behaviour baseline remains the oracle. `VE_AUTHORITY` still defaults to `python`.

## Decisions recorded

- **DRI decision (orchestrator, 2026-09-29): the search-refusal change is accepted.** Gate 2 checklist item 1b listed one test change that is not wording: under a backend authority, a search witness that the Lean countermodel check refuses returns `CheckerUnavailable` (`tests/test_assurance_manifest.py`). This follows the fail-closed assurance rule: a refused witness is a generator/check disagreement, never a verdict. The same rule now governs every adapter added in this checkpoint (below).

## Gate 2 measurement

`tools/stage2_parity.py --authority lean` reruns every Stage 0 probe (9,384 cells plus the graph, boundary and feature probes). Inputs are built by the retained Python and each probed call runs under the backend authority. The named graph probes now run on the backend too, and the tool records the operations each one routes. It compares the result with the frozen baseline and with today's Python. The current report is [stage2-parity.md](stage2-parity.md). Cells fall into these classes:

| Class | Cells | Meaning |
|---|---:|---|
| regression | 0 | S→R/U/X, a changed S verdict status, or a changed R/U code |
| different | 0 | same cell and code, different record |
| baseline drift | 115 | differs from the baseline exactly as today's Python does (main added `lean_outcome` to bundle records) |
| same, adapter | 5,112 | identical; the operation's own adapter ran on the backend (3,220 at the previous checkpoint) |
| same, constituents | 1,782 | identical; only constituent adapters ran on the backend |
| same, python | 2,375 | identical; no adapter was dispatched |

All 11 named graph probes are `same, adapter`, and every named boundary and feature probe is `same` or `baseline drift`. None is `different`.

The 4,157 cells that are not `same, adapter` split into two groups:

- **1,769 cells never reach the operation.** The probe itself refuses the cell before calling it: for example "norms@0 required", "definitions@0 required", or an order environment with definitions, which is rejected when it is constructed. No adapter can cover these.
- **2,388 cells reach the operation without its own adapter deciding.** By family: order 1,589 of all non-adapter cells, closure 965, core 928 and FOL 675 (both groups included). They are:
  - operations whose Lean checker is FOL-only and that are not dispatched on the other families: argument graph, bundle, readings, and norms elaborate, certificate and conflict;
  - bundles over norms environments, because the route bundle case refuses `regulated`;
  - parse and canonicalisation over `definitions@0` environments, whose surface sugar (`no`, `every … that is`, `iff`, `define`) is in no Lean surface parser;
  - rejection cells that a constituent adapter decides before the operation dispatches: for example a conclusion that the typing adapter rejects, or a model whose stale identity the container check rejects.

For information only, `--authority rust-experimental` gives 2,609 regressions and 805 `different` cells, up from 2,497 and 690. That authority sends only evaluation and search to Rust, and now more operations dispatch, so more of them are `CheckerUnavailable` there. It is not a Gate 2 authority.

## Adapters added in this checkpoint

Every class-A operation of the plan's section 2.3 now dispatches its own adapter. Where the Lean interface does not cover an input, the adapter routes it to the retained Python statically (listed per row). This is a recorded scope gap, not a fallback after a failure.

| Operation (dispatch name) | Lean interface | Scope routed to the backend | Not yet on the backend |
|---|---|---|---|
| norms elaborate, certificate, conflict (`norms_elaborate`, `norms_certificate`, `norms_conflict`) | `ve_norms_route` cases, with data flags (`VE/Norms/Flagged.lean`) | FOL-family plain norm documents, with definitions and flags | closure, core and order families; soft, reports, alternatives and quantity environments |
| norms admission (`norms_admission`) | norms route `admission` | every `norms@0` envelope (Lean's envelope gate gives Python's FOL-only diagnostic) | none |
| premise status, compare (`premise_status`, `compare`) | the constituents pinned to the backend (`dispatch.composed`) | all | none (compare is trusted, narrowed, as the plan decides) |
| typing of `formula_from_data`/`formula_to_data` (`typing`) | `check` mode | all non-generated formulas | W6 quantity environments; generated Background premises keep a structural re-check |
| environment, model and Background validation (`environment_validation`, `model_validation`) | `environment` and `model` modes | ve.core@0.2 envelopes | statement layers and legacy envelopes (their routes validate them); core-family n-ary definitions; search candidates without an identity |
| definitions elaboration (`definitions_elaboration`) | route `background` | as model validation | as model validation |
| bundle (`bundle`) | route `bundle` (`bundle_sound`) | FOL family without norm declarations or statement layers | closure, core and order families; norms environments |
| parse and canonicalise (`parse`) | new `parse` mode over the family surface parsers | ve.core@0.2 without `definitions@0` | `definitions@0` sugar; statement layers |
| argument graph (`graph`) | new `graph` mode (`VE/Service/Graph.lean`) | FOL family (norms included) and the v0 envelope | closure, core and order families; ve.core@0.1 |
| readings (`readings`) | new readings checker (`VE/Service/Readings.lean`) | FOL family (norms included) | closure, core and order families |

Rules every adapter follows:

- **Lean decides, Python names.** Where Python's code is also the structural decoder (environment, model, definitions, bundle, parse), both run. If Lean accepts, the Python container is returned only if its identity is the one Lean recomputed. If both reject, Python's diagnostic names the rejection. If only Lean rejects, Lean's diagnostic is raised. If Lean accepts what Python's decoder rejects, the call is `CheckerUnavailable`. Python's rejection is never the verdict (`ve/backends/validation.py`).
- **Generators stay untrusted.** Python's provers, model searches, conflict-witness search and readings search only propose evidence. Lean checks it; a proposal Lean refuses is `CheckerUnavailable`, and an exhausted generator is `UNKNOWN`, which asserts nothing.
- **Composing operations pin their constituents.** Premise status, compare, argument checking and readings run every constituent replay and model check on the backend, whatever the per-operation overrides.

## Lean changes

- `VE/Norms/Flagged.lean` (new): data flags on norms elaborate, certificate and conflict. Flag premises come first in Background, as Python orders its generators. A conflict case with flags or definitions is checked over Python's base environment and base Background, against Python's conflict formulas, which keep defined atoms. Before this change, Lean answered UNKNOWN for every Python certificate over a document with definitions. Theorems: `norms_flagged_acceptance`, `norms_flagged_conflict_sound`, `norms_flagged_witness_sound`.
  - **Design risk closed.** The small-model restriction (`conflict_smallModel`) keeps universal premises but not the ∀∃ premise of a `total` flag. So the elaboration's `fragment` flag is false under a `total` flag. CONFLICT-FREE still needs certificates (binding decision 9.4), so no verdict depended on it.
- `VE/Service/Standalone.lean`:
  - environment and model modes now validate core-family definitions and flags (through `Core.Layers`), refuse n-ary core definitions as deferred, apply the norms profile check, reserve Python's `no`, and compute identities over canonical act phrases;
  - model identity now sorts domains as Python does;
  - new `parse` case;
  - `folBackground` regenerates Python's Background, norms profile premises included.
- `VE/Service/Graph.lean` (new): the `graph` mode. It recomputes claim and edge identities and certificate bindings. Background premises are explicit assumption leaves heading every deduction's premises, so the unchanged `VE.Graph.checkTableau` covers composition with Background. Theorems: `graph_sound`, `graph_entails`, `graph_unfolds`.
- `VE/Service/Readings.lean` (new): the readings checker. It rebuilds the premise lists (Background, fixed premises, per-set right-nested disjunctions or chosen readings) and checks the certificate or the admissible model. It carries the plan's three theorems, `readings_all_sound`, `readings_none_sound` and `readings_some_sound`, which the manifest moves from planned to proved. The plan named `Route/Readings.lean`; that file keeps its `readings_all_iff` lemma.
- `VE/Service/Protocol.lean`: new modes `parse`, `graph` and `readings`, each pinned by an `rfl` dispatch theorem.

## Verification

On the final code of this checkpoint (`VE_NATIVE_PREBUILT=1`, 16 file chunks at `-n 3`, four per call, then the three slow files):

- **`VE_AUTHORITY=lean`:** 3,973 passed and 6 skipped, 0 failures. `test_english_mixed_merge_smoke` exceeds the 10-minute tool limit, so its work ran as five parallel slices of `english_mixed.mixed(1)` (configuration offsets 0–4, 4–8, 8–11, 11–14 and 14–18). Every slice has 0 row failures, 5,825 texts in total, and the slices together cover all 15 registered node types. Each partial slice also reports the expected slicing artifacts ("registered construct has no exercising configuration" for constructs whose configurations fall in another slice).
- **Default authority (`VE_AUTHORITY` unset):** 3,973 passed and 6 skipped, and the same five merge-smoke slices with the same results. An explicit `VE_AUTHORITY=python` run was not repeated in this checkpoint; at the previous one it failed the alternatives tests by design (alternatives is Lean-only).
- **Parity:** `tools/stage2_parity.py --authority lean` gives 0 regressions and 0 `different` cells over 9,384 cells and every named probe.
- **Lean:**
  - `lake build` passes;
  - `lean/VE/Route/frozen.py` passes, re-hashed, with the three new modules listed;
  - `lean/checkers.lock` pins the rebuilt `ve_service`;
  - `python lean/audit.py` audits 191 source files and 1,646 named theorems, with only `propext`, `Classical.choice` and `Quot.sound`, and no `sorry`. No existing theorem statement changed.
- **Rust:** unchanged, so `cargo test` was not rerun.
- **New tests:**
  - `test_stage2_norms.py`: norms operations with flags and definitions; the witness flag check; a refused witness.
  - `test_stage2_validation.py`: every profile combination's environment and model; the decision rule; caches; identity sorting; definitions.
  - `test_stage2_bundle.py`, `test_stage2_parse.py`, `test_stage2_graph.py` and `test_stage2_readings.py`: each adapter against Python, Lean's identity and binding re-checks, and refusal or disagreement as `CheckerUnavailable`.
  - `test_stage2_faults.py`: fault injection per adapter.
  - `test_inventory_lint.py`.
  - Additions to `test_stage2_dispatch.py`: the pin and the composing adapters.

## Trusted composition points

- **Soft premises.** In the Lean Background adapter, soft premises come from a validated soft document and are not environment data. They are composed after Lean's base Background. Lean regenerates them in the soft route, and `soft_route.check_regenerated` compares them there.
- **Legacy Background.** Legacy v0/v0.1 envelopes have an empty Background: their Lean certificate runners bind case premises alone.
- **Reports and soft vocabularies.** `reports@0` and soft vocabularies are reduced before route cases whose answers carry no environment identity. The reports reduction is the vocabulary the Lean attribution decoder hands the route decoder.
- **Soft certificate premises.** Certificate cases on soft environments carry the soft document's premises, and the Lean norms route appends them after the profile premises. This is the same composition point as soft Background.
- **Displays.** These texts are Python display built over checked values:
  - the CONFLICT record's `situation` (the rules Python selects at the checked tuple);
  - the bundle report's leaves, reading choices and English;
  - the readings labels;
  - the argument record's per-edge diagnostics and package-wide status (trusted, narrowed, as the plan decides).
- **Source to AST in the graph mode.** A claim's source is bound through its `source_id`. Its parse is the parse adapter's; the graph mode checks the claim's AST.

## Test changes

- Earlier checkpoints:
  - `tests/test_assurance_manifest.py`: the search-refusal change, now accepted (see Decisions), and allowing `ve/backends/rust_jsonl.py` to start processes;
  - `tests/test_replay_conservativity.py`: Lean's invalid-replay wording;
  - `tests/test_stage2_dispatch.py`: the fault injection patches the Rust client's runner.
- This checkpoint changed no existing assertion. `tests/test_lean_service.py`'s scripted service handshake and its per-mode schema seeds gained the three new modes (`parse`, `graph`, `readings`), as the protocol requires.

## Gate 2 checklist: not passed

Each criterion from the plan's Gate 2 paragraph, in order:

| # | Criterion | Status | Evidence or gap |
|---|---|---|---|
| 1 | The full suite passes under `VE_AUTHORITY=lean` | **Met** | 3,973 passed, 6 skipped. The merge smoke's work passes in five slices (it exceeds the tool's 10-minute limit as one test). |
| 1a | … for every class-A operation | **Partly met** | Every class-A operation dispatches its own adapter, and 5,112 cells run it. Outside each adapter's recorded scope (table above), 2,388 reachable cells still take Python's verdict or a constituent-only path. The largest gaps are the closure, core and order families for graph, bundle, readings and the norms operations, and `definitions@0` parsing. |
| 1b | Fixture changes limited to `checker_build`, `record_id` and documented message wording | **Met** | The one non-wording change (search refusal as `CheckerUnavailable`) is accepted by the DRI decision above. This checkpoint changed no existing assertion. |
| 2 | The full Stage 0 baseline and public API agree under the section-5 projection | **Met as measured** | 0 regressions and 0 different cells over 9,384 cells and every named probe. The 115 `baseline drift` cells are main's `lean_outcome` bundle field, which today's Python shares. |
| 3 | Matrix Lean/Rust column: no S→R, S→U or code change (empty regression diff) | **Met under `VE_AUTHORITY=lean`** | Same report. `rust-experimental` is not a Gate 2 authority. |
| 4 | Adapter fault-injection tests | **Met** | `tests/test_stage2_faults.py`: each of the 23 dispatched operations with a missing Lean service, an unlisted build, a crash and a hang, and the four Rust-backed operations with a missing, unlisted, crashing and timed-out Rust checker. All give `CheckerUnavailable`, never a `VEError`, and the Python path is never dispatched in the backend's place. `tests/test_stage2_dispatch.py` keeps the dispatch-level cases. |
| 5 | The inventory lint passes (no retained module imports a class-A body) | **Met** | `tools/inventory_lint.py`: 0 violations and 9 recorded exceptions, each with its reason (untrusted generators, surface decoders typing open formulas, structural re-typing of generated premises). `tests/test_inventory_lint.py` keeps it at zero. Building it removed two redundant Python Background validations (`evaluate._validate_model` and the norms witness decoder) and turned `validate_background` into an adapter. |
| 6 | The `graph` mode is merged | **Met** | `VE/Service/Graph.lean` and the `graph` adapter. All 11 graph probes compose through it. Closure, core and order packages are not composed by Lean yet (see 1a). |
| 7 | The readings checker is merged, or its exclusion from `covered_operations` is recorded | **Met** | `VE/Service/Readings.lean` with `readings_all_sound`, `readings_none_sound` and `readings_some_sound`, and the `readings` adapter. It covers FOL-family environments; readings on other families are not dispatched (see 1a). |

Stage 2 obligations outside the Gate 2 paragraph that are also open:

- **Coverage closure (2c) for the remaining families:**
  - graph, readings and bundles on the closure, core and order families (their Lean checkers are FOL-only);
  - norms elaborate, certificate and conflict on those families;
  - bundles over norms environments;
  - the `definitions@0` surface in the Lean parsers;
  - n-ary definitions on the core family;
  - order-family certificates with profile pairs (still `CheckerUnavailable`).
- **Record wording and provenance.** The plan's documented wording change for composed argument records ("Lean graph report checked" instead of "Python replay checked") is not applied: records are unchanged for parity. The `authority`, `assurance`, `covered_operations` and `trusted` record fields are not added yet.
- **Batching:** one request per operation for `premise_status`, `check_readings`, `check_argument` and `check_step`.
- **Rust parse diagnostics:** codes and spans.
- **Assurance manifest:** the new Lean modules are pinned decoders, and the readings and graph theorems are mapped. The manifest's bindings still describe the one-shot runners, not the service adapters.

Suggested order for the next session: the closure, core and order families for graph, readings and bundle (Lean checkers over those formula types), then the norms operations on those families, then the `definitions@0` surface in the Lean parser, then record provenance and the documented argument wording.
