import VE.Alternatives.Background

/-! The route restated with `BaseAdmissibleAlt` and `backgroundAlt`
(docs/spec/alternatives.md 7.2, the soft-norms 9.3 shape). The slot premises
are new base premises, so W1's document-wide theorems are restated over
`BaseAdmissibleAlt`; every per-structure lemma (`local_expands`,
`conflictFreeAt_of_base`, `prefix_char`, `sat_document`, …) is W1's on the
inlined document. The route is W1's chain of layers over `inlineTree A` with
the slot premises added to each prefix's admissibility (`PrefixAdmissibleAlt`). -/
namespace VE.Alternatives
open VE.Norms
open VE.Route (Unique)
universe u

/-- The prefix characterisation over the extended base (W1's `prefix_satisfaction`). -/
theorem alt_prefix_satisfaction (A : AltDoc) (h : WellFormedAlt A = true) (i : Nat)
    (hi : i ≤ size (inlineTree A)) (S : VE.Structure.{u}) :
    PrefixAdmissibleAlt A i S ↔ S.Admissible (envAt (inlineTree A) i) ∧
      BaseAdmissibleAlt A (restrictAll (inlineTree A).T S) ∧ Sat S (PrefixPremises (inlineTree A) i) := by
  rw [PrefixAdmissibleAlt, prefix_satisfaction _ (alternatives_wellFormed A h) i hi S]
  constructor
  · rintro ⟨⟨h1, h2, h3⟩, h4⟩
    exact ⟨h1, ⟨h2, h4⟩, h3⟩
  · rintro ⟨h1, ⟨h2, h4⟩, h3⟩
    exact ⟨⟨h1, h2, h3⟩, h4⟩

/-- Conflict-freedom over the extended bases gives W1's local test at every regulated predicate. -/
theorem alt_conflictFree_prefix (A : AltDoc) (h : WellFormedAlt A = true) (r : Regulated)
    (hr : r ∈ (inlineTree A).T.regulated) (hc : AltConflictFree.{u} A) (S₀ : VE.Structure.{u})
    (h₀ : PrefixAdmissibleAlt A (before (inlineTree A) r.name) S₀) :
    ConflictFreeAt (inlineTree A) r.name S₀ := by
  have hv := valid_of_wellFormed _ (alternatives_wellFormed A h)
  obtain ⟨k, hk⟩ := mem_syms_index (hv.regulated r hr)
  have hb : before (inlineTree A) r.name = k := before_eq hv hk
  unfold ConflictFreeAt
  rw [hb] at h₀ ⊢
  have hB := ((prefix_char hv k (prefixAdmissible_le h₀.1) S₀).mp h₀.1).2.1
  exact conflictFreeAt_of_base hv hk S₀ h₀.1 (hc _ ⟨hB, h₀.2⟩)

section AltLayer
variable {A : AltDoc} (hv : Valid (inlineTree A)) {k : Nat} {q : Sym}
  (hk : (syms (inlineTree A).T)[k]? = some q)
include hk

theorem alt_restrict_admissible (S : VE.Structure.{u}) (h : PrefixAdmissibleAlt A (k + 1) S) :
    PrefixAdmissibleAlt A k (forget [q.name] S) := by
  have h1 := h.1
  simp only [PrefixAdmissible, hk] at h1
  refine ⟨h1.2.1, ?_⟩
  rw [restrictAll_forget (name_mem_layerNames hk)]
  exact h.2

include hv in
theorem alt_layer_expands
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissibleAlt A k S₀ → ConflictFreeAtIdx (inlineTree A) k S₀)
    (S₀ : VE.Structure.{u}) (h₀ : PrefixAdmissibleAlt A k S₀) :
    Unique fun S => forget [q.name] S = S₀ ∧ PrefixAdmissibleAlt A (k + 1) S ∧
      ∀ a ∈ symPremises (inlineTree A).T q, a.denote S [] := by
  have := (local_expands hv hk S₀ h₀.1).mpr (hc S₀ h₀)
  refine (unique_congr fun S => ?_).mp this
  constructor
  · rintro ⟨h₁, h₂⟩
    refine ⟨h₁, ⟨h₂, ?_⟩, symPremises_sat hv hk S h₂⟩
    rw [← restrictAll_forget (name_mem_layerNames hk) S, h₁]
    exact h₀.2
  · rintro ⟨h₁, h₂, _⟩
    exact ⟨h₁, h₂.1⟩

