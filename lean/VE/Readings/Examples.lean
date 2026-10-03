import VE.Readings.Lines
import VE.Readings.Superpose
import VE.Readings.Wire
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

/-! ## `genKeys_nodup` and the line order (DRI ruling 1)

As first approved the statement was false. `WellFormedRights` accepts a document whose `sourceOrder` lists one
default fan-out line twice: the two copies are four instances `rights-fan-1` to `rights-fan-4` with distinct rule
names, and two pairs of them carry the same source key `excepted no-torture (bearer b)` (`twiceListed`). It also
accepts an order that lists a line its right does not have, and the rights checks never compare the order with the
rights' lines (`orderOnly`: the order lists no entry twice, and keys still repeat). `genKeys_nodup` now takes
`linesOnce` as its hypothesis; S1 admission refuses both documents with `lineOrderText`'s texts. -/

def fanDefault : VE.Rights.SourceLine :=
  ⟨.claim, some (defaultNode "no-torture" "torture_permitted_state" false), none, none,
   VE.Rights.Examples.fanMap, none, []⟩
def twiceListed : VE.Rights.RightsDoc :=
  { VE.Rights.Examples.beta VE.Rights.Examples.fanMap with
    rs := [⟨"r5", "person", .top, [fanDefault]⟩],
    sourceOrder := some [("r5", fanDefault), ("r5", fanDefault)] }
#guard chainWF .rights twiceListed
#guard !decide (((genKeys twiceListed).map (·.1)).Nodup)
#guard !linesOnce twiceListed
#guard lineOrderText twiceListed == some "InvalidInput: line order lists a line of right r5 twice"

/-- The same line with a citation added: another entry, which no right lists. -/
def fanCited : VE.Rights.SourceLine := { fanDefault with cites := [("note", [])] }
def orderOnly : VE.Rights.RightsDoc :=
  { twiceListed with sourceOrder := some [("r5", fanDefault), ("r5", fanCited)] }
#guard chainWF .rights orderOnly
#guard decide (VE.Rights.sourceLines orderOnly).Nodup
#guard !decide (((genKeys orderOnly).map (·.1)).Nodup)
#guard !linesOnce orderOnly
#guard lineOrderText orderOnly == some "UnknownRight: r5"

/-- Listed once, the same document has distinct keys, as `genKeys_nodup` proves. -/
def listedOnce : VE.Rights.RightsDoc := { twiceListed with sourceOrder := some [("r5", fanDefault)] }
#guard chainWF .rights listedOnce && linesOnce listedOnce
#guard decide (((genKeys listedOnce).map (·.1)).Nodup)
-- Every candidate document of K19 passes the check.
#guard linesOnce (one K19 "rs9" 0).1 && linesOnce (one K19 "rs9" 1).1

/-! # S2a: the superposed document (docs/spec/composition-s2.md 9.2)

The fixtures of 9.2 that are values of the definitions of 8.3 and 8.4, on environment K. `b` is the bit of `rs1`
(`ve__bit__1__0` on `ve__here`), `χ₀ = ¬b`, `χ₁ = b`; `ex₂` is `soft__excepted__rd_2_no_deception`. The certificates,
models and English of 9.2 are the Python search's and the wire's (`tests/test_readings_s2.py`); here the Boolean
values they are checked against. -/

open VE.Rights (correlate)
open VE.Norms (envAt)
open VE.SoftNorms (soften)

def bit (n j : Nat) : VE.Formula := .unary (bitName n j) here
def b1 : VE.Formula := bit 1 0
def ex₂ : String := "soft__excepted__rd_2_no_deception"
def quiet₂ : VE.Formula := .all "agent" (.all "user" (.implies (.binary ex₂ (.var 1) (.var 0)) b1))

/-! ## M1: K1's document -/

#guard supReady K1 && uniformPrecedence K1 && superposable K1
#guard (sup K1).1.soft.E.sorts == ["agent", "user", "ve__reading"]
#guard (sup K1).1.soft.E.constants "ve__here" == some "ve__reading"
#guard (sup K1).1.soft.E.predicates "ve__bit__1__0" == some ["ve__reading"]
#guard (sup K1).1.soft.T.nodes ==
  [{ S with name := "rd-1-no-deception", guard := .and .top (.not b1) },
   { Df with name := "rd-2-no-deception", guard := .and .top b1 }]
