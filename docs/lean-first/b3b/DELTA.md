# Lean-first batch 3b: DELTA

Base `96d49927` (`lean-first/b3` at the gate), head `lean-first/b3b`. Plan `docs/LEAN-FIRST-PLAN.md` (draft 3,
branch `design/lean-first`), section 4 F5b and section 5.2 row 3b–3e: build each candidate's `one D s i` at most
once per request and reuse it wherever the answer needs it, gated on a measured improvement of the captured UDHR
readings case (pilot `pilot/udhr-20261003T0600Z`, `translation.ve.md`: 39 content-bearing sets, 176 candidates, 734
pairs).

## What the profile showed, and what changed

Profiled first (`profile/`, a Lake package over `lean/`; `evidence/profile-*.txt`). Building `one D s i` is not the
cost: 45 µs on the UDHR document. What a request repeats is the work done **on** each candidate's document:

- **Admission validated every document twice.** `admissionText` validates `free D` and each candidate's
  `one D s i` (`chainText`: `validateRights`, then the assertions' typing), and `admitReadings` then evaluated
  `WellFormedDoc`, whose `sideWF` conjuncts are the same two checks again. A UDHR validation costs 1.2–2.8 s of CPU
  depending on host load, nearly all of it independent of the candidate (below).
- **A pair evaluated each side twice.** `pairFacts` computed `separates` (the witness's `sideValid` and `sideValue`,
  the other side's completions) and then the same `sideValid`, `sideValue` and completions again for its fields. A
  `sideValue` is 0.1–0.4 s on the UDHR document.
- A candidate's row built `one D s i` for its keys and again for its findings, and a pair rebuilt both readings'
  documents in nearly every helper it called (`decodeSituation`, `situationWF`, `sideValid`, `cells`, ...).

The changes, each beside the specified function it replaces, with a lemma that the two are equal. Every
candidate's document is built **once per request**: admission's `candidateStage` builds it, validates it and keeps
it in the request's table (`Admitted.ones`), and the rows, the pairs and the findings read it from there
(`Admitted.side`). In `Separate.lean` each executable check has a form on a document the caller built
(`sideValidOf`, `sideValueOf`, `ownedKeysOf`, `cellsOf`, `assignmentsOf`, `tablesForOf`, `situationWFOf`,
`decisionOnlyOf`, `actOnlyOf`); the form on `D s i` that the theorems state is that form applied to `one D s i`,
so the logic has one owner and no statement changed.

| Lean | Specified | Run | Lemma |
|---|---|---|---|
| `Readings/Wire.lean` | `admitReadingsSpec` (`WellFormedDoc` in full) | `admitReadings`: `frontText`, then `candidateStage` (each candidate's `one D s i` built once, validated, kept; the first diagnostic stops it), then `frameWF` only | `admitReadings_eq`, from `wellFormedDoc_of_admissionText`, `sideWF_of_chainText`, `candidateStage_eq` (`stageOf_eq`), `candidateStage_ok`, `admissionText_of_stage` |
| `Readings/Wire.lean` | `one D s i` | `Admitted.side`: the request's table (`oneOf`) | `Admitted.side_eq`, from `oneOf_eq`; `onesOf_holds`: the table holds every candidate |
| `Readings/Run.lean` | `pairFactsSpec` | `pairFacts`: both documents from the table; `situationWF` (the replay's `shape`) and the bound not evaluated again; the witness's completion once; with no owned key the other side's one completion once; otherwise `otherScan`: each completion's admissibility when the scan reaches it, its value only when admissible and the witness shows the value, stopping at the first completion that decides both answers | `pairFacts_eq`, from `scanOthers_eq`, `otherScan_id`, `and_not_and_any` |
| `Readings/Run.lean` | `candidateJsonSpec` | `candidateJson`: the document from the table, read once | `candidateJson_eq` |
| `Readings/Run.lean` | `setFindingsSpec` | `setFindings`: the documents from the table | `setFindings_eq` |

`readings_wire_separate_sound` is unchanged: `replaySeparate` reads `admitReadings`, whose result is now the
specified one by `admitReadings_eq`. The 19 new theorems use the standard axioms only (`lean/axioms.txt`); no
theorem statement changed. `ve_readings_route` is the only executable whose bytes change: the 16 other Lean
executables, `ve_service` included (`checkers.lock` unchanged), and the Rust binary are byte-identical to the base
build. No Python changes behaviour: the batch deletes nothing (row 3b–3e: "none"), so it has no ledger.

## Review round (B1, B2)

The review of `b7366e0f` found two classes, both fixed here; the tables are in the generated block below
(`evidence/review-*.json`, `udhr_timing.py alternate`: the three executables one after another, each once per
round; the minimum and the median over rounds).

- **B1, eager evaluation where the specification short-circuits.** `completions` evaluated every assignment's
  admissibility before `.all`/`.any` could stop (the review's reproducer, first row of the review round table).
  The other side is now `otherScan`, which asks each completion only when the scan reaches it. The same class was
  in admission: `firstSome` was `filterMap` then `head?`, which validated every candidate after the first
  diagnostic (second row: a document whose first candidate is ill-formed); it is now `findSome?`. Regressions:
  `RunExamples.lean` counts `otherScan`'s evaluations in a state monad at build time (1 and 1 of 16 on the review's case, 9 and 9 when the ninth completion decides, 1 and 0
  when the witness misses, 2 and 0 when nothing is admissible); `tests/test_readings_lean_sharing.py` runs both
  reproducers under a CPU limit (3 s and 2 s) that the head before the fixes exceeds.
- **B2, sharing within a row only.** Each candidate's document is now built once per request (above). The test is
  the compiler's: `tests/test_readings_lean_sharing.py` reads the route's IR with the pinned toolchain and walks
  every function reachable from `main`; none reaches `one` or `build` except `candidateStage` and `oneOf`'s
  fallback (unreachable by `onesOf_holds`), and the same walk from `pairFactsSpec`, `candidateJsonSpec` and
  `admitReadingsSpec` does reach `one`.
- **A `Thunk` table was measured and rejected.** The first version of the table held each document in a `Thunk`,
  built when first read. On the UDHR first set it cost 5–8% more CPU than the head before the fixes (one-off runs
  of the intermediate builds, 7 rounds, not kept in `evidence/`). The likely cause, not confirmed in the runtime's
  source (the toolchain does not ship it), is that the runtime marks a `Thunk`'s value as shared between threads,
  which makes every later reference count on the document atomic. A table built up front was as fast as before but
  built every document even when admission stops at the first candidate (the second row's document took 2 s, and
  the CPU-limited test failed). `candidateStage` builds each document in the order admission checks them and stops
  with it, which is both.

The readings corpus (1,137 cases of `.scratch/corpus-cases.json`, one route call) gives answers byte-identical to
the base's and to the head's before the fixes.

## Gate item 2: corpus A/B

`tools/lean_first_diff.py record` on the base (a clean worktree of `96d49927` with its own builds) and on the head,
then `compare`:

| Corpus | Records per side | Same | Wording | Order | Verdict | Availability |
|---|---:|---:|---:|---:|---:|---:|
| readings (`readings_route.validate`, corpus SHA-256 `4f18eaa2…`, as batch 3) | 1,137 | 1,137 | 0 | 0 | 0 | 0 |
| pilots (`ve document check` of every `pilot/*` document) | 237 | 237 | 0 | 0 | 0 | 0 |

`compare` exits 0, `"unlisted": 0`, no `delta.json` needed. The probe matrix and the conformance corpora were not
recorded again: they never reach `ve_readings_route` (batch 3's DELTA), and every executable they do reach is
byte-identical. The UDHR translation is `CheckerUnavailable` on both sides inside the pilots corpus (the route's
120 s limit); its answer is compared directly below, byte for byte, in every timed run. An earlier A/B on the
previous base `a29ef3d0` gave the same result (1,374 of 1,374 the same).

## Gate item 4: latency

Base and head run **at the same moment** on the same case (`udhr_timing.py time`), so both see the same host load;
the host was shared with other workers throughout (one-minute load 13 to 51), which inflates CPU time as well as
wall time, so the comparison is the ratio. The tables below are generated from `evidence/` by
[`report.py`](report.py) (`tests/test_lean_first_b3b_report.py`).

<!-- BEGIN GENERATED: python docs/lean-first/b3b/report.py --write -->
### UDHR readings call (paired runs)

| Case | Sets | Candidates | Pairs | Run | Load | Base CPU (s) | Head CPU (s) | Change | Head wall (s) | Answers |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| first set | 1 | 4 | 12 | 1 | 22.6–25.2 | 23.9 | 12.2 | −49% | 12.4 | identical |
| first set | 1 | 4 | 12 | 2 | 25.2–31.6 | 24.6 | 11.9 | −52% | 12.3 | identical |
| first set | 1 | 4 | 12 | 3 | 31.6–37.7 | 25.0 | 12.8 | −49% | 14.8 | identical |
| first 10 sets | 10 | 30 | 72 | 1 | 37.4–34.8 | 151.2 | 78.5 | −48% | 81.6 | identical |
| whole document | 39 | 176 | 734 | 1 | 34.8–35.6 | 1,375.7 | 759.0 | −45% | 830.6 | identical |

### Where the head's CPU goes

| Step of the head's whole-document call | CPU (s) | Share |
|---|---:|---:|
| admission: 4.1's checks, `free D` and 176 candidates validated once each | 488.5 | 62% |
| pairs: 734 ordered pairs | 280.0 | 36% |
| candidate rows | 15.6 | 2% |
| 4.6 findings | 0.1 | 0% |
| **total** | **784.2** | |

| One validation or one pair (head, whole document) | CPU (s) |
|---|---:|
| `validateRights` | 1.51 |
| `softSemanticCheck` | 1.27 |
| `checkSoft` | 0.22 |
| `targets` | 0.17 |
| `rightsSemanticCheck` | 0.01 |
| pair `rs_u087`: pairFacts | 0.70 |
| pair `rs_u087`: sideValue witness | 0.42 |
| pair `rs_u087`: sideValue other, every assignment | 0.23 |
| pair `rs_u087`: conflict formula, built | 0.22 |
| pair `rs_u087`: outcome formula, built | 0.22 |
| pair `rs_u087`: conflict formula, evaluated | 0.00 |
| pair `rs_u087`: outcome formula, evaluated | 0.00 |

### Other measured workloads

| Readings corpus run (1,137 documents through `readings_route.validate`) | Base Lean CPU (s) | Head Lean CPU (s) | Change | Outcomes (ok / rejected / unavailable), both sides |
|---|---:|---:|---:|---|
| lake output 0 | 96.1 | 104.3 | +9% | 621 / 516 / 0 |
| lake output 1 | 96.1 | 104.4 | +9% | 621 / 516 / 0 |
| lake output 2 | 102.6 | 111.8 | +9% | 621 / 516 / 0 |
| fresh copy 1 | 53.3 | 53.0 | 0% | 621 / 516 / 0 |
| fresh copy 2 | 55.2 | 54.9 | −1% | 621 / 516 / 0 |
| the same cases in one process, run 1 | 4.36 | 3.01 | −31% | |
| the same cases in one process, run 2 | 4.00 | 2.97 | −26% | |
| the same cases, one process each, alternating | 60.7 | 59.8 | −1% | |

| 100 start-ups on an empty batch (user + sys, s) | Base, lake output | Head, lake output | Head, fresh copy of the same bytes |
|---|---:|---:|---:|
| run 1 | 6.43 | 6.84 | 6.30 |
| run 2 | 4.34 | 4.95 | 4.39 |
| run 3 | 4.35 | 4.74 | 4.39 |

| Constitution pilot S1 document (`ve document check`, children CPU, two runs) | Base (s) | Head (s) |
|---|---|---|
| `pilot/cc-20261003T0600Z` | 5.0, 5.1 | 4.8, 5.6 |
| `pilot/cc-20261004T0600Z` | 3.7, 3.7 | 3.6, 3.6 |
| `pilot/cc-20261004T1800Z` | 4.2, 3.9 | 3.5, 3.7 |

### Review round (B1, B2): base, the head before the fixes, the head

| Case | Rounds | Load | Base, min / median CPU (s) | Before the fixes, min / median | Head, min / median | Head against before, min / median | Rounds the head is faster | Answers |
|---|---:|---|---:|---:|---:|---:|---:|---|
| review B1's reproducer: 12 cells, ten fixed default rules | 3 | 17.7–32.0 | 0.15 / 0.16 | 8.88 / 11.14 | 0.09 / 0.10 | −99% / −99% | 3 of 3 | identical |
| the first set's default candidate ill-formed, 119 candidates after it | 3 | 32.0–42.8 | 3.26 / 3.56 | 3.44 / 3.50 | 0.19 / 0.19 | −94% / −95% | 3 of 3 | identical |
| UDHR first set | 9 | 36.6–13.8 | 17.06 / 18.22 | 8.64 / 9.77 | 8.74 / 9.05 | +1% / −7% | 5 of 9 | identical |
<!-- END GENERATED -->

**Reading.**

- **The F5b gate is met:** the captured UDHR case's Lean CPU falls by 45% (1,375.7 s to 759.0 s, paired), 48% on
  its first 10 sets and 49–52% on its first set, with byte-identical answers in every run.
- **The readings corpus is unchanged end to end**, as expected: its 1,137 documents are small, and a one-shot route
  spends ~50–60 ms of each call starting the 181 MB executable. The work itself falls 26–31% (the same cases in one
  process). The first three corpus runs showed the head 9% slower; the cause is the head executable's file as the
  linker wrote it (12 extents on disk), which costs ~4–6 ms more system time per start than a copy of the same bytes
  (1 extent) or the base's file. With a fresh copy at the same path the two sides are within 1%. This is a property
  of this host's file system, not of the code, and every rebuild produces a new file; it is recorded rather than
  hidden.
- **Constitution pilot S1 documents:** within the noise of two runs each (3.5–5.6 s), under the 120 s budget on both
  sides. No measured workload is slower beyond the start-up artefact above (budget rule: ≤ 20% more Lean CPU).

## The remainder against the 120 s limit, and what 3c–3e would each save

**F5b alone does not bring UDHR under the limit.** The head's call needs **759 s of Lean CPU (831 s wall)** at
load ~35 and 710 s (1,021 s wall) in an unpaired run at load 18–50. On a quiet host the same validation costs about
1.2 s against 2.8 s at load ~40 (profile runs), so the quiet-host remainder is **about 300–400 s, 2.5–3.5× the
limit** (estimate; no quiet host was available).

Where it goes (generated table above): admission 62% (177 validations, ~2.8 s each at that load), pairs 36% (734
pairs, ~0.38 s each), rows 2%. Inside a validation, `softSemanticCheck` is 84%; inside a pair, building the two
expanded formulas of the probe (`conflict`, `outcomeBase`: 0.22 s each) is all of it, evaluating them takes under
0.1 ms. Both are the same pattern: the layered environment `envAt (soften D) (size (soften D))` and the expansion
table are rebuilt (a topological sort of the stratum DAG each time) for every formula typed or expanded.

| Batch | What it would do | Saving on the UDHR call | Basis |
|---|---|---|---|
| **3d** (F5d, rights-chain speed-up) | compute `soften D`, its layered environments and expansion table once per document (`let`), in `softSemanticCheck`, `targets`, `observe`, `declaredTyped` | admission ~488 → ~80 s, pairs ~280 → ≲ 10 s at load ~35: **about 759 → 100–110 s CPU at load ~35, roughly 45–60 s on a quiet host, under 120 s** | *measured* on one UDHR validation: `softSemanticCheck` 1.27–1.88 s → 0.03 s with `soften D` and both environments computed once, same answer (`profile/` `ssc`, `softSemanticCheckHoisted`); *measured* that a pair is formula building, not evaluation; *estimate* that hoisting the expansion table removes the building cost |
| **3c** (F5c, shared base once, each candidate a delta) | validate the frame (62 regulated predicates, their decision formulas, `targets`) once, each candidate's own unit as a delta, with the equality lemma | on 3b's code: admission ~488 → a few seconds plus 176 deltas, **about −480 s (to ~280–300 s at load ~35, pairs untouched)**; after 3d: the remaining `checkSoft`/`targets` part, ~0.2–0.4 s × 176, **about −40–70 s** | *estimate* from the profile: a validation's cost is the frame's (a candidate adds 1–2 rules to a 62-predicate frame); `targets` is 0.17–0.26 s per validation |
| **3e** (F5e, sets in parallel across the pool) | one request per independent set | wall ÷ pool size **only after 3c**; before 3c each per-set request re-admits the whole document (177 validations), so 39 requests cost ~39× today's admission CPU (~19,000 s at load ~35) | *estimate* from the profile; the plan already orders F5e after F5b for this reason, and the profile says it must also follow 3c (or 3d) |

**Recommendation for the series:** 3d next (the largest saving, the smallest change: hoisted `let`s whose
equalities are `rfl`), then 3c if the 3d measurement leaves admission above the budget, then 3e only if wall time
still matters. This reverses the plan's order of 3c and 3d; it is the profile's finding and goes to the DRI with
this DELTA.

## Seeded bugs (build checklist 13)

Each was applied alone in a separate worktree (`ve-lf-3b-mut`), first showing that its equality lemma no longer
builds, then with that lemma's proof replaced by `sorry` so the executable builds, running the readings tests
(`test_readings_s1_lean.py`, `test_readings_s1_differential.py` at 200 documents, `test_readings_route_relay.py`);
the file was restored after each (`git status` clean).

| Mutant | Behaviour it breaks | Lemma that fails to build | Failing tests |
|---|---|---|---|
| M1 `admitReadings` skips `admissionText` (no candidate validated) | admission validates each document once | `admitReadings_eq` | 12 and more of `test_readings_s1_lean.py` (`test_k8_duplicate_declaration_across_sets`, `test_k20_fixed_unit_attached_to_two_sets`, `test_k18_norm_defaults_abstention`, `test_line_order_lists_each_line_once`, the `test_line_order_compares_lines_decoded` cases, …) |
| M2 `separatesWith` (now `pairFacts`'s `want && !blocked`) drops the other side's completions | a pair is separated only when no completion of the other side shows the value | `separatesWith_eq` (now `pairFacts_eq`) | `test_k1_strict_witness_does_not_separate`, `test_a_third_reading_never_witnesses_a_pair` |
| M3 a row's findings read `free D` instead of the candidate's document | a row's findings are its own document's | `candidateJson_eq` | `test_k19_rights_candidates_under_a_fixed_limitation` |
| M4 `other_admissible` asks every assignment instead of some | `other_admissible` is "some assignment is admissible" | `pairFacts_eq` | none of the existing tests (no fixture has a pair whose other side is admissible under some assignments but not all); the corpus A/B shows 34 `verdict` differences; this batch extends `test_generated_sets_lean_answers` to compare `other_admissible` with the search's own evaluation of the assignments, which then fails (`c6`) |

## Rest of the gate (5.1)

- **Suite (item 1), review round:** the full suite at `ce1c07f5` (the fixes; this file's later commit changes
  documentation only), in this worktree with its builds, four chunks of `-n 8` with `VE_NATIVE_PREBUILT=1`:
  **9,143 passed, 7 skipped, 0 failed** (1,761 + 4,430 + 1,747 + 1,205), `test_lean_transitive_axiom_allowlist`
  and `tests/test_readings_lean_sharing.py` among the passes; `lake build` and `python lean/audit.py` pass (3,064
  theorems, standard axioms only). Test changes: `tests/test_readings_lean_sharing.py` (6 IDs) and
  `test_every_review_round_gave_identical_answers`, pinned in `tools/gate-collection.json`.
- **Suite (item 1), before the review:** the full suite at `3819af3e` (this file's later commits change documentation only), in a
  clean worktree with its own builds, four chunks of `-n 8` with the gate's pytest options and environment
  (`VE_NATIVE_PREBUILT`, `VE_LEAN_PREBUILT`, `VE_RUST_PREBUILT`, `VE_RUST_BINARY`, no plugin autoload): **9,136
  passed, 6 skipped, 1 failed**. The failure, `test_rust_reproducible.py::test_a_copy_of_the_workspace_elsewhere_builds_the_same_binary`,
  is the clean worktree's: the test seeds an offline Cargo registry from the checkout's untracked
  `.cargo-home/registry`, which a fresh worktree does not have. With that directory copied in, the file passes
  (8 passed); no Rust changed. `test_lean_transitive_axiom_allowlist` (the whole `lean/audit.py`) is among the
  passes. Test changes: `test_generated_sets_lean_answers` also compares `other_admissible` (M4 above), and
  `tests/test_lean_first_b3b_report.py` is new (2 IDs pinned in `tools/gate-collection.json`).
- **Lean audit:** `lake env lean VE/Audit.lean` lists the 19 new theorems with `propext`, `Quot.sound` and
  `Classical.choice` only; `lean/axioms.txt` and `VE/Route/frozen-sources.sha256` are updated (`RunExamples.lean`
  added), and the assurance manifest pins `Readings/Wire.lean` at its new length (the whole file stays pinned;
  `admitReadingsSpec` is listed beside `admitReadings`).
- **Differential fuzzer:** not run. It does not reach the readings route (batch 3's DELTA), and no executable it
  reaches changed, so its baseline cannot grow.
- **Deletion ledger (item 3):** none; nothing is deleted.

## Not done here

- The UDHR first 10 sets and whole document were not timed again at the fixed head. Its first set was (review
  round table, 9 rounds at load 14–37): within noise of the head before the fixes (+1% by minimum, −7% by median,
  faster in 5 of 9 rounds). That case is admission's (5 validations), which the fixes do not change, and none of its
  pairs has an owned key, so `otherScan` is not reached there.
- The review's C item (the case sizes in `report.py` and the A/B and suite totals outside the generated block) is
  left as its follow-up.

- A quiet-host measurement of the UDHR call (none was available; the remainder above is an estimate from loaded
  runs).
- Batches 3c–3e; the saving column above is what this profile supports, and each needs its own measured gate.
- Statement review: no approved statement changed; the 8 new lemmas are equalities between a specified and an
  optimised computation, listed above for the reviewers.
