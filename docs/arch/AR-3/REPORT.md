# AR-3: test collection checked against the merge base

Plan: `docs/ARCHITECTURE-REVIEW-2026-10.md` on `design/arch-review`, section 4.3, row AR-3. Branch
`infra/arch-AR-3`, base `cbbab2df` (`evidence/scope.json`).

## What changed

- `tools/gate.py` no longer reads a committed list of test IDs. It takes the expected collection from the merge
  base with `main` (on `main` itself, the first parent; `--base REV` names another commit): the record a gate
  attached to that commit as the git note `refs/notes/ve-gate-collection`, or a parent's record when the parent
  has the same tree (a merge commit and the branch head it merged), or, with neither, a collection of the base in
  a scratch worktree, with the head's Lean build copied there and rebuilt, and the head's Rust binary when the
  base's `lean/checkers.lock` pins it (otherwise a reproducible Cargo build of the base). That collection is then
  attached as the base's record, so the next gate on the same base reads it.
- A base ID the head does not collect fails the gate unless `git diff --no-renames base..HEAD` deletes its file,
  deletes its test function or a class the ID names (read with `ast` on both sides), or changes its
  parametrisation: the decorators of the function and of its classes, the classes' bases, the module's
  `pytestmark` and `pytest_generate_tests`, the decorators of the module's fixtures the function takes, and every
  module-level statement those name, transitively. New IDs pass. Collection reports still fail the gate.
- Every full gate attaches its own clean collection to its commit (`head_record` in `gate-result.json`). A rerun
  of failed tests records nothing.
- One owner: the rule, the record and the base collection are in `tools/gate_collection.py`; `tools/gate.py`
  calls them and keeps the collection command both sides use (`collection_command`).
- Deleted: `tools/gate-collection.json` and its two writers (`tools/gate_collection.py --write`,
  `tools/gate.py --write-collection`). `tools/gate_collection.py --check` now runs the gate's comparison on the
  worktree. `tools/gate-optional.json` stays.

The deltas to the gate are listed in [DELTA.md](DELTA.md); one (G6, where the IDs are stored) needs a DRI
signature.

## Measured outcome

From `evidence/measure.json` (`measure.py`, run on the batch head with the base `cbbab2df`):

- Removed from the tree: `tools/gate-collection.json`, 14,129 lines (1,858,052 bytes, 14,127 IDs).
- Commits avoided: in the 14 days before the base, 285 commits on `main` (merges not counted) changed that file;
  none is needed now.
- The rule replayed over main's history: for each of the 66 first-parent commits in those 14 days that changed
  the file, its parent's IDs against its own, with the diff between them. 1,369 IDs were removed; the rule
  explains 1,360 and refuses 9, all in one merge (`24ea9e45`, lf-1): parameters of
  `tests/test_assurance_manifest.py::test_every_declared_response_field_is_enforced` read from
  `ve/assurance-manifest.json`, which is the case the plan's fixture says must fail (DELTA G3).
- The extra cost when the base has no record: one collection of the base in a scratch worktree took 86.2 s,
  and collected the 14,127 IDs of the baseline committed at the base, with no difference either way.

## Coordination

