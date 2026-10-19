import VE.Calc.Eval

/-! Physical dimensions (math-evidence spec 6.1, ME-6): the physical dimension of an expression,
the unit-change invariance of comparisons and roundings, and conversion by unit factors. The
statistics cases of `Expr.dimOf` and `commonDim` arrive with ME-7's expression forms. -/

namespace VE.Calc
open VE.Numbers

/-- A physical dimension: an exponent per base dimension; normal form sorted by name, no zero exponent. -/
structure PhysDim where
  exps : List (String × Int)
  deriving Repr, DecidableEq, Inhabited

def PhysDim.Normal (d : PhysDim) : Prop :=
  (d.exps.map (·.1)).Pairwise (· < ·) ∧ ∀ e ∈ d.exps, e.2 ≠ 0
def PhysDim.one : PhysDim := ⟨[]⟩

/-- Add exponent `e.2` of base `e.1` into a sorted list, dropping a zero exponent. -/
def insertExp (e : String × Int) : List (String × Int) → List (String × Int)
  | [] => if e.2 = 0 then [] else [e]
  | (n, k) :: rest =>
    if e.1 = n then (if k + e.2 = 0 then rest else (n, k + e.2) :: rest)
    else if e.1 < n then (if e.2 = 0 then (n, k) :: rest else e :: (n, k) :: rest)
    else (n, k) :: insertExp e rest

def PhysDim.mul (a b : PhysDim) : PhysDim := ⟨b.exps.foldl (fun acc e => insertExp e acc) a.exps⟩
def PhysDim.inv (a : PhysDim) : PhysDim := ⟨a.exps.map fun e => (e.1, -e.2)⟩
def PhysDim.npow (a : PhysDim) (k : Nat) : PhysDim :=
  if k = 0 then PhysDim.one else ⟨a.exps.map fun e => (e.1, e.2 * k)⟩

/-- Literals are dimensionless; sums and differences need equal dimensions (`none` is `DimensionMismatch`). -/
def Expr.dimOf (Γ : String → Option PhysDim) : Expr → Option PhysDim
  | .lit _ => some PhysDim.one
  | .val n => Γ n
  | .add a b | .sub a b => do
      let x ← a.dimOf Γ
      let y ← b.dimOf Γ
      if x = y then some x else none
  | .mul a b => do let x ← a.dimOf Γ; let y ← b.dimOf Γ; pure (x.mul y)
  | .div a b => do let x ← a.dimOf Γ; let y ← b.dimOf Γ; pure (x.mul y.inv)
  | .pow a k => (a.dimOf Γ).map (·.npow k)

/-- A change of base units: a positive factor per base dimension. -/
structure Rescale where
  factor : String → Rat
  pos : ∀ b, 0 < factor b

def zpowR (q : Rat) : Int → Rat
  | .ofNat n => q ^ n
  | .negSucc n => 1 / q ^ (n + 1)

def Rescale.of (ρ : Rescale) (d : PhysDim) : Rat :=
  (d.exps.map fun e => zpowR (ρ.factor e.1) e.2).foldl (· * ·) 1

/-- Every named value rescaled by its own physical dimension's factor. -/
def Rescale.apply (ρ : Rescale) (Γ : String → Option PhysDim) (σ : Values) : Values :=
  fun n => match σ n, Γ n with
    | some q, some d => some (q * ρ.of d)
    | v, _ => v

/-- `ve-units@1` tags stay nominal (debate A5): each is read as its own base dimension. -/
def legacyDim (tag : String) : PhysDim := ⟨[(tag, 1)]⟩

/-! ## Proofs -/

theorem zpowR_eq (q : Rat) (i : Int) : zpowR q i = q ^ i := by
  cases i with
  | ofNat n => rfl
  | negSucc n =>
      change 1 / q ^ (n + 1) = (q ^ (n + 1))⁻¹
      simp [Rat.div_def]

theorem zpowR_mul_nat (q : Rat) (hq : q ≠ 0) (i : Int) (k : Nat) :
    q ^ (i * (k : Int)) = (q ^ i) ^ k := by
  induction k with
  | zero => simp
  | succ k ih =>
      rw [show i * ((k + 1 : Nat) : Int) = i * (k : Int) + i by simp [Int.mul_add],
        Rat.zpow_add hq, ih, Rat.pow_succ]

