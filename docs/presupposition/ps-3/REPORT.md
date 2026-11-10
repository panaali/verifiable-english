# ps-3: proved coupling of equal goals (PS-3)

Feature item ps-3 (sprint family presupposition, plan batch PS-3; spec `docs/spec/presupposition.md` 1.9, 4.8, 7.2).
Branch feature/ps-3. Lean only; no route changes (DELTA.md: no rows).

## Plan rows

| Row | Delivered | Where |
|---|---|---|
| (1) Couple.lean definitions, spec 4.8 text | yes: `Pick`, `pickOf`, `Group`, `groups`, `repCandidate`, `rep`, `Uniform`, `uniformB`, `couplable`, `coupledSet`, `readingFor`, `unitFormulas`, `formulasUnder`, `unitRule`, `treeUnder`, `assumptionsUnder`, `PickFits`, `pickedU`, `SatUnder`, `PickedWF`, `SameModels`, `SameDecides` | `lean/VE/Presupposition/Couple.lean` |
| (1) S15, S18, S19, S22 fixtures; >64 joint choices | yes | `#guard`s in `lean/VE/Presupposition/CoupleExamples.lean`; fixture data and the proofs about it (S15's `SameModels`, S22's completion) in `lean/VE/Presupposition/Couple/Fixtures.lean` |
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

Only Lean product code changed, so Lean is the only language. **Hand mutants:** 35 in `mutants.json` (the four the task
names, and at least one per new trusted definition), all KILLED. Each is a find/replace in its file, built with `lake build
VE.Presupposition.Couple.Statements VE.Presupposition.Couple.Fixtures VE.Presupposition.CoupleExamples`, then
restored. They were replayed on 57bd8d153's layout; the failing lines are in `evidence/mutants-run.txt`.

| Mutant | Definition | Fails |
|---|---|---|
| `couplable` without `J.all (… J.contains (rep g ch))` | `couplable` | `CoupleExamples.lean:49` `#guard !couplable J18 g18` |
| `rep` replaces picks outside `g.members` | `rep` | `CoupleExamples.lean:21` `#guard (groups fixtureTable same19).all (fun g =>` |
| `SatUnder` with the placeholder `deny` (W1's elaboration) | `SatUnder` | `Couple/Fixtures.lean:216` `exact ⟨fun a ha => (VE.eval_iff_denote M [] a).mp (List.all_eq_true.mp` |
| `PickFits` admits in place (`t c.ob.row c.pos` for `emitted t c`) | `PickFits` | `CoupleExamples.lean:81` `#guard !decide (PickFits fixtureTable repNeg [("o1", .inPlace)])` |

The other 31: `M-pickOf-ne`, `M-groups-min`, `M-groups-core`, `M-groups-goal`, `M-repCandidate-order`, `M-Uniform-self`, `M-uniformB-self`, `M-coupledSet-any`, `M-readingFor-head`, `M-unitFormulas-premise`, `M-formulasUnder-take`, `M-unitRule-none`, `M-treeUnder-fixed`, `M-assumptions-none`, `M-pickedU-unspec`, `M-PickedWF-sign`, `M-SameModels-imp`, `M-SameDecides-imp`, `M-choiceOf-index`, `M-groupConstraints-excludes`, `M-couplingConstraints-all`, `M-sourceChoices-open`, `M-sourceChoices-one`, `M-SourceChoice-label`, `M-formulasUnder-background`, `M-treeUnder-open-only`, `M-pickedU-lits`, `M-unitFormulas-asserted`, `M-readingFor-resolved`, `M-SameDecides-same`, `M-SameModels-noWF`.

**R16 sweep** (`trust-mutants.json`, `trust-mutants-allow.json`; `mac-pytest.sh --trustmut -- --max-mutants 1000 --test
lean/VE/Presupposition/CoupleExamples.lean --allow docs/presupposition/ps-3/trust-mutants-allow.json --rescore <run 3>`,
on the VM): 18 definitions, 314 mutants: **236 KILLED, 0 SURVIVOR, 0 UNKNOWN, 9 INVALID, 69 ALLOWED, exit 0**, at
872a11aa1. History, all at 4 jobs or more on the VM:
- **Run 1** passed `Couple/Statements.lean` as a second `--test` and got 204 UNKNOWN: the tool never cuts a proof in a
  `--test` file (`tools/trust_mutants.py:1384`).
- **Run 2** used `CoupleExamples.lean` alone. Its proof `example`s still made every mutant that broke one UNKNOWN, so the
  fixture data and the proofs moved to `Couple/Fixtures.lean`, which `CoupleExamples.lean` (now `#guard`s only) imports.
- **Survivors** were list positions the guards did not move. Each now has a guard: `couplable`'s `J` and `cands` (the
  deciding pick or candidate first, middle or last), `repCandidate`'s later member, two and three groups in `groups`,
  `coupledSet` over two groups, two background formulas, two fixed rules over two regulated predicates (`¬ SatUnder` by
  each premise), `Uniform` (made decidable, as `PickFits` and `PickedWF` are), `uniformB` on no members, and `PickFits` with
  an unknown id beside a known one.
