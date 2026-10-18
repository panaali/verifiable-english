import VE.Judgments.Decl
import VE.Judgments.Scan
import VE.Route.Typed

/-! The JT-1 fixtures of docs/spec/judgment-terms.md section 11 (11.1, 11.2 and the direct scan of 11.3), as
`#guard` checks on the built definitions. Each value is the one the spec's stub computed by `#eval`. The status,
usage-map and removal rows (11.3, 11.9), with the norms check of every replayed rule fixture, come with
`Status.lean` (item jt-1b); the zone, criteria, deciders and undeclared-word rows (11.4 to 11.7) belong to JT-3 and
JT-4. A difference between this file and a row of section 11 is a finding against the spec or the build, decided
before the row is changed. -/

namespace VE.Judgments.Examples
open Lean VE.Judgments

/-- The refusal text of an answer, if it is one. -/
def errText {α : Type} : Except String α → Option String
  | .error e => some e
  | .ok _ => none

/-- The value of an answer, if it is one. -/
def okVal {α : Type} : Except String α → Option α
  | .ok a => some a
  | .error _ => none

/-! ## 11.1 W2 under the profile, on the wire (decoded by Lean's own readers) -/

def envText : String :=
  "{\"language\": \"ve.core@0.2\", \"profiles\": [\"relational-fol@0\"], " ++
  "\"spec_revision\": \"ve-v0.2-expand2-2026-09-25\", \"vocabulary\": {\"sorts\": " ++
  "{\"person\": {\"description\": \"a person\"}, \"act\": {\"description\": \"an act\"}}, \"predicates\": " ++
  "{\"treats_unfairly\": {\"arguments\": [\"person\", \"person\"], \"description\": \"{0} treats {1} unfairly\"}, " ++
  "\"arbitrary\": {\"arguments\": [\"act\"], \"description\": \"{0} is arbitrary\"}}, \"constants\": {}}}"

def termText (name args : String) : String :=
  "[{\"name\": \"" ++ name ++ "\", \"arguments\": " ++ args ++ ", \"decided_by\": \"unresolved_decider\", " ++
  "\"necessary\": [], \"sufficient\": [], \"factors\": [\"the Declaration gives no test for arbitrariness\"], " ++
  "\"precedents\": [], \"jurisdiction\": \"udhr\", \"version\": 1}]"

/-- One record through W2 three ways (no flag, the flag off, the flag on) and through `records`. -/
def w2Probe (name args : String) :
    Except String (Except String (List String) × Except String (List String) × Except String (List String) ×
      Except String (List Rec)) := do
  let env ← Json.parse envText
  let e ← VE.Route.Gate.decodeEnvelope env
  let rv ← VE.Route.Typed.routeVocabulary e
  let t ← Json.parse (termText name args)
  pure (VE.Discourse.Loader.openTermNames rv t (python := true),
    VE.Discourse.Loader.openTermNames rv t (python := true) (sorts := false),
    VE.Discourse.Loader.openTermNames rv t (python := true) (sorts := true),
    records rv t false none)

def factor : String := "the Declaration gives no test for arbitrariness"

-- J-ο (wire): repeated sorts are W2's refusal with its own text, unless the profile's flag is on (J-λ for W2)
#guard match w2Probe "treats_unfairly" "[\"person\", \"person\"]" with
  | .ok (a, b, c, d) => errText a == some "invalid open-term arguments" &&
      errText b == some "invalid open-term arguments" && okVal c == some ["treats_unfairly"] &&
      okVal d == some [(⟨"treats_unfairly", ["person", "person"], "unresolved_decider", [factor]⟩, 0, 0)]
  | .error _ => false
-- J-α (wire): the same answer all three ways; `records` keeps the factor
#guard match w2Probe "arbitrary" "[\"act\"]" with
  | .ok (a, b, c, d) => okVal a == some ["arbitrary"] && okVal b == some ["arbitrary"] &&
      okVal c == some ["arbitrary"] &&
      okVal d == some [(⟨"arbitrary", ["act"], "unresolved_decider", [factor]⟩, 0, 0)]
  | .error _ => false

/-! ## The environment of 11.2 to 11.7 -/

def table (preds : List (String × List String)) (p : String) : Option (List String) :=
  (preds.find? (·.1 == p)).map Prod.snd

def P : List (String × List String) :=
  [("subjects", ["person", "act"]), ("reports", ["person", "act"]), ("arrest", ["act"]), ("arbitrary", ["act"]),
   ("unreasonable", ["act"]), ("detention", ["act"]), ("unlawful", ["act"]), ("court_ordered", ["act"]),
   ("wrongful_detention", ["act"]), ("unlawful_detention", ["act"]),
   ("natural_and_fundamental_group_unit", ["thing"]), ("treats_unfairly", ["person", "person"]),
   ("gives_serious_uplift", ["act"]), ("deprivation", ["act"]), ("denial", ["act"]),
   ("make_reasonable_efforts", ["person", "act"])]

def E : VE.Environment :=
  { sorts := ["person", "act", "thing"], predicates := table P,
    constants := fun c => if c == "the_family" then some "thing" else none }

def u (p : String) : VE.Formula := .unary p (.var 0)

def defs : List VE.Definitions.Def :=
  [⟨"wrongful_detention", ["act"], .and (u "detention") (u "arbitrary")⟩,
   ⟨"unlawful_detention", ["act"], .and (u "detention") (u "unlawful")⟩]

def regulated : List String := ["subjects", "reports", "make_reasonable_efforts"]

