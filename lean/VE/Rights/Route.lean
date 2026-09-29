import VE.Rights.Distinction

/-! The conditional contract and the restated route (docs/spec/rights.md 5, 9.3).

`Lim_D` is a new base premise, so the soft route's document-wide theorems are restated
with `BaseAdmissible″ D B := BaseAdmissible′ (correlate D) B ∧ Sat B Lim_D` and
`background″ := background′ (correlate D) ++ Lim_D`; every per-structure lemma
(`coherent_expands`, `soft_conflict_decomposition`, `soften_faithful`, …) is reused on
`correlate D`. The route is soft's chain of W1 layers over `T″′` with `Lim_D` added to
each prefix's admissibility (`PrefixAdmissibleR`), exactly as soft adds `Soft_T`. -/
namespace VE.Rights
open VE.Norms
open VE.Route (Unique)
open VE.SoftNorms (SoftDoc soften PrefixAdmissible' BaseAdmissible' background' backgroundBase' softPremises
  holdsSoft NoStrictCollision NoHardPairConflict)
universe u

/-! ## The contract -/

/-- Reused on `correlate D`, not restated: soft's per-structure instance of W1's
`conflictFree_expands_document`. -/
theorem coherent_expands (D : RightsDoc) (h : WellFormedRights D = true) (B : VE.Structure.{u})
    (hB : VE.Norms.BaseAdmissible (soften (correlate D)) B) :
    VE.Route.Unique (VE.Norms.DocumentExpansion (soften (correlate D)) B) ↔
      VE.Norms.ConflictFree (soften (correlate D)) B :=
  VE.SoftNorms.coherent_expands (correlate D) (correlate_wellFormed D h) B hB

/-- The global form, restated over the rights-admissible bases. -/
theorem rights_coherent_expands_all (D : RightsDoc) (h : WellFormedRights D = true) :
    (∀ B : VE.Structure.{u}, BaseAdmissibleR D B →
      VE.Route.Unique (VE.Norms.DocumentExpansion (soften (correlate D)) B)) ↔ RightsConflictFree.{u} D :=
  ⟨fun hu B hB => (coherent_expands D h B hB.1.1).mp (hu B hB),
   fun hc B hB => (coherent_expands D h B hB.1.1).mpr (hc B hB)⟩

/-- W1's `conflictFreeCheck` on `T″′` with `Background_base″`. -/
def rightsConflictFreeCheck (D : RightsDoc) (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (targets (soften (correlate D))).length == certs.length &&
    ((targets (soften (correlate D))).zip certs).all (fun (t, c) => match c with
      | some c => VE.Tableau.checkCertificate (envAt (soften (correlate D)) 0) (backgroundBaseR D) (targetConclusion t) c
      | none => false)

theorem rightsConflictFreeCheck_target {D : RightsDoc} {certs : List (Option VE.Tableau.Certificate)}
    (hc : rightsConflictFreeCheck D certs = true) {t : String × List String × VE.Formula}
    (ht : t ∈ targets (soften (correlate D))) :
    ∃ c, VE.Tableau.checkCertificate (envAt (soften (correlate D)) 0) (backgroundBaseR D) (targetConclusion t) c = true := by
  simp only [rightsConflictFreeCheck, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
  obtain ⟨hl, hall⟩ := hc
  obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp ht
  have hlt : i < (targets (soften (correlate D))).length := (List.getElem?_eq_some_iff.mp hi).1
  have hlt' : i < certs.length := hl ▸ hlt
  have hmem : (t, certs[i]) ∈ (targets (soften (correlate D))).zip certs := by
    apply List.mem_iff_getElem?.mpr
    refine ⟨i, ?_⟩
    rw [List.getElem?_zip_eq_some]
    exact ⟨hi, List.getElem?_eq_getElem hlt'⟩
  have := hall _ hmem
  cases hci : certs[i] with
  | none => rw [hci] at this; cases this
  | some c => rw [hci] at this; exact ⟨c, this⟩

theorem sat_backgroundBaseR {D : RightsDoc} {B : VE.Structure.{u}} (hB : BaseAdmissibleR D B) :
    ∀ a ∈ backgroundBaseR D, a.denote B [] := by
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact VE.SoftNorms.sat_backgroundBasePrime hB.1 a ha
  · exact hB.2 a ha

/-- 5.2, the certified statement. -/
theorem rights_conflict_free (D : RightsDoc) (h : WellFormedRights D = true)
    (certs : List (Option VE.Tableau.Certificate)) (hc : rightsConflictFreeCheck D certs = true) :
    RightsConflictFree.{u} D := by
  have hv := valid_of_wellFormed _ (VE.SoftNorms.soften_wellFormed _ (correlate_wellFormed D h))
  intro B hB
  have cert : ∀ t ∈ targets (soften (correlate D)), ∀ vs, VE.TupleTyped B t.2.1 vs →
      ¬ t.2.2.denote B (tupleVal vs) := by
    intro t ht vs hvs
    obtain ⟨c, hcc⟩ := rightsConflictFreeCheck_target hc ht
    have he := VE.Tableau.checkCertificate_sound.{u} _ _ _ c hcc B hB.1.1.1 (sat_backgroundBaseR hB)
    exact (bindAll_denote_nil B _ _).mp he vs hvs
  refine ⟨fun r hr vs hvs => ?_, fun pr hpr vs hvs => ?_⟩
  · exact cert (r.name, r.sorts, conflict (soften (correlate D)) r)
      (List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩)) vs hvs
  · exact cert (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflict (soften (correlate D)) pr)
      (List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)) vs hvs

