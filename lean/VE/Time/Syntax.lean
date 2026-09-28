import VE.Order.Typing
import VE.Time.Calendar

/-! W6a annotated statements (units-schema §3.1) and their admission and erasure.

A statement type is either a user sort or a unit tag. The two are separate
constructors, so a sort spelled like a tag is never a quantity type. Every
integer term carries its tag; the seven quantifier-free date operations are
canonical constructors whose integer meaning Lean generates itself.

`QFormula.admits` is the executable admission; `Admitted` is its independent
specification (`units_admit_sound`, `units_admit_complete`). `QFormula.erase`
regenerates the frozen order@0 formula, which is well typed in the erased
environment (`erase_wellTyped`). -/
namespace VE.Time
open VE.Order (SortName Term Formula)

def dimensionless : String := "dimensionless"
def dayTag : String := "day"
def elapsedTag : String := "elapsed_day"

inductive QType where
  | obj (sort : String)
  | qty (tag : String)
  deriving DecidableEq, Repr

def QType.erase : QType → SortName
  | .obj s => .user s
  | .qty _ => .int

/-- An admitted W6 environment: user sorts, declared unit tags, and the tagged
signatures of predicates and constants. -/
structure QEnv where
  sorts : List String
  tags : List String
  predicates : String → Option (List QType)
  constants : String → Option QType

def QEnv.ValidTag (E : QEnv) (t : String) : Prop := t = dimensionless ∨ t ∈ E.tags

def QEnv.validTag (E : QEnv) (t : String) : Bool := t == dimensionless || E.tags.contains t

theorem QEnv.validTag_iff (E : QEnv) (t : String) : E.validTag t = true ↔ E.ValidTag t := by
  simp [QEnv.validTag, QEnv.ValidTag]

/-- The erased core environment: symbols and sorts unchanged, tags forgotten. -/
def QEnv.erase (E : QEnv) : VE.Order.Environment :=
  ⟨E.sorts, fun p => (E.predicates p).map (List.map QType.erase),
    fun c => (E.constants c).map QType.erase⟩

inductive QTerm where
  | var (index : Nat)
  | obj (name : String)
  | num (tag : String) (value : Int)
  | const (tag : String) (name : String)
  | add (tag : String) (left right : QTerm)
  | scale (tag : String) (coefficient : Int) (term : QTerm)
  deriving DecidableEq, Repr

inductive QFormula where
  | top
  | bottom
  | unary (predicate : String) (term : QTerm)
  | binary (predicate : String) (left right : QTerm)
  | eq (left right : QTerm)
  | lt (left right : QTerm)
  | le (left right : QTerm)
  | not (body : QFormula)
  | and (left right : QFormula)
  | or (left right : QFormula)
  | implies (left right : QFormula)
  | all (sort : String) (body : QFormula)
  | ex (sort : String) (body : QFormula)
  | dateOn (t d : QTerm)
  | dateBefore (t d : QTerm)
  | dateAfter (t d : QTerm)
  | dateNoLater (t d : QTerm)
  | within (t d : QTerm) (n : Nat)
  | shift (t d : QTerm) (n : Nat)
  | elapsed (d t v : QTerm)
  deriving DecidableEq, Repr

/-! ## Specification of admission -/

/-- Independent typing of annotated terms. Every quantity rule requires a
declared tag; addition and scaling are homogeneous and never apply to dates. -/
inductive HasType (E : QEnv) (Γ : List String) : QTerm → QType → Prop
  | var {i s} : Γ[i]? = some s → HasType E Γ (.var i) (.obj s)
  | obj {c s} : E.constants c = some (.obj s) → HasType E Γ (.obj c) (.obj s)
  | num {t z} : E.ValidTag t → HasType E Γ (.num t z) (.qty t)
  | const {t c} : E.ValidTag t → E.constants c = some (.qty t) → HasType E Γ (.const t c) (.qty t)
  | add {t l r} : t ≠ dayTag → E.ValidTag t → HasType E Γ l (.qty t) → HasType E Γ r (.qty t) →
      HasType E Γ (.add t l r) (.qty t)
  | scale {t k u} : t ≠ dayTag → E.ValidTag t → HasType E Γ u (.qty t) →
      HasType E Γ (.scale t k u) (.qty t)

