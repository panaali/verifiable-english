import VE.Numbers.Round
import VE.Numbers.Bits

/-! Exact statistics (math-evidence spec 7, ME-7): the mean, the sample and population variances, a square root
rounded by squared bounds, the exact sign-flip p value, the Stats.binomial tail and Cohen's kappa. Each statistic of a list
is undefined outside its domain (statement review J5); `signFlipC` charges the 2ⁿ sign vectors against a limit. -/

namespace VE.Calc
open VE.Numbers

def mean? (xs : List Rat) : Option Rat := if xs = [] then none else some (xs.sum / xs.length)

def sampleVariance? (xs : List Rat) : Option Rat :=
  if xs.length < 2 then none
  else
    let m := xs.sum / xs.length
    some ((xs.map fun x => (x - m) * (x - m)).sum / (xs.length - 1 : Nat))

def populationVariance? (xs : List Rat) : Option Rat :=
  if xs = [] then none
  else
    let m := xs.sum / xs.length
    some ((xs.map fun x => (x - m) * (x - m)).sum / xs.length)

def rootGe (v c : Rat) : Prop := c ≤ 0 ∨ c * c ≤ v     -- √v ≥ c
def rootGt (v c : Rat) : Prop := c < 0 ∨ c * c < v     -- √v > c
def rootLe (v c : Rat) : Prop := 0 ≤ c ∧ v ≤ c * c     -- √v ≤ c
def rootLt (v c : Rat) : Prop := 0 < c ∧ v < c * c     -- √v < c
def rootEq (v c : Rat) : Prop := 0 ≤ c ∧ c * c = v     -- √v = c

instance (v c : Rat) : Decidable (rootGe v c) := by unfold rootGe; infer_instance
instance (v c : Rat) : Decidable (rootGt v c) := by unfold rootGt; infer_instance
instance (v c : Rat) : Decidable (rootLe v c) := by unfold rootLe; infer_instance
instance (v c : Rat) : Decidable (rootLt v c) := by unfold rootLt; infer_instance
instance (v c : Rat) : Decidable (rootEq v c) := by unfold rootEq; infer_instance

/-- "The square root of v, rounded, is p", by squared bounds; this is the definition. -/
def SqrtRoundsTo (r : Rounding) (p : Printed) (v : Rat) : Prop :=
  let u := tenPow p.places
  let D : Rat := p.digits
  0 ≤ v ∧ match r with
  | .tiesUp => rootGe v ((2 * D - 1) / (2 * u)) ∧ rootLt v ((2 * D + 1) / (2 * u))
  | .halfEven => (rootGt v ((2 * D - 1) / (2 * u)) ∧ rootLt v ((2 * D + 1) / (2 * u))) ∨
      ((rootEq v ((2 * D - 1) / (2 * u)) ∨ rootEq v ((2 * D + 1) / (2 * u))) ∧ p.digits % 2 = 0)
  | .down => rootGe v (D / u) ∧ rootLt v ((D + 1) / u)
  | .up => rootGt v ((D - 1) / u) ∧ rootLe v (D / u)

instance (r : Rounding) (p : Printed) (v : Rat) : Decidable (SqrtRoundsTo r p v) := by
  unfold SqrtRoundsTo; cases r <;> exact inferInstance

theorem Stats.sq_le_sq {a b : Rat} (ha : 0 ≤ a) (hb : 0 ≤ b) : a * a ≤ b * b ↔ a ≤ b := by
  constructor
  · intro h
    apply Classical.byContradiction; intro hn
    have := Rat.mul_pos (show 0 < a - b by grind) (show 0 < a + b by grind)
    grind
  · intro h
    have := Rat.mul_nonneg (show 0 ≤ b - a by grind) (show 0 ≤ b + a by grind)
    grind

theorem Stats.sq_lt_sq {a b : Rat} (ha : 0 ≤ a) (hb : 0 ≤ b) : a * a < b * b ↔ a < b := by
  have h1 := Stats.sq_le_sq hb ha
  constructor
  · intro h; apply Classical.byContradiction; intro hn; grind
  · intro h; apply Classical.byContradiction; intro hn; grind

