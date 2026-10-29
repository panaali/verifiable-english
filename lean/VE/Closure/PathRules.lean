import VE.Closure.Substitution

namespace VE.Closure
universe u

def composeKind : Kind → Kind → Kind
  | .star, .star => .star
  | _, _ => .plus

theorem reachable_trans {α : Type u} {R : α → α → Prop} (k l : Kind) {a b c : α}
    (h : Reachable k R a b) (g : Reachable l R b c) : Reachable (composeKind k l) R a c := by
  cases k <;> cases l <;> simp only [Reachable, composeKind] at *
  · exact h.trans g
  · rcases g with rfl | g
    · exact h
    · exact h.trans g
  · rcases h with rfl | h
    · exact g
    · exact h.trans g
  · rcases h with rfl | h
    · exact g
    · rcases g with rfl | g
      · exact .inr h
      · exact .inr (h.trans g)

theorem reach_compose (S : Structure) (ρ : Valuation S) (e : Edge) (k l : Kind) (a b c : Term)
    (h : (Formula.reach k e a b).denote S ρ) (g : (Formula.reach l e b c).denote S ρ) :
    (Formula.reach (composeKind k l) e a c).denote S ρ := by
  rw [reach_denote] at h g ⊢
  obtain ⟨x,y,hx,hy,h⟩ := h
  obtain ⟨y',z,hy',hz,g⟩ := g
  have he : y = y' := Option.some.inj (hy.symm.trans hy')
  subst y'
  exact ⟨x,z,hx,hz,reachable_trans k l h g⟩

theorem edge_inclusion (S : Structure) (ρ : Valuation S) (p : String) (t r : Term)
    (h : (Formula.binary p t r).denote S ρ) :
    (Formula.reachNamed .plus p t r).denote S ρ := by
  obtain ⟨x,y,hx,hy,h⟩ := h
  exact ⟨x,y,hx,hy,Path.edge h⟩

theorem Path.first {α : Type u} {R : α → α → Prop} {x y : α} (h : Path R x y) :
    ∃ z, R x z := by
  cases h with
  | edge h => exact ⟨_,h⟩
  | cons h _ => exact ⟨_,h⟩

theorem Path.last {α : Type u} {R : α → α → Prop} {x y : α} (h : Path R x y) :
    ∃ z, R z y := by
  induction h with
  | edge h => exact ⟨_,h⟩
  | cons _ _ ih => exact ih

def endEdge (last : Bool) (e : Edge) (s : String) (t r : Term) : Formula :=
  .ex s (if last then e.shift.at (.var 0) (liftTerm r)
    else e.shift.at (liftTerm t) (.var 0))

theorem endEdge_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (ρ : Valuation S) (last : Bool) (e : Edge) (s : String) (t r : Term)
    (he : e.Typed E s) (h : (Formula.reach .plus e t r).denote S ρ) :
    (endEdge last e s t r).denote S ρ := by
  obtain ⟨x,y,hx,hy,hp⟩ := (reach_denote S ρ .plus e t r).mp h
  have hs : ∀ q a, e.shift = .body q a → q = s := by
    cases e <;> simp_all [Edge.Typed, Edge.shift]
  cases last with
  | false =>
    obtain ⟨z,hz⟩ := hp.first
    have hd := edge_typed hS ρ e s he x z hz
    refine ⟨z,hd.2,?_⟩
    apply (edge_at_denote S (z :: ρ) e.shift (liftTerm t) (.var 0) x z
      (by rw [liftTerm_denote]; exact hx) rfl (by
        intro q a h; rw [hs q a h]; exact hd)).mpr
    rw [edge_shift_denote]; exact hz
  | true =>
    obtain ⟨z,hz⟩ := hp.last
    have hd := edge_typed hS ρ e s he z y hz
    refine ⟨z,hd.1,?_⟩
    apply (edge_at_denote S (z :: ρ) e.shift (.var 0) (liftTerm r) z y
      rfl (by rw [liftTerm_denote]; exact hy) (by
        intro q a h; rw [hs q a h]; exact hd)).mpr
    rw [edge_shift_denote]; exact hz

theorem named_body_denote {E : Environment} {S : Structure} (hS : S.Admissible E)
    (ρ : Valuation S) (k : Kind) (p s : String) (t r : Term)
    (hp : E.predicates p = some [s,s]) :
    (Formula.reachNamed k p t r).denote S ρ ↔
    (Formula.reachBody k s (.binary p (.var 1) (.var 0)) t r).denote S ρ := by
  have he : (fun x y => S.relation p [x,y]) =
      (fun x y => S.domain s x ∧ S.domain s y ∧
        (Formula.binary p (.var 1) (.var 0)).denote S (y :: x :: ρ)) := by
    funext x y
    apply propext
    simp only [Formula.denote, Term.denote, List.getElem?_cons_succ, List.getElem?_cons_zero,
      Option.some.injEq, pair_values]
    constructor
    · intro h
      have hd := edge_typed hS ρ (.named p) s hp x y h
      exact ⟨hd.1,hd.2,h⟩
    · exact fun h => h.2.2
  change (∃ x y, _ ∧ _ ∧ Reachable k _ x y) ↔ (∃ x y, _ ∧ _ ∧ Reachable k _ x y)
  rw [he]

end VE.Closure
