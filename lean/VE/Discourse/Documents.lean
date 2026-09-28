import VE.Discourse.Joint

/-! # Document names, validity verdicts and conservativity (docs/spec/discourse.md 1.6, 4.7, 9.6)

A document name is an ordinary declared constant of the manifest's `document_sort`; the
profile adds no symbol. `document_sort_conservative` shows that declaring a fresh sort
and fresh constant names changes no consequence over the old vocabulary. A validity
claim is evaluated in a second phase from three outcomes: admitted, rejected (a completed
non-resource diagnostic) and unknown; only the first two can make a claim `checked` or
`refuted`, and unknown is always `unconfirmed`. -/
namespace VE.Discourse
universe u

/-- The environment with a fresh document sort and its constants declared. -/
def withDocuments (E : VE.Environment) (sort : String) (names : List String) : VE.Environment where
  sorts := E.sorts ++ [sort]
  predicates := E.predicates
  constants := fun c => if c ∈ names then some sort else E.constants c

/-- 4.7: the three outcomes of checking another document; rejection is a completed diagnostic. -/
inductive ImportOutcome | admitted | rejected (diagnostic : String) | unknown (reason : String)
  deriving DecidableEq, Repr

def verdictOf (holds : Bool) : ImportOutcome → Verdict
  | .admitted => if holds then .checked else .refuted
  | .rejected _ => if holds then .refuted else .checked
  | .unknown r => .unconfirmed r

/-- An unknown outcome is never `checked` nor `refuted`, for either polarity. -/
theorem verdictOf_unknown (holds : Bool) (r : String) : verdictOf holds (.unknown r) = .unconfirmed r := rfl

/-- A negative claim is `checked` only against a completed rejection. -/
theorem verdictOf_negative_checked (o : ImportOutcome) (h : verdictOf false o = .checked) :
    ∃ e, o = .rejected e := by
  cases o with
  | admitted => simp [verdictOf] at h
  | rejected e => exact ⟨e, rfl⟩
  | unknown r => simp [verdictOf] at h

def refersSelf (D : DDoc) (name : String) : Prop := ∃ d ∈ D.K.documents, d.name = name ∧ d.refers = .self
def refersImport (D : DDoc) (name key : String) : Prop :=
  ∃ d ∈ D.K.documents, d.name = name ∧ d.refers = .imported key

def stripValidity (D : DDoc) : DDoc := { D with K := { D.K with validity := [] } }

/-! ## Conservativity of document names -/

section Conservative
variable (S : VE.Structure.{u}) (sort : String) (names : List String)

/-- The old structure with one fresh element (`none`) for every document constant. -/
def extendDocs : VE.Structure.{u} where
  Carrier := Option S.Carrier
  domain s v := match v with
    | some w => S.domain s w
    | none => s = sort
  constant c := if c ∈ names then some none else (S.constant c).map some
  relation p vs := ∃ ws, vs = ws.map some ∧ S.relation p ws

variable {S sort names}

theorem extend_term {E : VE.Environment} (hfresh : ∀ n ∈ names, E.constants n = none)
    {Γ : List String} {t : VE.Term} {s : String} (ht : t.sortOf E Γ = some s) (ρ : VE.Valuation S) :
    t.denote (extendDocs S sort names) (ρ.map some) = (t.denote S ρ).map some := by
  cases t with
  | var i => simp [VE.Term.denote]
  | const c =>
    have hc : c ∉ names := fun hm => by
      simp only [VE.Term.sortOf] at ht
      rw [hfresh c hm] at ht
      cases ht
    simp [VE.Term.denote, extendDocs, hc]

