import VE.Readings.SoftDefaults
import VE.Readings.Scan

/-! Separation on filled sides (docs/spec/rd-9-soft-chain.md 1.5, 4.2 and 6.6; plan SC-2).

A reading of a document under the soft completion is read on its filled tree `fill (asU N X)`, a W1 document, with
soft's premises regenerated on it as extra base premises (`softX`). Its **filled side** `sideOfS` is S1's `Side`
with that tree, so S1's executable functions, which read a side and nothing else, run on it unchanged: `separatesS`
is S1's pair check `pairEval` (the function the route runs) on the two filled sides, with the witness's `Fill_T`
evaluated on its own completion (`fillHoldsS`). The other reading's `Fill_T` is not evaluated, which is sound since
`AchievesS` requires it of every completion it admits.

`separatesS_sound` says that, on a base valid over the filled author vocabulary, a `true` answer proves the witness
achieves the recorded value on the shown base and shared tables and the other reading does not. The proof is S1's
(`separates_witness`, `separates_other`) with two lemmas for the side: `sideValidOn_sideOfS_iff` (the filled side's
admissibility is the filled tree's base background and exactly `softX`) and `observeOn_sideOfS_sound` (its
observation is the W1 semantics of the filled tree, read in its canonical expansion). -/
namespace VE.Readings
open VE.Norms (Regulated tupleVal envAt size ConstantsTyped)
open VE.SoftNorms (SoftNode canon)
open VE.Rights (RightsDoc correlate)
universe u

def sideOfS (N : NDoc) (X : RightsDoc × List VE.Formula) : Side :=
  let S := VE.NormDefaults.fill (asU N X.1)
  let L := VE.Norms.layersOf S
  ⟨X.1, X.2, genKeys X.1, S, L, VE.Norms.hide S.E L.names⟩

theorem excLabels_length (D : VE.SoftNorms.SoftDoc) :
    (VE.SoftNorms.Wire.excLabels D).length = (VE.SoftNorms.excPremises D).length := by
  simp only [VE.SoftNorms.Wire.excLabels, VE.SoftNorms.excPremises, List.length_flatMap]
  congr 1
  apply List.map_congr_left
  intro N _
  simp only [VE.SoftNorms.excPremisesOf]
  cases N.mode <;> cases N.exception <;> simp

/-- `backgroundValidOn` on a filled side evaluates exactly `softX`. -/
theorem softPremisesIn_fill (N : NDoc) (X : RightsDoc) :
    VE.SoftNorms.softPremisesIn (correlate X) (VE.NormDefaults.fill (asU N X))
      (VE.Norms.layersOf (VE.NormDefaults.fill (asU N X))) = softX N X := by
  simp only [VE.SoftNorms.softPremisesIn, softX, softXL, VE.NormDefaults.Wire.softLabelledU, List.map_append,
    List.map_map]
  congr 1
  · exact (List.map_snd_zip (by rw [excLabels_length]; exact Nat.le_refl _)).symm
  · apply List.map_congr_left
    intro p _
    simp only [Function.comp, VE.SoftNorms.cohPremiseIn, VE.NormDefaults.Wire.cohPremiseU, VE.Norms.substIn_eq,
      VE.Norms.layersOf_syms, VE.Norms.size, VE.SoftNorms.selectsOn]

def fillHoldsS {α : Type} [DecidableEq α] (N : NDoc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) : Bool :=
  (VE.NormDefaults.fillPremises (oneU N s i)).all (fun φ => φ.eval (tablesModel (one N.D s i).1 M T) [])

def separatesS {α : Type} [DecidableEq α] (N : NDoc) (s : String) (i j : Nat) (σ : Situation α) : Bool :=
  let Pi := sideOfS N (one N.D s i)
  let Pj := sideOfS N (one N.D s j)
  decide (cellsOn N.D s j Pj σ.base ≤ maxCells) &&
  (pairEval (m := Id) (pure ()) (pure ()) N.D s i j Pi Pj σ).1 &&
  fillHoldsS N s i σ.base (tablesForOf Pi.X (σ.fixed ++ σ.decisions))

def ObservesF (N : NDoc) (X : RightsDoc) (A : List VE.Formula) (B : VE.Structure.{u}) :
    Probe B.Carrier → Bool → Prop
  | .outcome p vs, v => ∃ r ∈ (correlate X).T.regulated, r.name = p ∧ VE.TupleTyped B r.sorts vs ∧
      VE.Norms.Value (VE.NormDefaults.fill (asU N X)).T r (canon (VE.NormDefaults.fill (asU N X)) B) vs = some v
  | .selects k p vs, v => VE.TupleTyped B (VE.SoftNorms.sortsOf (correlate X) p) vs ∧
      ((∃ M ∈ selectable X k p, VE.Norms.SelectsD (VE.NormDefaults.fill (asU N X)).T
          (canon (VE.NormDefaults.fill (asU N X)) B) (tupleVal vs)
          (VE.Norms.fuel (VE.NormDefaults.fill (asU N X)).T) (VE.SoftNorms.primeNode (correlate X) M)) ↔ v = true)
  | .holds, v => ((∀ a ∈ A, a.denote (canon (VE.NormDefaults.fill (asU N X)) B) []) ↔ v = true)

def AchievesS (N : NDoc) (s : String) (i : Nat) (B : VE.Structure.{u}) (F : Tables B.Carrier)
    (q : Probe B.Carrier) (v : Bool) : Prop :=
  B.Admissible (filledAuthorEnv N) ∧
  ∃ G : Tables B.Carrier, (∀ k, owned N.D s i k = false → ∀ vs, G k vs ↔ F k vs) ∧
    VE.NormDefaults.Wire.BaseAdmissibleX (oneU N s i) (oneX N s i) (withTables (one N.D s i).1 B G) ∧
    ObservesF N (one N.D s i).1 (one N.D s i).2 (withTables (one N.D s i).1 B G) q v
def SeparatedS (N : NDoc) (s : String) (i j : Nat) : Prop :=
  ∃ (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier) (v : Bool),
    (AchievesS N s i B F q v ∧ ¬ AchievesS N s j B F q v) ∨ (AchievesS N s j B F q v ∧ ¬ AchievesS N s i B F q v)

/-! ## The filled side -/

