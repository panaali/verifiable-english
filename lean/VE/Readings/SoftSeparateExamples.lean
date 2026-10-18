import VE.Readings.SoftSeparate
import VE.Readings.UnspecifiedExamples

/-! RD-9 SC-2's fixtures (docs/spec/rd-9-soft-chain.md 8.1 and 8.2), each value computed here by `#guard` against
the value the spec records: separation on filled sides (`separatesS`), the filled side's admissibility and value, the
witness's `Fill_T` (`fillHoldsS`, isolated on `NSDq`), soft's premises regenerated on the filled tree
(`softPremisesIn_fill`), the constitution's miniature shapes C1′, C2′ and C9′, and F-SD2's K18, whose filled sides
are K1's. Every iff and "exactly when" claim of 8.2 that SC-2 owns has a fixture for each direction. -/
namespace VE.Readings.SoftSeparateExamples
open VE.Readings
open VE.Readings.Examples (K1 K2 K5 rs1 cand docK regsK m0 q0 exc sit)
open VE.Norms.Checks (envOf perm oblig)
open VE.Rights.Examples (noSoft strictNode defaultNode)
open VE.Rights (RightsDoc correlate)
open VE.SoftNorms (SoftNode)

/-- The predicate names a formula mentions. -/
def predsOf : VE.Formula → List String
  | .unary p _ => [p]
  | .binary p _ _ => [p]
  | .not a => predsOf a
  | .and a b | .or a b | .implies a b => predsOf a ++ predsOf b
  | .all _ a | .ex _ a => predsOf a
  | _ => []

/-! ## F-SD1: K1 with `avoid_required` unspecified -/

def NSD1 : NDoc := ⟨K1, ["avoid_required"]⟩
def mFill (fill : List (List String)) : VE.FiniteModel String :=
  { m0 with relations := fun p => if p == "unsaid__avoid_required" then fill else m0.relations p }
def σDef (fill : List (List String)) (v : Bool) : Situation String :=
  sit (mFill fill) [] [(exc "no-deception", [["a", "u"]])] q0 v
def σNone (fill : List (List String)) (v : Bool) : Situation String := sit (mFill fill) [] [] q0 v

#guard WellFormedSD NSD1 && softShaped NSD1.D
#guard (oneX NSD1 "rs1" 0).length == 0 && (oneX NSD1 "rs1" 1).length == 0
#guard decisionOnly NSD1.D "rs1" 0 1 == some (exc "no-deception")
#guard choices NSD1.D == [[("rs1", 0)], [("rs1", 1)]]
-- separation: the default witness separates only with the filling "no"; the strict witness never does
#guard separatesS NSD1 "rs1" 1 0 (σDef [] false)
#guard !separatesS NSD1 "rs1" 1 0 (σDef [["a", "u"]] false)
#guard !separatesS NSD1 "rs1" 0 1 (σNone [] true)
#guard !separatesS NSD1 "rs1" 0 1 (σNone [["a", "u"]] true)
-- the sides (`observeOn_sideOfS_sound`, both values): the filling decides the default side where it is excepted
#guard sideValidOn (sideOfS NSD1 (one K1 "rs1" 1)) (mFill []) [(exc "no-deception", [["a", "u"]])]
#guard sideValueOn (sideOfS NSD1 (one K1 "rs1" 1)) (mFill []) [(exc "no-deception", [["a", "u"]])] q0 == some false
#guard sideValueOn (sideOfS NSD1 (one K1 "rs1" 1)) (mFill [["a", "u"]]) [(exc "no-deception", [["a", "u"]])] q0 ==
  some true