#guard genKeys (sup K1).1 == [(exc "rd-2-no-deception", ex₂, ["agent", "user"])]
#guard choiceLabelled K1 == [("readings:rs1@1:1:quiet", quiet₂)]
#guard onePremises K1 == [] && slotP K1 == [quiet₂]
#guard choices K1 == [[("rs1", 0)], [("rs1", 1)]]
#guard position K1 0 0 == 1 && position K1 0 1 == 2
#guard origin K1 "rd-2-no-deception" == some (0, 1) && origin K1 "rd-1-no-deception" == some (0, 0) &&
  origin K1 "no-deception" == none
#guard qName K1 [("rs1", 1)] "no-deception" == "rd-2-no-deception" &&
  qName K1 [("rs1", 0)] "no-deception" == "rd-1-no-deception"
#guard nameMap K1 [("rs1", 1)] "soft__excepted__no_deception" == ex₂ &&
  nameMap K1 [("rs1", 1)] "avoid_required" == "avoid_required" && nameMap K1 [("rs1", 1)] "asks" == "asks"
#guard nameMap K1 [("rs1", 0)] "soft__excepted__no_deception" == "soft__excepted__no_deception"

/-! ## M2: three bases of `sup D` (the slot holds on `B₁` and `B₀`; `B₂` breaks the quiescence premise) -/

def baseM (bitOn excepted : Bool) : VE.FiniteModel String where
  domains s := match s with | "agent" => ["a"] | "user" => ["u"] | "ve__reading" => ["e"] | _ => []
  constants x := if x == "ve__here" then some "e" else none
  relations p := if p == "ve__bit__1__0" then (if bitOn then [["e"]] else [])
    else if p == ex₂ then (if excepted then [["a", "u"]] else []) else []
#guard VE.Compose.backgroundValidP (correlate (sup K1).1) (slotP K1) (baseM true true)
#guard VE.Compose.backgroundValidP (correlate (sup K1).1) (slotP K1) (baseM false false)
#guard !VE.Compose.backgroundValidP (correlate (sup K1).1) (slotP K1) (baseM false true)
-- B₁ spells candidate 1, B₀ candidate 0
#guard (choiceAtom K1 "rs1" 1).eval (baseM true true) [] && !(choiceAtom K1 "rs1" 0).eval (baseM true true) []
#guard (choiceAtom K1 "rs1" 0).eval (baseM false false) [] && !(choiceAtom K1 "rs1" 1).eval (baseM false false) []

/-! ## M5, M6: a narrowing; a coupling and a dead reading -/

def helpX : SoftNode := strictNode "help-x" "help_required" true
def n1 : Narrowing := ⟨"n1", "rs1", 1, ["strict"]⟩
def M5 : Doc := ⟨.soft, frameK, [.set rs1, .fixed "u0" (.norm helpX) [], .fixed "u2" (.assertion .top) []], [], [n1]⟩
#guard superposable M5
#guard choiceLabelled M5 == [("readings:rs1@1:1:quiet", quiet₂), ("narrowing:n1", .not b1)]
#guard choices M5 == [[("rs1", 0)]]

def labelled (c : Candidate) (v : String) : Candidate := { c with labels := [("force", v)] }
def rs1f : ReadingSet := ⟨"rs1", "u1", 1, [labelled (cand "strict" S) "strict", labelled (cand "default" Df) "default"]⟩
def rs2f (v : Nat := 1) : ReadingSet := ⟨"rs2", "u2", v,
  [labelled (cand "strict" (strictNode "be-kind" "help_required" true)) "strict", labelled (cand "default" beKind) "default"]⟩
