# Answers that hold unless an exception applies: statement spec (DF-S)

> Status: **draft 3** (2026-10-14), branch `research/defeasible-p1`, the item-1 statement spec of
> [defeasible-PLAN.md](defeasible-PLAN.md) draft 4 (batch DF-S, done: the diff-only re-check of draft 2 returned PASS,
> `manage-agents/defeasible-p3ver1.final.md`). Draft 3 applies phase 1's results
> ([docs/research/defeasible-phase1.md](../research/defeasible-phase1.md)) to the text around the statements. **No
> Lean statement, definition, English row, diagnostic or computed fixture value changed**, so the stub
> `lean/SpecStubs_defeasible.lean` (untracked, never committed; it is in the `design/defeasible` worktree,
> `ve-design-defeasible`, not in this one) was not edited or re-run. The elaboration and computation records below are
> draft 2's and still hold.
>
> **Changes in this draft (3).**
> 1. 8.1 DF-λ: through `ve document` on `main` the fixture is refused at load until RD-9 SC-8 (phase 1, DF-0.4); the
>    computed value is on the decoders and unchanged. The plan's spelling `instructs_via_system_prompt` is the same
>    rule.
> 2. 8.7 P-1: the pilot number's "0" is DF-0.3's baseline, deferred until `rd-9/integrate` is on `main` and recorded
>    before DF-1b merges.
> 3. 6: no specificity suggestion either, until DF-E3's re-run meets its bar (phase 1: UNKNOWN).
> 4. 10: plan section 11's seven issues are decided (DRI DF1 to DF7); new item 4 lists phase 1's deferred items that
>    touch this spec.
>
> Draft 2 (`632bc4ed`, branch `design/defeasible`, for plan draft 3) applied the statement review's ruling
> (`manage-agents/debates/defeasible-spec/DRI-RULING.md`: verdict FIX, design kept; 13 agreed corrections and 3
> disputed points ruled). Section 2.2 maps each ruling item to the places it changed
> (R1 to R16). Nothing else changed.
>
> **Elaborated.** Every Lean block in section 7 was type-checked in an untracked stub,
> `lean/SpecStubs_defeasible.lean`, run from the `design/defeasible` worktree as
> `lake -d /home/seyran/code/ve-rd-9-int/lean env lean lean/SpecStubs_defeasible.lean`, against the build of
> `rd-9/integrate`, because RD-9's names (`EntailsX`, `LayeredU`, `xModelOk`, `CounterX`, `sdSem`, the fold) are not
> on `main` (`f98183bf`). That checkout is at `ecb81c32`, whose `lean/` is identical to `fbb81599`'s (the commit draft
> 1 used; `git diff fbb81599 ecb81c32 -- lean` is empty). The `design/defeasible` worktree has no Lean build of its own, and
> `lake env lean` does not build. Draft 2's run reported no error. Its only warnings were `declaration uses 'sorry'`,
> for bodies and proofs that a build batch writes. The stub is not committed and no `sorry` is committed. It stays
> untracked in that worktree for the reviewers to re-run. WG-6's zone names and WG-1's `WeighDoc` are not on any built
> branch. Their reviewed signatures (weighing-PLAN 3.4, draft 5) were copied into the stub so that DF-5's and DF-6's
> statements elaborate against them. Section 7 marks those blocks.
>
> **Computed.** Every fixture value in section 8 is an `#eval` in the stub, run on the real decoders
> (`decodeSoftU`, `situationX`, `decodeFilling`) and on RD-9's checks (`modelCheckX`, `localFree`, `xModelOk`,
> `foldEntailment`, `foldConflict`). None was worked out by hand. Draft 2 re-ran every fixture, and recomputed the
> claims that rest on a model of `⊥` with the empty domain allowed (R1). Two kinds of value remain *derived*, and
> section 8 marks them: the certificate-dependent values (no prover runs in Lean), and the pilot rows on `CE4`, which
> DF-1b measures. No model was called. The diff-only re-check of draft 2 returned PASS. Next: DF-1a, once
> `rd-9/integrate` merges and PK-1 lands (plan draft 4, batch order).

## Change log

| Date | Draft | What |
|---|---|---|
| 2026-10-14 | 1 | First statement spec. Plan draft 2's statements were elaborated, and the 19 corrections in section 2 come from that run (the main one: `basis_needs_sound` as drafted is false, DF-σ). Every fixture of plan 4.1 was computed, with one added for each direction of every "exactly when" claim. New statements: `cone_minimal_iff` (until now a placeholder), `defaultZone_budget`, `default_conflict_is_gate`, `questionDiag_none`, `viewOf_layered` and the fallback `default_entails_minimal_of`. The stub proves 9 statements outright, and 3 more modulo `dflt_wellFormed` and `defaultCoherenceCheck_sound` (section 7.8). |
| 2026-10-14 | 2 | The statement review's ruling (FIX), item by item in section 2.2 (R1 to R16). New: `CoherenceReplay` and `defaults_coherence_sound`, `elaborateRows`, `forcedAt_sound`, `collisionTuple_some`, `cohU_rank_valid` and `collision_unranked`, `giveWayDeciders`, `viewOf` through `decodeLayered` with `decodeLayered_soften`, DF-3's wire theorems (`DVerdicts`), DF-5's `notSaid` and `noCompletion` soundness, `forcedAllOf` with `forcedAll_sound`, `defaultCompletion_below` and `forced_everywhere`, `zoneForm`, `decisionAtoms_none`. Deleted: `hsuff` and `noSufficientHolds`. English: DE4·u, DE7's decider sentences, DE8 with DE12, DE10 in three forms, DE13; "avoidable" defined. Fixtures: DF-γ recomputed with the empty domain, DF-γ′, DF-ω, F-DF1′, DF-δ's zone; seeded bugs corrected (sufficient condition: DF-β (i)). The stub now proves 12 statements outright (section 7.8). |
| 2026-10-14 | 3 | Phase 1's results, text only: DF-λ's CLI status (refused at load until RD-9 SC-8), P-1's baseline (DF-0.3, deferred), no specificity suggestion until DF-E3's re-run, plan section 11 decided (DF1 to DF7), section 10 item 4. No statement or computed value changed; the stub was not edited. |

## 1. Scope

This spec fixes what DF-1a, DF-2, DF-3, DF-5 and DF-6 build: every definition, the wording of every English row,
every diagnostic text, and the statement of every theorem. DF-4's English (DE9) is fixed here too. Its grammar row and
its all-derivations check belong to DF-4, in english-lean's catalogue. Proofs are the batches' work. Section 7.8 lists
what the stub already proves.

Three things are owned once. Lean owns every value named here: `Dflt_T`, the gate, the basis, the form, `forced`, the
diagnostics, the zone and the fold. Python relays and binds them (R8 of the DRI rulings). Python renders only the row
Lean selects.

## 2. Corrections

### 2.1 Draft 1: corrections to plan draft 2 found by elaboration

Plan draft 2's design stands. Everything the debate agreed is unchanged: the varied fillings (D15), the three-valued
basis, the non-vacuity conjunct, the FREE-only default fold, the two English forms and the full enumeration in DF-5.
The statements below differ from plan draft 2's text, and each row says why ("Draft 2" in this table is the plan's).
Plan draft 2's section 3 is superseded by section 7 of this spec. The plan's status line points here.

