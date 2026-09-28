import Std

/-! Small audited arithmetic facts for W6a's exact grid and endpoint conventions.
They do not decode wire statements or certify W6 quantities. -/
namespace VE.Time

/-- Integer-coordinate lowering of a signed decimal significand `m` with `p`
places on scale `s`. The source decoder must establish that these parameters
really came from the submitted decimal text. -/
def lowerOnGrid (m : Int) (p : Nat) (s : Int) : Option Int :=
  let numerator := m * s
  let divisor := (10 : Int) ^ p
  if numerator % divisor = 0 then some (numerator / divisor) else none

/-- Successful grid lowering has exactly the submitted rational value. -/
theorem coordinate_exact_of_lowering (m : Int) (p : Nat) (s q : Int)
    (h : lowerOnGrid m p s = some q) : q * (10 : Int) ^ p = m * s := by
  by_cases hgrid : (m * s) % (10 : Int) ^ p = 0
  · have hq : (m * s) / (10 : Int) ^ p = q := by
      simpa [lowerOnGrid, hgrid] using h
    rw [← hq]
    exact Int.ediv_mul_cancel (Int.dvd_of_emod_eq_zero hgrid)
  · simp [lowerOnGrid, hgrid] at h

/-- An accepted nominal comparison carries the same tag at both operands. -/
def sameTag (left right : String) : Bool := decide (left = right)

theorem sameTag_sound (left right : String) (h : sameTag left right = true) :
    left = right := by
  simpa [sameTag] using h

/-- The fixed display interval for supported day coordinates. -/
def validDateCoordinate (d : Int) : Prop := 0 ≤ d ∧ d ≤ 2932896

/-- A forward `n`-day interval includes both endpoints. -/
def withinDays (t d : Int) (n : Nat) : Prop :=
  validDateCoordinate d ∧ validDateCoordinate t ∧ d ≤ t ∧ t ≤ d + n

/-- A zero-day inclusive interval contains exactly its origin date. -/
theorem within_zero_iff_on (t d : Int) :
    withinDays t d 0 ↔ validDateCoordinate d ∧ validDateCoordinate t ∧ t = d := by
  constructor
  · intro h
    rcases h with ⟨hd, ht, hdt, htd⟩
    have heq : t = d := by omega
    exact ⟨hd, ht, heq⟩
  · rintro ⟨hd, ht, rfl⟩
    exact ⟨hd, ht, by omega, by omega⟩

/-- Signed elapsed duration is the exact difference of the two day coordinates. -/
theorem elapsed_difference_iff (d t v : Int) : v = t - d ↔ d + v = t := by
  constructor <;> intro h <;> omega

end VE.Time
