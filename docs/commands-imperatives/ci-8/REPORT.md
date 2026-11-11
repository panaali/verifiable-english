# ci-8 report: the generated `E_web` environment (CI-8, re-scoped)

Status: done; final HEAD is the commit that adds this report. No DELTA row and no signature are reserved for the DRI.
Changed: `lean/VE/Commands/WebEnvMain.lean` prints `E_web` and its lexicon. `tools/webapp_commands_env.py --write/--check`
is registered as `webapp-commands-env` in `GENERATED`. The committed `usecases/webapp-commands/environment.json` was written by `regen_generated.py --write`.
Open: the rest of CI-8 is paused by the DRI's re-scope. It is not built and not stubbed (see "Not in this item").
No commands coverage number is published. Commands are measured after the sprint.

Plan: `docs/spec/commands-imperatives-PLAN.md` on main: "CI-8" (lines 1130-1149), row (iv) (line 63) and section 9's
R12 row (line 1311). Re-scope: `reviews/dri-decisions-20261108-featureplan-asks.md` item 2 (manage-agents). Statement
gate: CI-2 has merged. The re-scope removes deliverables and adds none. No theorem statement is added or changed.

## Deliverables

| # | Task line | Delivered | Evidence |
|---|---|---|---|
| 1 | `lean/VE/Commands/WebEnvMain.lean` prints `VE.Commands.Examples.E_web` as JSON, as the profile table is printed | `main` prints `{"environment": E_web, "lexicon": lexJson E_web}` with `Json.pretty`, like `VE/Compose/ProfilesMain.lean` | db86472f9; `test_the_committed_environment_is_the_lean_generators_output` |
| 2 | `tools/webapp_commands_env.py --write` and `--check` | A copy of `tools/profile_table.py`'s shape. `--write` stores Lean's stdout. `--check` compares byte for byte. A printer failure is never a pass | db86472f9; `test_write_stores_exactly_what_lean_printed`, `test_check_refuses_any_other_file_and_a_failed_printer` |
| 3 | `Generated("webapp-commands-env", ("usecases/webapp-commands/environment.json",), ...)` with a `fresh=` test | The entry sits after `profile-table`, with `fresh="tests/test_webapp_commands_env.py::test_the_committed_environment_is_the_lean_generators_output"` | db86472f9; `test_regen_generated_owns_the_file_through_this_generator`, `tests/test_regen_generated.py` (all pass) |
| 4 | `usecases/webapp-commands/environment.json`, written only by `regen_generated.py --write` | Written by `uv run python tools/regen_generated.py --write` (40 entries, rc 0, 5m09s). That run also regenerated `.gitattributes`, the codemap and the inventories | b1bed8978 |
| 5 | Layers for the new files in `tools/layer_policy.py` if needed | `VE.Commands.WebEnvMain` is layer 4. The `VE.Commands.*` prefix would place it at layer 3, below the layer-4 `RunExamples` it imports. `tools/check_lean_imports.py`'s `RUN_ONLY` names it, because no default target builds it (like `ProfilesMain`). `tools/trust-classes.json` classifies `main` as T. `ve/assurance-manifest.json`'s `other_json` gives the print entry a reason, as it does for `ProfilesMain`, and `docs/merge-tooling.md` lists the entry | db86472f9, 5e1e5d554, the manifest commit; `tests/test_lean_default_build.py` (passes) |

### Not in this item (paused by the re-scope; not built, not stubbed)

These are not built: `usecases/webapp-commands/segments.json`, `harness.py`, `evidence/coverage.json`, the tutorial census,
`usecases/webapp-commands/REPORT.md` and `docs/spec/commands-imperatives-report.md`. No commands coverage number is
published. It is measured after the sprint. If the DRI renews it, this work is the rest of CI-8.

## Decisions taken inside the scope

