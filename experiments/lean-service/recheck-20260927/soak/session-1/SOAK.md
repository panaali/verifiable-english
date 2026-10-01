# Lean service soak (stage 1, gate 1)

Commit `7f4e094`; AMD EPYC 7B12; load average [3.2529296875, 3.7099609375, 4.517578125] at start and [3.63427734375, 3.7373046875, 4.4697265625] after.

- 20000 requests (seed 20260927; 1-8 cases each, mixed modes {'check-certificate': 3346, 'english': 3297, 'evaluate': 3389, 'norms': 3260, 'order': 3339, 'route': 3369}) in 62.5 s on one process.
- Result mismatches against the one-shot executables: 0.
- Restarts: 0; recycling disabled.
- RSS at request 1,000: 95.2 MB; at the end: 100.1 MB; growth 5.16% (gate < 10%); peak 100.1 MB.
- Per-request latency at the client boundary after the first 100: p50 2.387 ms [2.349, 2.42], p95 6.486 ms [6.393, 6.576], p99 10.748 ms [9.966, 12.344], max 101.189 ms. First 100: p50 2.104 ms, p95 6.144 ms.
- Gate: **PASS**.

RSS samples (MB): 1000: 95.2, 2000: 95.2, 3000: 95.2, 4000: 95.2, 5000: 100.1, 6000: 100.1, 7000: 100.1, 8000: 100.1, 9000: 100.1, 10000: 100.1, 11000: 100.1, 12000: 100.1, 13000: 100.1, 14000: 100.1, 15000: 100.1, 16000: 100.1, 17000: 100.1, 18000: 100.1, 19000: 99.5, 20000: 100.1
