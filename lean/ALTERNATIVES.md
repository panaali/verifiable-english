# Alternatives in Lean (`lean/VE/Alternatives/*`)

Specification: [docs/spec/alternatives.md](../docs/spec/alternatives.md) section 7 (draft 3) and
[docs/spec/causation-PLAN.md](../docs/spec/causation-PLAN.md) item 2. This file lists every
definition the statement review reads and every theorem in plain words. `lean/audit.py` audits
every theorem: no `sorry`, only `propext`, `Classical.choice` and `Quot.sound`. No frozen P0 file,
no `lean/VE/Norms/*` and no `lean/VE/Route/*` source changed (`python3 VE/Route/frozen.py`);
`VE/Audit.lean` gained imports and audit entries only, and `lakefile.toml` gained the
`ve_alternatives_route` target (root `AlternativesMain.lean`) without changing existing targets.

## Files

| File | Contents |
|---|---|
| `Decl.lean` | `Outcomes`, `Fulfilment`, `AltEnv`, `AltDoc`, `Row`; the four profile bodies (`avoidableF`, `unavoidableF`, `allowsF`, `preventsF`) with fixed argument orders; `extEnv`; `inline` (W1's capture-avoiding `inst`), `inlineTree`, `withDefinitions`; `WellFormedAlt` with the diagnostics of 6 (`checkBlock`, `checkProfileTyping`, W1's `validate` on the inlined tree, `checkFulfilments`, `Γ_base` typing) |
| `Inline.lean` | `AltValid` (the facts the proofs use, from `WellFormedAlt`); `alternatives_wellFormed`, `inlineTree_shape`, `inline_base`, `inline_faithful` |
| `Background.lean` | the slot premises (`ownPremise`, `oneTakenPremise`, `oneInactionPremise`, `proximatePremise`, `altPremises`), `tableComplete`, `backgroundBaseAlt`, `backgroundAlt`, `BaseAdmissibleAlt`, `PrefixAdmissibleAlt`, `AltConflictFree`, `altConflictFreeCheck`, `backgroundValidAlt`, `extendAvailable`, `oldEnv`; ownership, monotonicity, conservativity and the conflict check |
| `Route.lean` | the route restated over `PrefixAdmissibleAlt`: W1's frozen layers of the inlined document composed with the frozen `Layer.comp` (`altRoute`), its Background theorems, acceptance and countermodel |
| `Followable.lean` | `oBase`, `performedF`, `fulfilF`, `clearF`, `followableF`, `notFollowableF`, `allFollowable`; `TypedChooser`, `Avail`, `ClearIn`, `FollowableIn`; both soundness theorems |
| `Validate.lean` | `RowsConsistent`, `E1`–`E3`, `ExistenceFacts`, the Boolean gate `altModelChecks`, `validateAlternatives` (texts of 6), `scenarioConflict`, the untrusted `diagnose` |
| `Examples.lean` | build-time `#guard` regressions on the 8.1 fixture shapes (see below) |
| `Wire.lean` | profile gate, the W1 view (block stripped), strict block decoder, verbalisations, base units and the regenerated `table_complete`, `decodeAltSource`, `alt-elaborate` outputs |
| `Replay.lean` | source-bound conflict, followability, dilemma and entailment packages and the wire theorems |
| `Run.lean`, `../AlternativesMain.lean` | the `ve_alternatives_route` executable |

## Conventions

* Argument orders are fixed once (7): `avoidable`, `unavoidable` take `(harm, chooser)`; `allows`,
  `prevents` take `(action, harm)`; `clear` takes `(chooser, action)`; `followable` takes
  `(chooser)`. Every generated formula's context is its argument list reversed and it is
  evaluated at `tupleVal` of its arguments in argument order.
* Carrier transport: expansion-level statements are over `S` and `restrictAll (inlineTree A).T S`
  (same carrier); `extendAvailable` extends `S` on its own carrier; a finite witness appears only
  as `M.asStructure`.
* `O_p°` is W1's `outcomeBase` of the inlined document, instantiated at the action or chooser by
  `inst`; fulfilment bodies are base formulas typed over `(action :: remaining sorts).reverse`.
* Premise order on the route: `backgroundAlt A = background (inlineTree A) ++ altPremises A`
  (definitions, literals, profile, then the slot, 11.15), then the layer premises, then `Γ`.

## Theorems in plain words

Names have prefix `VE.Alternatives.`.

