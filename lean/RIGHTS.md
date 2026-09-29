# Rights in Lean (`lean/VE/Rights/*`, item 4)

Specification: [docs/spec/rights.md](../docs/spec/rights.md) section 9 (the theorem statements)
and [docs/spec/rights-PLAN.md](../docs/spec/rights-PLAN.md) section 4. This file lists every
definition the statement review reads and every theorem in plain words. All statements quantify
universally over their displayed parameters. `lean/audit.py` audits every theorem: no `sorry`,
only `propext`, `Classical.choice` and `Quot.sound`. No `lean/VE/Norms/*`, `lean/VE/SoftNorms/*`,
`lean/VE/Route/*` or P0 source changed (`python3 VE/Route/frozen.py` passes; the soft sources are
byte-identical to `soft/build` 9c54be2, imported into this branch as a prerequisite);
`VE.lean` and `VE/Audit.lean` gained imports and audit entries only, and `lakefile.toml` gained the
`ve_rights_route` target (root `RightsMain.lean`, also in `defaultTargets`). The audit allowlist
is unchanged.

## Files

| File | Contents |
|---|---|
| `Tree.lean` | `Kind`, `IKind`, `Reading`, `Condition`, `Limitation`, `Bar`, `SourceLine`, `Line`, `Right`, `AltersEntry`, `RightsEnv`, `RightsDoc`; generated names (`fanName`, `barRuleName`, `limName`, `condName`, `aimedName`); line instances in instance order (`linesOf`); `holderSlot`, `dutyKind`, `libertyKind`, `rightDerived`, `rightPermission`, `ruleReading`, `inScope`; the canonical orders and indices (`limKeys`, `condKeys`, `barPreds`, `limIndex`, `condIndex`, `barIndex`); `E″` (`genDecls`, `envR`) |
| `Correlate.lean` | `holderConj`, `ownGuard`, `limF`, `limPack`, `limPackList`, `nodeOf`, `barNode`, `barNodes`, `correlate`, `flattenTop`, `outcomeSubst`, `selectsR`; `Lim_D` (`limPremise`, `limPremisesLabelled`, `limPremises`); `backgroundBaseR`, `backgroundR`, `BaseAdmissibleR`, `RightsConflictFree`; `barReach`, `Narrowing`, `narrowings`, `condF`; the diagnostics (`checkBlock`, `checkShape`, `checkSourceLine`, `checkRights`), `rightsSemanticCheck`, `validateRights`, `WellFormedRights`, `RightsValid`; shape theorems |
| `Semantics.lean` | The direct semantics (`LiveR`, `BarredR`, the rule-level recursion `…X` and the line-level `…R`, `DecidesR`, `ValueRight`); denotation lemmas; `correlate_faithful` |
| `Projections.lean` | `SelectsRN`, `owes`, `free`, `rightsOf`, `dutiesOf`, `regOf`; `projections_agree`, `owes_outcome`, `same_effect_delivered` |
| `Bar.lean` | `bar_blocks`, `bar_value` |
| `Scope.lean` | `NarrowsAt`, `cited`, `rightCollision`, `sameEffectStrict`, `certTarget`, `certified`, `licensed`, `Finding`, `limitationScope`; `narrowings_complete`, `licensed_certified_sound`, `limitation_scope_sound` |
| `Distinction.lean` | `independentReported`, `distinctionHits`, `noDistinction`; `rightDerived_regulated`, `no_distinction_sound`, `noDistinction_sound` |
| `Route.lean` | `coherent_expands` (reused), `rights_coherent_expands_all`, `rightsConflictFreeCheck`, `rights_conflict_free`, `backgroundValidR`, `rights_conflict_witness_sound`, `PrefixAdmissibleR` and the layer chain, `rightsRoute`, `rights_route_backgroundSound/Complete`, `rights_route_intended`, `rights_route_acceptance`, `rights_route_countermodel` |
| `Wire.lean` | The rights environment and unit decoders, `RightsSource`, identity (`rightsDocumentHash`, `primeJsonR`, `basePrimeJsonR`), conflict/scope packages, witness and entailment replays, the wire theorems |
| `Run.lean`, `../RightsMain.lean` | The `ve_rights_route` executable |
| `Examples.lean` | Build-time `#guard` regressions on documents in the shapes of fixtures α, β, γ, ε, η, κ, μ, ο, π, ρ, σ, υ, φ, ψ (μ and ψ on the binary act `publish_about(person, person)`) |

