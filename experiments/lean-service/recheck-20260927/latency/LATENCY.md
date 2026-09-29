# Lean service latency (stage 1)

Commit `7f4e094`; AMD EPYC 7B12, 8 logical CPUs; load average [3.40966796875, 4.47314453125, 5.05712890625] before, [3.61181640625, 4.2412109375, 4.87939453125] after; Python 3.14.7; full bench corpus.

Persistent: `LeanService.run(mode, [case])` on one warm `ve_service` process, timed at the Python boundary (JSON, IPC, supervision included). One-shot: one executable process per case, as ve-bench measured Lean. Bracketed values are 95% bootstrap intervals.

Cold start (spawn to handshake, n=20): p50 49.784 ms, p95 71.008 ms.

First 100 service requests are timed separately before workload sampling: {'n': 100, 'p50_ms': 0.926, 'p50_ci_ms': [0.872, 1.022], 'p95_ms': 27.053, 'p95_ci_ms': [2.195, 30.6], 'p99_ms': 32.919, 'p99_ci_ms': [27.072, 35.025], 'max_ms': 35.025}.

| Workload | Mode | Persistent p50 ms | Persistent p95 ms | Persistent p99 ms | One-shot p50 ms | One-shot p95 ms | p50 speedup |
|---|---|---:|---:|---:|---:|---:|---:|
| certificate/tableau | check-certificate | 1.001 [0.973, 1.038] | 1.452 [1.405, 1.555] | 1.726 [1.58, 2.033] | 51.894 | 60.134 | 51.8x |
| certificate/tableau-large | check-certificate | 24.934 [24.499, 25.446] | 32.095 [30.91, 35.252] | 44.275 [37.926, 53.941] | 63.471 | 78.096 | 2.5x |
| certificate/closure | check-certificate | 1.369 [1.333, 1.411] | 1.924 [1.841, 2.03] | 2.338 [2.067, 2.664] | 58.854 | 71.766 | 43.0x |
| certificate/order-farkas | order | 1.129 [1.065, 1.187] | 1.963 [1.804, 2.08] | 2.403 [2.116, 2.501] | 56.575 | 65.543 | 50.1x |
| finite-model/evaluation | evaluate | 1.224 [1.167, 1.289] | 2.649 [2.363, 3.258] | 4.255 [3.384, 5.234] | 52.341 | 71.827 | 42.8x |
| W1/norm-elaboration | norms | 0.724 [0.693, 0.762] | 1.134 [1.072, 1.216] | 1.439 [1.288, 1.535] | 51.926 | 63.487 | 71.7x |
| W1/conflict-check | norms | 1.591 [1.565, 1.62] | 2.211 [2.116, 2.35] | 2.773 [2.445, 2.991] | 48.98 | 53.289 | 30.8x |
| W3/definitions | route | 1.563 [1.468, 1.654] | 3.401 [3.004, 3.749] | 4.387 [3.869, 6.647] | 60.326 | 73.035 | 38.6x |
| W3/bundle | route | 1.512 [1.467, 1.546] | 1.954 [1.902, 2.002] | 2.221 [2.095, 2.439] | 48.735 | 57.059 | 32.2x |
| English/parse | english | 1.027 [0.983, 1.071] | 1.589 [1.519, 1.751] | 2.069 [1.808, 2.483] | 61.054 | 74.154 | 59.4x |
| English/admission | english | 1.003 [0.959, 1.052] | 1.75 [1.597, 1.987] | 2.124 [2.044, 2.347] | 58.963 | 101.362 | 58.8x |

Batches (section 4 gates; the client splits at 256 cases per request):

| Workload | Cases | Gate s | Persistent median s | Persistent p95 s | One-shot median s |
|---|---:|---:|---:|---:|---:|
| certificate/tableau-large | 8 | 0.3 | 0.213 | 0.238 | 0.184 |
| W1/conflict-check | 256 | 0.5 | 0.203 | 0.242 | 0.226 |
| W3/definitions | 2048 | 1.0 | 1.345 | 1.581 | 1.037 |
| W3/bundle | 256 | 0.25 | 0.189 | 0.241 | 0.208 |