- **The file carries the lexicon as well as `E_web`.** It has two fields, `environment` (`E_web` as Lean defines it)
  and `lexicon` (`VE.Commands.RunExamples.lexJson E_web`). Those are the two fields an `english.command` request
  carries besides its wording. A later harness therefore builds neither of them in Python, which keeps one owner.
  The task's seeded bug "the Lean print drops the lexicon" assumes this shape. `lexJson` is reused, not copied.
- **The freshness test reads Lean twice.** It runs the generator's `--check`, unmocked. It also runs
  `lake env lean --run VE/Commands/WebEnvMain.lean` itself and compares the output with the committed file. If the
  generator kept a hand copy, its own `--check` would compare the copy with itself and pass. The direct comparison
  is what catches that case (seeded bug 3).

## Seeded bugs (docs/commands-imperatives/ci-8/mutants.json)

Each bug was planted in the working tree, shown with the named test, then restored with `git checkout`.

| # | Language, file | Bug | Failing test |
|---|---|---|---|
| 1 | Lean, `lean/VE/Commands/WebEnvMain.lean` | the print drops the lexicon | `test_the_committed_environment_is_the_lean_generators_output` (1 failed: "environment.json is stale") |
| 2 | Python, `tools/webapp_commands_env.py` | `--check` compares only the top-level keys, so one sort removed passes | `test_check_refuses_any_other_file_and_a_failed_printer` (1 failed) |
| 3 | Python, `tools/webapp_commands_env.py` | the generator uses a hand-kept copy. `E_web`'s task was also edited in `Examples.lean` and `VE.Commands.RunExamples` rebuilt | `test_the_committed_environment_is_the_lean_generators_output` and `test_write_stores_exactly_what_lean_printed` (2 failed; the generator's own `--check` passed) |

Rust: unchanged.

## Trust

`uv run python tools/trust_map.py --check` (after 5e1e5d554) printed `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0` and `PASS`.
No trusted Lean was added, so there is no R16 row, no allowance and no FOLLOW-UPS ties row. The light lane
(`light-lane.py check`) prints NOT. Its reasons are that `WebEnvMain.lean` is not in the base's side table and that
the item touches trust-table and generated files. No `trust_mutants` sweep was run, because the item adds no trusted
definition for it to mutate (trust_map +0). Neither the task nor checklist 13a asks for one without R16 growth.

## Size

SIZE: 64 product, 96 tests, 155 other hand-written lines. Product: WebEnvMain 10, the generator 40, `regen_generated` 5,
`layer_policy` 2, `check_lean_imports` 1, `trust-classes.json` 5, the assurance manifest 1. Other: `docs/merge-tooling.md` 1
and this directory (`DELTA.md`, `mutants.json`, this report). Counted with `git diff --numstat $(git merge-base HEAD main)`.
Generated and excluded: `environment.json` (140 lines), `.gitattributes`, `docs/codemap/*`, `lean/declarations.txt` and `lean/predicates.txt`.

Pilot bytes: none expected to move. The item adds a generated file and changes no reader.

## Checks run

- `lake build`: rc 0, 1391 jobs. `python3 lean/audit.py`: PASS, 847 source files.
- `uv run pytest -q tests/test_lean_default_build.py tests/test_regen_generated.py tests/test_webapp_commands_env.py tests/test_repo_map.py`:
  105 passed.
