# Lean service soak (stage 1, gate 1)

Commit `9eaec60`; AMD EPYC 7B12; load average [3.4814453125, 4.02197265625, 4.97509765625] at start and [5.69921875, 4.65185546875, 5.12158203125] after.

- 20000 requests (seed 20260927; 1-8 cases each, mixed modes {'check-certificate': 3346, 'english': 3297, 'evaluate': 3389, 'norms': 3260, 'order': 3339, 'route': 3369}) in 70.5 s on one process.
- Result mismatches against the one-shot executables: 0.
- Restarts: 0; recycling disabled.
- RSS at request 1,000: 94.5 MB; at the end: 99.4 MB; growth 5.20% (gate < 10%); peak 99.4 MB.
- Per-request latency at the client boundary after the first 100: p50 2.579 ms [2.534, 2.624], p95 8.032 ms [7.89, 8.143], p99 14.092 ms [12.83, 19.382], max 105.357 ms. First 100: p50 3.183 ms, p95 9.753 ms.
- Gate: **PASS**.

RSS samples (MB): 1000: 94.5, 2000: 94.5, 3000: 94.4, 4000: 94.4, 5000: 99.4, 6000: 99.4, 7000: 99.4, 8000: 99.4, 9000: 99.4, 10000: 99.4, 11000: 99.4, 12000: 99.4, 13000: 99.4, 14000: 99.4, 15000: 99.4, 16000: 99.3, 17000: 99.3, 18000: 99.4, 19000: 98.7, 20000: 99.4
