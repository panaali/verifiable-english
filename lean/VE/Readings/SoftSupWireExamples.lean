import VE.Readings.SoftSupWire
import VE.Readings.SoftSupExamples

/-! SC-11's fixtures (docs/spec/rd-9-soft-chain.md 14.9), each value computed here by `#guard`: the label mapping on
W-2 to W-4 (`labelImage`, `sdShown`, `fillLabels_choice`), the route of W-6 and W-6′ (`routeSD`, one row per conjunct
of `routeSD_superposed_iff`) and W-13's route values (14.11). The route reads its environment only through
`sdChoiceText`'s author checks (`lowerJson`), so a small soft-chain environment is decoded here; W-6′'s per-choice
row decodes one with 253 declared predicates, so each reading fits the vocabulary limit of 256 and a choice taking
two default readings does not. This is the only module that evaluates the route (sc-11b switches the dispatch). -/
namespace VE.Readings.SoftSupWireExamples
open Lean VE.Readings VE.Readings.Wire
open VE.Readings.SoftSeparateExamples (NSD1 NSD2 NSD4 NSDq NC9 frame4 mustX needNotX D4)
open VE.Readings.SoftSupExamples (NSD4a NSD4c pullFM satAll m4 m1)
open VE.Readings.Examples (docK cand binarySet M8)
open VE.Rights.Examples (strictNode defaultNode)

def supLabels (N : NDoc) : List String := (softXL N (sup N.D).1).map (·.1)

/-! ## W-2, W-2′: the label image, both roles -/

#guard (choices NSD4.D).map (labelImage NSD4) == [[], [
  ("soft:exception:must-x:sufficient:0", "soft:exception:rd-2-must-x:sufficient:0"),
  ("soft:coherence:must-x,need-not-x", "soft:coherence:need-not-x,rd-2-must-x")]]
-- `labelImage_fst` and `labelImage_snd_mem` on each fixture
#guard [NSD1, NSD2, NSD4, NSD4a, NC9, NSDq].all fun N => (choices N.D).all fun c =>
  (labelImage N c).map (·.1) == (softXL N (choiceDoc N.D c).1).map (·.1) &&
    (labelImage N c).all (fun p => (supLabels N).contains p.2)
#guard (choices NC9.D).map (labelImage NC9) == [[], (List.range 3).map fun i =>
  (s!"soft:exception:comply:sufficient:{i}", s!"soft:exception:rd-2-comply:sufficient:{i}")]
#guard (choices NSD2.D).map (labelImage NSD2) ==
  [[], [("soft:exception:no-deception:necessary:0", "soft:exception:rd-2-no-deception:necessary:0")]]

/-! ## W-3: a premise dead in every choice -/

/-- One set of two defaults on one act with opposite signs, no fixed unit. -/
def NSDd : NDoc := ⟨docK [.set ⟨"rs1", "u1", 1, [cand "must" (defaultNode "must-x" "x_required" true),
  cand "need-not" (defaultNode "need-not-x" "x_required" false)]⟩] .soft frame4, ["y_permitted"]⟩

#guard WellFormedSD NSDd && superposable NSDd.D
#guard supLabels NSDd == ["soft:coherence:rd-1-must-x,rd-2-need-not-x"]
#guard (choices NSDd.D).map (labelImage NSDd) == [[], []]
-- nothing is shown for it, and no other name in its place
#guard sdShown NSDd [] (supLabels NSDd) == []
-- it holds at each encoded base, the slot holding (`supLabel_other`): the bit off encodes `(rs1,0)`, on `(rs1,1)`
#guard [false, true].map (fun b => (satAll (m4 b [] []) (slotP NSDd.D), satAll (m4 b [] []) (supX NSDd),
  (choices NSDd.D).map fun c => satAll (m4 b [] []) (atoms NSDd.D c))) ==
  [(true, true, [true, false]), (true, true, [false, true])]

/-! ## W-4: two superposed labels, one choice label -/

/-- One set of two defaults `x` under different guards, a fixed default `need-not-x`. -/
def NSDm : NDoc := ⟨docK [.fixed "u0" (.norm needNotX) [], .set ⟨"rs1", "u1", 1,
  [cand "c" (defaultNode "x" "x_required" true (.unary "c" (.var 0))),
   cand "y" (defaultNode "x" "x_required" true (.unary "y_permitted" (.var 0)))]⟩] .soft frame4, ["y_permitted"]⟩

#guard WellFormedSD NSDm && superposable NSDm.D
#guard supLabels NSDm == ["soft:coherence:need-not-x,rd-1-x", "soft:coherence:need-not-x,rd-2-x"]
-- each superposed label read back through every choice that has it: one label each, twice
#guard (supLabels NSDm).map (fun s => (choices NSDm.D).filterMap fun c => ((labelImage NSDm c).find? (·.2 == s)).map (·.1)) ==
  [["soft:coherence:need-not-x,x"], ["soft:coherence:need-not-x,x"]]
