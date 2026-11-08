# sc-10b report: `sd_superpose_conflict_free`; `sd_superpose_all` and `sd_superpose_countermodel` move to sc-10bb

**Status:** built, cut under the size rule (cut ruling below). Branch `feature/sc-10b`, code final at `d0002a3a5`
(later commits: the trust ledger and this report). **Signatures:** none reserved. Trusted +0, no DELTA row.

## Task rows

| Row | Delivered | Evidence |
| --- | --- | --- |
| (1) `sd_superpose_conflict_free`, word for word, no `sorry`, no new axiom | yes | `SoftSup.lean:1357`; `check_rd9_sc1_statements.py` "SC-10 superposition PASS: 9 exact"; `#print axioms`: `propext, Classical.choice, Quot.sound` |
| (1) `sd_superpose_all`, `sd_superpose_countermodel` | **no**: cut to sc-10bb | Cut |
| (1) reuse `fillPremisesSD_pull`, `supX_pull`, `fill_sim`, no second copy | yes. `outcome_pullF` and `selects_fill_wf` were moved out of `fillPremisesSD_pull` and `selU_canon`, which now call them | `SoftSup.lean` diff |
| (2) 13.5 fixtures of `sd_superpose_conflict_free`, both directions | yes. CONFLICT on both sides (NSD4c, NSD4 under `[]`; NSD4a with `[]` for `supX`) in Lean. CONFLICT-FREE (NSD4a, NSD4c under `rs1:1`) through `readings-verdicts` | `SoftSupExamples.lean:210-218`; `test_readings_sd_lean.py::test_sd_superpose_conflict_free_derived_rows` (2 passed) |
| (2) fixtures of the two cut theorems | **no**: sc-10bb | — |
| (3) guard killing sc-10a F2's `supU` mutant of `sharedEnvSD` | yes | `SoftSupExamples.lean:227`; mutants M5 |
| (4) seeded bugs 1 and 3; bug 2 | 1, 3: yes (M1, M3). Bug 2 needs the countermodel theorem: sc-10bb | `mutants.json` |
| (5) section 13 in `check_rd9_sc1_statements.py` | yes, with the two cut theorems as its not-built list (it can only shrink; `test_rd9_statements.py` pins it) | `uv run python tools/check_rd9_sc1_statements.py`: rc 0 |
| (6) inventories via `regen_generated.py --write` | yes (`--skip route-cases`: it needs a Rust release binary this worktree lacks; none of its inputs changed) | `3a128d6a2` |
| F3/F4 of sc-10's review | not done: left to row sc-10-report-head | — |

**Superpose.lean** (read-only for this item) gains `encodes_unique_slot`, and `encodes_unique` becomes its wrapper with
its statement unchanged. DRI ruling: `reviews/dri-decisions-20261108-sc-10b.md` item 1. The `statements.txt` diff adds
`encodes_unique_slot` only. No other branch touches the file (overlap check, 23:28Z).

## How the proof goes

- **Down:** `encodes_unique_slot` and `encodes_atoms` give the choice. `pullF_admissible` and `pullF_literals` give the
  admissible pulled base; `fillPremisesSD_pull` and `supX_pull` carry `Fill_T` and `X`. `conflictFree_pullF` gives
  `fill_sim` on the conflict and pair formulas.
- **Up:** S2a's `upB` is applied to the base with its `unsaid__` tables emptied (`dropUnsaid`), so S2a's
  `upB_admissible` and `pull_upB` apply. `upRel`'s third disjunct keeps the tables: `upB_admissibleF`, `pullF_upB`,
  `pullF_up`. `choiceX_up` carries `choiceX` premise by premise: an exception through the frame (S2a's
  `choice_exc_typed`), a coherence premise through `selects_fill_wf`. The empty carrier case is `conflictFree_empty`.

## Cut (size rule)

Before the certificate and countermodel steps, `git diff --numstat $(git merge-base HEAD main)` without generated files
gave 566 hand-written lines (`SoftSup.lean` +403 −24, `Superpose.lean` +11 −5, `SoftSupExamples.lean` +42, tests +27 −5,
tools +14 −5, `mutants.json` +30). Each cut theorem also needs a filled-tree form of S2a's `superpose_situation`. That
means the superposed assertions and `Γ`, `φ` over `sharedEnvSD` read on both canonical interpretations, plus an
expansion of the base. That does not fit in the ~35 lines left. Cut ruling asked:
`inbox/dri/20261108T232753Z-sc-10b-951854.md`.

## Seeded bugs (`mutants.json`)

All five Lean bugs (M1, M3-M6) were killed by a proof or a `#guard`, and P1 (Python, the checker's word) was killed by
`test_rd9_statements.py`. M5 is killed only by the new guard `:227`, so sc-10a F2's survivor is now covered.

## Trust, bytes, tests

- `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 … PASS".
  `dropUnsaid` is classed P and the new fixtures T (`tools/trust-classes.json`).
- Pilot bytes expected: 0 (proofs only; no route reads these theorems, so edit 5 of syn2 still holds).
- `lake build`: "Build completed successfully (1327 jobs)". `python3 lean/audit.py`: "PASS: 792 source files; 8787 named
  theorem declarations audited".
- Selected tests: see the run line below.

## Spec re-read

- `sd_superpose_conflict_free` against `docs/spec/rd-9-soft-chain.md:1818-1824`: the checker compares it word for word.
- 13.5's row for this theorem (`:1914`) gives the fixtures above, and 13.3's guidance (`:1852-1865`) the down/up plan.
  DRI 20261031 item 4's condition (both directions, NSD4a/NSD4c) is met by the Lean CONFLICT rows and the route
  CONFLICT-FREE rows.

## Self-review against BUILDER-CHECKLIST

1. Typed answers: N.A., no relayed answer or schema.
2. Deliverables: PASS with the cut recorded (Task rows, Cut; ruling asked).
3. Tests can fail: PASS, `mutants.json` (6 KILLED).
4. Py/Lean/Rust agree: N.A., no answer changes.
5. R8: N.A., no relayed field.
6. Gate evidence: PASS for the selected tests on the final code (below). The full gate is the chain's.
7. Unsigned items: PASS, trusted +0 (`trust_map.py --check`), no DELTA.
8. User-visible changes: N.A., none (no route reads the theorem).
9. Selection: PASS, the selected run (below) includes `tests/test_rd9_statements.py` and `lake build`.
10. Statements: PASS, `check_rd9_sc1_statements.py` (9 exact); M6 shows `choiceX` is needed on the right.
11. Budgets: N.A., no evaluator or runner is added.
12. CPU/memory: N.A., no runtime path changes.
13. Removed tests: N.A., none removed or renamed.
14. Both directions: PASS, CONFLICT and CONFLICT-FREE fixtures (Task rows (2)), with the spec re-read above.
15. Overclaim, silent cut, checks fail, limits: PASS for the cut (ruling asked before review) and for M1-M6/P1. Limits: N.A.

FOLLOW-UP: sc-10bb `sd_superpose_all` and `sd_superpose_countermodel` (13.3) with their 13.5 fixtures and seeded bug 2
