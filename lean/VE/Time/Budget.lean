import VE.Order.Consequence

/-! The W6 finite-evaluation budget (units-schema gate 4).

Python and Rust charge one unit per formula-node visit, never per term, and stop
with `ResourceLimit` (UNKNOWN) when a visit finds `MAX_EVALUATIONS = 1,000,000`
units already spent. Connectives short-circuit and a quantifier stops at the
first decisive entity. `evalB` is that evaluator: it returns the value and the
work spent, or `none` for UNKNOWN. When it returns a value, the value is the
reference evaluator's (`evalB_sound`), so the budget only ever turns an answer
into UNKNOWN, never into a different answer. -/
namespace VE.Time
open VE.Order

/-- Python/Rust `MAX_EVALUATIONS`. -/
def maxEvaluations : Nat := 1000000

/-- A quantifier loop: stop at the first entity whose value differs from
`universal`; with no such entity the value is `universal`. -/
def quantB {β : Type} (universal : Bool) (step : β → Nat → Option (Bool × Nat)) :
    List β → Nat → Option (Bool × Nat)
  | [], w => some (universal, w)
  | v :: vs, w => match step v w with
    | none => none
    | some (b, w') => if b = universal then quantB universal step vs w' else some (!universal, w')

/-- Charge one formula-node visit (Python `tick`): fail when `w ≥ limit`. -/
def charge (limit w : Nat) (k : Nat → Option (Bool × Nat)) : Option (Bool × Nat) :=
  if limit ≤ w then none else k (w + 1)

/-- The budgeted evaluator; `w` is the work already spent. -/
def evalB {α : Type} [DecidableEq α] (M : FiniteModel α) (limit : Nat) :
    List (Value α) → Formula → Nat → Option (Bool × Nat)
  | ρ, .not a, w => charge limit w fun w => (evalB M limit ρ a w).map fun r => (!r.1, r.2)
  | ρ, .and a b, w => charge limit w fun w => match evalB M limit ρ a w with
    | none => none
    | some (true, w) => evalB M limit ρ b w
    | some (false, w) => some (false, w)
  | ρ, .or a b, w => charge limit w fun w => match evalB M limit ρ a w with
    | none => none
    | some (true, w) => some (true, w)
    | some (false, w) => evalB M limit ρ b w
  | ρ, .implies a b, w => charge limit w fun w => match evalB M limit ρ a w with
    | none => none
    | some (true, w) => evalB M limit ρ b w
    | some (false, w) => some (true, w)
  | ρ, .all s a, w => charge limit w fun w =>
    quantB true (fun v => evalB M limit (.inl v :: ρ) a) (M.domains s) w
  | ρ, .ex s a, w => charge limit w fun w =>
    quantB false (fun v => evalB M limit (.inl v :: ρ) a) (M.domains s) w
  | ρ, f, w => charge limit w fun w => some (f.eval M ρ, w)

theorem quantB_sound {β : Type} (universal : Bool) (step : β → Nat → Option (Bool × Nat))
    (g : β → Bool) : ∀ (l : List β),
    (∀ v ∈ l, ∀ w r, step v w = some r → r.1 = g v) →
    ∀ w r, quantB universal step l w = some r →
      r.1 = (if universal then l.all g else l.any g)
  | [], _, w, r, h => by
    simp only [quantB, Option.some.injEq] at h
    subst h; cases universal <;> rfl
  | v :: vs, hs, w, r, h => by
    simp only [quantB] at h
    split at h
    · cases h
    · rename_i b w' hstep
      have hb : b = g v := hs v (List.mem_cons_self ..) w (b, w') hstep
      split at h
      · rename_i hu
        have := quantB_sound universal step g vs
          (fun x hx => hs x (List.mem_cons_of_mem _ hx)) w' r h
        rw [this]
        subst hb
        cases universal <;> simp [List.all_cons, List.any_cons, hu]
      · rename_i hu
        simp only [Option.some.injEq] at h
        subst h
        subst hb
        cases universal <;> cases hg : g v <;> simp_all

theorem charge_some {limit w : Nat} {k : Nat → Option (Bool × Nat)} {r : Bool × Nat}
    (h : charge limit w k = some r) : k (w + 1) = some r := by
  unfold charge at h
  split at h
  · cases h
  · exact h

/-- **Budget soundness.** A budgeted value is the reference evaluator's value. -/
theorem evalB_sound {α : Type} [DecidableEq α] (M : FiniteModel α) (limit : Nat) :
    ∀ (f : Formula) (ρ : List (Value α)) (w : Nat) (r : Bool × Nat),
      evalB M limit ρ f w = some r → r.1 = f.eval M ρ := by
  intro f
  induction f with
  | top | bottom | unary | binary | eq | lt | le =>
    intro ρ w r h
    have h := charge_some h
    simp only [Option.some.injEq] at h
    subst h; rfl
  | not a ih =>
    intro ρ w r h
    have h := charge_some h
    cases ha : evalB M limit ρ a (w + 1) with
    | none => rw [ha] at h; cases h
    | some x =>
      rw [ha] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [Formula.eval, ih ρ _ x ha]
  | and a b ia ib =>
    intro ρ w r h
    have h := charge_some h
    simp only at h
    split at h
    · cases h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Formula.eval, ← this, Bool.true_and]
      exact ib ρ _ _ h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [Formula.eval, ← this]
  | or a b ia ib =>
    intro ρ w r h
    have h := charge_some h
    simp only at h
    split at h
    · cases h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [Formula.eval, ← this]
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Formula.eval, ← this, Bool.false_or]
      exact ib ρ _ _ h
  | implies a b ia ib =>
    intro ρ w r h
    have h := charge_some h
    simp only at h
    split at h
    · cases h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Formula.eval, ← this, Bool.not_true, Bool.false_or]
      exact ib ρ _ _ h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [Formula.eval, ← this]
  | all s a ih =>
    intro ρ w r h
    have h := charge_some h
    have := quantB_sound true _ (fun v => a.eval M (.inl v :: ρ)) (M.domains s)
      (fun v _ w r hv => ih _ w r hv) _ r h
    simpa [Formula.eval] using this
  | ex s a ih =>
    intro ρ w r h
    have h := charge_some h
    have := quantB_sound false _ (fun v => a.eval M (.inl v :: ρ)) (M.domains s)
      (fun v _ w r hv => ih _ w r hv) _ r h
    simpa [Formula.eval] using this