- `uv run python tools/gate_collection.py --check --prebuilt`: 5 added, 0 refused, 0 stale, 0 malformed.
- `tools/select_tests.py --base $(git merge-base HEAD main)`: 517/589 units, including `tests/test_webapp_commands_env.py`.
- Final selected run (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select`, started on committed 65009777a; it ran locally on the VM
  because the Mac was unreachable): exit 1. It recorded 517 units, and 2 tests failed:
  `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` (the new print entry had no
  `other_json` reason) and `tests/test_merge_tooling_evidence.py::test_the_generated_file_table_names_every_entry`
  (`docs/merge-tooling.md` had no row for the new entry). Both are fixed in the commit after 65009777a. A rerun of
  only those two ids (`mac-pytest.sh -- <ids>`) gave 2 passed. Neither test is on main's known-red list.
- Not run: the full gate (the chain runs it) and a `trust_mutants` sweep (see Trust).

## Spec re-read

- "`environment.json` (`E_web`), **generated** from `VE.Commands.Examples.E_web`" against PLAN:1136. The file's
  `environment` is `E_web` exactly, and `test_the_file_is_the_environment_and_its_lexicon` pins its sorts, task and addressee.
- "`WebEnvMain.lean` prints it, as `VE/Compose/ProfilesMain.lean` prints the profile table" against PLAN:1137. The
  print uses the same `IO.println (… ).pretty` and the same `lake env lean --run`.
- "`tools/webapp_commands_env.py --write` and `--check` … registered in `tools/regen_generated.py`" against PLAN:1138-1139.
- "never written by hand" against PLAN:1139 and row (iv) at PLAN:63 ("not a hand copy with an equality test"). The
  committed file is checked against Lean's own print. No Python copy exists, and seeded bug 3 shows that a copy fails.
- Section 9 R12 row (PLAN:1311): generated files go through `regen_generated` and are never hand-edited or counted as overlaps. `DELTA.md` records this.

## Notes for the DRI

- `lexJson` lives in `VE.Commands.RunExamples`, a fixture module. The print imports it rather than copying it. A later
  item that wants the lexicon owner outside a fixtures module could move `lexJson` without changing this file's bytes.
- The first selected run was killed by the tool's 10-minute background limit, so the "failed last time" list in
  the rerun's order line names tests that were interrupted, not tests that failed.

## Next item

ci-4 (after ci-3) and ci-6 (after ci-3 and ci-e1). If the DRI renews it, the rest of CI-8 (harness, census, report) comes after the sprint.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. The item relays no Lean answer. The file is a generated table that no product code reads yet.
2. Deliverables built, no rule broken: PASS. The Deliverables table maps each task line to a commit and a test. No Python copy of `E_web` exists (seeded bug 3, `test_the_committed_environment_is_the_lean_generators_output`).
3. Tests can fail: PASS. Seeded bugs 1-3 (`mutants.json`). Each test is shown failing. No R16 growth.
4. Py/Lean/Rust agree: N.A. The item makes no verdict path change.
5. R8 binding: N.A. There is no relayed field.
6. Gate evidence matches HEAD: PASS. The selected run on 65009777a had 2 failures, both fixed. Those ids were rerun on the fix commit (2 passed). The chain runs the full gate on the final HEAD. The commit list comes from `main..HEAD --no-merges`.
7. No unsigned item: PASS. `DELTA.md` has no rows and reserves nothing. Trust is +0 (`tools/trust_map.py --check`).
8. Every user-visible change in DELTA: PASS. A new generated file is the only change, and no verdict changes. `test_regen_generated_owns_the_file_through_this_generator` covers the registration.
9. Test selection finds the tests: PASS. `select_tests.py` selects `tests/test_webapp_commands_env.py` (517/589 units, mostly because of the `layer_policy`/`regen_generated` edits).
10. Lean statements: N.A. No theorem is added.
11. Budgets fail closed: N.A. There is no evaluator or budget. Tests wait with `HANG_TIMEOUT` (`tests/test_webapp_commands_env.py`).
12. No CPU or memory regression: N.A. There is no runtime path. The print takes 1.5 s (`time uv run python tools/webapp_commands_env.py --check`).
13. Test-removed trailers: PASS. `tools/gate_collection.py --check --prebuilt` reports 0 removed, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. `test_check_refuses_any_other_file_and_a_failed_printer` passes the true file and refuses a sort removed, the lexicon dropped, a missing file and a failed printer. Claims cite commands above. The spec re-read is above.
15. Overclaim / silent cut / checks can fail / limits: PASS. The paused deliverables are listed as not built, and the cut is the DRI's re-scope. Every new check has a seeded bug. Limits are N.A. (no evaluator).
