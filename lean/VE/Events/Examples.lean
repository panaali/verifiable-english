import VE.Events.Completion
import VE.Events.Conservative
import VE.Time.Wire

/-! The ET-3 fixtures of docs/spec/events-time-causation.md 8 as `#guard` lines: T1 to T6, T10, T13,
T2b, the fragment rows F1 and the day numbers; et-3b's completion pieces and its counterexample to
`embeddable_sound`, refused since et-3d's year bound; et-3c's T7 (conservativity); et-3cb's finite situation of the
pack alone; et-3d's year boundary.
T8 (identity) is ET-4's. -/
namespace VE.Events.Examples
open VE.Events
open VE.Time (Civil dateMax)

def d (y m dd : Nat) : Civil := ⟨y, m, dd⟩

def base (dates : List Civil) : EventsEnv :=
  { day := "day", before := "before", events := [], states := [], dates := dates, anchor := none, links := [] }

def envDay : VE.Environment :=
  ⟨["day"], fun p => if p = "before" then some ["day", "day"] else none, fun _ => none⟩

/-- A situation over string entities: days in `before` order, other domains, constants and relations. -/
def chain (days : List String) (consts : List (String × String))
    (doms : List (String × List String) := []) (rels : List (String × List (List String)) := []) :
    VE.FiniteModel String :=
  { domains := fun s => if s = "day" then days else ((doms.find? (·.1 == s)).map (·.2)).getD []
    constants := fun c => (consts.find? (·.1 == c)).map (·.2)
    relations := fun p =>
      if p = "before" then
        ((List.range days.length).flatMap fun i => (List.range days.length).filterMap fun j =>
          if i < j then some [days[i]!, days[j]!] else none)
      else ((rels.find? (·.1 == p)).map (·.2)).getD [] }

/-- The label of the first generated premise the situation violates. -/
def firstFailing (V : EventsEnv) (M : VE.FiniteModel String) : Option String :=
  ((eventsLabelled V).find? (fun p => !p.2.eval M [])).map (·.1)

-- day numbers (W6 coordinates)
#guard (d 1970 1 1).num == 0
#guard (d 9999 12 31).num == dateMax
#guard (d 2026 10 12).num == 20738
#guard (d 2027 1 5).num == 20823
#guard dateName (d 2026 10 12) == "date__2026_10_12"

def c12 : String := dateName (d 2026 10 12)
def c13 : String := dateName (d 2026 10 13)
def c14 : String := dateName (d 2026 10 14)

-- T1: labels, no adjacency; the dates ordered as the calendar orders them, both ways
def vT1 : EventsEnv := base [d 2026 10 12, d 2027 1 5]
#guard WellFormedEvents envDay vT1
#guard (regenEnv envDay vT1).constants c12 == some "day" && (regenEnv envDay vT1).constants c13 == none
#guard (regenEnv envDay vT1).sorts == envDay.sorts
#guard EventsTyped (regenEnv envDay vT1) vT1 && !EventsTyped envDay vT1
#guard (calendarLabelled vT1).map (·.1) ==
  ["events:irreflexive", "events:transitive", "events:linear", "events:date:2026-10-12:2027-01-05"]
#guard orderPremises vT1 == [irreflexiveF vT1, transitiveF vT1, linearF vT1]
def mT1 : VE.FiniteModel String := chain ["a", "b"] [(c12, "a"), (dateName (d 2027 1 5), "b")]
#guard (calendarPremises vT1).all (·.eval mT1 [])
#guard (dateFactF vT1 (d 2026 10 12) (d 2027 1 5)).eval mT1 []
#guard !(dateFactF vT1 (d 2027 1 5) (d 2026 10 12)).eval mT1 []
example : (d 2026 10 12).Before (d 2027 1 5) := by unfold Civil.Before d; decide
example : ¬ (d 2027 1 5).Before (d 2026 10 12) := by unfold Civil.Before d; decide

-- T2: one date premise and one adjacency premise; no day strictly between the two named days
def vT2 : EventsEnv := base [d 2026 10 12, d 2026 10 13]
#guard (calendarLabelled vT2).map (·.1) ==
  ["events:irreflexive", "events:transitive", "events:linear", "events:date:2026-10-12:2026-10-13",
   "events:adjacent:2026-10-12:2026-10-13"]
#guard !(calendarPremises vT2).all (·.eval (chain ["a", "x", "b"] [(c12, "a"), (c13, "b")]) [])

