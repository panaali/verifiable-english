# kb-10d-nightly-fix: ownership adapter load is independent of what other use cases left in sys.modules

Status: built, ready for the chain gate. Branch feature/kb-10d-nightly-fix; final HEAD is the commit adding this report.
Changed: `tools/ownership_trace.py` `_load` (Python test-harness loader) and one new test in `tests/test_ownership_floor.py`.
Open items: none. DRI signature needed: none (DELTA: none, trust +0).
main-known-red line for kb-10d to remove on merge (`main-known-red.txt` line 4,
`tests/test_ownership_floor.py::test_the_safety_framework_adapter_records_plan_12_item_27`).

SIZE: 10 product, 20 tests, 0 other hand-written lines (excluding this report). Source: `git diff --stat main...HEAD`,
which shows tools/ownership_trace.py +10/-2 and tests/test_ownership_floor.py +20.

## Cause

The usecases' `run.py` files import their siblings by bare name (`import translation as T`). `tests/test_eligibility_wfp.py:23-25`
imports eligibility's `translation`, `run` and `reference` at module level, so in an unsharded run the collection step
puts eligibility's `translation` into `sys.modules` before any test runs. `_load` put the safety-framework directory on
`sys.path`, but `import translation` returned the cached eligibility module, which has no `READING_SETS`.

## Deliverables

| # | Task line | Commit | Evidence |
|---|---|---|---|
| 1 | Failing-first test, committed before the fix, independent of xdist grouping | 7b8dbaa0e9 (test only), extended in 46ab37d0a2 | `tests/test_ownership_floor.py::test_an_adapter_loads_its_own_siblings_whatever_another_use_case_left_in_sys_modules` |
| 2 | Smallest fix: `_load` order-independent; ownership.json byte-identical | d608ce1d10 | trace rerun below |
| 3 | Same pattern in other tools loaders: listed | (none needed) | list below |
| 4 | Optional autouse conftest fixture | not added: it would fail existing tests | list below |
| 5 | main-known-red.txt not edited | n/a | first lines of this report |

### (1) Fail-first

The test sets up the collision itself. It loads `usecases/eligibility/translation.py` as the module `translation`, puts it in
`sys.modules` with `monkeypatch.setitem`, and runs the item-27 check. It then loads the adapter again and asserts three things:
the adapter's `T` is safety-framework's `translation.py`; `sys.modules["translation"]` is still the eligibility module; and
`vocabulary`, which was absent before, is now the adapter's own module.

At 7b8dbaa0e9 (the test only; `_load` as on main):
`uv run pytest -q -p no:xdist tests/test_ownership_floor.py -k "sys_modules or plan_12_item_27"` gave exit=1, log
`/tmp/kb10d-failfirst.log`:
`E   AttributeError: module 'translation' has no attribute 'READING_SETS'` (usecases/safety-framework/run.py:63),
`FAILED tests/test_ownership_floor.py::test_an_adapter_loads_its_own_siblings_whatever_another_use_case_left_in_sys_modules`,
`1 failed, 1 passed`.

After the fix:
- Alone: `uv run pytest -q -p no:xdist tests/test_ownership_floor.py::test_an_adapter_loads_its_own_siblings_whatever_another_use_case_left_in_sys_modules` gave `1 passed`.
- With the whole file: `uv run pytest -q -p no:xdist tests/test_ownership_floor.py` gave exit=0, `25 passed`
  (`/tmp/kb10d-fix1.log`).

### (2) Fix

Before `exec_module`, `_load` pops from `sys.modules` every name that is a `*.py` stem in the use case's directory. The
names come from the tree, so a new sibling needs no list edit. It puts those entries back in a `finally` block. A
sibling name nothing held before keeps the use case's own module, as it did before the fix. This matters because the
harnesses import some siblings lazily, at call time: `import stage0` in anthropic-rsp and openai-preparedness `run.py`;
`import severity_and_dates`, then `import translation` and `import vocabulary` in safety-framework; `import reference`
in eligibility; `import reference_policy` in agent-policy. So a fresh trace process behaves exactly as before.
`sys.path` handling is unchanged.

