# Events in Lean (`lean/VE/Events/*`)

Specification: [docs/spec/events-time-causation.md](../docs/spec/events-time-causation.md) section 6.1 and 6.2
(statement spec, draft 3) and [docs/spec/events-time-causation-PLAN.md](../docs/spec/events-time-causation-PLAN.md)
batch ET-3. This file lists the files, the theorems of 6.2 proved so far in plain words, the fixtures and every
difference from 6.1. `lean/audit.py` audits every theorem: no unfinished proof, only `propext`, `Classical.choice`
and `Quot.sound`. No existing Lean source changed; `VE.lean` gained one block of imports and `VE/Audit.lean` its
generated entries.

ET-3 is delivered in parts. et-3 holds the block, the generated premises, the calendar check and the completion's
fragment with its transfer theorem. et-3b adds the completion itself, the typing theorems and the conventions' place
in the fragment. et-3c adds conservativity over the vocabulary the block does not touch. et-3cb adds
`embeddable_complete` and `eventsPremises_satisfiable`. et-3d bounds each named date's year in `EventsTyped` (the
DRI's amendment) and proves `embeddable_sound`, so all of ET-3 is built.

## Files

| File | Contents |
|---|---|
| `Decl.lean` | `EventSort`, `StateSort`, `LinkForm`, `Link`, `EventsEnv`; `maxDates`, `dateName`, `dateConst`; role sorts and predicates, `startRole`, `boundRole`; `roleWordingOk`, `beforeWording`, `linkWording`; `consecutive`; `WellFormedEvents` (the block against the author's environment), `regenEnv`, `EventsTyped` |
| `Premises.lean` | the formulas of 1.4 (`irreflexiveF`, `transitiveF`, `linearF`, `dateFactF`, `adjacentF`, `oneRoleF`, `notBeforeBeginF`, `linkForwardF`, `linkWeakerF`), the labelled lists (`calendarLabelled`, `conventionLabelled`, `eventsLabelled`), `orderPremises`, `calendarPremises`, `conventionPremises`, `eventsX`, `Embeds`; `calendar_sat`, `datesOrder_iff`, `datesOrder_calendar`, `unorderedSame_of_order` |
| `Calendar.lean` | the check of 1.6 on finite situations: `beforeB`, `rank`, `dateDay`, `namedRank`, `strictLinearB`, `calendarCheck` (its diagnostic texts), `embeddable`, `numbering`; the counting lemmas (`countP_lt_succ`, `countP_eq_le_one`, `countP_lt_le`, `countP_lt_lt`) and `embeddable_complete`; `pairwise_of_chain`, `rel_getLast`, `countP_lt_of` and `embeddable_sound` |
| `Completion.lean` | the completion of 1.7 (`numOf`, `oldTuple`, `addedDay`, `isDayC`, `completion`) and its fragment (`isConst`, `isVar`, `hits`, `vacuous`, `up`, `down`, `DayExtension`); `hits_vacuous`, `dayExtension_transfer`, `completion_extension`, `completion_reading`, `completion_admissible`, `conventions_exact` |
| `Conservative.lean` | `oldEnv` (the vocabulary the block does not touch), `expDays`, `firstDay` and `expansion` (proof helpers); `dateName_inj`, `wf_transfer`, `conventions_empty`, `events_conservative`; `dayNames`, `firstName` and `datesSituation` (proof helpers), `chain_pairwise`, `eventsPremises_satisfiable` |
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
  (`EventsTyped`) against the environment with the date constants added. Both checks require every named date to
  be a valid date, year 9999 at most. The decoder builds only such dates (`parseIso_valid`).
* **`eventsPremises_wellFormed`**: every generated premise is closed and typed in that environment.
* **`conventions_exact`**: every convention is both `up` and `down` whenever no role or link predicate is in `ng`:
  each day quantifier in a convention is guarded by a role or link atom, so added days never change its value.
* **`completion_extension`**, **`completion_reading`**, **`completion_admissible`**: the completion of a situation
  numbered as civil days adds a day for every unused day number, with no facts except their order. It is a day
  extension of the situation in which only `before` has tuples with added days. Its days are every civil day, so it
  is a calendar reading (`CalendarReading`: an embedding onto `0..dateMax`). It is a structure of the situation's
  environment.
* **`events_conservative`**: take the vocabulary the block does not touch (`oldEnv`: no day sort, no predicate
  with the day sort in its signature, no day constant, no link). For premises and a claim written only in it, the
  claim follows from the premises with the block exactly when it follows without the block. One way, a structure of
  the block forgets the touched vocabulary. The other way, a structure of the old vocabulary gains one day for each
  named date, in date order (or a single day when there is none), with the author's day constants on the first of
  them and every role, link and day relation empty: it satisfies the calendar premises (`calendar_sat`), the
  conventions hold because each is guarded by an empty role or link (`conventions_empty`), and the old formulas keep
  their values (`wf_transfer`). The proof needs **`dateName_inj`**: two dates with the same constant name are the
  same date.
* **`embeddable_complete`**: if some numbering numbers a situation's days as civil days (`Embeds`), and its day
  list has no repeat, the check passes. No year bound is needed: `Embeds` already keeps every number within
  `0..dateMax`. The proof counts. Under such a numbering, a day's rank is the number of days with a smaller
  number. A number is taken by at most one day, so at most `b - a` days have a number from `a` to `b - 1`
  (`countP_lt_le`, a pigeonhole count over lists, without Mathlib). That bounds each count of step 4: the days
  before the first named date, between two consecutive named dates, and after the last. A named day is counted
  below every later named day (`countP_lt_lt`), so step 3 passes too.
* **`embeddable_sound`**: if a situation passes the check, `numbering` embeds it. No calendar premise is assumed.
  A day's number is its rank plus an offset: the date number minus the rank of the last named day at or below it
  (or of the first named day, below all of them). Step 3 orders the named days, and the gap bounds of step 4 make
  the offsets grow along the dates. So the numbers rise with the order, are distinct, and are the dates' own
  numbers on named days. The bound after the last date keeps every number within `dateMax`, and it uses that the
  last date is at most 9999-12-31, which is the year bound of `EventsTyped`. Without that bound the theorem is
  false (et-3b's counterexample, below).
* **`eventsPremises_satisfiable`**: the generated premises alone have a finite situation that passes the check.
  The situation (`datesSituation`) has one day for each named date, ordered as the dates are (one day when there is
  none), and one element of every other sort. The author's day constants are on the first day, and there is no fact
  except the days' order. It is the finite form of `expansion` with nothing to expand. It satisfies the calendar
  premises (`calendar_sat`). The conventions hold because no role or link has a fact (`conventions_empty`), and
  `embeddable_complete` gives `embeddable`.
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
`embeddable_sound` as first approved: one day named 10000-01-01 passes the check, but no numbering embeds it.
Since et-3d it is not `EventsTyped`. et-3c adds T7 (conservativity): a document with no day vocabulary has the same
verdicts with and without the block. A claim that does not follow has a countermodel either way (with the block, the
named dates' days added), and a claim that follows without the block follows with it, by `events_conservative`.
et-3cb adds the pack alone: `datesSituation` for T4's block, T7's block (author constants of a day sort and of
another sort), R1's five dates and no date at all. Each satisfies every generated premise and passes the check, and
`eventsPremises_satisfiable` is applied to T7. et-3d adds the year boundary. 9999-12-31 is typed and numbered
`dateMax`, and a day after it fails the check. 10000-01-01 is not typed, neither alone nor after 9999-12-31. An
earlier date without its constant, or an improper earlier date, is not typed either. `embeddable_sound` is applied
to the boundary block. The decoders refuse 10000-01-01: `parseIso` gives `InvalidDate(10000-01-01)`, and day
2932897 gives `DateRange(2932897)`. Every date `parseIso` returns meets the bound. T8 (identity on the wire) and T10's `EventsReserved` are
the decoder's (ET-4).

## Differences from 6.1

* One, signed by the DRI (reviews/dri-decisions-20261027-featureplan-gates.md item 1): `EventsTyped` adds
  `decide (D.year ≤ 9999)` for every named date (`docs/events-time-causation/et-3d/evidence/statements.json`: 72
  exact, `EventsTyped` differing by exactly that edit). `pairwise_of_chain`, `rel_getLast` and `countP_lt_of` are
  proof helpers of `embeddable_sound`.
* None otherwise: every other definition and theorem statement of 6.1 and 6.2 is the approved
  text, whitespace aside (`docs/events-time-causation/et-3/evidence/statements.json`,
  `docs/events-time-causation/et-3b/evidence/statements.json`, `docs/events-time-causation/et-3c/evidence/statements.json`, `docs/events-time-causation/et-3cb/evidence/statements.json`). `isVar` and `isVar_beq` are proof helpers that read
  `hits`'s test `t == .var k` as a function on the term; `unorderedSame_of_order` is fixture T2b's theorem.
  `oldTuple_map`, `oldTuple_eq`, `completion_before_new`, `completion_typed`, `startRole_mem` and `boundRole_mem`
  are proof helpers, and so are `pad_value`, `pad_chars`, `dateName_data`, `dateName_inj`, `wf_transfer`,
  `guarded_empty`, `conventions_empty`, `expansion_typed` and `tupleTyped_relation`, and so are the four
  counting lemmas and `chain_pairwise`.
