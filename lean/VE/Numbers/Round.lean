import VE.Numbers.Decimal

namespace VE.Numbers

structure Printed where
  digits : Int
  places : Int
  deriving Repr, DecidableEq

def Printed.value (p : Printed) : Rat := (p.digits : Rat) / tenPow p.places
def Printed.ofDec (d : VE.Time.Dec) : Printed := ⟨d.significand, (d.places : Int)⟩
def Printed.sci (d : VE.Time.Dec) (e : Int) : Printed :=
  ⟨d.significand, (d.places : Int) - e⟩

theorem Printed.value_ofDec (d : VE.Time.Dec) :
    (Printed.ofDec d).value = decValue d := by
  simp [Printed.value, Printed.ofDec, decValue, tenPow]

theorem Printed.value_sci (d : VE.Time.Dec) (e : Int) :
    (Printed.sci d e).value = decValue d * tenPow e := by
  have hp : tenPow ((d.places : Int) - e) * tenPow e = tenPow (d.places : Int) := by
    rw [← tenPow_add]
    simp
  have hne : tenPow ((d.places : Int) - e) ≠ 0 :=
    Rat.ne_of_gt (tenPow_pos _)
  have hneb : tenPow e ≠ 0 := Rat.ne_of_gt (tenPow_pos _)
  have hinv : (tenPow ((d.places : Int) - e))⁻¹ =
      (tenPow (d.places : Int))⁻¹ * tenPow e := by
    rw [← hp, Rat.inv_mul_rev]
    calc
      (tenPow ((d.places : Int) - e))⁻¹ =
          ((tenPow e)⁻¹ * tenPow e) * (tenPow ((d.places : Int) - e))⁻¹ := by
        rw [Rat.inv_mul_cancel _ hneb, Rat.one_mul]
      _ = (tenPow e)⁻¹ * (tenPow ((d.places : Int) - e))⁻¹ * tenPow e := by
        rw [Rat.mul_assoc, Rat.mul_comm (tenPow e)
          (tenPow ((d.places : Int) - e))⁻¹, ← Rat.mul_assoc]
  simp only [Printed.value, Printed.sci, decValue, Rat.div_def]
  change (d.significand : Rat) * (tenPow ((d.places : Int) - e))⁻¹ =
    (d.significand : Rat) * (tenPow (d.places : Int))⁻¹ * tenPow e
  rw [hinv, Rat.mul_assoc]

inductive Rounding where
  | tiesUp | halfEven | down | up
  deriving Repr, DecidableEq

def RoundsTo (r : Rounding) (p : Printed) (x : Rat) : Prop :=
  match r with
  | .tiesUp => 2 * (p.digits : Rat) - 1 ≤ 2 * (x * tenPow p.places) ∧
      2 * (x * tenPow p.places) < 2 * (p.digits : Rat) + 1
  | .halfEven =>
      (2 * (p.digits : Rat) - 1 < 2 * (x * tenPow p.places) ∧
        2 * (x * tenPow p.places) < 2 * (p.digits : Rat) + 1) ∨
      ((2 * (x * tenPow p.places) = 2 * (p.digits : Rat) - 1 ∨
        2 * (x * tenPow p.places) = 2 * (p.digits : Rat) + 1) ∧ p.digits % 2 = 0)
  | .down => (p.digits : Rat) ≤ x * tenPow p.places ∧
      x * tenPow p.places < (p.digits : Rat) + 1
  | .up => (p.digits : Rat) - 1 < x * tenPow p.places ∧
      x * tenPow p.places ≤ (p.digits : Rat)

instance (r : Rounding) (p : Printed) (x : Rat) : Decidable (RoundsTo r p x) := by
  cases r <;> dsimp [RoundsTo] <;> infer_instance

def Rounding.round (r : Rounding) (k : Int) (x : Rat) : Int :=
  match r with
  | .tiesUp => Rat.floor (x * tenPow k + 1 / 2)
  | .halfEven =>
      let f := Rat.floor (x * tenPow k + 1 / 2)
      if (f : Rat) = x * tenPow k + 1 / 2 ∧ f % 2 ≠ 0 then f - 1 else f
  | .down => Rat.floor (x * tenPow k)
  | .up => Rat.ceil (x * tenPow k)

