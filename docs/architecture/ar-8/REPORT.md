# AR-8: the Rust boundary checked by cargo

Plan: `docs/ARCHITECTURE-REVIEW-2026-10.md` (branch `design/arch-review`), section 4.3, row AR-8.

## What changed

- `tools/check_rust_deps.py` reads `cargo metadata --format-version 1 --no-deps --offline` instead of tokenizing
  Rust. Rules: a crate depends only on workspace crates of a lower layer (`ve-kernel` 1, `ve-profile` 2,
  `ve-core` 3, `ve` 4), so `ve-kernel` uses no workspace crate, `ve-profile` only `ve-kernel`, `ve-core` both and
  `ve` all; every dependency kind and target counts, as cargo resolves it (workspace inheritance, renames,
  `package =`); a path dependency must reach a workspace member; every member has a layer; the `ve-core`
  facade has a library whose directory holds only `lib.rs`.
- Deleted: the module-group tokenizer and its rules, the `--crates-only` flag, `tools/rust-module-exceptions.json`
  and the tokenizer's fixture tables and tests in `tools/test_layer_policy.py`.
- The pre-commit hook's snapshot now holds the staged Rust workspace (manifests, sources, `rust-toolchain.toml`),
  so the hook runs the whole check when a Rust manifest or source is staged (`tools/hooks/README.md` updated).
- `tools/select_tests.py`: the deleted ledger is no longer a Rust-check input.
- `rust/ve-kernel/src/internal.rs`: a doc comment that cited the deleted module check, reworded on the same two
  lines; the release binary's hash is unchanged and pinned.
- Behaviour deltas of the tools: [DELTA.md](DELTA.md) (T1 and T5, and part of T2, need a DRI signature).

## Fixtures (plan row)

| Plan fixture | Test |
|---|---|
| `ve-kernel/Cargo.toml` gains a dependency on `ve-profile`: fail | `tools/test_layer_policy.py::LayerSelectionTests::test_outward_crate_dependencies_are_rejected` (also kernel → core, profile → core, core → `ve`) |
| A new module in `ve-core/src`: fail | `test_modules_in_the_facade_are_rejected` (`extra.rs`, `nested/inner.rs`, and a facade with no library); through the hook: `tests/test_precommit_hook.py::test_staged_rust_workspace_is_read_by_cargo` |
| The real workspace passes | `test_rust_crate_graph_kept`; a clean fixture workspace: `test_inward_fixture_workspace_passes` |
| Kept from the old crate check | renamed target build dependency and inherited renamed dev dependency (`test_renamed_and_inherited_rust_dependencies_are_read_as_cargo_resolves_them`); unmapped crate and outside path dependency; a manifest cargo cannot read (`test_unreadable_rust_workspace_fails`) |

## Measured outcome

Numbers rendered by `docs/architecture/ar-8/measure.py` from [evidence.json](evidence.json), which it measured
from fixed commits; `tests/test_ar8_evidence.py` re-renders this table from the saved evidence. The plan's
estimate was "500 of 648 lines" deleted from the checker.

<!-- measured: begin -->
| Measure | Base | Head |
|---|---:|---:|
| `tools/check_rust_deps.py` lines | 648 | 89 |
| `tools/rust-module-exceptions.json` lines | 1 | 0 |
| `tools/test_layer_policy.py` lines | 883 | 559 |

Diff `c24aeab2..8920ccd6` over 5 commits and 8 files: +177 −1048 lines (net -871).

| Seeded bug | File | Test run | Exit | Result |
|---|---|---|---:|---|
| M1 outward edges never reported | `tools/check_rust_deps.py` | `LayerSelectionTests::test_outward_crate_dependencies_are_rejected` | 1 | 4 failed, 1 passed in 0.73s |
| M2 dev and build dependencies skipped | `tools/check_rust_deps.py` | `LayerSelectionTests::test_renamed_and_inherited_rust_dependencies_are_read_as_cargo_resolves_them` | 1 | 2 failed, 1 passed in 0.46s |
| M3 facade modules ignored | `tools/check_rust_deps.py` | `LayerSelectionTests::test_modules_in_the_facade_are_rejected` | 1 | 2 failed, 1 passed in 0.57s |
| M4 outside path dependency accepted | `tools/check_rust_deps.py` | `LayerSelectionTests::test_unmapped_crates_and_outside_path_dependencies_are_rejected` | 1 | 1 failed in 0.41s |
| M5 hook snapshot without Rust sources | `tools/hooks/precommit.py` | `test_staged_rust_workspace_is_read_by_cargo` | 1 | 1 failed in 0.81s |
| M6 facade without a library accepted | `tools/check_rust_deps.py` | `LayerSelectionTests::test_modules_in_the_facade_are_rejected` | 1 | 1 failed, 2 subtests passed in 0.62s |
| M7 unmapped crates accepted | `tools/check_rust_deps.py` | `LayerSelectionTests::test_unmapped_crates_and_outside_path_dependencies_are_rejected` | 1 | 1 failed in 0.44s |
<!-- measured: end -->

The seeded bugs ran on the code at the evidence's head, each against the named test, and were removed
(the tree is clean). An earlier candidate, "a renamed dependency read by its alias", survived: it is
equivalent, because path dependencies are matched by path, so it was replaced by "dev and build dependencies
skipped".

## Coordination (plan 4.2)

Files checked at the start against `git diff --name-only main...<branch>` for every `lean-first/*`,
`readings-defaults/*`, `question-answering/*` and `infra/*` branch. Overlaps, so these files were NOT touched:

- `docs/ARCHITECTURE-LAYERS.md` (`readings-defaults/rd4b`): its Rust paragraph (lines 22–35) still describes
  the module check and links `tools/rust-module-exceptions.json`, which this batch deletes. Follow-up after rd4b
  merges, or in AR-7's sweep: replace that paragraph with "Rust's boundary is cargo's crate graph, checked by
  `tools/check_rust_deps.py` from `cargo metadata`".
- `tools/layer_policy.py` (`question-answering/integrate`, `readings-defaults/rd4b`): only lists the file name
  `check_rust_deps.py`; no change needed.
- `docs/TESTING.md` (`infra/eff-tests`): historical tables only; no change needed.

Shared inventory touched: `tools/gate-collection.json` (one test added to `tests/test_precommit_hook.py`, the
new `tests/test_ar8_evidence.py`). **Collision rule:** "conflict in `tools/gate-collection.json`: take `main`'s
file and run `uv run python tools/gate_collection.py --write`" (after AR-3 merges: "modify/delete conflict on
`gate-collection.json`: take the deletion").

## Gate

- Plan gate: `cargo test --workspace --locked` (run by the selected tests and the full gate's `cargo_test`
  stage) and `tools/test_layer_policy.py`.
- 4.1: the full suite through `tools/gate.py` on the final HEAD (result below); item 2 (corpus A/B) and item 3
  (Lean statements and trust) do not apply: no `ve/` or `lean/` file changes.
- Not run: no corpus comparison or latency measurement (no `ve/` or `lean/` change), no model calls.
