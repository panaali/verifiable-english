# The `unspecified` completion in Lean (`lean/VE/NormDefaults/*`)

Specification: [docs/spec/norm-defaults.md](../docs/spec/norm-defaults.md) section 7 (the theorem
statements) and [docs/spec/norm-defaults-PLAN.md](../docs/spec/norm-defaults-PLAN.md) section 11,
work item (2). This file lists the definitions and every section-7 theorem in plain words, and the
places where a section-7 statement had to change because it is false as written. `lean/audit.py`
audits every theorem: no `sorry`, only `propext`, `Classical.choice` and `Quot.sound`. No
`lean/VE/Norms/*`, `lean/VE/SoftNorms/*`, `lean/VE/Route/*` or P0 source changed
(`python3 VE/Route/frozen.py` passes; `frozen-sources.sha256` gained the new modules and the new
`VE/Audit.lean` hash, every other entry is unchanged). `VE/Audit.lean` gained imports and audit
entries only; `lakefile.toml` gained the `ve_norm_defaults_route` target (root
`NormDefaultsMain.lean`, which calls `VE.NormDefaults.Run.main`; also in `defaultTargets`). The audit allowlist is unchanged.

## Files

| File | Contents |
|---|---|
| `Tree.lean` | `Completion`, `UDoc`, `completionOf`, `unsaidName`, `fillName`, `fillNode`, `UDoc.switch`, `sortsOf`, `unsaidNames`, `pairMembers`; `fillEnv` (`E‴`), `fillRoot`, `fillNodes`, `fillTree`, `fill`; `WellFormedU` = `WellFormed U.D` ∧ `unspecDeclared` ∧ `reservedFree` ∧ `limitsU` ((i)–(v)) |
| `Dag.lean` | Two facts about the shared `dependencyOrder`: Kahn's search succeeds on an acyclic graph with distinct names (`dependencyOrder_ok`), and the order reads only names and edges (`dependencyOrder_congr`) |
| `Check.lean` | W1's `check` restated with named loop bodies (`checkSteps`, `check_eq : check D = checkSteps D` by `rfl`), read declaratively (`CheckOK`, `check_iff`, `wellFormed_iff`); the same for `actChecks` (`actSteps`, `actChecks_dual`) |
| `Fill.lean` | `UValid` (the facts `WellFormedU` gives); the structure of `T‴`; fuel stability (`yields_stable`, `selects_stable`); "a subtree yields iff one of its rules selects" (`yields_iff_selects`); `fill_selects_author`, `fill_decides`, `fill_local_conflict`, `fill_eq_self` |
| `FillCheck.lean` | `fill_wellFormed`: `CheckOK (fill U)` and `semanticCheck (fill U)` from `WellFormedU U` |
| `Semantics.lean` | `Outcome3`, `value3`, `Value3`, `IntendedAt3`, `Expansion3`; `fill_intended` |
| `Premises.lean` | `gapF`, `reachedF`, `fillPremises` (`Fill_T`), `BaseAdmissibleU`, `ConflictFreeU`, `FillTables`, `withFill`, `canonicalFill`, `canonTyped`, `expandFill`; `fill_conservative`, `conflictFreeU_iff`, `canonical_fill_sat`, `fill_extends` |
| `Status.lean` | `fill_expansions`, `conflictFreeU_consistent`, `SettledAs`, `UndecidedAt`, `settled_expansions`, `settled_all_expansions`, `undecided_expansions`, `unreached_switch` |
| `Evidence.lean` | `FiniteFill`, `FiniteModel.withFill`, `fillValid`; Kleene evaluation (`kleene`, `kleene_sound`); `table3` (DAG order, pair rule); `enumerateSettled`; `table3_sound`, `settled_of_table3`, `settled_of_enumeration`, `undecided_witness_sound`, `conflictU_witness_sound` (and its pair companion), `UniversalQF`, `fillPremises_universal` |
| `Routes.lean` | `fill_soft_value`, `excepted_lifts`, `excepted_collapses_under_deny`, `fill_rights_value`; the followability formulas on the filled tree (`allFollowableU`, `backgroundBaseAltU`, `BaseAdmissibleAltU`) and `followableU_sound` |
| `Wire.lean` | The `norm-defaults@0` decoder (`decodeSourceU`), `decode_conservative`; regenerated outputs (`regeneratedU`); conflict-package replay over `E‴_base` and `Background_base(E‴) ++ Fill_T` (`normDefaults_wire_conflict_sound`, `normDefaults_wire_expands`); entailment replay (`normDefaults_wire_acceptance`) |
| `Replay.lean` | Filled CONFLICT witnesses over `E‴_base` (`baseModelVocabularyU`, `normDefaults_wire_witness_sound`), status replays (`table3`, enumeration, two fillings; `normDefaults_wire_status_sound`) and `gaps: none` certificates (`normDefaults_wire_gaps_sound`) |
| `Admission.lean` | W2 admission on `fill U` (`admitDocument`, `admitDocument_spec`): nodes over `E‴`, certificates bound to the regenerated `E‴` JSON (`fillJson`), leaves that are W2 provenance, a layer of `T‴`, a pair premise or a `Fill_T` premise under `unsaid:pair:<r>,<m>`; `wire_report_consequence` |
| `Run.lean` | The `ve_norm_defaults_route` dispatch: `norm-defaults-elaborate`, `-conflict` (packages or `witness`), `-status` (answer key `point_status`), `-gaps`, `-certificate`, and `admission` under the profile (`normDefaults_wire_admission`; the report id binds the source environment under its own profiles); every other case goes to the unchanged `ve_norms_route` logic |
| `Examples.lean` | Build-time `#guard` regressions in the shapes of fixtures u1, u5 (a)–(c), u6, u12 and u16 |

