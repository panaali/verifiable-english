# Weighing competing considerations (`weighing@0`): buildable plan

## Changes in this draft

Draft 5 (2026-10-13) applies phase 1, [weighing-phase1.md](../research/weighing-phase1.md) (reviewed FIX in
`manage-agents/weighing-ph1-review.final.md`, fixed in `weighing-ph1-fix.final.md`). No Lean statement, wording,
diagnostic or fixture changes, and the cross-plan edits are kept as written.

- **WG-E1: FAIL.** 1 of 40 sampled CROSSACT units is two exclusive positive acts (the bar is 8), and none would change
  a checked answer (the bar is 5). WG-E1's row, its section and D14 record the result.
- **WG-10: closed** by WG-E1. Its text is kept as history. No exclusive-act construct is planned; 2.7 and 8 make
  collisions between different acts residual.
- **WG-0: DEFERRED.** Trigger: RD-9 SC-8 on `main`, not met on 2026-10-13. Otherwise unchanged; its pilot effect is
  still "measured by WG-0".
- **Status after phase 1** (5.0): every batch and experiment with its result or trigger, and what it gates.
- **Measured numbers** (7): WG-E1's counts and the sampled bytes by class. WG-10's measured effect is 0 B of checked
  answers.
- **Refusal units** (8): the three sampled units that name refusing need AP's act identity, not a weighing construct.
- **Not tested by phase 1, unchanged:** WG-1 to WG-9, WG-E2 and research 4.7.
- **Cross-plan:** the synthesis still names WG-10 as `alternatives@0`'s consumer (edits 7 and 10, SYNTHESIS O9, 2.9
  and C17). That text is kept here; the conflict is in "Cross-plan issues for the DRI" at the end.

> Status: plan draft 5 (2026-10-13), branch `research/weighing-p1`; draft 4 was on `design/weighing` from `main` at
> `49de179e`. Draft 5 applies phase 1's results ([weighing-phase1.md](../research/weighing-phase1.md)): WG-E1 FAIL,
> WG-10 closed, WG-0 DEFERRED. Research wave of 2026-10-12 (DRI). Draft 1 (2026-10-12) was reviewed by Astra and Fable (`manage-agents/debates/design-weighing/`,
> converged in round 3 on REVISE to draft 2) and by the cross-plan review of 2026-10-13
> (`manage-agents/debates/plan-synthesis/SYNTHESIS.md`, whose ten edits for this plan settle the debate's one open
> item). Draft 2 carries both; its only other changes are pointers to WG-1's statement spec. Draft 3 carries the
> statement review of WG-1's spec (`manage-agents/debates/weighing-spec/`, verdict FIX, settled by `DRI-RULING.md`,
> items 1 to 14), synchronised with [weighing.md](weighing.md) draft 2; it changes no frozen W1, soft or P0
> semantics. Draft 4 carries the bounded re-check of weighing.md draft 2 (`manage-agents/weighing-p3ver1.final.md`,
> FAIL on ruling item 1), synchronised with weighing.md draft 3: the second accepted document that falsifies
> `strength_iff`'s unrestricted statement (4.1, W-α); it changes no statement. It is the plan for the
> design recommended in [docs/research/weighing.md](../research/weighing.md) (cited here as `research n`), which must
> be read first for the prior art and the comparison of candidate designs. Research section 2 (the measured need) is
> filled only in 2.1, the CROSSACT class written for WG-E1 before its draw, and section 5 is still a placeholder.
> So every claim draft 1 cited from them (unit ids, byte estimates) stays withdrawn below and is marked where it
> stood. Planning only: no code, proof, test or generated file changed, and no model was called for this draft (phase
> 1 made one, WG-E1's second reader, saved as evidence). The Lean blocks below are the plan's statements; WG-1
> elaborated them in an untracked stub, and the item-1 statement specification [weighing.md](weighing.md) holds the elaborated statements for WG-2 to WG-5, the fixture
> values computed in Lean and the stub's findings. Numbers are measured (the method is named beside each) or labelled
> *estimate*.
>
> Inputs: [soft-norms.md](soft-norms.md) (cited `soft n`), [soft-norms-PLAN.md](soft-norms-PLAN.md),
> [norm-defaults.md](norm-defaults.md), [lean/SOFT-NORMS.md](../../lean/SOFT-NORMS.md),
> [lean/NORMDEFAULTS.md](../../lean/NORMDEFAULTS.md), RD-9's plan `docs/spec/rd-9-soft-chain-PLAN.md` on
> `design/rd-9` and its build on `rd-9/integrate` (`LayeredEntail.lean`, `LayeredAdmission.lean`), [VISION.md](../../VISION.md)
> (the converged rule "elaborate by default", items 1, 2, 5 and 8), `lean/VE/SoftNorms/{Tree,Soften,Semantics}.lean`,
> `lean/VE/NormDefaults/{Premises,Layered,Evidence,Routes}.lean`, the pinned constitution and UDHR pilots of
> run `20261012T1800Z`, SYNTHESIS.md's shared items PK-1 (premise packs), AR-10 (profile-gate table), QS-1 (order
> closure), AP's split map and the hard-constraint queue, and phase 1's report
> [weighing-phase1.md](../research/weighing-phase1.md) with its evidence in `docs/research/evidence/weighing/`.

## 0. Summary

The constitution asks Claude to weigh: four values in an order that is "holistic rather than strict", costs against
benefits, operators' wishes against users' interests, and almost every "should" is a default that judgment can set
aside. VE already has the right stance for this (`soft-norms@0`, merged and proved): weighing is a set of **named open
decisions** (is this rule's exception met here? does the lower-ranked consideration outweigh the higher one here? has
this party switched the rule off?), and the checker certifies the *structure* around them, never the weighing itself.

This plan extends that stance in two directions, both inside VE's rules (one reading per sentence, plain English, Lean
owns meaning, a new profile that changes no existing answer, honest UNKNOWN):

1. **Constrain the open decisions** (`weighing@0`, batches WG-2 to WG-5). Four kinds of sentence the constitution uses
   and soft norms cannot say become one-reading English, each elaborated into a labelled base premise on an open
   decision, in PK-1's `weighing` pack of the layered route's extra premises `X`. No new semantics: `ValueSoft`,
   `soften` and `fill` are unchanged, and every existing check, certificate and theorem applies. Weighing constrains
   decisions that exist; it is not a conservative extension (8).
   - **Strength of a rank edge**: "Safety always outranks ethics." (never outweighed, and the same for every rank
     above safety against every rank below ethics) beside "Ethics outranks guidelines." (the holistic override,
     decided by the named decider; "Ethics generally outranks guidelines." is accepted as the same sentence and shown
     in the plain form).
   - **Conditions on an override**: "Helpfulness outweighs ethics on complying with an operator instruction only
     when …" (necessary) or "… when …" (sufficient), with factor lists.
   - **Conditions on a switch, and delegated switches**: "Users may turn off rule 7 only where the operator allows
     it." The checker also checks that a party never grants more than its own switches (:138, "operators cannot grant
     users more than operator-level trust"), and the grantee's switch carries every condition on the grantor's own.
