# Lean service latency after response validation fixes

The [full latency run](latency/LATENCY.md) measured commit `c4d4430` with the
frozen workloads and sampling counts: 20 cold starts, 100 warmup calls, 400
persistent calls per workload, and 30 repetitions per batch. Every persistent
result matched its one-shot reference. No model calls were made.

The host was busy throughout: eight logical CPUs, with one-minute load 11.254
before and 10.274 after. This run is diagnostic evidence, not a quiet-host gate
pass. The cold-start p95 upper 95% confidence bound was **1,677.538 ms** against
the frozen **150 ms** limit. The 2,048-definition batch median was **2.749 s**
against **1.0 s**. The eight large-certificate median was **0.685 s** against
**0.3 s**, and the 256-bundle median was **0.383 s** against **0.25 s**. The
256-conflict median was **0.460 s** against **0.5 s**. No target was changed.

The quiet-host performance gate remains open. Section 4 of
`docs/spec/SEMANTICS-MIGRATION-PLAN.md` requires a quiet-machine rerun or
explicit exception acceptance before the migration gate can pass.
