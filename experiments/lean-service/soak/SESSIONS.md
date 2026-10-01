# Lean service review follow-up: three independent soak sessions

Each session starts a fresh service process and sends 20,000 mixed-mode requests,
with a different deterministic request seed. The first 100 calls are reported
separately. Subsequent p50, p95 and p99 values have 95% bootstrap intervals in
the session files. All calls are timed at the Python client boundary.

| Session | Seed | Load at start / end (1 min) | Mismatches | Restarts | RSS growth from request 1,000 | p95 ms, upper 95% bound | p99 ms, upper 95% bound |
|---|---:|---:|---:|---:|---:|---:|---:|
| [1](session-1/SOAK.md) | 20260927 | 3.48 / 5.70 | 0 | 0 | 5.20% | 8.143 | 19.382 |
| [2](session-2/SOAK.md) | 20260928 | 4.85 / 4.48 | 0 | 0 | 5.24% | 6.710 | 11.484 |
| [3](session-3/SOAK.md) | 20260929 | 4.29 / 4.26 | 0 | 0 | 5.15% | 6.356 | 12.525 |

Total: 60,000 requests, zero result mismatches, zero restarts. Each session's
memory growth is below the 10% soak gate. The updated [full latency run](../latency/LATENCY.md)
uses 20 separate cold starts, reports its first 100 warmup calls separately,
samples 400 persistent calls per workload, and repeats each batch 30 times.
Its largest ordinary-call p50 upper bound is 2.039 ms and p95 upper bound is
4.198 ms; the 2,047-node certificate p95 upper bound is 50.645 ms. These are
below the 5, 20 and 200 ms targets, respectively.

**Measurement limitation:** The host was not quiet: one-minute load was
3.15–4.85 at the start of these runs on 8 logical CPUs, and rose as high as
5.70. These results show the targets passing under the observed contention,
but they do not satisfy the plan's literal quiet-machine condition. That
condition still needs a quiet host run or explicit gate acceptance.
