import VE.Core.Consequence

namespace VE.Core
universe u

def liftTerm : Term → Term
  | .var i => .var (i+1)
  | .const c => .const c

def liftSub (σ : Nat → Term) : Nat → Term
  | 0 => .var 0
  | i+1 => liftTerm (σ i)

def substTerm (σ : Nat → Term) : Term → Term
  | .var i => σ i
  | .const c => .const c

def Formula.subst (σ : Nat → Term) : Formula → Formula
  | .top => .top
  | .bottom => .bottom
  | .unary p t => .unary p (substTerm σ t)
  | .binary p t r => .binary p (substTerm σ t) (substTerm σ r)
  | .atom p ts => .atom p (ts.map (substTerm σ))
  | .eq t r => .eq (substTerm σ t) (substTerm σ r)
  | .not a => .not (a.subst σ)
  | .and a b => .and (a.subst σ) (b.subst σ)
  | .or a b => .or (a.subst σ) (b.subst σ)
  | .implies a b => .implies (a.subst σ) (b.subst σ)
  | .all s a => .all s (a.subst (liftSub σ))
  | .ex s a => .ex s (a.subst (liftSub σ))
  | .reachNamed k p t r => .reachNamed k p (substTerm σ t) (substTerm σ r)
  | .reachBody k s a t r => .reachBody k s (a.subst (liftSub (liftSub σ)))
      (substTerm σ t) (substTerm σ r)

theorem substTerm_denote (S : Structure) (ρ τ : Valuation S) (σ : Nat → Term)
    (h : ∀ i, (σ i).denote S τ = ρ[i]?) (t : Term) :
    (substTerm σ t).denote S τ = t.denote S ρ := by
  cases t with
  | var i => exact h i
  | const c => rfl

theorem liftSub_denote (S : Structure) (ρ τ : Valuation S) (σ : Nat → Term)
    (h : ∀ i, (σ i).denote S τ = ρ[i]?) (v : S.Carrier) :
    ∀ i, (liftSub σ i).denote S (v :: τ) = (v :: ρ)[i]? := by
  intro i
  cases i with
  | zero => rfl
  | succ i => cases he : σ i <;> simpa [liftSub, he, liftTerm, Term.denote] using h i

theorem subst_denote (S : Structure) (ρ τ : Valuation S) (σ : Nat → Term)
    (h : ∀ i, (σ i).denote S τ = ρ[i]?) (a : Formula) :
    (a.subst σ).denote S τ ↔ a.denote S ρ := by
  induction a generalizing ρ τ σ with
  | all s a ih =>
    change (∀ v, S.domain s v → (a.subst (liftSub σ)).denote S (v :: τ)) ↔ _
    apply forall_congr'; intro v
    exact imp_congr Iff.rfl (ih _ _ _ (liftSub_denote S ρ τ σ h v))
  | ex s a ih =>
    change (∃ v, S.domain s v ∧ (a.subst (liftSub σ)).denote S (v :: τ)) ↔ _
    apply exists_congr; intro v
    exact and_congr Iff.rfl (ih _ _ _ (liftSub_denote S ρ τ σ h v))
  | reachBody k s a t r ih =>
    simp only [Formula.subst, Formula.denote, substTerm_denote S ρ τ σ h]
    have he : (fun x y => S.domain s x ∧ S.domain s y ∧
        (a.subst (liftSub (liftSub σ))).denote S (y :: x :: τ)) =
        (fun x y => S.domain s x ∧ S.domain s y ∧ a.denote S (y :: x :: ρ)) := by
      funext x y
      apply propext
      simp only [ih _ _ _ (liftSub_denote S _ _ _ (liftSub_denote S ρ τ σ h x) y)]
    rw [he]
  | not a ih => exact not_congr (ih ρ τ σ h)
  | and a b ia ib => exact and_congr (ia ρ τ σ h) (ib ρ τ σ h)
  | or a b ia ib => exact or_congr (ia ρ τ σ h) (ib ρ τ σ h)
  | implies a b ia ib => exact imp_congr (ia ρ τ σ h) (ib ρ τ σ h)
  | atom p ts =>
    have hts : (ts.map (substTerm σ)).mapM (·.denote S τ) =
        ts.mapM (·.denote S ρ) := by
      induction ts with
      | nil => rfl
      | cons t ts ih => simp [List.mapM_cons, substTerm_denote S ρ τ σ h, ih]
    simp [Formula.subst, Formula.denote, hts]
  | _ => simp only [Formula.subst, Formula.denote, substTerm_denote S ρ τ σ h]

def Edge.denote (S : Structure) (ρ : Valuation S) : Edge → S.Carrier → S.Carrier → Prop
  | .named p => fun x y => S.relation p [x,y]
  | .body s a => fun x y => S.domain s x ∧ S.domain s y ∧ a.denote S (y :: x :: ρ)

def Edge.shift : Edge → Edge
  | .named p => .named p
  | .body s a => .body s (a.subst (liftSub (liftSub (fun i => .var (i+1)))))

def Edge.at : Edge → Term → Term → Formula
  | .named p, t, r => .binary p t r
  | .body _ a, t, r => a.subst (fun i => match i with
      | 0 => r | 1 => t | i+2 => .var i)

def Edge.Typed (E : Environment) (s : String) : Edge → Prop
  | .named p => E.predicates p = some [s,s]
  | .body r _ => r = s

