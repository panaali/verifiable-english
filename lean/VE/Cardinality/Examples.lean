import VE.Cardinality.Theorems
import VE.Order.Tableau
import VE.Order.Wire
import VE.Readings.Strings

/-! Fixtures of `cardinality@0`'s core (docs/spec/quantities.md 9.1: FA1, FA1b, FA1c, FA2, FA3, FA4, FA4c, FA4d, FA4e,
FA5, FA5b, FA8, FA9a, FA9c, FA9e, FA10).

Each `#guard` fails the build when the definition it exercises changes its answer. `holdsFin` is the test oracle: it
counts each body directly on a finite model, with no regions, so comparing it with the erased formula on
`withRegionsFinite` checks erasure on that model. FA1's certificate was found by Python's untrusted search on the
erased problem; Lean replays it here. -/
namespace VE.Cardinality.Examples
open VE.Cardinality
open VE.Time (QFormula TStructure)

/-- A finite model of one sort: `rows` lists, for each kind of object, the predicates it has and how many there are. -/
def rowsModel (s : String) (rows : List (List String × Nat)) : VE.Order.FiniteModel Nat :=
  let objs := (rows.flatMap fun r => List.replicate r.2 r.1).zipIdx
  { domains := fun t => if t == s then objs.map (·.2) else []
    constants := fun _ => none
    relations := fun p => (objs.filter (·.1.contains p)).map (fun o => [.inl o.2]) }

def cmpB : Cmp → Int → Int → Bool
  | .gt, a, b => b < a
  | .ge, a, b => b ≤ a
  | .lt, a, b => a < b
  | .le, a, b => a ≤ b
  | .eq, a, b => a == b

/-- A ratio operand's integer on a finite model: a closed term's value, or a count. -/
def valFin (M : VE.Order.FiniteModel Nat) : CTerm → Option Int
  | .quantity t => match t.erase.denote M.asStructure [] with
    | some (.inr z) => some z
    | _ => none
  | .count s b => some (countFin M s b)

/-- The meaning on a finite model, counting each body directly; rounding is decided by `VE.Numbers.RoundsTo`. -/
def holdsFin (M : VE.Order.FiniteModel Nat) : CFormula → Bool
  | .quantity a => a.erase.eval M []
  | .count c =>
    let lhs := (c.terms.map fun kb => kb.1 * (countFin M c.sort kb.2 : Int)).sum
    match c.rel with
    | .lt => lhs < c.bound
    | .le => lhs ≤ c.bound
    | .eq => lhs == c.bound
  | .proportion p =>
    let n := countFin M p.sort p.whole
    0 < n && cmpB p.cmp (p.den * (countFin M p.sort (.and p.whole p.part) : Int)) (p.num * (n : Int))
  | .roundsTo r n d D k => match valFin M n, valFin M d with
    | some a, some b => 0 < b && decide (VE.Numbers.RoundsTo r ⟨D, k⟩ ((a : Rat) / b))
    | _, _ => false
  | .percentOf p w D k => match valFin M p, valFin M w with
    | some a, some b => 0 < b && 100 * 10 ^ k * a == D * b
    | _, _ => false
  | .percentRoundsTo r p w D k => match valFin M p, valFin M w with
    | some a, some b => 0 < b && decide (VE.Numbers.RoundsTo r ⟨D, k⟩ ((100 * a : Rat) / b))
    | _, _ => false
  | .not a => !holdsFin M a
  | .and a b => holdsFin M a && holdsFin M b
  | .or a b => holdsFin M a || holdsFin M b
  | .implies a b => !holdsFin M a || holdsFin M b

/-- The erased formula on the model with its region sizes. -/
def erasedFin (E : CEnv) (fs : List CFormula) (M : VE.Order.FiniteModel Nat) (a : CFormula) : Bool :=
  (a.erase E fs).erase.eval (withRegionsFinite E fs M) []

/-- Meaning and erasure agree on every formula of the problem, and every region and bridge premise holds. -/
def agrees (E : CEnv) (fs : List CFormula) (M : VE.Order.FiniteModel Nat) : Bool :=
  fs.all (fun a => holdsFin M a == erasedFin E fs M a) &&
    (nonnegPremises E fs ++ bridgePremises E fs).all (fun q => q.erase.eval (withRegionsFinite E fs M) [])

/-! ## FA1: news S3, "16 of the 18 FOMC policymakers …" -/

def pm : String := "fomc_policymaker"
def inc : String := "expects_further_increase"
def stay : String := "expects_rates_to_stay"

def fomc : CEnv where
  q := { sorts := [pm, "user"], tags := [],
         predicates := fun p => if p == inc || p == stay then some [.obj pm]
           else if p == "curious" then some [.obj "user"]
           else if p == "advises" then some [.obj pm, .obj pm] else none,
         constants := fun _ => none }
  finite := [pm]

def isInc : QFormula := .unary inc (.var 0)
def isStay : QFormula := .unary stay (.var 0)
def noneBoth : CFormula := .quantity (.all pm (.not (.and isInc isStay)))
def fa1Conclusion : CFormula := .quantity (.all pm (.or isInc isStay))
def fa1 : List CFormula :=
  [.count (exactlyAtom pm .any 18), .count (exactlyAtom pm (.atom inc) 16),
    .count (exactlyAtom pm (.atom stay) 2), noneBoth]
/-- The reading "at least 16 of the 18". -/
def fa1AtLeast : List CFormula :=
  [.count (exactlyAtom pm .any 18), .count (atLeastAtom pm (.atom inc) 16),
    .count (exactlyAtom pm (.atom stay) 2), noneBoth]

#guard (fa1Conclusion :: fa1).all (·.admits fomc)
#guard (regionTable fomc (fa1Conclusion :: fa1)).map (·.1) =
  ["cardinality__fomc_policymaker__00", "cardinality__fomc_policymaker__01",
   "cardinality__fomc_policymaker__10", "cardinality__fomc_policymaker__11"]
#guard predsOn fomc (fa1Conclusion :: fa1) pm = [inc, stay]
#guard (bridgePremises fomc (fa1Conclusion :: fa1)).length = 2
#guard (erasedProblem fomc fa1 fa1Conclusion).1.length = 10
#guard problemLimits fomc (fa1Conclusion :: fa1) matches .ok ()
-- 91 formula and term nodes in the erased problem, within W6a's 10,000-node aggregate.
#guard (((erasedProblem fomc fa1 fa1Conclusion).1 ++ [(erasedProblem fomc fa1 fa1Conclusion).2]).map
  (fun q => VE.Order.Wire.formulaNodes q.erase)).sum = 91

