import VE.Readings.Unspecified
import VE.NormDefaults.LayeredEntail

/-! Documents and extra base premises for readings on the soft completion. -/
namespace VE.Readings
open VE.Norms (envAt)
open VE.SoftNorms (SoftNode SoftDoc soften)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content)
universe u

def contentSoft : Content → Bool
  | .assertion _ => true
  | .norm _ => true
  | _ => false

def softShaped (D : Doc) : Bool :=
  D.chain == .soft && D.frame.soft.T.nodes.isEmpty && noRights D.frame &&
  D.items.all (fun it => match it with
    | .fixed _ c _ => contentSoft c
    | .bar _ _ => false
    | .set R => R.candidates.all (fun a => (a.content.map contentSoft).getD true))

def softXL (N : NDoc) (X : RightsDoc) : List (String × VE.Formula) :=
  VE.NormDefaults.Wire.softLabelledU (asU N X) (correlate X)
def softX (N : NDoc) (X : RightsDoc) : List VE.Formula := (softXL N X).map (·.2)
def freeX (N : NDoc) : List VE.Formula := softX N (free N.D).1
def oneX (N : NDoc) (s : String) (i : Nat) : List VE.Formula := softX N (one N.D s i).1
def choiceX (N : NDoc) (c : Choice) : List VE.Formula := softX N (choiceDoc N.D c).1

theorem softX_strict (N : NDoc) (X : RightsDoc) (hr : noRights X = true) (hs : allStrict X = true) :
    softX N X = [] := by
  have hh : StrictNodes X.soft := by
    intro M hM
    simp only [allStrict, List.all_eq_true, Bool.and_eq_true, beq_iff_eq, List.isEmpty_iff] at hs
    exact hs M hM
  have hc := correlate_noRights X hr
  have hp := softPremises_strict X.soft hh
  change VE.SoftNorms.excPremises X.soft ++ VE.SoftNorms.cohPremises X.soft = [] at hp
  obtain ⟨he, hcoh⟩ := List.append_eq_nil_iff.mp hp
  have hcp : VE.SoftNorms.collidingPairs X.soft = [] := by
    simpa only [VE.SoftNorms.cohPremises, List.map_eq_nil_iff] using hcoh
  simp only [softX, softXL, VE.NormDefaults.Wire.softLabelledU, hc.1, hcp, List.map_nil,
    List.append_nil, List.map_eq_nil_iff]
  simp [he]

theorem choiceX_normsShaped (N : NDoc) (hn : normsShaped N.D = true) (c : Choice) :
    choiceX N c = [] := by
  have hs : StrictDoc (choiceDoc N.D c).1 :=
    build_strict N.D (shaped hn) _ _ (fun R a h => by
      cases hi : c.index R.id with
      | none => rw [hi] at h; cases h
      | some i => rw [hi] at h; exact List.mem_of_getElem? h)
  exact softX_strict N _ hs.1 (by
    simp only [allStrict, List.all_eq_true, Bool.and_eq_true, beq_iff_eq, List.isEmpty_iff]
    intro M hM
    exact hs.2 M hM)

/-- `selects_wellFormed` for a rule typed by its own guard and carve-outs, whether or not the tree holds it. -/
theorem selects_wellFormed_of {T : VE.Norms.Tree} {E : VE.Environment} {Γ : List String} {p : String}
    (hT : VE.Norms.RulesTyped T E Γ p) (f : Nat) (M : VE.Norms.Node)
    (hM : M.guard.WellFormed E Γ ∧ ∀ C ∈ M.carveOuts, C.WellFormed E Γ) (hp : M.pred = p) :
    (VE.Norms.selects T f M).WellFormed E Γ := by
  refine ⟨VE.Norms.applies_wellFormed hM, VE.Norms.anyF_wellFormed E Γ _ ?_⟩
  intro a ha
  obtain ⟨C, hC, rfl⟩ := List.mem_map.mp ha
  obtain ⟨hC, hCp⟩ := VE.Norms.mem_children hC
  exact VE.Norms.yields_wellFormed hT f C hC (hCp.trans hp)