2. **Say what the weighing decides, without doing it** (zone answers, batches WG-6 to WG-8). At a situation, for an
   act, Lean answers one of: **settled** whatever the open decisions are, claimed only with one admissible completion
   checked; **left to** a named decider, naming the questions the answer turns on; **not said** by the text
   (norm-defaults' gap); both of the last two together; **inconsistent at this situation**, naming the premises that
   refute every decision assignment (Lean enumerates them all and refutes each by a labelled premise); or
   **unknown** with the reason Lean checked (the budget it exceeded, or a branch it could neither refute nor
   confirm). The same machinery checks a **decision record** (a decider's findings in one situation): admissible,
   with the outcome it produces, or ruled out by named sentences of the document.

Two further pieces were planned as **experiments** with pre-registered bars (WG-E1, WG-E2). WG-E1 asked whether
collisions between *different* acts ("help" against "refuse") need a new construct beyond act identification. It ran
in phase 1 and **failed** its bar: 1 of 40 sampled units is two exclusive positive acts, and none would change a
checked answer (5.0, 7). So WG-10 is closed, and no exclusive-act construct is planned. WG-E2 asks whether worked
examples can bind a decider as precedents (Horty's a fortiori constraint, compiled into the same decision
conditions); it runs after WG-2. A holistic choice among explicit alternatives, numeric weights and a
defeasible-logic engine inside the checker are not planned (research 4, 5).

**The first batch that moves a pilot number** is WG-0: no product code, it writes the constitution's value order and
the hard constraints' immunity with what `soft-norms@0` already offers, once RD-9 lets a soft document sit beside
`norm-defaults@0` (RD-9 SC-8). Draft 1's estimate of its effect cited research 5.2, which is unfilled; the estimate is
withdrawn, and WG-0 measures. WG-0 is **DEFERRED**: on 2026-10-13 SC-8 is not on `main` (5.0).

## 1. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | Weighing stays a set of named open decisions with deciders. The checker certifies structure, bounds and coherence, and answers where the weighing matters; it never computes an "all things considered" verdict | VISION converged rule item 8 ("unconstrained weighing" is outside certification); soft 0; the source itself delegates the judgment ("we do want Claude to weigh these different priorities", :34) | an inside-the-checker weighing (numeric or argumentation-based), research 4.4 and 4.5 |
| D2 | A new profile `weighing@0` requires `soft-norms@0` and `norms@0`, registered as one row of AR-10's profile-gate table (`requires := ["soft-norms@0", "norms@0"]`, with the row's composition proof; `refuses := [rights@0]` until AR-10's composition proof and a fixture both cover that combination), with a new environment block `weighing` beside the vocabulary's `soft` block. `soft-norms@0`'s bytes, decoders, identities, statements and answers do not change; a document without the block is a soft document (WG-2 `weigh_conservative`) | VISION converged rule item 2 (meaning freeze; extensions are new profiles); soft 3.1's strict decoder rejects unknown fields, so the block cannot live inside `soft`; AR-10's table is the one place a profile is registered | new fields in the `soft` block; a `soft-norms@1`; hand-written profile registry rows |
| D3 | Every `weighing@0` construct is a **condition on an open decision**, elaborated into labelled base premises `Weigh_T`. `Weigh_T` is PK-1's `weighing` pack (`kind := .constraint`, `decls := []`, `labelled := weighLabelled Wd`, `origins`: each label ↦ the request path of its entry in the `weighing` block); PK-1 assembles X in its fixed order (soft, rights, weighing, attitudes, scales, events), and RD-9's `EntailsX`, `acceptanceX`, `conflictFreeCheckX_sound`, `modelCheckX_sound` apply to it. Weighing constrains existing decisions: its local checks guarantee `weigh_alone_base_free`, and there is no global conservativity claim (8) | soft's exception conditions (`Exc_T`) are already this shape; RD-9 proves the checkers sound for any typed `X`; PK-1 is the one assembler of X; so the only new proof obligations are typing, the meaning of the premises and conservativity at the wire | changing `ValueSoft` or `soften`; a second premise pipeline; an assembly of X in `Weighing/*` |
| D4 | **Strength.** A declared edge "a outranks b" may be marked `always`. A rank pair `(H, L)` with `H` above `L` is **strict** when some chain of declared edges from `H` down to `L` contains an `always` edge, and **holistic** otherwise; it is computed with QS-1's reachability (`strictPair H L := some always edge (a, b) with H at least a and b at least L`, `VE.Closure.Order.atLeast`). A strict pair contributes `∀x̄. ¬outweighs_{a,L,H}(x̄)` for every act `a` on which the pair's rules collide | one rule a reader can apply ("a lower rank can outweigh a higher one only if no step between them says *always*"); it is monotone both ways (`strictPair_down`, `strictPair_up`), so "safety always outranks ethics" also protects safety from guidelines and helpfulness; the closure is QS-1's, never weighing's own | strictness per declared edge only (it would let guidelines outweigh safety while ethics cannot, research 4.1); strictness only on the first edge; a rank closure in `Weighing/*` |
| D5 | `always` under the holistic flag removes the override; under the strict flag it is accepted and inert, with a warning (`StrengthInert`). A plain "a outranks b" keeps the flag's meaning. "a generally outranks b" is an input synonym of the plain sentence, shown as the plain sentence; under the strict flag the English layer refuses it (`GenerallyUnderStrictOutranking`). The wire carries only `always` edges | under the strict flag no `outweighs` decision exists (soft 1.3), and creating one would change `E′`, so `soft-norms@0`'s vocabulary would change; a strength with no formal effect on the wire would break the rule that every construct is a premise (debate E5) | creating `outweighs` atoms under the strict flag; a `generally` strength on the wire |
| D6 | **Override and switch conditions** have soft's exception-condition form: quantifier-free base formulas over the target's argument sorts, naming base predicates of `E` only; factor lists are strings with no premise. Weighing may constrain decisions, never the world on its own: a condition on an `outweighs` decision of a strict pair (D4's closure) is refused (`ConditionOnStrictPair`); a sufficient condition must be shown to imply each necessary condition on its target by a propositional check proved sound in Lean (`ConditionsDisagree`, text "the checker cannot show that condition i implies condition j"; sound, not complete; it never searches, so it never exhausts a budget); a sufficient condition on a switch is refused. A target that names a rule or act `acts@0` split is refused with AP's diagnostic ("name one of its parts"), read from AP's `VE.Acts.SplitMap`, never re-derived; a target may name a generated part | soft 3.2 and 6.1's fragment gate carry over unchanged, so `Weigh_T` stays in the universal function-free fragment; without the two checks a sufficient condition would make X certify a fact about the world (debate E2); AP owns act identity (synthesis edit 8) | conditions over regulated or decision predicates (circular and outside the fragment); a tableau search for the implication; re-deriving a split |
| D7 | **Delegated switches.** "<Party> may turn off rule n only where <grant>" is a necessary condition on `off_{n,party}`; a grant names its grantor, and the grantor must itself hold a switch on rule n (`DelegationExceedsGrantor`) and the grant's predicate must be attributed to the grantor (`GrantNotAttributed`). The grantee's switch also carries every necessary condition on the grantor's switch and the grantor's own grants, along the whole grant chain (`grant_within_grantor`); every inherited condition is written out in the English. A grant premise is the necessary `.off` case of the one condition generator (`condPremise`). Grant cycles, self-grants included, are refused (`DelegationCycle: rule <n>, <party>`), an explicit restriction of `weighing@0`, not a soundness necessity | :138; the bound is a structural check, decidable and stated as a theorem (`delegation_bounded`), and the inheritance carries :138's meaning, which the structural check alone does not (debate E3) | a general authority logic (research 4.6); a separate grant generator |
| D8 | **Zone answers** reuse norm-defaults' three-valued machinery (Kleene evaluation, cones, bounded enumeration, `kleene_sound`, `settled_of_enumeration`) with the set of *open* atoms widened from the unsaid atoms to the unsaid atoms and the decision atoms. The widening is made once, in its owner file `NormDefaults/Evidence.lean`, with today's functions as the instance "open = unsaid" (`rfl`) and the enumeration budget a parameter (norm-defaults keeps 12, zones use 16). The enumeration prunes the assignments that Kleene evaluation refutes against PK-1's whole assembled X and `Fill_T`, as `coneValues` already prunes by `Fill_T` | one owner of three-valued evaluation; norm-defaults' answers stay byte-identical; without pruning by X an outcome that only a weighing condition settles stays UNKNOWN (debate E1) | a second Kleene evaluator in `Weighing/`; Python enumeration; an enumeration that ignores X |
| D9 | A zone answer separates **left to <decider>** (two admissible decision assignments, same filling, opposite outcomes) from **not said** (norm-defaults' UNDECIDED: same decisions, two fillings) and carries both witness pairs when both hold. "Settled" is claimed only from a complete enumeration of the cone or a replayed certificate **and** one admissible completion checked by `modelCheckX`; without that completion the answer is UNKNOWN. With no admissible completion the answer is **inconsistent at this situation**, citing a premise Kleene evaluation refutes, or on every branch of a complete enumeration the premise that refutes it (labels recomputed by Lean, deduplicated and sorted), or UNKNOWN when neither holds, with the reason Lean checked: the budget exceeded (the enumeration incomplete), or a surviving branch it could neither refute nor confirm; never a budget after a complete enumeration | the constitution sends "unclear or uncertain" hard-constraint cases to "holistic and nuanced prioritization" (:457): today those come out UNDECIDED, which reads as "the text does not say", the wrong message; a "settled" with no admissible completion is vacuous | one UNDECIDED for both; settled without a checked completion |
| D10 | **Decision records** (a decider's findings in a situation) are checked with the zone machinery with the recorded atoms fixed: ADMISSIBLE with the outcome (and what is still open), RULED OUT with the violated premises' labels rendered as their sentences (no admissible completion agrees with the record, and Kleene evaluation refutes that premise with the record fixed, or on every branch of a complete enumeration), or UNKNOWN with its checked reason | this is the one place a checker can audit a judgment it does not make: consistency with the document's bounds, not correctness | judging whether the finding is right |
| D11 | **No new service mode.** A `weighing@0` document is a layered-route document: the layered decoder validates the original envelope and profiles (`weighGate`, before anything is stripped), hands the soft decoder the environment without the block (`stripWeighing`), decodes the block, checks `WellFormedWeigh` and gives PK-1 the `weighing` pack. The layered route's existing kinds (`-elaborate`, `-conflict`, `-status`, `-report`, `-certificate`, `admission`) answer weighing documents directly; `weighing-zone` and `weighing-record` are two new kinds of the layered route, run on the same decoded `LayeredU` with PK-1's X, their certificates bound through `bindCertX` to the full environment. A `weighing@0` document takes the layered route whether or not `norm-defaults@0` is on: with no unspecified predicate `fill U = U.D` and `Fill_T = []` (`fill_conservative`, merged) | one route for every `weighing@0` answer; profile-specific answers are layered-route kinds (SYNTHESIS O3, C9) | a `weighing` service mode; extending `ve_soft_norms_route` (meaning freeze) |
| D12 | English: each new wording has one reading and a deterministic paraphrase; decision predicates, labels and formulas never appear in what a reader sees (zero-training English). Wordings are registered where `soft-norms@0`'s are registered today (`ve/surface/registry.py` records, selected by `ve/norm_english.py` when the profile is on). Once english-lean's catalogue owns norm wordings, the wordings of 2.2 and soft's reading sets for "normally", "typically", "usually" and "in most cases" are rows there instead, never both | one owner per wording | symbols, rank numbers or weights in the text |
| D13 | No numeric weights, no "weigh" relation computed by the checker, no default inference inside the checker | research 4.4, 4.5; VISION converged rule item 5 | — |
| D14 | Cross-act collisions and precedents are **experiments first** (WG-E1, WG-E2), each with a pre-registered bar; a build follows only if the bar is met. If WG-E1 passes, exclusive acts come from `alternatives@0` (its chooser, `available` and exclusive choice) composed with soft norms, designed and reviewed in WG-10; weighing defines no exclusivity relation. **Outcome (phase 1):** WG-E1 failed (1 of 40 sampled CROSSACT units are two exclusive positive acts, or 3 of 40 with the second reader's calls on the contested units; none would change a checked answer). WG-10 is closed, and no exclusive-act construct is planned. Weighing still defines no exclusivity relation | when D14 was written the need was unmeasured; WG-E1 then measured it for cross-act collisions ([weighing-phase1.md](../research/weighing-phase1.md) 2.3, 2.4). Precedents stay unmeasured until WG-E2. `alternatives@0` owns exclusive choice (SYNTHESIS O9) | building exclusive-act semantics now; extending soft's colliding pairs with declared exclusive acts |

## 2. Design

### 2.1 What a `weighing@0` document is

A `weighing@0` document is a soft document (soft 1) whose environment carries a `weighing` block. Everything soft
requires still holds (soft 4.1), and the layered branch's well-formedness (`WellFormedU (soften D, unspec)`) holds; the
weighing checks come on top (2.5).

### 2.2 The English (one reading each; rejected as today when `weighing@0` is off)

| Wording | The one reading (the paraphrase the IDE shows) | Formal effect |
|---|---|---|
| `<Rank a> always outranks <rank b>.` | Where a rule serving <a>, or a rank above <a>, collides on one act with a rule serving <b>, or a rank below <b>, the lower rule gives way to an effective higher rule, and <decider> may not find that the lower consideration outweighs it: pairwise defeat, as for *outranks*. | declared edge `(a, b)` marked `always`; `Str_T` premises (D4) |
| `<Rank a> outranks <rank b>.` under the holistic flag (`<Rank a> generally outranks <rank b>.` is the same sentence, shown in this form) | If the pair is holistic: where a rule serving <a> collides on one act with a rule serving <b>, the lower rule gives way to an effective <a> rule unless <decider> finds that the <b> consideration outweighs it there; this document's ranking is holistic, and no step between them is marked *always*. If the pair is strict through another chain: the strict pair paraphrase below. | soft's declared edge, unchanged (D5) |
| `<Rank l> outweighs <rank h> on <act phrase> only when <condition>.` | <decider> may find that the <l> consideration outweighs the <h> consideration on <act phrase> only in situations where <condition>. | necessary condition on `outweighs_{act,l,h}` |
| `<Rank l> outweighs <rank h> on <act phrase> when <condition>.` | Wherever <condition>, the <l> consideration outweighs the <h> consideration on <act phrase>. Outside this condition, this sentence imposes no requirement; other conditions still apply. | sufficient condition on `outweighs_{act,l,h}` |
| `Whether <rank l> outweighs <rank h> on <act phrase> takes account of <consideration>[, <consideration>]*.` | Declared considerations for this finding: <consideration>; …; the checker does not verify that they were weighed. | factors (no premise) |
| `<Party> may turn off rule n only when <condition>.` | Rule n's switch for <party> works only in situations where <condition>. | necessary condition on `off_{n,party}` |
| `<Party> may turn off rule n only where <grantor> allows it.` | <party>'s switch on rule n works only where <grantor> has allowed it; <grantor> must itself be able to turn rule n off, and every condition on <grantor>'s own switch, written out, applies to <party>'s too. | grant: necessary conditions on `off_{n,party}` over the grantor's attributed predicate and the grantor's inherited conditions (D7) |
| `<Party> may turn off rule n only where <grantor> allows it, namely where <verbalisation of p>.` | The same, with the grant's predicate named. | the same grant with predicate `p` |

The legend line for a grant's predicate is soft's `instruction_of` line ("<verbalisation> records an instruction of
<grantor>"). Wordings not in this table are not `weighing@0` wordings: "normally", "typically", "usually", "in most
cases" stay soft 2.2's reading sets (a default rule or a frequency claim), and "all things considered" has no
wording (it is the decider's judgment, D1). A switch condition without "only" has no wording (D6).

The first two rows promise pairwise defeat by an effective higher rule, as soft's `outranks` wording does; no
paraphrase promises that the higher rule finally decides (where the higher rule's exception applies, the lower rule
may decide despite *always*: W-α). "<grantor> allows it" resolves only when exactly one predicate attributed to the
grantor is typed over rule n's argument sorts. With none, the English layer refuses and says that such a predicate
must be declared first; with several, it refuses, lists them and offers the last row's form for each. That form
elaborates to the same grant, inherits the grantor's conditions and is accepted subject to the normal grant checks
(2.5 step 5), never unconditionally.

**Paraphrase of a strict pair** (2.3 checklist, extended): "A <l> rule never outweighs a <h> rule: <h> always
outranks <m>, and <m> outranks <l>." The chain shown is the shortest one containing an `always` edge, in rank-name
order on ties (WG-2 `strictWitness`); the `always` step may be anywhere on it, so a rank above an `always` edge is
shown protected too. **Paraphrase of a holistic pair**: "A <l> rule outweighs a <h> rule only where <decider> finds
so; no step between them says *always*, and a plain *outranks* takes the document's holistic ranking."

### 2.3 Wire form (environment vocabulary, identity-bound like `soft`)

```json
"weighing": {
  "always":     [["safety", "ethics"]],
  "conditions": [{"target": {"outweighs": {"act": "comply_permitted", "lower": "helpfulness", "higher": "ethics"}},
                  "kind": "necessary", "condition": ["unary", "emergency", ["var", 0]]}],
  "factors":    [{"target": {"outweighs": {"act": "comply_permitted", "lower": "helpfulness", "higher": "ethics"}},
                  "factors": ["how much the user would lose", "how severe the ethical cost is"]}],
  "grants":     [{"rule": "r7", "party": "user", "grantor": "operator", "predicate": "operator_allows_user_switch"}]
}
```

Each `always` pair names a declared `soft.outranks` pair. `act` is soft's act key (soft 1.3). Every list is optional
and defaults to empty; the block is absent when empty. The canonical environment bytes include the block, so
`environment_id` changes when any entry changes and is unchanged for every environment without it (WG-3
`weigh_identity`). The layered decoder validates the original envelope and profiles first (`weighGate`, 2.5 step 1),
then hands the soft decoder the environment with the block and `weighing@0` removed (`stripWeighing`, a total pure
function: the identity on a non-object, rewriting `profiles` and `vocabulary` only when present), and every
certificate binds the **full** environment (2.6).

### 2.4 Elaboration: `Weigh_T`

```text
Str_T    for each (a, L, H) ∈ outweighsTriples(D) with strictPair(H, L):   ∀x̄. ¬outweighs_{a,L,H}(x̄)
                                                          label weigh:strength:<H>:<L>:<a>
Dec_T    for each condition c, in block order:
           necessary:  ∀x̄. target_c(x̄) → C(x̄)          label weigh:condition:<i>:necessary
           sufficient: ∀x̄. C(x̄) → target_c(x̄)          label weigh:condition:<i>:sufficient
Grant_T  for each grant g, the necessary case of the same generator on off_{g.rule,g.party}:
           ∀x̄. off_{g.rule,g.party}(x̄) → g.predicate(x̄)        label weigh:grant:<rule>:<party>
           and, for each party ρ the switch is granted through (the grantor, its grantor, …):
           ∀x̄. off_{g.rule,g.party}(x̄) → C(x̄)  per necessary condition i on off_{g.rule,ρ}
                                                          label weigh:grant:<rule>:<party>:condition:<i>
           ∀x̄. off_{g.rule,g.party}(x̄) → g'.predicate(x̄)  for ρ's own grant g'
                                                          label weigh:grant:<rule>:<party>:grant:<ρ>
Weigh_T  := Str_T ++ Dec_T ++ Grant_T                   PK-1's `weighing` pack; X's order is PK-1's
```

`outweighsTriples` is soft's (`Tree.lean:276`), so a strength premise exists only for an `outweighs` decision that
exists. A condition whose target names no existing decision is rejected (`NoSuchDecision`), never turned into a
fresh predicate.

### 2.5 Well-formedness (`WellFormedWeigh`), in order

The order is weighing.md 3.2's, authoritative in both documents: the gate, then the stripped document, then the
block, then the weighing checks. A case with a faulty soft document and a faulty block answers with the soft text
(the block decoder takes the decoded document, so it cannot run first).

1. The gate (`weighGate`, on the original environment, before anything is stripped): the envelope's `profiles` is a
   string array, sorted and unique; AR-10's row: the profiles contain `weighing@0`, `soft-norms@0` and `norms@0`
   (`UnsupportedProfile: weighing@0 requires soft-norms@0`) and not `rights@0` (`UnsupportedProfile: Unsupported
   profile combination rights@0 x weighing@0`); a `weighing` block only with `weighing@0`.
2. The stripped document passes `WellFormedSoft` and the layered branch's `WellFormedU (soften D, unspec)`; then the
   block decodes (shape, field types, lists, sizes: at most 64 `always` edges, 128 conditions, 64 factor entries of at
   most 16 strings of at most 200 bytes, 32 grants).
3. Each `always` edge names a declared edge (`StrengthOnUndeclaredEdge: <a>, <b>`), at most once
   (`DuplicateDeclaration: strength <a>, <b>`).
4. Each condition and factor target: a split source name is refused with AP's diagnostic (D6); the target names an
   existing decision (`NoSuchDecision: <rendered target>`); a sufficient condition on a switch is refused; a condition
   on an `outweighs` decision of a strict pair is refused (`ConditionOnStrictPair: <rendered target>`); a condition is
   typed over the target's argument sorts and mentions base predicates of `E` only (`InvalidInput: condition <i>
   mentions <q>`); it is quantifier-free after definition expansion (soft 6.1's gate).
5. Each grant: the rule exists and `party ∈ alterable(rule)` (`NoSuchDecision`); `grantor ∈ alterable(rule)`
   (`DelegationExceedsGrantor: rule <n>, <party>, <grantor>`); the predicate is a base predicate with
   `instruction_of = grantor` (`GrantNotAttributed: <predicate>, <grantor>`) and the rule's argument sorts. After
   every grant has passed these checks, the grants are checked in list order for cycles, self-grants included
   (`DelegationCycle: rule <n>, <party>`, D7).
6. Each sufficient condition implies each necessary condition on its target, by the propositional check
   (`ConditionsDisagree: the checker cannot show that condition <i> implies condition <j>`). A pair with more than
   `maxPropAtoms = 12` distinct atoms is refused (`ResourceLimit: conditions <i>, <j>`), never answered; boundary
   fixtures at 12 atoms (accepted) and 13 (refused), weighing.md 1.5 and θ19/θ20. Conditions on strict pairs stay
   refused (step 4).
7. Every generated premise is within `MAX_DEPTH` and `MAX_NODES` (`ResourceLimit: generated weighing premise
   <label>`), computed before it is built (soft 8, "Accepted means elaborable"); X with the background as one checker
   types it is PK-1's assembled check.

Warnings: `StrengthInert: <a>, <b>` (D5). `GenerallyUnderStrictOutranking: <a>, <b>` is the English layer's refusal
(D5), as are E7's refusals when "allows it" resolves to no predicate or to several (2.2). Diagnostic codes follow AR-13's scheme when it lands (DRI D6); until then the texts above are the contract,
identical in Lean and Python's display.

### 2.6 Zone answers and decision records

At a finite situation `M` (a base model over `E′_base` whose decision tables are ignored), for a regulated predicate
`r` and a typed tuple `v̄`, the **open atoms** are the decision atoms (every decision predicate of `E′` at every typed
tuple of `M`) and, under `norm-defaults@0`, the unsaid atoms. An **admissible completion** sets every open atom and
satisfies PK-1's whole assembled X (soft's, weighing's, and the attitudes, scales and events packs when those profiles
are on) and `Fill_T` on `M` (2.4). Lean answers:

| Answer | Meaning | Evidence |
|---|---|---|
| `settled <value>` | every admissible completion gives `<value>`, and one exists | complete enumeration of the cone's open atoms under the budget, pruning the assignments Kleene evaluation refutes against X ++ `Fill_T` (sound by `kleene_sound`), all surviving assignments agreeing; or a replayed certificate for `X ++ Fill_T ++ diagram(M) ⊢ outcome`; in both cases with one admissible completion checked by `modelCheckX` (else `unknown`) |
| `left to <deciders>` | two admissible completions with the **same** filling and opposite values | the two completions, each checked by `modelCheckX`; the decision atoms on which they differ, rendered in document terms |
| `not said` | two admissible completions with the **same** decisions and opposite values | norm-defaults' witness, as today |
| `left to` and `not said` | both hold | both witness pairs, in one answer (D9) |
| `inconsistent at this situation` | no admissible completion | labels Lean computes itself: Lean enumerates every assignment of the cone's open atoms compatible with the record (other open atoms stay unknown) and refutes each by Kleene evaluation of a labelled premise of `X ++ Fill_T`; per assignment, the first premise it refutes, then deduplicated and sorted. With no atom to assign, one assignment and one label: a premise refuted outright. Never taken from `proposed` or the search |
| `unknown <reason>` | none of the above | the reason Lean checked: the budget exceeded, so the enumeration is incomplete (`MAX_OPEN_ATOMS`, 16 by default; norm-defaults' status keeps 12); or a surviving branch of a complete enumeration that Lean could neither refute nor confirm as a witness. A budget is never the reason after a complete enumeration |

With `events@0` on, a completion is reported as a `left to` or `not said` witness only if events' calendar
completion-preservation theorem covers it; otherwise the answer is `unknown`, with events' `NotCalendar` reason (a
branch Lean could not confirm as a witness).

A **decision record** fixes some decision atoms (the decider's findings). The answer is the zone answer over
completions that agree with the record; when none does, `ruled out by <labels>`, with the same evidence as
"inconsistent" (a premise Kleene evaluation refutes with the record fixed, or every branch of a complete enumeration
refuted), each label rendered as its premise's sentence (`unknown`, with its checked reason, otherwise). Without a
record, no admissible completion is "inconsistent at this situation". "Assuming no exception applies" is the record
that fixes every `excepted` atom in the cone to false; the answer says so ("assuming no rule's exception applies
here").

English (display only; Lean selects the rows): "Settled: whatever the assistant decides here, the text requires the
assistant to <act>." / "Left to the assistant: this depends on whether rule 12's exception applies here, and on
whether helpfulness outweighs ethics on complying with this instruction here." / "Not said: the text does not say
whether …" / "Inconsistent at this situation: no way of deciding the open questions here satisfies the document; it
says …" / "Unknown: more than 16 open questions bear on this point." / "Unknown: the checker could neither rule out
nor confirm one way of deciding the open questions here: …" / "Ruled out: this record finds that guidelines
outweigh safety here; the document says safety always outranks ethics, and ethics outranks guidelines."

### 2.7 What stays open (the residual, never certified)

The findings themselves (`excepted`, `outweighs`, `off`); whether a decider considered the listed factors; whether a
finding is wise; "the spirit of the document" (:44); which category a consideration falls under (:44, "it may be
unclear which category a given consideration falls under"), which stays a translator's reading set over a rule's rank;
collisions between different acts (not planned: WG-E1 found 1 of 40 sampled CROSSACT units to be two exclusive
positive acts, 95% upper bound 0.13; the scope is the CROSSACT screen of the constitution's `norms` units, and such
pairs exist outside the sample, weighing-phase1.md 2.3); "best" responses among alternatives (research 4.7, research
only: 2 of the 40 sampled units ask for one).

## 3. Lean statements

Names have prefix `VE.Weighing.`; soft names are `VE.SoftNorms.*`, norm-defaults names `VE.NormDefaults.*`, RD-9 names
as on `rd-9/integrate`; PK-1, AR-10, QS-1 and AP names as in SYNTHESIS 2.1, 2.2, 2.3 and 2.6. New files (D13 of RD-9's
placement rule: a general definition goes in the file that owns its special case; new `Weighing/*` files hold only
what is specific to this profile). The statements of 3.1 to 3.3 are elaborated in [weighing.md](weighing.md) sections
1, 5 and 6, with the stub's findings in its section 0.

| File | Contents | Batch |
|---|---|---|
| `lean/VE/Weighing/Tree.lean` | `CondKind`, `Target`, `CondDecl`, `FactorDecl`, `GrantDecl`, `WeighEnv`, `WeighDoc`, `rankOrder`, `strictPair`, `strictWitness`, `targetF`, `targetSorts` | WG-2 |
| `lean/VE/Weighing/Conditions.lean` | `strengthPremises`, `condPremise`, `grantConds`, `weighLabelled`, `weighPremises`, `propImplies`, `checkWeigh`, `WellFormedWeigh`, the theorems of 3.2 | WG-2 |
| `lean/VE/Weighing/Examples.lean` | `#guard` fixtures W-α to W-λ | WG-2 |
| `lean/VE/Weighing/Wire.lean` | block decoder, `weighGate`, `stripWeighing`, `stripCase`, the `weighing` pack provider (PK-1), identity | WG-3 |
| `lean/VE/NormDefaults/Evidence.lean` (owner, extended) | `atomVO`, `coneAtomO`, `coneEvalO`, `coneValuesO`, `enumerateSettledO`, `table3O` with today's functions as the `opens = unsaidNames U` instances | WG-6 |
| `lean/VE/Weighing/Zone.lean`, `ZoneExamples.lean` | `decisionAtoms`, `AdmissibleCompletion`, `SettledZ`, `LeftToZ`, `zoneOf`, `recordCheck`, the theorems of 3.4 | WG-6 |
| the layered route's response-shape files (`lean/ResponseShape/Schemas/`, `Encoders/`) | the two kinds' row shapes and encoder theorems | WG-7 |
| `lean/WEIGHING.md` | every definition and theorem in plain words | WG-2, WG-3, WG-6 |

### 3.1 Definitions (WG-2)

```lean
namespace VE.Weighing
open VE.Norms VE.SoftNorms VE.NormDefaults
universe u

inductive CondKind | necessary | sufficient
  deriving DecidableEq, Repr

/-- The open decision a condition constrains (soft 1.3). -/
inductive Target
  | outweighs (act lower higher : String)
  | off (rule party : String)
  deriving DecidableEq, Repr

structure CondDecl where
  target : Target
  kind : CondKind
  condition : VE.Formula            -- context (targetSorts target).reverse, base predicates of E only
  deriving DecidableEq, Repr

structure FactorDecl where
  target : Target
  factors : List String
  deriving DecidableEq, Repr

structure GrantDecl where
  rule : String
  party : String
  grantor : String
  predicate : String               -- a base predicate with instruction_of = grantor, over the rule's sorts
  deriving DecidableEq, Repr

/-- Only `always` edges are on the wire (D5). -/
structure WeighEnv where
  always : List (String × String)
  conditions : List CondDecl
  factors : List FactorDecl
  grants : List GrantDecl
  deriving DecidableEq, Repr

def WeighEnv.empty : WeighEnv := ⟨[], [], [], []⟩

/-- `split` is AP's map, empty unless `acts@0` split a rule or an act (D6). -/
structure WeighDoc where
  D : SoftDoc
  W : WeighEnv
  split : VE.Acts.SplitMap

/-- Soft's ranks and declared edges as QS-1's order. -/
def rankOrder (Wd : WeighDoc) : VE.Closure.Order String := ⟨Wd.D.soft.ranks, Wd.D.soft.outranks⟩

/-- `(H, L)` is strict when some chain of declared edges from `H` to `L` contains an `always` edge. -/
def strictPair (Wd : WeighDoc) (H L : String) : Bool :=
  Wd.W.always.any (fun (a, b) => (rankOrder Wd).atLeast H a && (rankOrder Wd).atLeast b L)

/-- The shortest chain containing an `always` edge, names ordered on ties; `none` when the pair is holistic. -/
def strictWitness (Wd : WeighDoc) (H L : String) : Option (List String)

def targetSorts (Wd : WeighDoc) : Target → List String
  | .outweighs a _ _ => actSortsOf Wd.D a
  | .off n _ => match Wd.D.T.nodes.find? (·.name == n) with
      | some N => sortsOf Wd.D N.pred
      | none => []

def targetF (Wd : WeighDoc) : Target → VE.Formula
  | .outweighs a L H => outweighsF Wd.D a L H
  | .off n π => match Wd.D.T.nodes.find? (·.name == n) with
      | some N => atom (offName N π) (sortsOf Wd.D N.pred)
      | none => .bottom

/-- `Str_T` (2.4). -/
def strengthPremises (Wd : WeighDoc) : List VE.Formula

/-- The one generator: `Dec_T` for one condition, as soft's `excPremisesOf`; `Grant_T` is its necessary `.off` case. -/
def condPremise (Wd : WeighDoc) (c : CondDecl) : VE.Formula :=
  match c.kind with
  | .sufficient => bindAll (targetSorts Wd c.target) (.implies c.condition (targetF Wd c.target))
  | .necessary  => bindAll (targetSorts Wd c.target) (.implies (targetF Wd c.target) c.condition)

/-- `Grant_T` as labelled necessary `.off` conditions: each grant, then what it inherits along the grant chain (D7). -/
def grantConds (Wd : WeighDoc) : List (String × CondDecl × RequestPath)

/-- `Weigh_T` with its labels (2.4), in the order Str_T, Dec_T, Grant_T. -/
def weighLabelled (Wd : WeighDoc) : List (String × VE.Formula)
def weighPremises (Wd : WeighDoc) : List VE.Formula := (weighLabelled Wd).map (·.2)

/-- The implication check of D6: propositional, decided exactly, sound (`propImplies_sound`). -/
def propImplies (a b : VE.Formula) : Bool

/-- 2.5, steps 3 to 7, after `WellFormedSoft`; the diagnostics in that order. -/
def checkWeigh (Wd : WeighDoc) : Except String Unit
def WellFormedWeigh (Wd : WeighDoc) : Bool :=
  WellFormedSoft Wd.D && (checkWeigh Wd).isOk
```

### 3.2 Theorems (WG-2)

```lean
/-- D4: a strict pair is ordered. -/
theorem strictPair_outranks (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H L : String)
    (hs : strictPair Wd H L = true) : outranksPlus Wd.D.soft H L = true

/-- D4: an `always` edge is a strict pair. -/
theorem strictPair_of_always (Wd : WeighDoc) (a b : String) (hab : (a, b) ∈ Wd.W.always) : strictPair Wd a b = true

/-- D4: strictness is inherited downward and upward along the order. -/
theorem strictPair_down (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H M L : String)
    (h₁ : strictPair Wd H M = true) (h₂ : outranksPlus Wd.D.soft M L = true) : strictPair Wd H L = true
theorem strictPair_up (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H M L : String)
    (h₁ : outranksPlus Wd.D.soft H M = true) (h₂ : strictPair Wd M L = true) : strictPair Wd H L = true

/-- D4: a pair is holistic exactly when every chain from `H` to `L` avoids `always` edges. -/
theorem holistic_iff_no_always_chain (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H L : String) :
    strictPair Wd H L = false ↔ ∀ c, RankChain Wd H L c → ∀ e ∈ chainEdges c, e ∉ Wd.W.always

/-- D4: `Str_T` has a premise exactly for the `outweighs` decisions of strict pairs, queried at declared ranks and
    a declared predicate. Without `hL` and `hH` it is false: a rank name may end in `_`, so `outweighsName` aliases,
    and two accepted documents falsify it (weighing.md F9 and F13, 7.3); a third alias names an undeclared act, and
    the unrestricted statement survives it (F10). -/
theorem strength_iff (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (a L H : String)
    (hL : L ∈ Wd.D.soft.ranks) (hH : H ∈ Wd.D.soft.ranks)
    (ha : ∃ ss, Wd.D.E.predicates a = some ss) :
    bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H)) ∈ strengthPremises Wd ↔
      (a, L, H) ∈ outweighsTriples Wd.D ∧ strictPair Wd H L = true

/-- The meaning of `always`: in every structure satisfying `Str_T`, a higher effective default rule dominates a
    colliding lower default rule of a strict pair (no holistic override). Fixture W-α. -/
theorem always_dominates (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (strengthPremises Wd)) (M N : SoftNode) (hM : M ∈ Wd.D.T.nodes) (hN : N ∈ Wd.D.T.nodes)
    (hMd : M.mode = .default) (hNd : N.mode = .default) (hi : Incompatible Wd.D M N = true)
    (hh : higher Wd.D M N = true) (hs : strictPair Wd (rk M) (rk N) = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSortsOf Wd.D (act Wd.D N)) vs)
    (heff : EffD Wd.D S (tupleVal vs) (rankFuel Wd.D) M) :
    DominatedD Wd.D S (tupleVal vs) (rankFuel Wd.D) N

/-- ... and the lower rule never dominates the higher one by override: `DomWithD`'s override disjunct, which the
    holistic flag guards (so it is false under the strict flag), is false. WG-1 checked it against a counterexample
    model (weighing.md F1). -/
theorem always_no_override (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (strengthPremises Wd)) (M N : SoftNode) (hM : M ∈ Wd.D.T.nodes) (hN : N ∈ Wd.D.T.nodes)
    (hMd : M.mode = .default) (hNd : N.mode = .default) (hi : Incompatible Wd.D M N = true)
    (hh : higher Wd.D M N = true) (hs : strictPair Wd (rk M) (rk N) = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSortsOf Wd.D (act Wd.D M)) vs) :
    ¬ (Wd.D.soft.outranking = .holistic ∧ higher Wd.D M N = true ∧ EligibleD Wd.D S (tupleVal vs) N ∧
        OutweighsD Wd.D S (tupleVal vs) (act Wd.D M) (rk N) (rk M))

/-- Where every comparable colliding pair is strict, the holistic document decides exactly as the same document under
    the strict flag, on every structure satisfying `Str_T`, at tuples typed for the act. -/
theorem all_always_is_strict (Wd : WeighDoc) (h : WellFormedWeigh Wd = true)
    (hall : ∀ M N, (M, N) ∈ collidingPairs Wd.D → Comparable Wd.D M N = true →
      strictPair Wd (rk M) (rk N) = true ∨ strictPair Wd (rk N) (rk M) = true)
    (S : VE.Structure.{u}) (hS : Sat S (strengthPremises Wd)) (p : String) (sign : Bool)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSortsOf Wd.D (actKey Wd.D p)) vs) :
    DecidesSoftD Wd.D S (tupleVal vs) p sign ↔ DecidesSoftD (strictFlag Wd.D) S (tupleVal vs) p sign

/-- D6: the implication check is sound. -/
theorem propImplies_sound (a b : VE.Formula) (hp : propImplies a b = true) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (ha : a.denote S ρ) : b.denote S ρ

/-- D6: outside a necessary condition its decision is false (2.2's "only when"). -/
theorem condition_necessary (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (c : CondDecl) (hc : c ∈ Wd.W.conditions)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (targetSorts Wd c.target) vs) :
    c.kind = .necessary → ¬ c.condition.denote S (tupleVal vs) → ¬ (targetF Wd c.target).denote S (tupleVal vs)

/-- D6: inside a sufficient condition its decision is true (2.2's "when"). -/
theorem condition_sufficient (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (c : CondDecl) (hc : c ∈ Wd.W.conditions)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (targetSorts Wd c.target) vs) :
    c.kind = .sufficient → c.condition.denote S (tupleVal vs) → (targetF Wd c.target).denote S (tupleVal vs)

/-- D6: factor lists add no premise. -/
theorem factors_inert (D : SoftDoc) (W : WeighEnv) (sm : VE.Acts.SplitMap) (fs : List FactorDecl) :
    weighPremises ⟨D, {W with factors := fs}, sm⟩ = weighPremises ⟨D, W, sm⟩

/-- D7: a delegated switch works only where its grant holds. Fixture W-ζ. -/
theorem grant_needed (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (g : GrantDecl) (hg : g ∈ Wd.W.grants)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (targetSorts Wd (.off g.rule g.party)) vs)
    (hng : ¬ (atom g.predicate (targetSorts Wd (.off g.rule g.party))).denote S (tupleVal vs)) :
    ¬ (targetF Wd (.off g.rule g.party)).denote S (tupleVal vs)

/-- D7: a switch carries every necessary condition and every grant of each party it is granted through (`ρ ≠ π` on
    an accepted document: grant cycles are refused). -/
theorem grant_within_grantor (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (n π ρ : String) (hr : grantReach Wd n π ρ = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (targetSorts Wd (.off n π)) vs)
    (hoff : (targetF Wd (.off n π)).denote S (tupleVal vs)) :
    (∀ c ∈ Wd.W.conditions, c.target = .off n ρ → c.condition.denote S (tupleVal vs)) ∧
    (∀ g ∈ Wd.W.grants, g.rule = n → g.party = ρ →
      (atom g.predicate (targetSorts Wd (.off n π))).denote S (tupleVal vs))

/-- D7: no party is granted a switch its grantor lacks. -/
theorem delegation_bounded (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (g : GrantDecl) (hg : g ∈ Wd.W.grants) :
    ∃ N ∈ Wd.D.T.nodes, N.name = g.rule ∧ g.party ∈ N.alterable ∧ g.grantor ∈ N.alterable ∧
      (g.predicate, g.grantor) ∈ Wd.D.soft.instructionOf

/-- Typing, weighing's obligation to PK-1: `Weigh_T` is a list of closed base formulas of the filled environment. -/
theorem weighPremises_wellFormed (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (unspec : List String)
    (hw : WellFormedU ⟨soften Wd.D, unspec⟩ = true) :
    ∀ a ∈ weighPremises Wd, a.WellFormed (envAt (fill ⟨soften Wd.D, unspec⟩) 0) []

/-- The fragment: every premise survives sort-respecting substructures (soft's gate, D6). -/
theorem weighPremises_substructure (Wd : WeighDoc) (h : WellFormedWeigh Wd = true)
    (B₀ B : VE.Structure.{u}) (hsub : BaseSubstructure Wd.D B₀ B) (hs : Sat B (weighPremises Wd)) :
    Sat B₀ (weighPremises Wd)

/-- D3: `Weigh_T` alone never constrains the base. `SameBase Wd B B'`: `B'` agrees with `B` on every predicate that
    is not a decision; the witness sets each `outweighs` atom to the disjunction of its sufficient conditions and each
    switch to false. No global theorem: with soft's coherence, X can constrain the base (W-κ). -/
theorem weigh_alone_base_free (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (B : VE.Structure.{u}) :
    ∃ B' : VE.Structure.{u}, SameBase Wd B B' ∧ Sat B' (weighPremises Wd)

/-- D2: an empty block adds nothing. -/
theorem weigh_conservative (D : SoftDoc) (sm : VE.Acts.SplitMap) : weighPremises ⟨D, WeighEnv.empty, sm⟩ = []
theorem wellFormedWeigh_empty (D : SoftDoc) (sm : VE.Acts.SplitMap) :
    WellFormedWeigh ⟨D, WeighEnv.empty, sm⟩ = WellFormedSoft D
```

### 3.3 The route (WG-3)

```lean
namespace VE.Weighing

/-- PK-1's `weighing` pack: a constraint pack that declares no symbol. -/
def weighPack (Wd : WeighDoc) : VE.NormDefaults.Packs.Pack :=
  ⟨"weighing", .constraint, [], weighLabelled Wd, weighOrigins Wd⟩

/-- Certified entailment on a weighing document: RD-9's acceptanceX at PK-1's assembled X (each member a weighing
    premise or typed by its own provider; `assemble_wellFormed`'s instance). -/
theorem weigh_acceptance (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (unspec : List String)
    (hw : WellFormedU ⟨soften Wd.D, unspec⟩ = true) (X : List VE.Formula)
    (hX : ∀ a ∈ X, a ∈ weighPremises Wd ∨ a.WellFormed (envAt (fill ⟨soften Wd.D, unspec⟩) 0) [])
    (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill ⟨soften Wd.D, unspec⟩) (size (fill ⟨soften Wd.D, unspec⟩)))
            (Wire.premisesX ⟨soften Wd.D, unspec⟩ X Γ) φ cert = true) :
    EntailsX.{u} ⟨soften Wd.D, unspec⟩ X Γ φ

/-- Conflict-freedom on a weighing document: RD-9's `conflictFreeCheckX_sound` at PK-1's X. -/
theorem weigh_conflict_free (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (unspec : List String)
    (hw : WellFormedU ⟨soften Wd.D, unspec⟩ = true) (X : List VE.Formula)
    (hX : ∀ a ∈ X, a ∈ weighPremises Wd ∨ a.WellFormed (envAt (fill ⟨soften Wd.D, unspec⟩) 0) [])
    (certs : List (Option VE.Tableau.Certificate))
    (hc : Wire.conflictFreeCheckX ⟨soften Wd.D, unspec⟩ X certs = true) :
    Wire.ConflictFreeX.{u} ⟨soften Wd.D, unspec⟩ X

/-- Strength removes holistic weighing points from the conditional claim: a comparable colliding pair of a strict
    pair has its coherence conjunct implied by `Str_T` and the other premises (so it never appears in `conditional_on`
    for a lack of `outweighs` findings). -/
theorem strict_pair_coherent (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (M N : SoftNode)
    (hc : (M, N) ∈ collidingPairs Wd.D) (hcmp : Comparable Wd.D M N = true) (B : VE.Structure.{u})
    (hS : Sat B (strengthPremises Wd)) : (cohPremise Wd.D M N).denote B []
  -- already true without Str_T by `coh_rank_valid`; the statement review keeps it only if it adds a case
  -- (WG-1: it adds none, weighing.md F2)

namespace Wire
/-- The block removed: the profile list without `weighing@0`, the vocabulary without `weighing`; every other byte
    of the environment is unchanged. Total: the identity on a non-object; `profiles` and `vocabulary` rewritten only
    when present; no `Json.setObjVal!` on a non-object (weighing.md 1.8). -/
def stripWeighing (environment : Json) : Json
/-- The case with its environment stripped, total in the same way. -/
def stripCase (j : Json) : Json
theorem stripWeighing_other (environment : Json) (k : String) (hk : k ≠ "weighing") :
    ((stripWeighing environment).getObjValD "vocabulary").getObjValD k =
      (environment.getObjValD "vocabulary").getObjValD k
theorem stripCase_idem (j : Json) : stripCase (stripCase j) = stripCase j

/-- WG-3's step-1 gate (2.5 step 1), run on the original environment before anything is stripped: the envelope,
    profiles sorted and unique, AR-10's row (prerequisites present, `rights@0` refused), a block only with
    `weighing@0` (weighing.md 1.8). -/
def weighGate (environment : Json) : Except String Unit

/-- A case that passes the gate and whose `weighing` block is absent gets the layered route's answers byte for byte,
    except the rebound identity fields `environment_id` and `document_hash`: it decodes to the document of its
    stripped case. `LayeredU.core := (route, D, U, labelled, rightsCount, sitVocab, baseEnv)`, with `D` carrying
    `D.E` and `baseEnv` taken from the stripped environment; certificates are bound to the full source and compared
    through correspondingly rebound packages (`blockOf`, `stripCase`, `LayeredU.core`: weighing.md 1.8). -/
theorem runWeigh_delegates (j : Json) (hg : weighGate (j.getObjValD "environment") = .ok ())
    (hb : blockOf (j.getObjValD "environment") = none) :
    (VE.NormDefaults.Wire.decodeLayered j).map LayeredU.core =
      (VE.NormDefaults.Wire.decodeLayered (stripCase j)).map LayeredU.core

/-- Identity: a weighing document is bound to the full environment, block included. -/
theorem weigh_identity (j : Json) (L : VE.NormDefaults.Wire.LayeredU)
    (hL : VE.NormDefaults.Wire.decodeLayered j = .ok L) :
    ∃ c, VE.NormDefaults.Wire.canonicalEnvironmentJsonU (j.getObjValD "environment") = .ok c ∧
      VE.Route.Wire.environmentId (VE.NormDefaults.Wire.profilesOf (j.getObjValD "environment")) c = .ok L.envId ∧
      ((c.getObjValD "vocabulary").getObjVal? "weighing").toOption = blockOf (j.getObjValD "environment")
end Wire
end VE.Weighing
```

`weighX`, `weighX_wellFormed` (now PK-1's `assemble_wellFormed` instance) and `VE.Service.runMode_weighing` are
deleted: X is PK-1's, and there is no `weighing` mode. `runWeigh_delegates` is what makes the profile conservative at
the wire: the layered route reads a weighing document without a block as the soft document it is, never through a
second implementation. Its hypothesis `hg` is needed: without it, a case the gate refuses (a missing prerequisite,
`weighing@0` twice, an unsorted list, `j = {}`) would be compared with a stripped case that decodes or refuses with
another text (weighing.md F11 and W-η's refusals).

### 3.4 Zone answers and records (WG-6)

In `NormDefaults/Evidence.lean` (the owner), beside today's definitions, each with today's function as an instance:

```lean
namespace VE.NormDefaults

/-- `atomV` with an explicit list of open base predicate names. -/
def atomVO (U : UDoc) (M : VE.FiniteModel α) (opens : List String) (tab : String → List α → Option Bool)
    (p : String) (vs : List α) : Option Bool :=
  if p ∈ layerNames (fill U).T then tab p vs
  else if p ∈ opens then none
  else some (decide (vs ∈ M.relations p))
theorem atomV_eq_open (U : UDoc) (M : VE.FiniteModel α) (tab) :
    atomV U M tab = atomVO U M (unsaidNames U) tab := rfl

/-- `coneAtom`, `coneEval`, `coneOf`, `coneAtoms`, `coneAtomV`, `coneValues`, `tabK`, `table3` likewise
    (`coneAtomO` … `table3O`), each with `<name>_eq_open : <name> … = <name>O … (unsaidNames U) …` by `rfl`.
    `coneValuesO` prunes the assignments that Kleene evaluation refutes against `X ++ Fill_T`. -/
def enumerateSettledO (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (budget : Nat) (fixed : List ((String × List α) × Bool)) (n : String) (vs : List α) : Option Bool
theorem enumerateSettled_eq_open (U : UDoc) (M : VE.FiniteModel α) (n : String) (vs : List α) :
    enumerateSettled U M n vs = enumerateSettledO U [] M (unsaidNames U) 12 [] n vs
```

In `Weighing/Zone.lean`:

```lean
namespace VE.Weighing

/-- The decision atoms of a finite situation: every decision predicate of `D` at every typed tuple. -/
def decisionAtoms (D : SoftDoc) (M : VE.FiniteModel α) : List (String × List α)
def openNames (L : VE.NormDefaults.LayeredU) : List String := decisionNames L.D ++ unsaidNames L.U

/-- The labels of a labelled premise list. The zone takes PK-1's assembled X with its labels, and `Fill_T` with
    norm-defaults' labels (`VE.NormDefaults.Admission.fillLabelled`), so that Lean computes every cited label. -/
def labelsOf (ps : List (String × VE.Formula)) : List String := ps.map (·.1)

/-- A completion of `M`: relations that agree with `M` off the open names and with the record on its atoms, and
    satisfy PK-1's whole assembled X and `Fill_T`. -/
def AdmissibleCompletion (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (record : List ((String × List α) × Bool)) (R : String → List α → Prop) : Prop :=
  (∀ n vs, n ∉ opens → (R n vs ↔ vs ∈ M.relations n)) ∧
  (∀ a b, (a, b) ∈ record → (R a.1 a.2 ↔ b = true)) ∧
  Wire.BaseAdmissibleX U X { M.asStructure with relation := R }

def OutcomeIn (U : UDoc) (M : VE.FiniteModel α) (R : String → List α → Prop) (r : Regulated) (vs : List α) : Prop :=
  (outcomeBase (fill U) r.name).denote { M.asStructure with relation := R } (tupleVal vs)

/-- Settled, and not vacuously: some admissible completion exists. -/
def SettledZ (U X M opens record r vs) (b : Bool) : Prop :=
  (∃ R, AdmissibleCompletion U X M opens record R) ∧
  ∀ R, AdmissibleCompletion U X M opens record R → (OutcomeIn U M R r vs ↔ b = true)

/-- Left to the deciders: two admissible completions that agree on every unsaid atom and differ in outcome. -/
def LeftToZ (U X M opens record r vs) (unsaid : List String) : Prop :=
  ∃ R₁ R₂, AdmissibleCompletion U X M opens record R₁ ∧ AdmissibleCompletion U X M opens record R₂ ∧
    (∀ n ∈ unsaid, ∀ ws, R₁ n ws ↔ R₂ n ws) ∧ OutcomeIn U M R₁ r vs ∧ ¬ OutcomeIn U M R₂ r vs

/-- Why an answer is `unknown`; each reason is one Lean checked. -/
inductive ZoneUnknown (α : Type u)
  | budget (opens limit : Nat)
      -- the enumeration was not completed: the cone has `opens` open atoms not fixed by the record, over `limit`;
      -- never given after a complete enumeration
  | branch (assignment : List ((String × List α) × Bool)) (why : String)
      -- a complete enumeration left this assignment, which Kleene evaluation does not refute against X ++ Fill_T
      -- and no completion checked by `modelCheckX` confirms as a witness (`why`: none checked, or events' `NotCalendar`)

inductive ZoneAnswer (α : Type u)
  | settled (b : Bool) (witness : List ((String × List α) × Bool))
  | notSettled
      (leftTo : Option (List (String × List α) × List ((String × List α) × Bool) × List ((String × List α) × Bool)))
      (notSaid : Option (List ((String × List α) × Bool) × List ((String × List α) × Bool)))
  | ruledOut (labels : List String)
  | inconsistent (labels : List String)
  | unknown (reason : ZoneUnknown α)

def zoneOf (L : VE.NormDefaults.LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (r : Regulated) (vs : List α)
    (proposed : List (List ((String × List α) × Bool))) : ZoneAnswer α
  -- `X`: PK-1's assembled X with its labels. `proposed`: completions found by the untrusted search; Lean checks each
  -- (modelCheckX), never trusts it. `ruledOut` and `inconsistent` are produced only when Lean itself enumerates every
  -- assignment of the cone's open atoms compatible with the record (other open atoms stay unknown) and refutes every
  -- one by Kleene evaluation of a labelled premise of `X ++ fillLabelled L.U`; the labels are Lean's: per assignment
  -- the first premise it refutes, deduplicated and sorted (with no atom to assign, the one label of a premise
  -- refuted outright). Never a label from `proposed` or the search.

theorem zone_settled_sound (L : VE.NormDefaults.LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt L.U.D 0)) (hb : backgroundValid L.U.D M = true)
    (record) (r : Regulated) (hr : r ∈ L.U.D.T.regulated) (vs : List α)
    (typed : VE.TupleTyped M.asStructure r.sorts vs) (proposed) (b : Bool) (w)
    (hz : zoneOf L X M record r vs proposed = .settled b w) :
    SettledZ L.U (X.map (·.2)) M (openNames L) record r vs b

theorem zone_leftTo_sound (L X M valid hb record r hr vs typed proposed differ w₁ w₂ ns)
    (hz : zoneOf L X M record r vs proposed = .notSettled (some (differ, w₁, w₂)) ns) :
    LeftToZ L.U (X.map (·.2)) M (openNames L) record r vs (unsaidNames L.U) ∧
    ∀ a ∈ differ, a.1 ∈ decisionNames L.D

theorem zone_notSaid_sound (L X M valid hb record r hr vs typed proposed lt w₁ w₂)
    (hz : zoneOf L X M record r vs proposed = .notSettled lt (some (w₁, w₂))) :
    VE.NormDefaults.UndecidedAtX L.U (X.map (·.2))
      { M.asStructure with relation := completionOf M record w₁ } r vs

/-- A record ruled out, or a situation inconsistent: no admissible completion, at least one label, and every label
    cited is a premise of `X ++ Fill_T` (Lean refuted each branch of a complete enumeration with one). -/
theorem zone_ruledOut_sound (L X M valid hb record r hr vs typed proposed labels)
    (hz : zoneOf L X M record r vs proposed = .ruledOut labels ∨
          zoneOf L X M record r vs proposed = .inconsistent labels) :
    (¬ ∃ R, AdmissibleCompletion L.U (X.map (·.2)) M (openNames L) record R) ∧ labels ≠ [] ∧
      ∀ l ∈ labels, l ∈ labelsOf (X ++ VE.NormDefaults.Admission.fillLabelled L.U)

/-- Today's norm-defaults status is the instance with no decision open, no record and budget 12. -/
theorem zone_extends_status (U : UDoc) (M : VE.FiniteModel α) (n : String) (vs : List α) :
    VE.NormDefaults.enumerateSettledO U [] M (unsaidNames U) 12 [] n vs = VE.NormDefaults.enumerateSettled U M n vs
```

`zone_settled_sound` is proved from the cone lemma (a Kleene-definite value under an assignment of the cone's atoms is
the value in every structure agreeing on them, `kleene_sound`), the completeness of the enumeration over the cone's
atoms (`enumerate_all`, generalized), the soundness of pruning (an assignment Kleene evaluation refutes against
`X ++ Fill_T` extends to no admissible completion, `kleene_sound` against X), and the checked witness, which gives the
existence conjunct. `zone_ruledOut_sound` uses the same two lemmas without the witness: the enumeration covers every
assignment of the cone's open atoms compatible with the record, each is refuted by a premise, so no admissible
completion exists; the label conjuncts hold by construction (each label is read off `X ++ Fill_T` by Lean).
Existing norm-defaults answers and budgets are unchanged (`zone_extends_status` and its fixtures).

## 4. Fixtures

### 4.1 Synthetic (`#guard` in Lean, the same through the service in Python; the W fixtures' values computed in Lean by WG-1, weighing.md 7; the Z fixtures are WG-6's)

Unless a fixture says otherwise, soft 10's frame: one sort `assistant`, act X with `x_required` (obligation,
deny-by-default, permission `x_permitted`) and `x_permitted` (permission, allow-by-default), situation `a`, guards `⊤`,
holistic flag, decider `the assistant`. Each fixture names its record.

- **W-α (always).** Soft (α) plus `a always outranks b`, record "no exception applies". `Str_T =
  [∀x. ¬soft__outweighs__b__a__x_permitted(x)]`. Every admissible completion has H alone selecting: `settled yes`. The
  finite base with the `outweighs` atom true at `a` fails `modelCheckX` with label `weigh:strength:a:b:x_permitted`.
  Without the strength, soft (α)'s two answers. With the record "h's exception applies, l's does not": accepted, and
  the lower rule decides despite `always` (`settled no`): E1 is pairwise defeat. Two accepted renamings of W-α
  falsify `strength_iff`'s unrestricted statement, as regressions, never refusals (weighing.md 7.3): the lower rank
  `b_`, queried at `(x_permitted, b, _a)` (F9), and ranks `c > c_`, queried at `(x_permitted, c, _c)`, where `c` is
  declared and only `hH` excludes the query (F13). Ranks `c`, `c_`, `l` with the triple `(x_permitted, l, c_)`,
  queried at `(_x_permitted, l, c)`, is a name collision the unrestricted statement survives: the act is undeclared,
  so the query's formula is `¬⊥` (F10).
- **W-β (closure).** Ranks `s > e > g > h`; `s always outranks e`, `e outranks g`, `g outranks h`.
  `strictPair`: `(s,e)`, `(s,g)`, `(s,h)` strict; `(e,g)`, `(e,h)`, `(g,h)` holistic. `strictWitness s h = [s, e, g,
  h]`. Colliding rules ranked `s` and `h` on X: no override; ranked `e` and `h`: override possible.
- **W-γ (flags).** The strict flag with `e generally outranks g`: `GenerallyUnderStrictOutranking: e, g` (English
  layer). The strict flag with `s always outranks e`: accepted, `StrengthInert: s, e`, `Str_T = []`.
- **W-δ (necessary override condition).** Soft (α), `a outranks b`, condition "b outweighs a on doing x only when
  urgent" (`urgent(x)` a base predicate), record "no exception applies". Zone of `x_required` at `a` with `urgent(a)`
  false: `settled yes`. With `urgent(a)` true: `left to the assistant`, differing on the one `outweighs` atom.
- **W-ε (sufficient override condition).** As W-δ with "b outweighs a on doing x when urgent", record "no exception
  applies": with `urgent(a)` true, `settled no` (L alone selects); with `urgent(a)` false, `left to the assistant`.
- **W-ζ (grant).** Strict `must X` on `x_required`, `alterable: [operator, user]`, grant (user, grantor operator,
  `operator_allows(x)` with `instruction_of: operator`), record "the operator has not turned rule n off". Zone at `a`
  with `operator_allows(a)` false: `settled yes` whatever the user's switch is; true: `left to` the user's switch.
  Without the record, `left to` the operator's own switch. With `alterable: [user]` only: `DelegationExceedsGrantor:
  rule n, user, operator`. With `instruction_of: user` on the predicate: `GrantNotAttributed: operator_allows,
  operator`. The inheritance of D7 (a condition on the operator's switch; a chain of two grants) is weighing.md's
  W-ζ2 and W-ζ3. Grant cycles: a self-grant and a two-party cycle are refused (`DelegationCycle: rule n, user`);
  W-ζ3's chain stays accepted.
- **W-η (conservativity).** Every soft fixture α to υ under `weighing@0` with no block passes the gate, and the
  layered route's answers equal those of the same case without `weighing@0`, compared without the rebound identity
  fields (`environment_id`, `document_hash`), which W-η compares separately (`runWeigh_delegates`; `base_environment`
  is the stripped environment's); certificate answers are compared through rebound packages. Refusals by the gate,
  each with its exact text recorded and `stripCase` returning on each: profiles `[norms@0, relational-fol@0,
  weighing@0]` without a block (`UnsupportedProfile: weighing@0 requires soft-norms@0`); `j = {}` (no panic); a
  malformed envelope; a duplicated profile; unsorted profiles; `rights@0` with `weighing@0`; a `weighing` block with
  `weighing@0` off. A combined fault (a bad soft document and a bad block) answers with soft's text. Every
  norm-defaults fixture's `-status` is byte-identical (`zone_extends_status`, budget 12).
- **W-θ (diagnostics).** `StrengthOnUndeclaredEdge`, `DuplicateDeclaration: strength`, `NoSuchDecision` (an
  `outweighs` target on an act with no colliding pair), `InvalidInput: condition 0 mentions x_required`, a quantified
  condition (fragment gate), `ConditionOnStrictPair` (on a declared `always` edge and through the closure), a
  sufficient switch condition, each grant diagnostic, `ResourceLimit: generated weighing premise <label>` on a
  condition at the depth limit, `ResourceLimit: conditions 0, 1` at 13 distinct atoms beside an accepted pair at 12,
  an accepted necessary-and-sufficient pair on one target whose necessary condition forces the finding "no" outside
  the sufficient condition (θ11, why E4's paraphrase says "Outside this condition, this sentence imposes no
  requirement; other conditions still apply."), and the required regression: contradictory sufficient and necessary
  conditions on one target (`ConditionsDisagree`), whose premises, without the check, admit no decision assignment
  where the condition holds (a vacuously "settled" outcome; bypassing admission, the zone answer is "inconsistent",
  an internal counterexample only, weighing.md W-θ bypassed).
- **W-ι (identity).** Changing one `always` edge, condition, factor or grant changes `environment_id`; a certificate
  replayed after the change is refused with the stale-binding text.
- **W-κ (mandatory regression; complete refutation).** Two opposing unranked defaults with true guards, exceptions
  forbidden, one switch each (`s₁`, `s₂`), and the necessary condition `urgent` on both switches. Where `urgent` is
  false, the answer is "inconsistent at this situation", from the complete enumeration of the 16 assignments, each
  refuted by a labelled premise; the labels are all five of X's (`soft:coherence:M,N`, both `soft:exception:*`
  labels from the branches with an `excepted` atom true, and both `weigh:condition:<i>:necessary`), computed by Lean
  (weighing.md 7.2's sixteen-branch table).
- **W-λ (split names).** An `.off` target naming a split rule is refused with AP's diagnostic; the same target naming
  one of its parts is accepted.
- **W-μ (argument order).** An act over `(assistant, user)`; a condition and a grant predicate that use both
  variables; two elements per sort, chosen so that swapping the indices changes the admissible set; the expected
  answer recorded (weighing.md 7.2: 4 admissible assignments of 256). The seeded bugs of WG-2 swap the index in
  `(targetSorts _).reverse`, `tupleVal` or `atom`'s `.binary p (var 1) (var 0)`; each must fail this fixture.
- **Z-α (left to).** Soft (δ), unranked weighing point: zone of `x_required` at `a` is `left to the assistant`, the
  two completions excepting `A` and `B` respectively; the coherence conjunct rules out the completion with neither
  excepted.
- **Z-β (record).** W-α with the record "b outweighs a on doing x here": `ruled out by
  [weigh:strength:a:b:x_permitted]` (the one-label case: the premise is refuted with the record fixed and nothing open
  assigned), rendered "the document says a always outranks b".
- **Z-γ (not said beside left to).** A default rule on an `unspecified` predicate whose exception is open
  (norm-defaults' u8 frame): zone where the exception may hold: `left to` on the exception and `not said` on the
  gap, both reported in one answer.
- **Z-δ (budget; insufficient budget).** Seventeen open atoms in the cone: `unknown` with reason the budget (17 open
  atoms over 16), "more than 16 open questions"; the enumeration is incomplete, so the answer is never
  `inconsistent`.
- **Z-ε (presumption).** Soft (ρ) with the record "assuming no exception applies": `settled yes` "assuming no
  rule's exception applies here"; without the record, `left to`.
- **Z-ζ (surviving branch).** Soft (α)'s rules on act X beside W-κ's two rules moved to a second act Y; zone of
  `x_required` at `a` with `urgent(a)` false. The cone of `x_required` holds X's decision atoms only, so W-κ's
  premises on Y evaluate to Kleene `none` on every branch and refute none, while no completion exists (Y's atoms
  admit none). Expected: never `inconsistent`; `unknown` with reason the surviving branch, never a budget (the
  enumeration is complete). WG-6 computes the branch.

### 4.2 From the constitution (real units, run `20261012T1800Z`)

Draft 1 cited unit ids, spans and texts from research 2.5, which is unfilled; WG-0 and WG-5 record them from the run's
ledger. Each fixture records the VE sentences, the expected status, and the zone answer where one applies; WG-5 and
WG-8 check them through `ve document` on the pilot branch.

| Fixture | Source | VE sentences (shape) | Expected |
|---|---|---|---|
| C-1 | :34 value order | soft 2.4's three `outranks` sentences, the holistic flag, decider "the assistant"; unit READINGS {A strict dominance, B open weighing carve-out, C ranks with the holistic flag} | WG-0: rank sentences CHECKED; flag OPEN; unit READINGS |
| C-2 | :40 "even if Claude is confident in its reasoning" | `Safety always outranks ethics.` beside `Safety outranks ethics.` (a reading set: :34 says the order is holistic, :40 says the safety step is robust) | WG-5: READINGS, both readings conflict-free |
| C-3 | :42 "Exceptions to this are any hard constraints … and any cases where Anthropic's guidelines overlap with broad safety" | the hard constraints are strict rules (already); guideline rules that overlap with safety carry rank safety (a narrowing per rule, attributed) | WG-5: OPEN (the overlap is an open classification) |
| C-4 | :138 "operators cannot grant users more than operator-level trust" | grants on the instructable-behaviour rules | WG-5: CHECKED where the rules are declared: `DelegationExceedsGrantor` and the inherited conditions (`grant_within_grantor`) are the checked content |
| C-5 | :405-423 instructable behaviours | default rules `(operators may turn off)` / `(users may turn off)` with grants where the source says "absent increased or decreased trust granted by operators" | WG-5: OPEN (each default's exception) |
| C-6 | :443 "cannot be unlocked by any operator or user" | soft's `hard: true` narrowing, cited once on the hard-constraint header | WG-0: CHECKED (`HardConstraintAltered` is the check) |
| C-7 | :457 "For cases that are more unclear or uncertain, we want Claude to be guided by the more holistic … prioritization" | each hard constraint's prohibition in the knowing-or-likely case (today's repair) beside a default "should not" for the unclear case, decided by the assistant | WG-8: zone `settled no` (knowing case), `left to the assistant` (unclear case) where today's probe says UNDECIDED |

## 5. Batches

Every batch is 2 to 6 hours for one builder and passes the lean-first gate (LEAN-FIRST-PLAN 5.1) as RD-9's batches do:
the full gate once on the final commit, selected tests while iterating, seeded bugs in each changed language
recorded with the failing test, `DELTA.md` with the corpus A/B by class, the deletion ledger, the frozen-inventory and
assurance-manifest updates (DRI D2), trust classes with any budget rise signed (DRI D3), `tools/lean_statements.py`
showing additions only, and `lean/audit.py`. New Python respects the layer map (DRI D5); new diagnostics take AR-13's
codes when they land (DRI D6); every identity is Lean's (DRI D7). Generated files are never edited by hand:
`tools/gate-collection.json`, `lean/checkers.lock` and the rest through `tools/regen_generated.py --write`.

| # | Batch | Hours | Owner | Needs | Pilot effect |
|---|---|---:|---|---|---|
| WG-0 | The value order and the hard constraints' immunity with today's `soft-norms@0` | 3–4 | pilot | RD-9 SC-8 on `main`; SC-9's soft form adopted or on the same pilot branch. **DEFERRED** on 2026-10-13 (5.0) | measured by WG-0 (draft 1's estimate cited research 5.2, unfilled; withdrawn; phase 1 measured nothing to replace it) |
| WG-1 | Statement review of section 3, elaborated in a stub; fixture values computed | 3–4 | planner | — | none |
| WG-2 | Lean: block, strength, conditions, grants, premises and their theorems | 5–6 | Lean | WG-1; QS-1; AP's split map (for the split checks); `main` | none |
| WG-3 | Lean: block decoder, `stripWeighing`, the `weighing` pack, AR-10's row, identity | 5–6 | Lean | WG-2; RD-9 SC-1 and SC-6 on `main`; PK-1; AR-10's table | none |
| WG-4 | Python: surface records, relay, document dispatch, fuzz tests | 4–5 | Python | WG-3; RD-9 SC-8 on `main`; the document-mode queue | none |
| WG-5 | The constitution: strengths, conditions, switches and grants | 4–5 | pilot | WG-4, WG-0; the hard-constraint queue | not estimated (draft 1's estimate withdrawn) |
| WG-6 | Lean: zone answers and records (open atoms widened in their owner) | 5–6 | Lean | WG-3; RD-9 SC-A on `main`; PK-1 | none |
| WG-7 | Layered-route kinds and display: `weighing-zone`, `weighing-record`, English, CLI | 5–6 | Lean, Python | WG-6, WG-4; PK-1 | none |
| WG-8 | The constitution: zone probe on the hard constraints, the "should" sets and each grant | 3 | pilot | WG-7; the hard-constraint queue | no coverage claim; answers recorded |
| WG-E1 | Experiment: do collisions between different acts need a new construct? | 4 | planner | done: **FAIL** ([weighing-phase1.md](../research/weighing-phase1.md)). It did not need WG-0, because clause 1 decided it | decided WG-10: closed |
| WG-E2 | Experiment: can worked examples bind a decider as precedents? | 5–6 | planner | WG-2 | decides WG-9 |
| WG-9 | (only if E2 passes) Lean: precedents compiled into decision conditions | 5–6 | Lean | WG-E2, WG-3 | per E2's measurement |
| WG-10 | **CLOSED** by WG-E1's FAIL (kept as history). Was: (only if E1 passes) design and review of `alternatives@0` composed with soft norms | 3 | planner | WG-E1 (failed); `alternatives@0` | none. Measured: 0 B; no sampled (ii) unit changes a checked answer (7) |

**Order.** WG-1's statement review is done (one obligation is left before WG-2, see 5.0), and WG-E1 is done (FAIL);
WG-2 needs QS-1. The constitution's path is WG-0 → WG-2 → WG-3 →
WG-4 → WG-5, then WG-6 → WG-7 → WG-8: WG-5 shows each grant's effect through `modelCheckX`, and WG-8 records each
grant's zone answer, so no requirement depends on a later batch. WG-0 runs on its own after SC-8; the RD-9
prerequisites stay as stated, and WG-E2 keeps its pre-registered bar. WG-3 lands on `Layered.lean` after
AT-2/AT-3a and before ET-4 and QT-B2 (PK-1's integration order); WG-5's and WG-8's edits to u0165.s01–s07 run in the
hard-constraint queue. Landing preference: weighing lands after quantities' track A and before events. About 38 to 47
builder-hours on the path (*estimate*, not evidence of speed).

### 5.0 Status after phase 1 (2026-10-13)

Phase 1 is the cross-plan build order's "Now, no product code" step (SYNTHESIS 4.1). The report is
[weighing-phase1.md](../research/weighing-phase1.md), and its evidence is in `docs/research/evidence/weighing/`.

| Item | Status | Result, or the trigger that releases it | What it gates |
|---|---|---|---|
| WG-0 | **DEFERRED** | Trigger: RD-9 SC-8 on `main`. That means `rd-9/integrate` is merged, and `ve/document.py` no longer refuses `soft-norms@0` beside `norm-defaults@0`. Not met on 2026-10-13: at `main` `d006b1f4`, `rd-9/integrate` (`5019007c`) is not an ancestor, `LayeredEntail.lean` and `LayeredAdmission.lean` are absent, and the refusal is at `ve/document.py:630-634`. Not attempted | WG-5 (with WG-4); the first measured pilot number |
| WG-1 | done, with one obligation left | The statement spec is [weighing.md](weighing.md). Before WG-2 starts, the untracked stub is re-elaborated against draft 2's statements and its `#eval`s for the *derived* values are run. The stub is not in the repository today | WG-2 |
| WG-2 to WG-8 | not started; unchanged | Their "Needs" in the table above. Phase 1 did not test them: WG-E1 classified conflicts between acts, not the construct a unit needs | — |
| WG-E1 | **FAIL** | (ii) is 1 of 40 against a bar of 8, and 0 (ii) units change a checked answer against a bar of 5. With the second reader's calls on the three contested units, (ii) is 3 of 40 and still 0 change an answer. Clopper–Pearson 95% upper bound on the (ii) rate: 0.132 (0.204 with those calls); the bar's rate is 0.20 | WG-10, now closed |
| WG-E1's second reader | done | 10 of 10 agree on the frozen subset (orders 1 to 10; κ 1.0, chance agreement 0.82, 9 of the 10 are (iv)). Post hoc, 0 of 3 agree on the contested (i)/(ii) units. A later measurement that depends on the (i)/(ii) boundary should have two readers on every unit, not on a subset | — (reported, not part of the bar) |
| WG-E2 | **DEFERRED** (not run) | Trigger: WG-2 lands (its "Needs"). The bar is unchanged. Two cost-benefit units WG-E1 drew (u0129.s03 :321, u0183 :479) look like the decision WG-E2 expects to pick (:325-347). That is consistent with WG-E2's protocol, not evidence for it | WG-9 |
| WG-9 | **DEFERRED** | Trigger: WG-E2 passes | precedents in `Dec_T` |
| WG-10 | **CLOSED** | WG-E1 FAIL: "Otherwise record the result and close" | — |
| research 4.7 (best response) | research, no batch | 2 of the 40 sampled units are (iii) (u0034.s01 :70, u0036.s01 :78), and the one (ii) unit has the shape of a preference among alternatives. Its priority neither rises nor falls | — |

### WG-0. The value order and the hard constraints' immunity (pilot, 3–4 h)

**DEFERRED** until RD-9 SC-8 is on `main` (5.0). Phase 1 checked that prerequisite on 2026-10-13, found it unmet, and
did not attempt the translation. Nothing below changes.

On a pilot branch (`pilot/cc-<stamp>`), scripts under `usecases/claude-constitution-pilot/run-<stamp>/`, all at one
commit, in the foreground, host load recorded. No product code.

1. Start from RD-9 SC-9's probe translation (soft form of the four "should" sets) if adopted, else from the committed
   translation with `soft-norms@0` added through SC-8's path.
2. Declare the soft block: ranks `safety`, `ethics`, `guidelines`, `helpfulness`; the three `outranks` edges; the
   holistic flag decided by "the assistant" (soft 2.4's :34 reading C). The :34 unit becomes a reading set {A, B, C}
   (soft-norms-PLAN 4); the translator's narrowing to {B, C} is a separate attributed unit citing :34 "holistic rather
   than strict".
3. The :27-32 value list: the four rank names with their definitions as open-term declarations (`meaning: open`), the
   bytes of each definition counted to the term's schema as `factors` (soft-norms-PLAN 4); not CHECKED.
4. "Rule n serves <rank>" on every existing default rule whose rank the source cites (u0073.s05's rule serves
   helpfulness, citing :32), each a narrowing unit.
5. :443's "cannot be unlocked by any operator or user": `hard: true` on the hard-constraint rules, cited once on the
   header (soft-norms-PLAN 4, "split the units").
6. Check, render, measure: before and after at one commit, the measures of RD-9 SC-9's table plus `weighing_points`,
   `holistic_overrides`, the per-pair classification, and the bytes per status. Blind whole-span fidelity review of
   every changed unit before anything is counted (soft-norms-PLAN 4, C1); failures reverted.

Done when: the table is filled with measured values, `SUMMARY.md` and `metrics.json` report before and after, and
every refused sentence, UNKNOWN and failed review is listed rather than worked around. Deleted, not duplicated: none
(no product code). Shared files: none in the product repository.

### WG-1. Statement review (planner, 3–4 h)

Every definition and theorem of section 3 written in an untracked stub (`lean/SpecStubs_weighing.lean`) against the
build of `main` and of `rd-9/integrate`; each theorem as `def T : Prop := …` and the short ones proved; every fixture of
4.1 recomputed with `#eval`; each theorem checked against a counterexample model. Reviewed by Astra and Opus until
converged (Fable arbitrates only an unconverged debate). Questions for the review: D4's closure rule against per-edge
strength; whether `strict_pair_coherent` adds anything beyond `coh_rank_valid` (drop it if not); `all_always_is_strict`'s
typing hypothesis; the pruning soundness of `coneValuesO` (by `kleene_sound` against X); `weigh_alone_base_free`;
`grant_within_grantor`; the restated `runWeigh_delegates`; the wordings of 2.2 for one reading each. Re-check W-δ, W-ζ,
Z-β and C-4 against the edited statements, and confirm that the layered gate accepts a stripped document that lacks
`norm-defaults@0`. Done when the review has converged and this file carries its edits. The item-1 statement
specification, [weighing.md](weighing.md) (2026-10-13), is WG-1's output for WG-2 to WG-5. Its review
(`manage-agents/debates/weighing-spec/`) ended FIX, settled by the DRI's ruling; weighing.md draft 2 and plan draft 3
carry all 14 items, and weighing.md draft 3 and this draft 4 carry the bounded re-check's one finding (item 1's
second falsifying regression, F13). Build authorisation follows the corrected statement spec: the untracked stub is
re-elaborated against draft 2's statements (draft 3 changes none), and its `#eval`s for the values marked *derived*
are run, before WG-2 starts.

### WG-2. Lean: block, strength, conditions, grants (Lean, 5–6 h)

Files (new): `lean/VE/Weighing/{Tree,Conditions,Examples}.lean`, `lean/WEIGHING.md`. Shared: `lean/VE.lean`
(import), `lean/VE/Audit.lean` (audit entries for every theorem of 3.2), the frozen inventory and assurance manifest
(new files pinned).

Fixtures: W-α to W-θ, W-κ, W-λ and W-μ as `#guard`s on the direct semantics and on the generated premises,
including weighing.md's draft 2 rows (W-α with h excepted, θ11's zone, θ19/θ20, the grant cycles, W-κ's sixteen
branches, the `strength_iff` regressions). Seeded bugs (lean-first gate): among them, swapping the index in
`(targetSorts _).reverse`, in `tupleVal` and in `atom`'s `.binary p (var 1) (var 0)`, each failing W-μ, recorded with
the failing check.

Deleted, not duplicated: no second premise generator (`condPremise` has soft's `excPremisesOf` shape but targets
decisions soft does not constrain; the statement review checks whether `excPremisesOf` can be stated as the
`.excepted` instance of one generator, and if so the generator moves to `SoftNorms/Soften.lean` with soft's statements
unchanged); grant premises are `condPremise`'s necessary `.off` case; no rank closure of its own: reachability is
QS-1's over `VE.Closure`, proved equal to soft's `outranksPlus`.

Done when: builds with no `sorry` and the allowed axioms only, `lean_statements.py` shows additions only, every
theorem is in `WEIGHING.md` in plain words, and the gate passes. No answer can change: nothing calls the new code.

### WG-3. Lean: the block on the layered route (Lean, 5–6 h)

Files (new): `lean/VE/Weighing/Wire.lean` (the block decoder, `stripWeighing`, the `weighing` pack provider,
identity). Shared: PK-1's provider line in `lean/VE/NormDefaults/Layered.lean`/`Packs.lean` (the layered decoder runs
`weighGate` on the original environment, strips the block, decodes the stripped source, decodes the block, checks
`WellFormedWeigh` and adds the pack), AR-10's table (one `ProfileRow` for `weighing@0`, `requires := ["soft-norms@0",
"norms@0"]`, `refuses := [rights@0]`, with the row's composition proof),
`lean/VE/Audit.lean`. No service mode: no `Protocol.lean` constructor, dispatch arm or `runMode_weighing`, no entry in
`ve/backends/service_schema.py`'s `MODES`, no `ve/backends/lean_service_schema/weighing.json`; the Python profile side
is generated by AR-10.

The layered route's existing kinds answer weighing documents with PK-1's X; certificates go through `bindCertX` with
the full environment. No kind is reimplemented.

Fixtures: W-η through the layered route (rows compared without the identity fields, certificates through rebound
packages; the gate's refusals with their exact texts; `stripCase` on each refused case; the combined fault), W-ι,
and W-α, W-δ, W-ζ's conflict and certificate answers. Route-case fixtures recorded into `tests/data/route-cases.jsonl` by
`tests/route_case_recorder.py` and checked by `tests/test_route_row_schemas.py` (WG-4 adds the Python tests that
record them).

Deleted, not duplicated: no premise assembly and no service mode in `Weighing/*`; weighing is one PK-1 pack and two
layered-route kinds. `repo_map.py --check` passes (no new mode).

Done when: the fixtures pass, `runWeigh_delegates` and `stripCase_idem` are proved, the corpus A/B is identical (no
corpus document has the profile), and the gate passes.

### WG-4. Python: surface, relay, documents (Python, 4–5 h)

Files (new): `ve/surface/weighing.py` (records for 2.2's wordings, profile-gated as soft's are),
`ve/weighing.py` (the relay: sends the layered route's weighing cases, and the two kinds `weighing-zone` and
`weighing-record` once WG-7 adds them, with `rows` from `ve/backends/relay.py`; checks schema and binding only, R8),
`tests/test_weighing_lean.py` (documents through the service), `tests/test_weighing_answer.py` (fuzz: each member of a
genuine answer dropped, emptied, retyped, duplicated, reordered, an index pushed out of range, one and two faults at a
time; every mutant `CheckerUnavailable` or showing nothing different). Shared: `ve/norm_english.py` (select the new
records when `weighing@0` is on), `ve/document.py` (a `weighing@0` document goes to the layered route, not to a
`weighing` mode; the refusal text for unsupported combinations; this edit joins the document-mode queue after
`lf-16g`, in landing order AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10), `tests/test_english_unambiguity.py` (the new
wordings), and the regenerated `tools/gate-collection.json`.

English paraphrases: rendered from Lean's elaboration row (`strictWitness`, labels, targets, inherited conditions) by
display code only; `tools/relay_lint.py` gains `weigh__`-free checks (no premise label or decision name in rendered
text). E7's resolution of "allows it" (2.2) with weighing.md 7.6's fixtures: one match accepted; none refused (the
predicate must be declared first); several refused with the list and the offer; the offered form accepted and shown
to inherit, with the control that fails. The Sonnet 5.5 comprehension check of 8's open question is saved evidence
under the batch's `docs/<batch>/`, not a suite test: suite tests make no model calls.

Deleted, not duplicated: Python builds no `Weigh_T`, no `strictPair`, no `X`; it renders Lean's rows.

Done when: the fixtures pass through `ve document load/check/render`, the fuzz tests pass, the unambiguity test covers
every new wording, and the gate passes.

### WG-5. The constitution: strengths, conditions, switches, grants (pilot, 4–5 h)

As WG-0 (pilot branch, one commit, blind review before counting). Its edits to u0165.s01–s07 run in the hard-constraint
queue (AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → WG-5), starting from the translation as AT-6a/AT-6b left it. Translate
C-2 to C-5 (4.2): the :38-44 safety robustness sentences as the reading set {always, plain} on the safety edge with
their citations; :42's exceptions; the operator and user permission layering of :134-139 as switches and grants; the
instructable-behaviour lists of :405-423 as default rules with switches. Measure as WG-0. Required: each new grant's
effect shown through `modelCheckX` (the situation where the grantee's switch is on and the grant is off is refused,
citing `weigh:grant:<rule>:<party>`); the zone answer for each grant is WG-8's. Done as WG-0.

### WG-6. Lean: zone answers and records (Lean, 5–6 h)

Files: `lean/VE/NormDefaults/Evidence.lean` (shared owner: the `*O` definitions and `*_eq_open` lemmas of 3.4; today's
functions become the instances, statements unchanged), `lean/VE/Weighing/{Zone,ZoneExamples}.lean` (new). Shared:
`lean/VE/Audit.lean`, frozen inventory and assurance manifest (Evidence.lean re-pinned, decoder code unchanged).

`AdmissibleCompletion`, `coneValuesO`'s pruning and the `modelCheckX` check of each witness use PK-1's whole assembled
X, which includes the attitudes, scales and events packs when those profiles are on, not the weighing premises alone.
With `events@0` on, a completion is reported as a `left to` or `not said` witness only if events' calendar
completion-preservation theorem covers it; otherwise the answer is `unknown`, with events' `NotCalendar` reason.

Fixtures: Z-α to Z-ζ as `#guard`s, with the three regressions of the zone evidence: complete refutation (W-κ,
labels computed by Lean), insufficient budget (Z-δ, `unknown` naming the budget), a surviving unrefuted branch (Z-ζ,
never `inconsistent`, its reason the branch, not a budget); the bypassed W-θ documents as internal counterexamples;
every norm-defaults `-status` fixture byte-identical (`zone_extends_status`, budgets unchanged).

Deleted, not duplicated: no second Kleene evaluator, cone or enumeration; the bodies of `atomV`, `coneAtom`,
`coneAtomV`, `coneValues`, `enumerateSettled` become one-line instances of their `*O` forms (ledger lines recorded).

Done when: builds, the theorems of 3.4 are proved with the allowed axioms, the norm-defaults A/B is byte-identical,
and the gate passes.

### WG-7. Layered-route kinds and display for zone answers and records (Lean, Python, 5–6 h)

Lean: `weighing-zone` (situation, act, tuple, optional record, proposed completions) and `weighing-record`, kinds of the
layered route, run on the decoded `LayeredU` with PK-1's X, their certificates bound through `bindCertX` to the full
environment; their shapes and encoder theorems in the layered route's response-shape files. Python: `ve/weighing.py`
relays them; the untrusted search that proposes completions reuses `ve/readings_s1.py`'s search over Lean's
environment (no second search); the English of 2.6 rendered from Lean's rows; CLI `ve document zone <doc> --situation
<file> --act <phrase> [--record <file>] [--assume-no-exceptions]` in `ve/__main__.py` (shared: one subcommand). Fuzz
tests as WG-4 on both kinds.

Done when: Z-α to Z-ζ pass through the CLI, the fuzz tests pass, and the gate passes.

### WG-8. Zone probe on the constitution (pilot, 3 h)

On the pilot branch after WG-5, in the hard-constraint queue (after WG-5, one at a time with QT-B4, whichever is ready
first): for each hard constraint (u0165.s01 to s07) at the one-element situations of today's
`probes/unspecified-probe.json`, for each "should" set, and for each grant WG-5 added, record the zone answer verbatim.
Expected (C-7): `settled no` where the knowing-or-likely condition holds; `left to the assistant` where the case holds
but the condition does not, if the default reading of :457 is translated; `not said` only where the act is
unspecified and no rule speaks. No coverage is claimed from the probe; every `unknown` is listed with its reason (the
budget, or the surviving branch).

### WG-E1. Experiment: collisions between different acts (planner, 4 h)

Question: how many of the constitution's value conflicts are collisions between *different* positive acts, which
neither soft's same-act collision nor act identification ("refuse" read as "not comply") captures?

Pre-registered protocol: draw 40 units at random (seed `20261012`) from the units whose primary blocker is `norms`
and whose text hits the CROSSACT class of research 2.1, which must be written and committed before any unit is drawn
(it was: research 2.1, committed at `f904d675` before the draw; drafts 1 to 4 read "draft 1 cited it, and research
2.1 is unfilled", and weighing-phase1.md 2.1 quotes the protocol as it was pre-registered); for each, a reader
classifies the conflict it expresses as
(i) same act after identification, (ii) two exclusive positive acts, (iii) a choice of the best response among
several, (iv) no conflict between acts. The reader records the act phrases and the citation for each. A second reader
classifies 10 of them blind; agreement is reported.

Bar: build exclusive acts (WG-10) only if (ii) is at least 8 of 40 **and** at least 5 of those 8 would change a
checked answer of the translation (a conflict found or resolved). Otherwise record the result and close.

**Result: FAIL** (phase 1, [weighing-phase1.md](../research/weighing-phase1.md) 2.3 and 2.4). The pre-registration was
committed at `f904d675`, the screen and draw at `878e7345`, and the reading at `1369e004`; the second reader's input and
prompt at `111218fb` and `c999832a`, before the reading, and its answer at `1de755c6`.

- Of 669 units with primary blocker `norms`, 106 are in CROSSACT, and 40 were drawn. Tally: 10 (i), **1 (ii)**, 2
  (iii), 27 (iv). Clause 1 fails (1 against 8), and clause 2 fails (0 against 5).
- The one (ii) unit is u0204.s01 (:531): "raising concerns, seeking clarification, or declining to proceed are
  generally preferable to unilateral intervention". It states a preference, not a duty. The translation regulates
  nothing on unilateral intervention, so declaring the acts exclusive changes no checked answer.
- Second reader (a fresh Fable 5.1 session with 0 tool calls, given each unit's full span and rule 4 of the report's
  2.2). It agrees on 10 of 10 on the frozen subset, but 9 of the 10 are (iv). Post hoc, it agrees on 0 of the 3
  contested units: u0200.s01 and u0221.s04 are (ii) for it, u0274.s02 is (iv). With its calls, (ii) is 3 of 40, and
  still 0 change a checked answer.
- Post hoc, under the most generous reading, (ii) is 8 of 40, which meets clause 1 exactly. None of the 8 changes a
  checked answer, so the verdict is still FAIL.
- Limits: CROSSACT is a lexical screen, so (ii) pairs exist outside the sample (the paragraph of u0200.s01 has one).
  Clause 2 was judged against the run's translation and WG-0's planned rules, not against a WG-0 translation.

WG-10 is closed. WG-E1 did not test WG-0, WG-2 to WG-5 or WG-E2: (iv) is its catch-all category, and the constructs
(iv) units would need were not counted. This plan cites no WG-E1 number as evidence for those batches.

### WG-E2. Experiment: precedents (planner, 5–6 h)

Question: can the constitution's worked examples constrain one open decision as precedents, without inventing
factors? Protocol: pick the open decision with the most worked examples in the source (expected: the cost-benefit
judgment of :325-347, or the operator-instruction exception of :166); list its factors from the source's own lists
(:332-343); write each example as a precedent (factors present, outcome), citing its span; hold out one third of the
examples (seed `20261012`). Compile the rest into necessary and sufficient conditions by Horty's result model
(research 3.4): a case at least as strong for an outcome as a precedent with that outcome must have it.

Bar: build WG-9 only if (a) every example can be written with source-listed factors only, (b) the precedent set is
consistent, and (c) the compiled conditions force the held-out examples' recorded outcomes in at least half of them
and contradict none. A contradiction or invented factor fails the experiment.

### WG-9. Precedents compiled into decision conditions (Lean, 5–6 h; only if WG-E2 passes)

```lean
namespace VE.Weighing

/-- A recorded decision: the factors present, with their polarity for the decision, and the outcome. -/
structure Precedent where
  target : Target
  pro : List String              -- base predicates favouring the decision (true)
  con : List String              -- base predicates favouring its negation
  present : List String          -- the factors present in the recorded case
  outcome : Bool

/-- The result model: a case at least as strong for the outcome as the precedent must have it. -/
def precedentPremise (Wd : WeighDoc) (P : Precedent) : VE.Formula

def consistentPrecedents (Ps : List Precedent) : Bool :=
  Ps.all (fun P => Ps.all (fun Q =>
    !(P.outcome && !Q.outcome && P.target == Q.target &&
      (P.pro.filter (· ∈ P.present)).all (· ∈ Q.present) &&
      (Q.con.filter (· ∈ Q.present)).all (· ∈ P.present))))

/-- Consistency is exactly satisfiability of the compiled premises at every factor valuation. -/
theorem consistentPrecedents_iff (Wd : WeighDoc) (Ps : List Precedent) (h : WellFormedPrecedents Wd Ps = true) :
    consistentPrecedents Ps = true ↔
      ∀ (S : VE.Structure.{u}) (vs : List S.Carrier), ∃ b : Bool,
        ∀ P ∈ Ps, (precedentPremiseAt Wd P b).denote S (tupleVal vs)

/-- A fortiori: a case dominating a precedent is decided as the precedent was, in every structure satisfying the
    compiled premises. -/
theorem afortiori_sound (Wd : WeighDoc) (P : Precedent) (S : VE.Structure.{u}) (hS : Sat S [precedentPremise Wd P])
    (vs : List S.Carrier) (typed : VE.TupleTyped S (targetSorts Wd P.target) vs)
    (hdom : AtLeastAsStrong Wd P S vs) :
    ((targetF Wd P.target).denote S (tupleVal vs) ↔ P.outcome = true)
```

The compiled premises join `Dec_T`; nothing else changes. Deleted, not duplicated: none.

### WG-10. Exclusive acts (design batch, only if WG-E1 passes): CLOSED

**Closed by WG-E1's FAIL** (phase 1). Nothing is designed, reviewed or built, and no exclusive-act construct is
planned. Weighing still defines no exclusivity relation. The text below is kept as history: it is synthesis edit 7,
and the cross-plan issue it raises is at the end of this plan.

If WG-E1 passes, WG-10 designs and reviews a composition of `alternatives@0` (its chooser, `available` and exclusive
choice) with soft norms, and weighing consumes it. Weighing defines no exclusivity relation and does not extend soft's
colliding pairs with declared exclusive acts. Nothing is built before that composition's statements pass review.
WG-E1's bar is unchanged.

## 6. In-flight work and merge conflicts

| In-flight item (branch) | What this plan uses | How conflicts are avoided |
|---|---|---|
| RD-9 (`rd-9/lean`, `rd-9/integrate`, `rd-9/py`; plan on `design/rd-9`) | SC-1's `EntailsX`, `acceptanceX`, `conflictFreeCheckX_sound`, `modelCheckX_sound`, `softLabelledU_wellFormed`; SC-6's `LayeredAdmission.lean` and `bindCertX`; SC-8's `ve document` path for soft documents under `norm-defaults@0`; SC-9's pilot migration; SC-A's edits to `NormDefaults/Evidence.lean` | WG-3 starts only after SC-1 and SC-6 are on `main`; WG-4 after SC-8; WG-6 (the only batch editing a file RD-9 edits, `Evidence.lean`) after SC-A; WG-0 after SC-8, on the pilot branch SC-9 uses |
| design wave siblings and shared items (SYNTHESIS.md) | PK-1 (WG-3, WG-6, WG-7); AR-10's table (WG-3); QS-1 (WG-2); AP's split map (WG-2's checks); `alternatives@0` (WG-10; kept as synthesis edit 10 wrote it, though WG-10 is closed by WG-E1, so nothing consumes it: see "Cross-plan issues for the DRI"); the hard-constraint queue (WG-5, WG-8). The wordings of 2.2 and soft's reading sets for "normally", "typically", "usually" and "in most cases" are rows in english-lean's catalogue once it owns norm wordings (D12: never both) | shared files in WG-0 to WG-8: `lean/VE.lean`, `lean/VE/Audit.lean`, PK-1's provider line in `Layered.lean`/`Packs.lean` (integration order AT-2/AT-3a → WG-3 → ET-4 → QT-B2), AR-10's table row, `ve/document.py` (the document-mode queue after `lf-16g`: AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10), `ve/norm_english.py`, `ve/__main__.py` (append-only edits; merge-train regenerates generated files with `regen_generated.py --resolve`) |
| lean-first and arch items (`infra/arch-AR-*`, lf-14 to lf-18) | AR-13's diagnostic codes (DRI D6) | new diagnostics are texts until AR-13 lands, then take its codes in the batch after |

Every shared file a batch touches is listed in its section. New code goes in new files (`lean/VE/Weighing/*`,
`ve/surface/weighing.py`, `ve/weighing.py`, `tests/test_weighing_*.py`). Generated inventories are regenerated by
their tools, never hand-merged.

## 7. The measure

Coverage is measured as soft-norms-PLAN 4 requires: a unit changes status only after end-to-end admission through
`ve document`, against a baseline of the same split at the same commit, and after a blind whole-span fidelity review;
claimed and audit-verified bytes are reported separately; no figure is predicted (draft 1's estimates cited research
5.2, which is unfilled, and are withdrawn). Zone answers are reported as counts of `settled`, `left to`, `not said`,
`inconsistent` (each with the labels Lean computed) and `unknown` answers (split by reason: budget or surviving
branch) on the probe set, never as coverage.

**Measured so far (phase 1, WG-E1).** These numbers describe WG-E1's sample, not the pilot as a whole, and none of them
replaces a pilot-effect estimate of WG-0 to WG-8. Units and verdicts come from weighing-phase1.md 2.3 and 2.4. Bytes
are the units' span lengths: the spans in `wg-e1-sample.json` are byte offsets into the pinned source, joined with the
categories of `wg-e1-classification.json`, and this draft sums them from that saved evidence. Nothing is extrapolated
to the 106 CROSSACT units or the 669 `norms` units.

| Measure | Units | Bytes |
|---|---:|---:|
| Units with primary blocker `norms` (run `20261012T1800Z`) | 669 | — |
| of those, in CROSSACT | 106 | — |
| drawn (seed `20261012`) | 40 | 8,104 |
| (i) same act after identification | 10 | 2,146 |
| of which name refusing (u0147.s04, u0179.s02, u0137.s02) | 3 | 527 |
| (ii) two exclusive positive acts (u0204.s01) | 1 | 131 |
| (iii) best response among several | 2 | 264 |
| (iv) no conflict between acts | 27 | 5,563 |
| (ii) that would change a checked answer: WG-10's measured effect | 0 | 0 |
| (ii) with the second reader's calls on the contested units (u0204.s01, u0200.s01, u0221.s04) | 3 | 464 |
| of those, changing a checked answer | 0 | 0 |

## 8. Not claimed, risks, open questions

- **Not claimed.** That any finding of a decider is right; that a decider considered the listed factors; completeness
  of the zone search (`unknown` is honest); completeness of the implication check (it says "cannot show");
  completeness of the classification of colliding pairs beyond soft 9.5; anything about collisions between different
  acts (WG-E1 failed, and WG-10 is closed); any speed. That X is conservative: through soft coherence, switch and
  override conditions can leave a situation with no admissible decision assignment, and `X` can then entail base
  facts (in W-κ the premises entail `urgent`). Weighing is a constraint on existing decisions, not a conservative extension; its guarantee is
  `weigh_alone_base_free`.
- **Risk: false comfort from "settled".** A `settled` answer is about the rules on one act at one situation, under the
  document's premises; it says nothing about other acts or about whether the situation is described correctly. The
  English says "the text requires", never "the assistant should". A situation with no admissible completion is
  "inconsistent at this situation" when Lean refutes every branch of a complete enumeration, else `unknown`; never
  "settled".
- **Risk: residual size.** Strength and conditions add premises, not decisions, so the residual does not grow; grants
  add none either. Zone answers can name many questions; WG-7 shows at most five, then "and <n> more".
- **Risk: reading drift on "always".** "Safety always outranks ethics" is a translator's reading of :40, never the
  only one: C-2 keeps the reading set. WG-0 and WG-5's blind review audits it.
- **Risk: RD-9 and the shared items slip.** WG-0, WG-3 to WG-8 wait on RD-9; WG-2 waits on QS-1; WG-3, WG-6 and WG-7
  wait on PK-1; WG-3 on AR-10's table. The risk has started to show: on 2026-10-13 WG-0 is DEFERRED because SC-8 is
  not on `main` (5.0). WG-1 does not wait on RD-9, WG-E1 is done, and WG-E2 waits only on WG-2.
- **Dependency, not a batch: refusals as not doing the act.** The three sampled WG-E1 units that name refusing
  (u0147.s04, u0179.s02, u0137.s02; 527 B) are (i). Refusing or declining to assist, or giving an unhelpful response,
  is not doing the requested act. A weighing condition can target units like these only after AP's act identity
  (AP-1 to AP-3) identifies "decline to assist", "refuse to assist" and "unhelpful response" with not doing the
  requested act; then soft's same-act collision applies. This is consistent with D6 and synthesis edit 8 but does not
  test them. The other seven (i) units are of other kinds and are not evidence for this line.
- **Open question (WG-1).** Is D4's "some chain contains `always`" the reading readers take from "always outranks"?
  WG-4's unambiguity test and a Sonnet 5.5 comprehension check (as RD-9's SC-9 does) on three paraphrases are the
  evidence; the check is saved evidence under the batch's `docs/<batch>/`, not a suite test (suite tests make no
  model calls); the DRI decides if they disagree.

## 9. Review checklist (WG-1)

1. D2 and D3: `weighing@0` changes no byte, decoder, statement or answer of `soft-norms@0` or `norm-defaults@0`
   (`weigh_conservative`, `wellFormedWeigh_empty`, `runWeigh_delegates`, `zone_extends_status`), and claims no
   conservativity beyond `weigh_alone_base_free`.
2. D4's closure: `strictPair_down`, `strictPair_up`, `holistic_iff_no_always_chain` (through QS-1); the paraphrase of
   2.2.
3. `always_dominates`, `always_no_override` (on the override disjunct), `all_always_is_strict` against soft's
   `DomWithD`.
4. Conditions and grants: their premises, `ConditionOnStrictPair`, `propImplies_sound` and its 12-atom bound,
   `condition_necessary`, `condition_sufficient`, `factors_inert`, `grant_needed`, `grant_within_grantor`,
   `delegation_bounded`, `DelegationCycle`, the fragment gate; `strength_iff` with its declared-name hypotheses.
5. The route: the `weighing` pack, `weighPremises_wellFormed`, `weigh_acceptance` and `weigh_conflict_free` at PK-1's
   X, `stripWeighing_other`, `stripCase_idem`, `weighGate`, `runWeigh_delegates` under `hg`, `weigh_identity`; the
   order gate, stripped document, block (2.5); `rights@0` refused by the row.
6. Zone: the definitions of 3.4, the pruning by X, settled with a checked completion, the four soundness theorems, the
   separation of `left to` from `not said` and both together (D9), "inconsistent at this situation" and "ruled out"
   only from a complete enumeration with every branch refuted and labels Lean computed (`zone_ruledOut_sound`'s three
   conjuncts), `unknown`'s checked reasons (never a budget after a complete enumeration), and that no evaluator is
   duplicated (D8).
7. The wordings of 2.2: one reading each, E7 by its resolution; pairwise defeat, never a promise that the higher rule
   finally decides; no symbol in what a reader sees.
8. The two experiments' bars, fixed before any data is read. WG-E1's was fixed first (`f904d675`), and it failed
   (5.0). WG-E2's stays as written.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-10-12 | Draft 1 | Plan for the design recommended in docs/research/weighing.md: decisions D1 to D14; `weighing@0` (strength, override and switch conditions, grants) as premises on open decisions over RD-9's generic `X`; zone answers and decision records on norm-defaults' widened three-valued machinery; Lean statements; fixtures W-α to W-ι, Z-α to Z-ε and C-1 to C-7; batches WG-0 to WG-10 with dependencies and shared files; two pre-registered experiments. Planning only. |
| 2026-10-13 | Draft 2 | The converged debate (rounds 1 to 3) and the cross-plan synthesis edits 1 to 10. Debate: `settled` prunes by X and needs a checked completion (E1); `ConditionOnStrictPair`, the propositional `ConditionsDisagree`, no sufficient switch condition (E2, reduced); grants inherit the grantor's conditions along the chain with one generator, `grant_within_grantor` (E3); `runWeigh_delegates` restated without the identity fields (E4); `generally` an input synonym, only `always` on the wire, the upward-closure and plain-edge paraphrases (E5); fixtures name their records; `ZoneAnswer` carries both witness sets and a no-completion result; `always_no_override` on the override disjunct; factor paraphrase; budget a parameter (12 and 16); build order WG-2 → WG-3 → WG-4 → WG-5 → WG-6 → WG-7 → WG-8 with the grant evidence split between WG-5 and WG-8; research-cited unit ids and estimates withdrawn. Synthesis: `weigh_alone_base_free` and W-κ, no global conservativity (1); X assembled by PK-1, `weighX` deleted (2); no `weighing` mode, two layered-route kinds (3); AR-10's row and WG-3's slot (4); `strictPair` through QS-1 (5); zone answers on the whole X, events' `NotCalendar` (6); WG-10 through `alternatives@0` (7); split names, W-λ (8); the hard-constraint queue (9); dependencies and the english-lean catalogue (10). WG-1's item-1 statement spec is weighing.md. |
| 2026-10-13 | Draft 3 | The statement review of weighing.md draft 1 (`manage-agents/debates/weighing-spec/`, FIX, `DRI-RULING.md` items 1 to 14), synchronised with weighing.md draft 2. `strength_iff` in 3.2 with `hL`, `hH`, `ha` (1); `runWeigh_delegates` under `hg`, total `stripWeighing`/`stripCase`, `stripCase_idem`, `weighGate`, the seven-field `core`, rebound certificate packages (2, D11, 2.3, 3.3, W-η); E1/E2 as pairwise defeat by an effective higher rule, W-α with h excepted (3); E4's "Outside this condition, …", θ11 (4); E7's resolution and the explicit form (5, 2.2, WG-4); grant cycles refused (6, D7, 2.5); `condition_necessary`, `condition_sufficient`, `factors_inert` (7, 3.2); W-μ and its seeded bugs (8, WG-2); zone evidence: `ruledOut`/`inconsistent` with label lists from a complete enumeration, `ZoneUnknown`'s checked reasons, labelled X, `labelsOf`, `zone_ruledOut_sound`'s three conjuncts, W-κ's five labels, Z-δ and the new Z-ζ (9, 0, D9, D10, 2.6, 3.4, 7, 9); 2.5's order gate, stripped document, block, and the combined fault (10); `maxPropAtoms = 12` with boundary fixtures (11); `rights@0` refused by the row (12, D2, WG-3); the comprehension check as saved evidence (13, 8, WG-4). |
| 2026-10-13 | Draft 4 | The bounded re-check of weighing.md draft 2 (`manage-agents/weighing-p3ver1.final.md`, FAIL on ruling item 1), synchronised with weighing.md draft 3 (F13). Item 1's two falsifying regressions are now the lower rank `b_` (F9) and ranks `c > c_` queried at `(x_permitted, c, _c)` (F13); the ruling's `c`/`c_` document with an undeclared act is a collision the unrestricted statement survives (F10). 3.2's `strength_iff` docstring, 4.1's W-α and WG-1 updated; no statement changed. |
| 2026-10-13 | Draft 5 | Phase 1's results ([weighing-phase1.md](../research/weighing-phase1.md), reviewed FIX and fixed), synchronised with weighing.md draft 4. WG-E1 FAIL (1 of 40 (ii), 0 changing a checked answer; second reader 10 of 10 on the frozen subset, 0 of 3 on the contested units): its row, section, D14 and 9.8 record it. WG-10 closed, kept as history. 2.7 and 8 make collisions between different acts residual. WG-0 DEFERRED with its trigger (RD-9 SC-8 on `main`). New 5.0 status table (WG-E2 and WG-9 DEFERRED with their triggers). 7 gains WG-E1's measured counts and sampled bytes. 8 gains the refusal-identity dependency on AP. The header's research-placeholder sentence is corrected (2.1 is written). No Lean statement, wording, diagnostic, fixture or cross-plan edit changed; `alternatives@0` (WG-10) stays in 6 as edit 10 wrote it, and the conflict is raised under "Cross-plan issues for the DRI". |

## Cross-plan issues for the DRI

Phase 1's results conflict with one shared part. It is kept above as the cross-plan edits wrote it and is raised here
for the DRI; this plan does not change it.

1. **`alternatives@0`'s weighing consumer no longer exists.** WG-E1 failed, so WG-10 is closed
   (weighing-phase1.md 3, item 1, which proposes removing the dependency). The shared text still names WG-10 as a
   consumer:
   - synthesis edit 7 (WG-10's body; kept as history in WG-10's section);
   - synthesis edit 10's dependency list, "`alternatives@0` (WG-10)" (kept in 6's design-wave row, marked as having no
     consumer);
   - SYNTHESIS O9's row, 2.9 ("WG-10 consumes a reviewed alternatives/soft composition") and C17.

   This plan's own wording follows the result: 2.7's residual line and 8's "Not claimed" no longer point to WG-10
   through `alternatives@0` (weighing.md 8 likewise), and D14 keeps edit 7's rule with the outcome added.

   Unaffected: O9's ownership. `alternatives@0` still owns exclusive choice, and weighing still defines no
   exclusivity relation. [alternatives.md](alternatives.md) does not name WG-10.

   **For the DRI to decide:**
   - (a) whether to drop WG-10 from O9's "plans" column, from 2.9's "What the plans do" cell and from edit 10's list,
     and to mark edit 7 as void;
   - (b) whether any weight given to `alternatives@0` for weighing's sake (in its plan's priority or in NORTH-STAR's
     "priority across different obligations" row) should be lowered. WG-E1 measured 1 of 40 sampled CROSSACT units
     (131 B), with a 95% upper bound of 0.13, and 0 B of checked answers. Soft 4.5's stage 3 and that NORTH-STAR row
     may cite this result.

   Until the DRI decides, nothing in this plan depends on `alternatives@0`.

Not conflicts, for the record: WG-0's deferral leaves SYNTHESIS 4.1's "WG-0 runs once RD-9 SC-8 is on `main`"
unchanged. WG-E1 ran in phase 1 under its own gates, as 4.1 lists it. The hard-constraint queue (4.4), PK-1's
integration order, AR-10's row, QS-1 and AP's split map are untouched by phase 1.
