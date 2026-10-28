import VE.Arith.Holds
import VE.Arith.Defs
import VE.Time.Budget

/-! The budget (spec 12.2, draft 5; me-12n): one unit per node visit, term and formula nodes alike, as W6's
`VE.Time.evalB` charges a formula node; a call, of a function or a predicate, is one visit plus its arguments' and its
body's. Every value a term yields, and every value a range step binds, is also charged its size (`bits`), so the
units bound the size of every value and the work done on it (`Term.evalB_bits`). `decideBounded` is this evaluator
from no work spent; when it completes, its answer is the meaning's (`decideBounded_sound`), so the budget only turns
an answer into unknown. -/

namespace VE.Arith
open VE.Numbers

/-- The size of a value: the bit length of its magnitude, and 1 for 0. -/
def bits (x : Int) : Nat := x.natAbs.log2 + 1

def charge {α : Type} (limit w : Nat) (k : Nat → Option (α × Nat)) : Option (α × Nat) :=
  if limit ≤ w then none else k (w + 1)

/-- A value is charged its size once it is computed: refused (none) when the units would pass the budget. -/
def chargeBits (limit : Nat) (x : Int) (w : Nat) : Option (Int × Nat) :=
  if limit < w + bits x then none else some (x, w + bits x)

/-- A range step charges the size of the value it binds, then visits the condition at that value. -/
def stepB (limit : Nat) (cond : Int → Nat → Option (Bool × Nat)) (i : Int) (w : Nat) : Option (Bool × Nat) :=
  (chargeBits limit i w).bind fun r => cond i r.2

def quantLoop (universal : Bool) (step : Int → Nat → Option (Bool × Nat)) :
    Nat → Int → Nat → Option (Bool × Nat)
  | 0, _, w => some (universal, w)
  | n + 1, i, w => match step i w with
    | none => none
    | some (b, w') => if b = universal then quantLoop universal step n (i + 1) w' else some (!universal, w')

def countLoop (step : Int → Nat → Option (Bool × Nat)) : Nat → Int → Nat → Nat → Option (Int × Nat)
  | 0, _, acc, w => some ((acc : Int), w)
  | n + 1, i, acc, w => match step i w with
    | none => none
    | some (b, w') => countLoop step n (i + 1) (if b then acc + 1 else acc) w'

structure OpEnv where
  funs : String → Option (Nat × (List Int → Nat → Option (Int × Nat)))
  preds : String → Option (Nat × (List Int → Nat → Option (Bool × Nat)))

mutual
def Term.evalB (E : OpEnv) (limit : Nat) (ρ : List Int) : Term → Nat → Option (Int × Nat)
  | .var i, w => charge limit w fun w => (ρ[i]?).bind fun x => chargeBits limit x w
  | .num n, w => charge limit w fun w => chargeBits limit n w
  | .add a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).bind fun r => chargeBits limit (x + r.1) r.2
  | .sub a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).bind fun r => chargeBits limit (x - r.1) r.2
  | .mul a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).bind fun r => chargeBits limit (x * r.1) r.2
  | .call f args, w => charge limit w fun w => match E.funs f with
    | none => none
    | some (n, g) => match Term.evalBs E limit ρ args w with
      | none => none
      | some (xs, w) => if xs.length = n then (g xs w).bind fun r => chargeBits limit r.1 r.2 else none
  | .countFromTo lo hi φ, w => charge limit w fun w => match Term.evalB E limit ρ lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit ρ hi w with
      | none => none
      | some (h, w) => (countLoop (stepB limit fun i w => Formula.evalB E limit (i :: ρ) φ w)
          (h - l + 1).toNat l 0 w).bind fun r => chargeBits limit r.1 r.2
def Term.evalBs (E : OpEnv) (limit : Nat) (ρ : List Int) : List Term → Nat → Option (List Int × Nat)
  | [], w => some ([], w)
  | t :: ts, w => match Term.evalB E limit ρ t w with
    | none => none
    | some (x, w) => (Term.evalBs E limit ρ ts w).map fun r => (x :: r.1, r.2)
def Formula.evalB (E : OpEnv) (limit : Nat) (ρ : List Int) : Formula → Nat → Option (Bool × Nat)
  | .eq a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x = r.1), r.2)
  | .lt a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x < r.1), r.2)
  | .le a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x ≤ r.1), r.2)
  | .dvd a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x ∣ r.1), r.2)
  | .call p args, w => charge limit w fun w => match E.preds p with
    | none => none
    | some (n, P) => match Term.evalBs E limit ρ args w with
      | none => none
      | some (xs, w) => if xs.length = n then P xs w else none
  | .not φ, w => charge limit w fun w => (Formula.evalB E limit ρ φ w).map fun r => (!r.1, r.2)
  | .and φ ψ, w => charge limit w fun w => match Formula.evalB E limit ρ φ w with
    | none => none
    | some (true, w) => Formula.evalB E limit ρ ψ w
    | some (false, w) => some (false, w)
  | .or φ ψ, w => charge limit w fun w => match Formula.evalB E limit ρ φ w with
    | none => none
    | some (true, w) => some (true, w)
    | some (false, w) => Formula.evalB E limit ρ ψ w
  | .imp φ ψ, w => charge limit w fun w => match Formula.evalB E limit ρ φ w with
    | none => none
    | some (true, w) => Formula.evalB E limit ρ ψ w
    | some (false, w) => some (true, w)
  | .allNat _, _ => none
  | .exNat _, _ => none
  | .allInt _, _ => none
  | .exInt _, _ => none
  | .allFromTo lo hi φ, w => charge limit w fun w => match Term.evalB E limit ρ lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit ρ hi w with
      | none => none
      | some (h, w) => quantLoop true (stepB limit fun i w => Formula.evalB E limit (i :: ρ) φ w) (h - l + 1).toNat l w
  | .exFromTo lo hi φ, w => charge limit w fun w => match Term.evalB E limit ρ lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit ρ hi w with
      | none => none
      | some (h, w) => quantLoop false (stepB limit fun i w => Formula.evalB E limit (i :: ρ) φ w) (h - l + 1).toNat l w
end

def Defs.opEnv (limit : Nat) (D : Defs) : OpEnv :=
  D.foldl (fun E d => match d with
    | .fn f n body => { E with funs := fun g => if g = f then some (n, fun xs w => Term.evalB E limit xs body w) else E.funs g }
    | .pred p n body => { E with preds := fun q => if q = p then some (n, fun xs w => Formula.evalB E limit xs body w) else E.preds q })
    ⟨fun _ => none, fun _ => none⟩

def maxSteps : Nat := VE.Time.maxEvaluations

/-- The value and the units spent, or none (UNKNOWN). -/
def decideBounded (D : Defs) (limit : Nat) (φ : Formula) : Option (Bool × Nat) :=
  Formula.evalB (D.opEnv limit) limit [] φ 0

/-- A statement's row. An unbounded statement is classified before any evaluation. -/
def arithOutcome (D : Defs) (limit : Nat) (φ : Formula) : Outcome :=
  if φ.Bounded D then
    match decideBounded D limit φ with
    | some (true, _) => .decided .holds
    | some (false, _) => .decided .fails
    | none => .unknown (.limit .evaluations)
  else .unknown .unboundedStatement

/-! Proofs: the loops, then the evaluator against the meaning, through an agreement of environments. -/