def jrec (name : String) (args : List String) (decider : String := "unresolved_decider")
    (nec suf : Nat := 0) : Rec :=
  (⟨name, args, decider, []⟩, nec, suf)

def J1 : List String := ["arbitrary"]
def guardα : VE.Formula := .and (u "arrest") (u "arbitrary")
def judgment (name : String) (args : List String) : Judgment := ⟨name, args, "unresolved_decider", []⟩

/-! ## 11.2 Admission -/

#guard okVal (admit E defs regulated [jrec "arbitrary" ["act"]]) == some [judgment "arbitrary" ["act"]]   -- J-α
#guard errText (admit E defs regulated [jrec "reasonable_limitation" ["act"]]) ==                        -- J-δ
  some "JudgmentUnbound: reasonable_limitation"
#guard E.predicates "wrongful_detention" == some ["act"]                                                  -- J-π
#guard errText (admit E defs regulated [jrec "wrongful_detention" ["act"]]) ==
  some "JudgmentUnbound: wrongful_detention"
#guard errText (admit E defs regulated [jrec "arbitrary" ["person"]]) ==                                 -- J-ε
  some "JudgmentArguments: arbitrary"
#guard errText (admit E defs regulated [jrec "subjects" ["person", "act"]]) ==                           -- J-ρ
  some "JudgmentRegulated: subjects"
#guard errText (admit E defs regulated [jrec "arbitrary" ["act"] (nec := 1)]) ==                         -- J-ζ
  some "JudgmentCriterionAsUnit: arbitrary"
#guard errText (admit E defs regulated [jrec "arbitrary" ["act"] (suf := 2)]) ==                         -- J-ζ′
  some "JudgmentCriterionAsUnit: arbitrary"
#guard errText (admit E defs regulated [jrec "arbitrary" ["act"] "unstated"]) ==                         -- J-η
  some "JudgmentDecider: arbitrary"
#guard okVal (admit E defs regulated [jrec "treats_unfairly" ["person", "person"]]) ==                   -- J-ο
  some [judgment "treats_unfairly" ["person", "person"]]
#guard okVal (admit E defs regulated [jrec "gives_serious_uplift" ["act"]]) ==                           -- J-ν
  some [judgment "gives_serious_uplift" ["act"]]
#guard okVal (admit E defs regulated [jrec "natural_and_fundamental_group_unit" ["thing"]]) ==           -- J-θ
  some [judgment "natural_and_fundamental_group_unit" ["thing"]]
-- the first fault: record order (order 1), then check order within a record (order 2)
#guard errText (admit E defs regulated
  [jrec "arbitrary" ["act"], jrec "reasonable_limitation" ["act"], jrec "unreasonable" ["person"]]) ==
  some "JudgmentUnbound: reasonable_limitation"
#guard errText (admit E defs regulated [jrec "arbitrary" ["person"] "unstated" 1 0]) ==
  some "JudgmentArguments: arbitrary"
-- each later check of order 2 under the next one's fault: arguments before regulated, regulated before the
-- criteria, the criteria before the decider
#guard errText (admit E defs regulated [jrec "subjects" ["act"]]) ==
  some "JudgmentArguments: subjects"
#guard errText (admit E defs regulated [jrec "subjects" ["person", "act"] "unstated" 1 0]) ==
  some "JudgmentRegulated: subjects"
#guard errText (admit E defs regulated [jrec "arbitrary" ["act"] "unstated" 1 0]) ==
  some "JudgmentCriterionAsUnit: arbitrary"

/-! ## 11.3 Dependence, directly (the one scan) -/

def fγ : VE.Formula := .all "act" (.implies (u "wrongful_detention") (.not (u "court_ordered")))
#guard opensIn J1 [guardα] == ["arbitrary"]
#guard opensIn J1 [u "arrest"] == []
#guard opensIn J1 [fγ] == []
-- the scan answers in `J`'s order, not the formulas'
#guard opensIn ["arrest", "arbitrary"] [u "arbitrary", u "arrest"] == ["arrest", "arbitrary"]

/-! ## J-ω: one word over two sorts is two bound terms (its own environment) -/

def Pω : List (String × List String) :=
  [("subjects_to_measure", ["person", "measure"]), ("subjects_to_interference", ["person", "interference"]),
   ("measure_taken", ["measure"]), ("interference_with_privacy", ["interference"]),
   ("arbitrary_measure", ["measure"]), ("arbitrary_interference", ["interference"])]
def Eω : VE.Environment :=
  { sorts := ["person", "measure", "interference"], predicates := table Pω, constants := fun _ => none }
def regulatedω : List String := ["subjects_to_measure", "subjects_to_interference"]
#guard okVal (admit Eω [] regulatedω
  [jrec "arbitrary_measure" ["measure"], jrec "arbitrary_interference" ["interference"]]) ==
  some [judgment "arbitrary_measure" ["measure"], judgment "arbitrary_interference" ["interference"]]
-- `names` reads the admitted judgments' names, in record order
#guard (okVal (admit Eω [] regulatedω
  [jrec "arbitrary_measure" ["measure"], jrec "arbitrary_interference" ["interference"]])).map names ==
  some ["arbitrary_measure", "arbitrary_interference"]
theorem names_omega : (okVal (admit Eω [] regulatedω
    [jrec "arbitrary_measure" ["measure"], jrec "arbitrary_interference" ["interference"]])).map names =
    some ["arbitrary_measure", "arbitrary_interference"] := by
  decide
#guard errText (admit Eω [] regulatedω [jrec "arbitrary_measure" ["interference"]]) ==                    -- J-ω′
  some "JudgmentArguments: arbitrary_measure"

end VE.Judgments.Examples