def c1 (v : Nat := 1) : Coupling := ⟨"c1", "force", [("rs1", 1), ("rs2", v)]⟩
def M6 (ns : List Narrowing := []) : Doc := ⟨.soft, frameK, [.set rs1f, .set (rs2f)], [c1], ns⟩
def b2 : VE.Formula := bit 2 0
#guard superposable (M6)
#guard couplingPremises (M6) == [("coupling:c1", .and (.not (.and (.not b1) b2)) (.not (.and b1 (.not b2))))]
#guard choices (M6) == [[("rs1", 0), ("rs2", 0)], [("rs1", 1), ("rs2", 1)]]
#guard (quietOwn (M6)).map (·.1) == ["readings:rs1@1:1:quiet", "readings:rs2@1:1:quiet"]
#guard (genKeys (sup (M6)).1).map (·.2.1) == [ex₂, "soft__excepted__rd_4_be_kind"]
#guard choices (M6 [n1]) == [[("rs1", 0), ("rs2", 0)]]
-- with `n1` no compatible choice takes candidate 1 of `rs2` (DeadReading: rs2:1), and none is dropped by a premise
-- on it: its atom is refuted from the coupling and the narrowing together
#guard choiceCore (M6 [n1]) == [.and (.not (.and (.not b1) b2)) (.not (.and b1 (.not b2))), .not b1]

/-! ## M7: three candidates, two bits -/

def M7 : Doc := docK [.set ⟨"rs1", "u1", 1, [cand "strict" S, cand "default" Df, ⟨"assert", some (.assertion asksAll), [], []⟩]⟩]
def b0' : VE.Formula := bit 1 0
def b1' : VE.Formula := bit 1 1
#guard bitsOf 3 == 2 && bitsOf 1 == 0 && bitsOf 2 == 1 && bitsOf 4 == 2 && bitsOf 5 == 3
#guard choiceAtom M7 "rs1" 0 == .and (.not b0') (.not b1') && choiceAtom M7 "rs1" 1 == .and b0' (.not b1') &&
  choiceAtom M7 "rs1" 2 == .and (.not b0') b1'
#guard onePremises M7 == [("readings:rs1@1:one", .not (.and b0' b1'))]
#guard (sup M7).2 == [.implies (.and (.not b0') b1') asksAll]
#guard (choiceLabelled M7).map (·.1) == ["readings:rs1@1:one", "readings:rs1@1:1:quiet"]
#guard (choices M7).length == 3 && superposable M7

/-! ## M8: the precedence leak -/

def waiveX (over : List String) : SoftNode :=
  strictNode "waive-x" "avoid_required" false (.binary "asks" (.var 1) (.var 0)) [] over
def M8 : Doc := docK [.fixed "u0" (.norm (strictNode "base-x" "avoid_required" true)) [],
  .set ⟨"rs1", "u1", 1, [cand "a" (waiveX []), cand "b" (waiveX ["base-x"])]⟩,
  .fixed "u3" (.norm (strictNode "stop-x" "avoid_required" false .top [] ["waive-x"])) []]
#guard WellFormedDoc M8
#guard !uniformPrecedence M8 && !superposable M8
#guard (choices M8).length == 2 && (choices M8).all (fun c => sideWF M8 (choiceDoc M8 c))
-- the mutation: without the condition the copies of `waive-x` carry different parents
#guard supReady M8 && sideWF M8 (sup M8)
#guard ((sup M8).1.soft.T.nodes.find? (·.name == "stop-x")).map (·.over) == some ["rd-1-waive-x", "rd-2-waive-x"]

/-! ## M9: a dependency cycle across candidates -/

def frame9 : VE.Rights.RightsDoc :=
  { frameK with soft := { frameK.soft with
      E := envOf ["agent", "user"] ([("asks", ["agent", "user"])] ++
        (regsK ++ [oblig "warn_required" ["agent", "user"] false none "{0} warn {1}"]).map (fun r => (r.name, r.sorts))),
      T := { frameK.soft.T with regulated := regsK ++ [oblig "warn_required" ["agent", "user"] false none "{0} warn {1}"] } } }
def on2 (p : String) : VE.Formula := .binary p (.var 1) (.var 0)
def M9 : Doc := ⟨.soft, frame9,
  [.fixed "u0" (.norm (strictNode "f-warn" "warn_required" true (on2 "asks"))) [],
   .set ⟨"rs1", "u1", 1, [cand "a" (strictNode "r-a" "avoid_required" true (on2 "help_required")),
     cand "b" (strictNode "r-b" "help_required" true (on2 "warn_required"))]⟩,
   .set ⟨"rs2", "u2", 1, [cand "c" (strictNode "r-c" "warn_required" true (on2 "avoid_required")),
     cand "d" (strictNode "r-d" "warn_required" true)]⟩], [], []⟩
#guard WellFormedDoc M9
#guard supReady M9 && uniformPrecedence M9 && !sideWF M9 (sup M9) && !superposable M9
#guard (choices M9).length == 4 && (choices M9).all (fun c => sideWF M9 (choiceDoc M9 c))

/-! ## M10, M10b: owners of an outweighs predicate -/

def M10 : Doc := docK [.set ⟨"rs1", "u1", 1, [cand "strict" S, cand "default" { Df with rank := some "lo" }]⟩,
  .fixed "u0" (.norm { Df with name := "never-avoid-d", sign := false, rank := some "hi" }) []] .soft (frameWith holistic)
def ow : String := "soft__outweighs__lo__hi__avoid_required"
#guard superposable M10
#guard (genKeys (sup M10).1).map (·.1) ==
  [exc "rd-2-no-deception", exc "never-avoid-d", .outweighs "avoid_required" "lo" "hi"]
#guard owners M10 (.outweighs "avoid_required" "lo" "hi") == [[(0, 1)]] && owners M10 (exc "never-avoid-d") == [[]]
#guard quietOwn M10 == [("readings:rs1@1:1:quiet",
  .and quiet₂ (.all "agent" (.all "user" (.implies (.binary ow (.var 1) (.var 0)) b1))))]