/-- Replay a certificate trace on the erased problem with the frozen order checker. -/
def replays (ps : List CFormula) (c : CFormula) (t : VE.Order.Tableau.Trace) : Bool :=
  VE.Order.Tableau.checkCertificate (fomc.elab (c :: ps)).erase ((erasedProblem fomc ps c).1.map QFormula.erase)
    (erasedProblem fomc ps c).2.erase ⟨VE.Order.Tableau.checkerVersion, "", [], "", t⟩

/-- Found by `ve.entailment.prove_entailment` on the regenerated problem (untrusted search). -/
def fa1Trace : VE.Order.Tableau.Trace :=
  .expand 4 none [.expand 5 none [.expand 10 none [.expand 15 none [.expand 11 none [.expand 18 none [
    .expand 19 none [.expand 12 none [.neq 22 [.farkas [] ⟨[(0, 1), (23, 1)], []⟩, .expand 13 none [.close,
      .farkas [] ⟨[(6, 1), (7, -1), (8, -1), (23, 1), (24, 1)], []⟩]], .close]]], .expand 12 none [.close, .close]]]]]]

#guard replays fa1 fa1Conclusion fa1Trace
-- Under the reading "at least 16" the conclusion still follows; the inequality takes a nonnegative multiplier.
def fa1AtLeastTrace : VE.Order.Tableau.Trace :=
  .expand 4 none [.expand 5 none [.expand 10 none [.expand 15 none [.expand 11 none [.expand 18 none [
    .expand 19 none [.expand 12 none [.neq 22 [.farkas [] ⟨[(0, 1), (23, 1)], []⟩, .expand 13 none [.close,
      .farkas [] ⟨[(6, 1), (7, 1), (8, -1), (23, 1), (24, 1)], []⟩]], .close]]], .expand 12 none [.close, .close]]]]]]
#guard replays fa1AtLeast fa1Conclusion fa1AtLeastTrace
#guard !replays fa1AtLeast fa1Conclusion fa1Trace
-- The trace does not close the problem without the exclusion premise.
#guard !replays fa1.dropLast fa1Conclusion fa1Trace

theorem fomc_wellFormed : fomc.WellFormed := ⟨by decide, fun _ _ h => nomatch h⟩

/-- FA1 end to end (spec 3.6): the replayed certificate proves the counting claim itself, through
`erasedProblem_admitted`, the frozen checker's soundness and `cardinality_elab_sound`. -/
theorem fa1_entails : CEntails.{0} fomc fa1 fa1Conclusion := by
  have hps : ∀ a ∈ fa1, Admitted fomc a := fun a ha => admits_sound _ _ (by revert a ha; decide +kernel)
  have hc : Admitted fomc fa1Conclusion := admits_sound _ _ (by decide +kernel)
  have hadm := erasedProblem_admitted fomc fomc_wellFormed fa1 fa1Conclusion hps hc
  exact cardinality_elab_sound fomc fomc_wellFormed fa1 fa1Conclusion hps hc
    (VE.Time.tentails_of_entails (fun a ha => hadm a (List.mem_append_left _ ha)) (hadm _ (by simp))
      (VE.Order.Tableau.checkCertificate_sound _ _ _ _ (by decide +kernel : replays fa1 fa1Conclusion fa1Trace)))

/-- A model of FA1 (2 stay only, 16 increase only): every premise, bridge and the conclusion hold, so it refutes
nothing. -/
def fa1Model : VE.Order.FiniteModel Nat := rowsModel pm [([stay], 2), ([inc], 16)]
#guard agrees fomc (fa1Conclusion :: fa1) fa1Model && !refutesC fomc fa1 fa1Conclusion fa1Model
#guard (fa1Conclusion :: fa1).all (holdsFin fa1Model)

/-- FA1b's countermodel (neither, stay only, increase only, both) = (1, 1, 15, 1). -/
def fa1bModel : VE.Order.FiniteModel Nat := rowsModel pm [([], 1), ([stay], 1), ([inc], 15), ([inc, stay], 1)]

#guard refutesC fomc fa1.dropLast fa1Conclusion fa1bModel
#guard agrees fomc (fa1Conclusion :: fa1.dropLast) fa1bModel
#guard (fa1.dropLast.map (holdsFin fa1bModel), holdsFin fa1bModel fa1Conclusion) = ([true, true, true], false)
-- With the exclusion premise the same model is no countermodel: it breaks that premise.
#guard !refutesC fomc fa1 fa1Conclusion fa1bModel
#guard agrees fomc (fa1Conclusion :: fa1) fa1bModel

/-- FA1c: "at least 16" with "at most 2", exclusion kept, refuted by (1, 0, 17, 0); so the reading matters. -/
def fa1c : List CFormula :=
  [.count (exactlyAtom pm .any 18), .count (atLeastAtom pm (.atom inc) 16),
    .count (atMostAtom pm (.atom stay) 2), noneBoth]
def fa1cModel : VE.Order.FiniteModel Nat := rowsModel pm [([], 1), ([inc], 17)]
#guard refutesC fomc fa1c fa1Conclusion fa1cModel
#guard agrees fomc (fa1Conclusion :: fa1c) fa1cModel
#guard !refutesC fomc fa1AtLeast fa1Conclusion fa1cModel

/-! ## FA2: agreement with W6a's counting forms on models of 6, 7 and 8 objects -/

/-- `k` of `total` objects expect an increase, and the first `j` of those also expect rates to stay. -/
def flagged (total k j : Nat) : VE.Order.FiniteModel Nat :=
  rowsModel pm [([inc, stay], j), ([inc], k - j), ([], total - k)]

/-- Each count atom, erased and evaluated with its region sizes, against W6a's sugar on the same model. -/
def agreeOn (M : VE.Order.FiniteModel Nat) (n m : Nat) : Bool :=
  let b : Body := .atom inc
  let w := fun (f : VE.Order.Formula) => f.eval M []
  let e := fun (a : CFormula) => erasedFin fomc [a] M a
  e (.count (atLeastAtom pm b n)) == w (VE.Time.atLeast pm n b.toFormula) &&
  e (.count (atMostAtom pm b n)) == w (VE.Time.atMost pm n b.toFormula) &&
  e (.count (exactlyAtom pm b n)) == w (VE.Time.exactly pm n b.toFormula) &&
  e (nOfMFormula pm n m b (.atom stay)) == w (VE.Time.nOfM pm n m b.toFormula (Body.atom stay).toFormula)

