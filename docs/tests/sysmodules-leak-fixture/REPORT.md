# sysmodules-leak-fixture: a use case's harness modules stay with the test module that imported them

Status: built; waiting for the chain gate. Branch feature/sysmodules-leak-fixture; the final HEAD is the commit that adds this report's last edit.
Changed: `tests/conftest.py` (a collection hookwrapper, a module-scoped autouse fixture and two helpers) and two new test modules, `tests/test_sysmodules_leak_a.py` and `tests/test_sysmodules_leak_b.py`.
Open items: none. DRI signature needed: none (DELTA: none; trust +0).
Speed: no measurable slowdown. The fixture's own cost is about 0.06 s per pytest process (details under (2)).

SIZE: 72 product (test-harness conftest), 70 tests, 0 other hand-written lines (excluding this report and the mutants record). Source: `git diff --numstat $(git merge-base HEAD main)` gave
`72 tests/conftest.py`, `34 tests/test_sysmodules_leak_a.py`, `36 tests/test_sysmodules_leak_b.py` before the docs commit.
Light lane: `python3 -I .../light-lane.py check` printed `LIGHT 142 changed lines outside generated files <= 150 (3 files), no trusted-core file, against 4142e7e5`, so there was no trust_mutants sweep.

Base: the task was planned at main 20cf38f5422e. The branch starts at main 4142e7e59f, which also contains kb-10d-nightly-fix (`tools/ownership_trace.py` `_load`). kb-10d's fix is unchanged here.

## Deliverables

| # | Task line | Commit | Evidence |
|---|---|---|---|
| 1 | Failing-first pair (A then B, one process), committed before the fix, with a lazy-import case | f43ce85a3d | (1) below |
| 2 | Hookwrapper + module-scoped autouse fixture in tests/conftest.py, restricted to harness modules; suite time before/after | a8182aab29, 337158a644 | (2) below |
| 3 | Selected run; one `-p no:xdist` process over every test file that inserts a usecases/ dir, plus tests/test_ownership_floor.py | (no test change needed) | (3) below |
| 4 | Seeded bugs (i) no restore, (ii) restore too much, (iii) drop a package module | (planted and restored) | `seeded-mutants.json`, Seeded bugs below |

### (1) Fail-first

Module A (`tests/test_sysmodules_leak_a.py`) puts `usecases/eligibility` on `sys.path` and imports `run` and `translation` by bare name
at module level, as `tests/test_eligibility_wfp.py:21-25` does. Its tests assert two things:
- `sys.modules["translation"] is translation is run.T`, and the directory is on `sys.path`.
- `run.fixture_model(...)` runs, and its call-time `import reference as R` (`usecases/eligibility/run.py:287`) resolves to
  `usecases/eligibility/reference.py`. This is the lazy-sibling case (b).

Module B (`tests/test_sysmodules_leak_b.py`) asserts that `translation`, `run` and `reference` in `sys.modules` are not A's (absent, or
`__file__` outside A's use-case dir) and that A's dir is not on `sys.path`. It also has the package guard: every submodule that
`ve`, `ve.backends` or `tools` holds as an attribute is still that entry of `sys.modules`.

At f43ce85a3d (tests only; `tests/conftest.py` as on main 4142e7e59f):
`uv run pytest -q -p no:xdist tests/test_sysmodules_leak_a.py tests/test_sysmodules_leak_b.py` gave exit=1 (`/tmp/smleak-failfirst.log`):
`FAILED tests/test_sysmodules_leak_b.py::test_module_a_left_no_harness_module_and_no_use_case_directory`,
`AssertionError: translation is still module A's <module 'translation' from '.../usecases/eligibility/translation.py'>`,
`1 failed, 3 passed`.

After the fix, at 337158a644, the same command gave exit=0 with `4 passed`. The reverse order
(`... tests/test_sysmodules_leak_b.py tests/test_sysmodules_leak_a.py`) also gave exit=0 with `4 passed` (`/tmp/smleak-reverse.log`).

### (2) Fix

All new code is in `tests/conftest.py`, after the existing fixtures. No listed region is edited. The only other change is one added
import line, `from contextlib import contextmanager`.

