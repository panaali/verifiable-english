import VE.Calc.Decls

/-! Linear facts over rational unknowns and their Farkas certificates (spec 5, plan 3.4). Separate from the frozen
integer `VE.Order.Lin`: the unknowns range over ℚ and there are no cuts. -/

namespace VE.Calc

/-- A linear form over unknowns with rational coefficients. -/
structure QLin where
  const : Rat
  coeffs : List (String × Rat)
  deriving Repr, DecidableEq

def QLin.eval (κ : String → Rat) (L : QLin) : Rat := L.const + (L.coeffs.map fun p => p.2 * κ p.1).sum
def QLin.scale (w : Rat) (L : QLin) : QLin := ⟨w * L.const, L.coeffs.map fun p => (p.1, w * p.2)⟩
def QLin.add (L M : QLin) : QLin := ⟨L.const + M.const, L.coeffs ++ M.coeffs⟩
def QLin.coeffOf (L : QLin) (n : String) : Rat := ((L.coeffs.filter (·.1 == n)).map (·.2)).sum

/-- A fact `0 ≤ L`, or `0 < L` when strict. -/
structure QFact where
  form : QLin
  strict : Bool
  deriving Repr, DecidableEq

def QFact.Holds (κ : String → Rat) (f : QFact) : Prop :=
  if f.strict then 0 < f.form.eval κ else 0 ≤ f.form.eval κ

instance (κ : String → Rat) (f : QFact) : Decidable (f.Holds κ) := by
  unfold QFact.Holds; split <;> infer_instance

/-- ¬(0 ≤ L) is 0 < −L; ¬(0 < L) is 0 ≤ −L. -/
def QFact.negate (f : QFact) : QFact := ⟨f.form.scale (-1), !f.strict⟩

theorem rsum_append (l m : List Rat) : (l ++ m).sum = l.sum + m.sum := by
  induction l with
  | nil => simp [Rat.zero_add]
  | cons x l ih => simp only [List.cons_append, List.sum_cons, ih]; grind

theorem QLin.eval_scale (κ : String → Rat) (w : Rat) (L : QLin) : (L.scale w).eval κ = w * L.eval κ := by
  have h : ∀ l : List (String × Rat), ((l.map fun p => (p.1, w * p.2)).map fun p => p.2 * κ p.1).sum =
      w * (l.map fun p => p.2 * κ p.1).sum := by
    intro l; induction l with
    | nil => simp
    | cons p l ih => simp only [List.map_cons, List.sum_cons] at *; rw [ih]; grind
  simp only [QLin.eval, QLin.scale, h]; grind

theorem QLin.eval_add (κ : String → Rat) (L M : QLin) : (L.add M).eval κ = L.eval κ + M.eval κ := by
  simp only [QLin.eval, QLin.add, List.map_append, rsum_append]; grind

theorem QFact.negate_holds (κ : String → Rat) (f : QFact) : f.negate.Holds κ ↔ ¬ f.Holds κ := by
  cases hs : f.strict <;> simp [QFact.Holds, QFact.negate, hs, QLin.eval_scale] <;> grind

/-- Nonnegative weights, one per fact, whose combination cancels every unknown. -/
structure Farkas where
  weights : List Rat
  deriving Repr, DecidableEq

def Farkas.combination (fs : List QFact) (c : Farkas) : QLin :=
  (List.zipWith (fun w f => f.form.scale w) c.weights fs).foldl QLin.add ⟨0, []⟩

/-- One nonnegative weight per fact; the combination cancels every unknown and leaves a negative constant, or zero
with a positive weight on a strict fact. -/
def Farkas.check (fs : List QFact) (c : Farkas) : Bool :=
  let comb := c.combination fs
  c.weights.length == fs.length && c.weights.all (fun w => decide (0 ≤ w)) &&
  (comb.coeffs.map (·.1)).all (fun n => comb.coeffOf n == 0) &&
  (decide (comb.const < 0) ||
    (comb.const == 0 && (List.zipWith (fun w f => decide (0 < w) && f.strict) c.weights fs).any id))

theorem QLin.eval_foldl (κ : String → Rat) (acc : QLin) (ls : List QLin) :
    (ls.foldl QLin.add acc).eval κ = acc.eval κ + (ls.map (QLin.eval κ)).sum := by
  induction ls generalizing acc with
  | nil => simp [Rat.add_zero]
  | cons L ls ih => simp only [List.foldl_cons, ih, QLin.eval_add, List.map_cons, List.sum_cons]; grind

/-- The terms of one unknown, and the rest. -/
theorem sum_split (κ : String → Rat) (l : List (String × Rat)) (n : String) :
    (l.map fun p => p.2 * κ p.1).sum = ((l.filter (·.1 == n)).map (·.2)).sum * κ n +
      ((l.filter fun p => !(p.1 == n)).map fun p => p.2 * κ p.1).sum := by
  induction l with
  | nil => simp [Rat.add_zero]
  | cons p l ih => by_cases h : p.1 = n <;> simp [h, ih] <;> grind

