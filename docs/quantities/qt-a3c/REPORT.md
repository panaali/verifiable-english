# qt-a3c report: the `cardinality` service mode (quantities QT-A3, third part)

No DRI signature is reserved. Delivered: the mode `cardinality` (registry, dispatch, `runMode_cardinality`, `DEADLINES`), `cardinality.json` with `runCaseReported_fits`, the `cardinality@0` row of AR-10's table with its
composition theorem `gate_cardinality`, P3 charged as the erased problem is built (`chargedNodes`, `problemChecks_eq`), and the route cases FA1, FA1b and the hostile set.
Trust: V +12, K +0, S +0 (R16; +16 before fix round 1). DELTA rows 1–2 cite SYNTHESIS 2.2 in me-2b's wording, row 3 cites R2, row 4 cites R16. Size: about 780 hand-written lines, over the ~600 guide (see "Size").
Next: **qt-a3cb**, the `countermodel` case; then qt-a3d (`Document.lean`, `Render.lean`) and QT-A4. Fix round 1 (review F1): the region structure is computed once per problem and the erased problem built once ("Fix round 1"). Fix round 2 (loop recheck F5): the counted universals, sorts and
predicates are deduplicated in near-linear time ("Fix round 2").

## Statement gate

The QT-A3 statements were reviewed in QT-0 (manage-agents `quantities-p3ver1.final.md`; qt-a3's REPORT). This item
proves two of them. Each equals spec 4.3's text after whitespace normalisation, checked by a script over
`docs/spec/quantities.md`, `Protocol.lean` and `Encoders/Cardinality.lean`:
- `VE.Service.runMode_cardinality (j : Json) : runMode .cardinality j = VE.Cardinality.Run.runCaseReported j := rfl`,
  which is also the plan's text;
- `ResponseShape.Encoders.Cardinality.runCaseReported_fits (j : Json) : Fits j Skeletons.cardinality (VE.Cardinality.Run.runCaseReported j)`.
  This is spec 4.3's form. The plan's block writes `ResponseShape.Fits ResponseShape.Schemas.Cardinality.row …` and says QT-0 names the predicate, which spec 4.3 does.

qt-a3's and qt-a3b's statements are unchanged. `checkCertificate`'s body is unchanged; its `problemChecks` is now
charged (below), and `checkCertificate_sound` builds as before. `lean/statements.txt` only gains lines. The new
helper theorems name no plan statement: `gate_cardinality`, `sublist_of_sorted`, `problemChecks_eq`,
`foldl_capped_gt`, `foldl_capped_ge`, `foldl_add_ge`, `regionsJson_fits`, `erasedJson_fits`, `certificate_kind`
and `runCase_fits`. All use only the standard axioms (`python3 lean/audit.py`: PASS).

## Plan rows (the task's order)

| Row | Delivered | Where, checked by |
|---|---|---|
| (1) Registry entry, dispatch, `runMode_cardinality` | yes: `Mode.cardinality`, its name and `modes` entry; `runMode .cardinality` | `Registry.lean`, `Protocol.lean`; `modes_complete`; handshake `envelope.json` (generated); `test_lean_service.py::test_handshake` |
| (1) `MODES`, `DEADLINES` | `MODES` reads the handshake (generated). `DEADLINES["cardinality"] = (60.0, 60.0)`, W6a's `quantity` deadline | `test_the_deadline_keys_are_the_handshakes_modes`; mutant `py-deadline` |
| (2) `cardinality.json` shape and encoder, `runCaseReported_fits` | yes. The row is typed to the leaves. The cardinality and W6a identities are under separate names. There is one statement per request premise (`x-length`), and each region constant's sort is a request finite sort (`x-references`). An admission has the region table and the erased problem; a certificate case has `valid`. A refusal carries `valid: false` exactly in a certificate case | `Schemas/Cardinality.lean`, `Encoders/Cardinality.lean`; `test_cardinality_service.py::test_answers_are_typed_and_bound_to_their_request`; `test_route_row_schemas.py` (corpus, fuzz, weakenings `cardinality-sorts-unbound`, `cardinality-premises-unbound`); relay gate (4,404 refused, 50 allowed by entry) |
| (3) `cardinality@0` table row and composition theorem | yes. The row requires `order@0`, `relational-fol@0` and `time@0`, and refuses every other table profile except `documents@1` and `judgments@0` (the document layer, whose own row composes it: refusing it would break jt-2's `gate_judgments`). `gate_cardinality`: with `cardinality@0` and without `judgments@0`, the gate admits exactly E2's lists (`Wire.profileLists`), on the frozen route. Python's environment list leaves it out (`modeProfiles`) until QT-A4 | `Gate.lean`; `Compose/Examples.lean` QT-A3 guards (both sides of every boundary); `test_profile_table.py` |
| (4) Route cases FA1, FA1b, hostile set | 19 cases in `tests/data/route-cases.jsonl`: FA1 admitted and certified (`valid: true`), FA1b admitted (no `kind`) and certified (`valid: false`), FA1 with its regenerated tables claimed; forged region table, forged erased problem, FA11's stale certificate, a malformed certificate, the kind `countermodel` (refused here; qt-a3cb), E2, S1, S5 (the plan's seeded bug), S7, S8, S10, P1, P2, P3 | `test_cardinality_service.py::test_route_cases_answer_as_recorded` |
| (5) `countermodel` case | **qt-a3cb** (size rule) | FOLLOW-UPS "## qt-a3c" |
| Evaluated once, size charged (the DRI's rule of 2026-10-27) | P3 is charged as the erased problem is built (`erasedThunks`, `chargedNodes`): each formula is built only while the total is within 10,000 nodes. `problemChecks_eq` proves the same verdict and text as W6a's aggregate on the whole problem. The growing chain: a 64-term count erases to over 8,000 nodes, 64 times its terms' source. 200 of them would build 1.6 million erased nodes; now the build stops after two (`10000 < n < 20000`), with W6a's text. Fix round 1: the region structure (`regionData`: counted sorts, predicates per sort, counted universals) is computed once per problem after P1 and its table once after P2 (`checkedRegions`); the erasure, the bridges and `CEnv.elab` read them (`eraseBy`, `bridgeBy`, `elabBy`); the charge keeps each formula it builds, and the answer and the replay read that list (`charge`, `checkedProblem`) | `RunExamples.lean` charged guards; route case `p3-charged`; mutant `charged-nostop` |
| No `ve/profiles.py` row, no `Document.lean`, `Render.lean`, `lean/VE/Calc/`, `lean/VE/Arith/`, `ve/document/` edit | none edited. Two proofs in `Dispatch.lean`, `todayGate_base` and `rowChecks_erase`, gain the new row's facts, as ap-1b's and jt-2's rows did; their statements are unchanged | |
| `ve/assurance-manifest.json`, `ROADMAP.md` | manifest: `Run.lean`'s pin and the decoder total re-measured, and `Encoders/Cardinality.lean` classified (`other_json`). `ROADMAP.md`: the trust-cost line | `test_assurance_manifest.py` |

Overlap (at the start; every branch in flight): `lean/VE.lean` (ap-2c, sc-5rb), `tools/trust-classes.json`
(ap-2c, sc-5rb) and `ve/assurance-manifest.json` (sc-5rb). All three are additive lines in shared tables. No other
hand-written file is shared.

## Seeded bugs

[`mutants.json`](mutants.json): 11 of 11 killed (`uv run python tools/mutants.py docs/quantities/qt-a3c/mutants.json
--no-baseline`, [evidence/mutants-run.json](evidence/mutants-run.json)). Lean and Python changed; no Rust.

| Mutant | File | Killed by |
|---|---|---|
| `row-requires` (row without `time@0`) | `lean/VE/Compose/Dispatch.lean` | `Compose/Examples.lean` QT-A3 refusal guard |
| `others-norms` | `Dispatch.lean`, `cardinalityOthers` | same guard (`cardinality@0 with norms@0`) |
| `modeProfiles-empty` | `Dispatch.lean`, `modeProfiles` | `environmentProfiles` guard |
| `registry-name` | `lean/VE/Service/Registry.lean` | `ResponseShape/Schemas.lean` registry guard |
| `dispatch-w6a` (W6a's runner for the mode) | `lean/VE/Service/Protocol.lean` | `ResponseShape.Encoders.runMode_fits` (the ve_service build of the service test) |
| `encoder-statement` (no `meaning_id`) | `lean/VE/Cardinality/Run.lean` | `runCaseReported_fits` |
| `tactic-certificate` | `lean/ResponseShape/Encoders/Cardinality.lean` | `runCase_fits` |
| `charged-nostop` | `Run.lean`, `chargedNodes` | `RunExamples.lean` charged guard |
| `charged-bridges` | `Run.lean`, `erasedThunks` | `problemChecks_eq` |
| `charged-text` | `Run.lean`, `problemChecks` | `RunExamples.lean` P3 guards |
| `py-deadline` | `ve/backends/lean_service.py` | `tests/test_lean_service.py::test_the_deadline_keys_are_the_handshakes_modes` |

Mechanical mutants (R16, checklist 13a): `mac-pytest.sh --trustmut -- --max-mutants 1000 --allow
docs/quantities/qt-a3c/trust-mutants-allow.json` on ve-mac-1, [trust-mutants.json](trust-mutants.json): 5
definitions, 88 mutants: 71 KILLED, 17 ALLOWED, 0 SURVIVOR, 0 UNKNOWN, exit 0. The first run had 34 survivors and 8 UNKNOWN.
`cardinalityOthers`' 15 are killed by a new guard: the row refuses exactly every other table profile
(`Compose/Examples.lean`). The tactic macro's 10 left the trusted set: it only builds proofs, so it is now P, as
calc's is. The rest are allowed in [trust-mutants-allow.json](trust-mutants-allow.json): `modes` (killed by the proof
`modes_complete`, as me-2b's), `Schemas.files` (does not elaborate, as me-2b's), and `environmentProfiles`. Those are
equivalent mutants (dropping the last base row, which is `cardinality@0` and filtered anyway; `take 1` of
one-element lists) and one that does not elaborate.

## Trust, size and evidence

- Trust (`tools/trust_map.py --check`, final tree, against `b8eac7455`): K +0, S +0, untied V +12 (+16 before fix round 1, `Run.lean` −4; DELTA row 4,
  R16; `docs/trust-baseline.json`; FOLLOW-UPS "## qt-a3c" ties pass). The shapes, skeleton and P3 helpers are G[R].
  `problemChecks` is tied to `problemChecks_eq`.
- Size (`git diff --numstat` against the merge base, generated files and evidence JSON excluded): about 780 lines.
  Lean about 460: the shape 158, `Gate.lean` 92, the encoder 67, `RunTheorems` 42, and the table, runner and guards
  about 100. Tests and fixtures about 160; side tables about 135 (`relay-gate-allow.json` 59, `trust-classes.json`
  47, allowances, manifest); docs about 30 before this report. It is over the ~600 guide because (3) and (4) each
  need the earlier parts to be exercised, and the DRI's charge rule and the relay gate's fixtures and allowances,
  which the selected tests asked for, came on top. The `countermodel` case was cut to qt-a3cb.
- Selected tests (`mac-pytest.sh --select`, on `fe156656`): 4 failures, all in data this new mode needs. These were
  the binding census answers, the relay-gate fixtures and allowances (which found the untyped `predicates` map, now an
  object), and the malformed-response seed. After the fix, the failed ids and the tests that read the changed shape
  passed: 244 passed. `regen_generated.py --check`: 33 entries fresh. `gate_collection.py --check --prebuilt`:
  0 refused, 0 stale, 0 malformed. No test is listed in `main-known-red.txt` for these files.
- Pilot bytes moved: 0 (estimate; the mode reaches documents only through QT-A4).

## Not delivered (next items)

- **qt-a3cb**: the `countermodel` case (spec 3.9, budgeted as W6a's `refutesB`, through `refutesC_sound`), with the
  region sizes computed once per model and charged (`withRegionsFinite` still reads `regionTable` at each constant;
  no service mode reaches it until then).
- **qt-a3d**: `Document.lean`, `Render.lean`. Then SC-1c and AP-4 in the protocol queue, and QT-A4 (the relay, which
  will bind the region table's predicate names: relay-gate F4 entries for `service:cardinality`).

## Fix round 1 (review `qt-a3c-review.final.md`)

- **F1 (B), the region structure recomputed at every read.** Each count's erasure called `predsOn E fs`, a scan of
  the whole problem, so a problem's cost grew with its size squared. Now:
  - `regionData` (`Regions.lean`) holds the counted sorts, each sort's predicates and the counted universals, each
    computed once; `checkedRegions` builds it after P1 (so predicates are listed for at most 8 sorts) and runs P2 on
    it; `RegionData.table` is built once, after P2.
  - The erasure family reads the predicates from a function (`regionSumBy`, `CountAtom.eraseBy`, `Proportion.eraseBy`,
    `CTerm.eraseBy`, `CFormula.eraseBy`, `bridgeBy`); the statements' forms (`regionSum`, `CTerm.erase`,
    `CFormula.erase`, `bridge`) are its instances at `predsOn E fs`, so no statement changed. `CEnv.elab` reads its
    table once (`elabBy`) rather than at each constant. Sweep (b): `countedUniversals` reads the counted sorts once
    (`countedAmong`). Sweep (c): `regionsJson` and `nonnegOf` read the one table.
  - Sweep (d): the charge keeps every formula it builds (`charge`); the runner reads that list for the answer
    (`problemJson`), the identities (`idsOf`) and the replay (`checkErased`), so the erased problem is built once.
  - Same behaviour, proved: `regionData_predsOn`, `regionData_table`, `checkedRegions_eq` (`Theorems.lean`);
    `charge_fst`, `charge_snd`, `checkedProblem_eq`, `checkErased_eq` (`RunTheorems.lean`). The recorded route cases
    answer as before.
  - Measured (the review's probe, `ve_service` wall clock): 50 count premises 10.9 s before, 3.2 s after; 150 premises
    52.6 s before, 8.6 s after (ratio 4.8 before here, 6.7 in the review; 2.7 after); 200 premises 10.6 s (67.5 s in
    the review); 280 premises refused by P3 after 10.2 s (55.8 s). Regression benchmark:
    `tools/bench/test_perf.py::test_cardinality_region_structure_once` (CPU 1.49 s and 4.32 s, baselines recorded; it
    requires the 150-premise CPU under five times the 50-premise CPU).
  - Rest of the class, probed: the first-use deduplication (`firstUse`) is quadratic in the number of distinct items,
    but sorts and predicates are bounded by the environment's 256-name vocabulary limit; distinct counted universal
    statements, which that limit does not bound, cost 3.3 s at 8,000 and 6.8 s at 16,000 (linear to the line limit).
    That holds only for statements that differ early; the loop recheck's F5 sent statements that differ at the end
    (quadratic), fixed in round 2.
    `withRegionsFinite` (the countermodel check) is not on a service path; qt-a3cb's case brings it there.
  - Seeded bugs: `mutants-fix1.json`, 6/6 killed (`evidence/mutants-fix1-run.json`): `regions-rescan` (the base's
    rescanning erasure, killed by the benchmark), `charge-keeps` (route cases `fa1-claimed`, `fa1-certificate`) and
    `charge-keeps-proof` (`charge_snd`), `preds-row` (`regionData_predsOn`) and `preds-row-service` (route cases),
    `elab-once` (`regionSum_typed`). Lean only: no Python or Rust product code changed.
  - Trust mutants of the round (`--base aa2803bcb`, the trusted lines it changed: `regionsJson`, `runCase`):
    `trust-mutants-fix1.json`, 23 KILLED, 0 SURVIVOR, 4 ALLOWED (list-empty mutants that do not elaborate, reasons in
    `trust-mutants-allow.json`), 8 INVALID, exit 0. Trust: untied V +12 (+16 before; `Run.lean` −4), DELTA row 4.
- **F2, F3, F4 (C)**: not changed in this round (F2 is QT-A4's relay, F3 is size, F4 the wording of a signed DELTA row).

## Fix round 2 (loop recheck `qt-a3c-looprecheck1.final.md`)

- **F5 (B), the dedup of the counted universals is quadratic and runs before P3.** `firstUse` compared each item with
  every item kept before it (`List.contains`) and appended it (`acc ++ [x]`). Universal statements that differ only
  at the end cost a full comparison each, so the dedup cost (statements)² × size before P3 refused the request.
  The class is every first-use dedup of request data on the service path: `countedSorts` (count bodies' sorts),
  `countedAmong` (the universals) and `predsAmong` (each sort's predicates) all ran `firstUse` before P1, P2 or P3.
  - Now: `firstUseH` (`Regions.lean`) keeps a hash set of the items seen and an array in first-use order. Each
    item is hashed once (derived `Hashable` of `QTerm`, `QFormula` and `Body`, over the whole item) and compared only
    with the items in its bucket. `firstUseH_eq` proves `firstUseH xs = firstUse xs` (same items, same order) for any
    lawful `BEq`. The three definitions keep `firstUse`, so the kernel still evaluates them (`decide +kernel` in
    `Examples.lean`) and no theorem changed. `@[csimp]` lemmas (`countedSorts_eq_H`, `countedAmong_eq_H`,
    `predsAmong_eq_H`) make compiled code run the hash-set versions. They come right after each definition, before
    its callers are compiled. There is no Python or Rust copy of this code.
  - Same answers, proved: `firstUseH_eq` and the three `@[csimp]` equalities; the recorded route cases answer as
    before. No DELTA row, as for P3's charge: the verdicts and texts are equal by theorem.
  - PROBE F5 (`ve_service` wall clock): 1,800 statements 3.4 s and 5,400 statements 26.9 s before (ratio 7.9); 1.7 s
    and 5.1 s after (ratio 3.1). Regression tests:
    - `tools/bench/test_perf.py::test_cardinality_universal_dedup_near_linear`, the probe as a CPU benchmark. Its
      baselines are 1.37 s and 4.10 s, and it requires the larger CPU under 4.5 times the smaller.
    - `tests/test_cardinality_service.py::test_universals_are_bridged_once_in_first_use_order`, with no timing: sixteen
      statements that differ only at the end, then the same sixteen in reverse order. Each is bridged once, in
      first-use order, with the sixteen-statement request's region table.
  - Seeded bugs: `mutants-fix2.json`, 4/4 killed (`evidence/mutants-fix2-run.json`):
    - `dedup-csimp-dropped` (countedAmong's `@[csimp]` removed) and `dedup-hash-constant` (a constant hash of formulas
      and bodies): both killed by the benchmark.
    - `dedup-step-no-insert` (an item kept but not added to the set): killed by `firstUseStep_inv`.
    - `dedup-step-no-insert-service` (the same bug with its proof bypassed): killed by
      `test_universals_are_bridged_once_in_first_use_order` and the route cases.

    Lean only.
  - Trust: the new definitions and instances are class C (checked code). `tools/trust_map.py --check --since
    3694f9791` gives trusted +0, so the round has no trusted line for trust mutants. The item total is unchanged:
    untied V +12 (DELTA row 4).

## Self-review against BUILDER-CHECKLIST

1. PASS: every field of genuine answers dropped, emptied, duplicated, retyped (null, true, 7, "7", [], {}, 10,000-deep) and rebound: `tools/relay_mutation_gate.py --route service:cardinality` (4,404 refused, 50 allowed by named entries B0, F4, QTA3C-1); `tests/test_relay_mutation_gate.py`; `tests/test_route_row_schemas.py`.
2. PASS: plan-row table above with tests; no Python copy of a Lean decision (the table row's texts are the table's own, and Python reads `profile_table.json`); no permanent report test; overlap listed.
3. PASS: `mutants.json` 11/11 (`evidence/mutants-run.json`), Lean and Python; `trust-mutants.json` exit 0.
4. PASS: no existing answer changes: `problemChecks_eq` (same P3 verdict and text); qt-a3b's `RunExamples.lean` guards unchanged and passing; `test_route_row_schemas.py` (Lean side agrees on every mutation). No Rust.
5. PASS: undeclared sort in a region constant, premises dropped or added, id rebound, an admission given `valid`, an extra member: `test_cardinality_service.py::test_answers_are_typed_and_bound_to_their_request`; inputs: `s5-not-finite`, `e2-profiles`, `s1-format` route cases.
6. PASS: no gate run by me (the chain runs it on the final HEAD); evidence is saved (mutants, trust mutants).
7. PASS: DELTA rows 1–2 in me-2b's ruling wording (SYNTHESIS 2.2), row 3 R2, row 4 R16; `review-ready.py --delta-dri-needed`: none.
8. PASS: DELTA rows 1–3 (new mode, table row with the changed refusal text of mixed lists, the served order); `checkers.lock` re-pinned by regen.
9. PASS: `select_tests.py --base <merge-base>` selects `test_cardinality_service.py`, `test_route_row_schemas.py`, `test_relay_mutation_gate.py`, `test_profile_table.py`.
10. PASS: `runCaseReported_fits` breaks on `encoder-statement`; `problemChecks_eq` on `charged-bridges`; `gate_cardinality` is stated about `gateOf profileTable`, the value the callers use.
11. PASS: P3 charged as built, at and past the limit (10,000 / 10,001 nodes, qt-a3b's guards; 200-count chain); no timing in tests.
12. PASS: step-count guard `charged (mentioning 6 :: List.replicate 200 anyCount) top < 20000` (`RunExamples.lean`) fails if the eager build comes back (`charged-nostop`).
13. PASS: no test removed or renamed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.

## FIXMAP
- `lean/VE/Service/Registry.lean`: `Mode.cardinality`, its name, `modes` entry.
- `lean/VE/Service/Protocol.lean`: dispatch line in `runMode`; `runMode_cardinality` (rfl).
- `lean/ResponseShape/Schemas/Cardinality.lean`: the row shape (`admission`, `certificate`, `error`, `regions`, `problem`, `formula`, `body`, `operand`); `x-length` on premises, `x-references` on region sorts.
- `lean/ResponseShape/Encoders/Cardinality.lean`: `regionsJson_fits` :11, `problemJson_fits` :17, `erasedJson_fits` :23, macro `cardinality_rows`, `runCase_fits` :48, `runCaseReported_fits` :64.
- `lean/ResponseShape/{Schemas,Skeletons,Encoders}.lean`: registration (file list, skeleton, `runMode_fits` case).
- `lean/VE/Compose/Dispatch.lean`: `cardinalityOthers` :766, the row :798, `modeProfiles` :826 (in `environmentProfiles`); proofs `todayGate_base` (`hcard`), `rowChecks_erase` (simp set).
- `lean/VE/Compose/Examples.lean`: QT-A3 guards at the end (both sides; the exact-refusals guard).
- `lean/VE/Cardinality/Gate.lean`: `sublist_of_sorted` :12, `gate_cardinality` :37 (spec 4.2 E2 and SYNTHESIS 2.2).
- `lean/VE/Cardinality/Erase.lean`: the erasure reads predicates from `P` (`regionSumBy` :25, `CFormula.eraseBy` :61, `bridgeBy` :90, `nonnegOf` :83); the statements' forms are instances (`regionSum`, `CFormula.erase`, `bridge`: abbrevs).
- `lean/VE/Cardinality/Regions.lean`: `countedAmong` :80, `predsAmong` :89, `tableOf` :120, `CEnv.elabBy` :129, `sortLimit` :146, `predicateLimit` :150, `RegionData` :166, `regionData` :187, `checkedRegions` :191; their equalities in `Theorems.lean` (`regionData_predsOn`, `regionData_table`, `checkedRegions_eq`).
- `lean/VE/Cardinality/Run.lean`: `erasedThunks` :29, `chargedNodes` :37, `problemChecks` :43 (P3 charged; spec 4.2), `charge` :49, `checkedProblem` :62, `idsOf` :71, `checkErased` :102, `checkCertificate` :117, `regionsJson` :168, `problemJson` :174, `runCase` :192.
- `lean/VE/Cardinality/RunTheorems.lean`: `erasedJson_problemJson` :44, `erasedThunks_built` :88, `problemChecks_eq` :95, `charge_fst` :117, `charge_snd` :128, `checkedProblem_eq` :144, `checkErased_eq` :163.
- `lean/VE/Cardinality/RunExamples.lean`: `anyCount`, `charged` and the charged guards in the P section.
- `ve/backends/lean_service.py`: `DEADLINES["cardinality"]`.
- `tests/test_cardinality_service.py`: route-case answers, typing and binding mutants. `tests/data/route-cases.jsonl`: the 19 cases (written from the Lean fixtures of `RunExamples.lean`).
- `tests/lean_service_corpus.py` (`recorded`, `cardinality_cases`), `tests/test_route_row_schemas.py` (ROUTE_MODES, two weakenings), `tests/test_profile_table.py`, `tests/test_lean_service.py` (`_SCHEMA_SEEDS`).
- `tests/data/relay-gate-cases.jsonl` (13 cardinality fixtures, kept as `--record` keeps them), `tools/relay-gate-allow.json` (cardinality B0, F4, QTA3C-1), `tests/data/binding-answers.jsonl.gz` (`tools/binding_census.py --answers`).
- `tools/trust-classes.json`, `docs/trust-baseline.json` (R16 allowance V +16; the item measures +12), `ve/assurance-manifest.json` (Run.lean pin, decoder total, encoder `other_json`).
- Regression tests: `uv run pytest -q tests/test_cardinality_service.py tests/test_profile_table.py tests/test_cardinality_exercised.py tests/test_assurance_manifest.py tests/test_trust_budget.py`; `uv run pytest -q -n 8 tests/test_route_row_schemas.py tests/test_relay_mutation_gate.py`; `cd lean && lake build VE.Compose.Examples VE.Cardinality.RunExamples VE.Cardinality.Gate ResponseShape.Encoders`.
- Generated (never by hand): `uv run python tools/regen_generated.py --write` (cardinality.json and envelope.json, profile_table.json, inventories, Audit files, binding census, checkers.lock); the schema writer needs `lake build ve_response_decode` first; a new mode needs `tools/response_schemas.py --write` before the regen pass (the service's handshake is checked against envelope.json).
- Mutants: `uv run python tools/mutants.py docs/quantities/qt-a3c/mutants.json --no-baseline --evidence docs/quantities/qt-a3c/evidence/mutants-run.json`.
- Fix round 1: `uv run python tools/mutants.py docs/quantities/qt-a3c/mutants-fix1.json --no-baseline --evidence docs/quantities/qt-a3c/evidence/mutants-fix1-run.json` (pinned build first); benchmark `uv run --frozen python -m pytest tools/bench/test_perf.py -k cardinality_region` (needs a pinned build: the file's collection starts the service).
- Fix round 2: `uv run python tools/mutants.py docs/quantities/qt-a3c/mutants-fix2.json --no-baseline --evidence docs/quantities/qt-a3c/evidence/mutants-fix2-run.json` (pinned build first); benchmark `uv run --frozen python -m pytest tools/bench/test_perf.py -k universal_dedup`; `lean/VE/Cardinality/Regions.lean`: `firstUseH` :25, `firstUseH_eq` :51, the derived `Hashable` instances :54, `countedSortsH`/`countedSorts_eq_H`, `countedAmongH`/`countedAmong_eq_H`, `predsAmongH`/`predsAmong_eq_H` (after each definition).
- Trust mutants: `zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/quantities/qt-a3c/trust-mutants-allow.json --rescore docs/quantities/qt-a3c/trust-mutants.json --json docs/quantities/qt-a3c/trust-mutants.json`.
## END FIXMAP
