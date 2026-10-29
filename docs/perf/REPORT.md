Status: F3 FIXED; the profiler now measures every split-main `admitS2` call.
HEAD: `infra/scale-admission-profile`; the final fix commits and evidence are committed with this report.
Changed: Lean profiling, non-W2 regressions and seeded fault, three-repeat CPU evidence, corrected analysis.
Open: dense 185 KB under 30 s remains unproven; the 4× UDHR hits the vocabulary limit.
Signatures: the timing delta is DRI-signed by `reviews/dri-decisions-20261028-scale.md` item 1; the one trusted line is covered by R16.

# Build report: scale-admission-profile

## Decision and deliverables

The decision input is in [admission-profile-20261029.md](admission-profile-20261029.md): the admitted 2× case's main fixed-part `admitNDFull` takes 10.55 CPU s median within a 12.90 s ordinary route call. The earlier evidence omitted the repeated non-W2 main admission and understated stage totals. Linear scaling of the current 2× route to 185 KB at the same density is about 109 CPU s, so the earlier 15–25 s projection is withdrawn. The actual 185,033-byte constitution took 1.00 CPU s median because it has only 16 norm-kind units and two reading sets. The 4× dense synthetic UDHR refused at the vocabulary limit. This report measures and proposes an optimization; no admission decision logic changed.

| Finding | Fix | Regression or check | Commit |
|---|---|---|---|
| F1 | Time the repeated `admitS2` and fixed-part `admitNDFull` in split main and W2 product paths; regenerate all three evidence sets and the analysis | `test_split_w2_fixed_part_completion_is_timed`, `test_saved_twofold_profile_records_fixed_part_completion`; F1 probe | `6431c67d1`, `f6305c17c`, `864d3dd8c` |
| F2 | Register and expand environment handles using the service protocol before profiling | `test_normal_client_profiles_registered_and_reused_handle`; F2 probe | `6431c67d1` |
| F-ready1 | Build and kill two seeded Lean faults; save the record with changed file paths | `seeded-bugs.json`; review-ready `[mutants]` | `8400da266` |
| F-ready2 | Record the DRI's item 1 signature in the DELTA Ruling cell | review-ready `[delta]` | `8400da266` |
| F3 | Time the non-W2 split-main fallback `admitS2`; regenerate all evidence sets and stage fits | `test_split_non_w2_main_records_fallback_admission`, `test_saved_non_w2_prefixes_record_fallback_admission`, `test_saved_stage_table_uses_all_calls_in_each_run`; F3 probe | `9a0a8269d` (code), `d6f2766c8` (evidence) |

| Requirement | Owner | Delivered by | Check |
|---|---|---|---|
| Opt-in Lean stage timing, fixed-part and handle paths, unchanged answer | AGENT | `lean/VE/Service/ReadingsAdmissionProfile.lean`, `lean/Serve.lean`; commits `6431c67d1`, `f6305c17c`, `864d3dd8c` | `tests/test_readings_stage_times.py`, two seeded failures in `seeded-bugs.json` |
| Three CPU repeats of 13/19/31-norm prefixes and whole UDHR | AGENT | `admission-profile-evidence.json`, `admission-profile-controlled.json`, saved `inputs/` | Evidence probe: each listed case has exactly three runs |
| Three CPU repeats of synthetic 2×/4× and source generator | AGENT | `admission_cases.py`, `measure_admission.py`, `admission-profile-evidence.json` | Three runs each; 2× admitted, 4× recorded as vocabulary refusal |
| 185 KB target, stage fits, cause and bounded decision | AGENT | `admission-profile-constitution.json`, [profile](admission-profile-20261029.md) | Three constitution runs and stage table/fits from saved CPU ticks |
| R16 trusted growth, assurance inventory, generated Lean records | AGENT | `docs/trust-baseline.json`, `ve/assurance-manifest.json`, `lean/checkers.lock`, `lean/declarations.txt`, `lean/predicates.txt`; commits `f248cf187`, `85334b466`, `e7b2413d9` | `trust_map.py --check`, trust mutation evidence, assurance failed ID rerun |
| Final release gate on committed HEAD | EXTERNAL (chain) | Deferred by the task instruction | The chain writes `gate-result.json`; no local full gate was run |

The evidence files store the source and request hashes, service binary hash, VM one-minute load, process CPU, and per-stage CPU ticks for each repeat. The attempted `iso.sh exp-scale-admission 24G` call failed at the user systemd bus on this VM; the runner recorded that failure and used the same Lean executable at `nice -n 15`. The fits use CPU seconds under shared VM load, not wall time. No model API calls were made. No permanent test reads a moving Git diff for the report.