Trace rerun (no diff): `bash /tmp/kb10d-trace.sh` ran under `wait-bg.sh` (exit 0, log `/tmp/kb10d-trace.log`). It runs
`tools/ownership_trace.py run <key> --out /tmp/kb10d-traces --jobs 4` for the five keys, then
`verdict --traces /tmp/kb10d-traces --out /tmp/kb10d-kernel`, then `cmp` against `docs/kernel/`. Output:
`agent-policy 0/42, anthropic-rsp 100/126, eligibility 269/269, openai-preparedness 228/239, safety-framework 244/262`,
`SAME ownership.json`, `SAME ownership.md`.

`passing-functions` on the same traces differs from the committed `docs/kernel/kb-10d/functions-under-passing.json` in
one record: the committed file lists `ve/backends/lean_service.py:executable_sha256.<locals>.<lambda>` under 4
openai-preparedness items. That lambda runs only when the `ve_service.sha256-cache` sidecar misses
(`ve/backends/lean_service.py:514-517`). My run hit the cache, so the difference comes from the binary-cache state and not
from `_load`. The file is not edited here.

### (3) Other tools loaders that put a directory on sys.path and import or exec

I searched `grep -rlE "sys\.path\.insert" tools | xargs grep -lE "exec_module|import_module"`, plus every
`sys.path.insert` that names a use case:
- `tools/ask_fixtures.py:90` inserts `usecases/agent-policy`, then `import focused`. No other use case has `focused.py`, so
  no collision is possible today and no test can fail. Listed, not changed.
- `tools/gate_collection.py`, `tools/hooks/precommit.py`, `tools/lean_service_parity.py`,
  `tools/question_answering_agreement.py`, `tools/question_answering_measure.py`, `tools/relay_lint.py`,
  `tools/history_tests.py`: they put ROOT, `tools/` or `tests/` on the path, not a use-case directory. They have no
  bare-name use-case siblings. Listed, not changed.

### (4) Autouse fixture: not added

A per-test fixture that fails a test leaving a use-case sibling in `sys.modules` would fail existing tests. Probe in one
process: loading the safety-framework, eligibility and agent-policy adapters leaves
`['environments', 'focused', 'mutants', 'translation', 'vocabulary']`. That is by design, for the lazy imports above. The
tests that would fail are those that call `OT.ADAPTERS[...]().load()` in a fresh process:
`tests/test_ownership_floor.py::test_the_safety_framework_adapter_records_plan_12_item_27` and the other tests in that file
that load an adapter. Also, the nightly leak comes from module-level imports at collection (`tests/test_eligibility_wfp.py`,
`tests/test_agent_policy*.py` `import check`), which a per-test fixture does not see.

## Condition tests

- `tests/test_ownership_floor.py`, with the new test named above, is selected:
  `uv run python tools/select_tests.py --base $(git merge-base HEAD main)` lists it (`/tmp/kb10d-select.log` line 4).
- One process, after every test file that loads a use case's modules:
  `zsh mac-pytest.sh -- -q -p no:xdist tests/test_eligibility_wfp.py tests/test_agent_policy.py tests/test_agent_policy_replay_decode.py tests/test_agent_policy_rerun.py tests/test_agent_policy_unspecified.py tests/test_kb10b_switch.py tests/test_keyed_answers_authority.py tests/test_kb10_shadow.py tests/test_ownership_floor.py`
  gave exit=0, `290 passed in 122.16s`, "workers xdist off; HEAD d608ce1d (clean)" (`/tmp/kb10d-oneproc.log`).

## Seeded bugs (Python; the only changed language)

Each bug was planted in `tools/ownership_trace.py` `_load` and checked against
`tests/test_ownership_floor.py::test_an_adapter_loads_its_own_siblings_whatever_another_use_case_left_in_sys_modules`
with `-p no:xdist`. Each was restored with `git checkout`.

