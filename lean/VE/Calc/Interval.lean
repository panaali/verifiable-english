import VE.Calc.Decls

/-! Interval enclosures (math-evidence spec 8.1, ME-8): a printed input stands for every value in its rounding
interval, and `enclose` evaluates an inlined expression exactly over those intervals, the inputs kept as `val` nodes
(statement review J4). Each operation's enclosure is proved (`enclose_sound`); `encloseC` is the same evaluation
charged in 3.2's unit (`Work`). -/

namespace VE.Calc
open VE.Numbers Work

/-- The closed interval that holds every value rounding to `p` under `r`. -/
def _root_.VE.Numbers.Printed.box (r : Rounding) (p : Printed) : Rat × Rat :=
  let u := tenPow p.places
  let D : Rat := p.digits
  match r with
  | .tiesUp | .halfEven => ((2 * D - 1) / (2 * u), (2 * D + 1) / (2 * u))
  | .down => (D / u, (D + 1) / u)
  | .up => ((D - 1) / u, D / u)

theorem Interval.div_le_of {a c x : Rat} (hc : 0 < c) (h : a ≤ x * c) : a / c ≤ x := by
  rw [← Rat.not_lt, Rat.lt_div_iff hc]; grind

theorem Interval.le_div_of {a c x : Rat} (hc : 0 < c) (h : x * c ≤ a) : x ≤ a / c := by
  rw [← Rat.not_lt, Rat.div_lt_iff hc]; grind

theorem _root_.VE.Numbers.Printed.box_sound (r : Rounding) (p : Printed) (x : Rat) (h : RoundsTo r p x) :
    (p.box r).1 ≤ x ∧ x ≤ (p.box r).2 := by
  have hu := tenPow_pos p.places
  have h2 : (0 : Rat) < 2 * tenPow p.places := by grind
  cases r <;> simp only [RoundsTo] at h <;> simp only [Printed.box] <;>
    exact ⟨Interval.div_le_of (by assumption) (by grind), Interval.le_div_of (by assumption) (by grind)⟩

def minR (a b : Rat) : Rat := if a ≤ b then a else b
def maxR (a b : Rat) : Rat := if a ≤ b then b else a

def Interval.add (a b : Rat × Rat) : Rat × Rat := (a.1 + b.1, a.2 + b.2)
def Interval.sub (a b : Rat × Rat) : Rat × Rat := (a.1 - b.2, a.2 - b.1)
def Interval.mul (a b : Rat × Rat) : Rat × Rat :=
  (minR (minR (a.1 * b.1) (a.1 * b.2)) (minR (a.2 * b.1) (a.2 * b.2)),
   maxR (maxR (a.1 * b.1) (a.1 * b.2)) (maxR (a.2 * b.1) (a.2 * b.2)))
/-- The reciprocals of an interval that excludes 0; none when it may contain 0. -/
def Interval.inv? (b : Rat × Rat) : Option (Rat × Rat) := if 0 < b.1 ∨ b.2 < 0 then some (b.2⁻¹, b.1⁻¹) else none
/-- Powers: monotone on a nonnegative interval, else bounded by the largest magnitude. -/
def Interval.pow (a : Rat × Rat) (k : Nat) : Rat × Rat :=
  if 0 ≤ a.1 then (a.1 ^ k, a.2 ^ k) else (-(maxR (-a.1) a.2 ^ k), maxR (-a.1) a.2 ^ k)

theorem Interval.between {l h x : Rat} (y : Rat) (h1 : l ≤ x) (h2 : x ≤ h) :
    (l * y ≤ x * y ∧ x * y ≤ h * y) ∨ (h * y ≤ x * y ∧ x * y ≤ l * y) := by
  by_cases hy : 0 ≤ y
  · exact .inl ⟨Rat.mul_le_mul_of_nonneg_right h1 hy, Rat.mul_le_mul_of_nonneg_right h2 hy⟩
  · have hy' : 0 ≤ -y := by grind
    have := Rat.mul_le_mul_of_nonneg_right h1 hy'; have := Rat.mul_le_mul_of_nonneg_right h2 hy'; grind

theorem Interval.mul_sound {a b : Rat × Rat} {x y : Rat} (hx : a.1 ≤ x ∧ x ≤ a.2) (hy : b.1 ≤ y ∧ y ≤ b.2) :
    (Interval.mul a b).1 ≤ x * y ∧ x * y ≤ (Interval.mul a b).2 := by
  have h0 := between y hx.1 hx.2
  have h1 := between a.1 hy.1 hy.2
  have h2 := between a.2 hy.1 hy.2
  simp only [Interval.mul, minR, maxR]; grind

