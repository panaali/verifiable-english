# Presupposition and definite descriptions (`presupposition@0`): item-1 statement specification

> Status: draft 3, 2026-10-14, branch `research/presupposition-p1`. Written from
> [presupposition-PLAN.md](presupposition-PLAN.md) draft 4. This is PS-S's deliverable. Theorem statements and
> fixtures are implementation obligations, not claims of completed proofs or tests.

## Changes in this draft (draft 3)

Draft 3 applies phase 1 ([docs/research/presupposition-phase1.md](../research/presupposition-phase1.md), cited as
Ph1) and the DRI's ruling PS-C9. **No Lean definition, body or theorem statement changes**, and no fixture value
changes: phase 1 changes the English of the pilot's heading units and where the report is carried, not their
formulas. The scratch stub `lean/SpecStubs_presupposition.lean` is not tracked, so it needs no edit, and the
elaboration status below is unchanged.
- **Headings' English** (1.4a, 2.1, 7.4). The formulas of P1–P4 round-trip through VE's renderer (Ph1 2.3), but VE
  English has no admitted relational-noun wording today ("is a core value of" and every variant tried fall back to
  the quoted form; Ph1 2.5): P1, P2 and P4's English waits for the plan's PS-6r. P3 is writable now as "Some thing is
  unsolved." with the sort noun "thing". Uniqueness is written in VE's enumerated form; the one-line form is refused.
- **The quoted fallback is not VE English** (2.3, 8): "has the recorded relation …" never carries a claim.
- **The assumed line is the target wording** (2.3): PS-E2 tests what PS-6r's rows render.
- **The report is a field of the Lean document mode's answer** (4.7; DRI PS-C9): no `presuppositions` service mode.
- **Fixture wording** (3, 7.3): "Some entity …" becomes "Some thing …"; A25 is stated on formulas.
- **Choices C19–C22** (10).

