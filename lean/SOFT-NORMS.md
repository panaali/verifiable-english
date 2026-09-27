# Soft norms in Lean (`lean/VE/SoftNorms/*`, item 4)

Specification: [docs/spec/soft-norms.md](../docs/spec/soft-norms.md) section 9 (the approved
statements) and [docs/spec/soft-norms-PLAN.md](../docs/spec/soft-norms-PLAN.md) section 5 row 4.
This file lists every definition the statement review reads and every theorem in plain words.
All statements quantify universally over their displayed parameters. `lean/audit.py` audits
every theorem: no `sorry`, only `propext`, `Classical.choice` and `Quot.sound`. No frozen P0
file and no `lean/VE/Norms/*` or `lean/VE/Route/*` source changed (`python3 VE/Route/frozen.py`
passes); `VE.lean` and `VE/Audit.lean` gained imports and audit entries only, and
`lakefile.toml` gained the `ve_soft_norms_route` target (root `SoftNormsMain.lean`, also in
`defaultTargets`) without changing existing targets. The audit allowlist is unchanged.

## Files

| File | Contents |
|---|---|
| `Tree.lean` | `Mode`, `Outranking`, `Exception`, `SoftNode` (a W1 `Node` plus mode, rank, alterable, exception, hard), `SoftEnv`, `SoftTree`, `SoftDoc` and its W1 base; declarations (`sortsOf`, `dualPerm`, `dualOblig`, `actKey`, `act`); children; the rank closure `outranksPlus` and `rankHeight`; `Incompatible`, `Comparable`, `collidingPairs`; the decision vocabulary (`exceptedName`, `offName`, `outweighsName`, `decisions`, `envPrime`, `weighingSyms`, `attributed`) |
| `Soften.lean` | every generated formula of `ValueSoft` (`strictDecidesF` on the strict core, `liveF`, `blockedF`, `eligibleF`, `domWith`/`effF`/`dominatedF`), `derived`, `derivedList`, `primeNode`, `soften`; `selects'`, `defaultDecidesF`, `excPremises`, `cohPremise(s)`, `softPremises`; the executable `checkSoft`/`validateSoft`/`WellFormedSoft` with the section 8 diagnostics; `SoftValid`; shape theorems |
| `Semantics.lean` | the direct semantics (`LiveD` … `DecidesSoftD`, `ValueSoft`, `IntendedSoftAt`, `holdsSoft`); denotation lemmas; `soften_faithful`; fuel, existence, rank resolution, hard over soft, weighing independence, the cone and its independence theorems, `rank_acyclic`, `weighing_points_complete` |
| `Coherence.lean` | `backgroundBase'`, `background'`, `BaseAdmissible'`, `PrefixAdmissible'`, `NoStrictCollision`, `NoHardPairConflict`, `SoftConflictFree`; the canonical interpretation `canon`; the decomposition and its consequences; `softConflictFreeCheck`; witnesses; `InFragment`, `BaseSubstructure`; the restated route (`softSymLayer`, `softChain`, `softRoute`) and its theorems |
| `Status.lean` | `PairStatus`, `classificationBackground`; `coh_rank_valid`, `disjoint_sound`, `weighing_point_sound` |
| `Wire.lean` | the soft environment and norm decoders, `SoftSource`, identity (`softDocumentHash`, `basePrimeJson`, `primeJson`), regenerated outputs, conflict-package, witness and entailment replays |
| `Admission.lean` | W2 admission with soft norm units (W1's `Norms.Admission` with the soft decoder) |
| `Run.lean`, `../SoftNormsMain.lean` | the `ve_soft_norms_route` executable, `SoftAdmissionAnswer`, `Run.soft_wire_acceptance` |

## How the proofs are organised

* `soften D` is an ordinary W1 `Doc`, so W1's per-structure lemmas (`selects_denote`,
  `elaborate_iff`, `local_expands`, `conflictFreeAt_of_base`, `prefix_char`,
  `conflictFree_expands_document`, the frozen `Layer`, `Layer.comp`, `route_acceptance`,
  `route_countermodel_expands`, `route_entails_iff`) apply to `T′` unchanged.
* Each generated formula mirrors its proposition syntactically, with the same fuel; so
  `soften_faithful` is unfolding (`derived_denote`, children commuting with `primeNode`) and
  needs no fuel argument. Fuel matters only for `eff_fuel`, `rank_resolves` and
  `eligible_effective`, through `rankHeight_lt_of_higher` (a higher rank has a strictly
  smaller height), proved from the rank order returned by the shared `dependencyOrder`.