/-- The countermodel check under one shared budget, premises first in order,
stopping at the first false premise (Python `_check_countermodel_values`,
Rust `order_case`). `none` is UNKNOWN. -/
def refutesB {α : Type} [DecidableEq α] (M : FiniteModel α) (limit : Nat) :
    List Formula → Formula → Nat → Option Bool
  | [], c, w => (evalB M limit [] c w).map (fun r => !r.1)
  | p :: ps, c, w => match evalB M limit [] p w with
    | none => none
    | some (false, _) => some false
    | some (true, w) => refutesB M limit ps c w

/-- A budgeted countermodel verdict is the reference verdict. -/
theorem refutesB_sound {α : Type} [DecidableEq α] (M : FiniteModel α) (limit : Nat) :
    ∀ (ps : List Formula) (c : Formula) (w : Nat) (b : Bool),
      refutesB M limit ps c w = some b → b = countermodelCheck M ps c
  | [], c, w, b, h => by
    simp only [refutesB] at h
    cases hc : evalB M limit [] c w with
    | none => rw [hc] at h; cases h
    | some x =>
      rw [hc] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [countermodelCheck, evalB_sound M limit c [] w x hc]
  | p :: ps, c, w, b, h => by
    simp only [refutesB] at h
    split at h
    · cases h
    · rename_i w' hp
      have := evalB_sound M limit p [] w _ hp
      simp only [Option.some.injEq] at h
      subst h
      simp [countermodelCheck, ← this]
    · rename_i w' hp
      have := evalB_sound M limit p [] w _ hp
      rw [refutesB_sound M limit ps c w' b h]
      simp [countermodelCheck, ← this]

end VE.Time
