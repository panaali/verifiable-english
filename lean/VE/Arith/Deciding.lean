import VE.Arith.Bounded

/-! The deciding value (spec 12.5, me-12ac): the first value at which a statement's outermost bounded quantifier
stops, in the evaluator's order (12.2). `decidingLoop` is `quantLoop` returning the value where it stops early instead
of the answer, so it stops exactly when that loop does (`decidingLoop_iff`), and the value it returns is the first
counterexample of a failed "for every" or the first witness of a true "there is" (`decidingValue_all`,
`decidingValue_ex`). -/

namespace VE.Arith

/-- `quantLoop`'s loop, returning the value where a step decides the quantifier and the units spent there; none when
every step agrees with `universal` or the budget runs out. -/
def decidingLoop (universal : Bool) (step : Int → Nat → Option (Bool × Nat)) :
    Nat → Int → Nat → Option (Int × Nat)
  | 0, _, _ => none
  | n + 1, i, w => match step i w with
    | none => none
    | some (b, w') => if b = universal then decidingLoop universal step n (i + 1) w' else some (i, w')

/-- The evaluator's visit of a bounded quantifier node at the top of a statement (`Formula.evalB` on `allFromTo` or
`exFromTo`), with `decidingLoop` in place of `quantLoop`. -/
def decidingAt (E : OpEnv) (limit : Nat) (universal : Bool) (lo hi : Term) (ψ : Formula) : Option (Int × Nat) :=
  charge limit 0 fun w => match Term.evalB E limit [] lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit [] hi w with
      | none => none
      | some (h, w) => decidingLoop universal (stepB limit fun i w => Formula.evalB E limit [i] ψ w) (h - l + 1).toNat l w

/-- The first decisive value of a statement's outermost bounded quantifier, in 12.2's evaluation order: for
`allFromTo`, the first value where its body fails; for `exFromTo`, the first where it holds; none otherwise. -/
def decidingValue (D : Defs) (limit : Nat) (φ : Formula) : Option Int :=
  match φ with
  | .allFromTo lo hi ψ => (decidingAt (D.opEnv limit) limit true lo hi ψ).map (·.1)
  | .exFromTo lo hi ψ => (decidingAt (D.opEnv limit) limit false lo hi ψ).map (·.1)
  | _ => none

/-- The loop stops at a value of its range where the step disagrees with `universal`, and every earlier step agrees. -/
theorem decidingLoop_sound (Q : Int → Prop) (step : Int → Nat → Option (Bool × Nat)) (u : Bool)
    (hs : ∀ i w b w', step i w = some (b, w') → (Q i ↔ b = true)) :
    ∀ n i w j w', decidingLoop u step n i w = some (j, w') →
      i ≤ j ∧ j < i + n ∧ (Q j ↔ u = false) ∧ ∀ m, i ≤ m → m < j → (Q m ↔ u = true)
  | 0, _, _, _, _, h => by simp [decidingLoop] at h
  | n + 1, i, w, j, w', h => by
    simp only [decidingLoop] at h
    cases hst : step i w with
    | none => simp [hst] at h
    | some r =>
      obtain ⟨b, w0⟩ := r
      have hq := hs i w b w0 hst
      simp only [hst] at h
      by_cases hb : b = u
      · simp only [hb, ite_true] at h
        have ⟨h1, h2, h3, h4⟩ := decidingLoop_sound Q step u hs n (i + 1) w0 j w' h
        refine ⟨by omega, by omega, h3, fun m hm1 hm2 => ?_⟩
        by_cases hm : m = i
        · subst hm hb; exact hq
        · exact h4 m (by omega) hm2
      · simp only [hb, ite_false, Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        refine ⟨Int.le_refl _, by omega, ?_, fun m hm1 hm2 => absurd hm2 (by omega)⟩
        cases b <;> cases u <;> simp_all

/-- The loop stops exactly when `quantLoop` stops early, after the same units: `quantLoop` then answers `!universal`. -/
theorem decidingLoop_iff (u : Bool) (step : Int → Nat → Option (Bool × Nat)) :
    ∀ n i w w', (∃ j, decidingLoop u step n i w = some (j, w')) ↔ quantLoop u step n i w = some (!u, w')
  | 0, _, _, _ => by cases u <;> simp [decidingLoop, quantLoop]
  | n + 1, i, w, w' => by
    simp only [decidingLoop, quantLoop]
    cases step i w with
    | none => simp
    | some r =>
      obtain ⟨b, w0⟩ := r
      by_cases hb : b = u
      · simp only [hb, ite_true]; exact decidingLoop_iff u step n (i + 1) w0 w'
      · have : b = !u := by cases b <;> cases u <;> simp_all
        simp [this]

/-- A deciding value at the top of a statement: the range's ends have values in the meaning, the value lies between
them, and the loop's description holds of the body's meaning. -/
theorem decidingAt_sound (D : Defs) (limit : Nat) (u : Bool) (lo hi : Term) (ψ : Formula) (i : Int)
    (h : (decidingAt (D.opEnv limit) limit u lo hi ψ).map (·.1) = some i) :
    ∃ l v, Term.value D.env [] lo = some l ∧ Term.value D.env [] hi = some v ∧ l ≤ i ∧ i ≤ v ∧
      (Holds D.env [i] ψ ↔ u = false) ∧ ∀ m, l ≤ m → m < i → (Holds D.env [m] ψ ↔ u = true) := by
  have hA := agrees_env D limit
  simp only [Option.map_eq_some_iff] at h
  obtain ⟨⟨j, w'⟩, h, rfl⟩ := h
  have ⟨_, h⟩ := charge_some h
  cases hl : Term.evalB (D.opEnv limit) limit [] lo (0 + 1) with
  | none => simp [hl] at h
  | some rl =>
    obtain ⟨l, w1⟩ := rl
    cases hh : Term.evalB (D.opEnv limit) limit [] hi w1 with
    | none => simp [hl, hh] at h
    | some rh =>
      obtain ⟨v, w2⟩ := rh
      simp only [hl, hh] at h
      have ⟨h1, h2, h3, h4⟩ := decidingLoop_sound (fun m => Holds D.env [m] ψ) _ u
        (fun m w b w' hs => ((stepB_sound fun m w b w' hc => Formula.evalB_sound hA ψ [m] w b w' hc) m w b w' hs).1)
        _ _ _ _ _ h
      exact ⟨l, v, (Term.evalB_sound hA lo [] _ l w1 hl).1, (Term.evalB_sound hA hi [] _ v w2 hh).1, h1,
        by omega, h3, h4⟩

