# Lean service latency (stage 1)

Commit `a1d879f`; AMD EPYC 7B12, 8 logical CPUs; load average [4.359375, 5.36083984375, 8.24169921875] before, [4.6650390625, 5.0751953125, 7.55810546875] after; Python 3.14.7; full bench corpus.

Persistent: `LeanService.run(mode, [case])` on one warm `ve_service` process, timed at the Python boundary (JSON, IPC, supervision included). One-shot: one executable process per case, as ve-bench measured Lean. Bracketed values are 95% bootstrap intervals.

Build check (SHA-256 of the executable, once per client process, not in the cold starts): 143.191 ms.

Cold start (spawn to handshake, n=20): p50 42.551 ms [41.469, 43.778], p95 45.002 ms [43.912, 45.594], max 45.594 ms.

First 100 service requests are timed separately before workload sampling: {'n': 100, 'p50_ms': 1.366, 'p50_ci_ms': [1.247, 1.521], 'p95_ms': 28.195, 'p95_ci_ms': [2.462, 35.397], 'p99_ms': 41.684, 'p99_ci_ms': [28.258, 42.902], 'max_ms': 42.902}.

| Workload | Mode | Persistent p50 ms | Persistent p95 ms | Persistent p99 ms | One-shot p50 ms | One-shot p95 ms | p50 speedup |
|---|---|---:|---:|---:|---:|---:|---:|
| certificate/tableau | check-certificate | 1.249 [1.207, 1.288] | 1.851 [1.754, 2.004] | 2.407 [2.063, 3.23] | 49.726 | 53.272 | 39.8x |
| certificate/tableau-large | check-certificate | 41.001 [40.63, 41.698] | 48.865 [47.73, 50.497] | 79.745 [51.283, 87.733] | 65.06 | 94.578 | 1.6x |
| certificate/closure | check-certificate | 1.359 [1.339, 1.394] | 2.008 [1.918, 2.088] | 2.203 [2.115, 2.382] | 49.239 | 55.302 | 36.2x |
| certificate/order-farkas | order | 0.763 [0.758, 0.774] | 1.677 [1.621, 1.783] | 2.146 [1.851, 2.295] | 50.181 | 54.497 | 65.8x |
| finite-model/evaluation | evaluate | 0.868 [0.848, 0.903] | 1.405 [1.364, 1.505] | 1.832 [1.514, 2.193] | 51.664 | 55.761 | 59.5x |
| W1/norm-elaboration | norms | 0.974 [0.925, 1.009] | 1.561 [1.501, 1.647] | 1.813 [1.696, 2.108] | 58.229 | 74.239 | 59.8x |
| W1/conflict-check | norms | 1.705 [1.659, 1.751] | 2.573 [2.406, 2.673] | 3.081 [2.746, 3.211] | 56.862 | 63.534 | 33.4x |
| W3/definitions | route | 1.376 [1.364, 1.389] | 2.146 [2.063, 2.258] | 2.494 [2.346, 2.771] | 50.754 | 57.927 | 36.9x |
| W3/bundle | route | 1.5 [1.439, 1.546] | 2.087 [1.989, 2.15] | 2.284 [2.215, 2.424] | 49.208 | 55.853 | 32.8x |
| English/parse | english | 0.673 [0.655, 0.691] | 1.187 [1.146, 1.253] | 1.483 [1.312, 1.754] | 51.835 | 55.872 | 77.0x |
| English/admission | english | 0.724 [0.703, 0.751] | 1.193 [1.146, 1.277] | 1.495 [1.369, 1.591] | 53.99 | 57.383 | 74.6x |

Batches (section 4 gates; the client splits at 256 cases per request, and the pool into at least one request per process):

| Workload | Cases | Gate s | Pool of 2 median s | Pool of 2 p95 s | One process median s | One process p95 s | One-shot median s |
|---|---:|---:|---:|---:|---:|---:|---:|
| certificate/tableau-large | 8 | 0.3 | 0.195 [0.178, 0.205] | 0.236 | 0.256 | 0.380 | 0.229 |
| W1/conflict-check | 256 | 0.5 | 0.155 [0.151, 0.16] | 0.171 | 0.200 | 0.244 | 0.209 |
| W3/definitions | 2048 | 1.0 | 0.884 [0.873, 0.917] | 0.986 | 1.253 | 1.334 | 0.942 |
| W3/bundle | 256 | 0.25 | 0.161 [0.157, 0.168] | 0.202 | 0.198 | 0.307 | 0.197 |
