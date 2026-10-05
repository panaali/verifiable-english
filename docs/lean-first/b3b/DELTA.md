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
- A candidate's row built `one D s i` for its keys and again for its findings (cheap, removed as the plan states).

The changes, each beside the specified function it replaces, with a lemma that the two are equal:

| Lean | Specified | Run | Lemma |
|---|---|---|---|
| `Readings/Wire.lean` | `admitReadingsSpec` (`WellFormedDoc` in full) | `admitReadings`: after `admissionText` finds nothing, `frameWF` only | `admitReadings_eq`, from `wellFormedDoc_of_admissionText` and `sideWF_of_chainText` |
| `Readings/Run.lean` | `pairFactsSpec` | `pairFacts`: the witness's completion once; the other side's `completions` once per assignment, its value a `Thunk` read at most once | `pairFacts_eq`, from `separatesWith_eq` and `assignments_of_ownedKeys_nil` |
| `Readings/Run.lean` | `candidateJsonSpec` | `candidateJson`: `one D s i` once, `findingsOf` reads it | `candidateJson_eq` (`rfl`) |

`readings_wire_separate_sound` is unchanged: `replaySeparate` reads `admitReadings`, whose result is now the
specified one by `admitReadings_eq`. The 8 new theorems use the standard axioms only (`lean/axioms.txt`); no
theorem statement changed. `ve_readings_route` is the only executable whose bytes change: the 16 other Lean
executables, `ve_service` included (`checkers.lock` unchanged), and the Rust binary are byte-identical to the base
build. No Python changes behaviour: the batch deletes nothing (row 3b–3e: "none"), so it has no ledger.

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
| M2 `separatesWith` drops the other side's completions | a pair is separated only when no completion of the other side shows the value | `separatesWith_eq` (so `pairFacts_eq`) | `test_k1_strict_witness_does_not_separate`, `test_a_third_reading_never_witnesses_a_pair` |
| M3 a row's findings read `free D` instead of the candidate's document | a row's findings are its own document's | `candidateJson_eq` | `test_k19_rights_candidates_under_a_fixed_limitation` |
| M4 `other_admissible` asks every assignment instead of some | `other_admissible` is "some assignment is admissible" | `pairFacts_eq` | none of the existing tests (no fixture has a pair whose other side is admissible under some assignments but not all); the corpus A/B shows 34 `verdict` differences; this batch extends `test_generated_sets_lean_answers` to compare `other_admissible` with the search's own evaluation of the assignments, which then fails (`c6`) |

## Rest of the gate (5.1)

- **Suite (item 1):** see the fix report for the run at the final head (four chunks, `-n 8`, the gate's pytest
  options and prebuilt binaries, in a clean worktree).
- **Lean audit:** `lake env lean VE/Audit.lean` lists the 8 new theorems with `propext`, `Quot.sound` and
  `Classical.choice` only; `lean/axioms.txt` and `VE/Route/frozen-sources.sha256` are updated, and the assurance
  manifest pins `Readings/Wire.lean` at its new length (the whole file stays pinned; `admitReadingsSpec` is listed
  beside `admitReadings`).
- **Differential fuzzer:** not run. It does not reach the readings route (batch 3's DELTA), and no executable it
  reaches changed, so its baseline cannot grow.
- **Deletion ledger (item 3):** none; nothing is deleted.

## Not done here

- A quiet-host measurement of the UDHR call (none was available; the remainder above is an estimate from loaded
  runs).
- Batches 3c–3e; the saving column above is what this profile supports, and each needs its own measured gate.
- Statement review: no approved statement changed; the 8 new lemmas are equalities between a specified and an
  optimised computation, listed above for the reviewers.
