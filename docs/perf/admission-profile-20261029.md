Status: whole-request admission CPU re-measured on main's `ve_service`; dense 185 KB under 30 s is not shown.
The 185,033-byte constitution took 1.36 CPU s median for the whole request (three runs).
HEAD: committed on `infra/scale-admission-profile`; baseline `471ccc7e4`; no product file differs from it.
Changed: stage profiler withdrawn, every stage figure UNKNOWN; inputs and runner kept, evidence re-measured.
Open: the 4× UDHR is refused at the vocabulary limit; stage attribution moves to row scale-stage-timers.

# Readings admission profile, 2026-10-29 (re-measured 2026-10-30)

## Decision input

For reviews/dri-decisions-20261028-scale.md item 2 (one 185 KB admission under ~30 s?), whole-request process
CPU only. Every per-stage count, total and fit, including the earlier "main fixed-part `admitNDFull`
10.55 CPU s", the stage table, the stage fits and the `runCase` column, is withdrawn: **UNKNOWN (stage profiler
withdrawn, reviews/dri-decisions-20261029-scale-admission-profile.md item 1)**. No dominant stage is named.

- **Measured constitution:** 1.36 CPU s median (1,132 units, but 16 norm-kind units and two reading sets).
- **Extrapolation, not a measurement:** the dense synthetic 2× UDHR's 12.30 CPU s median, scaled linearly in
  source bytes from 21,832 to 185,033 at the same density, gives about 104 CPU s; 30 s would need about a
  3.5-fold cut in CPU per byte.
- **Fit:** least squares of log(whole-request CPU) on log(norm-kind units) over the three controlled prefixes
  (13, 19, 31; three main sets each) gives exponent 1.57, descriptive only (three points; units and companions
  also change).
- **4× refusal:** the synthetic 4× UDHR (520 units, 28 companion sets) is refused with
  `ResourceLimit: vocabulary size` before admission (0.14 CPU s median).

## Method and evidence

`admission_cases.py` builds the requests from `inputs/` (the scale review's 50/75/100% UDHR prefixes, 100% being
the whole UDHR, and the 06Z constitution pilot); every regenerated request is byte-identical to its saved hash.
Synthetic cases replicate and rename articles and fix main sets to their first reading; `--main-sets 3` makes
the 31-norm controlled case. `measure_admission.py` runs each request three times in a fresh `ve_service`,
recording child CPU (user plus system), one-minute load before and after, transport, answer status and error,
request hash and service SHA-256. It sets no environment variable and records no stage rows. Runs used
`VE_READINGS_STAGE_TIMES` unset and service `92dd48e7…`, main's pinned build, which has no stage code. Transport
was `iso.sh exp-scale-admission 24G` for every run (it execs the service in a systemd scope, so its CPU counts as
the runner's child); the superseded runs used the `nice -n 15` fallback. Load was 25.55–28.58 on 32 vCPUs.

| Input | Evidence case | Source bytes | Units | Norm-kind units | Sets | Whole-request CPU s, median | Outcome |
|---|---|---:|---:|---:|---:|---:|---|
| UDHR 50% | `admission-prefix-50` | 5,545 | 64 | 13 | 7 | 0.71 | admitted |
| UDHR 75% | `admission-prefix-75` | 8,260 | 101 | 19 | 9 | 0.94 | admitted |
| UDHR 100%, three main sets | `admission-prefix-100-main3` | 10,916 | 130 | 31 | 10 | 2.71 | admitted, eight main choices |
| Whole UDHR | `admission-prefix-100` | 10,916 | 130 | 31 | 14 | 5.56 | admitted, 64 main choices |
| Synthetic 2× UDHR | `admission-prefix-100-2x` | 21,832 | 260 | 62 | 14 | 12.30 | admitted; main sets fixed |
| Synthetic 4× UDHR | `admission-prefix-100-4x` | 43,664 | 520 | 124 | 28 | 0.14 | `ResourceLimit: vocabulary size` |
| Constitution pilot | `admission-constitution-185kb` | 185,033 | 1,132 | 16 | 2 | 1.36 | admitted |

Runs: `admission-profile-evidence.json`, `-controlled.json`, `-constitution.json`; `tests/test_admission_evidence.py`
checks three numeric runs per case, no numeric stage field, no stage variable in either script, and these medians.
