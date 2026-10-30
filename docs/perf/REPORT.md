Status: scope cut done per reviews/dri-decisions-20261029-scale-admission-profile.md item 1 (deletions plus 150 authored lines).
HEAD: `infra/scale-admission-profile`; the product tree (`lean ve rust tools conformance`) equals base `471ccc7e4`.
Changed: stage profiler deleted; whole-request admission CPU re-measured with the stage variable unset; stage figures UNKNOWN.
Open: dense 185 KB under 30 s is not shown (2× extrapolation about 104 CPU s); 4× UDHR hits the vocabulary limit.
Signatures: none needed; DELTA.md reads "No user-visible delta."

# Build report: scale-admission-profile

The decision input is [admission-profile-20261029.md](admission-profile-20261029.md): whole-request CPU per case
(median of 3), the fit against norms, the labelled 2× extrapolation, the measured constitution (1.36 CPU s) and the
4× refusal. Every stage-attributed figure from earlier rounds, including the 10.55 s `admitNDFull` claim, the
stage tables and the stage fits, is withdrawn as UNKNOWN; stage timing moves to row scale-stage-timers
([FOLLOW-UPS.md](FOLLOW-UPS.md)).

| Finding | Resolution | Check |
|---|---|---|
| F1–F9 | WITHDRAWN by the ruling: `ReadingsAdmissionProfile.lean`, its `Serve.lean` hook and `tests/test_readings_stage_times.py` are deleted, so the F7–F9 probes now stop at `ModuleNotFoundError` | `git diff main...HEAD -- lean ve rust tools conformance` is empty |
| Whole-request figures | `measure_admission.py` and `admission_cases.py` set no environment variable and keep no stage rows; seven cases × 3 runs re-measured | `tests/test_admission_evidence.py` (4 tests) |
| F-ready1, F-ready2 | No product code changes, so `[mutants]` needs no product mutant; DELTA has no rows | `seeded-bugs.json`; [DELTA.md](DELTA.md) |

Trust baseline, trust classes, assurance manifest, `checkers.lock`, `declarations.txt`, `predicates.txt` and
`history-dependent.json` were restored to the base and checked by their generators; `trust-mutants.json` was deleted.

## Checks

- `lake build`: PASS, 1,161 jobs; its `ve_service` (`92dd48e7…`) is pinned in main's `checkers.lock`. `lean/audit.py`:
  PASS, 668 sources, 7,428 theorems. `trust_map.py --check`: PASS, +0. `regen_generated.py --check`: 33 up to date.
- `test_readings_nd_lean.py`, `test_readings_s1_lean.py`, `test_admission_evidence.py`, `test_hang_guards.py`: 279 passed.
- `mac-pytest.sh --select` (26 units; VM fallback): `test_hang_guards` read the new test's `cpu > 0` as a time assert, so
  the bound was dropped and the test passes on rerun. `test_safety_framework.py::test_fsf_r2_probes_rerun_equals_saved_probes`
  ("probes.json is out of date") fails again on rerun. It is **pre-existing**: it reads only `usecases/` and product code,
  which equal the base. It is not in main-known-red.txt, so it is left to its own fix item.
- Seeded faults, each restored: the stage variable set in `measure_admission.py`, and a numeric stage row in the
  constitution evidence. Each fails its test ([seeded-bugs.json](seeded-bugs.json)).
- Not run: the full release gate and the full suite (owned by the chain and the merge train). No model calls.
  The copied 50%/75% UDHR inputs keep a trailing space and a blank final line, to preserve the review's exact inputs.
