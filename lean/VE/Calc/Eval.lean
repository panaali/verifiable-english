import VE.Calc.Syntax

namespace VE.Calc
open VE.Numbers

def Expr.eval (σ : Values) : Expr → Option Rat
  | .lit q => some q
  | .val n => σ n
  | .add a b => do let x ← a.eval σ; let y ← b.eval σ; pure (x + y)
  | .sub a b => do let x ← a.eval σ; let y ← b.eval σ; pure (x - y)
  | .mul a b => do let x ← a.eval σ; let y ← b.eval σ; pure (x * y)
  | .div a b => do
      let x ← a.eval σ
      let y ← b.eval σ
      if y = 0 then none else pure (x / y)
  | .pow a k => (a.eval σ).map (· ^ k)

theorem Expr.eval_sound (σ : Values) (e : Expr) (q : Rat)
    (h : e.eval σ = some q) : Denotes σ e q := by
  induction e generalizing q with
  | lit v =>
      simp [Expr.eval] at h
      cases h
      exact .lit
  | val n => exact .val h
  | add a b iha ihb =>
      cases ha : a.eval σ with
      | none => simp [Expr.eval, ha] at h
      | some x =>
        cases hb : b.eval σ with
        | none => simp [Expr.eval, ha, hb] at h
        | some y =>
          simp [Expr.eval, ha, hb] at h
          cases h
          exact .add (iha _ ha) (ihb _ hb)
  | sub a b iha ihb =>
      cases ha : a.eval σ with
      | none => simp [Expr.eval, ha] at h
      | some x =>
        cases hb : b.eval σ with
        | none => simp [Expr.eval, ha, hb] at h
        | some y =>
          simp [Expr.eval, ha, hb] at h
          cases h
          exact .sub (iha _ ha) (ihb _ hb)
  | mul a b iha ihb =>
      cases ha : a.eval σ with
      | none => simp [Expr.eval, ha] at h
      | some x =>
        cases hb : b.eval σ with
        | none => simp [Expr.eval, ha, hb] at h
        | some y =>
          simp [Expr.eval, ha, hb] at h
          cases h
          exact .mul (iha _ ha) (ihb _ hb)
  | div a b iha ihb =>
      cases ha : a.eval σ with
      | none => simp [Expr.eval, ha] at h
      | some x =>
        cases hb : b.eval σ with
        | none => simp [Expr.eval, ha, hb] at h
        | some y =>
          by_cases hy : y = 0
          · simp [Expr.eval, ha, hb, hy] at h
          · simp [Expr.eval, ha, hb, hy] at h
            cases h
            exact .div (iha _ ha) (ihb _ hb) hy
  | pow a k iha =>
      simp only [Expr.eval, Option.map_eq_some_iff] at h
      obtain ⟨x, ha, hq⟩ := h
      cases hq
      exact .pow (iha _ ha)

theorem Denotes.eval_complete {σ : Values} {e : Expr} {q : Rat}
    (h : Denotes σ e q) : e.eval σ = some q := by
  induction h with
  | lit => rfl
  | val hv => exact hv
  | add ha hb iha ihb => simp [Expr.eval, iha, ihb]
  | sub ha hb iha ihb => simp [Expr.eval, iha, ihb]
  | mul ha hb iha ihb => simp [Expr.eval, iha, ihb]
  | div ha hb hne iha ihb => simp [Expr.eval, iha, ihb, hne]
  | pow ha iha => simp [Expr.eval, iha]

theorem Expr.eval_iff (σ : Values) (e : Expr) (q : Rat) :
    e.eval σ = some q ↔ Denotes σ e q :=
  ⟨e.eval_sound σ q, Denotes.eval_complete⟩

theorem Denotes.unique {σ : Values} {e : Expr} {x y : Rat}
    (hx : Denotes σ e x) (hy : Denotes σ e y) : x = y := by
  have h1 := (Expr.eval_iff σ e x).mpr hx
  have h2 := (Expr.eval_iff σ e y).mpr hy
  exact Option.some.inj (h1.symm.trans h2)

def Claim.decide (σ : Values) : Claim → Verdict
  | .compare c a b => match a.eval σ, b.eval σ with
    | some x, some y => if c.Holds x y then .holds else .fails
    | _, _ => .undefined
  | .within e lo hi => match e.eval σ, lo.eval σ, hi.eval σ with
    | some x, some l, some h => if l ≤ x ∧ x ≤ h then .holds else .fails
    | _, _, _ => .undefined
  | .rounds r e p => match e.eval σ with
    | some x => if RoundsTo r p x then .holds else .fails
    | none => .undefined

def Claim.tieSensitive (σ : Values) : Claim → Bool
  | .rounds .tiesUp e p | .rounds .halfEven e p => match e.eval σ with
    | some x => tieAt p.places x
    | none => false
  | _ => false

theorem Claim.decide_holds (σ : Values) (c : Claim) :
    c.decide σ = .holds ↔ c.Holds σ := by
  cases c with
  | compare r a b =>
      cases ha : a.eval σ <;> cases hb : b.eval σ <;>
        simp [Claim.decide, Claim.Holds, ha, hb, ← Expr.eval_iff]
  | within e lo hi =>
      cases he : e.eval σ <;> cases hl : lo.eval σ <;> cases hh : hi.eval σ <;>
        simp [Claim.decide, Claim.Holds, he, hl, hh, ← Expr.eval_iff]
  | rounds r e p =>
      cases he : e.eval σ <;>
        simp [Claim.decide, Claim.Holds, he, ← Expr.eval_iff]

theorem Claim.decide_undefined (σ : Values) (c : Claim) :
    c.decide σ = .undefined ↔ ¬ c.Defined σ := by
  cases c with
  | compare r a b =>
      cases ha : a.eval σ <;> cases hb : b.eval σ <;>
        simp [Claim.decide, Claim.Defined, Claim.exprs, ha, hb, ← Expr.eval_iff] <;>
        split <;> simp_all
  | within e lo hi =>
      cases he : e.eval σ <;> cases hl : lo.eval σ <;> cases hh : hi.eval σ <;>
        simp [Claim.decide, Claim.Defined, Claim.exprs, he, hl, hh, ← Expr.eval_iff] <;>
        split <;> simp_all
  | rounds r e p =>
      cases he : e.eval σ <;>
        simp [Claim.decide, Claim.Defined, Claim.exprs, he, ← Expr.eval_iff] <;>
        split <;> simp_all

theorem Claim.decide_fails (σ : Values) (c : Claim) :
    c.decide σ = .fails ↔ c.Defined σ ∧ ¬ c.Holds σ := by
  have hh := Claim.decide_holds σ c
  have hu := Claim.decide_undefined σ c
  cases h : c.decide σ <;> simp_all

end VE.Calc
