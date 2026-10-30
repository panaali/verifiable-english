# gi-2a build report

Status: implemented; the chain runs the final full gate on the committed HEAD. No DRI signature is reserved.
HEAD: `feature/gi-2a` tip at handoff.
Changed: `writer="train"` in the registry, the overlay `lean/.lake/ve-inventory/`, and `inventory_path`. Every
reader of a train-only file now goes through `inventory_path`, and a guard test enforces it. Writers still write
the committed paths. DELTA: none. Trust: +0. Pilot bytes expected: 0.
Next: gi-2b. Size: 1201 added lines outside generated files, 697 of them the test file (cap ~600; see Size).

## Delivery (DESIGN.md 4 steps 1-2 and 4, 7 step 2, 8 row gi-2a, 9; DRI decision 1(b))

| Plan row | Owner | Commit and evidence |
|---|---|---|
| (1) `writer="train"` on `lean-statements`, `lean-audit-manifests`, `checker-pins`, `assurance-doc`; one helper | AGENT | d716a982; `regen_generated.train_only()`; `test_the_registry_names_exactly_the_train_only_files` |
| (2) Overlay `lean/.lake/ve-inventory/` (git-ignored) | AGENT | `lean/.gitignore` already ignores `.lake/`; `test_the_overlay_is_git_ignored_and_the_committed_copies_are_not` |
| (2) `inventory_path`: fresh overlay gives the overlay copy; unchanged modules give the committed copy; a changed module with no or a stale overlay is a stale error naming it | AGENT | `tools/lean_statements.py`; `test_a_fresh_overlay_is_read_and_a_stale_one_is_an_error`, `test_unchanged_modules_read_the_committed_copy`, `test_a_changed_module_with_no_overlay_is_a_stale_error_naming_it` (edited, added, removed module, unreadable list), `test_an_incomplete_or_altered_overlay_is_not_fresh` |
| (3) Readers moved (table below) | AGENT | d716a982, f401a186 |
| (4) Writers write the committed path by default; the overlay is opt-in | AGENT | `inventory_target`, `write_inventory`; `test_writers_write_the_committed_path_unless_the_overlay_is_asked_for` (unset, empty, `committed`, `overlay`, refused `Overlay` and `1`) |
| Condition (a): guard against literal reads, with an allow-list | AGENT | `test_no_train_only_path_is_read_outside_the_accessor` scans every tracked Python file but `docs/` and folds each expression to the paths it can spell (review F1, below). The allow-list is keyed by file, function and path, with the number of sites, one reason each. Its detector has accepting and refusing fixtures: `test_the_guard_sees_a_literal_read_and_nothing_else` (31 cases, one per spelling) |
| Statement gate: no theorem statement changes | AGENT | `git diff --quiet <merge-base> HEAD -- lean/statements.txt ...`: every train-only file is unchanged; no `.lean` file changed |
| Final full gate | EXTERNAL, merge chain | Runs on the committed HEAD after handoff; the builder did not run it |

**What the accessor does.** Each entry's overlay files are stamped together in `<entry>.stamp.json`, which
records each file's SHA-256 and the inputs. For the Lean entries the inputs are the hashes of the tree's modules
except the manifests. For the pins and the doc they are the committed copies. The overlay is fresh only when
every file of its entry matches the stamp and the stamp's inputs are the tree's. Otherwise the committed copy
of a Lean entry is used only if the committed `declarations.txt` records every module as it is. Under the flip
in gi-2b, a branch's committed copy is main's, so this means "no module differs from main". Until then a builder
who regenerated still passes, as DESIGN 7 step 2 requires. Anything else raises `StaleInventory`, which names up
to five modules and counts the rest. The pins and the doc cover no module: their own checks decide, by digest
membership and by rendering.

## Readers moved and what each checks now (DESIGN.md 9: no check gets weaker)

| Reader | Reads now | Check, before and after |
|---|---|---|
| `trust_map` (`scan_tree`, `read_tree`, `walk`, `measure`, `ledger`, `main`; `trust_changes`, `trust_mutants.plan` through `trust_map.inventory`) | The accessor's copy of the three lists. Each manifest module is hashed and scanned from its accessor copy | Same per-module "not compiled from this source" problems; the probe's `scan_tree()[3]` still counts them. The base is still measured from `git archive` of the base (`measure_rev`). `test_scan_tree_hashes_the_manifest_copy_the_accessor_gives` |
| `lean/audit.py` | Declarations, both manifests and `axioms.txt` through `inventory_path`; writes through `write_inventory` | The stale-declarations check is now the accessor's (same message, same modules); its duplicate was deleted. Manifest and record comparisons are unchanged. `test_lean_audit_record.py` (scratch tests and `test_committed_manifests_are_the_generated_ones`) |
| `lean_statements.py` `--check`, write, `audited_names`, default list paths | `inventory_status` copy; `write_inventory` | `--check` compares the fresh dump with the copy that readers get. A stale copy differs because the dump records the hashes |
| `regen_generated` `_lock`, `_write_lock` (`check_pins`, `pin_checkers`, `_Service`) | `inventory_path(PIN_FILE)`, with `PIN_FILE` taken from the registry | Unchanged digest-membership check. `test_regen_generated.py` bootstrap tests |
| `lean_service._spawn` pin read | `build_lock()`, which imports the accessor at run time (reason in its docstring) | Same pins, same refusal. `test_the_service_client_reads_its_pins_through_the_accessor` |
| `assurance_manifest.py --check`; `repo_map`; `check_readings_defaults_statements`; 23 test files | `inventory_path` | Unchanged comparisons |

