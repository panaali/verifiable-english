# Layer map and test policy

Imports and crate dependencies point inward: a module in layer *n* may depend
on layer *n* or any smaller number. For Python the rule applies to every import chain, at any depth in a
function (`import-linter`); for Lean and Rust to direct dependencies. Python's layers follow lean-first
(architecture plan T5, DRI decision D5): the transport to Lean is the innermost layer, so a container that
relays Lean's answer imports inward.
The stage-0 AST inventory (`mig/stage0:docs/spec/semantics-inventory.md` and
`mig/stage0:tools/semantic_inventory.py`) guided the assignments; a module with mixed duties is placed at its outermost
duty until it can be split. In particular, Python's `ve/__init__.py` is a
public facade whose names resolve lazily (`_EXPORTS` and `__getattr__`), so `import ve` loads no submodule; a
module below layer 4 may not import the facade, only the module that defines the name.

| Layer | Python `ve` modules | Lean modules | Rust |
|---|---|---|---|
| 1 kernel | Transport and wire: `assurance`, `backends.*`, `environment_wire`, `errors`, `limits`, `profiles`, `wire`, `wire_contract` | `VE.Syntax`, `Semantics`, `Typing`, `Finite`, `Consequence`, `Bridge`, `RoundTrip`, `CertificateWire`, `ClaimGraph`, `GraphChecks`, `ModelProofs`, `EnvironmentProofs`, `Tableau*`, `VE.Core.*`, `VE.Json` except `VE.Core.Surface` | `ve-core` crate root and `ast`, `environment`, `model`, `wire`, `semantics`, `graph` (one crate holds all three groups until the crate split) |
| 2 profiles | Containers built from Lean's answers and the encoders of their cases: `alternatives`, `ast`, `background`, `backends.lean_runner`, `backends.rust_jsonl`, `closure`, `definitions`, `entailment`, `environment`, `evaluate`, `identity`, `model`, `norms`, `norms_contract`, `order`, `rights`, `softnorms`, `speech_acts`, `units` | `VE.Closure.*` except `VE.Closure.Surface`, `Order.*`, `Norms.*` except `Norms.FlaggedSpec` and `Norms.RunSound`, `Definitions.*`, `Data.*`, `Route.*` except `Route.Run`, `Route.RunSound` and `Route.Checks`; other `VE.*` profile modules | Profile files inside `ve-core/src` (`eval`, `route`, `search`, `order`, `units`, `risk`, `discourse`); intra-crate module groups are checked by `tools/check_rust_deps.py` |
| 3 surface | Display and English rendering: `backends.english_lean`, `english*`, `fluent`, `fol`, `grammar`, `natural`, `norm_english`, `parser`, `printer`, `readings_english`, `readings_s2_english`, `report_english`, `senses`, `speech_english`, `surface.*`, `lexicon.*` | `VE.Surface*`, `LexicalProofs`, `ParserContracts`, `VE.English.*`, `VE.Order.Surface`, `VE.Core.Surface`, `VE.Closure.Surface` | none: Rust reads no source text since lean-first batch 15b (the `ve-surface` crate is deleted) |
| 4 tools | CLI, documents, assist, adapters and route modules: `__main__`, `adapters.*`, `admission`, `argument`, `ask`, `attacks`, `authoring`, `backends.senses`, `backends.speech_source`, `bundle`, `calc`, `check`, `defaults`, `defaults_english`, `document`, `equivalence`, `filling_search`, `norm_admission`, `norm_defaults`, `norm_defaults_contract`, `norm_defaults_english`, `norm_defaults_route`, `norm_strict`, `openterms`, `propose`, `readings`, `readings_route`, `readings_s1`, `readings_sup`, `readings_verdicts`, `readings_components`, `readings_s2_wording`, `senses_document`, `search`, `stream_audit`, `vacuity`, `words`, `assist.*`, `discourse`, `reports`, `reports_route`, `risk`, `rights_route`, `scope`, `soft_route`, `speech_document` | Entry points: every `lean_exe` root in `lean/lakefile.toml` (`Main`, `NormsMain`, `SoftNormsMain`, `RightsMain`, `SpeechActsMain`, `AlternativesMain`, `RiskMain`, `RiskEvalMain`, `QuantityMain`, `ReportsMain`, `DiscourseMain`, `Serve`, `ResponseDecode`, `EnglishRunMain`) and every top-level `*Main`; `VE.*.Run`, `VE.Service.*`, `VE.Norms.FlaggedSpec` (theorems on `Norms.Run.runCase`), `VE.Route.RunSound` and `VE.Norms.RunSound` (theorems on `Route.Run.runCase` and `Norms.Run.runCase`) | `ve` binary crate |
| 5 apps and measurements | Apps: `argument_fixtures`, `ve_experiments.*` | `VE`, `Iceberg`, `VE.Audit`, `VE.Checks`, `VE.Route.Checks` aggregation and audit targets | `rust/benchmark.py`, `rust/fuzz_closure.py`, reports |

