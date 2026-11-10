# ps-3: proved coupling of equal goals (PS-3)

Feature item ps-3 (sprint family presupposition, plan batch PS-3; spec `docs/spec/presupposition.md` 1.9, 4.8, 7.2).
Branch feature/ps-3. Lean only; no route changes (DELTA.md: no rows).

## Plan rows

| Row | Delivered | Where |
|---|---|---|
| (1) Couple.lean definitions, spec 4.8 text | yes: `Pick`, `pickOf`, `Group`, `groups`, `repCandidate`, `rep`, `Uniform`, `uniformB`, `couplable`, `coupledSet`, `readingFor`, `unitFormulas`, `formulasUnder`, `unitRule`, `treeUnder`, `assumptionsUnder`, `PickFits`, `pickedU`, `SatUnder`, `PickedWF`, `SameModels`, `SameDecides` | `lean/VE/Presupposition/Couple.lean` |
| (1) S15, S18, S19, S22 fixtures; >64 joint choices | yes | `lean/VE/Presupposition/CoupleExamples.lean` |
| (2) `coupled_subset`, `coupled_uniform` | proved | `Couple/Statements.lean` |
| (3) `coupling_complete` | proved, VACUOUS over today's `candidateTable` (no admitted group; `groups_admit_nil`); the semantic proof (spec 4.8 'Why it holds') is not done: row ps-3-semantic | `Couple/Statements.lean` |
| (4) generated `requires` constraints, `couplings_spec` | yes: `choiceOf`, `groupConstraints`, `couplingConstraints`; `couplings_spec` proved | `Couple.lean`, `Couple/Statements.lean` |
| (5) source-identity choice | yes: `SourceChoice`, `sourceChoices` (labelled, offered, never imposed); `sourceChoice_entails` through `source_identity_entails` | `Couple.lean`, `Couple/Statements.lean` |
| P12 (u049) | projection fixture only, unchanged (coupling deferred, spec 8) | none |

**Order inside PS-3.** No PS-0p step-7 re-count exists: no `docs/presupposition/ps-0p*` directory and no
translator field with the count on main. So the case "does not exist" held: coupling first, then source identity.

**Statement gate.** PASSED (task). Probe `evidence/probe.py` (comments stripped, whitespace-normalised; a spec entry
without a body is compared up to its `:=`), run as `python3 -I docs/presupposition/ps-3/evidence/probe.py
<manage-agents>/reviews/ps-s-stub/SpecStubs_presupposition.lean`: spec 4.8 block 21 of 21 equal (including the three
theorem statements), stub 4.8 section 22 of 22 equal, `differing []`. A planted change to `couplable` makes it print
`DIFFERS` for both. The stub is read, never committed.

**Prerequisites.** `admit` (`Admit.lean:289`), `Report.checked` (`Wire.lean:173`) and `emitted` (`Wire.lean:199`) have
the shape the spec assumes. lf-14d's API is in `lean/VE/Discourse/Joint.lean` and `Manifest.lean`: `Choice`,
`Satisfies`, `satisfiesAll`, `compatibleChoices` (limit `VE.Scope.choiceLimit` = 64), and the constraint type
`VE.Discourse.Constraint` with `ConstraintKind.requires`. They are called, never edited.

## The DRI ruling on vacuity

`coupling_complete` is true but vacuous over `admit`. `admit_unresolved_readings` gives every unresolved obligation at
least two emitted readings, and the only `candidateTable` cell with two candidates is generic/consequent
`[.assumed, .unconditional]`. `.unconditional` is not a root carrier, so `groups candidateTable R = []` for every
admitted `R` (`groups_admit_nil`). The DRI signed proving it word for word through that lemma
(reviews/dri-decisions-20261110-ps-3.md item 1). If PS-E1's table gains a cell with two root carriers,
`candidateTable_core` and `groups_admit_nil` stop building, and the semantic proof is owed then. Row ps-3-semantic
(item 2, filed by the DRI) holds the semantic statement over `admitWith t`; it is a statement change. Nothing here cites
`coupling_complete` as evidence that coupling preserves models, decisions or assumptions. The fixtures carry that
content: S15, S18 and S19 over `fixtureTable`, and S22 as a proved `SatUnder` for both picks under the completion.
`#guard (groups fixtureTable same19).length == 1` runs the group code on a table where groups exist.

## What the statements and fixtures show

