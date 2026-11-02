import VE.Calc.Interval
import VE.Calc.Inline
import VE.Calc.Stats

/-! Consistency of printed numbers (math-evidence spec 8.1, ME-8): the one proposition `Consistent` (statement review
J4), a witness that establishes it and an enclosure or a granularity that refutes it, all over the outputs inlined
with the inputs kept (2.7); GRIM (`mean_grain_refutes`) and the sign-flip granularity (`signFlip_grain_refutes`). -/

namespace VE.Calc
open VE.Numbers

/-- The meaning of a consistency check (J4). -/
def Consistent (ds : List Decl) (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim) : Prop :=
  ∃ κ : String → Rat, InBox r inputs κ ∧ ∀ c ∈ outs, c.Holds (values (assign ds (inputs.map Prod.fst) κ))

/-- A witness for inlined outputs: a value for every input, inside its interval, under which every output holds. -/
def witnessCheck (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim)
    (w : List (String × Rat)) : Bool :=
  inputs.all (fun i => match w.lookup i.1 with
    | some x => decide (RoundsTo r i.2 x)
    | none => false) &&
  outs.all fun c => c.decide (fun n => w.lookup n) == .holds

/-- No pair of points of the two intervals is in the relation. -/
def _root_.VE.Numbers.Rel.misses : Rel → Rat × Rat → Rat × Rat → Bool
  | .eq, x, y => Decidable.decide (x.2 < y.1 ∨ y.2 < x.1)
  | .lt, x, y => Decidable.decide (y.2 ≤ x.1)
  | .le, x, y => Decidable.decide (y.2 < x.1)

/-- An output whose sides' enclosures, in `Claim.exprs`' order, show it false at every point. -/
def Claim.misses : Claim → List (Option (Rat × Rat)) → Bool
  | .compare c _ _, [some x, some y] => if c.swap then c.rel.misses y x else c.rel.misses x y
  | .within .., [some x, some l, some h] => Decidable.decide (x.2 < l.1 ∨ h.2 < x.1 ∨ h.2 < l.1)
  | .rounds r _ p, [some x] => Decidable.decide (x.2 < (p.box r).1 ∨ (p.box r).2 < x.1)
  | _, _ => false

/-- *Opaque* in spec 8.1: an inlined output whose enclosures show it false at every point of the input intervals. -/
def refuteByEnclosure (r : Rounding) (inputs : List (String × Printed)) (c : Claim) : Bool :=
  c.misses (c.exprs.map (enclose r inputs))

/-- *Opaque* in spec 8.1: an inlined output `rounds r' (.stat .signFlip xs) p` with `grainRefutes (2 ^ xs.length) r' p`.
`Expr` has no `.stat` yet (me-7b), so no claim carries a sign-flip p and none is refuted here; the arm comes with it. -/
def refuteByGrain (_ : Claim) : Bool := false

theorem refuteByEnclosure_sound (r : Rounding) (inputs : List (String × Printed)) (c : Claim)
    (h : refuteByEnclosure r inputs c = true) (κ : String → Rat) (hκ : InBox r inputs κ) :
    ¬ c.Holds (fun n => some (κ n)) := by
  have hs := fun e lo hi he x hx => enclose_sound r inputs e lo hi he κ hκ x hx
  cases c with
  | compare k a b =>
    rintro ⟨x, y, hx, hy, hk⟩
    simp only [refuteByEnclosure, Claim.exprs, List.map] at h
    cases ha : enclose r inputs a with
    | none => simp [ha, Claim.misses] at h
    | some A =>
      cases hb : enclose r inputs b with
      | none => simp [ha, hb, Claim.misses] at h
      | some B =>
        have := hs a A.1 A.2 ha x hx; have := hs b B.1 B.2 hb y hy
        obtain ⟨rel, swap⟩ := k
        cases rel <;> cases swap <;>
          simp_all [Claim.misses, Rel.misses, Comparison.Holds, Rel.Holds] <;> grind
  | within e lo hi =>
    rintro ⟨x, l, u, hx, hl, hu, h1, h2⟩
    simp only [refuteByEnclosure, Claim.exprs, List.map] at h
    cases he : enclose r inputs e <;> cases hle : enclose r inputs lo <;> cases hhi : enclose r inputs hi <;>
      simp only [he, hle, hhi, Claim.misses, decide_eq_true_eq, Bool.false_eq_true] at h
    rename_i X L U
    have := hs e X.1 X.2 he x hx; have := hs lo L.1 L.2 hle l hl; have := hs hi U.1 U.2 hhi u hu; grind
  | rounds r' e p =>
    rintro ⟨x, hx, hr⟩
    simp only [refuteByEnclosure, Claim.exprs, List.map] at h
    cases he : enclose r inputs e <;> simp only [he, Claim.misses, decide_eq_true_eq, Bool.false_eq_true] at h
    rename_i X
    have := hs e X.1 X.2 he x hx; have := Printed.box_sound r' p x hr; grind

