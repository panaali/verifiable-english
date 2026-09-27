# Lean service latency (stage 1)

Commit `04aac0c`; AMD EPYC 7B12, 8 logical CPUs; load average [7.24560546875, 6.1416015625, 5.8779296875] before, [6.0263671875, 6.10791015625, 5.8994140625] after; Python 3.14.7; full bench corpus.

Persistent: `LeanService.run(mode, [case])` on one warm `ve_service` process, timed at the Python boundary (JSON, IPC, supervision included). One-shot: one executable process per case, as ve-bench measured Lean. Bracketed values are 95% bootstrap intervals.

Cold start (spawn to handshake, n=20): p50 53.827 ms, p95 91.265 ms.

| Workload | Mode | Persistent p50 ms | Persistent p95 ms | One-shot p50 ms | One-shot p95 ms | p50 speedup |
|---|---|---:|---:|---:|---:|---:|
| certificate/tableau | check-certificate | 0.965 [0.945, 0.985] | 1.447 [1.385, 1.537] | 84.47 | 115.986 | 87.5x |
| certificate/tableau-large | check-certificate | 30.892 [28.784, 33.021] | 45.652 [44.265, 47.597] | 78.438 | 115.6 | 2.5x |
| certificate/closure | check-certificate | 1.281 [1.252, 1.325] | 2.428 [2.239, 2.616] | 85.985 | 98.233 | 67.1x |
| certificate/order-farkas | order | 1.246 [1.211, 1.284] | 1.996 [1.903, 2.172] | 69.319 | 109.075 | 55.6x |
| finite-model/evaluation | evaluate | 0.775 [0.757, 0.787] | 1.496 [1.36, 1.627] | 65.386 | 90.044 | 84.4x |
| W1/norm-elaboration | norms | 0.618 [0.593, 0.648] | 1.509 [1.33, 1.711] | 79.552 | 92.426 | 128.7x |
| W1/conflict-check | norms | 1.699 [1.657, 1.753] | 2.745 [2.64, 2.95] | 75.587 | 84.26 | 44.5x |
| W3/definitions | route | 1.391 [1.352, 1.449] | 4.857 [4.494, 5.198] | 81.108 | 131.487 | 58.3x |
| W3/bundle | route | 1.659 [1.622, 1.732] | 2.816 [2.653, 3.007] | 84.114 | 104.575 | 50.7x |
| English/parse | english | 0.597 [0.59, 0.602] | 1.183 [1.093, 1.251] | 55.468 | 82.553 | 92.9x |
| English/admission | english | 0.647 [0.626, 0.675] | 1.448 [1.285, 1.511] | 56.129 | 82.51 | 86.8x |

Batches (section 4 gates; the client splits at 256 cases per request):

| Workload | Cases | Gate s | Persistent median s | Persistent p95 s | One-shot median s |
|---|---:|---:|---:|---:|---:|
| certificate/tableau-large | 8 | 0.3 | 0.343 | 0.474 | 0.333 |
| W1/conflict-check | 256 | 0.5 | 0.315 | 0.353 | 0.368 |
| W3/definitions | 2048 | 1.0 | 2.227 | 2.319 | 1.937 |
| W3/bundle | 256 | 0.25 | 0.322 | 0.373 | 0.241 |
