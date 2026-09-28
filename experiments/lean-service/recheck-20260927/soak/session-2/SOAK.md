# Lean service soak (stage 1, gate 1)

Commit `7f4e094`; AMD EPYC 7B12; load average [4.54345703125, 4.09912109375, 4.53955078125] at start and [4.62255859375, 4.27099609375, 4.5615234375] after.

- 20000 requests (seed 20260928; 1-8 cases each, mixed modes {'check-certificate': 3227, 'english': 3305, 'evaluate': 3283, 'norms': 3360, 'order': 3512, 'route': 3313}) in 79.6 s on one process.
- Result mismatches against the one-shot executables: 0.
- Restarts: 0; recycling disabled.
- RSS at request 1,000: 88.5 MB; at the end: 93.5 MB; growth 5.58% (gate < 10%); peak 93.5 MB.
- Per-request latency at the client boundary after the first 100: p50 2.967 ms [2.922, 3.008], p95 8.773 ms [8.63, 8.918], p99 13.737 ms [13.049, 14.928], max 116.092 ms. First 100: p50 2.978 ms, p95 9.051 ms.
- Gate: **PASS**.

RSS samples (MB): 1000: 88.5, 2000: 93.4, 3000: 93.5, 4000: 93.5, 5000: 93.5, 6000: 93.5, 7000: 93.5, 8000: 93.5, 9000: 93.5, 10000: 93.5, 11000: 93.5, 12000: 93.5, 13000: 93.5, 14000: 93.5, 15000: 93.5, 16000: 93.5, 17000: 93.5, 18000: 93.4, 19000: 93.5, 20000: 93.5