-- T2b: two days neither before the other violate the order premises (`linear`), so they never
-- refute `unorderedSameF` (`unorderedSame_of_order`)
def vT2b : EventsEnv := base []
def mT2b : VE.FiniteModel String :=
  { domains := fun s => if s = "day" then ["a", "b"] else [], constants := fun _ => none, relations := fun _ => [] }
#guard !(unorderedSameF vT2b).eval mT2b []
#guard !(orderPremises vT2b).all (·.eval mT2b [])

-- T3: the gap count, the date order and the named days
def vT3 : EventsEnv := base [d 2026 10 12, d 2026 10 14]
#guard (calendarLabelled vT3).length == 4
#guard calendarCheck vT3 (chain ["a", "x1", "x2", "x3", "b"] [(c12, "a"), (c14, "b")]) ==
  some "NotCalendar: 3 days between 2026-10-12 and 2026-10-14, at most 1"
#guard calendarCheck vT3 (chain ["a", "x1", "x2", "b"] [(c12, "a"), (c14, "b")]) ==
  some "NotCalendar: 2 days between 2026-10-12 and 2026-10-14, at most 1"
#guard calendarCheck vT3 (chain ["a", "x1", "b"] [(c12, "a"), (c14, "b")]) == none
#guard calendarCheck vT3 (chain ["a", "b"] [(c12, "a"), (c14, "b")]) == none
#guard numbering vT3 (chain ["a", "x1", "b"] [(c12, "a"), (c14, "b")]) "x1" == (d 2026 10 13).num
#guard calendarCheck vT3 (chain ["a", "b"] [(c12, "b"), (c14, "a")]) ==
  some "NotCalendar: 2026-10-12 is not before 2026-10-14"
#guard calendarCheck vT3 (chain ["a"] [(c12, "a")]) == some "NotCalendar: 2026-10-14 denotes no day"

-- T3e: the edges
#guard calendarCheck (base [d 1970 1 1]) (chain ["x", "a"] [(dateName (d 1970 1 1), "a")]) ==
  some "NotCalendar: 1 day before 1970-01-01, at most 0"
#guard calendarCheck (base [d 1970 1 1]) (chain ["a", "x"] [(dateName (d 1970 1 1), "a")]) == none
#guard calendarCheck (base [d 9999 12 31]) (chain ["a", "x"] [(dateName (d 9999 12 31), "a")]) ==
  some "NotCalendar: 1 day after 9999-12-31, at most 0"

-- F1: the fragment on T3b, T3c, T3d and R1's claim
def between : VE.Formula :=
  .ex "day" (.and (.binary "before" (.const c12) (.var 0)) (.binary "before" (.var 0) (.const c14)))
def after12 : VE.Formula := .ex "day" (.binary "before" (.const c12) (.var 0))
def actAfter12 : VE.Formula :=
  .ex "act" (.ex "day" (.and (.binary "committed_on" (.var 1) (.var 0)) (.binary "before" (.const c12) (.var 0))))
def c21 : String := dateName (d 2026 9 21)
def c27 : String := dateName (d 2026 9 27)
def inProgress : VE.Formula :=
  .ex "day" (.and (.binary "begins" (.const "s") (.var 0)) (.and (.not (.binary "before" (.var 1) (.var 0)))
    (.not (.ex "day" (.and (.binary "ends" (.const "s") (.var 0)) (.binary "before" (.var 0) (.var 2)))))))
def throughout : VE.Formula :=
  .all "day" (.implies (.and (.not (.binary "before" (.var 0) (.const c21))) (.not (.binary "before" (.const c27) (.var 0))))
    inProgress)
#guard down "day" ["before"] between == false
#guard up "day" ["before"] between == true
#guard down "day" ["before"] after12 == false
#guard down "day" ["before"] actAfter12 == true
#guard down "day" ["before"] throughout == true
#guard up "day" ["before"] throughout == false
#guard up "day" ["before"] (.not between) == false
#guard down "day" ["before"] (.not between) == true
-- T3b: the situation with only 12 and 14 October refutes `between`, but it is not `down`
#guard !between.eval (chain ["a", "b"] [(c12, "a"), (c14, "b")]) []
#guard between.eval (chain ["a", "x", "b"] [(c12, "a"), (c14, "b")]) []

