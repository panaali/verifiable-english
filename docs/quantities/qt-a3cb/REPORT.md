# qt-a3cb report: the `countermodel` case of the `cardinality` mode (quantities QT-A3, spec 3.9)

Status: built; no DRI signature is reserved. The mode answers `countermodel` (W6a's budgeted `refutesB` on the erased
problem, proved through `refutesC_sound` by `countermodel_sound`); each region's size is computed once per model and
its work charged against W6a's evaluation budget before it runs (`regionSizes`, `regionCost`, `withSizes_eq`).
Trust: untied V +8, K +0, S +0 (R16). Seeded bugs 12/12 killed; trust mutants 0 survivors. Nothing was cut: no qt-a3cc.
Next: qt-a4 (relay and document hook). Open: FOLLOW-UPS "## qt-a3cb" (ties pass; QT-A4 binds `sizes` to the table).

## Plan, spec and synthesis

- Read: plan QT-A3 and 2.3 (`quantities-PLAN.md` 225-240, 625-665, 709-760), spec 3.9, 4.1-4.3, qt-a3c's REPORT,
  reviews `qt-a3c-review.final.md`, `qt-a3c-review-ov.final.md`, FOLLOW-UPS "## qt-a3c". Synthesis round 2's edits
  (`edits-quantities.md` 1-7: QT-A7 units, the premise budget, AR-10 rows, `time@0`/`order@0`, "often", QT-A6, hedged
  counts) concern other items: this item implements none of them.
- Statement gate: `refutesC_sound`, `withRegionsFinite`, `refutesC` and the rest of 3.9 are unchanged (Erase.lean and
  Theorems.lean only gain lines: `git diff --numstat` 35/0 and 44/0); `lean/statements.txt` only gains lines.
- New theorems (no plan statement): `evalBy_eq`, `sizeIndex_get`, `regionSizes_eq`, `withSizes_eq` (Theorems.lean),
  `sortDomains_valid`, `sizesJson_regionSizes`, `countermodel_sound` (RunTheorems.lean), `sizesJson_fits`,
  `certificate_kind`, `countermodel_kind` (Encoders/Cardinality.lean). `python3 lean/audit.py`: "PASS: 676 source
  files; 7562 named theorem declarations audited".

## Plan rows (the task's order)

