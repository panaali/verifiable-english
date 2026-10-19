import VE.Time.Semantics
import VE.Numbers.Round

/-! Rounding and percent-of for `cardinality@0` (docs/spec/quantities.md 3.8; plan QT-A2).

The meaning of "a / b rounds to D / 10^k under rule r" is `VE.Numbers.RoundsTo` (math-evidence owns it); this file
has no rounding definition of its own. `erasedRounding` is the linear integer form that erasure hands to W6a, and
`roundsTo_ratio_agree` proves it means exactly `RoundsTo` when `b > 0`. `halfEven`'s endpoints depend on the parity
of the literal `D`, so its erased form stays linear. A rounded percentage is `erasedRounding r (100 · a) b D k`.
`roundingQ` writes the same inequalities as W6a statements in the operands' tag. -/
namespace VE.Cardinality
open VE.Time (QTerm QFormula TStructure)
open VE.Numbers (Rounding RoundsTo tenPow)
universe u

/-- The linear integer form of "a / b rounds to D / 10^k under rule r" (b > 0) that erasure hands to W6a. -/
def erasedRounding : Rounding → Int → Int → Int → Nat → Prop
  | .tiesUp, a, b, D, k => (2 * D - 1) * b ≤ 2 * 10 ^ k * a ∧ 2 * 10 ^ k * a < (2 * D + 1) * b
  | .halfEven, a, b, D, k =>
      if D % 2 = 0 then (2 * D - 1) * b ≤ 2 * 10 ^ k * a ∧ 2 * 10 ^ k * a ≤ (2 * D + 1) * b
      else (2 * D - 1) * b < 2 * 10 ^ k * a ∧ 2 * 10 ^ k * a < (2 * D + 1) * b
  | .down, a, b, D, k => D * b ≤ 10 ^ k * a ∧ 10 ^ k * a < (D + 1) * b
  | .up, a, b, D, k => (D - 1) * b < 10 ^ k * a ∧ 10 ^ k * a ≤ D * b

/-- The same inequalities as W6a statements in the operands' tag `g`. -/
def roundingQ (g : String) (r : Rounding) (a b : QTerm) (D : Int) (k : Nat) : QFormula :=
  let s := fun (c : Int) (t : QTerm) => QTerm.scale g c t
  match r with
  | .tiesUp => .and (.le (s (2 * D - 1) b) (s (2 * 10 ^ k) a)) (.lt (s (2 * 10 ^ k) a) (s (2 * D + 1) b))
  | .halfEven =>
      if D % 2 = 0 then .and (.le (s (2 * D - 1) b) (s (2 * 10 ^ k) a)) (.le (s (2 * 10 ^ k) a) (s (2 * D + 1) b))
      else .and (.lt (s (2 * D - 1) b) (s (2 * 10 ^ k) a)) (.lt (s (2 * 10 ^ k) a) (s (2 * D + 1) b))
  | .down => .and (.le (s D b) (s (10 ^ k) a)) (.lt (s (10 ^ k) a) (s (D + 1) b))
  | .up => .and (.lt (s (D - 1) b) (s (10 ^ k) a)) (.le (s (10 ^ k) a) (s D b))

/-! ## The erased inequalities mean `RoundsTo` -/

/-- `c ≤ m · (a / b) · 10^k` and its kin, for `b > 0`, are the integer comparisons of `c · b` with `m · 10^k · a`. -/
theorem ratio_cmp (a b : Int) (k : Nat) (hb : 0 < b) (c m : Int) :
    ((c : Rat) ≤ m * ((a : Rat) / b * tenPow k) ↔ c * b ≤ m * 10 ^ k * a) ∧
    (m * ((a : Rat) / b * tenPow k) < c ↔ m * 10 ^ k * a < c * b) ∧
    ((c : Rat) < m * ((a : Rat) / b * tenPow k) ↔ c * b < m * 10 ^ k * a) ∧
    (m * ((a : Rat) / b * tenPow k) ≤ c ↔ m * 10 ^ k * a ≤ c * b) ∧
    (m * ((a : Rat) / b * tenPow k) = c ↔ m * 10 ^ k * a = c * b) := by
  have hB : (0 : Rat) < b := Rat.intCast_lt_intCast.mpr hb
  have hy : m * ((a : Rat) / b * tenPow k) = ((m * 10 ^ k * a : Int) : Rat) / b := by
    simp only [tenPow, Rat.div_def]; push_cast; grind
  have lt : ∀ u v : Int, ((u : Rat) / b < v ↔ u < v * b) := fun u v => by
    rw [Rat.div_lt_iff hB, ← Rat.intCast_mul, Rat.intCast_lt_intCast]
  have gt : ∀ u v : Int, ((v : Rat) < u / b ↔ v * b < u) := fun u v => by
    rw [Rat.lt_div_iff hB, ← Rat.intCast_mul, Rat.intCast_lt_intCast]
  have eq : ∀ u v : Int, ((u : Rat) / b = v ↔ u = v * b) := fun u v => by
    constructor
    · intro h
      have := congrArg (· * (b : Rat)) h
      simp only [Rat.div_mul_cancel (Rat.ne_of_gt hB)] at this
      exact Rat.intCast_inj.mp (by rw [this, Rat.intCast_mul])
    · intro h; rw [h, Rat.intCast_mul, Rat.mul_div_cancel (Rat.ne_of_gt hB)]
  rw [hy]
  refine ⟨?_, lt _ _, gt _ _, ?_, eq _ _⟩
  · rw [← Rat.not_lt, lt, Int.not_lt]
  · rw [← Rat.not_lt, gt, Int.not_lt]

