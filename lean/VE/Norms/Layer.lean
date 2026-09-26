import VE.Norms.Conflict

/-! The P0 route instances (docs/spec/norms.md 6.2): one frozen `VE.Route.Layer`
per layer symbol, their composition with the frozen `Layer.comp`, and the
route acceptance and countermodel theorems obtained from the frozen
`route_acceptance` and `route_countermodel_expands`.

A regulated predicate's layer has the premise `elab_p`, meaning `IntendedAt`
(faithfulness is `elab_iff_intended`, independent of output admissibility) and
`expands` from `local_expands` under the layer's hypothesis `hc`. A definition's
biconditional sits in Background's `definitions` slice (P0 generator order,
W3's convention), so its layer contributes no premise; its meaning is part of
its output admissibility, as the W3 interface requirement of 6.1 demands. Every
layer's output admissibility is `PrefixAdmissible D (k+1)`, the input of the
next, so consecutive layers compose by construction. -/
namespace VE.Norms
open VE.Route
universe u

/-- The premises a layer symbol contributes on the route. -/
def symPremises (T : Tree) : Sym → List VE.Formula
  | .reg r => [elabPremise T r]
  | .defn _ => []

theorem flatMap_symPremises (T : Tree) (l : List Sym) :
    l.flatMap (symPremises T) = l.filterMap (fun | .reg r => some (elabPremise T r) | .defn _ => none) := by
  induction l with
  | nil => rfl
  | cons q l ih => cases q <;> simp [symPremises, ih]

theorem elaborate_eq_flatMap (T : Tree) : elaborate T = (syms T).flatMap (symPremises T) :=
  (flatMap_symPremises T (syms T)).symm

section Sym
variable {D : Doc} (hv : Valid D) {k : Nat} {q : Sym} (hk : (syms D.T)[k]? = some q)
include hv hk

theorem symPremises_wellFormed : ∀ a ∈ symPremises D.T q, a.WellFormed (envAt D (k + 1)) [] := by
  cases q with
  | defn _ => intro a ha; cases ha
  | reg r =>
    intro a ha
    rw [symPremises, List.mem_singleton] at ha
    subst ha
    have hd := hv.decl _ (List.mem_of_getElem? hk)
    refine elab_wellFormed (fun N hN hp => ?_) hd.2.1 (envAt_earlier hv hk (Nat.lt_succ_self k)) hd.2.2
    obtain ⟨hg, hu⟩ := rulesTyped_of_valid hv hk N hN hp
    exact ⟨envAt_mono (Nat.le_succ k) _ _ hg, fun U hU => envAt_mono (Nat.le_succ k) _ _ (hu U hU)⟩

theorem symPremises_sat (S : VE.Structure.{u}) (h : PrefixAdmissible D (k + 1) S) :
    ∀ a ∈ symPremises D.T q, a.denote S [] := by
  simp only [PrefixAdmissible, hk] at h
  have hM := (layerMeaning_iff hv hk S).mp h.2.2.1
  cases q with
  | defn _ => intro a ha; cases ha
  | reg r =>
    intro a ha
    rw [symPremises, List.mem_singleton] at ha
    subst ha
    exact (elabPremise_iff_meaning D.T r (sym_arity hv hk) S).mpr hM

theorem symLayer_faithful (S : VE.Structure.{u}) (h : PrefixAdmissible D (k + 1) S) :
    (∀ a ∈ symPremises D.T q, a.denote S []) ↔ LayerMeaning D.T S q := by
  cases q with
  | reg r =>
    simp only [symPremises, List.mem_singleton, forall_eq, LayerMeaning]
    exact elab_iff_intended D.T r (sym_arity hv hk) S
      (decides_forget hv hk [r.name] (self_hidden hv hk) S)
  | defn d =>
    simp only [PrefixAdmissible, hk] at h
    exact ⟨fun _ => h.2.2.1, fun _ a ha => by cases ha⟩

theorem symLayer_expands (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissible D k S₀ → ConflictFreeAtIdx D k S₀)
    (S₀ : VE.Structure.{u}) (h₀ : PrefixAdmissible D k S₀) :
    Unique fun S => forget [q.name] S = S₀ ∧ PrefixAdmissible D (k + 1) S ∧
      ∀ a ∈ symPremises D.T q, a.denote S [] := by
  have := (local_expands hv hk S₀ h₀).mpr (hc S₀ h₀)
  refine (unique_congr fun S => ?_).mp this
  exact ⟨fun ⟨h₁, h₂⟩ => ⟨h₁, h₂, symPremises_sat hv hk S h₂⟩, fun ⟨h₁, h₂, _⟩ => ⟨h₁, h₂⟩⟩

end Sym