#guard quietShared M10 == []
#guard !((genKeys (choiceDoc M10 [("rs1", 0)]).1).any (·.2.1 == ow))

def M10b : Doc := docK [.set ⟨"rs1", "u1", 1, [cand "strict" S, cand "default" { Df with rank := some "lo" }]⟩,
  .set ⟨"rs2", "u2", 1, [cand "strict" (strictNode "be-firm" "avoid_required" false),
    cand "default" { defaultNode "be-firm" "avoid_required" false with rank := some "hi" }]⟩] .soft (frameWith holistic)
#guard superposable M10b
#guard owners M10b (.outweighs "avoid_required" "lo" "hi") == [[(0, 1), (1, 1)]]
#guard quietShared M10b == [("readings:quiet:outweighs:avoid_required:lo:hi",
  .all "agent" (.all "user" (.implies (.binary ow (.var 1) (.var 0)) (.and b1 b2))))]

/-! ## M12, M14, M16 -/

#guard (choices K19).length == 2 && (choices K19).all (fun c => sideWF K19 (choiceDoc K19 c))
#guard copies K9 "no-deception" == ["rd-1-no-deception", "rd-2-no-deception"]
#guard ((sup K9).1.soft.T.nodes.find? (·.name == "except-x")).map (·.over) ==
  some ["rd-1-no-deception", "rd-2-no-deception"]
#guard uniformPrecedence K9 && superposable K9
def name45 : String := "n" ++ String.mk (List.replicate 44 'x')
def M16 : Doc := docK [.set ⟨"rs1", "u1", 1, [cand "strict" { S with name := name45 }, cand "default" { Df with name := name45 }]⟩]
#guard name45.length == 45 && WellFormedDoc M16
-- The chain's check enforces `MAX_IDENTIFIER_BYTES` on generated decision predicates (`namesFit`, DRI ruling 2):
-- the candidate's own predicate has 61 bytes and passes, `sup D`'s has 66 and fails with the chain's own text.
#guard (genKeys (sup M16).1).map (·.2.1.utf8ByteSize) == [66] && (genKeys (one M16 "rs1" 1).1).map (·.2.1.utf8ByteSize) == [61]
#guard supReady M16 && uniformPrecedence M16 && !sideWF M16 (sup M16) && !superposable M16
#guard Wire.chainText .soft (sup M16) == some ("ResourceLimit: decision predicate soft__excepted__rd_2_" ++ name45)
#guard (choices M16).length == 2 && (choices M16).all (fun c => sideWF M16 (choiceDoc M16 c))