#guard sdShown NSDm [] (supLabels NSDm) == ["soft:coherence:need-not-x,x"]
-- under a named reading, only the choices taking it (`sdShown_mem`, `sdShown_image`)
#guard sdShown NSDm [("rs1", 0)] ["soft:coherence:need-not-x,rd-2-x"] == [] &&
  sdShown NSDm [("rs1", 1)] ["soft:coherence:need-not-x,rd-2-x"] == ["soft:coherence:need-not-x,x"]
-- `fillLabels_choice`: one `Fill_T` label, the same in each choice
#guard VE.NormDefaults.Admission.fillLabels (supU NSDq) != [] && (choices NSDq.D).all fun c =>
  VE.NormDefaults.Admission.fillLabels (choiceU NSDq c) == VE.NormDefaults.Admission.fillLabels (supU NSDq)

/-! ## W-5, W-5′: one premise at an encoded filled base -/

/-- Each pair of `labelImage N c`: its superposed premise at `M`, its choice premise at the filled pull. -/
def pairVals (N : NDoc) (c : Choice) (M : VE.FiniteModel String) : List (String × Bool × Bool) :=
  (labelImage N c).filterMap fun p => do
    let a ← ((softXL N (choiceDoc N.D c).1).find? (·.1 == p.1)).map (·.2)
    let a' ← ((softXL N (sup N.D).1).find? (·.1 == p.2)).map (·.2)
    pure (p.1, a'.eval M [], a.eval (pullFM N c M) [])

-- `supLabel_pull`, NSD4 at `(rs1,1)` with `c = {a}`: the sufficient premise false on both sides with the
-- exception's table empty, true on both with it `{a}`
#guard satAll (m4 true [["a"]] []) (slotP NSD4.D) && pairVals NSD4 [("rs1", 1)] (m4 true [["a"]] []) ==
  [("soft:exception:must-x:sufficient:0", false, false), ("soft:coherence:must-x,need-not-x", true, true)]
#guard pairVals NSD4 [("rs1", 1)] (m4 true [["a"]] [["a"]]) ==
  [("soft:exception:must-x:sufficient:0", true, true), ("soft:coherence:must-x,need-not-x", true, true)]
-- `supLabel_other` needs `hsl`: NSD2 with the bits naming `(rs1,0)` (no image there) and the necessary condition's
-- table `{(a,u)}`, the slot is broken and the premise false; with the table empty both hold
#guard labelImage NSD2 [("rs1", 0)] == [] &&
  [m1 false [["a", "u"]] [], m1 false [] []].map (fun M => (satAll M (slotP NSD2.D), satAll M (supX NSD2))) ==
  [(false, false), (true, true)]

/-! ## W-6, W-6′: the route, one row per conjunct -/

def envWith (n : Nat) : Json := Json.mkObj [("language", "ve.core@0.2"),
  ("spec_revision", "ve-v0.2-expand2-2026-09-25"),
  ("profiles", toJson ["norm-defaults@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]),
  ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("agent", Json.mkObj [("description", "agent")])]),
    ("predicates", Json.mkObj ((List.range n).map fun i => (s!"p{i}", Json.mkObj [("arguments", toJson ["agent"]),
      ("description", "{0} p")]))), ("constants", Json.mkObj [])])]

/-- `routeSD`, with its conjuncts: `routeOf true`, `sdSuperposable`, the choices checked, `sdCheckWork`. -/
def routeFacts (N : NDoc) (declared : Nat := 0) : String :=
  match decodeEnvironment (envWith declared) with
  | .ok re => s!"{(routeOf true N.D).text} {sdSuperposable N} {(checkedChoices N.D).length} {sdCheckWork N} " ++
      (routeSD re N).text
  | .error e => e

#guard [NSD1, NSD4, NSD4a, NSD4c, NC9, NSD2, NSDq].all fun N => (routeFacts N).endsWith " superposed"
-- `superposable` false: precedence not uniform under a rule
#guard !superposable M8 && routeFacts ⟨M8, []⟩ == "enumerated false 2 30 enumerated" &&
  (match decodeEnvironment (envWith 0) with | .ok re => sdChecked re ⟨M8, []⟩ | .error _ => false)
-- `WellFormedU (supU N)` false with `superposable` true; every choice's text fails too (REPORT: not isolated)
#guard superposable D4 && !VE.NormDefaults.WellFormedU (supU ⟨D4, ["bogus"]⟩) &&
  routeFacts ⟨D4, ["bogus"]⟩ == "enumerated false 2 28 enumerated"