theorem edge_typed {E : Environment} {S : Structure} (hS : S.Admissible E)
    (ρ : Valuation S) (e : Edge) (s : String) (he : e.Typed E s)
    (x y : S.Carrier) (h : e.denote S ρ x y) : S.domain s x ∧ S.domain s y := by
  cases e with
  | named p =>
    obtain ⟨ss, hp, ht⟩ := hS.2 p [x,y] h
    have he : E.predicates p = some [s,s] := he
    rw [he] at hp
    cases hp
    exact ⟨ht.1, ht.2.1⟩
  | body r a => cases he; exact ⟨h.1, h.2.1⟩

theorem edge_at_denote (S : Structure) (ρ : Valuation S) (e : Edge) (t r : Term)
    (x y : S.Carrier) (ht : t.denote S ρ = some x) (hr : r.denote S ρ = some y)
    (hd : ∀ s a, e = .body s a → S.domain s x ∧ S.domain s y) :
    (e.at t r).denote S ρ ↔ e.denote S ρ x y := by
  cases e with
  | named p => simp [Edge.at, Formula.denote, ht, hr, Edge.denote]
  | body s a =>
    have hs := hd s a rfl
    rw [Edge.at, subst_denote S (y :: x :: ρ) ρ _ (by
      intro i; cases i with
      | zero => exact hr
      | succ i => cases i with
        | zero => exact ht
        | succ i => rfl)]
    simp [Edge.denote, hs]

theorem edge_shift_denote (S : Structure) (ρ : Valuation S) (e : Edge) (v : S.Carrier) :
    e.shift.denote S (v :: ρ) = e.denote S ρ := by
  cases e with
  | named p => rfl
  | body s a =>
    funext x y
    apply propext
    simp only [Edge.shift, Edge.denote]
    rw [subst_denote S (y :: x :: ρ) (y :: x :: v :: ρ) _
      (liftSub_denote S _ _ _ (liftSub_denote S _ _ _ (fun _ => rfl) x) y)]

theorem reach_denote (S : Structure) (ρ : Valuation S) (k : Kind) (e : Edge) (t r : Term) :
    (Formula.reach k e t r).denote S ρ ↔ ∃ x y, t.denote S ρ = some x ∧
      r.denote S ρ = some y ∧ Reachable k (e.denote S ρ) x y := by
  cases e <;> rfl

def unfold (k : Kind) (e : Edge) (s : String) (t r : Term) : Formula :=
  match k with
  | .star => .or (.eq t r) (.reach .plus e t r)
  | .plus => .or (e.at t r) (.ex s (.and
      (e.shift.at (liftTerm t) (.var 0)) (.reach .plus e.shift (.var 0) (liftTerm r))))

theorem liftTerm_denote (S : Structure) (ρ : Valuation S) (v : S.Carrier) (t : Term) :
    (liftTerm t).denote S (v :: ρ) = t.denote S ρ := by
  cases t <;> rfl

theorem pair_values {α : Type u} (P : α → α → Prop) (x y : α) :
    (∃ a b, x = a ∧ y = b ∧ P a b) ↔ P x y := by
  constructor
  · rintro ⟨a,b,rfl,rfl,h⟩; exact h
  · intro h; exact ⟨x,y,rfl,rfl,h⟩

theorem unfold_denote {E : Environment} {S : Structure} (hS : S.Admissible E)
    (ρ : Valuation S) (k : Kind) (e : Edge) (s : String) (t r : Term)
    (he : e.Typed E s) (x y : S.Carrier)
    (ht : t.denote S ρ = some x) (hr : r.denote S ρ = some y)
    (hx : S.domain s x) (hy : S.domain s y) :
    (unfold k e s t r).denote S ρ ↔ (Formula.reach k e t r).denote S ρ := by
  have hb : ∀ q a, e = .body q a → q = s := by
    intro q a h; subst e; exact he
  have hat := edge_at_denote S ρ e t r x y ht hr (by
    intro q a h; rw [hb q a h]; exact ⟨hx,hy⟩)
  cases k with
  | star => simp [unfold, Formula.denote, reach_denote, ht, hr, Reachable, eq_comm]
  | plus =>
    change ((e.at t r).denote S ρ ∨ ∃ v, S.domain s v ∧
      (e.shift.at (liftTerm t) (.var 0)).denote S (v :: ρ) ∧
      (Formula.reach .plus e.shift (.var 0) (liftTerm r)).denote S (v :: ρ)) ↔ _
    simp only [reach_denote, liftTerm_denote, ht, hr, Reachable, edge_shift_denote,
      show ∀ v : S.Carrier, (Term.var 0).denote S (v :: ρ) = some v from fun _ => rfl,
      Option.some.injEq]
    simp only [pair_values]
    rw [hat, Path.unfold]
    have hh (v : S.Carrier) (hv : S.domain s v) :
        (e.shift.at (liftTerm t) (.var 0)).denote S (v :: ρ) ↔ e.denote S ρ x v := by
      rw [edge_at_denote S (v :: ρ) e.shift (liftTerm t) (.var 0) x v
        (by rw [liftTerm_denote]; exact ht) rfl (by
          intro q a h
          have hq : q = s := by cases e <;> simp_all [Edge.shift, Edge.Typed]
          rw [hq]; exact ⟨hx,hv⟩), edge_shift_denote]
    constructor
    · rintro (h | ⟨v,hv,ha,hp⟩)
      · exact .inl h
      · exact .inr ⟨v,(hh v hv).mp ha,hp⟩
    · rintro (h | ⟨v,ha,hp⟩)
      · exact .inl h
      · have hv := (edge_typed hS ρ e s he x v ha).2
        exact .inr ⟨v,hv,(hh v hv).mpr ha,hp⟩

end VE.Core
