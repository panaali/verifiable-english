# Lean service latency (stage 1)

Commit `8bf11607040f3577f33d8e49f951286353185ffa`; AMD EPYC 7B12, 16 logical CPUs; load average [5.98681640625, 7.27294921875, 10.279296875] before, [6.65869140625, 7.0380859375, 9.6416015625] after; Python 3.14.7; full bench corpus.

Persistent: `LeanService.run(mode, [case])` on one warm `ve_service` process, timed at the Python boundary (JSON, IPC, supervision included). One-shot: one executable process per case, as ve-bench measured Lean. Bracketed values are 95% bootstrap intervals.

Build check (SHA-256 of the executable, once per client process, not in the cold starts): 143.869 ms.

Cold start (spawn to handshake, n=20): p50 40.819 ms [40.274, 41.903], p95 42.348 ms [41.993, 43.304], max 43.304 ms.

First 100 service requests are timed separately before workload sampling: {'n': 100, 'p50_ms': 1.33, 'p50_ci_ms': [1.182, 1.468], 'p95_ms': 25.24, 'p95_ci_ms': [1.948, 25.978], 'p99_ms': 29.182, 'p99_ci_ms': [25.31, 33.253], 'max_ms': 33.253}.

Service CPU is the service process's on-CPU time per call; runqueue wait is the time the service process and the client thread were runnable but waiting for a CPU during the call (`/proc/.../schedstat`), the share of the latency that other load on the host adds.

| Workload | Mode | Persistent p50 ms | Persistent p95 ms | Persistent p99 ms | Service CPU p50 / p95 ms | Runqueue wait p50 / p95 / max ms | One-shot p50 ms | One-shot p95 ms | p50 speedup |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| certificate/tableau | check-certificate | 0.748 [0.736, 0.794] | 1.589 [1.501, 1.647] | 1.772 [1.71, 2.078] | 0.456 / 0.846 | 0.0 / 0.008 / 0.033 | 49.074 | 54.181 | 65.6x |
| certificate/tableau-large | check-certificate | 24.659 [24.458, 24.957] | 39.663 [33.838, 40.805] | 50.235 [42.128, 60.445] | 18.471 / 28.864 | 0.0 / 0.031 / 37.238 | 61.94 | 65.713 | 2.5x |
| certificate/closure | check-certificate | 1.196 [1.078, 1.287] | 1.901 [1.841, 1.989] | 2.163 [2.025, 2.245] | 0.713 / 1.146 | 0.0 / 0.016 / 1.391 | 49.811 | 53.303 | 41.6x |
| certificate/order-farkas | order | 1.387 [1.345, 1.417] | 1.842 [1.76, 1.938] | 2.218 [1.98, 2.349] | 0.779 / 1.003 | 0.0 / 0.014 / 0.602 | 49.298 | 57.462 | 35.5x |
| finite-model/evaluation | evaluate | 0.998 [0.775, 1.111] | 1.517 [1.476, 1.582] | 1.853 [1.669, 2.064] | 0.551 / 0.708 | 0.0 / 0.02 / 0.546 | 49.222 | 51.776 | 49.3x |
| W1/norm-elaboration | norms | 0.762 [0.673, 0.817] | 1.438 [1.358, 1.498] | 1.741 [1.557, 1.923] | 0.321 / 0.545 | 0.0 / 0.015 / 0.266 | 45.005 | 48.939 | 59.1x |
| W1/conflict-check | norms | 1.041 [1.032, 1.054] | 2.15 [1.97, 2.254] | 2.454 [2.311, 2.775] | 0.725 / 1.34 | 0.0 / 0.013 / 0.05 | 44.796 | 56.51 | 43.0x |
| W3/definitions | route | 1.426 [1.32, 1.496] | 2.058 [1.999, 2.183] | 2.493 [2.338, 2.595] | 0.838 / 1.139 | 0.0 / 0.015 / 0.881 | 48.265 | 51.921 | 33.8x |
| W3/bundle | route | 1.363 [1.272, 1.494] | 2.402 [2.349, 2.551] | 3.068 [2.578, 4.15] | 0.823 / 1.443 | 0.0 / 0.013 / 0.046 | 54.165 | 67.155 | 39.7x |
| English/parse | english | 0.747 [0.728, 0.778] | 1.217 [1.18, 1.246] | 1.638 [1.308, 2.003] | 0.386 / 0.513 | 0.0 / 0.015 / 2.858 | 46.187 | 51.507 | 61.8x |
| English/admission | english | 1.128 [1.108, 1.152] | 1.522 [1.483, 1.736] | 1.976 [1.841, 2.196] | 0.464 / 0.6 | 0.0 / 0.022 / 1.202 | 44.162 | 47.398 | 39.2x |

Batches (section 4 gates; the client splits at 256 cases per request, and the pool into at least one request per process):

| Workload | Cases | Gate s | Pool of 2 median s | Pool of 2 p95 s | One process median s | One process p95 s | One-shot median s |
|---|---:|---:|---:|---:|---:|---:|---:|
| certificate/tableau-large | 8 | 0.3 | 0.141 [0.135, 0.147] | 0.162 | 0.211 | 0.254 | 0.175 |
| W1/conflict-check | 256 | 0.5 | 0.110 [0.106, 0.114] | 0.125 | 0.182 | 0.193 | 0.186 |
| W3/definitions | 2048 | 1.0 | 0.797 [0.782, 0.811] | 0.876 | 1.283 | 1.385 | 0.880 |
| W3/bundle | 256 | 0.25 | 0.122 [0.118, 0.124] | 0.138 | 0.190 | 0.225 | 0.183 |