/-- A rule's selection regenerated on the filled tree is a base formula over its act's sorts. -/
theorem fillSelects_wellFormed (N : NDoc) (X : RightsDoc) (hs : VE.SoftNorms.WellFormedSoft (correlate X) = true)
    (hw : VE.NormDefaults.WellFormedU (asU N X) = true) (K : SoftNode) (hK : K ∈ (correlate X).T.nodes) :
    (VE.Norms.subst (VE.NormDefaults.fill (asU N X)).T (VE.Norms.size (VE.NormDefaults.fill (asU N X)))
      (VE.Norms.selects (VE.NormDefaults.fill (asU N X)).T (VE.Norms.fuel (VE.NormDefaults.fill (asU N X)).T)
        (VE.SoftNorms.primeNode (correlate X) K))).WellFormed (envAt (VE.NormDefaults.fill (asU N X)) 0)
      (VE.SoftNorms.sortsOf (correlate X) K.pred).reverse ∧
    ∀ s ∈ VE.SoftNorms.sortsOf (correlate X) K.pred, s ∈ (envAt (VE.NormDefaults.fill (asU N X)) 0).sorts := by
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ hs
  have hv : VE.Norms.Valid (VE.NormDefaults.fill (asU N X)) :=
    VE.Norms.valid_of_wellFormed _ (VE.NormDefaults.fill_wellFormed _ hw)
  obtain ⟨n, hn, hnK⟩ := List.mem_map.mp (hsv.predReg K hK)
  obtain ⟨r, hr⟩ : ∃ r, (correlate X).T.regulated.find? (·.name == K.pred) = some r :=
    Option.isSome_iff_exists.mp (List.find?_isSome.mpr ⟨n, hn, by simpa using hnK⟩)
  have hrm : r ∈ (VE.NormDefaults.fill (asU N X)).T.regulated := List.mem_of_find?_eq_some hr
  have hrn : r.name = K.pred := by simpa using List.find?_some hr
  have hso : VE.SoftNorms.sortsOf (correlate X) K.pred = r.sorts := by
    simp [VE.SoftNorms.sortsOf, VE.SoftNorms.sortsIn, hr]
  have hk := VE.Norms.index_before hv hrm
  have hT := VE.Norms.rulesTyped_of_valid hv hk
  have hpn : VE.NormDefaults.fillRoot (asU N X) (VE.SoftNorms.primeNode (correlate X) K) ∈
      (VE.NormDefaults.fill (asU N X)).T.nodes :=
    VE.NormDefaults.mem_fill_nodes.mpr (Or.inl ⟨_, List.mem_map_of_mem hK, rfl⟩)
  have hg := hT _ hpn (by rw [VE.NormDefaults.fillRoot_pred, hrn]; rfl)
  rw [VE.NormDefaults.fillRoot_guard, VE.NormDefaults.fillRoot_carveOuts] at hg
  have h1 := selects_wellFormed_of hT (VE.Norms.fuel (VE.NormDefaults.fill (asU N X)).T) _ hg
    (by rw [hrn]; rfl)
  have hle : VE.Norms.before (VE.NormDefaults.fill (asU N X)) r.name ≤
      VE.Norms.size (VE.NormDefaults.fill (asU N X)) :=
    Nat.le_of_lt (List.getElem?_eq_some_iff.mp hk).1
  rw [hso]
  exact ⟨VE.Norms.subst_wellFormed hv _ _ _ (VE.Norms.envAt_mono hle _ _ h1),
    (hv.decl _ (List.mem_of_getElem? hk)).2.2⟩

theorem softX_wellFormed (N : NDoc) (X : RightsDoc) (hs : VE.SoftNorms.WellFormedSoft (correlate X) = true)
    (hw : VE.NormDefaults.WellFormedU (asU N X) = true) :
    ∀ a ∈ softX N X, a.WellFormed (envAt (VE.NormDefaults.fill (asU N X)) 0) [] := by
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ hs
  intro a ha
  obtain ⟨⟨l, a⟩, hla, rfl⟩ := List.mem_map.mp ha
  rcases List.mem_append.mp hla with he | hc
  · -- `Exc_T`: soft's own premises, typed over `E′`, whose declarations `E‴` keeps
    have hea : a ∈ VE.SoftNorms.excPremises (correlate X) := (List.of_mem_zip he).2
    have := hsv.premTyped a (List.mem_append_left _ hea)
    exact VE.Norms.wf_mono (E := envAt (asU N X).D 0) (E' := envAt (VE.NormDefaults.fill (asU N X)) 0) rfl rfl
      (VE.NormDefaults.envAt_fill_mono (VE.NormDefaults.uvalid hw) 0) a [] this
  · obtain ⟨⟨M, K⟩, hMK, he⟩ := List.mem_map.mp hc
    cases he
    obtain ⟨hM, hK, -, -, -, -⟩ := VE.SoftNorms.mem_collidingPairs.mp hMK
    have hMs := fillSelects_wellFormed N X hs hw M hM
    have hKs := fillSelects_wellFormed N X hs hw K hK
    rw [← hsv.cpSorts _ hMK] at hKs
    apply VE.Norms.bindAll_wellFormed hMs.2 [] _
    simp only [List.append_nil]
    exact ⟨hMs.1, hKs.1⟩

def filledAuthorEnv (N : NDoc) : VE.Environment :=
  envAt { N.D.frame.soft with E := fillFrameEnv N }.base 0

theorem filledAuthorEnv_eq (N : NDoc) : filledAuthorEnv N = authorEnv (fillDoc N) := by
  rfl

def WellFormedSD (N : NDoc) : Bool :=
  WellFormedDoc N.D && softShaped N.D && fillNamesFree N && VE.NormDefaults.WellFormedU (freeU N) &&
  N.D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
    (R.candidates[i]?.bind (·.content)).isNone || VE.NormDefaults.WellFormedU (oneU N R.id i)))
end VE.Readings
