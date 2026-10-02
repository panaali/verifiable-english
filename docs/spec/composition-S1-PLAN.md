# Composition stage S1 (pointer plan)

> Status: planning draft 2 (2026-10-02), pointer only: no code, Lean or frozen contract changes. Draft 2 applies the
> converged Astra + Fable design debate recorded in `manage-agents/debates/design-compose-s1/{astra,fable}.md` and
> nothing else. Both files end `STATUS: CONVERGED` after round 3; the Astra seat was held in all three rounds by Sol
> xhigh as the recorded cross-family stand-in. The debate's question (`TOPIC.md`) is the parent plan,
> [composition-PLAN.md](composition-PLAN.md), and its joint position is Fable's round 3 list, accepted by the Astra
> seat's round 3: REVISE draft 1 of the parent plan into draft 2, then BUILD through statement review with no second
> design debate. Every converged edit is already in the parent plan's draft 2, whose section 10 maps each edit to
> its change. This file therefore restates no edit: the table below lists which converged edits bind stage S1 and
> where each one sits. The statement specification of S1 is [composition-s1.md](composition-s1.md), the file the
> parent plan and [composition.md](composition.md) call `readings.md`.

Item 1 of THIS plan is stage S1 of docs/spec/composition-PLAN.md (the next stage after S0 in that plan's stage order, which is merged on main with docs/spec/composition.md). Apply that plan's S1 section, its fixtures and open questions; S0's statements are frozen inputs. Measure the unlock on the constitution and UDHR pilot units the plan names for S1.

## The converged edits and where each binds S1

Numbering is the parent plan's section 10: edits 1 to 7 are Fable's round 1 list, Q4 and Q7 the two reporting
wordings, A1 to A4 the Astra seat's four corrections. "Parent" is composition-PLAN.md draft 2; "spec" is
composition-s1.md.

| # | Converged edit | Binds S1? | Parent | Spec |
|---|---|---|---|---|
| 4 | Drop `Probe.selects (rule)`; the probe key is `(kind, predicate, tuple)`, today's key; renamed-twin fixture | yes: one of the two points S1's specification starts from | 2.4; S1 (`Probe`, `selectable`, `Observes`, acceptance); F22 | 1.6, 4.5, 8.3, fixtures F22 and K3 |
| 5 | Fixed units' decisions go into the shared base, so they are not enumerated | yes: the other starting point | 2.4 (situation, `Achieves`, the bound); S1 (`sharedBase`, `sharedName`, `Achieves`, `separates`, `separates_sound`) | 1.5, 1.6, 4.5, 8.3, fixture K5 |
| 7 | Declared names distinct across sets, checked across sets (the Astra seat's wider form: every declared name) | yes: an admission check of S1, and the precondition S2's `choice_wellFormed` names | 2.2; S1 scope | 1.3, 4.3, fixture K8 |
| 7 | Formula-only sets keep W2's ALL and NONE route | yes, as a limit: S1 changes nothing for a set whose candidates are all assertions | 2.1 (the Readings row); 2.5; section 3 | 4.8, 4.9, fixture K16 |
| Q4 | Keep decision-based separation; finding `SeparatedByDecisionOnly`; the IDE says "suppose *the decider* decides the exception applies" | yes | 2.4 (the Force bullet, the finding); section 3; S1 scope; section 7 question 4 | 1.7, 2 (E14, E15), 4.6, 8.3 |
| A1 | A fixed rule's `over` or `cites` reference to a name every candidate declares maps to every qualified copy | the admission half: the interface name and `ReadingInterface`. The copy mapping is S2's | 2.2 (interface name); 2.3 (`sup D`) | 1.3, 4.2, fixture K9 |
| A4 | `Content` in `VE.Compose.Content` (S0) | yes: S1 opens S0's type and defines none of its own | section 0; S0 (`Content`); S1 (`open`) | 1.2, 8.2 |
| 3 | `dispatch` returns today's route on every list that has one; the error branch is new only outside today's lists and the validated chain | as a frozen input: S1 registers `readings@1` and wires `dispatch` as composition.md 4.2 defines it | 2.1 rules 1 and 6; S0 | 1.1, 4.1, 9.5 |
| 6 | S2a (soft) first; rights on the enumerated fallback until the rights `superpose_faithful`, bar case included, is proved | as a limit: document verdicts over content-bearing sets stay UNKNOWN until S2 | section 0; S2; section 6 | 0, 4.8 |
| 1 | Owner-based quiescence, `aimed_m` included; F21 | no: S2 | 2.3; 2.6; S2; F21 | — |
| 2 | Rule 2 states the quiescence exception | no: S2 | 2.1 rule 2 | — |
| Q7 | Provenance mentions: attributed, counted separately, never changing a status | no: S4 | 2.8; S4 scope; F17 | — |
| A2 | The combined slot `Lim_D ++ Choice_D ++ gated Rel_D`; a candidate's totality premise enters as `χ → ρ` | no: S2 and S3. S1 adds no premise | 2.1 rule 4; 2.3; 2.7 | 5 |
| A3 | Empty carrier: `superpose_conflict_free` needs no hypothesis; `superpose_all` through the lifting lemma | no: S2 | 2.5; S2; section 7 question 16 | — |

The two precisions the parent plan flagged for the statement reviews (its section 10, last paragraph) are settled
for S1 in the spec and nowhere else. The shared base names generated predicates by source key (spec 1.5), and a
key is shared exactly when every rule or limitation name in it is a fixed unit's (spec 1.5, resolved choice 13.3).

## Process

No second design debate (the converged position). composition-s1.md goes to the Astra + Fable item-1 statement
review (PLAN-EXPAND2 rule 10) before any S1 Lean starts; a draft alone opens nothing. S0's statements
([composition.md](composition.md) sections 4, 5 and 9, and `lean/VE/Compose/*` as merged) are frozen inputs: the
spec instantiates them and changes none. The stage ends with both pilots rerun and audited on the units the parent
plan names for S1 (its section 6, row S1; spec section 11), and the measured figures replace that row.

Statement review of spec draft 1 (`manage-agents/debates/compose-s1-spec/{astra,fable}.md`, CONVERGED after round
3; the Astra seat was again held by Sol xhigh as the recorded cross-family stand-in): **FIX**. The joint position
names seven corrections to composition-s1.md (Fable's six edits and the Astra seat's refusal of a fixed unit
attached to two sets) and none to this file: the design, the table above and every pointer in it stand. Spec draft
2 applies them and lists each in its change log. The S1 Lean build stays closed until the re-review of the changed
statements, admission rules, wording and fixtures passes (spec section 12).

Verification of spec draft 2 against that joint position (`manage-agents/compose-s1-p3ver1.final.md`): the seven
corrections are present and nothing else changed in substance, and one correction was incomplete. Spec 4.5 claimed
that `separates` enforces all of step 1, a base valid over the author's vocabulary included, and `situationWF`
never tests that validity. The spec now qualifies the claim: `separates` checks step 1's conditions on keys, tables
and the probe, and the base's validity stays the decoder's proof and the hypothesis `valid` of `separates_sound`,
as the joint position has it. No definition or theorem statement of the spec changes, and nothing in this file's
design, table or pointers. The build stays closed as above.

## Change log

| Revision | Changes |
|---|---|
| Draft 1 (commit `3a99ed1e`) | The pointer: item 1 is stage S1 of composition-PLAN.md. |
| Draft 2 (2026-10-02) | The converged design debate applied, nothing else: the status note, the table of the converged edits that bind S1 with their places in the parent plan and in the spec, the process line. The pointer paragraph is unchanged. No statement, fixture or stage of the parent plan changed. Design only. |
| Draft 2, review note (2026-10-02) | The outcome of the statement review of spec draft 1 recorded under Process: FIX, applied in spec draft 2, re-review pending. The joint position asks no edit of this file, and none is made beyond this record: no pointer, edit, stage or design point changed. |
| Draft 2, verification note (2026-10-02) | The outcome of the verification of spec draft 2 recorded under Process: one correction incomplete (the spec's claim that `separates` enforces all of 4.5 step 1, base validity included), qualified in the spec with no statement changed. No edit of this file beyond this record: no pointer, edit, stage or design point changed. |
