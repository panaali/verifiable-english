import VE.Order.Consequence
import VE.Time.Syntax

/-! Direct tagged semantics of W6a statements and their faithfulness to erasure.

A tagged structure interprets integer constants as coordinates *with* their
tag, and date operations by their calendar meaning over civil dates (§6.2),
not by integer arithmetic. `units_faithful` proves that an admitted statement
holds in a tagged structure exactly when its regenerated core formula holds in
the structure with tags forgotten; `temporal_iff` is the calendar half.
`lift` gives every admissible core structure its tagged interpretation, which is
unique on declared symbols (`lift_unique`). -/
namespace VE.Time
universe u v
open VE.Order (Structure Value Term Formula Compare)

inductive TValue (α : Type u) where
  | obj (a : α)
  | qty (tag : String) (z : Int)
  deriving DecidableEq

def TValue.forget {α : Type u} : TValue α → Value α
  | .obj a => .inl a
  | .qty _ z => .inr z

/-- A tagged structure over carrier `α`. -/
structure TStructure (α : Type u) where
  objects : String → α → Prop
  constant : String → Option (TValue α)
  relation : String → List (TValue α) → Prop

/-- A tagged value of the given statement type. -/
def TValue.Typed {α : Type u} (objects : String → α → Prop) : QType → TValue α → Prop
  | .obj s, .obj a => objects s a
  | .qty g, .qty g' _ => g' = g
  | _, _ => False

def TTuple {α : Type u} (objects : String → α → Prop) : List QType → List (TValue α) → Prop
  | [], [] => True
  | τ :: τs, v :: vs => v.Typed objects τ ∧ TTuple objects τs vs
  | _, _ => False

def TStructure.Admissible {α : Type u} (T : TStructure α) (E : QEnv) : Prop :=
  (∀ c τ, E.constants c = some τ → ∃ v, T.constant c = some v ∧ v.Typed T.objects τ) ∧
  (∀ p vs, T.relation p vs → ∃ τs, E.predicates p = some τs ∧ TTuple T.objects τs vs)

/-- The units-only restriction map: the same carrier and objects, tags forgotten. -/
def TStructure.lower {α : Type u} (T : TStructure α) : Structure.{u} where
  Carrier := α
  objects := T.objects
  constant c := (T.constant c).map TValue.forget
  relation p ws := ∃ vs, T.relation p vs ∧ vs.map TValue.forget = ws

/-! ## Calendar meanings of the date operations -/

/-- `x` is the coordinate of the accepted civil date `D`. -/
def Coord (x : Int) (D : Civil) : Prop := D.Valid ∧ (D.num : Int) = x

def CalOn (t d : Int) : Prop := ∃ T D, Coord t T ∧ Coord d D ∧ T = D
def CalBefore (t d : Int) : Prop := ∃ T D, Coord t T ∧ Coord d D ∧ T.Before D
def CalAfter (t d : Int) : Prop := ∃ T D, Coord t T ∧ Coord d D ∧ D.Before T
def CalNoLater (t d : Int) : Prop := ∃ T D, Coord t T ∧ Coord d D ∧ (T.Before D ∨ T = D)
/-- `t` is the civil date `n` days after `d`. -/
def CalShift (t d : Int) (n : Nat) : Prop := ∃ T D, Coord t T ∧ Coord d D ∧ T = D.addDays n
/-- `t` is on or after `d` and on or before `n` days after `d`. -/
def CalWithin (t d : Int) (n : Nat) : Prop :=
  ∃ T D, Coord t T ∧ Coord d D ∧ ∃ k ≤ n, T = D.addDays k
/-- The signed number of civil days from `d` to `t` is `v`. -/
def CalElapsed (d t v : Int) : Prop :=
  ∃ D T, Coord d D ∧ Coord t T ∧
    (0 ≤ v ∧ T = D.addDays v.toNat ∨ v < 0 ∧ D = T.addDays (-v).toNat)

/-- The visible date guard. -/
def Guard (x : Int) : Prop := 0 ≤ x ∧ x ≤ (dateMax : Int)

theorem guard_iff_coord (x : Int) : Guard x ↔ ∃ D, Coord x D := by
  constructor
  · rintro ⟨h0, hm⟩
    obtain ⟨D, hv, hn⟩ := exists_valid_of_le (n := x.toNat) (by omega)
    exact ⟨D, hv, by rw [hn]; omega⟩
  · rintro ⟨D, hv, hn⟩
    have := (valid_iff hv.1).mp hv
    exact ⟨by omega, by omega⟩

theorem coord_unique {x : Int} {D D' : Civil} (h : Coord x D) (h' : Coord x D') : D = D' :=
  num_injective h.1.1 h'.1.1 (by have := h.2; have := h'.2; omega)

theorem guard_of_coord {x : Int} {D : Civil} (h : Coord x D) : Guard x :=
  (guard_iff_coord x).mpr ⟨D, h⟩

