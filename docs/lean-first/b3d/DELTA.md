# Lean-first batch 3d: DELTA

Base `b7366e0f` (`lean-first/b3b` at its gate), head `lean-first/b3d`. Plan `docs/LEAN-FIRST-PLAN.md` (draft 3,
branch `design/lean-first`), section 4 F5 and section 5.2 row 3b–3e, as the DRI ruled on 2026-10-04 from batch 3b's
measurement: 3d before 3c, and 3d computes once per document what admission and pair evaluation rebuilt per
candidate and per pair: `soften D`, the layered environment (`envAt`) and the formula expansion table. Gate: a
measured improvement of the captured UDHR readings case (pilot `pilot/udhr-20261003T0600Z`, `translation.ve.md`:
39 content-bearing sets, 176 candidates, 734 pairs) against the previous head, and the pilot load under the
route's 120 s limit.

## What was rebuilt, and what changed

Batch 3b's profile located the cost; this batch's profiler (`profile/`, mode `prims`) found its source. Every
`envAt S i`, `size S` and `before S p` computes the layer order of `S = soften (correlate X)` again, a topological
sort of the stratum DAG (2–4 ms on a UDHR candidate, 62 regulated predicates). `expTable T i` is a function that
recomputes the layer order at each of its `i` levels and rebuilds the meaning of the symbol it finds, recursively;
nothing is kept between lookups. A UDHR validation computed the layer order a few hundred times
(`softSemanticCheck` types each rule's selection and four decision formulas per regulated predicate, each over a
fresh `envAt`; `checkSoft`'s conflict targets rebuild the table per target), and each pair rebuilt it for both
conflict formulas of its probe, on each side.

Each new function sits beside the function it replaces, with a lemma that they are equal:

| Lean | Specified | Run | Lemma |
|---|---|---|---|
| `Readings/Layers.lean` | `expTable T i` | `expAt (expEntries T) i`: one entry per layer symbol, newest first, each symbol's base formula a `Thunk` built when first read under the entries before it | `expAt_expEntries` (induction: `entryTable_take`, `expStep_foldl_drop`, `expStep_foldl_length`) |
| `Readings/Layers.lean` | `conflict`, `outcomeBase`, `pairConflict`, `targets` | `conflictIn`, `outcomeBaseIn`, `pairConflictIn`, `targetsIn`, from a document's layers (`layersOf`: its layer symbols, their names and the entries, one sort) | `conflictIn_eq`, `outcomeBaseIn_eq`, `pairConflictIn_eq`, `targetsIn_eq` |
| `Readings/Layers.lean` | `checkSoft`, `softSemanticCheck`, `validateSoft`, `validateRights` | `checkSoftOnce` (targets and soft premises from the layers), `softSemanticCheckOnce` (`soften D`, its layers and both layered environments computed once), `validateSoftOnce`, `validateRightsOnce` | `checkSoftOnce_eq`, `softSemanticCheckOnce_eq`, `validateSoftOnce_eq`, `validateRightsOnce_eq` (with `softPremisesIn_eq`, `selectsOn_soften`) |
| `Readings/Wire.lean` | `chainTextSpec` | `chainText`: each validation by its `Once` function, the complete environment for the assertions computed once | `chainText_eq`; `sideWF_of_chainText` reads `chainTextSpec` through it, so `admitReadings_eq` (3b) is unchanged |
| `Readings/Separate.lean` | `sideValid`, `sideValue`, `cells`, `assignments`, `tablesModel` | `sideValidOn`, `sideValueOn`, `cellsOn`, `assignmentsOn`, `tablesModelOn`, reading a candidate's `Side` (`sideOf D s i`: its document, assertions and keys, `soften (correlate X)`, its layers and base environment) | `sideValidOn_sideOf`, `sideValueOn_sideOf`, `cellsOn_sideOf`, `assignmentsOn_sideOf`, `tablesModelOn_sideOf` |
| `Readings/Run.lean`, `Readings/Scan.lean` | `pairFactsSpec`, `setPairsSpec` | `pairFactsIn` (both sides read from a cache, the other side scanned lazily by `pairEval`; review B below), `setPairs` (each candidate's side built once per set, `sidesOf`, read by all its pairs) | `pairFactsIn_eq` (with `replayPair_doc`, `pairEval_id`), `sideAt_sidesOf`, `setPairs_eq` |

The 30 new theorems use the standard axioms only (`lean/axioms.txt`); no theorem statement changed.
`readings_wire_separate_sound` is unchanged. The functions that replace W1, soft-norm and rights functions are
declared in those functions' namespaces but live in `Readings/Layers.lean`, which only the readings route imports.
So `lean/VE/{Norms,SoftNorms,Rights}` are byte-identical to the base, and `ve_readings_route` is the only executable
whose bytes change. The 16 other Lean executables (`ve_service` included; `checkers.lock` unchanged) and the Rust
binary are byte-identical to the base build (`cmp` of every `lean/.lake/build/bin` executable). No Python changes
behaviour; the batch deletes nothing (row 3b–3e: "none"), so it has no ledger.

<!-- BEGIN GENERATED: python docs/lean-first/b3d/report.py --write -->
### Gate item 2: corpus A/B

| Records per side | Same | Wording | Order | Verdict | Availability | Unlisted |
|---:|---:|---:|---:|---:|---:|---:|
| 1,374 | 1,373 | 0 | 0 | 0 | 1 | 0 |

| Corpus | Records per side |
|---|---:|
| pilots | 237 |
| readings | 1,137 |

### UDHR readings call (paired runs)

| Case | Sets | Candidates | Pairs | Run | Load | Base CPU (s) | Head CPU (s) | Change | Head wall (s) | Answers |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| first set | 1 | 4 | 12 | 1 | 6.6–6.7 | 8.8 | 0.7 | −93% | 0.7 | identical |
| first set | 1 | 4 | 12 | 2 | 6.7–6.8 | 8.8 | 0.7 | −93% | 0.7 | identical |
| first set | 1 | 4 | 12 | 3 | 6.8–6.7 | 8.8 | 0.7 | −93% | 0.7 | identical |
| first 10 sets | 10 | 30 | 72 | 1 | 6.7–6.2 | 53.6 | 4.4 | −92% | 4.4 | identical |
| first 10 sets | 10 | 30 | 72 | 2 | 6.2–5.7 | 44.7 | 3.3 | −93% | 3.3 | identical |
| whole document | 39 | 176 | 734 | 1 | 5.7–19.5 | 457.2 | 26.4 | −94% | 27.0 | identical |

### UDHR pilot translation through `ve document check` (paired runs)

| Run | Load | Base: wall (s), exit, answer | Head: wall (s), exit, answer | Head CPU, process and children (s) |
|---:|---|---|---|---:|
| 1 | 6.8–5.9 | 120.6, 5, CheckerUnavailable | 49.6, 0, answered (269,874 bytes) | 49.6 |
| 2 | 5.9–6.9 | 120.5, 5, CheckerUnavailable | 49.3, 0, answered (269,874 bytes) | 49.3 |

### Where the CPU went, and where the head's goes

| On the first UDHR candidate (`prims`), wall time | Specified (s) | As run (s) | Same answer |
|---|---:|---:|---|
| `targets` / `targetsIn` | 0.175 | 0.000 (+ `layersOf` 0.003) | yes |
| `checkSoft` / `checkSoftOnce` | 0.196 | 0.030 | yes |
| `softSemanticCheck` / `softSemanticCheckOnce` | 1.259 | 0.022 | yes |
| `validateRights` / `validateRightsOnce` | 1.474 | 0.064 | yes |
| `chainTextSpec` / `chainText` | 1.682 | 0.069 | yes |
| layer order of one document (`order`, a topological sort) | 0.002 | | |
| pair `rs_u087`: `pairFacts` / `pairFactsIn` (sides built) | 0.370 | 0.019 | yes |

| Step of the head's whole-document call (`split`) | CPU (s) | Share |
|---|---:|---:|
| admission: 4.1's checks, `free D` and 176 candidates validated once each | 14.8 | 45% |
| candidate rows (`candidateJson`) | 10.1 | 31% |
| pairs: 734 ordered pairs, each side built once per set | 7.8 | 24% |
| 4.6 findings | 0.0 | 0% |
| **total** | **32.7** | |

### The readings corpus

| Readings corpus (1,137 documents through `readings_route.validate`) | Load | Base Lean CPU (s) | Head Lean CPU (s) | Change | Outcomes (ok / rejected / unavailable) |
|---|---|---:|---:|---:|---|
| one route process per document, run 1 | 18.8–14.5 | 51.1 | 50.9 | 0% | 621 / 516 / 0 |
| one route process per document, run 2 | 14.5–13.3 | 61.8 | 61.7 | 0% | 621 / 516 / 0 |
| the same 1,137 route cases in one route process, run 1 | 13.4–13.4 | 2.53 | 2.19 | −13% | answers identical |
| the same 1,137 route cases in one route process, run 2 | 13.4–13.2 | 2.30 | 2.14 | −7% | answers identical |
<!-- END GENERATED -->

## Gate item 2: corpus A/B

`tools/lean_first_diff.py record --corpus readings pilots` on the base (a clean worktree of `b7366e0f` with its
own builds) and on the head, run at the same moment, then `compare --delta docs/lean-first/b3d/delta.json`
(table above; `evidence/ab-summary.json`). The readings corpus is batch 3's (SHA-256 `4f18eaa2…`, 1,137
documents). The probe matrix and the conformance corpora were not recorded: they never reach `ve_readings_route`
(batch 3's DELTA), and every executable they reach is byte-identical.

### A1: the UDHR pilot translation is answered (`availability`)

One record differs: `pilot/udhr-20261003T0600Z:usecases/udhr-pilot/run-20261003T0600Z/translation.ve.md`. On the
base, `ve document check` reports `CheckerUnavailable: ve_readings_route is unavailable` (exit 5): the readings call
exceeds the route's 120 s limit. On the head, the call completes and the check answers the document (exit 0, a
269,874-byte `ve-document@1` report, coverage 100%). Both outcomes are the one `availability` record of
[`delta.json`](delta.json). Every readings answer the head gives was compared byte for byte with the base's
answer to the same captured case (the paired runs above), so the report's readings content is the base's own
answer, which the base could not deliver within the limit.

**Signature:** DRI, availability A1 (1 record) — signed 2026-10-04: the UDHR document now loads (was CheckerUnavailable at the limit); answers byte-identical elsewhere.

## Gate item 4: latency

Base and head run **at the same moment** on the same input (`../b3b/udhr_timing.py time` for the route case,
`timing.py` for the corpus and the pilot), so both see the same host load. The host had 32 cores, one-minute load
5.7–19.5. Every table above is generated from `evidence/` by [`report.py`](report.py)
(`tests/test_lean_first_b3d_report.py`).

**Reading.**

- **The F5d gate is met:** the captured UDHR readings case falls from 457 s to 26 s of Lean CPU (−94%; 27.0 s wall),
  −92% to −93% on its first 10 sets and −93% on its first set, with byte-identical answers in every run.
- **The UDHR pilot now loads:** `ve document check` of the translation answers in 49.3–49.6 s wall (load 5.9–6.9)
  where the base stops at the route's 120 s limit with `CheckerUnavailable`. The readings call is 27 s of that; the
  rest is the document's other checks. This meets the plan's pilot-load row (≤ 120 s), measured at load ~6 on 32
  cores rather than on an idle host.
- **The readings corpus:** with one route process per document, the corpus costs the same on both sides, because
  start-up dominates its small documents (batch 3b's finding). The same 1,137 route cases in one route process cost
  7–13% less, with identical answers. The outcomes (621 accepted, 516 rejected, none unavailable) are identical. No
  measured workload is slower (budget rule: ≤ 20% more Lean CPU).
- **The profile:** on the first UDHR candidate a validation (`chainText`) falls from 1.68 s to 0.07 s and one pair
  of `rs_u087` from 0.37 s to 0.02 s, with each specified function and its replacement giving the same answer on the
  same input (`evidence/profile-prims.txt`, `profile-pair.txt`).

## The remainder, and 3c and 3e

The head's whole-document call (profiler `split`, 32.7 s at load 10–15) is admission 45%, candidate rows 31% and
pairs 24%. One validation now costs about 0.06 s: `checkSoftOnce` 0.03 s, `softSemanticCheckOnce` 0.02 s, and the
rights checks. What remains is spread across W1's own checks of `soften D` (`checkW1`, `semanticCheck`; a few layer
sorts each) and the per-candidate work, not one repeated computation.

- **3c** (validate the shared frame once, each candidate as a delta) would now save part of the 14.8 s of
  admission (*estimate*: under 10 s). It is no longer needed for the 120 s row.
- **3e** (one request per set across the service pool) still re-admits the whole document in each per-set request:
  39 requests × ~15 s of admission is about 585 s of CPU against today's 27 s, for a wall time of at best
  admission plus the largest set. Not worth doing unless 3c lands first, and not needed for the budget.
- **Rows** (10.1 s, 31%): not profiled inside in this batch. Each row computes the chain's document hash over the
  whole document's source units (`documentHash`); that is the likeliest cost, and it is outside F5's list.

**Recommendation:** the series' budget row is met by 3d. 3c and 3e can be closed, or kept as optional work if
UDHR-sized documents become frequent; this goes to the DRI.

## Seeded bugs (build checklist 13)

Each was applied alone in a separate worktree (`ve-lf-3d-mut`). Each was first shown to stop its equality lemma
from building. Then that lemma's proof was replaced by `sorry` so the executable builds, and the readings tests
were run (`test_readings_s1_lean.py`, `test_readings_s1_differential.py` at 200 documents,
`test_readings_route_relay.py`; 281 tests). The file was restored after each (`git status` clean).

| Mutant | Behaviour it breaks | Lemma that fails to build | Failing tests |
|---|---|---|---|
| M1 `expStep` expands each symbol's meaning without the entries before it | the expansion table built once is `expTable` | `entryTable_take` (so `expAt_expEntries`) | `test_outcome_probe_through_two_layers` (new) |
| M2 `chainText` types the assertions over the base environment | admission's checks with the layers computed once are the specified ones | `chainText_eq` | `test_outcome_probe_through_two_layers` (its asserted unit reads a layer symbol: "ill-typed assertion") |
| M3 `sideAt` gives every candidate the first candidate's side | each candidate's side is built once per set and read by its own pairs | `sideAt_sidesOf` | 36 failures and 90 errors in all three files (`test_k1_separation_keys_and_finding`, `test_unit_kinds_decide_what_is_in_force`, the rights and soft null cases, …; the module fixtures of the relay and differential tests get "distinguishing model violates a generated premise") |
| M4 `pairFactsIn` evaluates the other side's completions with the witness's side | a pair reads each side's own layers | `pairFactsIn_eq` | the same 36 failures and 90 errors |
| M5 `softSemanticCheckOnce` types each rule's selection over the base environment | the soft semantic check with the layers computed once is the specified one | `softSemanticCheckOnce_eq` | `test_outcome_probe_through_two_layers` (the reading's rule reads a layer symbol: "not stratified") |

