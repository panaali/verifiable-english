# tarch-split: split heavy tests without losing their relations (test architecture rank 7, §3.7)

Branch `infra/tarch-split`, from main `dae12d5f`. Plan: `reviews/test-architecture-2026-10-14.md` draft 2, §3.7
and rank 7; Astra's re-check (ADOPT WITH CHANGES) point 9.

**No DRI signature is needed.** There is no user-visible product delta: no verdict, diagnostic, wording, limit,
checker CPU or relayed answer changes, so no standing ruling applies and there is no DELTA.md. Test IDs change:
5 IDs are replaced by their cases. Each has a `Test-removed` trailer, and `tools/gate_collection.py --check
--prebuilt` reports 4 removed by a trailer and 0 refused, stale or malformed. The fifth ID, a test this branch
added and renamed, was never on main.

## Result (Mac, before and after)

The same 18 test files (`tests/test_assist.py`, the 14 `tests/test_p1*.py`, the rd6b differential,
`tests/test_english_evidence.py`, `tests/test_risk_margins.py`) were run through `mac-pytest.sh` on ve-mac-1:
6 workers, the longest-first scheduler, `--durations=0`, no VM fallback.
- Before: base `dae12d5f` from a clean worktree, Mac load 31/22/22.
- After: head `051d2344`, Mac load 28/35/40, so the after run was under somewhat higher load.
- Saved data: `evidence/mac-{before,after}-durations.txt`. `measure.py` parses them, recomputes the input
  partitions, and writes `evidence/measure.json`.

| | before | after |
|---|---:|---:|
| outcome | 322 passed, 2 skipped | 354 passed, 2 skipped |
| pytest wall (6 workers) | 579 s | **430 s** |
| summed test time | 3,044 s | 2,144 s |
| **longest test** | **257 s** (`test_p1.py::test_actual_offline_known_answer_gate`, setup) | **92 s** (the same test) |

