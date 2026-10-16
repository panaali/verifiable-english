import VE.NormDefaults.Layered

/-! Entailment and finite models for the layered route's extra base premises. -/
namespace VE.NormDefaults
open VE.Norms
universe u

def Wire.premisesX (U : UDoc) (X Γ : List VE.Formula) : List VE.Formula :=
  background (fill U) ++ X ++ fillPremises U ++ elaborate (fill U).T ++ Γ

theorem Wire.premisesX_nil (U : UDoc) (Γ : List VE.Formula) : Wire.premisesX U [] Γ = Wire.premisesU U Γ := by
  simp [Wire.premisesX, Wire.premisesU]

def EntailsX (U : UDoc) (X Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∀ S : VE.Structure.{u}, Wire.BaseAdmissibleX U X (restrictAll (fill U).T S) →
    DocumentExpansion (fill U) (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S []

theorem baseAdmissibleX_nil (U : UDoc) (B : VE.Structure.{u}) :
    Wire.BaseAdmissibleX U [] B ↔ BaseAdmissibleU U B := by
  simp [Wire.BaseAdmissibleX, Sat]

theorem entailsX_nil (U : UDoc) (Γ : List VE.Formula) (φ : VE.Formula) :
    EntailsX.{u} U [] Γ φ ↔ EntailsU.{u} U Γ φ := by
  simp [EntailsX, EntailsU, Wire.BaseAdmissibleX, Sat]

theorem conflictFreeX_nil (U : UDoc) : Wire.ConflictFreeX.{u} U [] ↔ ConflictFreeU.{u} U := by
  simp [Wire.ConflictFreeX, ConflictFreeU, Wire.BaseAdmissibleX, Sat]

theorem acceptanceX (U : UDoc) (h : WellFormedU U = true) (X : List VE.Formula)
    (hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill U) (size (fill U))) (Wire.premisesX U X Γ) φ cert = true) :
    EntailsX.{u} U X Γ φ := by
  intro S hBU hE hΓ
  apply VE.Tableau.checkCertificate_sound.{u} _ _ _ cert hv S hE.2.1
  intro a ha
  simp only [Wire.premisesX, List.mem_append] at ha
  rcases ha with (((ha | ha) | ha) | ha) | ha
  · exact hE.2.2 a (List.mem_append_left _ ha)
  · exact (restrictAll_denote a [] (hX a ha) S []).mp (hBU.2 a ha)
  · exact (restrictAll_denote a [] (Wire.fillPremises_wellFormed h a ha) S []).mp (hBU.1.2 a ha)
  · exact hE.2.2 a (List.mem_append_right _ ha)
  · exact hΓ a ha

def Wire.conflictFreeCheckX (U : UDoc) (X : List VE.Formula)
    (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (targets (fill U)).length == certs.length &&
    ((targets (fill U)).zip certs).all (fun (t, c) => match c with
      | some c => VE.Tableau.checkCertificate (envAt (fill U) 0)
          (backgroundBase (fill U) ++ X ++ fillPremises U) (targetConclusion t) c
      | none => false)

theorem Wire.conflictFreeCheckX_nil (U : UDoc) (certs : List (Option VE.Tableau.Certificate)) :
    Wire.conflictFreeCheckX U [] certs = Wire.conflictFreeCheckU U certs := by
  simp [Wire.conflictFreeCheckX, Wire.conflictFreeCheckU, Wire.baseBackgroundU]
  rfl

theorem Wire.conflictFreeCheckX_sound (U : UDoc) (h : WellFormed (fill U) = true) (X : List VE.Formula)
    (certs : List (Option VE.Tableau.Certificate)) (hc : Wire.conflictFreeCheckX U X certs = true) :
    Wire.ConflictFreeX.{u} U X := by
  have hv := valid_of_wellFormed _ h
  intro B hB
  have hcert : ∀ t ∈ targets (fill U), ∀ vs : List B.Carrier,
      VE.TupleTyped B t.2.1 vs → ¬ t.2.2.denote B (tupleVal vs) := by
    intro t ht vs hvs
    simp only [Wire.conflictFreeCheckX, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
    obtain ⟨hl, hall⟩ := hc
    obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp ht
    have hlt : i < (targets (fill U)).length := (List.getElem?_eq_some_iff.mp hi).1
    have hlt' : i < certs.length := hl ▸ hlt
    have hmem : (t, certs[i]) ∈ (targets (fill U)).zip certs := by
      apply List.mem_iff_getElem?.mpr
      refine ⟨i, ?_⟩
      rw [List.getElem?_zip_eq_some]
      exact ⟨hi, List.getElem?_eq_getElem hlt'⟩
    have hc' := hall _ hmem
    cases hci : certs[i] with
    | none => rw [hci] at hc'; cases hc'
    | some c =>
      rw [hci] at hc'
      have he := VE.Tableau.checkCertificate_sound.{u} _ _ _ c hc' B hB.1.1.1 (fun a ha => by
        rcases List.mem_append.mp ha with ha | ha
        · rcases List.mem_append.mp ha with ha | ha
          · exact hB.1.1.2 a ha
          · exact hB.2 a ha
        · exact hB.1.2 a ha)
      exact (bindAll_denote_nil B _ _).mp he vs hvs
  refine ⟨fun r hr vs hvs => ?_, fun pr hpr vs hvs => ?_⟩
  · exact hcert _ (List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩)) vs hvs
  · exact hcert _ (List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)) vs hvs