The exact assignments, including exceptions to these patterns, live in
[`tools/layer_policy.py`](../tools/layer_policy.py). A Python package's row places every module in it, so a new
module in `ve/backends/`, `ve/document/` or `ve/assist/` needs no row; a longer row overrides it (the
`ve.backends` modules that encode containers, read English or are routes). A new top-level Python module and a
new Lean module must be classified there; `tools/check_python_layers.py` (which generates `.importlinter` and
runs `import-linter`) and `tools/test_layer_policy.py` fail on any unclassified module in `ve/` or `lean/`. A new route or service executable needs no entry:
its `lakefile.toml` root, or a top-level `*Main` module, is tool layer by rule. Rust's two crate boundaries are in
[`tools/check_rust_deps.py`](../tools/check_rust_deps.py). The desired future
split is separate Rust kernel, profile and surface crates. Until then the same
checker also assigns each `ve-core/src/*.rs` module a group (kernel: the crate
root, `ast`, `environment`, `model`, `wire`, `semantics`, `graph`; profile:
`eval`, `route`, `search`, `order`, `risk`;
surface: `surface`) and rejects
outward paths except the exact edges in
[`tools/rust-module-exceptions.json`](../tools/rust-module-exceptions.json). This
module check is a stopgap until the crate split, after which cargo enforces the
boundary, so it does not re-implement Rust's name resolution: it is fail-closed
on a strict subset. It tokenizes as rustc does (nested comments, raw strings,
decoded string escapes, Unicode identifiers after NFC) and accepts plain
`crate::<module>::...` paths (also through `super::` reaching the root), ordinary
`mod` declarations, and `lib.rs`'s top-level `use` items as the only re-exporting
facade, each naming a module directly, so `crate::<name>` resolves in one hop.
The crate root's own items count as kernel. Every form that could hide a
dependency is rejected with a message naming the plain form: aliases and globs
of the crate root, re-exports anywhere else, facade chains and module globs,
inline modules named like an imported name or a crate module, crate paths in
attribute or macro strings and in macro definitions, `#[path]`, `#[macro_use]`,
`#[macro_export]` (also under `cfg_attr`), `include!` (also renamed),
`extern crate self`, macros 2.0 and macro metavariables after `::`.
Rust's `risk` is a profile module (its `readings` replay was deleted in
lean-first batch 3, its `discourse` re-check in batch 4 and its `units` quantity route in batch 9), as in Lean
(`VE.Risk.*`, `VE.Route.Readings` and the `VE.Discourse.*` checks are
layer 2). Python files the same duties differently: `ve.units` is a container
module but `ve.risk`, `ve.readings` and `ve.discourse` are layer-4 route
modules. This cross-language mismatch is recorded, not resolved
([plan 2](ARCHITECTURE-LAYERS-PLAN2.md), open question 9).
The Lean service is a tool-layer Lean module; its Python client (`ve.backends.lean_service`) and the relay
are Python's layer 1.

## Tests and non-import dependencies

