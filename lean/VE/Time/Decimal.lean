import Std

/-! W6 exact decimal lowering (units-schema §2.3, obligation `Time.decimal_exact`).

A decimal literal is a sign, a whole part and fractional digits. On a unit whose
scale is `10^k`, lowering succeeds exactly when the scaled significand is
divisible by `10^p` (`p` fractional digits), and then yields that exact
quotient: there is no rounding. Rendering a coordinate with `k` places and
lowering it again recovers the coordinate (`lower_render`). The scale is a
power of ten by construction, so a zero or negative scale cannot arise. -/
namespace VE.Time

structure Dec where
  neg : Bool
  whole : Nat
  frac : List Nat
  deriving DecidableEq, Repr

/-- The value of a digit list, most significant first. -/
def digitsVal (ds : List Nat) : Nat := ds.foldl (fun acc d => acc * 10 + d) 0

def Dec.places (d : Dec) : Nat := d.frac.length

/-- The signed significand `m`: the literal's value is `m / 10^places`. -/
def Dec.significand (d : Dec) : Int :=
  (if d.neg then -1 else 1) * ((d.whole * 10 ^ d.places + digitsVal d.frac : Nat) : Int)

/-- Lowering onto the grid of scale `10^k`. -/
def lower (d : Dec) (k : Nat) : Option Int :=
  let numerator := d.significand * 10 ^ k
  let divisor : Int := 10 ^ d.places
  if numerator % divisor = 0 then some (numerator / divisor) else none

/-- **`Time.decimal_exact`**: lowering succeeds iff the literal is on the grid,
and the coordinate times `10^places` is exactly the scaled significand. -/
theorem decimal_exact (d : Dec) (k : Nat) (q : Int) :
    lower d k = some q ↔ ((10 : Int) ^ d.places ∣ d.significand * 10 ^ k ∧
      q * 10 ^ d.places = d.significand * 10 ^ k) := by
  have hpos : (10 : Int) ^ d.places ≠ 0 := by
    exact Int.pow_ne_zero (by decide)
  simp only [lower]
  constructor
  · intro h
    split at h
    · rename_i hg
      cases h
      have hdvd := Int.dvd_of_emod_eq_zero hg
      exact ⟨hdvd, Int.ediv_mul_cancel hdvd⟩
    · cases h
  · rintro ⟨hdvd, hq⟩
    rw [if_pos (Int.emod_eq_zero_of_dvd hdvd)]
    congr 1
    rw [← hq]
    exact Int.mul_ediv_cancel q hpos

/-- Off-grid literals are rejected, never rounded. -/
theorem lower_none_iff (d : Dec) (k : Nat) :
    lower d k = none ↔ ¬ (10 : Int) ^ d.places ∣ d.significand * 10 ^ k := by
  simp only [lower]
  constructor
  · intro h hdvd
    rw [if_pos (Int.emod_eq_zero_of_dvd hdvd)] at h
    cases h
  · intro h
    rw [if_neg (fun hz => h (Int.dvd_of_emod_eq_zero hz))]

/-- The low `k` decimal digits of `r`, most significant first. -/
def fracDigits : Nat → Nat → List Nat
  | 0, _ => []
  | k + 1, r => fracDigits k (r / 10) ++ [r % 10]

theorem digitsVal_append (xs : List Nat) (d : Nat) :
    digitsVal (xs ++ [d]) = digitsVal xs * 10 + d := by
  simp [digitsVal, List.foldl_append]

theorem fracDigits_length (k r : Nat) : (fracDigits k r).length = k := by
  induction k generalizing r with
  | zero => rfl
  | succ k ih => simp [fracDigits, ih]

theorem fracDigits_val (k r : Nat) : digitsVal (fracDigits k r) = r % 10 ^ k := by
  induction k generalizing r with
  | zero => simp [fracDigits, digitsVal, Nat.mod_one]
  | succ k ih =>
    rw [fracDigits, digitsVal_append, ih, Nat.pow_succ, Nat.mul_comm (10 ^ k) 10, Nat.mod_mul]
    omega

