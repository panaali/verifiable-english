# Lean service latency after design directive 3

The [full latency run](latency/LATENCY.md) measured commit `eb97efad`. That commit binds every result to its case
by position and SHA-256 (protocol 2) and leaves binding-preserving content to the service (the threat model in
`docs/spec/lean-service.md`). The run used the frozen workloads and sampling counts: 20 cold starts, 100 warmup
calls, 400 persistent calls per workload and 30 repetitions per batch. Every persistent, pooled and one-shot result
matched its reference, with zero restarts and retries over 4,841 single-process and 434 pooled requests. No model
calls were made.

| Gate | Target | Measured (95% upper bound) | Status |
|---|---|---|---|
| Cold start, spawn to handshake | ≤ 150 ms | p95 64.124 ms (64.874) | met |
| Per call, ordinary workloads | median ≤ 5 ms, p95 ≤ 20 ms | max p50 1.622 (1.655) ms, max p95 2.326 (2.390) ms | met |
| Large certificate (2,047 nodes) | p95 ≤ 200 ms | p95 54.94 (56.678) ms | met |
| 2,048 definitions | ≤ 1.0 s | pool median 0.938 s (0.974); one process 1.408 s | met on the pool |
| 256 bundles | ≤ 0.25 s | pool median 0.162 s (0.170) | met |
| 256 conflicts | ≤ 0.5 s | pool median 0.150 s (0.153) | met |
| 8 large certificates | ≤ 0.3 s | pool median 0.174 s (0.185) | met |

## Contention, measured

The previous records could only report the load average. The harness now reads `/proc/<pid>/schedstat` of the
service process and of the client thread around every persistent call, outside the timed region. From that it
reports the service's on-CPU time, and the runqueue wait: the time the service or the client was runnable but
waiting for a CPU. Runqueue wait is the part of a latency that other load on the host adds.

The host was busy: 16 logical CPUs, one-minute load 11.0 before and 10.5 after. Even so, the median runqueue wait
of every workload was 0.0 ms. Its p95 was at most 0.716 ms for the ordinary workloads and 2.643 ms for the large
certificate. So at the median the measured figures are what a quiet host would give. The quiet-machine wording in
Section 4 of `docs/spec/SEMANTICS-MIGRATION-PLAN.md` has no measurable definition. This measurement is the evidence
for accepting this run, which is the DRI's decision. Without that acceptance, a rerun of
`tools/lean_service_latency.py` on an idle host remains the formal route.

## What the binding costs

The first run after the binding change (`d7683faf`) put the 2,048-definition batch at a 1.155 s pool median. Every
figure below is from an A/B run that alternated with the `ecce438` stack (its client and its service) under the
same load. The three causes, per 256-case chunk (454 KB):

* the service ran every runner twice, because `response` computed the results for its counts and again for its
  bound results (fixed in `eb97efad`);
* the service split the cases a second time for their digests, at about 42 ms (fixed in `d7683faf` by one byte
  pass);
* the client split the case texts again, at about 25 ms (fixed in `d7683faf`: `run()` passes the texts it already
  has).

What remains is the price of binding. SHA-256 in Lean runs at about 32 MB/s, which is about 14 ms per chunk. The
client's bound-result validation costs 8.5 ms per chunk, against 6.2 ms before. The response is also slightly
larger. In the alternating A/B at load 10 to 12, the pool medians of the definitions batch were 0.87–1.09 s for
`ecce438` and 0.94–1.25 s for this stack. The bundle batch medians were 0.16 s and 0.17–0.18 s.
