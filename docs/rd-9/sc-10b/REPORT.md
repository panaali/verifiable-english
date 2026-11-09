# sc-10b report: the three superposition theorems of 13.3

**Status:** built. Branch `feature/sc-10b`; the code is final at the commit that adds this version of the report (its
parent `51fb60836` holds all the code; the report and `mutants.json` follow). **Signatures:** none reserved. Trusted +0,
no DELTA row.

## Task rows

| Row | Delivered | Evidence |
| --- | --- | --- |
| (1) `sd_superpose_conflict_free`, `sd_superpose_all`, `sd_superpose_countermodel`, word for word | yes | `SoftSup.lean:1568`, `:1597`, `:1658`. `uv run python tools/check_rd9_sc1_statements.py`: "SC-10 superposition PASS: 11 exact after whitespace normalization"; `#print axioms` on each: `propext, Classical.choice, Quot.sound` |
| (1) reuse `fillPremisesSD_pull`, `supX_pull`, `fill_sim`; no second copy | yes. `outcome_pullF` and `selects_fill_wf` were moved out of `fillPremisesSD_pull` and `selU_canon`, which now call them | How the proofs go |
| (1) size measured before the certificate and countermodel steps | yes: 566 hand-written lines (`git diff --numstat`, commit `4c0a22d46`). A cut asked then was withdrawn by the DRI, who counts proof lines and ruling-required fixtures as exempt (`reviews/dri-decisions-20261109-adv0001.md` item 2) | Size |
| (2) 13.5 fixtures, each direction | yes, see the next table | `SoftSupExamples.lean:210-271`; `test_readings_sd_lean.py` |
| (3) guard for sc-10a F2's `supU` mutant of `sharedEnvSD` | yes | `SoftSupExamples.lean:227`; M5 |
| (4) seeded bugs 1, 2, 3 | yes (M1, M2, M3), plus M4-M7 and P1 | `mutants.json` |
| (5) section 13 in `check_rd9_sc1_statements.py` | yes, with nothing marked not built | rc 0 above; `tests/test_rd9_statements.py` 33 passed |
| (6) inventories via `regen_generated.py --write` | yes, with `--skip route-cases` (it needs a Rust release binary this worktree lacks, and none of its inputs changed) | `51fb60836` |
| sc-10 review F3/F4 (optional) | not done: left to row sc-10-report-head | — |

| 13.5 row | Both sides hold | Both sides fail |
| --- | --- | --- |
| `sd_superpose_conflict_free` | NSD4a and NSD4c under `rs1:1` are CONFLICT-FREE through `readings-verdicts` (`test_sd_superpose_conflict_free_derived_rows`, 2 passed). On the same model, NSD4c is a base with no target (`:218`) | NSD4c and NSD4 under `[]` are CONFLICT on both sides (`:210`). NSD4a with `[]` for `supX` is CONFLICT; with `supX` the model is a base of neither side (`:214-215`) |
| `sd_superpose_all` | under `[(rs1,0)]` the query holds on both sides (`:267`); `(rs1,0)` proved and ALL under `rs1:0` through the route (`test_fsd1_verdicts_query_some_all_none`) | under `[]` there is no certificate, since the countermodel names `(rs1,1)` (`:262-263`) |
| `sd_superpose_countermodel` | NSD1 under `[]`: `modelCheckX` passes with the query false and `localFree`, the bits name `(rs1,1)`, and it is a countermodel on that choice's side (`:262-263`) | read as `(rs1,0)`, the model holds the query (`:265`). Without `hl`: NSD4 passes `modelCheckX` with `⊥` false and is not `localFree` (`:271`) |

**Read-only files edited, each by a DRI ruling, statements unchanged:**
- `Superpose.lean`: `encodes_unique_slot`, with `encodes_unique` its wrapper (`reviews/dri-decisions-20261108-sc-10b.md`).
- `Situation.lean`: `assertions_iff`, with `assertions_canon` proved from it (`reviews/dri-decisions-20261109-sc-10b.md`).

The `statements.txt` diff adds the two lemmas and leaves both originals byte-identical. Overlap checks (23:28Z for
`Superpose.lean`, 00:3xZ for `Situation.lean`): no other branch touches either file. `tools/trust-classes.json` is
shared by eight branches; each adds its own module's entries.

## How the proofs go

