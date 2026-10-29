# Scale Lean admission memo delta

| Item | User-visible delta | Ruling | Evidence |
|---|---|---|---|
| 1 | Whole UDHR check: wall 2,935.6 → 474.9 s; summed Lean CPU 2,799.9 → 405.7 s. Result remains `CONFLICT-FREE`, premises `model`; 6,526 service requests on each run. | SIGNED by the DRI, `reviews/dri-decisions-20261028-scale.md` item 1 (no meaning change, build this speed fix). | `measurement.json`; `tests/test_readings_memo.py::test_memo_hit_answer_equals_fresh_service` |
| 2 | Trusted Lean growth against 785927e109ec: K +0, S +0, V +146 (`VE/Readings/Run.lean` +75, `VE/Service/Protocol.lean` +65, `Serve.lean` +6). | SIGNED by standing ruling R16 (DRI-RULINGS.md): within 150 lines and no K growth; the test and ties follow-up are recorded below. | `tools/trust_map.py --since 785927e109ec`; `tests/test_readings_memo.py`; `lean/VE/Service/MemoExamples.lean`; `FOLLOW-UPS.md` |

No verdict, diagnostic, fault-order, refusal, or JSON field delta was observed in the compared whole-document result. The source baseline used an isolated scope; this sandbox refused `iso.sh` with `Failed to connect to bus`, so the after run used the same profiler directly (both load samples are saved in `measurement.json`).