/-- Over a root `s ≥ 0` of `v`, each squared bound is the comparison with `s`. -/
theorem Stats.root_iff {s v : Rat} (hs : 0 ≤ s) (hv : s * s = v) (c : Rat) :
    (rootGe v c ↔ c ≤ s) ∧ (rootGt v c ↔ c < s) ∧ (rootLe v c ↔ s ≤ c) ∧ (rootLt v c ↔ s < c) ∧
      (rootEq v c ↔ c = s) := by
  subst hv
  refine ⟨?_, ?_, ?_, ?_, ?_⟩
  · by_cases hc : c ≤ 0 <;> simp only [rootGe, hc, true_or, false_or] <;> grind [Stats.sq_le_sq]
  · by_cases hc : c < 0 <;> simp only [rootGt, hc, true_or, false_or] <;> grind [Stats.sq_lt_sq]
  · by_cases hc : 0 ≤ c <;> simp only [rootLe, hc, true_and, false_and] <;> grind [Stats.sq_le_sq]
  · by_cases hc : 0 < c <;> simp only [rootLt, hc, true_and, false_and] <;> grind [Stats.sq_lt_sq]
  · by_cases hc : 0 ≤ c <;> simp only [rootEq, hc, true_and, false_and]
    · constructor
      · intro h; have := (Stats.sq_le_sq hc hs).mp (by grind); have := (Stats.sq_le_sq hs hc).mp (by grind); grind
      · intro h; subst h; rfl
    · grind

theorem Stats.div_le_iff_mul {a s w : Rat} (hw : 0 < w) : a / w ≤ s ↔ a ≤ s * w := by
  have := Rat.lt_div_iff (b := a) (a := s) hw; grind
theorem Stats.le_div_iff_mul {a s w : Rat} (hw : 0 < w) : s ≤ a / w ↔ s * w ≤ a := by
  have := Rat.div_lt_iff (a := a) (c := s) hw; grind
theorem Stats.div_eq_iff_mul {a s w : Rat} (hw : 0 < w) : a / w = s ↔ a = s * w := by
  have := @Stats.div_le_iff_mul a s w hw; have := @Stats.le_div_iff_mul a s w hw; grind

/-- Agreement with rounding the root whenever the root is rational. -/
theorem sqrtRoundsTo_of_square (r : Rounding) (p : Printed) (s v : Rat) (hs : 0 ≤ s) (hv : s * s = v) :
    SqrtRoundsTo r p v ↔ RoundsTo r p s := by
  have hu := tenPow_pos p.places
  have h2u : 0 < 2 * tenPow p.places := by grind
  have hv0 : 0 ≤ v := hv ▸ Rat.mul_nonneg hs hs
  have R := Stats.root_iff hs hv
  cases r <;>
    simp only [SqrtRoundsTo, RoundsTo, hv0, true_and, (R _).1, (R _).2.1, (R _).2.2.1, (R _).2.2.2.1,
      (R _).2.2.2.2, Stats.div_le_iff_mul hu, Stats.div_le_iff_mul h2u, Rat.div_lt_iff hu, Rat.div_lt_iff h2u, Stats.le_div_iff_mul hu,
      Rat.lt_div_iff hu, Rat.lt_div_iff h2u, Stats.div_eq_iff_mul h2u] <;> grind

def signs : Nat → List (List Int)
  | 0 => [[]]
  | n + 1 => (signs n).flatMap fun s => [1 :: s, -1 :: s]

theorem signs_length (n : Nat) : (signs n).length = 2 ^ n := by
  have step (l : List (List Int)) : (l.flatMap fun s => [1 :: s, -1 :: s]).length = 2 * l.length := by
    induction l with
    | nil => rfl
    | cons s l ih => simp only [List.flatMap_cons, List.length_append, ih]; simp; omega
  induction n with
  | zero => rfl
  | succ n ih => rw [signs, step, ih, Nat.pow_succ, Nat.mul_comm]