## How the proofs are organised

`fill U` is an ordinary W1 document, so every W1 theorem applies to it once
`WellFormed (fill U)` is known; `fill_wellFormed` supplies it from `WellFormedU U`, never as a
hypothesis. Its proof reads W1's imperative `check` through `check_iff`, whose restatement
`checkSteps` is definitionally `check` (`rfl`), and walks each condition on `T‴`: `F_p` adds one
rule (limit (iii)), one rule name ((i), (ii), unused names), one typed guard (`E‴` declares
`unsaid__p` with `p`'s sorts), a bounded AST ((v)) and one precedence level ((iv)); the
precedence DAG stays acyclic because `F_p` has no parent (`fill_acyclic`, then `dependencyOrder_ok`),
and the stratum order is unchanged because `unsaid__p` is not a node of the stratum DAG
(`dependencyOrder_congr`).

Base formulas are read through soft's `canon` (every layer symbol interpreted by its substituted
meaning); `fill_decides` then says the synthetic rule's value at a gap is the filling. Source
expansions and filled W1 expansions differ only on the unsaid tables, which no Background formula,
decision formula or `IntendedAt3` reads (`sat_background_congr`, `intendedAt3_congr`).

## Theorems (section 7 order)

- `fill_wellFormed`: the author-side limits of `WellFormedU` suffice: `WellFormed (fill U)`.
- `fill_conservative`: without unspecified predicates, `fill U = U.D` and `Fill_T = []`.
- `fill_selects_author`: no author rule's `selects` formula changes truth on `T‴` (fuel included).
- `fill_decides`: on an unspecified `p`, `T‴` decides "yes" iff the author rules do, or the gap is
  filled "yes" and no author rule decides; it decides "no" iff the author rules do.
- `fill_local_conflict`: the local conflict target of every regulated predicate is W1's.
- `fill_intended`: W1's meaning of `p` on `T‴` is `IntendedAt3` plus agreement with the filling at
  the gaps.
- `fill_expansions`: the source expansions of `B` are exactly the filled W1 expansions (with an
  admissible filling) with the unsaid tables forgotten.
- `canonical_fill_sat`: "true on permission members, false elsewhere" satisfies `Fill_T`.
- `fill_extends`: any filling can be made admissible by changing only pair members' tables.
- `conflictFreeU_iff`: CONFLICT-FREE under every admissible filling iff a unique filled expansion.
- `conflictFreeU_consistent`: a CONFLICT-FREE document has a source expansion in every base
  situation.
- `settled_expansions`, `settled_all_expansions`, `undecided_expansions`: a SETTLED point has its
  value in every expansion of a CONFLICT-FREE document (and in the canonical expansion of each
  admissible conflict-free filling); an UNDECIDED point has opposite values in two expansions.
- `unreached_switch`: switching a deny/allow completion that no admissible filling reaches to
  `unspecified` changes no expansion (see finding 2).
- `table3_sound`, `settled_of_table3`: a definite `table3` entry is the outcome under every checked
  filling, hence SETTLED.
- `settled_of_enumeration`: agreement of every checked filling is SETTLED.
- `undecided_witness_sound`: two checked finite fillings with opposite outcomes witness UNDECIDED.
- `conflictU_witness_sound` (and `conflictU_pair_witness_sound`): a filled finite witness (settled or
  latent) refutes `ConflictFreeU`.
