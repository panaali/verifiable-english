import VE.Time.Semantics

/-! `cardinality@0` statements (docs/spec/quantities.md 3.2, 3.4): counts and proportions over sorts the document
declares finite, beside W6a statements, and their admission.

`Admitted` is the independent specification of admission and `CFormula.admits` its executable form
(`admits_sound`, `admits_complete`). The ratio constructors (`roundsTo`, `percentOf`, `percentRoundsTo`) and their
operands are QT-A2's. -/
namespace VE.Cardinality
open VE.Time (QEnv QFormula)

/-- A property of one counted object: unary predicates of its sort with `not`, `and`, `or`; `any` is every object. -/
inductive Body where
  | atom (predicate : String)
  | any
  | not (body : Body)
  | and (left right : Body)
  | or (left right : Body)
  deriving DecidableEq, Repr

inductive Rel where
  | lt | le | eq
  deriving DecidableEq, Repr

/-- `Σ kᵢ · #{x of sort | bodyᵢ x}  rel  bound`. -/
structure CountAtom where
  sort : String
  terms : List (Int × Body)
  rel : Rel
  bound : Int
  deriving DecidableEq, Repr

/-- How a proportion compares with a literal fraction: the share is more than, at least, … the fraction. -/
inductive Cmp where
  | gt | ge | lt | le | eq
  deriving DecidableEq, Repr

/-- "`cmp` `num` in `den` of the objects of `sort` with `whole` have `part`". -/
structure Proportion where
  sort : String
  whole : Body
  part : Body
  cmp : Cmp
  num : Nat
  den : Nat
  deriving DecidableEq, Repr

/-- W6a statements, count atoms, proportions and the connectives. -/
inductive CFormula where
  | quantity (a : QFormula)
  | count (c : CountAtom)
  | proportion (p : Proportion)
  | not (a : CFormula)
  | and (a b : CFormula)
  | or (a b : CFormula)
  | implies (a b : CFormula)
  deriving DecidableEq, Repr

/-- W6a's environment and the sorts the document declares finite. -/
structure CEnv where
  q : QEnv
  finite : List String

def regionPrefix : String := "cardinality__"

/-- What the environment decoder establishes (spec 4.2, E5–E8): finite sorts are declared, and no declared constant
begins with the region prefix, so region constants are fresh. -/
structure CEnv.WellFormed (E : CEnv) : Prop where
  finiteDeclared : ∀ s ∈ E.finite, s ∈ E.q.sorts
  fresh : ∀ c τ, E.q.constants c = some τ → c.startsWith regionPrefix = false

/-! ## Admission -/

/-- Every atom of a body is a declared unary predicate of `s`. -/
def BodyTyped (E : CEnv) (s : String) : Body → Prop
  | .atom p => E.q.predicates p = some [.obj s]
  | .any => True
  | .not b => BodyTyped E s b
  | .and a b => BodyTyped E s a ∧ BodyTyped E s b
  | .or a b => BodyTyped E s a ∧ BodyTyped E s b

/-- Independent admission: counts and proportions name a declared finite sort with typed bodies; a proportion's
fraction is between 0 and 1 with a positive denominator; W6a parts are W6a-admitted. (Freshness of region constants
is `CEnv.WellFormed`.) -/
inductive Admitted (E : CEnv) : CFormula → Prop
  | quantity {a} : VE.Time.Admitted E.q [] a → Admitted E (.quantity a)
  | count {c} : c.sort ∈ E.finite → (∀ kb ∈ c.terms, BodyTyped E c.sort kb.2) → Admitted E (.count c)
  | proportion {p} : p.sort ∈ E.finite → BodyTyped E p.sort p.whole → BodyTyped E p.sort p.part →
      0 < p.den → p.num ≤ p.den → Admitted E (.proportion p)
  | not {a} : Admitted E a → Admitted E (.not a)
  | and {a b} : Admitted E a → Admitted E b → Admitted E (.and a b)
  | or {a b} : Admitted E a → Admitted E b → Admitted E (.or a b)
  | implies {a b} : Admitted E a → Admitted E b → Admitted E (.implies a b)

