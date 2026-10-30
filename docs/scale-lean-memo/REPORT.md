# Scale Lean admission memo build report

Status: review round 1 fixed (F1 B; follow-ups F2 and F3 too); trust mutation and selected tests passed on `05f308fb8`.
HEAD: final local branch tip after this report is committed; final Lean source commit `05f308fb8`.
Change: a process-local, bounded Lean memo reuses pure readings admissions; `admissions` now counts admission runs.
Open items: the chain's final-HEAD release gate, which the task assigns to the test runner.
DRI signature needed: none; `DELTA.md` cites item 1 of the signed scale decision and R16 (V +148 of 150).

## Review fix round 1 (`scale-lean-memo-review.final.md`)

| Finding | Fix | Regression tests | Commits |
|---|---|---|---|
| F1 B: the re-admission test counted misses, not admission work; a hit path that re-admitted passed every test | Structural: `admitComponentsMemo` no longer receives the request's parts. Its only admission is the `onMiss` thunk `runCaseReportedMemo` builds, which counts each of its own runs in `admissions`. The memo path runs in `ExceptT String (StateM AdmissionMemo)`, so a case refused after admission keeps the entry and the count. Before, a refusal dropped both: the next identical case admitted again, and the count missed that run. | `MemoExamples.lean` guard (hit with a failing, a counting and an emptied admission; 28-case sweep: every kind and component, consecutive and batched); `tests/test_readings_memo.py::test_a_hit_admits_nothing_on_every_kind_consecutive_and_batched[*]` (27 cases), `::test_a_case_refused_after_its_admission_keeps_it` | `57e981837`, `f37a34246`, `05f308fb8` |
| F2 C: byte charging untested on real entries | Tests charge real entries and pin the 2 MiB limit both ways | `::test_memo_charges_each_entry_its_serialized_bytes`, `::test_an_entry_over_the_byte_bound_is_answered_but_not_kept[2097152-True]`, `[2097153-False]`, `::test_entries_over_the_aggregate_byte_bound_evict_the_oldest[2-False]`, `[3-True]` | `f37a34246` |
| F3 C: self-review lacked item 14 | Item 14 below | — | this report |

PROBE F1 was "none". Instead, the reviewer's mutant, run before the fix (a hit returning `admitComponents kind parts` and keeping the counters), passed all 4 Python memo tests and `lake build` (`uv run pytest -q tests/test_readings_memo.py`: `4 passed`). After the fix, `parts` is not in the hit path's scope. The four seeded mutants below are its forms that still compile.

## Delivery and evidence

| Acceptance item | Owner | Delivery | Evidence |
|---|---|---|---|
| Admit once per document in a service process | AGENT | `7195b23a1`, `57e981837`, `lean/VE/Readings/Run.lean`, `lean/Serve.lean` | `tests/test_readings_memo.py::test_second_choice_does_not_readmit`, `::test_a_hit_admits_nothing_on_every_kind_consecutive_and_batched[*]`, `::test_a_case_refused_after_its_admission_keeps_it` |
| Exact key across environment, document and kind | AGENT | `7195b23a1`; structural JSON equality | `tests/test_readings_memo.py::test_memo_key_contains_document_environment_and_kind` |
| Bounded entries and bytes, restart clears state | AGENT | `7195b23a1`; four entries, 2 MiB serialized input bytes, process-local state | `tests/test_readings_memo.py::test_memo_evicts_oldest_entry_at_count_bound`, `::test_memo_charges_each_entry_its_serialized_bytes`, `::test_an_entry_over_the_byte_bound_is_answered_but_not_kept[*]`, `::test_entries_over_the_aggregate_byte_bound_evict_the_oldest[*]`, fresh-service test |
| Byte-identical answer to a fresh service | AGENT | `7195b23a1`; memo stores the existing `admitComponents` value and uses `runAdmitted` | `tests/test_readings_memo.py::test_memo_hit_answer_equals_fresh_service`, `lean/VE/Service/MemoExamples.lean` |
| Whole-UDHR before/after, CPU, wall and load | AGENT | `52c80b3d6`, `b97c503ae`; `measurement.json` | 2,935.6 → 474.9 s wall, 2,799.9 → 405.7 s Lean CPU; load 21.95 → 11.83 baseline, 19.90 → 41.60 after |
| Trusted growth under R16 | AGENT | `docs/trust-baseline.json`, `DELTA.md`, `FOLLOW-UPS.md` | `tools/trust_map.py --since 314b23a42c21`: K +0, S +0, V +148; trust mutation evidence below |
| Full release gate on final committed HEAD | EXTERNAL: chain | Deliberately left to the test chain under task instructions | Gate writes `gate-result.json` after handoff |