- `_harness_scope(key)` is a context manager. On entry it puts back the harness `sys.path` entries and modules recorded for `key`.
  On exit it records the harness entries added inside the scope, removes the added harness `sys.path` entries, and gives every
  harness name its value from before the scope: an earlier entry is put back, and a name the scope first added is removed.
- `pytest_make_collect_report` hookwrapper. `Module.collect()` imports the test module, so collection of a module (and of its
  classes) runs inside `_harness_scope(module.path)`. Doing it here, rather than in `pytest_pycollect_makemodule`, is
  required: that hook only builds the node, and the import comes later.
- `harness_modules_stay_with_their_test_module` is a module-scoped autouse fixture. The module's tests run inside the same
  `_harness_scope(module.path)`, so A's own modules and directory are in place for its tests (and its lazy sibling imports)
  and are taken out at module teardown. Under xdist, a worker that runs a module again re-enters the scope, and the scope works
  the same way.
- A harness module is a bare-named module (no dot) that is not a package (no `__path__`) and has a `__file__`. Its directory must
  not be one of the shared directories (ROOT, `tests/`, `tools/`, `lean/`) and must not be under `sys.prefix`, `sys.base_prefix`
  or `sys.exec_prefix` (stdlib, the venv and its site-packages). So `ve.*`, `tools.*`, the test modules, `subprocesses` and every
  installed package are never dropped. A harness `sys.path` entry is an added entry whose directory is outside those same
  shared and system directories. Added shared entries, such as `tools/`, are left as they were before this item.
