# wc-s4-2: the Rust contract tables (wire-contract S4 item 2, first part)

No DRI signature is reserved in this item. DELTA: none. Trust: +0.

## Plan rows delivered

| Plan or task line | Delivered by | Test or evidence |
|---|---|---|
| Statement gate: "a statement spec for the Rust engine … the generated module's grammar and the `error` object" (S4 plan :112, question 8 :189) | `docs/spec/wire-contract-s4-2.md` (8a1abee8b), accepted with one change by `reviews/dri-decisions-20261031-wc-s4-2.md`; the change was applied in d9773640a | the decision file |
| (2) Rust table types, data only, one per type of `Table.lean` | `rust/ve-kernel/src/contract.rs` (55994c3b8) | the generated tables compile: `cargo test -p ve-kernel --test contract_tables` passes 3 tests |
| (3) Rust emitter beside the Lean one, called next to `generated_lean`, for the three units and the corpus | `tools/wire_contract_rust.py`, `tools/wire_contract.py` `generated_rust` (55994c3b8, c0dda8841) | `python -m tools.wire_contract --check`, and the same with `--directory conformance/wire-contract/contracts`: both exit 0 with no output |
| Both paths in the "wire-contract" row, written by regen | `tools/regen_generated.py` (and `keys_table/mod.rs`); written by `regen_generated.py --write` (4bd09d8d6, 34 entries written) | `/tmp/wc-s4-2-regen2.log`: "regen_generated: wrote 34 entries" |
| Keys in code point order | `ordered()` in the emitter; the set-like key lists and `args` names | `test_rust_table_rows_equal_the_contract_rows` (its last assertion), seeded bug S2 |
| (4) cargo test: embedded hash equals its lock entry | `embedded_hashes_equal_their_lock_entries`, `the_keys_table_hash_equals_its_file` | seeded bug S3 |
| (4) cargo dump of rows and a pytest that compares it with the contract JSON, for all three units, the corpus contracts and a key outside the BMP | `dump_rows`, `tests/test_wire_contract_rust.py`, `tools/wire_contract.py` `table_rows` | seeded bugs S1, S2, S4 |
| (4) `--check` covers the Rust files | `test_l11_swapped_rust_rows` (passes on a clean copy, then reports WC11 for the shipped and the corpus module) | `pytest tests/test_wire_contract_lint.py -k l11`: 2 passed |
| (4) a fault in `tools/mutation_check.py` (two rows swapped in `contract_tables.rs`) | `_swap_rust` (d9773640a). It was first moved to wc-s4-2b at the size line (c0dda8841); the DRI decision's condition "F1-F4 as in section 9" put it back | `uv run python tools/mutation_check.py --wire-only`: "wire generated Lean and Rust row swaps detected by --check" |
| Re-generate `lean/checkers.lock` if the Rust build hash moves | it moved: `b56b8d2c…` was pinned by `regen_generated.py --write --only checker-pins` (4bd09d8d6) | `python3 tools/rust_build.py` printed "NOT pinned" before the pin |

Not delivered here (wc-s4-2b, as the task names it): the engine run, the engine corpus in Rust, the `error` object's
`diagnostic` member and its jsonl schema entry, and the large well-formed input under the DRI's rule of 2026-10-27.

## Deviations from the plan, recorded here and not in the plan