def bodyCheck (E : CEnv) (s : String) : Body → Bool
  | .atom p => E.q.predicates p == some [.obj s]
  | .any => true
  | .not b => bodyCheck E s b
  | .and a b => bodyCheck E s a && bodyCheck E s b
  | .or a b => bodyCheck E s a && bodyCheck E s b

def CFormula.admits (E : CEnv) : CFormula → Bool
  | .quantity a => a.admits E.q []
  | .count c => E.finite.contains c.sort && c.terms.all (fun kb => bodyCheck E c.sort kb.2)
  | .proportion p => E.finite.contains p.sort && bodyCheck E p.sort p.whole &&
      bodyCheck E p.sort p.part && decide (0 < p.den) && decide (p.num ≤ p.den)
  | .not a => a.admits E
  | .and a b => a.admits E && b.admits E
  | .or a b => a.admits E && b.admits E
  | .implies a b => a.admits E && b.admits E

theorem bodyCheck_iff (E : CEnv) (s : String) (b : Body) : bodyCheck E s b = true ↔ BodyTyped E s b := by
  induction b with
  | atom p => simp [bodyCheck, BodyTyped]
  | any => simp [bodyCheck, BodyTyped]
  | not b ih => simpa [bodyCheck, BodyTyped] using ih
  | and a b ia ib | or a b ia ib => simp [bodyCheck, BodyTyped, ia, ib]

theorem admits_iff (E : CEnv) (a : CFormula) : a.admits E = true ↔ Admitted E a := by
  induction a with
  | quantity a =>
    simp only [CFormula.admits]
    constructor
    · intro h; exact .quantity (VE.Time.units_admit_sound _ _ _ h)
    · intro h; cases h with | quantity h => exact VE.Time.units_admit_complete _ _ _ h
  | count c =>
    simp only [CFormula.admits, Bool.and_eq_true, List.contains_iff_mem, List.all_eq_true, bodyCheck_iff]
    exact ⟨fun h => .count h.1 h.2, fun h => by cases h with | count hs hb => exact ⟨hs, hb⟩⟩
  | proportion p =>
    simp only [CFormula.admits, Bool.and_eq_true, List.contains_iff_mem, bodyCheck_iff, decide_eq_true_eq]
    exact ⟨fun h => .proportion h.1.1.1.1 h.1.1.1.2 h.1.1.2 h.1.2 h.2,
      fun h => by cases h with | proportion hs hw hp hd hn => exact ⟨⟨⟨⟨hs, hw⟩, hp⟩, hd⟩, hn⟩⟩
  | not a ih =>
    simp only [CFormula.admits, ih]
    exact ⟨.not, fun h => by cases h with | not h => exact h⟩
  | and a b ia ib =>
    simp only [CFormula.admits, Bool.and_eq_true, ia, ib]
    exact ⟨fun h => .and h.1 h.2, fun h => by cases h with | and x y => exact ⟨x, y⟩⟩
  | or a b ia ib =>
    simp only [CFormula.admits, Bool.and_eq_true, ia, ib]
    exact ⟨fun h => .or h.1 h.2, fun h => by cases h with | or x y => exact ⟨x, y⟩⟩
  | implies a b ia ib =>
    simp only [CFormula.admits, Bool.and_eq_true, ia, ib]
    exact ⟨fun h => .implies h.1 h.2, fun h => by cases h with | implies x y => exact ⟨x, y⟩⟩

theorem admits_sound (E : CEnv) (a : CFormula) (h : a.admits E = true) : Admitted E a :=
  (admits_iff E a).mp h

theorem admits_complete (E : CEnv) (a : CFormula) (h : Admitted E a) : a.admits E = true :=
  (admits_iff E a).mpr h

end VE.Cardinality
