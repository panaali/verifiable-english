import VE.Order.Consequence
import VE.Consequence

namespace VE.Order
universe u

def embedTerm : VE.Term → Term
  | .var i => .var i
  | .const c => .const c

def embed : VE.Formula → Formula
  | .top => .top
  | .bottom => .bottom
  | .unary p t => .unary p (embedTerm t)
  | .binary p t u => .binary p (embedTerm t) (embedTerm u)
  | .eq t u => .eq (embedTerm t) (embedTerm u)
  | .not a => .not (embed a)
  | .and a b => .and (embed a) (embed b)
  | .or a b => .or (embed a) (embed b)
  | .implies a b => .implies (embed a) (embed b)
  | .all s a => .all s (embed a)
  | .ex s a => .ex s (embed a)

def expandEnvironment (E : VE.Environment) : Environment where
  sorts := E.sorts
  constants c := (E.constants c).map SortName.user
  predicates p := (E.predicates p).map (List.map SortName.user)

/-- Every old structure has this expansion, including empty and infinite user
sorts. No integers are added to any old domain or old predicate extension. -/
def expandStructure (S : VE.Structure) : Structure where
  Carrier := S.Carrier
  objects := S.domain
  constant c := (S.constant c).map Sum.inl
  relation p vs := ∃ xs, vs = xs.map Sum.inl ∧ S.relation p xs

theorem embedTerm_denote (S : VE.Structure) (ρ : VE.Valuation S) (t : VE.Term) :
    (embedTerm t).denote (expandStructure S) (ρ.map Sum.inl) =
      (t.denote S ρ).map Sum.inl := by
  cases t <;> simp [embedTerm, Term.denote, VE.Term.denote, expandStructure]

theorem expand_relation_unary (S : VE.Structure) (p : String) (v : S.Carrier) :
    (expandStructure S).relation p [.inl v] ↔ S.relation p [v] := by
  simp only [expandStructure]
  constructor
  · rintro ⟨xs, h, hr⟩
    have hx : xs = [v] := (List.map_inj_right (fun _ _ he => Sum.inl.inj he)).mp h.symm
    simpa [hx] using hr
  · intro h; exact ⟨[v], rfl, h⟩

theorem expand_relation_binary (S : VE.Structure) (p : String) (v w : S.Carrier) :
    (expandStructure S).relation p [.inl v, .inl w] ↔ S.relation p [v, w] := by
  simp only [expandStructure]
  constructor
  · rintro ⟨xs, h, hr⟩
    have hx : xs = [v, w] := (List.map_inj_right (fun _ _ he => Sum.inl.inj he)).mp h.symm
    simpa [hx] using hr
  · intro h; exact ⟨[v, w], rfl, h⟩

theorem conservativity (S : VE.Structure) (ρ : VE.Valuation S) (a : VE.Formula) :
    (embed a).denote (expandStructure S) (ρ.map Sum.inl) ↔ a.denote S ρ := by
  induction a generalizing ρ with
  | top | bottom => simp [embed, Formula.denote, VE.Formula.denote]
  | unary p t =>
    simp only [embed, Formula.denote, VE.Formula.denote, embedTerm_denote]
    cases h : t.denote S ρ <;> simp
    exact expand_relation_unary S p _
  | binary p t u =>
    simp only [embed, Formula.denote, VE.Formula.denote, embedTerm_denote]
    cases h : t.denote S ρ <;> cases k : u.denote S ρ <;> simp
    exact expand_relation_binary S p _ _
  | eq t u =>
    simp only [embed, Formula.denote, VE.Formula.denote, embedTerm_denote]
    cases h : t.denote S ρ <;> cases k : u.denote S ρ <;> simp
  | not a ih => simp [embed, Formula.denote, VE.Formula.denote, ih]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    simp [embed, Formula.denote, VE.Formula.denote, ia, ib]
  | all s a ih =>
    change (∀ v, S.domain s v → (embed a).denote (expandStructure S) ((v :: ρ).map Sum.inl)) ↔ _
    simp only [ih, VE.Formula.denote]
  | ex s a ih =>
    change (∃ v, S.domain s v ∧ (embed a).denote (expandStructure S) ((v :: ρ).map Sum.inl)) ↔ _
    simp only [ih, VE.Formula.denote]

theorem tupleTyped_expand (S : VE.Structure) (ss : List String) (vs : List S.Carrier) :
    TupleTyped (expandStructure S) (ss.map SortName.user) (vs.map Sum.inl) ↔
      VE.TupleTyped S ss vs := by
  induction ss generalizing vs with
  | nil => cases vs <;> simp [TupleTyped, VE.TupleTyped]
  | cons s ss ih =>
    cases vs with
    | nil => simp [TupleTyped, VE.TupleTyped]
    | cons v vs =>
      change (_ ∧ TupleTyped (expandStructure S) _ _) ↔ (_ ∧ VE.TupleTyped S ss vs)
      exact and_congr Iff.rfl (ih vs)

theorem expansion_admissible (S : VE.Structure) (E : VE.Environment)
    (h : S.Admissible E) : (expandStructure S).Admissible (expandEnvironment E) := by
  constructor
  · intro c s hs
    simp only [expandEnvironment, Option.map_eq_some_iff] at hs
    obtain ⟨r, hr, rfl⟩ := hs
    obtain ⟨v, hv, hd⟩ := h.1 c r hr
    exact ⟨.inl v, by simp [expandStructure, hv], hd⟩
  · intro p vs hp
    obtain ⟨xs, rfl, hr⟩ := hp
    obtain ⟨ss, hs, ht⟩ := h.2 p xs hr
    exact ⟨ss.map SortName.user, by simp [expandEnvironment, hs],
      (tupleTyped_expand S ss xs).mpr ht⟩

/-- Adding standard integers creates no new entailments between old claims. -/
theorem entails_v0 (E : VE.Environment) (ps : List VE.Formula) (c : VE.Formula)
    (h : Entails.{u} (expandEnvironment E) (ps.map embed) (embed c)) :
    VE.Entails.{u} E ps c := by
  intro S hs hp
  apply (conservativity S [] c).mp
  apply h (expandStructure S) (expansion_admissible S E hs)
  intro a ha
  obtain ⟨b, hb, rfl⟩ := List.mem_map.mp ha
  exact (conservativity S [] b).mpr (hp b hb)

end VE.Order