theorem extend_denote {E : VE.Environment} (hs : sort ∉ E.sorts) (hfresh : ∀ n ∈ names, E.constants n = none) :
    ∀ (a : VE.Formula) (Γ : List String) (ρ : VE.Valuation S), a.WellFormed E Γ →
      (a.denote (extendDocs S sort names) (ρ.map some) ↔ a.denote S ρ)
  | .top, _, _, _ => Iff.rfl
  | .bottom, _, _, _ => Iff.rfl
  | .unary p t, Γ, ρ, h => by
    obtain ⟨s, _, ht⟩ := h
    simp only [VE.Formula.denote, extend_term hfresh ht ρ]
    constructor
    · rintro ⟨v, hv, ws, hws, hr⟩
      cases hd : t.denote S ρ with
      | none => rw [hd] at hv; cases hv
      | some w =>
        rw [hd] at hv
        simp only [Option.map_some, Option.some.injEq] at hv
        subst hv
        match ws, hws with
        | [w'], hws =>
          simp only [List.map_cons, List.map_nil] at hws
          injection hws with h1 _
          injection h1 with h1
          subst h1
          exact ⟨w, rfl, hr⟩
    · rintro ⟨v, hv, hr⟩
      exact ⟨some v, by rw [hv]; rfl, [v], rfl, hr⟩
  | .binary p t w, Γ, ρ, h => by
    obtain ⟨s, r, _, ht, hw⟩ := h
    simp only [VE.Formula.denote, extend_term hfresh ht ρ, extend_term hfresh hw ρ]
    constructor
    · rintro ⟨v, v', hv, hv', ws, hws, hr⟩
      cases hd : t.denote S ρ with
      | none => rw [hd] at hv; cases hv
      | some x =>
        cases hd' : w.denote S ρ with
        | none => rw [hd'] at hv'; cases hv'
        | some y =>
          rw [hd] at hv; rw [hd'] at hv'
          simp only [Option.map_some, Option.some.injEq] at hv hv'
          subst hv hv'
          match ws, hws with
          | [x', y'], hws =>
            simp only [List.map_cons, List.map_nil] at hws
            injection hws with h1 h2
            injection h2 with h2 _
            injection h1 with h1
            injection h2 with h2
            subst h1 h2
            exact ⟨x, y, rfl, rfl, hr⟩
    · rintro ⟨v, v', hv, hv', hr⟩
      exact ⟨some v, some v', by rw [hv]; rfl, by rw [hv']; rfl, [v, v'], rfl, hr⟩
  | .eq t w, Γ, ρ, h => by
    obtain ⟨s, ht, hw⟩ := h
    simp only [VE.Formula.denote, extend_term hfresh ht ρ, extend_term hfresh hw ρ]
    constructor
    · rintro ⟨v, hv, hv'⟩
      cases hd : t.denote S ρ with
      | none => rw [hd] at hv; cases hv
      | some x =>
        cases hd' : w.denote S ρ with
        | none => rw [hd'] at hv'; cases hv'
        | some y =>
          rw [hd] at hv; rw [hd'] at hv'
          simp only [Option.map_some] at hv hv'
          rw [← hv'] at hv
          exact ⟨x, rfl, by rw [Option.some.inj hv]⟩
    · rintro ⟨v, hv, hv'⟩
      exact ⟨some v, by rw [hv]; rfl, by rw [hv']; rfl⟩
  | .not a, Γ, ρ, h => by
    simp only [VE.Formula.denote, extend_denote hs hfresh a Γ ρ h]
  | .and a b, Γ, ρ, h => by
    simp only [VE.Formula.denote, extend_denote hs hfresh a Γ ρ h.1, extend_denote hs hfresh b Γ ρ h.2]
  | .or a b, Γ, ρ, h => by
    simp only [VE.Formula.denote, extend_denote hs hfresh a Γ ρ h.1, extend_denote hs hfresh b Γ ρ h.2]
  | .implies a b, Γ, ρ, h => by
    simp only [VE.Formula.denote, extend_denote hs hfresh a Γ ρ h.1, extend_denote hs hfresh b Γ ρ h.2]
  | .all s a, Γ, ρ, h => by
    have hne : s ≠ sort := fun e => hs (e ▸ h.1)
    simp only [VE.Formula.denote]
    constructor
    · intro hall v hv
      have := hall (some v) hv
      rwa [show some v :: ρ.map some = (v :: ρ).map some from rfl, extend_denote hs hfresh a (s :: Γ) _ h.2] at this
    · intro hall v hv
      match v, hv with
      | some w, hv =>
        rw [show some w :: ρ.map some = (w :: ρ).map some from rfl, extend_denote hs hfresh a (s :: Γ) _ h.2]
        exact hall w hv
      | none, hv => exact absurd hv hne
  | .ex s a, Γ, ρ, h => by
    have hne : s ≠ sort := fun e => hs (e ▸ h.1)
    simp only [VE.Formula.denote]
    constructor
    · rintro ⟨v, hv, hb⟩
      match v, hv, hb with
      | some w, hv, hb =>
        rw [show some w :: ρ.map some = (w :: ρ).map some from rfl, extend_denote hs hfresh a (s :: Γ) _ h.2] at hb
        exact ⟨w, hv, hb⟩
      | none, hv, _ => exact absurd hv hne
    · rintro ⟨w, hv, hb⟩
      refine ⟨some w, hv, ?_⟩
      rw [show some w :: ρ.map some = (w :: ρ).map some from rfl, extend_denote hs hfresh a (s :: Γ) _ h.2]
      exact hb

theorem extend_admissible {E : VE.Environment} (hS : S.Admissible E) (hfresh : ∀ n ∈ names, E.constants n = none) :
    (extendDocs S sort names).Admissible (withDocuments E sort names) := by
  refine ⟨fun c s hc => ?_, fun p vs hp => ?_⟩
  · by_cases hm : c ∈ names
    · simp only [withDocuments, hm, if_true, Option.some.injEq] at hc
      subst hc
      exact ⟨none, by simp [extendDocs, hm], rfl⟩
    · simp only [withDocuments, hm, if_false] at hc
      obtain ⟨v, hv, hd⟩ := hS.1 c s hc
      exact ⟨some v, by simp [extendDocs, hm, hv], hd⟩
  · obtain ⟨ws, rfl, hr⟩ := hp
    obtain ⟨ss, hss, ht⟩ := hS.2 p ws hr
    refine ⟨ss, hss, ?_⟩
    clear hss hr
    induction ss generalizing ws with
    | nil => cases ws <;> simp_all [VE.TupleTyped]
    | cons s ss ih =>
      cases ws with
      | nil => simp [VE.TupleTyped] at ht
      | cons w ws => exact ⟨ht.1, ih ws ht.2⟩

end Conservative

/-- Declaring a fresh document sort and fresh constant names changes no old-vocabulary consequence. -/
theorem document_sort_conservative (E : VE.Environment) (sort : String) (hs : sort ∉ E.sorts) (names : List String)
    (hfresh : ∀ n ∈ names, E.constants n = none) (hnodup : names.Nodup)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ g ∈ Γ, g.WellFormed E []) (hφ : φ.WellFormed E []) :
    VE.Entails.{u} (withDocuments E sort names) Γ φ ↔ VE.Entails.{u} E Γ φ := by
  constructor
  · intro h S hS hp
    have := h (extendDocs S sort names) (extend_admissible hS hfresh) (fun a ha => by
      have := (extend_denote hs hfresh a [] [] (hΓ a ha)).mpr (hp a ha)
      simpa using this)
    have e := (extend_denote (S := S) hs hfresh φ [] [] hφ)
    simp only [List.map_nil] at e
    exact e.mp this
  · intro h S hS hp
    have hS' : S.Admissible E := by
      refine ⟨fun c s hc => ?_, hS.2⟩
      have hm : c ∉ names := fun hm => by rw [hfresh c hm] at hc; cases hc
      exact hS.1 c s (by simp [withDocuments, hm, hc])
    exact h S hS' hp

end VE.Discourse