theorem sideValidOn_sideOfS_iff {α : Type} [DecidableEq α] (N : NDoc) (X : RightsDoc × List VE.Formula)
    (hr : noRights X.1 = true) (M : VE.FiniteModel α) (T : List (GenKey × List (List α))) :
    sideValidOn (sideOfS N X) M T = true ↔
      tablesTypedOn (sideOfS N X) M T = true ∧
      VE.Norms.backgroundValid (VE.NormDefaults.fill (asU N X.1)) (tablesModelOn (sideOfS N X) M T) = true ∧
      ∀ a ∈ softX N X.1, a.eval (tablesModelOn (sideOfS N X) M T) [] = true := by
  have hl := (correlate_noRights X.1 hr).2
  have hs := softPremisesIn_fill N X.1
  simp only [sideValidOn, backgroundValidOn, sideOfS] at hs ⊢
  rw [hs, hl]
  simp [Bool.and_eq_true, List.all_eq_true]

/-- The filled side's base environment is the filled tree's base vocabulary. -/
theorem sideOfS_E0 (N : NDoc) (X : RightsDoc × List VE.Formula) :
    (sideOfS N X).E0 = envAt (VE.NormDefaults.fill (asU N X.1)) 0 := by
  simp only [sideOfS, envAt, VE.Norms.layersOf_names, List.drop_zero]

theorem tablesModelOn_sideOfS {α : Type} (N : NDoc) (X : RightsDoc × List VE.Formula) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) : tablesModelOn (sideOfS N X) M T = tablesModel X.1 M T := rfl

/-- W1's conflict formula on a valid document is the decisions of its canonical interpretation. -/
theorem conflict_canon_doc {S : VE.Norms.Doc} (hv : VE.Norms.Valid S) (B : VE.Structure.{u})
    (hc : ConstantsTyped S B) {r : Regulated} (hr : r ∈ S.T.regulated) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) :
    (VE.Norms.conflict S r).denote B (tupleVal vs) ↔
      VE.Norms.DecidesD S.T (canon S B) (tupleVal vs) r.name true ∧
        VE.Norms.DecidesD S.T (canon S B) (tupleVal vs) r.name false := by
  have hk := VE.Norms.index_before hv hr
  have hT := VE.Norms.rulesTyped_of_valid hv hk
  have hρ := VE.Norms.tupleVal_typed B _ vs hvs
  simp only [VE.Norms.conflict, VE.Norms.pos, VE.Norms.neg, VE.Formula.denote]
  rw [VE.SoftNorms.canon_subst hv B hc _ _ _ (VE.Norms.decides_wellFormed hT true) _ hρ,
    VE.SoftNorms.canon_subst hv B hc _ _ _ (VE.Norms.decides_wellFormed hT false) _ hρ,
    VE.Norms.decides_denote, VE.Norms.decides_denote]

/-- W1's outcome formula on a valid document is the completed outcome of its canonical interpretation. -/
theorem outcome_canon_doc {S : VE.Norms.Doc} (hv : VE.Norms.Valid S) (B : VE.Structure.{u})
    (hc : ConstantsTyped S B) {r : Regulated} (hr : r ∈ S.T.regulated) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) :
    (VE.Norms.outcomeBase S r.name).denote B (tupleVal vs) ↔
      (if r.allowByDefault then ¬ VE.Norms.DecidesD S.T (canon S B) (tupleVal vs) r.name false
       else VE.Norms.DecidesD S.T (canon S B) (tupleVal vs) r.name true) := by
  have hk := VE.Norms.index_before hv hr
  have hT := VE.Norms.rulesTyped_of_valid hv hk
  have hρ := VE.Norms.tupleVal_typed B _ vs hvs
  simp only [VE.Norms.outcomeBase, VE.Norms.find_regulated hv hk]
  rw [VE.SoftNorms.canon_subst hv B hc _ _ _ (VE.Norms.outcome_wellFormed hT) _ hρ, VE.Norms.outcome_denote,
    VE.Norms.pos, VE.Norms.neg, VE.Norms.decides_denote, VE.Norms.decides_denote]

/-- A selectable rule's selection on the filled tree is typed over the act's sorts at the top of the order. -/
theorem fillSelects_typed {N : NDoc} {X : RightsDoc} (hv : VE.Norms.Valid (VE.NormDefaults.fill (asU N X)))
    {r : Regulated} (hr : r ∈ X.soft.T.regulated) {K : SoftNode} (hK : K ∈ (correlate X).T.nodes)
    (hp : K.pred = r.name) :
    (VE.Norms.selects (VE.NormDefaults.fill (asU N X)).T (VE.Norms.fuel (VE.NormDefaults.fill (asU N X)).T)
      (VE.SoftNorms.primeNode (correlate X) K)).WellFormed
      (envAt (VE.NormDefaults.fill (asU N X)) (size (VE.NormDefaults.fill (asU N X)))) r.sorts.reverse := by
  have hk := VE.Norms.index_before hv (show r ∈ (VE.NormDefaults.fill (asU N X)).T.regulated from hr)
  have hT := VE.Norms.rulesTyped_of_valid hv hk
  have hpn : VE.NormDefaults.fillRoot (asU N X) (VE.SoftNorms.primeNode (correlate X) K) ∈
      (VE.NormDefaults.fill (asU N X)).T.nodes :=
    VE.NormDefaults.mem_fill_nodes.mpr (Or.inl ⟨_, List.mem_map_of_mem hK, rfl⟩)
  have hg := hT _ hpn (by rw [VE.NormDefaults.fillRoot_pred]; exact hp)
  rw [VE.NormDefaults.fillRoot_guard, VE.NormDefaults.fillRoot_carveOuts] at hg
  have hle : VE.Norms.before (VE.NormDefaults.fill (asU N X)) r.name ≤ size (VE.NormDefaults.fill (asU N X)) :=
    Nat.le_of_lt (List.getElem?_eq_some_iff.mp hk).1
  exact VE.Norms.envAt_mono hle _ _ (selects_wellFormed_of hT _ _ hg hp)

/-- The finite evaluation on a filled side is the W1 semantics of the filled tree, on an admissible base and a
    typed probe. -/
