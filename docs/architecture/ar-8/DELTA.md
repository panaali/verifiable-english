# AR-8 deltas

AR-8 changes only tooling: no file under `ve/` or `lean/` changes, so the checker's answers, wire texts and
Lean statements are unchanged (plan 4.1 items 2 and 3 do not apply; `lake build` and `lean/audit.py` still pass
in the gate). The one Rust source edit rewords a doc comment on the same two lines: the release binary's
SHA-256 is unchanged and still pinned in `lean/checkers.lock` (`python3 tools/rust_build.py --check`).

The deltas below are in what `tools/check_rust_deps.py` and the pre-commit hook accept and print.

| # | Delta | Before | After | Signature |
|---|---|---|---|---|
| T1 | The intra-crate module-group check is deleted (plan 4.3 AR-8 "Change" and "Deleted") | Each `src/*.rs` module of `ve-kernel`, `ve-profile` and `ve-core` had to be listed in `MODULE_GROUPS`; outward module paths, `#[path]`, `include!`, macro-built paths and similar forms were rejected | A new module in `ve-kernel` or `ve-profile` needs no entry (its crate is its layer); cargo's crate graph is the boundary. Residual: a `#[path]` or `include!` that compiles another crate's file inside a crate is not seen by `cargo metadata`; a follow-up could read rustc's dep-info if wanted | **Needs DRI signature**: DRI-RULINGS lists deleting a check as always a DRI decision; the deletion is the plan row's own change |
| T2 | Path-dependency diagnostics follow cargo | `unmapped path dependency: A -> key`; `mismatched path dependency: A -> key` (the path's package differs from the declared name); `missing workspace dependency: A -> key` | `path dependency outside the workspace: A -> key` (same names quoted); a mismatched name is judged by the member the path reaches (cargo builds fail on it anyway); a missing workspace dependency fails as `cannot read the Rust workspace: cargo metadata failed: ...` with cargo's message naming the key | SIGNED by standing ruling R1 (DRI-RULINGS.md) for the first message: it keeps the crate and the manifest key, and names the fault more precisely ("outside the workspace"). Test: `test_unmapped_crates_and_outside_path_dependencies_are_rejected` checks the exact text with a renamed key. The other two messages are replaced by cargo's own text: **needs DRI signature** if R1 is read to require our wording |
| T3 | A module file in the `ve-core` facade | `unmapped Rust module: ve-core: extra` | `module in the ve-core facade: extra.rs; add it to ve-kernel or ve-profile and re-export it from ve-core` | SIGNED by standing ruling R1: quotes the crate and the module and adds the remedy. Test: `test_modules_in_the_facade_are_rejected` |
| T4 | A facade with no library target fails | Not checked (the old module map defaulted a missing `lib.rs`) | `the ve-core facade has no library target` | Stricter; no ruling needed beyond the plan row ("ve-core has no modules of its own beyond its re-exports"). Tests: the same test and `test_staged_rust_workspace_is_read_by_cargo` |
| T5 | The pre-commit hook's Rust check | Ran on staged `rust/**/Cargo.toml` only, read TOML with no cargo, skipped Rust sources (`--crates-only`) | Runs on staged `rust/**/Cargo.toml` and `rust/**/*.rs`; the snapshot holds the staged Rust manifests, sources and `rust-toolchain.toml`, and `cargo metadata --offline --no-deps` reads them; without cargo the hook fails closed (`cannot read the Rust workspace`) | **Needs DRI signature** (stricter hook, new dependency on cargo at commit time; no ruling covers hook scope). Test: `tests/test_precommit_hook.py::test_staged_rust_workspace_is_read_by_cargo` |
| T6 | `--crates-only` flag | Accepted | Removed (the whole check runs everywhere) | Follows T5 |

No delta widens what the Rust boundary accepts across crates: every outward crate edge the old crate check
rejected is still rejected (`test_outward_crate_dependencies_are_rejected`,
`test_renamed_and_inherited_rust_dependencies_are_read_as_cargo_resolves_them`).