#guard [6, 7, 8].all fun t => (List.range 4).all fun k => (List.range (k + 1)).all fun j =>
  (List.range 4).all fun n => (List.range 4).all fun m => agreeOn (flagged t k j) n m
-- Every number of flagged objects, at the bound 2.
#guard [6, 7, 8].all fun t => (List.range (t + 1)).all fun k => agreeOn (flagged t k 0) 2 2
-- A model may list an object twice; it is still one object.
def dupModel : VE.Order.FiniteModel Nat := { flagged 3 2 0 with domains := fun t => if t == pm then [0, 1, 0, 2] else [] }
#guard (List.range 4).all fun n => agreeOn dupModel n 2

/-! ## FA3, FA8: admission and the problem limits -/

-- "Exactly 16 of the 18" is admitted here; W6a's sugar caps "n of m" at 7.
#guard (nOfMFormula pm 16 18 .any (.atom inc)).admits fomc
-- A count over a sort not declared finite; a binary predicate; another sort's predicate; a fraction 3 in 2;
-- a denominator 0. Each is refused, and "exactly 16" on the finite sort is admitted.
#guard !(CFormula.count (exactlyAtom "user" (.atom "curious") 2)).admits fomc
#guard !(CFormula.count (exactlyAtom pm (.atom "advises") 2)).admits fomc
#guard !(CFormula.count (exactlyAtom pm (.atom "curious") 2)).admits fomc
#guard !(CFormula.proportion ⟨pm, .any, .atom inc, .gt, 3, 2⟩).admits fomc
#guard !(CFormula.proportion ⟨pm, .any, .atom inc, .gt, 0, 0⟩).admits fomc
#guard (CFormula.count (exactlyAtom pm (.atom inc) 16)).admits fomc

def many (k : Nat) : Body := (List.range k).foldr (fun i b => .and (.atom s!"p{i}") b) .any
def manyQ (k : Nat) : QFormula := .all pm ((List.range k).foldr (fun i b => .and (.unary s!"p{i}" (.var 0)) b) .top)

#guard problemLimits fomc [.count (exactlyAtom pm (many 7) 1)] matches
  .error "ResourceLimit: At most 6 predicates on counted sort fomc_policymaker (64 regions)"
#guard problemLimits fomc [.count (exactlyAtom pm (many 6) 1)] matches .ok ()
-- A universal statement with seven predicates and no count makes no region; with a count over its sort, it does.
#guard (regionTable fomc [.quantity (manyQ 7)]).length = 0
#guard problemLimits fomc [.quantity (manyQ 7)] matches .ok ()
#guard problemLimits fomc [.quantity (manyQ 7), .count (exactlyAtom pm .any 1)] matches
  .error "ResourceLimit: At most 6 predicates on counted sort fomc_policymaker (64 regions)"
#guard problemLimits fomc ((List.range 9).map fun i => .count (exactlyAtom s!"s{i}" .any 1)) matches
  .error "ResourceLimit: At most 8 counted sorts"
#guard problemLimits fomc ((List.range 8).map fun i => .count (exactlyAtom s!"s{i}" .any 1)) matches .ok ()

/-! ## FA9a: a declared constant spelled like a region constant -/

/-- `fomc` with a declared constant spelled like a region constant: not `WellFormed`, so the decoder refuses it
(QT-A3). Without that check, "the constant is 5" holds on the model and fails on its erasure, which overwrites the
constant with its region's size 0: `erase_iff` needs `WellFormed`. -/
def colliding : CEnv :=
  { fomc with q := { fomc.q with
      constants := fun c => if c == "cardinality__fomc_policymaker__0" then some (.qty dl) else none } }
def collide : CFormula := .quantity (.eq (.const dl "cardinality__fomc_policymaker__0") (.num dl 5))
def collideModel : VE.Order.FiniteModel Nat :=
  { rowsModel pm [([inc], 2)] with
    constants := fun c => if c == "cardinality__fomc_policymaker__0" then some (.inr 5) else none }
#guard [collide, .count (exactlyAtom pm (.atom inc) 2)].all (·.admits colliding)
#guard (regionTable colliding [collide, .count (exactlyAtom pm (.atom inc) 2)]).map (·.1) =
  ["cardinality__fomc_policymaker__0", "cardinality__fomc_policymaker__1"]
#guard holdsFin collideModel collide
#guard !erasedFin colliding [collide, .count (exactlyAtom pm (.atom inc) 2)] collideModel collide

/-! ## FA9c, FA10: an empty population -/

def users : CEnv := { fomc with finite := [pm, "user"] }
def harm : Body := .atom "curious"
/-- "At least 1 in 1,000 of the users …" as a proportion, and as the bare count atom `−1,000 × #harm + #users ≤ 0`. -/
def oneIn1000 : CFormula := .proportion ⟨"user", .any, harm, .ge, 1, 1000⟩
def bareAtom : CFormula := .count ⟨"user", [(-1000, harm), (1, .any)], .le, 0⟩
def moreThanHalf : CFormula := .proportion ⟨"user", .any, harm, .gt, 1, 2⟩
def userModel (yes no : Nat) : VE.Order.FiniteModel Nat := rowsModel "user" [(["curious"], yes), ([], no)]

#guard [oneIn1000, bareAtom, moreThanHalf].all (·.admits users)
#guard !holdsFin (userModel 0 0) oneIn1000 && holdsFin (userModel 0 0) bareAtom
#guard (([(1, 999), (0, 1000), (1, 1000), (1, 1001)] : List (Nat × Nat)).map fun r =>
  holdsFin (userModel r.1 r.2) oneIn1000) = [true, false, false, false]
#guard (([(0, 0), (2, 2), (3, 2)] : List (Nat × Nat)).map fun r =>
  holdsFin (userModel r.1 r.2) moreThanHalf) = [false, false, true]
#guard ([(0, 0), (3, 2), (1, 999)] : List (Nat × Nat)).all fun r =>
  agrees users [oneIn1000, bareAtom, moreThanHalf] (userModel r.1 r.2)

/-! ## FA4, FA4e: rounding a ratio of two numbers (VE's paper), each claim's (meaning, erasure) -/

