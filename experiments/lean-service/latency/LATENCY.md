# Lean service latency (stage 1)

Commit `9eaec60`; AMD EPYC 7B12, 8 logical CPUs; load average [3.1513671875, 4.35595703125, 5.29052734375] before, [3.76904296875, 4.1103515625, 5.0244140625] after; Python 3.14.7; full bench corpus.

Persistent: `LeanService.run(mode, [case])` on one warm `ve_service` process, timed at the Python boundary (JSON, IPC, supervision included). One-shot: one executable process per case, as ve-bench measured Lean. Bracketed values are 95% bootstrap intervals.

Cold start (spawn to handshake, n=20): p50 75.466 ms, p95 151.561 ms.

First 100 service requests are timed separately before workload sampling: {'n': 100, 'p50_ms': 1.148, 'p50_ci_ms': [0.975, 1.359], 'p95_ms': 31.302, 'p95_ci_ms': [2.652, 34.318], 'p99_ms': 35.826, 'p99_ci_ms': [31.2, 36.602], 'max_ms': 36.602}.

| Workload | Mode | Persistent p50 ms | Persistent p95 ms | Persistent p99 ms | One-shot p50 ms | One-shot p95 ms | p50 speedup |
|---|---|---:|---:|---:|---:|---:|---:|
| certificate/tableau | check-certificate | 1.118 [1.087, 1.175] | 2.217 [2.062, 2.388] | 2.907 [2.469, 3.232] | 87.879 | 96.323 | 78.6x |
| certificate/tableau-large | check-certificate | 35.501 [34.87, 36.262] | 46.529 [44.95, 50.645] | 57.985 [52.951, 60.365] | 111.334 | 140.624 | 3.1x |
| certificate/closure | check-certificate | 1.878 [1.787, 1.972] | 3.521 [3.261, 3.705] | 4.434 [3.916, 5.007] | 117.41 | 145.416 | 62.5x |
| certificate/order-farkas | order | 1.969 [1.908, 2.039] | 3.25 [3.09, 3.689] | 4.557 [3.922, 6.02] | 109.522 | 132.607 | 55.6x |
| finite-model/evaluation | evaluate | 1.411 [1.339, 1.51] | 3.58 [3.281, 4.198] | 5.044 [4.409, 5.465] | 185.453 | 701.551 | 131.4x |
| W1/norm-elaboration | norms | 0.869 [0.816, 0.919] | 1.76 [1.572, 1.968] | 2.584 [2.132, 2.914] | 63.901 | 78.121 | 73.5x |
| W1/conflict-check | norms | 1.519 [1.456, 1.587] | 2.497 [2.295, 2.624] | 3.38 [2.736, 3.825] | 57.965 | 68.072 | 38.2x |
| W3/definitions | route | 1.482 [1.449, 1.546] | 2.326 [2.178, 2.527] | 2.907 [2.558, 3.034] | 59.745 | 67.359 | 40.3x |
| W3/bundle | route | 1.62 [1.593, 1.656] | 2.362 [2.201, 2.475] | 3.1 [2.72, 4.555] | 57.761 | 74.814 | 35.7x |
| English/parse | english | 0.695 [0.657, 0.725] | 1.258 [1.156, 1.412] | 1.619 [1.444, 1.757] | 61.463 | 70.384 | 88.4x |
| English/admission | english | 0.827 [0.79, 0.851] | 1.346 [1.283, 1.401] | 1.823 [1.497, 2.202] | 62.045 | 71.8 | 75.0x |

Batches (section 4 gates; the client splits at 256 cases per request):

| Workload | Cases | Gate s | Persistent median s | Persistent p95 s | One-shot median s |
|---|---:|---:|---:|---:|---:|
| certificate/tableau-large | 8 | 0.3 | 0.310 | 0.361 | 0.329 |
| W1/conflict-check | 256 | 0.5 | 0.186 | 0.216 | 0.224 |
| W3/definitions | 2048 | 1.0 | 1.197 | 1.291 | 1.094 |
| W3/bundle | 256 | 0.25 | 0.210 | 0.248 | 0.237 |
