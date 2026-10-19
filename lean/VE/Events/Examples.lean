import VE.Events.Completion

/-! The ET-3 fixtures of docs/spec/events-time-causation.md 8 as `#guard` lines: T1 to T6, T10, T13,
T2b, the fragment rows F1 and the day numbers. T7 (conservativity) is et-3b's, T8 (identity) ET-4's. -/
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

end VE.Events.Examples