theorem Interval.inv_le {c y : Rat} (hc : 0 < c) (h : c ≤ y) : y⁻¹ ≤ c⁻¹ := by
  have hy : 0 < y := by grind
  have h1 := Rat.mul_le_mul_of_nonneg_right h (Rat.le_of_lt (Rat.inv_pos.mpr hy))
  have h2 := Rat.mul_le_mul_of_nonneg_left h1 (Rat.le_of_lt (Rat.inv_pos.mpr hc))
  have e1 : y * y⁻¹ = 1 := by grind
  have e2 : c⁻¹ * (c * y⁻¹) = y⁻¹ := by grind
  rw [e1, Rat.mul_one, e2] at h2; exact h2

theorem Interval.inv_sound {b i : Rat × Rat} {y : Rat} (h : Interval.inv? b = some i) (hy : b.1 ≤ y ∧ y ≤ b.2) :
    i.1 ≤ y⁻¹ ∧ y⁻¹ ≤ i.2 := by
  unfold Interval.inv? at h; split at h <;> cases h
  rename_i hb; rcases hb with hb | hb
  · exact ⟨inv_le (by grind) hy.2, inv_le hb hy.1⟩
  · have e : ∀ z : Rat, (-z)⁻¹ = -z⁻¹ := by grind
    have h1 := inv_le (c := -b.2) (y := -y) (by grind) (by grind)
    have h2 := inv_le (c := -y) (y := -b.1) (by grind) (by grind)
    rw [e, e] at h1 h2; exact ⟨by grind, by grind⟩

theorem Interval.pow_nonneg {x : Rat} (hx : 0 ≤ x) (k : Nat) : 0 ≤ x ^ k := by
  induction k with
  | zero => rw [Rat.pow_zero]; decide
  | succ k ih => rw [Rat.pow_succ]; exact Rat.mul_nonneg ih hx

theorem Interval.pow_le_pow {x y : Rat} (hx : 0 ≤ x) (h : x ≤ y) (k : Nat) : x ^ k ≤ y ^ k := by
  induction k with
  | zero => rw [Rat.pow_zero, Rat.pow_zero]; exact Rat.le_refl
  | succ k ih =>
    rw [Rat.pow_succ, Rat.pow_succ]
    exact Rat.le_trans (Rat.mul_le_mul_of_nonneg_left h (pow_nonneg hx k))
      (Rat.mul_le_mul_of_nonneg_right ih (by grind))

theorem Interval.pow_abs {m x : Rat} (hm : 0 ≤ m) (h1 : -m ≤ x) (h2 : x ≤ m) (k : Nat) :
    -(m ^ k) ≤ x ^ k ∧ x ^ k ≤ m ^ k := by
  induction k with
  | zero => rw [Rat.pow_zero, Rat.pow_zero]; grind
  | succ k ih =>
    have hM := pow_nonneg hm k
    have hb := between x ih.1 ih.2
    have := Rat.mul_le_mul_of_nonneg_left h1 hM; have := Rat.mul_le_mul_of_nonneg_left h2 hM
    rw [Rat.pow_succ, Rat.pow_succ]; grind

theorem Interval.pow_sound {a : Rat × Rat} {x : Rat} (k : Nat) (hx : a.1 ≤ x ∧ x ≤ a.2) :
    (Interval.pow a k).1 ≤ x ^ k ∧ x ^ k ≤ (Interval.pow a k).2 := by
  unfold Interval.pow; split
  · exact ⟨pow_le_pow (by assumption) hx.1 k, pow_le_pow (by grind) hx.2 k⟩
  · exact pow_abs (by unfold maxR; split <;> grind) (by unfold maxR; split <;> grind) (by unfold maxR; split <;> grind) k

/-- *Opaque* in spec 8.1: exact interval evaluation of an inlined expression over the input intervals; none when it
reads a name that is not an input or divides by an interval that contains 0. -/
def enclose (r : Rounding) (inputs : List (String × Printed)) (e : Expr) : Option (Rat × Rat) := match e with
  | .lit q => some (q, q)
  | .val n => (inputs.lookup n).map (Printed.box r)
  | .add a b => do pure (Interval.add (← enclose r inputs a) (← enclose r inputs b))
  | .sub a b => do pure (Interval.sub (← enclose r inputs a) (← enclose r inputs b))
  | .mul a b => do pure (Interval.mul (← enclose r inputs a) (← enclose r inputs b))
  | .div a b => do
      let x ← enclose r inputs a
      let y ← enclose r inputs b
      pure (Interval.mul x (← Interval.inv? y))
  | .pow a k => (enclose r inputs a).map (Interval.pow · k)

