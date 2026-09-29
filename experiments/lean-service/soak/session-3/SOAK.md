# Lean service soak (stage 1, gate 1)

Commit `9eaec60`; AMD EPYC 7B12; load average [4.2919921875, 4.46044921875, 4.97900390625] at start and [4.26123046875, 4.419921875, 4.931640625] after.

- 20000 requests (seed 20260929; 1-8 cases each, mixed modes {'check-certificate': 3313, 'english': 3314, 'evaluate': 3358, 'norms': 3455, 'order': 3287, 'route': 3273}) in 58.5 s on one process.
- Result mismatches against the one-shot executables: 0.
- Restarts: 0; recycling disabled.
- RSS at request 1,000: 95.2 MB; at the end: 100.1 MB; growth 5.15% (gate < 10%); peak 100.1 MB.
- Per-request latency at the client boundary after the first 100: p50 2.244 ms [2.21, 2.283], p95 6.246 ms [6.138, 6.356], p99 10.529 ms [9.546, 12.525], max 73.772 ms. First 100: p50 1.705 ms, p95 4.381 ms.
- Gate: **PASS**.

RSS samples (MB): 1000: 95.2, 2000: 95.2, 3000: 95.2, 4000: 95.2, 5000: 95.2, 6000: 95.2, 7000: 95.2, 8000: 95.2, 9000: 95.2, 10000: 95.2, 11000: 95.2, 12000: 95.2, 13000: 95.2, 14000: 95.2, 15000: 95.2, 16000: 100.1, 17000: 100.1, 18000: 100.1, 19000: 100.1, 20000: 100.1
