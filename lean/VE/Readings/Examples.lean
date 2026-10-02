import VE.Readings.Separate
import VE.Rights.Examples

/-! The item-1 fixtures of docs/spec/composition-s1.md 9.2 on one small document, as build-time checks (`#guard`:
the build fails if one is false). Environment K: sorts `agent`, `user`; the base predicate `asks(agent, user)`;
the obligations `avoid_required` and `help_required`, deny by default, no dual. `S` is the strict rule
`no-deception` on `+avoid_required`, `Df` the same rule as a default rule decided by `unstated`; set `rs1` on unit
`u1` is {0: `S`, 1: `Df`}; `m0` has one agent `a`, one user `u` and `asks` empty; `q0` is the outcome probe on
`avoid_required` at `(a, u)`. The texts of the diagnostics are the wire's (`Wire.lean`); here the Boolean checks
they report. K10's base predicate `ve__bit__1__0` and K18 (`norm-defaults@0`) are the wire decoder's checks, since
`VE.Environment` lists no predicate names and `Chain` has no `norm-defaults@0` case. -/
namespace VE.Readings.Examples
open VE.Readings
open VE.Norms.Checks (envOf perm oblig)
open VE.Rights.Examples (noSoft strictNode defaultNode block line l29 arrestClaim mkRights)
open VE.SoftNorms (SoftNode)

def regsK : List VE.Norms.Regulated :=
  [oblig "avoid_required" ["agent", "user"] false none "{0} avoid deceiving {1}",
   oblig "help_required" ["agent", "user"] false none "{0} help {1}"]
def frameWith (soft : VE.SoftNorms.SoftEnv) : VE.Rights.RightsDoc where
  soft := ⟨envOf ["agent", "user"] ([("asks", ["agent", "user"])] ++ regsK.map (fun r => (r.name, r.sorts))), [], soft,
    ⟨regsK, [], []⟩⟩
  rights := ⟨[], [], [], []⟩
  rs := []
  limits := []
  bars := []
  outsideCites := []
  sourceOrder := some []
def frameK := frameWith noSoft
def S : SoftNode := strictNode "no-deception" "avoid_required" true
def Df : SoftNode := defaultNode "no-deception" "avoid_required" true
def cand (id : String) (N : SoftNode) : Candidate := ⟨id, some (.norm N), [], []⟩
def rs1 : ReadingSet := ⟨"rs1", "u1", 1, [cand "strict" S, cand "default" Df]⟩
def docK (items : List Item) (ch : Chain := .soft) (fr := frameK) : Doc := ⟨ch, fr, items, [], []⟩
def K1 : Doc := docK [.set rs1]
def modelK (users : List String) (asks : List (List String)) : VE.FiniteModel String where
  domains s := match s with | "agent" => ["a"] | "user" => users | _ => []
  constants _ := none
  relations p := if p == "asks" then asks else []
def m0 := modelK ["u"] []
def q0 : Probe String := .outcome "avoid_required" ["a", "u"]
def exc (r : String) : GenKey := .excepted r none
def sit (M : VE.FiniteModel String) (fx dec : List (GenKey × List (List String))) (q : Probe String) (v : Bool) :
    Situation String := ⟨M, fx, dec, q, v⟩

-- K19
def frameR : VE.Rights.RightsDoc :=
  { mkRights ["state", "person"] [("arbitrary_arrest", ["state", "person"]), ("journalist", ["person"])]
    [perm "arrest_permitted" ["state", "person"] true "{0} arrest {1}"] [] block [] [] [] with sourceOrder := some [] }
def arrestDefault : VE.Rights.SourceLine :=
  line .claim { defaultNode "no-arbitrary-arrest" "arrest_permitted" false with guard := .binary "arbitrary_arrest" (.var 1) (.var 0) }
def rs9 : ReadingSet := ⟨"rs9", "u9", 1, [⟨"strict", some (.right ⟨"r9", "person", .top, [arrestClaim]⟩), [], []⟩,
  ⟨"default", some (.right ⟨"r9", "person", .top, [arrestDefault]⟩), [], []⟩]⟩
def K19 : Doc := ⟨.rights, frameR, [.set rs9, .fixed "u29" (.limitation l29) []], [], []⟩
def mR : VE.FiniteModel String where
  domains s := match s with | "state" => ["Texas"] | "person" => ["Ann", "Bob"] | _ => []
  constants _ := none
  relations p := if p == "arbitrary_arrest" then [["Texas", "Ann"]] else []

