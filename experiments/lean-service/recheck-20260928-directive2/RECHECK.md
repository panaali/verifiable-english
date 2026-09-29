# Lean service latency after design directive 2

The [full latency run](latency/LATENCY.md) measured commit `a1d879f` (schema-driven
response validation, the parallel pool and the corrected cold-start timing) with the
frozen workloads and sampling counts: 20 cold starts, 100 warmup calls, 400 persistent
calls per workload and 30 repetitions per batch. Every persistent, pooled and one-shot
result matched its reference; zero restarts and retries. No model calls were made.

Two changes since the [previous record](../recheck-20260928-response/RECHECK.md):

* **Cold-start timing.** Previously, the first of the 20 cold starts also included the
  client's one-time build check, a SHA-256 of the 176 MB executable (about 145 ms). After
  a rebuild it also included reading that file from disk. With 20 samples, that single
  start was the p95 upper bound in every earlier record, for example 1,677.538 ms against
  a 132.714 ms p50. The build check is now timed separately (143.191 ms, once per client
  process, cached by file identity). The cold starts are spawn to handshake, as the
  harness has always defined them.
* **Batches on the pool.** `LeanServicePool` now splits a batch into at least one
  request per process and answers the requests in parallel. The results and the
  earliest error are those of one process. Batches are timed on one process and on
  `LeanServicePool(2)`, the section-4 IDE footprint. The gate figure is the pool's.

| Gate | Target | Measured (95% upper bound) | Status |
|---|---|---|---|
| Cold start, spawn to handshake | ≤ 150 ms | p95 45.002 ms (45.594) | met |
| Per call, ordinary workloads | median ≤ 5 ms, p95 ≤ 20 ms | max p50 1.705 (1.751) ms, max p95 2.573 (2.673) ms | met |
| Large certificate (2,047 nodes) | p95 ≤ 200 ms | p95 48.865 (50.497) ms | met |
| 2,048 definitions | ≤ 1.0 s | pool median 0.884 s (0.917); one process 1.253 s | met on the pool |
| 256 bundles | ≤ 0.25 s | pool median 0.161 s (0.168); one process 0.198 s | met |
| 256 conflicts | ≤ 0.5 s | pool median 0.155 s (0.160); one process 0.200 s | met |
| 8 large certificates | ≤ 0.3 s | pool median 0.195 s (0.205); one process 0.256 s | met |

**The host was not quiet.** It had 8 logical CPUs, and the one-minute load was 4.36
before and 4.67 after (five-minute load 5.36 and 5.08). Every numerical target is met
on the upper bounds under this contention. The quiet-machine condition in Section 4 of
`docs/spec/SEMANTICS-MIGRATION-PLAN.md` is still formally open. It can be closed by a
quiet-host rerun (`tools/lean_service_latency.py`, unchanged sampling) or by explicit
acceptance of this contended run by the DRI.