set_option linter.unusedVariables false in
/-- The deciding value of a failed universal is its first counterexample… -/
theorem decidingValue_all (D : Defs) (hD : D.WellFormed = true) (lo hi : Term) (ψ : Formula)
    (hφ : (Formula.allFromTo lo hi ψ).Scoped D 0 = true) (limit : Nat) (i : Int)
    (h : decidingValue D limit (.allFromTo lo hi ψ) = some i) :
    ∃ l u, Term.value D.env [] lo = some l ∧ Term.value D.env [] hi = some u ∧ l ≤ i ∧ i ≤ u ∧
      ¬ Holds D.env [i] ψ ∧ ∀ m, l ≤ m → m < i → Holds D.env [m] ψ := by
  have ⟨l, u, hl, hu, h1, h2, h3, h4⟩ := decidingAt_sound D limit true lo hi ψ i h
  exact ⟨l, u, hl, hu, h1, h2, by simpa using h3, fun m hm1 hm2 => by simpa using h4 m hm1 hm2⟩

set_option linter.unusedVariables false in
/-- … and of a true existential its first witness. -/
theorem decidingValue_ex (D : Defs) (hD : D.WellFormed = true) (lo hi : Term) (ψ : Formula)
    (hφ : (Formula.exFromTo lo hi ψ).Scoped D 0 = true) (limit : Nat) (i : Int)
    (h : decidingValue D limit (.exFromTo lo hi ψ) = some i) :
    ∃ l u, Term.value D.env [] lo = some l ∧ Term.value D.env [] hi = some u ∧ l ≤ i ∧ i ≤ u ∧
      Holds D.env [i] ψ ∧ ∀ m, l ≤ m → m < i → ¬ Holds D.env [m] ψ := by
  have ⟨l, u, hl, hu, h1, h2, h3, h4⟩ := decidingAt_sound D limit false lo hi ψ i h
  exact ⟨l, u, hl, hu, h1, h2, by simpa using h3, fun m hm1 hm2 => by simpa using h4 m hm1 hm2⟩

/-- A failed universal always reports its deciding value. -/
theorem decidingValue_of_fails (D : Defs) (limit : Nat) (lo hi : Term) (ψ : Formula)
    (h : arithOutcome D limit (.allFromTo lo hi ψ) = .decided .fails) :
    (decidingValue D limit (.allFromTo lo hi ψ)).isSome = true := by
  unfold arithOutcome at h
  split at h
  · split at h <;> simp at h
    next w hb =>
      simp only [decidingValue, decidingAt, Option.isSome_map]
      simp only [decideBounded, Formula.evalB, charge] at hb ⊢
      split at hb
      · simp at hb
      · next hlim =>
        simp only [hlim, ite_false]
        split at hb
        · simp at hb
        · next l w1 hl =>
          simp only [hl]
          split at hb
          · simp at hb
          · next v w2 hh =>
            obtain ⟨j, hj⟩ := (decidingLoop_iff true _ _ _ _ _).mpr hb
            simp [hh, hj]
  · simp at h

end VE.Arith