The first `iso.sh` attempt failed because this sandbox could not connect to the systemd bus. The before result is the DRI's isolated measurement in `scale-20261028/runs/p100-check.json`; the after runs used its profiler directly. The final after run began below the 32 load cutoff. It includes the main-merged choice batch, which reduced readings-route requests from 82 to 6. The memo-only intermediate run used 6,526 requests and took 499.6 s wall, 370.0 s Lean CPU. Result and premises were `CONFLICT-FREE` and `model` in every run. This is performance evidence, not a full bytewise comparison of every UDHR intermediate response. UNVERIFIED on `05f308fb8`: the UDHR timing was not re-run after the review fix. A hit or a miss calls the same functions as before. A refusal now keeps its admission, which can only remove admissions.

## Seeded bugs

Each mutation was made in `lean/VE/Readings/Run.lean`, the named test failed, and the original code was restored before the final build:

| Mutated behaviour | Failing test |
|---|---|
| A hit returned an empty admission list | `test_memo_hit_answer_equals_fresh_service` |
| The key ignored the environment | `test_memo_key_contains_document_environment_and_kind` |
| The count cap changed from four to five | `test_memo_evicts_oldest_entry_at_count_bound` |
| A hit stopped incrementing the hit counter | `test_second_choice_does_not_readmit` |

Review fix round 1: each mutation was planted in `lean/VE/Readings/Run.lean` at `05f308fb8`'s source, built (`lake build VE.Service.MemoExamples`, then `lake build ve_service`) and run (`VE_NATIVE_PREBUILT=1 uv run pytest -q tests/test_readings_memo.py`, because the suite's own `lake build` already fails on the guard), then restored (`git diff --stat` clean):