/-- Independent admission of annotated formulas: every signature slot, comparison
and time operation has the declared compatible tag. -/
inductive Admitted (E : QEnv) : List String → QFormula → Prop
  | top {Γ} : Admitted E Γ .top
  | bottom {Γ} : Admitted E Γ .bottom
  | unary {Γ p t τ} : E.predicates p = some [τ] → HasType E Γ t τ → Admitted E Γ (.unary p t)
  | binary {Γ p t u τ σ} : E.predicates p = some [τ, σ] → HasType E Γ t τ → HasType E Γ u σ →
      Admitted E Γ (.binary p t u)
  | eq {Γ t u τ} : HasType E Γ t τ → HasType E Γ u τ → Admitted E Γ (.eq t u)
  | lt {Γ t u g} : HasType E Γ t (.qty g) → HasType E Γ u (.qty g) → Admitted E Γ (.lt t u)
  | le {Γ t u g} : HasType E Γ t (.qty g) → HasType E Γ u (.qty g) → Admitted E Γ (.le t u)
  | not {Γ a} : Admitted E Γ a → Admitted E Γ (.not a)
  | and {Γ a b} : Admitted E Γ a → Admitted E Γ b → Admitted E Γ (.and a b)
  | or {Γ a b} : Admitted E Γ a → Admitted E Γ b → Admitted E Γ (.or a b)
  | implies {Γ a b} : Admitted E Γ a → Admitted E Γ b → Admitted E Γ (.implies a b)
  | all {Γ s a} : s ≠ "$int" → s ∈ E.sorts → Admitted E (s :: Γ) a → Admitted E Γ (.all s a)
  | ex {Γ s a} : s ≠ "$int" → s ∈ E.sorts → Admitted E (s :: Γ) a → Admitted E Γ (.ex s a)
  | dateOn {Γ t d} : HasType E Γ t (.qty dayTag) → HasType E Γ d (.qty dayTag) →
      Admitted E Γ (.dateOn t d)
  | dateBefore {Γ t d} : HasType E Γ t (.qty dayTag) → HasType E Γ d (.qty dayTag) →
      Admitted E Γ (.dateBefore t d)
  | dateAfter {Γ t d} : HasType E Γ t (.qty dayTag) → HasType E Γ d (.qty dayTag) →
      Admitted E Γ (.dateAfter t d)
  | dateNoLater {Γ t d} : HasType E Γ t (.qty dayTag) → HasType E Γ d (.qty dayTag) →
      Admitted E Γ (.dateNoLater t d)
  | within {Γ t d n} : HasType E Γ t (.qty dayTag) → HasType E Γ d (.qty dayTag) →
      Admitted E Γ (.within t d n)
  | shift {Γ t d n} : HasType E Γ t (.qty dayTag) → HasType E Γ d (.qty dayTag) →
      Admitted E Γ (.shift t d n)
  | elapsed {Γ d t v} : HasType E Γ d (.qty dayTag) → HasType E Γ t (.qty dayTag) →
      HasType E Γ v (.qty elapsedTag) → Admitted E Γ (.elapsed d t v)

/-! ## Executable admission -/

def QTerm.typeOf (E : QEnv) (Γ : List String) : QTerm → Option QType
  | .var i => Γ[i]?.map .obj
  | .obj c => match E.constants c with
    | some (.obj s) => some (.obj s)
    | _ => none
  | .num t _ => if E.validTag t then some (.qty t) else none
  | .const t c => if E.validTag t && E.constants c == some (.qty t) then some (.qty t) else none
  | .add t l r =>
    if t != dayTag && E.validTag t && l.typeOf E Γ == some (.qty t) && r.typeOf E Γ == some (.qty t)
    then some (.qty t) else none
  | .scale t _ u =>
    if t != dayTag && E.validTag t && u.typeOf E Γ == some (.qty t) then some (.qty t) else none

def QTerm.isDay (E : QEnv) (Γ : List String) (t : QTerm) : Bool := t.typeOf E Γ == some (.qty dayTag)