#guard sideValueOn (sideOfS NSD1 (one K1 "rs1" 0)) (mFill []) [] q0 == some true
#guard fillHoldsS NSD1 "rs1" 1 (mFill []) [(exc "no-deception", [["a", "u"]])]
-- force twins: with the exception table empty no probe separates the pair, either value, either filling
#guard [[], [["a", "u"]]].all (fun fl => (probesOf K1 (mFill fl)).all (fun q => [true, false].all (fun v =>
  !separatesS NSD1 "rs1" 0 1 (sit (mFill fl) [] [] q v) && !separatesS NSD1 "rs1" 1 0 (sit (mFill fl) [] [] q v))))

/-! ## F-SD5: `fillDoc` on the soft chain is not well formed (D1) -/

#guard Wire.chainText .soft (one (fillDoc NSD1) "rs1" 1) ==
  some "SoftOverHard: rule no-deception over unsaid--avoid-required"
#guard !WellFormedDoc (fillDoc NSD1)

/-! ## F-SD3: K5 under the completion (a fixed default rule's table is shared) -/

def NSD3 : NDoc := ⟨K5, ["avoid_required", "help_required"]⟩

#guard WellFormedSD NSD3
#guard cellsOn K5 "rs1" 0 (sideOfS NSD3 (one K5 "rs1" 0)) m0 == 0
#guard cellsOn K5 "rs1" 1 (sideOfS NSD3 (one K5 "rs1" 1)) m0 == 1
#guard !owned K5 "rs1" 0 (exc "be-kind") && !owned K5 "rs1" 1 (exc "be-kind")
#guard separatesS NSD3 "rs1" 1 0 (sit m0 [(exc "be-kind", [["a", "u"]])] [(exc "no-deception", [["a", "u"]])] q0 false)

/-! ## F-SD4: `coherent` beside its strict twin (`softPremisesIn_fill`) -/

def regs4 : List VE.Norms.Regulated :=
  [oblig "x_required" ["assistant"] false (some "x_permitted") "{0} do x",
   perm "x_permitted" ["assistant"] false "{0} do x",
   perm "y_permitted" ["assistant"] false "{0} do y"]
def frame4 : RightsDoc where
  soft := ⟨envOf ["assistant"] ([("c", ["assistant"])] ++ regs4.map (fun r => (r.name, r.sorts))), [], noSoft,
    ⟨regs4, [], []⟩⟩
  rights := ⟨[], [], [], []⟩
  rs := []
  limits := []
  bars := []
  outsideCites := []
  sourceOrder := some []
def mustX : SoftNode := { defaultNode "must-x" "x_required" true (.unary "y_permitted" (.var 0)) with
  exception := some ⟨some "unstated", [.unary "c" (.var 0)], [], []⟩ }
def needNotX : SoftNode := defaultNode "need-not-x" "x_required" false
def D4 : Doc := docK [.fixed "u0" (.norm needNotX) [],
  .set ⟨"rs1", "u1", 1, [cand "strict" (strictNode "must-x" "x_required" true (.unary "y_permitted" (.var 0))),
    cand "default" mustX]⟩] .soft frame4
def NSD4 : NDoc := ⟨D4, ["y_permitted"]⟩

#guard WellFormedDoc D4 && WellFormedSD NSD4
#guard (softXL NSD4 (one D4 "rs1" 0).1).map (·.1) == []
#guard (softXL NSD4 (one D4 "rs1" 1).1).map (·.1) ==
  ["soft:exception:must-x:sufficient:0", "soft:coherence:must-x,need-not-x"]
-- the filled side's coherence premise reads the unsaid atom; soft's own does not
#guard (softXL NSD4 (one D4 "rs1" 1).1).map (fun x => (predsOf x.2).contains "unsaid__y_permitted") == [false, true]
#guard (VE.SoftNorms.cohPremises (correlate (one D4 "rs1" 1).1)).map
  (fun a => (predsOf a).contains "unsaid__y_permitted") == [false]

/-! ## `sideValidOn_sideOfS_iff`, both directions: K2's unsatisfiable necessary condition -/

def NSD2 : NDoc := ⟨K2, ["avoid_required"]⟩