-- T4 to T6: the conventions, with an event sort, a state sort and three links
def vEv : EventsEnv :=
  { day := "day", before := "before", events := [⟨"act", "committed_on"⟩],
    states := [⟨"marriage", "marriage_begins", "marriage_ends"⟩], dates := [d 2026 10 12, d 2026 10 13],
    anchor := none,
    links := [⟨"contributed_to", .contributed, "act", "act", some "the drafters"⟩,
      ⟨"contributed_to_state", .contributed, "act", "marriage", none⟩,
      ⟨"necessary_for", .necessary, "act", "act", none⟩] }
def envEv : VE.Environment :=
  ⟨["day", "act", "marriage"], fun p => match p with
    | "before" => some ["day", "day"]
    | "committed_on" => some ["act", "day"]
    | "marriage_begins" | "marriage_ends" => some ["marriage", "day"]
    | "contributed_to" | "necessary_for" => some ["act", "act"]
    | "contributed_to_state" => some ["act", "marriage"]
    | _ => none, fun _ => none⟩
#guard WellFormedEvents envEv vEv
#guard !WellFormedEvents envEv { vEv with before := "committed_on" }
#guard (conventionLabelled vEv).map (·.1) ==
  ["events:one_day:act", "events:one_begin:marriage", "events:one_end:marriage", "events:not_before_begin:marriage",
   "events:link_forward:contributed_to", "events:link_forward:contributed_to_state",
   "events:link_forward:necessary_for", "events:link_weaker:necessary_for:contributed_to"]
#guard (conventionPremises vEv).all (fun a => up "day" ["before"] a && down "day" ["before"] a)
#guard (calendarPremises vEv).all (fun a => up "day" ["before"] a) == false
/-- Days a (12 October), b (13 October) and c (unnamed, after b). -/
def sit (doms : List (String × List String)) (rels : List (String × List (List String))) : VE.FiniteModel String :=
  chain ["a", "b", "c"] [(c12, "a"), (c13, "b")] doms rels
-- T4: one act on two days, then on one day
#guard firstFailing vEv (sit [("act", ["x"])] [("committed_on", [["x", "a"], ["x", "b"]])]) ==
  some "events:one_day:act"
#guard firstFailing vEv (sit [("act", ["x"])] [("committed_on", [["x", "a"]])]) == none
-- T5: a marriage that ends before it begins, then on the day it begins
#guard firstFailing vEv (sit [("marriage", ["m"])] [("marriage_begins", [["m", "b"]]), ("marriage_ends", [["m", "a"]])]) ==
  some "events:not_before_begin:marriage"
#guard firstFailing vEv (sit [("marriage", ["m"])] [("marriage_begins", [["m", "b"]]), ("marriage_ends", [["m", "b"]])]) ==
  none
-- T6: the effect before the cause; a cause after the marriage's last day; a cause during the marriage;
-- a marriage with no last day
#guard firstFailing vEv (sit [("act", ["x", "y"])]
  [("committed_on", [["x", "b"], ["y", "a"]]), ("contributed_to", [["x", "y"]])]) ==
  some "events:link_forward:contributed_to"
#guard firstFailing vEv (sit [("act", ["x"]), ("marriage", ["m"])]
  [("committed_on", [["x", "c"]]), ("marriage_begins", [["m", "a"]]), ("marriage_ends", [["m", "b"]]),
   ("contributed_to_state", [["x", "m"]])]) == some "events:link_forward:contributed_to_state"
#guard firstFailing vEv (sit [("act", ["x"]), ("marriage", ["m"])]
  [("committed_on", [["x", "b"]]), ("marriage_begins", [["m", "a"]]), ("marriage_ends", [["m", "c"]]),
   ("contributed_to_state", [["x", "m"]])]) == none
#guard firstFailing vEv (sit [("act", ["x"]), ("marriage", ["m"])]
  [("committed_on", [["x", "c"]]), ("marriage_begins", [["m", "a"]]), ("contributed_to_state", [["x", "m"]])]) == none
-- link_weaker: a necessary link that did not contribute
#guard firstFailing vEv (sit [("act", ["x", "y"])]
  [("committed_on", [["x", "a"], ["y", "b"]]), ("necessary_for", [["x", "y"]])]) ==
  some "events:link_weaker:necessary_for:contributed_to"

-- T10: 64 and 65 named dates, a date given twice, a declared constant with a date's name, 1969-12-31
#guard WellFormedEvents envDay (base ((List.range 64).map VE.Time.epoch.addDays))
#guard !WellFormedEvents envDay (base ((List.range 65).map VE.Time.epoch.addDays))
#guard !WellFormedEvents envDay (base [d 2026 10 12, d 2026 10 12])
#guard !WellFormedEvents { envDay with constants := fun c => if c = c12 then some "day" else none } (base [d 2026 10 12])
#guard (match VE.Time.parseIso "1969-12-31" with
  | .error e => e == "DateRange(1969-12-31)"
  | .ok _ => false)

