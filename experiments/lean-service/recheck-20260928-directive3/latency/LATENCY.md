# Lean service latency (stage 1)

Commit `eb97efad`; AMD EPYC 7B12, 16 logical CPUs; load average [11.04541015625, 12.72998046875, 12.34716796875] before, [10.48779296875, 11.2314453125, 11.80419921875] after; Python 3.14.7; full bench corpus.

Persistent: `LeanService.run(mode, [case])` on one warm `ve_service` process, timed at the Python boundary (JSON, IPC, supervision included). One-shot: one executable process per case, as ve-bench measured Lean. Bracketed values are 95% bootstrap intervals.

Build check (SHA-256 of the executable, once per client process, not in the cold starts): 140.372 ms.

Cold start (spawn to handshake, n=20): p50 46.783 ms [41.922, 63.143], p95 64.124 ms [63.579, 64.874], max 64.874 ms.

First 100 service requests are timed separately before workload sampling: {'n': 100, 'p50_ms': 1.474, 'p50_ci_ms': [1.231, 1.593], 'p95_ms': 43.285, 'p95_ci_ms': [2.021, 44.581], 'p99_ms': 44.999, 'p99_ci_ms': [43.242, 48.339], 'max_ms': 48.339}.

Service CPU is the service process's on-CPU time per call; runqueue wait is the time the service process and the client thread were runnable but waiting for a CPU during the call (`/proc/.../schedstat`), the share of the latency that other load on the host adds.

| Workload | Mode | Persistent p50 ms | Persistent p95 ms | Persistent p99 ms | Service CPU p50 / p95 ms | Runqueue wait p50 / p95 / max ms | One-shot p50 ms | One-shot p95 ms | p50 speedup |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| certificate/tableau | check-certificate | 1.164 [1.155, 1.172] | 1.647 [1.613, 1.751] | 2.059 [1.89, 2.495] | 0.768 / 0.967 | 0.0 / 0.716 / 1.324 | 70.332 | 73.731 | 60.4x |
| certificate/tableau-large | check-certificate | 41.33 [40.904, 41.85] | 54.94 [51.867, 56.678] | 74.035 [57.356, 87.361] | 32.851 / 43.031 | 0.0 / 2.643 / 8.446 | 96.134 | 102.297 | 2.3x |
| certificate/closure | check-certificate | 1.368 [1.327, 1.396] | 1.989 [1.912, 2.018] | 2.239 [2.06, 2.454] | 0.859 / 1.218 | 0.0 / 0.019 / 0.601 | 49.935 | 63.338 | 36.5x |
| certificate/order-farkas | order | 1.505 [1.479, 1.527] | 1.809 [1.761, 1.905] | 2.264 [1.943, 2.287] | 0.821 / 0.941 | 0.0 / 0.016 / 0.066 | 50.496 | 60.249 | 33.6x |
| finite-model/evaluation | evaluate | 1.064 [0.981, 1.125] | 1.61 [1.541, 1.73] | 1.981 [1.774, 2.079] | 0.575 / 0.835 | 0.0 / 0.017 / 0.107 | 49.184 | 52.078 | 46.2x |
| W1/norm-elaboration | norms | 0.824 [0.797, 0.847] | 1.277 [1.231, 1.323] | 1.534 [1.367, 1.71] | 0.365 / 0.51 | 0.0 / 0.014 / 0.07 | 44.732 | 46.855 | 54.3x |
| W1/conflict-check | norms | 1.547 [1.514, 1.574] | 2.227 [2.14, 2.315] | 2.457 [2.338, 2.538] | 1.09 / 1.519 | 0.0 / 0.017 / 0.088 | 45.25 | 48.846 | 29.3x |
| W3/definitions | route | 1.381 [1.354, 1.407] | 1.942 [1.867, 2.003] | 2.103 [2.032, 2.4] | 0.951 / 1.208 | 0.0 / 0.013 / 0.146 | 49.522 | 58.253 | 35.9x |
| W3/bundle | route | 1.622 [1.569, 1.655] | 2.326 [2.266, 2.39] | 2.583 [2.405, 2.911] | 1.127 / 1.529 | 0.0 / 0.015 / 0.089 | 69.519 | 75.424 | 42.9x |
| English/parse | english | 0.884 [0.852, 0.901] | 1.259 [1.209, 1.344] | 1.505 [1.373, 1.834] | 0.389 / 0.576 | 0.0 / 0.012 / 0.078 | 44.684 | 47.748 | 50.5x |
| English/admission | english | 0.615 [0.592, 0.635] | 1.094 [1.044, 1.156] | 1.389 [1.179, 1.663] | 0.283 / 0.487 | 0.0 / 0.009 / 0.033 | 43.463 | 45.28 | 70.7x |

Batches (section 4 gates; the client splits at 256 cases per request, and the pool into at least one request per process):

| Workload | Cases | Gate s | Pool of 2 median s | Pool of 2 p95 s | One process median s | One process p95 s | One-shot median s |
|---|---:|---:|---:|---:|---:|---:|---:|
| certificate/tableau-large | 8 | 0.3 | 0.174 [0.165, 0.185] | 0.223 | 0.254 | 0.361 | 0.182 |
| W1/conflict-check | 256 | 0.5 | 0.150 [0.148, 0.153] | 0.166 | 0.185 | 0.213 | 0.186 |
| W3/definitions | 2048 | 1.0 | 0.938 [0.886, 0.974] | 1.145 | 1.408 | 1.576 | 0.904 |
| W3/bundle | 256 | 0.25 | 0.162 [0.16, 0.17] | 0.191 | 0.206 | 0.265 | 0.184 |
