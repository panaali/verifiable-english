import VE.Readings.SoftSup
import VE.NormDefaults.PacksLabels

/-! SC-11's label mapping (docs/spec/rd-9-soft-chain.md 14.1, 14.4, 14.8): a superposed answer shows each choice's
own labels.

`labelImage N c` pairs each soft label of `c`'s document with the label of the premise it is sent to in the superposed
document: an exception label keeps its role and index under the image name `fmap N.D c`, and a coherence label is
rebuilt with the two image names ascending. `sdShown` reads the used superposed labels back as choice labels of the
compatible choices taking `A`. The label theorems say the first components are the choice's labels
(`labelImage_fst`) and the second components superposed labels (`labelImage_snd_mem`); 14.4's other three
(`labelImage_functional`, `supLabel_pull`, `supLabel_other`) are sc-11c's (docs/rd-9/sc-11/REPORT.md). -/
namespace VE.Readings
open VE.Norms (Sat)
open VE.SoftNorms (SoftNode SoftDoc)
open VE.Rights (RightsDoc correlate)
universe u

/-- One rule's exception labels (the node form of `excLabels`). -/
def nodeExcLabels (M : VE.SoftNorms.SoftNode) : List String :=
  match M.mode, M.exception with
  | .default, some e =>
    (List.range e.sufficient.length).map (fun i => s!"soft:exception:{M.name}:sufficient:{i}") ++
      (List.range e.necessary.length).map (fun i => s!"soft:exception:{M.name}:necessary:{i}")
  | _, _ => []

/-- (choice label, superposed label) of each soft premise of `c`'s document. -/
def labelImage (N : NDoc) (c : Choice) : List (String × String) :=
  let Y := (choiceDoc N.D c).1.soft
  Y.T.nodes.flatMap (fun M => (nodeExcLabels M).zip (nodeExcLabels (fmap N.D c M))) ++
    (VE.SoftNorms.collidingPairs Y).map (fun x =>
      let a := fmap N.D c x.1
      let b := fmap N.D c x.2
      (VE.SoftNorms.Wire.cohLabel x.1 x.2,
        if a.name < b.name then VE.SoftNorms.Wire.cohLabel a b else VE.SoftNorms.Wire.cohLabel b a))

/-- What an answer shows for the superposed labels `used`: choice labels of the compatible choices taking `A`. -/
def sdShown (N : NDoc) (A : Choice) (used : List String) : List String :=
  VE.SoftNorms.dedup (((checkedChoices N.D).filter (fun c => A.all (c.contains ·))).flatMap (fun c =>
    (labelImage N c).filterMap (fun p => if used.contains p.2 then some p.1 else none)))

/-! ## The labels of a soft document, read from its nodes -/

/-- An exception label: `soft:exception:<name>:<kind>:<i>`, as `PacksLabels` reads it. -/
def excData (n : String) (k : List Char) (i : Nat) : List Char :=
  "soft:exception:".data ++ (n.data ++ ':' :: (k ++ ':' :: Nat.toDigits 10 i))

