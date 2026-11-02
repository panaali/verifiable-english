# wg-6a delta: weighing's zone interface definitions (`lean/VE/Weighing/Zone.lean`)

Base: `git merge-base HEAD main` (1d9ad881d). wg-6a adds six definitions of weighing-PLAN section 3.4 (at
bda82d18c) and their fixtures; DRI decision reviews/dri-decisions-20261031-df-5-weighing-names.md item 1.

**Public output: none changes.** No service mode, runner, decoder or encoder reads `VE.Weighing.*`: the two new
modules are imported only by the aggregate `lean/VE.lean` and the generated `lean/VE/Audit.lean`
(`grep -rn "VE.Weighing" lean --include=*.lean` lists only those two and the files themselves). No Python or Rust file
changes. No verdict, diagnostic, fault order, English line, byte or CPU figure changes, so none is a row below.

## User-visible deltas

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0, S +31, untied V
+0, trusted +31 against the merge base ("PASS: K, S and untied [V] within 1d9ad881def5 and the allowances introduced
since"); recorded as one allowance (S 31) in `docs/trust-baseline.json` with `trust_map.py --allow`. R16's cap is 150
lines per item, none in K. The ties-pass row R16 asks for is in manage-agents FOLLOW-UPS.md, section "## wg-6a".

| # | File | Trusted lines (class, declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Weighing/Zone.lean` | +31, all S: `decisionAtoms`, `openNames`, `AdmissibleCompletion`, `OutcomeIn`, `SettledZ`, `ZoneUnknown` | `lean/VE/Weighing/ZoneExamples.lean`: the `#guard`s at lines 20, 23 and 37 (`decisionAtoms`, `openNames` on DF-α and on a two-rule document), the proofs `admissible0`, `notAdmissible1`, `outcome_x`, `not_outcome_y`, `settled_x`, `not_settled_x_false`, `not_settled_vacuous` and the `ZoneUnknown` examples; 6 seeded bugs, one per definition, all killed ([mutants.json](mutants.json)); trust mutants 31 KILLED, 20 ALLOWED, 0 SURVIVOR, 0 UNKNOWN ([trust-mutants.json](trust-mutants.json), allow file [trust-mutants-allow.json](trust-mutants-allow.json)) | R16 (DRI-RULINGS.md) |
