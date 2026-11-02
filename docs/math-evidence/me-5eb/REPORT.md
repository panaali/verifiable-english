# me-5eb: the R16 ties pass for me-5e

- **Status:** done, ready for review. No DRI signature is reserved and no allowance is raised.
- **What changed:** `lean/VE/Calc/Ties.lean` adds connecting theorems (proofs only). `tools/trust-classes.json` ties `Shown.matches`, `Derive.shown`, `Check.runShown` and `Run.rowJson` to them, and `Run.row` gains one more tie. Trusted lines fall by exactly the 49 tied lines (58,026 → 57,977), all in `VE/Calc/Run.lean`. K, S and approved statements are unchanged.
- **Open items:** four theorems the task named cannot carry a tie under the tool's rule. Each has a connecting theorem instead (see "Deviations").
- **Head:** the last commit on `feature/me-5eb`. Base: main `f3a4da815`, which contains the task's `432763b06`.

## Delivered (task items 1-3)

1. **Re-measure.** I re-measured with `tools/trust_map.py`, using the `walk` and `measure_rev` scripts saved in `evidence/ties-me-5eb/trust-counts.json`.
   - me-5e moved `VE/Calc/Run.lean` from 127 to 170 trusted lines (`795e003bd^1` → `795e003bd`, +43). The file is at 168 on the base.
   - Four of the five declarations in the FOLLOW-UPS row are untied D[V]: `Shown.matches` 8, `Derive.shown` 12, `Check.runShown` 18 and `Run.rowJson` 11, for 49 lines.
   - `Run.row` was already tied G[V] (to `Run.row_outcome`), so it carries 0 trusted lines.
