import VE.Order.Consequence

/-! Linear integer forms over declared integer constants.

A form is a constant plus a list of (constant name, coefficient) pairs. The
list need not be normalized; `collect` merges repeated names and is proved to
preserve the value. Every integer term of a well-typed order formula is ground
(integer binders are excluded), so linearization never sees a variable. -/
namespace VE.Order
universe u

structure Lin where
  const : Int
  coeffs : List (String × Int)
  deriving DecidableEq, Repr

def sumTerms (κ : String → Int) : List (String × Int) → Int
  | [] => 0
  | (c, k) :: rest => k * κ c + sumTerms κ rest

def Lin.eval (κ : String → Int) (L : Lin) : Int := L.const + sumTerms κ L.coeffs

def Lin.zero : Lin := ⟨0, []⟩
def Lin.add (a b : Lin) : Lin := ⟨a.const + b.const, a.coeffs ++ b.coeffs⟩
def Lin.smul (k : Int) (a : Lin) : Lin := ⟨k * a.const, a.coeffs.map (fun p => (p.1, k * p.2))⟩
def Lin.sub (a b : Lin) : Lin := a.add (b.smul (-1))
def Lin.shift (a : Lin) (z : Int) : Lin := ⟨a.const + z, a.coeffs⟩

theorem sumTerms_append (κ : String → Int) (xs ys : List (String × Int)) :
    sumTerms κ (xs ++ ys) = sumTerms κ xs + sumTerms κ ys := by
  induction xs with
  | nil => simp [sumTerms]
  | cons p xs ih =>
    obtain ⟨c, k⟩ := p
    simp only [List.cons_append, sumTerms, ih]
    omega

theorem sumTerms_smul (κ : String → Int) (k : Int) (xs : List (String × Int)) :
    sumTerms κ (xs.map (fun p => (p.1, k * p.2))) = k * sumTerms κ xs := by
  induction xs with
  | nil => simp [sumTerms]
  | cons p xs ih =>
    obtain ⟨c, m⟩ := p
    simp only [List.map_cons, sumTerms, ih, Int.mul_add, Int.mul_assoc]

theorem Lin.eval_zero (κ : String → Int) : Lin.zero.eval κ = 0 := by
  simp [Lin.zero, Lin.eval, sumTerms]

theorem Lin.eval_add (κ : String → Int) (a b : Lin) :
    (a.add b).eval κ = a.eval κ + b.eval κ := by
  simp only [Lin.eval, Lin.add, sumTerms_append]
  omega

theorem Lin.eval_smul (κ : String → Int) (k : Int) (a : Lin) :
    (a.smul k).eval κ = k * a.eval κ := by
  simp only [Lin.eval, Lin.smul, sumTerms_smul, Int.mul_add]

theorem Lin.eval_sub (κ : String → Int) (a b : Lin) :
    (a.sub b).eval κ = a.eval κ - b.eval κ := by
  simp only [Lin.sub, Lin.eval_add, Lin.eval_smul]
  omega

theorem Lin.eval_shift (κ : String → Int) (a : Lin) (z : Int) :
    (a.shift z).eval κ = a.eval κ + z := by
  simp only [Lin.eval, Lin.shift]
  omega

/-- Linearization accepts only integer-typed constants, numerals, sums and
literal scalings. Variables and object constants are rejected. -/
def linearize (E : Environment) : Term → Option Lin
  | .var _ => none
  | .const c => if E.constants c = some .int then some ⟨0, [(c, 1)]⟩ else none
  | .num z => some ⟨z, []⟩
  | .add t u => match linearize E t, linearize E u with
    | some a, some b => some (a.add b)
    | _, _ => none
  | .scale k t => match linearize E t with
    | some a => some (a.smul k)
    | none => none

/-- The integer denoted by each constant; object or absent constants read 0,
which is never consulted for linearized terms in admissible structures. -/
def intValue (S : Structure.{u}) (c : String) : Int :=
  match S.constant c with
  | some (.inr z) => z
  | _ => 0