* Strict selection is generated on the *strict core* (`coreNode`: ranks, exceptions, `hard`
  and default rules' switches removed), so `hard_never_weighed` (ii) is a rewrite.
* `canon D B` interprets every layer symbol of `T′` over a base structure `B` by its
  substituted meaning; it exists even at conflict points. On typed valuations `φ°` in `B`
  is `φ` in `canon B` (`canon_subst`), which turns every base conflict formula into a
  statement about the direct semantics; `soft_conflict_decomposition` then follows from
  `hard_over_soft`, `weighing_points_complete` and the coherence conjuncts.
* `WellFormedSoft` ends with `softSemanticCheck`, the facts the proofs use (unique rule and
  regulated names, the pair maps, rank declarations and order, `SoftOverHard`, fresh and
  unique decision names, typing of guards, of the generated soft premises and of the
  selection formulas, equal sorts across colliding pairs). Each is implied by the
  diagnostics before it (as W1's `semanticCheck` is), so it rejects no document they accept.

## Theorems in plain words

Names have prefix `VE.SoftNorms.`.

| Theorem | Statement in plain words |
|---|---|
| `soften_wellFormed` | A document passing `WellFormedSoft` elaborates to a W1-well-formed `T′` over `E′`. |
| `soften_shape` | `soften` keeps `E′`, literals, regulated declarations, definitions and every node, adding only `derivedList` after the author carve-outs. |
| `soften_hard_identity` | If every rule is strict and unswitchable, `E′ = E` and `T′`'s nodes are the rules unchanged (fixture ξ). |
| `live_denote`, `strictDecides_denote`, `blocked_denote`, `eff_denote`, `dominated_denote`, `derived_denote` | Each generated formula denotes its direct-semantics proposition; `applies` of a `T′` node is `AppliesSoftD`. |
| `eff_fuel` | Effectiveness of a rule is the same at every fuel above its rank height, in particular at `rankFuel`. |
| `soften_faithful` | W1's `Value` on `T′` equals `ValueSoft` on `T`, on every structure and tuple. |
| `soft_intended_iff`, `soft_elaborate_iff` | `IntendedAt` on `T′` is `IntendedSoftAt`; `T′`'s elaborations hold iff `holdsSoft`. |
| `eligible_effective` | At a fixed act and tuple, if some default rule on the act is eligible, some default rule on it is effective (4.3). |
| `hard_over_soft` | A strict decision on a predicate silences every default on it; a strict prohibition silences a default obligation across the pair, and a strict obligation a default prohibition. |
| `hard_over_soft_base` | The same for the base formulas of `T′`, in every structure: no conflict point has a strict rule on one side and a default rule on the other. |
| `hard_never_weighed` | Strict selection mentions no weighing symbol, is a function of the strict core only, and is invariant under any change to weighing symbols. |
| `cone_independent` | `O_p°` is invariant under changes to predicates outside `cone(p)`. |
| `hard_never_weighed_global` | With a decision-free cone, `O_p°` is invariant under changes to decisions (fixture μ shows the hypothesis is needed). |
| `authority_independent` | If no predicate attributed to party π is in the cone, `O_p°` is invariant under changes to π's predicates (declared attribution only). |
| `rank_acyclic` | The rank graph is acyclic and `outranks⁺` is irreflexive and transitive. |
| `rank_resolves` | Two comparable colliding default rules never both select. |
| `coh_rank_valid` | The coherence conjunct of a comparable colliding pair holds in every structure admissible for `E′_base`. |
| `weighing_points_complete` | Every default–default collision on a predicate or across a pair is at a colliding pair of `CP(T)` whose ranks are not comparable. |
| `soft_premises_substructure` | Under the complete fragment gate every generated soft premise survives sort-respecting substructures of `E′_base`. |
| `coherent_expands` | W1's pointwise document iff on `T′`: exactly one expansion iff conflict-free (reused). |
| `soft_conflict_decomposition` | Over a base-admissible structure, conflict-freedom of `T′` is exactly: no strict collision, no pair conflict unless both sides are default, and `Coh_T`. |
| `soft_conflict_free_iff` | Conflict-freedom over coherent bases is exactly no strict collision and no hard pair conflict. |
| `soft_witness_classified` | A conflict in a coherent base is a strict collision or a pair conflict with a strict rule or a completion. |
| `soft_coherent_expands_all` | Every coherent base has a unique expansion iff the document is conflict-free over coherent bases. |
| `soft_conflict_free` | Accepted certificates for every target over `Background_base′` prove `SoftConflictFree` (the certified statement). |
| `soft_conflict_witness_sound` | A valid finite base witness over `E′_base` passing `Background_base′` refutes conflict-freedom, unique expansion and `SoftConflictFree`, and is classified. |
| `disjoint_sound` | A DISJOINT certificate over `Background_base(E′) ++ Exc_T` proves the conjunct. |
| `weighing_point_sound` | A WEIGHING POINT witness refutes the conjunct and the unconditional claim. |
| `soft_prefix_satisfaction` | `PrefixAdmissible′` is admissibility, `BaseAdmissible′` of the base restriction and the prefix's premises. |
| `soft_conflictFree_prefix` | Coherent conflict-freedom gives each layer's local test on every `PrefixAdmissible′` prefix. |
| `soft_route_backgroundSound`, `soft_route_backgroundComplete` | On the soft route, `background′` holds in every admissible output satisfying the layer premises, and characterises output admissibility. |
| `soft_route_intended`, `soft_route_acceptance` | An accepted certificate for `background′ ++ elaborate T′ ++ Γ ⊢ φ` gives φ under the direct soft semantics, and, for a coherently conflict-free document and base formulas, over every `BaseAdmissible′` structure (through the frozen route). |
| `soft_route_countermodel` | A coherent base countermodel expands to a document expansion that satisfies the soft premises and is still a countermodel. |
| `soft_route_entails_iff` | For base formulas, the checked entailment over `E′` is exactly consequence over `BaseAdmissible′` structures. |
| `Wire.soft_wire_conflict_sound` | A successful raw conflict-package replay with every certificate accepted: the input decodes to exactly the replayed well-formed soft document, which is conflict-free over coherent bases. |
| `Wire.soft_wire_conflict_witness_sound` | A successful raw witness replay whose target formula is true: the input decodes to that document and the model refutes conflict-freedom and `SoftConflictFree`, classified. |
| `Wire.soft_wire_acceptance` | A successful raw entailment replay with an accepted certificate: the input decodes to that document, the conclusion holds under the direct soft semantics, and over every coherent base given conflict-freedom. |
| `Admission.admitDocument_spec`, `Admission.soft_wire_report_consequence` | A successful soft admission decodes from its raw source, binds every certificate to the regenerated `E′`, admits every node (W2 provenance, exact regenerated layer, profile or soft leaf), and its root follows from `background′ ++ elaborate T′` and the remaining assumptions. |
| `Run.soft_wire_acceptance`, `Run.runAdmission_sound` | A successful public `admission` answer on the soft path is exactly the encoding of a checked admission with recomputed bindings (`SoftAdmissionAnswer`). |

The remaining theorems are helper lemmas (list and rank-closure facts, preds, substitution,
substructure embedding, route plumbing), audited with the same allowlist.

## Statement deviations (all recorded here for the reviewers)

1. `WellFormedSoft` lives in `Soften.lean`, not `Tree.lean`: its last step is W1's
   `validate` on `soften D`.
2. `hard_over_soft_base` writes `φ°` as `circ D φ := subst (soften D).T (size (soften D)) φ`
   and the conjunction as `VE.Formula.and (circ D _) (circ D _)`.
3. `cone_independent`, `hard_never_weighed_global` and `authority_independent` take
   `p ∈ VE.Norms.regulatedNames D.base.T` (`D.T` is a `SoftTree`); the hypothesis is unused.
4. `coh_rank_valid` takes `hB : B.Admissible (envAt (soften D) 0)`: "valid" means true in
   every structure admissible for `E′_base`, as `VE.Entails` does. Without it an
   uninterpreted constant can make substituted atoms and their meanings disagree.
5. `weighing_point_sound` states the tuple typing as `TupleTyped Mo.asStructure (actSorts D M) vs`
   and the witness formula with `circ`.
6. `SoftConflictFree` is universe-polymorphic; the wire theorems use universe 0, as W1's do.
7. `hard_never_weighed` (ii) uses `sameStrictCore`: same `E`, literals, regulated,
   definitions and `nodes.map coreNode` (rank, exception, `hard` and default switches erased).
8. `rankHeight` is computed by `heightR` with fuel `ranks.length` (the longest ascending
   `outranks⁺` chain; stable at that fuel, `heightR_stable`).
9. `soft_route_intended` is the conflict-freedom-free half of `soft_route_acceptance`
   (W1 has `norms_route_intended`), used by `Wire.soft_wire_acceptance`.

## The `ve_soft_norms_route` cases (for the Python harness)

Every case is `{"id", "kind", "environment", "norms", ...}` with a `ve.core@0.2` environment
whose sorted profiles contain `soft-norms@0` and `norms@0`, an optional vocabulary `soft`
block (3.1) and optional `instruction_of` on predicates; `norms` is the array of soft norm
objects (3.2). Case kinds and outputs are listed in `Run.lean` (9.4): `soft-elaborate`,
`soft-pairs`, `soft-conflict` (packages or witness), `soft-certificate`, `admission`. Cases
without a soft construct delegate to `ve_norms_route` behaviour unchanged.

## Wire choices Python (item 2) must match, or report back

These are the Lean executable's current choices where the spec leaves bytes open:

* **No `null` on the Lean wire.** The frozen restricted JSON parser (`VE/Json.lean`) rejects
  `null`; `exception.decided_by: null` must be sent as an absent key (Lean reads absence as
  "inherit"), and `rank: null`/`exception: null` likewise.
* Soft block: `outranking` (`{"mode", "decided_by"?}`) is required when the block is present;
  `parties`, `ranks`, `outranks`, `ties`, `exception_decider` are optional (default empty).
* Decision predicate entries in `E′` JSON: `{"arguments": <sorts>, "description": "soft-norms decision"}`,
  appended to the vocabulary's predicates in `decisions` order (excepted, then switches, then
  `outweighs`).
* `E′_base` JSON (inner binding of conflict and classification packages): W1's base
  environment of the environment stripped of `soft-norms@0`, the `soft` block and every
  `instruction_of`, plus the decision entries; profiles without `norms@0`/`soft-norms@0`.
* `E′` JSON (entailment and admission certificates): the canonical source environment plus the
  decision entries, original profiles.
* Soft document hash: domain `ve-soft-norms-<identity version>\n` over
  `{"environment_id", "document": [canonical norm objects]}`, the canonical object omitting
  `mode: "strict"`, `alterable: []`, `hard: false` and absent `rank`/`exception`.
* Labels: `soft:exception:<rule>:sufficient|necessary:<i>`, `soft:coherence:<a>,<b>` (names
  sorted); classification packages use the coherence label as `target`.
* `conditional_on` is conservative on `soft-conflict`/`soft-certificate`/`soft-elaborate`:
  every coherence conjunct whose pair is not comparable (DISJOINT discharge is reported by
  `soft-pairs`, which needs the classification evidence). On `admission` it is the open
  coherence labels actually used as report leaves.
* New diagnostic texts the spec leaves open: `InvalidInput: invalid soft name <x>` (`__` in a
  rank, party or regulated name, `soft__` prefix on any declared predicate),
  `InvalidInput: invalid soft block`, `InvalidInput: invalid soft fields for environment`.

## Status and what is not claimed

* Proved: every theorem of spec 9.2 and 9.3 as listed above (with the deviations recorded),
  and the three wire theorems of 9.3 plus `Run.soft_wire_acceptance`.
* Tested: `tests/test_soft_norms_lean.py` drives the executable on the item-1 fixtures
  α, γ, δ, ε, η, θ, κ, λ, μ, ν, ξ, π, ρ, σ, υ (outcomes read off the regenerated `T′`
  premises with the Python evaluator, diagnostics, witnesses, pair classification, W1
  delegation).
* Not done here (handoffs): the Python/Lean differential on generated soft trees and
  byte-for-byte agreement of the regenerated outputs with Python (needs item 2); certificate
  replay against Python-produced packages; the `Overlap`, `override_cycles` and
  `DualGuardCycle` English report lines (Python's report layer); W2 *unit* contents that
  mention decision predicates (units are decoded over `E`; graph nodes over `E′`).
* Not claimed, as in the spec (9.5): completeness of the classification or of the conflict
  check outside norms.md 7 on `T′`; anything about the English surface; that
  `IntendedSoftAt` matches an author's intent; anything about deciders; override cycles
  beyond the determinacy of `ValueSoft`; enumeration completeness.