| Row | Delivered | Where, checked by |
|---|---|---|
| (1) `countermodel` case, budgeted as W6a's `refutesB`, through `refutesC_sound` | yes. `Run.countermodel`: W6a's model decoder on the projection's vocabulary, the charge, then `refutesB` on the sorted presentation with the hash index, as W6a's `countermodel` case. `countermodel_sound`: on the problem `checkedProblem` built, `countermodel … = .ok (true, _)` gives `¬ CEntails.{0}` (via `refutesB_sound`, `withSizes_eq`, `sortDomains_valid`, `refutesC_sound`; `hq : w.env.q = w.w6.vocab.env` is `decodeEnvironment_sound`'s) | RunExamples countermodel guards (FA1b refuted, sizes 1, 1, 15, 1; FA1 not refuted; a model satisfying the conclusion not refuted; the whole answer); route cases `fa1b-countermodel`, `fa1-countermodel` |
| (2) Region sizes computed once per model, charged against a stated limit | yes. `regionSizes` reads each sort's objects (`firstUseH`) and predicates once and computes each region's size once; `sizeIndex` is built once; `withSizes` reads a constant through it (`withSizes_eq`: it is `withRegionsFinite`, which no service path evaluates any more). `regionCost` (2^k × objects × (k + 1) per sort) is charged against W6a's `maxEvaluations` (1,000,000) before any size is computed, and `refutesB` starts from it | growing chain: `test_region_sizes_are_charged_before_they_are_computed` (1 and 2 sorts of 1,000 objects refuted, 3 refused, UNKNOWN); `test_the_charge_and_the_check_share_one_budget`; `#guard err (chain 3 1000 0) == budgetExhausted`. Probe (`uv run python`, ve_service): the chain's three cases in 0.22 s |
| (3) Row shape, encoder, `runCaseReported_fits`, route cases | yes. `cardinality.json`: `countermodel` (`refutes`, the admission's statements and identities, `regions`, `sizes`) and `sizes` (each constant with a natural size, at most 512); `runCase_fits` extended (`sizesJson_fits`, `countermodel_kind`) | `test_countermodel_rows_are_typed_and_bound` (49 mutants); relay gate `service:cardinality`: 4,807 mutants, 0 failures ([evidence/relay-gate.json](evidence/relay-gate.json)) |
| (4) Seeded bugs | 12/12 killed, below | `mutants.json` |
| DELTA | rows 1 (SYNTHESIS 2.2, as qt-a3c's rows 1-2), 2 (R2), 3 (R16) | [DELTA.md](DELTA.md); review-ready's `uncited_ruling_rows`: [] |

Overlap at the start: `tools/trust-classes.json` (ap-2bb, jt-2c, me-2nc, sc-1c, me-1) and
`tests/data/route-cases.jsonl` (sc-1c), additive lines in shared tables.

## Seeded bugs

`uv run python tools/mutants.py docs/quantities/qt-a3cb/mutants.json --no-baseline`: 12/12 killed
([evidence/mutants-run.json](evidence/mutants-run.json); the two service-killed charge mutants rerun with
`VE_NATIVE_PREBUILT=1`, [evidence/mutants-run-service.json](evidence/mutants-run-service.json): in the first run
pytest's session build stopped on the three-sort `#guard` first). Lean only: no Python or Rust product code changed.

| Mutant | File | Killed by |
|---|---|---|
| `charge-dropped` (the region size left uncharged) | `Run.lean`, `countermodel` | `test_region_sizes_are_charged_before_they_are_computed` (the third sort answered) |
| `charge-not-shared` (`refutesB` from 0) | `Run.lean`, `countermodel` | `test_the_charge_and_the_check_share_one_budget` |
| `premises-unread` (a countermodel that does not refute accepted) | `Run.lean`, `countermodel` | `#guard (refute fa1Premises fa1bModel).getObjValD "refutes" == .bool false` |
| `evalBy-not`, `regionSizes-whole-sort` | `Erase.lean` | FA1b's sizes `#guard` (proofs cut for the run) |
| `regionCost-predicates` | `Erase.lean` | `test_region_sizes_are_charged_before_they_are_computed` |
| `sizeIndex-zero`, `withSizes-off-by-one` | `Erase.lean` | FA1b's `refutes == .bool true` `#guard` (proofs cut) |
| `sizesJson-size`, `runCase-countermodel-kind` | `Run.lean` | FA1b's sizes `#guard`; the countermodel guards |
| `schema-refutes-typed`, `schema-sizes-typed` | `Schemas/Cardinality.lean` | `test_countermodel_rows_are_typed_and_bound` |

Trust mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --allow … --rescore …`, final Lean, HEAD 7b7470ef6):
[trust-mutants.json](trust-mutants.json) 29 KILLED, 0 SURVIVOR, 2 ALLOWED, 4 INVALID, exit 0. The first run's six
`runCase` survivors cut the countermodel answer's statements and identities, which no guard read: RunExamples now pins
the whole answer. The two ALLOWED `sizesJson` mutants do not elaborate ([trust-mutants-allow.json](trust-mutants-allow.json)).

## Trust, size, tests

- Trust (`tools/trust_map.py --check`: "PASS: K, S and untied [V] within 96c5d418d98e and the allowances"): untied
  V +8, all `Run.lean` (`sizesJson` 4, `runCase` +4); `countermodel` G[V] tied by `countermodel_sound`; the C and
  G[R] declarations as in DELTA row 3. Allowance recorded under R16; FOLLOW-UPS "## qt-a3cb".
- Size (`git diff --numstat` against the merge base, generated files and evidence JSON excluded): about 600 lines
  with this report: Lean 340 (guards 103, theorems 112), tests and data 107, side tables 60, docs about 130.
- Selected tests (`mac-pytest.sh --select`, tree 7b046476a9, 6 shards): 403 units, 401 passed; failed
  `test_cardinality_exercised.py` (`sizesJson` was stated about by no theorem: `sizesJson_regionSizes` added) and
  `test_consolidation_tools.py::test_committed_ledger_names_real_declarations` (step 7's measured figures, as qt-a3d
  re-measured them: 721, 661, 55.1); both files rerun: "6 passed". None is in `main-known-red.txt`.
- `regen_generated.py --check`: 34 entries fresh. `gate_collection.py --check --prebuilt`: 3 added, 0 refused, 0
  stale, 0 malformed. The release gate was not run by me (the chain runs it on the final HEAD).
- Pilot bytes moved: 0 (estimate; the mode reaches documents only through QT-A4).

## Spec re-read

- 3.9 "a claimed region table is never read (QT-A3 refuses a forged one)": the case refuses a forged table before the
  model (`RunExamples` guard), reads an equal one past it, and a model naming a region constant is refused.
- 4.1 case kinds (`countermodel`) and identities: the answer carries both identities as an admission (whole-answer guard).
- 4.2 "A limit is ResourceLimit naming the bound, never a partial answer; exhaustion of a search is UNKNOWN": the
  charge and the check refuse with W6a's `budgetExhausted`, never a verdict.
- Plan 2.3 "Lean computes the region sizes by enumeration and runs W6a's existing countermodel check": `regionSizes`, `refutesB`.

## Self-review against BUILDER-CHECKLIST

1. PASS: `test_countermodel_rows_are_typed_and_bound` (each member dropped, retyped with BAD, rebound); relay gate 4,807 mutants, 0 failures.
2. PASS: plan-row table above; no Python copy of a Lean decision (no Python product change); no permanent report test.
3. PASS: `mutants.json` 12/12 (each a `#guard` or service test, not a build or hash step); trust mutants exit 0.
4. PASS: `test_route_cases_answer_as_recorded` (every other route case answers as before); FA1 and FA1b on both sides.
5. PASS: model inputs: an undeclared entity, wrong arity, a duplicate tuple, a region constant refused (RunExamples guards); region constants of a request finite sort (`x-references`, mutant "a constant of another sort").
6. PASS: evidence saved under `evidence/`; gate left to the chain on the final HEAD.
7. PASS: DELTA rows 1-3 cite SYNTHESIS 2.2 (decision file), R2, R16; `uncited_ruling_rows` and `dri_needed_rows`: [].
8. PASS: DELTA rows 1-2 (the kind, its answers, its order and refusals); no other route case changed.
9. PASS: `select_tests.py` selected 403 units including `test_cardinality_service.py` and `test_cardinality_exercised.py`.
10. PASS: `countermodel_sound` is about `Run.countermodel`, the value `runCase` returns; `premises-unread` breaks it and the guard.
11. PASS: budget exhaustion is UNKNOWN (`budgetExhausted`), at the charge and in the check (both chain tests); no timing in tests.
12. PASS: step-count fixture: the charge refuses three sorts before any size is computed (`#guard err (chain 3 1000 0)`; `charge-dropped`).
13. PASS: no test removed; `gate_collection.py --check --prebuilt` 0 refused, 0 stale, 0 malformed.
14. PASS: both directions: charge (2 sorts answered, 3 refused), budget (1 sort answered, 2 exhausted), verdict (true, false), claims (equal read past, forged refused), model (valid, four refusals).

## FIXMAP

- `lean/VE/Cardinality/Erase.lean`: `Body.evalBy`, `regionSizes`, `regionCost`, `sizeIndex`, `withSizes`.
- `lean/VE/Cardinality/Theorems.lean`: `evalBy_eq`, `sizeIndex_get`, `regionSizes_eq`, `withSizes_eq`.
- `lean/VE/Cardinality/Run.lean`: `countermodel`, `sizesJson`, the `countermodel` kind in `runCase`.
- `lean/VE/Cardinality/RunTheorems.lean`: `sortDomains_valid`, `sizesJson_regionSizes`, `countermodel_sound`.
- `lean/VE/Cardinality/RunExamples.lean`: the countermodel guards and the growing chain.
- `lean/ResponseShape/Schemas/Cardinality.lean`, `Encoders/Cardinality.lean`: the row and its proof.
- `tests/test_cardinality_service.py`, `tests/data/route-cases.jsonl`, `relay-gate-cases.jsonl`, `tools/relay-gate-allow.json` (B0: `sizes`).
- `tools/trust-classes.json`, `ve/assurance-manifest.json` (Run.lean re-pinned), `docs/CONSOLIDATION-PLAN.md` (step 7).