/-- Soft's `backgroundValid′` on `correlate D` and the finite evaluation of `Lim_D`. -/
def backgroundValidR {α : Type u} [DecidableEq α] (D : RightsDoc) (M : VE.FiniteModel α) : Bool :=
  VE.SoftNorms.backgroundValid' (correlate D) M && (limPremises D).all (fun a => a.eval M [])

theorem baseAdmissibleR_of_valid {α : Type u} [DecidableEq α] (D : RightsDoc) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (soften (correlate D)) 0)) (hb : backgroundValidR D M = true) :
    BaseAdmissibleR D M.asStructure := by
  simp only [backgroundValidR, Bool.and_eq_true, List.all_eq_true] at hb
  exact ⟨VE.SoftNorms.baseAdmissiblePrime_of_valid _ M valid hb.1,
    fun a ha => (VE.eval_iff_denote M [] a).mp (hb.2 a ha)⟩

/-- A typed finite base witness over `E″′_base` passing the extended Background check refutes the
conditional claim, and is classified. -/
theorem rights_conflict_witness_sound {α : Type u} [DecidableEq α] (D : RightsDoc) (h : WellFormedRights D = true)
    (t : String × List String × VE.Formula) (ht : t ∈ VE.Norms.targets (soften (correlate D)))
    (M : VE.FiniteModel α) (valid : M.Valid (VE.Norms.envAt (soften (correlate D)) 0))
    (hb : backgroundValidR D M = true) (vs : List α) (typed : VE.TupleTyped M.asStructure t.2.1 vs)
    (hw : t.2.2.eval M (tupleVal vs) = true) :
    ¬ VE.Norms.ConflictFree (soften (correlate D)) M.asStructure ∧ ¬ RightsConflictFree.{u} D ∧
    (¬ NoStrictCollision (correlate D) M.asStructure ∨ ¬ NoHardPairConflict (correlate D) M.asStructure) := by
  have hw' := correlate_wellFormed D h
  have hB := baseAdmissibleR_of_valid D M valid hb
  obtain ⟨hn, _, _⟩ := Replay.target_refutes (soften (correlate D)) (VE.SoftNorms.soften_wellFormed _ hw') t ht
    M.asStructure hB.1.1 vs typed ((VE.eval_iff_denote M _ _).mp hw)
  exact ⟨hn, fun hc => hn (hc _ hB), VE.SoftNorms.soft_witness_classified _ hw' _ hB.1 hn⟩

/-! ## The restated route -/

/-- `PrefixAdmissible′` with `Lim_D` on the base restriction. -/
def PrefixAdmissibleR (D : RightsDoc) (k : Nat) (S : VE.Structure.{u}) : Prop :=
  PrefixAdmissible' (correlate D) k S ∧ Sat (restrictAll (soften (correlate D)).T S) (limPremises D)

section RightsLayer
variable {D : RightsDoc} (hv : Valid (soften (correlate D))) {k : Nat} {q : Sym}
  (hk : (syms (soften (correlate D)).T)[k]? = some q)
include hv hk

omit hv in
theorem rights_restrict_admissible (S : VE.Structure.{u}) (h : PrefixAdmissibleR D (k + 1) S) :
    PrefixAdmissibleR D k (forget [q.name] S) := by
  refine ⟨VE.SoftNorms.soft_restrict_admissible hk S h.1, ?_⟩
  rw [restrictAll_forget (name_mem_layerNames hk)]
  exact h.2

theorem rights_layer_expands
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissibleR D k S₀ → ConflictFreeAtIdx (soften (correlate D)) k S₀)
    (S₀ : VE.Structure.{u}) (h₀ : PrefixAdmissibleR D k S₀) :
    Unique fun S => forget [q.name] S = S₀ ∧ PrefixAdmissibleR D (k + 1) S ∧
      ∀ a ∈ symPremises (soften (correlate D)).T q, a.denote S [] := by
  have := (local_expands hv hk S₀ h₀.1.1).mpr (hc S₀ h₀)
  refine (unique_congr fun S => ?_).mp this
  constructor
  · rintro ⟨h₁, h₂⟩
    refine ⟨h₁, ⟨⟨h₂, ?_⟩, ?_⟩, symPremises_sat hv hk S h₂⟩
    · rw [← restrictAll_forget (name_mem_layerNames hk) S, h₁]
      exact h₀.1.2
    · rw [← restrictAll_forget (name_mem_layerNames hk) S, h₁]
      exact h₀.2
  · rintro ⟨h₁, h₂, _⟩
    exact ⟨h₁, h₂.1.1⟩

