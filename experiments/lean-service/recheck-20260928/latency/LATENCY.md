# Lean service latency (stage 1)

Commit `7cbcfba`; AMD EPYC 7B12, 8 logical CPUs; load average [13.998046875, 8.6689453125, 7.47412109375] before, [10.50537109375, 14.05712890625, 11.212890625] after; Python 3.14.7; full bench corpus.

Persistent: `LeanService.run(mode, [case])` on one warm `ve_service` process, timed at the Python boundary (JSON, IPC, supervision included). One-shot: one executable process per case, as ve-bench measured Lean. Bracketed values are 95% bootstrap intervals.

Cold start (spawn to handshake, n=20): p50 216.411 ms, p95 349.037 ms.

First 100 service requests are timed separately before workload sampling: {'n': 100, 'p50_ms': 4.567, 'p50_ci_ms': [3.9, 4.865], 'p95_ms': 128.22, 'p95_ci_ms': [13.072, 145.661], 'p99_ms': 151.829, 'p99_ci_ms': [128.174, 161.813], 'max_ms': 161.813}.

| Workload | Mode | Persistent p50 ms | Persistent p95 ms | Persistent p99 ms | One-shot p50 ms | One-shot p95 ms | p50 speedup |
|---|---|---:|---:|---:|---:|---:|---:|
| certificate/tableau | check-certificate | 1.8 [1.391, 2.783] | 8.163 [7.975, 8.988] | 10.841 [9.936, 17.062] | 318.668 | 403.287 | 177.0x |
| certificate/tableau-large | check-certificate | 142.446 [134.088, 148.482] | 287.77 [268.874, 306.52] | 347.536 [316.18, 475.243] | 417.583 | 636.542 | 2.9x |
| certificate/closure | check-certificate | 2.669 [2.298, 2.893] | 8.432 [7.001, 8.997] | 10.467 [9.246, 12.032] | 213.335 | 349.138 | 79.9x |
| certificate/order-farkas | order | 1.683 [1.629, 1.76] | 5.311 [4.748, 6.077] | 8.567 [6.329, 9.4] | 226.449 | 375.142 | 134.6x |
| finite-model/evaluation | evaluate | 1.906 [1.76, 2.267] | 7.395 [6.364, 8.105] | 9.992 [8.314, 12.32] | 338.904 | 496.018 | 177.8x |
| W1/norm-elaboration | norms | 0.68 [0.656, 0.716] | 4.333 [4.16, 4.509] | 6.566 [4.616, 7.978] | 206.674 | 611.714 | 303.9x |
| W1/conflict-check | norms | 1.535 [1.497, 1.584] | 5.326 [5.199, 5.528] | 8.983 [5.551, 9.714] | 151.903 | 199.698 | 99.0x |
| W3/definitions | route | 1.503 [1.455, 1.611] | 5.248 [5.141, 5.437] | 6.06 [5.592, 9.767] | 148.871 | 181.2 | 99.0x |
| W3/bundle | route | 1.33 [1.323, 1.34] | 2.109 [1.957, 2.351] | 2.877 [2.594, 4.4] | 68.975 | 79.701 | 51.9x |
| English/parse | english | 0.531 [0.526, 0.537] | 0.949 [0.911, 0.969] | 1.31 [1.035, 1.831] | 67.607 | 82.193 | 127.3x |
| English/admission | english | 0.531 [0.527, 0.536] | 0.917 [0.871, 0.965] | 1.052 [0.973, 1.155] | 64.915 | 70.045 | 122.3x |

Batches (section 4 gates; the client splits at 256 cases per request):

| Workload | Cases | Gate s | Persistent median s | Persistent p95 s | One-shot median s |
|---|---:|---:|---:|---:|---:|
| certificate/tableau-large | 8 | 0.3 | 0.974 | 1.833 | 0.717 |
| W1/conflict-check | 256 | 0.5 | 0.621 | 0.852 | 0.680 |
| W3/definitions | 2048 | 1.0 | 2.306 | 4.820 | 1.769 |
| W3/bundle | 256 | 0.25 | 0.298 | 0.347 | 0.322 |