/-- The layer of the `k`-th layer symbol: a frozen P0 `Layer` for FOL, available
exactly when every admissible prefix input passes the local test. -/
def symLayer (D : Doc) (hv : Valid D) (k : Nat) (q : Sym) (hk : (syms D.T)[k]? = some q)
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissible D k S₀ → ConflictFreeAtIdx D k S₀) :
    Layer fol.{u} Unit where
  E_in := envAt D k
  E_out := envAt D (k + 1)
  extends_env a h := envAt_mono (Nat.le_succ k) a [] h
  premises _ := symPremises D.T q
  premises_wellFormed _ := symPremises_wellFormed hv hk
  Admissible_in := PrefixAdmissible D k
  Admissible_out := PrefixAdmissible D (k + 1)
  admissible_out _ h := prefixAdmissible_admissible h
  restrict := forget [q.name]
  restrict_admissible S h := by
    simp only [PrefixAdmissible, hk] at h
    exact h.2.1
  restrict_holds S a _ ha := denote_forget (self_hidden hv hk) S a [] [] ha
  Intended _ S := LayerMeaning D.T S q
  faithful _ S h := symLayer_faithful hv hk S h
  expands _ S₀ h₀ := symLayer_expands hv hk hc S₀ h₀

theorem index_before {D : Doc} (hv : Valid D) {r : Regulated} (hr : r ∈ D.T.regulated) :
    (syms D.T)[before D r.name]? = some (.reg r) := by
  obtain ⟨k, hk⟩ := mem_syms_index (hv.regulated r hr)
  have hb : before D r.name = k := before_eq hv hk
  rw [hb]; exact hk

/-- `layer`: the P0 instance of a regulated predicate `p`, given its `hc`.
`E_in = E_(before p)`, `E_out = E_(before p + 1)`, premises `[elab T p]`,
`Admissible_in = PrefixAdmissible (before p)`, `Admissible_out` is `AdmissibleOut`
(prefix admissibility including the current elaboration), `restrict = forget p`,
`Intended = IntendedAt T p`, `faithful` by `elab_iff_intended` and `expands` by
`conflictFree_expands` under `hc`. -/
def layer (D : Doc) (h : WellFormed D = true) (r : Regulated) (hr : r ∈ D.T.regulated)
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissible D (before D r.name) S₀ → ConflictFreeAt D r.name S₀) :
    Layer fol.{u} Unit :=
  symLayer D (valid_of_wellFormed D h) (before D r.name) (.reg r)
    (index_before (valid_of_wellFormed D h) hr) hc

theorem layer_premises (D : Doc) (h : WellFormed D = true) (r : Regulated) (hr : r ∈ D.T.regulated)
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissible D (before D r.name) S₀ → ConflictFreeAt D r.name S₀) :
    (layer D h r hr hc).premises () = [elabPremise D.T r] := rfl

theorem layer_intended (D : Doc) (h : WellFormed D = true) (r : Regulated) (hr : r ∈ D.T.regulated)
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissible D (before D r.name) S₀ → ConflictFreeAt D r.name S₀)
    (S : VE.Structure.{u}) : (layer D h r hr hc).Intended () S ↔ IntendedAt D.T r S := Iff.rfl

theorem layer_admissible_out (D : Doc) (h : WellFormed D = true) (r : Regulated) (hr : r ∈ D.T.regulated)
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissible D (before D r.name) S₀ → ConflictFreeAt D r.name S₀)
    (S : VE.Structure.{u}) : (layer D h r hr hc).Admissible_out S ↔ AdmissibleOut D r.name S := Iff.rfl

/-! ## The composed route -/

/-- A composed prefix of the route with the facts the next composition step and
the route theorems need. -/
structure Chain (D : Doc) (k : Nat) where
  R : Layer fol.{u} Unit
  E_in : R.E_in = envAt D 0
  E_out : R.E_out = envAt D k
  A_in : ∀ S, R.Admissible_in S ↔ PrefixAdmissible D 0 S
  A_out : ∀ S, R.Admissible_out S ↔ PrefixAdmissible D k S
  restrict : ∀ S, R.restrict S = forget ((layerNames D.T).take k) S
  premises : ∀ d, R.premises d = ((syms D.T).take k).flatMap (symPremises D.T)

