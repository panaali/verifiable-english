import VE.SpeechActs.Answer

/-! Consequence questions, exact consequence correspondence, dormant-request
invariance and scope (docs/spec/speech-acts.md 4.6, 4.7, 4.8 and 8.4).

`follows` is an accepted certificate over the query's regenerated premise list,
`gap` a validated finite countermodel of it; there is no `refuted` judgment.
`premises D` and `policy D` are functions of the active core alone, so
questions, answer and compliance records, dormant units and bindings (which
`SpeechDoc` does not even carry) contribute nothing. `speech_route_acceptance`
is W1's `norms_route_acceptance` on the regenerated policy, verbatim.

`gap_sound` is stated for `Entails` at every universe: a countermodel in
`Type` refutes consequence over structures of any universe, through
`entails_lower` (a structure lifts along `ULift` with the same truths). -/
namespace VE.SpeechActs
open VE.Norms (Sat background elaborate BaseAdmissible ConflictFree holdsCatala definitionsHold profileHold
  backgroundBase envAt size Node)
universe u v

/-! ## Lifting a structure to a higher universe -/

/-- The same structure over `ULift` of its carrier. -/
def liftStructure (S : VE.Structure.{0}) : VE.Structure.{v} where
  Carrier := ULift.{v} S.Carrier
  domain s x := S.domain s x.down
  constant c := (S.constant c).map ULift.up
  relation p xs := S.relation p (xs.map ULift.down)

theorem liftStructure_term (S : VE.Structure.{0}) (ρ : VE.Valuation S) (t : VE.Term) :
    t.denote (liftStructure.{v} S) (ρ.map ULift.up) = (t.denote S ρ).map ULift.up := by
  cases t with
  | var i => simp [VE.Term.denote]
  | const c => rfl

theorem liftStructure_denote (S : VE.Structure.{0}) (a : VE.Formula) :
    ∀ ρ : VE.Valuation S, a.denote (liftStructure.{v} S) (ρ.map ULift.up) ↔ a.denote S ρ := by
  induction a with
  | top | bottom => intro ρ; simp [VE.Formula.denote]
  | unary p t =>
    intro ρ
    simp only [VE.Formula.denote, liftStructure_term]
    constructor
    · rintro ⟨x, hx, hr⟩
      cases ht : t.denote S ρ <;> rw [ht] at hx <;> simp at hx
      subst hx
      exact ⟨_, rfl, by simpa [liftStructure] using hr⟩
    · rintro ⟨x, hx, hr⟩
      exact ⟨ULift.up x, by rw [hx]; rfl, by simpa [liftStructure] using hr⟩
  | binary p t w =>
    intro ρ
    simp only [VE.Formula.denote, liftStructure_term]
    constructor
    · rintro ⟨x, y, hx, hy, hr⟩
      cases ht : t.denote S ρ <;> rw [ht] at hx <;> simp at hx
      cases hw : w.denote S ρ <;> rw [hw] at hy <;> simp at hy
      subst hx hy
      exact ⟨_, _, rfl, rfl, by simpa [liftStructure] using hr⟩
    · rintro ⟨x, y, hx, hy, hr⟩
      exact ⟨ULift.up x, ULift.up y, by rw [hx]; rfl, by rw [hy]; rfl, by simpa [liftStructure] using hr⟩
  | eq t w =>
    intro ρ
    simp only [VE.Formula.denote, liftStructure_term]
    constructor
    · rintro ⟨x, hx, hy⟩
      cases ht : t.denote S ρ <;> rw [ht] at hx <;> simp at hx
      cases hw : w.denote S ρ <;> rw [hw] at hy <;> simp at hy
      subst hx
      exact ⟨_, rfl, by rw [ULift.up.injEq] at hy; rw [hy]⟩
    · rintro ⟨x, hx, hy⟩
      exact ⟨ULift.up x, by rw [hx]; rfl, by rw [hy]; rfl⟩
  | not a ih => intro ρ; simp only [VE.Formula.denote]; rw [ih ρ]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro ρ; simp only [VE.Formula.denote]; rw [ia ρ, ib ρ]
  | all s a ih =>
    intro ρ
    simp only [VE.Formula.denote]
    constructor
    · intro h x hx
      exact (ih (x :: ρ)).mp (h (ULift.up x) hx)
    · intro h x hx
      exact (ih (x.down :: ρ)).mpr (h x.down hx)
  | ex s a ih =>
    intro ρ
    simp only [VE.Formula.denote]
    constructor
    · rintro ⟨x, hx, ha⟩
      exact ⟨x.down, hx, (ih (x.down :: ρ)).mp ha⟩
    · rintro ⟨x, hx, ha⟩
      exact ⟨ULift.up x, hx, (ih (x :: ρ)).mpr ha⟩

