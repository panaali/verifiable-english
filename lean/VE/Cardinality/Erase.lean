import VE.Cardinality.Semantics
import VE.Cardinality.Regions
import VE.Cardinality.Ratio
import VE.Order.Consequence

/-! Erasure of a `cardinality@0` problem into W6a (docs/spec/quantities.md 3.5, 3.9).

Each count becomes a sum of region constants, each proportion its linear form over a nonempty population, and each
ratio statement its linear form over a positive denominator in its operands' tag (`roundingQ`); a count operand
becomes its dimensionless region sum. A
recognised universal statement over a counted sort stays as written; erasure adds a bridge premise saying it holds
exactly when the regions outside its body sum to 0. Every region constant gets the premise `0 ≤ n`. The erased problem
goes to W6a's existing certificate route. A finite countermodel is a model of the original vocabulary: Lean computes
each region's size from it (`withRegionsFinite`) and runs the frozen countermodel check. -/
namespace VE.Cardinality
open VE.Time (QTerm QFormula TStructure)
universe u

def sumTerms : List QTerm → QTerm
  | [] => .num dl 0
  | [t] => t
  | t :: ts => .add dl t (sumTerms ts)

/-- The sum of the region constants of sort `s` inside `b`, the predicates on each sort read from `P`. -/
def regionSumBy (P : String → List String) (s : String) (b : Body) : QTerm :=
  let ps := P s
  sumTerms (((regions ps.length).filter (fun r => b.inRegion ps r)).map
    (fun r => QTerm.const dl (regionConst s r)))

abbrev regionSum (E : CEnv) (fs : List CFormula) (s : String) (b : Body) : QTerm := regionSumBy (predsOn E fs) s b

/-! The erasure reads the predicates on each sort from `P`: `predsOn E fs` in the statements (`CFormula.erase`), and
the region structure computed once per problem in the runner (`RegionData.predsOn`, `regionData_predsOn`). -/

def CountAtom.eraseBy (P : String → List String) (c : CountAtom) : QFormula :=
  let lhs := sumTerms (c.terms.map (fun kb => QTerm.scale dl kb.1 (regionSumBy P c.sort kb.2)))
  let rhs : QTerm := .num dl c.bound
  match c.rel with
  | .lt => .lt lhs rhs
  | .le => .le lhs rhs
  | .eq => .eq lhs rhs

def Cmp.erase (a b : QTerm) : Cmp → QFormula
  | .gt => .lt b a
  | .ge => .le b a
  | .lt => .lt a b
  | .le => .le a b
  | .eq => .eq a b

def Proportion.eraseBy (P : String → List String) (p : Proportion) : QFormula :=
  let n := regionSumBy P p.sort p.whole
  let m := regionSumBy P p.sort (.and p.whole p.part)
  .and (.lt (.num dl 0) n) (p.cmp.erase (.scale dl p.den m) (.scale dl p.num n))

def CTerm.eraseBy (P : String → List String) : CTerm → QTerm
  | .quantity t => t
  | .count s b => regionSumBy P s b

abbrev CTerm.erase (E : CEnv) (fs : List CFormula) (t : CTerm) : QTerm := t.eraseBy (predsOn E fs)

def CFormula.eraseBy (E : CEnv) (P : String → List String) : CFormula → QFormula
  | .quantity a => a
  | .count c => c.eraseBy P
  | .proportion p => p.eraseBy P
  | .roundsTo r n d D k =>
      let g := (n.tagOf E).getD dl
      .and (.lt (.num g 0) (d.eraseBy P)) (roundingQ g r (n.eraseBy P) (d.eraseBy P) D k)
  | .percentOf p w D k =>
      let g := (p.tagOf E).getD dl
      .and (.lt (.num g 0) (w.eraseBy P))
        (.eq (.scale g (100 * 10 ^ k) (p.eraseBy P)) (.scale g D (w.eraseBy P)))
  | .percentRoundsTo r p w D k =>
      let g := (p.tagOf E).getD dl
      .and (.lt (.num g 0) (w.eraseBy P)) (roundingQ g r (.scale g 100 (p.eraseBy P)) (w.eraseBy P) D k)
  | .not a => .not (a.eraseBy E P)
  | .and a b => .and (a.eraseBy E P) (b.eraseBy E P)
  | .or a b => .or (a.eraseBy E P) (b.eraseBy E P)
  | .implies a b => .implies (a.eraseBy E P) (b.eraseBy E P)

