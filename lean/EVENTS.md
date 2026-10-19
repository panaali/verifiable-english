# Events in Lean (`lean/VE/Events/*`)

Specification: [docs/spec/events-time-causation.md](../docs/spec/events-time-causation.md) section 6.1 and 6.2
(statement spec, draft 3) and [docs/spec/events-time-causation-PLAN.md](../docs/spec/events-time-causation-PLAN.md)
batch ET-3. This file lists the files, the theorems of 6.2 proved so far in plain words, the fixtures and every
difference from 6.1. `lean/audit.py` audits every theorem: no unfinished proof, only `propext`, `Classical.choice`
and `Quot.sound`. No existing Lean source changed; `VE.lean` gained one block of imports and `VE/Audit.lean` its
generated entries.

ET-3 is delivered in parts. et-3 holds the block, the generated premises, the calendar check and the completion's
fragment with its transfer theorem. et-3b adds the completion itself, the typing theorems and the conventions' place
in the fragment. Conservativity, `embeddable_sound`, `embeddable_complete` and `eventsPremises_satisfiable` are not built yet (listed at the end); one of them,
`embeddable_sound`, does not hold as approved.

## Files

| File | Contents |
|---|---|
| `Decl.lean` | `EventSort`, `StateSort`, `LinkForm`, `Link`, `EventsEnv`; `maxDates`, `dateName`, `dateConst`; role sorts and predicates, `startRole`, `boundRole`; `roleWordingOk`, `beforeWording`, `linkWording`; `consecutive`; `WellFormedEvents` (the block against the author's environment), `regenEnv`, `EventsTyped` |
| `Premises.lean` | the formulas of 1.4 (`irreflexiveF`, `transitiveF`, `linearF`, `dateFactF`, `adjacentF`, `oneRoleF`, `notBeforeBeginF`, `linkForwardF`, `linkWeakerF`), the labelled lists (`calendarLabelled`, `conventionLabelled`, `eventsLabelled`), `orderPremises`, `calendarPremises`, `conventionPremises`, `eventsX`, `Embeds`; `calendar_sat`, `datesOrder_iff`, `datesOrder_calendar`, `unorderedSame_of_order` |
| `Calendar.lean` | the check of 1.6 on finite situations: `beforeB`, `rank`, `dateDay`, `namedRank`, `strictLinearB`, `calendarCheck` (its diagnostic texts), `embeddable`, `numbering` |
| `Completion.lean` | the completion of 1.7 (`numOf`, `oldTuple`, `addedDay`, `isDayC`, `completion`) and its fragment (`isConst`, `isVar`, `hits`, `vacuous`, `up`, `down`, `DayExtension`); `hits_vacuous`, `dayExtension_transfer`, `completion_extension`, `completion_reading`, `completion_admissible`, `conventions_exact` |
| `Examples.lean` | the fixtures as `#guard` lines (below) |

## Theorems (6.2) in plain words

* **`calendar_sat`**: every structure whose days are numbered as civil days (`Embeds`: one-to-one, within
  `0..dateMax`, `before` is `<`, each named date denotes a day with its number) satisfies the calendar premises:
  the three order premises, one `date` fact per consecutive pair of named dates, and the adjacency premise for each
  pair one day apart. So every calendar reading does.
* **`datesOrder_iff`**: in every structure of the calendar premises, a named date is `before` another exactly when
  its day number is smaller. The proof walks the sorted date list (`chain_positions`) with transitivity and
  irreflexivity; no other date premise is needed (transitivity derives every other pair, D5).
* **`datesOrder_calendar`**: that number order is W6a's chronological order (`VE.Time.before_iff`): one calendar.
* **`dayExtension_transfer`**: in a day extension (added elements are days, and only predicates of `ng` have true
  tuples with them), an `up` formula true at old elements stays true, and a `down` formula false at old elements
  stays false. `hits_vacuous` is its base: a formula that `hits` variable `k` is false, and one `vacuous` at `k` is
  true, whenever `k` is an added day, at every valuation of the extension.
* **`regen_typed`**: a block that passes `WellFormedEvents` against the author's environment is typed
  (`EventsTyped`) against the environment with the date constants added.
* **`eventsPremises_wellFormed`**: every generated premise is closed and typed in that environment.
* **`conventions_exact`**: every convention is both `up` and `down` whenever no role or link predicate is in `ng`:
  each day quantifier in a convention is guarded by a role or link atom, so added days never change its value.
* **`completion_extension`**, **`completion_reading`**, **`completion_admissible`**: the completion of a situation
  numbered as civil days adds a day for every unused day number, with no facts except their order. It is a day
  extension of the situation in which only `before` has tuples with added days. Its days are every civil day, so it
  is a calendar reading (`CalendarReading`: an embedding onto `0..dateMax`). It is a structure of the situation's
  environment.
* **`unorderedSame_of_order`** (fixture T2b, not in 6.2): the order premises entail that two days neither before
  the other are the same day. It needs `linear`.

## Fixtures (`Examples.lean`)

T1 (labels, both orders of the dates, `datesOrder_calendar` both ways), T2 (labels with the adjacency premise; a day
between the two named days violates it), T2b (a two-day situation without order violates the order premises and
refutes the claim), T3 and T3e (every diagnostic text of `calendarCheck`, its passing cases and `numbering`), F1
(`up` and `down` on T3b, T3c, T3d and R1's claim; the conventions are `up` and `down`, the calendar premises not all
`up`), T4 to T6 (the first violated premise's label, and the accepted cases, including a state with no last day),
T9's shape rows (`roleWordingOk`, the profile wordings), T10 (64 and 65 dates, a repeated date, a declared constant
with a date's name, `DateRange(1969-12-31)`), T11 and R1's premise counts, T13 (strict precedence: a confirmation
on 12 October is before an action on 13 October; on the same day it is not). et-3b adds the completion's pieces
(old tuples, numbers, added days; a finite situation is never a calendar reading) and the counterexample to
`embeddable_sound` (below). T7 (conservativity) is et-3c's; T8 (identity on the wire) and T10's `EventsReserved` are
the decoder's (ET-4).

## Differences from 6.1

* None in the delivered declarations: every definition and theorem statement of 6.1 and 6.2 built is the approved
  text, whitespace aside (`docs/events-time-causation/et-3/evidence/statements.json`,
  `docs/events-time-causation/et-3b/evidence/statements.json`). `isVar` and `isVar_beq` are proof helpers that read
  `hits`'s test `t == .var k` as a function on the term; `unorderedSame_of_order` is fixture T2b's theorem.
  `oldTuple_map`, `oldTuple_eq`, `completion_before_new`, `completion_typed`, `startRole_mem` and `boundRole_mem`
  are proof helpers.

## Not built yet (et-3c)

* `Conservative.lean`: `oldEnv` and `events_conservative`, with fixture T7. A proof exists in this branch's history
  (et-3b's report names the commits); it was moved out for size.

* **`embeddable_sound` does not hold as approved.** `EventsTyped` bounds no year, so a named date after 9999-12-31
  passes the check: a situation whose one day is named 10000-01-01 is `embeddable`, but its number is
  `dateMax + 1`, and no numbering embeds it (`Examples.lean`, the last fixture). The statement needs an amendment
  (a year bound in `EventsTyped`, or a hypothesis) that only the DRI can approve.
* `embeddable_complete` and `eventsPremises_satisfiable` are left for et-3c because of size. No counterexample is
  known to either; the planned proof of the second takes the named dates' days in date order as the situation and
  gets `embeddable` from the first.