theorem liftStructure_admissible (S : VE.Structure.{0}) (E : VE.Environment) (h : S.Admissible E) :
    (liftStructure.{v} S).Admissible E := by
  have typed : ∀ (ss : List String) (xs : List (ULift.{v} S.Carrier)),
      VE.TupleTyped S ss (xs.map ULift.down) → VE.TupleTyped (liftStructure.{v} S) ss xs := by
    intro ss
    induction ss with
    | nil => intro xs hx; cases xs with
      | nil => trivial
      | cons _ _ => exact hx.elim
    | cons s ss ih => intro xs hx; cases xs with
      | nil => exact hx.elim
      | cons x xs => exact ⟨hx.1, ih xs hx.2⟩
  refine ⟨fun c s hc => ?_, fun p xs hr => ?_⟩
  · obtain ⟨x, hx, hd⟩ := h.1 c s hc
    exact ⟨ULift.up x, by simp [liftStructure, hx], hd⟩
  · obtain ⟨ss, hss, ht⟩ := h.2 p _ hr
    exact ⟨ss, hss, typed ss xs ht⟩

/-- Consequence over structures of any universe implies consequence over structures in `Type`. -/
theorem entails_lower {E : VE.Environment} {Γ : List VE.Formula} {φ : VE.Formula}
    (h : VE.Entails.{v} E Γ φ) : VE.Entails.{0} E Γ φ := by
  intro S hS hΓ
  have := h (liftStructure.{v} S) (liftStructure_admissible S E hS)
    (fun a ha => (liftStructure_denote S a []).mpr (hΓ a ha))
  exact (liftStructure_denote S φ []).mp this

/-! ## 8.4 -/

/-- 4.6 -/
theorem follows_sound (D : SpeechDoc) (h : WellFormedSpeech D = true) (qr : Query) (hq : qr ∈ D.queries)
    (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (queryPremises D qr) qr.target c = true) :
    VE.Entails (En D) (queryPremises D qr) qr.target :=
  VE.Tableau.checkCertificate_sound _ _ _ c acc

theorem gap_sound {α : Type} [DecidableEq α] (D : SpeechDoc) (h : WellFormedSpeech D = true) (qr : Query)
    (hq : qr ∈ D.queries) (M : VE.FiniteModel α) (valid : M.Valid (En D))
    (hb : VE.Norms.backgroundValid (policy D) M = true)
    (hs : (queryPremises D qr).all (fun φ => φ.eval M []) = true) (hn : qr.target.eval M [] = false) :
    ¬ VE.Entails (En D) (queryPremises D qr) qr.target := by
  intro he
  exact VE.countermodel_sound M valid _ _ (by simp [VE.countermodelCheck, hs, hn]) (entails_lower he)

theorem follows_gap_exclusive {α : Type} [DecidableEq α] (D : SpeechDoc) (h : WellFormedSpeech D = true)
    (qr : Query) (hq : qr ∈ D.queries) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (queryPremises D qr) qr.target c = true)
    (M : VE.FiniteModel α) (valid : M.Valid (En D)) (hb : VE.Norms.backgroundValid (policy D) M = true)
    (hs : (queryPremises D qr).all (fun φ => φ.eval M []) = true) (hn : qr.target.eval M [] = false) : False :=
  gap_sound D h qr hq M valid hb hs hn (follows_sound.{0} D h qr hq c acc)

/-- The target never enters its own premise list through the query (`pinnedAsserted`, `trivialQuery`: 8.1). -/
theorem query_target_separate (D : SpeechDoc) (h : WellFormedSpeech D = true) (qr : Query) (hq : qr ∈ D.queries) :
    qr.premises = pinnedAsserted D qr ∧ (qr.target ∈ qr.premises → trivialQuery D qr = true) := by
  have hk := (validSpeech_of_wellFormed D h).queries qr hq
  simp only [queryOk, Bool.and_eq_true, decide_eq_true_eq] at hk
  have he := hk.1.1
  refine ⟨he, fun hm => ?_⟩
  simp only [trivialQuery, decide_eq_true_eq]
  exact he ▸ hm