/-! ## K1: strict and default twins -/

#guard WellFormedDoc K1
#guard ownedKeys K1 "rs1" 0 == [] && ownedKeys K1 "rs1" 1 == [exc "no-deception"]
#guard separates K1 "rs1" 1 0 (sit m0 [] [(exc "no-deception", [["a", "u"]])] q0 false)
-- the strict reading as witness: the default reading reaches `true` with the empty table
#guard !separates K1 "rs1" 0 1 (sit m0 [] [] q0 true)
#guard decisionOnly K1 "rs1" 0 1 == some (exc "no-deception")
#guard cells K1 "rs1" 1 m0 == 1 && (assignments K1 "rs1" 1 m0).length == 2

/-! ## K2: an unsatisfiable necessary condition -/

def K2 : Doc := docK [.set ⟨"rs1", "u1", 1, [cand "strict" S,
  cand "default" { Df with exception := some ⟨some "unstated", [], [.bottom], []⟩ }]⟩]
#guard WellFormedDoc K2
-- K1's σ: the witness's completion violates a generated premise
#guard !sideValid K2 "rs1" 1 m0 [(exc "no-deception", [["a", "u"]])]
#guard !separates K2 "rs1" 1 0 (sit m0 [] [(exc "no-deception", [["a", "u"]])] q0 false)
-- the same base, witness 1, no decision, value true: does not separate
#guard !separates K2 "rs1" 1 0 (sit m0 [] [] q0 true)
-- no probe of `probesOf` separates the pair on `m0` without a decision
#guard (probesOf K2 m0).all (fun q => [true, false].all (fun v =>
  !separates K2 "rs1" 0 1 (sit m0 [] [] q v) && !separates K2 "rs1" 1 0 (sit m0 [] [] q v)))

/-! ## K2b: a base with a tuple on a generated predicate is not over the author's vocabulary -/

def m0b : VE.FiniteModel String :=
  { m0 with relations := fun p => if p == "soft__excepted__no_deception" then [["a", "u"]] else m0.relations p }

theorem k2b_not_admissible : ¬ m0b.asStructure.Admissible (authorEnv K2) := by
  rintro ⟨_, hr⟩
  obtain ⟨ss, hss, _⟩ := hr "soft__excepted__no_deception" ["a", "u"]
    (by show ["a", "u"] ∈ m0b.relations "soft__excepted__no_deception"; decide)
  have hE : K2.frame.soft.E.predicates "soft__excepted__no_deception" = none := by decide
  simp only [authorEnv, VE.Norms.envAt, VE.Norms.hide] at hss
  split at hss
  · cases hss
  · rw [show K2.frame.soft.base.E = K2.frame.soft.E from rfl, hE] at hss; cases hss

theorem k2b_achieves_neither (i : Nat) (F : Tables String) (q : Probe String) (v : Bool) :
    ¬ Achieves K2 "rs1" i m0b.asStructure F q v :=
  fun h => k2b_not_admissible h.1

/-! ## K3: a renamed twin is separated by no probe -/

def K3 : Doc := docK [.set ⟨"rs1", "u1", 1,
  [cand "a" { S with name := "no-deception-a" }, cand "b" { S with name := "no-deception-b" }]⟩]
#guard WellFormedDoc K3
#guard (probesOf K3 m0).all (fun q => [true, false].all (fun v =>
  !separates K3 "rs1" 0 1 (sit m0 [] [] q v) && !separates K3 "rs1" 1 0 (sit m0 [] [] q v)))
#guard observeAll K3 "rs1" 0 m0 [] == observeAll K3 "rs1" 1 m0 []
def K3d : Doc := docK [.set ⟨"rs1", "u1", 1,
  [cand "a" { Df with name := "no-deception-a" }, cand "b" { Df with name := "no-deception-b" }]⟩]
#guard WellFormedDoc K3d
-- the other reading empties `avoid_required` with its own table
#guard !separates K3d "rs1" 0 1 (sit m0 [] [(exc "no-deception-a", [["a", "u"]])] q0 false)
#guard sideValue K3 "rs1" 0 m0 [] (.selects "norm" "avoid_required" ["a", "u"]) ==
  sideValue K3 "rs1" 1 m0 [] (.selects "norm" "avoid_required" ["a", "u"])