open Classical in
theorem quantLoop_true (Q : Int → Prop) (step : Int → Nat → Option (Bool × Nat)) (limit : Nat)
    (hs : ∀ i w b w', step i w = some (b, w') → (Q i ↔ b = true) ∧ (w ≤ limit → w' ≤ limit)) :
    ∀ n i w b w', quantLoop true step n i w = some (b, w') →
      (b = true ↔ ∀ k : Nat, k < n → Q (i + k)) ∧ (w ≤ limit → w' ≤ limit)
  | 0, i, w, b, w', h => by
    simp only [quantLoop, Option.some.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    simp
  | n + 1, i, w, b, w', h => by
    simp only [quantLoop] at h
    cases hst : step i w with
    | none => simp [hst] at h
    | some r =>
      obtain ⟨b0, w0⟩ := r
      have ⟨hq, hw⟩ := hs i w b0 w0 hst
      cases b0 with
      | true =>
        simp only [hst, ite_true] at h
        have ⟨ih, ihw⟩ := quantLoop_true Q step limit hs n (i + 1) w0 b w' h
        refine ⟨ih.trans ⟨fun H k hk => ?_, fun H k hk => ?_⟩, fun h0 => ihw (hw h0)⟩
        · cases k with
          | zero => simpa using hq.mpr rfl
          | succ k => have := H k (by omega); rwa [show i + 1 + (k : Int) = i + ((k + 1 : Nat) : Int) by omega] at this
        · have := H (k + 1) (by omega); rwa [show i + ((k + 1 : Nat) : Int) = i + 1 + (k : Int) by omega] at this
      | false =>
        simp only [hst] at h
        simp at h hq
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨by simp; exact ⟨0, by omega, by simpa using hq⟩, hw⟩

theorem quantLoop_false (Q : Int → Prop) (step : Int → Nat → Option (Bool × Nat)) (limit : Nat)
    (hs : ∀ i w b w', step i w = some (b, w') → (Q i ↔ b = true) ∧ (w ≤ limit → w' ≤ limit)) :
    ∀ n i w b w', quantLoop false step n i w = some (b, w') →
      (b = true ↔ ∃ k : Nat, k < n ∧ Q (i + k)) ∧ (w ≤ limit → w' ≤ limit)
  | 0, i, w, b, w', h => by
    simp only [quantLoop, Option.some.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    simp
  | n + 1, i, w, b, w', h => by
    simp only [quantLoop] at h
    cases hst : step i w with
    | none => simp [hst] at h
    | some r =>
      obtain ⟨b0, w0⟩ := r
      have ⟨hq, hw⟩ := hs i w b0 w0 hst
      cases b0 with
      | false =>
        simp only [hst, ite_true] at h
        have ⟨ih, ihw⟩ := quantLoop_false Q step limit hs n (i + 1) w0 b w' h
        refine ⟨ih.trans ⟨fun ⟨k, hk, H⟩ => ⟨k + 1, by omega, ?_⟩, fun ⟨k, hk, H⟩ => ?_⟩, fun h0 => ihw (hw h0)⟩
        · rwa [show i + ((k + 1 : Nat) : Int) = i + 1 + (k : Int) by omega]
        · cases k with
          | zero => simp at hq H; exact absurd H hq
          | succ k => exact ⟨k, by omega, by rwa [show i + 1 + (k : Int) = i + ((k + 1 : Nat) : Int) by omega]⟩
      | true =>
        simp only [hst] at h
        simp at h hq
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨by simp; exact ⟨0, by omega, by simpa using hq⟩, hw⟩

open Classical in
theorem countLoop_sound (Q : Int → Prop) (step : Int → Nat → Option (Bool × Nat)) (limit : Nat)
    (hs : ∀ i w b w', step i w = some (b, w') → (Q i ↔ b = true) ∧ (w ≤ limit → w' ≤ limit)) :
    ∀ n i acc w c w', countLoop step n i acc w = some (c, w') →
      c = ((acc + ((List.range n).filter fun k : Nat => decide (Q (i + k))).length : Nat) : Int) ∧
        (w ≤ limit → w' ≤ limit)
  | 0, i, acc, w, c, w', h => by
    simp only [countLoop, Option.some.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    simp
  | n + 1, i, acc, w, c, w', h => by
    simp only [countLoop] at h
    cases hst : step i w with
    | none => simp [hst] at h
    | some r =>
      obtain ⟨b0, w0⟩ := r
      have ⟨hq, hw⟩ := hs i w b0 w0 hst
      simp only [hst] at h
      have ⟨ih, ihw⟩ := countLoop_sound Q step limit hs n (i + 1) _ w0 c w' h
      refine ⟨?_, fun h0 => ihw (hw h0)⟩
      rw [ih, List.range_succ_eq_map, List.filter_cons, List.filter_map]
      have hf : ((fun k : Nat => decide (Q (i + k))) ∘ Nat.succ) = fun k : Nat => decide (Q (i + 1 + k)) := by
        funext k; simp only [Function.comp]; congr 2; omega
      rw [hf]
      cases b0 <;> simp at hq <;> simp [hq] <;> omega

theorem range_all (l h : Int) (Q : Int → Prop) :
    (∀ k : Nat, k < (h - l + 1).toNat → Q (l + k)) ↔ ∀ i : Int, l ≤ i → i ≤ h → Q i :=
  ⟨fun H i h1 h2 => by have := H (i - l).toNat (by omega); rwa [show l + ((i - l).toNat : Int) = i by omega] at this,
   fun H k hk => H _ (by omega) (by omega)⟩

theorem range_ex (l h : Int) (Q : Int → Prop) :
    (∃ k : Nat, k < (h - l + 1).toNat ∧ Q (l + k)) ↔ ∃ i : Int, l ≤ i ∧ i ≤ h ∧ Q i :=
  ⟨fun ⟨k, hk, H⟩ => ⟨_, by omega, by omega, H⟩,
   fun ⟨i, h1, h2, H⟩ => ⟨(i - l).toNat, by omega, by rwa [show l + ((i - l).toNat : Int) = i by omega]⟩⟩

/-- An evaluator environment agrees with a meaning environment: each name has the same arity, a completed call gives
the meaning's value, and its work stays within the limit. -/
structure Agrees (E : Env) (O : OpEnv) (limit : Nat) : Prop where
  funs : ∀ f n g, O.funs f = some (n, g) → ∃ g', E.funs f = some (n, g') ∧
    ∀ xs w x w', g xs w = some (x, w') → g' xs = some x ∧ (w ≤ limit → w' ≤ limit)
  preds : ∀ p n P, O.preds p = some (n, P) → ∃ P', E.preds p = some (n, P') ∧
    ∀ xs w b w', P xs w = some (b, w') → (P' xs ↔ b = true) ∧ (w ≤ limit → w' ≤ limit)

theorem charge_some {α : Type} {limit w : Nat} {k : Nat → Option (α × Nat)} {r : α × Nat}
    (h : charge limit w k = some r) : w < limit ∧ k (w + 1) = some r := by
  unfold charge at h; split at h <;> simp_all

theorem chargeBits_some {limit w : Nat} {x y : Int} {w' : Nat} (h : chargeBits limit x w = some (y, w')) :
    y = x ∧ w' = w + bits x ∧ w + bits x ≤ limit := by
  unfold chargeBits at h; split at h
  · simp at h
  · simp only [Option.some.injEq, Prod.mk.injEq] at h; omega

theorem chargeBits_bits {limit w : Nat} {x y : Int} {w' : Nat} (h : chargeBits limit x w = some (y, w')) :
    bits y ≤ limit ∧ w' ≤ limit := by
  obtain ⟨rfl, rfl, h⟩ := chargeBits_some h; omega