/-- A proper date `k` days after an accepted date is accepted when its
coordinate is in range. -/
theorem coord_addDays {d : Int} {D : Civil} (h : Coord d D) (k : Nat)
    (hk : d + k ≤ (dateMax : Int)) : Coord (d + k) (D.addDays k) := by
  have hp := addDays_proper h.1.1 k
  have hn := num_addDays h.1.1 k
  refine ⟨(valid_iff hp).mpr (by have := h.2; omega), by rw [hn]; have := h.2; omega⟩

/-! ### `Time.temporal_iff`: each guarded integer formula is its calendar meaning -/

theorem on_iff (t d : Int) : CalOn t d ↔ (Guard t ∧ Guard d) ∧ t = d := by
  constructor
  · rintro ⟨T, D, ht, hd, rfl⟩
    exact ⟨⟨guard_of_coord ht, guard_of_coord hd⟩, by have := ht.2; have := hd.2; omega⟩
  · rintro ⟨⟨gt, _⟩, rfl⟩
    obtain ⟨T, ht⟩ := (guard_iff_coord t).mp gt
    exact ⟨T, T, ht, ht, rfl⟩

theorem before_iff_lt (t d : Int) : CalBefore t d ↔ (Guard t ∧ Guard d) ∧ t < d := by
  constructor
  · rintro ⟨T, D, ht, hd, hb⟩
    have := (before_iff ht.1.1 hd.1.1).mp hb
    exact ⟨⟨guard_of_coord ht, guard_of_coord hd⟩, by have := ht.2; have := hd.2; omega⟩
  · rintro ⟨⟨gt, gd⟩, hlt⟩
    obtain ⟨T, ht⟩ := (guard_iff_coord t).mp gt
    obtain ⟨D, hd⟩ := (guard_iff_coord d).mp gd
    exact ⟨T, D, ht, hd, (before_iff ht.1.1 hd.1.1).mpr (by have := ht.2; have := hd.2; omega)⟩

theorem after_iff_lt (t d : Int) : CalAfter t d ↔ (Guard t ∧ Guard d) ∧ d < t := by
  constructor
  · rintro ⟨T, D, ht, hd, hb⟩
    have := (before_iff hd.1.1 ht.1.1).mp hb
    exact ⟨⟨guard_of_coord ht, guard_of_coord hd⟩, by have := ht.2; have := hd.2; omega⟩
  · rintro ⟨⟨gt, gd⟩, hlt⟩
    obtain ⟨T, ht⟩ := (guard_iff_coord t).mp gt
    obtain ⟨D, hd⟩ := (guard_iff_coord d).mp gd
    exact ⟨T, D, ht, hd, (before_iff hd.1.1 ht.1.1).mpr (by have := ht.2; have := hd.2; omega)⟩

theorem noLater_iff_le (t d : Int) : CalNoLater t d ↔ (Guard t ∧ Guard d) ∧ t ≤ d := by
  constructor
  · rintro ⟨T, D, ht, hd, hb | rfl⟩
    · have := (before_iff ht.1.1 hd.1.1).mp hb
      exact ⟨⟨guard_of_coord ht, guard_of_coord hd⟩, by have := ht.2; have := hd.2; omega⟩
    · exact ⟨⟨guard_of_coord ht, guard_of_coord hd⟩, by have := ht.2; have := hd.2; omega⟩
  · rintro ⟨⟨gt, gd⟩, hle⟩
    obtain ⟨T, ht⟩ := (guard_iff_coord t).mp gt
    obtain ⟨D, hd⟩ := (guard_iff_coord d).mp gd
    refine ⟨T, D, ht, hd, ?_⟩
    rcases Int.lt_or_eq_of_le hle with hlt | heq
    · exact Or.inl ((before_iff ht.1.1 hd.1.1).mpr (by have := ht.2; have := hd.2; omega))
    · subst heq; exact Or.inr (coord_unique ht hd)

theorem shift_iff (t d : Int) (n : Nat) :
    CalShift t d n ↔ (Guard t ∧ Guard d) ∧ t = d + n := by
  constructor
  · rintro ⟨T, D, ht, hd, rfl⟩
    have := num_addDays hd.1.1 n
    exact ⟨⟨guard_of_coord ht, guard_of_coord hd⟩, by have := ht.2; have := hd.2; omega⟩
  · rintro ⟨⟨gt, gd⟩, rfl⟩
    obtain ⟨D, hd⟩ := (guard_iff_coord d).mp gd
    exact ⟨D.addDays n, D, coord_addDays hd n gt.2, hd, rfl⟩

theorem within_iff (t d : Int) (n : Nat) :
    CalWithin t d n ↔ (Guard t ∧ Guard d) ∧ (d ≤ t ∧ t ≤ d + n) := by
  constructor
  · rintro ⟨T, D, ht, hd, k, hk, rfl⟩
    have := num_addDays hd.1.1 k
    exact ⟨⟨guard_of_coord ht, guard_of_coord hd⟩, by have := ht.2; have := hd.2; omega⟩
  · rintro ⟨⟨gt, gd⟩, hlo, hhi⟩
    obtain ⟨D, hd⟩ := (guard_iff_coord d).mp gd
    have hc := coord_addDays hd (t - d).toNat (by have := gt.2; omega)
    have ht : d + ((t - d).toNat : Int) = t := by omega
    rw [ht] at hc
    exact ⟨_, D, hc, hd, (t - d).toNat, by omega, rfl⟩

