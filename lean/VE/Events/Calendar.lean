import VE.Events.Premises
import VE.Finite

/-! The calendar check on finite situations (docs/spec/events-time-causation.md 1.6, 6.1): the days
are strictly ordered by `before`, each named date denotes a day, the named days are in date order,
and no gap holds more unnamed days than the calendar has between (or beyond) the named dates.
`embeddable` is its success; `numbering` numbers the days as civil days. -/
namespace VE.Events
open VE.Time (Civil dateMax)

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

/-- The first failing condition of 1.6, as its diagnostic text; `none` when the situation passes. -/
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

/-- A named day takes its date's number; an unnamed day the number of the last named day below it
    plus the rank difference (below the first named day: that day's number minus the difference;
    with no named date: its rank). -/
def numbering (V : EventsEnv) (M : VE.FiniteModel α) (x : α) : Nat :=
  let r := namedRank V M
  match (V.dates.filter (fun D => decide (r D ≤ rank V M x))).getLast? with
  | some D => D.num + (rank V M x - r D)
  | none =>
    match V.dates with
    | [] => rank V M x
    | D₁ :: _ => D₁.num - (r D₁ - rank V M x)
end Finite

end VE.Events