/-- The layers `0 … k-1` composed innermost first with the frozen `Layer.comp`,
given every layer's local hypothesis. -/
def chain (D : Doc) (hv : Valid D)
    (hc : ∀ k (S₀ : VE.Structure.{u}), PrefixAdmissible D k S₀ → ConflictFreeAtIdx D k S₀) :
    (k : Nat) → k ≤ size D → Chain.{u} D k
  | 0, _ =>
    { R := Layer.id (envAt D 0) (PrefixAdmissible D 0) (fun _ h => h.1)
      E_in := rfl
      E_out := rfl
      A_in := fun _ => Iff.rfl
      A_out := fun _ => Iff.rfl
      restrict := fun S => by simp [Layer.id, forget_nil]
      premises := fun _ => by simp [Layer.id] }
  | k + 1, hk =>
    let C := chain D hv hc k (Nat.le_of_succ_le hk)
    have hlt : k < (syms D.T).length := hk
    let q := (syms D.T)[k]
    have hq : (syms D.T)[k]? = some q := List.getElem?_eq_getElem hlt
    let L := symLayer D hv k q hq (hc k)
    { R := Layer.comp C.R L C.E_out.symm (fun S => (C.A_out S).symm)
      E_in := C.E_in
      E_out := rfl
      A_in := C.A_in
      A_out := fun _ => Iff.rfl
      restrict := fun S => by
        show C.R.restrict (forget [q.name] S) = _
        rw [C.restrict, forget_forget, List.take_succ, names_getElemOpt hq]
        rfl
      premises := fun d => by
        simp only [Layer.comp]
        rw [C.premises, List.take_succ, hq]
        simp [L, symLayer] }

/-- Global base conflict-freedom gives every layer's hypothesis. -/
theorem chain_hc {D : Doc} (hv : Valid D)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B) :
    ∀ k (S₀ : VE.Structure.{u}), PrefixAdmissible D k S₀ → ConflictFreeAtIdx D k S₀ :=
  fun k S₀ h₀ => conflictFree_prefix_idx hv hc k S₀ h₀

/-- The whole route of a conflict-free document. -/
def route (D : Doc) (hv : Valid D)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B) : Chain.{u} D (size D) :=
  chain D hv (chain_hc hv hc) (size D) (Nat.le_refl _)

theorem route_premises {D : Doc} (hv : Valid D)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B) (d : Unit) :
    (route D hv hc).R.premises d = elaborate D.T := by
  rw [(route D hv hc).premises, elaborate_eq_flatMap]
  simp [size]

theorem route_restrict {D : Doc} (hv : Valid D)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B) (S : VE.Structure.{u}) :
    (route D hv hc).R.restrict S = restrictAll D.T S := by
  rw [(route D hv hc).restrict, List.take_of_length_le (by simp [size, layerNames])]
  rfl

/-- `BackgroundSound` on the norms route, from prefix satisfaction. -/
theorem route_backgroundSound {D : Doc} (hv : Valid D)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B) :
    BackgroundSound (route D hv hc).R (background D) := by
  intro d S hS _
  have hpa := ((route D hv hc).A_out S).mp hS
  obtain ⟨_, hB, hM, hP⟩ := (prefix_char hv _ (Nat.le_refl _) S).mp hpa
  have := (sat_document hv S).mpr ⟨(sat_literals_forget _ _ S).mp hB.2, hM, hP⟩
  exact fun a ha => this a (List.mem_append_left _ ha)

/-- `BackgroundComplete` on the norms route, from prefix satisfaction. -/
theorem route_backgroundComplete {D : Doc} (hv : Valid D)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B) :
    BackgroundComplete (route D hv hc).R (background D) := by
  intro d S hA hbg hprem
  rw [(route D hv hc).E_out] at hA
  rw [route_premises] at hprem
  have hsat : Sat S (background D ++ elaborate D.T) := fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · exact hbg a ha
    · exact hprem a ha
  obtain ⟨hl, hM, hP⟩ := (sat_document hv S).mp hsat
  apply ((route D hv hc).A_out S).mpr
  exact (prefix_char hv _ (Nat.le_refl _) S).mpr
    ⟨hA, ⟨restrictAll_admissible _ S hA, (sat_literals_forget _ _ S).mpr hl⟩, hM, hP⟩

/-! ## Route theorems -/

def definitionsHold (D : Doc) (S : VE.Structure.{u}) : Prop := Sat S (definitionPremises D.T)
def profileHold (D : Doc) (S : VE.Structure.{u}) : Prop := Sat S (pairPremises D.T)

/-- The first half of `norms_route_acceptance`, which needs no conflict-freedom:
an accepted certificate for Background ++ norm elaborations ++ Γ ⊢ φ gives φ in
every admissible structure satisfying the direct semantics, the definitions,
the profile, `Background_base` and `Γ`. -/
theorem norms_route_intended (D : Doc) (h : WellFormed D = true)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt D (size D)) (background D ++ elaborate D.T ++ Γ) φ c = true)
    (S : VE.Structure.{u}) (hS : S.Admissible (envAt D (size D))) (hcat : holdsCatala D.T S)
    (hdef : definitionsHold D S) (hprof : profileHold D S) (hbase : Sat S (backgroundBase D))
    (hΓ : Sat S Γ) : φ.denote S [] := by
  apply VE.Tableau.checkCertificate_sound.{u} _ _ _ c accepted S hS
  intro a ha
  simp only [List.mem_append, background] at ha
  rcases ha with (((ha | ha) | ha) | ha) | ha
  · exact hdef a ha
  · exact hbase a ha
  · exact hprof a ha
  · exact (elaborate_iff D h S).mpr hcat a ha
  · exact hΓ a ha

