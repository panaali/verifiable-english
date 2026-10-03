# Layer map and test policy

Imports and crate dependencies point inward: a module in layer *n* may depend
on layer *n* or any smaller number. The rule applies to direct dependencies.
The stage-0 AST inventory (`mig/stage0:docs/spec/semantics-inventory.md` and
`mig/stage0:tools/semantic_inventory.py`) guided the assignments; a module with mixed duties is placed at its outermost
duty until it can be split. In particular, Python's `ve/__init__.py` is a
public reexport facade, not an architectural dependency source.

| Layer | Python `ve` modules | Lean modules | Rust |
|---|---|---|---|
| 1 kernel | `assurance`, `ast`, `environment`, `errors`, `identity`, `limits`, `model`, `wire`, `wire_contract` | `VE.Syntax`, `Semantics`, `Typing`, `Finite`, `Consequence`, `Bridge`, `RoundTrip`, `CertificateWire`, `ClaimGraph`, `GraphChecks`, `ModelProofs`, `EnvironmentProofs`, `Tableau*`, `VE.Core.*`, `VE.Json` except `VE.Core.Surface` | `ve-core` (one crate currently contains kernel, profile and surface code) |
| 2 profiles | `alternatives`, `background`, `closure`, `definitions`, `entailment`, `evaluate`, `norms`, `order`, `profiles`, `reports`, `rights`, `softnorms`, `softnorms_contract`, `speech_acts`, `units` | `VE.Closure.*` except `VE.Closure.Surface`, `Order.*`, `Norms.*`, `Definitions.*`, `Data.*`, `Route.*` except `Route.Run` and `Route.Checks`; other `VE.*` profile modules | Profile files inside `ve-core/src` (`order`, `route`, `eval`, `search`); intra-crate module groups are checked by `tools/check_rust_deps.py` |
| 3 surface | `english*`, `fluent`, `fol`, `grammar`, `natural`, `norm_english`, `parser`, `printer`, `readings_english`, `report_english`, `speech_english`, `surface.*`, `lexicon.*` | `VE.Surface*`, `LexicalProofs`, `ParserContracts`, `VE.English.*`, `VE.Order.Surface`, `VE.Core.Surface`, `VE.Closure.Surface` | `ve-core/src/surface.rs` (same crate limitation) |
| 4 tools | `__main__`, `adapters.*`, `admission`, `argument`, `attacks`, `authoring`, `backends.*`, `bundle`, `check`, `document`, `equivalence`, `norm_admission`, `norm_defaults`, `norm_defaults_english`, `norm_defaults_route`, `norm_strict`, `openterms`, `propose`, `readings`, `readings_route`, `readings_s1`, `search`, `stream_audit`, `vacuity`, `assist.*`, `discourse`, `quantity_admission`, `reports_route`, `risk`, `rights_route`, `soft_route`, `speech_document` | Entry points: every `lean_exe` root in `lean/lakefile.toml` (`Main`, `NormsMain`, `SoftNormsMain`, `RightsMain`, `SpeechActsMain`, `AlternativesMain`, `RiskMain`, `RiskEvalMain`, `QuantityMain`, `ReportsMain`, `DiscourseMain`, `Serve`, `ResponseDecode`, `VE.English.Run`) and every top-level `*Main`; `VE.*.Run`, `VE.Service.*` | `ve` binary crate |
| 5 apps and measurements | `argument_fixtures`, `ve_experiments.*` | `VE`, `Iceberg`, `VE.Audit`, `VE.Checks`, `VE.Route.Checks` aggregation and audit targets | `rust/benchmark.py`, `rust/fuzz_closure.py`, reports |

The exact assignments, including exceptions to these patterns, live in
[`tools/layer_policy.py`](../tools/layer_policy.py). New Python and Lean modules
must be classified there; `tools/test_layer_policy.py` fails on any unclassified
module in `ve/` or `lean/`. A new route or service executable needs no entry:
its `lakefile.toml` root, or a top-level `*Main` module, is tool layer by rule. Rust's two crate boundaries are in
[`tools/check_rust_deps.py`](../tools/check_rust_deps.py). The desired future
split is separate Rust kernel, profile and surface crates. Until then the same
checker also assigns each `ve-core/src/*.rs` module a group (kernel: the crate
root, `ast`, `environment`, `model`, `wire`; profile: `eval`, `route`, `search`,
`order`, `units`, `risk`, `readings`, `discourse`; surface: `surface`) and rejects
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
The stage-1 Lean service and its Python adapter are tool-layer modules. This
classification checks their imports and selects their consumers; the service is
still outside the `ve` command path, as described in
[`INTEGRATION-GAPS.md`](INTEGRATION-GAPS.md).

