# df-1a: the no-exception premises, the basis and the form (build report)

No DRI signature is reserved: the one delta (trust, DELTA T1) is signed by standing ruling R16. **Size cut**: this item
is DF-1a's first part; the gate and everything on the wire move to **df-1ab** (section 5).

Branch `feature/df-1a`, base `main` 702ff7429. Plan `docs/spec/defeasible-PLAN.md` and spec `docs/spec/defeasible.md`,
copied verbatim from `research/defeasible-p1` 00a45ce36 (byte-identical to the copies on `feature/df-03`). Statement
gate: DF-S passed (spec draft 2 applied the DRI ruling R1–R16; the diff-only re-check `manage-agents/defeasible-p3ver1.final.md`
returned PASS). DRI-DECISIONS-PHASE2 DF4 and DF7 concern the kind row and the collision witness, both df-1ab's; JT-R2
(the empty pack list) does not touch this part.

## 1. Plan rows delivered

| Plan DF-1a row | Delivered | Where |
| --- | --- | --- |
| `Defaults/Premises.lean` (spec 7.1): `dfltOf`, `dfltLabelled`, `dfltPremises`, `dfltLabels`, `defaultX`, `withoutDefaults`, `certChecks`, `assumptionsOf`, `Basis`, `basisOf`, `Form`, `bareExceptionLabels`, `followsForm` | yes, bodies as spec 7.1 | `lean/VE/Defaults/Premises.lean` |
| Theorems `dflt_wellFormed`, `entailsX_mono`, `strict_of_withoutDefaults`, `premisesX_split`, `assumptions_sound`, `basis_strict_sound`, `basis_needs_sound` (with its non-vacuity part `CounterX`), `followsForm_short` | proved, no `sorry`; `lean/audit.py` PASS | `Premises.lean` |
| The gate: `DefaultCoherent`, `pairChecks`, `defaultCoherenceCheck`, `collisionCheck`, `pairChecks_sound`, `defaultCoherenceCheck_sound`, `collision_sound` | **df-1ab** (size cut): written, proved and guarded, kept on local branch `wip/df-1ab-gate` (5ee7887c7) | — |
| `decisionFree`, `whatOf`, `questionDiag`, `questionDiag_none`, `limitDiag`, `selU`, `cohPremiseU_selU`, `collisionTuple`, `collisionTuple_some`, `cohU_rank_valid`, `collision_unranked`, `decidersOf`, `giveWayDeciders` | df-1ab | — |
| `Defaults/Wire.lean` (spec 7.2), the four kinds as one row of PK-1's kind table calling `defaultsCase`, shapes and encoder theorems | df-1ab; PK-1's kind table is pk-1b's and not on `main` | — |
| `Defaults/Examples.lean`: DF-α, DF-α′, DF-β, DF-γ (its `defaultX` part), DF-δ, DF-δ′, DF-ε, DF-ζ, DF-ζ0, DF-ι, DF-κ, DF-σ as `#guard`s | yes (DF-γ's gate, DF-ω, DF-η and DF-θ are df-1ab's) | `lean/VE/Defaults/Examples.lean` |
| Import lists; generated files through `tools/regen_generated.py --write` | `lean/VE.lean` +2; `Audit.lean`, `axioms.txt`, `{statements,predicates,declarations}.txt` regenerated | — |
| `lean/DEFAULTS.md` in plain words, no minimality claim | yes | `lean/DEFAULTS.md` |
| Trust recorded (R16) | S +18, V +26 (DELTA T1); FOLLOW-UPS "## df-1a" | `docs/trust-baseline.json`, `tools/trust-classes.json` |

The statements built are the reviewed ones: all 21 declarations above compare equal to spec 7.1, token for token after
whitespace normalisation. None of the statements the task names was changed. Those that are df-1ab's
(`defaults_coherence_sound`, `forcedAt_sound`, `collisionTuple_some`, `cohU_rank_valid`, `collision_unranked`,
`decodeLayered_soften`) and DF-2's (`replace_admissible`) are not stated here. No text claims minimality.