| # | Plan draft 2 | This spec | Why |
|---|---|---|---|
| C1 | `basis_needs_sound` assumed `(modelCheckX U X M F Γ φ) = (true, false)` | it assumes RD-9's `xModelOk U X [] Γ φ m false = true` (typing, `modelCheckX`, conclusion false, `localFree`) and concludes `CounterX U X Γ φ ∧ ¬ EntailsX.{0} U X Γ φ`. **Proved in the stub** | Draft 2's statement is **false**. At DF-σ (two strict rules on `x_required` of opposite sign) `modelCheckX` gives `(true, false)` for `∀a. ⊥` on the one-assistant situation. That situation has a conflict, so it has no expansion, and `EntailsX U X [] (∀a. ⊥)` holds (8.1, DF-σ). A countermodel needs local conflict freedom, as RD-9's `xModelOk` requires. |
| C2 | non-vacuity conjunct spelled out; `model` checked by `modelCheckX … φ := ⊤` | the conjunct is RD-9's `ConsistentX U (defaultX D X) Γ`, which is the same formula, and the model is checked by `xModelOk U (defaultX D X) [] Γ ⊥ m false` | It has C1's defect. Without `localFree` the checked situation can have no expansion, so it shows nothing. |
| C3 | `ModelReplay.ok` by `modelCheckX` | `xModelOk U (defaultX D X) [] Γ φ m false` | C1 again (`defaults_model_sound`). |
| C4 | `certChecks ps φ c` | `certChecks U ps φ c` | The tableau check needs the environment `envAt (fill U) (size (fill U))`, which is `acceptanceX`'s. |
| C5 | `assumptions_sound`, `basis_strict_sound` without `hD`, `hl`; `dflt_wellFormed` without `h` | `hD : WellFormedSoft D`, `hl : wellLabelled (dfltLabelled D)`; `dflt_wellFormed` takes `h : WellFormedU U` | `acceptanceX` needs every premise of `X ++ blank …` well formed, which comes from `dflt_wellFormed`, which needs `hD` and `h`. `usedLabels_sound` takes `hl`. |
| C6 | `defaultCoherenceCheck_sound` with `h`, `hU`, `hR` | only the check `hc` | As RD-9's `conflictFreeCheckX_sound`: the tableau's soundness needs no typing of the premises. |
| C7 | `collisionCheck … (vs)`; `collision_sound` without `valid` | no tuple in the check (Lean computes DE7's tuple, `collisionTuple`); `collision_sound` takes `valid : M.Valid (envAt U.D 0)`; the witness is a `SituationG` | `admissibleX_of_fill` needs `valid`. A tuple supplied by the request would be one more binding to check, while Lean can find it. |
| C8 | `DefaultsView` with `hX`, `hR`; `viewOf (L : LayeredU)`; `defaultsCase (L …)` | `DefaultsView` also carries `hU`, `hD`, `hXw`, `hl`; `viewOf (j : Json)` decodes as `decodeLayered` does (`viewOf_layered`); `defaultsCase (v : DefaultsView …)` | `LayeredU` records only `wfU`. `L.U.D = soften L.D` cannot be checked at run time (`Environment` holds functions and has no decidable equality), so the decoder must produce it, as RD-9's `choiceLayeredG` does. Draft 2 settles how (R12): `viewOf` calls `decodeLayered` itself, `hU` is the lemma `decodeLayered_soften`, and `hD`, `hXw` are Boolean checks. |
| C9 | `CertReplay` with Boolean fields described in comments; the soundness theorem quantified over `replayCert j = .ok x` | `CertReplay` holds the evidence (`cert`, `pairCerts`, `collision`, `model`, `strictModel`). Each verdict, basis, form and reason is a Lean function of it, and `defaults_certificate_sound` holds **for every value**. **Proved in the stub** modulo C5's two lemmas | `replayCert` then carries no proof obligation beyond decoding. A certificate that `bindCertX` refuses is decoded as absent (DF-κ). |
| C10 | D5 read through `decisionFree` | `questionDiag`: the first premise predicate that is a decision **or regulated**, and its text | `decisionFree` lets a regulated predicate through, but D5 refuses both (8.4). Draft 2's text "what rule n decides" names no rule when no rule is on the predicate, so the text is "the outcome p". |
| C11 | `dSem` with `sdSem N`, `choiceR N c` | `VE.Readings.Wire.sdSem` (its namespace on `rd-9/integrate`); `R = []` on the soft chain (`choiceX_softX`, proved); the FREE-only rule as the theorem `default_conflict_is_gate` (proved) | A default-fold CONFLICT beside a FREE strict fold is a failed gate, which makes DE7 per choice a theorem, not a convention. |
| C12 | DF-5: untyped binders; `cone_minimal_iff` a placeholder; DF-μ″ "r1 on plain p and r2 on plain q, colliding"; seeded bug "compare unsaid atoms: DF-μ turns into leftTo"; DF-μ "the one default completion" | typed statements; `cone_minimal_iff` stated over `ConeIndependent`; `defaultZone_budget`; DF-μ″ is DF-γ's zone of `x_permitted`; the unsaid-atom bug shows on the new DF-μ′b; DF-μ has two default completions with the same decisions | Plain predicates have no permission dual, so two rules on different plain predicates never collide (`Incompatible`), and draft 2's DF-μ″ cannot exist. On DF-μ, comparing unsaid atoms leaves both answers unchanged (8.6). |
| C13 | `dfltRankingW D Wd` | `dfltRankingW Wd`, keeping `¬outweighs` when no condition applies | Without that, the empty case is `∀x. outweighs → ⊥`, not `dfltLabelled`'s `∀x. ¬outweighs`, and `dfltRankingW_empty` would be false as an equality. |
| C14 | — | diagnostic 6 (repeated generated labels) | `hl` is checked, not assumed. It never fires on a decoded document (8.4: all 15 fixture documents pass). |
| C15 | DF-δ "strict countermodel: r1's exception at a" | the first strict countermodel the search finds is `outweighs` (r2 outweighs r1) | Either one shows `needs`. The fixture records the one found. |
| C16 | DF-ξ = weighing's Z-ε | Z-ε's shape (DF-α) and DF-π, both computed; Z-ε's own document replays in DF-5 | Z-ε is weighing's document and is not on a built branch. DF-ξ′ is added (8.6): it shows that `hadm` is needed. (Spec draft 1 said `hsuff`; DF-ξ′ fails `hadm` too, and spec draft 2 deletes `hsuff`, R14.) |
| C17 | `defaultBase_of_dflt` without `h`; `defaults_model_default_base` with no source for `X = softX …` | `h : WellFormedU U`; no extra hypothesis (`v.hX` gives it) | Typing of the condition formulas. |
| C18 | fallback described in words | `default_entails_minimal_of` with `ReplacementHolds` as an explicit hypothesis | The fallback's (→) as a statement. |
| C19 | DE2, DE2′, DE5 assume a named decider | variants for an `unstated` decider, in soft's existing phrase ("names no decider") | P-1's three rules are decided by `unstated` (8.7). |

### 2.2 Draft 2: the statement review's ruling

The review (Astra and Fable, three rounds, then the DRI's ruling) kept the design and asked for the edits below. "A" is
an agreed correction of the ruling, "D" a disputed point it ruled. Every new statement elaborates in the stub, and every
new value is computed there.

| # | Ruling | Change | Where |
|---|---|---|---|
| R1 | A1 | DF-γ says "No one-assistant situation admits `defaultX`", not "no situation" or "no model". The empty-domain situation is an accepted consistency witness for DF-γ (computed on the wire), and the conclusion holds there. The gate regression carries it and a bound certificate, so only the gate keeps the answer UNKNOWN. DF-ι and DF-σ were recomputed with the empty domain: unaffected | 8.1, 8.5, 8.9, the stub's comment for 7.3's seeded bug |
| R2 | A2 | The gate has three outcomes: checked coherence, a checked collision, or UNKNOWN. New fixture DF-ω (pair certificate missing, no collision): UNKNOWN | 3.3, 8.1, 8.2 |
| R3 | A3 | `CoherenceReplay` (view, pair certificates, optional collision), its verdict and per-pair status, `defaults_coherence_sound`, with `pairChecks` and `pairChecks_sound` as the one per-pair check. `defaults-elaborate`'s rows are `elaborateRows`, `elaborateRows_eq` (`rfl`, proved) | 7.1, 7.2 |
| R4 | A4 | `CertReplay.reason` tests the collision first, then the gate, the model and the certificate: plan 2.6's order. No verdict changes | 5, 7.2 |
| R5 | A5 | The sufficient-condition mutation fails DF-β (i), which it turns FOLLOWS (computed). DF-β (ii) stays entailed | 8.9 |
| R6 | A6 | F-DF1 compares only requests with an accepted consistency witness. New fixture F-DF1′ (contradictory facts) | 8.8 |
| R7 | A7 | `forcedAt_sound` | 3.6, 7.2 |
| R8 | A8 | `selU` with `cohPremiseU_selU` (`rfl`, proved), so DE7's tuple uses `cohPremiseU`'s selection; `collisionTuple_some`. DE7 keeps "The text ranks neither above the other", backed by `cohU_rank_valid` and `collision_unranked` (computed evidence on DF-δ, DF-δ′, DF-γ) | 7.1, 8.2 |
| R9 | A9 | DE4·u. DE7 names one decider when both rules' `exceptionDecider` agree, otherwise both (`giveWayDeciders`, DE7a, DE7b, with `·u` rows). `decidersOf` calls `VE.SoftNorms.Wire.exceptionDecider`. New fixture DF-γ′ (two deciders) | 4, 7.1, 8.1 |
| R10 | A10 | DF-3's wire theorems stated (`DVerdicts`, `readings_wire_default_*`). With the default fold SOME, NONE or UNKNOWN the member is relayed and no default sentence is shown. DE8 appends DE12 for each `unsettled` reading | 3.9, 4, 7.4 |
| R11 | A11 | `defaultZone_notSaid_sound`, `defaultZone_noCompletion_sound`, provisional until WG-6 exposes the enumeration over a given atom list | 7.5 |
| R12 | A12 | `viewOf` runs `match h : decodeLayered j`, takes `hU` from `decodeLayered_soften`, and checks `hD` and `hXw` as Booleans (diagnostic 7). No second decoder, no PK-1 field. `viewOf_layered` is proved | 5, 7.2, 9, 10 |
| R13 | A13 | "Avoidable" defined. "The facts here force <e>" is rendered only from `forcedAll` | 3.8, 4 |
| R14 | D1 | `hsuff` and `noSufficientHolds` deleted. `decisionAtoms_none` stated and proved. DF-ξ′ shows that `hadm` is needed (computed at `x_permitted`) | 2.1 (C16), 7.5, 8.6, 9 |
| R15 | D2 | DE10 in three forms, chosen by `zoneForm`, with DE13 for each assumed decision and one paraphrase. "Completion" and "true decision" stay out of DE10. DF-δ's zone is the regression | 3.8, 4, 7.5, 8.6, 8.9 |
| R16 | D3 | `forcedAllOf` with `forcedAll_sound` (a default completion exists, and each typed exception atom listed holds in every one), `defaultCompletion_below`, `forced_everywhere` (proved from it). DF-μ′ and DF-μ″ report neither alternative exception as forced | 7.5, 8.6, 8.9 |

## 3. Definitions, each with its one reading

### 3.1 `Dflt_T`, the no-exception premises

For each rule `N` of the soft document, in rule order:

- if `N` is a default rule with stated sufficient conditions `C₁ … C_k` (k ≥ 0), the premise
  `∀x̄. excepted_N(x̄) → (⊥ ∨ C₁(x̄) ∨ … ∨ C_k(x̄))`, labelled `default:exception:<N>`. With `k = 0` it is
  `∀x̄. excepted_N(x̄) → ⊥`. *Reading:* rule N's exception holds only where one of the conditions the text states for it
  holds. With none stated, it holds nowhere.
- for each party `π` that may turn `N` off, `∀x̄. ¬off_{N,π}(x̄)`, labelled `default:switch:<N>:<π>`. *Reading:* π
  has not turned rule N off anywhere.

Then for each `outweighs` triple `(a, L, H)` (holistic flag only, in soft's order), `∀x̄. ¬outweighs_{a,L,H}(x̄)`,
labelled `default:ranking:<L>:<H>:<a>`. *Reading:* on act a, the lower-ranked consideration L never outweighs the
higher-ranked H.

Each premise is closed, universal and function-free over the filled base vocabulary (`dflt_wellFormed`). Together with
`Exc_T`'s sufficient premises (`C_i → excepted_N`), `Dflt_T` makes each exception hold **exactly** where a stated
sufficient condition holds. Both directions are fixtures (8.1, DF-β).

### 3.2 A default answer

A default answer is RD-9's checked entailment with `defaultX D X = X ++ Dflt_T` for the document's own `X`. It is
FOLLOWS only with all three of the following. Otherwise it is UNKNOWN with the first missing one as its reason.

1. A certificate for `premisesX U (defaultX D X) Γ ⊢ φ`, bound by `bindCertX`.
2. The gate's certificates.
3. A finite model of `defaultX` and the premises, checked by `xModelOk` (non-vacuity).

### 3.3 The gate

`DefaultCoherent U D R`: on every base admissible with `Exc_T ++ R ++ Dflt_T` (with `Fill_T`), the coherence premise
of every colliding default pair holds. *Reading:* if no exception applies, no two colliding default rules both select.
It is checked with one certificate per pair (`defaultCoherenceCheck`). It is refuted by one checked finite base where
a pair's coherence premise is false (`collisionCheck`). `Coh_T` stays in `X` for the answer itself (D3).

The gate has three outcomes. Checked coherence excludes collisions; a checked collision refutes coherence; without
either, the status is UNKNOWN (DF-ω). Each colliding pair has its own status too: `resolved` when its certificate
checks (its coherence premise then holds on every base admissible with `Exc_T ++ R ++ Dflt_T`), `collision` when the
checked witness names it, `unknown` otherwise.

### 3.4 The basis

`basisOf as sc` takes the labels `as` that the certificate kept (readings' `usedLabels` over `Dflt_T`) and `sc`, the
result of checking the request's strict model:

- `strict` exactly when `as = []`. The conclusion then follows from the document's own premises
  (`basis_strict_sound`).
- `needs` exactly when `as ≠ []` and a strict countermodel checks with `xModelOk U X [] Γ φ m false`. The conclusion
  then fails in some situation the document's own premises allow (`basis_needs_sound`).
- `unsettled` otherwise: labels were kept and no strict countermodel was checked.

`as` is sufficient for the certificate checked. It is never claimed to be minimal.

### 3.5 The form

`followsForm D as` is `short` exactly when every kept label is a **bare exception** label: `default:exception:<N>`
for a default rule with no stated sufficient condition. Otherwise it is `long`. A kept switch, a kept ranking and a
kept exception with conditions each make the form `long`. `followsForm_short` states what `short` gives.

### 3.6 `forced`

`forcedAt D U M F` lists every exception that holds on the finite base, in rule order and then tuple order, as
`(rule, i, tuple)`, where `i` is the index of the first stated sufficient condition that holds at the tuple (the number
of conditions when none does). On a checked default model (`Dflt_T` holds there) every entry has `i <` the number of
conditions (`forcedAt_sound`: the entry names a default rule, and condition `i` and the exception both hold at the
entry's tuple). DE6 is shown exactly when `forced = []`. DE6′ is shown otherwise, with one DE11 per entry.

### 3.7 A default base (D15)

`DefaultBase U D X B` holds when `B` is admissible with `X`, no switch is on, and every admissible competitor on the
same facts, domain and constants whose decisions are a subset of `B`'s has exactly `B`'s decisions. The competitor is
`withOpen U D B δ F`: decisions `δ`, unsaid tables `F`, everything else as in `B`, and `F` is free. *Reading:* the
open decisions are as few as the document and the facts allow, whatever the text leaves unsaid. This is
circumscription of the decision predicates with the unsaid predicates varied. The decision predicates are exceptions,
switches and `outweighs`.

`replacementSafe U D R` is the computed check behind the meaning theorem's (→). It passes when no premise of `R`
(other packs) and no premise of the base background names a decision predicate of `D` or an unsaid predicate of a
pair member.

### 3.8 At one situation (DF-5)

A **default completion** of a finite situation `M` is a completion with three properties:

- it is admissible with PK-1's whole `X` and `Fill_T`;
- it agrees with the record and has every switch off unless the record says otherwise;
- it agrees with the observations, and no completion with these properties has strictly fewer decision atoms.

Only decision atoms are compared, so unsaid atoms vary (D15, the same definition as 3.7). The zone of an outcome at a
tuple is one of five:

- `by default b`: every default completion gives `b`, and at least one exists;
- `left to <decider>`: two default completions with the same filling differ;
- `by default not said`: they differ, but only between different fillings;
- `no completion`: the record or the observations rule out every completion;
- `unknown`, with weighing's reasons; `unknown (budget)` when more than `maxDefaultAtoms` = 12 open atoms remain.

The enumeration covers every open atom of `M` not fixed by the record (`openAtomsAll`), never only the query's cone,
until `cone_minimal_iff` is proved for a computed independence check.

**True decisions, avoidable, forced.** A completion's *true decisions* are its decision atoms (exceptions, switches,
rankings) that hold in it. A completion's true decisions are *avoidable* when a nonempty subset of them can be removed
while the premises, the record and the observations still hold, with the unsaid tables free to change. A default
completion is one whose true decisions are not avoidable. `forcedAll` lists the typed exception atoms true in every
default completion. Lean gives it only from a nonempty, completely checked enumeration: a zone that is `unknown`
or `no completion` has none. Each exception it lists is then true in every admissible completion that agrees with the record
and the observations (`forced_everywhere`, through the finite minimal-subcompletion lemma `defaultCompletion_below`),
so "The facts here force <e>" is said of it, and of nothing else.

### 3.9 Across readings (DF-3)

`dSem N` is RD-9's `xSem` with `defaultX` for each choice. A choice's conflict freedom is RD-9's strict one together
with the gate. RD-9's fold theorems hold for it as stated. The answer shows the default fold **only when the strict
conflict fold is FREE**. A default-fold CONFLICT is then a failed gate for some compatible choice
(`default_conflict_is_gate`), and it renders as DE7 for that choice. A default fold ALL renders as DE8. With the
default fold SOME, NONE or UNKNOWN the member is relayed and no default sentence is shown. Section 7.4 states the wire
theorems.

## 4. The English (one reading each; Lean selects the row, Python renders it)

`<conclusion>`, `<condition>` and `<situation>` are rendered by the existing renderers. `<Decider>` uses soft's decider
phrases: "the assistant" for the party `assistant`. For `unstated`, the `·u` rows apply.

| # | Wording | The one reading | Paraphrase (IDE, same reading) | Lean selects it when |
|---|---|---|---|---|
| DE1 | `Unless an exception applies, the conclusion follows: <conclusion>.` | In every situation the document allows where no listed rule's exception applies anywhere, the conclusion holds. | `If none of the exceptions listed below applies, then <conclusion>.` | FOLLOWS, basis `needs` or `unsettled`, form `short` |
| DE1′ | `Under the assumptions listed below, the conclusion follows: <conclusion>.` | In every situation the document allows where every listed assumption holds, the conclusion holds. | `If each assumption listed below holds, then <conclusion>.` | FOLLOWS, basis `needs` or `unsettled`, form `long` |
| DE2 | `This assumes that the exception to rule <n> does not apply. <Decider> decides where it applies; the text names no case.` | Assumed: rule n's exception holds nowhere. The text states no condition for it, and the decider is named. | `Assumed: rule <n>'s exception applies nowhere. <Decider> decides where it applies, and the text gives no case where it does.` | a kept `default:exception:<n>` with no stated condition and a named decider |
| DE2·u | `This assumes that the exception to rule <n> does not apply. The text names no case where it applies, and no one who decides.` | the same assumption, decider `unstated` | `Assumed: rule <n>'s exception applies nowhere. The text gives no case and names no decider.` | the same, decider `unstated` |
| DE2′ | `This assumes that the exception to rule <n> applies only where the text says it does: <condition>[, or <condition>]*. <Decider> decides any other case.` | Assumed: rule n's exception holds only where one of the listed conditions holds. | `Assumed: rule <n>'s exception applies only where <condition>[, or where <condition>]*.` | a kept `default:exception:<n>` with stated conditions; conditions in the rule's order |
| DE2′·u | `This assumes that the exception to rule <n> applies only where the text says it does: <condition>[, or <condition>]*. The text names no one who decides any other case.` | the same, decider `unstated` | as DE2′ | the same, decider `unstated` |
| DE3 | `This assumes that <party> has not turned rule <n> off.` | Assumed: party π has turned rule n off nowhere. | `Assumed: rule <n> is not turned off by <party>.` | a kept `default:switch:<n>:<party>` |
| DE4 | `This assumes that, on <act phrase>, the <rank l> consideration does not outweigh the <rank h> consideration. <Decider> decides where it does.` | Assumed: on act a, L never outweighs H. | `Assumed: on <act phrase>, <rank h> is not outweighed by <rank l>.` | a kept `default:ranking:<l>:<h>:<a>`, outranking decider named |
| DE4·u | `This assumes that, on <act phrase>, the <rank l> consideration does not outweigh the <rank h> consideration. The text names no one who decides where it does.` | the same assumption, outranking decider `unstated` (soft-norms.md 3.1 allows it) | `Assumed: on <act phrase>, <rank h> is not outweighed by <rank l>. The text names no decider.` | the same, outranking decider `unstated` |
| DE5 | `This holds whatever <deciders> decide.` (`decides` with one decider) | The conclusion follows from the document's own premises, whatever any exception, switch or ranking decision is. | `This does not depend on any exception, switch or ranking.` | FOLLOWS, basis `strict`, `Dflt_T` not empty. `<deciders>` = `decidersOf D`, each once, in rule order |
| DE5·u | `This holds whatever <deciders> decide, and whatever is decided where the text names no decider.` (no named decider: `This holds whatever is decided where the text names no decider.`) | as DE5 | as DE5 | as DE5, `decidersOf D` contains `unstated` |
| DE6 | `Even if no exception applies, the conclusion does not follow. It fails here: <situation>.` | At the situation shown (a default base) no rule's exception holds, the document's premises and the question's facts hold, and the conclusion fails. | `With no exception at all, the conclusion can still fail, as here: <situation>.` | DOES-NOT-FOLLOW, `forced = []`; then norm-defaults' gap sentences |
| DE6′ | `Even if no exception applies beyond those the text states, the conclusion does not follow. It fails here: <situation>.` + one DE11 per `forced` entry | At the situation shown, every exception that holds is one the text's own conditions force there, and the conclusion fails. | `Even with only the exceptions the text itself forces, the conclusion can fail, as here: <situation>.` | DOES-NOT-FOLLOW, `forced ≠ []` |
| DE7 | `Rules <m> and <n> conflict here unless one of them gives way: <effect of m>, and <effect of n>. The text ranks neither above the other, and names no exception that applies here.` + one of DE7a, DE7a·u, DE7b, DE7b·u | A checked base where, with no exception, both colliding rules select at the tuple shown (`collisionTuple_some`), and the two rules are unranked (`collision_unranked`). | `With no exception, rules <m> and <n> both apply here and cannot both be followed; the text does not say which gives way.` | COLLISION; the gated UNKNOWN of a question; in DF-3, prefixed `Under <reading>:`, each choice whose gate fails when the strict fold is FREE |
| DE7a | `Which rule gives way is left to <decider>.` | Both rules' exceptions are decided by the one decider named. | `<Decider> decides which rule gives way.` | `giveWayDeciders` = one named decider |
| DE7a·u | `The text names no one who decides which rule gives way.` | Neither rule's exception has a decider. | `No decider is named for either rule's exception.` | `giveWayDeciders` = `[unstated]` |
| DE7b | `Whether rule <m> gives way is left to <decider of m>, and whether rule <n> gives way is left to <decider of n>.` | The two rules' exceptions have different named deciders. | `<Decider of m> decides whether rule <m> gives way, and <decider of n> decides whether rule <n> gives way.` | `giveWayDeciders` = two named deciders, in pair order |
| DE7b·u | `Whether rule <k> gives way is left to <decider of k>; the text names no one who decides whether rule <j> gives way.` | One rule's exception has the decider named, the other's has none. | `<Decider of k> decides whether rule <k> gives way; no decider is named for rule <j>.` | `giveWayDeciders` = two entries, one `unstated` (rule j's) |
| DE8 | `Under every reading, the conclusion follows under the assumptions listed for that reading.` + per non-strict reading its DE2 to DE4, then DE12 when that reading's basis is `unsettled` | The default fold is ALL. Each reading's conclusion follows from its own premises with its own listed assumptions. | `Whichever reading is meant, the conclusion follows, given that reading's assumptions below.` | DF-3, default fold ALL, some choice's basis not `strict`. With the default fold SOME, NONE or UNKNOWN, no default sentence is shown |
| DE9 | `Rule n. Every <noun> <verbalisation>, unless an exception applies.` | A default rule on a plain predicate: each `<noun>` satisfies the verbalisation except where rule n's exception applies. | `Each <noun> <verbalisation>, except where rule n's exception applies; <decider> decides where it applies.` | DF-4, authoring and rendering |
| DE10 | `With no exceptions here that could be dropped, alone or together, <result>.` + the listed assumptions | Zone `by default`: in every situation the text, the record and the observations allow whose true decisions are not avoidable (3.8), the outcome is `<result>`, and such a situation exists. | `None of the assumptions listed here can be dropped, alone or together, while satisfying the text, the recorded choices and the observed facts, even if details the text leaves open change.` | DF-5, zone `by default`, `zoneForm` short: every decision atom the record leaves open is an exception |
| DE10′ | `With no assumptions here that could be dropped, alone or together, <result>.` + the listed assumptions | as DE10 | as DE10 | zone `by default`, `zoneForm` long: some open decision atom is not an exception (a ranking; every switch atom is fixed, by the record or off) |
| DE10″ | `With no exceptions here that could be dropped, alone or together, the answer depends on which rule gives way: <two completions>.` (`assumptions` in place of `exceptions` when `zoneForm` is long) | Zone `left to`: two such situations with the same filling give different outcomes. | as DE10 | zone `leftTo`. `<two completions>` lists the true decisions of `w₁` and of `w₂`, each in the words of DE11, DE13 or the forced sentence |
| DE10f | `The facts here force the exception to rule <n> for <tuple>.` | In every situation the text, the record and the observations allow, rule n's exception holds at the tuple (`forced_everywhere`). | `Here rule <n>'s exception must apply for <tuple>, whatever else holds.` | after DE10 or DE10′, once per `forcedAll` entry that no stated condition forces. Never from an `unknown` or `no completion` zone |
| DE11 | `The text's own exception to rule <n> applies here: <condition>.` | At the situation shown, `<condition>` (a stated sufficient condition of rule n's exception, entry `i` of `forced`) holds, so `Exc_T` forces the exception. | `Here rule <n>'s exception applies, because <condition>.` | after DE6′, once per `forced` entry; after DE10 to DE10″, once per true exception a stated condition forces |
| DE12 | `Whether it also holds without these assumptions was not checked.` | Basis `unsettled`: the conclusion may or may not follow from the document's own premises. | `It was not checked whether the conclusion needs these assumptions.` | FOLLOWS, basis `unsettled`, after DE1 or DE1′ and the assumption sentences; in DE8, per `unsettled` reading |
| DE13 | `This assumes that the exception to rule <n> applies to <tuple>.` / `This assumes that <party> has turned rule <n> off for <tuple>.` / `This assumes that, on <act phrase>, the <rank l> consideration outweighs the <rank h> consideration.` | In the situation shown, this decision holds. The ranking uses soft's phrase for an `outweighs` decision (soft-norms.md 1.3). | `Assumed here: rule <n>'s exception applies to <tuple>.` / `Assumed here: <party> has turned rule <n> off for <tuple>.` / `Assumed here: on <act phrase>, <rank l> outweighs <rank h>.` | after DE10 to DE10″, once per true decision of the completion shown that neither DE11 nor DE10f covers |

**DE10's words.** DE10 lists the assumed decisions explicitly, one sentence per true exception, switch or ranking
decision of the completion shown (DE11, DE10f or DE13). "Alone or together" gives the subset reading of 3.8's
"avoidable": without it a reader takes "could be dropped" one assumption at a time, which is a different minimality.
The first form speaks of exceptions only when every decision atom the record leaves open is an exception
(`zoneForm`). Otherwise a ranking could be dropped while every exception stays, as DF-δ's zone shows (8.6), and the
sentence says "assumptions". The words "completion" and "true decision" are this spec's, PLAN 2.8's and the Lean
docstrings'. They never appear in DE10.

**Non-wordings.** The rendered text never contains:

- any `default:`, `soft__` or `unsaid__` name, a label, a formula or a decision name;
- "by default" for these answers (D6);
- "unless an exception applies" where a kept assumption is a switch, a ranking or an exception with stated
  conditions;
- "even if no exception applies" where an exception holds at the situation shown;
- "completion" or "true decision" (DE10 says "assumptions … that could be dropped, alone or together");
- "The facts here force" for anything not in `forcedAll`.

Every row goes through W7's all-derivations gate before it is shown. DE9 is the only row an author writes. The
paraphrases are the IDE's "say it another way" lines: each has the same one reading as its row, and W7 checks each one
the same way.

## 5. Diagnostics and statuses

The texts are computed by Lean (8.4 shows them).

| # | Text | When |
|---|---|---|
| 1 | `UnsupportedProfile: answers that assume no exception are not available with weighing@0 yet` | the source's profiles contain `weighing@0`, until DF-6 |
| 2 | `InvalidInput: answers that assume no exception need premises that name no decision: <label>` | a premise of `R` (`X` after the soft pack) names a decision predicate (`decisionFree`); `<label>` is its pack label |
| 3 | `InvalidInput: a question that assumes no exception may state facts only; it states <what>` | `questionDiag D Γ = some …`. `<what>` is computed from the first premise predicate, in premise order, that is regulated or a decision: `whether rule <n>'s exception applies`, `whether <party> has turned rule <n> off`, `whether the <L> consideration outweighs the <H> consideration on <a>`, or `the outcome <p>` |
| 4 | `ResourceLimit: generated default premise <label>` | a `Dflt_T` premise fails soft's `withinLimits` (`MAX_NODES`, `MAX_DEPTH`). The premise is one atom and the author's own condition formulas, so building it is linear in the source |
| 5 | `InvalidInput: coherence certificates do not match the colliding pairs` | the request's pair list differs in length or order from `coherence_targets` |
| 6 | `InvalidInput: two generated default premises share the label <label>` | `wellLabelled (dfltLabelled D)` fails. It never fires on a decoded document (rule names, parties and ranks contain no `:`), and is kept so that `hl` is checked |
| 7 | `InvalidInput: answers that assume no exception need a well-formed document` | `WellFormedSoft L.D` or the check of `L.X` (`Formula.check` at `envAt (fill L.U) 0`, read through `check_iff_wellFormed`) fails. It never fires on a decoded document (8.4: all 15 fixture documents pass; RD-9 proves both per branch), and is kept so that `hD` and `hXw` are checked, not assumed |

`viewOf` gives `decodeLayered`'s own refusals, then 7, 1, 2, 6 and 4, in that order. `replayCert` gives 3 and 5, and
`replayCoherence` gives 5. Statuses of `defaults-certificate`, in the order `CertReplay.reason` checks them (plan 2.6's
order; the collision first, whether or not a certificate was sent):
`UNKNOWN (with no exception, rules <m> and <n> conflict)` (a checked collision),
`UNKNOWN (no-exception coherence not checked)`,
`UNKNOWN (no checked situation where the premises hold with no exception)`, and
`UNKNOWN (no certificate)`.

`defaults-coherence` answers COHERENT (every pair certificate checks), COLLISION (the collision checks) or UNKNOWN
(neither), with each pair's status `resolved`, `collision` or `unknown`.

## 6. Not claimed

- No claim that an exception does not apply in fact. A default answer says what holds if none applies.
- No answer over all situations to a question that states an outcome or a decision (D5).
- No automatic priority by specificity, recency or authority (D8). No specificity suggestion either: the IDE check
  "Rule m (exception to rule n)." is built only if DF-E3's re-run meets its bar (phase 1: UNKNOWN, 0 certain pairs).
- No minimality of the listed assumptions: they are sufficient for the certificate checked.
- No claim that the conclusion needs its assumptions unless the basis is `needs` (a checked strict countermodel).
- Minimality of the situations only once DF-2 is proved, only under the gate and `replacementSafe`, and never under
  the fallback. Until then, no English, `lean/DEFAULTS.md` or doc text says that the situations range over the fewest
  decisions.

## 7. Lean statements

Each block elaborates in the namespace and `open`s shown. Theorems are given without proofs. 7.8 records what the stub
proves.

### 7.1 `lean/VE/Defaults/Premises.lean` (DF-1a)

```lean
namespace VE.Defaults
open VE.Norms (bindAll atom anyF preds Sat DocumentExpansion restrictAll envAt size)
open VE.SoftNorms (SoftDoc SoftNode exceptedF outweighsF offName sortsOf actSortsOf outweighsTriples
  decisionNames offDecisions collidingPairs excPremises soften WellFormedSoft)
open VE.NormDefaults (UDoc fill fillPremises WellFormedU EntailsX modelCheckX)
open VE.NormDefaults.Wire (BaseAdmissibleX cohPremiseU softLabelledU premisesX LayeredU)
universe u

def dfltOf (D : SoftDoc) (N : SoftNode) : List (String × VE.Formula) :=
  (match N.mode, N.exception with
   | .default, some e =>
       [("default:exception:" ++ N.name,
         bindAll (sortsOf D N.pred) (.implies (exceptedF D N) (anyF e.sufficient)))]
   | _, _ => []) ++
  N.alterable.map (fun π =>
    ("default:switch:" ++ N.name ++ ":" ++ π,
     bindAll (sortsOf D N.pred) (.not (atom (offName N π) (sortsOf D N.pred)))))

def dfltLabelled (D : SoftDoc) : List (String × VE.Formula) :=
  D.T.nodes.flatMap (dfltOf D) ++
  (outweighsTriples D).map (fun (a, L, H) =>
    ("default:ranking:" ++ L ++ ":" ++ H ++ ":" ++ a, bindAll (actSortsOf D a) (.not (outweighsF D a L H))))

def dfltPremises (D : SoftDoc) : List VE.Formula := (dfltLabelled D).map (·.2)
def dfltLabels (D : SoftDoc) : List String := (dfltLabelled D).map (·.1)
def defaultX (D : SoftDoc) (X : List VE.Formula) : List VE.Formula := X ++ dfltPremises D
def withoutDefaults (D : SoftDoc) (X : List VE.Formula) : List VE.Formula :=
  X ++ (dfltPremises D).map (fun _ => VE.Formula.top)

def decisionFree (D : SoftDoc) (φ : VE.Formula) : Bool :=
  (preds φ).all (fun p => !(decisionNames D).contains p)

def whatOf (D : SoftDoc) (p : String) : Option String :=
  match (VE.SoftNorms.keyedDecisions D).find? (·.2.1 == p) with
  | some (.excepted r, _) => some s!"whether rule {r}'s exception applies"
  | some (.off r π, _) => some s!"whether {π} has turned rule {r} off"
  | some (.outweighs a L H, _) => some s!"whether the {L} consideration outweighs the {H} consideration on {a}"
  | none => if (D.T.regulated.map (·.name)).contains p then some s!"the outcome {p}" else none

def questionDiag (D : SoftDoc) (Γ : List VE.Formula) : Option String :=
  ((Γ.flatMap preds).findSome? (whatOf D)).map (fun w =>
    "InvalidInput: a question that assumes no exception may state facts only; it states " ++ w)

theorem questionDiag_none (D : SoftDoc) (Γ : List VE.Formula) (h : questionDiag D Γ = none) :
    ∀ a ∈ Γ, ∀ p ∈ preds a, p ∉ decisionNames D ∧ p ∉ D.T.regulated.map (·.name)

def limitDiag (D : SoftDoc) : Option String :=
  ((dfltLabelled D).find? (fun x => !VE.SoftNorms.withinLimits x.2)).map (fun x =>
    "ResourceLimit: generated default premise " ++ x.1)

theorem dflt_wellFormed (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) :
    ∀ a ∈ dfltPremises D, a.WellFormed (envAt (fill U) 0) []

theorem entailsX_mono (U : UDoc) (X₁ X₂ Γ : List VE.Formula) (φ : VE.Formula)
    (h : ∀ a ∈ X₁, a = .top ∨ a ∈ X₂) : EntailsX.{u} U X₁ Γ φ → EntailsX.{u} U X₂ Γ φ

theorem strict_of_withoutDefaults (U : UDoc) (D : SoftDoc) (X Γ : List VE.Formula) (φ : VE.Formula)
    (h : EntailsX.{u} U (withoutDefaults D X) Γ φ) : EntailsX.{u} U X Γ φ

def DefaultCoherent (U : UDoc) (D : SoftDoc) (R : List VE.Formula) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleX U (excPremises D ++ R ++ dfltPremises D) B →
    ∀ M N, (M, N) ∈ collidingPairs D → (cohPremiseU U D M N).denote B []

/-- One pair's certificate checks: the pair's `cohPremiseU` from `Exc_T ++ R ++ Dflt_T` with the base background
    and `Fill_T`. -/
def pairChecks (U : UDoc) (D : SoftDoc) (R : List VE.Formula) (P Q : SoftNode)
    (c : Option VE.Tableau.Certificate) : Bool :=
  match c with
  | some c => VE.Tableau.checkCertificate (envAt (fill U) 0)
      (VE.Norms.backgroundBase (fill U) ++ (excPremises D ++ R ++ dfltPremises D) ++ fillPremises U)
      (cohPremiseU U D P Q) c
  | none => false

def defaultCoherenceCheck (U : UDoc) (D : SoftDoc) (R : List VE.Formula)
    (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (collidingPairs D).length == certs.length &&
    ((collidingPairs D).zip certs).all (fun (p, c) => pairChecks U D R p.1 p.2 c)

theorem defaultCoherenceCheck_sound (U : UDoc) (D : SoftDoc) (R : List VE.Formula)
    (certs : List (Option VE.Tableau.Certificate)) (hc : defaultCoherenceCheck U D R certs = true) :
    DefaultCoherent.{u} U D R

theorem pairChecks_sound (U : UDoc) (D : SoftDoc) (R : List VE.Formula) (P Q : SoftNode)
    (c : Option VE.Tableau.Certificate) (hc : pairChecks U D R P Q c = true) (B : VE.Structure.{u})
    (hB : BaseAdmissibleX U (excPremises D ++ R ++ dfltPremises D) B) : (cohPremiseU U D P Q).denote B []

def collisionCheck (U : UDoc) (D : SoftDoc) (R : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (m n : String) : Bool :=
  match (collidingPairs D).find? (fun p => p.1.name == m && p.2.name == n) with
  | none => false
  | some (P, Q) =>
    VE.Norms.backgroundValid U.D M && VE.NormDefaults.fillValid U M F &&
      VE.NormDefaults.Wire.extraValid U (excPremises D ++ R ++ dfltPremises D) M F &&
      !(cohPremiseU U D P Q).eval (M.withFill F) []

theorem collision_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (R : List VE.Formula)
    (M : VE.FiniteModel VE.Bridge.Entity) (valid : M.Valid (envAt U.D 0))
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (m n : String)
    (hc : collisionCheck U D R M F m n = true) :
    ¬ DefaultCoherent.{0} U D R

/-- A rule's selection on the filled tree, as `cohPremiseU` builds it. -/
def selU (U : UDoc) (D : SoftDoc) (K : SoftNode) : VE.Formula :=
  VE.Norms.subst (fill U).T (size (fill U)) (VE.Norms.selects (fill U).T (VE.Norms.fuel (fill U).T) (VE.SoftNorms.primeNode D K))

theorem cohPremiseU_selU (U : UDoc) (D : SoftDoc) (P Q : SoftNode) :
    cohPremiseU U D P Q = bindAll (VE.SoftNorms.actSorts D P) (.not (.and (selU U D P) (selU U D Q)))   -- `rfl`

def collisionTuple (U : UDoc) (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (P Q : SoftNode) : Option (List VE.Bridge.Entity) :=
  (VE.NormDefaults.allTuples M (VE.SoftNorms.actSorts D P)).find? (fun vs =>
    (VE.Formula.and (selU U D P) (selU U D Q)).eval (M.withFill F) (VE.Norms.tupleVal vs))

/-- DE7 always has a tuple to show. -/
theorem collisionTuple_some (U : UDoc) (D : SoftDoc) (R : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (m n : String) (P Q : SoftNode)
    (hp : (collidingPairs D).find? (fun p => p.1.name == m && p.2.name == n) = some (P, Q))
    (hc : collisionCheck U D R M F m n = true) :
    ∃ vs, collisionTuple U D M F P Q = some vs

/-- Soft's `coh_rank_valid_unconditional` on the filled tree: a ranked pair's coherence premise is valid. -/
theorem cohU_rank_valid (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (M N : SoftNode) (hc : (M, N) ∈ collidingPairs D)
    (hcmp : VE.SoftNorms.Comparable D M N = true) (B : VE.Structure.{u}) : (cohPremiseU U D M N).denote B []

/-- DE7's "The text ranks neither above the other": a checked collision's pair is unranked. -/
theorem collision_unranked (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
    (valid : M.Valid (envAt U.D 0)) (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (m n : String)
    (P Q : SoftNode) (hp : (collidingPairs D).find? (fun p => p.1.name == m && p.2.name == n) = some (P, Q))
    (hc : collisionCheck U D R M F m n = true) :
    VE.SoftNorms.Comparable D P Q = false

def certChecks (U : UDoc) (ps : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (fill U) (size (fill U))) ps φ c

theorem premisesX_split (U : UDoc) (D : SoftDoc) (X Γ : List VE.Formula) :
    premisesX U (defaultX D X) Γ =
      (VE.Norms.background (fill U) ++ X) ++ (dfltLabelled D).map (·.2) ++
        (fillPremises U ++ VE.Norms.elaborate (fill U).T ++ Γ)

def assumptionsOf (U : UDoc) (D : SoftDoc) (X Γ : List VE.Formula) (φ : VE.Formula)
    (c : VE.Tableau.Certificate) : List String :=
  VE.Readings.usedLabels (fun ps => certChecks U ps φ c)
    (VE.Norms.background (fill U) ++ X) (dfltLabelled D)
    (fillPremises U ++ VE.Norms.elaborate (fill U).T ++ Γ)

theorem assumptions_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (hl : VE.Compose.Labelled.wellLabelled (dfltLabelled D) = true)
    (X Γ : List VE.Formula) (hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []) (φ : VE.Formula)
    (c : VE.Tableau.Certificate) (hc : certChecks U (premisesX U (defaultX D X) Γ) φ c = true) :
    EntailsX.{u} U (X ++ VE.Readings.blank (dfltLabelled D) (assumptionsOf U D X Γ φ c)) Γ φ

inductive Basis | strict | needs | unsettled
  deriving DecidableEq, Repr

def basisOf (as : List String) (strictCounter : Bool) : Basis :=
  if as.isEmpty then .strict else if strictCounter then .needs else .unsettled

theorem basis_strict_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (hl : VE.Compose.Labelled.wellLabelled (dfltLabelled D) = true)
    (X Γ : List VE.Formula) (hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []) (φ : VE.Formula)
    (c : VE.Tableau.Certificate) (hc : certChecks U (premisesX U (defaultX D X) Γ) φ c = true) (sc : Bool)
    (hb : basisOf (assumptionsOf U D X Γ φ c) sc = .strict) :
    EntailsX.{u} U X Γ φ

theorem basis_needs_sound (U : UDoc) (h : WellFormedU U = true) (X Γ : List VE.Formula) (φ : VE.Formula)
    (m : VE.Readings.Wire.FilledModel U) (hm : VE.Readings.Wire.xModelOk U X [] Γ φ m false = true) :
    VE.Readings.CounterX U X Γ φ ∧ ¬ EntailsX.{0} U X Γ φ

inductive Form | short | long
  deriving DecidableEq, Repr

def bareExceptionLabels (D : SoftDoc) : List String :=
  D.T.nodes.filterMap (fun N => match N.mode, N.exception with
    | .default, some e => if e.sufficient.isEmpty then some ("default:exception:" ++ N.name) else none
    | _, _ => none)

def followsForm (D : SoftDoc) (as : List String) : Form :=
  if as.all (fun l => (bareExceptionLabels D).contains l) then .short else .long

theorem followsForm_short (D : SoftDoc) (as : List String) (h : followsForm D as = .short) :
    ∀ l ∈ as, ∃ N ∈ D.T.nodes, l = "default:exception:" ++ N.name ∧
      (l, bindAll (sortsOf D N.pred) (.implies (exceptedF D N) (anyF []))) ∈ dfltLabelled D

def decidersOf (D : SoftDoc) : List String :=
  let raw := D.T.nodes.flatMap (fun N =>
      (match N.mode, N.exception with
       | .default, some _ => [VE.SoftNorms.Wire.exceptionDecider D N]
       | _, _ => []) ++ N.alterable) ++
    (if (outweighsTriples D).isEmpty then [] else [(D.soft.outrankingDecider).getD "unstated"])
  raw.foldl (fun acc d => if acc.contains d then acc else acc ++ [d]) []

/-- DE7's deciders: one when the two rules' exceptions have the same decider (soft's `exceptionDecider`), otherwise
    both, in pair order. `unstated` selects the `·u` rows. -/
def giveWayDeciders (D : SoftDoc) (P Q : SoftNode) : List String :=
  let dP := VE.SoftNorms.Wire.exceptionDecider D P
  let dQ := VE.SoftNorms.Wire.exceptionDecider D Q
  if dP == dQ then [dP] else [dP, dQ]
```

`collision_unranked` is `cohU_rank_valid` evaluated on the checked base: the collision makes the pair's coherence
premise false there, and a ranked pair's premise holds everywhere. `cohU_rank_valid` is soft's
`coh_rank_valid_unconditional` (`SoftNorms/RankProof.lean`) carried to `fill U` (`fillTree`: the soft rules'
roots, plus one rule per unspecified predicate guarded by its unsaid table). It is stated, not proved. The stub
evaluates the premise on every one-element situation of DF-δ and DF-δ′ (8.2). If DF-1a cannot prove it, DE7 drops
"The text ranks neither above the other", the ruling's alternative.

### 7.2 `lean/VE/Defaults/Wire.lean` (DF-1a)

```lean
namespace VE.Defaults.Wire
open VE.Defaults
open VE.Norms (envAt size)
open VE.SoftNorms (SoftDoc SoftNode soften WellFormedSoft)
open VE.NormDefaults (UDoc fill EntailsX)
open VE.NormDefaults.Wire (LayeredU softLabelledU premisesX)
universe u

structure DefaultsView where
  L : LayeredU
  R : List VE.Formula
  hX : L.X = (softLabelledU L.U L.D).map (·.2) ++ R
  hU : L.U.D = soften L.D
  hD : WellFormedSoft L.D = true
  hXw : ∀ a ∈ L.X, a.WellFormed (envAt (fill L.U) 0) []
  hR : R.all (decisionFree L.D) = true
  hl : VE.Compose.Labelled.wellLabelled (dfltLabelled L.D) = true

/-- Both branches of `decodeLayered` build `U := ⟨soften D, …⟩` (`decodeSoftU`, `decodeRightsU`). -/
theorem decodeLayered_soften (j : Json) (L : LayeredU) (h : VE.NormDefaults.Wire.decodeLayered j = .ok L) :
    L.U.D = soften L.D

/-- What diagnostics 1, 2, 6 and 4 give on a decoded document: `R` (X after the soft pack) with `hX`, `hR`, `hl`. -/
structure ViewRest (L : LayeredU) where
  R : List VE.Formula
  hX : L.X = (softLabelledU L.U L.D).map (·.2) ++ R
  hR : R.all (decisionFree L.D) = true
  hl : VE.Compose.Labelled.wellLabelled (dfltLabelled L.D) = true

/-- Diagnostics 1, 2, 6 and 4 of section 5, in that order. -/
def viewRest (j : Json) (L : LayeredU) : Except String (ViewRest L)

def notWellFormedText : String := "InvalidInput: answers that assume no exception need a well-formed document"

/-- `decodeLayered` itself (no second decoder), then diagnostic 7 (`hD`, and `hXw` through `check_iff_wellFormed`),
    then `viewRest`. `hU` is `decodeLayered_soften`. -/
def viewOf (j : Json) : Except String DefaultsView :=
  match h : VE.NormDefaults.Wire.decodeLayered j with
  | .error e => .error e
  | .ok L =>
    if hD : WellFormedSoft L.D = true then
      if hXw : L.X.all (·.check (envAt (fill L.U) 0) []) = true then
        match viewRest j L with
        | .error e => .error e
        | .ok r => .ok ⟨L, r.R, r.hX, decodeLayered_soften j L h, hD,
            fun a ha => (VE.check_iff_wellFormed _ _ a).mp (List.all_eq_true.mp hXw a ha), r.hR, r.hl⟩
      else .error notWellFormedText
    else .error notWellFormedText

theorem viewOf_layered (j : Json) (v : DefaultsView) (h : viewOf j = .ok v) :
    VE.NormDefaults.Wire.decodeLayered j = .ok v.L                                  -- proved in the stub

structure Collision (U : UDoc) where
  S : VE.NormDefaults.Wire.SituationG U
  F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity
  m : String
  n : String

structure CertReplay where
  v : DefaultsView
  Γ : List VE.Formula
  φ : VE.Formula
  cert : Option VE.Tableau.Certificate
  pairCerts : List (Option VE.Tableau.Certificate)
  collision : Option (Collision v.L.U)
  model : Option (VE.Readings.Wire.FilledModel v.L.U)
  strictModel : Option (VE.Readings.Wire.FilledModel v.L.U)

def CertReplay.certOk (x : CertReplay) : Bool :=
  match x.cert with
  | some c => certChecks x.v.L.U (premisesX x.v.L.U (defaultX x.v.L.D x.v.L.X) x.Γ) x.φ c
  | none => false
def CertReplay.coherent (x : CertReplay) : Bool := defaultCoherenceCheck x.v.L.U x.v.L.D x.v.R x.pairCerts
def CertReplay.collides (x : CertReplay) : Bool :=
  match x.collision with
  | some w => collisionCheck x.v.L.U x.v.L.D x.v.R w.S.M w.F w.m w.n
  | none => false
def CertReplay.modelOk (x : CertReplay) : Bool :=
  match x.model with
  | some m => VE.Readings.Wire.xModelOk x.v.L.U (defaultX x.v.L.D x.v.L.X) [] x.Γ .bottom m false
  | none => false
def CertReplay.strictCounter (x : CertReplay) : Bool :=
  match x.strictModel with
  | some m => VE.Readings.Wire.xModelOk x.v.L.U x.v.L.X [] x.Γ x.φ m false
  | none => false
def CertReplay.assumptions (x : CertReplay) : List String :=
  match x.cert with
  | some c => assumptionsOf x.v.L.U x.v.L.D x.v.L.X x.Γ x.φ c
  | none => []
def CertReplay.basis (x : CertReplay) : Basis := basisOf x.assumptions x.strictCounter
def CertReplay.form (x : CertReplay) : Form := followsForm x.v.L.D x.assumptions
def CertReplay.verdict (x : CertReplay) : String :=
  if x.certOk && x.coherent && x.modelOk then "FOLLOWS" else "UNKNOWN"
/-- Plan 2.6's order: a checked collision first, whether or not a certificate was sent (it implies
    `coherent = false`, so no verdict changes); then the gate, the model and the certificate. -/
def CertReplay.reason (x : CertReplay) : String :=
  match x.collision, x.collides with
  | some w, true => s!"with no exception, rules {w.m} and {w.n} conflict"
  | _, _ =>
    if !x.coherent then "no-exception coherence not checked"
    else if !x.modelOk then "no checked situation where the premises hold with no exception"
    else "no certificate"

/-- The view, the premises (diagnostic 3), the conclusion, the certificate bound by `bindCertX` to
    `premisesX U (defaultX D X) Γ` (absent when it does not bind), the pair certificates (diagnostic 5), the
    collision witness, the model and the strict model. -/
def replayCert (j : Json) : Except String CertReplay

theorem defaults_follows_gated (x : CertReplay) (hv : x.verdict = "FOLLOWS") :
    x.certOk = true ∧ x.coherent = true ∧ x.modelOk = true

theorem defaults_certificate_sound (x : CertReplay) (hv : x.verdict = "FOLLOWS") :
    EntailsX.{u} x.v.L.U (x.v.L.X ++ VE.Readings.blank (dfltLabelled x.v.L.D) x.assumptions) x.Γ x.φ ∧
    DefaultCoherent.{u} x.v.L.U x.v.L.D x.v.R ∧
    VE.Readings.ConsistentX x.v.L.U (defaultX x.v.L.D x.v.L.X) x.Γ ∧
    (x.basis = .strict → EntailsX.{u} x.v.L.U x.v.L.X x.Γ x.φ) ∧
    (x.basis = .needs → VE.Readings.CounterX x.v.L.U x.v.L.X x.Γ x.φ)

/-- `defaults-elaborate`: `default_premises` (label, AST) and `coherence_targets` (the two rule names and the pair's
    `cohPremiseU`), in these orders. -/
def elaborateRows (v : DefaultsView) : List (String × VE.Formula) × List (SoftNode × SoftNode) :=
  (dfltLabelled v.L.D, VE.SoftNorms.collidingPairs v.L.D)

theorem elaborateRows_eq (v : DefaultsView) :
    (elaborateRows v).1 = dfltLabelled v.L.D ∧ (elaborateRows v).2 = VE.SoftNorms.collidingPairs v.L.D   -- `⟨rfl, rfl⟩`

structure CoherenceReplay where
  v : DefaultsView
  pairCerts : List (Option VE.Tableau.Certificate)
  collision : Option (Collision v.L.U)

def CoherenceReplay.coherent (x : CoherenceReplay) : Bool :=
  defaultCoherenceCheck x.v.L.U x.v.L.D x.v.R x.pairCerts
def CoherenceReplay.collides (x : CoherenceReplay) : Bool :=
  match x.collision with
  | some w => collisionCheck x.v.L.U x.v.L.D x.v.R w.S.M w.F w.m w.n
  | none => false
def CoherenceReplay.verdict (x : CoherenceReplay) : String :=
  if x.coherent then "COHERENT" else if x.collides then "COLLISION" else "UNKNOWN"

inductive PairStatus | resolved | collision | unknown
  deriving DecidableEq, Repr

/-- Each colliding pair, in `collidingPairs` order, with its status. -/
def CoherenceReplay.pairs (x : CoherenceReplay) : List ((SoftNode × SoftNode) × PairStatus) :=
  (VE.SoftNorms.collidingPairs x.v.L.D).mapIdx (fun i p =>
    (p, if pairChecks x.v.L.U x.v.L.D x.v.R p.1 p.2 (x.pairCerts.getD i none) then .resolved
        else if x.collides && x.collision.any (fun w => w.m == p.1.name && w.n == p.2.name) then .collision
        else .unknown))

/-- The view, the pair certificates (diagnostic 5) and the collision witness. -/
def replayCoherence (j : Json) : Except String CoherenceReplay

theorem defaults_coherence_sound (x : CoherenceReplay) :
    (x.verdict = "COHERENT" → DefaultCoherent.{u} x.v.L.U x.v.L.D x.v.R) ∧
    (x.verdict = "COLLISION" → ¬ DefaultCoherent.{0} x.v.L.U x.v.L.D x.v.R) ∧
    (∀ P Q, ((P, Q), PairStatus.resolved) ∈ x.pairs → ∀ B : VE.Structure.{u},
      VE.NormDefaults.Wire.BaseAdmissibleX x.v.L.U (VE.SoftNorms.excPremises x.v.L.D ++ x.v.R ++ dfltPremises x.v.L.D) B →
        (VE.NormDefaults.Wire.cohPremiseU x.v.L.U x.v.L.D P Q).denote B [])

def forcedAt (D : SoftDoc) (U : UDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) : List (String × Nat × List VE.Bridge.Entity) :=
  D.T.nodes.flatMap (fun N => match N.mode with
    | .default =>
      let conds := (N.exception.map (·.sufficient)).getD []
      (VE.NormDefaults.allTuples M (VE.SoftNorms.sortsOf D N.pred)).filterMap (fun vs =>
        if (VE.SoftNorms.exceptedF D N).eval (M.withFill F) (VE.Norms.tupleVal vs) then
          some (N.name, (conds.findIdx? (fun C => C.eval (M.withFill F) (VE.Norms.tupleVal vs))).getD conds.length, vs)
        else none)
    | .strict => [])

structure ModelReplay where
  v : DefaultsView
  Γ : List VE.Formula
  φ : VE.Formula
  m : VE.Readings.Wire.FilledModel v.L.U

def ModelReplay.ok (x : ModelReplay) : Bool :=
  VE.Readings.Wire.xModelOk x.v.L.U (defaultX x.v.L.D x.v.L.X) [] x.Γ x.φ x.m false
def ModelReplay.forced (x : ModelReplay) : List (String × Nat × List VE.Bridge.Entity) :=
  forcedAt x.v.L.D x.v.L.U x.m.M x.m.F
def ModelReplay.verdict (x : ModelReplay) : String := if x.ok then "DOES-NOT-FOLLOW" else "UNKNOWN"

def replayModel (j : Json) : Except String ModelReplay

theorem defaults_model_sound (x : ModelReplay) (hv : x.ok = true) :
    ∃ S : VE.Structure.{0},
      VE.NormDefaults.Wire.BaseAdmissibleX x.v.L.U (defaultX x.v.L.D x.v.L.X)
        (VE.Norms.restrictAll (fill x.v.L.U).T S) ∧
      VE.Norms.DocumentExpansion (fill x.v.L.U) (VE.Norms.restrictAll (fill x.v.L.U).T S) S ∧
      VE.Norms.Sat S x.Γ ∧ ¬ x.φ.denote S [] ∧
      (x.forced = [] → ∀ N ∈ x.v.L.D.T.nodes, N.mode = .default →
        (VE.Norms.bindAll (VE.SoftNorms.sortsOf x.v.L.D N.pred) (.not (VE.SoftNorms.exceptedF x.v.L.D N))).denote S [])

/-- DE6′'s and DE11's claim: each `forced` entry names a default rule, its index is below that rule's number of
    stated sufficient conditions, and that condition and the exception both hold at the entry's tuple. -/
theorem forcedAt_sound (x : ModelReplay) (hv : x.ok = true) :
    ∀ e ∈ x.forced, ∃ N ∈ x.v.L.D.T.nodes, ∃ ex : VE.SoftNorms.Exception,
      N.mode = .default ∧ N.exception = some ex ∧ e.1 = N.name ∧
      ∃ hi : e.2.1 < ex.sufficient.length,
        (ex.sufficient[e.2.1]'hi).eval (x.m.M.withFill x.m.F) (VE.Norms.tupleVal e.2.2) = true ∧
        (VE.SoftNorms.exceptedF x.v.L.D N).eval (x.m.M.withFill x.m.F) (VE.Norms.tupleVal e.2.2) = true

/-- The `defaults-*` kinds; `none` for any other kind (one row of PK-1's layered kind table). -/
def defaultsCase (v : DefaultsView) (id kind : String) (j : Json) : Except String (Option Json)

theorem defaultsCase_other (v : DefaultsView) (id kind : String) (j : Json)
    (hk : kind.startsWith "defaults-" = false) : defaultsCase v id kind j = .ok none
```

The kinds' rows are as in plan 2.2. `defaults-elaborate` answers `elaborateRows`. `defaults-coherence` answers
`verdict` and `pairs`, and with COLLISION the situation, the tuple (`collisionTuple`) and the deciders
(`giveWayDeciders`) that DE7 renders. `defaults-certificate` answers `verdict`. With FOLLOWS it adds `basis`, `form`
and `assumptions`. With UNKNOWN it adds `reason`. `defaults-model` answers `verdict`, the situation and `forced`.

`viewOf_layered` is proved in the stub from `viewOf`'s body: the view's `L` is the one `decodeLayered` returned. Its
`#print axioms` lists `sorryAx` only because `viewRest` and `decodeLayered_soften` have no body yet.

### 7.3 `lean/VE/Defaults/Meaning.lean` (DF-2)

```lean
namespace VE.Defaults
open VE.Norms (bindAll atom anyF preds Sat DocumentExpansion restrictAll envAt size)
open VE.SoftNorms (SoftDoc SoftNode exceptedF exceptedName sortsOf decisionNames soften WellFormedSoft)
open VE.NormDefaults (UDoc fill fillPremises WellFormedU EntailsX)
open VE.NormDefaults.Wire (BaseAdmissibleX softLabelledU)
universe u

def withOpen (U : UDoc) (D : SoftDoc) (B : VE.Structure.{u}) (δ F : String → List B.Carrier → Prop) :
    VE.Structure.{u} :=
  { B with relation := fun p vs =>
      if p ∈ decisionNames D then δ p vs
      else if p ∈ VE.NormDefaults.unsaidNames U then F p vs
      else B.relation p vs }

def SwitchesOff (D : SoftDoc) (B : VE.Structure.{u}) : Prop :=
  Sat B (((dfltLabelled D).filter (fun a => a.1.startsWith "default:switch:")).map (·.2))

def DefaultBase (U : UDoc) (D : SoftDoc) (X : List VE.Formula) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissibleX U X B ∧ SwitchesOff D B ∧
  ∀ δ F : String → List B.Carrier → Prop,
    (∀ p ∈ decisionNames D, ∀ vs, δ p vs → B.relation p vs) →
    BaseAdmissibleX U X (withOpen U D B δ F) → SwitchesOff D (withOpen U D B δ F) →
    ∀ p ∈ decisionNames D, ∀ vs, B.relation p vs → δ p vs

def softX (U : UDoc) (D : SoftDoc) (R : List VE.Formula) : List VE.Formula :=
  (softLabelledU U D).map (·.2) ++ R

def leastDecisions (D : SoftDoc) (B : VE.Structure.{u}) : String → List B.Carrier → Prop := fun p vs =>
  ∃ N ∈ D.T.nodes, N.mode = .default ∧ p = exceptedName N ∧ VE.TupleTyped B (sortsOf D N.pred) vs ∧
    ∃ C ∈ ((N.exception.map (·.sufficient)).getD []), C.denote B (VE.Norms.tupleVal vs)

def replacementSafe (U : UDoc) (D : SoftDoc) (R : List VE.Formula) : Bool :=
  (R ++ VE.Norms.backgroundBase (fill U)).all (fun φ => (preds φ).all (fun p =>
    !(decisionNames D).contains p &&
    !((VE.NormDefaults.pairMembers U).map VE.NormDefaults.unsaidName).contains p))

theorem replace_admissible (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (hsafe : replacementSafe U D R = true)
    (hcoh : DefaultCoherent.{u} U D R) (B : VE.Structure.{u}) (hB : BaseAdmissibleX U (softX U D R) B) :
    ∃ F : String → List B.Carrier → Prop,
      (∀ p, p ∉ (VE.NormDefaults.pairMembers U).map VE.NormDefaults.unsaidName →
        ∀ vs, (F p vs ↔ B.relation p vs)) ∧
      BaseAdmissibleX U (defaultX D (softX U D R)) (withOpen U D B (leastDecisions D B) F)

theorem defaultBase_of_dflt (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (B : VE.Structure.{u})
    (hB : BaseAdmissibleX U (defaultX D (softX U D R)) B) :
    DefaultBase U D (softX U D R) B

theorem default_entails_minimal (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (hsafe : replacementSafe U D R = true)
    (hcoh : DefaultCoherent.{u} U D R) (Γ : List VE.Formula) (φ : VE.Formula) :
    EntailsX.{u} U (defaultX D (softX U D R)) Γ φ ↔
      ∀ S : VE.Structure.{u}, DefaultBase U D (softX U D R) (restrictAll (fill U).T S) →
        DocumentExpansion (fill U) (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S []

/-- The fallback (plan 3.4): `replace_admissible`'s conclusion as an explicit hypothesis. -/
def ReplacementHolds (U : UDoc) (D : SoftDoc) (R : List VE.Formula) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleX U (softX U D R) B →
    ∃ F : String → List B.Carrier → Prop,
      BaseAdmissibleX U (defaultX D (softX U D R)) (withOpen U D B (leastDecisions D B) F)

theorem default_entails_minimal_of (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (hrep : ReplacementHolds.{u} U D R)
    (Γ : List VE.Formula) (φ : VE.Formula) :
    EntailsX.{u} U (defaultX D (softX U D R)) Γ φ ↔
      ∀ S : VE.Structure.{u}, DefaultBase U D (softX U D R) (restrictAll (fill U).T S) →
        DocumentExpansion (fill U) (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S []

theorem defaults_model_default_base (x : Wire.ModelReplay) (hv : x.ok = true) :
    ∃ S : VE.Structure.{0}, DefaultBase x.v.L.U x.v.L.D x.v.L.X (restrictAll (fill x.v.L.U).T S) ∧
      DocumentExpansion (fill x.v.L.U) (restrictAll (fill x.v.L.U).T S) S ∧ Sat S x.Γ ∧ ¬ x.φ.denote S []
```

Proof route, as in plan 3.4, with two facts the fixtures confirm.

- (→) `replace_admissible` turns a default base into a competitor with `δ_B`, so minimality gives `B = δ_B` on
  decisions. The gate `hcoh` supplies `Coh_T` after the replacement. `fill_extends` repairs only the pair members'
  unsaid tables.
- (←) is `defaultBase_of_dflt`, which needs no gate.

The fixtures (8.5) confirm both directions on every fixture document where the gate passes. They confirm that the
equivalence fails without the gate (DF-γ). They confirm that it fails under draft 1's fixed filling (DF-π). The DF-π
pair that the plan wants as `example`s is computed in 8.5: `B_π` is a default base with the filling fixed, and is not
one with the filling varied. DF-2 writes them as `example`s over the same finite bases, by `decide` on the evaluation
through `eval_withFill`.

### 7.4 `lean/VE/Readings/DefaultVerdicts.lean` (DF-3)

```lean
namespace VE.Readings
open VE.Defaults
universe u

def choiceSoft (N : NDoc) (c : Choice) : VE.SoftNorms.SoftDoc := VE.Rights.correlate (choiceDoc N.D c).1

theorem choiceX_softX (N : NDoc) (c : Choice) :
    choiceX N c = VE.Defaults.softX (choiceU N c) (choiceSoft N c) []

theorem choiceU_soften (N : NDoc) (c : Choice) : (choiceU N c).D = VE.SoftNorms.soften (choiceSoft N c)

def dSem (N : NDoc) : ChoiceSem :=
  { xSem.{u} N (fun c => defaultX (choiceSoft N c) (choiceX N c)) with
    free := fun c => (VE.Readings.Wire.sdSem.{u} N).free c ∧ DefaultCoherent.{u} (choiceU N c) (choiceSoft N c) []
    notFree := fun c => (VE.Readings.Wire.sdSem.{0} N).notFree c ∨
      ¬ DefaultCoherent.{0} (choiceU N c) (choiceSoft N c) [] }

theorem dSem_entails (N : NDoc) (c : Choice) (Γ : List VE.Formula) (φ : VE.Formula) :
    (dSem.{u} N).entails c Γ φ ↔
      VE.NormDefaults.EntailsX.{u} (choiceU N c) (defaultX (choiceSoft N c) (choiceX N c))
        ((choiceDoc N.D c).2 ++ Γ) φ

theorem default_conflict_is_gate (N : NDoc) (A : Choice) (cs ds : List (Choice × ChoiceResult))
    (hcs : CoversG (VE.Readings.Wire.sdSem.{0} N) A cs)
    (hrs : ∀ x ∈ cs, HoldsG (VE.Readings.Wire.sdSem.{0} N) [] .bottom x.1 x.2)
    (hfree : foldConflict cs = .free)
    (hds : CoversG (dSem.{0} N) A ds) (hrd : ∀ x ∈ ds, HoldsG (dSem.{0} N) [] .bottom x.1 x.2)
    (hconf : foldConflict ds = .conflict) :
    ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ ¬ DefaultCoherent.{0} (choiceU N c) (choiceSoft N c) []

/-- DF-3's replay: RD-9's (`replayVerdictsSD`) and, per chosen choice, the default rows decoded from its
    `defaults-coherence`, `defaults-certificate` and `defaults-model` evidence on the same `choiceLayeredG` source,
    with each FOLLOWS choice's basis and assumptions. -/
structure DVerdicts where
  y : VE.Readings.Wire.SDVerdicts
  dConflictRows : List (Choice × ChoiceResult)
  dQueryRows : List (Choice × ChoiceResult)
  bases : List (Choice × VE.Defaults.Basis × List String)

def replayVerdictsD (j : Lean.Json) : Except String DVerdicts

/-- The default rows hold at `dSem`, from the per-choice replays' soundness theorems. -/
theorem d_rowsHold (z : DVerdicts) :
    RowsHoldG (dSem.{u} z.y.r.N) z.y.x.A z.y.x.Γ z.y.x.φ z.dConflictRows z.dQueryRows

/-- Each listed basis is its choice's `defaults_certificate_sound` basis. -/
theorem d_bases_sound (z : DVerdicts) :
    ∀ c b as, (c, b, as) ∈ z.bases →
      VE.NormDefaults.EntailsX.{u} (choiceU z.y.r.N c)
        (choiceX z.y.r.N c ++ blank (dfltLabelled (choiceSoft z.y.r.N c)) as)
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ ∧
      (b = .strict → VE.NormDefaults.EntailsX.{u} (choiceU z.y.r.N c) (choiceX z.y.r.N c)
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ) ∧
      (b = .needs → CounterX (choiceU z.y.r.N c) (choiceX z.y.r.N c) ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ)

/-- The `default` member: present only when the strict conflict fold is FREE; it carries the default conflict fold
    and the default fold. -/
def DVerdicts.defaultMember (z : DVerdicts) : Option (ChoiceResult × ReadingVerdict) :=
  if foldConflict z.y.x.conflictRows = .free then
    some (foldConflict z.dConflictRows, foldEntailment z.dConflictRows z.dQueryRows)
  else none

theorem readings_wire_default_present (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (m : ChoiceResult × ReadingVerdict) (hm : z.defaultMember = some m) :
    foldConflict z.y.x.conflictRows = .free

theorem readings_wire_default_verdicts_all (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (hv : foldEntailment z.dConflictRows z.dQueryRows = .all) :
    ∀ c, Compatible z.y.r.N.D c → (∀ x ∈ z.y.x.A, x ∈ c) →
      (dSem.{u} z.y.r.N).free c ∧
      VE.NormDefaults.EntailsX.{u} (choiceU z.y.r.N c) (defaultX (choiceSoft z.y.r.N c) (choiceX z.y.r.N c))
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ

theorem readings_wire_default_verdicts_none (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (hv : foldEntailment z.dConflictRows z.dQueryRows = .none) :
    ∀ c, Compatible z.y.r.N.D c → (∀ x ∈ z.y.x.A, x ∈ c) →
      (dSem.{u} z.y.r.N).free c ∧
      CounterX (choiceU z.y.r.N c) (defaultX (choiceSoft z.y.r.N c) (choiceX z.y.r.N c))
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ

theorem readings_wire_default_verdicts_some (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (hv : foldEntailment z.dConflictRows z.dQueryRows = .some) :
    (∀ c, Compatible z.y.r.N.D c → (∀ x ∈ z.y.x.A, x ∈ c) → (dSem.{u} z.y.r.N).free c) ∧
    (∃ c, Compatible z.y.r.N.D c ∧ (∀ x ∈ z.y.x.A, x ∈ c) ∧
      VE.NormDefaults.EntailsX.{u} (choiceU z.y.r.N c) (defaultX (choiceSoft z.y.r.N c) (choiceX z.y.r.N c))
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ) ∧
    (∃ c, Compatible z.y.r.N.D c ∧ (∀ x ∈ z.y.x.A, x ∈ c) ∧
      CounterX (choiceU z.y.r.N c) (defaultX (choiceSoft z.y.r.N c) (choiceX z.y.r.N c))
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ)

theorem readings_wire_default_conflict_free (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (hv : foldConflict z.dConflictRows = .free) :
    ∀ c, Compatible z.y.r.N.D c → (∀ x ∈ z.y.x.A, x ∈ c) → (dSem.{u} z.y.r.N).free c

/-- A present member with a default-fold CONFLICT names a choice whose gate fails (DE7 for that choice). -/
theorem readings_wire_default_conflict (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (r : ReadingVerdict) (hm : z.defaultMember = some (.conflict, r)) :
    ∃ c, Compatible z.y.r.N.D c ∧ (∀ x ∈ z.y.x.A, x ∈ c) ∧
      ¬ DefaultCoherent.{0} (choiceU z.y.r.N c) (choiceSoft z.y.r.N c) []
```

RD-9's `foldG_*` theorems apply to `dSem N` unchanged. The stub elaborates `foldG_all_sound` at `dSem` as an
`example`. DF-3's wire theorems are RD-9 SC-5's `readings_wire_sd_verdicts_*` with `dSem` for `sdSem`, on the rows
read from per-choice `defaults-certificate`, `defaults-model` and `defaults-coherence` replays (`d_rowsHold`), plus
`readings_wire_default_present`: the `default` member is present only when `foldConflict` of the strict rows is FREE.
With it, `readings_wire_default_conflict` (through `default_conflict_is_gate`) turns a default-fold CONFLICT into DE7
for each named choice. The stub proves all six `readings_wire_default_*` from `d_rowsHold` and RD-9's `sd_rowsHold`.

What the member shows, selected by Lean: with the default conflict fold CONFLICT, DE7 per choice whose gate fails
(the default fold is then UNKNOWN). Otherwise, by the default fold: ALL, DE8, with each non-strict reading's DE2 to DE4
and, for an `unsettled` reading, DE12 (`d_bases_sound` gives each reading's basis); SOME, NONE or UNKNOWN, the member
is relayed and no default sentence is shown. DF-3 uses the enumerated route only (at
most 64 choices; plan section 11, issue 6).

### 7.5 WG-6's interface (copied; weighing-PLAN 3.4, draft 5) and `lean/VE/Defaults/Zone.lean` (DF-5)

The `VE.Weighing` block is WG-6's reviewed text, typed, and is not DF's to write. `decisionAtoms` has the body its
docstring describes.

```lean
namespace VE.Weighing
open VE.Norms (Regulated tupleVal outcomeBase)
open VE.NormDefaults (UDoc fill unsaidNames)
open VE.SoftNorms (SoftDoc decisionNames)

def decisionAtoms {α : Type} (D : SoftDoc) (M : VE.FiniteModel α) : List (String × List α) :=
  (VE.SoftNorms.decisions D).flatMap (fun (n, ss) => (VE.NormDefaults.allTuples M ss).map (fun vs => (n, vs)))
def openNames (L : VE.NormDefaults.Wire.LayeredU) : List String := decisionNames L.D ++ unsaidNames L.U
def AdmissibleCompletion {α : Type} (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (record : List ((String × List α) × Bool)) (R : String → List α → Prop) : Prop :=
  (∀ n vs, n ∉ opens → (R n vs ↔ vs ∈ M.relations n)) ∧
  (∀ a b, (a, b) ∈ record → (R a.1 a.2 ↔ b = true)) ∧
  VE.NormDefaults.Wire.BaseAdmissibleX U X { M.asStructure with relation := R }
def OutcomeIn {α : Type} (U : UDoc) (M : VE.FiniteModel α) (R : String → List α → Prop) (r : Regulated)
    (vs : List α) : Prop :=
  (outcomeBase (fill U) r.name).denote { M.asStructure with relation := R } (tupleVal vs)
def SettledZ {α : Type} (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (record : List ((String × List α) × Bool)) (r : Regulated) (vs : List α) (b : Bool) : Prop :=
  (∃ R, AdmissibleCompletion U X M opens record R) ∧
  ∀ R, AdmissibleCompletion U X M opens record R → (OutcomeIn U M R r vs ↔ b = true)
inductive ZoneUnknown (α : Type)
  | budget (opens limit : Nat)
  | branch (assignment : List ((String × List α) × Bool)) (why : String)
end VE.Weighing

namespace VE.Defaults
open VE.Weighing (AdmissibleCompletion OutcomeIn decisionAtoms openNames SettledZ ZoneUnknown)
open VE.SoftNorms (SoftDoc decisionNames offDecisions outweighsTriples)
open VE.NormDefaults (UDoc)
open VE.NormDefaults.Wire (LayeredU)

def DecLe {α : Type} (D : SoftDoc) (M : VE.FiniteModel α) (R₁ R₂ : String → List α → Prop) : Prop :=
  ∀ a ∈ decisionAtoms D M, R₁ a.1 a.2 → R₂ a.1 a.2

def Observed {α : Type} (U : UDoc) (M : VE.FiniteModel α) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (R : String → List α → Prop) : Prop :=
  ∀ o ∈ obs, (OutcomeIn U M R o.1.1 o.1.2 ↔ o.2 = true)

def switchesOffRecord {α : Type} [DecidableEq α] (D : SoftDoc) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) : List ((String × List α) × Bool) :=
  (offDecisions D).flatMap (fun (n, ss) => (VE.NormDefaults.allTuples M ss).filterMap (fun vs =>
    if record.any (fun r => r.1 == (n, vs)) then none else some ((n, vs), false)))

def DefaultCompletion {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (R : String → List α → Prop) : Prop :=
  let rec' := record ++ switchesOffRecord L.D M record
  AdmissibleCompletion L.U X M (openNames L) rec' R ∧ Observed L.U M obs R ∧
  ∀ R', AdmissibleCompletion L.U X M (openNames L) rec' R' → Observed L.U M obs R' → DecLe L.D M R' R →
    DecLe L.D M R R'

def ByDefaultZ {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (r : VE.Norms.Regulated) (vs : List α) (b : Bool) : Prop :=
  (∃ R, DefaultCompletion L X M record obs R) ∧
  ∀ R, DefaultCompletion L X M record obs R → (OutcomeIn L.U M R r vs ↔ b = true)

def ByDefaultLeftTo {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (r : VE.Norms.Regulated) (vs : List α) : Prop :=
  ∃ R₁ R₂, DefaultCompletion L X M record obs R₁ ∧ DefaultCompletion L X M record obs R₂ ∧
    (∀ n ∈ VE.NormDefaults.unsaidNames L.U, ∀ ws, R₁ n ws ↔ R₂ n ws) ∧
    OutcomeIn L.U M R₁ r vs ∧ ¬ OutcomeIn L.U M R₂ r vs

inductive DefaultZone (α : Type)
  | byDefault (b : Bool) (witness : List ((String × List α) × Bool))
  | leftTo (differ : List (String × List α)) (w₁ w₂ : List ((String × List α) × Bool))
  | notSaid (w₁ w₂ : List ((String × List α) × Bool))
  | noCompletion (labels : List String)
  | unknown (reason : ZoneUnknown α)

def maxDefaultAtoms : Nat := 12

def openAtomsAll {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) : List (String × List α) :=
  (decisionAtoms L.D M ++ L.U.unspec.flatMap (fun p =>
      (VE.NormDefaults.allTuples M (VE.NormDefaults.sortsOf L.U.D p)).map (fun vs => (VE.NormDefaults.unsaidName p, vs)))).filter
    (fun a => !record.any (fun r => r.1 == a))

/-- WG-6's bounded enumeration over `openAtomsAll` (the atom list given; plan section 11, issue 1), then the
    assignments that satisfy `X` and `Fill_T` and agree with the observations, each evaluated on the finite
    situation, then the minimality filter over their decision parts. -/
def defaultZoneOf {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (r : VE.Norms.Regulated) (vs : List α) (proposed : List (List ((String × List α) × Bool))) : DefaultZone α

def Adm {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α)
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (R : String → List α → Prop) : Prop :=
  AdmissibleCompletion L.U X M (openNames L) (switchesOffRecord L.D M []) R ∧ Observed L.U M obs R

def Splice {α : Type} [DecidableEq α] (C : List (String × List α)) (R₁ R₂ : String → List α → Prop) :
    String → List α → Prop :=
  fun n vs => if (n, vs) ∈ C then R₁ n vs else R₂ n vs

def AgreeOn {α : Type} (C : List (String × List α)) (R₁ R₂ : String → List α → Prop) : Prop :=
  ∀ a ∈ C, (R₁ a.1 a.2 ↔ R₂ a.1 a.2)

def DecLeOn {α : Type} (D : SoftDoc) (M : VE.FiniteModel α) (C : List (String × List α))
    (R₁ R₂ : String → List α → Prop) : Prop :=
  ∀ a ∈ decisionAtoms D M, a ∈ C → R₁ a.1 a.2 → R₂ a.1 a.2

def ConeIndependent {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α)
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (C : List (String × List α)) : Prop :=
  ∀ R₁ R₂, Adm L X M obs R₁ → Adm L X M obs R₂ → Adm L X M obs (Splice C R₁ R₂)

def QueryIn {α : Type} (L : LayeredU) (M : VE.FiniteModel α) (C : List (String × List α))
    (r : VE.Norms.Regulated) (vs : List α) : Prop :=
  ∀ R₁ R₂, AgreeOn C R₁ R₂ → (OutcomeIn L.U M R₁ r vs ↔ OutcomeIn L.U M R₂ r vs)

theorem cone_minimal_iff {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α)
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (C : List (String × List α))
    (hC : ConeIndependent L X M obs C) (R : String → List α → Prop) :
    (∃ R', DefaultCompletion L X M [] obs R' ∧ AgreeOn C R' R) ↔
      ((∃ R₀, Adm L X M obs R₀ ∧ AgreeOn C R₀ R) ∧
        ∀ R', Adm L X M obs R' → DecLeOn L.D M C R' R → DecLeOn L.D M C R R')

theorem defaultZone_byDefault_sound {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (r : VE.Norms.Regulated) (hr : r ∈ L.U.D.T.regulated)
    (vs : List α) (typed : VE.TupleTyped M.asStructure r.sorts vs)
    (proposed : List (List ((String × List α) × Bool))) (b : Bool) (w : List ((String × List α) × Bool))
    (hz : defaultZoneOf L X M record obs r vs proposed = .byDefault b w) :
    ByDefaultZ L (X.map (·.2)) M record obs r vs b

theorem defaultZone_leftTo_sound {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (r : VE.Norms.Regulated) (hr : r ∈ L.U.D.T.regulated)
    (vs : List α) (typed : VE.TupleTyped M.asStructure r.sorts vs)
    (proposed : List (List ((String × List α) × Bool))) (differ : List (String × List α))
    (w₁ w₂ : List ((String × List α) × Bool))
    (hz : defaultZoneOf L X M record obs r vs proposed = .leftTo differ w₁ w₂) :
    ByDefaultLeftTo L (X.map (·.2)) M record obs r vs ∧ ∀ a ∈ differ, a.1 ∈ decisionNames L.D

theorem defaultZone_notSaid_sound {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (r : VE.Norms.Regulated) (hr : r ∈ L.U.D.T.regulated)
    (vs : List α) (typed : VE.TupleTyped M.asStructure r.sorts vs)
    (proposed : List (List ((String × List α) × Bool))) (w₁ w₂ : List ((String × List α) × Bool))
    (hz : defaultZoneOf L X M record obs r vs proposed = .notSaid w₁ w₂) :
    (∃ R₁ R₂, DefaultCompletion L (X.map (·.2)) M record obs R₁ ∧ DefaultCompletion L (X.map (·.2)) M record obs R₂ ∧
      OutcomeIn L.U M R₁ r vs ∧ ¬ OutcomeIn L.U M R₂ r vs) ∧
    ¬ ByDefaultLeftTo L (X.map (·.2)) M record obs r vs

theorem defaultZone_noCompletion_sound {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (r : VE.Norms.Regulated) (vs : List α)
    (proposed : List (List ((String × List α) × Bool))) (labels : List String)
    (hz : defaultZoneOf L X M record obs r vs proposed = .noCompletion labels) :
    ¬ ∃ R, DefaultCompletion L (X.map (·.2)) M record obs R

/-- The exception atoms true in every default completion, from the same complete enumeration as `defaultZoneOf`;
    `none` when that enumeration is not complete (the budget, or a branch left unknown) or finds no default
    completion. "The facts here force <e>" is rendered only from a `some` list. -/
def forcedAllOf {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (proposed : List (List ((String × List α) × Bool))) : Option (List (String × List α))

theorem forcedAll_sound {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (proposed : List (List ((String × List α) × Bool)))
    (fs : List (String × List α)) (hf : forcedAllOf L X M record obs proposed = some fs) :
    (∃ R, DefaultCompletion L (X.map (·.2)) M record obs R) ∧
    ∀ a ∈ fs, (∃ ss, (a.1, ss) ∈ VE.SoftNorms.exceptedDecisions L.D ∧ a.2 ∈ VE.NormDefaults.allTuples M ss) ∧
      ∀ R, DefaultCompletion L (X.map (·.2)) M record obs R → R a.1 a.2

/-- The finite minimal-subcompletion lemma: below every admissible completion that agrees with the observations
    there is a default completion (so it lacks every decision atom the first one lacks). -/
theorem defaultCompletion_below {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula)
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (R : String → List α → Prop)
    (hR : AdmissibleCompletion L.U X M (openNames L) (record ++ switchesOffRecord L.D M record) R)
    (ho : Observed L.U M obs R) :
    ∃ R', DefaultCompletion L X M record obs R' ∧ DecLe L.D M R' R

/-- "The facts here force <e>": a decision atom true in every default completion is true in every admissible
    completion that agrees with the record and the observations. Proved in the stub from `defaultCompletion_below`. -/
theorem forced_everywhere {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula)
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (a : String × List α) (ha : a ∈ decisionAtoms L.D M)
    (hall : ∀ R, DefaultCompletion L X M record obs R → R a.1 a.2) (R : String → List α → Prop)
    (hR : AdmissibleCompletion L.U X M (openNames L) (record ++ switchesOffRecord L.D M record) R)
    (ho : Observed L.U M obs R) : R a.1 a.2

/-- DE10's first form ("no exceptions here …", `short`) only when every decision atom the record leaves open is an
    exception; otherwise the second ("no assumptions here …", `long`). -/
def zoneForm {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) : Form :=
  if (openAtomsAll L M (record ++ switchesOffRecord L.D M record)).all (fun a =>
      !(decisionNames L.D).contains a.1 || (VE.SoftNorms.exceptedDecisions L.D).any (·.1 == a.1))
  then .short else .long

theorem defaultZone_budget {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (r : VE.Norms.Regulated) (vs : List α)
    (proposed : List (List ((String × List α) × Bool))) (n k : Nat)
    (hz : defaultZoneOf L X M record obs r vs proposed = .unknown (.budget n k)) :
    n = (openAtomsAll L M record).length ∧ k = maxDefaultAtoms ∧ maxDefaultAtoms < n

def noExceptionRecord {α : Type} (D : SoftDoc) (M : VE.FiniteModel α) : List ((String × List α) × Bool) :=
  (VE.SoftNorms.exceptedDecisions D).flatMap (fun (n, ss) =>
    (VE.NormDefaults.allTuples M ss).map (fun vs => ((n, vs), false)))

/-- With no switch and no `outweighs` decision, the decision atoms are exactly the atoms of weighing's record.
    Proved in the stub (`simp`). -/
theorem decisionAtoms_none {α : Type} (D : SoftDoc) (M : VE.FiniteModel α)
    (hnone : offDecisions D = [] ∧ outweighsTriples D = []) (a : String × List α) :
    a ∈ decisionAtoms D M ↔ a ∈ (noExceptionRecord D M).map (·.1)

theorem defaultZone_eq_noException {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula)
    (M : VE.FiniteModel α) (r : VE.Norms.Regulated) (vs : List α) (b : Bool)
    (hnone : offDecisions L.D = [] ∧ outweighsTriples L.D = [])
    (hadm : ∃ R, AdmissibleCompletion L.U X M (openNames L) (noExceptionRecord L.D M) R) :
    ByDefaultZ L X M [] [] r vs b ↔ SettledZ L.U X M (openNames L) (noExceptionRecord L.D M) r vs b
```

`defaultZone_eq_noException` needs no condition on the sufficient conditions (draft 1's `hsuff` and
`noSufficientHolds` are deleted). Under `hnone`, `switchesOffRecord L.D M [] = []`, and by `decisionAtoms_none` the
decision atoms are exactly the atoms of `noExceptionRecord`. `hadm` gives a completion R₀ with no true decision, and R₀
is admissible with the empty record. Every `DefaultCompletion` R has `DecLe R₀ R`, so minimality gives `DecLe R R₀`:
every decision of R is false, and R meets `noExceptionRecord`. Conversely, a completion that meets `noExceptionRecord`
has every decision false, so it is minimal. The two sets of completions coincide, which gives the equivalence. DF-ξ′
(8.6) shows that `hadm` is needed.

DF-5's soundness theorems (`defaultZone_*_sound`, `forcedAll_sound`) are provisional until WG-6 exposes the
enumeration over a given atom list (plan section 11, issue 1). `defaultCompletion_below` and `forced_everywhere` do not
depend on it.

Two notes on `cone_minimal_iff`.

- **Why it is true.** Splicing along an independent `C` keeps admissibility, so the decision order factors over `C`
  and the rest. A completion minimal globally is minimal on `C`. Conversely, a cone-minimal assignment extends to a
  completion minimal among those that agree with it on `C`, and splicing shows that this completion is minimal
  globally.
- **What it needs before pruning.** Cone pruning (`coneValuesO`) is enabled only after this theorem is proved and
  three more things hold: a computed check proved to imply `ConeIndependent`, the observations' and the query's atoms
  in `C` (`QueryIn`), and a review. DF-γ's query cone fails `ConeIndependent` (8.6). Containing the observations' atoms
  is not enough.

### 7.6 WG-1's interface (copied from the weighing stub) and DF-6

```lean
namespace VE.Weighing
open VE.SoftNorms (SoftDoc)
inductive CondKind | necessary | sufficient
  deriving DecidableEq, Repr
inductive Target
  | outweighs (act lower higher : String)
  | off (rule party : String)
  deriving DecidableEq, Repr
structure CondDecl where
  target : Target
  kind : CondKind
  condition : VE.Formula
structure WeighEnv where   -- WG-1's also has `factors` and `grants`; DF-6 reads neither
  always : List (String × String)
  conditions : List CondDecl
structure WeighDoc where   -- WG-1's also has `split`
  D : SoftDoc
  W : WeighEnv
end VE.Weighing

namespace VE.Defaults
open VE.Norms (bindAll anyF)
open VE.SoftNorms (SoftDoc outweighsF actSortsOf outweighsTriples)

def sufficientOverrides (Wd : VE.Weighing.WeighDoc) : List (String × String × String × VE.Formula) :=
  Wd.W.conditions.filterMap (fun c => match c.kind, c.target with
    | .sufficient, .outweighs a L H => some (a, L, H, c.condition)
    | _, _ => none)

def dfltRankingW (Wd : VE.Weighing.WeighDoc) : List (String × VE.Formula) :=
  (outweighsTriples Wd.D).map (fun (a, L, H) =>
    let conds := (sufficientOverrides Wd).filterMap (fun (a', L', H', C) =>
      if a' == a && L' == L && H' == H then some C else none)
    ("default:ranking:" ++ L ++ ":" ++ H ++ ":" ++ a,
     bindAll (actSortsOf Wd.D a)
       (if conds.isEmpty then .not (outweighsF Wd.D a L H) else .implies (outweighsF Wd.D a L H) (anyF conds))))

theorem dfltRankingW_empty (Wd : VE.Weighing.WeighDoc) (h : sufficientOverrides Wd = []) :
    dfltRankingW Wd = (dfltLabelled Wd.D).filter (fun a => a.1.startsWith "default:ranking:")
```

`default_entails_minimal_weigh` gets its statement after WG-1's review (plan 3.7). Weighing's premises name decisions,
so `replacementSafe` fails, and the theorem needs weighing's own replacement argument. Until DF-6 lands, `weighing@0`
documents get diagnostic 1.

### 7.7 Files

| Batch | File | Section |
|---|---|---|
| DF-1a | `lean/VE/Defaults/Premises.lean`, `Wire.lean`, `Examples.lean` (the fixtures of 8.1 to 8.4 as `#guard`s) | 7.1, 7.2 |
| DF-2 | `lean/VE/Defaults/Meaning.lean` (with DF-π's two `example`s) | 7.3 |
| DF-3 | `lean/VE/Readings/DefaultVerdicts.lean` | 7.4 |
| DF-5 | `lean/VE/Defaults/Zone.lean`, `ZoneExamples.lean` | 7.5 |
| DF-6 | `lean/VE/Defaults/Premises.lean`, `Meaning.lean` | 7.6 |

### 7.8 What the stub proves

The proofs come from the stub's `#print axioms` lines, run against the build of `rd-9/integrate` (`propext`,
`Classical.choice` and `Quot.sound` only, no `sorryAx`):

- **Proved outright (12):** `entailsX_mono`, `strict_of_withoutDefaults`, `premisesX_split` (checklist item 3: the
  split matches RD-9's `premisesX` order), `basis_needs_sound`, `defaults_follows_gated`, `choiceX_softX`,
  `choiceU_soften` (`rfl`), `dSem_entails` (`Iff.rfl`), `default_conflict_is_gate`, and, new in draft 2,
  `cohPremiseU_selU` (`rfl`), `elaborateRows_eq` (`rfl`) and `decisionAtoms_none`. In addition, `foldG_all_sound`
  elaborates at `dSem` as an `example`.
- **Proved modulo `dflt_wellFormed` and `defaultCoherenceCheck_sound` (3):** `assumptions_sound`,
  `basis_strict_sound` and `defaults_certificate_sound`. The composition of the wire theorem from the batch's lemmas
  is therefore checked.
- **Proved modulo one stated lemma or body (8, new in draft 2):** `viewOf_layered` (from `viewOf`'s body; `sorryAx`
  enters only through `viewRest` and `decodeLayered_soften`), `forced_everywhere` (modulo
  `defaultCompletion_below`), and DF-3's six wire theorems `readings_wire_default_present`, `_verdicts_all`,
  `_verdicts_none`, `_verdicts_some`, `_conflict_free` and `_conflict` (modulo `d_rowsHold`, and `replayVerdictsD`
  for the statements that name it).
- **Proved for the stub's dispatch shape:** `defaultsCase_other`. It holds for any body that tests the `defaults-`
  prefix first.
- **Stated only:** `dflt_wellFormed`, `defaultCoherenceCheck_sound`, `pairChecks_sound`, `collision_sound`,
  `collisionTuple_some`, `cohU_rank_valid`, `collision_unranked`, `followsForm_short`, `questionDiag_none`,
  `decodeLayered_soften`, `defaults_coherence_sound`, `defaults_model_sound`, `forcedAt_sound`, `replace_admissible`,
  `defaultBase_of_dflt`, `default_entails_minimal`, `default_entails_minimal_of`, `defaults_model_default_base`,
  `d_rowsHold`, `d_bases_sound`, `cone_minimal_iff`, `defaultZone_byDefault_sound`, `defaultZone_leftTo_sound`,
  `defaultZone_notSaid_sound`, `defaultZone_noCompletion_sound`, `defaultZone_budget`, `forcedAll_sound`,
  `defaultCompletion_below`, `defaultZone_eq_noException` and `dfltRankingW_empty`.

## 8. Acceptance fixtures, computed

### 8.0 Method

Unless a fixture says otherwise, the frame is one sort, `assistant`, and the act X. `x_required` is an `unspecified`
obligation whose dual is `x_permitted`, and `x_permitted` is an allow-by-default permission. Guards are `⊤`. The
profiles are `norm-defaults@0`, `norms@0`, `relational-fol@0` and `soft-norms@0`, and the decider is `assistant`. Each
document is decoded by the real `decodeSoftU`.

"One-element" means one entity per sort. The stub runs every one-element situation: every subset of the base and
decision atoms, and every filling. For each one it applies RD-9's `modelCheckX` with `localFree` (the situation has an
expansion). This check is **complete** for these documents. Every premise and every conclusion checked is universal
over one tuple of variables, and every predicate takes exactly that tuple. A countermodel therefore restricts to the
one-element substructure at a failing tuple, and universal premises hold on substructures.

It is not complete for a conclusion that an empty domain falsifies, such as `⊥`: a model of `⊥` may have an empty
domain. Draft 2 therefore also checks the empty-domain situation on the wire (`situationX` with every sort empty, then
`xModelOk`) wherever a claim rests on a model of `⊥`: DF-γ, DF-ι, DF-σ and F-DF1′ (R1). `assumptions` is computed by `usedLabels` with that complete semantic check in place of a certificate check. It is the
set a certificate keeps when the certificate needs no more, and DF-1a records the certificate's own set (*derived*).
Named situations are also checked on the wire: `situationX`, `decodeFilling` and `xModelOk`.

### 8.1 DF-1a's synthetic fixtures

| # | Document | Question | Computed |
|---|---|---|---|
| DF-α | r1 "Every assistant should X." (default, no condition) | `∀a. x_required(a)` | `Dflt_T` = `[default:exception:r1 : ∀a. excepted_r1(a) → ⊥]`. No colliding pair. Strict: does not follow, and the strict countermodel {excepted_r1}, filling no, checks on the wire (`xModelOk` true). The default model {} checks on the wire with `forced = []`. FOLLOWS, basis **needs**, form **short**, assumptions `[default:exception:r1]`. Rows DE1 + DE2. `decidersOf` = `[assistant]` |
| DF-α′ | DF-α without a strict model, or with the strict model {} (which does not check: `xModelOk` false, since the conclusion holds there) | as DF-α | basis **unsettled**, never `needs`. Rows DE1 + DE2 + DE12 |
| DF-β | DF-α with r1's exception "when that assistant is urgent" (sufficient: `urgent(x)`) | (i) `∀a. x_required(a)`; (ii) `∀a. ¬urgent(a) → x_required(a)` | `Dflt_T` = `[∀a. excepted_r1(a) → (⊥ ∨ urgent(a))]`. (i) DOES-NOT-FOLLOW: the default countermodel {urgent, excepted_r1} checks on the wire with `forced = [(r1, 0, a)]` (condition 0 is `urgent`). Rows DE6′ + DE11 "The text's own exception to rule r1 applies here: that assistant is urgent.", never DE6. (ii) FOLLOWS, basis needs (strict countermodel {excepted_r1}), form **long**, assumptions `[default:exception:r1]`. Rows DE1′ + DE2′. `Dflt_T`'s premise is false on {excepted_r1} and true on {urgent, excepted_r1} |
| DF-γ | r1 "should X", r2 "should not X" (on `x_permitted`), both default, unranked | `∀a. x_required(a)` | colliding pairs `[(r1, r2)]`. The gate fails: no pair certificate checks (`defaultCoherenceCheck` is false with `[none]` and with `[]`), and the collision at the situation with no exception and no filling checks (`collisionCheck` true; `collisionTuple` = the assistant; `giveWayDeciders` = `[assistant]`). No one-assistant situation admits `defaultX` (0 of the one-element bases, against 5 for `X`). The empty-domain situation does: it is an accepted consistency witness on the wire (`xModelOk U (defaultX D X) [] [] ⊥ m false` true), and the conclusion holds there. So the gate regression sends that model and a bound certificate (*derived*: `defaultX` entails the conclusion), `certOk` and `modelOk` hold, and only the gate keeps the answer from FOLLOWS. UNKNOWN (with no exception, rules r1 and r2 conflict), whether or not a certificate was sent (R4). Rows DE7 + DE7a "Which rule gives way is left to the assistant." |
| DF-γ′ | (new) DF-γ with r2's exception decided by the operator | as DF-γ | the same collision at {}. `giveWayDeciders` = `[assistant, operator]`: DE7b "Whether rule r1 gives way is left to the assistant, and whether rule r2 gives way is left to the operator." `decidersOf` = `[assistant, operator]` |
| DF-δ | DF-γ with r1 at rank safety and r2 at rank helpfulness, safety outranking helpfulness, holistic | `∀a. x_required(a)` | `Dflt_T` labels `[default:exception:r1, default:exception:r2, default:ranking:helpfulness:safety:x_permitted]`. The gate passes (rank-resolved). FOLLOWS, basis needs (the first strict countermodel found is {outweighs}), form **long**, assumptions `[default:exception:r1, default:ranking:helpfulness:safety:x_permitted]`. Rows DE1′ + DE2 + DE4, never DE1 |
| DF-δ′ | DF-δ with the strict flag | as DF-δ | `Dflt_T` labels `[default:exception:r1, default:exception:r2]` (no `outweighs` decision). FOLLOWS, needs, form **short**, assumptions `[default:exception:r1]`. Rows DE1 + DE2 |
| DF-ε | r1 "should X", alterable by `user` | `∀a. x_required(a)` | FOLLOWS, needs (strict countermodel {off_r1_user}), form **long**, assumptions `[default:exception:r1, default:switch:r1:user]`. Rows DE1′ + DE2 + DE3, never DE1 |
| DF-ζ | r0 "Every assistant must X." (strict) and r1 "should X" (default) | `∀a. x_required(a)` | strict: follows. FOLLOWS, basis **strict**, assumptions `[]`, `decidersOf` = `[assistant]`. Row DE5 "This holds whatever the assistant decides." |
| DF-ζ0 | r0 alone | as DF-ζ | `Dflt_T` = `[]`, basis strict. DE5 is not shown (F-DF1's case) |
| DF-η | DF-α, premise `∃a. excepted_r1(a)` | — | diagnostic 3: "… it states whether rule r1's exception applies" |
| DF-θ | DF-α with `weighing@0` | any | diagnostic 1 (a profile check; the stub computes no weighing document) |
| DF-ι | DF-β, premises `∃a. urgent(a)` and `∀a. ¬urgent(a)` | `∀a. x_required(a)` | entailment from `defaultX` holds vacuously, and no model exists, the empty domain included (`∃a. urgent(a)` fails there; computed on the wire, R1: unaffected). UNKNOWN (no checked situation where the premises hold with no exception), never FOLLOWS |
| DF-κ | DF-α | — | the default kind binds 5 premises (`premisesX U (defaultX D X) []`) against the strict kind's 4: exactly the one `Dflt_T` premise more. A certificate bound to the strict list, or to a list with one premise added, is refused by `bindCertX`, so the certificate is absent. DF-α has no colliding pair (the gate passes with `[]`, computed) and its default model checks, so the status is UNKNOWN (no certificate). The certificate itself is *derived* (recorded by DF-1a) |
| DF-λ | plain `instructs(operator)`, `unspecified`; g1 "Every operator instructs, unless an exception applies." (default, decided by the operator) | `∀o. instructs(o)` | strict countermodel {excepted_g1}. FOLLOWS, needs, form short, assumptions `[default:exception:g1]`. DF-4's parse and print are DF-4's fixtures. The value is computed on the decoders; through `ve document` on `main` this document (and the plan's spelling `instructs_via_system_prompt`, the same rule) is refused at load until RD-9 SC-8 (phase 1, DF-0.4), and DF-4 runs those probe documents as its regression fixtures |
| DF-π | Astra's counterexample: DF-α with `x_permitted` also `unspecified` | `∀a. x_required(a)` | `Dflt_T` labels `[default:exception:r1]`, pair members `[x_required, x_permitted]`, `replacementSafe` true, no pair. FOLLOWS, needs, form short. The default model is {}, with the permission's gap filled **yes** (the filling no/no is not admissible with no exception). See 8.5 for the meaning theorem |
| DF-σ | (new; C1) two strict rules: "must X" and "must not X", `x_required` deny | `∀a. ⊥` | on the one-assistant situation `modelCheckX` gives `(true, false)`, but `localFree` is false and `xModelOk` is false. `EntailsX U X [] (∀a. ⊥)` holds, because every conflict-free situation has no assistant. Plan draft 2's `basis_needs_sound` would have concluded the opposite. With the empty domain checked on the wire (R1): `X` is consistent there, and `∀a. ⊥` holds there; the claim is unaffected |
| DF-ω | (new; R2) DF-δ, the request with its pair certificate missing (`[]` or `[none]`) and no collision | `∀a. x_required(a)` | `defaultCoherenceCheck` is false for both, and no collision exists on any one-element situation. `defaults-coherence`: UNKNOWN, pair (r1, r2) `unknown`, never COLLISION. `defaults-certificate`: UNKNOWN (no-exception coherence not checked), never FOLLOWS |

### 8.2 The "exactly when" claims, one fixture for each direction

| Claim | Holds | Fails |
|---|---|---|
| `Exc_T ++ Dflt_T`: an exception holds exactly where a stated condition holds | DF-β: {urgent, excepted} admissible, and its `Dflt_T` premise true | DF-β: {excepted} without urgent violates `Dflt_T`; {urgent} without excepted is not admissible with `X` (`Exc_T`'s sufficient premise) |
| form short exactly when every kept label is a bare exception | DF-α, DF-δ′, DF-λ, DF-π, P-1a to P-1c: short | DF-β (ii) (a condition), DF-δ (a ranking), DF-ε (a switch), P-3: long |
| DE6 exactly when `forced = []` | DF-α's default model: `forced = []` | DF-β (i): `forced = [(r1, 0, a)]` |
| basis strict exactly when no label is kept | DF-ζ: `[]`, strict | DF-α: one label kept, not strict |
| basis needs exactly when labels are kept and a strict countermodel checks | DF-α with its strict countermodel | DF-α′ (none sent, or one that does not check): unsettled |
| DE5 shown exactly when the basis is strict and `Dflt_T ≠ []` | DF-ζ | DF-ζ0 (`Dflt_T = []`) |
| the gate has three outcomes: checked coherence excludes collisions; a checked collision refutes coherence; without either, the status is UNKNOWN | COHERENT: DF-δ with its pair certificate (*derived*; no collision exists on any one-element situation). COLLISION: DF-γ, the collision at {} | UNKNOWN: DF-ω, no pair certificate and no collision; never read as coherent or as a collision |
| a checked collision's pair is unranked (DE7's "ranks neither") | DF-γ: `Comparable` false, and the coherence premise fails on some one-element situation | DF-δ, DF-δ′: `Comparable` true, and the coherence premise holds on every one-element situation (`cohU_rank_valid`'s evidence), so no collision exists |
| DE7a exactly when the two rules' deciders agree | DF-γ: `[assistant]`; DF-ρ's colliding choice: `[unstated]` (DE7a·u) | DF-γ′: `[assistant, operator]` (DE7b) |
| DE10's first form exactly when every open decision atom is an exception (`zoneForm`) | DF-μ, DF-μ′, DF-μ″: short | DF-δ at {a}: long (the ranking atom is open) |
| "The facts here force <e>" exactly for the exceptions in `forcedAll` | DF-μ: `forcedAll` = [g1's exception at o1] | DF-μ′, DF-μ″: `forcedAll` = [], although each default completion has an exception |
| `replacementSafe` | DF-π with `R = []`: true | DF-α with `R = [∀a. excepted_r1(a)]`: false |
| `questionDiag = none` exactly when the premises state facts only | DF-β, premise `∃a. urgent(a)`: none | DF-η (a decision); `∀a. x_permitted(a)` gives "it states the outcome x_permitted"; DF-ε's switch gives "it states whether user has turned rule r1 off"; DF-δ's ranking gives "it states whether the helpfulness consideration outweighs the safety consideration on x_permitted" |
| the default member present exactly when the strict conflict fold is FREE | DF-ν, DF-ρ: strict FREE, member present | DF-τ: strict CONFLICT, no member |
| `leftTo` exactly when two default completions with the same filling differ | DF-μ′: leftTo | DF-μ′b: the completions differ only in the filling, so notSaid |

### 8.3 Readings (DF-3), on RD-9's K1 (`VE.Readings.Examples`)

| # | Document | Question | Computed |
|---|---|---|---|
| DF-ν | K1: set rs1 = {strict "no-deception", default "no-deception"} on `avoid_required(agent, user)`, `unspecified` | `∀agent ∀user. avoid_required` | choices `[(rs1, 0)]`, `[(rs1, 1)]`. Strict rows: (rs1, 0) proved, (rs1, 1) refuted. Strict fold FREE, **SOME** (RD-9's value). Default rows: (rs1, 0) basis strict, (rs1, 1) basis needs with `[default:exception:no-deception]`. Default fold FREE, **ALL**. Row DE8, then (rs1, 1)'s DE2·u (no DE12: its basis is `needs`) |
| DF-ρ | K1 plus rs2 = {strict "help" on `+help_required`, default "permit-deception" on `−avoid_required`}; `WellFormedSD` true | as DF-ν | 4 choices, strict conflict fold FREE, strict SOME. Gate: only ((rs1, 1), (rs2, 1)) collides (no-deception, permit-deception, at {}). Default fold **CONFLICT**, from the gate only. Rows: RD-9's strict answer, then "Under <reading>: Rules no-deception and permit-deception conflict here unless one of them gives way: …" (DE7) for that one choice, never RD-9's contradiction wording. Both rules' exceptions are decided by `unstated` (`giveWayDeciders` = `[unstated]`), so DE7's last sentence is DE7a·u "The text names no one who decides which rule gives way." The default fold is UNKNOWN, and no other default sentence is shown |
| DF-τ | (new) K1 plus the fixed strict rule "allow-deception" on `−avoid_required` | as DF-ν | strict conflict fold **CONFLICT**, so no default member at all |
| F-DF2 | S1's K1 to K22, S2a's M1 to M20 | — | *derived*; DF-3 runs it |

### 8.4 Diagnostics, computed

| Input | Text |
|---|---|
| DF-α, premise `∃a. excepted_r1(a)` | `InvalidInput: a question that assumes no exception may state facts only; it states whether rule r1's exception applies` |
| DF-α, premise `∀a. x_permitted(a)` | `… it states the outcome x_permitted` |
| DF-ε, premise `∃a. off_r1_user(a)` | `… it states whether user has turned rule r1 off` |
| DF-δ, premise `∃a. outweighs(a)` | `… it states whether the helpfulness consideration outweighs the safety consideration on x_permitted` |
| DF-β, premise `∃a. urgent(a)` | none |
| the 15 soft fixture documents of 8.1, 8.6 and 8.7 (DF-α, β, γ, δ, δ′, ε, ζ, ζ0, π, λ, μ′, P-1a to P-1c, P-3) | diagnostic 4: none; diagnostic 6: none (`wellLabelled` true); diagnostic 7: none (`WellFormedSoft` true, and every premise of `X` checks at `envAt (fill U) 0`) |

### 8.5 The meaning theorem (DF-2), both sides on every one-element situation

Each row gives three values, in this order:

- **L**: `defaultX` entails the conclusion.
- **R**: the conclusion holds in every default base that has an expansion, with D15's varied filling.
- **R₁**: the same with draft 1's fixed filling.

| Fixture | gate | `replacementSafe` | L | R | R₁ |
|---|---|---|---|---|---|
| DF-α | passes | true | true | true | true |
| DF-β (i) | passes | true | **false** | **false** | false |
| DF-β (ii) | passes | true | true | true | true |
| DF-δ | passes | true | true | true | true |
| DF-δ′ | passes | true | true | true | true |
| DF-ε | passes | true | true | true | true |
| DF-ζ | passes | true | true | true | true |
| DF-π | passes | true | true | true | **false** |
| DF-γ | **fails** | true | true (no one-assistant situation admits `defaultX`; the empty domain does, and the conclusion holds there) | **false** | false |

So the equivalence holds in both directions on every fixture where the gate passes, including a case where both sides
are false (DF-β (i)). Its countermodel {urgent, excepted_r1} is a default base, because the exception is forced. Two
rows show why the hypotheses are needed:

- DF-γ shows that the gate is needed: this is DF-2's seeded bug "stated without `hcoh`".
- DF-π shows that draft 1's fixed filling makes the theorem false. `B_π` = {excepted_r1}, fillings no/no, is a default
  base with the filling fixed and is not one with the filling varied. The competitor {} with the permission's gap
  filled yes is admissible, and the competitor {} with fillings no/no is not. These are DF-2's two `example`s.

### 8.6 At one situation (DF-5), by the full enumeration over `openAtomsAll`

| # | Document and situation | Computed |
|---|---|---|
| DF-μ | DF-λ at {o1, o2}, observed `instructs(o1)` = no | 4 open atoms. The default completions are **two**, with the same decisions {excepted_g1 at o1}; they differ only in the unsaid atom at o2, which changes no answer. Zone at o2: **by default yes**; at o1: **by default no**. `zoneForm` short (every open decision atom is an exception), `forcedAll` = [g1's exception at o1]. Rows DE10 "With no exceptions here that could be dropped, alone or together, …", then DE10f "The facts here force the exception to rule g1 for o1." Seeded bug "compare unsaid atoms too": both answers unchanged, so this fixture does not catch it (DF-μ′b does) |
| DF-μ′ | plain `p` (`unspecified`), r1 (+, guard `cond_a`), r2 (−, guard `cond_b`), unranked, at {a} with both guards | **leftTo**, with 4 default completions: r1 excepted or r2 excepted, two fillings each. `zoneForm` short; `forcedAll` = []: neither alternative exception is forced. Rows DE10″, each completion's exception as DE13, no DE10f. Seeded bug "forced read from one default completion": reports r2's exception as forced |
| DF-μ′b | (new) DF-μ′ with neither guard | **notSaid**, with 2 default completions differing only in the filling. Seeded bug "compare unsaid atoms too": **by default no** |
| DF-μ″ | DF-γ at {a}, zone of `x_permitted` (replaces plan draft 2's impossible document; C12) | full enumeration: **leftTo** (3 default completions). Seeded bug "minimality over the query's cone only" (the cone is {excepted_r2}): **by default no**. `ConeIndependent` fails both for the cone {excepted_r2} and for {excepted_r1, excepted_r2}, because `Coh_T` ties the two exceptions and `Fill_T` ties them to the unsaid tables. In DF-μ, the atoms at o2 are independent of those at o1 (true). `zoneForm` short; `forcedAll` = []: neither alternative exception is forced (seeded bug "forced read from one default completion" reports r2's) |
| DF-δz | (new; R15) DF-δ at {a}, nothing observed, zone of `x_required` | **by default yes**: 2 default completions, both with no decision, differing only in the filling. `zoneForm` long (the ranking atom is open), so DE10′ "With no assumptions here that could be dropped, alone or together, …"; `forcedAll` = []. The strict countermodel {outweighs} has no exception either, and gives **no** (the ranking reversal changes the result); it is not a default completion, because its one true decision can be dropped. Seeded bug "minimality over exception atoms only" keeps it: **leftTo** (3 completions). This is the regression that DE10's first form must not be used here |
| DF-π′ | DF-π at {a}, nothing observed | **by default yes** (2 default completions with no decision). Seeded bug "draft 1's fixed filling": **notSaid** (it keeps {excepted_r1} with no/no) |
| DF-ξ | Z-ε's shape: DF-α at {a} | by default yes, and weighing's settled answer under `noExceptionRecord` is yes; `hadm` holds (a completion meets the record). Without the record weighing's answer is not settled. DF-π at {a}: by default yes, settled yes, `hadm` holds |
| DF-ξ′ | (new in draft 1; recomputed, R14) DF-β at {a} with `urgent(a)` | `hadm` fails: no completion meets weighing's record "no exception", because the stated condition forces the exception. Zone of `x_required`: **notSaid** (the exception is forced; `x_required` is then a gap), and weighing's record gives **no completion**, so both sides of `defaultZone_eq_noException` are false there. Zone of `x_permitted`: **by default yes**, and weighing's record again gives **no completion**: the left side holds and the right side does not. So the theorem needs `hadm`. Draft 1 attributed this to `hsuff`, which draft 2 deletes |
| budget | DF-λ at 13 operators | 26 open atoms > 12: **unknown (budget 26)** |

### 8.7 From the pilots

| # | Unit | Computed (standalone analogue in the frame of 8.0) | On `CE4` |
|---|---|---|---|
| P-1a | u0036.s05 "Claude should ask for clarification in cases of genuine ambiguity." | `∀a. genuine_ambiguity(a) → clarification_required(a)`: strict does not follow; FOLLOWS, needs, short, `[default:exception:ask-clarification]` | *derived*, DF-1b |
| P-1b | u0156.s03 "Claude shouldn't actively deceive the user about the existence of a system prompt or its content." | `∀a. ¬prompt_deception_permitted(a)`: FOLLOWS, needs, short, `[default:exception:no-prompt-deception]` | *derived*, DF-1b |
| P-1c | u0263.s04.p2 "… in situations where Claude has explicitly been instructed not to engage in unintended exploits, it should comply." | `∀a. told_no_exploits(a) → exploit_compliance_required(a)`: FOLLOWS, needs, short, `[default:exception:comply-no-exploits]`, decider `unstated`: DE1 + DE2·u | *derived*, DF-1b |
| P-1 | the pilot number | the standalone analogues go from no answer to "unless an exception applies, the conclusion follows" for **3 of 3** | measured by DF-1b's probe; the "no answer" side is DF-0.3's baseline on `CE4` (deferred in phase 1 until `rd-9/integrate` is on `main`, recorded before DF-1b merges) |
| P-3 | u0073.s05 (one default rule, three sufficient conditions: unsafe, unethical, against guidelines) | `∀a. ¬unsafe ∧ ¬unethical ∧ ¬against_guidelines → x_required`: FOLLOWS, needs, **long**, DE1′ + DE2′ listing the three. `∀a. x_required(a)`: DOES-NOT-FOLLOW; the countermodel {unethical, excepted_comply} has `forced = [(comply, 1, a)]` (condition 1, "unethical"): DE6′ + DE11 | *derived*, DF-1b |
| P-2, P-4, P-5 | as plan 4.2 | — | *derived*, DF-3, DF-4 |

### 8.8 Conservativity

F-DF0 (byte-identical answers for every existing kind, by `defaultsCase_other` and PK-1's table) and F-DF1 are
DF-1a's, run through the service. DF-ζ0 is F-DF1's shape: `Dflt_T = []` and basis strict.

F-DF1 compares only requests that carry an accepted consistency witness (a `model` that `xModelOk` accepts with
`defaultX` and `⊥`). On those, `defaults-certificate` gives FOLLOWS with basis strict exactly where
`norm-defaults-certificate` accepts the certificate. The existing route needs no consistency model and the new one
does (R6), so without the restriction the equivalence is false:

| # | Document | Premises | Computed |
|---|---|---|---|
| F-DF1′ | (new) DF-ζ0 with the base predicate `urgent` | `∃a. urgent(a)` and `∀a. ¬urgent(a)` (facts: `questionDiag` none) | `Dflt_T = []`. The strict entailment of `∀a. x_required(a)` holds vacuously, so `norm-defaults-certificate` accepts a bound certificate (*derived*). No consistency witness exists: none among the one-element situations, and the empty domain fails `∃a. urgent(a)` (computed on the wire). `defaults-certificate`: UNKNOWN (no checked situation where the premises hold with no exception) |

### 8.9 Seeded bugs, with the fixture each one fails

| Bug | Fails |
|---|---|
| `dfltOf` drops the sufficient-condition disjunct | DF-β (i): the mutation excludes its forced-exception countermodel {urgent, excepted_r1}, and the conclusion turns FOLLOWS (computed: it follows on every one-element situation, and the model {} remains). DF-β (ii) stays entailed under the mutation and is not the regression |
| `basisOf` always `.strict` | DF-α's basis |
| `basisOf` gives `.needs` without a checked strict model | DF-α′ |
| the strict model checked by `modelCheckX` without `localFree` | DF-σ (a countermodel with no expansion) |
| `followsForm` ignores switch labels | DF-ε's form |
| `forcedAt` returns `[]` | DF-β (i) (DE6 instead of DE6′) |
| `defaultsCase` answers FOLLOWS without the gate's certificates | DF-γ, sent with the empty-domain model (an accepted consistency witness) and a bound certificate: the mutant answers FOLLOWS, the correct answer is UNKNOWN (R1) |
| `CertReplay.reason` tests the certificate before the collision | DF-γ sent without a certificate: "no certificate" instead of the conflict |
| `defaults-coherence` answers COHERENT when no collision is supplied | DF-ω (UNKNOWN) |
| `default_entails_minimal` without `hcoh` | DF-γ (8.5) |
| `DefaultBase` with the filling fixed | DF-π (8.5) |
| `dSem.free` without the gate | DF-ρ (ALL instead of CONFLICT) |
| default member shown with the strict fold not FREE | DF-τ |
| the zone filter compares unsaid atoms | DF-μ′b |
| the zone filter compares only completions with the same filling | DF-π′ |
| the enumeration restricted to the query's cone | DF-μ″ |
| the zone filter compares exception atoms only, not rankings | DF-δz (leftTo instead of by default yes) |
| `forcedAll` read from one default completion | DF-μ′, DF-μ″ (r2's exception reported as forced) |
| `zoneForm` always short | DF-δz (DE10's exceptions form where a ranking is open) |

## 9. Review checklist (plan section 9, with this spec's references)

1. `dfltOf` and `dfltLabelled` (7.1) regenerate 3.1's premises, in that order, with soft's names and sorts (DF-α, DF-β,
   DF-δ, DF-ε computed).
2. `basis_strict_sound` and `basis_needs_sound` are true as stated. The latter is proved. DF-σ shows that plan draft
   2's form was false.
3. `premisesX_split` (proved).
4. `DefaultCoherent` checks against `Exc_T ++ R ++ Dflt_T ++ Fill_T` with no `Coh_T`, and its check is minimal (C6).
   The gate has three outcomes (DF-γ, DF-δ, DF-ω), and `defaults_coherence_sound` covers each verdict and each
   `resolved` pair.
5. `DefaultBase` and `DefaultCompletion` both use D15's comparison. Check that `replace_admissible` and
   `default_entails_minimal` are true under their hypotheses (8.5 computes both sides). DF-π and DF-γ are in 8.5. If
   the (→) proof is not confirmed, adopt `default_entails_minimal_of` (the fallback) and record it.
6. `defaultBase_of_dflt` needs no gate (DF-γ: L holds because no one-assistant situation admits `defaultX`, and (←)
   still holds).
7. `questionDiag` covers every regulated and decision predicate, and its texts name rules (8.4).
8. DE1 to DE13, with their `·u` variants: one reading each; the paraphrases have the same reading; the form, `forced`,
   decider and `zoneForm` rules hold in both directions (8.2). Each English claim has its theorem: DE6′ and DE11
   `forcedAt_sound`; DE7 `collisionTuple_some` and `collision_unranked`; DE10f `forcedAll_sound` with
   `forced_everywhere`.
9. The fixtures are as computed in section 8, and P-1 to P-3 are *derived* on `CE4`.
10. `defaultsCase_other`, F-DF0 to F-DF2, with F-DF1 restricted to requests with an accepted consistency witness
    (F-DF1′). The non-vacuity conjunct is RD-9's `ConsistentX` (C2), and `default_conflict_is_gate` is proved; check
    DF-ρ and DF-τ, and DF-3's six wire theorems (7.4).
11. No batch leaves a Python computation of anything section 7 defines.
12. DF-5's statements against WG-6 as reviewed. `cone_minimal_iff` over `ConeIndependent`, and no pruning before it is
    proved together with a computed independence check. `defaultZone_eq_noException` with DF-ξ, and DF-ξ′, which shows
    that `hadm` is needed; no `hsuff`.
13. C8 as settled by R12: `viewOf` through `decodeLayered`, `decodeLayered_soften`, and diagnostic 7.

## 10. Open items for the DRI

1. **The decoder's facts (C8): settled by the ruling (R12).** `viewOf` calls `decodeLayered` itself, takes `hU`
   from `decodeLayered_soften`, and checks `hD` and `hXw` as Booleans (diagnostic 7). No second decoder and no PK-1
   field.
2. **`cohU_rank_valid` is stated, not proved.** DE7's "The text ranks neither above the other" rests on it through
   `collision_unranked`. The stub's evidence is the one-element evaluation in 8.2. If DF-1a cannot prove it on
   `fill U`, DE7 drops that clause (the ruling's alternative), and DF-1a records it.
3. **Plan section 11's seven issues: decided** (DRI DF1 to DF7, plan 11.1). Issue 1 became DF1, merged with
   judgment-terms' JT-R1: WG-6's statement review states `zoneOf` over an explicit atom list `opens`. `defaultZoneOf`
   as typed in 7.5 is the statement to check that interface against, and `forcedAllOf` reads the same enumeration.
   7.5's copied WG-6 signatures are updated when WG-6's reviewed statement lands, not before.
4. **Phase 1's deferred items that touch this spec** (plan 0.1, 0.2). None changes a statement. DF-0.3 (the baseline)
   supplies P-1's and P-2's "before" values in 8.7. DF-0.1 (the blind reader) bears only on DF-4's byte estimate and
   DF-E2, neither of which this spec states. DF-E3's re-run decides whether a specificity suggestion exists at all (6);
   if it does, its statement is a later draft's.