end AltLayer

/-- The alternatives layer of the `k`-th layer symbol of the inlined document. -/
def altSymLayer (A : AltDoc) (hv : Valid (inlineTree A)) (k : Nat) (q : Sym)
    (hk : (syms (inlineTree A).T)[k]? = some q)
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissibleAlt A k S₀ → ConflictFreeAtIdx (inlineTree A) k S₀) :
    VE.Route.Layer VE.Route.fol.{u} Unit where
  E_in := envAt (inlineTree A) k
  E_out := envAt (inlineTree A) (k + 1)
  extends_env a h := envAt_mono (Nat.le_succ k) a [] h
  premises _ := symPremises (inlineTree A).T q
  premises_wellFormed _ := symPremises_wellFormed hv hk
  Admissible_in := PrefixAdmissibleAlt A k
  Admissible_out := PrefixAdmissibleAlt A (k + 1)
  admissible_out _ h := prefixAdmissible_admissible h.1
  restrict := forget [q.name]
  restrict_admissible S h := alt_restrict_admissible hk S h
  restrict_holds S a _ ha := denote_forget (self_hidden hv hk) S a [] [] ha
  Intended _ S := LayerMeaning (inlineTree A).T S q
  faithful _ S h := symLayer_faithful hv hk S h.1
  expands _ S₀ h₀ := alt_layer_expands hv hk hc S₀ h₀

/-- A composed prefix of the alternatives route. -/
structure AltChain (A : AltDoc) (k : Nat) where
  R : VE.Route.Layer VE.Route.fol.{u} Unit
  E_in : R.E_in = envAt (inlineTree A) 0
  E_out : R.E_out = envAt (inlineTree A) k
  A_in : ∀ S, R.Admissible_in S ↔ PrefixAdmissibleAlt A 0 S
  A_out : ∀ S, R.Admissible_out S ↔ PrefixAdmissibleAlt A k S
  restrict : ∀ S, R.restrict S = forget ((layerNames (inlineTree A).T).take k) S
  premises : ∀ d, R.premises d = ((syms (inlineTree A).T).take k).flatMap (symPremises (inlineTree A).T)

def altChain (A : AltDoc) (hv : Valid (inlineTree A))
    (hc : ∀ k (S₀ : VE.Structure.{u}), PrefixAdmissibleAlt A k S₀ → ConflictFreeAtIdx (inlineTree A) k S₀) :
    (k : Nat) → k ≤ size (inlineTree A) → AltChain.{u} A k
  | 0, _ =>
    { R := VE.Route.Layer.id (envAt (inlineTree A) 0) (PrefixAdmissibleAlt A 0) (fun _ h => h.1.1)
      E_in := rfl
      E_out := rfl
      A_in := fun _ => Iff.rfl
      A_out := fun _ => Iff.rfl
      restrict := fun S => by simp [VE.Route.Layer.id, forget_nil]
      premises := fun _ => by simp [VE.Route.Layer.id] }
  | k + 1, hk =>
    let C := altChain A hv hc k (Nat.le_of_succ_le hk)
    have hlt : k < (syms (inlineTree A).T).length := hk
    let q := (syms (inlineTree A).T)[k]
    have hq : (syms (inlineTree A).T)[k]? = some q := List.getElem?_eq_getElem hlt
    let L := altSymLayer A hv k q hq (hc k)
    { R := VE.Route.Layer.comp C.R L C.E_out.symm (fun S => (C.A_out S).symm)
      E_in := C.E_in
      E_out := rfl
      A_in := C.A_in
      A_out := fun _ => Iff.rfl
      restrict := fun S => by
        show C.R.restrict (forget [q.name] S) = _
        rw [C.restrict, forget_forget, List.take_succ, names_getElemOpt hq]
        rfl
      premises := fun d => by
        simp only [VE.Route.Layer.comp]
        rw [C.premises, List.take_succ, hq]
        simp [L, altSymLayer] }

