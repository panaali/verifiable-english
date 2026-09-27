import VE.Definitions.Layer

/-! The route acceptance theorems for `definitions@0` (PLAN-EXPAND2 W3 and 3.4),
instantiated through the frozen `Layer` and the abstract route theorems of
`VE.Route.Route`. Background on the FOL and closure families is
`expand ds ++ literals lits` (the Background hook order: definitions, then
literals), followed by the case's premises. The checker is unchanged: the
definitions are premises. -/
namespace VE.Definitions
universe u
open VE.Route VE.Route.Background

/-- The definitions slice of Background followed by the literals slice. -/
def background (ds : List Def) (lits : List String) : List VE.Formula := expand ds ++ literals lits

/-- The reviewed meaning of the full vocabulary: string-admissible and every
defined predicate agrees with its body. -/
def Intended (E : VE.Environment) (ds : List Def) (lits : List String) (S : VE.Structure.{u}) : Prop :=
  StringAdmissible E lits S ∧ ∀ d ∈ ds, Agrees S d

theorem literalsFree (lits : List String) : RelationFree.{u} (fun S => LiteralsDistinct S lits) :=
  fun _ _ => Iff.rfl

/-- The route layer of a checked definition list, over string-admissible
structures. -/
def routeLayer (E : VE.Environment) (ds : List Def) (h : Chain E ds) (lits : List String) :
    Layer fol.{u} Unit :=
  layer E ds h (fun S => LiteralsDistinct S lits) (literalsFree lits)

theorem routeLayer_background_sound (E : VE.Environment) (ds : List Def) (h : Chain E ds)
    (lits : List String) (hn : lits.Nodup) :
    BackgroundSound (routeLayer.{u} E ds h lits) (literals lits) := by
  intro _ S hS _
  have := ((chainLayer (Doc := Unit) E _ (literalsFree lits) ds h).Admissible_out S).mp hS
  exact (literals_sat_iff S lits hn).mpr this.2

theorem sat_background_iff (ds : List Def) (lits : List String) (Γ : List VE.Formula)
    (S : VE.Structure.{u}) :
    (∀ a ∈ background ds lits ++ Γ, a.denote S []) ↔
      (∀ a ∈ literals lits ++ expand ds ++ Γ, a.denote S []) := by
  simp only [background, List.mem_append]
  constructor
  · intro h a ha
    rcases ha with (ha | ha) | ha
    · exact h a (Or.inl (Or.inr ha))
    · exact h a (Or.inl (Or.inl ha))
    · exact h a (Or.inr ha)
  · intro h a ha
    rcases ha with (ha | ha) | ha
    · exact h a (Or.inl (Or.inr ha))
    · exact h a (Or.inl (Or.inl ha))
    · exact h a (Or.inr ha)

/-- The route acceptance theorem for definitions on the FOL family. An
accepted tableau certificate for `Background ++ Γ ⊢ φ`, where Background is the
definitions followed by the literals, gives

1. the checked entailment over the full vocabulary;
2. `φ` in every intended structure (string-admissible, every defined predicate
   agreeing with its body) satisfying `Γ`;
3. for `Γ` and `φ` over the base vocabulary (no defined predicate):
   `φ` in every string-admissible base structure satisfying `Γ`
   (conservativity: the definitions add no base consequences);
4. for every string-admissible base structure, its unique expansion by the
   definitions satisfies `Γ → φ`. -/
theorem acceptance (E : VE.Environment) (ds : List Def) (h : Chain E ds)
    (lits : List String) (hn : lits.Nodup) (Γ : List VE.Formula) (φ : VE.Formula)
    (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate E (background ds lits ++ Γ) φ c = true) :
    VE.Entails.{u} E (background ds lits ++ Γ) φ ∧
      (∀ S : VE.Structure.{u}, Intended E ds lits S → (∀ a ∈ Γ, a.denote S []) → φ.denote S []) ∧
      ((∀ a ∈ Γ, a.WellFormed (hide E (names ds)) []) → φ.WellFormed (hide E (names ds)) [] →
        ∀ S₀ : VE.Structure.{u}, StringAdmissible (hide E (names ds)) lits S₀ →
          (∀ a ∈ Γ, a.denote S₀ []) → φ.denote S₀ []) ∧
      (∀ S₀ : VE.Structure.{u}, StringAdmissible (hide E (names ds)) lits S₀ →
        ∃ S : VE.Structure.{u}, forget (names ds) S = S₀ ∧ Intended E ds lits S ∧
          ((∀ a ∈ Γ, a.denote S []) → φ.denote S [])) := by
  have he : VE.Entails.{u} E (background ds lits ++ Γ) φ :=
    VE.Tableau.checkCertificate_sound E _ φ c accepted
  let c := chainLayer (Doc := Unit) E _ (literalsFree lits) ds h
  let R := routeLayer.{u} E ds h lits
  have hbg := routeLayer_background_sound.{u} E ds h lits hn
  have hout : ∀ S, R.Admissible_out S ↔ StringAdmissible E lits S := fun S => by
    show c.layer.Admissible_out S ↔ _
    rw [c.Admissible_out, hide_nil]; rfl
  have hR : fol.Entails R.E_out (checkedPremises R (literals lits) () Γ) φ := by
    intro S hS hs
    have hS' : S.Admissible E := by
      have : R.E_out = E := by show c.layer.E_out = E; rw [c.E_out, hide_nil]
      rw [← this]; exact hS
    apply he S hS'
    apply (sat_background_iff ds lits Γ S).mpr
    have hp : R.premises () = expand ds := c.premises ()
    simpa [checkedPremises, hp] using hs
  have hint : ∀ S, Intended E ds lits S → (∀ a ∈ Γ, a.denote S []) → φ.denote S [] := by
    intro S hS hΓ
    have hSo := (hout S).mpr hS.1
    have hp : ∀ a ∈ R.premises (), a.denote S [] := by
      have : R.premises () = expand ds := c.premises ()
      rw [this]; exact (faithful ds (chain_arity E ds h) S).mpr hS.2
    exact route_intended R (literals lits) hbg () Γ φ hR S hSo ((R.faithful () S hSo).mp hp) hΓ
  refine ⟨he, hint, fun hΓ hφ S₀ h₀ hs => ?_, fun S₀ h₀ => ?_⟩
  · have hwΓ : ∀ a ∈ Γ, fol.WellFormed R.E_in a := fun a ha => by
      show a.WellFormed c.layer.E_in []; rw [c.E_in]; exact hΓ a ha
    have hwφ : fol.WellFormed R.E_in φ := by show φ.WellFormed c.layer.E_in []; rw [c.E_in]; exact hφ
    exact route_base R (literals lits) hbg () Γ φ hwΓ hwφ hR S₀
      ((c.Admissible_in S₀).mpr ⟨h₀.1, h₀.2⟩) hs
  · obtain ⟨S, ⟨hr, ha, hp⟩, _⟩ := conservative E ds h _ (literalsFree lits) S₀ h₀.1 h₀.2
    have hi : Intended E ds lits S := ⟨⟨ha.1, ha.2⟩, (faithful ds (chain_arity E ds h) S).mp hp⟩
    exact ⟨S, hr, hi, hint S hi⟩