/-! ## K4: two acts -/

def rs4 (id : String) : ReadingSet := ⟨id, "u1", 1,
  [cand "avoid" { S with name := "avoid-x" }, cand "help" (strictNode "help-x" "help_required" true)]⟩
def K4 : Doc := docK [.set (rs4 "rs1")]
#guard WellFormedDoc K4
#guard separates K4 "rs1" 0 1 (sit m0 [] [] q0 true)
#guard actOnly K4 "rs1" 0 1 == some ("avoid_required", "help_required")

/-! ## K5: a fixed default rule's table is shared -/

def beKind : SoftNode := defaultNode "be-kind" "help_required" true
def K5 : Doc := docK [.fixed "u0" (.norm beKind) [], .set rs1]
#guard WellFormedDoc K5
#guard !owned K5 "rs1" 0 (exc "be-kind") && !owned K5 "rs1" 1 (exc "be-kind")
#guard separates K5 "rs1" 1 0 (sit m0 [(exc "be-kind", [["a", "u"]])] [(exc "no-deception", [["a", "u"]])] q0 false)
#guard cells K5 "rs1" 0 m0 == 0 && cells K5 "rs1" 1 m0 == 1
-- the same table under `decisions`: not owned by the witness
#guard !situationWF K5 "rs1" 1 0
  (sit m0 [] [(exc "be-kind", [["a", "u"]]), (exc "no-deception", [["a", "u"]])] q0 false)
#guard decisionOnly K5 "rs1" 0 1 == some (exc "no-deception")

/-! ## K6: a fixed strict rule against the twins -/

def K6 : Doc := docK [.fixed "u0" (.norm (strictNode "never-avoid" "avoid_required" false)) [], .set rs1]
#guard WellFormedDoc K6
#guard sideValue K6 "rs1" 1 m0 [] q0 == some false
#guard sideValue K6 "rs1" 0 m0 [] q0 == none
#guard separates K6 "rs1" 1 0 (sit m0 [] [] q0 false)
#guard decisionOnly K6 "rs1" 0 1 == none

/-! ## K7: the bound on the other side's cells -/

def users13 : List String := (List.range 13).map (fun k => s!"u{k + 1}")
def m13 := modelK users13 []
#guard cells K1 "rs1" 1 m13 == 13
#guard !separates K1 "rs1" 0 1 (sit m13 [] [] (.outcome "avoid_required" ["a", "u1"]) true)

/-! ## K8: distinct declarations across sets and fixed units -/

#guard !distinctAcrossSets (docK [.set rs1, .set ⟨"rs2", "u2", 1, [cand "x" { S with pred := "help_required" }]⟩])
#guard !distinctAcrossSets (docK [.fixed "u0" (.norm beKind) [],
  .set ⟨"rs1", "u1", 1, [cand "strict" S, cand "kind" { beKind with mode := .strict, exception := none }]⟩])
def rs2kind : ReadingSet := ⟨"rs2", "u2", 1,
  [cand "strict" (strictNode "be-kind" "help_required" true), cand "default" beKind]⟩
#guard !distinctAcrossSets (docK [.set rs1, .set rs2kind,
  .fixed "u3" (.norm (strictNode "twice-x" "avoid_required" false .top [] ["no-deception"])) [],
  .fixed "u4" (.norm (strictNode "twice-x" "help_required" false .top [] ["be-kind"])) []])

/-! ## K9: an interface name -/

def exceptX : SoftNode := strictNode "except-x" "avoid_required" false (.binary "asks" (.var 1) (.var 0)) [] ["no-deception"]
def K9 : Doc := docK [.set rs1, .fixed "u3" (.norm exceptX) []]
#guard WellFormedDoc K9
#guard interfaceClosed K9
#guard attached K9 "u3" == ["rs1"]
#guard (one K9 "rs1" 0).1.soft.T.nodes.any (·.name == "except-x")
def K9b : Doc := docK [.set rs1, .set (rs4 "rs2"), .fixed "u3" (.norm exceptX) []]
#guard !(one K9b "rs2" 0).1.soft.T.nodes.any (·.name == "except-x")
#guard !interfaceClosed (docK [.set ⟨"rs1", "u1", 1, [cand "strict" S, cand "default" { Df with name := "no-deceit" }]⟩,
  .fixed "u3" (.norm exceptX) []])

/-! ## K10: reserved names -/

