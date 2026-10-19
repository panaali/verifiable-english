import VE.Judgments.Status
import VE.Norms.Checks
import VE.Route.Typed

/-! The JT-1 fixtures of docs/spec/judgment-terms.md section 11 (11.1 to 11.3, and 11.9), as `#guard` checks on the
built definitions. Each value is the one the spec's stub computed by `#eval`. Every rule fixture that JT-2 replays
through the service is also a document the norms route's own check accepts (`VE.Norms.validate`), and every formula
fixture type-checks in its environment (11.9). The zone, criteria, deciders and undeclared-word rows (11.4 to 11.7)
belong to JT-3 and JT-4. A difference between this file and a row of section 11 is a finding against the spec or the
build, decided before the row is changed. -/

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
def and3 (a b c : VE.Formula) : VE.Formula := .and a (.and b c)

def defs : List VE.Definitions.Def :=
  [⟨"wrongful_detention", ["act"], .and (u "detention") (u "arbitrary")⟩,
   ⟨"unlawful_detention", ["act"], .and (u "detention") (u "unlawful")⟩]

def regulated : List String := ["subjects", "reports", "make_reasonable_efforts"]

def jrec (name : String) (args : List String) (decider : String := "unresolved_decider")
    (nec suf : Nat := 0) : Rec :=
  (⟨name, args, decider, []⟩, nec, suf)

/-- A forbidding rule on `pred` (default `subjects(person, act)`): its guard is typed in `[act, person]`, so `.var 0`
    is the act. -/
def rule (name : String) (guard : VE.Formula) (pred : String := "subjects") : VE.Norms.Node :=
  VE.Norms.Checks.rule name pred false guard

def view (id meaning : String) (listed : List String) (own : Option Content) (set : Option ActiveSet := none)
    (asserted : Bool := false) : UnitView :=
  ⟨id, meaning, listed, asserted, own, set⟩

def J1 : List String := ["arbitrary"]
def J2 : List String := ["arbitrary", "unreasonable"]
def guardα : VE.Formula := .and (u "arrest") (u "arbitrary")
def uα (meaning : String) (listed : List String := ["arbitrary"]) : UnitView :=
  view "u1" meaning listed (some (.rule (rule "no-arbitrary-arrest" guardα)))
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

/-! ## 11.3 Status and usage -/

-- J-α
#guard okVal (status defs J1 (uα "open")) == some "OPEN"
#guard usageMap defs J1 [uα "open"] == ([("arbitrary", ["u1"])], [])
-- J-β
#guard errText (status defs J1 (uα "specified" [])) == some "JudgmentNotChecked: u1 arbitrary"
-- J-γ, J-γ′ (through a definition), J-γ″ (a definition that does not reach)
def fγ : VE.Formula := .all "act" (.implies (u "wrongful_detention") (.not (u "court_ordered")))
def fγ'' : VE.Formula := .all "act" (.implies (u "unlawful_detention") (.not (u "court_ordered")))
def ruleγ' : VE.Norms.Node := rule "no-wrongful-detention" (u "wrongful_detention")
#guard errText (status defs J1 (view "u1" "specified" [] (some (.formula fγ)))) ==
  some "JudgmentNotChecked: u1 arbitrary"
#guard errText (status defs J1 (view "u1" "specified" [] (some (.rule ruleγ')))) ==
  some "JudgmentNotChecked: u1 arbitrary"
#guard okVal (status defs J1 (view "u1" "specified" [] (some (.formula fγ'')))) == some "CHECKED"
-- dependence, directly and through definitions
#guard opensIn J1 [guardα] == ["arbitrary"]
#guard opensIn J1 [u "arrest"] == []
#guard opensIn J1 [fγ] == []
-- the scan answers in `J`'s order, not the formulas'
#guard opensIn ["arrest", "arbitrary"] [u "arbitrary", u "arrest"] == ["arrest", "arbitrary"]
#guard dependsOn defs J1 [fγ] == ["arbitrary"]
#guard dependsOn [] J1 [fγ] == []
-- J-θ
def uθ : UnitView := view "u1" "open" ["natural_and_fundamental_group_unit"]
  (some (.formula (.unary "natural_and_fundamental_group_unit" (.const "the_family")))) (asserted := true)
