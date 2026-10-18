import VE.Cardinality.Theorems
import VE.Order.Tableau
import VE.Order.Wire
import VE.Readings.Strings

/-! Fixtures of `cardinality@0`'s core (docs/spec/quantities.md 9.1: FA1, FA1b, FA1c, FA2, FA3, FA8, FA9a, FA9c, FA10).

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

end VE.Cardinality.Examples