#guard !reservedFree (docK [.set ⟨"rs1", "u1", 1, [cand "strict" { S with name := "rd-1-x" }, cand "default" Df]⟩])
#guard reservedFree K1

/-! ## K11: a default candidate over a hard fixed rule -/

def K11 : Doc := docK [.fixed "u0" (.norm (strictNode "be-strict" "avoid_required" true)) [],
  .set ⟨"rs1", "u1", 1, [cand "strict" S, cand "default" { Df with over := ["be-strict"] }]⟩]
#guard !sideWF K11 (one K11 "rs1" 1)
#guard match VE.SoftNorms.validateSoft (one K11 "rs1" 1).1.soft with
  | .error e => e == "SoftOverHard: rule no-deception over be-strict"
  | .ok () => false
#guard !WellFormedDoc K11

/-! ## K12, K13: assertions -/

def asksAll : VE.Formula := .all "agent" (.all "user" (.binary "asks" (.var 1) (.var 0)))
def K12 : Doc := docK [.set ⟨"rs1", "u1", 1, [⟨"assert", some (.assertion asksAll), [], []⟩, cand "strict" S]⟩]
#guard WellFormedDoc K12
#guard separates K12 "rs1" 1 0 (sit m0 [] [] q0 true)
#guard separates K12 "rs1" 1 0 (sit m0 [] [] .holds true)
def K13 : Doc := docK [.set ⟨"rs1", "u1", 1, [⟨"asks", some (.assertion asksAll), [], []⟩,
  ⟨"not-asks", some (.assertion (.all "agent" (.all "user" (.not (.binary "asks" (.var 1) (.var 0)))))), [], []⟩,
  cand "strict" S]⟩]
#guard WellFormedDoc K13
#guard separates K13 "rs1" 1 0 (sit m0 [] [] .holds true)

/-! ## K14: no admissible completion of the default reading -/

def K14 : Doc := docK [.set ⟨"rs1", "u1", 1, [cand "strict" S,
  cand "default" { Df with exception := some ⟨some "unstated", [.binary "asks" (.var 1) (.var 0)], [.bottom], []⟩ }]⟩]
def m1 := modelK ["u"] [["a", "u"]]
#guard WellFormedDoc K14
#guard (assignments K14 "rs1" 1 m1).all (fun G => !sideValid K14 "rs1" 1 m1 G)
#guard separates K14 "rs1" 0 1 (sit m1 [] [] q0 true)
#guard decisionOnly K14 "rs1" 0 1 == none

/-! ## K15: a pending candidate -/

def rs15 : ReadingSet := ⟨"rs1", "u1", 1, [cand "strict" S, ⟨"pending", none, [], []⟩]⟩
#guard WellFormedDoc (docK [.set rs15])
#guard !interfaceClosed (docK [.set rs15, .fixed "u3" (.norm exceptX) []])

/-! ## K16: a formula-only set -/

def K16 : Doc := docK [.fixed "u0" (.norm S) [],
  .set ⟨"rs1", "u1", 1, [⟨"a", some (.assertion asksAll), [], []⟩, ⟨"b", some (.assertion (.not asksAll)), [], []⟩]⟩]
#guard WellFormedDoc K16
#guard (one K16 "rs1" 0).1.soft.T.nodes == (free K16).1.soft.T.nodes

/-! ## K17: the norms chain -/

def K17 : Doc := docK [.set (rs4 "rs1")] .norms
#guard WellFormedDoc K17
#guard separates K17 "rs1" 0 1 (sit m0 [] [] q0 true)
#guard actOnly K17 "rs1" 0 1 == some ("avoid_required", "help_required")
-- a default candidate is no strict rule
#guard !chainWF .norms (one (docK [.set rs1] .norms) "rs1" 1).1

/-! ## K19: a right under a fixed limitation -/
def σ19 : Situation String :=
  sit mR [] [(exc "no-arbitrary-arrest", [["Texas", "Ann"]])] (.outcome "arrest_permitted" ["Texas", "Ann"]) true
#guard WellFormedDoc K19
#guard ![GenKey.lim "l29" "arrest_permitted", .cond "l29" "arrest_permitted" "determined_by_law",
  .cond "l29" "arrest_permitted" "solely_for_permitted_purpose"].any (fun k => owned K19 "rs9" 0 k || owned K19 "rs9" 1 k)