def num (z : Int) : CTerm := .quantity (.num dl z)
def rounds (r : VE.Numbers.Rounding) (a b D : Int) (k : Nat) : CFormula := .roundsTo r (num a) (num b) D k
def none0 : VE.Order.FiniteModel Nat := rowsModel pm []
def both (E : CEnv) (M : VE.Order.FiniteModel Nat) (f : CFormula) : Bool × Bool := (holdsFin M f, erasedFin E [f] M f)
def nums : CFormula → Bool × Bool := both fomc none0

def fa4 : List CFormula := [rounds .tiesUp 176 594 296 3, rounds .halfEven 176 594 296 3, rounds .tiesUp 52 243 214 3,
  rounds .tiesUp 31 243 128 3, rounds .tiesUp 21 243 86 3, rounds .tiesUp 26 100 3 1]
#guard fa4.all (·.admits fomc) && fa4.all (nums · == (true, true))
-- "0.297" is false, and "0.30" (two places) is a different claim from "0.3".
#guard [rounds .tiesUp 176 594 297 3, rounds .tiesUp 26 100 30 2].all (nums · == (false, false))
-- The tie fixture, one per rule: 1/8 = 0.125.
#guard (nums (rounds .tiesUp 1 8 13 2), nums (rounds .tiesUp 1 8 12 2)) = ((true, true), (false, false))
#guard (nums (rounds .halfEven 1 8 13 2), nums (rounds .halfEven 1 8 12 2)) = ((false, false), (true, true))
#guard [rounds .tiesUp 1 2 0 0, rounds .tiesUp 1 2 1 0, rounds .halfEven 1 2 0 0, rounds .halfEven 1 2 1 0,
  rounds .halfEven 3 2 2 0, rounds .halfEven 3 2 1 0].map (nums · |>.1) = [false, true, true, false, true, false]
-- FA4e: ties go to the larger value, also below 0, for a ratio and for a percent.
#guard [rounds .tiesUp (-1) 2 0 0, .percentRoundsTo .tiesUp (num (-1)) (num 200) 0 0].all (nums · == (true, true))
#guard [rounds .tiesUp (-1) 2 (-1) 0, .percentRoundsTo .tiesUp (num (-1)) (num 200) (-1) 0].all
  (nums · == (false, false))
-- Meaning and erasure agree on a grid, every rule, for a ratio and for a percent; a zero denominator holds neither.
#guard [VE.Numbers.Rounding.tiesUp, .halfEven, .down, .up].all fun r => (List.range 7).all fun a =>
  (List.range 4).all fun b => (List.range 9).all fun D => (List.range 2).all fun k =>
    let (a, b, D) := ((a : Int) - 3, (b : Int), (D : Int) - 4)
    [rounds r a b D k, .percentRoundsTo r (num a) (num b) (10 * D) k, .percentOf (num a) (num b) (10 * D) k].all
      fun f => (nums f).1 == (nums f).2

/-! ## FA4c, FA4d: counts as operands; "divided by" names each operand's whole body -/

def dec : String := "decision"
def paper : CEnv where
  q := { fomc.q with sorts := [dec], predicates := fun p =>
    if p == "scored" || p == "false_approval" then some [.obj dec] else none }
  finite := [dec]
def scored : Body := .atom "scored"
def falseApp : Body := .atom "false_approval"
/-- "The number of scored decisions that are false approvals, divided by the number of scored decisions, rounds to
…". -/
def fa4c (D : Int) : CFormula := .roundsTo .tiesUp (.count dec (.and scored falseApp)) (.count dec scored) D 3
/-- The other reading "out of" allowed: every false approval, scored or not. -/
def fa4dOther (D : Int) : CFormula := .roundsTo .tiesUp (.count dec falseApp) (.count dec scored) D 3
/-- Region sizes (neither, scored only, false approval only, both) = (5, 418, `u`, 176). -/
def paperModel (u : Nat) : VE.Order.FiniteModel Nat :=
  rowsModel dec [([], 5), (["scored"], 418), (["false_approval"], u), (["scored", "false_approval"], 176)]

#guard [fa4c 296, fa4dOther 296].all (·.admits paper)
-- Each claim's (meaning, erasure): with no unscored false approval both readings give 0.296; with 3 they part.
#guard [fa4c 296, fa4c 297, fa4dOther 296].map (both paper (paperModel 0)) = [(true, true), (false, false), (true, true)]
#guard [fa4c 296, fa4dOther 296, fa4dOther 301].map (both paper (paperModel 3)) =
  [(true, true), (false, false), (true, true)]
-- `erasedProblem_admitted` on FA4c: 4 region premises and the erased claim, each W6a-admitted in `E.elab`.
#guard (erasedProblem paper [] (fa4c 296)).1.length = 4 &&
  ((erasedProblem paper [] (fa4c 296)).1 ++ [(erasedProblem paper [] (fa4c 296)).2]).all
    (·.admits (paper.elab [fa4c 296]) [])

/-! ## FA5, FA5b: PCE estimates in basis points (September 370, June 360); FA9e: admission of ratios -/

def news : CEnv where
  q := { fomc.q with
    tags := ["bp", "day", "elapsed_day"]
    constants := fun c => if c == "sept" || c == "june" then some (.qty "bp") else none }
  finite := fomc.finite
def sept : CTerm := .quantity (.const "bp" "sept")
def june : CTerm := .quantity (.const "bp" "june")
def pce (s : Int) : VE.Order.FiniteModel Nat :=
  { none0 with
    constants := fun c => if c == "sept" then some (.inr s) else if c == "june" then some (.inr 360) else none }
def fa5 : List CFormula := [.roundsTo .tiesUp sept june 1028 3, .roundsTo .halfEven sept june 1028 3,
  .percentRoundsTo .tiesUp sept june 103 0, .percentOf sept june 103 0, .percentOf sept june 1027778 4]
/-- "… is exactly 105 percent of …" against "… minus … equals 5 percentage points" (500 at 2 places). -/
def relative : CFormula := .percentOf sept june 105 0
def points : CFormula :=
  .quantity (.eq (.add "bp" (.const "bp" "sept") (.scale "bp" (-1) (.const "bp" "june"))) (.num "bp" 500))

#guard fa5.all (·.admits news) && [relative, points].all (·.admits news)
#guard fa5.map (both news (pce 370)) = [(true, true), (true, true), (true, true), (false, false), (false, false)]
#guard [370, 378, 860].map (fun s => (both news (pce s) relative, both news (pce s) points)) =
  [((false, false), (false, false)), ((true, true), (false, false)), ((false, false), (true, true))]
