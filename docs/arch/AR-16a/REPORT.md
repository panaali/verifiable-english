# AR-16a: `ve/document.py` becomes the package `ve/document/`

**Built and committed with a clean tree. No DRI signature is needed. One gap: `tools/batch_evidence.py --check
docs/arch/AR-16a` passes every section except `[gate]`.** The gate record can only be saved after the chain's
gate has run. The saved scope, A/B and gate must all name the commit that was gated, so they are re-saved in one
follow-up commit that touches only `docs/arch/AR-16a/` (see "After the gate").

Plan: architecture review 2026-10 (`design/arch-review` 6ae55ebb8), section 4.4, row AR-16a/b/c ("16a (after
lf-16g): `ve/document.py` → `ve/document/` with file reading and front matter, the Lean relay and binding,
rendering and the report display"); batch gate 4.1; coordination 4.2. The gate condition is met: lf-16g has merged.

## Measured outcome

From `docs/arch/AR-16a/verbatim.py` and `cycles.py` (outputs in `evidence/`) and `wc -l`:

| Module | Lines | Holds (each module imports only the modules above it) |
|---|---:|---|
| `ve/document/source.py` | 198 | file reading and front matter: `MAX_DOCUMENT_BYTES`, `SUPPORTS`, `STATUSES`, `_body`, `front_matter`, `_split`, `_parts`, `_english_fences`, `_document_id`, `_environment`, `stored_identities`, `base_environment`, `_no_lone_surrogate` |
| `ve/document/containers.py` | 132 | the unit roles both load paths build: `_wire_unit`, `_soft_contents`, `_readings_routes`, `_s1_attached`, `_free_norms`, `_defaults_environment`, `_reading_plan`, `_content_bearing`, `_content_environment`, `_RIGHTS_KINDS`, ... |
| `ve/document/lean.py` | 390 | the Lean relay and binding (AR-11b's later target): `_document_case`, `_lean_answer`, `_lean_document`, `_bind_document_answer`, `_soft_bound`, `_spans_a_strict_fence`, `_names_a_model_member`, `_BLOCK_LINES` |
| `ve/document/load.py` | 434 | `load_document`, `_load`, Python's retained loader `_load_document`, `_meaning`, `_content`, `_quantity_content` |
| `ve/document/report.py` | 629 | the report: `check_document`, `_check_document`, `_report`, `coverage`, `coverage_defaults`, the premises, the rights and lower routes, `_check_narrowing_choices`, `quantity_admission_input`, `_graph_nodes` |
| `ve/document/render.py` | 200 | `render_document` |
| `ve/document/cli.py` | 122 | `main` (`ve document`) |
| `ve/document/__init__.py` | 41 | the docstring, and the re-export of every name callers import (32 of the package's own, and `Environment`, `digest`, `rights_meaning_id`) |
| `ve/document/__main__.py` | 6 | `python -m ve.document` |

- **Before:** one module of 2,038 lines (merge base `beb5c463`). **After:** 9 files, 2,152 lines. The extra
  114 lines are the module docstrings, the import headers and the package's re-exports. **Largest module:**
  `report.py`, 629 lines. The target was no module over 1,000 lines; the largest is 37% under it.
- **Boundaries from the call graph.** `source` calls nothing in the package. `containers` calls `source`.
  `lean` builds the request from `source` and `containers` and binds the answer. `load` chooses Lean's answer
  (`lean`) or the retained loader. `report` reads a loaded document. `render` and `cli` sit on top. The order is
  pinned by `tests/test_document_split.py::test_each_module_imports_only_the_modules_before_it`.
- **A pure move.** `verbatim.py` checks that each of the base's 63 top-level definitions is in exactly one
  module, with the same text. The only exception is an indented relative import, which gains one dot. It also
  checks that both top-level comments are kept and that the union of imports from outside the package is the
  base's. Result: 63/63 moved verbatim, 0 errors (`evidence/verbatim.json`). No check was reordered and no text
  changed.
- **Lazy imports.** 87 indented imports before and 87 after, all still indented. No module-level import was
  added that the base did not have (`verbatim.py`, header comparison).
- **Import cycles** (`cycles.py`, an `ast` walk over every `ve/**/*.py` import at any depth):

  | | modules | edges | cycles (sizes) | the document cycle |
  |---|---:|---:|---|---:|
  | merge base `beb5c463` | 134 | 815 | 42, 10, 2 | 10 |
  | head, the package's modules read as one (the old module) | 134 | 815 | 42, 10, 2 | 10, the same 10 modules |
  | head, each module of the package a node | 142 | 898 | 42, 17, 2 | 17 = the 10, with `ve.document` replaced by `ve.document` and its 7 code modules |

  No cycle was added. The raw component grows by 7 nodes only because one module became eight: the readings
  modules import `ve.document`, whose `__init__` imports every submodule, and each submodule reaches the readings
  modules back. The cycle keeps the same 10 members as before (`evidence/cycles-before.json`,
  `cycles-after.json`).
- **Monkeypatch targets retargeted: 12 of 12.** The `package_patches` scanner of `tests/test_document_split.py`
  was run over the merge base's `tests/`, `tools/`, `conformance/` and `docs/lean-first/`. It finds 12 sites, in
  5 test files, that patch a name on `ve.document`. The "about 21" of the task prompt counted the patches in these
  files that target other modules (for example `relay.answer`); a move does not affect those. Each of the 12 now
  patches the module that looks the name up. A seeded bug in each patched path makes that test fail
  (M1 to M12 below). `test_no_test_patches_the_package_where_a_module_looks_the_name_up` keeps it so: it fails on
  any patch of `ve.document.<name>` where a module of the package reads `<name>`.

  | Site (merge base line) | Patched name | Now patches | Mutant |
  |---|---|---|---|
  | `tests/test_b16d_document.py:86` | `_load_document` | `ve.document.load` | M1 |
  | `tests/test_b16d_document.py:123` | `_load_document` | `ve.document.load` | M2 |
  | `tests/test_document_lean_switch.py:61` (`no_python_loader`) | `_load_document` | `ve.document.load` | M3 |
  | `tests/test_document_lean_switch.py:71` | `_load_document` | `ve.document.load` | M4 |
  | `tests/test_document_lean_switch.py:100` | `_load_document` | `ve.document.load` | M5 |
  | `tests/test_document_lean_switch.py:382` | `_load_document` | `ve.document.load` | M6 |
  | `tests/test_b16e_rights_document.py:53` | `_lean_answer` | `ve.document.load` | M7 |
  | `tests/test_b16f_document.py:54` | `_lean_answer` | `ve.document.load` | M8 |
  | `tests/test_b16f_senses_document.py:67` | `_lean_answer` | `ve.document.load` | M9 |
  | `tests/test_document_lean_switch.py:604` | `Environment` | `ve.document.source` and `ve.document.lean`, which both looked it up in the one module | M10 |
  | `tests/test_document_lean_switch.py:632` | `admit_document` | `ve.document.report` | M11 |
  | `tests/test_document_lean_switch.py:639` | `_check_narrowing_choices` | `ve.document.report` | M12 |

- **Behaviour (gate 4.1 item 2):** `tools/lean_first_diff.py` over all nine corpora of the lean-first gate.
  Base `beb5c463` was recorded from a worktree and the head from this checkout, one side after the other. Result:
  **0 differences**: 100,428 records the same and 14 unavailable on both sides with identical outputs (R7,
  `evidence/ab-delta.json`). After the re-runs below, the base and head recordings are byte-identical (SHA-256
  `9f4f3bdd…` for both).
  - Two whole-UDHR pilot records (runs 20261012T0600Z and 20261012T1800Z) hit the recorder's 600 s limit on the
    head while the machine's load average was about 50. The base answered them. Re-run alone, one after the other
    (`pilot_rerun.py --timeout 1500`), both sides answered with identical outputs: 482 s base against 486 s head,
    and 632 s against 797 s (`evidence/pilot-rerun.json`). The head's recording carries those re-runs. This is
    PIPELINE-LIMITS L75; the as-recorded file is kept as `head-as-recorded.jsonl.gz`.
  - A pilot branch, `pilot/cc-20261019T1800Z`, was published during the run (8 new documents). They were recorded
    the same way on both sides: 8/8 identical.
  - The recordings are in `~/.cache/ve-ar16a-ab/` (7.7 MB each, gzip). That is over D4's 1 MB, so they stay out of
    the tree; `evidence/ab.json` records their SHA-256.
- **Trust:** `uv run python tools/trust_map.py --check`: "against beb5c4630262: K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0". PASS.
- **Lean, Rust:** no change. `lean/` and `rust/` are `main`'s.

## Plan rows and directives

| Directive | Delivered by | Test or evidence |
|---|---|---|
| `ve/document.py` → `ve/document/`: file reading and front matter, Lean relay and binding, rendering, report display; boundaries from the call graph, stated with line counts | `7b44fdf4` | table above; `tests/test_document_split.py` |
| No module over 1,000 lines | `7b44fdf4` | largest 629 (`report.py`) |
| A pure move: no behaviour or text change, no reordered checks, code verbatim apart from imports | `7b44fdf4` | `evidence/verbatim.json` (63/63, 0 errors); A/B 0 differences |
| `ve.document` keeps every name importable today | `7b44fdf4` (`__init__`) | `test_every_name_callers_import_is_the_owners_object[*]` (32), `test_the_imported_names_callers_read_are_their_modules_objects[*]` (3), `test_python_m_ve_document_runs_the_command_line` |
| `readings_route.py`, `readings_sup.py`, `readings_s1.py` untouched; `elaborate`, `validate`, `report` and `Wording` called as before | not in the diff (`git diff --name-only main...HEAD`) | `verbatim.json`: the calls moved verbatim |
| Retarget every monkeypatch; for each, plant a bug and show the test fails | `7b44fdf4`, `357efd11` | M1 to M12; `test_no_test_patches_the_package_where_a_module_looks_the_name_up` |
| Lazy imports stay lazy; no new cycles; cycle sizes before and after, from an `ast` walk saved as evidence, not as a test | `7b44fdf4`; `cycles.py` | `evidence/cycles-before.json`, `cycles-after.json` |
| `tools/layer_policy.py`: the new modules get `document`'s layer | no edit needed: the `document` entry covers the package (`ve/document/*` maps to `ve.document`) | `uv run python tools/repo_map.py file ve/document/__init__.py` → "layer: 4 (tools)", and the same for `lean.py`; `tools/check_python_layers.py` "1 kept, 0 broken" |
| Generated files through `regen_generated.py --write`; `repo_map.py --check`; `repo_map.py file ve/document/__init__.py` | binding census regenerated (`7b44fdf4`, and by `--resolve` in the merge `0016c3d9`) | `regen_generated.py --check`: "checked 31 entries", PASS; `repo_map.py --check`: "PASS: 37 modes" |
| `ve/assurance-manifest.json`: its 3 paths to `ve/document.py` follow the move, as its own tooling expects | `7b44fdf4` | its regen entry is hand-reviewed pins with check `check_assurance_pins()`; `tools/assurance_manifest.py --check` exit 0; `tests/test_assurance_manifest.py` 137 passed |
| `lean_first_diff.py` over the gate corpora, 0 differences | evidence | `evidence/ab.json`, 0 unlisted |
| D4: no permanent report or evidence test, no per-batch mutant script; `evidence.toml`; `batch_evidence.py --check` | `docs/arch/AR-16a/` | `tests/test_document_split.py` pins package structure, not batch numbers (it was revised in `6eba0d5f` so that it no longer freezes the pre-split name list); mutants run by `tools/mutants.py` |
| Coordination: overlaps with branches in flight | checked at start and after syncing | see "Coordination" |
| `trust_map.py --check` shows no change | | +0 everywhere |
| One owner per piece of logic; no weakened check; no deleted test | | `gate_collection.py --check --prebuilt`: 48 added, 0 removed, 0 refused, 0 stale, 0 malformed |

### Inventories and tools that keyed on the old path

All of these are in `7b44fdf4` unless noted:

- `ve/assurance-manifest.json` (three reviewed handlers) and `docs/spec/assurance-manifest.md` (regenerated).
- `tools/identity-sites.json` (four sites).
- `tools/semantic_inventory.py`: the key of `check_document`'s combination (`ve.document.report`).
- `tools/relay_lint.py`: the senses-loader rule now reads every module of `ve/document/`. Before, it read the one
  file; reading fewer modules would have checked less. `tests/test_relay_lint.py::test_the_senses_path_is_read_by_the_third_rule`
  checks that it reads all of them (M16).
- `tools/identity_lint.py` `growth`: when the base lists `ve/x.py` and the head no longer has it, a site in
  `ve/x/*.py` counts as `ve/x.py`'s. The count per (module, domain, owner) still must not grow.
  `test_a_module_split_into_its_package_keeps_its_sites` covers five cases: a moved site, an added site, a package
  site beside the kept module, `ve/xy/`, and `ve/y/`. M15 covers it.
- `docs/test-architecture/binding-probes.jsonl.gz`: its recorded frame paths were renamed by `rename_probe_sites.py`,
  and the census was regenerated.
- The seeded-fault scripts of lean-first batches 16b to 16f (`84ae8a94`; `rename_seed_paths.py`,
  `evidence/seed-paths.json`): each fault's file becomes the module that holds its text exactly once (27 faults).
  Four faults in 16c and 16d whose text the base's `ve/document.py` no longer held were already stale before the
  split and keep their old name (a follow-up for their batches).
- Two tests that read the module's source: `test_one_selection_serves_both_python_paths` and
  `test_diagnostic_modules_stay_off_verdict_import_paths` (`84ae8a94`).

## Coordination

At the start, and again after syncing with `main` at `beb5c463` (lf-18, et-3b, et-7b and sc-3a had merged; none
touches `ve/document.py`), every branch in flight was checked with
`git diff --name-only main...<branch>` against this batch's 37 paths:

- `foundation/me-1`: `ve/assurance-manifest.json`. That branch's last commit is 2026-10-15. The manifest has a
  per-key merge rule ("a merge keeps each side's pins"), and this batch changes only the three `ve/document.py`
  keys.
- `infra/arch-20261019-1` (AR-17): `docs/test-architecture/binding-census.{json,md}`. These are generated
  (R12: not an overlap), and `regen_generated.py --resolve` rebuilds them.
- No other branch overlaps, and no branch in flight edits `ve/document.py`. AR-17 edits `ve/readings_route.py`,
  `readings_sup.py` and `readings_s1.py`; this batch does not touch them.

## DELTA

`DELTA.md`: none. The only rows are the 14 identical unavailable pairs (R7).

## Seeded bugs

`docs/arch/AR-16a/mutants.json`, run by `uv run python tools/mutants.py docs/arch/AR-16a/mutants.json --evidence
docs/arch/AR-16a/evidence/mutants.json`: 16/16 killed. Every one is Python: `ve/document/` and two tools. No Lean
or Rust product code changed.

| Id | File | Bug | Failing test |
|---|---|---|---|
| M1–M5 | `ve/document/load.py` | `_load` always takes the retained loader | `test_b16d_document.py::test_norm_defaults_readings_and_english_fence_are_decided_by_lean`, `::test_labeled_pending_pilot_is_lean_decided`, `test_document_lean_switch.py::test_coverage_and_statuses_are_leans`, `::test_owned_documents_are_decided_by_lean[plain]`, `::test_null_content_is_absent_on_the_lean_path` |
| M6 | `ve/document/load.py` | the retained loader runs twice | `test_document_lean_switch.py::test_undecided_answers_take_the_retained_path` (2 parameters fail; run as a command, because the harness's FAILED pattern stops at a space in a parameter ID) |
| M7–M9 | `ve/document/load.py` | the retained path's document id is cut | `test_b16e_rights_document.py::test_rights_corpus_sample_is_lean_decided_with_the_prior_outcome`, `test_b16f_document.py::test_the_layer_seeds_are_decided_by_lean_with_the_retained_public_outcome[soft-norms]`, `test_b16f_senses_document.py::test_a_valid_senses_document_is_decided_by_lean[d_parenthetical_switch-modern]` |
| M10 | `ve/document/lean.py` | a build failure of a Lean-accepted document escapes as VEError | `test_document_lean_switch.py::test_a_document_lean_accepted_that_python_cannot_build_is_unavailable` |
| M11 | `ve/document/report.py` | the admission route's rejection escapes | `::test_the_admission_route_rejecting_what_lean_admitted_is_unavailable` |
| M12 | `ve/document/report.py` | Python's narrowing checks always run | `::test_python_graph_checks_do_not_run_on_a_lean_admitted_document` |
| M13 | `ve/document/__init__.py` | a re-export dropped | `test_document_split.py::test_every_name_callers_import_is_the_owners_object[coverage_defaults]` |
| M14 | `ve/document/__main__.py` | `python -m ve.document` runs nothing | `test_document_split.py::test_python_m_ve_document_runs_the_command_line` |
| M15 | `tools/identity_lint.py` | a package site counts as the module's while the module remains | `test_identity_lint.py::test_a_module_split_into_its_package_keeps_its_sites` |
| M16 | `tools/relay_lint.py` | the senses-loader rule reads only `load.py` | `test_relay_lint.py::test_the_senses_path_is_read_by_the_third_rule` |

Each patch mutant (M1 to M12) fails only because the patch reaches the code. Take M1: had the patch stayed on
`ve.document`, the real retained loader would have run, given the expected result, and the mutant would have
survived.

## Tests run

- Selected tests (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`; the Mac runner yielded to a
  candidate gate, so it ran on the VM): see the result line in the build report. The selection is every unit
  (452/452). The cause is inherent to the move: the deleted module `ve/document.py` is in nearly every test's
  static import closure, and many tests list `ve/`.
- `tests/test_document_split.py`, `tests/test_assurance_manifest.py`, and the tests each mutant names: passed.
- Not run here, per the task: the full gate (`tools/gate.py`), which the chain runs on the final HEAD.

## Follow-ups (not in this batch)

1. `tools/mutants.py`: `FAILED = re.compile(r"^(?:FAILED|ERROR) (\S+?)...")` does not read a parametrized test ID
   that holds a space, so a mutant that kills such a test reads as surviving. M6 works around this with a command.
2. The raw import cycle now has 17 nodes (10 modules). It would shrink if the readings modules imported the
   submodule they use (`ve.document.source`, ...) rather than the package. That edits the readings modules, which
   AR-17 owns; AR-16b's territory.
3. Comments that still name `ve/document.py`: Lean docstrings (`lean/VE/Service/Document.lean`,
   `Attribution/*.lean`, `Discourse/Loader.lean`), `tools/lean_decided_share.py`, `research/defeasible/baseline.py`
   and `tests/frozen_speech/speech_document.py`. Lean is out of scope, and the rest are comments.
4. Four seeded faults in `docs/lean-first/b16c` and `b16d/seed_faults.py` name text the base no longer held
   (`evidence/seed-paths.json`, `stale_before_the_split`). They were stale before this batch.
5. The whole-UDHR pilot runs near the recorder's 600 s limit: 482 s to 797 s alone, more under load (L75).

## After the gate

The scope, the A/B and the gate must name the commit the chain gates (`<G>`). After the chain's gate of `<G>`,
make one report commit that changes only `docs/arch/AR-16a/`:

    cp gate-result.json docs/arch/AR-16a/evidence/gate.json
    uv run python -m tools.evidence scope --base main --head <G> --out docs/arch/AR-16a/evidence/scope.json
    gunzip -kf ~/.cache/ve-ar16a-ab/base.jsonl.gz ~/.cache/ve-ar16a-ab/head.jsonl.gz
    uv run python -m tools.evidence ab ~/.cache/ve-ar16a-ab/base.jsonl ~/.cache/ve-ar16a-ab/head.jsonl \
        --base-commit beb5c463026211d9e8be684884153565ca0026b9 --head-commit <G> \
        --out docs/arch/AR-16a/evidence/ab.json --delta docs/arch/AR-16a/evidence/ab-delta.json
    uv run python -m tools.evidence report docs/arch/AR-16a   # paste between the markers
    uv run python tools/batch_evidence.py --check docs/arch/AR-16a --report-commit HEAD

The head recording was made at `0016c3d9`. From there to `<G>`, `ve/`, `lean/`, `rust/`, `conformance/` and
`tools/lean_first_diff.py` are unchanged: `git diff --stat 0016c3d9 <G> -- ve lean rust conformance
tools/lean_first_diff.py` is empty, and the commits after it change only tests, `tools/` lints and
`docs/arch/AR-16a/`.

<!-- BEGIN GENERATED AR-16A NUMBERS -->
- Scope: `beb5c463..7256481b --no-merges`, 7 commits: `7256481b`, `8fb410f7`, `0a122dcf`, `6eba0d5f`, `84ae8a94`, `357efd11`, `7b44fdf4`.
- Corpus A/B (`beb5c463` against `7256481b`): 100428 records identical, 14 unavailable on both sides with identical outputs (R7, listed), 0 unlisted; pilots 595, document 3632, discourse 6350, rights 2500, readings 1137.
- Seeded mutants (tools/mutants.py): 16/16 killed.
<!-- END GENERATED AR-16A NUMBERS -->