def modelCheckX (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : FiniteFill U VE.Bridge.Entity) (Γ : List VE.Formula) (φ : VE.Formula) : Bool × Bool :=
  ((modelCheckU U M F Γ φ).1 && Wire.extraValid U X M F, (modelCheckU U M F Γ φ).2)

theorem modelCheckX_nil (U : UDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : FiniteFill U VE.Bridge.Entity) (Γ : List VE.Formula) (φ : VE.Formula) :
    modelCheckX U [] M F Γ φ = modelCheckU U M F Γ φ := by
  simp [modelCheckX, Wire.extraValid]

theorem modelCheckX_sound (U : UDoc) (h : WellFormedU U = true) (X : List VE.Formula)
    (M : VE.FiniteModel VE.Bridge.Entity) (valid : M.Valid (envAt U.D 0))
    (F : FiniteFill U VE.Bridge.Entity) (Γ : List VE.Formula) (φ : VE.Formula)
    (hm : (modelCheckX U X M F Γ φ).1 = true) :
    Wire.BaseAdmissibleX U X (withFill U M.asStructure (finFill M F)) ∧
    (∀ a ∈ Γ, (subst (fill U).T (size (fill U)) a).denote
      (withFill U M.asStructure (finFill M F)) []) ∧
    ((subst (fill U).T (size (fill U)) φ).denote
      (withFill U M.asStructure (finFill M F)) [] ↔
      (modelCheckX U X M F Γ φ).2 = true) := by
  simp only [modelCheckX, Bool.and_eq_true] at hm
  have hm' : (modelCheckU U M F Γ φ).1 = true := hm.1
  have hX : Wire.extraValid U X M F = true := hm.2
  obtain ⟨hB, hΓ, hφ⟩ := modelCheckU_sound U h M valid F Γ φ hm'
  exact ⟨⟨hB, fun a ha => (eval_withFill U M F a []).mp (List.all_eq_true.mp hX a ha)⟩, hΓ, hφ⟩
/-! ## `X` is a list of closed base formulas of `E‴` -/

/-- `selects_wellFormed` for a rule typed by its own guard and carve-outs, whether or not the tree holds it. -/
theorem selects_wellFormed_of {T : Tree} {E : VE.Environment} {Γ : List String} {p : String}
    (hT : RulesTyped T E Γ p) (f : Nat) (M : Node)
    (hM : M.guard.WellFormed E Γ ∧ ∀ C ∈ M.carveOuts, C.WellFormed E Γ) (hp : M.pred = p) :
    (selects T f M).WellFormed E Γ := by
  refine ⟨applies_wellFormed hM, anyF_wellFormed E Γ _ ?_⟩
  intro a ha
  obtain ⟨C, hC, rfl⟩ := List.mem_map.mp ha
  obtain ⟨hC, hCp⟩ := mem_children hC
  exact yields_wellFormed hT f C hC (hCp.trans hp)