1. **Crate.** The plan says `rust/ve-core/src/`. Since layers2 R3 (`7b37ef31d`) `ve-core` is a facade, and
   `tools/check_rust_deps.py:90` refuses a module there. So the files are `rust/ve-kernel/src/contract.rs` and
   `contract_tables.rs`, both `pub mod` in the kernel, with no facade re-export (the tests are the kernel's).
   `python tools/check_rust_deps.py` prints "Rust crate graph kept". `lib.rs` gains two `mod` lines, not one,
   because the types and the generated tables are separate files.
2. **Python engine.** The plan names `ve/wire_contract/engine.py`. Since `9fa67ead6` it is the test oracle
   `conformance/wire_contract_engine.py`, and Lean's engine runs in production. The Rust tables split their
   templates with the oracle's `pieces`, as the Lean emitter already does.
3. **`keys@0`** (DRI decision, item 1): generator-test data at `rust/ve-kernel/tests/data/keys@0.json`, with its table in
   `rust/ve-kernel/tests/keys_table/mod.rs` and a recomputed hash check. `git diff main -- conformance/wire-contract/contracts/`
   is empty.
4. **One parser for both emitters.** `parse_pattern` and `parse_ranges` live in `tools/wire_contract_lean.py`, and both
   emitters call them, so that no second copy is kept. The generated Lean is unchanged (`--check` exit 0).
5. **Hook snapshot.** `tools/hooks/precommit.py` copies `tools/wire_contract_rust.py` and `contract_tables.rs` into its
   staged snapshot, and two tests that list the files a revision write changes now include the Rust table
   (`test_l13_…`, `test_t3_…`). Without this the selected run failed (see Tests).

## Size

`git diff --numstat $(git merge-base HEAD main)` with the generated files left out (tables, locks, codemap,
`.gitattributes`, `checkers.lock`) gives +867 −44, plus this report. That is over the ~600 line. The task's own
cut (the mutation-check fault, 58 changed lines) is the one the DRI's condition kept. Every other part is one of
the deliverables (1) to (4) or a consequence of them: the spec (141), types (164), emitter (175 + 75 + 23), cargo
test (161), pytest (51). No further coherent cut was left.

## Seeded bugs (each shown failing, then restored with `git checkout`)

The same rows, with file and test keys: `seeded-bugs.json` beside this report. S1 and S4 were shown failing again on 7eb0684b.

| # | Language, file | Bug | Failing check |
|---|---|---|---|
| S1 | Rust, `rust/ve-kernel/src/contract_tables.rs` | soft-norms rows 1.1 and 1.2 swapped (line 86) | `tools.wire_contract --check`: "contract_tables.rs: WC11: generated module differs", exit 1; `tests/test_wire_contract_rust.py::test_rust_table_rows_equal_the_contract_rows` failed on `id` |
| S2 | Python, `tools/wire_contract_rust.py` `ordered` | keys sorted by UTF-16 code units, corpus regenerated | `test_rust_table_rows_equal_the_contract_rows`: `{'keys': [['😀', 'ｚ'], …]} != {'keys': [['ｚ', '😀'], …]}` |
| S3 | data, `ve/wire_contract/norms@0.json` and its lock | revision 1→2 and the lock updated, tables not regenerated | `cargo test --test contract_tables embedded`: `embedded_hashes_equal_their_lock_entries` panicked, "norms@0.json in …contracts.lock" |
| S4 | Python, `tools/wire_contract_rust.py` `pieces` | every renderer written `Raw`, corpus regenerated | `test_rust_table_rows_equal_the_contract_rows`: `['arg', 'value', 'raw'] != ['arg', 'value', 'json']`. With only the shipped units regenerated, the tables did not change, because no shipped template uses a non-raw renderer (`grep -c ':json}'` is 0 for all three) |

## Trust

`uv run python tools/trust_map.py --check` on 4bd09d8d6: "against 327bf922a119: K +0, S +0, D +0, G +0, tied +0,
unclassified +0, trusted +0 … PASS". Rust and tools are untrusted, and no Lean file changed, so there is no new
trusted definition and no mutants.json.

## Tests

- Selected set, once: `mac-pytest.sh --select` (441 of 505 units; a Rust kernel change and the release pin reach
  every Rust user) gave shard 1: 143 of 146, shard 2: 147 of 148, shard 3: 147 of 147. The 5 failed ids were
  `test_precommit_hook.py::test_large_staged_change_passes` and `::test_wire_contract_accepts_staged_equivalent_json`
  (the snapshot lacked the Rust emitter and table), `test_wire_contract_lint.py::test_l13_…`,
  `test_wire_contract_s4_lean.py::test_t3_…` and `test_wire_gate_corpus.py::test_gate_corpus_holds_every_test_input_of_every_unit`
  (the nested run of the two before). Fixed in d4efb9cea. The rerun of these 5 ids gave "5 passed", HEAD d4efb9ce clean.
- No test of `main-known-red.txt` was reached.

## Pilot bytes

None expected: no output, verdict, message or schema changes (estimate; nothing is claimed before a pilot audit).

## Observation

`regen_generated.py --write` runs `route-cases`, which calls the Rust release binary, before `checker-pins`.
So when the Rust hash moves, the first `--write` stops with "Rust executable hash mismatch", and it needs
`--write --only checker-pins` first. Not changed here.

## Spec re-read

- The Rust `error` gains `diagnostic` "in item 2 and not before", checked against wire-contract-S4-PLAN.md:99. Spec 6 puts it in wc-s4-2b, the second part of item 2.
- Rust "defers on every soft-norms hook and is counted, not compared", checked against wire-contract-S4-PLAN.md:101 and spec 7.
- "generated static data, committed (no `build.rs` …); a cargo test compares the embedded hashes with the lock", checked against wire-contract-PLAN.md:255 and spec 4.
- "`tools/mutation_check.py` gains one injected fault (two rows swapped in a generated table)", checked against wire-contract-PLAN.md:416 (F4).
- Code point order of keys, not UTF-16, checked against wire-contract.md:84-86 and spec 4.

## Next item

wc-s4-2b: the Rust engine run (order 2.6, record 2.7, outcomes 2.8 with `deferred`), the engine corpus run in Rust
byte-identical to `engine-golden.json`, the `error` object's `diagnostic` member with its jsonl schema entry, and
the large well-formed input under its stated limit.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed or changed.
2. PASS: the plan rows table above, with a commit and a test for each; the files of in-flight branches were checked (`feature/gi-2a`, `foundation/me-1`, `infra/arch-AR-1` touch `tools/regen_generated.py`, but not the wire-contract row).
3. PASS: seeded bugs S1 to S4. The comparator fails on an empty dump (the contract-set assertion) and on a missing row (the length assertion) in `test_rust_table_rows_equal_the_contract_rows`.
4. PASS: the Rust rows equal Python's reading for every table (`test_rust_table_rows_equal_the_contract_rows`); the generated Lean is unchanged (`--check`).
5. N.A.: no relayed field is read.
6. PASS: the selected tests ran on the committed tree, and the failed ids were rerun on d4efb9ce. The gate is run by the chain.
7. PASS: no DELTA row, and no trust growth (`trust_map.py --check` PASS).
8. PASS: DELTA none. No output, error or schema changes (Rust `Error` untouched; `jsonl.json` untouched).
9. PASS: `select_tests.py --base …` selects `tests/test_wire_contract_rust.py`, and S1's failing test is in it.
10. N.A.: no Lean statement.
11. N.A.: no budget, limit or deadline; the engine (an evaluator) is wc-s4-2b.
12. N.A.: data-only statics; no runtime path reads them.
13. PASS: no test removed or renamed.
14. PASS: both directions: `test_l11_swapped_rust_rows` (clean copy passes, a swap fails), the hash test (passes as committed, fails at S3); the spec re-read is above.