#guard ownedKeys K19 "rs9" 0 == []
#guard separates K19 "rs9" 1 0 σ19
#guard decisionOnly K19 "rs9" 0 1 == some (exc "no-arbitrary-arrest")
#guard (VE.Rights.limitationScope (one K19 "rs9" 1).1 []).map (·.text) ==
  ["UnlicensedLimitation: exception of rule no-arbitrary-arrest on right r9"]
#guard VE.Rights.limitationScope (one K19 "rs9" 0).1 [] == []

/-! ## K20: a fixed unit attached to two sets -/

def bothX (over : List String) : SoftNode :=
  strictNode "both-x" "avoid_required" false (.binary "asks" (.var 1) (.var 0)) [] over
def K20 (over : List String) : Doc := docK [.set rs1, .set rs2kind, .fixed "u3" (.norm (bothX over)) []]
#guard interfaceClosed (K20 ["no-deception", "be-kind"])
#guard attached (K20 ["no-deception", "be-kind"]) "u3" == ["rs1", "rs2"]
#guard !singlyAttached (K20 ["no-deception", "be-kind"])
#guard attached (K20 ["no-deception"]) "u3" == ["rs1"]
#guard singlyAttached (K20 ["no-deception"])
#guard WellFormedDoc (K20 ["no-deception"])

/-! ## K21: malformed situations -/

-- (a) a shared table on a key neither reading's document generates
#guard !situationWF K1 "rs1" 1 0 (sit m0 [(exc "be-kind", [["a", "u"]])] [(exc "no-deception", [["a", "u"]])] q0 false)
#guard !separates K1 "rs1" 1 0 (sit m0 [(exc "be-kind", [["a", "u"]])] [(exc "no-deception", [["a", "u"]])] q0 false)
-- (b) a key listed twice
#guard !situationWF K5 "rs1" 1 0
  (sit m0 [(exc "be-kind", [["a", "u"]]), (exc "be-kind", [["a", "u"]])] [(exc "no-deception", [["a", "u"]])] q0 false)
-- (c) an ill-typed table on a key only the other reading's document generates
def holistic : VE.SoftNorms.SoftEnv :=
  ⟨[], ["lo", "hi"], [("hi", "lo")], [], .holistic, some "unstated", none, [],
   VE.SoftNorms.closureOf ["lo", "hi"] [("hi", "lo")]⟩
def K21c : Doc := docK [.fixed "u0" (.norm { Df with name := "never-avoid-d", sign := false, rank := some "hi" }) [],
  .set ⟨"rs1", "u1", 1, [cand "strict" { S with rank := some "lo" }, cand "default" { Df with rank := some "lo" }]⟩]
  .soft (frameWith holistic)
def σ21c : Situation String := sit m0 [(.outweighs "avoid_required" "lo" "hi", [["u", "a"]])] [] q0 true
#guard WellFormedDoc K21c
#guard (genKeys (one K21c "rs1" 1).1).any (·.1 == .outweighs "avoid_required" "lo" "hi")
#guard !(genKeys (one K21c "rs1" 0).1).any (·.1 == .outweighs "avoid_required" "lo" "hi")
#guard !situationWF K21c "rs1" 0 1 σ21c
#guard !separates K21c "rs1" 0 1 σ21c

/-! ## `genKeys_nodup` as approved does not hold

`WellFormedRights` accepts a document whose `sourceOrder` lists one default fan-out line twice: the two copies are
four instances `rights-fan-1` to `rights-fan-4` with distinct rule names, and two pairs of them carry the same source
key `excepted no-torture (bearer b)`. `one D s i` never builds such an order (each unit's lines are appended once),
so the statement needs a hypothesis on `sourceOrder`; it is reported against spec 8.3 and not proved here. -/

def fanDefault : VE.Rights.SourceLine :=
  ⟨.claim, some (defaultNode "no-torture" "torture_permitted_state" false), none, none,
   VE.Rights.Examples.fanMap, none, []⟩
def twiceListed : VE.Rights.RightsDoc :=
  { VE.Rights.Examples.beta VE.Rights.Examples.fanMap with
    rs := [⟨"r5", "person", .top, [fanDefault]⟩],
    sourceOrder := some [("r5", fanDefault), ("r5", fanDefault)] }
#guard chainWF .rights twiceListed
#guard !decide (((genKeys twiceListed).map (·.1)).Nodup)

end VE.Readings.Examples
