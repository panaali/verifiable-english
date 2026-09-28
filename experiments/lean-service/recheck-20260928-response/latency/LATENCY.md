# Lean service latency (stage 1)

Commit `c4d4430`; AMD EPYC 7B12, 8 logical CPUs; load average [11.25390625, 10.64013671875, 9.8701171875] before, [10.2744140625, 10.642578125, 10.16455078125] after; Python 3.14.7; full bench corpus.

Persistent: `LeanService.run(mode, [case])` on one warm `ve_service` process, timed at the Python boundary (JSON, IPC, supervision included). One-shot: one executable process per case, as ve-bench measured Lean. Bracketed values are 95% bootstrap intervals.

Cold start (spawn to handshake, n=20): p50 132.714 ms, p95 249.73 ms.

First 100 service requests are timed separately before workload sampling: {'n': 100, 'p50_ms': 1.664, 'p50_ci_ms': [1.512, 1.924], 'p95_ms': 59.563, 'p95_ci_ms': [5.499, 65.272], 'p99_ms': 65.685, 'p99_ci_ms': [59.574, 73.427], 'max_ms': 73.427}.

| Workload | Mode | Persistent p50 ms | Persistent p95 ms | Persistent p99 ms | One-shot p50 ms | One-shot p95 ms | p50 speedup |
|---|---|---:|---:|---:|---:|---:|---:|
| certificate/tableau | check-certificate | 1.646 [1.531, 1.736] | 4.398 [3.77, 5.099] | 6.088 [5.259, 7.535] | 148.698 | 216.828 | 90.3x |
| certificate/tableau-large | check-certificate | 69.48 [67.828, 71.544] | 138.682 [123.618, 149.629] | 189.961 [159.042, 228.66] | 175.644 | 247.29 | 2.5x |
| certificate/closure | check-certificate | 2.724 [2.465, 3.024] | 8.59 [7.525, 9.133] | 11.344 [9.905, 14.425] | 183.595 | 257.774 | 67.4x |
| certificate/order-farkas | order | 1.752 [1.633, 1.894] | 5.484 [4.903, 5.955] | 7.118 [6.308, 8.377] | 154.109 | 251.422 | 88.0x |
| finite-model/evaluation | evaluate | 2.006 [1.991, 2.043] | 4.802 [4.126, 5.266] | 6.581 [5.729, 10.661] | 174.04 | 226.849 | 86.8x |
| W1/norm-elaboration | norms | 1.09 [0.964, 1.184] | 4.353 [3.808, 4.567] | 5.627 [4.804, 6.688] | 174.062 | 240.018 | 159.7x |
| W1/conflict-check | norms | 2.348 [2.206, 2.464] | 6.126 [5.202, 7.191] | 10.476 [8.221, 13.203] | 173.542 | 273.2 | 73.9x |
| W3/definitions | route | 1.732 [1.537, 1.868] | 4.866 [4.19, 5.417] | 6.214 [5.488, 6.594] | 150.757 | 201.959 | 87.0x |
| W3/bundle | route | 1.532 [1.493, 1.564] | 3.186 [2.95, 3.922] | 5.033 [4.04, 6.022] | 109.669 | 159.283 | 71.6x |
| English/parse | english | 0.569 [0.563, 0.583] | 1.701 [1.391, 2.166] | 4.455 [2.921, 4.915] | 95.183 | 156.949 | 167.3x |
| English/admission | english | 0.57 [0.556, 0.59] | 2.503 [2.018, 3.662] | 4.329 [4.041, 6.338] | 125.613 | 173.361 | 220.4x |

Batches (section 4 gates; the client splits at 256 cases per request):

| Workload | Cases | Gate s | Persistent median s | Persistent p95 s | One-shot median s |
|---|---:|---:|---:|---:|---:|
| certificate/tableau-large | 8 | 0.3 | 0.685 | 0.877 | 0.550 |
| W1/conflict-check | 256 | 0.5 | 0.460 | 0.569 | 0.534 |
| W3/definitions | 2048 | 1.0 | 2.749 | 3.120 | 2.182 |
| W3/bundle | 256 | 0.25 | 0.383 | 0.522 | 0.381 |