## Tests and non-import dependencies

`tools/select_tests.py` reads the changed paths from a working-tree diff,
branch diff, historical commit or explicit path list. Its test assignment uses
AST imports, resolves `from ve import ...` through the public facade, and uses
the highest imported layer when a test spans layers. Test helpers and fixtures
imported from other test files contribute their providers transitively; changing
a helper also selects its consumers. Reviewed outward imports lower the changed
module's effective layer to include inner consumers, following exception edges
transitively. It runs tests assigned to that layer and every outer layer.
Unknown paths and shared fixtures select the full suite. A changed test file is
always selected.

| Source or input | Assigned layer / test effect |
|---|---|
| `ve/*.py`, `lean/**/*.lean`, `rust/{ve-core,ve}/**` | Module or crate layer above; Lean changes build `lake`, Rust changes run `cargo test` and build the release binary |
| `tests/test_*.py` | Test's import-derived layer; select the changed test itself |
| `tests/conftest.py`, `tests/data/**`, `conformance/**` | Layer 1, since fixtures and generated reports feed tests across layers; conformance changes rebuild both native backends |
| `lean/{lakefile.toml,lean-toolchain,lake-manifest.json}`, `rust/{Cargo.toml,Cargo.lock}`, `pyproject.toml`, `uv.lock` | Layer 1 |
| `ve_experiments/**`, `experiments/**`, `usecases/**`, `paper/**`, documentation | Layer 5, except generated `docs/english-surface.md` and `docs/fluent-examples.md` are layer 1 because tests compare their contents |
| Unknown paths | Layer 1 full-suite fallback |

Tests that call a `lean/.lake/build/bin` executable (any `lean_exe` named in
`lean/lakefile.toml`) or `rust/target/release/ve` are treated
as tool-level consumers even without a Python import. Tests that read
`usecases` data are app-level consumers. Four cross-cutting Python files always run:
`test_conformance.py`, `test_lean_conformance.py`,
`test_replay_conservativity.py`, and `test_p0_three_way.py`. The Python, Lean,
Rust import/dependency checks, selector boundary checks, and Lean axiom audit
always run. A missing native binary is built before its selected consumer runs;
a `lean_exe` outside `defaultTargets` (such as `ve_risk_eval`) is named in its own
`lake build` when a selected test uses it.
The randomized recovery replay and wall-clock deadline tests are layer-5
measurements even though their imported implementation is in layer 4.

Use `python3 tools/select_tests.py --base <merge-base> --run` for a branch
check, or omit `--base` for the current working tree. `--json` emits the exact
paths and commands for CI. The runner executes commands sequentially; `pytest`
excludes the live model tests through `pyproject.toml`'s default marker filter.
`UV_CACHE_DIR=/tmp/ve-layers-uv-cache` is the default runner cache location.

Selective runs are for fix loops and branch checks. **Before any green tag,
and nightly, run the full suite** with
`python3 tools/select_tests.py --full --run`, including Lean build, Rust tests,
release binary, Python tests, dependency checks and axiom audit. Do not treat a
selected run as a green-tag gate.

## Current exceptions

The exact imported edges and reasons are tracked in
[`tools/layer-exceptions.json`](../tools/layer-exceptions.json) (12 Python
edges plus the assist CLI app edge) and [`tools/lean-layer-exceptions.json`](../tools/lean-layer-exceptions.json)
(16 Lean edges). The checkers reject a new edge and reject a stale exception.
The largest clusters are kernel constructors that still invoke profile checks,
kernel AST/wire traversal that uses surface registrations, and legacy Lean
`Core` and tableau proofs that import routed or closure proof machinery.
`VE.Norms.Wire -> VE.Route.Run` was removed by importing the needed gate and
wire directly, with `VE.Norms.Run` importing `VE.Route.Run` explicitly.