Before this batch, M1, M2 and M5 failed no test: no fixture and no document of the readings corpus or the UDHR case
has a layer symbol whose meaning reads another, or an asserted unit that reads a layer symbol (M1's route gave
byte-identical answers on both corpora). `test_outcome_probe_through_two_layers` is new. It has a probe on
`avoid_required`, whose reading reads `warn_required`, whose fixed rule reads `help_required`, which reads `asks`.
It also has an asserted unit over `warn_required`. It passes on the base and the head.

## Review B: the other side of a pair is scanned lazily

The review found that `completionsOn` (in `pairFactsIn`) built every completion's admissibility before `.all` and
`.any` could stop. That is the pattern the DRI note of 2026-10-04 ruled out for this batch. Instrumented, a 12-cell
query whose first completion decides both answers evaluated all 4,096. The fix:

- `pairFactsIn` checks the bound and then runs `pairEval` (`Readings/Scan.lean`) in `Id`. Its other side goes
  through `scanOthers`, as in batch 3b's fix: each completion's admissibility is evaluated when the scan reaches it,
  its value only when it is admissible and the witness shows the value, and the scan stops once both answers are
  decided. `completions`, `separatesWith`, `completionsOn` and `pairFacts` are gone. `pairEval_id` states
  `pairEval` against `separates` and the specified fields, and `pairFactsIn_eq` now states `pairFactsIn` against
  `pairFactsSpec` directly. `ownedKeysOn` is the one owned-key list read by `cellsOn`, `assignmentsOn` and
  `pairEval`.