- **The 69 ALLOWED,** each with its reason in the allow file:
  - `PickFits`, `PickedWF` and `Uniform` mutants refuted by a `#guard` that reads the definition through its `Decidable`
    instance, which the tool does not credit;
  - `SatUnder`, `SameModels` and `SameDecides`, Props no check evaluates, each exercised by the proofs it breaks (named);
  - the equivalent `uniformB` cuts (one of its two member lists cut while the other stays whole);
  - `list-empty` mutants that do not elaborate.

## Trust

`uv run python tools/trust_map.py --check` on the final tree: "PASS: K, S and untied [V] within c94ad399b7b1 and the
allowances introduced since"; against c94ad399b7b1: K +0, S +105, D +0, G +29, tied +26, unclassified +0, **trusted +105**
(`VE/Presupposition/Couple.lean: trusted +105`). Allowance recorded with `trust_map.py --allow`, "SIGNED by standing ruling
R16 (DRI-RULINGS.md), ps-3, 2026-11-10" (`docs/trust-baseline.json`). R16's conditions:
- at most 150 untied lines: +105;
- no K growth: K +0;
- every new trusted definition exercised by a check that can fail: the sweep above and `mutants.json`.

The tied G[V] are `SourceChoice`, `choiceOf`, `groupConstraints`, `couplingConstraints` and `sourceChoices`. The ties
pass is a FOLLOW-UPS row under "## ps-3". Fixtures are T (`Couple/Fixtures.lean`), and the three `Decidable` instances are C.

## Size

`git diff --numstat c94ad399b` (the merge base). Exempt: statement proof lines and the S-fixtures (size rule,
reviews/dri-decisions-20261108-adv1207.md item 3), and generated files.

| File | Added | Counted |
|---|---|---|
| `Couple.lean` (definitions, constraint generation, source identity, 3 instances) | 171 | 171 |
| `Couple/Statements.lean` | 303 | 132 (68 statement lines, 64 header/comments/blank; 172 proof lines exempt) |
| `Couple/Fixtures.lean` | 246 | about 56 (header, R-3, budget, the survivor fixtures; S15/S18/S19/S22 data and 88 proof lines exempt) |
| `CoupleExamples.lean` | 138 | about 50 (header, R-3, budget, the survivor guards; S-guards exempt) |
| docs and evidence (REPORT, DELTA, `probe.py`, `mutants.json`, `mutants-run.txt`, allow file) | about 300 | about 300 |
| `tools/trust-classes.json` (new entries; the file's key moves are the generator's) | 143 net | 143 |

Product, statements and non-S guards: about 410. With docs, evidence and trust classes the total is about 850, over the
~600 rule. The overshoot is mostly R16 sweep evidence and survivor fixtures added after deliverable (5). Cutting (5)
would save about 20 counted lines, not enough to fit. The DRI decider was asked (msg.sh dri ps-3, 2026-11-10T15:32Z);
no cut was made on my own.

## Evaluators, budgets, bytes

- No evaluator, runner or mode is exposed: nothing on a route calls the coupling (PS-4 wires it). `couplable` reads
  `J` once per pick (O(|J|²) membership tests); `J` is lf-14d's enumeration within its limit of 64 joint choices
  (`compatibleChoices`), over which the enumeration is `ResourceLimit: joint choices` (UNKNOWN, `#guard`).
  `groupConstraints` is quadratic in a group's members, which `admit` bounds by `maxObligations` (256).