- Files touched (`evidence/scope.json`): `tools/gate.py`, `tools/gate_collection.py`,
  `tools/gate-collection.json` (deleted), `tests/test_gate_collection.py`, `tests/test_gate.py`,
  `tests/test_gate_integrity.py`, `tests/test_gate_rerun.py`, `tests/test_eff_tests_report.py` (it read the
  deleted file; it now reads the JUnit record saved with that batch's evidence), `README.md`, this directory and
  its test, `tests/test_ar3_report.py`.
- Overlap with branches in flight (`git diff --name-only main...<branch>` for `lean-first/*`,
  `readings-defaults/*`, `question-answering/*`, `infra/*`): `tools/gate.py` is also changed by
  `readings-defaults/rd6b` (the Lean build step); `git merge-tree` merges the two with no conflict in it.
  `docs/TESTING.md` is changed by `infra/ts-B1`, so it was left alone (its mentions of the deleted file are
  historical table rows). Every branch that changed `tools/gate-collection.json` gets a modify/delete conflict
  there.
- **Collision rule:** "modify/delete conflict on `tools/gate-collection.json`: take the deletion".
- The records are local refs, like the gate notes before them. Main's merge commits have the tree of the synced
  branch head they merge (true of the last eight), so when the full gate ran on that head, the next branch's gate
  finds the base's record through the same-tree parent. A missing record only costs one base collection.
- AR-3 changes a gate input (plan 4.2): the owner of the lead's "speed and efficiency" item should know that a
  gate on a base without a record collects the base once (about 1.5 minutes here, more when the branch changes
  many Lean modules, which the base's build must redo).

## Seeded bugs

Each was planted in the named file, its test failed, and the source was restored (`seed_faults.py`,
`evidence/mutants.json`). Only Python product code changed (`tools/`), so all are in Python.

| Bug | File | Test that fails |
|---|---|---|
| a deleted test file does not explain its tests | tools/gate_collection.py | test_the_diff_explains_a_deleted_or_reparametrised_test[deleted test file] |
| a deleted test function does not explain its tests | tools/gate_collection.py | test_the_diff_explains_a_deleted_or_reparametrised_test[deleted test function] |
| the parametrisation leaves out the module-level names its decorators use | tools/gate_collection.py | test_the_diff_explains_a_deleted_or_reparametrised_test[shrunk module list] |
| a change anywhere in the test file explains a dropped test | tools/gate_collection.py | test_a_module_dropped_at_collection_fails_twice[import error] |
| a record copied to another commit is used | tools/gate_collection.py | test_a_record_retyped_or_rebound_is_ignored[commit other] |
| the gate passes a base ID nothing explains | tools/gate.py | test_the_gate_fails_on_every_unexplained_missing_id_and_lists_the_explained |
| the gate collects the base even when it has a record | tools/gate.py | test_the_gate_takes_the_base_record_and_collects_only_without_one |
| a full gate does not record its collection | tools/gate.py | test_a_full_gate_records_its_tree_and_mode |

## Tests

- New and changed: `tests/test_gate_collection.py` (the plan's fixtures: a module that fails to import, a
  conftest that ignores a module, a parameter list that shrinks in an unchanged function, each failing; a
  deleted test function, file, class and a renamed file passing; the record retyped and rebound field by field;
  the merge base; the scratch worktree; the base's Rust binary), `tests/test_gate.py`,
  `tests/test_gate_integrity.py`, `tests/test_gate_rerun.py`, `tests/test_ar3_report.py` (this report against
  the saved evidence).
- Selected tests (`tools/select_tests.py --base <merge base> --run`): every selected file passed but two.
  `tests/test_rust_reproducible.py` failed on the new test's Cargo call, fixed in `3621ea4e`.
  `tools/test_layer_policy.py::test_documented_python_layers_match_policy` fails on `main` too: `ve/ask.py`
  (question answering) is missing from `docs/ARCHITECTURE-LAYERS.md`; AR-3 touches neither file, and the gate
  does not run `tools/`.
- The full gate runs once, on the final commit; its record is `gate-result.json` in the worktree.

## Checklist

Lines of `prompts/build-checklist.txt` that apply: 11 (the rule reads test modules with `ast`, never a regular
expression; Git is asked through its commands), 13 (seeded bugs above; an always-explain rule and a
never-explain rule each fail a test), 14 (temporary paths only; no waits; the base collection's environment is
the recorded pytest stage's with the base worktree first on `PYTHONPATH`), 16 (the expected collection is
generated, never kept by hand), 20 (every number above is checked by `tests/test_ar3_report.py` against the
saved evidence), 22 and 23 (above and DELTA.md). The rest concern VE's languages, wire and proofs, which AR-3
does not touch.

## Commits

- d98373a5 AR-3: the gate checks its collection against the merge base's, not a committed baseline
- 170211c1 AR-3: the base worktree gets a Rust binary its own lock pins
- 3621ea4e AR-3: the base Rust build test checks rust_build's flags
- da8f28dd AR-3: measurement, seeded faults and scope scripts with their saved evidence
