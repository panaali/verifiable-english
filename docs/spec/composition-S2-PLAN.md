# Composition stage S2 (pointer plan)

> Status: planning draft 3 (2026-10-02), pointer only: no code, Lean or frozen contract changes. Draft 2 applied the
> converged Astra + Fable design debate recorded in `manage-agents/debates/design-compose-s2/{astra,fable}.md` and
> nothing else. Both files end `STATUS: CONVERGED` after round 3; the Astra seat was held in all three rounds by Sol
> xhigh as the recorded cross-family stand-in. The debate's question (`TOPIC.md`) is the parent plan,
> [composition-PLAN.md](composition-PLAN.md), and its joint position is Fable's round 3 list, accepted by the Astra
> seat's round 3: REVISE draft 1 of the parent plan into draft 2, then BUILD through statement review with no second
> design debate. The record is, line for line as read, the one the parent plan's draft 2 and the S1 pointer plan
> applied (`debates/design-compose`, `debates/design-compose-s1`). Every converged edit is already in the parent
> plan's draft 2, whose section 10 maps each edit to its change. This file therefore restates no edit: the table
> below lists which converged edits bind stage S2 and where each one sits. The statement specification of S2's
> item 1, milestone S2a, is [composition-s2.md](composition-s2.md), now at draft 2: draft 3 of this file records the
> converged Astra + Fable statement review of the spec's draft 1
> (`manage-agents/debates/compose-s2-spec/{astra,fable}.md`, CONVERGED after round 2 on FIX with five corrections, all
> applied in the spec's draft 2 and listed in its change log; the Astra seat's round 1 is recorded as held by Sol
> xhigh) and synchronizes the references below to it. The parenthesis "(the next stage after S0 …)" in
> the pointer paragraph below is carried over from the S1 pointer and is not edited: item 1 is S2a, the stage after
> S1 in the parent plan's order (S0, S1, S2a, S2b).