-- FA9e: `down` and `up` are not admitted; two dates, a rate against a count, and a rate against a date are refused;
-- two durations, and a count against a dimensionless number, are admitted.
def date : CTerm := .quantity (.num "day" 1)
def dur : CTerm := .quantity (.num "elapsed_day" 3)
#guard ![CFormula.roundsTo .down sept june 1 0, .percentRoundsTo .up sept june 1 0, .roundsTo .tiesUp date date 1 0,
  .percentOf date date 1 0, .roundsTo .halfEven sept (.count pm .any) 1 0, .percentOf sept date 1 0].any
    (·.admits news)
#guard [CFormula.roundsTo .tiesUp dur dur 1 0, .percentOf (.count pm (.atom inc)) (num 4) 1 0].all (·.admits news)

/-! ## Every case of the trusted meaning and admission, in both directions

Standing ruling R16 signs the trusted lines of `Syntax.lean` and `Semantics.lean` only when every definition is
exercised by a check that can fail. Each theorem below states a case of a definition that a changed case falsifies,
true cases beside false ones, so `tools/trust_map.py` sees the definition used (`tests/test_cardinality_exercised.py`)
and every bug of `docs/quantities/qt-a1/mutants.json` fails the build. -/

/-- Two users, the first curious: a share is 1 in 2. -/
def two : VE.Time.TStructure Nat where
  objects s x := s = "user" ∧ x < 2
  constant _ := none
  relation p vs := p = "curious" ∧ vs = [.obj 0]

theorem two_some : HasCount two "user" (.and .any harm) 1 :=
  ⟨[0], by simp, rfl, fun x => by simp [two, Body.holds, harm]; omega⟩

theorem two_all : HasCount two "user" .any 2 :=
  ⟨[0, 1], by simp, rfl, fun x => by simp [two, Body.holds]; omega⟩

-- The first user is curious and the second is not; `or` and `and` combine both sides.
theorem body_cases : Body.holds two 0 harm ∧ ¬ Body.holds two 1 harm ∧ Body.holds two 1 (.not harm) ∧
    ¬ Body.holds two 0 (.not harm) ∧ Body.holds two 1 .any ∧ Body.holds two 1 (.or harm (.not harm)) ∧
    ¬ Body.holds two 1 (.or harm harm) ∧ Body.holds two 0 (.and .any harm) ∧ ¬ Body.holds two 1 (.and .any harm) := by
  simp [Body.holds, two, harm]

theorem harm_two : HasCount two "user" harm 1 :=
  ⟨[0], by simp, rfl, fun x => by simp [two, Body.holds, harm]; omega⟩
theorem not_harm_two : HasCount two "user" (.not harm) 1 :=
  ⟨[1], by simp, rfl, fun x => by simp [two, Body.holds, harm]; omega⟩
theorem harm_or_not_two : HasCount two "user" (.or harm (.not harm)) 2 :=
  ⟨[0, 1], by simp, rfl, fun x => by simp [two, Body.holds, harm]; omega⟩
theorem neither_two : HasCount two "user" (.and (.not harm) harm) 0 :=
  ⟨[], by simp, rfl, fun x => by simp [two, Body.holds, harm]⟩

/-- The terms of a count atom have one list of counts. -/
theorem counts_unique {α : Type} {T : TStructure α} (c : CountAtom) {ns ms : List Nat}
    (hn : Counts T c.sort c.terms ns) (hm : Counts T c.sort c.terms ms) : ns = ms := by
  suffices ∀ (terms : List (Int × Body)) (ns ms : List Nat), Counts T c.sort terms ns → Counts T c.sort terms ms →
    ns = ms from this _ _ _ hn hm
  intro terms
  induction terms with
  | nil => intro ns ms hn hm; cases ns <;> cases ms <;> first | rfl | exact (hn : False).elim | exact (hm : False).elim
  | cons kb rest ih =>
    intro ns ms hn hm
    cases ns <;> cases ms <;> first | exact (hn : False).elim | exact (hm : False).elim | skip
    rename_i n ns m ms
    rw [hasCount_unique hn.1 hm.1, ih ns ms hn.2 hm.2]

theorem counts_two : Counts two "user" [(1, .any), (-1, harm)] [2, 1] ∧ ¬ Counts two "user" [(1, .any)] [] ∧
    ¬ Counts two "user" [] [2] ∧ ¬ Counts two "user" [(1, .any)] [2, 1] :=
  ⟨⟨two_all, harm_two, trivial⟩, id, id, fun h => h.2⟩

/-- On `two`, a count of every user compares 2 with the bound. -/
theorem everyone_two (r : Rel) (k : Int) : CountAtom.holds two ⟨"user", [(1, .any)], r, k⟩ ↔ r.holds 2 k := by
  constructor
  · rintro ⟨ns, hc, h⟩
    match ns, hc with
    | [n], ⟨hn, _⟩ => rw [hasCount_unique hn two_all] at h; simpa using h
  · intro h; exact ⟨[2], ⟨two_all, trivial⟩, by simpa using h⟩

def everyone (r : Rel) (k : Int) : CFormula := .count ⟨"user", [(1, .any)], r, k⟩

theorem rel_cases_two :
    (everyone .lt 3).holds two ∧ ¬ (everyone .lt 2).holds two ∧ (everyone .le 2).holds two ∧
    ¬ (everyone .le 1).holds two ∧ (everyone .eq 2).holds two ∧ ¬ (everyone .eq 1).holds two ∧
    ¬ (everyone .eq 3).holds two := by
  simp only [everyone, CFormula.holds, everyone_two, Rel.holds]; decide

-- "2 users, less one curious user, is 1": a term's coefficient multiplies its count.
theorem weighted_two : (CFormula.count ⟨"user", [(1, .any), (-1, harm)], .eq, 1⟩).holds two ∧
    ¬ (CFormula.count ⟨"user", [(1, .any), (-1, harm)], .eq, 3⟩).holds two := by
  have : ∀ k : Int, (CFormula.count ⟨"user", [(1, .any), (-1, harm)], .eq, k⟩).holds two ↔ k = 1 := fun k => by
    constructor
    · rintro ⟨ns, hc, h⟩
      rw [counts_unique ⟨"user", [(1, .any), (-1, harm)], .eq, k⟩ hc counts_two.1] at h
      simp [Rel.holds] at h; omega
    · rintro rfl; exact ⟨[2, 1], counts_two.1, by simp [Rel.holds]⟩
  exact ⟨(this 1).mpr rfl, fun h => by have := (this 3).mp h; omega⟩

