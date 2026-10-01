# Lean service latency recheck after protocol validation

Commit `7cbcfba`; the [full latency run](latency/LATENCY.md) used the frozen
workloads and sampling counts: 20 cold starts, 100 warmup calls, 400 persistent
calls per workload, and 30 repetitions per batch. It made no model calls.

This host was not quiet. It has 8 logical CPUs; one-minute load was 13.998 at
the start and 10.505 at the end (five-minute load 8.669 and 14.057). The
one-shot median for `certificate/tableau` was 318.668 ms, compared with
51.894 ms in the [previous recheck](../recheck-20260927/latency/LATENCY.md).
These measurements are retained as diagnostic evidence, not a Stage 1 gate pass.

The cold-start p95 upper 95% confidence bound was **631.785 ms**, above the
frozen **150 ms** limit. The 2,048-definition batch median was **2.306 s**,
above the frozen **1.0 s** limit. The other three batch medians also exceeded
their frozen limits under this load. No target was changed.

The quiet-host performance gate remains open. Closing it requires a full rerun
on a quiet machine or explicit exception acceptance under
`docs/spec/SEMANTICS-MIGRATION-PLAN.md` section 4.
