# Weighing reasons, in Lean (`lean/VE/Weighing/*`)

Specification: weighing-PLAN section 3.4 (on branch refresh/weighing-20261028 at bda82d18c; the weighing family's
plan item brings it to main). This file is a stub: so far it holds only the zone's six shared definitions (item
wg-6a), which defeasible's DF-5 also states its zone over. The zone answers (`zoneOf`, `recordCheck`, `ZoneAnswer`)
and their theorems are WG-6's and extend `Zone.lean`. No service mode answers through these files yet, and no
current answer changes.

## Files

| File | Contents |
|---|---|
| `Zone.lean` | `decisionAtoms`, `openNames`, `AdmissibleCompletion`, `OutcomeIn`, `SettledZ`, `ZoneUnknown` |
| `ZoneExamples.lean` | the six on defeasible's decoded DF-α document and on a small literal document, as `#guard`s and proved `example`s |
| `Tree.lean` | the block, its targets and the strength of a rank pair (WG-2, weighing.md 1.1-1.3) |
| `Conditions.lean` | the premises `Weigh_T`, the implication check, `checkWeigh`, `WellFormedWeigh` and weighing.md 5's theorems that wg-2 proves |
| `Examples.lean` | W-α, W-β's witness, W-ε, W-λ and W-μ, the strict flag, the implication bounds and `strength_iff`'s counterexample, as `#guard`s |

## Definitions

- **`decisionAtoms D M`.** Every ground atom a decider could settle in the finite situation `M`: each decision
  predicate of the soft document `D` (its exceptions, switches and outweighing choices), at each tuple of `M` of that
  predicate's sorts, predicate by predicate and tuple by tuple in `M`'s order.
- **`openNames L`.** The predicate names a completion may choose freely for the layered document `L`: its decision
  predicates, then the unsaid tables of its unspecified regulated predicates.
- **`AdmissibleCompletion U X M opens record R`.** `R` is a way to finish the situation `M`: it agrees with `M` on
  every predicate outside `opens`, it agrees with the record on every atom the record fixes, and the finished
  situation satisfies the document's base admissibility on `fill U` with the route's extra premises `X`.
- **`OutcomeIn U M R r vs`.** In the situation `M` finished by `R`, the regulated predicate `r` comes out true at
  the tuple `vs` (its base outcome formula on `fill U` holds there).
- **`SettledZ U X M opens record r vs b`.** The outcome of `r` at `vs` is settled as `b`: at least one admissible
  completion exists, and every admissible completion gives the outcome `b`. Without a completion nothing is
  settled, so a contradictory record settles nothing.
- **`ZoneUnknown α`.** Why a zone answer is `unknown`: `budget`, the enumeration stopped because there were more
  open atoms than the limit; or `branch`, a complete enumeration left an assignment that nothing refuted and no
  checked completion confirmed.

Nothing calls this code yet: no service mode, decoder or answer reads `VE.Weighing.Tree` or `Conditions`. The block
decoder, the pack and the profile row are WG-3's. The zone interface is `Weighing/Zone.lean` (wg-6a).

## Block, strength, conditions and grants (WG-2): definitions

- `Tree.lean`. `WeighEnv` is the decoded block: the `always` edges, the conditions, the factor lists and the grants.
  `WeighDoc` is a soft document with its block and AP's split map. A `Target` is an open decision of soft: an
  `outweighs` atom `(act, lower, higher)` or a switch `(rule, party)`. `targetF` is that decision's atom over
  `targetSorts`, its argument sorts. `targetExists` says the decision is one of soft's. `rankOrder` is soft's ranks as
  QS-1's order. `strictPair H L` holds when some `always` edge `(a, b)` has `H` at or above `a` and `b` at or above `L`.
  `chainEdges c` lists the steps of a list of ranks, and `RankChain H L c` says `c` runs from `H` down to `L` along
  declared edges. `chainsFrom` lists every such chain, with the number of ranks as fuel. `strictWitness H L` is the
  chain the paraphrase shows: the shortest chain from `H` to `L` that passes an `always` edge, the least in list order
  among the shortest (`chainLt`), and nothing when the pair is not strict.
- `Conditions.lean`. A strength premise (`Str_T`) says no act of a strict pair outweighs. `condPremise` is the one
  generator: a sufficient condition implies its decision, and a decision implies each of its necessary conditions. A
  grant becomes necessary conditions on the grantee's switch: the grant itself, then every necessary condition and grant
  of each party the switch is granted through (`grantConds`). `weighLabelled` lists the premises with their labels, and
  `weighOrigins` gives each label's request path. `propImplies a b` checks `a → b` over every truth assignment to at
  most 12 distinct atoms. `checkWeigh` makes weighing.md 1.6's checks in order. `WellFormedWeigh` is
  `WellFormedSoft` and `checkWeigh` together.