theorem mem_signs (n : Nat) (s : List Int) : s ∈ signs n ↔ s.length = n ∧ ∀ k ∈ s, k = 1 ∨ k = -1 := by
  induction n generalizing s with
  | zero => cases s <;> simp [signs]
  | succ n ih =>
      cases s with
      | nil => simp [signs]
      | cons k t =>
          simp only [signs, List.mem_flatMap, List.mem_cons, List.cons.injEq,
            List.not_mem_nil, or_false, List.length_cons, Nat.add_right_cancel_iff, forall_eq_or_imp]
          constructor
          · rintro ⟨t', ht', (⟨rfl, rfl⟩ | ⟨rfl, rfl⟩)⟩ <;> simp_all
          · rintro ⟨hl, hk, ht⟩
            exact ⟨t, (ih t).mpr ⟨hl, ht⟩, by rcases hk with rfl | rfl <;> simp⟩

def absR (x : Rat) : Rat := if x < 0 then -x else x

/-- The exact two-sided sign-flip p value: the share of sign vectors whose signed mean is at least the observed mean
in absolute value, the observed vector counted (`paper/analysis/README.md`). -/
def signFlipP (d : List Rat) : Rat :=
  let obs := absR (d.sum / d.length)
  let hits := (signs d.length).filter fun s =>
    decide (obs ≤ absR ((List.zipWith (fun (k : Int) (x : Rat) => (k : Rat) * x) s d).sum / d.length))
  (hits.length : Rat) / ((2 ^ d.length : Nat) : Rat)

theorem signFlipP_grain (d : List Rat) :
    ∃ m : Nat, m ≤ 2 ^ d.length ∧ signFlipP d = (m : Rat) / ((2 ^ d.length : Nat) : Rat) :=
  ⟨_, signs_length d.length ▸ List.length_filter_le _ _, rfl⟩

/-- The limit of spec 7: a sign flip over more than 16 values is refused at decode (`SignFlipTooLong`). -/
def maxSignFlip : Nat := 16

/-- 12.2's units for `signFlipP d` (one per value computed plus its bits, `bits` of the numerator and of the
denominator), known before it runs and never below its work. There are `2ⁿ + 2` rows: the 2ⁿ sign vectors, the
observed mean, and the values read with the final share. Each row has at most `4n + 8` values: a sign, its entry in
the vector, a product and a partial sum per value, then the length, the mean, its absolute value and the comparison.
Each value is one visit plus at most `A + 2 · bits L + 2n + 2` bits, `A` the largest numerator's bits and `L` the
least common multiple of the denominators: a partial sum's denominator divides `L` and its numerator is below
`n · 2^A · L`, and dividing by `n` adds `bits n ≤ n + 1` (me-7-signflip-bits; the charge before it counted the
length only). -/
def signFlipWork (d : List Rat) : Nat :=
  let n := d.length
  let A := (d.map fun x => bits x.num).foldl max 0
  let L := (d.map (·.den)).foldl Nat.lcm 1
  (2 ^ n + 2) * (4 * n + 8) * (A + 2 * bits L + 2 * n + 3)

/-- The sign-flip p value charged its work first: none (UNKNOWN) when the work passes the limit. -/
def signFlipC (limit : Nat) (d : List Rat) : Option (Rat × Nat) :=
  if signFlipWork d ≤ limit then some (signFlipP d, signFlipWork d) else none

theorem signFlipC_sound (limit : Nat) (d : List Rat) (q : Rat) (w : Nat) (h : signFlipC limit d = some (q, w)) :
    q = signFlipP d ∧ w = signFlipWork d ∧ w ≤ limit := by
  unfold signFlipC at h; split at h <;> simp_all

theorem signFlipC_complete (limit : Nat) (d : List Rat) (h : signFlipWork d ≤ limit) :
    signFlipC limit d = some (signFlipP d, signFlipWork d) := by
  simp [signFlipC, h]

/-- Core Lean v4.24.0 has no `Nat.choose` (checked in the stub), so ME-7 defines it. -/
def choose : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, k + 1 => choose n k + choose n (k + 1)

theorem choose_succ_succ (n k : Nat) : choose (n + 1) (k + 1) = choose n k + choose n (k + 1) := rfl

/-- P(X ≥ k) for X Stats.binomial with n trials and success probability p. -/
def binomialTail (n k : Nat) (p : Rat) : Rat :=
  ((List.range (n + 1)).filter (k ≤ ·)).foldl
    (fun acc i => acc + (choose n i : Rat) * p ^ i * (1 - p) ^ (n - i)) 0