## Checks and seeded bugs

- `cd lean && PATH=$HOME/.elan/bin:$PATH lake build`: PASS, 1,163 jobs on the final Lean source. `python3 lean/audit.py`: PASS, 669 sources and 7,428 named theorem declarations.
- `.venv/bin/pytest -q tests/test_readings_stage_times.py`: PASS, 15 tests after F3; F1, F2 and F3 probes pass. The F3 probe failed before the fix.
- `uv run --no-sync python tools/trust_map.py --check`: PASS, K +0, S +0, trusted +1 in `Serve.lean`, unclassified 0. The earlier `trust-mutants.json` has zero applicable definitions; no new trusted definition was added in the fix.
- `tools/regen_generated.py --write` ran before the final Lean edit; `tools/lean_statements.py` and the checker-pin generator refreshed their outputs after the final build. The service hash in every evidence file equals the final binary hash.
- F3 final build: PASS, 1,163 jobs. `python3 lean/audit.py`: PASS, 669 sources and 7,428 theorem declarations. `test_saved_stage_table_uses_all_calls_in_each_run` checks the revised table directly against saved CPU ticks, including both non-W2 main admissions.
- Selected tests: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` passed 394 files with 0 failed IDs on the Mac. The runner snapshotted the final Lean source and evidence before two test-only assertion commits. On the final HEAD, the tightened timing file passed 8 tests and the one additional selected file, `tests/test_lineage_lint.py`, passed 13 tests. Together these cover the final 395-file selection without repeating the unchanged 394 files.
- `review-ready.py` on committed `30b66bac5`: PASS for clean, mutants, relay mutation gate, and DELTA. Its sole FAIL is the full release gate assigned to the merge train by this task.

`git diff --check main...HEAD` flags one trailing space in the copied 50% UDHR source and one blank final line in the copied 75% source. They are retained to preserve the exact inputs from the scale review; the authored code and report files have no whitespace findings.

Each temporary fault below was built, failed its named behavior test, and was restored before the final build. The machine-readable record is [seeded-bugs.json](seeded-bugs.json).

| Changed product file and temporary fault | Failing test |
|---|---|
| `lean/VE/Service/ReadingsAdmissionProfile.lean`: disable the W2 fixed-part branch | `test_split_w2_fixed_part_completion_is_timed` failed for elaborate, choice, and verdicts |
| `lean/Serve.lean`: pass an empty handle table to profiling | `test_normal_client_profiles_registered_and_reused_handle` failed on reuse |
| `lean/VE/Service/ReadingsAdmissionProfile.lean`: restrict the repeated probe to W2 | `test_split_non_w2_main_records_fallback_admission` failed for elaborate and choice |

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean response or Python relay schema changed; timing JSON stays on stderr, as checked by `test_readings_stage_times_do_not_change_the_answer`.
2. PASS — requirement table above maps each task row to commits and checks; `git diff main...HEAD` reviewed for one-owner, generated-file and scope rules.
3. PASS — two planted faults above each failed a focused test; `docs/perf/trust-mutants.json` from the original build records zero applicable trusted definitions.
4. PASS — `test_readings_stage_times_do_not_change_the_answer` checks the genuine response bytes with and without timing; no Python or Rust product code changed.
5. N.A. — no Python field was added to a relayed Lean answer; the diagnostic JSON is never read by Python.
6. N.A. — the user explicitly assigns the final full gate to the chain; `gate-result.json` is not yet produced on this branch.
7. PASS — [DELTA.md](DELTA.md) cites the DRI decision item 1 and R16, with a silent-default test and a ties follow-up in [FOLLOW-UPS.md](FOLLOW-UPS.md).
8. PASS — `test_readings_stage_times_do_not_change_the_answer` and `test_readings_stage_times_are_silent_by_default` exercise the only user-visible output delta; DELTA lists the opt-in stderr change.
9. PASS — the Mac selected run passed 394 files; the one final-HEAD addition and the tightened timing file passed separately as recorded above.
10. N.A. — no Lean theorem or approved statement changed; `lean/audit.py` passed.
11. N.A. — no public budget, deadline, limit or verdict behavior changed; timing tests use no sleep or elapsed-time assertion.
12. PASS — `admission-profile-evidence.json` and `admission-profile-constitution.json` record CPU and load; the hook is off by default by `test_readings_stage_times_are_silent_by_default`.
13. The full release gate and its collection check are assigned to the merge train by the task instruction.

No full release gate, full suite, or repeated broad selection was run locally. The external chain owns the final-HEAD gate under the task instruction.
