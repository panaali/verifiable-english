# AR-16b: `ve/readings_verdicts.py` becomes the package `ve/readings_verdicts/`

**Built and committed with a clean tree. No DRI signature is needed. One gap, as in AR-16a: `tools/batch_evidence.py
--check docs/arch/AR-16b` passes every section except `[gate]`.** The gate record can only be saved after the chain's
gate has run, and the saved scope, A/B and gate must all name the commit that was gated. So they are re-saved in one
follow-up commit that touches only `docs/arch/AR-16b/` (see "After the gate").

Plan: architecture review 2026-10 (`design/arch-review` 6ae55ebb8), section 4.4, row AR-16a/b/c ("16b (after RD-7):
`ve/readings_verdicts.py` along its classes (`Superposed`, `Enumerated`, the choice document) and the binding helpers
that AR-11 has not removed"); batch gate 4.1; coordination 4.2. The gate condition is met: RD-7 merged
(ve-green-rd-7), and AR-17, which changed the readings route, merged on 2026-10-20.

## Measured outcome

From `docs/arch/AR-16b/verbatim.py` and `cycles.py` (outputs in `evidence/`) and `wc -l`:

| Module | Lines | Holds (each module imports only the modules above it) |
|---|---:|---|
| `ve/readings_verdicts/route.py` | 143 | what every route shares: `_LeanBudget`, `BUDGET`, `PENDING`, `_dropped`, `_Route`, `Pending`, `_request_key` |
| `ve/readings_verdicts/binding.py` | 497 | the binding of a `readings-verdicts` answer to its request (AR-11's later target): `dead_finding`, `ROW_PIECES`, `PAIR_LABEL`, `_Frame`, `_shown_of`, `_need`, `INVALID_ANSWER`, `relayed`, `_labels`, `_check_rows`, `_walk`, `SHOWN_IN`, `_check_result`, `_check_dead`, `_check_english`, `_check_answer`, `_check_sup_answer`, `_bound_gaps` |
| `ve/readings_verdicts/choice.py` | 407 | the choice document: `_ChoiceDocument`, `_FilledView`, `_FilledChoiceDocument` |
| `ve/readings_verdicts/superposed.py` | 611 | `_found`, `_scaled`, `_public_sup_conflict`, `Superposed`, `_dead_certificates` |
| `ve/readings_verdicts/enumerated.py` | 224 | `_NOT_SUPERPOSABLE`, `Enumerated`, `_conflict_notes` |
| `ve/readings_verdicts/__init__.py` | 51 | the docstring, `context` and `__all__`, and the re-export of 22 names: the 18 that other modules, tests and tools import, and the module's other public names |

- **Before:** one module of 1,872 lines (merge base `25ac4131`). **After:** 6 files, 1,933 lines. The extra 61 lines
  are the module docstrings, the import headers and the package's re-exports. **Largest module:** `superposed.py`,
  611 lines. The target was no module over 1,000 lines; the largest is 39% under it.
- **Boundaries from the call graph.** Each module imports only the ones above it in the table, and only what it
  names: `binding` imports nothing of the package; `choice` imports 1 name (`BUDGET`); `superposed` imports 5
  (`BUDGET`, `_Route`, `_request_key`, `_check_sup_answer`, `_ChoiceDocument`); `enumerated` imports 8 (`BUDGET`,
  `_Route`, `_request_key`, `_Frame`, `_check_answer`, `_ChoiceDocument`, `_FilledChoiceDocument`, `_dead_certificates`).
  The four names the task left open went where their callers make the fewest cross-module references:
  - `_LeanBudget` (`BUDGET`) is read by `route`, `choice`, `superposed` and `enumerated`, so it sits in the lowest
    module. Every reader imports the one object, and a test's `BUDGET[...] = 0` reaches them all.
  - `_Route` is the base class of `Pending`, `Superposed` and `Enumerated`, so it goes in `route`.
  - `Pending` is 18 lines that only `context` calls, and its base is in `route`, so it goes there too.
  - `_Frame` goes in `binding`. Its readers are `_check_answer` and its helpers there, `Enumerated.frame`, and
    `ve/readings_components.py`.

  Placed by the same rule: `_dead_certificates` calls `Superposed._core_environment`, so it is in `superposed`, and
  `enumerated` imports it. `_request_key` is used by both routes, so it is in `route`. `dead_finding` is read only
  by `_check_dead`, so it is in `binding`. `context` needs all three routes, so it is in the package `__init__`.
  The order is pinned by `tests/test_readings_verdicts_split.py::test_each_module_imports_only_the_modules_before_it`.
- **A pure move.** `verbatim.py` checks four things. Each of the base's 38 top-level definitions is in exactly one
  module, with the same text. The only exception is an indented relative import, which gains one dot. All 10
  top-level comments are kept. The union of imports from outside the package is the base's. There are 90 indented
  imports before and 90 after. Result: 38/38 moved verbatim, 0 errors (`evidence/verbatim.json`). No check was
  reordered and no text changed.
- **Lazy imports.** 90 indented imports before and 90 after, all still indented. No module-level import was added
  that the base did not have. The new modules import their siblings directly (`from .route import BUDGET`), never
  the package: `test_no_module_imports_the_package_itself[*]`.
- **Import cycles** (`cycles.py`, an `ast` walk over every `ve/**/*.py` import at any depth, relative imports
  resolved). The first two rows were measured on a worktree of the merge base, the others on the head:

  | | modules | edges | cycles (sizes) | the readings/document cycle |
  |---|---:|---:|---|---:|
  | merge base `25ac4131` | 142 | 898 | 42, 17, 2 | 17 |
  | merge base, each import to the module that defines the name | 142 | 899 | 42, 13, 2 | 13 |
  | head, the package's modules read as one (the old module) | 142 | 898 | 42, 17, 2 | 17, the same 17 modules |
  | head, each module of the package a node | 147 | 930 | 42, 22, 2 | 22 = the 17, with the 5 new code modules |
  | head, each import to the module that defines the name | 147 | 940 | 42, 18, 2 | 18 = the base's 13, with the 5 new code modules |

  No cycle was added: read as one module, the cycle has the same 17 members as before (`evidence/cycles-before.json`,
  `cycles-after.json`). The 5 new code modules are on it because each keeps the old module's lazy imports of the
  readings modules, and those modules import the package back. `route` and `binding` import `readings_route` and
  `readings_s1` (`binding` also imports `readings_s2_wording`). `choice` imports `readings_s1`, `readings_sup` and
  `ve.document`. `superposed` imports `readings_route` and `readings_sup`. `enumerated` imports `readings_route`.
  Back the other way, `readings_route` (`context`), `readings_s2_wording` (`Enumerated`, `Superposed`, `context`) and
  `readings_components` import `ve.readings_verdicts`, whose `__init__` imports every module. These are real call
  paths: `readings_route` calls `context`, which builds a route whose checks call `readings_route` back. They stay on
  the cycle when each import is read as an import of the module that defines the name. **AR-16a's modules:**
  `ve.document.cli`, `ve.document.render` and `ve.document.report` are on the cycle only because callers import
  through `ve.document`'s `__init__` (`on_the_cycle_only_through_a_package_init`). This was already true at the
  base, and it is a follow-up (below); `ve/document/` is not edited here.
- **Monkeypatch targets.** At the merge base, five test lines patch something on `ve.readings_verdicts`. One needs a
  new target: it patches a name that a module now looks up in its own globals. The other four patch attributes of
  objects that the package and its modules share, and they reach the same object as before. The `package_patches`
  scanner of `tests/test_readings_verdicts_split.py` finds no remaining patch of a name on the package that a module
  looks up, and no `patch("ve.readings_verdicts.<name>")` string, in `tests/`, `tools/` or `conformance/`.

  | Site (merge base line) | Patched | Now patches | Mutant (killed) |
  |---|---|---|---|
  | `tests/test_readings_sup_verdicts.py:251` | `_ChoiceDocument` on the module | **retargeted**: `ve.readings_verdicts.superposed`, where `Superposed._lifted` looks it up | M1; M12 shows the old target no longer reaches it |
  | `tests/test_premise_scale.py:72` | `BUDGET._set` (an attribute of the one `BUDGET` object) | unchanged; the same object as `route.BUDGET` | M2 |
  | `tests/test_premise_scale.py:382` | `BUDGET._set` | unchanged | M3 |
  | `tests/test_premise_scale.py:387` | `BUDGET._set` | unchanged | M4 |
  | `tests/test_readings_verdicts_lean.py:580` | `Enumerated.check_answer` (a class attribute) | unchanged; the same class object | M5 |

  M12 is the converse check. It puts the base's target back (`monkeypatch.setattr(readings_verdicts,
  "_ChoiceDocument", ...)`), and the test fails with no bug planted, because the stand-in is never called. So the
  retargeted patch is the one that reaches the code.
- **Behaviour (gate 4.1 item 2):** `tools/lean_first_diff.py` over all nine corpora of the lean-first gate. Each
  corpus was recorded on its own, the base from a worktree of the merge base `25ac4131` and the head from a worktree
  of `1f9edc44`, one side after the other. **Result: 0 differences.** Each of the nine corpora's recordings is
  byte-identical between base and head, and so are the two whole files (SHA-256 `9ffbd9e5…` for both). `compare`
  gives 100,457 records the same and 21 unavailable on both sides with identical outputs, every one listed with its
  reason (R7, `evidence/ab-delta.json`), and 0 unlisted (`evidence/ab.json`). The 21 are the 14 constitution
  companion documents and 7 whole-UDHR runs at the recorder's 600 s limit on both sides (DELTA rows 1 and 2). The
  recordings are in `~/.cache/ve-ar16b-ab2/{base,head}.jsonl.gz` (7.8 MB each, over D4's 1 MB), so they stay out of
  the tree, and `evidence/ab.json` records their SHA-256. On the first recording,
  against the earlier base `f1943fab`, eight corpora were byte-identical. In pilots, two whole-UDHR records (runs
  20261012T0600Z and 20261012T1800Z) hit the recorder's 600 s limit on the base, while the head answered (PIPELINE-
  LIMITS L75). Re-run alone, one after the other (`docs/arch/AR-16a/pilot_rerun.py --timeout 1500`), both sides
  answered with identical outputs: 635 s base against 848 s head, and 656 s against 519 s
  (`evidence/pilot-rerun.json`). With the re-runs in, the two recordings were byte-identical (SHA-256 `a755e9f1…`
  for both). `main` then moved to `25ac4131` (me-2b), and the whole A/B was recorded again at the new base: the result above.
- **CPU, base against head** (`pilot_cpu.py`, `evidence/pilot-cpu.json`). Three constitution readings pilots, two
  alternating rounds, CPU time of the whole child process tree. The ratios of the head's minimum to the base's are:
  `all-strict-narrow` 1.018 (7.40 s base, 7.53 s head), `nd-all` 0.823 (70.3 s, 57.8 s), and `soft-chain` 0.926
  (24.8 s, 23.0 s). Every output was identical.
- **Relay mutation gate** (`tools/relay_mutation_gate.py --json`, `evidence/relay-gate-{base,head}.json`). Base
  `25ac4131` and head `1f9edc44` give 43 routes, 138,735 mutants and 0 failures each. Every route's counts per
  verdict class and per allow-list entry are equal. The two files differ only in their `seconds` fields.
  `tools/relay-gate-allow.json` is unchanged. Before the sync, at `f1943fab` against `becce6b8`, both sides gave
  42 routes, 137,782 mutants and 0 failures, again equal but for `seconds`.
- **Trust:** `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted
  +0". PASS.
- **Lean, Rust:** no change. `lean/` and `rust/` are `main`'s.

## Plan rows and directives

| Directive | Delivered by | Test or evidence |
|---|---|---|
| `ve/readings_verdicts.py` → `ve/readings_verdicts/` along `Superposed`, `Enumerated`, the choice document and the binding helpers; boundaries from the call graph (`_Route`, `_Frame`, `_LeanBudget`, `Pending` placed by their callers), stated with line counts | `19b8c282` | table above; `tests/test_readings_verdicts_split.py` |
| No module over 1,000 lines | `19b8c282` | largest 611 (`superposed.py`) |
| A pure move: no behaviour or text change, no reordered checks, code verbatim apart from imports | `19b8c282` | `evidence/verbatim.json` (38/38, 0 errors); A/B 0 differences |
| `ve.readings_verdicts` keeps every name importable today | `19b8c282` (`__init__`) | `test_every_name_callers_import_is_the_owners_object[*]` (22), `test_context_and_the_public_names_stay_the_packages` |
| Retarget every monkeypatch; for each retargeted patch, plant a bug and show the test fails | `19b8c282` | M1, M12 (retargeted); M2 to M5 (unchanged patches still reach); `test_no_test_patches_the_package_where_a_module_looks_the_name_up` |
| Lazy imports stay lazy; no new cycle; submodules import their siblings, never the package | `19b8c282` | `verbatim.json` (90/90 indented imports); `cycles-*.json`; `test_no_module_imports_the_package_itself[*]` |
| Cycle sizes before and after from an `ast` walk, saved as evidence (not a test); new modules on the cycle and why; AR-16a modules on it only through `ve.document`'s `__init__` | `docs/arch/AR-16b/cycles.py` | `evidence/cycles-before.json`, `cycles-after.json`; follow-up 1 |
| `tools/layer_policy.py`: the new modules get `readings_verdicts`' layer | no edit needed: the `readings_verdicts` entry covers the package (`ve/readings_verdicts/*` maps to `ve.readings_verdicts`) | `uv run python tools/repo_map.py file ve/readings_verdicts/__init__.py` → "layer: 4 (tools)", and the same for `binding.py`; `tools/check_python_layers.py` "1 kept, 0 broken"; `.importlinter` unchanged |
| Generated files through `regen_generated.py --write`; `repo_map.py --check`; `repo_map.py file ve/readings_verdicts/__init__.py` | binding census regenerated (`19b8c282`, and after the merge in `1f9edc44`) | `regen_generated.py --check`: PASS after `--write` ("wrote 33 entries"); `repo_map.py --check`: "PASS: 38 modes"; `repo_map.py route readings-route` lists `ve/readings_verdicts/binding.py (_check_answer, _check_sup_answer)` |
| `ve/assurance-manifest.json`: the path naming `ve/readings_verdicts.py` follows the move, as its own tooling expects | `19b8c282` | its regen entry is hand-reviewed pins with check `check_assurance_pins()`; the key `ve/readings_verdicts/binding.py:relayed` keeps its place and reason; `tools/assurance_manifest.py --check` exit 0; `tests/test_assurance_manifest.py` passes in the selection |
| Relay mutation gate: the same verdict per mutant before and after; `relay-gate-allow.json` gains no entry | evidence | `evidence/relay-gate-{base,head}.json`: equal but for `seconds`; allow-list unchanged |
| `lean_first_diff.py` over the gate corpora, 0 differences | evidence | `evidence/ab.json`, 0 unlisted |
| D4: no permanent report or evidence test, no per-batch mutant script; `evidence.toml`; files under 1 MB; `batch_evidence.py --check` | `docs/arch/AR-16b/` | `tests/test_readings_verdicts_split.py` pins package structure, not batch numbers; mutants run by `tools/mutants.py`; the largest evidence file is 255 KB (`pilot-rerun.json`), and the recordings (7.8 MB each, gzip) stay in `~/.cache/ve-ar16b-ab2/` with their SHA-256 in `evidence/ab.json` |
| Coordination: overlaps with branches in flight | checked at start and after syncing | see "Coordination" |
| `trust_map.py --check` shows no change | | +0 everywhere |
| One owner per piece of logic; no weakened check; no deleted test | | `relay_lint.py` reads more modules, not fewer (M10, M11); `gate_collection.py --check --prebuilt`: 38 added, 0 removed, 0 refused, 0 stale, 0 malformed |

### Inventories and tools that keyed on the old path

All of these are in `19b8c282` unless noted:

- `ve/assurance-manifest.json`: the reviewed broad handler `ve/readings_verdicts.py:relayed` became
  `ve/readings_verdicts/binding.py:relayed` (`test_broad_exception_handlers_are_reviewed` finds it there).
- `tools/identity-sites.json`: its three sites (`_ChoiceDocument._bound`, `_ChoiceDocument._bound.meaning`,
  `_FilledChoiceDocument._packages.meaning`) name `ve/readings_verdicts/choice.py`. `tools/identity_lint.py`:
  "PASS: 45 identity site(s) in 21 module(s)".
- `tools/relay_lint.py`: the reserved-name rule and the wording rule read `ve/readings*.py` *and* `ve/readings*/*.py`
  (`READINGS_GLOBS`, `readings_modules()`). Before the change, the glob `ve/readings*.py` would have stopped
  reading the moved code, so the rules would have checked less. `test_every_readings_module_is_read_by_the_reserved_rule`
  (M10) and the new `test_the_wording_rule_reads_every_readings_module` (M11) check that they read the package.
  `relay_lint.py`: "14 readings module(s), no reserved completion name; 18 readings and norm-defaults module(s), no
  situation or point wording".
- `docs/test-architecture/binding-probes.jsonl.gz`: the one recorded probe whose site named `ve/readings_verdicts.py`
  names `ve/readings_verdicts/superposed.py`, the module that holds its line text. The rename was done by
  `rename_probe_sites.py`, which resolves by text: `conflict` is defined in three modules. The census was then
  regenerated. 10,204 probes, 1 site renamed; nothing else in the recording changed.
- Two tests that read the module's source: `test_python_sup_has_no_fold_or_dependency_replay`
  (`tests/test_readings_sup_verdicts.py`) now reads every module of the package, and the readings rules of
  `tests/test_relay_lint.py` call `readings_modules()`.
- Report tests of rd2b, rd3 and rd6b check that each saved seeded bug's file exists. Their saved evidence names
  `ve/readings_verdicts.py`, so each gains a `MOVED` map, as AR-16a added for rd2a
  (`test_seeded_bugs_name_real_tests_and_rows`, `test_saved_mutants_failed_real_tests_and_were_removed`,
  `test_round3_mutants_were_rejected_and_reported`, `test_saved_latency_and_seeded_bugs`).

## Coordination

At the start, and again after syncing with `main` at `25ac4131` (me-2b had merged; it does not touch
`ve/readings_verdicts.py`), every branch in flight (`git branch --list 'lean-first/*' 'feature/*' 'infra/*'
'foundation/*'`) was checked with `git diff --name-only main...<branch>` against this batch's hand-written paths:

- `feature/q1-4`: `tools/relay_lint.py`, `ve/assurance-manifest.json` (and `ve/ask.py`, which this batch does not
  touch). q1-4's `relay_lint.py` hunk changes lines 69–72 (`RELAYED_FUNCTIONS`); this batch's change the module docstring
  (line 23), lines 77–78 (`READINGS_GLOBS`), 92 (`WORDING_GLOBS`) and 342–351, with unchanged lines between.
  `git merge-tree --write-tree HEAD feature/q1-4` merges with no conflict (exit 0). In the manifest, both change only their own
  keys. The manifest has a per-key merge rule ("a merge keeps each side's pins"; `.gitattributes`
  `merge=ve-generated`).
- `feature/sc-1b`, `feature/jt-2`, `foundation/me-1`: `ve/assurance-manifest.json` (per-key merge, as above; this
  batch changes one key).
- `feature/jt-2`: `docs/test-architecture/binding-census.{json,md}`. These are generated (R12: not an overlap), and
  `regen_generated.py --resolve` rebuilds them.
- No branch in flight edits `ve/readings_verdicts.py`, and none adds an import from it (`git diff main...<branch> |
  grep '^+' | grep -c readings_verdicts` = 0 for sc-1b, q1-4, ap-3, speed-tmchecks, eff-20261026-1 and
  arch-20261026-2).

## DELTA

`DELTA.md`: none. The only rows are records unavailable on both sides with identical outputs (R7).

## Seeded bugs

`docs/arch/AR-16b/mutants.json`, run by `uv run python tools/mutants.py docs/arch/AR-16b/mutants.json --evidence
docs/arch/AR-16b/evidence/mutants.json` on the merged head: 12/12 killed. Every one is Python (`ve/readings_verdicts/`,
`tools/relay_lint.py` and one test file). No Lean or Rust product code changed.

| Id | File | Bug | Failing test |
|---|---|---|---|
| M1 | `ve/readings_verdicts/superposed.py` | `Superposed._lifted` no longer caches a small choice's document (the retargeted patch's path) | `test_readings_sup_verdicts.py::test_repeated_premise_proposals_search_each_small_choice_once` |
| M2 | `ve/readings_verdicts/route.py` | every `BUDGET` key reads `max_proof_steps` | `test_premise_scale.py::test_the_readings_budget_is_leans` |
| M3 | `ve/readings_verdicts/superposed.py` | `_scaled` skips the ground-fact route | `test_premise_scale.py::test_readings_premise_check_takes_the_ground_route` |
| M4 | `ve/readings_verdicts/route.py` | a budget key a test sets to 0 is ignored | the same test |
| M5 | `ve/readings_verdicts/enumerated.py` | the conflict-notes check never runs | `test_readings_verdicts_lean.py::test_a_reading_s_conflict_notes_are_the_same_in_every_answer` |
| M6 | `ve/readings_verdicts/binding.py` | a row's word need not name a piece the row notes accepted | `test_readings_verdicts_lean.py::test_every_row_word_names_a_piece_lean_accepted` |
| M7 | `ve/readings_verdicts/choice.py` | a filled choice's model keeps the filled tables in its base | `test_readings_rd6b_differential.py::test_generated_documents_agree_on_both_routes[0]` |
| M8 | `ve/readings_verdicts/__init__.py` | a re-export (`_public_sup_conflict`) dropped | `test_readings_verdicts_split.py::test_every_name_callers_import_is_the_owners_object[_public_sup_conflict]` |
| M9 | `ve/readings_verdicts/__init__.py` | `context` builds the superposed route for an enumerated document | `test_readings_verdicts_lean.py::test_fnd1_query_some_each_reading_named_by_its_own_sentence` |
| M10 | `tools/relay_lint.py` | the reserved-name rule reads `ve/readings*.py` only | `test_relay_lint.py::test_every_readings_module_is_read_by_the_reserved_rule` |
| M11 | `tools/relay_lint.py` | the wording rule's globs are the base's | `test_relay_lint.py::test_the_wording_rule_reads_every_readings_module` |
| M12 | `tests/test_readings_sup_verdicts.py` | the patch back on the package (the base's target) | `test_readings_sup_verdicts.py::test_repeated_premise_proposals_search_each_small_choice_once` |

A first choice of test for M6 (the rows-exactly check `_need(expected and seen == expected)` in `_check_rows`) did
not kill it. `tests/test_readings_verdicts_lean.py`, `test_readings_sd_relay.py` and `test_readings_components_load.py`
(149 tests) all pass with that check reduced to `_need(expected)`. The code is the base's, verbatim, so this gap
already existed (follow-up 2). M6 now seeds the row-word check of the same function instead.

## Tests run

- Selected tests (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, on ve-mac-1, at `becce6b8`):
  185 of 462 units, exit 0, 0 failed, 3,266 s. The selection includes every test the mutants name
  (`select_tests.py`: `test_readings_sup_verdicts.py`, `test_premise_scale.py`, `test_readings_verdicts_lean.py`,
  `test_readings_rd6b_differential.py`, `test_readings_verdicts_split.py`, `test_relay_lint.py`).
- After the sync with `main` (`1f9edc44`): the seeded mutants (12/12), the relay mutation gate and the A/B were run
  again at the new base and head. The selected tests were run again too; see the last line below.
- `tests/test_readings_verdicts_split.py` (37), `tests/test_relay_lint.py`, `tests/test_words.py`,
  `tests/test_identity_lint.py`, `tests/test_assurance_manifest.py`, `tests/test_binding_census.py` and the rd2a,
  rd2b, rd3, rd4a, rd6b and q2 report tests passed.
- Not run here, per the task: the full gate (`tools/gate.py`), which the chain runs on the final HEAD.

## Follow-ups (not in this batch)

1. **AR-16a's modules on the cycle through `ve.document`'s `__init__`:** `ve.document.cli`, `ve.document.render` and
   `ve.document.report`. They would leave the readings/document cycle (13 instead of 17 nodes at the base) if
   `ve/readings_verdicts/choice.py` and the other readings modules imported the submodule that defines what they use,
   for example `from ..document.source import _environment` instead of `from ..document import _environment`.
   That edits the readings modules' code, which a pure move does not.
2. **`_check_rows`'s rows-exactly check is not covered by a test that fails without it** (see "Seeded bugs"). A
   test of a verdicts answer whose rows are a reordered or shortened copy of the request's choices, with every other
   member consistent, would cover it.
3. Two unused lazy imports, `from ..entailment import prove_entailment` in `Superposed._generate_conflict` and in
   `Superposed._generate_certificate` (ruff F401). They were the base's too and moved verbatim.
4. `_NOT_SUPERPOSABLE = "ReadingsNotSuperposable: "` has a second copy in `ve/readings_components.py:25` (one owner per
   piece of logic). This was already true at the base.
5. An order-dependent failure, the same at the base: in one process, `tests/test_words.py` and
   `tests/test_relay_lint.py` before `tests/test_assurance_manifest.py` make
   `test_python_entries_resolve_to_guarded_callables` fail (`('ve_frozen.norm_english:parse_english',
   'english.statement')` is registered by an earlier import). Alone, and in the selection, it passes.
6. Text that still names `ve/readings_verdicts.py`, out of scope for a move that changes no text: `docs/ARCHITECTURE.md`
   (lines 44 and 138), the docstring of `ve/norm_defaults_route.py:76`, two Lean docstrings with line numbers
   (`lean/VE/Readings/Verdicts.lean:452, 462`), and specifications and saved batch evidence under `docs/`.
7. The whole-UDHR pilot still runs near the recorder's 600 s limit under load (L75): 519 s to 848 s alone here.

## After the gate

The scope, the A/B and the gate must name the commit the chain gates (`<G>`). After the chain's gate of `<G>`,
make one report commit that changes only `docs/arch/AR-16b/`:

    cp gate-result.json docs/arch/AR-16b/evidence/gate.json
    uv run python -m tools.evidence scope --base main --head <G> --out docs/arch/AR-16b/evidence/scope.json
    gunzip -kf ~/.cache/ve-ar16b-ab2/base.jsonl.gz ~/.cache/ve-ar16b-ab2/head.jsonl.gz
    uv run python -m tools.evidence ab ~/.cache/ve-ar16b-ab2/base.jsonl ~/.cache/ve-ar16b-ab2/head.jsonl \
        --base-commit 25ac413119c8991d1385cc95c51bcaac7415f9a2 --head-commit <G> \
        --out docs/arch/AR-16b/evidence/ab.json --delta docs/arch/AR-16b/evidence/ab-delta.json
    uv run python -m tools.evidence report docs/arch/AR-16b   # paste between the markers
    uv run python tools/batch_evidence.py --check docs/arch/AR-16b --report-commit HEAD

The head recording was made at `1f9edc44`. From there to `<G>`, `ve/`, `lean/`, `rust/`, `conformance/` and
`tools/lean_first_diff.py` are unchanged: `git diff --stat 1f9edc44 <G> -- ve lean rust conformance
tools/lean_first_diff.py` is empty, and the commits after it change only `docs/arch/AR-16b/`.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A. No relay, schema or binding changed. `_check_answer`,
   `_check_sup_answer` and their helpers moved verbatim (`evidence/verbatim.json`), and their fuzz tests pass
   unchanged (`tests/test_readings_verdicts_lean.py::test_a_mutated_verdicts_answer_is_unavailable`,
   `tests/test_readings_sup_verdicts.py`). The relay mutation gate is equal at base and head
   (`evidence/relay-gate-*.json`).
2. Every deliverable built, no rule broken: PASS. See "Plan rows and directives". No new report test (D4): the only
   new test file is `tests/test_readings_verdicts_split.py`, which pins structure. No new Python copy of a Lean
   decision. Overlaps are listed under "Coordination".
3. Tests can fail: PASS. 12/12 seeded mutants killed (`evidence/mutants.json`): M1 for the retargeted patch, M12 for
   its old target, and M2 to M5 for the four patch sites that still reach their path.
   `test_the_scanner_finds_a_patch_on_the_package` shows that the stale-patch scanner finds patches.
4. Python, Lean and Rust agree; valid inputs still pass: PASS. The corpus A/B over nine corpora has 0 unlisted
   differences (`evidence/ab.json`), and the recordings are byte-identical.
5. R8 binding: N.A. The binding code moved verbatim; no field read changed.
6. Gate evidence matches the final HEAD: N.A. here. The chain gates the final HEAD, and "After the gate" lists the
   re-save. The scope base is `git merge-base` (`25ac4131`), synced with `main` in `0865c873`.
7. No unsigned item: PASS. DELTA's two rows cite R7. Trust +0 (`trust_map.py --check`).
8. Every user-visible change in DELTA: PASS. The A/B is empty, so DELTA says none.
9. Test selection: PASS. 185/462 units, not every unit. It includes every test file the mutants name.
10. Lean statements: N.A. No Lean change.
11. Budgets, limits and deadlines: N.A. No budget path changed. `BUDGET` is one object, and M2 and M4 show that a
    test's zero still reaches it. `test_readings_budget_zero.py` passes in the selection.
12. No CPU or memory regression: PASS. A pure move: base and head recordings are identical. CPU time, base against
    head, on three readings pilots: ratios 1.018, 0.823 and 0.926 (`evidence/pilot-cpu.json`). Solo whole-UDHR wall
    time was 635 s base against 848 s head, and 656 s against 519 s. That is noise on a shared VM; the code that
    runs is the same text.
13. Test-removed trailers: PASS. `uv run python tools/gate_collection.py --check --prebuilt`: 19,419 collected,
    38 added, 0 removed, 0 refused, 0 stale, 0 malformed.

<!-- BEGIN GENERATED AR-16B NUMBERS -->
- Scope: `25ac4131..1f9edc44 --no-merges`, 4 commits: `1f9edc44`, `7f873a0f`, `becce6b8`, `19b8c282`.
- Corpus A/B (`25ac4131` against `1f9edc44`): 100457 records identical, 21 unavailable on both sides with identical outputs (R7, listed), 0 unlisted; pilots 631, document 3632, discourse 6350, rights 2500, readings 1137.
- Seeded mutants (tools/mutants.py): 12/12 killed.
<!-- END GENERATED AR-16B NUMBERS -->
