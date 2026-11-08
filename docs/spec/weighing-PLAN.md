# Weighing competing considerations (`weighing@0`): buildable plan

Synthesis round 2 (2026-10-29): the DRI-decided edits of `manage-agents/debates/plan-synthesis-2/edits-weighing.md`
(items 1 to 8) are applied in place below; its item 9 is the plan steward's PLANS-INDEX row.

## Changes in this revision (wg-rev, DRI 2026-11-02 fp-weighing item 1)

The weighing fidelity pilot of 2026-11-02 (`manage-agents/reviews/fidelity-pilot-20261102/weighing/`, 4 of 10,
REVISE) found WG-R1 to WG-R5. `reviews/dri-decisions-20261102-fp-weighing.md` item 1 orders each fix, and this
revision applies them as ordered. The pilot read this plan at `bda82d18c`; this revision starts from `1ae4b7402`.
The new writing rules are 2.8, and its GAP-W names are listed there with their owners.

1. **WG-R1 (A), the strength choice** (2.8 W-R1, 4.2 C-2, WG-5, 8): the choice between `always outranks` and plain
   `outranks` is refused under profile-composition rule 8 as GAP-W1. C-2 no longer expects a reading set. No PC form is
   requested.
2. **WG-R2 (A), E5 only on a stated collision** (2.8 W-R2, 4.2 C-8 and C-9, WG-5): no frame rule is added to give E5
   a target. Considerations with no stated collision go to soft's `factors` on the rule the source ties them to, or to
   GAP-W2. `targetCheck` and `NoSuchDecision` are unchanged. No target-less E5 is needed.
3. **WG-R3 (B), considerations copied verbatim** (2.8 W-R3, WG-E2): every consideration in the quoted form, so a
   comma or "and" stays inside it; one string per item; a verbatim head for an item over 200 bytes, with the rest
   stubbed or GAP-W3.
4. **WG-R4 (B), rank claims** (2.7, 2.8 W-R4): a general uncertainty about rank is GAP-W4. A rank clause inside an
   analogy's frame is no rank edge.
5. **WG-R5 (B), the summary and the cost-benefit verdict** (0, 2.7, 2.8 W-R5, 6.1): GAP-W5a (a verdict the text
   states that a cost is worth a benefit) and GAP-W5b (an equal-weight statement). The summary now claims only what
   the plan builds. Request rows go to quantities and judgment-terms. `docs/research/weighing.md`'s matching line is
   outside this revision's two files and is left as it is; this plan's 0 governs.
6. **C point** (8): "err on the side of" is added to the open points.
7. **OPEN-1 to OPEN-11** (weighing.md 10): marked RULED (`reviews/dri-decisions-20261102-wg-1.md` items 2 to 4).
   OPEN-5's request row is added to 6.1.

Statements: no Lean statement of WG-2 or WG-3 changes, and neither does any en-wg statement, wire field, diagnostic
text or W fixture. The fixture changes are WG-5's real-unit rows only: C-2's expected answer, and the new C-8 and C-9.

## Changes in this draft (refresh 2026-10-28)

Draft 6 applies the refresh debate's adopted position (`manage-agents/debates/refresh-weighing-20261028/`; DRI ruling
`reviews/dri-decisions-20261028-weighing-refresh.md` item 1, (a) to (g) and the order) to main at `6d0a10526`. Rounds:
A*n* is `astra.md` round *n*, F*n* is `fable.md` round *n*; "DRI (x)" is the ruling's item 1 (x).

1. **Current status replaces the historical dependency claims** (0, 5, 5.0, 6, 8): RD-9's core, PK-1, AR-10, QS-1
   and AP's `SplitMap` are on main. The 06:00Z pilot's soft chain loads and then fails `check`, so a **NEW
   RD-9-owned document-routing repair** comes before WG-0 and WG-5. WG-0 also needs the part-document design. SC-9's
   migration and source audit stay pending. (A1 item 1; F1 disputed point 4; F2)
2. **The profile row** (D2, D11, 2.5, 3.3, WG-1, WG-3): `requires` gains `norm-defaults@0`, the slot is `pack`
   (synthesis round 2, N1: draft 6 said `layer`), with `interface` value `.pack "weighing"`, and
   the `rights@0` refusal comes from `refusing`, without the prefix. D11's "whether or not `norm-defaults@0` is on"
   and WG-1's question about it are deleted. (A1 item 3; F1 disputed point 2; A2; F2)
3. **PK-1 and the kind table as built** (D3, D11, 3.3, WG-3, WG-7): `Pack.consts := []`; `LayeredU.core` reads
   `packs`; `assemble U used ps`. The two kinds are `Packs.KindRow` rows. WG-3 widens `runOtherCase`'s forwarding,
   `decodeSoftU`'s pack list and pack-leaf recognition, adds regressions where a weighing premise changes an
   admission and a certificate, and adds relay-inventory rows. (A1 item 3; A2 disputed point 2; F2)
4. **Duplicates removed** (3.3, WG-3): `dropField` is `Risk/Wire.lean`'s. The profile list is filtered by
   generalising `withoutDocumentLayers`; weighing is not a document layer. (A1 item 3; F1 disputed point 3; A2
   disputed point 3; F2)
5. **English** (D12, 2.2, WG-4, 6): Lean owns the templates, paraphrases, resolution and diagnostics, and Python binds
   and displays the returned records. A NEW english-lean item, **en-wg**, reads the sentences. WG-4 shrinks to
   binding, display, document dispatch (`ve/document/`) and fuzz tests. (DRI (a), (b); A3 items 1 and 2; F3 point 3)
6. **Acceptance checks** (4.1, WG-4): source/object disagreement is detected (seeded bugs: drop `always`; swap
   necessary and sufficient). Two readers until E3, tested for disjointness with C-2's minimal pair and the soft-frame
   refusals. (DRI (c), (d); A3 item 3; F3 point 1)
7. **"generally" is a D6 word.** Its row goes into en-sw's `SourceWords.lean`. Soft's frequency rows stay with
   their owner. (DRI (e); F3 point 2; F1 disputed point 1; F2)
8. **Zones** (3.4, WG-6): `zoneOf` takes an explicit atom list `opens` (DF1, JT-R1). Defeasible owns
   `DefaultCompletion`, and weighing keeps its record (DF2). (A1 item 4; F2)
9. **New section "Shared pieces"**: each NEW piece with its closest existing definition and owner, D6 and D8 named.
   (A1 item 4; A2; F2; F3 point 2; DRI (b), (e), (f))
10. **D8**: the zone vocabulary is NEW, pending synthesis round 2; situation wording reuses `VE.Words`. (F2; A3;
    DRI (f))
11. **`acts@0` refuses soft norms** (D6, 5, WG-5): an act-phrases-owned prerequisite is named, and the refusal stays
    until it is proved. AP-3 Group A joins the hard-constraint queue before WG-5. (A1 item 5; F1)
12. **Measures** (4.2, 7): re-anchored on run `20261028T0600Z`. The census puts WG in either role on 132 units,
    25,225 B; these are census bytes, not forecasts. Phase-1 evidence is kept as history. (A1 item 6; F1)
13. **WG1 (a) and (b) applied** (6, D14, WG-10, "Cross-plan issues"): the `alternatives@0` dependency is removed,
    WG-10 stays closed, and no cross-plan issue is open. (A1 item 6; F1)
14. **Build rules** (5): standing rulings apply where their condition holds, decisions no ruling covers stay, and the
    committed `gate-collection.json` instructions are removed. (A1 item 7; F1)
15. **The wider E3 migration** of soft's frames is governed by signed edit 10 ("once it owns norm wordings"). No DRI
    signature is reserved. (DRI (g); A3 item 4; F2; F3)
16. **Order and M10's path** (5): as the ruling orders. (DRI order; A3; F3)

17. **Checker fixes** (completing items 3 and 8): an absent block contributes no pack (D11, weighing.md 3.2 step 5),
    so `runWeigh_delegates`' `core`, which reads `packs`, is equal on both sides. `enumerateSettledO` takes the ground
    atoms it enumerates as a parameter `atoms` (DRI DF1), with today's cone `coneAtoms U M n vs` in the legacy
    equations (`enumerateSettled_eq_open`, `zone_extends_status`) and DF-5's `openAtomsAll` as another argument;
    `opens` stays the open predicate names (JT-R1) (D8, 3.4, WG-6, 6.1). (A1 items 3 and 4; F1; F2)
18. **The research note** ([docs/research/weighing.md](../research/weighing.md) 0 to 2, 5 and 6) is refreshed with
    item 1's status and item 12's anchor and census, and WG1 (a) is applied there; its own list says which part.
    (A1 items 1 and 6; F1)
19. **DRI decisions after the apply step** (`dri-decisions-20261028-weighing-refresh-apply.md`): the comprehension
    check's tie-break is decided in advance, in the conservative direction (8); `VE.Acts.splitRefusal`, which
    weighing.md 1.6 calls, is not on `main`: WG-2 factors AP's inline split-predicate refusals out of
    `Acts/Elaborate.lean` into it with byte-identical texts (WG-1 fixes its signature); WG-3 recomputes the gate
    refusal texts where it places the row (WG-3). (DRI)

## Changes in draft 5 (2026-10-13)

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

> Status: plan draft 6 (2026-10-28), branch `refresh/weighing-20261028` from `main` at `6d0a10526`: the refresh
> above, checked against main as it is now. Draft 5 (2026-10-13) was on `research/weighing-p1`. Where draft 5's text
> below names RD-9's branches (`rd-9/integrate`) or calls PK-1, AR-10, QS-1 or AP's split map unmerged, that is
> history: all of them are on main (5.0).
>
> Draft 5 (2026-10-13), branch `research/weighing-p1`; draft 4 was on `design/weighing` from `main` at
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

What this plan builds is narrower than that list (wg-rev, WG-R5). The rank decisions themselves are soft's, on main:
an `outweighs` decision between two ranked rules that collide on one act. On those decisions the plan builds
`always` strength marks, conditions and declared factors. It also builds conditions on switches, grants, and zone
answers and records over the open decisions. Costs against benefits are
weighed only where they are such a decision. Operators' wishes against users' interests are weighed through switches
and grants (C-4, C-5). The plan builds no verdict the text itself states that a cost is worth a benefit (GAP-W5a,
2.8), and no statement that two considerations weigh equally (GAP-W5b).

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

**The first batch that moves a pilot number** is WG-0. It has no product code: it writes the constitution's value order
and the hard constraints' immunity with what `soft-norms@0` already offers, once a soft document beside
`norm-defaults@0` is checked end to end through `ve document`. Draft 1's estimate of its effect cited research 5.2,
which is unfilled. That estimate is withdrawn, and WG-0 measures instead.

