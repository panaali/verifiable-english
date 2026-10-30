# Scale Lean admission memo build report

Status: build complete; local trust mutation and targeted Mac reruns passed.
HEAD: final local branch tip after this report is committed; final Lean source commit `79620fc4a`.
Change: a process-local, bounded Lean memo reuses pure readings admissions by exact environment, document and kind.
Open items: the chain's final-HEAD release gate, which the task assigns to the test runner.
DRI signature needed: none; `DELTA.md` cites item 1 of the signed scale decision and R16.

## Delivery and evidence

| Acceptance item | Owner | Delivery | Evidence |
|---|---|---|---|
| Admit once per document in a service process | AGENT | `7195b23a1`, `lean/VE/Readings/Run.lean`, `lean/Serve.lean` | `tests/test_readings_memo.py::test_second_choice_does_not_readmit` |
| Exact key across environment, document and kind | AGENT | `7195b23a1`; structural JSON equality | `tests/test_readings_memo.py::test_memo_key_contains_document_environment_and_kind` |
| Bounded entries and bytes, restart clears state | AGENT | `7195b23a1`; four entries, 2 MiB serialized input bytes, process-local state | `tests/test_readings_memo.py::test_memo_evicts_oldest_entry_at_count_bound`, fresh-service test |
| Byte-identical answer to a fresh service | AGENT | `7195b23a1`; memo stores the existing `admitComponents` value and uses `runAdmitted` | `tests/test_readings_memo.py::test_memo_hit_answer_equals_fresh_service`, `lean/VE/Service/MemoExamples.lean` |
| Whole-UDHR before/after, CPU, wall and load | AGENT | `52c80b3d6`, `b97c503ae`; `measurement.json` | 2,935.6 → 474.9 s wall, 2,799.9 → 405.7 s Lean CPU; load 21.95 → 11.83 baseline, 19.90 → 41.60 after |
| Trusted growth under R16 | AGENT | `docs/trust-baseline.json`, `DELTA.md`, `FOLLOW-UPS.md` | `tools/trust_map.py --since 314b23a42c21`: K +0, S +0, V +146; trust mutation evidence below |
| Full release gate on final committed HEAD | EXTERNAL: chain | Deliberately left to the test chain under task instructions | Gate writes `gate-result.json` after handoff |

The first `iso.sh` attempt failed because this sandbox could not connect to the systemd bus. The before result is the DRI's isolated measurement in `scale-20261028/runs/p100-check.json`; the after runs used its profiler directly. The final after run began below the 32 load cutoff. It includes the main-merged choice batch, which reduced readings-route requests from 82 to 6. The memo-only intermediate run used 6,526 requests and took 499.6 s wall, 370.0 s Lean CPU. Result and premises were `CONFLICT-FREE` and `model` in every run. This is performance evidence, not a full bytewise comparison of every UDHR intermediate response.

## Seeded bugs

Each mutation was made in `lean/VE/Readings/Run.lean`, the named test failed, and the original code was restored before the final build:

| Mutated behaviour | Failing test |
|---|---|
| A hit returned an empty admission list | `test_memo_hit_answer_equals_fresh_service` |
| The key ignored the environment | `test_memo_key_contains_document_environment_and_kind` |
| The count cap changed from four to five | `test_memo_evicts_oldest_entry_at_count_bound` |
| A hit stopped incrementing the hit counter | `test_second_choice_does_not_readmit` |

The final source also has build-time `#guard` probes for each new trusted definition and the service response envelope. The Mac trust mutation gate passed with 119 KILLED, 0 SURVIVOR, 0 UNKNOWN, 3 INVALID, 16 ALLOWED and 0 NOT RUN. Its complete verdicts and exact allowances are in `trust-mutants.json` and `trust-mutants-allow.json`.

## Validation

- `lake build` passed: 1,162 jobs; `python3 lean/audit.py` passed: 669 source files, 7,428 named theorem declarations.
- `tools/trust_map.py --since 314b23a42c21` passed with no unclassified lines; K +0, S +0, V +146.
- `tools/gate_collection.py --check --prebuilt` passed: 4 added tests, 0 removed, refused, stale or malformed trailers.
- `tools/select_tests.py --base 314b23a42c21` selected 397 of 496 units. Its first local attempt hit a read-only home cache; `XDG_CACHE_HOME=/tmp/scale-cache` made the planning command pass.
- The selected Mac run before the final stats ordering fix reached 389 units and failed four IDs: two memo tests exposed a stderr response race, one trust-table completeness test exposed missing classifications, and one assurance manifest test exposed an unclassified Lean JSON fixture module. The exact four IDs passed on the Mac after the fixes (`/tmp/scale-failed-ids-mac.log`, 4 passed).
- No full `tools/gate.py` run was made locally, as instructed.

## Self-review against BUILDER-CHECKLIST

1. N.A. No response schema or Python relay fields changed; the existing binder is exercised by `test_memo_hit_answer_equals_fresh_service`.
2. PASS — `test_second_choice_does_not_readmit`, `test_memo_key_contains_document_environment_and_kind`, `test_memo_evicts_oldest_entry_at_count_bound` cover the required state, key and bound.
3. PASS — the four seeded failures above; `trust-mutants.json` records the trusted Lean mutation gate.
4. PASS — `test_memo_hit_answer_equals_fresh_service` and `MemoExamples.lean` compare hit and pure answers; Rust product code did not change.
5. N.A. No Python response binder changed; `test_memo_key_contains_document_environment_and_kind` exercises key separation at the service boundary.
6. N.A. The task assigns final-HEAD full gate to the chain; `tools/gate_collection.py --check --prebuilt` passed locally.
7. PASS — `DELTA.md` cites the DRI scale decision and R16, checked by `tools/trust_map.py --since 314b23a42c21`.
8. PASS — `test_memo_hit_answer_equals_fresh_service` compares full JSON; `measurement.json` records the UDHR result and request counts.
9. PASS — `tools/select_tests.py --base 314b23a42c21` selected 397 units including `tests/test_readings_memo.py`.
10. N.A. No theorem or statement was added; `python3 lean/audit.py` passed.
11. PASS — `test_memo_evicts_oldest_entry_at_count_bound` covers count and byte limits; `MemoExamples.lean` covers oversized entry eviction.
12. PASS — `measurement.json` records CPU/wall/load; `test_second_choice_does_not_readmit` is the step-count regression test.
13. PASS — `tools/gate_collection.py --check --prebuilt` reports zero removed, stale or malformed trailers.