#guard sideValidOn (sideOfS NSD2 (one K2 "rs1" 1)) m0 []
#guard !sideValidOn (sideOfS NSD2 (one K2 "rs1" 1)) m0 [(exc "no-deception", [["a", "u"]])]
#guard (oneX NSD2 "rs1" 1).length == 1

/-! ## `fillHoldsS`: F-ND1's frame (a pair with both members unspecified) on the soft chain -/

open VE.Readings.UnspecifiedExamples (frame1 mustHelp unspec1 base1) in
def NSDp : NDoc := ⟨⟨.soft, frame1, [.set ⟨"rs_1", "u1", 1,
  [cand "strict" mustHelp, cand "default" (defaultNode "must-help" "help_required" true)]⟩], [], []⟩, unspec1⟩

open VE.Readings.UnspecifiedExamples (base1) in
#guard WellFormedSD NSDp && (VE.NormDefaults.fillPremises (oneU NSDp "rs_1" 0)).length == 1 &&
  fillHoldsS NSDp "rs_1" 0 (base1 [["a", "u"]]) [] && !fillHoldsS NSDp "rs_1" 0 (base1 []) [] &&
  !separatesS NSDp "rs_1" 0 1 (⟨base1 [["a", "u"]], [], [], .outcome "help_required" ["a", "u"], true⟩ : Situation String) &&
  !separatesS NSDp "rs_1" 0 1 (⟨base1 [], [], [], .outcome "help_required" ["a", "u"], true⟩ : Situation String)

/-! ## `fillHoldsS` isolated (debate F2): the other reading regulates a different act, so `pairEval` holds on both
    bases and the witness's `Fill_T` alone decides `separatesS` -/

open VE.Readings.UnspecifiedExamples (regs1 frameOf mustHelp unspec1) in
def NSDq : NDoc := ⟨⟨.soft, frameOf (regs1 ++ [oblig "greet_required" ["agent", "user"] false none "{0} greet {1}"])
    [("asks", ["user", "agent"])], [.set ⟨"rs_1", "u1", 1,
  [cand "strict" mustHelp, cand "default" (defaultNode "must-greet" "greet_required" true)]⟩], [], []⟩, unspec1⟩
open VE.Readings.UnspecifiedExamples (base1) in
def σq (permitted : List (List String)) : Situation String :=
  ⟨base1 permitted, [], [], .outcome "help_required" ["a", "u"], true⟩
def pairEvalQ (σ : Situation String) : Bool :=
  (pairEval (m := Id) (pure ()) (pure ()) NSDq.D "rs_1" 0 1 (sideOfS NSDq (one NSDq.D "rs_1" 0))
    (sideOfS NSDq (one NSDq.D "rs_1" 1)) σ).1

open VE.Readings.UnspecifiedExamples (base1) in
#guard WellFormedSD NSDq && (VE.NormDefaults.fillPremises (oneU NSDq "rs_1" 0)).length == 1 &&
  pairEvalQ (σq [["a", "u"]]) && pairEvalQ (σq []) &&
  fillHoldsS NSDq "rs_1" 0 (base1 [["a", "u"]]) [] && !fillHoldsS NSDq "rs_1" 0 (base1 []) [] &&
  separatesS NSDq "rs_1" 0 1 (σq [["a", "u"]]) && !separatesS NSDq "rs_1" 0 1 (σq [])

/-! ## Constitution shapes (C1′, C2′, C9′) in a miniature frame

C9′'s first exception condition is named `harmful` here: the Lean audit refuses the spec's word for it in any
source, as a reserved Lean keyword. The values are the spec's, since they read the rule's name only. -/

def frameC (sorts : List String) (base : List (String × List String)) (regs : List VE.Norms.Regulated) : RightsDoc where
  soft := ⟨envOf sorts (base ++ regs.map (fun r => (r.name, r.sorts))), [], noSoft, ⟨regs, [], []⟩⟩
  rights := ⟨[], [], [], []⟩
  rs := []
  limits := []
  bars := []
  outsideCites := []
  sourceOrder := some []