end RightsLayer

/-- The rights layer of the `k`-th layer symbol of `T″′`. -/
def rightsSymLayer (D : RightsDoc) (hv : Valid (soften (correlate D))) (k : Nat) (q : Sym)
    (hk : (syms (soften (correlate D)).T)[k]? = some q)
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissibleR D k S₀ → ConflictFreeAtIdx (soften (correlate D)) k S₀) :
    VE.Route.Layer VE.Route.fol.{u} Unit where
  E_in := envAt (soften (correlate D)) k
  E_out := envAt (soften (correlate D)) (k + 1)
  extends_env a h := envAt_mono (Nat.le_succ k) a [] h
  premises _ := symPremises (soften (correlate D)).T q
  premises_wellFormed _ := symPremises_wellFormed hv hk
  Admissible_in := PrefixAdmissibleR D k
  Admissible_out := PrefixAdmissibleR D (k + 1)
  admissible_out _ h := prefixAdmissible_admissible h.1.1
  restrict := forget [q.name]
  restrict_admissible S h := rights_restrict_admissible hk S h
  restrict_holds S a _ ha := denote_forget (self_hidden hv hk) S a [] [] ha
  Intended _ S := LayerMeaning (soften (correlate D)).T S q
  faithful _ S h := symLayer_faithful hv hk S h.1.1
  expands _ S₀ h₀ := rights_layer_expands hv hk hc S₀ h₀

/-- A composed prefix of the rights route. -/
structure RightsChain (D : RightsDoc) (k : Nat) where
  R : VE.Route.Layer VE.Route.fol.{u} Unit
  E_in : R.E_in = envAt (soften (correlate D)) 0
  E_out : R.E_out = envAt (soften (correlate D)) k
  A_in : ∀ S, R.Admissible_in S ↔ PrefixAdmissibleR D 0 S
  A_out : ∀ S, R.Admissible_out S ↔ PrefixAdmissibleR D k S
  restrict : ∀ S, R.restrict S = forget ((layerNames (soften (correlate D)).T).take k) S
  premises : ∀ d, R.premises d = ((syms (soften (correlate D)).T).take k).flatMap (symPremises (soften (correlate D)).T)

def rightsChain (D : RightsDoc) (hv : Valid (soften (correlate D)))
    (hc : ∀ k (S₀ : VE.Structure.{u}), PrefixAdmissibleR D k S₀ → ConflictFreeAtIdx (soften (correlate D)) k S₀) :
    (k : Nat) → k ≤ size (soften (correlate D)) → RightsChain.{u} D k
  | 0, _ =>
    { R := VE.Route.Layer.id (envAt (soften (correlate D)) 0) (PrefixAdmissibleR D 0) (fun _ h => h.1.1.1)
      E_in := rfl
      E_out := rfl
      A_in := fun _ => Iff.rfl
      A_out := fun _ => Iff.rfl
      restrict := fun S => by simp [VE.Route.Layer.id, forget_nil]
      premises := fun _ => by simp [VE.Route.Layer.id] }
  | k + 1, hk =>
    let C := rightsChain D hv hc k (Nat.le_of_succ_le hk)
    have hlt : k < (syms (soften (correlate D)).T).length := hk
    let q := (syms (soften (correlate D)).T)[k]
    have hq : (syms (soften (correlate D)).T)[k]? = some q := List.getElem?_eq_getElem hlt
    let L := rightsSymLayer D hv k q hq (hc k)
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
        simp [L, rightsSymLayer] }