theorem linearize_denote {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (ρ : Valuation S) (t : Term) (L : Lin) (h : linearize E t = some L) :
    t.denote S ρ = some (.inr (L.eval (intValue S))) := by
  induction t generalizing L with
  | var i => simp [linearize] at h
  | const c =>
    simp only [linearize] at h
    split at h
    next hc =>
      cases h
      obtain ⟨v, hv, hd⟩ := hS.1 c .int hc
      obtain ⟨z, rfl⟩ := integer_of_domain hd
      simp [Term.denote, hv, Lin.eval, sumTerms, intValue]
    next => contradiction
  | num z =>
    simp only [linearize, Option.some.injEq] at h
    subst h
    simp [Term.denote, Lin.eval, sumTerms]
  | add t u it iu =>
    simp only [linearize] at h
    split at h
    next a b ha hb =>
      cases h
      simp [Term.denote, it a ha, iu b hb, Lin.eval_add]
    next => contradiction
  | scale k t it =>
    simp only [linearize] at h
    split at h
    next a ha =>
      cases h
      simp [Term.denote, it a ha, Lin.eval_smul]
    next => contradiction

/-- Merge one coefficient into a list, adding to an existing entry for the name. -/
def insertCoeff (c : String) (k : Int) : List (String × Int) → List (String × Int)
  | [] => [(c, k)]
  | (d, m) :: rest => if c = d then (d, m + k) :: rest else (d, m) :: insertCoeff c k rest

def collect : List (String × Int) → List (String × Int)
  | [] => []
  | (c, k) :: rest => insertCoeff c k (collect rest)

theorem sumTerms_insert (κ : String → Int) (c : String) (k : Int) (xs : List (String × Int)) :
    sumTerms κ (insertCoeff c k xs) = k * κ c + sumTerms κ xs := by
  induction xs with
  | nil => simp [insertCoeff, sumTerms]
  | cons p xs ih =>
    obtain ⟨d, m⟩ := p
    by_cases h : c = d
    · subst h
      simp only [insertCoeff, if_true, sumTerms, Int.add_mul]
      omega
    · simp only [insertCoeff, h, if_false, sumTerms, ih]
      omega

theorem sumTerms_collect (κ : String → Int) (xs : List (String × Int)) :
    sumTerms κ (collect xs) = sumTerms κ xs := by
  induction xs with
  | nil => rfl
  | cons p xs ih =>
    obtain ⟨c, k⟩ := p
    simp only [collect, sumTerms_insert, ih, sumTerms]

def Lin.normal (L : Lin) : Lin := ⟨L.const, collect L.coeffs⟩

theorem Lin.eval_normal (κ : String → Int) (L : Lin) : L.normal.eval κ = L.eval κ := by
  simp [Lin.normal, Lin.eval, sumTerms_collect]

theorem sumTerms_zero (κ : String → Int) (xs : List (String × Int))
    (h : xs.all (fun p => p.2 == 0) = true) : sumTerms κ xs = 0 := by
  induction xs with
  | nil => rfl
  | cons p xs ih =>
    obtain ⟨c, k⟩ := p
    simp only [List.all_cons, Bool.and_eq_true, beq_iff_eq] at h
    simp [sumTerms, h.1, ih h.2]

def divideLin (g : Int) (L : Lin) : Lin := ⟨L.const / g, L.coeffs.map (fun p => (p.1, p.2 / g))⟩

theorem sumTerms_divide (κ : String → Int) (g : Int) (xs : List (String × Int))
    (h : xs.all (fun p => p.2 % g == 0) = true) :
    sumTerms κ xs = g * sumTerms κ (xs.map (fun p => (p.1, p.2 / g))) := by
  induction xs with
  | nil => simp [sumTerms]
  | cons p xs ih =>
    obtain ⟨c, k⟩ := p
    simp only [List.all_cons, Bool.and_eq_true, beq_iff_eq] at h
    have hk : g * (k / g) = k := Int.mul_ediv_cancel' (Int.dvd_of_emod_eq_zero h.1)
    simp only [List.map_cons, sumTerms, ih h.2, Int.mul_add]
    rw [← Int.mul_assoc, hk]

/-- Rounding a scaled lower bound: the integer core of a Chvatal-Gomory cut. -/
theorem floor_bound (g b y : Int) (hg : 0 < g) (h : 0 ≤ b + g * y) : 0 ≤ b / g + y := by
  have hdiv : g * (b / g) + b % g = b := Int.mul_ediv_add_emod b g
  have hr0 : 0 ≤ b % g := Int.emod_nonneg b (by omega)
  have hr1 : b % g < g := Int.emod_lt_of_pos b hg
  have hsplit : b + g * y = g * (b / g + y) + b % g := by
    rw [Int.mul_add]
    omega
  apply Classical.byContradiction
  intro hn
  have hz : b / g + y ≤ -1 := by omega
  have hm : g * (b / g + y) ≤ g * (-1) := Int.mul_le_mul_of_nonneg_left hz (by omega)
  omega

theorem tighten_sound (κ : String → Int) (g : Int) (L : Lin) (hg : 0 < g)
    (hd : L.coeffs.all (fun p => p.2 % g == 0) = true) (h : 0 ≤ L.eval κ) :
    0 ≤ (divideLin g L).eval κ := by
  simp only [Lin.eval, divideLin] at h ⊢
  rw [sumTerms_divide κ g L.coeffs hd] at h
  exact floor_bound g L.const _ hg h

end VE.Order
