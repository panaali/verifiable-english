# Lean service latency after response schema validation

Commit `43c6bc7`. The [full latency run](latency/LATENCY.md) used the frozen
workloads and sampling counts: 20 cold starts, 100 warmup calls, 400 persistent
calls per workload, and 30 repetitions per batch. It made no model calls.

The host was busy: 8 logical CPUs and one-minute load 7.831 at the start and
8.432 at the end. This is diagnostic evidence, not a quiet-host gate pass.

The cold-start p95 upper 95% confidence bound was **354.248 ms** against the
frozen **150 ms** limit. The 2,048-definition batch median was **1.899 s**
against **1.0 s**. The 8 large-certificate median was **0.327 s** against
**0.3 s**, and the 256-bundle median was **0.317 s** against **0.25 s**.
The 256-conflict median was **0.296 s** against **0.5 s**. No target was changed.

The quiet-host performance gate remains open. Section 4 of
`docs/spec/SEMANTICS-MIGRATION-PLAN.md` requires a quiet-machine rerun or
explicit exception acceptance before the migration gate can pass.