def regsC1 : List VE.Norms.Regulated := [perm "denial_permitted" ["claude_instance"] false "{0} directly deny being Claude"]
def rsC1 : ReadingSet := ⟨"force-u0125-s04-p2", "u0125.s04.p2", 1,
  [cand "strict" (strictNode "no-denying-being-claude" "denial_permitted" false),
   cand "default" (defaultNode "no-denying-being-claude" "denial_permitted" false)]⟩
def NC1 : NDoc := ⟨docK [.set rsC1] .soft (frameC ["claude_instance"] [] regsC1), ["denial_permitted"]⟩
def mC1 (fill : List (List String)) : VE.FiniteModel String where
  domains s := match s with | "claude_instance" => ["c"] | _ => []
  constants _ := none
  relations p := if p == "unsaid__denial_permitted" then fill else []
def qC1 : Probe String := .outcome "denial_permitted" ["c"]

#guard WellFormedSD NC1 && (oneX NC1 rsC1.id 1).length == 0
#guard decisionOnly NC1.D rsC1.id 0 1 == some (exc "no-denying-being-claude")
#guard separatesS NC1 rsC1.id 1 0 (sit (mC1 [["c"]]) [] [(exc "no-denying-being-claude", [["c"]])] qC1 true)
#guard !separatesS NC1 rsC1.id 1 0 (sit (mC1 []) [] [(exc "no-denying-being-claude", [["c"]])] qC1 true)
#guard sideValueOn (sideOfS NC1 (one NC1.D rsC1.id 0)) (mC1 [["c"]]) [] qC1 == some false

def regsC2 : List VE.Norms.Regulated :=
  [oblig "clarification_required" ["claude_instance", "situation"] false none "{0} seek clarification in {1}"]
def rsC2 : ReadingSet := ⟨"force-u0036-s05", "u0036.s05", 1,
  [cand "strict" (strictNode "clarify-ambiguity" "clarification_required" true (.unary "genuine_ambiguity" (.var 0))),
   cand "default" (defaultNode "clarify-ambiguity" "clarification_required" true (.unary "genuine_ambiguity" (.var 0)))]⟩
def NC2 : NDoc := ⟨docK [.set rsC2] .soft
  (frameC ["claude_instance", "situation"] [("genuine_ambiguity", ["situation"])] regsC2), ["clarification_required"]⟩
def mC2 (amb : List (List String)) : VE.FiniteModel String where
  domains s := match s with | "claude_instance" => ["c"] | "situation" => ["s"] | _ => []
  constants _ := none
  relations p := if p == "genuine_ambiguity" then amb else []
def qC2 : Probe String := .outcome "clarification_required" ["c", "s"]

#guard WellFormedSD NC2 && (oneX NC2 rsC2.id 1).length == 0
#guard separatesS NC2 rsC2.id 1 0 (sit (mC2 [["s"]]) [] [(exc "clarify-ambiguity", [["c", "s"]])] qC2 false)
-- without the ambiguity neither reading's rule applies: not separated
#guard !separatesS NC2 rsC2.id 1 0 (sit (mC2 []) [] [(exc "clarify-ambiguity", [["c", "s"]])] qC2 false)
#guard sideValueOn (sideOfS NC2 (one NC2.D rsC2.id 0)) (mC2 [["s"]]) [] qC2 == some true

def regsC9 : List VE.Norms.Regulated :=
  [oblig "compliance_required" ["claude_instance", "instruction"] false none "{0} comply with {1}"]
def complyD : SoftNode := { defaultNode "comply" "compliance_required" true with
  exception := some ⟨some "unstated", [.unary "harmful" (.var 0), .unary "unethical" (.var 0),
    .unary "against_guidelines" (.var 0)], [], []⟩ }
