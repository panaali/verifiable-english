Status: MEASURED; near-linear admission is reachable at bounded choice count.
HEAD: `infra/scale-admission-profile`, code through `e7b2413d9`; this report and evidence are committed with it.
Changed: opt-in Lean stage timings, UDHR and constitution measurement inputs, three-repeat CPU evidence and growth fits.
Open: the 4× UDHR hits the vocabulary limit; `scale-linear-admission` is the next infra row.
Signatures: the timing delta is DRI-signed by `reviews/dri-decisions-20261028-scale.md` item 1; the one trusted line is covered by R16.

# Build report: scale-admission-profile

## Decision and deliverables

The decision input is in [admission-profile-20261029.md](admission-profile-20261029.md): `admitS2` and filled-document admission have controlled-prefix fitted exponents 2.93 and 2.47. Indexing norms and relevant units and reusing filled checks should reduce admission to exponent about 1.0–1.2 at bounded choices, with an estimated 15–25 CPU s for an admissible UDHR-density 185 KB document. The actual 185,033-byte constitution took 1.29 CPU s median for ordinary `runCase`, because it has only 16 norm-kind units and two reading sets. The 4× dense synthetic UDHR refused at the vocabulary limit, so no admission time is claimed for it. This report is measurement and a fix proposal; no admission decision logic was changed.

| Requirement | Owner | Delivered by | Check |
|---|---|---|---|
| Opt-in Lean stage timing, silent by default, unchanged answer | AGENT | `lean/VE/Service/ReadingsAdmissionProfile.lean`, `lean/Serve.lean`; commits `f248cf187`, `85334b466` | `tests/test_readings_stage_times.py` (3 passed), three seeded failures below |
| Three CPU repeats of 13/19/31-norm prefixes and whole UDHR | AGENT | `admission-profile-evidence.json`, `admission-profile-controlled.json`, saved `inputs/` | Evidence probe: each listed case has exactly three runs |
| Three CPU repeats of synthetic 2×/4× and source generator | AGENT | `admission_cases.py`, `measure_admission.py`, `admission-profile-evidence.json` | Three runs each; 2× admitted, 4× recorded as vocabulary refusal |
| 185 KB target, stage fits, cause and near-linear decision | AGENT | `admission-profile-constitution.json`, [profile](admission-profile-20261029.md) | Three constitution runs and stage table/fits from saved CPU ticks |
| R16 trusted growth, assurance inventory, generated Lean records | AGENT | `docs/trust-baseline.json`, `ve/assurance-manifest.json`, `lean/checkers.lock`, `lean/declarations.txt`, `lean/predicates.txt`; commits `f248cf187`, `85334b466`, `e7b2413d9` | `trust_map.py --check`, trust mutation evidence, assurance failed ID rerun |
| Final release gate on committed HEAD | EXTERNAL (chain) | Deferred by the task instruction | The chain writes `gate-result.json`; no local full gate was run |

The evidence files store the source and request hashes, service binary hash, VM one-minute load, process CPU, and per-stage CPU ticks for each repeat. The attempted `iso.sh exp-scale-admission 24G` call failed at the user systemd bus on this VM; the runner recorded that failure and used the same Lean executable at `nice -n 15`. The load exceeded 32 on several runs, so the fits use CPU seconds, not wall time. No model API calls were made. No permanent test reads a moving Git diff for the report.

## Checks and seeded bugs

- `python3 tools/check_lean_imports.py`: PASS, 669 modules, after moving the profiler to the service layer. The first selected run stopped here before pytest, prompting the move.
- `uv run python tools/regen_generated.py --write`: PASS after the module move and again after the assurance manifest fix; generated files were not hand-edited.
- `cd lean && PATH=$HOME/.elan/bin:$PATH lake build`: PASS, 1163 jobs. `python3 lean/audit.py`: PASS, 669 sources and 7,428 theorem declarations.
- `uv run pytest -q tests/test_readings_stage_times.py`: PASS, 3 tests. `uv run python tools/trust_map.py --check`: PASS, K +0, S +0, trusted +1 in `Serve.lean`, unclassified 0. `docs/perf/trust-mutants.json`: Mac runner exit 0, 0 applicable definitions and 0 mutants; rescore after the module move performed a full run because Lean inputs differed.
- Selected tests: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` ran 393 mapped test units on the Mac. One failed: `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`. Adding the new file to `other_json` made the local failed-ID check pass and the Mac `mac-pytest.sh -- tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` rerun pass (1 passed). The broad selection was not rerun.
- `uv run python tools/gate_collection.py --check --prebuilt`: PASS, 30,165 collected, 3 added, 0 refused, 0 stale or malformed trailers. No tests were removed or renamed. Free disk space before the final evidence commit: 141 GB.

Each seeded fault was restored before the final build. These faults changed the behavior under test and each failed its named test, rather than only a hash or build check:

| Changed product file and temporary fault | Failing test |
|---|---|
| `lean/VE/Service/ReadingsAdmissionProfile.lean` (at its earlier `Readings/AdmissionProfile.lean` path): require `VE_READINGS_STAGE_TIMES=0` instead of `=1` | `test_readings_stage_times_are_silent_by_default` |
| Same Lean file: emit `splitCaseWrong` instead of `splitCase` | `test_readings_stage_times_are_json_lines_for_each_stage` |
| `lean/Serve.lean`: output JSON `null` instead of the response | `test_readings_stage_times_do_not_change_the_answer`; its expected-response assertion was strengthened after an equality-only version failed to catch this fault |

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean response or Python relay schema changed; timing JSON stays on stderr, as checked by `test_readings_stage_times_do_not_change_the_answer`.
2. PASS — requirement table above maps each task row to commits and checks; `git diff main...HEAD` reviewed for one-owner, generated-file and scope rules.
3. PASS — three seeded faults above each failed a focused test; `docs/perf/trust-mutants.json` exits 0 and records zero applicable trusted definitions.
4. PASS — `test_readings_stage_times_do_not_change_the_answer` checks the genuine response bytes with and without timing; no Python or Rust product code changed.
5. N.A. — no Python field was added to a relayed Lean answer; the diagnostic JSON is never read by Python.
6. N.A. — the user explicitly assigns the final full gate to the chain; `gate-result.json` is not yet produced on this branch.
7. PASS — [DELTA.md](DELTA.md) cites the DRI decision item 1 and R16, with a silent-default test and a ties follow-up in [FOLLOW-UPS.md](FOLLOW-UPS.md).
8. PASS — `test_readings_stage_times_do_not_change_the_answer` and `test_readings_stage_times_are_silent_by_default` exercise the only user-visible output delta; DELTA lists the opt-in stderr change.
9. PASS — the selected runner mapped 393 units and found the missing assurance classification; `test_every_json_handling_lean_file_is_classified` then passed on the Mac.
10. N.A. — no Lean theorem or approved statement changed; `lean/audit.py` passed.
11. N.A. — no public budget, deadline, limit or verdict behavior changed; timing tests use no sleep or elapsed-time assertion.
12. PASS — `admission-profile-evidence.json` and `admission-profile-constitution.json` record CPU and load; the hook is off by default by `test_readings_stage_times_are_silent_by_default`.
13. PASS — `tools/gate_collection.py --check --prebuilt` reports 0 refused, stale and malformed trailers; 3 tests added and none removed.

No full release gate, full suite, or repeated broad selection was run locally. The external chain owns the final-HEAD gate under the task instruction.
