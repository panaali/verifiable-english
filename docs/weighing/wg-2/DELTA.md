# wg-2 delta: weighing's block, strength, conditions and grants (`lean/VE/Weighing/{Tree,Conditions,Examples}.lean`)

Base: `git merge-base HEAD main` (c3d9ea938).

**Public output: none changes.** No service mode, runner, decoder or encoder reads `VE.Weighing.Tree`, `Conditions` or
`Examples`. Only the aggregate `lean/VE.lean` and the generated `lean/VE/Audit.lean` import them. `refsOk`'s two
refusal texts now come from `VE.Acts.splitRefusal`, with the same bytes (`Acts/ElaborateExamples.lean`'s guards at
lines 150-155, 218, 232-240 pass unchanged). No Rust file changes. One Python file changes, and it is not product
output: `tools/layer_policy.py` puts `VE.Weighing.{Tree,Conditions,Examples}` at Lean layer 3, which
`tools/check_lean_imports.py` and test selection read (the layering question stays open with the DRI: REPORT section
3). No verdict, diagnostic, fault order, English line or byte changes, so none of these is a row below.

## User-visible deltas

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code (f6e03a5df, with the
restored theorems and `strictWitness`): K +0, S +132, untied V -1, trusted +131 against the merge base ("PASS: K, S and untied [V] within c3d9ea9380cb and the allowances introduced
since"). It is recorded as one allowance (S 132) in `docs/trust-baseline.json` with `trust_map.py --allow`. R16's cap
is 150 lines per item, none of them in K. The ties-pass row that R16 asks for is in manage-agents FOLLOW-UPS.md,
section "## wg-2". The definitions the fix round restored add no trusted line: `chainEdges`, `RankChain`,
`strictWitness`, `strictFlag` and `SameBase` are G[V] tied to the theorems that state them, `chainsFrom` is C (a
search `strictWitness_isSome` and `strictWitness_chain` prove sound and complete), `chainLt` is G[I] (the display
order of the witness) and `freeWitness` is P (`tools/trust-classes.json`).

| # | File | Trusted lines (class, declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Weighing/Tree.lean` | +68, all S: `CondKind`, `Target`, `CondDecl`, `FactorDecl`, `GrantDecl`, `WeighEnv`, `WeighDoc`, `nodeNamed`, `ruleSorts`, `targetSorts`, `targetF`, `targetExists` (`rankOrder`, `strictPair`, `WeighEnv.empty` are G[V], tied to the theorems that state them) | `lean/VE/Weighing/Examples.lean`'s `#guard`s; one hand mutant per definition killed by a guard ([mutants.json](mutants.json)); trust mutants ([trust-mutants.json](trust-mutants.json)) | R16 |
| 2 | `lean/VE/Weighing/Conditions.lean` | +64, all S: `strengthEntries`, `condPremise`, `condEntries`, `grantEdges`, `grantReach`, `grantedThrough`, `grantConds`, `grantEntries`, `weighEntries`, `strengthPremises`, `weighLabelled`, `weighConditions` (`weighPremises` and `WellFormedWeigh` are G[V], tied) | the same | R16 |
| 3 | `lean/VE/Acts/Elaborate.lean` | -1: `splitRefusal` is D[R] (refusal text), and `refsOk` is one line shorter | `Acts/ElaborateExamples.lean:150` and W-λ's guard (`Examples.lean:74`) | R16 |

## Cut by the DRI (2026-11-04)

Changing an approved Lean theorem statement is never covered by a standing ruling (DRI-RULINGS.md, "Never covered"). The DRI cut `strength_iff` from wg-2 (item 1) and signed its added hypothesis for follow-up row wg-2-siff (item 2): reviews/dri-decisions-20261104-wg-2-strength.md.

| # | File | Row | Evidence | Ruling |
|---|---|---|---|---|
| 4 | `lean/VE/Weighing/Conditions.lean` | `strength_iff` (weighing.md 5.1) is not delivered. As approved it is false: on a directly built document with a regulated `_x_permitted`, every hypothesis holds at `(_x_permitted, l, c)`, the premise is in `Str_T` (it is `(x_permitted, l, c_)`'s, the same `outweighs` name), and the triple is no decision. The decoder refuses the name ("Invalid ASCII identifier"), so no wire document reaches it. Candidate fixes for the DRI: a hypothesis that `a` (or every regulated name) begins with a letter, or a soft check that refuses such names | `lean/VE/Weighing/Examples.lean` (`cxD`, `cxX`, `cxW` and the decoder guard); `strength_mem` proves the reverse direction for every triple | SIGNED by the DRI 2026-11-04 (reviews/dri-decisions-20261104-wg-2-strength.md item 1) |
