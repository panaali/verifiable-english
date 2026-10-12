# AR-3: test collection checked against the merge base

Plan: `docs/ARCHITECTURE-REVIEW-2026-10.md` on `design/arch-review` (draft 2), section 4.3, row AR-3. Branch
`infra/arch-AR-3`, base `7478b23d` (main, merged in at `27655d64`) (`evidence/scope.json`).

## What changed

- `tools/gate.py` no longer reads a committed list of test IDs. It takes the expected collection from the merge
  base with `main` (on `main` itself, the first parent; `--base REV` names another commit). The source is, in
  order: the record a gate attached to that commit as the git note `refs/notes/ve-gate-collection`; or a
  parent's record when the parent has the same tree (a merge commit and the branch head it merged); or, with
  neither, a collection of the base in a scratch worktree. That worktree gets the head's Lean build copied in
  and rebuilt, and the head's Rust binary when the base's `lean/checkers.lock` pins it (otherwise a
  reproducible Cargo build of the base). The collection is then attached as the base's record, so the next gate
  on the same base reads it.
- **Removal records.** A base ID the head does not collect fails the gate unless a commit in `base..HEAD` carries
  the trailer `Test-removed: <target> — <reason>`. The target is the ID, or the function, class or file whose IDs
  it covers. Git parses the trailers. A trailer whose target covers an ID the head still collects fails as stale,
  and a trailer without a target and a reason fails as malformed. New IDs pass. Collection reports still fail the
  gate, and `tools/gate-optional.json` stays.
- **The `ast` rule only labels.** `git diff --no-renames base..HEAD` labels each removal in the gate's report:
  its file is deleted, or its test function or a class the ID names is deleted (read with `ast` on both sides),
  or its parametrisation changed, or none of these. It never authorises a removal. The parametrisation is the
  decorators of the function and of its classes, the classes' bases, the module's `pytestmark` and
  `pytest_generate_tests`, the decorators of the module's fixtures the function takes, and every module-level
  statement those name, transitively. The failure lists each refused ID with its label and suggests one trailer
  per deleted file, class or function (one per ID otherwise).
- `gate-result.json`'s `collection` object holds the base, the record's source, the counts, `removed` (each ID
  with its label, the trailer's reason and commit), `refused` (each with its label), `stale` and `malformed`.
- Every full gate attaches its own clean collection to its commit (`head_record`). A rerun of failed tests
  records nothing.
- One owner: the rule, the trailers, the record and the base collection are in `tools/gate_collection.py`.
  `tools/gate.py` calls them and keeps the collection command both sides use (`collection_command`).
- Deleted: `tools/gate-collection.json` and its two writers (`tools/gate_collection.py --write`,
  `tools/gate.py --write-collection`). `tools/gate_collection.py --check` now runs the gate's comparison on the
  worktree, with the trailers up to `HEAD`.
- `tools/regen_generated.py` (on `main` since this batch's first base) listed the file as a generated inventory
  with that writer. The merge commit `27655d64` removes the entry and `tools/gate.py`'s exemption, regenerates
  `.gitattributes`, drops the row of `docs/merge-tooling.md`, and adds `RETIRED`: `--resolve` settles a
  conflict on a retired generated file by taking the deletion, so the merge train applies the collision rule
  below without an agent (`tests/test_regen_generated.py::test_resolve_takes_the_deletion_of_a_retired_file`).
- This batch's own removals: 12 base IDs (the baseline's guard and report tests, a renamed collector and a
  renamed expected reason). `73a9e30d` records them, each with its reason; the removing commits came before the
  rule. `723764dc` records the tests it replaced itself.

The deltas to the gate are listed in [DELTA.md](DELTA.md); one (G6, where the IDs are stored) needs a DRI
signature.

## Measured outcome

From `evidence/measure.json` (`measure.py`, run on the batch head with the base `7478b23d`):

- Removed from the tree: `tools/gate-collection.json`, 14,250 lines (1,870,144 bytes, 14,248 IDs).
- Commits avoided: in the 14 days before the base, 292 commits on `main` (merges not counted) changed that file;
  none is needed now.
- The rule replayed over main's history: for each of the 68 first-parent commits in those 14 days that changed
  the file, its parent's IDs against its own, with the diff between them. No commit then carried a removal
  record, so every removed ID would have been refused until one was added. 1,369 IDs were removed, in 20
  of the 68 commits. The diff labels 1,360 of them; 9 are unlabelled, all in one merge (`24ea9e45`, lf-1):
  parameters of `tests/test_assurance_manifest.py::test_every_declared_response_field_is_enforced` read from
  `ve/assurance-manifest.json`.
- The cost of the records: the trailers the gate's failure suggests come to 1,035 for those 1,369 IDs. 901 of
  them are lf-1's (1,149 IDs, mostly test functions re-parametrised in place, whose IDs need a trailer each,
  since a function-level trailer would be stale). The other 19 commits need 134. See the follow-up below.
