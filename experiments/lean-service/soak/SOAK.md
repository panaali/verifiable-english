# Lean service soak (stage 1, gate 1)

Commit `04aac0c`; AMD EPYC 7B12; load average [5.32421875, 5.8466796875, 5.82373046875] at start.

- 20000 requests (1-8 cases each, mixed modes {'check-certificate': 3346, 'english': 3297, 'evaluate': 3389, 'norms': 3260, 'order': 3339, 'route': 3369}) in 70.5 s on one process.
- Result mismatches against the one-shot executables: 0.
- Restarts: 0; recycling disabled.
- RSS at request 1,000: 96.1 MB; at the end: 101.0 MB; growth 5.11% (gate < 10%); peak 101.0 MB.
- Per-request latency at the client boundary after the first 100: p50 2.574 ms [2.527, 2.615], p95 7.848 ms [7.731, 7.96], p99 12.009 ms, max 100.593 ms. First 100: p50 2.423 ms, p95 8.214 ms.
- Gate: **PASS**.

RSS samples (MB): 1000: 96.1, 2000: 96.1, 3000: 96.0, 4000: 96.0, 5000: 101.0, 6000: 101.0, 7000: 101.0, 8000: 101.0, 9000: 101.0, 10000: 101.0, 11000: 101.0, 12000: 101.0, 13000: 101.0, 14000: 101.0, 15000: 101.0, 16000: 100.9, 17000: 100.9, 18000: 101.0, 19000: 100.3, 20000: 101.0