theorem observeOn_sideOfS_sound {α : Type} [DecidableEq α] (N : NDoc) (X : RightsDoc × List VE.Formula)
    (hw : VE.NormDefaults.WellFormedU (asU N X.1) = true)
    (hA : ∀ a ∈ X.2, a.WellFormed (envAt (VE.NormDefaults.fill (asU N X.1))
      (VE.Norms.size (VE.NormDefaults.fill (asU N X.1)))) [])
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (VE.NormDefaults.fill (asU N X.1)) 0))
    (hb : VE.Norms.backgroundValid (VE.NormDefaults.fill (asU N X.1)) M = true)
    (q : Probe α) (hq : probeTyped X.1 M q = true) (v : Bool) :
    observeOn (sideOfS N X) M q = some v ↔ ObservesF N X.1 X.2 M.asStructure q v := by
  have hv : VE.Norms.Valid (VE.NormDefaults.fill (asU N X.1)) :=
    VE.Norms.valid_of_wellFormed _ (VE.NormDefaults.fill_wellFormed _ hw)
  have hc : ConstantsTyped (VE.NormDefaults.fill (asU N X.1)) M.asStructure :=
    (VE.Norms.baseAdmissible_of_valid _ M valid hb).1.1
  cases q with
  | outcome p vs =>
    simp only [probeTyped, Bool.and_eq_true, List.any_eq_true, beq_iff_eq] at hq
    obtain ⟨⟨r, hr, rfl⟩, ht⟩ := hq
    have hrf : r ∈ (VE.NormDefaults.fill (asU N X.1)).T.regulated := hr
    have hk := VE.Norms.index_before hv hrf
    have hfind : (correlate X.1).T.regulated.find? (·.name == r.name) = some r := VE.Norms.find_regulated hv hk
    have hs : VE.SoftNorms.sortsIn X.1.soft.T.regulated r.name = r.sorts := by
      simp [VE.SoftNorms.sortsIn, show X.1.soft.T.regulated.find? (·.name == r.name) = some r from hfind]
    rw [hs, typedTuple_iff] at ht
    have hcf := conflict_canon_doc hv _ hc hrf vs ht
    have ho := outcome_canon_doc hv _ hc hrf vs ht
    rw [← VE.eval_iff_denote] at hcf ho
    simp only [observeOn, sideOfS, VE.Norms.conflictIn_eq, VE.Norms.outcomeBaseIn_eq, hfind]
    constructor
    · intro hobs
      refine ⟨r, hr, rfl, ht, ?_⟩
      unfold VE.Norms.Value
      rw [catalaValue_eq]
      split at hobs
      · cases hobs
      · rename_i hcon
        cases hobs
        exact ⟨fun hpn => hcon (hcf.mpr hpn), ho.symm⟩
    · rintro ⟨r', hr'', hn, _, hval⟩
      have : r' = r := by
        have hf' := VE.Norms.find_regulated hv (VE.Norms.index_before hv
          (show r' ∈ (VE.NormDefaults.fill (asU N X.1)).T.regulated from hr''))
        rw [hn] at hf'
        exact Option.some.inj (hf'.symm.trans hfind)
      subst this
      unfold VE.Norms.Value at hval
      rw [catalaValue_eq] at hval
      rw [if_neg (fun hcon => hval.1 (hcf.mp hcon))]
      congr 1
      have h2 := hval.2
      cases hov : (VE.Norms.outcomeBase (VE.NormDefaults.fill (asU N X.1)) r'.name).eval M (tupleVal vs) <;>
        cases v
      · rfl
      · exact absurd (ho.mpr (h2.mpr rfl)) (by simp [hov])
      · exact absurd (h2.mp (ho.mp hov)) (by simp)
      · rfl
  | selects k p vs =>
    simp only [probeTyped, Bool.and_eq_true, List.any_eq_true, beq_iff_eq] at hq
    obtain ⟨⟨_, r, hr, rfl⟩, ht⟩ := hq
    have hrf : r ∈ (VE.NormDefaults.fill (asU N X.1)).T.regulated := hr
    have hk := VE.Norms.index_before hv hrf
    have hfind : (correlate X.1).T.regulated.find? (·.name == r.name) = some r := VE.Norms.find_regulated hv hk
    have hs : VE.SoftNorms.sortsIn X.1.soft.T.regulated r.name = r.sorts := by
      simp [VE.SoftNorms.sortsIn, show X.1.soft.T.regulated.find? (·.name == r.name) = some r from hfind]
    rw [hs, typedTuple_iff] at ht
    have hsel : ∀ K ∈ selectable X.1 k r.name,
        (VE.Norms.substIn (sideOfS N X).L (sideOfS N X).L.syms.length
          (VE.SoftNorms.selectsOn (sideOfS N X).S (correlate (sideOfS N X).X) K)).eval M (tupleVal vs) = true ↔
        VE.Norms.SelectsD (VE.NormDefaults.fill (asU N X.1)).T (canon (VE.NormDefaults.fill (asU N X.1))
          M.asStructure) (tupleVal vs) (VE.Norms.fuel (VE.NormDefaults.fill (asU N X.1)).T)
          (VE.SoftNorms.primeNode (correlate X.1) K) := by
      intro K hK
      obtain ⟨hK', hp⟩ := selectable_mem hK
      have e : (VE.Norms.syms (VE.NormDefaults.fill (asU N X.1)).T).length = size (VE.NormDefaults.fill (asU N X.1)) :=
        rfl
      simp only [sideOfS, VE.Norms.substIn_eq, VE.Norms.layersOf_syms, VE.SoftNorms.selectsOn, e]
      rw [VE.eval_iff_denote, VE.SoftNorms.canon_subst hv _ hc _ _ _ (fillSelects_typed hv hr hK' hp) _
        (VE.Norms.tupleVal_typed _ _ vs ht), VE.Norms.selects_denote]
    have hso : VE.SoftNorms.sortsOf (correlate X.1) r.name = r.sorts := hs
    simp only [observeOn, ObservesF, Option.some.injEq, hso]
    constructor
    · rintro rfl
      refine ⟨ht, ?_⟩
      rw [List.any_eq_true]
      exact ⟨fun ⟨K, hK, hs⟩ => ⟨K, hK, (hsel K hK).mpr hs⟩, fun ⟨K, hK, hs⟩ => ⟨K, hK, (hsel K hK).mp hs⟩⟩
    · rintro ⟨_, hiff⟩
      cases hany : (selectable (sideOfS N X).X k r.name).any (fun K =>
          (VE.Norms.substIn (sideOfS N X).L (sideOfS N X).L.syms.length
            (VE.SoftNorms.selectsOn (sideOfS N X).S (correlate (sideOfS N X).X) K)).eval M (tupleVal vs))
      · cases v
        · rfl
        · exfalso
          obtain ⟨K, hK, hs⟩ := hiff.mpr rfl
          have := (hsel K hK).mpr hs
          rw [List.any_eq_false] at hany
          exact hany K hK (by simp [this])
      · rw [List.any_eq_true] at hany
        obtain ⟨K, hK, hs⟩ := hany
        exact (hiff.mp ⟨K, hK, (hsel K hK).mp hs⟩).symm
  | holds =>
    have hh : ∀ a ∈ X.2, (VE.Norms.substIn (sideOfS N X).L (sideOfS N X).L.syms.length a).eval M [] = true ↔
        a.denote (canon (VE.NormDefaults.fill (asU N X.1)) M.asStructure) [] := by
      intro a ha
      simp only [sideOfS, VE.Norms.substIn_eq, VE.Norms.layersOf_syms]
      rw [VE.eval_iff_denote]
      exact VE.SoftNorms.canon_subst hv _ hc _ a [] (hA a ha) [] (VE.typed_empty _)
    simp only [observeOn, ObservesF, Option.some.injEq]
    constructor
    · rintro rfl
      rw [List.all_eq_true]
      exact ⟨fun h a ha => (hh a ha).mpr (h a (by simpa [sideOfS] using ha)),
        fun h a ha => (hh a (by simpa [sideOfS] using ha)).mp (h a (by simpa [sideOfS] using ha))⟩
    · intro hiff
      cases hall : (sideOfS N X).A.all (fun a => (VE.Norms.substIn (sideOfS N X).L (sideOfS N X).L.syms.length
          a).eval M [])
      · cases v
        · rfl
        · exfalso
          have h' := hiff.mpr rfl
          rw [List.all_eq_false] at hall
          obtain ⟨a, ha, hf⟩ := hall
          exact hf ((hh a ha).mpr (h' a ha))
      · rw [List.all_eq_true] at hall
        exact (hiff.mp (fun a ha => (hh a ha).mp (hall a ha))).symm

/-! ## Proofs: the filled author vocabulary -/

/-- `WellFormedSD`, unpacked for one reading with content. -/
theorem wellFormedSD_doc {N : NDoc} (hN : WellFormedSD N = true) :
    WellFormedDoc N.D = true ∧ softShaped N.D = true ∧ fillNamesFree N = true := by
  simp only [WellFormedSD, Bool.and_eq_true] at hN
  exact ⟨hN.1.1.1.1, hN.1.1.1.2, hN.1.1.2⟩

theorem wellFormedSD_one {N : NDoc} (hN : WellFormedSD N = true) {s : String} {i : Nat}
    (hi : (candidate N.D s i).bind (·.content) ≠ none) : VE.NormDefaults.WellFormedU (oneU N s i) = true := by
  simp only [WellFormedSD, Bool.and_eq_true, List.all_eq_true, List.mem_range, Bool.or_eq_true,
    Option.isNone_iff_eq_none] at hN
  unfold candidate at hi
  cases hR : N.D.sets.find? (·.id == s) with
  | none => rw [hR] at hi; exact absurd rfl hi
  | some R =>
    rw [hR] at hi
    have hRs : R.id = s := by simpa using List.find?_some hR
    simp only [Option.bind_some] at hi
    cases ha : R.candidates[i]? with
    | none => rw [ha] at hi; exact absurd rfl hi
    | some a =>
      have hlt : i < R.candidates.length := (List.getElem?_eq_some_iff.mp ha).1
      rcases hN.2 R (List.mem_of_find?_eq_some hR) i hlt with h | h
      · rw [ha] at hi h; exact absurd h hi
      · rw [← hRs]; exact h

/-- A reading's document on the soft chain has no rights content and a well-formed soft document, and its
    assertions are typed over its elaborated vocabulary. -/
theorem sideWF_soft {N : NDoc} (hN : WellFormedSD N = true) {s : String} {i : Nat}
    (hi : (candidate N.D s i).bind (·.content) ≠ none) :
    noRights (one N.D s i).1 = true ∧ VE.SoftNorms.WellFormedSoft (correlate (one N.D s i).1) = true ∧
    ∀ a ∈ (one N.D s i).2, a.WellFormed (envAt (VE.NormDefaults.fill (oneU N s i))
      (size (VE.NormDefaults.fill (oneU N s i)))) [] := by
  obtain ⟨hD, hs, _⟩ := wellFormedSD_doc hN
  have hw := sideWF_one N.D hD hi
  have hc : N.D.chain = .soft := by
    simp only [softShaped, Bool.and_eq_true, beq_iff_eq] at hs; exact hs.1.1.1
  simp only [sideWF, Bool.and_eq_true, List.all_eq_true, hc] at hw
  have hcw := hw.1
  simp only [chainWF, Bool.and_eq_true] at hcw
  have hu := VE.NormDefaults.uvalid (wellFormedSD_one hN hi)
  refine ⟨hcw.1.1, chain_soft .soft _ hw.1, fun a ha => ?_⟩
  have h := (VE.check_iff_wellFormed _ _ _).mp (hw.2 a ha)
  have e : size (VE.NormDefaults.fill (oneU N s i)) = size (oneU N s i).D := VE.NormDefaults.size_fill hu
  rw [e]
  exact VE.Norms.wf_mono (E := envAt (oneU N s i).D (size (oneU N s i).D))
    (E' := envAt (VE.NormDefaults.fill (oneU N s i)) (size (oneU N s i).D)) rfl rfl
    (VE.NormDefaults.envAt_fill_mono hu _) a [] h

theorem filledAuthorEnv_predicates (N : NDoc) (p : String) :
    (filledAuthorEnv N).predicates p =
      if p ∈ VE.Norms.layerNames N.D.frame.soft.base.T then none else (fillFrameEnv N).predicates p := rfl

theorem authorEnv_predicates (D : Doc) (p : String) :
    (authorEnv D).predicates p =
      if p ∈ VE.Norms.layerNames D.frame.soft.base.T then none else D.frame.soft.E.predicates p := rfl

/-- Outside the generated names, the filled tree's base vocabulary is the filled author vocabulary. -/
theorem envAt_filledAuthor (N : NDoc) (X : RightsDoc) (hX : KeepsFrame N.D X)
    (hw : VE.NormDefaults.WellFormedU (asU N X) = true) {p : String} {ss : List String}
    (hg : (genKeys X).find? (·.2.1 == p) = none) (ha : (filledAuthorEnv N).predicates p = some ss) :
    (envAt (VE.NormDefaults.fill (asU N X)) 0).predicates p = some ss := by
  have hu := VE.NormDefaults.uvalid hw
  rw [filledAuthorEnv_predicates] at ha
  split at ha
  · cases ha
  · rename_i hnl
    simp only [fillFrameEnv] at ha
    cases hf : N.unspec.find? (fun q => VE.NormDefaults.unsaidName q == p) with
    | some q =>
      rw [hf] at ha
      cases ha
      have hq : q ∈ N.unspec := List.mem_of_find?_eq_some hf
      have hqp : VE.NormDefaults.unsaidName q = p := by simpa using List.find?_some hf
      rw [← hqp, VE.NormDefaults.envAt_fill_unsaid hu 0 hq]
      show some (((X.soft.T.regulated.find? (·.name == q)).map (·.sorts)).getD []) = _
      rw [hX.regulated]
      rfl
    | none =>
      rw [hf] at ha
      have hA : (authorEnv N.D).predicates p = some ss := by
        rw [authorEnv_predicates, if_neg hnl]; exact ha
      exact VE.NormDefaults.envAt_fill_mono hu 0 _ _ (envAt_author N.D X hX hg hA)

theorem envAt_filled_constants (N : NDoc) (X : RightsDoc) (hX : KeepsFrame N.D X) :
    (envAt (VE.NormDefaults.fill (asU N X)) 0).constants = (filledAuthorEnv N).constants :=
  envAt_constants N.D X hX

/-- A filled side's finite model is valid over the filled tree's base vocabulary: the base is valid over the filled
    author vocabulary, and the tables are typed. -/
theorem valid_tablesModelS {α : Type} [DecidableEq α] (N : NDoc) (X : RightsDoc × List VE.Formula)
    (hX : KeepsFrame N.D X.1) (hw : VE.NormDefaults.WellFormedU (asU N X.1) = true)
    (M : VE.FiniteModel α) (valid : M.Valid (filledAuthorEnv N)) (T : List (GenKey × List (List α)))
    (ht : tablesTypedOn (sideOfS N X) M T = true) :
    (tablesModel X.1 M T).Valid (envAt (VE.NormDefaults.fill (asU N X.1)) 0) := by
  refine ⟨fun c s hc => ?_, fun p vs hvs => ?_⟩
  · rw [envAt_filled_constants N X.1 hX] at hc
    exact valid.1 c s hc
  · change vs ∈ (tablesModel X.1 M T).relations p at hvs
    simp only [tablesModel] at hvs
    split at hvs
    · rename_i g hg
      obtain ⟨hgm, hgp⟩ := find_name hg
      obtain ⟨t, htT, htk, hvt⟩ := mem_tableOf hvs
      simp only [tablesTypedOn, List.all_eq_true, Bool.and_eq_true, Bool.or_eq_true, bne_iff_ne, ne_eq] at ht
      have := (ht t htT).2 vs hvt g hgm
      have hk : ((sideOfS N X).keys.find? (·.2.1 == g.2.1)).map (·.1) = some t.1 := by
        show ((genKeys X.1).find? (·.2.1 == g.2.1)).map (·.1) = some t.1
        rw [hgp, hg, htk]; rfl
      rw [hk] at this
      simp only [not_true_eq_false, false_or] at this
      unfold declaredTypedOn at this
      rw [sideOfS_E0, hgp] at this
      split at this
      · rename_i ss hss
        exact ⟨ss, hss, (tupleTyped_tablesModel X.1 M T ss vs).mpr ((typedTuple_iff M ss vs).mp this)⟩
      · cases this
    · rename_i hg
      obtain ⟨ss, hss, hty⟩ := valid.2 p vs hvs
      exact ⟨ss, envAt_filledAuthor N X.1 hX hw hg hss, (tupleTyped_tablesModel X.1 M T ss vs).mpr hty⟩

/-- S1's table check, which reads the elaborated vocabulary, gives the filled side's, which reads the filled
    tree's: the generated names keep their declarations. -/
theorem tablesTypedOn_of_tablesTyped {α : Type} [DecidableEq α] (N : NDoc) (X : RightsDoc × List VE.Formula)
    (hw : VE.NormDefaults.WellFormedU (asU N X.1) = true) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) (h : tablesTyped X.1 M T = true) :
    tablesTypedOn (sideOfS N X) M T = true := by
  have hu := VE.NormDefaults.uvalid hw
  simp only [tablesTyped, tablesTypedOn, List.all_eq_true, Bool.and_eq_true, Bool.or_eq_true, bne_iff_ne,
    ne_eq] at h ⊢
  intro t ht
  refine ⟨(h t ht).1, fun vs hvs g hg => ?_⟩
  rcases (h t ht).2 vs hvs g hg with h' | h'
  · exact Or.inl h'
  · right
    unfold declaredTyped at h'
    unfold declaredTypedOn
    rw [sideOfS_E0]
    split at h'
    · rename_i ss hss
      rw [VE.NormDefaults.envAt_fill_mono hu 0 _ _ hss]
      exact h'
    · cases h'

/-! ## Proofs: `pairEval`'s first component on any two sides -/

theorem pairEval_fst {α : Type} [DecidableEq α] (D : Doc) (s : String) (i j : Nat) (Pi Pj : Side)
    (σ : Situation α) :
    (pairEval (m := Id) (pure ()) (pure ()) D s i j Pi Pj σ).1 =
      ((situationWFOf D s i j Pi.X Pj.X σ && sideValidOn Pi σ.base (tablesForOf Pi.X (σ.fixed ++ σ.decisions)) &&
        sideValueOn Pi σ.base (tablesForOf Pi.X (σ.fixed ++ σ.decisions)) σ.probe == some σ.value) &&
      (assignmentsOn D s j Pj σ.base).all (fun G =>
        !(sideValidOn Pj σ.base (tablesForOf Pj.X σ.fixed ++ G) &&
          sideValueOn Pj σ.base (tablesForOf Pj.X σ.fixed ++ G) σ.probe == some σ.value))) := by
  unfold pairEval
  by_cases ho : ownedKeysOn D s j Pj = []
  · have ha : assignmentsOn D s j Pj σ.base = [[]] := by unfold assignmentsOn; rw [ho]; rfl
    simp only [ho, if_true, ha, List.all_cons, List.all_nil, List.append_nil, Bool.and_true]
    rfl
  · simp only [ho, if_false]
    rw [otherScanOn_id]
    simp only [bind, pure, and_not_and_any]

/-! ## Proofs: `separatesS_sound` -/

theorem observesF_rel {N : NDoc} {X : RightsDoc} {A : List VE.Formula} {α : Type u} {d : String → α → Prop}
    {c : String → Option α} {R1 R2 : String → List α → Prop} (h : R1 = R2) (q : Probe α) (v : Bool)
    (ho : ObservesF N X A ⟨α, d, c, R1⟩ q v) : ObservesF N X A ⟨α, d, c, R2⟩ q v := by
  subst h; exact ho

/-- The witness side of `separatesS_sound`. -/
theorem separatesS_witness {α : Type} [DecidableEq α] (N : NDoc) (hN : WellFormedSD N = true) (s : String)
    (i : Nat) (hi : (candidate N.D s i).bind (·.content) ≠ none) (σ : Situation α)
    (valid : σ.base.Valid (filledAuthorEnv N))
    (hnd : ((σ.fixed ++ σ.decisions).map (·.1)).Nodup)
    (hdec : ∀ t ∈ σ.decisions, owned N.D s i t.1 = true)
    (hpt : probeTyped (one N.D s i).1 σ.base σ.probe = true)
    (hsvi : sideValidOn (sideOfS N (one N.D s i)) σ.base (tablesFor N.D s i (σ.fixed ++ σ.decisions)) = true)
    (hvi : sideValueOn (sideOfS N (one N.D s i)) σ.base (tablesFor N.D s i (σ.fixed ++ σ.decisions)) σ.probe =
      some σ.value)
    (hfill : fillHoldsS N s i σ.base (tablesFor N.D s i (σ.fixed ++ σ.decisions)) = true) :
    AchievesS N s i σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value := by
  obtain ⟨hnr, _, hAi⟩ := sideWF_soft hN hi
  have hw := wellFormedSD_one hN hi
  obtain ⟨htt, hbg, hsoft⟩ := (sideValidOn_sideOfS_iff N (one N.D s i) hnr _ _).mp hsvi
  rw [tablesModelOn_sideOfS] at hbg hsoft
  have hvalT := valid_tablesModelS N (one N.D s i) (keepsFrame_one N.D s i) hw σ.base valid _ htt
  have hGi : ∀ g ∈ genKeys (one N.D s i).1, ∀ vs,
      vs ∈ tableOf (tablesFor N.D s i (σ.fixed ++ σ.decisions)) g.1 ↔ tablesOf (σ.fixed ++ σ.decisions) g.1 vs := by
    intro g hg vs
    have hk : (genKeys (one N.D s i).1).any (·.1 == g.1) = true := List.any_eq_true.mpr ⟨g, hg, by simp⟩
    rw [tablesFor_generated N.D s i _ g.1 hk]
    exact mem_tableOf_iff hnd g.1 vs
  have hreli := tablesModel_rel (one N.D s i).1 σ.base _ _ (fun p g hg vs => hGi g (find_name hg).1 vs)
  have hpti : probeTyped (one N.D s i).1 (tablesModel (one N.D s i).1 σ.base
      (tablesFor N.D s i (σ.fixed ++ σ.decisions))) σ.probe = true :=
    (probeTyped_congr (X := (one N.D s i).1) (Y := (one N.D s i).1)
      (M := tablesModel (one N.D s i).1 σ.base (tablesFor N.D s i (σ.fixed ++ σ.decisions))) (M' := σ.base)
      rfl rfl σ.probe).trans hpt
  have hobs := (observeOn_sideOfS_sound N (one N.D s i) hw hAi _ hvalT hbg σ.probe hpti σ.value).mp hvi
  have hB : VE.NormDefaults.Wire.BaseAdmissibleX (oneU N s i) (oneX N s i)
      (tablesModel (one N.D s i).1 σ.base (tablesFor N.D s i (σ.fixed ++ σ.decisions))).asStructure := by
    refine ⟨⟨VE.Norms.baseAdmissible_of_valid _ _ hvalT hbg, fun a ha => ?_⟩, fun a ha => ?_⟩
    · exact (VE.eval_iff_denote (tablesModel (one N.D s i).1 σ.base (tablesFor N.D s i (σ.fixed ++ σ.decisions)))
        [] a).mp (List.all_eq_true.mp hfill a ha)
    · exact (VE.eval_iff_denote (tablesModel (one N.D s i).1 σ.base (tablesFor N.D s i (σ.fixed ++ σ.decisions)))
        [] a).mp (hsoft a (by simpa only [oneX] using ha))
  have e : (tablesModel (one N.D s i).1 σ.base (tablesFor N.D s i (σ.fixed ++ σ.decisions))).asStructure =
      withTables (one N.D s i).1 σ.base.asStructure (tablesOf (σ.fixed ++ σ.decisions)) := by
    simp only [VE.FiniteModel.asStructure, withTables]
    congr 1
  refine ⟨valid, tablesOf (σ.fixed ++ σ.decisions), ?_, by rw [← e]; exact hB,
    observesF_rel hreli σ.probe σ.value hobs⟩
  intro k hk vs
  simp only [tablesOf, List.mem_append]
  constructor
  · rintro ⟨t, ht | ht, rfl, hv⟩
    · exact ⟨t, ht, rfl, hv⟩
    · rw [hdec t ht] at hk; cases hk
  · rintro ⟨t, ht, rfl, hv⟩; exact ⟨t, Or.inl ht, rfl, hv⟩

/-- On an enumerated assignment whose finite model is admissible and observes the value, the scan finds it. -/
theorem otherShowsS {α : Type} [DecidableEq α] (N : NDoc) (s : String) (i j : Nat) (σ : Situation α)
    (hnr : noRights (one N.D s j).1 = true)
    (hAj : ∀ a ∈ (one N.D s j).2, a.WellFormed (envAt (VE.NormDefaults.fill (oneU N s j))
      (size (VE.NormDefaults.fill (oneU N s j)))) [])
    (hw : VE.NormDefaults.WellFormedU (oneU N s j) = true)
    (htyj : tablesTypedOn (sideOfS N (one N.D s j)) σ.base (tablesFor N.D s j σ.fixed) = true)
    (hpt : probeTyped (one N.D s i).1 σ.base σ.probe = true)
    (hall : ∀ G ∈ assignmentsOn N.D s j (sideOfS N (one N.D s j)) σ.base,
      (sideValidOn (sideOfS N (one N.D s j)) σ.base (tablesFor N.D s j σ.fixed ++ G) &&
        sideValueOn (sideOfS N (one N.D s j)) σ.base (tablesFor N.D s j σ.fixed ++ G) σ.probe == some σ.value) =
        false)
    (G' : List (GenKey × List (List α))) (hG'mem : G' ∈ assignmentsOn N.D s j (sideOfS N (one N.D s j)) σ.base)
    (htyG' : tablesTypedOn (sideOfS N (one N.D s j)) σ.base G' = true)
    (hBA' : VE.NormDefaults.Wire.BaseAdmissibleX (oneU N s j) (oneX N s j)
      (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G')).asStructure)
    (hobsj : ObservesF N (one N.D s j).1 (one N.D s j).2
      (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G')).asStructure σ.probe σ.value) :
    False := by
  have hvalj : (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G')).Valid
      (envAt (VE.NormDefaults.fill (oneU N s j)) 0) := hBA'.1.1.1
  have hbgj : VE.Norms.backgroundValid (VE.NormDefaults.fill (oneU N s j))
      (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G')) = true :=
    List.all_eq_true.mpr (fun a ha => (VE.eval_iff_denote
      (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G')) [] a).mpr (hBA'.1.1.2 a ha))
  have hsoftj : ∀ a ∈ softX N (one N.D s j).1,
      a.eval (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G')) [] = true :=
    fun a ha => (VE.eval_iff_denote
      (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G')) [] a).mpr (hBA'.2 a ha)
  have htyT' : tablesTypedOn (sideOfS N (one N.D s j)) σ.base (tablesFor N.D s j σ.fixed ++ G') = true := by
    simp only [tablesTypedOn, List.all_append, Bool.and_eq_true] at htyj htyG' ⊢
    exact ⟨htyj, htyG'⟩
  have hsvj : sideValidOn (sideOfS N (one N.D s j)) σ.base (tablesFor N.D s j σ.fixed ++ G') = true :=
    (sideValidOn_sideOfS_iff N (one N.D s j) hnr _ _).mpr ⟨htyT', hbgj, hsoftj⟩
  have hd : (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G')).domains = σ.base.domains := rfl
  have hr : (one N.D s j).1.soft.T.regulated = (one N.D s i).1.soft.T.regulated := by
    rw [(keepsFrame_one N.D s j).regulated, (keepsFrame_one N.D s i).regulated]
  have hptj : probeTyped (one N.D s j).1 (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G'))
      σ.probe = true := (probeTyped_congr hr hd σ.probe).trans hpt
  have hsvalj := (observeOn_sideOfS_sound N (one N.D s j) hw hAj _ hvalj hbgj σ.probe hptj σ.value).mpr hobsj
  have := hall G' hG'mem
  have hv' : sideValueOn (sideOfS N (one N.D s j)) σ.base (tablesFor N.D s j σ.fixed ++ G') σ.probe =
      some σ.value := hsvalj
  rw [hsvj, hv'] at this
  simp at this

/-- The other reading's completion `G`, as one of the enumerated assignments: its finite model is the completion, and
    its tables are typed. -/
theorem otherAssignmentS {α : Type} [DecidableEq α] (N : NDoc) (s : String) (j : Nat) (σ : Situation α)
    (hndf : (σ.fixed.map (·.1)).Nodup)
    (hfx : ∀ t ∈ σ.fixed, owned N.D s j t.1 = false)
    (G : Tables σ.base.asStructure.Carrier)
    (hagree : ∀ k, owned N.D s j k = false → ∀ vs, G k vs ↔ tablesOf σ.fixed k vs)
    (hadm : (withTables (one N.D s j).1 σ.base.asStructure G).Admissible
      (envAt (VE.NormDefaults.fill (oneU N s j)) 0)) :
    ∃ G' ∈ assignmentsOn N.D s j (sideOfS N (one N.D s j)) σ.base,
      (fun p vs => vs ∈ (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G')).relations p) =
        (fun p vs => match (genKeys (one N.D s j).1).find? (·.2.1 == p) with
          | some g => G g.1 vs
          | none => vs ∈ σ.base.relations p) ∧
      tablesTypedOn (sideOfS N (one N.D s j)) σ.base G' = true := by
  classical
  have htyp : ∀ p g, (genKeys (one N.D s j).1).find? (·.2.1 == p) = some g → ∀ vs, G g.1 vs →
      ∃ ss, (envAt (VE.NormDefaults.fill (asU N (one N.D s j).1)) 0).predicates p = some ss ∧
        VE.TupleTyped σ.base.asStructure ss vs := by
    intro p g hg vs hv
    have hrel : (withTables (one N.D s j).1 σ.base.asStructure G).relation p vs := by
      simp only [withTables, hg]; exact hv
    obtain ⟨ss, hss, ht⟩ := hadm.2 p vs hrel
    exact ⟨ss, hss, (tupleTyped_withTables ss vs).mp ht⟩
  obtain ⟨G', hG'⟩ : ∃ G' : List (GenKey × List (List α)), G' =
      (ownedKeysOn N.D s j (sideOfS N (one N.D s j))).map (fun k =>
        (k, (keyTuplesOn (sideOfS N (one N.D s j)) σ.base k).filter (fun vs => decide (G k vs)))) := ⟨_, rfl⟩
  refine ⟨G', by rw [hG']; exact mem_assignments_foldr _ _ _, tablesModel_rel _ _ _ _ ?_, ?_⟩
  · intro p g hg vs
    have hgm := find_name hg
    have hk : (genKeys (one N.D s j).1).any (·.1 == g.1) = true := List.any_eq_true.mpr ⟨g, hgm.1, by simp⟩
    by_cases ho : owned N.D s j g.1 = true
    · rw [tableOf_append_of_not g.1 _ _ (fun t ht e => by
          have := hfx t (List.mem_filter.mp ht).1; rw [e, ho] at this; cases this)]
      rw [hG', tableOf_map_keys (fun k => (keyTuplesOn (sideOfS N (one N.D s j)) σ.base k).filter
        (fun vs => decide (G k vs))) g.1]
      have hmem : g.1 ∈ ownedKeysOn N.D s j (sideOfS N (one N.D s j)) :=
        List.mem_filter.mpr ⟨List.mem_map_of_mem hgm.1, ho⟩
      rw [if_pos hmem, List.mem_filter, decide_eq_true_eq]
      refine ⟨fun h => h.2, fun hv => ⟨?_, hv⟩⟩
      obtain ⟨ss, hss, ht⟩ := htyp p g hg vs hv
      rw [keyTuplesOn, mem_uniq, List.mem_flatMap]
      refine ⟨g, hgm.1, ?_⟩
      have hkey : (((sideOfS N (one N.D s j)).keys.find? (·.2.1 == g.2.1)).map (·.1)) = some g.1 := by
        show ((genKeys (one N.D s j).1).find? (·.2.1 == g.2.1)).map (·.1) = some g.1
        rw [hgm.2, hg]; rfl
      have hE : (sideOfS N (one N.D s j)).E0.predicates g.2.1 = some ss := by
        rw [sideOfS_E0, hgm.2]; exact hss
      simp only [hkey, beq_self_eq_true, if_true, hE]
      exact (mem_tuplesOf σ.base ss vs).mpr ht
    · have ho' : owned N.D s j g.1 = false := by simpa using ho
      rw [tableOf_append_right_not g.1 _ _ (fun t ht e => by
          rw [hG'] at ht
          obtain ⟨k, hk', rfl⟩ := List.mem_map.mp ht
          have := (List.mem_filter.mp hk').2
          simp only at e; rw [e, ho'] at this; cases this),
        tablesFor_generated N.D s j _ g.1 hk, mem_tableOf_iff hndf]
      exact (hagree g.1 ho' vs).symm
  · simp only [tablesTypedOn, List.all_eq_true, Bool.and_eq_true, Bool.or_eq_true, bne_iff_ne, ne_eq]
    intro t ht
    rw [hG'] at ht
    obtain ⟨k, hk, rfl⟩ := List.mem_map.mp ht
    obtain ⟨hk1, _⟩ := List.mem_filter.mp hk
    obtain ⟨g0, hg0, hg0k⟩ := List.mem_map.mp hk1
    refine ⟨List.any_eq_true.mpr ⟨g0, hg0, by simp [hg0k]⟩, fun vs hvs g'' _ => ?_⟩
    obtain ⟨_, hv⟩ := List.mem_filter.mp hvs
    rw [decide_eq_true_eq] at hv
    by_cases hkn : (((sideOfS N (one N.D s j)).keys.find? (·.2.1 == g''.2.1)).map (·.1)) = some k
    · right
      obtain ⟨g3, hg3, hg3k⟩ := Option.map_eq_some_iff.mp hkn
      obtain ⟨ss, hss, ht⟩ := htyp g''.2.1 g3 hg3 vs (hg3k ▸ hv)
      unfold declaredTypedOn
      rw [sideOfS_E0, hss]
      exact (typedTuple_iff σ.base ss vs).mpr ht
    · exact Or.inl hkn

/-- The other side of `separatesS_sound`: a completion of `j` with the recorded value is one of the enumerated
    assignments, and on it the filled side is valid and shows the value. -/
theorem separatesS_other {α : Type} [DecidableEq α] (N : NDoc) (hN : WellFormedSD N = true) (s : String)
    (i j : Nat) (hj : (candidate N.D s j).bind (·.content) ≠ none) (σ : Situation α)
    (hndf : (σ.fixed.map (·.1)).Nodup)
    (hfx : ∀ t ∈ σ.fixed, owned N.D s j t.1 = false)
    (htyj : tablesTypedOn (sideOfS N (one N.D s j)) σ.base (tablesFor N.D s j σ.fixed) = true)
    (hpt : probeTyped (one N.D s i).1 σ.base σ.probe = true)
    (hall : ∀ G ∈ assignmentsOn N.D s j (sideOfS N (one N.D s j)) σ.base,
      (sideValidOn (sideOfS N (one N.D s j)) σ.base (tablesFor N.D s j σ.fixed ++ G) &&
        sideValueOn (sideOfS N (one N.D s j)) σ.base (tablesFor N.D s j σ.fixed ++ G) σ.probe == some σ.value) =
        false) :
    ¬ AchievesS N s j σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value := by
  obtain ⟨hnr, _, hAj⟩ := sideWF_soft hN hj
  have hw := wellFormedSD_one hN hj
  rintro ⟨_, G, hagree, hBA, hObs⟩
  obtain ⟨G', hG'mem, hrelj, htyG'⟩ := otherAssignmentS N s j σ hndf hfx G hagree hBA.1.1.1
  have heq : (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G')).asStructure =
      withTables (one N.D s j).1 σ.base.asStructure G := by
    simp only [VE.FiniteModel.asStructure, withTables]
    congr 1
  have hBA' : VE.NormDefaults.Wire.BaseAdmissibleX (oneU N s j) (oneX N s j)
      (tablesModel (one N.D s j).1 σ.base (tablesFor N.D s j σ.fixed ++ G')).asStructure := by
    rw [heq]; exact hBA
  exact otherShowsS N s i j σ hnr hAj hw htyj hpt hall G' hG'mem htyG' hBA'
    (observesF_rel hrelj.symm σ.probe σ.value hObs)

theorem separatesS_sound {α : Type} [DecidableEq α] (N : NDoc) (hN : WellFormedSD N = true) (s : String)
    (i j : Nat) (hi : (candidate N.D s i).bind (·.content) ≠ none) (hj : (candidate N.D s j).bind (·.content) ≠ none)
    (σ : Situation α) (valid : σ.base.Valid (filledAuthorEnv N)) (h : separatesS N s i j σ = true) :
    AchievesS N s i σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value ∧
      ¬ AchievesS N s j σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value := by
  simp only [separatesS, pairEval_fst, situationWFOf, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true,
    beq_iff_eq, Bool.not_eq_true', Bool.or_eq_true] at h
  obtain ⟨⟨_, ⟨⟨⟨⟨⟨⟨⟨hnd, hfx⟩, hdec⟩, _⟩, htyj⟩, hpt⟩, hsvi⟩, hvi⟩, hall⟩, hfill⟩ := h
  have hndf : (σ.fixed.map (·.1)).Nodup := by
    rw [List.map_append] at hnd; exact (List.nodup_append.mp hnd).1
  refine ⟨separatesS_witness N hN s i hi σ valid hnd (fun t ht => (hdec t ht).1) hpt hsvi hvi hfill,
    separatesS_other N hN s i j hj σ hndf (fun t ht => (hfx t ht).1.2)
      (tablesTypedOn_of_tablesTyped N (one N.D s j) (wellFormedSD_one hN hj) _ _ htyj) hpt (fun G hG => ?_)⟩
  have := hall G hG
  simpa using this

/-- The corollary: a checked separation on filled sides proves `SeparatedS`. -/
theorem separatesS_separated {α : Type} [DecidableEq α] (N : NDoc) (hN : WellFormedSD N = true) (s : String)
    (i j : Nat) (hi : (candidate N.D s i).bind (·.content) ≠ none) (hj : (candidate N.D s j).bind (·.content) ≠ none)
    (σ : Situation α) (valid : σ.base.Valid (filledAuthorEnv N)) (h : separatesS N s i j σ = true) :
    SeparatedS.{0} N s i j :=
  ⟨σ.base.asStructure, tablesOf σ.fixed, σ.probe, σ.value,
    Or.inl (separatesS_sound N hN s i j hi hj σ valid h)⟩

end VE.Readings
