# eff-20261018-1: a content-keyed cache for the two Lean dump entries of tools/regen_generated.py

No DRI signature is needed. There are no DELTA rows: this is Python tooling only, with no user-visible change and no
Lean, Rust or product-code change (trust +0). The full gate is the chain's, on the final HEAD.

Sources: the task prompt (prompts/eff-20261018-1.txt). `reviews/efficiency-daily-20261018.md` and the PIPELINE-LIMITS.md
row L76 did not exist when this was built (the newest are efficiency-daily-20261017.md and L75). I worked from the
measurements that the prompt quotes.

## What was built

- `tools/cache_store.py` (new) is the one owner of the store that both caches use: the cache directory (`VE_RUN_CACHE`:
  `off`, a path, or by default the git common directory's `ve-run-cache`, with a subdirectory per named cache), entry
  names (`key_of`, `entry_path`), `load` (None on any unreadable or malformed entry), and `store`. `store` writes
  atomically (an `mkstemp` file in the same directory, then `replace`) and keeps the newest `keep` entries by mtime.
  `tools/run_cache.py` now calls it instead of keeping its own copy. Its format, key and behaviour are unchanged.
- `tools/lean_dump_cache.py` (new) provides `cached(step, root, sources, run, count, files, values)`. It looks up an
  entry before any Lean run. On a hit it returns the stored texts and prints `<step>: from cache <key8>` on stderr.
  On a miss it runs the dump as today and stores the result. The steps are `lean-statements` and
  `lean-audit-manifests`, the names of the regen entries they serve (the test
  `test_the_steps_are_the_regeneration_entries` checks this).
- `tools/lean_statements.py`: `dump_all(root, cache=False)`. The command line (`main`, used by both `--check` and the
  write) calls `dump_all(cache=True)`. The tests that dump fixture trees call `dump_all(tmp_path)` and never reach the
  cache.
- `lean/audit.py`: the Lean part (`lake build` of the manifests' imports, then the `#print axioms` parts) moved
  unchanged into `axiom_outputs(imports, texts)`. With `cache`, that one call goes through `cached`. Everything else
  runs live on the replayed text exactly as on a fresh one: the forbidden-word and admit scans, the declaration-list
  freshness check, the manifest writes and comparison, the parse of every output line, the allowed-axiom assertion,
  `seen == actual`, and the comparison with `axioms.txt` or its write. The stdout, the exit decision and the written
  files are therefore those of a fresh run (`test_the_audit_replays_lean_output_and_checks_it_as_fresh`). So the whole
  axiom audit could be keyed. The cached part is exactly the Lean output, and nothing Python decides is cached.
  `cached_mode(argv)` is true only for an explicit `--check` or `--write`, the regen entry's modes. The plain
  `python lean/audit.py`, which tools/gate.py's lean_audit stage runs (gate.py:765), never uses the cache
  (`test_only_the_explicit_audit_modes_are_cached`).

## The key (`lean_dump_cache.inputs`)

| input | how |
|---|---|
| every Lean source the dump reads | `lean:<path>` and its SHA-256, for each path in `lean_statements.sources()` (every `*.lean` under `lean/` outside `.lake`, so the generated `lean/VE/Audit.lean` and `lean/ResponseShape/Audit.lean` are included). An edit, an addition, a removal or a rename gives another key. |
| toolchain, lakefile, manifest | `file:lean/lean-toolchain`, `lean/lakefile.toml`, `lean/lakefile.lean` (keyed as absent today), `lean/lake-manifest.json` |
| installed toolchain | the digests of `bin/lean`, `bin/lake` and `lib/lean/*.so` / `*.dylib` in elan's directory for the toolchain that `lean-toolchain` names (found without running elan, so a lookup can never trigger a download) |
| `lake` program | the path `PATH` resolves it to, and the digest of its real file |
| environment | every `LEAN*`, `LAKE*` and `ELAN*` variable, with the checkout path written as `<root>` |
| platform | `platform.platform()`, the machine, and the Python version |
| code | `code:<path>` and its digest for `tools/lean_statements.py`, `lean/audit.py` and every repository module their imports reach. This is the BFS over `tools/source_graph.py`'s import edges (today 9 files: the two scripts, `lean_dump_cache.py`, `cache_store.py`, `source_graph.py`, `change_units.py`, `check_lean_imports.py`, `layer_policy.py`, `tests/subprocesses.py`). The embedded Lean scripts (`PRELUDE`, `TREE`, `SCRIPT`, `ALONE`) are in `lean_statements.py`, so its digest covers them. I left out the source graph's string-mention edges: they pulled in most of the repository (about 300 files, from `ve/` to `experiments/`), and the dump runs no named script. |
| caller's inputs | for the audit: `file:lean/declarations.txt` and `value:texts`, the SHA-256 of the exact part texts that Lean elaborates (their imports and `#print axioms` lines) |
| `FORMAT`, step | `ve-lean-dump-cache@1`, and `step` as an input |

Generated text files: the statement dump reads none of `statements.txt`, `predicates.txt`, `declarations.txt` or
`axioms.txt`. They are its outputs, or inputs of later steps, so they are not in its key. The audit reads
`declarations.txt`, so its key includes it.

On lookup, the entry must have the format, step and key, and its recorded `inputs` must equal the current inputs as a
whole dict. So a changed, missing or extra recorded input is a miss. Its `outputs` must also be a list of exactly
`count` strings. Anything else is a miss and the dump runs: an entry that is missing, unreadable, truncated, not gzip,
not JSON or a JSON non-object, or is a directory. A dump is stored only when it finished, returned `count` texts, and
its inputs, recomputed after the run, still equal those it was keyed on. A failed store does not fail the dump.

Doubts that are handled as misses or refusals:
- Lean code that runs while a file elaborates could read a file the key does not name. A tree with a source whose
  code (comments and strings blanked by `audit.code_only`) contains `#eval`, `#exit`, `include_str`, `run_cmd`,
  `run_elab`, `run_meta`, `initialize` or `builtin_initialize` is never cached. The same holds for a source that
  defines elaboration code (`elab`, `macro`, `syntax`, `MetaM`, ...) and also names `IO.`, `System.` or `FilePath.`.
  The run prints `not cached: <file> runs code while it elaborates`. The real tree has none
  (`test_the_real_tree_runs_no_code_while_it_elaborates`). This is a regex screen, not a proof. A residual is
  elaboration code in the tree that reads a file without spelling any of these words. None exists today: no source
  combines elaboration code with IO.
- If the inputs cannot be read (for example the checkout is not a git checkout, so the source graph cannot list it),
  the dump runs uncached.
- Not keyed: the toolchain's `.olean` library of Init, Lean, Std and Lake. It belongs to the installed release, whose
  programs and shared libraries are keyed. Also not keyed: environment variables other than `LEAN*`, `LAKE*` and
  `ELAN*` (and `PATH`'s choice of `lake`). The dump scripts read only their own `VE_*` variables, which they set
  themselves.

## Off switch, hermetic tests, and what can reach the cache

`VE_RUN_CACHE=off` disables it: no lookup, no input digest, no write (`test_off_never_reads_or_writes`). The nightlies
set it in the gate's environment (mac-gate-wrap.py `VE_GATE_RUN_CACHE_OFF`).

Suite tests do not reach the cache. They call `dump_all(tmp_path)` and `audit.main([...])` without `cache`, and no
test starts either command line as a subprocess (grep: the one subprocess run of `lean/audit.py`, in
`tests/test_lean_conformance.py:274`, is the plain run). The cache's own tests set `VE_RUN_CACHE` and `XDG_CACHE_HOME`
(the source graph's parse cache) under `tmp_path`, and give the scratch tree its own `ELAN_HOME` toolchain.

Pipeline paths that reach the cache: any `tools/regen_generated.py --check`, `--write` or `--resolve` that includes
`lean-statements` or `lean-audit-manifests`, and any direct `tools/lean_statements.py` or `lean/audit.py --check` /
`--write`. In practice:
- builders and fixers, and agent syncs, by hand;
- presync-watch-job.sh `rgen` (`--resolve`);
- merge-train.sh `regen_merge` (`--resolve`) and the candidate regen `cregen_run` (`--check` and `--write` of the
  named entries, under `CAND_REGEN_TIMEOUT` 300 s).

New cache use gained by R2 and R3: none, checked by grep on 2026-10-18.
- tools/gate.py runs only the plain `lean/audit.py` (line 765) and neither tool's cached modes.
- The R2 candidate gate is tools/gate.py.
- R3 runs only the plain `lean/audit.py`: verify.sh:6, mac-verify.sh, mac-gate-job.sh:178/208/224, mac-run-full.sh:15.
  Its only regen calls are `--write --only checker-pins` (mac-gate-job.sh:176/206, mac-gate-wrap.py:50,
  mac-pytest-job.sh:106, mac-run-full.sh:14), which is no Lean dump entry.
- The nightlies (nightly-verify.sh, nightly-vm-verify.sh) run these same gates with `VE_RUN_CACHE=off`.

## Measurements (evidence.json and the four logs)

These are `regen_generated.py` over every entry on the same commit a1b4ba9ed and the same machine (the VM): first a
fresh cache directory, then the same directory for the next three runs.

| run | seconds | lean-statements | lean-audit-manifests | 1-min load (start to end) |
|---|---|---|---|---|
| `--check`, cold | 270.5 | 139.3 | 84.1 | 11.7 to 18.8 |
| `--check`, warm | 47.3 | 1.9 (from cache) | 3.5 (from cache) | 18.7 to 20.4 |
| `--write` | 33.9 | 2.5 (from cache) | 4.2 (from cache) | 20.4 to 18.8 |
| `--check` after the write | 49.8 | 1.8 (from cache) | 3.9 (from cache) | 18.8 to 19.6 |

- The warm check saves 223 s of the cold 270.5 s. The stop rule needs 150 s, so it is met, and the result falls inside
  the expected 30 to 60 s for a warm check.
- The write left the tree unchanged (git status clean apart from the logs).
- An earlier run at load 23 to 28, on the code before the toolchain key: cold 413.1 s, warm 64.5 s.
- The single entries measured alone: lean_statements `--check` 190.4 s cold and 1.5 s warm; `lean/audit.py --check`
  85.9 s cold and 3.5 s warm, with byte-identical stdout.
- A warm lookup costs about 2 to 4 s per entry: the source scan, the source graph, and hashing 9 MB of Lean and the
  200 MB toolchain.

## Tests (tests/test_lean_dump_cache.py, 60 tests)

- **A hit is the cold dump byte for byte, on the real tree.** One cold and warm pair through `dump_all(cache=True)`
  (`test_a_replayed_dump_is_the_cold_dump_of_the_real_tree`, about 3 min). It is not marked heavy by hand, because
  heavy marks come only from the measured inventory (tests/heavy.json). It will enter that inventory at the next
  measurement.
- **Each keyed input kind, changed, is a miss, and the new dump is then stored and replayed**
  (`test_each_keyed_input_changed_is_a_miss[...]`, 21 cases): one Lean source edited, added, removed or renamed;
  `lean-toolchain`; the installed toolchain's library; its `lean`; the lakefile; an added `lakefile.lean`; the Lake
  manifest; `tools/lean_statements.py`; `lean/audit.py`; the cache's store; a module reached only through another's
  imports (`tools/layer_policy.py`); `FORMAT`; a `LEAN_*` setting; the `lake` program; the platform; the step; the
  caller's file; the caller's value.
- **Recorded inputs are re-verified on lookup.** An entry under the right key whose recorded inputs have one digest
  changed, one input removed or one added is a miss
  (`test_an_entry_whose_recorded_inputs_are_not_the_current_ones_is_a_miss`, 4 cases).
- **A corrupt or truncated entry is a miss and the dump runs**, and the miss stores a valid entry
  (`test_a_corrupt_entry_is_a_miss_and_the_dump_runs`, 15 cases).
- **Off:** `test_off_never_reads_or_writes` and `test_the_cache_directory`.
- **Concurrent stores:** two threads store one key, both entries are written whole before either rename, and one
  valid entry remains with no stray temporary file
  (`test_two_concurrent_stores_of_one_key_leave_one_valid_entry`). Pruning keeps the newest
  (`test_the_store_keeps_the_newest_entries`).
- **Worktrees share an entry:** `test_two_checkouts_of_one_tree_share_an_entry`.
- **Failed, changing and unkeyable runs are not stored:**
  `test_a_dump_that_fails_or_whose_inputs_change_while_it_runs_is_not_stored`,
  `test_a_tree_whose_inputs_cannot_be_read_runs_the_dump` and
  `test_a_tree_that_runs_code_while_it_elaborates_is_never_cached` (5 cases).
- **The callers:** `test_the_audit_replays_lean_output_and_checks_it_as_fresh` (the replayed output passes the same
  checks: a stale record still fails, and a changed declaration list is a miss), `test_the_command_lines_use_the_cache`
  and `test_only_the_explicit_audit_modes_are_cached`.

No literal sleeps and no elapsed-time asserts. The barrier and the thread joins use `HANG_TIMEOUT`.

## Seeded bugs (mutants.json: 15, each applied alone, its test failing, the file restored byte for byte)

The three the task asks for:
- **Drop the toolchain from the key** (both `lean-toolchain` in `LEAN_INPUTS` and `program:toolchain`): file
  tools/lean_dump_cache.py; failing test `test_each_keyed_input_changed_is_a_miss[the toolchain]`.
- **Drop an imported module from the code digest** (direct imports only, so `tools/layer_policy.py` drops out): file
  tools/lean_dump_cache.py; failing test `test_each_keyed_input_changed_is_a_miss[a module imported through another]`.
- **Skip the re-verification on lookup** (`entry.get("inputs") == current` removed): file tools/lean_dump_cache.py;
  failing test `test_an_entry_whose_recorded_inputs_are_not_the_current_ones_is_a_miss`.

The other twelve, as file and failing test:

| seeded bug | file | failing test |
|---|---|---|
| installed toolchain not keyed | tools/lean_dump_cache.py | `...[the installed toolchain's library]` |
| `VE_RUN_CACHE=off` ignored | tools/cache_store.py | `test_off_never_reads_or_writes` |
| temporary file named by pid (not unique) | tools/cache_store.py | the concurrent-stores test |
| pruning keeps every entry | tools/cache_store.py | the pruning test |
| output type unchecked | tools/lean_dump_cache.py | `test_a_corrupt_entry_is_a_miss_and_the_dump_runs[an output not text]` |
| a dump whose inputs changed while it ran is stored | tools/lean_dump_cache.py | the not-stored test |
| unreadable inputs crash | tools/lean_dump_cache.py | the inputs-cannot-be-read test |
| the elaboration screen off | tools/lean_dump_cache.py | the never-cached test |
| the plain audit replays | lean/audit.py | `test_only_the_explicit_audit_modes_are_cached` |
| the audit's declaration list dropped from its key | lean/audit.py | `test_the_audit_replays_lean_output_and_checks_it_as_fresh` |
| the statements command line skips the cache | tools/lean_statements.py | `test_the_command_lines_use_the_cache` |
| run_cache ignores the shared store's `load` | tools/run_cache.py | `tests/test_run_cache.py::test_changing_any_keyed_input_runs_again[recorded test file]` |

Python is the only language changed. Every changed Python product file of the tools layer has a seeded bug:
tools/cache_store.py, tools/lean_dump_cache.py, tools/lean_statements.py, tools/run_cache.py and lean/audit.py.

## Runs

- Selected tests (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`) on ed3e35ad2 passed: exit 0,
  87 of 436 units, 0 failed. It ran on the VM because the Mac runner was busy with a candidate gate.
- After the later commits (the toolchain key, the unreadable-inputs guard, two tests, and the regenerated
  `tests/history-dependent.json`), these passed: `tests/test_lean_dump_cache.py`, `tests/test_run_cache.py` and
  `tests/test_lean_audit_record.py` (111 passed), and the four `regen_generated.py` runs above (exit 0, every entry).
  The selected run is repeated on the final HEAD; see the build report.
- `tools/gate_collection.py --check --prebuilt`: 56 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- Pre-existing reds (main-known-red.txt, 3 tests: two in `tests/test_lean_service.py` and one in
  `tests/test_readings_defaults_rd8_report.py`): untouched by this branch.

## Commits (main..HEAD --no-merges, before this report's commit)

a1b4ba9ed, 4f8f5691b, dba2371ec, 3b52c51d6, ed3e35ad2, ea92f3305, 5f805cad7, 29c359c08.