theorem mul_pow_nat (a b : Rat) (k : Nat) : (a * b) ^ k = a ^ k * b ^ k := by
  induction k with
  | zero => simp
  | succ k ih => rw [Rat.pow_succ, Rat.pow_succ, Rat.pow_succ, ih]; grind

theorem one_pow_nat (k : Nat) : (1 : Rat) ^ k = 1 := by
  induction k with
  | zero => rfl
  | succ k ih => rw [Rat.pow_succ, ih, Rat.mul_one]

theorem foldl_mul_rat (a : Rat) (l : List Rat) : l.foldl (· * ·) a = a * l.foldl (· * ·) 1 := by
  induction l generalizing a with
  | nil => simp
  | cons x xs ih =>
      simp only [List.foldl_cons]
      rw [ih (a * x), ih (1 * x)]
      grind

theorem Rescale.of_cons (ρ : Rescale) (e : String × Int) (l : List (String × Int)) :
    ρ.of ⟨e :: l⟩ = ρ.factor e.1 ^ e.2 * ρ.of ⟨l⟩ := by
  simp only [Rescale.of, List.map_cons, List.foldl_cons]
  rw [foldl_mul_rat, zpowR_eq]
  grind

theorem Rescale.factor_ne (ρ : Rescale) (b : String) : ρ.factor b ≠ 0 :=
  fun h => by have := ρ.pos b; rw [h] at this; exact absurd this (by decide)

theorem Rescale.of_pos (ρ : Rescale) (d : PhysDim) : 0 < ρ.of d := by
  obtain ⟨exps⟩ := d
  induction exps with
  | nil => exact (by decide : (0 : Rat) < 1)
  | cons e rest ih => rw [Rescale.of_cons]; exact Rat.mul_pos (Rat.zpow_pos (ρ.pos _)) ih

theorem Rescale.of_one (ρ : Rescale) : ρ.of PhysDim.one = 1 := by
  simp [Rescale.of, PhysDim.one]

theorem Rescale.of_insertExp (ρ : Rescale) (e : String × Int) (l : List (String × Int)) :
    ρ.of ⟨insertExp e l⟩ = ρ.factor e.1 ^ e.2 * ρ.of ⟨l⟩ := by
  have hadd := fun b => Rat.zpow_add (ρ.factor_ne b)
  induction l with
  | nil => by_cases h : e.2 = 0 <;> simp [insertExp, h, Rescale.of, zpowR_eq]
  | cons hd rest ih =>
      obtain ⟨n, k⟩ := hd
      simp only [insertExp]
      by_cases h1 : e.1 = n
      · have h0 := hadd n k e.2
        by_cases h2 : k + e.2 = 0
        · simp only [h1, h2, if_true, Rescale.of_cons] at h0 ⊢
          rw [Rat.zpow_zero] at h0
          grind
        · simp only [h1, h2, if_true, if_false, Rescale.of_cons]
          rw [h0]; grind
      · by_cases h3 : e.1 < n
        · by_cases h4 : e.2 = 0
          · simp [h1, h3, h4]
          · simp [h1, h3, h4, Rescale.of_cons]
        · simp only [h1, h3, if_false, Rescale.of_cons, ih]
          grind

theorem Rescale.of_mul_any (ρ : Rescale) (a b : PhysDim) : ρ.of (a.mul b) = ρ.of a * ρ.of b := by
  obtain ⟨as⟩ := a
  obtain ⟨bs⟩ := b
  simp only [PhysDim.mul]
  induction bs generalizing as with
  | nil => simp [Rescale.of]
  | cons e rest ih =>
      simp only [List.foldl_cons]
      rw [ih, Rescale.of_insertExp, Rescale.of_cons]
      grind

theorem Rescale.of_mul (ρ : Rescale) (a b : PhysDim) (ha : a.Normal) (hb : b.Normal) :
    ρ.of (a.mul b) = ρ.of a * ρ.of b :=
  let _ := ha; let _ := hb
  ρ.of_mul_any a b

theorem Rescale.of_inv (ρ : Rescale) (a : PhysDim) : ρ.of a.inv = (ρ.of a)⁻¹ := by
  obtain ⟨exps⟩ := a
  induction exps with
  | nil => exact (Rat.inv_mul_cancel 1 (by decide)).symm.trans (Rat.mul_one _)
  | cons e rest ih =>
      simp only [PhysDim.inv, List.map_cons] at ih ⊢
      rw [Rescale.of_cons, Rescale.of_cons, ih, Rat.zpow_neg, Rat.inv_mul_rev]
      grind