/-! ## M17: the shape of couplings and narrowings -/

def unlabelled : Doc := ⟨.soft, frameK, [.set rs1, .set rs2kind], [c1], []⟩
#guard !supReady unlabelled
#guard couplingPremises unlabelled == []
#guard [[("rs1", 0), ("rs2", 0)], [("rs1", 0), ("rs2", 1)], [("rs1", 1), ("rs2", 0)], [("rs1", 1), ("rs2", 1)]].all
  (fun c => complete unlabelled c && !couplingHolds unlabelled c (c1))
#guard !supReady ⟨.soft, frameK, [.set rs1f, .set (rs2f)], [c1, c1], []⟩
#guard !supReady ⟨.soft, frameK, [.set rs1f, .set (rs2f)], [c1 2], []⟩
def M17d : Doc := ⟨.soft, frameK, [.set rs1f, .set (rs2f 2)], [c1 2], [⟨"n0", "rs2", 1, ["strict"]⟩]⟩
#guard (inForce M17d ⟨"n0", "rs2", 1, ["strict"]⟩).isNone && narrowingShape M17d ⟨"n0", "rs2", 1, ["strict"]⟩
#guard supReady M17d && narrowingPremises M17d == [] && choices M17d == choices (M6)

/-! ## M18: a coupled formula-only document whose recorded narrowings together keep no choice -/

def notAsks : VE.Formula := .all "agent" (.all "user" (.not (.binary "asks" (.var 1) (.var 0))))
def formulaSet (id u : String) : ReadingSet := ⟨id, u, 1,
  [{ (⟨"A", some (.assertion asksAll), [], []⟩ : Candidate) with labels := [("force", "A")] },
   { (⟨"B", some (.assertion notAsks), [], []⟩ : Candidate) with labels := [("force", "B")] }]⟩
def M18 : Doc := ⟨.soft, frameK, [.set (formulaSet "rs1" "u1"), .set (formulaSet "rs2" "u2")],
  [c1], [⟨"n1", "rs1", 1, ["A"]⟩, ⟨"n2", "rs2", 1, ["B"]⟩]⟩
#guard supReady M18 && choices M18 == []
#guard (onePremises M18 ++ couplingPremises M18 ++ narrowingPremises M18).map (·.1) ==
  ["coupling:c1", "narrowing:n1", "narrowing:n2"]

/-! ## M19: the frame declares the choice vocabulary (rejection fixtures, DRI ruling 1)

`VE.Environment` lists its constants and predicates as functions, so `WellFormedDoc` cannot see a frame that
declares the constant `ve__here` or a bit predicate (S1 leaves those names to the wire decoder, 1.8), and
`choiceEnv` overrides the frame's declaration in `sup D` while `choiceDoc D c` keeps it. `supReady` therefore carries
`choiceFresh`, and both documents below are refused by it, so no theorem of 8.4 applies to them. What the conjunct
excludes is visible: `KH` is a formula-only set in a frame that declares `ve__here : agent`; `MH` is a slot-admissible
base of `sup KH` encoding the choice `[(rs1, 0)]` whose `ve__here` is no agent, so its pull is not admissible for the
choice's document (`kh_base_down_fails`): `base_down` would be false without the conjunct. A frame predicate named
`ve__bit__1__0` breaks `base_up` and `superpose_conflict_free` in the same way. -/

def frameH : VE.Rights.RightsDoc :=
  { frameK with soft := { frameK.soft with E := { frameK.soft.E with
      constants := fun x => if x == "ve__here" then some "agent" else none } } }
def rsF : ReadingSet := ⟨"rs1", "u1", 1, [⟨"a", some (.assertion .top), [], []⟩, ⟨"b", some (.assertion .bottom), [], []⟩]⟩
def KH : Doc := docK [.set rsF] .soft frameH
#guard WellFormedDoc KH && !choiceFresh KH && !supReady KH && !superposable KH && compatible KH [("rs1", 0)]
-- without the conjunct the rest of `superposable` holds
#guard uniformPrecedence KH && sideWF KH (sup KH)
def MH : VE.FiniteModel String where
  domains s := match s with | "agent" => ["a"] | "user" => ["u"] | "ve__reading" => ["e"] | _ => []
  constants x := if x == "ve__here" then some "e" else none
  relations _ := []