Deviations (statements unchanged):
1. `bindAll_wellFormed_inv` moved unchanged from `Norms/FlaggedSpec.lean` (layer 4) to `Norms/Elaborate.lean`, beside
   `bindAll_wellFormed`, so `dflt_wellFormed` uses it at layer 2 without a copy. The audit manifests were rebuilt with
   `lean_statements.py` and `audit.py --write` (the stale `#print axioms` line of the moved name was dropped from the
   working copy first, so that the build could run; the committed file is the generator's).
2. Added helper `atom_wf` (a declared atom is typed by its sorts, arity 1, 2 or `⊥`).
3. `assumptionsOf` is exercised on two certificates written in `Examples.lean` for DF-α (`∀a. ¬excepted` from `Dflt_T`,
   which keeps the label; `∀a. e → e`, which keeps none). The other fixtures' assumption lists use `assume1`, the
   complete one-element check in place of the certificate check (spec 8.0); their certificates are *derived* (df-1b).
4. `ve/assurance-manifest.json` lists `lean/VE/Defaults/Examples.lean` under `other_json` (fixtures parse JSON
   literals with the pinned decoders).

## 2. Evidence

- `lake build` (default targets): every `#guard` of `Examples.lean` passes.
- `python3 lean/audit.py`: PASS, 572 files, 6,498 theorems, standard axioms only.
- `uv run python tools/regen_generated.py --check`: 31 entries checked.
- `uv run python tools/trust_map.py --check`: PASS with the recorded allowance.
- Selected tests: see section 6.
- Pre-existing failures (`main-known-red.txt`): the two sub-tick deadline tests and the rd8 report test, not touched.

## 3. Seeded bugs (Lean; no Python or Rust product file changed)

`docs/defeasible/df-1a/mutants.json` lists each with its file, definition and failing guards;
`evidence/run_mutants.py` runs them with every theorem removed, the unmutated control passing every guard;
`evidence/mutants.out` is the saved run (control 0 failures; all 14 fail named guards). The plan's seeded bugs for the
definitions built here are M1, M11, M12 and M14.

| # | Definition, bug | Fails (`Examples.lean`) |
| --- | --- | --- |
| M1 | `dfltOf` drops the sufficient-condition disjunct (plan) | DF-β's premise values, `Exc_T`/`Dflt_T`, (i) |
| M2 | `dfltOf` drops switches | DF-ε |
| M3 | `dfltLabelled` drops rankings | DF-δ |
| M4 | `dfltPremises` drops the first premise | DF-α and 8 more |
| M5 | `dfltLabels` reversed | DF-γ, DF-δ, DF-δ′, DF-ε |
| M6 | `defaultX` without `Dflt_T` | DF-α, DF-κ and 5 more |
| M7 | `withoutDefaults` without the `⊤`s | DF-α |
| M8 | `certChecks` accepts everything | DF-α's two certificate guards |
| M9, M10 | `assumptionsOf` keeps none / all | DF-α's `cNeeds` / `cStrict` guards |
| M11 | `basisOf` always `strict` (plan) | DF-α's basis and 5 more |
| M12 | `basisOf` gives `needs` without a checked strict countermodel (plan) | DF-α′ |
| M13 | `bareExceptionLabels` counts a stated condition as bare | DF-β, DF-β (ii)'s form |
| M14 | `followsForm` ignores switch labels (plan) | DF-ε's form |

The plan's other seeded bugs (`forcedAt`, `defaultsCase` without the gate, `defaults-coherence` without a checked
collision) belong to definitions df-1ab builds.

## 4. Size and trust