/-- On `two`, the share of curious users is 1 in 2. -/
theorem share_two (c : Cmp) (num den : Nat) :
    Proportion.holds two ⟨"user", .any, harm, c, num, den⟩ ↔ c.holds den (num * 2) := by
  constructor
  · rintro ⟨n, m, hn, hm, -, h⟩
    rw [hasCount_unique hn two_all, hasCount_unique hm two_some] at h; simpa using h
  · intro h; exact ⟨2, 1, two_all, two_some, by omega, by simpa using h⟩

def share (c : Cmp) (num den : Nat) : CFormula := .proportion ⟨"user", .any, harm, c, num, den⟩

theorem cmp_cases_two :
    ¬ (share .gt 1 2).holds two ∧ (share .gt 1 3).holds two ∧ (share .ge 1 2).holds two ∧
    ¬ (share .ge 2 3).holds two ∧ ¬ (share .lt 1 2).holds two ∧ (share .lt 2 3).holds two ∧
    (share .le 1 2).holds two ∧ ¬ (share .le 1 3).holds two ∧ (share .eq 1 2).holds two ∧
    ¬ (share .eq 1 3).holds two ∧ ¬ (share .eq 2 3).holds two := by
  simp only [share, CFormula.holds, share_two, Cmp.holds]; omega

/-- No users. -/
def nobody : TStructure Nat where
  objects _ _ := False
  constant _ := none
  relation _ _ := False

-- "At least 0 in 1" holds of a nonempty population only; the share counts the whole that has the part.
theorem population_cases : (share .ge 0 1).holds two ∧ ¬ (share .ge 0 1).holds nobody ∧
    ¬ Proportion.holds two ⟨"user", .not harm, harm, .gt, 0, 1⟩ := by
  refine ⟨(share_two .ge 0 1).mpr (by simp [Cmp.holds]), ?_, ?_⟩
  · rintro ⟨n, m, hn, -, hpos, -⟩
    rw [hasCount_unique hn ⟨[], by simp, rfl, fun x => by simp [nobody]⟩] at hpos; simp at hpos
  · rintro ⟨n, m, -, hm, -, h⟩
    rw [hasCount_unique hm neither_two] at h; simp [Cmp.holds] at h

def somebodyCurious : QFormula := .ex "user" (.unary "curious" (.var 0))
def everybodyCurious : QFormula := .all "user" (.unary "curious" (.var 0))

theorem quantity_cases : (CFormula.quantity .top).holds two ∧ ¬ (CFormula.quantity .bottom).holds two ∧
    (CFormula.quantity somebodyCurious).holds two ∧ ¬ (CFormula.quantity everybodyCurious).holds two := by
  refine ⟨trivial, id, ⟨0, by simp [two], .obj 0, rfl, by simp [two]⟩, fun h => ?_⟩
  obtain ⟨v, hv, hr⟩ := h 1 (by simp [two])
  simp [VE.Time.QTerm.tdenote] at hv; subst hv; simp [two] at hr

/-- A true and a false statement about `two`. -/
def yes : CFormula := everyone .eq 2
def no : CFormula := everyone .eq 1

theorem connective_cases :
    (CFormula.not no).holds two ∧ ¬ (CFormula.not yes).holds two ∧
    (CFormula.and yes yes).holds two ∧ ¬ (CFormula.and yes no).holds two ∧ ¬ (CFormula.and no yes).holds two ∧
    (CFormula.or yes no).holds two ∧ (CFormula.or no yes).holds two ∧ ¬ (CFormula.or no no).holds two ∧
    (CFormula.implies no no).holds two ∧ (CFormula.implies no yes).holds two ∧
    (CFormula.implies yes yes).holds two ∧ ¬ (CFormula.implies yes no).holds two := by
  simp only [yes, no, everyone, CFormula.holds, everyone_two, Rel.holds]; decide

-- "More than half" fails (1 of 2) and "at least 1 in 1,000" holds.
theorem fa10_two : ¬ moreThanHalf.holds two ∧ oneIn1000.holds two := by
  simp only [moreThanHalf, oneIn1000, CFormula.holds, share_two, Cmp.holds]; decide

theorem two_admissible : Admissible users two := by
  refine ⟨⟨by simp [users, fomc], ?_⟩, fun s _ => ⟨if s = "user" then [0, 1] else [], fun x => ?_⟩⟩
  · rintro p vs ⟨rfl, rfl⟩
    exact ⟨[.obj "user"], by simp [users, fomc, inc, stay], by simp [two, VE.Time.TTuple, VE.Time.TValue.Typed]⟩
  · by_cases hs : s = "user" <;> simp [two, hs] <;> omega

/-- `erase_iff` in each direction on `two`: "at least 1 in 1,000 are curious" holds and its erasure holds; "more than
half are curious" fails and so does its erasure, where region constants are region sizes. -/
theorem erase_two : (oneIn1000.erase users [oneIn1000, moreThanHalf]).tdenote
      (withRegions users [oneIn1000, moreThanHalf] two) [] ∧
    ¬ (moreThanHalf.erase users [oneIn1000, moreThanHalf]).tdenote
      (withRegions users [oneIn1000, moreThanHalf] two) [] := by
  have hE : users.WellFormed := ⟨by decide, fun _ _ h => nomatch h⟩
  have ha : ∀ a ∈ [oneIn1000, moreThanHalf], a.admits users = true := by decide +kernel
  have hi := fun a h => erase_iff users hE _ two two_admissible a (admits_sound _ _ (ha a h)) h
  exact ⟨(hi _ (by simp)).mp fa10_two.2, fun h => fa10_two.1 ((hi _ (by simp)).mpr h)⟩

theorem mem_le_sum : ∀ {xs : List Nat} {x : Nat}, x ∈ xs → x ≤ xs.sum
  | _ :: _, _, .head _ => by simp
  | _ :: _, _, .tail _ h => by have := mem_le_sum h; simp; omega

/-- Every natural number is a user: no finite list holds them all. -/
def everyNat : TStructure Nat := { two with objects := fun s _ => s = "user" }
/-- `two` with a relation on a predicate `users` does not declare. -/
def wild : TStructure Nat := { two with relation := fun p vs => p = "nope" ∧ vs = [.obj 0] }

theorem admissible_cases : Admissible users two ∧ ¬ Admissible users everyNat ∧ ¬ Admissible users wild := by
  refine ⟨two_admissible, fun ⟨_, h⟩ => ?_, fun ⟨⟨_, h⟩, _⟩ => ?_⟩
  · obtain ⟨xs, hxs⟩ := h "user" (by simp [users])
    have := mem_le_sum ((hxs (xs.sum + 1)).mp rfl); omega
  · obtain ⟨τs, hp, -⟩ := h "nope" [.obj 0] ⟨rfl, rfl⟩
    simp [users, fomc, inc, stay] at hp