theorem floor_eq_iff (z : Rat) (d : Int) :
    z.floor = d ↔ (d : Rat) ≤ z ∧ z < (d + 1 : Int) := by
  constructor
  · intro h
    rw [← h]
    exact ⟨Rat.floor_le z, Rat.lt_floor_add_one z⟩
  · rintro ⟨hlo, hhi⟩
    apply Int.le_antisymm
    · have h : z.floor < d + 1 := Rat.floor_lt_iff.mpr hhi
      omega
    · exact Rat.le_floor_iff.mpr hlo

theorem tiesUp_iff (p : Printed) (x : Rat) :
    RoundsTo .tiesUp p x ↔ Rounding.round .tiesUp p.places x = p.digits := by
  simp only [RoundsTo, Rounding.round, floor_eq_iff]
  grind

theorem down_iff (p : Printed) (x : Rat) :
    RoundsTo .down p x ↔ Rounding.round .down p.places x = p.digits := by
  simp only [RoundsTo, Rounding.round, floor_eq_iff, Rat.intCast_add]
  simp

theorem up_iff (p : Printed) (x : Rat) :
    RoundsTo .up p x ↔ Rounding.round .up p.places x = p.digits := by
  simp only [RoundsTo, Rounding.round, Rat.ceil_eq_neg_floor_neg]
  have hneg : -(-(x * tenPow p.places)).floor = p.digits ↔
      (-(x * tenPow p.places)).floor = -p.digits := by omega
  rw [hneg]
  rw [floor_eq_iff]
  simp only [Rat.intCast_neg, Rat.intCast_add]
  grind

theorem halfEven_interval (p : Printed) (x : Rat) :
    RoundsTo .halfEven p x ↔
      (((p.digits : Rat) < x * tenPow p.places + 1 / 2 ∧
          x * tenPow p.places + 1 / 2 < (p.digits + 1 : Int)) ∨
        ((x * tenPow p.places + 1 / 2 = (p.digits : Rat) ∨
          x * tenPow p.places + 1 / 2 = (p.digits + 1 : Int)) ∧
          p.digits % 2 = 0)) := by
  simp only [RoundsTo, Rat.intCast_add]
  grind

theorem interval_off_tie (z : Rat) (d : Int)
    (hz : (z.floor : Rat) ≠ z) :
    (((d : Rat) < z ∧ z < (d + 1 : Int)) ∨
      ((z = (d : Rat) ∨ z = (d + 1 : Int)) ∧ d % 2 = 0)) ↔ z.floor = d := by
  constructor
  · intro h
    rcases h with h | ⟨h, _⟩
    · exact (floor_eq_iff z d).mpr ⟨Rat.le_of_lt h.1, h.2⟩
    · rcases h with h | h
      · rw [h, Rat.floor_intCast] at hz
        exact False.elim (hz rfl)
      · rw [h, Rat.floor_intCast] at hz
        exact False.elim (hz rfl)
  · intro h
    have hb := (floor_eq_iff z d).mp h
    left
    constructor
    · grind
    · exact hb.2