/-- The erased inequalities mean exactly `VE.Numbers.RoundsTo` under the sentence's rule. -/
theorem roundsTo_ratio_agree (r : Rounding) (a b D : Int) (k : Nat) (hb : 0 < b) :
    erasedRounding r a b D k ↔ RoundsTo r ⟨D, (k : Int)⟩ ((a : Rat) / b) := by
  have h := ratio_cmp a b k hb
  cases r with
  | tiesUp =>
    have h1 := (h (2 * D - 1) 2).1
    have h2 := (h (2 * D + 1) 2).2.1
    push_cast at h1 h2
    simp only [erasedRounding, RoundsTo, h1, h2]
  | halfEven =>
    have h1 := (h (2 * D - 1) 2).2.2.1
    have h2 := (h (2 * D + 1) 2).2.1
    have e1 := (h (2 * D - 1) 2).2.2.2.2
    have e2 := (h (2 * D + 1) 2).2.2.2.2
    push_cast at h1 h2 e1 e2
    have hb' : (2 * D - 1) * b < (2 * D + 1) * b := by
      simp only [Int.sub_mul, Int.add_mul, Int.one_mul]; omega
    simp only [erasedRounding, RoundsTo, h1, h2, e1, e2]
    split <;> omega
  | down =>
    have h1 := (h D 1).1
    have h2 := (h (D + 1) 1).2.1
    push_cast [Rat.one_mul, Int.one_mul] at h1 h2
    simp only [erasedRounding, RoundsTo, h1, h2]
  | up =>
    have h1 := (h (D - 1) 1).2.2.1
    have h2 := (h D 1).2.2.2.1
    push_cast [Rat.one_mul, Int.one_mul] at h1 h2
    simp only [erasedRounding, RoundsTo, h1, h2]

/-! ## `roundingQ` is `erasedRounding` in W6a -/

theorem tcompare_qty {α : Type u} (R : Int → Int → Prop) (g : String) (a b : Int) :
    VE.Time.TCompare (α := α) R (some (.qty g a)) (some (.qty g b)) ↔ R a b :=
  ⟨fun ⟨_, _, _, h1, h2, h⟩ => by cases h1; cases h2; exact h, fun h => ⟨g, a, b, rfl, rfl, h⟩⟩

theorem roundingQ_iff {α : Type u} (W : TStructure α) (g : String) (r : Rounding) {a b : QTerm} {x y : Int}
    (D : Int) (k : Nat) (ha : a.tdenote W [] = some (.qty g x)) (hb : b.tdenote W [] = some (.qty g y)) :
    (roundingQ g r a b D k).tdenote W [] ↔ erasedRounding r x y D k := by
  cases r <;> simp only [roundingQ, erasedRounding] <;> (try split) <;>
    simp [QFormula.tdenote, QTerm.tdenote, tcompare_qty, ha, hb]

theorem roundingQ_admitted {E : VE.Time.QEnv} {Γ : List String} {g : String} (r : Rounding) {a b : QTerm}
    (D : Int) (k : Nat) (hg : g ≠ VE.Time.dayTag) (hv : E.ValidTag g) (ha : VE.Time.HasType E Γ a (.qty g))
    (hb : VE.Time.HasType E Γ b (.qty g)) : VE.Time.Admitted E Γ (roundingQ g r a b D k) := by
  cases r <;> simp only [roundingQ] <;> (try split) <;>
    exact .and (by constructor <;> first | exact .scale hg hv ha | exact .scale hg hv hb)
      (by constructor <;> first | exact .scale hg hv ha | exact .scale hg hv hb)

end VE.Cardinality
