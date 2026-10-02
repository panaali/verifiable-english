# Layers, plan 2: retiring the recorded exceptions and splitting `ve-core`

Status: plan only, no code changes. Branch `design/layers2` at `d9f8c4aa` (main).
Companion to [`ARCHITECTURE-LAYERS.md`](ARCHITECTURE-LAYERS.md), whose exception
counts (12 Python, 16 Lean) are stale; the ledgers hold **50 Python** keys and
**22 Lean** keys today.

## 0. Scope and what is out of scope

| Ledger group | Keys | Handled here |
|---|---:|---|
| Python structural edges (kernel ↔ profile ↔ surface ↔ tools) | 24 | Part 1, steps P1–P20 |
| Python app edge `ve.assist.cli -> ve_experiments.assist_haiku` | 1 | P21 (decision needed) |
| Python stage-2 authority adapters `ve.* -> ve.backends.*` | 25 | **Deferred** to `docs/spec/SEMANTICS-MIGRATION-PLAN.md` stage 5. The same-signature wrappers that survive stage 5 still call `ve.backends`, so deleting the Python bodies does not remove these edges; only moving `ve.backends.{dispatch,lean_service,service_schema,rust_jsonl,lean_runner,validation}` inward does. Two harmless preparations are listed as P22. |
| Lean edges | 22 | Part 2, steps L1–L9; two edges (L9) need a decision |
| Rust intra-crate edges (unenforced today) | 3 | Part 3, steps R1–R4 |

Invariants and what protects them (from reading `ve/assurance.py`, `ve/identity.py`,
`tools/rust_build.py`, `lean/VE/Route/frozen.py`):

- **Identities** are SHA-256 over an ASCII domain string plus canonical JSON
  (`ve/wire.py:81-99`). No identity reads a Python module name, class
  `__qualname__`, Rust crate or type name, or Lean module name. Pure moves cannot
  change them; the suites in §0.2 prove it anyway.
- **Assurance manifest** (`ve/assurance-manifest.json`) pins every
  `@semantic_entry` as `module:qualname`, the three Lean call sites, every broad
  `except` handler by file, and ~30 Lean decoder files by sha256 + line count +
  ranges. Rule for this plan: a step may relocate a pinned Python function only
  where the step says so (P20 is the only one) and then regenerates with
  `python tools/assurance_manifest.py --write`.
- **Lean sources** are all pinned in `lean/VE/Route/frozen-sources.sha256`;
  `Main.lean` is pinned through `MAIN_BASE`. Every Lean edit rehashes its files
  (`sha256sum` from `lean/`, then `python3 VE/Route/frozen.py`).
- **Binaries** are pinned in `lean/checkers.lock`: `rust_jsonl` (the release `ve`)
  and `ve_service`. Any Rust or Lean edit changes a binary and needs a repin
  (`python3 tools/rust_build.py` prints the hash; `ve_service` is hashed by hand).
- **Python/Lean/Rust agreement**: conformance fixtures, the P0 three-way, the
  stage-2 parity report and the shadow authority (§0.2).

### 0.1 Rules every step follows

1. One commit removes one group of ledger keys: delete the imports, delete the keys,
   run `uv run --group dev python tools/check_python_layers.py --write` (Python) or
   `python3 tools/check_lean_imports.py` (Lean). The checkers reject a stale key
   and a new edge, so the ledger cannot drift.
2. **Facade rule.** Every moved name is re-exported from its old module. `ve/__init__.py`
   keeps its 83 names (P20 changes one source module). Tests may keep importing private
   names (`ve.search._used_predicates`, `ve.evaluate._Evaluator`, …) through the old module.
3. A new `ve/<name>.py` or package is added to `tools/layer_policy.py` `PYTHON` **and**
   the table in `ARCHITECTURE-LAYERS.md` in the same commit (`tools/test_layer_policy.py:262-274`
   enforces the match; an unmapped module fails the checker and the selector).
4. Never move a Lean call site (`ve.admission:_lean_quantity_admission`,
   `ve.argument:_lean_deductions`, `ve.bundle:lean_bundle_verdict`) or a broad-except handler.