theorem elapsed_iff (d t v : Int) :
    CalElapsed d t v ↔ (Guard d ∧ Guard t) ∧ v = t + -1 * d := by
  constructor
  · rintro ⟨D, T, hd, ht, ⟨hv, rfl⟩ | ⟨hv, rfl⟩⟩
    · have := num_addDays hd.1.1 v.toNat
      exact ⟨⟨guard_of_coord hd, guard_of_coord ht⟩, by have := ht.2; have := hd.2; omega⟩
    · have := num_addDays ht.1.1 (-v).toNat
      exact ⟨⟨guard_of_coord hd, guard_of_coord ht⟩, by have := ht.2; have := hd.2; omega⟩
  · rintro ⟨⟨gd, gt⟩, hv⟩
    obtain ⟨D, hd⟩ := (guard_iff_coord d).mp gd
    obtain ⟨T, ht⟩ := (guard_iff_coord t).mp gt
    refine ⟨D, T, hd, ht, ?_⟩
    by_cases h0 : 0 ≤ v
    · refine Or.inl ⟨h0, coord_unique ht ?_⟩
      have hc := coord_addDays hd v.toNat (by have := gt.2; omega)
      have : d + (v.toNat : Int) = t := by omega
      rwa [this] at hc
    · refine Or.inr ⟨by omega, coord_unique hd ?_⟩
      have hc := coord_addDays ht (-v).toNat (by have := gd.2; omega)
      have : t + ((-v).toNat : Int) = d := by omega
      rwa [this] at hc

/-- A zero-day inclusive window contains exactly its origin date. -/
theorem within_zero_iff_on (t d : Int) : CalWithin t d 0 ↔ CalOn t d := by
  rw [within_iff, on_iff]
  constructor
  · rintro ⟨g, h1, h2⟩; exact ⟨g, by omega⟩
  · rintro ⟨g, rfl⟩; exact ⟨g, by omega, by omega⟩

/-! ## Direct tagged semantics -/

