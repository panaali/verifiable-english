# Batch 18 public outcome comparison

The A/B recording covers 100,410 records at base `ffb3155a5` (the merge base with `main`) and the code head
named in [REPORT.md](REPORT.md): every corpus of `tools/lean_first_diff.py` (the probe matrix and the
conformance files under the `python` and `lean` settings, the pilots, the readings, discourse, rights, quantity,
norm-defaults and document corpora). Since this batch no setting selects an authority, so the head's `python`
rows are Lean's answers; they equal the base's Python-authority rows on every case. The saved comparison is
[`evidence/ab.json`](evidence/ab.json), the recordings `evidence/base-ab.jsonl.gz` and `evidence/head-ab.jsonl.gz`.

**100,399 records are identical. 11 are unavailable on both sides with identical outputs.** No verdict, wording,
order or availability changes.

The first head recording stopped two UDHR whole-document pilots at the recorder's 600 s wall-clock limit
where the base had answered (`evidence/ab-initial.json`, `evidence/head-ab-initial.jsonl.gz`). The document takes
520 to 620 s on this host depending on load, under both revisions: alone, the base took 586 s and the head
621 s; run at the same time, the base took 523.5 s and the head 519.5 s, with byte-identical output. Re-recorded
on both sides at once with one worker (`docs/lean-first/b16f/splice_recording.py pilots`), one of the two stops at
600 s on both sides and the other answers on both (`evidence/pilot-rerun.json`); those rows are spliced into both
recordings. The recorder's limit, not the batch, decides them.

| Row | Class | Change | Records | Ruling |
|---|---|---|---:|---|
| U1 | `unavailable` (both sides, identical outputs) | 8 constitution-pilot companion documents answer the same pre-existing `ReadingsConstruction` `CheckerUnavailable` at base and head, and 3 UDHR whole-document pilots stop at the recorder's 600 s limit on both sides. Listed in [`DELTA.json`](DELTA.json). | 11 | SIGNED by standing ruling R7 (DRI-RULINGS.md) |
| T1 | trust budget | Trusted V +34 over the base, re-measured on the final HEAD with `tools/trust_map.py`: `VE/Route/MeteredTrace.lean` +30 (the explanation's `Trace`, `Row`, `Trace.rows`, `Trace.rowsOf`, `Row.json`, `Trace.json`), `ResponseShape/Skeletons.lean` +3 (`metered`), `VE/Service/Protocol.lean` +2 (the `metered` mode), `ResponseShape/Schemas.lean` +1 (its file); S −3 (`VE/Limits.lean`'s two S limits replace three S copies); K +0. Exercised by `tests/test_metered_lean.py` (every family's trace against Python's), `tests/test_stage2_evaluation.py::test_traced_evaluation_matches_python` and the relay gate's 646 `service:metered` mutants; the ties pass is a FOLLOW-UPS.md row. | — | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| L1 | latency (section 4: use-case harnesses) | `usecases/agent-policy/check.py base` is 1.42× the base wall (median of three paired runs: 101.2 s → 143.8 s; child CPU 1.18×) with identical output, over the harness row's 1.25×. Its evaluations, 8,169 sequential calls, were Python's in-process evaluator and are now one Lean service request each (about 1.5 to 2.7 ms: Lean re-decodes the environment of every case, which the handle only saves re-sending). The whole harness (base and mutants parts) measured 1.23× at the same load, UDHR 0.94× and eligibility 0.72× (`evidence/latency.json`). The fix is the unbuilt half of F2: Lean keeps the decoded environment of a handle. | — | DRI signature needed (L52: the reason this item stops) |