/-- Every input's value rounds to its printed number. -/
def InBox (r : Rounding) (inputs : List (String × Printed)) (κ : String → Rat) : Prop :=
  ∀ i ∈ inputs, RoundsTo r i.2 (κ i.1)

instance (r : Rounding) (inputs : List (String × Printed)) (κ : String → Rat) : Decidable (InBox r inputs κ) := by
  unfold InBox; infer_instance

theorem lookup_mem {α : Type} {l : List (String × α)} {n : String} {p : α} (h : l.lookup n = some p) :
    (n, p) ∈ l := by
  induction l with
  | nil => cases h
  | cons hd tl ih =>
    obtain ⟨m, q⟩ := hd
    by_cases hm : n = m
    · subst hm; simp [List.lookup] at h; simp [h]
    · have : (n == m) = false := by simpa using hm
      simp only [List.lookup, this] at h; exact List.mem_cons_of_mem _ (ih h)

theorem enclose_sound (r : Rounding) (inputs : List (String × Printed)) (e : Expr) (lo hi : Rat)
    (h : enclose r inputs e = some (lo, hi)) (κ : String → Rat) (hκ : InBox r inputs κ) (x : Rat)
    (hx : Denotes (fun n => some (κ n)) e x) : lo ≤ x ∧ x ≤ hi := by
  induction e generalizing lo hi x with
  | lit q => cases hx; simp [enclose] at h; grind
  | val n =>
    cases hx with
    | val hn =>
      simp only [Option.some.injEq] at hn; subst hn
      obtain ⟨p, hp, hb⟩ := Option.map_eq_some_iff.mp h
      have := Printed.box_sound r p (κ n) (hκ (n, p) (lookup_mem hp)); rw [hb] at this; exact this
  | add a b iha ihb | sub a b iha ihb | mul a b iha ihb =>
    cases hx; rename_i hxa hxb
    simp only [enclose, bind, Option.bind_eq_some_iff, pure, Option.some.injEq] at h
    obtain ⟨⟨la, ha⟩, hea, ⟨lb, hb⟩, heb, hr⟩ := h
    have := iha la ha hea _ hxa; have := ihb lb hb heb _ hxb
    first
      | (simp only [Interval.add, Interval.sub, Prod.mk.injEq] at hr; grind)
      | (have := Interval.mul_sound (a := (la, ha)) (b := (lb, hb)) ‹_› ‹_›; rw [hr] at this; exact this)
  | div a b iha ihb =>
    cases hx with
    | div hxa hxb hy =>
      simp only [enclose, bind, Option.bind_eq_some_iff, pure, Option.some.injEq] at h
      obtain ⟨⟨la, ha⟩, hea, ⟨lb, hb⟩, heb, ⟨li, hi'⟩, hinv, hr⟩ := h
      have hyi := Interval.inv_sound hinv (ihb lb hb heb _ hxb)
      have := Interval.mul_sound (a := (la, ha)) (iha la ha hea _ hxa) hyi
      rw [hr, ← Rat.div_def] at this; exact this
  | pow a k iha =>
    cases hx with
    | pow hxa =>
      obtain ⟨⟨la, ha⟩, hea, hr⟩ := Option.map_eq_some_iff.mp h
      have := Interval.pow_sound (a := (la, ha)) k (iha la ha hea _ hxa); rw [hr] at this; exact this

/-- An interval computed is charged its endpoints' sizes. -/
def chargeI (limit : Nat) (i : Rat × Rat) (w : Nat) : Option (Option (Rat × Rat) × Nat) :=
  if limit < w + qbits i.1 + qbits i.2 then none else some (some i, w + qbits i.1 + qbits i.2)

/-- Two charged enclosures, in order, combined by `f`; no enclosure on either side gives none. -/
def binI (limit : Nat) (ea eb : Nat → Option (Option (Rat × Rat) × Nat))
    (f : Rat × Rat → Rat × Rat → Option (Rat × Rat)) (w : Nat) : Option (Option (Rat × Rat) × Nat) :=
  visitC limit w fun w => (ea w).bind fun (x, w) => (eb w).bind fun
    | (some y, w) => match x with
      | some x => match f x y with
        | some i => chargeI limit i w
        | none => some (none, w)
      | none => some (none, w)
    | (none, w) => some (none, w)