-- T13: strict precedence: "that confirmation happens before that action"
def vT13 : EventsEnv :=
  { base [d 2026 10 12, d 2026 10 13] with events := [⟨"confirmation", "confirmed_on"⟩, ⟨"action", "acted_on"⟩] }
def confirmedBefore : VE.Formula :=
  .ex "day" (.ex "day" (.and (.binary "confirmed_on" (.const "k") (.var 1))
    (.and (.binary "acted_on" (.const "g") (.var 0)) (bin "before" 1 0))))
def mT13 (confirmed acted : String) : VE.FiniteModel String :=
  chain ["a", "b"] [(c12, "a"), (c13, "b"), ("k", "k"), ("g", "g")] [("confirmation", ["k"]), ("action", ["g"])]
    [("confirmed_on", [["k", confirmed]]), ("acted_on", [["g", acted]])]
#guard (eventsX vT13).all (·.eval (mT13 "a" "b") []) && confirmedBefore.eval (mT13 "a" "b") []
#guard (eventsX vT13).all (·.eval (mT13 "b" "b") []) && (VE.Formula.not confirmedBefore).eval (mT13 "b" "b") []

-- T9 (shape only): the profile wordings and the role wordings
#guard beforeWording == "{0} is before {1}"
#guard linkWording .contributed == "{0} contributed to {1}" && linkWording .necessary == "{0} was necessary for {1}"
#guard roleWordingOk "{0} is committed on {1}"
#guard roleWordingOk "{0} happens on {1}"
#guard !roleWordingOk "{0} committed {1}"
#guard !roleWordingOk "{0} on {1}"
#guard !roleWordingOk "{0} happens on {1} to {0}"
#guard !roleWordingOk "{0} is {1} on {1}"

-- T11 and R1: the calendar premise counts and R1's adjacency labels
#guard (calendarLabelled (base [d 2027 1 4, d 2027 1 5, d 2027 1 7])).length == 3 + 2 + 1
def vR1 : EventsEnv := base [d 2026 6 29, d 2026 9 20, d 2026 9 21, d 2026 9 26, d 2026 9 27]
#guard (calendarLabelled vR1).length == 3 + 4 + 2
#guard ((calendarLabelled vR1).filter (·.1.startsWith "events:adjacent:")).map (·.1) ==
  ["events:adjacent:2026-09-20:2026-09-21", "events:adjacent:2026-09-26:2026-09-27"]

-- The completion's pieces (et-3b): old tuples, numbers, added days (T3's situation, 13 October missing)
#guard oldTuple ([.inl "a", .inl "b"] : List (String ⊕ Nat)) == some ["a", "b"]
#guard oldTuple ([.inl "a", .inr 3] : List (String ⊕ Nat)) == none && oldTuple ([.inr 3, .inl "a"] : List (String ⊕ Nat)) == none
#guard numOf (fun (_ : String) => 5) (.inl "a") == 5 && numOf (fun (_ : String) => 5) (.inr 3) == 3
def mC : VE.FiniteModel String := chain ["a", "b"] [(c12, "a"), (c14, "b")]
def numC (x : String) : Nat := if x = "a" then (d 2026 10 12).num else (d 2026 10 14).num
example : addedDay vT3 mC numC (d 2026 10 13).num := by unfold addedDay; decide
example : ¬ addedDay vT3 mC numC (d 2026 10 12).num := by unfold addedDay; decide
example : ¬ addedDay vT3 mC numC (dateMax + 1) := by unfold addedDay; decide
example : isDayC vT3 mC numC (.inl "a") ∧ ¬ isDayC vT3 mC numC (.inl "k") := by simp only [isDayC]; decide
-- a finite situation is never a calendar reading: day 0 is missing (1.5)
example : ¬ CalendarReading vT3 mC.asStructure numC := fun h => by
  obtain ⟨x, hx, hn⟩ := h.2 0 (by decide)
  have hx : x ∈ ["a", "b"] := hx
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
  rcases hx with rfl | rfl <;> exact absurd hn (by decide)

-- T7: a document with no day vocabulary, with and without the block: the same verdicts
def envT7 : VE.Environment :=
  ⟨["person", "day", "act"], fun p => match p with
    | "before" => some ["day", "day"] | "committed_on" => some ["act", "day"]
    | "contributed_to" => some ["act", "act"] | "admires" => some ["person", "person"] | _ => none,
   fun c => match c with | "alice" | "bob" => some "person" | "the_day" => some "day" | _ => none⟩