theorem prefixAdmissibleAlt_zero (A : AltDoc) (B : VE.Structure.{u}) :
    PrefixAdmissibleAlt A 0 B ↔ BaseAdmissibleAlt A B := by
  constructor
  · rintro ⟨hB, hs⟩
    refine ⟨hB, ?_⟩
    rw [restrictAll_self B hB.1] at hs
    exact hs
  · rintro ⟨hB, hs⟩
    refine ⟨hB, ?_⟩
    rw [restrictAll_self B hB.1]
    exact hs

/-- Conflict-freedom over the extended bases gives every layer's hypothesis. -/
theorem altChain_hc {A : AltDoc} (hv : Valid (inlineTree A)) (hc : AltConflictFree.{u} A) :
    ∀ k (S₀ : VE.Structure.{u}), PrefixAdmissibleAlt A k S₀ → ConflictFreeAtIdx (inlineTree A) k S₀ := by
  intro k S₀ h₀
  cases hk : (syms (inlineTree A).T)[k]? with
  | none => simp [ConflictFreeAtIdx, hk]
  | some q =>
    have hB := ((prefix_char hv k (prefixAdmissible_le h₀.1) S₀).mp h₀.1).2.1
    exact conflictFreeAt_of_base hv hk S₀ h₀.1 (hc _ ⟨hB, h₀.2⟩)

def altRouteChain (A : AltDoc) (h : WellFormedAlt A = true) (hc : AltConflictFree.{u} A) :
    AltChain.{u} A (size (inlineTree A)) :=
  altChain A (valid_of_wellFormed _ (alternatives_wellFormed A h))
    (altChain_hc (valid_of_wellFormed _ (alternatives_wellFormed A h)) hc) _ (Nat.le_refl _)

theorem altRouteChain_premises (A : AltDoc) (h : WellFormedAlt A = true) (hc : AltConflictFree.{u} A)
    (d : Unit) : (altRouteChain A h hc).R.premises d = elaborate (inlineTree A).T := by
  rw [(altRouteChain A h hc).premises, elaborate_eq_flatMap]
  simp [size]

theorem altRouteChain_restrict (A : AltDoc) (h : WellFormedAlt A = true) (hc : AltConflictFree.{u} A)
    (S : VE.Structure.{u}) : (altRouteChain A h hc).R.restrict S = restrictAll (inlineTree A).T S := by
  rw [(altRouteChain A h hc).restrict, List.take_of_length_le (by simp [size, layerNames])]
  rfl

/-- The alternatives route: the composed frozen P0 layers of the inlined document with
`BaseAdmissibleAlt` as input admissibility. -/
def altRoute (A : AltDoc) (h : WellFormedAlt A = true) (hc : AltConflictFree.{u} A) :
    { R : VE.Route.Layer VE.Route.fol.{u} Unit // R.E_in = envAt (inlineTree A) 0 ∧
      (∀ B, R.Admissible_in B ↔ BaseAdmissibleAlt A B) ∧
      R.E_out = envAt (inlineTree A) (size (inlineTree A)) ∧ R.premises () = elaborate (inlineTree A).T } :=
  ⟨(altRouteChain A h hc).R, (altRouteChain A h hc).E_in,
    fun B => ((altRouteChain A h hc).A_in B).trans (prefixAdmissibleAlt_zero A B),
    (altRouteChain A h hc).E_out, altRouteChain_premises A h hc ()⟩