#guard okVal (status defs ["natural_and_fundamental_group_unit"] uθ) == some "OPEN"
#guard usageMap defs ["natural_and_fundamental_group_unit"] [uθ] ==
  ([("natural_and_fundamental_group_unit", ["u1"])], [])
-- J-μ
def uμ : UnitView := view "u1" "specified" [] (some (.rule (rule "no-arrest" (u "arrest"))))
#guard okVal (status defs J1 uμ) == some "CHECKED"
#guard usageMap defs J1 [uμ] == ([], ["arbitrary"])
-- J-ξ: an authored set (its one signed, asserted reading) on a unit with no content; the reading uses `arbitrary`
def fξ : VE.Formula := .all "act" (.implies (.and (u "deprivation") (u "arbitrary")) .bottom)
def uξ : UnitView := view "u055" "open" ["arbitrary"] none (some ⟨true, true, [some (.formula fξ)]⟩)
#guard okVal (status defs J1 uξ) == some "OPEN"
#guard uξ.legacy == "CHECKED"
#guard usageMap defs J1 [uξ] == ([("arbitrary", ["u055"])], [])
-- J-ξ′: an open set of u055's two scopes, which differ; a model with one act, a denial that is not arbitrary
def fξw : VE.Formula :=
  .all "act" (.implies (.and (.or (u "deprivation") (u "denial")) (u "arbitrary")) .bottom)
def fξn : VE.Formula :=
  .all "act" (.and (.implies (.and (u "deprivation") (u "arbitrary")) .bottom) (.implies (u "denial") .bottom))
def uξ' : UnitView :=
  view "u055" "open" ["arbitrary"] none (some ⟨false, true, [some (.formula fξw), some (.formula fξn)]⟩)
def mξ : VE.FiniteModel String :=
  { domains := fun s => if s == "act" then ["a"] else [],
    constants := fun _ => none,
    relations := fun p => if p == "denial" then [["a"]] else [] }
#guard (fξw.eval mξ [], fξn.eval mξ []) == (true, false)
#guard okVal (status defs J1 uξ') == some "OPEN"
#guard uξ'.legacy == "OPEN"
#guard usageMap defs J1 [uξ'] == ([("arbitrary", ["u055"])], [])
-- J-υ: a contextual unit whose formula uses `arbitrary`: LABELLED today, OPEN under the profile
def uυ : UnitView := view "u1" "contextual" [] (some (.formula (.all "act" (.implies guardα .bottom))))
#guard okVal (status defs J1 uυ) == some "OPEN"
#guard uυ.legacy == "LABELLED"
-- J-σ, J-τ
def uτ : UnitView := view "u1" "open" ["arbitrary", "unreasonable"] (some (.rule (rule "r" guardα)))
def ruleσ : VE.Norms.Node := rule "r" (and3 (u "arrest") (u "arbitrary") (u "unreasonable"))
#guard errText (status defs J2 (view "u1" "open" ["arbitrary"] (some (.rule ruleσ)))) ==
  some "JudgmentNotListed: u1 unreasonable"
#guard errText (status defs J2 uτ) == some "JudgmentListedUnused: u1 unreasonable"
-- J-τ′: `JudgmentListedUnused` only on a complete unit; an active set takes precedence over own content
def cα : Option Content := some (.formula (.all "act" (.implies guardα .bottom)))
def τ'a : UnitView := view "u1" "open" J2 none
def τ'b : UnitView := view "u1" "open" J2 none (some ⟨false, false, [none, none]⟩)
def τ'c : UnitView := view "u1" "open" J2 none (some ⟨false, false, [cα, none]⟩)
def τ'd : UnitView := view "u1" "open" J2 (some (.rule (rule "r" guardα))) (some ⟨false, false, [none]⟩)
def τ'e : UnitView := view "u1" "open" J2 none (some ⟨true, true, [cα]⟩)
#guard [τ'a, τ'b, τ'c, τ'd, τ'e].map (fun v => (v.complete, okVal (status defs J2 v), v.legacy)) ==
  [(false, some "OPEN", "OPEN"), (false, some "OPEN", "OPEN"), (false, some "OPEN", "OPEN"),
   (false, some "OPEN", "OPEN"), (true, none, "CHECKED")]