theorem prefixAdmissibleR_zero (D : RightsDoc) (B : VE.Structure.{u}) :
    PrefixAdmissibleR D 0 B ↔ BaseAdmissibleR D B := by
  constructor
  · rintro ⟨hB, hs⟩
    refine ⟨(VE.SoftNorms.prefixAdmissiblePrime_zero _ B).mp hB, ?_⟩
    rw [restrictAll_self B hB.1.1] at hs
    exact hs
  · rintro ⟨hB, hs⟩
    refine ⟨(VE.SoftNorms.prefixAdmissiblePrime_zero _ B).mpr hB, ?_⟩
    rw [restrictAll_self B hB.1.1]
    exact hs

/-- Conflict-freedom over the rights-admissible bases gives every layer's hypothesis. -/
theorem rightsChain_hc {D : RightsDoc} (hv : Valid (soften (correlate D))) (hc : RightsConflictFree.{u} D) :
    ∀ k (S₀ : VE.Structure.{u}), PrefixAdmissibleR D k S₀ → ConflictFreeAtIdx (soften (correlate D)) k S₀ := by
  intro k S₀ h₀
  cases hk : (syms (soften (correlate D)).T)[k]? with
  | none => simp [ConflictFreeAtIdx, hk]
  | some q =>
    have hB := ((prefix_char hv k (prefixAdmissible_le h₀.1.1) S₀).mp h₀.1.1).2.1
    exact conflictFreeAt_of_base hv hk S₀ h₀.1.1 (hc _ ⟨⟨hB, h₀.1.2⟩, h₀.2⟩)

def rightsRouteChain (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree.{u} D) :
    RightsChain.{u} D (size (soften (correlate D))) :=
  rightsChain D (valid_of_wellFormed _ (VE.SoftNorms.soften_wellFormed _ (correlate_wellFormed D h)))
    (rightsChain_hc (valid_of_wellFormed _ (VE.SoftNorms.soften_wellFormed _ (correlate_wellFormed D h))) hc) _
    (Nat.le_refl _)

theorem rightsRouteChain_premises (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree.{u} D)
    (d : Unit) : (rightsRouteChain D h hc).R.premises d = elaborate (soften (correlate D)).T := by
  rw [(rightsRouteChain D h hc).premises, elaborate_eq_flatMap]
  simp [size]

theorem rightsRouteChain_restrict (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree.{u} D)
    (S : VE.Structure.{u}) : (rightsRouteChain D h hc).R.restrict S = restrictAll (soften (correlate D)).T S := by
  rw [(rightsRouteChain D h hc).restrict, List.take_of_length_le (by simp [size, layerNames])]
  rfl

/-- The rights route: the composed frozen P0 layers of `T″′` with `BaseAdmissible″` as input
admissibility. -/
def rightsRoute (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree.{u} D) :
    { L : VE.Route.Layer VE.Route.fol.{u} Unit // L.E_in = VE.Norms.envAt (soften (correlate D)) 0 ∧
      (∀ B, L.Admissible_in B ↔ BaseAdmissibleR D B) ∧
      L.premises () = VE.Norms.elaborate (soften (correlate D)).T } :=
  ⟨(rightsRouteChain D h hc).R, (rightsRouteChain D h hc).E_in,
    fun B => ((rightsRouteChain D h hc).A_in B).trans (prefixAdmissibleR_zero D B),
    rightsRouteChain_premises D h hc ()⟩

theorem rightsRoute_E_out (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree.{u} D) :
    (rightsRoute D h hc).1.E_out = envAt (soften (correlate D)) (size (soften (correlate D))) :=
  (rightsRouteChain D h hc).E_out

theorem sat_lim_restrict {D : RightsDoc} (hv : RightsValid D) (S : VE.Structure.{u}) :
    Sat (restrictAll (soften (correlate D)).T S) (limPremises D) ↔ Sat S (limPremises D) := by
  constructor
  · intro hs a ha
    exact (restrictAll_denote a [] (hv.limTyped a ha) S []).mp (hs a ha)
  · intro hs a ha
    exact (restrictAll_denote a [] (hv.limTyped a ha) S []).mpr (hs a ha)