## How the proofs are organised

* `correlate D` is a soft document, so soft's per-structure lemmas (`soften_faithful`,
  `selects_strict`, `decides_split`, `hard_over_soft`, `cone_independent`, `circ_canon`,
  `coherent_expands`, the soft route pieces) apply to it unchanged.
* The only structural novelty of `T″` over the lines is the bar node. A bar node is strict, has
  no carve-out, no switch and no children (`RightsValid.barOver`), so it applies, yields and
  selects exactly where `aimed_m` holds (`strictYields_bar`, `yields_bar`, `selects_bar`), and
  it is a child of exactly the right-derived positive line nodes on `m` (`exists_child_split`,
  using unique rule names). `correlate_faithful` is rule-by-rule unfolding from this.
* `limitation_scope_sound` reads every hypothesis and every mechanism condition through the
  canonical interpretation (`canon`, `circ_canon`): `φ°` on a base-admissible `B` is `φ` at
  `canon B`. There `narrowings_complete` names an active mechanism, `condF_of_narrowsAt` makes
  its condition true, and the audit's licence gives the disjunct; a certified mechanism goes
  through `licensed_certified_sound`.
* `WellFormedRights` ends with `rightsSemanticCheck`: no rule's `over` names a bar node; no
  right-derived permission predicate has a permission dual; the own guard, `selects″`, every
  mechanism condition, the pack and (under the rule reading) `aimed_m` of every line are typed;
  `Lim_D` is typed over `E″′_base`. Each is implied by the construction and the diagnostics
  before it, as soft's `softSemanticCheck` is.

## Theorems in plain words

Names have prefix `VE.Rights.`.

| Theorem | Statement in plain words |
|---|---|
| `correlate_wellFormed` | A well-formed rights document elaborates to a well-formed soft document `(E″, T″)`. |
| `correlate_shape` | `correlate` keeps literals, the soft block, regulated declarations and definitions; `E″ = envR D`; the nodes are the line nodes in instance order, the outside rules, then the bar nodes. |
| `correlate_identity` | With no limitation, power, fan-out or bar, `E″ = E` and the nodes are the lines with the holder conjunct only, then the outside rules. |
| `correlate_identity_top`, `correlate_identity_top_env` | If moreover every holder guard is `⊤`, `correlate D` is exactly `flattenTop D`, so `E″ = E` and `E″′` is the flattened document's `E′`. |
| `liveR_denote` | The generated live formula of a line node denotes `LiveR`. |
| `bar_denote` | Under the rule reading, `bar_m` strictly selects exactly where `aimed_m` holds. |
| `strictDecidesR_denote` | Strict decisions on `T″` are the direct strict decisions (lines, outside rules, the bar). |
| `correlate_faithful`, `correlate_value` | `ValueSoft` on `T″` equals `ValueRight` on `D`; with `soften_faithful`, W1's `Value` on `T″′` does too. |
| `projections_agree` | For a duty line, `(R, N, v̄)` is among the holder's rights iff it is among the bearer's duties. |
| `owes_outcome` | A selecting line of the document with no opposite-sign decision fixes the completed outcome to the line's sign. |
| `same_effect_delivered` | A strict decision of a line's sign with no strict decision of the opposite sign fixes the outcome to that sign. |
| `bar_blocks` | Where `aimed_m` holds (rule reading): no right-derived positive line on `m` selects, the bar strictly decides `¬m`, and no default rule on `m` or `require`ing on `m`'s dual selects. |
| `bar_value` | If every positive rule on `m` is right-derived, `m` is false wherever `aimed_m` holds. |
| `narrowings_complete` | Where a line's own guard holds and it does not select, some listed mechanism is active. |
| `licensed_certified_sound` | An accepted certificate for `cond_n° → limpack_N` over `Background_base″` gives the pack wherever the mechanism's condition holds in a rights-admissible base. |
| `limitation_scope_sound` | With no audit finding, a line in scope of a limitation that does not select where its own guard holds is where some covering limitation holds, a cited mechanism is active, another right's line collides, a same-effect strict rule selects, or the bar applies. |
| `rightDerived_regulated` | Every right-derived predicate is regulated in `T″`. |
| `no_distinction_sound` | On a right-derived predicate with a protected-free cone, the completed outcome is invariant under the protected predicates. |
| `noDistinction_sound` | The audit reports `independent` only for protected-free cones. |
| `coherent_expands` | Soft's per-structure unique-expansion iff, on `correlate D` (reused). |
| `rights_coherent_expands_all` | Every rights-admissible base has a unique expansion iff the document is conflict-free over rights-admissible bases. |
| `rights_conflict_free` | Accepted certificates for every target over `Background_base″` prove `RightsConflictFree`. |
| `rights_conflict_witness_sound` | A valid finite base witness passing `Background_base″` refutes conflict-freedom and is classified (strict collision or pair conflict with a strict rule or a completion). |
| `rights_route_backgroundSound`, `rights_route_backgroundComplete` | On the rights route, `background″` holds in every admissible output satisfying the layer premises, and characterises output admissibility. |
| `rights_route_intended`, `rights_route_acceptance` | An accepted certificate for `background″ ++ elaborate T″′ ++ Γ ⊢ φ` gives φ under the direct soft semantics with the soft and limitation premises, and, given conflict-freedom and base formulas, over every rights-admissible base. |
| `rights_route_countermodel` | A rights-admissible base countermodel expands to a document expansion satisfying the soft and limitation premises that is still a countermodel. |
| `Wire.rights_wire_conflict_sound` | A successful raw conflict replay with every certificate accepted decodes to exactly the replayed well-formed document, which is conflict-free over rights-admissible bases. |
| `Wire.rights_wire_scope_sound` | A successful raw scope replay with no finding decodes to that document, and its audit with the replayed certificates is empty. |
| `Wire.rights_wire_acceptance` | A successful raw entailment replay with an accepted certificate decodes to that document and gives the two halves of `rights_route_acceptance`. |
| `Wire.rights_wire_conflict_witness_sound` | A successful raw witness replay whose target formula is true refutes conflict-freedom, classified. |