- Pilot bytes moved: 0 (plan "Bytes. 0"; no route change). Nothing is claimed before a pilot audit.

## Final checks

All on the final Lean, after `uv run python tools/regen_generated.py --write` (exit 0; its lake-build step "Build completed
successfully (1361 jobs)"):
- **Audit.** `python3 lean/audit.py`: "PASS: 828 source files; 9314 named theorem declarations audited …; only the declared
  standard axiom allowlist". `lean/axioms.txt` lists `coupled_subset` [propext], `coupled_uniform` [propext, Quot.sound],
  and `coupling_complete`, `couplings_spec`, `couplings_spec_admit` and `sourceChoice_entails` [propext, Classical.choice,
  Quot.sound].
- **Layers.** `python3 tools/check_lean_imports.py`: "Lean layer graph kept (828 modules, 18 reviewed legacy edges)".
- **Gate collection.** `uv run python tools/gate_collection.py --check --prebuilt`: "0 added, 0 removed by a trailer, 0
  refused, 0 stale and 0 malformed trailers".
- **Statement probe.** `python3 -I docs/presupposition/ps-3/evidence/probe.py <stub>`: 43 `equal` (spec 21, stub 22),
  `differing []`.
- **Selected tests:** SELECTED-TESTS

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: grades not recorded. The session that ran the self-reviewer agent (one call, on 51ce0636f) was restarted
before it wrote the A/B/C counts. Its fixes are commit b094fe134:
- `couplings_spec` is over K's constraints plus the coupling ones, with its `admit` corollary;
- `sourceChoice_members`;
- lf-14d enumeration guards;
- fixtures for background, fixed rules, claim units and resolved obligations;
- `¬ SameDecides`;
- `groups` on an in-place cell.

1. N.A.: no relayed answer; nothing on a route calls the coupling (DELTA.md).
2. PASS: the plan rows table above, one row per deliverable with its file; no Python copy, no report test (`git diff --stat c94ad399b` has no `ve/` or `tests/` file).
3. PASS: 35 hand mutants KILLED (`mutants.json`, `evidence/mutants-run.txt`); the trust_mutants sweep exits 0 (`trust-mutants.json`); the allow file names definition and operator, no wildcard.
4. N.A.: Lean only; no Python or Rust path changed.
5. N.A.: no relayed field.
6. PASS: synced with main (merge base c94ad399b = main); `trust_map --check`, audit and regen run on the final Lean; the gate runs on the committed HEAD.
7. PASS: DELTA has no rows; the trust growth is SIGNED by standing ruling R16 (`trust_map --check` PASS).
8. PASS: no route answer changed; no file under `ve/`, `rust/` or `lean/VE/Service/` changed (`git diff --stat`).
9. PASS: the selected tests (below) include the Lean build of the new modules (`tools/select_tests.py --base c94ad399b`).
10. PASS: statement probe `differing []`; `#guard`s and proofs fail under the planted mutants (`mutants.json`); no hypothesis added.
11. PASS: over 64 joint choices is `ResourceLimit: joint choices` (UNKNOWN): `#guard`s in `CoupleExamples.lean` "lf-14d's budget" (7 binary sets; 6 give 64).
12. N.A.: no evaluator on a route; `couplable` is O(|J|²) over lf-14d's J of at most 64 (stated above).
13. PASS: `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed; no test removed.
14. PASS, both directions: `couplable` true and false, `PickFits` accepts and refuses, `SatUnder` holds (S22) and fails (D2n, the raw W1 form), `groups` forms and refuses.
    - Spec re-read: `groups`, `rep`, `Uniform`, `couplable`, `coupledSet`, `PickFits`, `SatUnder`, `SameModels`, `SameDecides`, `coupling_complete`, `coupled_uniform` and `coupled_subset` against docs/spec/presupposition.md:1234-1290; `couplings_spec` against :1293; source identity against :227 and :802.
15. PASS:
    - no overclaim: `coupling_complete` is written as vacuous over today's table;
    - no silent cut: all five deliverables are built, and the size question went to the DRI;
    - every new check can fail: the sweep and the hand mutants;
    - limits are charged before work: lf-14d's `compatibleChoices` limit (`#guard`).

## Next item

ps-4 (on the composition stack), then ps-2b; ps-3-semantic (the DRI's row: the semantic coupling statement over
`admitWith t`, after the spec's statement review).