`tools/select_tests.py` selects tests by the functions, files and programs a
change touches, using a recorded coverage map with the static import graph as
the fallback; layers no longer decide selection. [`TESTING.md`](TESTING.md)
describes the rules, the map and the evidence. Before any green tag, and
nightly, run the full suite (`python3 tools/select_tests.py --full --run`, which never
stops early and applies no quarantine, or `python3 tools/gate.py`); a selected
run is not a green-tag gate.

Nightly, after the full suite, also run the deep differential fuzz:
`uv run python tools/difffuzz.py --deep 20 --report difffuzz-nightly.json`
([conformance/DIFFFUZZ.md](../conformance/DIFFFUZZ.md)). It takes 20 times the
CI sample from the date's seed. Exit 1 means one of three things: a new
disagreement, which it reports minimised; a baseline entry that no longer
reproduces; or an entry with no follow-up id. Triage each new disagreement:
fix it, or add it to `conformance/difffuzz-baseline.json` with a follow-up id
(`--update-baseline` writes it as `TODO`).

## Current exceptions

The exact imported edges and reasons are tracked in
[`tools/layer-exceptions.json`](../tools/layer-exceptions.json) (the count is in
[ARCHITECTURE.md](ARCHITECTURE.md) section 1; architecture batch AR-14 deleted the edges that T5's layers make
inward) and [`tools/lean-layer-exceptions.json`](../tools/lean-layer-exceptions.json)
(16 Lean edges). The checkers reject a new edge and reject a stale exception.
The Python edges are containers that still call search's walkers or the rights route, AST
traversal that uses surface registrations, the wire and the relay reading the AST's tables, and legacy Lean
`Core` and tableau proofs that import routed or closure proof machinery.
`VE.Norms.Wire -> VE.Route.Run` was removed by importing the needed gate and
wire directly, with `VE.Norms.Run` importing `VE.Route.Run` explicitly.
The three `ve-core` module edges were removed without changing the `ve` binary's
output: `dependency_order` moved to kernel `graph`, the evaluator core
(`Evaluator`, `Explanation`, `TraceBinding`, `compatible`) to kernel `semantics`,
and `wire` decodes with its own `FORMULA_ARITY` table, which the surface records
repeat (a unit test keeps the two equal).

| Language | Current outward edges (exact exceptions) |
|---|---|
| Python | `ve.assist.cli -> ve_experiments.assist_haiku`, `ve.ast -> ve.surface.nary`, `ve.backends.relay -> ve.ast`, `ve.closure -> ve.surface.registry`, `ve.english -> ve.argument`, `ve.norms -> ve.search`, `ve.rights -> ve.rights_route`, `ve.units -> ve.search`, `ve.wire -> ve.ast` |
| Lean | `VE.Bridge -> VE.Surface`, `VE.TableauExtendedRules -> VE.Closure.Congruence`, `VE.RoundTrip -> VE.LexicalProofs`, `VE.CertificateWire -> VE.Closure.Bridge`, `VE.TableauExtendedInduction -> VE.Closure.Induction`, `VE.TableauExtended -> VE.Closure.Substitution`, `VE.TableauExtendedExtra -> VE.Closure.PathRules`, `VE.Order.WireGate -> VE.Order.Surface`, `VE.Core.Bridge -> VE.Route.Gate`, `VE.Core.Conservativity -> VE.Closure.Consequence`, `VE.Core.RoundTrip -> VE.Core.Surface`, `VE.Closure.RoundTrip -> VE.Closure.Surface`, `VE.Core.Route -> VE.Route.Checker`, `VE.Core.Route -> VE.Route.Gate`, `VE.Core.Route -> VE.Route.Route`, `VE.Core.Wire -> VE.Route.Wire` |
| Rust | None at the crate boundary or inside `ve-core` |

Commands: `uv run --group dev python tools/check_python_layers.py`,
`python3 tools/check_lean_imports.py`, `python3 tools/check_rust_deps.py`.

## Selection evidence

The layer-based selection evidence that stood here was replaced with the
function-level selector's in [`TESTING.md`](TESTING.md#evidence).