2. **Ties** (all in `lean/VE/Calc/Ties.lean`; the anchors come from each theorem's `-- uses` line in `lean/statements.txt`):

   | Declaration | Tied to | What the statements fix |
   |---|---|---|
   | `Shown.matches` | `Shown.matches_iff`, `Derive.shown_matches`, `Check.followsShown_matches` | The full truth table: holds with a nonempty certificate, fails with a counterexample, and nothing for every other outcome (anchor `Outcome`, S) |
   | `Derive.shown` | `Derive.shown_holds`, `Derive.shown_fails`, `Derive.shown_nothing`, `Derive.shown_matches` | Holds shows a certificate whose replay is checked, so the goal holds wherever the facts and links hold (`Derivation.check_sound`; `QFact.Holds`, S). Fails shows a point where the facts and links hold and the goal does not (`Counterexample.check_sound`; `Answer.point`, S). Every other outcome shows nothing |
   | `Check.runShown` | `Check.runShown_sound`, `_holds`, `_fails`, `_nothing`, `Check.followsShown_matches` | The outcome means its clause (`Check.run_sound`; `OutcomeMeans`, S). A holds row's certificate replays over the lowered premises, and `Follows` holds (S). A fails row's point is a counterexample in claim semantics (`Claim.Holds` at `Answer.point`, S). A claim, and every other outcome, shows nothing |
   | `Run.row` (already tied) | `Run.row_means`, `Run.row_outcome` | The row's outcome means its check's clause, and its shown evidence is `runShown`'s |
   | `Run.rowJson` | `Run.rowJson_outcome`, `Run.rowJson_shown` | `outcome`/`reason` read back as the row's outcome (`outcomes`/`words`, as `outcomeAt` reads them). A holds row writes `certificate` = its steps and `counterexample` = `null`; a fails row writes `null` and one `[name, "n/d"]` per free value read at `Answer.point κ`; every other outcome writes two `null`s |

3. **`trust_map --check` before and after.**
   - Before: PASS, trusted 58,026 (`evidence/ties-me-5eb/check-before.txt`).
   - After: PASS, "K +0, S +0, D +0, G +0, tied +49, … trusted -49; VE/Calc/Run.lean: trusted -49", trusted 57,977 (`check-after.txt`).
   - Per file: `VE/Calc/Run.lean` 168 → 119; `VE/Calc/Ties.lean` 0 → 0 (183 P lines).
   - The fall equals the tied lines: 8 + 12 + 18 + 11 = 49.
   - The numbers are recorded in DELTA row 4 (`docs/math-evidence/me-5e/DELTA.md`), with Ruling cell "R16 ties pass".

## Deviations from the task's named theorems

A tie needs the theorem in `lean/statements.txt`, and its `-- uses` line must name the declaration plus a K, S or untied-[V] anchor (`trust_map.classify`). Four of the named theorems fail that rule:

- **`Check.run_sound`** names `Check.run`, not `runShown`. `Check.runShown_sound` restates it about `(k.runShown ds).1`.
- **`Derivation.check_sound` and `Counterexample.check_sound`** are fact-level statements and never name `runShown`. They are the proofs behind `Check.runShown_holds`/`_fails` and `Derive.shown_holds`/`_fails`, which are the theorems listed in the tie.
- **`Run.row_sound`** names `runCaseReported` and `outcomeAt`, not `Run.row`: the wire builds its rows with `Run.rowOf`. `Run.row_means` connects `Run.row` through the same `Check.run_sound` step.
- **`rowJson_fits` and `runCaseReported_fits`** (`ResponseShape.Encoders.Calc`) are not in `lean/statements.txt`, and `runCaseReported_fits` does not mention `rowJson`. A shape fit also fixes only the form of the row, not its content. `Run.rowJson_shown` takes the same `Shown.matches` hypothesis as `rowJson_fits` and fixes the content instead.

**Statement gate:** no approved statement changed (`python3 tools/lean_statements.py --check`: "PASS: 7418 statements … unchanged" on the committed tree). The item adds only theorems.

**Synthesis-2 edits** (`debates/plan-synthesis-2/edits-math-evidence.md`): this item implements none of them. All five concern plan text: AR-10 rows, durations, `hedged`, budgets and "about".

## Files beyond the task's list

- **`lean/VE.lean`:** one import line. The root import list is hand-kept and union-merged, and `tests/test_lean_default_build.py` requires every source to be built.
- **`tools/layer_policy.py`:** two lines that put `VE.Calc.Ties` in layer 4, beside `VE.Cardinality.RunTheorems`. Without them, `check_lean_imports.py` refused the import of `VE.Calc.Run` as outward.
- **`ve/assurance-manifest.json`:** one `other_json` reason. `test_every_json_handling_lean_file_is_classified` requires one because the file states what `Json.getObjVal?` reads.
- **Generated, through `regen_generated.py --write`:** `lean/statements.txt`, `declarations.txt`, `predicates.txt`, `axioms.txt`, `VE/Audit.lean` and `docs/codemap/*`. The codemap pages other than Calc's were already stale on main, and the regeneration refreshed them.

## Seeded bugs

Each was applied alone and restored; the output is in `evidence/ties-me-5eb/seed-*.txt` and the list in `mutants.json`.

| Id | File | Bug | Fails |
|---|---|---|---|
| S1 | `lean/statements.txt` | drops `rowJson` from `Run.rowJson_shown`'s uses line | `trust_map.py --check` ("does not mention VE.Calc.Run.rowJson"), `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check` |
| S2 | `tools/trust-classes.json` | ties `Shown.matches` to the unrelated `Run.outcomes_words` | same two checks ("does not mention VE.Calc.Shown.matches") |
| L1 | `lean/VE/Calc/Run.lean` | `Shown.matches` also accepts undefined with a counterexample | `lake build VE.Calc.Ties`: `Shown.matches_iff` |
| L2 | `lean/VE/Calc/Run.lean` | `Derive.shown` fails with the point `[]` | `Derive.shown_fails` |
| L3 | `lean/VE/Calc/Run.lean` | `Check.runShown` shows a counterexample for a claim | `Check.runShown_nothing` |
| L4 | `lean/VE/Calc/Run.lean` | `Run.rowJson` swaps the `certificate` and `counterexample` members | `Run.rowJson_shown` |
| L5 | `lean/VE/Calc/Ties.lean` | `Run.row_means` restated without `Run.row` (still true) | `trust_map.py --check`, `test_committed_budget_passes_its_check` |
| P1 | `tools/layer_policy.py` | drops the `VE.Calc.Ties` row | `check_lean_imports.py`, `tests/test_precommit_hook.py::test_large_staged_change_passes` |

- Each of L1-L4 breaks only `Ties.lean`: `Run.lean`'s own theorems and `#guard`s still build. So the ties constrain these definitions beyond what was proved before.
- No Rust code changed.
- `trust_mutants` was not run. This item adds no trusted definition: every new line is P.

## Checks run

- `regen_generated.py --write` (all 35 entries; it builds and audits): "PASS: 722 source files; 7992 named theorem declarations audited".
- `lake build`: 1,229 jobs passed.
- `tools/gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- Selected tests, first run: two failures.
  - The first was an outward import, `check_lean_imports.py`, which also stopped shard 1 from running.
  - The second was `test_precommit_hook.py::test_large_staged_change_passes`.
  - Both were fixed by the layer row.
- Selected tests, second run after that code change: one failure, `test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`, fixed by the manifest reason. Rerunning that id alone passed (`mac-pytest.sh`, VM fallback, "1 passed").
- None of these tests is in `main-known-red.txt`.
- The full gate was not run here; the chain runs it on the final HEAD.

**Spec re-read:**
- `Run.rowJson_shown` checked against `docs/spec/math-evidence.md:1162`: `certificate` on holds, `counterexample` on fails, and one `[name, "n/d"]` per free value read.
- `Run.rowJson_shown` checked against `:3293` and `:3300`: both members are `null` for unknown and undefined rows.
- `Check.runShown_holds` and `_fails` checked against `:1396`: a replayed certificate and a counterexample checked by evaluation, with square links included.

**Pilot bytes:** 0 (no output changes). **Size:** about 540 hand-written lines, under 600. **Next item:** none in this family's chain.

## Self-review against BUILDER-CHECKLIST

1. **N.A.** No relayed answer, schema or relay changed.
2. **PASS.** Items 1-3 are delivered, and the deviations are listed. `check-after.txt` is the evidence.
3. **PASS.** Seeded bugs S1, S2, L1-L5 and P1 fail the checks named in the table above.
4. **N.A.** No Python, Lean or Rust behaviour changed. L1-L4 show that the Lean definitions are pinned.
5. **N.A.** No binding changed.
6. **PASS.** The selected tests ran on the fixed tree, and the one failed id was rerun after its fix. The chain gates the final HEAD.
7. **PASS.** DELTA row 4 cites R16 (`review-ready.py --delta-dri-needed`: "no DELTA row reserved for the DRI").
8. **PASS.** The trust change is in DELTA row 4. No user-visible output changes.
9. **PASS.** The selection contains `tests/test_trust_ratchet.py` and `tests/test_precommit_hook.py`, which S1, S2, L5 and P1 fail.
10. **PASS.** Mutants L1-L4 break `lake build VE.Calc.Ties`. `lean_statements.py --check` passes, and no statement is changed or gains a hypothesis.
11. **N.A.** No budget, limit or deadline changed.
12. **N.A.** No runtime code changed. The theorems are erased at run time.
13. **PASS.** No test was removed (`gate_collection.py --check --prebuilt`: 0 removed).
14. **PASS.** Both directions are covered: each tie theorem states the holds, fails and null cases, and S2 checks the opposite, an unrelated tie being refused. Each claim cites its evidence file, and the spec re-read is listed above.