What R2 still waits on: across the whole suite, the longest test stays `test_wire_gate_corpus` (597 s in the
plan's G-suite run). This batch keeps it as it is, as §3.7 requires: its nested run is reused through
`tools/run_cache.py` with run_cache's own key, and nothing here touches it. So R2's lower bound is now that test,
not the assist property test (516 s in G-suite, split by test-tail) or the P1 gate (206–257 s, now 92 s).

## Per test: inputs, relations kept, longest wall time on the Mac

| test | inputs before = after | relation(s) kept inside each case | cases before → after | longest Mac s before → after |
|---|---|---|---|---|
| `test_assist.py::test_astra_fix3_property_success_is_invariant_under_node_order_and_monotone_in_budget` (test-tail's split, checked, unchanged) | 7 graph specs × 2 search settings × 8 budgets × 5 orders = 560 sessions | order invariance over the 5 orders at each budget; monotonicity over the 8 budgets; the expected outcome at the largest budget | 14 → 14 | 38.3 → 48.9 (unchanged code; load) |
| `test_assist.py::test_astra_fix4_parent_order_never_changes_the_check_or_success` | 9 budgets × 3 parent orders = 27 sessions and 27 ledger replays | the step's check and success are equal across all 3 parent orders at the case's budget; replay equals the session | 1 → 9 (one per budget) | 49.0 → 10.3 |
| `test_assist.py::test_astra_rr2_property_success_is_monotone_in_the_proof_budget` | 6 items × 9 budgets = 54 sessions | monotonicity over all 9 budgets; the item's expected outcome (legitimate items succeed at the largest budget, probes never succeed) | 1 → 6 (one per item) | 91.4 → 30.0 |
| `test_assist.py::test_astra_rr2_property_any_inconclusive_fidelity_search_is_non_success` | 4 items, each forcing every one of its decisions to `unknown`; then every search exhausted at once on `plain` | per item: the classification run and every forced index of that item | 1 → 4 + 1 (`…every_search_exhausted_at_once_is_non_success`) | 69.8 → 27.3 |
| P1 known-answer gate (`test_p1.py`, fixture `known`) and the P1 tests that read a whole split (`test_p1_amendment9/12/13/14`, `test_p1_preflight`, `test_p1_history`) | 200 items' reference findings (identical: per-item SHA-256 equal to a sequential run, `evidence/p1-findings-threaded-vs-sequential.json`); then `p1.known_answer()` whole: 5 simulated judges over all 1,336 frozen requests, and 20,000 random trials per arm and panel | all of `known_answer`'s cross-item and cross-arm assertions run in one call; the fixture asserts the gate checked no finding the warm-up did not | not split; the per-item checks run 4 at a time | 257.0 → 92.0 (all P1: 1,160 → 335 s summed) |
| `test_readings_rd6b_differential.py::test_generated_documents_agree_on_both_routes` | 200 documents, each answered on both routes and compared whole (`measure.json`: 200 distinct before and after) | per document: both routes, every choice, premises, the query; per chunk: both conflict statuses and two verdicts (the guard), kept exactly | 10 → 15 chunks (20 → 13–14 documents) | 59.0 → 33.8 |
| `test_english_evidence.py::test_english_mixed_merge_smoke` | each configuration's whole corpus. The four slow ones have 706, 705, 1,118 and 1,122 documents, and the part sizes sum to the corpus before and after (`measure.json`) | per document: render, parse with all derivations, equality; per part: its count and one round trip per document | 24 → 34 parts (news-article-reviewed 4 → 8, claude-constitution-excerpt-reviewed 3 → 6, news-article 2 → 4, claude-constitution-excerpt 1 → 2) | 72.2 → 48.1 |
| `test_risk_margins.py::test_margins_agree_with_brute_force` | profiled, not changed: 8 shards × 25 records, about 1,000 probes each | per shard: every record's scans against brute force; the guard that every kind occurs | 8 → 8 | 26.0 → 33.0 (load) |

## 1. Test-tail's split checked against §3.7

§3.7 requires each shard to be one independent outer group holding all its orderings and budgets.
- test-tail cut the property test (tests/test_assist.py:1429-1444 at the plan's commit) into one case per (graph
  spec, search setting).
- Each case runs all 5 orders (`None, 1, 2, 3, 4`) at each of the 8 budgets, and asserts one outcome per budget,
  monotonicity over the budgets, and the expected outcome at the largest.
- That is exactly the loop body at 9f40783b, run for one (spec, setting) pair.
- No assertion at 9f40783b compares search settings or specs, so each case is a whole outer group, and every
  order-invariance and monotonicity assertion still sees all of its inputs.
- **The split did not cut a relation, and it is kept as it is.**

Seeded bugs, planted in the product code `ve/assist/session_views.py` (where `success` is computed):
- **S1, an order-dependent success:** success is false when node `fact` was inserted first.
  - It fails `[plain-search]` and `[plain_universal-no_search]`.
  - The failing assertion is the order-invariance one: `AssertionError: ('plain', {}, 3, 'order-dependent')` at
    tests/test_assist.py:1447.
- **S2, a success that turns false at a larger budget:** success is false at `max_proof_steps == 6`.
  - It fails `[plain-search]` on the monotonicity assertion, with `{0: False, 2: False, 3: True, 4: True, …}` at
    :1450. The largest budget still succeeds, so a missing input could not explain the failure.
  - It also fails rr2's `[plain]` case on its own monotonicity assertion.

## 2. The P1 known-answer gate: what its setup was, and why it is not cut into tests

Profile (cProfile, VM, `dae12d5f`): `p1.known_answer()` took 654 s.
- **639 s was `p1.finding(item)` for the 200 items.** Each item's argument check (`check_argument`, about 5,000
  one-shot `ve_metered` runs) happens on first use and is cached per process (`p1._finding`, an `lru_cache` of
  exactly 200).
- The gate's own simulations took about 14 s.
- The P1 files that read every item (amendment9, amendment12, preflight) and every dev or scored item
  (amendment13 and history; amendment14) pay the same cost on a cold worker. The per-file probe on the VM
  counted 200, 200, 200, 32, 32 and 168 misses.

**Why not split it across tests.**
- The gate's assertions span all items and all arms: accuracy per family, and the random rates and their contrasts
  per panel. So the gate itself has no independent outer group smaller than itself.
- A split across xdist workers would make every part recompute the findings in its own process, or share them
  through a cache. The plan forbids the second.
- `experiments/p1.py` is frozen with the preregistration (`experiments/P1-deference/freeze.json`) and is not
  edited.

**What changed instead.**
- The per-item checks are independent of each other: each item's reference replay, witness and record, each
  raising `PreflightError`.
- `tests/p1_findings.py::warm` runs them through the same function and the same cache, 4 at a time. The stack
  under them already serves concurrent callers: the pooled Lean services, the locked Rust checker pool, the
  one-shot runs, and a copy of the caller's context per item.
- The gate then runs whole. Its fixture asserts that `known_answer` caused no cache miss, so it checked only
  findings that `warm` computed.
- Measured on the VM: 8 threads gave 273 s against 1,064 s sequential at the same time. The findings were
  identical for all 200 items. `known_answer` on warm findings took 17.6 s.
- In `test_p1_history`, the warm-up runs between its two fingerprint reads, so that test still covers computing
  the findings.
- `test_p1_amendment15` (25 particular scored items), amendment7 and reconcile are left alone. Warming a whole
  split there would cost more than it saves.

## 3. rd6b: why 15 chunks

Each document is an independent differential. The chunk-level guard ("both conflict statuses and two verdicts,
so no chunk compares constants") is a relation over a chunk's documents and is kept exactly.
- Per-document data from all 200 documents is in `evidence/rd6b-documents-vm.json`: VM seconds, status and
  verdict, and both routes agreed on every document.
- Only 39 documents are CONFLICT, so `index % 20` would leave 2 chunks without one.
- **15 is the largest count up to 25 at which every `index % CHUNKS` chunk meets the guard.**
- Finer partitions fitted to the measured outcomes were rejected, because they depend on today's answers.
- Seeded bug S7 (16 chunks) shows the guard fails chunk 4.
- The cost is Python proof search (`prove_entailment`, CPU-bound), so threads would not help.

## 4. Mixed merge smoke

A part is `documents[part::parts]` of one configuration: each document is its own render, parse and equality
round trip, and the part asserts its own count and one round trip per document. Doubling the parts of the four
slow configurations keeps every document checked exactly once (`measure.json` sums the parts to the corpus).

## 5. `test_risk_margins.py` profile (not split)

Profile of one shard (VM): 75.4 s, of which 68.7 s waits for the Lean service and about 6 s is Python (building
records, JSON, validation).
- The test's `ThreadPoolExecutor(2)` gives no parallelism. `tests/lean_routes.py` drives one module-level
  `LeanService`, whose exchange holds a lock, so the two halves run one after the other (117 s of lock wait
  summed over the two threads).
- Running them in parallel would need a second service in `tests/lean_routes.py`. That module is not this
  batch's, and every route case goes through it for the wire-gate corpus recorder. This is left as a follow-up.
- At 26–33 s per shard on the Mac, the test is not near the tail, so it is not split. Its shards are also seeded
  draws, and changing the shard count would change the records.

## 6. Scheduling data: `tools/test-durations.json`

- **Why it needed updating.** The longest-first scheduler (test-tail) orders the suite by this file. A split
  test's new case IDs are unknown to it, so they are estimated as quick tests and could all go to one worker
  again.
- **How it was regenerated.** As test-tail did for its own split:
  - the changed files were profiled alone at 8 workers on the VM (`tools/bench/suite_tail.py run`, 277 tests
    passed, `evidence/suite-split-files-vm.json`);
  - the file was regenerated with the new `durations --previous` option, which counts the earlier file as one
    more run, so each test keeps its longest time.
- **Why longest time.** A cold P1 time is not replaced by a warm one, which is the tail the file's rule exists
  to prevent.
- **Result.** 39 case IDs were added. The split tests' old IDs and 9 IDs that main no longer collects dropped
  out. No time outside the profiled files changed.
- This is a measured data file, not a test criterion. No test asserts a duration.

## R2 and R3 stay complete and live

Nothing here touches the gate, selection, the store, `run_cache` or any reuse.
- **Every check that existed still runs.**
  - Every input is still checked, and the counts are listed above.
  - Every relation assertion still sees all its inputs in one test.
  - The P1 gate runs whole on findings computed by the same frozen function.
- **Nothing depends on duration.**
  - The durations file only orders tests.
  - No test asserts a duration, and no test depends on a cache from another process.
  - The in-process `lru_cache` was already there; `warm` only fills it earlier.
- **Astra point 5** (R3 should set `VE_RUN_CACHE=off` so the wire-gate corpus's nested run reruns live) belongs to
  the R3 pipeline, not to this batch's files. It is noted here because the longest test is that one.

## Seeded bugs

`mutants.json` was run with `tools/mutants.py`. Each named test passed unmutated first, then failed with the
mutant, and the file was restored byte for byte. Result: **11 of 11 killed**, saved in
`evidence/mutants-assist-tools.json` and `evidence/mutants-p1-rd6b-english.json`.

| id | file | behaviour claimed | killed by |
|---|---|---|---|
| S1 | ve/assist/session_views.py | split fix3 cases still check order invariance | fix3 `[plain-search]`, `[plain_universal-no_search]` (the `'order-dependent'` assertion) |
| S2 | ve/assist/session_views.py | split fix3 and rr2 cases still check budget monotonicity | fix3 `[plain-search]`, rr2 monotone `[plain]` (the monotonicity assertion) |
| S3 | ve/assist/session.py | split fix4 cases still compare all parent orders | fix4 `[3]`, `[4]` |
| S4 | experiments/p1.py (frozen; restored) | a failing per-item reference replay still fails the gate when checked concurrently | `test_p1.py::test_actual_offline_known_answer_gate` |
| S5 | tests/p1_findings.py | the gate reads no finding the warm-up did not check | the same (`assert 200 == 32`) |
| S6 | ve/readings_verdicts.py | each rd6b chunk still compares both routes | rd6b `[6]` |
| S7 | tests/test_readings_rd6b_differential.py | each chunk keeps its guard (16 chunks break it) | rd6b `[4]` |
| S8 | conformance/english_mixed.py | each mixed part checks every document of its share | `[claude-constitution-excerpt-1]` |
| S9 | tools/bench/suite_tail.py | `--previous` is one more run (a test keeps its longest time) | `test_suite_tail.py::test_durations_command_counts_an_earlier_file_as_one_more_run` |
| S10 | tools/test_schedule.py | `--previous` keeps the earlier file's estimate of an unrecorded test | the same |
| S11 | tools/bench/suite_tail.py | `--previous` refuses a file that is not a durations file | the same |

Changed product code is Python only, in `tools/test_schedule.py` and `tools/bench/suite_tail.py`, with S9–S11
planted there. No Lean or Rust changed.

## Plan rows and directives (BUILDER-CHECKLIST 2)

| plan row or directive | delivered by |
|---|---|
| "Shard only independent outer groups … one graph spec with all its orderings and budgets … never one shard per (ordering, budget) cell" | §1 (test-tail's split checked); 05f2d844 (fix4 per budget, rr2 per item) |
| "Seeded bugs: an order-dependent success, and a success that turns false at a larger budget. Each must fail the sharded test" | S1, S2 (cc004352) |
| "test_wire_gate_corpus … Keep that, rather than a new key" | untouched; `git diff main...HEAD -- tests/test_wire_gate_corpus.py tools/run_cache.py` is empty |
| rank 7 main files: test_assist.py, test_p1*.py, rd6b, english_evidence; profile risk_margins | 05f2d844, 5f05fefd, f0b5397b; §5 |
| "Report per test: inputs checked before/after (must be equal), the relations kept, longest-test wall time before/after on the Mac" | the table above; `evidence/measure.json` |
| "nothing weakens what is checked … no timing-threshold correctness test" | the R2/R3 section; no duration assertion added |
| "owns … and nothing in tools/select_tests.py" | select_tests.py unchanged |

## Not run, and checks run

- **Not run here:** the full gate. The chain runs it on the final HEAD.
- **Stopped:** the first before-run fell back to the loaded VM (no Mac slot within 10 minutes) and was stopped at
  its 2-hour limit. The Mac before-run above replaces it.
- **Selected tests:** `mac-pytest.sh --select -- --base dae12d5f --run` on HEAD 6aae37ae ran 155 of 394 units,
  0 failed, on ve-mac-1.
- **Seeded selection check:** S2's change in `ve/assist/session_views.py` selects all 394 units, `tests/test_assist.py`
  included (a `ve/` change selects everything today).
- **Collection check:** `tools/gate_collection.py --check --prebuilt`: 15,766 collected; 37 added; 4 removed by a
  trailer; 0 refused, stale or malformed.
- **Known red:** the tests in `main-known-red.txt` (`test_lean_service` sub-tick, the rd8 report) are not in this
  batch's files and were not touched.

## Follow-ups

- **Risk test:** `tests/lean_routes.py` serialises callers on one service, so the risk test's two threads run one
  after the other (§5).
- **P1 per-process cache:** the cache is still paid once per worker that runs a whole-split P1 test (up to 3 in
  one run), now about a third of the time. Grouping those files on one worker is a scheduler feature (test-tail's
  follow-up).
- **Largest remaining cases:** rr2 `inconclusive[legit_chain]` and `monotone[carrier_chain]` are the largest assist
  cases left (27–30 s on the Mac). Their budgets and forced indices are one relation each, so they are not cut
  further.
- **R3 run cache:** R3's `VE_RUN_CACHE=off` (Astra 5) belongs to the R3 pipeline.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer is fully typed and contained: N.A. No relay, schema or Lean answer was touched.
2. Every deliverable built, no rule broken: PASS. See the plan-rows table. Grep of the diff: no Python copy of a
   Lean decision, no new permanent report test (D4), and `tools/select_tests.py` untouched.
3. Tests and gates can fail: PASS. S1–S11 are all killed (`evidence/mutants-*.json`). S1 and S2 fail on the
   relation assertions themselves.
4. Python, Lean and Rust agree, and valid inputs still pass: PASS. The rd6b differential compares both routes on
   all 200 documents (`evidence/rd6b-documents-vm.json`: all agree). The Mac after-run passed 354, failed 0.
5. R8 binding: N.A. No relayed field was read or added.
6. Gate evidence matches the final HEAD: PASS for this report's evidence. The chain gates the final HEAD. The
   commit list is `git log main..HEAD --no-merges` (8 commits up to 6aae37ae plus this report).
7. No unsigned item: PASS. There is no product delta, and the test ID changes carry trailers.
8. Every user-visible change in DELTA: N.A. The diff of product outputs is empty; only tests, the scheduler's
   data and a bench tool changed.
9. Selection still finds the tests the change can break: PASS. `select_tests --base dae12d5f` gives 155/394 units
   and includes every changed test file. The seeded S2 change selects `tests/test_assist.py`.
10. Lean statements and proofs: N.A. No Lean changed.
11. Budgets, limits and deadlines fail closed: N.A. No budget code changed. The relation tests still check
    budget-0 sessions (fix4 `[0]`, rr2 budget 0).
12. No CPU or memory regression: PASS. The work is unchanged (the same findings and inputs), and wall time fell
    (`evidence/measure.json`).
13. Every removed or renamed test has a `Test-removed` trailer: PASS. `gate_collection.py --check --prebuilt`
    reports 4 removed by a trailer and 0 refused, stale or malformed.
