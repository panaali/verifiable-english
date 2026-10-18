import VE.Cardinality.Theorems
import VE.Order.Tableau
import VE.Order.Wire

/-! Fixtures of `cardinality@0`'s core (docs/spec/quantities.md 9.1: FA1, FA1b, FA1c, FA2, FA3, FA8, FA9a, FA9c, FA10).

Each `#guard` fails the build when the definition it exercises changes its answer. `holdsFin` is the test oracle: it
counts each body directly on a finite model, with no regions, so comparing it with the erased formula on
`withRegionsFinite` checks erasure on that model. FA1's certificate was found by Python's untrusted search on the
erased problem; Lean replays it here. -/
namespace VE.Cardinality.Examples
open VE.Cardinality
open VE.Time (QFormula)

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

/-- The meaning on a finite model, counting each body directly. -/
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
         constants := fun c => if c == "cardinality__fomc_policymaker__0" then some (.qty dl) else none }
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

-- `fomc` declares `cardinality__fomc_policymaker__0`, so it is not `WellFormed` and the decoder refuses it (QT-A3).
-- Without that check, "the constant is 5" holds on the model and fails on its erasure, which overwrites the
-- constant with its region's size 0: `erase_iff` needs `WellFormed`.
def collide : CFormula := .quantity (.eq (.const dl "cardinality__fomc_policymaker__0") (.num dl 5))
def collideModel : VE.Order.FiniteModel Nat :=
  { rowsModel pm [([inc], 2)] with
    constants := fun c => if c == "cardinality__fomc_policymaker__0" then some (.inr 5) else none }
#guard (regionTable fomc [collide, .count (exactlyAtom pm (.atom inc) 2)]).map (·.1) =
  ["cardinality__fomc_policymaker__0", "cardinality__fomc_policymaker__1"]
#guard holdsFin collideModel collide
#guard !erasedFin fomc [collide, .count (exactlyAtom pm (.atom inc) 2)] collideModel collide

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

/-! ## The meaning itself, on a two-object structure -/

/-- Two users, the first curious. -/
def two : VE.Time.TStructure Nat where
  objects s x := s = "user" ∧ x < 2
  constant _ := none
  relation p vs := p = "curious" ∧ vs = [.obj 0]

theorem two_some : HasCount two "user" (.and .any harm) 1 :=
  ⟨[0], by simp, rfl, fun x => by simp [two, Body.holds, harm]; omega⟩

theorem two_all : HasCount two "user" .any 2 :=
  ⟨[0, 1], by simp, rfl, fun x => by simp [two, Body.holds]; omega⟩

-- "More than half" fails (1 of 2) and "at least 1 in 1,000" holds.
example : ¬ moreThanHalf.holds two := by
  rintro ⟨n, m, hn, hm, -, h⟩
  rw [hasCount_unique hn two_all, hasCount_unique hm two_some] at h
  simp [Cmp.holds] at h

example : oneIn1000.holds two := ⟨2, 1, two_all, two_some, by omega, by simp [Cmp.holds]⟩

end VE.Cardinality.Examples