theorem refuteByGrain_sound (c : Claim) (h : refuteByGrain c = true) (σ : Values) : ¬ c.Holds σ := by
  simp [refuteByGrain] at h

theorem mapM_ok_mem {α β ε : Type} {f : α → Except ε β} {xs : List α} {ys : List β} (h : xs.mapM f = .ok ys) :
    (∀ x ∈ xs, ∃ y ∈ ys, f x = .ok y) ∧ (∀ y ∈ ys, ∃ x ∈ xs, f x = .ok y) := by
  induction xs generalizing ys with
  | nil => simp only [List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h; subst h; simp
  | cons x xs ih =>
    simp only [List.mapM_cons, bind, Except.bind, pure, Except.pure] at h
    cases hx : f x with
    | error e => simp [hx] at h
    | ok y =>
      cases hr : xs.mapM f with
      | error e => simp [hx, hr] at h
      | ok ys' =>
        simp only [hx, hr, Except.ok.injEq] at h; subst h
        obtain ⟨ih1, ih2⟩ := ih hr
        refine ⟨fun z hz => ?_, fun z hz => ?_⟩
        · rcases List.mem_cons.mp hz with rfl | hz
          · exact ⟨y, by simp, hx⟩
          · obtain ⟨u, hu, hfu⟩ := ih1 z hz; exact ⟨u, by simp [hu], hfu⟩
        · rcases List.mem_cons.mp hz with rfl | hz
          · exact ⟨x, by simp, hx⟩
          · obtain ⟨u, hu, hfu⟩ := ih2 z hz; exact ⟨u, by simp [hu], hfu⟩

/-- An inlined claim reads only kept names. -/
theorem Claim.inline_names (ds : List Decl) (keep : List String) (c c' : Claim) (hc : c.inline ds keep = .ok c') :
    ∀ e ∈ c'.exprs, ∀ n ∈ e.names, n ∈ keep := by
  have hn := fun e e' (he : e.inline ds keep = .ok e') => Expr.inline_names ds keep e e' he
  cases c <;> simp only [Claim.inline, Claim.subst, bind, Except.bind, pure, Except.pure] at hc <;>
    (repeat' split at hc) <;> simp only [reduceCtorEq, Except.ok.injEq] at hc <;> subst hc <;>
    simp only [Claim.exprs, List.mem_cons, List.not_mem_nil, or_false] <;> rintro e (rfl | rfl | rfl) <;>
    first | exact hn _ _ ‹_› | (rename_i h; exact hn _ _ h)

theorem Claim.decide_congr_on (c : Claim) (σ τ : Values) (h : ∀ e ∈ c.exprs, ∀ n ∈ e.names, σ n = τ n) :
    c.decide σ = c.decide τ := by
  have he := fun e (m : e ∈ c.exprs) => Expr.eval_congr_on e σ τ (h e m)
  cases c with
  | compare k a b => simp only [Claim.decide]; rw [he a (by simp [Claim.exprs]), he b (by simp [Claim.exprs])]
  | within e lo hi =>
    simp only [Claim.decide]
    rw [he e (by simp [Claim.exprs]), he lo (by simp [Claim.exprs]), he hi (by simp [Claim.exprs])]
  | rounds r e p => simp only [Claim.decide]; rw [he e (by simp [Claim.exprs])]

/-- The witness establishes the one proposition, over one lowering. -/
theorem consistent_of_witness (ds : List Decl) (h : WellFormed ds) (r : Rounding)
    (inputs : List (String × Printed)) (hk : ∀ i ∈ inputs, i.1 ∈ ds.map Decl.name) (outs outs' : List Claim)
    (hl : outs.mapM (Claim.inline ds (inputs.map Prod.fst)) = .ok outs') (w : List (String × Rat))
    (hw : witnessCheck r inputs outs' w = true) : Consistent ds r inputs outs := by
  simp only [witnessCheck, Bool.and_eq_true, List.all_eq_true, beq_iff_eq] at hw
  obtain ⟨hin, hout⟩ := hw
  have hlk : ∀ i ∈ inputs, ∃ x, w.lookup i.1 = some x ∧ RoundsTo r i.2 x := fun i hi => by
    have := hin i hi; split at this <;> simp_all
  let κ : String → Rat := fun n => (w.lookup n).getD 0
  refine ⟨κ, fun i hi => ?_, fun c hc => ?_⟩
  · obtain ⟨x, hx, hr⟩ := hlk i hi; simpa [κ, hx] using hr
  · obtain ⟨c', hc', hi⟩ := (mapM_ok_mem hl).1 c hc
    have hk' : ∀ n ∈ inputs.map Prod.fst, n ∈ ds.map Decl.name := fun n hn => by
      obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hn; exact hk i hi
    rw [Claim.inline_sound ds h _ hk' c c' hi κ, ← Claim.decide_holds]
    rw [Claim.decide_congr_on c' _ (fun n => w.lookup n) fun e he n hn => ?_]
    · exact hout c' hc'
    · obtain ⟨i, hi, rfl⟩ := List.mem_map.mp (Claim.inline_names ds _ c c' hi e he n hn)
      obtain ⟨x, hx, _⟩ := hlk i hi; simp [κ, hx]

/-- An enclosure that misses an inlined output, or a sign-flip granularity refutation, refutes the same proposition. -/
theorem inconsistent_of_refutation (ds : List Decl) (h : WellFormed ds) (r : Rounding)
    (inputs : List (String × Printed)) (hk : ∀ i ∈ inputs, i.1 ∈ ds.map Decl.name) (outs outs' : List Claim)
    (hl : outs.mapM (Claim.inline ds (inputs.map Prod.fst)) = .ok outs') (c : Claim) (hc : c ∈ outs')
    (hr : refuteByEnclosure r inputs c = true ∨ refuteByGrain c = true) : ¬ Consistent ds r inputs outs := by
  rintro ⟨κ, hbox, hall⟩
  obtain ⟨c0, hc0, hi⟩ := (mapM_ok_mem hl).2 c hc
  have hk' : ∀ n ∈ inputs.map Prod.fst, n ∈ ds.map Decl.name := fun n hn => by
    obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hn; exact hk i hi
  have hholds := (Claim.inline_sound ds h _ hk' c0 c hi κ).mp (hall c0 hc0)
  rcases hr with hr | hr
  · exact refuteByEnclosure_sound r inputs c hr κ hbox hholds
  · exact refuteByGrain_sound c hr _ hholds

/-- No multiple of `1/g` rounds to `p` under `r` (the candidates are the multiples near p's interval). -/
def grainRefutes (g : Nat) (r : Rounding) (p : Printed) : Bool :=
  let u := tenPow p.places
  let a := Rat.floor ((p.digits - 1 : Rat) / u * g) - 1
  let b := Rat.ceil ((p.digits + 1 : Rat) / u * g) + 1
  (List.range (b - a + 1).toNat).all fun i => !decide (RoundsTo r p (((a + i : Int) : Rat) / g))

/-- Every rule's interval lies within one unit of the last place. -/
theorem roundsTo_near (r : Rounding) (p : Printed) (x : Rat) (h : RoundsTo r p x) :
    (p.digits : Rat) - 1 ≤ x * tenPow p.places ∧ x * tenPow p.places ≤ p.digits + 1 := by
  cases r <;> simp only [RoundsTo] at h <;> grind

theorem grain_sound (g : Nat) (hg : 0 < g) (r : Rounding) (p : Printed) (h : grainRefutes g r p = true) :
    ∀ m : Int, ¬ RoundsTo r p ((m : Rat) / g) := by
  intro m hm
  have hu := tenPow_pos p.places
  have hg' : (0 : Rat) < g := by exact_mod_cast hg
  obtain ⟨h1, h2⟩ := roundsTo_near r p _ hm
  -- (D ∓ 1) / u * g brackets m: multiply the bounds on m / g * u by g / u.
  have hc : (0 : Rat) ≤ g * (tenPow p.places)⁻¹ := Rat.le_of_lt (by
    have := Rat.inv_pos.mpr hu; exact Rat.mul_pos hg' this)
  have e1 : (m : Rat) / g * tenPow p.places * (g * (tenPow p.places)⁻¹) = m := by
    rw [Rat.div_def]; have : (g : Rat) ≠ 0 := Rat.ne_of_gt hg'; have : tenPow p.places ≠ 0 := Rat.ne_of_gt hu
    grind
  have hlo := Rat.mul_le_mul_of_nonneg_right h1 hc
  have hhi := Rat.mul_le_mul_of_nonneg_right h2 hc
  rw [e1] at hlo hhi
  have ea : ((p.digits : Rat) - 1) * (g * (tenPow p.places)⁻¹) = (p.digits - 1 : Rat) / tenPow p.places * g := by
    rw [Rat.div_def]; grind
  have eb : ((p.digits : Rat) + 1) * (g * (tenPow p.places)⁻¹) = (p.digits + 1 : Rat) / tenPow p.places * g := by
    rw [Rat.div_def]; grind
  rw [ea] at hlo; rw [eb] at hhi
  have fa := Rat.floor_le ((p.digits - 1 : Rat) / tenPow p.places * g)
  have fb := Rat.floor_le (-((p.digits + 1 : Rat) / tenPow p.places * g))
  have ha : Rat.floor ((p.digits - 1 : Rat) / tenPow p.places * g) ≤ m :=
    Rat.intCast_le_intCast.mp (Rat.le_trans fa hlo)
  have hb : m ≤ Rat.ceil ((p.digits + 1 : Rat) / tenPow p.places * g) := by
    rw [Rat.ceil_eq_neg_floor_neg]
    have : ((-(Rat.floor (-((p.digits + 1 : Rat) / tenPow p.places * g))) : Int) : Rat) ≥ (m : Rat) := by
      push_cast; grind
    exact Rat.intCast_le_intCast.mp this
  simp only [grainRefutes, List.all_eq_true, List.mem_range, Bool.not_eq_true', decide_eq_false_iff_not] at h
  have := h (m - (Rat.floor ((p.digits - 1 : Rat) / tenPow p.places * g) - 1)).toNat (by omega)
  rw [Int.toNat_of_nonneg (by omega), Int.add_comm, Int.sub_add_cancel] at this
  exact this hm

/-- Granularity of sign-flip p values (uses ME-7's `signFlipP_grain`, hence ME-7 → ME-8). -/
theorem signFlip_grain_refutes (d : List Rat) (r : Rounding) (p : Printed)
    (h : grainRefutes (2 ^ d.length) r p = true) : ¬ RoundsTo r p (signFlipP d) := by
  obtain ⟨m, _, hm⟩ := signFlipP_grain d
  have := grain_sound _ (Nat.pow_pos (by decide)) r p h m
  rw [hm]; simpa using this

theorem sum_intCast (xs : List Int) : (xs.map fun (x : Int) => (x : Rat)).sum = ((xs.sum : Int) : Rat) := by
  induction xs with
  | nil => simp
  | cons x xs ih => simp [ih]

/-- GRIM: the mean of n integers is a multiple of 1/n. -/
theorem mean_grain_refutes (xs : List Int) (hx : xs ≠ []) (r : Rounding) (p : Printed)
    (h : grainRefutes xs.length r p = true) :
    ¬ RoundsTo r p ((xs.map fun (x : Int) => (x : Rat)).sum / xs.length) := by
  rw [sum_intCast]; exact grain_sound _ (List.length_pos_iff.mpr hx) r p h _

end VE.Calc