def QFormula.admits (E : QEnv) (Γ : List String) : QFormula → Bool
  | .top | .bottom => true
  | .unary p t => match E.predicates p, t.typeOf E Γ with
    | some [s], some r => s == r
    | _, _ => false
  | .binary p t u => match E.predicates p, t.typeOf E Γ, u.typeOf E Γ with
    | some [s, r], some s', some r' => s == s' && r == r'
    | _, _, _ => false
  | .eq t u => match t.typeOf E Γ, u.typeOf E Γ with
    | some s, some r => s == r
    | _, _ => false
  | .lt t u | .le t u => match t.typeOf E Γ, u.typeOf E Γ with
    | some (.qty a), some (.qty b) => a == b
    | _, _ => false
  | .not a => a.admits E Γ
  | .and a b | .or a b | .implies a b => a.admits E Γ && b.admits E Γ
  | .all s a | .ex s a => s != "$int" && E.sorts.contains s && a.admits E (s :: Γ)
  | .dateOn t d | .dateBefore t d | .dateAfter t d | .dateNoLater t d
  | .within t d _ | .shift t d _ => t.isDay E Γ && d.isDay E Γ
  | .elapsed d t v => d.isDay E Γ && t.isDay E Γ && v.typeOf E Γ == some (.qty elapsedTag)

theorem typeOf_iff (E : QEnv) (Γ : List String) (t : QTerm) (τ : QType) :
    t.typeOf E Γ = some τ ↔ HasType E Γ t τ := by
  induction t generalizing τ with
  | var i =>
    constructor
    · intro h
      simp only [QTerm.typeOf, Option.map_eq_some_iff] at h
      obtain ⟨s, hs, rfl⟩ := h
      exact .var hs
    · rintro ⟨hs⟩
      simp [QTerm.typeOf, *]
  | obj c =>
    constructor
    · intro h
      simp only [QTerm.typeOf] at h
      split at h
      · rename_i s hc; cases h; exact .obj hc
      · cases h
    · intro h
      cases h with
      | obj hc => simp [QTerm.typeOf, hc]
  | num t z =>
    constructor
    · intro h
      simp only [QTerm.typeOf] at h
      split at h
      · rename_i hv; cases h; exact .num ((E.validTag_iff t).mp hv)
      · cases h
    · intro h
      cases h with
      | num hv => simp [QTerm.typeOf, (E.validTag_iff t).mpr hv]
  | const t c =>
    constructor
    · intro h
      simp only [QTerm.typeOf] at h
      split at h
      · rename_i hv
        cases h
        simp only [Bool.and_eq_true, beq_iff_eq] at hv
        exact .const ((E.validTag_iff t).mp hv.1) hv.2
      · cases h
    · intro h
      cases h with
      | const hv hc => simp [QTerm.typeOf, (E.validTag_iff t).mpr hv, hc]
  | add t l r il ir =>
    constructor
    · intro h
      simp only [QTerm.typeOf] at h
      split at h
      · rename_i hv
        cases h
        simp only [Bool.and_eq_true, bne_iff_ne, ne_eq, beq_iff_eq] at hv
        exact .add hv.1.1.1 ((E.validTag_iff t).mp hv.1.1.2) ((il _).mp hv.1.2) ((ir _).mp hv.2)
      · cases h
    · intro h
      cases h with
      | add hd hv hl hr =>
        simp [QTerm.typeOf, hd, (E.validTag_iff t).mpr hv, (il _).mpr hl, (ir _).mpr hr]
  | scale t k u iu =>
    constructor
    · intro h
      simp only [QTerm.typeOf] at h
      split at h
      · rename_i hv
        cases h
        simp only [Bool.and_eq_true, bne_iff_ne, ne_eq, beq_iff_eq] at hv
        exact .scale hv.1.1 ((E.validTag_iff t).mp hv.1.2) ((iu _).mp hv.2)
      · cases h
    · intro h
      cases h with
      | scale hd hv hu => simp [QTerm.typeOf, hd, (E.validTag_iff t).mpr hv, (iu _).mpr hu]

theorem isDay_iff (E : QEnv) (Γ : List String) (t : QTerm) :
    t.isDay E Γ = true ↔ HasType E Γ t (.qty dayTag) := by
  simp [QTerm.isDay, typeOf_iff]

