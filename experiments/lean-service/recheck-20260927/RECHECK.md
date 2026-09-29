# Lean service recheck on the corrected client

Commit `7f4e094`; AMD EPYC 7B12, 8 logical CPUs. All measurements use the
supervised Python client boundary. These records are kept as numerical evidence;
the Stage 1 quiet-machine performance gate remains open because the host was busy.
The [full fixture parity](parity/PARITY.md) is 16,556/16,556 identical to the
one-shot runners.

## Mixed-mode soak

Each [session](soak/session-1/SOAK.md) used a fresh process, 20,000 requests, a
distinct seed, and parity with the one-shot runners. Detailed results are in the
session directories.

| Session | Seed | One-minute load at start / end | Mismatches | Restarts | RSS growth from request 1,000 | p95 upper 95% bound |
|---|---:|---:|---:|---:|---:|---:|
| [1](soak/session-1/SOAK.md) | 20260927 | 3.25 / 3.63 | 0 | 0 | 5.16% | 6.576 ms |
| [2](soak/session-2/SOAK.md) | 20260928 | 4.54 / 4.62 | 0 | 0 | 5.58% | 8.918 ms |
| [3](soak/session-3/SOAK.md) | 20260929 | 5.64 / 5.25 | 0 | 0 | 5.17% | 9.776 ms |

The numerical soak conditions pass over 60,000 requests: zero mismatches, zero
restarts, and less than 10% RSS growth in every session.

## Latency

The [full latency run](latency/LATENCY.md) used 20 separate cold starts, 100
separately reported warmup calls, 400 persistent calls per workload, and 30 batch
repetitions. One-minute host load was 3.41 at start and 3.61 at end.

- The largest ordinary-call p50 upper bound was 1.654 ms and p95 upper bound was
  3.749 ms, below the 5 and 20 ms targets. The 2,047-node certificate p95 upper
  bound was 35.252 ms, below 200 ms.
- Three batch medians passed their frozen targets. The 2,048-definition batch
  median was **1.345 s**, above its **1.0 s** target.
- Cold-start p95 was 71.008 ms, with an upper 95% confidence bound of
  **217.529 ms**, above the **150 ms** gate when the plan's upper-bound rule is
  applied.

The quiet-host condition and the two latency bounds above are not satisfied by
this measurement. A quiet-host rerun or explicit gate acceptance is required;
neither is recorded here. No frozen target has been changed.
