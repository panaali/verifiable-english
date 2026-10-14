import VE.Time.Decimal

namespace VE.Numbers

/-- The exact value of a written decimal. -/
def decValue (d : VE.Time.Dec) : Rat :=
  (d.significand : Rat) / ((10 : Rat) ^ d.places)

/-- W6's exact lowering preserves the value of a decimal. -/
theorem decValue_lower (d : VE.Time.Dec) (k : Nat) (q : Int)
    (h : VE.Time.lower d k = some q) :
    decValue d = (q : Rat) / ((10 : Rat) ^ k) := by
  have he := (VE.Time.decimal_exact d k q).mp h
  simp only [decValue]
  have hpowd : (((10 : Int) ^ d.places : Int) : Rat) = (10 : Rat) ^ d.places := by
    simpa using Rat.intCast_pow (10 : Int) d.places
  have hpowk : (((10 : Int) ^ k : Int) : Rat) = (10 : Rat) ^ k := by
    simpa using Rat.intCast_pow (10 : Int) k
  rw [← hpowd, ← hpowk]
  rw [← Rat.divInt_eq_div, ← Rat.divInt_eq_div]
  apply (Rat.divInt_eq_divInt_iff (Int.pow_ne_zero (by decide))
    (Int.pow_ne_zero (by decide))).2
  exact he.2.symm

/-- Exact powers of ten, including negative powers. -/
def tenPow : Int → Rat
  | .ofNat n => (10 : Rat) ^ n
  | .negSucc n => 1 / (10 : Rat) ^ (n + 1)

private theorem tenPow_eq_zpow (k : Int) : tenPow k = (10 : Rat) ^ k := by
  cases k with
  | ofNat n => rfl
  | negSucc n =>
      change 1 / (10 : Rat) ^ (n + 1) = ((10 : Rat) ^ (n + 1))⁻¹
      simp [Rat.div_def]

theorem tenPow_pos (k : Int) : 0 < tenPow k := by
  rw [tenPow_eq_zpow]
  exact Rat.zpow_pos (by decide)

theorem tenPow_add (a b : Int) : tenPow (a + b) = tenPow a * tenPow b := by
  simp only [tenPow_eq_zpow]
  exact Rat.zpow_add (by decide) a b

end VE.Numbers