| Mutated behaviour | Lean guard (`MemoExamples.lean:8`) | Failing Python tests |
|---|---|---|
| M1: a hit also runs `onMiss` (re-admits, counted) | fails | 31, e.g. `test_second_choice_does_not_readmit`, `test_a_hit_admits_nothing_on_every_kind_consecutive_and_batched[readings-validate-main]` |
| M2: a hit runs `onMiss`, returns its fresh result and restores the counters (the review's mutant) | fails | none: its answers are byte-identical and its counters untouched, so only the guard's emptied and failing admissions can see it; the suite cannot start, because its build fails |
| M3: entries charged 0 bytes (F2) | passes | 5: every `test_memo_charges_*`, `test_an_entry_over_the_byte_bound_*` and `test_entries_over_the_aggregate_byte_bound_*` case |
| M4: a refusal drops the memo's update (the pre-fix behaviour) | fails | 7: `test_a_case_refused_after_its_admission_keeps_it` and the sweep's six refused cases, e.g. `[readings-model-main]` |

No Python or Rust product code changed in this round, so only Lean mutants apply.

The final source also has build-time `#guard` probes for each new trusted definition and the service response envelope. The trust mutation gate on `05f308fb8` (`mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/scale-lean-memo/trust-mutants.json --allow docs/scale-lean-memo/trust-mutants-allow.json --test lean/VE/Service/MemoExamples.lean`, a full run without `--rescore`, cloud pool, snapshot tree `94a21377` = `05f308fb8^{tree}`) passed with 119 KILLED, 0 SURVIVOR, 0 UNKNOWN, 3 INVALID, 16 ALLOWED and 0 NOT RUN. Its complete verdicts and exact allowances are in `trust-mutants.json` and `trust-mutants-allow.json`.

## Validation

Review fix round 1, on `05f308fb8`:

- `cd lean && lake build`: `Build completed successfully (1162 jobs).` `python3 lean/audit.py`: `PASS: 669 source files; 7428 named theorem declarations audited`.
- `tools/trust_map.py --since 314b23a42c21`: `K +0, S +0, D +0, G +148, tied +0, unclassified +0, trusted +148` (`VE/Readings/Run.lean: trusted +77`, `VE/Service/Protocol.lean: trusted +65`, `Serve.lean: trusted +6`). `trust_map.py --check` exits 0 after the V +2 R16 allowance in `docs/trust-baseline.json`.
- `tools/regen_generated.py --check`: `regen_generated: checked 33 entries`.
- `tools/gate_collection.py --check --prebuilt`: `30311 collected, 30274 at 314b23a42c21...; 37 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers`.
- `uv run pytest -q tests/test_readings_memo.py` (local VM): `37 passed`.
- `mac-pytest.sh --select -- --base 314b23a42c21 --run`: `recorded 397 units ...; 0 failed`, `ran on ve-mac-1 (aarch64) ... HEAD 05f308fb + uncommitted changes` (the uncommitted change was only `trust-mutants.json`), `exit=0; failed/error ids=0`.
- Not run: the full `tools/gate.py`, as instructed; the UDHR timing (see above).

Round 0, on `79620fc4a`:

- `lake build` passed: 1,162 jobs; `python3 lean/audit.py` passed: 669 source files, 7,428 named theorem declarations.
- `tools/trust_map.py --since 314b23a42c21` passed with no unclassified lines; K +0, S +0, V +146.
- `tools/gate_collection.py --check --prebuilt` passed: 4 added tests, 0 removed, refused, stale or malformed trailers.
- `tools/select_tests.py --base 314b23a42c21` selected 397 of 496 units. Its first local attempt hit a read-only home cache; `XDG_CACHE_HOME=/tmp/scale-cache` made the planning command pass.
- The selected Mac run before the final stats ordering fix reached 389 units and failed four IDs: two memo tests exposed a stderr response race, one trust-table completeness test exposed missing classifications, and one assurance manifest test exposed an unclassified Lean JSON fixture module. The exact four IDs passed on the Mac after the fixes (`/tmp/scale-failed-ids-mac.log`, 4 passed).

## Self-review against BUILDER-CHECKLIST

1. N.A. No response schema or Python relay fields changed; the existing binder is exercised by `test_memo_hit_answer_equals_fresh_service`.
2. PASS — `test_a_hit_admits_nothing_on_every_kind_consecutive_and_batched[*]`, `test_a_case_refused_after_its_admission_keeps_it`, `test_memo_key_contains_document_environment_and_kind`, `test_memo_evicts_oldest_entry_at_count_bound` and the byte-bound tests cover the required state, key and bounds.
3. PASS — the seeded failures of both rounds above; `trust-mutants.json` (119 KILLED, 0 SURVIVOR on `05f308fb8`).
4. PASS — `test_a_hit_admits_nothing_on_every_kind_consecutive_and_batched[*]` and the `MemoExamples.lean` sweep compare hit, batch and pure answers on every kind; Rust product code did not change.
5. N.A. No Python response binder changed; `test_memo_key_contains_document_environment_and_kind` exercises key separation at the service boundary.
6. N.A. The task assigns final-HEAD full gate to the chain; `tools/gate_collection.py --check --prebuilt` passed locally.
7. PASS — `DELTA.md` cites the DRI scale decision and R16 (V +148), checked by `tools/trust_map.py --since 314b23a42c21`.
8. PASS — `test_memo_hit_answer_equals_fresh_service` compares full JSON; `measurement.json` records the UDHR result and request counts.
9. PASS — `mac-pytest.sh --select` recorded 397 units, including `tests/test_readings_memo.py`.
10. N.A. No theorem or statement was added; `python3 lean/audit.py` passed.
11. PASS — `test_an_entry_over_the_byte_bound_is_answered_but_not_kept[2097152-True]`/`[2097153-False]` (limit and limit+1), `test_entries_over_the_aggregate_byte_bound_evict_the_oldest[*]`, `test_memo_evicts_oldest_entry_at_count_bound`.
12. PASS — `measurement.json` records CPU/wall/load; `test_second_choice_does_not_readmit` and the sweep count admission runs.
13. PASS — `tools/gate_collection.py --check --prebuilt` reports 37 added and zero removed, stale or malformed trailers.
14. PASS — both directions, evidence and the spec re-read:
   - **Opposite direction.** Hit versus miss: the guard runs a failing and a counting `onMiss` on both. A hit runs neither; a miss runs each once, and its failure is not kept. Byte bound: an entry of exactly 2,097,152 bytes is kept, and 2,097,153 is not. Aggregate bound: two 838,861-byte entries are both kept, and three evict the oldest. Refusal: a refused case keeps its admission, and its answer still equals the pure answer (`refusedFirst == runCaseReported bad1`). Key: different kind, environment or document misses, and the same request hits (`test_memo_key_contains_document_environment_and_kind`).
   - **Command output.** Every claim in this report names its command and quotes the output above. The UDHR timing on the fix HEAD is marked UNVERIFIED.
   - **Spec re-read.**
     - "the memo must return exactly the value the pure admission function returns" against `prompts/task-scale-lean-memo.txt` line 3: a miss runs `admitComponents kind parts` unchanged, and a hit returns its stored value.
     - "(d) a test that fails if the second request of the same document re-admits (count admissions via an env-gated counter or the service's stats line)" against line 4: `admissions` on the `VE_READINGS_MEMO_STATS` line now counts runs of `onMiss`.
     - "Answers byte-identical ... refusals" against line 3: the sweep compares refused answers with `runCaseReported`.
     - "no meaning change" against `reviews/dri-decisions-20261028-scale.md:4`: no answer changed.