abbrev CFormula.erase (E : CEnv) (fs : List CFormula) (a : CFormula) : QFormula := a.eraseBy E (predsOn E fs)

/-- One premise `0 ≤ n` per region constant of `table`. -/
def nonnegOf (table : List (String × String × Region)) : List QFormula :=
  table.map fun e => .le (.num dl 0) (.const dl e.1)

/-- One premise `0 ≤ n` per region constant. -/
def nonnegPremises (E : CEnv) (fs : List CFormula) : List QFormula := nonnegOf (regionTable E fs)

/-- A counted universal statement's bridge: it holds exactly when the regions outside its body sum to 0. -/
def bridgeBy (P : String → List String) (x : String × Body × QFormula) : QFormula :=
  let z : QFormula := .eq (regionSumBy P x.1 (.not x.2.1)) (.num dl 0)
  .and (.implies x.2.2 z) (.implies z x.2.2)

abbrev bridge (E : CEnv) (fs : List CFormula) (x : String × Body × QFormula) : QFormula := bridgeBy (predsOn E fs) x

/-- One premise per counted universal statement. -/
def bridgePremises (E : CEnv) (fs : List CFormula) : List QFormula := (countedUniversals E fs).map (bridge E fs)

/-- The problem handed to W6a: region premises, bridges and the erased premises; the erased conclusion. -/
def erasedProblem (E : CEnv) (ps : List CFormula) (c : CFormula) : List QFormula × QFormula :=
  let fs := c :: ps
  (nonnegPremises E fs ++ bridgePremises E fs ++ ps.map (CFormula.erase E fs), c.erase E fs)

open Classical in
noncomputable def regionSize {α : Type u} (T : TStructure α) (s : String) (b : Body) : Nat :=
  if h : ∃ n, HasCount T s b n then Classical.choose h else 0

/-- The structure that reads every region constant as the number of objects in its region. -/
noncomputable def withRegions {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α) :
    TStructure α :=
  { T with constant := fun c => match (regionTable E fs).find? (·.1 == c) with
      | some (_, s, r) => some (.qty dl (regionSize T s (regionBody (predsOn E fs s) r)))
      | none => T.constant c }

/-! ## Finite countermodels -/

def Body.evalFin {α : Type} [DecidableEq α] (M : VE.Order.FiniteModel α) (x : α) : Body → Bool
  | .atom p => (M.relations p).any (fun t => decide (t = [Sum.inl x]))
  | .any => true
  | .not b => !(b.evalFin M x)
  | .and a b => a.evalFin M x && b.evalFin M x
  | .or a b => a.evalFin M x || b.evalFin M x

/-- The number of distinct listed objects of `s` with `b`. -/
def countFin {α : Type} [DecidableEq α] (M : VE.Order.FiniteModel α) (s : String) (b : Body) : Nat :=
  ((firstUse (M.domains s)).filter (fun x => b.evalFin M x)).length

/-- A finite model extended with each region constant's size. -/
def withRegionsFinite {α : Type} [DecidableEq α] (E : CEnv) (fs : List CFormula)
    (M : VE.Order.FiniteModel α) : VE.Order.FiniteModel α :=
  { M with constants := fun c => match (regionTable E fs).find? (·.1 == c) with
      | some (_, s, r) => some (.inr (countFin M s (regionBody (predsOn E fs s) r)))
      | none => M.constants c }

/-- W6a's existing countermodel check on the erased problem over `withRegionsFinite`. -/
def refutesC {α : Type} [DecidableEq α] (E : CEnv) (ps : List CFormula) (c : CFormula)
    (M : VE.Order.FiniteModel α) : Bool :=
  VE.Order.countermodelCheck (withRegionsFinite E (c :: ps) M)
    ((erasedProblem E ps c).1.map QFormula.erase) (erasedProblem E ps c).2.erase

end VE.Cardinality
