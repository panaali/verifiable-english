import VE.Closure.Substitution

namespace VE.Closure

def unlift : Term → Option Term
  | .var 0 => none
  | .var (i+1) => some (.var i)
  | .const c => some (.const c)

def liftMatch (cmp : Term → Term → Bool) (t r : Term) : Bool :=
  match unlift t, unlift r with
  | none, none => true
  | some a, some b => cmp a b
  | _, _ => false

theorem unlift_denote (S : Structure) (ρ : Valuation S) (v : S.Carrier) (t : Term) :
    t.denote S (v :: ρ) = match unlift t with
      | none => some v
      | some a => a.denote S ρ := by
  cases t with
  | const c => rfl
  | var i => cases i <;> rfl

theorem liftMatch_sound (S : Structure) (ρ τ : Valuation S) (cmp : Term → Term → Bool)
    (h : ∀ t r, cmp t r = true → t.denote S ρ = r.denote S τ) (v : S.Carrier)
    (t r : Term) (hm : liftMatch cmp t r = true) :
    t.denote S (v :: ρ) = r.denote S (v :: τ) := by
  rw [unlift_denote, unlift_denote]
  cases ht : unlift t <;> cases hr : unlift r <;> simp_all [liftMatch]
  exact h _ _ hm

def Formula.matches (cmp : Term → Term → Bool) : Formula → Formula → Bool
  | .top, .top | .bottom, .bottom => true
  | .unary p t, .unary q r => decide (p = q) && cmp t r
  | .binary p t u, .binary q r v => decide (p = q) && cmp t r && cmp u v
  | .eq t u, .eq r v => cmp t r && cmp u v
  | .not a, .not b => a.matches cmp b
  | .and a b, .and c d | .or a b, .or c d | .implies a b, .implies c d =>
      a.matches cmp c && b.matches cmp d
  | .all s a, .all r b | .ex s a, .ex r b =>
      decide (s = r) && a.matches (liftMatch cmp) b
  | .reachNamed k p t u, .reachNamed l q r v =>
      decide (k = l ∧ p = q) && cmp t r && cmp u v
  | .reachBody k s a t u, .reachBody l r b v w =>
      decide (k = l ∧ s = r) && a.matches (liftMatch (liftMatch cmp)) b && cmp t v && cmp u w
  | _, _ => false

theorem formula_matches_sound (S : Structure) (a b : Formula) (ρ τ : Valuation S)
    (cmp : Term → Term → Bool)
    (h : ∀ t r, cmp t r = true → t.denote S ρ = r.denote S τ)
    (hm : a.matches cmp b = true) : a.denote S ρ ↔ b.denote S τ := by
  induction a generalizing b ρ τ cmp with
  | top | bottom => cases b <;> simp_all [Formula.matches, Formula.denote]
  | unary p t =>
    cases b <;> simp only [Formula.matches, Bool.and_eq_true, decide_eq_true_eq] at hm
    all_goals try contradiction
    obtain ⟨rfl,ht⟩ := hm
    simp only [Formula.denote, h _ _ ht]
  | binary p t u =>
    cases b <;> simp only [Formula.matches, Bool.and_eq_true, decide_eq_true_eq] at hm
    all_goals try contradiction
    obtain ⟨⟨rfl,ht⟩,hu⟩ := hm
    simp only [Formula.denote, h _ _ ht, h _ _ hu]
  | eq t u =>
    cases b <;> simp only [Formula.matches, Bool.and_eq_true] at hm
    all_goals try contradiction
    simp only [Formula.denote, h _ _ hm.1, h _ _ hm.2]
  | not a ih =>
    cases b <;> simp only [Formula.matches] at hm
    all_goals try contradiction
    exact not_congr (ih _ _ _ _ h hm)
  | and a c ia ib | or a c ia ib | implies a c ia ib =>
    cases b <;> simp only [Formula.matches, Bool.and_eq_true] at hm
    all_goals try contradiction
    first
    | exact and_congr (ia _ _ _ _ h hm.1) (ib _ _ _ _ h hm.2)
    | exact or_congr (ia _ _ _ _ h hm.1) (ib _ _ _ _ h hm.2)
    | exact imp_congr (ia _ _ _ _ h hm.1) (ib _ _ _ _ h hm.2)
  | all s a ih | ex s a ih =>
    cases b <;> simp only [Formula.matches, Bool.and_eq_true, decide_eq_true_eq] at hm
    all_goals try contradiction
    obtain ⟨rfl,hm⟩ := hm
    first
    | apply forall_congr'; intro v
      exact imp_congr Iff.rfl (ih _ _ _ _ (liftMatch_sound S ρ τ cmp h v) hm)
    | apply exists_congr; intro v
      exact and_congr Iff.rfl (ih _ _ _ _ (liftMatch_sound S ρ τ cmp h v) hm)
  | reachNamed k p t u =>
    cases b <;> simp only [Formula.matches, Bool.and_eq_true, decide_eq_true_eq] at hm
    all_goals try contradiction
    obtain ⟨⟨⟨rfl,rfl⟩,ht⟩,hu⟩ := hm
    simp only [Formula.denote, h _ _ ht, h _ _ hu]
  | reachBody k s a t u ih =>
    cases b <;> simp only [Formula.matches, Bool.and_eq_true, decide_eq_true_eq] at hm
    all_goals try contradiction
    obtain ⟨⟨⟨⟨rfl,rfl⟩,hm⟩,ht⟩,hu⟩ := hm
    rename_i body left right
    have he (x y : S.Carrier) := ih _ _ _ _
      (liftMatch_sound S _ _ _ (liftMatch_sound S ρ τ cmp h x) y) hm
    have heq : (fun x y => S.domain s x ∧ S.domain s y ∧ a.denote S (y :: x :: ρ)) =
        (fun x y => S.domain s x ∧ S.domain s y ∧ body.denote S (y :: x :: τ)) := by
      funext x y; exact propext (and_congr Iff.rfl (and_congr Iff.rfl (he x y)))
    simp only [Formula.denote, h _ _ ht, h _ _ hu, heq]

end VE.Closure