The remaining theorems are helper lemmas, audited with the same allowlist.

## Statement deviations (recorded for the reviewers)

1. `WellFormedRights` is in `Correlate.lean`, not `Tree.lean` (it ends with `validateSoft`
   on `correlate D`), and `narrowings`/`condF` are there too, because the semantic check
   records their typing.
2. The direct semantics recurses on rules (`StrictYieldsX`, `SelectsX`, … over `directNodes D`,
   the rules of `T″` without bars), because a line's exception may be a rule outside rights.
   The line-level names of 9.1 (`StrictSelectsR`, `SelectsR`, …) are the rule-level ones on the
   line's node; `LiveX` is soft's `LiveD` on a rule, which for a line node is `LiveR`
   (`liveR_denote`). `StrictDecidesR` uses the direct strict selection for outside rules too.
3. `rightsOf` and `dutiesOf` are predicates (`TupleSet`) with a membership instance: the
   project has no Mathlib `Set`. `vs.get? i` is written `vs[i]?`.
4. `projections_agree` takes the holder and bearer values as implicit arguments.
5. `rightDerived_regulated` concludes `p ∈ regulatedNames (correlate D).base.T` (`(correlate D).T`
   is a `SoftTree`), as soft-norms' deviation 3.
6. `licensed_certified_sound`'s target is written with `.implies` (the spec's `.imp`) and `φ°` as
   `outcomeSubst D φ`.
7. `RightsDoc` has an `outsideCites` field: the citations of the norm units outside rights
   (`cites["narrows:<line>"]`, 3.2), which `SoftNode` does not carry.
8. The `bar` mechanism is listed only under the rule reading (the only reading with a bar
   node); `barReach` itself is as specified. The typing fact for `aimed_m` is required under
   the rule reading only (without a bar unit `aimed_m` is not declared).
9. `rightsRoute`'s subtype is exactly the spec's; `E_out` is the separate lemma
   `rightsRoute_E_out`.
10. (Withdrawn.) The decoder records the source line order (`RightsDoc.sourceOrder`), so a
   `right_lines` unit appends to its right at the unit's own position and instance order and
   fan-out indices are 1.6's.
