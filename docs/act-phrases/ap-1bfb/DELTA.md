# ap-1bfb delta: the `acts@0` wire contract's rule phases, frames and adverbs, and ap-1bf's review findings F1, F2

Base: `git merge-base HEAD main` (`8eda0371fd`). The contract stays `shadow`: it reports and refuses nothing, and no
route reads it. Its revision goes from 1 to 2 (WC10: the content changed).

**Everything else: no change.** No product path asks for the `acts@0` `diagnose` unit: `ve/backends/soft_relay.py:47`,
the only caller of `diagnose` in `ve/`, names `soft-norms@0` (`grep -rn '"diagnose"' ve/`). The recorded route cases
are unchanged: `git diff --stat 8eda0371fd -- lean/VE/Route/examples tests/data` is empty after
`uv run python tools/regen_generated.py --write` (40 entries). `lean/VE/WireContract/Hooks/Norms.lean`,
`ve/wire_contract/norms@0.json`, `lean/statements.txt` and the spec files are unchanged (`git diff --stat 8eda0371fd --`
those paths is empty).

## User-visible deltas

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | A1: `acts@0`'s record of an `acts@0` source without `norms@0` (check 1.1d, path `/environment`) now has the text `UnsupportedProfile: acts@0 requires norms@0`, the profile row's, which Python's engine relays from Lean's environment mode; before, Lean's was `UnsupportedProfile: norms@0 is required` and Python's the new one (ap-1bf review F1). The text keeps the quoted profile `norms@0`, names the profile that requires it, and the check and path are unchanged. | Saved before/after record: [delta.json](delta.json) (base revision 1, head revision 2); `tests/test_acts_contract.py::test_the_saved_wording_delta_keeps_the_base_path_and_quoted_names` checks that the head keeps the base's path, check and quoted profiles and is Lean's record today; `::test_a_source_without_norms_gives_one_record_in_both_engines` (failing first: [a1-before.txt](a1-before.txt)). | SIGNED by standing ruling R1 (DRI-RULINGS.md) |
| 2 | Trust growth, measured on the final tree with `uv run python tools/trust_map.py --check` against `8eda0371fd`: K +0, S +0, untied V +36, recorded as one allowance in `docs/trust-baseline.json`. Per file: `lean/VE/WireContract/Hooks/Acts.lean` +36 (G[V] `typingEnvironment`, `ruleTyping`, `blockOf`, and the changed `decoded`, `member`, `classifier`, `hooks`, `registered`). New Lean-owned behaviour: the rule phases' typing environment and the frames members. | [trust-mutants.json](trust-mutants.json): 457 KILLED, 0 SURVIVOR, 0 UNKNOWN, 15 ALLOWED (each with its reason in [trust-allow.json](trust-allow.json)), 4 INVALID; [mutants.json](mutants.json) (17 killed); FOLLOW-UPS.md row "## ap-1bfb" asks for the ties pass. | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 3 | Generated files rewritten only by `uv run python tools/regen_generated.py --write`: `lean/VE/WireContract/Tables/Acts.lean`, `ve/wire_contract/contracts.lock`, `rust/ve-kernel/src/contract_tables.rs`, `docs/spec/acts-wire-table.md`, `conformance/wire-contract/acts@0-catalogue.json`, `lean/checkers.lock`, `lean/declarations.txt`, the codemaps and `tests/history-dependent.json`. | `uv run python tools/regen_generated.py --check`; `tests/test_acts_contract.py::test_the_limit_example_is_the_source_at_the_limits_and_the_catalogue_is_current`; `tests/test_wire_contract_rust.py::test_rust_table_rows_equal_the_contract_rows`. | SIGNED by standing ruling R12 (DRI-RULINGS.md) |

## Evidence that is not a row (shadow diagnostics: no verdict, no acceptance change)

- **The rule phases (B).** `acts@0.json` includes `norms@0`'s phases `profiles`, `rule-shape`, `rules`, `references`
  and `semantic` as `norms`; a refused rule of an `acts@0` source now names its `norms@0` member (for example
  `norms/4.7b`) where it gave the residual `ACTS_INVALID_INPUT`. Faults: 10 in the catalogue (`rules-limit` to
  `precedence-cycle`), both engines, record by record (`tests/test_acts_contract.py::test_every_fault_gives_its_member_in_python_with_leans_text`,
  `::test_every_fault_gives_its_record_in_lean_and_the_sources_at_each_limit_are_clean`).
- **The frames and adverbs (C).** A refusal of D-31 is 1.1e at 31a's limit (`ACTS_RESOURCE_LIMIT`) and 1.1f otherwise
  (the new code `ACTS_INVALID_FRAMES`, class InvalidInput), where it gave 1.1d (`ACTS_INVALID_ENVIRONMENT`, same class).
  Faults: 22 (at and around the limit, one per condition 31b to 31s, two that do not decode).
- **The engine sweep (A1).** 45 cases, [sweep-before-a1.json](sweep-before-a1.json) 4 differ,
  [sweep-after.json](sweep-after.json) 2 differ: the two that `norms@0` shares (a `defined` declaration without
  `definitions@0`, a bad `language`), listed in REPORT.md and not changed here.