/-- Model correspondence for definitions: a finite model satisfying the
regenerated Background (every defined table equal to its body's extension,
distinct literals) is an intended structure, so a checked countermodel refutes
the statement over intended structures. -/
theorem countermodel {α : Type u} [DecidableEq α] (E : VE.Environment) (ds : List Def)
    (h : Chain E ds) (lits : List String) (hn : lits.Nodup) (M : VE.FiniteModel α)
    (valid : M.Valid E) (hb : (background ds lits).all (fun a => a.eval M []) = true)
    (Γ : List VE.Formula) (φ : VE.Formula) (checked : VE.countermodelCheck M Γ φ = true) :
    Intended E ds lits M.asStructure ∧
      ¬ (∀ S : VE.Structure.{u}, Intended E ds lits S → (∀ a ∈ Γ, a.denote S []) → φ.denote S []) := by
  have hsat : ∀ a ∈ background ds lits, a.denote M.asStructure [] :=
    fun a ha => (VE.eval_iff_denote M [] a).mp (List.all_eq_true.mp hb a ha)
  have hi : Intended E ds lits M.asStructure :=
    ⟨⟨valid, (literals_sat_iff _ lits hn).mp (fun a ha => hsat a (List.mem_append_right _ ha))⟩,
      (faithful ds (chain_arity E ds h) _).mp (fun a ha => hsat a (List.mem_append_left _ ha))⟩
  obtain ⟨hp, hc⟩ := (VE.countermodelCheck_iff M Γ φ).mp checked
  exact ⟨hi, fun hall => hc (hall _ hi hp)⟩

/-- The closure family: Background (definitions, then literals) is embedded
unchanged. An accepted closure certificate proves `φ` in every intended
structure satisfying `Γ`, and in the unique expansion of every
string-admissible base structure. -/
theorem closure_acceptance (E : VE.Environment) (ds : List Def) (h : Chain E ds)
    (lits : List String) (hn : lits.Nodup) (Γ : List VE.Closure.Formula) (φ : VE.Closure.Formula)
    (c : VE.Closure.Tableau.Certificate)
    (accepted : VE.Closure.Tableau.checkCertificate E
      ((background ds lits).map VE.Closure.embed ++ Γ) φ c = true) :
    (∀ S : VE.Structure.{u}, Intended E ds lits S → (∀ a ∈ Γ, a.denote S []) → φ.denote S []) ∧
      (∀ S₀ : VE.Structure.{u}, StringAdmissible (hide E (names ds)) lits S₀ →
        ∃ S : VE.Structure.{u}, forget (names ds) S = S₀ ∧ Intended E ds lits S ∧
          ((∀ a ∈ Γ, a.denote S []) → φ.denote S [])) := by
  have hint : ∀ S : VE.Structure.{u}, Intended E ds lits S → (∀ a ∈ Γ, a.denote S []) →
      φ.denote S [] := by
    intro S hS hΓ
    apply VE.Closure.Tableau.checkCertificate_sound E _ φ c accepted S hS.1.1
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · obtain ⟨b, hb, rfl⟩ := List.mem_map.mp ha
      apply (VE.Closure.conservativity S [] b).mpr
      rcases List.mem_append.mp hb with hb | hb
      · exact (faithful ds (chain_arity E ds h) S).mpr hS.2 b hb
      · exact (literals_sat_iff S lits hn).mpr hS.1.2 b hb
    · exact hΓ a ha
  refine ⟨hint, fun S₀ h₀ => ?_⟩
  obtain ⟨S, ⟨hr, ha, hp⟩, _⟩ := conservative E ds h _ (literalsFree lits) S₀ h₀.1 h₀.2
  have hi : Intended E ds lits S := ⟨⟨ha.1, ha.2⟩, (faithful ds (chain_arity E ds h) S).mp hp⟩
  exact ⟨S, hr, hi, hint S hi⟩

end VE.Definitions