theorem interval_on_tie (z : Rat) (d : Int)
    (hz : (z.floor : Rat) = z) :
    (((d : Rat) < z ∧ z < (d + 1 : Int)) ∨
      ((z = (d : Rat) ∨ z = (d + 1 : Int)) ∧ d % 2 = 0)) ↔
      (if z.floor % 2 ≠ 0 then z.floor - 1 else z.floor) = d := by
  let f := z.floor
  have hz' : z = (f : Rat) := hz.symm
  rw [hz']
  simp only [Rat.floor_intCast]
  have hno : ¬ ((d : Rat) < (f : Rat) ∧ (f : Rat) < (d + 1 : Int)) := by
    intro ⟨h1, h2⟩
    have h1' : d < f := Rat.intCast_lt_intCast.mp h1
    have h2' : f < d + 1 := Rat.intCast_lt_intCast.mp h2
    omega
  simp only [hno, false_or]
  have heq : ((f : Rat) = (d : Rat) ∨ (f : Rat) = (d + 1 : Int)) ↔
      (f = d ∨ f = d + 1) := by simp [← Rat.intCast_add, Rat.intCast_inj]
  rw [heq]
  by_cases ho : f % 2 ≠ 0
  · simp only [if_pos ho]
    omega
  · simp only [if_neg ho]
    omega

theorem halfEven_iff (p : Printed) (x : Rat) :
    RoundsTo .halfEven p x ↔ Rounding.round .halfEven p.places x = p.digits := by
  let z := x * tenPow p.places + 1 / 2
  rw [halfEven_interval]
  change (((p.digits : Rat) < z ∧ z < (p.digits + 1 : Int)) ∨
    ((z = (p.digits : Rat) ∨ z = (p.digits + 1 : Int)) ∧ p.digits % 2 = 0)) ↔
    (if (z.floor : Rat) = z ∧ z.floor % 2 ≠ 0 then z.floor - 1 else z.floor) = p.digits
  by_cases ht : (z.floor : Rat) = z
  · rw [interval_on_tie z p.digits ht]
    simp [ht]
  · rw [interval_off_tie z p.digits ht]
    simp [ht]

theorem roundsTo_iff_round (r : Rounding) (p : Printed) (x : Rat) :
    RoundsTo r p x ↔ r.round p.places x = p.digits := by
  cases r with
  | tiesUp => exact tiesUp_iff p x
  | halfEven => exact halfEven_iff p x
  | down => exact down_iff p x
  | up => exact up_iff p x

theorem roundsTo_round (r : Rounding) (k : Int) (x : Rat) :
    RoundsTo r ⟨r.round k x, k⟩ x := by
  rw [roundsTo_iff_round]

theorem roundsTo_unique (r : Rounding) (x : Rat) (p q : Printed)
    (hk : p.places = q.places) (hp : RoundsTo r p x) (hq : RoundsTo r q x) : p = q := by
  rw [roundsTo_iff_round] at hp hq
  cases p with
  | mk pd pk =>
    cases q with
    | mk qd qk =>
      simp only [Printed.mk.injEq] at *
      constructor
      · subst qk
        exact hp.symm.trans hq
      · exact hk

theorem roundsTo_close (p : Printed) (x : Rat) (h : RoundsTo .tiesUp p x) :
    -(1 / 2) ≤ x * tenPow p.places - p.digits ∧
      x * tenPow p.places - p.digits < 1 / 2 := by
  simp only [RoundsTo] at h
  grind

def tieAt (k : Int) (x : Rat) : Bool :=
  let z := 2 * (x * tenPow k)
  z.den == 1 && z.num % 2 != 0

theorem tieAt_iff (k : Int) (x : Rat) :
    tieAt k x = true ↔
      ∃ d : Int, 2 * (x * tenPow k) = ((2 * d - 1 : Int) : Rat) := by
  let z : Rat := 2 * (x * tenPow k)
  constructor
  · intro h
    have h' : z.den = 1 ∧ z.num % 2 ≠ 0 := by
      simpa [tieAt, z] using h
    have hz : z = (z.num : Rat) := by
      apply Rat.ext
      · simp
      · simpa using h'.1
    let d := (z.num + 1) / 2
    have hd : 2 * d - 1 = z.num := by omega
    refine ⟨d, ?_⟩
    change z = ((2 * d - 1 : Int) : Rat)
    rw [hz, hd]
  · rintro ⟨d, hd⟩
    change z = ((2 * d - 1 : Int) : Rat) at hd
    suffices z.den = 1 ∧ z.num % 2 ≠ 0 by simpa [tieAt, z] using this
    rw [hd]
    change (((2 * d - 1 : Int) : Rat).den = 1 ∧
      ((2 * d - 1 : Int) : Rat).num % 2 ≠ 0)
    constructor
    · exact Rat.den_intCast _
    · simpa only [Rat.num_intCast] using (by omega : (2 * d - 1 : Int) % 2 ≠ 0)

theorem tieAt_iff_floor_tie (k : Int) (x : Rat) :
    tieAt k x = true ↔
      ((Rat.floor (x * tenPow k + 1 / 2) : Int) : Rat) =
        x * tenPow k + 1 / 2 := by
  rw [tieAt_iff]
  constructor
  · rintro ⟨d, hd⟩
    have hz : x * tenPow k + 1 / 2 = (d : Rat) := by
      have hc : ((2 * d - 1 : Int) : Rat) = 2 * (d : Rat) - 1 := by norm_cast
      rw [hc] at hd
      grind
    rw [hz, Rat.floor_intCast]
  · intro ht
    let f := Rat.floor (x * tenPow k + 1 / 2)
    refine ⟨f, ?_⟩
    have hc : ((2 * f - 1 : Int) : Rat) = 2 * (f : Rat) - 1 := by norm_cast
    rw [hc]
    have hf : (f : Rat) = x * tenPow k + 1 / 2 := ht
    grind

theorem rules_differ_iff (k : Int) (x : Rat) :
    Rounding.round .tiesUp k x ≠ Rounding.round .halfEven k x ↔
      tieAt k x = true ∧ Rounding.round .tiesUp k x % 2 ≠ 0 := by
  let f := Rat.floor (x * tenPow k + 1 / 2)
  change (f ≠ (if (f : Rat) = x * tenPow k + 1 / 2 ∧ f % 2 ≠ 0
    then f - 1 else f)) ↔ tieAt k x = true ∧ f % 2 ≠ 0
  rw [tieAt_iff_floor_tie]
  change (f ≠ (if (f : Rat) = x * tenPow k + 1 / 2 ∧ f % 2 ≠ 0
    then f - 1 else f)) ↔
      ((f : Rat) = x * tenPow k + 1 / 2) ∧ f % 2 ≠ 0
  by_cases ht : (f : Rat) = x * tenPow k + 1 / 2
  · by_cases ho : f % 2 ≠ 0
    · simp [ht, ho]
      omega
    · simp [ht, ho]
  · simp [ht]

theorem rules_agree_off_tie (p : Printed) (x : Rat)
    (h : tieAt p.places x = false) :
    RoundsTo .tiesUp p x ↔ RoundsTo .halfEven p x := by
  have heq : Rounding.round .tiesUp p.places x =
      Rounding.round .halfEven p.places x := by
    by_cases hne : Rounding.round .tiesUp p.places x =
        Rounding.round .halfEven p.places x
    · exact hne
    · have ht := (rules_differ_iff p.places x).mp hne
      simp [h] at ht
  rw [roundsTo_iff_round .tiesUp p x, roundsTo_iff_round .halfEven p x, heq]

inductive Verdict where
  | holds | fails | undefined
  deriving Repr, DecidableEq

inductive Limit where
  | digits | evaluations | derivationSteps | witnessPoints | polyTerms
  deriving Repr, DecidableEq

inductive UnknownReason where
  | limit (l : Limit)
  | floatingPointNotModelled
  | derivationInconclusive
  | consistencyInconclusive
  | identityNotShown
  | unboundedStatement
  deriving Repr, DecidableEq

inductive Outcome where
  | decided (v : Verdict)
  | unknown (r : UnknownReason)
  deriving Repr, DecidableEq

/-- The fixed user-facing explanation of an operational unknown. -/
def UnknownReason.text (budget : Nat) : UnknownReason → String
  | .limit .digits => "unknown: an exact value would have more than 4,096 digits"
  | .limit .evaluations =>
      "unknown: the budget of " ++ toString budget ++ " evaluation steps ran out"
  | .limit .derivationSteps =>
      "unknown: the derivation search ran out of its 10,000 combination steps"
  | .limit .witnessPoints =>
      "unknown: the consistency search tried its 4,096 candidate points"
  | .limit .polyTerms => "unknown: a normal form would have more than 10,000 terms"
  | .floatingPointNotModelled => "unknown: floating-point computation not modelled"
  | .derivationInconclusive => "unknown: no certificate and no counterexample was found"
  | .consistencyInconclusive => "unknown: neither a witness nor an enclosure decides it"
  | .identityNotShown =>
      "unknown: the normal forms differ and no point where the sides differ was found"
  | .unboundedStatement => "stated, not decided: a quantifier has no bound"

end VE.Numbers
