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
| `Premises.lean` | `Dflt_T` (`dfltOf`, `dfltLabelled`), `defaultX`, the basis (`assumptionsOf`, `Basis`, `basisOf`) and the form (`Form`, `followsForm`) |
| `Examples.lean` | the fixtures of spec 8.1 and 8.2 that these definitions decide (DF-α to DF-ζ, DF-ι, DF-κ, DF-σ), as `#guard`s on documents decoded by `decodeSoftU` |

## Definitions

- **`dfltOf D N`, `dfltLabelled D`.** For each default rule, in rule order: "the rule's exception holds only where one
  of its stated sufficient conditions holds" (with none stated: "it holds nowhere"), labelled
  `default:exception:<rule>`; then for each party that may turn the rule off, "that party has not turned it off",
  labelled `default:switch:<rule>:<party>`. Then, under the holistic flag, for each `outweighs` decision, "the lower
  consideration does not outweigh the higher one on this act", labelled `default:ranking:<low>:<high>:<act>`.
- **`defaultX D X`** is the document's own premises followed by these; **`withoutDefaults D X`** reads each of them
  as `⊤`.
- **`assumptionsOf`**: the `Dflt_T` labels a certificate needs, found by readings' `usedLabels` (a label is dropped
  when the certificate still checks with its premise read as `⊤`). The list is enough for this certificate; another
  certificate may need fewer.
- **`basisOf as sc`**: `strict` when no label is kept; `needs` when some are and a strict countermodel checked;
  `unsettled` otherwise.
- **`followsForm D as`**: `short` exactly when every kept label is a rule's exception with no stated condition;
  otherwise `long` (a switch, a ranking or a stated condition is an assumption "Unless an exception applies" does not
  state).

## Theorems

- `dflt_wellFormed`: every premise of `Dflt_T` is a closed formula typed over the filled base vocabulary.
- `entailsX_mono`, `strict_of_withoutDefaults`: adding premises or `⊤` keeps an entailment; what follows with `Dflt_T`
  read as `⊤` follows from the document's own premises.
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
- Not yet built (df-1ab): the gate (`DefaultCoherent`, `pairChecks`, `defaultCoherenceCheck`, `collisionCheck` and
  their soundness theorems, cut for size and kept on local branch `wip/df-1ab-gate`), `decisionFree`, `questionDiag`,
  `limitDiag`, `selU`, `collisionTuple` and its theorem, `cohU_rank_valid`, `collision_unranked`, `decidersOf`,
  `giveWayDeciders`, and all of `Wire.lean` (spec 7.2).
