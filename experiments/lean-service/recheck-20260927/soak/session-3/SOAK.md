# Lean service soak (stage 1, gate 1)

Commit `7f4e094`; AMD EPYC 7B12; load average [5.6396484375, 4.63720703125, 4.66455078125] at start and [5.24853515625, 4.787109375, 4.71923828125] after.

- 20000 requests (seed 20260929; 1-8 cases each, mixed modes {'check-certificate': 3313, 'english': 3314, 'evaluate': 3358, 'norms': 3455, 'order': 3287, 'route': 3273}) in 90.3 s on one process.
- Result mismatches against the one-shot executables: 0.
- Restarts: 0; recycling disabled.
- RSS at request 1,000: 95.0 MB; at the end: 99.9 MB; growth 5.17% (gate < 10%); peak 99.9 MB.
- Per-request latency at the client boundary after the first 100: p50 3.398 ms [3.339, 3.451], p95 9.625 ms [9.456, 9.776], p99 15.5 ms [14.654, 18.279], max 134.685 ms. First 100: p50 3.081 ms, p95 8.25 ms.
- Gate: **PASS**.

RSS samples (MB): 1000: 95.0, 2000: 94.9, 3000: 95.0, 4000: 94.9, 5000: 94.9, 6000: 94.9, 7000: 95.0, 8000: 94.9, 9000: 94.9, 10000: 95.0, 11000: 94.9, 12000: 94.9, 13000: 94.9, 14000: 94.9, 15000: 95.0, 16000: 99.9, 17000: 99.9, 18000: 99.9, 19000: 99.9, 20000: 99.9
