import VE.Semantics
import VE.Time.Calendar

/-! The `events@0` block (docs/spec/events-time-causation.md 1.2, 1.3, 6.1): a day sort with its
`before` order, event sorts with an `on` role, state sorts with `begins` and `ends` roles, named
dates from W6a's calendar, and causal links. The decoder (ET-4) builds an `EventsEnv` from the
environment JSON; this file holds the decoded form, the date names and the typing check. -/
namespace VE.Events
open VE.Time (Civil)

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
  deriving DecidableEq, Repr

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

def maxDates : Nat := 64

/-- The constant of a named date: `date__YYYY_MM_DD` (the reserved prefix `date__`). -/
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

/-- The author's environment with one constant of the day sort per named date. -/
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

end VE.Events