theorem Stats.choose_eq_zero : ∀ {n k : Nat}, n < k → choose n k = 0
  | 0, _ + 1, _ => rfl
  | n + 1, k + 1, h => by
      rw [choose_succ_succ, Stats.choose_eq_zero (by omega : n < k), Stats.choose_eq_zero (by omega : n < k + 1)]

theorem Stats.foldl_add (g : Nat → Rat) (l : List Nat) (c : Rat) :
    l.foldl (fun acc i => acc + g i) c = c + (l.map g).sum := by
  induction l generalizing c with
  | nil => simp only [List.foldl_nil, List.map_nil, List.sum_nil]; grind
  | cons i l ih => simp only [List.foldl_cons, ih, List.map_cons, List.sum_cons]; grind

theorem Stats.sum_map_add (f g : Nat → Rat) (l : List Nat) :
    (l.map fun i => f i + g i).sum = (l.map f).sum + (l.map g).sum := by
  induction l with
  | nil => simp only [List.map_nil, List.sum_nil]; grind
  | cons i l ih => simp only [List.map_cons, List.sum_cons, ih]; grind

theorem Stats.sum_map_mul (a : Rat) (f : Nat → Rat) (l : List Nat) :
    (l.map fun i => a * f i).sum = a * (l.map f).sum := by
  induction l with
  | nil => simp
  | cons i l ih => simp only [List.map_cons, List.sum_cons, ih]; grind

theorem Stats.sum_append (l l' : List Rat) : (l ++ l').sum = l.sum + l'.sum := by
  induction l with
  | nil => simp only [List.nil_append, List.sum_nil]; grind
  | cons x l ih => simp only [List.cons_append, List.sum_cons, ih]; grind

theorem Stats.sum_congr {f g : Nat → Rat} {l : List Nat} (h : ∀ i ∈ l, f i = g i) :
    (l.map f).sum = (l.map g).sum := by
  rw [List.map_congr_left h]

/-- The Stats.binomial theorem over `choose`. -/
theorem Stats.binomial (a b : Rat) (n : Nat) :
    ((List.range (n + 1)).map fun i => (choose n i : Rat) * a ^ i * b ^ (n - i)).sum = (a + b) ^ n := by
  induction n with
  | zero => simp [choose]; grind
  | succ n ih =>
      rw [List.range_succ_eq_map, List.map_cons, List.sum_cons, List.map_map]
      have hs : ∀ i ∈ List.range (n + 1),
          ((fun i => (choose (n + 1) i : Rat) * a ^ i * b ^ (n + 1 - i)) ∘ Nat.succ) i =
            a * ((choose n i : Rat) * a ^ i * b ^ (n - i)) + (choose n (i + 1) : Rat) * a ^ (i + 1) * b ^ (n - i) := by
        intro i _
        simp only [Function.comp, Nat.succ_eq_add_one, choose_succ_succ, Rat.natCast_add, Nat.add_sub_add_right,
          Rat.pow_succ]
        grind
      rw [Stats.sum_congr hs, Stats.sum_map_add, Stats.sum_map_mul, ih]
      -- b · Σ C(n, i) aⁱ bⁿ⁻ⁱ, split at i = 0, is bⁿ⁺¹ plus the shifted sum without its last term C(n, n + 1) = 0.
      have hb : b * (a + b) ^ n = b ^ (n + 1) +
          ((List.range n).map fun i => (choose n (i + 1) : Rat) * a ^ (i + 1) * b ^ (n - i)).sum := by
        rw [← ih, ← Stats.sum_map_mul, List.range_succ_eq_map, List.map_cons, List.sum_cons, List.map_map]
        have ht : ∀ i ∈ List.range n, ((fun i => b * ((choose n i : Rat) * a ^ i * b ^ (n - i))) ∘ Nat.succ) i =
            (choose n (i + 1) : Rat) * a ^ (i + 1) * b ^ (n - i) := by
          intro i hi
          have : n - i = n - (i + 1) + 1 := by simp at hi; omega
          simp only [Function.comp, Nat.succ_eq_add_one, this, Rat.pow_succ]
          grind
        rw [Stats.sum_congr ht]
        simp [choose, Rat.pow_succ]
        grind
      rw [List.range_succ, List.map_append, Stats.sum_append]
      simp only [List.map_cons, List.map_nil, List.sum_cons, List.sum_nil, Stats.choose_eq_zero (Nat.lt_succ_self n),
        Nat.sub_zero, Rat.pow_zero, Rat.pow_succ (a + b)]
      simp only [choose]
      grind

