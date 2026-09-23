import VE.Closure.PathRules

namespace VE.Closure
universe u

/-- A supplied invariant propagates along either kind of finite path. -/
theorem reachable_induction {α : Type u} {R : α → α → Prop} (k : Kind)
    (P : α → Prop) (x : α) (base : P x)
    (step : ∀ a b, P a → R a b → P b) :
    ∀ y, Reachable k R x y → P y := by
  have hp : ∀ a b, Path R a b → P a → P b := by
    intro a b h
    induction h with
    | edge h => exact fun ha => step _ _ ha h
    | cons h _ ih => exact fun ha => ih (step _ _ ha h)
  intro y h
  cases k with
  | plus => exact hp x y h base
  | star => rcases h with rfl | h; exact base; exact hp x y h base

/-- P has context s :: Γ; instantiation removes its one local binder. -/
def invariantAt (P : Formula) (t : Term) : Formula :=
  P.subst (fun i => match i with | 0 => t | i+1 => .var i)

def inductionStep (s : String) (e : Edge) (P : Formula) : Formula :=
  .all s (.all s (.implies
    (.and (P.subst (fun i => match i with | 0 => .var 1 | i+1 => .var (i+2)))
      (e.shift.shift.at (.var 1) (.var 0)))
    (P.subst (fun i => match i with | 0 => .var 0 | i+1 => .var (i+2)))))

theorem invariantAt_denote (S : Structure) (ρ : Valuation S) (P : Formula)
    (t : Term) (v : S.Carrier) (ht : t.denote S ρ = some v) :
    (invariantAt P t).denote S ρ ↔ P.denote S (v :: ρ) := by
  apply subst_denote
  intro i
  cases i with
  | zero => exact ht
  | succ i => rfl

theorem inductionStep_denote {E : Environment} {S : Structure} (hS : S.Admissible E)
    (ρ : Valuation S) (s : String) (e : Edge) (P : Formula) (he : e.Typed E s)
    (h : (inductionStep s e P).denote S ρ) :
    ∀ a b, P.denote S (a :: ρ) → e.denote S ρ a b → P.denote S (b :: ρ) := by
  intro a b ha hab
  obtain ⟨hda,hdb⟩ := edge_typed hS ρ e s he a b hab
  have hs := h a hda b hdb
  have hpa := subst_denote S (a :: ρ) (b :: a :: ρ)
    (fun i => match i with | 0 => .var 1 | i+1 => .var (i+2)) (by
    intro i; cases i <;> rfl) P
  have hpb := subst_denote S (b :: ρ) (b :: a :: ρ)
    (fun i => match i with | 0 => .var 0 | i+1 => .var (i+2)) (by
    intro i; cases i <;> rfl) P
  apply hpb.mp
  apply hs
  refine ⟨hpa.mpr ha, ?_⟩
  rw [edge_at_denote S (b :: a :: ρ) e.shift.shift (.var 1) (.var 0) a b
    rfl rfl (by
      intro q f hf
      have hq : q = s := by cases e <;> simp_all [Edge.shift, Edge.Typed]
      rw [hq]; exact ⟨hda,hdb⟩), edge_shift_denote, edge_shift_denote]
  exact hab

theorem closure_induction {E : Environment} {S : Structure} (hS : S.Admissible E)
    (ρ : Valuation S) (k : Kind) (s : String) (e : Edge) (P : Formula) (t r : Term)
    (he : e.Typed E s) (base : (invariantAt P t).denote S ρ)
    (step : (inductionStep s e P).denote S ρ)
    (path : (Formula.reach k e t r).denote S ρ) :
    (invariantAt P r).denote S ρ := by
  obtain ⟨x,y,hx,hy,hp⟩ := (reach_denote S ρ k e t r).mp path
  exact (invariantAt_denote S ρ P r y hy).mpr
    (reachable_induction k (fun v => P.denote S (v :: ρ)) x
      ((invariantAt_denote S ρ P t x hx).mp base)
      (inductionStep_denote hS ρ s e P he step) y hp)

end VE.Closure