/-- A term has at most one type. -/
theorem HasType.unique {E : QEnv} {Γ : List String} {t : QTerm} {τ σ : QType}
    (h₁ : HasType E Γ t τ) (h₂ : HasType E Γ t σ) : τ = σ := by
  rw [← typeOf_iff] at h₁ h₂
  rw [h₁] at h₂
  exact Option.some.inj h₂

/-- **`Time.units_admit_sound`**: successful executable admission implies the
independent admission relation: every occurrence, slot, comparison and time
operation has its declared compatible tag. -/
theorem units_admit_sound (E : QEnv) (Γ : List String) (a : QFormula)
    (h : a.admits E Γ = true) : Admitted E Γ a := by
  induction a generalizing Γ with
  | top => exact .top
  | bottom => exact .bottom
  | unary p t =>
    simp only [QFormula.admits] at h
    split at h
    · rename_i s r hp ht
      exact .unary (τ := s) hp ((typeOf_iff E Γ t s).mp (by rw [ht, beq_iff_eq.mp h]))
    · cases h
  | binary p t u =>
    simp only [QFormula.admits] at h
    split at h
    · rename_i s r s' r' hp ht hu
      simp only [Bool.and_eq_true, beq_iff_eq] at h
      exact .binary hp ((typeOf_iff E Γ t _).mp (by rw [ht, h.1]))
        ((typeOf_iff E Γ u _).mp (by rw [hu, h.2]))
    · cases h
  | eq t u =>
    simp only [QFormula.admits] at h
    split at h
    · rename_i s r ht hu
      exact .eq ((typeOf_iff E Γ t s).mp ht) ((typeOf_iff E Γ u s).mp (by rw [hu, beq_iff_eq.mp h]))
    · cases h
  | lt t u =>
    simp only [QFormula.admits] at h
    split at h
    · rename_i a b ht hu
      exact .lt ((typeOf_iff E Γ t _).mp ht) ((typeOf_iff E Γ u _).mp (by rw [hu, beq_iff_eq.mp h]))
    · cases h
  | le t u =>
    simp only [QFormula.admits] at h
    split at h
    · rename_i a b ht hu
      exact .le ((typeOf_iff E Γ t _).mp ht) ((typeOf_iff E Γ u _).mp (by rw [hu, beq_iff_eq.mp h]))
    · cases h
  | not a ih => exact .not (ih Γ h)
  | and a b ia ib =>
    simp only [QFormula.admits, Bool.and_eq_true] at h; exact .and (ia Γ h.1) (ib Γ h.2)
  | or a b ia ib =>
    simp only [QFormula.admits, Bool.and_eq_true] at h; exact .or (ia Γ h.1) (ib Γ h.2)
  | implies a b ia ib =>
    simp only [QFormula.admits, Bool.and_eq_true] at h; exact .implies (ia Γ h.1) (ib Γ h.2)
  | all s a ih =>
    simp only [QFormula.admits, Bool.and_eq_true, bne_iff_ne, ne_eq, List.contains_iff_mem] at h
    exact .all h.1.1 h.1.2 (ih _ h.2)
  | ex s a ih =>
    simp only [QFormula.admits, Bool.and_eq_true, bne_iff_ne, ne_eq, List.contains_iff_mem] at h
    exact .ex h.1.1 h.1.2 (ih _ h.2)
  | dateOn t d =>
    simp only [QFormula.admits, Bool.and_eq_true, isDay_iff] at h; exact .dateOn h.1 h.2
  | dateBefore t d =>
    simp only [QFormula.admits, Bool.and_eq_true, isDay_iff] at h; exact .dateBefore h.1 h.2
  | dateAfter t d =>
    simp only [QFormula.admits, Bool.and_eq_true, isDay_iff] at h; exact .dateAfter h.1 h.2
  | dateNoLater t d =>
    simp only [QFormula.admits, Bool.and_eq_true, isDay_iff] at h; exact .dateNoLater h.1 h.2
  | within t d n =>
    simp only [QFormula.admits, Bool.and_eq_true, isDay_iff] at h; exact .within h.1 h.2
  | shift t d n =>
    simp only [QFormula.admits, Bool.and_eq_true, isDay_iff] at h; exact .shift h.1 h.2
  | elapsed d t v =>
    simp only [QFormula.admits, Bool.and_eq_true, isDay_iff, beq_iff_eq, typeOf_iff] at h
    exact .elapsed h.1.1 h.1.2 h.2