Item 1 of THIS plan is the next stage after S1 (S2a, soft norms first) of docs/spec/composition-PLAN.md (the next stage after S0 in that plan's stage order, which is merged on main with docs/spec/composition.md). Apply that plan's S2a section, its fixtures and open questions; S0 and S1 statements are frozen inputs. Measure the unlock on the constitution and UDHR pilot units the plan names for S2a.

## The converged edits and where each binds S2

Numbering is the parent plan's section 10: edits 1 to 7 are Fable's round 1 list, Q4 and Q7 the two reporting
wordings, A1 to A4 the Astra seat's four corrections. "Parent" is composition-PLAN.md draft 2; "spec" is
composition-s2.md.

| # | Converged edit | Binds S2? | Parent | Spec |
|---|---|---|---|---|
| 1 | Owner-based quiescence for every generated predicate some choice's document lacks, `g → ⋁ χ(owners)`, `aimed_m` included when its permission has only candidate owners; the fixed bar's implementation kept intact; fixture F21 | yes. S2a: the exception and switch predicates of a candidate's rule (one owner) and the `outweighs` predicates of colliding default pairs (one owner, or a pair of candidates of different sets). S2b: the `lim`, `cond` and `aimed` predicates, the bar case and F21 | 2.3 (quiescence, the per-choice paragraph); 2.6; S2; F21; section 7 questions 1 and 9 | 1.6, 4.3, 8.3, fixtures M1, M10; section 12 for S2b |
| 2 | Rule 2 states the quiescence exception: the premises of `Choice_D` name predicates the chain generates on `sup D`, computed by the chain's own naming functions after they have run | yes | 2.1 rule 2 | 1.6, 4.1 |
| 6 | S2a (soft) first; S2b (rights) on the enumerated fallback until the rights `superpose_faithful`, bar case included, is proved; the UDHR row of section 6 qualified | yes: the scope of this stage. Superposition on the soft and norms chains; the enumerated fallback on every chain; the UDHR stays UNKNOWN (over the 64-choice budget) | section 0; 2.6; S2 (two milestones, split acceptance); section 6; question 1 | 0, 1.1, 4.5, 4.6, 11, 12 |
| 7 | Formula-only sets keep W2's ALL and NONE route verbatim; declared names distinct across sets as the precondition of `choice_wellFormed` | yes. The statement review fixed the route order so that W2's row is chosen before `choiceCore D`, the `⊥` check and `DeadReading`: a recorded narrowing stays on request on W2's route, as today | 2.1 (the Readings row); 2.5; 2.2; S2 (`choice_wellFormed`) | 1.1, 4.1, 4.7, 8.4 (`superpose_assertions`, `choice_wellFormed`), fixtures M11, M18; F20 extended |
| A1 | A fixed rule's `over` or `cites` reference to a name every candidate declares maps to every qualified copy | yes: the copy mapping is S2's (S1 did the admission half, `ReadingInterface`). Writing the statement showed that the mapping is faithful only when the copies carry one `over` list; the spec adds that as a superposability condition, not as a design change | 2.2 (interface name); 2.3 (`sup D`) | 1.4, 1.8, 8.3, fixtures M8, M14; resolved choice 14.3 |
| A2 | The combined slot `Lim_D ++ Choice_D ++ gated Rel_D`, labelled, with per-choice model correspondence; a candidate's totality premise enters as `χ → ρ`; one rule: `sup` gates everything a candidate owns or causes | yes: `slotP`, `Choice_D` appended after `Lim_D` (empty on the soft and norms chains), `gatedRel` empty until S3, both directions of model correspondence | 2.1 rule 4; 2.3 (the rule, `combined slot`); 2.7 | 1.4, 1.6, 4.3, 8.3, 8.4 (`base_down`, `base_up`) |
| A3 | Empty carrier: `superpose_conflict_free` needs no hypothesis; `superpose_all` drops it through the lifting lemma, stated explicitly; the fallback wording "every reading with at least one individual"; `base_up` keeps it | yes: the lifting lemma is built in S2a (composition.md 9.5 fixed its statements) | 2.5; S2; question 16 | 4.4, 8.2, 8.4, 9.4 (G5) |
| 3 | `dispatch` returns today's route on every list that has one; the error branch is new only outside today's lists and the validated chain | as a frozen input: the head `readings` hands `sup D` to the route `dispatch` names for the list without `readings@1` | 2.1 rules 1 and 6; S0 | 1.1, 4.1 |
| 5 | Fixed units' decisions go into the shared base, named by source key | as a frozen input: S1's source keys (`GenKey`, `genKeys`) are what the name map of S2 is defined on | 2.4; S1 | 1.7, 8.3 (`nameMap`) |
| A4 | `Content` in `VE.Compose.Content` (S0) | as a frozen input | section 0; S0 | 8.1 |
| 4 | Probe key `(kind, predicate, tuple)`; renamed-twin fixture | no: S1, unchanged by S2 | 2.4; S1 | — |
| Q4 | Decision-based separation kept; `SeparatedByDecisionOnly`; "suppose *the decider* decides the exception applies" | no: S1, unchanged by S2 | 2.4; section 3 | — |
| Q7 | Provenance mentions: attributed, counted separately, never changing a status | no: S4 | 2.8; S4 | — |

The two precisions the parent plan flagged for the statement reviews (its section 10, last paragraph) are settled
for S2 in the spec and nowhere else. First, in edit 1 an owner of a generated predicate may be a pair of candidates
of different sets, so a disjunct of `⋁ χ(owners)` may be a conjunction of two atoms (spec 1.6, fixture M10). Second,
edit 5's source keys are the names the spec's `nameMap` reads (spec 1.7).

Writing the statements exactly against the merged code found three places where the parent plan's S2 sketch is
false or not well typed as written; each is repaired in the spec without a design change and is listed for the
statement review to attack first (spec 13, 14): the copy mapping of A1 leaks a fixed exception's yield through an
unchosen copy whose `over` list differs from the chosen copy's, so `superpose_faithful` needs the superposability
condition of spec 1.8 (fixture M8); the plan's `pull` keeps the choice vocabulary's tuples, so its `base_down`
conclusion is never admissible for the choice's document (spec 1.7); and `encodes_unique`'s uniqueness needs the
other choice to be complete (spec 8.4). The spec states `superpose_all` per situation of a reading's document, in the
expansion of its base, so that a conclusion about a regulated predicate is covered; the plan's base-formula form is
its stated corollary.

The statement review of the spec's draft 1 (`manage-agents/debates/compose-s2-spec`, CONVERGED after round 2)
returned FIX with five corrections, none a design change, all in the spec's draft 2 (its change log): the route of
spec 1.1 is chosen before `choiceCore D`, the `⊥` check and `DeadReading`, which run only on the superposed and
enumerated routes, so a formula-only document with a coupling and recorded narrowings keeps W2's verdict and its
on-request narrowing (edit 7 above; fixture M18, F20 extended); `supReady` carries the shape of the couplings and
narrowings that today's decoders require, which `encodes_unique` and the theorems on it need (spec 1.8, 8.3; fixture
M17); `origin` is defined on the names of `sup D` and `qName` goes through the declaring set and the chosen
candidate, so the name map of an interface name lands on the chosen copy (spec 1.5, 1.7, 8.3; M1); the M8 wording
names the one copy that is a child of `base-x`; and spec 8.1 says that `Wire.lean` and `Run.lean` receive S2a's
additions with no S1 definition, statement or case kind changed.