theorem kh_sup_const (x : String) : (envAt (soften (correlate (sup KH).1)) 0).constants x =
    if x == "ve__here" then some "ve__reading" else frameH.soft.E.constants x := rfl
theorem kh_choice_const (x : String) :
    (envAt (soften (correlate (choiceDoc KH [("rs1", 0)]).1)) 0).constants x = frameH.soft.E.constants x := rfl

theorem kh_valid : MH.Valid (envAt (soften (correlate (sup KH).1)) 0) := by
  refine ⟨fun x s hx => ?_, fun p vs h => ?_⟩
  · rw [kh_sup_const] at hx
    by_cases h : x = "ve__here"
    · subst h
      simp at hx; subst hx
      exact ⟨"e", rfl, by simp [VE.FiniteModel.asStructure, MH]⟩
    · have : (x == "ve__here") = false := by simpa using h
      simp only [this, frameH, frameK, Bool.false_eq_true, if_false] at hx
      cases hx
  · exact absurd h (by simp [VE.FiniteModel.asStructure, MH])

theorem kh_slot : VE.Compose.BaseAdmissibleP (correlate (sup KH).1) (slotP KH) MH.asStructure := by
  have h0 : VE.Norms.backgroundBase (soften (correlate (sup KH).1)) = [] := by
    show VE.Route.Background.literals [] = []
    simp [VE.Route.Background.literals, VE.Route.sortStrings, VE.Route.Background.pairs]
  have h1 : VE.SoftNorms.softPremises (correlate (sup KH).1) = [] := by decide
  have h2 : slotP KH = [] := by decide
  refine ⟨⟨⟨kh_valid, ?_⟩, ?_⟩, ?_⟩
  · rw [h0]; exact VE.Compose.sat_nil _
  · rw [h1]; exact VE.Compose.sat_nil _
  · rw [h2]; exact VE.Compose.sat_nil _

theorem kh_encodes : Encodes KH [("rs1", 0)] MH.asStructure := by
  intro R hR i hi
  have hR' : R = rsF := by simpa [KH, docK, Doc.sets] using hR
  subst hR'
  have hi' : i = 0 ∨ i = 1 := by simp [rsF] at hi; omega
  rcases hi' with rfl | rfl
  · rw [← VE.eval_iff_denote]; decide
  · rw [← VE.eval_iff_denote]; decide

theorem kh_base_down_fails :
    ¬ VE.Rights.BaseAdmissibleR (choiceDoc KH [("rs1", 0)]).1 (pull KH [("rs1", 0)] MH.asStructure) := by
  intro h
  obtain ⟨v, hv, hd⟩ := h.1.1.1.1 "ve__here" "agent" (by rw [kh_choice_const]; rfl)
  simp [pull, VE.FiniteModel.asStructure, MH] at hv hd
  subst hv
  exact absurd hd (by decide)

/-! The same gap would break `superpose_assertions`: in a frame that declares `ve__bit__1__0` over agents and
`ve__here` as an agent, the assertion candidates `ve__bit__1__0(ve__here)` and its negation are admitted, but `sup KB`
gates them with the very bit they mention, so no reinterpretation of the choice vocabulary satisfies both gated
assertions while every structure satisfies one candidate (`kb_superpose_assertions_fails`). `supReady KB` is false,
so `superpose_assertions` (whose `hr` is `supReady`) does not apply to it. -/

def frameB : VE.Rights.RightsDoc :=
  { frameK with soft := { frameK.soft with E := { frameK.soft.E with
      predicates := fun p => if p == "ve__bit__1__0" then some ["agent"] else frameK.soft.E.predicates p,
      constants := fun x => if x == "ve__here" then some "agent" else none } } }
