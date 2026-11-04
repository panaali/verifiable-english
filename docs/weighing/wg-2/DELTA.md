# wg-2 delta: weighing's block, strength, conditions and grants (`lean/VE/Weighing/{Tree,Conditions,Examples}.lean`)

Base: `git merge-base HEAD main` (c3d9ea938).

**Public output: none changes.** No service mode, runner, decoder or encoder reads `VE.Weighing.Tree`, `Conditions` or
`Examples`. Only the aggregate `lean/VE.lean` and the generated `lean/VE/Audit.lean` import them. `refsOk`'s two
refusal texts now come from `VE.Acts.splitRefusal`, with the same bytes (`Acts/ElaborateExamples.lean`'s guards at
lines 150-155, 218, 232-240 pass unchanged). No Python or Rust file changes. No verdict, diagnostic, fault order,
English line or byte changes, so none of these is a row below.

## User-visible deltas

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0, S +132, untied V -1,
trusted +131 against the merge base ("PASS: K, S and untied [V] within c3d9ea9380cb and the allowances introduced
since"). It is recorded as one allowance (S 132) in `docs/trust-baseline.json` with `trust_map.py --allow`. R16's cap
is 150 lines per item, none of them in K. The ties-pass row that R16 asks for is in manage-agents FOLLOW-UPS.md,
section "## wg-2".

| # | File | Trusted lines (class, declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Weighing/Tree.lean` | +68, all S: `CondKind`, `Target`, `CondDecl`, `FactorDecl`, `GrantDecl`, `WeighEnv`, `WeighDoc`, `nodeNamed`, `ruleSorts`, `targetSorts`, `targetF`, `targetExists` (`rankOrder`, `strictPair`, `WeighEnv.empty` are G[V], tied to the theorems that state them) | `lean/VE/Weighing/Examples.lean`'s `#guard`s; one hand mutant per definition killed by a guard ([mutants.json](mutants.json)); trust mutants ([trust-mutants.json](trust-mutants.json)) | R16 |
| 2 | `lean/VE/Weighing/Conditions.lean` | +64, all S: `strengthEntries`, `condPremise`, `condEntries`, `grantEdges`, `grantReach`, `grantedThrough`, `grantConds`, `grantEntries`, `weighEntries`, `strengthPremises`, `weighLabelled`, `weighConditions` (`weighPremises` and `WellFormedWeigh` are G[V], tied) | the same | R16 |
| 3 | `lean/VE/Acts/Elaborate.lean` | -1: `splitRefusal` is D[R] (refusal text), and `refsOk` is one line shorter | `Acts/ElaborateExamples.lean:150` and W-λ's guard (`Examples.lean:74`) | R16 |