/-- Two sets of a strict and a default reading of `must-x`, five sets of two assertions: 128 choices. -/
def softSet (k : Nat) (g : VE.Formula := .top) : Item :=
  .set ⟨s!"rs{k}", s!"u{k + 1}", 1, [cand "strict" (strictNode s!"must-x-{k}" "x_required" true g),
    cand "default" { mustX with name := s!"must-x-{k}" }]⟩
def NSDlate : NDoc := ⟨docK ([.fixed "u0" (.norm needNotX) [], softSet 0, softSet 1] ++
  (List.range 5).map (fun k => binarySet (k + 2))) .soft frame4, ["y_permitted"]⟩

-- a choice past 64 whose `sdChoiceText` is some: 253 declared names, so a reading's two decision predicates fit and
-- the three of a choice taking both default readings do not; the first such choice is the 97th
#guard (decisionCount (one NSDlate.D "rs0" 1).1, decisionCount (choiceDoc NSDlate.D
  [("rs0", 1), ("rs1", 1), ("s2", 0), ("s3", 0), ("s4", 0), ("s5", 0), ("s6", 0)]).1) == (2, 3)
#guard match decodeEnvironment (envWith 253) with
  | .ok re => ((checkedChoices NSDlate.D).zipIdx.find? (fun (p : Choice × Nat) =>
      (sdChoiceText re NSDlate p.1).isSome)).map (·.2) == some 96
  | .error _ => false
#guard routeFacts NSDlate 253 == "enumerated true 128 3200 enumerated" &&
  routeFacts NSDlate == "enumerated true 128 3200 superposed"
-- `w2` and `pending` are `routeOf`'s rows, unchanged
#guard routeFacts ⟨docK [.fixed "u0" (.norm needNotX) []] .soft frame4, ["y_permitted"]⟩ == "w2 true 1 1 w2"
#guard (routeFacts ⟨docK [.set ⟨"rs1", "u1", 1, [⟨"a", none, [], []⟩, cand "b" mustX]⟩] .soft frame4,
  ["y_permitted"]⟩).endsWith " pending"

/-! ## W-13 (14.11): large, well formed

`NSDbig n`: `n` sets of a strict and a default reading with a sufficient condition, one fixed unit, `2^n` choices.
At `maxSdCheckWork` = 32,768 (measured, docs/rd-9/sc-11/w13-cpu.md; DRI decision 2026-11-09 item 1) the largest is 8 sets (256 choices, work
24,832, 0.71 s of compiled Lean CPU); 11 sets have more than `maxChoiceChecks` choices; and 8 sets with one wide
guard, or 10 sets, are over the work limit, which is read before any choice's text (`sdChecked`'s `&&`). -/

def wide : Nat → VE.Formula
  | 0 => .unary "c" (.var 0)
  | k + 1 => .and (wide k) (wide k)
def NSDbig (n : Nat) (g : VE.Formula := .top) (gated : Nat := 1) : NDoc :=
  ⟨docK (.fixed "u0" (.norm needNotX) [] :: (List.range n).map (fun k => softSet k (if k < gated then g else .top)))
    .soft frame4, ["y_permitted"]⟩

#guard routeFacts (NSDbig 8) == "enumerated true 256 24832 superposed"
#guard routeFacts (NSDbig 11) == "enumerated true 1025 136325 enumerated" && (choices (NSDbig 11).D).length == 65
#guard routeFacts (NSDbig 8 (wide 5)) == "enumerated true 256 48896 enumerated"
#guard routeFacts (NSDbig 10) == "enumerated true 1024 123904 enumerated"
-- `maxChoiceChecks` still binds first where a choice charges few units: 2048 choices, 9 units each
def NSDcount : NDoc := ⟨docK (.set ⟨"rs0", "u0", 1, [cand "do" (strictNode "must-x" "x_required" true),
  cand "need-not" (strictNode "need-not-x" "x_required" false)]⟩ :: (List.range 10).map (fun k => binarySet (k + 1)))
  .soft frame4, ["y_permitted"]⟩
#guard routeFacts NSDcount == "enumerated true 1025 9225 enumerated"
-- at most 64 choices over the work limit: enumerated, today's row (ten guarded fixed rules, 543 units a choice)
def guarded (k : Nat) : Item := .fixed s!"g{k}" (.norm (strictNode s!"guarded-{k}"
  (["x_required", "x_permitted", "y_permitted"][k % 3]!) true (wide 4))) []
def NSDheavy : NDoc := ⟨{ (NSDbig 6).D with items := (NSDbig 6).D.items ++ (List.range 10).map guarded }, ["y_permitted"]⟩
#guard routeFacts NSDheavy == "enumerated true 64 34752 enumerated"

end VE.Readings.SoftSupWireExamples