11. Carve-out mechanisms are 0-based internally and rendered 1-based (`carve-out 1`, citation
   key `unless:1`), as the spec numbers `U_1`.
12. Arity is at most two in the Lean formula language, so the ternary `nary@0` fixtures (μ, ψ)
   are not expressible; `Examples.lean` and `tests/test_rights_lean.py` cover their binary shapes
   on `publish_about(person, person)`.
13. `rightCollision` follows the 4.5 table and 13.6, and the 9.1 comment is tightened to match:
   blocking by a right-derived strict line of the opposite effect is a collision; dominance by a
   right-derived line is a collision only under a cited ranking (`cites["rank"]` on either
   line), so an uncited rank between two rights' lines stays `UnlicensedLimitation` (fixture μ).
   `narrowings` lists `dominatedBy M` only when `M` can dominate (`dominable`: `M` outranks the
   line, or holistic outranking with the line above `M`), the two disjuncts of `dom(M, N)`; a
   lower-ranked `M` under strict outranking is never active and is not listed.

## The `ve_rights_route` cases

Every case is `{"id", "kind", "environment", "document", ...}` with a `ve.core@0.2`
environment whose sorted profiles contain `rights@0`, `soft-norms@0` and `norms@0`, the
vocabulary's `rights` block (3.1: `holders`, `bearers`, optional `protected` and `alters`),
and `document` the array of unit contents of 3.2. Case kinds and outputs are listed in
`Run.lean`: `rights-elaborate`, `rights-projections`, `rights-scope`, `rights-conflict`
(packages or witness), `rights-bar`, `rights-certificate`. Cases without a rights construct
delegate to `ve_soft_norms_route` behaviour unchanged.

Matched wire choices (the Lean executable's choices where the spec leaves bytes open):

* No `null` on the Lean wire: `holder_slot`, `recognition`, `decided_by` and a fan-out line's
  `predicate` are sent absent.
* An outside norm unit is `{"norm": {...}}` with an optional `"cites"` beside `norm`.
* Generated predicate entries in `E″′` JSON: `{"arguments": <sorts>, "description":
  "rights-generated open predicate"}`, appended after the author predicates and before soft's
  decision entries.
* Rights document hash: domain `ve-rights-<identity version>\n` over `{"environment_id",
  "document": [canonical units]}`, each norm object omitting `mode: "strict"`, `alterable: []`,
  `hard: false`.
* Scope packages are keyed by `<rule>:<mechanism>` (e.g. `no-arbitrary-arrest:exception rule-7`).
* `conditional_on` lists a coherence or limitation label when a certificate's replay fails with
  that premise replaced by `⊤` at its position (soft's convention), so it may include premises
  a proof touches without needing them.

## Status and what is not claimed

* Proved: every theorem of spec 9.2, the wire theorems of 9.3 and the rights W2
  admission theorem on accepted documents (with the deviations recorded).
* W2 `admission` on the rights path decodes active right, right_lines, limitation,
  bar and outside norm units; regenerates the extended environment and exact layer,
  soft and limitation leaves; checks source citation ids and coupling labels; and
  proves `Run.rights_wire_acceptance`. Reading sets whose candidates are rights
  objects still require per-choice elaboration and are reported as pending by the
  document checker.
* Tested: `Examples.lean` (build-time `#guard`: well-formedness, exact diagnostic texts,
  generated names, `Lim_D` labels, outcomes on finite base models through `selects″°` and
  `O_p°`, the audit with an uncited and a cited adopter exception); `tests/test_rights_lean.py`
  drives the executable, including an end-to-end CONFLICT-FREE replay whose certificate
  (Python's unchanged prover over the Lean-regenerated `E″′_base`) needs a `Lim_D` premise.
  `WellFormedRights` is not kernel-decidable on concrete documents (the frozen soft validator
  uses `mergeSort`/`startsWith`), so the examples are compiled evaluations, not kernel proofs.
* Not claimed, as in the spec (9.5): completeness of the conflict check or the classification
  outside norms.md 7 on `T″′`; anything about the English surface; that `ValueRight` matches an
  author's intent; anything about deciders; that a coupling is the right interpretation; the
  effect of a power or a forbidden status change; enumeration completeness.