/-- Admission is also complete for its specification: nothing admitted by the
relation is rejected by the executable check. -/
theorem units_admit_complete (E : QEnv) (Γ : List String) (a : QFormula)
    (h : Admitted E Γ a) : a.admits E Γ = true := by
  induction h with
  | top | bottom => rfl
  | unary hp ht => simp [QFormula.admits, hp, (typeOf_iff _ _ _ _).mpr ht]
  | binary hp ht hu =>
    simp [QFormula.admits, hp, (typeOf_iff _ _ _ _).mpr ht, (typeOf_iff _ _ _ _).mpr hu]
  | eq ht hu => simp [QFormula.admits, (typeOf_iff _ _ _ _).mpr ht, (typeOf_iff _ _ _ _).mpr hu]
  | lt ht hu => simp [QFormula.admits, (typeOf_iff _ _ _ _).mpr ht, (typeOf_iff _ _ _ _).mpr hu]
  | le ht hu => simp [QFormula.admits, (typeOf_iff _ _ _ _).mpr ht, (typeOf_iff _ _ _ _).mpr hu]
  | not _ ih => exact ih
  | and _ _ ia ib | or _ _ ia ib | implies _ _ ia ib => simp [QFormula.admits, ia, ib]
  | all hs hm _ ih | ex hs hm _ ih => simp [QFormula.admits, hs, hm, ih]
  | dateOn ht hd | dateBefore ht hd | dateAfter ht hd | dateNoLater ht hd
  | within ht hd | shift ht hd =>
    simp [QFormula.admits, (isDay_iff _ _ _).mpr ht, (isDay_iff _ _ _).mpr hd]
  | elapsed hd ht hv =>
    simp [QFormula.admits, (isDay_iff _ _ _).mpr hd, (isDay_iff _ _ _).mpr ht,
      (typeOf_iff _ _ _ _).mpr hv]

/-! ## Erasure: the regenerated core formula -/

def QTerm.erase : QTerm → Term
  | .var i => .var i
  | .obj c => .const c
  | .num _ z => .num z
  | .const _ c => .const c
  | .add _ l r => .add l.erase r.erase
  | .scale _ k u => .scale k u.erase

/-- `validDate(x) := 0 <= x and x <= dateMax`, visible formula content. -/
def guard (x : Term) : Formula := .and (.le (.num 0) x) (.le x (.num (dateMax : Int)))

def guards (a b : Term) : Formula := .and (guard a) (guard b)

/-- Erasure regenerates the temporal operations exactly as Python and Rust do. -/
def QFormula.erase : QFormula → Formula
  | .top => .top
  | .bottom => .bottom
  | .unary p t => .unary p t.erase
  | .binary p t u => .binary p t.erase u.erase
  | .eq t u => .eq t.erase u.erase
  | .lt t u => .lt t.erase u.erase
  | .le t u => .le t.erase u.erase
  | .not a => .not a.erase
  | .and a b => .and a.erase b.erase
  | .or a b => .or a.erase b.erase
  | .implies a b => .implies a.erase b.erase
  | .all s a => .all s a.erase
  | .ex s a => .ex s a.erase
  | .dateOn t d => .and (guards t.erase d.erase) (.eq t.erase d.erase)
  | .dateBefore t d => .and (guards t.erase d.erase) (.lt t.erase d.erase)
  | .dateAfter t d => .and (guards t.erase d.erase) (.lt d.erase t.erase)
  | .dateNoLater t d => .and (guards t.erase d.erase) (.le t.erase d.erase)
  | .within t d n => .and (guards t.erase d.erase)
      (.and (.le d.erase t.erase) (.le t.erase (.add d.erase (.num n))))
  | .shift t d n => .and (guards t.erase d.erase) (.eq t.erase (.add d.erase (.num n)))
  | .elapsed d t v => .and (guards d.erase t.erase)
      (.eq v.erase (.add t.erase (.scale (-1) d.erase)))