- `coupled_subset` and `coupled_uniform` are short (`List.mem_filter`, `uniformB_iff`).
- `couplings_spec` (statement written here; spec 4.8 pins only its content): for a report whose obligation ids are
  distinct (`admit`'s `checkIds` gives this) and a joint set `J` of fitting picks, filtering `J` with lf-14d's
  `satisfiesAll` on the manifest extended by `couplingConstraints` gives exactly
  `coupledSet J ((groups t R).filter (couplable J))`. A reading set is named by its obligation (spec 1.9: a unit's
  only open set is its obligation's own), at the version `ver o`; reading `i` is the `i`-th emitted candidate.
  An uncouplable group adds no constraint (S18: `couplingConstraints ver0 J18 [g18] == []`).
- `sourceChoice_entails`: for each offered choice, `pre` once entails `ruleGoal r N pre` for every rule
  (`source_identity_entails`, Rules.lean:145; closedness from `check E []`). The choice is offered in its own list and
  enters no pick, group, constraint or joint set; S19's coupled sets are computed without it.
- S15: the mixed pick `[B1, U, U → B2]` and its representative `[B1, U, B2, U]` agree on the four models (false, false,
  true, false), and the assumptions agree (`[U]` and `[U, U]`). The readings are built by `expectedReadings`.
- S18: `!couplable J18 g18`; the representative is uniform but outside `J`.
- S19: identical guards give one group, 32 picks, 2 coupled; different guards give no group and 32 picks; one
  source-identity choice for the closed `pre` in both cases; none for an open `pre`, one rule act alone or a
  non-rule-act position.
- S22: `s22_completion` proves `SatUnder` for both picks on a model where `p` holds at the gap `s2`, through
  `IntendedAt3` read off `decides` (`intendedAt3_of_eval`, `value3_holds`, `decides_denote`). The raw W1 form
  (`elaborate`, placeholder `deny`) refutes both (`#guard`). Both picks pass `PickedWF`; an undeclared `unspecified`
  predicate fails it, only with the block.
- R-3: `PickFits` refuses a pick that names in place, a missing pick, a duplicate and an unknown obligation.
- lf-14d's limit: 7 binary sets (128 > 64) give `ResourceLimit: joint choices` (UNKNOWN); 6 give 64 choices.
- `SameModels` and `SameDecides`: reflexive examples, and `¬ SameModels D15 R15 mixed15 cond15` (no owner: the
  all-conditioned pick holds, the mixed pick does not).

## Seeded bugs

The four the task names, and one per new trusted definition, in `mutants.json` (28 Lean mutants, all KILLED; each
applied to `Couple.lean`, built with `lake build VE.Presupposition.Couple.Statements VE.Presupposition.CoupleExamples`,
restored). Only Lean product code changed, so Lean is the only language.

| Mutant | Definition | Fails |
|---|---|---|
| `couplable` without `J.all (… J.contains (rep g ch))` | `couplable` | `CoupleExamples.lean:76` `#guard !couplable J18 g18` (S18) |
| `rep` replaces picks outside `g.members` | `rep` | `:43` S19 guard: a pick outside the group is unchanged |
| `SatUnder` with the placeholder `deny` (W1's elaboration) | `SatUnder` | `:256` the S22 proof (`satUnder_of_eval`) |
| `PickFits` admits in place (`t c.ob.row c.pos` for `emitted t c`) | `PickFits` | `:91` `#guard !decide (PickFits … [("o1", .inPlace)])` (R-3) |

The other 24 (one or more per definition: `pickOf`, `groups` (3), `repCandidate`, `Uniform`, `uniformB`,
`coupledSet`, `readingFor`, `unitFormulas`, `formulasUnder`, `unitRule`, `treeUnder`, `assumptionsUnder`, `pickedU`,
`PickedWF`, `SameModels`, `SameDecides`, `choiceOf`, `groupConstraints`, `couplingConstraints`, `sourceChoices` (3))
are in `mutants.json` with the guard or proof each breaks.

## Trust

TRUST-NUMBERS

## Size

SIZE-NUMBERS

## Evaluators, budgets, bytes

- No evaluator, runner or mode is exposed: nothing on a route calls the coupling (PS-4 wires it). `couplable` reads
  `J` once per pick (O(|J|²) membership tests); `J` is lf-14d's enumeration within its limit of 64 joint choices
  (`compatibleChoices`), over which the enumeration is `ResourceLimit: joint choices` (UNKNOWN, `#guard`).
  `groupConstraints` is quadratic in a group's members, which `admit` bounds by `maxObligations` (256).
- Pilot bytes moved: 0 (plan "Bytes. 0"; no route change). Nothing is claimed before a pilot audit.

## Final checks

FINAL-CHECKS

## Next item

ps-4 (on the composition stack), then ps-2b; ps-3-semantic (the DRI's row: the semantic coupling statement over
`admitWith t`, after the spec's statement review).