- The rule names no directory in a string except the generic words `tests`, `tools` and `lean` (`GENERIC_DIRECTORIES` in `tools/source_graph.py`). `tools/source_graph.py` reads the string constants of `tests/conftest.py` as paths, and
  that file is in every test's closure. My first version had `Path(entry or ".")` and `ROOT / "usecases"`. The `"."` named every
  file, which broke two `tests/test_select_tests.py` checks (see Notes). Because the rule is directory-based rather than
  usecases-based, it also catches a use-case module whose directory already left `sys.path` before the scope ended
  (`tests/test_pf_fidelity_fix.py` `_load` and kb-10d's `_load` remove their directories).

Suite time, measured over the 20 files listed in (3) (every file that inserts a usecases/ dir, with A) plus B, in one process,
`zsh mac-pytest.sh -- -q -p no:xdist <files>`, on the VM (the runner chose the VM both times, at VM load about 29):
- Before (main's conftest, 4142e7e59f): `1 failed, 1161 passed, 7 deselected in 5080.38s` (`/tmp/smleak-oneproc-before.log`; the
  one failure is B, as expected).
- After (337158a644): `1162 passed, 7 deselected in 4253.07s` (`/tmp/smleak-oneproc-after.log`).
- The 16% difference in favour of the fix is VM noise; it is not a speed-up. So the fixture's own cost was measured directly.
  A throwaway `-p` probe plugin (`/tmp/smleak-probe/smleak_probe.py`, not committed) timed `_harness_scope` over the same
  collection: `scopes=21 bookkeeping=0.029s recorded_modules=40 distinct_names=21` (`/tmp/smleak-probe-collect.log`).
  `-X importtime` gave the self time of the second and later copies of re-imported harness modules (agent-policy's `check`,
  `focused`, `mutants` and `environments`, imported by 4 test modules each, and others): `26513` µs (`/tmp/smleak-importtime.log`).
  That totals about 0.06 s per process, under 0.01% of either run, so it is well under the 2% threshold.
- `--collect-only` wall time, 3 runs each (`/tmp/smleak-collect-{main,fixed}-{1,2,3}.log`): main 7.04/6.55/6.26 s and fixed
  7.25/11.97/9.85 s. The spread is VM load (the probe above is the cost measure); it is reported here for completeness.

### (3) Existing-suite check

One process: `zsh mac-pytest.sh -- -q -p no:xdist <the 20 files> tests/test_sysmodules_leak_b.py` at 337158a644 gave exit=0 with
`1162 passed, 7 deselected in 4253.07s` (`/tmp/smleak-oneproc-after.log`). The files come from `git grep -l 'sys.path.insert' -- 'tests/test_*.py'`
intersected with files naming `usecases`; tests/test_ownership_floor.py is one of them. All tests passed in every file
(per-file counts from `--collect-only`, `/tmp/smleak-collect-fixed-1.log`):

| File | Tests | Result |
|---|---|---|
| tests/test_agent_policy.py | 115 | passed |
| tests/test_agent_policy_replay_decode.py | 8 | passed |
| tests/test_agent_policy_rerun.py | 4 | passed |
| tests/test_agent_policy_unspecified.py | 9 | passed |
| tests/test_asimov_extended.py | 17 | passed |
| tests/test_assurance_manifest.py | 167 | passed |
| tests/test_b16f_senses_document.py | 64 | passed |
| tests/test_eligibility_wfp.py | 82 | passed |
| tests/test_english_e2_responses.py | 95 | passed |
| tests/test_english_statement_blocks.py | 9 | passed |
| tests/test_et8_completion.py | 5 | passed |
| tests/test_kb9_selected_facts.py | 54 | passed |
| tests/test_ownership_floor.py | 25 | passed |
| tests/test_pf_fidelity_fix.py | 63 | passed |
| tests/test_readings_rd5_udhr.py | 5 | passed |
| tests/test_safety_framework.py | 46 | passed |
| tests/test_safetyfw_usecases.py | 105 | passed |
| tests/test_select_tests.py | 260 | passed |
| tests/test_senses_packs.py | 25 | passed |
| tests/test_sysmodules_leak_a.py | 2 | passed |
| tests/test_sysmodules_leak_b.py | 2 | passed |

No existing test had passed only because of a leaked module, so no test's own import needed a fix.

Selected run: `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` at d6fa3a1683 (clean tree; it ran
locally on the VM) gave exit=0. The plan was `648/648 test units ... FULL: tests/conftest.py`, and the run `recorded 648 units for tree
17347e22e7; 0 others left to the static graph until they run; 0 failed` (`/tmp/smleak-select.log`). After it, only this report and one comment in `tests/conftest.py` changed (b344cf437f and the final commit; no code line).

## Seeded bugs (Python; tests/conftest.py is the only changed file with code)

Each bug was planted in `tests/conftest.py` and run with
`uv run pytest -q -p no:xdist tests/test_sysmodules_leak_a.py tests/test_sysmodules_leak_b.py`, then restored with `git checkout`.
The three are committed, with file and test keys, in `docs/tests/sysmodules-leak-fixture/seeded-mutants.json`.

1. (i) No restore (`_harness_scope`: both restore statements replaced by `pass`): exit=1,
   `FAILED tests/test_sysmodules_leak_b.py::test_module_a_left_no_harness_module_and_no_use_case_directory` (`/tmp/smleak-seed1.log`).
2. (ii) Restore too much (`_harness_scope`: the recorded entries are not put back on entry): exit=1, with
   `FAILED ...test_a_sibling_the_harness_imports_lazily_at_call_time_comes_from_its_own_use_case`
   (`ModuleNotFoundError: No module named 'reference'`, the lazy import) and
   `FAILED ...test_its_own_harness_modules_and_directory_are_in_place_while_its_tests_run` (`KeyError: 'translation'`) (`/tmp/smleak-seed2.log`).
3. (iii) Package modules counted as harness (`_harness_module`: the no-dot and non-package conditions removed, and the directory
   test moved one level up, so `ve/backends/*.py` counts as harness): exit=1,
   `FAILED tests/test_sysmodules_leak_b.py::test_package_modules_stay_loaded_and_bound_to_their_package`,
   `AssertionError: ve.backends.lean_runner` (`/tmp/smleak-seed3.log`).

No Lean or Rust code changed. Trust mutants: none (LIGHT lane; no trusted-core file).

## Can the nightly unsharded order still leak?

Not across test modules, for the `translation` class of leak. The modules affected are bare-named harness modules and their
directories, whether imported at collection or during the tests of a module. Each is now scoped to the test module that
imported it. Two things remain, and both are by design:
- Within one test module, its tests still share its harness modules. This is constraint (c): the tests are not failed for it.
- A session-scoped fixture or a plugin that imported a harness module would run outside every module scope. None does today:
  `git grep -A6 'scope="session"' -- 'tests/*.py'` shows no `usecases`, `sys.path`, `import_module` or `load_script` line.

State other than `sys.modules` and `sys.path` (module globals in `ve`, environment variables, cwd) is out of this item's scope.
A test module imported by another (`from tests.test_safety_framework import ...`) loads as `tests.test_safety_framework`, a
separate module object, inside the importer's scope. Its harness entries are therefore scoped to the importer, and pytest's own
import of `test_safety_framework` runs its module code again in its own scope.

## DELTA

None. This is a test-harness change only: no trusted Lean line, no decision path and no user-visible output. Trust +0. No DRI
signature is reserved.

## Spec re-read

- "snapshot sys.modules keys and sys.path before each test module is imported and restore after (keeping entries that existed
  before; dropping only names first added by that module's import ...)" against the task's deliverable 2. Done in
  `_harness_scope` (names that existed before get their earlier value back). The test is mutant (i).
- "re-install the module's own entries for its tests": done by the module fixture. The test is mutant (ii).
- "never drop stdlib, site-packages, `ve`, `tools`, `tests` or other package modules". Done by `_harness_module` (no dot, not a
  package, outside the shared and system directories). The test is mutant (iii).
- The task word "under a usecases/ dir or a dir that module added to sys.path" is implemented as "outside the shared and system
  directories", which covers both without naming `usecases` (see (2) for why). This is a wider class: bare modules from
  `docs/.../evidence`, `experiments/...` and `tmp_path` dirs that tests insert also count as harness. All of them are test-inserted
  directories, which the task's own wording includes.

## Notes for the DRI

- First version, caught by my own one-process run: the original rule's `Path(entry or ".")` and `ROOT / "usecases"` constants
  made `tools/source_graph.py` treat every file (and every use-case file) as read by every test. This failed
  `tests/test_select_tests.py::test_an_evidence_file_selects_its_readers_not_every_unmapped_unit` and
  `...::test_selector_mutants_fail_the_checks[the plan's graph forgets deleted files]` (`/tmp/smleak-oneproc-fixed.log`). Both pass
  with the final rule (`/tmp/smleak-fix2.log`, `6 passed`). The conftest comment says why no directory is named there.
- `tests/usecase_scope.py`, the per-file `_load` helpers (`tests/test_safety_framework.py`, `tests/test_pf_fidelity_fix.py`) and
  kb-10d's `_load` now overlap partly with the conftest scope. They are left as they are, because this item does not change them;
  removing them is a possible later clean-up.
- Selection: a `tests/conftest.py` change selects all 648 units (`select_tests.py --base ...` printed `648/648 test units ... FULL:
  tests/conftest.py`). This is expected for a shared-harness file and is unchanged.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed answer or Lean route touched.
2. Every deliverable built: PASS. The Deliverables table above lists deliverables 1-4 with commits and tests. The diff grep found no Python copy of a Lean decision, no report test and no overlap with in-flight branches (`git diff --name-only main...<branch>` for every `feature/ infra/ lean-first/ foundation/` branch: none touches tests/conftest.py).
3. Tests can fail: PASS. Seeded bugs (i)-(iii) each fail a named test (`seeded-mutants.json`).
4. Python/Lean/Rust agree: N.A., no product code in any language.
5. R8 binding: N.A., no relayed field.
6. Gate evidence matches final HEAD: PASS. The chain runs the gate on the committed final HEAD. The one-process run is on 337158a644 and the selected run on d6fa3a1683; code is unchanged since 337158a644, and the only later commits are docs.
7. No unsigned item: PASS. There are no DELTA rows and no trust growth.
8. Every user-visible change in DELTA: N.A. There is no user-visible output; this is test harness only.
9. Test selection: PASS. The plan selects every unit for a conftest change, including `tests/test_sysmodules_leak_{a,b}.py` (`/tmp/smleak-plan.log`). The intermediate select_tests regression was found and fixed (Notes).
10. Lean statements: N.A., no Lean.
11. Budgets fail closed: N.A., no budget or deadline. The new tests have no sleeps or timeouts.
12. No CPU or memory regression: PASS. The fixture's cost is 0.029 s of bookkeeping plus 0.027 s of re-imports per process (probe and `-X importtime`, (2)).
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions and cited evidence: PASS. B checks harness modules gone and package modules kept, and A checks its own modules present. Every number above names its command and log.
15. No overclaim, no silent cut, every check can fail, limits charged: PASS for the first three (the claims are scoped in "Can the nightly unsharded order still leak?"; nothing was cut; mutants (i)-(iii)). Limits: N.A.