theorem erase_sortOf {E : QEnv} {Γ : List String} {t : QTerm} {τ : QType}
    (h : HasType E Γ t τ) : t.erase.sortOf E.erase (Γ.map .user) = some τ.erase := by
  induction h with
  | var hs => simp [QTerm.erase, Term.sortOf, hs, QType.erase]
  | obj hc => simp [QTerm.erase, Term.sortOf, QEnv.erase, hc, QType.erase]
  | num _ => rfl
  | const _ hc => simp [QTerm.erase, Term.sortOf, QEnv.erase, hc, QType.erase]
  | add _ _ _ _ il ir => simp [QTerm.erase, Term.sortOf, il, ir, QType.erase]
  | scale _ _ _ iu => simp [QTerm.erase, Term.sortOf, iu, QType.erase]

theorem guard_wellFormed {E : VE.Order.Environment} {Γ : List SortName} {x : Term}
    (h : x.sortOf E Γ = some .int) : (guard x).WellFormed E Γ :=
  ⟨⟨rfl, h⟩, ⟨h, rfl⟩⟩

/-- **`Time.erase_wellTyped`**: erasing an admitted statement yields a well-typed
formula of the erased core environment. -/
theorem erase_wellTyped {E : QEnv} {Γ : List String} {a : QFormula} (h : Admitted E Γ a) :
    a.erase.WellFormed E.erase (Γ.map .user) := by
  induction h with
  | top | bottom => trivial
  | unary hp ht =>
    exact ⟨_, by simp [QEnv.erase, hp], erase_sortOf ht⟩
  | binary hp ht hu =>
    exact ⟨_, _, by simp [QEnv.erase, hp], erase_sortOf ht, erase_sortOf hu⟩
  | eq ht hu => exact ⟨_, erase_sortOf ht, erase_sortOf hu⟩
  | lt ht hu | le ht hu => exact ⟨erase_sortOf ht, erase_sortOf hu⟩
  | not _ ih => exact ih
  | and _ _ ia ib | or _ _ ia ib | implies _ _ ia ib => exact ⟨ia, ib⟩
  | all hs hm _ ih | ex hs hm _ ih => exact ⟨hs, hm, ih⟩
  | dateOn ht hd | dateBefore ht hd | dateNoLater ht hd =>
    exact ⟨⟨guard_wellFormed (erase_sortOf ht), guard_wellFormed (erase_sortOf hd)⟩,
      by first | exact ⟨_, erase_sortOf ht, erase_sortOf hd⟩ | exact ⟨erase_sortOf ht, erase_sortOf hd⟩⟩
  | dateAfter ht hd =>
    exact ⟨⟨guard_wellFormed (erase_sortOf ht), guard_wellFormed (erase_sortOf hd)⟩,
      erase_sortOf hd, erase_sortOf ht⟩
  | within ht hd =>
    have t' := erase_sortOf ht
    have d' := erase_sortOf hd
    exact ⟨⟨guard_wellFormed t', guard_wellFormed d'⟩, ⟨d', t'⟩, t',
      by simp [Term.sortOf, d', QType.erase]⟩
  | shift ht hd =>
    have t' := erase_sortOf ht
    have d' := erase_sortOf hd
    exact ⟨⟨guard_wellFormed t', guard_wellFormed d'⟩, _, t',
      by simp [Term.sortOf, d', QType.erase]⟩
  | elapsed hd ht hv =>
    have t' := erase_sortOf ht
    have d' := erase_sortOf hd
    exact ⟨⟨guard_wellFormed d', guard_wellFormed t'⟩, _, erase_sortOf hv,
      by simp [Term.sortOf, d', t', QType.erase]⟩

/-- The executable form: admitted statements pass the frozen order checker. -/
theorem erase_check {E : QEnv} {a : QFormula} (h : a.admits E [] = true) :
    a.erase.check E.erase [] = true :=
  (VE.Order.check_iff_wellFormed _ _ _).mpr (erase_wellTyped (units_admit_sound E [] a h))

end VE.Time