/-- A form whose every coefficient cancels evaluates to its constant. -/
theorem QLin.eval_of_cancel (κ : String → Rat) (L : QLin)
    (h : ∀ n ∈ L.coeffs.map (·.1), L.coeffOf n = 0) : L.eval κ = L.const := by
  suffices hs : ∀ (k : Nat) (l : List (String × Rat)), l.length ≤ k →
      (∀ n ∈ l.map (·.1), ((l.filter (·.1 == n)).map (·.2)).sum = 0) → (l.map fun p => p.2 * κ p.1).sum = 0 by
    simp only [QLin.eval, hs _ L.coeffs (Nat.le_refl _) h]; grind
  intro k
  induction k with
  | zero => intro l hl _; simp_all
  | succ k ih =>
    intro l hl hc
    match l with
    | [] => simp
    | p :: rest =>
      rw [sum_split κ _ p.1, hc p.1 (by simp)]
      have hlen : ((p :: rest).filter fun q => !(q.1 == p.1)).length ≤ k := by
        have := List.length_filter_le (fun q : String × Rat => !(q.1 == p.1)) rest
        simp [List.filter_cons] at *; omega
      rw [ih _ hlen ?_]
      · grind
      intro m hm
      obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hm
      have hne : ¬ q.1 = p.1 := by simpa using (List.mem_filter.mp hq).2
      rw [List.filter_filter, List.filter_congr (q := (·.1 == q.1)) (by
        intro r _; by_cases hr : r.1 = q.1 <;> simp [hr, hne])]
      exact hc q.1 (List.mem_map.mpr ⟨q, (List.mem_filter.mp hq).1, rfl⟩)

/-- The weighted sum of the facts' values; nonnegative where the facts hold, and positive with a positive weight on
a strict fact. -/
theorem weighted_nonneg (κ : String → Rat) (ws : List Rat) (fs : List QFact) (hw : ∀ w ∈ ws, 0 ≤ w)
    (hf : ∀ f ∈ fs, f.Holds κ) :
    0 ≤ (List.zipWith (fun w f => w * f.form.eval κ) ws fs).sum ∧
      ((List.zipWith (fun w f => decide (0 < w) && f.strict) ws fs).any id = true →
        0 < (List.zipWith (fun w f => w * f.form.eval κ) ws fs).sum) := by
  induction ws generalizing fs with
  | nil => simp [Rat.le_refl]
  | cons w ws ih =>
    cases fs with
    | nil => simp [Rat.le_refl]
    | cons f fs =>
      have hw0 : 0 ≤ w := hw w (by simp)
      have hf0 := hf f (by simp)
      obtain ⟨h1, h2⟩ := ih fs (fun v hv => hw v (by simp [hv])) (fun g hg => hf g (by simp [hg]))
      have hval : 0 ≤ f.form.eval κ := by
        unfold QFact.Holds at hf0; split at hf0 <;> grind
      have hprod : 0 ≤ w * f.form.eval κ := Rat.mul_nonneg hw0 hval
      simp only [List.zipWith_cons_cons, List.sum_cons, List.any_cons]
      refine ⟨by grind, ?_⟩
      intro hany
      by_cases hs : decide (0 < w) && f.strict
      · simp only [Bool.and_eq_true, decide_eq_true_eq] at hs
        have hpos : 0 < f.form.eval κ := by simpa [QFact.Holds, hs.2] using hf0
        have : 0 < w * f.form.eval κ := Rat.mul_pos hs.1 hpos
        grind
      · simp only [hs] at hany; grind

theorem Farkas.combination_eval (κ : String → Rat) (fs : List QFact) (c : Farkas) :
    (c.combination fs).eval κ = (List.zipWith (fun w f => w * f.form.eval κ) c.weights fs).sum := by
  have hz : ∀ (ws : List Rat) (gs : List QFact),
      (List.zipWith (fun w f => f.form.scale w) ws gs).map (QLin.eval κ) =
        List.zipWith (fun w f => w * f.form.eval κ) ws gs := by
    intro ws; induction ws with
    | nil => simp
    | cons w ws ih => intro gs; cases gs <;> simp [ih, QLin.eval_scale]
  rw [Farkas.combination, QLin.eval_foldl, hz]; simp only [QLin.eval, List.map_nil, List.sum_nil]; grind

theorem Farkas.check_sound (fs : List QFact) (c : Farkas) (h : c.check fs = true) :
    ∀ κ : String → Rat, ¬ ∀ f ∈ fs, f.Holds κ := by
  intro κ hall
  simp only [Farkas.check, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq, beq_iff_eq,
    Bool.or_eq_true] at h
  obtain ⟨⟨⟨_, hw⟩, hcancel⟩, hconst⟩ := h
  have heval := QLin.eval_of_cancel κ _ hcancel
  rw [Farkas.combination_eval] at heval
  obtain ⟨h1, h2⟩ := weighted_nonneg κ c.weights fs hw hall
  rcases hconst with hneg | ⟨hzero, hany⟩
  · grind
  · have := h2 hany; grind

/-- The proved square rule (plan D11). -/
theorem lt_of_sq_lt (x a b : Rat) (hx : 0 ≤ x) (hb : 0 < b) (h : x * x < a) (hab : a ≤ b * b) : x < b := by
  apply Classical.byContradiction
  intro hn
  have hbx : b ≤ x := by grind
  have h1 : b * b ≤ b * x := Rat.mul_le_mul_of_nonneg_left hbx (by grind)
  have h2 : b * x ≤ x * x := Rat.mul_le_mul_of_nonneg_right hbx hx
  grind

end VE.Calc
