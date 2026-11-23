# date-arith-build: deltas

Orchestrator ruling: manage-agents `reviews/dri-ruling-date-arith-20261123.md` (item 1: build it, the trusted core grows
by at most +135 kernel lines). Design: manage-agents `reviews/spare/date-arith/` (PROPOSAL.md frozen, SIZING.md sections
0, 2, 3 and 9, CHALLENGE.md). Build report: [REPORT.md](REPORT.md).

## What a user sees

- The `quantity` mode accepts two new nodes: the day term `["cal", E]` and the formula `["cal_cmp", op, E1, E2]`, with
  the ground date expressions `E` of docs/spec/units-schema.md section 6.2a. Lean works them out while decoding; the
  checked formula sees a day number (from 1970) or, for a comparison with a date before 1970, `top`/`bottom`.
- A statement with such nodes carries `inputs` (each `cal`/`cal_cmp` node's source, compressed): they are in its meaning
  id's canonical object and in the document report's claim (`ve/backends/lean_service_schema/quantity.json`, `claim`).
- Every request without these nodes answers byte for byte as before: no `inputs`, the same `Q`, meaning ids and reports.
  A request that sent these node names before got "Invalid quantity term" / "Unknown quantity formula cal_cmp"; it is
  now decoded (quantity) or refused with "UnsupportedProfile: ground date expressions are not admitted on the
  cardinality route" (cardinality, which binds no inputs).
- New shell module `ve/surface/dates.py` (the written form of PROPOSAL 2.1-2.4 lowered to these nodes, with the C2 and
  C3 rules). No route calls it yet; the four-laws re-measure (row date-arith-remeasure) will.

Limits (ruling item 4, and the build): tables and "deemed to be" lines are not written; dates outside 1900..9999 are
refused, and a date that becomes a day number must lie in 1970..9999; day offsets of a ground date are 0..3660 days (no
"minus N days" on a ground date: Opus review B8); an age whose target month lacks the birth day (29 February, or for
example 31 March plus 66 years and 6 months) is refused unless a reading is written, never guessed (C11, review B11);
the real-text tests were same-family.

## Trust base

| # | What | Measure | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | Kernel growth on the `quantity` path: `Civil.addMonths`, `Civil.MonthsLater`, `nthWeekday`, `Civil.weekday`, `parseIsoFrom`, `minGroundYear`, `Civil.Ground`, `MonthEnd` (Calendar); `elabCal`, `calDay`, `elabCalCmp`, `calNode`, `CalDenotes`, `CalOrder`, `monthEndOf`, `calInputs`, `inputsField`, the `cal`/`cal_cmp` cases and the input lines of `statementIds`, `decodeQuantity`, `claimJson` (Wire, Document); listed theorems `elabCal_sound`, `calDay_sound`, `calCmp_sound`, `calDenotes_unique`, `weekday_epoch`, `weekday_succ`, `parseIsoFrom_valid` | `tools/kernel_closure.py`: kernel 9,738 -> 9,869 (+131, cap +135); quantity path 2,190 -> 2,321 (Calendar 57 -> 98, Wire 553 -> 643); docs/kernel/closure-baseline.json, ALLOWANCES.md, kernel-boundary.md target restated at 9,869 | the listed theorems; `lean/VE/Time/CalExamples.lean` (#guard checks); `tests/test_date_arith.py`; trust_mutants (row 2) | SIGNED by the DRI 2026-11-23 (reviews/dri-ruling-date-arith-20261123.md item 1) |
| 2 | Trust growth outside K (`tools/trust_map.py --since df25d3c3b3`): trusted +70 (K +0, S +49, untied V +21): lean/VE/Time/Wire.lean +43, lean/VE/Time/Calendar.lean +24, lean/VE/Cardinality/Wire.lean +2, lean/ResponseShape/Schemas/Quantity.lean +1; tied: `addMonths`, `nthWeekday`, `elabCal`, `calDay`, `elabCalCmp` | +70 <= 150, K +0; ties pass filed (manage-agents FOLLOW-UPS.md, "date-arith-build") | `trust-mutants.json` (`tools/trust_mutants.py --max-mutants 1000 --test lean/VE/Time/WireSound.lean --test lean/ResponseShape/QuantityClaimExamples.lean --allow trust-mutants-allow.json`): TM_SUMMARY; four planted off-by-one errors caught (REPORT.md section 4) | R16 |