-- "At least 0 users" follows from no premises, "at least 1" from "exactly 2", and "at most 1" from neither.
theorem entails_cases : CEntails users [] (.count (atLeastAtom "user" .any 0)) ∧
    CEntails users [.count (exactlyAtom "user" .any 2)] (.count (atLeastAtom "user" .any 1)) ∧
    ¬ CEntails.{0} users [] (.count (atMostAtom "user" .any 1)) := by
  refine ⟨fun α T hT _ => ?_, fun α T hT hps => ?_, fun h => ?_⟩
  · obtain ⟨n, hn, -⟩ := hasCount_exists_unique users T hT "user" (by simp [users]) .any
    exact ⟨[n], ⟨hn, trivial⟩, by simp [atLeastAtom, Rel.holds]⟩
  · obtain ⟨ns, hc, h⟩ := hps _ (List.mem_singleton_self _)
    match ns, hc with
    | [n], ⟨hn, _⟩ =>
      simp [exactlyAtom, Rel.holds] at h
      exact ⟨[n], ⟨hn, trivial⟩, by simp [atLeastAtom, Rel.holds]; omega⟩
  · obtain ⟨ns, hc, h⟩ := h Nat two two_admissible (by simp)
    match ns, hc with
    | [n], ⟨hn, _⟩ =>
      rw [hasCount_unique hn two_all] at h
      simp [atMostAtom, Rel.holds] at h

-- FA9a's colliding constant begins with the region prefix, so `colliding` is not `WellFormed`.
theorem colliding_prefix : "cardinality__fomc_policymaker__0".startsWith regionPrefix = true := by
  have h := VE.Readings.startsWith_append_ascii regionPrefix "fomc_policymaker__0" (by decide)
  have e : regionPrefix ++ "fomc_policymaker__0" = "cardinality__fomc_policymaker__0" := by decide
  rwa [e] at h

/-- `fomc` with a constant `rate`, which no region constant can be; and with an undeclared finite sort. -/
def named : CEnv := { fomc with q := { fomc.q with constants := fun c => if c == "rate" then some (.qty dl) else none } }
def ghost : CEnv := { fomc with finite := ["ghost"] }

theorem wellFormed_cases : users.WellFormed ∧ named.WellFormed ∧ ¬ colliding.WellFormed ∧ ¬ ghost.WellFormed := by
  refine ⟨⟨by simp [users, fomc], by intro c τ h; simp [users, fomc] at h⟩, ⟨by simp [named, fomc], ?_⟩,
    fun h => ?_, fun h => ?_⟩
  · intro c τ h
    simp only [named] at h
    split at h
    · rename_i hc; simp at hc; subst hc; decide
    · simp at h
  · have := h.fresh "cardinality__fomc_policymaker__0" (.qty dl) (by simp [colliding])
    rw [colliding_prefix] at this; exact Bool.noConfusion this
  · exact absurd (h.finiteDeclared "ghost" (by simp [ghost])) (by simp [ghost, fomc, pm])

-- Each part of a statement is checked: the finite sort, the bodies' atoms below `not`, `and` and `or`, the fraction,
-- the W6a part (`nope` is undeclared), and both sides of each connective.
def good : CFormula := .count (exactlyAtom pm (.atom inc) 16)
def badQ : CFormula := .quantity (.all pm (.unary "nope" (.var 0)))
def badP : CFormula := .proportion ⟨"user", .any, harm, .ge, 1, 2⟩

theorem admitted_cases :
    Admitted fomc good ∧ ¬ Admitted fomc badQ ∧ ¬ Admitted fomc badP ∧ Admitted users badP ∧
    ¬ Admitted users (.proportion ⟨"user", .atom inc, harm, .ge, 1, 2⟩) ∧
    ¬ Admitted users (.proportion ⟨"user", .any, .atom inc, .ge, 1, 2⟩) ∧
    ¬ Admitted fomc (.count ⟨pm, [(1, .atom inc), (1, .atom "curious")], .le, 3⟩) ∧
    ¬ Admitted fomc (.count (exactlyAtom pm (.not (.atom "advises")) 1)) ∧
    ¬ Admitted fomc (.count (exactlyAtom pm (.and (.atom inc) (.atom "advises")) 1)) ∧
    ¬ Admitted fomc (.count (exactlyAtom pm (.or (.atom "advises") (.atom inc)) 1)) ∧
    Admitted fomc (.count (exactlyAtom pm (.or (.not (.atom stay)) (.and .any (.atom inc))) 1)) ∧
    Admitted users (.proportion ⟨"user", .any, harm, .le, 2, 2⟩) ∧
    ¬ Admitted users (.proportion ⟨"user", .any, harm, .le, 3, 2⟩) ∧
    ¬ Admitted users (.proportion ⟨"user", .any, harm, .le, 0, 0⟩) ∧
    Admitted fomc (.not good) ∧ ¬ Admitted fomc (.not badQ) ∧
    Admitted fomc (.and good good) ∧ ¬ Admitted fomc (.and good badQ) ∧ ¬ Admitted fomc (.and badQ good) ∧
    Admitted fomc (.or good good) ∧ ¬ Admitted fomc (.or good badQ) ∧ ¬ Admitted fomc (.or badQ good) ∧
    Admitted fomc (.implies good good) ∧ ¬ Admitted fomc (.implies good badQ) ∧
    ¬ Admitted fomc (.implies badQ good) := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
    first
    | exact admits_sound _ _ (by decide)
    | exact fun h => absurd (admits_complete _ _ h) (by decide)


/-! ## The ratio cases of the trusted meaning and admission (QT-A2), in both directions -/

def cur : CTerm := .count "user" harm
def all2 : CTerm := .count "user" .any

theorem den_cur (z : Int) : cur.Denotes two z ↔ z = 1 :=
  ⟨fun ⟨n, hn, e⟩ => by rw [e, hasCount_unique hn harm_two]; rfl, fun e => ⟨1, harm_two, e⟩⟩
theorem den_all (z : Int) : all2.Denotes two z ↔ z = 2 :=
  ⟨fun ⟨n, hn, e⟩ => by rw [e, hasCount_unique hn two_all]; rfl, fun e => ⟨2, two_all, e⟩⟩