def bH : VE.Formula := .unary "ve__bit__1__0" (.const "ve__here")
def rsB : ReadingSet := ⟨"rs1", "u1", 1, [⟨"a", some (.assertion bH), [], []⟩, ⟨"b", some (.assertion (.not bH)), [], []⟩]⟩
def KB : Doc := docK [.set rsB] .soft frameB
#guard WellFormedDoc KB && !choiceFresh KB && !supReady KB && !superposable KB

theorem kb_sup_assertions : (sup KB).2 = [.implies (.not bH) bH, .implies bH (.not bH)] := by decide
theorem kb_choice : choicePremises KB = [] := by decide

def SB : VE.Structure.{0} where
  Carrier := Unit
  domain _ _ := True
  constant _ := some ()
  relation _ _ := False

theorem kb_superpose_assertions_fails :
    ¬ ((∃ S', ChoiceExtension KB SB S' ∧ VE.Norms.Sat S' ((sup KB).2 ++ choicePremises KB)) ↔
      (VE.Norms.Sat SB (free KB).2 ∧ ∀ R ∈ KB.sets, ∃ a ∈ R.candidates, ∃ φ, a.content = some (.assertion φ) ∧
        φ.denote SB [])) := by
  intro h
  have hrhs : VE.Norms.Sat SB (free KB).2 ∧ ∀ R ∈ KB.sets, ∃ a ∈ R.candidates, ∃ φ,
      a.content = some (.assertion φ) ∧ φ.denote SB [] := by
    refine ⟨?_, fun R hR => ?_⟩
    · have : (free KB).2 = [] := by decide
      rw [this]; exact VE.Compose.sat_nil _
    · have : R = rsB := by simpa [KB, docK, Doc.sets] using hR
      subst this
      refine ⟨⟨"b", some (.assertion (.not bH)), [], []⟩, by simp [rsB], .not bH, rfl, ?_⟩
      simp [bH, VE.Formula.denote, SB]
  obtain ⟨S', _, hs⟩ := h.mpr hrhs
  rw [kb_sup_assertions, kb_choice] at hs
  have h1 : (VE.Formula.implies (.not bH) bH).denote S' [] := hs _ (by simp)
  have h2 : (VE.Formula.implies bH (.not bH)).denote S' [] := hs _ (by simp)
  by_cases hb : bH.denote S' []
  · exact (h2 hb) hb
  · exact hb (h1 hb)

/-! ## M20: `asserted_shared` needs distinct set ids (reported against 8.4)

Two open sets under one id: `choiceDoc D c` and `one D s i` read a set by its id, so both pick index `i` in both
sets, and S1's check of candidate 0 of the first set types its assertion beside the second set's default rule. The
assertion mentions that rule's decision predicate, which `sharedEnv D` does not declare: the statement of 8.4 without
`supReady` is false here, and `asserted_shared` is proved with it (`Asserted.lean`). -/

def phiEx : VE.Formula := .all "agent" (.all "user" (.binary "soft__excepted__no_deception" (.var 1) (.var 0)))
def M20 : Doc := docK [.set ⟨"s", "u1", 1, [⟨"a", some (.assertion phiEx), [], []⟩, ⟨"b", some (.assertion .top), [], []⟩]⟩,
  .set ⟨"s", "u2", 1, [cand "default" Df, cand "strict" S]⟩]
#guard WellFormedDoc M20 && compatible M20 [("s", 0), ("s", 0)] && !supReady M20
#guard (choiceDoc M20 [("s", 0), ("s", 0)]).2 == [phiEx] && !phiEx.check (sharedEnv M20) []

theorem m20_choice : (choiceDoc M20 [("s", 0), ("s", 0)]).2 = [phiEx] := by decide
theorem m20_unchecked : phiEx.check (sharedEnv M20) [] = false := by decide

theorem m20_asserted_shared_fails : ¬ ∀ a ∈ (choiceDoc M20 [("s", 0), ("s", 0)]).2, a.WellFormed (sharedEnv M20) [] := by
  intro h
  have := (VE.check_iff_wellFormed _ _ _).mpr (h phiEx (by rw [m20_choice]; simp))
  rw [m20_unchecked] at this
  cases this

end VE.Readings.Examples
