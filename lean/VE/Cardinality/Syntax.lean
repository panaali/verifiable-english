import VE.Time.Semantics
import VE.Numbers.Round

/-! `cardinality@0` statements (docs/spec/quantities.md 3.2, 3.4): counts and proportions over sorts the document
declares finite, beside W6a statements, and their admission.

`Admitted` is the independent specification of admission and `CFormula.admits` its executable form
(`admits_sound`, `admits_complete`). A rounding names a `VE.Numbers` tie rule; its meaning is `VE.Numbers.RoundsTo`. -/
namespace VE.Cardinality
open VE.Time (QEnv QTerm QFormula)

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

/-- A ratio operand: a W6a quantity term, or the number of objects of a counted sort with a body (dimensionless). -/
inductive CTerm where
  | quantity (t : QTerm)
  | count (sort : String) (body : Body)
  deriving DecidableEq, Repr

/-- W6a statements, count atoms, proportions, the ratio statements with their tie rules and the connectives.
`digits` and `places` keep the printed number as written: "0.296" is `(296, 3)` and "0.30" is `(30, 2)`. -/
inductive CFormula where
  | quantity (a : QFormula)
  | count (c : CountAtom)
  | proportion (p : Proportion)
  | roundsTo (r : VE.Numbers.Rounding) (num den : CTerm) (digits : Int) (places : Nat)
  | percentOf (part whole : CTerm) (digits : Int) (places : Nat)                                -- exactly
  | percentRoundsTo (r : VE.Numbers.Rounding) (part whole : CTerm) (digits : Int) (places : Nat)  -- to the nearest
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

/-- The tie rules QT-A2 admits (decision d). -/
def admittedRules : List VE.Numbers.Rounding := [.tiesUp, .halfEven]

/-- A ratio operand's tag: a quantity's W6a tag, or `dimensionless` for a count over a declared finite sort with a
typed body. -/
inductive CTermTyped (E : CEnv) : CTerm → String → Prop
  | quantity {t g} : VE.Time.HasType E.q [] t (.qty g) → CTermTyped E (.quantity t) g
  | count {s b} : s ∈ E.finite → BodyTyped E s b → CTermTyped E (.count s b) VE.Time.dimensionless

/-- Independent admission: counts and proportions name a declared finite sort with typed bodies; a proportion's
fraction is between 0 and 1 with a positive denominator; ratio operands share one tag that is not `day`, and a rounding
names an admitted rule; W6a parts are W6a-admitted. (Freshness of region constants is `CEnv.WellFormed`.) -/
inductive Admitted (E : CEnv) : CFormula → Prop
  | quantity {a} : VE.Time.Admitted E.q [] a → Admitted E (.quantity a)
  | count {c} : c.sort ∈ E.finite → (∀ kb ∈ c.terms, BodyTyped E c.sort kb.2) → Admitted E (.count c)
  | proportion {p} : p.sort ∈ E.finite → BodyTyped E p.sort p.whole → BodyTyped E p.sort p.part →
      0 < p.den → p.num ≤ p.den → Admitted E (.proportion p)
  | roundsTo {r n d D k g} : r ∈ admittedRules → g ≠ VE.Time.dayTag → CTermTyped E n g →
      CTermTyped E d g → Admitted E (.roundsTo r n d D k)
  | percentOf {p w D k g} : g ≠ VE.Time.dayTag → CTermTyped E p g → CTermTyped E w g →
      Admitted E (.percentOf p w D k)
  | percentRoundsTo {r p w D k g} : r ∈ admittedRules → g ≠ VE.Time.dayTag → CTermTyped E p g →
      CTermTyped E w g → Admitted E (.percentRoundsTo r p w D k)
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

def CTerm.tagOf (E : CEnv) : CTerm → Option String
  | .quantity t => match t.typeOf E.q [] with
    | some (.qty g) => some g
    | _ => none
  | .count s b => if E.finite.contains s && bodyCheck E s b then some VE.Time.dimensionless else none

def ratioTyped (E : CEnv) (x y : CTerm) : Bool :=
  match x.tagOf E, y.tagOf E with
  | some g, some h => g == h && g != VE.Time.dayTag
  | _, _ => false

def CFormula.admits (E : CEnv) : CFormula → Bool
  | .quantity a => a.admits E.q []
  | .count c => E.finite.contains c.sort && c.terms.all (fun kb => bodyCheck E c.sort kb.2)
  | .proportion p => E.finite.contains p.sort && bodyCheck E p.sort p.whole &&
      bodyCheck E p.sort p.part && decide (0 < p.den) && decide (p.num ≤ p.den)
  | .roundsTo r n d _ _ => admittedRules.contains r && ratioTyped E n d
  | .percentOf p w _ _ => ratioTyped E p w
  | .percentRoundsTo r p w _ _ => admittedRules.contains r && ratioTyped E p w
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

theorem tagOf_iff (E : CEnv) (x : CTerm) (g : String) : x.tagOf E = some g ↔ CTermTyped E x g := by
  cases x with
  | quantity t =>
    constructor
    · intro h
      simp only [CTerm.tagOf] at h
      split at h
      · rename_i g' hg; cases h; exact .quantity ((VE.Time.typeOf_iff _ _ _ _).mp hg)
      · cases h
    · intro h; cases h with | quantity h => simp [CTerm.tagOf, (VE.Time.typeOf_iff _ _ _ _).mpr h]
  | count s b =>
    simp only [CTerm.tagOf, Bool.and_eq_true, List.contains_iff_mem, bodyCheck_iff]
    constructor
    · intro h; split at h
      · rename_i hs; cases h
        simp only [Bool.and_eq_true, List.contains_iff_mem, bodyCheck_iff] at hs; exact .count hs.1 hs.2
      · cases h
    · intro h; cases h with | count hs hb => simp [hs, (bodyCheck_iff E s b).mpr hb]

theorem ratioTyped_iff (E : CEnv) (x y : CTerm) :
    ratioTyped E x y = true ↔ ∃ g, g ≠ VE.Time.dayTag ∧ CTermTyped E x g ∧ CTermTyped E y g := by
  simp only [ratioTyped, ← tagOf_iff]
  cases x.tagOf E <;> cases y.tagOf E <;> simp
  exact ⟨fun ⟨h, h'⟩ => ⟨h ▸ h', h⟩, fun ⟨h', h⟩ => ⟨h, h ▸ h'⟩⟩

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
  | roundsTo r n d D k =>
    simp only [CFormula.admits, Bool.and_eq_true, List.contains_iff_mem, ratioTyped_iff]
    exact ⟨fun ⟨hr, g, hg, hn, hd⟩ => .roundsTo hr hg hn hd, fun h => by cases h with
      | roundsTo hr hg hn hd => exact ⟨hr, _, hg, hn, hd⟩⟩
  | percentRoundsTo r n d D k =>
    simp only [CFormula.admits, Bool.and_eq_true, List.contains_iff_mem, ratioTyped_iff]
    exact ⟨fun ⟨hr, g, hg, hn, hd⟩ => .percentRoundsTo hr hg hn hd, fun h => by cases h with
      | percentRoundsTo hr hg hn hd => exact ⟨hr, _, hg, hn, hd⟩⟩
  | percentOf p w D k =>
    simp only [CFormula.admits, ratioTyped_iff]
    exact ⟨fun ⟨g, hg, hp, hw⟩ => .percentOf hg hp hw, fun h => by cases h with
      | percentOf hg hp hw => exact ⟨_, hg, hp, hw⟩⟩
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