## Seeded bugs (`mutants.json`; all Python; no Lean or Rust product code changed)

| Behaviour | File | Test that failed (exit 1), then restored |
|---|---|---|
| No fallback for a changed module | `tools/lean_statements.py` | `test_a_changed_module_with_no_overlay_is_a_stale_error_naming_it` |
| Overlay freshness needs this tree's inputs | `tools/lean_statements.py` | `test_a_fresh_overlay_is_read_and_a_stale_one_is_an_error` |
| Unknown `VE_INVENTORY` is refused | `tools/lean_statements.py` | `test_writers_write_the_committed_path_unless_the_overlay_is_asked_for` |
| `scan_tree` hashes the accessor's manifest copy | `tools/trust_map.py` | `test_scan_tree_hashes_the_manifest_copy_the_accessor_gives` |
| `read_tree` reads the accessor's predicate list | `tools/trust_map.py` | the same test |
| The service reads pins through the accessor | `ve/backends/lean_service.py` | `test_the_service_client_reads_its_pins_through_the_accessor` |
| The registry marks the doc train-only | `tools/regen_generated.py` | `test_the_registry_names_exactly_the_train_only_files` |
| The audit reads no literal copy | `lean/audit.py` | `test_no_train_only_path_is_read_outside_the_accessor` |
| F1 S1: `walk` reads `root / STATEMENTS` (a registry name) | `tools/trust_map.py` | `test_no_train_only_path_is_read_outside_the_accessor` |
| F1 S2: `_lock` reads `ROOT / PIN_FILE` (a name the registry computes) | `tools/regen_generated.py` | the same test |
| F1 S3: `--check` reads `ROOT / DOC` | `tools/assurance_manifest.py` | the same test |
| F1 S4: `olds` read `ROOT / name` over `dict(zip(...))` | `tools/lean_statements.py` | the same test |
| F1 S5: the manifest check reads `ROOT / manifest` (a module tuple) | `lean/audit.py` | the same test |
| F1 S6: a test reads `ROOT / "lean/statements.txt"`, ROOT imported | `tests/test_enum_domains.py` | the same test |
| F1 S7: a second read in an allowed function | `tools/repo_map.py` | the same test |

## Runs

- `uv run python tools/regen_generated.py --write` (once): exit 0. The Lean inventories, pins and doc are
  unchanged; it regenerated the code map and `tests/history-dependent.json` (6b3d8eaf, R12).
- `uv run python tools/trust_map.py --check`: `against 5f476e5fd236: K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0` and `PASS`. No R16 or R6 allowance and no FOLLOW-UPS row are needed.
- `lake build`: `Build completed successfully (1164 jobs)`. `tools/gate_collection.py --check --prebuilt`:
  `41 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed`. `lean/audit.py` was not rerun because no
  Lean changed.
- Selected run (`mac-pytest.sh --select`, GitHub Actions, 3 shards): 9 tests and `tools/test_layer_policy.py`
  failed (the `str` constant in `trust_changes`, the pin recorder's extra "data" read, and every unit selected
  through a static service import), and 24 units did not start. All were fixed in f401a186. Rerun: the 9 ids plus
  this test file passed (81 passed); `tools/test_layer_policy.py` passed (`OK`); the 24 skipped units passed
  (`10302 passed`).

## Review fix: F1 (review of c51307154)

F1 (B): the guard saw only `/` joins and whole-string module constants. The class is "a spelling the guard does not
fold", so the detector was rebuilt rather than patched: it folds every expression of a file to the paths it can
spell (strings, f-strings, `+`, `/`, `%`, `.format`, `Path`, `joinpath`, `os.path.join`, `str.join`, `glob`,
`dict`/`zip`, comprehensions, subscripts), through local and module names, tuple unpacking, loop variables, calls and
fixtures of the same file, the registry, and constants other modules export (`module.NAME` through imports). Outside
tests it fails where a path is first spelled; in tests on each read onto a tree the test did not make. It scans
every tracked Python file but `docs/` (before: `tools/`, `lean/`, `tests/`). Allow-list entries are keyed by
function and site count, so a new read in an allowed file still fails (seed S7).