theorem den_nobody (b : Body) (z : Int) : (CTerm.count "user" b).Denotes nobody z ↔ z = 0 :=
  ⟨fun ⟨n, hn, e⟩ => by rw [e, hasCount_unique hn ⟨[], by simp, rfl, fun x => by simp [nobody]⟩]; rfl,
    fun e => ⟨0, ⟨[], by simp, rfl, fun x => by simp [nobody]⟩, e⟩⟩
theorem den_num {α : Type} (T : TStructure α) (z z' : Int) : (num z).Denotes T z' ↔ z' = z := by
  simp [CTerm.Denotes, num, VE.Time.QTerm.tdenote, eq_comm]

-- A count denotes its count; a closed number its value; an object, no integer.
theorem denotes_cases : cur.Denotes two 1 ∧ ¬ cur.Denotes two 2 ∧ (num 7).Denotes two 7 ∧ ¬ (num 7).Denotes two 8 ∧
    ¬ (CTerm.quantity (.obj "x")).Denotes two 0 := by
  refine ⟨(den_cur 1).mpr rfl, fun h => by simp [den_cur] at h, (den_num _ 7 7).mpr rfl,
    fun h => by simp [den_num] at h, fun ⟨g, h⟩ => ?_⟩
  simp [VE.Time.QTerm.tdenote, two] at h

-- On `two` the share of curious users is 1/2 = 50 percent: rule, places, operand order and the positive denominator.
theorem ratio_cases :
    (CFormula.roundsTo .tiesUp cur all2 5 1).holds two ∧ ¬ (CFormula.roundsTo .tiesUp cur all2 5 0).holds two ∧
    ¬ (CFormula.roundsTo .tiesUp all2 cur 5 1).holds two ∧ (CFormula.roundsTo .tiesUp cur all2 1 0).holds two ∧
    (CFormula.roundsTo .halfEven cur all2 0 0).holds two ∧ ¬ (CFormula.roundsTo .halfEven cur all2 1 0).holds two ∧
    ¬ (CFormula.roundsTo .tiesUp cur all2 0 0).holds two ∧
    ¬ (CFormula.roundsTo .tiesUp (.count "user" harm) (.count "user" .any) 0 0).holds nobody ∧
    (CFormula.percentOf cur all2 50 0).holds two ∧ (CFormula.percentOf cur all2 500 1).holds two ∧
    ¬ (CFormula.percentOf cur all2 50 1).holds two ∧ ¬ (CFormula.percentOf all2 cur 50 0).holds two ∧
    ¬ (CFormula.percentOf (.count "user" harm) (.count "user" .any) 0 0).holds nobody ∧
    (CFormula.percentRoundsTo .tiesUp cur all2 50 0).holds two ∧
    ¬ (CFormula.percentRoundsTo .tiesUp cur all2 1 0).holds two ∧
    ¬ (CFormula.percentRoundsTo .tiesUp cur all2 500 0).holds two ∧
    ¬ (CFormula.percentRoundsTo .tiesUp (.count "user" harm) (.count "user" .any) 0 0).holds nobody ∧
    (CFormula.percentRoundsTo .tiesUp (num 1) (num 200) 1 0).holds two ∧
    (CFormula.percentRoundsTo .halfEven (num 1) (num 200) 0 0).holds two ∧
    ¬ (CFormula.percentRoundsTo .halfEven (num 1) (num 200) 1 0).holds two := by
  simp only [roundsTo_holds_iff den_cur den_all, roundsTo_holds_iff den_all den_cur,
    percentOf_holds_iff den_cur den_all, percentOf_holds_iff den_all den_cur, percentRoundsTo_holds_iff den_cur den_all,
    roundsTo_holds_iff (den_nobody _) (den_nobody _), percentOf_holds_iff (den_nobody _) (den_nobody _),
    percentRoundsTo_holds_iff (den_nobody _) (den_nobody _),
    percentRoundsTo_holds_iff (den_num two 1) (den_num two 200), erasedRounding]
  simp

theorem admittedRules_cases : VE.Numbers.Rounding.tiesUp ∈ admittedRules ∧ .halfEven ∈ admittedRules ∧
    .down ∉ admittedRules ∧ .up ∉ admittedRules := by decide

-- A count is dimensionless over a declared finite sort with a typed body; a quantity has its own tag.
theorem cterm_typed_cases : CTermTyped users cur dl ∧ ¬ CTermTyped users cur "bp" ∧ ¬ CTermTyped fomc cur dl ∧
    ¬ CTermTyped users (.count "user" (.atom inc)) dl ∧ CTermTyped news sept "bp" ∧ ¬ CTermTyped news sept dl ∧
    ¬ CTermTyped news (.quantity (.const "bp" "rate")) "bp" := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
    first
    | exact (tagOf_iff _ _ _).mp (by decide)
    | exact fun h => absurd ((tagOf_iff _ _ _).mpr h) (by decide)

-- Each ratio statement needs an admitted rule, one tag on both operands, and no date.
theorem admitted_ratio_cases :
    Admitted news (.roundsTo .tiesUp sept june 1 0) ∧ Admitted news (.roundsTo .halfEven sept june 1 0) ∧
    ¬ Admitted news (.roundsTo .down sept june 1 0) ∧ ¬ Admitted news (.roundsTo .tiesUp sept (.count pm .any) 1 0) ∧
    ¬ Admitted news (.roundsTo .tiesUp (.count pm .any) sept 1 0) ∧ ¬ Admitted news (.roundsTo .tiesUp date date 1 0) ∧
    Admitted news (.percentOf sept june 1 0) ∧ ¬ Admitted news (.percentOf date date 1 0) ∧
    ¬ Admitted news (.percentOf sept (.count pm .any) 1 0) ∧ ¬ Admitted news (.percentOf (.count pm .any) sept 1 0) ∧
    Admitted news (.percentRoundsTo .halfEven (.count pm .any) (num 3) 1 0) ∧
    ¬ Admitted news (.percentRoundsTo .up sept june 1 0) ∧ ¬ Admitted news (.percentRoundsTo .tiesUp date date 1 0) ∧
    ¬ Admitted news (.percentRoundsTo .tiesUp (num 3) sept 1 0) ∧
    ¬ Admitted news (.percentRoundsTo .tiesUp sept (num 3) 1 0) := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
    first
    | exact admits_sound _ _ (by decide)
    | exact fun h => absurd (admits_complete _ _ h) (by decide)

end VE.Cardinality.Examples
