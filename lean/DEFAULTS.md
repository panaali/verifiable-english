# Answers that hold unless an exception applies, in Lean (`lean/VE/Defaults/*`)

Specification: [docs/spec/defeasible.md](../docs/spec/defeasible.md) sections 7.1 and 7.2 (draft 3) and
[docs/spec/defeasible-PLAN.md](../docs/spec/defeasible-PLAN.md) batch DF-1a. This file lists the files and every
definition and theorem built so far, in plain words. `lean/audit.py` audits every theorem: no `sorry`, only
`propext`, `Classical.choice` and `Quot.sound`. The service mode `norm-defaults` answers the four kinds on the soft and
rights branches, through one row of the layered kind table (`Route.lean`); no answer of another kind changes.

A default answer is conditional on the listed assumptions. Nothing here says that the situations it ranges over are
those with the fewest exceptions; that is DF-2's theorem, not proved.

## Files

| File | Contents |
|---|---|
| `Premises.lean` | `Dflt_T` (`dfltOf`, `dfltLabelled`), `defaultX`, diagnostics 2 to 4 (`decisionFree`, `questionDiag`, `limitDiag`), the gate (`DefaultCoherent`, `pairChecks`, `defaultCoherenceCheck`, `collisionCheck`), the collision DE7 shows (`collisionTuple`), the basis (`assumptionsOf`, `Basis`, `basisOf`), the form (`Form`, `followsForm`) and the deciders (`decidersOf`, `giveWayDeciders`) |
| `Examples.lean` | the fixtures of spec 8.1, 8.2 and 8.4 that these definitions decide (DF-α to DF-ζ, DF-γ′, DF-η, DF-ι, DF-κ, DF-ω, DF-σ), as `#guard`s on documents decoded by `decodeSoftU` |
| `Wire.lean` | the view of a decoded document (`viewOf`, diagnostics 7, 1, 2, 6 and 4) and the kinds `defaults-elaborate`, `defaults-coherence`, `defaults-certificate` and `defaults-model` (`defaultsCase`) |
| `WireExamples.lean` | the wire answers of DF-θ, DF-α to DF-ω, DF-γb, DF-γ2 and DF-γ3, through `viewOf` and `defaultsCase` on JSON requests |
| `Route.lean` | the layered kind table with the four kinds as one row (`defaultsRows`, needing the soft pack), and the branches' runner `runLayered` |
| `RouteExamples.lean` | the four kinds through the service mode, the pack, the routing's boundaries and the other kinds' answers unchanged |

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

- **`viewOf j`** (`Wire.lean`): the layered route's own decoder, then diagnostic 7 (the soft document and the extra
  premises are well formed), then **`viewRest`**: diagnostic 1 (`weighing@0`), 2 (a later pack's premise names a
  decision), 6 (two generated labels coincide) and 4. It returns the document with `R`, its premises after the soft
  pack's, and the facts the theorems need.
- **`replayCert`**, **`replayCoherence`**: what a request carries, checked against the view: the question's premises
  (diagnostic 3) and conclusion, a certificate bound to `defaultX`'s premise list (one that does not bind is absent),
  one optional certificate per colliding pair in the listed order (diagnostic 5; no list, `null` or `[]` sends none), a
  collision (refused when it names a rule the document does not declare), a model of `defaultX` and a strict
  countermodel.
- **`CertReplay.verdict`**: FOLLOWS only with the certificate, every pair's certificate and the model checked;
  otherwise UNKNOWN, with **`CertReplay.reason`** in this order: a checked collision, the gate, the model, the
  certificate. With FOLLOWS the answer adds the basis, the form and the kept assumptions.
- **`CoherenceReplay.verdict`**: COHERENT (every pair's certificate checks), COLLISION (the collision checks) or
  UNKNOWN; **`CoherenceReplay.pairs`**: each pair resolved, collision or unknown. With COLLISION the answer adds the
  pair, the tuple `collisionTuple` finds, `giveWayDeciders` and the situation (**`situationJson`**: every unsaid table of
  the checked filled situation, as a report line's witness shows it).
- **`elaborateRows`**: `Dflt_T` with its labels and the colliding pairs; **`defaultsCase`** answers the four kinds and
  nothing else.
- **`replayModel`**: the question and a model of `defaultX`; DOES-NOT-FOLLOW when the model checks as a countermodel,
  otherwise UNKNOWN; with DOES-NOT-FOLLOW the situation and **`forcedAt`**: the exceptions that hold there, each with
  the first stated condition that holds at its tuple.
- **`defaultsRows`** (`Route.lean`): the four kinds, each needing the soft pack, answered by `defaultsCase` on `viewOf`;
  **`layeredRows`** is today's four rows and this one; **`runLayered`** decodes the source and dispatches over them.

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
- `decodeLayered_soften`, `viewOf_layered`: the view's document is the layered decoder's own, with `U` built on the
  softened document.
- `defaults_follows_gated`, `defaults_certificate_sound`: FOLLOWS has its certificate, gate and model checked; it gives
  the entailment from the document's premises and the kept assumptions, the gate, a situation where the premises hold
  with no exception, and, with basis `strict`, the entailment from the document's own premises, with basis `needs`, a
  countermodel of them.
- `default_exception`, `forcedAt_sound`, `defaults_model_sound`: a well-formed soft document's default rules all have
  an exception; each `forced` entry names a default rule, a stated condition that holds at its tuple and the exception
  there; DOES-NOT-FOLLOW gives an admissible situation where the premises hold and the conclusion does not, and with
  `forced = []` no rule's exception holds there.
- `elaborateRows_eq`: the elaborate rows are `Dflt_T` and the colliding pairs.
- `defaults_coherence_sound`: COHERENT gives the gate, COLLISION refutes it, and each resolved pair's coherence premise
  holds on every admissible base.
- `coherence_collision_shown`: a pair shown `collision`, or a `collision` member, only with a collision that checks.
- `coherence_collision_named`: a pair shown `collision` is the pair the collision names, by both rules, and the
  `collision` member's tuple and deciders are those of that pair.
- `defaultsCase_other`: a kind that does not start with `defaults-` gets no answer here.
- `layeredKindCase_other` (`Route.lean`): a kind outside the row is dispatched by today's rows, as before.

## Deviations

- `bindAll_wellFormed_inv` moved unchanged from `Norms/FlaggedSpec.lean` (layer 4) to `Norms/Elaborate.lean`, beside
  `bindAll_wellFormed`, so that `dflt_wellFormed` can use it at layer 2.
- `SoftNorms/RankProof.lean`'s helper lemmas take the substitution table, the tree and the fuel as parameters, so that
  `cohU_rank_valid` reuses soft's argument without a copy; `coh_rank_valid_unconditional` and the approved
  `coh_rank_valid` keep their statements.
- The row reads the view through `viewOf`, so a `defaults-*` case decodes its source twice (`runLayered`, then
  `viewOf`): `viewOf`'s approved text decodes the request itself.