theorem alt_route_backgroundSound (A : AltDoc) (h : WellFormedAlt A = true) (hc : AltConflictFree.{u} A) :
    VE.Route.BackgroundSound (altRoute A h hc).1 (backgroundAlt A) := by
  have hav := altValid_of_wellFormed A h
  have hv := valid_of_wellFormed _ hav.wf
  intro d S hS _
  have hpa := ((altRouteChain A h hc).A_out S).mp hS
  obtain ⟨_, hB, hM, hP⟩ := (prefix_char hv _ (Nat.le_refl _) S).mp hpa.1
  have hdoc := (sat_document hv S).mpr ⟨(sat_literals_forget _ _ S).mp hB.2, hM, hP⟩
  have hslot := (sat_altPremises_restrict hav S).mp hpa.2
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact hdoc a (List.mem_append_left _ ha)
  · exact hslot a ha

theorem alt_route_backgroundComplete (A : AltDoc) (h : WellFormedAlt A = true) (hc : AltConflictFree.{u} A) :
    VE.Route.BackgroundComplete (altRoute A h hc).1 (backgroundAlt A) := by
  have hav := altValid_of_wellFormed A h
  have hv := valid_of_wellFormed _ hav.wf
  intro d S hA hbg hprem
  have hA' : S.Admissible (envAt (inlineTree A) (size (inlineTree A))) := by
    have := (altRouteChain A h hc).E_out
    simp only [VE.Route.fol] at hA
    rw [show (altRoute A h hc).1 = (altRouteChain A h hc).R from rfl, this] at hA
    exact hA
  have hprem' : Sat S (elaborate (inlineTree A).T) := by
    have := altRouteChain_premises A h hc d
    intro a ha
    exact hprem a (by show a ∈ (altRouteChain A h hc).R.premises d; rw [this]; exact ha)
  have hsat : Sat S (background (inlineTree A) ++ elaborate (inlineTree A).T) := fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · exact hbg a (List.mem_append_left _ ha)
    · exact hprem' a ha
  obtain ⟨hl, hM, hP⟩ := (sat_document hv S).mp hsat
  apply ((altRouteChain A h hc).A_out S).mpr
  refine ⟨(prefix_char hv _ (Nat.le_refl _) S).mpr
    ⟨hA', ⟨restrictAll_admissible _ S hA', (sat_literals_forget _ _ S).mpr hl⟩, hM, hP⟩, ?_⟩
  exact (sat_altPremises_restrict hav S).mpr (fun a ha => hbg a (List.mem_append_right _ ha))

/-- The first half of `alt_route_acceptance`, which needs no conflict-freedom. -/
theorem alt_route_intended (A : AltDoc) (h : WellFormedAlt A = true)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (inlineTree A) (size (inlineTree A)))
                  (backgroundAlt A ++ elaborate (inlineTree A).T ++ Γ) φ c = true)
    (S : VE.Structure.{u}) (hS : S.Admissible (envAt (inlineTree A) (size (inlineTree A))))
    (hcat : VE.Norms.holdsCatala (inlineTree A).T S) (hdef : VE.Norms.definitionsHold (inlineTree A) S)
    (hprof : VE.Norms.profileHold (inlineTree A) S) (hbase : Sat S (backgroundBase (inlineTree A)))
    (hslot : Sat S (altPremises A)) (hΓ : Sat S Γ) :
    φ.denote S [] := by
  apply VE.Tableau.checkCertificate_sound.{u} _ _ _ c accepted S hS
  intro a ha
  simp only [List.mem_append, backgroundAlt, background] at ha
  rcases ha with (((((ha | ha) | ha) | ha) | ha) | ha)
  · exact hdef a ha
  · exact hbase a ha
  · exact hprof a ha
  · exact hslot a ha
  · exact (elaborate_iff _ (alternatives_wellFormed A h) S).mpr hcat a ha
  · exact hΓ a ha

