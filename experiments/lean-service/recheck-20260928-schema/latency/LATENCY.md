# Lean service latency (stage 1)

Commit `43c6bc7`; AMD EPYC 7B12, 8 logical CPUs; load average [7.83056640625, 8.4208984375, 7.77197265625] before, [8.43212890625, 8.5087890625, 7.9609375] after; Python 3.14.7; full bench corpus.

Persistent: `LeanService.run(mode, [case])` on one warm `ve_service` process, timed at the Python boundary (JSON, IPC, supervision included). One-shot: one executable process per case, as ve-bench measured Lean. Bracketed values are 95% bootstrap intervals.

Cold start (spawn to handshake, n=20): p50 64.308 ms, p95 133.338 ms.

First 100 service requests are timed separately before workload sampling: {'n': 100, 'p50_ms': 1.232, 'p50_ci_ms': [1.024, 1.303], 'p95_ms': 40.526, 'p95_ci_ms': [1.786, 44.118], 'p99_ms': 44.553, 'p99_ci_ms': [40.514, 47.786], 'max_ms': 47.786}.

| Workload | Mode | Persistent p50 ms | Persistent p95 ms | Persistent p99 ms | One-shot p50 ms | One-shot p95 ms | p50 speedup |
|---|---|---:|---:|---:|---:|---:|---:|
| certificate/tableau | check-certificate | 0.96 [0.953, 0.967] | 1.385 [1.341, 1.526] | 2.374 [1.669, 3.879] | 66.967 | 87.078 | 69.8x |
| certificate/tableau-large | check-certificate | 37.616 [36.58, 38.065] | 44.78 [41.568, 51.806] | 67.877 [65.401, 72.233] | 97.028 | 154.564 | 2.6x |
| certificate/closure | check-certificate | 1.185 [1.175, 1.191] | 1.577 [1.528, 1.642] | 2.722 [1.725, 3.946] | 63.716 | 124.115 | 53.8x |
| certificate/order-farkas | order | 0.972 [0.967, 0.981] | 1.461 [1.407, 1.529] | 2.378 [1.644, 3.071] | 65.262 | 74.492 | 67.1x |
| finite-model/evaluation | evaluate | 0.649 [0.639, 0.654] | 1.102 [1.045, 1.181] | 3.452 [1.231, 4.736] | 66.488 | 111.784 | 102.4x |
| W1/norm-elaboration | norms | 0.593 [0.589, 0.599] | 0.988 [0.964, 1.031] | 1.097 [1.051, 1.631] | 69.326 | 74.831 | 116.9x |
| W1/conflict-check | norms | 1.442 [1.427, 1.464] | 2.153 [1.96, 2.355] | 3.001 [2.507, 6.28] | 70.916 | 86.101 | 49.2x |
| W3/definitions | route | 1.193 [1.185, 1.201] | 1.644 [1.6, 1.799] | 2.101 [1.856, 2.228] | 64.116 | 70.939 | 53.7x |
| W3/bundle | route | 1.612 [1.577, 1.649] | 2.58 [2.502, 2.723] | 3.971 [2.975, 5.231] | 65.168 | 76.786 | 40.4x |
| English/parse | english | 0.546 [0.541, 0.552] | 1.326 [1.112, 1.467] | 1.986 [1.508, 4.24] | 81.443 | 101.092 | 149.2x |
| English/admission | english | 0.529 [0.523, 0.539] | 1.168 [1.047, 1.31] | 1.682 [1.388, 4.004] | 75.914 | 106.755 | 143.5x |

Batches (section 4 gates; the client splits at 256 cases per request):

| Workload | Cases | Gate s | Persistent median s | Persistent p95 s | One-shot median s |
|---|---:|---:|---:|---:|---:|
| certificate/tableau-large | 8 | 0.3 | 0.327 | 0.416 | 0.282 |
| W1/conflict-check | 256 | 0.5 | 0.296 | 0.367 | 0.334 |
| W3/definitions | 2048 | 1.0 | 1.899 | 2.017 | 1.525 |
| W3/bundle | 256 | 0.25 | 0.317 | 0.342 | 0.330 |