theorem Rescale.of_npow (ρ : Rescale) (a : PhysDim) (k : Nat) : ρ.of (a.npow k) = ρ.of a ^ k := by
  by_cases hk : k = 0
  · simp [PhysDim.npow, hk, Rescale.of_one]
  · simp only [PhysDim.npow, hk, if_false]
    obtain ⟨exps⟩ := a
    induction exps with
    | nil => exact (one_pow_nat k).symm
    | cons e rest ih =>
        simp only [List.map_cons] at ih ⊢
        rw [Rescale.of_cons, Rescale.of_cons, ih, zpowR_mul_nat _ (ρ.factor_ne _),
          mul_pow_nat]

/-- Evaluation under rescaled values: the value of an expression of dimension `d` scales by `ρ.of d`. -/
theorem Expr.eval_rescale (Γ : String → Option PhysDim) (ρ : Rescale) (σ : Values) (e : Expr)
    (d : PhysDim) (hd : e.dimOf Γ = some d) :
    e.eval (ρ.apply Γ σ) = (e.eval σ).map (· * ρ.of d) := by
  induction e generalizing d with
  | lit q =>
      simp only [Expr.dimOf, Option.some.injEq] at hd
      subst hd
      simp [Expr.eval, Rescale.of_one]
  | val n =>
      simp only [Expr.dimOf] at hd
      simp only [Expr.eval, Rescale.apply, hd]
      cases σ n <;> rfl
  | add a b iha ihb | sub a b iha ihb =>
      simp only [Expr.dimOf] at hd
      cases ha : a.dimOf Γ with
      | none => simp [ha] at hd
      | some x =>
        cases hb : b.dimOf Γ with
        | none => simp [ha, hb] at hd
        | some y =>
          by_cases hxy : x = y
          · simp [ha, hb, hxy] at hd
            subst hd hxy
            simp only [Expr.eval, iha x ha, ihb x hb]
            cases a.eval σ <;> cases b.eval σ <;> simp <;> grind
          · simp [ha, hb, hxy] at hd
  | mul a b iha ihb =>
      simp only [Expr.dimOf] at hd
      cases ha : a.dimOf Γ with
      | none => simp [ha] at hd
      | some x =>
        cases hb : b.dimOf Γ with
        | none => simp [ha, hb] at hd
        | some y =>
          simp [ha, hb] at hd
          subst hd
          simp only [Expr.eval, iha x ha, ihb y hb, Rescale.of_mul_any]
          cases a.eval σ <;> cases b.eval σ <;> simp <;> grind
  | div a b iha ihb =>
      simp only [Expr.dimOf] at hd
      cases ha : a.dimOf Γ with
      | none => simp [ha] at hd
      | some x =>
        cases hb : b.dimOf Γ with
        | none => simp [ha, hb] at hd
        | some y =>
          simp [ha, hb] at hd
          subst hd
          have hy := Rat.ne_of_gt (ρ.of_pos y)
          simp only [Expr.eval, iha x ha, ihb y hb, Rescale.of_mul_any, Rescale.of_inv]
          cases a.eval σ <;> cases hv : b.eval σ <;> simp
          rename_i u v
          by_cases hv0 : v = 0
          · simp [hv0]
          · have hmul : v * ρ.of y ≠ 0 := fun h => by
              rcases Rat.mul_eq_zero.mp h with h | h
              · exact hv0 h
              · exact hy h
            simp [hv0, hmul]
            grind
  | pow a k iha =>
      simp only [Expr.dimOf] at hd
      cases ha : a.dimOf Γ with
      | none => simp [ha] at hd
      | some x =>
        simp [ha] at hd
        subst hd
        simp only [Expr.eval, iha x ha, Rescale.of_npow]
        cases a.eval σ <;> simp [mul_pow_nat]