/-- A soft rule's selection regenerated on the filled tree is a base formula over its act's sorts. -/
theorem fillSelects_wellFormed (D : VE.SoftNorms.SoftDoc) (unspec : List String)
    (hs : VE.SoftNorms.WellFormedSoft D = true) (hw : WellFormedU ⟨VE.SoftNorms.soften D, unspec⟩ = true)
    (K : VE.SoftNorms.SoftNode) (hK : K ∈ D.T.nodes) :
    (subst (fill ⟨VE.SoftNorms.soften D, unspec⟩).T (size (fill ⟨VE.SoftNorms.soften D, unspec⟩))
      (selects (fill ⟨VE.SoftNorms.soften D, unspec⟩).T (fuel (fill ⟨VE.SoftNorms.soften D, unspec⟩).T)
        (VE.SoftNorms.primeNode D K))).WellFormed (envAt (fill ⟨VE.SoftNorms.soften D, unspec⟩) 0)
      (VE.SoftNorms.sortsOf D K.pred).reverse ∧
    ∀ s ∈ VE.SoftNorms.sortsOf D K.pred, s ∈ (envAt (fill ⟨VE.SoftNorms.soften D, unspec⟩) 0).sorts := by
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ hs
  have hv : Valid (fill ⟨VE.SoftNorms.soften D, unspec⟩) := valid_of_wellFormed _ (fill_wellFormed _ hw)
  obtain ⟨n, hn, hnK⟩ := List.mem_map.mp (hsv.predReg K hK)
  obtain ⟨r, hr⟩ : ∃ r, D.T.regulated.find? (·.name == K.pred) = some r :=
    Option.isSome_iff_exists.mp (List.find?_isSome.mpr ⟨n, hn, by simpa using hnK⟩)
  have hrm : r ∈ (fill ⟨VE.SoftNorms.soften D, unspec⟩).T.regulated := List.mem_of_find?_eq_some hr
  have hrn : r.name = K.pred := by simpa using List.find?_some hr
  have hso : VE.SoftNorms.sortsOf D K.pred = r.sorts := by
    simp [VE.SoftNorms.sortsOf, VE.SoftNorms.sortsIn, hr]
  have hk := index_before hv hrm
  have hT := rulesTyped_of_valid hv hk
  have hpn : fillRoot ⟨VE.SoftNorms.soften D, unspec⟩ (VE.SoftNorms.primeNode D K) ∈
      (fill ⟨VE.SoftNorms.soften D, unspec⟩).T.nodes :=
    mem_fill_nodes.mpr (Or.inl ⟨_, List.mem_map_of_mem hK, rfl⟩)
  have hg := hT _ hpn (by rw [fillRoot_pred, hrn]; rfl)
  rw [fillRoot_guard, fillRoot_carveOuts] at hg
  have h1 := selects_wellFormed_of hT (fuel (fill ⟨VE.SoftNorms.soften D, unspec⟩).T) _ hg (by rw [hrn]; rfl)
  have hle : before (fill ⟨VE.SoftNorms.soften D, unspec⟩) r.name ≤ size (fill ⟨VE.SoftNorms.soften D, unspec⟩) :=
    Nat.le_of_lt (List.getElem?_eq_some_iff.mp hk).1
  rw [hso]
  exact ⟨subst_wellFormed hv _ _ _ (envAt_mono hle _ _ h1), (hv.decl _ (List.mem_of_getElem? hk)).2.2⟩

/-- Soft's premises regenerated on the filled tree (`Exc_T`, then `Coh_T` read on `fill U`) are closed base formulas
    of `E‴`: `Exc_T` is typed over `E′` (`WellFormedSoft`), whose declarations `E‴` keeps, and each coherence
    premise's selections are typed by the filled tree's rules. -/
theorem Wire.softLabelledU_wellFormed (D : VE.SoftNorms.SoftDoc) (unspec : List String)
    (hs : VE.SoftNorms.WellFormedSoft D = true) (hw : WellFormedU ⟨VE.SoftNorms.soften D, unspec⟩ = true) :
    ∀ a ∈ (Wire.softLabelledU ⟨VE.SoftNorms.soften D, unspec⟩ D).map (·.2),
      a.WellFormed (envAt (fill ⟨VE.SoftNorms.soften D, unspec⟩) 0) [] := by
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ hs
  intro a ha
  obtain ⟨⟨l, a⟩, hla, rfl⟩ := List.mem_map.mp ha
  rcases List.mem_append.mp hla with he | hc
  · have hea : a ∈ VE.SoftNorms.excPremises D := (List.of_mem_zip he).2
    exact wf_mono (E := envAt (VE.SoftNorms.soften D) 0) (E' := envAt (fill ⟨VE.SoftNorms.soften D, unspec⟩) 0)
      rfl rfl (envAt_fill_mono (uvalid hw) 0) a [] (hsv.premTyped a (List.mem_append_left _ hea))
  · obtain ⟨⟨M, K⟩, hMK, he⟩ := List.mem_map.mp hc
    cases he
    obtain ⟨hM, hK, -, -, -, -⟩ := VE.SoftNorms.mem_collidingPairs.mp hMK
    have hMs := fillSelects_wellFormed D unspec hs hw M hM
    have hKs := fillSelects_wellFormed D unspec hs hw K hK
    rw [← hsv.cpSorts _ hMK] at hKs
    apply bindAll_wellFormed hMs.2 [] _
    simp only [List.append_nil]
    exact ⟨hMs.1, hKs.1⟩
end VE.NormDefaults

namespace VE.NormDefaults.Wire
open Lean
open VE.Norms

/-- Bind a certificate to the source environment and all regenerated premises. -/
def bindCertX (environment : Json) (U : UDoc) (X A : List VE.Formula) (own : List Json)
    (conclusion : Json) (j : Json) : Except String VE.Tableau.Certificate := do
  let cert ← VE.CertificateWire.decodeCertificate j
  VE.Route.Wire.bindingOk (profilesOf environment) (← canonicalEnvironmentJsonU environment)
    ((premisesX U X A).map enc ++ own) conclusion cert.environment_id cert.premise_meaning_ids
    cert.conclusion_meaning_id
  pure cert
end VE.NormDefaults.Wire