def vT7 : EventsEnv := { base [d 2026 10 12, d 2026 10 14] with
  events := [⟨"act", "committed_on"⟩], links := [⟨"contributed_to", .contributed, "act", "act", none⟩] }
#guard WellFormedEvents envT7 vT7
#guard (oldEnv envT7 vT7).sorts == ["person", "act"]
#guard (oldEnv envT7 vT7).predicates "admires" == some ["person", "person"] &&
  ["before", "committed_on", "contributed_to"].all ((oldEnv envT7 vT7).predicates · == none)
#guard (oldEnv envT7 vT7).constants "alice" == some "person" && (oldEnv envT7 vT7).constants "the_day" == none
def gT7 : List VE.Formula := [.binary "admires" (.const "alice") (.const "bob")]
def notEntailedT7 : VE.Formula := .binary "admires" (.const "bob") (.const "alice")
def entailedT7 : VE.Formula := .ex "person" (.binary "admires" (.const "alice") (.var 0))
#guard (notEntailedT7 :: entailedT7 :: gT7).all (·.check (oldEnv envT7 vT7) [])
-- NOT ENTAILED without the block, and with it (the countermodel with the named dates' days)
def mT7 (days : List String) (consts : List (String × String)) : VE.FiniteModel String :=
  chain days ([("alice", "alice"), ("bob", "bob")] ++ consts) [("person", ["alice", "bob"])]
    [("admires", [["alice", "bob"]])]
#guard gT7.all (·.eval (mT7 [] []) []) && !notEntailedT7.eval (mT7 [] []) []
#guard (eventsX vT7).all (·.eval (mT7 ["a", "b"] [(c12, "a"), (c14, "b"), ("the_day", "a")]) []) &&
  gT7.all (·.eval (mT7 ["a", "b"] [(c12, "a"), (c14, "b"), ("the_day", "a")]) []) &&
  !notEntailedT7.eval (mT7 ["a", "b"] [(c12, "a"), (c14, "b"), ("the_day", "a")]) []
-- ENTAILED with the block, from the entailment without it (`events_conservative`)
example : ∀ S : VE.Structure.{0}, S.Admissible (regenEnv envT7 vT7) → VE.Norms.Sat S (eventsX vT7) →
    VE.Norms.Sat S gT7 → entailedT7.denote S [] :=
  (events_conservative envT7 vT7 (by decide) gT7 entailedT7
    (fun a ha => (VE.check_iff_wellFormed _ _ a).1 (by simp only [gT7, List.mem_singleton] at ha; subst ha; decide))
    ((VE.check_iff_wellFormed _ _ _).1 (by decide))).2 fun S hS hΓ => by
      obtain ⟨_, w, hv, hw, hr⟩ := hΓ _ (List.mem_singleton_self _)
      obtain ⟨b, hb, db⟩ := hS.1 "bob" "person" rfl
      simp only [VE.Term.denote, hb, Option.some.injEq] at hw; subst hw
      exact ⟨b, db, _, b, hv, rfl, hr⟩

-- The pack alone (et-3cb, `eventsPremises_satisfiable`): the named dates' days in date order satisfy every
-- generated premise and pass the check (`embeddable_complete`); author day constants are on the first day
#guard (eventsX vEv).all (·.eval (datesSituation envEv vEv) []) && embeddable vEv (datesSituation envEv vEv)
#guard (datesSituation envEv vEv).domains "day" == [("day", c12), ("day", c13)] &&
  (datesSituation envEv vEv).relations "before" == [[("day", c12), ("day", c13)]]
#guard (eventsX vT7).all (·.eval (datesSituation envT7 vT7) []) && embeddable vT7 (datesSituation envT7 vT7)
#guard (datesSituation envT7 vT7).constants "the_day" == some ("day", c12) &&
  (datesSituation envT7 vT7).constants "alice" == some ("person", "") &&
  (datesSituation envT7 vT7).domains "person" == [("person", "")]
#guard (eventsX vR1).all (·.eval (datesSituation envDay vR1) []) && embeddable vR1 (datesSituation envDay vR1)
-- with no named date: one day
#guard (datesSituation envDay (base [])).domains "day" == [("day", "")] &&
  (eventsX (base [])).all (·.eval (datesSituation envDay (base [])) []) && embeddable (base []) (datesSituation envDay (base []))
example : ∃ M : VE.FiniteModel VE.Bridge.Entity, M.Valid (regenEnv envT7 vT7) ∧
    VE.Norms.Sat M.asStructure (eventsX vT7) ∧ embeddable vT7 M = true :=
  eventsPremises_satisfiable envT7 vT7 (by decide)

-- et-3d: `EventsTyped` bounds every named date's year by 9999, as the decoder does (`Civil.Valid`; the DRI's
-- amendment, reviews/dri-decisions-20261027-featureplan-gates.md item 1). et-3b's counterexample, a named date
-- 10000-01-01 that passes the check with number `dateMax + 1`, is no longer typed, so `embeddable_sound` holds as
-- approved.
def vX : EventsEnv := base [d 10000 1 1]
def envX : VE.Environment :=
  ⟨["day"], fun p => if p = "before" then some ["day", "day"] else none,
   fun c => if c = dateName (d 10000 1 1) then some "day" else none⟩