/-- `norms_route_acceptance`: an accepted FOL certificate for
`Background ++ layer premises ++ Γ ⊢ φ` over the complete environment gives
(1) `φ` in every admissible structure satisfying the direct semantics, the
definitions, the profile, `Background_base` and `Γ`; and (2), for a conflict-free
document and base formulas, `φ` in every base-admissible structure satisfying
`Γ` (through the composed frozen route). -/
theorem norms_route_acceptance (D : Doc) (h : WellFormed D = true)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt D (size D)) (background D ++ elaborate D.T ++ Γ) φ c = true) :
    (∀ S : VE.Structure.{u}, S.Admissible (envAt D (size D)) → holdsCatala D.T S → definitionsHold D S →
      profileHold D S → Sat S (backgroundBase D) → Sat S Γ → φ.denote S []) ∧
    ((∀ a ∈ Γ, a.WellFormed (envAt D 0) []) → φ.WellFormed (envAt D 0) [] →
      ∀ B : VE.Structure.{u}, BaseAdmissible D B → Sat B Γ → φ.denote B []) := by
  have hv := valid_of_wellFormed D h
  refine ⟨fun S hS hcat hdef hprof hbase hΓ =>
    norms_route_intended D h Γ φ c accepted S hS hcat hdef hprof hbase hΓ, fun hΓ hφ => ?_⟩
  · let C := route D hv hc
    have hacc : (Checker.tableau C.R.E_out).valid c
        (checkedPremises C.R (background D) () Γ) φ := by
      show VE.Tableau.checkCertificate C.R.E_out _ φ c = true
      rw [C.E_out, checkedPremises, route_premises]
      exact accepted
    have := route_acceptance C.R (background D) (route_backgroundSound hv hc)
      (Checker.tableau C.R.E_out) () Γ φ c _ φ hacc (List.map_id _) rfl
    intro B hB hs
    exact this.2.2 (by rw [C.E_in]; exact hΓ) (by rw [C.E_in]; exact hφ) B ((C.A_in B).mpr hB) hs

/-- `norms_route_countermodel`: a base countermodel expands to one the checker
sees (through the composed frozen route). -/
theorem norms_route_countermodel (D : Doc) (h : WellFormed D = true)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt D 0) []) (hφ : φ.WellFormed (envAt D 0) [])
    (B : VE.Structure.{u}) (hB : BaseAdmissible D B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
    ∃ S, DocumentExpansion D B S ∧ Sat S Γ ∧ ¬ φ.denote S [] := by
  have hv := valid_of_wellFormed D h
  let C := route D hv hc
  obtain ⟨S, hr, hA, hsat, hno⟩ := route_countermodel_expands C.R (background D)
    (route_backgroundSound hv hc) () Γ φ (by rw [C.E_in]; exact hΓ) (by rw [C.E_in]; exact hφ)
    B ((C.A_in B).mpr hB) hs hn
  obtain ⟨hbg, hp, hg⟩ := (sat_checked C.R (background D) S () Γ).mp hsat
  rw [route_premises] at hp
  refine ⟨S, ⟨by rw [← route_restrict hv hc]; exact hr,
    prefixAdmissible_admissible ((C.A_out S).mp hA), fun a ha => ?_⟩, hg, hno⟩
  rcases List.mem_append.mp ha with ha | ha
  · exact hbg a ha
  · exact hp a ha

/-- Model correspondence on the norms route: for base statements the checked
entailment is exactly consequence over base-admissible structures. -/
theorem norms_route_entails_iff (D : Doc) (h : WellFormed D = true)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt D 0) []) (hφ : φ.WellFormed (envAt D 0) []) :
    VE.Entails.{u} (envAt D (size D)) (background D ++ elaborate D.T ++ Γ) φ ↔
      ∀ B : VE.Structure.{u}, BaseAdmissible D B → Sat B Γ → φ.denote B [] := by
  have hv := valid_of_wellFormed D h
  let C := route D hv hc
  have := route_entails_iff C.R (background D) (route_backgroundSound hv hc)
    (route_backgroundComplete hv hc) () Γ φ (by rw [C.E_in]; exact hΓ) (by rw [C.E_in]; exact hφ)
  rw [C.E_out, checkedPremises, route_premises] at this
  rw [fol_entails_iff] at this
  rw [this]
  exact ⟨fun h B hB hs => h B ((C.A_in B).mpr hB) hs, fun h B hB hs => h B ((C.A_in B).mp hB) hs⟩

end VE.Norms
