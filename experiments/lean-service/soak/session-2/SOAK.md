# Lean service soak (stage 1, gate 1)

Commit `9eaec60`; AMD EPYC 7B12; load average [4.84716796875, 4.56103515625, 5.07275390625] at start and [4.48291015625, 4.51025390625, 5.01806640625] after.

- 20000 requests (seed 20260928; 1-8 cases each, mixed modes {'check-certificate': 3227, 'english': 3305, 'evaluate': 3283, 'norms': 3360, 'order': 3512, 'route': 3313}) in 60.3 s on one process.
- Result mismatches against the one-shot executables: 0.
- Restarts: 0; recycling disabled.
- RSS at request 1,000: 94.1 MB; at the end: 99.0 MB; growth 5.24% (gate < 10%); peak 99.1 MB.
- Per-request latency at the client boundary after the first 100: p50 2.3 ms [2.266, 2.336], p95 6.61 ms [6.513, 6.71], p99 10.693 ms [9.989, 11.484], max 79.904 ms. First 100: p50 1.541 ms, p95 5.257 ms.
- Gate: **PASS**.

RSS samples (MB): 1000: 94.1, 2000: 99.0, 3000: 99.0, 4000: 99.0, 5000: 99.0, 6000: 99.0, 7000: 99.0, 8000: 99.0, 9000: 99.0, 10000: 99.0, 11000: 99.0, 12000: 99.1, 13000: 99.0, 14000: 99.0, 15000: 99.0, 16000: 99.0, 17000: 99.0, 18000: 99.0, 19000: 99.0, 20000: 99.0