| Theorem | Statement in plain words |
|---|---|
| `alternatives_wellFormed` | A well-formed alternatives document inlines to a well-formed W1 document. |
| `inlineTree_shape` | Inlining keeps the environment, literals and regulated declarations and replaces exactly the guards and carve-outs by their inlined forms. |
| `inline_base` | An inlined formula is typed over `E` and mentions no profile word. |
| `inline_faithful` | On every structure admissible for `E` and typed valuation, an inlined formula is true iff the original is true when the profile words are interpreted by their bodies. |
| `owner_unique` | Under the slot premises an action is available to at most one chooser. |
| `alternative_monotone` | On a well-formed block, adding available alternatives on the same carrier never removes avoidability, an `allows` or a `prevents` (nothing is claimed for `clear`). |
| `alternatives_conservative` | For premises and a conclusion over `oldEnv` (no role predicate), consequence over `BaseAdmissibleAlt` equals consequence over W1's `BaseAdmissible` (the empty-relation expansion). |
| `alt_conflict_free` | Accepted certificates for every W1 conflict target of the inlined document over `Background_baseAlt` (or W1's `Background_base` alone) give `AltConflictFree`. |
| `alt_conflict_witness_sound` | A typed finite base witness passing `backgroundValidAlt` at which a conflict formula evaluates true refutes conflict-freedom there, unique expansion there and `AltConflictFree`. |
| `clear_denote`, `followable_denote` | On a document expansion `S`, `clear°` and `∀r. followable°(r)` in the base restriction denote `ClearIn` and `FollowableIn` in `S`. |
| `followable_sound` | FOLLOWABLE: an accepted certificate for `Background_baseAlt ++ Γ_base ⊢ ∀r. followable°(r)` gives `FollowableIn` in every document expansion of every `BaseAdmissibleAlt` structure satisfying `Γ_base`. |
| `dilemma_witness_sound` | DILEMMA: a typed chooser of a valid finite witness (passing `backgroundValidAlt` and `Γ_base`) at which `¬followable°` evaluates true refutes the document-wide claim. |
| `dilemma_expansion` | On a document expansion whose base restriction satisfies the slot premises, a typed chooser at which `¬followable°` holds has no clear alternative. |
| `followable_eval_iff_denote` | Finite evaluation of `¬followable°` agrees with its denotation. |
| `validate_sound` | Successful validation (with the Bridge decoder's `M.Valid`) gives `backgroundValidAlt`, `Γ_base` by evaluation, `BaseAdmissibleAlt` and the rows and existence facts. |
| `scenarioConflict_sound` | A conflict formula true at a typed tuple of a validated scenario refutes conflict-freedom of the model and `AltConflictFree`. |
| `alt_prefix_satisfaction`, `alt_conflictFree_prefix` | W1's prefix characterisation and local test, over the extended base. |
| `altRoute`, `alt_route_backgroundSound`, `alt_route_backgroundComplete` | The composed frozen P0 route of the inlined document with `BaseAdmissibleAlt` as input admissibility; `backgroundAlt` is sound and complete for its output. |
| `alt_route_acceptance`, `alt_route_countermodel` | W1's route acceptance and countermodel theorems restated with `BaseAdmissibleAlt` and `backgroundAlt`. |
| `Replay.alternatives_wire_conflict_sound` | A raw conflict-package replay with every target accepted: the input decodes to exactly that well-formed source, which is `AltConflictFree`. |
| `Replay.alternatives_wire_followable_sound` | A raw followability replay (CONFLICT-FREE packages and an accepted followability package): decoding, well-formedness, `AltConflictFree` and the FOLLOWABLE claim of `followable_sound`. |
| `Replay.alternatives_wire_dilemma_sound` | A raw dilemma replay: decoding, well-formedness, `AltConflictFree`, successful validation of the witness with its rows, a typed chooser, `¬followable°` evaluated true, and the refutation of the document-wide claim. |
| `Replay.alternatives_wire_acceptance` | A raw entailment replay with an accepted certificate over `backgroundAlt ++ layer premises ++ premises`: the conclusion under the direct semantics with the slot premises, and, given `AltConflictFree` and base formulas, over every `BaseAdmissibleAlt` structure. |

The remaining theorems are helper lemmas (typing of the bodies and premises, denotation lemmas of
the profile words, the Boolean checks' soundness, list lemmas) audited with the same allowlist.

## Build-time regressions (`Examples.lean`)

Compiled `#guard` evaluations on the `asimov-v2` shapes of 8.1: well-formedness of every rule set
used; l6 `AlternativesSort: leads_to expects (action, harm)`; n `DependencyCycle`; the reserved,
performed and fulfilment diagnostics; scenario a (clear `pull`), b (A₀ clear `pull`; A₁ a valid
witness with `¬followable°`, NONE-PERMITTED; A₂ NONE-PERMITTED; B JOINTLY-UNDISCHARGEABLE), c
(`unavoidable`, both clear under {3, 7} and {3, 8}, UNDISCHARGEABLE under {3, 8⁻}), d (OVER-REQUIRED
under {1–6}, clear `shield`, `retreat` under {3, 6′}), e (NONE-PERMITTED), j (OVER-REQUIRED), o
(clear `act`, `rescue` versus `rescue`), s2 (scenario CONFLICT on `permitted` at `nothing`); and the
`InvalidModel` texts of l1–l4, m, p1, p2/p6 (with the regenerated `table_complete`) and h3.

## The `ve_alternatives_route` cases

Every case is `{"id", "kind", "environment", "norms", "units"?, ...}`: a `ve.core@0.2` environment
with `alternatives@0` and `norms@0` and the `alternatives` block (3.1), the norm objects of W1
(guards may use the profile words) and the document's active base units `{"label", "ast"}`.
Scenario models are Bridge models of the base vocabulary with signed `outcomes` rows naming
entities of the action and harm domains; a missing `leads_to` table is the set of positive rows.

| Kind | Extra input | Output |
|---|---|---|
| `alt-elaborate` | none | `legend` (2.3), `inlined`, `alternatives` (labelled slot premises), `base_premises`, `followable` (`ast`, `followable`, `clear`), existentially closed `profile_exists` probes generated from the four profile bodies, `unmapped_obligations`, and W1's `order`, `background`, `premises`, `conflict_targets`, `fragment` |
| `alt-validate` | `scenario` (`model`, `outcomes`), optional `packages` | `InvalidModel(alternatives): …`; else a CONFLICT witness (`target`, `tuple`) if a conflict formula holds; else `model_id`, per-chooser reports and the status text of 5.2 |
| `alt-conflict` | `packages`, or `witness` (`model`, `outcomes`, `target`, `tuple`) | `CONFLICT-FREE` / `CONFLICT` / `UNKNOWN` |
| `alt-followable` | `packages` and `package`, or `packages` and `witness` (`model`, `outcomes`, `chooser`) | `FOLLOWABLE` / `DILEMMA` (with the diagnosis) / `UNKNOWN` / `not computed` |
| `alt-certificate` | `premises`, `conclusion`, `certificate` | `valid`, `background`, `layers`, `conditional_on` |

Cases without the profile, the block or an `alt-*` kind are delegated unchanged to
`VE.Norms.Run`.

End-to-end runs: `tests/test_alternatives_three_way.py` binds Python W1 prover certificates to the
alternatives source and replays conflict packages as CONFLICT-FREE for the A₁, B and j rule sets.
Their witnesses replay as DILEMMA with NONE-PERMITTED, JOINTLY-UNDISCHARGEABLE and OVER-REQUIRED;
a rule-free document's followability certificate replays as FOLLOWABLE. Changing the block's decider
invalidates the packages. Earlier local runs also covered {3, 7, 9} and {3, 5, 7, 9}.
The Python search found no
followability certificate for b′(A) within 50,000 steps (proof search is outside this item).

`tests/test_alternatives_three_way.py` checks the a, b, b′(A, A5), c, d, e, f, g, h, j, l5, o, t and u scenario shapes:
Lean validates each model and reports its clear actions; Python and Rust evaluate
Lean's closed followability and four profile probes over the same base model.
The s2, b′(A⁻) and b′(A⁻5) conflict targets are also compared three ways.
The p1, p2 and p6 outcome-table cases check signed-row completeness and the
document's `table_complete` premise; p2's derived formulas are compared across
all three evaluators.

## Status, deviations from 7.2 and what is not claimed

* Proved as stated: every theorem of 7.2 except those listed next, with the spec's hypotheses.
* `validate_sound` takes `M.Valid (envAt (inlineTree A) 0)` as a hypothesis. A `FiniteModel`'s
  relation table is a function and cannot be enumerated, so structural admissibility is
  established by the Bridge decoder (`decodeScenario`, as W1's `witnessFrom`), and the dilemma
  wire theorem uses that decoded fact. `validateAlternatives` additionally needs an `EntityName`
  instance to render entity names in its failure texts; success does not depend on it.
* The wire statements decode from `(j.getObjValD "environment") (j.getObjValD "norms")
  (j.getObjValD "units")` (the W1 case shape the Python transport already sends), not from a
  single `document` field.
* Not implemented: W2 `admission` with the block and `Run.alternatives_wire_acceptance`
  (`AltAdmissionAnswer`); the per-alternative rule reasons of the diagnosis rendering; English
  renderings of fulfilment bodies other than `avoids` in the legend (the act phrase is quoted); `conditional_on` of a FOLLOWABLE answer lists every `Γ_base` label rather than the
  ones the certificate uses.
* A conflict target's certificate is accepted over `Background_baseAlt` or, as 4.5 allows, over
  W1's `Background_base` alone (`targetAccepted`; both bindings are tried on replay).
* The Lean diagnostic order follows 6 (the block, the rules, W1 on the inlined tree,
  fulfilments, `Γ_base`); Python's block-shape check now follows the same role-sort
  order, including fixture l6's `AlternativesSort: leads_to expects (action, harm)`.
* Nothing is claimed about the diagnosis, its minimality, the existence facts beyond
  `validate_sound`, the English surface, or the truth of the declared table (7.4).