WG-0 is still **DEFERRED** (5.0). RD-9's core is on main, but routing is not. In the 06:00Z pilot of 2026-10-28, the
soft-chain probe loads and then fails `check` with "norm-defaults@0 documents are checked through fill", because the
document path still sends the soft admission route under `norm-defaults@0`. A **NEW RD-9-owned document-routing
repair** comes first. WG-0 also needs the part-document design, because the whole constitution exceeds L70.

## 1. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | Weighing stays a set of named open decisions with deciders. The checker certifies structure, bounds and coherence, and answers where the weighing matters; it never computes an "all things considered" verdict | VISION converged rule item 8 ("unconstrained weighing" is outside certification); soft 0; the source itself delegates the judgment ("we do want Claude to weigh these different priorities", :34) | an inside-the-checker weighing (numeric or argumentation-based), research 4.4 and 4.5 |
| D2 | A new profile `weighing@0` requires `norm-defaults@0`, `soft-norms@0` and `norms@0`, registered as one row of AR-10's profile-gate table (`Compose/Dispatch.lean`'s `baseRows`: `⟨"weighing@0", ["norm-defaults@0", "norms@0", "soft-norms@0"], refusing "weighing@0" ["rights@0"], "pack"⟩`, with its `interface` value `.pack "weighing"` (profile-composition PC-3 adds the slot; synthesis round 2, N1) and the row's composition proof; `rights@0` stays refused until AR-10's composition proof and a fixture both cover that combination). The refusal text is the table's `refusing` text (`weighing@0 with rights@0`), and `gateOf` adds the `UnsupportedProfile:` prefix. The row also adds a new environment block `weighing` beside the vocabulary's `soft` block. `soft-norms@0`'s bytes, decoders, identities, statements and answers do not change; a document without the block is a soft document (WG-2 `weigh_conservative`) | VISION converged rule item 2 (meaning freeze; extensions are new profiles); soft 3.1's strict decoder rejects unknown fields, so the block cannot live inside `soft`; AR-10's table is the one place a profile is registered | new fields in the `soft` block; a `soft-norms@1`; hand-written profile registry rows |
| D3 | Every `weighing@0` construct is a **condition on an open decision**, elaborated into labelled base premises `Weigh_T`. `Weigh_T` is PK-1's `weighing` pack (`kind := .constraint`, `decls := []`, `consts := []`, `labelled := weighLabelled Wd`, `origins`: each label ↦ the request path of its entry in the `weighing` block, `conditions := weighConditions Wd`: each sufficient condition with its decision, profile-composition 1.9); PK-1 assembles X in its fixed order (soft, rights, weighing, attitudes, scales, events), and RD-9's `EntailsX`, `acceptanceX`, `conflictFreeCheckX_sound`, `modelCheckX_sound` apply to it. Weighing constrains existing decisions: its local checks guarantee `weigh_alone_base_free`, and there is no global conservativity claim (8) | soft's exception conditions (`Exc_T`) are already this shape; RD-9 proves the checkers sound for any typed `X`; PK-1 is the one assembler of X; so the only new proof obligations are typing, the meaning of the premises and conservativity at the wire | changing `ValueSoft` or `soften`; a second premise pipeline; an assembly of X in `Weighing/*` |
| D4 | **Strength.** A declared edge "a outranks b" may be marked `always`. A rank pair `(H, L)` with `H` above `L` is **strict** when some chain of declared edges from `H` down to `L` contains an `always` edge, and **holistic** otherwise; it is computed with QS-1's reachability (`strictPair H L := some always edge (a, b) with H at least a and b at least L`, `VE.Closure.Order.atLeast`). A strict pair contributes `∀x̄. ¬outweighs_{a,L,H}(x̄)` for every act `a` on which the pair's rules collide | one rule a reader can apply ("a lower rank can outweigh a higher one only if no step between them says *always*"); it is monotone both ways (`strictPair_down`, `strictPair_up`), so "safety always outranks ethics" also protects safety from guidelines and helpfulness; the closure is QS-1's, never weighing's own | strictness per declared edge only (it would let guidelines outweigh safety while ethics cannot, research 4.1); strictness only on the first edge; a rank closure in `Weighing/*` |
| D5 | `always` under the holistic flag removes the override; under the strict flag it is accepted and inert, with a warning (`StrengthInert`). A plain "a outranks b" keeps the flag's meaning. "a generally outranks b" is an input synonym of the plain sentence, shown as the plain sentence; under the strict flag the English layer refuses it (`GenerallyUnderStrictOutranking`). The wire carries only `always` edges | under the strict flag no `outweighs` decision exists (soft 1.3), and creating one would change `E′`, so `soft-norms@0`'s vocabulary would change; a strength with no formal effect on the wire would break the rule that every construct is a premise (debate E5) | creating `outweighs` atoms under the strict flag; a `generally` strength on the wire |
| D6 | **Override and switch conditions** have soft's exception-condition form: quantifier-free base formulas over the target's argument sorts, naming base predicates of `E` only; factor lists are strings with no premise. Weighing may constrain decisions, never the world on its own: a condition on an `outweighs` decision of a strict pair (D4's closure) is refused (`ConditionOnStrictPair`); a sufficient condition must be shown to imply each necessary condition on its target by a propositional check proved sound in Lean (`ConditionsDisagree`, text "the checker cannot show that condition i implies condition j"; sound, not complete; it never searches, so it never exhausts a budget); a sufficient condition on a switch is refused. A target that names a rule or act `acts@0` split is refused with AP's diagnostic ("name one of its parts"), read from AP's `VE.Acts.SplitMap`, never re-derived; a target may name a generated part. `SplitMap` is on main, but that does not make the two profiles compose: `acts@0` refuses `soft-norms@0` (`actsRefuses`, `Compose/Dispatch.lean`). So a weighing document has no split map until an **act-phrases-owned prerequisite (NEW)** admits `acts@0` with soft norms, and the refusal stays until that prerequisite is proved | soft 3.2 and 6.1's fragment gate carry over unchanged, so `Weigh_T` stays in the universal function-free fragment; without the two checks a sufficient condition would make X certify a fact about the world (debate E2); AP owns act identity (synthesis edit 8) | conditions over regulated or decision predicates (circular and outside the fragment); a tableau search for the implication; re-deriving a split |
| D7 | **Delegated switches.** "<Party> may turn off rule n only where <grant>" is a necessary condition on `off_{n,party}`; a grant names its grantor, and the grantor must itself hold a switch on rule n (`DelegationExceedsGrantor`) and the grant's predicate must be attributed to the grantor (`GrantNotAttributed`). The grantee's switch also carries every necessary condition on the grantor's switch and the grantor's own grants, along the whole grant chain (`grant_within_grantor`); every inherited condition is written out in the English. A grant premise is the necessary `.off` case of the one condition generator (`condPremise`). Grant cycles, self-grants included, are refused (`DelegationCycle: rule <n>, <party>`), an explicit restriction of `weighing@0`, not a soundness necessity | :138; the bound is a structural check, decidable and stated as a theorem (`delegation_bounded`), and the inheritance carries :138's meaning, which the structural check alone does not (debate E3) | a general authority logic (research 4.6); a separate grant generator |
| D8 | **Zone answers** reuse norm-defaults' three-valued machinery (Kleene evaluation, cones, bounded enumeration, `kleene_sound`, `settled_of_enumeration`) with the set of *open* atoms widened from the unsaid atoms to the unsaid atoms and the decision atoms. The widening is made once, in its owner file `NormDefaults/Evidence.lean`, with today's functions as the instance "open = unsaid" (`rfl`) and the enumeration budget a parameter (norm-defaults keeps 12, zones use 16). The list of ground atoms enumerated is an explicit parameter of the enumeration (`atoms`; DRI DF1), with today's cone the argument at every current call, and `zoneOf` takes the open predicate names `opens` (JT-R1), with weighing's answers the instance `opens = openNames L`. So defeasible's DF-5 passes `openAtomsAll` and judgment-terms' JT-4 passes its own `opens` without editing a weighing file. The enumeration prunes the assignments that Kleene evaluation refutes against PK-1's whole assembled X and `Fill_T`, as `coneValues` already prunes by `Fill_T` | one owner of three-valued evaluation; norm-defaults' answers stay byte-identical; without pruning by X an outcome that only a weighing condition settles stays UNKNOWN (debate E1) | a second Kleene evaluator in `Weighing/`; Python enumeration; an enumeration that ignores X |
| D9 | A zone answer separates **left to <decider>** (two admissible decision assignments, same filling, opposite outcomes) from **not said** (norm-defaults' UNDECIDED: same decisions, two fillings) and carries both witness pairs when both hold. "Settled" is claimed only from a complete enumeration of the cone or a replayed certificate **and** one admissible completion checked by `modelCheckX`; without that completion the answer is UNKNOWN. With no admissible completion the answer is **inconsistent at this situation**, citing a premise Kleene evaluation refutes, or on every branch of a complete enumeration the premise that refutes it (labels recomputed by Lean, deduplicated and sorted), or UNKNOWN when neither holds, with the reason Lean checked: the budget exceeded (the enumeration incomplete), or a surviving branch it could neither refute nor confirm; never a budget after a complete enumeration | the constitution sends "unclear or uncertain" hard-constraint cases to "holistic and nuanced prioritization" (:457): today those come out UNDECIDED, which reads as "the text does not say", the wrong message; a "settled" with no admissible completion is vacuous | one UNDECIDED for both; settled without a checked completion |
| D10 | **Decision records** (a decider's findings in a situation) are checked with the zone machinery with the recorded atoms fixed: ADMISSIBLE with the outcome (and what is still open), RULED OUT with the violated premises' labels rendered as their sentences (no admissible completion agrees with the record, and Kleene evaluation refutes that premise with the record fixed, or on every branch of a complete enumeration), or UNKNOWN with its checked reason | this is the one place a checker can audit a judgment it does not make: consistency with the document's bounds, not correctness | judging whether the finding is right |
| D11 | **No new service mode.** A `weighing@0` document is a layered-route document: the layered decoder validates the original envelope and profiles (`weighGate`, before anything is stripped), hands the soft decoder the environment without the block (`stripWeighing`), decodes the block, checks `WellFormedWeigh` and, when the block is present, gives PK-1 the `weighing` pack; an absent block contributes no pack, so the case decodes as its stripped case (`runWeigh_delegates`). The layered route's existing kinds (`-elaborate`, `-conflict`, `-status`, `-report`, `-certificate`, `admission`) answer weighing documents directly; `weighing-zone` and `weighing-record` are two new kinds of the layered route, run on the same decoded `LayeredU` with PK-1's X, their certificates bound through `bindCertX` to the full environment. The layered branch runs only when `norm-defaults@0` is listed (`hasProfile`, `NormDefaults/Run.lean` `runOtherCase` and `runCase`), so `weighing@0` requires it (D2). Without `unspecified` predicates the extra profile has no effect: `fill U = U.D` and `Fill_T = []` (`fill_conservative`). On main the route reaches only soft packs and its own kinds, so WG-3 widens four places, and each is required. (i) The two kinds are `Packs.KindRow` rows beside `Defaults/Route.lean`'s `defaultsRows`. (ii) `runOtherCase` forwards them, since today it forwards only `norm-defaults-*` and `defaultsKinds`. (iii) The pack list that `decodeSoftU` assembles (today `[softPack U src.D]`) gains the weighing pack when the block is present, and nothing when it is absent. (iv) Admission and certificate replay recognise a regenerated premise of any pack (today `SoftLeafX` accepts the `"soft"` pack only), so the existing kinds consume the complete regenerated pack list and full identities. Regressions show a weighing premise changing an admission answer and a certificate answer | one route for every `weighing@0` answer; profile-specific answers are layered-route kinds (SYNTHESIS O3, C9) | a `weighing` service mode; extending `ve_soft_norms_route` (meaning freeze) |
| D12 | English: each new wording has one reading and a deterministic paraphrase; decision predicates, labels and formulas never appear in what a reader sees (zero-training English). **Lean owns** the weighing templates, the paraphrases, E7's resolution and every diagnostic with its text; **Python binds and displays** the returned records (passive display records, no wording text or matcher of its own). The sentences are read by **en-wg** (NEW, owned by english-lean). en-wg reads the original sentence through the shared grammar machinery (closest abstraction `lean/VE/EnglishGrammar/Actions.lean`, which today produces formulas, terms and declarations; a weighing-statement value type is NEW) and returns the weighing object, embedded conditions included. There is no separate weighing matcher. Until E3 there are **two readers**: soft's plain *outranks* stays in Python's `parse_declaration` (`ve/surface/softnorms.py`), while E1 and the input synonym *generally outranks* are en-wg's. The one-reading argument (weighing.md 2.4) is therefore a disjointness claim, and it is tested. *generally* is a D6 word, so its row goes into en-sw's `SourceWords.lean` beside soft's rows, not into a weighing table (C1). Weighing owns only the rank-frame row; the plain normality frame stays DF-4's (hedges-generics item 2(a), DF3). Soft's reading sets for "normally", "typically", "usually" and "in most cases" stay with their owner, and this plan moves none. The wider E3 migration of soft's existing frames is governed by signed edit 10 ("rows in english-lean's catalogue once it owns norm wordings"); no DRI signature is reserved for it | one owner per wording; Lean owns meaning and acceptance, so Python interprets no new frame (DRI (a), (b)) | symbols, rank numbers or weights in the text; a Python wording table or frame matcher for weighing (Python would interpret the sentence: `_bind_wordings` checks only names and slot counts, and `english.statement` runs with no Lean overlay check); a separate weighing matcher in Lean |
| D13 | No numeric weights, no "weigh" relation computed by the checker, no default inference inside the checker | research 4.4, 4.5; VISION converged rule item 5 | — |
| D14 | Cross-act collisions and precedents are **experiments first** (WG-E1, WG-E2), each with a pre-registered bar; a build follows only if the bar is met. If WG-E1 passes, exclusive acts come from `alternatives@0` (its chooser, `available` and exclusive choice) composed with soft norms, designed and reviewed in WG-10; weighing defines no exclusivity relation. **Outcome (phase 1):** WG-E1 failed (1 of 40 sampled CROSSACT units are two exclusive positive acts, or 3 of 40 with the second reader's calls on the contested units; none would change a checked answer). WG-10 is closed, and no exclusive-act construct is planned. Weighing still defines no exclusivity relation. Edit 7 is void (kept as history) and WG-10 is dropped from O9, 2.9 and edit 10's list (DRI WG1 (a)), so nothing in this plan depends on `alternatives@0` | when D14 was written the need was unmeasured; WG-E1 then measured it for cross-act collisions ([weighing-phase1.md](../research/weighing-phase1.md) 2.3, 2.4). Precedents stay unmeasured until WG-E2. `alternatives@0` owns exclusive choice (SYNTHESIS O9) | building exclusive-act semantics now; extending soft's colliding pairs with declared exclusive acts |

## 2. Design

### 2.1 What a `weighing@0` document is

A `weighing@0` document is a soft document (soft 1) whose environment carries a `weighing` block. Everything soft
requires still holds (soft 4.1), and the layered branch's well-formedness (`WellFormedU (soften D, unspec)`) holds; the
weighing checks come on top (2.5).

### 2.2 The English (one reading each; rejected as today when `weighing@0` is off)

"The English layer" below is en-wg, in Lean (D12). It reads each sentence, resolves E7 and computes every refusal
with its text. Python relays the result and displays it.

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
<grantor>"). Wordings not in this table are not `weighing@0` wordings. "normally", "typically", "usually" and "in most
cases" stay with their owners: soft 2.2's reading sets (a default rule or a frequency claim), and the plain normality
frame, which is DF-4's (D12). "all things considered" has no wording: it is the decider's judgment (D1). A switch condition without "only" has no wording (D6).

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
   string array, sorted and unique. AR-10's row: the profiles contain `weighing@0`, `norm-defaults@0`, `norms@0` and
   `soft-norms@0` (`UnsupportedProfile: weighing@0 requires <the first missing one>`, in `requires` order, from
   `needText`) and not `rights@0` (`UnsupportedProfile: weighing@0 with rights@0`, from `refusing`). A `weighing`
   block is allowed only with `weighing@0`.
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
here"). Defeasible owns `DefaultCompletion` and its comparison, and weighing keeps this record (DRI DF2). Once
`defaultZone_eq_noException` is proved, the record's sentence is rendered from defeasible's; until then each
wording has one catalogue row.

The zone words (settled / left to / not said / inconsistent / unknown) are a vocabulary over the three-valued
machine beside QA's leads, the speech-acts answers and defeasible's `basis`. They are listed as **NEW** under
plans-index D8, pending synthesis round 2. Situation wording reuses `VE.Words`.

English (display only; Lean selects the rows): "Settled: whatever the assistant decides here, the text requires the
assistant to <act>." / "Left to the assistant: this depends on whether rule 12's exception applies here, and on
whether helpfulness outweighs ethics on complying with this instruction here." / "Not said: the text does not say
whether …" / "Inconsistent at this situation: no way of deciding the open questions here satisfies the document; it
says …" / "Unknown: more than 16 open questions bear on this point." / "Unknown: the checker could neither rule out
nor confirm one way of deciding the open questions here: …" / "Ruled out: this record finds that guidelines
outweigh safety here; the document says safety always outranks ethics, and ethics outranks guidelines."

### 2.7 What stays open (the residual, never certified)

The findings themselves (`excepted`, `outweighs`, `off`); whether a decider considered the listed factors; whether a
finding is wise; "the spirit of the document" (:44); which category a consideration falls under. Where the source
places that doubt on a rule it names, it stays a translator's reading set over that rule's rank. Where it states the
doubt in general (:44, "it may be unclear which category a given consideration falls under"), it names no rule, and
it is GAP-W4 (2.8 W-R4), never a set on a rule it does not name; a verdict the text states that a cost is worth a
benefit (GAP-W5a), and a statement that two considerations weigh equally (GAP-W5b);
collisions between different acts (not planned: WG-E1 found 1 of 40 sampled CROSSACT units to be two exclusive
positive acts, 95% upper bound 0.13; the scope is the CROSSACT screen of the constitution's `norms` units, and such
pairs exist outside the sample, weighing-phase1.md 2.3); "best" responses among alternatives (research 4.7, research
only: 2 of the 40 sampled units ask for one).

### 2.8 Writing rules (wg-rev: the 2026-11-02 pilot, WG-R1 to WG-R5)

These rules bind anyone who writes source sentences in this plan's constructs: WG-0, WG-5, WG-8, WG-E2 and every
fidelity pilot. They change no construct, statement, wire field or diagnostic. Where a rule cannot be met, the
translator records the GAP it names; nothing is admitted that the rule does not state. Each GAP-W is a line of the
unit's report, never a status, and the part it covers stays UNFORMALISED.

| GAP | What it covers | Owner |
|---|---|---|
| GAP-W1 | the strength of a rank edge, where the source leaves `always` against plain `outranks` as a reading choice | weighing |
| GAP-W2 | a consideration with no collision the source states, and no rule whose exception the source ties it to | weighing |
| GAP-W3 | the part of a consideration that fits no verbatim string: an item with no head within 200 bytes, or the rest of a longer item that no family's stub takes | weighing |
| GAP-W4 | a general uncertainty about rank that names no rule | weighing |
| GAP-W5a | a verdict the text itself states that a cost is worth a benefit, outside a rank decision on one act | weighing |
| GAP-W5b | a statement that two considerations weigh equally (the equative words themselves are quantities', quantities-PLAN "comparatives, equatives") | weighing |

No batch of this plan closes a GAP-W. A GAP-W is closed only by a later revision of this plan with its own pilot
evidence, and any form another plan would have to add goes through a request row in 6.1.

**W-R1, the strength of a rank edge as a reading choice (WG-R1).** A source sentence that can be read either as
`always outranks` or as plain `outranks` (C-2) is not written as a reading set. The choice is refused under
profile-composition rule 8 ("A reading candidate holds one content"; a candidate that needs more stays pending, with
`content: null` and `unknown` rows), for three reasons:
- neither strength is a content: `always` is an entry of the identity-bound `weighing` block, and the plain edge is
  soft's `outranks` entry, both in the environment (2.3);
- `Str_T` is a pack premise in X, which no choice gates (profile-composition G1 and G4);
- so a set {always, plain} has no candidate that holds its reading, and putting `always` in the block decides the
  choice for every candidate.

What the translator writes:
- the edge as the rest of the document declares it (C-1 for the value order);
- no `always` entry for that edge;
- no reading set on its strength;
- the strength words as UNFORMALISED, with GAP-W1.

The unit is never CHECKED on the strength. `always` (E1) stays the construct for a sentence whose one reading is the
strict step. This plan requests no new PC form for the choice: one would be a request row in 6.1 plus a DRI ruling.

**W-R2, E5 only on a collision the source states (WG-R2).** E5 names an `outweighs` decision, and that decision
exists only for two ranked default rules colliding on one act (soft 1.3; 2.4's `outweighsTriples`). An E5 line is
written only where the source's own sentences state that collision: both rules and the ranks they serve. A
translator never adds a rule, rank or frame to give E5 a target. Such a frame invents a collision. It can also
reverse the source's standard: a frame where ethics outranks helpfulness on every requested action refuses by
default unless helpfulness is found to outweigh, while :325 avoids an action only where its risks "clearly" outweigh
its benefits.

A consideration with no stated collision goes to soft's `factors`, through soft's sentence `The exception to rule n
takes account of <consideration>.` (main), on the rule the source ties it to. This requires all of the following:
- that rule is in the document;
- the source's words make the consideration bear on whether that rule is excepted (soft's reading: "These
  considerations bear on whether rule n is excepted; none is by itself decisive");
- the factor keeps that rule's scope: it is declared on that rule only, never on a wider act or on every requested
  action (u0183's factors belong to the power-concentration assessment of :463-479).

Otherwise the consideration is GAP-W2. `targetCheck` and `NoSuchDecision` stay as they are (weighing.md 1.6): an E5
line with no decision is still refused there. Nothing here needs an E5 without a target.

**W-R3, a consideration is copied, never reworded (WG-R3).** Each consideration is one string of the source's words,
byte for byte (plan-synthesis-2 DECISIONS item 5). The rules for writing it:
- **One string per item.** Each item of a source list is its own string, never merged with another or split across
  two.
- **Markup is not part of the string.** Markup the source's format adds (a list bullet, emphasis marks) stays
  LABELLED, as main labels it.
- **Always the quoted form.** In E5 and in soft's factor sentence, every consideration is written quoted, one JSON
  string each, which keeps an embedded comma or "and". This is the canonical form main's `ve/norm_english.py` prints
  for soft's factors. The unquoted list is never written: main's reader splits it on ", " and on " and ", so an item
  holding either would silently become two strings.
- **An item over 200 bytes is written as its head.** Past 200 bytes, 1.6's limit gives `InvalidInput: invalid
  factors <i>`, and soft's limit gives `SOFT_INVALID_FACTORS`. The head is the item's emphasised lead, copied byte for
  byte, when the source emphasises one. Otherwise the head is the longest leading span of the item's words, copied
  byte for byte, that ends where the source writes a comma, colon, dash or bracket. Either way the head is at most
  200 bytes. The rest is written as stubs of the families that own its parts (u0135.s08: the head is its emphasised
  lead, "The vulnerability of those involved", and the rest is definitions' "e.g.", quantities' comparison and
  purpose-explanation's reason). A part no family owns is GAP-W3.
- **An item with no such head is GAP-W3 whole.**
- **Never reworded.** A string never has commas removed, words added, or words dropped from its middle.

**W-R4, rank claims need a rank the source states (WG-R4).**
- A general uncertainty about rank that names no rule (u0021.s01, :44) is GAP-W4. No reading set is written on a rule
  the sentence does not name (2.7).
- A rank clause inside an analogy's frame is part of the analogy and is no rank edge. For example, u0056.s02 :122:
  "akin to … where the staffing agency has its own norms of conduct that take precedence over those of the business
  owner". It stays LABELLED with the analogy (main's `analogy` kind, inert). No rank, `outranks` edge or `always`
  entry is declared from it.

**W-R5, a cost-benefit verdict and an equal weight (WG-R5).** E3 to E5 constrain an open decision that a decider
makes on one act (D1). None of them states a finding the text makes itself.
- A verdict the text itself states, that a named cost is worth a named benefit (u0221.s05: "this is worth the
  benefit of"), is GAP-W5a. No ranks are declared to fit E3 or E4, which would invent an order and an override.
- A statement that two considerations weigh equally (u0031.s03: "just as real to us as") is GAP-W5b where it is a
  weighing. Its equative words are quantities'.

The request rows in 6.1 ask quantities and judgment-terms to stop sending these to weighing as built constructs.

## 3. Lean statements

Names have prefix `VE.Weighing.`; soft names are `VE.SoftNorms.*`, norm-defaults names `VE.NormDefaults.*`; RD-9,
PK-1 (`NormDefaults/Packs.lean`), AR-10 (`Compose/Dispatch.lean`), QS-1 (`Closure/Order.lean`) and AP
(`Acts/Elaborate.lean`) names as on main. New files (D13 of RD-9's
placement rule: a general definition goes in the file that owns its special case; new `Weighing/*` files hold only
what is specific to this profile). The statements of 3.1 to 3.3 are elaborated in [weighing.md](weighing.md) sections
1, 5 and 6, with the stub's findings in its section 0.

| File | Contents | Batch |
|---|---|---|
| `lean/VE/Weighing/Tree.lean` | `CondKind`, `Target`, `CondDecl`, `FactorDecl`, `GrantDecl`, `WeighEnv`, `WeighDoc`, `rankOrder`, `strictPair`, `strictWitness`, `targetF`, `targetSorts` | WG-2 |
| `lean/VE/Weighing/Conditions.lean` | `strengthPremises`, `condPremise` (on the condition decoded through the chain's guard decoder, with attitudes' AT-3a guard node), `grantConds`, `weighLabelled`, `weighPremises`, `propImplies`, `checkWeigh`, `WellFormedWeigh`, the theorems of 3.2 | WG-2 |
| `lean/VE/Weighing/Examples.lean` | `#guard` fixtures W-α to W-λ | WG-2 |
| `lean/VE/Weighing/Wire.lean` | block decoder, `weighGate`, `stripWeighing`, `stripCase`, the `weighing` pack provider (PK-1), identity | WG-3 |
| `lean/VE/NormDefaults/Evidence.lean` (norm-defaults' NEW item nd-atoms, not WG-6's; WG-6 consumes it) | `atomVO`, `coneAtomO`, `coneEvalO`, `coneValuesO`, `enumerateSettledO` (with its `atoms` parameter, DF1), `table3O` with today's functions as the `opens = unsaidNames U` instances (and `atoms` today's cone) | nd-atoms (norm-defaults); consumed by WG-6 |
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
  condition : VE.Formula            -- context (targetSorts target).reverse, base predicates of E only; decoded
                                    -- through the chain's guard decoder, with attitudes' AT-3a guard node
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

/-- The one generator: `Dec_T` for one condition, as soft's `excPremisesOf`; `Grant_T` is its necessary `.off` case.
    `c.condition` is the decoded formula: each `CondDecl.condition` is decoded through the chain's guard decoder,
    with attitudes' AT-3a guard node, so a condition may hold an attitude atom (synthesis round 2). -/
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

/-- PK-1's `weighing` pack: a constraint pack that declares no symbol and no constant. -/
def weighPack (Wd : WeighDoc) : VE.NormDefaults.Packs.Pack :=
  ⟨"weighing", .constraint, [], [], weighLabelled Wd, weighOrigins Wd, weighConditions Wd⟩

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
    when present; no `Json.setObjVal!` on a non-object (weighing.md 1.8). It reuses `VE.Risk.Wire.dropField` and the
    profile filter generalised from `VE.Compose.withoutDocumentLayers` (NEW, "Shared pieces"). Weighing is not a
    document layer: an environment decoder reads its `weighing` block. -/
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
    stripped case. `LayeredU.core := (route, D, U, packs, sitVocab, baseEnv)`, with `D` carrying
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

In `NormDefaults/Evidence.lean` (the owner; built by norm-defaults' item nd-atoms, which WG-6 consumes), beside
today's definitions, each with today's function as an instance:

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
    `coneValuesO` prunes the assignments that Kleene evaluation refutes against `X ++ Fill_T`.
    `atoms`: the ground atoms enumerated, a parameter (DRI DF1). Today's answers and the zone pass the query's cone
    (`coneAtoms U M n vs`, and `coneAtomsO … opens …` for the zone); defeasible's DF-5 passes `openAtomsAll L M record`.
    Over `budget` atoms not fixed by `fixed`, `none`. -/
def enumerateSettledO (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (atoms : List (String × List α)) (budget : Nat) (fixed : List ((String × List α) × Bool)) (n : String)
    (vs : List α) : Option Bool
theorem enumerateSettled_eq_open (U : UDoc) (M : VE.FiniteModel α) (n : String) (vs : List α) :
    enumerateSettled U M n vs = enumerateSettledO U [] M (unsaidNames U) (coneAtoms U M n vs) 12 [] n vs
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
    (opens : List String) (record : List ((String × List α) × Bool)) (r : Regulated) (vs : List α)
    (proposed : List (List ((String × List α) × Bool))) : ZoneAnswer α
  -- `opens`: the explicit open predicate names (JT-R1); weighing's answers are the instance `opens = openNames L`,
  -- and JT-4 passes its own. The ground atoms enumerated are `enumerateSettledO`'s `atoms` (DRI DF1): here the
  -- cone, `coneAtomsO` at `opens`; DF-5 passes `openAtomsAll`. WG-6's statement review fixes the exact types.
  -- `X`: PK-1's assembled X with its labels. `proposed`: completions found by the untrusted search; Lean checks each
  -- (modelCheckX), never trusts it. `ruledOut` and `inconsistent` are produced only when Lean itself enumerates every
  -- assignment of the cone's open atoms compatible with the record (other open atoms stay unknown) and refutes every
  -- one by Kleene evaluation of a labelled premise of `X ++ fillLabelled L.U`; the labels are Lean's: per assignment
  -- the first premise it refutes, deduplicated and sorted (with no atom to assign, the one label of a premise
  -- refuted outright). Never a label from `proposed` or the search.

theorem zone_settled_sound (L : VE.NormDefaults.LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt L.U.D 0)) (hb : backgroundValid L.U.D M = true)
    (record) (r : Regulated) (hr : r ∈ L.U.D.T.regulated) (vs : List α)
    (typed : VE.TupleTyped M.asStructure r.sorts vs) (opens : List String) (proposed) (b : Bool) (w)
    (hz : zoneOf L X M opens record r vs proposed = .settled b w) :
    SettledZ L.U (X.map (·.2)) M opens record r vs b

/-- The last conjunct is DF1/JT-R1's: every differing atom is in `opens` and not unsaid. -/
theorem zone_leftTo_sound (L X M valid hb record r hr vs typed opens proposed differ w₁ w₂ ns)
    (hz : zoneOf L X M opens record r vs proposed = .notSettled (some (differ, w₁, w₂)) ns) :
    LeftToZ L.U (X.map (·.2)) M opens record r vs (unsaidNames L.U) ∧
    ∀ a ∈ differ, a.1 ∈ opens ∧ a.1 ∉ unsaidNames L.U

theorem zone_notSaid_sound (L X M valid hb record r hr vs typed opens proposed lt w₁ w₂)
    (hz : zoneOf L X M opens record r vs proposed = .notSettled lt (some (w₁, w₂))) :
    VE.NormDefaults.UndecidedAtX L.U (X.map (·.2))
      { M.asStructure with relation := completionOf M record w₁ } r vs

/-- A record ruled out, or a situation inconsistent: no admissible completion, at least one label, and every label
    cited is a premise of `X ++ Fill_T` (Lean refuted each branch of a complete enumeration with one). -/
theorem zone_ruledOut_sound (L X M valid hb record r hr vs typed opens proposed labels)
    (hz : zoneOf L X M opens record r vs proposed = .ruledOut labels ∨
          zoneOf L X M opens record r vs proposed = .inconsistent labels) :
    (¬ ∃ R, AdmissibleCompletion L.U (X.map (·.2)) M opens record R) ∧ labels ≠ [] ∧
      ∀ l ∈ labels, l ∈ labelsOf (X ++ VE.NormDefaults.Admission.fillLabelled L.U)

/-- Today's norm-defaults status is the instance with no decision open, no record and budget 12. -/
theorem zone_extends_status (U : UDoc) (M : VE.FiniteModel α) (n : String) (vs : List α) :
    VE.NormDefaults.enumerateSettledO U [] M (unsaidNames U) (VE.NormDefaults.coneAtoms U M n vs) 12 [] n vs =
      VE.NormDefaults.enumerateSettled U M n vs
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
- **W-η (conservativity).** Every soft fixture α to υ under `weighing@0` and `norm-defaults@0` with no block passes the
  gate, and the layered route's answers equal those of the same case without `weighing@0`, compared without the rebound identity
  fields (`environment_id`, `document_hash`), which W-η compares separately (`runWeigh_delegates`; `base_environment`
  is the stripped environment's); certificate answers are compared through rebound packages. Refusals by the gate,
  each with its exact text recorded and `stripCase` returning on each: profiles `[norm-defaults@0, norms@0,
  relational-fol@0, weighing@0]` without a block (`UnsupportedProfile: weighing@0 requires soft-norms@0`); profiles
  `[norms@0, relational-fol@0, soft-norms@0, weighing@0]` (`UnsupportedProfile: weighing@0 requires
  norm-defaults@0`); `j = {}` (no panic); a malformed envelope; a duplicated profile; unsorted profiles; `rights@0`
  with `weighing@0` (`UnsupportedProfile: weighing@0 with rights@0`); a `weighing` block with `weighing@0` off. A combined fault (a bad soft document and a bad block) answers with soft's text. Every
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
- **W-ν (source and object agree; en-wg, weighing.md 7.6).** The checks compare the object en-wg returns with the
  original sentence; accepting a well-formed wire object is not enough. Seeded bugs that must each fail a fixture:
  en-wg drops `always` (E1 read as E2), and en-wg swaps necessary and sufficient (E3 read as E4, and the reverse).
  They sit beside E7's zero-, one- and several-candidate cases (7.6).
- **W-ξ (two readers, disjoint; WG-4).** Until E3, soft's Python `parse_declaration` and en-wg both read rank
  sentences. Each E1–E7 fixture is accepted by exactly one reader, and so is each sentence of its minimal pair (C-2:
  "Safety always outranks ethics." / "Safety outranks ethics."). The weighing reader refuses every soft-frame
  fixture. W-ν's seeded bugs and W-ξ's minimal pair and soft-frame refusals stay selected once built (DRI condition).
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

### 4.2 From the constitution (real units, run `20261028T0600Z`)

Re-anchored (refresh 2026-10-28) on the newest pilot, run `20261028T0600Z`: 1,133 units of the pinned constitution
(`units.json`), the unit set the census of 2026-10-28 labels. Draft 1 cited unit ids, spans and texts from research
2.5, which is unfilled. WG-0 and WG-5 record them from this run's ledger, keep the run's instance-bound repairs as
they stand (for example C-7's knowing-or-likely repair), and measure their own gains against it. Each fixture records the VE sentences, the expected status, and the zone answer where one applies; WG-5 and
WG-8 check them through `ve document` on the pilot branch.

| Fixture | Source | VE sentences (shape) | Expected |
|---|---|---|---|
| C-1 | :34 value order | soft 2.4's three `outranks` sentences, the holistic flag, decider "the assistant"; unit READINGS {A strict dominance, B open weighing carve-out, C ranks with the holistic flag} | WG-0: rank sentences CHECKED; flag OPEN; unit READINGS |
| C-2 | :40 "even if Claude is confident in its reasoning" | the safety edge as C-1 declares it; no `always` entry and no reading set on its strength (:34 says the order is holistic, :40 says the safety step is robust, and that choice has no candidate form under profile-composition rule 8: 2.8 W-R1) | WG-5: the strength is GAP-W1, its words UNFORMALISED, the unit OPEN; never READINGS. `Safety always outranks ethics.` and `Safety outranks ethics.` stay W-ξ's minimal pair as sentences read one at a time (each accepted by exactly one reader), not as a set (wg-rev, WG-R1) |
| C-3 | :42 "Exceptions to this are any hard constraints … and any cases where Anthropic's guidelines overlap with broad safety" | the hard constraints are strict rules (already); guideline rules that overlap with safety carry rank safety (a narrowing per rule, attributed) | WG-5: OPEN (the overlap is an open classification) |
| C-4 | :138 "operators cannot grant users more than operator-level trust" | grants on the instructable-behaviour rules | WG-5: CHECKED where the rules are declared: `DelegationExceedsGrantor` and the inherited conditions (`grant_within_grantor`) are the checked content |
| C-5 | :405-423 instructable behaviours | default rules `(operators may turn off)` / `(users may turn off)` with grants where the source says "absent increased or decreased trust granted by operators" | WG-5: OPEN (each default's exception) |
| C-6 | :443 "cannot be unlocked by any operator or user" | soft's `hard: true` narrowing, cited once on the hard-constraint header | WG-0: CHECKED (`HardConstraintAltered` is the check) |
| C-7 | :457 "For cases that are more unclear or uncertain, we want Claude to be guided by the more holistic … prioritization" | each hard constraint's prohibition in the knowing-or-likely case (today's repair) beside a default "should not" for the unclear case, decided by the assistant | WG-8: zone `settled no` (knowing case), `left to the assistant` (unclear case) where today's probe says UNDECIDED |
| C-8 | u0135.s03's shape: a list item (:332-343) under a lead-in that says what the items bear on ("relevant to how much weight to give to potential harms"), with no collision the source states | no E5 line and no added rule or frame (2.8 W-R2). Each item is one verbatim string in the quoted form (W-R3), as soft's `factors` on the rule the source ties it to, only where that rule is in the document and the item bears on whether it is excepted | WG-5: no `weighing` block entry from the unit; otherwise GAP-W2. Control: the same item as an E5 line with no stated collision is `NoSuchDecision: outweighs <act>, <lower>, <higher>` (θ14), and the writing rule forbids the frame that would hide it (wg-rev, WG-R2) |
| C-9 | u0183's shape: considerations stated for one assessment ("In the weighing the harms at stake", in the power-concentration passage :463-479), with a duty to consider them | the considerations as C-8, declared only on the rule of that assessment, never on every requested action. The duty "should also consider" is main's `should`, not weighing's. Every item is in the quoted form, never reworded (W-R3) | WG-5: no factor on a target wider than the source's assessment; with no such rule in the document, GAP-W2 (wg-rev, WG-R2) |

## 5. Batches

Every batch is 2 to 6 hours for one builder and passes the lean-first gate (LEAN-FIRST-PLAN 5.1) as RD-9's batches do:
the full gate once on the final commit, selected tests while iterating, seeded bugs in each changed language
recorded with the failing test, `DELTA.md` with the corpus A/B by class, the deletion ledger, the frozen-inventory and
assurance-manifest updates (DRI D2), trust classes with any budget rise signed (DRI D3), `tools/lean_statements.py`
showing additions only, and `lean/audit.py`. New Python respects the layer map (DRI D5); new diagnostics take AR-13's
codes when they land (DRI D6); every identity is Lean's (DRI D7). Each standing ruling this plan cites applies to a
batch where its condition holds. A decision no standing ruling covers stays this plan's, and no batch reserves a DRI
signature that a standing ruling covers. Generated files are never edited by hand: `lean/checkers.lock` and the rest
go through `tools/regen_generated.py --write`. No test-collection file is committed: the gate ties test IDs to the
commit, and `tools/gate_collection.py --check` compares with the merge base.

| # | Batch | Hours | Owner | Needs | Pilot effect |
|---|---|---:|---|---|---|
| WG-0 | The value order and the hard constraints' immunity with today's `soft-norms@0` | 3–4 | pilot | the RD-9-owned document-routing repair (NEW) on `main`; composition's NEW item `sa-parts`, the part-document design (a checked cross-part interface; the whole constitution exceeds L70); SC-9's soft form adopted or on the same pilot branch (SC-9's migration and source audit still pending). **DEFERRED** (5.0) | measured by WG-0 against run `20261028T0600Z` (draft 1's estimate cited research 5.2, unfilled; withdrawn) |
| WG-1 | Statement review of section 3, re-elaborated against main, with en-wg's statements written in weighing.md 2 (frames, target objects, refusals) | 3–4 | planner | — | none |
| WG-2 | Lean: block, strength, conditions, grants, premises and their theorems | 5–6 | Lean | WG-1; QS-1 and AP's split map (both on `main`; the split checks are reachable only after the act-phrases prerequisite of D6) | none |
| WG-3 | Lean: block decoder, `stripWeighing`, the `weighing` pack, AR-10's row, the kind rows, pack-leaf recognition, identity | 5–6 | Lean | WG-2; AT-2/AT-3a; profile-composition's PC-9 (typed priority checks and the "no exception" statements) and EXP-G1, both before WG-3; PC-3 (the slot `pack`); RD-9 SC-1 and SC-6, PK-1 and AR-10's table are on `main` | none |
| en-wg | english-lean (NEW): the weighing-frame integration that reads E1–E7 in Lean and returns the weighing object (D12) | not estimated | english-lean | en-sw; WG-2 (the objects); runs alongside WG-3 | none |
| WG-4 | Python: bind the relayed Lean reading, passive display records, document dispatch, fuzz tests | 4–5 | Python | WG-3; en-wg; the document-mode queue | none |
| WG-5 | The constitution: strengths, conditions, switches and grants | 4–5 | pilot | WG-4, WG-0; the routing repair; the amended hard-constraint queue (AP-3 Group A after AT-6a/AT-6b); the act-phrases prerequisite for `acts@0` with soft norms (D6) | not estimated (draft 1's estimate withdrawn) |
| WG-6 | Lean: zone answers and records (consuming norm-defaults' nd-atoms: open atoms over an explicit atom list) | 5–6 | Lean | WG-3; nd-atoms (norm-defaults); RD-9 SC-A on `main`; PK-1 | none |
| WG-7 | Layered-route kinds and display: `weighing-zone`, `weighing-record`, English, CLI | 5–6 | Lean, Python | WG-6, WG-4; PK-1 | none |
| WG-8 | The constitution: zone probe on the hard constraints, the "should" sets and each grant | 3 | pilot | WG-7; the hard-constraint queue | no coverage claim; answers recorded |
| WG-E1 | Experiment: do collisions between different acts need a new construct? | 4 | planner | done: **FAIL** ([weighing-phase1.md](../research/weighing-phase1.md)). It did not need WG-0, because clause 1 decided it | decided WG-10: closed |
| WG-E2 | Experiment: can worked examples bind a decider as precedents? | 5–6 | planner | WG-2 | decides WG-9 |
| WG-9 | (only if E2 passes) Lean: precedents compiled into decision conditions | 5–6 | Lean | WG-E2, WG-3 | per E2's measurement |
| WG-10 | **CLOSED** by WG-E1's FAIL (kept as history; edit 7 void, DRI WG1 (a)). Was: (only if E1 passes) design and review of `alternatives@0` composed with soft norms | 3 | planner | WG-E1 (failed) | none. Measured: 0 B; no sampled (ii) unit changes a checked answer (7) |

**Order (refresh 2026-10-28).**
1. WG-1, re-elaborated, with en-wg's statements.
2. WG-2.
3. WG-3 after AT-2/AT-3a, PC-3, PC-9 and EXP-G1, with en-wg in parallel after en-sw and WG-2. WG-3 keeps its place in
   the constitution path after AT-3a.
4. WG-4.
5. WG-5 after WG-0 and the amended hard-constraint queue.
6. WG-6, then WG-7, then WG-8.

WG-0 waits for the routing repair and the part-document design. WG-E2 follows WG-2 and keeps its pre-registered bar.
WG-5 shows each grant's effect through `modelCheckX`, and WG-8 records each grant's zone answer, so no requirement
depends on a later batch. The landing order on `Layered.lean` (WG-3 after AT-2/AT-3a and before ET-4 and QT-B2)
is a merge preference only, not a dependency. WG-5's and WG-8's edits to u0165.s01–s07 run in the hard-constraint queue
(AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → AP-3 Group A → WG-5, DRI AP2). Landing preference: weighing lands after
quantities' track A and before events. About 38 to 47 builder-hours on the path (*estimate*, not evidence of speed;
en-wg is not estimated).

**M10's path** (WG-3, AT-2/AT-3a, then WG-5) names these prerequisites: the routing repair, en-sw, en-wg, AP-3
Group A, and the act-phrases prerequisite for `acts@0` with soft norms.

### 5.0 Status on 2026-10-28 (refresh)

Checked against `main` at `6d0a10526`. The phase-1 table below it is kept as history.

| Item | Status | What it needs now |
|---|---|---|
| RD-9 core (SC-1 `LayeredEntail.lean`, SC-6 `LayeredAdmission.lean`, `bindCertX`), PK-1 (`NormDefaults/Packs.lean`), AR-10 (`Compose/Dispatch.lean`'s `profileTable`), QS-1 (`Closure/Order.lean`), AP's `SplitMap` (`Acts/Elaborate.lean`) | on `main` | — |
| SC-8's document path (`ve/document.py` is now the package `ve/document/`) | **not working for the soft chain**: the 06:00Z pilot's `soft-chain-probe.json` loads and then fails `check` ("norm-defaults@0 documents are checked through fill"), because the document path still calls the soft admission route under `norm-defaults@0` | the RD-9-owned document-routing repair (NEW) |
| SC-9 (pilot migration, source audit) | pending | — |
| WG-0 | **DEFERRED** | the routing repair; `sa-parts` (the part-document design) |
| WG-1 | the stub is re-elaborated against `main` at `9ba2140e2` (weighing.md draft 6, 2026-11-02), with en-wg's statements in weighing.md 2.5 and its OPEN lines in section 10. The statement gate passed at `1ae4b7402` (`reviews/dri-decisions-20261102-wg-1.md` item 1), and OPEN-1 to OPEN-11 are RULED (items 2 to 4) | — |
| wg-rev (the 2026-11-02 pilot's WG-R1 to WG-R5) | this revision: 2.8's writing rules, C-2, C-8, C-9, the summary and the request rows. No statement of WG-2 or WG-3 changes, and none of en-wg's | its one review; then the re-pilot (fp-weighing). WG-2 is blocked by wg-rev (fp-weighing decision item 2) |
| `acts@0` with soft norms | refused (`actsRefuses` lists `soft-norms@0`) | an act-phrases-owned prerequisite (D6) |
| en-sw, en-wg | not on `main` (en-sw queued; en-wg filed, blocked by en-sw and WG-2's objects) | — |

### 5.0.1 Status after phase 1 (2026-10-13, history)

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

**DEFERRED** (5.0) until the RD-9-owned document-routing repair is on `main` and composition's `sa-parts` (the
part-document design, a checked cross-part interface) exists.
Phase 1 checked SC-8 on 2026-10-13, found it unmet, and did not attempt the translation. On 2026-10-28 RD-9 is merged,
but the 06:00Z pilot's soft chain fails `check`, so the repair is the trigger. The starting translation is run
`20261028T0600Z`'s; otherwise nothing below changes.

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
Z-β and C-4 against the edited statements. Done when the review has converged and this file carries its edits.

**Re-elaboration (refresh 2026-10-28).** WG-1's remaining obligation re-elaborates the stub against `main` (no longer
`rd-9/integrate`) and writes en-wg's statements in weighing.md 2: the frames E1–E7, the weighing object each returns
(embedded conditions included), and the refusals with their texts. It also states 2.4's one-reading argument as the
disjointness claim of W-ξ. It also fixes the signature of `VE.Acts.splitRefusal` (weighing.md 1.6), which is not on
`main`: AP's two inline texts in `Acts/Elaborate.lean` ("rule N …" and "definition N …; name one of its parts") need a
role argument; WG-2 factors them into it, byte-identical (`Acts/ElaborateExamples.lean`'s guard unchanged), and
computes weighing's texts with it (DRI, plan item 19). `weighing@0` requires `norm-defaults@0` (D2, D11), so the question whether the layered
gate accepts a stripped document without it is gone. The item-1 statement
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
identity). Shared:
- PK-1's provider line in `lean/VE/NormDefaults/Layered.lean`/`Packs.lean`. The layered decoder runs `weighGate` on
  the original environment, strips the block, decodes the stripped source, decodes the block, checks
  `WellFormedWeigh`, and adds `weighPack` to the list `decodeSoftU` hands `Packs.assemble U used ps`.
- AR-10's table in `lean/VE/Compose/Dispatch.lean`: one `ProfileRow`,
  `⟨"weighing@0", ["norm-defaults@0", "norms@0", "soft-norms@0"], refusing "weighing@0" ["rights@0"], "pack"⟩`, with
  its `interface` value `.pack "weighing"` (profile-composition PC-3 adds the slot `pack`; synthesis round 2, N1) and
  the row's composition proof. The layered kinds `weighing-zone` and `weighing-record` are unchanged. weighing.md's
  `weighingRow` (1.7, slot `"layer"`) is restated with slot `"pack"` at WG-1. Also the profile filter generalised from `withoutDocumentLayers` (owner: composition),
  which `withoutDocumentLayers` becomes an instance of.
- The condition decoder: the block decoder decodes each `CondDecl.condition` through the chain's guard decoder, with
  attitudes' AT-3a guard node, so a condition may hold an attitude atom; `condPremise` takes the decoded formula, and
  WG-3's statements say so (synthesis round 2).
- `lean/VE/Defaults/Route.lean`: the weighing kinds as `Packs.KindRow` rows.
- `lean/VE/NormDefaults/Run.lean`: `runOtherCase` forwards them.
- `lean/VE/NormDefaults/LayeredAdmission.lean`: pack-premise leaf recognition generalised from `SoftLeafX` to any pack
  id (owner: RD-9), so that admission and certificate replay consume the complete regenerated pack list and full
  identities.
- The relay-binding inventory: one row per relayed weighing answer in `docs/spec/rd-9-relay-binding.md` and
  `tests/test_relay_binding_inventory.py`'s `INVENTORY` (catalogue-owner D9).
- `lean/VE/Audit.lean`.

`stripWeighing` reuses `VE.Risk.Wire.dropField` (no second copy). No service mode: no `Protocol.lean` constructor, dispatch arm or `runMode_weighing`, no entry in
`ve/backends/service_schema.py`'s `MODES`, no `ve/backends/lean_service_schema/weighing.json`; the Python profile side
is generated by AR-10.

The layered route's existing kinds answer weighing documents with PK-1's X; certificates go through `bindCertX` with
the full environment. No kind is reimplemented.

**"No exception" (synthesis round 2, D3).** Weighing's record is defined as defeasible's `dfltUniform` instance only
if profile-composition's EXP-D3 proves `record_eq_dflt`. Until EXP-D3 and defeasible's DF-U, defaults with provider
conditions, weighing's included, stay refused with E1d; only the `--assume-no-exception` question is refused, and the
same document without that flag routes.

**Weighing × attitudes (synthesis round 2).** W × At rests on profile-composition's EXP-G1, whose fixture must be
non-vacuous: the attitude atom decides a weighing guard in at least one model (DECISIONS item 4). No examined
constitution sentence puts an attitude atom inside a weighing condition under scope.

Fixtures: W-η through the layered route (rows compared without the identity fields, certificates through rebound
packages; the gate's refusals with their exact texts; `stripCase` on each refused case; the combined fault), W-ι,
and W-α, W-δ, W-ζ's conflict and certificate answers. Required regressions: a weighing premise changes an
`admission` answer and a certificate answer (each fails if the weighing pack is left out of `decodeSoftU`'s list or out
of leaf recognition). Route-case fixtures recorded into `tests/data/route-cases.jsonl` by
`tests/route_case_recorder.py` and checked by `tests/test_route_row_schemas.py` (WG-4 adds the Python tests that
record them).

The gate refusal texts in weighing.md 4.1 were computed with the weighing row last in AR-10's table. WG-3 recomputes
them by `#eval` where it actually places the row and, if any differs (another fault reported first), updates
weighing.md 4.1 and W-η in the same change (DRI, plan item 19).

Deleted, not duplicated: no premise assembly and no service mode in `Weighing/*`; weighing is one PK-1 pack and two
layered-route kinds. `repo_map.py --check` passes (no new mode).

Done when: the fixtures pass, `runWeigh_delegates` and `stripCase_idem` are proved, the corpus A/B is identical (no
corpus document has the profile), and the gate passes.

### en-wg. The weighing-frame integration (english-lean, NEW; not this plan's batch)

Owned by english-lean (backlog row en-wg, blocked by en-sw; it also needs WG-2's objects). What this plan needs from
it (D12): en-wg reads the original E1–E7 sentence through the shared grammar machinery and returns the weighing object
WG-2 defines, embedded conditions included. Its closest abstraction is `lean/VE/EnglishGrammar/Actions.lean`, and a
weighing-statement value type is NEW. It adds no separate weighing matcher. Its word rows (*generally* among them, a
D6 word) go into en-sw's `SourceWords.lean`, and weighing owns only the rank-frame row. Its acceptance checks are
W-ν's source/object seeded bugs and E7's zero-, one- and several-candidate cases (weighing.md 7.6), computed in Lean.
WG-1's re-elaboration writes its statements in weighing.md 2.

### WG-4. Python: binding, display, documents (Python, 4–5 h)

Files (new):
- `ve/weighing.py`, the relay. It sends the layered route's weighing cases, and the two kinds `weighing-zone` and
  `weighing-record` once WG-7 adds them, with `rows` from `ve/backends/relay.py`. It binds the relayed Lean reading
  and rows, checking schema and binding only (R8).
- `ve/surface/weighing.py`: passive display records, profile-gated as soft's are. They hold no wording text and
  match nothing.
- `tests/test_weighing_lean.py`: documents through the service.
- `tests/test_weighing_answer.py`: fuzz tests. Each member of a genuine answer is dropped, emptied, retyped,
  duplicated, reordered, or has an index pushed out of range, one and two faults at a time; every mutant is
  `CheckerUnavailable` or shows nothing different.

Shared:
- `ve/document/`: a `weighing@0` document goes to the layered route, not to a `weighing` mode. This edit joins the
  document-mode queue after `lf-16g`, in landing order AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10.
- `tests/test_english_unambiguity.py`: the new wordings, and W-ξ's disjointness test.

English: the reading, the paraphrases, E7's resolution and every refusal text are Lean's (en-wg and the elaboration
row: `strictWitness`, labels, targets, inherited conditions). Python displays them. `tools/relay_lint.py` gains
`weigh__`-free checks: no premise label or decision name in rendered text. Through the service, WG-4 runs
weighing.md 7.6's fixtures, which en-wg computes in Lean: one match accepted; none refused (the predicate must be
declared first); several refused with the list and the offer; the offered form accepted and shown to inherit, with
the control that fails. It also runs W-ν and W-ξ. The Sonnet 5.5 comprehension check of 8's open question is saved
evidence under the batch's `docs/<batch>/`, not a suite test: suite tests make no model calls.

Deleted, not duplicated: Python builds no `Weigh_T`, no `strictPair`, no `X`, no wording and no frame reader. It
binds and renders Lean's rows.

Done when: the fixtures pass through `ve document load/check/render`, the fuzz tests pass, the unambiguity and
disjointness tests cover every new wording, and the gate passes.

### WG-5. The constitution: strengths, conditions, switches, grants (pilot, 4–5 h)

As WG-0 (pilot branch, one commit, blind review before counting). Its edits to u0165.s01–s07 run in the hard-constraint
queue (AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → AP-3 Group A → WG-5), starting from the translation as AP-3 Group A
left it. It also needs the routing repair, and the act-phrases prerequisite for `acts@0` with soft norms wherever a
translated rule is split (D6). Translate
C-2 to C-5, C-8 and C-9 (4.2) under 2.8's writing rules: the :38-44 safety robustness sentences with the safety
edge as C-1 declares it and their strength as GAP-W1, never the reading set {always, plain} (W-R1); :42's exceptions; the operator and user permission layering of :134-139 as switches and grants; the
instructable-behaviour lists of :405-423 as default rules with switches. Measure as WG-0. Required: each new grant's
effect shown through `modelCheckX` (the situation where the grantee's switch is on and the grant is off is refused,
citing `weigh:grant:<rule>:<party>`); the zone answer for each grant is WG-8's. Done as WG-0.

Notes (synthesis round 2, for WG-5 and WG-8):
- u0115.s01 to s02 (E2): the considerations of u0115.s02 are soft-norms' `factors`, neither sufficient nor
  necessary, text verbatim with "for business reasons"; weighing makes no `Grant_T` or `Dec_T` condition from them.
  The share/deceive comparison is stage-3 material (different acts; soft 4.5), so today there is no colliding pair
  and no `Weigh_T` premise; WG-E1 failed, so no new construct.
- u0165.s01 to s07 with u0173 (E1): the hard rules are `hard_never_weighed`, so weighing adds no `Weigh_T` premise
  to them; WG-5 checks that no colliding soft pair exists there.

### WG-6. Lean: zone answers and records (Lean, 5–6 h)

Files: `lean/VE/Weighing/{Zone,ZoneExamples}.lean` (new). WG-6 needs norm-defaults' NEW item nd-atoms, which makes
the atom-list change to `lean/VE/NormDefaults/Evidence.lean` (`enumerateSettledO` with its `atoms` parameter,
`coneAtomsO` at `opens`, `table3O`, today's functions as instances: the `*O` definitions and `*_eq_open` lemmas of
3.4); WG-6 consumes it and does not extend `Evidence.lean` (synthesis round 2, C10). WG-6's statement review states
`zoneOf` over explicit open names `opens` on nd-atoms' enumeration (today's cone at every current call; DF-5 passes
`openAtomsAll`), with today's answers the instance `opens = openNames L` and `zone_leftTo_sound`'s last conjunct
"every differing atom is in `opens` and not unsaid" (DRI DF1, JT-R1). DF-5 and JT-4 wait for nd-atoms, not for
WG-6. Defeasible owns `DefaultCompletion` and its comparison, and
weighing keeps its record (DRI DF2). Shared:
`lean/VE/Audit.lean`, frozen inventory and assurance manifest (decoder code unchanged).

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
budget, or the surviving branch). The notes on u0115.s01 to s02 (E2) and on u0165.s01 to s07 with u0173 (E1) under
WG-5 hold here too.

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
(:332-343), each item one verbatim string under 2.8 W-R3; write each example as a precedent (factors present, outcome), citing its span; hold out one third of the
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
which the DRI declared void (WG1 (a)).

If WG-E1 passes, WG-10 designs and reviews a composition of `alternatives@0` (its chooser, `available` and exclusive
choice) with soft norms, and weighing consumes it. Weighing defines no exclusivity relation and does not extend soft's
colliding pairs with declared exclusive acts. Nothing is built before that composition's statements pass review.
WG-E1's bar is unchanged.

## 6. In-flight work and merge conflicts

| In-flight item (branch) | What this plan uses | How conflicts are avoided |
|---|---|---|
| RD-9 (merged on `main`; plan `docs/spec/rd-9-soft-chain-PLAN.md`) | SC-1's `EntailsX`, `acceptanceX`, `conflictFreeCheckX_sound`, `modelCheckX_sound`; SC-6's `LayeredAdmission.lean` and `bindCertX`; the relay-binding inventory (`docs/spec/rd-9-relay-binding.md`); SC-A's edits to `NormDefaults/Evidence.lean`. Still to come: the **document-routing repair** (NEW, RD-9-owned: the soft chain under `norm-defaults@0` fails `check` through `ve document`); SC-9's pilot migration and source audit; pack-leaf recognition generalised from `SoftLeafX` (WG-3) | WG-0 and WG-5 after the routing repair, WG-0 on the pilot branch SC-9 uses; norm-defaults' nd-atoms (the only item editing a file RD-9 edits, `Evidence.lean`) after SC-A; WG-6 consumes it |
| design wave siblings and shared items (SYNTHESIS.md, DRI-DECISIONS-PHASE2.md) | PK-1 (WG-3, WG-6, WG-7); AR-10's table (WG-3); QS-1 (WG-2); AP's split map (WG-2's checks), all on `main`; the act-phrases prerequisite for `acts@0` with soft norms (D6; WG-2's split checks, WG-5); the hard-constraint queue with AP-3 Group A (WG-5, WG-8); defeasible's `DefaultCompletion` (DF2) and the `opens` list (DF1, JT-R1) (WG-6). Nothing depends on `alternatives@0` (DRI WG1 (a)). english-lean: en-sw's `SourceWords.lean` (word rows), en-wg (the frames, D12). Soft's reading sets for "normally", "typically", "usually" and "in most cases" stay with their owner. The wider E3 migration of soft's frames follows signed edit 10 ("once it owns norm wordings"; D12: never both) | shared files in WG-0 to WG-8: `lean/VE.lean`, `lean/VE/Audit.lean`, PK-1's provider line in `Layered.lean`/`Packs.lean` (integration order AT-2/AT-3a → WG-3 → ET-4 → QT-B2), AR-10's table row and the profile filter in `Compose/Dispatch.lean`, the kind rows in `Defaults/Route.lean`, `NormDefaults/Run.lean`'s forwarding, `NormDefaults/LayeredAdmission.lean`'s leaf recognition, the relay-binding inventory, `ve/document/` (the document-mode queue after `lf-16g`: AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10), `ve/__main__.py` (append-only edits; merge-train regenerates generated files with `regen_generated.py --resolve`) |
| lean-first and arch items (`infra/arch-AR-*`, lf-14 to lf-18) | AR-13's diagnostic codes (DRI D6) | new diagnostics are texts until AR-13 lands, then take its codes in the batch after |

Every shared file a batch touches is listed in its section. New code goes in new files (`lean/VE/Weighing/*`,
`ve/surface/weighing.py`, `ve/weighing.py`, `tests/test_weighing_*.py`). Generated inventories are regenerated by
their tools, never hand-merged.

## 6.1 Shared pieces

Each piece is **NEW** unless marked, with its closest existing definition and its owner. Weighing adds rows or
instances only.

| Piece | Closest existing definition | Owner | Weighing's use |
|---|---|---|---|
| The profile filter: an environment without a given list of profiles (NEW) | `VE.Compose.withoutDocumentLayers` (`Compose/Dispatch.lean`), which becomes its instance at `documentLayers` | composition | `stripWeighing` drops `weighing@0` (WG-3). Weighing is not a document layer, because an environment decoder reads its block |
| Pack-premise leaf recognition for any pack id (NEW) | `SoftLeafX` (`NormDefaults/LayeredAdmission.lean`), soft pack only | RD-9 | admission and certificate replay accept weighing premises (WG-3) |
| A JSON object without one field (existing; NEW only if extracted into a shared module) | `VE.Risk.Wire.dropField` (`Risk/Wire.lean`) | its current owner, or the module it is extracted to | `stripWeighing` drops the `weighing` block; weighing.md 1.8's copy is deleted |
| The enumeration over an explicit ground-atom list `atoms`, and `zoneOf` over explicit open names `opens` (NEW) | `enumerateSettled`, `coneAtoms`, `coneValues` (`NormDefaults/Evidence.lean`) | norm-defaults (O18), item nd-atoms; WG-6 consumes it | zone answers with `atoms` the cone and `opens = openNames L` (WG-6); DF-5 passes `openAtomsAll` (DF1); JT-4 its own `opens` (JT-R1) |
| The weighing-statement value type and the frame actions (NEW) | `lean/VE/EnglishGrammar/Actions.lean` (formulas, terms, declarations) | english-lean (en-wg) | E1–E7 read in Lean (D12) |
| Plans-index **D6**: source-word reading sets, among them *generally* | en-sw's `SourceWords.lean` (`SourceWordRow`) | english-lean (en-sw; catalogue owner C1) | the `generally outranks` row beside soft's rows; weighing owns only the rank-frame row, and the plain normality frame is DF-4's |
| Plans-index **D8**: the zone vocabulary (settled / left to / not said / inconsistent / unknown) (NEW, pending synthesis round 2) | QA's leads, the speech-acts answers, defeasible's `basis`, `VE.Words` | synthesis round 2 decides | zone answers (2.6); situation wording reuses `VE.Words` |
| The "no exception" completion | defeasible's `DefaultCompletion` | defeasible (DF2) | weighing keeps its record; its sentence comes from DF's once `defaultZone_eq_noException` is proved; the record is defeasible's `dfltUniform` instance only if EXP-D3 proves `record_eq_dflt`, and until EXP-D3 and DF-U the `--assume-no-exception` question with provider conditions is refused with E1d (WG-3) |
| Relay binding | the rd-9 relay-binding inventory | RD-9 (catalogue-owner D9) | one inventory row per relayed weighing answer (WG-3, WG-7) |
| **REQUEST (wg-rev; OPEN-5, RULED by `reviews/dri-decisions-20261102-wg-1.md` item 4):** a target on a split part once `acts@0` admits soft norms | profile-composition 1.10 and PC-6 (parts share the source's decision); weighing.md 1.6 `targetCheck`, `grantConds` | act-phrases (the prerequisite for `acts@0` with soft norms, D6) | while `acts@0` refuses `soft-norms@0` this is unreachable, and WG-2 builds W-λ as written. Request: when the prerequisite lifts that refusal, a target on a split part is refused until a ruling covers it, and the prerequisite's statements say so. No weighing statement changes |
| **REQUEST (wg-rev, WG-R5):** quantities' "Not in scope, by owner" line, which gives `"outweighs" (**weighing**)` | quantities-PLAN.md, "Not in scope" | quantities | weighing builds `outweighs` only as an open decision between two ranked rules colliding on one act (E3 to E5, 2.8 W-R5). A verdict the text itself states that a cost is worth or outweighs a benefit is GAP-W5a, and no plan builds it. Request: the line names that narrower scope, so no unit's verdict is sent to weighing as a built construct |
| **REQUEST (wg-rev, WG-R5):** judgment-terms' u0031.s03 row: "the comparison of risks stays quantities' and weighing's" | judgment-terms-PLAN.md, the C u0031.s03 row | judgment-terms | weighing builds no comparison of two considerations outside a rank decision on one act. An equal-weight statement is GAP-W5b, and its equative words are quantities'. Request: the row names quantities alone for the comparison, or names GAP-W5b for its weighing part |

## 7. The measure

Coverage is measured as soft-norms-PLAN 4 requires: a unit changes status only after end-to-end admission through
`ve document`, against a baseline of the same split at the same commit, and after a blind whole-span fidelity review;
claimed and audit-verified bytes are reported separately; no figure is predicted (draft 1's estimates cited research
5.2, which is unfilled, and are withdrawn). Zone answers are reported as counts of `settled`, `left to`, `not said`,
`inconsistent` (each with the labels Lean computed) and `unknown` answers (split by reason: budget or surviving
branch) on the probe set, never as coverage.

**Anchor (refresh 2026-10-28).** The baseline is run `20261028T0600Z`. WG-0 and WG-5 measure their gains against
it, keeping its instance-bound repairs. The constitution census of 2026-10-28 labels that run's 1,133 units. WG
appears in either role (primary or secondary) on **132 units, 25,225 B** (recounted from
`reviews/constitution-census-20261028.tsv`). That is the span of units weighing touches, not a forecast of bytes
weighing will check. The primary-family shares are soft: on the stratified sample WG agrees 4 of 8, kappa 0.63
overall. So no batch is sized or ranked on them. The phase-1 numbers below are history: they describe WG-E1's
sample of run `20261012T1800Z`.

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
  only one. That choice has no candidate form (profile-composition rule 8), so C-2 writes no reading set: the strength
  is GAP-W1 (2.8 W-R1; wg-rev). WG-0 and WG-5's blind review audits it.
- **Risk: the remaining prerequisites slip.** RD-9's core, PK-1, AR-10, QS-1 and AP's split map are on `main`
  (5.0). Still to come: the RD-9-owned routing repair (WG-0, WG-5), the part-document design (WG-0), en-sw and en-wg
  (WG-4), AP-3 Group A and the act-phrases prerequisite for `acts@0` with soft norms (WG-5), and AT-2/AT-3a (WG-3).
  All of them are on M10's path. WG-1 waits on none of them, WG-E1 is done, and WG-E2 waits only on WG-2.
- **Risk: two readers until E3.** Soft's plain *outranks* is read in Python and E1 in Lean, so one reading rests on
  how sentences are routed to a reader, not on one parser. W-ξ tests the disjointness. When E3 moves soft's frames
  into Lean (signed edit 10), the parser itself carries the check.
- **Dependency, not a batch: refusals as not doing the act.** The three sampled WG-E1 units that name refusing
  (u0147.s04, u0179.s02, u0137.s02; 527 B) are (i). Refusing or declining to assist, or giving an unhelpful response,
  is not doing the requested act. A weighing condition can target units like these only after AP's act identity
  (AP-1 to AP-3) identifies "decline to assist", "refuse to assist" and "unhelpful response" with not doing the
  requested act; then soft's same-act collision applies. This is consistent with D6 and synthesis edit 8 but does not
  test them. The other seven (i) units are of other kinds and are not evidence for this line.
- **Open question (WG-1).** Is D4's "some chain contains `always`" the reading readers take from "always outranks"?
  WG-4's unambiguity test and a Sonnet 5.5 comprehension check (as RD-9's SC-9 does) on three paraphrases are the
  evidence; the check is saved evidence under the batch's `docs/<batch>/`, not a suite test (suite tests make no
  model calls). If they disagree, the DRI's ruling (`dri-decisions-20261028-weighing-refresh-apply.md` item 1) applies
  and no further DRI decision is needed: the input frames and D4 stay as they are; WG-4 does not ship the disputed
  paraphrase; Lean's paraphrase of a strict pair through the closure spells out the chain (each edge named, the
  `always` edge marked); the check is re-run on it and saved. If it still disagrees, the closure pair is shown only as
  that explicit chain, with no "always outranks" summary sentence.
- **Open point (wg-rev, from the 2026-11-02 pilot): "err on the side of".** u0193.s02 and u0078.s01 say "err on the
  side of". No plan has a wording for it. Main's nearest strength, a default `should`, passed the weighing part (F)
  in both seats on both units. The phrase cost u0193.s02 its whole-unit grade (W) only, and u0078.s01 passed W. It is not built here, and this point records it
  for a later revision.

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
   finally decides; no symbol in what a reader sees. en-wg's statements (frames, objects, refusals); the
   disjointness of the two readers (W-ξ); source/object agreement (W-ν).
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
| 2026-11-02 | Draft 6, WG-1's sync | weighing.md draft 6: `weighPack`'s seventh field (D3, 3.3), 5.0's WG-1 row. No decision changed. |
| 2026-11-02 | Draft 6, wg-rev | wg-rev, DRI 2026-11-02 fp-weighing item 1: WG-R1 to WG-R5 of the 2026-11-02 fidelity pilot ("Changes in this revision"). New 2.8 (writing rules W-R1 to W-R5, GAP-W1 to GAP-W5b); 0 narrowed; 2.7; C-2's expected answer, new C-8 and C-9 (4.2); WG-5, WG-E2; three request rows in 6.1 (OPEN-5, quantities, judgment-terms); 8's "err on the side of" open point. weighing.md 10's OPEN lines are marked RULED. No Lean statement, wire field, diagnostic or W fixture changed. |
| 2026-10-28 | Draft 6 | The refresh against `main` `6d0a10526` (debate `refresh-weighing-20261028`, DRI ruling `dri-decisions-20261028-weighing-refresh.md` item 1): the 16 edits of "Changes in this draft (refresh 2026-10-28)". Lean statements changed: `weighPack` (`consts`), `LayeredU.core` (`packs`), AR-10's row (`norm-defaults@0`, `refusing`, `layer`), `zoneOf` and the zone theorems (`opens`), `enumerateSettledO` and its legacy equations (`atoms`, DF1). New: en-wg (english-lean), W-ν, W-ξ, 5.0's current status, 6.1 "Shared pieces". |

## Cross-plan issues for the DRI

**None open (refresh 2026-10-28).** Item 1 below was decided by DRI WG1 (a) and (b) (`DRI-DECISIONS-PHASE2.md`),
and this draft applies it: WG-10 is dropped from O9, 2.9 and edit 10's list; edit 7 is void and kept as history;
nothing here depends on `alternatives@0`. The other cross-plan points this draft uses are decided too: DF1, DF2,
JT-R1, AP2, catalogue-owner C1 and D9, hedges-generics 2(a). The wider E3 migration of soft's frames is governed by
signed edit 10, so no DRI signature is reserved for it. The text below is draft 5's, kept as history.

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

   **For the DRI to decide (draft 5; decided since: DRI WG1 (a) and (b) adopted both):**
   - (a) whether to drop WG-10 from O9's "plans" column, from 2.9's "What the plans do" cell and from edit 10's list,
     and to mark edit 7 as void;
   - (b) whether any weight given to `alternatives@0` for weighing's sake (in its plan's priority or in NORTH-STAR's
     "priority across different obligations" row) should be lowered. WG-E1 measured 1 of 40 sampled CROSSACT units
     (131 B), with a 95% upper bound of 0.13, and 0 B of checked answers. Soft 4.5's stage 3 and that NORTH-STAR row
     may cite this result.

   Draft 5: until the DRI decides, nothing in this plan depends on `alternatives@0`. (Decided; still true.)

Not conflicts, for the record: WG-0's deferral leaves SYNTHESIS 4.1's "WG-0 runs once RD-9 SC-8 is on `main`"
unchanged. WG-E1 ran in phase 1 under its own gates, as 4.1 lists it. The hard-constraint queue (4.4), PK-1's
integration order, AR-10's row, QS-1 and AP's split map are untouched by phase 1.