#guard errText (status defs J2 τ'e) == some "JudgmentListedUnused: u1 unreasonable"
-- J-λ: without bound judgments every status is today's
#guard [uα "open", uα "specified" [], view "u1" "specified" [] (some (.formula fγ)), uθ, uμ, uξ, uξ', uυ].map
  (fun v => (okVal (status defs [] v), v.legacy)) ==
  [(some "OPEN", "OPEN"), (some "CHECKED", "CHECKED"), (some "CHECKED", "CHECKED"), (some "OPEN", "OPEN"),
   (some "CHECKED", "CHECKED"), (some "CHECKED", "CHECKED"), (some "OPEN", "OPEN"), (some "LABELLED", "LABELLED")]
-- J-χ (F3): a rule whose guard reads the regulated predicate that J-α's judgment rule decides stays CHECKED
def uχ : UnitView := view "u2" "specified" []
  (some (.rule (rule "report-when-forbidden" (.binary "subjects" (.var 1) (.var 0)) "reports")))
#guard okVal (status defs J1 uχ) == some "CHECKED"
#guard usageMap defs J1 [uα "open", uχ] == ([("arbitrary", ["u1"])], [])
-- 11.4's asserted criterion unit `u2` ("No arrest ordered by a court is arbitrary."): OPEN
def uι : UnitView := view "u2" "open" ["arbitrary"] (some (.formula
  (.all "act" (.implies (.and (u "arrest") (u "court_ordered")) (.not (u "arbitrary")))))) (asserted := true)
#guard okVal (status defs J1 uι) == some "OPEN"

/-! ## J-ω: one word over two sorts is two bound terms, one usage row each (its own environment) -/

def Pω : List (String × List String) :=
  [("subjects_to_measure", ["person", "measure"]), ("subjects_to_interference", ["person", "interference"]),
   ("measure_taken", ["measure"]), ("interference_with_privacy", ["interference"]),
   ("arbitrary_measure", ["measure"]), ("arbitrary_interference", ["interference"])]
def Eω : VE.Environment :=
  { sorts := ["person", "measure", "interference"], predicates := table Pω, constants := fun _ => none }
def regulatedω : List String := ["subjects_to_measure", "subjects_to_interference"]
def Jω : List String := ["arbitrary_measure", "arbitrary_interference"]
def u037ω : UnitView := view "u037" "open" ["arbitrary_measure"]
  (some (.rule (rule "no-arbitrary-measure" (.and (u "measure_taken") (u "arbitrary_measure")) "subjects_to_measure")))
def u045aω : UnitView := view "u045a" "open" ["arbitrary_interference"]
  (some (.rule (rule "no-arbitrary-interference" (.and (u "interference_with_privacy") (u "arbitrary_interference"))
    "subjects_to_interference")))
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
#guard [u037ω, u045aω].map (fun v => okVal (status [] Jω v)) == [some "OPEN", some "OPEN"]
#guard usageMap [] Jω [u037ω, u045aω] == ([("arbitrary_measure", ["u037"]), ("arbitrary_interference", ["u045a"])], [])

/-! ## Rows the build adds (internal: no row of section 11, not replayed), one per definition no row reaches -/

-- a rule's carve-outs are read: the guard is judgment-free, the carve-out uses `arbitrary`
def ruleκ : VE.Norms.Node := VE.Norms.Checks.rule "no-arrest" "subjects" false (u "arrest") [u "arbitrary"]
theorem formulas_carve : (Content.rule ruleκ).formulas = [u "arrest", u "arbitrary"] := rfl
#guard errText (status defs J1 (view "u1" "specified" [] (some (.rule ruleκ)))) ==
  some "JudgmentNotChecked: u1 arbitrary"
-- a definition reached through another: `prolonged_detention` uses `wrongful_detention`, which uses `arbitrary`
def defsChain : List VE.Definitions.Def :=
  defs ++ [⟨"prolonged_detention", ["act"], .and (u "wrongful_detention") (u "prolonged")⟩]
theorem reachedBodies_chain : reachedBodies defsChain [u "prolonged_detention"] =
    [.and (u "detention") (u "arbitrary"), .and (u "wrongful_detention") (u "prolonged")] := by decide