- The same class, elsewhere in this batch: `softSemanticCheckOnce` built the layers and both layered environments
  before its first conjunct, and `chainText` built the complete environment before knowing whether there is an
  assertion to type. The specified functions build these only when a conjunct reaches them. Each is now a `Thunk`
  read where the original computed it; the equality lemmas are unchanged.
- Regression, with no timing. `pairEval` is generic in a monad with one tick for each admissibility and each value
  evaluated on the other side. `Readings/RunExamples.lean`, imported by `VE.lean`, pins the counts at build time:
  (1, 1) on the 12-cell query, (1, 0) when the witness does not show the value, (9, 9) on four users where the ninth
  completion shows it, (2, 0) when no completion is admissible, and (1, 1) when the other side owns no key. Each
  answer is also compared with the specified one. `tests/test_readings_lazy_pairs.py` reads the compiled IR of
  `ve_readings_route`: `pairFactsIn` must call `pairEval`, and `main` must reach `scanOthers`. It also checks the
  route's answer on the review's reproducer (12 cells, ten fixed default rules). That test's CPU limit only stops a
  runaway route. Here, evaluating every completion costs 0.37 s and the scan 0.09 s, and the generated-layer limits
  admit no heavier side, so time cannot separate the two.

Seeded mutants, each applied alone and then restored:

| Mutant | Lemma | Failing check |
|---|---|---|
| R1 `scanOthers` keeps scanning after an admissible completion when the witness does not show the value | none (`scanOthers_eq` still builds) | `RunExamples.lean` (12-cell `σWrong12`: count is not (1, 0)); `lake build` fails |
| R2 `pairEval` evaluates every completion's admissibility up front (`mapM`), then reads the list | `pairEval_id` (replaced by `sorry`) | `RunExamples.lean`: the 12-cell, `σWrong12` and `σAvoid` counts; `lake build` fails |
| R3 `pairFactsIn` restored to the code before the fix (`completionsOn`, `separatesWith`), bypassing `pairEval` | `pairFactsIn_eq` (replaced by `sorry`) | `test_the_route_runs_the_counted_pair_evaluation` (`pairFactsIn` no longer calls `pairEval`) |

## Rest of the gate (5.1)

- **Suite (item 1):** the full suite at `1675c0f4` (this file's later commits change documentation only), in a
  clean worktree with its own builds (the Lean build copied and rechecked by `lake build`, the Rust build and the
  offline Cargo registry copied), six chunks of `-n 8` with the gate's pytest options and environment
  (`VE_NATIVE_PREBUILT`, `VE_LEAN_PREBUILT`, `VE_RUST_PREBUILT`, `VE_RUST_BINARY`, no plugin autoload,
  `-m "not live"`), load 11–38: **9,141 passed, 6 skipped, 0 failed** (9,147 collected; the gate collection pins
  9,148 IDs, the other one is `live`). The worktree was clean afterwards. Test changes:
  `test_outcome_probe_through_two_layers` is new (seeded bugs M1, M2, M5), and
  `tests/test_lean_first_b3d_report.py` is new (3 IDs); the 4 IDs are pinned in `tools/gate-collection.json`.
- **Lean audit:** `python3 lean/audit.py` passes: 3,083 theorems, the 30 new ones with `propext`, `Quot.sound` and
  `Classical.choice` at most. `lean/axioms.txt`, `VE/Route/frozen-sources.sha256` (the new module, `Audit.lean`
  and the three changed readings modules) are updated; `python3 VE/Route/frozen.py` passes. The assurance manifest
  pins `Readings/Wire.lean` at its new length (765 lines; the whole file stays pinned).
- **Differential fuzzer:** not run. It does not reach the readings route, and no executable it reaches changed, so
  its baseline cannot grow.
- **Deletion ledger (item 3):** none; nothing is deleted.

## Not done here

- **HUMAN (DRI):** the signature for A1.
- **HUMAN (reviewers):** statement review. No approved statement changed; the 30 new lemmas are equalities between
  a specified and an optimised computation, listed above and in `lean/READINGS.md`.
- **AGENT, when a host is idle:** the pilot and whole-document measurement on an idle host. These runs were at
  one-minute load ~6 to 19 on 32 cores.
- **AGENT, if the DRI keeps 3c or 3e:** profiling inside the candidate rows (31% of the remainder).
