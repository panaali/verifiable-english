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

def regionSum (E : CEnv) (fs : List CFormula) (s : String) (b : Body) : QTerm :=
  let ps := predsOn E fs s
  sumTerms (((regions ps.length).filter (fun r => b.inRegion ps r)).map
    (fun r => QTerm.const dl (regionConst s r)))

def CountAtom.erase (E : CEnv) (fs : List CFormula) (c : CountAtom) : QFormula :=
  let lhs := sumTerms (c.terms.map (fun kb => QTerm.scale dl kb.1 (regionSum E fs c.sort kb.2)))
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

def Proportion.erase (E : CEnv) (fs : List CFormula) (p : Proportion) : QFormula :=
  let n := regionSum E fs p.sort p.whole
  let m := regionSum E fs p.sort (.and p.whole p.part)
  .and (.lt (.num dl 0) n) (p.cmp.erase (.scale dl p.den m) (.scale dl p.num n))

def CTerm.erase (E : CEnv) (fs : List CFormula) : CTerm → QTerm
  | .quantity t => t
  | .count s b => regionSum E fs s b

def CFormula.erase (E : CEnv) (fs : List CFormula) : CFormula → QFormula
  | .quantity a => a
  | .count c => c.erase E fs
  | .proportion p => p.erase E fs
  | .roundsTo r n d D k =>
      let g := (n.tagOf E).getD dl
      .and (.lt (.num g 0) (d.erase E fs)) (roundingQ g r (n.erase E fs) (d.erase E fs) D k)
  | .percentOf p w D k =>
      let g := (p.tagOf E).getD dl
      .and (.lt (.num g 0) (w.erase E fs))
        (.eq (.scale g (100 * 10 ^ k) (p.erase E fs)) (.scale g D (w.erase E fs)))
  | .percentRoundsTo r p w D k =>
      let g := (p.tagOf E).getD dl
      .and (.lt (.num g 0) (w.erase E fs)) (roundingQ g r (.scale g 100 (p.erase E fs)) (w.erase E fs) D k)
  | .not a => .not (a.erase E fs)
  | .and a b => .and (a.erase E fs) (b.erase E fs)
  | .or a b => .or (a.erase E fs) (b.erase E fs)
  | .implies a b => .implies (a.erase E fs) (b.erase E fs)

/-- One premise `0 ≤ n` per region constant. -/
def nonnegPremises (E : CEnv) (fs : List CFormula) : List QFormula :=
  (regionTable E fs).map fun e => .le (.num dl 0) (.const dl e.1)

/-- One premise per counted universal statement: it holds exactly when the regions outside its body sum to 0. -/
def bridgePremises (E : CEnv) (fs : List CFormula) : List QFormula :=
  (countedUniversals E fs).map fun x =>
    let z : QFormula := .eq (regionSum E fs x.1 (.not x.2.1)) (.num dl 0)
    .and (.implies x.2.2 z) (.implies z x.2.2)

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