theorem sat_soft_restrictR {D : RightsDoc} (hv : RightsValid D) (S : VE.Structure.{u}) :
    Sat (restrictAll (soften (correlate D)).T S) (softPremises (correlate D)) ↔ Sat S (softPremises (correlate D)) :=
  VE.SoftNorms.sat_soft_restrict (VE.SoftNorms.softValid_of_wellFormed _ hv.wfSoft) S

theorem rights_route_backgroundSound (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree.{u} D) :
    VE.Route.BackgroundSound (rightsRoute D h hc).1 (backgroundR D) := by
  have hrv := rightsValid_of_wellFormed D h
  have hv := valid_of_wellFormed _ (VE.SoftNorms.soften_wellFormed _ hrv.wfSoft)
  intro d S hS _
  have hpa := ((rightsRouteChain D h hc).A_out S).mp hS
  obtain ⟨_, hB, hM, hP⟩ := (prefix_char hv _ (Nat.le_refl _) S).mp hpa.1.1
  have hdoc := (sat_document hv S).mpr ⟨(sat_literals_forget _ _ S).mp hB.2, hM, hP⟩
  have hsoft := (sat_soft_restrictR hrv S).mp hpa.1.2
  have hlim := (sat_lim_restrict hrv S).mp hpa.2
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · rcases List.mem_append.mp ha with ha | ha
    · exact hdoc a (List.mem_append_left _ ha)
    · exact hsoft a ha
  · exact hlim a ha

theorem rights_route_backgroundComplete (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree.{u} D) :
    VE.Route.BackgroundComplete (rightsRoute D h hc).1 (backgroundR D) := by
  have hrv := rightsValid_of_wellFormed D h
  have hv := valid_of_wellFormed _ (VE.SoftNorms.soften_wellFormed _ hrv.wfSoft)
  intro d S hA hbg hprem
  have hA' : S.Admissible (envAt (soften (correlate D)) (size (soften (correlate D)))) := by
    have := rightsRoute_E_out D h hc
    simp only [VE.Route.fol] at hA
    rw [this] at hA
    exact hA
  have hprem' : Sat S (elaborate (soften (correlate D)).T) := by
    have := rightsRouteChain_premises D h hc d
    intro a ha
    exact hprem a (by show a ∈ (rightsRouteChain D h hc).R.premises d; rw [this]; exact ha)
  have hsat : Sat S (background (soften (correlate D)) ++ elaborate (soften (correlate D)).T) := fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · exact hbg a (List.mem_append_left _ (List.mem_append_left _ ha))
    · exact hprem' a ha
  obtain ⟨hl, hM, hP⟩ := (sat_document hv S).mp hsat
  apply ((rightsRouteChain D h hc).A_out S).mpr
  refine ⟨⟨(prefix_char hv _ (Nat.le_refl _) S).mpr
    ⟨hA', ⟨restrictAll_admissible _ S hA', (sat_literals_forget _ _ S).mpr hl⟩, hM, hP⟩, ?_⟩, ?_⟩
  · exact (sat_soft_restrictR hrv S).mpr (fun a ha => hbg a (List.mem_append_left _ (List.mem_append_right _ ha)))
  · exact (sat_lim_restrict hrv S).mpr (fun a ha => hbg a (List.mem_append_right _ ha))