- PROBE F1 (`open("lean/checkers.lock")` in a function): `AssertionError: guard blind` on c51307154; passes now.
- Regression tests: every spelling the review names is a case of `test_the_guard_sees_a_literal_read_and_nothing_else`
  (`open`, `Path(...).read_text()`, `.joinpath`, `os.path.join`, f-string, local variable, module tuple, `.format`,
  imported `ROOT`, function-local root, `audit.ROOT`, a helper called with ROOT, a registry name, a child script),
  with the refusing cases (`tmp_path` trees, `.name`, comparisons, prose, docstrings, the accessor).
  `test_the_guard_reads_a_registry_modules_own_names_by_their_value` and
  `test_the_file_filter_keeps_every_file_the_guard_finds_a_read_in` cover the two shortcuts.
- Seeds S1-S7 (table above) revert real readers, including the five spellings of review F2; each failed the tree test.
- The wider scan found no unmoved reader. Its new allow-list entries are the registry itself, the manifests' writer
  (`audit.MANIFESTS`), the two name tables of `trust_mutants` and `architecture_numbers` (one reads a revision's
  blobs), `assurance_manifest.document`'s template, `repo_map`'s existence check, `trust_map.rev_paths` (a revision's
  archive), two `test_regen_generated` sites (git attributes, a fake user on a tmp tree) and the pin readers of
  DESIGN.md 4 step 5. `lean_service._spawn` names the lock only for its refusal; it reads through `build_lock`.
- F2-F6 are C (FOLLOW-UP) and are not part of this fix. F2's five reversions now fail the guard (S1-S5).

## Size

`git diff --numstat <merge-base>`, without the code map and the history list: 1201 added and 141 deleted. Of
these, 697 are the new test file (about 460 of them the F1 guard), 157 are the accessor, 136 are this batch's
documents, and about 60 are one- or two-line reader moves in 25 test files. Every row is a deliverable or a DRI
condition (the guard is condition (a)), so no part was cut to a follow-on item.

## Found for gi-2b

- Pin readers kept on the allow-list: `answer_cutoff`, `gate` (two Rust checks), `gate_collection`,
  `lean_first_cache`, `lean_output_diff`, `lean_share` (two), `rust_build`. `test_map_recorder` only records the read.
  Since F1 the guard scans them too: `ve/backends/rust_jsonl.py` `BUILD_LOCK` and
  `research/defeasible/baseline.py` are on the pin-reader list; `lean_first_oracle.FROZEN` (git ls-tree of a
  revision) and `lean_share.lean_tree` (leaves the pins out of HEAD's tree hash) read no key.
- `test_map_recorder` calls a pin read "client" only when it comes from `lean_service._spawn`. Once an overlay
  exists, the accessor hashes the committed lock for the stamp. The one pin reader must keep that classification
  (`tests/test_answer_cutoff.py` failed on it).
- `docs/spec/assurance-manifest.md` has hand-written sections. A branch-mode "train-only path unchanged since the
  merge base" check would refuse edits to them.
- `tests/test_regen_generated.py`'s service-reach test now ignores paths that pass through the runner, because a
  script that imports the registry runs none of its steps.

## Spec re-read

`writer="train"` and one list: DESIGN.md 4 step 1 (lines 82-84). Overlay path, accessor, no silent fallback, the
reader list: step 2 (85-92) and DRI 1(b). `scan_tree` manifest hashes: step 4 (109-110). Writers' default kept and
overlay opt-in: 7 step 2 (238-240). Guard and readers: 8 row gi-2a (273). Checks kept: 9 (292-304).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay or response changed; the pin refusal is still CheckerUnavailable, `test_a_stored_answer_is_served_after_the_process_starts`).
2. Every deliverable and rule: PASS (delivery table; `test_inventory_path.py`).
3. Tests and gates can fail: PASS (15 seeded bugs above; both sides of the guard in `test_the_guard_sees_a_literal_read_and_nothing_else`).
4. Python, Lean and Rust agree: N.A. (no answer path changed; the train-only files are byte-identical).
5. R8 binding: N.A. (no relayed field).
6. Gate evidence matches final HEAD: N.A. (the chain gates the final HEAD; the tree is clean at handoff).
7. No unsigned item: PASS (`trust_map.py --check` +0; DELTA has no rows).
8. Every user-visible change in DELTA: PASS (`DELTA.md`; the inventory diff is empty).
9. Test selection finds the checks: PASS (`tools/test_layer_policy.py` OK and `test_select_tests.py` ids pass after the run-time import; `test_inventory_path.py` imports every changed module).
10. Lean statements and proofs: N.A. (no Lean change).
11. Budgets, limits and deadlines: N.A. (none changed).
12. CPU or memory regression: N.A. (no evaluator; each accessor call hashes about 670 sources, about 0.05 s measured).
13. Removed test trailers: PASS (`gate_collection.py --check --prebuilt`: 0 removed, 0 stale).
14. Both directions, cited evidence, spec re-read: PASS (accepting and refusing fixtures for each check above; Runs; Spec re-read).