/-- Every value a term yields within budget `limit` has at most `limit` bits, in any environment (draft 5). -/
theorem Term.evalB_bits (E : OpEnv) (limit : Nat) (ρ : List Int) (t : Term) (w : Nat) (x : Int) (w' : Nat)
    (h : Term.evalB E limit ρ t w = some (x, w')) : bits x ≤ limit ∧ w' ≤ limit := by
  cases t <;> simp only [Term.evalB, charge] at h <;>
    repeat' (first | (split at h) | (rw [Option.bind_eq_some_iff] at h; obtain ⟨_, _, h⟩ := h))
  all_goals first | (simp at h; done) | exact chargeBits_bits h

theorem log2_le_of_lt {n k : Nat} (h : n < 2 ^ (k + 1)) : n.log2 ≤ k := by
  by_cases hn : n = 0
  · subst hn; simp [Nat.log2_zero]
  · exact Nat.lt_succ_iff.1 ((Nat.log2_lt hn).2 h)

theorem bits_natAbs_le {x : Int} {n k : Nat} (hx : x.natAbs ≤ n) (h : n < 2 ^ (k + 1)) : bits x ≤ k + 1 := by
  have := log2_le_of_lt (n := x.natAbs) (k := k) (by omega)
  unfold bits; omega

/-! The one value computed beyond the budget, whose charge is refused, is built from operands within it. -/

theorem bits_add_le (x y : Int) : bits (x + y) ≤ max (bits x) (bits y) + 1 := by
  have hx := Nat.lt_log2_self (n := x.natAbs)
  have hy := Nat.lt_log2_self (n := y.natAbs)
  have hm1 : 2 ^ (x.natAbs.log2 + 1) ≤ 2 ^ (max (bits x) (bits y)) :=
    Nat.pow_le_pow_right (by omega) (by simp only [bits]; omega)
  have hm2 : 2 ^ (y.natAbs.log2 + 1) ≤ 2 ^ (max (bits x) (bits y)) :=
    Nat.pow_le_pow_right (by omega) (by simp only [bits]; omega)
  exact bits_natAbs_le (Int.natAbs_add_le x y) (by rw [Nat.pow_succ]; omega)

theorem bits_sub_le (x y : Int) : bits (x - y) ≤ max (bits x) (bits y) + 1 := by
  have := bits_add_le x (-y)
  simpa [Int.sub_eq_add_neg, bits, Int.natAbs_neg] using this

theorem bits_mul_le (x y : Int) : bits (x * y) ≤ bits x + bits y := by
  have hx := Nat.lt_log2_self (n := x.natAbs)
  have hy := Nat.lt_log2_self (n := y.natAbs)
  have := bits_natAbs_le (k := x.natAbs.log2 + y.natAbs.log2 + 1) (Nat.le_of_eq (Int.natAbs_mul x y))
    (calc x.natAbs * y.natAbs < 2 ^ (x.natAbs.log2 + 1) * 2 ^ (y.natAbs.log2 + 1) := Nat.mul_lt_mul'' hx hy
      _ = 2 ^ (x.natAbs.log2 + y.natAbs.log2 + 1 + 1) := by rw [← Nat.pow_add]; congr 1; omega)
  unfold bits at this ⊢; omega

theorem stepB_some {limit : Nat} {cond : Int → Nat → Option (Bool × Nat)} {i : Int} {w : Nat} {r : Bool × Nat}
    (h : stepB limit cond i w = some r) : w + bits i ≤ limit ∧ cond i (w + bits i) = some r := by
  unfold stepB chargeBits at h; split at h
  · simp at h
  · exact ⟨by omega, by simpa using h⟩

/-- A step agrees with `Q` and keeps the work within the limit when its condition does. -/
theorem stepB_sound {Q : Int → Prop} {limit : Nat} {cond : Int → Nat → Option (Bool × Nat)}
    (hs : ∀ i w b w', cond i w = some (b, w') → (Q i ↔ b = true) ∧ (w ≤ limit → w' ≤ limit)) :
    ∀ i w b w', stepB limit cond i w = some (b, w') → (Q i ↔ b = true) ∧ (w ≤ limit → w' ≤ limit) :=
  fun _ _ _ _ h => have ⟨hw, h⟩ := stepB_some h; ⟨(hs _ _ _ _ h).1, fun _ => (hs _ _ _ _ h).2 hw⟩

mutual
theorem Term.evalB_sound {E : Env} {O : OpEnv} {limit : Nat} (hA : Agrees E O limit) :
    ∀ (t : Term) (ρ : List Int) (w : Nat) (x : Int) (w' : Nat), Term.evalB O limit ρ t w = some (x, w') →
      Term.value E ρ t = some x ∧ (w ≤ limit → w' ≤ limit)
  | .var i, ρ, w, x, w', h => by
    have hk := fun _ : w ≤ limit => (Term.evalB_bits O limit ρ _ w x w' h).2
    simp only [Term.evalB] at h
    have ⟨_, h⟩ := charge_some h
    cases hi : ρ[i]? with
    | none => simp [hi] at h
    | some v =>
      simp only [hi, Option.bind_some] at h
      obtain ⟨rfl, -, -⟩ := chargeBits_some h
      exact ⟨by simp [Term.value, hi], hk⟩
  | .num n, ρ, w, x, w', h => by
    have hk := fun _ : w ≤ limit => (Term.evalB_bits O limit ρ _ w x w' h).2
    simp only [Term.evalB] at h
    have ⟨_, h⟩ := charge_some h
    obtain ⟨rfl, -, -⟩ := chargeBits_some h
    exact ⟨by simp [Term.value], hk⟩
  | .add a b, ρ, w, x, w', h | .sub a b, ρ, w, x, w', h | .mul a b, ρ, w, x, w', h => by
    have hk := fun _ : w ≤ limit => (Term.evalB_bits O limit ρ _ w x w' h).2
    simp only [Term.evalB] at h
    have ⟨_, h⟩ := charge_some h
    cases ha : Term.evalB O limit ρ a (w + 1) with
    | none => simp [ha] at h
    | some ra =>
      obtain ⟨xa, wa⟩ := ra
      cases hb : Term.evalB O limit ρ b wa with
      | none => simp [ha, hb] at h
      | some rb =>
        obtain ⟨xb, wb⟩ := rb
        have ⟨va, _⟩ := Term.evalB_sound hA a ρ (w + 1) xa wa ha
        have ⟨vb, _⟩ := Term.evalB_sound hA b ρ wa xb wb hb
        simp only [ha, hb, Option.bind_some] at h
        obtain ⟨rfl, -, -⟩ := chargeBits_some h
        exact ⟨by simp [Term.value, va, vb], hk⟩
  | .call f args, ρ, w, x, w', h => by
    have hk := fun _ : w ≤ limit => (Term.evalB_bits O limit ρ _ w x w' h).2
    simp only [Term.evalB] at h
    have ⟨_, h⟩ := charge_some h
    cases hf : O.funs f with
    | none => simp [hf] at h
    | some r =>
      obtain ⟨n, g⟩ := r
      cases hs : Term.evalBs O limit ρ args (w + 1) with
      | none => simp [hf, hs] at h
      | some rs =>
        obtain ⟨xs, ws⟩ := rs
        simp only [hf, hs] at h
        split at h
        · obtain ⟨g', hg', hgg⟩ := hA.funs f n g hf
          have ⟨vs, _⟩ := Term.evalBs_sound hA args ρ (w + 1) xs ws hs
          rw [Option.bind_eq_some_iff] at h
          obtain ⟨⟨y, wy⟩, hy, h⟩ := h
          obtain ⟨rfl, -, -⟩ := chargeBits_some h
          have ⟨vx, _⟩ := hgg xs ws x wy hy
          exact ⟨by simp [Term.value, *], hk⟩
        · simp at h
  | .countFromTo lo hi φ, ρ, w, x, w', h => by
    have hk := fun _ : w ≤ limit => (Term.evalB_bits O limit ρ _ w x w' h).2
    simp only [Term.evalB] at h
    have ⟨_, h⟩ := charge_some h
    cases hl : Term.evalB O limit ρ lo (w + 1) with
    | none => simp [hl] at h
    | some rl =>
      obtain ⟨l, wl⟩ := rl
      cases hh : Term.evalB O limit ρ hi wl with
      | none => simp [hl, hh] at h
      | some rh =>
        obtain ⟨u, wh⟩ := rh
        simp only [hl, hh] at h
        have ⟨vl, _⟩ := Term.evalB_sound hA lo ρ (w + 1) l wl hl
        have ⟨vh, _⟩ := Term.evalB_sound hA hi ρ wl u wh hh
        rw [Option.bind_eq_some_iff] at h
        obtain ⟨⟨c, wc⟩, hc, h⟩ := h
        obtain ⟨rfl, -, -⟩ := chargeBits_some h
        have ⟨vc, _⟩ := countLoop_sound (fun i => Holds E (i :: ρ) φ) _ limit
          (stepB_sound fun i w b w' hs => Formula.evalB_sound hA φ (i :: ρ) w b w' hs) _ _ _ _ _ _ hc
        exact ⟨by simp [Term.value, vl, vh, vc], hk⟩
theorem Term.evalBs_sound {E : Env} {O : OpEnv} {limit : Nat} (hA : Agrees E O limit) :
    ∀ (ts : List Term) (ρ : List Int) (w : Nat) (xs : List Int) (w' : Nat), Term.evalBs O limit ρ ts w = some (xs, w') →
      Term.values E ρ ts = some xs ∧ (w ≤ limit → w' ≤ limit)
  | [], ρ, w, xs, w', h => by simp_all [Term.evalBs, Term.values]
  | t :: ts, ρ, w, xs, w', h => by
    simp only [Term.evalBs] at h
    cases ht : Term.evalB O limit ρ t w with
    | none => simp [ht] at h
    | some r =>
      obtain ⟨x, w1⟩ := r
      cases hs : Term.evalBs O limit ρ ts w1 with
      | none => simp [ht, hs] at h
      | some rs =>
        obtain ⟨ys, w2⟩ := rs
        have ⟨vt, wkt⟩ := Term.evalB_sound hA t ρ w x w1 ht
        have ⟨vs, wks⟩ := Term.evalBs_sound hA ts ρ w1 ys w2 hs
        simp only [ht, hs, Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨by simp [Term.values, vt, vs], fun h0 => wks (wkt h0)⟩
theorem Formula.evalB_sound {E : Env} {O : OpEnv} {limit : Nat} (hA : Agrees E O limit) :
    ∀ (φ : Formula) (ρ : List Int) (w : Nat) (b : Bool) (w' : Nat), Formula.evalB O limit ρ φ w = some (b, w') →
      (Holds E ρ φ ↔ b = true) ∧ (w ≤ limit → w' ≤ limit)
  | .eq a c, ρ, w, b, w', h | .lt a c, ρ, w, b, w', h | .le a c, ρ, w, b, w', h | .dvd a c, ρ, w, b, w', h => by
    simp only [Formula.evalB] at h
    have ⟨hw, h⟩ := charge_some h
    cases ha : Term.evalB O limit ρ a (w + 1) with
    | none => simp [ha] at h
    | some ra =>
      obtain ⟨xa, wa⟩ := ra
      cases hc : Term.evalB O limit ρ c wa with
      | none => simp [ha, hc] at h
      | some rc =>
        obtain ⟨xc, wc⟩ := rc
        have ⟨va, wka⟩ := Term.evalB_sound hA a ρ (w + 1) xa wa ha
        have ⟨vc, wkc⟩ := Term.evalB_sound hA c ρ wa xc wc hc
        simp only [ha, hc, Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨by simp [Holds, va, vc], fun _ => wkc (wka hw)⟩
  | .call p args, ρ, w, b, w', h => by
    simp only [Formula.evalB] at h
    have ⟨hw, h⟩ := charge_some h
    cases hp : O.preds p with
    | none => simp [hp] at h
    | some r =>
      obtain ⟨n, P⟩ := r
      cases hs : Term.evalBs O limit ρ args (w + 1) with
      | none => simp [hp, hs] at h
      | some rs =>
        obtain ⟨xs, ws⟩ := rs
        simp only [hp, hs] at h
        split at h
        · obtain ⟨P', hP', hPP⟩ := hA.preds p n P hp
          have ⟨vs, wks⟩ := Term.evalBs_sound hA args ρ (w + 1) xs ws hs
          have ⟨vx, wkx⟩ := hPP xs ws b w' h
          refine ⟨?_, fun _ => wkx (wks hw)⟩
          simp only [Holds, hP', vs, Option.some.injEq, Prod.mk.injEq]
          constructor
          · rintro ⟨_, _, _, ⟨rfl, rfl⟩, rfl, _, hx⟩; exact vx.mp hx
          · intro hb; exact ⟨n, P', xs, ⟨rfl, rfl⟩, rfl, by assumption, vx.mpr hb⟩
        · simp at h
  | .not φ, ρ, w, b, w', h => by
    simp only [Formula.evalB] at h
    have ⟨hw, h⟩ := charge_some h
    cases hφ : Formula.evalB O limit ρ φ (w + 1) with
    | none => simp [hφ] at h
    | some r =>
      obtain ⟨b1, w1⟩ := r
      have ⟨v, wk⟩ := Formula.evalB_sound hA φ ρ (w + 1) b1 w1 hφ
      simp only [hφ, Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
      obtain ⟨rfl, rfl⟩ := h
      exact ⟨by simp [Holds, v], fun _ => wk hw⟩
  | .and φ ψ, ρ, w, b, w', h | .or φ ψ, ρ, w, b, w', h | .imp φ ψ, ρ, w, b, w', h => by
    simp only [Formula.evalB] at h
    have ⟨hw, h⟩ := charge_some h
    cases hφ : Formula.evalB O limit ρ φ (w + 1) with
    | none => simp [hφ] at h
    | some r =>
      obtain ⟨b1, w1⟩ := r
      have ⟨v, wk⟩ := Formula.evalB_sound hA φ ρ (w + 1) b1 w1 hφ
      cases b1 <;> simp only [hφ, Option.some.injEq, Prod.mk.injEq] at h <;>
        first
        | (obtain ⟨rfl, rfl⟩ := h; exact ⟨by simp_all [Holds], fun _ => wk hw⟩)
        | (have ⟨v2, wk2⟩ := Formula.evalB_sound hA ψ ρ w1 b w' h
           exact ⟨by simp_all [Holds], fun _ => wk2 (wk hw)⟩)
  | .allNat _, _, _, _, _, h | .exNat _, _, _, _, _, h | .allInt _, _, _, _, _, h | .exInt _, _, _, _, _, h => by
    simp [Formula.evalB] at h
  | .allFromTo lo hi φ, ρ, w, b, w', h | .exFromTo lo hi φ, ρ, w, b, w', h => by
    simp only [Formula.evalB] at h
    have ⟨hw, h⟩ := charge_some h
    cases hl : Term.evalB O limit ρ lo (w + 1) with
    | none => simp [hl] at h
    | some rl =>
      obtain ⟨l, wl⟩ := rl
      cases hh : Term.evalB O limit ρ hi wl with
      | none => simp [hl, hh] at h
      | some rh =>
        obtain ⟨u, wh⟩ := rh
        simp only [hl, hh] at h
        have ⟨vl, wkl⟩ := Term.evalB_sound hA lo ρ (w + 1) l wl hl
        have ⟨vh, wkh⟩ := Term.evalB_sound hA hi ρ wl u wh hh
        have hs := stepB_sound fun i w b w' hs => Formula.evalB_sound hA φ (i :: ρ) w b w' hs
        first
        | (have ⟨v, wk⟩ := quantLoop_true (fun i => Holds E (i :: ρ) φ) _ limit hs _ _ _ _ _ h
           have H : Holds E ρ (.allFromTo lo hi φ) ↔ ∀ i, l ≤ i → i ≤ u → Holds E (i :: ρ) φ := by simp [Holds, vl, vh]
           exact ⟨(H.trans (range_all l u (fun i => Holds E (i :: ρ) φ)).symm).trans v.symm, fun _ => wk (wkh (wkl hw))⟩)
        | (have ⟨v, wk⟩ := quantLoop_false (fun i => Holds E (i :: ρ) φ) _ limit hs _ _ _ _ _ h
           have H : Holds E ρ (.exFromTo lo hi φ) ↔ ∃ i, l ≤ i ∧ i ≤ u ∧ Holds E (i :: ρ) φ := by simp [Holds, vl, vh]
           exact ⟨(H.trans (range_ex l u (fun i => Holds E (i :: ρ) φ)).symm).trans v.symm, fun _ => wk (wkh (wkl hw))⟩)
end

theorem agrees_env (D : Defs) (limit : Nat) : Agrees D.env (D.opEnv limit) limit := by
  unfold Defs.env Defs.opEnv
  generalize hE : (⟨fun _ => none, fun _ => none⟩ : Env) = E
  generalize hO : (⟨fun _ => none, fun _ => none⟩ : OpEnv) = O
  have hA : Agrees E O limit := by subst hE hO; exact ⟨by simp, by simp⟩
  clear hE hO
  induction D generalizing E O with
  | nil => exact hA
  | cons d D ih =>
    apply ih
    cases d with
    | fn f n body =>
      refine ⟨fun g m k hk => ?_, hA.preds⟩
      by_cases hg : g = f
      · subst hg
        simp only [ite_true, Option.some.injEq, Prod.mk.injEq] at hk ⊢
        obtain ⟨rfl, rfl⟩ := hk
        exact ⟨_, ⟨rfl, rfl⟩, fun xs w x w' h => Term.evalB_sound hA body xs w x w' h⟩
      · simp only [hg, ite_false] at hk ⊢; exact hA.funs g m k hk
    | pred p n body =>
      refine ⟨hA.funs, fun q m k hk => ?_⟩
      by_cases hq : q = p
      · subst hq
        simp only [ite_true, Option.some.injEq, Prod.mk.injEq] at hk ⊢
        obtain ⟨rfl, rfl⟩ := hk
        exact ⟨_, ⟨rfl, rfl⟩, fun xs w b w' h => Formula.evalB_sound hA body xs w b w' h⟩
      · simp only [hq, ite_false] at hk ⊢; exact hA.preds q m k hk


set_option linter.unusedVariables false in
theorem decideBounded_sound (D : Defs) (hD : D.WellFormed = true) (φ : Formula)
    (hφ : φ.Scoped D 0 = true) (limit : Nat) (b : Bool) (w : Nat)
    (h : decideBounded D limit φ = some (b, w)) : D.Means φ ↔ b = true :=
  (Formula.evalB_sound (agrees_env D limit) φ [] 0 b w h).1

theorem decideBounded_work (D : Defs) (φ : Formula) (limit : Nat) (b : Bool) (w : Nat)
    (h : decideBounded D limit φ = some (b, w)) : w ≤ limit :=
  (Formula.evalB_sound (agrees_env D limit) φ [] 0 b w h).2 (Nat.zero_le _)

theorem arithOutcome_unbounded_iff (D : Defs) (limit : Nat) (φ : Formula) :
    arithOutcome D limit φ = .unknown .unboundedStatement ↔ φ.Bounded D = false := by
  unfold arithOutcome
  cases φ.Bounded D <;> simp
  split <;> simp

theorem arithOutcome_exhausted_iff (D : Defs) (limit : Nat) (φ : Formula) :
    arithOutcome D limit φ = .unknown (.limit .evaluations) ↔
      φ.Bounded D = true ∧ decideBounded D limit φ = none := by
  unfold arithOutcome
  cases φ.Bounded D <;> simp
  split <;> simp_all

theorem arithOutcome_decided (D : Defs) (hD : D.WellFormed = true) (φ : Formula)
    (hφ : φ.Scoped D 0 = true) (limit : Nat) (v : Verdict) (h : arithOutcome D limit φ = .decided v) :
    v ≠ .undefined ∧ (v = .holds ↔ D.Means φ) := by
  unfold arithOutcome at h
  split at h
  · split at h <;> simp at h <;> subst h
    · next w hb => simp [decideBounded_sound D hD φ hφ limit true w hb]
    · next w hb => simp [decideBounded_sound D hD φ hφ limit false w hb]
  · simp at h

/-! A larger budget never changes an answer (`decideBounded_mono`): a completed call of the smaller budget's
environment completes, with the same value and units, in the larger one's. -/

/-- Each call `O` completes, `O'` completes with the same value and units. -/
structure Extends (O O' : OpEnv) : Prop where
  funs : ∀ f n g, O.funs f = some (n, g) → ∃ g', O'.funs f = some (n, g') ∧ ∀ xs w r, g xs w = some r → g' xs w = some r
  preds : ∀ p n P, O.preds p = some (n, P) → ∃ P', O'.preds p = some (n, P') ∧
    ∀ xs w r, P xs w = some r → P' xs w = some r

theorem charge_mono {α : Type} {limit limit' w : Nat} {k k' : Nat → Option (α × Nat)} {r : α × Nat}
    (hl : limit ≤ limit') (hk : ∀ r, k (w + 1) = some r → k' (w + 1) = some r) (h : charge limit w k = some r) :
    charge limit' w k' = some r := by
  have ⟨hw, h⟩ := charge_some h
  unfold charge; rw [if_neg (by omega)]; exact hk _ h

theorem chargeBits_mono {limit limit' w : Nat} {x : Int} {r : Int × Nat} (hl : limit ≤ limit')
    (h : chargeBits limit x w = some r) : chargeBits limit' x w = some r := by
  unfold chargeBits at h ⊢; split at h
  · simp at h
  · rw [if_neg (by omega)]; exact h

theorem stepB_mono {limit limit' : Nat} {cond cond' : Int → Nat → Option (Bool × Nat)} (hl : limit ≤ limit')
    (hs : ∀ i w r, cond i w = some r → cond' i w = some r) :
    ∀ i w r, stepB limit cond i w = some r → stepB limit' cond' i w = some r := fun i w r h => by
  have ⟨hw, h⟩ := stepB_some h
  unfold stepB chargeBits; rw [if_neg (by omega)]; exact hs _ _ _ h

theorem quantLoop_mono (u : Bool) {step step' : Int → Nat → Option (Bool × Nat)}
    (hs : ∀ i w r, step i w = some r → step' i w = some r) :
    ∀ n i w r, quantLoop u step n i w = some r → quantLoop u step' n i w = some r
  | 0, _, _, _, h => h
  | n + 1, i, w, r, h => by
    simp only [quantLoop] at h ⊢
    cases hst : step i w with
    | none => simp [hst] at h
    | some r0 =>
      obtain ⟨b, w'⟩ := r0
      rw [hs i w _ hst]; simp only [hst] at h ⊢
      split at h
      · rw [if_pos ‹_›]; exact quantLoop_mono u hs n _ _ _ h
      · rw [if_neg ‹_›]; exact h

theorem countLoop_mono {step step' : Int → Nat → Option (Bool × Nat)}
    (hs : ∀ i w r, step i w = some r → step' i w = some r) :
    ∀ n i acc w r, countLoop step n i acc w = some r → countLoop step' n i acc w = some r
  | 0, _, _, _, _, h => h
  | n + 1, i, acc, w, r, h => by
    simp only [countLoop] at h ⊢
    cases hst : step i w with
    | none => simp [hst] at h
    | some r0 =>
      obtain ⟨b, w'⟩ := r0
      rw [hs i w _ hst]; simp only [hst] at h ⊢
      exact countLoop_mono hs n _ _ _ _ h

mutual
theorem Term.evalB_mono {O O' : OpEnv} {limit limit' : Nat} (hE : Extends O O') (hl : limit ≤ limit') :
    ∀ (t : Term) (ρ : List Int) (w : Nat) (r : Int × Nat), Term.evalB O limit ρ t w = some r →
      Term.evalB O' limit' ρ t w = some r
  | .var i, ρ, w, r, h => by
    simp only [Term.evalB] at h ⊢
    refine charge_mono hl (fun r h => ?_) h
    cases hi : ρ[i]? with
    | none => simp [hi] at h
    | some v => simp only [hi, Option.bind_some] at h ⊢; exact chargeBits_mono hl h
  | .num n, ρ, w, r, h => by
    simp only [Term.evalB] at h ⊢
    exact charge_mono hl (fun r h => chargeBits_mono hl h) h
  | .add a b, ρ, w, r, h | .sub a b, ρ, w, r, h | .mul a b, ρ, w, r, h => by
    simp only [Term.evalB] at h ⊢
    refine charge_mono hl (fun r h => ?_) h
    cases ha : Term.evalB O limit ρ a (w + 1) with
    | none => simp [ha] at h
    | some ra =>
      obtain ⟨xa, wa⟩ := ra
      rw [Term.evalB_mono hE hl a ρ _ _ ha]; simp only [ha] at h ⊢
      cases hb : Term.evalB O limit ρ b wa with
      | none => simp [hb] at h
      | some rb =>
        rw [Term.evalB_mono hE hl b ρ wa _ hb]; simp only [hb, Option.bind_some] at h ⊢
        exact chargeBits_mono hl h
  | .call f args, ρ, w, r, h => by
    simp only [Term.evalB] at h ⊢
    refine charge_mono hl (fun r h => ?_) h
    cases hf : O.funs f with
    | none => simp [hf] at h
    | some fg =>
      obtain ⟨n, g⟩ := fg
      obtain ⟨g', hg', hgg⟩ := hE.funs f n g hf
      rw [hg']; simp only [hf] at h ⊢
      cases hs : Term.evalBs O limit ρ args (w + 1) with
      | none => simp [hs] at h
      | some rs =>
        obtain ⟨xs, ws⟩ := rs
        rw [Term.evalBs_mono hE hl args ρ _ _ hs]; simp only [hs] at h ⊢
        split at h
        · rw [if_pos ‹_›]
          rw [Option.bind_eq_some_iff] at h ⊢
          obtain ⟨y, hy, h⟩ := h
          exact ⟨y, hgg _ _ _ hy, chargeBits_mono hl h⟩
        · simp at h
  | .countFromTo lo hi φ, ρ, w, r, h => by
    simp only [Term.evalB] at h ⊢
    refine charge_mono hl (fun r h => ?_) h
    cases hlo : Term.evalB O limit ρ lo (w + 1) with
    | none => simp [hlo] at h
    | some rl =>
      obtain ⟨l, wl⟩ := rl
      rw [Term.evalB_mono hE hl lo ρ _ _ hlo]; simp only [hlo] at h ⊢
      cases hhi : Term.evalB O limit ρ hi wl with
      | none => simp [hhi] at h
      | some rh =>
        obtain ⟨u, wh⟩ := rh
        rw [Term.evalB_mono hE hl hi ρ wl _ hhi]; simp only [hhi] at h ⊢
        rw [Option.bind_eq_some_iff] at h ⊢
        obtain ⟨c, hc, h⟩ := h
        exact ⟨c, countLoop_mono (stepB_mono hl fun i w r hs => Formula.evalB_mono hE hl φ (i :: ρ) w r hs) _ _ _ _ _ hc,
          chargeBits_mono hl h⟩
theorem Term.evalBs_mono {O O' : OpEnv} {limit limit' : Nat} (hE : Extends O O') (hl : limit ≤ limit') :
    ∀ (ts : List Term) (ρ : List Int) (w : Nat) (r : List Int × Nat), Term.evalBs O limit ρ ts w = some r →
      Term.evalBs O' limit' ρ ts w = some r
  | [], ρ, w, r, h => by simpa [Term.evalBs] using h
  | t :: ts, ρ, w, r, h => by
    simp only [Term.evalBs] at h ⊢
    cases ht : Term.evalB O limit ρ t w with
    | none => simp [ht] at h
    | some rt =>
      obtain ⟨x, w1⟩ := rt
      rw [Term.evalB_mono hE hl t ρ w _ ht]; simp only [ht] at h ⊢
      cases hs : Term.evalBs O limit ρ ts w1 with
      | none => simp [hs] at h
      | some rs => rw [Term.evalBs_mono hE hl ts ρ w1 _ hs]; simpa [hs] using h
theorem Formula.evalB_mono {O O' : OpEnv} {limit limit' : Nat} (hE : Extends O O') (hl : limit ≤ limit') :
    ∀ (φ : Formula) (ρ : List Int) (w : Nat) (r : Bool × Nat), Formula.evalB O limit ρ φ w = some r →
      Formula.evalB O' limit' ρ φ w = some r
  | .eq a c, ρ, w, r, h | .lt a c, ρ, w, r, h | .le a c, ρ, w, r, h | .dvd a c, ρ, w, r, h => by
    simp only [Formula.evalB] at h ⊢
    refine charge_mono hl (fun r h => ?_) h
    cases ha : Term.evalB O limit ρ a (w + 1) with
    | none => simp [ha] at h
    | some ra =>
      obtain ⟨xa, wa⟩ := ra
      rw [Term.evalB_mono hE hl a ρ _ _ ha]; simp only [ha] at h ⊢
      cases hc : Term.evalB O limit ρ c wa with
      | none => simp [hc] at h
      | some rc => rw [Term.evalB_mono hE hl c ρ wa _ hc]; simpa [hc] using h
  | .call p args, ρ, w, r, h => by
    simp only [Formula.evalB] at h ⊢
    refine charge_mono hl (fun r h => ?_) h
    cases hp : O.preds p with
    | none => simp [hp] at h
    | some pP =>
      obtain ⟨n, P⟩ := pP
      obtain ⟨P', hP', hPP⟩ := hE.preds p n P hp
      rw [hP']; simp only [hp] at h ⊢
      cases hs : Term.evalBs O limit ρ args (w + 1) with
      | none => simp [hs] at h
      | some rs =>
        obtain ⟨xs, ws⟩ := rs
        rw [Term.evalBs_mono hE hl args ρ _ _ hs]; simp only [hs] at h ⊢
        split at h
        · rw [if_pos ‹_›]; exact hPP _ _ _ h
        · simp at h
  | .not φ, ρ, w, r, h => by
    simp only [Formula.evalB] at h ⊢
    refine charge_mono hl (fun r h => ?_) h
    cases hφ : Formula.evalB O limit ρ φ (w + 1) with
    | none => simp [hφ] at h
    | some r1 => rw [Formula.evalB_mono hE hl φ ρ _ _ hφ]; simpa [hφ] using h
  | .and φ ψ, ρ, w, r, h | .or φ ψ, ρ, w, r, h | .imp φ ψ, ρ, w, r, h => by
    simp only [Formula.evalB] at h ⊢
    refine charge_mono hl (fun r h => ?_) h
    cases hφ : Formula.evalB O limit ρ φ (w + 1) with
    | none => simp [hφ] at h
    | some r1 =>
      obtain ⟨b1, w1⟩ := r1
      rw [Formula.evalB_mono hE hl φ ρ _ _ hφ]
      cases b1 <;> simp only [hφ] at h ⊢ <;> first | exact h | exact Formula.evalB_mono hE hl ψ ρ w1 r h
  | .allNat _, _, _, _, h | .exNat _, _, _, _, h | .allInt _, _, _, _, h | .exInt _, _, _, _, h => by
    simp [Formula.evalB] at h
  | .allFromTo lo hi φ, ρ, w, r, h | .exFromTo lo hi φ, ρ, w, r, h => by
    simp only [Formula.evalB] at h ⊢
    refine charge_mono hl (fun r h => ?_) h
    cases hlo : Term.evalB O limit ρ lo (w + 1) with
    | none => simp [hlo] at h
    | some rl =>
      obtain ⟨l, wl⟩ := rl
      rw [Term.evalB_mono hE hl lo ρ _ _ hlo]; simp only [hlo] at h ⊢
      cases hhi : Term.evalB O limit ρ hi wl with
      | none => simp [hhi] at h
      | some rh =>
        obtain ⟨u, wh⟩ := rh
        rw [Term.evalB_mono hE hl hi ρ wl _ hhi]; simp only [hhi] at h ⊢
        exact quantLoop_mono _ (stepB_mono hl fun i w r hs => Formula.evalB_mono hE hl φ (i :: ρ) w r hs) _ _ _ _ h
end

theorem foldl_rel {α β γ : Type} (R : α → β → Prop) {f : α → γ → α} {g : β → γ → β}
    (h : ∀ a b c, R a b → R (f a c) (g b c)) : ∀ (l : List γ) a b, R a b → R (l.foldl f a) (l.foldl g b)
  | [], _, _, hr => hr
  | c :: l, a, b, hr => foldl_rel R h l _ _ (h a b c hr)

theorem opEnv_extends (D : Defs) {limit limit' : Nat} (hl : limit ≤ limit') :
    Extends (D.opEnv limit) (D.opEnv limit') := by
  refine foldl_rel Extends (fun O O' d hE => ?_) D _ _ ⟨by simp, by simp⟩
  cases d with
  | fn f n body =>
    refine ⟨fun g m k hk => ?_, hE.preds⟩
    by_cases hg : g = f
    · subst hg
      simp only [ite_true, Option.some.injEq, Prod.mk.injEq] at hk ⊢
      obtain ⟨rfl, rfl⟩ := hk
      exact ⟨_, ⟨rfl, rfl⟩, fun xs w r h => Term.evalB_mono hE hl body xs w r h⟩
    · simp only [hg, ite_false] at hk ⊢; exact hE.funs g m k hk
  | pred p n body =>
    refine ⟨hE.funs, fun q m k hk => ?_⟩
    by_cases hq : q = p
    · subst hq
      simp only [ite_true, Option.some.injEq, Prod.mk.injEq] at hk ⊢
      obtain ⟨rfl, rfl⟩ := hk
      exact ⟨_, ⟨rfl, rfl⟩, fun xs w r h => Formula.evalB_mono hE hl body xs w r h⟩
    · simp only [hq, ite_false] at hk ⊢; exact hE.preds q m k hk

theorem decideBounded_mono (D : Defs) (φ : Formula) (limit limit' : Nat) (r : Bool × Nat)
    (h : decideBounded D limit φ = some r) (hl : limit ≤ limit') : decideBounded D limit' φ = some r :=
  Formula.evalB_mono (opEnv_extends D hl) hl φ [] 0 r h

/-! A bounded, admitted statement is decided once the budget covers its work (`decideBounded_complete`). The work is
the statement's own: the same units and the same answer at every budget that covers them (`decideBounded_covered`). -/

/-- What admission guarantees of a site (spec 12.1), for the definitions `E` a body may call and `depth` outer values. -/
def Site.Ok (E : Defs) (depth : Nat) : Site → Prop
  | .free j => j < depth
  | .call pred f argc => ∃ d, E.find? (fun d => d.name == f && d.isPred == pred) = some d ∧ d.arity = argc
  | .count _ => True

theorem Site.ok_of_refusal {D E : Defs} {depth : Nat} {B : Option (String → Bool)} :
    ∀ {s : Site}, s.refusal D E depth B = none → s.Ok E depth
  | .free j, h => by simp only [Site.refusal] at h; split at h <;> simp_all [Site.Ok]
  | .call pred f argc, h => by
    simp only [Site.refusal] at h
    split at h
    · split at h
      · simp at h
      · next d hd => split at h
                     · exact ⟨d, hd, ‹_›⟩
                     · simp at h
    · simp at h
  | .count _, _ => trivial

/-- Each name `B` marks, as `E` finds it, completes in the environment of every budget, with a value and a work that
depend only on its arguments, once the budget covers that work. -/
structure Total (O : Nat → OpEnv) (E : Defs) (B : String → Bool) : Prop where
  funs : ∀ f d, E.find? (fun d => d.name == f && d.isPred == false) = some d → B f = true →
    ∀ xs : List Int, xs.length = d.arity → ∃ x W, ∀ limit, ∃ g, (O limit).funs f = some (d.arity, g) ∧
      ∀ w, w + W ≤ limit → g xs w = some (x, w + W)
  preds : ∀ p d, E.find? (fun d => d.name == p && d.isPred == true) = some d → B p = true →
    ∀ xs : List Int, xs.length = d.arity → ∃ b W, ∀ limit, ∃ P, (O limit).preds p = some (d.arity, P) ∧
      ∀ w, w + W ≤ limit → P xs w = some (b, w + W)

theorem charge_eq {α : Type} {limit w : Nat} {k : Nat → Option (α × Nat)} (h : w < limit) :
    charge limit w k = k (w + 1) := by
  unfold charge; rw [if_neg (by omega)]

theorem chargeBits_eq {limit w : Nat} {x : Int} (h : w + bits x ≤ limit) :
    chargeBits limit x w = some (x, w + bits x) := by
  unfold chargeBits; rw [if_neg (by omega)]

/-- A step's work is its value's size plus its condition's. -/
theorem stepB_total (cond : Nat → Int → Nat → Option (Bool × Nat))
    (hs : ∀ i, ∃ b W, ∀ limit w, w + W ≤ limit → cond limit i w = some (b, w + W)) :
    ∀ i, ∃ b W, ∀ limit w, w + W ≤ limit → stepB limit (cond limit) i w = some (b, w + W) := fun i => by
  obtain ⟨b, W, h⟩ := hs i
  exact ⟨b, bits i + W, fun limit w hw => by
    simp only [stepB, chargeBits_eq (show w + bits i ≤ limit by omega), Option.bind_some,
      h limit (w + bits i) (by omega), Nat.add_assoc]⟩

theorem quantLoop_total (u : Bool) (step : Nat → Int → Nat → Option (Bool × Nat))
    (hs : ∀ i, ∃ b W, ∀ limit w, w + W ≤ limit → step limit i w = some (b, w + W)) :
    ∀ n i, ∃ b W, ∀ limit w, w + W ≤ limit → quantLoop u (step limit) n i w = some (b, w + W)
  | 0, _ => ⟨u, 0, fun _ _ _ => by simp [quantLoop]⟩
  | n + 1, i => by
    obtain ⟨b, W1, h1⟩ := hs i
    obtain ⟨c, W2, h2⟩ := quantLoop_total u step hs n (i + 1)
    by_cases hb : b = u
    · exact ⟨c, W1 + W2, fun limit w hw => by
        simp only [quantLoop, h1 limit w (by omega), hb, if_true, h2 limit (w + W1) (by omega), Nat.add_assoc]⟩
    · exact ⟨!u, W1, fun limit w hw => by simp [quantLoop, h1 limit w hw, hb]⟩

theorem countLoop_total (step : Nat → Int → Nat → Option (Bool × Nat))
    (hs : ∀ i, ∃ b W, ∀ limit w, w + W ≤ limit → step limit i w = some (b, w + W)) :
    ∀ n i acc, ∃ c W, ∀ limit w, w + W ≤ limit → countLoop (step limit) n i acc w = some (c, w + W)
  | 0, _, acc => ⟨acc, 0, fun _ _ _ => by simp [countLoop]⟩
  | n + 1, i, acc => by
    obtain ⟨b, W1, h1⟩ := hs i
    obtain ⟨c, W2, h2⟩ := countLoop_total step hs n (i + 1) (if b then acc + 1 else acc)
    exact ⟨c, W1 + W2, fun limit w hw => by
      simp only [countLoop, h1 limit w (by omega), h2 limit (w + W1) (by omega), Nat.add_assoc]⟩

/-- The sites of a part are sites of the whole. -/
macro (name := subSites) "sub_sites" hs:term : term =>
  `(fun s h => $hs s (by simp only [Term.sites, Term.sitesList, Formula.sites, List.mem_append, List.mem_cons]; simp [h]))

mutual
theorem Term.evalB_total {O : Nat → OpEnv} {E : Defs} {B : String → Bool} {depth : Nat} (hT : Total O E B) :
    ∀ (t : Term) (k : Nat) (ρ : List Int), Term.bnd B t = true → (∀ s ∈ Term.sites k t, s.Ok E depth) →
      ρ.length = k + depth → ∃ x W, ∀ limit w, w + W ≤ limit → Term.evalB (O limit) limit ρ t w = some (x, w + W)
  | .var i, k, ρ, _, hs, hl => by
    have hi : i < ρ.length := by
      by_cases hk : k ≤ i
      · have := hs (.free (i - k)) (by simp [Term.sites, hk]); simp only [Site.Ok] at this; omega
      · omega
    exact ⟨ρ[i], 1 + bits ρ[i], fun limit w hw => by
      simp only [Term.evalB, charge_eq (show w < limit by omega), hi, getElem?_pos, Option.bind_some,
        chargeBits_eq (show w + 1 + bits ρ[i] ≤ limit by omega), ← Nat.add_assoc]⟩
  | .num n, _, _, _, _, _ => ⟨n, 1 + bits n, fun limit w hw => by
      simp only [Term.evalB, charge_eq (show w < limit by omega), chargeBits_eq (show w + 1 + bits n ≤ limit by omega),
        ← Nat.add_assoc]⟩
  | .add a b, k, ρ, hb, hs, hl => by
    simp only [Term.bnd, Bool.and_eq_true] at hb
    obtain ⟨x, Wa, ha⟩ := Term.evalB_total hT a k ρ hb.1 (sub_sites hs) hl
    obtain ⟨y, Wb, hb'⟩ := Term.evalB_total hT b k ρ hb.2 (sub_sites hs) hl
    exact ⟨x + y, 1 + Wa + Wb + bits (x + y), fun limit w hw => by
      simp only [Term.evalB, charge_eq (show w < limit by omega), ha limit (w + 1) (by omega),
        hb' limit (w + 1 + Wa) (by omega), Option.bind_some,
        chargeBits_eq (show w + 1 + Wa + Wb + bits (x + y) ≤ limit by omega), ← Nat.add_assoc]⟩
  | .sub a b, k, ρ, hb, hs, hl => by
    simp only [Term.bnd, Bool.and_eq_true] at hb
    obtain ⟨x, Wa, ha⟩ := Term.evalB_total hT a k ρ hb.1 (sub_sites hs) hl
    obtain ⟨y, Wb, hb'⟩ := Term.evalB_total hT b k ρ hb.2 (sub_sites hs) hl
    exact ⟨x - y, 1 + Wa + Wb + bits (x - y), fun limit w hw => by
      simp only [Term.evalB, charge_eq (show w < limit by omega), ha limit (w + 1) (by omega),
        hb' limit (w + 1 + Wa) (by omega), Option.bind_some,
        chargeBits_eq (show w + 1 + Wa + Wb + bits (x - y) ≤ limit by omega), ← Nat.add_assoc]⟩
  | .mul a b, k, ρ, hb, hs, hl => by
    simp only [Term.bnd, Bool.and_eq_true] at hb
    obtain ⟨x, Wa, ha⟩ := Term.evalB_total hT a k ρ hb.1 (sub_sites hs) hl
    obtain ⟨y, Wb, hb'⟩ := Term.evalB_total hT b k ρ hb.2 (sub_sites hs) hl
    exact ⟨x * y, 1 + Wa + Wb + bits (x * y), fun limit w hw => by
      simp only [Term.evalB, charge_eq (show w < limit by omega), ha limit (w + 1) (by omega),
        hb' limit (w + 1 + Wa) (by omega), Option.bind_some,
        chargeBits_eq (show w + 1 + Wa + Wb + bits (x * y) ≤ limit by omega), ← Nat.add_assoc]⟩
  | .call f args, k, ρ, hb, hs, hl => by
    simp only [Term.bnd, Bool.and_eq_true] at hb
    obtain ⟨d, hd, har⟩ := hs (.call false f args.length) (by simp [Term.sites])
    obtain ⟨xs, Ws, hlen, hxs⟩ := Term.evalBs_total hT args k ρ hb.2 (sub_sites hs) hl
    obtain ⟨x, Wg, hg⟩ := hT.funs f d hd hb.1 xs (by omega)
    exact ⟨x, 1 + Ws + Wg + bits x, fun limit w hw => by
      obtain ⟨g, hf, hgw⟩ := hg limit
      simp only [Term.evalB, charge_eq (show w < limit by omega), hf, hxs limit (w + 1) (by omega), hlen, har,
        if_true, hgw (w + 1 + Ws) (by omega), Option.bind_some,
        chargeBits_eq (show w + 1 + Ws + Wg + bits x ≤ limit by omega), ← Nat.add_assoc]⟩
  | .countFromTo lo hi φ, k, ρ, hb, hs, hl => by
    simp only [Term.bnd, Bool.and_eq_true] at hb
    obtain ⟨l, Wl, hlo⟩ := Term.evalB_total hT lo k ρ hb.1.1 (sub_sites hs) hl
    obtain ⟨u, Wh, hhi⟩ := Term.evalB_total hT hi k ρ hb.1.2 (sub_sites hs) hl
    obtain ⟨c, Wc, hc⟩ := countLoop_total (fun limit => stepB limit fun i w => Formula.evalB (O limit) limit (i :: ρ) φ w)
      (stepB_total (fun limit i w => Formula.evalB (O limit) limit (i :: ρ) φ w)
        fun i => Formula.evalB_total hT φ (k + 1) (i :: ρ) hb.2 (sub_sites hs) (by simp [hl]; omega))
      (u - l + 1).toNat l 0
    exact ⟨c, 1 + Wl + Wh + Wc + bits c, fun limit w hw => by
      simp only [Term.evalB, charge_eq (show w < limit by omega), hlo limit (w + 1) (by omega),
        hhi limit (w + 1 + Wl) (by omega), hc limit (w + 1 + Wl + Wh) (by omega), Option.bind_some,
        chargeBits_eq (show w + 1 + Wl + Wh + Wc + bits c ≤ limit by omega), ← Nat.add_assoc]⟩
theorem Term.evalBs_total {O : Nat → OpEnv} {E : Defs} {B : String → Bool} {depth : Nat} (hT : Total O E B) :
    ∀ (ts : List Term) (k : Nat) (ρ : List Int), Term.bndList B ts = true →
      (∀ s ∈ Term.sitesList k ts, s.Ok E depth) → ρ.length = k + depth →
      ∃ xs W, xs.length = ts.length ∧ ∀ limit w, w + W ≤ limit → Term.evalBs (O limit) limit ρ ts w = some (xs, w + W)
  | [], _, _, _, _, _ => ⟨[], 0, rfl, fun _ _ _ => by simp [Term.evalBs]⟩
  | t :: ts, k, ρ, hb, hs, hl => by
    simp only [Term.bndList, Bool.and_eq_true] at hb
    obtain ⟨x, Wt, ht⟩ := Term.evalB_total hT t k ρ hb.1 (sub_sites hs) hl
    obtain ⟨xs, Ws, hlen, hxs⟩ := Term.evalBs_total hT ts k ρ hb.2 (sub_sites hs) hl
    exact ⟨x :: xs, Wt + Ws, by simp [hlen], fun limit w hw => by
      simp only [Term.evalBs, ht limit w (by omega), hxs limit (w + Wt) (by omega), Option.map_some, Nat.add_assoc]⟩
theorem Formula.evalB_total {O : Nat → OpEnv} {E : Defs} {B : String → Bool} {depth : Nat} (hT : Total O E B) :
    ∀ (φ : Formula) (k : Nat) (ρ : List Int), Formula.bnd B φ = true → (∀ s ∈ Formula.sites k φ, s.Ok E depth) →
      ρ.length = k + depth → ∃ b W, ∀ limit w, w + W ≤ limit → Formula.evalB (O limit) limit ρ φ w = some (b, w + W)
  | .eq a c, k, ρ, hb, hs, hl => by
    simp only [Formula.bnd, Bool.and_eq_true] at hb
    obtain ⟨x, Wa, ha⟩ := Term.evalB_total hT a k ρ hb.1 (sub_sites hs) hl
    obtain ⟨y, Wc, hc⟩ := Term.evalB_total hT c k ρ hb.2 (sub_sites hs) hl
    exact ⟨decide (x = y), 1 + Wa + Wc, fun limit w hw => by
      simp only [Formula.evalB, charge_eq (show w < limit by omega), ha limit (w + 1) (by omega),
        hc limit (w + 1 + Wa) (by omega), Option.map_some, ← Nat.add_assoc]⟩
  | .lt a c, k, ρ, hb, hs, hl => by
    simp only [Formula.bnd, Bool.and_eq_true] at hb
    obtain ⟨x, Wa, ha⟩ := Term.evalB_total hT a k ρ hb.1 (sub_sites hs) hl
    obtain ⟨y, Wc, hc⟩ := Term.evalB_total hT c k ρ hb.2 (sub_sites hs) hl
    exact ⟨decide (x < y), 1 + Wa + Wc, fun limit w hw => by
      simp only [Formula.evalB, charge_eq (show w < limit by omega), ha limit (w + 1) (by omega),
        hc limit (w + 1 + Wa) (by omega), Option.map_some, ← Nat.add_assoc]⟩
  | .le a c, k, ρ, hb, hs, hl => by
    simp only [Formula.bnd, Bool.and_eq_true] at hb
    obtain ⟨x, Wa, ha⟩ := Term.evalB_total hT a k ρ hb.1 (sub_sites hs) hl
    obtain ⟨y, Wc, hc⟩ := Term.evalB_total hT c k ρ hb.2 (sub_sites hs) hl
    exact ⟨decide (x ≤ y), 1 + Wa + Wc, fun limit w hw => by
      simp only [Formula.evalB, charge_eq (show w < limit by omega), ha limit (w + 1) (by omega),
        hc limit (w + 1 + Wa) (by omega), Option.map_some, ← Nat.add_assoc]⟩
  | .dvd a c, k, ρ, hb, hs, hl => by
    simp only [Formula.bnd, Bool.and_eq_true] at hb
    obtain ⟨x, Wa, ha⟩ := Term.evalB_total hT a k ρ hb.1 (sub_sites hs) hl
    obtain ⟨y, Wc, hc⟩ := Term.evalB_total hT c k ρ hb.2 (sub_sites hs) hl
    exact ⟨decide (x ∣ y), 1 + Wa + Wc, fun limit w hw => by
      simp only [Formula.evalB, charge_eq (show w < limit by omega), ha limit (w + 1) (by omega),
        hc limit (w + 1 + Wa) (by omega), Option.map_some, ← Nat.add_assoc]⟩
  | .call p args, k, ρ, hb, hs, hl => by
    simp only [Formula.bnd, Bool.and_eq_true] at hb
    obtain ⟨d, hd, har⟩ := hs (.call true p args.length) (by simp [Formula.sites])
    obtain ⟨xs, Ws, hlen, hxs⟩ := Term.evalBs_total hT args k ρ hb.2 (sub_sites hs) hl
    obtain ⟨b, Wp, hp⟩ := hT.preds p d hd hb.1 xs (by omega)
    exact ⟨b, 1 + Ws + Wp, fun limit w hw => by
      obtain ⟨P, hP, hPw⟩ := hp limit
      simp only [Formula.evalB, charge_eq (show w < limit by omega), hP, hxs limit (w + 1) (by omega), hlen, har,
        if_true, hPw (w + 1 + Ws) (by omega), ← Nat.add_assoc]⟩
  | .not φ, k, ρ, hb, hs, hl => by
    simp only [Formula.bnd] at hb
    obtain ⟨b, W, h⟩ := Formula.evalB_total hT φ k ρ hb (sub_sites hs) hl
    exact ⟨!b, 1 + W, fun limit w hw => by
      simp only [Formula.evalB, charge_eq (show w < limit by omega), h limit (w + 1) (by omega), Option.map_some,
        ← Nat.add_assoc]⟩
  | .and φ ψ, k, ρ, hb, hs, hl | .or φ ψ, k, ρ, hb, hs, hl | .imp φ ψ, k, ρ, hb, hs, hl => by
    simp only [Formula.bnd, Bool.and_eq_true] at hb
    obtain ⟨b1, W1, h1⟩ := Formula.evalB_total hT φ k ρ hb.1 (sub_sites hs) hl
    obtain ⟨b2, W2, h2⟩ := Formula.evalB_total hT ψ k ρ hb.2 (sub_sites hs) hl
    cases b1
    all_goals first
      | exact ⟨_, 1 + W1, fun limit w hw => by
          simp only [Formula.evalB, charge_eq (show w < limit by omega), h1 limit (w + 1) (by omega), ← Nat.add_assoc] <;> exact rfl⟩
      | exact ⟨_, 1 + W1 + W2, fun limit w hw => by
          simp only [Formula.evalB, charge_eq (show w < limit by omega), h1 limit (w + 1) (by omega),
            h2 limit (w + 1 + W1) (by omega), ← Nat.add_assoc] <;> exact rfl⟩
  | .allNat _, _, _, hb, _, _ | .exNat _, _, _, hb, _, _ | .allInt _, _, _, hb, _, _ | .exInt _, _, _, hb, _, _ => by
    simp [Formula.bnd] at hb
  | .allFromTo lo hi φ, k, ρ, hb, hs, hl => by
    simp only [Formula.bnd, Bool.and_eq_true] at hb
    obtain ⟨l, Wl, hlo⟩ := Term.evalB_total hT lo k ρ hb.1.1 (sub_sites hs) hl
    obtain ⟨u, Wh, hhi⟩ := Term.evalB_total hT hi k ρ hb.1.2 (sub_sites hs) hl
    have hst := stepB_total (fun limit i w => Formula.evalB (O limit) limit (i :: ρ) φ w)
      fun i => Formula.evalB_total hT φ (k + 1) (i :: ρ) hb.2 (sub_sites hs) (by simp [hl]; omega)
    obtain ⟨c, Wq, hq⟩ := quantLoop_total true (fun limit => stepB limit fun i w => Formula.evalB (O limit) limit (i :: ρ) φ w) hst
      (u - l + 1).toNat l
    exact ⟨c, 1 + Wl + Wh + Wq, fun limit w hw => by
      simp only [Formula.evalB, charge_eq (show w < limit by omega), hlo limit (w + 1) (by omega),
        hhi limit (w + 1 + Wl) (by omega), hq limit (w + 1 + Wl + Wh) (by omega), ← Nat.add_assoc]⟩
  | .exFromTo lo hi φ, k, ρ, hb, hs, hl => by
    simp only [Formula.bnd, Bool.and_eq_true] at hb
    obtain ⟨l, Wl, hlo⟩ := Term.evalB_total hT lo k ρ hb.1.1 (sub_sites hs) hl
    obtain ⟨u, Wh, hhi⟩ := Term.evalB_total hT hi k ρ hb.1.2 (sub_sites hs) hl
    have hst := stepB_total (fun limit i w => Formula.evalB (O limit) limit (i :: ρ) φ w)
      fun i => Formula.evalB_total hT φ (k + 1) (i :: ρ) hb.2 (sub_sites hs) (by simp [hl]; omega)
    obtain ⟨c, Wq, hq⟩ := quantLoop_total false (fun limit => stepB limit fun i w => Formula.evalB (O limit) limit (i :: ρ) φ w) hst
      (u - l + 1).toNat l
    exact ⟨c, 1 + Wl + Wh + Wq, fun limit w hw => by
      simp only [Formula.evalB, charge_eq (show w < limit by omega), hlo limit (w + 1) (by omega),
        hhi limit (w + 1 + Wl) (by omega), hq limit (w + 1 + Wl + Wh) (by omega), ← Nat.add_assoc]⟩
end

/-! The definitions' environment is total on its bounded names: by induction on the definitions, each admitted by
`Defs.WellFormed` over the ones above it. -/

theorem opEnv_snoc (limit : Nat) (E : Defs) (d : Def) : (E ++ [d]).opEnv limit = match d with
    | .fn f n body => { (E.opEnv limit) with
        funs := fun g => if g = f then some (n, fun xs w => Term.evalB (E.opEnv limit) limit xs body w)
          else (E.opEnv limit).funs g }
    | .pred p n body => { (E.opEnv limit) with
        preds := fun q => if q = p then some (n, fun xs w => Formula.evalB (E.opEnv limit) limit xs body w)
          else (E.opEnv limit).preds q } := by
  unfold Defs.opEnv; rw [List.foldl_append]; rfl

theorem boundedNames_snoc (E : Defs) (d : Def) : (E ++ [d]).boundedNames = match d with
    | .fn f _ body => fun g => if g = f then Term.bnd E.boundedNames body else E.boundedNames g
    | .pred p _ body => fun q => if q = p then Formula.bnd E.boundedNames body else E.boundedNames q := by
  unfold Defs.boundedNames; rw [List.foldl_append]; rfl

/-- What admission guarantees of every site of a definition's body, over the definitions `E` above it. -/
def Def.SitesOk (E : Defs) : Def → Prop
  | .fn _ n body => ∀ s ∈ Term.sites 0 body, s.Ok E n
  | .pred _ n body => ∀ s ∈ Formula.sites 0 body, s.Ok E n

theorem wellFormed_at {D : Defs} (hD : D.WellFormed = true) {k : Nat} {d : Def} (hk : D[k]? = some d) :
    (D.take k).any (·.name == d.name) = false ∧ d.SitesOk (D.take k) := by
  have hlt : k < D.length := (List.getElem?_eq_some_iff.1 hk).1
  simp only [Defs.WellFormed, Defs.refusals, List.isEmpty_iff, List.append_eq_nil_iff, List.filterMap_eq_nil_iff,
    List.flatMap_eq_nil_iff, List.mem_range] at hD
  obtain ⟨h1, h2⟩ := hD
  refine ⟨?_, ?_⟩
  · have := h1 k hlt; simp only [hk, Option.bind_some] at this; split at this <;> simp_all
  · have := h2 k hlt; simp only [hk] at this
    cases d <;> simp only [Def.SitesOk, List.filterMap_eq_nil_iff, List.mem_map] at this ⊢ <;>
      exact fun s hs => Site.ok_of_refusal (this _ ⟨s, hs, rfl⟩)

theorem Total.snoc {E : Defs} {d : Def} (hT : Total (fun limit => E.opEnv limit) E E.boundedNames)
    (hnew : E.any (·.name == d.name) = false) (hs : d.SitesOk E) :
    Total (fun limit => (E ++ [d]).opEnv limit) (E ++ [d]) (E ++ [d]).boundedNames := by
  have hnone : ∀ pred, E.find? (fun d' => d'.name == d.name && d'.isPred == pred) = none := fun pred => by
    rw [List.find?_eq_none]; intro x hx; have := List.any_eq_false.1 hnew x hx; simp_all
  have hfind : ∀ f pred d', E.find? (fun d => d.name == f && d.isPred == pred) = some d' → f ≠ d.name :=
    fun f pred d' h hf => by subst hf; simp [hnone] at h
  cases d with
  | fn f n body =>
    replace hnone : ∀ pred, E.find? (fun d' => d'.name == f && d'.isPred == pred) = none := hnone
    replace hfind : ∀ g pred d', E.find? (fun d => d.name == g && d.isPred == pred) = some d' → g ≠ f := hfind
    simp only [Def.SitesOk] at hs
    refine ⟨fun g d' hd' hB xs hlen => ?_, fun q d' hd' hB xs hlen => ?_⟩
    · by_cases hg : g = f
      · subst hg
        rw [List.find?_append, hnone, List.find?_singleton] at hd'
        simp [Def.name, Def.isPred] at hd'
        subst hd'
        simp only [boundedNames_snoc, ↓reduceIte] at hB
        obtain ⟨x, W, h⟩ := Term.evalB_total hT body 0 xs hB hs (by simpa [Def.arity] using hlen)
        exact ⟨x, W, fun limit => ⟨fun xs w => Term.evalB (Defs.opEnv limit E) limit xs body w,
          by simp only [opEnv_snoc, ↓reduceIte, Def.arity], fun w hw => h limit w hw⟩⟩
      · rw [List.find?_append, List.find?_singleton] at hd'
        have hd'' : E.find? (fun d => d.name == g && d.isPred == false) = some d' := by
          simpa [Def.name, Ne.symm hg] using hd'
        simp only [boundedNames_snoc, if_neg hg] at hB
        obtain ⟨x, W, h⟩ := hT.funs g d' hd'' hB xs hlen
        exact ⟨x, W, fun limit => by simpa [opEnv_snoc, hg] using h limit⟩
    · rw [List.find?_append, List.find?_singleton] at hd'
      have hd'' : E.find? (fun d => d.name == q && d.isPred == true) = some d' := by simpa [Def.isPred] using hd'
      simp only [boundedNames_snoc, if_neg (hfind q true d' hd'')] at hB
      obtain ⟨b, W, h⟩ := hT.preds q d' hd'' hB xs hlen
      exact ⟨b, W, fun limit => by simpa [opEnv_snoc] using h limit⟩
  | pred p n body =>
    replace hnone : ∀ pred, E.find? (fun d' => d'.name == p && d'.isPred == pred) = none := hnone
    replace hfind : ∀ g pred d', E.find? (fun d => d.name == g && d.isPred == pred) = some d' → g ≠ p := hfind
    simp only [Def.SitesOk] at hs
    refine ⟨fun g d' hd' hB xs hlen => ?_, fun q d' hd' hB xs hlen => ?_⟩
    · rw [List.find?_append, List.find?_singleton] at hd'
      have hd'' : E.find? (fun d => d.name == g && d.isPred == false) = some d' := by simpa [Def.isPred] using hd'
      simp only [boundedNames_snoc, if_neg (hfind g false d' hd'')] at hB
      obtain ⟨x, W, h⟩ := hT.funs g d' hd'' hB xs hlen
      exact ⟨x, W, fun limit => by simpa [opEnv_snoc] using h limit⟩
    · by_cases hq : q = p
      · subst hq
        rw [List.find?_append, hnone, List.find?_singleton] at hd'
        simp [Def.name, Def.isPred] at hd'
        subst hd'
        simp only [boundedNames_snoc, ↓reduceIte] at hB
        obtain ⟨b, W, h⟩ := Formula.evalB_total hT body 0 xs hB hs (by simpa [Def.arity] using hlen)
        exact ⟨b, W, fun limit => ⟨fun xs w => Formula.evalB (Defs.opEnv limit E) limit xs body w,
          by simp only [opEnv_snoc, ↓reduceIte, Def.arity], fun w hw => h limit w hw⟩⟩
      · rw [List.find?_append, List.find?_singleton] at hd'
        have hd'' : E.find? (fun d => d.name == q && d.isPred == true) = some d' := by
          simpa [Def.name, Ne.symm hq] using hd'
        simp only [boundedNames_snoc, if_neg hq] at hB
        obtain ⟨b, W, h⟩ := hT.preds q d' hd'' hB xs hlen
        exact ⟨b, W, fun limit => by simpa [opEnv_snoc, hq] using h limit⟩

theorem total_take (D : Defs) (hD : D.WellFormed = true) :
    ∀ k, Total (fun limit => Defs.opEnv limit (D.take k)) (D.take k) (Defs.boundedNames (D.take k))
  | 0 => ⟨fun _ _ h => by simp at h, fun _ _ h => by simp at h⟩
  | k + 1 => by
    rw [List.take_succ]
    cases hk : D[k]? with
    | none => simpa using total_take D hD k
    | some d => obtain ⟨h1, h2⟩ := wellFormed_at hD hk; exact (total_take D hD k).snoc h1 h2

/-- The work bound: a bounded, admitted statement has an answer and a number of units, fixed by the statement and its
definitions, that every budget covering those units returns. -/
theorem decideBounded_covered (D : Defs) (hD : D.WellFormed = true) (φ : Formula) (hφ : φ.Scoped D 0 = true)
    (hb : φ.Bounded D = true) : ∃ b W, ∀ limit, W ≤ limit → decideBounded D limit φ = some (b, W) := by
  have hT := total_take D hD D.length
  rw [List.take_length] at hT
  simp only [Formula.Scoped, List.isEmpty_iff, List.filterMap_eq_nil_iff] at hφ
  obtain ⟨b, W, h⟩ := Formula.evalB_total (depth := 0) hT φ 0 [] hb (fun s hs => Site.ok_of_refusal (hφ s hs)) rfl
  exact ⟨b, W, fun limit hl => by simpa using h limit 0 (by omega)⟩

theorem decideBounded_complete (D : Defs) (hD : D.WellFormed = true) (φ : Formula)
    (hφ : φ.Scoped D 0 = true) (hb : φ.Bounded D = true) : ∃ limit r, decideBounded D limit φ = some r := by
  obtain ⟨b, W, h⟩ := decideBounded_covered D hD φ hφ hb
  exact ⟨W, _, h W (Nat.le_refl W)⟩

end VE.Arith