> Draft 2's header follows.
>
> **Draft 2** applies the statement review of draft 1 (`manage-agents/debates/presupposition-spec/`: `fable.md`,
> `astra.md`, and the arbiter's `DRI-RULING.md`, verdict FIX). The ruling's points D1 to D6 and corrections 1 to 14
> are written here; each edit is tagged with its point, for example (R-D1) or (R-7). In short:
> - **In place** (R-D1 to R-D4, R-1 to R-5). In place is never a reading of its own. At a *shallow* frame (`not ·`
>   or the antecedent of "if", 4.2) it has the same models as conditioned, by a Lean theorem over the whole unit, and
>   the conditioned reading carries it as an alias wording. At every other frame it is not offered, and a recorded
>   in-place carrier is refused. An open set needs at least two readings after merging.
> - **Admission** (R-D5, R-D6, R-6, R-7, R-10). A heading position for the presuppositions of titles; a unit may
>   assume itself only there; a trigger inside another trigger's restriction is refused; unresolved admission drops
>   its UNFORMALISED escape; unresolved rule readings obey the default restriction.
> - **Semantics of open sets and coupling** (R-8, R-9). Separation is named per document, open sets with a
>   conditioned rule reading are on the norms chain only, and coupling compares picks under the unspecified
>   completion when the document carries `norm-defaults@0`.
> - **Plan, experiment, English, fixtures** (R-11 to R-14).
>
> PS-S passes only when the ruling's gate holds: both documents and the stub carry every edit; the stub elaborates
> in a checkout whose Lean modules are built; every `#guard` passes; and both reviewers do a bounded re-check of
> the edited sections. PS-1 starts only after that.
>
> **Not yet elaborated.** Every definition and statement below is transcribed in the scratch file
> `lean/SpecStubs_presupposition.lean`: definitions with their bodies, each theorem as a `Prop`-valued definition
> `stmt_<name>`, and every fixture value as a `#guard` on a finite model. The stubs have not elaborated and the
> `#guard`s have not run: draft 1's attempt failed with `unknown module prefix 'VE'` because the checkout had no
> built modules, which is not evidence either way, and draft 2's session could not run commands. The fixture values
> in section 7 were derived by hand and count as computed only once the stub run passes. The run, after
> `lake build` in the same checkout: `cd lean && PATH=~/.elan/bin:$PATH lake env lean SpecStubs_presupposition.lean`.
> The scratch file contains no word the Lean audit bans, and it is not committed.
>
> Section 10 lists every place where this draft chose between readings of the plan or of the ruling.

## 0. Scope, one paragraph

A presupposition trigger ("the owner", "Claude’s core values", "the operator’s instructions") is a row of a closed
table. The row builds three formulas at the trigger's position: what it takes for granted (`pre`), the clause with
`pre` built in (`strong`), and the clause read where `pre` holds (`weak`). Lean regenerates the trigger's position (a
one-hole frame in the unit's carrier-free base content, a W1 rule's act, or a heading) and its projected goal
(Karttunen's filtering). Each occurrence is an obligation with exactly one carrier: proved by a checked certificate
from strictly earlier units and declared background; assumed as an explicit asserted unit; asserted as
`goal ∧ clause`; conditioned as `goal → clause` (for a rule, its guard gains `pre`, and only an `unspecified`
predicate may be conditioned); or unresolved, as a reading set whose readings are exactly the row's measured
candidates at that position, at least two of them, with in place never a reading of its own (1.8). Several
carriers in one unit compose by one operator that puts asserted goals above every condition. Coupling of equal goals
is an optional compression that Lean admits only after checking that no admissible joint reading is lost. Nothing
here changes a frozen report text, a P0, W1 or W3 theorem statement, or a checker function. One hash-frozen source
changes: discourse's `Descriptions.lean` gains the generalised description builders, its hash in
`lean/VE/Route/frozen-sources.sha256` is renewed, and today's `uniqueD` and `assertive` stay equal to their current
bodies by `rfl`.

## 1. Definitions

### 1.1 Rows and readings

- A **row** is one of `definite`, `plural` and `generic` (section 4.4). Other names are refused
  (`PresuppositionUnknownRow`).
- A **reading** is a triple of formulas over the hole's context: `pre`, `strong`, `weak`. A row's **definedness** at a
  valuation `τ` is `strong ↔ pre ∧ weak` there (`Reading.DefinedAt`).
- **Arguments** come from the wire: `sort` and `restriction` (definite and plural), `body` (the clause at the hole,
  for content positions), and `pre` (generic only). A rule's act and a heading have no `body`.

| Row | `pre` | `strong` | `weak` |
|---|---|---|---|
| `definite σ D P` (context of length `n`) | `uniqueOpen n σ D` = `∃x:σ (D ∧ ∀y:σ (D' → y = x))` | `assertiveOpen n σ D P` = `∃x:σ (D ∧ (∀y:σ (D' → y = x)) ∧ P)` | `presupposed σ D P` = `∀x:σ (D → P)` |
| `plural σ D P` | `∃x:σ D` | `(∃x:σ D) ∧ ∀x:σ (D → P)` | `∀x:σ (D → P)` |
| `generic pre body` | `pre` | `pre ∧ body` | `pre → body` |

`D'` is `raise1 n D`: the restriction weakened past the inner binder, so its variable 1 and above skip the outer
binder's index. All three definite formulas are built in discourse's file (4.1); on closed restrictions (`n = 0`)
they are discourse@1's `uniqueD`, `assertive` and `presupposed` exactly.

### 1.2 Frames, goals and position classes

- A **frame** `f` is a formula with one hole, built from VE's eleven formula constructors (section 4.2). `f.plug a`
  puts `a` in the hole. `f.binders` lists the sorts of the binders crossed, innermost first; the hole's context is
  `f.binders ++ Γ`.
- The **projected goal** `f.goal p`:
  - passes through negation, the left side of every connective and the antecedent of "if";
  - gains the left side as a hypothesis on the right of "and" and of "if", and its negation on the right of "or";
  - closes universally over every binder crossed, "some" included.
- **Reach.** `f.Reach S ρ τ` holds when the hole is evaluated at `τ` from `ρ`, under what the text to its left
  guarantees there (Schlenker's incremental local context). `goal_denote` says the goal holds exactly when `p` holds
  at every reached valuation.
- **Position class** (`Frame.cls`): the first operator from the root that is not "and" or a quantifier decides it:
  none (`top`), "not" (`negated`), the antecedent of "if" (`antecedent`), the consequent of "if" (`consequent`), a
  disjunct (`disjunct`). A rule's act is `ruleAct`. `ruleGuard` exists for authoring only (10, C2).
- **Shallow frame** (`Frame.shallow`, R-D1): the frame is exactly "not" at the root (`notF hole`) or exactly the
  antecedent of a root "if" (`impL hole r`). Only there does in place have the models of conditioned for every row
  and every composition of carriers (`inPlace_iff_conditioned_shallow`, 4.3). Other frames of class `negated` or
  `antecedent` are not shallow, for example `not (not ·)`, `not (· and r)`, `not (· or r)` and `(not ·) and r`.
- `f.close p` is the universal closure over the binders alone, without hypotheses: the proviso's unconditional goal.
- **Heading** (R-10). A trigger in a heading has no frame: the heading's unit states what it takes for granted, so
  its goal is `pre` itself, built over the empty context.

### 1.3 Base content

A unit's **base content** `B` is its content with each trigger's clause (`strong`) in place and no carrier added. For
a rule, the **base rule** is the rule with the conditions that carriers added removed from its guard. Every frame and
every goal is computed on the base content or the base rule (D2-8). So a `pre` that one carrier adds never filters
another obligation, and never proves its own goal. Paths in the wire are paths into `B`.

### 1.4 Carriers

Write `G = f.goal pre` for an obligation at frame `f` in `B`.

| Carrier | The unit's recorded content | What else must exist | Where `G` fails |
|---|---|---|---|
| proved | `B` | a deduction node whose certificate checks `G` from `premisesBefore` (1.7) | cannot fail in a model of the premises |
| assumed | `B` | an asserted unit whose content is `G` | not a model of the document |
| asserted | `G ∧ B` (`assertedAt`) | — | false, at every frame (`asserted_false_off_goal`) |
| conditioned | `G → B` (`conditionedAt`) | — | says nothing, at every frame (`conditioned_vacuous_off_goal`) |
| in place (local accommodation) | `B` (`inPlaceAt`) | — | the clause as written: true where `pre` fails at a shallow negated frame, possibly false at a nested one (R-5) |
| unconditional | `B` | an asserted unit whose content is `f.close pre` | not a model of the document |
| unresolved | an open reading set (1.8) | — | readings@1 verdicts |

- Where `G` holds and the row is defined at every reached valuation, asserted, conditioned and in place all equal
  the weak reading of the whole sentence (`carriers_on_goal`, from `collapse`).
- In place and unconditional exist only in cells where PS-E1 measures them: in place only at a shallow frame in a
  `negated` or `antecedent` cell (option (e); R-5), unconditional in the `consequent` cells (the proviso bar).
- **In place is the conditioned reading's alias** (R-D1, R-D2). At a shallow frame, in place and conditioned have the
  same content denotation for the whole unit, and neither has a premise (`inPlace_iff_conditioned_shallow`). So in
  place is never a reading of its own: the conditioned reading carries the in-place wording as an alias. At any other
  frame no equivalence is stated, in place is not offered, and a recorded in-place carrier is refused
  (`PresuppositionCandidates`; 8, "in place at a nested frame").
- A recorded carrier other than proved and unresolved must be one of the row's candidates at the obligation's position
  class: the translator's narrowing, attributed and labelled (discourse 2.4). Otherwise `PresuppositionCandidates`.
  A heading admits only proved and assumed (1.4a).
- **The assumed unit** is another unit, except at a heading (R-D5): an obligation at a path or a rule act whose
  assumed unit is its own unit is `PresuppositionAssumedUnit`.

### 1.4a Headings (R-10)

A heading's presupposition is the heading's own unit, stated as an assumption: "Claude’s core values" heads a unit
whose content is "Claude has at least one core value". The obligation's position is `{"heading": {}}`. It has no
frame and no `body`; its `pre` is the row's `pre` over the empty context (`buildPre row 0 args`), and its goal is
`pre`. Its carrier is proved or assumed; any other carrier is `PresuppositionCandidates`. An assumed heading carrier
may name the obligation's own unit, whose content must then be exactly `pre` (`admit_heading_goal`,
`admit_assumed_sound`). This is PS-0p's audit rule "exactly the existence, nothing more", checked by Lean.

**The heading unit's English** (Ph1 2.2, 2.5; C19). Lean checks the formula; whether the fenced English says it stays
the audit's. In the pilot, the existence sentence needs the sort's English noun not to be reserved (the constitution
pilot declares `entity` as "thing"/"things", a document field), and the restriction needs an admitted wording. Today
"{0} is unsolved" is admitted (P3: "Some thing is unsolved."), and no relational-noun wording is (P1, P2, P4 wait for
the plan's PS-6r). A uniqueness `pre` is written in VE's enumerated form, "There is a first thing such that both of
the following hold: (a) the first thing is a N of t; (b) for every second thing that is a N of t, the second thing is
the same as the first thing.". With the unary stand-in "unsolved" it parses to exactly the existence-and-uniqueness
formula (Ph1 2.5); with a relational noun it is measured once PS-6r lands.

### 1.5 Several obligations in one unit

The unit's recorded content is `carried ms B`, where `ms` lists each obligation's root mode and goal in block order:
asserted contributes its goal as a left conjunct; conditioned contributes its goal as an antecedent; every other
carrier contributes nothing at the root.

`carried ms B = A₁ ∧ (A₂ ∧ … ∧ (C₁ → (C₂ → … → B)))`, the `Aᵢ` the asserted goals and the `Cⱼ` the conditioned goals,
each group in block order.

- An asserted goal never sits under another obligation's condition, so where it fails the unit is false
  (`carried_asserted`).
- Where a conditioned goal fails, the unit says exactly its asserted goals (`carried_conditioned_off`).
- Where every goal holds, the unit is `B` (`carried_on_goals`).
- `peel k m` removes `k` left conjuncts and then `m` antecedents; `peel` of `carried` returns `B` (`peel_carried`).
  This is how Lean recovers `B` from the recorded content before it locates the paths.
- **A trigger inside another trigger's restriction** (R-D6). A definite's or plural's `strong` writes its restriction
  `D` twice (the definite's second copy is `raise1 n D`). A path that enters either copy of another obligation's
  restriction is refused with `PresuppositionPosition`, decided from the two paths and the row's restriction offsets
  (`restrictionPaths`, 4.7). A path into the other obligation's body `P` is unaffected. (8, "a trigger in a
  restriction".)

### 1.6 Rules

- The **rule goal** of a trigger in the act of rule `N` on regulated predicate `r` is
  `ruleGoal r N pre = ∀x̄:r.sorts (applies N → pre)`. The binders are `r.sorts` in declared order (D2-1), never
  `N.over`, which holds precedence names. `pre` is over the context `r.sorts.reverse`.
- **Conditioning.** `conditionNode N c` is `N` with guard `g ∧ c`. `conditionRule T n c` conditions the rule named
  `n` in place; every rule keeps its name, predicate, sign, carve-outs and precedence (`conditionRule_shape`). This is
  the plan's `replaceNode`.
- Several conditioned obligations on one rule add their `pre`s in block order: guard `((g ∧ pre₁) ∧ pre₂) …`.
- **Where `pre` fails** the conditioned rule selects nothing: it contributes no decision
  (`conditioned_contributes_nothing`). The predicate is UNDECIDED there only where no other rule of either sign
  decides, and only because it is `unspecified`: norm-defaults' `value3 P N .unspecified` is `unsaid` exactly when
  neither side decides (`unsaid_iff`).
- **Default predicates.** For a predicate with an allow or deny default, the default would decide where the text says
  nothing. A conditioned carrier on its rules is refused: `PresuppositionDefault: <obligation>: <predicate>`. So is an
  unresolved obligation on its rules whose cell lists conditioned (R-7): the candidate is refused, never silently
  dropped from the open set.
- **Candidates.** A rule act has no asserted carrier; its candidates are at most assumed and conditioned
  (`candidates_ruleAct`, over the table's shape check).
- **Validity.** The recorded tree and the base tree both pass W1's `validate` (a computed check, not a proof).
- **Source identity.** When several rules take one closed `pre` for granted, assuming `pre` once entails every one of
  their rule goals (`source_identity_entails`). Lean offers it as one extra, labelled choice; it is never imposed.

### 1.7 Premises of a proved carrier

`premisesBefore D u` is the declared background (W5 flags, literal distinctness, W3 definitions, in the P0 generator
order) followed by the contents of the asserted claim units strictly before `u`, in document order (D2-3). Rule
elaborations, the unit `u` itself and every later unit are excluded. A certificate that needs any of them fails:
`PresuppositionCertificate`.

### 1.8 Candidates, the table and reading sets

- `Candidate` is one of assumed, conditioned, asserted, in place, unconditional.
- The **candidate table** gives, per row and position class, the candidates in the row's order. PS-E1 fills it. Until
  then every cell is empty, so no obligation is admitted as unresolved, and authoring refuses every unproved trigger.
- **Shape check** (`cellOk`, `tableOk`): no duplicates; never both assumed and asserted in one cell (they have the same
  models, so readings@1 could not separate them; 10, C3); no asserted in a `ruleAct` cell; in place only in a
  `negated` or `antecedent` cell, and only together with `conditioned` in the same cell (R-2; an in-place entry
  licenses only the alias, which is used only at a shallow frame in such a cell, R-5); unconditional only in
  `consequent`.
- An **unresolved** obligation's unit carries an open reading set whose readings are, in the cell's order, one per
  **emitted** candidate (`expectedReadings`). The emitted candidates are the cell's candidates other than in place:
  in place is never emitted, at any frame (R-D1).
  - a claim's reading is `carried ms B` with this obligation's root mode set by the candidate, plus a premise for
    assumed (`G`) and unconditional (`f.close pre`);
  - a rule's reading is the base rule with the other obligations' recorded conditions, plus this one's for
    conditioned, and the premise `G` for assumed.
  - **Aliases** (R-1, R-D2). Each reading carries a list of alias candidates, ordered as in the cell. The conditioned
    reading at a shallow frame whose cell lists in place has the aliases `[inPlace]`; every other reading has none.
    A merged reading's canonical content and premise are the conditioned reading's. Picks, `readingFor`, the lines
    of 2.3 and the rewrites of 2.4 name the canonical reading, with the alias wording shown beside it.
- **At least two readings** (R-D3, R-6). The open set must have at least two emitted readings after merging; fewer is
  `PresuppositionCandidates`. So a cell with one candidate, or with conditioned and in place only, admits no open
  set.
- readings@1's own check requires the readings to be pairwise separated by admitted situations; PS-2a calls it (R-8):
  - when the document carries `norm-defaults@0`, readings-defaults' separation on the document under the unspecified
    completion: `separates (fillDoc N) s i j σ` with `fillHolds N s i σ.base` (`lean/VE/Readings/Unspecified.lean`,
    sound for `SeparatedU`);
  - otherwise readings@1's `separates D s i j σ` (`lean/VE/Readings/Separate.lean`).
  A failed separation is readings@1's own diagnostic on the admission path; in translation the unit stays
  UNFORMALISED (8).
- **Chains** (R-8). An open set that contains a conditioned rule reading needs an `unspecified` predicate, so the
  document carries `norm-defaults@0`, and the open set is therefore on the norms chain only: on the soft and rights
  chains `abstention` in `lean/VE/Readings/Wire.lean` refuses readings@1 content beside `norm-defaults@0`
  ("UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented").
- At most one unresolved obligation per unit (10, C6).

### 1.9 Coupling (PS-3)

- A **pick** chooses one emitted candidate per unresolved obligation; it never names in place (`PickFits`, R-3).
- A **group** is two or more unresolved obligations with equal goals and equal cells, all of whose candidates are root
  carriers (assumed, conditioned, asserted). Groups are computed on the table cell, so an in-place entry in the cell
  still keeps a group from forming; the alias is invisible to coupling (R-3). Every obligation is in at most one
  group. In presupposition@0 a unit's only open set is its obligation's own, so every obligation sits in the root
  reading alternative (10, C9).
- The **representative** of a pick on a group sets every member to assumed if any member chose assumed; else to
  asserted if any chose asserted; else to conditioned.
- **Couplable.** Over the existing constrained joint set `J` (lf-14d's enumeration, within its budget), every pick's
  representative is in `J`. Only couplable groups are coupled, by generated `requires` constraints.
- `coupling_complete`: for a couplable group, every admissible pick's representative is admissible and uniform, and
  has the same models, the same `decides` at typed tuples and the same assumptions. A group that is not couplable stays
  uncoupled: equal goals never impose one choice by themselves.
- **Models under the document's semantics** (R-9). "The same models" compares each picked document under its own
  semantics: without a norm-defaults block, W1's elaboration (today's form); with one, norm-defaults' unspecified
  completion (`IntendedAt3` on each regulated predicate), with each picked document passing `WellFormedU`. The
  placeholder `deny` that `placeholderFrame` writes for an `unspecified` predicate is never applied. `decides` is
  compared over the models of the same case split.
- In place and unconditional candidates are never in a group; they couple only through an explicit shared
  source-choice identity with its own preservation proof (not in presupposition@0).

## 2. English

### 2.1 What each row takes for granted

| Row | Trigger | `pre` in English |
|---|---|---|
| definite | "the N", "the N of t", "t’s N" (singular) | "there is exactly one N" / "t has exactly one N" |
| plural | "t’s Ns", "the Ns of t", "its/their N" (mass or plural) | "there is at least one N" / "t has at least one N" |
| generic | factive complement, earlier state, earlier event (owner's row) | the owner's sentence, e.g. "the action was in progress before that day" |

These are the target sentences. "t has at least one N" and "t has exactly one N" need a relational-noun wording that
the wording lint admits; none is admitted today (Ph1 2.5), and the plan's PS-6r adds it. Until then a `pre` over a
relational noun has no VE English, and VE's quoted fallback ("… has the recorded relation "core_value_of" to
claude") is not a substitute: it is not VE English, and an audit rejects a claim written in it (C20). "There is at
least one N" with a unary wording parses today once the sort's noun is not reserved ("Some thing is unsolved.").

### 2.2 One-reading paraphrases

Each line below is the English for exactly one formula. The formula column is what the paraphrase must elaborate
to; PS-6 proves each authoring rewrite has exactly one reading (`refused_have_rewrites`). "The owner is ready." uses
the `definite` row with `D = owner`, `P = ready`.

| Position | Carrier | Paraphrase | Formula |
|---|---|---|---|
| top | asserted | "There is exactly one owner, and that owner is ready." | `U ∧ assertive` |
| top | conditioned | "Where there is exactly one owner, that owner is ready." | `U → assertive` |
| top | assumed | "Assumed (from ‘the owner’): There is exactly one owner." and "The owner is ready." | unit `U`; content `assertive` |
| negated | asserted | "There is exactly one owner, and that owner is not ready." | `U ∧ ¬assertive` |
| negated | conditioned | "Where there is exactly one owner, that owner is not ready." | `U → ¬assertive` |
| negated (shallow) | in place: the conditioned reading's alias | "It is not so that both of these are so: there is exactly one owner, and that owner is ready." | `¬assertive` |
| consequent | asserted | "If the shop is open, then both of these are so: there is exactly one owner, and that owner is ready." | `(open → U) ∧ (open → assertive)` |
| consequent | conditioned | "If the shop is open and there is exactly one owner, then that owner is ready." | `(open → U) → (open → assertive)` |
| consequent | unconditional | "Assumed (from ‘the owner’): There is exactly one owner." and the sentence | unit `U`; content `open → assertive` |
| rule act | assumed | "Assumed (from ‘the operator’s instructions’): In every situation this rule covers, the operator has given at least one instruction." and the rule | unit `ruleGoal`; the base rule |
| rule act | conditioned | "If the operator has given at least one instruction, then Claude must follow the operator’s instructions." | the rule with guard `g ∧ pre` |

The consequent rows rely on two propositional equivalences, checked when the stub's fixtures run on S21:
`(o → U) ∧ (o → A)` is `o → (U ∧ A)`, and `(o → U) → (o → A)` is `(o ∧ U) → A`.

The negated in-place line and the consequent asserted line say "both of these are so" so that "and" cannot take
the outer operator's place (R-13): without it, "It is not so that there is exactly one owner and that owner is
ready" also reads as "(it is not so that there is exactly one owner) and that owner is ready". Both lines are PS-6
one-reading fixtures under `refused_have_rewrites` (7.6). The in-place line is shown only as the alias wording of the
conditioned reading at a shallow frame (1.4); the two lines of a merged reading have the same models.

### 2.3 Lines the reader sees

- **Proved.** No line by default. "Why": "‘<words>’ takes for granted that <pre>; <the earlier sentence, condition or
  declaration> says so."
- **Assumed.** In the assumptions list: "Assumed (from ‘<words>’): <goal>." For a relational noun this is the target
  wording ("Assumed (from ‘Claude’s core values’): Claude has at least one core value."); VE renders it once PS-6r's
  rows exist, and PS-E2 tests those rendered lines (C21).
- **Asserted.** The asserted paraphrase of 2.2.
- **Conditioned.** "This applies only where <goal>." For a rule: "Where <pre>, <rule>. Where not, this rule contributes
  no decision."
- **In place.** Never a line of its own (R-1). A recorded in-place carrier (shallow frames only) shows the in-place
  paraphrase of 2.2; in an open set, the conditioned reading at a shallow frame shows its line with the in-place
  paraphrase beside it, as one reading: "(2) This applies only where <goal>. Said another way: <in-place
  paraphrase>."
- **Unresolved.** "Two readings: (1) … (2) …", one per emitted reading, each followed by a situation where they
  differ, in document terms.
- **Refuted.** `PresuppositionRefuted: <obligation>: <assumed unit>` when the existing inconsistency report shows that
  the premises refute an assumed goal.
- No symbols, ids or arrows by default; obligation ids are in the provenance view. PS-E2 tests these lines.

### 2.4 Authoring: refusal and rewrites (PS-6)

A trigger construction in VE English is admitted with one reading only when its obligation is proved. Otherwise:

`PresuppositionUnresolved: ‘<words>’ takes for granted that <pre>.`

followed by exactly one rewrite per emitted reading (1.8), in the row's order (R-1):
- assumed: add "<goal>." to the document, before the sentence;
- conditioned: "Where <goal>, <sentence>."; for a rule, "If <pre>, then <rule sentence>.", offered only for an
  `unspecified` predicate; at a shallow frame whose cell lists in place, the in-place paraphrase is shown beside it as
  the same reading's other wording, not as a second rewrite;
- asserted: "<goal>, and <sentence with an anaphor>.";
- unconditional: add "<closure of pre>." to the document.

A one-reading cell offers exactly one rewrite, and the original wording is still refused (D2-6). An empty cell gives
the refusal with the advice "rephrase so that the sentence states or conditions on <pre>". At a frame that is not
shallow, an in-place entry in the cell offers nothing.

### 2.5 PS-E1's options (exact item wording)

The question is "What does the sentence say about this situation?" in a situation where the projected goal fails.
- (a) "The sentence is false in this situation." Dropped for rule-act items.
- (b) "The sentence says nothing about this situation." For rule-act items: "This rule decides nothing in this
  situation."
- (c) "The sentence takes for granted that <pre>, so this situation goes against the text."
- (d) "I cannot tell."
- (e) In the negated and antecedent cells only: "The sentence is true in this situation."

Results are labelled "proxy, an upper bound for careful readers". They decide candidates and wording only.

**Scoring option (e)** (R-D4). Every negated and antecedent item uses a shallow frame. Options (b) and (e) are scored
as one class only for an item whose stub `#guard` shows that in place and conditioned have the same value in that
item's failing situation; otherwise they are scored apart. "True here" is never identified with in place at a
compound or nested frame. The per-item frames and denotations are fixed in PS-E1's preregistration file (6) before
any model call.

## 3. Wire form

```json
"presuppositions": {
  "version": "presupposition@0",
  "obligations": [
    {"id": "p1", "unit": "u0156.s03", "span": [95180, 95191], "row": "plural",
     "position": {"rule_act": "no-system-prompt-deception"},
     "arguments": {"sort": "entity", "restriction": ["binary", "content_of", ["var", 0], ["var", 1]]},
     "carrier": {"conditioned": {}}},
    {"id": "p2", "unit": "u0013.presupposition", "span": [6120, 6144], "row": "plural",
     "position": {"heading": {}},
     "arguments": {"sort": "entity", "restriction": ["binary", "core_value_of", ["var", 0], ["const", "claude"]]},
     "carrier": {"assumed": {"unit": "u0013.presupposition"}}}
  ]
}
```

| Field | Type | Rule |
|---|---|---|
| `version` | `"presupposition@0"` | exact |
| `id` | token of the existing id grammar | unique in the block |
| `unit` | unit id | a unit of the document |
| `span` | `[start, end]` byte offsets | display and audit only; Lean never reads meaning from it |
| `row` | `"definite"`, `"plural"`, `"generic"` | else `PresuppositionUnknownRow` |
| `position` | `{"path": [i, …]}`, `{"rule_act": name}` or `{"heading": {}}` | path: child indices into the base content (`not`: 0; `and`, `or`, `implies`: 0 left, 1 right; `all`, `ex`: 0); heading: the unit is a heading's presupposition (1.4a) |
| `arguments` | object with optional `sort`, `restriction`, `body`, `pre` | P0 wire formulas over the hole's context, the described entity at index 0; absent, never `null` |
| `carrier` | one of `{"proved": {"node": id}}`, `{"assumed": {"unit": id}}`, `{"conditioned": {}}`, `{"asserted": {}}`, `{"in_place": {}}`, `{"unconditional": {"unit": id}}`, `{"unresolved": {}}` | exactly one key |

- At `rule_act` and at `heading`, `body` is absent; present, it is `PresuppositionMismatch: <obligation>: body`.
- The block sits in the front matter, so it is identity-bound through `document_id` like discourse's block.
- Python never reads the block's meaning: it sends the document to Lean and binds the `presuppositions` field of the
  document mode's answer (plan PS-2b; DRI PS-C9).
- p1's conditioned carrier is admitted only if the rule's predicate is `unspecified` in the norm-defaults block.
- p2 is a heading obligation assumed on its own unit (R-10). It is admitted only if u0013.presupposition is an
  asserted unit whose content is exactly `pre`, `∃x:entity core_value_of(x, claude)`; a unit that says more, or
  less, is `PresuppositionAssumedUnit: p2: u0013.presupposition`. Its English, "Some thing is a core value of
  Claude.", is writable once PS-6r admits the wording (1.4a); the formula does not depend on it.

## 4. Lean: definitions and exact statements

The stub transcribes each `theorem` below as `def stmt_<name> : Prop := ∀ …` with the same binders and conclusion.

### 4.1 `lean/VE/Discourse/Descriptions.lean` (edited in PS-1; frozen hash rehashed)

```lean
namespace VE.Discourse

def uniqueAt (σ : String) (Dr Dr' : VE.Formula) : VE.Formula :=
  .ex σ (.and Dr (.all σ (.implies Dr' (.eq (.var 0) (.var 1)))))
def assertiveAt (σ : String) (Dr Dr' P : VE.Formula) : VE.Formula :=
  .ex σ (.and Dr (.and (.all σ (.implies Dr' (.eq (.var 0) (.var 1)))) P))

/-- A restriction over `σ :: Δ` (`n = Δ.length`) weakened past one new binder at index 1, by W1's `inst`. -/
def raise1 (n : Nat) (Dr : VE.Formula) : VE.Formula :=
  VE.Norms.inst (.var 0 :: (List.range n).map (fun i => .var (i + 2))) Dr
def uniqueOpen (n : Nat) (σ : String) (Dr : VE.Formula) : VE.Formula := uniqueAt σ Dr (raise1 n Dr)
def assertiveOpen (n : Nat) (σ : String) (Dr P : VE.Formula) : VE.Formula := assertiveAt σ Dr (raise1 n Dr) P

-- today's definitions become wrappers; each is `rfl`-equal to its current body (S11)
def uniqueD (σ : String) (Dr : VE.Formula) : VE.Formula := uniqueAt σ Dr Dr
def assertive (σ : String) (Dr P : VE.Formula) : VE.Formula := assertiveAt σ Dr Dr P

theorem raise1_zero (Dr : VE.Formula) : raise1 0 Dr = Dr
theorem uniqueOpen_zero (σ : String) (Dr : VE.Formula) : uniqueOpen 0 σ Dr = uniqueD σ Dr
theorem assertiveOpen_zero (σ : String) (Dr P : VE.Formula) : assertiveOpen 0 σ Dr P = assertive σ Dr P
```

Every existing proof that unfolds `uniqueD` or `assertive` adds `uniqueAt` or `assertiveAt` to its `simp only` list;
no statement changes. `tools/trust-classes.json` gets the five new definitions.

### 4.2 `lean/VE/Presupposition/Frame.lean`

```lean
import VE.Semantics

namespace VE.Presupposition
universe u

inductive Frame where
  | hole
  | notF (f : Frame)
  | andL (f : Frame) (r : VE.Formula)
  | andR (l : VE.Formula) (f : Frame)
  | orL (f : Frame) (r : VE.Formula)
  | orR (l : VE.Formula) (f : Frame)
  | impL (f : Frame) (r : VE.Formula)
  | impR (l : VE.Formula) (f : Frame)
  | allF (s : String) (f : Frame)
  | exF (s : String) (f : Frame)
  deriving DecidableEq, Repr

def Frame.plug : Frame → VE.Formula → VE.Formula
  | .hole, a => a
  | .notF f, a => .not (f.plug a)
  | .andL f r, a => .and (f.plug a) r
  | .andR l f, a => .and l (f.plug a)
  | .orL f r, a => .or (f.plug a) r
  | .orR l f, a => .or l (f.plug a)
  | .impL f r, a => .implies (f.plug a) r
  | .impR l f, a => .implies l (f.plug a)
  | .allF s f, a => .all s (f.plug a)
  | .exF s f, a => .ex s (f.plug a)

def Frame.binders : Frame → List String
  | .hole => []
  | .allF s f | .exF s f => f.binders ++ [s]
  | .notF f | .andL f _ | .andR _ f | .orL f _ | .orR _ f | .impL f _ | .impR _ f => f.binders

def Frame.goal : Frame → VE.Formula → VE.Formula
  | .hole, p => p
  | .notF f, p | .andL f _, p | .orL f _, p | .impL f _, p => f.goal p
  | .andR l f, p | .impR l f, p => .implies l (f.goal p)
  | .orR l f, p => .implies (.not l) (f.goal p)
  | .allF s f, p | .exF s f, p => .all s (f.goal p)

def Frame.close : Frame → VE.Formula → VE.Formula
  | .hole, p => p
  | .notF f, p | .andL f _, p | .andR _ f, p | .orL f _, p | .orR _ f, p | .impL f _, p | .impR _ f, p => f.close p
  | .allF s f, p | .exF s f, p => .all s (f.close p)

def Frame.Reach (S : VE.Structure.{u}) : Frame → VE.Valuation S → VE.Valuation S → Prop
  | .hole, ρ, τ => τ = ρ
  | .notF f, ρ, τ | .andL f _, ρ, τ | .orL f _, ρ, τ | .impL f _, ρ, τ => f.Reach S ρ τ
  | .andR l f, ρ, τ | .impR l f, ρ, τ => l.denote S ρ ∧ f.Reach S ρ τ
  | .orR l f, ρ, τ => ¬ l.denote S ρ ∧ f.Reach S ρ τ
  | .allF s f, ρ, τ | .exF s f, ρ, τ => ∃ v, S.domain s v ∧ f.Reach S (v :: ρ) τ

def Frame.locate : VE.Formula → List Nat → Option (Frame × VE.Formula)
  | a, [] => some (.hole, a)
  | .not a, 0 :: p => (Frame.locate a p).map (fun x => (Frame.notF x.1, x.2))
  | .and a r, 0 :: p => (Frame.locate a p).map (fun x => (Frame.andL x.1 r, x.2))
  | .and l a, 1 :: p => (Frame.locate a p).map (fun x => (Frame.andR l x.1, x.2))
  | .or a r, 0 :: p => (Frame.locate a p).map (fun x => (Frame.orL x.1 r, x.2))
  | .or l a, 1 :: p => (Frame.locate a p).map (fun x => (Frame.orR l x.1, x.2))
  | .implies a r, 0 :: p => (Frame.locate a p).map (fun x => (Frame.impL x.1 r, x.2))
  | .implies l a, 1 :: p => (Frame.locate a p).map (fun x => (Frame.impR l x.1, x.2))
  | .all s a, 0 :: p => (Frame.locate a p).map (fun x => (Frame.allF s x.1, x.2))
  | .ex s a, 0 :: p => (Frame.locate a p).map (fun x => (Frame.exF s x.1, x.2))
  | _, _ :: _ => none

inductive PositionClass where
  | top | negated | antecedent | consequent | disjunct | ruleAct | ruleGuard
  deriving DecidableEq, Repr

def Frame.cls : Frame → PositionClass
  | .hole => .top
  | .andL f _ | .andR _ f | .allF _ f | .exF _ f => f.cls
  | .notF _ => .negated
  | .impL _ _ => .antecedent
  | .impR _ _ => .consequent
  | .orL _ _ | .orR _ _ => .disjunct

/-- R-D1: "not" at the root, or the antecedent of a root "if": where in place has the models of conditioned. -/
def Frame.shallow (f : Frame) : Prop := f = .notF .hole ∨ ∃ r, f = .impL .hole r

def Frame.shallowB : Frame → Bool
  | .notF .hole => true
  | .impL .hole _ => true
  | _ => false

theorem Frame.shallowB_iff (f : Frame) : f.shallowB = true ↔ f.shallow

instance (f : Frame) : Decidable f.shallow := decidable_of_iff _ f.shallowB_iff

theorem goal_denote (f : Frame) (p : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (f.goal p).denote S ρ ↔ ∀ τ, f.Reach S ρ τ → p.denote S τ

theorem plug_congr (f : Frame) (a b : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (h : ∀ τ, f.Reach S ρ τ → (a.denote S τ ↔ b.denote S τ)) :
    (f.plug a).denote S ρ ↔ (f.plug b).denote S ρ

theorem reach_typed (f : Frame) (S : VE.Structure.{u}) (Γ : List String) (ρ τ : VE.Valuation S)
    (hρ : VE.Valuation.Typed S Γ ρ) (h : f.Reach S ρ τ) : VE.Valuation.Typed S (f.binders ++ Γ) τ

theorem plug_wellFormed (E : VE.Environment) (f : Frame) (a : VE.Formula) (Γ : List String)
    (h : (f.plug a).WellFormed E Γ) : a.WellFormed E (f.binders ++ Γ)

theorem goal_wellFormed (E : VE.Environment) (f : Frame) (a p : VE.Formula) (Γ : List String)
    (hf : (f.plug a).WellFormed E Γ) (hp : p.WellFormed E (f.binders ++ Γ)) : (f.goal p).WellFormed E Γ

theorem close_wellFormed (E : VE.Environment) (f : Frame) (a p : VE.Formula) (Γ : List String)
    (hf : (f.plug a).WellFormed E Γ) (hp : p.WellFormed E (f.binders ++ Γ)) : (f.close p).WellFormed E Γ

theorem locate_plug (a : VE.Formula) (path : List Nat) (f : Frame) (b : VE.Formula)
    (h : Frame.locate a path = some (f, b)) : f.plug b = a
```

The instance needs `Frame.shallowB_iff` with a proof, so the stub proves it (a case split); it is the only proof in
the stub. `cls` and `shallow` are independent: a shallow frame has class `negated` or `antecedent`, but most frames
of those classes are not shallow (1.2).

### 4.3 `lean/VE/Presupposition/Reading.lean`

```lean
import VE.Presupposition.Frame
import VE.Norms.Prefix

structure Reading where
  pre    : VE.Formula
  strong : VE.Formula
  weak   : VE.Formula
  deriving DecidableEq, Repr

def Reading.DefinedAt (r : Reading) (S : VE.Structure.{u}) (τ : VE.Valuation S) : Prop :=
  r.strong.denote S τ ↔ r.pre.denote S τ ∧ r.weak.denote S τ

theorem collapse (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hdef : ∀ τ, f.Reach S ρ τ → r.DefinedAt S τ) (hgoal : (f.goal r.pre).denote S ρ) :
    (f.plug r.strong).denote S ρ ↔ (f.plug r.weak).denote S ρ

theorem collapse_certified (E : VE.Environment) (prem : List VE.Formula) (f : Frame) (r : Reading)
    (c : VE.Tableau.Certificate) (acc : VE.Tableau.checkCertificate E prem (f.goal r.pre) c = true)
    (hdef : ∀ S : VE.Structure.{u}, S.Admissible E → ∀ τ, f.Reach S [] τ → r.DefinedAt S τ)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S prem) :
    (f.plug r.strong).denote S [] ↔ (f.plug r.weak).denote S []

theorem collapse_assumed (E : VE.Environment) (prem : List VE.Formula) (f : Frame) (r : Reading)
    (hdef : ∀ S : VE.Structure.{u}, S.Admissible E → ∀ τ, f.Reach S [] τ → r.DefinedAt S τ)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S (prem ++ [f.goal r.pre])) :
    (f.plug r.strong).denote S [] ↔ (f.plug r.weak).denote S []

def assertedAt (f : Frame) (r : Reading) : VE.Formula := .and (f.goal r.pre) (f.plug r.strong)
def conditionedAt (f : Frame) (r : Reading) : VE.Formula := .implies (f.goal r.pre) (f.plug r.strong)
def inPlaceAt (f : Frame) (r : Reading) : VE.Formula := f.plug r.strong

theorem asserted_false_off_goal (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (h : ¬ (f.goal r.pre).denote S ρ) : ¬ (assertedAt f r).denote S ρ

theorem conditioned_vacuous_off_goal (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (h : ¬ (f.goal r.pre).denote S ρ) : (conditionedAt f r).denote S ρ

theorem carriers_on_goal (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hdef : ∀ τ, f.Reach S ρ τ → r.DefinedAt S τ) (hgoal : (f.goal r.pre).denote S ρ) :
    ((assertedAt f r).denote S ρ ↔ (f.plug r.weak).denote S ρ) ∧
    ((conditionedAt f r).denote S ρ ↔ (f.plug r.weak).denote S ρ) ∧
    ((inPlaceAt f r).denote S ρ ↔ (f.plug r.weak).denote S ρ)

inductive Root where
  | bare | asserted | conditioned
  deriving DecidableEq, Repr

def carried (ms : List (Root × VE.Formula)) (B : VE.Formula) : VE.Formula :=
  (ms.filter (fun m => m.1 == Root.asserted)).foldr (fun m a => .and m.2 a)
    ((ms.filter (fun m => m.1 == Root.conditioned)).foldr (fun m a => .implies m.2 a) B)

def peel : Nat → Nat → VE.Formula → Option VE.Formula
  | 0, 0, a => some a
  | 0, m + 1, .implies _ b => peel 0 m b
  | k + 1, m, .and _ b => peel k m b
  | _, _, _ => none

theorem carried_denote (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) :
    (carried ms B).denote S ρ ↔
      (∀ m ∈ ms, m.1 = Root.asserted → m.2.denote S ρ) ∧
      ((∀ m ∈ ms, m.1 = Root.conditioned → m.2.denote S ρ) → B.denote S ρ)

theorem carried_asserted (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (m : Root × VE.Formula) (hm : m ∈ ms) (ha : m.1 = Root.asserted)
    (h : (carried ms B).denote S ρ) : m.2.denote S ρ

theorem carried_conditioned_off (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (m : Root × VE.Formula) (hm : m ∈ ms) (hc : m.1 = Root.conditioned)
    (hoff : ¬ m.2.denote S ρ) :
    (carried ms B).denote S ρ ↔ ∀ m' ∈ ms, m'.1 = Root.asserted → m'.2.denote S ρ

theorem carried_on_goals (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (h : ∀ m ∈ ms, m.1 ≠ Root.bare → m.2.denote S ρ) :
    (carried ms B).denote S ρ ↔ B.denote S ρ

theorem peel_carried (ms : List (Root × VE.Formula)) (B : VE.Formula) :
    peel (ms.filter (fun m => m.1 == Root.asserted)).length
      (ms.filter (fun m => m.1 == Root.conditioned)).length (carried ms B) = some B

/-- Congruence through `carried`: a conditioned goal whose failure already gives `B` changes nothing at the root. -/
theorem carried_idle (ms₁ ms₂ : List (Root × VE.Formula)) (g B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (h : ¬ g.denote S ρ → B.denote S ρ) :
    (carried (ms₁ ++ (Root.conditioned, g) :: ms₂) B).denote S ρ ↔
      (carried (ms₁ ++ (Root.bare, g) :: ms₂) B).denote S ρ

/-- R-D2: at a shallow frame, the whole unit with this obligation in place has the models of the whole unit with it
    conditioned, whatever the other obligations' root modes `ms₁`, `ms₂`. -/
theorem inPlace_iff_conditioned_shallow (f : Frame) (hf : f.shallow) (r : Reading)
    (ms₁ ms₂ : List (Root × VE.Formula)) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hpre : ∀ τ, f.Reach S ρ τ → r.strong.denote S τ → r.pre.denote S τ) :
    (carried (ms₁ ++ (Root.bare, f.goal r.pre) :: ms₂) (f.plug r.strong)).denote S ρ ↔
      (carried (ms₁ ++ (Root.conditioned, f.goal r.pre) :: ms₂) (f.plug r.strong)).denote S ρ
```

`inPlace_iff_conditioned_shallow` is the whole-unit statement of R-D2: the unit's content under each candidate is
`carried ms B` (`claimReading`, 4.7), with `B = f.plug r.strong` when the frame is located from the unit's root
(`locate_plug`), and neither candidate has a premise. Its hypotheses are explicit: the row's `strong → pre` at the
reached valuations (`hpre`, which every row's definedness lemma gives at typed valuations), and congruence through
`carried` (`carried_idle`). No equivalence of in place with any other candidate is stated, at any frame that is not
shallow. PS-2a's `admit_inPlace_alias` (4.7) states the same equivalence over `claimReading` for an admitted
document; Reading.lean cannot name `claimReading`, which is PS-2a's (10, C13).

### 4.4 `lean/VE/Presupposition/Rows.lean`

```lean
import VE.Presupposition.Reading
import VE.Discourse.Descriptions

def definite (n : Nat) (σ : String) (D P : VE.Formula) : Reading :=
  { pre := VE.Discourse.uniqueOpen n σ D, strong := VE.Discourse.assertiveOpen n σ D P,
    weak := VE.Discourse.presupposed σ D P }

def plural (σ : String) (D P : VE.Formula) : Reading :=
  { pre := .ex σ D, strong := .and (.ex σ D) (.all σ (.implies D P)), weak := .all σ (.implies D P) }

def generic (pre body : VE.Formula) : Reading :=
  { pre := pre, strong := .and pre body, weak := .implies pre body }

/-- Generalises `VE.Discourse.description_definedness` (the case `Δ = []`, `τ = []`). -/
theorem definite_defined (E : VE.Environment) (Δ : List String) (σ : String) (hσ : σ ∈ E.sorts)
    (D P : VE.Formula) (hD : D.WellFormed E (σ :: Δ)) (hP : P.WellFormed E (σ :: Δ))
    (S : VE.Structure.{u}) (hS : S.Admissible E) (τ : VE.Valuation S) (hτ : VE.Valuation.Typed S Δ τ) :
    (definite Δ.length σ D P).DefinedAt S τ

theorem plural_defined (σ : String) (D P : VE.Formula) (S : VE.Structure.{u}) (τ : VE.Valuation S) :
    (plural σ D P).DefinedAt S τ

theorem generic_defined (pre body : VE.Formula) (S : VE.Structure.{u}) (τ : VE.Valuation S) :
    (generic pre body).DefinedAt S τ

/-- The arguments as one tuple: `(sort, restriction, body, pre)`. Errors name the field. -/
def buildReading (row : String) (n : Nat) (a : Option String × Option VE.Formula × Option VE.Formula ×
    Option VE.Formula) : Except String Reading :=
  match row, a with
  | "definite", (some σ, some D, some P, none) => .ok (definite n σ D P)
  | "plural", (some σ, some D, some P, none) => .ok (plural σ D P)
  | "generic", (none, none, some b, some p) => .ok (generic p b)
  | "definite", _ | "plural", _ | "generic", _ => .error "arguments"
  | _, _ => .error "row"

def buildPre (row : String) (n : Nat) (a : Option String × Option VE.Formula × Option VE.Formula ×
    Option VE.Formula) : Except String VE.Formula :=
  match row, a with
  | "definite", (some σ, some D, none, none) => .ok (VE.Discourse.uniqueOpen n σ D)
  | "plural", (some σ, some D, none, none) => .ok (.ex σ D)
  | "generic", (none, none, none, some p) => .ok p
  | "definite", (_, _, some _, _) | "plural", (_, _, some _, _) | "generic", (_, _, some _, _) => .error "body"
  | "definite", _ | "plural", _ | "generic", _ => .error "arguments"
  | _, _ => .error "row"
```

`buildReading row (f.binders.length) args` at a content position (the unit's content is closed, so the hole's
context is `f.binders`); `buildPre row r.sorts.length args` at a rule act; `buildPre row 0 args` at a heading (R-10).
For a definite at a content position, `buildPre` and `(buildReading …).pre` agree, and so do the plural forms.

### 4.5 `lean/VE/Presupposition/Rules.lean`

```lean
import VE.Presupposition.Reading
import VE.Norms.Elaborate
import VE.NormDefaults.Semantics

def ruleGoal (r : VE.Norms.Regulated) (N : VE.Norms.Node) (pre : VE.Formula) : VE.Formula :=
  VE.Norms.bindAll r.sorts (.implies (VE.Norms.applies N) pre)

def conditionNode (N : VE.Norms.Node) (c : VE.Formula) : VE.Norms.Node := { N with guard := .and N.guard c }

def conditionRule (T : VE.Norms.Tree) (n : String) (c : VE.Formula) : VE.Norms.Tree :=
  { T with nodes := T.nodes.map (fun M => if M.name == n then conditionNode M c else M) }

theorem condition_applies (N : VE.Norms.Node) (c : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (VE.Norms.applies (conditionNode N c)).denote S ρ ↔ (VE.Norms.applies N).denote S ρ ∧ c.denote S ρ

theorem conditionRule_shape (T : VE.Norms.Tree) (n : String) (c : VE.Formula) :
    (conditionRule T n c).regulated = T.regulated ∧ (conditionRule T n c).definitions = T.definitions ∧
    (conditionRule T n c).nodes.map (fun M => (M.name, M.pred, M.sign, M.carveOuts, M.over)) =
      T.nodes.map (fun M => (M.name, M.pred, M.sign, M.carveOuts, M.over))

theorem rule_collapse_decides (T : VE.Norms.Tree) (n : String) (c : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (h : ∀ M ∈ T.nodes, M.name = n → (VE.Norms.applies M).denote S ρ → c.denote S ρ)
    (p : String) (sign : Bool) :
    (VE.Norms.decides (conditionRule T n c) p sign).denote S ρ ↔ (VE.Norms.decides T p sign).denote S ρ

theorem rule_collapse_typed (T : VE.Norms.Tree) (r : VE.Norms.Regulated) (N : VE.Norms.Node) (pre : VE.Formula)
    (S : VE.Structure.{u}) (hname : ∀ M ∈ T.nodes, M.name = N.name → M = N)
    (hgoal : (ruleGoal r N pre).denote S []) (vs : List S.Carrier) (hvs : VE.TupleTyped S r.sorts vs)
    (p : String) (sign : Bool) :
    (VE.Norms.decides (conditionRule T N.name pre) p sign).denote S (VE.Norms.tupleVal vs) ↔
      (VE.Norms.decides T p sign).denote S (VE.Norms.tupleVal vs)

theorem rule_collapse_certified (E : VE.Environment) (prem : List VE.Formula) (T : VE.Norms.Tree)
    (r : VE.Norms.Regulated) (N : VE.Norms.Node) (pre : VE.Formula) (cert : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate E prem (ruleGoal r N pre) cert = true)
    (hname : ∀ M ∈ T.nodes, M.name = N.name → M = N)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S prem)
    (vs : List S.Carrier) (hvs : VE.TupleTyped S r.sorts vs) (p : String) (sign : Bool) :
    (VE.Norms.decides (conditionRule T N.name pre) p sign).denote S (VE.Norms.tupleVal vs) ↔
      (VE.Norms.decides T p sign).denote S (VE.Norms.tupleVal vs)

theorem conditioned_contributes_nothing (T : VE.Norms.Tree) (f : Nat) (N : VE.Norms.Node) (c : VE.Formula)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) (h : ¬ c.denote S ρ) :
    ¬ (VE.Norms.selects T f (conditionNode N c)).denote S ρ

theorem unsaid_iff (P N : Prop) : VE.NormDefaults.value3 P N .unspecified = .unsaid ↔ ¬ P ∧ ¬ N

theorem source_identity_entails (E : VE.Environment) (pre : VE.Formula) (hpre : pre.WellFormed E [])
    (S : VE.Structure.{u}) (h : pre.denote S []) (r : VE.Norms.Regulated) (N : VE.Norms.Node) :
    (ruleGoal r N pre).denote S []
```

`rule_collapse_decides` needs no validity: it holds at any valuation where every rule named `n` gives the condition
when it applies. `rule_collapse_typed` instantiates it at typed tuples of the predicate's sorts, from the rule goal,
through `VE.Norms.bindAll_denote_nil`. The hypothesis `hname` (rule names unique) holds in every W1-valid tree.

### 4.6 `lean/VE/Presupposition/Agree.lean`

```lean
import VE.Presupposition.Rows
import VE.Data.Background
import VE.SpeechActs.Answer

theorem discourse_definite_is_row (σ : String) (D P : VE.Formula) :
    (definite 0 σ D P).pre = VE.Discourse.uniqueD σ D ∧
    (definite 0 σ D P).strong = VE.Discourse.assertive σ D P ∧
    (definite 0 σ D P).weak = VE.Discourse.presupposed σ D P

theorem data_attribute_proved (E : VE.Environment) (f : VE.Data.Background.Flag) (c : String)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hc : E.constants c = some f.source)
    (hfun : (VE.Data.Background.functionalPremise f).denote S [])
    (htot : (VE.Data.Background.totalPremise f).denote S []) :
    (Frame.hole.goal (VE.Discourse.uniqueD f.target (.binary f.name (.const c) (.var 0)))).denote S []

theorem speech_question_top (D : VE.SpeechActs.SpeechDoc) (q : VE.SpeechActs.Question) :
    Frame.hole.goal (VE.SpeechActs.presupposition D q) = VE.SpeechActs.presupposition D q
```

(Plan draft 1 wrote `VE.Data.Flag`; the flag type is `VE.Data.Background.Flag`.)

### 4.7 `lean/VE/Presupposition/{Wire,Admit,Run}.lean` (PS-2a)

**Where the report goes** (DRI PS-C9). `Run.lean` builds the report that the Lean document mode's answer carries as
its `presuppositions` field (plan PS-4); there is no `presuppositions` service mode, no runner of its own and no
schema of its own. Nothing below depends on the choice: every statement is over `admit` and `PDoc`.

**Types.**

```lean
inductive Carrier where
  | proved (node : String) | assumed (unit : String) | conditioned | asserted | inPlace
  | unconditional (unit : String) | unresolved
  deriving DecidableEq, Repr

inductive Candidate where
  | assumed | conditioned | asserted | inPlace | unconditional
  deriving DecidableEq, Repr

def Carrier.root : Carrier → Root            -- asserted ↦ asserted, conditioned ↦ conditioned, else bare
def Carrier.cand : Carrier → Option Candidate -- the candidate a recorded carrier stands for; none for proved, unresolved
def Candidate.root : Candidate → Root
def Candidate.core : Candidate → Bool        -- assumed, conditioned, asserted

inductive Position where
  | path (p : List Nat)
  | ruleAct (rule : String)
  | heading                                   -- R-10: `{"heading": {}}`
  deriving DecidableEq, Repr

structure Args where
  sort        : Option String := none
  restriction : Option VE.Formula := none
  body        : Option VE.Formula := none
  pre         : Option VE.Formula := none
  deriving DecidableEq, Repr

structure Obligation where
  id : String
  unit : String
  span : Nat × Nat
  row : String
  position : Position
  args : Args
  carrier : Carrier
  deriving DecidableEq, Repr

abbrev CandidateTable := String → PositionClass → List Candidate
def candidateTable : CandidateTable := fun _ _ => []     -- filled from PS-E1's output
def cellOk (pc : PositionClass) (cs : List Candidate) : Bool
def tableOk (rows : List String) (t : CandidateTable) : Bool

inductive RContent where
  | claim (a : VE.Formula)
  | rule (N : VE.Norms.Node)
  deriving DecidableEq, Repr

structure RReading where
  cand : Candidate                          -- the canonical candidate; never `.inPlace`
  aliases : List Candidate                  -- R-1: other wordings of the same reading, ordered as in the cell
  content : RContent
  premise : Option VE.Formula
  deriving DecidableEq, Repr

inductive UContent where
  | claim (a : VE.Formula) | rule (name : String) | readings (rs : List RReading) | unformalised
  deriving DecidableEq, Repr

structure DocUnit where
  id : String
  asserted : Bool
  content : UContent
  deriving DecidableEq, Repr

/-- PS-2a's view of the decoded W2 document. -/
structure PDoc where
  E : VE.Environment
  lits : List String
  norms : VE.Norms.Tree                     -- the fixed W1 rules
  defaults : Bool                           -- R-8, R-9: the document carries `norm-defaults@0`
  unspec : List String                      -- norm-defaults' `unspecified` predicates ([] without its block)
  background : List VE.Formula              -- declared background, P0 generator order
  units : List DocUnit                        -- document order
  proofs : List (String × VE.Tableau.Certificate)   -- deduction nodes: id, certificate
  block : Option (List Obligation)

structure Checked where
  ob : Obligation
  frame : Frame                 -- in the base content; `.hole` at a rule act and at a heading
  pre : VE.Formula
  reading : Option Reading      -- none at a rule act and at a heading
  goal : VE.Formula
  pos : PositionClass           -- `.top` at a heading, which has no cell (only proved and assumed)
  deriving DecidableEq, Repr

structure Report where
  checked : List Checked                    -- one per obligation, block order
  bases : List (String × VE.Formula)        -- each claim unit with obligations: its base content
  baseTree : VE.Norms.Tree                  -- every rule with the carriers' conditions removed (open rules included)
```

The bodies of `tableOk`, `premisesBefore`, `unitContent`, `unitAsserted`, `unitReadings`, `nodeCertificate`,
`unitModes`, `claimReading`, `ruleReading` and `ruleConditions` are in the stub, as written in sections 1.4 to 1.8;
`claimReading` and `ruleReading` set `aliases := []`. Draft 2 drops `unitUnformalised`, which no statement uses any
more (R-6). The definitions that draft 2 changes or adds are written here in full:

```lean
/-- R-2: in place only in a negated or antecedent cell, and only beside conditioned. -/
def cellOk (pc : PositionClass) (cs : List Candidate) : Bool :=
  decide cs.Nodup && !(cs.contains .assumed && cs.contains .asserted) &&
    (!cs.contains .inPlace || cs.contains .conditioned) &&
    cs.all (fun c => match c with
      | .assumed | .conditioned => true
      | .asserted => pc != .ruleAct
      | .inPlace => pc == .negated || pc == .antecedent
      | .unconditional => pc == .consequent)

/-- R-D1: the candidates that become readings: the cell without in place, in the cell's order. -/
def emitted (t : CandidateTable) (c : Checked) : List Candidate := (t c.ob.row c.pos).filter (· != .inPlace)

/-- R-1, R-D2: a reading's aliases, ordered as in the cell: in place, on the conditioned reading at a shallow frame. -/
def aliasesOf (t : CandidateTable) (c : Checked) (k : Candidate) : List Candidate :=
  (t c.ob.row c.pos).filter (fun a => a == .inPlace && k == .conditioned && decide c.frame.shallow)

/-- The readings an unresolved obligation's unit must carry: one per emitted candidate, in the cell's order. -/
def expectedReadings (t : CandidateTable) (R : Report) (c : Checked) : Option (List RReading) :=
  match c.ob.position with
  | .path _ => ((R.bases.find? (fun x => x.1 == c.ob.unit)).map (·.2)).map (fun B =>
      (emitted t c).map (fun k => { claimReading R c B k with aliases := aliasesOf t c k }))
  | .ruleAct n => (R.baseTree.nodes.find? (fun N => N.name == n)).map (fun N =>
      (emitted t c).map (ruleReading R c N))
  | .heading => none

/-- R-D1, check step 4: a recorded carrier's candidate is in the cell, and in place also needs a shallow frame. -/
def carrierAllowed (t : CandidateTable) (c : Checked) (k : Candidate) : Bool :=
  (t c.ob.row c.pos).contains k && (k != .inPlace || decide c.frame.shallow)

/-- R-D6: every path from a row's `strong` to a copy of its restriction `D` (4.4: `assertiveAt`, `plural`). -/
def restrictionPaths : String → List (List Nat)
  | "definite" => [[0, 0], [0, 1, 0, 0, 0]]
  | "plural" => [[0, 0], [1, 0, 0]]
  | _ => []

/-- R-D6: the path `q` enters the restriction of the obligation of row `row` at path `p`. -/
def entersRestriction (row : String) (p q : List Nat) : Bool :=
  (restrictionPaths row).any (fun o => (p ++ o).isPrefixOf q)
```

A rule-act cell never lists in place (`cellOk`), so `emitted` drops nothing there, and the rule readings have no
aliases. The body `P` sits at `[0, 1, 1]` in a definite's `strong` and at `[1, 0, 1]` in a plural's, outside every
restriction path; a generic row has no restriction.

**The check, in order.** The first failing step gives the answer.
1. Budget: at most 256 obligations, and every regenerated formula within W1's 10,000-node AST budget; else
   `ResourceLimit: presuppositions` (UNKNOWN).
2. Per obligation, block order: a unique id (`PresuppositionMismatch: <o>: id`), an existing unit (`…: unit`) and a
   known row (`PresuppositionUnknownRow`).
3. Per unit with obligations, document order: the base content `B = peel kₐ k꜀ (recorded content)` for a claim unit
   (for an open set, from each reading, all equal), and the base rule for a rule; a shape that does not peel is
   `PresuppositionMismatch: <first obligation of the unit>: content` or `…: rule`.
4. Per obligation, block order:
   - position: the path locates in `B`, the rule is the unit's (fixed or open), or, at a heading, the unit is a
     claim unit; else `PresuppositionPosition`. A path that enters another obligation's restriction in the same unit
     (`entersRestriction`, R-D6) is also `PresuppositionPosition`;
   - arguments: `buildReading` at a path, `buildPre` at a rule act and at a heading (with `n = 0`); errors are
     `PresuppositionMismatch: <o>: arguments` or `…: body`; at a path the located subformula is `strong`, else
     `…: clause`;
   - carrier: proved checks against `premisesBefore` (`PresuppositionCertificate`); assumed and unconditional need an
     asserted unit with the regenerated content, and at a path or a rule act the assumed unit is not the
     obligation's own (`PresuppositionAssumedUnit`, R-D5); a heading admits only proved and assumed
     (`PresuppositionCandidates`, R-10); a conditioned rule needs an `unspecified` predicate, and so does an
     unresolved rule obligation whose cell lists conditioned (`PresuppositionDefault`, R-7); a recorded carrier must
     pass `carrierAllowed`: in the cell, and in place only at a shallow frame (`PresuppositionCandidates`, R-D1);
     unresolved needs an open set on its unit (`PresuppositionUnresolved`), with exactly `expectedReadings` and at
     least two of them (`PresuppositionCandidates`, R-D3), and no second unresolved obligation in the unit
     (`PresuppositionCandidates` on the second).
5. Per unit: `carried (unitModes R u) B` equals the recorded content (`…: content`); each recorded rule equals its base
   rule with `ruleConditions` (`…: rule`); the recorded tree and the base tree pass `VE.Norms.validate` (`…: rule`);
   readings@1's separation check accepts each open set (its diagnostic). The separation function is named by the
   document (R-8): with `norm-defaults@0`, readings-defaults' `separates (fillDoc N) s i j σ` with
   `fillHolds N s i σ.base` (under the unspecified completion); without it, readings@1's `separates D s i j σ`.

An open set that contains a conditioned rule reading needs an `unspecified` predicate, hence `norm-defaults@0`, and
is therefore admitted on the norms chain only. On the soft and rights chains `abstention` in
`lean/VE/Readings/Wire.lean` refuses it before this check runs: "UnsupportedProfile: readings@1 content with
norm-defaults@0 is not implemented" (R-8; fixtures A26, A27). In place appears only at a shallow frame in a
negated or antecedent cell (R-5), as the conditioned reading's alias or as a recorded carrier.

**Statements.** `admit` is PS-2a's function `PDoc → Except String Report`.

```lean
theorem admit_regenerates (D : PDoc) (R : Report) (h : admit D = .ok R) :
    D.block = some (R.checked.map (·.ob))

theorem admit_goals_from_base (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (p : List Nat) (hp : c.ob.position = .path p) :
    ∃ B r, (c.ob.unit, B) ∈ R.bases ∧ c.reading = some r ∧ Frame.locate B p = some (c.frame, r.strong) ∧
      buildReading c.ob.row c.frame.binders.length c.ob.args.tuple = .ok r ∧
      c.pre = r.pre ∧ c.goal = c.frame.goal r.pre ∧ c.pos = c.frame.cls

theorem admit_rule_goal (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (n : String) (hp : c.ob.position = .ruleAct n) :
    ∃ N ∈ R.baseTree.nodes, N.name = n ∧ ∃ r ∈ D.norms.regulated, r.name = N.pred ∧
      buildPre c.ob.row r.sorts.length c.ob.args.tuple = .ok c.pre ∧ c.goal = ruleGoal r N c.pre ∧
      c.pos = .ruleAct ∧ c.ob.args.body = none

/-- R-10: a heading's goal is its `pre` over the empty context; no body; only proved or assumed. -/
theorem admit_heading_goal (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (hp : c.ob.position = .heading) :
    buildPre c.ob.row 0 c.ob.args.tuple = .ok c.pre ∧ c.goal = c.pre ∧ c.ob.args.body = none ∧
      ((∃ n, c.ob.carrier = .proved n) ∨ (∃ u, c.ob.carrier = .assumed u))

/-- R-D6: no admitted path enters the restriction of another obligation of its unit. -/
theorem admit_outside_restrictions (D : PDoc) (R : Report) (h : admit D = .ok R) (c d : Checked)
    (hc : c ∈ R.checked) (hd : d ∈ R.checked) (hu : c.ob.unit = d.ob.unit) (p q : List Nat)
    (hp : c.ob.position = .path p) (hq : d.ob.position = .path q) :
    entersRestriction c.ob.row p q = false

theorem admit_claim_content (D : PDoc) (R : Report) (h : admit D = .ok R) (x : String × VE.Formula)
    (hx : x ∈ R.bases) (hres : ∀ c ∈ R.checked, c.ob.unit = x.1 → c.ob.carrier ≠ .unresolved) :
    unitContent D x.1 = some (carried (unitModes R x.1) x.2)

theorem admit_rule_content (D : PDoc) (R : Report) (h : admit D = .ok R) :
    VE.Norms.WellFormed ⟨D.E, D.lits, D.norms⟩ = true ∧ VE.Norms.WellFormed ⟨D.E, D.lits, R.baseTree⟩ = true ∧
    ∀ N ∈ R.baseTree.nodes, ∀ M ∈ D.norms.nodes, M.name = N.name →
      M = (ruleConditions R N.name).foldl conditionNode N

theorem admit_proved_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (n : String) (hp : c.ob.carrier = .proved n) :
    ∃ cert, nodeCertificate D n = some cert ∧
      VE.Tableau.checkCertificate (env D) (premisesBefore D c.ob.unit) c.goal cert = true

/-- R-D5: the assumed unit is the obligation's own only at a heading. -/
theorem admit_assumed_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (u : String) (hp : c.ob.carrier = .assumed u) :
    unitAsserted D u = true ∧ unitContent D u = some c.goal ∧ (c.ob.position ≠ .heading → u ≠ c.ob.unit)

theorem admit_unconditional_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (u : String) (hp : c.ob.carrier = .unconditional u) :
    unitAsserted D u = true ∧ unitContent D u = some (c.frame.close c.pre)

/-- R-7: also an unresolved rule obligation whose cell lists conditioned. -/
theorem admit_conditioned_rule_unspecified (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (n : String) (hpos : c.ob.position = .ruleAct n)
    (hcar : c.ob.carrier = .conditioned ∨
      (c.ob.carrier = .unresolved ∧ Candidate.conditioned ∈ candidateTable c.ob.row .ruleAct)) :
    ∃ N ∈ R.baseTree.nodes, N.name = n ∧ N.pred ∈ D.unspec

/-- R-D1, R-10: a recorded carrier is in the cell, and in place only at a shallow frame; headings excepted. -/
theorem admit_carrier_candidate (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hpos : c.ob.position ≠ .heading) (k : Candidate) (hk : c.ob.carrier.cand = some k) :
    k ∈ candidateTable c.ob.row c.pos ∧ (k = .inPlace → c.frame.shallow)

/-- R-6, R-D3: exactly the expected readings, at least two of them; no UNFORMALISED escape. -/
theorem admit_unresolved_readings (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hu : c.ob.carrier = .unresolved) :
    unitReadings D c.ob.unit = expectedReadings candidateTable R c ∧
      ∃ rs, expectedReadings candidateTable R c = some rs ∧ 2 ≤ rs.length

/-- R-6: under the empty table no checked obligation is unresolved. -/
theorem admit_empty_table (hT : ∀ row pc, candidateTable row pc = []) (D : PDoc) (R : Report)
    (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked) : c.ob.carrier ≠ .unresolved

/-- R-D2 over `claimReading`: at a shallow frame, in place and conditioned have the same content denotation for the
    whole unit, and neither has a premise. The alias of `aliasesOf` is attached exactly where this applies. -/
theorem admit_inPlace_alias (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (p : List Nat) (hp : c.ob.position = .path p) (hs : c.frame.shallow) (B : VE.Formula)
    (hB : (c.ob.unit, B) ∈ R.bases) (r : Reading) (hr : c.reading = some r)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hpre : ∀ τ, c.frame.Reach S ρ τ → r.strong.denote S τ → r.pre.denote S τ) :
    (∃ a a', (claimReading R c B .inPlace).content = .claim a ∧
      (claimReading R c B .conditioned).content = .claim a' ∧ (a.denote S ρ ↔ a'.denote S ρ)) ∧
    (claimReading R c B .inPlace).premise = none ∧ (claimReading R c B .conditioned).premise = none

theorem no_silent_accommodation (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hu : c.ob.carrier = .unresolved) : unitContent D c.ob.unit = none

theorem one_open_per_unit (D : PDoc) (R : Report) (h : admit D = .ok R) (c d : Checked)
    (hc : c ∈ R.checked) (hd : d ∈ R.checked) (hu : c.ob.unit = d.ob.unit)
    (hcu : c.ob.carrier = .unresolved) (hdu : d.ob.carrier = .unresolved) : c.ob.id = d.ob.id

theorem candidates_ruleAct (t : CandidateTable) (ht : tableOk rowNames t = true) (row : String)
    (hrow : row ∈ rowNames) (c : Candidate) (hc : c ∈ t row .ruleAct) : c = .assumed ∨ c = .conditioned

/-- PS-2a's wrapper (and PS-4's document mode) on a document without the block. -/
theorem no_block_unchanged (D : PDoc) (h : D.block = none) : admitWrapped D = admitBase D
```

`candidateTable` is a constant; `#guard tableOk rowNames candidateTable` runs in `Examples.lean` once PS-E1 fills it.
Under the empty table no obligation is unresolved (`admit_empty_table`), so the "table starts empty" limit (8) is a
theorem, not a reliance on readings@1's internals.

### 4.8 `lean/VE/Presupposition/Couple.lean` (PS-3)

```lean
abbrev Pick := List (String × Candidate)
def pickOf (ch : Pick) (o : String) : Option Candidate := (ch.find? (fun x => x.1 == o)).map (·.2)

structure Group where
  members : List String
  goal : VE.Formula
  cands : List Candidate
  deriving DecidableEq, Repr

def groups (t : CandidateTable) (R : Report) : List Group         -- 1.9; body in the stub
def repCandidate (g : Group) (ch : Pick) : Candidate
def rep (g : Group) (ch : Pick) : Pick :=
  ch.map (fun x => if g.members.contains x.1 then (x.1, repCandidate g ch) else x)
def Uniform (g : Group) (ch : Pick) : Prop := ∀ o ∈ g.members, ∀ o' ∈ g.members, pickOf ch o = pickOf ch o'
def couplable (J : List Pick) (g : Group) : Bool :=
  g.cands.all Candidate.core && J.all (fun ch => J.contains (rep g ch))
def coupledSet (J : List Pick) (gs : List Group) : List Pick := J.filter (fun ch => gs.all (fun g => uniformB g ch))

def formulasUnder (D : PDoc) (R : Report) (ch : Pick) : List VE.Formula      -- background, claims, picked readings
def treeUnder (D : PDoc) (R : Report) (ch : Pick) : VE.Norms.Tree            -- fixed rules and picked open rules
def assumptionsUnder (D : PDoc) (R : Report) (ch : Pick) : List VE.Formula   -- the picked readings' premises

/-- R-3: a pick names emitted readings only, never in place. -/
def PickFits (t : CandidateTable) (R : Report) (ch : Pick) : Prop :=
  (ch.map (·.1)).Nodup ∧
  (∀ x ∈ ch, ∃ c ∈ R.checked, c.ob.id = x.1 ∧ c.ob.carrier = .unresolved ∧ x.2 ∈ emitted t c) ∧
  ∀ c ∈ R.checked, c.ob.carrier = .unresolved → (pickOf ch c.ob.id).isSome

/-- R-9: the picked document as norm-defaults' `UDoc`. -/
def pickedU (D : PDoc) (R : Report) (ch : Pick) : VE.NormDefaults.UDoc :=
  ⟨⟨D.E, D.lits, treeUnder D R ch⟩, D.unspec⟩

/-- R-9: a model of the picked document under the document's own semantics: W1's elaboration without a
    norm-defaults block; with one, the unspecified completion. The placeholder `deny` is never applied. -/
def SatUnder (D : PDoc) (R : Report) (ch : Pick) (S : VE.Structure.{u}) : Prop :=
  if D.defaults then
    VE.Norms.Sat S (formulasUnder D R ch) ∧
      ∀ r ∈ D.norms.regulated, VE.NormDefaults.IntendedAt3 (pickedU D R ch) r S
  else VE.Norms.Sat S (formulasUnder D R ch ++ VE.Norms.elaborate (treeUnder D R ch))

/-- R-9: with a norm-defaults block, the picked document passes norm-defaults' check. -/
def PickedWF (D : PDoc) (R : Report) (ch : Pick) : Prop :=
  D.defaults = true → VE.NormDefaults.WellFormedU (pickedU D R ch) = true

def SameModels (D : PDoc) (R : Report) (ch ch' : Pick) : Prop :=
  PickedWF D R ch ∧ PickedWF D R ch' ∧
  ∀ S : VE.Structure.{u}, S.Admissible D.E → (SatUnder D R ch S ↔ SatUnder D R ch' S)

def SameDecides (D : PDoc) (R : Report) (ch ch' : Pick) : Prop :=
  ∀ S : VE.Structure.{u}, S.Admissible D.E → SatUnder D R ch S →
    ∀ r ∈ D.norms.regulated, ∀ vs, VE.TupleTyped S r.sorts vs → ∀ sign : Bool,
      ((VE.Norms.decides (treeUnder D R ch) r.name sign).denote S (VE.Norms.tupleVal vs) ↔
        (VE.Norms.decides (treeUnder D R ch') r.name sign).denote S (VE.Norms.tupleVal vs))

theorem coupling_complete (D : PDoc) (R : Report) (h : admit D = .ok R) (J : List Pick) (g : Group)
    (hg : g ∈ groups candidateTable R) (hc : couplable J g = true) (ch : Pick) (hch : ch ∈ J)
    (hfit : PickFits candidateTable R ch) :
    rep g ch ∈ J ∧ Uniform g (rep g ch) ∧ SameModels.{u} D R ch (rep g ch) ∧ SameDecides.{u} D R ch (rep g ch) ∧
      ∀ φ, φ ∈ assumptionsUnder D R ch ↔ φ ∈ assumptionsUnder D R (rep g ch)

theorem coupled_uniform (J : List Pick) (gs : List Group) (g : Group) (hg : g ∈ gs) (ch : Pick)
    (hch : ch ∈ coupledSet J gs) : Uniform g ch

theorem coupled_subset (J : List Pick) (gs : List Group) (ch : Pick) (hch : ch ∈ coupledSet J gs) : ch ∈ J
```

- `J` is lf-14d's enumeration of the existing constrained joint set. PS-3 proves, against lf-14d's API once it lands,
  that its generated `requires` constraints cut `J` down to exactly `coupledSet J (couplable groups)`
  (`couplings_spec`); the constraint type is lf-14d's and is pinned then.
- Why `coupling_complete` holds: a mixed pick that contains assumed or asserted entails the shared goal `G`; under `G`
  each conditioned member equals its base (`carried_on_goals`, `rule_collapse_typed`), so the representative has the
  same models and decisions. With a norm-defaults block the same argument runs through `IntendedAt3`, whose value at
  each typed tuple is read off `decides` (`Value3`). A pick that is all conditioned is its own representative. The
  assumptions agree because the representative is assumed exactly when some member was.
- A group whose representatives leave `J` (S18) is not couplable and stays uncoupled.
- `readingFor` finds the picked reading by its canonical candidate; a reading's aliases never enter a pick, a group
  or `couplable` (R-3). S18 and S19 are documents without a norm-defaults block; S22 is the case with one.

## 5. Diagnostics

Lean writes the text; Python prints it. `<o>` is an obligation id.

| Diagnostic | When |
|---|---|
| `PresuppositionUnknownRow: <o>: <row>` | the row is not `definite`, `plural` or `generic` |
| `PresuppositionPosition: <o>` | the path does not locate in the base content, the rule is not the unit's, or the path enters another obligation's restriction in the same unit (R-D6) |
| `PresuppositionMismatch: <o>: <field>` | `<field>` is `id` (duplicate), `unit` (missing), `arguments`, `body` (at a rule act or a heading), `clause` (the located subformula is not `strong`), `content` (the recorded content is not the regenerated one), `rule` (a recorded rule, or a tree that fails W1's check) |
| `PresuppositionCertificate: <o>` | no certificate, or it fails against `premisesBefore` (a certificate citing the unit itself or a later one fails here) |
| `PresuppositionAssumedUnit: <o>: <unit>` | the assumed or unconditional unit is missing, not asserted, or has another content; or, at a path or a rule act, it is the obligation's own unit (R-D5) |
| `PresuppositionDefault: <o>: <predicate>` | a conditioned rule, or an unresolved rule obligation whose cell lists conditioned (R-7), whose predicate has an allow or deny default |
| `PresuppositionUnresolved: <o>` | an unresolved obligation on a unit with one content |
| `PresuppositionCandidates: <o>` | readings not exactly the emitted candidates, or fewer than two (R-D3); a recorded carrier not in the cell; a recorded in place at a frame that is not shallow (R-D1); a heading carrier other than proved and assumed (R-10); a second unresolved obligation in one unit |
| `ResourceLimit: presuppositions` | over budget: UNKNOWN, never a rejection |

`PresuppositionRefuted: <o>: <unit>` is a report line, not a diagnostic.

## 6. Table and template formats

**Candidate table** (PS-E1's output, read by PS-2a and PS-6): one JSON object per row,

```json
{"row": "plural", "cells": {"top": ["assumed", "conditioned"], "negated": [], "antecedent": [],
                            "consequent": [], "disjunct": [], "rule_act": ["assumed", "conditioned"],
                            "rule_guard": []}}
```

with candidate names `assumed`, `conditioned`, `asserted`, `in_place`, `unconditional`, in the measured order (the
share of answers, highest first; ties in this list's order). A generator writes the Lean `candidateTable` from it;
`tableOk` must hold, and a table that fails it is a PS-E1 analysis error. The values above are placeholders, not
measurements.

**PS-E1's preregistration** (R-12). Before any model call, a committed file,
`docs/research/presupposition-E1-prereg.md`, fixes:
1. the mapping of PS-E1's seven trigger classes to the three row names;
2. the aggregation rule that turns the items of the classes mapped to one row into that row's cell;
3. the rule for classes of one row that disagree on a cell;
4. the ordering rule: share of answers, highest first, ties in the list order above;
5. the per-item frame and denotation table: for each item, its frame, whether the frame is shallow, and the values
   of asserted, conditioned and in place in the item's failing situation, computed by the stub's `#guard`s;
6. the equivalent-option rule of R-D4 (2.5): (b) and (e) count as one class only for an item whose row in item 5
   shows in place and conditioned with the same value.

The generator that writes `candidateTable` reads this file and PS-E1's answers, and `tableOk` must hold on its
output. This draft fixes what the file must contain, not its values.

**English templates** (filled after PS-E2): per row, a `pre` template with the slots `{t}` (possessor) and `{N}` (the
noun), and per candidate the reader line and the rewrite of 2.3 and 2.4, with `{goal}`, `{pre}` and `{sentence}`.

## 7. Acceptance fixtures

### 7.1 Formula-level fixtures (PS-1 `Examples.lean`; computed by the stub's `#guard`s)

Values were derived by hand for this draft; the stub's `#guard`s compute them. Models are finite: `entity` holds the
listed elements, and only the listed tuples are true. "The owner" is `definite 0 entity owner ready`; `U` its `pre`.

| Id | Fixture | Models | Expected (in model order) |
|---|---|---|---|
| S1, S13 | "The owner is ready." | none: no owner; one: `a` owner, ready; one-unready; two-one-unready: `a`, `b` owners, `a` ready; two-ready | asserted `U ∧ strong`: F T F F F. Conditioned `U → strong`: T T F T T. Weak in two-one-unready: F (draft 1's conditioned) |
| S1 (definedness) | `strong ↔ U ∧ weak` | one / none / one-unready | true with both sides true / false through `U` / false through weak |
| S2 (R-14) | "If Alice has exactly one manager, then her manager is ready." (`definite`, `D = manager_of(x, alice)`, path `[1]`) | Alice with no manager; one ready manager; two managers | frame `impR U hole`; goal `U → U`: T T T (proved by a one-step certificate; `collapse_certified`; one reading) |
| S4 (R-14) | "Alice has no manager, or her manager is ready." (`plural`, path `[1]`) | no manager; one ready manager | frame `orR (¬∃m D) hole`; goal `¬¬∃m D → ∃m D`: T T (proved). M1's goal `¬∃m D → ∃m D`: F in "no manager" |
| S5 (R-14) | (a) "Every person who has a manager trusts their manager."; (b) "Every person trusts their manager."; (c) "Some person trusts their manager." (`plural`, `D = manager_of(m, x)`, `P = trusts(x, m)`) | `p1` a person with manager `m`, trusting `m`; `p2` a person with no manager | (a) goal `∀x ((person x ∧ ∃m D) → ∃m D)`: T (the restrictor proves it). (b) goal `∀x (person x → ∃m D)`: F, unresolved. (c) the frame crosses `ex`, and the goal closes universally: the goal of (b), F, while the sentence is T (through `p1`) |
| S9 (R-14) | "Her manager is ready, and Alice has exactly one manager." (path `[0]`) | no manager | frame `andL hole U`; goal `U`, not `U → U`: the right conjunct does not filter (incremental local context). F: unresolved |
| S12 | "The owner is not ready." (frame `not ·`, shallow) | none, one, one-unready, two-one-unready | asserted F F T F; conditioned T F T T; in place T F T T: one column (R-D2). Under the fixture table's negated cell `[assumed, conditioned, inPlace]`, `expectedReadings` has two readings, assumed and conditioned with aliases `[inPlace]`, and none whose candidate is in place (R-4). Draft 1 at none: asserted (`¬strong`) T, conditioned (`¬weak`) F. Collapse: one, both F; one-unready, both T |
| S25 (R-4) | "It is not so that the owner is not ready." (frame `not (not ·)`, class negated, not shallow) | none | in place `¬¬strong`: F; conditioned `U → ¬¬strong`: T (`pre` false). `expectedReadings` emits no in-place reading and the conditioned reading has no alias; `carrierAllowed` refuses a recorded in place |
| S26 (R-4) | two `generic` triggers: `q = p ∧ ⊤`, `B = ¬¬(q ∧ ⊤)`; the outer at `[0, 0]` (`pre` `q`, body `⊤`), unresolved, goal `q`; the inner at `[0, 0, 0]` (`pre` `p`, body `⊤`), conditioned, goal `p` | `p` false | the outer's readings with the inner conditioned: in place `p → B`: T; asserted `q ∧ (p → B)`: F; assumed: content `p → B`, premise `q`: F, so no model with `p` false. The emitted readings exclude in place, and no reading has an alias |
| S27 (R-4) | frames `not (· and r)`, `not (· or r)` and `(not ·) and r` (class negated, not shallow) | — | `expectedReadings` emits no in-place reading and no alias; `carrierAllowed … inPlace` is false, so a recorded in place is `PresuppositionCandidates` (A23) |
| S21 | "If the shop is open, then the owner is ready." | open, no owner; closed; open, one ready owner | goal `open → U`: F T T. Asserted F T T. Conditioned T T T |
| S16 | "The owner is ready, or the manager is busy." (owner asserted, manager conditioned) | neither; one ready owner; one unready owner, no manager; an unready owner and an idle manager | `carried`: F T T F. The opposite nesting `G_manager → (U_owner ∧ B)`: T in "neither". In the third model the manager's goal fails and the unit is exactly the owner's goal (T) |
| S15 | two units, one goal: assumed and conditioned | none, one (ready, idle), one (ready, busy), two-ready | mixed `[B₁, U, U → B₂]` and uniform `[B₁, U, B₂, U]`: both F F T F |
| S14 | rule on `answer_required(agent, situation)`; `pre` = "a request in that situation addressed to that agent" | agents `ag1`, `ag2`; situation `s1`; request `q` in `s1` addressed to `ag1` | S14a (guard = `pre`): goal T; `decides` original = conditioned at (ag1, s1): T = T, at (ag2, s1): F = F. S14b (guard without the addressee): goal F; at (ag2, s1) original T, conditioned F. M3 (binders from `over`): goal T, wrongly |
| S8 | `resides_in` total and functional; "the State wherein Alice resides" | Alice in one state; Alice in two | flags T and `U` T; functional F and `U` F |
| S20 | a rule act with `body` | — | `buildPre` gives `body`; without `body`, `.ex entity D` |
| S17 | `premisesBefore` of the second of three units | background `⊤` | `[⊤, <first unit's claim>]`: the unit itself and the third are excluded |
| S19 | "the user" in 5 rules: identical goals; different goals | candidates {assumed, conditioned}, no constraints | identical: 32 picks, 1 group, couplable, 2 coupled picks. Different: 0 groups, 32 picks |
| S18 | 2 obligations, one goal, a constraint that excludes both uniform pairs | `J` = the two mixed picks | not couplable; the representative of the first is the all-assumed pick, outside `J` |
| S22 (R-9) | a document with `norm-defaults@0`: `p(situation)` `unspecified`; two rules on `p` with guard `g(s)`, each with "the operator’s instructions" unresolved in its act (one goal, candidates {assumed, conditioned}) | situations `s1`, `s2`; `g(s1)`; one instruction; `p(s1)` and `p(s2)` true (no rule decides at `s2`) | for the mixed pick (assumed, conditioned) and its representative (assumed, assumed): `SatUnder` holds in the model for both (`unsaid` at `s2`), and `SameModels` holds there. W1's raw `Sat (formulas ++ elaborate)` fails for both at `p(s2)` (the placeholder `deny`). A PS-3 `example`, since `value3` is noncomputable; the raw side is a `#guard` |
| S23 (R-10) | heading p2 (3): `plural`, `D = core_value_of(x, claude)`, no body | — | `buildPre "plural" 0` gives `∃x:entity core_value_of(x, claude)`, which is the heading unit's content (PS-0p's audit rule); with a body, the error is `body` |
| S24 (R-14) | open descriptions: "Every situation's operator is ready." (`∀s:situation`, `definite 1 entity (operator_of(x, s)) ready`) | one each (`a` operates `s1`, `b` operates `s2`); `s1` has two (`a`, `b`), `s2` has one (`c`); `a` ready | `∀s U(s)`: T, F. `DefinedAt` at `[s1]` and `[s2]`: true in both models. Without `raise1` (`uniqueAt entity D D`): T, T: the inner `D` reads the outer entity where the situation should be |
| expected | `expectedReadings` length | S1 under a table whose top cell is `[conditioned]`; under the fixture table | 1 (refused: fewer than two, R-D3); 2 |
| table | `tableOk` | the fixture table; the empty table; `[asserted]` everywhere; `[assumed, asserted]` everywhere; `[inPlace]` alone in the negated cell; `[conditioned, inPlace]` in the negated cell | T, T, F, F, F (R-2), T |
| 4.1 | builders | — | `definite 0`'s `pre` and `strong` are discourse's `uniqueD` and `assertive`; `raise1 1` maps var 1 to var 2; `raise1 0` is the identity on the sample |
| 4.2 | `locate`, `cls` | — | `[0]` under `not`, `[1]` under `or`; `[2]` into `ex` is none; classes negated, consequent (through a quantifier and a conjunct), disjunct |

### 7.2 Every "exactly when" claim, both directions

| Claim | Holds (true side) | Fails (false side) |
|---|---|---|
| `goal_denote` | S21 closed (nothing reached), open with a ready owner (every reached valuation has `U`) | S21 open, no owner (a reached valuation fails `U`) |
| `plug_congr`, `collapse` | S12 one-unready: both plugs true | S12 one: both plugs false |
| `DefinedAt` (definite) | one: strong, `U`, weak all true | none: strong and `U` false; one-unready: strong and weak false |
| `carriers_on_goal` | S1 one: asserted = conditioned = weak = T | S12 one: asserted = conditioned = in place = weak-plug = F |
| `condition_applies` | S14b at (ag1, s1): applies and `pre` both true, conditioned applies | S14b at (ag2, s1): `pre` false, conditioned does not apply |
| `rule_collapse_decides` | S14a at (ag1, s1): both decide | S14a at (ag2, s1): neither decides. S14b at (ag2, s1) shows the hypothesis is needed |
| `carried_denote` | S16 one ready owner: T | S16 neither (an asserted goal fails); S16 unready owner, idle manager (goals hold, `B` fails) |
| `carried_conditioned_off` | S16 unready owner, no manager: unit T = owner's goal T | S16 neither: unit F = owner's goal F |
| `carried_on_goals` | S16 one ready owner: unit T = `B` T | S16 unready owner, idle manager: unit F = `B` F |
| `unsaid_iff` | S7 (document): no rule decides, UNDECIDED | S7b (document): another rule decides, decided (`value3` is noncomputable, so these are PS-2b documents) |
| `tableOk` | the fixture table, the empty table, `[conditioned, inPlace]` negated | `[asserted]` at a rule act; `[assumed, asserted]`; `[inPlace]` alone (R-2) |
| `inPlace_iff_conditioned_shallow`, `admit_inPlace_alias` | S12 (shallow): in place and conditioned T F T T alike | S25 (`not (not ·)`, not shallow): in place F, conditioned T; S26: the whole-unit in place T, asserted F |
| in place only at a shallow frame (`carrierAllowed`, `admit_carrier_candidate`) | A22: recorded in place at `not ·` | A23: recorded in place at `not (· and r)` |
| `couplable` | S19 identical goals | S18 |
| readings exactly the emitted candidates, at least two (`admit_unresolved_readings`) | A1 | A2 (one missing); A21 (one candidate) |
| `admit_conditioned_rule_unspecified` | A4 (conditioned, `unspecified`) | A5 (conditioned, allow); A5u-allow, A5u-deny (unresolved, cell lists conditioned) |
| `admit_assumed_sound`'s own-unit clause | A24: a heading assumed on its own unit | A20: a path obligation assumed on its own unit |
| `admit_outside_restrictions` | A18b: a path into the body `P` | A18: a path into the restriction `D` |
| `SameModels` under the completion | S22: `SatUnder` holds for both picks | S22's raw W1 form fails for both (the placeholder `deny`) |
| `no_block_unchanged` | S11: every discourse@1 answer byte-identical | — (an equality; A14 shows a block changes the answer) |

### 7.3 Admission fixtures (PS-2a in Lean, PS-2b as documents)

One fixture per accept rule and per diagnostic. The fixture table of the stub stands in for PS-E1's.

| Id | Document | Expected |
|---|---|---|
| A1 | S1 with an open set {assumed, conditioned} in the cell's order | admitted; two readings, separated by the no-owner situation |
| A2 | A1 with the conditioned reading missing | `PresuppositionCandidates: p1` |
| A3 | S1 unresolved on a unit with one content | `PresuppositionUnresolved: p1` |
| A4 | S7 conditioned, predicate `unspecified` | admitted; at a situation without instructions, UNDECIDED when no other rule decides |
| A5 | S7d: S7 with an allow-by-default predicate | `PresuppositionDefault: p1: <predicate>` |
| A5u-allow (R-7) | S7 unresolved, cell {assumed, conditioned}, allow-by-default predicate | `PresuppositionDefault: p1: <predicate>` |
| A5u-deny (R-7) | S7 unresolved, cell {assumed, conditioned}, deny-by-default predicate | `PresuppositionDefault: p1: <predicate>` |
| A6 | S20: a rule act with `body` | `PresuppositionMismatch: p1: body` |
| A7 | S17: proved, the certificate cites its own unit or the later "There is exactly one owner." | `PresuppositionCertificate: p1` |
| A8 | S10: the same unit after "Alice has exactly one manager." | admitted, proved |
| A9 | assumed carrier whose unit states `pre` without the projected hypothesis (S21: "There is exactly one owner." where the goal is "If the shop is open, there is exactly one owner") | `PresuppositionAssumedUnit: p1: <unit>` |
| A10 | conditioned recorded as `B → G` instead of `G → B` | `PresuppositionMismatch: p1: content` |
| A11 | S16 with the two root goals recorded in the opposite nesting | `PresuppositionMismatch: p1: content` |
| A12 | row `"title"` | `PresuppositionUnknownRow: p1: title` |
| A13 | path `[2]` into an `ex` | `PresuppositionPosition: p1` |
| A14 | a recorded asserted carrier in a cell without asserted | `PresuppositionCandidates: p1` |
| A15 | 257 obligations | `ResourceLimit: presuppositions` (UNKNOWN) |
| A16 | S14 conditioned, the recorded guard `g ∧ pre` with `pre` written over the wrong variable order | `PresuppositionMismatch: p1: rule` |
| A17 | S11: no block | byte-identical to today's answers |
| A18 (R-D6) | "The manager of the owner is ready.": p1 the outer `definite`, whose restriction holds p2, the inner `definite` ("the owner"); p2's path starts with p1's path and `[0, 0]` | `PresuppositionPosition: p2`; the same with p2 in the copy at `[0, 1, 0, 0, 0]` |
| A18b (R-D6) | "The owner trusts the manager.": p2 ("the manager") in the body `P` of p1 ("the owner"), at p1's path and `[0, 1, 1]` | admitted |
| A19 (R-10) | a heading obligation with a conditioned carrier | `PresuppositionCandidates: p1` |
| A20 (R-D5) | S1 with an assumed carrier that names its own unit (a path obligation) | `PresuppositionAssumedUnit: p1: <unit>` |
| A21 (R-6) | S1 unresolved under a table whose top cell is `[conditioned]` | `PresuppositionCandidates: p1` |
| A22 (R-D1) | S12 with a recorded in-place carrier, the negated cell listing in place | admitted; the content is `B` |
| A23 (R-D1) | a recorded in-place carrier at `not (· and r)`, the negated cell listing in place | `PresuppositionCandidates: p1` |
| A24 (R-10) | p2 of section 3: a heading assumed on its own unit, whose content is `pre` | admitted; P1's unit is CHECKED as an assumption |
| A25 (R-10) | A24 with the unit's content `pre` conjoined with one more atom, `∃x:entity (core_value_of(x, claude) ∧ desired(x))` (draft 2 wrote it in English as "Some entity is a core value of Claude, and it is desired.", which VE does not parse; the fixture is on formulas) | `PresuppositionAssumedUnit: p2: u0013.presupposition` (PS-0p's audit rule, checked by Lean) |
| A26 (R-8) | S7 unresolved {assumed, conditioned}, predicate `unspecified`, on the soft chain | readings@1's abstention: `UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented` |
| A27 (R-8) | A26 on the rights chain | the same abstention |
| A28 (R-10) | a heading obligation with a `body` | `PresuppositionMismatch: p1: body` |

### 7.4 Pilot fixtures

P1 to P13 are the plan's (5.2), with its draft 2 and draft 3 corrections:
- **P1 to P4 are heading obligations** (R-10): position `{"heading": {}}`, no `body`, carrier assumed on the
  heading's own unit, whose content must be exactly `pre` (A24, A25). P1: `plural`, `core_value_of(x, claude)`; P2:
  `plural`, `guideline_of(x, anthropic)`; P3: `generic`, `pre` = `∃x open_problem(x)`; P4: `definite`, whose `pre` is
  the uniqueness `uniqueD` (`buildPre "definite" 0`). Each is admitted, and its unit is CHECKED as an assumption.
  Draft 1's form (path `[]`, body `⊤`, the obligation's own unit) failed the check: the unit's content had to equal
  both `strong` and `G`.
- **Their English, measured in phase 1** (Ph1 2.2–2.5; draft 3). The formulas are unchanged, and VE's renderer and
  parser round-trip all five exactly (Ph1 2.3). In the pilot document: the sort `entity`'s noun is "thing"/"things";
  P3's `open_problem` is worded "{0} is unsolved" and its unit is "Some thing is unsolved." (loads, CHECKED +29 B, 8
  of 8 choices conflict-free, probes byte-identical; Ph1 2.5); P1, P2 and P4 have no admitted wording until PS-6r and
  stay UNFORMALISED with the note "waits for the relational-noun wording (PS-6r)"; P4's English is the enumerated
  uniqueness form (1.4a), not the plan's one-line shape ("Some thing is a mission of Anthropic, and every thing that
  is a mission of Anthropic is that thing."), whose unary stand-in phase 1 found refused. The Lean fixtures of PS-1 use the formulas; their English column waits for PS-6r.
- P2 no longer proves u0073.s05 (strictly earlier units).
- P6 and P11's conditioned carriers need `unspecified` predicates, and their open sets are therefore on the norms
  chain only (R-8).
- P7's bridging premise must be an earlier unit or the background.
- P8 is a goal fixture only (its trigger sits in a guard, 10, C2).
- **P12 is a projection fixture only; coupling deferred** (R-11): its obligations sit inside the nationality or
  residence reading set, another profile's open set, which presupposition@0 cannot address (8), and `Pick` cannot
  express that choice.

### 7.5 Seeded bugs

- **Lean (PS-1).** M1: `goal` for `orR` without `.not`; S4 and `plug_congr` fail. M3: `ruleGoal` binds `N.over`; S14's
  goal `#guard` flips. M4: `carried` puts the conditioned goals outside the asserted ones; S16's first `#guard` fails.
- **Lean (PS-2a).** M2: proved accepted without the certificate check; A7 is admitted and its test fails.
- **Python (PS-2b).** The relay accepts an obligation id that is not in the request; a fuzz test fails.

### 7.6 Authoring fixtures (PS-6, under `refused_have_rewrites`; R-13)

| Id | Sentence | Expected |
|---|---|---|
| E1 | "It is not so that both of these are so: there is exactly one owner, and that owner is ready." | one reading, `¬assertive` |
| E2 | "If the shop is open, then both of these are so: there is exactly one owner, and that owner is ready." | one reading, `(open → U) ∧ (open → assertive)` |

Each is a rewrite that PS-6 offers; each must parse to exactly one reading.

## 8. Limits

- **The translation boundary.** Lean cannot see a trigger in free English. A trigger's presence, its row and, for a
  rule act, the link between the restriction and the act are the translator's claim, checked by the audit.
- **Positions.** presupposition@0 addresses content paths and rule acts. A trigger in a rule's guard, under a modal or
  an attitude, or inside reported content has no position: the unit stays UNFORMALISED in translation, and authoring
  refuses with advice. Reported content is a plug owned by attribution.
- **One open obligation per unit.** A unit with two unresolved triggers stays UNFORMALISED until a later version.
- **Units in another profile's open set** (a scope or act-phrase reading set) have no single base content, so their
  obligations are not addressable in presupposition@0. P12's coupling with the nationality or residence set is
  deferred for this reason (R-11).
- **In place at a nested frame is deferred** (R-D1). In place is offered only at a shallow frame, as the conditioned
  reading's alias. At every other frame, including other frames of class negated or antecedent, it is neither a
  reading nor an admitted carrier, though it may be a distinct reading there (S25, S26).
- **A trigger in a restriction** (R-D6). A trigger inside another trigger's restriction `D` is refused with
  `PresuppositionPosition`: `D` appears twice in a definite's or plural's `strong`, and presupposition@0 has no rule
  for which copy an obligation addresses. A trigger in the body `P` is addressable.
- **Too few readings or failed separation** (R-D3). An open set needs at least two readings after merging
  (`PresuppositionCandidates` otherwise), and readings@1's separation decides the rest (its own diagnostic). In
  translation such a unit stays UNFORMALISED.
- **Chains** (R-8). An open set with a conditioned rule reading needs `norm-defaults@0`, so it is admitted on the
  norms chain only; on the soft and rights chains readings@1's `abstention` refuses it.
- **Proxy readers.** PS-E1 and PS-E2 use Sonnet as a proxy; the results bound careful readers from above and say
  nothing certain about untrained human readers.
- **The table starts empty.** Until PS-E1 runs, every unproved trigger is refused in authoring and UNFORMALISED in
  translation (`admit_empty_table`).
- **Validity of trees** is a computed check (W1's `validate` on both trees), not a theorem about conditioning.
- **Budgets.** Over 256 obligations, or over W1's AST budget, or over lf-14d's joint budget, the answer is UNKNOWN.
- **Untrusted certificates.** A certificate may come from any prover; Lean only checks it.
- **Relational-noun English** (Ph1 2.5). Until the plan's PS-6r, VE English has no admitted wording for "t has at
  least one N" or "t has exactly one N" over a relational noun, so a `pre` over one cannot be written as a fenced
  unit. The formulas and every check above are unaffected; only the pilot's English and the reader lines of 2.3 wait.
- **The quoted fallback** (Ph1 2.3). VE's renderer falls back to quoted identifiers ("has the recorded relation …",
  "is classified as …") for a predicate without an admitted wording. Such text loads and checks, but it is not VE
  English; no claim is written in it (C20).

## 9. Review checklist (PS-S)

1. `goal`'s `exF` case closes universally (S5's restrictor proof, `goal_denote`).
2. Incremental, not symmetric, local contexts (S9).
3. The generalised builders: `uniqueD` and `assertive` stay `rfl`-equal; `raise1` through `VE.Norms.inst`.
4. Root carriers and `carried` against S12, S13 and S16.
5. `rule_collapse_typed`'s binders and `conditionRule` against S14 and M3.
6. `premisesBefore` against S17 and A7.
7. `coupling_complete`'s conditions against S18 and S19, and `SameModels` under the completion against S22.
8. The choices of section 10.
9. The stub run, in a checkout whose Lean modules are built: every statement elaborates and every `#guard` passes,
   including S2, S4, S5, S9, the open-description fixtures (S24) and the fixtures of R-2, R-4, R-6, R-7, R-8,
   R-9, R-10 and R-D5.
10. Draft 2's edits (the bounded re-check): in place and its alias (1.4, 1.8, 2.3, 2.4, 2.5, 4.3, 4.7) against S12,
    S25, S26, S27, A22 and A23; headings (1.4a, 3, 4.7) against S23, A24, A25 and A28; the admission changes (R-D5,
    R-D6, R-6, R-7) against A5u, A18, A20 and A21; separation, chains and coupling semantics (R-8, R-9) against
    A26, A27 and S22; the paraphrases (R-13) against E1 and E2.
11. Draft 3 (phase 1, PS-C9): every `lean` block is byte-identical to draft 2's, so items 1–10 stand; the re-check
    reads 1.4a, 2.1, 2.3, 7.4, 8 and C19–C22 only.

## 10. Choices this draft made, and questions for the review

- **C1. Position classes.** The plan lists top, negated, antecedent, consequent, rule act, rule guard, modal,
  attitude and reported. VE's formulas have no modal, attitude or reported constructor, so presupposition@0 has no
  frame for them; this draft drops them and adds `disjunct` (a hole under "or" first), which PS-E1 does not measure,
  so its cell is empty. `cls` takes the first operator from the root that is not "and" or a quantifier.
- **C2. Rule guards.** The plan's wire has no address for a trigger inside a guard, so `ruleGuard` is for authoring
  only, and P8 is a goal fixture, not an admission one. A later version can add `{"rule_guard": name, "path": …}`.
- **C3. Assumed and asserted never share a cell.** They have the same models (`G` as a premise with `B`, against
  `G ∧ B`), so readings@1 could not separate them. If PS-E1 puts both above the bar, this draft proposes that the cell
  lists `assumed` (the presupposition stays visible as "Assumed: …"), and that PS-E2 tests the asserted wording as its
  paraphrase. **Question Q1:** assumed, asserted, or a merged reading with two wordings?
- **C4. A recorded carrier must be a candidate.** A translator's single carrier other than proved is a narrowing of
  the cell's readings, so it must be one of them (`PresuppositionCandidates` otherwise).
- **C5. `premisesBefore`.** The background is W5 flags, literal distinctness and W3 definitions; rule elaborations are
  excluded even when earlier, since a rule's meaning is not evidence that something exists. **Question Q2:** should
  earlier rules' elaborations count?
- **C6. One open obligation per unit** (8).
- **C7. Recovering the base.** `B` is peeled from the recorded content by the canonical wrapper shape of `carried`;
  rule conditions are appended as left-nested conjunctions in block order. An author who writes an equivalent but
  differently shaped content gets `…: content`.
- **C8. `replaceNode` is `conditionRule`,** by name; tree validity is a computed check of both trees (8).
- **C9. The reading alternative.** In presupposition@0 a unit's only open set is its obligation's, so every
  obligation is in the root alternative, and "same alternative" in 1.9 always holds. It becomes a real condition when
  units inside other profiles' sets are addressable.
- **C10. Budgets.** 256 obligations and W1's 10,000-node AST budget are this draft's proposal.
- **C11. The representative's order** (assumed, then asserted, then conditioned) keeps every assumption: the
  representative is assumed exactly when some member was.
- **C12. Names.** `uniqueAt`, `assertiveAt`, `raise1`, `uniqueOpen` and `assertiveOpen` live in discourse's file;
  `conditionRule` replaces the plan's `replaceNode`; the plan's `assertedContent`, `conditionedContent` and
  `candidateContent` are `assertedAt`, `conditionedAt`, `claimReading` and `ruleReading`.

Draft 2's choices in applying the ruling:

- **C13. Where R-D2's theorem lives.** The ruling states `inPlace_iff_conditioned_shallow` in Reading.lean over
  `claimReading`, and keeps it in PS-1. `claimReading` is PS-2a's (it needs `Report` and `Checked`), and Reading.lean
  cannot import it. So Reading.lean states the theorem over `carried`, which is exactly `claimReading`'s content,
  with the other obligations' root modes as `ms₁` and `ms₂` and congruence through `carried` as `carried_idle`; and
  PS-2a states the same equivalence over `claimReading` for an admitted document (`admit_inPlace_alias`), with both
  premises `none`. The alias is attached exactly where `admit_inPlace_alias` applies (`aliasesOf`). Both are stated
  for every structure, admissible or not; the ruling's "every admissible structure" is the special case.
- **C14. `SameDecides` under R-9.** The ruling redefines `SameModels` and `SameDecides`'s satisfaction hypothesis by
  one case split. This draft uses one predicate, `SatUnder`, for both. Without a norm-defaults block,
  `SameDecides`'s hypothesis therefore gains W1's elaboration, which draft 1's form (`Sat` of the formulas alone)
  did not have; draft 1's form is a stronger statement and the same argument proves it. The re-check may keep the
  formulas-only hypothesis in the no-block case if it prefers the stronger statement.
- **C15. The document's norm-defaults block** is a field, `PDoc.defaults`, because R-8 and R-9 split on whether the
  block is present, and `unspec = []` does not say that (a block may default every predicate).
- **C16. A heading's `Checked`** has frame `.hole`, no reading and class `.top`; the class is never read, since a
  heading admits only proved and assumed and `admit_carrier_candidate` excludes headings.
- **C17. Restriction paths** (R-D6) cover the definite's two copies of `D` and the plural's two; a generic row has no
  restriction, and a trigger inside its `pre` or `body` is addressed as usual.
- **C18. The paraphrases** (R-13) use "both of these are so" to bracket a conjunction under "not" and under
  "if … then". PS-E2 and PS-6 test the wording; another bracketing that passes E1 and E2 may replace it.

Draft 3's choices in applying phase 1 and PS-C9:

- **C19. A heading's English is the audit's, its formula Lean's.** `admit_heading_goal` and `admit_assumed_sound`
  compare formulas; the fence's English is parsed by VE's own parser before Lean sees it. So "Some thing is
  unsolved." for "open problems" is admitted by Lean as `∃x open_problem(x)`, and whether "unsolved thing" is what
  "open problems" names is the audit's question (Ph1 2.5). No Lean statement changes.
- **C20. No claim in the quoted fallback.** It would let PS-0p claim +145 B today (Ph1 2.3), but it violates VE's
  "plain English, no symbols" rule, so the spec counts it as no English at all.
- **C21. The assumed line's wording** (2.3) is the target; PS-E2 tests PS-6r's rendered lines, or labels its items
  as target wording if PS-6r is late (plan PS-E2).
- **C22. A field, not a mode** (DRI PS-C9). 4.7's statements are over `admit`; where the report is carried changes
  no statement. `no_block_unchanged` covers the document mode's answer without the block.