#guard dependsOn defsChain J1 [u "prolonged_detention"] == ["arbitrary"]
-- `viewOf` takes the unit's own active set from the loader's list, with its candidates (J-ξ's view)
def fsξ : VE.Discourse.FrontSet := ⟨"s1", "u055", 1, "authored", []⟩
theorem viewOf_xi : viewOf [(fsξ, [true])] (fun _ => [some (.formula fξ)]) "u055" "open" ["arbitrary"] false none =
    ⟨"u055", "open", ["arbitrary"], false, none, some ⟨true, true, [some (.formula fξ)]⟩⟩ := by decide
#guard viewOf [(fsξ, [true])] (fun _ => [some (.formula fξ)]) "u055" "open" ["arbitrary"] false none == uξ
#guard (viewOf [(fsξ, [true])] (fun _ => [some (.formula fξ)]) "u1" "open" ["arbitrary"] false none).set == none

/-! ## 11.9 Removal: both hypotheses of `status_remove_unused` are needed -/

-- J-β lists nothing and depends on `arbitrary`: removing it would hide the refusal
#guard errText (status defs J1 (uα "specified" [])) == some "JudgmentNotChecked: u1 arbitrary"
#guard okVal (status defs (J1.filter (· != "arbitrary")) (uα "specified" [])) == some "CHECKED"
#guard usageMap defs J1 [uα "specified" []] == ([("arbitrary", ["u1"])], [])
-- J-τ lists `unreasonable` and does not depend on it: removing it would hide the refusal too
#guard okVal (status defs (J2.filter (· != "unreasonable")) uτ) == some "OPEN"
#guard usageMap defs J2 [uτ] == ([("arbitrary", ["u1"])], ["unreasonable"])
-- J-μ neither depends on nor lists `arbitrary`: removing it changes nothing
#guard okVal (status defs (J1.filter (· != "arbitrary")) uμ) == some "CHECKED"

/-! ## 11.9 The fixtures JT-2 replays are valid documents -/

open VE.Norms in
def rulesOf (vs : List UnitView) : List Node :=
  vs.filterMap fun v => match v.own with
    | some (.rule N) => some N
    | _ => none

open VE.Norms VE.Norms.Checks in
def docω (nodes : List Node) : Doc :=
  let regs := [perm "subjects_to_measure" ["person", "measure"] false "{0} subject someone to {1}",
    perm "subjects_to_interference" ["person", "interference"] false "{0} interfere with {1}"]
  mkDoc ["person", "measure", "interference"] (Pω.filter fun p => !(regs.map (·.name)).contains p.1) regs [] nodes

open VE.Norms VE.Norms.Checks in
/-- 11.3's environment as one norm document: its three regulated predicates and its two W3 definitions. -/
def doc11 (nodes : List Node) : Doc :=
  let regs := [perm "subjects" ["person", "act"] false "{0} subject someone to {1}",
    perm "reports" ["person", "act"] false "{0} report {1}",
    perm "make_reasonable_efforts" ["person", "act"] false "{0} make reasonable efforts at {1}"]
  let ds : List Definition := defs.map fun d => ⟨d.name, d.args, d.body⟩
  mkDoc ["person", "act", "thing"] (P.filter fun p => !((regs.map (·.name)) ++ ds.map (·.name)).contains p.1)
    regs ds nodes

#guard okVal (VE.Norms.validate (docω (rulesOf [u037ω, u045aω]))) == some ()                              -- J-ω
-- draft 3's J-ω, on `subjects`, which J-ω's environment does not declare
#guard errText (VE.Norms.validate (docω ((rulesOf [u037ω, u045aω]).map ({ · with pred := "subjects" })))) ==
  some "UnknownSymbol: regulated predicate subjects"
#guard [rulesOf [uα "open"], rulesOf [uα "specified" []], [ruleγ'], rulesOf [uμ], [ruleσ], rulesOf [uτ],
  rulesOf [τ'd], rulesOf [uα "open", uχ]].all fun ns => okVal (VE.Norms.validate (doc11 ns)) == some ()
#guard [fγ, fγ'', .unary "natural_and_fundamental_group_unit" (.const "the_family"), fξ, fξw, fξn,
  .all "act" (.implies guardα .bottom)].all
  fun φ => φ.check E []

end VE.Judgments.Examples