def QTerm.tdenote {α : Type u} (T : TStructure α) (ρ : List α) : QTerm → Option (TValue α)
  | .var i => ρ[i]?.map .obj
  | .obj c => match T.constant c with
    | some (.obj a) => some (.obj a)
    | _ => none
  | .num g z => some (.qty g z)
  | .const g c => match T.constant c with
    | some (.qty g' z) => if g' = g then some (.qty g z) else none
    | _ => none
  | .add g l r => match l.tdenote T ρ, r.tdenote T ρ with
    | some (.qty a x), some (.qty b y) => if a = g ∧ b = g then some (.qty g (x + y)) else none
    | _, _ => none
  | .scale g k t => match t.tdenote T ρ with
    | some (.qty a x) => if a = g then some (.qty g (k * x)) else none
    | _ => none

/-- Two quantities of one tag, compared by `R`. -/
def TCompare {α : Type u} (R : Int → Int → Prop) (x y : Option (TValue α)) : Prop :=
  ∃ g a b, x = some (.qty g a) ∧ y = some (.qty g b) ∧ R a b

/-- Two day coordinates satisfying the calendar relation `R`. -/
def TDates {α : Type u} (R : Int → Int → Prop) (x y : Option (TValue α)) : Prop :=
  ∃ a b, x = some (.qty dayTag a) ∧ y = some (.qty dayTag b) ∧ R a b

def QFormula.tdenote {α : Type u} (T : TStructure α) (ρ : List α) : QFormula → Prop
  | .top => True
  | .bottom => False
  | .unary p t => ∃ v, t.tdenote T ρ = some v ∧ T.relation p [v]
  | .binary p t u => ∃ v w, t.tdenote T ρ = some v ∧ u.tdenote T ρ = some w ∧
      T.relation p [v, w]
  | .eq t u => ∃ v, t.tdenote T ρ = some v ∧ u.tdenote T ρ = some v
  | .lt t u => TCompare (· < ·) (t.tdenote T ρ) (u.tdenote T ρ)
  | .le t u => TCompare (· ≤ ·) (t.tdenote T ρ) (u.tdenote T ρ)
  | .not a => ¬ a.tdenote T ρ
  | .and a b => a.tdenote T ρ ∧ b.tdenote T ρ
  | .or a b => a.tdenote T ρ ∨ b.tdenote T ρ
  | .implies a b => a.tdenote T ρ → b.tdenote T ρ
  | .all s a => ∀ x, T.objects s x → a.tdenote T (x :: ρ)
  | .ex s a => ∃ x, T.objects s x ∧ a.tdenote T (x :: ρ)
  | .dateOn t d => TDates CalOn (t.tdenote T ρ) (d.tdenote T ρ)
  | .dateBefore t d => TDates CalBefore (t.tdenote T ρ) (d.tdenote T ρ)
  | .dateAfter t d => TDates CalAfter (t.tdenote T ρ) (d.tdenote T ρ)
  | .dateNoLater t d => TDates CalNoLater (t.tdenote T ρ) (d.tdenote T ρ)
  | .within t d n => TDates (fun a b => CalWithin a b n) (t.tdenote T ρ) (d.tdenote T ρ)
  | .shift t d n => TDates (fun a b => CalShift a b n) (t.tdenote T ρ) (d.tdenote T ρ)
  | .elapsed d t v => ∃ a b w, d.tdenote T ρ = some (.qty dayTag a) ∧
      t.tdenote T ρ = some (.qty dayTag b) ∧ v.tdenote T ρ = some (.qty elapsedTag w) ∧
      CalElapsed a b w

/-! ## Faithfulness -/

/-- An object valuation for a context of user sorts. -/
def Typed {α : Type u} (T : TStructure α) (Γ : List String) (ρ : List α) : Prop :=
  ∀ (i : Nat) (s : String), Γ[i]? = some s → ∃ a, ρ[i]? = some a ∧ T.objects s a

theorem Typed.cons {α : Type u} {T : TStructure α} {Γ : List String} {ρ : List α}
    (h : Typed T Γ ρ) {s : String} {x : α} (hx : T.objects s x) : Typed T (s :: Γ) (x :: ρ) := by
  intro i s' hi
  cases i with
  | zero => simp at hi; subst hi; exact ⟨x, rfl, hx⟩
  | succ i => exact h i s' (by simpa using hi)

theorem forget_inj {α : Type u} {objects : String → α → Prop} {τ : QType} {v w : TValue α}
    (hv : v.Typed objects τ) (hw : w.Typed objects τ) (h : v.forget = w.forget) : v = w := by
  cases τ <;> cases v <;> cases w <;> simp_all [TValue.Typed, TValue.forget]

theorem typed_qty {α : Type u} {objects : String → α → Prop} {g : String} {v : TValue α}
    (h : v.Typed objects (.qty g)) : ∃ z, v = .qty g z := by
  cases v with
  | obj a => exact False.elim h
  | qty g' z => simp [TValue.Typed] at h; subst h; exact ⟨z, rfl⟩

theorem term_faithful {α : Type u} {E : QEnv} {T : TStructure α} (hT : T.Admissible E)
    {Γ : List String} {ρ : List α} (hρ : Typed T Γ ρ) {t : QTerm} {τ : QType}
    (h : HasType E Γ t τ) :
    ∃ v, t.tdenote T ρ = some v ∧ v.Typed T.objects τ ∧
      t.erase.denote T.lower (ρ.map .inl) = some v.forget := by
  induction h with
  | @var i s hs =>
    obtain ⟨a, ha, ho⟩ := hρ i s hs
    exact ⟨.obj a, by simp [QTerm.tdenote, ha], ho,
      by simp [QTerm.erase, Term.denote, TValue.forget]; exact ha⟩
  | @obj c s hc =>
    obtain ⟨v, hv, hty⟩ := hT.1 c _ hc
    cases v with
    | obj a => exact ⟨.obj a, by simp [QTerm.tdenote, hv], hty,
        by simp [QTerm.erase, Term.denote, TStructure.lower, hv, TValue.forget]⟩
    | qty g z => exact False.elim hty
  | @num g z _ => exact ⟨.qty g z, rfl, rfl, rfl⟩
  | @const g c _ hc =>
    obtain ⟨v, hv, hty⟩ := hT.1 c _ hc
    obtain ⟨z, rfl⟩ := typed_qty hty
    exact ⟨.qty g z, by simp [QTerm.tdenote, hv], rfl,
      by simp [QTerm.erase, Term.denote, TStructure.lower, hv, TValue.forget]⟩
  | @add g l r _ _ _ _ il ir =>
    obtain ⟨v, hv, hvt, hve⟩ := il
    obtain ⟨w, hw, hwt, hwe⟩ := ir
    obtain ⟨x, rfl⟩ := typed_qty hvt
    obtain ⟨y, rfl⟩ := typed_qty hwt
    exact ⟨.qty g (x + y), by simp [QTerm.tdenote, hv, hw], rfl,
      by simp [QTerm.erase, Term.denote, hve, hwe, TValue.forget]⟩
  | @scale g k u _ _ _ iu =>
    obtain ⟨v, hv, hvt, hve⟩ := iu
    obtain ⟨x, rfl⟩ := typed_qty hvt
    exact ⟨.qty g (k * x), by simp [QTerm.tdenote, hv], rfl,
      by simp [QTerm.erase, Term.denote, hve, TValue.forget]⟩

/-- A day-typed term denotes one coordinate in both semantics. -/
theorem day_faithful {α : Type u} {E : QEnv} {T : TStructure α} (hT : T.Admissible E)
    {Γ : List String} {ρ : List α} (hρ : Typed T Γ ρ) {t : QTerm} {g : String}
    (h : HasType E Γ t (.qty g)) :
    ∃ x, t.tdenote T ρ = some (.qty g x) ∧ t.erase.denote T.lower (ρ.map .inl) = some (.inr x) := by
  obtain ⟨v, hv, hvt, hve⟩ := term_faithful hT hρ h
  obtain ⟨x, rfl⟩ := typed_qty hvt
  exact ⟨x, hv, hve⟩

theorem guard_denote {S : Structure.{u}} {ρ : VE.Order.Valuation S} {t : Term} {x : Int}
    (h : t.denote S ρ = some (.inr x)) : (guard t).denote S ρ ↔ Guard x := by
  simp [guard, Guard, Formula.denote, Compare, Term.denote, h]

theorem guards_denote {S : Structure.{u}} {ρ : VE.Order.Valuation S} {t d : Term} {x y : Int}
    (ht : t.denote S ρ = some (.inr x)) (hd : d.denote S ρ = some (.inr y)) :
    (guards t d).denote S ρ ↔ Guard x ∧ Guard y := by
  simp only [guards, Formula.denote, guard_denote ht, guard_denote hd]

theorem tdates_iff {α : Type u} {R : Int → Int → Prop} {x y : Int} {a b : Option (TValue α)}
    (ha : a = some (.qty dayTag x)) (hb : b = some (.qty dayTag y)) :
    TDates R a b ↔ R x y := by
  subst ha hb
  simp [TDates]

theorem and_denote {S : Structure.{u}} {ρ : VE.Order.Valuation S} (a b : Formula) :
    (Formula.and a b).denote S ρ = (a.denote S ρ ∧ b.denote S ρ) := rfl

theorem eq_denote_iff {S : Structure.{u}} {ρ : VE.Order.Valuation S} {t u : Term} {x y : Int}
    (ht : t.denote S ρ = some (.inr x)) (hu : u.denote S ρ = some (.inr y)) :
    (Formula.eq t u).denote S ρ ↔ x = y := by
  simp [Formula.denote, ht, hu]
  exact eq_comm

theorem lt_denote_iff {S : Structure.{u}} {ρ : VE.Order.Valuation S} {t u : Term} {x y : Int}
    (ht : t.denote S ρ = some (.inr x)) (hu : u.denote S ρ = some (.inr y)) :
    (Formula.lt t u).denote S ρ ↔ x < y := by
  simp [Formula.denote, Compare, ht, hu]

theorem le_denote_iff {S : Structure.{u}} {ρ : VE.Order.Valuation S} {t u : Term} {x y : Int}
    (ht : t.denote S ρ = some (.inr x)) (hu : u.denote S ρ = some (.inr y)) :
    (Formula.le t u).denote S ρ ↔ x ≤ y := by
  simp [Formula.denote, Compare, ht, hu]

theorem add_num_denote {S : Structure.{u}} {ρ : VE.Order.Valuation S} {d : Term} {y : Int}
    (hd : d.denote S ρ = some (.inr y)) (n : Nat) :
    (Term.add d (.num n)).denote S ρ = some (.inr (y + n)) := by
  simp [Term.denote, hd]

theorem sub_denote {S : Structure.{u}} {ρ : VE.Order.Valuation S} {t d : Term} {x y : Int}
    (ht : t.denote S ρ = some (.inr y)) (hd : d.denote S ρ = some (.inr x)) :
    (Term.add t (.scale (-1) d)).denote S ρ = some (.inr (y + -1 * x)) := by
  simp [Term.denote, ht, hd]

/-- **`Time.units_faithful`**: an admitted statement holds in its direct tagged
semantics exactly when its regenerated core formula holds after the units-only
restriction. This preserves truth, not measurement accuracy. -/
theorem units_faithful {α : Type u} {E : QEnv} {T : TStructure α} (hT : T.Admissible E)
    {Γ : List String} {a : QFormula} (h : Admitted E Γ a) {ρ : List α} (hρ : Typed T Γ ρ) :
    a.tdenote T ρ ↔ a.erase.denote T.lower (ρ.map .inl) := by
  induction h generalizing ρ with
  | top | bottom => simp [QFormula.tdenote, QFormula.erase, Formula.denote]
  | unary hp ht =>
    obtain ⟨v, hv, hvt, hve⟩ := term_faithful hT hρ ht
    simp only [QFormula.tdenote, QFormula.erase, Formula.denote]
    rw [hv, hve]
    constructor
    · rintro ⟨v', h1, hr⟩
      cases h1
      exact ⟨v.forget, rfl, [v], hr, rfl⟩
    · rintro ⟨w, h1, vs, hr, hm⟩
      cases h1
      obtain ⟨τs, hps, htup⟩ := hT.2 _ _ hr
      rw [hp] at hps; cases hps
      match vs, htup, hm with
      | [v'], ⟨hv', _⟩, hm =>
        simp only [List.map_cons, List.map_nil, List.cons.injEq, and_true] at hm
        exact ⟨v, rfl, by rwa [← forget_inj hv' hvt hm]⟩
  | binary hp ht hu =>
    obtain ⟨v, hv, hvt, hve⟩ := term_faithful hT hρ ht
    obtain ⟨w, hw, hwt, hwe⟩ := term_faithful hT hρ hu
    simp only [QFormula.tdenote, QFormula.erase, Formula.denote]
    rw [hv, hve, hw, hwe]
    constructor
    · rintro ⟨v', w', h1, h2, hr⟩
      cases h1; cases h2
      exact ⟨v.forget, w.forget, rfl, rfl, [v, w], hr, rfl⟩
    · rintro ⟨v', w', h1, h2, vs, hr, hm⟩
      cases h1; cases h2
      obtain ⟨τs, hps, htup⟩ := hT.2 _ _ hr
      rw [hp] at hps; cases hps
      match vs, htup, hm with
      | [v', w'], ⟨hv', hw', _⟩, hm =>
        simp only [List.map_cons, List.map_nil, List.cons.injEq, and_true] at hm
        exact ⟨v, w, rfl, rfl, by rwa [← forget_inj hv' hvt hm.1, ← forget_inj hw' hwt hm.2]⟩
  | eq ht hu =>
    obtain ⟨v, hv, hvt, hve⟩ := term_faithful hT hρ ht
    obtain ⟨w, hw, hwt, hwe⟩ := term_faithful hT hρ hu
    simp only [QFormula.tdenote, QFormula.erase, Formula.denote]
    rw [hv, hve, hw, hwe]
    constructor
    · rintro ⟨v', h1, h2⟩
      cases h1; cases h2
      exact ⟨_, rfl, rfl⟩
    · rintro ⟨w', h1, h2⟩
      cases h1
      have := forget_inj hvt hwt (Option.some.inj h2).symm
      subst this
      exact ⟨v, rfl, rfl⟩
  | lt ht hu | le ht hu =>
    obtain ⟨x, hv, hve⟩ := day_faithful hT hρ ht
    obtain ⟨y, hw, hwe⟩ := day_faithful hT hρ hu
    simp only [QFormula.tdenote, QFormula.erase, Formula.denote, TCompare, Compare]
    rw [hv, hve, hw, hwe]
    constructor
    · rintro ⟨g, a, b, h1, h2, hr⟩
      cases h1; cases h2
      exact ⟨_, _, rfl, rfl, hr⟩
    · rintro ⟨a, b, h1, h2, hr⟩
      cases h1; cases h2
      exact ⟨_, _, _, rfl, rfl, hr⟩
  | not _ ih => simp only [QFormula.tdenote, QFormula.erase, Formula.denote, ih hρ]
  | and _ _ ia ib | or _ _ ia ib | implies _ _ ia ib =>
    simp only [QFormula.tdenote, QFormula.erase, Formula.denote, ia hρ, ib hρ]
  | all _ _ _ ih =>
    simp only [QFormula.tdenote, QFormula.erase, Formula.denote, TStructure.lower]
    exact forall_congr' fun x => imp_congr_right fun hx => ih (hρ.cons hx)
  | ex _ _ _ ih =>
    simp only [QFormula.tdenote, QFormula.erase, Formula.denote, TStructure.lower]
    exact exists_congr fun x => and_congr_right fun hx => ih (hρ.cons hx)
  | dateOn ht hd =>
    obtain ⟨x, hv, hve⟩ := day_faithful hT hρ ht
    obtain ⟨y, hw, hwe⟩ := day_faithful hT hρ hd
    rw [QFormula.tdenote, tdates_iff hv hw, on_iff]
    simp only [QFormula.erase]
    rw [and_denote, guards_denote hve hwe, eq_denote_iff hve hwe]
  | dateBefore ht hd =>
    obtain ⟨x, hv, hve⟩ := day_faithful hT hρ ht
    obtain ⟨y, hw, hwe⟩ := day_faithful hT hρ hd
    rw [QFormula.tdenote, tdates_iff hv hw, before_iff_lt]
    simp only [QFormula.erase]
    rw [and_denote, guards_denote hve hwe, lt_denote_iff hve hwe]
  | dateAfter ht hd =>
    obtain ⟨x, hv, hve⟩ := day_faithful hT hρ ht
    obtain ⟨y, hw, hwe⟩ := day_faithful hT hρ hd
    rw [QFormula.tdenote, tdates_iff hv hw, after_iff_lt]
    simp only [QFormula.erase]
    rw [and_denote, guards_denote hve hwe, lt_denote_iff hwe hve]
  | dateNoLater ht hd =>
    obtain ⟨x, hv, hve⟩ := day_faithful hT hρ ht
    obtain ⟨y, hw, hwe⟩ := day_faithful hT hρ hd
    rw [QFormula.tdenote, tdates_iff hv hw, noLater_iff_le]
    simp only [QFormula.erase]
    rw [and_denote, guards_denote hve hwe, le_denote_iff hve hwe]
  | @within _ _ _ n ht hd =>
    obtain ⟨x, hv, hve⟩ := day_faithful hT hρ ht
    obtain ⟨y, hw, hwe⟩ := day_faithful hT hρ hd
    rw [QFormula.tdenote, tdates_iff (R := fun a b => CalWithin a b n) hv hw, within_iff]
    simp only [QFormula.erase]
    rw [and_denote, guards_denote hve hwe, and_denote, le_denote_iff hwe hve,
      le_denote_iff hve (add_num_denote hwe n)]
  | @shift _ _ _ n ht hd =>
    obtain ⟨x, hv, hve⟩ := day_faithful hT hρ ht
    obtain ⟨y, hw, hwe⟩ := day_faithful hT hρ hd
    rw [QFormula.tdenote, tdates_iff (R := fun a b => CalShift a b n) hv hw, shift_iff]
    simp only [QFormula.erase]
    rw [and_denote, guards_denote hve hwe, eq_denote_iff hve (add_num_denote hwe n)]
  | elapsed hd ht hv =>
    obtain ⟨x, hx, hxe⟩ := day_faithful hT hρ hd
    obtain ⟨y, hy, hye⟩ := day_faithful hT hρ ht
    obtain ⟨w, hw, hwe⟩ := day_faithful hT hρ hv
    simp only [QFormula.erase]
    rw [and_denote, guards_denote hxe hye, eq_denote_iff hwe (sub_denote hye hxe), ← elapsed_iff]
    simp only [QFormula.tdenote]
    rw [hx, hy, hw]
    constructor
    · rintro ⟨a, b, c, h1, h2, h3, hr⟩
      cases h1; cases h2; cases h3
      exact hr
    · intro hr
      exact ⟨x, y, w, rfl, rfl, rfl, hr⟩

/-! ## Admissibility and the unique tagged interpretation -/

theorem lower_admissible {α : Type u} {E : QEnv} {T : TStructure α} (hT : T.Admissible E) :
    T.lower.Admissible E.erase := by
  constructor
  · intro c s hc
    simp only [QEnv.erase, Option.map_eq_some_iff] at hc
    obtain ⟨τ, hτ, rfl⟩ := hc
    obtain ⟨v, hv, hty⟩ := hT.1 c τ hτ
    refine ⟨v.forget, by simp [TStructure.lower, hv], ?_⟩
    cases τ <;> cases v <;> simp_all [TValue.Typed, TValue.forget, QType.erase,
      Structure.domain, TStructure.lower]
  · rintro p ws ⟨vs, hr, rfl⟩
    obtain ⟨τs, hp, htup⟩ := hT.2 p vs hr
    refine ⟨τs.map QType.erase, by simp [QEnv.erase, hp], ?_⟩
    clear hp hr
    induction τs generalizing vs with
    | nil => cases vs <;> simp_all [TTuple, VE.Order.TupleTyped]
    | cons τ τs ih =>
      cases vs with
      | nil => exact False.elim htup
      | cons v vs =>
        refine ⟨?_, ih vs htup.2⟩
        have hv := htup.1
        cases τ <;> cases v <;> simp_all [TValue.Typed, TValue.forget, QType.erase,
          Structure.domain, TStructure.lower]

/-- Retag a core value at a declared statement type. -/
def retag {α : Type u} : QType → Value α → TValue α
  | .qty g, .inr z => .qty g z
  | _, .inl a => .obj a
  | .obj _, .inr z => .qty dimensionless z

def retagAll {α : Type u} : List QType → List (Value α) → List (TValue α)
  | τ :: τs, v :: vs => retag τ v :: retagAll τs vs
  | _, _ => []

/-- The units-only expansion map: the tagged interpretation of a core structure. -/
def lift (E : QEnv) (S : Structure.{u}) : TStructure S.Carrier where
  objects := S.objects
  constant c := match E.constants c with
    | some τ => (S.constant c).map (retag τ)
    | none => none
  relation p vs := ∃ τs, E.predicates p = some τs ∧ TTuple S.objects τs vs ∧
    S.relation p (vs.map TValue.forget)

theorem retag_typed {S : Structure.{u}} {τ : QType} {v : Value S.Carrier}
    (h : S.domain τ.erase v) : (retag τ v).Typed S.objects τ ∧ (retag τ v).forget = v := by
  cases τ <;> cases v <;> simp_all [retag, TValue.Typed, TValue.forget, QType.erase,
    Structure.domain]

theorem lift_admissible {E : QEnv} {S : Structure.{u}} (hS : S.Admissible E.erase) :
    (lift E S).Admissible E := by
  constructor
  · intro c τ hc
    obtain ⟨v, hv, hd⟩ := hS.1 c τ.erase (by simp [QEnv.erase, hc])
    exact ⟨retag τ v, by simp [lift, hc, hv], (retag_typed hd).1⟩
  · rintro p vs ⟨τs, hp, htup, _⟩
    exact ⟨τs, hp, htup⟩

theorem tuple_retag {S : Structure.{u}} :
    ∀ (τs : List QType) (ws : List (Value S.Carrier)),
      VE.Order.TupleTyped S (τs.map QType.erase) ws →
      TTuple S.objects τs (retagAll τs ws) ∧ (retagAll τs ws).map TValue.forget = ws
  | [], [], _ => ⟨trivial, rfl⟩
  | τ :: τs, w :: ws, ⟨hw, hws⟩ =>
    let ⟨ht, hf⟩ := retag_typed hw
    let ⟨hts, hfs⟩ := tuple_retag τs ws hws
    ⟨⟨ht, hts⟩, by simp [retagAll, hf, hfs]⟩
  | [], _ :: _, h => False.elim h
  | _ :: _, [], h => False.elim h

/-- The lift restricts back to the core structure on declared constants and
on every relation. -/
theorem lower_lift {E : QEnv} {S : Structure.{u}} (hS : S.Admissible E.erase) :
    (∀ c τ, E.constants c = some τ → (lift E S).lower.constant c = S.constant c) ∧
      ∀ p ws, (lift E S).lower.relation p ws ↔ S.relation p ws := by
  constructor
  · intro c τ hc
    obtain ⟨v, hv, hd⟩ := hS.1 c τ.erase (by simp [QEnv.erase, hc])
    simp [TStructure.lower, lift, hc, hv, (retag_typed hd).2]
  · intro p ws
    constructor
    · rintro ⟨vs, ⟨_, _, _, hr⟩, rfl⟩
      exact hr
    · intro hr
      obtain ⟨ss, hp, htup⟩ := hS.2 p ws hr
      simp only [QEnv.erase, Option.map_eq_some_iff] at hp
      obtain ⟨τs, hτs, rfl⟩ := hp
      obtain ⟨ht, hf⟩ := tuple_retag (S := S) τs ws htup
      exact ⟨retagAll τs ws, ⟨τs, hτs, ht, by rw [hf]; exact hr⟩, hf⟩

theorem tuple_forget_inj {α : Type u} {objects : String → α → Prop} :
    ∀ (τs : List QType) (vs ws : List (TValue α)), TTuple objects τs vs → TTuple objects τs ws →
      vs.map TValue.forget = ws.map TValue.forget → vs = ws
  | [], [], [], _, _, _ => rfl
  | τ :: τs, v :: vs, w :: ws, hv, hw, h => by
    simp only [List.map_cons, List.cons.injEq] at h
    rw [forget_inj hv.1 hw.1 h.1, tuple_forget_inj τs vs ws hv.2 hw.2 h.2]
  | [], _ :: _, _, hv, _, _ => False.elim hv
  | [], [], _ :: _, _, hw, _ => False.elim hw
  | _ :: _, [], _, hv, _, _ => False.elim hv
  | _ :: _, _ :: _, [], _, hw, _ => False.elim hw

/-- **Uniqueness**
: an admissible tagged structure is determined, on declared
symbols, by its units-only restriction: it agrees with the lift of that
restriction. -/
theorem lift_unique {α : Type u} {E : QEnv} {T : TStructure α} (hT : T.Admissible E) :
    (∀ c τ, E.constants c = some τ → (lift E T.lower).constant c = T.constant c) ∧
      ∀ p vs, (lift E T.lower).relation p vs ↔ T.relation p vs := by
  constructor
  · intro c τ hc
    obtain ⟨v, hv, hty⟩ := hT.1 c τ hc
    simp only [lift, hc, TStructure.lower, hv, Option.map_some, Option.some.injEq]
    cases τ <;> cases v <;> simp_all [retag, TValue.Typed, TValue.forget]
  · intro p vs
    constructor
    · rintro ⟨τs, hp, htup, ws, hr, hm⟩
      obtain ⟨τs', hp', htup'⟩ := hT.2 p ws hr
      rw [hp] at hp'; cases hp'
      have : ws = vs := tuple_forget_inj τs ws vs htup' htup hm
      rwa [← this]
    · intro hr
      obtain ⟨τs, hp, htup⟩ := hT.2 p vs hr
      exact ⟨τs, hp, htup, vs, hr, rfl⟩

/-! ## Entailment over tagged structures -/

/-- Tagged entailment: every admissible tagged structure satisfying the
premises satisfies the conclusion. -/
def TEntails (E : QEnv) (premises : List QFormula) (conclusion : QFormula) : Prop :=
  ∀ (α : Type v) (T : TStructure α), T.Admissible E →
    (∀ a ∈ premises, a.tdenote T []) → conclusion.tdenote T []

theorem typed_nil {α : Type u} (T : TStructure α) : Typed T [] [] := by
  intro i s h; simp at h

/-- Core entailment of the regenerated formulas gives tagged entailment of the
admitted statements. -/
theorem tentails_of_entails {E : QEnv} {ps : List QFormula} {c : QFormula}
    (hps : ∀ a ∈ ps, Admitted E [] a) (hc : Admitted E [] c)
    (h : VE.Order.Entails.{v} E.erase (ps.map QFormula.erase) c.erase) : TEntails.{v} E ps c := by
  intro α T hT hp
  have hS := lower_admissible hT
  have := h T.lower hS (by
    intro a ha
    obtain ⟨b, hb, rfl⟩ := List.mem_map.mp ha
    exact (units_faithful hT (hps b hb) (typed_nil T)).mp (hp b hb))
  exact (units_faithful hT hc (typed_nil T)).mpr this

end VE.Time