- `Conditions.lean`, for the statements. `strictFlag D` is the document with the strict flag in place of the
  holistic one. `SameBase B B'` says `B'` is `B` with only the decision predicates changed. `freeWitness` is the
  structure `weigh_alone_base_free` builds: each `outweighs` atom holds exactly where one of its sufficient conditions
  holds, every switch is off, and every other predicate is `B`'s.
- `VE.Acts.splitRefusal role name` is AP's refusal text. `refsOk` now uses it, with the same bytes.

## Block, strength, conditions and grants (WG-2): theorems (each assumes `WellFormedWeigh`, except where noted)

- `strictPair_outranks`: a strict pair is ordered: the higher rank outranks the lower through the declared edges.
- `strictPair_of_always` (no assumption): an `always` edge is itself a strict pair.
- `strictPair_down`, `strictPair_up`: a pair below a strict pair's lower rank, or above its higher rank, is strict.
- `propImplies_sound` (no assumption): when the check accepts `a → b`, every structure and valuation that makes `a`
  true makes `b` true.
- `condition_necessary`: in every structure that satisfies the weighing premises, a decision is false at a typed
  tuple where one of its necessary conditions is false.
- `condition_sufficient`: in such a structure, a decision is true wherever one of its sufficient conditions is true.
- `grant_needed`: in such a structure, a granted switch is off wherever its grant's predicate is false.
- `delegation_bounded`: a grant names a rule that declares switches for both the party and the grantor, and the
  grant's predicate is attributed to the grantor.
- `weigh_conservative`, `wellFormedWeigh_empty` (no assumption): an empty block adds no premise and accepts exactly
  the documents soft accepts.
- `holistic_iff_no_always_chain`: a pair is not strict exactly when no chain of declared edges from the higher rank
  to the lower one passes an `always` edge.
- `strictWitness_isSome`: the paraphrase names a chain exactly for the strict pairs. `strictWitness_chain` (no
  assumption): the chain it names runs from the higher rank to the lower one along declared edges and passes an
  `always` edge.
- `always_dominates`: in every structure that satisfies the strength premises, an effective higher default rule of a
  strict pair dominates a colliding lower default rule. `always_no_override`: there the lower rule never overrides
  the higher one.
- `all_always_is_strict`: when every comparable colliding pair is strict, the document decides every act exactly as
  the same document under the strict flag, in every structure that satisfies the strength premises.
- `factors_inert` (no assumption): factor lists add no premise.
- `grant_within_grantor`: where a granted switch is on, every necessary condition and every grant of each party it is
  granted through holds.
- `weighPremises_wellFormed`: every weighing premise is a closed formula over the base vocabulary of the filled
  document (PK-1's typing obligation). `weighPremises_substructure`: every premise survives sort-respecting
  substructures (soft's fragment).
- `weigh_alone_base_free`: for every structure `B` there is a structure with `B`'s base predicates that satisfies the
  weighing premises: they alone never constrain the base.

- `strength_iff` (weighing.md 5.1, wg-2-siff): when every regulated name begins with an ASCII letter (the decoder's
  identifier rule, so every wire document), `Str_T` has a premise exactly for the `outweighs` decisions of strict
  pairs. Without that hypothesis it is false on a document built without the decoder (a regulated predicate named
  `_x_permitted`, or its mirror; `Examples.lean`'s guards, weighing.md 7.3 F19). The proof recovers the ranks and the
  act from the `outweighs` name (`outweighsName_inj`). Its reverse direction, `strength_mem`, holds for every triple.

The helpers `weighFacts` and `condFacts` (what an accepted block guarantees), `rankOrder_above` (soft's `outranksPlus`
is QS-1's `above`), `evalProp_denote`, `condPremise_mem`, the chain lemmas, `premise_facts` and the arity lemmas are
lemmas for these proofs.

Not in this part (wg-2b): `holistic_iff_no_always_chain`, `strictWitness` with `strictWitness_isSome` and
`strictWitness_chain`, `always_dominates`, `always_no_override`, `all_always_is_strict`,
`grant_within_grantor`, `weighPremises_wellFormed`, `weighPremises_substructure`, `weigh_alone_base_free`, and the
rest of weighing.md 7.2's fixtures.