## Process

No second design debate (the converged position). composition-s2.md goes to the Astra + Fable item-1 statement
review (PLAN-EXPAND2 rule 10) before any S2 Lean starts; a draft alone opens nothing. The review attacks
`superpose_faithful` first (the parent plan's order: F21's shape for rights, and in S2a the leak of fixture M8), then
the lifting lemma behind `superpose_all`. The review of draft 1 converged on FIX (above); the converged process from
here is one confirmation round on the spec's draft 2, scoped to the edited passages, and the S2a build gate opens
on its PASS. S0's statements ([composition.md](composition.md) sections 4, 5 and 9,
`lean/VE/Compose/*` as merged) and S1's ([composition-s1.md](composition-s1.md) draft 2 with its review, recheck and
loop fixes, `lean/VE/Readings/{Doc,Separate,Lines,Wire,Run}.lean` as merged at `119e2f8a`) are frozen inputs: the
spec instantiates them and changes no statement of them; `lean/VE/Compose/Adjoin.lean` is new, and `Wire.lean` and
`Run.lean` gain S2a's case kinds additively with no S1 definition, statement or case kind changed (spec 8.1). The
stage ends with both pilots rerun and audited on the units the parent
plan names for S2a (its section 6, row S2a; spec section 11), and the measured figures replace that row.

## Change log

| Revision | Changes |
|---|---|
| Draft 1 (commit `119e2f8a`) | The pointer: item 1 is stage S2a of composition-PLAN.md. |
| Draft 2 (2026-10-02) | The converged design debate applied, nothing else: the status note, the table of the converged edits that bind S2 with their places in the parent plan and in the spec, the two flagged precisions and the three repairs the statement spec makes, the process line. The pointer paragraph is unchanged. No statement, fixture or stage of the parent plan changed. Design only. |
| Draft 3 (2026-10-02) | The converged statement review of the spec's draft 1 recorded (`debates/compose-s2-spec`, CONVERGED after round 2 on FIX, five corrections) and the references synchronized to the spec's draft 2: the status note; edit 7's row (the route order, fixtures M18 and F20) and A1's row (resolved choice 14.3, not 13.3); the paragraph on the five corrections; the process line (one confirmation round on draft 2; `Wire.lean` and `Run.lean` additive, `Adjoin.lean` new); the cross-reference to the spec's sections 13 and 14. The pointer paragraph is unchanged. No statement, fixture or stage of the parent plan changed. |
