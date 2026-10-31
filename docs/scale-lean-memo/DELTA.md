# Scale Lean admission memo delta

| Item | User-visible delta | Ruling | Evidence |
|---|---|---|---|
| 1 | Whole UDHR check: wall 2,935.6 → 474.9 s; summed Lean CPU 2,799.9 → 405.7 s. Result remains `CONFLICT-FREE`, premises `model`. The main-merged choice batch also reduced service requests 6,526 → 6,450 (readings-route requests 82 → 6); the memo-only intermediate run took 499.6 s wall and 370.0 s Lean CPU with 6,526 requests. | SIGNED by the DRI, `reviews/dri-decisions-20261028-scale.md` item 1 (no meaning change, build this speed fix). | `measurement.json`; `tests/test_readings_memo.py::test_memo_hit_answer_equals_fresh_service` |
| 2 | Trusted Lean growth against 314b23a42c21: K +0, S +0, V +148 (`VE/Readings/Run.lean` +77, `VE/Service/Protocol.lean` +65, `Serve.lean` +6), re-measured on `05f308fb8` after review fix F1 (+2). | R16 (DRI-RULINGS.md): within 150 lines and no K growth; the test and ties follow-up are recorded below. | `tools/trust_map.py --since 314b23a42c21`; `tests/test_readings_memo.py`; `lean/VE/Service/MemoExamples.lean`; `FOLLOW-UPS.md` |

No verdict, diagnostic, fault-order, refusal, or JSON field delta was observed in the compared whole-document result. The source baseline used an isolated scope; this sandbox refused `iso.sh` with `Failed to connect to bus`, so the after run used the same profiler directly (both load samples are saved in `measurement.json`).

Review fix F1 changes only process-local memo state, with no answer changed. A case refused after its admission now keeps the admission for later cases (`MemoExamples.lean` checks the refusal still equals `runCaseReported`). The `admissions` count on the test-only `VE_READINGS_MEMO_STATS` stderr line now counts admission runs, not misses.