def mX : VE.FiniteModel String := chain ["x"] [(dateName (d 10000 1 1), "x")]
#guard !EventsTyped envX vX && embeddable vX mX && numbering vX mX "x" == dateMax + 1
-- and no numbering at all embeds it, though the check passes
example (num : String → Nat) : ¬ Embeds vX mX.asStructure num := fun h => by
  obtain ⟨x, -, hx, hn⟩ := h.2.2.2 (d 10000 1 1) (by decide)
  have := h.2.1 x hx
  rw [hn] at this
  exact absurd this (by decide)
-- the boundary: the last date, 9999-12-31, is typed and numbered `dateMax`; the next one is not, alone or after it
def vL : EventsEnv := base [d 9999 12 31]
def vL2 : EventsEnv := base [d 9999 12 31, d 10000 1 1]
#guard EventsTyped (regenEnv envDay vL) vL && WellFormedEvents envDay vL
#guard !EventsTyped (regenEnv envDay vX) vX && !WellFormedEvents envDay vX
#guard !EventsTyped (regenEnv envDay vL2) vL2 && !WellFormedEvents envDay vL2
#guard EventsTyped (regenEnv envDay (base [d 9998 12 31, d 9999 1 1])) (base [d 9998 12 31, d 9999 1 1])
#guard embeddable vL (chain ["x"] [(dateName (d 9999 12 31), "x")]) &&
  numbering vL (chain ["x"] [(dateName (d 9999 12 31), "x")]) "x" == dateMax
#guard embeddable vL (chain ["w", "x"] [(dateName (d 9999 12 31), "x")]) &&
  numbering vL (chain ["w", "x"] [(dateName (d 9999 12 31), "x")]) "w" == dateMax - 1
#guard calendarCheck vL (chain ["x", "y"] [(dateName (d 9999 12 31), "x")]) ==
  some "NotCalendar: 1 day after 9999-12-31, at most 0"
-- `embeddable_sound` with no hypothesis beyond the approved ones, its typing from the author's block
example (M : VE.FiniteModel String) (valid : M.Valid (regenEnv envDay vL)) (he : embeddable vL M = true) :
    Embeds vL M.asStructure (numbering (α := String) vL M) :=
  embeddable_sound (regenEnv envDay vL) vL (regen_typed envDay vL (by decide)) M valid he

-- the decoders never build such a date (the DRI's condition, reviews/dri-decisions-20261028-et-3d.md): the ISO
-- reader takes four-digit years, and the day-number reader refuses `dateMax + 1`
#guard (match VE.Time.parseIso "10000-01-01" with
  | .error e => e == "InvalidDate(10000-01-01)"
  | .ok _ => false)
#guard (match VE.Time.parseIso "9999-12-31" with
  | .error _ => false
  | .ok D => D == d 9999 12 31)
#guard (match VE.Time.Wire.runConversion "c" "civil" (Lean.Json.mkObj [("day", 2932897)]) with
  | .error e => e == "DateRange(2932897)"
  | .ok _ => false)
#guard (match VE.Time.Wire.runConversion "c" "civil" (Lean.Json.mkObj [("day", 2932896)]) with
  | .error _ => false
  | .ok j => (j.getObjValAs? String "date").toOption == some "9999-12-31")
-- every date the ISO reader returns passes the new bound, so the decoder discharges it
example {s : String} {D : Civil} (h : VE.Time.parseIso s = .ok D) : decide (D.year ≤ 9999) = true :=
  decide_eq_true (VE.Time.parseIso_valid h).2

end VE.Events.Examples