def rsC9 : ReadingSet := ⟨"u0073-s05", "u0073.s05", 1,
  [cand "strict" (strictNode "comply" "compliance_required" true), cand "default" complyD]⟩
def NC9 : NDoc := ⟨docK [.set rsC9] .soft (frameC ["claude_instance", "instruction"]
  [("harmful", ["instruction"]), ("unethical", ["instruction"]), ("against_guidelines", ["instruction"])] regsC9),
  ["compliance_required"]⟩
def mC9 (bad : List (List String)) : VE.FiniteModel String where
  domains s := match s with | "claude_instance" => ["c"] | "instruction" => ["i"] | _ => []
  constants _ := none
  relations p := if p == "harmful" then bad else []
def qC9 : Probe String := .outcome "compliance_required" ["c", "i"]
def PC9 : Side := sideOfS NC9 (one NC9.D rsC9.id 1)

#guard WellFormedSD NC9
#guard (softXL NC9 (one NC9.D rsC9.id 1).1).map (·.1) ==
  ["soft:exception:comply:sufficient:0", "soft:exception:comply:sufficient:1", "soft:exception:comply:sufficient:2"]
#guard decisionOnly NC9.D rsC9.id 0 1 == none
-- a harmful instruction forces the exception: the empty decision table is inadmissible, the full one admissible
#guard !sideValidOn PC9 (mC9 [["i"]]) [] && sideValidOn PC9 (mC9 [["i"]]) [(exc "comply", [["c", "i"]])]
-- where it applies the default reading leaves the act unsaid (the filling answers), the strict reading settles it
#guard sideValueOn PC9 (mC9 [["i"]]) [(exc "comply", [["c", "i"]])] qC9 == some false
#guard sideValueOn (sideOfS NC9 (one NC9.D rsC9.id 0)) (mC9 [["i"]]) [] qC9 == some true
#guard separatesS NC9 rsC9.id 1 0 (sit (mC9 [["i"]]) [] [(exc "comply", [["c", "i"]])] qC9 false)
-- a harmless instruction: the empty table is admissible and the default reading's rule applies (no separation at false)
#guard sideValidOn PC9 (mC9 []) [] && !separatesS NC9 rsC9.id 1 0 (sit (mC9 []) [] [] qC9 false)

/-! ## F-SD2 (debate F5): K18 is K1 with the profile and nothing unspecified; its filled sides are K1's sides -/

def N18 : NDoc := ⟨K1, []⟩
def tabs18 : List (List (GenKey × List (List String))) := [[], [(exc "no-deception", [["a", "u"]])]]

#guard WellFormedSD N18 && (oneX N18 "rs1" 0).length == 0 && (oneX N18 "rs1" 1).length == 0
#guard (VE.NormDefaults.fillPremises (oneU N18 "rs1" 0)).length == 0 &&
  (VE.NormDefaults.fillPremises (oneU N18 "rs1" 1)).length == 0
-- every side check and every pair check S1 runs on K1 has the same value on the filled sides of `N18`
#guard [0, 1].all (fun i => tabs18.all (fun T =>
  sideValidOn (sideOfS N18 (one K1 "rs1" i)) m0 T == sideValidOn (sideOf K1 "rs1" i) m0 T &&
  (probesOf K1 m0).all (fun q => sideValueOn (sideOfS N18 (one K1 "rs1" i)) m0 T q == sideValueOn (sideOf K1 "rs1" i) m0 T q)))
#guard [(0, 1), (1, 0)].all (fun (i, j) => tabs18.all (fun T => (probesOf K1 m0).all (fun q => [true, false].all (fun v =>
  separatesS N18 "rs1" i j (sit m0 [] T q v) == separates K1 "rs1" i j (sit m0 [] T q v)))))
#guard separates K1 "rs1" 1 0 (sit m0 [] [(exc "no-deception", [["a", "u"]])] q0 false)

end VE.Readings.SoftSeparateExamples
