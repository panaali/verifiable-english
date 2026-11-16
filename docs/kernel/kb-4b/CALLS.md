# kb-4b step 1: the `metered` cases the five frozen keys and the test suite send, by environment arm

Measured on `b8abce49e` (branch `feature/kb-4b` before any change), 2026-11-16, as
[kb-8b's CALLS.md](../kb-8b/CALLS.md) measured `quantity`: a throwaway recorder on `PYTHONPATH`
(`/tmp/kb4b/site/sitecustomize.py`, not committed) wraps `ve.backends.lean_service.LeanService.run_bound` and
`LeanServicePool.run_bound` (every relay of a service mode: `relay.rows`, `relay.decide` and the handle path
all call one of them; the pool calls `_run_chunk` directly, so no case is counted twice) and the one-shot runner
`ve.backends.lean.run` with `runner == "ve_metered"`, and logs every case of mode `metered`: its `kind`, the
answer's `status` and the features below, read from the case's `environment` object. A `sitecustomize` covers
the harnesses' and pytest's worker processes. Raw figures: [calls.json](calls.json).

The features (the Python reading of the Lean predicate named):

| | Feature | Lean |
|---|---|---|
| (a) | `language` is `ve.core@0` or `ve.core@0.1` | `Standalone.isLegacy`, the `decodeLegacy` arm of `evaluable` |
| (b) | `judgments@0` listed | the arm of `Compose.decidingEnvironment` that runs the profile table |
| (c) | `acts@0` listed | `Norms.Wire.readsActs`, the arm of `Standalone.actsRead` that gates and strips it |
| (d) | `norms@0` listed and a predicate with a `regulated` field | the regulated check and strip of `validated`, and the norms profile `profileTree` |
| (e) | `closure@0` and `nary@0` listed and a predicate with `defined`, `functional` or `total` | `Core.Layers.usesLayers` on the core family: the layered arm of `validated` and `CaseModel` |

## The five frozen keys

Each harness ran once, the five in parallel, each in its own scope
(`zsh manage-agents/iso.sh kb4b-<key> 16G -- .venv/bin/python <command>`); the run was repeated once more with a
digest of every case and answer recorded (the "before" side of the byte comparison in the report): both runs
logged the same calls.

| Key | Command | Exit | `metered` calls | (a) | (b) | (c) | (d) | (e) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| eligibility | `usecases/eligibility/run.py --no-write` | 0 | 0 | | | | | |
| Anthropic RSP | `usecases/anthropic-rsp/run.py --check` | 0 | 2,311 | 0 | 0 | 0 | 0 | 0 |
| OpenAI Preparedness | `usecases/openai-preparedness/run.py --check` | 0 | 36 | 0 | 0 | 0 | 0 | 0 |
| DeepMind FSF | `usecases/safety-framework/run.py --check` | 0 | 10,209 | 0 | 0 | 0 | 0 | 0 |
| agent policy | `usecases/agent-policy/check.py base` | 0 | 11,829 | 0 | 0 | 0 | 480 | 0 |
| **total** | | | **24,385** | **0** | **0** | **0** | **480** | **0** |

Every call is of kind `evaluate-budgeted` and every answer has status `ok`. Every environment is `ve.core@0.2`;
the profile lists are `relational-fol@0` (RSP, Preparedness, FSF), `data@0,relational-fol@0` (agent policy,
11,349) and `data@0,norms@0,relational-fol@0` (agent policy, 480, the ones with a `regulated` predicate). The eight
`usecases/*/results.json` files had the same SHA-256 after the runs as before, and `git status` was clean.

The figure 24,945 in `docs/kernel/frozen-keys-20261111.md` (item 3) and ALLOWANCES.md (2026-11-11) was counted on
an earlier tree; on this commit the keys send 24,385 `metered` cases.

**No frozen key sends (a), (b) or (c)**, so the split of step 2 moves no keyed call out of the kernel tier: the
condition to stop does not hold. Every keyed call is answered by the current runner.

## The test suite

The tests that reach `evaluate`: the 87 test files that the coverage map
(`~/.cache/ve-testmap/828449f6c0….json.gz`) records under the `evaluate` operation and as calling
`ve/backends/lean_runner.py:_metered` (the relay of the `metered` mode); the list is in [calls.json](calls.json)
(`tests.test_files` names the 82 of them that sent an `evaluate-budgeted` case). They ran once,
`.venv/bin/python -m pytest -q -n 12 -p no:cacheprovider <the 87 files>`, in a detached worktree of the same commit
with this checkout's Lean and Rust builds copied in: 4,094 passed, 3 skipped, 83 xfailed, 2 failed, 1 error. Of
those three, `tests/test_ownership_floor.py::test_the_safety_framework_adapter_records_plan_12_item_27` is red on
main (manage-agents/main-known-red.txt, row kb-10d), and
`tests/test_assurance_manifest.py::test_undeclared_call_site_inside_ve_is_refused` and
`tests/test_wire_gate_corpus.py::test_gate_corpus_holds_every_test_input_of_every_unit` (which reruns it) fail
because of the recorder: its wrapper of `lean.run` is the caller frame that `require_lean_call_site` reads. None
of them reads a `metered` answer.

| Kind | Cases | (a) | (b) | (c) | (d) | (e) |
|---|---:|---:|---:|---:|---:|---:|
| `evaluate-budgeted` | 137,397 | 66,707 (37 files) | 0 | 0 | 8,368 (15 files) | 11 (2 files) |
| `non-vacuity` | 87 | | | | | |

Every answer has status `ok`. By language: `ve.core@0` 56,539, `ve.core@0.1` 10,168, `ve.core@0.2` 70,690. The
files that send each feature are listed in [calls.json](calls.json) (`tests.feature_files`); (e) comes from
`tests/test_stage0_probe_matrix.py` and `tests/test_stage2_evaluation.py`.

No test sends (b) or (c) through the Python relay either: the `judgments@0` and `acts@0` arms of the `metered`
mode are reached only by Lean's own examples and by the service's recorded fixtures, which the recorder does not see.

## What the split moves

| Arm | Keyed calls | Test-suite calls | Runner after step 2 |
|---|---:|---:|---|
| (a) a frozen envelope | 0 | 66,707 | `runCaseLegacy` (candidate path `meteredLegacy`) |
| (c) `acts@0` read | 0 | 0 | `runCaseActs` (candidate path `meteredActs`) |
| (b) `judgments@0`, no `acts@0` | 0 | 0 | the current runner (kernel; this item leaves this arm where it is) |
| every other `ve.core@0.2` case, (d) and (e) included | 24,385 | 70,690 | the current runner (kernel) |