theorem nodeExcLabels_length (M M' : SoftNode) (hm : M'.mode = M.mode)
    (he : M'.exception.map (fun e => (e.sufficient.length, e.necessary.length)) =
      M.exception.map (fun e => (e.sufficient.length, e.necessary.length))) :
    (nodeExcLabels M').length = (nodeExcLabels M).length := by
  unfold nodeExcLabels
  rw [hm]
  cases M.mode <;> cases h1 : M.exception <;> cases h2 : M'.exception <;> simp_all

theorem zip_map_same {α β γ : Type} (f : α → β) (g : α → γ) :
    ∀ l : List α, (l.map f).zip (l.map g) = l.map (fun x => (f x, g x))
  | [] => rfl
  | x :: l => by simp [zip_map_same f g l]

/-- The pairs of two nodes' exception labels with one shape: one kind and one index, two names. -/
theorem mem_zip_nodeExcLabels {M M' : SoftNode} (hm : M'.mode = M.mode)
    (he : M'.exception.map (fun e => (e.sufficient.length, e.necessary.length)) =
      M.exception.map (fun e => (e.sufficient.length, e.necessary.length)))
    {p : String × String} (hp : p ∈ (nodeExcLabels M).zip (nodeExcLabels M')) :
    ∃ k i, (k = "sufficient".data ∨ k = "necessary".data) ∧ p.1.data = excData M.name k i ∧
      p.2.data = excData M'.name k i := by
  unfold nodeExcLabels at hp
  rw [hm] at hp
  cases hmd : M.mode <;> rw [hmd] at hp
  · simp at hp
  cases h1 : M.exception <;> cases h2 : M'.exception <;> rw [h1, h2] at he <;> simp only [h1, h2] at hp
  · simp at hp
  · simp at he
  · simp at he
  rename_i e e'
  simp only [Option.map_some, Option.some.injEq, Prod.mk.injEq] at he
  rw [he.1, he.2, List.zip_append (by simp), zip_map_same, zip_map_same] at hp
  rcases List.mem_append.mp hp with hp | hp <;> obtain ⟨i, _, rfl⟩ := List.mem_map.mp hp
  · exact ⟨_, i, Or.inl rfl, VE.NormDefaults.Packs.pk_exc_suff _ i, VE.NormDefaults.Packs.pk_exc_suff _ i⟩
  · exact ⟨_, i, Or.inr rfl, VE.NormDefaults.Packs.pk_exc_nec _ i, VE.NormDefaults.Packs.pk_exc_nec _ i⟩

theorem excLabels_nodes (Y : SoftDoc) : VE.SoftNorms.Wire.excLabels Y = Y.T.nodes.flatMap nodeExcLabels := rfl

theorem softXL_labels (N : NDoc) (X : RightsDoc) :
    (softXL N X).map (·.1) = (correlate X).T.nodes.flatMap nodeExcLabels ++
      (VE.SoftNorms.collidingPairs (correlate X)).map (fun x => VE.SoftNorms.Wire.cohLabel x.1 x.2) := by
  simp only [softXL, VE.NormDefaults.Wire.softLabelledU, List.map_append]
  congr 1
  · exact List.map_fst_zip (Nat.le_of_eq (excLabels_length _))
  · rw [List.map_map]; rfl

/-- The colliding pairs of a document's own nodes are colliding pairs of its correlated document. -/
theorem collidingPairs_correlate {X : RightsDoc} {x : SoftNode × SoftNode}
    (hx : x ∈ VE.SoftNorms.collidingPairs X.soft) : x ∈ VE.SoftNorms.collidingPairs (correlate X) := by
  obtain ⟨h1, h2, h3, h4, h5, h6⟩ := VE.SoftNorms.mem_collidingPairs.mp hx
  have hd : VE.SoftNorms.dualPerm (correlate X) = VE.SoftNorms.dualPerm X.soft := rfl
  refine VE.SoftNorms.mem_collidingPairs.mpr ⟨?_, ?_, h3, h4, h5, by simpa [VE.SoftNorms.Incompatible, hd] using h6⟩ <;>
    simp only [correlate, List.mem_append] <;> simp [h1, h2]

/-! ## The image of a choice's rule -/

section Image
variable {N : NDoc} (hh : Hyps N.D) (c : Choice)
include hh

theorem fmap_exception_shape {M : SoftNode} (hM : M ∈ (choiceDoc N.D c).1.soft.T.nodes) :
    (fmap N.D c M).exception.map (fun e => (e.sufficient.length, e.necessary.length)) =
      M.exception.map (fun e => (e.sufficient.length, e.necessary.length)) := by
  rcases (mem_choiceNodes N.D c M).mp hM with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hcc⟩
  · rw [fmap_frame hh c hf]
  · rw [fmap_fixed hh c hu]; rfl
  · rw [fmap_chosen hh c hm hi ha hcc]; cases h : M.exception <;> simp [gateNorm, h]

theorem nodeExcLabels_fmap_length {M : SoftNode} (hM : M ∈ (choiceDoc N.D c).1.soft.T.nodes) :
    (nodeExcLabels (fmap N.D c M)).length = (nodeExcLabels M).length :=
  nodeExcLabels_length _ _ (fmap_fields hh c hM).2.2.1 (fmap_exception_shape hh c hM)

/-- The images of a colliding pair of `c`'s document, ascending, are a colliding pair of the superposed one. -/
theorem image_pair_mem {x : SoftNode × SoftNode} (hx : x ∈ VE.SoftNorms.collidingPairs (choiceDoc N.D c).1.soft) :
    (if (fmap N.D c x.1).name < (fmap N.D c x.2).name then (fmap N.D c x.1, fmap N.D c x.2)
      else (fmap N.D c x.2, fmap N.D c x.1)) ∈ VE.SoftNorms.collidingPairs (sup N.D).1.soft := by
  obtain ⟨hM, hM', hMd, hM'd, hlt, hi⟩ := VE.SoftNorms.mem_collidingPairs.mp hx
  have hinc : ∀ P Q : SoftNode, VE.SoftNorms.Incompatible (sup N.D).1.soft P Q =
      VE.SoftNorms.Incompatible (choiceDoc N.D c).1.soft P Q := fun P Q => by
    simp only [VE.SoftNorms.Incompatible, dualPerm_eq c]
  have f1 := fmap_fields hh c hM
  have f2 := fmap_fields hh c hM'
  have hd1 : (fmap N.D c x.1).mode = .default := f1.2.2.1.trans hMd
  have hd2 : (fmap N.D c x.2).mode = .default := f2.2.2.1.trans hM'd
  have hI : VE.SoftNorms.Incompatible (sup N.D).1.soft (fmap N.D c x.1) (fmap N.D c x.2) = true := by
    rw [hinc]; simpa [VE.SoftNorms.Incompatible, f1.1, f1.2.1, f2.1, f2.2.1] using hi
  have hne : (fmap N.D c x.1).name ≠ (fmap N.D c x.2).name := fun h => by
    have := fmap_inj hh c hM hM' (sup_name_inj hh (fmap_mem hh c hM) (fmap_mem hh c hM') h)
    rw [this] at hlt; exact String.lt_irrefl _ hlt
  split
  · exact VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hM, fmap_mem hh c hM', hd1, hd2, by assumption, hI⟩
  · rename_i hn
    rcases VE.SoftNorms.str_lt_or_gt _ _ hne with h | h
    · exact absurd h hn
    · exact VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hM', fmap_mem hh c hM, hd2, hd1, h,
        by rw [VE.SoftNorms.incompatible_symm]; exact hI⟩

end Image

/-- Where a pair of `labelImage` comes from: an exception label of a rule of `c`'s document with its image's, or a
    colliding pair with its images ascending. -/
theorem mem_labelImage {N : NDoc} {c : Choice} {p : String × String} (hp : p ∈ labelImage N c) :
    (∃ M ∈ (choiceDoc N.D c).1.soft.T.nodes, p ∈ (nodeExcLabels M).zip (nodeExcLabels (fmap N.D c M))) ∨
      ∃ x ∈ VE.SoftNorms.collidingPairs (choiceDoc N.D c).1.soft, p.1 = VE.SoftNorms.Wire.cohLabel x.1 x.2 ∧
        p.2 = (let y := if (fmap N.D c x.1).name < (fmap N.D c x.2).name then (fmap N.D c x.1, fmap N.D c x.2)
          else (fmap N.D c x.2, fmap N.D c x.1); VE.SoftNorms.Wire.cohLabel y.1 y.2) := by
  rcases List.mem_append.mp hp with h | h
  · exact Or.inl (List.mem_flatMap.mp h)
  · obtain ⟨x, hx, rfl⟩ := List.mem_map.mp h
    exact Or.inr ⟨x, hx, rfl, by simp only; split <;> rfl⟩

theorem labelImage_fst (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c) :
    (labelImage N c).map (·.1) = (softXL N (choiceDoc N.D c).1).map (·.1) := by
  have hh := hyps_sd hN hs
  rw [softXL_labels, choice_correlate hh]
  simp only [labelImage, List.map_append, List.map_flatMap, List.map_map]
  congr 1
  exact VE.NormDefaults.flatMap_congr_mem (fun M hM => List.map_fst_zip (Nat.le_of_eq (nodeExcLabels_fmap_length hh c hM).symm))

theorem labelImage_snd_mem (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (p : String × String) (hp : p ∈ labelImage N c) :
    p.2 ∈ (softXL N (sup N.D).1).map (·.1) := by
  have hh := hyps_sd hN hs
  rw [softXL_labels, sup_correlate hh]
  rcases mem_labelImage hp with ⟨M, hM, hz⟩ | ⟨x, hx, -, h2⟩
  · exact List.mem_append_left _ (List.mem_flatMap.mpr ⟨_, fmap_mem hh c hM, (List.of_mem_zip hz).2⟩)
  · exact List.mem_append_right _ (List.mem_map.mpr ⟨_, image_pair_mem hh c hx, h2.symm⟩)

/-! ## The shown labels -/

theorem sdShown_mem (N : NDoc) (hr : supReady N.D = true) (hle : (checkedChoices N.D).length ≤ maxChoiceChecks)
    (A : Choice) (used : List String) (l : String) (hl : l ∈ sdShown N A used) :
    ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ l ∈ (softXL N (choiceDoc N.D c).1).map (·.1) := by
  simp only [sdShown, VE.SoftNorms.mem_dedup, List.mem_flatMap, List.mem_filter, List.mem_filterMap,
    List.all_eq_true, List.contains_iff_mem] at hl
  obtain ⟨c, ⟨hc, hA⟩, p, hp, hpl⟩ := hl
  refine ⟨c, compatible_of_mem_search N.D _ c hc, hA, ?_⟩
  split at hpl
  · cases hpl
    rw [softXL_labels]
    rcases mem_labelImage hp with ⟨M, hM, hz⟩ | ⟨x, hx, h1, -⟩
    · refine List.mem_append_left _ (List.mem_flatMap.mpr ⟨M, ?_, (List.of_mem_zip hz).1⟩)
      simp only [correlate, List.mem_append]; exact Or.inl (Or.inr hM)
    · exact List.mem_append_right _ (List.mem_map.mpr ⟨x, collidingPairs_correlate hx, h1.symm⟩)
  · cases hpl

theorem sdShown_image (N : NDoc) (hr : supReady N.D = true) (hle : (checkedChoices N.D).length ≤ maxChoiceChecks)
    (A : Choice) (used : List String) (c : Choice) (hc : Compatible N.D c) (hA : ∀ x ∈ A, x ∈ c)
    (l s : String) (hp : (l, s) ∈ labelImage N c) (hu : s ∈ used) :
    l ∈ sdShown N A used := by
  have hlt : (search N.D N.D.sets [] (maxChoiceChecks + 1)).length < maxChoiceChecks + 1 := by
    have := hle; simp only [checkedChoices] at this; omega
  simp only [sdShown, VE.SoftNorms.mem_dedup, List.mem_flatMap, List.mem_filter, List.mem_filterMap,
    List.all_eq_true, List.contains_iff_mem]
  exact ⟨c, ⟨(search_spec N.D hr _ hlt c).mpr hc, hA⟩, (l, s), hp, by simp [hu]⟩

theorem fillLabels_choice (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c) :
    VE.NormDefaults.Admission.fillLabels (choiceU N c) = VE.NormDefaults.Admission.fillLabels (supU N) := by
  have hh := hyps_sd hN hs
  unfold VE.NormDefaults.Admission.fillLabels
  rw [choiceU_D hh, supU_D hh]
  simp only [VE.SoftNorms.soften, regs_eq c]
  rfl

end VE.Readings