- The extra cost when the base has no record: one collection of the base in a scratch worktree took 120.6 s
  (load average near 110), and collected the 14,248 IDs of the baseline committed at the base, with no
  difference either way.

## Coordination

- Files touched (`evidence/scope.json`): `tools/gate.py`, `tools/gate_collection.py`,
  `tools/gate-collection.json` (deleted), `tools/regen_generated.py`, `tests/test_regen_generated.py`,
  `.gitattributes`, `docs/merge-tooling.md`, `tests/test_gate_collection.py`, `tests/test_gate.py`,
  `tests/test_gate_integrity.py`, `tests/test_gate_rerun.py`, `tests/test_eff_tests_report.py` (it read the
  deleted file; it now reads the JUnit record saved with that batch's evidence), `README.md`, this directory and
  its test, `tests/test_ar3_report.py`.
- Overlap with branches in flight (`git diff --name-only main...<branch>` for `lean-first/*`,
  `readings-defaults/*`, `question-answering/*`, `infra/*`, rechecked on the final code):
  - `tools/gate.py` is also changed by `infra/ts-B5`.
  - `tools/regen_generated.py` is also changed by `infra/arch-AR-1`, `infra/arch-AR-8`, `infra/arch-20261010-1`
    and `infra/arch-20261010-2`. AR-1 and `arch-20261010-1` also change `tests/test_regen_generated.py`, and
    those two and AR-8 change `.gitattributes` and `docs/merge-tooling.md`.
  - `git merge-tree` merges each of these branches, and current `main` (AR-6 merged), with no conflict in those
    files.
  - Rechecked on 2026-10-12 against `main` at `5479466f`: `main` still merges with no conflict but the one below.
    Two newer branches overlap. `infra/oom-rootcause` changes `tests/test_gate_integrity.py` and merges without
    conflict. `infra/eff-20261011-1` changes `tools/regen_generated.py` (no conflict) and
    `tests/test_regen_generated.py`, where both branches append tests at the end of the file: keep both.
    `infra/arch-AR-8` no longer overlaps.
  - `docs/TESTING.md` is changed by `infra/ts-B1`, so it was left alone (its mentions of the deleted file are
    historical table rows).
  - Every branch that changed `tools/gate-collection.json` gets a modify/delete conflict there; DRI-RULINGS R12
    says such generated files are no overlap.
- **Collision rule:** "modify/delete conflict on `tools/gate-collection.json`: take the deletion", which
  `tools/regen_generated.py --resolve` applies once this batch has merged (its `RETIRED` list). Until then, a
  merge into a branch takes the deletion by hand (`git rm tools/gate-collection.json`); never regenerate it
  (R12).
- The records are local refs, like the gate notes before them. Main's merge commits have the tree of the synced
  branch head they merge, so when the full gate ran on that head, the next branch's gate finds the base's record
  through the same-tree parent. A missing record only costs one base collection.
- AR-3 changes a gate input (plan 4.2). The owner of the lead's "speed and efficiency" item should know two
  things. A gate on a base without a record collects the base once (about two minutes here, more when the
  branch changes many Lean modules, which the base's build must redo). And every lost test ID now needs a
  reviewed trailer before the gate passes.

## Follow-up (for the DRI)

- The trailer count for re-parametrised functions (901 of 1,035 in the replay, one merge). The plan allows one
  trailer per deleted function or file. A function whose parameters are renamed in place keeps being collected,
  so its lost IDs need a trailer each. A form such as "every ID of `<function>` the head no longer collects" would
  cut lf-1's 901 to about the number of functions. It widens what one trailer authorises, so it is left to the
  DRI and not built here.

## Seeded bugs

Each was planted in the named file, its test failed, and the source was restored (`seed_faults.py`,
`evidence/mutants.json`). Only Python product code changed (`tools/`), so all are in Python. The test column
names the test function in `tests/test_gate_collection.py` unless it names its file.

| Bug | File | Test that fails |
|---|---|---|
| the diff's deletion of a function authorises its removal without a trailer | tools/gate_collection.py | test_a_dropped_test_fails_without_a_trailer_and_passes_with_one[deleted test function] |
| a trailer covers any ID that starts with its target | tools/gate_collection.py | test_what_a_trailer_covers[tests/a.py::test_f] |
| a trailer naming a test the head still collects is not stale | tools/gate_collection.py | test_a_trailer_naming_a_collected_test_is_stale[its file] |
| a trailer without a reason records a removal | tools/gate_collection.py | test_a_trailer_is_a_target_and_a_reason[no reason] |
| trailers before the base count | tools/gate_collection.py | test_git_reads_the_trailers_of_base_to_head_only |
| a deleted test function is not labelled | tools/gate_collection.py | test_a_dropped_test_fails_without_a_trailer_and_passes_with_one[deleted test function] |
| the parametrisation leaves out the module-level names its decorators use | tools/gate_collection.py | test_a_dropped_test_fails_without_a_trailer_and_passes_with_one[shrunk module list] |
| a record copied to another commit is used | tools/gate_collection.py | test_a_record_retyped_or_rebound_is_ignored[commit other] |
| the gate passes a base ID no trailer names | tools/gate.py | test_the_gate_fails_on_every_missing_id_no_trailer_names_and_lists_the_recorded |
| the gate passes a stale trailer | tools/gate.py | test_a_stale_or_malformed_trailer_fails_the_gate[stale] |
| the gate collects the base even when it has a record | tools/gate.py | test_the_gate_takes_the_base_record_and_collects_only_without_one |
| a merge stops on a conflict over the retired baseline | tools/regen_generated.py | test_resolve_takes_the_deletion_of_a_retired_file |
| a full gate does not record its collection | tools/gate.py | test_a_full_gate_records_its_tree_and_mode |

## Tests

- New and changed: `tests/test_gate_collection.py`, `tests/test_gate.py`, `tests/test_gate_integrity.py`,
  `tests/test_gate_rerun.py`, and `tests/test_ar3_report.py` (this report against the saved evidence).
  `tests/test_gate_collection.py` holds the plan's fixtures:
  - each fails without a trailer: a module that fails to import or is skipped; a conftest that ignores a module;
    a parameter list that shrinks in an unchanged function (from a data file or an imported module);
  - a deleted test function, file, class, parametrised function and a renamed file fail without a trailer and
    pass with one;
  - a trailer naming a still-collected ID, file, class or function fails as stale; a malformed trailer fails;
  - what a target covers, at its boundaries; git's reading of the trailers of `base..head` only;
  - the record retyped and rebound field by field; the merge base; the scratch worktree; the base's Rust binary.
- `tools/gate_collection.py --check --prebuilt` on the final code (`evidence/check.txt`): 14,327 collected,
  14,248 at the base, 91 added, 12 removed by a trailer, none refused, stale or malformed.
- Selected tests (`tools/select_tests.py --base <merge base> --run`), before the merge with `main`: every
  selected file passed but two. `tests/test_rust_reproducible.py` failed on the new test's Cargo call, fixed in
  `3621ea4e`.
  `tools/test_layer_policy.py::test_documented_python_layers_match_policy` fails on `main` too: `ve/ask.py`
  (question answering) is missing from `docs/ARCHITECTURE-LAYERS.md`. AR-3 touches neither file, and the gate
  does not run `tools/`.
- Since the merge, `.gitattributes` differs from the base, so the selector selects the whole suite; the full
  gate runs that suite. The changed files were run directly on the final code, and passed:
  `tests/test_gate_collection.py`, `test_gate.py`, `test_gate_integrity.py`, `test_gate_rerun.py`,
  `test_regen_generated.py`, `test_eff_tests_report.py` and `test_ar3_report.py`.
- The full gate on the final code, `aff7a4c2` (`evidence/gate-full.json`, `--workers 8`, load 70 to 110 on 32
  CPUs): Lean build and audit, Rust build and its 36 native tests, then 14,233 passed, 92 skipped (all allowed)
  and 1 failed. Its collection matches `evidence/check.txt`: the base's record, 14,327 collected, 91 added, 12
  removed by a trailer, none refused, stale or malformed; it wrote the head's record. The failure was
  `tests/test_lean_conformance.py::test_lean_transitive_axiom_allowlist`: `lean/audit.py` hit its 1,800 s
  limit (the gate's own Lean audit stage passed). AR-3 changes no Lean.
- `tools/gate.py --rerun-failed` on the same commit (`evidence/gate-rerun.json`): `rerun-passed`, the 87 tests
  of that file passed, the failed one among them. Under R13 the gate counts as passed. This is the test's
  third retry this week (lf-13b-loopfix2 and ts-B5 on 2026-10-10); the ts-B5 review already put it on the
  load-sensitive list, so no new follow-up.
- Earlier attempts on `aff7a4c2` were stopped before they finished: by the shell's one-hour and two-hour
  limits, and one stale run that was killed. None of them wrote a result. The commit that saves the two records
  and this text changes no code, and is not in the commit list below, which is the saved scope.

## Checklist

Lines of `prompts/build-checklist.txt` that apply:

- 4: the record is fully typed and bound to its commit and tree, retyped and rebound field by field. A trailer
  is bound to the request: its target must cover an ID the base had and the head lacks, or it is stale when the
  head collects one.
- 11: test modules are read with `ast`, and trailers by git's own trailer parser, never a regular expression.
- 13: the seeded bugs above.
- 14: temporary paths only, and no waits. The base collection's environment is the recorded pytest stage's,
  with the base worktree first on `PYTHONPATH`.
- 16: the expected collection is generated, never kept by hand.
- 20: every number above is checked by `tests/test_ar3_report.py` against the saved evidence.
- 22 and 23: above and DELTA.md.

The rest concern VE's languages, wire and proofs, which AR-3 does not touch.

## Commits

- d98373a5 AR-3: the gate checks its collection against the merge base's, not a committed baseline
- 170211c1 AR-3: the base worktree gets a Rust binary its own lock pins
- 3621ea4e AR-3: the base Rust build test checks rust_build's flags
- da8f28dd AR-3: measurement, seeded faults and scope scripts with their saved evidence
- 3f78b873 AR-3: report, DELTA and the report's test over the saved evidence
- a3a52b67 AR-3: measurement and seeded faults again at the new merge base, with the retired-file fault
- 3e958d25 AR-3: report and DELTA at the new merge base; the retired-file resolution (G7)
- 723764dc AR-3: a lost test ID needs a Test-removed trailer; the diff only labels it
- 73a9e30d AR-3: removal records for the base tests this batch replaced
- b694bafc AR-3: measurement and seeded faults for the removal records