- **Down** (`pullF_baseX`): `encodes_unique_slot` and `encodes_atoms` give the choice. `pullF_admissible`,
  `pullF_literals`, `fillPremisesSD_pull` and `supX_pull` make the filled pull a base of that choice.
  `conflictFree_pullF` reads `fill_sim` on the conflict and pair formulas.
- **Up** (`upB_baseX`): S2a's `upB` is applied to the base with its `unsaid__` tables emptied (`dropUnsaid`), so S2a's
  `upB_admissible` and `pull_upB` apply. `upRel`'s third disjunct keeps the tables (`upB_admissibleF`, `pullF_upB`,
  `pullF_up`). `choiceX_up` carries `choiceX` premise by premise.
- **ALL and countermodel:** each side is read on its filled canonical interpretation. Expansions come from
  `documentExpansion_canon` and `expansion_of_conflictFree`; shared sentences from `shared_canonF`, the assertions from
  `assertions_iff` with `gate_canonF`; the lift from `canon_pullF_up`; and an added point from `canon_adjoin`.
  `sd_superpose_all` replays the certificate with `acceptanceX`. `sd_superpose_countermodel` starts from
  `modelCheckX_sound` and `conflictFree_of_localFree`.

## Size

Rule as the DRI applies it (adv1207 item 3): proof lines for the gated statements and the fixtures a ruling requires do
not count. Counted here: tests +32 −2, tools +6 −3, `trust-classes.json` +13 −2, `mutants.json` +37, this report.
Exempt: `SoftSup.lean` +692 −24, `SoftSupExamples.lean` +86, `Superpose.lean` +11 −5, `Situation.lean` +23 −17.

## Seeded bugs (`mutants.json`)

M1-M7 (Lean) and P1 (Python) were each planted alone on the final code, and all were killed. M1 (`supCertificateCheckSD`
ignoring `A`) is caught by `sd_superpose_all`'s proof, and with that stubbed, by the guard `:80`. M2 (the countermodel's
bits naming another choice) is caught by `sd_superpose_countermodel`'s proof; the fixture `:262-265` pins that the bits
name `(rs1,1)`. M3 (`supX` = `[]`) is caught by two proofs, and with them stubbed, by the NSD4a guard `:214`. M5
(`sharedEnvSD` on `supU`) is caught by `sharedSD_pred`. Before the two new theorems existed, only the guard `:227`
caught it.

## Trust, bytes, tests

- `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0", "PASS".
- Pilot bytes expected: 0 (proofs only; no route reads these theorems yet, so syn2's edit 5 still holds).
- `lake build`: "Build completed successfully (1327 jobs)". `python3 lean/audit.py`: "PASS: 792 source files; 8805 named
  theorem declarations audited".
- Selected tests on the final code: see the last line of this report.

## Spec re-read

- The three statements against `docs/spec/rd-9-soft-chain.md:1818-1848`: compared by the checker (11 exact).
- The 13.5 rows at `:1914` and `:1923`, and the guidance at `:1852-1865`, give the tables above. DRI 20261031 item 4's
  condition (both directions of `sd_superpose_conflict_free` on NSD4a/NSD4c) is met by the first row.

## Self-review against BUILDER-CHECKLIST

1. Typed answers: N.A., no relayed answer or schema.
2. Deliverables: PASS, every task row (Task rows), with no cut.
3. Tests can fail: PASS, `mutants.json` (8 KILLED).
4. Py/Lean/Rust agree: N.A., no answer changes.
5. R8: N.A., no relayed field.
6. Gate evidence: PASS for the selected run on the final code (last line). The full gate is the chain's.
7. Unsigned items: PASS, trusted +0 (`trust_map.py --check`), no DELTA row, both read-only edits ruled.
8. User-visible changes: N.A., none (no route reads the theorems).
9. Selection: PASS, the selected run includes `tests/test_rd9_statements.py`, `tests/test_readings_sd_lean.py` and `lake build`.
10. Statements: PASS, `check_rd9_sc1_statements.py` (11 exact). M2, M6 and M7 show each statement's key part is needed.
11. Budgets: N.A., no evaluator or runner is added.
12. CPU/memory: N.A., no runtime path changes.
13. Removed tests: N.A., none removed or renamed.
14. Both directions: PASS, the 13.5 table above, with the spec re-read.
15. Overclaim, silent cut, checks fail, limits: PASS. No cut; the two read-only edits were asked before they were made; M1-M7 and P1 are recorded. Limits: N.A.

Selected tests: pending (filled in after the run).
