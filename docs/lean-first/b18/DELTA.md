# Batch 18 public outcome comparison

The A/B recording covers 100,410 records at base `ffb3155a5` (the merge base with `main`) and the code head
named in [REPORT.md](REPORT.md): every corpus of `tools/lean_first_diff.py` (the probe matrix and the
conformance files under the `python` and `lean` settings, the pilots, the readings, discourse, rights, quantity,
norm-defaults and document corpora). Since this batch no setting selects an authority, so the head's `python`
rows are Lean's answers; they equal the base's Python-authority rows on every case. The saved comparison is
[`evidence/ab.json`](evidence/ab.json), the recordings `evidence/base-ab.jsonl.gz` and `evidence/head-ab.jsonl.gz`.
After the DRI note's speed fix (F7, REPORT.md), every corpus but the pilots was re-recorded on the code head
`450a7101b`: all 99,847 records equal the base's ([`evidence/ab-f7.json`](evidence/ab-f7.json)).

**100,398 records are identical. 12 are unavailable on both sides with identical outputs.** No verdict, wording,
order or availability changes.

Two head recordings each stopped UDHR whole-document pilots at the recorder's 600 s wall-clock limit where
the base had answered: two in the first (before the transport caches of `1ffcda5f`), one in the final one
(`evidence/ab-initial.json`, `evidence/head-ab-initial.jsonl.gz`). The document takes 520 to 620 s on this host
depending on load, under both revisions: alone, the base took 586 s and the head 621 s; run at the same time, the
base took 523.5 s and the head 519.5 s, with byte-identical output. Each was re-recorded on both sides at once with
one worker (`docs/lean-first/b16f/splice_recording.py pilots`) and behaved alike on both sides
(`evidence/pilot-rerun.json`); those rows are spliced into both recordings. The recorder's limit, not the batch,
decides them.

| Row | Class | Change | Records | Ruling |
|---|---|---|---:|---|
| U1 | `unavailable` (both sides, identical outputs) | 8 constitution-pilot companion documents answer the same pre-existing `ReadingsConstruction` `CheckerUnavailable` at base and head, and 4 UDHR whole-document pilots stop at the recorder's 600 s limit on both sides. Listed in [`DELTA.json`](DELTA.json). | 12 | SIGNED by standing ruling R7 (DRI-RULINGS.md) |
| T1 | trust budget | Trusted V +121 over the base, re-measured on the final HEAD with `tools/trust_map.py`: `VE/Service/Protocol.lean` +65 (the `metered` mode +2; DRI note F7 +63: `Entry`, `Entry.of`, `Handles.entry?`, `caseResultWith`, `caseBounds`, `restrictedCases`), `VE/Route/MeteredTrace.lean` +30 (the explanation's `Trace`, `Row`, `Trace.rows`, `Trace.rowsOf`, `Row.json`, `Trace.json`), `VE/Route/MeteredRun.lean` +24 (F7: `Prepared`, `prepare`, `runWith`, `reportedWith`), `ResponseShape/Skeletons.lean` +3 (`metered`), `ResponseShape/Schemas.lean` +1 (its file), `ResponseShape/Schemas/Envelope.lean` −2; S −3 (`VE/Limits.lean`'s two S limits replace three S copies); K +0: +118 lines K+S+V in all. Exercised by `tests/test_metered_lean.py` (every family's trace against Python's), `tests/test_stage2_evaluation.py::test_traced_evaluation_matches_python`, the relay gate's 1,216 `service:metered` mutants, and for F7 `tests/test_metered_handles.py` (interleaved handles, a dropped or refused handle, the client's decodings), the `restrictedCases` `#guard`s against `VE.JsonInput.parseCases` and the theorem `caseResult_cached`; the ties pass is a FOLLOW-UPS.md row. | — | Standing ruling R16 (DRI-RULINGS.md): at most 150 lines K+S+V (+118), none in K, itemised here, each definition tested, ties row in FOLLOW-UPS.md |