theorem binomialTail_zero (n : Nat) (p : Rat) : binomialTail n 0 p = (p + (1 - p)) ^ n := by
  rw [binomialTail, Stats.foldl_add, ← Stats.binomial]
  rw [List.filter_eq_self.mpr (by simp)]; grind

theorem Stats.sum_filter_le (g : Nat → Rat) (P : Nat → Bool) (l : List Nat) (hg : ∀ i ∈ l, 0 ≤ g i) :
    0 ≤ ((l.filter P).map g).sum ∧ ((l.filter P).map g).sum ≤ (l.map g).sum := by
  induction l with
  | nil => simp only [List.filter_nil, List.map_nil, List.sum_nil]; grind
  | cons i l ih =>
      have := hg i (by simp)
      have ih := ih fun j hj => hg j (by simp [hj])
      cases h : P i <;> simp [h] <;> grind

/-- On its domain a Stats.binomial tail is a probability. -/
theorem binomialTail_unit (n k : Nat) (p : Rat) (h0 : 0 ≤ p) (h1 : p ≤ 1) :
    0 ≤ binomialTail n k p ∧ binomialTail n k p ≤ 1 := by
  have one : ∀ m : Nat, (1 : Rat) ^ m = 1 := fun m => by
    induction m with
    | zero => exact Rat.pow_zero 1
    | succ m ih => rw [Rat.pow_succ, ih]; grind
  have hall := Stats.binomial p (1 - p) n
  rw [show p + (1 - p) = 1 by grind, one] at hall
  rw [binomialTail, Stats.foldl_add]
  have := Stats.sum_filter_le (fun i => (choose n i : Rat) * p ^ i * (1 - p) ^ (n - i)) (k ≤ ·) (List.range (n + 1))
    fun i _ => Rat.mul_nonneg (Rat.mul_nonneg Rat.natCast_nonneg (Rat.pow_nonneg h0)) (Rat.pow_nonneg (by grind))
  grind

/-- Cohen's kappa of a square agreement table; none when the table is empty or chance agreement is 1. -/
def kappa? (t : List (List Nat)) : Option Rat :=
  let k := t.length
  let n : Rat := ((t.map List.sum).sum : Nat)
  if n = 0 then none else
  let po := ((List.range k).map fun i => (((t.getD i []).getD i 0 : Nat) : Rat)).sum / n
  let rowsum := t.map fun r => ((r.sum : Nat) : Rat)
  let colsum := (List.range k).map fun j => (((t.map fun r => r.getD j 0).sum : Nat) : Rat)
  let pe := (List.zipWith (· * ·) rowsum colsum).sum / (n * n)
  if pe = 1 then none else some ((po - pe) / (1 - pe))

/-- The statistics of a list of named values (spec 2.1). -/
inductive Stat where
  | mean | variance | populationVariance | signFlip
  deriving Repr, DecidableEq

/-- The shortest list each statistic of 2.1 is defined on (J5). -/
def Stat.minLength : Stat → Nat
  | .variance => 2
  | _ => 1

def Stat.run : Stat → List Rat → Option Rat
  | .mean, xs => mean? xs
  | .variance, xs => sampleVariance? xs
  | .populationVariance, xs => populationVariance? xs
  | .signFlip, xs => if xs = [] then none else some (signFlipP xs)

theorem Stat.run_isSome (s : Stat) (xs : List Rat) : (s.run xs).isSome = true ↔ s.minLength ≤ xs.length := by
  cases s <;> cases xs <;>
    simp [Stat.run, Stat.minLength, mean?, sampleVariance?, populationVariance?] <;> omega

end VE.Calc
