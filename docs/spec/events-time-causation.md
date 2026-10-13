# Events, time and causation (`events@0`, and `alternatives@0` with the completion): statement spec (ET-2)

> Status: item-1 statement spec, draft 2 (2026-10-13), branch `design/events-time-causation`. Draft 2 applies the
> converged statement review of draft 1 (`manage-agents/debates/events-time-causation-spec/{astra,fable}.md`,
> CONVERGED in round 3: **FIX**; build authorization pending). Its items are cited **SR-A1** to **SR-A4** (ET-7) and
> **SR-B1** to **SR-B5** (events), because 2.4 already names reading candidates A1, B1 and so on; SR-B3 includes
> Astra's round-3 hypothesis `hb` (literal distinctness of the situation). The regressions R-A2, R-A3 and R-A4 of
> Fable's round 3 are fixtures T12d, T12e and T12f. Section 12 lists the changes. Draft 1 was written from
> [events-time-causation-PLAN.md](events-time-causation-PLAN.md) draft 2, which applies the converged Astra + Fable
> review of the plan (`manage-agents/debates/design-events-time-causation/{astra,fable}.md`, CONVERGED in round 3:
> **REVISE now, BUILD after this spec's statement review**) and the DRI's cross-plan synthesis edits X1 to X10 (same
> files, last section). Debate items are cited as the plan cites them: **A** to **J**, **R1** to **R4**, **X1** to
> **X10**. This file is ET-2's deliverable: the plan's sections 2 and 3 as statements, with definitions, the one
> reading of every wording, the Lean statements, the diagnostics and the acceptance fixtures (definitions first,
> expectations after). Every "exactly when" claim has a fixture for each direction.
>
> **Elaboration: not yet run.** In the session that wrote draft 1 the harness refused to run `lake` and `lean`, and
> draft 2's worktree has no build, so no statement here has been elaborated. Every Lean block of section 6, and every
> fixture value marked *guarded*, is in the scratch stub `SpecStubs_events-time-causation.lean` (each
> `theorem T b : C` as `def T b : Prop := C`, with the same binders; definitions with the bodies stated here; fixture
> values as `#guard` lines; no `sorry`). The stub is not committed; 11 says where it is and the one command that
> elaborates it. Fixture values marked *guarded* were derived by reading the sources, and the day numbers were
> cross-checked with a Python transcription of `Civil.num` that agrees with the proved anchors `num_epoch` (0) and
> `num_lastDate` (2932896); the `#guard` lines are the check.
> Values marked *derived* are obligations of the batch named. Statements are implementation obligations, not claims
> of completed proofs. No model was called.
>
> Draft 2 also read, at `ac4a62f8`: `lean/VE/NormDefaults/Wire.lean` (`decodeSourceU`, `checkAuthor`),
> `lean/VE/NormDefaults/Evidence.lean` (`fillBody`, `admissible_of_fillValid`), `lean/VE/NormDefaults/Report.lean`
> (`admissibleX_of_fill`), `lean/VE/NormDefaults/Layered.lean` (`situationX`, `filledX`, `replayStatusX`),
> `lean/VE/Alternatives/{Followable,Replay,Validate}.lean` (`dilemma_witness_sound`, the wire theorems,
> `validateAlternatives`).
>
> Inputs, read at `892fe1fc` (`main` at `49de179e` plus the plan): `lean/VE/{Syntax,Semantics,Finite}.lean`,
> `lean/VE/Time/Calendar.lean`, `lean/VE/Norms/{Tree,Prefix,Subst,Conflict,SmallModel}.lean`,
> `lean/VE/NormDefaults/{Tree,Premises,Evidence,Status,Report,Layered,Routes,Wire,Examples}.lean`,
> `lean/VE/Alternatives/{Decl,Wire,Background}.lean`, `lean/VE/Compose/Dispatch.lean`, `lean/VE/Route/Wire.lean`,
> `ve/surface/time.py`, `rd-9/integrate` at `321e610a` (`lean/VE/NormDefaults/LayeredEntail.lean`),
> [norms.md](norms.md) 7, [norm-defaults.md](norm-defaults.md) 2.5, 3.3 and 9, and the eligibility answer key
> (`usecases/eligibility/PLAN.md` C25 to C27).
>
> The gate: ET-3 opens on the PASS of the statement review the DRI assigns (two frontier reviewers), after the
> elaboration run of 11 succeeds. PASS requires three things: the corrections of draft 2 are in (this file, the plan
> and the stub), both reviewers have re-read the changed statements and accept each statement as **true under its
> hypotheses**, and the corrected stub's elaboration is recorded with its command, its log and the reviewed commit;
> that the stub elaborates is necessary, not sufficient. Each reviewer derives the expectations of 8.1 before reading
> 8.2. The review may pass section 5 (ET-7) before the rest, once SR-A1 to SR-A4 and their fixtures (T12c to T12f)
> are in and the ET-7 part of the stub elaborates; ET-7 then starts.

## 0. Scope, one paragraph

A document with `events@0` has a **day sort** of whole civil days, a `before` order on it, **event sorts** whose
things happen on at most one day, **state sorts** whose things begin and end, **named dates** from 1970-01-01 to
9999-12-31 whose order Lean takes from W6a's calendar, an optional **date of this document**, and **causal links**
between events and states that the checker never decides. The block regenerates closed universal premises, which are
PK-1's `events` pack, the last pack of the layered route's extra premises `X` (X1); no checker, route or service mode
is added. The **day domain is fixed**: the intended reading has every civil day as a day. A certificate holds in every
structure of the premises, so in that reading. A finite witness or countermodel is reported only when the **calendar
completion theorem** (1.7) carries it to a situation with every civil day; otherwise the answer is UNKNOWN with
`NotCalendar` (A, X2). Source words such as "until" become reading sets per modality (R2); authored text uses explicit
wordings, checked with readers before they are written (R4). `alternatives@0` gains the completion with an evidence
contract (C). Out of scope: durations over events, deadlines, branching time, order within a day, dates before 1970,
`data@0` (triggers ET-T1 to ET-T4), and pruning the order premises (an option with its own theorem, 6.5).

In this spec: definitions (1), the English (2), wire and identity (3), diagnostics (4), the ET-7 evidence contract
(5), the Lean statements (6), what is not claimed (7), the acceptance fixtures (8), the review checklist (9), the
differences from the plan's blocks (10), the elaboration record (11), and draft 2's changes (12).

## 1. Definitions

### 1.1 Where this applies: the profile row (D12, H, X3)

`events@0` is one row of AR-10's profile-gate table: `requires`, `refuses` with its texts, and `slot`. Its fields:

| Field | Value |
|---|---|
| `requires` | `relational-fol@0`, `norms@0`, `norm-defaults@0`, checked in this order; a missing one is `UnsupportedProfile: events@0 requires <p>` |
| `refuses` | `alternatives@0`, `closure@0`, `data@0`, `nary@0`, `order@0`, `reports@0`, `risk@0`, `speech-acts@0`, `time@0`, checked after `requires`; the first refused profile in the (sorted) profile list is named: `UnsupportedProfile: events@0 with <p>` |
| `slot` | PK-1's `events` pack in the layered route's `X` (1.11) |
| admitted beside it | every other profile the layered route admits without `events@0` (`documents@1`, `soft-norms@0`, `rights@0`, the wrapper `readings@1`, and `definitions@0` exactly when the layered route admits it); `events@0` neither widens nor narrows the layered route's admissions except by the refusals above |

`data@0` is refused, not admitted (R1): admitting it needs a composition proof for a use case (agent-policy, R3) that
also needs order within a day, so R3 is the trigger ET-T4. The batch that adds the row (ET-4) proves the composition
theorem for the combinations it newly admits (6.3, `events_row_composition`, stated against AR-10's names); no gate
theorem is re-proved in `Dispatch.lean`, and Python reads AR-10's generated data, with no `ve/profiles.py` row and no
mirror (X3).

### 1.2 The block and its decoded form

The environment carries one block:

```json
"events": {
  "day": "day", "before": "before",
  "events": [{"sort": "act", "on": "committed_on"}, {"sort": "conviction", "on": "convicted_on"}],
  "states": [{"sort": "stay", "begins": "stay_begins", "ends": "stay_ends"}],
  "dates": ["2026-09-21", "2026-09-27"],
  "anchor": "2026-10-12",
  "links": [{"predicate": "contributed_to", "form": "contributed", "decided_by": "the drafters"}]
}
```

`day`, `before`, `events`, `states`, `dates` and `links` are required (empty lists allowed); `anchor` is optional; any
other field is `InvalidInput: events.<field>`. The vocabulary declares every sort and predicate the block names; the
block adds none. Lean decodes it to:

```lean
structure EventSort where
  sort : String
  on : String              -- base predicate (sort, day)

structure StateSort where
  sort : String
  begins : String          -- (sort, day)
  ends : String            -- (sort, day)

inductive LinkForm where
  | contributed            -- "{0} contributed to {1}"
  | necessary              -- "{0} was necessary for {1}"

structure Link where
  predicate : String       -- base predicate (cause, effect); an open term
  form : LinkForm
  cause : String           -- the predicate's first sort, an event or state sort
  effect : String          -- its second sort, an event or state sort
  decidedBy : Option String   -- none is "unstated"

structure EventsEnv where
  day : String
  before : String
  events : List EventSort
  states : List StateSort
  dates : List Civil       -- parsed, valid, sorted by `Civil.num`, unique, the anchor included
  anchor : Option Civil
  links : List Link
```

The decoder parses each date and the anchor with `VE.Time.parseIso` (one calendar, one date grammar), adds the anchor
to the dates (a date equal to the anchor is the same date, not a duplicate), sorts by `Civil.num`, and rejects
duplicates; nothing is removed silently. `WellFormedEvents E V` (6.1) is the typing part of the checks, against the
author's environment `E`; `regenEnv E V` adds one constant `dateName D` of the day sort per named date; `EventsTyped`
is what every later statement assumes of the regenerated environment, and `regen_typed` says the first gives the
second. The verbalisation checks, which need the vocabulary's JSON, are the decoder's (4, items 3 to 5):
`before` reads exactly "{0} is before {1}", each role reads "{0} <verb phrase> on {1}" (`roleWordingOk`, R3), and
each link reads its form's fixed wording.

### 1.3 Named dates and the anchor

A named date `D` is the constant `dateName D` = `date__YYYY_MM_DD` of the day sort (`date__2026_10_12`). `date__` is a
reserved prefix, registered in PK-1's `reservedPrefixes` (X1): no declared name may start with it. The constant's
verbalisation is its ISO form (`Civil.iso`); W6's date-literal class reads both "2026-10-12" and "12 October 2026"
and renders the long form, so events adds no month table and no date code (one owner: today `ve/surface/time.py`,
english-lean's catalogue when the class moves there). The anchor's constant has the fixed verbalisation "the date of
this document"; its ISO and long forms read as the same constant through the literal class. The anchor is the one
indexical day for every plan; quantities' QT-0p "at the moment" refers to it once `events@0` lands (X9). Dates run
from 1970-01-01 (`Civil.num` 0) to 9999-12-31 (`dateMax` = 2932896); a date before 1970 is `parseIso`'s
`DateRange(<iso>)`, a stated limit until ET-T3 fires (G, X8). At most 64 named dates (`maxDates`), anchor included.

### 1.4 The generated premises and their labels

In this order, one label each (6.1 gives the formulas):

| Label | Formula | When |
|---|---|---|
| `events:irreflexive` | `∀t. ¬ before(t, t)` | always |
| `events:transitive` | `∀t u v. before(t, u) ∧ before(u, v) → before(t, v)` | always |
| `events:linear` | `∀t u. before(t, u) ∨ t = u ∨ before(u, t)` | always |
| `events:date:<D>:<D'>` | `before(c_D, c_D')` | each consecutive pair of named dates |
| `events:adjacent:<D>:<D'>` | `∀t. ¬ (before(c_D, t) ∧ before(t, c_D'))` | each consecutive pair with `D'.num = D.num + 1` |
| `events:one_day:<E>` | `∀x. ∀t. on_E(x, t) → ∀u. on_E(x, u) → t = u` | each event sort |
| `events:one_begin:<S>`, `events:one_end:<S>` | the same with `begins_S`, `ends_S` | each state sort |
| `events:not_before_begin:<S>` | `∀x. ∀t. begins_S(x, t) → ∀u. ends_S(x, u) → ¬ before(u, t)` | each state sort |
| `events:link_forward:<L>` | `∀x y. L(x, y) → ∀t. start(x, t) → ∀u. bound(y, u) → ¬ before(u, t)` | each link |
| `events:link_weaker:<N>:<C>` | `∀x y. N(x, y) → C(x, y)` | each `necessary` link N and `contributed` link C on the same sort pair |

`<D>` is the ISO date; `start` is the cause sort's `on` (event) or `begins` (state); `bound` is the effect sort's `on`
(event) or `ends` (state). The first five rows are the **calendar premises** (`calendarPremises`), true in every
calendar reading (`calendar_sat`). The rest are the **conventions** (`conventionPremises`), each written with every
day quantifier guarded by a role atom, so the completion theorem covers them (`conventions_exact`). All are closed,
universal and function-free. Existence facts (an event's day, a state's beginning) are validated on situations, never
assumed: a situation in which a stated event has no day is accepted, and the report says the fact is missing where a
wording needed it.

### 1.5 Calendar readings: the day domain is fixed (A)

`Embeds V S num` says `num` numbers the days of `S` as civil days: one-to-one on days, at most `dateMax`, `before`
on days is `<` on numbers, and each named date denotes a day with its date's number. A **calendar reading** is an
embedding onto every civil day: `CalendarReading V S num := Embeds V S num ∧ ∀ n ≤ dateMax, ∃ day x, num x = n`.
This is the intended reading: its days are exactly the civil days `0..dateMax`. A finite situation is at most an
embedding (one-to-one, never onto); draft 1's `CalendarReading` lacked `onto`, which is why it could not justify a
refutation (the plan's A).

### 1.6 The calendar check and the numbering

`calendarCheck V M` (6.1) decides, on a finite situation `M`, in this order, and returns the first failure's text:

1. `before` restricted to the day domain is a strict linear order, and the day list has no repeat;
2. each named date denotes a day;
3. the named days are in date order;
4. sorting the days by `before`, the days below the first named date `D₁` number at most `D₁.num`; the days strictly
   between consecutive named dates `D < D'` number at most `D'.num − D.num − 1`; the days above the last named date
   `Dk` number at most `dateMax − Dk.num`; with no named date, there are at most `dateMax + 1` days.

`embeddable V M := (calendarCheck V M).isNone`. `numbering V M` gives a named day its date's number and an unnamed
day the number of the last named day below it plus the rank difference (below the first named day: that day's number
minus the difference; with no named date: its rank). **`embeddable V M` holds exactly when some numbering embeds
`M`** (`embeddable_sound` with `numbering`, and `embeddable_complete`); fixtures T3 and T3e give both directions.
`embeddable_sound` assumes no calendar premise of `M`: the check gives them (step 1 the order, step 3 the date facts,
step 4 with a gap of 0 the adjacency), so a caller that knows only the base, as SETTLED's, can use it (SR-B2).

### 1.7 The calendar completion and its fragment (A, X2)

**The completion.** `completion V M num` is `M` plus one **added day** for each civil day number `0..dateMax` that
`num` leaves unused. Its carrier is `α ⊕ Nat` (old elements `inl x`, added days `inr n`); an added day belongs to the
day sort only; constants are `M`'s; a tuple of old elements is in a relation exactly when it is in `M`; a tuple with
an added day is in no relation except `before`, where days are ordered by number. So the completion adds the missing
calendar days in the gaps and at both edges, with no facts except their order. `completion_reading`: it is a calendar
reading. `completion_extension`: it is a **day extension** of `M` (`DayExtension`, 6.1) in which only `before` has
tuples with added days.

**The fragment.** A day extension can change the value of a formula only through a day quantifier that reaches an
added day. Four Boolean functions on formulas, with `ng` the predicates whose tables may hold added days (`before`
and the unsaid tables), decide where that cannot matter:

- `hits ng k a`: `a` is false whenever variable `k` is an added day. True for an atom of a predicate not in `ng` with
  `k` as an argument, for `k = c` with `c` a constant, for a conjunction with one such conjunct, for a disjunction of
  two, for `∃s. a` when `a` hits `k + 1`, and for `¬ a` when `a` is vacuous at `k`.
- `vacuous ng k a`: `a` is true whenever variable `k` is an added day: an implication whose antecedent hits `k` or
  whose consequent is vacuous, `¬ a` with `a` hitting `k`, and the dual cases.
- `up day ng a`: if `a` is true in `M` at old elements, it is true in every day extension. A universal day
  quantifier needs its body vacuous at the new variable (it is **guarded**); an existential one needs nothing (its
  witness is old).
- `down day ng a`: if `a` is true in a day extension at old elements, it is true in `M`. An existential day
  quantifier needs its body to hit the new variable; a universal one needs nothing (a counterexample in `M` is old).

Negation swaps `up` and `down`; an implication needs `down` of its antecedent and `up` of its consequent for `up`, and
the reverse for `down`. **`dayExtension_transfer`** (6.2): in every day extension, `up` formulas stay true and `down`
formulas stay false (in the contrapositive form above), at every valuation of old elements. Atoms are exact because
old tuples are `M`'s.

**The filled completion (SR-B1).** A situation with a filling of its unsaid tables is completed by completing its
base and extending the filling: `completionFill` keeps the filling on tuples of old elements and takes
`canonicalFill` (true on the unsaid tables of permission members, false elsewhere) on every tuple with an added day;
`completed U V M F` is the completion with that filling, and it is the situation every situation-based answer
reports. Its days, order and constants are the completion's, and it is a day extension of the filled situation with
`ng = unguarded U V` (1.8). `Fill_T` cannot be tested as a whole: each of its premises quantifies over its pair's
tuples, a day among them, with no guard (`fillPremises` binds `[agent, day]`), so its `up` is false for every
day-indexed pair with an unspecified member. Only the **body** of each fill premise is tested with `up`: on tuples of
old elements the body transfers, and on tuples with an added day it holds pointwise because the canonical filling
answers "yes" to every permission member and "no" to every obligation member there, as in `canonical_fill_sat`
(`fillPremises_canonical_completion`, 6.3). Leaving the added-day tuples empty would not do: an added day before a
closure makes an obligation true by its rule while its unspecified permission member is false there, which breaks
`Fill_T`.

**In plain words.** A claim "there is a day such that …" that a situation refutes stays refuted when days are added
only if every such day must also satisfy a role, link or author atom that no added day satisfies; a claim "on each
day …" that a situation refutes stays refuted because the counterexample day is one of the situation's own. Order
atoms are never guards, and neither are predicates derived from the order: "is in progress on" and "between" can be
true of an added day (refinement 2 of round 3). Unsaid tables are never guards either, because a filling may extend
them to added days.

**Examples** (fixtures T3b, T3c, R1, *guarded* in the stub):

| Claim | Refuted in a situation | `down` | Reported |
|---|---|---|---|
| "there is a day such that that day is after 12 October 2026 and that day is before 14 October 2026" | with only 12 and 14 October | false | UNKNOWN, `NotCalendar` |
| "there is a day such that that day is after 12 October 2026" | whose last day is 12 October | false | UNKNOWN, `NotCalendar` |
| "there is an act and a day such that that act is committed on that day and that day is after 12 October 2026" | with no act | true | the countermodel, completed |
| "that stay is in progress on each day from 21 September 2026 through 27 September 2026" | where the stay ends on 26 September | true | the countermodel, completed |

### 1.8 Which answers need which polarity, and where R1 falls

Every situation-based answer on a document with `events@0`, on every route that admits the profile (weighing's zone
completions included, X2), is reported only when the situation is `embeddable` and the formulas its check reads pass
the polarity test of its kind; the situation reported is the filled completion `completed U V M F` (1.7). `ng` is
`unguarded U V` = `before` and the unsaid predicates. "Premises" are the base background, `Fill_T`, every other
pack's premises in the assembled `X`, the events conventions and, for a model check, each premise of `Γ`; rules and
definitions are read expanded (outcome substitution), so they are tested inside the formulas that use them. For
`up`, `Fill_T` is tested through the body of each of its premises (`fillBodies`, SR-B1); for `down`, as a whole. The
calendar premises are not tested: every calendar reading satisfies them.

| Answer | Premises | Queried formula | Lean |
|---|---|---|---|
| a countermodel or model (NOT ENTAILED, a readings NONE or SOME model, a scenario, a zone completion) | `up` | `down` if reported false, `up` if reported true | `modelSafe`, `events_model_calendar` |
| a CONFLICT witness, a `gaps: reachable` witness | `up` | the target: `up` | `witnessSafe`, `events_witness_calendar` |
| UNDECIDED (two fillings) | `up` | the outcome: `up` and `down` | `undecidedSafe`, `events_undecided_calendar` |
| SETTLED (`table3`, enumeration) | `up`; and the base background and `Fill_T`: `down` | the outcome: `up` and `down` | `settledSafe`, `events_settled_calendar` |

A failing test makes the answer UNKNOWN with `NotCalendar: <label> may change when the missing calendar days are
added` (4), naming the first failing formula in the order of the table's columns. A certificate is never suppressed:
certificates hold in every structure of the premises (`events_certificate_calendar`), so in every calendar reading.

**SETTLED needs a situation of the document (SR-B3).** `SettledAs` quantifies over the admissible fillings of the
situation and holds vacuously when there is none, and it reads neither the other packs' `X` nor the conventions. So
SETTLED is reported only on a situation whose base background holds (`backgroundValid`, which includes the
distinctness of declared literals), with a filling that passes `fillValid` and `extraValid` over the whole assembled
`X ++ eventsX V`, and with the `up` test above; `events_settled_calendar` then also gives an admissible filled
completion satisfying the whole `X`. A situation that violates a generated premise or another pack's premise is that
pack's `InvalidModel` (4), one whose literals coincide is `InvalidModel(literals)`, and a situation for which no
filling is validated is UNKNOWN, never SETTLED (T14).

**Where R1 falls: inside, for its refutations.** R1's claim is "that stay is in progress on each day from 21
September 2026 through 27 September 2026"; its premises are atoms (each stay's days) and the conventions. With the
answer key's complete case data every answer is a certificate (C25, C26, C27), which 1.8 never suppresses. When a case
states no end, a countermodel refutes the claim at one of the situation's own days, and "is in progress on" is `down`
(its existential quantifier over beginnings hits the variable through `begins`, and its negated existential over ends
is `up`), so that countermodel is reported. A countermodel to the claim's **negation** (a situation in which the stay
never ends) needs `up` of the claim, which is false (an added day inside the week is not guarded), so that answer is
UNKNOWN with `NotCalendar`: nothing in such a case says that the stay continues. The fixtures of 8 give the answers.

### 1.9 States and persistence (F)

"<state> is in progress on <day>" means: it has begun on or before that day and has not ended before that day
(`∃b. begins(x, b) ∧ ¬ before(t, b) ∧ ¬ ∃e. ends(x, e) ∧ before(e, t)`). "Ends on" is inclusive: a state is in
progress on its last day. Persistence is never assumed. A state with no stated end day is in progress on a later day
only in situations that give it no end; a certificate that it is in progress there needs a stated premise that it has
not ended, such as "there is no day such that that stay ends on that day" or "that stay does not end on any day before
28 September 2026", which the report lists with its support like any premise. A situation that gives a state no end
is shown as such ("in this situation the stay has no last day"); that is a fact of the situation, not a claim about
the source.

### 1.10 Causal links and their conventions (D)

A link is a base predicate between two event or state sorts, declared in the block with a form and a decider and
declared as a W2 open term with the same decider (`LinkNotOpen: <p>` otherwise). The route never decides a link: a
link atom is true in a situation only if the situation says so, and certificates use links only as stated. The
checker adds two premises, each an explicit convention printed in the legend: `link_forward` (the cause does not
start after the day of an effect that is an event, and does not start after the last day of an effect that is a
state, which binds only when that state ends) and `link_weaker` (a necessary condition contributed). A later event
may contribute to a state already in progress (T6). The report's `causal_links` lists each link predicate with its
form, sorts and decider, and each unit that states or denies a link with its support.

### 1.11 The pack (PK-1, X1, X2)

`eventsPack d` is PK-1's `Pack` with `id := "events"`, `kind := .constraint`, `decls :=` the named-date constants
(`(dateName D, [V.day])`, in PK-1's encoding of a constant), `labelled := eventsLabelled V` (1.4) and `origins :=` each
label and each date mapped to its request path in the block. PK-1 places it last (`soft, rights, weighing, attitudes,
scales, events`), so the assembled `X` is the other packs' `X` followed by `eventsX V`, which is how 6.3 states it.
An absent block gives no pack (`eventsX_absent`), and PK-1's rule that an absent pack contributes nothing does the
rest.

**Kind, with its condition.** The pack is `.constraint`: its premises constrain symbols the author declares
(`before`, roles, links), so it is not a fresh-vocabulary pack, and events claims no conservativity beyond
`events_conservative`, whose formulas mention no day, role, link or named date (`oldEnv`). A PK-1 chain lemma may count
the events pack as a conservative step only for formulas over `oldEnv E V`, by `events_conservative`, and a witness it
reports must also pass 1.8's test, by the completion theorem.

### 1.12 Completeness: membership of norms 7.1 is reported, not assumed (B)

Events claims no completeness of its own. Membership of norms 7.1 after outcome substitution and definition expansion
is the layered route's existing report line (`fragment_fill`, `VE.Norms.InFragment (fill U)`); a day-quantified
wording in a guard ("happens before", "is in progress on") makes it `false`. Outside 7.1 an answer comes from a
certificate or is UNKNOWN; inside it, a finite witness is still reported only under 1.8. CONFLICT-FREE needs a
certificate in every case (norms 7.2, binding decision 9.4).

## 2. English

Every wording below is registered with `profiles=("events@0",)` in english-lean's catalogue (X9) and rejected when
`events@0` is off. ET-E1 checks them with readers before ET-5 writes them (R4); a wording below its bar is reworded
here first. Model results are early evidence, not proof about human readers.

### 2.1 Role wordings (R3)

Each role predicate's verbalisation is the author's, of the form "{0} <verb phrase> on {1}" (`roleWordingOk`): "{0}
happens on {1}", "{0} is committed on {1}", "{0} begins on {1}", "{0} is dissolved on {1}". The role's meaning comes
from its place in the block (`on`, `begins`, `ends`), never from its words. Derived wordings reuse the verb phrase:
with "{0} is committed on {1}", "that act is committed before 12 October 2026".

### 2.2 Derived wordings, one reading each

| Wording | The one reading (the IDE's paraphrase) | Formal effect |
|---|---|---|
| `<event> <vp> on <day>` | the event happens on that day | `on_E(x, t)` |
| `<state> <begins-vp> on <day>` / `<state> <ends-vp> on <day>` | its first day / its last day (it is still in progress on its last day) | `begins_S(x, t)` / `ends_S(x, t)` |
| `<day> is before <day>` | strictly earlier: an earlier day, never the same day (E) | `before(t, u)` |
| `<day> is after <day>` | strictly later | `before(u, t)` |
| `<day> is no later than <day>` | earlier or the same day | `before(t, u) ∨ t = u` |
| `<day> is on or after <day>` | the same day or later | `before(u, t) ∨ t = u` |
| `each day from <day> through <day>` | every day from the first to the second, both included | `∀t. ¬ before(t, a) ∧ ¬ before(b, t) → …` |
| `<event> <vp> before <day>` (also `no later than`, `after`, `on or after`) | the event happens, on a day so placed | `∃u. on_E(x, u) ∧ …` |
| `<event> <vp> before <event>` (also `no later than`, `after`, `on the same day as`) | both happen, on days so placed | `∃t u. on_E(x, t) ∧ on_F(y, u) ∧ …` |
| `<state> is in progress on <day>` | it has begun on or before that day and has not ended before that day (F) | 1.9 |
| `<cause> contributed to <effect>` | an open causal link, decided by its decider | `L(x, y)`, form `contributed` |
| `<cause> was necessary for <effect>` | an open but-for link: without the cause the effect would not have happened, decided by its decider | `N(x, y)`, form `necessary` |
| `12 October 2026`, `2026-10-12`, `the date of this document` | the named day | `c_D` |

Days are quantified with the existing forms ("each day", "there is a day such that", "that day"); no new binder is
added, and quantifier scope inside a sentence ("every day before") is the phrase grammar's (X7). A regulated
predicate may take a day argument ("{0} be presumed innocent on {1}"), which keeps it two-place.

### 2.3 The legend

Generated from the block, in this order: "Times are counted in whole days: two things on the same day happen on the
same day, and neither is before the other." "A state is in progress from the day it begins through the day it ends."
When links are declared: "A cause does not start after the day of an event it contributed to, and does not start
after the last day of a state it contributed to, when that state ends. Whatever was necessary for something
contributed to it." When an anchor is declared: "The date of this document is <long form>."

### 2.4 Source words: reading sets (D8, D9, X9)

In a translation, each word below opens a reading set whose candidates are explicit wordings; the distinguishing
situation is shown with it. ET-5 writes these rows, rows only, into english-lean's catalogue.

| Source word | Candidates | Distinguishing situation |
|---|---|---|
| "m X until E" (E an event), for each modality m | U1: m X on each day before the day E happens (silent from that day); U2: U1, and the opposite of m on each day from the day E happens. The opposite of "may" is "must not", of "must" is "need not", of "must not" is "may", of "need not" is "must" (R2) | E's day, the day before it and a later day (T11, T11b); with the predicate unspecified, U1 is UNDECIDED from E's day and U2 settled to the opposite |
| "m X until D" (D a date) | the four candidates exclusive (each day before D) or inclusive (each day no later than D), each silent after or with the opposite from the next day (R2) | D itself and the day after D (T11c) |
| "by D" (a deadline) | B1: before D; B2: no later than D | the act on D itself |
| "within n days of D" | W1: on or after D and no later than the date n days after D; W2: on or after D and before the date n days after D; W3: on or after the date n days before D and no later than the date n days after D. The translator names both end dates as named dates (SR-B4) | an act on the date n days after D (W1 and W3 against W2) and an act before D, within n days of it (W3 against W1 and W2) (T11d). "within n days of <event>" has no candidate: UNFORMALISED, reason `duration` (ET-T1) |
| "during S", "while S" (temporal) | on each day on which S is in progress | none (one candidate; the legend's inclusive end decides the last day) |
| "while" (contrast) | the two clauses joined by "and" | a reading set with the temporal candidate; a day on which S is not in progress |
| "since E" | S1: on each day after the day E happens; S2: on each day on or after that day | E's own day |
| "always" | A1: on each day; A2: on each day on or after the date of this document | a day before the anchor (with no anchor, A1 only) |
| "eventually" | E1: there is a day such that …; E2: there is a day after the date of this document such that … | only a day before the anchor (with no anchor, E1 only) |
| "whenever C" | on each day on which C holds | none (one candidate) |
| "resulted in", "led to", "caused" (between events or states) | C1: <cause> contributed to <effect>; C2: <cause> was necessary for <effect>; C3, only where a decision model is declared: <action> leads to <harm> | a situation in which the contributed link holds and the necessary link does not |

Under a `deny` or `allow` completion, U1 and U2 may coincide; then the set has no distinguishing situation and the
translator must choose, and the grounding line of norm-defaults 3.2 applies.

### 2.5 Authored text: refusals with rewrites

When `events@0` is on, each pattern is rejected with its advice (advice rows in english-lean's catalogue):

| Pattern | Advice |
|---|---|
| `until <...>` | "Write the rule for each day with the guard 'if it is not the case that <event> happens no later than that day'; the text then says nothing about later days. If it means the rule stops, add a second rule with the opposite wording ('must not' for 'may', 'need not' for 'must', 'may' for 'must not') for the days on which <event> happens no later than that day. For a date, say whether the date itself is included: 'before <date>' or 'no later than <date>'." |
| `by <day or event>` (a deadline) | "Write 'before <day>' or 'no later than <day>'." |
| `within <n> days` | "Durations over events are not available here; name the dates, or use the quantity wordings in a quantity document." |
| `during <state>`, `while <state>` | "Write the rule for each day with the guard '<state> is in progress on that day'." |
| `since <...>`, `always`, `eventually`, `whenever` | "Write the days explicitly: 'on each day, if ...', 'there is a day such that ...'." |
| `resulted in`, `led to`, `caused` between events | "Write '<cause> contributed to <effect>' or '<cause> was necessary for <effect>'; in a decision model write 'leads to'." |

The link wordings are disjoint from `alternatives@0`'s and `risk@0`'s fixed wordings (`leads to`, `allows ... to
happen`, `prevents`, `causes`, `might lead to`, `cannot lead to`); the catalogue's disjointness check covers them, and
alternatives' rejection of "results in" and "brings about" stays (D11).

## 3. Wire and identity

- **The block** is in the canonical environment bytes, so `environment_id` changes only for environments that carry
  it; an environment without it is byte-identical to today.
- **The regenerated vocabulary** declares the named-date constants. Python builds the bytes for certificate bindings
  by relaying Lean's `baseEnvironmentJson`, never by computing them.
- **Binding.** `eventsX V` enters `premisesX` as the last pack, so every certificate binds it by meaning id; a replay
  against a changed block, date list or link decider is stale.
- **Report fields** (ET-4, typed response shapes with encoder theorems): `named_dates` (each date's ISO and its
  constant), `events_premises` (the labels of 1.4 in order), `causal_links` (1.10), and, on every reported situation,
  `calendar_days`: each day of the situation with its civil date (`numbering`, then `VE.Time.civilOf`), so an unnamed
  day of a countermodel reads as a date ("13 October 2026").
- **Relay** (`ve/events.py`): every named date, label, link and day the answer names exists in the request, and no
  row is empty or extra; anything else is `CheckerUnavailable`.

## 4. Diagnostics, in order

Decoding stops at the first failure.

1. The profile row (1.1): `UnsupportedProfile: events@0 requires <p>`, then `UnsupportedProfile: events@0 with <p>`.
2. The block's shape: `InvalidInput: events.<field>` (unknown or missing field, wrong type);
   `InvalidInput: events.links.decided_by` (more than 64 bytes; `unstated` is the explicit absence).
3. The day and `before`: `EventsSort: <day>` (the day sort undeclared); `EventsSort: <before>` (signature not
   `(day, day)`); `EventsVerbalisation: <before>` (not exactly "{0} is before {1}"); `EventsRegulated: <p>` (`before`,
   a role or a link is regulated or defined).
4. Event and state sorts: `EventsSort: <s>` (undeclared, or the day sort); `DuplicateDeclaration: event sort <s>` or
   `DuplicateDeclaration: state sort <s>` (a sort used twice among event and state sorts); `EventsSort: <p>` (a role's
   signature is not `(s, day)`); `EventsVerbalisation: <p>` (`roleWordingOk` fails); `DuplicateDeclaration: role <p>`
   (role predicates not pairwise distinct, or one equal to `before`).
5. Links: `EventsSort: <p>` (signature not two event or state sorts); `EventsVerbalisation: <p>` (not its form's
   wording); `DuplicateDeclaration: link <p>`; `LinkNotOpen: <p>` (not declared as an open term with the same decider).
6. Dates: `parseIso`'s own texts, unchanged (`InvalidDate(<s>)`, `DateRange(<s>)`); `DuplicateDeclaration: date
   <iso>`; `ResourceLimit: events dates` (more than 64); `EventsReserved: <name>` (a declared name starting with
   `date__`).
7. `ResourceLimit: events premise <label>` (a generated premise over `MAX_NODES`).

At answer time:

- A supplied situation that violates a generated premise: the layered route's existing text with the pack's id,
  `InvalidModel(events): the model violates a background premise`, and the first failing label (`events:one_day:act`)
  in the answer's detail where the route has one.
- A situation that fails `calendarCheck`: UNKNOWN with its text, one of `NotCalendar: before is not a strict linear
  order on the days`, `NotCalendar: <iso> denotes no day`, `NotCalendar: <iso> is not before <iso>`, `NotCalendar: <n>
  days before <iso>, at most <m>`, `NotCalendar: <n> days between <iso> and <iso>, at most <m>`, `NotCalendar: <n>
  days after <iso>, at most <m>`, `NotCalendar: <n> days, at most 2932897` ("1 day" for one).
- A situation outside the fragment (1.8): UNKNOWN with `NotCalendar: <label> may change when the missing calendar days
  are added`, the label being a premise's label, `the conclusion`, `the target <name>` or `the outcome of <p>`.
- For a status (1.8, SR-B3): a situation whose declared literals coincide is the layered route's existing
  `InvalidModel(literals): the model violates a background premise`; a supplied filling that violates another pack's
  premise is that pack's text (`InvalidModel(soft): the model violates a background premise`); a situation for which
  no filling passes `fillValid` and `extraValid` is UNKNOWN, never SETTLED.

`NotCalendar: <iso> denotes no day` is unreachable through the service: a valid situation interprets every declared
constant in its sort (the first clause of `Admissible`), so it is checked by a Lean `#guard` on `calendarCheck` only
(T3, SR-B5).

## 5. `alternatives@0` with the completion (ET-7): the evidence contract (C)

The alternatives route accepts `norm-defaults@0` beside `alternatives@0` and `norms@0` (D13). Its decoder
(`decodeAltSourceU`) has `decodeSourceU`'s two branches (SR-A2). **Without `norm-defaults@0`**, an `unspecified`
value is `UnsupportedProfile: unspecified completion requires norm-defaults@0`, and otherwise today's decoder runs
unchanged, its texts included (`decodeAltSourceU_conservative`). **With it**, the decoder checks the original
profile list with today's gate (`profileGate`: sorted and unique, `alternatives@0` and `norms@0` present, no
`soft-norms@0`), reads each `unspecified` default as the placeholder and sets the profile aside (`placeholderJson`),
runs today's decoder on the result (the rest of the profile list, the block, the rules and Γ), records the
unspecified predicates in regulated order, then checks the reserved names and author limits of nd 8 (`checkAuthor`)
and `WellFormedU`, each failure under its own text. It answers:

- **CONFLICT-FREE** over the alternatives route's own base: no conflict in any structure of `BaseAdmissibleAltU`,
  which includes the slot premises (`AltConflictFreeU`, as today's `AltConflictFree` over `BaseAdmissibleAlt`;
  SR-A3). As today, CONFLICT-FREE is the prerequisite of the document's FOLLOWABLE and DILEMMA.
- **FOLLOWABLE** from a certificate over `backgroundBaseAltU A unspec ++ A.Γ` for `allFollowableU` (`followableU_sound`,
  proved; on the wire `alternativesU_wire_followable_sound`).
- **DILEMMA** from a witness situation that passes today's scenario validation (`M.Valid`, `backgroundValidAlt`, the
  signed rows, the existence checks and Γ), a filling validated by `fillValid`, and a typed chooser at which
  `¬ followable°` holds (`alternativesU_dilemma_witness_sound`). Its statement assumes `WellFormedAlt A`: Γ is typed
  over the base vocabulary, which declares no unsaid predicate, so Γ keeps its value when the filling is added
  (SR-A1, T12c).
- **Per alternative**, in a scenario: **clear** or **not clear** only when its `clear` formula is settled under every
  admissible filling, from a definite Kleene value (`kleene_sound`) or an enumeration of its cone within
  `MAX_UNSAID_ATOMS` (as `settled_of_enumeration`); **UNDECIDED** only from two fillings, each validated, that give
  `clear` opposite values (as `undecided_witness_sound`, nd 2.5); **UNKNOWN** otherwise, naming the budget when it was
  exhausted. A Kleene "unknown" alone is UNKNOWN, never UNDECIDED. Each row carries its evidence (`ScenarioRowU`'s
  soundness fields, 6.4), as `StatusX` does on the layered route, and every row also carries the scenario's validity
  (today's validation with its signed rows, a typed chooser and action) and one filling validated by `fillValid`, so
  no status is vacuous (SR-A4). A scenario that fails validation answers with today's validation text; one for which
  no filling is validated is UNKNOWN for every alternative; neither is ever clear or not clear (T12f).
- The untrusted diagnosis gains `UNSETTLED(<alternatives>)` before NONE-PERMITTED, listing only alternatives with
  UNDECIDED evidence; nothing new is claimed for it.

The refusal `alternatives@0 with norm-defaults@0 is not implemented` and the route's own `UnsupportedProfile:
Unsupported profile norm-defaults@0` are deleted; the deletion in `Dispatch.lean` is serialised with AR-10's table
(X3). `risk@0` with the completion stays refused (nd 293-298).

## 6. Lean statements

Files: `lean/VE/Events/{Decl,Premises,Calendar,Completion,Conservative,Wire,Chain}.lean`, `lean/EVENTS.md`; ET-7
`lean/VE/Alternatives/FillWire.lean`. Names are under `VE.Events` (ET-7 `VE.Alternatives`); no theorem name contains a
prime, and no name or comment contains a word `lean/audit.py` rejects. Without Mathlib, order lemmas are proved
locally. RD-9's `premisesX`, `EntailsX` and `modelCheckX` are on `rd-9/integrate` (`LayeredEntail.lean`), not on
`main`; PK-1's `Pack` is not built yet. The stub copies the first and states the second as the synthesis defines it.

### 6.1 Definitions (ET-3)

```lean
namespace VE.Events
open VE.Norms (Sat)
open VE.Time (Civil dateMax)

def maxDates : Nat := 64
def dateName (D : Civil) : String := "date__" ++ D.iso.map (fun c => if c = '-' then '_' else c)
def dateConst (D : Civil) : VE.Term := .const (dateName D)

def eventSorts (V : EventsEnv) : List String := V.events.map (·.sort)
def stateSorts (V : EventsEnv) : List String := V.states.map (·.sort)
def roleSorts (V : EventsEnv) : List String := eventSorts V ++ stateSorts V
def rolePreds (V : EventsEnv) : List String :=
  V.events.map (·.on) ++ V.states.flatMap (fun s => [s.begins, s.ends])

/-- The role giving the day a thing starts: `on` for an event sort, `begins` for a state sort. -/
def startRole (V : EventsEnv) (s : String) : Option String :=
  match V.events.find? (·.sort == s) with
  | some e => some e.on
  | none => (V.states.find? (·.sort == s)).map (·.begins)

/-- The role bounding an effect: `on` for an event sort, `ends` for a state sort. -/
def boundRole (V : EventsEnv) (s : String) : Option String :=
  match V.events.find? (·.sort == s) with
  | some e => some e.on
  | none => (V.states.find? (·.sort == s)).map (·.ends)

def sig2 (E : VE.Environment) (p s t : String) : Bool := E.predicates p == some [s, t]

/-- A role's verbalisation: "{0} <verb phrase> on {1}", the verb phrase nonempty and with no slot (R3). -/
def roleWordingOk (w : String) : Bool :=
  let vp := (w.drop 4).dropRight 7
  w.startsWith "{0} " && w.endsWith " on {1}" && !vp.isEmpty && !vp.contains '{' && !vp.contains '}'

def beforeWording : String := "{0} is before {1}"
def linkWording : LinkForm → String
  | .contributed => "{0} contributed to {1}"
  | .necessary => "{0} was necessary for {1}"

def consecutive (V : EventsEnv) : List (Civil × Civil) := V.dates.zip V.dates.tail

/-- The block against the author's environment (before the dates are regenerated). -/
def WellFormedEvents (E : VE.Environment) (V : EventsEnv) : Bool :=
  E.sorts.contains V.day && sig2 E V.before V.day V.day &&
  V.events.all (fun e => E.sorts.contains e.sort && e.sort != V.day && sig2 E e.on e.sort V.day) &&
  V.states.all (fun s => E.sorts.contains s.sort && s.sort != V.day && sig2 E s.begins s.sort V.day &&
    sig2 E s.ends s.sort V.day) &&
  decide (roleSorts V).Nodup && decide (rolePreds V).Nodup && !(rolePreds V).contains V.before &&
  V.links.all (fun l => sig2 E l.predicate l.cause l.effect && (roleSorts V).contains l.cause &&
    (roleSorts V).contains l.effect && !(rolePreds V).contains l.predicate && l.predicate != V.before) &&
  decide (V.links.map (·.predicate)).Nodup &&
  V.dates.all (fun D => D.properB && decide (D.year ≤ 9999) && E.constants (dateName D) == none) &&
  (consecutive V).all (fun p => decide (p.1.num < p.2.num)) &&
  decide (V.dates.length ≤ maxDates) &&
  V.anchor.all (fun A => V.dates.contains A)

def regenEnv (E : VE.Environment) (V : EventsEnv) : VE.Environment :=
  { E with constants := fun c => if V.dates.any (fun D => dateName D == c) then some V.day else E.constants c }

/-- The regenerated environment types the block. -/
def EventsTyped (E : VE.Environment) (V : EventsEnv) : Bool :=
  E.sorts.contains V.day && sig2 E V.before V.day V.day &&
  V.events.all (fun e => E.sorts.contains e.sort && e.sort != V.day && sig2 E e.on e.sort V.day) &&
  V.states.all (fun s => E.sorts.contains s.sort && s.sort != V.day && sig2 E s.begins s.sort V.day &&
    sig2 E s.ends s.sort V.day) &&
  V.links.all (fun l => sig2 E l.predicate l.cause l.effect) &&
  V.dates.all (fun D => D.properB && E.constants (dateName D) == some V.day) &&
  (consecutive V).all (fun p => decide (p.1.num < p.2.num))

def bin (p : String) (i j : Nat) : VE.Formula := .binary p (.var i) (.var j)

def irreflexiveF (V : EventsEnv) : VE.Formula := .all V.day (.not (bin V.before 0 0))
def transitiveF (V : EventsEnv) : VE.Formula :=
  .all V.day (.all V.day (.all V.day
    (.implies (.and (bin V.before 2 1) (bin V.before 1 0)) (bin V.before 2 0))))
def linearF (V : EventsEnv) : VE.Formula :=
  .all V.day (.all V.day (.or (bin V.before 1 0) (.or (.eq (.var 1) (.var 0)) (bin V.before 0 1))))
def dateFactF (V : EventsEnv) (D D' : Civil) : VE.Formula := .binary V.before (dateConst D) (dateConst D')
def adjacentF (V : EventsEnv) (D D' : Civil) : VE.Formula :=
  .all V.day (.not (.and (.binary V.before (dateConst D) (.var 0)) (.binary V.before (.var 0) (dateConst D'))))
/-- `∀x. ∀t. role(x,t) → ∀u. role(x,u) → t = u` (guarded). -/
def oneRoleF (V : EventsEnv) (sort role : String) : VE.Formula :=
  .all sort (.all V.day (.implies (bin role 1 0)
    (.all V.day (.implies (bin role 2 0) (.eq (.var 1) (.var 0))))))
/-- `∀x. ∀t. begins(x,t) → ∀u. ends(x,u) → ¬ before(u,t)` (guarded). -/
def notBeforeBeginF (V : EventsEnv) (s : StateSort) : VE.Formula :=
  .all s.sort (.all V.day (.implies (bin s.begins 1 0)
    (.all V.day (.implies (bin s.ends 2 0) (.not (bin V.before 0 1))))))
/-- `∀x y. L(x,y) → ∀t. start(x,t) → ∀u. bound(y,u) → ¬ before(u,t)` (guarded). -/
def linkForwardF (V : EventsEnv) (l : Link) : VE.Formula :=
  match startRole V l.cause, boundRole V l.effect with
  | some st, some bd =>
    .all l.cause (.all l.effect (.implies (bin l.predicate 1 0)
      (.all V.day (.implies (bin st 2 0)
        (.all V.day (.implies (bin bd 2 0) (.not (bin V.before 0 1))))))))
  | _, _ => .top
/-- `∀x y. N(x,y) → C(x,y)`. -/
def linkWeakerF (n c : Link) : VE.Formula :=
  .all n.cause (.all n.effect (.implies (bin n.predicate 1 0) (bin c.predicate 1 0)))
def weakerPairs (V : EventsEnv) : List (Link × Link) :=
  (V.links.filter (fun l => l.form == LinkForm.necessary)).flatMap fun n =>
    (V.links.filter (fun c => c.form == LinkForm.contributed && c.cause == n.cause && c.effect == n.effect)).map
      (fun c => (n, c))

def isoPair (D D' : Civil) : String := D.iso ++ ":" ++ D'.iso

def calendarLabelled (V : EventsEnv) : List (String × VE.Formula) :=
  [("events:irreflexive", irreflexiveF V), ("events:transitive", transitiveF V), ("events:linear", linearF V)] ++
  (consecutive V).map (fun p => ("events:date:" ++ isoPair p.1 p.2, dateFactF V p.1 p.2)) ++
  ((consecutive V).filter (fun p => p.2.num == p.1.num + 1)).map
    (fun p => ("events:adjacent:" ++ isoPair p.1 p.2, adjacentF V p.1 p.2))

def conventionLabelled (V : EventsEnv) : List (String × VE.Formula) :=
  V.events.map (fun e => ("events:one_day:" ++ e.sort, oneRoleF V e.sort e.on)) ++
  V.states.flatMap (fun s => [("events:one_begin:" ++ s.sort, oneRoleF V s.sort s.begins),
    ("events:one_end:" ++ s.sort, oneRoleF V s.sort s.ends),
    ("events:not_before_begin:" ++ s.sort, notBeforeBeginF V s)]) ++
  V.links.map (fun l => ("events:link_forward:" ++ l.predicate, linkForwardF V l)) ++
  (weakerPairs V).map (fun p => ("events:link_weaker:" ++ p.1.predicate ++ ":" ++ p.2.predicate, linkWeakerF p.1 p.2))

def eventsLabelled (V : EventsEnv) : List (String × VE.Formula) := calendarLabelled V ++ conventionLabelled V
def orderPremises (V : EventsEnv) : List VE.Formula := [irreflexiveF V, transitiveF V, linearF V]
def calendarPremises (V : EventsEnv) : List VE.Formula := (calendarLabelled V).map (·.2)
def conventionPremises (V : EventsEnv) : List VE.Formula := (conventionLabelled V).map (·.2)
def eventsX (V : EventsEnv) : List VE.Formula := (eventsLabelled V).map (·.2)

def Embeds (V : EventsEnv) (S : VE.Structure.{u}) (num : S.Carrier → Nat) : Prop :=
  (∀ x y, S.domain V.day x → S.domain V.day y → num x = num y → x = y) ∧
  (∀ x, S.domain V.day x → num x ≤ dateMax) ∧
  (∀ x y, S.domain V.day x → S.domain V.day y → (S.relation V.before [x, y] ↔ num x < num y)) ∧
  (∀ D ∈ V.dates, ∃ x, S.constant (dateName D) = some x ∧ S.domain V.day x ∧ num x = D.num)

def CalendarReading (V : EventsEnv) (S : VE.Structure.{u}) (num : S.Carrier → Nat) : Prop :=
  Embeds V S num ∧ ∀ n, n ≤ dateMax → ∃ x, S.domain V.day x ∧ num x = n
```

The calendar check, the numbering and the completion (`α : Type`, situations are over `VE.Bridge.Entity`):

```lean
section Finite
variable {α : Type} [DecidableEq α]

def beforeB (V : EventsEnv) (M : VE.FiniteModel α) (x y : α) : Bool := decide ([x, y] ∈ M.relations V.before)
def rank (V : EventsEnv) (M : VE.FiniteModel α) (x : α) : Nat :=
  ((M.domains V.day).filter (fun y => beforeB V M y x)).length
def dateDay (V : EventsEnv) (M : VE.FiniteModel α) (D : Civil) : Option α :=
  (M.constants (dateName D)).filter (fun x => (M.domains V.day).contains x)
def namedRank (V : EventsEnv) (M : VE.FiniteModel α) (D : Civil) : Nat :=
  ((dateDay V M D).map (rank V M)).getD 0
def daysText (n : Nat) : String := if n = 1 then "1 day" else s!"{n} days"

def strictLinearB (V : EventsEnv) (M : VE.FiniteModel α) : Bool :=
  let ds := M.domains V.day
  decide ds.Nodup && ds.all (fun x => !beforeB V M x x) &&
    ds.all (fun x => ds.all (fun y => ds.all (fun z => !(beforeB V M x y && beforeB V M y z) || beforeB V M x z))) &&
    ds.all (fun x => ds.all (fun y => x == y || beforeB V M x y || beforeB V M y x))

def calendarCheck (V : EventsEnv) (M : VE.FiniteModel α) : Option String :=
  let ds := M.domains V.day
  let r := namedRank V M
  if !strictLinearB V M then some "NotCalendar: before is not a strict linear order on the days"
  else match V.dates.find? (fun D => (dateDay V M D).isNone) with
  | some D => some s!"NotCalendar: {D.iso} denotes no day"
  | none =>
  match (consecutive V).find? (fun p => !decide (r p.1 < r p.2)) with
  | some p => some s!"NotCalendar: {p.1.iso} is not before {p.2.iso}"
  | none =>
  match V.dates with
  | [] =>
    if ds.length ≤ dateMax + 1 then none
    else some s!"NotCalendar: {daysText ds.length}, at most {dateMax + 1}"
  | D₁ :: rest =>
    let Dk := (D₁ :: rest).getLastD D₁
    if r D₁ > D₁.num then some s!"NotCalendar: {daysText (r D₁)} before {D₁.iso}, at most {D₁.num}"
    else match (consecutive V).find? (fun p => decide (r p.2 - r p.1 - 1 > p.2.num - p.1.num - 1)) with
    | some p =>
      some s!"NotCalendar: {daysText (r p.2 - r p.1 - 1)} between {p.1.iso} and {p.2.iso}, at most {p.2.num - p.1.num - 1}"
    | none =>
      if ds.length - 1 - r Dk > dateMax - Dk.num then
        some s!"NotCalendar: {daysText (ds.length - 1 - r Dk)} after {Dk.iso}, at most {dateMax - Dk.num}"
      else none

def embeddable (V : EventsEnv) (M : VE.FiniteModel α) : Bool := (calendarCheck V M).isNone

def numbering (V : EventsEnv) (M : VE.FiniteModel α) (x : α) : Nat :=
  let r := namedRank V M
  match (V.dates.filter (fun D => decide (r D ≤ rank V M x))).getLast? with
  | some D => D.num + (rank V M x - r D)
  | none =>
    match V.dates with
    | [] => rank V M x
    | D₁ :: _ => D₁.num - (r D₁ - rank V M x)
end Finite

def numOf {α : Type} (num : α → Nat) : α ⊕ Nat → Nat
  | .inl x => num x
  | .inr n => n
def oldTuple {α : Type} : List (α ⊕ Nat) → Option (List α)
  | [] => some []
  | .inl x :: zs => (oldTuple zs).map (x :: ·)
  | .inr _ :: _ => none
def addedDay {α : Type} (V : EventsEnv) (M : VE.FiniteModel α) (num : α → Nat) (n : Nat) : Prop :=
  n ≤ dateMax ∧ ∀ x ∈ M.domains V.day, num x ≠ n
def isDayC {α : Type} (V : EventsEnv) (M : VE.FiniteModel α) (num : α → Nat) : α ⊕ Nat → Prop
  | .inl x => x ∈ M.domains V.day
  | .inr n => addedDay V M num n

def completion {α : Type} (V : EventsEnv) (M : VE.FiniteModel α) (num : α → Nat) : VE.Structure.{0} where
  Carrier := α ⊕ Nat
  domain := fun s z => match z with
    | .inl x => x ∈ M.domains s
    | .inr n => s = V.day ∧ addedDay V M num n
  constant := fun c => (M.constants c).map Sum.inl
  relation := fun p zs => match oldTuple zs with
    | some xs => xs ∈ M.relations p
    | none => p = V.before ∧ ∃ z w, zs = [z, w] ∧ isDayC V M num z ∧ isDayC V M num w ∧ numOf num z < numOf num w
```

The fragment, day extensions and the untouched vocabulary:

```lean
def isConst : VE.Term → Bool
  | .const _ => true
  | .var _ => false

mutual
def hits (ng : List String) (k : Nat) : VE.Formula → Bool
  | .bottom => true
  | .unary p t => !ng.contains p && t == .var k
  | .binary p t w => !ng.contains p && (t == .var k || w == .var k)
  | .eq t w => (t == .var k && isConst w) || (w == .var k && isConst t)
  | .not a => vacuous ng k a
  | .and a b => hits ng k a || hits ng k b
  | .or a b => hits ng k a && hits ng k b
  | .ex _ a => hits ng (k + 1) a
  | _ => false
def vacuous (ng : List String) (k : Nat) : VE.Formula → Bool
  | .top => true
  | .not a => hits ng k a
  | .and a b => vacuous ng k a && vacuous ng k b
  | .or a b => vacuous ng k a || vacuous ng k b
  | .implies a b => hits ng k a || vacuous ng k b
  | .all _ a => vacuous ng (k + 1) a
  | _ => false
end

mutual
def up (day : String) (ng : List String) : VE.Formula → Bool
  | .not a => down day ng a
  | .and a b => up day ng a && up day ng b
  | .or a b => up day ng a && up day ng b
  | .implies a b => down day ng a && up day ng b
  | .ex _ a => up day ng a
  | .all s a => up day ng a && (s != day || vacuous ng 0 a)
  | _ => true
def down (day : String) (ng : List String) : VE.Formula → Bool
  | .not a => up day ng a
  | .and a b => down day ng a && down day ng b
  | .or a b => down day ng a && down day ng b
  | .implies a b => up day ng a && down day ng b
  | .ex s a => down day ng a && (s != day || hits ng 0 a)
  | .all _ a => down day ng a
  | _ => true
end

def DayExtension (day : String) (ng : List String) (M : VE.Structure.{u}) (S : VE.Structure.{v})
    (ι : M.Carrier → S.Carrier) : Prop :=
  (∀ x y, ι x = ι y → x = y) ∧
  (∀ s x, S.domain s (ι x) ↔ M.domain s x) ∧
  (∀ s y, S.domain s y → (∀ x, ι x ≠ y) → s = day) ∧
  (∀ c, S.constant c = (M.constant c).map ι) ∧
  (∀ p xs, S.relation p (xs.map ι) ↔ M.relation p xs) ∧
  (∀ p ys, S.relation p ys → (∃ y ∈ ys, ∀ x, ι x ≠ y) → p ∈ ng)

/-- The vocabulary the block does not touch: no day sort, nothing with the day sort in its signature, no link. -/
def oldEnv (E : VE.Environment) (V : EventsEnv) : VE.Environment :=
  { sorts := E.sorts.filter (· != V.day)
    predicates := fun p => match E.predicates p with
      | some ss => if ss.contains V.day || V.links.any (·.predicate == p) then none else some ss
      | none => none
    constants := fun c => match E.constants c with
      | some s => if s == V.day then none else some s
      | none => none }
```

### 6.2 Theorems (ET-3)

```lean
theorem regen_typed (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true) :
    EventsTyped (regenEnv E V) V = true

/-- Every generated premise is closed and typed over the regenerated environment. -/
theorem eventsPremises_wellFormed (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true) :
    ∀ p ∈ eventsX V, p.WellFormed (regenEnv E V) []

/-- Every embedding (so every calendar reading) satisfies the calendar premises. -/
theorem calendar_sat (E : VE.Environment) (V : EventsEnv) (hT : EventsTyped E V = true) (S : VE.Structure.{u})
    (hS : S.Admissible E) (num : S.Carrier → Nat) (hc : Embeds V S num) :
    Sat S (calendarPremises V)

/-- Named dates are ordered exactly as the calendar orders them, in every structure of the calendar premises. -/
theorem datesOrder_iff (E : VE.Environment) (V : EventsEnv) (hT : EventsTyped E V = true) (S : VE.Structure.{u})
    (hS : S.Admissible E) (hp : Sat S (calendarPremises V)) (D D' : Civil) (hD : D ∈ V.dates)
    (hD' : D' ∈ V.dates) :
    (VE.Formula.binary V.before (dateConst D) (dateConst D')).denote S [] ↔ D.num < D'.num

/-- One owner of the calendar: the generated order is W6a's chronological order. -/
theorem datesOrder_calendar (D D' : Civil) (hD : D.Proper) (hD' : D'.Proper) :
    D.num < D'.num ↔ D.Before D' :=
  (VE.Time.before_iff hD hD').symm

/-- The pack alone is satisfiable by a finite calendar situation. -/
theorem eventsPremises_satisfiable (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true) :
    ∃ M : VE.FiniteModel VE.Bridge.Entity, M.Valid (regenEnv E V) ∧ Sat M.asStructure (eventsX V) ∧
      embeddable V M = true

/-- The check passes only when the numbering embeds the situation (the check itself gives the calendar premises on
    the situation's days, so none is assumed: SR-B2) ... -/
theorem embeddable_sound {α : Type} [DecidableEq α] (E : VE.Environment) (V : EventsEnv)
    (hT : EventsTyped E V = true) (M : VE.FiniteModel α) (valid : M.Valid E) (he : embeddable V M = true) :
    Embeds V M.asStructure (numbering V M)

/-- ... and passes whenever some numbering does. -/
theorem embeddable_complete {α : Type} [DecidableEq α] (E : VE.Environment) (V : EventsEnv)
    (hT : EventsTyped E V = true) (M : VE.FiniteModel α) (valid : M.Valid E) (hn : (M.domains V.day).Nodup)
    (num : α → Nat) (hm : Embeds V M.asStructure num) :
    embeddable V M = true

/-- The transfer theorem: in a day extension, `up` formulas stay true and `down` formulas stay false, at every
    valuation of old elements. -/
theorem dayExtension_transfer (day : String) (ng : List String) (M : VE.Structure.{u}) (S : VE.Structure.{v})
    (ι : M.Carrier → S.Carrier) (hx : DayExtension day ng M S ι) (a : VE.Formula) (ρ : List M.Carrier) :
    (up day ng a = true → a.denote M ρ → a.denote S (ρ.map ι)) ∧
    (down day ng a = true → a.denote S (ρ.map ι) → a.denote M ρ)

/-- The completion is a day extension in which only `before` has tuples with added days ... -/
theorem completion_extension {α : Type} [DecidableEq α] (V : EventsEnv) (M : VE.FiniteModel α) (num : α → Nat)
    (hm : Embeds V M.asStructure num) :
    DayExtension V.day [V.before] M.asStructure (completion V M num) Sum.inl

/-- ... whose days are every civil day ... -/
theorem completion_reading {α : Type} [DecidableEq α] (V : EventsEnv) (M : VE.FiniteModel α) (num : α → Nat)
    (hm : Embeds V M.asStructure num) :
    CalendarReading V (completion V M num) (numOf num)

/-- ... and which is a structure of the situation's environment. -/
theorem completion_admissible {α : Type} [DecidableEq α] (E : VE.Environment) (V : EventsEnv)
    (hT : EventsTyped E V = true) (M : VE.FiniteModel α) (valid : M.Valid E) (num : α → Nat)
    (hm : Embeds V M.asStructure num) :
    (completion V M num).Admissible E

/-- The conventions are in the fragment both ways. -/
theorem conventions_exact (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true) (ng : List String)
    (hng : ∀ p ∈ rolePreds V ++ V.links.map (·.predicate), p ∉ ng) :
    ∀ a ∈ conventionPremises V, up V.day ng a = true ∧ down V.day ng a = true

/-- Conservativity over the untouched vocabulary. Proof by restriction one way and, the other way, by an expansion
    on `S.Carrier ⊕ ULift Nat` whose days are the named dates' days in date order (author day constants sent to the
    first named day, or to a single day 0 when there is none; role, link and day-indexed relations empty). -/
theorem events_conservative (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (oldEnv E V) []) (hφ : φ.WellFormed (oldEnv E V) []) :
    (∀ S : VE.Structure.{u}, S.Admissible (regenEnv E V) → Sat S (eventsX V) → Sat S Γ → φ.denote S []) ↔
    (∀ S : VE.Structure.{u}, S.Admissible (oldEnv E V) → Sat S Γ → φ.denote S [])
```

### 6.3 The pack, the wire and the answers (ET-4)

```lean
open VE.NormDefaults (UDoc fill WellFormedU FiniteFill FillTables withFill finFill fillValid fillBody openPairs
  canonicalFill BaseAdmissibleU EntailsX modelCheckX fillPremises unsaidNames SettledAs)
open VE.NormDefaults.Wire (BaseAdmissibleX extraValid)
open VE.Norms (subst size envAt backgroundBase outcomeBase Regulated tupleVal)

structure EventsDecoded where
  V : EventsEnv
  E : VE.Environment                          -- the regenerated environment
  origins : List (String × VE.Packs.RequestPath)

def decodeEvents (environment : Lean.Json) : Except String (Option EventsDecoded)   -- 1.2 and 4

def eventsPack (d : EventsDecoded) : VE.Packs.Pack :=
  { id := "events", kind := .constraint, decls := d.V.dates.map (fun D => (dateName D, [d.V.day])),
    labelled := eventsLabelled d.V, origins := d.origins }

/-- An absent block gives no pack (PK-1's rule then leaves X as the other packs' X). -/
theorem eventsX_absent (environment : Lean.Json) (h : (environment.getObjVal? "events").toOption = none) :
    decodeEvents environment = .ok none

def unguarded (U : UDoc) (V : EventsEnv) : List String := V.before :: unsaidNames U

/-- The body of each `Fill_T` premise, before its pair's universal closure (`fillBody`, nd's owner; SR-B1). -/
def fillBodies (U : UDoc) : List VE.Formula := (openPairs U).map (fillBody U)

/-- Every premise-side formula an `up` test reads, except the calendar premises; `Fill_T` through its bodies. -/
def checkedPremises (U : UDoc) (V : EventsEnv) (X : List VE.Formula) : List VE.Formula :=
  backgroundBase (fill U) ++ fillBodies U ++ X ++ conventionPremises V

/-- A filling extended to the completion (SR-B1): the filling on tuples of old elements, `canonicalFill` on tuples
    with an added day. -/
def completionFill {α : Type} [DecidableEq α] (U : UDoc) (V : EventsEnv) (M : VE.FiniteModel α) (num : α → Nat)
    (F : FillTables U M.asStructure) : FillTables U (completion V M num) :=
  fun n zs => match oldTuple (α := α) zs with
    | some xs => F n xs
    | none => canonicalFill U (completion V M num) n zs

/-- The filled completion every situation-based answer reports. -/
def completed {α : Type} [DecidableEq α] (U : UDoc) (V : EventsEnv) (M : VE.FiniteModel α)
    (F : FillTables U M.asStructure) : VE.Structure.{0} :=
  withFill U (completion V M (numbering V M)) (completionFill U V M (numbering V M) F)

def modelSafe (U : UDoc) (V : EventsEnv) (X Γ : List VE.Formula) (φ : VE.Formula) (value : Bool) : Bool :=
  let ng := unguarded U V
  let sub := subst (fill U).T (size (fill U))
  (checkedPremises U V X ++ Γ.map sub).all (up V.day ng) &&
    (if value then up V.day ng (sub φ) else down V.day ng (sub φ))
def witnessSafe (U : UDoc) (V : EventsEnv) (X : List VE.Formula) (ψ : VE.Formula) : Bool :=
  (checkedPremises U V X).all (up V.day (unguarded U V)) && up V.day (unguarded U V) ψ
def settledSafe (U : UDoc) (V : EventsEnv) (X : List VE.Formula) (n : String) : Bool :=
  let ng := unguarded U V
  (backgroundBase (fill U) ++ fillPremises U).all (down V.day ng) &&
    (checkedPremises U V X).all (up V.day ng) &&
    up V.day ng (outcomeBase (fill U) n) && down V.day ng (outcomeBase (fill U) n)
def undecidedSafe (U : UDoc) (V : EventsEnv) (X : List VE.Formula) (n : String) : Bool :=
  let ng := unguarded U V
  (checkedPremises U V X).all (up V.day ng) &&
    up V.day ng (outcomeBase (fill U) n) && down V.day ng (outcomeBase (fill U) n)

/-- SR-B1, the canonical extension: an admissible filling of the situation, extended by `completionFill`, is an
    admissible filling of the completion. Proof: the filled completion is a day extension of the filled situation
    with `ng = unguarded U V`; on tuples of old elements the base background and each fill premise's body transfer
    by `dayExtension_transfer`; on a tuple with an added day the body holds pointwise, as in `canonical_fill_sat`
    (`fill_sat_of`). -/
theorem fillPremises_canonical_completion {α : Type} [DecidableEq α] (U : UDoc) (h : WellFormedU U = true)
    (V : EventsEnv) (hT : EventsTyped (envAt U.D 0) V = true) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt U.D 0)) (num : α → Nat) (hm : Embeds V M.asStructure num)
    (F : FillTables U M.asStructure) (hF : BaseAdmissibleU U (withFill U M.asStructure F))
    (hs : (backgroundBase (fill U) ++ fillBodies U).all (up V.day (unguarded U V)) = true) :
    BaseAdmissibleU U (withFill U (completion V M num) (completionFill U V M num F))

/-- Certified entailment at PK-1's assembled X (events last). With `calendar_sat`, every calendar reading that
    satisfies the other packs, the conventions and Γ satisfies φ (D7). -/
theorem events_certificate_calendar (U : UDoc) (h : WellFormedU U = true) (V : EventsEnv) (X Γ : List VE.Formula)
    (φ : VE.Formula) (hX : ∀ a ∈ X ++ eventsX V, a.WellFormed (envAt (fill U) 0) [])
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill U) (size (fill U)))
      (VE.NormDefaults.Wire.premisesX U (X ++ eventsX V) Γ) φ cert = true) :
    EntailsX.{u} U (X ++ eventsX V) Γ φ

/-- A model check inside the fragment is a calendar situation: the filled completion has every civil day,
    satisfies the whole assembled X and Γ, and gives the conclusion the reported value. -/
theorem events_model_calendar (U : UDoc) (h : WellFormedU U = true) (V : EventsEnv) (X : List VE.Formula)
    (hT : EventsTyped (envAt U.D 0) V = true)
    (M : VE.FiniteModel VE.Bridge.Entity) (valid : M.Valid (envAt U.D 0))
    (F : FiniteFill U VE.Bridge.Entity) (Γ : List VE.Formula) (φ : VE.Formula)
    (hm : (modelCheckX U (X ++ eventsX V) M F Γ φ).1 = true)
    (he : embeddable V M = true)
    (hs : modelSafe U V X Γ φ (modelCheckX U (X ++ eventsX V) M F Γ φ).2 = true) :
    CalendarReading V (completion V M (numbering V M)) (numOf (numbering V M)) ∧
      BaseAdmissibleX U (X ++ eventsX V) (completed U V M (finFill M F)) ∧
      (∀ a ∈ Γ, (subst (fill U).T (size (fill U)) a).denote (completed U V M (finFill M F)) []) ∧
      ((subst (fill U).T (size (fill U)) φ).denote (completed U V M (finFill M F)) [] ↔
        (modelCheckX U (X ++ eventsX V) M F Γ φ).2 = true)

/-- A CONFLICT or `reachable` witness inside the fragment is a calendar situation where the target holds: the
    filled completion, at the witness's own tuple. -/
theorem events_witness_calendar (U : UDoc) (h : WellFormedU U = true) (V : EventsEnv) (X : List VE.Formula)
    (hT : EventsTyped (envAt U.D 0) V = true)
    (M : VE.FiniteModel VE.Bridge.Entity) (valid : M.Valid (envAt U.D 0))
    (hb : VE.Norms.backgroundValid U.D M = true)
    (F : FiniteFill U VE.Bridge.Entity) (hF : fillValid U M F = true)
    (hX : extraValid U (X ++ eventsX V) M F = true)
    (ψ : VE.Formula) (ss : List String) (vs : List VE.Bridge.Entity)
    (typed : VE.TupleTyped M.asStructure ss vs) (hw : ψ.eval (M.withFill F) (tupleVal vs) = true)
    (he : embeddable V M = true) (hs : witnessSafe U V X ψ = true) :
    CalendarReading V (completion V M (numbering V M)) (numOf (numbering V M)) ∧
      BaseAdmissibleX U (X ++ eventsX V) (completed U V M (finFill M F)) ∧
      VE.TupleTyped (completed U V M (finFill M F)) ss (vs.map Sum.inl) ∧
      ψ.denote (completed U V M (finFill M F)) (tupleVal (vs.map Sum.inl))

/-- SETTLED in the situation is SETTLED in its completion, and the filled completion is an admissible situation
    of the whole assembled X (SR-B3: the review's `∃ F'`, with its witness named), so the answer is about a
    situation of the document, never vacuous. -/
theorem events_settled_calendar (U : UDoc) (h : WellFormedU U = true) (V : EventsEnv) (X : List VE.Formula)
    (hT : EventsTyped (envAt U.D 0) V = true) (M : VE.FiniteModel VE.Bridge.Entity)
    (valid : M.Valid (envAt U.D 0)) (hb : VE.Norms.backgroundValid U.D M = true) (he : embeddable V M = true)
    (F : FiniteFill U VE.Bridge.Entity) (hF : fillValid U M F = true)
    (hX : extraValid U (X ++ eventsX V) M F = true)
    (r : Regulated) (vs : List VE.Bridge.Entity) (b : Bool) (hset : SettledAs.{0} U M.asStructure r vs b)
    (hs : settledSafe U V X r.name = true) :
    CalendarReading V (completion V M (numbering V M)) (numOf (numbering V M)) ∧
      SettledAs.{0} U (completion V M (numbering V M)) r (vs.map Sum.inl) b ∧
      BaseAdmissibleX U (X ++ eventsX V) (completed U V M (finFill M F))

/-- UNDECIDED in the situation is UNDECIDED in its completion, both fillings extended over the same completed
    base (SR-B1). -/
theorem events_undecided_calendar (U : UDoc) (h : WellFormedU U = true) (V : EventsEnv) (X : List VE.Formula)
    (hT : EventsTyped (envAt U.D 0) V = true) (M : VE.FiniteModel VE.Bridge.Entity)
    (valid : M.Valid (envAt U.D 0)) (he : embeddable V M = true)
    (r : Regulated) (vs : List VE.Bridge.Entity) (F₁ F₂ : FillTables U M.asStructure)
    (h₁ : BaseAdmissibleX U (X ++ eventsX V) (withFill U M.asStructure F₁))
    (h₂ : BaseAdmissibleX U (X ++ eventsX V) (withFill U M.asStructure F₂))
    (v₁ : (outcomeBase (fill U) r.name).denote (withFill U M.asStructure F₁) (tupleVal vs))
    (v₂ : ¬ (outcomeBase (fill U) r.name).denote (withFill U M.asStructure F₂) (tupleVal vs))
    (hs : undecidedSafe U V X r.name = true) :
    CalendarReading V (completion V M (numbering V M)) (numOf (numbering V M)) ∧
      BaseAdmissibleX U (X ++ eventsX V) (completed U V M F₁) ∧
      BaseAdmissibleX U (X ++ eventsX V) (completed U V M F₂) ∧
      (outcomeBase (fill U) r.name).denote (completed U V M F₁) (tupleVal (vs.map Sum.inl)) ∧
      ¬ (outcomeBase (fill U) r.name).denote (completed U V M F₂) (tupleVal (vs.map Sum.inl))

structure EventsEntailmentReplay where
  U : UDoc
  V : EventsEnv
  E : VE.Environment
  X : List VE.Formula
  premises : List VE.Formula
  conclusion : VE.Formula
  valid : Bool

def replayEventsEntailment (j : Lean.Json) : Except String EventsEntailmentReplay

/-- The wire: a replayed entailment decodes to exactly this block and holds with its premises. -/
theorem events_wire_acceptance (j : Lean.Json) (r : EventsEntailmentReplay) (h : replayEventsEntailment j = .ok r)
    (hv : r.valid = true) :
    (decodeEvents (j.getObjValD "environment")).map (·.map (fun d => (d.V, d.E))) = .ok (some (r.V, r.E)) ∧
      EntailsX.{u} r.U (r.X ++ eventsX r.V) r.premises r.conclusion
```

The four answer-level theorems state their situation explicitly (SR-B1): the filled completion `completed U V M F`
of the situation's own filling (for UNDECIDED, of each of its two fillings, over the same completed base). The
calendar reading is stated on the base completion; `completed` has its carrier, days, `before` and named dates,
since `withFill` changes only the unsaid tables. The calendar check is therefore taken on the base `M` (`he`), which
gives the same answer as on `M.withFill F`, whose only extra tables are unsaid ones.

`events_wire_acceptance` is instantiated per route that enables the profile, as nd's wire theorems are; the readings
route uses the same `X` per choice (RD-9's `choiceX`). **`events_row_composition`** (stated against AR-10's names
when its table lands): for every profile list the `events@0` row admits, the route chosen is the one chosen for the
list without `events@0`, with the `events` pack added to `X`; every list it refuses is refused with its text, before
any events check (4, item 1).

### 6.4 `alternatives@0` with the completion (ET-7)

```lean
namespace VE.Alternatives
open VE.NormDefaults (UDoc fill WellFormedU BaseAdmissibleAltU backgroundBaseAltU allFollowableU
  followableFU clearFU FiniteFill fillValid FillTables withFill)
open VE.NormDefaults.Wire (hasProfile unspecifiedNames placeholderJson checkAuthor)

structure AltSourceU where
  src : Wire.AltSource
  unspec : List String          -- the regulated predicates whose `default` is "unspecified", in regulated order

/-- `decodeSourceU`'s two branches (SR-A2). With `norm-defaults@0`: today's gate on the original profile list
    (`profileGate`), the placeholders (`placeholderJson` sets the profile aside), today's decoder on the result (the
    rest of the profile list, the block, the rules, Γ), then the reserved names and author limits of nd 8 and
    `WellFormedU`. Without it: an `unspecified` value is refused, and otherwise today's decoder runs unchanged. -/
def decodeAltSourceU (environment norms premises : Lean.Json) : Except String AltSourceU :=
  if hasProfile environment then do
    let _ ← Wire.profileGate environment
    let src ← Wire.decodeAltSource (← placeholderJson environment) norms premises
    let unspec := (src.A.T.regulated.map (·.name)).filter ((unspecifiedNames environment).contains ·)
    checkAuthor environment ⟨inlineTree src.A, unspec⟩
    unless WellFormedU ⟨inlineTree src.A, unspec⟩ do
      throw "InvalidInput: norm-defaults document is not well formed"
    pure ⟨src, unspec⟩
  else do
    unless (unspecifiedNames environment).isEmpty do
      throw "UnsupportedProfile: unspecified completion requires norm-defaults@0"
    let src ← Wire.decodeAltSource environment norms premises
    pure ⟨src, []⟩

def noUnspecified (environment : Lean.Json) : Bool :=
  !hasProfile environment && (unspecifiedNames environment).isEmpty

def notFollowableFU (A : AltDoc) (unspec : List String) : VE.Formula := .not (followableFU A unspec)

/-- No `unspecified` value and no `norm-defaults@0`: today's decoder, texts included (by unfolding the second
    branch, as `decode_conservative`). -/
theorem decodeAltSourceU_conservative (environment norms premises : Lean.Json)
    (h : noUnspecified environment = true) :
    decodeAltSourceU environment norms premises =
      (Wire.decodeAltSource environment norms premises).map (fun s => AltSourceU.mk s [])

/-- Conflict freedom over the route's own base, the slot premises included, as `AltConflictFree` is over
    `BaseAdmissibleAlt` (SR-A3). -/
def AltConflictFreeU (A : AltDoc) (unspec : List String) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleAltU A unspec B → VE.Norms.ConflictFree (fill ⟨inlineTree A, unspec⟩) B

structure FollowableUReplay where
  src : AltSourceU
  followable : Bool             -- CONFLICT-FREE first, then the certificate, as `FollowableReplay.followable`

def replayFollowableU (j : Lean.Json) : Except String FollowableUReplay

/-- FOLLOWABLE on the wire, with the completion (`followableU_sound` applied to the replayed source). -/
theorem alternativesU_wire_followable_sound (j : Lean.Json) (res : FollowableUReplay)
    (h : replayFollowableU j = .ok res) (hv : res.followable = true) :
    decodeAltSourceU (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "premises") = .ok res.src ∧
    WellFormedU ⟨inlineTree res.src.src.A, res.src.unspec⟩ = true ∧
    AltConflictFreeU.{u} res.src.src.A res.src.unspec ∧
    ∀ B : VE.Structure.{u}, BaseAdmissibleAltU res.src.src.A res.src.unspec B → VE.Norms.Sat B res.src.src.A.Γ →
      (allFollowableU res.src.src.A res.src.unspec).denote B []

/-- DILEMMA: a valid witness, a validated filling and a typed chooser at which ¬followable° holds refute the
    document-wide claim. `hA` types Γ over the base vocabulary, which declares no unsaid predicate, so Γ holds in the
    filled witness (`withFill_agrees`); the base and slot premises hold there by `admissible_of_fillValid` and
    `withFill_agrees` (SR-A1). -/
theorem alternativesU_dilemma_witness_sound {α : Type u} [DecidableEq α] (A : AltDoc) (unspec : List String)
    (hA : WellFormedAlt A = true) (h : WellFormedU ⟨inlineTree A, unspec⟩ = true) (M : VE.FiniteModel α)
    (F : FiniteFill ⟨inlineTree A, unspec⟩ α) (valid : M.Valid (VE.Norms.envAt (inlineTree A) 0))
    (hb : backgroundValidAlt A M = true) (hfill : fillValid ⟨inlineTree A, unspec⟩ M F = true)
    (hΓ : A.Γ.all (fun p => p.eval M []) = true) (r : α) (typed : r ∈ M.domains A.alt.chooser)
    (hd : (notFollowableFU A unspec).eval (M.withFill F) (VE.Norms.tupleVal [r]) = true) :
    ¬ (∀ B : VE.Structure.{u}, BaseAdmissibleAltU A unspec B → VE.Norms.Sat B A.Γ →
        (allFollowableU A unspec).denote B [])

def SettledF (A : AltDoc) (unspec : List String) (B : VE.Structure.{u}) (φ : VE.Formula) (vs : List B.Carrier)
    (b : Bool) : Prop :=
  ∀ F : FillTables ⟨inlineTree A, unspec⟩ B, BaseAdmissibleAltU A unspec (withFill ⟨inlineTree A, unspec⟩ B F) →
    (φ.denote (withFill ⟨inlineTree A, unspec⟩ B F) (VE.Norms.tupleVal vs) ↔ b = true)

def UndecidedF (A : AltDoc) (unspec : List String) (B : VE.Structure.{u}) (φ : VE.Formula)
    (vs : List B.Carrier) : Prop :=
  ∃ F₁ F₂ : FillTables ⟨inlineTree A, unspec⟩ B,
    BaseAdmissibleAltU A unspec (withFill ⟨inlineTree A, unspec⟩ B F₁) ∧
    BaseAdmissibleAltU A unspec (withFill ⟨inlineTree A, unspec⟩ B F₂) ∧
    φ.denote (withFill ⟨inlineTree A, unspec⟩ B F₁) (VE.Norms.tupleVal vs) ∧
    ¬ φ.denote (withFill ⟨inlineTree A, unspec⟩ B F₂) (VE.Norms.tupleVal vs)

inductive AltStatus
  | clear
  | notClear
  | undecided
  | unknown

/-- A scenario row: the scenario's validity, today's (its model, its background with the slot premises, its signed
    rows, the existence checks and Γ), a typed chooser and action, and one filling validated by `fillValid`, so that
    no status is vacuous (SR-A4); then the evidence its status needs (C). `unknown` needs no more. -/
structure ScenarioRowU (A : AltDoc) (unspec : List String) where
  M : VE.FiniteModel VE.Bridge.Entity
  rows : List Row
  chooser : VE.Bridge.Entity
  action : VE.Bridge.Entity
  status : AltStatus
  valid : M.Valid (VE.Norms.envAt (inlineTree A) 0)
  background : backgroundValidAlt A M = true
  checked : validateAlternatives A M rows = .ok ()
  chooser_typed : chooser ∈ M.domains A.alt.chooser
  action_typed : action ∈ M.domains A.alt.action
  F : FiniteFill ⟨inlineTree A, unspec⟩ VE.Bridge.Entity
  filled : fillValid ⟨inlineTree A, unspec⟩ M F = true
  clear_sound : status = .clear → SettledF.{0} A unspec M.asStructure (clearFU A unspec) [chooser, action] true
  notClear_sound : status = .notClear →
    SettledF.{0} A unspec M.asStructure (clearFU A unspec) [chooser, action] false
  undecided_sound : status = .undecided → UndecidedF.{0} A unspec M.asStructure (clearFU A unspec) [chooser, action]
```

`clearFU`'s variable 0 is the action and variable 1 the chooser, so the tuple `[chooser, action]` reads through
`tupleVal`. With `valid`, `background` and `filled`, `admissible_of_fillValid` and `withFill_agrees` give an
admissible filling of `M` (`BaseAdmissibleAltU`), so `SettledF` is never vacuous. The scenario function that builds
rows (`scenarioRowU`) is the batch's: today's validation of the scenario (its text on failure), the typed chooser and
action (today's `InvalidInput: <x> is not in the <s> domain` otherwise), a filling checked by `fillValid` (when none
is, the scenario has no rows and answers UNKNOWN for every alternative), then Kleene (`kleene_sound`), then
enumeration of the cone, then the untrusted search's two fillings checked by `fillValid`; any other outcome is
`.unknown`.

### 6.5 Pruning (optional; J)

Leaving out the order premises when no formula needs them is an optimisation, not a promised fallback. A batch that
takes it writes its own statement, under its own review, with preservation conditions over **declarations as well as
formulas**: two declared dates and "all days are equal" are inconsistent with the full pack but not without its order
premises, and the proof must put a linear order on any day domain, which `events_conservative`'s expansion does not
give. Until then, if ET-6's bar fails, the fallback stands: the block is not added to that part, and that is reported.

## 7. Not claimed; limits

- The truth of any link or of any day an event is said to happen on; durations over events; deadline fulfilment;
  branching time; order within a day (`time-of-day`: same-day facts never make a point UNDECIDED, E).
- A refutation outside the completion fragment: UNKNOWN, never false (A).
- Completeness outside norms 7.1 (B), and any conservativity beyond `events_conservative`'s `oldEnv` (X2).
- Persistence of a state without a stated end (F).
- A status on a situation with no validated filling (none passes `fillValid` and `extraValid` over the whole
  assembled `X`): UNKNOWN, never SETTLED (SR-B3).
- "within n days of <event>" (ET-T1); "within n days of D" only as the reading set W1 to W3 of 2.4, with both end
  dates named (SR-B4).
- A consequence that needs counting the days between two named dates more than one day apart: UNKNOWN unless a
  certificate gives it (only the one-day gap has a premise).
- Dates before 1970 (ET-T3); `events@0` with `data@0` (ET-T4).
- Limits: at most 64 named dates; each generated premise within `MAX_NODES`; ET-7's enumeration within
  `MAX_UNSAID_ATOMS`.

## 8. Acceptance fixtures

### 8.1 Definitions

Synthetic, `#guard` in Lean where marked, and the same cases through the service in Python. The block `base dates`
has day sort `day`, predicate `before`, and no events, states or links; `chain days names` is a situation whose days
are in `before` order and whose named dates denote the given days.

| # | Definition |
|---|---|
| T1 | `base [2026-10-12, 2027-01-05]`: the premises' labels; `datesOrder_iff` for (2026-10-12, 2027-01-05) and the reverse; `datesOrder_calendar` for the same pairs |
| T2 | `base [2026-10-12, 2026-10-13]`: labels; the claim "there is a day such that that day is after 12 October 2026 and that day is before 13 October 2026" |
| T2b | `base []`; the claim "for each day and each day, if neither day is before the other, the two days are the same day"; then `linearF` dropped |
| T3 | `base [2026-10-12, 2026-10-14]`; `chain` with 3, 2, 1 and 0 unnamed days between the two named days; with the named dates swapped; with only 12 October named (this last case a Lean `#guard` on `calendarCheck` only, not through the service: SR-B5) |
| T3b | T3's block, the situation with no day between the named days, the claim of T2 with 14 for 13 October; then the situation with one day between |
| T3c | `base [2026-10-12]`, a situation whose only day is 12 October, the claim "there is a day such that that day is after 12 October 2026" |
| T3d | an event sort `act` (`committed_on`) beside T3c's block; the claim "there is an act and a day such that that act is committed on that day and that day is after 12 October 2026", in a situation with no act |
| T3e | the edges: `base [1970-01-01]` with one day below the named day, then with one day above it; `base [9999-12-31]` with one day above |
| T4 | event sort `act`, role `committed_on`; a situation with one act on two days, then on one day |
| T5 | state sort `marriage`; a situation in which a marriage ends before it begins, then on the day it begins |
| T6 | links `contributed_to` (act → act), `contributed_to_state` (act → marriage), `necessary_for` (act → act): the effect act before the cause act; a cause act after the marriage's last day; a cause act after the marriage began and before it ended; a cause act with a marriage that has no last day |
| T7 | a document with no day vocabulary in any rule or premise, with and without the block |
| T8 | every existing fixture without the block; one with it |
| T9 | each wording of 2.2; the role wordings "{0} is committed on {1}", "{0} happens on {1}", "{0} committed {1}", "{0} on {1}", "{0} happens on {1} to {0}", "{0} is {1} on {1}"; each pattern of 2.5 in authored text |
| T10 | 64 and 65 named dates; the date 1969-12-31; a declared constant `date__x`; a date given twice |
| T11 | the permission "until": U1 "Every person may be presumed innocent on each day, if it is not the case that there is a conviction such that that conviction is of that person and that conviction happens no later than that day." with `presumed_innocent_permitted(person, day)` unspecified; U2 adds "Every person must not be presumed innocent on each day, if there is a conviction such that that conviction is of that person and that conviction happens no later than that day."; dates 4, 5 and 7 January 2027; a conviction of P on 5 January 2027; the status of P on each of the three days under U1 and under U2 |
| T11b | the obligation "until": U1 "Every agent must file a report on each day, if it is not the case that there is a closure such that that closure is of that agent and that closure happens no later than that day." on `x_required(agent, day)`, `x_permitted` its pair, both unspecified; U2 adds "Every agent need not file a report on each day, if there is a closure such that …"; a closure of A on 5 January 2027; A on 7 January 2027 |
| T11c | "valid until 31 December 2026" on a permission; the four candidates of 2.4; days 31 December 2026 and 1 January 2027 |
| T11d | "within" (SR-B4): the source clause "the act is committed within 10 days of 5 January 2027" on event sort `act` (`committed_on`); named dates 26 December 2026 and 1, 5 and 15 January 2027; candidates W1 "that act is committed on or after 5 January 2027, and that act is committed no later than 15 January 2027", W2 the same with "before 15 January 2027", W3 the same as W1 with "26 December 2026" for "5 January 2027"; situations: one act committed on 15 January 2027, one on 1 January 2027, one on 5 January 2027; then the clause "within 10 days of the conviction" |
| T12 | ET-7: nd fixture u10 (chooser R; pull forbidden by a rule, push with no rule; `permitted` unspecified); then with "Every action may be performed, if that action is push." |
| T12b | ET-7: push's permission given by the rule "Every action may be performed, if that agent may Y, or it is not the case that that agent may Y." (nd u12's guard), `y_permitted` unspecified; then with `MAX_UNSAID_ATOMS = 0` |
| T12c | ET-7, SR-A1 (Astra's regression): one chooser R, actions a1 and a2 both available to R, the permission member `allow`, the obligation member unspecified with its fulfilment declared, no rules, and Γ = [`allFollowableU A unspec`] as a Lean term; the unfilled model, and its filling that requires both actions |
| T12d | ET-7, SR-A2 and R-A2, the decoder: `{"profiles":[]}`; T12's environment with `norm-defaults@0` removed and `unspecified` kept; then, with `norm-defaults@0`: the profile listed twice; an unknown profile `zzz@0`; a declared predicate `unsaid__x`; an unspecified predicate whose name is 57 bytes long; a document that passes the author checks and fails `WellFormedU` (taken from nd's fixtures) |
| T12e | ET-7, SR-A3 and R-A3: T12's document with a rule pair that requires and forbids performing an action exactly when it is available to two different choosers, which the slot premise `alternatives:own` excludes |
| T12f | ET-7, SR-A4 and R-A4: T12's document with a scenario in which push is available to R and to a second chooser R2 (so no filling is admissible: the slot premise fails); then a scenario whose chooser names an entity of the action domain |
| T13 | events `confirmation`, `action`; "that confirmation happens before that action"; a confirmation on 12 October 2026 and the action on 13 October 2026; then both on 13 October 2026 |
| T14 | SETTLED on the events chain (SR-B3): T11's U1 document, the status of P on 4 January 2027 by `table3`, in four situations: (a) the conviction of P on both 4 and 5 January 2027, the canonical filling supplied; (b) with `soft-norms@0` and a soft premise, read on base predicates only, that the situation violates, the canonical filling supplied; (c) Astra's case: no conviction, and the declared literals `P` and `Q` interpreted as the same person; (d) with `soft-norms@0` and a soft premise, read through the outcome of `presumed_innocent_permitted`, that every filling of the situation violates, no filling supplied |
| F1 | the fragment functions on the formulas of T3b, T3c, T3d, R1's claim and their negations; the conventions of T6's block; its calendar premises |
| R1 | the norms chain (`documents@1`, `events@0`, `norm-defaults@0`, `norms@0`, `relational-fol@0`); state sort `stay` (`stay_begins`, `stay_ends`); dates 2026-06-29, 2026-09-20, 2026-09-21, 2026-09-26, 2026-09-27; per case, the claim "that stay is in progress on each day from 21 September 2026 through 27 September 2026": C25 (begins 2026-06-29, ends 2026-09-26), C26 (begins 2026-06-29, ends 2026-09-27), C27 (begins 2026-06-29, ends 2026-09-20), C28 (begins 2026-06-29, no end stated), C28n (C28 with the premise "there is no day such that that stay ends on that day") |
| R2 | asimov-laws with `permitted` switched to `unspecified` (ET-8) |

Pilot fixtures P1 to P11 are the plan's 4.2, unchanged except P6 (the reading set {U1, U2} of T11), P8 (the role
wording "{0} is committed on {1}") and P9 (rechecked under the link conventions); their expectations depend on the
audits and are stated there.

### 8.2 Expectations

| # | Expected | |
|---|---|---|
| T1 | labels `events:irreflexive`, `events:transitive`, `events:linear`, `events:date:2026-10-12:2027-01-05`; no adjacency. `before(c_2026_10_12, c_2027_01_05)` certified, and its reverse refuted by certificate (transitivity and irreflexivity); `datesOrder_calendar` true and true for the pair, false and false for the reverse | *guarded* (labels, the two `num` comparisons); certificates *derived* (ET-3) |
| T2 | labels as T1's with `events:date:2026-10-12:2026-10-13` and `events:adjacent:2026-10-12:2026-10-13`; the claim refuted by certificate (adjacency) | labels *guarded*; certificate *derived* |
| T2b | certified; with `linearF` dropped (ET-3's seeded bug) the certificate is not accepted. T2's certificate does not need `linear` (I) | *derived* |
| T3 | 3 days: `NotCalendar: 3 days between 2026-10-12 and 2026-10-14, at most 1`; 2 days: `NotCalendar: 2 days between 2026-10-12 and 2026-10-14, at most 1`; 1 day and 0 days: accepted, the unnamed day numbered as 13 October 2026; swapped: `NotCalendar: 2026-10-12 is not before 2026-10-14`; only 12 October named: `NotCalendar: 2026-10-14 denotes no day` (`#guard` only: a valid situation cannot reach it, 4) | *guarded* |
| T3b | the claim is never refuted: UNKNOWN with `NotCalendar: the conclusion may change when the missing calendar days are added` (its `down` is false); in the situation with one day between, the claim holds and the model is reported, completed | fragment *guarded*; answers *derived* (ET-4) |
| T3c | never refuted: UNKNOWN with `NotCalendar` as T3b | fragment *guarded*; answer *derived* |
| T3d | refuted: NOT ENTAILED, with the completed calendar situation (its `down` is true) | fragment *guarded*; answer *derived* |
| T3e | `NotCalendar: 1 day before 1970-01-01, at most 0`; one day above 1970-01-01: accepted; `NotCalendar: 1 day after 9999-12-31, at most 0` | *guarded* |
| T4 | `InvalidModel(events): the model violates a background premise`, detail `events:one_day:act`; one day: accepted | *derived* |
| T5 | the same text, detail `events:not_before_begin:marriage`; on the day it begins: accepted | *derived* |
| T6 | effect before cause: detail `events:link_forward:contributed_to`; cause after the last day: detail `events:link_forward:contributed_to_state`; cause during the marriage: accepted; marriage with no last day: accepted (the bound binds only when the state ends). Labels: `events:one_day:act`, `events:one_begin:marriage`, `events:one_end:marriage`, `events:not_before_begin:marriage`, `events:link_forward:contributed_to`, `events:link_forward:contributed_to_state`, `events:link_forward:necessary_for`, `events:link_weaker:necessary_for:contributed_to` | labels *guarded*; answers *derived* |
| T7 | the same statuses and verdicts with and without the block; certificates differ only in their bound premise list (`events_conservative`, both directions) | *derived* |
| T8 | without the block: `environment_id` and every hash unchanged; with it: `environment_id` changes; `decodeEvents` gives `none` exactly when the block is absent | *derived* |
| T9 | one derivation each; role wordings: the first two accepted, the other four `EventsVerbalisation`; each pattern rejected with its advice | role wordings *guarded*; the rest *derived* (ET-5) |
| T10 | 64 dates well formed, 65 `ResourceLimit: events dates`; `DateRange(1969-12-31)`; `EventsReserved: date__x`; `DuplicateDeclaration: date 2026-10-12` | 64/65, `DateRange` and the duplicate *guarded*; texts *derived* |
| T11 | 6 calendar premises (3 order, 2 date, 1 adjacency: 4 and 5 January). 4 January: SETTLED yes under U1 and U2 (with a validated filling of the whole assembled `X`, SR-B3). 5 and 7 January: U1 UNDECIDED (the text does not say), U2 SETTLED no. The three days form the distinguishing situation; E's own day is in it | count *guarded*; statuses *derived* (ET-4) |
| T11b | U2: `x_required` SETTLED no on 7 January; `x_permitted` UNDECIDED there, never SETTLED no (the obligation stops; nothing is forbidden). U1: `x_required` UNDECIDED on 7 January. The UNDECIDED answers and their fillings are reported through the canonical extension (SR-B1): the body of each fill premise is `up`, its day quantifier is not | *derived* |
| T11c | 31 December 2026 tells the exclusive candidates from the inclusive ones; 1 January 2027 tells "silent" from "ends" | *derived* |
| T11d | 15 January 2027: W1 and W3 true, W2 false; 1 January 2027: W3 true, W1 and W2 false; 5 January 2027: all three true (not distinguishing). The reading set shows the first two situations. The end dates: 15 January 2027 is 10 days after 5 January 2027, and 26 December 2026 is 10 days before it (`Civil.num` 20833, 20823 and 20813). "within 10 days of the conviction": UNFORMALISED, reason `duration` | end dates *guarded*; truth values *derived* (ET-5) |
| T12 | DILEMMA; push UNDECIDED from two validated fillings; diagnosis `UNSETTLED(push)`; with the push rule FOLLOWABLE | *derived* (ET-7) |
| T12b | Kleene unknown; enumeration settles push clear; never UNDECIDED; with `MAX_UNSAID_ATOMS = 0`: UNKNOWN naming the budget | *derived* (ET-7) |
| T12c | `WellFormedAlt A` is false (Γ names an unsaid predicate, which `envAt (inlineTree A) 0` does not declare), so `alternativesU_dilemma_witness_sound` has no instance here. Without `hA` its statement is false here: the unfilled model satisfies Γ (no action is required), the filling that requires both actions passes `fillValid` and leaves R with no clear action, and the conclusion would deny "Γ implies Γ". Such a Γ cannot be written on the wire: the decoder types premises over the base vocabulary | *derived* (ET-7) |
| T12d | `{"profiles":[]}`: `UnsupportedProfile: alternatives@0 is required`, today's text (the two decoders agree). `unspecified` without the profile: `UnsupportedProfile: unspecified completion requires norm-defaults@0`. With the profile: listed twice, `UnsupportedProfile: profiles must be sorted and unique`; `zzz@0`, `UnsupportedProfile: Unsupported profile zzz@0`; `unsaid__x`, `InvalidInput: reserved name unsaid__x`; the 57-byte name, `ResourceLimit: unspecified name length`; the ill-formed document, `InvalidInput: norm-defaults document is not well formed` | the first *guarded*; the rest *derived* (ET-7) |
| T12e | CONFLICT-FREE: no conflict in any structure of `BaseAdmissibleAltU` (`AltConflictFreeU`), so FOLLOWABLE or DILEMMA may follow. The conflict lives only in structures that violate `alternatives:own`, so draft 1's `ConflictFreeU`, which drops the slot premises, is false here | *derived* (ET-7) |
| T12f | first: today's validation text, `InvalidModel(alternatives): action push is available to two choosers: R, R2`; second: today's `InvalidInput: <x> is not in the <s> domain`, `<s>` the chooser sort; for neither is any alternative clear or not clear | *derived* (ET-7) |
| T13 | first: certified; second: its negation certified (the same day is not before); never UNDECIDED | *derived* |
| T14 | (a) `InvalidModel(events): the model violates a background premise`, detail `events:one_day:conviction`; (b) `InvalidModel(soft): the model violates a background premise`; (c) `InvalidModel(literals): the model violates a background premise` (without `hb` SETTLED would hold vacuously: no filling satisfies the base background, and the completion keeps the two constants equal); (d) UNKNOWN, no filling validated. None is SETTLED | *derived* (ET-4) |
| F1 | `down` false and `up` true for T3b's claim; `down` false for T3c's; `down` true for T3d's; for R1's claim `down` true and `up` false; for T3b's negation `up` false and `down` true; every convention of T6's block `up` and `down`; T6's block's calendar premises not all `up` | *guarded* |
| R1 | 9 calendar premises (3 order, 4 date, 2 adjacency: 20/21 and 26/27 September). C26: in progress throughout, certified. C25 (not in progress on 27 September) and C27 (not on 21 September): the negation certified. C28: not entailed, with a calendar countermodel (the stay ends between 21 and 27 September); its negation is not certified, and the countermodel to it (a situation where the stay never ends) is outside the fragment, so that answer is UNKNOWN with `NotCalendar: the conclusion may change when the missing calendar days are added`. C28n: in progress throughout, certified. Matches the answer key: C26 throughout, C25 and C27 not | count and adjacency labels *guarded*; answers *derived* (ET-5) |
| R2 | the README's measured bound becomes the computed result: clear actions only where a rule permits; `UNSETTLED(...)` only with two validated fillings | *derived* (ET-8) |

The "exactly when" claims and their two directions: `datesOrder_iff` and `datesOrder_calendar` (T1, both orders);
adjacency exactly for consecutive day numbers (T2 has it, T3 has none); `embeddable` exactly when an embedding exists
(T3 and T3e, failing and passing); "is in progress on" exactly when begun and not ended before (R1, C26 against C25
and C27); `link_forward` for a state effect exactly when the state ends (T6, the last two cases); U1 and U2 differ
exactly from E's day (T11, 4 January against 5 and 7 January); UNDECIDED exactly with two validated fillings (T12
against T12b); `decodeEvents` gives no pack exactly when the block is absent (T8); conservativity both ways (T7);
SETTLED exactly on a situation of the document with a validated filling of the whole assembled `X` (T11 against
T14); W2 against W1 and W3 exactly on the end date, W3 against W1 and W2 exactly before D (T11d);
`decodeAltSourceU` is today's decoder exactly without the profile and without `unspecified` (T12d).

## 9. Review checklist

1. Is `CalendarReading` (with `onto`) the intended reading, and does the completion (`completion_reading`) realise
   every civil day, in the gaps and at both edges?
2. Is `dayExtension_transfer` true as stated, for every case of `hits`, `vacuous`, `up` and `down`, and is
   `completion_extension` true with `ng = [before]`?
3. Does 1.8's table cover every formula each answer's check reads (other packs' `X`, `Fill_T`, the base background,
   the expanded rules and definitions, the conclusion), and is each route-level statement of 6.3 true? In particular
   `fillPremises_canonical_completion` with `Fill_T` tested through its bodies (SR-B1), and SETTLED's hypotheses
   `hb`, `hF`, `hX` with its conclusion over the whole `X` (SR-B3)?
4. Are T3b and T3c never refuted, and is R1 inside the fragment as 1.8 says?
5. Are the conventions exactly the plan's (D4, D10), each universal, and `conventions_exact`?
6. Is each wording of 2.2 one reading, and do 2.4's candidates and 2.5's advice say what to write?
7. Is "until" right per modality (2.4, T11, T11b), with E's own day and the inclusive date readings?
8. Is ET-7's contract (5, 6.4) nd 2.5's rule, with no UNDECIDED from Kleene alone, and are SR-A1 to SR-A4 right:
   `WellFormedAlt A` in DILEMMA, the decoder's two branches, `AltConflictFreeU` over `BaseAdmissibleAltU`, and the
   scenario row's validity and filling?
9. Is the profile row (1.1) right, in particular refusing `data@0` and `alternatives@0`?
10. Is the pack's kind (1.11) and its condition what X2 requires?

## 10. Differences from the plan's blocks

- **Calendar readings** are split: `Embeds` (draft 1's `CalendarReading`, which a finite situation has) and
  `CalendarReading` (with `onto`, the intended reading). Both are `Prop` definitions over a numbering, so the
  numbering is named in statements.
- **New**: the completion, `DayExtension`, the fragment functions, `dayExtension_transfer`, `completion_*`,
  `conventions_exact`, `embeddable_complete`, and the four answer-level theorems, replacing
  `events_countermodel_calendar` (A, X2).
- **Order of premises**: the calendar premises first, then the conventions; draft 1's 2.3 interleaved them, its 3.1
  did not. The conventions are in guarded form.
- **`EventsTyped`** on the regenerated environment, with `regen_typed`; the later statements assume it, not
  `WellFormedEvents` on the regenerated environment (whose date-freshness test would fail there).
- **`Link`** carries its cause and effect sorts, decoded from the predicate's signature.
- **`calendarCheck`** returns the diagnostic text; `embeddable` is its `isNone`. `numbering` is named.
- **`eventsX_absent`** is stated on the decoder (no pack); PK-1's assembler does the rest (X1). `assembleX` is gone.
- **`decodeAltSourceU`** takes the alternatives decoder's three inputs (`environment`, `norms`, `premises`), not two.
- **`alternativesU_dilemma_witness_sound`** types the chooser by `r ∈ M.domains A.alt.chooser` (there is no
  `inDomain`).
- **Scenario rows** carry their evidence (`ScenarioRowU`, `SettledF`, `UndecidedF`), replacing "the three values come
  from Kleene evaluation" (C).
- **Diagnostic texts** reuse the existing owners: `parseIso`'s `DateRange(<iso>)` (not `DateRange: <iso>`), and the
  layered route's `InvalidModel(<pack>): the model violates a background premise` with the label as detail (not
  `InvalidModel("events", "premise … fails")`).
- **Named dates' verbalisation** is the ISO form, read and rendered by W6's literal class, so events holds no month
  table.
- **`embeddable_sound`** assumes no calendar premise of the situation (the plan's `hp` is gone, SR-B2).
- **The answer-level theorems** name their situation, the filled completion `completed` (SR-B1), take the calendar
  check on the base `M`, and SETTLED takes the situation's background check, a validated filling and `X` (SR-B3).
- **`decodeAltSourceU`** has `decodeSourceU`'s two branches (SR-A2); the wire theorem concludes `AltConflictFreeU`
  (SR-A3); DILEMMA assumes `WellFormedAlt A` (SR-A1).

## 11. Elaboration record

- The stub `SpecStubs_events-time-causation.lean` holds every definition and statement of 6 and the *guarded*
  fixtures of 8. Draft 2's stub is the untracked `lean/SpecStubs_events-time-causation.lean` of this branch's
  worktree (`ve-design-events-time-causation`), with draft 2's statements and the new *guarded* values (T11d's end
  dates, T12d's first case). It has **not been run**: draft 1's session could not run `lake` and `lean`, and draft
  2's worktree has no build. It is not committed. The copy at
  `manage-agents/debates/design-events-time-causation/SpecStubs_events-time-causation.lean` is draft 1's; the run
  uses the worktree's stub.
- PASS needs this record filled in: the command, its log (kept beside the stub copy) and the commit of this file the
  reviewers accepted. Elaborating is necessary, not sufficient.
- To elaborate: copy it to `lean/` in a checkout of this branch with the build of `main` at `49de179e` (or later),
  then `cd lean && PATH=~/.elan/bin:$PATH lake env lean SpecStubs_events-time-causation.lean`. It imports
  `VE.NormDefaults.{Layered,Routes}`, `VE.Alternatives.{Wire,Background}` and `VE.Time.Calendar`. Expected: no
  error; every `#guard` passes; `datesOrder_calendar` is proved in the stub. Delete the copy afterwards; never commit
  it.
- RD-9's `premisesX`, `EntailsX` and `modelCheckX` are copied into the stub from `rd-9/integrate` at `321e610a`;
  PK-1's `Pack` is stated as the synthesis defines it. When either lands under other names, 6.3 is renamed to match.
- If the run reports an error, the statement is corrected here and in the stub before the review starts; a wrong
  `#guard` value is corrected in 8.2 from the `#eval` of the same expression.

## 12. Changes in draft 2 (the statement review's FIX)

ET-7 (5, 6.4):

- **SR-A1.** `alternativesU_dilemma_witness_sound` assumes `WellFormedAlt A`, as `dilemma_witness_sound` does: without
  it Γ may name unsaid predicates, hold before the filling and fail after it. Astra's counterexample is T12c.
- **SR-A2.** `decodeAltSourceU` takes `decodeSourceU`'s two branches: without the profile, `unspecified` is refused and
  today's decoder runs unchanged; with it, today's gate on the original profile list, the placeholders, today's
  decoder, then `checkAuthor` and `WellFormedU`.
  Draft 1 called `placeholderJson` first, so `{"profiles":[]}` failed on the missing vocabulary instead of today's
  text, and the equation `decodeAltSourceU_conservative` was false. Fixtures T12d (R-A2).
- **SR-A3.** The wire theorem concludes `AltConflictFreeU`, over `BaseAdmissibleAltU` with the slot premises, not
  nd's `ConflictFreeU`, which drops them; CONFLICT-FREE stays the prerequisite of FOLLOWABLE and DILEMMA. Fixture
  T12e (R-A3).
- **SR-A4.** `ScenarioRowU` carries the scenario's validity (`valid`, `background`, `checked` with the signed rows),
  the typed chooser and action, and a filling that passes `fillValid`, so `SettledF` is never vacuous. Fixture T12f
  (R-A4).

Events (1.6 to 1.8, 2.4, 4, 6.2, 6.3, 7, 8):

- **SR-B1.** `Fill_T`'s day quantifier is never guarded, so draft 1's `up` test failed on every day-indexed pair with
  an unspecified member, and T11b's UNDECIDED answers could not be reported. The completion now extends a filling
  canonically on tuples with an added day (`completionFill`, `completed`); `up` tests each fill premise's body
  (`fillBodies`, from nd's `fillBody`); `fillPremises_canonical_completion` is new; the model, witness and UNDECIDED
  theorems state their situation as the filled completion, both UNDECIDED fillings over the same completed base.
- **SR-B2.** `embeddable_sound` drops `hp`: the check gives the calendar premises, and SETTLED's caller has no `hp`.
- **SR-B3.** SETTLED takes `hb` (Astra, round 3), `hF` and `hX` over the whole `X ++ eventsX V`; `settledSafe`
  takes `X` and adds the `up` test of the base background, the fill bodies, `X` and the conventions; the conclusion
  adds an admissible filled completion satisfying the whole `X`. Fixture T14, with Astra's literal case as (c).
- **SR-B4.** "within n days of D" has three bounded candidates, W1 to W3, each with its direction and end points.
  Fixture T11d.
- **SR-B5.** T3's "denotes no day" is a `#guard` fixture only.