/-- 4.7: premises depend only on the active core; questions, answers, compliance and dormant units contribute nothing. -/
theorem premises_core (D D₂ : SpeechDoc) (h : WellFormedSpeech D = true) (h₂ : WellFormedSpeech D₂ = true)
    (hc : core D = core D₂) : premises D = premises D₂ ∧ policy D = policy D₂ := by
  obtain ⟨E, lits, scope, regulated, norms, commands, questions, queries, asserted⟩ := D
  obtain ⟨E₂, lits₂, scope₂, regulated₂, norms₂, commands₂, questions₂, queries₂, asserted₂⟩ := D₂
  simp only [core, Prod.mk.injEq] at hc
  obtain ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩ := hc
  exact ⟨rfl, rfl⟩

theorem questions_no_premises (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions) :
    premises D = premises { D with questions := D.questions.erase q } := rfl

/-- Dormant-request invariance as verdict invariance: the same certificates replay and the same models refute. -/
theorem dormant_invariance (D D₂ : SpeechDoc) (h : WellFormedSpeech D = true) (h₂ : WellFormedSpeech D₂ = true)
    (hc : core D = core D₂) (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate) :
    (VE.Tableau.checkCertificate (En D) (premises D ++ Γ) φ c =
      VE.Tableau.checkCertificate (En D₂) (premises D₂ ++ Γ) φ c) ∧
    (∀ B : VE.Structure, BaseAdmissible (policy D) B → (ConflictFree (policy D) B ↔ ConflictFree (policy D₂) B)) := by
  obtain ⟨hp, hpol⟩ := premises_core D D₂ h h₂ hc
  have hE : En D = En D₂ := by simp only [En, hpol]
  exact ⟨by rw [hp, hE], fun B _ => by rw [hpol]⟩

/-- Ordinary composition preserved: W1's route acceptance on the regenerated policy, verbatim. `norms_route_acceptance`
    (Layer.lean:261) has exactly the binders `D h hc Γ φ c accepted`; the well-formedness of `Γ` and `φ` over
    `envAt D 0` is a hypothesis of its second conjunct, not a binder. As in W1, every structure ranges over one
    universe. -/
theorem speech_route_acceptance (D : SpeechDoc) (h : WellFormedSpeech D = true)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissible (policy D) B → ConflictFree (policy D) B)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (background (policy D) ++ elaborate (policy D).T ++ Γ) φ c = true) :
    (∀ S : VE.Structure.{u}, S.Admissible (En D) → holdsCatala (policy D).T S → definitionsHold (policy D) S →
       profileHold (policy D) S → Sat S (backgroundBase (policy D)) → Sat S Γ → φ.denote S []) ∧
    ((∀ a ∈ Γ, a.WellFormed (envAt (policy D) 0) []) → φ.WellFormed (envAt (policy D) 0) [] →
       ∀ B : VE.Structure.{u}, BaseAdmissible (policy D) B → Sat B Γ → φ.denote B []) :=
  VE.Norms.norms_route_acceptance (policy D) (policy_wellFormed D h) hc Γ φ c acc

/-- The answer-to-claim bridge licenses exactly H ∧ F of a certificate-supported answer. -/
theorem answer_bridge_sound (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (a : Answer) (φ : VE.Formula) (hφ : correct D q a = some φ) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) φ) c = true)
    (S : VE.Structure) (hS : S.Admissible (En D)) (hp : Sat S (premises D)) :
    (VE.Formula.and (presupposition D q) φ).denote S [] :=
  VE.Tableau.checkCertificate_sound _ _ _ c acc S hS hp

/-- 4.8 -/
theorem combine_scope (D₁ D₂ D : SpeechDoc) (h : combine D₁ D₂ = .ok D) :
    D₁.scope = D₂.scope ∧ D₁.E = D₂.E ∧ D.commands = D₁.commands ++ D₂.commands := by
  unfold combine at h
  split at h
  · cases h
  · rename_i hs
    split at h
    · rename_i he
      cases h
      exact ⟨Classical.byContradiction hs, he.1, rfl⟩
    · cases h

theorem two_task_separation (D₁ D₂ : SpeechDoc) (hs : D₁.scope ≠ D₂.scope) :
    combine D₁ D₂ = .error ("ScopeMismatch: " ++ D₁.scope.task ++ ", " ++ D₂.scope.task) := by
  unfold combine
  rw [if_pos hs]

/-- No policy contains rules of two scopes: every rule of policy D is an author unit of D or a demand of D's commands. -/
theorem policy_rules (D : SpeechDoc) (h : WellFormedSpeech D = true) (N : Node) (hN : N ∈ (policy D).T.nodes) :
    N ∈ D.norms ∨ ∃ c ∈ D.commands, N = demand D c := by
  rw [policy_nodes] at hN
  rcases List.mem_append.mp hN with hN | hN
  · exact Or.inl hN
  · obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hN
    exact Or.inr ⟨c, hc, rfl⟩

end VE.SpeechActs
