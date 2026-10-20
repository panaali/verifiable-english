# df-1ab: the gate and the rest of spec 7.1 (build report)

No DRI signature is reserved: the one delta (trust, DELTA T1) is signed by standing ruling R16. **Size cut**: deliveries
(1) and (2) are built; (3), `lean/VE/Defaults/Wire.lean` (spec 7.2) with the four kinds as one row of PK-1's kind
table, is named **df-1ac** (section 5). pk-1b is on main, so the kind row is not blocked; it does not fit the size.

Branch `feature/df-1ab`, base `main` bfec7f9ef. Plan `docs/spec/defeasible-PLAN.md` and spec `docs/spec/defeasible.md`
as on main (df-1a's verbatim copies of 00a45ce36, unchanged here). Statement gate: DF-S passed
(`manage-agents/defeasible-p3ver1.final.md`). The six statements the task names are spec 7.1's and 7.2's text;
`collisionTuple_some`, `cohU_rank_valid` and `collision_unranked` are built here unchanged, and
`defaults_coherence_sound`, `forcedAt_sound` and `decodeLayered_soften` are df-1ac's (spec 7.2), unchanged. No text
claims minimality (DF-2 is not proved).

## 1. Plan rows delivered

| Plan DF-1a row (spec 7.1, 7.2, 8.1) | Delivered | Where |
| --- | --- | --- |
| The gate: `DefaultCoherent`, `pairChecks`, `defaultCoherenceCheck`, `collisionCheck`, `pairChecks_sound`, `defaultCoherenceCheck_sound`, `collision_sound` | yes, restored unchanged from `wip/df-1ab-gate` (5ee7887c7) | `Premises.lean`, cef2ed102 |
| DF-γ's gate and DF-ω as `#guard`s; wip mutants M8, M9, M10, M18 | yes (as D1 to D4) | `Examples.lean`, `mutants.json` |
| `decisionFree`, `whatOf`, `questionDiag`, `questionDiag_none`, `limitDiag` | yes, proved | `Premises.lean`, a00d61c73 |
| `selU`, `cohPremiseU_selU` (`rfl`), `collisionTuple`, `collisionTuple_some` | yes, proved | `Premises.lean` |
| `cohU_rank_valid`, `collision_unranked` | yes, proved (no `sorry`), so DE7 keeps "The text ranks neither above the other" | `Premises.lean`, `SoftNorms/RankProof.lean` |
| `decidersOf`, `giveWayDeciders` | yes | `Premises.lean` |
| Fixtures: DF-γ′, DF-η and spec 8.4's diagnostics, DF-γ's tuple and deciders, rank validity on DF-δ/DF-δ′ | yes, `#guard`s | `Examples.lean` |
| DF-θ (diagnostic 1, a profile check in `viewRest`) | **df-1ac** | — |
| `Defaults/Wire.lean` (7.2), the kinds as one kind-table row (DRI DF4), shapes and encoder theorems | **df-1ac** (size cut) | — |
| Plan seeded bugs `forcedAt` `[]`, `defaultsCase` without the gate, `defaults-coherence` without a collision | **df-1ac**: all three mutate `Wire.lean` definitions | — |
| Generated files through `regen_generated.py --write` | `Audit.lean`, `axioms.txt`, `{statements,predicates,declarations}.txt` | 456226b8c |
| `lean/DEFAULTS.md`, plain words, no minimality claim | yes | 2cb602a06 |

Spec comparison: the 20 declarations above compare equal to spec 7.1's text token for token, after whitespace
normalisation and with docstrings and comments stripped (script run on HEAD: 20 OK, 0 DIFF).

Deviations (statements unchanged):
1. `cohU_rank_valid` reuses soft's argument instead of copying it. `SoftNorms/RankProof.lean`'s helper lemmas took
   soft's substitution (`circ D`); they now take any table, and the new `VE.SoftNorms.coh_rank_valid_with` says that
   two comparable colliding defaults never both select, for any tree, fuel and table (only each rule's own guard and
   carve-outs are read). `coh_rank_valid_unconditional` is its instance with the same statement; the approved
   `coh_rank_valid` and its pinning `example` are untouched. The helpers' statements (in no spec) gain the parameter.
2. df-1a review F3: DF-ι now also checks the empty-domain situation on the wire (no model), and DF-γ checks that the
   empty-domain situation is an accepted consistency witness of `defaultX` where the conclusion holds (spec 8.1).
3. df-1a review F1: `mutants.json`'s `test` cells name fixtures that exist (section headings and DF names);
   the `guards` key carries the exact guard lines the runner checks.
4. `docs/defeasible/df-1a/evidence/run_mutants.py` takes a mutants file as its argument and runs theorem mutants
   (`theorems` key) with the theorems kept, instead of a second copy of the runner. Run on HEAD with no argument it
   still fails all 14 of df-1a's mutants (exit 0); their outputs list the new guards too.
5. `limitDiag`'s positive fixture is DF-β with its condition nested 400 negations deep (`deepen`), built in Lean: a
   decoded document stays within soft's limits.

## 2. Evidence

- `lake build` (default targets, 1,039 jobs): every `#guard` of `Examples.lean` passes.
- `python3 lean/audit.py`: PASS, 587 source files, 6,688 theorems, standard axioms only.
- `uv run python tools/regen_generated.py --check`: 32 entries checked, exit 0 (no schema or checker pin changes).
- `uv run python tools/trust_map.py --check`: PASS with the recorded allowance (section 4).
- `uv run python tools/gate_collection.py --check --prebuilt`: 18,313 collected; 0 added, 0 removed, 0 refused,
  0 stale, 0 malformed.
- Pre-existing failures (`main-known-red.txt`): none was selected or failed.

## 3. Seeded bugs (Lean; no Python or Rust product file changed)

`docs/defeasible/df-1ab/mutants.json`, run by `python3 docs/defeasible/df-1a/evidence/run_mutants.py
docs/defeasible/df-1ab/mutants.json`; saved run `evidence/mutants.out`: control 0 failures, all 17 fail. Every new
definition of `Premises.lean` has at least one.

| # | Definition, bug | Fails |
| --- | --- | --- |
| D1 | `pairChecks` accepts a missing certificate | DF-ω, DF-γ gate guards |
| D2 | `defaultCoherenceCheck` without the length check | DF-ω, DF-γ gate guards |
| D3 | `collisionCheck` does not evaluate the coherence premise | DF-ω |
| D4 | `DefaultCoherent` read as `True` | theorem `collision_sound` (and `defaultCoherenceCheck_sound`) |
| D5 | `collisionCheck` looks the pair up reversed | DF-γ gate, DF-γ′ |
| D6 | `decisionFree` always true | DF-η/8.4 DF-α, DF-ε, DF-δ diagnostics |
| D7, D8 | `whatOf`: an exception worded as a switch; outcomes not named | DF-η; DF-α and DF-β diagnostics |
| D9 | `questionDiag` names the last offending premise | DF-β facts-only guard |
| D10 | `limitDiag` never reports | diagnostic-4 `deepen` guard |
| D11 | `selU` drops the derived carve-outs (a rule selects where its exception applies) | DF-γ tuple, DF-δ/δ′ rank |
| D12 | `collisionTuple` shows a tuple where one rule selects | DF-γ tuple, DF-δ/δ′ rank |
| D13, D14, D15 | `decidersOf` without the outranking decider; repeated; without switch parties | DF-δo; DF-δ, DF-γ; DF-ε |
| D16, D17 | `giveWayDeciders` always both; second dropped | DF-γ tuple; DF-γ′ |

The plan's seeded bugs `dfltOf`, `basisOf` (twice) and `followsForm` are df-1a's (M1, M14, M15, M17 there); the other
three mutate `Wire.lean` definitions and move with it to df-1ac.

## 4. Size and trust

- **Trust** (R16, DELTA T1): S +6, V +23, K +0, all in `Premises.lean`; FOLLOW-UPS "## df-1ab".
- **Size**: `git diff --numstat $(git merge-base HEAD main)`, hand-written lines added, generated files and the saved
  `mutants.out` excluded: `Premises.lean` 218 (89 of them the wip gate, written by df-1a's builder), `Examples.lean`
  103, `RankProof.lean` 67 (58 of them replace lines), `DEFAULTS.md` 30, `trust-classes.json` 32, runner 22,
  `mutants.json` 25, DELTA 17, this report about 140: about 650, near the ~600 guideline. `Wire.lean` with the kind
  row, shapes, encoders and its fixtures would add several hundred lines, so it is cut whole.

## 5. Next items

- **df-1ac**: `Defaults/Wire.lean` (spec 7.2: `DefaultsView`, `viewOf` with `decodeLayered_soften` and diagnostics 1
  and 7, `CertReplay`, `CoherenceReplay` with `defaults_coherence_sound` and the pair statuses, `elaborateRows`,
  `forcedAt` with `forcedAt_sound`, `ModelReplay`, `defaultsCase`, `defaultsCase_other`); the four kinds as one row of
  PK-1's layered kind table (DRI DF4); shapes and encoder theorems; DF-θ and the wire answers of DF-α to DF-ω; the
  plan's three remaining seeded bugs. pk-1c waits on that kind row (FOLLOW-UPS "## pk-1b").
- Then **df-1b** (the relay and the first pilot number; df-03's baseline P-1 0 of 3, P-2 SOME is recorded), with DF-2.

## 6. Pilot bytes

None expected: no CLI path or service mode reaches these definitions (`defaultsCase_other` is df-1ac's).

## 7. Tests

- Selected tests on the Mac runner (`mac-pytest.sh --select -- --base bfec7f9ef --run`, HEAD 2cb602a0, clean): 397 of
  455 units, including `lake build`, `lean/audit.py` and `tools/test_layer_policy.py`: **0 failed** (1,797 s).
- The mutant runs (section 3) elaborate `Premises.lean` and `Examples.lean` 18 times.
- Not run by me: the full gate (the chain runs it on the final HEAD).

Evidence commit list (`git log --oneline main..HEAD --no-merges`, before this report's commit): cef2ed102, a00d61c73,
456226b8c, d4186ce1b, 6563e7770, 2cb602a06, d6a0328e9.

## Self-review against BUILDER-CHECKLIST

1. **Every Lean answer typed and contained.** N.A.: no response shape, schema, relay or service mode changes; the kinds
   are df-1ac's (`regen_generated.py --check`: no schema or pin rewritten).
2. **Every required deliverable built.** PASS: section 1 lists each plan row with its commit, or df-1ac under the
   task's size rule. Diff grep: no Python product file, no Python copy of a Lean decision, no permanent report test.
   Overlap with branches in flight: only `tools/trust-classes.json` (ap-1a, jt-2, me-9, sc-1ab, me-1), the
   trust ledger's side table, which each item extends in its own module entries.
3. **Tests and gates can fail.** PASS: D1 to D17, at least one per new definition, each failing a named guard (D4 a
   named theorem); control passes (`evidence/mutants.out`).
4. **Python, Lean and Rust agree; valid inputs pass.** N.A.: nothing reaches the new definitions from Python or Rust;
   the fixtures decode real JSON documents through `decodeSoftU`, including a new party (`operator`) and a holistic
   outranking decider.
5. **R8 binding.** N.A.: no relayed field.
6. **Gate evidence matches the final HEAD.** PASS: based on main bfec7f9ef (the merge base); the chain gates the final
   HEAD; the commit list is from `main..HEAD --no-merges`.
7. **No unsigned item.** PASS: DELTA T1 cites R16 with its evidence.
8. **Every user-visible change in DELTA.** PASS: none besides trust (no schema, pin or mode changes:
   `regen_generated.py --check`).
9. **Test selection.** PASS: the selected plan includes `lake build`, which elaborates every guard, so a seeded bug in
   `Premises.lean` fails it (D1 to D17 fail at a guard).
10. **Lean statements say what is claimed.** PASS: the 20 declarations equal spec 7.1's text; D4 breaks
    `collision_sound`; `cohU_rank_valid` is about `cohPremiseU`, the premise the gate checks, and DF-δ/δ′'s guard
    evaluates that premise on every one-element situation.
11. **Budgets and limits fail closed.** PASS: `limitDiag` reports the first premise beyond soft's limits (D10, the
    `deepen` guard); no budget or deadline is added.
12. **No CPU or memory regression.** N.A.: nothing on a route runs the new code; no pilot run (L70).
13. **Test-removed trailers.** PASS: `tools/gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused,
    0 stale, 0 malformed.