/-- `enclose`, charged in 3.2's unit: one unit a visit and each endpoint's size, so each node is computed once and
its size paid; none (UNKNOWN) when the units would pass `limit`. A power beyond the digit limit is not computed: no
enclosure. -/
def encloseC (limit : Nat) (r : Rounding) (inputs : List (String × Printed)) :
    Expr → Nat → Option (Option (Rat × Rat) × Nat)
  | .lit q, w => visitC limit w (chargeI limit (q, q))
  | .val n, w => visitC limit w fun w => match inputs.lookup n with
    | some p => chargeI limit (p.box r) w
    | none => some (none, w)
  | .add a b, w => binI limit (encloseC limit r inputs a) (encloseC limit r inputs b)
      (fun x y => some (Interval.add x y)) w
  | .sub a b, w => binI limit (encloseC limit r inputs a) (encloseC limit r inputs b)
      (fun x y => some (Interval.sub x y)) w
  | .mul a b, w => binI limit (encloseC limit r inputs a) (encloseC limit r inputs b)
      (fun x y => some (Interval.mul x y)) w
  | .div a b, w => binI limit (encloseC limit r inputs a) (encloseC limit r inputs b)
      (fun x y => (Interval.inv? y).map (Interval.mul x)) w
  | .pow a k, w => visitC limit w fun w => (encloseC limit r inputs a w).bind fun
    | (some x, w) =>
      if powTooLarge x.1 k || powTooLarge x.2 k then some (none, w) else chargeI limit (Interval.pow x k) w
    | (none, w) => some (none, w)

theorem chargeI_some {limit : Nat} {i : Rat × Rat} {w : Nat} {j : Option (Rat × Rat)} {w' : Nat}
    (h : chargeI limit i w = some (j, w')) : j = some i := by
  unfold chargeI at h; split at h <;> simp_all

theorem binI_some {limit : Nat} {ea eb : Nat → Option (Option (Rat × Rat) × Nat)}
    {f : Rat × Rat → Rat × Rat → Option (Rat × Rat)} {w : Nat} {i : Rat × Rat} {w' : Nat}
    (h : binI limit ea eb f w = some (some i, w')) :
    ∃ x y wa wb wc, ea wa = some (some x, wb) ∧ eb wb = some (some y, wc) ∧ f x y = some i := by
  obtain ⟨_, h⟩ := visitC_some h
  obtain ⟨⟨x, w1⟩, ha, h⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨⟨y, w2⟩, hb, h⟩ := Option.bind_eq_some_iff.mp h
  cases y with
  | none => cases h
  | some y =>
    cases x with
    | none => cases h
    | some x =>
      simp only at h; split at h
      · rename_i j hj; cases chargeI_some h; exact ⟨x, y, _, _, _, ha, hb, hj⟩
      · cases h

/-- A charged enclosure is `enclose`'s. -/
theorem encloseC_some (limit : Nat) (r : Rounding) (inputs : List (String × Printed)) (e : Expr) (w : Nat)
    (i : Rat × Rat) (w' : Nat) (h : encloseC limit r inputs e w = some (some i, w')) : enclose r inputs e = some i := by
  induction e generalizing w i w' with
  | lit q => unfold encloseC at h; obtain ⟨_, h⟩ := visitC_some h; simp [enclose, chargeI_some h]
  | val n =>
    unfold encloseC at h; obtain ⟨_, h⟩ := visitC_some h
    split at h
    · rename_i hp; simp [enclose, hp, chargeI_some h]
    · cases h
  | add a b iha ihb | sub a b iha ihb | mul a b iha ihb | div a b iha ihb =>
    unfold encloseC at h
    obtain ⟨x, y, _, _, _, ha, hb, hf⟩ := binI_some h
    simp only [enclose, iha _ _ _ ha, ihb _ _ _ hb, bind, Option.bind, pure] at hf ⊢
    first | exact hf | (obtain ⟨j, hj, rfl⟩ := Option.map_eq_some_iff.mp hf; simp [hj])
  | pow a k iha =>
    unfold encloseC at h; obtain ⟨_, h⟩ := visitC_some h
    obtain ⟨⟨x, w1⟩, ha, h⟩ := Option.bind_eq_some_iff.mp h
    cases x with
    | none => cases h
    | some x =>
      simp only at h; split at h
      · cases h
      · simp [enclose, iha _ _ _ ha, chargeI_some h]

end VE.Calc