theorem fracDigits_lt (k r : Nat) : ∀ x ∈ fracDigits k r, x < 10 := by
  induction k generalizing r with
  | zero => simp [fracDigits]
  | succ k ih =>
    intro x hx
    simp only [fracDigits, List.mem_append, List.mem_singleton] at hx
    rcases hx with hx | hx
    · exact ih _ x hx
    · omega

/-- Canonical rendering of coordinate `q` with `k` fractional digits. -/
def render (k : Nat) (q : Int) : Dec :=
  ⟨decide (q < 0), q.natAbs / 10 ^ k, fracDigits k (q.natAbs % 10 ^ k)⟩

theorem render_significand (k : Nat) (q : Int) : (render k q).significand = q := by
  unfold render Dec.significand Dec.places
  simp only [fracDigits_length, fracDigits_val, Nat.mod_mod]
  have hsplit : q.natAbs / 10 ^ k * 10 ^ k + q.natAbs % 10 ^ k = q.natAbs := Nat.div_add_mod' _ _
  rw [hsplit]
  by_cases hq : q < 0
  · simp only [hq, decide_true, if_true]
    omega
  · simp only [hq, decide_false, Bool.false_eq_true, if_false, Int.one_mul]
    omega

/-- **Rendering inverse**: lowering the canonical rendering on the same grid
recovers exactly the coordinate. -/
theorem lower_render (k : Nat) (q : Int) : lower (render k q) k = some q := by
  have hplaces : (render k q).places = k := fracDigits_length _ _
  rw [decimal_exact, hplaces, render_significand]
  exact ⟨Int.dvd_mul_left _ _, rfl⟩

/-- Rendering never produces negative zero. -/
theorem render_zero (k : Nat) : (render k 0).neg = false := by simp [render]

/-! ## Wire spelling (boundary code, differentially tested against Python/Rust) -/

def maxNumeralChars : Nat := 40

def digitOf (c : Char) : Option Nat :=
  if 48 ≤ c.toNat ∧ c.toNat ≤ 57 then some (c.toNat - 48) else none

def digitList (cs : List Char) : Option (List Nat) := cs.mapM digitOf

/-- `-?(0|[1-9][0-9]*)(\.[0-9]+)?` with at most 40 digits; sign and point are
not counted, so every admitted coordinate's rendering reparses (at most 40
characters rendered with at most 39 places has at most 40 digits). -/
def parseDecimal (s : String) : Except String Dec := do
  if (s.toList.filter (fun c => (digitOf c).isSome)).length > maxNumeralChars then
    throw s!"ResourceLimit: Decimal literal exceeds {maxNumeralChars} digits"
  let invalid := s!"Invalid decimal literal {s.quote}"
  let (neg, body) := match s.toList with
    | '-' :: rest => (true, rest)
    | cs => (false, cs)
  let (wholeChars, fracChars) := match body.span (· != '.') with
    | (w, []) => (w, none)
    | (w, _ :: f) => (w, some f)
  let some whole := digitList wholeChars | throw invalid
  if whole.isEmpty || (whole.length > 1 && whole.head? == some 0) then throw invalid
  let frac ← match fracChars with
    | none => pure []
    | some f => match digitList f with
      | some ds => if ds.isEmpty then throw invalid else pure ds
      | none => throw invalid
  pure ⟨neg, digitsVal whole, frac⟩

def Dec.toString (d : Dec) : String :=
  (if d.neg then "-" else "") ++ Nat.repr d.whole ++
    (if d.frac.isEmpty then "" else "." ++ String.mk (d.frac.map (fun x => Char.ofNat (48 + x))))

/-- The coordinate display amount with `k` places (Python `render_coordinate`). -/
def renderAmount (k : Nat) (q : Int) : String := (render k q).toString

end VE.Time