- `fillPremises_universal`: under W1's gate on `fill U`, every `Fill_T` formula is universal
  quantifier-free.
- `fill_soft_value`, `fill_rights_value`: on the soft and rights routes `Value3` reads the route's
  own decisions; `excepted_lifts`: an excepted sole default rule leaves an unspecified act unsaid
  (`excepted_collapses_under_deny` keeps the deny collapse as a regression).
- `followableU_sound`: an accepted certificate for `∀r. followable°(r)` on the filled tree, with
  `Fill_T` in the background, gives FOLLOWABLE under every admissible filling.
- `decode_conservative`: without `unspecified` and without the profile, the decoder is exactly the
  norms decoder with `unspec = []`, and the canonical environment bytes are the same.
- `normDefaults_wire_conflict_sound`, `normDefaults_wire_acceptance`: from a successful raw replay,
  for the document decoded from that very input: CONFLICT-FREE under every admissible filling; the
  conclusion in every filled expansion that satisfies the premises.
- `normDefaults_wire_witness_sound`, `normDefaults_wire_status_sound`, `normDefaults_wire_gaps_sound`
  (additions): a replayed filled witness refutes CONFLICT-FREE (settled or latent); a replayed
  SETTLED/UNDECIDED status is `SettledAs`/`UndecidedAt`; an accepted `∀x̄. ¬reached_p` certificate
  means no admissible filling reaches `p` (`gaps: none`, the hypothesis of `unreached_switch` when
  computed on `U.switch p`).

## Findings: statements changed because the section-7 form is false

1. **`settled_expansions` and `undecided_expansions`.** `expandFill` is written with `canon`, which
   holds on ill-typed tuples wherever a substituted outcome is true there (a rule with guard `⊤`
   makes every tuple true), so `expandFill` need not be admissible and `Expansion3` fails. With
   `canon` read on typed tuples (`canonTyped`), the relation claim fails at ill-typed `vs`, where an
   outcome formula can still be true. Change: `expandFill` uses `canonTyped`, and both theorems take
   `typed : VE.TupleTyped B r.sorts vs`, as `settled_all_expansions` already does (review finding 10).
2. **`unreached_switch`.** Counterexample to the section-7 form: `r` an unspecified obligation with
   no rules, paired with `m` (permission, deny, rule `m if p`); `p` deny with the rule `p if not r`.
   Under `U` the pair premise forces every gap of `r` to "no", so `p` is never reached and `hnr`
   holds; after the switch, `r` = yes, `p` = yes (a gap filled yes), `m` = yes is an expansion of
   `U.switch p` that `U` rejects. Change: `hnr` quantifies over the admissible fillings of
   `U.switch p` and reads `reachedF (U.switch p) p`. The migration audit (6.3) must compute the
   certificate on the switched document.
3. **`fill_rights_value`** takes `WellFormedRights D` (what `correlate_faithful` needs);
   `WellFormedU` does not imply it.

## Notes for the Python side and the statement pass

- `enumerateSettled` enumerates every unsaid atom of the finite situation (bounded by
  `MAX_UNSAID_ATOMS = 12`). Enumerating only the atoms in `ā`'s cone, with the others fixed, is not
  sound in general: a premise at a point in the cone can read, through a guard, an atom outside it.
- `table3`'s pair rule fires where the pair closes: it sets the member being placed if that member
  is the gap, and otherwise the earlier member's still-unknown entry (`closeRule`); symbols placed
  in between keep the earlier unknown (sound, less complete). Fixture u5(b) needs the second case:
  with no dependency between the members, `x_permitted` is placed first.
- `canonicalFill` needs no typing: `withFill` reads every filling on typed tuples only.
- `reservedFree` checks the reserved prefixes on regulated, defined and rule names, and that the
  names `fill` introduces are undeclared; base predicate names cannot be enumerated from an
  `Environment`, so the decoder checks the prefix on every declared name.
- `E‴_base` on the wire (`baseEnvironmentJsonU`) adds each `unsaid__p` as
  `{"arguments": sorts, "description": "the text does not say whether p"}`; Python must build the
  same bytes for certificate bindings.

## Not done in this item

`default reached` witnesses and `UngroundedDefault` findings on the wire (the report block), the soft, rights,
alternatives and risk route branches (their Wire/Run files are frozen here) and W8. Python's side
(`ve/norm_defaults_route.py`) and the three-way fixtures (`conformance/norm_defaults_three_way.py`,
`tests/test_norm_defaults_three_way.py`) were added at integration.