/-- W1's acceptance restated with `BaseAdmissibleAlt` and `backgroundAlt`. -/
theorem alt_route_acceptance (A : AltDoc) (h : WellFormedAlt A = true) (hc : AltConflictFree.{u} A)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (inlineTree A) (size (inlineTree A)))
                  (backgroundAlt A ++ elaborate (inlineTree A).T ++ Γ) φ c = true) :
    (∀ S : VE.Structure.{u}, S.Admissible (envAt (inlineTree A) (size (inlineTree A))) →
       VE.Norms.holdsCatala (inlineTree A).T S → VE.Norms.definitionsHold (inlineTree A) S →
       VE.Norms.profileHold (inlineTree A) S → Sat S (backgroundBase (inlineTree A)) →
       Sat S (altPremises A) → Sat S Γ → φ.denote S []) ∧
    ((∀ a ∈ Γ, a.WellFormed (envAt (inlineTree A) 0) []) → φ.WellFormed (envAt (inlineTree A) 0) [] →
       ∀ B : VE.Structure.{u}, BaseAdmissibleAlt A B → Sat B Γ → φ.denote B []) := by
  refine ⟨fun S hS hcat hdef hprof hbase hslot hΓ =>
    alt_route_intended A h Γ φ c accepted S hS hcat hdef hprof hbase hslot hΓ, fun hΓ hφ => ?_⟩
  let R := altRoute A h hc
  have hacc : (VE.Route.Checker.tableau R.1.E_out).valid c
      (VE.Route.checkedPremises R.1 (backgroundAlt A) () Γ) φ := by
    show VE.Tableau.checkCertificate R.1.E_out _ φ c = true
    rw [R.2.2.2.1, VE.Route.checkedPremises, R.2.2.2.2]
    exact accepted
  have := VE.Route.route_acceptance R.1 (backgroundAlt A) (alt_route_backgroundSound A h hc)
    (VE.Route.Checker.tableau R.1.E_out) () Γ φ c _ φ hacc (List.map_id _) rfl
  intro B hB hs
  exact this.2.2 (by rw [R.2.1]; exact hΓ) (by rw [R.2.1]; exact hφ) B ((R.2.2.1 B).mpr hB) hs

/-- W1's countermodel theorem restated. -/
theorem alt_route_countermodel (A : AltDoc) (h : WellFormedAlt A = true) (hc : AltConflictFree.{u} A)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (inlineTree A) 0) []) (hφ : φ.WellFormed (envAt (inlineTree A) 0) [])
    (B : VE.Structure.{u}) (hB : BaseAdmissibleAlt A B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
    ∃ S, DocumentExpansion (inlineTree A) B S ∧ Sat S (altPremises A) ∧ Sat S Γ ∧ ¬ φ.denote S [] := by
  let R := altRoute A h hc
  obtain ⟨S, hr, hA, hsat, hno⟩ := VE.Route.route_countermodel_expands R.1 (backgroundAlt A)
    (alt_route_backgroundSound A h hc) () Γ φ (by rw [R.2.1]; exact hΓ) (by rw [R.2.1]; exact hφ)
    B ((R.2.2.1 B).mpr hB) hs hn
  obtain ⟨hbg, hp, hg⟩ := (VE.Route.sat_checked R.1 (backgroundAlt A) S () Γ).mp hsat
  have hp' : Sat S (elaborate (inlineTree A).T) := by
    intro a ha
    exact hp a (by show a ∈ R.1.premises (); rw [R.2.2.2.2]; exact ha)
  refine ⟨S, ⟨by rw [← altRouteChain_restrict A h hc]; exact hr,
    prefixAdmissible_admissible (((altRouteChain A h hc).A_out S).mp hA).1, fun a ha => ?_⟩,
    fun a ha => hbg a (List.mem_append_right _ ha), hg, hno⟩
  rcases List.mem_append.mp ha with ha | ha
  · exact hbg a (List.mem_append_left _ ha)
  · exact hp' a ha

end VE.Alternatives