| Language | Current outward edges (exact exceptions) |
|---|---|
| Python | `ve.ast -> ve.surface.nary`, `ve.assist.cli -> ve_experiments.assist_haiku`, `ve.closure -> ve.surface.registry`, `ve.english -> ve.argument`, `ve.environment -> ve.definitions`, `ve.environment -> ve.profiles`, `ve.model -> ve.background`, `ve.model -> ve.definitions`, `ve.model -> ve.evaluate`, `ve.norms -> ve.search` |
| Lean | `VE.Bridge -> VE.Surface`, `VE.TableauExtendedRules -> VE.Closure.Congruence`, `VE.RoundTrip -> VE.LexicalProofs`, `VE.CertificateWire -> VE.Closure.Bridge`, `VE.TableauExtendedInduction -> VE.Closure.Induction`, `VE.TableauExtended -> VE.Closure.Substitution`, `VE.TableauExtendedExtra -> VE.Closure.PathRules`, `VE.Order.WireGate -> VE.Order.Surface`, `VE.Core.Bridge -> VE.Route.Gate`, `VE.Core.Conservativity -> VE.Closure.Consequence`, `VE.Core.RoundTrip -> VE.Core.Surface`, `VE.Closure.RoundTrip -> VE.Closure.Surface`, `VE.Core.Route -> VE.Route.Checker`, `VE.Core.Route -> VE.Route.Gate`, `VE.Core.Route -> VE.Route.Route`, `VE.Core.Wire -> VE.Route.Wire` |
| Rust | None at the crate boundary; inside `ve-core`: `environment -> route`, `model -> eval`, `wire -> surface` |

Commands: `uv run --group dev python tools/check_python_layers.py`,
`python3 tools/check_lean_imports.py`, `python3 tools/check_rust_deps.py`.

## Selection evidence

The following replays the 10 newest non-merge commits immediately before this
branch's layer commits. Counts are Python test files in the present tree; the full
suite had 96 files at the time of measurement; the merged tree has 101. Historical paths were classified under that policy snapshot.

| Commit | Minimum layer | Selected / full |
|---|---:|---:|
| `c395da7` | 5 | 53 / 96 |
| `b107b7d` | 5 | 53 / 96 |
| `f4286ef` | 5 | 53 / 96 |
| `fe7fd33` | 5 | 53 / 96 |
| `39350c0` | 5 | 53 / 96 |
| `4af44bd` | 5 | 53 / 96 |
| `2be5772` | 5 | 53 / 96 |
| `03d0fd3` | 5 | 53 / 96 |
| `628659a` | 5 | 53 / 96 |
| `4704fd8` | 4 | 80 / 96 |

Reproduce a row with `python3 tools/select_tests.py --commit <sha> --json`.
For representative changed paths at each layer, the selector chooses 96, 96,
92, 80, and 53 of 96 files respectively from kernel through apps.

One reversible functional fault was injected in a source module at each layer:
canonical JSON serialization, profile family dispatch, grammar export,
gatekeeper exemption, and the T1c breadth-first search. An additional registry
fault covers a reviewed outward edge to the kernel. For each fault,
`tools/mutation_check.py` ran a selected witness that failed and ran every
*excluded* test file under the fault. Thus no excluded test failed because of
these mutations; all full-suite failures attributable to each injected fault
are inside that layer's selection. The app exclusion was split into four
11-file invocations after two wall-clock-sensitive assist stress tests were
assigned to layer 5.

| Fault layer | Selected / full files | Witness failures | Excluded files passing |
|---|---:|---:|---:|
| 1 kernel | 96 / 96 | 1 | 0 / 0 |
| 2 profiles | 96 / 96 | 1 | 0 / 0 |
| 3 surface | 92 / 96 | 3 | 4 / 4 |
| 4 tools | 80 / 96 | 1 | 16 / 16 |
| 5 apps | 53 / 96 | 1 | 43 / 43 |

Exact witness IDs, commands' test-file groups, exit codes and timings are in
[`layer-mutation-results.json`](layer-mutation-results.json). The full Python suite
passed with **2,161 passed, 5 skipped** in 21m31s using four pytest workers;
the five skips are optional backends, an absent pinned FOLIO corpus, a Rust
admission case outside Rust scope, and an uncached tokenizer. `lake build`,
`cargo test --locked --all-features`, the Rust release build, the Lean axiom
audit, and all three dependency checks also passed.
