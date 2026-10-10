import VE.Ask.Groups
import VE.Ask.Sound

/-! The figures of docs/spec/question-answering.md 7.6, computed: every row's lead and reason, the agreement with
RD-3's fold, and the groups of the two-set example and of U3's shape. -/

namespace VE.Ask.Examples
open VE.Readings VE.Ask

def results : List ChoiceResult := [.proved, .refuted, .free, .conflict, .model, .inconsistent, .unknown]

/-- Every row with choice `[]`: 7 results for each of the four result fields, two split flags (4,802 rows). -/
def allRows : List Row :=
  results.flatMap fun cf => results.flatMap fun p => results.flatMap fun q => results.flatMap fun n =>
    [false, true].map fun s => ⟨[], cf, p, q, n, s⟩

def countLead (d : Lead) : Nat := (allRows.filter (·.lead == d)).length
def countReason (x : Reason) : Nat := (allRows.filter (·.reason == some x)).length

#guard allRows.length = 4802
#guard countLead .yes = 14 ∧ countLead .no = 12 ∧ countLead .notSettled = 252 ∧ countLead .notNecessarily = 42 ∧
  countLead .unknown = 4482
#guard countReason .conflict = 686 ∧ countReason .conflictUnchecked = 3430 ∧ countReason .inconsistent = 56 ∧
  countReason .unchecked = 130 ∧ countReason .noResult = 180 ∧ countReason .tooMany = 0
-- `lead_agrees` and `reason_exact` on every row.
#guard allRows.all fun r => (r.lead != .yes || r.query == .proved) &&
  ((r.lead != .no && r.lead != .notSettled && r.lead != .notNecessarily) || r.query != .proved) &&
  ((r.lead == .unknown) == r.reason.isSome)

/-! The decisive rows -/

#guard (Row.mk [] .free .model .proved .unknown false).lead = .yes
#guard (Row.mk [] .free .unknown .proved .unknown false).reason = some .unchecked
#guard (Row.mk [] .free .model .unknown .proved false).lead = .no
#guard (Row.mk [] .free .model .refuted .unknown true).lead = .notSettled
#guard (Row.mk [] .free .model .refuted .unknown false).lead = .notNecessarily
#guard (Row.mk [] .conflict .model .proved .unknown false).reason = some .conflict
#guard (Row.mk [] .free .inconsistent .proved .unknown false).reason = some .inconsistent
-- A countermodel alone is never "no" (D4).
#guard (Row.mk [] .free .model .refuted .unknown false).lead != .no

/-! `all_yes_iff_fold` on every list of one to three rows of five samples (155 lists) -/

def samples : List Row :=
  [⟨[], .free, .model, .proved, .unknown, false⟩, ⟨[], .free, .model, .refuted, .unknown, false⟩,
   ⟨[], .free, .model, .unknown, .proved, false⟩, ⟨[], .conflict, .model, .proved, .unknown, false⟩,
   ⟨[], .free, .model, .refuted, .unknown, true⟩]

def lists : List (List Row) :=
  (samples.map fun a => [a]) ++ (samples.flatMap fun a => samples.map fun b => [a, b]) ++
    (samples.flatMap fun a => samples.flatMap fun b => samples.map fun c => [a, b, c])

def bothHold (rs : List Row) : Bool := rs.all (·.lead == .yes) && foldEntailment (conflictRows rs) (queryRows rs) == .all
def bothFail (rs : List Row) : Bool := !rs.all (·.lead == .yes) && foldEntailment (conflictRows rs) (queryRows rs) != .all

#guard lists.length = 155
#guard (lists.filter bothHold).length = 3 ∧ (lists.filter bothFail).length = 152

/-! Groups (R7) -/

/-- Two binary sets `a`, `b`: yes on (0, 0) and (1, 1), not necessarily elsewhere. -/
def twoSets : List Row :=
  [⟨[("a", 0), ("b", 0)], .free, .model, .proved, .unknown, false⟩,
   ⟨[("a", 0), ("b", 1)], .free, .model, .refuted, .unknown, false⟩,
   ⟨[("a", 1), ("b", 0)], .free, .model, .refuted, .unknown, false⟩,
   ⟨[("a", 1), ("b", 1)], .free, .model, .proved, .unknown, false⟩]

def leadKey (r : Row) : Lead × List Source := (r.lead, [])

#guard relevantSets ["a", "b"] twoSets leadKey = ["a", "b"]
#guard !separates twoSets leadKey ["a"] && !separates twoSets leadKey ["b"] && separates twoSets leadKey ["a", "b"]
#guard (groups ["a", "b"] twoSets leadKey).length = 4

/-- U3's shape: `rs_u087` (three readings) and `rs_u096` (two); not settled on `rs_u096 = 0`, yes on `= 1`. -/
def u3Shape : List Row :=
  [0, 1, 2].flatMap fun i =>
    [⟨[("rs_u087", i), ("rs_u096", 0)], .free, .model, .refuted, .unknown, true⟩,
     ⟨[("rs_u087", i), ("rs_u096", 1)], .free, .model, .proved, .unknown, false⟩]

#guard relevantSets ["rs_u087", "rs_u096"] u3Shape leadKey = ["rs_u096"]
#guard separates u3Shape leadKey ["rs_u096"] && !separates u3Shape leadKey ["rs_u087"]
#guard (groups ["rs_u087", "rs_u096"] u3Shape leadKey).map (fun g => (g.lead, g.on, g.rows.length)) =
  [(.notSettled, [("rs_u096", some 0)], 3), (.yes, [("rs_u096", some 1)], 3)]

end VE.Ask.Examples
