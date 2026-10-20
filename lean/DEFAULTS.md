# Answers that hold unless an exception applies, in Lean (`lean/VE/Defaults/*`)

Specification: [docs/spec/defeasible.md](../docs/spec/defeasible.md) section 7.1 (draft 3) and
[docs/spec/defeasible-PLAN.md](../docs/spec/defeasible-PLAN.md) batch DF-1a. This file lists the files and every
definition and theorem built so far, in plain words. `lean/audit.py` audits every theorem: no `sorry`, only
`propext`, `Classical.choice` and `Quot.sound`. No answer kind exists yet: nothing here is reachable from the service,
so no existing answer changes.

A default answer is conditional on the listed assumptions. Nothing here says that the situations it ranges over are
those with the fewest exceptions; that is DF-2's theorem, not proved.

## Files

| File | Contents |
|---|---|
| `Premises.lean` | `Dflt_T` (`dfltOf`, `dfltLabelled`), `defaultX`, diagnostics 2 to 4 (`decisionFree`, `questionDiag`, `limitDiag`), the gate (`DefaultCoherent`, `pairChecks`, `defaultCoherenceCheck`, `collisionCheck`), the collision DE7 shows (`collisionTuple`), the basis (`assumptionsOf`, `Basis`, `basisOf`), the form (`Form`, `followsForm`) and the deciders (`decidersOf`, `giveWayDeciders`) |
| `Examples.lean` | the fixtures of spec 8.1, 8.2 and 8.4 that these definitions decide (DF-α to DF-ζ, DF-γ′, DF-η, DF-ι, DF-κ, DF-ω, DF-σ), as `#guard`s on documents decoded by `decodeSoftU` |

## Definitions

- **`dfltOf D N`, `dfltLabelled D`.** For each default rule, in rule order: "the rule's exception holds only where one
  of its stated sufficient conditions holds" (with none stated: "it holds nowhere"), labelled
  `default:exception:<rule>`; then for each party that may turn the rule off, "that party has not turned it off",
  labelled `default:switch:<rule>:<party>`. Then, under the holistic flag, for each `outweighs` decision, "the lower
  consideration does not outweigh the higher one on this act", labelled `default:ranking:<low>:<high>:<act>`.
- **`defaultX D X`** is the document's own premises followed by these; **`withoutDefaults D X`** reads each of them
  as `⊤`.
- **`decisionFree D φ`**: `φ` names no exception, switch or `outweighs` decision (diagnostic 2 reads it on the
  other packs' premises). **`questionDiag D Γ`** (diagnostic 3): the first question premise predicate, in premise
  order, that is a decision or a regulated outcome, described in words by **`whatOf`** ("whether rule r1's exception
  applies", "the outcome x_permitted"). **`limitDiag D`** (diagnostic 4): the first `Dflt_T` premise outside soft's
  node and depth limits.
- **`DefaultCoherent U D R`**, the gate: on every base admissible with the exception premises, the other packs'
  premises `R` and `Dflt_T`, no two colliding rules both select. **`defaultCoherenceCheck`** checks one certificate
  per colliding pair, in pair order; **`collisionCheck`** checks a finite base and filling where they do.
- **`selU U D K`**: rule `K`'s selection on the filled tree, as the coherence premise builds it.
  **`collisionTuple`**: the first tuple of a checked collision where both rules select, the one DE7 shows.
- **`assumptionsOf`**: the `Dflt_T` labels a certificate needs, found by readings' `usedLabels` (a label is dropped
  when the certificate still checks with its premise read as `⊤`). The list is enough for this certificate; another
  certificate may need fewer.
- **`basisOf as sc`**: `strict` when no label is kept; `needs` when some are and a strict countermodel checked;
  `unsettled` otherwise.
- **`followsForm D as`**: `short` exactly when every kept label is a rule's exception with no stated condition;
  otherwise `long` (a switch, a ranking or a stated condition is an assumption "Unless an exception applies" does not
  state).
- **`decidersOf D`**: DE5's deciders, each once, in rule order: each default rule's exception decider and switch
  parties, then the outranking decider when a ranking decision exists. **`giveWayDeciders D P Q`**: DE7's deciders,
  one when both rules' exceptions have the same decider, otherwise both, in pair order; `unstated` where none is named.

## Theorems

- `dflt_wellFormed`: every premise of `Dflt_T` is a closed formula typed over the filled base vocabulary.
- `entailsX_mono`, `strict_of_withoutDefaults`: adding premises or `⊤` keeps an entailment; what follows with `Dflt_T`
  read as `⊤` follows from the document's own premises.
- `pairChecks_sound`, `defaultCoherenceCheck_sound`: a checked pair certificate makes that pair's coherence premise
  hold on every admissible base; all of them checked give the gate.
- `collision_sound`: a checked collision refutes the gate. With neither check the gate is unknown.
- `questionDiag_none`: without diagnostic 3, no question premise names a decision or a regulated outcome.
- `cohPremiseU_selU`: the coherence premise is "not both `selU`", over the pair's act sorts.
- `collisionTuple_some`: a checked collision always has a tuple to show.
- `cohU_rank_valid`: a ranked (comparable) colliding pair's coherence premise holds in every structure. It is soft's
  `coh_rank_valid_unconditional` carried to the filled tree: both read only each rule's own guard and carve-outs, so
  soft's argument holds for any substitution table (`VE.SoftNorms.coh_rank_valid_with`).
- `collision_unranked`: a checked collision's pair is unranked (DE7's "The text ranks neither above the other").
- `premisesX_split`: RD-9's premise list for `defaultX` is the document's part, then `Dflt_T`, then the rest.
- `assumptions_sound`: a checked certificate gives the entailment from the document's premises and the kept
  assumptions alone.
- `basis_strict_sound`: `strict` means the conclusion follows from the document's own premises.
- `basis_needs_sound`: a strict countermodel checked by RD-9's `xModelOk` (which requires local conflict freedom)
  shows that the conclusion does not follow from them (DF-σ shows why `modelCheckX` alone is not enough).
- `followsForm_short`: with the short form, every kept label's premise says only "this rule's exception holds
  nowhere".
- `atom_wf` (helper): a declared atom is typed by its own sorts.

## Deviations

- `bindAll_wellFormed_inv` moved unchanged from `Norms/FlaggedSpec.lean` (layer 4) to `Norms/Elaborate.lean`, beside
  `bindAll_wellFormed`, so that `dflt_wellFormed` can use it at layer 2.
- `SoftNorms/RankProof.lean`'s helper lemmas take the substitution table, the tree and the fuel as parameters, so that
  `cohU_rank_valid` reuses soft's argument without a copy; `coh_rank_valid_unconditional` and the approved
  `coh_rank_valid` keep their statements.
- Not yet built (df-1ac): all of `Wire.lean` (spec 7.2), the four kinds as one row of PK-1's kind table, their
  response shapes and encoder theorems.