1. No drop before exec (the saved-entries filter is made always false): exit=1,
   `AttributeError: module 'translation' has no attribute 'READING_SETS'` (`/tmp/kb10d-seed1.log`).
2. No restore (`sys.modules.update(saved)` replaced by `pass`): exit=1, `assert <module 'translation' from
   '.../safety-framework/translation.py'> is <module 'translation' from '.../eligibility/translation.py'>` (`/tmp/kb10d-seed2.log`).
3. Own siblings popped after exec (the full-restore form): exit=1, `assert None is <module 'vocabulary' from
   '.../safety-framework/vocabulary.py'>` (`/tmp/kb10d-seed3.log`).

Trust mutants: none. No Lean changed, no trusted-core file, about 30 changed lines.

## DELTA

None. This is a Python test-harness loader, with no trusted Lean line and no decision path replaced. The trace output is
byte-identical (above). Trust +0. No DRI signature is reserved.

## Notes for the DRI

- `tests/usecase_scope.py` (`usecase_scope`, `load_script`) already scopes use-case siblings for tests. It also pops the
  case's own siblings and resets `sys.path` on exit, which would break the trace harness's lazy imports when
  `run_harness` calls `main(["--check"])` after the load. For that reason `_load` keeps its own 7-line form. One shared
  owner (a tools-side helper with a "keep own siblings" option that `tests/usecase_scope.py` imports) is a possible
  later refactor.
- Lazy sibling imports at call time are still order-dependent within one process. For example, `severity_and_dates`
  does `import run as R` and gets whatever `run` is in `sys.modules`; after collection that is eligibility's `run` from
  `tests/test_eligibility_wfp.py`. No current test exercises that path after another use case's module is loaded; the
  one-process run above is green. Making it fully order-independent means loading siblings under case-unique names
  (an import hook), which is beyond this item's smallest fix.
- MEASURED CW: `delegate-cw.py` could not find this session ("own session not found (needs VE_STEP and
  CLAUDE_CONFIG_DIR ...)"), so this was not measured.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A. No relayed answer or schema changed.
2. Deliverables: PASS. See the Deliverables table; the new test is named above. Diff grep: no Python copy of a Lean
   decision and no new report test.
3. Tests can fail: PASS. Seeded bugs 1-3 fail the new test.
4. Py/Lean/Rust agreement: N.A. No checker path changed. Trace verdict `SAME ownership.json` / `SAME ownership.md`
   (`/tmp/kb10d-trace.log`).
5. R8 binding: N.A. No field read from a Lean answer.
6. Gate evidence: PASS. The chain runs the gate on the committed final HEAD. The final selected run is on committed code.
7. Unsigned items: PASS. No DELTA rows; no trust growth.
8. User-visible change: PASS (none). The trace output is byte-identical (`/tmp/kb10d-trace.log`).
9. Test selection: PASS. `select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_ownership_floor.py`
   (`/tmp/kb10d-select.log`).
10. Lean statements: N.A. No Lean changed.
11. Budgets and deadlines: N.A. No budget or deadline code. The new test has no sleep or timeout.
12. CPU and memory: N.A. Each load pops and restores at most the use case's own `*.py` stems (fewer than 10 names).
13. Test-removed trailers: N.A. No test removed or renamed.
14. Both directions: PASS. The new test asserts that a stale entry is replaced during the load, that the stale entry is
    put back after it, and that a name nothing held keeps the case's module (seeded bugs 1-3). Every claim cites a log.
    Spec re-read: task (2) "save, drop and restore the use case's sibling modules ... around exec_module" against
    `tools/ownership_trace.py` `_load`. The restore covers the entries that were there before; a name absent before is
    not dropped, because of the lazy imports (Notes). This is the narrower behaviour change.
15. Overclaim, silent cut, checks that can fail, limits: PASS. Step (4) is not done, with its reason and the tests it
    would fail. The universal claims ("byte-identical", "no diff") cite `/tmp/kb10d-trace.log`. Limits: N.A.