/-- The first half of `rights_route_acceptance`, which needs no conflict-freedom. -/
theorem rights_route_intended (D : RightsDoc) (h : WellFormedRights D = true)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (VE.Norms.envAt (soften (correlate D)) (size (soften (correlate D))))
                  (backgroundR D ++ VE.Norms.elaborate (soften (correlate D)).T ++ Γ) φ c = true)
    (S : VE.Structure.{u}) (hS : S.Admissible (VE.Norms.envAt (soften (correlate D)) (size (soften (correlate D)))))
    (hsoft : holdsSoft (correlate D) S) (hdef : VE.Norms.definitionsHold (soften (correlate D)) S)
    (hprof : VE.Norms.profileHold (soften (correlate D)) S)
    (hbase : Sat S (VE.Norms.backgroundBase (soften (correlate D)))) (hsp : Sat S (softPremises (correlate D)))
    (hlim : Sat S (limPremises D)) (hΓ : Sat S Γ) :
    φ.denote S [] := by
  apply VE.Tableau.checkCertificate_sound.{u} _ _ _ c accepted S hS
  intro a ha
  simp only [List.mem_append, backgroundR, background', background] at ha
  rcases ha with (((((ha | ha) | ha) | ha) | ha) | ha) | ha
  · exact hdef a ha
  · exact hbase a ha
  · exact hprof a ha
  · exact hsp a ha
  · exact hlim a ha
  · exact (VE.SoftNorms.soft_elaborate_iff _ (correlate_wellFormed D h) S).mpr hsoft a ha
  · exact hΓ a ha

/-- 5.2: the soft route's acceptance restated with `BaseAdmissible″` and `background″`. -/
theorem rights_route_acceptance (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree.{u} D)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (VE.Norms.envAt (soften (correlate D)) (size (soften (correlate D))))
                  (backgroundR D ++ VE.Norms.elaborate (soften (correlate D)).T ++ Γ) φ c = true) :
    (∀ S : VE.Structure.{u}, S.Admissible (VE.Norms.envAt (soften (correlate D)) (size (soften (correlate D)))) →
       holdsSoft (correlate D) S → VE.Norms.definitionsHold (soften (correlate D)) S →
       VE.Norms.profileHold (soften (correlate D)) S → Sat S (VE.Norms.backgroundBase (soften (correlate D))) →
       Sat S (softPremises (correlate D)) → Sat S (limPremises D) → Sat S Γ → φ.denote S []) ∧
    ((∀ a ∈ Γ, a.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) []) →
       φ.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) [] →
       ∀ B : VE.Structure.{u}, BaseAdmissibleR D B → Sat B Γ → φ.denote B []) := by
  refine ⟨fun S hS hsoft hdef hprof hbase hsp hlim hΓ =>
    rights_route_intended D h Γ φ c accepted S hS hsoft hdef hprof hbase hsp hlim hΓ, fun hΓ hφ => ?_⟩
  let R := rightsRoute D h hc
  have hacc : (VE.Route.Checker.tableau R.1.E_out).valid c
      (VE.Route.checkedPremises R.1 (backgroundR D) () Γ) φ := by
    show VE.Tableau.checkCertificate R.1.E_out _ φ c = true
    rw [rightsRoute_E_out D h hc, VE.Route.checkedPremises, R.2.2.2]
    exact accepted
  have := VE.Route.route_acceptance R.1 (backgroundR D) (rights_route_backgroundSound D h hc)
    (VE.Route.Checker.tableau R.1.E_out) () Γ φ c _ φ hacc (List.map_id _) rfl
  intro B hB hs
  exact this.2.2 (by rw [R.2.1]; exact hΓ) (by rw [R.2.1]; exact hφ) B ((R.2.2.1 B).mpr hB) hs

/-- 5.2: the soft route's countermodel restated. -/
theorem rights_route_countermodel (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree.{u} D)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) [])
    (hφ : φ.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) [])
    (B : VE.Structure.{u}) (hB : BaseAdmissibleR D B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
    ∃ S, VE.Norms.DocumentExpansion (soften (correlate D)) B S ∧ Sat S (softPremises (correlate D)) ∧
      Sat S (limPremises D) ∧ Sat S Γ ∧ ¬ φ.denote S [] := by
  let R := rightsRoute D h hc
  obtain ⟨S, hr, hA, hsat, hno⟩ := VE.Route.route_countermodel_expands R.1 (backgroundR D)
    (rights_route_backgroundSound D h hc) () Γ φ (by rw [R.2.1]; exact hΓ) (by rw [R.2.1]; exact hφ)
    B ((R.2.2.1 B).mpr hB) hs hn
  obtain ⟨hbg, hp, hg⟩ := (VE.Route.sat_checked R.1 (backgroundR D) S () Γ).mp hsat
  have hp' : Sat S (elaborate (soften (correlate D)).T) := by
    intro a ha
    exact hp a (by show a ∈ R.1.premises (); rw [R.2.2.2]; exact ha)
  refine ⟨S, ⟨by rw [← rightsRouteChain_restrict D h hc]; exact hr,
    prefixAdmissible_admissible (((rightsRouteChain D h hc).A_out S).mp hA).1.1, fun a ha => ?_⟩,
    fun a ha => hbg a (List.mem_append_left _ (List.mem_append_right _ ha)),
    fun a ha => hbg a (List.mem_append_right _ ha), hg, hno⟩
  rcases List.mem_append.mp ha with ha | ha
  · exact hbg a (List.mem_append_left _ (List.mem_append_left _ ha))
  · exact hp' a ha

end VE.Rights