- **Trust** (R16, DELTA T1): S +18, V +26, K +0, all in `Premises.lean`.
- **Size**: hand-written lines, `git diff --numstat $(git merge-base HEAD main)`, excluding the verbatim plan and spec
  and the generated files: `Premises.lean` 256, `Examples.lean` 227, the lemma move 14, `VE.lean` 2, `DEFAULTS.md` 59,
  `trust-classes.json` 83, `trust-baseline.json` 14, `assurance-manifest.json` 1, mutants and runner 99, this report
  and DELTA about 155: about 910 (`mutants.out` is the runner's output). This is over the ~600 guideline. Before the
  cut it was about 1,000; I cut the gate (about 110 lines with its guards and mutants). What remains is the smallest part that
  passes its own fixtures and seeded bugs: the definitions are spec 7.1's and the proofs are the stub's, and
  without the fixture harness (about 110 lines of `Examples.lean`) no guard can decode a document.

## 5. Next items

- **df-1ab**: the gate (restore from `wip/df-1ab-gate`: its code, the three soundness theorems, the DF-γ and DF-ω
  guards and mutants M8 to M10 and M18 there); then `decisionFree`, `questionDiag(_none)`, `limitDiag`, `selU`,
  `collisionTuple(_some)`, `cohU_rank_valid`, `collision_unranked`, `decidersOf`, `giveWayDeciders`; `Wire.lean`
  (spec 7.2) with the four kinds as one kind-table row after pk-1b (DRI DF4), shapes and encoders; the plan's seeded
  bugs `forcedAt`, `defaultsCase` without the gate and `defaults-coherence` without a collision.
- Then **df-1b** (the relay and the first pilot number, after df-03's baseline is recorded).

## 6. Pilot bytes

None expected: no CLI path reaches these definitions (plan 5: DF-1a has no pilot effect; P-1 moves with df-1b).

## 7. Tests

- Selected tests on the Mac runner (`mac-pytest.sh --select -- --base 702ff7429 --run`, HEAD fbe0d484, clean): the
  Lean binary cutoff applied (`ve_service` and every other executable built the same), so the plan is `lake build`
  (every guard), `lean/audit.py`, the layer policy and 72 test units: **0 failed** (1,246 s). An earlier VM run
  (no cutoff record, 353 units) stopped at its one failure, `test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`;
  fixed in fbe0d484 (`other_json` entry), and that file passes in the Mac run above.
- `uv run python tools/gate_collection.py --check --prebuilt`: 18,161 collected, 0 added, 0 removed, 0 refused,
  0 stale, 0 malformed.
- `review-ready.py`: clean, commits, mutants (Lean), relay and delta PASS; the gate is the chain's.
- Not run by me: the full gate (the chain runs it on the final HEAD).

Evidence commit list (`git log --oneline main..HEAD --no-merges`, before this report's last commit): 116cd243e,
94c34e5a3, 5ee7887c7, 075edbdfd, fbe0d4846.

## Self-review against BUILDER-CHECKLIST

1. **Every Lean answer typed and contained.** N.A.: no response shape, schema, relay or service mode changes; the
   kinds are df-1ab's (`ve_service` pin unchanged).
2. **Every required deliverable built.** PASS, with the size cut named: section 1's table lists each plan row with
   where it is or that it moves to df-1ab (the plan's own split instruction in the task). Rule grep of the diff: no
   Python, no Python copy of a Lean decision, no permanent report test; overlap check of the hand-written files
   against every `feature/*`, `infra/*`, `lean-first/*`, `foundation/*` branch: only `docs/spec/defeasible*.md`,
   byte-identical on `feature/df-03`.
3. **Tests and gates can fail.** PASS: 14 Lean mutants, one or more per new definition, each failing a named guard with
   the theorems removed (`evidence/run_mutants.py`, `evidence/mutants.out`, control passes).
4. **Python, Lean and Rust agree; valid inputs pass.** N.A.: no route answer changes and nothing reaches the new
   definitions from Python or Rust; the fixtures decode real JSON documents through `decodeSoftU`.
5. **R8 binding.** N.A.: no relayed field.
6. **Gate evidence matches the final HEAD.** PASS: synced at main 702ff7429 (the merge base); the chain gates the
   committed final HEAD; the evidence commit list is from `main..HEAD --no-merges`.
7. **No unsigned item.** PASS: DELTA T1 cites R16 with its evidence; `review-ready.py --delta-dri-needed` exit 0.
8. **Every user-visible change in DELTA.** PASS: none besides trust; `ve_service` and every executable built the same
   (the Mac run's binary cutoff), and no schema or pin changed (`tools/regen_generated.py --check`).
9. **Test selection.** PASS: the selection plan includes `lake build`, which elaborates `Examples.lean`'s guards, so a
   seeded bug in `Premises.lean` fails the selected plan (M1 to M14 fail at a guard); the 72-unit selection follows
   from the binary cutoff.
10. **Lean statements say what is claimed.** PASS: the 21 built declarations equal spec 7.1's text; the theorems are
    about the returned values (`assumptionsOf`, `basisOf`, `followsForm`), and the mutants M8 to M14 change those
    values and fail guards.
11. **Budgets and limits fail closed.** N.A.: no budget, limit or deadline is added; `basisOf` never gives `needs`
    without a checked strict countermodel (M12, DF-α′).
12. **No CPU or memory regression.** N.A.: nothing on a route runs the new code; no pilot run (L70).
13. **Test-removed trailers.** PASS: `tools/gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused,
    0 stale, 0 malformed.