theorem denotes_rescale (Γ : String → Option PhysDim) (ρ : Rescale) (σ : Values) (e : Expr) (d : PhysDim)
    (x : Rat) (hΓ : ∀ n d', Γ n = some d' → d'.Normal) (hd : e.dimOf Γ = some d) (hx : Denotes σ e x) :
    Denotes (ρ.apply Γ σ) e (x * ρ.of d) := by
  have _ := hΓ
  rw [← Expr.eval_iff, Expr.eval_rescale Γ ρ σ e d hd, (Expr.eval_iff σ e x).mpr hx]
  rfl

/-- A comparison keeps its truth when both sides are multiplied by one positive factor. -/
theorem Comparison.holds_scale (c : Comparison) (x y o : Rat) (ho : 0 < o) :
    c.Holds (x * o) (y * o) ↔ c.Holds x y := by
  have hne : o ≠ 0 := fun h => by rw [h] at ho; exact absurd ho (by decide)
  have heq : ∀ u v : Rat, u * o = v * o ↔ u = v := fun u v => by
    constructor
    · intro h
      have := congrArg (· * o⁻¹) h
      simp only [Rat.mul_assoc, Rat.mul_inv_cancel o hne, Rat.mul_one] at this
      exact this
    · intro h; rw [h]
  have hlt : ∀ u v : Rat, u * o < v * o ↔ u < v := fun u v => Rat.mul_lt_mul_right ho
  have hle : ∀ u v : Rat, u * o ≤ v * o ↔ u ≤ v := fun u v => by
    constructor
    · intro h
      exact Classical.byContradiction fun hn =>
        absurd h (Rat.not_le.mpr ((hlt v u).mpr (Rat.not_le.mp hn)))
    · intro h; exact Rat.mul_le_mul_of_nonneg_right h (Rat.le_of_lt ho)
  obtain ⟨rel, swap⟩ := c
  cases rel <;> cases swap <;> simp [Comparison.Holds, Rel.Holds, heq, hlt, hle]

/-- **Unit-change invariance**: a comparison of two expressions of one physical dimension has the same truth in
every system of base units. -/
theorem compare_invariant (Γ : String → Option PhysDim) (ρ : Rescale) (σ : Values) (c : Comparison)
    (a b : Expr) (d : PhysDim) (hΓ : ∀ n d', Γ n = some d' → d'.Normal)
    (ha : a.dimOf Γ = some d) (hb : b.dimOf Γ = some d) :
    (Claim.compare c a b).Holds σ ↔ (Claim.compare c a b).Holds (ρ.apply Γ σ) := by
  have _ := hΓ
  simp only [Claim.Holds, ← Expr.eval_iff, Expr.eval_rescale Γ ρ σ a d ha, Expr.eval_rescale Γ ρ σ b d hb]
  cases a.eval σ <;> cases b.eval σ <;> simp [Comparison.holds_scale c _ _ _ (ρ.of_pos d)]

/-- A rounding claim is admitted only on a dimensionless expression, whose truth no change of units moves. -/
theorem rounds_invariant (Γ : String → Option PhysDim) (ρ : Rescale) (σ : Values) (r : Rounding)
    (e : Expr) (p : Printed) (hΓ : ∀ n d', Γ n = some d' → d'.Normal) (he : e.dimOf Γ = some PhysDim.one) :
    (Claim.rounds r e p).Holds σ ↔ (Claim.rounds r e p).Holds (ρ.apply Γ σ) := by
  have _ := hΓ
  simp only [Claim.Holds, ← Expr.eval_iff, Expr.eval_rescale Γ ρ σ e _ he, Rescale.of_one]
  cases e.eval σ <;> simp

/-- Units are values (their factor to the coherent unit): `q` in unit `u` is `q · fu / fv` in unit `v`. Quantities'
QT-A7 uses this theorem. -/
theorem convert_by_factors (σ : Values) (u v : String) (fu fv q x : Rat) (hu : σ u = some fu)
    (hv : σ v = some fv) (hfv : fv ≠ 0) :
    Denotes σ (.mul (.lit q) (.val u)) x ↔ Denotes σ (.mul (.lit (q * fu / fv)) (.val v)) x := by
  simp [← Expr.eval_iff, Expr.eval, hu, hv, Rat.div_mul_cancel hfv]

theorem legacy_nominal (t t' : String) (h : t ≠ t') : legacyDim t ≠ legacyDim t' := by
  intro heq
  simp only [legacyDim, PhysDim.mk.injEq, List.cons.injEq, Prod.mk.injEq, and_true] at heq
  exact h heq

end VE.Calc