5. Reclassification (changing a module's layer without touching its code) is used only
   where the module's duty is argued to be the outer layer. Each such step states the argument.
6. Each step's commit runs its listed suites; a merge to main runs the full gate
   (`python3 tools/select_tests.py --full --run`, or `python3 tools/gate.py`).

### 0.2 Suite bundles referenced below

| Code | Command / files | What it proves |
|---|---|---|
| **S** | `python3 tools/select_tests.py --run` on the working tree | Layer checkers, `test_layer_policy`, axiom audit, always-run conformance (`test_conformance`, `test_lean_conformance`, `test_replay_conservativity`, `test_p0_three_way`, `test_rust_conformance`), plus selected tests |
| **M** | `tests/test_assurance_manifest.py test_inventory_lint.py test_background.py test_surface_registry.py test_precommit_hook.py test_stage0_probe_matrix.py` | Pins by module/qualname, inventory tables, path-coupled tests |
| **P** | `uv run python tools/stage2_parity.py --authority lean --write && git diff --exit-code docs/spec/stage2-parity.md`; `tests/test_stage2_*.py`; optionally the full suite under `VE_AUTHORITY=shadow` with an empty verdict section in `ve-shadow.jsonl` | Python/Lean agreement on 9,384 probe cells; fail-closed dispatch |
| **L** | `lake build`, `python3 lean/audit.py`, rehash + `frozen.py`, `check_lean_imports.py`, manifest decoder pins, `ve_service` repin, `tools/lean_service_parity.py`, `test_lean_conformance`, `test_p0_three_way`, `test_lean_service.py` | Lean edits change nothing observable |
| **R** | `python3 tools/rust_build.py test --locked --all-features --manifest-path rust/Cargo.toml -- --test-threads=1`; `cargo fmt --check`; clippy `-D warnings`; `python3 tools/check_rust_deps.py`; `python3 tools/rust_build.py --check` then repin; `tests/test_rust_reproducible.py`, `test_rust_conformance.py`, `test_p0_three_way.py`, `test_*_three_way.py`, `test_*_differential.py`, `test_risk_profile.py` | Rust output and reproducibility |
| **D** | New `tools/rust_output_diff.py` (R0): runs the previously pinned binary and the new one over `ve conformance` / `ve jsonl` for every `conformance/*.json` corpus and `lean/VE/Route/examples/route-cases.json`, and over `parse`, `format`, `evaluate`, `canonical-json` on the fixture sources; compares stdout, stderr and exit codes byte for byte | "No Rust output change" as a direct differential, independent of the fixtures' coverage |

Effort scale: **S** ≤ half a day, **M** 1–2 days, **L** 3–5 days, each including one full-suite run.

### 0.3 One new mechanism: bound slots (`ve/slots.py`, kernel, ~40 lines)

Five edges call a **pinned, Lean-dispatching** profile or tool function from inside a
kernel or profile constructor, at a position that fixes diagnostic precedence:
`Environment._decode` → `definitions.compile_definitions` and `risk.validate_block`;
`FiniteModel._decode` → `definitions.compile_definitions` + `background._validate_background_python`;
`SpeechDocument` → `speech_english.parse_speech` and `vacuity.premise_status`. The callee cannot
move inward (manifest pin, authority dispatch, recursion on `Environment`), and moving the
call to the route changes which error fires first and breaks constructor-raise tests and the
Lean conformance comparisons. The ledger reasons already ask for "a profile-owned hook".

Design: `class Slot(name)`; `bind(fn)` once (a second bind with a different function raises);
`__call__` raises `SlotUnbound(name)` when unbound (fail closed, never silent). Providers bind at
import time at the bottom of their own module, so no pinned function moves. `ve/__init__.py`
imports the providers (it already imports layer-4 modules and is exempt from the layer rule).
`tests/test_slots.py` pins each slot's bound `module:qualname`, asserts all are bound after
`import ve`, and asserts the unbound error. `ARCHITECTURE-LAYERS.md` gains a bindings table
replacing the removed ledger rows, so the inversion stays as visible as the exceptions were.

## 1. Part 1: Python edges, lowest risk first

New kernel modules: `ve/slots.py`, `ve/tokens.py`, `ve/semantics.py`, package `ve/blocks/`
(`units.py`, `speech_acts.py`, `risk.py`). Reclassified: `profiles` → layer 1, `alternatives` → layer 4.

| # | Ledger keys removed | Change (files) | Facade kept by | Proof | Effort |
|---|---|---|---|---|---|
| P1 | `evaluate -> surface.registry` | Delete never-registered hook lookups: `evaluate.py:77-80` (`evaluator_hook`), `ast.py:250-254` (`typecheck_hook`), `:401-404` (`wire_encoder`), `:482-484` (`wire_decoder`), `closure.py:120-125` (`traversal_hooks["substitute"]`; `substitute` has no callers, delete it). Drop those four slots from `SurfaceRecord` (`surface/registry.py:8-33`); nothing registers them. | n/a (deletions) | S, M; new test: `SurfaceRecord` field set | S |
| P2 | `wire -> surface.registry`, `ast -> surface.registry` | Kernel tag tables in `ast.py`: `WIRE_TAGS: dict[type,str]`, `NODE_TYPES` (inverse), `WIRE_ARITY` (top/bottom 1; not 2; unary, eq, lt, le, and, or, implies, forall, exists, atom 3; binary 4; reach 5). `wire.formula_tag_arity` (`wire.py:111-115`) reads `WIRE_ARITY`; `ast.py:434-435,527-529` read the tables instead of `by_tag/by_node`. `registry.register()` asserts `node_type`/`wire_arity` agree with the kernel tables for every tag that sets them. | registry keeps its fields for surface users (`formula_arities`, `by_node`) | S; new test: every registered record with `node_type` or `wire_arity` matches the kernel table (guards tags beyond the 15 listed); `conformance/wire.json`, `parser.json` via S | S |
| P3 | `ast -> surface.nary` | Move the side-effect import `ast.py:552` to `ve/surface/__init__.py` beside `alternatives`/`risk`. After P2 the kernel never reads the registry, so registration timing only matters for surface/tool users, which import `ve.surface.*` themselves. | n/a | S; new test: `import ve` leaves `by_tag("atom")` registered; `test_precommit_hook.py:110,201` switch their example edge to one that stays (`ve.ast -> ve.backends.dispatch`) | S |
| P4 | `closure -> surface.registry` | `closure.map_free` (`closure.py:80-111`) gets a native `ast.Atom` branch mirroring `surface/nary.py:48-54`; drop the `traversal_hooks["map_free"]` lookup. `Atom` is a kernel class, so the kernel may traverse it. | n/a | S; `conformance/closure.json`, `test_closure*.py`, closure three-way | S |
| P5 | `environment -> profiles` | Reclassify `ve.profiles` to layer 1: it imports only `ve.errors` and holds the route vocabulary (`LANGUAGE`, `SPEC_REVISION`, `checker_family`) that `Environment.identity_version` depends on, i.e. kernel data. Edits: `layer_policy.py:18` (append, keeping the literal `"ast environment errors` that `test_precommit_hook.py:228` asserts), docs table, `tools/mutation_check.py:29` picks another layer-2 example (`ve/order.py`). Side effect: `ve/backends/validation.py:27` (`STATEMENT_LAYERS`) becomes an inward import, helping P22. | n/a | S, M | S |
| P6 | `alternatives -> backends.lean` | Reclassify `ve.alternatives` (32 lines, pure Lean transport, only importer `admission.py:509` is layer 4) to layer 4. | n/a | S | S |
| P7 | `reports -> admission`, `speech_acts -> admission` | New kernel `ve/tokens.py`: `_TOKEN`, `token`, `ATOMIC_KINDS`, `ACTS`, `MODALITIES`, `RELATIONS`, `_check_kind` (`admission.py:26-44,129-156`, ~35 lines, needs only `re` and `ve.errors`). `reports.py:12`, `speech_acts.py:207,502,657` import from `ve.tokens`. | `admission` re-exports (14 own uses; importers `readings`, `speech_document`, `openterms`, `discourse`, `document`, `norm_admission`, `norm_defaults_route`, `quantity_admission`, `test_lean_service_schema.py:911-928`) | S, M; update `tools/semantic_inventory.py:92` | S |
| P8 | `speech_acts -> norm_admission` | Move `_check_quoted` (`norm_admission.py:20-25`) into `norms.py`; `speech_acts.py:591,658` import from `norms` (already imported at `:16`). | `norm_admission` re-exports (own `:98`, `document.py:557`) | S | S |
| P9 | `norms -> search`, `rights -> search`, `softnorms -> search`, half of `units -> search` | Move `_used_predicates` (`search.py:232-256`) and `_node_count` (`search.py:77-92`) into `ast.py`, with a native `Atom` branch (as P4) so no registry import appears; `norms.py:18`, `rights.py:16`, `softnorms.py:21`, `units.py:599` import from `ast`. | `search` re-exports (own uses `:98,595,751,764,840`; `norm_defaults.py:33`, `document.py:510`, `norm_defaults_english.py:247`, `usecases/agent-policy/check.py:55`, `tests/test_closure.py:214`, `test_w6a2_looprecheck1.py:23`) | S, M; norms/softnorms/rights suites and three-ways; `semantic_inventory.py:85` | S |
| P10 | rest of `units -> search` | Move `quantity_countermodel` + `BUDGET_EXHAUSTED` (`units.py:634-649`) into `ve/quantity_admission.py` (layer 4, already imports `units`). It calls `check_countermodel`, a pinned dispatching entry, so it cannot go inward, and **no re-export is possible** from `units` (any import recreates the edge). | none; rewrite 8 importers: 7 tests (`test_w6a_looprecheck1/2`, `test_w6a_limit_generator`, `test_w6a_limits`, `test_units_lean_w6a`, `test_w6a2_numeral_characters`, `test_w6a_route_limits:301,344`) and `usecases/safety-framework/severity_and_dates.py:37` (a script, not a frozen key) | S; W6 suites | S |
| P11 | `environment -> units` | New kernel package `ve/blocks/` with `units.py` (~225 lines: `units.py:17-41,44-247`: `validate_units`, `validate_tag`, `validate_slot_units`, `validate_extension`, display helpers, `W6_PROFILES`, `RISK_UNIT_PROFILES`, `W6_PROFILE_TEXT`). Move `MAX_NUMERAL_CHARS` (`ast.py:163`) to `limits.py` to avoid an `ast ↔ blocks` cycle; `ast` re-exports. `environment.py:338,353,421,500,514,605` import `ve.blocks.units`. Add `blocks` to `PYTHON[1]`. | `units` re-exports (`surface/time.py:14-15`, `test_w6a_looprecheck1.py:22`, `test_w6a_review_regressions.py:16`, `test_risk_profile.py:83`) | S, M; W6 suites, `test_units_rust_w6a`, `test_units_lean_w6a`, `test_w6b_gates` | M |
| P12 | `environment -> speech_acts` | `ve/blocks/speech_acts.py` (~75 lines): `validate_scope`, `check_templates`, `ATTACHED_SLOT`, `_TOKEN`, `_PHRASE`, `_SURFACE_SPACES`, `_WORD_BREAK` (`speech_acts.py:19-20,26-72,75-101,256,262`); `environment.py:520` imports it. | `speech_acts` re-imports (uses at `:297-380,540`) | S; speech-acts suites and conformance | S |
| P13 | pure half of `environment -> risk` | `ve/blocks/risk.py`: `check_route_declarations` (`risk.py:207-215`), `decode_block` (`:70-128`), `check_alt_reserved` (`:131-136`) and helpers (`:21-25,31-67`); `environment.py:516` imports it. `check_block` stays (P15). | `risk` re-exports | S; `test_risk_*` | S |
| P14 | `environment -> definitions` | Add `ve/slots.py` (§0.3) and slot `ENVIRONMENT_DEFINITIONS`; `environment.py:618-619` calls the slot at the same position. `definitions.py` binds `compile_definitions`-based check at import; `ve/__init__.py` imports `definitions`. | n/a | S, M, P; new `tests/test_slots.py`; `test_definitions.py:131-139` (constructor still raises) | M |
| P15 | rest of `environment -> risk` | Slot `ENVIRONMENT_RISK_BLOCK` bound by `ve.risk` to `validate_block` (whose `check_block` calls pinned `background.dependency_order`, `risk.py:141,162`); `environment.py:558-560` calls the slot. `ve/__init__.py` imports `risk`. | n/a | S, P; `test_risk_diagnostics.py:202`, `test_risk_every_diagnostic.py:267`, `test_risk_profile.py:105` (pinned `DependencyCycle` text) | S |
| P16 | `model -> definitions`, `model -> evaluate`, `model -> background` | Two slots. `MODEL_DEFINED_RELATIONS`: `model.py:183-204` moves verbatim into `definitions.py` as `model_defined_relations(cls, env, domains, constants, relations, tuple_count) -> int` (mutates `relations`, keeps the in-loop `MAX_TUPLES` and budget diagnostics and their order). `MODEL_BACKGROUND`: `model.py:214-215` → `background.py` binds `_validate_background_python`. `FiniteModel.from_dict` (pinned) does not move. | n/a | S, M, P; `test_definitions*`, `test_background`, `test_definitions_differential`; add the new function to `tools/inventory_lint.py` `BODIES["ve.background"]`/`["ve.definitions"]` | M |
| P17 | none (alignment) | Move `Explanation`, `_Exhausted`, `_Evaluator` (`evaluate.py:16-28,43-44,47-169`) to kernel `ve/semantics.py`, matching Lean `VE.Semantics` (layer 1) and the Rust `Evaluator` move in R1. `evaluate.py` keeps the pinned `evaluate`. Optional but recommended for one layer map across the three implementations. | `evaluate` re-exports (`search.py:14`, `speech_acts.py:949,973`, 35 test files) | S, M, P | S |
| P18 | `speech_acts -> speech_english` | Slot `SPEECH_WORDINGS`; `SpeechDocument._check_wordings` (`speech_acts.py:809-836`) moves into `speech_english.py` (which already imports `speech_acts`, so today's cycle breaks) and binds; the call at `:623` becomes `SPEECH_WORDINGS(self)`, keeping `ModeMismatch`/`QueryMismatch` precedence over `UnknownRule` (`:627-640`). `ve/__init__.py` imports `speech_english`. | n/a | S, P; `test_speech_acts.py:131-317`, `test_speech_acts_conformance.py` (constructor raises, Lean comparison) | S |
| P19 | `speech_acts -> vacuity` | Slot `SPEECH_PREMISE_STATUS` bound by `vacuity.premise_status` (pinned, dispatching); `speech_acts.py:938-939` calls the slot. `ve/__init__.py` imports `vacuity`. | n/a | S, P; `test_speech_acts.py:158-318`, conformance `:225,411,919-989` | S |
| P20 | `english -> argument` | Move `parse_english_argument` (`english.py:1738-1770`, `@semantic_entry("english.admission")`) into `argument.py`, importing `_parse_english_document` lazily. **Manifest relocation**: `ve.english:parse_english_argument` → `ve.argument:...` (`assurance-manifest.json:871`), regenerate. `ve/__init__.py:31` imports it from `argument`; `test_assurance_manifest.py:1123,1138` update; the `argument.check_argument` monkeypatch (`:1145`) keeps working since the function resolves it as a module global. | facade (`tests/test_natural.py:12`, `conformance/natural_surface.py:8`) | S, M, P | M |
| P21 | `assist.cli -> ve_experiments.assist_haiku` | `cli.main(argv=None, *, proposer_factory=None)`; keep `_proposer` as default hook name (`test_assist.py:709` patches it); new app entry `ve_experiments/assist_cli.py` passes `ClaudeProposer`. **Behaviour change**: `python -m ve assist propose` loses the live proposer (`ve/__main__.py:51-53` is layer 4 and cannot import apps either). `tools/test_layer_policy.py:77` changes (minimum layer 5). | `cli` API unchanged | S; `test_assist.py` | S |
| P22 | none (stage-5 preparation) | Move `AdmissionError` (`admission.py:38-39`) to `ve.errors` (admission re-exports) so `ve/backends/diagnostics.py:47` imports inward. With P5, `ve.backends.dispatch`, `lean_service`, `service_schema`, `validation`, `lean`, `rust_jsonl` then import only layers ≤ 1. Open: import-linter may not accept a subpackage of a layer-4 package at layer 1; a sibling package may be needed at stage 5. | — | S, M | S |

Ordering rationale: P1–P4 touch only dead code and data tables; P5–P6 are policy-only; P7–P13
are pure moves with re-exports; P14–P19 introduce the slot inversion (one mechanism, five uses);
P20 is the single manifest relocation; P21 is the single user-visible change. Dependencies:
P13 before P15; P14 before P15, P16, P18, P19; P2 before P3 (registration timing). Everything else is independent.
After P21, re-run `tools/mutation_check.py` and refresh the evidence tables in `ARCHITECTURE-LAYERS.md`.

## 2. Part 2: Lean edges

Thirteen edges go away by reclassification only (no Lean edit, nothing to rehash); six need
small edits; two (edges 1 and 5 of the ledger) have no small fix. Policy edits live in
`tools/layer_policy.py` `lean_layer` as explicit sets evaluated before the prefix rules.

| # | Ledger keys removed | Change | Argument / side effects | Proof | Effort |
|---|---|---|---|---|---|
| L1 | `TableauExtendedRules -> Closure.Congruence`, `TableauExtendedInduction -> Closure.Induction`, `TableauExtended -> Closure.Substitution`, `TableauExtendedExtra -> Closure.PathRules`, `CertificateWire -> Closure.Bridge` | Reclassify the six `VE.TableauExtended*` modules and `VE.CertificateWire` to layer 2. | All six tableau modules are `namespace VE.Closure.Tableau`: closure-profile proof code filed as kernel. `CertificateWire` decodes closure certificates. Importers (`Route.Checker`, `Route.Steps`, `Main`, `Route.Wire`, `Order.*`, `Service.Protocol`, `Audit`) are all ≥ 2. | S (`check_lean_imports`, `test_layer_policy`, `test_precommit_hook` Lean strings) | S |
| L2 | `Core.Bridge -> Route.Gate`, `Core.Conservativity -> Closure.Consequence`, `Core.Route -> Route.{Checker,Gate,Route}`, `Core.Wire -> Route.Wire`, `Core.Layers -> Route.Wire` | Reclassify `VE.Core.{Route,Bridge,Wire,Layers,Conservativity}` to layer 2 and `VE.Core.Checks` to layer 5 (same rule as `VE.Route.Checks`). | These are the core family's routed checker, gate, wire and layer glue, the same duty as `VE.Route.*`. The kernel keeps `VE.Core.{Syntax,Finite,Paths,PathRules,Substitution,Congruence,Induction,Consequence,TableauExtended*}`. No layer-1 module imports the moved six (importers: each other, `EvaluationCounts`, `Route.Run`, `Service.Standalone`, `Audit`). `tools/test_layer_policy.py:206-223` (`Core.Wire -> Route.Run` outward) still holds. The redundant imports `Core/Route.lean:2,4` and `Core/Layers.lean:2` may be deleted later; that needs a rehash, so not here. | S | S |
| L3 | `Discourse.English -> English.Proofs` | Reclassify `VE.Discourse.English` to layer 3. | Its content is English-surface theorems; importers are `VE.lean` and `Audit` (layer 5). | S | S |
| L4 | `Discourse.Access -> English.Parse`, `Discourse.Manifest -> English.Statements` | New `lean/VE/Tok.lean` holding `inductive Tok` (`English/Lexicon.lean:18-21`) under `namespace VE.English`; `Lexicon` imports it; `Discourse/Manifest.lean:2` becomes `import VE.Tok`; delete `Discourse/Access.lean:2` (redundant, it only used `Tok`). | Every Discourse module except `.English` uses only `Tok`; the ledger's "walks parse trees" is inaccurate. Rehash 3 files + add `Tok.lean`; `ve_service` repin; `VE.Tok` is layer 2 by default rule. | L; discourse suites and three-way | S |
| L5 | `Norms.Plain -> Route.Run`, `Discourse.Loader -> Route.Run` | (a) Reclassify `VE.Norms.Plain` to layer 4: it delegates to `Route.Run.runCase` (`Plain.lean:217`), so it is runner glue; importers `Norms.Run`, `Service.Standalone` are 4. (b) New `VE/Route/Dispatch.lean` with `claimJson`, `caseKind`, `decodeRouteVocabulary` (`Run.lean:34-41,59-64`) keeping `namespace VE.Route.Run`; `Run` imports it; `Loader.lean:2` → `import VE.Route.Dispatch`; `Discourse/Run.lean` adds `import VE.Route.Run` (it uses `runCase` transitively today). | `Main.lean` keeps `import VE.Route.Run` (`MAIN_BASE` untouched). The manifest `dispatch` file lists (`assurance-manifest.json:535,536,679,716,843`) must include `Dispatch.lean` because `caseKind` carries the kind literals; regenerate. Rehash `Run`, `Loader`, `Discourse/Run`, add `Dispatch`. | L; norms and discourse suites | M |
| L6 | `Order.WireGate -> Order.Surface` | New layer-3 `VE/Order/SurfaceGate.lean` holding `surface_route_gate`, `combined_profiles_surface_rejected` (`WireGate.lean:44-86`) and `Route.Gate.legacy_routes_reject_v02` (`Gate.lean:192-211`, which reaches `Order.Surface` only transitively today and would stop elaborating). `WireGate.lean:2` → `import VE.Order.Wire`; `Audit` imports `SurfaceGate`; add it to the layer-3 set and to manifest `other_json`. | Manifest repin for `Route/Gate.lean` (hash and line count; range [126,163] unchanged). Rehash 4 files. | L | M |
| L7 | `Core.RoundTrip -> Core.Surface` | Delete the unreferenced `VE.Core.Bridge.runCase`/`runCaseReported` (`Core/Bridge.lean:127-157`) and `Core/Bridge.lean:2`; reclassify `Core.RoundTrip` to layer 3; `Audit` imports `Core.RoundTrip` (its `#print` lines 1021-1024 rely on the transitive import); `Core.Checks` adds `import VE.Core.Surface`. | "Unreferenced" must be confirmed by `lake build` after deletion. Manifest repin for `Core/Bridge.lean` (range [10,126] unchanged). | L | S |
| L8 | `RoundTrip -> LexicalProofs` | Reclassify `VE.RoundTrip` to layer 3 (it is `namespace VE.Surface` round-trip proofs) and delete the unused `EnvironmentProofs.lean:2` import so `EnvironmentProofs` stays kernel. | Other importers (`ParserContracts`, `Core.Surface`, `Closure.Surface`) are layer 3. Rehash `EnvironmentProofs`. | L | S |
| L9 | `Bridge -> Surface`, `Closure.RoundTrip -> Closure.Surface` | **Decision needed.** Root cause: the legacy evaluate runners `VE.Bridge.runCase` (`Bridge.lean:264-270`) and `VE.Closure.Bridge.runCase` (`Closure/Bridge.lean:67-97`) check canonical text with the surface printer/parser and are called from layer 2 (`Order.ProfileGate.runEvaluationCase`, `ProfileGate.lean:27`) and by theorems in `ProfileGate`, `WireGate`, `Route.Gate`. Reclassifying `Closure.RoundTrip` only renames the edge to `Closure.Bridge -> Closure.RoundTrip`. | Option A, policy reversal: formal-notation parsers (`VE.Surface`, `SurfaceProofs`, `LexicalProofs`, `Core.Surface`) become layer 1 and `Closure.Surface`, `Order.Surface` layer 2. No Lean edit; but it contradicts the layer table, breaks `test_precommit_hook.py:215,272,312` (`VE.Core.Planted -> VE.Surface (layer 1 -> 3)`) and undoes L8. Option B, move the runners outward: both `runCase`s, `runEvaluationCase` and their theorems into a layer-3 module. Costs: `Main.lean` must import it (edit `MAIN_BASE` in `frozen.py:15-18`), manifest `dispatch` entries move (`"countermodel"` at `Bridge.lean:260`), pinned decoder files `Bridge.lean`, `Closure/Bridge.lean` change, `Audit` imports change. Recommendation: B, as its own reviewed change after L1–L8. | L, P | L (B) |

Lean tooling to add first (L0, S): `lean/VE/Route/frozen.py --write <files>` to rehash listed
files, and a `tools/repin_checkers.py` that hashes both binaries into `lean/checkers.lock`.
Both are manual today (`tools/hooks/README.md:50-52`), which is where mistakes will happen.

## 3. Part 3: Rust, `ve-core` into kernel, profile and surface crates

Current graph (`rust/ve-core/src`, 7,135 lines, all modules private `mod`, curated `pub use` in
`lib.rs:18-38`). Three edges cross outward inside the crate and form one strongly connected set:

| Edge | Site | Python twin |
|---|---|---|
| kernel `environment` → profile `route` | `environment.rs:4,553` uses `dependency_order` (`route.rs:134-181`, pure) | `environment -> definitions` |
| kernel `model` → profile `eval` | `model.rs:3,183,225,244` uses `eval::Evaluator` (`eval.rs:40-290`, plus `ClosureCache`, `compatible` `:291-299`) | `model -> evaluate` |
| kernel `wire` → surface `surface` | `wire.rs:295-297` reads `surface::formula_record(tag).wire_arity` (`surface.rs:8-103`) | `wire -> surface.registry` |

Unassigned modules: `units.rs` (921, uses `order`), `risk.rs` (1,002, root only), `readings.rs` (70),
`discourse.rs` (78, use `eval`/`search`). `order.rs` (1,435) embeds the order@0 parser and printer
(`:461-768`), a surface duty inside a profile file, exactly like Lean `VE.Order.Surface`; Python's
`ve.order` keeps its notation in the profile too, so this plan leaves `order.rs` whole (open question 8).

"Rust output" is the `ve` binary: subcommands `conformance`, `jsonl`, `countermodel`,
`check-countermodel`, `parse`, `format`, `evaluate`, `canonical-json` (`rust/ve/src/main.rs:366-503`),
JSON through `serde_json` without `preserve_order` (keys sorted), errors as `{"id","status":"error","error":{code,message,span?}}`,
and `ve evaluate` printing `Evaluation` field order. Nothing in `rust/` uses `module_path!`,
`type_name`, `env!("CARGO_PKG_*")` or derives `Serialize` on an enum, so crate and module names
cannot reach the output. The binary **bytes** will change (mangled crate names, panic-location
paths, cross-crate inlining), so every Rust step ends with a `checkers.lock` repin; bundle **D**
is the proof that the output did not.

| # | Change | Details | Proof | Effort |
|---|---|---|---|---|
| R0 | Tooling | `tools/rust_output_diff.py` (bundle D). Extend `tools/check_rust_deps.py` with an intra-crate module check: parse `use crate::X` and inline `crate::X::` paths per `src/*.rs`, map module → group (kernel: root, `ast`, `environment`, `model`, `wire`, `semantics`, `graph`; profile: `eval`, `route`, `search`, `order`, `units`, `risk`, `readings`, `discourse`; surface: `surface`), fail on outward edges against a new ledger `tools/rust-module-exceptions.json` seeded with today's three edges. Add tests to `tools/test_layer_policy.py`. | run on the unchanged tree: exactly three ledgered edges | S |
| R1 | Untangle inside `ve-core` | (a) `dependency_order` → new kernel `graph.rs`; `route.rs` re-exports so `ve_core::dependency_order` is unchanged. (b) `Evaluator`, `ClosureCache`, `compatible`, `EvaluationKernel` (`eval.rs:338-366`, feature-gated) → kernel `semantics.rs`; `eval.rs` keeps `evaluate*`, `Evaluation`, `TracedEvaluation` (field order untouched). (c) `wire.rs` gets a fixed `FORMULA_ARITY` table with the values of P2; `surface.rs` records keep `wire_arity` and a unit test asserts both tables agree. Ledger `rust-module-exceptions.json` becomes empty. | R, D, repin | M |
| R2 | Classify and document | Assign `units`, `risk`, `readings`, `discourse` to the profile group (Lean puts `VE.Risk.*`, `VE.Route.Readings`, `VE.Discourse.*` in layer 2; Python's `discourse`/`readings`/`risk` are layer-4 route modules, a cross-language mismatch recorded in `ARCHITECTURE-LAYERS.md`). Update the layer table rows for Rust. | S (docs/policy tests) | S |
| R3 | Three crates behind a facade | New members `rust/ve-kernel` (root items `Error`, `Span`, `Result`, `MAX_*`, `error()`, modules `ast`, `environment`, `model`, `wire`, `semantics`, `graph`), `rust/ve-profile` (`eval`, `route`, `search`, `order`, `units`, `risk`, `readings`, `discourse`), `rust/ve-surface` (`surface`); each `#![forbid(unsafe_code)]`, workspace-inherited edition/version, `serde_json.workspace = true` with no extra features. `rust/ve-core` becomes a **facade crate** whose `lib.rs` reproduces today's `pub use` list exactly from the three crates and forwards `bench-internals = ["ve-kernel/bench-internals"]`; `tests/*.rs` and `examples/bench.rs` stay in it (they use only `ve_core::`; `include_bytes!("../../../conformance/…")` paths are unchanged). Visibility: items that were `pub(crate)` across the cut (`error()`, `environment::{RESERVED, identifier, is_defined, model_sorts, require_checker, schema_name}`, `Environment` and `FiniteModel` field access, `ast::{ast_limit, Formula::predicates, Document::belongs_to}`, `model::{model_limits, predicate_sort, constant_sort}`, `semantics::Evaluator`) are exposed as `#[doc(hidden)] pub mod internal` in `ve-kernel` with **read-only accessor methods instead of public fields**, keeping "checked values have private fields; a claim is made only through `Document::check` or `parse`" (`lib.rs:2-3`). The facade does not re-export `internal`, so the external API is byte-identical. `rust/ve/Cargo.toml` unchanged. Regenerate `Cargo.lock` (every build is `--locked`). | R, D, repin; `cargo fmt`, clippy | L |
| R4 | Enforcement and path-coupled files | `check_rust_deps.py`: `CRATE_LAYERS = {"ve-kernel": 1, "ve-profile": 2, "ve-surface": 3, "ve-core": 3, "ve": 4}` (facade declared layer 3, allowed to depend on ≤ 3); add a manifest rule that no member enables `serde_json` features. `layer_policy.source_layer`: `rust/ve-kernel` → 1, `rust/ve-core` → 1 (facade plus whole-API tests, conservative), `rust/ve-profile` → 2, `rust/ve-surface` → 3, `rust/ve` → 4. `tests/test_rust_reproducible.py:100` copies all workspace members instead of `("ve","ve-core")`; `tests/test_risk_profile.py:82` → `rust/ve-profile/src/units.rs`; `rust/benchmark.py:162-164` hashes `rust/*/src/*.rs`; `docs/rust.md`, `ARCHITECTURE-LAYERS.md:12-14,25,94`. | R; `tools/test_layer_policy.py:359-378` extended for five crates | M |
| R5 (optional) | Drop the facade | Point `rust/ve` at the three crates directly and move `tests/`/`bench.rs` to the crate they exercise. Zero benefit for output; some churn; defer until something needs it. | R, D, repin | M |

Order: R0 → R1 → R2 → R3 → R4 (R3 and R4 may land as one commit if the checker must pass on every commit;
otherwise R4 first with the new crate names pre-registered). P2 and R1(c) should land in the same week so
the Python and Rust arity tables are reviewed together; `conformance/wire.json` is the cross-check.

## 4. Effort summary

| Part | Steps | Effort | Edges removed |
|---|---|---|---|
| Python | P1–P20 (+P21 decision, P22 prep) | 11 S, 4 M ≈ 12–14 days incl. full-suite runs | 24 (+1) |
| Lean | L0–L8 | 1 S tooling, 6 S, 2 M ≈ 7–9 days | 20 |
| Lean | L9 | L, after decision | 2 |
| Rust | R0–R4 | 2 S, 2 M, 1 L ≈ 8–10 days | 3 intra-crate, crate check live |

## 5. Open questions

1. **Slots as the sanctioned inversion** (P14–P19). The alternative, route-owned checks, changes
   diagnostic precedence and needs a spec revision plus Lean changes. Is a runtime binding pinned by
   `tests/test_slots.py` acceptable where a static import was not?
2. **Reclassification arguments** for `profiles` (→1), `alternatives` (→4), the tableau cluster and
   `CertificateWire` (→2), `Core.{Route,Bridge,Wire,Layers,Conservativity}` (→2), `Norms.Plain` (→4),
   `RoundTrip`, `Core.RoundTrip`, `Discourse.English` (→3). Each removes a ledger key without changing
   the import graph; reviewers should reject any whose duty argument they do not accept.
3. **L9**: Option A (parsers are kernel) versus Option B (move the legacy runners out, editing
   `MAIN_BASE` and manifest dispatch entries). Without a decision two Lean edges stay.
4. **P20** relocates a manifest-pinned entry. Allowed, or keep `english -> argument` as a permanent exception?
5. **P21** changes `python -m ve assist propose`. Accept, or keep this as the single permanent app exception?
6. **P10** cannot keep a facade and rewrites seven tests and one use-case script.
7. **Stage-2 adapters (25 keys)** stay until migration stage 5; whether `ve.backends` can sit at layer 1
   as a subpackage of a layer-4 package under import-linter is untested.
8. **Rust `order.rs`** keeps its parser/printer in the profile crate, matching Python but not Lean
   (`VE.Order.Surface` is layer 3). Splitting it needs `order_case` glue to move to the binary crate.
9. **Cross-language home for discourse/readings/risk** differs (Lean 2, Rust profile, Python 4). Align later or record.
10. **Counts**: the request said 24 Python and 20 Lean; the ledgers have 50 and 22. This plan uses the ledger.
11. **Risk block cycle check** (P15): a local Python reimplementation would avoid the slot but would let
    Python decide a check that is Lean's under `VE_AUTHORITY=lean`; the slot keeps the authority.
12. **P17** is alignment only; skip it if the kernel should stay minimal.
